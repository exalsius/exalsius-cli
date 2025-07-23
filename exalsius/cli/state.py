from typing import Optional

from pydantic import BaseModel, Field

from exalsius.cli import config as cli_config


class AppState(BaseModel):
    """
    Base state object that holds shared configuration for the CLI application.

    This class serves as a container for the application configuration that gets
    passed down to all sub-commands through the Typer context object.
    """

    config: cli_config.AppConfig = Field(
        default_factory=cli_config.load_config,
        description="Application configuration loaded from config files and environment variables",
    )

    access_token: Optional[str] = Field(
        default=None,
        description="The access token",
    )
