from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WorkspaceDeploymentResourcesConfigDTO(BaseModel):
    gpu_count: int = Field(default=1, description="The number of GPUs")
    cpu_cores: int = Field(default=16, description="The number of CPU cores")
    memory_gb: int = Field(default=64, description="The amount of memory in GB")
    pvc_storage_gb: int = Field(
        default=100, description="The amount of PVC storage in GB"
    )
    ephemeral_storage_gb: Optional[int] = Field(
        default=None, description="The amount of ephemeral storage in GB"
    )


class WorkspaceDeploymentConfigDTO(BaseModel):
    cluster_id: str = Field(..., description="The ID of the cluster")
    cluster_name: str = Field(..., description="The name of the cluster")
    workspace_name: str = Field(..., description="The name of the workspace")
    workspace_template_name: str = Field(
        ..., description="The name of the workspace template"
    )
    resources: WorkspaceDeploymentResourcesConfigDTO = Field(
        ..., description="The resources of the workspace"
    )
    variables: Dict[str, Any] = Field(..., description="The variables of the workspace")
