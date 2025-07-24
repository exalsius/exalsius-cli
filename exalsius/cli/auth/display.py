from typing import Optional

import qrcode
from rich.console import Console

from exalsius.display.base import BaseDisplayManager


class AuthDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def _generate_qr_code(self, uri: str) -> qrcode.QRCode:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        return qr

    def display_device_code_polling_started(
        self, verification_uri_complete: str, user_code: str
    ):
        qr = self._generate_qr_code(verification_uri_complete)

        self.print_info("Scan this QR code with your smartphone to complete login:")
        self.print_info("")
        qr.print_ascii(invert=True)
        self.print_info("")
        self.print_info("")
        self.print_info("Or open the following URL:")
        self.print_info("")
        self.print_info(verification_uri_complete)
        self.print_info("")
        self.print_info("Please verify that the displayed code matches this one:")
        self.print_info("")
        self.print_info(user_code)
        self.print_info("")
        self.print_info("Waiting for verification...")
        self.print_info("Press Ctrl+C to cancel")

    def display_device_code_polling_started_via_browser(
        self, verification_uri_complete: str, user_code: str
    ):
        self.print_info("Your browser should have been opened.")
        self.print_info("Please verify that the displayed code matches this one:")
        self.print_info("")
        self.print_info(user_code)
        self.print_info("")
        self.print_info("If the browser is not opened, please go to this URL to login:")
        self.print_info("")
        self.print_info(verification_uri_complete)
        self.print_info("")
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
