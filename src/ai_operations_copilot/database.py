"""Load validated DataFrames into the PostgreSQL MVP schema."""

from __future__ import annotations

from collections.abc import Mapping
from io import StringIO

import pandas as pd
import psycopg

from .etl import validate_dataset


TABLE_COLUMNS: dict[str, list[str]] = {
    "stores": ["store_id", "store_name", "region", "store_type", "opened_date"],
    "products": ["product_id", "product_name", "category", "unit_cost", "unit_price"],
    "customers": ["customer_id", "segment", "region", "signup_date"],
    "sales": [
        "sale_id",
        "sale_date",
        "store_id",
        "product_id",
        "customer_id",
        "quantity",
        "unit_price",
        "discount",
    ],
    "inventory": [
        "inventory_date",
        "store_id",
        "product_id",
        "stock_on_hand",
        "reorder_point",
        "stock_in",
        "stock_out",
    ],
}


def load_dataset(dataset: Mapping[str, pd.DataFrame], connection_string: str) -> None:
    """Replace raw MVP tables with a validated dataset in one transaction."""
    validate_dataset(dataset)
    with psycopg.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE sales, inventory, customers, products, stores CASCADE")
            for table_name in ("stores", "products", "customers", "sales", "inventory"):
                _copy_frame(cursor, table_name, dataset[table_name])


def _copy_frame(cursor: psycopg.Cursor, table_name: str, frame: pd.DataFrame) -> None:
    columns = TABLE_COLUMNS[table_name]
    csv_data = frame[columns].to_csv(index=False, header=False, na_rep="\\N")
    quoted_columns = ", ".join(columns)
    with cursor.copy(f"COPY {table_name} ({quoted_columns}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')") as copy:
        copy.write(csv_data)
