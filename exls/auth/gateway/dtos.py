from __future__ import annotations

import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr


class Auth0BaseParams(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")


class Auth0FetchDeviceCodeParams(Auth0BaseParams):
    audience: StrictStr = Field(..., description="The audience")
    scope: List[StrictStr] = Field(..., description="The scope")
    algorithms: List[StrictStr] = Field(..., description="The algorithms")


class Auth0AuthenticationParams(Auth0BaseParams):
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


class Auth0ValidateTokenParams(Auth0BaseParams):
    id_token: StrictStr = Field(..., description="The ID token")


class Auth0RefreshTokenParams(Auth0BaseParams):
    refresh_token: StrictStr = Field(..., description="The refresh token")
    scope: StrictStr = Field(..., description="The scope")


class Auth0RevokeTokenParams(Auth0BaseParams):
    token: StrictStr = Field(..., description="The token")


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


class StoreTokenOnKeyringParams(Auth0BaseParams):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    expires_in: PositiveInt = Field(..., description="The expiration time in seconds")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime.datetime = Field(..., description="The expiry datetime")


class LoadedTokenDTO(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime.datetime = Field(..., description="The expiry datetime")
