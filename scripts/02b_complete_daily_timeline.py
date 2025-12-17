from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"

IN_CSV = DATA_PROC / "pm25_daily_claudelands_study.csv"
OUT_CSV = DATA_PROC / "pm25_daily_claudelands_complete.csv"


def main():
    df = pd.read_csv(IN_CSV, parse_dates=["date"]).sort_values("date")

    # Build complete daily calendar
    full_dates = pd.DataFrame({
        "date": pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    })

    # Merge observed PM2.5 onto full calendar
    merged = full_dates.merge(df, on="date", how="left")

    # Explicit flags
    merged["pm25_observed"] = merged["pm25_ugm3"].notna()
    merged["high_pm25_day"] = merged["high_pm25_day"].fillna(False)

    # Keep metadata consistent
    merged["site"] = "Claudelands"
    merged["region"] = "Waikato"

    merged.to_csv(OUT_CSV, index=False)

    print(f"Saved complete daily timeline → {OUT_CSV}")
    print(f"Total days: {len(merged)}")
    print(f"Observed PM2.5 days: {merged['pm25_observed'].sum()}")
    print(f"Missing PM2.5 days: {(~merged['pm25_observed']).sum()}")


if __name__ == "__main__":
    main()