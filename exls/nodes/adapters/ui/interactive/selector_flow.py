from __future__ import annotations

from typing import List

import questionary

from exls.nodes.adapters.cli.display import ComposingNodeDisplayManager
from exls.nodes.adapters.values import NodeImportTypeDTO
from exls.shared.core.ports import UserCancellationException
from exls.shared.core.exceptions import ExalsiusError


class NodeImportSelectorFlowInterruptionException(UserCancellationException):
    """Raised when the user cancels an interactive node import type selection flow."""


class NodeImportSelectorFlow:
    """Flow for selecting the node import type (SSH or Offer)."""

    def __init__(self, display_manager: ComposingNodeDisplayManager):
        self._display_manager: ComposingNodeDisplayManager = display_manager

    def run(self) -> NodeImportTypeDTO:
        """
        Prompt user to select import type.
        """
        try:
            import_type_choices: List[questionary.Choice] = [
                questionary.Choice(
                    NodeImportTypeDTO.SSH.value, NodeImportTypeDTO.SSH.value
                ),
                questionary.Choice(
                    NodeImportTypeDTO.OFFER.value, NodeImportTypeDTO.OFFER.value
                ),
            ]
            import_type = self._display_manager.ask_select_required(
                "Choose import type:",
                choices=import_type_choices,
                default=import_type_choices[0],
            )
            return NodeImportTypeDTO(import_type.value)
        except UserCancellationException:
            raise NodeImportSelectorFlowInterruptionException(
                "Node import type selection cancelled by user."
            )
        except Exception as e:
            raise ExalsiusError(f"An unexpected error occurred: {str(e)}") from e
