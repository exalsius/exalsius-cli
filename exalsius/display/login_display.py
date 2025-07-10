from rich.console import Console

from exalsius.display.base import BaseDisplayManager


class LoginDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_login_success(self):
        self.print_success("Login successful")

    def display_login_error(self, error: str):
        self.print_error(f"Login failed: {error}")
