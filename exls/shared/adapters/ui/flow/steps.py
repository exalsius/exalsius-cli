from pathlib import Path
from typing import Callable, Generic, List, Optional, Sequence, Type, TypeVar

from pydantic import BaseModel

from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import FlowStep
from exls.shared.adapters.ui.input.values import (
    DisplayChoice,
)

T_Model = TypeVar("T_Model", bound=BaseModel)
T_Choice = TypeVar("T_Choice")


class ConfirmStep(FlowStep[T_Model]):
    def __init__(
        self,
        key: str,
        message: str,
        default: bool = False,
    ):
        self.key = key
        self.message = message
        self.default = default

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        result: bool = io_facade.ask_confirm(message=self.message, default=self.default)
        setattr(model, self.key, result)


class TextInputStep(FlowStep[T_Model]):
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

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        result: str = io_facade.ask_text(
            message=self.message,
            default=self.default,
            validator=self.validator,
        )
        setattr(model, self.key, result)


class PathInputStep(FlowStep[T_Model]):
    def __init__(
        self,
        key: str,
        message: str,
        default: Optional[Path] = None,
    ):
        self.key = key
        self.message = message
        self.default = default

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        result: Path = io_facade.ask_path(
            message=self.message,
            default=self.default,
        )
        setattr(model, self.key, result)


class SelectRequiredStep(FlowStep[T_Model], Generic[T_Model, T_Choice]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: Sequence[DisplayChoice[T_Choice]],
        default: Optional[DisplayChoice[T_Choice]] = None,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.default = default or choices[0]

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        result: DisplayChoice[T_Choice] = io_facade.ask_select_required(
            message=self.message,
            choices=self.choices,
            default=self.default,
        )
        setattr(model, self.key, result.value)


class SelectOptionalStep(FlowStep[T_Model], Generic[T_Model, T_Choice]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: Sequence[DisplayChoice[T_Choice]],
        default: Optional[DisplayChoice[T_Choice]] = None,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.default = default or choices[0]

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        result: Optional[DisplayChoice[T_Choice]] = io_facade.ask_select_optional(
            message=self.message,
            choices=self.choices,
            default=self.default,
        )
        setattr(model, self.key, result.value if result else None)


class CheckboxStep(FlowStep[T_Model], Generic[T_Model, T_Choice]):
    def __init__(
        self,
        key: str,
        message: str,
        choices: Sequence[DisplayChoice[T_Choice]],
        min_choices: int = 1,
    ):
        self.key = key
        self.message = message
        self.choices = choices
        self.min_choices = min_choices

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        result: Sequence[DisplayChoice[T_Choice]] = io_facade.ask_checkbox(
            message=self.message,
            choices=self.choices,
            min_choices=self.min_choices,
        )
        setattr(model, self.key, [choice.value for choice in result])


class ActionStep(FlowStep[T_Model]):
    """A step that executes an arbitrary callable."""

    def __init__(self, action: Callable[[T_Model, IIOFacade[BaseModel]], None]):
        self._action: Callable[[T_Model, IIOFacade[BaseModel]], None] = action

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        self._action(model, io_facade)


class ConditionalStep(FlowStep[T_Model], Generic[T_Model]):
    def __init__(
        self,
        condition: Callable[[T_Model], bool],
        true_step: FlowStep[T_Model],
        false_step: Optional[FlowStep[T_Model]] = None,
    ):
        self.condition: Callable[[T_Model], bool] = condition
        self.true_step: FlowStep[T_Model] = true_step
        self.false_step: Optional[FlowStep[T_Model]] = false_step

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        if self.condition(model):
            self.true_step.execute(model, io_facade)
        elif self.false_step:
            self.false_step.execute(model, io_facade)


T_ChildModel = TypeVar("T_ChildModel", bound=BaseModel)


class SubModelStep(FlowStep[T_Model], Generic[T_Model, T_ChildModel]):
    """
    Runs a child step (or entire flow) on a specific field of the parent model.
    """

    def __init__(
        self,
        field_name: str,
        child_step: FlowStep[T_ChildModel],
        child_model_class: Type[T_ChildModel],
    ):
        self.field_name: str = field_name
        self.child_step: FlowStep[T_ChildModel] = child_step
        self.child_model_class: Type[T_ChildModel] = child_model_class

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        child_model: T_ChildModel = self.child_model_class()
        self.child_step.execute(child_model, io_facade)
        setattr(model, self.field_name, child_model)


class ListBuilderStep(FlowStep[T_Model], Generic[T_Model, T_ChildModel]):
    """
    Runs a child step (or entire flow) in a loop to build a list of child models.
    """

    def __init__(
        self,
        key: str,
        item_step: FlowStep[T_ChildModel],
        item_model_class: Type[T_ChildModel],
        prompt_message: str = "Add another item?",
        min_items: int = 0,
        max_items: Optional[int] = None,
    ):
        self.key = key
        self.item_step = item_step
        self.item_model_class = item_model_class
        self.prompt_message = prompt_message
        self.min_items = min_items
        self.max_items = max_items

    def execute(self, model: T_Model, io_facade: IIOFacade[BaseModel]) -> None:
        items: List[T_ChildModel] = []
        while True:
            if self.max_items is not None and len(items) >= self.max_items:
                break

            should_ask = len(items) >= self.min_items
            if should_ask:
                if not io_facade.ask_confirm(message=self.prompt_message, default=True):
                    break

            item_model = self.item_model_class()
            self.item_step.execute(item_model, io_facade)
            items.append(item_model)

        existing_items: List[T_ChildModel] = getattr(model, self.key) or []

        setattr(model, self.key, existing_items + items)
