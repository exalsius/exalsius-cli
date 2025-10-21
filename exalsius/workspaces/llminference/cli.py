import logging
from typing import Optional

import typer
from pydantic import PositiveInt

from exalsius.config import AppConfig
from exalsius.core.base.display import ErrorDisplayModel
from exalsius.core.base.service import ServiceError
from exalsius.utils import commons as utils
from exalsius.workspaces.cli import poll_workspace_creation, workspaces_deploy_app
from exalsius.workspaces.display import TableWorkspacesDisplayManager
from exalsius.workspaces.dtos import (
    ResourcePoolDTO,
    WorkspaceDTO,
)
from exalsius.workspaces.llminference.service import LLMInferenceWorkspacesService

logger: logging.Logger = logging.getLogger("cli.workspaces.llm-inference")


def get_llm_inference_workspaces_service(
    ctx: typer.Context,
) -> LLMInferenceWorkspacesService:
    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)
    return LLMInferenceWorkspacesService(config, access_token)


@workspaces_deploy_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage LLM inference workspaces.
    """
    utils.help_if_no_subcommand(ctx)


@workspaces_deploy_app.command("llm-inference", help="Deploy a LLM inference workspace")
def deploy_llm_inference_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the service to"
    ),
    name: str = typer.Option(
        "exls-llminference",
        "--name",
        "-n",
        help="The name of the workspace to add. If not provided, a random name will be generated.",
        show_default=False,
        callback=utils.validate_kubernetes_name,
    ),
    docker_image: Optional[str] = typer.Option(
        None,
        "--docker-image",
        "-i",
        help="The docker image to use for the workspace",
        show_default=False,
    ),
    huggingface_model: str = typer.Option(
        "microsoft/phi-4",
        "--huggingface-model",
        "-m",
        help="The HuggingFace model to use",
    ),
    huggingface_token: str = typer.Option(
        ...,
        "--huggingface-token",
        "-t",
        envvar=["HUGGINGFACE_TOKEN", "HF_TOKEN"],
        help="The HuggingFace token to use",
    ),
    num_model_replicas: PositiveInt = typer.Option(
        1,
        "--num-model-replicas",
        "-r",
        help="The number of model replicas to use",
    ),
    tensor_parallel_size: PositiveInt = typer.Option(
        1,
        "--tensor-parallel-size",
        "-tp",
        help="The tensor parallel size to use",
    ),
    pipeline_parallel_size: PositiveInt = typer.Option(
        1,
        "--pipeline-parallel-size",
        "-pp",
        help="The pipeline parallel size to use",
    ),
    pip_dependencies: str = typer.Option(
        "numpy==1.26.4,vllm==0.9.0,ray==2.46.0",
        "--pip-dependencies",
        help="The pip dependencies to install in the runtime environment",
    ),
    gpu_count: PositiveInt = typer.Option(
        1,
        "--gpu-count",
        "-g",
        help="The number of GPUs to add to the workspace",
    ),
    gpu_per_actor: PositiveInt = typer.Option(
        1,
        "--gpu-per-actor",
        help="The number of GPUs to use per actor",
    ),
    cpu_cores: PositiveInt = typer.Option(
        16,
        "--cpu-cores",
        "-c",
        help="The number of CPU cores to add to the workspace",
    ),
    cpu_per_actor: PositiveInt = typer.Option(
        16,
        "--cpu-per-actor",
        help="The number of CPUs to use per actor",
    ),
    memory_gb_per_actor: PositiveInt = typer.Option(
        32,
        "--memory-gb",
        "-m",
        help="The amount of memory in GB to add to the workspace",
    ),
    ephemeral_storage_gb_per_actor: PositiveInt = typer.Option(
        100,
        "--ephemeral-storage-gb",
        "-e",
        help="The amount of ephemeral storage in GB to add to the workspace",
    ),
):
    # Check sanity of GPU parameters
    if gpu_count < num_model_replicas * gpu_per_actor:
        raise typer.BadParameter(
            "The total number of GPUs (`gpu-count`) must be greater than or equal to "
            "the number of model replicas (`num-model-replicas`) multiplied by "
            "the number of GPUs per replica (`gpu-per-actor`)."
        )
    if gpu_count > num_model_replicas * gpu_per_actor:
        logger.warning(
            "The total number of GPUs (`gpu-count`) is greater than the number of model replicas (`num-model-replicas`) "
            "multiplied by the number of GPUs per replica (`gpu-per-actor`). "
            "This means that some GPUs will be unused."
        )

    # Check sanity of CPU parameters
    if cpu_cores < num_model_replicas * cpu_per_actor:
        raise typer.BadParameter(
            "The total number of CPUs (`cpu-cores`) must be greater than or equal to "
            "the number of model replicas (`num-model-replicas`) multiplied by "
            "the number of CPUs per replica (`cpu-per-actor`)."
        )
    if cpu_cores > num_model_replicas * cpu_per_actor:
        logger.warning(
            "The total number of CPUs (`cpu-cores`) is greater than the number of model replicas (`num-model-replicas`) "
            "multiplied by the number of CPUs per replica (`cpu-per-actor`). "
            "This means that some CPUs will be unused."
        )

    # Check pipeline and tensor parallelism sanity
    if gpu_count < num_model_replicas * pipeline_parallel_size * tensor_parallel_size:
        raise typer.BadParameter(
            "The total number of GPUs (`gpu-count`) must be greater than or equal to "
            "the number of model replicas (`num-model-replicas`) multiplied by "
            "the number of pipeline parallel replicas (`pipeline-parallel-size`) multiplied by "
            "the number of tensor parallel replicas (`tensor-parallel-size`)."
        )

    display_manager: TableWorkspacesDisplayManager = TableWorkspacesDisplayManager()

    service: LLMInferenceWorkspacesService = get_llm_inference_workspaces_service(ctx)

    resources: ResourcePoolDTO = ResourcePoolDTO(
        gpu_count=gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb_per_actor,
        storage_gb=1,  # llm inference workspaces do not support PVC storage, this will be ignored
    )

    variables = {
        "deploymentName": name,
        "deploymentImage": docker_image,
        "huggingfaceModel": huggingface_model,
        "huggingfaceToken": huggingface_token,
        "numModelReplicas": num_model_replicas,
        "runtimeEnvironmentPipPackages": pip_dependencies,
        "tensorParallelSize": tensor_parallel_size,
        "pipelineParallelSize": pipeline_parallel_size,
        "cpuPerActor": cpu_per_actor,
        "gpuPerActor": gpu_per_actor,
        "ephemeralStorageGb": ephemeral_storage_gb_per_actor,
    }

    try:
        workspace_id: str = service.create_llm_inference_workspace(
            cluster_id=cluster_id,
            name=name,
            resources=resources,
            variables=variables,
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    workspace: WorkspaceDTO = poll_workspace_creation(
        display_manager=display_manager,
        service=service,
        workspace_id=workspace_id,
    )

    access_infos = workspace.access_information
    if not access_infos or len(access_infos) == 0:
        display_manager.display_success(
            f"workspace {workspace.name} ({workspace_id}) created successfully"
        )
        raise typer.Exit(0)

    for access_info in access_infos:
        access_info.workspace_id = workspace_id

    display_manager.display_success(
        f"workspace {workspace.name} ({workspace_id}) created successfully."
    )
    display_manager.display_info("Access information:")
    display_manager.display_workspace_access_info(access_infos)
