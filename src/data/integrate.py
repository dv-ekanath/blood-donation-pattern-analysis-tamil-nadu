"""Milestone 5: Data integration.

The trickiest part of this project: donors have `City`, blood banks have
`district` directly, and the population census has `District`. None of
these are guaranteed to line up as free text, so we integrate through a
canonical district list (config.yaml -> tn_districts) using fuzzy matching,
with an explicit manual-override table for known mismatches.

Fill in `CITY_TO_DISTRICT_OVERRIDES` as you discover mismatches during
milestone 5/6 — this is meant to grow, not be complete on day one.
"""

import pandas as pd
from rapidfuzz import process, fuzz  # add `rapidfuzz` to requirements.txt
from src.utils.config import CONFIG
from src.utils.logger import get_logger

log = get_logger(__name__)

TN_DISTRICTS = CONFIG["tn_districts"]

# Known city -> district mappings that fuzzy matching won't get right
# (e.g. "Coimbatore North" is a locality inside Coimbatore district, not a
# district itself). Extend this as you inspect real data in milestone 3.
CITY_TO_DISTRICT_OVERRIDES = {
    "Chennai City": "Chennai",
    "Coimbatore North": "Coimbatore",
    "Coimbatore South": "Coimbatore",
    "Trichy": "Tiruchirappalli",
    "Tuticorin": "Thoothukudi",
    "Nagercoil": "Kanyakumari",
    "Ooty": "Nilgiris",
    "Udhagamandalam": "Nilgiris",
    "Pondicherry": None,   # not a TN district — flag for exclusion/review
    "Puducherry": None,
}


def map_to_district(value: str, score_cutoff: int = 80) -> str | None:
    """Map a free-text city/locality string to a canonical TN district name.

    Returns None if no confident match is found — inspect these rows rather
    than silently dropping them.
    """
    if pd.isna(value) or not str(value).strip():
        return None
    value = str(value).strip()

    if value in CITY_TO_DISTRICT_OVERRIDES:
        return CITY_TO_DISTRICT_OVERRIDES[value]

    match = process.extractOne(value, TN_DISTRICTS, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
    return match[0] if match else None


def add_district_column(df: pd.DataFrame, source_col: str, new_col: str = "District") -> pd.DataFrame:
    df = df.copy()
    df[new_col] = df[source_col].apply(map_to_district)
    n_unmatched = df[new_col].isna().sum()
    if n_unmatched:
        log.info(
            f"{n_unmatched}/{len(df)} rows in '{source_col}' could not be mapped to a "
            f"TN district (score_cutoff too strict, or genuinely out-of-state / "
            f"free-text noise). Inspect df[df['{new_col}'].isna()]['{source_col}'].unique()."
        )
    return df


def integrate_donors(donors_clean: pd.DataFrame) -> pd.DataFrame:
    donors = add_district_column(donors_clean, source_col="City", new_col="District")
    return donors


def integrate_blood_banks(blood_banks_clean: pd.DataFrame) -> pd.DataFrame:
    bb = blood_banks_clean.copy()
    if "district" in bb.columns:
        bb = add_district_column(bb, source_col="district", new_col="District")
    return bb


def build_district_summary(
    donors: pd.DataFrame,
    blood_banks: pd.DataFrame,
    population: pd.DataFrame,
) -> pd.DataFrame:
    """One row per district — the table BDPI and the dashboard are built on."""

    donor_agg = (
        donors.groupby("District")
        .agg(
            n_donors=("Donor_ID", "count"),
            n_eligible=("Eligible_for_Donation", "sum"),
            avg_total_donations=("Total_Donations", "mean"),
        )
        .reset_index()
    )
    donor_agg["eligible_pct"] = donor_agg["n_eligible"] / donor_agg["n_donors"]

    bb_agg = (
        blood_banks.groupby("District")
        .size()
        .reset_index(name="n_blood_banks")
    )

    summary = (
        population.merge(donor_agg, on="District", how="left")
        .merge(bb_agg, on="District", how="left")
    )

    for col in ["n_donors", "n_eligible", "n_blood_banks"]:
        summary[col] = summary[col].fillna(0)

    summary["donor_density_per_100k"] = summary["n_donors"] / summary["Population"] * 100_000
    summary["population_per_blood_bank"] = summary["Population"] / summary["n_blood_banks"].replace(0, pd.NA)

    log.info(f"build_district_summary: {len(summary)} districts")
    return summary
