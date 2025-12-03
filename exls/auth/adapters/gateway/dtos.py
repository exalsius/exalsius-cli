from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr


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


class TokenExpiryMetadataResponse(BaseModel):
    iat: datetime.datetime = Field(..., description="The issued at datetime")
    exp: datetime.datetime = Field(..., description="The expires at datetime")

    model_config = {"extra": "allow"}


class ValidatedAuthUserResponse(BaseModel):
    email: StrictStr = Field(..., description="The email")
    nickname: StrictStr = Field(..., description="The nickname")
    sub: StrictStr = Field(..., description="The subject")

    model_config = {"extra": "allow"}


class LoadedTokenDTO(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime.datetime = Field(..., description="The expiry datetime")
