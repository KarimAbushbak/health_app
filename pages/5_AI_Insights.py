"""AI Insights: rule-based narratives and lightweight anomaly detection."""

from __future__ import annotations

import streamlit as st

from utils.data_loader import load_healthcare_data
from utils.filters import render_sidebar_filters
from utils.insights import detect_cost_wait_anomalies, generate_rule_based_insights
from utils.page_setup import setup_page
from utils.styling import page_header

setup_page("AI Insights | Healthcare Analytics")

page_header(
    "AI Insights",
    "Automated highlights from aggregates plus unsupervised anomaly screening (not clinical AI).",
)

try:
    raw = load_healthcare_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

filtered = render_sidebar_filters(raw)

if filtered.empty:
    st.warning("No rows match the current filters.")
    st.stop()

st.subheader("Rule-based insights")
for line in generate_rule_based_insights(filtered):
    st.markdown(f"- {line}")

st.subheader("Anomaly detection (Isolation Forest)")
st.caption(
    "Flags unusual combinations of treatment cost, wait time, and length of stay for analyst follow-up."
)
anomalies = detect_cost_wait_anomalies(filtered)
if anomalies.empty:
    st.info("Not enough complete rows to run anomaly detection under current filters.")
else:
    st.dataframe(anomalies, use_container_width=True, hide_index=True)

st.download_button(
    "Download filtered data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="healthcare_filtered_ai_insights.csv",
    mime="text/csv",
)
