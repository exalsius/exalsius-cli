import logging
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, Optional

import keyring
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exls.auth.gateway.dtos import (
    Auth0AuthenticationParams,
    Auth0DeviceCodeResponse,
    Auth0FetchDeviceCodeParams,
    Auth0RefreshTokenParams,
    Auth0RevokeTokenParams,
    Auth0TokenResponse,
    Auth0UserResponse,
    Auth0ValidateTokenParams,
    LoadedTokenDTO,
    StoreTokenOnKeyringParams,
)
from exls.auth.gateway.errors import Auth0TokenError, KeyringCommandError
from exls.core.base.commands import BaseCommand
from exls.core.commons.deserializer import (
    DeserializationError,
    PydanticDeserializer,
)
from exls.core.commons.gateways.commands.http import (
    PostRequestWithoutResponseCommand,
    PostRequestWithResponseCommand,
)


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"
    ID_TOKEN_KEY = "id_token"


class Auth0FetchDeviceCodeCommand(
    PostRequestWithResponseCommand[Auth0DeviceCodeResponse]
):
    def __init__(self, params: Auth0FetchDeviceCodeParams):
        super().__init__(model=Auth0DeviceCodeResponse)
        self.params: Auth0FetchDeviceCodeParams = params

    def _get_url(self) -> str:
        return f"https://{self.params.domain}/oauth/device/code"

    def _get_payload(self) -> Dict[str, Any]:
        return {
            "client_id": self.params.client_id,
            "audience": self.params.audience,
            "scope": " ".join(self.params.scope),
        }


class Auth0GetTokenFromDeviceCodeCommand(
    PostRequestWithResponseCommand[Auth0TokenResponse]
):
    def __init__(self, params: Auth0AuthenticationParams):
        super().__init__(model=Auth0TokenResponse)
        self.params: Auth0AuthenticationParams = params

    def _get_url(self) -> str:
        return f"https://{self.params.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.params.client_id,
            "device_code": self.params.device_code,
            "grant_type": self.params.grant_type,
        }


class Auth0ValidateTokenCommand(BaseCommand[Auth0UserResponse]):
    def __init__(
        self,
        params: Auth0ValidateTokenParams,
        deserializer: PydanticDeserializer[Auth0UserResponse] = PydanticDeserializer(),
    ):
        self.params: Auth0ValidateTokenParams = params
        self.deserializer: PydanticDeserializer[Auth0UserResponse] = deserializer

    def execute(self) -> Auth0UserResponse:
        jwks_url: str = f"https://{self.params.domain}/.well-known/jwks.json"
        issuer: str = f"https://{self.params.domain}/"
        sv: AsymmetricSignatureVerifier = AsymmetricSignatureVerifier(jwks_url)
        tv: TokenVerifier = TokenVerifier(
            signature_verifier=sv,
            issuer=issuer,
            audience=self.params.client_id,
            leeway=self.params.leeway,
        )
        try:
            resp: Dict[str, Any] = tv.verify(self.params.id_token)
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
    def __init__(self, params: StoreTokenOnKeyringParams):
        self.params: StoreTokenOnKeyringParams = params

    def execute(self) -> None:
        try:
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.params.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
                self.params.access_token,
            )
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.params.client_id}_{KeyringKeys.ID_TOKEN_KEY}",
                self.params.id_token,
            )
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.params.client_id}_{KeyringKeys.EXPIRY_KEY}",
                self.params.expiry.isoformat(),
            )
            if self.params.refresh_token:
                keyring.set_password(
                    KeyringKeys.SERVICE_KEY,
                    f"{self.params.client_id}_{KeyringKeys.REFRESH_TOKEN_KEY}",
                    self.params.refresh_token,
                )
        except Exception as e:
            raise KeyringCommandError(f"failed to store token on keyring: {e}") from e


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
            id_token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.ID_TOKEN_KEY}",
            )
            if token and expiry_str and id_token:
                expiry: datetime = datetime.fromisoformat(expiry_str)
                return LoadedTokenDTO(
                    client_id=self.client_id,
                    access_token=token,
                    id_token=id_token,
                    expiry=expiry,
                    refresh_token=refresh_token,
                )
            else:
                raise KeyringCommandError(message="failed to load token from keyring.")
        except Exception as e:
            raise KeyringCommandError(
                message=f"failed to load token from keyring: {e}"
            ) from e


class Auth0RefreshTokenCommand(PostRequestWithResponseCommand[Auth0TokenResponse]):
    def __init__(self, params: Auth0RefreshTokenParams):
        super().__init__(model=Auth0TokenResponse)
        self.params: Auth0RefreshTokenParams = params

    def _get_url(self) -> str:
        return f"https://{self.params.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.params.client_id,
            "refresh_token": self.params.refresh_token,
        }
        if self.params.scope:
            payload["scope"] = self.params.scope
        return payload


class Auth0RevokeTokenCommand(PostRequestWithoutResponseCommand):
    def __init__(self, params: Auth0RevokeTokenParams):
        self.params: Auth0RevokeTokenParams = params

    def _get_url(self) -> str:
        return f"https://{self.params.domain}/oauth/revoke"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.params.client_id,
            "token": self.params.token,
        }


class ClearTokenFromKeyringCommand(BaseCommand[bool]):
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

    def execute(self) -> bool:
        success: bool = True
        success &= self._delete_token(KeyringKeys.ACCESS_TOKEN_KEY)
        success &= self._delete_token(KeyringKeys.EXPIRY_KEY)
        success &= self._delete_token(KeyringKeys.REFRESH_TOKEN_KEY)
        return success
