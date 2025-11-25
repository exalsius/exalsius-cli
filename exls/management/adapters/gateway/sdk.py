from typing import List, Optional

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

from exls.management.adapters.gateway.commands import (
    AddSshKeySdkCommand,
    DeleteSshKeySdkCommand,
    ListClusterTemplatesSdkCommand,
    ListCredentialsSdkCommand,
    ListServiceTemplatesSdkCommand,
    ListSshKeysSdkCommand,
    ListWorkspaceTemplatesSdkCommand,
)
from exls.management.adapters.gateway.mappers import (
    cluster_template_from_sdk_model,
    credentials_from_sdk_model,
    service_template_from_sdk_model,
    ssh_key_from_sdk_model,
    workspace_template_from_sdk_model,
)
from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)
from exls.management.core.ports import IManagementGateway
from exls.shared.adapters.gateway.sdk.service import create_api_client


class ManagementGatewaySdk(IManagementGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def list_ssh_keys(self) -> List[SshKey]:
        command: ListSshKeysSdkCommand = ListSshKeysSdkCommand(self._management_api)
        response: SshKeysListResponse = command.execute()
        ssh_keys: List[SshKey] = []
        if response.ssh_keys:
            for ssh_key in response.ssh_keys:
                ssh_key_domain: Optional[SshKey] = ssh_key_from_sdk_model(
                    sdk_model=ssh_key
                )
                if ssh_key_domain is not None:
                    ssh_keys.append(ssh_key_domain)
        return ssh_keys

    def delete_ssh_key(self, ssh_key_id: str) -> str:
        command: DeleteSshKeySdkCommand = DeleteSshKeySdkCommand(
            self._management_api, ssh_key_id
        )
        command.execute()
        return ssh_key_id

    def import_ssh_key(self, name: str, base64_key_content: str) -> str:
        existing_ssh_keys: List[SshKey] = self.list_ssh_keys()
        if any(ssh_key.name == name for ssh_key in existing_ssh_keys):
            raise ValueError(f"SSH key with name {name} already exists")
        create_request: SshKeyCreateRequest = SshKeyCreateRequest(
            name=name,
            private_key_b64=base64_key_content,
        )
        command: AddSshKeySdkCommand = AddSshKeySdkCommand(
            self._management_api, request=create_request
        )
        response: SshKeyCreateResponse = command.execute()
        return response.ssh_key_id

    def list_cluster_templates(self) -> List[ClusterTemplate]:
        command: ListClusterTemplatesSdkCommand = ListClusterTemplatesSdkCommand(
            self._management_api
        )
        response: ClusterTemplateListResponse = command.execute()
        return [
            cluster_template_from_sdk_model(sdk_model=ct)
            for ct in response.cluster_templates
        ]

    def list_credentials(self) -> List[Credentials]:
        command: ListCredentialsSdkCommand = ListCredentialsSdkCommand(
            self._management_api
        )
        response: CredentialsListResponse = command.execute()
        return [credentials_from_sdk_model(sdk_model=c) for c in response.credentials]

    def list_service_templates(self) -> List[ServiceTemplate]:
        command: ListServiceTemplatesSdkCommand = ListServiceTemplatesSdkCommand(
            self._management_api
        )
        response: ServiceTemplateListResponse = command.execute()
        return [
            service_template_from_sdk_model(sdk_model=st)
            for st in response.service_templates
        ]

    def list_workspace_templates(self) -> List[WorkspaceTemplate]:
        command: ListWorkspaceTemplatesSdkCommand = ListWorkspaceTemplatesSdkCommand(
            self._management_api
        )
        response: WorkspaceTemplateListResponse = command.execute()
        return [
            workspace_template_from_sdk_model(sdk_model=wt)
            for wt in response.workspace_templates
        ]


def create_management_gateway(
    backend_host: str,
    access_token: str,
) -> ManagementGatewaySdk:
    management_api: ManagementApi = ManagementApi(
        create_api_client(backend_host=backend_host, access_token=access_token)
    )
    return ManagementGatewaySdk(management_api=management_api)
