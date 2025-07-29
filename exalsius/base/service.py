import logging
import os
from abc import ABC
from multiprocessing import AuthenticationError
from typing import Any, Optional, Tuple

from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration

from exalsius.base.operations import BaseOperation

logger = logging.getLogger("core.services.base")


class BaseService(ABC):
    def execute_operation(self, operation: BaseOperation) -> Tuple[Any, Optional[str]]:
        """
        Execute an operation and handle common service-level concerns.

        Args:
            operation: The operation to execute

        Returns:
            Tuple[Any, Optional[str]]: The operation result and optional error message

        Raises:
            ApiClientError: If the operation fails due to API client issues
        """
        try:
            return operation.execute()
        except Exception as e:
            return None, f"Error during operation execution: {str(e)}"


class BaseServiceWithAuth(BaseService):
    def __init__(self, access_token: str, host: Optional[str] = None):
        api_host = host or os.getenv("EXALSIUS_API_HOST", "https://api.exalsius.ai")

        # Create configuration
        client_config = Configuration(host=api_host)

        if not access_token:
            raise AuthenticationError("No credentials found")

        self.api_client = ApiClient(configuration=client_config)

        self.api_client.set_default_header("Authorization", f"Bearer {access_token}")

        logger.debug(
            f"Trying to connect to {self.api_client.configuration.host} with "
            f"auth token {access_token[:4]}..."
        )
