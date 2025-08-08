from enum import StrEnum

from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.models.service_template import ServiceTemplate
from pydantic import Field

from exalsius.core.base.models import BaseRequestDTO


class ServiceTemplates(StrEnum):
    NVIDIA_GPU_OPERATOR = "nvidia_gpu_operator"

    def create_service_template(self) -> ServiceTemplate:
        match self:
            case ServiceTemplates.NVIDIA_GPU_OPERATOR:
                return ServiceTemplate(
                    name="gpu-operator-24-9-2",
                    description="nvidia gpu operator",
                    variables={
                        "gpu-operator": {
                            "operator": {
                                "defaultRuntime": "containerd",
                            },
                            "toolkit": {
                                "env": [
                                    {
                                        "name": "CONTAINERD_CONFIG",
                                        "value": "/etc/k0s/containerd.d/nvidia.toml",
                                    },
                                    {
                                        "name": "CONTAINERD_SOCKET",
                                        "value": "/run/k0s/containerd.sock",
                                    },
                                    {
                                        "name": "CONTAINERD_RUNTIME_CLASS",
                                        "value": "nvidia",
                                    },
                                ]
                            },
                            "dcgmExporter": {
                                "serviceMonitor": {
                                    "enabled": True,
                                    "interval": "15s",
                                    "honorLabels": True,
                                    "additionalLabels": {},
                                }
                            },
                        }
                    },
                )


class ServicesBaseRequestDTO(BaseRequestDTO):
    api: ServicesApi = Field(..., description="The API client")


class ServicesSingleServiceRequestDTO(ServicesBaseRequestDTO):
    service_id: str = Field(..., description="The ID of the service")


class ServicesListRequestDTO(ServicesBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")


class ServicesGetRequestDTO(ServicesSingleServiceRequestDTO):
    pass


class ServicesDeleteRequestDTO(ServicesSingleServiceRequestDTO):
    pass


class ServicesDeployRequestDTO(ServicesBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")
    service_template_factory: ServiceTemplates = Field(
        ..., description="The service template factory to use"
    )
