from abc import ABC, abstractmethod
from typing import Dict, List

from exls.clusters.dtos import ClusterDTO
from exls.core.commons.display import (
    BaseDisplayManager,
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ComposingDisplayManager,
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exls.core.commons.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exls.core.commons.render.table import (
    Column,
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)
from exls.management.types.workspace_templates.dtos import WorkspaceTemplateDTO
from exls.workspaces.common.deploy_dtos import WorkspaceDeployConfigDTO
from exls.workspaces.common.dtos import WorkspaceAccessInformationDTO, WorkspaceDTO


class BaseWorkspaceDeployDisplayManager(BaseDisplayManager, ABC):
    """Base display manager for workspace deployment operations."""

    @abstractmethod
    def display_workspaces(self, workspaces: List[WorkspaceDTO]):
        """Display list of workspaces."""
        pass

    @abstractmethod
    def display_workspace(self, workspace: WorkspaceDTO):
        """Display a single workspace."""
        pass

    @abstractmethod
    def display_clusters(self, clusters: List[ClusterDTO]):
        """Display list of clusters."""
        pass

    @abstractmethod
    def display_workspace_templates(self, templates: List[WorkspaceTemplateDTO]):
        """Display list of workspace templates."""
        pass

    @abstractmethod
    def display_deploy_config(self, config: WorkspaceDeployConfigDTO):
        """Display workspace deployment configuration."""
        pass


class JsonWorkspacesDisplayManager(
    BaseJsonDisplayManager, BaseWorkspaceDeployDisplayManager
):
    def __init__(
        self,
        workspaces_list_renderer: JsonListStringRenderer[
            WorkspaceDTO
        ] = JsonListStringRenderer[WorkspaceDTO](),
        workspaces_single_item_renderer: JsonSingleItemStringRenderer[
            WorkspaceDTO
        ] = JsonSingleItemStringRenderer[WorkspaceDTO](),
        workspace_access_info_renderer: JsonListStringRenderer[
            WorkspaceAccessInformationDTO
        ] = JsonListStringRenderer[WorkspaceAccessInformationDTO](),
        clusters_list_renderer: JsonListStringRenderer[
            ClusterDTO
        ] = JsonListStringRenderer[ClusterDTO](),
        templates_list_renderer: JsonListStringRenderer[
            WorkspaceTemplateDTO
        ] = JsonListStringRenderer[WorkspaceTemplateDTO](),
        deploy_config_renderer: JsonSingleItemStringRenderer[
            WorkspaceDeployConfigDTO
        ] = JsonSingleItemStringRenderer[WorkspaceDeployConfigDTO](),
    ):
        super().__init__()
        self.workspaces_list_display = ConsoleListDisplay(
            renderer=workspaces_list_renderer
        )
        self.workspaces_single_item_display = ConsoleSingleItemDisplay(
            renderer=workspaces_single_item_renderer
        )
        self.workspace_access_info_display = ConsoleListDisplay(
            renderer=workspace_access_info_renderer
        )
        self.clusters_list_display = ConsoleListDisplay(renderer=clusters_list_renderer)
        self.templates_list_display = ConsoleListDisplay(
            renderer=templates_list_renderer
        )
        self.deploy_config_display = ConsoleSingleItemDisplay(
            renderer=deploy_config_renderer
        )

    def display_workspaces(self, workspaces: List[WorkspaceDTO]):
        self.workspaces_list_display.display(workspaces)

    def display_workspace(self, workspace: WorkspaceDTO):
        self.workspaces_single_item_display.display(workspace)

    def display_workspace_access_info(self, data: List[WorkspaceAccessInformationDTO]):
        self.workspace_access_info_display.display(data)

    def display_clusters(self, clusters: List[ClusterDTO]):
        self.clusters_list_display.display(clusters)

    def display_workspace_templates(self, templates: List[WorkspaceTemplateDTO]):
        self.templates_list_display.display(templates)

    def display_deploy_config(self, config: WorkspaceDeployConfigDTO):
        self.deploy_config_display.display(config)


DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "workspace_id": get_column("ID", no_wrap=True),
    "workspace_name": get_column("Name"),
    "workspace_status": get_column("Status"),
    "workspace_created_at": get_column("Created At"),
    "cluster_name": get_column("Deployed to Cluster"),
    "workspace_access_information.access_endpoint": get_column("Access Endpoint"),
}

DEFAULT_CLUSTERS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
    "cluster_status": get_column("Status"),
}

DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Name"),
    "description": get_column("Description"),
}

DEFAULT_DEPLOY_CONFIG_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "cluster_id": get_column("Cluster ID"),
    "template_name": get_column("Template"),
    "workspace_name": get_column("Workspace Name"),
    "resources.gpu_count": get_column("GPUs"),
    "resources.cpu_cores": get_column("CPU Cores"),
    "resources.memory_gb": get_column("Memory (GB)"),
    "resources.storage_gb": get_column("Storage (GB)"),
}


class TableWorkspacesDisplayManager(
    BaseTableDisplayManager, BaseWorkspaceDeployDisplayManager
):
    def __init__(
        self,
        workspaces_list_renderer: TableListRenderer[WorkspaceDTO] = TableListRenderer[
            WorkspaceDTO
        ](columns_rendering_map=DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP),
        workspaces_single_item_renderer: TableSingleItemRenderer[
            WorkspaceDTO
        ] = TableSingleItemRenderer[WorkspaceDTO](
            columns_map=DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP
        ),
        clusters_list_renderer: TableListRenderer[ClusterDTO] = TableListRenderer[
            ClusterDTO
        ](columns_rendering_map=DEFAULT_CLUSTERS_COLUMNS_RENDERING_MAP),
        templates_list_renderer: TableListRenderer[
            WorkspaceTemplateDTO
        ] = TableListRenderer[WorkspaceTemplateDTO](
            columns_rendering_map=DEFAULT_WORKSPACE_TEMPLATES_COLUMNS_RENDERING_MAP
        ),
        deploy_config_renderer: TableSingleItemRenderer[
            WorkspaceDeployConfigDTO
        ] = TableSingleItemRenderer[WorkspaceDeployConfigDTO](
            columns_map=DEFAULT_DEPLOY_CONFIG_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.workspaces_list_display = ConsoleListDisplay(
            renderer=workspaces_list_renderer
        )
        self.workspaces_single_item_display = ConsoleSingleItemDisplay(
            renderer=workspaces_single_item_renderer
        )
        self.clusters_list_display = ConsoleListDisplay(renderer=clusters_list_renderer)
        self.templates_list_display = ConsoleListDisplay(
            renderer=templates_list_renderer
        )
        self.deploy_config_display = ConsoleSingleItemDisplay(
            renderer=deploy_config_renderer
        )

    def display_workspaces(self, workspaces: List[WorkspaceDTO]):
        self.workspaces_list_display.display(workspaces)

    def display_workspace(self, workspace: WorkspaceDTO):
        self.workspaces_single_item_display.display(workspace)

    def display_clusters(self, clusters: List[ClusterDTO]):
        self.clusters_list_display.display(clusters)

    def display_workspace_templates(self, templates: List[WorkspaceTemplateDTO]):
        self.templates_list_display.display(templates)

    def display_deploy_config(self, config: WorkspaceDeployConfigDTO):
        self.deploy_config_display.display(config)


class ComposingWorkspaceDeployDisplayManager(ComposingDisplayManager):
    """Composing display manager for workspace deployment operations."""

    def __init__(
        self,
        display_manager: BaseWorkspaceDeployDisplayManager,
    ):
        super().__init__(display_manager=display_manager)
        self.display_manager: BaseWorkspaceDeployDisplayManager = display_manager

    def display_workspaces(self, workspaces: List[WorkspaceDTO]):
        self.display_manager.display_workspaces(workspaces)

    def display_workspace(self, workspace: WorkspaceDTO):
        self.display_manager.display_workspace(workspace)

    def display_clusters(self, clusters: List[ClusterDTO]):
        self.display_manager.display_clusters(clusters)

    def display_workspace_templates(self, templates: List[WorkspaceTemplateDTO]):
        self.display_manager.display_workspace_templates(templates)

    def display_deploy_config(self, config: WorkspaceDeployConfigDTO):
        self.display_manager.display_deploy_config(config)
