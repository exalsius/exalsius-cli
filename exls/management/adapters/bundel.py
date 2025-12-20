import typer
from exalsius_api_client.api.management_api import ManagementApi

from exls.management.adapters.gateway.gateway import ManagementGateway
from exls.management.adapters.gateway.sdk.sdk import ManagementGatewaySdk
from exls.management.adapters.ui.flows.import_ssh_key import ImportSshKeyFlow
from exls.management.core.service import ManagementService
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.file.adapters import StringBase64FileReadAdapter
from exls.shared.core.ports.file import FileReadPort


class ManagementBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_management_service(self) -> ManagementService:
        management_api: ManagementApi = ManagementApi(
            api_client=self.create_api_client()
        )
        management_gateway: ManagementGateway = ManagementGatewaySdk(
            management_api=management_api
        )
        file_read_adapter: FileReadPort[str] = StringBase64FileReadAdapter()
        return ManagementService(
            management_repository=management_gateway,
            file_read_adapter=file_read_adapter,
        )

    def get_import_ssh_key_flow(self, ask_confirm: bool = True) -> ImportSshKeyFlow:
        return ImportSshKeyFlow(ask_confirm=ask_confirm)
