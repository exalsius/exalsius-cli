from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, StrictStr


class ClusterTemplateDTO(BaseModel):
    name: StrictStr = Field(..., description="The name of the cluster template")
    description: Optional[StrictStr] = Field(
        None, description="The description of the cluster template"
    )
    k8s_version: Optional[StrictStr] = Field(
        None, description="The Kubernetes version of the cluster template"
    )


class CredentialsDTO(BaseModel):
    name: StrictStr = Field(..., description="The name of the credentials")
    description: Optional[StrictStr] = Field(
        None, description="The description of the credentials"
    )


class ServiceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the service template")
    description: str = Field(description="The description of the service template")
    variables: str = Field(description="The variables of the service template")


class SshKeyDTO(BaseModel):
    id: StrictStr = Field(..., description="The ID of the SSH key")
    name: StrictStr = Field(..., description="The name of the SSH key")


class WorkspaceTemplateDTO(BaseModel):
    name: str = Field(description="The name of the workspace template")
    description: str = Field(description="The description of the workspace template")
    variables: Dict[str, Any] = Field(
        description="The variables of the workspace template with default values"
    )


class ImportSshKeyRequestDTO(BaseModel):
    name: StrictStr = Field(default="", description="The name of the SSH key")
    key_path: Path = Field(default=Path(""), description="The path to the SSH key file")
