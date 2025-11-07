from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from exls.nodes.display import ComposingNodeDisplayManager


class BaseNodeImportFlow(ABC):
    """Base class for node import flows with shared functionality."""

    def __init__(self, display_manager: "ComposingNodeDisplayManager"):
        self._display_manager: "ComposingNodeDisplayManager" = display_manager

    def _handle_cancellation(self) -> None:
        """Handle user cancellation consistently."""
        self._display_manager.display_info("\nOperation cancelled by user.")
