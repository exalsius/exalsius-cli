import logging
from datetime import datetime
from enum import StrEnum
from time import sleep, time
from typing import Any, Dict, Optional

import keyring
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exls.auth.dtos import (
    TokenKeyringStorageStatusDTO,
)
from exls.auth.gateway.dtos import (
    Auth0AuthenticationRequest,
    Auth0DeviceCodeResponse,
    Auth0FetchDeviceCodeRequest,
    Auth0HTTPErrorResponse,
    Auth0RefreshTokenRequest,
    Auth0RevokeTokenRequest,
    Auth0TokenResponse,
    Auth0UserResponse,
    Auth0ValidateTokenRequest,
    LoadedTokenDTO,
    StoreTokenOnKeyringRequest,
)
from exls.core.base.commands import BaseCommand, CommandError
from exls.core.commons.commands.http import (
    HTTPCommandError,
    PostRequestWithoutResponseCommand,
    PostRequestWithResponseCommand,
)
from exls.core.commons.deserializer import (
    DeserializationError,
    PydanticDeserializer,
)


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"


class Auth0Error(CommandError):
    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.message: str = message
        self.error_code: Optional[int] = error_code


class Auth0AuthentificationFailed(Auth0Error):
    pass


class Auth0TimeoutError(Auth0Error):
    pass


class Auth0TokenError(Auth0Error):
    pass


class Auth0AccessDeniedError(Auth0Error):
    pass


class KeyringError(CommandError):
    pass


class Auth0FetchDeviceCodeCommand(
    PostRequestWithResponseCommand[Auth0DeviceCodeResponse]
):
    def __init__(self, request: Auth0FetchDeviceCodeRequest):
        self.request: Auth0FetchDeviceCodeRequest = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/device/code"

    def _get_payload(self) -> Dict[str, Any]:
        return {
            "client_id": self.request.client_id,
            "audience": self.request.audience,
            "scope": " ".join(self.request.scope),
        }


class Auth0PollForAuthenticationCommand(
    PostRequestWithResponseCommand[Auth0TokenResponse]
):
    def __init__(self, request: Auth0AuthenticationRequest):
        self.request: Auth0AuthenticationRequest = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "device_code": self.request.device_code,
            "grant_type": self.request.grant_type,
        }

    def execute(self) -> Auth0TokenResponse:
        start_time_in_seconds: float = time()
        retry_count: int = 0
        interval: int = self.request.poll_interval_seconds
        last_error: Optional[Auth0Error] = None
        while True:
            if retry_count >= self.request.retry_limit:
                if last_error:
                    raise Auth0AuthentificationFailed(
                        message=f"failed to authenticate after {self.request.retry_limit} retries. "
                        f"error: {last_error.message}",
                        error_code=last_error.error_code,
                    )
                else:
                    raise Auth0Error(
                        message=f"failed to authenticate after {self.request.retry_limit} retries. "
                        f"unknown error",
                        error_code=None,
                    )

            sleep(interval)
            if time() - start_time_in_seconds > self.request.poll_timeout_seconds:
                raise Auth0TimeoutError(message="polling timed out")
            try:
                result: Auth0TokenResponse = super().execute()
                if result.access_token:
                    break
                else:
                    last_error = Auth0AuthentificationFailed(
                        message="auth0 returned an empty access token.",
                        error_code=None,
                    )
                    retry_count += 1
                    continue

            except HTTPCommandError as e:
                if e.status >= 400 and e.status < 500:
                    if e.error_body:
                        auth0_error: Auth0HTTPErrorResponse = (
                            Auth0HTTPErrorResponse.model_validate(e.error_body)
                        )
                        if auth0_error.error == "authorization_pending":
                            continue
                        elif auth0_error.error == "slow_down":
                            interval += 1
                            continue
                        elif auth0_error.error == "expired_token":
                            raise Auth0TokenError(
                                message=auth0_error.error_description,
                                error_code=e.status,
                            )
                        elif auth0_error.error == "access_denied":
                            raise Auth0AccessDeniedError(
                                message=auth0_error.error_description,
                                error_code=e.status,
                            )
                        else:
                            last_error = Auth0AuthentificationFailed(
                                message=auth0_error.error_description,
                                error_code=e.status,
                            )
                            retry_count += 1
                            continue
                else:
                    last_error = Auth0AuthentificationFailed(
                        message=e.message,
                        error_code=e.status,
                    )
                    retry_count += 1
                    continue
            except Exception as e:
                last_error = Auth0AuthentificationFailed(
                    message=f"unexpected error while waiting for authentication: {e}",
                    error_code=500,
                )
                retry_count += 1
                continue

        return result


class Auth0ValidateTokenCommand(BaseCommand[Auth0UserResponse]):
    def __init__(
        self,
        request: Auth0ValidateTokenRequest,
        deserializer: PydanticDeserializer[Auth0UserResponse] = PydanticDeserializer(),
    ):
        self.request: Auth0ValidateTokenRequest = request
        self.deserializer: PydanticDeserializer[Auth0UserResponse] = deserializer

    def execute(self) -> Auth0UserResponse:
        jwks_url: str = f"https://{self.request.domain}/.well-known/jwks.json"
        issuer: str = f"https://{self.request.domain}/"
        sv: AsymmetricSignatureVerifier = AsymmetricSignatureVerifier(jwks_url)
        tv: TokenVerifier = TokenVerifier(
            signature_verifier=sv,
            issuer=issuer,
            audience=self.request.client_id,
        )
        try:
            resp: Dict[str, Any] = tv.verify(self.request.id_token)
            return self.deserializer.deserialize(resp, Auth0UserResponse)
        except DeserializationError as e:
            raise Auth0TokenError(
                message=f"{e}",
            ) from e
        except TokenValidationError as e:
            raise Auth0TokenError(
                message=f"failed to validate token: {e}",
            ) from e
        except Exception as e:
            raise Auth0TokenError(
                message=f"unexpected error while validating token: {e}",
            ) from e


class StoreTokenOnKeyringCommand(BaseCommand[None]):
    def __init__(self, request: StoreTokenOnKeyringRequest):
        self.request: StoreTokenOnKeyringRequest = request

    def execute(self) -> None:
        try:
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
                self.request.access_token,
            )
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.request.client_id}_{KeyringKeys.EXPIRY_KEY}",
                self.request.expiry.isoformat(),
            )
            if self.request.refresh_token:
                keyring.set_password(
                    KeyringKeys.SERVICE_KEY,
                    f"{self.request.client_id}_{KeyringKeys.REFRESH_TOKEN_KEY}",
                    self.request.refresh_token,
                )
        except Exception as e:
            raise KeyringError(f"failed to store token on keyring: {e}") from e


class LoadTokenFromKeyringCommand(BaseCommand[LoadedTokenDTO]):
    def __init__(self, client_id: str):
        self.client_id: str = client_id

    def execute(self) -> LoadedTokenDTO:
        try:
            token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
            )
            expiry_str: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.EXPIRY_KEY}",
            )
            refresh_token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.REFRESH_TOKEN_KEY}",
            )
            if token and expiry_str:
                expiry: datetime = datetime.fromisoformat(expiry_str)
                return LoadedTokenDTO(
                    client_id=self.client_id,
                    access_token=token,
                    expiry=expiry,
                    refresh_token=refresh_token,
                )
            else:
                raise KeyringError(message="failed to load token from keyring.")
        except Exception as e:
            raise KeyringError(message=f"failed to load token from keyring: {e}") from e


class Auth0RefreshTokenCommand(PostRequestWithResponseCommand[Auth0TokenResponse]):
    def __init__(self, request: Auth0RefreshTokenRequest):
        self.request: Auth0RefreshTokenRequest = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.request.client_id,
            "refresh_token": self.request.refresh_token,
        }
        if self.request.scope:
            payload["scope"] = self.request.scope
        return payload


class Auth0RevokeTokenCommand(PostRequestWithoutResponseCommand):
    def __init__(self, request: Auth0RevokeTokenRequest):
        self.request: Auth0RevokeTokenRequest = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/revoke"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "token": self.request.token,
        }


class ClearTokenFromKeyringCommand(BaseCommand[TokenKeyringStorageStatusDTO]):
    def __init__(self, client_id: str):
        self.client_id: str = client_id

    def _delete_token(self, token_type: KeyringKeys) -> bool:
        try:
            keyring.delete_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{token_type}",
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
