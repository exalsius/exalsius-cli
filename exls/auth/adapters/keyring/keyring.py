from exls.auth.adapters.keyring.commands import (
    ClearTokenFromKeyringCommand,
    LoadTokenFromKeyringCommand,
    StoreTokenOnKeyringCommand,
)
from exls.auth.core.domain import LoadedToken, Token
from exls.auth.core.ports.repository import TokenRepository, TokenRepositoryError
from exls.shared.core.ports.command import CommandError


class KeyringAdapter(TokenRepository):
    def store(self, token: Token) -> None:
        command: StoreTokenOnKeyringCommand = StoreTokenOnKeyringCommand(token=token)
        try:
            command.execute()
        except CommandError as e:
            raise TokenRepositoryError(f"Failed to store token: {str(e)}") from e

    def load(self, client_id: str) -> LoadedToken:
        command: LoadTokenFromKeyringCommand = LoadTokenFromKeyringCommand(
            client_id=client_id
        )
        try:
            return command.execute()
        except CommandError as e:
            raise TokenRepositoryError(f"Failed to load token: {str(e)}") from e

    def delete(self, client_id: str) -> None:
        command: ClearTokenFromKeyringCommand = ClearTokenFromKeyringCommand(
            client_id=client_id
        )
        try:
            command.execute()
        except CommandError as e:
            raise TokenRepositoryError(f"Failed to clear token: {str(e)}") from e
