from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional

from exalsius_api_client.models.service import Service as SdkService
from exalsius_api_client.models.service_template import ServiceTemplate
from pydantic import BaseModel, Field, StrictStr
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceFilterParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")


class BaseServiceTemplate(BaseModel):
    name: ClassVar[str] = ""

    def to_api_model(self) -> ServiceTemplate: ...


class NvidiaOperatorVariables(BaseSettings):
    # This is a placeholder for the variables of the nvidia operator service template
    model_config = SettingsConfigDict(alias_generator=to_camel, populate_by_name=True)


class NvidiaOperatorServiceTemplate(BaseServiceTemplate):
    name: ClassVar[str] = "gpu-operator-24-9-2"

    variables: NvidiaOperatorVariables = Field(
        ..., description="The variables of the nvidia operator service template"
    )

    def to_api_model(self) -> ServiceTemplate:
        return ServiceTemplate(
            name=self.name,
            variables=self.variables.model_dump(by_alias=True, exclude_none=True),
        )


class ServiceDeployParams(BaseModel):
    cluster_id: StrictStr = Field(..., description="The ID of the cluster")
    name: StrictStr = Field(..., description="The name of the service")
    service_template: BaseServiceTemplate = Field(
        ..., description="The service template factory to use"
    )


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
