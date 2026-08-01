"""Milestone 6: spatial (district-level) and health (per-donor) features."""

import numpy as np
import pandas as pd
from src.utils.config import CONFIG
from src.utils.logger import get_logger

log = get_logger(__name__)
THRESH = CONFIG["thresholds"]


def add_health_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Healthy_Donor"] = (
        (df["Hemoglobin_g_dL"] >= THRESH["eligible_min_hemoglobin_g_dl"])
        & (df["Weight_kg"] >= THRESH["eligible_min_weight_kg"])
        & df["Age"].between(THRESH["eligible_min_age"], THRESH["eligible_max_age"])
    )

    if "Medical_Condition" in df.columns:
        no_condition_values = {"none", "nil", "na", "n/a", "no", ""}
        df["Has_Medical_Condition"] = ~(
            df["Medical_Condition"].astype(str).str.strip().str.lower().isin(no_condition_values)
        )
    else:
        df["Has_Medical_Condition"] = np.nan

    df["High_Hemoglobin"] = df["Hemoglobin_g_dL"] > 17.5  # upper normal bound, flag for review

    log.info("add_health_features: added Healthy_Donor, Has_Medical_Condition, High_Hemoglobin")
    return df


def add_spatial_features(donors: pd.DataFrame, district_summary: pd.DataFrame) -> pd.DataFrame:
    """Broadcast district-level spatial stats (bank count, density) back onto
    each donor row — useful for donor-level modeling later, even though the
    core spatial analysis (DBSCAN/KDE) operates on district_summary directly."""

    cols = ["District", "n_blood_banks", "population_per_blood_bank", "donor_density_per_100k"]
    cols = [c for c in cols if c in district_summary.columns]

    df = donors.merge(district_summary[cols], on="District", how="left")
    log.info(f"add_spatial_features: broadcast {cols[1:]} onto donor rows")
    return df
