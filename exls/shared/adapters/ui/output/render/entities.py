from pydantic import BaseModel, Field


class BaseRenderContext(BaseModel):
    """Base class for all render contexts."""


class TextMessageItem(BaseModel):
    """Text message item."""

    message: str = Field(..., description="The message.")
