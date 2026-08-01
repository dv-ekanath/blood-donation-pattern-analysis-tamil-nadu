"""Milestone 4: Data cleaning.

Each `clean_*` function takes a raw DataFrame and returns a cleaned one.
Keep these pure functions (no I/O) so they're easy to unit test —
I/O (reading raw, writing processed) stays in load.py / integrate.py.
"""

import numpy as np
import pandas as pd
from src.utils.config import CONFIG
from src.utils.logger import get_logger

log = get_logger(__name__)

THRESH = CONFIG["thresholds"]


def _strip_and_titlecase(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.title()


def clean_donors(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- normalize text columns ---
    for col in ["City", "State", "Country", "Blood_Group", "Donation_Center"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df["City"] = _strip_and_titlecase(df["City"])
    if "State" in df.columns:
        df["State"] = _strip_and_titlecase(df["State"])

    # --- parse dates ---
    for col in ["Registration_Date", "Last_Donation_Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    before = len(df)
    df = df[df["Registration_Date"].notna()]
    log.info(f"Dropped {before - len(df)} rows with unparseable Registration_Date")

    # Last_Donation_Date before Registration_Date is a logical error — null it out
    bad_order = df["Last_Donation_Date"] < df["Registration_Date"]
    log.info(f"Nulling {bad_order.sum()} Last_Donation_Date values earlier than registration")
    df.loc[bad_order, "Last_Donation_Date"] = pd.NaT

    # --- numeric columns ---
    for col in ["Age", "Total_Donations", "Weight_kg", "Hemoglobin_g_dL"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # plausible-range filtering (drop clearly corrupt rows, don't silently clip)
    df.loc[~df["Age"].between(16, 100), "Age"] = np.nan
    df.loc[~df["Weight_kg"].between(30, 200), "Weight_kg"] = np.nan
    df.loc[~df["Hemoglobin_g_dL"].between(3, 25), "Hemoglobin_g_dL"] = np.nan
    df.loc[df["Total_Donations"] < 0, "Total_Donations"] = np.nan
    df["Total_Donations"] = df["Total_Donations"].fillna(0).astype(int)

    # --- categorical normalization ---
    df["Gender"] = df["Gender"].astype(str).str.strip().str.upper().str[0]  # M/F/O
    df["Blood_Group"] = df["Blood_Group"].astype(str).str.strip().str.upper()
    valid_bg = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    df.loc[~df["Blood_Group"].isin(valid_bg), "Blood_Group"] = np.nan

    if "Eligible_for_Donation" in df.columns:
        df["Eligible_for_Donation"] = (
            df["Eligible_for_Donation"].astype(str).str.strip().str.upper()
            .map({"YES": True, "TRUE": True, "1": True,
                  "NO": False, "FALSE": False, "0": False})
        )

    # --- deduplicate ---
    before = len(df)
    df = df.drop_duplicates(subset=["Donor_ID"], keep="last")
    log.info(f"Dropped {before - len(df)} duplicate Donor_ID rows")

    log.info(f"clean_donors: {len(df)} rows remaining")
    return df.reset_index(drop=True)


def clean_blood_banks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in ["state", "city", "district"]:
        if col in df.columns:
            df[col] = _strip_and_titlecase(df[col])

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Tamil Nadu bounding box sanity check — catches swapped/garbage coordinates
    # (approx TN extent: lat 8-13.6, lon 76.2-80.5)
    valid_coords = df["latitude"].between(7.5, 14) & df["longitude"].between(75.5, 81)
    before = len(df)
    n_bad = (~valid_coords & df["latitude"].notna()).sum()
    log.info(f"{n_bad} blood banks have coordinates outside plausible TN bounding box "
             f"(kept, but flagged in `coord_valid` column)")
    df["coord_valid"] = valid_coords

    df = df.drop_duplicates(subset=["id"], keep="last") if "id" in df.columns else df.drop_duplicates()
    log.info(f"clean_blood_banks: {len(df)} rows remaining (dropped {before - len(df)} dupes)")
    return df.reset_index(drop=True)


def clean_tn_blood_banks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    if "Name of the District" in df.columns:
        df["Name of the District"] = _strip_and_titlecase(df["Name of the District"])
    df = df.drop_duplicates()
    return df.reset_index(drop=True)


def clean_population(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse the raw Census extract (sub-district/town/village granularity)
    down to one row per District with total/male/female population.

    Census 'Level' column typically has a District-total row (TRU='Total',
    Level='DISTRICT') — prefer that when present; otherwise aggregate.
    """
    df = df.copy()
    df["District"] = _strip_and_titlecase(df["District"])

    for col in ["TOT_P", "TOT_M", "TOT_F"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Prefer the pre-aggregated District-level row (avoids double counting
    # when town/village-level rows are also present in the same extract)
    if "Level" in df.columns:
        district_level = df[df["Level"].astype(str).str.upper() == "DISTRICT"]
        if len(district_level) > 0:
            df = district_level
        else:
            log.info("No 'DISTRICT' level rows found — summing all rows per district "
                     "(check for double-counting if sub-levels are present)")

    keep_cols = ["District", "TOT_P", "TOT_M", "TOT_F"]
    df = df[[c for c in keep_cols if c in df.columns]]

    district_pop = (
        df.groupby("District", as_index=False)[["TOT_P", "TOT_M", "TOT_F"]]
        .sum()
        .rename(columns={"TOT_P": "Population", "TOT_M": "Population_Male", "TOT_F": "Population_Female"})
    )
    log.info(f"clean_population: aggregated to {len(district_pop)} districts")
    return district_pop
