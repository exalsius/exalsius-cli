from pydantic import BaseModel, Field


class TextMessageItem(BaseModel):
    """Text message item."""

    message: str = Field(..., description="The message.")
