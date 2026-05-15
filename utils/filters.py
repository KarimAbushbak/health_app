"""Sidebar filters shared across dashboard pages."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st


def add_age_group_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add age_group buckets for filtering and charts.
    Invalid or missing ages map to 'Unknown' so filters stay intuitive.
    """
    out = df.copy()
    ages = out["age"]
    groups = pd.Series("Unknown", index=out.index, dtype=object)
    valid = ages.notna() & (ages >= 0) & (ages <= 110)
    clipped = ages.clip(lower=0, upper=110)
    bins = [0, 18, 35, 50, 65, 111]
    labels = ["0-17", "18-34", "35-49", "50-64", "65+"]
    groups.loc[valid] = pd.cut(clipped[valid], bins=bins, labels=labels, right=False).astype(str)
    out["age_group"] = groups.astype(str)
    return out


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render Streamlit sidebar controls and return a filtered DataFrame.
    Expects parsed admission_date; adds age_group for convenience.
    """
    df = add_age_group_column(df)

    st.sidebar.markdown("### Filters")
    st.sidebar.caption("Apply across all dashboard sections.")

    min_d = df["admission_date"].min().date()
    max_d = df["admission_date"].max().date()
    default_start = max(min_d, date(max_d.year - 1, max_d.month, min(max_d.day, 28)))

    date_range = st.sidebar.date_input(
        "Admission date range",
        value=(default_start, max_d),
        min_value=min_d,
        max_value=max_d,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
    else:
        start, end = min_d, max_d

    departments = sorted(df["department"].dropna().unique())
    diagnoses = sorted(df["diagnosis"].dropna().unique())
    genders = sorted(df["gender"].dropna().unique())
    age_groups = [g for g in sorted(df["age_group"].unique()) if g != "nan"]

    sel_dept = st.sidebar.multiselect("Department", departments, default=departments)
    sel_dx = st.sidebar.multiselect("Diagnosis", diagnoses, default=diagnoses)
    sel_gender = st.sidebar.multiselect("Gender", genders, default=genders)
    sel_age = st.sidebar.multiselect("Age group", age_groups, default=age_groups)

    mask = (
        (df["admission_date"].dt.date >= start)
        & (df["admission_date"].dt.date <= end)
        & (df["department"].isin(sel_dept))
        & (df["diagnosis"].isin(sel_dx))
        & (df["gender"].isin(sel_gender))
        & (df["age_group"].isin(sel_age))
    )

    filtered = df.loc[mask].copy()
    st.sidebar.metric("Rows after filters", f"{len(filtered):,}")
    return filtered
