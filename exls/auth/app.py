import json
import logging
from typing import Optional

import typer

from exls.auth.adapters.bundle import AuthBundle
from exls.auth.adapters.ui.display.display import IOAuthFacade
from exls.auth.adapters.ui.display.render import USER_VIEW
from exls.auth.core.domain import (
    AuthFlowType,
    LoginFlowState,
    PkceLoginState,
)
from exls.auth.core.ports.operations import AuthError
from exls.auth.core.ports.repository import TokenRepositoryError
from exls.auth.core.service import AuthService, NotLoggedInWarning, PkceTimeoutError
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.adapters.ui.utils import get_app_state_from_ctx, get_config_from_ctx
from exls.shared.core.exceptions import ServiceError, ServiceWarning

logger = logging.getLogger(__name__)


def _get_bundle(ctx: typer.Context) -> AuthBundle:
    """Helper to instantiate the AuthBundle from the context."""
    return AuthBundle(get_config_from_ctx(ctx), get_app_state_from_ctx(ctx))


def _display_flow_state(
    io_facade: IOAuthFacade,
    state: LoginFlowState,
    output_format: OutputFormat,
) -> None:
    """Render the intermediate login state to the user."""
    if isinstance(state, PkceLoginState):
        io_facade.display_pkce_browser_opening(state.auth_url, output_format)
    else:
        io_facade.display_auth_poling(device_code=state.device_code)


def login(
    ctx: typer.Context,
    auth_flow: Optional[AuthFlowType] = typer.Option(
        None,
        "--auth-flow",
        help="Authentication flow: pkce, device_code, auto (default: auto-detect)",
    ),
    organization: Optional[str] = typer.Option(
        None,
        "--organization",
        help="Auth0 organization ID or name for org-scoped logins",
    ),
):
    """Authenticate and store credentials

    Auto-detects PKCE (browser) or Device Code (headless) based on environment.
    Use --auth-flow to override.
    """
    bundle = _get_bundle(ctx)
    io_facade: IOAuthFacade = bundle.get_io_facade()
    auth_service: AuthService = bundle.get_auth_service(auth_flow_override=auth_flow)

    try:
        state = auth_service.initiate_login(organization=organization)
        _display_flow_state(io_facade, state, bundle.message_output_format)

        try:
            auth_session = auth_service.complete_login(state)
        except PkceTimeoutError:
            io_facade.display_pkce_timeout_with_fallback(bundle.message_output_format)
            fallback_state = auth_service.initiate_login(
                force_device_code=True, organization=organization
            )
            _display_flow_state(io_facade, fallback_state, bundle.message_output_format)
            auth_session = auth_service.complete_login(fallback_state)

        io_facade.display_success_message(
            f"Welcome, {auth_session.user.nickname}!",
            output_format=bundle.message_output_format,
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
    """Log out and remove stored credentials

    Removes authentication tokens from the system's keyring.
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


def get_token(ctx: typer.Context):
    """Print the current access token

    Writes the access token to stdout so it can be captured, for example:

        curl -H "Authorization: Bearer $(exls get-token)" https://api.exalsius.ai/...

    The token is refreshed automatically if it has expired. With --format json
    the output is {"access_token": "<token>"}; otherwise the bare token is
    printed. Diagnostics are written to stderr and, on any failure, nothing is
    written to stdout and the command exits non-zero.
    """
    bundle = _get_bundle(ctx)
    auth_service: AuthService = bundle.get_auth_service()

    try:
        auth_session = auth_service.acquire_access_token()
    except NotLoggedInWarning:
        typer.echo("You are not logged in. Please log in.", err=True)
        raise typer.Exit(1)
    except ServiceError as e:
        typer.echo(
            f"Failed to acquire access token. Please log in again. Error: {str(e)}",
            err=True,
        )
        raise typer.Exit(1)

    access_token: str = auth_session.token.access_token
    if bundle.object_output_format == OutputFormat.JSON:
        typer.echo(json.dumps({"access_token": access_token}))
    else:
        typer.echo(access_token)
