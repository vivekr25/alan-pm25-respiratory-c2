import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data_raw"
DATA_PROC = ROOT / "data_proc"

DATA_PROC.mkdir(exist_ok=True)

XLSX_PATH = DATA_RAW / "lawa_air-quality-download-data_2016-2024.xlsx"
OUT_CSV = DATA_PROC / "pm25_daily_nz.csv"


def find_best_sheet(xlsx_path: Path) -> str:
    """Pick the most likely data sheet from a LAWA Excel file."""
    xls = pd.ExcelFile(xlsx_path, engine="openpyxl")
    sheets = xls.sheet_names
    preferred = [s for s in sheets if re.search(r"(data|monitor|dataset|meas|observ)", s, re.I)]
    return preferred[0] if preferred else sheets[0]


def main():
    if not XLSX_PATH.exists():
        raise FileNotFoundError(f"Missing file: {XLSX_PATH}")

    sheet = find_best_sheet(XLSX_PATH)
    df = pd.read_excel(XLSX_PATH, sheet_name=sheet, engine="openpyxl")

    # Standardise column names
    df.columns = [str(c).strip() for c in df.columns]

    # Try to find key columns (these names vary across exports)
    def pick_col(patterns):
        for p in patterns:
            for c in df.columns:
                if re.search(p, c, re.I):
                    return c
        return None

    col_date = pick_col([r"sample\s*date", r"date"])
    col_value = pick_col([r"concentration", r"value"])
    col_indicator = pick_col([r"indicator", r"parameter"])
    col_site = pick_col([r"site", r"location", r"station"])
    col_region = pick_col([r"region", r"council"])

    if not col_date or not col_value or not col_indicator:
        raise ValueError(
            "Could not identify required columns. "
            f"Found date={col_date}, value={col_value}, indicator={col_indicator}."
        )

    # Convert date, filter PM2.5
    df[col_date] = pd.to_datetime(df[col_date], errors="coerce")
    df = df.dropna(subset=[col_date, col_value])

    # Keep only PM2.5 rows
    pm25 = df[df[col_indicator].astype(str).str.contains("PM2.5", case=False, na=False)].copy()

    # Build a daily series (mean per day per site/region if available)
    group_cols = ["date"]
    pm25["date"] = pm25[col_date].dt.date

    if col_site:
        pm25 = pm25.rename(columns={col_site: "site"})
        group_cols.append("site")
    if col_region:
        pm25 = pm25.rename(columns={col_region: "region"})
        group_cols.append("region")

    pm25[col_value] = pd.to_numeric(pm25[col_value], errors="coerce")
    pm25 = pm25.dropna(subset=[col_value])

    daily = (
        pm25.groupby(group_cols, as_index=False)[col_value]
        .mean()
        .rename(columns={col_value: "pm25_ugm3"})
    )

    daily.to_csv(OUT_CSV, index=False)
    print(f"Saved: {OUT_CSV} ({len(daily):,} rows)")


if __name__ == "__main__":
    main()