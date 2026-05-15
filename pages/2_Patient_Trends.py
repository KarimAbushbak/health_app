"""Patient Trends: admissions over time, diagnoses, departments, age groups."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.data_loader import load_healthcare_data
from utils.filters import render_sidebar_filters
from utils.page_setup import setup_page
from utils.styling import page_header

setup_page("Patient Trends | Healthcare Analytics")

page_header("Patient Trends", "Volume, clinical mix, and demographic distribution.")

try:
    raw = load_healthcare_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

filtered = render_sidebar_filters(raw)

if filtered.empty:
    st.warning("No rows match the current filters.")
    st.stop()

# Admissions over time (monthly)
filtered = filtered.copy()
filtered["admission_month"] = filtered["admission_date"].dt.to_period("M").dt.to_timestamp()
monthly = filtered.groupby("admission_month", as_index=False).size().rename(columns={"size": "admissions"})

fig_time = px.line(
    monthly,
    x="admission_month",
    y="admissions",
    markers=True,
    title="Admissions over time (by month)",
)
fig_time.update_layout(template="plotly_white", hovermode="x unified")

dx_df = filtered["diagnosis"].value_counts().reset_index()
dx_df.columns = ["diagnosis", "count"]
fig_dx = px.bar(dx_df, x="diagnosis", y="count", title="Diagnosis distribution (encounter volume)")
fig_dx.update_layout(template="plotly_white", xaxis_tickangle=-35)

dept_df = filtered["department"].value_counts().reset_index()
dept_df.columns = ["department", "count"]
fig_dept = px.bar(dept_df, x="department", y="count", title="Department utilization")
fig_dept.update_layout(template="plotly_white")

age_df = filtered["age_group"].value_counts().reset_index()
age_df.columns = ["age_group", "count"]
fig_age = px.bar(age_df, x="age_group", y="count", title="Encounters by age group")
fig_age.update_layout(template="plotly_white")

r1, r2 = st.columns(2)
with r1:
    st.plotly_chart(fig_time, use_container_width=True)
with r2:
    st.plotly_chart(fig_dx, use_container_width=True)

r3, r4 = st.columns(2)
with r3:
    st.plotly_chart(fig_dept, use_container_width=True)
with r4:
    st.plotly_chart(fig_age, use_container_width=True)

st.download_button(
    "Download filtered data (CSV)",
    data=filtered.drop(columns=["admission_month"], errors="ignore").to_csv(index=False).encode("utf-8"),
    file_name="healthcare_filtered_trends.csv",
    mime="text/csv",
)
