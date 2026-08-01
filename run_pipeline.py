"""Orchestrates the full batch pipeline end to end:

    load -> clean -> integrate -> feature engineer -> temporal analysis
    -> spatial analysis -> BDPI -> recommendations -> write outputs

Run with: python run_pipeline.py

Each stage writes its intermediate output to data/processed/ so you can
resume from any point (and so notebooks can just read the parquet files
instead of recomputing everything).
"""

import pandas as pd
from src.utils.config import CONFIG, resolve_path
from src.utils.logger import get_logger

from src.data.load import load_donors, load_blood_banks, load_tn_blood_banks, load_population
from src.data.clean import clean_donors, clean_blood_banks, clean_tn_blood_banks, clean_population
from src.data.integrate import integrate_donors, integrate_blood_banks, build_district_summary
from src.features.temporal_features import add_temporal_features
from src.features.spatial_health_features import add_health_features, add_spatial_features
from src.temporal.trend_analysis import monthly_registration_trend, monthly_donation_activity_trend, seasonal_index
from src.spatial.clustering import dbscan_cluster
from src.recommendation.bdpi import compute_bdpi
from src.recommendation.engine import generate_recommendations

log = get_logger("pipeline")
PROCESSED_DIR = resolve_path(CONFIG["paths"]["processed_dir"])
PROCESSED_FILES = CONFIG["processed_files"]


def main():
    log.info("=== Stage 1/8: Load raw data ===")
    donors_raw = load_donors()
    blood_banks_raw = load_blood_banks()
    _tn_bb_raw = load_tn_blood_banks()  # used for cross-validation, not primary merge yet
    population_raw = load_population()

    log.info("=== Stage 2/8: Clean ===")
    donors = clean_donors(donors_raw)
    blood_banks = clean_blood_banks(blood_banks_raw)
    _tn_bb = clean_tn_blood_banks(_tn_bb_raw)
    population = clean_population(population_raw)

    log.info("=== Stage 3/8: Integrate (map to districts, merge population) ===")
    donors = integrate_donors(donors)
    blood_banks = integrate_blood_banks(blood_banks)
    district_summary = build_district_summary(donors, blood_banks, population)

    log.info("=== Stage 4/8: Feature engineering ===")
    donors = add_temporal_features(donors)
    donors = add_health_features(donors)
    donors = add_spatial_features(donors, district_summary)

    # fold recent-activity rate back into district_summary for BDPI
    recent_activity = donors.groupby("District")["Recent_Donor"].mean().rename("recent_activity_pct")
    district_summary = district_summary.merge(recent_activity, on="District", how="left")

    log.info("=== Stage 5/8: Temporal analysis ===")
    reg_trend = monthly_registration_trend(donors)
    donation_trend = monthly_donation_activity_trend(donors)
    season_idx = seasonal_index(donors)

    log.info("=== Stage 6/8: Spatial analysis ===")
    blood_banks_clustered = dbscan_cluster(blood_banks)

    log.info("=== Stage 7/8: BDPI + recommendations ===")
    bdpi_df = compute_bdpi(district_summary)
    recommendations = generate_recommendations(bdpi_df)

    log.info("=== Stage 8/8: Write outputs ===")
    donors.to_parquet(PROCESSED_DIR / PROCESSED_FILES["donors_enriched"], index=False)
    bdpi_df.to_parquet(PROCESSED_DIR / PROCESSED_FILES["district_summary"], index=False)
    recommendations.to_csv(PROCESSED_DIR / PROCESSED_FILES["district_recommendations"], index=False)
    reg_trend.to_csv(PROCESSED_DIR / "registration_trend.csv", index=False)
    donation_trend.to_csv(PROCESSED_DIR / "donation_trend.csv", index=False)
    season_idx.to_csv(PROCESSED_DIR / "seasonal_index.csv", index=False)
    blood_banks_clustered.to_parquet(PROCESSED_DIR / "blood_banks_clustered.parquet", index=False)

    log.info(f"Pipeline complete. Outputs written to {PROCESSED_DIR}")
    log.info(f"\nTop 5 priority districts:\n{recommendations.head(5).to_string(index=False)}")


if __name__ == "__main__":
    main()
