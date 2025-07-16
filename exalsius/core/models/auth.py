from __future__ import annotations

import logging
import os
from enum import StrEnum
from typing import Any, Optional

from filelock import FileLock
from pydantic import BaseModel, Field, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from exalsius.cli.config import CFG_DIR

logger = logging.getLogger("exls.cli.auth")

SESSION_LOCK_FILE = CFG_DIR / "session.lock"
SESSION_FILE = CFG_DIR / "session.json"

CREDENTIAL_ENV_VARS = ("EXLS_USERNAME", "EXLS_PASSWORD")
CREDENTIAL_ENV_VARS_ALIAS = ("EXALSIUS_USERNAME", "EXALSIUS_PASSWORD")


class CredentialsSource(StrEnum):
    CLI = "cli arguments"
    CREDENTIAL_ENV = "credential environment variables"
    REGULAR_ENV = "environment variables"
    FILE = "config file"
    DOTENV = "dotenv file"
    SECRETS_FILE = "secrets file"
    SESSION = "session"


class CredentialsSourceTagger(PydanticBaseSettingsSource):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        source: PydanticBaseSettingsSource,
        cred_source: CredentialsSource,
    ):
        super().__init__(settings_cls)
        self.source = source
        self.cred_source = cred_source
        self.field_name = "credentials"
        self.username_key = "username"
        self.password_key = "password"
        self.source_key = "source"

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        value, key, is_complex = self.source.get_field_value(field, field_name)
        if field_name == self.field_name and value and self.username_key in value:
            value.setdefault(self.source_key, self.cred_source)
        return value, key, is_complex

    def __call__(self) -> dict[str, Any]:
        data = self.source()
        if (
            self.field_name in data
            and isinstance(data[self.field_name], dict)
            and self.username_key in data[self.field_name]
        ):
            data[self.field_name].setdefault(self.source_key, self.cred_source)
        return data


class Credentials(BaseSettings):
    source: Optional[CredentialsSource] = Field(
        default=None, description="The source of the credentials"
    )
    username: Optional[str] = Field(
        default=None, description="The username for authentication"
    )
    password: Optional[str] = Field(
        default=None, description="The password for authentication"
    )

    def __repr_args__(self) -> list[tuple[str, Any]]:
        return [
            ("credentials source", self.source.value if self.source else None),
            ("username", self.username),
            ("password", "******"),
        ]

    model_config = SettingsConfigDict(
        env_prefix="EXLS_",
        env_nested_delimiter="__",
    )

    @model_validator(mode="after")
    def log_final_credentials_source(self) -> Credentials:
        logger.debug(
            f"Using credentials from source '{self.source}': username={self.username}, password=******"
        )
        return self

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
            CredentialsSourceTagger(
                settings_cls,
                CredentialsFromCredentialEnv(settings_cls),
                CredentialsSource.CREDENTIAL_ENV,
            ),
            CredentialsSourceTagger(
                settings_cls, env_settings, CredentialsSource.REGULAR_ENV
            ),
            CredentialsSourceTagger(
                settings_cls, dotenv_settings, CredentialsSource.DOTENV
            ),
            CredentialsSourceTagger(
                settings_cls, file_secret_settings, CredentialsSource.SECRETS_FILE
            ),
        )


class CredentialsFromCredentialEnv(PydanticBaseSettingsSource):
    def __call__(self) -> dict[str, Any]:
        username = os.getenv(CREDENTIAL_ENV_VARS[0]) or os.getenv(
            CREDENTIAL_ENV_VARS_ALIAS[0]
        )
        password = os.getenv(CREDENTIAL_ENV_VARS[1]) or os.getenv(
            CREDENTIAL_ENV_VARS_ALIAS[1]
        )

        if username and password:
            creds = {
                "username": username,
                "password": password,
                "source": CredentialsSource.CREDENTIAL_ENV,
            }
            return {"credentials": creds}
        return {}

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        return None, field_name, False


# TODO: This will be replaced by a session token in the future
class Session(BaseSettings):
    credentials: Optional[Credentials] = Field(
        default=None, description="The credentials for authentication"
    )


class AuthRequest(BaseModel):
    credentials: Credentials


class AuthResponse(BaseModel):
    session: Session


class ValidateSessionRequest(BaseModel):
    session: Session


class ValidateSessionResponse(BaseModel):
    valid: bool


class LogoutRequest(BaseModel):
    session: Session


class LogoutResponse(BaseModel):
    success: bool


def authenticate(
    username: Optional[str] = None, password: Optional[str] = None
) -> Session:
    if username and password:
        return Session(credentials=Credentials(username=username, password=password))
    else:
        credentials: Credentials = Credentials()
        if credentials.username and credentials.password:
            logger.debug(f"Using credentials {credentials}")
            return Session(credentials=credentials)
        else:
            raise ValueError("No credentials provided")


def load_credentials() -> Credentials:
    credentials: Credentials = Credentials()
    if credentials.username and credentials.password:
        return credentials
    else:
        raise ValueError("No credentials provided")


def load_session() -> Optional[Session]:
    with FileLock(SESSION_LOCK_FILE):
        if not SESSION_FILE.exists():
            return None
        return Session.model_validate_json(SESSION_FILE.read_text())


def save_session(session: Session) -> None:
    with FileLock(SESSION_LOCK_FILE):
        SESSION_FILE.write_text(session.model_dump_json())


def delete_session() -> None:
    with FileLock(SESSION_LOCK_FILE):
        SESSION_FILE.unlink(missing_ok=True)
