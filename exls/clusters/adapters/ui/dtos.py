from __future__ import annotations

from enum import StrEnum
from typing import List, Optional, cast

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


class UnassignedClusterNodeDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    name: StrictStr = Field(..., description="The name of the node")


class DeployClusterRequestFromFlowDTO(BaseModel):
    name: StrictStr = Field(default="", description="The name of the cluster")
    cluster_type: AllowedClusterTypesDTO = Field(
        default=AllowedClusterTypesDTO.REMOTE, description="The type of the cluster"
    )
    worker_node_ids: List[UnassignedClusterNodeDTO] = Field(
        default_factory=lambda: cast(List[UnassignedClusterNodeDTO], []),
        description="The worker nodes",
    )
    control_plane_node_ids: Optional[List[UnassignedClusterNodeDTO]] = Field(
        default_factory=lambda: cast(Optional[List[UnassignedClusterNodeDTO]], []),
        description="The control plane nodes",
    )
    enable_multinode_training: bool = Field(
        default=False,
        description="Enable multinode AI model training for the cluster",
    )
    enable_telemetry: bool = Field(
        default=False, description="Enable telemetry for the cluster"
    )
    enable_vpn: bool = Field(default=False, description="Enable VPN for the cluster")
