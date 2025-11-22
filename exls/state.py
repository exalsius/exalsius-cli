from typing import Optional

from pydantic import BaseModel, Field

from exls import config as cli_config
from exls.shared.adapters.ui.display.values import OutputFormat


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

    message_output_format: Optional[OutputFormat] = Field(
        default=None,
        description=f"The output format to use for the CLI ({', '.join([f.value for f in OutputFormat])}).",
    )
    object_output_format: Optional[OutputFormat] = Field(
        default=None,
        description=f"The output format to use for the CLI ({', '.join([f.value for f in OutputFormat])}).",
    )
