"""Scenario simulation for comparing reactive and proactive recovery.

Intervention effects are explicit assumptions, not causal estimates.
"""

from __future__ import annotations

import pandas as pd


def simulate_policies(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()

    # Baseline/reactive assumption: a smaller share of at-risk customers receives
    # effective recovery, at a relatively uniform cost after escalation.
    baseline_cost = 50.0
    baseline_reduction = 0.04

    out["baseline_expected_churn_loss"] = out["churn_propensity"] * out["estimated_clv"]
    out["baseline_value_preserved"] = (
        out["churn_propensity"] * baseline_reduction * out["estimated_clv"]
    )
    out["baseline_recovery_cost"] = (
        (out["support_attempts"] > 0).astype(int) * baseline_cost
    )
    out["baseline_net_retention_value"] = (
        out["baseline_value_preserved"] - out["baseline_recovery_cost"]
    )

    out["proactive_value_preserved"] = (
        out["churn_propensity"]
        * out["assumed_churn_reduction"]
        * out["estimated_clv"]
    )
    out["proactive_net_retention_value"] = (
        out["proactive_value_preserved"] - out["recovery_cost"]
    )

    summary = pd.DataFrame(
        {
            "Policy": ["Standard / Reactive", "Risk-Aware / Proactive"],
            "Recovery Spend": [
                out["baseline_recovery_cost"].sum(),
                out["recovery_cost"].sum(),
            ],
            "Expected Value Preserved": [
                out["baseline_value_preserved"].sum(),
                out["proactive_value_preserved"].sum(),
            ],
            "Net Retention Value": [
                out["baseline_net_retention_value"].sum(),
                out["proactive_net_retention_value"].sum(),
            ],
        }
    )

    return out, summary
