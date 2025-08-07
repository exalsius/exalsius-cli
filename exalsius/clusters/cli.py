from typing import List, Optional

import typer
from rich.console import Console

from exalsius.clusters.display import ClustersDisplayManager
from exalsius.clusters.models import ClusterType, NodesToAddDTO
from exalsius.clusters.service import ClustersService
from exalsius.config import AppConfig, ConfigDefaultCluster, save_config
from exalsius.core.commons.models import ServiceError
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    Manage clusters.
    """
    utils.help_if_no_subcommand(ctx)


@app.command("list", help="List all clusters")
def list_clusters(
    ctx: typer.Context,
    status: Optional[str] = typer.Option(
        None,
        "--status",
        help="Filter clusters by status",
    ),
):
    """
    List all clusters.
    """
    console: Console = Console(theme=custom_theme)
    display_manager: ClustersDisplayManager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)

    service: ClustersService = ClustersService(config, access_token)

    try:
        clusters = service.list_clusters(status)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_clusters(clusters)


@app.command("get", help="Get a cluster")
def get_cluster(
    ctx: typer.Context,
    cluster_id: Optional[str] = typer.Argument(
        None,
        help="The ID of the cluster to get. If not provided, the default cluster will be used.",
    ),
):
    """
    Get a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)

    service = ClustersService(config, access_token)

    if not cluster_id:
        cfg: AppConfig = utils.get_config_from_ctx(ctx)
        # TODO: Revisit this to improve the UX: start interative selection of cluster
        if not cfg.default_cluster:
            display_manager.print_error(
                "No cluster ID provided and no default cluster set."
            )
            raise typer.Exit(1)
        cluster_id = cfg.default_cluster.id

    try:
        cluster_response = service.get_cluster(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_cluster(cluster_response)


@app.command("delete", help="Delete a cluster")
def delete_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to delete"),
):
    """
    Delete a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service = ClustersService(config, access_token)

    try:
        cluster_response = service.get_cluster(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_cluster(cluster_response)

    if not typer.confirm("Are you sure you want to delete this cluster?"):
        display_manager.display_delete_cluster_message(cluster_response)
        raise typer.Exit()

    try:
        cluster_response = service.delete_cluster(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.print_success(f"Cluster {cluster_id} deleted successfully.")


@app.command("create", help="Create a cluster")
def create_cluster(
    ctx: typer.Context,
    name: str = typer.Argument(help="The name of the cluster"),
    cluster_type: ClusterType = typer.Option(
        ClusterType.CLOUD,
        "--cluster-type",
        help="The type of the cluster",
    ),
):
    """
    Create a cluster.
    """
    # TODO: add support for full ClusterCreateRequest object, either via file or cli flags
    console: Console = Console(theme=custom_theme)
    display_manager: ClustersDisplayManager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)

    service: ClustersService = ClustersService(config, access_token)

    try:
        cluster_create_response = service.create_cluster(
            name=name, cluster_type=cluster_type
        )
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.print_success(
        f"Cluster {cluster_create_response.cluster_id} created successfully."
    )
    display_manager.print_info(
        f"The cluster is in `Staging` state. Please check the status with `exls clusters get {cluster_create_response.cluster_id}`"
    )


@app.command("deploy", help="Deploy a cluster")
def deploy_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to deploy"),
):
    """
    Deploy a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ClustersService = ClustersService(config, access_token)

    try:
        cluster_response = service.get_cluster(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_cluster(cluster_response)

    if not typer.confirm("Are you sure you want to deploy this cluster?"):
        display_manager.display_cluster(cluster_response)
        raise typer.Exit()

    try:
        cluster_response = service.deploy_cluster(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.print_success(
        f"Cluster {cluster_id} deployment started successfully."
    )
    display_manager.print_info(
        f"Please check the status with `exls clusters get {cluster_id}`"
    )


@app.command("list-nodes", help="List all nodes of a cluster")
def list_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to list nodes of"),
):
    """
    List all nodes of a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ClustersService = ClustersService(config, access_token)

    try:
        cluster_nodes_response = service.get_cluster_nodes(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_cluster_nodes(cluster_nodes_response)


@app.command("add-node", help="Add a node to a cluster")
def add_node(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to add a node to"),
    node_ids: List[str] = typer.Argument(
        help="The IDs of the nodes to add to the cluster"
    ),
    node_role: str = typer.Option(
        "WORKER",
        "--node-role",
        help="The role of the nodes to add to the cluster. Can be `WORKER` or `CONTROL_PLANE`, defaults to `WORKER`",
        case_sensitive=True,
        show_choices=True,
        rich_help_panel="Node Role",
        prompt=False,
        callback=lambda v: (
            v
            if v in ("WORKER", "CONTROL_PLANE")
            else typer.BadParameter("node_role must be 'WORKER' or 'CONTROL_PLANE'")
        ),
    ),
):
    """
    Add a node to a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager_clusters = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ClustersService = ClustersService(config, access_token)

    # TODO: Add validation for node_ids

    try:
        cluster_nodes_response = service.add_cluster_node(
            cluster_id=cluster_id,
            nodes_to_add=[
                NodesToAddDTO(node_id=node_id, node_role=node_role)
                for node_id in node_ids
            ],
        )
    except ServiceError as e:
        display_manager_clusters.print_error(e.message)
        raise typer.Exit(1)

    display_manager_clusters.print_success(
        f"Nodes {node_ids} added to cluster {cluster_id} successfully."
    )
    display_manager_clusters.display_cluster_nodes(cluster_nodes_response)


@app.command("show-available-resources", help="Get the resources of a cluster")
def get_cluster_resources(
    ctx: typer.Context,
    cluster_id: Optional[str] = typer.Argument(
        None,
        help="The ID of the cluster to get resources of. If not provided, the default cluster will be used.",
    ),
):
    """
    Get the resources of a cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ClustersService = ClustersService(config, access_token)

    cfg: AppConfig = utils.get_config_from_ctx(ctx)
    if not cluster_id:
        if not cfg.default_cluster:
            display_manager.print_error(
                "No cluster ID provided and no default cluster set."
            )
            raise typer.Exit(1)
        cluster_id = cfg.default_cluster.id

    try:
        cluster_resources_response = service.get_cluster_resources(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_cluster_resources(cluster_resources_response)


@app.command("set-default", help="Set a default cluster")
def set_default_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(help="The ID of the cluster to set as default"),
):
    """
    Set a default cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ClustersService = ClustersService(config, access_token)

    try:
        cluster_response = service.get_cluster(cluster_id)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    cfg: AppConfig = utils.get_config_from_ctx(ctx)
    cfg.default_cluster = ConfigDefaultCluster(
        id=cluster_id, name=cluster_response.cluster.name
    )
    save_config(cfg)
    display_manager.print_success(
        f"Default cluster set to:\n{cfg.default_cluster.name} {cfg.default_cluster.id}"
    )


@app.command("get-default", help="Get the default cluster")
def get_default_cluster(ctx: typer.Context):
    """
    Get the default cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    cfg: AppConfig = utils.get_config_from_ctx(ctx)
    # TODO: This need to got into the service
    if not cfg.default_cluster:
        display_manager.print_info("No default cluster set.")
        raise typer.Exit()
    get_cluster(ctx, cfg.default_cluster.id)


@app.command(
    "list-cloud-credentials",
    help="List all available cloud provider credentials for the current user",
)
def list_cloud_credentials(ctx: typer.Context):
    """List all available cloud provider credentials."""
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: ClustersService = ClustersService(config, access_token)

    try:
        cloud_credentials = service.list_cloud_credentials()
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)

    display_manager.display_cloud_credentials(cloud_credentials)
