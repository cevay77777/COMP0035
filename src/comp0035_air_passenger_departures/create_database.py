"""
Create and populate an SQLite database using the air passenger departure CSV files.

Run:
    python -m src.create_database
"""

from pathlib import Path
import sqlite3
import pandas as pd
from . import db_schema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "air_passenger_departures.db"


# ------------------------------------------------------------
# LOAD & CLEAN
# ------------------------------------------------------------
def load_and_clean():
    """Load and clean the raw CSV files."""
    global_df = pd.read_csv(DATA_RAW_DIR / "TotalAirPassengerDepartures.csv")
    region_df = pd.read_csv(DATA_RAW_DIR / "TotalAirPassengerDeparturesbyRegion.csv")
    country_df = pd.read_csv(DATA_RAW_DIR / "TotalAirPassengerDeparturesbyCountry.csv")

    # Convert month to YYYY-MM string and value to numeric
    for df in (global_df, region_df, country_df):
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["month"] = df["month"].dt.strftime("%Y-%m")

    return global_df, region_df, country_df


# ------------------------------------------------------------
# DIMENSION TABLES
# ------------------------------------------------------------
def extract_dimensions(region_df, country_df):
    """Create Region and Country dimension tables."""

    # Build unique Region list
    region_names = (
        pd.concat([region_df["level_2"], country_df["level_2"]])
        .dropna()
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    region_dim = pd.DataFrame({
        "region_id": range(1, len(region_names) + 1),
        "region_name": region_names
    })

    # Map region_name → region_id
    region_id_map = dict(zip(region_dim["region_name"], region_dim["region_id"]))

    # Build Country dimension
    countries = (
        country_df[["level_3", "level_2"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"level_3": "country_name", "level_2": "region_name"})
        .reset_index(drop=True)
    )

    countries["region_id"] = countries["region_name"].map(region_id_map)

    country_dim = pd.DataFrame({
        "country_id": range(1, len(countries) + 1),
        "country_name": countries["country_name"],
        "region_id": countries["region_id"]
    })

    # Map country_name → country_id
    country_id_map = dict(zip(country_dim["country_name"], country_dim["country_id"]))

    return region_dim, country_dim, region_id_map, country_id_map


# ------------------------------------------------------------
# CREATE DATABASE
# ------------------------------------------------------------
def create_database():
    print("Loading and cleaning data...")
    global_df, region_df, country_df = load_and_clean()

    print("Extracting dimension tables...")
    region_dim, country_dim, region_id_map, country_id_map = extract_dimensions(region_df, country_df)

    # Build Regional fact table
    regional_facts = pd.DataFrame({
        "month": region_df["month"],
        "region_id": region_df["level_2"].map(region_id_map),
        "value": region_df["value"],
    }).dropna(subset=["region_id"])

    # Build Country fact table
    country_facts = pd.DataFrame({
        "month": country_df["month"],
        "country_id": country_df["level_3"].map(country_id_map),
        "value": country_df["value"],
    }).dropna(subset=["country_id"])

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        print("Creating tables...")
        cursor.execute(db_schema.CREATE_REGION_TABLE)
        cursor.execute(db_schema.CREATE_COUNTRY_TABLE)
        cursor.execute(db_schema.CREATE_GLOBAL_DEPARTURES_TABLE)
        cursor.execute(db_schema.CREATE_REGIONAL_DEPARTURES_TABLE)
        cursor.execute(db_schema.CREATE_COUNTRY_DEPARTURES_TABLE)

        print("Inserting Region dimension...")
        cursor.executemany(
            "INSERT INTO Region (region_id, region_name) VALUES (?, ?);",
            list(region_dim.itertuples(index=False, name=None))
        )

        print("Inserting Country dimension...")
        cursor.executemany(
            "INSERT INTO Country (country_id, country_name, region_id) VALUES (?, ?, ?);",
            list(country_dim.itertuples(index=False, name=None))
        )

        print("Inserting GlobalDepartures...")
        cursor.executemany(
            "INSERT INTO GlobalDepartures (month, value) VALUES (?, ?);",
            list(global_df[["month", "value"]].itertuples(index=False, name=None))
        )

        print("Inserting RegionalDepartures...")
        cursor.executemany(
            "INSERT INTO RegionalDepartures (month, region_id, value) VALUES (?, ?, ?);",
            list(regional_facts[["month", "region_id", "value"]].itertuples(index=False, name=None))
        )

        print("Inserting CountryDepartures...")
        cursor.executemany(
            "INSERT INTO CountryDepartures (month, country_id, value) VALUES (?, ?, ?);",
            list(country_facts[["month", "country_id", "value"]].itertuples(index=False, name=None))
            )
