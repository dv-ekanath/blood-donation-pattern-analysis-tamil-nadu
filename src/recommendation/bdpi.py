"""Milestone 10: Blood Donation Priority Index (BDPI).

BDPI = 0.30*population_score + 0.25*donor_density + 0.20*eligible_pct
       + 0.15*blood_bank_coverage + 0.10*recent_donation_activity

Every sub-score is min-max normalized to [0, 100] across districts *before*
weighting, so the weights in config.yaml genuinely control contribution —
without normalization a raw population count would dominate the raw
percentage columns purely due to scale.

Note the deliberate inversions:
- population_score: higher population -> higher priority (more potential need)
- donor_density: higher existing donor density -> LOWER priority (already served)
- blood_bank_coverage: fewer people per blood bank -> LOWER priority (well covered)
So donor_density and blood_bank_coverage are inverted after normalization —
see the comments below. Revisit this framing before finalizing your report;
it's a modeling choice you should be able to defend in the viva.
"""

import pandas as pd
from src.utils.config import CONFIG
from src.utils.logger import get_logger

log = get_logger(__name__)
WEIGHTS = CONFIG["bdpi_weights"]


def _minmax_0_100(s: pd.Series) -> pd.Series:
    rng = s.max() - s.min()
    if rng == 0:
        return pd.Series(50.0, index=s.index)  # no variance -> neutral score
    return (s - s.min()) / rng * 100


def compute_bdpi(district_summary: pd.DataFrame) -> pd.DataFrame:
    df = district_summary.copy()

    # --- sub-scores, each normalized 0-100 ---
    df["population_score"] = _minmax_0_100(df["Population"])

    # donor_density_per_100k: higher = already well-served -> invert so LOW
    # density gets a HIGH priority contribution
    donor_density_norm = _minmax_0_100(df["donor_density_per_100k"].fillna(0))
    df["donor_density_score"] = 100 - donor_density_norm

    df["eligible_donor_pct_score"] = _minmax_0_100(df["eligible_pct"].fillna(0) * 100)

    # population_per_blood_bank: higher = worse coverage -> higher priority (no invert)
    df["blood_bank_coverage_score"] = _minmax_0_100(df["population_per_blood_bank"].fillna(df["population_per_blood_bank"].max()))

    # recent_donation_activity should come from temporal analysis
    # (fraction of donors in this district who donated recently); default to
    # neutral 50 if not yet joined in.
    if "recent_activity_pct" not in df.columns:
        log.warning("`recent_activity_pct` not found in district_summary — "
                     "defaulting recent_donation_activity_score to 50 (neutral). "
                     "Join this in from temporal analysis before finalizing.")
        df["recent_activity_pct"] = 0.5
    recent_norm = _minmax_0_100(df["recent_activity_pct"].fillna(0.5))
    df["recent_donation_activity_score"] = 100 - recent_norm  # low recent activity -> higher priority

    df["BDPI"] = (
        WEIGHTS["population_score"] * df["population_score"]
        + WEIGHTS["donor_density"] * df["donor_density_score"]
        + WEIGHTS["eligible_donor_pct"] * df["eligible_donor_pct_score"]
        + WEIGHTS["blood_bank_coverage"] * df["blood_bank_coverage_score"]
        + WEIGHTS["recent_donation_activity"] * df["recent_donation_activity_score"]
    ).round(2)

    df["BDPI_Rank"] = df["BDPI"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("BDPI_Rank")

    log.info(f"compute_bdpi: scored {len(df)} districts, top priority = "
             f"{df.iloc[0]['District']} ({df.iloc[0]['BDPI']})")
    return df
