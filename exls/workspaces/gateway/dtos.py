from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, StrictStr


class RequestedResourcesParams(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    pvc_storage_gb: int = Field(..., description="The amount of PVC storage in GB")
    ephemeral_storage_gb: Optional[int] = Field(
        None, description="The amount of ephemeral storage in GB"
    )


class DeployWorkspaceParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    template_name: StrictStr = Field(..., description="The ID of the template")
    workspace_name: StrictStr = Field(..., description="The name of the workspace")
    resources: RequestedResourcesParams = Field(
        ..., description="The resources of the workspace"
    )
    description: Optional[str] = Field(
        None, description="The description of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        None, description="The date and time when the workspace should be deleted"
    )
    variables: Dict[str, Any] = Field(..., description="The variables of the workspace")
