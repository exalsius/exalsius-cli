from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar, Union

from exls.shared.adapters.ui.display.interfaces import (
    IBaseInputManager,
    IMessageOutputManager,
)

T_Display = TypeVar("T_Display", bound=Union[IBaseInputManager, IMessageOutputManager])


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
