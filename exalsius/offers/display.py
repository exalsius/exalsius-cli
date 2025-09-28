from typing import List

from exalsius_api_client.models.offer import Offer

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


class JsonOffersDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        offers_list_renderer: JsonListStringRenderer[Offer] = JsonListStringRenderer[
            Offer
        ](),
        offers_single_item_renderer: JsonSingleItemStringRenderer[
            Offer
        ] = JsonSingleItemStringRenderer[Offer](),
    ):
        super().__init__()
        self.offers_list_display = ConsoleListDisplay(renderer=offers_list_renderer)
        self.offers_single_item_display = ConsoleSingleItemDisplay(
            renderer=offers_single_item_renderer
        )

    def display_offers(self, data: List[Offer]):
        self.offers_list_display.display(data)

    def display_offer(self, data: Offer):
        self.offers_single_item_display.display(data)


DEFAULT_COLUMNS_RENDERING_MAP = {
    "id": get_column("ID", no_wrap=True),
    "gpu_type": get_column("GPU"),
    "gpu_count": get_column("Qty"),
    "cloud_provider": get_column("Cloud"),
    "instance_type": get_column("Instance Type"),
    "gpu_memory_mib": get_column("GPU Mem (MiB)"),
    "num_vcpus": get_column("vCPUs"),
    "main_memory_mib": get_column("Host Mem (MiB)"),
    "hourly_cost": get_column("Hourly Cost"),
    "region": get_column("Region"),
}


class TableOffersDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        offers_list_renderer: TableListRenderer[Offer] = TableListRenderer[Offer](
            columns_rendering_map=DEFAULT_COLUMNS_RENDERING_MAP
        ),
        offers_single_item_renderer: TableSingleItemRenderer[
            Offer
        ] = TableSingleItemRenderer[Offer](columns_map=DEFAULT_COLUMNS_RENDERING_MAP),
    ):
        super().__init__()
        self.offers_list_display = ConsoleListDisplay(renderer=offers_list_renderer)
        self.offers_single_item_display = ConsoleSingleItemDisplay(
            renderer=offers_single_item_renderer
        )

    def display_offers(self, data: List[Offer]):
        self.offers_list_display.display(data)

    def display_offer(self, data: Offer):
        self.offers_single_item_display.display(data)
