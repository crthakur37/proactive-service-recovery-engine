# V1 Product & Data Specification

## 1. Decision Problem

V1 assumes that an existing logistics backend already supplies **Predicted Delay Severity**. The prototype does not attempt to predict ETA or optimize routing.

The decision engine answers:

1. Should the platform intervene proactively?
2. Should the customer stay in automated support or receive priority human escalation?
3. What level of service recovery is proportionate?

## 2. Unit of Analysis

One row represents one active food-delivery order with customer context available at the point of likely or actual SLA breach.

## 3. Synthetic Feature Schema

| Feature | Type | Meaning | V1 Assumption |
|---|---|---|---|
| order_id | ID | Synthetic order identifier | Generated sequentially |
| predicted_delay_min | Numeric | Expected minutes beyond promised SLA | Supplied by existing logistics backend |
| order_value | Numeric | Current order value in INR | Synthetic right-skewed distribution |
| scheduled_order | Binary | Scheduled vs on-demand order | Synthetic |
| active_tracking_intensity | Numeric | ETA/status checks in recent window | Neutral attention signal; not an emotion score |
| support_attempts | Integer | Support contacts during current order | Synthetic behavioral signal |
| minutes_since_first_support | Numeric | Time since first support attempt | 0 if no support contact |
| tenure_months | Numeric | Customer tenure on platform | Synthetic |
| monthly_order_frequency | Numeric | Typical orders/month | Synthetic |
| avg_order_value | Numeric | Historical AOV | Synthetic |
| recent_service_failures | Integer | SLA/service failures in recent orders | Synthetic |
| complaint_history | Integer | Prior complaints in recent history | Synthetic |
| estimated_clv | Numeric | Formula-based expected future contribution value | Not a trained CLV model |
| churn_propensity | Numeric | Synthetic probability-like customer attrition score | Scenario input, not a validated production churn model |

## 4. Important Feature Interpretation

### Active Tracking Intensity (ATI)

ATI measures **monitoring intensity**, not anger, anxiety, or dissatisfaction.

High ATI may occur because of urgency, coordination, habit, or location guidance. In V1 it is treated as a plausible but unvalidated signal that may add information when combined with delay severity and other context.

## 5. Estimated CLV

V1 deliberately uses a transparent formula rather than a complex model.

Conceptually:

Estimated CLV = Monthly Order Frequency × Historical AOV × Assumed Contribution Margin × Remaining Relationship Horizon

The exact margin and horizon are explicit simulation assumptions.

## 6. Service Recovery Risk Score

V1 uses a transparent weighted score rather than a black-box model.

Core factors:
- Delay severity
- Active Tracking Intensity
- Support attempts
- Recent service failures
- Complaint history
- Churn propensity
- Customer value percentile

The score is scaled to 0–100.

This is a **decision-prioritization score**, not a psychological score and not a causal model.

## 7. Recovery Policy

### Low Risk
- Standard automated flow
- No proactive monetary compensation

### Medium Risk
- Proactive apology / ETA communication
- Nominal recovery credit or fee waiver

### High Risk
- Priority human-support escalation
- Higher recovery budget / refund review

Baseline delivery operations remain identical across customer-value segments.

## 8. Simulation

The app compares:

### Policy A — Standard / Reactive
Recovery begins after escalation and uses a relatively uniform response.

### Policy B — Risk-Aware / Proactive
Recovery resources are allocated based on the Service Recovery Risk Score.

The simulation uses explicit scenario assumptions for:
- intervention cost,
- probability of preventing churn,
- value preserved.

These are **not claimed as causal estimates**.

## 9. Primary Business Metric

### Net Retention Value

Expected customer value preserved minus service-recovery cost.

Secondary metrics:
- recovery spend,
- customers proactively handled,
- human escalations,
- expected churn events avoided,
- recovery cost per expected churn avoided.

## 10. V1 Limitations

- Synthetic data only
- No proprietary Swiggy/Zomato logic
- No validated causal effect of ATI on escalation/churn
- No production churn or CLV model
- No real intervention-effectiveness estimates
- No routing / batching / dispatch optimization
- No live system integration
