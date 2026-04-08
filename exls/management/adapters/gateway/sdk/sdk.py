import logging
from typing import List, Optional

from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.models.ssh_key_create_request import SshKeyCreateRequest
from exalsius_api_client.models.ssh_key_create_response import SshKeyCreateResponse
from exalsius_api_client.models.ssh_keys_list_response import SshKeysListResponse
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)
from exalsius_api_client.models.workspace_template import (
    WorkspaceTemplate as SdkWorkspaceTemplate,
)
from exalsius_api_client.models.workspace_template_list_response import (
    WorkspaceTemplateListResponse,
)

from exls.management.adapters.gateway.gateway import ManagementGateway
from exls.management.adapters.gateway.sdk.commands import (
    AddSshKeySdkCommand,
    DeleteSshKeySdkCommand,
    GetDashboardUrlSdkCommand,
    ListSshKeysSdkCommand,
    ListWorkspaceTemplatesSdkCommand,
)
from exls.management.core.domain import (
    SshKey,
    SshKeyScope,
    WorkspaceTemplate,
)

logger = logging.getLogger(__name__)


def _ssh_key_from_sdk_model(
    sdk_model: SshKeysListResponseSshKeysInner,
) -> Optional[SshKey]:
    if sdk_model.id is None or sdk_model.name is None:
        logger.warning(f"Unexpected SSH key response: {sdk_model}")
        return None
    scope = SshKeyScope(sdk_model.scope) if sdk_model.scope else SshKeyScope.PRIVATE
    return SshKey(id=sdk_model.id, name=sdk_model.name, scope=scope)


def _workspace_template_from_sdk_model(
    sdk_model: SdkWorkspaceTemplate,
) -> WorkspaceTemplate:
    return WorkspaceTemplate(
        name=sdk_model.name,
        description=sdk_model.description if sdk_model.description else "",
        variables=sdk_model.variables,
    )


class ManagementGatewaySdk(ManagementGateway):
    def __init__(self, management_api: ManagementApi):
        self._management_api = management_api

    def list_ssh_keys(self) -> List[SshKey]:
        command: ListSshKeysSdkCommand = ListSshKeysSdkCommand(self._management_api)
        response: SshKeysListResponse = command.execute()
        ssh_keys: List[SshKey] = []
        if response.ssh_keys:
            for ssh_key in response.ssh_keys:
                ssh_key_domain: Optional[SshKey] = _ssh_key_from_sdk_model(
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

    def create_ssh_key(
        self, name: str, base64_key_content: str, scope: str = "private"
    ) -> str:
        existing_ssh_keys: List[SshKey] = self.list_ssh_keys()
        if any(ssh_key.name == name for ssh_key in existing_ssh_keys):
            raise ValueError(f"SSH key with name {name} already exists")
        create_request: SshKeyCreateRequest = SshKeyCreateRequest(
            name=name,
            private_key_b64=base64_key_content,
            scope=scope,
        )
        command: AddSshKeySdkCommand = AddSshKeySdkCommand(
            self._management_api, request=create_request
        )
        response: SshKeyCreateResponse = command.execute()
        return response.ssh_key_id

    def list_workspace_templates(self) -> List[WorkspaceTemplate]:
        command: ListWorkspaceTemplatesSdkCommand = ListWorkspaceTemplatesSdkCommand(
            self._management_api
        )
        response: WorkspaceTemplateListResponse = command.execute()
        return [
            _workspace_template_from_sdk_model(sdk_model=wt)
            for wt in response.workspace_templates
        ]

    def get_dashboard_url(self) -> str:
        command: GetDashboardUrlSdkCommand = GetDashboardUrlSdkCommand(
            api_client=self._management_api
        )
        response = command.execute()
        return response.url
