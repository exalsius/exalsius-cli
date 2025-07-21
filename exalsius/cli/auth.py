import logging
from typing import Optional, Tuple, cast

import typer

from exalsius.cli.utils import get_cli_state
from exalsius.core.models.auth import (
    AuthRequest,
    Credentials,
    Session,
    ValidateSessionRequest,
    load_credentials,
    load_session,
)
from exalsius.core.services.auth_service import AuthService, SessionService


class AuthenticationError(Exception):
    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(self.message)


def username_password_together_callback(
    ctx: typer.Context, password: Optional[str]
) -> Optional[str]:
    username = ctx.params.get("username")
    logging.debug(f"username: {username}, password: {password}")
    if (username is None) != (password is None):
        raise typer.BadParameter(
            "--username and --password must be supplied together (or omitted together)"
        )
    return password


def _try_to_authenticate(
    auth_service: AuthService, credentials: Credentials
) -> Tuple[Optional[Session], Optional[str]]:
    auth_request = AuthRequest(credentials=credentials)
    auth_response, error = auth_service.authenticate(auth_request)
    if error:
        return None, f"Authentication failed: {error}"
    if not auth_response or not auth_response.session:
        return None, "Authentication failed: invalid response from server."
    return auth_response.session, None


def get_session(
    username: Optional[str],
    password: Optional[str],
) -> Optional[Session]:
    """
    Authentication callback for protected commands.
    """
    auth_service = AuthService()
    session: Optional[Session] = None
    error_message: Optional[str] = None

    # Order of authentication attempts:
    # 1. CLI arguments (--username, --password)
    # 2. Local session file
    # 3. Local credentials file

    # 1. Attempt authentication with provided credentials
    if username and password:
        logging.debug(
            f"Attempting authentication with provided credentials username: {username}, password: xxxxx."
        )
        session, error_message = _try_to_authenticate(
            auth_service, Credentials(username=username, password=password)
        )

    # 2. If no session yet, try to load and validate an existing session
    if not session:
        loaded_session: Optional[Session] = load_session()
        if loaded_session:
            logging.debug("Found existing session, validating...")
            session_service = SessionService(loaded_session)
            req = ValidateSessionRequest(session=loaded_session)
            _, validation_error = session_service.validate_session(req)
            if not validation_error:
                logging.debug("Existing session is valid.")
                session = loaded_session
            else:
                logging.warning(f"Existing session is invalid: {validation_error}")

    # 3. If still no session, try to get a new one with stored credentials
    if not session:
        try:
            logging.debug("Attempting to load stored credentials.")
            stored_credentials: Credentials = load_credentials()
            logging.debug(
                f"Attempting to get new session with stored credentials {stored_credentials}."
            )
            session, error_message = _try_to_authenticate(
                auth_service, stored_credentials
            )
        except ValueError:
            logging.debug("No stored credentials found.")

    if not session:
        final_error = error_message or (
            "Authentication required. Please run 'exalsius login' or use "
            "--username and --password."
        )
        logging.error(final_error)
        return None

    logging.debug("Authentication successful.")
    return session


def get_current_session_or_fail(ctx: typer.Context) -> Session:
    """
    Get the current session from the context.
    This is a dependency that can be used in commands to get the current session.
    It will exit if the session is not available.
    """
    state = get_cli_state(ctx)
    if not state.session:
        # This should not happen if auth_callback is called before
        raise AuthenticationError(
            "Authentication required. Please run 'exalsius login'.", 1
        )
    return cast(Session, state.session)
