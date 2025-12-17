from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"

IN_CSV = DATA_PROC / "pm25_daily_claudelands_complete.csv"
OUT_CSV = DATA_PROC / "pm25_event_windows_claudelands_complete.csv"

WINDOW = 7  # ±7 days


def main():
    df = pd.read_csv(IN_CSV, parse_dates=["date"]).sort_values("date").reset_index(drop=True)

    # Event days are high PM2.5 days (must be observed)
    event_days = df[df["high_pm25_day"]].copy()

    rows = []

    for _, event in event_days.iterrows():
        event_date = event["date"]

        window_df = df[
            (df["date"] >= event_date - pd.Timedelta(days=WINDOW)) &
            (df["date"] <= event_date + pd.Timedelta(days=WINDOW))
        ].copy()

        window_df["relative_day"] = (window_df["date"] - event_date).dt.days
        window_df["event_date"] = event_date

        # Rule 1: Keep event day always
        # Rule 2: For control days, keep only days where PM2.5 was observed
        window_df = window_df[
            (window_df["relative_day"] == 0) |
            (window_df["pm25_observed"])
        ]

        # Rule 3: Exclude OTHER high-exposure days from control days
        window_df = window_df[
            (window_df["relative_day"] == 0) |
            (~window_df["high_pm25_day"])
        ]

        # Helpful label for downstream work
        window_df["is_event_day"] = window_df["relative_day"] == 0
        window_df["is_control_day"] = window_df["relative_day"] != 0

        rows.append(window_df)

    out = pd.concat(rows, ignore_index=True)

    out = out[
        ["event_date", "date", "relative_day",
         "pm25_ugm3", "pm25_observed", "high_pm25_day",
         "is_event_day", "is_control_day"]
    ].sort_values(["event_date", "relative_day"])

    out.to_csv(OUT_CSV, index=False)

    counts = out.groupby("event_date").size()

    print(f"Total events: {len(event_days)}")
    print(f"Total rows: {len(out)}")
    print(f"Rows per event (min/median/max): {counts.min()} / {int(counts.median())} / {counts.max()}")
    print(f"Saved → {OUT_CSV}")


if __name__ == "__main__":
    main()