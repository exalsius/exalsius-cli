from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, PositiveInt, StrictFloat, StrictInt, StrictStr

from exls.workspaces.core.domain import GPUVendorPreference, WorkerResources


class ResourceRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    gpu_vendor_preference: GPUVendorPreference = Field(
        ..., description="The vendor of the GPUs"
    )
    resource_split_tolerance: StrictFloat = Field(
        ..., description="The tolerance for the resource split"
    )


class SingleNodeWorkerResourcesRequest(ResourceRequest):
    num_gpus: PositiveInt = Field(..., description="The number of GPUs")


class WorkerGroupResourcesRequest(ResourceRequest):
    num_workers: StrictInt = Field(
        default=-1,
        description="The number of workers. If -1, the maximum number of workers will be used.",
    )
    num_gpus_per_worker: PositiveInt = Field(
        default=1, description="The number of GPUs per worker"
    )


class DeployWorkspaceRequest(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    workspace_name: StrictStr = Field(..., description="The name of the workspace")
    template_id: StrictStr = Field(..., description="The ID of the workspace template")
    template_variables: Dict[str, Any] = Field(
        ..., description="The variables of the workspace template"
    )
    resources: WorkerResources = Field(
        ..., description="The resources of the workspace"
    )
    description: Optional[str] = Field(
        default=None, description="The description of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None,
        description="The date and time when the workspace should be deleted",
    )
