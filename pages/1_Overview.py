"""Overview page: headline KPIs for the filtered cohort."""

from __future__ import annotations

import streamlit as st

from utils.data_loader import load_healthcare_data
from utils.filters import render_sidebar_filters
from utils.kpis import compute_overview_kpis
from utils.page_setup import setup_page
from utils.styling import page_header

setup_page("Overview | Healthcare Analytics")

page_header("Overview", "Population-level KPIs for the currently filtered encounters.")

try:
    raw = load_healthcare_data()
except Exception as e:  # noqa: BLE001 — show friendly message in UI
    st.error(f"Could not load data: {e}")
    st.stop()

filtered = render_sidebar_filters(raw)

kpis = compute_overview_kpis(filtered)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Distinct patients", f"{int(kpis['total_patients']):,}")
c2.metric("Avg length of stay (days)", f"{kpis['avg_los']:.1f}")
c3.metric("30-day readmission rate", f"{kpis['readmission_rate']:.1f}%")
c4.metric("Avg treatment cost", f"${kpis['avg_cost']:,.0f}")
c5.metric("Avg wait time (min)", f"{kpis['avg_wait']:.0f}")

st.divider()
left, right = st.columns([2, 1])
with left:
    st.markdown("### Snapshot")
    st.dataframe(
        filtered.head(50),
        use_container_width=True,
        hide_index=True,
    )
with right:
    st.markdown("### Export")
    st.download_button(
        label="Download filtered data (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="healthcare_filtered_overview.csv",
        mime="text/csv",
    )
    st.caption("Export respects all sidebar filters on this page.")
