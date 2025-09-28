from typing import Dict, List

from exalsius_api_client.models.credentials import Credentials

from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exalsius.core.commons.render.json import JsonListStringRenderer
from exalsius.core.commons.render.table import Column, TableListRenderer, get_column


class JsonCredentialsDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        credentials_list_renderer: JsonListStringRenderer[
            Credentials
        ] = JsonListStringRenderer[Credentials](),
    ):
        super().__init__()
        self.credentials_list_display = ConsoleListDisplay(
            renderer=credentials_list_renderer
        )

    def display_credentials(self, credentials: List[Credentials]):
        self.credentials_list_display.display(credentials)


DEFAULT_CREDENTIALS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Credential Name"),
    "description": get_column("Credential Description"),
}


class TableCredentialsDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        credentials_list_renderer: TableListRenderer[Credentials] = TableListRenderer[
            Credentials
        ](columns_rendering_map=DEFAULT_CREDENTIALS_COLUMNS_RENDERING_MAP),
    ):
        super().__init__()
        self.credentials_list_display = ConsoleListDisplay(
            renderer=credentials_list_renderer
        )

    def display_credentials(self, credentials: List[Credentials]):
        self.credentials_list_display.display(credentials)
