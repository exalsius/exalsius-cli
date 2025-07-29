import logging
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Dict, Optional, Tuple

import keyring
import requests
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exalsius.auth.models import (
    Auth0AuthenticationResponse,
    Auth0FetchDeviceCodeRequest,
    Auth0FetchDeviceCodeResponse,
    Auth0PollForAuthenticationRequest,
    Auth0RefreshTokenRequest,
    Auth0RevokeTokenRequest,
    Auth0ValidateTokenRequest,
    Auth0ValidateTokenResponse,
    ClearTokenFromKeyringRequest,
    LoadTokenFromKeyringRequest,
    LoadTokenFromKeyringResponse,
    StoreTokenOnKeyringRequest,
)
from exalsius.base.operations import BaseOperation, BooleanOperation


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"


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
    ) -> Tuple[Optional[Auth0AuthenticationResponse], Optional[str]]:
        resp = requests.post(
            f"https://{self.request.domain}/oauth/token",
            data=self._get_payload(),
        )
        resp.raise_for_status()
        data = resp.json()

        return Auth0AuthenticationResponse(**data), None


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


class StoreTokenOnKeyringOperation(BooleanOperation):
    def __init__(self, request: StoreTokenOnKeyringRequest):
        self.request = request

    def execute(self) -> Tuple[bool, Optional[str]]:
        expiry = datetime.now() + timedelta(seconds=self.request.expires_in)
        try:
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
                self.request.access_token,
            )
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{KeyringKeys.EXPIRY_KEY}",
                expiry.isoformat(),
            )
            if self.request.refresh_token:
                keyring.set_password(
                    KeyringKeys.SERVICE_KEY,
                    f"{self.request.client_id}_{KeyringKeys.REFRESH_TOKEN_KEY}",
                    self.request.refresh_token,
                )
        except Exception as e:
            return False, f"Failed to store token on keyring: {e}"
        return True, None


class LoadTokenFromKeyringOperation(BaseOperation):
    def __init__(self, request: LoadTokenFromKeyringRequest):
        self.request = request

    def execute(self) -> Tuple[Optional[LoadTokenFromKeyringResponse], Optional[str]]:
        try:
            token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
            )
            expiry_str: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{KeyringKeys.EXPIRY_KEY}",
            )
            refresh_token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{KeyringKeys.REFRESH_TOKEN_KEY}",
            )
            if token and expiry_str:
                expiry: datetime = datetime.fromisoformat(expiry_str)
                return (
                    LoadTokenFromKeyringResponse(
                        access_token=token,
                        expiry=expiry,
                        refresh_token=refresh_token,
                    ),
                    None,
                )
            else:
                return None, None
        except Exception as e:
            return None, f"Failed to load token from keyring: {e}"


class Auth0RefreshTokenOperation(BaseOperation):
    def __init__(self, request: Auth0RefreshTokenRequest):
        self.request = request

    def _get_payload(self) -> Dict[str, str]:
        return {
            "grant_type": "refresh_token",
            "client_id": self.request.client_id,
            "refresh_token": self.request.refresh_token,
        }

    def execute(self) -> Tuple[Optional[Auth0AuthenticationResponse], Optional[str]]:
        response = requests.post(
            f"https://{self.request.domain}/oauth/token",
            data=self._get_payload(),
        )
        response.raise_for_status()
        data = response.json()
        return Auth0AuthenticationResponse(**data), None


class Auth0RevokeTokenOperation(BooleanOperation):
    def __init__(self, request: Auth0RevokeTokenRequest):
        self.request = request

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "token": self.request.token,
            "token_type_hint": self.request.token_type_hint,
        }

    def execute(self) -> Tuple[bool, Optional[str]]:
        payload = self._get_payload()
        response = requests.post(
            f"https://{self.request.domain}/oauth/revoke", data=payload
        )
        response.raise_for_status()
        return True, None


class ClearTokenFromKeyringOperation(BooleanOperation):
    def __init__(self, request: ClearTokenFromKeyringRequest):
        self.request = request

    def _delete_token(self, token_type: KeyringKeys) -> None:
        try:
            keyring.delete_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{token_type}",
            )
        except Exception as e:
            logging.warning(f"Failed to delete token {token_type} from keyring: {e}")

    def execute(self) -> Tuple[bool, Optional[str]]:
        self._delete_token(KeyringKeys.ACCESS_TOKEN_KEY)
        self._delete_token(KeyringKeys.EXPIRY_KEY)
        self._delete_token(KeyringKeys.REFRESH_TOKEN_KEY)
        return True, None
