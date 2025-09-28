import typer

from exalsius.management.cluster_templates.cli import cluster_templates_app
from exalsius.management.credentials.cli import credentials_app
from exalsius.management.service_templates.cli import service_templates_app
from exalsius.management.ssh_keys.cli import ssh_keys_app
from exalsius.management.workspace_templates.cli import workspace_templates_app
from exalsius.utils import commons as utils

management_app: typer.Typer = typer.Typer()
management_app.add_typer(cluster_templates_app, name="cluster-templates")
management_app.add_typer(credentials_app, name="credentials")
management_app.add_typer(service_templates_app, name="service-templates")
management_app.add_typer(ssh_keys_app, name="ssh-keys")
management_app.add_typer(workspace_templates_app, name="workspace-templates")


@management_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage management.
    """
    utils.help_if_no_subcommand(ctx)
