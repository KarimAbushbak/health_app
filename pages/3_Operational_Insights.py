"""Operational Insights: wait times, LOS, cost, and readmission trends."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.data_loader import load_healthcare_data
from utils.filters import render_sidebar_filters
from utils.page_setup import setup_page
from utils.styling import page_header

setup_page("Operational Insights | Healthcare Analytics")

page_header("Operational Insights", "Access, efficiency, cost, and outcomes-oriented views.")

try:
    raw = load_healthcare_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

filtered = render_sidebar_filters(raw)

if filtered.empty:
    st.warning("No rows match the current filters.")
    st.stop()

wait_by_dept = (
    filtered.groupby("department", as_index=False)["wait_time_minutes"].mean().sort_values("wait_time_minutes")
)
fig_wait = px.bar(
    wait_by_dept,
    x="department",
    y="wait_time_minutes",
    title="Average wait time by department (minutes)",
)
fig_wait.update_layout(template="plotly_white")

los_by_dx = filtered.groupby("diagnosis", as_index=False)["length_of_stay"].mean().sort_values("length_of_stay")
fig_los = px.bar(los_by_dx, x="diagnosis", y="length_of_stay", title="Average length of stay by diagnosis")
fig_los.update_layout(template="plotly_white", xaxis_tickangle=-35)

cost_by_dept = filtered.groupby("department", as_index=False)["treatment_cost"].mean().sort_values(
    "treatment_cost", ascending=False
)
fig_cost = px.bar(cost_by_dept, x="department", y="treatment_cost", title="Average treatment cost by department")
fig_cost.update_layout(template="plotly_white")

filtered = filtered.copy()
filtered["admission_month"] = filtered["admission_date"].dt.to_period("M").dt.to_timestamp()
readmit_trend = filtered.groupby("admission_month", as_index=False)["readmission_30_days"].mean()
readmit_trend["rate_pct"] = readmit_trend["readmission_30_days"] * 100
fig_readmit = px.line(
    readmit_trend,
    x="admission_month",
    y="rate_pct",
    markers=True,
    title="30-day readmission rate over time (% of encounters)",
)
fig_readmit.update_layout(template="plotly_white", yaxis_title="Readmission %", hovermode="x unified")

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(fig_wait, use_container_width=True)
with c2:
    st.plotly_chart(fig_cost, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(fig_los, use_container_width=True)
with c4:
    st.plotly_chart(fig_readmit, use_container_width=True)

export_df = filtered.drop(columns=["admission_month"], errors="ignore")
st.download_button(
    "Download filtered data (CSV)",
    data=export_df.to_csv(index=False).encode("utf-8"),
    file_name="healthcare_filtered_operations.csv",
    mime="text/csv",
)

