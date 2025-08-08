import datetime
import enum
from abc import abstractmethod
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.resource_pool import ResourcePool
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from pydantic import BaseModel, Field

from exalsius.core.base.models import BaseRequestDTO


class WorkspaceTemplates(str, enum.Enum):
    POD = "pod"
    JUPYTER = "jupyter"
    LLM_INFERENCE = "llm-inference"

    def create_workspace_template(self) -> WorkspaceTemplate:
        match self:
            case WorkspaceTemplates.POD:
                return WorkspaceTemplate(
                    name="vscode-devcontainer-template",
                    variables={
                        "deploymentName": "devcontainer",
                        "deploymentNamespace": "default",
                        "deploymentImage": "nvcr.io/nvidia/pytorch:25.01-py3",
                        "podStorage": "20Gi",
                        "podShmSize": "8Gi",
                    },
                )
            case WorkspaceTemplates.JUPYTER:
                return WorkspaceTemplate(
                    name="jupyter-notebook-template",
                    variables={
                        "deploymentName": "my-notebook",
                        "deploymentNamespace": "default",
                        "deploymentImage": "tensorflow/tensorflow:2.18.0-gpu-jupyter",
                        "enablePvcDeletion": "false",
                        "notebookPassword": "mysecurepassword",
                        "podStorage": "20Gi",
                    },
                )
            case WorkspaceTemplates.LLM_INFERENCE:
                return WorkspaceTemplate(
                    name="ray-llm-service-template",
                    variables={
                        "deploymentName": "my-llm-service",
                        "deploymentNamespace": "default",
                        "deploymentImage": "rayproject/ray-ml:2.46.0.0e19ea",
                        "numModelReplicas": "1",
                        "runtimeEnvironmentPipPackages": "numpy==1.26.4,vllm>=0.9.0,ray==2.46.0",
                        "llmModelName": "microsoft/phi-4",
                        "tensorParallelSize": "1",
                        "pipelineParallelSize": "1",
                        "placementGroupStrategy": "PACK",
                        "cpuPerActor": "8",
                        "gpuPerActor": "1",
                    },
                )


class WorkspacesBaseRequestDTO(BaseRequestDTO):
    api: WorkspacesApi = Field(..., description="The API client")


class WorkspacesListRequestDTO(WorkspacesBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")


class GetWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    workspace_id: str = Field(..., description="The ID of the workspace")


class WorkspaceBaseTemplateDTO(BaseModel):
    template_type: WorkspaceTemplates = Field(
        ..., description="The type of the workspace template"
    )

    @abstractmethod
    def to_api_model(self) -> WorkspaceTemplate:
        pass


class WorkspacePodTemplateDTO(WorkspaceBaseTemplateDTO):
    template_type: WorkspaceTemplates = WorkspaceTemplates.POD

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = self.template_type.create_workspace_template()
        return template


class WorkspaceJupyterTemplateDTO(WorkspaceBaseTemplateDTO):
    template_type: WorkspaceTemplates = WorkspaceTemplates.JUPYTER

    jupyter_password: Optional[str] = Field(
        None, description="The password of the Jupyter notebook"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = self.template_type.create_workspace_template()
        if self.jupyter_password is not None:
            template.variables["jupyterPassword"] = self.jupyter_password
        return template


class WorkspaceLLMInferenceTemplateDTO(WorkspaceBaseTemplateDTO):
    template_type: WorkspaceTemplates = WorkspaceTemplates.LLM_INFERENCE

    huggingface_model: str = Field(
        ..., description="The model of the workspace template"
    )
    huggingface_token: Optional[str] = Field(
        None, description="The token of the workspace template"
    )

    def to_api_model(self) -> WorkspaceTemplate:
        template: WorkspaceTemplate = self.template_type.create_workspace_template()
        template.variables["huggingfaceModel"] = self.huggingface_model
        if self.huggingface_token is not None:
            template.variables["huggingFaceToken"] = self.huggingface_token
        return template


class ResourcePoolDTO(BaseModel):
    gpu_count: int = Field(..., description="The number of GPUs")
    gpu_type: Optional[str] = Field(None, description="The type of the GPUs")
    gpu_vendor: Optional[str] = Field(None, description="The vendor of the GPUs")
    cpu_cores: int = Field(..., description="The number of CPU cores")
    memory_gb: int = Field(..., description="The amount of memory in GB")
    storage_gb: int = Field(..., description="The amount of storage in GB")

    def to_api_model(self) -> ResourcePool:
        return ResourcePool(
            gpu_count=self.gpu_count,
            gpu_type=self.gpu_type,
            gpu_vendor=self.gpu_vendor,
            cpu_cores=self.cpu_cores,
            memory_gb=self.memory_gb,
            storage_gb=self.storage_gb,
        )


class CreateWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    cluster_id: str = Field(..., description="The ID of the cluster")
    name: str = Field(..., description="The name of the workspace")
    description: Optional[str] = Field(
        None, description="The description of the workspace"
    )
    resources: ResourcePoolDTO = Field(
        ..., description="The resources of the workspace"
    )
    template: WorkspaceBaseTemplateDTO = Field(
        ..., description="The template of the workspace"
    )
    to_be_deleted_at: Optional[datetime.datetime] = Field(
        None, description="The date and time the workspace will be deleted"
    )

    def to_api_model(self) -> WorkspaceCreateRequest:
        return WorkspaceCreateRequest(
            cluster_id=self.cluster_id,
            name=self.name,
            resources=self.resources.to_api_model(),
            template=self.template.to_api_model(),
            description=self.description,
            to_be_deleted_at=self.to_be_deleted_at,
        )


class DeleteWorkspaceRequestDTO(WorkspacesBaseRequestDTO):
    workspace_id: str = Field(..., description="The ID of the workspace")
