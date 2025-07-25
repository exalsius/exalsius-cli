from pathlib import Path

import typer
from rich.console import Console

from exalsius.cli import utils
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
def _root(
    ctx: typer.Context,
):
    """
    Manage SSH keys, cluster templates, and cloud credentials.
    """
    utils.help_if_no_subcommand(ctx)


# SSH Key commands
@ssh_key_app.callback(invoke_without_command=True)
def ssh_key_callback(ctx: typer.Context):
    """Manage SSH keys in the management cluster"""
    utils.help_if_no_subcommand(ctx)


@ssh_key_app.command("list")
def list_ssh_keys(ctx: typer.Context):
    """List all SSH keys in the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = SSHKeyDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = SSHKeyService(access_token)

    ssh_keys, error = service.list_ssh_keys()
    if error:
        display_manager.print_error(f"Failed to list SSH keys: {error}")
        raise typer.Exit(1)
    display_manager.display_ssh_keys(ssh_keys)


@ssh_key_app.command("add")
def add_ssh_key(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Name for the SSH key"),
    key_path: Path = typer.Option(
        ..., "--key-path", "-k", help="Path to the SSH private key file"
    ),
):
    """Add a new SSH key to the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = SSHKeyDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = SSHKeyService(access_token)

    ssh_key_create_response, error = service.add_ssh_key(name, key_path)
    if error:
        display_manager.print_error(f"Failed to add SSH key: {error}")
        raise typer.Exit(1)
    if not ssh_key_create_response:
        display_manager.print_error("Failed to add SSH key.")
        raise typer.Exit(1)
    display_manager.print_success(
        f"Added SSH key '{ssh_key_create_response.ssh_key_id}' from {key_path}"
    )


@ssh_key_app.command("delete")
def delete_ssh_key(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Name of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    console = Console(theme=custom_theme)
    display_manager = SSHKeyDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = SSHKeyService(access_token)

    delete_success, error = service.delete_ssh_key(name)
    if not delete_success and error:
        display_manager.print_error(f"Failed to delete SSH key: {error}")
        raise typer.Exit(1)

    display_manager.print_success(f"Deleted SSH key '{name}'")


# Cluster Templates commands
@cluster_templates_app.callback(invoke_without_command=True)
def cluster_templates_callback(ctx: typer.Context):
    """Manage cluster templates"""
    utils.help_if_no_subcommand(ctx)


@cluster_templates_app.command("list")
def list_cluster_templates(ctx: typer.Context):
    """List all available cluster templates."""
    console = Console(theme=custom_theme)
    display_manager = ClusterTemplateDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = ClusterTemplateService(access_token)

    cluster_templates, error = service.list_cluster_templates()
    if error:
        display_manager.print_error(f"Failed to list cluster templates: {error}")
        raise typer.Exit(1)
    display_manager.display_cluster_templates(cluster_templates)


# Credentials commands
@credentials_app.callback(invoke_without_command=True)
def credentials_callback(ctx: typer.Context):
    """Manage cloud provider credentials"""
    utils.help_if_no_subcommand(ctx)


@credentials_app.command("list")
def list_cloud_credentials(ctx: typer.Context):
    """List all available cloud provider credentials."""
    console = Console(theme=custom_theme)
    display_manager = CloudCredentialsDisplayManager(console)

    access_token: str = utils.get_access_token_from_ctx(ctx)
    service = CloudCredentialsService(access_token)

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
