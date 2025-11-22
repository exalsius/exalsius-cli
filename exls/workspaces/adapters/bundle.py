import typer

from exls.shared.adapters.bundle import SharedBundle
from exls.shared.adapters.ui.display.factory import InteractionManagerFactory
from exls.workspaces.adapters.gateway.sdk import create_workspaces_gateway
from exls.workspaces.adapters.ui.display.display import (
    WorkspacesInteractionManager,
)
from exls.workspaces.core.ports import IWorkspacesGateway
from exls.workspaces.core.service import WorkspacesService


class WorkspacesBundle(SharedBundle):
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

    def get_interaction_manager(self) -> WorkspacesInteractionManager:
        interaction_manager_factory = InteractionManagerFactory()
        return WorkspacesInteractionManager(
            input_manager=interaction_manager_factory.get_input_manager(),
            output_manager=interaction_manager_factory.get_output_manager(),
        )
