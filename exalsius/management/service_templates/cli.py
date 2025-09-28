from typing import List

import typer
from exalsius_api_client.models.service_template import ServiceTemplate

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.management.service_templates.display import (
    TableServiceTemplatesDisplayManager,
)
from exalsius.management.service_templates.service import ServiceTemplatesService
from exalsius.utils import commons as utils

service_templates_app = typer.Typer()


@service_templates_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage service templates.
    """
    utils.help_if_no_subcommand(ctx)


@service_templates_app.command("list", help="List all available service templates")
def list_service_templates(
    ctx: typer.Context,
):
    """List all available service templates."""
    display_manager: TableServiceTemplatesDisplayManager = (
        TableServiceTemplatesDisplayManager()
    )

    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)

    service: ServiceTemplatesService = ServiceTemplatesService(config, access_token)

    try:
        service_templates: List[ServiceTemplate] = service.list_service_templates()
        display_manager.display_service_templates(service_templates)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
