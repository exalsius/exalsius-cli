from __future__ import annotations

import datetime
from enum import StrEnum
from typing import Dict, List, Optional

from exalsius_api_client.models.cluster_add_node_request import ClusterAddNodeRequest
from exalsius_api_client.models.cluster_create_request import ClusterCreateRequest
from exalsius_api_client.models.cluster_node_to_add import ClusterNodeToAdd
from pydantic import BaseModel, Field, StrictStr


class ClusterLabels(StrEnum):
    GPU_TYPE = "cluster.exalsius.ai/gpu-type"
    WORKLOAD_TYPE = "cluster.exalsius.ai/workload-type"
    TELEMETRY_TYPE = "cluster.exalsius.ai/telemetry-enabled"


class ClusterLabelValuesGPUType(StrEnum):
    NVIDIA = "nvidia"
    AMD = "amd"
    NO_GPU = "no-gpu"


class ClusterLabelValuesWorkloadType(StrEnum):
    VOLCANO = "volcano"


class ClusterFilterParams(BaseModel):
    status: Optional[StrictStr] = Field(..., description="The status of the cluster")


class ClusterCreateParams(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster")
    cluster_type: StrictStr = Field(..., description="The type of the cluster")
    cluster_labels: Dict[StrictStr, StrictStr] = Field(
        ..., description="The labels of the cluster"
    )
    colony_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the colony to add the cluster to"
    )
    to_be_deleted_at: Optional[datetime.datetime] = Field(
        default=None, description="The date and time the cluster will be deleted"
    )
    control_plane_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )
    worker_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the worker nodes"
    )

    def to_sdk_request(self) -> ClusterCreateRequest:
        return ClusterCreateRequest(
            name=self.name,
            cluster_type=self.cluster_type,
            cluster_labels=self.cluster_labels,
            colony_id=self.colony_id,
            to_be_deleted_at=self.to_be_deleted_at,
            control_plane_node_ids=self.control_plane_node_ids,
            worker_node_ids=self.worker_node_ids,
        )


class NodeToAddParams(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node to add")
    node_role: StrictStr = Field(..., description="The role of the node to add")

    def to_sdk_model(self) -> ClusterNodeToAdd:
        return ClusterNodeToAdd(node_id=self.node_id, node_role=self.node_role)


class AddNodesParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    nodes_to_add: List[NodeToAddParams] = Field(
        ..., description="The nodes to add to the cluster"
    )

    def to_sdk_request(self) -> ClusterAddNodeRequest:
        return ClusterAddNodeRequest(
            nodes_to_add=[node.to_sdk_model() for node in self.nodes_to_add]
        )


class RemoveNodeParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    node_id: StrictStr = Field(..., description="The ID of the node to remove")
