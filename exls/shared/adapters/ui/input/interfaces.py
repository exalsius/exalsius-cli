from abc import ABC, abstractmethod
from typing import (
    Callable,
    List,
    Optional,
    Sequence,
    TypeVar,
)

from exls.shared.adapters.ui.input.values import DisplayChoice

T = TypeVar("T")


class IInputManager(ABC):
    @abstractmethod
    def ask_confirm(self, message: str, default: bool = False) -> bool: ...

    @abstractmethod
    def ask_text(
        self,
        message: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> str: ...

    @abstractmethod
    def ask_select_required(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: DisplayChoice[T],
    ) -> DisplayChoice[T]: ...

    @abstractmethod
    def ask_select_optional(
        self,
        message: str,
        choices: Sequence[DisplayChoice[T]],
        default: Optional[DisplayChoice[T]] = None,
    ) -> Optional[DisplayChoice[T]]: ...

    @abstractmethod
    def ask_checkbox(
        self, message: str, choices: Sequence[DisplayChoice[T]], min_choices: int = 1
    ) -> List[DisplayChoice[T]]: ...
