from pathlib import Path
import pandas as pd

# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"

IN_CSV = DATA_PROC / "pm25_daily_nz.csv"
OUT_CSV = DATA_PROC / "pm25_daily_claudelands_study.csv"

SITE_NAME = "Claudelands"
HIGH_EXPOSURE_PERCENTILE = 0.90  # top 10%


def main():
    if not IN_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {IN_CSV}")

    df = pd.read_csv(IN_CSV, parse_dates=["date"])

    # Filter to Claudelands
    site_df = df[df["site"] == SITE_NAME].copy()

    if site_df.empty:
        raise ValueError(f"No data found for site: {SITE_NAME}")

    # Calculate threshold
    threshold = site_df["pm25_ugm3"].quantile(HIGH_EXPOSURE_PERCENTILE)

    # Label high-exposure days
    site_df["high_pm25_day"] = site_df["pm25_ugm3"] >= threshold

    # Sort for sanity
    site_df = site_df.sort_values("date")

    # Save
    site_df.to_csv(OUT_CSV, index=False)

    print(f"Site: {SITE_NAME}")
    print(f"High-exposure threshold (90th percentile): {threshold:.2f} µg/m³")
    print(f"Total days: {len(site_df)}")
    print(f"High-exposure days: {site_df['high_pm25_day'].sum()}")
    print(f"Saved study dataset → {OUT_CSV}")


if __name__ == "__main__":
    main()