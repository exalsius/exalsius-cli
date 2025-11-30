from __future__ import annotations

import logging
from typing import Any, List, Optional

import yaml
from filelock import FileLock
from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from exls.defaults import (
    CFG_DIR,
    CFG_FILE,
    CONFIG_ENV_NESTED_DELIMITER,
    CONFIG_ENV_PREFIX,
    CONFIG_LOCK_FILE,
)
from exls.shared.adapters.ui.output.values import OutputFormat

logger = logging.getLogger("cli.config")


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


class Auth0NodeAgentConfig(BaseSettings):
    client_id: str = Field(
        default="faXh6VlIgMpS3HwowrxrksooFiNHBvQg",
        description="The Auth0 client ID for the node agent",
    )
    scope: List[str] = Field(
        default=["openid", "offline_access", "nodeagent"],
        description="The Auth0 scope for the node agent",
    )


class ConfigWorkspaceCreationPolling(BaseSettings):
    timeout_seconds: int = Field(
        default=120,
        description="The timeout in seconds to poll for workspace creation",
    )
    polling_interval_seconds: int = Field(
        default=5,
        description="The interval in seconds to poll for workspace creation",
    )


class AppConfig(BaseSettings):
    backend_host: str = Field(
        default="https://api.exalsius.ai",
        description="The backend host",
    )
    auth0: Auth0Config = Field(
        default=Auth0Config(), description="The Auth0 configuration"
    )
    auth0_node_agent: Auth0NodeAgentConfig = Field(
        default=Auth0NodeAgentConfig(),
        description="The Auth0 configuration for the node agent (includes client ID and scope)",
    )
    workspace_creation_polling: ConfigWorkspaceCreationPolling = Field(
        default=ConfigWorkspaceCreationPolling(),
        description="The workspace creation polling configuration",
    )
    default_message_output_format: OutputFormat = Field(
        default=OutputFormat.TEXT,
        description="The default output format for messages",
    )
    default_object_output_format: OutputFormat = Field(
        default=OutputFormat.TABLE,
        description="The default output format for objects",
    )

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX,
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            ExalsiusYamlConfig(settings_cls),
        )


class ExalsiusYamlConfig(PydanticBaseSettingsSource):
    def __call__(self) -> dict[str, Any]:
        """
        Returns the loaded configuration.

        This method is called by Pydantic to get the configuration data from this source.

        Returns:
            The dictionary of configuration data.
        """
        return self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """
        Loads and merges YAML files from the AWS plugin's config directory.

        Supports both .yml and .yaml file extensions. YAML files are merged with
        a simple update, meaning keys in later-loaded files will overwrite those
        from earlier ones. Files are processed in alphabetical order by filename.
        The entire merged configuration is placed under an 'aws' key.

        Returns:
            A dictionary containing the merged configuration under the 'aws' key.
        """
        if not CFG_FILE.exists():
            return {}

        with FileLock(CONFIG_LOCK_FILE):
            with CFG_FILE.open() as f:
                return yaml.safe_load(f) or {}

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        return None, field_name, False


__app_config: Optional[AppConfig] = None


def load_config(force_reload: bool = False) -> AppConfig:
    """Loads the application configuration, implemented as a singleton."""
    global __app_config
    if __app_config is None or force_reload:
        __app_config = AppConfig()
    return __app_config


def save_config(cfg: AppConfig) -> None:
    with FileLock(CONFIG_LOCK_FILE):
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        CFG_FILE.write_text(yaml.dump(cfg.model_dump(mode="json")))
