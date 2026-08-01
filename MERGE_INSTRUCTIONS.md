# How to merge this into your existing repo

You already have an initial commit + datasets in
`dv-ekanath/blood-donation-pattern-analysis-tamil-nadu`. Don't overwrite
your data files — copy this scaffold in around them.

```bash
cd blood-donation-pattern-analysis-tamil-nadu

# 1. Copy everything from this scaffold except data/
cp -r /path/to/scaffold/src .
cp -r /path/to/scaffold/dashboard .
cp -r /path/to/scaffold/notebooks .
cp -r /path/to/scaffold/tests .
cp /path/to/scaffold/reports/scope_note.md reports/ 2>/dev/null || (mkdir -p reports/figures && cp /path/to/scaffold/reports/scope_note.md reports/)
cp /path/to/scaffold/config.yaml .
cp /path/to/scaffold/requirements.txt .
cp /path/to/scaffold/run_pipeline.py .
cp /path/to/scaffold/MERGE_INSTRUCTIONS.md .   # delete after merging, it's a one-time doc

# 2. Merge .gitignore (don't overwrite if you already have entries you want)
cat /path/to/scaffold/.gitignore >> .gitignore

# 3. Rename your existing raw CSVs to match config.yaml's raw_files
#    (or edit config.yaml to match your actual filenames — that's easier)
mv "<your donor csv>"        data/raw/blood_donation_portal.csv
mv "<your blood bank csv>"   data/raw/blood_bank_directory.csv
mv "<your TN blood bank csv>" data/raw/tn_blood_banks.csv
mv "<your population csv>"   data/raw/population_census.csv

# 4. Install deps and do a first run
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py

# 5. Commit in milestone-sized chunks, matching your own plan
git add src/data config.yaml requirements.txt
git commit -m "Milestone 3-4: data loading and cleaning modules"

git add src/data/integrate.py
git commit -m "Milestone 5: data integration (district mapping, merge)"

git add src/features
git commit -m "Milestone 6: temporal, spatial, and health feature engineering"

git add notebooks/
git commit -m "Milestone 3/7: inspection notebook + EDA scaffolding"

git add src/temporal
git commit -m "Milestone 8: temporal trend analysis and forecasting"

git add src/spatial
git commit -m "Milestone 9: DBSCAN clustering, KDE, folium maps"

git add src/recommendation
git commit -m "Milestone 10-11: BDPI and recommendation engine"

git add run_pipeline.py
git commit -m "Add pipeline orchestrator tying all stages together"

git add dashboard
git commit -m "Milestone 12: Streamlit dashboard"

git add tests
git commit -m "Milestone 14: unit tests for cleaning and BDPI logic"

git add reports/scope_note.md README.md
git commit -m "Milestone 13: documentation - scope note and README"

git push
```

Delete this file once merged — it's not part of the project itself.
