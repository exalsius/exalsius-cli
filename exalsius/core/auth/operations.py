from typing import Any, Dict, Optional, Tuple

import requests
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exalsius.core.auth.models import (
    Auth0FetchDeviceCodeRequest,
    Auth0FetchDeviceCodeResponse,
    Auth0PollForAuthenticationRequest,
    Auth0PollForAuthenticationResponse,
    Auth0ValidateTokenRequest,
    Auth0ValidateTokenResponse,
)
from exalsius.core.operations.base import BaseOperation


class Auth0FetchDeviceCodeOperation(BaseOperation):
    def __init__(self, request: Auth0FetchDeviceCodeRequest):
        self.request = request

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "audience": self.request.audience,
            "scope": " ".join(self.request.scope),
        }

    def execute(self) -> Tuple[Optional[Auth0FetchDeviceCodeResponse], Optional[str]]:
        response = requests.post(
            f"https://{self.request.domain}/oauth/device/code",
            data=self._get_payload(),
        )
        response.raise_for_status()
        data = response.json()

        return Auth0FetchDeviceCodeResponse(**data), None


class Auth0PollForAuthenticationOperation(BaseOperation):
    def __init__(self, request: Auth0PollForAuthenticationRequest):
        self.request = request

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "device_code": self.request.device_code,
            "grant_type": self.request.grant_type,
        }

    def execute(
        self,
    ) -> Tuple[Optional[Auth0PollForAuthenticationResponse], Optional[str]]:
        response = requests.post(
            f"https://{self.request.domain}/oauth/token",
            data=self._get_payload(),
        )
        response.raise_for_status()
        data = response.json()

        return Auth0PollForAuthenticationResponse(**data), None


class Auth0ValidateTokenOperation(BaseOperation):
    def __init__(self, request: Auth0ValidateTokenRequest):
        self.request = request

    def execute(self) -> Tuple[Optional[Auth0ValidateTokenResponse], Optional[str]]:
        jwks_url = f"https://{self.request.domain}/.well-known/jwks.json"
        issuer = f"https://{self.request.domain}/"
        sv = AsymmetricSignatureVerifier(jwks_url)
        tv = TokenVerifier(
            signature_verifier=sv, issuer=issuer, audience=self.request.client_id
        )
        try:
            resp: Dict[str, Any] = tv.verify(self.request.id_token)
            return Auth0ValidateTokenResponse(**resp), None
        except TokenValidationError as e:
            return None, f"TokenValidationError: {e}"
        except Exception as e:
            return None, f"Unexpected error: {e}"
