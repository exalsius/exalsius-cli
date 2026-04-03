from typing import Dict

from exls.shared.adapters.ui.output.render.service import (
    format_datetime,
    format_datetime_humanized,
    format_na,
    format_short_id,
)
from exls.shared.adapters.ui.output.render.table import Column, TableRenderContext
from exls.shared.adapters.ui.output.view import ViewContext

# -----------------------------------------------------------------------------
# NODE LIST VIEWS (humanized timestamps)
# -----------------------------------------------------------------------------

_NODE_LIST_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column(
        "ID", no_wrap=True, value_formatter=format_short_id
    ),
    "hostname": TableRenderContext.get_column("Hostname"),
    "status": TableRenderContext.get_column("Status"),
    "resources": TableRenderContext.get_column(
        "GPU",
        value_formatter=lambda r: (
            f"{r.gpu_count}x {r.gpu_vendor} {r.gpu_type}"
            if hasattr(r, "gpu_count") and r.gpu_count > 0
            else "N/A"
        ),
    ),
    "price_per_hour": TableRenderContext.get_column("Price", value_formatter=format_na),
    # Self-Managed Node Attributes
    "username": TableRenderContext.get_column("Username"),
    "ssh_key_name": TableRenderContext.get_column("SSH Key"),
    "endpoint": TableRenderContext.get_column("Endpoint", value_formatter=format_na),
    "import_time": TableRenderContext.get_column(
        "Import Time", value_formatter=format_datetime_humanized
    ),
}

NODE_LIST_VIEW = ViewContext.from_table_columns(_NODE_LIST_COLUMNS)


# -----------------------------------------------------------------------------
# NODE DETAIL VIEWS (ISO timestamps for single resource get)
# -----------------------------------------------------------------------------

_NODE_DETAIL_COLUMNS: Dict[str, Column] = {
    "id": TableRenderContext.get_column("ID", no_wrap=True),
    "hostname": TableRenderContext.get_column("Hostname"),
    "import_time": TableRenderContext.get_column(
        "Import Time", value_formatter=format_datetime
    ),
    "status": TableRenderContext.get_column("Status"),
    "warning_message": TableRenderContext.get_column("Warning", hide_if_empty=True),
    "price_per_hour": TableRenderContext.get_column("Price", value_formatter=format_na),
    # Hardware Resources
    "resources.gpu_vendor": TableRenderContext.get_column("GPU Vendor"),
    "resources.gpu_type": TableRenderContext.get_column("GPU Type"),
    "resources.gpu_count": TableRenderContext.get_column("GPU Count"),
    "resources.cpu_cores": TableRenderContext.get_column("CPU Cores"),
    "resources.memory_gb": TableRenderContext.get_column("Memory (GB)"),
    "resources.storage_gb": TableRenderContext.get_column("Storage (GB)"),
    # Cloud Node Attributes
    "provider": TableRenderContext.get_column("Provider"),
    "instance_type": TableRenderContext.get_column("Instance Type"),
    # Self-Managed Node Attributes
    "username": TableRenderContext.get_column("Username"),
    "ssh_key_name": TableRenderContext.get_column("SSH Key"),
    "endpoint": TableRenderContext.get_column("Endpoint", value_formatter=format_na),
}

NODE_DETAIL_VIEW = ViewContext.from_table_columns(_NODE_DETAIL_COLUMNS)

# -----------------------------------------------------------------------------
# IMPORT REQUEST VIEWS
# -----------------------------------------------------------------------------

_IMPORT_SELFMANAGED_NODE_REQUEST_COLUMNS: Dict[str, Column] = {
    "hostname": TableRenderContext.get_column("Hostname"),
    "endpoint": TableRenderContext.get_column("Endpoint"),
    "username": TableRenderContext.get_column("Username"),
    "ssh_key": TableRenderContext.get_column(
        "SSH Key",
        value_formatter=lambda val: val.name if hasattr(val, "name") else str(val),
    ),
}

IMPORT_SELFMANAGED_NODE_REQUEST_VIEW = ViewContext.from_table_columns(
    _IMPORT_SELFMANAGED_NODE_REQUEST_COLUMNS
)

# -----------------------------------------------------------------------------
# FAILURE VIEWS
# -----------------------------------------------------------------------------

_NODE_IMPORT_FAILURE_COLUMNS: Dict[str, Column] = {
    "node_import_request.hostname": TableRenderContext.get_column("Node"),
    "error_message": TableRenderContext.get_column("Error Message"),
}

NODE_IMPORT_FAILURE_VIEW = ViewContext.from_table_columns(_NODE_IMPORT_FAILURE_COLUMNS)
