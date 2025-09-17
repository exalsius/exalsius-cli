from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from exalsius.core.base.models import BaseRequestDTO

######################################
########### Exceptions ###############
######################################


class AuthenticationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"AuthenticationError: {self.message}"


class KeyringError(AuthenticationError):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self) -> str:
        return f"KeyringError: {self.message}"


class Auth0APIError(AuthenticationError):
    def __init__(self, error: str, status_code: int, error_description: str):
        super().__init__(error)
        self.error = error
        self.status_code = status_code
        self.error_description = error_description

    def __str__(self) -> str:
        return (
            f"Auth0APIError: {self.error} "
            f"(status code: {self.status_code}, "
            f"error description: {self.error_description})"
        )


class Auth0AuthenticationError(AuthenticationError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"Auth0AuthenticationError: {self.message}"


class NotLoggedInWarning(Warning):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


######################################
######## Request DTOs ################
######################################


class KeyringBaseRequestDTO(BaseRequestDTO):
    client_id: str = Field(..., description="The Auth0 client ID")


class ClearTokenFromKeyringRequestDTO(KeyringBaseRequestDTO):
    pass


class LoadTokenFromKeyringRequestDTO(KeyringBaseRequestDTO):
    pass


class StoreTokenOnKeyringRequestDTO(KeyringBaseRequestDTO):
    access_token: str = Field(..., description="The access token")
    expires_in: int = Field(..., description="The expiration time in seconds")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")


class Auth0BasePostRequestDTO(KeyringBaseRequestDTO):
    domain: str = Field(..., description="The URL to post to")


class Auth0RevokeTokenRequestDTO(Auth0BasePostRequestDTO):
    token: str = Field(..., description="The token")
    token_type_hint: str = Field(..., description="The token type hint")


class Auth0FetchDeviceCodeRequestDTO(Auth0BasePostRequestDTO):
    audience: str = Field(..., description="The Auth0 audience")
    scope: List[str] = Field(..., description="The Auth0 scope")
    algorithms: List[str] = Field(
        ..., description="The algorithms to use for authentication"
    )


class Auth0PollForAuthenticationRequestDTO(Auth0BasePostRequestDTO):
    device_code: str = Field(..., description="The device code")
    grant_type: str = Field(..., description="The grant type")
    poll_interval_seconds: int = Field(
        default=5, description="The interval in seconds to poll for authentication"
    )
    poll_timeout_seconds: int = Field(
        default=300, description="The timeout in seconds to poll for authentication"
    )
    retry_limit: int = Field(
        default=3,
        description="The number of times to retry authentication when an unexpected error occurs",
    )


class Auth0ValidateTokenRequestDTO(Auth0BasePostRequestDTO):
    id_token: str = Field(..., description="The ID token")


class Auth0RefreshTokenRequestDTO(Auth0BasePostRequestDTO):
    refresh_token: str = Field(..., description="The refresh token")
    scope: Optional[List[str]] = Field(
        default=None, description="The scope for reauthorization"
    )


######################################
######## Response DTOs ###############
######################################


class Auth0DeviceCodeAuthenticationDTO(BaseModel):
    verification_uri: str = Field(..., description="The verification URI")
    verification_uri_complete: str = Field(
        ..., description="The verification URI complete"
    )
    user_code: str = Field(..., description="The user code")
    device_code: str = Field(..., description="The device code")
    expires_in: int = Field(..., description="The expiration time in seconds")
    interval: int = Field(..., description="The interval in seconds")


class Auth0AuthenticationDTO(BaseModel):
    access_token: str = Field(..., description="The access token")
    id_token: str = Field(..., description="The ID token")
    scope: str = Field(..., description="The scope")
    token_type: str = Field(..., description="The token type")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")
    expires_in: int = Field(..., description="The expiration time in seconds")


class Auth0UserInfoDTO(BaseModel):
    # We can add more fields here if needed
    email: Optional[str] = Field(default=None, description="The email")
    sub: Optional[str] = Field(default=None, description="The subject")


class Auth0RevokeTokenStatusDTO(BaseModel):
    success: bool = Field(..., description="Whether the token was revoked successfully")


class LoadedTokenDTO(BaseModel):
    access_token: str = Field(..., description="The access token")
    expiry: datetime = Field(..., description="The expiry datetime")
    refresh_token: Optional[str] = Field(default=None, description="The refresh token")


class TokenKeyringStorageStatusDTO(BaseModel):
    success: bool = Field(..., description="Whether the token was stored successfully")
