# Blood Donation Pattern Analysis and Donation Drive Recommendation System — Tamil Nadu

M.Tech (Integrated) course project for **Sequential and Spatial Data Mining**.

Analyzes donor registration/donation data and blood bank distribution across
Tamil Nadu to surface temporal and spatial patterns, and recommends districts
and time periods for future donation drives via a custom **Blood Donation
Priority Index (BDPI)**.

> Note: the donor dataset has no per-event donation history (only
> `Registration_Date`, `Last_Donation_Date`, `Total_Donations`), so the
> "sequential" component is implemented as **temporal data mining**
> (trend/seasonality/recency analysis, forecasting) rather than classical
> sequential pattern mining (PrefixSpan/SPADE/GSP). This is a deliberate,
> documented scope decision — see `reports/scope_note.md`.

## Project Structure

```
├── data/
│   ├── raw/            # original CSVs, untouched (gitignored except .gitkeep)
│   ├── processed/       # cleaned + integrated datasets (gitignored)
│   └── external/        # e.g. Tamil Nadu district GeoJSON boundaries
├── notebooks/            # exploration only — logic gets promoted to src/
├── src/
│   ├── data/             # loading, cleaning, integration
│   ├── features/         # temporal, spatial, health feature engineering
│   ├── temporal/         # trend, seasonality, forecasting
│   ├── spatial/           # DBSCAN, KDE, geopandas/folium helpers
│   ├── recommendation/    # BDPI + recommendation engine
│   └── utils/              # config, io, logging helpers
├── dashboard/             # Streamlit app
├── reports/
│   └── figures/            # exported charts/maps for the report
├── tests/                  # unit tests for src/ modules
├── config.yaml              # paths, weights, column-name mappings
├── requirements.txt
└── run_pipeline.py          # orchestrates the full batch pipeline
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Place the four raw CSVs into `data/raw/` using these exact filenames
(or update `config.yaml`):

```
data/raw/blood_donation_portal.csv
data/raw/blood_bank_directory.csv
data/raw/tn_blood_banks.csv
data/raw/population_census.csv
```

## Running the pipeline

```bash
python run_pipeline.py
```

This runs: clean → integrate → engineer features → temporal analysis →
spatial analysis → BDPI → recommendations, writing outputs to
`data/processed/` and `reports/`.

## Running the dashboard

```bash
streamlit run dashboard/app.py
```

## Milestones (tracked as GitHub issues / commits)

- [x] 1. Project setup
- [x] 2. Dataset import
- [ ] 3. Data inspection
- [ ] 4. Data cleaning
- [ ] 5. Data integration
- [ ] 6. Feature engineering
- [ ] 7. Exploratory Data Analysis
- [ ] 8. Temporal analysis
- [ ] 9. Spatial analysis
- [ ] 10. Blood Donation Priority Index
- [ ] 11. Recommendation engine
- [ ] 12. Streamlit dashboard
- [ ] 13. Documentation
- [ ] 14. Final testing
