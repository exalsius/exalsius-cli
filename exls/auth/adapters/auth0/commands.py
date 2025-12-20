from enum import StrEnum
from typing import Any, Dict

import jwt
from auth0.authentication.token_verifier import (
    AsymmetricSignatureVerifier,
    TokenVerifier,
)
from auth0.exceptions import TokenValidationError

from exls.auth.adapters.auth0.requests import (
    AuthenticationRequest,
    FetchDeviceCodeRequest,
    RefreshTokenRequest,
    RevokeTokenRequest,
    ValidateTokenRequest,
)
from exls.auth.adapters.auth0.responses import (
    Auth0DeviceCodeResponse,
    Auth0TokenResponse,
    TokenExpiryMetadataResponse,
    ValidatedAuthUserResponse,
)
from exls.shared.adapters.deserializer import (
    DeserializationError,
    PydanticDeserializer,
)
from exls.shared.adapters.http.commands import (
    PostRequestWithoutResponseCommand,
    PostRequestWithResponseCommand,
)
from exls.shared.core.ports.command import BaseCommand, CommandError


class Auth0CommandError(CommandError):
    pass


class Auth0TokenError(Auth0CommandError):
    pass


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"
    ID_TOKEN_KEY = "id_token"


class Auth0FetchDeviceCodeCommand(
    PostRequestWithResponseCommand[Auth0DeviceCodeResponse]
):
    def __init__(self, request: FetchDeviceCodeRequest):
        super().__init__(model=Auth0DeviceCodeResponse)
        self.request: FetchDeviceCodeRequest = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/device/code"

    def _get_payload(self) -> Dict[str, Any]:
        return {
            "client_id": self.request.client_id,
            "audience": self.request.audience,
            "scope": " ".join(self.request.scope),
            "algorithms": self.request.algorithms,
        }


class Auth0GetTokenFromDeviceCodeCommand(
    PostRequestWithResponseCommand[Auth0TokenResponse]
):
    def __init__(self, request: AuthenticationRequest):
        super().__init__(model=Auth0TokenResponse)
        self.request: AuthenticationRequest = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/token"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "device_code": self.request.device_code,
            "grant_type": self.request.grant_type,
        }


# This is not the exact right place for this command since it depends on
# jwt and not the auth0 specific logic. But its fine for now.
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
        request: ValidateTokenRequest,
        deserializer: PydanticDeserializer[
            ValidatedAuthUserResponse
        ] = PydanticDeserializer(),
    ):
        self.request: ValidateTokenRequest = request
        self.deserializer: PydanticDeserializer[ValidatedAuthUserResponse] = (
            deserializer
        )

    def execute(self) -> ValidatedAuthUserResponse:
        jwks_url: str = f"https://{self.request.domain}/.well-known/jwks.json"
        issuer: str = f"https://{self.request.domain}/"
        sv: AsymmetricSignatureVerifier = AsymmetricSignatureVerifier(jwks_url)
        tv: TokenVerifier = TokenVerifier(
            signature_verifier=sv,
            issuer=issuer,
            audience=self.request.client_id,
            leeway=self.request.leeway,
        )
        try:
            resp: Dict[str, Any] = tv.verify(self.request.id_token)
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


class Auth0RefreshTokenCommand(PostRequestWithResponseCommand[Auth0TokenResponse]):
    def __init__(self, request: RefreshTokenRequest):
        super().__init__(model=Auth0TokenResponse)
        self.request: RefreshTokenRequest = request

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
    def __init__(self, request: RevokeTokenRequest):
        super().__init__()
        self.request: RevokeTokenRequest = request

    def _get_url(self) -> str:
        return f"https://{self.request.domain}/oauth/revoke"

    def _get_payload(self) -> Dict[str, str]:
        return {
            "client_id": self.request.client_id,
            "token": self.request.token,
        }
