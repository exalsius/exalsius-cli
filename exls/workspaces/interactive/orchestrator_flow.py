from typing import TYPE_CHECKING, List, Optional

from exls.clusters.dtos import ClusterDTO
from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO
from exls.workspaces.common.deploy_dtos import WorkspaceDeployConfigDTO
from exls.workspaces.interactive.base_flow import BaseWorkspaceDeployFlow
from exls.workspaces.interactive.cluster_selector_flow import (
    WorkspaceClusterSelectorFlow,
)
from exls.workspaces.interactive.config_editor_flow import WorkspaceConfigEditorFlow
from exls.workspaces.interactive.template_selector_flow import (
    WorkspaceTemplateSelectorFlow,
)

if TYPE_CHECKING:
    from exls.workspaces.common.display import ComposingWorkspaceDeployDisplayManager


class WorkspaceDeployOrchestratorFlow(BaseWorkspaceDeployFlow):
    """Orchestrates the workspace deployment process."""

    def __init__(
        self,
        clusters: List[ClusterDTO],
        templates: List[WorkspaceTemplateDTO],
        display_manager: "ComposingWorkspaceDeployDisplayManager",
    ):
        super().__init__(display_manager)
        self._clusters: List[ClusterDTO] = clusters
        self._templates: List[WorkspaceTemplateDTO] = templates

    def run(self) -> Optional[WorkspaceDeployConfigDTO]:
        """
        Main orchestration method for workspace deployment.

        Orchestrates the full flow:
        1. Display welcome message
        2. Select cluster
        3. Select template
        4. Edit configuration (resources & variables)
        5. Return final config DTO

        Returns:
            WorkspaceDeployConfigDTO if successful, None if cancelled
        """
        try:
            # Welcome message
            self._display_manager.display_info(
                "🚀 Workspace Deploy - Interactive Mode: This will guide you through deploying a workspace"
            )

            # Step 1: Select cluster
            self._display_manager.display_info("\n📋 Step 1: Select Cluster")
            cluster_selector = WorkspaceClusterSelectorFlow(
                self._clusters, self._display_manager
            )
            cluster_id: Optional[str] = cluster_selector.run()

            if cluster_id is None:
                self._display_manager.display_info("\nDeployment cancelled by user.")
                return None

            # Step 2: Select template
            self._display_manager.display_info("\n📋 Step 2: Select Workspace Template")
            template_selector = WorkspaceTemplateSelectorFlow(
                self._templates, self._display_manager
            )
            template: Optional[WorkspaceTemplateDTO] = template_selector.run()

            if template is None:
                self._display_manager.display_info("\nDeployment cancelled by user.")
                return None

            # Step 3: Configure deployment (resources & variables)
            self._display_manager.display_info(
                "\n⚙️  Step 3: Configure Deployment (Resources & Variables)"
            )
            config_editor = WorkspaceConfigEditorFlow(
                cluster_id, template, self._display_manager
            )
            config: Optional[WorkspaceDeployConfigDTO] = config_editor.run()

            if config is None:
                self._display_manager.display_info("\nDeployment cancelled by user.")
                return None

            # Step 4: Final summary
            self._display_manager.display_info("\n✅ Configuration Complete!")
            self._display_manager.display_success(
                f"Workspace '{config.workspace_name}' ready to deploy on cluster '{cluster_id}'"
            )

            return config

        except (KeyboardInterrupt, TypeError):
            self._display_manager.display_info("\nDeployment cancelled by user.")
            return None
