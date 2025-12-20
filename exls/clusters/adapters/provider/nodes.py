from typing import Dict, List

from exls.clusters.core.domain import (
    ClusterNode,
    ClusterNodeResources,
    ClusterNodeRole,
    ClusterNodeStatus,
)
from exls.clusters.core.ports.provider import (
    ClusterNodeData,
    ClusterNodeImportIssue,
    ClusterNodesImportResult,
    NodesProvider,
)
from exls.clusters.core.requests import ClusterNodeSpecification
from exls.nodes.core.domain import (
    BaseNode,
    NodeResources,
    SelfManagedNode,
)
from exls.nodes.core.results import ImportSelfmanagedNodesResult
from exls.nodes.core.service import NodesService


def _map_resources(resources: NodeResources) -> ClusterNodeResources:
    return ClusterNodeResources(
        gpu_type=resources.gpu_type,
        gpu_vendor=resources.gpu_vendor,
        gpu_count=resources.gpu_count,
        cpu_cores=resources.cpu_cores,
        memory_gb=resources.memory_gb,
        storage_gb=resources.storage_gb,
    )


def _get_empty_resources(resources: ClusterNodeResources) -> ClusterNodeResources:
    return ClusterNodeResources(
        gpu_type=resources.gpu_type,
        gpu_vendor=resources.gpu_vendor,
        gpu_count=0,
        cpu_cores=0,
        memory_gb=0,
        storage_gb=0,
    )


class NodesDomainProvider(NodesProvider):
    def __init__(self, nodes_service: NodesService):
        self.nodes_service: NodesService = nodes_service

    def list_nodes(self) -> List[ClusterNodeData]:
        domain_nodes: List[BaseNode] = self.nodes_service.list_nodes()
        nodes: List[ClusterNodeData] = []
        for node in domain_nodes:
            if isinstance(node, SelfManagedNode):
                nodes.append(
                    ClusterNodeData(
                        id=node.id,
                        hostname=node.hostname,
                        username=node.username,
                        ssh_key_id=node.ssh_key_id,
                        status=node.status.value,
                        endpoint=node.endpoint,
                        resources=_map_resources(node.resources),
                    )
                )
        return nodes

    def list_available_nodes(self) -> List[ClusterNode]:
        node_data_list: List[ClusterNodeData] = self.list_nodes()
        return [
            ClusterNode(
                id=node.id,
                hostname=node.hostname,
                username=node.username,
                ssh_key_id=node.ssh_key_id,
                status=ClusterNodeStatus.from_str(node.status),
                endpoint=node.endpoint or "",
                role=ClusterNodeRole.UNASSIGNED,
                free_resources=node.resources,
                occupied_resources=_get_empty_resources(node.resources),
            )
            for node in node_data_list
        ]

    def import_nodes(
        self,
        nodes_specs: List[ClusterNodeSpecification],
        wait_for_available: bool = False,
    ) -> ClusterNodesImportResult:
        import_results: ImportSelfmanagedNodesResult = (
            self.nodes_service.import_selfmanaged_nodes(nodes_specs, wait_for_available)
        )
        nodes_specs_map: Dict[str, ClusterNodeSpecification] = {
            node.hostname: node for node in nodes_specs
        }

        nodes: List[ClusterNode] = []
        for node in import_results.imported_nodes:
            nodes.append(
                ClusterNode(
                    id=node.id,
                    hostname=node.hostname,
                    username=node.username,
                    ssh_key_id=node.ssh_key_id,
                    status=ClusterNodeStatus.from_str(node.status.value),
                    endpoint=node.endpoint or "",
                    free_resources=_map_resources(node.resources),
                    occupied_resources=_get_empty_resources(
                        _map_resources(node.resources)
                    ),
                    role=ClusterNodeRole.UNASSIGNED,
                )
            )

        issues: List[ClusterNodeImportIssue] = [
            ClusterNodeImportIssue(
                node_specification=nodes_specs_map[issue.node_import_request.hostname],
                error_message=f"{issue.error_message}",
            )
            for issue in import_results.issues
        ]

        return ClusterNodesImportResult(
            nodes=nodes,
            issues=issues,
        )
