from __future__ import annotations

import os
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


st.set_page_config(
    page_title="Rwanda Nutrition MEL Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_resource
def get_engine():
    load_dotenv()
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    db = os.getenv("PGDATABASE", "nutrition_mel")
    user = os.getenv("PGUSER", "postgres")
    pwd = os.getenv("PGPASSWORD", "")
    sslmode = os.getenv("PGSSLMODE", "require")
    channel_binding = os.getenv("PGCHANNELBINDING", "prefer")

    if not pwd:
        st.error("PGPASSWORD is missing. Add it in .env before launching Streamlit.")
        st.stop()

    db_url = URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=pwd,
        host=host,
        port=int(port),
        database=db,
        query={"sslmode": sslmode, "channel_binding": channel_binding},
    )

    return create_engine(db_url)


@st.cache_data(ttl=300)
def load_table(query_text: str, params: dict | None = None) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as connection:
        return pd.read_sql_query(text(query_text), connection, params=params)


INDICATORS = [
    "stunting",
    "wasting",
    "severe_wasting",
    "overweight",
    "underweight",
]


DISPLAY_NAMES = {
    "stunting": "Stunting (%)",
    "wasting": "Wasting (%)",
    "severe_wasting": "Severe Wasting (%)",
    "overweight": "Overweight (%)",
    "underweight": "Underweight (%)",
}


INDICATOR_COLORS = {
    "Stunting (%)": "#d62728",
    "Wasting (%)": "#ff7f0e",
    "Severe Wasting (%)": "#9467bd",
    "Overweight (%)": "#1f77b4",
    "Underweight (%)": "#2ca02c",
}


def to_long(df: pd.DataFrame, indicator_columns: Iterable[str]) -> pd.DataFrame:
    return df.melt(
        id_vars=[c for c in df.columns if c not in indicator_columns],
        value_vars=list(indicator_columns),
        var_name="indicator",
        value_name="value",
    )


def format_metric(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{value:.1f}%"


def pretty_indicator(value: str) -> str:
    return DISPLAY_NAMES.get(value, value.replace("_", " ").title())


def yoy_delta(df: pd.DataFrame, metric: str) -> str:
    if metric not in df.columns:
        return "n/a"
    series = df[["year", metric]].dropna().sort_values("year")
    if len(series) < 2:
        return "n/a"
    delta = float(series.iloc[-1][metric] - series.iloc[-2][metric])
    if delta > 0:
        marker = "▲"
    elif delta < 0:
        marker = "▼"
    else:
        marker = "•"
    return f"{marker} {delta:+.1f} pp vs previous year"


def summarize_trend_change(trend_long: pd.DataFrame) -> str:
    if trend_long.empty:
        return "No trend insight available for current filter selection."
    pivot = trend_long.groupby(["indicator", "year"], as_index=False)["value"].mean()
    rows = []
    for indicator in pivot["indicator"].dropna().unique():
        section = pivot[pivot["indicator"] == indicator].sort_values("year")
        if len(section) >= 2:
            delta = float(section.iloc[-1]["value"] - section.iloc[0]["value"])
            rows.append((indicator, delta))
    if not rows:
        return "Insufficient years to compute end-to-end indicator change."
    indicator, delta = max(rows, key=lambda item: abs(item[1]))
    direction = "increased" if delta > 0 else "decreased" if delta < 0 else "was unchanged"
    return f"Largest net shift: {indicator} {direction} by {abs(delta):.1f} percentage points across selected years."


def summarize_method_gap(adjusted_frame: pd.DataFrame, primary_col: str, adjusted_col: str) -> str:
    compare = adjusted_frame[[primary_col, adjusted_col]].dropna()
    if compare.empty:
        return "No overlapping observations for the selected primary vs adjusted metric."
    gap = (compare[adjusted_col] - compare[primary_col]).abs().mean()
    metric_name = primary_col.replace("primary_", "").replace("_", " ").title()
    return f"Average absolute gap between primary and adjusted {metric_name} is {gap:.2f} percentage points."


def summarize_stratifier_gap(plot_df: pd.DataFrame, metric_label: str) -> str:
    if plot_df.empty or plot_df[metric_label].isna().all():
        return "No stratifier gap insight available for this metric."
    spread = float(plot_df[metric_label].max() - plot_df[metric_label].min())
    high_row = plot_df.loc[plot_df[metric_label].idxmax()]
    low_row = plot_df.loc[plot_df[metric_label].idxmin()]
    return (
        f"Gap between highest and lowest stratifier is {spread:.1f} percentage points "
        f"({high_row['stratifier']} vs {low_row['stratifier']})."
    )


def main() -> None:
    st.title("Rwanda Child Nutrition MEL Dashboard")
    st.markdown(
        "Source: [JME survey estimates workbook (Primary Data + Age-Adjusted)](https://data.unicef.org/resources/dataset/malnutrition-data/)"
    )

    with st.expander("How to read this dashboard", expanded=True):
        st.markdown(
            """
This dashboard helps answer four questions:
1. What is the latest burden level for core child nutrition indicators in Rwanda?
2. Are outcomes improving or worsening over time?
3. How different are primary and age-adjusted estimates?
4. Are there meaningful differences across stratifiers?
            """
        )

    latest = load_table("SELECT * FROM nutrition.vw_rwanda_latest_nutrition_snapshot")
    trends = load_table("SELECT * FROM nutrition.vw_rwanda_trends_primary")
    adjusted = load_table("SELECT * FROM nutrition.vw_rwanda_trends_adjusted_vs_primary")
    stratifier_latest = load_table("SELECT * FROM nutrition.vw_rwanda_latest_by_stratifier")

    with st.sidebar:
        st.header("Filters")
        available_years = sorted([y for y in trends["year"].dropna().unique().tolist()], reverse=True)
        selected_years = st.multiselect(
            "Year",
            options=available_years,
            default=available_years,
        )
        selected_indicators = st.multiselect(
            "Indicators",
            options=INDICATORS,
            default=["stunting", "wasting", "overweight"],
            format_func=lambda value: DISPLAY_NAMES[value],
        )

    badge_cols = st.columns(3)
    badge_cols[0].metric("Years Available", f"{len(available_years)}")
    badge_cols[1].metric("Latest Year", f"{max(available_years) if available_years else '-'}")
    badge_cols[2].metric("Indicators Selected", f"{len(selected_indicators)}")

    if selected_years:
        trends = trends[trends["year"].isin(selected_years)]
        adjusted = adjusted[adjusted["year"].isin(selected_years)]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Overview",
            "Trends & Change",
            "Method Comparison",
            "Equity (Stratifiers)",
            "Definitions & Limitations",
        ]
    )

    with tab1:
        st.subheader("Latest Rwanda Snapshot")
        snapshot = latest.sort_values(["year", "stratifier"], ascending=[False, True]).copy()
        total_row = snapshot[snapshot["stratifier"].str.lower() == "total"]
        if not total_row.empty:
            row = total_row.iloc[0]
            metric_cols = st.columns(5)
            metric_cols[0].metric("Stunting", format_metric(row.get("stunting")), yoy_delta(trends, "stunting"))
            metric_cols[1].metric("Wasting", format_metric(row.get("wasting")), yoy_delta(trends, "wasting"))
            metric_cols[2].metric("Underweight", format_metric(row.get("underweight")), yoy_delta(trends, "underweight"))
            metric_cols[3].metric("Severe Wasting", format_metric(row.get("severe_wasting")), yoy_delta(trends, "severe_wasting"))
            metric_cols[4].metric("Overweight", format_metric(row.get("overweight")), yoy_delta(trends, "overweight"))

            priority_values = {
                "Stunting": row.get("stunting"),
                "Wasting": row.get("wasting"),
                "Underweight": row.get("underweight"),
                "Severe Wasting": row.get("severe_wasting"),
                "Overweight": row.get("overweight"),
            }
            valid_values = {k: v for k, v in priority_values.items() if v is not None and not pd.isna(v)}
            if valid_values:
                top_metric = max(valid_values, key=valid_values.get)
                st.info(f"Snapshot insight: Highest latest prevalence is {top_metric} at {valid_values[top_metric]:.1f}%.")
        with st.expander("Show underlying snapshot data"):
            st.dataframe(snapshot, use_container_width=True)

    with tab2:
        st.subheader("Indicator Trends (Primary Data)")
        if not selected_indicators:
            st.warning("Select at least one indicator from the sidebar.")
        elif trends.empty:
            st.info("No trend data for selected filters.")
        else:
            trend_long = to_long(trends, selected_indicators)
            trend_long = trend_long.dropna(subset=["value"])
            trend_long["indicator"] = trend_long["indicator"].map(pretty_indicator)
            chart = px.line(
                trend_long,
                x="year",
                y="value",
                color="indicator",
                markers=True,
                title="Rwanda trends by indicator",
                labels={"value": "Prevalence (%)", "year": "Year", "indicator": "Indicator"},
                color_discrete_map=INDICATOR_COLORS,
            )
            chart.add_vline(x=2021, line_dash="dash", line_color="gray")
            st.plotly_chart(chart, use_container_width=True)
            st.info(summarize_trend_change(trend_long))
            st.caption("Dashed line at 2021: global reporting shifted to modeled estimates for stunting/overweight.")
            with st.expander("Show underlying trend data"):
                st.dataframe(trends, use_container_width=True)

    with tab3:
        st.subheader("Primary vs Age-Adjusted (Wasting, Severe Wasting, Underweight)")
        if adjusted.empty:
            st.info("No adjusted comparison data for selected filters.")
        else:
            metric_name = st.selectbox(
                "Comparison metric",
                options=[
                    ("primary_wasting", "adjusted_wasting"),
                    ("primary_severe_wasting", "adjusted_severe_wasting"),
                    ("primary_underweight", "adjusted_underweight"),
                ],
                format_func=lambda value: value[0].replace("primary_", "").replace("_", " ").title(),
            )
            plot_df = adjusted[["year", metric_name[0], metric_name[1]]].copy()
            plot_df = plot_df.melt(id_vars=["year"], var_name="series", value_name="value")
            series_labels = {
                metric_name[0]: "Primary",
                metric_name[1]: "Age-Adjusted",
            }
            plot_df["series"] = plot_df["series"].map(series_labels)
            plot_df = plot_df.dropna(subset=["value"])
            compare_chart = px.line(
                plot_df,
                x="year",
                y="value",
                color="series",
                markers=True,
                labels={"value": "Prevalence (%)", "year": "Year", "series": "Series"},
                color_discrete_map={"Primary": "#1f77b4", "Age-Adjusted": "#d62728"},
            )
            st.plotly_chart(compare_chart, use_container_width=True)
            st.info(summarize_method_gap(adjusted, metric_name[0], metric_name[1]))
            with st.expander("Show underlying method comparison data"):
                st.dataframe(adjusted, use_container_width=True)

    with tab4:
        st.subheader("Latest by Stratifier")
        if stratifier_latest.empty:
            st.info("No stratifier data available.")
        else:
            metric = st.selectbox(
                "Stratifier metric",
                options=INDICATORS,
                format_func=lambda value: DISPLAY_NAMES[value],
                key="strat_metric",
            )
            plot_df = stratifier_latest[["stratifier", "year", metric]].dropna(subset=[metric]).copy()
            plot_df = plot_df.sort_values(metric, ascending=False)
            metric_label = DISPLAY_NAMES[metric]
            plot_df = plot_df.rename(columns={metric: metric_label})
            bar = px.bar(
                plot_df,
                x="stratifier",
                y=metric_label,
                color="stratifier",
                labels={metric_label: "Prevalence (%)", "stratifier": "Stratifier"},
                title=f"Latest Rwanda {metric_label} by stratifier",
            )
            st.plotly_chart(bar, use_container_width=True)
            st.info(summarize_stratifier_gap(plot_df, metric_label))
            with st.expander("Show underlying stratifier data"):
                st.dataframe(stratifier_latest, use_container_width=True)

    with tab5:
        st.subheader("Indicator Definitions & Notes")
        st.markdown(
            """
- Stunting: Height-for-age below -2 SD of WHO Child Growth Standards.
- Wasting: Weight-for-height below -2 SD.
- Severe wasting: Weight-for-height below -3 SD.
- Overweight: Weight-for-height above +2 SD.
- Underweight: Weight-for-age below -2 SD.

Data caveat:
- From 2021, modeled estimates replaced primary source estimates for official stunting/overweight reporting.
- This dashboard currently uses Source #3 workbook sheets (`Primary Data`, `Age-Adjusted`) for project MVP.
            """
        )

    st.download_button(
        label="Download current trend table as CSV",
        data=trends.to_csv(index=False).encode("utf-8"),
        file_name="rwanda_nutrition_trends_primary.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
