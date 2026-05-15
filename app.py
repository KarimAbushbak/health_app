"""
Healthcare Analytics Dashboard — main entry point.

Run locally: streamlit run app.py

Multipage sections live under pages/. Shared utilities load data, apply filters,
and render a consistent clinical-style UI.
"""

from __future__ import annotations

import streamlit as st

from utils.page_setup import setup_page
from utils.styling import page_header

# Page config must be the first Streamlit command.
setup_page("Healthcare Analytics Dashboard")

page_header(
    "Healthcare Analytics Dashboard",
    "Portfolio demo: synthetic inpatient-style data for analytics, operations, and data quality practice.",
)

st.info(
    "**Data disclaimer:** All records are **synthetic** and intended for education and analytics "
    "portfolio use only. They do not represent real patients and must not be used for care decisions."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### What this demonstrates")
    st.markdown(
        "- Health informatics metrics (LOS, readmissions, cost, access)\n"
        "- Interactive reporting with Streamlit + Plotly\n"
        "- Data quality monitoring patterns\n"
        "- Rule-based operational insights + simple anomaly screening"
    )
with col2:
    st.markdown("### How to navigate")
    st.markdown(
        "Use the **sidebar** to open each section:\n\n"
        "1. **Overview** — KPI cards\n"
        "2. **Patient Trends** — volume and mix\n"
        "3. **Operational Insights** — wait, cost, LOS drivers\n"
        "4. **Data Quality** — completeness and validity\n"
        "5. **AI Insights** — automated highlights"
    )
with col3:
    st.markdown("### Filters")
    st.markdown(
        "Date range, department, diagnosis, gender, and age group filters apply on each page "
        "via the sidebar. Download the **filtered** table as CSV from any analytics page."
    )

st.divider()
st.caption("Built with Python · Streamlit · Pandas · Plotly · scikit-learn")
