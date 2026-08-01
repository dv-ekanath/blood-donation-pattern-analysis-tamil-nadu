"""Milestone 6: per-donor temporal features derived from
Registration_Date / Last_Donation_Date / Total_Donations."""

import numpy as np
import pandas as pd
from src.utils.config import CONFIG
from src.utils.logger import get_logger

log = get_logger(__name__)
THRESH = CONFIG["thresholds"]

SEASON_MAP = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon",
}


def add_temporal_features(df: pd.DataFrame, reference_date: pd.Timestamp | None = None) -> pd.DataFrame:
    df = df.copy()
    reference_date = reference_date or pd.Timestamp.today().normalize()

    df["Registration_Year"] = df["Registration_Date"].dt.year
    df["Registration_Month"] = df["Registration_Date"].dt.month
    df["Registration_Season"] = df["Registration_Month"].map(SEASON_MAP)

    df["Last_Donation_Month"] = df["Last_Donation_Date"].dt.month
    df["Last_Donation_Season"] = df["Last_Donation_Month"].map(SEASON_MAP)

    df["Days_Since_Last_Donation"] = (reference_date - df["Last_Donation_Date"]).dt.days
    df["Years_As_Donor"] = (reference_date - df["Registration_Date"]).dt.days / 365.25

    # Estimated donation frequency: donations per year of donor tenure.
    # Guard against div-by-zero for brand-new registrants.
    tenure_years = df["Years_As_Donor"].clip(lower=1 / 365.25)
    df["Estimated_Donation_Frequency"] = df["Total_Donations"] / tenure_years

    df["Repeat_Donor"] = df["Total_Donations"] >= THRESH["repeat_donor_min_total"]
    df["Recent_Donor"] = df["Days_Since_Last_Donation"] <= THRESH["recent_activity_days"]
    # Never donated at all (Last_Donation_Date missing but registered)
    df["Never_Donated"] = df["Last_Donation_Date"].isna()

    log.info("add_temporal_features: added Registration_Year/Month/Season, "
             "Last_Donation_Month/Season, Days_Since_Last_Donation, Years_As_Donor, "
             "Estimated_Donation_Frequency, Repeat_Donor, Recent_Donor, Never_Donated")
    return df
