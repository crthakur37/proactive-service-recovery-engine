"""Streamlit app for the Proactive Service-Recovery Decision Engine."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_generator import generate_orders
from src.recovery_policy import apply_recovery_policy
from src.scoring import add_service_risk_score
from src.simulation import simulate_policies


st.set_page_config(
    page_title="Proactive Service-Recovery Engine",
    page_icon="🍽️",
    layout="wide",
)

st.title("Proactive Service-Recovery Decision Engine")
st.caption(
    "Synthetic-data MVP for risk-aware customer recovery in Indian food delivery"
)

st.warning(
    "Portfolio prototype only. All order/customer data and intervention effects are synthetic "
    "assumptions; this app does not represent Swiggy, Zomato, or any platform's internal logic."
)

with st.sidebar:
    st.header("Scenario Controls")
    n_orders = st.slider("Synthetic orders", 500, 10000, 3000, 500)
    seed = st.number_input("Random seed", min_value=1, max_value=9999, value=42)

df = generate_orders(n=n_orders, seed=int(seed))
df = add_service_risk_score(df)
df = apply_recovery_policy(df)
detail, summary = simulate_policies(df)

st.subheader("1. Executive View")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Orders evaluated", f"{len(detail):,}")
c2.metric(
    "Medium / High recovery risk",
    f"{(detail['risk_band'].isin(['Medium', 'High'])).sum():,}",
)
c3.metric(
    "Priority human escalations",
    f"{(detail['support_route'] == 'Priority human escalation').sum():,}",
)
c4.metric(
    "Proactive recovery spend",
    f"₹{detail['recovery_cost'].sum():,.0f}",
)

left, right = st.columns(2)

with left:
    risk_counts = (
        detail["risk_band"]
        .value_counts()
        .reindex(["Low", "Medium", "High"], fill_value=0)
        .reset_index()
    )
    risk_counts.columns = ["Risk Band", "Orders"]
    fig_risk = px.bar(
        risk_counts,
        x="Risk Band",
        y="Orders",
        title="Service Recovery Risk Distribution",
    )
    st.plotly_chart(fig_risk, use_container_width=True)

with right:
    policy_view = summary.melt(
        id_vars="Policy",
        value_vars=["Recovery Spend", "Expected Value Preserved", "Net Retention Value"],
        var_name="Metric",
        value_name="Value",
    )
    fig_policy = px.bar(
        policy_view,
        x="Metric",
        y="Value",
        color="Policy",
        barmode="group",
        title="Illustrative Policy Economics",
    )
    st.plotly_chart(fig_policy, use_container_width=True)

st.subheader("2. Inspect an Order")

selected_order = st.selectbox(
    "Select synthetic order ID",
    options=detail["order_id"].tolist(),
)

row = detail.loc[detail["order_id"] == selected_order].iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Predicted delay", f"{row['predicted_delay_min']:.1f} min")
m2.metric("Active Tracking Intensity", int(row["active_tracking_intensity"]))
m3.metric("Churn propensity", f"{row['churn_propensity']:.1%}")
m4.metric("Estimated CLV", f"₹{row['estimated_clv']:,.0f}")

st.progress(min(int(row["service_recovery_risk_score"]), 100))
st.write(
    f"**Service Recovery Risk Score:** {row['service_recovery_risk_score']:.1f}/100 "
    f"({row['risk_band']})"
)
st.write(f"**Recommended support route:** {row['support_route']}")
st.write(f"**Recommended recovery action:** {row['recovery_action']}")
st.write(f"**Illustrative recovery cost:** ₹{row['recovery_cost']:,.0f}")

with st.expander("Why was this order prioritized this way?"):
    explain_df = pd.DataFrame(
        {
            "Signal": [
                "Predicted delay",
                "Active Tracking Intensity",
                "Support attempts",
                "Recent service failures",
                "Complaint history",
                "Churn propensity",
                "Estimated CLV",
            ],
            "Value": [
                row["predicted_delay_min"],
                row["active_tracking_intensity"],
                row["support_attempts"],
                row["recent_service_failures"],
                row["complaint_history"],
                row["churn_propensity"],
                row["estimated_clv"],
            ],
        }
    )
    st.dataframe(explain_df, use_container_width=True, hide_index=True)
    st.caption(
        "V1 uses a transparent weighted decision score. ATI measures monitoring intensity only; "
        "it is not interpreted as anger or anxiety."
    )

st.subheader("3. Policy Comparison")
display_summary = summary.copy()
for col in ["Recovery Spend", "Expected Value Preserved", "Net Retention Value"]:
    display_summary[col] = display_summary[col].map(lambda x: f"₹{x:,.0f}")
st.dataframe(display_summary, use_container_width=True, hide_index=True)

st.subheader("4. High-Priority Queue")
queue_cols = [
    "order_id",
    "predicted_delay_min",
    "active_tracking_intensity",
    "support_attempts",
    "recent_service_failures",
    "churn_propensity",
    "estimated_clv",
    "service_recovery_risk_score",
    "support_route",
    "recovery_action",
]
queue = detail.sort_values(
    ["service_recovery_risk_score", "predicted_delay_min"],
    ascending=False,
)[queue_cols].head(25)
st.dataframe(queue, use_container_width=True, hide_index=True)

with st.expander("V1 assumptions and limitations"):
    st.markdown(
        """
- Predicted delay is treated as an input from an existing logistics backend.
- Customer and order data are synthetic.
- CLV is formula-based, not a trained production model.
- Churn propensity is synthetic and scenario-driven.
- Recovery effectiveness is an explicit simulation assumption, not a causal estimate.
- Active Tracking Intensity is a hypothesis feature and should not be interpreted as emotion.
- Customer value changes recovery intensity, not physical delivery priority.
        """
    )
