import typer

from exls.auth.adapters.gateway.factory import (
    create_auth_gateway,
    create_token_storage_gateway,
)
from exls.auth.adapters.ui.display.display import IOAuthFacade
from exls.auth.core.ports import IAuthGateway, ITokenStorageGateway
from exls.auth.core.service import AuthService
from exls.config import AppConfig
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory


class AuthBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_auth_service(self, config: AppConfig) -> AuthService:
        auth_gateway: IAuthGateway = create_auth_gateway()
        token_storage_gateway: ITokenStorageGateway = create_token_storage_gateway()
        return AuthService(
            config=config,
            auth_gateway=auth_gateway,
            token_storage_gateway=token_storage_gateway,
        )

    def get_io_facade(self) -> IOAuthFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOAuthFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )
