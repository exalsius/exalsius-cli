from exls.auth.adapters.gateway.dtos import (
    Auth0DeviceCodeResponse,
    Auth0TokenResponse,
    LoadedTokenDTO,
    TokenExpiryMetadataResponse,
    ValidatedAuthUserResponse,
)
from exls.auth.core.domain import (
    DeviceCode,
    LoadedToken,
    Token,
    TokenExpiryMetadata,
    User,
)


def token_from_response(client_id: str, response: Auth0TokenResponse) -> Token:
    return Token(
        client_id=client_id,
        access_token=response.access_token,
        id_token=response.id_token,
        scope=response.scope,
        token_type=response.token_type,
        refresh_token=response.refresh_token,
        expires_in=response.expires_in,
    )


def device_code_from_response(response: Auth0DeviceCodeResponse) -> DeviceCode:
    return DeviceCode(
        verification_uri=response.verification_uri,
        verification_uri_complete=response.verification_uri_complete,
        user_code=response.user_code,
        device_code=response.device_code,
        expires_in=response.expires_in,
        interval=response.interval,
    )


def token_expiry_metadata_from_response(
    response: TokenExpiryMetadataResponse,
) -> TokenExpiryMetadata:
    return TokenExpiryMetadata(
        iat=response.iat,
        exp=response.exp,
    )


def user_from_response(response: ValidatedAuthUserResponse) -> User:
    return User(
        email=response.email,
        nickname=response.nickname,
        sub=response.sub,
    )


def loaded_token_from_response(client_id: str, response: LoadedTokenDTO) -> LoadedToken:
    return LoadedToken(
        client_id=client_id,
        access_token=response.access_token,
        id_token=response.id_token,
        refresh_token=response.refresh_token,
        expiry=response.expiry,
    )
