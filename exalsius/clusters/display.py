from typing import List

from exalsius_api_client.models.cluster import Cluster

from exalsius.core.base.models import ErrorDTO
from exalsius.core.base.render import BaseListRenderer, BaseSingleItemRenderer
from exalsius.core.commons.display import (
    ConsoleListDisplay,
    ConsoleSingleItemDisplay,
)
from exalsius.core.commons.render.json import (
    JsonListRenderer,
    JsonMessageRenderer,
    JsonSingleItemRenderer,
)
from exalsius.core.commons.render.table import (
    TableListRenderer,
    TableSingleItemRenderer,
    get_column,
)


class ClusterDisplayManager:
    def __init__(
        self,
        list_renderer: BaseListRenderer[Cluster, str],
        single_item_renderer: BaseSingleItemRenderer[Cluster, str],
        info_renderer: BaseSingleItemRenderer[str, str],
        success_renderer: BaseSingleItemRenderer[str, str],
        error_renderer: BaseSingleItemRenderer[ErrorDTO, str],
    ):
        self.list_display = ConsoleListDisplay[Cluster](renderer=list_renderer)
        self.single_item_display = ConsoleSingleItemDisplay[Cluster](
            renderer=single_item_renderer
        )
        self.info_display = ConsoleSingleItemDisplay[str](renderer=info_renderer)
        self.success_display = ConsoleSingleItemDisplay[str](renderer=success_renderer)
        self.error_display = ConsoleSingleItemDisplay[ErrorDTO](renderer=error_renderer)

    def display_clusters(self, data: List[Cluster]):
        self.list_display.display(data)

    def display_cluster(self, data: Cluster):
        self.single_item_display.display(data)

    def display_info(self, message: str):
        self.info_display.display(message)

    def display_success(self, message: str):
        self.success_display.display(message)

    def display_error(self, error: ErrorDTO):
        self.error_display.display(error)


class JsonClusterDisplayManager(ClusterDisplayManager):
    def __init__(self):
        super().__init__(
            list_renderer=JsonListRenderer[Cluster](),
            single_item_renderer=JsonSingleItemRenderer[Cluster](),
            info_renderer=JsonMessageRenderer(message_key="message"),
            success_renderer=JsonMessageRenderer(message_key="message"),
            error_renderer=JsonSingleItemRenderer[ErrorDTO](),
        )


class TableClusterDisplayManager(ClusterDisplayManager):
    def __init__(self):
        columns_rendering_map = {
            "id": get_column("ID", no_wrap=True),
            "name": get_column("Name"),
            "cluster_status": get_column("Status"),
            "created_at": get_column("Created At"),
            "updated_at": get_column("Updated At"),
        }
        super().__init__(
            list_renderer=TableListRenderer[Cluster](
                columns_rendering_map=columns_rendering_map
            ),
            single_item_renderer=TableSingleItemRenderer[Cluster](
                columns_map=columns_rendering_map
            ),
            info_renderer=JsonMessageRenderer(message_key="message"),
            success_renderer=JsonMessageRenderer(message_key="message"),
            error_renderer=JsonSingleItemRenderer[ErrorDTO](),
        )
