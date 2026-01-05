"""
Data description and exploration for COMP0035 Coursework 1.

Loads the air passenger departure datasets (global, by region, by country),
performs basic description and exploration using pandas, and generates charts.

Run:
    python -m src.data_description
"""

from pathlib import Path
from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_raw_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three CSV files from data/raw into pandas DataFrames."""
    global_df = pd.read_csv(
        DATA_RAW_DIR / "TotalAirPassengerDepartures.csv"
    )
    region_df = pd.read_csv(
        DATA_RAW_DIR / "TotalAirPassengerDeparturesbyRegion.csv"
    )
    country_df = pd.read_csv(
        DATA_RAW_DIR / "TotalAirPassengerDeparturesbyCountry.csv"
    )
    return global_df, region_df, country_df


def clean_common_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean common columns:
    - Parse 'month' as datetime.
    - Convert 'value' to numeric, treating 'na' as missing.
    """
    df = df.copy()
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    if "value" in df.columns and df["value"].dtype == "object":
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def explore_structure(df: pd.DataFrame, name: str) -> None:
    """Print basic structural information about a DataFrame."""
    print(f"\n=== {name}: structure ===")
    print("Shape:", df.shape)
    print("\nColumn dtypes:")
    print(df.dtypes)
    print("\nFirst 5 rows:")
    print(df.head())

    if "value" in df.columns:
        missing = df["value"].isna().sum()
        print(f"\nMissing values in 'value': {missing} "
              f"({missing / len(df):.2%} of rows)")

        print("\nSummary statistics for 'value':")
        print(df["value"].describe())


def explore_global_trend(global_df: pd.DataFrame) -> None:
    """Plot overall global passenger departures over time."""
    print("\n=== Global monthly departures over time ===")
    print(global_df[["month", "value"]].head())

    ax = global_df.plot(
        x="month",
        y="value",
        kind="line",
        title="Global air passenger departures over time",
        legend=False,
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of passenger departures")
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED_DIR / "global_departures_trend.png")
    plt.close()


def explore_regional_distribution(region_df: pd.DataFrame) -> None:
    """Plot an example of regional departures for a sample year."""
    sample_year = 2019
    subset = region_df[region_df["month"].dt.year == sample_year]

    print(f"\n=== Regional departures for {sample_year} (first 10 rows) ===")
    print(subset.head(10))

    pivot = subset.pivot_table(
        index="month",
        columns="level_2",
        values="value",
        aggfunc="sum",
    )

    ax = pivot.plot(
        kind="line",
        title=f"Regional air passenger departures in {sample_year}",
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of passenger departures")
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED_DIR / "regional_departures_2019.png")
    plt.close()


def explore_country_distribution(country_df: pd.DataFrame) -> None:
    """Show basic country-level distribution and a simple bar chart."""
    print("\n=== Unique regions and countries (country-level file) ===")
    print("Regions:", sorted(country_df["level_2"].unique()))
    print("Number of countries:", country_df["level_3"].nunique())

    latest_year = country_df["month"].dt.year.max()
    latest = country_df[country_df["month"].dt.year == latest_year]

    totals = latest.groupby("level_3")["value"].sum().sort_values(ascending=False)
    print(f"\nTop 10 countries by departures in {latest_year}:")
    print(totals.head(10))

    ax = totals.head(10).plot(
        kind="bar",
        title=f"Top 10 countries by air passenger departures in {latest_year}",
    )
    ax.set_xlabel("Country")
    ax.set_ylabel("Number of passenger departures (year total)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED_DIR / "top_countries_latest_year.png")
    plt.close()


def main() -> None:
    """Entry point for running data description and exploration."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    global_df, region_df, country_df = load_raw_datasets()

    global_df = clean_common_columns(global_df)
    region_df = clean_common_columns(region_df)
    country_df = clean_common_columns(country_df)

    explore_structure(global_df, "Global departures")
    explore_structure(region_df, "Regional departures")
    explore_structure(country_df, "Country-level departures")

    explore_global_trend(global_df)
    explore_regional_distribution(region_df)
    explore_country_distribution(country_df)


if __name__ == "__main__":
    main()
