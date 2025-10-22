from typing import List

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.management.types.workspace_templates.display import (
    TableWorkspaceTemplatesDisplayManager,
)
from exls.management.types.workspace_templates.dtos import (
    ListWorkspaceTemplatesRequestDTO,
    WorkspaceTemplateDTO,
)
from exls.management.types.workspace_templates.service import (
    WorkspaceTemplatesService,
    get_workspace_templates_service,
)
from exls.utils import commons as utils

workspace_templates_app = typer.Typer()


def _get_workspace_templates_service(ctx: typer.Context) -> WorkspaceTemplatesService:
    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)
    return get_workspace_templates_service(config, access_token)


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
    display_manager = TableWorkspaceTemplatesDisplayManager()
    service = _get_workspace_templates_service(ctx)

    try:
        workspace_templates: List[WorkspaceTemplateDTO] = (
            service.list_workspace_templates(ListWorkspaceTemplatesRequestDTO())
        )
        display_manager.display_workspace_templates(workspace_templates)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)
