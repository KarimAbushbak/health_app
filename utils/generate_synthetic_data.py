"""
Generate a realistic synthetic healthcare dataset for portfolio / demo use.
Not for clinical decision-making. Introduces intentional data-quality issues for the DQ page.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Departments and diagnoses used for realistic cross-tabs
DEPARTMENTS = [
    "Emergency",
    "Cardiology",
    "Orthopedics",
    "Internal Medicine",
    "Surgery",
    "Neurology",
    "Oncology",
    "Pulmonology",
]

DIAGNOSES = [
    "Pneumonia",
    "Heart Failure",
    "Type 2 Diabetes",
    "COPD",
    "Acute MI",
    "Stroke",
    "Sepsis",
    "Hip Fracture",
    "Cellulitis",
    "Acute Kidney Injury",
]

GENDERS = ["M", "F", "Other", "Unknown"]
INSURANCE = ["Medicare", "Medicaid", "Commercial", "Self-pay", "Other"]
OUTCOMES = ["Discharged Home", "Transferred", "Deceased", "AMA", "SNF"]


def _random_dates(
    rng: np.random.Generator, n: int, start: datetime
) -> tuple[pd.Series, pd.Series, np.ndarray]:
    """Admission and discharge dates with LOS aligned to discharge - admission."""
    offsets = rng.integers(0, 730, size=n)  # spread over ~2 years
    admissions = pd.to_datetime([start + timedelta(days=int(x)) for x in offsets])
    los_base = rng.poisson(lam=5, size=n).clip(1, 60)
    discharges = admissions + pd.to_timedelta(los_base, unit="D")
    return admissions, discharges, los_base


def generate_healthcare_dataset(
    n_rows: int = 4000,
    seed: int = 42,
    start_date: datetime | None = None,
) -> pd.DataFrame:
    """
    Build a synthetic inpatient-style table with deliberate quality problems:
    - Some missing cells
    - Duplicate patient_id rows
    - Invalid ages
    - Discharge before admission on a subset
    - data_quality_issue flags for auditing
    """
    rng = np.random.default_rng(seed)
    start = start_date or datetime(2023, 1, 1)

    patient_ids = np.arange(1, n_rows + 1)
    # Simulate repeat visits: duplicate ~8% of IDs with new rows appended later
    dup_mask = rng.random(n_rows) < 0.08
    dup_ids = patient_ids[dup_mask]

    ages = rng.normal(62, 18, size=n_rows).round().astype(int)
    gender = rng.choice(GENDERS, size=n_rows, p=[0.46, 0.46, 0.04, 0.04])
    department = rng.choice(DEPARTMENTS, size=n_rows, p=[0.22, 0.14, 0.12, 0.18, 0.12, 0.08, 0.08, 0.06])
    diagnosis = rng.choice(DIAGNOSES, size=n_rows)

    admissions, discharges, los_days = _random_dates(rng, n_rows, start)

    # Treatment cost correlates weakly with LOS and department complexity
    base_cost = 8000 + los_days * 1200
    dept_factor = pd.Series(department).map(
        {
            "Emergency": 1.1,
            "Cardiology": 1.35,
            "Orthopedics": 1.25,
            "Internal Medicine": 1.0,
            "Surgery": 1.4,
            "Neurology": 1.2,
            "Oncology": 1.45,
            "Pulmonology": 1.05,
        }
    ).to_numpy()
    noise = rng.normal(1.0, 0.12, size=n_rows)
    treatment_cost = np.clip(base_cost * dept_factor * noise, 2000, 250000).round(2)

    # Readmission higher for longer LOS and certain diagnoses
    readmit_prob = 0.08 + 0.002 * los_days
    readmit_prob += np.where(np.isin(diagnosis, ["Heart Failure", "COPD", "Pneumonia"]), 0.06, 0)
    readmission_30_days = rng.random(n_rows) < np.clip(readmit_prob, 0.02, 0.45)

    insurance_type = rng.choice(INSURANCE, size=n_rows, p=[0.35, 0.15, 0.38, 0.07, 0.05])
    outcome = rng.choice(OUTCOMES, size=n_rows, p=[0.72, 0.12, 0.03, 0.05, 0.08])

    # Wait times (minutes) — Emergency skews high
    wait_base = rng.gamma(shape=3, scale=25, size=n_rows)
    wait_base = np.where(department == "Emergency", wait_base * 1.8, wait_base)
    wait_time_minutes = np.clip(wait_base.round(), 5, 600).astype(int)

    df = pd.DataFrame(
        {
            "patient_id": patient_ids,
            "age": ages,
            "gender": gender,
            "diagnosis": diagnosis,
            "department": department,
            "admission_date": admissions,
            "discharge_date": discharges,
            "length_of_stay": los_days.astype(int),
            "readmission_30_days": readmission_30_days,
            "treatment_cost": treatment_cost,
            "insurance_type": insurance_type,
            "outcome": outcome,
            "wait_time_minutes": wait_time_minutes,
            "data_quality_issue": np.full(n_rows, "None", dtype=object),
        }
    )

    # --- Inject data quality issues (flagged in data_quality_issue) ---
    miss_idx = rng.choice(n_rows, size=int(n_rows * 0.03), replace=False)
    df.loc[miss_idx, "insurance_type"] = np.nan
    df.loc[miss_idx, "data_quality_issue"] = "missing_field"

    inv_age_idx = rng.choice(n_rows, size=25, replace=False)
    df.loc[inv_age_idx, "age"] = rng.choice([-3, 0, 150, 200], size=len(inv_age_idx))
    df.loc[inv_age_idx, "data_quality_issue"] = np.where(
        df.loc[inv_age_idx, "data_quality_issue"].eq("None"),
        "invalid_age",
        df.loc[inv_age_idx, "data_quality_issue"] + ";invalid_age",
    )

    bad_date_idx = rng.choice(n_rows, size=40, replace=False)
    df.loc[bad_date_idx, "discharge_date"] = df.loc[bad_date_idx, "admission_date"] - timedelta(days=1)
    df.loc[bad_date_idx, "data_quality_issue"] = np.where(
        df.loc[bad_date_idx, "data_quality_issue"].eq("None"),
        "date_inconsistency",
        df.loc[bad_date_idx, "data_quality_issue"] + ";date_inconsistency",
    )

    # Duplicate patient visits: copy rows with same patient_id (new admission)
    dup_rows = df[df["patient_id"].isin(dup_ids)].copy()
    if not dup_rows.empty:
        dup_rows["admission_date"] = dup_rows["admission_date"] + pd.to_timedelta(rng.integers(30, 400, len(dup_rows)), unit="D")
        dup_rows["discharge_date"] = dup_rows["admission_date"] + pd.to_timedelta(
            rng.integers(2, 20, len(dup_rows)), unit="D"
        )
        dup_rows["length_of_stay"] = (dup_rows["discharge_date"] - dup_rows["admission_date"]).dt.days.clip(lower=1)
        dup_rows["readmission_30_days"] = rng.random(len(dup_rows)) < 0.2
        dup_rows["data_quality_issue"] = np.where(
            dup_rows["data_quality_issue"].eq("None"),
            "duplicate_record",
            dup_rows["data_quality_issue"] + ";duplicate_record",
        )
        df = pd.concat([df, dup_rows], ignore_index=True)

    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    # Recompute length_of_stay from dates where consistent (keeps intentional bad rows wrong)
    ok = df["discharge_date"] >= df["admission_date"]
    df.loc[ok, "length_of_stay"] = (df.loc[ok, "discharge_date"] - df.loc[ok, "admission_date"]).dt.days.clip(lower=1).astype(int)

    return df


def ensure_dataset_csv(path: str, n_rows: int = 4000) -> None:
    """Write synthetic CSV if missing or empty."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        return
    df = generate_healthcare_dataset(n_rows=n_rows)
    df.to_csv(path, index=False)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "data", "healthcare_records.csv")
    ensure_dataset_csv(os.path.abspath(out))
    print(f"Wrote {os.path.abspath(out)}")
