from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr


class DeviceCode(BaseModel):
    verification_uri: StrictStr = Field(..., description="The verification URI")
    verification_uri_complete: StrictStr = Field(
        ..., description="The verification URI complete"
    )
    user_code: StrictStr = Field(..., description="The user code")
    device_code: StrictStr = Field(..., description="The device code")
    expires_in: PositiveInt = Field(..., description="The expiration time in seconds")
    interval: PositiveInt = Field(..., description="The interval in seconds")


class LoadedToken(BaseModel):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime = Field(..., description="The expiry datetime")

    @property
    def expires_in(self) -> int:
        return int((self.expiry - datetime.now(timezone.utc)).total_seconds())

    @property
    def is_expired(self) -> bool:
        return self.expires_in <= 0


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

    @property
    def expiry(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)


class TokenExpiryMetadata(BaseModel):
    iat: datetime = Field(..., description="The issued at datetime")
    exp: datetime = Field(..., description="The expires at datetime")

    @property
    def expires_in(self) -> int:
        return int((self.exp - datetime.now(timezone.utc)).total_seconds())


class User(BaseModel):
    email: StrictStr = Field(..., description="The email")
    nickname: StrictStr = Field(..., description="The nickname")
    sub: StrictStr = Field(..., description="The subject")


class AuthSession(BaseModel):
    user: User
    token: LoadedToken


class BaseAuthRequest(BaseModel):
    domain: StrictStr = Field(..., description="The domain")
    client_id: StrictStr = Field(..., description="The client ID")


class FetchDeviceCodeRequest(BaseAuthRequest):
    audience: StrictStr = Field(..., description="The audience")
    scope: List[StrictStr] = Field(..., description="The scope")
    algorithms: List[StrictStr] = Field(..., description="The algorithms")


class AuthenticationRequest(BaseAuthRequest):
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


class ValidateTokenRequest(BaseAuthRequest):
    id_token: StrictStr = Field(..., description="The ID token")
    leeway: int = Field(..., description="The leeway in seconds")


class RefreshTokenRequest(BaseAuthRequest):
    refresh_token: StrictStr = Field(..., description="The refresh token")
    scope: StrictStr = Field(..., description="The scope")


class RevokeTokenRequest(BaseAuthRequest):
    token: StrictStr = Field(..., description="The token")


class StoreTokenRequest(BaseAuthRequest):
    client_id: StrictStr = Field(..., description="The client ID")
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    expires_in: PositiveInt = Field(..., description="The expiration time in seconds")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime = Field(..., description="The expiry datetime")
