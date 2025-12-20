from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Auth0Config(BaseSettings):
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
