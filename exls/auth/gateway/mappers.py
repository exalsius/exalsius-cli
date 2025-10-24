from exls.auth.domain import DeviceCode, LoadedToken, Token, User
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
from exls.config import Auth0Config


def auth0_fetch_device_code_params_from_config(
    config: Auth0Config,
) -> Auth0FetchDeviceCodeParams:
    return Auth0FetchDeviceCodeParams(
        client_id=config.client_id,
        domain=config.domain,
        audience=config.audience,
        scope=config.scope,
        algorithms=config.algorithms,
    )


def auth0_authentication_params_from_device_code_and_config(
    device_code: DeviceCode,
    config: Auth0Config,
) -> Auth0AuthenticationParams:
    return Auth0AuthenticationParams(
        client_id=config.client_id,
        domain=config.domain,
        device_code=device_code.device_code,
        grant_type=config.device_code_grant_type,
        poll_interval_seconds=config.device_code_poll_interval_seconds,
        poll_timeout_seconds=config.device_code_poll_timeout_seconds,
        retry_limit=config.device_code_retry_limit,
    )


def auth0_validate_token_params_from_access_token_and_config(
    id_token: str,
    config: Auth0Config,
) -> Auth0ValidateTokenParams:
    return Auth0ValidateTokenParams(
        client_id=config.client_id,
        domain=config.domain,
        id_token=id_token,
    )


def auth0_refresh_token_params_from_token_and_config(
    loaded_token: LoadedToken,
    config: Auth0Config,
) -> Auth0RefreshTokenParams:
    assert loaded_token.refresh_token is not None
    return Auth0RefreshTokenParams(
        client_id=config.client_id,
        domain=config.domain,
        refresh_token=loaded_token.refresh_token,
        scope=" ".join(config.scope) if config.scope else "",
    )


def auth0_revoke_token_params_from_token_and_config(
    loaded_token: LoadedToken,
    config: Auth0Config,
) -> Auth0RevokeTokenParams:
    return Auth0RevokeTokenParams(
        client_id=config.client_id,
        domain=config.domain,
        token=loaded_token.access_token,
    )


def store_token_params_from_token_and_config(
    token: Token,
    config: Auth0Config,
) -> StoreTokenOnKeyringParams:
    return StoreTokenOnKeyringParams(
        client_id=config.client_id,
        domain=config.domain,
        access_token=token.access_token,
        id_token=token.id_token,
        expires_in=token.expires_in,
        refresh_token=token.refresh_token,
        expiry=token.expiry,
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


def user_from_response(response: Auth0UserResponse) -> User:
    return User(
        email=response.email,
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
