from typing import Any, Optional

import qrcode

from exalsius.core.base.models import ErrorDTO
from exalsius.core.commons.display import BaseDisplayManager
from exalsius.core.commons.render.text import (
    RichTextErrorMessageRenderer,
    RichTextRenderer,
    RichTextSuccessMessageRenderer,
)


class AuthDisplayManager(BaseDisplayManager):
    def __init__(self):
        super().__init__(
            info_renderer=RichTextRenderer(),
            success_renderer=RichTextSuccessMessageRenderer(),
            error_renderer=RichTextErrorMessageRenderer(),
        )

    def _generate_qr_code(self, uri: str) -> qrcode.QRCode[Any]:
        qr: qrcode.QRCode[Any] = qrcode.QRCode(
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
        qr: qrcode.QRCode[Any] = self._generate_qr_code(verification_uri_complete)

        self.display_info("Scan this QR code with your smartphone to complete login:")
        self.display_info("")
        qr.print_ascii(invert=True)
        self.display_info("")
        self.display_info("")
        self.display_info("Or open the following URL:")
        self.display_info("")
        self.display_info(verification_uri_complete)
        self.display_info("")
        self.display_info("Please verify that the displayed code matches this one:")
        self.display_info("")
        self.display_info(user_code)
        self.display_info("")
        self.display_info("Waiting for verification...")
        self.display_info("Press Ctrl+C to cancel")

    def display_device_code_polling_started_via_browser(
        self, verification_uri_complete: str, user_code: str
    ):
        self.display_info("Your browser should have been opened.")
        self.display_info("Please verify that the displayed code matches this one:")
        self.display_info("")
        self.display_info(user_code)
        self.display_info("")
        self.display_info(
            "If the browser is not opened, please go to this URL to login:"
        )
        self.display_info("")
        self.display_info(verification_uri_complete)
        self.display_info("")
        self.display_info("Waiting for verification...")
        self.display_info("Press Ctrl+C to cancel")

    def display_device_code_polling_cancelled(self):
        self.display_info("Login canceled via Ctrl+C")

    def display_authentication_error(self, error: str):
        self.display_error(
            ErrorDTO(
                message=f"Login error: {error}",
                error_type="AUTHENTICATION_ERROR",
            )
        )

    def display_authentication_success(self, email: Optional[str], sub: Optional[str]):
        self.display_success(
            f"You are successfully logged in as '{email or sub or 'unknown'}'"
        )
        self.display_success("Let's start setting up your workspaces!")

    def display_logout_success(self):
        self.display_success("Logged out successfully.")

    def display_not_logged_in(self):
        self.display_info("You are not logged in.")

    def display_deployment_token_request_success(
        self,
        access_token: str,
    ):
        self.display_info("")
        self.display_success("Request for deployment token successful!")
        self.display_info("")
        self.display_success("Your deployment token is:")
        self.display_info("")
        self.display_info(access_token)
        self.display_info("")
