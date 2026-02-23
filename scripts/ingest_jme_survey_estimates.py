from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os


def normalize_column_name(column_name: str) -> str:
    value = column_name.strip().lower()
    value = value.replace("*", "")
    value = value.replace("('000s)", "_thousands")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [normalize_column_name(c) for c in cleaned.columns]

    if "year" in cleaned.columns:
        cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce").astype("Int64")

    numeric_columns = {
        "whz_survey_sample_n",
        "haz_survey_sample_n",
        "waz_survey_sample_n",
        "severe_wasting",
        "wasting",
        "overweight",
        "stunting",
        "underweight",
        "u5_population_thousands",
    }

    for column in numeric_columns.intersection(set(cleaned.columns)):
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    for column in ["survey_year", "fieldwork_period", "country_and_areas", "stratifier", "type_of_estimate"]:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype("string").str.strip()

    return cleaned


def load_workbook(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    primary = pd.read_excel(path, sheet_name="Primary Data")
    adjusted = pd.read_excel(path, sheet_name="Age-Adjusted")
    notes = pd.read_excel(path, sheet_name="Notes")
    other_sources = pd.read_excel(path, sheet_name="Other Sources")

    primary = clean_dataframe(primary)
    adjusted = clean_dataframe(adjusted)
    notes = clean_dataframe(notes)
    other_sources = clean_dataframe(other_sources)

    primary["data_source_sheet"] = "Primary Data"
    adjusted["data_source_sheet"] = "Age-Adjusted"

    return primary, adjusted, notes, other_sources


def export_processed(primary: pd.DataFrame, adjusted: pd.DataFrame, notes: pd.DataFrame, other_sources: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    primary.to_csv(output_dir / "primary_data_clean.csv", index=False)
    adjusted.to_csv(output_dir / "age_adjusted_clean.csv", index=False)
    notes.to_csv(output_dir / "notes_clean.csv", index=False)
    other_sources.to_csv(output_dir / "other_sources_clean.csv", index=False)



def get_engine_from_env() -> tuple[str, object]:
    load_dotenv()
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT", "5432")
    db = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    pwd = os.getenv("PGPASSWORD")
    schema = os.getenv("PGSCHEMA", "nutrition")

    missing = [k for k, v in {
        "PGHOST": host,
        "PGDATABASE": db,
        "PGUSER": user,
        "PGPASSWORD": pwd,
    }.items() if not v]

    if missing:
        raise ValueError(f"Missing environment variables for DB load: {', '.join(missing)}")

    engine = create_engine(f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}")
    return schema, engine



def write_to_postgres(primary: pd.DataFrame, adjusted: pd.DataFrame, notes: pd.DataFrame, other_sources: pd.DataFrame) -> None:
    schema, engine = get_engine_from_env()
    with engine.begin() as connection:
        connection.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema};")

    primary.to_sql("raw_primary_data", engine, schema=schema, if_exists="replace", index=False)
    adjusted.to_sql("raw_age_adjusted", engine, schema=schema, if_exists="replace", index=False)
    notes.to_sql("raw_notes", engine, schema=schema, if_exists="replace", index=False)
    other_sources.to_sql("raw_other_sources", engine, schema=schema, if_exists="replace", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest JME survey estimates workbook into clean files and optional PostgreSQL tables.")
    parser.add_argument("--input", required=True, help="Path to jme_survey_estimates.xlsx")
    parser.add_argument("--output-dir", default="data/processed", help="Output directory for cleaned CSV files")
    parser.add_argument("--load-db", action="store_true", help="Load cleaned data into PostgreSQL using .env variables")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Workbook not found: {input_path}")

    primary, adjusted, notes, other_sources = load_workbook(input_path)
    export_processed(primary, adjusted, notes, other_sources, output_dir)

    if args.load_db:
        write_to_postgres(primary, adjusted, notes, other_sources)

    print("Ingestion complete")
    print(f"Primary rows: {len(primary):,}")
    print(f"Age-adjusted rows: {len(adjusted):,}")
    print(f"Notes rows: {len(notes):,}")
    print(f"Other sources rows: {len(other_sources):,}")


if __name__ == "__main__":
    main()
