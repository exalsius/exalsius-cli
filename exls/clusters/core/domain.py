from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import List, Optional, cast

from pydantic import BaseModel, Field, StrictInt, StrictStr, field_validator


class ClusterType(StrEnum):
    REMOTE = "REMOTE"
    ADOPTED = "ADOPTED"
    CLOUD = "CLOUD"
    DOCKER = "DOCKER"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterType:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class ClusterStatus(StrEnum):
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    READY = "READY"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterStatus:
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN


class Cluster(BaseModel):
    id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the cluster")
    status: ClusterStatus = Field(..., description="The status of the cluster")
    type: ClusterType = Field(..., description="The type of the cluster")
    created_at: datetime = Field(..., description="The creation date of the cluster")
    updated_at: Optional[datetime] = Field(
        ..., description="The last update date of the cluster"
    )


class ClusterWithNodes(Cluster):
    nodes: List[AssignedClusterNode] = Field(
        ..., description="The nodes of the cluster"
    )


class Resources(BaseModel):
    gpu_type: StrictStr = Field(..., description="The type of the GPU")
    gpu_vendor: StrictStr = Field(..., description="The vendor of the GPU")
    gpu_count: StrictInt = Field(..., description="The count of the GPU")
    cpu_cores: StrictInt = Field(..., description="The count of the CPU cores")
    memory_gb: StrictInt = Field(..., description="The amount of memory in GB")
    storage_gb: StrictInt = Field(..., description="The amount of storage in GB")


class ClusterNodeResources(BaseModel):
    cluster_node: AssignedClusterNode = Field(..., description="The cluster node")

    free_resources: Resources = Field(..., description="The free resources of the node")
    occupied_resources: Resources = Field(
        ..., description="The occupied resources of the node"
    )


class ClusterNodeStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    DISCOVERING = "DISCOVERING"
    ADDED = "ADDED"
    DEPLOYED = "DEPLOYED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: str) -> ClusterNodeStatus:
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN


class ClusterNodeRole(StrEnum):
    WORKER = "WORKER"
    CONTROL_PLANE = "CONTROL_PLANE"


class ClusterNode(BaseModel):
    id: StrictStr = Field(..., description="The ID of the node")
    hostname: StrictStr = Field(..., description="The hostname of the node")
    username: StrictStr = Field(..., description="The username of the node")
    ssh_key_id: StrictStr = Field(..., description="The SSH key of the node")
    status: ClusterNodeStatus = Field(..., description="The status of the node")
    endpoint: Optional[StrictStr] = Field(
        default=None, description="The endpoint of the node"
    )


class UnassignedClusterNode(ClusterNode):
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: ClusterNodeStatus) -> ClusterNodeStatus:
        if v not in [ClusterNodeStatus.AVAILABLE, ClusterNodeStatus.DISCOVERING]:
            raise ValueError(
                f"Unassigned nodes must be in AVAILABLE or DISCOVERING status, got {v}"
            )
        return v


class AssignedClusterNode(ClusterNode):
    role: ClusterNodeRole = Field(..., description="The role of the node")

    @classmethod
    def from_unassigned_node(
        cls, node: UnassignedClusterNode, role: ClusterNodeRole
    ) -> AssignedClusterNode:
        return cls(
            id=node.id,
            hostname=node.hostname,
            username=node.username,
            ssh_key_id=node.ssh_key_id,
            status=node.status,
            role=role,
        )


class NodeValidationIssue(BaseModel):
    node_id: Optional[StrictStr] = Field(
        default=None, description="The ID of the node, if known"
    )
    node_spec_repr: Optional[StrictStr] = Field(
        default=None, description="String representation of node spec if ID not known"
    )
    reason: StrictStr = Field(..., description="The reason for validation failure")


class DeployClusterResult(BaseModel):
    cluster: Optional[ClusterWithNodes] = Field(
        default=None, description="The created cluster with its nodes"
    )
    issues: List[NodeValidationIssue] = Field(
        default_factory=lambda: cast(List[NodeValidationIssue], []),
        description="List of validation issues encountered",
    )

    @property
    def is_success(self) -> bool:
        return self.cluster is not None and len(self.issues) == 0

    @property
    def is_partially_successful(self) -> bool:
        return self.cluster is not None and len(self.issues) > 0


class NodesLoadingIssue(BaseModel):
    node_id: StrictStr = Field(..., description="The ID of the node")
    reason: StrictStr = Field(..., description="The reason for loading failure")


class NodesLoadingResult(BaseModel):
    nodes: List[AssignedClusterNode] = Field(..., description="The loaded nodes")
    issues: Optional[List[NodesLoadingIssue]] = Field(
        default=None, description="List of loading issues encountered"
    )

    @property
    def is_success(self) -> bool:
        return self.issues is None or len(self.issues) == 0
