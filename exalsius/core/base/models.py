from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseRequestDTO(BaseModel):
    """Base request DTO that commands receive and use internally to perform commands."""

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ErrorDTO(BaseModel):
    """Error DTO for renderers."""

    message: str
    error_type: Optional[str] = None
    error_code: Optional[str] = None
