from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UnauthorizedError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Auth0FetchDeviceCodeRequest(BaseModel):
    domain: str = Field(..., description="The Auth0 domain")
    client_id: str = Field(..., description="The Auth0 client ID")
    audience: str = Field(..., description="The Auth0 audience")
    scope: List[str] = Field(..., description="The Auth0 scope")
    algorithms: List[str] = Field(
        ..., description="The algorithms to use for authentication"
    )


class Auth0FetchDeviceCodeResponse(BaseModel):
    verification_uri: str = Field(..., description="The verification URI")
    verification_uri_complete: str = Field(
        ..., description="The verification URI complete"
    )
    user_code: str = Field(..., description="The user code")
    device_code: str = Field(..., description="The device code")
    expires_in: int = Field(..., description="The expiration time in seconds")
    interval: int = Field(..., description="The interval in seconds")


class Auth0PollForAuthenticationRequest(BaseModel):
    domain: str = Field(..., description="The Auth0 domain")
    client_id: str = Field(..., description="The Auth0 client ID")
    device_code: str = Field(..., description="The device code")
    grant_type: str = Field(..., description="The grant type")


class Auth0AuthenticationResponse(BaseModel):
    access_token: str = Field(..., description="The access token")
    id_token: str = Field(..., description="The ID token")
    scope: str = Field(..., description="The scope")
    token_type: str = Field(..., description="The token type")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")
    expires_in: int = Field(..., description="The expiration time in seconds")


class Auth0ValidateTokenRequest(BaseModel):
    domain: str = Field(..., description="The Auth0 domain")
    client_id: str = Field(..., description="The Auth0 client ID")
    id_token: str = Field(..., description="The ID token")


class Auth0ValidateTokenResponse(BaseModel):
    # We can add more fields here if needed
    email: Optional[str] = Field(default=None, description="The email")
    sub: Optional[str] = Field(default=None, description="The subject")


class StoreTokenOnKeyringRequest(BaseModel):
    client_id: str = Field(..., description="The client ID")
    access_token: str = Field(..., description="The access token")
    expires_in: int = Field(..., description="The expiration time in seconds")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")


class LoadTokenFromKeyringRequest(BaseModel):
    client_id: str = Field(..., description="The client ID")


class LoadTokenFromKeyringResponse(BaseModel):
    access_token: str = Field(..., description="The access token")
    expiry: datetime = Field(..., description="The expiry datetime")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")


class Auth0RefreshTokenRequest(BaseModel):
    client_id: str = Field(..., description="The client ID")
    domain: str = Field(..., description="The Auth0 domain")
    refresh_token: str = Field(..., description="The refresh token")


class Auth0RevokeTokenRequest(BaseModel):
    client_id: str = Field(..., description="The client ID")
    domain: str = Field(..., description="The Auth0 domain")
    token: str = Field(..., description="The token")
    token_type_hint: str = Field(..., description="The token type hint")


class ClearTokenFromKeyringRequest(BaseModel):
    client_id: str = Field(..., description="The client ID")
