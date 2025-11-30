import typer

from exls.clusters.adapters.gateway.sdk import create_clusters_gateway
from exls.clusters.adapters.provider.nodes import NodesDomainProvider
from exls.clusters.adapters.ui.display.display import IOClustersFacade
from exls.clusters.adapters.ui.flows.cluster_deploy import DeployClusterFlow
from exls.clusters.core.ports.gateway import IClustersGateway
from exls.clusters.core.ports.provider import INodesProvider
from exls.clusters.core.service import ClustersService
from exls.nodes.adapters.bundle import NodesBundle
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.gateway.file.gateways import (
    IFileWriteGateway,
    YamlFileWriteGateway,
)
from exls.shared.adapters.ui.factory import IOFactory


class ClustersBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)
        self._nodes_bundle: NodesBundle = NodesBundle(ctx)

    def get_clusters_service(self) -> ClustersService:
        clusters_gateway: IClustersGateway = create_clusters_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        file_write_gateway: IFileWriteGateway[str] = YamlFileWriteGateway()
        cluster_nodes_provider: INodesProvider = NodesDomainProvider(
            nodes_service=self._nodes_bundle.get_nodes_service()
        )
        return ClustersService(
            clusters_gateway=clusters_gateway,
            file_write_gateway=file_write_gateway,
            nodes_provider=cluster_nodes_provider,
        )

    def get_deploy_cluster_flow(self) -> DeployClusterFlow:
        return DeployClusterFlow(service=self.get_clusters_service())

    def get_io_facade(self) -> IOClustersFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOClustersFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )
