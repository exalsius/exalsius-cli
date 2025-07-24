import typer
from rich.console import Console

from exalsius.cli import utils
from exalsius.cli.auth.display import AuthDisplayManager
from exalsius.cli.auth.service import Auth0Service
from exalsius.cli.state import AppState
from exalsius.utils.theme import custom_theme


def login(
    ctx: typer.Context,
):
    """
    Login with your exalsius credentials.
    """
    app_state: AppState = utils.get_app_state_from_ctx(ctx)

    console: Console = Console(theme=custom_theme)
    display_manager: AuthDisplayManager = AuthDisplayManager(console)

    auth_service: Auth0Service = Auth0Service(config=app_state.config)

    # Start the device code authentication flow. Get the device code.
    resp, error = auth_service.fetch_device_code()
    if error:
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if resp is None:
        display_manager.display_authentication_error("Unexpected error.")
        raise typer.Exit(1)

    # Display the device code to the user. We need to wait for the user to use the url to authenticate.
    # We will poll for the authentication response.
    display_manager.display_device_code_polling_started(
        verification_uri_complete=resp.verification_uri_complete,
        user_code=resp.user_code,
    )

    # Poll for the authentication response.
    try:
        auth_resp, error = auth_service.poll_for_authentication(resp.device_code)
        if error:
            display_manager.display_authentication_error(error)
            raise typer.Exit(1)
        if auth_resp is None:
            display_manager.display_authentication_error("Unexpected error.")
            raise typer.Exit(1)
    except KeyboardInterrupt:
        display_manager.display_device_code_polling_cancelled()
        raise typer.Exit(0)

    # If the authentication is successful, validate the token.
    validate_resp, error = auth_service.validate_token(auth_resp.id_token)
    if error:
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if not validate_resp:
        display_manager.display_authentication_error("Unexpected error.")
        raise typer.Exit(1)

    # We store the token on the keyring to access it in subsequent CLI calls
    success, error = auth_service.store_token_on_keyring(
        token=auth_resp.access_token,
        expires_in=auth_resp.expires_in,
        refresh_token=auth_resp.refresh_token,
    )
    if error:
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if not success:
        display_manager.display_authentication_error(
            "unexpected error. Failed to store token on keyring."
        )
        raise typer.Exit(1)

    # Display the authentication success message.
    display_manager.display_authentication_success(
        validate_resp.email, validate_resp.sub
    )


def logout(ctx: typer.Context):
    """
    Logout from the exalsius API.
    """
    app_state: AppState = utils.get_app_state_from_ctx(ctx)

    console: Console = Console(theme=custom_theme)
    display_manager: AuthDisplayManager = AuthDisplayManager(console)

    auth_service: Auth0Service = Auth0Service(config=app_state.config)

    success, error = auth_service.logout()
    # This is hacky doe to the current interface to the auth service.
    # We will fix this in the future.
    if success and error:
        display_manager.display_not_logged_in()
        raise typer.Exit(0)
    if not success:
        display_manager.display_authentication_error(
            "unexpected error. Failed to logout."
        )
        raise typer.Exit(1)

    display_manager.display_logout_success()
