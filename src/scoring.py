"""Transparent Service Recovery Risk scoring logic for V1."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _minmax(series: pd.Series, low: float, high: float) -> pd.Series:
    return ((series - low) / (high - low)).clip(0, 1)


def add_service_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    clv_rank = out["estimated_clv"].rank(pct=True)

    # Weights are explicit V1 assumptions chosen for interpretability.
    score = (
        0.28 * _minmax(out["predicted_delay_min"], 0, 30)
        + 0.14 * _minmax(out["active_tracking_intensity"], 0, 10)
        + 0.12 * _minmax(out["support_attempts"], 0, 4)
        + 0.10 * _minmax(out["recent_service_failures"], 0, 3)
        + 0.08 * _minmax(out["complaint_history"], 0, 3)
        + 0.18 * out["churn_propensity"].clip(0, 1)
        + 0.10 * clv_rank
    )

    out["service_recovery_risk_score"] = (100 * score).clip(0, 100).round(1)

    out["risk_band"] = pd.cut(
        out["service_recovery_risk_score"],
        bins=[-1, 40, 75, 101],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    return out
