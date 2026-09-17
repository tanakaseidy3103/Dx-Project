"""Create evidence-first insight payloads for a local LLM or template renderer."""

from __future__ import annotations

from collections.abc import Mapping


def build_insight(
    anomaly: Mapping[str, object],
    inventory: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build an AI-safe payload without claiming an unverified causal explanation."""
    entity_id = str(anomaly["entity_id"])
    anomaly_type = str(anomaly["anomaly_type"])
    evidence = dict(anomaly["evidence"])
    possible_factors = [
        "キャンペーン、曜日、季節性、商品構成などの追加データを確認する必要があります。",
        "現在のデータだけでは、原因を一つに断定できません。",
    ]
    risk = "high" if anomaly_type == "sales_drop" else "medium"
    action = f"{entity_id}の対象期間を確認し、売上・顧客数・在庫を前期間と比較する。"

    if inventory is not None:
        inventory_evidence = {
            "stock_on_hand": int(inventory["stock_on_hand"]),
            "reorder_point": int(inventory["reorder_point"]),
            "stockout_risk": bool(inventory["stockout_risk"]),
        }
        evidence["inventory"] = inventory_evidence
        if inventory_evidence["stockout_risk"]:
            risk = "high"
            action = f"{entity_id}の在庫と補充状況を優先確認し、欠品リスクの商品を担当者が判断する。"

    return {
        "current_situation": f"{entity_id}で{anomaly_type}が検知されました。",
        "evidence": evidence,
        "possible_factors": possible_factors,
        "risk": risk,
        "recommended_action": action,
        "generation_method": "evidence_first_template",
    }
