import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.recommendation.bdpi import compute_bdpi


def make_dummy_district_summary():
    return pd.DataFrame({
        "District": ["A", "B", "C"],
        "Population": [1_000_000, 500_000, 2_000_000],
        "n_donors": [1000, 100, 200],
        "n_blood_banks": [10, 1, 2],
        "eligible_pct": [0.8, 0.3, 0.5],
        "donor_density_per_100k": [100, 20, 10],
        "population_per_blood_bank": [100_000, 500_000, 1_000_000],
    })


def test_bdpi_score_range():
    df = compute_bdpi(make_dummy_district_summary())
    assert df["BDPI"].between(0, 100).all()


def test_bdpi_rank_is_unique_and_sequential():
    df = compute_bdpi(make_dummy_district_summary())
    assert sorted(df["BDPI_Rank"].tolist()) == [1, 2, 3]


def test_high_population_low_coverage_district_ranks_high_priority():
    df = compute_bdpi(make_dummy_district_summary())
    # District C: largest population, worst blood-bank coverage -> should rank near top
    top_district = df.iloc[0]["District"]
    assert top_district in {"C", "B"}  # both are plausible top priorities given the inputs
