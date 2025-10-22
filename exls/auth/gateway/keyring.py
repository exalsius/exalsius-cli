from exls.auth.domain import LoadedToken, Token
from exls.auth.gateway.base import TokenStorageGateway
from exls.auth.gateway.commands import (
    ClearTokenFromKeyringCommand,
    LoadTokenFromKeyringCommand,
    StoreTokenOnKeyringCommand,
)
from exls.auth.gateway.dtos import LoadedTokenDTO, StoreTokenOnKeyringRequest


class KeyringTokenStorageGateway(TokenStorageGateway):
    def store_token(self, token: Token) -> None:
        request: StoreTokenOnKeyringRequest = StoreTokenOnKeyringRequest.from_token(
            token
        )
        command: StoreTokenOnKeyringCommand = StoreTokenOnKeyringCommand(request)
        command.execute()

    def load_token(self, client_id: str) -> LoadedToken:
        command: LoadTokenFromKeyringCommand = LoadTokenFromKeyringCommand(
            client_id=client_id
        )
        loaded_token: LoadedTokenDTO = command.execute()
        return LoadedToken.from_dto(loaded_token)

    def clear_token(self, loaded_token: LoadedToken) -> None:
        command: ClearTokenFromKeyringCommand = ClearTokenFromKeyringCommand(
            client_id=loaded_token.client_id
        )
        command.execute()
