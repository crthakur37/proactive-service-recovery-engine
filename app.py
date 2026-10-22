"""Streamlit entry point for the Proactive Service-Recovery Decision Engine."""

import streamlit as st

st.set_page_config(
    page_title="Proactive Service-Recovery Engine",
    page_icon="🍽️",
    layout="wide",
)

st.title("Proactive Service-Recovery Decision Engine")
st.caption("V1 prototype — implementation in progress")

st.info(
    "This project uses synthetic data to explore risk-aware customer service recovery "
    "for likely or actual food-delivery SLA breaches."
)
