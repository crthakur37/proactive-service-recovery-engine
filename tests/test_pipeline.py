"""Business-rule and edge-case tests for the V1 pipeline."""

from __future__ import annotations

import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from src.data_generator import generate_orders
from src.recovery_policy import apply_recovery_policy
from src.scoring import add_service_risk_score
from src.simulation import simulate_policies


class DataGenerationTests(unittest.TestCase):
    def test_generation_is_reproducible_and_internally_consistent(self) -> None:
        first = generate_orders(n=200, seed=7)
        second = generate_orders(n=200, seed=7)

        assert_frame_equal(first, second)
        self.assertFalse(first.isna().any().any())
        self.assertFalse(first["order_id"].duplicated().any())
        self.assertTrue(first["churn_propensity"].between(0.02, 0.95).all())
        self.assertTrue((first["estimated_clv"] > 0).all())
        no_contact = first["support_attempts"] == 0
        self.assertTrue((first.loc[no_contact, "minutes_since_first_support"] == 0).all())

    def test_generation_rejects_non_positive_or_non_integer_sizes(self) -> None:
        for invalid_n in (0, -1, 1.5, True):
            with self.subTest(n=invalid_n), self.assertRaises(ValueError):
                generate_orders(n=invalid_n)  # type: ignore[arg-type]


class ScoringAndPolicyTests(unittest.TestCase):
    def test_score_is_bounded_and_extreme_cases_reach_expected_bands(self) -> None:
        inputs = pd.DataFrame(
            {
                "predicted_delay_min": [0.0, 45.0],
                "active_tracking_intensity": [0, 15],
                "support_attempts": [0, 5],
                "recent_service_failures": [0, 4],
                "complaint_history": [0, 5],
                "churn_propensity": [0.0, 1.0],
                "estimated_clv": [100.0, 10000.0],
            }
        )

        scored = add_service_risk_score(inputs)

        self.assertTrue(scored["service_recovery_risk_score"].between(0, 100).all())
        self.assertEqual(scored["risk_band"].tolist(), ["Low", "High"])

    def test_policy_boundaries_and_delay_based_costs(self) -> None:
        inputs = pd.DataFrame(
            {
                "service_recovery_risk_score": [35.0, 35.1, 55.0, 55.1, 80.0],
                "predicted_delay_min": [30.0, 19.9, 20.0, 24.9, 25.0],
            }
        )

        result = apply_recovery_policy(inputs)

        self.assertEqual(
            result["support_route"].tolist(),
            [
                "Automated support",
                "Proactive automated outreach",
                "Proactive automated outreach",
                "Priority human escalation",
                "Priority human escalation",
            ],
        )
        self.assertEqual(result["recovery_cost"].tolist(), [0.0, 30.0, 50.0, 100.0, 150.0])
        self.assertEqual(
            result["assumed_churn_reduction"].tolist(), [0.0, 0.08, 0.08, 0.18, 0.18]
        )

    def test_default_synthetic_mix_contains_meaningful_all_three_bands(self) -> None:
        scored = add_service_risk_score(generate_orders(n=5000, seed=42))
        shares = scored["risk_band"].value_counts(normalize=True)

        self.assertGreater(shares.get("Low", 0), 0.60)
        self.assertLess(shares.get("Low", 0), 0.80)
        self.assertGreater(shares.get("Medium", 0), 0.15)
        self.assertGreater(shares.get("High", 0), 0.02)

    def test_missing_scoring_inputs_raise_a_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing scoring columns"):
            add_service_risk_score(pd.DataFrame({"estimated_clv": [100.0]}))


class SimulationTests(unittest.TestCase):
    def test_reactive_value_is_only_preserved_when_support_was_contacted(self) -> None:
        inputs = pd.DataFrame(
            {
                "churn_propensity": [0.5, 0.5],
                "estimated_clv": [1000.0, 1000.0],
                "support_attempts": [0, 1],
                "assumed_churn_reduction": [0.0, 0.08],
                "recovery_cost": [0.0, 30.0],
            }
        )

        detail, summary = simulate_policies(inputs)

        self.assertEqual(detail["baseline_value_preserved"].tolist(), [0.0, 20.0])
        self.assertEqual(detail["baseline_recovery_cost"].tolist(), [0.0, 50.0])
        self.assertEqual(detail["estimated_value_at_risk"].tolist(), [500.0, 500.0])
        self.assertAlmostEqual(
            summary.loc[0, "Net Retention Value"],
            summary.loc[0, "Expected Value Preserved"]
            - summary.loc[0, "Recovery Spend"],
        )

    def test_complete_pipeline_has_consistent_outputs(self) -> None:
        scored = add_service_risk_score(generate_orders(n=1000, seed=11))
        policy = apply_recovery_policy(scored)
        detail, summary = simulate_policies(policy)

        self.assertFalse(detail.isna().any().any())
        self.assertTrue(
            (
                detail["proactive_net_retention_value"]
                == detail["proactive_value_preserved"] - detail["recovery_cost"]
            ).all()
        )
        self.assertEqual(summary["Policy"].nunique(), 2)


if __name__ == "__main__":
    unittest.main()
