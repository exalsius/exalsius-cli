from typing import Optional

from rich.console import Console

from exalsius.display.base import BaseDisplayManager


class AuthDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_device_code_polling_started(
        self, verification_uri_complete: str, user_code: str
    ):
        self.print_info(
            f"Open the following URL in your browser: {verification_uri_complete}"
        )
        self.print_info(
            f"and verify that the displayed code matches this one '{user_code}'"
        )
        self.print_info("Waiting for verification...")
        self.print_info("Press Ctrl+C to cancel")

    def display_device_code_polling_cancelled(self):
        self.print_info("Login canceled via Ctrl+C")

    def display_authentication_error(self, error: str):
        self.print_error(f"Login error: {error}")

    def display_authentication_success(self, email: Optional[str], sub: Optional[str]):
        self.print_success(
            f"You are successfully logged in as '{email or sub or 'unknown'}'"
        )
        self.print_success("Let's start setting up your workspaces!")

    def display_logout_success(self):
        self.print_success("Logged out successfully.")

    def display_not_logged_in(self):
        self.print_info("You are not logged in.")
