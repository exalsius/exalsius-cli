import logging
import os
import sys
from typing import Optional

from exls.auth.adapters.auth0.auth0 import Auth0Adapter
from exls.auth.adapters.auth0.config import Auth0Config
from exls.auth.adapters.auth0.pkce_adapter import Auth0PkceAdapter
from exls.auth.adapters.keyring.keyring import KeyringAdapter
from exls.auth.adapters.ui.display.display import IOAuthFacade
from exls.auth.core.domain import AuthFlowType
from exls.auth.core.ports.pkce_operations import PkceOperations
from exls.auth.core.service import AuthService
from exls.config import AppConfig
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory
from exls.state import AppState

logger = logging.getLogger(__name__)


class AuthBundle(BaseBundle):
    def __init__(self, app_config: AppConfig, app_state: AppState):
        super().__init__(app_config, app_state)

    @staticmethod
    def detect_auth_flow(override: Optional[AuthFlowType] = None) -> AuthFlowType:
        """Determine authentication flow based on environment."""
        if override and override != AuthFlowType.AUTO:
            logger.debug("Auth flow override: %s", override)
            return override

        if not sys.stdout.isatty():
            logger.debug("Non-interactive terminal, using device code")
            return AuthFlowType.DEVICE_CODE

        if sys.platform.startswith("linux"):
            if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
                logger.debug("No display server, using device code")
                return AuthFlowType.DEVICE_CODE

        import webbrowser

        try:
            webbrowser.get()
            logger.debug("Browser available, using PKCE")
            return AuthFlowType.PKCE
        except webbrowser.Error:
            logger.debug("No browser found, using device code")
            return AuthFlowType.DEVICE_CODE

    def get_auth_service(
        self, auth_flow_override: Optional[AuthFlowType] = None
    ) -> AuthService:
        auth_config: Auth0Config = Auth0Config()
        auth0_adapter = Auth0Adapter(config=auth_config)

        flow = self.detect_auth_flow(auth_flow_override)
        pkce_ops: Optional[PkceOperations] = None
        if flow == AuthFlowType.PKCE:
            pkce_ops = Auth0PkceAdapter(config=auth_config)

        return AuthService(
            auth_operations=auth0_adapter,
            token_repository=KeyringAdapter(),
            device_code_operations=auth0_adapter,
            pkce_operations=pkce_ops,
        )

    def get_io_facade(self) -> IOAuthFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOAuthFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )
