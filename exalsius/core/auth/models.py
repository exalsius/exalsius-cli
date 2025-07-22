from typing import List, Optional

from pydantic import BaseModel, Field


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


class Auth0PollForAuthenticationResponse(BaseModel):
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
