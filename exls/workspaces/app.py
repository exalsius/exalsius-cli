import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.flows.keys import PublicKeySpecDTO
from exls.shared.adapters.ui.input.values import UserCancellationException
from exls.shared.adapters.ui.utils import help_if_no_subcommand
from exls.shared.core.crypto import CryptoService
from exls.shared.core.domain import generate_random_name
from exls.workspaces.adapters.bundle import WorkspacesBundle
from exls.workspaces.adapters.dtos import (
    MultiNodeWorkspaceDTO,
    SingleNodeWorkspaceDTO,
    WorkspaceDTO,
)
from exls.workspaces.adapters.ui.configurators import (
    DistributedTrainingConfigurator,
    DistributedTrainingModels,
    GradientCompression,
    InvalidWorkspaceConfiguration,
    JupyterConfigurator,
    MarimoConfigurator,
    VSCodeDevPodConfigurator,
)
from exls.workspaces.adapters.ui.display.display import IOWorkspacesFacade
from exls.workspaces.adapters.ui.dtos import IntegratedWorkspaceTemplates
from exls.workspaces.adapters.ui.mapper import (
    deploy_multi_node_workspace_request_dto_from_domain,
    deploy_single_node_workspace_request_dto_from_domain,
    multi_node_workspace_dto_from_domain,
    single_node_workspace_dto_from_domain,
    workspace_dto_from_domain,
)
from exls.workspaces.core.domain import (
    Workspace,
    WorkspaceCluster,
    WorkspaceTemplate,
)
from exls.workspaces.core.requests import (
    AssignedMultiNodeWorkspaceResources,
    AssignedSingleNodeWorkspaceResources,
    DeployWorkspaceRequest,
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
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to list the workspaces for"
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    cluster: WorkspaceCluster = service.get_cluster(cluster_id)

    workspaces: List[Workspace] = service.list_workspaces(cluster_id=cluster_id)
    workspace_dtos: List[WorkspaceDTO] = [
        workspace_dto_from_domain(workspace, cluster.name) for workspace in workspaces
    ]

    io_facade.display_data(workspace_dtos, bundle.object_output_format)


@workspaces_app.command("get", help="Get a workspace of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def get_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to get",
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    workspace: Workspace = service.get_workspace(workspace_id)
    cluster: WorkspaceCluster = service.get_cluster(workspace.cluster_id)

    workspace_dto: WorkspaceDTO = workspace_dto_from_domain(workspace, cluster.name)

    io_facade.display_data(workspace_dto, bundle.object_output_format)


@workspaces_app.command("delete", help="Delete a workspace of a cluster")
@handle_application_layer_errors(WorkspacesBundle)
def delete_workspace(
    ctx: typer.Context,
    workspace_id: str = typer.Argument(
        help="The ID of the workspace to delete",
    ),
):
    bundle = WorkspacesBundle(ctx)
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service = bundle.get_workspaces_service()

    service.delete_workspace(workspace_id=workspace_id)

    io_facade.display_success_message(
        f"Workspace {workspace_id} deleted successfully.", bundle.message_output_format
    )


@workspaces_app.command("deploy", help="Deploy a workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_workspace(
    ctx: typer.Context,
):
    """
    Deploy a workspace.
    """
    # TODO: Implement generic workspace deployment
    pass


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
    if len(x) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return x


def _validate_api_token_non_empty(x: str) -> str:
    if len(x) == 0:
        raise ValueError("API token must be non-empty")
    return x


def _validate_num_gpus(x: int) -> int:
    if x < 1:
        raise ValueError("Number of GPUs must be at least 1")
    return x


@workspaces_deploy_app.command("jupyter", help="Deploy a Jupyter workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_jupyter_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the workspace to"
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
        help="The password to use for the Jupyter workspace",
        callback=_validate_optional_password,
        prompt=True,
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
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    cluster: WorkspaceCluster = service.get_cluster(cluster_id)

    resources: AssignedSingleNodeWorkspaceResources = (
        service.get_resources_for_single_node_workspace(
            cluster_id=cluster_id, num_gpus=num_gpus
        )
    )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.JUPYTER
    )
    configurator: JupyterConfigurator = JupyterConfigurator(bundle, password)
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
        deploy_single_node_workspace_request_dto_from_domain(
            domain=request, cluster_name=cluster.name
        ),
        bundle.object_output_format,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace = service.deploy_workspace(
        request=request, wait_for_ready=wait_for_ready
    )
    workspace_dto: SingleNodeWorkspaceDTO = single_node_workspace_dto_from_domain(
        workspace, cluster.name
    )

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(workspace_dto, bundle.object_output_format)


@workspaces_deploy_app.command("marimo", help="Deploy a Marimo workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_marimo_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the workspace to"
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
        help="The password to use for the Marimo workspace",
        callback=_validate_optional_password,
        prompt=True,
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
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    cluster: WorkspaceCluster = service.get_cluster(cluster_id)

    resources: AssignedSingleNodeWorkspaceResources = (
        service.get_resources_for_single_node_workspace(
            cluster_id=cluster_id, num_gpus=num_gpus
        )
    )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.MARIMO
    )
    configurator: MarimoConfigurator = MarimoConfigurator(bundle, password)
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
        deploy_single_node_workspace_request_dto_from_domain(
            domain=request, cluster_name=cluster.name
        ),
        bundle.object_output_format,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace = service.deploy_workspace(
        request=request, wait_for_ready=wait_for_ready
    )
    workspace_dto: SingleNodeWorkspaceDTO = single_node_workspace_dto_from_domain(
        workspace, cluster.name
    )

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(workspace_dto, bundle.object_output_format)


@workspaces_deploy_app.command("dev-pod", help="Deploy a VSCode dev pod workspace")
@handle_application_layer_errors(WorkspacesBundle)
def deploy_vscode_dev_pod_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the workspace to"
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
        prompt=False,
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
    Deploy a VSCode dev pod workspace.
    """
    bundle = WorkspacesBundle(ctx)
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    cluster: WorkspaceCluster = service.get_cluster(cluster_id)

    resources: AssignedSingleNodeWorkspaceResources = (
        service.get_resources_for_single_node_workspace(
            cluster_id=cluster_id, num_gpus=num_gpus
        )
    )

    if not ssh_password and not ssh_public_key:
        io_facade.display_error_message(
            "No SSH password or public key provided. Please provide at least one of them.",
            bundle.message_output_format,
        )
        raise typer.Exit(1)

    ssh_public_key_str: Optional[str] = None
    crypto_service: CryptoService = bundle.get_crypto_service()
    if ssh_public_key:
        ssh_public_key_str = crypto_service.resolve_public_key(
            PublicKeySpecDTO(path=ssh_public_key)
        )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.VSCODE_DEV_POD
    )
    configurator: VSCodeDevPodConfigurator = VSCodeDevPodConfigurator(
        bundle, ssh_password, ssh_public_key_str
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
        description=f"VSCode dev pod workspace with {num_gpus} GPUs",
    )

    io_facade.display_data(
        deploy_single_node_workspace_request_dto_from_domain(
            domain=request, cluster_name=cluster.name
        ),
        bundle.object_output_format,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace = service.deploy_workspace(
        request=request, wait_for_ready=wait_for_ready
    )
    workspace_dto: SingleNodeWorkspaceDTO = single_node_workspace_dto_from_domain(
        workspace, cluster.name
    )

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(workspace_dto, bundle.object_output_format)


@workspaces_deploy_app.command(
    "distributed-training", help="Deploy a distributed training workspace"
)
@handle_application_layer_errors(WorkspacesBundle)
def deploy_distributed_training_workspace(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        help="The ID of the cluster to deploy the workspace to"
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
    io_facade: IOWorkspacesFacade = bundle.get_io_facade()
    service: WorkspacesService = bundle.get_workspaces_service()

    cluster: WorkspaceCluster = service.get_cluster(cluster_id)

    resources: AssignedMultiNodeWorkspaceResources = (
        service.get_resources_for_multi_node_workspace(cluster_id=cluster_id)
    )

    template: WorkspaceTemplate = _get_workspace_template(
        service, IntegratedWorkspaceTemplates.DIST_TRAINING
    )
    configurator: DistributedTrainingConfigurator = DistributedTrainingConfigurator(
        bundle,
        model,
        gradient_compression,
        wandb_token,
        hf_token,
        resources.total_nodes,
        resources.heterogenous,
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
        workspace_name=f"dist-train-{model.value}-compression-{gradient_compression.value}",
        template_id=template.id_name,
        template_variables=template_variables,
        resources=resources,
        description=f"Distributed training of {model.value} with gradient compression {gradient_compression.value} on 1 nodes",
    )

    io_facade.display_data(
        deploy_multi_node_workspace_request_dto_from_domain(
            domain=request,
            cluster_name=cluster.name,
            total_nodes=resources.total_nodes,
            gpu_types=resources.gpu_vendor or "",
        ),
        bundle.object_output_format,
    )
    if not io_facade.ask_confirm(
        message="Do you want to deploy the workspace?",
        default=False,
    ):
        raise UserCancellationException("User cancelled the workspace deployment")

    workspace: Workspace = service.deploy_workspace(
        request=request, wait_for_ready=False
    )
    workspace_dto: MultiNodeWorkspaceDTO = multi_node_workspace_dto_from_domain(
        domain=workspace,
        total_nodes=resources.total_nodes,
        gpu_types=resources.gpu_vendor or "",
        cluster_name=cluster.name,
    )

    io_facade.display_success_message(
        f"Workspace {workspace.name} deployed successfully.",
        bundle.message_output_format,
    )
    io_facade.display_data(workspace_dto, bundle.object_output_format)
