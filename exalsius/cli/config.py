from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from filelock import FileLock
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

CFG_DIR = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser() / "exalsius"
CFG_FILE = CFG_DIR / "config.yaml"
POINTER_FILE = CFG_DIR / "current_profile"
LOCK_FILE = CFG_DIR / "config.lock"


class ConfigDefaultCluster(BaseSettings):
    id: str = Field(..., description="The ID of the workspace")
    name: Optional[str] = Field(default=None, description="The name of the workspace")


class Credentials(BaseSettings):
    username: str = Field(..., description="The username for authentication")
    password: str = Field(..., description="The password for authentication")


class AppConfig(BaseSettings):
    default_cluster: Optional[ConfigDefaultCluster] = Field(
        default=None, description="The default cluster"
    )
    credentials: Optional[Credentials] = Field(
        default=None, description="The user credentials"
    )
    profiles: dict[str, Any] = Field(
        default_factory=dict, description="Profile placeholder for future use"
    )

    model_config = SettingsConfigDict(
        env_prefix="EXLS_",
        env_nested_delimiter="__",
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
            ExalsiusYamlConfig(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


class ExalsiusYamlConfig(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]):
        """
        Initializes the AwsYamlConfig source.

        Args:
            settings_cls: The Pydantic settings class this source is for.
        """
        super().__init__(settings_cls)
        self.config = self._load_config()

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str] | None:
        """
        Retrieves a configuration value for a given field.

        Args:
            field: The field object from the Pydantic model.
            field_name: The name of the field.

        Returns:
            A tuple containing the value and the field name if found, otherwise None.
        """
        return self.config.get(field_name), field_name

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

        with FileLock(LOCK_FILE):
            with CFG_FILE.open() as f:
                return yaml.safe_load(f) or {}

    def __call__(self) -> dict[str, Any]:
        """
        Returns the loaded configuration.

        This method is called by Pydantic to get the configuration data from this source.

        Returns:
            The dictionary of configuration data.
        """
        return self.config


def load() -> AppConfig:
    return AppConfig()


def save(cfg: AppConfig) -> None:
    with FileLock(LOCK_FILE):
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        CFG_FILE.write_text(
            yaml.dump(cfg.model_dump(mode="json", exclude_defaults=True))
        )


def active_cluster(cli_arg_id: str | None = None) -> Optional[ConfigDefaultCluster]:
    # 1. CLI flag has highest precedence
    if cli_arg_id:
        return ConfigDefaultCluster(id=cli_arg_id)

    # 2. Config file / Env vars
    cfg = load()
    return cfg.default_cluster
