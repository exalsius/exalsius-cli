from pathlib import Path
from typing import List, Optional

import typer
from pydantic import StrictStr

from exls.clusters.adapters.bundle import ClustersBundle
from exls.clusters.adapters.dtos import (
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    DashboardUrlResponseDTO,
)
from exls.clusters.adapters.ui.display.display import IOClustersFacade
from exls.clusters.adapters.ui.dtos import DeployClusterRequestFromFlowDTO
from exls.clusters.adapters.ui.flows.cluster_deploy import DeployClusterFlow
from exls.clusters.adapters.ui.mapper import (
    cluster_dto_from_domain,
    cluster_node_dto_from_domain,
    cluster_node_resources_dto_from_domain,
    cluster_with_nodes_dto_from_domain,
    node_validation_issue_dto_from_domain,
)
from exls.clusters.core.domain import (
    AssignedClusterNode,
    Cluster,
    ClusterNodeResources,
    ClusterStatus,
    ClusterType,
    ClusterWithNodes,
    DeployClusterResult,
    NodesLoadingResult,
)
from exls.clusters.core.requests import ClusterDeployRequest
from exls.clusters.core.service import ClustersService
from exls.shared.adapters.decorators import handle_application_layer_errors
from exls.shared.adapters.ui.flow.flow import FlowContext
from exls.shared.adapters.ui.utils import (
    called_with_any_user_input,
    help_if_no_subcommand,
    open_url_in_browser,
)
from exls.shared.core.domain import (
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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    clusters_domain: List[Cluster] = service.list_clusters(status=status)
    clusters_dto: List[ClusterDTO] = [
        cluster_dto_from_domain(domain=cluster) for cluster in clusters_domain
    ]
    io_facade.display_data(clusters_dto, bundle.object_output_format)


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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster_domain: ClusterWithNodes = service.get_cluster(cluster_id)

    io_facade.display_data(
        cluster_with_nodes_dto_from_domain(domain=cluster_domain),
        bundle.object_output_format,
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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster_domain: Cluster = service.get_cluster(cluster_id)
    cluster_dto: ClusterDTO = cluster_dto_from_domain(domain=cluster_domain)

    if not confirmation:
        io_facade.display_data(cluster_dto, bundle.object_output_format)
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
    enable_vpn: bool = typer.Option(
        False,
        "--enable-vpn",
        help="Enable VPN for the cluster",
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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    deploy_cluster_request: ClusterDeployRequest
    if interactive or called_with_any_user_input(ctx):
        cluster_deploy_request_dto: DeployClusterRequestFromFlowDTO = (
            DeployClusterRequestFromFlowDTO()
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
            enable_telemetry=cluster_deploy_request_dto.enable_telemetry,
            enable_vpn=cluster_deploy_request_dto.enable_vpn,
        )
    else:
        deploy_cluster_request = ClusterDeployRequest(
            name=name,
            type=ClusterType.REMOTE,
            worker_nodes=[node for node in worker_node_ids or []],
            enable_multinode_training=enable_multinode_training,
            enable_telemetry=False,
            enable_vpn=enable_vpn,
        )
    result: DeployClusterResult = service.deploy_cluster(deploy_cluster_request)

    # Handle success and error cases
    # Case success: all nodes were added to the cluster, cluster deployment started
    if result.is_success:
        assert result.cluster is not None
        io_facade.display_success_message(
            message=f"Started deploying cluster {result.cluster.name}.",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=cluster_with_nodes_dto_from_domain(domain=result.cluster),
            output_format=bundle.object_output_format,
        )
    # Case partially successful: not all nodes were added to the cluster
    # cluster deployment started with nodes that were successfully added
    elif result.is_partially_successful:
        assert result.cluster is not None
        io_facade.display_info_message(
            message=f"Started deploying cluster {result.cluster.name} with some issues.",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=cluster_dto_from_domain(domain=result.cluster),
            output_format=bundle.object_output_format,
        )
        io_facade.display_error_message(
            message="Following nodes could not be added to the cluster:",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=[
                node_validation_issue_dto_from_domain(issue) for issue in result.issues
            ],
            output_format=bundle.object_output_format,
        )
    # Case error: no nodes were added to the cluster
    # cluster deployment cannot be started
    else:
        io_facade.display_error_message(
            message="Failed to deploy cluster. The selected nodes cannot be added to the cluster:",
            output_format=bundle.message_output_format,
        )
        io_facade.display_data(
            data=[
                node_validation_issue_dto_from_domain(issue) for issue in result.issues
            ],
            output_format=bundle.object_output_format,
        )


@clusters_app.command("list-nodes", help="List all nodes of a cluster")
@handle_application_layer_errors(ClustersBundle)
def list_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument("", help="The ID of the cluster to list nodes of"),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help="Enable interactive mode to list nodes of the cluster",
    ),
):
    """
    List all nodes of a cluster.
    """
    bundle: ClustersBundle = ClustersBundle(ctx)
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster: Cluster = service.get_cluster(cluster_id)

    nodes_loading_result: NodesLoadingResult = service.get_cluster_nodes(cluster_id)
    if not nodes_loading_result.is_success:
        io_facade.display_error_message(
            message=(
                f"Failed to load nodes of cluster '{cluster.name}': "
                f"{'\n'.join([issue.issue for issue in nodes_loading_result.issues or []])}"
            ),
            output_format=bundle.message_output_format,
        )
        raise typer.Exit(1)

    cluster_nodes: List[AssignedClusterNode] = nodes_loading_result.nodes
    cluster_nodes_dto: List[ClusterNodeDTO] = [
        cluster_node_dto_from_domain(domain=node, cluster_name=cluster.name)
        for node in cluster_nodes
    ]
    io_facade.display_info_message(
        message=f"Nodes of cluster '{cluster.name}':",
        output_format=bundle.message_output_format,
    )
    io_facade.display_data(
        data=cluster_nodes_dto, output_format=bundle.object_output_format
    )


@clusters_app.command("add-nodes", help="Add nodes to a cluster")
@handle_application_layer_errors(ClustersBundle)
def add_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument("", help="The ID of the cluster to add a node to"),
    worker_node_ids: List[StrictStr] = typer.Option(
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
    # bundle: ClustersBundle = ClustersBundle(ctx)
    # display_manager = TableClusterDisplayManager()
    # config: AppConfig = bundle.config
    # access_token: str = bundle.access_token

    # from exls.nodes.service import get_node_service

    # node_service: NodesService = get_node_service(config, access_token)
    # service: ClustersService = bundle.get_clusters_service()

    # try:
    #     available_nodes: List[NodeDTO] = node_service.list_nodes(
    #         NodesListRequestDTO(status=AllowedNodeStatusFiltersDTO.AVAILABLE)
    #     )
    # except ServiceError as e:
    #     display_manager.display_error(ErrorDisplayModel(message=str(e)))
    #     raise typer.Exit(1)
    # if len(available_nodes) == 0:
    #     display_manager.display_error(
    #         ErrorDisplayModel(
    #             message="No available nodes in the node pool found. Please import nodes first."
    #         )
    #     )
    #     raise typer.Exit()

    # try:
    #     request = ListClustersRequestDTO()
    #     filter_params = cluster_list_filter_params_from_request_dto(request)
    #     available_clusters_domain: List[Cluster] = service.list_clusters(filter_params)
    #     available_clusters: List[ClusterDTO] = [
    #         ClusterDTO.from_domain(c) for c in available_clusters_domain
    #     ]
    # except ServiceError as e:
    #     display_manager.display_error(ErrorDisplayModel(message=str(e)))
    #     raise typer.Exit(1)
    # if len(available_clusters) == 0:
    #     display_manager.display_error(
    #         ErrorDisplayModel(
    #             message="No available clusters found. Please create a cluster first."
    #         )
    #     )
    #     raise typer.Exit()

    # validation_error: Optional[ErrorDisplayModel] = _validate_node_ids(
    #     available_nodes=available_nodes,
    #     node_ids=worker_node_ids,
    # )
    # if validation_error:
    #     display_manager.display_error(error=validation_error)
    #     raise typer.Exit()

    # if interactive or _called_with_any_user_input(ctx):
    #     display: ComposingClusterDisplayManager = ComposingClusterDisplayManager(
    #         display_manager=display_manager
    #     )
    #     interactive_flow: AddNodesInteractiveFlow = AddNodesInteractiveFlow(
    #         available_clusters=available_clusters,
    #         available_nodes=available_nodes,
    #         display_manager=display,
    #     )
    #     try:
    #         add_nodes_request: AddNodesRequestDTO = interactive_flow.run()
    #     except ClusterFlowInterruptionException as e:
    #         display_manager.display_info(str(e))
    #         raise typer.Exit(0)
    #     except ExalsiusError as e:
    #         display_manager.display_error(ErrorDisplayModel(message=str(e)))
    #         raise typer.Exit(1)
    # else:
    #     add_nodes_request = AddNodesRequestDTO(
    #         cluster_id=cluster_id,
    #         node_ids=worker_node_ids,
    #         node_role=AllowedClusterNodeRoleDTO.WORKER,
    #     )

    # try:
    #     params = cluster_add_nodes_params_from_add_nodes_request_dto(add_nodes_request)
    #     nodes_data = service.add_cluster_nodes(params)
    #     nodes: List[ClusterNodeDTO] = []
    #     for item in nodes_data:
    #         cluster, node_ref, node = item
    #         nodes.append(
    #             ClusterNodeDTO.from_domain(
    #                 cluster=cluster, cluster_node_ref=node_ref, node=node
    #             )
    #         )
    # except ServiceError as e:
    #     display_manager.display_error(ErrorDisplayModel(message=str(e)))
    #     raise typer.Exit(1)

    # display_manager.display_success(
    #     f" {len(worker_node_ids)} worker nodes added to cluster {cluster_id} successfully."
    # )
    # display_manager.display_cluster_nodes(nodes)


@clusters_app.command("remove-nodes", help="Remove nodes from a cluster")
@handle_application_layer_errors(ClustersBundle)
def remove_nodes(
    ctx: typer.Context,
    cluster_id: str = typer.Argument(
        ..., help="The ID of the cluster to remove nodes from"
    ),
    node_ids: List[StrictStr] = typer.Option(
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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    removed_node_ids: List[StrictStr] = service.remove_nodes_from_cluster(
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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    cluster: Cluster = service.get_cluster(cluster_id=cluster_id)
    cluster_node_resources: List[ClusterNodeResources] = service.get_cluster_resources(
        cluster_id
    )
    cluster_node_resources_dto: List[ClusterNodeResourcesDTO] = [
        cluster_node_resources_dto_from_domain(domain=res, cluster_name=cluster.name)
        for res in cluster_node_resources
    ]

    io_facade.display_info_message(
        message=f"Available resources of cluster '{cluster.name}':",
        output_format=bundle.message_output_format,
    )
    io_facade.display_data(
        data=cluster_node_resources_dto, output_format=bundle.object_output_format
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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    dashboard_url_str: str = service.get_dashboard_url(cluster_id)
    dashboard_url = DashboardUrlResponseDTO(url=dashboard_url_str)

    if open_browser:
        if open_url_in_browser(dashboard_url.url):
            io_facade.display_success_message(
                "Opening dashboard in browser...", bundle.message_output_format
            )
        else:
            io_facade.display_error_message(
                "Failed to open browser. Please open the URL manually.",
                bundle.message_output_format,
            )

    io_facade.display_success_message(
        f"Monitoring Dashboard URL: {dashboard_url.url}", bundle.message_output_format
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
    io_facade: IOClustersFacade = bundle.get_io_facade()
    service: ClustersService = bundle.get_clusters_service()

    service.import_kubeconfig(cluster_id, kubeconfig_path)

    io_facade.display_success_message(
        message=f"Kubeconfig from cluster {cluster_id} successfully imported to {kubeconfig_path}.",
        output_format=bundle.message_output_format,
    )
