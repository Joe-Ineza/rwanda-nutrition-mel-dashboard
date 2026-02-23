# Metabase setup (Rwanda nutrition MVP)

## 1) Connect PostgreSQL
- In Metabase: **Admin settings → Databases → Add database**
- Engine: PostgreSQL
- Use `.env` values: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`
- Schema to expose: `nutrition`

## 2) Use these starter views
- `nutrition.vw_rwanda_latest_nutrition_snapshot`
- `nutrition.vw_rwanda_trends_primary`
- `nutrition.vw_rwanda_trends_adjusted_vs_primary`

## 3) Build first 4 cards
1. Latest stunting, wasting, severe wasting, overweight, underweight (table or score cards)
2. Trend line by year for `stunting`, `wasting`, `overweight`
3. Adjusted vs primary (wasting, severe wasting, underweight)
4. Estimated affected children (`est_stunted_thousands`, `est_wasted_thousands`, `est_overweight_thousands`)

## 4) Suggested dashboard filters
- Year
- Stratifier
- Type of Estimate

## 5) Recommended naming convention
- Collection: `Rwanda Nutrition MEL`
- Dashboard: `Rwanda Child Nutrition Snapshot`
- Cards prefix: `RWA - ...`
