from exls.auth.adapters.gateway.auth0 import Auth0Gateway
from exls.auth.adapters.gateway.keyring import KeyringTokenStorageGateway
from exls.auth.core.ports import IAuthGateway, ITokenStorageGateway


def create_auth_gateway() -> IAuthGateway:
    return Auth0Gateway()


def create_token_storage_gateway() -> ITokenStorageGateway:
    return KeyringTokenStorageGateway()
