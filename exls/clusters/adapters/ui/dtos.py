from __future__ import annotations

from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr


class AllowedClusterStatusDTO(StrEnum):
    CREATED = "pending"
    DEPLOYING = "deploying"
    READY = "ready"
    FAILED = "failed"


class AllowedGpuTypesDTO(StrEnum):
    NVIDIA = "nvidia"
    AMD = "amd"
    NO_GPU = "no-gpu"

    @classmethod
    def values(cls) -> List[AllowedGpuTypesDTO]:
        return list(cls.__members__.values())


class AllowedClusterNodeRoleDTO(StrEnum):
    WORKER = "worker"
    CONTROL_PLANE = "control-plane"


class AllowedClusterTypesDTO(StrEnum):
    # CLOUD = "cloud"
    REMOTE = "remote"
    # ADOPTED = "adopted"

    @classmethod
    def values(cls) -> List[AllowedClusterTypesDTO]:
        return list(cls.__members__.values())


class AddNodesRequestDTO(BaseModel):
    cluster_id: StrictStr = Field(
        ..., description="The ID of the cluster to add nodes to"
    )
    node_ids: List[StrictStr] = Field(..., description="The IDs of the nodes to add")
    node_role: AllowedClusterNodeRoleDTO = Field(
        ..., description="The role of the nodes to add"
    )


class RemoveNodeRequestDTO(BaseModel):
    cluster_id: StrictStr = Field(
        ..., description="The ID of the cluster to remove a node from"
    )
    node_id: StrictStr = Field(..., description="The ID of the node to remove")


class DashboardUrlResponseDTO(BaseModel):
    url: StrictStr = Field(..., description="The dashboard URL")


class NodeValidationIssueDTO(BaseModel):
    node_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the node, if known"
    )
    node_name: Optional[StrictStr] = Field(
        default=None, description="The name of the node, if known"
    )
    error_message: StrictStr = Field(..., description="The error message that occurred")
