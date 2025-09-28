from typing import List

import typer
from exalsius_api_client.models.credentials import Credentials

from exalsius.config import AppConfig
from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.models import ServiceError
from exalsius.management.credentials.display import (
    TableCredentialsDisplayManager,
)
from exalsius.management.credentials.service import CredentialsService
from exalsius.utils import commons as utils

credentials_app = typer.Typer()


@credentials_app.callback(invoke_without_command=True)
def _root(  # pyright: ignore[reportUnusedFunction]
    ctx: typer.Context,
):
    """
    Manage credentials.
    """
    utils.help_if_no_subcommand(ctx)


@credentials_app.command("list", help="List all available credentials")
def list_credentials(ctx: typer.Context):
    """List all available credentials."""
    display_manager: TableCredentialsDisplayManager = TableCredentialsDisplayManager()

    config: AppConfig = utils.get_config_from_ctx(ctx)
    access_token: str = utils.get_access_token_from_ctx(ctx)

    service: CredentialsService = CredentialsService(config, access_token)

    try:
        credentials: List[Credentials] = service.list_credentials()
        display_manager.display_credentials(credentials)
    except ServiceError as e:
        display_manager.display_error(
            ErrorDTO(
                message=e.message,
                error_type=e.error_type,
                error_code=e.error_code,
            )
        )
        raise typer.Exit(1)
