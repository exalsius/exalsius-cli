from typing import Dict

from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.view import ViewContext

_USER_COLUMNS: Dict[str, Column] = {
    "email": TableRenderContext.get_column("Email"),
    "org_name": TableRenderContext.get_column(
        "Organization", value_formatter=lambda v: v or "-"
    ),
    "roles": TableRenderContext.get_column(
        "Roles", value_formatter=lambda v: ", ".join(v) if v else "-"
    ),
    "groups": TableRenderContext.get_column(
        "Groups", value_formatter=lambda v: ", ".join(v) if v else "-"
    ),
}

USER_VIEW = ViewContext.from_table_columns(_USER_COLUMNS)
