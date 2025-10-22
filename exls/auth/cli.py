import logging

import typer

from exls.auth.display import TableAuthDisplayManager
from exls.auth.dtos import UserInfoDTO
from exls.auth.service import Auth0Service, NotLoggedInWarning, get_auth_service
from exls.config import AppConfig
from exls.core.base.display import ErrorDisplayModel
from exls.core.base.service import ServiceError, ServiceWarning
from exls.utils import commons as utils

logger = logging.getLogger(__name__)


def login(
    ctx: typer.Context,
):
    """
    Authenticates the user and stores the credentials for future use.

    This command initiates the device code authentication flow. The user is prompted
    to visit a URL and enter a code to authorize the device. The command polls
    for the authentication to complete. Upon success, the tokens are stored
    securely in the system's keyring for subsequent CLI calls.
    """
    config: AppConfig = utils.get_config_from_ctx(ctx)

    display_manager: TableAuthDisplayManager = TableAuthDisplayManager()

    auth_service: Auth0Service = get_auth_service(config)

    try:
        user: UserInfoDTO = auth_service.login()
        display_manager.display_success("Logged in successfully!")
        display_manager.display_user_info(user=user)
    except ServiceWarning as w:
        display_manager.display_info(str(w))
        raise typer.Exit(0)
    except KeyboardInterrupt:
        display_manager.display_info(
            "User cancelled authentication polling via Ctrl+C."
        )
        raise typer.Exit(0)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)


def logout(ctx: typer.Context):
    """
    Logs the user out by removing stored credentials.

    This command removes the user's authentication tokens from the system's
    keyring, effectively logging them out of the Exalsius CLI.
    """
    config: AppConfig = utils.get_config_from_ctx(ctx)

    display_manager: TableAuthDisplayManager = TableAuthDisplayManager()

    auth_service: Auth0Service = get_auth_service(config)

    try:
        auth_service.logout()
    except NotLoggedInWarning:
        display_manager.display_info("You are not logged in.")
        raise typer.Exit(0)
    except ServiceWarning as w:
        display_manager.display_info(str(w))
        raise typer.Exit(0)
    except ServiceError as e:
        display_manager.display_error(ErrorDisplayModel(message=str(e)))
        raise typer.Exit(1)

    display_manager.display_success("Logged out successfully")
