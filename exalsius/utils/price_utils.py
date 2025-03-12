import pandas as pd


def process_accelerator_data(result: dict) -> dict[str, pd.DataFrame]:
    """Process the raw accelerator data into sorted DataFrames"""
    processed_data = {}

    for gpu, items in result.items():
        # Convert list of InstanceTypeInfo to DataFrame
        df = pd.DataFrame([t._asdict() for t in items])

        # Calculate minimum prices and sort
        df = (
            df.assign(
                min_price=df.groupby("cloud")["price"].transform("min"),
                min_spot_price=df.groupby("cloud")["spot_price"].transform("min"),
            )
            .sort_values(
                by=["min_price", "min_spot_price", "cloud", "price", "spot_price"]
            )
            .drop(columns=["min_price", "min_spot_price"])
        )

        processed_data[gpu] = df

    return processed_data


def _sort_by_cheapest(result: dict) -> pd.DataFrame:
    """Process the raw accelerator data into a single sorted DataFrame"""
    all_items = []

    for gpu, items in result.items():
        for item in items:
            data = item._asdict()
            data["gpu"] = gpu
            all_items.append(data)

    df = pd.DataFrame(all_items)

    df = df.sort_values(by=["price", "spot_price", "cloud", "gpu"], na_position="last")

    return df
