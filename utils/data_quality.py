"""Data quality checks for the Data Quality dashboard page."""

from __future__ import annotations

import pandas as pd


def missing_value_summary(df: pd.DataFrame) -> pd.Series:
    """Count nulls per column (excluding rows with no issues is not required — full scan)."""
    return df.isna().sum().sort_values(ascending=False)


def duplicate_patient_records(df: pd.DataFrame) -> pd.DataFrame:
    """Rows where patient_id appears more than once (repeat encounters / duplicate rows)."""
    dup_ids = df["patient_id"][df["patient_id"].duplicated(keep=False)]
    return df[df["patient_id"].isin(dup_ids)].sort_values(["patient_id", "admission_date"])


def invalid_ages(df: pd.DataFrame) -> pd.DataFrame:
    """Ages outside a plausible human range for administrative data."""
    ages = df["age"]
    bad = ages.isna() | (ages < 0) | (ages > 110)
    return df.loc[bad].copy()


def inconsistent_admission_discharge(df: pd.DataFrame) -> pd.DataFrame:
    """Discharge strictly before admission — impossible without data entry error."""
    bad = df["discharge_date"] < df["admission_date"]
    return df.loc[bad].copy()


def data_quality_issue_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode semicolon-separated data_quality_issue values and count occurrences.
    """
    col = df["data_quality_issue"].fillna("None").astype(str)
    exploded = col.str.split(";").explode()
    counts = exploded.value_counts().rename_axis("issue").reset_index(name="count")
    return counts
