from typing import Any, Callable, List, Optional, Union

from exls.shared.adapters.cli.display import ConsoleInteractionManager
from exls.shared.adapters.cli.interactive.flow import FlowContext, FlowStep


class TextInputStep(FlowStep[ConsoleInteractionManager]):
    def __init__(
        self,
        key: str,
        message: str,
        default: Optional[Union[str, Callable[[FlowContext], str]]] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ):
        self.key = key
        self.message = message
        self.default = default
        self.validator = validator

    def execute(self, context: FlowContext, display: ConsoleInteractionManager) -> None:
        default_val = self.default
        if callable(self.default):
            default_val = self.default(context)

        # Ensure default_val is Optional[str]
        default_str: Optional[str] = (
            str(default_val) if default_val is not None else None
        )

        result = display.ask_text(
            message=self.message,
            default=default_str,
            validator=self.validator,
        )
        context[self.key] = result


class SelectStep(FlowStep[ConsoleInteractionManager]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: Union[List[Any], Callable[[FlowContext], List[Any]]],
        default: Optional[Union[Any, Callable[[FlowContext], Any]]] = None,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.default = default

    def execute(self, context: FlowContext, display: ConsoleInteractionManager) -> None:
        choices_val = self.choices
        if callable(self.choices):
            choices_val = self.choices(context)

        if not choices_val:
            raise ValueError(f"No choices provided for {self.key}")

        default_val = self.default
        if callable(self.default):
            default_val = self.default(context)

        if default_val is None:
            default_val = choices_val[0]

        result = display.ask_select_required(
            message=self.message,
            choices=choices_val,
            default=default_val,
        )
        context[self.key] = result


class ConfirmStep(FlowStep[ConsoleInteractionManager]):
    def __init__(
        self,
        key: str,
        message: str,
        default: bool = False,
    ):
        self.key = key
        self.message = message
        self.default = default

    def execute(self, context: FlowContext, display: ConsoleInteractionManager) -> None:
        result = display.ask_confirm(message=self.message, default=self.default)
        context[self.key] = result


class ShowInfoStep(FlowStep[ConsoleInteractionManager]):
    def __init__(self, message: str):
        self.message = message

    def execute(self, context: FlowContext, display: ConsoleInteractionManager) -> None:
        display.display_text(self.message)
