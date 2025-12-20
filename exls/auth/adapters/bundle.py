import typer

from exls.auth.adapters.auth0.auth0 import Auth0Adapter
from exls.auth.adapters.auth0.config import Auth0Config
from exls.auth.adapters.keyring.keyring import KeyringAdapter
from exls.auth.adapters.ui.display.display import IOAuthFacade
from exls.auth.core.ports.operations import AuthOperations
from exls.auth.core.ports.repository import TokenRepository
from exls.auth.core.service import AuthService
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory


class AuthBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_auth_service(self) -> AuthService:
        auth_config: Auth0Config = Auth0Config()
        auth_operations: AuthOperations = Auth0Adapter(config=auth_config)
        token_repository: TokenRepository = KeyringAdapter()
        return AuthService(
            auth_operations=auth_operations,
            token_repository=token_repository,
        )

    def get_io_facade(self) -> IOAuthFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOAuthFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )
