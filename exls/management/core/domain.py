from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, StrictStr


class ClusterTemplate(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster template")
    description: Optional[StrictStr] = Field(
        None, description="The description of the cluster template"
    )
    k8s_version: Optional[StrictStr] = Field(
        None, description="The Kubernetes version of the cluster template"
    )


class Credentials(BaseModel):
    name: StrictStr = Field(..., description="The name of the credentials")
    description: Optional[StrictStr] = Field(
        None, description="The description of the credentials"
    )


class ServiceTemplate(BaseModel):
    name: StrictStr = Field(..., description="The name of the service template")
    description: StrictStr = Field(
        ..., description="The description of the service template"
    )
    variables: Dict[StrictStr, Any] = Field(
        ..., description="The variables of the service template"
    )


class WorkspaceTemplate(BaseModel):
    name: StrictStr = Field(..., description="The name of the workspace template")
    description: StrictStr = Field(
        ..., description="The description of the workspace template"
    )
    variables: Dict[StrictStr, Any] = Field(
        ..., description="The variables of the workspace template"
    )


class SshKey(BaseModel):
    id: StrictStr = Field(..., description="The ID of the SSH key")
    name: StrictStr = Field(..., description="The name of the SSH key")


class AddSshKeyRequest(BaseModel):
    name: StrictStr = Field(..., description="The name of the SSH key")
    key_path: Path = Field(..., description="The path to the SSH private key file")
