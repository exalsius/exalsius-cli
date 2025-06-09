from pathlib import Path

import typer
from rich.console import Console

from exalsius.core.services.cloud_credentials_service import CloudCredentialsService
from exalsius.core.services.cluster_template_service import ClusterTemplateService
from exalsius.core.services.ssh_key_service import SSHKeyService
from exalsius.display.cloud_credentials_display import CloudCredentialsDisplayManager
from exalsius.display.cluster_template_display import ClusterTemplateDisplayManager
from exalsius.display.ssh_key_display import SSHKeyDisplayManager
from exalsius.utils.theme import custom_theme

app = typer.Typer()
ssh_key_app = typer.Typer()
cluster_templates_app = typer.Typer()
credentials_app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context = typer.Context):
    """Manage SSH keys, cluster templates, and cloud credentials"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


# SSH Key commands
@ssh_key_app.callback(invoke_without_command=True)
def ssh_key_callback(ctx: typer.Context = typer.Context):
    """Manage SSH keys in the management cluster"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@ssh_key_app.command("list")
def list_ssh_keys():
    """List all SSH keys in the management cluster."""
    console = Console(theme=custom_theme)
    service = SSHKeyService()
    display_manager = SSHKeyDisplayManager(console)
    ssh_keys, error = service.list_ssh_keys()
    if error:
        display_manager.print_error(f"Failed to list SSH keys: {error}")
        raise typer.Exit(1)
    display_manager.display_ssh_keys(ssh_keys)


@ssh_key_app.command("add")
def add_ssh_key(
    name: str = typer.Option(..., "--name", "-n", help="Name for the SSH key"),
    key_path: Path = typer.Option(
        ..., "--key-path", "-k", help="Path to the SSH private key file"
    ),
):
    """Add a new SSH key to the management cluster."""
    console = Console(theme=custom_theme)
    service = SSHKeyService()
    display_manager = SSHKeyDisplayManager(console)
    ssh_key_create_response, error = service.add_ssh_key(name, key_path)
    if error:
        display_manager.print_error(f"Failed to add SSH key: {error}")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Added SSH key '{ssh_key_create_response.ssh_key_id}' from {key_path}"
    )


@ssh_key_app.command("delete")
def delete_ssh_key(
    name: str = typer.Option(..., "--name", "-n", help="Name of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    console = Console(theme=custom_theme)
    service = SSHKeyService()
    display_manager = SSHKeyDisplayManager(console)
    delete_success, error = service.delete_ssh_key(name)
    if not delete_success and error:
        display_manager.print_error(f"Failed to delete SSH key: {error}")
        raise typer.Exit(1)

    display_manager.print_success(f"Deleted SSH key '{name}'")


# Cluster Templates commands
@cluster_templates_app.callback(invoke_without_command=True)
def cluster_templates_callback(ctx: typer.Context = typer.Context):
    """Manage cluster templates"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@cluster_templates_app.command("list")
def list_cluster_templates():
    """List all available cluster templates."""
    console = Console(theme=custom_theme)
    service = ClusterTemplateService()
    display_manager = ClusterTemplateDisplayManager(console)
    cluster_templates, error = service.list_cluster_templates()
    if error:
        display_manager.print_error(f"Failed to list cluster templates: {error}")
        raise typer.Exit(1)
    display_manager.display_cluster_templates(cluster_templates)


# Credentials commands
@credentials_app.callback(invoke_without_command=True)
def credentials_callback(ctx: typer.Context = typer.Context):
    """Manage cloud provider credentials"""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@credentials_app.command("list")
def list_cloud_credentials():
    """List all available cloud provider credentials."""
    console = Console(theme=custom_theme)
    service = CloudCredentialsService()
    display_manager = CloudCredentialsDisplayManager(console)
    cloud_credentials, error = service.list_cloud_credentials()
    if error:
        display_manager.print_error(f"Failed to list cloud credentials: {error}")
        raise typer.Exit(1)
    display_manager.display_cloud_credentials(cloud_credentials)


# Add all subcommands to the main management app
app.add_typer(
    ssh_key_app,
    name="ssh-keys",
    help="Manage SSH keys in the management cluster",
)

app.add_typer(
    cluster_templates_app,
    name="cluster-templates",
    help="Manage cluster templates",
)

app.add_typer(
    credentials_app,
    name="credentials",
    help="Manage cloud provider credentials",
)
