from typing import List

from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.cloud_node import CloudNode
from exalsius_api_client.models.self_managed_node import SelfManagedNode
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)

from exalsius.core.base.render import BaseListRenderer, BaseSingleItemRenderer
from exalsius.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exalsius.core.commons.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exalsius.core.commons.render.table import (
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)


class JsonNodesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        cloud_nodes_list_renderer: BaseListRenderer[
            CloudNode, str
        ] = JsonListStringRenderer[CloudNode](),
        self_managed_nodes_list_renderer: BaseListRenderer[
            SelfManagedNode, str
        ] = JsonListStringRenderer[SelfManagedNode](),
        cloud_nodes_single_item_renderer: BaseSingleItemRenderer[
            CloudNode, str
        ] = JsonSingleItemStringRenderer[CloudNode](),
        self_managed_nodes_single_item_renderer: BaseSingleItemRenderer[
            SelfManagedNode, str
        ] = JsonSingleItemStringRenderer[SelfManagedNode](),
    ):
        super().__init__()
        self.cloud_nodes_list_display = ConsoleListDisplay[CloudNode](
            renderer=cloud_nodes_list_renderer
        )
        self.self_managed_nodes_list_display = ConsoleListDisplay[SelfManagedNode](
            renderer=self_managed_nodes_list_renderer
        )
        self.cloud_nodes_single_item_display = ConsoleSingleItemDisplay[CloudNode](
            renderer=cloud_nodes_single_item_renderer
        )
        self.self_managed_nodes_single_item_display = ConsoleSingleItemDisplay[
            SelfManagedNode
        ](renderer=self_managed_nodes_single_item_renderer)

    def display_nodes(self, data: List[BaseNode]):
        cloud_nodes = [node for node in data if isinstance(node, CloudNode)]
        self_managed_nodes = [
            node for node in data if isinstance(node, SelfManagedNode)
        ]
        if cloud_nodes:
            self.cloud_nodes_list_display.display(cloud_nodes)
        if self_managed_nodes:
            self.self_managed_nodes_list_display.display(self_managed_nodes)

    def display_node(self, data: BaseNode):
        if isinstance(data, CloudNode):
            self.cloud_nodes_single_item_display.display(data)
        elif isinstance(data, SelfManagedNode):
            self.self_managed_nodes_single_item_display.display(data)


DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "hostname": get_column("Hostname"),
    "import_time": get_column("Import Time"),
    "node_status": get_column("Status"),
    "provider": get_column("Provider"),
    "instance_type": get_column("Instance Type"),
    "price_per_hour": get_column("Price"),
}

DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "hostname": get_column("Hostname"),
    "import_time": get_column("Import Time"),
    "node_status": get_column("Status"),
    "endpoint": get_column("Endpoint"),
}


class TableNodesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        cloud_nodes_list_renderer: BaseListRenderer[CloudNode, str] = TableListRenderer[
            CloudNode
        ](columns_rendering_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP),
        self_managed_nodes_list_renderer: BaseListRenderer[
            SelfManagedNode, str
        ] = TableListRenderer[SelfManagedNode](
            columns_rendering_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
        cloud_nodes_single_item_renderer: BaseSingleItemRenderer[
            CloudNode, str
        ] = TableSingleItemRenderer[CloudNode](
            columns_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP
        ),
        self_managed_nodes_single_item_renderer: BaseSingleItemRenderer[
            SelfManagedNode, str
        ] = TableSingleItemRenderer[SelfManagedNode](
            columns_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.cloud_nodes_list_display = ConsoleListDisplay[CloudNode](
            renderer=cloud_nodes_list_renderer
        )
        self.self_managed_nodes_list_display = ConsoleListDisplay[SelfManagedNode](
            renderer=self_managed_nodes_list_renderer
        )
        self.cloud_nodes_single_item_display = ConsoleSingleItemDisplay[CloudNode](
            renderer=cloud_nodes_single_item_renderer
        )
        self.self_managed_nodes_single_item_display = ConsoleSingleItemDisplay[
            SelfManagedNode
        ](renderer=self_managed_nodes_single_item_renderer)

    def display_nodes(self, data: List[BaseNode]):
        cloud_nodes = [node for node in data if isinstance(node, CloudNode)]
        if cloud_nodes:
            self.cloud_nodes_list_display.display(cloud_nodes)

        self_managed_nodes = [
            node for node in data if isinstance(node, SelfManagedNode)
        ]
        if self_managed_nodes:
            self.self_managed_nodes_list_display.display(self_managed_nodes)

    def display_node(self, data: BaseNode):
        if isinstance(data, CloudNode):
            self.cloud_nodes_single_item_display.display(data)
        elif isinstance(data, SelfManagedNode):
            self.self_managed_nodes_single_item_display.display(data)


DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
}


class JsonSshKeysDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        ssh_keys_list_renderer: BaseListRenderer[
            SshKeysListResponseSshKeysInner, str
        ] = JsonListStringRenderer[SshKeysListResponseSshKeysInner](),
    ):
        super().__init__()
        self.ssh_keys_list_display = ConsoleListDisplay[
            SshKeysListResponseSshKeysInner
        ](renderer=ssh_keys_list_renderer)

    def display_ssh_keys(self, ssh_keys: List[SshKeysListResponseSshKeysInner]):
        self.ssh_keys_list_display.display(ssh_keys)


class TableSshKeysDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        ssh_keys_list_renderer: BaseListRenderer[
            SshKeysListResponseSshKeysInner, str
        ] = TableListRenderer[SshKeysListResponseSshKeysInner](
            columns_rendering_map=DEFAULT_SSH_KEYS_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.ssh_keys_list_display = ConsoleListDisplay[
            SshKeysListResponseSshKeysInner
        ](renderer=ssh_keys_list_renderer)

    def display_ssh_keys(self, ssh_keys: List[SshKeysListResponseSshKeysInner]):
        self.ssh_keys_list_display.display(ssh_keys)
