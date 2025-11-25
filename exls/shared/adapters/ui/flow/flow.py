from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel

from exls.shared.adapters.ui.facade.interface import IIOFacade

T = TypeVar("T")


class FlowStep(Generic[T], ABC):
    """Abstract base class for flow steps."""

    @abstractmethod
    def execute(self, model: T, io_facade: IIOFacade[BaseModel]) -> None: ...


class SequentialFlow(FlowStep[T]):
    """A step that executes a list of child steps in order."""

    def __init__(self, steps: Sequence[FlowStep[T]]):
        self.steps = steps

    def execute(self, model: T, io_facade: IIOFacade[BaseModel]) -> None:
        for step in self.steps:
            step.execute(model, io_facade)
