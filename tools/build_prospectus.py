"""Build prospectus/FM2270_Prospectus.pdf from the notebook's outputs (notebook/outputs/).

Every number in the text and tables is read from the files the notebook writes, so the prospectus
cannot drift from the notebook. Steps:
  1. run the notebook (jupyter nbconvert --execute ...), which writes notebook/outputs/
  2. python tools/build_prospectus.py   -> prospectus/FM2270_Prospectus.html and .pdf (Chrome headless)
"""
import base64
import json
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTS = ROOT / "notebook" / "outputs"
DEST = ROOT / "prospectus"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

GROUP_NAME = "Project Group C"
MEMBERS = "[Full name, student number]"
REPO_URL = "https://github.com/joaojleitao/FM2270_Group_Project"
APP_URL = "[STREAMLIT APP URL]"
DATE = "November 2026"

perf = pd.read_csv(OUTS / "table1_performance.csv", index_col=0)
robust = pd.read_csv(OUTS / "table2_robustness.csv", index_col=0)
costs = pd.read_csv(OUTS / "table3_costs.csv", index_col=0)
sub = pd.read_csv(OUTS / "table4_subperiods.csv", index_col=[0, 1])
gn = pd.read_csv(OUTS / "table_gross_net.csv", index_col=0)
wstats = pd.read_csv(OUTS / "weight_stats.csv", index_col=0)
yearly = pd.read_csv(OUTS / "yearly_returns.csv", index_col=0)
N = json.loads((OUTS / "numbers.json").read_text())

S, B, E, M = "Inverse-vol (strategy)", "60/40 (primary benchmark)", "Equal weight 1/3", "SPY buy & hold"
pct = lambda x, d=1: f"{x * 100:.{d}f}%"
num = lambda x, d=2: f"{x:.{d}f}"
P = lambda row, col=S: perf.loc[row, col]


def img(name):
    return "data:image/png;base64," + base64.b64encode((OUTS / name).read_bytes()).decode()


def table_html(df, fmt, first_col="", highlight_col=None):
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for idx, r in df.iterrows():
        cells = []
        for c in df.columns:
            v = r[c]
            cls = ' class="hl"' if c == highlight_col else ""
            cells.append(f"<td{cls}>{'–' if pd.isna(v) else fmt(idx, c, v)}</td>")
        rows.append(f"<tr><td class='rowh'>{idx}</td>{''.join(cells)}</tr>")
    return f"<table><thead><tr><th>{first_col}</th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


PCT_ROWS = {"Annualized mean return", "Annualized volatility", "Alpha (annualized)", "Tracking error (annualized)",
            "Max drawdown", "Average annual turnover"}
fmt_perf = lambda i, c, v: pct(v, 2) if i in PCT_ROWS else num(v)
t1 = perf.rename(columns={S: "Inverse-vol<br>(strategy)", B: "60/40<br>(benchmark)", E: "Equal weight<br>1/3", M: "SPY<br>buy &amp; hold"})
table1 = table_html(t1, fmt_perf, "Jan 2006 – Oct 2026, net of costs", "Inverse-vol<br>(strategy)")
table2 = table_html(robust, fmt_perf, "Strategy variant")

sub_rows = []
for (period, name), r in sub.iterrows():
    short = {S: "Inverse-vol", B: "60/40", E: "Equal weight"}[name]
    sub_rows.append(f"<tr><td class='rowh'>{period}</td><td>{short}</td><td>{pct(r['Mean (ann.)'])}</td>"
                    f"<td>{pct(r['Volatility (ann.)'])}</td><td>{num(r['Sharpe'])}</td><td>{pct(r['Max drawdown'])}</td></tr>")
table3 = ("<table><thead><tr><th>Period</th><th>Portfolio</th><th>Mean (ann.)</th><th>Volatility</th><th>Sharpe</th>"
          "<th>Max DD</th></tr></thead><tbody>" + "".join(sub_rows) + "</tbody></table>")

aw, lw = N["avg_weights"], N["latest_weights"]
y = lambda yr, col: yearly.loc[int(yr), col]
be = N["breakeven_bps"]
be_txt = "more than 2,000 bps" if be == float("inf") else f"about {be:,.0f} bps"

html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Risk-Balanced Portfolio Prospectus</title>
<style>
@page {{ size: A4; margin: 15mm 16mm 14mm 16mm; }}
body {{ font-family: 'Segoe UI', Calibri, Arial, sans-serif; font-size: 9.6pt; line-height: 1.38; color: #1d1d1d; }}
h1 {{ font-size: 15pt; color: #1f4e79; margin: 0 0 4pt; }}
h2 {{ font-size: 11.5pt; color: #1f4e79; border-bottom: 1.2pt solid #1f4e79; padding-bottom: 1pt; margin: 10pt 0 4pt; }}
h3 {{ font-size: 10pt; margin: 6pt 0 2pt; color: #333; }}
p {{ margin: 0 0 5pt; text-align: justify; }}
ul {{ margin: 0 0 5pt; padding-left: 14pt; }} li {{ margin-bottom: 2pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 3pt 0 4pt; }}
th, td {{ border-bottom: 0.6pt solid #bbb; padding: 2pt 4pt; text-align: right; }}
th {{ background: #eaf0f7; color: #1f4e79; }} td.rowh, th:first-child {{ text-align: left; }}
td.hl {{ background: #f3f7fb; font-weight: 600; }}
.cap {{ font-size: 8.2pt; color: #555; margin: 1pt 0 6pt; text-align: left; }}
.box {{ background: #f3f7fb; border-left: 3pt solid #1f4e79; padding: 5pt 8pt; margin: 4pt 0 6pt; }}
.two {{ display: flex; gap: 12pt; }} .two > div {{ flex: 1; }}
img.fig {{ width: 100%; }}
.page {{ page-break-after: always; }}
.cover {{ height: 255mm; display: flex; flex-direction: column; justify-content: center; text-align: center; }}
.cover h1 {{ font-size: 26pt; }} .cover .sub {{ font-size: 13pt; color: #444; margin-bottom: 26pt; }}
.cover table {{ width: 75%; margin: 0 auto; font-size: 10.5pt; }} .cover td {{ text-align: left; border: none; padding: 3pt; }}
.small {{ font-size: 8.2pt; }}
a {{ color: #1f4e79; }}
</style></head><body>

<div class="page cover">
  <h1>Risk-Balanced Portfolio</h1>
  <div class="sub">An inverse-volatility allocation to US equities, US Treasuries and gold<br>Investor prospectus</div>
  <table>
    <tr><td><b>Moodle group</b></td><td>{GROUP_NAME}</td></tr>
    <tr><td><b>Group members</b></td><td>{MEMBERS}</td></tr>
    <tr><td><b>Course</b></td><td>2270 Financial Modeling, MSc in Finance, Nova SBE</td></tr>
    <tr><td><b>Date</b></td><td>{DATE}</td></tr>
    <tr><td><b>Notebook &amp; source code</b></td><td><a href="{REPO_URL}">{REPO_URL}</a></td></tr>
    <tr><td><b>Interactive app</b></td><td>{APP_URL}</td></tr>
  </table>
  <p class="small" style="margin-top:30pt;text-align:center">Academic project. All results are hypothetical backtests on historical data
  (January 2006 – October 2026) and do not guarantee future performance. This document is not investment advice.</p>
</div>

<h1>1. The portfolio at a glance</h1>
<div class="box">
<b>What it holds:</b> three exchange-traded funds: US large-cap equities (SPY), 7–10 year US Treasury bonds (IEF) and physical gold (GLD).<br>
<b>How it is managed:</b> every month-end, each asset receives a weight inversely proportional to its recent volatility, so that the calmer assets
(usually bonds) get more capital and the more volatile ones (equities, gold) get less. Holdings are rebalanced monthly.<br>
<b>Backtest, Jan 2006 – Oct 2026 (net of costs):</b> {pct(P('Annualized mean return'))} average annual return with {pct(P('Annualized volatility'))}
volatility, a Sharpe ratio of {num(P('Sharpe ratio'))} and a worst peak-to-trough loss of {pct(P('Max drawdown'))}, compared with
{pct(P('Annualized mean return', B))}, {pct(P('Annualized volatility', B))}, {num(P('Sharpe ratio', B))} and {pct(P('Max drawdown', B))} for a classic 60/40 stock/bond portfolio.<br>
<b>In one sentence:</b> a lower-risk alternative to a 60/40 portfolio that gave up about {pct(P('Annualized mean return', B) - P('Annualized mean return'))}
of return per year in exchange for roughly a quarter less volatility and about half the maximum drawdown.
</div>

<h2>2. Target client</h2>
<p><b>Who.</b> Moderate-risk private investors in Portugal and other euro-area countries, served directly or through a wealth manager or financial
adviser: for example professionals in their 40s and 50s building retirement savings, or recent retirees who keep part of their wealth invested.</p>
<p><b>Objectives and horizon.</b> Steady growth of capital above inflation over a horizon of at least five years, with a smoother ride than an
equity portfolio. The client does not need income from the portfolio and values daily liquidity.</p>
<p><b>Attitude to risk.</b> Moderate and, above all, <i>drawdown-averse</i>: the client can live with ordinary fluctuations but would be tempted to
sell after a loss like the 51% fall of US equities in 2008–09, or even the 29% fall of a 60/40 portfolio. Our portfolio is designed for this client:
the risk level is kept roughly stable by construction, and three different return drivers are combined so that no single market dominates.</p>

<h2>3. Underlying assets</h2>
<table><thead><tr><th>ETF (US-listed, used in the backtest)</th><th style="text-align:left">Asset class and role for the client</th><th>Expense ratio</th><th>Trading since</th></tr></thead><tbody>
<tr><td class="rowh"><b>SPY</b> SPDR S&amp;P 500 ETF Trust</td><td class="rowh">US large-cap equities: the long-run growth engine</td><td>0.09%</td><td>Jan 1993</td></tr>
<tr><td class="rowh"><b>IEF</b> iShares 7–10 Year Treasury Bond ETF</td><td class="rowh">US government bonds: income, and usually a hedge in recessions</td><td>0.15%</td><td>Jul 2002</td></tr>
<tr><td class="rowh"><b>GLD</b> SPDR Gold Shares</td><td class="rowh">Physical gold: diversifier in crises and against inflation and currency debasement</td><td>0.40%</td><td>Nov 2004</td></tr>
</tbody></table>
<p>The three assets are liquid, cheap and have long histories, and their returns come from different sources: the equity risk premium, the term
premium on government bonds, and gold's role as a store of value. Historically their correlations have been low or negative
(daily correlation between SPY and IEF over the sample: {num(N['corr_spy_ief_full'])}), which is what makes a combination less risky than any
one of them. They were chosen for their economic role as broad asset classes, not because of their past returns (see Section 9).</p>

<h2>4. Allocation rule</h2>
<p>At the last trading day of each month <i>t</i>, we estimate the volatility σ<sub>i,t</sub> of each asset as the standard deviation of its daily
returns over the previous 252 trading days (about 12 months), up to and including day <i>t</i>. The weights are</p>
<p style="text-align:center"><b>w<sub>i,t</sub> = (1/σ<sub>i,t</sub>) / Σ<sub>j</sub> (1/σ<sub>j,t</sub>)</b>,  &nbsp; long-only, summing to 100%.</p>
<p>The new weights are bought at the month-end close and earn returns from the first trading day of month <i>t</i>+1, so every decision uses only
information available at the time. Between rebalancing dates the holdings drift with prices (no daily trading). <b>Motivation:</b> an asset
that is twice as volatile receives half the capital, so each asset contributes a similar amount of stand-alone risk. A 60/40 portfolio looks
balanced in capital but is not balanced in risk: equities are about three times as volatile as 7–10 year bonds and drive most of its fluctuations.
Inverse volatility is a simple, transparent step towards risk balancing that needs no return forecasts, which are notoriously unreliable.
<b>It is not full risk parity:</b> it ignores correlations, so risk contributions are only approximately equal.</p>
<img class="fig" src="{img('fig2_weights.png')}">
<p class="cap">Figure 2. Strategy weights at each month-end. Average: SPY {pct(aw['SPY'], 0)}, IEF {pct(aw['IEF'], 0)}, GLD {pct(aw['GLD'], 0)}.
Ranges: SPY {pct(wstats.loc['SPY', 'Min'], 0)}–{pct(wstats.loc['SPY', 'Max'], 0)}, IEF {pct(wstats.loc['IEF', 'Min'], 0)}–{pct(wstats.loc['IEF', 'Max'], 0)},
GLD {pct(wstats.loc['GLD', 'Min'], 0)}–{pct(wstats.loc['GLD', 'Max'], 0)}. Latest ({N['latest_weight_date']}): SPY {pct(lw['SPY'], 0)}, IEF {pct(lw['IEF'], 0)}, GLD {pct(lw['GLD'], 0)}.</p>

<h2>5. Data and backtest method</h2>
<ul>
<li><b>Source and adjustments:</b> daily prices from Yahoo Finance through the <code>yfinance</code> API, adjusted for splits and dividends
(<code>auto_adjust=True</code>), so returns are total returns after the ETFs' expense ratios. Risk-free rate: 3-month US Treasury bill
(FRED series TB3MS, monthly, % p.a.), converted to a monthly rate ln(1 + TB3MS/100)/12; average {pct(N['rf_mean_annual'], 2)} p.a. over the sample.</li>
<li><b>Sample:</b> prices from 1 December 2004 (GLD's history starts in November 2004) to 31 October 2026, the last complete month, both fixed in
the code. The first 12-month volatility estimate is available on 30 December 2005, so the evaluation period is <b>January 2006 – October 2026
({N['n_months']} months)</b>. It includes the 2008 financial crisis, the 2020 COVID crash and 2022, when stocks and bonds fell together.</li>
<li><b>Frequency:</b> daily data to estimate volatility and to let holdings drift; monthly returns for all performance measures.</li>
<li><b>Portfolio returns:</b> each portfolio starts in cash on 30 December 2005; asset weights are applied to simple returns (exact aggregation);
performance measures use monthly log returns, as in the course. Costs: 10 basis points on every unit bought or sold,
cost = 0.10% × Σ|w<sub>target</sub> − w<sub>drifted</sub>|, deducted at each rebalance, including the first purchase.</li>
<li><b>Benchmarks</b> (same costs and dates): the <b>primary benchmark is 60/40 SPY/IEF rebalanced monthly</b>, the standard moderate portfolio our
client would otherwise hold. A 1/3 equal-weight mix of the same three ETFs isolates the effect of the weighting rule from the effect of adding gold.
SPY alone (buy and hold) shows the equity-only alternative.</li>
</ul>

<h2>6. Historical performance</h2>
<img class="fig" src="{img('fig1_cumulative.png')}">
<p class="cap">Figure 1. Growth of $1 invested on 30 December 2005, net of transaction costs (log scale; all series start at 1). Source: notebook Section 8.</p>
{table1}
<p class="cap">Table 1. Performance measures, monthly data, net of costs. Mean return and volatility are annualized as 12 × mean and √12 × standard deviation of
monthly log returns. Sharpe ratio = annualized mean excess return over the T-bill rate divided by annualized volatility of excess returns.
Beta and alpha come from regressing each portfolio's monthly excess return on the 60/40 benchmark's excess return (cov/var, as in class);
<b>beta is not annualized</b>, alpha is ×12. Information ratio = 12·mean(R − R<sub>60/40</sub>) / (√12·std(R − R<sub>60/40</sub>)); tracking error
= √12·std(R − R<sub>60/40</sub>). Maximum drawdown = largest fall from a previous peak of the cumulative value. Turnover = Σ|Δw| per year, excluding the first purchase.</p>

<h2>7. What the numbers mean for the client</h2>
<ul>
<li><b>Average return ({pct(P('Annualized mean return'))} p.a.).</b> Lower than the 60/40 ({pct(P('Annualized mean return', B))}) and the equal-weight
mix ({pct(P('Annualized mean return', E))}): $1 grew to ${num(P('Final value of $1'))} versus ${num(P('Final value of $1', B))} for the 60/40.
The strategy holds on average only {pct(aw['SPY'], 0)} in equities, the best-performing asset of the period, so the client gives up return.</li>
<li><b>Volatility ({pct(P('Annualized volatility'))}).</b> About a quarter lower than the 60/40 ({pct(P('Annualized volatility', B))}) and less than
half of SPY ({pct(P('Annualized volatility', M))}). Risk was also more stable: the 36-month rolling volatility stayed between
{pct(N['rolling_vol_min'][S])} and {pct(N['rolling_vol_max'][S])}, versus {pct(N['rolling_vol_min'][B])}–{pct(N['rolling_vol_max'][B])} for the 60/40.
A stable risk level is what a moderate client needs to stay invested.</li>
<li><b>Sharpe ratio ({num(P('Sharpe ratio'))}).</b> Excess return per unit of risk was slightly higher than the 60/40 ({num(P('Sharpe ratio', B))}) and
SPY ({num(P('Sharpe ratio', M))}), but slightly lower than the naive equal-weight mix ({num(P('Sharpe ratio', E))}). The honest reading: most of the
risk-adjusted benefit comes from <i>adding gold</i> to stocks and bonds; inverse-volatility weighting then trades some of that return for lower
risk. The difference of {num(P('Sharpe ratio') - P('Sharpe ratio', B))} with the 60/40 is small relative to sampling noise over 21 years.</li>
<li><b>Beta ({num(P('Beta (not annualized)'))}, not annualized).</b> When the 60/40 portfolio's excess return moves by 1%, the strategy's moves on
average by about {num(P('Beta (not annualized)'))}%: the client's wealth is roughly half as sensitive to the stock/bond market as a 60/40 investor's.</li>
<li><b>Alpha ({pct(P('Alpha (annualized)'), 2)} p.a.).</b> After adjusting for its lower beta, the strategy earned {pct(P('Alpha (annualized)'), 2)} per
year more than a mix of the 60/40 and T-bills with the same beta. The (conventional OLS) t-statistic of {num(P('Alpha t-stat'))} is below 1.96, so the alpha is
<b>not statistically significant</b> at the 5% level, and it mostly reflects gold's strong performance, not skill.</li>
<li><b>Information ratio ({num(P('Information ratio'))}) and tracking error ({pct(P('Tracking error (annualized)'))}).</b> Measured directly against the
60/40, the strategy lost {num(-P('Information ratio'))} units of return per unit of deviation. A client who judges the portfolio by whether it
<i>beats</i> a 60/40 each year will be disappointed; this is a lower-risk product, not a higher-return one.</li>
<li><b>Maximum drawdown ({pct(P('Max drawdown'))}).</b> The deepest loss from a previous peak was about half that of the 60/40
({pct(P('Max drawdown', B))}) and a third of SPY ({pct(P('Max drawdown', M))}). In calendar year 2008 the strategy gained {pct(y('2008', S))} while the 60/40
lost {pct(-y('2008', B))}; its worst month was {pct(-N['worst_month'][S])} (October 2008) versus {pct(-N['worst_month'][B])} for the 60/40.
For a drawdown-averse client, this is the key result.</li>
</ul>
<img class="fig" src="{img('fig3_drawdowns.png')}">
<p class="cap">Figure 3. Drawdowns: percentage below the previous peak of each portfolio's cumulative value, net of costs.</p>

<h2>8. Robustness of the results</h2>
<p>Parameters such as a 12-month window can be chosen, consciously or not, because they worked in the past. Table 2 shows that the conclusions do
not depend on them: with 3- or 6-month windows, quarterly rebalancing, or trading one day later (at the close of the first trading day of
each month), the Sharpe ratio stays between {num(robust.loc['Sharpe ratio'].min())} and {num(robust.loc['Sharpe ratio'].max())}, volatility near
{pct(P('Annualized volatility'), 0)} and the maximum drawdown near {pct(P('Max drawdown'), 0)}.</p>
{table2}
<p class="cap">Table 2. Strategy variants, January 2006 – October 2026, net of 10 bps costs, measured against the 60/40 benchmark.</p>
<p><b>Sub-periods.</b> The strategy did best when it mattered most for a cautious client (2006–2015, which includes 2008), and lagged in the strong
equity market of 2016–2026. 2022 was the hardest year for any bond-heavy portfolio: stocks and bonds fell together (daily SPY–IEF correlation
{num(N['corr_spy_ief_2022'])} in 2022 versus {num(N['corr_spy_ief_full'])} over the whole sample) and the strategy lost {pct(-y('2022', S))},
less than the 60/40 ({pct(-y('2022', B))}) but more than in 2008.</p>
{table3}
<p class="cap">Table 3. Sub-period results: segments of the same continuous backtest (net of costs). Mean = 12 × average monthly log return; maximum drawdown
measured within each segment. The text quotes calendar-year (compounded) returns, which differ slightly from annualized log means.</p>

<h2>9. Implementation, costs and risks</h2>
<p><b>Rebalancing and costs.</b> Rebalancing is monthly, with three orders at the month-end close. Weights change slowly (Figure 2), so annual turnover
is only {pct(P('Average annual turnover'), 0)} of the portfolio, and costs reduced the return by just {pct(gn.loc[S, 'Cost drag (ann.)'], 2)} a year
(gross {pct(gn.loc[S, 'Gross mean (ann.)'], 2)}, net {pct(gn.loc[S, 'Net mean (ann.)'], 2)}). With 50 bps per unit traded the Sharpe ratio would be
{num(costs.loc['50 bps', 'Strategy Sharpe'])}, and the Sharpe advantage over the 60/40 only disappears at {be_txt} per unit traded, far above
realistic costs for these ETFs. Quarterly rebalancing (Table 2) is a cheaper option for small accounts with little loss of performance.</p>
<p><b>Investing from Portugal.</b> EU retail investors generally cannot buy US-domiciled ETFs (they have no PRIIPs key information document), so the
portfolio would be implemented with UCITS equivalents: an S&amp;P 500 UCITS ETF, a US Treasury 7–10 year UCITS ETF and a physically backed gold ETC
(for example from the iShares, Vanguard, Invesco or Xtrackers ranges; product, cost and domicile to be checked in each key information document).
The backtest is in US dollars: a euro investor also bears EUR/USD risk unless euro-hedged share classes are used, at an extra cost. Taxes are not modelled.</p>
<p><b>Main risks and limitations.</b></p>
<ul>
<li><b>Concentration:</b> on average {pct(aw['IEF'], 0)} of the capital is in one bond fund. The portfolio is exposed to rising interest rates and
inflation, as 2022 showed; it also holds only US assets plus gold.</li>
<li><b>Correlation risk:</b> the rule ignores correlations. When stocks and bonds fall together, the diversification the client relies on weakens.</li>
<li><b>Volatility is backward-looking:</b> weights react only after volatility rises, so a sudden crash is not avoided (e.g. March 2020).</li>
<li><b>Look-ahead bias:</b> avoided by construction: the weights at month-end <i>t</i> use data up to <i>t</i> only and are applied from the next trading day;
the notebook checks this by recomputing the weights with the data cut at <i>t</i>. Trading exactly at the close is slightly optimistic; the one-day-lag
test in Table 2 shows the effect is negligible.</li>
<li><b>Survivorship and selection bias:</b> the backtest uses three broad ETFs that still trade today; funds that closed are not in the choice set,
and our choice of asset classes is made with today's knowledge. The largest such effect is gold, which rose strongly over the sample: the results
would be weaker without it. Inside SPY, the index replacing failing companies is part of the investable return, not a bias of the backtest.</li>
<li><b>Sample dependence:</b> 2006–2026 includes a long decline in interest rates, which helped bonds until 2020. Past performance does not guarantee future results.</li>
</ul>

<h2>10. Interactive app</h2>
<p>An interactive app lets the investor change the <b>volatility lookback</b> (1–24 months), the <b>rebalancing frequency</b>, the <b>transaction cost</b>
and the <b>start year</b>, and see the resulting cumulative performance, weights and full performance table against the same benchmarks. It imports
the same calculation functions as the notebook (an automated test checks they are identical), and its default settings reproduce Table 1.
App: {APP_URL} · Source code, requirements and run instructions: <a href="{REPO_URL}">{REPO_URL}</a>.</p>
APP_SCREENSHOT

<h2>11. Generative-AI disclosure</h2>
<p class="small">The group chose the inverse-volatility strategy. <b>Claude Code</b> (Anthropic, model Claude Opus 5.5) was used to set up the Python
environment and repository, to summarise the course conventions from the class materials, to draft the strategy specification (assets, benchmarks,
sample and costs, from the group's brief), to write the backtest code, the notebook and the Streamlit app, and to draft this prospectus.
<b>OpenAI Codex</b> was used as an independent reviewer of the code for look-ahead bias, alignment and formula errors. Outputs were checked by running all
code, by automated tests (an independent day-by-day re-implementation of the backtest; hand-computed Sharpe, beta, alpha and information ratio;
identical code in notebook and app), by a look-ahead check in the notebook, and against the course formula sheet and lecture notebooks.
The group remains responsible for understanding the code and for the strategy, results and conclusions. A full log is in the repository (AI_USE_LOG.md and journal).</p>

<h2>12. References</h2>
<p class="small">Asness, C., Frazzini, A. &amp; Pedersen, L. H. (2012). Leverage aversion and risk parity. <i>Financial Analysts Journal</i>, 68(1), 47–59.<br>
Maillard, S., Roncalli, T. &amp; Teïletche, J. (2010). The properties of equally weighted risk contribution portfolios. <i>Journal of Portfolio Management</i>, 36(4), 60–70.<br>
Moreira, A. &amp; Muir, T. (2017). Volatility-managed portfolios. <i>Journal of Finance</i>, 72(4), 1611–1644.<br>
2270 Financial Modeling course materials (Nova SBE, 2026): formula sheet; Lecture 3 (APIs and pandas; portfolio strategies); Lecture 4 (backtesting).<br>
Data: Yahoo Finance via the <code>yfinance</code> Python package (adjusted prices); Federal Reserve Bank of St. Louis, FRED series TB3MS (3-Month Treasury Bill Secondary Market Rate).</p>
</body></html>"""

shot = DEST / "app_screenshot.png"
html = html.replace("APP_SCREENSHOT", f'<img class="fig" style="width:88%;margin-left:6%;border:0.6pt solid #bbb" src="data:image/png;base64,'
                    f'{base64.b64encode(shot.read_bytes()).decode()}"><p class="cap">Figure 4. The app with its default settings.</p>'
                    if shot.exists() else "")
DEST.mkdir(exist_ok=True)
out_html = DEST / "FM2270_Prospectus.html"
out_html.write_text(html, encoding="utf-8")
out_pdf = DEST / "FM2270_Prospectus.pdf"
import tempfile  # a throw-away Chrome profile, so a Chrome window that is already open does not interfere
import time
out_pdf.unlink(missing_ok=True)
profile = tempfile.mkdtemp()
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={profile}",
                f"--print-to-pdf={out_pdf}", out_html.as_uri()], check=True, capture_output=True, timeout=180)
for _ in range(120):  # Chrome may return before the PDF is fully written: wait until its size is stable
    if out_pdf.exists() and out_pdf.stat().st_size > 0:
        size = out_pdf.stat().st_size
        time.sleep(1.5)
        if out_pdf.stat().st_size == size:
            break
    time.sleep(0.5)
else:
    raise RuntimeError("Chrome did not write the PDF")

import pymupdf  # count pages and stamp page numbers (cover not numbered)
doc = pymupdf.open(str(out_pdf))
for i, page in enumerate(doc):
    if i == 0:
        continue
    r = page.rect
    page.insert_textbox(pymupdf.Rect(0, r.height - 28, r.width, r.height - 14), f"{i}",
                        fontsize=8, align=pymupdf.TEXT_ALIGN_CENTER)
tmp = out_pdf.with_suffix(".tmp.pdf")
doc.save(str(tmp)); doc.close(); tmp.replace(out_pdf)
n = pymupdf.open(str(out_pdf)).page_count
print(f"Wrote {out_pdf}: {n} pages = cover + {n - 1} content pages")
