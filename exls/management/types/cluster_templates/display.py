from typing import Dict, List

from exls.core.commons.display import (
    BaseJsonDisplayManager,
    BaseTableDisplayManager,
    ConsoleListDisplay,
)
from exls.core.commons.render.json import JsonListStringRenderer
from exls.core.commons.render.table import Column, TableListRenderer, get_column
from exls.management.types.cluster_templates.dtos import ClusterTemplateDTO


class JsonClusterTemplatesDisplayManager(BaseJsonDisplayManager):
    def __init__(
        self,
        cluster_templates_list_renderer: JsonListStringRenderer[
            ClusterTemplateDTO
        ] = JsonListStringRenderer[ClusterTemplateDTO](),
    ):
        super().__init__()
        self.cluster_templates_list_display = ConsoleListDisplay(
            renderer=cluster_templates_list_renderer
        )

    def display_cluster_templates(self, cluster_templates: List[ClusterTemplateDTO]):
        self.cluster_templates_list_display.display(cluster_templates)


DEFAULT_CLUSTER_TEMPLATES_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "name": get_column("Name"),
    "description": get_column("Description"),
    "k8s_version": get_column("Kubernetes Version"),
}


class TableClusterTemplatesDisplayManager(BaseTableDisplayManager):
    def __init__(
        self,
        cluster_templates_list_renderer: TableListRenderer[
            ClusterTemplateDTO
        ] = TableListRenderer(
            columns_rendering_map=DEFAULT_CLUSTER_TEMPLATES_COLUMNS_RENDERING_MAP
        ),
    ):
        super().__init__()
        self.cluster_templates_list_display = ConsoleListDisplay(
            renderer=cluster_templates_list_renderer
        )

    def display_cluster_templates(self, cluster_templates: List[ClusterTemplateDTO]):
        self.cluster_templates_list_display.display(cluster_templates)
