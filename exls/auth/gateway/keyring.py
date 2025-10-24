from exls.auth.domain import LoadedToken
from exls.auth.gateway.base import TokenStorageGateway
from exls.auth.gateway.commands import (
    ClearTokenFromKeyringCommand,
    LoadTokenFromKeyringCommand,
    StoreTokenOnKeyringCommand,
)
from exls.auth.gateway.dtos import LoadedTokenDTO, StoreTokenOnKeyringParams
from exls.auth.gateway.mappers import loaded_token_from_response


class KeyringTokenStorageGateway(TokenStorageGateway):
    def store_token(self, params: StoreTokenOnKeyringParams) -> None:
        command: StoreTokenOnKeyringCommand = StoreTokenOnKeyringCommand(params)
        command.execute()

    def load_token(self, client_id: str) -> LoadedToken:
        command: LoadTokenFromKeyringCommand = LoadTokenFromKeyringCommand(
            client_id=client_id
        )
        response: LoadedTokenDTO = command.execute()
        return loaded_token_from_response(client_id=client_id, response=response)

    def clear_token(self, client_id: str) -> None:
        command: ClearTokenFromKeyringCommand = ClearTokenFromKeyringCommand(
            client_id=client_id
        )
        command.execute()
