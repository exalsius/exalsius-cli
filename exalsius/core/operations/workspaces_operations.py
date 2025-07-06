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

from exalsius.core.operations.base import BaseOperation, ListOperation


class ListWorkspacesOperation(ListOperation[WorkspacesListResponse]):
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
            error = ExalsiusError.from_json(e.body).detail
            return None, error.detail
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
            error = ExalsiusError.from_json(e.body).detail
            return None, str(error.detail)
        except Exception as e:
            return None, str(e)


class CreateWorkspaceOperation(BaseOperation[WorkspaceCreateResponse]):
    def __init__(
        self,
        api_client: exalsius_api_client.api_client.ApiClient,
        cluster_id: str,
        name: str,
        owner: str,
        gpu_count: int,
    ):
        self.api_client: exalsius_api_client.api_client.ApiClient = api_client
        self.cluster_id: str = cluster_id
        self.name: str = name
        self.owner: str = owner
        self.workspace_template: WorkspaceTemplate = WorkspaceTemplate(
            name="vscode-devcontainer-template",
            description="string",
            variables={},
        )
        self.resources: ResourcePool = ResourcePool(
            gpu_count=gpu_count,
            gpu_vendor="NVIDIA",
            gpu_type="NVIDIA-A100-80GB-PCIe",
            cpu_cores=4,
            memory_gb=16,
            storage_gb=100,
        )

    def execute(self) -> Tuple[Optional[WorkspaceCreateResponse], Optional[str]]:
        api_instance = WorkspacesApi(self.api_client)
        try:
            workspace_create_request: WorkspaceCreateRequest = WorkspaceCreateRequest(
                cluster_id=self.cluster_id,
                name=self.name,
                template=self.workspace_template,
                resources=self.resources,
                owner=self.owner,
            )
            workspace_create_response: WorkspaceCreateResponse = (
                api_instance.create_workspace(workspace_create_request)
            )
            return workspace_create_response, None
        except ApiException as e:
            error = ExalsiusError.from_json(e.body).detail
            return None, str(error.detail)
        except Exception as e:
            return None, str(e)


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
            error = ExalsiusError.from_json(e.body).detail
            return None, str(error.detail)
        except Exception as e:
            return None, str(e)
