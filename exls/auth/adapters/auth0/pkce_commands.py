"""HTTP commands for PKCE flow."""

from typing import Any, Dict

from exls.auth.adapters.auth0.pkce_requests import PkceCodeExchangeRequest
from exls.auth.adapters.auth0.pkce_responses import PkceTokenResponse
from exls.shared.adapters.http.commands import PostRequestWithResponseCommand


class ExchangeCodeForTokenCommand(PostRequestWithResponseCommand[PkceTokenResponse]):
    """Exchange PKCE authorization code for tokens via POST to /oauth/token."""

    def __init__(self, request: PkceCodeExchangeRequest):
        super().__init__(model=PkceTokenResponse)
        self.request = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, Any]:
        return {
            "client_id": self.request.client_id,
            "code": self.request.code,
            "code_verifier": self.request.code_verifier,
            "redirect_uri": self.request.redirect_uri,
            "grant_type": self.request.grant_type,
        }
