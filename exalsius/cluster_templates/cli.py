import typer
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)
from rich.console import Console

from exalsius.cluster_templates.display import ClusterTemplatesDisplayManager
from exalsius.cluster_templates.service import ClusterTemplateService
from exalsius.config import AppConfig
from exalsius.core.commons.models import ServiceError
from exalsius.utils import commons as utils
from exalsius.utils.theme import custom_theme

app = typer.Typer()


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
):
    """
    Manage cluster templates.
    """
    utils.help_if_no_subcommand(ctx)


@app.command("list")
def list_cluster_templates(ctx: typer.Context):
    """List all available cluster templates."""
    console: Console = Console(theme=custom_theme)
    display_manager: ClusterTemplatesDisplayManager = ClusterTemplatesDisplayManager(
        console
    )

    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)

    service: ClusterTemplateService = ClusterTemplateService(config, access_token)

    try:
        cluster_templates: ClusterTemplateListResponse = (
            service.list_cluster_templates()
        )
        display_manager.display_cluster_templates(cluster_templates.cluster_templates)
    except ServiceError as e:
        display_manager.print_error(e.message)
        raise typer.Exit(1)
