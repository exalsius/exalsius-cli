from __future__ import annotations

from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, StrictStr


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


class DeployClusterRequestDTO(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster")
    cluster_type: AllowedClusterTypesDTO = Field(
        ..., description="The type of the cluster"
    )
    worker_node_ids: List[StrictStr] = Field(
        ..., description="The IDs of the worker nodes"
    )
    control_plane_node_ids: Optional[List[StrictStr]] = Field(
        default=None, description="The IDs of the control plane nodes"
    )
    enable_multinode_training: bool = Field(
        ...,
        description="Enable multinode AI model training for the cluster",
    )
    enable_telemetry: bool = Field(..., description="Enable telemetry for the cluster")
