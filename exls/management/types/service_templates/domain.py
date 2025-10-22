from __future__ import annotations

from typing import List

from exalsius_api_client.models.service_template import (
    ServiceTemplate as SdkServiceTemplate,
)
from pydantic import BaseModel, Field


class ServiceTemplateFilterParams(BaseModel):
    pass


class ServiceTemplate(BaseModel):
    sdk_model: SdkServiceTemplate = Field(
        ..., description="The SDK model of the service template"
    )

    @property
    def name(self) -> str:
        return self.sdk_model.name

    @property
    def description(self) -> str:
        return self.sdk_model.description or ""

    @property
    def variables(self) -> List[str]:
        return list(self.sdk_model.variables.keys())
