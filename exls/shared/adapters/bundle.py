from abc import ABC

from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration

from exls.config import AppConfig
from exls.shared.adapters.file.adapters import StringFileIOAdapter
from exls.shared.adapters.ui.facade.facade import IOBaseModelFacade
from exls.shared.adapters.ui.factory import IOFactory
from exls.shared.adapters.ui.output.values import OutputFormat
from exls.shared.core.crypto import CryptoService
from exls.shared.core.exceptions import ServiceError
from exls.state import AppState


class BaseBundle(ABC):
    def __init__(self, app_config: AppConfig, app_state: AppState):
        self._app_config: AppConfig = app_config
        self._app_state: AppState = app_state

    @property
    def config(self) -> AppConfig:
        return self._app_config

    @property
    def access_token(self) -> str:
        if not self._app_state.access_token:
            raise ServiceError(
                message="No access token found. Please try to log in again."
            )
        return self._app_state.access_token

    @property
    def message_output_format(self) -> OutputFormat:
        return (
            self._app_state.message_output_format
            or self.config.default_message_output_format
        )

    @property
    def object_output_format(self) -> OutputFormat:
        return (
            self._app_state.object_output_format
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
