from __future__ import annotations

import logging
import os
from pathlib import Path
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

logger = logging.getLogger("cli.config")

CFG_DIR = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser() / "exalsius"
CFG_FILE = CFG_DIR / "config.yaml"
CONFIG_LOCK_FILE = CFG_DIR / "config.lock"


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
        default=["openid", "audience", "profile", "email", "offline_access"],
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
    workspace_creation_polling: ConfigWorkspaceCreationPolling = Field(
        default=ConfigWorkspaceCreationPolling(),
        description="The workspace creation polling configuration",
    )

    model_config = SettingsConfigDict(
        env_prefix="EXLS_",
        env_nested_delimiter="__",
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


_APP_CONFIG: Optional[AppConfig] = None


def load_config(force_reload: bool = False) -> AppConfig:
    """Loads the application configuration, implemented as a singleton."""
    global _APP_CONFIG
    if _APP_CONFIG is None or force_reload:
        _APP_CONFIG = AppConfig()
    return _APP_CONFIG


def save_config(cfg: AppConfig) -> None:
    with FileLock(CONFIG_LOCK_FILE):
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        CFG_FILE.write_text(yaml.dump(cfg.model_dump(mode="json")))
