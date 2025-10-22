from __future__ import annotations

from typing import Optional

from exalsius_api_client.models.cluster_template import (
    ClusterTemplate as SdkClusterTemplate,
)
from pydantic import BaseModel, Field, StrictStr


class ClusterTemplateFilterParams(BaseModel):
    pass


class ClusterTemplate(BaseModel):
    sdk_model: SdkClusterTemplate = Field(
        ..., description="The SDK model of the cluster template"
    )

    @property
    def name(self) -> StrictStr:
        return self.sdk_model.name

    @property
    def description(self) -> Optional[StrictStr]:
        return self.sdk_model.description

    @property
    def k8s_version(self) -> Optional[StrictStr]:
        return self.sdk_model.k8s_version
