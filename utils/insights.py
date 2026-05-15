"""
Rule-based and lightweight ML-assisted insights for the AI Insights page.
Insights are descriptive only — not clinical guidance.
"""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest


def _safe_mean_by(df: pd.DataFrame, group_col: str, value_col: str) -> pd.Series:
    """Mean of value_col by group_col; empty-safe."""
    if df.empty or group_col not in df.columns:
        return pd.Series(dtype=float)
    return df.groupby(group_col, dropna=True)[value_col].mean().sort_values(ascending=False)


def generate_rule_based_insights(df: pd.DataFrame) -> list[str]:
    """
    Produce plain-language statements from aggregates.
    Order: cost, wait time, readmission vs LOS, top diagnosis volume.
    """
    insights: list[str] = []
    if df.empty:
        return ["Not enough rows under current filters to generate insights."]

    # Highest average treatment cost by department
    cost_by_dept = _safe_mean_by(df, "department", "treatment_cost")
    if not cost_by_dept.empty:
        top_dept = cost_by_dept.index[0]
        insights.append(
            f"{top_dept} shows the highest average treatment cost "
            f"(${cost_by_dept.iloc[0]:,.0f}) among filtered departments."
        )

    # Longest average wait by department
    wait_by_dept = _safe_mean_by(df, "department", "wait_time_minutes")
    if not wait_by_dept.empty:
        slow = wait_by_dept.index[0]
        insights.append(
            f"{slow} registers the longest average wait time "
            f"({wait_by_dept.iloc[0]:.0f} minutes) in the current selection."
        )

    # Readmission vs length of stay (simple correlation narrative)
    los_std = df["length_of_stay"].std()
    if pd.notna(los_std) and los_std > 0 and len(df) > 30:
        corr = df[["readmission_30_days", "length_of_stay"]].corr().iloc[0, 1]
        if corr > 0.08:
            insights.append(
                "Patients with longer stays show a higher readmission signal in this sample "
                f"(Pearson r ≈ {corr:.2f} between length of stay and readmission flag)."
            )
        elif corr < -0.05:
            insights.append(
                "Readmission appears negatively associated with length of stay in this slice — "
                "worth validating with risk-adjusted models before operational action."
            )

    # Top diagnosis by volume
    dx_counts = df["diagnosis"].value_counts()
    if not dx_counts.empty:
        top_dx = dx_counts.index[0]
        insights.append(
            f"The most frequent diagnosis in the filtered cohort is **{top_dx}** "
            f"({dx_counts.iloc[0]:,} encounters)."
        )

    # Insurance mix — self-pay cost pressure (simple rule)
    if "insurance_type" in df.columns and df["insurance_type"].notna().any():
        by_ins = df.groupby("insurance_type")["treatment_cost"].mean().sort_values(ascending=False)
        if "Self-pay" in by_ins.index:
            sp = by_ins.get("Self-pay", float("nan"))
            overall = df["treatment_cost"].mean()
            if sp > overall * 1.05:
                insights.append(
                    "Self-pay encounters average higher treatment cost than the overall mean — "
                    "often reflecting acuity, billing practices, or selection; investigate further."
                )

    return insights or ["No additional rule-based insights for this filter combination."]


def detect_cost_wait_anomalies(df: pd.DataFrame, contamination: float = 0.02) -> pd.DataFrame:
    """
    Flag multivariate outliers in cost / wait / LOS using Isolation Forest (unsupervised).
    Returns a small table of most anomalous rows for analyst review.
    """
    if len(df) < 50:
        return pd.DataFrame()

    use = df[["treatment_cost", "wait_time_minutes", "length_of_stay"]].dropna()
    if len(use) < 50:
        return pd.DataFrame()

    model = IsolationForest(contamination=min(contamination, 0.5), random_state=42)
    preds = model.fit_predict(use)
    scores = model.decision_function(use)
    out = df.loc[use.index].copy()
    out["anomaly_score"] = scores
    out["is_anomaly"] = preds == -1
    flagged = out[out["is_anomaly"]].sort_values("anomaly_score").head(25)
    return flagged[
        [
            "patient_id",
            "department",
            "diagnosis",
            "treatment_cost",
            "wait_time_minutes",
            "length_of_stay",
            "anomaly_score",
        ]
    ]
