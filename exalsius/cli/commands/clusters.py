from typing import List, Optional

import typer
from rich.console import Console

from exalsius.cli import config
from exalsius.core.services.clusters_service import ClustersService
from exalsius.core.services.node_service import NodeService
from exalsius.display.clusters_display import ClustersDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context):
    """
    Manage clusters.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("list", help="List all clusters")
def list_clusters(
    status: Optional[str] = typer.Option(
        None,
        "--status",
        help="Filter clusters by status",
    ),
):
    """
    List all clusters.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)
    clusters, error = service.list_clusters(status)
    if error:
        display_manager.print_error(f"Failed to list clusters: {error}")
        raise typer.Exit(1)
    display_manager.display_clusters(clusters)


@app.command("get", help="Get a cluster")
def get_cluster(
    cluster_id: str = typer.Argument(help="The ID of the cluster to get"),
):
    """
    Get a cluster.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)
    cluster_response, error = service.get_cluster(cluster_id)
    if error:
        display_manager.print_error(f"Failed to get cluster: {error}")
        raise typer.Exit(1)
    display_manager.display_cluster(cluster_response)


@app.command("delete", help="Delete a cluster")
def delete_cluster(
    cluster_id: str = typer.Argument(help="The ID of the cluster to delete"),
):
    """
    Delete a cluster.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)

    cluster_response, error = service.get_cluster(cluster_id)
    if error:
        display_manager.print_error(f"Failed to get cluster: {error}")
        raise typer.Exit(1)

    display_manager.display_cluster(cluster_response)

    if not typer.confirm("Are you sure you want to delete this cluster?"):
        display_manager.display_delete_cluster_message(cluster_response)
        raise typer.Exit()

    cluster_response, error = service.delete_cluster(cluster_id)
    if error:
        display_manager.print_error(f"Failed to delete cluster: {error}")
        raise typer.Exit(1)
    display_manager.print_success(f"Cluster {cluster_id} deleted successfully.")


@app.command("create", help="Create a cluster")
def create_cluster(
    name: str = typer.Argument(help="The name of the cluster"),
    k8s_version: str = typer.Option(
        "v1.28.1",
        "--k8s-version",
        help="The Kubernetes version to use for the cluster",
    ),
):
    """
    Create a cluster.
    """
    # TODO: add support for full ClusterCreateRequest object, either via file or cli flags
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)
    cluster_create_response, error = service.create_cluster(name, k8s_version)
    if error:
        display_manager.print_error(f"Failed to create cluster: {error}")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Cluster {cluster_create_response.cluster_id} created successfully."
    )
    display_manager.print_info(
        f"The cluster is in `Staging` state. Please check the status with `exls clusters get {cluster_create_response.cluster_id}`"
    )


@app.command("deploy", help="Deploy a cluster")
def deploy_cluster(
    cluster_id: str = typer.Argument(help="The ID of the cluster to deploy"),
):
    """
    Deploy a cluster.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)
    cluster_response, error = service.get_cluster(cluster_id)
    if error:
        display_manager.print_error(f"Failed to get cluster: {error}")
        raise typer.Exit(1)
    display_manager.display_cluster(cluster_response)

    if not typer.confirm("Are you sure you want to deploy this cluster?"):
        display_manager.display_deploy_cluster_message(cluster_response)
        raise typer.Exit()

    cluster_response, error = service.deploy_cluster(cluster_id)
    if error:
        display_manager.print_error(f"Failed to deploy cluster: {error}")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Cluster {cluster_id} deployment started successfully."
    )
    display_manager.print_info(
        f"Please check the status with `exls clusters get {cluster_id}`"
    )


@app.command("list-services", help="List all services of a cluster")
def list_services(
    cluster_id: str = typer.Argument(help="The ID of the cluster to list services of"),
):
    """
    List all services of a cluster.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)
    cluster_services_response, error = service.get_cluster_services(cluster_id)
    if error:
        display_manager.print_error(f"Failed to get cluster services: {error}")
        raise typer.Exit(1)

    if not cluster_services_response.services_deployments:
        display_manager.print_info("No services deployed to this cluster.")
        raise typer.Exit()

    display_manager.display_cluster_services(cluster_services_response)


@app.command("list-nodes", help="List all nodes of a cluster")
def list_nodes(
    cluster_id: str = typer.Argument(help="The ID of the cluster to list nodes of"),
):
    """
    List all nodes of a cluster.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)
    cluster_nodes_response, error = service.get_cluster_nodes(cluster_id)
    if error:
        display_manager.print_error(f"Failed to get cluster nodes: {error}")
        raise typer.Exit(1)

    if (
        not cluster_nodes_response.control_plane_node_ids
        and not cluster_nodes_response.worker_node_ids
    ):
        display_manager.print_info("No nodes in this cluster.")
        raise typer.Exit()

    display_manager.display_cluster_nodes(cluster_nodes_response)


@app.command("add-node", help="Add a node to a cluster")
def add_node(
    cluster_id: str = typer.Argument(help="The ID of the cluster to add a node to"),
    node_ids: List[str] = typer.Argument(
        help="The IDs of the nodes to add to the cluster"
    ),
    node_role: str = typer.Option(
        "worker",
        "--node-role",
        help="The role of the nodes to add to the cluster. Can be `worker` or `control-plane`, defaults to `control plane`",
    ),
):
    """
    Add a node to a cluster.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    node_service = NodeService()
    display_manager = ClustersDisplayManager(console)

    for node_id in node_ids:
        node_response, node_error = node_service.get_node(node_id)
        if node_error:
            display_manager.print_error(f"Failed to get node: {node_error}")
            raise typer.Exit(1)

        display_manager.display_node(node_response)

        if not typer.confirm("Are you sure you want to add this node to the cluster?"):
            display_manager.display_add_node_message(node_response)
            raise typer.Exit()

    cluster_nodes_response, error = service.add_cluster_node(
        cluster_id, node_ids, node_role
    )
    if error:
        display_manager.print_error(f"Failed to add nodes to cluster: {error}")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Nodes {node_ids} added to cluster {cluster_id} successfully."
    )
    display_manager.display_cluster_nodes(cluster_nodes_response)


@app.command("show-available-resources", help="Get the resources of a cluster")
def get_cluster_resources(
    cluster_id: str = typer.Argument(help="The ID of the cluster to get resources of"),
):
    """
    Get the resources of a cluster.
    """
    console = Console(theme=custom_theme)
    service = ClustersService()
    display_manager = ClustersDisplayManager(console)
    cluster_resources_response, error = service.get_cluster_resources(cluster_id)
    if error:
        display_manager.print_error(f"Failed to get cluster resources: {error}")
        raise typer.Exit(1)
    if not cluster_resources_response:
        display_manager.print_info("No resources available for this cluster.")
        raise typer.Exit()
    display_manager.display_cluster_resources(cluster_resources_response)


@app.command("set-default", help="Set a default cluster")
def set_default_cluster(
    cluster_id: str = typer.Argument(help="The ID of the cluster to set as default"),
):
    """
    Set a default cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)
    service = ClustersService()

    cluster_response, error = service.get_cluster(cluster_id)
    if error:
        display_manager.print_error(f"Error loading cluster: {error}")
        raise typer.Exit(1)
    if not cluster_response:
        display_manager.print_error(f"Cluster with ID '{cluster_id}' not found.")
        raise typer.Exit(1)

    cfg: config.AppConfig = config.load()
    cfg.default_cluster = config.ConfigDefaultCluster(
        id=cluster_id, name=cluster_response.cluster.name
    )
    config.save(cfg)
    display_manager.print_success(
        f"Default cluster set to:\n{cfg.default_cluster.name} {cfg.default_cluster.id}"
    )


@app.command("get-default", help="Get the default cluster")
def get_default_cluster():
    """
    Get the default cluster.
    """
    console = Console(theme=custom_theme)
    display_manager = ClustersDisplayManager(console)

    cluster_id = config.active_cluster()
    if not cluster_id:
        display_manager.print_info("No default cluster set.")
    else:
        get_cluster(cluster_id.id)
