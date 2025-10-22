from typing import Any

from exalsius.clusters.gateway.base import ClustersGateway
from exalsius.config import AppConfig, ConfigWorkspaceCreationPolling
from exalsius.core.commons.decorators import handle_service_errors
from exalsius.core.commons.factories import GatewayFactory
from exalsius.core.commons.gateways.fileio import YamlFileIOGateway
from exalsius.workspaces.diloco.domain import DeployDilocoWorkspaceParams
from exalsius.workspaces.diloco.dtos import DeployDilocoWorkspaceRequestDTO
from exalsius.workspaces.gateway.base import WorkspacesGateway
from exalsius.workspaces.service import WorkspacesService


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
        diloco_config_from_file: dict[str, Any] = self.yaml_fileio_gateway.read_file(
            file_path=request_dto.diloco_config_file
        )
        deploy_params: DeployDilocoWorkspaceParams = (
            DeployDilocoWorkspaceParams.from_request_dto(
                request_dto=request_dto, diloco_config_from_file=diloco_config_from_file
            )
        )

        return self.workspaces_gateway.deploy(deploy_params=deploy_params)


def get_diloco_workspaces_service(
    config: AppConfig, access_token: str
) -> DilocoWorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway()
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway()
    yaml_fileio_gateway: YamlFileIOGateway = (
        gateway_factory.create_yaml_fileio_gateway()
    )
    return DilocoWorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
        yaml_fileio_gateway=yaml_fileio_gateway,
    )
