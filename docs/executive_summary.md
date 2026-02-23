# Executive Summary: Rwanda Child Nutrition MEL Dashboard

## Purpose
This dashboard provides a concise, evidence-oriented view of child nutrition patterns in Rwanda to support monitoring, learning, and decision-making for program and policy stakeholders.

It is designed to answer four core questions:
1. What is the latest burden level for key child nutrition indicators?
2. How are those indicators changing over time?
3. How different are primary versus age-adjusted estimates?
4. Are there meaningful disparities across stratifiers?

---

## Data Source and Scope
- **Primary source:** UNICEF/WHO/World Bank Joint Malnutrition Estimates (JME), Survey Estimates workbook (`jme_survey_estimates.xlsx`)
- **Sheets used:** `Primary Data`, `Age-Adjusted`, `Notes`, `Other Sources`
- **Country focus:** Rwanda
- **Population:** Children aged 0–59 months
- **Indicators included:**
  - Stunting
  - Wasting
  - Severe wasting
  - Overweight
  - Underweight

---

## How We Built It
- **Ingestion and cleaning:** Loaded workbook sheets with Python (`pandas`), normalized column names to snake_case, parsed numeric and time fields, and exported cleaned extracts for reproducibility.
- **Storage layer:** Loaded cleaned tables into PostgreSQL under a dedicated schema for consistent query performance and reuse.
- **Analytical modeling:** Created SQL views for (a) latest Rwanda snapshot, (b) indicator trends, (c) primary vs age-adjusted comparison, and (d) stratifier-level latest values.
- **Visualization layer:** Built a Streamlit dashboard with guided tabs, KPI cards, trend charts, method-comparison views, and downloadable filtered outputs.
- **Interpretation support:** Added contextual annotations (including 2021 reporting context) and concise insight callouts to improve stakeholder readability.

---

## What the Dashboard Shows
- **Overview tab:** Latest prevalence snapshot and year-over-year movement for key indicators.
- **Trends & Change tab:** Multi-year indicator trends and major directional shifts.
- **Method Comparison tab:** Primary vs age-adjusted estimate differences for selected indicators.
- **Equity (Stratifiers) tab:** Latest differences by stratifier to highlight potential inequities.
- **Definitions & Limitations tab:** Metric definitions and interpretation caveats.

---

## Key Interpretation Notes
- The dashboard reports prevalence percentages for under-five nutrition outcomes.
- A vertical marker in trend analysis indicates **2021**, when official global reporting for selected indicators shifted toward modeled estimates.
- Primary and age-adjusted values are intentionally shown side-by-side to support transparent interpretation and better analytical judgment.

---

## Value for Stakeholders
This dashboard supports:
- **Program management:** Rapid identification of priority indicators requiring action.
- **MEL and governance reviews:** Clear trend and variance analysis for evidence-based discussions.
- **Technical planning:** Better interpretation of estimate methodologies and data comparability.
- **Communication:** A single, consistent narrative for cross-functional and non-technical audiences.

---

## Recommended Use in Review Meetings
1. Start with **Overview** to align on current burden.
2. Move to **Trends & Change** to discuss progress or deterioration.
3. Use **Method Comparison** to contextualize estimate differences.
4. Close with **Equity (Stratifiers)** to prioritize targeted actions.

---

## Limitations and Caveats
- The dashboard currently reflects one primary JME source package for the MVP phase.
- Some trend interpretation depends on data availability and year coverage in the selected filters.
- Cross-source comparability should be treated cautiously when methodology differs.

---

## Suggested Next Enhancements
- Add additional JME source packages to broaden triangulation.
- Include automated “top three findings” text output per filter selection.
- Add downloadable monthly MEL brief templates for recurring governance cycles.

---

## Document Control
- **Prepared for:** Stakeholder review and presentation support
- **Project:** Nutrition MEL Dashboard (Rwanda)
- **Version:** 1.0
- **Date:** February 2026
