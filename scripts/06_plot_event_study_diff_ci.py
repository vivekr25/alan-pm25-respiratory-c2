from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"
DOCS = ROOT / "docs"

IN_SUMMARY = DATA_PROC / "pm25_event_summary_claudelands.csv"
OUT_PNG = DOCS / "event_study_diff_ci_plot.png"

def main():
    DOCS.mkdir(exist_ok=True)

    df = pd.read_csv(IN_SUMMARY).sort_values("relative_day")

    plt.figure()
    # y = difference vs baseline, whiskers = CI around that difference
    y = df["diff_vs_control"]
    yerr = y - df["ci_low_diff"]

    plt.errorbar(df["relative_day"], y, yerr=yerr, fmt="o-", capsize=4)

    # zero line = baseline
    plt.axhline(0, linestyle="--")

    plt.title("Event study: change in admissions vs baseline (Claudelands)")
    plt.xlabel("Relative day (0 = high PM₂.₅ day)")
    plt.ylabel("Difference vs baseline admissions (95% CI)")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=180)

    print(f"Saved plot → {OUT_PNG}")

if __name__ == "__main__":
    main()
