import logging
import subprocess
import sys
import webbrowser
from abc import ABC
from typing import Any, Dict

import qrcode

from exls.auth.dtos import UserInfoDTO
from exls.core.commons.display import (
    BaseDisplayManager,
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleSingleItemDisplay,
)
from exls.core.commons.render.json import JsonSingleItemStringRenderer
from exls.core.commons.render.table import Column, TableSingleItemRenderer, get_column

logger = logging.getLogger(__name__)


# This is needed to prevent output messages to stdout and stderr when the browser is opened.
def register_silent_browser() -> bool:
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

    def __open_browser(
        self,
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

    def open_browser_for_device_code_authentication(self, uri: str) -> bool:
        if register_silent_browser():
            return self.__open_browser(webbrowser.get("silent"), uri)

        return self.__open_browser(webbrowser.get(), uri)


class BaseConsoleAuthDisplayManager(ABC, BaseDisplayManager):
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


class JsonAuthDisplayManager(BaseJsonDisplayManager, BaseConsoleAuthDisplayManager):
    def __init__(
        self,
        user_info_renderer: JsonSingleItemStringRenderer[
            UserInfoDTO
        ] = JsonSingleItemStringRenderer[UserInfoDTO](),
    ):
        super().__init__()
        self.user_info_display = ConsoleSingleItemDisplay(renderer=user_info_renderer)

    def display_user_info(self, user: UserInfoDTO):
        self.user_info_display.display(user)


DEFAULT_USER_INFO_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "email": get_column("Email"),
    "sub": get_column("Sub"),
}


class TableAuthDisplayManager(BaseTableDisplayManager, BaseConsoleAuthDisplayManager):
    def __init__(
        self,
        user_info_renderer: TableSingleItemRenderer[
            UserInfoDTO
        ] = TableSingleItemRenderer[UserInfoDTO](
            columns_map=DEFAULT_USER_INFO_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.user_info_display = ConsoleSingleItemDisplay(renderer=user_info_renderer)

    def display_user_info(self, user: UserInfoDTO):
        self.user_info_display.display(user)
