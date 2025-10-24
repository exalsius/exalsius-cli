from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from exls.auth.domain import DeviceCode, LoadedToken, Token, User

######################################
######## Request DTOs ################
######################################


class FetchDeviceCodeRequestDTO(BaseModel):
    client_id: str = Field(..., description="The client ID")
    domain: str = Field(..., description="The domain")
    audience: str = Field(..., description="The audience")
    scope: List[str] = Field(..., description="The scope")
    algorithms: List[str] = Field(
        ..., description="The algorithms to use for authentication"
    )


class KeyringRequestDTO(BaseModel):
    client_id: str = Field(..., description="The client ID")


class RevokeTokenRequestDTO(BaseModel):
    domain: str = Field(..., description="The URL to post to")
    token: str = Field(..., description="The token")
    token_type_hint: str = Field(..., description="The token type hint")


class PollForAuthenticationRequestDTO(BaseModel):
    device_code: str = Field(..., description="The device code")
    grant_type: str = Field(..., description="The grant type")
    poll_interval_seconds: int = Field(
        ..., description="The interval in seconds to poll for authentication"
    )
    poll_timeout_seconds: int = Field(
        ..., description="The timeout in seconds to poll for authentication"
    )
    retry_limit: int = Field(
        ...,
        description="The number of times to retry authentication when an unexpected error occurs",
    )


class ValidateTokenRequestDTO(BaseModel):
    id_token: str = Field(..., description="The ID token")


######################################
######## Response DTOs ###############
######################################


class DeviceCodeAuthenticationDTO(BaseModel):
    verification_uri: str = Field(..., description="The verification URI")
    verification_uri_complete: str = Field(
        ..., description="The verification URI complete"
    )
    user_code: str = Field(..., description="The user code")
    device_code: str = Field(..., description="The device code")
    expires_in: int = Field(..., description="The expiration time in seconds")

    @classmethod
    def from_domain(cls, device_code: DeviceCode) -> DeviceCodeAuthenticationDTO:
        return cls(
            verification_uri=device_code.verification_uri,
            verification_uri_complete=device_code.verification_uri_complete,
            user_code=device_code.user_code,
            device_code=device_code.device_code,
            expires_in=device_code.expires_in,
        )


class TokenDTO(BaseModel):
    access_token: str = Field(..., description="The access token")
    expiry: datetime = Field(..., description="The expiry datetime")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")


class AuthenticationDTO(BaseModel):
    access_token: str = Field(..., description="The access token")
    id_token: str = Field(..., description="The ID token")
    scope: str = Field(..., description="The scope")
    token_type: str = Field(..., description="The token type")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")
    expires_in: int = Field(..., description="The expiration time in seconds")

    @classmethod
    def from_domain(cls, token: Token) -> AuthenticationDTO:
        return cls(**token.model_dump())


class UserInfoDTO(BaseModel):
    # We can add more fields here if needed
    email: str = Field(..., description="The email")
    sub: str = Field(..., description="The subject")
    access_token: str = Field(..., description="The access token")

    @classmethod
    def from_token_domain(cls, user: User, token: Token) -> UserInfoDTO:
        return cls(
            email=user.email,
            sub=user.sub,
            access_token=token.access_token,
        )

    @classmethod
    def from_loaded_token_domain(
        cls, user: User, loaded_token: LoadedToken
    ) -> UserInfoDTO:
        return cls(
            email=user.email,
            sub=user.sub,
            access_token=loaded_token.access_token,
        )


class AcquiredAccessTokenDTO(BaseModel):
    access_token: str = Field(..., description="The access token")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")
    expiry: datetime = Field(..., description="The expiry datetime")

    @classmethod
    def from_loaded_token(cls, loaded_token: LoadedToken) -> AcquiredAccessTokenDTO:
        return cls(
            access_token=loaded_token.access_token,
            refresh_token=loaded_token.refresh_token,
            expiry=loaded_token.expiry,
        )
