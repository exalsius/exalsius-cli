import logging
from typing import Optional

from exalsius_api_client.models.cluster_template import (
    ClusterTemplate as SdkClusterTemplate,
)
from exalsius_api_client.models.credentials import Credentials as SdkCredentials
from exalsius_api_client.models.service_template import (
    ServiceTemplate as SdkServiceTemplate,
)
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)
from exalsius_api_client.models.workspace_template import (
    WorkspaceTemplate as SdkWorkspaceTemplate,
)

from exls.management.core.domain import (
    ClusterTemplate,
    Credentials,
    ServiceTemplate,
    SshKey,
    WorkspaceTemplate,
)


def ssh_key_from_sdk_model(
    sdk_model: SshKeysListResponseSshKeysInner,
) -> Optional[SshKey]:
    if sdk_model.id is None or sdk_model.name is None:
        logging.warning(f"Unexpected SSH key response: {sdk_model}")
        return None
    return SshKey(id=sdk_model.id, name=sdk_model.name)


def cluster_template_from_sdk_model(
    sdk_model: SdkClusterTemplate,
) -> ClusterTemplate:
    return ClusterTemplate(
        name=sdk_model.name,
        description=sdk_model.description,
        k8s_version=sdk_model.k8s_version,
    )


def credentials_from_sdk_model(
    sdk_model: SdkCredentials,
) -> Credentials:
    return Credentials(
        name=sdk_model.name,
        description=sdk_model.description,
    )


def service_template_from_sdk_model(
    sdk_model: SdkServiceTemplate,
) -> ServiceTemplate:
    return ServiceTemplate(
        name=sdk_model.name,
        description=sdk_model.description if sdk_model.description else "",
        variables=sdk_model.variables,
    )


def workspace_template_from_sdk_model(
    sdk_model: SdkWorkspaceTemplate,
) -> WorkspaceTemplate:
    return WorkspaceTemplate(
        name=sdk_model.name,
        description=sdk_model.description if sdk_model.description else "",
        variables=sdk_model.variables,
    )
