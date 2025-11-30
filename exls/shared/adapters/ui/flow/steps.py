from pathlib import Path
from typing import (
    Callable,
    Generic,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseModel, Field
from typing_extensions import Any

from exls.shared.adapters.ui.facade.interface import IIOFacade
from exls.shared.adapters.ui.flow.flow import (
    FlowCancelationByUserException,
    FlowContext,
    FlowStep,
)
from exls.shared.adapters.ui.input.values import (
    DisplayChoice,
    UserCancellationException,
)

T_Model = TypeVar("T_Model", bound=BaseModel)
T_Choice = TypeVar("T_Choice")


class ChoicesSpec(BaseModel, Generic[T_Choice]):
    choices: Sequence[DisplayChoice[T_Choice]] = Field(..., description="The choices")
    default: Optional[DisplayChoice[T_Choice]] = Field(
        default=None, description="The default choice"
    )


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

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        try:
            result: bool = io_facade.ask_confirm(
                message=self.message, default=self.default
            )
        except UserCancellationException as e:
            raise FlowCancelationByUserException(e) from e

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

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        try:
            result: str = io_facade.ask_text(
                message=self.message,
                default=self.default,
                validator=self.validator,
            )
        except UserCancellationException as e:
            raise FlowCancelationByUserException(e) from e

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

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        try:
            result: Path = io_facade.ask_path(
                message=self.message,
                default=self.default,
            )
        except UserCancellationException as e:
            raise FlowCancelationByUserException(e) from e

        setattr(model, self.key, result)


class ChoicesStep(FlowStep[T_Model], Generic[T_Model, T_Choice]):
    def __init__(
        self,
        key: str,
        message: str,
        choices_spec: Union[
            ChoicesSpec[T_Choice],
            Callable[[T_Model, FlowContext], ChoicesSpec[T_Choice]],
        ],
        remember_last_choice: bool = True,
    ):
        self.key: str = key
        self.message: str = message
        self.choices_spec: (
            ChoicesSpec[T_Choice]
            | Callable[[T_Model, FlowContext], ChoicesSpec[T_Choice]]
        ) = choices_spec
        self.remember_last_choice: bool = remember_last_choice

    def _resolve_choices_spec(
        self, model: T_Model, context: FlowContext
    ) -> ChoicesSpec[T_Choice]:
        choices_spec: ChoicesSpec[T_Choice] = (
            self.choices_spec(model, context)
            if callable(self.choices_spec)
            else self.choices_spec
        )
        if not choices_spec.choices:
            raise ValueError(f"No choices available for step '{self.key}'")

        # If no default is set and we should remember the last choice, try to find it in the context
        if choices_spec.default is None and self.remember_last_choice:
            last_choices = context.meta.get("last_choices", {})
            last_value = last_choices.get(self.key)

            if last_value is not None:
                found = next(
                    (c for c in choices_spec.choices if c.value == last_value), None
                )
                if found:
                    choices_spec.default = found

        return choices_spec

    def _save_last_choice(self, context: FlowContext, value: T_Choice) -> None:
        if self.remember_last_choice:
            if "last_choices" not in context.meta:
                context.meta["last_choices"] = {}
            context.meta["last_choices"][self.key] = value


class SelectRequiredStep(ChoicesStep[T_Model, T_Choice]):
    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        choices_spec: ChoicesSpec[T_Choice] = self._resolve_choices_spec(model, context)

        try:
            result: DisplayChoice[T_Choice] = io_facade.ask_select_required(
                message=self.message,
                choices=choices_spec.choices,
                default=choices_spec.default or choices_spec.choices[0],
            )
        except UserCancellationException as e:
            raise FlowCancelationByUserException(e) from e

        self._save_last_choice(context, result.value)
        setattr(model, self.key, result.value)


class SelectOptionalStep(ChoicesStep[T_Model, T_Choice]):
    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        choices_spec: ChoicesSpec[T_Choice] = self._resolve_choices_spec(model, context)

        try:
            result: Optional[DisplayChoice[T_Choice]] = io_facade.ask_select_optional(
                message=self.message,
                choices=choices_spec.choices,
                default=choices_spec.default or choices_spec.choices[0],
            )
        except UserCancellationException as e:
            raise FlowCancelationByUserException(e) from e

        if result:
            self._save_last_choice(context, result.value)
        setattr(model, self.key, result.value if result else None)


class UpdateLastChoiceStep(FlowStep[T_Model]):
    """
    Updates the 'last_choices' in the context meta with the current value of a field.
    Useful when a field's value changes after the initial selection (e.g. replacing a sentinel).
    """

    def __init__(self, key: str):
        self.key: str = key

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        value: Any = getattr(model, self.key)
        if "last_choices" not in context.meta:
            context.meta["last_choices"] = {}
        context.meta["last_choices"][self.key] = value


class CheckboxStep(ChoicesStep[T_Model, T_Choice]):
    def __init__(
        self,
        key: str,
        message: str,
        choices_spec: Union[
            ChoicesSpec[T_Choice],
            Callable[[T_Model, FlowContext], ChoicesSpec[T_Choice]],
        ],
        min_choices: int = 1,
    ):
        super().__init__(
            key=key,
            message=message,
            choices_spec=choices_spec,
            remember_last_choice=False,
        )
        self.min_choices: int = min_choices

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        choices_spec: ChoicesSpec[T_Choice] = self._resolve_choices_spec(model, context)
        try:
            result: Sequence[DisplayChoice[T_Choice]] = io_facade.ask_checkbox(
                message=self.message,
                choices=choices_spec.choices,
                min_choices=self.min_choices,
            )
        except UserCancellationException as e:
            raise FlowCancelationByUserException(e) from e
        setattr(model, self.key, [choice.value for choice in result])


class ActionStep(FlowStep[T_Model]):
    """A step that executes an arbitrary callable."""

    def __init__(
        self,
        action: Callable[[T_Model, FlowContext, IIOFacade[BaseModel]], None],
    ):
        self._action = action

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        self._action(model, context, io_facade)


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

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        try:
            if self.condition(model):
                self.true_step.execute(model, context, io_facade)
            elif self.false_step:
                self.false_step.execute(model, context, io_facade)
        except (UserCancellationException, FlowCancelationByUserException) as e:
            raise FlowCancelationByUserException(e) from e


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

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        child_model: T_ChildModel = self.child_model_class()

        # Create a new context for the sub-model, linking to parent
        sub_context = context.model_copy()
        sub_context.parent = model
        try:
            self.child_step.execute(child_model, sub_context, io_facade)
        except (UserCancellationException, FlowCancelationByUserException) as e:
            raise FlowCancelationByUserException(e) from e
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
        self.key: str = key
        self.item_step: FlowStep[T_ChildModel] = item_step
        self.item_model_class: Type[T_ChildModel] = item_model_class
        self.prompt_message: str = prompt_message
        self.min_items: int = min_items
        self.max_items: Optional[int] = max_items

    def execute(
        self, model: T_Model, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        items: List[T_ChildModel] = []
        while True:
            if self.max_items is not None and len(items) >= self.max_items:
                break

            should_ask = len(items) >= self.min_items
            if should_ask:
                if not io_facade.ask_confirm(message=self.prompt_message, default=True):
                    break

            item_model: T_ChildModel = self.item_model_class()

            # Create a new context for the list item
            item_context: FlowContext = context.model_copy()
            item_context.parent = model
            item_context.siblings = cast(List[BaseModel], items)

            try:
                self.item_step.execute(item_model, item_context, io_facade)
                items.append(item_model)
            except (UserCancellationException, FlowCancelationByUserException) as e:
                if not items:
                    raise FlowCancelationByUserException(e) from e
                break

        existing_items: List[T_ChildModel] = getattr(model, self.key) or []

        setattr(model, self.key, existing_items + items)
