from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, cast

from pydantic import BaseModel, Field

from exls.shared.adapters.ui.facade.interface import IIOFacade

T = TypeVar("T")


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
        self, model: T, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None: ...


class SequentialFlow(FlowStep[T]):
    """A step that executes a list of child steps in order."""

    def __init__(self, steps: Sequence[FlowStep[T]]):
        self.steps = steps

    def execute(
        self, model: T, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None:
        for step in self.steps:
            step.execute(model, context, io_facade)
