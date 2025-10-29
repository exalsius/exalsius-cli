from typing import Dict, List

from exls.clusters.dtos import (
    AddNodesRequestDTO,
    AllowedClusterNodeRoleDTO,
    DeployClusterRequestDTO,
    ListClustersRequestDTO,
)
from exls.clusters.gateway.dtos import (
    AddNodesParams,
    ClusterCreateParams,
    ClusterFilterParams,
    ClusterLabels,
    ClusterLabelValuesGPUType,
    ClusterLabelValuesWorkloadType,
    NodeToAddParams,
)


def cluster_list_filter_params_from_request_dto(
    request_dto: ListClustersRequestDTO,
) -> ClusterFilterParams:
    if request_dto.status is None:
        return ClusterFilterParams(
            status=None,
        )
    else:
        return ClusterFilterParams(
            status=request_dto.status.upper(),
        )


def cluster_create_params_from_request_dto(
    request_dto: DeployClusterRequestDTO,
) -> ClusterCreateParams:
    gpu_type_enum: ClusterLabelValuesGPUType = ClusterLabelValuesGPUType(
        request_dto.gpu_type
    )
    cluster_labels: Dict[str, str] = {}
    if gpu_type_enum != ClusterLabelValuesGPUType.NO_GPU:
        cluster_labels[ClusterLabels.GPU_TYPE] = gpu_type_enum.value
    if request_dto.diloco:
        cluster_labels[ClusterLabels.WORKLOAD_TYPE] = (
            ClusterLabelValuesWorkloadType.VOLCANO
        )
    if request_dto.telemetry_enabled:
        cluster_labels[ClusterLabels.TELEMETRY_TYPE] = "true"
    return ClusterCreateParams(
        name=request_dto.name,
        cluster_type=request_dto.cluster_type.value.upper(),
        cluster_labels=cluster_labels,
    )


def cluster_add_nodes_params_from_add_nodes_request_dto(
    request_dto: AddNodesRequestDTO,
) -> AddNodesParams:
    nodes_to_add: List[NodeToAddParams] = [
        NodeToAddParams(node_id=node_id, node_role=request_dto.node_role.value.upper())
        for node_id in request_dto.node_ids
    ]
    return AddNodesParams(
        cluster_id=request_dto.cluster_id,
        nodes_to_add=nodes_to_add,
    )


def cluster_add_nodes_params_from_deploy_cluster_request_dto(
    cluster_id: str,
    request_dto: DeployClusterRequestDTO,
) -> AddNodesParams:
    worker_nodes_to_add: List[NodeToAddParams] = [
        NodeToAddParams(
            node_id=node_id, node_role=AllowedClusterNodeRoleDTO.WORKER.value.upper()
        )
        for node_id in request_dto.worker_node_ids
    ]
    control_plane_nodes_to_add: List[NodeToAddParams] = []
    if request_dto.control_plane_node_ids is not None:
        control_plane_nodes_to_add = [
            NodeToAddParams(
                node_id=node_id,
                node_role=AllowedClusterNodeRoleDTO.CONTROL_PLANE.value.upper(),
            )
            for node_id in request_dto.control_plane_node_ids
        ]
    return AddNodesParams(
        cluster_id=cluster_id,
        nodes_to_add=worker_nodes_to_add + control_plane_nodes_to_add,
    )
