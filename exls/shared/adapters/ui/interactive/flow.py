from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseModel

from exls.shared.core.ports.display import OutputManager

T_Display = TypeVar("T_Display", bound=OutputManager[BaseModel])


class FlowContext(Dict[str, Any]):
    """Context to hold flow state."""

    pass


class FlowStep(ABC, Generic[T_Display]):
    """Abstract base class for flow steps."""

    @abstractmethod
    def execute(self, context: FlowContext, display: T_Display) -> None: ...


class SequentialFlow(FlowStep[T_Display]):
    """A step that executes a list of child steps in order."""

    def __init__(self, steps: List[FlowStep[T_Display]]):
        self.steps = steps

    def execute(self, context: FlowContext, display: T_Display) -> None:
        for step in self.steps:
            step.execute(context, display)
