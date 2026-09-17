import pandas as pd
import pytest

from ai_operations_copilot.analytics import forecast_store_sales
from ai_operations_copilot.copilot import build_insight
from ai_operations_copilot.etl import DataQualityError, build_sales_daily
from ai_operations_copilot.synthetic_data import DatasetConfig, generate_dataset


def test_synthetic_data_is_reproducible() -> None:
    config = DatasetConfig(seed=11, days=14, store_count=2, product_count=4, customer_count=10)
    first = generate_dataset(config)
    second = generate_dataset(config)

    for table_name in first:
        pd.testing.assert_frame_equal(first[table_name], second[table_name])


def test_quality_check_rejects_unknown_store() -> None:
    dataset = generate_dataset(DatasetConfig(seed=11, days=14, store_count=2, product_count=4, customer_count=10))
    dataset["sales"].loc[0, "store_id"] = "UNKNOWN"

    with pytest.raises(DataQualityError, match="unknown references"):
        build_sales_daily(dataset)


def test_forecast_returns_both_models_and_measured_metrics() -> None:
    dataset = generate_dataset(DatasetConfig(seed=11, days=30, store_count=2, product_count=4, customer_count=10))
    sales_daily = build_sales_daily(dataset)

    forecast = forecast_store_sales(sales_daily, "S001", horizon=7)

    assert set(forecast["model_name"]) == {"baseline_7_day_mean", "random_forest_lag_features"}
    assert forecast["mae"].notna().all()
    assert forecast["rmse"].notna().all()


def test_copilot_separates_evidence_from_possible_factors() -> None:
    insight = build_insight(
        {
            "entity_id": "S001",
            "anomaly_type": "sales_drop",
            "evidence": {"sales_change": -0.2, "customer_count": 12},
        },
        {"stock_on_hand": 2, "reorder_point": 10, "stockout_risk": True},
    )

    assert insight["evidence"]["sales_change"] == -0.2
    assert insight["risk"] == "high"
    assert "原因を一つに断定" in insight["possible_factors"][1]
