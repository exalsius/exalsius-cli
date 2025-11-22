from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.api.management_api import ManagementApi
from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration
from exls.clusters.gateway.base import ClustersGateway
from exls.clusters.gateway.sdk import ClustersGatewaySdk
from exls.management.types.cluster_templates.gateway.base import (
    ClusterTemplatesGateway,
)
from exls.management.types.cluster_templates.gateway.sdk import (
    ClusterTemplatesGatewaySdk,
)
from exls.management.types.credentials.gateway.base import CredentialsGateway
from exls.management.types.credentials.gateway.sdk import CredentialsGatewaySdk
from exls.management.types.service_templates.gateway.base import (
    ServiceTemplatesGateway,
)
from exls.management.types.service_templates.gateway.sdk import (
    ServiceTemplatesGatewaySdk,
)
from exls.management.types.ssh_keys.gateway.base import SshKeysGateway
from exls.management.types.ssh_keys.gateway.sdk import SshKeysGatewaySdk
from exls.management.types.workspace_templates.gateway.base import (
    WorkspaceTemplatesGateway,
)
from exls.management.types.workspace_templates.gateway.sdk import (
    WorkspaceTemplatesGatewaySdk,
)
from exls.offers.gateway.base import OffersGateway
from exls.offers.gateway.sdk import OffersGatewaySdk
from exls.services.gateway.base import ServicesGateway
from exls.services.gateway.sdk import ServicesGatewaySdk
from exls.workspaces.gateway.base import WorkspacesGateway
from exls.workspaces.gateway.sdk import WorkspacesGatewaySdk

from exls.auth.adapters.gateway.auth0 import Auth0Gateway
from exls.auth.adapters.gateway.keyring import KeyringTokenStorageGateway
from exls.auth.core.ports import IAuthGateway, ITokenStorageGateway
from exls.config import AppConfig
from exls.nodes.adapters.gateway.sdk import NodesGatewaySdk
from exls.nodes.core.ports import INodesGateway
from exls.shared.adapters.gateway.file.gateways import (
    StringFileIOGateway,
    YamlFileIOGateway,
)


class GatewayFactory:
    def __init__(self, config: AppConfig):
        self._config = config

    def _create_api_client(self, access_token: str) -> ApiClient:
        client_config: Configuration = Configuration(host=self._config.backend_host)
        api_client: ApiClient = ApiClient(configuration=client_config)
        api_client.set_default_header(  # type: ignore[reportUnknownMemberType]
            "Authorization", f"Bearer {access_token}"
        )
        return api_client

    def create_auth_gateway(self) -> IAuthGateway:
        return Auth0Gateway()

    def create_token_storage_gateway(self) -> ITokenStorageGateway:
        return KeyringTokenStorageGateway()

    def create_yaml_fileio_gateway(self) -> YamlFileIOGateway:
        return YamlFileIOGateway()

    def create_string_fileio_gateway(self) -> StringFileIOGateway:
        return StringFileIOGateway()

    def create_nodes_gateway(self, access_token: str) -> INodesGateway:
        nodes_api: NodesApi = NodesApi(self._create_api_client(access_token))
        return NodesGatewaySdk(nodes_api)

    def create_offers_gateway(self, access_token: str) -> OffersGateway:
        offers_api: OffersApi = OffersApi(self._create_api_client(access_token))
        return OffersGatewaySdk(offers_api)

    def create_services_gateway(self, access_token: str) -> ServicesGateway:
        services_api: ServicesApi = ServicesApi(self._create_api_client(access_token))
        return ServicesGatewaySdk(services_api)

    def create_clusters_gateway(self, access_token: str) -> ClustersGateway:
        clusters_api: ClustersApi = ClustersApi(self._create_api_client(access_token))
        return ClustersGatewaySdk(clusters_api)

    def create_workspaces_gateway(self, access_token: str) -> WorkspacesGateway:
        workspaces_api: WorkspacesApi = WorkspacesApi(
            self._create_api_client(access_token)
        )
        return WorkspacesGatewaySdk(workspaces_api)

    def create_cluster_templates_gateway(
        self, access_token: str
    ) -> ClusterTemplatesGateway:
        management_api: ManagementApi = ManagementApi(
            self._create_api_client(access_token)
        )
        return ClusterTemplatesGatewaySdk(management_api=management_api)

    def create_credentials_gateway(self, access_token: str) -> CredentialsGateway:
        management_api: ManagementApi = ManagementApi(
            self._create_api_client(access_token)
        )
        return CredentialsGatewaySdk(management_api=management_api)

    def create_service_templates_gateway(
        self, access_token: str
    ) -> ServiceTemplatesGateway:
        management_api: ManagementApi = ManagementApi(
            self._create_api_client(access_token)
        )
        return ServiceTemplatesGatewaySdk(management_api=management_api)

    def create_ssh_keys_gateway(self, access_token: str) -> SshKeysGateway:
        management_api: ManagementApi = ManagementApi(
            self._create_api_client(access_token)
        )
        return SshKeysGatewaySdk(management_api)

    def create_workspace_templates_gateway(
        self, access_token: str
    ) -> WorkspaceTemplatesGateway:
        management_api: ManagementApi = ManagementApi(
            self._create_api_client(access_token)
        )
        return WorkspaceTemplatesGatewaySdk(management_api)
