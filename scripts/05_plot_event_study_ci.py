from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"
DOCS = ROOT / "docs"

IN_SUMMARY = DATA_PROC / "pm25_event_summary_claudelands.csv"
OUT_PNG = DOCS / "event_study_ci_plot.png"


def main():
    DOCS.mkdir(exist_ok=True)

    df = pd.read_csv(IN_SUMMARY)

    # Plot mean admissions with error bars (95% CI)
    plt.figure()
    plt.errorbar(
        df["relative_day"],
        df["mean"],
        yerr=(df["mean"] - df["ci_low"]),
        fmt="o-",
        capsize=4,
    )

    # Baseline line
    baseline = float(df["baseline_control_mean"].iloc[0])
    plt.axhline(baseline, linestyle="--")

    plt.title("Event study: simulated respiratory admissions around high PM2.5 days (Claudelands)")
    plt.xlabel("Relative day (0 = high PM2.5 day)")
    plt.ylabel("Mean daily respiratory admissions (95% CI)")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=180)

    print(f"Saved plot → {OUT_PNG}")


if __name__ == "__main__":
    main()