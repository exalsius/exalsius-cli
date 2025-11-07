from typing import TYPE_CHECKING, List, Optional

import questionary

from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO
from exls.workspaces.interactive.base_flow import BaseWorkspaceDeployFlow
from exls.workspaces.interactive.mappers import templates_to_questionary_choices

if TYPE_CHECKING:
    from exls.workspaces.common.display import ComposingWorkspaceDeployDisplayManager


class WorkspaceTemplateSelectorFlow(BaseWorkspaceDeployFlow):
    """Flow for selecting a workspace template."""

    def __init__(
        self,
        templates: List[WorkspaceTemplateDTO],
        display_manager: "ComposingWorkspaceDeployDisplayManager",
    ):
        super().__init__(display_manager)
        if not templates:
            raise ValueError("No workspace templates available.")
        self._templates: List[WorkspaceTemplateDTO] = templates

    def run(self) -> Optional[WorkspaceTemplateDTO]:
        """
        Prompt user to select a workspace template.

        Returns:
            WorkspaceTemplateDTO if selected, None if cancelled
        """
        try:
            self._display_manager.display_workspace_templates(self._templates)

            template_choices: List[questionary.Choice] = (
                templates_to_questionary_choices(self._templates)
            )
            template_name = self._display_manager.ask_select_required(
                "Select workspace template:",
                choices=template_choices,
                default=template_choices[0],
            )

            for template in self._templates:
                if template.name == str(template_name):
                    return template

            return None

        except (KeyboardInterrupt, TypeError):
            return None
