import typer

from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory
from exls.workspaces.adapters.gateway.sdk import create_workspaces_gateway
from exls.workspaces.adapters.ui.display.display import IOWorkspacesFacade
from exls.workspaces.core.ports import IWorkspacesGateway
from exls.workspaces.core.service import WorkspacesService


class WorkspacesBundle(BaseBundle):
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)

    def get_workspaces_service(self) -> WorkspacesService:
        workspaces_gateway: IWorkspacesGateway = create_workspaces_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        return WorkspacesService(
            workspaces_gateway=workspaces_gateway,
            workspace_creation_polling_config=self.config.workspace_creation_polling,
        )

    def get_io_facade(self) -> IOWorkspacesFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOWorkspacesFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )
