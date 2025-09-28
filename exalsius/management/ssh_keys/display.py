from typing import Dict, List

from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)

from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exalsius.core.commons.render.json import JsonListStringRenderer
from exalsius.core.commons.render.table import Column, TableListRenderer, get_column


class JsonSshKeysDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        ssh_keys_list_renderer: JsonListStringRenderer[
            SshKeysListResponseSshKeysInner
        ] = JsonListStringRenderer[SshKeysListResponseSshKeysInner](),
    ):
        super().__init__()
        self.ssh_keys_list_display = ConsoleListDisplay(renderer=ssh_keys_list_renderer)

    def display_ssh_keys(self, ssh_keys: List[SshKeysListResponseSshKeysInner]):
        self.ssh_keys_list_display.display(ssh_keys)


DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
}


class TableSshKeysDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        ssh_keys_list_renderer: TableListRenderer[
            SshKeysListResponseSshKeysInner
        ] = TableListRenderer(
            columns_rendering_map=DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.ssh_keys_list_display = ConsoleListDisplay(renderer=ssh_keys_list_renderer)

    def display_ssh_keys(self, ssh_keys: List[SshKeysListResponseSshKeysInner]):
        self.ssh_keys_list_display.display(ssh_keys)
