from pathlib import Path
from typing import Dict, List, Optional, cast

from exls.nodes.core.domain import (
    BaseNode,
    CloudNode,
    NodeStatus,
    SelfManagedNode,
)
from exls.nodes.core.ports.operations import (
    ImportSelfmanagedNodeParameters,
    NodesOperations,
)
from exls.nodes.core.ports.provider import NodeSshKey, SshKeyProvider
from exls.nodes.core.ports.repository import NodesRepository
from exls.nodes.core.requests import (
    ImportCloudNodeRequest,
    ImportSelfmanagedNodeRequest,
    NodesFilterCriteria,
    NodesSshKeySpecification,
)
from exls.nodes.core.results import (
    DeleteNodeIssue,
    DeleteNodesResult,
    ImportSelfmanagedNodeIssue,
    ImportSelfmanagedNodesResult,
)
from exls.shared.core.decorators import handle_service_layer_errors
from exls.shared.core.exceptions import ServiceError
from exls.shared.core.parallel import ParallelExecutionResult, execute_in_parallel
from exls.shared.core.polling import poll_until


class NodesService:
    def __init__(
        self,
        nodes_repository: NodesRepository,
        nodes_operations: NodesOperations,
        ssh_key_provider: SshKeyProvider,
    ):
        self._nodes_repository: NodesRepository = nodes_repository
        self._nodes_operations: NodesOperations = nodes_operations
        self._ssh_key_provider: SshKeyProvider = ssh_key_provider

    # This should be rather done by an adapter layer but since it's
    # rather simple logic, we keep it here for now.
    def _resolve_ssh_key_name(self, nodes: List[BaseNode]) -> List[BaseNode]:
        for node in nodes:
            if isinstance(node, SelfManagedNode):
                ssh_key_map: Dict[str, NodeSshKey] = {
                    k.id: k for k in self._ssh_key_provider.list_keys()
                }
                if node.ssh_key_id in ssh_key_map:
                    node.ssh_key_name = ssh_key_map[node.ssh_key_id].name
        return nodes

    @handle_service_layer_errors("listing nodes")
    def list_nodes(
        self, filter: Optional[NodesFilterCriteria] = None
    ) -> List[BaseNode]:
        nodes: List[BaseNode] = self._nodes_repository.list(filter=filter)
        return self._resolve_ssh_key_name(nodes)

    @handle_service_layer_errors("getting node")
    def get_node(self, node_id: str) -> BaseNode:
        node: BaseNode = self._nodes_repository.get(node_id)
        return self._resolve_ssh_key_name([node])[0]

    @handle_service_layer_errors("deleting node")
    def delete_nodes(self, node_ids: List[str]) -> DeleteNodesResult:
        results: ParallelExecutionResult[str, str] = execute_in_parallel(
            items=node_ids,
            func=lambda node_id: self._nodes_repository.delete(node_id),
            max_workers=max(10, len(node_ids)),
        )

        all_failures = [
            DeleteNodeIssue(
                node_id=failure.item,
                error_message=failure.message,
            )
            for failure in results.failures
        ]
        return DeleteNodesResult(
            deleted_node_ids=results.successes,
            issues=all_failures,
        )

    def _wait_for_node_status(
        self, node_id: str, target_status: NodeStatus, timeout_seconds: int = 120
    ) -> BaseNode:
        """
        Waits for a node to reach a specific status.
        """

        def _fetch_node() -> BaseNode:
            return self.get_node(node_id)

        def _is_status_reached(node: BaseNode) -> bool:
            # You might want to handle failure states here too
            if node.status == NodeStatus.FAILED:
                raise ServiceError(
                    message=f"Node import of {node.hostname} failed with status: {node.status}"
                )
            return node.status == target_status

        return poll_until(
            fetcher=_fetch_node,
            predicate=_is_status_reached,
            timeout_seconds=timeout_seconds,
            interval_seconds=5,
            error_message=f"Node {node_id} did not reach status {target_status} within {timeout_seconds}s",
        )

    @handle_service_layer_errors("importing self-managed nodes")
    def import_selfmanaged_nodes(
        self,
        node_import_requests: List[ImportSelfmanagedNodeRequest],
        wait_for_available: bool = False,
    ) -> ImportSelfmanagedNodesResult:
        # Check that the import requests are valid
        if len(node_import_requests) == 0:
            raise ServiceError(
                message="Self-managed import request must contain at least one node to import"
            )

        # 1. Prepare parameters (Handle SSH keys, deduplication, and validation)
        import_parameters, pre_flight_failures = self._prepare_import_parameters(
            node_import_requests
        )

        # 2. Execute Node Imports in Parallel
        results: ParallelExecutionResult[
            ImportSelfmanagedNodeParameters, SelfManagedNode
        ] = execute_in_parallel(
            items=import_parameters,
            func=lambda p: self._import_single_node(p, wait_for_available),
            max_workers=10,
        )

        # 3. Combine Results
        all_failures = pre_flight_failures + [
            ImportSelfmanagedNodeIssue(
                node_import_request=ImportSelfmanagedNodeParameters.to_request(
                    failure.item
                ),
                error_message=failure.message,
            )
            for failure in results.failures
        ]

        return ImportSelfmanagedNodesResult(
            imported_nodes=results.successes,
            issues=all_failures,
        )

    def _prepare_import_parameters(
        self, requests: List[ImportSelfmanagedNodeRequest]
    ) -> tuple[List[ImportSelfmanagedNodeParameters], List[ImportSelfmanagedNodeIssue]]:
        """Resolves SSH keys and builds valid import parameters."""

        # Load all available SSH keys
        ssh_keys: List[NodeSshKey] = self._ssh_key_provider.list_keys()

        # Map: Key Name -> NodeSshKey (for quick lookup of existing keys by name)
        # Assuming key names are unique
        ssh_key_map: Dict[str, NodeSshKey] = {k.id: k for k in ssh_keys}
        ssh_key_name_map: Dict[str, NodeSshKey] = {k.name: k for k in ssh_keys}

        # Deduplicate new keys to import
        keys_to_import_map: Dict[str, NodesSshKeySpecification] = {}
        for req in requests:
            if not isinstance(req.ssh_key, str):
                # Only add if we don't already have a key with this name in the system
                if req.ssh_key.name not in ssh_key_name_map:
                    keys_to_import_map[req.ssh_key.name] = req.ssh_key

        def _import_single_ssh_key(spec: NodesSshKeySpecification) -> NodeSshKey:
            return self._import_ssh_key(spec.name, spec.key_path)

        # Import new keys in parallel
        ssh_key_import_results: ParallelExecutionResult[
            NodesSshKeySpecification, NodeSshKey
        ] = execute_in_parallel(
            items=list(keys_to_import_map.values()),
            func=_import_single_ssh_key,
            max_workers=10,
        )

        # Process SSH key import results
        for success_key in ssh_key_import_results.successes:
            ssh_key_map[success_key.id] = success_key
            ssh_key_name_map[success_key.name] = success_key

        ssh_key_failures: Dict[str, str] = {
            failure.item.name: failure.message
            for failure in ssh_key_import_results.failures
        }

        # Build node import parameters
        import_parameters: List[ImportSelfmanagedNodeParameters] = []
        pre_flight_failures: List[ImportSelfmanagedNodeIssue] = []

        for node_import_request in requests:
            ssh_key_id: str
            if isinstance(node_import_request.ssh_key, str):
                # ID provided directly
                if node_import_request.ssh_key not in ssh_key_map:
                    pre_flight_failures.append(
                        ImportSelfmanagedNodeIssue(
                            node_import_request=node_import_request,
                            error_message=f"SSH key with ID {node_import_request.ssh_key} not found",
                        )
                    )
                    continue
                ssh_key_id = node_import_request.ssh_key
            else:
                # Key specification provided
                if node_import_request.ssh_key.name in ssh_key_failures:
                    # Propagate key import failure
                    error_msg = ssh_key_failures[node_import_request.ssh_key.name]
                    pre_flight_failures.append(
                        ImportSelfmanagedNodeIssue(
                            node_import_request=node_import_request,
                            error_message=f"Failed to import SSH key {node_import_request.ssh_key.name}: {error_msg}",
                        )
                    )
                    continue
                elif node_import_request.ssh_key.name in ssh_key_name_map:
                    ssh_key_id = ssh_key_name_map[node_import_request.ssh_key.name].id
                else:
                    # Should not happen if previoud ssh key import was successful
                    # or if the key import failed
                    pre_flight_failures.append(
                        ImportSelfmanagedNodeIssue(
                            node_import_request=node_import_request,
                            error_message=f"Failed to resolve SSH key {node_import_request.ssh_key.name}",
                        )
                    )
                    continue

            import_parameters.append(
                ImportSelfmanagedNodeParameters(
                    hostname=node_import_request.hostname,
                    endpoint=node_import_request.endpoint,
                    username=node_import_request.username,
                    ssh_key_id=ssh_key_id,
                )
            )

        return import_parameters, pre_flight_failures

    def _import_single_node(
        self, params: ImportSelfmanagedNodeParameters, wait: bool
    ) -> SelfManagedNode:
        """Imports a single node and optionally waits for it."""
        node_id: str = self._nodes_operations.import_selfmanaged_node(parameters=params)
        # wait_for_node_status returns the updated node
        result_node: BaseNode
        if wait:
            result_node = self._wait_for_node_status(
                node_id=node_id, target_status=NodeStatus.DEPLOYED
            )
        else:
            result_node = self.get_node(node_id)

        # Runtime check to satisfy strict typing
        if not isinstance(result_node, SelfManagedNode):
            # This might imply an infrastructure data corruption or bad mapping
            raise ServiceError(
                f"Imported node {node_id} returned unexpected type: {type(result_node)}"
            )

        return result_node

    def _import_ssh_key(self, name: str, key_path: Path) -> NodeSshKey:
        # Forward the request to the SSH key provider
        return self._ssh_key_provider.import_key(name=name, key_path=key_path)

    @handle_service_layer_errors("listing ssh keys")
    def list_ssh_keys(self) -> List[NodeSshKey]:
        return self._ssh_key_provider.list_keys()

    @handle_service_layer_errors("importing cloud nodes")
    def import_cloud_nodes(self, request: ImportCloudNodeRequest) -> List[CloudNode]:
        node_ids: List[str] = self._nodes_operations.import_cloud_nodes(
            parameters=request
        )
        nodes: List[CloudNode] = [
            cast(CloudNode, self._nodes_repository.get(node_id)) for node_id in node_ids
        ]
        return nodes
