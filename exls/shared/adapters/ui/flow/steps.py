from typing import Callable, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowContext, FlowStep
from exls.shared.adapters.ui.input.values import DisplayChoice

T = TypeVar("T")


class ConfirmStep(FlowStep):
    def __init__(
        self,
        key: str,
        message: str,
        default: bool = False,
    ):
        self.key = key
        self.message = message
        self.default = default

    def execute(self, context: FlowContext, io_facade: IIOFacade[BaseModel]) -> None:
        result: bool = io_facade.ask_confirm(message=self.message, default=self.default)
        context[self.key] = result


class TextInputStep(FlowStep):
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

    def execute(self, context: FlowContext, io_facade: IIOFacade[BaseModel]) -> None:
        result: str = io_facade.ask_text(
            message=self.message,
            default=self.default,
            validator=self.validator,
        )
        context[self.key] = result


class SelectRequiredStep(FlowStep, Generic[T]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: List[DisplayChoice[T]],
        default: Optional[DisplayChoice[T]] = None,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.default = default or choices[0]

    def execute(self, context: FlowContext, io_facade: IIOFacade[BaseModel]) -> None:
        result: DisplayChoice[T] = io_facade.ask_select_required(
            message=self.message,
            choices=self.choices,
            default=self.default,
        )
        context[self.key] = result


class SelectOptionalStep(FlowStep, Generic[T]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: List[DisplayChoice[T]],
        default: Optional[DisplayChoice[T]] = None,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.default = default or choices[0]

    def execute(self, context: FlowContext, io_facade: IIOFacade[BaseModel]) -> None:
        result: Optional[DisplayChoice[T]] = io_facade.ask_select_optional(
            message=self.message,
            choices=self.choices,
            default=self.default,
        )
        context[self.key] = result


class CheckboxStep(FlowStep, Generic[T]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: List[DisplayChoice[T]],
        min_choices: int = 1,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.min_choices = min_choices

    def execute(self, context: FlowContext, io_facade: IIOFacade[BaseModel]) -> None:
        result: List[DisplayChoice[T]] = io_facade.ask_checkbox(
            message=self.message,
            choices=self.choices,
            min_choices=self.min_choices,
        )
        context[self.key] = result
