import copy
import logging

import typer

from exalsius.auth.display import AuthDisplayManager
from exalsius.auth.models import (
    Auth0AuthenticationDTO,
    Auth0UserInfoDTO,
    NotLoggedInWarning,
)
from exalsius.auth.service import Auth0Service
from exalsius.core.commons.models import ServiceError, ServiceWarning
from exalsius.state import AppState
from exalsius.utils import commons as utils

logger = logging.getLogger(__name__)


deployment_token_app = typer.Typer()


def _authorization_workflow(
    auth_service: Auth0Service,
    display_manager: AuthDisplayManager,
) -> tuple[Auth0AuthenticationDTO, Auth0UserInfoDTO]:
    # Start the device code authentication flow. Get the device code.
    logger.debug("Fetching device code.")
    try:
        resp = auth_service.fetch_device_code()
    except ServiceError as e:
        logger.error(f"Failed to fetch device code: {e.message}")
        display_manager.display_authentication_error(e.message)
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
        auth_resp = auth_service.poll_for_authentication(resp.device_code)
    except KeyboardInterrupt:
        logger.warning("User cancelled authentication polling.")
        display_manager.display_device_code_polling_cancelled()
        raise typer.Exit(0)
    logger.debug("Authentication successful.")

    # If the authentication is successful, validate the received ID token.
    logger.debug("Validating token.")
    try:
        validate_resp = auth_service.validate_token(auth_resp.id_token)
    except ServiceError as e:
        logger.error(f"Token validation failed: {e.message}")
        display_manager.display_authentication_error(e.message)
        raise typer.Exit(1)

    logger.debug("Token is valid.")
    return auth_resp, validate_resp


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

    display_manager: AuthDisplayManager = AuthDisplayManager()

    auth_service: Auth0Service = Auth0Service(config=app_state.config)

    auth_resp, validate_resp = _authorization_workflow(auth_service, display_manager)

    # Store the tokens on the system's keyring for future access.
    logger.debug("Storing token on keyring.")
    try:
        auth_service.store_token_on_keyring(
            token=auth_resp.access_token,
            expires_in=auth_resp.expires_in,
            refresh_token=auth_resp.refresh_token,
        )
    except ServiceError as e:
        logger.error(f"Failed to store token on keyring: {e.message}")
        display_manager.display_authentication_error(e.message)
        raise typer.Exit(1)

    logger.debug("Token stored successfully.")

    # Display the authentication success message to the user.
    logger.debug(f"Login successful for user {validate_resp.email}.")
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

    display_manager: AuthDisplayManager = AuthDisplayManager()

    auth_service: Auth0Service = Auth0Service(config=app_state.config)

    logger.debug("Attempting to log out.")
    try:
        auth_service.logout()
    except NotLoggedInWarning:
        display_manager.display_not_logged_in()
        raise typer.Exit(0)
    except ServiceWarning as w:
        logger.debug(str(w))
    except ServiceError as e:
        logger.error(f"Failed to log out: {e.message}")
        display_manager.display_authentication_error(e.message)
        raise typer.Exit(1)

    logger.debug("Logout successful.")
    display_manager.display_logout_success()


@deployment_token_app.command("get")
def get_deployment_token(
    ctx: typer.Context,
):
    """
    Requests a new access token and refresh token for deployment and displays the new tokens.

    The new tokens are displayed but not stored in the keyring.
    """
    logger.debug("Starting process of requesting deployment tokens.")
    original_app_state: AppState = utils.get_app_state_from_ctx(ctx)
    modified_app_state: AppState = copy.deepcopy(original_app_state)
    modified_app_state.config.auth0.client_id = (
        modified_app_state.config.auth0_node_agent.client_id
    )
    modified_app_state.config.auth0.scope = (
        modified_app_state.config.auth0_node_agent.scope
    )

    display_manager: AuthDisplayManager = AuthDisplayManager()

    auth_service: Auth0Service = Auth0Service(config=modified_app_state.config)

    auth_resp, validate_resp = _authorization_workflow(auth_service, display_manager)

    # Sanity check: If the refresh token is present, check if the scope can be used to escalate the scope.
    if auth_resp.refresh_token:
        auth_service.scope_escalation_check(
            refresh_token=auth_resp.refresh_token,
            current_scope=original_app_state.config.auth0_node_agent.scope,
            reference_scope=original_app_state.config.auth0.scope,
        )
    # Display the deployment token to the user.
    logger.debug(f"Deployment token request successful for user {validate_resp.email}.")
    display_manager.display_deployment_token_request_success(
        access_token=auth_resp.access_token,
    )
