from pathlib import Path
from typing import Dict, List, Optional, Tuple

from exls.clusters.core.domain import (
    Cluster,
    ClusterNodeRefResources,
    ClusterNodeResources,
    ClustersNode,
    ClusterStatus,
    DeployClusterResult,
    NodesLoadingIssue,
    NodesLoadingResult,
    NodeStatus,
    NodeValidationIssue,
)
from exls.clusters.core.ports.gateway import ClusterCreateParameters, IClustersGateway
from exls.clusters.core.ports.provider import ClusterNodeProviderNode, INodesProvider
from exls.clusters.core.requests import (
    AddNodesRequest,
    ClusterDeployRequest,
    NodeRef,
    NodeSpecification,
    RemoveNodesRequest,
)
from exls.shared.adapters.decorators import handle_service_layer_errors
from exls.shared.adapters.gateway.file.gateways import IFileWriteGateway
from exls.shared.core.parallel import ParallelExecutionResult, execute_in_parallel
from exls.shared.core.polling import poll_until
from exls.shared.core.service import ServiceError


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
    def get_cluster(self, cluster_id: str) -> Cluster:
        return self.clusters_gateway.get(cluster_id=cluster_id)

    @handle_service_layer_errors("deleting cluster")
    def delete_cluster(self, cluster_id: str) -> None:
        self.clusters_gateway.delete(cluster_id=cluster_id)

    def _validate_node_ids(
        self,
        node_ids: List[str],
        available_nodes_map: Dict[str, ClusterNodeProviderNode],
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
                    NodeValidationIssue(node_id=node_id, reason="Node not found")
                )
                continue

            node: ClusterNodeProviderNode = available_nodes_map[node_id]

            if node.status == NodeStatus.AVAILABLE:
                valid_ready_ids.append(node_id)
            elif node.status == NodeStatus.DISCOVERING:
                nodes_to_poll.append(node_id)
            else:
                issues.append(
                    NodeValidationIssue(
                        node_id=node_id,
                        node_spec_repr=str(node),
                        reason=f"Invalid status: {node.status}",
                    )
                )

        return valid_ready_ids, nodes_to_poll, issues

    def _import_nodes_bulk(
        self,
        node_specs: List[NodeSpecification],
    ) -> Tuple[List[str], List[NodeValidationIssue]]:
        if not node_specs:
            return [], []

        # The provider handles bulk import and should return a result with successes and failures
        # Assuming import_nodes waits if wait_for_available=True
        import_result = self.nodes_provider.import_nodes(
            requests=node_specs, wait_for_available=True
        )

        valid_ids: List[str] = []
        imported_nodes_map: Dict[str, ClustersNode] = {}
        issues: List[NodeValidationIssue] = []

        for node in import_result.nodes:
            valid_ids.append(node.id)
            imported_nodes_map[node.id] = node

        for issue in import_result.issues:
            issues.append(
                NodeValidationIssue(
                    node_spec_repr=issue.node_spec_repr,
                    reason=issue.error_message,
                )
            )

        return valid_ids, issues

    def _poll_node(self, node_id: str) -> ClusterNodeProviderNode:
        def fetcher() -> ClusterNodeProviderNode:
            return self.nodes_provider.get_node(node_id)

        def predicate(node: ClusterNodeProviderNode) -> bool:
            if node.status == NodeStatus.AVAILABLE:
                return True
            elif node.status == NodeStatus.DISCOVERING:
                return False
            else:
                # Raising exception here to stop polling and report failure
                raise ValueError(f"Node became invalid: {node.status}")

        try:
            return poll_until(
                fetcher=fetcher,
                predicate=predicate,
                timeout_seconds=60,
                interval_seconds=3,
                error_message=f"Timed out waiting for node {node_id} to become available",
            )
        except Exception:
            raise

    @handle_service_layer_errors("deploying cluster")
    def deploy_cluster(
        self, create_params: ClusterDeployRequest
    ) -> DeployClusterResult:
        # List the available nodes
        available_nodes: List[ClusterNodeProviderNode] = (
            self.nodes_provider.list_nodes()
        )
        available_nodes_map: Dict[str, ClusterNodeProviderNode] = {
            node.id: node for node in available_nodes
        }

        # Separate IDs and Specs for Workers
        worker_ids_to_check: List[str] = [
            n for n in create_params.worker_nodes if isinstance(n, str)
        ]
        worker_specs_to_import: List[NodeSpecification] = [
            n for n in create_params.worker_nodes if not isinstance(n, str)
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
        # We can combine worker and CP imports into one call but it's easier to track which
        # role they belong to unless we track indices.
        imported_worker_ids, worker_import_issues = self._import_nodes_bulk(
            worker_specs_to_import
        )
        imported_cp_ids, cp_import_issues = self._import_nodes_bulk(cp_specs_to_import)

        # Combine all validated/imported IDs
        final_worker_ids = valid_worker_ids + imported_worker_ids
        final_cp_ids = valid_cp_ids + imported_cp_ids

        # Combine all issues
        all_issues: List[NodeValidationIssue] = (
            worker_id_issues + worker_import_issues + cp_id_issues + cp_import_issues
        )

        # Combine nodes that need polling from existing validation
        # Dedup to avoid polling the same node multiple times if it appears in both lists or multiple times
        # since a node can be a worker and a control plane node
        existing_nodes_to_poll: List[str] = list(set(worker_poll_ids + cp_poll_ids))

        # Poll for existing nodes that are DISCOVERING
        if existing_nodes_to_poll:
            execution_result: ParallelExecutionResult[str, ClusterNodeProviderNode] = (
                execute_in_parallel(items=existing_nodes_to_poll, func=self._poll_node)
            )
            for failure in execution_result.failures:
                all_issues.append(
                    NodeValidationIssue(
                        node_id=failure.item,
                        node_spec_repr=str(available_nodes_map[failure.item]),
                        reason=f"Polling for status of node {failure.item} failed: {failure.message}",
                    )
                )

            for node in execution_result.successes:
                # A node can be a worker and a control plane node, so we add it to both lists
                if node.id in worker_poll_ids:
                    final_worker_ids.append(node.id)
                if node.id in cp_poll_ids:
                    final_cp_ids.append(node.id)

        # Check if we have any valid nodes left to deploy
        if not final_worker_ids and not final_cp_ids:
            return DeployClusterResult(issues=all_issues)

        # Build the create parameters with only valid nodes
        create_parameters: ClusterCreateParameters = ClusterCreateParameters(
            name=create_params.name,
            type=create_params.type,
            labels=create_params.labels,
            colony_id=create_params.colony_id,
            to_be_deleted_at=create_params.to_be_deleted_at,
            worker_node_ids=final_worker_ids,
            control_plane_node_ids=final_cp_ids,
        )

        # Create the cluster
        cluster_id: str = self.clusters_gateway.create(parameters=create_parameters)

        # Deploy the cluster
        deployed_cluster_id: str = self.clusters_gateway.deploy(cluster_id)

        cluster: Cluster = self.get_cluster(cluster_id=deployed_cluster_id)

        # Return result with any issues encountered during the process
        return DeployClusterResult(cluster=cluster, issues=all_issues)

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

    def _import_single_node(self, node_ref: NodeRef) -> ClustersNode:
        cluster_node: ClusterNodeProviderNode = self.nodes_provider.get_node(
            node_id=node_ref.id
        )
        return ClustersNode(
            id=cluster_node.id,
            hostname=cluster_node.hostname,
            endpoint=cluster_node.endpoint,
            username=cluster_node.username,
            ssh_key=cluster_node.ssh_key,
            status=cluster_node.status,
            role=node_ref.role,
        )

    def _load_cluster_node_by_refs(
        self, cluster_node_refs: List[NodeRef]
    ) -> Tuple[List[ClustersNode], List[NodesLoadingIssue]]:
        # Execute Node Imports in Parallel
        results: ParallelExecutionResult[NodeRef, ClustersNode] = execute_in_parallel(
            items=cluster_node_refs,
            func=self._import_single_node,
            max_workers=10,
        )

        return results.successes, [
            NodesLoadingIssue(node_id=failure.item.id, reason=str(failure.error))
            for failure in results.failures
        ]

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
    def add_nodes_to_cluster(self, request: AddNodesRequest) -> List[ClustersNode]:
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
    def remove_nodes_from_cluster(self, request: RemoveNodesRequest) -> List[str]:
        self._validate_cluster_status(
            cluster=self.get_cluster(cluster_id=request.cluster_id)
        )

        removed_node_ids: List[str] = self.clusters_gateway.remove_nodes_from_cluster(
            request=request
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
        loaded_nodes_map: Dict[str, ClustersNode] = {
            node.id: node for node in loaded_nodes
        }

        cluster_node_resources: List[ClusterNodeResources] = []
        for node_id in cluster_node_ref_resources_map:
            cluster_node_resource: ClusterNodeRefResources = (
                cluster_node_ref_resources_map[node_id]
            )
            cluster_node_resources.append(
                ClusterNodeResources(
                    node_id=node_id,
                    hostname=loaded_nodes_map[node_id].hostname,
                    endpoint=loaded_nodes_map[node_id].endpoint,
                    username=loaded_nodes_map[node_id].username,
                    ssh_key=loaded_nodes_map[node_id].ssh_key,
                    status=loaded_nodes_map[node_id].status,
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
        self._validate_cluster_status(cluster=self.get_cluster(cluster_id=cluster_id))

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
