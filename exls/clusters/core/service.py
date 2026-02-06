import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import StrictStr

from exls.clusters.core.domain import (
    Cluster,
    ClusterNode,
    ClusterNodeRole,
    ClusterNodeStatus,
    ClusterStatus,
    ClusterSummary,
)
from exls.clusters.core.ports.operations import ClusterOperations
from exls.clusters.core.ports.provider import (
    ClusterNodesImportResult,
    NodesProvider,
)
from exls.clusters.core.ports.repository import (
    ClusterCreateParameters,
    ClusterRepository,
)
from exls.clusters.core.requests import (
    ClusterDeployRequest,
    ClusterNodeSpecification,
)
from exls.clusters.core.results import (
    ClusterNodeIssue,
    ClusterScaleIssue,
    ClusterScaleResult,
    DeployClusterResult,
)
from exls.shared.core.decorators import handle_service_layer_errors
from exls.shared.core.exceptions import ServiceError
from exls.shared.core.polling import PollingTimeoutError, poll_until
from exls.shared.core.ports.file import FileWritePort

logger = logging.getLogger(__name__)


class ClustersService:
    def __init__(
        self,
        clusters_operations: ClusterOperations,
        clusters_repository: ClusterRepository,
        nodes_provider: NodesProvider,
        file_write_adapter: FileWritePort[str],
    ):
        self._clusters_operations: ClusterOperations = clusters_operations
        self._clusters_repository: ClusterRepository = clusters_repository
        self._nodes_provider: NodesProvider = nodes_provider
        self._file_write_adapter: FileWritePort[str] = file_write_adapter

    @handle_service_layer_errors("listing clusters")
    def list_clusters(
        self, status: Optional[ClusterStatus] = None
    ) -> List[ClusterSummary]:
        return self._clusters_repository.list(status=status)

    @handle_service_layer_errors("getting cluster")
    def get_cluster(self, cluster_id: str) -> Cluster:
        cluster: Cluster = self._clusters_repository.get(cluster_id=cluster_id)
        return cluster

    @handle_service_layer_errors("deleting cluster")
    def delete_cluster(self, cluster_id: str) -> str:
        self._clusters_repository.delete(cluster_id=cluster_id)
        return cluster_id

    def _validate_node_ids(
        self,
        node_ids: List[str],
        available_nodes_map: Dict[str, ClusterNode],
    ) -> Tuple[List[str], List[str], List[ClusterNodeIssue]]:
        """
        Validates existence of node IDs and categorizes them.
        Returns:
            - valid_ready_ids: IDs of nodes that exist and are available/discovering.
            - nodes_to_poll: IDs of nodes that exist but are in DISCOVERING state.
            - issues: Validation issues for missing nodes or nodes in invalid states.
        """
        valid_ready_ids: List[str] = []
        nodes_to_poll: List[str] = []
        issues: List[ClusterNodeIssue] = []

        for node_id in node_ids:
            if node_id not in available_nodes_map:
                issues.append(
                    ClusterNodeIssue(
                        node=None,
                        error_message=f"Node {node_id} not found in available nodes",
                    )
                )
                continue

            node: ClusterNode = available_nodes_map[node_id]

            if node.status == ClusterNodeStatus.AVAILABLE:
                valid_ready_ids.append(node_id)
            elif node.status == ClusterNodeStatus.DISCOVERING:
                nodes_to_poll.append(node_id)
            else:
                issues.append(
                    ClusterNodeIssue(
                        node=node,
                        error_message=f"Node {node_id} is in invalid status: {node.status}",
                    )
                )

        return valid_ready_ids, nodes_to_poll, issues

    def _import_nodes_bulk(
        self,
        node_specs: List[ClusterNodeSpecification],
    ) -> Tuple[List[ClusterNode], List[ClusterNodeIssue]]:
        if not node_specs:
            return [], []

        # The provider handles bulk import and should return a result with successes and failures
        # Assuming import_nodes waits if wait_for_available=True
        import_result: ClusterNodesImportResult = self._nodes_provider.import_nodes(
            nodes_specs=node_specs, wait_for_available=True
        )

        valid_nodes: List[ClusterNode] = []
        issues: List[ClusterNodeIssue] = []

        for node in import_result.nodes:
            valid_nodes.append(node)

        for issue in import_result.issues:
            issues.append(
                ClusterNodeIssue(
                    node=None,
                    error_message=f"Error importing node {str(issue.node_specification)}: {issue.error_message}",
                )
            )

        return valid_nodes, issues

    def _wait_for_nodes(
        self, node_ids: List[str]
    ) -> Tuple[List[str], List[ClusterNodeIssue]]:
        if not node_ids:
            return [], []

        def fetch() -> List[ClusterNode]:
            return self._nodes_provider.list_available_nodes()

        def predicate(nodes: List[ClusterNode]) -> bool:
            node_map = {n.id: n for n in nodes}
            for nid in node_ids:
                if nid not in node_map:
                    # We will detect and handle this case in the
                    # final check below
                    continue
                node = node_map[nid]
                if node.status == ClusterNodeStatus.DISCOVERING:
                    return False
            return True

        # We poll the nodes until they are available or we timeout
        # If we timeout, we fetch the nodes again to get the final state
        # and iterate over them to build the final result
        final_nodes: List[ClusterNode] = []
        try:
            final_nodes = poll_until(
                fetcher=fetch,
                predicate=predicate,
                timeout_seconds=60,
                interval_seconds=3,
                error_message="Timed out waiting for nodes to become available",
            )
        except PollingTimeoutError as e:
            logger.warning(f"Timed out waiting for nodes to become available: {e}")
        except Exception as e:
            raise ServiceError(
                f"Unexpected error waiting for nodes to become available: {e}"
            )
        finally:
            final_nodes = fetch()

        node_map = {n.id: n for n in final_nodes}
        ready_ids: List[str] = []
        issues: List[ClusterNodeIssue] = []

        for nid in node_ids:
            if nid not in node_map:
                issues.append(
                    ClusterNodeIssue(
                        node=None,
                        error_message=f"Node {nid} not found after polling",
                    )
                )
                continue

            node = node_map[nid]
            if node.status == ClusterNodeStatus.AVAILABLE:
                ready_ids.append(nid)
            elif node.status == ClusterNodeStatus.DISCOVERING:
                issues.append(
                    ClusterNodeIssue(
                        node=None,
                        error_message=f"Timed out waiting for node {nid} to become available. Node is still in DISCOVERING status.",
                    )
                )
            else:
                issues.append(
                    ClusterNodeIssue(
                        node=None,
                        error_message=f"Node in invalid status after polling: {node.status}",
                    )
                )
        return ready_ids, issues

    @handle_service_layer_errors("deploying cluster")
    def deploy_cluster(
        self, create_params: ClusterDeployRequest
    ) -> DeployClusterResult:
        # List the available nodes that can be deployed to
        available_nodes: List[ClusterNode] = self._nodes_provider.list_available_nodes()
        available_nodes_map: Dict[str, ClusterNode] = {
            node.id: node for node in available_nodes
        }

        # Separate IDs and Specs for Workers
        worker_ids_to_check: List[str] = [
            n for n in create_params.worker_nodes if isinstance(n, str)
        ]
        worker_specs_to_import: List[ClusterNodeSpecification] = [
            n
            for n in create_params.worker_nodes
            if isinstance(n, ClusterNodeSpecification)
        ]

        # Separate IDs and Specs for Control Plane
        cp_ids_to_check: List[str] = []
        cp_specs_to_import: List[ClusterNodeSpecification] = []
        if create_params.control_plane_nodes:
            cp_ids_to_check = [
                n for n in create_params.control_plane_nodes if isinstance(n, str)
            ]
            cp_specs_to_import = [
                n
                for n in create_params.control_plane_nodes
                if isinstance(n, ClusterNodeSpecification)
            ]

        # Validate Existing IDs and Check Status
        valid_worker_ids, worker_poll_ids, worker_id_issues = self._validate_node_ids(
            worker_ids_to_check, available_nodes_map
        )
        valid_cp_ids, cp_poll_ids, cp_id_issues = self._validate_node_ids(
            cp_ids_to_check, available_nodes_map
        )

        # Import New Nodes (Bulk)
        imported_worker_nodes, worker_import_issues = self._import_nodes_bulk(
            worker_specs_to_import
        )
        imported_cp_nodes, cp_import_issues = self._import_nodes_bulk(
            cp_specs_to_import
        )

        # Combine all issues so far
        all_issues: List[ClusterNodeIssue] = (
            worker_id_issues + worker_import_issues + cp_id_issues + cp_import_issues
        )

        # Combine nodes that need polling from existing validation
        polled_ready_worker_ids: List[str] = []
        if worker_poll_ids:
            ready_ids, polling_issues = self._wait_for_nodes(worker_poll_ids)
            polled_ready_worker_ids = ready_ids
            all_issues.extend(polling_issues)

        polled_ready_cp_ids: List[str] = []
        if cp_poll_ids:
            ready_ids, polling_issues = self._wait_for_nodes(cp_poll_ids)
            polled_ready_cp_ids = ready_ids
            all_issues.extend(polling_issues)

        # Final list of IDs
        final_worker_ids = valid_worker_ids + [
            node.id for node in imported_worker_nodes
        ]
        final_cp_ids = valid_cp_ids + [node.id for node in imported_cp_nodes]

        # Add polled IDs to respective lists
        for nid in polled_ready_worker_ids:
            final_worker_ids.append(nid)
        for nid in polled_ready_cp_ids:
            final_cp_ids.append(nid)

        # Check if we have any valid nodes left to deploy
        if not final_worker_ids and not final_cp_ids:
            return DeployClusterResult(
                deployed_cluster=None,
                issues=all_issues,
            )

        # Build the create parameters with only valid nodes
        create_parameters: ClusterCreateParameters = ClusterCreateParameters(
            name=create_params.name,
            type=create_params.type,
            enable_vpn=create_params.enable_vpn,
            enable_telemetry=create_params.enable_telemetry,
            enable_multinode_training=create_params.enable_multinode_training,
            prepare_llm_inference_environment=create_params.prepare_llm_inference_environment,
            colony_id=create_params.colony_id,
            to_be_deleted_at=create_params.to_be_deleted_at,
            worker_node_ids=final_worker_ids,
            control_plane_node_ids=final_cp_ids,
        )

        # Create the cluster
        cluster_id: str = self._clusters_repository.create(parameters=create_parameters)

        # Deploy the cluster
        deployed_cluster_id: str = self._clusters_operations.deploy(
            cluster_id=cluster_id
        )

        final_worker_nodes: List[ClusterNode] = []
        for node_id in valid_worker_ids + polled_ready_worker_ids:
            worker_node: ClusterNode = available_nodes_map[node_id]
            worker_node.role = ClusterNodeRole.WORKER
            final_worker_nodes.append(worker_node)

        final_cp_nodes: List[ClusterNode] = []
        for node_id in valid_cp_ids + polled_ready_cp_ids:
            cp_node: ClusterNode = available_nodes_map[node_id]
            cp_node.role = ClusterNodeRole.CONTROL_PLANE
            final_cp_nodes.append(cp_node)

        cluster: Cluster = self._clusters_repository.get(cluster_id=deployed_cluster_id)
        cluster_with_nodes: Cluster = Cluster(
            id=cluster.id,
            name=cluster.name,
            status=cluster.status,
            type=cluster.type,
            created_at=cluster.created_at,
            updated_at=cluster.updated_at,
            nodes=(
                final_worker_nodes
                + final_cp_nodes
                + imported_worker_nodes
                + imported_cp_nodes
            ),
        )

        # Return result with any issues encountered during the process
        return DeployClusterResult(
            deployed_cluster=cluster_with_nodes, issues=all_issues
        )

    def _validate_cluster_status(self, cluster: ClusterSummary) -> None:
        if cluster.status == ClusterStatus.READY:
            return
        if cluster.status == ClusterStatus.DEPLOYING:
            raise ServiceError(f"Cluster {cluster.name} is still deploying.")
        elif cluster.status == ClusterStatus.FAILED:
            raise ServiceError(f"Cluster {cluster.name} deployment failed.")
        else:
            raise ServiceError(
                f"Cluster {cluster.id} is in an unknown status: {cluster.status}"
            )

    @handle_service_layer_errors("scaling up cluster")
    def scale_up_cluster(
        self, cluster_id: str, node_ids: List[StrictStr]
    ) -> ClusterScaleResult:
        cluster: Cluster = self.get_cluster(cluster_id=cluster_id)
        self._validate_cluster_status(cluster=cluster)

        available_nodes: List[ClusterNode] = self._nodes_provider.list_available_nodes()
        available_nodes_map: Dict[str, ClusterNode] = {
            node.id: node for node in available_nodes
        }

        nodes_to_add: List[ClusterNode] = []
        issues: List[ClusterScaleIssue] = []
        for node_id in node_ids:
            if node_id not in available_nodes_map:
                issues.append(
                    ClusterScaleIssue(
                        node=None,
                        error_message=f"Node {node_id} not found in available nodes",
                    )
                )
                continue
            nodes_to_add.append(available_nodes_map[node_id])

        if not nodes_to_add:
            return ClusterScaleResult(nodes=[], issues=issues)

        scale_result: ClusterScaleResult = self._clusters_operations.scale_up(
            cluster_id=cluster_id, nodes_to_add=nodes_to_add
        )
        return ClusterScaleResult(
            nodes=scale_result.nodes, issues=issues + (scale_result.issues or [])
        )

    @handle_service_layer_errors("removing nodes from cluster")
    def remove_nodes_from_cluster(
        self, cluster_id: str, node_ids: List[StrictStr]
    ) -> ClusterScaleResult:
        cluster: Cluster = self.get_cluster(cluster_id=cluster_id)
        self._validate_cluster_status(cluster=cluster)

        cluster_nodes_map: Dict[str, ClusterNode] = {
            node.id: node for node in cluster.nodes
        }

        nodes_to_remove: List[ClusterNode] = []
        issues: List[ClusterScaleIssue] = []
        for node_id in node_ids:
            if node_id not in cluster_nodes_map:
                issues.append(
                    ClusterScaleIssue(
                        node=None,
                        error_message=f"Node {node_id} not part of the cluster {cluster.name} nodes",
                    )
                )
                continue
            nodes_to_remove.append(cluster_nodes_map[node_id])

        if not nodes_to_remove:
            return ClusterScaleResult(nodes=[], issues=issues)

        scale_result: ClusterScaleResult = self._clusters_operations.scale_down(
            cluster_id=cluster_id, nodes_to_remove=nodes_to_remove
        )
        return ClusterScaleResult(
            nodes=scale_result.nodes, issues=issues + (scale_result.issues or [])
        )

    @handle_service_layer_errors("importing kubeconfig")
    def import_kubeconfig(
        self,
        cluster_id: str,
        kubeconfig_file_path: str = Path.home().joinpath(".kube", "config").as_posix(),
    ) -> None:
        cluster: Cluster = self.get_cluster(cluster_id=cluster_id)
        self._validate_cluster_status(cluster=cluster)

        kubeconfig_content: str = self._clusters_operations.load_kubeconfig(
            cluster_id=cluster_id
        )
        self._file_write_adapter.write_file(
            file_path=Path(kubeconfig_file_path), content=kubeconfig_content
        )

    @handle_service_layer_errors("getting dashboard url")
    def get_dashboard_url(self, cluster_id: str) -> str:
        cluster: Cluster = self.get_cluster(cluster_id=cluster_id)
        self._validate_cluster_status(cluster=cluster)

        return self._clusters_operations.get_dashboard_url(cluster_id=cluster_id)

    def list_available_nodes(self) -> List[ClusterNode]:
        return self._nodes_provider.list_available_nodes()
