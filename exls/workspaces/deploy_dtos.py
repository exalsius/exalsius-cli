from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import yaml
from pydantic import BaseModel, Field


def infer_variable_type(value: Any) -> Any:
    """
    Infer the actual type of a variable value that may be stringified.

    Converts string representations to appropriate types:
    - "123" -> 123 (int)
    - "1.5" -> 1.5 (float)
    - "true"/"false" -> bool (case-insensitive)
    - Recursively processes nested dicts

    Args:
        value: The value to infer type for

    Returns:
        Value with inferred type
    """
    if not isinstance(value, str):
        if isinstance(value, dict):
            return infer_types_in_dict(cast(Dict[str, Any], value))
        return value

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    try:
        if "." not in value and "e" not in value.lower():
            return int(value)
    except (ValueError, TypeError):
        pass

    try:
        return float(value)
    except (ValueError, TypeError):
        pass

    return value


def infer_types_in_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively infer types for all values in a dictionary.

    Args:
        data: Dictionary with potentially stringified values

    Returns:
        Dictionary with properly typed values
    """
    result: Dict[str, Any] = {}
    for key, value in data.items():
        result[key] = infer_variable_type(value)
    return result


class WorkspaceDeployResourcesDTO(BaseModel):
    """Resources configuration for workspace deployment."""

    gpu_count: int = Field(default=0, description="The number of GPUs")
    gpu_vendor: Optional[str] = Field(
        default=None, description="The GPU vendor (e.g., NVIDIA, AMD)"
    )
    gpu_type: Optional[str] = Field(
        default=None, description="The GPU type (e.g., A100, H100)"
    )
    gpu_memory: Optional[int] = Field(default=None, description="GPU memory in GB")
    cpu_cores: int = Field(default=4, description="The number of CPU cores")
    memory_gb: int = Field(default=8, description="The amount of memory in GB")
    storage_gb: int = Field(default=50, description="The amount of storage in GB")


class WorkspaceDeployConfigDTO(BaseModel):
    """Complete configuration for workspace deployment."""

    cluster_id: str = Field(..., description="The ID of the cluster to deploy to")
    template_name: str = Field(..., description="The name of the workspace template")
    workspace_name: str = Field(..., description="The name for the workspace")
    resources: WorkspaceDeployResourcesDTO = Field(
        ..., description="Resource configuration"
    )
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template variables with nested structure support",
    )

    def to_yaml(self) -> str:
        """
        Convert the configuration to YAML string.

        Returns:
            YAML string representation with helpful comments
        """
        data = self.model_dump(mode="json", exclude_none=False)
        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)

        # Insert comments for specific fields
        lines = yaml_str.split("\n")
        result_lines: List[str] = []

        for line in lines:
            if line.startswith("cluster_id:"):
                result_lines.append("# Target cluster ID for workspace deployment")
            elif line.startswith("template_name:"):
                result_lines.append(
                    "# This is the template name of the workspace. Do not change it."
                )
            elif line.startswith("workspace_name:"):
                result_lines.append(
                    "# This is the name of the workspace. Please adjust the value as needed."
                )
            elif line.startswith("resources:"):
                result_lines.append(
                    "# This is the resources configuration for the workspace. Please adjust the values as needed."
                )
            elif line.startswith("variables:"):
                result_lines.append(
                    "# This is the variables configuration for the workspace. Please adjust the values as needed."
                )

            result_lines.append(line)

        return "\n".join(result_lines)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> WorkspaceDeployConfigDTO:
        """
        Create configuration from YAML string.

        Args:
            yaml_str: YAML string to parse

        Returns:
            WorkspaceDeployConfigDTO instance
        """
        data = yaml.safe_load(yaml_str)
        return cls(**data)

    def to_file(self, file_path: str | Path) -> None:
        """
        Save configuration to YAML file.

        Args:
            file_path: Path to save the file
        """
        path = Path(file_path)
        yaml_content = self.to_yaml()
        path.write_text(yaml_content, encoding="utf-8")

    @classmethod
    def from_file(cls, file_path: str | Path) -> WorkspaceDeployConfigDTO:
        """
        Load configuration from YAML file.

        Args:
            file_path: Path to the YAML file

        Returns:
            WorkspaceDeployConfigDTO instance
        """
        path = Path(file_path)
        yaml_content = path.read_text(encoding="utf-8")
        return cls.from_yaml(yaml_content)
