import logging
from typing import Any

from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration

from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand

logger = logging.getLogger("core.services.base")


class BaseService:
    def __init__(self, config: AppConfig):
        self.config = config

    def execute_command(self, command: BaseCommand) -> Any:
        try:
            return command.execute()
        except Exception as e:
            raise e


class BaseServiceWithAuth(BaseService):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config)

        client_config: Configuration = Configuration(host=self.config.backend_host)

        self.api_client: ApiClient = ApiClient(configuration=client_config)
        self.api_client.set_default_header(  # pyright: ignore[reportUnknownMemberType]
            "Authorization", f"Bearer {access_token}"
        )
