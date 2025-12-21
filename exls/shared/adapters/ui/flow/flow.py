from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, cast

from pydantic import BaseModel, Field

from exls.shared.adapters.ui.facade.interface import IOFacade
from exls.shared.adapters.ui.input.values import UserCancellationException
from exls.shared.core.exceptions import ExalsiusError

T = TypeVar("T")


class FlowError(ExalsiusError):
    """Exception raised when the flow encounters an error."""

    pass


class InvalidFlowStateError(ExalsiusError):
    """Exception raised when the flow is in an invalid state."""

    pass


class FlowCancelationByUserException(UserCancellationException):
    """Exception raised when the flow is cancelled."""

    pass


class FlowContext(BaseModel):
    # Parent model (if inside a sub-flow)
    parent: Optional[BaseModel] = Field(default=None, description="Parent model")
    # Previous items (if inside a list builder)
    siblings: List[BaseModel] = Field(
        default_factory=lambda: cast(List[BaseModel], []), description="Previous items"
    )
    # Arbitrary data
    meta: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary data")


class FlowStep(Generic[T], ABC):
    """Abstract base class for flow steps."""

    @abstractmethod
    def execute(
        self, model: T, context: FlowContext, io_facade: IOFacade[BaseModel]
    ) -> None: ...


class SequentialFlow(FlowStep[T]):
    """A step that executes a list of child steps in order."""

    def __init__(self, steps: Sequence[FlowStep[T]]):
        self.steps = steps

    def execute(
        self, model: T, context: FlowContext, io_facade: IOFacade[BaseModel]
    ) -> None:
        for step in self.steps:
            try:
                step.execute(model, context, io_facade)
            except (UserCancellationException, FlowCancelationByUserException) as e:
                raise FlowCancelationByUserException(e) from e
