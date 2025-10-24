from __future__ import annotations

from typing import Dict, Optional

from exalsius_api_client.models.workspace_template import (
    WorkspaceTemplate as SdkWorkspaceTemplate,
)
from pydantic import BaseModel, Field


class WorkspaceTemplate(BaseModel):
    sdk_model: SdkWorkspaceTemplate = Field(
        ..., description="The SDK model of the workspace template"
    )

    @property
    def name(self) -> str:
        return self.sdk_model.name

    @property
    def description(self) -> Optional[str]:
        return self.sdk_model.description

    @property
    def variables(self) -> Dict[str, str]:
        return self.sdk_model.variables
