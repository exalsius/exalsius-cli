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

        # Convert to dict, then dump to JSON with custom serializer
        data = (
            workspace_response.to_dict()
            if hasattr(workspace_response, "to_dict")
            else workspace_response.dict()
        )
        json_str = json.dumps(data, default=default_serializer, indent=2)
        self.console.print(JSON(json_str))
