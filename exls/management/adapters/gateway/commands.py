from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.cluster_template_list_response import (
    ClusterTemplateListResponse,
)
from exalsius_api_client.models.credentials_list_response import CredentialsListResponse
from exalsius_api_client.models.service_template_list_response import (
    ServiceTemplateListResponse,
)
from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse
from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exls.shared.adapters.gateway.sdk.command import ExalsiusSdkCommand


class BaseManagementSdkCommand[T_Cmd_Return](
    ExalsiusSdkCommand[ManagementApi, T_Cmd_Return]
):
    """Base class for all management commands."""

    def _execute_api_call(self) -> T_Cmd_Return:
        raise NotImplementedError


class ListClusterTemplatesSdkCommand(
    BaseManagementSdkCommand[ClusterTemplateListResponse]
):
    def _execute_api_call(self) -> ClusterTemplateListResponse:
        response: ClusterTemplateListResponse = self.api_client.list_cluster_templates()
        return response


class ListCredentialsSdkCommand(BaseManagementSdkCommand[CredentialsListResponse]):
    def _execute_api_call(self) -> CredentialsListResponse:
        response: CredentialsListResponse = self.api_client.list_credentials()
        return response


class ListServiceTemplatesSdkCommand(
    BaseManagementSdkCommand[ServiceTemplateListResponse]
):
    def _execute_api_call(self) -> ServiceTemplateListResponse:
        response: ServiceTemplateListResponse = self.api_client.list_service_templates()
        return response


class ListWorkspaceTemplatesSdkCommand(
    BaseManagementSdkCommand[WorkspaceTemplateListResponse]
):
    def _execute_api_call(self) -> WorkspaceTemplateListResponse:
        response: WorkspaceTemplateListResponse = (
            self.api_client.list_workspace_templates()
        )
        return response


class ListSshKeysSdkCommand(BaseManagementSdkCommand[SshKeysListResponse]):
    def _execute_api_call(self) -> SshKeysListResponse:
        response: SshKeysListResponse = self.api_client.list_ssh_keys()
        return response


class AddSshKeySdkCommand(BaseManagementSdkCommand[SshKeyCreateResponse]):
    def __init__(self, api_client: ManagementApi, request: SshKeyCreateRequest):
        super().__init__(api_client)

        self._request: SshKeyCreateRequest = request

    def _execute_api_call(self) -> SshKeyCreateResponse:
        response: SshKeyCreateResponse = self.api_client.add_ssh_key(
            ssh_key_create_request=self._request
        )
        return response


class DeleteSshKeySdkCommand(BaseManagementSdkCommand[str]):
    def __init__(self, api_client: ManagementApi, ssh_key_id: str):
        super().__init__(api_client)

        self._ssh_key_id: str = ssh_key_id

    def _execute_api_call(self) -> str:
        self.api_client.delete_ssh_key(ssh_key_id=self._ssh_key_id)
        return self._ssh_key_id
