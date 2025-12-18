from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"

EVENTS = DATA_PROC / "pm25_event_windows_claudelands_complete.csv"
ADM = DATA_PROC / "resp_admissions_daily_sim.csv"

OUT = DATA_PROC / "pm25_event_summary_claudelands.csv"


def main():
    w = pd.read_csv(EVENTS, parse_dates=["event_date", "date"])
    a = pd.read_csv(ADM, parse_dates=["date"])

    # Merge admissions onto event-window rows
    m = w.merge(a[["date", "resp_admissions"]], on="date", how="left")

    if m["resp_admissions"].isna().any():
        raise ValueError("Some event-window dates did not match admissions dates after merge.")

    # Baseline: mean admissions across ALL control days (relative_day != 0)
    control_mean = m.loc[m["relative_day"] != 0, "resp_admissions"].mean()

    # Summarise by relative day
    g = (
        m.groupby("relative_day")["resp_admissions"]
         .agg(mean="mean", sd="std", n="size")
         .reset_index()
         .sort_values("relative_day")
    )

    # Standard error and 95% CI for the mean
    # SE = SD / sqrt(n)
    g["se"] = g["sd"] / np.sqrt(g["n"])
    g["ci_low"] = g["mean"] - 1.96 * g["se"]
    g["ci_high"] = g["mean"] + 1.96 * g["se"]

    # Difference vs baseline
    g["baseline_control_mean"] = control_mean
    g["diff_vs_control"] = g["mean"] - control_mean
    g["ci_low_diff"] = g["ci_low"] - control_mean
    g["ci_high_diff"] = g["ci_high"] - control_mean

    g.to_csv(OUT, index=False)

    print(f"Saved summary → {OUT}")
    print(f"Baseline (all control days) mean admissions: {control_mean:.3f}")
    print(g[["relative_day", "mean", "n", "diff_vs_control", "ci_low_diff", "ci_high_diff"]].head(8))


if __name__ == "__main__":
    main()