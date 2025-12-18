from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, StrictStr

from exls.workspaces.core.domain import WorkerResources


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
