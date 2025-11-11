from typing import Callable, List, Optional, Protocol, TypeVar

from pydantic import BaseModel, Field, StrictStr

from exls.core.base.exceptions import ExalsiusWarning
from exls.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
    T_RenderInput_Contra,
    T_RenderInput_Inv,
    T_RenderOutput_Cov,
)

T_Choice = TypeVar("T_Choice")
T_TextEditor_Output_Cov = TypeVar("T_TextEditor_Output_Cov", covariant=True)


class UserCancellationException(ExalsiusWarning):
    """Raised when the user cancels an interactive operation."""


class ErrorDisplayModel(BaseModel):
    """Error model for renderers."""

    message: str = Field(description="The error message.")


class BaseListDisplay(Protocol[T_RenderInput_Inv, T_RenderOutput_Cov]):
    """Base display manager for lists of items."""

    @property
    def renderer(self) -> BaseListRenderer[T_RenderInput_Inv, T_RenderOutput_Cov]: ...

    def display(self, data: List[T_RenderInput_Inv]) -> None: ...


class BaseSingleItemDisplay(Protocol[T_RenderInput_Contra, T_RenderOutput_Cov]):
    """Base display manager for single items."""

    @property
    def renderer(
        self,
    ) -> BaseSingleItemRenderer[T_RenderInput_Contra, T_RenderOutput_Cov]: ...

    def display(self, data: T_RenderInput_Contra) -> None: ...


class BaseConfirmationDisplay(Protocol[T_RenderInput_Contra, T_RenderOutput_Cov]):
    """Base display manager for confirmation items."""

    @property
    def renderer(
        self,
    ) -> BaseSingleItemRenderer[T_RenderInput_Contra, T_RenderOutput_Cov]: ...

    def display(self, data: T_RenderInput_Contra) -> bool: ...


class BaseSpinnerDisplay(Protocol[T_RenderInput_Contra, T_RenderOutput_Cov]):
    """Base display manager for spinner items."""

    @property
    def renderer(
        self,
    ) -> BaseSingleItemRenderer[T_RenderInput_Contra, T_RenderOutput_Cov]: ...

    def start_display(self, data: T_RenderInput_Contra) -> None: ...
    def stop_display(self) -> None: ...


class BaseTextEditor(Protocol[T_RenderInput_Contra, T_TextEditor_Output_Cov]):
    """Base display manager for text editor items."""

    @property
    def renderer(
        self,
    ) -> BaseSingleItemRenderer[T_RenderInput_Contra, str]: ...

    def display(self, data: T_RenderInput_Contra) -> T_TextEditor_Output_Cov: ...


class InteractiveDisplay(Protocol[T_Choice]):
    """Protocol for interactive display operations."""

    def ask_text(
        self,
        message: StrictStr,
        default: Optional[StrictStr] = None,
        validator: Optional[Callable[[str], bool | str]] = None,
    ) -> StrictStr: ...
    def ask_select_required(
        self,
        message: StrictStr,
        choices: List[T_Choice],
        default: T_Choice,
    ) -> T_Choice: ...
    def ask_select_optional(
        self,
        message: StrictStr,
        choices: List[T_Choice],
        default: Optional[T_Choice] = None,
    ) -> Optional[T_Choice]: ...
    def ask_confirm(self, message: StrictStr, default: bool = False) -> bool: ...
    def ask_checkbox(
        self, message: StrictStr, choices: List[T_Choice], min_choices: int = 1
    ) -> List[T_Choice]: ...
