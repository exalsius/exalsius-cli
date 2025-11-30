from typing import Dict, List

from exls.clusters.core.domain import (
    AssignedClusterNode,
    ClusterNode,
    ClusterNodeStatus,
)
from exls.clusters.core.ports.provider import (
    ClusterNodeImportIssue,
    ClusterNodesImportResult,
    INodesProvider,
)
from exls.clusters.core.requests import NodeSpecification
from exls.nodes.core.domain import (
    BaseNode,
    SelfManagedNode,
)
from exls.nodes.core.requests import SelfManagedNodesImportResult
from exls.nodes.core.service import NodesService


class NodesDomainProvider(INodesProvider):
    def __init__(self, nodes_service: NodesService):
        self.nodes_service: NodesService = nodes_service

    def list_nodes(self) -> List[ClusterNode]:
        domain_nodes: List[BaseNode] = self.nodes_service.list_nodes()
        nodes: List[ClusterNode] = []
        for node in domain_nodes:
            if isinstance(node, SelfManagedNode):
                nodes.append(
                    ClusterNode(
                        id=node.id,
                        hostname=node.hostname,
                        username=node.username,
                        ssh_key_id=node.ssh_key_id,
                        status=ClusterNodeStatus.from_str(node.status.value),
                    )
                )
        return nodes

    def import_nodes(
        self, nodes_specs: List[NodeSpecification], wait_for_available: bool = False
    ) -> ClusterNodesImportResult:
        import_results: SelfManagedNodesImportResult = (
            self.nodes_service.import_selfmanaged_nodes(nodes_specs, wait_for_available)
        )
        nodes_specs_map: Dict[str, NodeSpecification] = {
            node.hostname: node for node in nodes_specs
        }

        nodes: List[AssignedClusterNode] = []
        for node in import_results.nodes:
            nodes.append(
                AssignedClusterNode(
                    id=node.id,
                    hostname=node.hostname,
                    endpoint=node.endpoint,
                    username=node.username,
                    ssh_key_id=node.ssh_key_id,
                    status=ClusterNodeStatus.from_str(node.status.value),
                    role=nodes_specs_map[node.hostname].role,
                )
            )

        issues: List[ClusterNodeImportIssue] = [
            ClusterNodeImportIssue(
                node_spec_repr=str(failure.node),
                error_message=f"{failure.message}: {failure.error}",
            )
            for failure in import_results.failures
        ]

        return ClusterNodesImportResult(
            nodes=nodes,
            issues=issues,
        )
