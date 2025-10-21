from exalsius_api_client.api.clusters_api import ClustersApi
from exalsius_api_client.api.nodes_api import NodesApi
from exalsius_api_client.api.offers_api import OffersApi
from exalsius_api_client.api.services_api import ServicesApi
from exalsius_api_client.api.workspaces_api import WorkspacesApi
from exalsius_api_client.api_client import ApiClient
from exalsius_api_client.configuration import Configuration

from exalsius.clusters.gateway.base import ClustersGateway
from exalsius.clusters.gateway.sdk import ClustersGatewaySdk
from exalsius.config import AppConfig
from exalsius.core.commons.gateways.fileio import YamlFileIOGateway
from exalsius.nodes.gateway.base import NodesGateway
from exalsius.nodes.gateway.sdk import NodesGatewaySdk
from exalsius.offers.gateway.base import OffersGateway
from exalsius.offers.gateway.sdk import OffersGatewaySdk
from exalsius.services.gateway.base import ServicesGateway
from exalsius.services.gateway.sdk import ServicesGatewaySdk
from exalsius.workspaces.gateway.base import WorkspacesGateway
from exalsius.workspaces.gateway.sdk import WorkspacesGatewaySdk


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

    def create_yaml_fileio_gateway(self) -> YamlFileIOGateway:
        return YamlFileIOGateway()
