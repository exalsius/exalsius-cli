from abc import ABC, abstractmethod
from typing import Any

import typer
from rich.console import Console
from sky.client import sdk
from sky.clouds.cloud import Cloud
from sky.exceptions import ApiServerConnectionError

from exalsius.utils.theme import custom_theme


class CloudsOperation(ABC):
    def __init__(self):
        self.console = Console(theme=custom_theme)

    @abstractmethod
    def execute(self) -> Any:
        pass


class CheckCloudsOperation(CloudsOperation):

    def execute(self) -> None:
        """
        Execute the check clouds operation.
        Ensures cloud configurations are properly set up.

        Returns:
            None
        """
        try:
            sdk.get(
                sdk.check(clouds=[], verbose=False),
            )
        except ApiServerConnectionError as e:
            self.console.print(f"[red]Error checking clouds: {str(e)}[/red]")
            raise typer.Exit(1)


class ListEnabledCloudsOperation(CloudsOperation):
    def execute(self) -> list[Cloud]:
        """
        Execute the list enabled clouds operation.

        Returns:
            list[Cloud]: List of enabled cloud providers
        """
        check_op = CheckCloudsOperation()
        check_op.execute()

        try:
            clouds: list[Cloud] = sdk.stream_and_get(sdk.enabled_clouds())
        except ApiServerConnectionError as e:
            self.console.print(f"[red]Error listing enabled clouds: {str(e)}[/red]")
            raise typer.Exit(1)
        return clouds
