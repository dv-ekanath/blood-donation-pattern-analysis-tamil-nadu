import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data.clean import clean_donors, clean_population


def make_dummy_donors():
    return pd.DataFrame({
        "Donor_ID": [1, 2, 3, 3],  # 3 is a duplicate
        "Full_Name": ["A", "B", "C", "C"],
        "Gender": ["male", "Female", "M", "M"],
        "Age": [25, 200, 30, 30],           # 200 is invalid
        "Blood_Group": ["O+", "XX", "A-", "A-"],  # XX is invalid
        "City": [" chennai ", "madurai", "Coimbatore", "Coimbatore"],
        "State": ["Tamil Nadu"] * 4,
        "Country": ["India"] * 4,
        "Last_Donation_Date": ["2023-01-01", "2020-05-01", "2019-01-01", "2019-01-01"],
        "Total_Donations": [3, 1, -5, -5],   # -5 invalid
        "Eligible_for_Donation": ["Yes", "No", "Yes", "Yes"],
        "Medical_Condition": ["None", "Diabetes", "None", "None"],
        "Weight_kg": [60, 55, 500, 500],     # 500 invalid
        "Hemoglobin_g_dL": [13.5, 12.0, 14.0, 14.0],
        "Donation_Center": ["X", "Y", "Z", "Z"],
        "Registration_Date": ["2022-01-01", "2019-01-01", "2020-01-01", "2020-01-01"],
    })


def test_clean_donors_drops_duplicates():
    df = clean_donors(make_dummy_donors())
    assert df["Donor_ID"].is_unique


def test_clean_donors_nulls_invalid_ranges():
    df = clean_donors(make_dummy_donors())
    assert df.loc[df["Donor_ID"] == 2, "Age"].isna().all()          # 200 -> NaN
    row3 = df[df["Donor_ID"] == 3]
    assert row3["Weight_kg"].isna().all()                            # 500 -> NaN


def test_clean_donors_invalid_blood_group_nulled():
    df = clean_donors(make_dummy_donors())
    assert df.loc[df["Donor_ID"] == 2, "Blood_Group"].isna().all()


def test_clean_population_aggregates_per_district():
    pop = pd.DataFrame({
        "District": ["Chennai", "Chennai", "Madurai"],
        "TOT_P": [100, 200, 50],
        "TOT_M": [50, 100, 25],
        "TOT_F": [50, 100, 25],
    })
    result = clean_population(pop)
    assert set(result["District"]) == {"Chennai", "Madurai"}
    assert result.loc[result["District"] == "Chennai", "Population"].iloc[0] == 300
