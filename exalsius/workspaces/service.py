import time
from datetime import datetime
from typing import Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.models.workspace import Workspace
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.config import AppConfig
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError
from exalsius.workspaces.commands import (
    CreateWorkspaceCommand,
    DeleteWorkspaceCommand,
    GetWorkspaceCommand,
    ListWorkspacesCommand,
)
from exalsius.workspaces.models import (
    CreateWorkspaceRequestDTO,
    DeleteWorkspaceRequestDTO,
    GetWorkspaceRequestDTO,
    ResourcePoolDTO,
    WorkspaceBaseTemplateDTO,
    WorkspacesListRequestDTO,
)


class WorkspacesService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.workspaces_api: WorkspacesApi = WorkspacesApi(self.api_client)

    def list_workspaces(self, cluster_id: str) -> WorkspacesListResponse:
        return self.execute_command(
            ListWorkspacesCommand(
                request=WorkspacesListRequestDTO(
                    cluster_id=cluster_id,
                    api=self.workspaces_api,
                )
            )
        )

    def get_workspace(self, workspace_id: str) -> WorkspaceResponse:
        return self.execute_command(
            GetWorkspaceCommand(
                request=GetWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    workspace_id=workspace_id,
                )
            )
        )

    def _create_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        workspace_template: WorkspaceBaseTemplateDTO,
        to_be_deleted_at: Optional[datetime] = None,
        description: Optional[str] = None,
    ) -> WorkspaceCreateResponse:
        command: CreateWorkspaceCommand = CreateWorkspaceCommand(
            request=CreateWorkspaceRequestDTO(
                api=self.workspaces_api,
                cluster_id=cluster_id,
                name=name,
                resources=resources,
                template=workspace_template,
                to_be_deleted_at=to_be_deleted_at,
                description=description,
            )
        )
        return self.execute_command(command)

    def delete_workspace(self, workspace_id: str) -> WorkspaceDeleteResponse:
        return self.execute_command(
            DeleteWorkspaceCommand(
                request=DeleteWorkspaceRequestDTO(
                    api=self.workspaces_api,
                    workspace_id=workspace_id,
                )
            )
        )

    def _poll_workspace_creation(
        self,
        workspace_id: str,
    ) -> WorkspaceResponse:
        # TODO: We generally need to improve the user feedback on what exactly happened / is happening.
        timeout = self.config.workspace_creation_polling.timeout_seconds
        polling_interval = (
            self.config.workspace_creation_polling.polling_interval_seconds
        )
        start_time = time.time()

        workspace_response: Optional[WorkspaceResponse] = None
        while time.time() - start_time < timeout:
            workspace_response = self.get_workspace(workspace_id)
            workspace: Workspace = workspace_response.workspace
            if workspace.workspace_status == "RUNNING":
                # TODO: This handles backend-side edge case where the status is running but the access info is not available yet.
                time.sleep(polling_interval)
                workspace_response = self.get_workspace(workspace_id)
                break

            if workspace.workspace_status == "FAILED":
                raise ServiceError(
                    f"Workspace {workspace.name} ({workspace_id}) creation failed."
                )

            time.sleep(polling_interval)
        else:
            raise TimeoutError(
                f"Workspace {workspace.name} ({workspace_id}) did not become active in time. This might be normal for some workspace types. Please check the status manually."
            )

        return workspace_response
