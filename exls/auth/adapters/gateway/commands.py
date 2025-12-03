import logging
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Optional

import jwt
import keyring
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exls.auth.adapters.gateway.dtos import (
    Auth0DeviceCodeResponse,
    Auth0TokenResponse,
    LoadedTokenDTO,
    TokenExpiryMetadataResponse,
    ValidatedAuthUserResponse,
)
from exls.auth.adapters.gateway.errors import Auth0TokenError, KeyringCommandError
from exls.auth.core.domain import (
    AuthenticationRequest,
    FetchDeviceCodeRequest,
    RefreshTokenRequest,
    RevokeTokenRequest,
    StoreTokenRequest,
    ValidateTokenRequest,
)
from exls.shared.adapters.gateway.deserializer import (
    DeserializationError,
    PydanticDeserializer,
)
from exls.shared.adapters.gateway.http.commands import (
    PostRequestWithoutResponseCommand,
    PostRequestWithResponseCommand,
)
from exls.shared.core.ports.command import BaseCommand


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"
    ID_TOKEN_KEY = "id_token"


class Auth0FetchDeviceCodeCommand(
    PostRequestWithResponseCommand[Auth0DeviceCodeResponse]
):
    def __init__(self, params: FetchDeviceCodeRequest):
        super().__init__(model=Auth0DeviceCodeResponse)
        self.params: FetchDeviceCodeRequest = params

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
    def __init__(self, params: AuthenticationRequest):
        super().__init__(model=Auth0TokenResponse)
        self.params: AuthenticationRequest = params

    def _get_url(self) -> str:
        return f"https://{self.params.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.params.client_id,
            "device_code": self.params.device_code,
            "grant_type": self.params.grant_type,
        }


class LoadTokenExpiryMetadataCommand(BaseCommand[TokenExpiryMetadataResponse]):
    def __init__(self, token: str):
        self.token: str = token
        self.deserializer: PydanticDeserializer[TokenExpiryMetadataResponse] = (
            PydanticDeserializer()
        )

    def execute(self) -> TokenExpiryMetadataResponse:
        try:
            decoded_token = jwt.decode(self.token, options={"verify_signature": False})
            return self.deserializer.deserialize(
                decoded_token, TokenExpiryMetadataResponse
            )
        except DeserializationError as e:
            raise Auth0TokenError(
                message=f"error while deserializing decoded token: {e}",
            ) from e
        except Exception as e:
            raise Auth0TokenError(
                message=f"unexpected error while validating token: {e}",
            ) from e


class ValidateTokenCommand(BaseCommand[ValidatedAuthUserResponse]):
    def __init__(
        self,
        params: ValidateTokenRequest,
        deserializer: PydanticDeserializer[
            ValidatedAuthUserResponse
        ] = PydanticDeserializer(),
    ):
        self.params: ValidateTokenRequest = params
        self.deserializer: PydanticDeserializer[ValidatedAuthUserResponse] = (
            deserializer
        )

    def execute(self) -> ValidatedAuthUserResponse:
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
            return self.deserializer.deserialize(resp, ValidatedAuthUserResponse)
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
    def __init__(self, params: StoreTokenRequest):
        self.params: StoreTokenRequest = params

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
                self.params.expiry.astimezone(timezone.utc).isoformat(),
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
                if expiry.tzinfo is None:
                    expiry = expiry.astimezone(timezone.utc)
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
    def __init__(self, params: RefreshTokenRequest):
        super().__init__(model=Auth0TokenResponse)
        self.params: RefreshTokenRequest = params

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
    def __init__(self, params: RevokeTokenRequest):
        self.params: RevokeTokenRequest = params

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
