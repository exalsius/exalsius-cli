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
from exls.management.types.credentials.display import (
    TableCredentialsDisplayManager,
)
from exls.management.types.credentials.dtos import (
    CredentialsDTO,
    ListCredentialsRequestDTO,
)
from exls.management.types.credentials.service import (
    CredentialsService,
    get_credentials_service,
)

credentials_app = typer.Typer()


def _get_credentials_service(ctx: typer.Context) -> CredentialsService:
    config: AppConfig = get_config_from_ctx(ctx)
    access_token: str = get_access_token_from_ctx(ctx)
    return get_credentials_service(config, access_token)


@credentials_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage credentials.
    """
    help_if_no_subcommand(ctx)


@credentials_app.command("list", help="List all available credentials")
def list_credentials(ctx: typer.Context):
    """List all available credentials."""
    display_manager = TableCredentialsDisplayManager()
    service: CredentialsService = _get_credentials_service(ctx)

    try:
        credentials: List[CredentialsDTO] = service.list_credentials(
            ListCredentialsRequestDTO()
        )
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_credentials(credentials=credentials)
