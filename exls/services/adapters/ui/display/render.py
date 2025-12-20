from typing import Dict

from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.view import ViewContext

_SERVICE_VIEW_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "name": TableRenderContext.get_column("Name"),
    "cluster_id": TableRenderContext.get_column("Cluster ID"),
    "service_template": TableRenderContext.get_column("Service Template"),
    "created_at": TableRenderContext.get_column("Created At"),
}

SERVICE_VIEW = ViewContext.from_table_columns(_SERVICE_VIEW_COLUMNS)
