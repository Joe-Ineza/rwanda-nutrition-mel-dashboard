# Nutrition MEL Streamlit Project (MVP)

This project ingests UNICEF/WHO/World Bank JME survey estimates from `jme_survey_estimates.xlsx`, loads cleaned tables into PostgreSQL, and serves a Rwanda-first MEL dashboard in Streamlit.

## Executive Summary
- **Objective:** Provide a concise MEL view of child nutrition outcomes in Rwanda for monitoring, learning, and decision support.
- **Questions answered:** latest burden, trend direction, primary vs age-adjusted differences, and stratifier disparities.
- **How it was built:** Python ingestion/cleaning pipeline, PostgreSQL storage, SQL analytical views, and Streamlit dashboard with guided tabs and insight callouts.
- **Stakeholder value:** Faster evidence review for governance discussions, clearer interpretation of indicator movement, and improved communication to non-technical audiences.
- **Important caveat:** Dashboard reflects the current MVP source package and should be interpreted with methodology/coverage context.

Full stakeholder brief: [docs/executive_summary.md](docs/executive_summary.md)

## Current scope (source 1)
- Workbook: `Interesting Datasets/jme_survey_estimates.xlsx`
- Sheets ingested:
  - `Primary Data`
  - `Age-Adjusted`
  - `Notes`
  - `Other Sources`

## Project structure
- `scripts/ingest_jme_survey_estimates.py` – Excel ingestion, cleaning, optional PostgreSQL load
- `sql/01_quality_checks.sql` – quick validation queries
- `sql/02_metabase_views.sql` – Rwanda-focused starter views
- `data/processed/*.csv` – cleaned outputs
- `app/streamlit_app.py` – interactive Streamlit dashboard
- `docs/metabase_setup.md` – first dashboard setup steps

## Setup
1. Ensure Python environment is configured.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. (Optional DB load) Copy `.env.example` to `.env` and fill PostgreSQL credentials.

## Run ingestion
```bash
python scripts/ingest_jme_survey_estimates.py --input "../Interesting Datasets/jme_survey_estimates.xlsx" --output-dir data/processed
```

## Load into PostgreSQL
```bash
python scripts/ingest_jme_survey_estimates.py --input "../Interesting Datasets/jme_survey_estimates.xlsx" --output-dir data/processed --load-db
```

## Apply SQL assets
- Run `sql/02_metabase_views.sql` in your PostgreSQL database.
- Run `sql/01_quality_checks.sql` to validate loaded data.

## Run Streamlit dashboard
```bash
streamlit run app/streamlit_app.py
```

## Dashboard modules (single-source MVP)
- Latest Rwanda snapshot
- Indicator trends (primary data)
- Primary vs age-adjusted comparison
- Latest stratifier comparison
- Indicator definitions and caveats

## Notes
- Column names are normalized to snake_case.
- Numeric indicators are parsed as numeric where possible.
- `Age-Adjusted` and `Primary Data` are kept separate for transparent comparison.
