"""Recovery policy for V1.

Customer value affects recovery intensity, not physical delivery priority.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.scoring import LOW_RISK_MAX, MEDIUM_RISK_MAX


def apply_recovery_policy(df: pd.DataFrame) -> pd.DataFrame:
    required = {"service_recovery_risk_score", "predicted_delay_min"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing policy columns: {', '.join(sorted(missing))}")
    if df[list(required)].isna().any().any():
        raise ValueError("Policy inputs must not contain missing values")

    out = df.copy()
    score = out["service_recovery_risk_score"]
    delay = out["predicted_delay_min"]
    is_low = score <= LOW_RISK_MAX
    is_medium = (score > LOW_RISK_MAX) & (score <= MEDIUM_RISK_MAX)

    out["support_route"] = np.select(
        [is_low, is_medium],
        ["Automated support", "Proactive automated outreach"],
        default="Priority human escalation",
    )
    out["recovery_action"] = np.select(
        [is_low, is_medium],
        ["Standard flow", "Apology + fee waiver / nominal credit"],
        default="Priority support + higher compensation review",
    )
    out["recovery_cost"] = np.select(
        [is_low, is_medium],
        [0.0, np.where(delay < 20, 30.0, 50.0)],
        default=np.where(delay < 25, 100.0, 150.0),
    ).astype(float)
    out["assumed_churn_reduction"] = np.select(
        [is_low, is_medium], [0.0, 0.08], default=0.18
    ).astype(float)

    return out
