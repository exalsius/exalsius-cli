import typer
from exalsius_api_client import NodesApi

from exls.management.adapters.bundel import ManagementBundle
from exls.nodes.adapters.gateway.gateway import NodesGateway
from exls.nodes.adapters.gateway.sdk.sdk import SdkNodesGateway
from exls.nodes.adapters.provider.sshkey import ManagementDomainSshProvider
from exls.nodes.adapters.ui.flows.adapters import ImportSshKeyManagementAdapterFlow
from exls.nodes.adapters.ui.flows.node_import import (
    ImportSelfmanagedNodeFlow,
    ImportSelfmanagedNodeRequestListFlow,
)
from exls.nodes.adapters.ui.flows.ports import IImportSshKeyFlow
from exls.nodes.core.ports.provider import ISshKeyProvider
from exls.nodes.core.service import NodesService
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.gateway.sdk.service import create_api_client


class NodesBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)
        self._management_bundle: ManagementBundle = ManagementBundle(ctx)

    def get_nodes_service(self) -> NodesService:
        nodes_api: NodesApi = NodesApi(
            api_client=create_api_client(
                backend_host=self.config.backend_host, access_token=self.access_token
            )
        )
        nodes_gateway: NodesGateway = SdkNodesGateway(nodes_api=nodes_api)
        ssh_key_provider: ISshKeyProvider = ManagementDomainSshProvider(
            management_service=self._management_bundle.get_management_service()
        )
        return NodesService(
            nodes_repository=nodes_gateway,
            nodes_operations=nodes_gateway,
            ssh_key_provider=ssh_key_provider,
        )

    def get_import_selfmanaged_node_flow(self) -> ImportSelfmanagedNodeFlow:
        import_ssh_key_flow: IImportSshKeyFlow = ImportSshKeyManagementAdapterFlow(
            import_ssh_key_flow=self._management_bundle.get_import_ssh_key_flow(
                ask_confirm=False
            )
        )
        return ImportSelfmanagedNodeFlow(
            service=self.get_nodes_service(),
            import_ssh_key_flow=import_ssh_key_flow,
            ask_confirmation=True,
        )

    def get_import_selfmanaged_nodes_flow(self) -> ImportSelfmanagedNodeRequestListFlow:
        return ImportSelfmanagedNodeRequestListFlow(
            import_selfmanaged_node_flow=self.get_import_selfmanaged_node_flow(),
        )
