"""KPI calculations for the Overview page."""

from __future__ import annotations

import pandas as pd


def compute_overview_kpis(df: pd.DataFrame) -> dict[str, float]:
    """
    Return core operational KPIs from the filtered frame.
    Uses distinct patient_id for 'total patients' to align with deduplicated headcount.
    """
    if df.empty:
        return {
            "total_patients": 0.0,
            "avg_los": 0.0,
            "readmission_rate": 0.0,
            "avg_cost": 0.0,
            "avg_wait": 0.0,
        }

    total_patients = float(df["patient_id"].nunique())
    avg_los = float(df["length_of_stay"].mean())
    readmission_rate = float(df["readmission_30_days"].mean() * 100)
    avg_cost = float(df["treatment_cost"].mean())
    avg_wait = float(df["wait_time_minutes"].mean())

    return {
        "total_patients": total_patients,
        "avg_los": avg_los,
        "readmission_rate": readmission_rate,
        "avg_cost": avg_cost,
        "avg_wait": avg_wait,
    }
