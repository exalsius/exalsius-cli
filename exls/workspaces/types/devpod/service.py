from exls.clusters.gateway.base import ClustersGateway
from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.service import WorkspacesService
from exls.workspaces.types.devpod.dtos import DeployDevPodWorkspaceRequestDTO
from exls.workspaces.types.devpod.gateway.dtos import DeployDevPodWorkspaceParams
from exls.workspaces.types.devpod.mappers import (
    deploy_devpod_workspace_params_from_request_dto,
)


class DevPodWorkspacesService(WorkspacesService):
    @handle_service_errors("creating devpod workspace")
    def deploy_devpod_workspace(
        self,
        request_dto: DeployDevPodWorkspaceRequestDTO,
    ) -> str:
        deploy_params: DeployDevPodWorkspaceParams = (
            deploy_devpod_workspace_params_from_request_dto(request_dto=request_dto)
        )
        return self.workspaces_gateway.deploy(deploy_params=deploy_params)


def get_devpod_workspaces_service(
    config: AppConfig, access_token: str
) -> DevPodWorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway(
        access_token=access_token
    )
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway(
        access_token=access_token
    )
    return DevPodWorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
    )
