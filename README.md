# Proactive Service-Recovery Decision Engine

AI-enabled decision support for service recovery in Indian online food delivery.

## Project Objective

This project explores how a food-delivery platform can respond more intelligently when its existing logistics systems already indicate that a delivery SLA breach is likely.

Rather than attempting to rebuild ETA prediction, rider dispatch, routing, or batching, V1 focuses on **customer-experience recovery**.

The central question is:

> When a likely or actual delivery SLA breach occurs, how can delay severity, customer behavior, recent service history, churn risk, and customer value be combined to decide whether to intervene proactively, how urgently to route support, and what level of recovery is economically justified?

## Why This Problem

The project originated from a real customer experience involving:
- a scheduled food-delivery order that showed signs of likely delay,
- repeated order-status checking,
- slow chatbot-to-human escalation,
- delayed support response,
- and limited recovery options after the SLA breach.

That experience is treated only as a **problem-discovery anecdote**, not as proof of platform-wide behavior.

External research is being used separately to validate the broader business problem and to distinguish:
- established facts,
- reasonable inferences,
- and assumptions used in the prototype.

## V1 Scope

### Inputs
The first version will use synthetic data representing:

**Order / service context**
- Predicted delay severity
- Promised ETA
- Order value
- Scheduled vs. normal order

**Behavioral signals**
- Active Tracking Intensity (ATI)
- Support-contact attempts
- Time since first support contact

**Customer context**
- Tenure
- Order frequency
- Average order value
- Recent service failures
- Complaint history
- Estimated customer lifetime value
- Churn propensity

### Core Decisions

The system will answer three questions:

1. **Should the platform intervene proactively?**
2. **Should the customer remain in automated support or receive priority human escalation?**
3. **What level of recovery action is proportionate?**

### Outputs

The V1 will produce:
- Service Recovery Risk Score
- Recommended support route
- Recommended recovery action
- Estimated recovery cost
- Estimated customer value at risk
- Business-impact comparison versus a standard/reactive policy

## Recovery Actions

The V1 will use a deliberately small action set:
- Standard automated flow
- Proactive apology / ETA communication
- Fee waiver or nominal credit
- Moderate coupon / credit
- Refund or higher-compensation review
- Priority human-support escalation

Customer value affects the **intensity of recovery resources**, not baseline delivery priority.

## Key Experimental Feature

### Active Tracking Intensity (ATI)

ATI measures how actively a customer monitors an ongoing order, for example through ETA/status checks in a recent time window.

It is treated as a neutral behavioral signal of **attention / monitoring intensity**.

It must **not** be interpreted directly as anger, anxiety, or dissatisfaction.

In V1, ATI is a testable hypothesis feature rather than an established causal predictor of escalation.

## V1 Architecture

```text
Existing Logistics Backend
        ↓
Predicted Delay Severity
        +
Customer History
        +
Active Tracking Intensity
        +
Support Attempts
        +
Churn Propensity / CLV
        ↓
Service Recovery Risk Score
        ↓
Policy Engine
        ↓
Automated Response / Proactive Recovery / Priority Human Escalation
        ↓
Recovery Cost + Expected Retention Value
```

## Business Metric

Primary metric:

**Net Retention Value**

Conceptually:

```text
Expected Customer Value Preserved - Recovery Cost
```

Secondary metrics may include:
- Total recovery spend
- High-risk customers proactively handled
- Human-support escalations
- Expected churn reduction
- Recovery cost per protected customer

## V1 Comparison

The simulation will compare:
- **Policy A:** Standard / reactive recovery
- **Policy B:** Risk-aware proactive recovery

A flat-compensation policy may also be added as a benchmark if time permits.

## Explicit V1 Exclusions

The first version will **not** attempt to build:
- ETA prediction
- Rider routing
- Dispatch optimization
- Batching optimization
- Restaurant preparation-time prediction
- Sophisticated CLV modeling
- Causal intervention modeling
- RAG
- Multi-agent systems
- Live Swiggy / Zomato integrations
- Production-grade platform infrastructure

## Data

The project uses **synthetic data only**.

Synthetic assumptions will be documented explicitly. The prototype does not claim to reproduce Swiggy's, Zomato's, or any other company's internal models, policies, or customer behavior.

## Planned Tech Stack

- Python
- pandas
- scikit-learn
- Streamlit
- Plotly / Matplotlib
- Git / GitHub

Additional libraries will be added only if the V1 genuinely requires them.

## Repository Structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── data/
├── assets/
└── src/
    ├── __init__.py
    ├── data_generator.py
    ├── scoring.py
    ├── recovery_policy.py
    └── simulation.py
```

## Current Status

**V1 scope frozen. Implementation starting.**

## Next Steps

1. Define synthetic-data schema and assumptions
2. Generate synthetic customer/order records
3. Build service-risk scoring logic
4. Define recovery-policy rules
5. Simulate standard vs. proactive recovery
6. Build Streamlit dashboard
7. Test edge cases
8. Deploy V1
9. Add screenshots, architecture visual, results, and verified references

## Disclaimer

This is an independent MBA portfolio project inspired by the Indian online food-delivery sector. It is not affiliated with, endorsed by, or based on proprietary data from Swiggy, Zomato, or any other platform.
