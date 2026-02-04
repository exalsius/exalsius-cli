import logging

import typer

from exls.auth.adapters.bundle import AuthBundle
from exls.auth.adapters.ui.display.display import IOAuthFacade
from exls.auth.adapters.ui.display.render import USER_VIEW
from exls.auth.core.domain import AuthSession, DeviceCode
from exls.auth.core.ports.operations import AuthError
from exls.auth.core.ports.repository import TokenRepositoryError
from exls.auth.core.service import AuthService, NotLoggedInWarning
from exls.shared.adapters.ui.utils import get_app_state_from_ctx, get_config_from_ctx
from exls.shared.core.exceptions import ServiceError, ServiceWarning

logger = logging.getLogger(__name__)


def _get_bundle(ctx: typer.Context) -> AuthBundle:
    """Helper to instantiate the AuthBundle from the context."""
    return AuthBundle(get_config_from_ctx(ctx), get_app_state_from_ctx(ctx))


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
    bundle = _get_bundle(ctx)
    io_facade: IOAuthFacade = bundle.get_io_facade()
    auth_service: AuthService = bundle.get_auth_service()

    try:
        device_code: DeviceCode = auth_service.initiate_device_code_login()

        io_facade.display_auth_poling(device_code=device_code)

        auth_session: AuthSession = auth_service.poll_for_authentication(
            device_code=device_code
        )

        io_facade.display_success_message(
            "Logged in successfully!", output_format=bundle.message_output_format
        )
        io_facade.display_data(
            auth_session.user,
            output_format=bundle.object_output_format,
            view_context=USER_VIEW,
        )
    except ServiceWarning as w:
        io_facade.display_info_message(
            str(w), output_format=bundle.message_output_format
        )
        raise typer.Exit(0)
    except (ServiceError, AuthError, TokenRepositoryError) as e:
        io_facade.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)


def logout(ctx: typer.Context):
    """
    Logs the user out by removing stored credentials.

    This command removes the user's authentication tokens from the system's
    keyring, effectively logging them out of the Exalsius CLI.
    """
    bundle = _get_bundle(ctx)
    io_facade: IOAuthFacade = bundle.get_io_facade()
    auth_service: AuthService = bundle.get_auth_service()

    try:
        auth_service.logout()
    except NotLoggedInWarning:
        io_facade.display_info_message(
            "You are not logged in.", output_format=bundle.message_output_format
        )
        raise typer.Exit(0)
    except ServiceWarning as w:
        io_facade.display_info_message(
            str(w), output_format=bundle.message_output_format
        )
        raise typer.Exit(0)
    except (ServiceError, AuthError, TokenRepositoryError) as e:
        io_facade.display_error_message(
            str(e), output_format=bundle.message_output_format
        )
        raise typer.Exit(1)

    io_facade.display_success_message(
        "Logged out successfully", output_format=bundle.message_output_format
    )
