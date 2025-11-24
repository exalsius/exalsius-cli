from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar

from pydantic import BaseModel

from exls.shared.adapters.ui.facade.interface import IIOFacade

T = TypeVar("T")


class FlowContext(
    Dict[
        str,
        Any,
    ]
):
    """Context to hold flow state."""

    pass


class FlowStep(ABC):
    """Abstract base class for flow steps."""

    @abstractmethod
    def execute(
        self, context: FlowContext, io_facade: IIOFacade[BaseModel]
    ) -> None: ...


class SequentialFlow(FlowStep):
    """A step that executes a list of child steps in order."""

    def __init__(self, steps: List[FlowStep]):
        self.steps = steps

    def execute(self, context: FlowContext, io_facade: IIOFacade[BaseModel]) -> None:
        for step in self.steps:
            step.execute(context, io_facade)
