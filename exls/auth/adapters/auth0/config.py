from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Auth0Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EXLS_AUTH0_",
        extra="ignore",
    )
    domain: str = Field(
        default="exalsius.eu.auth0.com",
        description="The Auth0 domain",
    )
    client_id: str = Field(
        default="kSbRc9MOnuMKMVLzhZYBo3xkTtk2KK7B", description="The Auth0 client ID"
    )
    audience: str = Field(
        default="https://api.exalsius.ai", description="The Auth0 audience"
    )
    scope: List[str] = Field(
        default=[
            "openid",
            "audience",
            "profile",
            "email",
            "offline_access",
            "userview",
            "nodeagent",
        ],
        description="The Auth0 scope",
    )
    algorithms: List[str] = Field(
        default=["RS256"], description="The algorithms to use for authentication"
    )
    device_code_grant_type: str = Field(
        default="urn:ietf:params:oauth:grant-type:device_code",
        description="The grant type to use for device code authentication",
    )
    token_expiry_buffer_minutes: int = Field(
        default=7,
        description="The buffer in minutes before the token expires. Default is 7 minutes.",
    )
    device_code_poll_interval_seconds: int = Field(
        default=5,
        description="The interval in seconds to poll for authentication",
    )
    device_code_poll_timeout_seconds: int = Field(
        default=300,
        description="The timeout in seconds to poll for authentication",
    )
    device_code_retry_limit: int = Field(
        default=3,
        description="The number of times to retry polling for authentication",
    )
    leeway: int = Field(
        default=3600,
        description="The leeway in seconds to validate the token",
    )
    pkce_code_challenge_method: str = Field(
        default="S256",
        description="PKCE code challenge method",
    )
    pkce_code_verifier_length: int = Field(
        default=64,
        description="PKCE code verifier length (43-128, RFC 7636)",
    )
    pkce_callback_timeout_seconds: int = Field(
        default=300,
        description="Timeout in seconds waiting for PKCE browser callback",
    )
    pkce_callback_port: int = Field(
        default=8999,
        description="Primary local port for PKCE callback server",
    )
    organization: Optional[str] = Field(
        default=None,
        description="Auth0 organization ID or name for org-scoped logins",
    )
