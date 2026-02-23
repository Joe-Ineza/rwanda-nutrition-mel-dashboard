# Streamlit quick start

## 1) Activate environment
```powershell
Set-Location "i:\Joe_Prsn\Irembo\New Positions\Monitoring and Evaluation\nutrition_mel_dashboard"
& "I:\Joe_Prsn\Irembo\New Positions\.venv\Scripts\Activate.ps1"
```

## 2) Ensure DB environment variables
- Keep `.env` in project root with:
  - `PGHOST`
  - `PGPORT`
  - `PGDATABASE`
  - `PGUSER`
  - `PGPASSWORD`
  - `PGSCHEMA`

## 3) Run app
```powershell
streamlit run .\app\streamlit_app.py
```

## 4) Dashboard tabs
- Latest Snapshot
- Trends
- Primary vs Adjusted
- Stratifier Comparison
- Data Notes

## 5) Demo flow (interview-ready)
1. Open Latest Snapshot and summarize current indicators.
2. Move to Trends and highlight change over time.
3. Show Primary vs Adjusted for comparability caveats.
4. Show Stratifier Comparison for equity lens.
5. Close with data caveats from Data Notes.
