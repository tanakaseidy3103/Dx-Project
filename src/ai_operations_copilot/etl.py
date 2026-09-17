"""Data quality checks and analysis-ready transformations."""

from __future__ import annotations

from typing import Mapping

import pandas as pd


class DataQualityError(ValueError):
    """Raised when generated or imported data violates the MVP contract."""


REQUIRED_TABLES = {"stores", "products", "customers", "sales", "inventory"}


def validate_dataset(dataset: Mapping[str, pd.DataFrame]) -> None:
    """Validate required entities, keys, foreign keys, and numeric ranges."""
    missing_tables = REQUIRED_TABLES.difference(dataset)
    if missing_tables:
        raise DataQualityError(f"missing tables: {sorted(missing_tables)}")

    for table_name in REQUIRED_TABLES:
        if dataset[table_name].empty:
            raise DataQualityError(f"table is empty: {table_name}")

    _require_unique(dataset["stores"], "store_id", "stores")
    _require_unique(dataset["products"], "product_id", "products")
    _require_unique(dataset["customers"], "customer_id", "customers")
    _require_unique(dataset["sales"], "sale_id", "sales")
    _require_unique(dataset["inventory"], ["inventory_date", "store_id", "product_id"], "inventory")

    _require_references(dataset["sales"], "store_id", dataset["stores"], "store_id", "sales.store_id")
    _require_references(dataset["sales"], "product_id", dataset["products"], "product_id", "sales.product_id")
    _require_references(dataset["sales"], "customer_id", dataset["customers"], "customer_id", "sales.customer_id")
    _require_references(dataset["inventory"], "store_id", dataset["stores"], "store_id", "inventory.store_id")
    _require_references(dataset["inventory"], "product_id", dataset["products"], "product_id", "inventory.product_id")

    for table_name, column in (("sales", "quantity"), ("inventory", "stock_on_hand"), ("inventory", "reorder_point")):
        if (dataset[table_name][column] < 0).any():
            raise DataQualityError(f"negative values found: {table_name}.{column}")


def build_sales_daily(dataset: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Create daily store/product metrics used by Power BI and ML."""
    validate_dataset(dataset)
    sales = dataset["sales"].copy()
    unit_cost = dataset["products"].set_index("product_id")["unit_cost"]
    sales["unit_cost"] = sales["product_id"].map(unit_cost)
    sales["gross_profit"] = (
        sales["quantity"] * (sales["unit_price"] * (1 - sales["discount"]) - sales["unit_cost"])
    ).round(2)
    sales["sales_amount"] = (sales["quantity"] * sales["unit_price"] * (1 - sales["discount"])).round(2)

    daily = (
        sales.groupby(["sale_date", "store_id", "product_id"], as_index=False)
        .agg(
            sales_amount=("sales_amount", "sum"),
            gross_profit=("gross_profit", "sum"),
            customer_count=("customer_id", "nunique"),
            quantity=("quantity", "sum"),
        )
        .rename(columns={"sale_date": "sales_date"})
    )
    return daily.sort_values(["sales_date", "store_id", "product_id"]).reset_index(drop=True)


def build_inventory_features(dataset: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Add transparent inventory risk flags for reporting."""
    validate_dataset(dataset)
    inventory = dataset["inventory"].copy()
    inventory["stockout_risk"] = inventory["stock_on_hand"] <= inventory["reorder_point"]
    inventory["stockout_risk_level"] = inventory["stockout_risk"].map({True: "high", False: "normal"})
    return inventory


def _require_unique(frame: pd.DataFrame, columns: str | list[str], table_name: str) -> None:
    if frame.duplicated(columns).any():
        raise DataQualityError(f"duplicate key found: {table_name}.{columns}")


def _require_references(
    child: pd.DataFrame,
    child_column: str,
    parent: pd.DataFrame,
    parent_column: str,
    label: str,
) -> None:
    missing = set(child[child_column].dropna()) - set(parent[parent_column].dropna())
    if missing:
        raise DataQualityError(f"unknown references in {label}: {sorted(missing)[:5]}")
