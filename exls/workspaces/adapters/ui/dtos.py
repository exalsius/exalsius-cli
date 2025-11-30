from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, StrictStr


class IntegratedWorkspaceTemplates(StrEnum):
    JUPYTER = "jupyter-notebook-template"
    MARIMO = "marimo-workspace-template"
    VSCODE_DEV_POD = "vscode-devcontainer-template"
    DIST_TRAINING = "diloco-training-template"
    OTHER = "other"

    @classmethod
    def from_str(cls, value: str) -> IntegratedWorkspaceTemplates:
        try:
            return cls(value)
        except ValueError:
            return cls.OTHER


class DeploySingleNodeWorkspaceRequestDTO(BaseModel):
    cluster_name: StrictStr = Field(..., description="The name of the cluster")
    workspace_name: StrictStr = Field(..., description="The name of the workspace")
    workspace_template_name: StrictStr = Field(
        ..., description="The name of the workspace template"
    )
    num_gpus: int = Field(..., description="The number of GPUs")
    variables: StrictStr = Field(..., description="The variables of the workspace")


class DeployMultiNodeWorkspaceRequestDTO(BaseModel):
    cluster_name: StrictStr = Field(..., description="The name of the cluster")
    workspace_name: StrictStr = Field(..., description="The name of the workspace")
    workspace_template_name: StrictStr = Field(
        ..., description="The name of the workspace template"
    )
    total_nodes: int = Field(..., description="The total number of nodes")
    gpu_types: StrictStr = Field(..., description="The types of the GPUs")
    variables: StrictStr = Field(..., description="The variables of the workspace")
