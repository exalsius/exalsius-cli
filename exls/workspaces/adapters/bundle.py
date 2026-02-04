from typing import Dict

from exalsius_api_client.api.workspaces_api import WorkspacesApi
from pydantic_settings import SettingsConfigDict

from exls.clusters.adapters.bundle import ClustersBundle
from exls.config import AppConfig
from exls.defaults import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.management.adapters.bundle import ManagementBundle
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.shared.render.render import (
    BaseYamlRenderConfig,
    DictToYamlStringRenderer,
    YamlRenderContext,
)
from exls.state import AppState
from exls.workspaces.adapters.gateway.gateway import WorkspacesGateway
from exls.workspaces.adapters.gateway.sdk.sdk import SdkWorkspacesGateway
from exls.workspaces.adapters.provider.clusters import ClustersDomainProvider
from exls.workspaces.adapters.provider.templates import WorkspaceTemplatesDomainProvider
from exls.workspaces.adapters.ui.configurators import (
    IntegratedWorkspaceTemplates,
    WorkspaceEditorRenderBundle,
)
from exls.workspaces.adapters.ui.editor.render import (
    get_workspace_template_editing_comments,
)
from exls.workspaces.adapters.ui.flows.access_flow import ConfigureWorkspaceAccessFlow
from exls.workspaces.core.ports.providers import (
    ClustersProvider,
    WorkspaceTemplatesProvider,
)
from exls.workspaces.core.service import WorkspacesService


class EditorYamlRenderConfig(BaseYamlRenderConfig):
    """Render configuration for the editor."""

    indent: int = 2

    model_config = SettingsConfigDict(
        env_prefix=CONFIG_ENV_PREFIX + "EDITOR_YAML_RENDER_CONFIG_",
        env_nested_delimiter=CONFIG_ENV_NESTED_DELIMITER,
        extra="ignore",
    )


class WorkspacesBundle(BaseBundle):
    def __init__(self, app_config: AppConfig, app_state: AppState):
        super().__init__(app_config, app_state)
        self._management_bundle: ManagementBundle = ManagementBundle(
            app_config, app_state
        )
        self._clusters_bundle: ClustersBundle = ClustersBundle(app_config, app_state)

    def get_workspaces_service(self) -> WorkspacesService:
        workspaces_api: WorkspacesApi = WorkspacesApi(
            api_client=self.create_api_client()
        )
        workspaces_gateway: WorkspacesGateway = SdkWorkspacesGateway(
            workspaces_api=workspaces_api
        )
        workspace_templates_provider: WorkspaceTemplatesProvider = (
            WorkspaceTemplatesDomainProvider(
                management_service=self._management_bundle.get_management_service(),
            )
        )
        clusters_provider: ClustersProvider = ClustersDomainProvider(
            clusters_service=self._clusters_bundle.get_clusters_service(),
        )
        return WorkspacesService(
            workspaces_repository=workspaces_gateway,
            workspaces_operations=workspaces_gateway,
            workspace_creation_polling_config=self.config.workspace_creation_polling,
            clusters_provider=clusters_provider,
            workspace_templates_provider=workspace_templates_provider,
        )

    def get_configure_workspace_access_flow(self) -> ConfigureWorkspaceAccessFlow:
        return ConfigureWorkspaceAccessFlow(service=self.get_crypto_service())

    def get_editor_render_bundle(
        self, integrated_template: IntegratedWorkspaceTemplates
    ) -> WorkspaceEditorRenderBundle:
        editor_yaml_render_config: EditorYamlRenderConfig = EditorYamlRenderConfig()
        editor_renderer: DictToYamlStringRenderer = DictToYamlStringRenderer(
            default_render_config=editor_yaml_render_config,
        )

        comments: Dict[str, str] = get_workspace_template_editing_comments(
            integrated_template
        )

        editor_render_context: YamlRenderContext = YamlRenderContext(
            indent=editor_yaml_render_config.indent,
            comments=comments,
        )

        return WorkspaceEditorRenderBundle(
            editor_renderer=editor_renderer,
            editor_render_context=editor_render_context,
            message_output_format=self.message_output_format,
        )
