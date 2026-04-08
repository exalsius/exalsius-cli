from enum import StrEnum
from typing import Any, Dict

from pydantic import BaseModel, Field, StrictStr


class SshKeyScope(StrEnum):
    PRIVATE = "private"
    ORG = "org"


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
    scope: SshKeyScope = Field(
        default=SshKeyScope.PRIVATE, description="The visibility scope of the SSH key"
    )
