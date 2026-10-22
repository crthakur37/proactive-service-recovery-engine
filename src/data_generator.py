"""Synthetic data generation for V1.

The data is deliberately transparent and scenario-driven. It is not intended to
reproduce any food-delivery platform's proprietary distributions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def generate_orders(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("n must be a positive integer")

    rng = np.random.default_rng(seed)

    order_id = np.arange(1, n + 1)
    scheduled_order = rng.binomial(1, 0.18, n)

    order_value = np.clip(rng.lognormal(mean=np.log(420), sigma=0.45, size=n), 120, 2500)
    avg_order_value = np.clip(order_value * rng.normal(0.95, 0.20, n), 120, 2200)
    tenure_months = np.clip(rng.gamma(shape=2.2, scale=8.0, size=n), 1, 60)
    monthly_order_frequency = np.clip(rng.gamma(shape=2.0, scale=2.2, size=n), 0.5, 18)

    recent_service_failures = np.clip(rng.poisson(0.7, n), 0, 4)
    complaint_history = np.clip(
        rng.poisson(0.35 + 0.25 * recent_service_failures, n), 0, 5
    )

    # This is assumed to be produced by an existing logistics backend.
    predicted_delay_min = np.clip(
        rng.gamma(shape=2.0, scale=6.5, size=n)
        + scheduled_order * rng.normal(1.5, 1.0, n),
        0,
        45,
    )

    # ATI is designed to be correlated with delay and prior failures, but with
    # substantial noise to preserve benign alternative explanations.
    ati_lambda = np.clip(
        0.7
        + 0.10 * predicted_delay_min
        + 0.35 * recent_service_failures
        + rng.normal(0, 0.6, n),
        0.1,
        8,
    )
    active_tracking_intensity = np.clip(rng.poisson(ati_lambda), 0, 15)

    support_prob = _sigmoid(
        -3.0
        + 0.10 * predicted_delay_min
        + 0.12 * active_tracking_intensity
        + 0.25 * recent_service_failures
    )
    contacted_support = rng.binomial(1, support_prob)
    support_attempts = contacted_support * np.clip(
        1 + rng.poisson(0.45 + 0.04 * predicted_delay_min, n), 1, 5
    )
    minutes_since_first_support = np.where(
        support_attempts > 0,
        np.clip(rng.normal(7 + 1.8 * support_attempts, 4, n), 1, 35),
        0,
    )

    # Transparent CLV proxy. Contribution margin and remaining horizon are assumptions.
    contribution_margin = 0.11
    remaining_horizon_months = np.clip(18 + 0.15 * tenure_months, 18, 30)
    estimated_clv = (
        monthly_order_frequency
        * avg_order_value
        * contribution_margin
        * remaining_horizon_months
    )

    churn_logit = (
        -2.1
        + 0.025 * predicted_delay_min
        + 0.22 * recent_service_failures
        + 0.18 * complaint_history
        + 0.06 * active_tracking_intensity
        - 0.012 * tenure_months
    )
    churn_propensity = np.clip(_sigmoid(churn_logit), 0.02, 0.95)

    return pd.DataFrame(
        {
            "order_id": order_id,
            "predicted_delay_min": predicted_delay_min.round(1),
            "order_value": order_value.round(0),
            "scheduled_order": scheduled_order,
            "active_tracking_intensity": active_tracking_intensity,
            "support_attempts": support_attempts,
            "minutes_since_first_support": minutes_since_first_support.round(1),
            "tenure_months": tenure_months.round(1),
            "monthly_order_frequency": monthly_order_frequency.round(1),
            "avg_order_value": avg_order_value.round(0),
            "recent_service_failures": recent_service_failures,
            "complaint_history": complaint_history,
            "estimated_clv": estimated_clv.round(0),
            "churn_propensity": churn_propensity.round(3),
        }
    )
