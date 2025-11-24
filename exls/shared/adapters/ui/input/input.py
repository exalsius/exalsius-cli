from typing import Any, Callable, List, Optional, Sequence, TypeVar

import questionary
from pydantic import StrictStr

from exls.shared.adapters.ui.input.interfaces import IInputManager
from exls.shared.adapters.ui.input.values import (
    DisplayChoice,
    UserCancellationException,
)

T = TypeVar("T")


class QuestionaryInputManager(IInputManager):
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
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def _to_questionary_choice(
        self, choice: DisplayChoice[T], default: Optional[DisplayChoice[T]] = None
    ) -> questionary.Choice:
        checked: bool = (
            choice == default
            or choice.value == default.value
            or choice.title == default.title
            if default
            else False
        )
        if isinstance(choice, str):
            return questionary.Choice(title=choice, value=choice, checked=checked)
        return questionary.Choice(
            title=choice.title, value=choice.value, checked=checked
        )

    def ask_select_required(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: DisplayChoice[T],
    ) -> DisplayChoice[T]:
        """Ask the user to select one option from a list."""
        q_default: questionary.Choice = self._to_questionary_choice(default)
        q_choices: List[questionary.Choice] = [
            self._to_questionary_choice(c, default) for c in choices
        ]

        result: Optional[DisplayChoice[T]] = questionary.select(
            message, choices=q_choices, default=q_default
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")

        return result

    def ask_select_optional(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: Optional[DisplayChoice[T]] = None,
    ) -> Optional[DisplayChoice[T]]:
        q_default: Optional[questionary.Choice] = (
            self._to_questionary_choice(default) if default else None
        )
        q_choices: List[questionary.Choice] = [
            self._to_questionary_choice(c, default) for c in choices
        ]

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
        result = questionary.confirm(message, default=default).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result

    def ask_checkbox(
        self, message: str, choices: Sequence[DisplayChoice[T]], min_choices: int = 1
    ) -> List[DisplayChoice[T]]:
        """Ask the user to select multiple options from a list."""

        def _validate_checkbox(choices: Sequence[Any]) -> bool | str:
            return (
                True
                if len(choices) >= min_choices
                else f"Please select at least {min_choices} options."
            )

        q_choices: List[questionary.Choice] = [
            self._to_questionary_choice(c) for c in choices
        ]

        result: Optional[List[DisplayChoice[T]]] = questionary.checkbox(
            message, choices=q_choices, validate=_validate_checkbox
        ).ask()
        if result is None:
            raise UserCancellationException("User cancelled")
        return result or []
