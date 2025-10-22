from __future__ import annotations

import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr

from exls.auth.domain import (
    FetchDeviceCodeParams,
    PollForAuthenticationParams,
    RefreshTokenParams,
    RevokeTokenParams,
    Token,
    ValidateTokenParams,
)


class Auth0FetchDeviceCodeRequest(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    audience: StrictStr = Field(..., description="The audience")
    scope: List[StrictStr] = Field(..., description="The scope")
    algorithms: List[StrictStr] = Field(..., description="The algorithms")

    @classmethod
    def from_params(cls, params: FetchDeviceCodeParams) -> Auth0FetchDeviceCodeRequest:
        return cls(
            domain=params.domain,
            client_id=params.client_id,
            audience=params.audience,
            scope=params.scope,
            algorithms=params.algorithms,
        )


class Auth0AuthenticationRequest(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    device_code: StrictStr = Field(..., description="The device code")
    grant_type: StrictStr = Field(..., description="The grant type")
    poll_interval_seconds: PositiveInt = Field(
        ..., description="The interval in seconds"
    )
    poll_timeout_seconds: PositiveInt = Field(..., description="The timeout in seconds")
    retry_limit: PositiveInt = Field(
        ...,
        description="The number of times to retry authentication when an unexpected error occurs",
    )

    @classmethod
    def from_params(
        cls, params: PollForAuthenticationParams
    ) -> Auth0AuthenticationRequest:
        return cls(
            domain=params.domain,
            client_id=params.client_id,
            device_code=params.device_code,
            grant_type=params.grant_type,
            poll_interval_seconds=params.poll_interval_seconds,
            poll_timeout_seconds=params.poll_timeout_seconds,
            retry_limit=params.retry_limit,
        )


class Auth0ValidateTokenRequest(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    id_token: StrictStr = Field(..., description="The ID token")

    @classmethod
    def from_params(cls, params: ValidateTokenParams) -> Auth0ValidateTokenRequest:
        return cls(
            domain=params.domain,
            client_id=params.client_id,
            id_token=params.id_token,
        )


class StoreTokenOnKeyringRequest(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    expires_in: PositiveInt = Field(..., description="The expiration time in seconds")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime.datetime = Field(..., description="The expiry datetime")

    @classmethod
    def from_token(cls, token: Token) -> StoreTokenOnKeyringRequest:
        return cls(
            client_id=token.client_id,
            access_token=token.access_token,
            expires_in=token.expires_in,
            refresh_token=token.refresh_token,
            expiry=token.expiry,
        )


class Auth0RefreshTokenRequest(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    refresh_token: StrictStr = Field(..., description="The refresh token")
    scope: StrictStr = Field(..., description="The scope")

    @classmethod
    def from_params(cls, params: RefreshTokenParams) -> Auth0RefreshTokenRequest:
        return cls(
            domain=params.domain,
            client_id=params.client_id,
            refresh_token=params.refresh_token,
            scope=params.scope,
        )


class Auth0RevokeTokenRequest(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    token: StrictStr = Field(..., description="The token")

    @classmethod
    def from_params(cls, params: RevokeTokenParams) -> Auth0RevokeTokenRequest:
        return cls(
            domain=params.domain,
            client_id=params.client_id,
            token=params.token,
        )


class Auth0DeviceCodeResponse(BaseModel):
    device_code: str = Field(..., description="The device code")
    user_code: str = Field(..., description="The user code")
    verification_uri: str = Field(..., description="The verification URI")
    verification_uri_complete: str = Field(
        ..., description="The verification URI complete"
    )
    expires_in: int = Field(..., description="The expiration time in seconds")
    interval: int = Field(..., description="The interval in seconds")


class Auth0TokenResponse(BaseModel):
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    scope: StrictStr = Field(..., description="The scope")
    token_type: StrictStr = Field(..., description="The token type")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expires_in: PositiveInt = Field(..., description="The expiration time in seconds")


class Auth0HTTPErrorResponse(BaseModel):
    error: StrictStr = Field(..., description="The error")
    error_description: StrictStr = Field(..., description="The error description")

    model_config = {"extra": "allow"}


class Auth0UserResponse(BaseModel):
    email: StrictStr = Field(..., description="The email")
    sub: StrictStr = Field(..., description="The subject")

    model_config = {"extra": "allow"}


class LoadedTokenDTO(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime.datetime = Field(..., description="The expiry datetime")
