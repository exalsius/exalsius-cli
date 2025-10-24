from typing import Any, Dict

from exls.clusters.gateway.base import ClustersGateway
from exls.config import AppConfig, ConfigWorkspaceCreationPolling
from exls.core.commons.decorators import handle_service_errors
from exls.core.commons.factories import GatewayFactory
from exls.core.commons.gateways.fileio import YamlFileIOGateway
from exls.workspaces.common.gateway.base import WorkspacesGateway
from exls.workspaces.common.service import WorkspacesService
from exls.workspaces.types.diloco.dtos import DeployDilocoWorkspaceRequestDTO
from exls.workspaces.types.diloco.gateway.dtos import DeployDilocoWorkspaceParams
from exls.workspaces.types.diloco.mappers import (
    deploy_diloco_workspace_params_from_request_dto,
)


class DilocoWorkspacesService(WorkspacesService):
    def __init__(
        self,
        workspaces_gateway: WorkspacesGateway,
        clusters_gateway: ClustersGateway,
        workspace_creation_polling_config: ConfigWorkspaceCreationPolling,
        yaml_fileio_gateway: YamlFileIOGateway,
    ):
        super().__init__(
            workspace_creation_polling_config=workspace_creation_polling_config,
            workspaces_gateway=workspaces_gateway,
            clusters_gateway=clusters_gateway,
        )
        self.yaml_fileio_gateway: YamlFileIOGateway = yaml_fileio_gateway

    @handle_service_errors("creating diloco workspace")
    def deploy_diloco_workspace(
        self,
        request_dto: DeployDilocoWorkspaceRequestDTO,
    ) -> str:
        diloco_config_from_file: Dict[str, Any] = self.yaml_fileio_gateway.read_file(
            file_path=request_dto.diloco_config_file
        )
        deploy_params: DeployDilocoWorkspaceParams = (
            deploy_diloco_workspace_params_from_request_dto(
                request_dto=request_dto,
                diloco_config_from_file=diloco_config_from_file,
            )
        )

        return self.workspaces_gateway.deploy(deploy_params=deploy_params)


def get_diloco_workspaces_service(
    config: AppConfig, access_token: str
) -> DilocoWorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway(
        access_token=access_token
    )
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway(
        access_token=access_token
    )
    yaml_fileio_gateway: YamlFileIOGateway = (
        gateway_factory.create_yaml_fileio_gateway()
    )
    return DilocoWorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
        yaml_fileio_gateway=yaml_fileio_gateway,
    )
