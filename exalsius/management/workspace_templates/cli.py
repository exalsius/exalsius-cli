from typing import List

import typer
from exalsius_api_client.models.workspace_template import WorkspaceTemplate

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.management.workspace_templates.display import (
    TableWorkspaceTemplatesDisplayManager,
)
from exalsius.management.workspace_templates.service import WorkspaceTemplatesService
from exalsius.utils import commons as utils

workspace_templates_app = typer.Typer()


@workspace_templates_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage workspace templates management.
    """
    utils.help_if_no_subcommand(ctx)


@workspace_templates_app.command("list", help="List all available workspace templates")
def list_workspace_templates(
    ctx: typer.Context,
):
    """List all available workspace templates."""
    display_manager: TableWorkspaceTemplatesDisplayManager = (
        TableWorkspaceTemplatesDisplayManager()
    )

    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)

    service: WorkspaceTemplatesService = WorkspaceTemplatesService(config, access_token)

    try:
        workspace_templates: List[WorkspaceTemplate] = (
            service.list_workspace_templates()
        )
        display_manager.display_workspace_templates(workspace_templates)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
