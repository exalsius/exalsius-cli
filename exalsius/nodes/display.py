from typing import TYPE_CHECKING, List

from exalsius_api_client.models.base_node import BaseNode
from exalsius_api_client.models.cloud_node import CloudNode
from exalsius_api_client.models.offer import Offer
from exalsius_api_client.models.self_managed_node import SelfManagedNode
from exalsius_api_client.models.ssh_keys_list_response_ssh_keys_inner import (
    SshKeysListResponseSshKeysInner,
)

if TYPE_CHECKING:
    from exalsius.nodes.interactive import NodeInteractiveConfig

from exalsius.core.commons.display import (
    BaseInteractiveDisplay,
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
        cloud_nodes_list_renderer: JsonListStringRenderer[
            CloudNode
        ] = JsonListStringRenderer[CloudNode](),
        self_managed_nodes_list_renderer: JsonListStringRenderer[
            SelfManagedNode
        ] = JsonListStringRenderer[SelfManagedNode](),
        cloud_nodes_single_item_renderer: JsonSingleItemStringRenderer[
            CloudNode
        ] = JsonSingleItemStringRenderer[CloudNode](),
        self_managed_nodes_single_item_renderer: JsonSingleItemStringRenderer[
            SelfManagedNode
        ] = JsonSingleItemStringRenderer[SelfManagedNode](),
    ):
        super().__init__()
        self.cloud_nodes_list_display = ConsoleListDisplay(
            renderer=cloud_nodes_list_renderer
        )
        self.self_managed_nodes_list_display = ConsoleListDisplay(
            renderer=self_managed_nodes_list_renderer
        )
        self.cloud_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=cloud_nodes_single_item_renderer
        )
        self.self_managed_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=self_managed_nodes_single_item_renderer
        )

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
        cloud_nodes_list_renderer: TableListRenderer[CloudNode] = TableListRenderer[
            CloudNode
        ](columns_rendering_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP),
        self_managed_nodes_list_renderer: TableListRenderer[
            SelfManagedNode
        ] = TableListRenderer[SelfManagedNode](
            columns_rendering_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
        cloud_nodes_single_item_renderer: TableSingleItemRenderer[
            CloudNode
        ] = TableSingleItemRenderer[CloudNode](
            columns_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP
        ),
        self_managed_nodes_single_item_renderer: TableSingleItemRenderer[
            SelfManagedNode
        ] = TableSingleItemRenderer[SelfManagedNode](
            columns_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.cloud_nodes_list_display = ConsoleListDisplay(
            renderer=cloud_nodes_list_renderer
        )
        self.self_managed_nodes_list_display = ConsoleListDisplay(
            renderer=self_managed_nodes_list_renderer
        )
        self.cloud_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=cloud_nodes_single_item_renderer
        )
        self.self_managed_nodes_single_item_display = ConsoleSingleItemDisplay(
            renderer=self_managed_nodes_single_item_renderer
        )

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


class NodeInteractiveDisplay(BaseInteractiveDisplay):
    """Display manager for node interactive flows."""

    def display_available_ssh_keys(
        self, ssh_keys: List[SshKeysListResponseSshKeysInner]
    ):
        """Display available SSH keys in a table format."""
        if not ssh_keys:
            return

        # Use the same table rendering system as other tables
        from exalsius.management.ssh_keys.display import TableSshKeysDisplayManager

        ssh_keys_display_manager = TableSshKeysDisplayManager()

        self.console.print("\n[bold]Available SSH Keys:[/bold]")
        ssh_keys_display_manager.display_ssh_keys(ssh_keys)

    def display_available_offers(self, offers: List[Offer]):
        """Display available offers in a table format."""
        if not offers:
            return

        # Use the same table rendering system as other tables
        from exalsius.offers.display import TableOffersDisplayManager

        offers_display_manager = TableOffersDisplayManager()

        self.console.print("\n[bold]Available Offers:[/bold]")
        offers_display_manager.display_offers(offers)

    def display_import_summary(self, config: "NodeInteractiveConfig"):
        """Display import configuration summary in a panel."""
        from rich.panel import Panel

        if config.import_type == "SSH":
            summary_text = f"""
[bold]Import Type:[/bold] Self-managed (SSH)
[bold]Hostname:[/bold] {config.hostname}
[bold]Endpoint:[/bold] {config.endpoint}
[bold]Username:[/bold] {config.username}
[bold]SSH Key ID:[/bold] {config.ssh_key_id[:12]}...
"""
        else:  # OFFER
            summary_text = f"""
[bold]Import Type:[/bold] Cloud Offer
[bold]Offer ID:[/bold] {config.offer_id[:12]}...
[bold]Hostname:[/bold] {config.hostname}
[bold]Amount:[/bold] {config.amount}
"""

        panel = Panel(
            summary_text.strip(), title="Import Configuration", border_style="custom"
        )
        self.console.print(panel)

    def display_imported_node(self, node: BaseNode):
        """Display details of imported node."""
        from exalsius.nodes.display import TableNodesDisplayManager

        nodes_display_manager = TableNodesDisplayManager()

        self.console.print("\n[bold]Imported Node Details:[/bold]")
        nodes_display_manager.display_node(node)
