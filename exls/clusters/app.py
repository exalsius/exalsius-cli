from pathlib import Path
from typing import List, Optional

import typer

from exls.clusters.adapters.bundle import ClustersBundle
from exls.clusters.adapters.ui.display.render import (
    CLUSTER_LIST_VIEW,
    CLUSTER_NODE_ISSUE_VIEW,
    CLUSTER_NODE_LIST_VIEW,
    CLUSTER_NODE_RESOURCES_VIEW,
    CLUSTER_WITH_NODES_VIEW,
)
from exls.clusters.adapters.ui.flows.cluster_deploy import (
    DeployClusterFlow,
    FlowDeployClusterRequestDTO,
)
from exls.clusters.core.domain import (
    Cluster,
    ClusterStatus,
    ClusterType,
)
from exls.clusters.core.requests import ClusterDeployRequest
from exls.clusters.core.results import DeployClusterResult
from exls.clusters.core.service import ClustersService
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.facade.facade import IOBaseModelFacade
from exls.shared.adapters.ui.flow.flow import FlowContext
from exls.shared.adapters.ui.utils import (
    called_with_any_user_input,
    help_if_no_subcommand,
    open_url_in_browser,
)
from exls.shared.core.utils import (
    generate_random_name,
    validate_kubernetes_name,
)

clusters_app = typer.Typer()


@clusters_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage clusters.
    """
    help_if_no_subcommand(ctx)


@clusters_app.command("list", help="List all clusters")
@handle_application_layer_errors(ClustersBundle)
def list_clusters(
    ctx: typer.Context,
    status: Optional[ClusterStatus] = typer.Option(
        None,
        "--status",
        help="Filter clusters by status",
    ),
):
    """
    List all clusters.
    """
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    clusters_domain: List[Cluster] = service.list_clusters(status=status)
    io_facade.display_data(
        clusters_domain, bundle.object_output_format, view_context=CLUSTER_LIST_VIEW
    )


@clusters_app.command("get", help="Get a cluster")
@handle_application_layer_errors(ClustersBundle)
def get_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(..., help="The ID of the cluster to get"),
):
    """
    Get a cluster.
    """
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster_domain: Cluster = service.get_cluster(cluster_id)

    io_facade.display_data(
        cluster_domain,
        bundle.object_output_format,
        view_context=CLUSTER_LIST_VIEW,
    )


@clusters_app.command("delete", help="Delete a cluster")
@handle_application_layer_errors(ClustersBundle)
def delete_cluster(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(..., help="The ID of the cluster to delete"),
    confirmation: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Confirm the deletion of the cluster. If not provided, you will be asked for confirmation.",
    ),
):
    """
    Delete a cluster.
    """
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster_domain: Cluster = service.get_cluster(cluster_id)

    if not confirmation:
        io_facade.display_data(
            cluster_domain,
            bundle.object_output_format,
            view_context=CLUSTER_LIST_VIEW,
        )
        user_confirmation: bool = io_facade.ask_confirm(
            message="Are you sure you want to delete this cluster?"
        )
        if not user_confirmation:
            raise typer.Exit()

    service.delete_cluster(cluster_id)

    io_facade.display_success_message(
        f"Cluster {cluster_id} deleted successfully.", bundle.message_output_format
    )


def _validate_worker_node_ids(value: Optional[List[str]]) -> Optional[List[str]]:
    if value is None:
        return None
    if len(value) == 0:
        raise typer.BadParameter("At least one worker node ID must be specified")
    return value


@clusters_app.command("deploy", help="Create a cluster")
@handle_application_layer_errors(ClustersBundle)
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
    worker_node_ids: Optional[List[str]] = typer.Option(
        None,
        "--worker-nodes",
        help="The IDs of the worker nodes to add to the cluster.",
        show_default=False,
        callback=_validate_worker_node_ids,
    ),
    enable_multinode_training: bool = typer.Option(
        False,
        "--enable-multinode-training",
        help="Enable multinode AI model training for the cluster",
    ),
    prepare_llm_inference_environment: bool = typer.Option(
        False,
        "--prepare-llm-inference-environment",
        help="Prepare LLM inference environment for the cluster",
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
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    deploy_cluster_request: ClusterDeployRequest
    if interactive or called_with_any_user_input(ctx):
        cluster_deploy_request_dto: FlowDeployClusterRequestDTO = (
            FlowDeployClusterRequestDTO()
        )
        deploy_cluster_flow: DeployClusterFlow = bundle.get_deploy_cluster_flow()
        deploy_cluster_flow.execute(
            cluster_deploy_request_dto, FlowContext(), io_facade
        )
        deploy_cluster_request = ClusterDeployRequest(
            name=cluster_deploy_request_dto.name,
            type=ClusterType.from_str(cluster_deploy_request_dto.cluster_type.value),
            worker_nodes=[
                node.id for node in cluster_deploy_request_dto.worker_node_ids
            ],
            control_plane_nodes=[],
            enable_multinode_training=cluster_deploy_request_dto.enable_multinode_training,
            prepare_llm_inference_environment=cluster_deploy_request_dto.prepare_llm_inference_environment,
            enable_telemetry=cluster_deploy_request_dto.enable_telemetry,
            enable_vpn=False,
        )
    else:
        deploy_cluster_request = ClusterDeployRequest(
            name=name,
            type=ClusterType.REMOTE,
            worker_nodes=[node for node in worker_node_ids or []],
            enable_multinode_training=enable_multinode_training,
            prepare_llm_inference_environment=prepare_llm_inference_environment,
            enable_telemetry=enable_telemetry,
            enable_vpn=False,
        )
    result: DeployClusterResult = service.deploy_cluster(deploy_cluster_request)

    # Handle success and error cases
    # Case success: all nodes were added to the cluster, cluster deployment started
    if result.is_success:
        assert result.deployed_cluster is not None
        io_facade.display_success_message(
            message=f"Started deploying cluster {result.deployed_cluster.name}.",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=result.deployed_cluster,
            output_format=bundle.object_output_format,
            view_context=CLUSTER_WITH_NODES_VIEW,
        )
    # Case partially successful: not all nodes were added to the cluster
    # cluster deployment started with nodes that were successfully added
    elif result.is_partially_successful:
        assert result.deployed_cluster is not None
        io_facade.display_info_message(
            message=f"Started deploying cluster {result.deployed_cluster.name} with some issues.",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=result.deployed_cluster,
            output_format=bundle.object_output_format,
            view_context=CLUSTER_LIST_VIEW,
        )
        io_facade.display_error_message(
            message="Following nodes could not be added to the cluster:",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=result.issues,
            output_format=bundle.object_output_format,
            view_context=CLUSTER_NODE_ISSUE_VIEW,
        )
    # Case error: no nodes were added to the cluster
    # cluster deployment cannot be started
    else:
        io_facade.display_error_message(
            message="Failed to deploy cluster. The selected nodes cannot be added to the cluster:",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=result.issues,
            output_format=bundle.object_output_format,
            view_context=CLUSTER_NODE_ISSUE_VIEW,
        )


@clusters_app.command("list-nodes", help="List all nodes of a cluster")
@handle_application_layer_errors(ClustersBundle)
def list_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument("", help="The ID of the cluster to list nodes of"),
):
    """
    List all nodes of a cluster.
    """
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster: Cluster = service.get_cluster(cluster_id)

    io_facade.display_info_message(
        message=f"Nodes of cluster '{cluster.name}':",
        output_format=bundle.message_output_format,
    )
    io_facade.display_data(
        data=cluster.nodes,
        output_format=bundle.object_output_format,
        view_context=CLUSTER_NODE_LIST_VIEW,
    )


@clusters_app.command("add-nodes", help="Add nodes to a cluster")
@handle_application_layer_errors(ClustersBundle)
def add_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument("", help="The ID of the cluster to add a node to"),
    worker_node_ids: List[str] = typer.Option(
        [],
        "--worker-nodes",
        help="The IDs of the worker nodes to add to the cluster.",
        show_default=False,
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help="Enable interactive mode to add nodes to the cluster",
    ),
):
    """
    Add nodes to a cluster.
    """
    raise NotImplementedError("Not implemented yet")


@clusters_app.command("remove-nodes", help="Remove nodes from a cluster")
@handle_application_layer_errors(ClustersBundle)
def remove_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to remove nodes from"
    ),
    node_ids: List[str] = typer.Option(
        [],
        "--node-ids",
        help="The IDs of the nodes to remove from the cluster.",
        show_default=False,
    ),
):
    """
    Remove nodes from a cluster.
    """
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    removed_node_ids: List[str] = service.remove_nodes_from_cluster(
        cluster_id=cluster_id,
        node_ids=node_ids,
    )

    io_facade.display_success_message(
        message=f"Following nodes removed from cluster {cluster_id} successfully: {', '.join(removed_node_ids)}.",
        output_format=bundle.message_output_format,
    )


@clusters_app.command("show-available-resources", help="Get the resources of a cluster")
@handle_application_layer_errors(ClustersBundle)
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
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster: Cluster = service.get_cluster(cluster_id=cluster_id)

    io_facade.display_info_message(
        message=f"Available resources of cluster '{cluster.name}':",
        output_format=bundle.message_output_format,
    )
    io_facade.display_data(
        data=cluster.nodes,
        output_format=bundle.object_output_format,
        view_context=CLUSTER_NODE_RESOURCES_VIEW,
    )


@clusters_app.command(
    "get-dashboard-url", help="Get the monitoring dashboard URL of a cluster"
)
@handle_application_layer_errors(ClustersBundle)
def get_dashboard_url(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to get the monitoring dashboard URL of"
    ),
    open_browser: bool = typer.Option(
        False,
        "--open",
        help="Open the dashboard URL in the default browser",
    ),
):
    """
    Get the monitoring dashboard URL of a cluster.
    """
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    dashboard_url_str: str = service.get_dashboard_url(cluster_id)

    if open_browser:
        if open_url_in_browser(dashboard_url_str):
            io_facade.display_success_message(
                "Opening dashboard in browser...", bundle.message_output_format
            )
        else:
            io_facade.display_error_message(
                "Failed to open browser. Please open the URL manually.",
                bundle.message_output_format,
            )

    io_facade.display_success_message(
        f"Monitoring Dashboard URL: {dashboard_url_str}", bundle.message_output_format
    )


@clusters_app.command(
    "import-kubeconfig", help="Import a kubeconfig file into a cluster"
)
@handle_application_layer_errors(ClustersBundle)
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
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOBaseModelFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    service.import_kubeconfig(cluster_id, kubeconfig_path)

    io_facade.display_success_message(
        message=f"Kubeconfig from cluster {cluster_id} successfully imported to {kubeconfig_path}.",
        output_format=bundle.message_output_format,
    )
