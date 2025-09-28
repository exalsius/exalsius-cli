from pathlib import Path
from typing import List

import typer
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.management.ssh_keys.display import (
    TableSshKeysDisplayManager,
)
from exalsius.management.ssh_keys.service import SshKeysService
from exalsius.utils import commons as utils

ssh_keys_app = typer.Typer()


@ssh_keys_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage SSH keys management.
    """
    utils.help_if_no_subcommand(ctx)


@ssh_keys_app.command("list", help="List all available SSH keys")
def list_ssh_keys(
    ctx: typer.Context,
):
    """List all available SSH keys."""
    display_manager: TableSshKeysDisplayManager = TableSshKeysDisplayManager()

    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)

    service: SshKeysService = SshKeysService(config, access_token)

    try:
        ssh_keys: List[SshKeysListResponseSshKeysInner] = service.list_ssh_keys()
        display_manager.display_ssh_keys(ssh_keys)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)


@ssh_keys_app.command("add", help="Add a new SSH key")
def add_ssh_key(
    ctx: typer.Context,
    name: str = typer.Option(..., "--name", "-n", help="Name for the SSH key"),
    key_path: Path = typer.Option(
        ..., "--key-path", "-k", help="Path to the SSH private key file"
    ),
):
    """Add a new SSH key to the management cluster."""
    display_manager: TableSshKeysDisplayManager = TableSshKeysDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)

    service: SshKeysService = SshKeysService(config, access_token)

    try:
        ssh_key_id: str = service.add_ssh_key(name, key_path)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)

    display_manager.display_success(f"Added SSH key '{ssh_key_id}' from {key_path}")


@ssh_keys_app.command("delete", help="Delete an SSH key")
def delete_ssh_key(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="ID of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    display_manager: TableSshKeysDisplayManager = TableSshKeysDisplayManager()

    access_token: str = utils.get_access_token_from_ctx(ctx)
    config: AppConfig = utils.get_config_from_ctx(ctx)
    service: SshKeysService = SshKeysService(config, access_token)

    try:
        service.delete_ssh_key(id)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)

    display_manager.display_success(f"Deleted SSH key '{id}'")
