"""PKCE authentication flow operations."""

from abc import ABC, abstractmethod
from typing import Optional

from exls.auth.core.domain import PkceSession, Token


class PkceOperations(ABC):
    @abstractmethod
    def generate_pkce_session(self, redirect_uri: str) -> PkceSession: ...

    @abstractmethod
    def start_callback_server(self) -> int:
        """Start callback server, return actual port."""
        ...

    @abstractmethod
    def build_authorization_url(
        self, session: PkceSession, organization: Optional[str] = None
    ) -> str: ...

    @abstractmethod
    def open_browser(self, url: str) -> bool: ...

    @abstractmethod
    def wait_for_callback(
        self, session: PkceSession, timeout: Optional[int] = None
    ) -> str:
        """Wait for callback, return authorization code."""
        ...

    @abstractmethod
    def exchange_code_for_token(self, code: str, session: PkceSession) -> Token: ...

    @abstractmethod
    def shutdown_callback_server(self) -> None: ...
