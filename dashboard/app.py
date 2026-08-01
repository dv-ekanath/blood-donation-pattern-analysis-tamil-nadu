"""Streamlit dashboard entry point.

Run with: streamlit run dashboard/app.py

Pages are implemented as functions rather than Streamlit's multipage
`pages/` folder convention, so state (loaded DataFrames) is shared cleanly
via st.session_state / caching without duplicating load logic per file.
Feel free to migrate to native multipage later if you prefer separate URLs.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))  # allow `import src.*`

from src.utils.config import CONFIG, resolve_path

st.set_page_config(page_title="TN Blood Donation Insights", layout="wide", page_icon="🩸")

PROCESSED_DIR = resolve_path(CONFIG["paths"]["processed_dir"])
PROCESSED_FILES = CONFIG["processed_files"]


@st.cache_data
def load_processed():
    """Loads the outputs of run_pipeline.py. Run that script first."""
    donors = pd.read_parquet(PROCESSED_DIR / PROCESSED_FILES["donors_enriched"])
    district_summary = pd.read_parquet(PROCESSED_DIR / PROCESSED_FILES["district_summary"])
    recommendations = pd.read_csv(PROCESSED_DIR / PROCESSED_FILES["district_recommendations"])
    reg_trend = pd.read_csv(PROCESSED_DIR / "registration_trend.csv", parse_dates=["month"])
    donation_trend = pd.read_csv(PROCESSED_DIR / "donation_trend.csv", parse_dates=["month"])
    season_idx = pd.read_csv(PROCESSED_DIR / "seasonal_index.csv")
    return donors, district_summary, recommendations, reg_trend, donation_trend, season_idx


def main():
    st.sidebar.title("🩸 TN Blood Donation Insights")
    page = st.sidebar.radio(
        "Navigate",
        ["Home", "EDA", "Temporal Analysis", "Spatial Analysis", "Recommendations"],
    )

    try:
        donors, district_summary, recommendations, reg_trend, donation_trend, season_idx = load_processed()
    except FileNotFoundError as e:
        st.error(
            f"Processed data not found ({e}).\n\n"
            f"Run `python run_pipeline.py` from the project root first to "
            f"generate the files this dashboard reads."
        )
        st.stop()

    if page == "Home":
        from dashboard.pages import home
        home.render(donors, district_summary, recommendations)
    elif page == "EDA":
        from dashboard.pages import eda
        eda.render(donors)
    elif page == "Temporal Analysis":
        from dashboard.pages import temporal
        temporal.render(reg_trend, donation_trend, season_idx)
    elif page == "Spatial Analysis":
        from dashboard.pages import spatial
        spatial.render(district_summary)
    elif page == "Recommendations":
        from dashboard.pages import recommendations_page
        recommendations_page.render(recommendations, district_summary)


if __name__ == "__main__":
    main()
