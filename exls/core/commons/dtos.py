from pydantic import BaseModel, Field


class SaveFileRequestDTO(BaseModel):
    file_path: str = Field(..., description="The path to the file to save")
    content: str = Field(..., description="The content to save to the file")


class SaveFileResponseDTO(BaseModel):
    file_path: str = Field(..., description="The path to the file that was saved")
