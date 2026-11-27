"""Calculation functions shared by the Streamlit app and the notebook.

The notebook defines these SAME functions inline (so it runs on its own in Colab).
tests/test_consistency.py checks that both versions are identical and give identical results.

STATUS: stubs only. The backtest is NOT implemented until the group approves strategy_proposal.md.
"""
import numpy as np
import pandas as pd


def inverse_vol_weights(daily_returns, rebalance_dates, lookback_days):
    """Inverse-volatility weights at each rebalance date.

    For each date t in rebalance_dates: sigma_i = std of asset i's daily returns over the
    trailing lookback_days up to and including t, annualized by sqrt(252);
    w_i = (1/sigma_i) / sum_j (1/sigma_j).
    Returns a DataFrame (index = rebalance dates, columns = assets). Weights decided at t are
    applied ONLY from the first trading day after t (see backtest).
    """
    raise NotImplementedError("pending group approval of strategy_proposal.md")


def backtest(daily_returns, target_weights, cost_bps):
    """Run the portfolio through time with rebalancing to target_weights and proportional costs.

    Returns a DataFrame of monthly returns with columns: gross, net, turnover.
    """
    raise NotImplementedError("pending group approval of strategy_proposal.md")


def max_drawdown(cumulative):
    """Maximum drawdown of a cumulative index: max_t (HWM_t - P_t) / HWM_t (course formula sheet)."""
    raise NotImplementedError("pending group approval of strategy_proposal.md")


def performance_table(port_returns, bench_returns, rf, periods_per_year=12):
    """Annualized mean, volatility, Sharpe, alpha, beta (not annualized), information ratio, max drawdown."""
    raise NotImplementedError("pending group approval of strategy_proposal.md")
