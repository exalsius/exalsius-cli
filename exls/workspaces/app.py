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
from exls.shared.adapters.ui.utils import (
    called_with_any_user_input,
    help_if_no_subcommand,
)
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
from exls.workspaces.adapters.ui.flows.workspace_deploy import (
    DeployDevPodFlowDTO,
    DeployDistributedTrainingFlowDTO,
    DeployJupyterFlowDTO,
    DeployMarimoFlowDTO,
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
    service: WorkspacesService = bundle.get_workspaces_service()

    # Select workspace type
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

    # Run the appropriate flow and execute deployment
    if workspace_type == "jupyter":
        flow_dto = DeployJupyterFlowDTO()
        bundle.get_deploy_jupyter_flow().execute(flow_dto, FlowContext(), io_facade)
        _execute_jupyter_deployment(bundle, io_facade, service, flow_dto)

    elif workspace_type == "marimo":
        flow_dto = DeployMarimoFlowDTO()
        bundle.get_deploy_marimo_flow().execute(flow_dto, FlowContext(), io_facade)
        _execute_marimo_deployment(bundle, io_facade, service, flow_dto)

    elif workspace_type == "dev-pod":
        flow_dto = DeployDevPodFlowDTO()
        bundle.get_deploy_dev_pod_flow().execute(flow_dto, FlowContext(), io_facade)
        _execute_dev_pod_deployment(bundle, io_facade, service, flow_dto)

    elif workspace_type == "distributed-training":
        flow_dto = DeployDistributedTrainingFlowDTO()
        bundle.get_deploy_distributed_training_flow().execute(
            flow_dto, FlowContext(), io_facade
        )
        _execute_distributed_training_deployment(bundle, io_facade, service, flow_dto)


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


# -----------------------------------------------------------------------------
# Deployment Execution Helpers (shared by interactive callback and subcommands)
# -----------------------------------------------------------------------------


def _execute_jupyter_deployment(
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
    service: WorkspacesService,
    flow_dto: DeployJupyterFlowDTO,
) -> None:
    """Execute Jupyter workspace deployment with collected inputs."""
    assert flow_dto.cluster is not None
    cluster_id = flow_dto.cluster.id
    num_gpus = int(flow_dto.num_gpus)

    resources = _get_resources_for_single_node_worker(service, cluster_id, num_gpus)
    template = _get_workspace_template(service, IntegratedWorkspaceTemplates.JUPYTER)

    configurator = JupyterConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.JUPYTER
        ),
        password=flow_dto.password,
    )
    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster_id,
        workspace_name=flow_dto.name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
        description=f"Workspace with {num_gpus} GPUs",
    )

    _deploy_and_display_result(
        bundle, io_facade, service, request, flow_dto.wait_for_ready
    )


def _execute_marimo_deployment(
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
    service: WorkspacesService,
    flow_dto: DeployMarimoFlowDTO,
) -> None:
    """Execute Marimo workspace deployment with collected inputs."""
    assert flow_dto.cluster is not None
    cluster_id = flow_dto.cluster.id
    num_gpus = int(flow_dto.num_gpus)

    resources = _get_resources_for_single_node_worker(service, cluster_id, num_gpus)
    template = _get_workspace_template(service, IntegratedWorkspaceTemplates.MARIMO)

    configurator = MarimoConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.MARIMO
        ),
        password=flow_dto.password,
    )
    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster_id,
        workspace_name=flow_dto.name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
        description=f"Marimo workspace with {num_gpus} GPUs",
    )

    _deploy_and_display_result(
        bundle, io_facade, service, request, flow_dto.wait_for_ready
    )


def _execute_dev_pod_deployment(
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
    service: WorkspacesService,
    flow_dto: DeployDevPodFlowDTO,
) -> None:
    """Execute DevPod workspace deployment with collected inputs."""
    assert flow_dto.cluster is not None
    cluster_id = flow_dto.cluster.id
    num_gpus = int(flow_dto.num_gpus)

    resources = _get_resources_for_single_node_worker(service, cluster_id, num_gpus)
    template = _get_workspace_template(service, IntegratedWorkspaceTemplates.DEV_POD)

    configurator = DevPodConfigurator(
        editor_render_bundle=bundle.get_editor_render_bundle(
            IntegratedWorkspaceTemplates.DEV_POD
        ),
        ssh_password=flow_dto.access.ssh_password,
        ssh_public_key=flow_dto.access.ssh_public_key,
    )
    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster_id,
        workspace_name=flow_dto.name,
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
        description=f"Dev pod workspace with {num_gpus} GPUs",
    )

    _deploy_and_display_result(
        bundle, io_facade, service, request, flow_dto.wait_for_ready
    )


def _execute_distributed_training_deployment(
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
    service: WorkspacesService,
    flow_dto: DeployDistributedTrainingFlowDTO,
) -> None:
    """Execute Distributed Training workspace deployment with collected inputs."""
    assert flow_dto.cluster is not None
    assert flow_dto.model is not None
    assert flow_dto.gradient_compression is not None
    cluster_id = flow_dto.cluster.id

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
        model=flow_dto.model,
        gradient_compression=flow_dto.gradient_compression,
        wandb_token=flow_dto.wandb_token,
        hf_token=flow_dto.hf_token,
        worker_groups=resources,
    )
    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster_id,
        workspace_name=f"dist-train-{flow_dto.model.value}-compression-{flow_dto.gradient_compression.value}",
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
        description=f"Distributed training of {flow_dto.model.value} with gradient compression {flow_dto.gradient_compression.value} on {sum([wg.num_workers for wg in resources])} nodes",
    )

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


def _deploy_and_display_result(
    bundle: WorkspacesBundle,
    io_facade: IOBaseModelFacade,
    service: WorkspacesService,
    request: DeployWorkspaceRequest,
    wait_for_ready: bool,
) -> None:
    """Execute deployment and display results."""
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


# -----------------------------------------------------------------------------
# Subcommands
# -----------------------------------------------------------------------------


@workspaces_deploy_app.command("jupyter", help="Deploy a Jupyter workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_jupyter_workspace(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        help="The name or ID of the cluster to deploy the workspace to",
        show_default=False,
        default=None,
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="The name of the workspace to deploy",
        show_default=False,
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="The password to use for the Jupyter workspace. Must be at least 6 characters long.",
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

    # If no CLI args provided, use interactive flow
    if not called_with_any_user_input(ctx):
        flow_dto = DeployJupyterFlowDTO()
        bundle.get_deploy_jupyter_flow().execute(flow_dto, FlowContext(), io_facade)
        _execute_jupyter_deployment(bundle, io_facade, service, flow_dto)
        return

    # CLI args provided - validate and use them
    if password is None or len(password) < 6:
        raise ValueError("Password must be provided and be at least 6 characters long")

    # Resolve cluster
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

    workspace_name = name if name else generate_random_name(prefix="jupyter")
    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=workspace_name,
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

    _deploy_and_display_result(bundle, io_facade, service, request, wait_for_ready)


@workspaces_deploy_app.command("marimo", help="Deploy a Marimo workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_marimo_workspace(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        help="The name or ID of the cluster to deploy the workspace to",
        show_default=False,
        default=None,
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="The name of the workspace to deploy",
        show_default=False,
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="The password to use for the Marimo workspace (optional, min. 6 characters if set).",
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

    # If no CLI args provided, use interactive flow
    if not called_with_any_user_input(ctx):
        flow_dto = DeployMarimoFlowDTO()
        bundle.get_deploy_marimo_flow().execute(flow_dto, FlowContext(), io_facade)
        _execute_marimo_deployment(bundle, io_facade, service, flow_dto)
        return

    # CLI args provided - validate and use them
    # Resolve cluster
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
        password=password or "",
    )
    try:
        template_variables: Dict[str, Any] = configurator.configure_and_validate(
            template.variables, io_facade
        )
    except InvalidWorkspaceConfiguration as e:
        io_facade.display_error_message(str(e), bundle.message_output_format)
        raise typer.Exit(1)

    workspace_name = name if name else generate_random_name(prefix="marimo")
    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=workspace_name,
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

    _deploy_and_display_result(bundle, io_facade, service, request, wait_for_ready)


@workspaces_deploy_app.command("dev-pod", help="Deploy a dev pod workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_dev_pod_workspace(
    ctx: typer.Context,
    cluster_name_or_id: Optional[str] = typer.Argument(
        None,
        help="The name or ID of the cluster to deploy the workspace to",
        show_default=False,
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="The name of the workspace to deploy",
        show_default=False,
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

    # If no CLI args provided, use interactive flow
    if not called_with_any_user_input(ctx):
        flow_dto = DeployDevPodFlowDTO()
        bundle.get_deploy_dev_pod_flow().execute(flow_dto, FlowContext(), io_facade)
        _execute_dev_pod_deployment(bundle, io_facade, service, flow_dto)
        return

    # CLI args provided - validate and use them
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

    workspace_name = name if name else generate_random_name(prefix="dev-pod")
    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=workspace_name,
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

    _deploy_and_display_result(bundle, io_facade, service, request, wait_for_ready)


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
    model: Optional[DistributedTrainingModels] = typer.Option(
        None,
        "--model",
        "-m",
        help="The model to deploy the workspace with",
        show_default=False,
    ),
    gradient_compression: Optional[GradientCompression] = typer.Option(
        None,
        "--gradient-compression",
        "-g",
        help="Compress the gradients during training to reduce the communication overhead.",
        show_default=False,
    ),
    wandb_token: Optional[str] = typer.Option(
        None,
        "--wandb-token",
        "-w",
        help="The API token to use for Weights and Biases",
        show_default=False,
    ),
    hf_token: Optional[str] = typer.Option(
        None,
        "--hf-token",
        "-t",
        help="The API token to use for Hugging Face",
        show_default=False,
    ),
):
    """
    Deploy a distributed training workspace.
    """
    bundle = WorkspacesBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    # If no CLI args provided, use interactive flow
    if not called_with_any_user_input(ctx):
        flow_dto = DeployDistributedTrainingFlowDTO()
        bundle.get_deploy_distributed_training_flow().execute(
            flow_dto, FlowContext(), io_facade
        )
        _execute_distributed_training_deployment(bundle, io_facade, service, flow_dto)
        return

    # CLI args provided - validate and use them
    if not wandb_token or len(wandb_token) == 0:
        raise ValueError("Weights & Biases API token must be provided")
    if not hf_token or len(hf_token) == 0:
        raise ValueError("Hugging Face API token must be provided")

    # Use defaults if not provided
    effective_model = model if model else DistributedTrainingModels.GPT_NEO_X
    effective_compression = (
        gradient_compression
        if gradient_compression
        else GradientCompression.MEDIUM_COMPRESSION
    )

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
        model=effective_model,
        gradient_compression=effective_compression,
        wandb_token=wandb_token,
        hf_token=hf_token,
        worker_groups=resources,
    )

    template_variables: Dict[str, Any] = configurator.configure_and_validate(
        template.variables, io_facade
    )

    request = DeployWorkspaceRequest(
        cluster_id=cluster.id,
        workspace_name=f"dist-train-{effective_model.value}-compression-{effective_compression.value}",
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
        description=f"Distributed training of {effective_model.value} with gradient compression {effective_compression.value} on {sum([wg.num_workers for wg in resources])} nodes",
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
