from exls.clusters.adapters.dtos import (
    ClusterDTO,
    ClusterNodeResourcesDTO,
    ResourcesDTO,
)
from exls.clusters.core.domain import Cluster, ClusterNodeRefResources


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


def cluster_node_resources_dto_from_domain(
    domain: ClusterNodeRefResources,
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
    return ClusterNodeResourcesDTO(
        node_id=domain.node_id,
        free_resources=free_resources,
        occupied_resources=occupied_resources,
    )
