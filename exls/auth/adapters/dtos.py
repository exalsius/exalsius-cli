from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, StrictStr

from exls.auth.core.domain import AuthSession, DeviceCode, LoadedToken, Token


class DeviceCodeAuthenticationDTO(BaseModel):
    verification_uri: StrictStr = Field(..., description="The verification URI")
    verification_uri_complete: StrictStr = Field(
        ..., description="The verification URI complete"
    )
    user_code: StrictStr = Field(..., description="The user code")
    device_code: StrictStr = Field(..., description="The device code")
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
    access_token: StrictStr = Field(..., description="The access token")
    expiry: datetime = Field(..., description="The expiry datetime")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )


class AuthenticationDTO(BaseModel):
    access_token: StrictStr = Field(..., description="The access token")
    id_token: StrictStr = Field(..., description="The ID token")
    scope: StrictStr = Field(..., description="The scope")
    token_type: StrictStr = Field(..., description="The token type")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expires_in: int = Field(..., description="The expiration time in seconds")

    @classmethod
    def from_domain(cls, token: Token) -> AuthenticationDTO:
        return cls(**token.model_dump())


class UserInfoDTO(BaseModel):
    email: StrictStr = Field(..., description="The email")
    nickname: StrictStr = Field(..., description="The nickname")
    sub: StrictStr = Field(..., description="The subject")

    @classmethod
    def from_auth_session(cls, session: AuthSession) -> UserInfoDTO:
        return cls(
            email=session.user.email,
            nickname=session.user.nickname,
            sub=session.user.sub,
        )


class AcquiredAccessTokenDTO(BaseModel):
    access_token: StrictStr = Field(..., description="The access token")
    refresh_token: Optional[StrictStr] = Field(
        default=None, description="The refresh token"
    )
    expiry: datetime = Field(..., description="The expiry datetime")

    @classmethod
    def from_loaded_token(cls, loaded_token: LoadedToken) -> AcquiredAccessTokenDTO:
        return cls(
            access_token=loaded_token.access_token,
            refresh_token=loaded_token.refresh_token,
            expiry=loaded_token.expiry,
        )
