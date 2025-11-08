from pathlib import Path
from typing import Any, List, Optional, Set

import typer
from pydantic import StrictStr

from exls.clusters.display import (
    ComposingClusterDisplayManager,
    TableClusterDisplayManager,
)
from exls.clusters.dtos import (
    AddNodesRequestDTO,
    AllowedClusterNodeRoleDTO,
    AllowedClusterStatusDTO,
    AllowedClusterTypesDTO,
    AllowedGpuTypesDTO,
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    DeployClusterRequestDTO,
    ListClustersRequestDTO,
    RemoveNodeRequestDTO,
)
from exls.clusters.interactive.flow import (
    ClusterFlowInterruptionException,
    ClusterInteractiveFlow,
)
from exls.clusters.service import ClustersService, get_clusters_service
from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.exceptions import ExalsiusError
from exls.core.base.service import ServiceError
from exls.core.commons.service import (
    generate_random_name,
    get_access_token_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
    validate_kubernetes_name,
)
from exls.nodes.dtos import AllowedNodeStatusFiltersDTO, NodeDTO, NodesListRequestDTO
from exls.nodes.service import NodeService, get_node_service

clusters_app = typer.Typer()


def _called_with_any_user_input(ctx: typer.Context) -> bool:
    """
    Return True if the command was invoked with ANY non-default option/argument.
    """
    for param in ctx.command.params:
        name: Optional[StrictStr] = param.name
        if name is None:
            continue
        actual_value: Optional[Any] = ctx.params.get(name, None)
        if actual_value is None:
            continue

        return True

    return False


def _get_clusters_service(ctx: typer.Context) -> ClustersService:
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)
    return get_clusters_service(config, access_token)


@clusters_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage clusters.
    """
    help_if_no_subcommand(ctx)


@clusters_app.command("list", help="List all clusters")
def list_clusters(
    ctx: typer.Context,
    status: Optional[AllowedClusterStatusDTO] = typer.Option(
        None,
        "--status",
        help="Filter clusters by status",
    ),
):
    """
    List all clusters.
    """
    display_manager = TableClusterDisplayManager()
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)
    service: ClustersService = get_clusters_service(config, access_token)

    try:
        clusters: List[ClusterDTO] = service.list_clusters(
            ListClustersRequestDTO(status=status)
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_clusters(clusters)


@clusters_app.command("get", help="Get a cluster")
def get_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(..., help="The ID of the cluster to get"),
):
    """
    Get a cluster.
    """
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        cluster: ClusterDTO = service.get_cluster(cluster_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_cluster(cluster)


@clusters_app.command("delete", help="Delete a cluster")
def delete_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(..., help="The ID of the cluster to delete"),
):
    """
    Delete a cluster.
    """
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        cluster: ClusterDTO = service.get_cluster(cluster_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_cluster(cluster)

    if not display_manager.display_confirmation(
        "Are you sure you want to delete this cluster?"
    ):
        raise typer.Exit()

    try:
        service.delete_cluster(cluster_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Cluster {cluster_id} deleted successfully.")


def _validate_node_ids(
    available_nodes: List[NodeDTO],
    node_ids: List[StrictStr],
) -> Optional[ErrorDisplayModel]:
    valid_node_ids: Set[StrictStr] = {node.id for node in available_nodes}
    invalid_node_ids: List[StrictStr] = [
        node_id for node_id in node_ids if node_id not in valid_node_ids
    ]
    if invalid_node_ids:
        return ErrorDisplayModel(
            message=f"Invalid node ID(s) found: {', '.join(invalid_node_ids)}."
        )
    return None


@clusters_app.command("deploy", help="Create a cluster")
def deploy_cluster(
    ctx: typer.Context,
    name: str = typer.Option(
        generate_random_name(prefix="exls-cluster"),
        "--name",
        "-n",
        help="The name of the cluster. If not provided, a random name will be generated.",
        show_default=False,
        callback=validate_kubernetes_name,
    ),
    worker_node_ids: List[str] = typer.Option(
        [],
        "--worker-nodes",
        help="The IDs of the worker nodes to add to the cluster.",
        show_default=False,
    ),
    gpu_type: AllowedGpuTypesDTO = typer.Option(
        AllowedGpuTypesDTO.NVIDIA.value,
        "--gpu-type",
        help="The type of the GPU to add to the cluster",
        show_choices=True,
        case_sensitive=False,
    ),
    enable_multinode_training: bool = typer.Option(
        False,
        "--enable-multinode-training",
        help="Enable multinode AI model training for the cluster",
    ),
    enable_telemetry: bool = typer.Option(
        False,
        "--enable-telemetry",
        help="Enable telemetry for the cluster",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help="Enable interactive mode to create the cluster",
    ),
):
    """
    Create a cluster.
    """
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)

    node_service: NodeService = get_node_service(config, access_token)
    cluster_service: ClustersService = get_clusters_service(config, access_token)

    display_manager = TableClusterDisplayManager()

    try:
        nodes_list_request: NodesListRequestDTO = NodesListRequestDTO(
            status=AllowedNodeStatusFiltersDTO.AVAILABLE,
        )
        available_nodes: List[NodeDTO] = node_service.list_nodes(
            request=nodes_list_request
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    if len(available_nodes) == 0:
        display_manager.display_error(
            ErrorDisplayModel(
                message="No available nodes for cluster deployment found. Please import nodes first."
            )
        )
        raise typer.Exit()

    deploy_request: Optional[DeployClusterRequestDTO] = None
    if interactive or _called_with_any_user_input(ctx):
        display: ComposingClusterDisplayManager = ComposingClusterDisplayManager(
            display_manager=display_manager
        )

        interactive_flow: ClusterInteractiveFlow = ClusterInteractiveFlow(
            available_nodes, display
        )
        try:
            deploy_request = interactive_flow.run()
        except ClusterFlowInterruptionException as e:
            display_manager.display_info(str(e))
            raise typer.Exit(0)
        except ExalsiusError as e:
            display_manager.display_error(ErrorDisplayModel(message=str(e)))
            raise typer.Exit(1)
    else:
        # Validate worker node IDs
        validation_error: Optional[ErrorDisplayModel] = _validate_node_ids(
            available_nodes=available_nodes,
            node_ids=worker_node_ids,
        )
        if validation_error:
            display_manager.display_error(error=validation_error)
            raise typer.Exit()

        deploy_request = DeployClusterRequestDTO(
            name=name,
            cluster_type=AllowedClusterTypesDTO.REMOTE,
            gpu_type=gpu_type,
            worker_node_ids=worker_node_ids,
            control_plane_node_ids=[],
            enable_multinode_training=enable_multinode_training,
            enable_telemetry=enable_telemetry,
        )

    try:
        cluster: ClusterDTO = cluster_service.deploy_cluster(deploy_request)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Cluster {cluster.id} created successfully.")


@clusters_app.command("list-nodes", help="List all nodes of a cluster")
def list_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to list nodes of"
    ),
):
    """
    List all nodes of a cluster.
    """
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        nodes: List[ClusterNodeDTO] = service.get_cluster_nodes(cluster_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_cluster_nodes(nodes)


@clusters_app.command("add-nodes", help="Add nodes to a cluster")
def add_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to add a node to"
    ),
    worker_node_ids: List[StrictStr] = typer.Option(
        [],
        "--worker-nodes",
        help="The IDs of the worker nodes to add to the cluster.",
        show_default=False,
    ),
):
    """
    Add nodes to a cluster.
    """
    display_manager = TableClusterDisplayManager()
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)
    node_service: NodeService = get_node_service(config, access_token)
    service: ClustersService = get_clusters_service(config, access_token)

    try:
        available_nodes: List[NodeDTO] = node_service.list_nodes(None)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    validation_error: Optional[ErrorDisplayModel] = _validate_node_ids(
        available_nodes=available_nodes,
        node_ids=worker_node_ids,
    )
    if validation_error:
        display_manager.display_error(error=validation_error)
        raise typer.Exit()

    try:
        nodes: List[ClusterNodeDTO] = service.add_cluster_nodes(
            AddNodesRequestDTO(
                cluster_id=cluster_id,
                node_ids=worker_node_ids,
                node_role=AllowedClusterNodeRoleDTO.WORKER,
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(
        f" {len(worker_node_ids)} worker nodes added to cluster {cluster_id} successfully."
    )
    display_manager.display_cluster_nodes(nodes)


@clusters_app.command("remove-node", help="Remove a node from a cluster")
def remove_node(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to remove a node from"
    ),
    node_id: str = typer.Argument(
        ..., help="The ID of the node to remove from the cluster"
    ),
):
    """
    Remove a node from a cluster.
    """
    # TODO: Validate node IDs; check if node is part of the cluster
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        removed_node_id: str = service.remove_cluster_node(
            RemoveNodeRequestDTO(cluster_id=cluster_id, node_id=node_id)
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(
        f"Node {removed_node_id} removed from cluster {cluster_id} successfully."
    )


@clusters_app.command("show-available-resources", help="Get the resources of a cluster")
def get_cluster_resources(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ...,
        help="The ID of the cluster to get resources of",
    ),
):
    """
    Get the resources of a cluster.
    """
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        available_cluster_resources: List[ClusterNodeResourcesDTO] = (
            service.get_cluster_resources(cluster_id)
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_cluster_resources(available_cluster_resources)


@clusters_app.command(
    "import-kubeconfig", help="Import a kubeconfig file into a cluster"
)
def import_kubeconfig(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to import the kubeconfig to"
    ),
    kubeconfig_path: str = typer.Option(
        Path.home().joinpath(".kube", "config").as_posix(),
        "--kubeconfig-path",
        help="The path to the kubeconfig file to import",
    ),
):
    """
    Import a kubeconfig file into a cluster.
    """
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        service.import_kubeconfig(cluster_id, kubeconfig_path)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(
        f"Kubeconfig from cluster {cluster_id} successfully imported to {kubeconfig_path}."
    )
