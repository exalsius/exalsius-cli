from exls.clusters.gateway.base import ClustersGateway
from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.service import WorkspacesService
from exls.workspaces.types.jupyter.domain import DeployJupyterWorkspaceParams
from exls.workspaces.types.jupyter.dtos import DeployJupyterWorkspaceRequestDTO


class JupyterWorkspacesService(WorkspacesService):
    @handle_service_errors("creating jupyter workspace")
    def deploy_jupyter_workspace(
        self,
        request_dto: DeployJupyterWorkspaceRequestDTO,
    ) -> str:
        deploy_params: DeployJupyterWorkspaceParams = (
            DeployJupyterWorkspaceParams.from_request_dto(request_dto=request_dto)
        )
        return self.workspaces_gateway.deploy(deploy_params=deploy_params)


def get_jupyter_workspaces_service(
    config: AppConfig, access_token: str
) -> JupyterWorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway()
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway()
    return JupyterWorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
    )
