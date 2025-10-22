from typing import Any, Dict, List, cast

from exalsius_api_client.models.workspace_template import WorkspaceTemplate

from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exalsius.core.commons.render.json import JsonListStringRenderer
from exalsius.core.commons.render.table import Column, TableListRenderer, get_column
from exalsius.management.workspace_templates.models import (
    RenderableWorkspaceTemplateDTO,
)


def _flatten_variables(
    variables: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, str]:
    """
    Flatten nested dictionary variables with dot notation.

    Args:
        variables: Dictionary of variables (potentially nested)
        parent_key: Parent key for nested dictionaries
        sep: Separator for nested keys (default: ".")

    Returns:
        Flattened dictionary with dot notation keys
    """
    items: List[tuple[str, str]] = []
    for key, value in variables.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(
                _flatten_variables(
                    cast(Dict[str, Any], value), new_key, sep=sep
                ).items()
            )
        else:
            items.append((new_key, str(value)))
    return dict(items)


def _format_variables_display(variables: Dict[str, Any]) -> str:
    """
    Format variables for display as inline comma-separated key=value pairs.

    Args:
        variables: Dictionary of variables (potentially nested)

    Returns:
        Formatted string with key=value pairs separated by commas
    """
    flattened = _flatten_variables(variables)
    return ", ".join(f"{key}={value}" for key, value in flattened.items())


class JsonWorkspaceTemplatesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        workspace_templates_list_renderer: JsonListStringRenderer[
            WorkspaceTemplate
        ] = JsonListStringRenderer[WorkspaceTemplate](),
    ):
        super().__init__()
        self.workspace_templates_list_display = ConsoleListDisplay(
            renderer=workspace_templates_list_renderer
        )

    def display_workspace_templates(self, workspace_templates: List[WorkspaceTemplate]):
        self.workspace_templates_list_display.display(workspace_templates)


DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Name"),
    "description": get_column("Description"),
    "variables": get_column("Variables"),
}


class TableWorkspaceTemplatesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        workspace_templates_list_renderer: TableListRenderer[
            RenderableWorkspaceTemplateDTO
        ] = TableListRenderer(
            columns_rendering_map=DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.workspace_templates_list_display = ConsoleListDisplay(
            renderer=workspace_templates_list_renderer
        )

    def display_workspace_templates(self, workspace_templates: List[WorkspaceTemplate]):
        renderable_workspace_templates: List[RenderableWorkspaceTemplateDTO] = [
            RenderableWorkspaceTemplateDTO(
                name=workspace_template.name,
                description=workspace_template.description or "",
                variables=_format_variables_display(workspace_template.variables),
            )
            for workspace_template in workspace_templates
        ]
        self.workspace_templates_list_display.display(renderable_workspace_templates)
