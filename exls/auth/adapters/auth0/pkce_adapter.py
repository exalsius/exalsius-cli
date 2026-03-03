"""Auth0 PKCE authentication adapter."""

import logging
import subprocess
import threading
from typing import Optional
from urllib.parse import urlencode

from exls.auth.adapters.auth0.callback_server import OAuthCallbackServer
from exls.auth.adapters.auth0.config import Auth0Config
from exls.auth.adapters.auth0.pkce_commands import ExchangeCodeForTokenCommand
from exls.auth.adapters.auth0.pkce_requests import PkceCodeExchangeRequest
from exls.auth.adapters.auth0.pkce_responses import PkceTokenResponse
from exls.auth.core.domain import PkceSession, Token
from exls.auth.core.pkce import (
    generate_code_challenge,
    generate_code_verifier,
    generate_nonce,
    generate_state,
)
from exls.auth.core.ports.operations import AuthError
from exls.auth.core.ports.pkce_operations import PkceOperations

logger = logging.getLogger(__name__)


class Auth0PkceAdapter(PkceOperations):
    """PKCE flow adapter for Auth0."""

    def __init__(self, config: Auth0Config):
        self._config = config
        self._server: Optional[OAuthCallbackServer] = None

    def generate_pkce_session(self, redirect_uri: str) -> PkceSession:
        return PkceSession(
            code_verifier=generate_code_verifier(
                self._config.pkce_code_verifier_length
            ),
            state=generate_state(),
            nonce=generate_nonce(),
            redirect_uri=redirect_uri,
        )

    def start_callback_server(self) -> int:
        self._server = OAuthCallbackServer(
            ports=[self._config.pkce_callback_port, 9000, 9001, 9002]
        )
        return self._server.start()

    def build_authorization_url(
        self, session: PkceSession, organization: Optional[str] = None
    ) -> str:
        params = {
            "response_type": "code",
            "client_id": self._config.client_id,
            "code_challenge": generate_code_challenge(session.code_verifier),
            "code_challenge_method": self._config.pkce_code_challenge_method,
            "redirect_uri": session.redirect_uri,
            "state": session.state,
            "nonce": session.nonce,
            "audience": self._config.audience,
            "scope": " ".join(self._config.scope),
        }
        if organization:
            params["organization"] = organization

        return f"https://{self._config.domain}/authorize?{urlencode(params)}"

    def open_browser(self, url: str) -> bool:
        def _open() -> None:
            try:
                subprocess.Popen(
                    ["xdg-open", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                import webbrowser

                webbrowser.open(url)

        try:
            thread = threading.Thread(target=_open, daemon=True)
            thread.start()
            thread.join(timeout=5)
            return True
        except Exception:
            logger.debug("Failed to open browser", exc_info=True)
            return False

    def wait_for_callback(
        self, session: PkceSession, timeout: Optional[int] = None
    ) -> str:
        if not self._server:
            raise AuthError("Callback server not started")

        timeout = timeout or self._config.pkce_callback_timeout_seconds
        result = self._server.wait_for_callback(timeout=timeout)

        if result.error:
            raise AuthError(
                f"Authentication failed: {result.error} - {result.error_description}"
            )
        if result.state != session.state:
            raise AuthError("State mismatch - possible CSRF attack")
        if not result.code:
            raise AuthError("No authorization code received")

        return result.code

    def exchange_code_for_token(self, code: str, session: PkceSession) -> Token:
        request = PkceCodeExchangeRequest(
            client_id=self._config.client_id,
            code=code,
            code_verifier=session.code_verifier,
            redirect_uri=session.redirect_uri,
            domain=self._config.domain,
        )
        response: PkceTokenResponse = ExchangeCodeForTokenCommand(request).execute()

        return Token(
            client_id=self._config.client_id,
            access_token=response.access_token,
            id_token=response.id_token,
            scope=response.scope,
            token_type=response.token_type,
            refresh_token=response.refresh_token,
            expires_in=response.expires_in,
        )

    def shutdown_callback_server(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server = None
