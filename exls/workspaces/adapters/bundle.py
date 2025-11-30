from typing import Dict

import typer
from pydantic_settings import SettingsConfigDict

from exls.clusters.adapters.bundle import ClustersBundle
from exls.defaults import CONFIG_ENV_NESTED_DELIMITER, CONFIG_ENV_PREFIX
from exls.management.adapters.bundel import ManagementBundle
from exls.shared.adapters.bundle import BaseBundle
from exls.shared.adapters.ui.factory import IOFactory
from exls.shared.adapters.ui.shared.render.render import (
    BaseYamlRenderConfig,
    DictToYamlStringRenderer,
    YamlRenderContext,
)
from exls.workspaces.adapters.gateway.sdk import create_workspaces_gateway
from exls.workspaces.adapters.provider.clusters import ClustersDomainProvider
from exls.workspaces.adapters.provider.templates import WorkspaceTemplatesProvider
from exls.workspaces.adapters.ui.display.display import IOWorkspacesFacade
from exls.workspaces.adapters.ui.dtos import IntegratedWorkspaceTemplates
from exls.workspaces.adapters.ui.editor.render import (
    get_workspace_template_editing_comments,
)
from exls.workspaces.adapters.ui.flows.access_flow import ConfigureWorkspaceAccessFlow
from exls.workspaces.core.ports.gateway import IWorkspacesGateway
from exls.workspaces.core.ports.provider import (
    IClustersProvider,
    IWorkspaceTemplatesProvider,
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
    def __init__(self, ctx: typer.Context):
        super().__init__(ctx)
        self._management_bundle: ManagementBundle = ManagementBundle(ctx)
        self._clusters_bundle: ClustersBundle = ClustersBundle(ctx)

    def get_workspaces_service(self) -> WorkspacesService:
        workspaces_gateway: IWorkspacesGateway = create_workspaces_gateway(
            backend_host=self.config.backend_host, access_token=self.access_token
        )
        workspace_templates_provider: IWorkspaceTemplatesProvider = (
            WorkspaceTemplatesProvider(
                management_service=self._management_bundle.get_management_service(),
            )
        )
        clusters_provider: IClustersProvider = ClustersDomainProvider(
            clusters_service=self._clusters_bundle.get_clusters_service(),
        )
        return WorkspacesService(
            workspaces_gateway=workspaces_gateway,
            workspace_creation_polling_config=self.config.workspace_creation_polling,
            clusters_provider=clusters_provider,
            workspace_templates_provider=workspace_templates_provider,
        )

    def get_io_facade(self) -> IOWorkspacesFacade:
        io_facade_factory: IOFactory = IOFactory()
        return IOWorkspacesFacade(
            input_manager=io_facade_factory.get_input_manager(),
            output_manager=io_facade_factory.get_output_manager(),
        )

    def get_configure_workspace_access_flow(self) -> ConfigureWorkspaceAccessFlow:
        return ConfigureWorkspaceAccessFlow(service=self.get_crypto_service())

    def get_editor_render_context(
        self, integrated_template: IntegratedWorkspaceTemplates
    ) -> YamlRenderContext:
        editor_yaml_render_config: EditorYamlRenderConfig = EditorYamlRenderConfig()
        comments: Dict[str, str] = get_workspace_template_editing_comments(
            integrated_template
        )

        return YamlRenderContext(
            indent=editor_yaml_render_config.indent,
            comments=comments,
        )

    def get_editor_renderer(self) -> DictToYamlStringRenderer:
        editor_yaml_render_config: EditorYamlRenderConfig = EditorYamlRenderConfig()
        return DictToYamlStringRenderer(
            default_render_config=editor_yaml_render_config,
        )
