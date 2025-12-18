from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_PROC = ROOT / "data_proc"
SUMMARY = DATA_PROC / "pm25_event_summary_claudelands.csv"

st.set_page_config(page_title="ALAN-C2 • PM₂.₅ × Respiratory Admissions", page_icon="🌫️", layout="wide")
st.title("🌫️ ALAN-C2: PM₂.₅ exposure & respiratory admissions (event study)")
st.caption("Claudelands (Waikato). Admissions are simulated. This app explains the pattern and uncertainty.")

if not SUMMARY.exists():
    st.error(f"Missing file: {SUMMARY}. Run scripts/04_summarise_event_effects.py first.")
    st.stop()

df = pd.read_csv(SUMMARY).sort_values("relative_day")

baseline = float(df["baseline_control_mean"].iloc[0])

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("How to read this")
    st.markdown(
        f"""
- **Day 0** = high PM₂.₅ day (top decile).  
- Dots = **mean** admissions.  
- Bars = **95% confidence interval** (uncertainty).  
- Baseline ≈ **{baseline:.2f}** admissions/day.
"""
    )

with c2:
    st.subheader("Summary table")
    show_cols = ["relative_day","mean","n","diff_vs_control","ci_low_diff","ci_high_diff"]
    st.dataframe(df[show_cols], use_container_width=True, hide_index=True)

st.divider()

st.subheader("Mean admissions (95% CI)")
st.line_chart(df.set_index("relative_day")[["mean"]], use_container_width=True)

st.caption("Tip: the line chart is a quick look. Use the difference chart below for the clearest interpretation.")

st.subheader("Difference vs baseline (with CI bounds)")
diff_plot = df.set_index("relative_day")[["diff_vs_control","ci_low_diff","ci_high_diff"]]
st.line_chart(diff_plot, use_container_width=True)

st.markdown(
    """
**Interpretation notes**
- This is an **observational pattern check**, not causal inference.
- Confidence intervals help show where results are most compatible with an uplift vs baseline.
"""
)
