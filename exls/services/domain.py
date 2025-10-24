from __future__ import annotations

from datetime import datetime
from typing import Optional

from exalsius_api_client.models.service import Service as SdkService
from pydantic import BaseModel, Field, StrictStr


class Service(BaseModel):
    sdk_model: SdkService = Field(..., description="The SDK model of the service")

    @property
    def id(self) -> StrictStr:
        if self.sdk_model.id is None:
            raise ValueError("ID is None")
        return self.sdk_model.id

    @property
    def cluster_id(self) -> StrictStr:
        return self.sdk_model.cluster_id

    @property
    def name(self) -> StrictStr:
        return self.sdk_model.name

    @property
    def service_template(self) -> StrictStr:
        return self.sdk_model.template.name

    @property
    def created_at(self) -> Optional[datetime]:
        return self.sdk_model.created_at
