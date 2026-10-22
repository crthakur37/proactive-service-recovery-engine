"""Scenario simulation for comparing reactive and proactive recovery.

Intervention effects are explicit assumptions, not causal estimates.
"""

from __future__ import annotations

import pandas as pd


def simulate_policies(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {
        "churn_propensity",
        "estimated_clv",
        "support_attempts",
        "assumed_churn_reduction",
        "recovery_cost",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing simulation columns: {', '.join(sorted(missing))}")
    if df[list(required)].isna().any().any():
        raise ValueError("Simulation inputs must not contain missing values")

    out = df.copy()

    # Baseline/reactive assumption: a smaller share of at-risk customers receives
    # effective recovery, at a relatively uniform cost after escalation.
    baseline_cost = 50.0
    baseline_reduction = 0.04

    baseline_intervened = (out["support_attempts"] > 0).astype(int)
    out["estimated_value_at_risk"] = (
        out["churn_propensity"] * out["estimated_clv"]
    )
    out["baseline_expected_churn_avoided"] = (
        baseline_intervened * out["churn_propensity"] * baseline_reduction
    )
    out["baseline_value_preserved"] = (
        out["baseline_expected_churn_avoided"] * out["estimated_clv"]
    )
    out["baseline_recovery_cost"] = baseline_intervened * baseline_cost
    out["baseline_net_retention_value"] = (
        out["baseline_value_preserved"] - out["baseline_recovery_cost"]
    )

    out["proactive_expected_churn_avoided"] = (
        out["churn_propensity"]
        * out["assumed_churn_reduction"]
    )
    out["proactive_value_preserved"] = (
        out["proactive_expected_churn_avoided"] * out["estimated_clv"]
    )
    out["proactive_net_retention_value"] = (
        out["proactive_value_preserved"] - out["recovery_cost"]
    )

    baseline_churn_avoided = out["baseline_expected_churn_avoided"].sum()
    proactive_churn_avoided = out["proactive_expected_churn_avoided"].sum()
    baseline_spend = out["baseline_recovery_cost"].sum()
    proactive_spend = out["recovery_cost"].sum()

    summary = pd.DataFrame(
        {
            "Policy": ["Standard / Reactive", "Risk-Aware / Proactive"],
            "Recovery Spend": [
                baseline_spend,
                proactive_spend,
            ],
            "Expected Value Preserved": [
                out["baseline_value_preserved"].sum(),
                out["proactive_value_preserved"].sum(),
            ],
            "Net Retention Value": [
                out["baseline_net_retention_value"].sum(),
                out["proactive_net_retention_value"].sum(),
            ],
            "Expected Churn Events Avoided": [
                baseline_churn_avoided,
                proactive_churn_avoided,
            ],
            "Cost per Expected Churn Avoided": [
                baseline_spend / baseline_churn_avoided
                if baseline_churn_avoided
                else float("nan"),
                proactive_spend / proactive_churn_avoided
                if proactive_churn_avoided
                else float("nan"),
            ],
        }
    )

    return out, summary
