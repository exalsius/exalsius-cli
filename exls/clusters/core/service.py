import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, cast

from pydantic import StrictStr

from exls.clusters.core.domain import (
    AssignedClusterNode,
    Cluster,
    ClusterNode,
    ClusterNodeResources,
    ClusterNodeRole,
    ClusterNodeStatus,
    ClusterStatus,
    ClusterWithNodes,
    DeployClusterResult,
    NodeLoadingIssue,
    NodesLoadingResult,
    NodeValidationIssue,
    UnassignedClusterNode,
)
from exls.clusters.core.ports.gateway import (
    ClusterCreateParameters,
    ClusterNodeRefResources,
    IClustersGateway,
)
from exls.clusters.core.ports.provider import ClusterNodesImportResult, INodesProvider
from exls.clusters.core.requests import (
    AddNodesRequest,
    ClusterDeployRequest,
    NodeRef,
    NodeSpecification,
)
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.adapters.gateway.file.gateways import IFileWriteGateway
from exls.shared.core.polling import PollingTimeoutError, poll_until
from exls.shared.core.service import ServiceError

logger = logging.getLogger(__name__)


class ClustersService:
    def __init__(
        self,
        clusters_gateway: IClustersGateway,
        nodes_provider: INodesProvider,
        file_write_gateway: IFileWriteGateway[str],
    ):
        self.clusters_gateway: IClustersGateway = clusters_gateway
        self.nodes_provider: INodesProvider = nodes_provider
        self.file_write_gateway: IFileWriteGateway[str] = file_write_gateway

    @handle_service_layer_errors("listing clusters")
    def list_clusters(self, status: Optional[ClusterStatus] = None) -> List[Cluster]:
        clusters: List[Cluster] = self.clusters_gateway.list(status=status)
        return clusters

    @handle_service_layer_errors("getting cluster")
    def get_cluster(self, cluster_id: str) -> ClusterWithNodes:
        cluster: Cluster = self.clusters_gateway.get(cluster_id=cluster_id)
        cluster_node_refs: List[NodeRef] = self.clusters_gateway.get_cluster_nodes(
            cluster_id=cluster_id
        )
        # TODO: Handle node loading issues
        loaded_nodes, _ = self._load_cluster_node_by_refs(
            cluster_node_refs=cluster_node_refs
        )
        return ClusterWithNodes(
            id=cluster.id,
            name=cluster.name,
            status=cluster.status,
            type=cluster.type,
            created_at=cluster.created_at,
            updated_at=cluster.updated_at,
            nodes=loaded_nodes,
        )

    @handle_service_layer_errors("deleting cluster")
    def delete_cluster(self, cluster_id: str) -> None:
        self.clusters_gateway.delete(cluster_id=cluster_id)

    def _get_unassigned_valid_nodes(self) -> List[UnassignedClusterNode]:
        """
        Gets all unassigned nodes that are available or discovering.
        """
        cluster_nodes: List[ClusterNode] = self.nodes_provider.list_nodes()
        return [
            cast(UnassignedClusterNode, cn)
            for cn in cluster_nodes
            if cn.status == ClusterNodeStatus.AVAILABLE
            or cn.status == ClusterNodeStatus.DISCOVERING
        ]

    def _validate_node_ids(
        self,
        node_ids: List[str],
        available_nodes_map: Dict[str, UnassignedClusterNode],
    ) -> Tuple[List[str], List[str], List[NodeValidationIssue]]:
        """
        Validates existence of node IDs and categorizes them.
        Returns:
            - valid_ready_ids: IDs of nodes that exist and are available/discovering.
            - nodes_to_poll: IDs of nodes that exist but are in DISCOVERING state.
            - issues: Validation issues for missing nodes or nodes in invalid states.
        """
        valid_ready_ids: List[str] = []
        nodes_to_poll: List[str] = []
        issues: List[NodeValidationIssue] = []

        for node_id in node_ids:
            if node_id not in available_nodes_map:
                issues.append(
                    NodeValidationIssue(
                        node_id=node_id,
                        node_spec_repr=node_id,
                        reason=f"Node {node_id} not found in available nodes",
                    )
                )
                continue

            node: UnassignedClusterNode = available_nodes_map[node_id]

            if node.status == ClusterNodeStatus.AVAILABLE:
                valid_ready_ids.append(node_id)
            elif node.status == ClusterNodeStatus.DISCOVERING:
                nodes_to_poll.append(node_id)

        return valid_ready_ids, nodes_to_poll, issues

    def _import_nodes_bulk(
        self,
        node_specs: List[NodeSpecification],
    ) -> Tuple[List[AssignedClusterNode], List[NodeValidationIssue]]:
        if not node_specs:
            return [], []

        # The provider handles bulk import and should return a result with successes and failures
        # Assuming import_nodes waits if wait_for_available=True
        import_result: ClusterNodesImportResult = self.nodes_provider.import_nodes(
            nodes_specs=node_specs, wait_for_available=True
        )

        valid_nodes: List[AssignedClusterNode] = []
        issues: List[NodeValidationIssue] = []

        for node in import_result.nodes:
            valid_nodes.append(node)

        for issue in import_result.issues:
            issues.append(
                NodeValidationIssue(
                    node_spec_repr=issue.node_spec_repr,
                    reason=issue.error_message,
                )
            )

        return valid_nodes, issues

    def _wait_for_nodes(
        self, node_ids: List[str]
    ) -> Tuple[List[str], List[NodeValidationIssue]]:
        if not node_ids:
            return [], []

        def fetch() -> List[ClusterNode]:
            return self.nodes_provider.list_nodes()

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
        issues: List[NodeValidationIssue] = []

        for nid in node_ids:
            if nid not in node_map:
                issues.append(
                    NodeValidationIssue(
                        node_id=nid, reason="Node not found after polling"
                    )
                )
                continue

            node = node_map[nid]
            if node.status == ClusterNodeStatus.AVAILABLE:
                ready_ids.append(nid)
            elif node.status == ClusterNodeStatus.DISCOVERING:
                issues.append(
                    NodeValidationIssue(
                        node_id=nid,
                        reason=f"Timed out waiting for node {nid} to become available. Node is still in DISCOVERING status.",
                    )
                )
            else:
                issues.append(
                    NodeValidationIssue(
                        node_id=nid,
                        reason=f"Node in invalid status after polling: {node.status}",
                    )
                )
        return ready_ids, issues

    @handle_service_layer_errors("deploying cluster")
    def deploy_cluster(
        self, create_params: ClusterDeployRequest
    ) -> DeployClusterResult:
        # List the available nodes that can be deployed to
        available_nodes: List[UnassignedClusterNode] = (
            self._get_unassigned_valid_nodes()
        )
        available_nodes_map: Dict[str, UnassignedClusterNode] = {
            node.id: node for node in available_nodes
        }

        # Separate IDs and Specs for Workers
        worker_ids_to_check: List[str] = [
            n for n in create_params.worker_nodes if isinstance(n, str)
        ]
        worker_specs_to_import: List[NodeSpecification] = [
            n for n in create_params.worker_nodes if isinstance(n, NodeSpecification)
        ]

        # Separate IDs and Specs for Control Plane
        cp_ids_to_check: List[str] = []
        cp_specs_to_import: List[NodeSpecification] = []
        if create_params.control_plane_nodes:
            cp_ids_to_check = [
                n for n in create_params.control_plane_nodes if isinstance(n, str)
            ]
            cp_specs_to_import = [
                n
                for n in create_params.control_plane_nodes
                if isinstance(n, NodeSpecification)
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
        all_issues: List[NodeValidationIssue] = (
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
            return DeployClusterResult(issues=all_issues)

        # Build the create parameters with only valid nodes
        create_parameters: ClusterCreateParameters = ClusterCreateParameters(
            name=create_params.name,
            type=create_params.type,
            vpn_cluster=create_params.enable_vpn,
            telemetry_enabled=create_params.enable_telemetry,
            labels=ClusterCreateParameters.get_labels(
                enable_multinode_training=create_params.enable_multinode_training
            ),
            colony_id=create_params.colony_id,
            to_be_deleted_at=create_params.to_be_deleted_at,
            worker_node_ids=final_worker_ids,
            control_plane_node_ids=final_cp_ids,
        )

        # Create the cluster
        cluster_id: str = self.clusters_gateway.create(parameters=create_parameters)

        # Deploy the cluster
        deployed_cluster_id: str = self.clusters_gateway.deploy(cluster_id)

        final_worker_nodes: List[AssignedClusterNode] = [
            AssignedClusterNode.from_unassigned_node(
                node=available_nodes_map[node_id], role=ClusterNodeRole.WORKER
            )
            for node_id in (valid_worker_ids + polled_ready_worker_ids)
        ]
        final_cp_nodes: List[AssignedClusterNode] = [
            AssignedClusterNode.from_unassigned_node(
                node=available_nodes_map[node_id], role=ClusterNodeRole.CONTROL_PLANE
            )
            for node_id in (valid_cp_ids + polled_ready_cp_ids)
        ]

        cluster: Cluster = self.get_cluster(cluster_id=deployed_cluster_id)
        cluster_with_nodes: ClusterWithNodes = ClusterWithNodes(
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
        return DeployClusterResult(cluster=cluster_with_nodes, issues=all_issues)

    def _validate_cluster_status(self, cluster: Cluster) -> None:
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

    def _load_cluster_node_by_refs(
        self, cluster_node_refs: List[NodeRef]
    ) -> Tuple[List[AssignedClusterNode], List[NodeLoadingIssue]]:
        if not cluster_node_refs:
            return [], []

        all_nodes: List[ClusterNode] = self.nodes_provider.list_nodes()
        all_nodes_map: Dict[str, ClusterNode] = {n.id: n for n in all_nodes}

        loaded_nodes: List[AssignedClusterNode] = []
        issues: List[NodeLoadingIssue] = []

        for ref in cluster_node_refs:
            if ref.id not in all_nodes_map:
                issues.append(
                    NodeLoadingIssue(
                        node_id=ref.id,
                        issue="Unexpected: Cluster node not found in nodes pool",
                    )
                )
                continue

            node = all_nodes_map[ref.id]
            loaded_nodes.append(
                AssignedClusterNode(
                    id=node.id,
                    hostname=node.hostname,
                    endpoint=node.endpoint,
                    username=node.username,
                    ssh_key_id=node.ssh_key_id,
                    status=node.status,
                    role=ref.role,
                )
            )

        return loaded_nodes, issues

    @handle_service_layer_errors("getting cluster nodes")
    def get_cluster_nodes(self, cluster_id: str) -> NodesLoadingResult:
        cluster: Cluster = self.get_cluster(cluster_id=cluster_id)
        self._validate_cluster_status(cluster=cluster)

        cluster_node_refs: List[NodeRef] = self.clusters_gateway.get_cluster_nodes(
            cluster_id=cluster_id
        )
        loaded_nodes, loading_issues = self._load_cluster_node_by_refs(
            cluster_node_refs=cluster_node_refs
        )
        return NodesLoadingResult(nodes=loaded_nodes, issues=loading_issues)

    @handle_service_layer_errors("adding cluster nodes")
    def add_nodes_to_cluster(
        self, request: AddNodesRequest
    ) -> List[AssignedClusterNode]:
        cluster: Cluster = self.get_cluster(cluster_id=request.cluster_id)
        self._validate_cluster_status(cluster=cluster)

        added_node_refs: List[NodeRef] = self.clusters_gateway.add_nodes_to_cluster(
            request=request
        )
        # For now we don't care about loading issues, we just want to get the nodes
        # TODO: Revisit this later
        loaded_nodes, _ = self._load_cluster_node_by_refs(
            cluster_node_refs=added_node_refs
        )
        return loaded_nodes

    @handle_service_layer_errors("removing nodes from cluster")
    def remove_nodes_from_cluster(
        self, cluster_id: str, node_ids: List[StrictStr]
    ) -> List[str]:
        self._validate_cluster_status(cluster=self.get_cluster(cluster_id=cluster_id))

        removed_node_ids: List[StrictStr] = (
            self.clusters_gateway.remove_nodes_from_cluster(
                cluster_id=cluster_id, node_ids=node_ids
            )
        )
        return removed_node_ids

    @handle_service_layer_errors("getting cluster resources")
    def get_cluster_resources(self, cluster_id: str) -> List[ClusterNodeResources]:
        self._validate_cluster_status(cluster=self.get_cluster(cluster_id=cluster_id))

        cluster_node_ref_resources: List[ClusterNodeRefResources] = (
            self.clusters_gateway.get_cluster_resources(cluster_id=cluster_id)
        )
        cluster_node_ref_resources_map: Dict[str, ClusterNodeRefResources] = {
            resource.node_id: resource for resource in cluster_node_ref_resources
        }

        cluster_node_refs: List[NodeRef] = self.clusters_gateway.get_cluster_nodes(
            cluster_id=cluster_id
        )

        loaded_nodes, _ = self._load_cluster_node_by_refs(
            cluster_node_refs=cluster_node_refs
        )
        loaded_nodes_map: Dict[str, AssignedClusterNode] = {
            node.id: node for node in loaded_nodes
        }

        cluster_node_resources: List[ClusterNodeResources] = []
        for node_id in cluster_node_ref_resources_map:
            cluster_node_resource: ClusterNodeRefResources = (
                cluster_node_ref_resources_map[node_id]
            )

            # This case should ideally never happen, but we handle it
            # since there were some issues with node IDs in the past
            # Nodes ids from loaded resources should always be in the node pool
            cluster_node: Union[AssignedClusterNode, StrictStr] = node_id
            if node_id in loaded_nodes_map:
                cluster_node = loaded_nodes_map[node_id]
            else:
                cluster_node = node_id
                logger.warning(
                    f"Node ID '{node_id}' not found in node pool. Node name is set to Unknown."
                )

            cluster_node_resources.append(
                ClusterNodeResources(
                    cluster_node=cluster_node,
                    free_resources=cluster_node_resource.free_resources,
                    occupied_resources=cluster_node_resource.occupied_resources,
                )
            )
        return cluster_node_resources

    @handle_service_layer_errors("importing kubeconfig")
    def import_kubeconfig(
        self,
        cluster_id: str,
        kubeconfig_file_path: str = Path.home().joinpath(".kube", "config").as_posix(),
    ) -> None:
        # self._validate_cluster_status(cluster=self.get_cluster(cluster_id=cluster_id))

        kubeconfig_content: str = self.clusters_gateway.get_kubeconfig(
            cluster_id=cluster_id
        )
        self.file_write_gateway.write_file(
            file_path=Path(kubeconfig_file_path), content=kubeconfig_content
        )

    @handle_service_layer_errors("getting dashboard url")
    def get_dashboard_url(self, cluster_id: str) -> str:
        self._validate_cluster_status(cluster=self.get_cluster(cluster_id=cluster_id))

        return self.clusters_gateway.get_dashboard_url(cluster_id=cluster_id)

    @handle_service_layer_errors("getting deployable nodes")
    def get_deployable_nodes(self) -> List[UnassignedClusterNode]:
        deployable_nodes: List[UnassignedClusterNode] = (
            self._get_unassigned_valid_nodes()
        )
        return deployable_nodes
