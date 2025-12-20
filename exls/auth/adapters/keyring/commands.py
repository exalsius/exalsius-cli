import logging
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

import keyring

from exls.auth.core.domain import (
    LoadedToken,
    Token,
)
from exls.shared.core.ports.command import BaseCommand, CommandError


class KeyringCommandError(CommandError):
    pass


class KeyringKeys(StrEnum):
    SERVICE_KEY = "exalsius_cli"
    ACCESS_TOKEN_KEY = "access_token"
    EXPIRY_KEY = "expiry"
    REFRESH_TOKEN_KEY = "refresh_token"
    ID_TOKEN_KEY = "id_token"


class StoreTokenOnKeyringCommand(BaseCommand[None]):
    def __init__(self, token: Token):
        self.token: Token = token

    def execute(self) -> None:
        try:
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.token.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
                self.token.access_token,
            )
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.token.client_id}_{KeyringKeys.ID_TOKEN_KEY}",
                self.token.id_token,
            )
            keyring.set_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.token.client_id}_{KeyringKeys.EXPIRY_KEY}",
                self.token.expiry.astimezone(timezone.utc).isoformat(),
            )
            if self.token.refresh_token:
                keyring.set_password(
                    KeyringKeys.SERVICE_KEY,
                    f"{self.token.client_id}_{KeyringKeys.REFRESH_TOKEN_KEY}",
                    self.token.refresh_token,
                )
        except Exception as e:
            raise KeyringCommandError(f"failed to store token on keyring: {e}") from e


class LoadTokenFromKeyringCommand(BaseCommand[LoadedToken]):
    def __init__(self, client_id: str):
        self.client_id: str = client_id

    def execute(self) -> LoadedToken:
        try:
            token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.ACCESS_TOKEN_KEY}",
            )
            expiry_str: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.EXPIRY_KEY}",
            )
            refresh_token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.REFRESH_TOKEN_KEY}",
            )
            id_token: Optional[str] = keyring.get_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{KeyringKeys.ID_TOKEN_KEY}",
            )
            if token and expiry_str and id_token:
                expiry: datetime = datetime.fromisoformat(expiry_str)
                if expiry.tzinfo is None:
                    expiry = expiry.astimezone(timezone.utc)
                return LoadedToken(
                    client_id=self.client_id,
                    access_token=token,
                    id_token=id_token,
                    refresh_token=refresh_token,
                    expiry=expiry,
                )

            else:
                raise KeyringCommandError(message="failed to load token from keyring.")
        except Exception as e:
            raise KeyringCommandError(
                message=f"failed to load token from keyring: {e}"
            ) from e


class ClearTokenFromKeyringCommand(BaseCommand[bool]):
    def __init__(self, client_id: str):
        self.client_id: str = client_id

    def _delete_token(self, token_type: KeyringKeys) -> bool:
        try:
            keyring.delete_password(
                KeyringKeys.SERVICE_KEY,
                f"{self.client_id}_{token_type}",
            )

            return True
        except Exception as e:
            logging.warning(f"failed to delete token {token_type} from keyring: {e}")
            return False

    def execute(self) -> bool:
        success: bool = True
        success &= self._delete_token(KeyringKeys.ACCESS_TOKEN_KEY)
        success &= self._delete_token(KeyringKeys.EXPIRY_KEY)
        success &= self._delete_token(KeyringKeys.REFRESH_TOKEN_KEY)
        return success
