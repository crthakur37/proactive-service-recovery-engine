"""Transparent Service Recovery Risk scoring logic for V1."""

from __future__ import annotations

import numpy as np
import pandas as pd


# Explicit scenario thresholds. A small High-risk queue is intentional, but the
# original 40/75 split classified only about 0.1% of generated orders as High.
# These cutoffs produce a more useful synthetic triage mix without changing the
# score formula or the V1 decision problem.
LOW_RISK_MAX = 35.0
MEDIUM_RISK_MAX = 55.0


_REQUIRED_COLUMNS = {
    "predicted_delay_min",
    "active_tracking_intensity",
    "support_attempts",
    "recent_service_failures",
    "complaint_history",
    "churn_propensity",
    "estimated_clv",
}


def _minmax(series: pd.Series, low: float, high: float) -> pd.Series:
    return ((series - low) / (high - low)).clip(0, 1)


def add_service_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    missing = _REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing scoring columns: {', '.join(sorted(missing))}")
    if df[list(_REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Scoring inputs must not contain missing values")

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
        bins=[-np.inf, LOW_RISK_MAX, MEDIUM_RISK_MAX, np.inf],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    return out
