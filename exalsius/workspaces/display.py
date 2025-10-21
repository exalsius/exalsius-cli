from typing import Dict, List

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
from exalsius.workspaces.dtos import WorkspaceAccessInformationDTO, WorkspaceDTO


class JsonWorkspacesDisplayManager(BaseJsonDisplayManager):
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

    def display_workspaces(self, data: List[WorkspaceDTO]):
        self.workspaces_list_display.display(data)

    def display_workspace(self, data: WorkspaceDTO):
        self.workspaces_single_item_display.display(data)

    def display_workspace_access_info(self, data: List[WorkspaceAccessInformationDTO]):
        self.workspace_access_info_display.display(data)


DEFAULT_WORKSPACES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "workspace_id": get_column("ID", no_wrap=True),
    "workspace_name": get_column("Name"),
    "workspace_status": get_column("Status"),
    "workspace_created_at": get_column("Created At"),
    "cluster_name": get_column("Deployed to Cluster"),
    "workspace_access_information.access_endpoint": get_column("Access Endpoint"),
}


class TableWorkspacesDisplayManager(BaseTableDisplayManager):
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
    ):
        super().__init__()
        self.workspaces_list_display = ConsoleListDisplay(
            renderer=workspaces_list_renderer
        )
        self.workspaces_single_item_display = ConsoleSingleItemDisplay(
            renderer=workspaces_single_item_renderer
        )

    def display_workspaces(self, data: List[WorkspaceDTO]):
        self.workspaces_list_display.display(data)

    def display_workspace(self, data: WorkspaceDTO):
        self.workspaces_single_item_display.display(data)
