import logging
from typing import Optional

import typer
from pydantic import PositiveInt

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.core.commons.service import (
    get_access_token_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
    validate_kubernetes_name,
)
from exls.workspaces.cli import poll_workspace_creation, workspaces_deploy_app
from exls.workspaces.common.display import TableWorkspacesDisplayManager
from exls.workspaces.common.dtos import WorkspaceDTO, WorkspaceResourcesRequestDTO
from exls.workspaces.types.llminference.dtos import (
    DeployLLMInferenceWorkspaceRequestDTO,
)
from exls.workspaces.types.llminference.service import (
    LLMInferenceWorkspacesService,
    get_llm_inference_workspaces_service,
)

logger: logging.Logger = logging.getLogger("cli.workspaces.llm-inference")


def get_llm_inference_workspaces_service_from_ctx(
    ctx: typer.Context,
) -> LLMInferenceWorkspacesService:
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)
    return get_llm_inference_workspaces_service(
        config=config, access_token=access_token
    )


@workspaces_deploy_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage LLM inference workspaces.
    """
    help_if_no_subcommand(ctx)


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
        callback=validate_kubernetes_name,
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
    huggingface_token: Optional[str] = typer.Option(
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
    display_manager: TableWorkspacesDisplayManager = TableWorkspacesDisplayManager()

    service: LLMInferenceWorkspacesService = (
        get_llm_inference_workspaces_service_from_ctx(ctx)
    )

    resources = WorkspaceResourcesRequestDTO(
        gpu_count=gpu_count,
        gpu_type=None,
        gpu_vendor=None,
        cpu_cores=cpu_cores,
        memory_gb=memory_gb_per_actor,
        pvc_storage_gb=1,  # llm inference workspaces do not support PVC storage, this will be ignored
        ephemeral_storage_gb=ephemeral_storage_gb_per_actor,
    )

    deploy_llm_inference_workspace_request = DeployLLMInferenceWorkspaceRequestDTO(
        cluster_id=cluster_id,
        name=name,
        resources=resources,
        docker_image=docker_image,
        huggingface_model=huggingface_model,
        huggingface_token=huggingface_token,
        num_model_replicas=num_model_replicas,
        tensor_parallel_size=tensor_parallel_size,
        pipeline_parallel_size=pipeline_parallel_size,
        pip_dependencies=pip_dependencies,
        gpu_per_actor=gpu_per_actor,
        cpu_per_actor=cpu_per_actor,
        memory_gb_per_actor=memory_gb_per_actor,
        ephemeral_storage_gb_per_actor=ephemeral_storage_gb_per_actor,
        to_be_deleted_at=None,
    )

    try:
        workspace_id: str = service.deploy_llm_inference_workspace(
            request_dto=deploy_llm_inference_workspace_request,
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    workspace: WorkspaceDTO = poll_workspace_creation(
        display_manager=display_manager,
        service=service,
        workspace_id=workspace_id,
    )

    display_manager.display_success(
        f"workspace {workspace.workspace_name} ({workspace.workspace_id}) created successfully."
    )
    display_manager.display_workspace(workspace)
