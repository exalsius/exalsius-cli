from typing import List, Optional, Protocol

from pydantic import BaseModel

from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
    T_RenderInput_Contra,
    T_RenderInput_Inv,
    T_RenderOutput_Cov,
)


class ErrorDisplayDTO(BaseModel):
    """Error DTO for renderers."""

    message: str
    error_type: Optional[str] = None
    error_code: Optional[str] = None


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
