from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.offers.adapters.dtos import OfferDTO
from exls.shared.adapters.ui.output.render.service import format_float
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext

DEFAULT_OFFER_COLUMNS_RENDERING_MAP = {
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

DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    OfferDTO: DEFAULT_OFFER_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)
