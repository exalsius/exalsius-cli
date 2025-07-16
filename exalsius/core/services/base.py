import logging
import os
from abc import ABC
from multiprocessing import AuthenticationError
from typing import Any, Optional, Tuple

from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration

from exalsius.core.models.auth import Session
from exalsius.core.operations.base import BaseOperation

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
            return None, f"Unexpected error during operation execution: {str(e)}"


class BaseServiceWithAuth(BaseService):
    def __init__(self, session: Session, host: Optional[str] = None):
        api_host = host or os.getenv("EXALSIUS_API_HOST", "https://api.exalsius.ai")

        # Create configuration
        client_config = Configuration(host=api_host)

        if (
            not session.credentials
            or not session.credentials.username
            or not session.credentials.password
        ):
            raise AuthenticationError("No credentials found")

        client_config.username = session.credentials.username
        client_config.password = session.credentials.password

        self.api_client = ApiClient(configuration=client_config)

        # Manually add basic auth header since the generated client doesn't include auth settings
        auth_token = client_config.get_basic_auth_token()
        if auth_token:
            self.api_client.set_default_header("Authorization", auth_token)

        logger.debug(
            f"Trying to connect to {self.api_client.configuration.host} with "
            f"auth token {auth_token} (credentials: {session.credentials})"
        )
