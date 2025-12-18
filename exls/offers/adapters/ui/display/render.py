from typing import Dict

from exls.shared.adapters.ui.output.render.service import format_float
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.view import ViewContext

_OFFERS_LIST_VIEW_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "gpu_type": TableRenderContext.get_column("GPU"),
    "gpu_count": TableRenderContext.get_column("Qty"),
    "provider": TableRenderContext.get_column("Cloud"),
    "instance_type": TableRenderContext.get_column("Instance Type"),
    "gpu_memory_mib": TableRenderContext.get_column("GPU Mem (MiB)"),
    "num_vcpus": TableRenderContext.get_column("vCPUs"),
    "main_memory_mib": TableRenderContext.get_column("Host Mem (MiB)"),
    "price_per_hour": TableRenderContext.get_column(
        "Hourly Cost", value_formatter=format_float
    ),
    "region": TableRenderContext.get_column("Region"),
}

OFFER_LIST_VIEW = ViewContext.from_table_columns(_OFFERS_LIST_VIEW_COLUMNS)
