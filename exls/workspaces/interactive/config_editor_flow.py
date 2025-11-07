from typing import TYPE_CHECKING, Any, Dict, Optional

import typer
from pydantic import ValidationError

from exls.core.base.display import ErrorDisplayModel
from exls.core.commons.service import generate_random_name
from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO
from exls.workspaces.common.deploy_dtos import (
    WorkspaceDeployConfigDTO,
    WorkspaceDeployResourcesDTO,
    infer_types_in_dict,
)
from exls.workspaces.interactive.base_flow import BaseWorkspaceDeployFlow

if TYPE_CHECKING:
    from exls.workspaces.common.display import ComposingWorkspaceDeployDisplayManager


class WorkspaceConfigEditorFlow(BaseWorkspaceDeployFlow):
    """Flow for editing workspace deployment configuration."""

    def __init__(
        self,
        cluster_id: str,
        template: WorkspaceTemplateDTO,
        display_manager: "ComposingWorkspaceDeployDisplayManager",
    ):
        super().__init__(display_manager)
        self._cluster_id: str = cluster_id
        self._template: WorkspaceTemplateDTO = template

    def run(self) -> Optional[WorkspaceDeployConfigDTO]:
        """
        Create and edit workspace deployment configuration.

        Returns:
            WorkspaceDeployConfigDTO if successful, None if cancelled
        """
        try:
            workspace_name: str = self._display_manager.ask_text(
                "Workspace name:", default=generate_random_name(prefix="exls-ws")
            )

            initial_config = WorkspaceDeployConfigDTO(
                cluster_id=self._cluster_id,
                template_name=self._template.name,
                workspace_name=workspace_name,
                resources=WorkspaceDeployResourcesDTO(
                    gpu_count=0,
                    gpu_vendor="NVIDIA",
                    gpu_type=None,
                    gpu_memory=None,
                    cpu_cores=4,
                    memory_gb=8,
                    storage_gb=50,
                ),
                variables=self._get_template_variables(),
            )

            initial_yaml = initial_config.to_yaml()

            self._display_manager.display_info(
                "\n📝 Opening editor to configure resources and variables..."
            )
            self._display_manager.display_info(
                "Please edit the configuration and save. Close the editor when done."
            )

            edited_yaml = typer.edit(initial_yaml)

            # Handle cancellation (user closed editor without saving)
            if edited_yaml is None:
                self._display_manager.display_info("\nConfiguration editing cancelled.")
                return None

            # Parse edited YAML back to DTO
            try:
                config = WorkspaceDeployConfigDTO.from_yaml(edited_yaml)
            except (ValidationError, Exception) as e:
                self._display_manager.display_error(
                    ErrorDisplayModel(
                        message=f"Invalid configuration: {str(e)}. Please check your YAML syntax."
                    )
                )
                return None

            self._display_manager.display_info("\n📊 Configured workspace deployment:")
            self._display_manager.display_deploy_config(config)

            confirmed = self._display_manager.ask_confirm(
                "Deploy workspace with this configuration?", default=True
            )

            if not confirmed:
                return None

            return config

        except (KeyboardInterrupt, TypeError):
            return None

    def _get_template_variables(self) -> Dict[str, Any]:
        """
        Get template variables from the WorkspaceTemplateDTO.

        Returns the variables dict with default values, preserving nested structure.
        Automatically infers types for stringified values (e.g., "50" -> 50).
        """
        return infer_types_in_dict(self._template.variables)
