"""Generate reproducible business data for the AI Operations Copilot MVP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DatasetConfig:
    """Controls the size and time range of a generated dataset."""

    seed: int = 42
    start_date: date = date(2025, 1, 1)
    days: int = 90
    store_count: int = 8
    product_count: int = 40
    customer_count: int = 300


def generate_dataset(config: DatasetConfig | None = None) -> dict[str, pd.DataFrame]:
    """Generate all MVP entities using one deterministic random generator."""
    config = config or DatasetConfig()
    if config.days < 14:
        raise ValueError("days must be at least 14 to support trend features")
    if min(config.store_count, config.product_count, config.customer_count) < 1:
        raise ValueError("entity counts must be positive")

    rng = np.random.default_rng(config.seed)
    stores = _generate_stores(config)
    products = _generate_products(config, rng)
    customers = _generate_customers(config, rng)
    sales = _generate_sales(config, rng, stores, products, customers)
    inventory = _generate_inventory(config, rng, stores, products, sales)

    return {
        "stores": stores,
        "products": products,
        "customers": customers,
        "sales": sales,
        "inventory": inventory,
    }


def _generate_stores(config: DatasetConfig) -> pd.DataFrame:
    regions = ["Kanto", "Kansai", "Chubu", "Kyushu"]
    store_types = ["urban", "suburban", "mall"]
    return pd.DataFrame(
        {
            "store_id": [f"S{i:03d}" for i in range(1, config.store_count + 1)],
            "store_name": [f"Store {chr(64 + i)}" for i in range(1, config.store_count + 1)],
            "region": [regions[(i - 1) % len(regions)] for i in range(1, config.store_count + 1)],
            "store_type": [store_types[(i - 1) % len(store_types)] for i in range(1, config.store_count + 1)],
            "opened_date": pd.to_datetime("2020-01-01").date(),
        }
    )


def _generate_products(config: DatasetConfig, rng: np.random.Generator) -> pd.DataFrame:
    categories = np.array(["Beverage", "Food", "Household", "Personal Care"])
    unit_cost = rng.uniform(200, 3000, config.product_count).round(2)
    markup = rng.uniform(1.2, 1.8, config.product_count)
    return pd.DataFrame(
        {
            "product_id": [f"P{i:04d}" for i in range(1, config.product_count + 1)],
            "product_name": [f"Product {i:04d}" for i in range(1, config.product_count + 1)],
            "category": rng.choice(categories, config.product_count),
            "unit_cost": unit_cost,
            "unit_price": (unit_cost * markup).round(2),
        }
    )


def _generate_customers(config: DatasetConfig, rng: np.random.Generator) -> pd.DataFrame:
    segments = np.array(["new", "regular", "high_value"])
    regions = np.array(["Kanto", "Kansai", "Chubu", "Kyushu"])
    signup_offsets = rng.integers(0, 365, config.customer_count)
    return pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(1, config.customer_count + 1)],
            "segment": rng.choice(segments, config.customer_count, p=[0.3, 0.55, 0.15]),
            "region": rng.choice(regions, config.customer_count),
            "signup_date": pd.Timestamp(config.start_date) - pd.to_timedelta(signup_offsets, unit="D"),
        }
    )


def _generate_sales(
    config: DatasetConfig,
    rng: np.random.Generator,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    dates = pd.date_range(config.start_date, periods=config.days, freq="D")
    rows: list[dict[str, object]] = []
    sale_id = 1
    product_lookup = products.set_index("product_id")

    for current_date in dates:
        seasonal_factor = 1 + 0.12 * np.sin(2 * np.pi * current_date.dayofyear / 365)
        weekday_factor = 1.15 if current_date.dayofweek >= 5 else 1.0
        for store_index, store_id in enumerate(stores["store_id"]):
            store_factor = 0.85 + store_index * 0.05
            active_products = products.loc[rng.random(len(products)) < 0.38, "product_id"]
            for product_id in active_products:
                quantity = max(1, int(rng.poisson(2.2 * seasonal_factor * weekday_factor * store_factor)))
                product = product_lookup.loc[product_id]
                customer_id = str(rng.choice(customers["customer_id"].to_numpy()))
                discount = float(rng.choice([0.0, 0.05, 0.1], p=[0.7, 0.2, 0.1]))
                rows.append(
                    {
                        "sale_id": sale_id,
                        "sale_date": current_date.date(),
                        "store_id": store_id,
                        "product_id": product_id,
                        "customer_id": customer_id,
                        "quantity": quantity,
                        "unit_price": float(product["unit_price"]),
                        "discount": discount,
                    }
                )
                sale_id += 1

    return pd.DataFrame(rows)


def _generate_inventory(
    config: DatasetConfig,
    rng: np.random.Generator,
    stores: pd.DataFrame,
    products: pd.DataFrame,
    sales: pd.DataFrame,
) -> pd.DataFrame:
    dates = pd.date_range(config.start_date, periods=config.days, freq="D")
    demand = sales.groupby(["sale_date", "store_id", "product_id"], as_index=False)["quantity"].sum()
    demand_lookup = demand.set_index(["sale_date", "store_id", "product_id"])["quantity"]
    rows: list[dict[str, object]] = []

    for current_date in dates:
        current_day = current_date.date()
        for store_id in stores["store_id"]:
            for product_id in products["product_id"]:
                key = (current_day, store_id, product_id)
                daily_demand = int(demand_lookup.get(key, 0))
                reorder_point = int(rng.integers(5, 25))
                stock_in = int(rng.integers(15, 45)) if current_date.dayofweek == 0 else 0
                stock_on_hand = max(0, int(rng.integers(10, 60)) + stock_in - daily_demand)
                rows.append(
                    {
                        "inventory_date": current_day,
                        "store_id": store_id,
                        "product_id": product_id,
                        "stock_on_hand": stock_on_hand,
                        "reorder_point": reorder_point,
                        "stock_in": stock_in,
                        "stock_out": daily_demand,
                    }
                )

    return pd.DataFrame(rows)
