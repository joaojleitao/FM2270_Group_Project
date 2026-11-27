"""Streamlit app (placeholder): inverse-volatility portfolio vs. benchmarks.

Run locally:  streamlit run app/app.py
All calculations come from app/strategy.py (identical to the notebook's functions).
"""
import datetime as dt
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))  # so "import strategy" works on Streamlit Cloud
import strategy  # noqa: E402

st.set_page_config(page_title="FM2270 Risk-Balanced Portfolio", layout="wide")
st.title("Risk-balanced (inverse-volatility) portfolio")
st.caption("FM 2270 Financial Modeling, Nova SBE. Academic project; backtested results are hypothetical.")

# --- user assumptions (the app's "meaningful assumption" controls) ---
with st.sidebar:
    st.header("Assumptions")
    lookback = st.select_slider("Volatility lookback (months)", options=[3, 6, 12], value=12)
    rebalance = st.radio("Rebalancing frequency", ["Monthly", "Quarterly"])
    cost_bps = st.slider("Transaction cost (bps on every unit traded)", 0, 50, 10)
    # first weights (12-month lookback) apply from 1 Feb 2006, see strategy_proposal.md section 2
    start = st.date_input("Start date", value=dt.date(2006, 2, 1),
                          min_value=dt.date(2006, 2, 1), max_value=dt.date(2020, 1, 1))

st.info("Placeholder: the backtest will be added after the group approves strategy_proposal.md. "
        f"Selected: lookback={lookback}m, {rebalance.lower()} rebalancing, {cost_bps} bps, start {start}.")
