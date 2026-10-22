"""Recovery policy for V1.

Customer value affects recovery intensity, not physical delivery priority.
"""

from __future__ import annotations

import pandas as pd


def apply_recovery_policy(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    def decide(row):
        score = row["service_recovery_risk_score"]
        delay = row["predicted_delay_min"]

        if score <= 40:
            return pd.Series(
                ["Automated support", "Standard flow", 0.0, 0.00],
                index=["support_route", "recovery_action", "recovery_cost", "assumed_churn_reduction"],
            )

        if score <= 75:
            cost = 30.0 if delay < 20 else 50.0
            return pd.Series(
                [
                    "Proactive automated outreach",
                    "Apology + fee waiver / nominal credit",
                    cost,
                    0.08,
                ],
                index=["support_route", "recovery_action", "recovery_cost", "assumed_churn_reduction"],
            )

        cost = 100.0 if delay < 25 else 150.0
        return pd.Series(
            [
                "Priority human escalation",
                "Priority support + higher compensation review",
                cost,
                0.18,
            ],
            index=["support_route", "recovery_action", "recovery_cost", "assumed_churn_reduction"],
        )

    policy = out.apply(decide, axis=1)
    return pd.concat([out, policy], axis=1)
