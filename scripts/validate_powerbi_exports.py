"""Validate CSV exports using the Power BI regional format."""

from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS = {
    "stores": {"store_id", "store_name", "region", "store_type", "opened_date"},
    "products": {"product_id", "product_name", "category", "unit_cost", "unit_price"},
    "customers": {"customer_id", "segment", "region", "signup_date"},
    "sales": {
        "sale_id",
        "sale_date",
        "store_id",
        "product_id",
        "customer_id",
        "quantity",
        "unit_price",
        "discount",
    },
    "inventory": {
        "inventory_date",
        "store_id",
        "product_id",
        "stock_on_hand",
        "reorder_point",
        "stock_in",
        "stock_out",
    },
}


def main() -> None:
    export_dir = Path("data/generated/powerbi")
    for table_name, expected_columns in EXPECTED_COLUMNS.items():
        path = export_dir / f"{table_name}.csv"
        frame = pd.read_csv(path, sep=";", decimal=",")
        missing_columns = expected_columns.difference(frame.columns)
        if missing_columns:
            raise ValueError(f"{table_name}: missing columns {sorted(missing_columns)}")
        if frame.empty:
            raise ValueError(f"{table_name}: export is empty")
        print(f"{table_name}: {len(frame):,} rows, regional parsing OK")

    sales = pd.read_csv(export_dir / "sales.csv", sep=";", decimal=",")
    if not sales["unit_price"].between(0, 100_000).all():
        raise ValueError("sales.unit_price is outside the expected range")
    if not sales["discount"].between(0, 1).all():
        raise ValueError("sales.discount must be between 0 and 1")
    print("Power BI exports passed validation")


if __name__ == "__main__":
    main()
