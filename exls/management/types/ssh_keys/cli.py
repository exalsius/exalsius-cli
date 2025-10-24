from pathlib import Path
from typing import List

import typer

from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError
from exls.core.commons.service import (
    get_access_token_from_ctx,
    get_config_from_ctx,
    help_if_no_subcommand,
)
from exls.management.types.ssh_keys.display import (
    TableSshKeysDisplayManager,
)
from exls.management.types.ssh_keys.dtos import (
    AddSshKeyRequestDTO,
    ListSshKeysRequestDTO,
    SshKeyDTO,
)
from exls.management.types.ssh_keys.service import (
    SshKeysService,
    get_ssh_keys_service,
)

ssh_keys_app = typer.Typer()


def _get_ssh_keys_service(ctx: typer.Context) -> SshKeysService:
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)
    return get_ssh_keys_service(config, access_token)


@ssh_keys_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage SSH keys management.
    """
    help_if_no_subcommand(ctx)


@ssh_keys_app.command("list", help="List all available SSH keys")
def list_ssh_keys(
    ctx: typer.Context,
):
    """List all available SSH keys."""
    display_manager = TableSshKeysDisplayManager()
    service = _get_ssh_keys_service(ctx)

    try:
        ssh_keys: List[SshKeyDTO] = service.list_ssh_keys(ListSshKeysRequestDTO())
        display_manager.display_ssh_keys(ssh_keys=ssh_keys)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
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
    display_manager = TableSshKeysDisplayManager()
    service = _get_ssh_keys_service(ctx)

    try:
        request = AddSshKeyRequestDTO(name=name, key_path=key_path)
        ssh_key_id: str = service.add_ssh_key(request)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Added SSH key '{ssh_key_id}' from {key_path}")


@ssh_keys_app.command("delete", help="Delete an SSH key")
def delete_ssh_key(
    ctx: typer.Context,
    ssh_key_id: str = typer.Argument(..., help="ID of the SSH key to delete"),
):
    """Delete an SSH key from the management cluster."""
    display_manager = TableSshKeysDisplayManager()
    service = _get_ssh_keys_service(ctx)
    try:
        service.delete_ssh_key(ssh_key_id)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success(f"Deleted SSH key '{ssh_key_id}'")
