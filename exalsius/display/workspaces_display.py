from exalsius_api_client.models.workspace import Workspace
from exalsius_api_client.models.workspace_response import WorkspaceResponse
from exalsius_api_client.models.workspaces_list_response import WorkspacesListResponse
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from exalsius.display.base import BaseDisplayManager


class WorkspacesDisplayManager(BaseDisplayManager):
    def __init__(self, console: Console):
        super().__init__(console)

    def display_workspaces(self, workspace_list_response: WorkspacesListResponse):
        """Display a list of workspaces in a formatted table."""
        table = Table(
            title="exalsius Workspaces",
            show_header=True,
            header_style="bold",
            border_style="custom",
        )

        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Owner", style="green")

        for workspace in workspace_list_response.workspaces:
            table.add_row(
                workspace.id,
                workspace.name,
                workspace.workspace_status or "N/A",
                workspace.owner,
            )

        self.console.print(table)

    def display_workspace(self, workspace_response: WorkspaceResponse):
        import json
        from datetime import datetime

        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        if workspace_response.workspace:
            workspace: Workspace = workspace_response.workspace
        else:
            self.print_warning(
                f"Workspace response is not a valid workspace: {workspace_response}"
            )
            return

        try:
            json_str = json.dumps(
                workspace.to_dict(), default=default_serializer, indent=2
            )
            self.console.print(JSON(json_str))
        except Exception as e:
            self.print_error(
                f"Error displaying workspace {workspace.name} ({workspace.id}): {e}"
            )
