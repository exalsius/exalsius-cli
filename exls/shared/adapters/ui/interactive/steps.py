from typing import Callable, List, Optional

from exls.shared.adapters.ui.display.interfaces import (
    IBaseInputManager,
)
from exls.shared.adapters.ui.display.values import DisplayChoice
from exls.shared.adapters.ui.interactive.flow import FlowContext, FlowStep


class TextInputStep(FlowStep[IBaseInputManager]):
    def __init__(
        self,
        key: str,
        message: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ):
        self.key = key
        self.message = message
        self.default = default
        self.validator = validator

    def execute(self, context: FlowContext, display: IBaseInputManager) -> None:
        result = display.ask_text(
            message=self.message,
            default=self.default,
            validator=self.validator,
        )
        context[self.key] = result


class SelectRequiredStep(FlowStep[IBaseInputManager]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: List[DisplayChoice],
        default: Optional[DisplayChoice] = None,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.default = default or choices[0]

    def execute(self, context: FlowContext, display: IBaseInputManager) -> None:
        result = display.ask_select_required(
            message=self.message,
            choices=self.choices,
            default=self.default,
        )
        context[self.key] = result


class ConfirmStep(FlowStep[IBaseInputManager]):
    def __init__(
        self,
        key: str,
        message: str,
        default: bool = False,
    ):
        self.key = key
        self.message = message
        self.default = default

    def execute(self, context: FlowContext, display: IBaseInputManager) -> None:
        result = display.ask_confirm(message=self.message, default=self.default)
        context[self.key] = result
