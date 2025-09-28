import time
from datetime import datetime
from typing import Any, List, Optional

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.exceptions import ApiException
from exalsius_api_client.models.workspace import Workspace
from exalsius_api_client.models.workspace_create_response import WorkspaceCreateResponse
from exalsius_api_client.models.workspace_delete_response import WorkspaceDeleteResponse
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse

from exalsius.config import AppConfig
from exalsius.core.base.commands import BaseCommand
from exalsius.core.base.service import BaseServiceWithAuth
from exalsius.core.commons.models import ServiceError, ServiceWarning
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

WORKSPACES_API_ERROR_TYPE: str = "WorkspacesApiError"


class WorkspacesService(BaseServiceWithAuth):
    def __init__(self, config: AppConfig, access_token: str):
        super().__init__(config, access_token)
        self.workspaces_api: WorkspacesApi = WorkspacesApi(self.api_client)

    def _execute_command(self, command: BaseCommand) -> Any:
        try:
            return command.execute()
        except ApiException as e:
            raise ServiceError(
                message=f"api error while executing command {command.__class__.__name__}: {e.body}",  # pyright: ignore[reportUnknownMemberType]
                error_code=(
                    str(
                        e.status  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    )
                    if e.status  # pyright: ignore[reportUnknownMemberType]
                    else None
                ),
                error_type=WORKSPACES_API_ERROR_TYPE,
            )
        except Exception as e:
            raise ServiceError(
                message=f"unexpected error while executing command {command.__class__.__name__}: {e}",
                error_type=WORKSPACES_API_ERROR_TYPE,
            )

    def list_workspaces(self, cluster_id: str) -> List[Workspace]:
        command: ListWorkspacesCommand = ListWorkspacesCommand(
            WorkspacesListRequestDTO(
                api=self.workspaces_api,
                cluster_id=cluster_id,
            )
        )
        response: WorkspacesListResponse = self._execute_command(command)
        return response.workspaces

    def get_workspace(self, workspace_id: str) -> Workspace:
        command: GetWorkspaceCommand = GetWorkspaceCommand(
            GetWorkspaceRequestDTO(
                api=self.workspaces_api,
                workspace_id=workspace_id,
            )
        )
        response: WorkspaceResponse = self._execute_command(command)
        return response.workspace

    def _create_workspace(
        self,
        cluster_id: str,
        name: str,
        resources: ResourcePoolDTO,
        workspace_template: WorkspaceBaseTemplateDTO,
        to_be_deleted_at: Optional[datetime] = None,
        description: Optional[str] = None,
    ) -> str:
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
        response: WorkspaceCreateResponse = self._execute_command(command)
        return response.workspace_id

    def delete_workspace(self, workspace_id: str) -> str:
        command: DeleteWorkspaceCommand = DeleteWorkspaceCommand(
            DeleteWorkspaceRequestDTO(
                api=self.workspaces_api,
                workspace_id=workspace_id,
            )
        )
        response: WorkspaceDeleteResponse = self._execute_command(command)
        return response.workspace_id

    def poll_workspace_creation(
        self,
        workspace_id: str,
    ) -> Workspace:
        # TODO: We generally need to improve the user feedback on what exactly happened / is happening.
        timeout = self.config.workspace_creation_polling.timeout_seconds
        polling_interval = (
            self.config.workspace_creation_polling.polling_interval_seconds
        )
        start_time = time.time()

        workspace: Optional[Workspace] = None
        while time.time() - start_time < timeout:
            workspace = self.get_workspace(workspace_id)
            if workspace.workspace_status == "RUNNING":
                break
            if workspace.workspace_status == "FAILED":
                raise ServiceWarning(
                    f"workspace {workspace.name} ({workspace_id}) creation failed. "
                    + f"Status of workspace: {workspace.workspace_status}"
                )

            time.sleep(polling_interval)
        else:
            # Edge case the timeout is reached before the workspace is polled. Should not happen.
            if not workspace:
                workspace = self.get_workspace(workspace_id)
            raise TimeoutError(
                f"workspace {workspace_id} did not become active in time."
            )

        return workspace
