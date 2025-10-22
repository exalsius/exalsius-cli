from typing import List

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.management.types.service_templates.display import (
    TableServiceTemplatesDisplayManager,
)
from exls.management.types.service_templates.dtos import (
    ListServiceTemplatesRequestDTO,
    ServiceTemplateDTO,
)
from exls.management.types.service_templates.service import (
    ServiceTemplatesService,
    get_service_templates_service,
)
from exls.utils import commons as utils

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
    display_manager = TableServiceTemplatesDisplayManager()

    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)

    service: ServiceTemplatesService = get_service_templates_service(
        config, access_token
    )

    try:
        service_templates: List[ServiceTemplateDTO] = service.list_service_templates(
            ListServiceTemplatesRequestDTO()
        )
        display_manager.display_service_templates(service_templates)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)
