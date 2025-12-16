from pathlib import Path
import pandas as pd

# Paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"

IN_CSV = DATA_PROC / "pm25_daily_claudelands_study.csv"
OUT_CSV = DATA_PROC / "pm25_event_windows_claudelands.csv"

WINDOW = 7  # ±7 days


def main():
    if not IN_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {IN_CSV}")

    df = pd.read_csv(IN_CSV, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)

    event_days = df[df["high_pm25_day"]].copy()

    rows = []

    for _, event in event_days.iterrows():
        event_date = event["date"]

        # Build window
        window_df = df[
            (df["date"] >= event_date - pd.Timedelta(days=WINDOW)) &
            (df["date"] <= event_date + pd.Timedelta(days=WINDOW))
        ].copy()

        # Relative day index
        window_df["relative_day"] = (window_df["date"] - event_date).dt.days
        window_df["event_date"] = event_date

        # Exclude OTHER high-exposure days from control window
        window_df = window_df[
            (window_df["relative_day"] == 0) |
            (~window_df["high_pm25_day"])
        ]

        rows.append(window_df)

    event_window_df = pd.concat(rows, ignore_index=True)

    # Final tidy
    event_window_df = event_window_df[
        ["event_date", "date", "relative_day", "pm25_ugm3", "high_pm25_day"]
    ].sort_values(["event_date", "relative_day"])

    event_window_df.to_csv(OUT_CSV, index=False)

    print(f"Total events: {event_days.shape[0]}")
    print(f"Total rows in event-window table: {event_window_df.shape[0]}")
    print(f"Saved → {OUT_CSV}")


if __name__ == "__main__":
    main()