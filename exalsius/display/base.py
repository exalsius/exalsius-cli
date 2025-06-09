from rich.console import Console

from exalsius.utils.theme import custom_theme


class BaseDisplayManager:
    def __init__(self, console: Console):
        self.console = console
        self.theme = custom_theme

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[red]{message}[/red]")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[yellow]{message}[/yellow]")

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.console.print(f"[green]{message}[/green]")

    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.console.print(f"[blue]{message}[/blue]")
