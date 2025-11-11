from abc import ABC, abstractmethod
from typing import List

from exls.core.commons.display import (
    BaseDisplayManager,
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ComposingDisplayManager,
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exls.core.commons.render.json import (
    JsonListStringRenderer,
    JsonSingleItemStringRenderer,
)
from exls.core.commons.render.table import (
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)
from exls.management.types.ssh_keys.dtos import SshKeyDTO
from exls.nodes.dtos import (
    CloudNodeDTO,
    NodeDTO,
    NodesImportFromOfferRequestDTO,
    NodesImportSSHRequestDTO,
    SelfManagedNodeDTO,
)
from exls.offers.dtos import OfferDTO


class BaseNodesDisplayManager(BaseDisplayManager, ABC):
    @abstractmethod
    def display_nodes(self, data: List[NodeDTO]):
        pass

    @abstractmethod
    def display_node(self, data: NodeDTO):
        pass

    @abstractmethod
    def display_ssh_keys(self, ssh_keys: List[SshKeyDTO]):
        pass

    @abstractmethod
    def display_offers(self, offers: List[OfferDTO]):
        pass

    @abstractmethod
    def display_import_ssh_request(self, dto: NodesImportSSHRequestDTO):
        pass

    @abstractmethod
    def display_import_offer_request(self, dto: NodesImportFromOfferRequestDTO):
        pass

    @abstractmethod
    def display_import_ssh_requests(self, dto: List[NodesImportSSHRequestDTO]):
        pass


class JsonNodesDisplayManager(BaseJsonDisplayManager, BaseNodesDisplayManager):
    def __init__(
        self,
        cloud_nodes_list_renderer: JsonListStringRenderer[
            CloudNodeDTO
        ] = JsonListStringRenderer[CloudNodeDTO](),
        self_managed_nodes_list_renderer: JsonListStringRenderer[
            SelfManagedNodeDTO
        ] = JsonListStringRenderer[SelfManagedNodeDTO](),
        cloud_nodes_single_item_renderer: JsonSingleItemStringRenderer[
            CloudNodeDTO
        ] = JsonSingleItemStringRenderer[CloudNodeDTO](),
        self_managed_nodes_single_item_renderer: JsonSingleItemStringRenderer[
            SelfManagedNodeDTO
        ] = JsonSingleItemStringRenderer[SelfManagedNodeDTO](),
        ssh_keys_list_renderer: JsonListStringRenderer[
            SshKeyDTO
        ] = JsonListStringRenderer[SshKeyDTO](),
        offers_list_renderer: JsonListStringRenderer[OfferDTO] = JsonListStringRenderer[
            OfferDTO
        ](),
        import_ssh_request_renderer: JsonSingleItemStringRenderer[
            NodesImportSSHRequestDTO
        ] = JsonSingleItemStringRenderer[NodesImportSSHRequestDTO](),
        import_ssh_requests_renderer: JsonListStringRenderer[
            NodesImportSSHRequestDTO
        ] = JsonListStringRenderer[NodesImportSSHRequestDTO](),
        import_offer_request_renderer: JsonSingleItemStringRenderer[
            NodesImportFromOfferRequestDTO
        ] = JsonSingleItemStringRenderer[NodesImportFromOfferRequestDTO](),
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
        self.ssh_keys_list_display = ConsoleListDisplay(renderer=ssh_keys_list_renderer)
        self.offers_list_display = ConsoleListDisplay(renderer=offers_list_renderer)
        self.import_ssh_request_display = ConsoleSingleItemDisplay(
            renderer=import_ssh_request_renderer
        )
        self.import_ssh_requests_display = ConsoleListDisplay(
            renderer=import_ssh_requests_renderer
        )
        self.import_offer_request_display = ConsoleSingleItemDisplay(
            renderer=import_offer_request_renderer
        )

    def display_nodes(self, data: List[NodeDTO]):
        cloud_nodes = [node for node in data if isinstance(node, CloudNodeDTO)]
        self_managed_nodes = [
            node for node in data if isinstance(node, SelfManagedNodeDTO)
        ]
        if cloud_nodes:
            self.cloud_nodes_list_display.display(cloud_nodes)
        if self_managed_nodes:
            self.self_managed_nodes_list_display.display(self_managed_nodes)

    def display_node(self, data: NodeDTO):
        if isinstance(data, CloudNodeDTO):
            self.cloud_nodes_single_item_display.display(data)
        elif isinstance(data, SelfManagedNodeDTO):
            self.self_managed_nodes_single_item_display.display(data)

    def display_ssh_keys(self, ssh_keys: List[SshKeyDTO]):
        self.ssh_keys_list_display.display(ssh_keys)

    def display_offers(self, offers: List[OfferDTO]):
        self.offers_list_display.display(offers)

    def display_import_ssh_request(self, dto: NodesImportSSHRequestDTO):
        self.import_ssh_request_display.display(dto)

    def display_import_offer_request(self, dto: NodesImportFromOfferRequestDTO):
        self.import_offer_request_display.display(dto)

    def display_import_ssh_requests(self, dto: List[NodesImportSSHRequestDTO]):
        self.import_ssh_requests_display.display(dto)


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

DEFAULT_SSH_KEY_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "name": get_column("Name"),
}

DEFAULT_OFFER_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "provider": get_column("Provider"),
    "instance_type": get_column("Instance Type"),
    "price_per_hour": get_column("Price/Hour"),
    "gpu_type": get_column("GPU Type"),
    "gpu_count": get_column("GPU Count"),
    "region": get_column("Region"),
}

DEFAULT_IMPORT_SSH_REQUEST_COLUMNS_RENDERING_MAP = {
    "hostname": get_column("Hostname"),
    "endpoint": get_column("Endpoint"),
    "username": get_column("Username"),
    "ssh_key_name": get_column("SSH Key"),
}

DEFAULT_IMPORT_OFFER_REQUEST_COLUMNS_RENDERING_MAP = {
    "hostname": get_column("Hostname"),
    "offer_id": get_column("Offer ID"),
    "amount": get_column("Amount"),
}


class TableNodesDisplayManager(BaseTableDisplayManager, BaseNodesDisplayManager):
    def __init__(
        self,
        cloud_nodes_list_renderer: TableListRenderer[CloudNodeDTO] = TableListRenderer[
            CloudNodeDTO
        ](columns_rendering_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP),
        self_managed_nodes_list_renderer: TableListRenderer[
            SelfManagedNodeDTO
        ] = TableListRenderer[SelfManagedNodeDTO](
            columns_rendering_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
        cloud_nodes_single_item_renderer: TableSingleItemRenderer[
            CloudNodeDTO
        ] = TableSingleItemRenderer[CloudNodeDTO](
            columns_map=DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP
        ),
        self_managed_nodes_single_item_renderer: TableSingleItemRenderer[
            SelfManagedNodeDTO
        ] = TableSingleItemRenderer[SelfManagedNodeDTO](
            columns_map=DEFAULT_SELF_MANAGED_NODE_COLUMNS_RENDERING_MAP
        ),
        ssh_keys_list_renderer: TableListRenderer[SshKeyDTO] = TableListRenderer[
            SshKeyDTO
        ](columns_rendering_map=DEFAULT_SSH_KEY_COLUMNS_RENDERING_MAP),
        offers_list_renderer: TableListRenderer[OfferDTO] = TableListRenderer[OfferDTO](
            columns_rendering_map=DEFAULT_OFFER_COLUMNS_RENDERING_MAP
        ),
        import_ssh_request_renderer: TableSingleItemRenderer[
            NodesImportSSHRequestDTO
        ] = TableSingleItemRenderer[NodesImportSSHRequestDTO](
            columns_map=DEFAULT_IMPORT_SSH_REQUEST_COLUMNS_RENDERING_MAP
        ),
        import_ssh_requests_renderer: TableListRenderer[
            NodesImportSSHRequestDTO
        ] = TableListRenderer[NodesImportSSHRequestDTO](
            columns_rendering_map=DEFAULT_IMPORT_SSH_REQUEST_COLUMNS_RENDERING_MAP
        ),
        import_offer_request_renderer: TableSingleItemRenderer[
            NodesImportFromOfferRequestDTO
        ] = TableSingleItemRenderer[NodesImportFromOfferRequestDTO](
            columns_map=DEFAULT_IMPORT_OFFER_REQUEST_COLUMNS_RENDERING_MAP
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
        self.ssh_keys_list_display = ConsoleListDisplay(renderer=ssh_keys_list_renderer)
        self.offers_list_display = ConsoleListDisplay(renderer=offers_list_renderer)
        self.import_ssh_request_display = ConsoleSingleItemDisplay(
            renderer=import_ssh_request_renderer
        )
        self.import_ssh_requests_display = ConsoleListDisplay(
            renderer=import_ssh_requests_renderer
        )
        self.import_offer_request_display = ConsoleSingleItemDisplay(
            renderer=import_offer_request_renderer
        )

    def display_nodes(self, data: List[NodeDTO]):
        cloud_nodes = [node for node in data if isinstance(node, CloudNodeDTO)]
        if cloud_nodes:
            self.cloud_nodes_list_display.display(cloud_nodes)

        self_managed_nodes = [
            node for node in data if isinstance(node, SelfManagedNodeDTO)
        ]
        if self_managed_nodes:
            self.self_managed_nodes_list_display.display(self_managed_nodes)

    def display_node(self, data: NodeDTO):
        if isinstance(data, CloudNodeDTO):
            self.cloud_nodes_single_item_display.display(data)
        elif isinstance(data, SelfManagedNodeDTO):
            self.self_managed_nodes_single_item_display.display(data)

    def display_ssh_keys(self, ssh_keys: List[SshKeyDTO]):
        self.ssh_keys_list_display.display(ssh_keys)

    def display_offers(self, offers: List[OfferDTO]):
        self.offers_list_display.display(offers)

    def display_import_ssh_request(self, dto: NodesImportSSHRequestDTO):
        self.import_ssh_request_display.display(dto)

    def display_import_offer_request(self, dto: NodesImportFromOfferRequestDTO):
        self.import_offer_request_display.display(dto)

    def display_import_ssh_requests(self, dto: List[NodesImportSSHRequestDTO]):
        self.import_ssh_requests_display.display(dto)


class ComposingNodeDisplayManager(ComposingDisplayManager):
    def __init__(
        self,
        display_manager: BaseNodesDisplayManager,
    ):
        super().__init__(display_manager=display_manager)
        self.display_manager: BaseNodesDisplayManager = display_manager

    def display_nodes(self, nodes: List[NodeDTO]):
        self.display_manager.display_nodes(nodes)

    def display_node(self, node: NodeDTO):
        self.display_manager.display_node(node)

    def display_ssh_keys(self, ssh_keys: List[SshKeyDTO]):
        self.display_manager.display_ssh_keys(ssh_keys)

    def display_offers(self, offers: List[OfferDTO]):
        self.display_manager.display_offers(offers)

    def display_import_ssh_request(self, dto: NodesImportSSHRequestDTO):
        self.display_manager.display_import_ssh_request(dto)

    def display_import_offer_request(self, dto: NodesImportFromOfferRequestDTO):
        self.display_manager.display_import_offer_request(dto)

    def display_import_ssh_requests(self, dto: List[NodesImportSSHRequestDTO]):
        self.display_manager.display_import_ssh_requests(dto)
