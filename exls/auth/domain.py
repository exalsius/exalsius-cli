from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr

from exls.auth.dtos import RefreshTokenRequestDTO
from exls.auth.gateway.dtos import (
    Auth0DeviceCodeResponse,
    Auth0TokenResponse,
    Auth0UserResponse,
    LoadedTokenDTO,
)
from exls.config import Auth0Config


class FetchDeviceCodeParams(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    domain: StrictStr = Field(..., description="The domain")
    audience: StrictStr = Field(..., description="The audience")
    scope: List[StrictStr] = Field(..., description="The scope")
    algorithms: List[StrictStr] = Field(
        ..., description="The algorithms to use for authentication"
    )

    @classmethod
    def from_config(cls, config: Auth0Config) -> FetchDeviceCodeParams:
        return cls(
            client_id=config.client_id,
            domain=config.domain,
            audience=config.audience,
            scope=config.scope,
            algorithms=config.algorithms,
        )


class PollForAuthenticationParams(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    device_code: StrictStr = Field(..., description="The device code")
    grant_type: StrictStr = Field(..., description="The grant type")
    poll_interval_seconds: PositiveInt = Field(
        ..., description="The interval in seconds to poll for authentication"
    )
    poll_timeout_seconds: PositiveInt = Field(
        ..., description="The timeout in seconds to poll for authentication"
    )
    retry_limit: PositiveInt = Field(
        ...,
        description="The number of times to retry authentication when an unexpected error occurs",
    )

    @classmethod
    def from_device_code_and_config(
        cls, device_code: DeviceCode, config: Auth0Config
    ) -> PollForAuthenticationParams:
        return cls(
            domain=config.domain,
            client_id=config.client_id,
            device_code=device_code.device_code,
            grant_type=config.device_code_grant_type,
            poll_interval_seconds=config.device_code_poll_interval_seconds,
            poll_timeout_seconds=config.device_code_poll_timeout_seconds,
            retry_limit=config.device_code_retry_limit,
        )


class ValidateTokenParams(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    id_token: StrictStr = Field(..., description="The ID token")

    @classmethod
    def from_token_and_config(
        cls, token: Token, config: Auth0Config
    ) -> ValidateTokenParams:
        return cls(
            domain=config.domain,
            client_id=config.client_id,
            id_token=token.id_token,
        )


class RefreshTokenParams(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    refresh_token: StrictStr = Field(..., description="The refresh token")
    scope: StrictStr = Field(..., description="The scope")

    @classmethod
    def from_token_and_config(
        cls, token: Token, config: Auth0Config
    ) -> RefreshTokenParams:
        if not token.refresh_token:
            raise ValueError("Refresh token is required")
        return cls(
            domain=config.domain,
            client_id=config.client_id,
            refresh_token=token.refresh_token,
            scope=token.scope,
        )

    @classmethod
    def from_refresh_token_request_and_config(
        cls, refresh_token_request: RefreshTokenRequestDTO, config: Auth0Config
    ) -> RefreshTokenParams:
        return cls(
            domain=config.domain,
            client_id=config.client_id,
            refresh_token=refresh_token_request.refresh_token,
            scope=" ".join(config.scope),
        )


class RevokeTokenParams(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")
    token: StrictStr = Field(..., description="The token")

    @classmethod
    def from_token_and_config(
        cls, token: StrictStr, config: Auth0Config
    ) -> RevokeTokenParams:
        return cls(
            domain=config.domain,
            client_id=config.client_id,
            token=token,
        )


class DeviceCode(BaseModel):
    verification_uri: StrictStr = Field(..., description="The verification URI")
    verification_uri_complete: StrictStr = Field(
        ..., description="The verification URI complete"
    )
    user_code: StrictStr = Field(..., description="The user code")
    device_code: StrictStr = Field(..., description="The device code")
    expires_in: PositiveInt = Field(..., description="The expiration time in seconds")
    interval: PositiveInt = Field(..., description="The interval in seconds")

    @classmethod
    def from_response(cls, response: Auth0DeviceCodeResponse) -> DeviceCode:
        return cls(
            verification_uri=response.verification_uri,
            verification_uri_complete=response.verification_uri_complete,
            user_code=response.user_code,
            device_code=response.device_code,
            expires_in=response.expires_in,
            interval=response.interval,
        )


class LoadedToken(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime = Field(..., description="The expiry datetime")

    @property
    def expires_in(self) -> int:
        return int((self.expiry - datetime.now()).total_seconds())

    @property
    def is_expired(self) -> bool:
        return self.expires_in <= 0

    @classmethod
    def from_dto(cls, dto: LoadedTokenDTO) -> LoadedToken:
        return cls(
            client_id=dto.client_id,
            access_token=dto.access_token,
            refresh_token=dto.refresh_token,
            expiry=dto.expiry,
        )


class Token(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    scope: StrictStr = Field(..., description="The scope")
    token_type: StrictStr = Field(..., description="The token type")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expires_in: PositiveInt = Field(..., description="The expiration time in seconds")
    expiry: datetime = Field(..., description="The expiry datetime")

    @classmethod
    def from_response(cls, client_id: StrictStr, response: Auth0TokenResponse) -> Token:
        return cls(
            client_id=client_id,
            access_token=response.access_token,
            id_token=response.id_token,
            scope=response.scope,
            token_type=response.token_type,
            refresh_token=response.refresh_token,
            expires_in=response.expires_in,
            expiry=datetime.now() + timedelta(seconds=response.expires_in),
        )


class User(BaseModel):
    email: StrictStr = Field(..., description="The email")
    sub: StrictStr = Field(..., description="The subject")

    @classmethod
    def from_response(cls, response: Auth0UserResponse) -> User:
        return cls(
            email=response.email,
            sub=response.sub,
        )
