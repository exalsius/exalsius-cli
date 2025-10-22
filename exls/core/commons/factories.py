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
from exls.config import AppConfig
from exls.core.commons.gateways.fileio import (
    StringFileIOGateway,
    YamlFileIOGateway,
)
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
from exls.nodes.gateway.base import NodesGateway
from exls.nodes.gateway.sdk import NodesGatewaySdk
from exls.offers.gateway.base import OffersGateway
from exls.offers.gateway.sdk import OffersGatewaySdk
from exls.services.gateway.base import ServicesGateway
from exls.services.gateway.sdk import ServicesGatewaySdk
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.gateway.sdk import WorkspacesGatewaySdk


class GatewayFactory:
    def __init__(self, config: AppConfig, access_token: str):
        self._config = config
        self._access_token = access_token
        self._api_client = self._create_api_client()

    def _create_api_client(self) -> ApiClient:
        client_config: Configuration = Configuration(host=self._config.backend_host)
        api_client: ApiClient = ApiClient(configuration=client_config)
        api_client.set_default_header("Authorization", f"Bearer {self._access_token}")  # pyright: ignore[reportUnknownMemberType]
        return api_client

    def create_nodes_gateway(self) -> NodesGateway:
        nodes_api: NodesApi = NodesApi(self._api_client)
        return NodesGatewaySdk(nodes_api)

    def create_offers_gateway(self) -> OffersGateway:
        offers_api: OffersApi = OffersApi(self._api_client)
        return OffersGatewaySdk(offers_api)

    def create_services_gateway(self) -> ServicesGateway:
        services_api: ServicesApi = ServicesApi(self._api_client)
        return ServicesGatewaySdk(services_api)

    def create_clusters_gateway(self) -> ClustersGateway:
        clusters_api: ClustersApi = ClustersApi(self._api_client)
        return ClustersGatewaySdk(clusters_api)

    def create_workspaces_gateway(self) -> WorkspacesGateway:
        workspaces_api: WorkspacesApi = WorkspacesApi(self._api_client)
        return WorkspacesGatewaySdk(workspaces_api)

    def create_cluster_templates_gateway(self) -> ClusterTemplatesGateway:
        management_api: ManagementApi = ManagementApi(self._api_client)
        return ClusterTemplatesGatewaySdk(management_api=management_api)

    def create_credentials_gateway(self) -> CredentialsGateway:
        management_api: ManagementApi = ManagementApi(self._api_client)
        return CredentialsGatewaySdk(management_api=management_api)

    def create_service_templates_gateway(self) -> ServiceTemplatesGateway:
        management_api: ManagementApi = ManagementApi(self._api_client)
        return ServiceTemplatesGatewaySdk(management_api=management_api)

    def create_ssh_keys_gateway(self) -> SshKeysGateway:
        management_api: ManagementApi = ManagementApi(self._api_client)
        return SshKeysGatewaySdk(management_api)

    def create_workspace_templates_gateway(self) -> WorkspaceTemplatesGateway:
        management_api: ManagementApi = ManagementApi(self._api_client)
        return WorkspaceTemplatesGatewaySdk(management_api)

    def create_yaml_fileio_gateway(self) -> YamlFileIOGateway:
        return YamlFileIOGateway()

    def create_string_fileio_gateway(self) -> StringFileIOGateway:
        return StringFileIOGateway()
