from typing import List, Protocol

from exalsius.core.base.render import (
    BaseListRenderer,
    BaseSingleItemRenderer,
    T_RenderInput_Contra,
    T_RenderInput_Inv,
    T_RenderOutput_Cov,
)


class BaseListDisplay(Protocol[T_RenderInput_Inv, T_RenderOutput_Cov]):
    """Base display manager."""

    @property
    def renderer(self) -> BaseListRenderer[T_RenderInput_Inv, T_RenderOutput_Cov]: ...

    def display(self, data: List[T_RenderInput_Inv]) -> None: ...


class BaseSingleItemDisplay(Protocol[T_RenderInput_Contra, T_RenderOutput_Cov]):
    """Base display manager."""

    @property
    def renderer(
        self,
    ) -> BaseSingleItemRenderer[T_RenderInput_Contra, T_RenderOutput_Cov]: ...

    def display(self, data: T_RenderInput_Contra) -> None: ...


class BaseConfirmationDisplay(Protocol[T_RenderInput_Contra, T_RenderOutput_Cov]):
    """Base display manager."""

    @property
    def renderer(
        self,
    ) -> BaseSingleItemRenderer[T_RenderInput_Contra, T_RenderOutput_Cov]: ...

    def display(self, data: T_RenderInput_Contra) -> bool: ...
