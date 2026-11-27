# Strategy Proposal: DRAFT FOR GROUP APPROVAL

> **⚠ AI-SUGGESTED.** Drafted by Claude Code (Claude Opus 5.5) on 2026-11-27. It follows the recommendations in the group's `SETUP_PROMPT.md` (Section 9), checked against the course conventions in `class_materials_index.md`.
> **Nothing here is decided until the group discusses and approves it.** Record the decision (and any changes) in `journal/JOURNAL.md`.
> The strategy family is already a group decision: an inverse-volatility ("risk-balanced") portfolio. Everything else below is a proposal.

**Approval status:** ☐ Assets ☐ Sample ☐ Volatility estimate ☐ Benchmarks ☐ Risk-free ☐ Metrics ☐ Costs ☐ Robustness ☐ Client ☐ Implementation ☐ App
**Approved by / date:** _[ ]_

---

## 1. Assets: long histories, clear roles
| Ticker | Asset | Role for the client | Trading since |
|---|---|---|---|
| **SPY** | SPDR S&P 500 ETF (US equities) | Growth engine | Jan 1993 |
| **IEF** | iShares 7–10 Year Treasury Bond ETF | Diversification and recession hedge | Jul 2002 |
| **GLD** | SPDR Gold Shares (physical gold) | Crisis and inflation diversifier | Nov 2004 |

Why these three: liquid, cheap, long histories, and distinct return drivers (equity risk premium, duration, real-asset/crisis hedge).
**Selection bias note (course: `Lecture4_backtesting.ipynb` §4.4):** these are broad asset-class ETFs chosen for their economic role, not single winners picked in hindsight. Say this in the prospectus, and admit that knowing gold's 2005–2026 performance is unavoidable hindsight.

## 2. Sample
- **Data from 2005-01-03**, the first trading day of 2005. GLD has traded since 18 Nov 2004.
- With a 252-trading-day lookback, the first *full* window ends on 3 Jan 2006 (checked with yfinance: 30 Dec 2005 has only 251 returns). The first month-end with a full window is **31 Jan 2006**, so the first strategy weights apply from **1 Feb 2006**.
  (Option: start the data on 2004-12-01. The first full window is then at month-end 30 Nov 2005, weights apply from 1 Dec 2005, and the evaluation can start on a clean calendar year, Jan 2006. Group to choose.)
  All benchmarks are evaluated over the **same** period as the strategy.
- **End date:** the last complete month before submission, hard-coded. At setup (27 Nov 2026) that is **2026-10-31**. If we submit in December, update it once to **2026-11-30** and freeze it.
- Coverage: the 2008 GFC, the 2020 COVID crash, and **2022**, a key stress test because stocks and bonds fell together (inverse-vol, which ignores correlations, gets no help from bonds there).

## 3. Volatility estimate and rebalancing
- At each month-end *t*: σ(i,t) = standard deviation of **daily** returns over the trailing **252 trading days**, up to and including *t*, annualized ×√252 (course: `Lecture4_backtesting.ipynb` uses 252).
- Weights w(i,t) = (1/σ(i,t)) / Σⱼ(1/σ(j,t)), long-only and summing to 1.
- **Timing:** weights decided with the close of month-end *t* apply from the first trading day of month *t+1*. This is the course's `shift(1)` convention (market-on-close at month-end), which the course calls "slightly optimistic". A `shift(2)`-style robustness check (trade on the second trading day) is cheap to add (`Lecture4_backtesting.ipynb` §4.1).
- **Monthly rebalancing** to the new target weights. Between rebalances the weights **drift** with prices (buy-and-hold within the month). This avoids the "hidden daily rebalancing" in a fixed-weights formula (`Lecture4_backtesting.ipynb` §4.3).
- Not full risk parity: correlations are ignored. Say so explicitly.

## 4. Benchmarks
- **Primary: 60/40 SPY/IEF, rebalanced monthly.** Same building blocks, so it isolates the allocation rule; it is also the classic "moderate" portfolio a wealth manager would offer.
- **Secondary: equal-weight (1/3) SPY/IEF/GLD, rebalanced monthly.** It separates the effect of *adding gold* from the effect of *inverse-vol weighting* (the course's 1/n benchmark, `Lecture3_portfolio_strategies.ipynb` §3.2).
- **Context: SPY alone** (buy-and-hold).
- Benchmarks use the same rebalancing dates and the same cost model, for a fair comparison.

## 5. Risk-free rate
- **FRED `TB3MS`** (3-month T-bill, secondary market, monthly, % p.a.) via the **keyless CSV URL**, as in `Lecture3_apis_pandas.ipynb` §3.4. No API key is needed in Colab, so the graders can run the notebook. Verified available through 2026-10 on 2026-11-27.
- Monthly rf: ln(1 + TB3MS/100)/12, consistent with log returns (or TB3MS/100/12 if we use simple returns; state the choice). TB3MS is quoted on a discount basis. The difference from a bond-equivalent yield is a few bps p.a. and can be ignored, but say so.
- Timing: the rf for month t+1 is the TB3MS value of month t+1, i.e. the rate earned over that month. That is not look-ahead, because rf is a benchmark rate, not a trading signal.
- The Kenneth French library (an alternative in the setup prompt) is not used in class, and it was only updated through 2026-09 when checked, so FRED is preferred.

## 6. Performance measures (course conventions, `class_materials_index.md` §2)
All computed on **monthly** returns, over the common sample.
| Measure | Definition | Annualization |
|---|---|---|
| Average return | mean of monthly returns | ×12 (arithmetic) |
| Volatility | std of monthly returns | ×√12 |
| Sharpe ratio | mean(R − R_f) / std(R − R_f) | (12·mean)/(√12·std) |
| Beta | cov(R−R_f, R_b−R_f) / var(R_b−R_f) vs the **primary benchmark** | **not annualized** |
| Alpha | mean(R−R_f) − β·mean(R_b−R_f) | ×12 |
| Information ratio | mean(R − R_b) / std(R − R_b) (formula sheet version) | (12·mean)/(√12·std) |
| Tracking error | std(R − R_b) | ×√12 |
| Max drawdown | max (HWM_t − P_t)/HWM_t on the cumulative index | n/a |
| Turnover | average Σᵢ\|Δwᵢ\| per rebalance (see §7 for the definition) | ×(rebalances per year) for annual |
Also report gross and net-of-cost versions, and optionally CAGR (labelled as an extra; not a course convention).
**Return type (group decision):** the course uses log returns. Proposal: compute **portfolio** returns from asset **simple** returns (exact aggregation), convert to log for metrics if we follow the course's log convention, and state it.
Alpha and beta are computed by hand (cov/var), as in class. Optionally cross-check with `statsmodels` OLS (it also gives standard errors / t-stats, useful to say whether alpha is statistically meaningful).

## 7. Transaction costs
- **Base case: 10 bps on every unit traded:** cost_t = 0.0010 × Σᵢ |w(i,t)_target − w(i,t)_drifted|, deducted at each rebalance. This is the course's "cost × |change in position|" model (`Lecture4_backtesting.ipynb` §4.3), where every buy AND every sell pays the cost.
  ⚠ **Definition to state in the prospectus:** "one-way turnover" is often defined as ½·Σ|Δw| (only the buys, or only the sells). Under that definition, "10 bps per unit of one-way turnover" would charge half as much. We propose the course's model above (more conservative), and reporting turnover as Σ|Δw| per rebalance.
  Justification: very liquid ETFs (tight spreads, low commissions at EU brokers). It is lower than the course's 0.5% retail single-stock example; say why.
- Show **gross and net** results, and the **breakeven cost** at which the strategy's edge vs the primary benchmark disappears (course "Explore" exercise).
- ETF expense ratios are already in the ETF prices (total-return NAV). Say this.

## 8. Robustness checks
- Lookback: **3 / 6 / 12 months** (63 / 126 / 252 trading days).
- Rebalancing: **monthly vs quarterly**.
- Costs: **0 / 10 / 25 bps** (+ breakeven).
- Optional: execution lag (+1 day), sub-period results (2006–2015 vs 2016–2026; 2022 alone), and rolling 36-month Sharpe/beta (course: rolling metrics, `Lecture3_portfolio_strategies.ipynb` §3.3, `Lecture4_backtesting.ipynb` §4.0).

## 9. Target client (proposal)
Moderate-risk retail or wealth-management clients in **Portugal**, with a **5+ year horizon**, who want equity-like long-run growth with **smaller drawdowns** than an equity portfolio. They are uncomfortable with 50% crashes (cf. SPY 2008) but accept moderate volatility.
Objectives: steady growth above inflation. Risk attitude: moderate, drawdown-averse. Liquidity: daily (ETFs).

## 10. Implementation
- **EU retail investors generally cannot buy US-domiciled ETFs** (no PRIIPs KID). Use **UCITS equivalents**, e.g. an S&P 500 UCITS ETF (such as iShares Core S&P 500 UCITS or Vanguard S&P 500 UCITS), a 7–10y US Treasury UCITS ETF (such as iShares $ Treasury Bond 7–10yr UCITS), and a physical gold ETC. _[Group to verify exact products, tickers, TERs and domicile before citing them.]_
- **Currency:** the backtest is in **USD**. A EUR investor bears EUR/USD risk, unless they use EUR-hedged share classes (which have hedging costs). Say this clearly; optionally show a EUR-converted version as a robustness check.
- Rebalancing operations: monthly orders at month-end close (or the next open); minimum trade sizes; taxes are out of scope (say so).

## 11. App (+2 marks)
- Sliders/controls: **lookback window**, **rebalancing frequency**, **transaction cost**, **start date**.
- Outputs: cumulative chart (all start at 1) vs the benchmarks, and the metrics table.
- Uses `app/strategy.py` (identical to the notebook; `tests/test_consistency.py`).
- Deployed on Streamlit Community Cloud from the GitHub repo; both URLs go in the prospectus and the notebook.

## 12. Data robustness
- **Primary:** `yfinance` with `auto_adjust=True` (as in class). The download cell must fail loudly with a clear message if data is missing or the date range is short (the four checks).
- **Fallback (documented, untested at setup):** the **Tiingo** API (free key, adjusted close incl. dividends and splits), with the key read from Colab Secrets (`google.colab.userdata`), never hard-coded.
  Stooq, a common keyless alternative, was tested on 2026-11-27 and failed: it now blocks scripted downloads with a JavaScript challenge, and `pandas-datareader` 0.11 no longer supports it.
  Note: graders run the notebook without our keys, so the primary yfinance path must work in a fresh Colab session. Test it right before submitting.

## 13. Open questions for the group
1. Approve the assets (or add one, e.g. a broad commodity or TIPS ETF?), and the 2005-01-03 vs 2004-12-01 data start.
2. Log vs simple returns for the metrics (see §6).
3. Base cost of 10 bps: OK?
4. Client profile wording.
5. End date: 2026-10-31 or 2026-11-30, depending on the submission date.
