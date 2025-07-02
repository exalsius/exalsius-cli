import os
from abc import ABC
from typing import Any, Optional, Tuple

import exalsius_api_client
import typer
from rich.console import Console

from exalsius.core.operations.base import BaseOperation


class BaseService(ABC):
    def __init__(self, host: Optional[str] = None):
        api_host = host or os.getenv("EXALSIUS_API_HOST", "https://api.exalsius.ai")

        # Create configuration
        config = exalsius_api_client.Configuration(host=api_host)

        # Set up basic authentication from environment variables if they exist
        username = os.getenv("EXALSIUS_USERNAME")
        password = os.getenv("EXALSIUS_PASSWORD")

        if username and password:
            config.username = username
            config.password = password

        self.api_client = exalsius_api_client.ApiClient(configuration=config)

        # Manually add basic auth header since the generated client doesn't include auth settings
        if username and password:
            auth_token = config.get_basic_auth_token()
            if auth_token:
                self.api_client.set_default_header("Authorization", auth_token)

        self._test_connection()

    def _test_connection(self) -> None:
        """
        Test the connection to the API server.

        Raises:
            ApiException: If the connection test fails
        """
        try:
            # Use a simple API endpoint to test connection
            # TODO: change this to a /health endpoint
            api_instance = exalsius_api_client.ClustersApi(self.api_client)
            api_instance.list_clusters()
        except Exception as e:
            console = Console()
            console.print(
                f"[red]Failed to connect to exalsius API server at {self.api_client.configuration.host}: {str(e)}[/red]"
            )
            raise typer.Exit(1)

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
