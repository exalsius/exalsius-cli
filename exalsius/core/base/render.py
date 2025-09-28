from typing import List, Protocol, TypeVar

T_RenderInput_Inv = TypeVar("T_RenderInput_Inv")
T_RenderInput_Contra = TypeVar("T_RenderInput_Contra", contravariant=True)
T_RenderOutput_Cov = TypeVar("T_RenderOutput_Cov", covariant=True)


class BaseListRenderer(Protocol[T_RenderInput_Inv, T_RenderOutput_Cov]):
    """Base list renderer."""

    def render(self, data: List[T_RenderInput_Inv]) -> T_RenderOutput_Cov: ...


class BaseSingleItemRenderer(Protocol[T_RenderInput_Contra, T_RenderOutput_Cov]):
    """Base single item renderer."""

    def render(self, data: T_RenderInput_Contra) -> T_RenderOutput_Cov: ...
