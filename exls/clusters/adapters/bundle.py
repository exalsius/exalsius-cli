import typer
from exalsius_api_client.api.clusters_api import ClustersApi

from exls.clusters.adapters.adapter import ClusterAdapter
from exls.clusters.adapters.gateway.sdk.sdk import SdkClustersGateway
from exls.clusters.adapters.provider.nodes import NodesDomainProvider
from exls.clusters.adapters.ui.flows.cluster_deploy import DeployClusterFlow
from exls.clusters.core.ports.provider import NodesProvider
from exls.clusters.core.service import ClustersService
from exls.nodes.adapters.bundle import NodesBundle
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.file.adapters import YamlFileWriteAdapter
from exls.shared.core.ports.file import FileWritePort


class ClustersBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)
        self._nodes_bundle: NodesBundle = NodesBundle(ctx)

    def get_clusters_service(self) -> ClustersService:
        clusters_api: ClustersApi = ClustersApi(api_client=self.create_api_client())
        clusters_gateway: SdkClustersGateway = SdkClustersGateway(
            clusters_api=clusters_api
        )
        nodes_provider: NodesProvider = NodesDomainProvider(
            nodes_service=self._nodes_bundle.get_nodes_service()
        )
        cluster_adapter: ClusterAdapter = ClusterAdapter(
            cluster_gateway=clusters_gateway, nodes_provider=nodes_provider
        )
        file_write_adapter: FileWritePort[str] = YamlFileWriteAdapter()
        return ClustersService(
            clusters_operations=cluster_adapter,
            clusters_repository=cluster_adapter,
            nodes_provider=nodes_provider,
            file_write_adapter=file_write_adapter,
        )

    def get_deploy_cluster_flow(self) -> DeployClusterFlow:
        return DeployClusterFlow(service=self.get_clusters_service())
