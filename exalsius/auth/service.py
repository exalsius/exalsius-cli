import logging
import subprocess
import sys
import webbrowser
from datetime import datetime, timedelta
from typing import Optional, TypeVar

from pydantic import BaseModel

from exalsius.auth.commands import (
    Auth0FetchDeviceCodeCommand,
    Auth0PollForAuthenticationCommand,
    Auth0RefreshTokenCommand,
    Auth0RevokeTokenCommand,
    Auth0ValidateTokenCommand,
    ClearTokenFromKeyringCommand,
    LoadTokenFromKeyringCommand,
    StoreTokenOnKeyringCommand,
)
from exalsius.auth.models import (
    Auth0AuthenticationDTO,
    Auth0DeviceCodeAuthenticationDTO,
    Auth0FetchDeviceCodeRequestDTO,
    Auth0PollForAuthenticationRequestDTO,
    Auth0RefreshTokenRequestDTO,
    Auth0RevokeTokenRequestDTO,
    Auth0UserInfoDTO,
    Auth0ValidateTokenRequestDTO,
    AuthenticationError,
    ClearTokenFromKeyringRequestDTO,
    LoadedTokenDTO,
    LoadTokenFromKeyringRequestDTO,
    NotLoggedInWarning,
    StoreTokenOnKeyringRequestDTO,
)
from exalsius.config import AppConfig, Auth0Config
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseService
from exalsius.core.commons.models import ServiceError

T = TypeVar("T", bound=BaseModel)


# This is needed to prevent output messages to stdout and stderr when the browser is opened.
class _SilentBrowser(webbrowser.BackgroundBrowser):
    def open(self, url, new=0, autoraise=True):
        return (
            subprocess.Popen(
                [self.name, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            is not None
        )


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
            logging.debug("Unsupported platform. Could not register silent browser.")
            return False
    except Exception as e:
        logging.debug(f"Could not register silent browser: {e}")
        return False
    return True


class Auth0Service(BaseService):
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.config: Auth0Config = config.auth0

    def _execute_command(self, command: BaseCommand[T]) -> T:
        try:
            return command.execute()
        except AuthenticationError as e:
            raise ServiceError(str(e))
        except Exception as e:
            raise ServiceError(
                f"unexpected error while executing command {command.__class__.__name__}: {str(e)}"
            )

    def fetch_device_code(
        self,
    ) -> Auth0DeviceCodeAuthenticationDTO:
        req = Auth0FetchDeviceCodeRequestDTO(
            domain=self.config.domain,
            client_id=self.config.client_id,
            audience=self.config.audience,
            scope=self.config.scope,
            algorithms=self.config.algorithms,
        )
        return self._execute_command(Auth0FetchDeviceCodeCommand(request=req))

    def poll_for_authentication(
        self,
        device_code: str,
    ) -> Auth0AuthenticationDTO:
        req = Auth0PollForAuthenticationRequestDTO(
            domain=self.config.domain,
            client_id=self.config.client_id,
            device_code=device_code,
            grant_type=self.config.device_code_grant_type,
            poll_interval_seconds=self.config.device_code_poll_interval_seconds,
            poll_timeout_seconds=self.config.device_code_poll_timeout_seconds,
            retry_limit=self.config.device_code_retry_limit,
        )
        return self._execute_command(Auth0PollForAuthenticationCommand(request=req))

    def validate_token(self, id_token: str) -> Auth0UserInfoDTO:
        req = Auth0ValidateTokenRequestDTO(
            domain=self.config.domain,
            client_id=self.config.client_id,
            id_token=id_token,
        )
        return self._execute_command(Auth0ValidateTokenCommand(request=req))

    def store_token_on_keyring(
        self,
        token: str,
        expires_in: int,
        refresh_token: Optional[str] = None,
    ) -> None:
        req = StoreTokenOnKeyringRequestDTO(
            client_id=self.config.client_id,
            access_token=token,
            expires_in=expires_in,
            refresh_token=refresh_token,
        )
        self._execute_command(StoreTokenOnKeyringCommand(request=req))

    def load_access_token_from_keyring(self) -> LoadedTokenDTO:
        req = LoadTokenFromKeyringRequestDTO(
            client_id=self.config.client_id,
        )
        return self._execute_command(LoadTokenFromKeyringCommand(request=req))

    def refresh_access_token(self, refresh_token: str) -> Auth0AuthenticationDTO:
        req = Auth0RefreshTokenRequestDTO(
            domain=self.config.domain,
            client_id=self.config.client_id,
            refresh_token=refresh_token,
        )
        return self._execute_command(Auth0RefreshTokenCommand(request=req))

    def acquire_access_token(self) -> str:
        try:
            load_resp = self.load_access_token_from_keyring()
        except ServiceError:
            raise ServiceError("You are not logged in. Please log in first.")

        if load_resp.expiry and datetime.now() >= (
            load_resp.expiry
            - timedelta(minutes=self.config.token_expiry_buffer_minutes)
        ):
            if not load_resp.refresh_token:
                raise ServiceError("Session is expired. Please log in again.")

            try:
                refresh_resp = self.refresh_access_token(load_resp.refresh_token)
            except ServiceError as e:
                raise ServiceError(
                    f"failed to refresh access token: {e}. Please log in again."
                )

            self.store_token_on_keyring(
                token=refresh_resp.access_token,
                expires_in=refresh_resp.expires_in,
                refresh_token=refresh_resp.refresh_token,
            )
            return refresh_resp.access_token
        return load_resp.access_token

    def logout(self) -> None:
        try:
            load_resp = self.load_access_token_from_keyring()
        except ServiceError:
            logging.debug("You are not logged in.")
            raise NotLoggedInWarning("You are not logged in.")

        req = Auth0RevokeTokenRequestDTO(
            client_id=self.config.client_id,
            domain=self.config.domain,
            token=load_resp.access_token,
            token_type_hint="access_token",
        )
        try:
            self._execute_command(Auth0RevokeTokenCommand(request=req))
        except ServiceError as e:
            logging.warning(f"failed to revoke token: {e}, ignoring.")

        req = ClearTokenFromKeyringRequestDTO(client_id=self.config.client_id)
        self._execute_command(ClearTokenFromKeyringCommand(request=req))

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
        if _register_silent_browser():
            return self.__open_browser(webbrowser.get("silent"), uri)

        return self.__open_browser(webbrowser.get(), uri)
