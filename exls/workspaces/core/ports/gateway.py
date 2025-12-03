from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.workspaces.core.domain import Workspace
from exls.workspaces.core.requests import DeployWorkspaceRequest


class WorkspaceResourceParameters(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")


class DeployWorkspaceParameters(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    template_name_id: StrictStr = Field(
        ...,
        description="The name of the template. Names are unique and used as identifiers.",
    )
    workspace_name: StrictStr = Field(..., description="The name of the workspace")
    resources: WorkspaceResourceParameters = Field(
        ..., description="The resources of the workspace"
    )
    description: Optional[str] = Field(
        None, description="The description of the workspace"
    )
    to_be_deleted_at: Optional[datetime] = Field(
        default=None,
        description="The date and time when the workspace should be deleted",
    )
    variables: Dict[str, Any] = Field(..., description="The variables of the workspace")


# TODO: This is really ambiguous. We should have a better data model to
# represent requested workspace resources.
def deploy_workspace_request_to_deploy_parameters(
    request: DeployWorkspaceRequest,
) -> DeployWorkspaceParameters:
    gpu_vendor: Optional[str] = request.resources.gpu_vendors
    if gpu_vendor:
        gpu_vendor = gpu_vendor.split(",")[0]

    resources: WorkspaceResourceParameters = WorkspaceResourceParameters(
        gpu_count=request.resources.gpu_count,
        gpu_type=request.resources.gpu_type,
        gpu_vendor=gpu_vendor,
        cpu_cores=request.resources.cpu_cores,
        memory_gb=request.resources.memory_gb,
        storage_gb=request.resources.storage_gb,
    )
    variables: Dict[str, Any] = request.template_variables

    return DeployWorkspaceParameters(
        cluster_id=request.cluster_id,
        template_name_id=request.template_id,
        workspace_name=request.workspace_name,
        resources=resources,
        description=request.description,
        to_be_deleted_at=request.to_be_deleted_at,
        variables=variables,
    )


class IWorkspacesGateway(ABC):
    @abstractmethod
    def list(self, cluster_id: Optional[str] = None) -> List[Workspace]:
        raise NotImplementedError

    @abstractmethod
    def get(self, workspace_id: str) -> Workspace:
        raise NotImplementedError

    @abstractmethod
    def deploy(self, parameters: DeployWorkspaceParameters) -> str:
        raise NotImplementedError

    @abstractmethod
    def delete(self, workspace_id: str) -> str:
        raise NotImplementedError
