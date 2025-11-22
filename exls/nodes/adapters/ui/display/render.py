from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from exls.nodes.adapters.dtos import (
    CloudNodeDTO,
    ImportCloudNodeRequestDTO,
    ImportSelfmanagedNodeRequestDTO,
    SelfManagedNodeDTO,
)
from exls.shared.adapters.ui.display.render.service import format_datetime, format_na
from exls.shared.adapters.ui.display.render.table import Column, TableRenderContext

DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "hostname": TableRenderContext.get_column("Hostname"),
    "import_time": TableRenderContext.get_column(
        "Import Time", value_formatter=format_datetime
    ),
    "node_status": TableRenderContext.get_column("Status"),
    "provider": TableRenderContext.get_column("Provider"),
    "instance_type": TableRenderContext.get_column("Instance Type"),
    "price_per_hour": TableRenderContext.get_column("Price", value_formatter=format_na),
}

DEFAULT_SELFMANAGED_NODE_COLUMNS_RENDERING_MAP: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "hostname": TableRenderContext.get_column("Hostname"),
    "import_time": TableRenderContext.get_column(
        "Import Time", value_formatter=format_datetime
    ),
    "node_status": TableRenderContext.get_column("Status"),
    "endpoint": TableRenderContext.get_column("Endpoint", value_formatter=format_na),
}

DEFAULT_IMPORT_SELFMANAGED_NODE_REQUEST_COLUMNS_RENDERING_MAP = {
    "hostname": TableRenderContext.get_column("Hostname"),
    "endpoint": TableRenderContext.get_column("Endpoint"),
    "username": TableRenderContext.get_column("Username"),
    "ssh_key_name": TableRenderContext.get_column("SSH Key"),
}

DEFAULT_IMPORT_CLOUD_NODE_REQUEST_COLUMNS_RENDERING_MAP = {
    "hostname": TableRenderContext.get_column("Hostname"),
    "offer_id": TableRenderContext.get_column("Offer ID"),
    "amount": TableRenderContext.get_column("Amount"),
}

DEFAULT_OFFER_COLUMNS_RENDERING_MAP = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "gpu_type": TableRenderContext.get_column("GPU"),
    "gpu_count": TableRenderContext.get_column("Qty"),
    "provider": TableRenderContext.get_column("Cloud"),
    "instance_type": TableRenderContext.get_column("Instance Type"),
    "gpu_memory_mib": TableRenderContext.get_column("GPU Mem (MiB)"),
    "num_vcpus": TableRenderContext.get_column("vCPUs"),
    "main_memory_mib": TableRenderContext.get_column("Host Mem (MiB)"),
    "price_per_hour": TableRenderContext.get_column("Hourly Cost"),
    "region": TableRenderContext.get_column("Region"),
}

DTO_DISPLAY_CONFIG_MAP: Dict[Any, Dict[str, Column]] = {
    CloudNodeDTO: DEFAULT_CLOUD_NODE_COLUMNS_RENDERING_MAP,
    SelfManagedNodeDTO: DEFAULT_SELFMANAGED_NODE_COLUMNS_RENDERING_MAP,
    ImportSelfmanagedNodeRequestDTO: DEFAULT_IMPORT_SELFMANAGED_NODE_REQUEST_COLUMNS_RENDERING_MAP,
    ImportCloudNodeRequestDTO: DEFAULT_IMPORT_CLOUD_NODE_REQUEST_COLUMNS_RENDERING_MAP,
}


def get_columns_rendering_map(dto_type: Type[BaseModel]) -> Optional[Dict[str, Column]]:
    return DTO_DISPLAY_CONFIG_MAP.get(dto_type, None)
