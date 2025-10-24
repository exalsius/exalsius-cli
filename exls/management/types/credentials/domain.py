from __future__ import annotations

from exalsius_api_client.models.credentials import Credentials as SdkCredentials
from pydantic import BaseModel, Field


class Credentials(BaseModel):
    sdk_model: SdkCredentials = Field(
        ..., description="The SDK model of the credentials"
    )

    @property
    def name(self) -> str:
        return self.sdk_model.name

    @property
    def description(self) -> str:
        return self.sdk_model.description
