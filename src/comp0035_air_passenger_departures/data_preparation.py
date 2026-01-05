"""
Data preparation for COMP0035 Coursework 1.
"""

from pathlib import Path
from typing import Tuple
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ----------------------------------------------------------------------
# LOAD & CLEAN
# ----------------------------------------------------------------------

def load_and_clean() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    print("[load_and_clean] Loading CSV files...")

    global_df = pd.read_csv(DATA_RAW_DIR / "TotalAirPassengerDepartures.csv")
    region_df = pd.read_csv(DATA_RAW_DIR / "TotalAirPassengerDeparturesbyRegion.csv")
    country_df = pd.read_csv(DATA_RAW_DIR / "TotalAirPassengerDeparturesbyCountry.csv")

    for df in (global_df, region_df, country_df):
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    print("[load_and_clean] Loaded successfully.")
    return global_df, region_df, country_df


# ----------------------------------------------------------------------
# Q1 — GLOBAL TRENDS
# ----------------------------------------------------------------------

def prepare_global_trends(global_df: pd.DataFrame) -> pd.DataFrame:
    print("[Q1] Preparing global trends...")
    df = global_df[["month", "value"]].dropna()
    df["year"] = df["month"].dt.year
    df["month_of_year"] = df["month"].dt.month
    print(f"[Q1] Rows prepared: {len(df)}")
    return df


def plot_global_trends(df: pd.DataFrame) -> None:
    print("[Q1] Plotting...")

    ax = df.plot(
        x="month",
        y="value",
        kind="line",
        title="Global Air Passenger Departures (1961–2020)",
        legend=False,
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Departures")
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED_DIR / "q1_global_trend.png")
    plt.close()

    seasonal = df.groupby("month_of_year")["value"].mean()
    ax = seasonal.plot(kind="line", marker="o", title="Average Seasonal Pattern")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average departures")
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED_DIR / "q1_global_seasonality.png")
    plt.close()

    print("[Q1] Done.")


# ----------------------------------------------------------------------
# Q2 — REGIONAL TRENDS
# ----------------------------------------------------------------------

def prepare_region_trends(region_df: pd.DataFrame) -> pd.DataFrame:
    """
    Your region dataset columns:
        month, level_1, level_2 (= region_name), value
    """
    print("[Q2] Preparing regional trends...")
    df = region_df[["month", "level_2", "value"]].copy()
    df = df.rename(columns={"level_2": "region_name"})
    df = df.dropna(subset=["value"])
    print(f"[Q2] Rows prepared: {len(df)}")
    return df


def plot_region_trends(df: pd.DataFrame) -> None:
    print("[Q2] Plotting regional charts...")

    pivot = df.pivot_table(
        index="month",
        columns="region_name",
        values="value",
        aggfunc="sum",
    )

    ax = pivot.plot(kind="line", title="Departures by Region Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Departures")
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED_DIR / "q2_region_trends.png")
    plt.close()

    df = df.copy()
    df["year"] = df["month"].dt.year
    yearly = df.groupby(["year", "region_name"])["value"].sum().reset_index()

    baseline_year = 1990
    baseline = yearly[yearly["year"] == baseline_year]
    baseline = baseline.set_index("region_name")["value"]

    yearly = yearly[yearly["year"] >= baseline_year].copy()
    yearly["baseline"] = yearly["region_name"].map(baseline)
    yearly["growth_index"] = yearly["value"] / yearly["baseline"]

    pivot_index = yearly.pivot_table(
        index="year",
        columns="region_name",
        values="growth_index",
    )

    ax = pivot_index.plot(
        kind="line",
        title=f"Regional Growth Index (baseline={baseline_year})",
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Index")
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED_DIR / "q2_region_growth_index.png")
    plt.close()

    print("[Q2] Done.")


# ----------------------------------------------------------------------
# Q3 — COUNTRY SHARES
# ----------------------------------------------------------------------

def prepare_country_shares(country_df: pd.DataFrame) -> pd.DataFrame:
    """
    Your country dataset columns:
        month, level_1, level_2 (= region_name), level_3 (= country_name), value
    """
    print("[Q3] Preparing country shares...")

    df = country_df[["month", "level_2", "level_3", "value"]].copy()
    df = df.rename(columns={
        "level_2": "region_name",
        "level_3": "country_name",
    })
    df = df.dropna(subset=["value"])

    df = df[df["month"].dt.year >= 2010].copy()
    df["year"] = df["month"].dt.year

    totals = df.groupby(["region_name", "country_name"])["value"].sum().reset_index()
    region_totals = totals.groupby("region_name")["value"].sum().rename("region_total")
    totals = totals.merge(region_totals, on="region_name")
    totals["share_of_region"] = totals["value"] / totals["region_total"]

    print(f"[Q3] Rows prepared: {len(totals)}")
    return totals


def plot_country_shares(totals: pd.DataFrame) -> None:
    print("[Q3] Plotting country share charts...")
    top_n = 5

    for region, subset in totals.groupby("region_name"):
        subset = subset.sort_values("share_of_region", ascending=False).head(top_n)

        ax = subset.set_index("country_name")["share_of_region"].plot(
            kind="bar",
            title=f"Top {top_n} Countries by Regional Share: {region}",
        )
        ax.set_xlabel("Country")
        ax.set_ylabel("Share")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        filename = (
            f"q3_country_shares_{region.replace(' ', '_').replace('/', '_')}.png"
        )
        plt.savefig(DATA_PROCESSED_DIR / filename)
        plt.close()

    print("[Q3] Done.")


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

def main() -> None:
    print("[main] Starting data preparation...")

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    global_df, region_df, country_df = load_and_clean()

    # Q1
    q1 = prepare_global_trends(global_df)
    q1.to_csv(DATA_PROCESSED_DIR / "prepared_global_trends.csv", index=False)
    plot_global_trends(q1)

    # Q2
    q2 = prepare_region_trends(region_df)
    q2.to_csv(DATA_PROCESSED_DIR / "prepared_region_trends.csv", index=False)
    plot_region_trends(q2)

    # Q3
    q3 = prepare_country_shares(country_df)
    q3.to_csv(DATA_PROCESSED_DIR / "prepared_country_shares.csv", index=False)
    plot_country_shares(q3)

    print("[main] All done.")


if __name__ == "__main__":
    main()
