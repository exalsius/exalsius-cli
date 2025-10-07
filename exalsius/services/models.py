from typing import ClassVar

from exalsius_api_client.models.service_deployment_create_request import (
    ServiceDeploymentCreateRequest,
)
from exalsius_api_client.models.service_template import ServiceTemplate
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

from exalsius.core.base.commands import BaseRequestDTO


class BaseServiceTemplateDTO(BaseModel):
    name: ClassVar[str] = ""

    def to_api_model(self) -> ServiceTemplate: ...


class NvidiaOperatorVariablesDTO(BaseSettings):
    # This is a placeholder for the variables of the nvidia operator service template
    model_config = SettingsConfigDict(alias_generator=to_camel, populate_by_name=True)


class NvidiaOperatorServiceTemplateDTO(BaseServiceTemplateDTO):
    name: ClassVar[str] = "gpu-operator-24-9-2"

    variables: NvidiaOperatorVariablesDTO = Field(
        ..., description="The variables of the nvidia operator service template"
    )

    def to_api_model(self) -> ServiceTemplate:
        return ServiceTemplate(
            name=self.name,
            variables=self.variables.model_dump(by_alias=True, exclude_none=True),
        )


class ServicesSingleServiceRequestDTO(BaseRequestDTO):
    service_id: str = Field(..., description="The ID of the service")


class ServicesListRequestDTO(BaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")


class ServicesGetRequestDTO(ServicesSingleServiceRequestDTO):
    pass


class ServicesDeleteRequestDTO(ServicesSingleServiceRequestDTO):
    pass


class ServicesDeployRequestDTO(BaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")
    name: str = Field(..., description="The name of the service")
    service_template: BaseServiceTemplateDTO = Field(
        ..., description="The service template factory to use"
    )

    def get_api_model(self) -> ServiceDeploymentCreateRequest:
        service_template: ServiceTemplate = self.service_template.to_api_model()
        return ServiceDeploymentCreateRequest(
            cluster_id=self.cluster_id,
            name=self.name,
            template=service_template,
        )
