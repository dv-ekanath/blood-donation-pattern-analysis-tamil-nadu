"""Milestone 11: Recommendation engine.

Turns the BDPI-scored district table into a human-readable recommendation
per district, with an explanation grounded in the actual sub-scores rather
than a fixed template — each explanation cites the specific driver(s)
that pushed the district's priority up or down.
"""

import pandas as pd
from src.utils.logger import get_logger

log = get_logger(__name__)

PRIORITY_BANDS = [
    (75, "Critical Priority", "Organize a donation drive immediately."),
    (55, "High Priority", "Organize additional donation camps within the next quarter."),
    (35, "Moderate Priority", "Consider a donation camp aligned with the next seasonal dip."),
    (0, "Low Priority", "Maintain existing donation frequency; monitor quarterly."),
]

SUB_SCORE_LABELS = {
    "population_score": "large population base",
    "donor_density_score": "low existing donor density",
    "eligible_donor_pct_score": "high eligible-donor share",
    "blood_bank_coverage_score": "poor blood bank coverage relative to population",
    "recent_donation_activity_score": "low recent donation activity",
}


def _priority_band(score: float):
    for threshold, label, action in PRIORITY_BANDS:
        if score >= threshold:
            return label, action
    return PRIORITY_BANDS[-1][1], PRIORITY_BANDS[-1][2]


def _top_drivers(row: pd.Series, n: int = 2) -> list[str]:
    scores = {col: row[col] for col in SUB_SCORE_LABELS if col in row.index}
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:n]
    return [SUB_SCORE_LABELS[col] for col, _ in ranked]


def generate_recommendations(bdpi_df: pd.DataFrame, seasonal_hint: dict | None = None) -> pd.DataFrame:
    """seasonal_hint: optional dict of {District: "recommended season string"}
    sourced from src/temporal/trend_analysis.seasonal_index, e.g. to append
    "before the summer donation dip" style context."""

    df = bdpi_df.copy()
    records = []

    for _, row in df.iterrows():
        band, action = _priority_band(row["BDPI"])
        drivers = _top_drivers(row)
        driver_text = " and ".join(drivers)

        explanation = (
            f"{row['District']} scores {row['BDPI']}/100 ({band}), "
            f"driven primarily by {driver_text}."
        )
        recommendation = action
        if seasonal_hint and row["District"] in seasonal_hint:
            recommendation += f" {seasonal_hint[row['District']]}"

        records.append({
            "District": row["District"],
            "BDPI": row["BDPI"],
            "Rank": row["BDPI_Rank"],
            "Priority_Band": band,
            "Recommendation": recommendation,
            "Explanation": explanation,
        })

    result = pd.DataFrame(records).sort_values("Rank")
    log.info(f"generate_recommendations: produced {len(result)} district recommendations")
    return result
