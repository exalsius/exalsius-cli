from typing import Dict, List

from exalsius_api_client.models.workspace import Workspace

from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exalsius.core.commons.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exalsius.core.commons.render.table import (
    Column,
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)
from exalsius.workspaces.models import WorkspaceAccessInformationDTO


class JsonWorkspacesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        workspaces_list_renderer: JsonListStringRenderer[
            Workspace
        ] = JsonListStringRenderer[Workspace](),
        workspaces_single_item_renderer: JsonSingleItemStringRenderer[
            Workspace
        ] = JsonSingleItemStringRenderer[Workspace](),
        workspace_access_info_renderer: JsonListStringRenderer[
            WorkspaceAccessInformationDTO
        ] = JsonListStringRenderer[WorkspaceAccessInformationDTO](),
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

    def display_workspaces(self, data: List[Workspace]):
        self.workspaces_list_display.display(data)

    def display_workspace(self, data: Workspace):
        self.workspaces_single_item_display.display(data)

    def display_workspace_access_info(self, data: List[WorkspaceAccessInformationDTO]):
        self.workspace_access_info_display.display(data)


DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
    "workspace_status": get_column("Status"),
    "owner": get_column("Owner"),
    "cluster_id": get_column("Cluster ID"),
}

DEFAULT_WORKSPACE_ACCESS_INFO_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "workspace_id": get_column("Workspace ID", no_wrap=True),
    "access_type": get_column("Access Type"),
    "access_endpoint": get_column("Access Endpoint"),
}


class TableWorkspacesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        workspaces_list_renderer: TableListRenderer[Workspace] = TableListRenderer[
            Workspace
        ](columns_rendering_map=DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP),
        workspaces_single_item_renderer: TableSingleItemRenderer[
            Workspace
        ] = TableSingleItemRenderer[Workspace](
            columns_map=DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP
        ),
        workspace_access_info_renderer: TableListRenderer[
            WorkspaceAccessInformationDTO
        ] = TableListRenderer[WorkspaceAccessInformationDTO](
            columns_rendering_map=DEFAULT_WORKSPACE_ACCESS_INFO_COLUMNS_RENDERING_MAP
        ),
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

    def display_workspaces(self, data: List[Workspace]):
        self.workspaces_list_display.display(data)

    def display_workspace(self, data: Workspace):
        self.workspaces_single_item_display.display(data)

    def display_workspace_access_info(self, data: List[WorkspaceAccessInformationDTO]):
        self.workspace_access_info_display.display(data)
