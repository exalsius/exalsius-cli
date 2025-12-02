from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, StrictStr


class WorkspaceResources(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(default=None, description="The type of the GPUs")
    gpu_vendors: Optional[StrictStr] = Field(
        default=None, description="The vendor of the GPUs"
    )
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")
    ephemeral_storage_gb: Optional[int] = Field(
        default=None, description="The amount of ephemeral storage in GB"
    )


class AssignedSingleNodeWorkspaceResources(WorkspaceResources):
    pass


class RequestedWorkspaceResources(WorkspaceResources):
    pass


class AssignedMultiNodeWorkspaceResources(WorkspaceResources):
    num_amd_nodes: int = Field(..., description="The number of AMD nodes")
    num_nvidia_nodes: int = Field(..., description="The number of NVIDIA nodes")

    @property
    def total_nodes(self) -> int:
        return self.num_amd_nodes + self.num_nvidia_nodes

    @property
    def heterogenous(self) -> bool:
        return self.num_amd_nodes > 0 and self.num_nvidia_nodes > 0


class DeployWorkspaceRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    workspace_name: StrictStr = Field(..., description="The name of the workspace")
    template_id: StrictStr = Field(..., description="The ID of the workspace template")
    template_variables: Dict[str, Any] = Field(
        ..., description="The variables of the workspace template"
    )
    resources: WorkspaceResources = Field(
        ..., description="The resources of the workspace"
    )
    description: Optional[str] = Field(
        default=None, description="The description of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None,
        description="The date and time when the workspace should be deleted",
    )
