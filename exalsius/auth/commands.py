import logging
from datetime import datetime, timedelta
from enum import StrEnum
from time import sleep, time
from typing import Any, Dict, Optional

import keyring
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exalsius.auth.models import (
    Auth0AuthenticationDTO,
    Auth0DeviceCodeAuthenticationDTO,
    Auth0FetchDeviceCodeRequestDTO,
    Auth0PollForAuthenticationRequestDTO,
    Auth0RefreshTokenRequestDTO,
    Auth0RevokeTokenRequestDTO,
    Auth0UserInfoDTO,
    Auth0ValidateTokenRequestDTO,
    ClearTokenFromKeyringRequestDTO,
    LoadedTokenDTO,
    LoadTokenFromKeyringRequestDTO,
    StoreTokenOnKeyringRequestDTO,
    TokenKeyringStorageStatusDTO,
)
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.exceptions import ExalsiusError
from exalsius.core.commons.commands import (
    APIError,
    PostRequestWithoutResponseCommand,
    PostRequestWithResponseCommand,
)
from exalsius.core.commons.deserializer import (
    DeserializationError,
    PydanticDeserializer,
)


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"


class Auth0Error(ExalsiusError):
    def __init__(self, message: str, error_code: Optional[int] = None):
        super().__init__(message)
        self.error_code: Optional[int] = error_code


class Auth0APIError(APIError):
    pass


class Auth0TimeoutError(Auth0Error):
    pass


class Auth0TokenError(Auth0Error):
    pass


class KeyringError(ExalsiusError):
    pass


class Auth0FetchDeviceCodeCommand(
    PostRequestWithResponseCommand[Auth0DeviceCodeAuthenticationDTO]
):
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


class Auth0PollForAuthenticationCommand(
    PostRequestWithResponseCommand[Auth0AuthenticationDTO]
):
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

    def execute(self) -> Auth0AuthenticationDTO:
        start_time: float = time()
        retry_count: int = 0
        interval: int = self.request.poll_interval_seconds
        last_error: Optional[APIError] = None
        while True:
            if retry_count >= self.request.retry_limit:
                raise Auth0Error(
                    message=f"failed to authenticate after {self.request.retry_limit} retries. "
                    f"error: {last_error.message if last_error else 'unknown error'}",
                    error_code=last_error.status_code if last_error else None,
                )

            sleep(interval)
            if time() - start_time > self.request.poll_timeout_seconds:
                raise Auth0TimeoutError("polling timed out")
            try:
                result: Auth0AuthenticationDTO = super().execute()
                if result.access_token:
                    break
                else:
                    last_error = APIError(
                        "auth0 returned an empty access token.",
                        self._get_url(),
                    )
                    retry_count += 1
                    continue

            except APIError as e:
                if e.status_code == 403:
                    if "authorization_pending" in e.message:
                        continue
                    else:
                        last_error = e
                        retry_count += 1
                        continue
                if e.status_code == 429:
                    if "slow_down" in e.message:
                        interval += 1
                        continue
                    else:
                        last_error = e
                        retry_count += 1
                        continue
                else:
                    last_error = e
                    retry_count += 1
                    continue
            except Exception as e:
                last_error = APIError(
                    message=f"unexpected error while polling for authentication: {e}",
                    endpoint=self._get_url(),
                )
                retry_count += 1
                continue

        return result


class Auth0ValidateTokenCommand(BaseCommand[Auth0UserInfoDTO]):
    def __init__(
        self,
        request: Auth0ValidateTokenRequestDTO,
        deserializer: PydanticDeserializer[Auth0UserInfoDTO] = PydanticDeserializer(),
    ):
        self.request: Auth0ValidateTokenRequestDTO = request
        self.deserializer: PydanticDeserializer[Auth0UserInfoDTO] = deserializer

    def execute(self) -> Auth0UserInfoDTO:
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
            return self.deserializer.deserialize(resp, Auth0UserInfoDTO)
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


class StoreTokenOnKeyringCommand(BaseCommand[TokenKeyringStorageStatusDTO]):
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
            raise KeyringError(f"failed to store token on keyring: {e}") from e
        return TokenKeyringStorageStatusDTO(success=True)


class LoadTokenFromKeyringCommand(BaseCommand[LoadedTokenDTO]):
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
            raise KeyringError(f"failed to load token from keyring: {e}") from e


class Auth0RefreshTokenCommand(PostRequestWithResponseCommand[Auth0AuthenticationDTO]):
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


class Auth0RevokeTokenCommand(PostRequestWithoutResponseCommand):
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


class ClearTokenFromKeyringCommand(BaseCommand[TokenKeyringStorageStatusDTO]):
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
