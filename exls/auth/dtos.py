from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from exls.auth.domain import DeviceCode, LoadedToken, Token, User

######################################
########### Exceptions ###############
######################################


class AuthenticationError(Exception):
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message: str = message
        self.error_code: Optional[str] = error_code


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


class RefreshTokenRequestDTO(BaseModel):
    refresh_token: str = Field(..., description="The refresh token")


######################################
######## Response DTOs ###############
######################################


class DeviceCodeAuthenticationDTO(BaseModel):
    verification_uri: str = Field(..., description="The verification URI")
    verification_uri_complete: str = Field(
        ..., description="The verification URI complete"
    )
    user_code: str = Field(..., description="The user code")
    expires_in: int = Field(..., description="The expiration time in seconds")

    @classmethod
    def from_domain(cls, device_code: DeviceCode):
        return cls(
            verification_uri=device_code.verification_uri,
            verification_uri_complete=device_code.verification_uri_complete,
            user_code=device_code.user_code,
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
    def from_domain(cls, token: Token):
        return cls(**token.model_dump())


class UserInfoDTO(BaseModel):
    # We can add more fields here if needed
    email: str = Field(..., description="The email")
    sub: str = Field(..., description="The subject")
    access_token: str = Field(..., description="The access token")

    @classmethod
    def from_domain(cls, user: User, token: Token):
        return cls(
            email=user.email,
            sub=user.sub,
            access_token=token.access_token,
        )


class AcquiredAccessTokenDTO(BaseModel):
    access_token: str = Field(..., description="The access token")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")
    expiry: datetime = Field(..., description="The expiry datetime")

    @classmethod
    def from_loaded_token(cls, loaded_token: LoadedToken):
        return cls(
            access_token=loaded_token.access_token,
            refresh_token=loaded_token.refresh_token,
            expiry=loaded_token.expiry,
        )


class TokenKeyringStorageStatusDTO(BaseModel):
    success: bool = Field(..., description="Whether the token was stored successfully")


class LoadedTokenDTO(BaseModel):
    client_id: str = Field(..., description="The client ID")
    access_token: str = Field(..., description="The access token")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")
    expiry: datetime = Field(..., description="The expiry datetime")

    @classmethod
    def from_loaded_token(cls, loaded_token: LoadedToken):
        return cls(
            client_id=loaded_token.client_id,
            access_token=loaded_token.access_token,
            refresh_token=loaded_token.refresh_token,
            expiry=loaded_token.expiry,
        )
