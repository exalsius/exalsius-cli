import pandas as pd
from rich.table import Table


def create_rich_table(df: pd.DataFrame, title: str, id_column: bool = False) -> Table:
    """Create a Rich table from processed DataFrame"""
    table = Table(
        title=title,
        show_header=True,
        header_style="bold",
        border_style="custom",
    )

    id_field_col = ["id", "ID"]

    columns = [
        ("accelerator_name", "GPU"),
        ("accelerator_count", "QTY"),
        ("cloud", "CLOUD"),
        ("instance_type", "INSTANCE_TYPE"),
        ("device_memory", "DEVICE_MEM"),
        ("cpu_count", "vCPUs"),
        ("memory", "HOST_MEM"),
        ("price", "HOURLY_PRICE"),
        ("spot_price", "HOURLY_SPOT_PRICE"),
        ("region", "REGION"),
    ]

    if id_column:
        columns.insert(0, id_field_col)

    for _, header in columns:
        table.add_column(header)

    for _, row in df.iterrows():
        formatted_row = [
            str(row["accelerator_name"]),
            str(row["accelerator_count"]),
            str(row["cloud"]),
            (
                str(row["instance_type"])
                if not pd.isna(row["instance_type"])
                else "(attachable)"
            ),
            (
                f"{row['device_memory']:.0f}GB"
                if not pd.isna(row["device_memory"])
                else "-"
            ),
            (
                str(int(row["cpu_count"]))
                if not pd.isna(row["cpu_count"])
                and float(row["cpu_count"]).is_integer()
                else f"{row['cpu_count']:.1f}" if not pd.isna(row["cpu_count"]) else "-"
            ),
            f"{row['memory']:.0f}GB" if not pd.isna(row["memory"]) else "-",
            f"$ {row['price']:.3f}" if not pd.isna(row["price"]) else "-",
            f"$ {row['spot_price']:.3f}" if not pd.isna(row["spot_price"]) else "-",
            str(row["region"]) if not pd.isna(row["region"]) else "-",
        ]
        if id_column:
            formatted_row.insert(0, str(row["id"]))
        table.add_row(*formatted_row)

    return table
