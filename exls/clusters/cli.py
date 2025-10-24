from pathlib import Path
from typing import List, Optional

import typer

from exls.clusters.display import TableClusterDisplayManager
from exls.clusters.dtos import (
    AddNodesRequestDTO,
    AllowedClusterNodeRoleDTO,
    AllowedClusterStatusDTO,
    AllowedClusterTypesDTO,
    AllowedGpuTypesDTO,
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    CreateClusterRequestDTO,
    ListClustersRequestDTO,
    RemoveNodeRequestDTO,
)
from exls.clusters.service import ClustersService, get_clusters_service
from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.core.commons.service import (
    get_access_token_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
)

clusters_app = typer.Typer()


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


@clusters_app.command("create", help="Create a cluster")
def create_cluster(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="The name of the cluster"),
    cluster_type: AllowedClusterTypesDTO = typer.Option(
        AllowedClusterTypesDTO.REMOTE,
        "--cluster-type",
        help="The type of the cluster",
    ),
    gpu_type: AllowedGpuTypesDTO = typer.Option(
        AllowedGpuTypesDTO.NVIDIA.value,
        "--gpu-type",
        help="The type of the GPU to add to the cluster",
        show_choices=True,
        case_sensitive=False,
    ),
    diloco: bool = typer.Option(
        False,
        "--diloco",
        help="Add the volcano workload type to the cluster to support Diloco workloads",
    ),
    telemetry_enabled: bool = typer.Option(
        False,
        "--telemetry-enabled",
        help="Enable telemetry for the cluster",
    ),
):
    """
    Create a cluster.
    """
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        cluster: ClusterDTO = service.create_cluster(
            CreateClusterRequestDTO(
                name=name,
                cluster_type=cluster_type,
                gpu_type=gpu_type,
                diloco=diloco,
                telemetry_enabled=telemetry_enabled,
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Cluster {cluster.id} created successfully.")


@clusters_app.command("deploy", help="Deploy a cluster")
def deploy_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(..., help="The ID of the cluster to deploy"),
):
    """
    Deploy a cluster.
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
        "Are you sure you want to deploy this cluster?"
    ):
        raise typer.Exit()

    try:
        service.deploy_cluster(cluster_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(
        f"Cluster {cluster_id} deployment started successfully."
    )

    display_manager.display_info(
        f"You can check the status with `exls clusters get {cluster_id}`"
    )


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


def _node_role_callback(value: str) -> str:
    if value not in ("WORKER", "CONTROL_PLANE"):
        raise typer.BadParameter("node_role must be 'WORKER' or 'CONTROL_PLANE'")
    return value


@clusters_app.command("add-nodes", help="Add nodes to a cluster")
def add_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to add a node to"
    ),
    node_ids: List[str] = typer.Argument(
        help="The IDs of the nodes to add to the cluster"
    ),
    node_role: AllowedClusterNodeRoleDTO = typer.Option(
        AllowedClusterNodeRoleDTO.WORKER,
        "--node-role",
        help="The role of the nodes to add to the cluster. Can be `WORKER` or `CONTROL_PLANE`, defaults to `WORKER`",
        case_sensitive=True,
        show_choices=True,
        rich_help_panel="Node Role",
        prompt=False,
        callback=_node_role_callback,
    ),
):
    """
    Add nodes to a cluster.
    """
    display_manager = TableClusterDisplayManager()
    service: ClustersService = _get_clusters_service(ctx)

    try:
        nodes: List[ClusterNodeDTO] = service.add_cluster_nodes(
            AddNodesRequestDTO(
                cluster_id=cluster_id, node_ids=node_ids, node_role=node_role
            )
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(
        f"Nodes {node_ids} added to cluster {cluster_id} successfully."
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
