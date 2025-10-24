from typing import Dict, List

from exls.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exls.core.commons.render.json import JsonListStringRenderer
from exls.core.commons.render.table import Column, TableListRenderer, get_column
from exls.management.types.credentials.dtos import CredentialsDTO


class JsonCredentialsDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        credentials_list_renderer: JsonListStringRenderer[
            CredentialsDTO
        ] = JsonListStringRenderer[CredentialsDTO](),
    ):
        super().__init__()
        self.credentials_list_display = ConsoleListDisplay(
            renderer=credentials_list_renderer
        )

    def display_credentials(self, credentials: List[CredentialsDTO]):
        self.credentials_list_display.display(credentials)


DEFAULT_CREDENTIALS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Credential Name"),
    "description": get_column("Credential Description"),
}


class TableCredentialsDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        credentials_list_renderer: TableListRenderer[
            CredentialsDTO
        ] = TableListRenderer[CredentialsDTO](
            columns_rendering_map=DEFAULT_CREDENTIALS_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.credentials_list_display = ConsoleListDisplay(
            renderer=credentials_list_renderer
        )

    def display_credentials(self, credentials: List[CredentialsDTO]):
        self.credentials_list_display.display(credentials)
