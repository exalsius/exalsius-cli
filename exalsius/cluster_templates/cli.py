import typer
from rich.console import Console

from exalsius.cluster_templates.display import ClusterTemplatesDisplayManager
from exalsius.cluster_templates.service import ClusterTemplateService
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
    console = Console(theme=custom_theme)
    display_manager = ClusterTemplatesDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = ClusterTemplateService(access_token)

    cluster_templates, error = service.list_cluster_templates()
    if error:
        display_manager.print_error(f"Failed to list cluster templates: {error}")
        raise typer.Exit(1)
    display_manager.display_cluster_templates(cluster_templates)
