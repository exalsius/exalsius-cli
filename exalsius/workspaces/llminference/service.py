from exalsius.clusters.gateway.base import ClustersGateway
from exalsius.config import AppConfig
from exalsius.core.commons.decorators import handle_service_errors
from exalsius.core.commons.factories import GatewayFactory
from exalsius.workspaces.gateway.base import WorkspacesGateway
from exalsius.workspaces.llminference.domain import DeployLLMInferenceWorkspaceParams
from exalsius.workspaces.llminference.dtos import DeployLLMInferenceWorkspaceRequestDTO
from exalsius.workspaces.service import WorkspacesService


class LLMInferenceWorkspacesService(WorkspacesService):
    @handle_service_errors("creating llm-inference workspace")
    def deploy_llm_inference_workspace(
        self,
        request_dto: DeployLLMInferenceWorkspaceRequestDTO,
    ) -> str:
        deploy_params: DeployLLMInferenceWorkspaceParams = (
            DeployLLMInferenceWorkspaceParams.from_request_dto(request_dto=request_dto)
        )
        return self.workspaces_gateway.deploy(deploy_params=deploy_params)


def get_llm_inference_workspaces_service(
    config: AppConfig, access_token: str
) -> LLMInferenceWorkspacesService:
    gateway_factory: GatewayFactory = GatewayFactory(
        config=config,
        access_token=access_token,
    )
    workspaces_gateway: WorkspacesGateway = gateway_factory.create_workspaces_gateway()
    clusters_gateway: ClustersGateway = gateway_factory.create_clusters_gateway()
    return LLMInferenceWorkspacesService(
        workspace_creation_polling_config=config.workspace_creation_polling,
        workspaces_gateway=workspaces_gateway,
        clusters_gateway=clusters_gateway,
    )
