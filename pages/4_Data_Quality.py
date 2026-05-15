"""Data Quality: missing values, duplicates, invalid ages, date logic, issue flags."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from utils.data_loader import load_healthcare_data
from utils.data_quality import (
    data_quality_issue_summary,
    duplicate_patient_records,
    inconsistent_admission_discharge,
    invalid_ages,
    missing_value_summary,
)
from utils.filters import render_sidebar_filters
from utils.page_setup import setup_page
from utils.styling import page_header

setup_page("Data Quality | Healthcare Analytics")

page_header("Data Quality", "Profiling and validity checks on the synthetic administrative feed.")

try:
    raw = load_healthcare_data()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

filtered = render_sidebar_filters(raw)

if filtered.empty:
    st.warning("No rows match the current filters.")
    st.stop()

miss = missing_value_summary(filtered)
miss_nonzero = miss[miss > 0]

st.subheader("Missing values")
if miss_nonzero.empty:
    st.success("No missing values in the filtered selection.")
else:
    df_miss = miss_nonzero.reset_index()
    df_miss.columns = ["column", "missing_count"]
    fig_miss = px.bar(
        df_miss,
        x="column",
        y="missing_count",
        title="Missing value counts by column",
    )
    fig_miss.update_layout(template="plotly_white")
    st.plotly_chart(fig_miss, use_container_width=True)
    with st.expander("Raw missing-value counts"):
        st.dataframe(miss_nonzero.to_frame(name="count"), use_container_width=True)

st.subheader("Duplicate patient records")
dups = duplicate_patient_records(filtered)
st.metric("Rows tied to duplicated patient_id values", f"{len(dups):,}")
if not dups.empty:
    st.dataframe(dups.head(100), use_container_width=True, hide_index=True)

st.subheader("Invalid ages")
bad_age = invalid_ages(filtered)
st.metric("Rows with missing or implausible age", f"{len(bad_age):,}")
if not bad_age.empty:
    st.dataframe(bad_age.head(100), use_container_width=True, hide_index=True)

st.subheader("Inconsistent admission / discharge dates")
bad_dates = inconsistent_admission_discharge(filtered)
st.metric("Rows where discharge precedes admission", f"{len(bad_dates):,}")
if not bad_dates.empty:
    st.dataframe(bad_dates.head(100), use_container_width=True, hide_index=True)

st.subheader("Summary of data_quality_issue flags")
issue_tbl = data_quality_issue_summary(filtered)
fig_issues = px.bar(issue_tbl, x="issue", y="count", title="Frequency of flagged data-quality issues")
fig_issues.update_layout(template="plotly_white", xaxis_tickangle=-30)
st.plotly_chart(fig_issues, use_container_width=True)
with st.expander("Issue table"):
    st.dataframe(issue_tbl, use_container_width=True, hide_index=True)

st.download_button(
    "Download filtered data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="healthcare_filtered_data_quality.csv",
    mime="text/csv",
)
