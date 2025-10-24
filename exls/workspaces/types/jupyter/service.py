from exls.clusters.gateway.base import ClustersGateway
from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.service import WorkspacesService
from exls.workspaces.types.jupyter.dtos import DeployJupyterWorkspaceRequestDTO
from exls.workspaces.types.jupyter.gateway.dtos import DeployJupyterWorkspaceParams
from exls.workspaces.types.jupyter.mappers import (
    deploy_jupyter_workspace_params_from_request_dto,
)


class JupyterWorkspacesService(WorkspacesService):
    @handle_service_errors("creating jupyter workspace")
    def deploy_jupyter_workspace(
        self,
        request_dto: DeployJupyterWorkspaceRequestDTO,
    ) -> str:
        deploy_params: DeployJupyterWorkspaceParams = (
            deploy_jupyter_workspace_params_from_request_dto(request_dto=request_dto)
        )
        return self.workspaces_gateway.deploy(deploy_params=deploy_params)


def get_jupyter_workspaces_service(
    config: AppConfig, access_token: str
) -> JupyterWorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway(
        access_token=access_token
    )
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway(
        access_token=access_token
    )
    return JupyterWorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
    )
