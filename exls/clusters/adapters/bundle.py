import typer

from exls.clusters.adapters.gateway.sdk import create_clusters_gateway
from exls.clusters.adapters.ui.display.display import ClustersInteractionManager
from exls.clusters.core.ports import IClustersGateway
from exls.clusters.core.service import ClustersService
from exls.shared.adapters.bundle import SharedBundle
from exls.shared.adapters.gateway.file.gateways import (
    IFileWriteGateway,
    YamlFileWriteGateway,
)
from exls.shared.adapters.ui.display.factory import InteractionManagerFactory


class ClustersBundle(SharedBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_clusters_service(self) -> ClustersService:
        clusters_gateway: IClustersGateway = create_clusters_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        file_write_gateway: IFileWriteGateway[str] = YamlFileWriteGateway()
        return ClustersService(
            clusters_gateway=clusters_gateway, file_write_gateway=file_write_gateway
        )

    def get_interaction_manager(self) -> ClustersInteractionManager:
        interaction_manager_factory = InteractionManagerFactory()
        return ClustersInteractionManager(
            input_manager=interaction_manager_factory.get_input_manager(),
            output_manager=interaction_manager_factory.get_output_manager(),
        )
