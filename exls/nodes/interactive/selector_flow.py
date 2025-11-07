from typing import TYPE_CHECKING, List, Literal, Optional

import questionary

from exls.nodes.interactive.base_flow import BaseNodeImportFlow

if TYPE_CHECKING:
    from exls.nodes.display import ComposingNodeDisplayManager


class NodeImportSelectorFlow(BaseNodeImportFlow):
    """Flow for selecting the node import type (SSH or Offer)."""

    def __init__(self, display_manager: "ComposingNodeDisplayManager"):
        super().__init__(display_manager)

    def run(self) -> Optional[Literal["SSH", "OFFER"]]:
        """
        Prompt user to select import type.

        Returns:
            "SSH" or "OFFER" if selected, None if cancelled
        """
        try:
            import_type_choices: List[questionary.Choice] = [
                questionary.Choice("Self-managed (SSH)", "SSH"),
                # commented out for now until we fully suppor the offers functionality
                # questionary.Choice("Cloud Offer", "OFFER"),
            ]
            import_type = self._display_manager.ask_select_required(
                "Choose import type:",
                choices=import_type_choices,
                default=import_type_choices[0],
            )
            return str(import_type)  # type: ignore
        except (KeyboardInterrupt, TypeError):
            return None
