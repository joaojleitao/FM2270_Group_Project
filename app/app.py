"""Streamlit app: inverse-volatility ("risk-balanced") portfolio vs. benchmarks.

Run locally:  streamlit run app/app.py
All calculations come from app/strategy.py, which is identical to the functions in the notebook
(tests/test_consistency.py). With the default settings the app reproduces Table 1 of the prospectus.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))  # so "import strategy" works on Streamlit Cloud
import strategy  # noqa: E402

# same fixed sample as the notebook
DATA_START, END_DATE = "2004-12-01", "2026-10-31"
TICKERS = ["SPY", "IEF", "GLD"]
PRIMARY_BENCHMARK = {"SPY": 0.6, "IEF": 0.4}
EQUAL_WEIGHT = {"SPY": 1 / 3, "IEF": 1 / 3, "GLD": 1 / 3}

st.set_page_config(page_title="Risk-Balanced Portfolio", layout="wide")
st.title("Risk-balanced (inverse-volatility) portfolio: SPY / IEF / GLD")
st.caption("FM 2270 Financial Modeling, Nova SBE. Academic project: backtested results are hypothetical "
           "and do not guarantee future performance. Data: Yahoo Finance (adjusted prices) and FRED TB3MS.")


@st.cache_data(ttl=24 * 3600, show_spinner="Downloading data from Yahoo Finance and FRED...")
def load_data():
    prices = strategy.download_prices(TICKERS, DATA_START, END_DATE)
    rf_monthly = strategy.download_rf("TB3MS", DATA_START, END_DATE)
    return prices.pct_change().iloc[1:], rf_monthly


# --- the user's assumptions ---
with st.sidebar:
    st.header("Assumptions")
    lookback_m = st.select_slider("Volatility lookback (months)", options=[1, 3, 6, 12, 24], value=12,
                                  help="Trailing window of daily returns used to estimate each asset's volatility.")
    freq_label = st.radio("Rebalancing frequency", ["Monthly", "Quarterly"])
    cost_bps = st.slider("Transaction cost (bps on every unit traded)", 0, 100, 10,
                         help="cost = bps/10,000 x sum |change in weights| at each rebalance; benchmarks pay the same.")
    start_year = st.slider("First year of the backtest", 2006, 2024, 2006,
                           help="The portfolio is bought at the last trading day of the previous year.")
    st.markdown("Defaults (12 months, monthly, 10 bps, 2006) reproduce the prospectus.")

try:
    daily_returns, rf_monthly = load_data()
except Exception as e:  # show a clear message instead of a stack trace
    st.error(f"Data download failed ({e}). Yahoo Finance sometimes rate-limits: please reload in a minute.")
    st.stop()

lookback_days = {1: 21, 3: 63, 6: 126, 12: 252, 24: 504}[lookback_m]
freq = "M" if freq_label == "Monthly" else "Q"
first_decision = daily_returns.loc[:f"{start_year - 1}-12-31"].index[-1]   # last trading day before the start year

# strategy: weights decided at each rebalance date, applied from the next trading day
dates = strategy.rebalance_dates(daily_returns, freq)
dates = dates[dates >= first_decision]
weights = strategy.inverse_vol_weights(daily_returns, dates, lookback_days)
if weights.empty or weights.index[0] != dates[0]:
    st.warning("Not enough history for this lookback at the chosen start: choose a later start or a shorter lookback.")
    st.stop()
monthly_dates = strategy.rebalance_dates(daily_returns, "M")
monthly_dates = monthly_dates[monthly_dates >= first_decision]

portfolios = {
    "Inverse-vol (strategy)": strategy.backtest(daily_returns, weights, cost_bps),
    "60/40 (primary benchmark)": strategy.backtest(daily_returns, strategy.fixed_weights(monthly_dates, PRIMARY_BENCHMARK), cost_bps),
    "Equal weight 1/3": strategy.backtest(daily_returns, strategy.fixed_weights(monthly_dates, EQUAL_WEIGHT), cost_bps),
    "SPY buy & hold": strategy.backtest(daily_returns, strategy.fixed_weights(monthly_dates[:1], {"SPY": 1.0}), cost_bps),
}
net = pd.DataFrame({k: v["net"] for k, v in portfolios.items()})
rf = rf_monthly.reindex(net.index.to_period("M"))
rf.index = net.index

# --- cumulative performance, all starting at 1 ---
cumulative = np.exp(np.log1p(net).cumsum())
cumulative = pd.concat([pd.DataFrame(1.0, index=[first_decision], columns=net.columns), cumulative])
col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("Cumulative performance (net of costs, start = 1)")
    fig, ax = plt.subplots(figsize=(8, 4))
    styles = {"Inverse-vol (strategy)": ("#1f4e79", 2.2, "-"), "60/40 (primary benchmark)": ("#c0504d", 1.6, "-"),
              "Equal weight 1/3": ("#c9a227", 1.3, "--"), "SPY buy & hold": ("#7f7f7f", 1.1, ":")}
    for col in cumulative:
        c, lw, ls = styles[col]
        ax.plot(cumulative.index, cumulative[col], color=c, lw=lw, ls=ls, label=col)
    ax.set_yscale("log"); ax.set_ylabel("Growth of $1 (log scale)"); ax.grid(alpha=0.3); ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    st.pyplot(fig)
with col2:
    st.subheader("Strategy weights")
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.stackplot(weights.index, weights.T.values, labels=weights.columns, colors=["#1f4e79", "#8fb3d9", "#c9a227"])
    ax2.set_ylim(0, 1); ax2.legend(loc="upper left", ncol=3, frameon=True, framealpha=1)
    st.pyplot(fig2)
    st.caption(f"Latest weights ({weights.index[-1]:%d %b %Y}): "
               + ", ".join(f"{k} {v:.1%}" for k, v in weights.iloc[-1].items()))

# --- performance table (same function as the notebook) ---
st.subheader(f"Performance, {net.index[0]:%b %Y} to {net.index[-1]:%b %Y} (monthly data, net of costs)")
perf = pd.DataFrame({k: strategy.performance_table(v["net"], portfolios["60/40 (primary benchmark)"]["net"], rf)
                     for k, v in portfolios.items()})
perf.loc[["Alpha t-stat", "Tracking error (annualized)", "Information ratio"], "60/40 (primary benchmark)"] = np.nan
perf = perf.mask(perf.abs() < 1e-12, 0.0)               # benchmark vs itself: alpha is 0 up to rounding
perf.loc["Final value of $1"] = cumulative.iloc[-1]
pct_rows = ["Annualized mean return", "Annualized volatility", "Alpha (annualized)", "Tracking error (annualized)", "Max drawdown"]
shown = perf.copy().astype(object)
for row in perf.index:
    shown.loc[row] = [("–" if pd.isna(x) else (f"{x:.2%}" if row in pct_rows else f"{x:.2f}")) for x in perf.loc[row]]
st.table(shown)
st.caption("Log returns; mean x12, volatility x√12; Sharpe on excess returns over FRED TB3MS; beta and alpha from the "
           "excess-return regression on the 60/40 benchmark (beta not annualized, alpha x12); information ratio vs 60/40. "
           "Inverse volatility ignores correlations, so it is not full risk parity.")
st.markdown("Source code and notebook: https://github.com/joaojleitao/FM2270_Group_Project")
