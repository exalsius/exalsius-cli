from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from exls.workspaces.common.display import ComposingWorkspaceDeployDisplayManager


class BaseWorkspaceDeployFlow:
    """Base class for workspace deployment flows with shared functionality."""

    def __init__(self, display_manager: "ComposingWorkspaceDeployDisplayManager"):
        self._display_manager: "ComposingWorkspaceDeployDisplayManager" = (
            display_manager
        )

    def _handle_cancellation(self) -> None:
        """Handle user cancellation consistently."""
        self._display_manager.display_info("\nOperation cancelled by user.")
