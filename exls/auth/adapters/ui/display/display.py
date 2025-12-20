import logging
import subprocess
import sys
import webbrowser
from typing import Any

import qrcode

from exls.auth.core.domain import DeviceCode
from exls.shared.adapters.ui.facade.interaction import IOBaseModelFacade
from exls.shared.adapters.ui.output.values import OutputFormat

logger = logging.getLogger(__name__)


def _is_interactive() -> bool:
    """Check if running in interactive environment (e.g., not CI/CD)."""
    return sys.stdout.isatty()


# This is needed to prevent output messages to stdout and stderr when the browser is opened.
def _register_silent_browser() -> bool:
    try:
        if sys.platform == "darwin":  # macOS
            webbrowser.register("silent", None, _SilentBrowser("open"), preferred=True)
        elif sys.platform == "win32":  # Windows
            webbrowser.register("silent", None, _SilentBrowser("start"), preferred=True)
        elif sys.platform.startswith("linux"):  # Linux
            webbrowser.register(
                "silent", None, _SilentBrowser("xdg-open"), preferred=True
            )
        else:
            logger.debug("Unsupported platform. Could not register silent browser.")
            return False
    except Exception as e:
        logger.debug(f"Could not register silent browser: {e}")
        return False
    return True


# This is needed to prevent output messages to stdout and stderr when the browser is opened.
class _SilentBrowser(webbrowser.BackgroundBrowser):
    def open(self, url: str, new: int = 0, autoraise: bool = True) -> bool:
        try:
            subprocess.Popen(
                [self.name, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception as e:
            logger.debug(f"Could not open browser: {e}")
            return False


def _open_browser(
    browser: webbrowser.BaseBrowser,
    url: str,
) -> bool:
    try:
        is_browser_opened = browser.open(url)
        if not is_browser_opened:
            return False
    except Exception as e:
        logging.debug(f"Could not open browser: {e}")
        return False
    return True


def _open_browser_for_device_code_authentication(uri: str) -> bool:
    if _register_silent_browser():
        return _open_browser(webbrowser.get("silent"), uri)

    return _open_browser(webbrowser.get(), uri)


class IOAuthFacade(IOBaseModelFacade):
    @staticmethod
    def _generate_qr_code(uri: str) -> qrcode.QRCode[Any]:
        qr: qrcode.QRCode[Any] = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        return qr

    def _display_device_code_polling_started(
        self, verification_uri_complete: str, user_code: str
    ):
        qr: qrcode.QRCode[Any] = self._generate_qr_code(verification_uri_complete)

        self.display_info_message(
            "Scan this QR code with your smartphone to complete login:",
            output_format=OutputFormat.TEXT,
        )
        self.display_info_message("", output_format=OutputFormat.TEXT)
        qr.print_ascii(invert=True)
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(
            "Or open the following URL:", output_format=OutputFormat.TEXT
        )
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(
            verification_uri_complete, output_format=OutputFormat.TEXT
        )
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(
            "Please verify that the displayed code matches this one:",
            output_format=OutputFormat.TEXT,
        )
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(user_code, output_format=OutputFormat.TEXT)
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(
            "Waiting for verification...", output_format=OutputFormat.TEXT
        )
        self.display_info_message(
            "Press Ctrl+C to cancel", output_format=OutputFormat.TEXT
        )

    def _display_device_code_polling_started_via_browser(
        self, verification_uri_complete: str, user_code: str
    ):
        self.display_info_message(
            "Your browser should have been opened.", output_format=OutputFormat.TEXT
        )
        self.display_info_message(
            "Please verify that the displayed code matches this one:",
            output_format=OutputFormat.TEXT,
        )
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(user_code, output_format=OutputFormat.TEXT)
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(
            "If the browser is not opened, please go to this URL to login:",
            output_format=OutputFormat.TEXT,
        )
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(
            verification_uri_complete, output_format=OutputFormat.TEXT
        )
        self.display_info_message("", output_format=OutputFormat.TEXT)
        self.display_info_message(
            "Waiting for verification...", output_format=OutputFormat.TEXT
        )
        self.display_info_message(
            "Press Ctrl+C to cancel", output_format=OutputFormat.TEXT
        )

    def display_auth_poling(self, device_code: DeviceCode):
        # Display the device code to the user and wait for them to authenticate.
        # The CLI will poll for the authentication response.
        logger.debug("Device code received. Waiting for user authentication.")
        if _is_interactive():
            # In an interactive session, attempt to open the verification URL in the user's browser.
            if _open_browser_for_device_code_authentication(
                uri=device_code.verification_uri_complete
            ):
                logger.debug("Opened browser for authentication.")
                self._display_device_code_polling_started_via_browser(
                    verification_uri_complete=device_code.verification_uri_complete,
                    user_code=device_code.user_code,
                )
            else:
                logger.debug("Could not open browser. Displaying URL.")
                self._display_device_code_polling_started(
                    verification_uri_complete=device_code.verification_uri_complete,
                    user_code=device_code.user_code,
                )
        else:
            # In a non-interactive session, display the URL and code for the user to handle manually.
            logger.debug("Non-interactive session. Displaying URL.")
            self._display_device_code_polling_started(
                verification_uri_complete=device_code.verification_uri_complete,
                user_code=device_code.user_code,
            )
