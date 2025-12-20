from typing import Dict

from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.view import ViewContext

_USER_COLUMNS: Dict[str, Column] = {
    "email": TableRenderContext.get_column("Email"),
    "nickname": TableRenderContext.get_column("Username"),
    "sub": TableRenderContext.get_column("Subject"),
}

USER_VIEW = ViewContext.from_table_columns(_USER_COLUMNS)
