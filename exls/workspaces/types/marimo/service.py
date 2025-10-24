from exls.clusters.gateway.base import ClustersGateway
from exls.config import AppConfig
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.service import WorkspacesService
from exls.workspaces.types.marimo.dtos import DeployMarimoWorkspaceRequestDTO
from exls.workspaces.types.marimo.gateway.dtos import DeployMarimoWorkspaceParams
from exls.workspaces.types.marimo.mappers import (
    deploy_marimo_workspace_params_from_request_dto,
)


class MarimoWorkspacesService(WorkspacesService):
    @handle_service_errors("creating marimo workspace")
    def deploy_marimo_workspace(
        self,
        request_dto: DeployMarimoWorkspaceRequestDTO,
    ) -> str:
        deploy_params: DeployMarimoWorkspaceParams = (
            deploy_marimo_workspace_params_from_request_dto(request_dto=request_dto)
        )
        return self.workspaces_gateway.deploy(deploy_params=deploy_params)


def get_marimo_workspaces_service(
    config: AppConfig, access_token: str
) -> MarimoWorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway(
        access_token=access_token
    )
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway(
        access_token=access_token
    )
    return MarimoWorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
    )
