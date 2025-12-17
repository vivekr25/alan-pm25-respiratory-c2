from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"

IN_EXPOSURE = DATA_PROC / "pm25_daily_claudelands_complete.csv"
OUT_ADM = DATA_PROC / "resp_admissions_daily_sim.csv"

RNG_SEED = 42

# A realistic-ish baseline for daily respiratory admissions in a catchment
BASELINE_MEAN = 18.0

# Effect assumptions:
# We simulate a small increase in admissions after high PM2.5 days (lagged).
# Values are multipliers on the mean (e.g., 0.06 = +6%).
LAG_EFFECTS = {
    0: 0.02,  # same day +2%
    1: 0.05,  # next day +5%
    2: 0.06,  # +6%
    3: 0.03,  # +3%
}

def main():
    np.random.seed(RNG_SEED)

    df = pd.read_csv(IN_EXPOSURE, parse_dates=["date"]).sort_values("date").reset_index(drop=True)

    # Basic calendar features
    df["dow"] = df["date"].dt.dayofweek  # 0=Mon ... 6=Sun
    df["month"] = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear

    # Seasonality (winter higher): smooth yearly wave
    # (This is just a plausible pattern for respiratory admissions.)
    seasonal = 1.0 + 0.18 * np.cos(2 * np.pi * (df["day_of_year"] / 365.25))

    # Day-of-week pattern (slightly lower weekends, common in admissions data)
    dow_multiplier = df["dow"].map({
        0: 1.00, 1: 1.02, 2: 1.01, 3: 1.00, 4: 1.03, 5: 0.92, 6: 0.90
    }).astype(float)

    # Small long-term drift (optional, subtle)
    t = np.arange(len(df))
    drift = 1.0 + 0.00002 * t  # tiny upward drift across years

    # Lagged exposure effect from high PM2.5 days
    # We apply effects only when the event day is high_pm25_day == True.
    high = df["high_pm25_day"].astype(int)

    # Build a multiplier starting at 1.0, then add lag contributions
    exposure_multiplier = np.ones(len(df), dtype=float)
    for lag, pct in LAG_EFFECTS.items():
        exposure_multiplier *= (1.0 + pct * high.shift(lag, fill_value=0).to_numpy())

    # Combine into expected mean admissions for each day
    mu = BASELINE_MEAN * seasonal * dow_multiplier * drift * exposure_multiplier

    # Generate counts using Poisson (good default for daily counts)
    admissions = np.random.poisson(lam=mu)

    out = df[["date"]].copy()
    out["resp_admissions"] = admissions
    out["mu_expected"] = mu  # helpful for debugging/teaching
    out["high_pm25_day"] = df["high_pm25_day"]
    out["pm25_observed"] = df["pm25_observed"]
    out["pm25_ugm3"] = df["pm25_ugm3"]

    out.to_csv(OUT_ADM, index=False)

    print(f"Saved simulated admissions → {OUT_ADM}")
    print(f"Rows: {len(out)}")
    print("Admissions summary:")
    print(out["resp_admissions"].describe().round(2))

if __name__ == "__main__":
    main()