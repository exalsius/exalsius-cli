from typing import List

from pydantic import StrictStr

from exls.clusters.adapters.ui.dtos import (
    ClusterDTO,
    ClusterNodeDTO,
    ClusterNodeResourcesDTO,
    ClusterWithNodesDTO,
    NodeValidationIssueDTO,
    ResourcesDTO,
)
from exls.clusters.core.domain import (
    Cluster,
    ClusterNode,
    ClusterNodeRole,
)
from exls.clusters.core.results import ClusterNodeIssue


def cluster_dto_from_domain(domain: Cluster) -> ClusterDTO:
    """Helper function to convert a cluster domain to a DTO cluster."""
    return ClusterDTO(
        id=domain.id,
        name=domain.name,
        status=domain.status.value,
        type=domain.type.value,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
    )


def cluster_with_nodes_dto_from_domain(domain: Cluster) -> ClusterWithNodesDTO:
    worker_nodes: List[ClusterNodeDTO] = [
        cluster_node_dto_from_domain(node, domain.name)
        for node in domain.nodes
        if node.role == ClusterNodeRole.WORKER
    ]
    control_plane_nodes: List[ClusterNodeDTO] = [
        cluster_node_dto_from_domain(node, domain.name)
        for node in domain.nodes
        if node.role == ClusterNodeRole.CONTROL_PLANE
    ]
    return ClusterWithNodesDTO(
        id=domain.id,
        name=domain.name,
        status=domain.status.value,
        type=domain.type.value,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        worker_nodes=worker_nodes,
        control_plane_nodes=control_plane_nodes,
    )


def node_validation_issue_dto_from_domain(
    domain: ClusterNodeIssue,
) -> NodeValidationIssueDTO:
    return NodeValidationIssueDTO(
        node_id=domain.node.id if domain.node else None,
        node_name=domain.node.hostname if domain.node else None,
        error_message=domain.error_message,
    )


def cluster_node_dto_from_domain(
    domain: ClusterNode, cluster_name: StrictStr
) -> ClusterNodeDTO:
    return ClusterNodeDTO(
        id=domain.id,
        role=domain.role.value,
        hostname=domain.hostname,
        status=domain.status.value,
        cluster_name=cluster_name,
    )


def cluster_node_resources_dto_from_domain(
    domain: ClusterNode, cluster_name: StrictStr
) -> ClusterNodeResourcesDTO:
    free_resources: ResourcesDTO = ResourcesDTO(
        gpu_type=domain.free_resources.gpu_type,
        gpu_vendor=domain.free_resources.gpu_vendor,
        gpu_count=domain.free_resources.gpu_count,
        cpu_cores=domain.free_resources.cpu_cores,
        memory_gb=domain.free_resources.memory_gb,
        storage_gb=domain.free_resources.storage_gb,
    )
    occupied_resources: ResourcesDTO = ResourcesDTO(
        gpu_type=domain.occupied_resources.gpu_type,
        gpu_vendor=domain.occupied_resources.gpu_vendor,
        gpu_count=domain.occupied_resources.gpu_count,
        cpu_cores=domain.occupied_resources.cpu_cores,
        memory_gb=domain.occupied_resources.memory_gb,
        storage_gb=domain.occupied_resources.storage_gb,
    )
    cluster_node: ClusterNodeDTO = ClusterNodeDTO(
        id=domain.id,
        role=domain.role.value,
        hostname=domain.hostname,
        status=domain.status.value,
        cluster_name=cluster_name,
    )
    return ClusterNodeResourcesDTO(
        cluster_node=cluster_node,
        free_resources=free_resources,
        occupied_resources=occupied_resources,
    )
