"""Load and cache healthcare data.

This dashboard is designed to work with a synthetic "fake" inpatient-style dataset by
default (portfolio demo). Optionally, you can point it at a custom CSV via an
environment variable, but the custom file must match the *internal dashboard schema*.
"""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from utils.generate_synthetic_data import ensure_dataset_csv

# Environment variable for pointing the app at a custom CSV.
# Example (PowerShell):
#   $env:HEALTHCARE_DASHBOARD_CSV = "C:\data\my_encounters.csv"
ENV_DATA_PATH = "HEALTHCARE_DASHBOARD_CSV"

REQUIRED_COLUMNS = (
    "patient_id",
    "age",
    "gender",
    "diagnosis",
    "department",
    "admission_date",
    "discharge_date",
    "length_of_stay",
    "readmission_30_days",
    "treatment_cost",
    "insurance_type",
    "outcome",
    "wait_time_minutes",
    "data_quality_issue",
)


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _default_data_path() -> str:
    """Path to the bundled synthetic portfolio CSV."""
    return os.path.join(_project_root(), "data", "healthcare_records.csv")


def _resolved_path(explicit: str | None) -> str:
    """Prefer explicit arg, then env var, then bundled synthetic default."""
    if explicit:
        return os.path.abspath(explicit)
    env = os.environ.get(ENV_DATA_PATH, "").strip().strip('"')
    if env:
        return os.path.abspath(env)
    return _default_data_path()


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(missing)
            + ". Expected: "
            + ", ".join(REQUIRED_COLUMNS)
        )


def _normalize_patient_id(series: pd.Series) -> pd.Series:
    """Support integer IDs or opaque strings (e.g. de-identified tokens)."""
    if pd.api.types.is_integer_dtype(series) or pd.api.types.is_float_dtype(series):
        return pd.to_numeric(series, errors="coerce").astype("Int64")
    out = series.astype(str).str.strip()
    return out.replace({"<na>": pd.NA, "nan": pd.NA})


def _normalize_readmission(series: pd.Series) -> pd.Series:
    """Accept bool, 0/1, or common string encodings from exports."""
    if pd.api.types.is_bool_dtype(series):
        return series
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).astype(int).astype(bool)
    s = series.astype(str).str.strip().str.lower()
    return s.isin(("1", "true", "t", "yes", "y"))


def _normalize_data_quality(series: pd.Series) -> pd.Series:
    """Normalize flags; empty strings map to 'None'."""
    out = series.astype(str).str.strip()
    out = out.replace({"": "None", "nan": "None"})
    return out


@st.cache_data(show_spinner=False)
def load_healthcare_data(csv_path: str | None = None) -> pd.DataFrame:
    """
    Load the healthcare dataset from CSV with Streamlit caching.

    Default: ``data/healthcare_records.csv`` (synthetic portfolio) (auto-created if missing).

    Real/custom data: set ``HEALTHCARE_DASHBOARD_CSV`` to a CSV path that uses the exact
    internal column names in ``REQUIRED_COLUMNS`` (dates must be parseable).
    """
    path = _resolved_path(csv_path)
    is_default = os.path.normpath(path) == os.path.normpath(_default_data_path())

    try:
        if is_default:
            ensure_dataset_csv(path)
        elif not os.path.isfile(path):
            raise FileNotFoundError(
                f"Custom data file not found: {path}. "
                f"Unset {ENV_DATA_PATH} to use the bundled synthetic dataset."
            )

        df = pd.read_csv(path, parse_dates=["admission_date", "discharge_date"])
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Data file not found at {path}") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError("CSV file is empty.") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to read healthcare data: {exc}") from exc

    _validate_columns(df)

    # Normalize dtypes for downstream charts
    df["patient_id"] = _normalize_patient_id(df["patient_id"])
    df["readmission_30_days"] = _normalize_readmission(df["readmission_30_days"])
    df["data_quality_issue"] = _normalize_data_quality(df["data_quality_issue"])
    return df

