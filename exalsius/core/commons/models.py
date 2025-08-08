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
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}"


class SaveFileRequestDTO(BaseModel):
    file_path: str = Field(..., description="The path to the file to save")
    content: str = Field(..., description="The content to save to the file")


class SaveFileResponseDTO(BaseModel):
    file_path: str = Field(..., description="The path to the file that was saved")
