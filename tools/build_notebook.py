"""Build notebook/FM2270_backtest.ipynb from the cells below.

The calculation functions are copied VERBATIM from app/strategy.py, so the notebook and the app
always use identical code (tests/test_consistency.py checks this).
Usage (from the project root):  python tools/build_notebook.py
Then execute it:  jupyter nbconvert --to notebook --execute --inplace notebook/FM2270_backtest.ipynb
"""
import ast
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app" / "strategy.py"
OUT = ROOT / "notebook" / "FM2270_backtest.ipynb"

GROUP_NAME = "[MOODLE GROUP NAME]"
MEMBERS = "[Full name, student number]"
REPO_URL = "https://github.com/joaojleitao/FM2270_Group_Project"
APP_URL = "[STREAMLIT APP URL]"

src = MODULE.read_text(encoding="utf-8")
tree = ast.parse(src)
FUNCS = {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef)}

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

# ---------------------------------------------------------------------------------------------
md(f"""
# FM 2270 Financial Modeling: Risk-Balanced (Inverse-Volatility) Portfolio

**Moodle group:** {GROUP_NAME}
**Members:** {MEMBERS}
**GitHub repository:** {REPO_URL}
**Streamlit app:** {APP_URL}

This notebook reproduces **every number, table and figure** in the investor prospectus. It runs from start to finish
in a fresh Google Colab session and downloads all data through APIs (no data files).

**Setup instructions**
1. Open https://colab.research.google.com → *File → Upload notebook* (or *Open notebook → GitHub* and paste the repository URL).
2. *Runtime → Run all*. The first code cell installs `yfinance`; everything else is preinstalled in Colab.
3. The data come from Yahoo Finance (prices) and FRED (risk-free rate). Both are free and keyless. The start and end dates
   are fixed in the Parameters cell, so the results are reproducible (Yahoo occasionally revises adjusted prices
   by tiny amounts; see Section 4).
4. Figures and tables are also saved to the folder `outputs/` (used to typeset the prospectus).

**Generative-AI disclosure.** Claude Code (Anthropic, model Claude Opus 5.5) was used for coding, for drafting text and
for checking the class conventions; OpenAI Codex was used as an independent code reviewer. Every output was checked by
running the code, by an independent day-by-day re-implementation of the backtest, and against the course formula sheet
and lecture notebooks. The inverse-volatility strategy was chosen by the group. Full log: `AI_USE_LOG.md` in the repository.
""")

md("## 1. Setup")
code("""
# Colab: install what is not preinstalled (quiet). yfinance downloads Yahoo Finance data.
!pip -q install yfinance
""")
code("""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.float_format", lambda x: f"{x:,.4f}")
os.makedirs("outputs", exist_ok=True)          # figures and tables for the prospectus
""")

md("""
## 2. Parameters
Every assumption is set here, explicitly. Monthly metrics: means ×12, volatilities ×√12. Beta is not annualized.
""")
code("""
DATA_START = '2004-12-01'      # first day of price data (GLD has traded since 18 Nov 2004)
FIRST_DECISION = '2005-12-30'  # first rebalance date (last trading day of 2005): first weights apply from 3 Jan 2006
END_DATE = '2026-10-31'        # last day of data (last complete month when the project was run); inclusive
TICKERS = ['SPY', 'IEF', 'GLD']  # US equities, 7-10 year US Treasuries, gold
LOOKBACK = 252                 # trading days of daily returns used to estimate volatility (about 12 months)
REBALANCE_FREQ = 'M'           # 'M' = monthly, 'Q' = quarterly
COST_BPS = 10                  # transaction cost in basis points on every unit traded: cost = 0.0010 x sum|delta w|
RF_SERIES = 'TB3MS'            # FRED: 3-month Treasury bill, secondary market rate, monthly, % per year
PERIODS_PER_YEAR = 12          # monthly returns -> mean x12, volatility x sqrt(12)
PRIMARY_BENCHMARK = {'SPY': 0.6, 'IEF': 0.4}               # 60/40 stocks/bonds, rebalanced monthly
EQUAL_WEIGHT = {'SPY': 1/3, 'IEF': 1/3, 'GLD': 1/3}         # 1/n of the same three assets, rebalanced monthly
""")

md("""
## 3. Calculation functions
These functions are **identical** to `app/strategy.py`, which the Streamlit app uses
(`tests/test_consistency.py` in the repository checks that the code and the results match).
""")
for name in FUNCS:
    code(FUNCS[name])

md("""
## 4. Data download via API, and the four checks
* **Prices:** Yahoo Finance through `yfinance`, daily, `auto_adjust=True`: closes adjusted for splits **and dividends**,
  so returns are total returns. ETF expense ratios are already deducted in the ETF prices.
* **Risk-free rate:** FRED series TB3MS (3-month T-bill, monthly average, % p.a.), keyless CSV as in Lecture 3.
  Monthly log rate = ln(1 + TB3MS/100)/12. TB3MS is quoted on a discount basis; the difference from a bond-equivalent
  yield is a few basis points per year and is ignored.

Checks (Lecture 3): shape, date range, missing values and a plot.
""")
code("""
prices = download_prices(TICKERS, DATA_START, END_DATE)
rf_monthly = download_rf(RF_SERIES, DATA_START, END_DATE)

print('1) Shape:', prices.shape)
print('2) Date range:', prices.index[0].date(), 'to', prices.index[-1].date())
print('3) Missing values per ticker:', prices.isna().sum().to_dict())
print('   Risk-free months:', len(rf_monthly), 'from', rf_monthly.index[0], 'to', rf_monthly.index[-1],
      '| missing:', int(rf_monthly.isna().sum()))
assert prices.isna().sum().sum() == 0, 'Unexpected missing prices: inspect before continuing'
assert prices.index[-1] >= pd.Timestamp(END_DATE) - pd.Timedelta(days=5), 'Price data end too early'

ax = (prices / prices.iloc[0]).plot(figsize=(9, 4), logy=True, title='4) Adjusted prices, start = 1 (log scale)')
ax.set_ylabel('Growth of $1'); plt.show()
""")

md("""
## 5. Data adjustments
* Daily **simple** returns from adjusted prices; the first day is dropped (no return).
* All three ETFs trade on the same US calendar, so no alignment across assets is needed (checked above: no missing values).
* No outliers are removed: large moves (2008, March 2020) are real and part of the risk the client bears.
* The risk-free rate is monthly and is matched to each month of portfolio returns.
* Portfolio returns are aggregated from simple returns (exact). Performance measures use monthly **log** returns
  (course convention): log return = ln(1 + simple return).
""")
code("""
daily_returns = prices.pct_change().iloc[1:]
print(daily_returns.describe().loc[['count', 'mean', 'std', 'min', 'max']])
""")

md("""
## 6. Strategy: inverse-volatility weights
At each month-end *t*: σ(i,t) = standard deviation of asset *i*'s daily returns over the last 252 trading days
**up to and including t** (annualized ×√252), and w(i,t) = (1/σ(i,t)) / Σⱼ (1/σ(j,t)).
The weights are applied only to returns from the **first trading day of month t+1** (no look-ahead).
Between rebalances the holdings drift with prices.

*Inverse volatility is not full risk parity: it ignores correlations, so each asset's contribution to total
portfolio risk is only approximately equal.*
""")
code("""
all_dates = rebalance_dates(daily_returns, REBALANCE_FREQ)
decision_dates = all_dates[all_dates >= FIRST_DECISION]
weights = inverse_vol_weights(daily_returns, decision_dates, LOOKBACK)
assert weights.index[0] == pd.Timestamp(FIRST_DECISION), 'First decision date lacks a full lookback window'
assert np.allclose(weights.sum(axis=1), 1.0)

# look-ahead check: recompute one date using ONLY data up to that date
t_check = weights.index[len(weights) // 2]          # a date in the middle of the sample
w_check = inverse_vol_weights(daily_returns.loc[:t_check], [t_check], LOOKBACK)
assert np.allclose(w_check.loc[t_check], weights.loc[t_check]), 'Weights use future data!'

weight_stats = pd.DataFrame({'Average': weights.mean(), 'Min': weights.min(), 'Max': weights.max(),
                             'Latest (' + str(weights.index[-1].date()) + ')': weights.iloc[-1]})
print(weight_stats)
weight_stats.to_csv('outputs/weight_stats.csv')

fig, ax = plt.subplots(figsize=(9, 3.6))
ax.stackplot(weights.index, weights.T.values, labels=weights.columns, colors=['#1f4e79', '#8fb3d9', '#c9a227'])
ax.set_ylim(0, 1); ax.set_ylabel('Weight'); ax.legend(loc='upper left', ncol=3, frameon=True, framealpha=1)
ax.set_title('Figure 2. Inverse-volatility weights at each month-end')
fig.tight_layout(); fig.savefig('outputs/fig2_weights.png', dpi=200); plt.show()
""")

md("""
## 7. Backtest: strategy and benchmarks
* **Strategy:** inverse-volatility, monthly rebalancing, 10 bps on every unit traded.
* **Primary benchmark: 60/40 SPY/IEF**, rebalanced monthly: the classic moderate portfolio for the same client.
* **Secondary benchmark: equal weight (1/3 each) of SPY, IEF, GLD**, rebalanced monthly: same assets, naive weights.
  It separates the effect of *adding gold* from the effect of *inverse-volatility weighting*.
* **Context: SPY**, buy and hold.

All portfolios start in cash on 30 Dec 2005, pay the same costs (including the first purchase), and are evaluated
over the same months (January 2006 to October 2026).
""")
code("""
strategy = backtest(daily_returns, weights, COST_BPS)
bench_6040 = backtest(daily_returns, fixed_weights(decision_dates, PRIMARY_BENCHMARK), COST_BPS)
bench_ew = backtest(daily_returns, fixed_weights(decision_dates, EQUAL_WEIGHT), COST_BPS)
bench_spy = backtest(daily_returns, fixed_weights(decision_dates[:1], {'SPY': 1.0}), COST_BPS)

# risk-free rate on the same months as the portfolio returns
rf = rf_monthly.reindex(strategy.index.to_period('M'))
rf.index = strategy.index
assert rf.notna().all(), 'Risk-free rate missing for some months'
assert strategy.index.equals(bench_6040.index) and strategy.index.equals(bench_spy.index)

portfolios = {'Inverse-vol (strategy)': strategy, '60/40 (primary benchmark)': bench_6040,
              'Equal weight 1/3': bench_ew, 'SPY buy & hold': bench_spy}
net = pd.DataFrame({k: v['net'] for k, v in portfolios.items()})
print('Months:', len(net), '| first:', net.index[0].date(), '| last:', net.index[-1].date())
net.head()
""")

md("## 8. Cumulative performance (all series start at 1)")
code("""
cumulative = np.exp(np.log1p(net).cumsum())                 # = product of (1 + monthly return)
start_row = pd.DataFrame(1.0, index=[decision_dates[0]], columns=net.columns)
cumulative = pd.concat([start_row, cumulative])             # value 1 on 30 Dec 2005

fig, ax = plt.subplots(figsize=(9, 4.2))
styles = {'Inverse-vol (strategy)': ('#1f4e79', 2.2, '-'), '60/40 (primary benchmark)': ('#c0504d', 1.6, '-'),
          'Equal weight 1/3': ('#c9a227', 1.3, '--'), 'SPY buy & hold': ('#7f7f7f', 1.1, ':')}
for col in cumulative:
    c, lw, ls = styles[col]
    ax.plot(cumulative.index, cumulative[col], color=c, lw=lw, ls=ls, label=col)
ax.set_yscale('log'); ax.set_ylabel('Growth of $1 (log scale, net of costs)')
ax.set_yticks([0.5, 1, 2, 3, 4, 6, 8]); ax.set_yticklabels(['0.5', '1', '2', '3', '4', '6', '8'])
ax.legend(frameon=False); ax.grid(alpha=0.3)
ax.set_title('Figure 1. Cumulative performance, Jan 2006 to Oct 2026 (start = 1)')
fig.tight_layout(); fig.savefig('outputs/fig1_cumulative.png', dpi=200); plt.show()
print(cumulative.iloc[-1].rename('Final value of $1'))
""")

md("""
## 9. Performance measures (net of costs, monthly data)
Assumptions: monthly log returns; annualized mean = 12 × mean; annualized volatility = √12 × std;
Sharpe ratio = 12·mean(R − R_f) / (√12·std(R − R_f)); beta and alpha from the excess-return regression on the
**60/40 benchmark's** excess returns, by cov/var as in class (beta **not annualized**; alpha ×12);
information ratio = 12·mean(R − R_b) / (√12·std(R − R_b)) against the 60/40 benchmark (formula sheet version);
maximum drawdown on the cumulative index. Risk-free: FRED TB3MS.
""")
code("""
perf = pd.DataFrame({k: performance_table(v['net'], bench_6040['net'], rf, PERIODS_PER_YEAR)
                     for k, v in portfolios.items()})
# the benchmark against itself has no alpha t-stat, tracking error or IR
perf.loc[['Alpha t-stat', 'Tracking error (annualized)', 'Information ratio'], '60/40 (primary benchmark)'] = np.nan
perf = perf.mask(perf.abs() < 1e-12, 0.0)               # benchmark vs itself: alpha is 0 up to rounding
perf.loc['Final value of $1'] = cumulative.iloc[-1]
perf.loc['Average annual turnover'] = {k: v['turnover'].iloc[1:].sum() / (len(v) / 12) for k, v in portfolios.items()}
perf.to_csv('outputs/table1_performance.csv')
perf
""")

md("""
**Gross versus net of costs.** The cost model charges 10 bps on every unit bought or sold (Lecture 4 model,
cost × |Δposition|). Turnover = Σ|Δw| per rebalance (the first purchase counts as turnover of 1 and is excluded
from the annual average above).
""")
code("""
gross_vs_net = pd.DataFrame({
    'Gross mean (ann.)': {k: PERIODS_PER_YEAR * np.log1p(v['gross']).mean() for k, v in portfolios.items()},
    'Net mean (ann.)': {k: PERIODS_PER_YEAR * np.log1p(v['net']).mean() for k, v in portfolios.items()},
})
gross_vs_net['Cost drag (ann.)'] = gross_vs_net['Gross mean (ann.)'] - gross_vs_net['Net mean (ann.)']
gross_vs_net.to_csv('outputs/table_gross_net.csv')
gross_vs_net
""")

md("## 10. Drawdowns and rolling risk")
code("""
drawdowns = (cumulative.cummax() - cumulative) / cumulative.cummax()
fig, ax = plt.subplots(figsize=(9, 3.4))
for col in ['Inverse-vol (strategy)', '60/40 (primary benchmark)', 'SPY buy & hold']:
    c, lw, ls = styles[col]
    ax.plot(drawdowns.index, -drawdowns[col], color=c, lw=lw if col != 'SPY buy & hold' else 1.0, ls=ls, label=col)
ax.set_ylabel('Drawdown from previous peak'); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
ax.legend(frameon=False, loc='lower left'); ax.grid(alpha=0.3)
ax.set_title('Figure 3. Drawdowns (net of costs)')
fig.tight_layout(); fig.savefig('outputs/fig3_drawdowns.png', dpi=200); plt.show()

# 36-month rolling annualized volatility: is the risk level stable over time?
rolling_vol = np.log1p(net).rolling(36).std() * np.sqrt(PERIODS_PER_YEAR)
print('Range of 36-month rolling volatility:')
print(pd.DataFrame({'min': rolling_vol.min(), 'max': rolling_vol.max()}))
rolling_vol.agg(['min', 'max']).T.to_csv('outputs/rolling_vol_range.csv')

# worst months and calendar years
yearly = np.exp(np.log1p(net).groupby(net.index.year).sum()) - 1
print('\\nCalendar-year returns (net):'); print(yearly)
yearly.to_csv('outputs/yearly_returns.csv')
""")

md("""
## 11. Robustness checks
Parameters such as the 12-month lookback can be "found" by searching the same history (data snooping, Lecture 4),
so we report how the results change with: the **lookback** (3, 6, 12 months), the **rebalancing frequency**
(monthly vs quarterly), the **cost level** (0, 10, 25, 50 bps), a one-day **execution lag** (Lecture 4's `shift(2)`
idea: trade at the close of the first trading day of the month), and **sub-periods**, including 2022 when stocks and
bonds fell together. All versions are measured over the same months against the 60/40 benchmark.
""")
code("""
key_rows = ['Annualized mean return', 'Annualized volatility', 'Sharpe ratio', 'Beta (not annualized)',
            'Alpha (annualized)', 'Information ratio', 'Max drawdown']
robust = {}

def run_variant(lookback=LOOKBACK, freq=REBALANCE_FREQ, cost=COST_BPS):
    dates = rebalance_dates(daily_returns, freq)
    dates = dates[dates >= FIRST_DECISION]
    w = inverse_vol_weights(daily_returns, dates, lookback)
    return backtest(daily_returns, w, cost), w

for months, days in [(3, 63), (6, 126), (12, 252)]:
    bt, _ = run_variant(lookback=days)
    robust[f'Lookback {months}m'] = performance_table(bt['net'], bench_6040['net'], rf)
bt_q, _ = run_variant(freq='Q')
robust['Quarterly rebalancing'] = performance_table(bt_q['net'], bench_6040['net'], rf)

# execution lag: the weights decided at month-end t are traded one trading day later (first day of month t+1)
w_lag = weights.iloc[:-1].copy()
w_lag.index = [daily_returns.index[daily_returns.index.get_loc(t) + 1] for t in w_lag.index]
bt_lag = backtest(daily_returns, w_lag, COST_BPS)
robust['1-day execution lag'] = performance_table(bt_lag['net'], bench_6040['net'], rf)

robust_table = pd.DataFrame(robust).loc[key_rows]
robust_table.to_csv('outputs/table2_robustness.csv')
robust_table
""")
code("""
# cost sensitivity: strategy AND benchmark pay the same cost; Sharpe ratios and alpha
cost_rows = {}
for c in [0, 10, 25, 50]:
    s = backtest(daily_returns, weights, c)
    b = backtest(daily_returns, fixed_weights(decision_dates, PRIMARY_BENCHMARK), c)
    p_s, p_b = performance_table(s['net'], b['net'], rf), performance_table(b['net'], b['net'], rf)
    cost_rows[f'{c} bps'] = {'Strategy mean (ann.)': p_s['Annualized mean return'], 'Strategy Sharpe': p_s['Sharpe ratio'],
                             '60/40 Sharpe': p_b['Sharpe ratio'], 'Alpha (ann.)': p_s['Alpha (annualized)']}
cost_table = pd.DataFrame(cost_rows).T
cost_table.to_csv('outputs/table3_costs.csv')
print(cost_table)

# breakeven cost: the cost (bps per unit traded, paid by both) at which the strategy's Sharpe edge over 60/40 is zero
def sharpe_edge(c):
    s = backtest(daily_returns, weights, c)
    b = backtest(daily_returns, fixed_weights(decision_dates, PRIMARY_BENCHMARK), c)
    return performance_table(s['net'], b['net'], rf)['Sharpe ratio'] - performance_table(b['net'], b['net'], rf)['Sharpe ratio']

lo, hi = 0.0, 2000.0
edge_0 = sharpe_edge(lo)
print(f'Sharpe edge over 60/40 at zero cost: {edge_0:.3f}')
if edge_0 <= 0:
    breakeven_bps = 0.0
    print('No positive Sharpe edge even without costs: no breakeven to compute.')
elif sharpe_edge(hi) > 0:
    breakeven_bps = float('inf')
    print('The Sharpe edge survives even 2,000 bps per unit traded.')
else:
    # check the edge falls steadily with costs on a coarse grid, so the bisection finds the single crossing
    grid = [sharpe_edge(c) for c in range(0, 2001, 250)]
    assert all(a > b for a, b in zip(grid, grid[1:])), 'Sharpe edge is not monotone in costs'
    for _ in range(30):                     # bisection
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if sharpe_edge(mid) > 0 else (lo, mid)
    breakeven_bps = (lo + hi) / 2
    print(f'Breakeven cost (Sharpe edge over 60/40 = 0): {breakeven_bps:,.0f} bps per unit traded')
""")
code("""
# sub-periods: SEGMENTS of the one continuous backtest (weights and holdings carried in from before each
# segment; drawdowns measured within the segment). 2022 = stocks and bonds fell together
periods = {'2006-2015': ('2006-01', '2015-12'), '2016-Oct 2026': ('2016-01', '2026-10'), '2022 only': ('2022-01', '2022-12'),
           '2008 only': ('2008-01', '2008-12')}
sub = {}
for label, (a, b) in periods.items():
    for name in ['Inverse-vol (strategy)', '60/40 (primary benchmark)', 'Equal weight 1/3']:
        p = performance_table(net.loc[a:b, name], net.loc[a:b, '60/40 (primary benchmark)'], rf.loc[a:b])
        sub[(label, name)] = {'Mean (ann.)': p['Annualized mean return'], 'Volatility (ann.)': p['Annualized volatility'],
                              'Sharpe': p['Sharpe ratio'], 'Max drawdown': p['Max drawdown']}
sub_table = pd.DataFrame(sub).T
sub_table.to_csv('outputs/table4_subperiods.csv')
sub_table
""")

md("## 12. Numbers used in the prospectus text")
code("""
numbers = {
    'first_month': str(net.index[0].date()), 'last_month': str(net.index[-1].date()), 'n_months': len(net),
    'breakeven_bps': breakeven_bps,
    'avg_weights': weights.mean().to_dict(), 'latest_weights': weights.iloc[-1].to_dict(),
    'latest_weight_date': str(weights.index[-1].date()),
    'rolling_vol_min': rolling_vol.min().to_dict(), 'rolling_vol_max': rolling_vol.max().to_dict(),
    'rf_mean_annual': float(PERIODS_PER_YEAR * rf.mean()),
    'corr_spy_ief_2022': float(daily_returns.loc['2022', 'SPY'].corr(daily_returns.loc['2022', 'IEF'])),
    'corr_spy_ief_full': float(daily_returns.loc['2006':, 'SPY'].corr(daily_returns.loc['2006':, 'IEF'])),
    'worst_month': {k: float(net[k].min()) for k in net}, 'worst_month_date': {k: str(net[k].idxmin().date()) for k in net},
}
with open('outputs/numbers.json', 'w') as f:
    json.dump(numbers, f, indent=2, default=float)
print(json.dumps(numbers, indent=2, default=float))
""")

md("""
## 13. Notes on the method and limitations (summarised; discussed in the prospectus)
* **Alpha t-statistic:** conventional OLS standard error (no correction for autocorrelation or heteroskedasticity).
* **Costs of the first purchase** are charged in the first month (January 2006) for every portfolio.
* **Selection / hindsight bias:** the three asset classes were chosen for their economic role, but we know today that
  gold did very well after 2005. The three ETFs still trade today: we test today's chosen ETF proxies, so funds that
  were closed or merged are not part of the choice set (a mild form of survivorship bias). Inside the ETFs, the S&P 500
  index itself replaces failing companies, which is part of the investable index return and not a backtest bias.
* **Correlations are ignored** (not full risk parity). In 2022 bonds did not hedge stocks.
* **USD results.** A euro investor also bears EUR/USD risk unless a hedged share class is used; taxes are ignored.
* **Execution:** trading at the month-end close is slightly optimistic; the one-day-lag check above measures this.
* **Past performance does not guarantee future results;** the 2006-2026 window includes a long fall in interest rates
  that helped bonds until 2020.
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                  "language_info": {"name": "python"}, "colab": {"provenance": []}}
nbf.write(nb, OUT)
print(f"Wrote {OUT} with {len(cells)} cells")
