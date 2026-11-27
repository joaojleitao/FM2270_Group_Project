"""Calculation functions shared by the Streamlit app and the notebook.

The notebook defines these SAME functions inline (so it runs on its own in Colab).
tests/test_consistency.py checks that both versions are identical and give identical results.

Conventions (see class_materials_index.md):
- Prices: Yahoo Finance adjusted closes (auto_adjust=True: dividends and splits included).
- Portfolios are built from daily SIMPLE returns (exact aggregation across assets).
- Performance measures use monthly LOG returns (course convention), annualized x12 (mean) and x sqrt(12) (volatility).
- Beta is NOT annualized.
"""
import numpy as np
import pandas as pd


def download_prices(tickers, start, end):
    """Daily adjusted close prices from Yahoo Finance (yfinance, auto_adjust=True).

    `end` is inclusive here (yfinance's own `end` is exclusive, so we add one day).
    Fails loudly if a ticker is missing or the history is too short.
    """
    import yfinance as yf
    end_exclusive = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    data = yf.download(tickers, start=start, end=end_exclusive, interval="1d",
                       auto_adjust=True, progress=False)
    prices = data["Close"][tickers]                       # keep the ticker order we asked for
    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    for t in tickers:                                     # check every ticker has data
        if prices[t].dropna().empty:
            raise ValueError(f"No data downloaded for {t}. Check the ticker or retry (Yahoo can rate-limit).")
    if prices.index[0] > pd.Timestamp(start) + pd.Timedelta(days=10):
        raise ValueError(f"Data starts on {prices.index[0].date()}, later than the requested {start}.")
    return prices


def download_rf(series, start, end):
    """Monthly risk-free rate from FRED (keyless CSV, as in Lecture 3).

    Returns the monthly LOG risk-free return, ln(1 + rate/100)/12, indexed by month (Period 'M').
    """
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    raw = pd.read_csv(url, index_col=0, parse_dates=True)
    rate = pd.to_numeric(raw.iloc[:, 0], errors="coerce")        # % per year; '.' = missing -> NaN
    rate = rate.loc[start:end].dropna()
    rate.index = rate.index.to_period("M")
    return np.log(1 + rate / 100) / 12


def rebalance_dates(daily_returns, freq):
    """Last trading day of each month ('M') or of each quarter ('Q') in the return data."""
    dates = daily_returns.index.to_series()
    return pd.DatetimeIndex(dates.groupby(dates.index.to_period(freq)).last().values)


def inverse_vol_weights(daily_returns, rebalance_dates, lookback_days):
    """Inverse-volatility weights at each rebalance date.

    For each date t in rebalance_dates: sigma_i = std of asset i's daily returns over the
    trailing lookback_days up to and including t, annualized by sqrt(252);
    w_i = (1/sigma_i) / sum_j (1/sigma_j).
    Dates without a full lookback window are skipped.
    Returns a DataFrame (index = rebalance dates, columns = assets). Weights decided at t are
    applied ONLY from the first trading day after t (see backtest).
    """
    rows = {}
    for t in rebalance_dates:
        window = daily_returns.loc[:t].tail(lookback_days)    # only data up to and including t
        if len(window) < lookback_days or window.isna().any().any():
            continue                                          # not enough history yet
        sigma = window.std() * np.sqrt(252)                   # annualized volatility of each asset
        inv = 1 / sigma
        rows[t] = inv / inv.sum()                             # weights sum to 1
    return pd.DataFrame(rows).T


def fixed_weights(rebalance_dates, weights):
    """Benchmark target weights: the same weights (a dict ticker -> weight) at every rebalance date."""
    return pd.DataFrame([weights] * len(rebalance_dates), index=rebalance_dates)


def backtest(daily_returns, target_weights, cost_bps):
    """Run the portfolio through time with rebalancing to target_weights and proportional costs.

    - Starts in cash at the first rebalance date t0 and buys the target weights (this first trade pays costs too).
    - Weights decided at the close of rebalance date t earn returns from the first trading day after t.
    - Between rebalances the holdings drift with prices (buy-and-hold inside the period).
    - Cost at each rebalance = cost_bps/10,000 x sum_i |target_i - drifted_i| (every unit bought or sold pays).
    Returns a DataFrame of MONTHLY simple returns (index = month-end trading days) with columns:
    gross (before costs), net (after costs) and turnover (sum |delta w| traded in that month).
    """
    c = cost_bps / 10_000
    assets = target_weights.columns
    rets = daily_returns[assets]
    dates = list(target_weights.index)
    held = pd.Series(0.0, index=assets)        # weights held just before trading (start in cash)
    gross_value, net_value = 1.0, 1.0
    gross_path, net_path, trades = {}, {}, {}
    for k, t in enumerate(dates):
        end = dates[k + 1] if k + 1 < len(dates) else rets.index[-1]
        period = rets.loc[(rets.index > t) & (rets.index <= end)]   # returns AFTER the decision date
        if period.empty:
            continue                                   # last decision date: nothing left to invest in
        target = target_weights.loc[t]
        turnover = (target - held).abs().sum()
        trades[period.index[0]] = turnover             # booked in the month whose return pays the cost
        net_value *= 1 - c * turnover                  # pay costs when trading at t
        growth = (1 + period).cumprod()                # growth of $1 in each asset since t
        port_growth = (growth * target).sum(axis=1)    # growth of the portfolio since t
        for d, g in port_growth.items():
            gross_path[d] = gross_value * g
            net_path[d] = net_value * g
        gross_value *= port_growth.iloc[-1]
        net_value *= port_growth.iloc[-1]
        held = target * growth.iloc[-1] / port_growth.iloc[-1]    # drifted weights at the next rebalance
    daily = pd.DataFrame({"gross": pd.Series(gross_path), "net": pd.Series(net_path)}).sort_index()
    month_end = daily.groupby(daily.index.to_period("M")).tail(1)   # value at each month-end
    monthly = month_end.pct_change()
    monthly.iloc[0] = month_end.iloc[0] - 1.0          # first month: relative to the starting value of 1
    trades = pd.Series(trades)
    turnover = trades.groupby(trades.index.to_period("M")).sum()
    monthly["turnover"] = turnover.reindex(monthly.index.to_period("M")).fillna(0.0).values
    return monthly


def max_drawdown(cumulative):
    """Maximum drawdown of a cumulative index: max_t (HWM_t - P_t) / HWM_t (course formula sheet)."""
    hwm = cumulative.cummax()                          # high-water mark
    return ((hwm - cumulative) / hwm).max()


def performance_table(port_returns, bench_returns, rf, periods_per_year=12):
    """Annualized mean, volatility, Sharpe, alpha, beta (not annualized), information ratio, max drawdown.

    port_returns, bench_returns: monthly SIMPLE returns (same dates). rf: monthly LOG risk-free return
    on the same dates. Returns are converted to log returns (course convention) before the statistics.
    """
    n = periods_per_year
    r = np.log1p(port_returns)                         # monthly log returns
    rb = np.log1p(bench_returns)
    ex, exb = r - rf, rb - rf                          # excess returns over the risk-free rate
    beta = np.cov(ex, exb)[0, 1] / np.var(exb, ddof=1)  # cov / var (not annualized)
    alpha = ex.mean() - beta * exb.mean()              # monthly alpha
    resid = ex - alpha - beta * exb                    # regression residuals (for alpha's t-stat)
    se_alpha = np.sqrt((resid ** 2).sum() / (len(r) - 2)
                       * (1 / len(r) + exb.mean() ** 2 / ((exb - exb.mean()) ** 2).sum()))
    active = r - rb                                    # return relative to the benchmark
    return {
        "Annualized mean return": n * r.mean(),
        "Annualized volatility": np.sqrt(n) * r.std(),
        "Sharpe ratio": n * ex.mean() / (np.sqrt(n) * ex.std()),
        "Beta (not annualized)": beta,
        "Alpha (annualized)": n * alpha,
        "Alpha t-stat": alpha / se_alpha,
        "Tracking error (annualized)": np.sqrt(n) * active.std(),
        "Information ratio": n * active.mean() / (np.sqrt(n) * active.std()),
        "Max drawdown": max_drawdown(np.exp(r.cumsum())),
    }
