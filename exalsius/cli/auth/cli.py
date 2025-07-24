import logging

import typer
from rich.console import Console

from exalsius.cli import utils
from exalsius.cli.auth.display import AuthDisplayManager
from exalsius.cli.auth.service import Auth0Service
from exalsius.cli.state import AppState
from exalsius.utils.theme import custom_theme

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
    logger.debug("Starting login process.")
    app_state: AppState = utils.get_app_state_from_ctx(ctx)

    console: Console = Console(theme=custom_theme)
    display_manager: AuthDisplayManager = AuthDisplayManager(console)

    auth_service: Auth0Service = Auth0Service(config=app_state.config)

    # Start the device code authentication flow. Get the device code.
    logger.debug("Fetching device code.")
    resp, error = auth_service.fetch_device_code()
    if error:
        logger.error(f"Failed to fetch device code: {error}")
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if resp is None:
        logger.error("Failed to fetch device code: unexpected error.")
        display_manager.display_authentication_error("Unexpected error.")
        raise typer.Exit(1)

    # Display the device code to the user and wait for them to authenticate.
    # The CLI will poll for the authentication response.
    logger.debug("Device code received. Waiting for user authentication.")
    if utils.is_interactive():
        # In an interactive session, attempt to open the verification URL in the user's browser.
        if auth_service.open_browser_for_device_code_authentication(
            uri=resp.verification_uri_complete
        ):
            logger.debug("Opened browser for authentication.")
            display_manager.display_device_code_polling_started_via_browser(
                verification_uri_complete=resp.verification_uri_complete,
                user_code=resp.user_code,
            )
        else:
            logger.debug("Could not open browser. Displaying URL.")
            display_manager.display_device_code_polling_started(
                verification_uri_complete=resp.verification_uri_complete,
                user_code=resp.user_code,
            )
    else:
        # In a non-interactive session, display the URL and code for the user to handle manually.
        logger.debug("Non-interactive session. Displaying URL.")
        display_manager.display_device_code_polling_started(
            verification_uri_complete=resp.verification_uri_complete,
            user_code=resp.user_code,
        )

    # Poll for the authentication response from the authentication server.
    logger.debug("Polling for authentication.")
    try:
        auth_resp, error = auth_service.poll_for_authentication(resp.device_code)
        if error:
            logger.error(f"Authentication failed during polling: {error}")
            display_manager.display_authentication_error(error)
            raise typer.Exit(1)
        if auth_resp is None:
            logger.error("Authentication failed during polling: unexpected error.")
            display_manager.display_authentication_error("Unexpected error.")
            raise typer.Exit(1)
    except KeyboardInterrupt:
        logger.warning("User cancelled authentication polling.")
        display_manager.display_device_code_polling_cancelled()
        raise typer.Exit(0)
    logger.info("Authentication successful.")

    # If the authentication is successful, validate the received ID token.
    logger.debug("Validating token.")
    validate_resp, error = auth_service.validate_token(auth_resp.id_token)
    if error:
        logger.error(f"Token validation failed: {error}")
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if not validate_resp:
        logger.error("Token validation failed: unexpected error.")
        display_manager.display_authentication_error("Unexpected error.")
        raise typer.Exit(1)
    logger.debug("Token is valid.")

    # Store the tokens on the system's keyring for future access.
    logger.debug("Storing token on keyring.")
    success, error = auth_service.store_token_on_keyring(
        token=auth_resp.access_token,
        expires_in=auth_resp.expires_in,
        refresh_token=auth_resp.refresh_token,
    )
    if error:
        logger.error(f"Failed to store token on keyring: {error}")
        display_manager.display_authentication_error(error)
        raise typer.Exit(1)
    if not success:
        logger.error("Failed to store token on keyring: unexpected error.")
        display_manager.display_authentication_error(
            "unexpected error. Failed to store token on keyring."
        )
        raise typer.Exit(1)
    logger.debug("Token stored successfully.")

    # Display the authentication success message to the user.
    logger.info(f"Login successful for user {validate_resp.email}.")
    display_manager.display_authentication_success(
        validate_resp.email, validate_resp.sub
    )


def logout(ctx: typer.Context):
    """
    Logs the user out by removing stored credentials.

    This command removes the user's authentication tokens from the system's
    keyring, effectively logging them out of the Exalsius CLI.
    """
    logger.debug("Starting logout process.")
    app_state: AppState = utils.get_app_state_from_ctx(ctx)

    console: Console = Console(theme=custom_theme)
    display_manager: AuthDisplayManager = AuthDisplayManager(console)

    auth_service: Auth0Service = Auth0Service(config=app_state.config)

    logger.debug("Attempting to log out.")
    success, error = auth_service.logout()
    # The auth_service.logout() method has a specific return signature.
    # If the user is already logged out, it returns (True, "Some error message").
    # This checks for that specific case.
    if success and error:
        logger.info("User was not logged in.")
        display_manager.display_not_logged_in()
        raise typer.Exit(0)
    if not success:
        logger.error(f"Logout failed: {error}")
        display_manager.display_authentication_error(
            "unexpected error. Failed to logout."
        )
        raise typer.Exit(1)

    logger.info("Logout successful.")
    display_manager.display_logout_success()
