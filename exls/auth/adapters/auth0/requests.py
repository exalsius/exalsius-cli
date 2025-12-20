from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt, StrictStr


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
