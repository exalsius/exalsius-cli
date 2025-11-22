from exls.auth.adapters.gateway.commands import (
    ClearTokenFromKeyringCommand,
    LoadTokenFromKeyringCommand,
    StoreTokenOnKeyringCommand,
)
from exls.auth.adapters.gateway.dtos import LoadedTokenDTO
from exls.auth.adapters.gateway.mappers import loaded_token_from_response
from exls.auth.core.domain import LoadedToken, StoreTokenRequest
from exls.auth.core.ports import ITokenStorageGateway, TokenStorageError
from exls.shared.core.ports.command import CommandError


class KeyringTokenStorageGateway(ITokenStorageGateway):
    def store_token(self, request: StoreTokenRequest) -> None:
        command: StoreTokenOnKeyringCommand = StoreTokenOnKeyringCommand(request)
        try:
            command.execute()
        except CommandError as e:
            raise TokenStorageError(f"Failed to store token: {str(e)}") from e

    def load_token(self, client_id: str) -> LoadedToken:
        command: LoadTokenFromKeyringCommand = LoadTokenFromKeyringCommand(
            client_id=client_id
        )
        try:
            response: LoadedTokenDTO = command.execute()
            return loaded_token_from_response(client_id=client_id, response=response)
        except CommandError as e:
            raise TokenStorageError(f"Failed to load token: {str(e)}") from e

    def clear_token(self, client_id: str) -> None:
        command: ClearTokenFromKeyringCommand = ClearTokenFromKeyringCommand(
            client_id=client_id
        )
        try:
            command.execute()
        except CommandError as e:
            raise TokenStorageError(f"Failed to clear token: {str(e)}") from e
