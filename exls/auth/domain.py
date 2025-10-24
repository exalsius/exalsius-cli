from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

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
        return int((self.expiry - datetime.now()).total_seconds())

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
        return datetime.now() + timedelta(seconds=self.expires_in)


class User(BaseModel):
    email: StrictStr = Field(..., description="The email")
    sub: StrictStr = Field(..., description="The subject")
