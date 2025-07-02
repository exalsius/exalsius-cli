from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse
from rich.console import Console

from exalsius.display.base import BaseDisplayManager


class WorkspacesDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_workspaces(self, workspaces: WorkspacesListResponse):
        # TODO: implement table view for workspaces
        pass
