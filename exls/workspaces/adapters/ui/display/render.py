from typing import Dict

from exls.shared.adapters.ui.output.render.service import format_datetime
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.view import ViewContext

# -----------------------------------------------------------------------------
# WORKSPACE VIEWS
# -----------------------------------------------------------------------------


_WORKSPACE_LIST_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "template_name": TableRenderContext.get_column("Template"),
    "status": TableRenderContext.get_column("Status"),
    "created_at": TableRenderContext.get_column(
        "Created At", value_formatter=format_datetime
    ),
    "cluster_id": TableRenderContext.get_column("Cluster ID"),
    "formatted_access_information": TableRenderContext.get_column("Access"),
}

WORKSPACE_LIST_VIEW = ViewContext.from_table_columns(_WORKSPACE_LIST_COLUMNS)

# -----------------------------------------------------------------------------
# DEPLOY REQUEST VIEWS
# -----------------------------------------------------------------------------

_DEPLOY_WORKSPACE_REQUEST_COLUMNS: Dict[str, Column] = {
    "cluster_id": TableRenderContext.get_column("Cluster ID"),
    "workspace_name": TableRenderContext.get_column("Name"),
    "template_id": TableRenderContext.get_column("Template"),
    "resources.gpu_count": TableRenderContext.get_column("GPUs"),
    "resources.cpu_cores": TableRenderContext.get_column("CPUs"),
    "resources.memory_gb": TableRenderContext.get_column("Memory (GB)"),
}

DEPLOY_WORKSPACE_REQUEST_VIEW = ViewContext.from_table_columns(
    _DEPLOY_WORKSPACE_REQUEST_COLUMNS
)
