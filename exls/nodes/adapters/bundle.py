import typer

from exls.management.adapters.bundel import ManagementBundle
from exls.nodes.adapters.gateway.sdk import create_nodes_gateway
from exls.nodes.adapters.provider.sshkey import ManagementDomainSshProvider
from exls.nodes.adapters.ui.display.display import IONodesFacade
from exls.nodes.adapters.ui.flows.adapters import ImportSshKeyManagementAdapterFlow
from exls.nodes.adapters.ui.flows.node_import import (
    ImportSelfmanagedNodeFlow,
    ImportSelfmanagedNodeRequestListFlow,
)
from exls.nodes.adapters.ui.flows.ports import IImportSshKeyFlow
from exls.nodes.core.ports.gateway import INodesGateway
from exls.nodes.core.ports.provider import ISshKeyProvider
from exls.nodes.core.service import NodesService
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory


class NodesBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)
        self._management_bundle: ManagementBundle = ManagementBundle(ctx)

    def get_nodes_service(self) -> NodesService:
        nodes_gateway: INodesGateway = create_nodes_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        ssh_key_provider: ISshKeyProvider = ManagementDomainSshProvider(
            management_service=self._management_bundle.get_management_service()
        )
        return NodesService(
            nodes_gateway=nodes_gateway, ssh_key_provider=ssh_key_provider
        )

    def get_io_facade(self) -> IONodesFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IONodesFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )

    def get_import_selfmanaged_nodes_flow(self) -> ImportSelfmanagedNodeRequestListFlow:
        import_ssh_key_flow: IImportSshKeyFlow = ImportSshKeyManagementAdapterFlow(
            import_ssh_key_flow=self._management_bundle.get_import_ssh_key_flow(
                ask_confirm=False
            )
        )
        import_selfmanaged_node_flow: ImportSelfmanagedNodeFlow = (
            ImportSelfmanagedNodeFlow(
                service=self.get_nodes_service(),
                import_ssh_key_flow=import_ssh_key_flow,
            )
        )
        return ImportSelfmanagedNodeRequestListFlow(
            import_selfmanaged_node_flow=import_selfmanaged_node_flow,
        )
