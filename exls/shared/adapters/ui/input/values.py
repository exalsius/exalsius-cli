from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from exls.shared.core.domain import ExalsiusWarning

T = TypeVar("T")


class UserCancellationException(ExalsiusWarning):
    """Raised when the user cancels an interactive operation."""


class DisplayChoice(BaseModel, Generic[T]):
    title: str = Field(..., description="The title of the choice.")
    value: T = Field(..., description="The value of the choice.")
