from pathlib import Path
from typing import Any, Callable, List, Optional, Sequence, Tuple, TypeVar

import questionary
from pydantic import StrictStr

from exls.shared.adapters.ui.input.interfaces import IInputManager
from exls.shared.adapters.ui.input.values import (
    DisplayChoice,
    UserCancellationException,
)

T = TypeVar("T")


class QuestionaryInputManager(IInputManager):
    def ask_path(
        self,
        message: str,
        default: Optional[Path] = None,
    ) -> Path:
        """Ask the user to select a path."""
        result: Optional[str] = questionary.path(
            message, default=str(default or "./")
        ).ask(kbi_msg="")
        if result is None:
            raise UserCancellationException("User cancelled the path selection")
        return Path(result)

    def ask_text(
        self,
        message: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> StrictStr:
        """Ask a free-form text question."""

        result: Optional[StrictStr] = questionary.text(
            message,
            default=default or "",
            validate=validator,
        ).ask(kbi_msg="")
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def _to_questionary_choice(
        self, choice: DisplayChoice[T] | str
    ) -> questionary.Choice:
        if isinstance(choice, str):
            return questionary.Choice(title=choice, value=choice)
        return questionary.Choice(title=choice.title, value=choice)

    def _to_questionary_choices(
        self,
        choices: Sequence[DisplayChoice[T] | str],
        default: Optional[DisplayChoice[T] | str] = None,
    ) -> Tuple[List[questionary.Choice], Optional[questionary.Choice]]:
        q_choices: List[questionary.Choice] = []
        q_default: Optional[questionary.Choice] = None

        for choice in choices:
            q_choice = self._to_questionary_choice(choice)
            q_choices.append(q_choice)

            if default is not None:
                c_val = choice if isinstance(choice, str) else choice.value
                d_val = default if isinstance(default, str) else default.value

                if c_val == d_val:
                    q_default = q_choice

        return q_choices, q_default

    def ask_select_required(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: DisplayChoice[T],
    ) -> DisplayChoice[T]:
        """Ask the user to select one option from a list."""
        q_choices, q_default = self._to_questionary_choices(choices, default)
        result: Optional[DisplayChoice[T]] = questionary.select(
            message, choices=q_choices, default=q_default
        ).ask(kbi_msg="")
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_select_optional(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: Optional[DisplayChoice[T]] = None,
    ) -> Optional[DisplayChoice[T]]:
        q_choices, q_default = self._to_questionary_choices(choices, default)

        # We need to ask_unsafe to detect KeyboardInterrupt and allow None-selection
        try:
            result: Optional[DisplayChoice[T]] = questionary.select(
                message, choices=q_choices, default=q_default
            ).unsafe_ask()
        except KeyboardInterrupt:
            raise UserCancellationException("User cancelled")
        return result

    def ask_confirm(self, message: str, default: bool = False) -> bool:
        """Ask a yes/no confirmation question."""
        result = questionary.confirm(message, default=default).ask(kbi_msg="")
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_checkbox(
        self, message: str, choices: Sequence[DisplayChoice[T]], min_choices: int = 1
    ) -> Sequence[DisplayChoice[T]]:
        """Ask the user to select multiple options from a list."""

        def _validate_checkbox(choices: Sequence[Any]) -> bool | str:
            return (
                True
                if len(choices) >= min_choices
                else f"Please select at least {min_choices} options."
            )

        q_choices, _ = self._to_questionary_choices(choices)

        result: Optional[Sequence[DisplayChoice[T]]] = questionary.checkbox(
            message, choices=q_choices, validate=_validate_checkbox
        ).ask(kbi_msg="")
        if result is None:
            raise UserCancellationException("User cancelled")
        return result or []
