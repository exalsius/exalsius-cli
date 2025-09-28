import logging
from datetime import datetime, timedelta
from enum import StrEnum
from time import sleep, time
from typing import Any, Dict, Optional

import keyring
import requests
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exalsius.auth.models import (
    Auth0APIError,
    Auth0AuthenticationDTO,
    Auth0AuthenticationError,
    Auth0DeviceCodeAuthenticationDTO,
    Auth0FetchDeviceCodeRequestDTO,
    Auth0PollForAuthenticationRequestDTO,
    Auth0RefreshTokenRequestDTO,
    Auth0RevokeTokenRequestDTO,
    Auth0RevokeTokenStatusDTO,
    Auth0UserInfoDTO,
    Auth0ValidateTokenRequestDTO,
    ClearTokenFromKeyringRequestDTO,
    KeyringError,
    LoadedTokenDTO,
    LoadTokenFromKeyringRequestDTO,
    StoreTokenOnKeyringRequestDTO,
    TokenKeyringStorageStatusDTO,
)
from exalsius.core.base.commands import BaseCommand
from exalsius.core.commons.commands import PostRequestCommand


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"


class Auth0FetchDeviceCodeCommand(PostRequestCommand):
    def __init__(self, request: Auth0FetchDeviceCodeRequestDTO):
        self.request = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/device/code"

    def _get_payload(self) -> Dict[str, Any]:
        return {
            "client_id": self.request.client_id,
            "audience": self.request.audience,
            "scope": " ".join(self.request.scope),
        }

    def execute(self) -> Auth0DeviceCodeAuthenticationDTO:
        try:
            return self._execute_post_request(Auth0DeviceCodeAuthenticationDTO)
        except requests.HTTPError as e:
            raise Auth0APIError(
                error=e.response.json().get("error", "unknown error"),
                status_code=e.response.status_code,
                error_description=e.response.json().get("error_description", str(e)),
                response=e.response,
            ) from e


class Auth0PollForAuthenticationCommand(PostRequestCommand):
    def __init__(self, request: Auth0PollForAuthenticationRequestDTO):
        self.request = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "device_code": self.request.device_code,
            "grant_type": self.request.grant_type,
        }

    def _format_error(self, error: requests.HTTPError | Exception) -> str:
        if isinstance(error, requests.HTTPError):
            return f"HTTP error: {error.response.status_code} {error.response.json().get('error_description', error.response.json().get('error', str(error)))}"
        else:
            return f"unexpected error: {error}"

    def execute(self) -> Auth0AuthenticationDTO:
        start_time: float = time()
        retry_count: int = 0
        interval: int = self.request.poll_interval_seconds
        last_error: Optional[requests.HTTPError | Exception] = None
        while True:
            if retry_count >= self.request.retry_limit:
                raise Auth0AuthenticationError(
                    message=f"failed to authenticate after {self.request.retry_limit} retries. "
                    f"error: {self._format_error(last_error) if last_error else 'unknown error'}",
                    error_code=(
                        str(last_error.response.status_code)
                        if last_error and isinstance(last_error, requests.HTTPError)
                        else None
                    ),
                )

            sleep(interval)
            if time() - start_time > self.request.poll_timeout_seconds:
                raise TimeoutError("polling timed out.")
            try:
                result: Auth0AuthenticationDTO = super()._execute_post_request(
                    Auth0AuthenticationDTO
                )
                if result.access_token:
                    break
                else:
                    last_error = Exception("auth0 returned an empty access token.")
                    retry_count += 1
                    continue

            except requests.HTTPError as e:
                if e.response.status_code == 403:
                    if "error" in e.response.json():
                        error = e.response.json()["error"]
                        if error == "authorization_pending":
                            continue
                        else:
                            raise Auth0AuthenticationError(
                                message=f"failed to login. reason: {e.response.json().get('error_description', e.response.json().get('error', 'unknown error'))}",
                                error_code=e.response.json().get("error"),
                            )
                    else:
                        last_error = e
                        retry_count += 1
                        continue
                if e.response.status_code == 429:
                    if "error" in e.response.json():
                        error = e.response.json()["error"]
                        if error == "slow_down":
                            interval += 1
                            continue
                        else:
                            raise Auth0APIError(
                                e.response.json().get("error", "unknown error"),
                                e.response.status_code,
                                e.response.json().get("error_description", ""),
                                response=e.response,
                            )
                    else:
                        last_error = e
                        retry_count += 1
                        continue
                else:
                    last_error = e
                    retry_count += 1
                    continue
            except Exception as e:
                last_error = e
                retry_count += 1
                continue

        return result


class Auth0ValidateTokenCommand(BaseCommand):
    def __init__(self, request: Auth0ValidateTokenRequestDTO):
        self.request = request

    def execute(self) -> Auth0UserInfoDTO:
        jwks_url = f"https://{self.request.domain}/.well-known/jwks.json"
        issuer = f"https://{self.request.domain}/"
        sv = AsymmetricSignatureVerifier(jwks_url)
        tv = TokenVerifier(
            signature_verifier=sv, issuer=issuer, audience=self.request.client_id
        )
        try:
            resp: Dict[str, Any] = tv.verify(self.request.id_token)
            return self._deserialize(resp, Auth0UserInfoDTO)
        except TokenValidationError as e:
            raise Auth0AuthenticationError(
                message=f"failed to validate token: {e}",
            )
        except Exception as e:
            raise Auth0AuthenticationError(
                message=f"unexpected error while validating token: {e}",
            )


class StoreTokenOnKeyringCommand(BaseCommand):
    def __init__(self, request: StoreTokenOnKeyringRequestDTO):
        self.request = request

    def execute(self) -> TokenKeyringStorageStatusDTO:
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
            raise KeyringError(f"failed to store token on keyring: {e}")
        return TokenKeyringStorageStatusDTO(success=True)


class LoadTokenFromKeyringCommand(BaseCommand):
    def __init__(self, request: LoadTokenFromKeyringRequestDTO):
        self.request = request

    def execute(self) -> LoadedTokenDTO:
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
                return LoadedTokenDTO(
                    access_token=token,
                    expiry=expiry,
                    refresh_token=refresh_token,
                )
            else:
                raise KeyringError("failed to load token from keyring.")
        except Exception as e:
            raise KeyringError(f"failed to load token from keyring: {e}")


class Auth0RefreshTokenCommand(PostRequestCommand):
    def __init__(self, request: Auth0RefreshTokenRequestDTO):
        self.request = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.request.client_id,
            "refresh_token": self.request.refresh_token,
        }
        if self.request.scope:
            payload["scope"] = " ".join(self.request.scope)
        return payload

    def execute(self) -> Auth0AuthenticationDTO:
        return self._execute_post_request(Auth0AuthenticationDTO)


class Auth0RevokeTokenCommand(PostRequestCommand):
    def __init__(self, request: Auth0RevokeTokenRequestDTO):
        self.request = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/revoke"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "token": self.request.token,
            "token_type_hint": self.request.token_type_hint,
        }

    def execute(self) -> Auth0RevokeTokenStatusDTO:
        try:
            self._execute_post_request_empty_response()
        except requests.HTTPError as e:
            raise Auth0APIError(
                error=e.response.json().get("error", "unknown error"),
                status_code=e.response.status_code,
                error_description=e.response.json().get("error_description", ""),
                response=e.response,
            ) from e
        except Exception as e:
            raise Auth0AuthenticationError(
                message=f"unexpected error while revoking token: {e}",
            )
        return Auth0RevokeTokenStatusDTO(success=True)


class ClearTokenFromKeyringCommand(BaseCommand):
    def __init__(self, request: ClearTokenFromKeyringRequestDTO):
        self.request = request

    def _delete_token(self, token_type: KeyringKeys) -> bool:
        try:
            keyring.delete_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{token_type}",
            )

            return True
        except Exception as e:
            logging.warning(f"failed to delete token {token_type} from keyring: {e}")
            return False

    def execute(self) -> TokenKeyringStorageStatusDTO:
        success: bool = True
        success &= self._delete_token(KeyringKeys.ACCESS_TOKEN_KEY)
        success &= self._delete_token(KeyringKeys.EXPIRY_KEY)
        success &= self._delete_token(KeyringKeys.REFRESH_TOKEN_KEY)
        return TokenKeyringStorageStatusDTO(success=success)
