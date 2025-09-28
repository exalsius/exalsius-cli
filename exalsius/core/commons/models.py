from typing import Optional

from pydantic import BaseModel, Field


class UnauthorizedError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ServiceWarning(Warning):
    def __init__(self, message: str):
        super().__init__(message)


class UnexpectedResponseWarning(ServiceWarning):
    def __init__(self, message: str):
        super().__init__(message)


class ServiceError(Exception):
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_type: Optional[str] = None,
    ):
        super().__init__(message)
        self.error_type: str = error_type or "service_error"
        self.message: str = message
        self.error_code: Optional[str] = error_code

    def __str__(self) -> str:
        return f"error_type: {self.error_type}, error_code: {self.error_code}, message: {self.message}"


class SaveFileRequestDTO(BaseModel):
    file_path: str = Field(..., description="The path to the file to save")
    content: str = Field(..., description="The content to save to the file")


class SaveFileResponseDTO(BaseModel):
    file_path: str = Field(..., description="The path to the file that was saved")
