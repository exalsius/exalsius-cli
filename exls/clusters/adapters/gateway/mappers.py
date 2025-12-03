import logging
from typing import List, Optional

from exalsius_api_client.models.cluster import Cluster as SdkCluster
from exalsius_api_client.models.cluster_resources_list_response_resources_inner import (
    ClusterResourcesListResponseResourcesInner,
)

from exls.clusters.core.domain import (
    Cluster,
    ClusterNodeRole,
    ClusterStatus,
    ClusterType,
    Resources,
)
from exls.clusters.core.ports.gateway import ClusterNodeRefResources
from exls.clusters.core.requests import NodeRef

logger = logging.getLogger(__name__)


def cluster_from_sdk_model(sdk_model: SdkCluster) -> Cluster:
    return Cluster(
        id=sdk_model.id or "",
        name=sdk_model.name,
        status=ClusterStatus.from_str(sdk_model.cluster_status),
        type=ClusterType.from_str(sdk_model.cluster_type or ""),
        created_at=sdk_model.created_at,
        updated_at=sdk_model.updated_at,
    )


def cluster_node_ref_from_node_ids(
    control_plane_node_ids: List[str], worker_node_ids: List[str]
) -> List[NodeRef]:
    return [
        NodeRef(id=node_id, role=ClusterNodeRole.CONTROL_PLANE)
        for node_id in control_plane_node_ids
    ] + [
        NodeRef(id=node_id, role=ClusterNodeRole.WORKER) for node_id in worker_node_ids
    ]


def resources_from_sdk_model(
    sdk_model: ClusterResourcesListResponseResourcesInner,
) -> Optional[ClusterNodeRefResources]:
    if sdk_model.node_id is None:
        logger.warning("Node ID is None for cluster node resources")
        return None
    if sdk_model.available is None:
        logger.warning(
            f"Available resources are None for cluster node {sdk_model.node_id}"
        )
        return None
    if sdk_model.occupied is None:
        logger.warning(
            f"Occupied resources are None for cluster node {sdk_model.node_id}"
        )
        return None

    available_resources: Resources = Resources(
        gpu_type=sdk_model.available.gpu_type or "",
        gpu_vendor=sdk_model.available.gpu_vendor or "",
        gpu_count=sdk_model.available.gpu_count or 0,
        cpu_cores=sdk_model.available.cpu_cores or 0,
        memory_gb=sdk_model.available.memory_gb or 0,
        storage_gb=sdk_model.available.storage_gb or 0,
    )
    occupied_resources: Resources = Resources(
        gpu_type=sdk_model.occupied.gpu_type or "",
        gpu_vendor=sdk_model.occupied.gpu_vendor or "",
        gpu_count=sdk_model.occupied.gpu_count or 0,
        cpu_cores=sdk_model.occupied.cpu_cores or 0,
        memory_gb=sdk_model.occupied.memory_gb or 0,
        storage_gb=sdk_model.occupied.storage_gb or 0,
    )
    return ClusterNodeRefResources(
        node_id=sdk_model.node_id,
        free_resources=available_resources,
        occupied_resources=occupied_resources,
    )
