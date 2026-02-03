import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from pydantic import BaseModel, Field

from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.facade.facade import IOBaseModelFacade
from exls.shared.adapters.ui.flow.flow import FlowContext, SequentialFlow
from exls.shared.adapters.ui.flow.steps import ChoicesSpec, SelectRequiredStep
from exls.shared.adapters.ui.flows.keys import PublicKeySpecDTO
from exls.shared.adapters.ui.input.values import (
    DisplayChoice,
    UserCancellationException,
)
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.crypto import CryptoService
from exls.shared.core.resolver import resolve_resource_id
from exls.shared.core.utils import generate_random_name
from exls.workspaces.adapters.bundle import WorkspacesBundle
from exls.workspaces.adapters.ui.configurators import (
    DevPodConfigurator,
    DistributedTrainingConfigurator,
    DistributedTrainingModels,
    GradientCompression,
    IntegratedWorkspaceTemplates,
    InvalidWorkspaceConfiguration,
    JupyterConfigurator,
    MarimoConfigurator,
)
from exls.workspaces.adapters.ui.display.render import (
    DEPLOY_WORKSPACE_REQUEST_VIEW,
    WORKSPACE_DETAIL_VIEW,
    WORKSPACE_LIST_VIEW,
)
from exls.workspaces.core.domain import (
    GPUVendorPreference,
    WorkerGroupResources,
    WorkerResources,
    Workspace,
    WorkspaceCluster,
    WorkspaceTemplate,
)
from exls.workspaces.core.requests import (
    DeployWorkspaceRequest,
    SingleNodeWorkerResourcesRequest,
)
from exls.workspaces.core.service import WorkspacesService

logger = logging.getLogger("cli.workspaces")

workspaces_app = typer.Typer()
workspaces_deploy_app = typer.Typer()

workspaces_app.add_typer(workspaces_deploy_app, name="deploy")


@workspaces_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage workspaces.
    """
    help_if_no_subcommand(ctx)


@workspaces_app.command("list", help="List all workspaces of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def list_workspaces(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        help="The name or ID of the cluster to list the workspaces for",
        show_default=False,
        default=None,
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    resolved_cluster_id: Optional[str] = None
    if cluster_name_or_id:
        clusters: List[WorkspaceCluster] = service.list_clusters()
        resolved_cluster_id = resolve_resource_id(
            clusters, cluster_name_or_id, "cluster"
        )

    workspaces: List[Workspace] = service.list_workspaces(
        cluster_id=resolved_cluster_id
    )

    if len(workspaces) == 0:
        io_facade.display_info_message(
            "No workspaces found. Run 'exls workspaces deploy <workspace-type>' to deploy a workspace.",
            bundle.message_output_format,
        )
    else:
        io_facade.display_data(
            data=workspaces,
            output_format=bundle.object_output_format,
            view_context=WORKSPACE_LIST_VIEW,
        )


@workspaces_app.command("get", help="Get a workspace of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def get_workspace(
    ctx: typer.Context,
    workspace_name_or_id: str = typer.Argument(
        help="The name or ID of the workspace to get",
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    workspaces: List[Workspace] = service.list_workspaces()
    workspace_id: str = resolve_resource_id(
        workspaces, workspace_name_or_id, "workspace"
    )
    workspace: Workspace = service.get_workspace(workspace_id)

    io_facade.display_data(
        data=workspace,
        output_format=bundle.object_output_format,
        view_context=WORKSPACE_DETAIL_VIEW,
    )


@workspaces_app.command("delete", help="Delete workspace of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def delete_workspace(
    ctx: typer.Context,
    workspace_name_or_id: str = typer.Argument(
        ...,
        help="The name or ID of the workspace to delete",
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    workspaces: List[Workspace] = service.list_workspaces()
    workspace_id: str = resolve_resource_id(
        workspaces, workspace_name_or_id, "workspace"
    )
    workspace: Workspace = service.get_workspace(workspace_id)

    service.delete_workspaces(workspace_ids=[workspace_id])

    io_facade.display_success_message(
        f"Workspace '{workspace.name}' deleted successfully.",
        bundle.message_output_format,
    )


class WorkspaceTypeChoice(BaseModel):
    """DTO for workspace type selection in interactive flow."""

    workspace_type: Optional[str] = Field(
        default=None, description="The selected workspace type"
    )


def _get_workspace_type_choices() -> ChoicesSpec[str]:
    """Get the available workspace types as choices."""
    return ChoicesSpec[str](
        choices=[
            DisplayChoice[str](title="Jupyter Notebook", value="jupyter"),
            DisplayChoice[str](title="Marimo Notebook", value="marimo"),
            DisplayChoice[str](title="VS Code Dev Container", value="dev-pod"),
            DisplayChoice[str](
                title="Distributed Training", value="distributed-training"
            ),
        ]
    )


@workspaces_deploy_app.callback(invoke_without_command=True)
@handle_application_layer_errors(WorkspacesBundle)
def deploy_workspace_interactive(
    ctx: typer.Context,
):
    """
    Deploy a workspace interactively.

    When called without a subcommand, this will guide you through
    selecting a workspace type and configuring it for deployment.

    You can also use subcommands directly:
      exls workspaces deploy jupyter
      exls workspaces deploy marimo
      exls workspaces deploy dev-pod
      exls workspaces deploy distributed-training
    """
    # If a subcommand was invoked, let it handle the request
    if ctx.invoked_subcommand is not None:
        return

    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()

    io_facade.display_info_message(
        "Deploying a new workspace - Interactive Mode",
        bundle.message_output_format,
    )

    # Step 1: Select workspace type
    workspace_type_dto = WorkspaceTypeChoice()
    type_selection_flow: SequentialFlow[WorkspaceTypeChoice] = SequentialFlow[
        WorkspaceTypeChoice
    ](
        steps=[
            SelectRequiredStep[WorkspaceTypeChoice, str](
                key="workspace_type",
                message="Select workspace type:",
                choices_spec=_get_workspace_type_choices(),
            )
        ]
    )
    type_selection_flow.execute(workspace_type_dto, FlowContext(), io_facade)

    workspace_type = workspace_type_dto.workspace_type

    # Step 2: Dispatch to the appropriate deployment flow based on type
    if workspace_type == "jupyter":
        _deploy_jupyter_interactive(ctx, bundle, io_facade)
    elif workspace_type == "marimo":
        _deploy_marimo_interactive(ctx, bundle, io_facade)
    elif workspace_type == "dev-pod":
        _deploy_dev_pod_interactive(ctx, bundle, io_facade)
    elif workspace_type == "distributed-training":
        _deploy_distributed_training_interactive(ctx, bundle, io_facade)


def _deploy_jupyter_interactive(
    ctx: typer.Context,
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
) -> None:
    """Interactive deployment flow for Jupyter workspace."""
    service: WorkspacesService = bundle.get_workspaces_service()

    # Get cluster
    cluster_id = _get_cluster_id(service, io_facade)
    if not cluster_id:
        io_facade.display_error_message(
            "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
            bundle.message_output_format,
        )
        raise typer.Exit(0)

    # Get workspace name
    name = io_facade.ask_text(
        message="Workspace name:",
        default=generate_random_name(prefix="jupyter"),
    )

    # Get password
    password = io_facade.ask_password(
        message="Jupyter password (min. 6 characters):",
        validator=lambda x: (
            True if len(x) >= 6 else "Password must be at least 6 characters"
        ),
    )

    # Get number of GPUs
    num_gpus_str = io_facade.ask_text(
        message="Number of GPUs:",
        default="1",
        validator=lambda x: (
            True if x.isdigit() and int(x) >= 1 else "Must be a positive integer"
        ),
    )
    num_gpus = int(num_gpus_str)

    # Get wait for ready
    wait_for_ready = io_facade.ask_confirm(
        message="Wait for workspace to be ready?",
        default=False,
    )

    # Get resources and template
    resources = _get_resources_for_single_node_worker(service, cluster_id, num_gpus)
    template = _get_workspace_template(service, IntegratedWorkspaceTemplates.JUPYTER)

    configurator = JupyterConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.JUPYTER
        ),
        password=password,
    )
    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster_id,
        workspace_name=name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Deploy this workspace?",
        default=True,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace
    if wait_for_ready:
        with io_facade.spinner("Deploying workspace and waiting for it to be ready..."):
            workspace = service.deploy_workspace(request=request, wait_for_ready=True)
    else:
        workspace = service.deploy_workspace(request=request, wait_for_ready=False)

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )


def _deploy_marimo_interactive(
    ctx: typer.Context,
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
) -> None:
    """Interactive deployment flow for Marimo workspace."""
    service: WorkspacesService = bundle.get_workspaces_service()

    # Get cluster
    cluster_id = _get_cluster_id(service, io_facade)
    if not cluster_id:
        io_facade.display_error_message(
            "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
            bundle.message_output_format,
        )
        raise typer.Exit(0)

    # Get workspace name
    name = io_facade.ask_text(
        message="Workspace name:",
        default=generate_random_name(prefix="marimo"),
    )

    # Get password (optional for Marimo)
    password = io_facade.ask_text(
        message="Marimo password (optional, min. 6 characters if set):",
        default="",
        validator=lambda x: (
            True
            if x == "" or len(x) >= 6
            else "Password must be at least 6 characters if provided"
        ),
    )

    # Get number of GPUs
    num_gpus_str = io_facade.ask_text(
        message="Number of GPUs:",
        default="1",
        validator=lambda x: (
            True if x.isdigit() and int(x) >= 1 else "Must be a positive integer"
        ),
    )
    num_gpus = int(num_gpus_str)

    # Get wait for ready
    wait_for_ready = io_facade.ask_confirm(
        message="Wait for workspace to be ready?",
        default=False,
    )

    # Get resources and template
    resources = _get_resources_for_single_node_worker(service, cluster_id, num_gpus)
    template = _get_workspace_template(service, IntegratedWorkspaceTemplates.MARIMO)

    configurator = MarimoConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.MARIMO
        ),
        password=password,
    )
    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster_id,
        workspace_name=name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Deploy this workspace?",
        default=True,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace
    if wait_for_ready:
        with io_facade.spinner("Deploying workspace and waiting for it to be ready..."):
            workspace = service.deploy_workspace(request=request, wait_for_ready=True)
    else:
        workspace = service.deploy_workspace(request=request, wait_for_ready=False)

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )


def _deploy_dev_pod_interactive(
    ctx: typer.Context,
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
) -> None:
    """Interactive deployment flow for DevPod workspace."""
    from exls.workspaces.adapters.ui.flows.access_flow import AccessDTO

    service: WorkspacesService = bundle.get_workspaces_service()

    # Get cluster
    cluster_id = _get_cluster_id(service, io_facade)
    if not cluster_id:
        io_facade.display_error_message(
            "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
            bundle.message_output_format,
        )
        raise typer.Exit(0)

    # Get workspace name
    name = io_facade.ask_text(
        message="Workspace name:",
        default=generate_random_name(prefix="dev-pod"),
    )

    # Get number of GPUs
    num_gpus_str = io_facade.ask_text(
        message="Number of GPUs:",
        default="1",
        validator=lambda x: (
            True if x.isdigit() and int(x) >= 1 else "Must be a positive integer"
        ),
    )
    num_gpus = int(num_gpus_str)

    # Get SSH access configuration using existing flow
    access_dto = AccessDTO()
    access_flow = bundle.get_configure_workspace_access_flow()
    access_flow.execute(access_dto, FlowContext(), io_facade)

    # Validate access configuration
    if not access_dto.ssh_password and not access_dto.ssh_public_key:
        raise ValueError("SSH password or public key is required")
    if access_dto.ssh_password and len(access_dto.ssh_password) < 6:
        raise ValueError("SSH password must be at least 6 characters")

    # Get wait for ready
    wait_for_ready = io_facade.ask_confirm(
        message="Wait for workspace to be ready?",
        default=False,
    )

    # Get resources and template
    resources = _get_resources_for_single_node_worker(service, cluster_id, num_gpus)
    template = _get_workspace_template(service, IntegratedWorkspaceTemplates.DEV_POD)

    configurator = DevPodConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.DEV_POD
        ),
        ssh_password=access_dto.ssh_password,
        ssh_public_key=access_dto.ssh_public_key,
    )
    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster_id,
        workspace_name=name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Deploy this workspace?",
        default=True,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace
    if wait_for_ready:
        with io_facade.spinner("Deploying workspace and waiting for it to be ready..."):
            workspace = service.deploy_workspace(request=request, wait_for_ready=True)
    else:
        workspace = service.deploy_workspace(request=request, wait_for_ready=False)

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )

    # Format access information for DevPod
    for access_info in workspace.access_information:
        access_info_str = access_info.formatted_access_information
        if access_info.access_protocol.lower() == "ssh":
            access_info_str = access_info_str.replace("dev@", "dev@")
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )


def _deploy_distributed_training_interactive(
    ctx: typer.Context,
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
) -> None:
    """Interactive deployment flow for Distributed Training workspace."""
    service: WorkspacesService = bundle.get_workspaces_service()

    # Get cluster
    cluster_id = _get_cluster_id(service, io_facade)
    if not cluster_id:
        io_facade.display_error_message(
            "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
            bundle.message_output_format,
        )
        raise typer.Exit(0)

    cluster: WorkspaceCluster = service.get_cluster(cluster_id)

    # Select model
    model_choices = ChoicesSpec[DistributedTrainingModels](
        choices=[
            DisplayChoice[DistributedTrainingModels](title=model.value, value=model)
            for model in DistributedTrainingModels
        ],
        default=DisplayChoice[DistributedTrainingModels](
            title=DistributedTrainingModels.GPT_NEO_X.value,
            value=DistributedTrainingModels.GPT_NEO_X,
        ),
    )

    class ModelSelectionDTO(BaseModel):
        model: Optional[DistributedTrainingModels] = None

    model_dto = ModelSelectionDTO()
    model_flow: SequentialFlow[ModelSelectionDTO] = SequentialFlow[ModelSelectionDTO](
        steps=[
            SelectRequiredStep[ModelSelectionDTO, DistributedTrainingModels](
                key="model",
                message="Select model to train:",
                choices_spec=model_choices,
            )
        ]
    )
    model_flow.execute(model_dto, FlowContext(), io_facade)
    assert model_dto.model is not None  # SelectRequiredStep ensures this
    model: DistributedTrainingModels = model_dto.model

    # Select gradient compression
    compression_choices = ChoicesSpec[GradientCompression](
        choices=[
            DisplayChoice[GradientCompression](
                title=compression.value, value=compression
            )
            for compression in GradientCompression
        ],
        default=DisplayChoice[GradientCompression](
            title=GradientCompression.MEDIUM_COMPRESSION.value,
            value=GradientCompression.MEDIUM_COMPRESSION,
        ),
    )

    class CompressionSelectionDTO(BaseModel):
        gradient_compression: Optional[GradientCompression] = None

    compression_dto = CompressionSelectionDTO()
    compression_flow: SequentialFlow[CompressionSelectionDTO] = SequentialFlow[
        CompressionSelectionDTO
    ](
        steps=[
            SelectRequiredStep[CompressionSelectionDTO, GradientCompression](
                key="gradient_compression",
                message="Select gradient compression level:",
                choices_spec=compression_choices,
            )
        ]
    )
    compression_flow.execute(compression_dto, FlowContext(), io_facade)
    assert (
        compression_dto.gradient_compression is not None
    )  # SelectRequiredStep ensures this
    gradient_compression: GradientCompression = compression_dto.gradient_compression

    # Get API tokens
    wandb_token = io_facade.ask_text(
        message="Weights & Biases API token:",
        validator=lambda x: True if len(x) > 0 else "Token cannot be empty",
    )

    hf_token = io_facade.ask_text(
        message="Hugging Face API token:",
        validator=lambda x: True if len(x) > 0 else "Token cannot be empty",
    )

    # Get resources for worker groups
    resources: List[WorkerGroupResources] = service.get_resources_for_worker_groups(
        cluster_id=cluster_id
    )

    template = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.DIST_TRAINING
    )
    configurator = DistributedTrainingConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.DIST_TRAINING
        ),
        model=model,
        gradient_compression=gradient_compression,
        wandb_token=wandb_token,
        hf_token=hf_token,
        worker_groups=resources,
    )

    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=f"dist-train-{model.value}-compression-{gradient_compression.value}",
        template_id=template.id_name,
        template_variables=template_variables,
        resources=WorkerResources(
            gpu_count=1,
            gpu_type=None,
            gpu_vendor=None,
            cpu_cores=min([wg.worker_resources.cpu_cores for wg in resources]),
            memory_gb=min([wg.worker_resources.memory_gb for wg in resources]),
            storage_gb=min([wg.worker_resources.storage_gb for wg in resources]),
        ),
        description=f"Distributed training of {model.value} with gradient compression {gradient_compression.value} on {sum([wg.num_workers for wg in resources])} nodes",
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Deploy this workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace = service.deploy_workspace(
        request=request, wait_for_ready=False
    )

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )


def _get_workspace_template(
    service: WorkspacesService, template_id: IntegratedWorkspaceTemplates
) -> WorkspaceTemplate:
    templates: List[WorkspaceTemplate] = service.get_workspace_templates()
    for template in templates:
        if template.id_name == template_id:
            return template
    raise ValueError(f"Workspace template {template_id} not found")


def _validate_optional_password(x: Optional[str]) -> Optional[str]:
    if x is None:
        return x
    if len(x) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return x


def _validate_api_token_non_empty(x: str) -> str:
    if len(x) == 0:
        raise ValueError("API token must be non-empty")
    return x


def _validate_num_gpus(x: int) -> int:
    if x < 1:
        raise ValueError("Number of GPUs must be at least 1")
    return x


# TODO: Move this to a better place
def _get_cluster_id(
    service: WorkspacesService, io_facade: IOBaseModelFacade
) -> Optional[str]:
    clusters: List[WorkspaceCluster] = service.list_clusters()
    if len(clusters) == 0:
        return None
    if len(clusters) == 1:
        return clusters[0].id
    if len(clusters) > 1:

        class ClusterSelectionDTO(BaseModel):
            cluster_id: Optional[str] = Field(
                default=None, description="The ID of the cluster"
            )

        flow: SequentialFlow[ClusterSelectionDTO] = SequentialFlow[ClusterSelectionDTO](
            steps=[
                SelectRequiredStep[ClusterSelectionDTO, str](
                    key="cluster_id",
                    message="Select a cluster:",
                    choices_spec=ChoicesSpec[str](
                        choices=[
                            DisplayChoice[str](title=cluster.name, value=cluster.id)
                            for cluster in clusters
                        ]
                    ),
                )
            ]
        )
        cluster_selection_dto: ClusterSelectionDTO = ClusterSelectionDTO()
        flow.execute(cluster_selection_dto, FlowContext(), io_facade)
        return cluster_selection_dto.cluster_id


def _get_resources_for_single_node_worker(
    service: WorkspacesService,
    cluster_id: str,
    num_gpus: int,
) -> WorkerResources:
    resources_request: SingleNodeWorkerResourcesRequest = (
        SingleNodeWorkerResourcesRequest(
            cluster_id=cluster_id,
            gpu_vendor_preference=GPUVendorPreference.AUTO,
            resource_split_tolerance=0.1,
            num_gpus=num_gpus,
        )
    )
    resources: WorkerResources = service.get_resources_for_single_node_worker(
        request=resources_request
    )
    return resources


@workspaces_deploy_app.command("jupyter", help="Deploy a Jupyter workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_jupyter_workspace(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        help="The name or ID of the cluster to deploy the workspace to",
        show_default=False,
        default=None,
    ),
    name: str = typer.Option(
        generate_random_name(prefix="jupyter"),
        "--name",
        "-n",
        help="The name of the workspace to deploy",
    ),
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="The password to use for the Jupyter workspace. Must be at least 6 characters long.",
        prompt="You need a password to access your Jupyter workspace. Please enter the password (min. 6 characters)",
        show_default=False,
    ),
    num_gpus: int = typer.Option(
        1,
        "--num-gpus",
        "-g",
        help="The number of GPUs to deploy the workspace with",
        callback=_validate_num_gpus,
    ),
    wait_for_ready: bool = typer.Option(
        False, "--wait-for-ready", "-w", help="Wait for the workspace to be ready"
    ),
):
    """
    Deploy a Jupyter workspace.
    """
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")

    valid_cluster_id: str
    if not cluster_name_or_id:
        loaded_cluster_id: Optional[str] = _get_cluster_id(service, io_facade)
        if not loaded_cluster_id:
            io_facade.display_error_message(
                "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
                bundle.message_output_format,
            )
            raise typer.Exit(0)
        valid_cluster_id = loaded_cluster_id
    else:
        clusters: List[WorkspaceCluster] = service.list_clusters()
        valid_cluster_id = resolve_resource_id(clusters, cluster_name_or_id, "cluster")

    cluster: WorkspaceCluster = service.get_cluster(valid_cluster_id)

    resources: WorkerResources = _get_resources_for_single_node_worker(
        service, cluster.id, num_gpus
    )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.JUPYTER
    )
    configurator: JupyterConfigurator = JupyterConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.JUPYTER
        ),
        password=password,
    )
    try:
        template_variables: Dict[str, Any] = configurator.configure_and_validate(
            template.variables, io_facade
        )
    except InvalidWorkspaceConfiguration as e:
        io_facade.display_error_message(str(e), bundle.message_output_format)
        raise typer.Exit(1)

    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
        description=f"Workspace with {num_gpus} GPUs",
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace
    if wait_for_ready:
        with io_facade.spinner("Deploying workspace and waiting for it to be ready..."):
            workspace = service.deploy_workspace(request=request, wait_for_ready=True)
    else:
        workspace = service.deploy_workspace(request=request, wait_for_ready=False)

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )


@workspaces_deploy_app.command("marimo", help="Deploy a Marimo workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_marimo_workspace(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        help="The name or ID of the cluster to deploy the workspace to",
        show_default=False,
        default=None,
    ),
    name: str = typer.Option(
        generate_random_name(prefix="marimo"),
        "--name",
        "-n",
        help="The name of the workspace to deploy",
    ),
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="The password to use for the Marimo workspace. Must be at least 6 characters long.",
        prompt="You need a password to access your Marimo workspace. Please enter the password (min. 6 characters)",
        callback=_validate_optional_password,
        show_default=False,
    ),
    num_gpus: int = typer.Option(
        1,
        "--num-gpus",
        "-g",
        help="The number of GPUs to deploy the workspace with",
        callback=_validate_num_gpus,
    ),
    wait_for_ready: bool = typer.Option(
        False, "--wait-for-ready", "-w", help="Wait for the workspace to be ready"
    ),
):
    """
    Deploy a Marimo workspace.
    """
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")

    valid_cluster_id: str
    if not cluster_name_or_id:
        loaded_cluster_id: Optional[str] = _get_cluster_id(service, io_facade)
        if not loaded_cluster_id:
            io_facade.display_error_message(
                "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
                bundle.message_output_format,
            )
            raise typer.Exit(0)
        valid_cluster_id = loaded_cluster_id
    else:
        clusters: List[WorkspaceCluster] = service.list_clusters()
        valid_cluster_id = resolve_resource_id(clusters, cluster_name_or_id, "cluster")

    cluster: WorkspaceCluster = service.get_cluster(valid_cluster_id)

    resources: WorkerResources = _get_resources_for_single_node_worker(
        service, cluster.id, num_gpus
    )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.MARIMO
    )
    configurator: MarimoConfigurator = MarimoConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.MARIMO
        ),
        password=password,
    )
    try:
        template_variables: Dict[str, Any] = configurator.configure_and_validate(
            template.variables, io_facade
        )
    except InvalidWorkspaceConfiguration as e:
        io_facade.display_error_message(str(e), bundle.message_output_format)
        raise typer.Exit(1)

    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
        description=f"Marimo workspace with {num_gpus} GPUs",
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace
    if wait_for_ready:
        with io_facade.spinner("Deploying workspace and waiting for it to be ready..."):
            workspace = service.deploy_workspace(request=request, wait_for_ready=True)
    else:
        workspace = service.deploy_workspace(request=request, wait_for_ready=False)

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )


@workspaces_deploy_app.command("dev-pod", help="Deploy a dev pod workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_dev_pod_workspace(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        None,
        help="The name or ID of the cluster to deploy the workspace to",
        show_default=False,
    ),
    name: str = typer.Option(
        generate_random_name(prefix="dev-pod"),
        "--name",
        "-n",
        help="The name of the workspace to deploy",
    ),
    num_gpus: int = typer.Option(
        1, "--num-gpus", "-g", help="The number of GPUs to deploy the workspace with"
    ),
    ssh_password: Optional[str] = typer.Option(
        None,
        "--ssh-password",
        "-p",
        help="The password to use for the SSH connection",
        callback=_validate_optional_password,
        show_default=False,
    ),
    ssh_public_key: Optional[Path] = typer.Option(
        None,
        "--ssh-public-key",
        "-k",
        help="Path to the public key file to use for the SSH connection",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    wait_for_ready: bool = typer.Option(
        False, "--wait-for-ready", "-w", help="Wait for the workspace to be ready"
    ),
):
    """
    Deploy a dev pod workspace.
    """
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    if not ssh_password and not ssh_public_key:
        raise ValueError(
            "No SSH password or public key provided. Please provide at least one of them."
        )

    if ssh_password and len(ssh_password) < 6:
        raise ValueError("SSH password must be at least 6 characters long")

    valid_cluster_id: str
    if not cluster_name_or_id:
        loaded_cluster_id: Optional[str] = _get_cluster_id(service, io_facade)
        if not loaded_cluster_id:
            io_facade.display_error_message(
                "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
                bundle.message_output_format,
            )
            raise typer.Exit(0)
        valid_cluster_id = loaded_cluster_id
    else:
        clusters: List[WorkspaceCluster] = service.list_clusters()
        valid_cluster_id = resolve_resource_id(clusters, cluster_name_or_id, "cluster")

    cluster: WorkspaceCluster = service.get_cluster(valid_cluster_id)

    resources: WorkerResources = _get_resources_for_single_node_worker(
        service, cluster.id, num_gpus
    )

    ssh_public_key_str: Optional[str] = None
    crypto_service: CryptoService = bundle.get_crypto_service()
    if ssh_public_key:
        ssh_public_key_str = crypto_service.resolve_public_key(
            PublicKeySpecDTO(path=ssh_public_key)
        )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.DEV_POD
    )
    configurator: DevPodConfigurator = DevPodConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.DEV_POD
        ),
        ssh_password=ssh_password,
        ssh_public_key=ssh_public_key_str,
    )
    try:
        template_variables: Dict[str, Any] = configurator.configure_and_validate(
            template.variables, io_facade
        )
    except InvalidWorkspaceConfiguration as e:
        io_facade.display_error_message(str(e), bundle.message_output_format)
        raise typer.Exit(1)

    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
        description=f"Dev pod workspace with {num_gpus} GPUs",
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace
    if wait_for_ready:
        with io_facade.spinner("Deploying workspace and waiting for it to be ready..."):
            workspace = service.deploy_workspace(request=request, wait_for_ready=True)
    else:
        workspace = service.deploy_workspace(request=request, wait_for_ready=False)

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )


@workspaces_deploy_app.command(
    "distributed-training", help="Deploy a distributed training workspace"
)
@handle_application_layer_errors(WorkspacesBundle)
def deploy_distributed_training_workspace(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        help="The name or ID of the cluster to deploy the workspace to",
        show_default=False,
        default=None,
    ),
    model: DistributedTrainingModels = typer.Option(
        DistributedTrainingModels.GPT_NEO_X,
        "--model",
        "-m",
        help="The model to deploy the workspace with",
    ),
    gradient_compression: GradientCompression = typer.Option(
        GradientCompression.MEDIUM_COMPRESSION,
        "--gradient-compression",
        "-g",
        help="We can compress the gradients during training to reduce the communication overhead.",
    ),
    wandb_token: str = typer.Option(
        None,
        "--wandb-token",
        "-w",
        help="The API token to use for Weights and Biases",
        callback=_validate_api_token_non_empty,
        prompt=True,
        show_default=False,
    ),
    hf_token: str = typer.Option(
        None,
        "--hf-token",
        "-t",
        help="The API token to use for Hugging Face",
        callback=_validate_api_token_non_empty,
        prompt=True,
        show_default=False,
    ),
):
    """
    Deploy a distributed training workspace.
    """
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    valid_cluster_id: str
    if not cluster_name_or_id:
        loaded_cluster_id: Optional[str] = _get_cluster_id(service, io_facade)
        if not loaded_cluster_id:
            io_facade.display_error_message(
                "No cluster found. Deploy a cluster first using 'exls clusters deploy'.",
                bundle.message_output_format,
            )
            raise typer.Exit(0)
        valid_cluster_id = loaded_cluster_id
    else:
        clusters: List[WorkspaceCluster] = service.list_clusters()
        valid_cluster_id = resolve_resource_id(clusters, cluster_name_or_id, "cluster")

    cluster: WorkspaceCluster = service.get_cluster(valid_cluster_id)

    resources: List[WorkerGroupResources] = service.get_resources_for_worker_groups(
        cluster_id=valid_cluster_id
    )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.DIST_TRAINING
    )
    configurator: DistributedTrainingConfigurator = DistributedTrainingConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.DIST_TRAINING
        ),
        model=model,
        gradient_compression=gradient_compression,
        wandb_token=wandb_token,
        hf_token=hf_token,
        worker_groups=resources,
    )

    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=f"dist-train-{model.value}-compression-{gradient_compression.value}",
        template_id=template.id_name,
        template_variables=template_variables,
        resources=WorkerResources(
            gpu_count=1,
            gpu_type=None,
            gpu_vendor=None,
            cpu_cores=min([wg.worker_resources.cpu_cores for wg in resources]),
            memory_gb=min([wg.worker_resources.memory_gb for wg in resources]),
            storage_gb=min([wg.worker_resources.storage_gb for wg in resources]),
        ),
        description=f"Distributed training of {model.value} with gradient compression {gradient_compression.value} on {sum([wg.num_workers for wg in resources])} nodes",
    )

    io_facade.display_data(
        request,
        bundle.object_output_format,
        view_context=DEPLOY_WORKSPACE_REQUEST_VIEW,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace = service.deploy_workspace(
        request=request, wait_for_ready=False
    )

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(
        workspace, bundle.object_output_format, view_context=WORKSPACE_LIST_VIEW
    )
