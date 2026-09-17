"""Business metrics, anomaly detection, and sales forecasting."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_kpis(sales_daily: pd.DataFrame, inventory: pd.DataFrame) -> dict[str, float | int]:
    """Calculate executive KPIs from analysis-ready tables."""
    total_sales = float(sales_daily["sales_amount"].sum())
    gross_profit = float(sales_daily["gross_profit"].sum())
    customer_count = int(sales_daily["customer_count"].sum())
    inventory_units = int(inventory["stock_on_hand"].sum())
    return {
        "total_sales": round(total_sales, 2),
        "gross_profit": round(gross_profit, 2),
        "customers": customer_count,
        "inventory_units": inventory_units,
        "alert_count": 0,
    }


def detect_store_anomalies(
    sales_daily: pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
) -> pd.DataFrame:
    """Detect unusual store-day behavior and attach inspectable evidence."""
    store_daily = (
        sales_daily.groupby(["sales_date", "store_id"], as_index=False)
        .agg(
            sales_amount=("sales_amount", "sum"),
            quantity=("quantity", "sum"),
            customer_count=("customer_count", "sum"),
        )
        .sort_values(["store_id", "sales_date"])
    )
    store_daily["sales_change"] = store_daily.groupby("store_id")["sales_amount"].pct_change().replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0)
    features = store_daily[["sales_amount", "quantity", "customer_count", "sales_change"]].fillna(0)
    model = IsolationForest(contamination=contamination, random_state=random_state)
    store_daily["model_label"] = model.fit_predict(features)
    store_daily["anomaly_score"] = -model.score_samples(features)
    anomalies = store_daily[store_daily["model_label"] == -1].copy()
    anomalies["anomaly_type"] = np.where(anomalies["sales_change"] < 0, "sales_drop", "sales_spike")
    anomalies["entity_type"] = "store"
    anomalies["detection_method"] = "isolation_forest"
    anomalies["evidence"] = anomalies.apply(
        lambda row: {
            "sales_amount": round(float(row["sales_amount"]), 2),
            "sales_change": round(float(row["sales_change"]), 4),
            "quantity": int(row["quantity"]),
            "customer_count": int(row["customer_count"]),
        },
        axis=1,
    )
    return anomalies[
        ["sales_date", "entity_type", "store_id", "anomaly_type", "anomaly_score", "evidence", "detection_method"]
    ].rename(columns={"store_id": "entity_id"})


def forecast_store_sales(
    sales_daily: pd.DataFrame,
    store_id: str,
    horizon: int = 7,
    random_state: int = 42,
) -> pd.DataFrame:
    """Compare a trailing-average baseline with a lag-based Random Forest."""
    if horizon < 1:
        raise ValueError("horizon must be positive")
    history = (
        sales_daily[sales_daily["store_id"] == store_id]
        .groupby("sales_date", as_index=False)["sales_amount"]
        .sum()
        .sort_values("sales_date")
    )
    if len(history) <= horizon + 7:
        raise ValueError("not enough history for the requested forecast horizon")

    history["sales_date"] = pd.to_datetime(history["sales_date"])
    history["lag_1"] = history["sales_amount"].shift(1)
    history["lag_7"] = history["sales_amount"].shift(7)
    history["day_of_week"] = history["sales_date"].dt.dayofweek
    history = history.dropna().reset_index(drop=True)
    train = history.iloc[:-horizon]
    test = history.iloc[-horizon:]
    feature_columns = ["lag_1", "lag_7", "day_of_week"]
    model = RandomForestRegressor(n_estimators=100, random_state=random_state, min_samples_leaf=2)
    model.fit(train[feature_columns], train["sales_amount"])
    ml_predictions = model.predict(test[feature_columns])
    baseline_value = float(train["sales_amount"].tail(7).mean())
    baseline_predictions = np.repeat(baseline_value, len(test))

    rows: list[dict[str, object]] = []
    for index, (_, row) in enumerate(test.iterrows()):
        rows.extend(
            [
                {
                    "forecast_date": row["sales_date"].date(),
                    "store_id": store_id,
                    "model_name": "baseline_7_day_mean",
                    "predicted_sales": round(float(baseline_predictions[index]), 2),
                    "actual_sales": round(float(row["sales_amount"]), 2),
                    "mae": None,
                    "rmse": None,
                },
                {
                    "forecast_date": row["sales_date"].date(),
                    "store_id": store_id,
                    "model_name": "random_forest_lag_features",
                    "predicted_sales": round(float(max(0, ml_predictions[index])), 2),
                    "actual_sales": round(float(row["sales_amount"]), 2),
                    "mae": None,
                    "rmse": None,
                },
            ]
        )

    results = pd.DataFrame(rows)
    metrics = {
        "baseline_7_day_mean": (
            mean_absolute_error(test["sales_amount"], baseline_predictions),
            mean_squared_error(test["sales_amount"], baseline_predictions) ** 0.5,
        ),
        "random_forest_lag_features": (
            mean_absolute_error(test["sales_amount"], ml_predictions),
            mean_squared_error(test["sales_amount"], ml_predictions) ** 0.5,
        ),
    }
    results["mae"] = results["model_name"].map({name: values[0] for name, values in metrics.items()})
    results["rmse"] = results["model_name"].map({name: values[1] for name, values in metrics.items()})
    return results
