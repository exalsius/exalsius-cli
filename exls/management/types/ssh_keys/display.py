from typing import Dict, List

from exls.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exls.core.commons.render.json import JsonListStringRenderer
from exls.core.commons.render.table import Column, TableListRenderer, get_column
from exls.management.types.ssh_keys.dtos import SshKeyDTO


class JsonSshKeysDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        ssh_keys_list_renderer: JsonListStringRenderer[
            SshKeyDTO
        ] = JsonListStringRenderer[SshKeyDTO](),
    ):
        super().__init__()
        self.ssh_keys_list_display = ConsoleListDisplay(renderer=ssh_keys_list_renderer)

    def display_ssh_keys(self, ssh_keys: List[SshKeyDTO]):
        self.ssh_keys_list_display.display(ssh_keys)


DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
}


class TableSshKeysDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        ssh_keys_list_renderer: TableListRenderer[SshKeyDTO] = TableListRenderer(
            columns_rendering_map=DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.ssh_keys_list_display = ConsoleListDisplay(renderer=ssh_keys_list_renderer)

    def display_ssh_keys(self, ssh_keys: List[SshKeyDTO]):
        self.ssh_keys_list_display.display(ssh_keys)
