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
    """
    Authenticate and store credentials.

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
