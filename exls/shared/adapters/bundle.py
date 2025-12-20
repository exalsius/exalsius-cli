from abc import ABC

import typer
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration

from exls.config import AppConfig
from exls.shared.adapters.file.adapters import StringFileIOAdapter
from exls.shared.adapters.ui.facade.interaction import IOBaseModelFacade
from exls.shared.adapters.ui.factory import IOFactory
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.adapters.ui.utils import (
    get_access_token_from_ctx,
    get_config_from_ctx,
    get_message_output_format_from_ctx,
    get_object_output_format_from_ctx,
)
from exls.shared.core.crypto import CryptoService


class BaseBundle(ABC):
    def __init__(self, ctx: typer.Context):
        self._ctx: typer.Context = ctx

    @property
    def config(self) -> AppConfig:
        return get_config_from_ctx(self._ctx)

    @property
    def access_token(self) -> str:
        return get_access_token_from_ctx(self._ctx)

    @property
    def message_output_format(self) -> OutputFormat:
        return (
            get_message_output_format_from_ctx(self._ctx)
            or self.config.default_message_output_format
        )

    @property
    def object_output_format(self) -> OutputFormat:
        return (
            get_object_output_format_from_ctx(self._ctx)
            or self.config.default_object_output_format
        )

    def get_crypto_service(self) -> CryptoService:
        adapter = StringFileIOAdapter()
        return CryptoService(file_reader=adapter, file_writer=adapter)

    def get_io_facade(self) -> IOBaseModelFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOBaseModelFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )

    # Thats a bit of a leaky abstraction since we couple with the SDK's API
    # client implementation but it's convenient for now.
    def create_api_client(self) -> ApiClient:
        client_config: Configuration = Configuration(host=self.config.backend_host)
        api_client: ApiClient = ApiClient(configuration=client_config)
        api_client.set_default_header(  # type: ignore[reportUnknownMemberType]
            "Authorization", f"Bearer {self.access_token}"
        )
        return api_client
