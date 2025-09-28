from typing import List

import typer
from exalsius_api_client.models.cluster_template import ClusterTemplate

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.management.cluster_templates.display import (
    TableClusterTemplatesDisplayManager,
)
from exalsius.management.cluster_templates.service import ClusterTemplateService
from exalsius.utils import commons as utils

cluster_templates_app = typer.Typer()


@cluster_templates_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage cluster templates.
    """
    utils.help_if_no_subcommand(ctx)


@cluster_templates_app.command("list", help="List all available cluster templates")
def list_cluster_templates(ctx: typer.Context):
    """List all available cluster templates."""
    display_manager: TableClusterTemplatesDisplayManager = (
        TableClusterTemplatesDisplayManager()
    )

    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)

    service: ClusterTemplateService = ClusterTemplateService(config, access_token)

    try:
        cluster_templates: List[ClusterTemplate] = service.list_cluster_templates()
        display_manager.display_cluster_templates(cluster_templates)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
