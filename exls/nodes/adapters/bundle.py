import typer

from exls.nodes.adapters.gateway.sdk import create_nodes_gateway
from exls.nodes.adapters.ui.display.display import NodesInteractionManager
from exls.nodes.core.ports import INodesGateway
from exls.nodes.core.service import NodesService
from exls.shared.adapters.bundle import SharedBundle
from exls.shared.adapters.ui.display.factory import InteractionManagerFactory


class NodesBundle(SharedBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_nodes_service(self) -> NodesService:
        nodes_gateway: INodesGateway = create_nodes_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        return NodesService(nodes_gateway)

    def get_interaction_manager(self) -> NodesInteractionManager:
        interaction_manager_factory = InteractionManagerFactory()
        return NodesInteractionManager(
            input_manager=interaction_manager_factory.get_input_manager(),
            output_manager=interaction_manager_factory.get_output_manager(),
        )
