from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"
DOCS = ROOT / "docs"

EVENTS = DATA_PROC / "pm25_event_windows_claudelands_complete.csv"
ADM = DATA_PROC / "resp_admissions_daily_sim.csv"

OUT_TABLE = DATA_PROC / "event_study_sim_results.csv"
OUT_PNG = DOCS / "event_study_sim_plot.png"

def main():
    DOCS.mkdir(exist_ok=True)

    w = pd.read_csv(EVENTS, parse_dates=["event_date", "date"])
    a = pd.read_csv(ADM, parse_dates=["date"])

    # Merge admissions onto the event-window table
    m = w.merge(a[["date", "resp_admissions"]], on="date", how="left")

    # Sanity: we expect admissions to exist for all dates
    if m["resp_admissions"].isna().any():
        missing = int(m["resp_admissions"].isna().sum())
        raise ValueError(f"Missing admissions after merge: {missing} rows")

    # Average admissions by relative_day across all events
    by_day = (
        m.groupby("relative_day", as_index=False)["resp_admissions"]
         .agg(mean_adm="mean", n="size")
         .sort_values("relative_day")
    )

    # Define a "control baseline" as the average of control days excluding day 0
    control = m[m["is_control_day"] == True]
    control_mean = control["resp_admissions"].mean()

    by_day["diff_vs_control"] = by_day["mean_adm"] - control_mean

    by_day.to_csv(OUT_TABLE, index=False)
    print(f"Saved event-study table → {OUT_TABLE}")
    print(f"Control mean admissions (all control days): {control_mean:.2f}")

    # Plot: mean admissions by relative day + baseline
    plt.figure()
    plt.plot(by_day["relative_day"], by_day["mean_adm"], marker="o")
    plt.axhline(control_mean, linestyle="--")
    plt.title("Simulated respiratory admissions around high PM2.5 days (Claudelands)")
    plt.xlabel("Relative day (0 = high PM2.5 day)")
    plt.ylabel("Mean daily respiratory admissions")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=180)
    print(f"Saved plot → {OUT_PNG}")

if __name__ == "__main__":
    main()