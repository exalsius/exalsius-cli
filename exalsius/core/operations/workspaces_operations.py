from typing import Optional, Tuple

import exalsius_api_client
import exalsius_api_client.api_client
from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.error import Error as ExalsiusError
from exalsius_api_client.models.resource_pool import ResourcePool
from exalsius_api_client.models.workspace_create_request import WorkspaceCreateRequest
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspace_template import WorkspaceTemplate
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.core.operations.base import BaseOperation


class ListWorkspacesOperation(BaseOperation[WorkspacesListResponse]):
    def __init__(
        self, api_client: exalsius_api_client.api_client.ApiClient, cluster_id: str
    ):
        self.api_client = api_client
        self.cluster_id = cluster_id

    def execute(self) -> Tuple[Optional[WorkspacesListResponse], Optional[str]]:
        api_instance = WorkspacesApi(self.api_client)
        try:
            workspaces_list_response: WorkspacesListResponse = (
                api_instance.list_workspaces(cluster_id=self.cluster_id)
            )
            return workspaces_list_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class GetWorkspaceOperation(BaseOperation[WorkspaceResponse]):
    def __init__(
        self, api_client: exalsius_api_client.api_client.ApiClient, workspace_id: str
    ):
        self.api_client = api_client
        self.workspace_id = workspace_id

    def execute(self) -> Tuple[Optional[WorkspaceResponse], Optional[str]]:
        api_instance = WorkspacesApi(self.api_client)
        try:
            workspace_response: WorkspaceResponse = api_instance.describe_workspace(
                workspace_id=self.workspace_id
            )
            return workspace_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class CreateWorkspaceOperation(BaseOperation[WorkspaceCreateResponse]):
    def __init__(
        self,
        api_client: exalsius_api_client.api_client.ApiClient,
        cluster_id: str,
        name: str,
        template: WorkspaceTemplate,
        owner: str,
        gpu_count: int,
    ):
        self.api_client: exalsius_api_client.api_client.ApiClient = api_client
        self.cluster_id: str = cluster_id
        self.name: str = name
        self.owner: str = owner
        self.template: WorkspaceTemplate = template
        # TODO: These are hacky fixes that need to be fixed in the backend.
        self.template.variables["deploymentName"] = name
        self.template.variables["memoryGB"] = "128"
        self.template.variables["podStorage"] = "200Gi"
        self.template.variables["storageGB"] = "200"
        self.resources: ResourcePool = ResourcePool(
            gpu_count=gpu_count,
            gpu_vendor="NVIDIA",
            gpu_type="NVIDIA-A100-80GB-PCIe",
            cpu_cores=32,
            memory_gb=128,
            storage_gb=200,
        )

    def execute(self) -> Tuple[Optional[WorkspaceCreateResponse], Optional[str]]:
        api_instance = WorkspacesApi(self.api_client)
        try:
            workspace_create_request: WorkspaceCreateRequest = WorkspaceCreateRequest(
                cluster_id=self.cluster_id,
                name=self.name,
                template=self.template,
                resources=self.resources,
                owner=self.owner,
            )

            workspace_create_response: WorkspaceCreateResponse = (
                api_instance.create_workspace(workspace_create_request)
            )
            return workspace_create_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)


class CreateWorkspacePodOperation(CreateWorkspaceOperation):
    def __init__(
        self,
        api_client: exalsius_api_client.api_client.ApiClient,
        cluster_id: str,
        name: str,
        owner: str,
        gpu_count: int,
    ):
        template = WorkspaceTemplate(
            name="vscode-devcontainer-template",
            description=f"{owner}'s amazing workspace",
            variables={},
        )
        super().__init__(api_client, cluster_id, name, template, owner, gpu_count)


class CreateWorkspaceJupyterOperation(CreateWorkspaceOperation):
    def __init__(
        self,
        api_client: exalsius_api_client.api_client.ApiClient,
        cluster_id: str,
        name: str,
        owner: str,
        gpu_count: int,
        jupyter_password: Optional[str] = None,
    ):
        template = WorkspaceTemplate(
            name="jupyter-notebook-template",
            description=f"{owner}'s amazing jupyter notebook workspace",
            variables={
                "deploymentImage": "tensorflow/tensorflow:2.18.0-gpu-jupyter",
            },
        )
        if jupyter_password:
            template.variables["notebookPassword"] = jupyter_password
        super().__init__(api_client, cluster_id, name, template, owner, gpu_count)


class DeleteWorkspaceOperation(BaseOperation[WorkspaceDeleteResponse]):
    def __init__(
        self, api_client: exalsius_api_client.api_client.ApiClient, workspace_id: str
    ):
        self.api_client = api_client
        self.workspace_id = workspace_id

    def execute(self) -> Tuple[Optional[WorkspaceDeleteResponse], Optional[str]]:
        api_instance = WorkspacesApi(self.api_client)
        try:
            workspace_delete_response: WorkspaceDeleteResponse = (
                api_instance.delete_workspace(workspace_id=self.workspace_id)
            )
            return workspace_delete_response, None
        except ApiException as e:
            if e.body:
                error = ExalsiusError.from_json(e.body)
                if error:
                    return None, str(error.detail)
                else:
                    return None, str(e)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)
