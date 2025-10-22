from typing import List

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.management.types.cluster_templates.display import (
    TableClusterTemplatesDisplayManager,
)
from exls.management.types.cluster_templates.dtos import (
    ClusterTemplateDTO,
    ListClusterTemplatesRequestDTO,
)
from exls.management.types.cluster_templates.service import (
    ClusterTemplateService,
    get_cluster_templates_service,
)
from exls.utils import commons as utils

cluster_templates_app = typer.Typer()


def _get_cluster_templates_service(ctx: typer.Context) -> ClusterTemplateService:
    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)
    return get_cluster_templates_service(config, access_token)


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
    service: ClusterTemplateService = _get_cluster_templates_service(ctx)

    try:
        cluster_templates: List[ClusterTemplateDTO] = service.list_cluster_templates(
            ListClusterTemplatesRequestDTO()
        )
        display_manager.display_cluster_templates(cluster_templates)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)
