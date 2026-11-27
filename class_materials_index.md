# Class Materials Index: 2270 Financial Modeling (Fall 2026)

Class files are in `D:\Financial Modelling\` (READ-ONLY; they are referenced by path and never copied into this repo).
This index was written with Claude Code on 2026-11-27, from text extracted from each file. **Group: please check the conventions against the cited sources.**
The project follows these conventions wherever they exist (see `CLAUDE.md`).

## 1. Files and topics

| File (in `D:\Financial Modelling\`) | Type | Topic |
|---|---|---|
| `Syllabus.pdf` | PDF | Instructors (T. Marchuk, B. Forbes Costa), agenda (W1 intro, W2 bonds/NumPy, W3 pandas, APIs and portfolio strategies, W4 backtesting and optimization, W5 Monte Carlo, W6 review), grading (exam 60%, group project 40%, groups of 5–6, weeks 5–6), Google Colab as the platform, textbooks (Benninga; Hilpisch; Lewinson) |
| `2270_Formulae.pdf` | PDF | Official formula sheet: PV/FV/NPV/IRR/annuity, bond price and duration, **beta, Sharpe ratio, information ratio, high-water mark, drawdown** |
| `Lecture1_Intro.pdf` | PDF | Principles of financial modelling (accuracy, efficiency, documenting data sources, assumptions and methods, interactivity/"what if"), why Python, "Can't I just use AI?" (verify output against financial logic) |
| `Lecture1_financial_calculations.ipynb` | Notebook | Time value of money, PV/NPV step by step, f-string formatting |
| `Lecture1_exercises.ipynb` / `Lecture1_exercises_solutions.ipynb` | Notebook | Annuity, NPV/IRR exercises; loop vs vectorized solutions |
| `Lecture2_python_numpy.ipynb` | Notebook | Python data types, lists, slicing, NumPy arrays, fancy indexing |
| `Lecture2_bond_valuation.ipynb` | Notebook | Vectorized bond pricing, duration, rate sensitivity (SVB example) |
| `Lecture2_exercises.ipynb` / `Lecture2_exercises_with_solutions.ipynb` | Notebook | Bond pricing, duration and immunization exercises |
| `Lecture3_apis_pandas.ipynb` | Notebook | **Data via APIs**: FRED (`fredapi`, and the keyless CSV URL with `pd.read_csv`), Yahoo Finance (`yfinance`, `auto_adjust=True`), the four checks of a download, the `dropna()` pitfall, CoinGecko |
| `Lecture3_portfolio_strategies.ipynb` | Notebook | Portfolio weights, fixed-weight vs buy-and-hold strategies, rebalancing, 1/n benchmark, **alpha/beta, Sharpe, information ratio, drawdowns**, `quantstats` |
| `Lecture4_backtesting.ipynb` | Notebook | **Backtesting**: look-ahead bias and the `.shift(1)` timing convention, survivorship bias, transaction costs and turnover, breakeven cost, hidden daily rebalancing in fixed weights, auditing AI-written backtests |
| `Lecture5_monte_carlo.ipynb` | Notebook | Monte Carlo: LLN, distributions, Markov chains (NBER recessions via FRED CSV), retirement simulation |
| `Lecture5_private_loan.ipynb` | Notebook | Explain-the-code exercise: valuing a private loan with FRED `GS5` yields |
| `lecture_2.pdf` … `lecture_5.pdf` | PDF | In-class quiz slides (Mentimeter-style). Relevant answers: weights sum to 1 (or 0 for self-financing); IR = reward per unit of deviation from the benchmark; log returns `np.log(df).diff(1)`; strategy return = `position.shift(1) * log_rtn` (or `.shift(2)`), never the unshifted position; buy-and-hold has the lowest transaction cost |

## 2. Course conventions (the project MUST follow these)

### 2.1 Returns
- **Log returns** are the course default: `np.log(df) - np.log(df.shift(1))`, or `np.log(df).diff(1)`.
  Sources: `Lecture3_portfolio_strategies.ipynb` §3.2 (code cell 7); `Lecture4_backtesting.ipynb` §4.1–4.2; `lecture_5.pdf` p.4.
- **Cumulative performance:** `log_returns.cumsum().apply(np.exp)`, which starts at 1 (`Lecture4_backtesting.ipynb` §4.1).
- **Portfolio return:** the class computes the 1/n portfolio as weights × asset log returns (`np.dot(weights, returns.T)`, `Lecture3_portfolio_strategies.ipynb` §3.2).
  ⚠ **Note for the group:** a weighted average of log returns is only an approximation of the portfolio log return. Exactly: r_p = log(Σ wᵢ·(e^{rᵢ} − 1) + 1). **Recommendation:** aggregate SIMPLE returns across assets (exact), then convert the portfolio return to log, ln(1 + R_p), if we report log-based metrics. State the choice in the prospectus.
- **Data frequency in class:** monthly via `yf.download(..., interval='1mo')` (`Lecture3_portfolio_strategies.ipynb` §3.2; `Lecture3_apis_pandas.ipynb` §3.2), and daily `interval='1d'` for trading rules (`Lecture4_backtesting.ipynb`).

### 2.2 Annualization (arithmetic scaling)
- **Means scale with time, volatilities with the square root of time** (`Lecture3_portfolio_strategies.ipynb` §3.4, check after code cell 13).
  - Monthly data: mean × **12**, volatility × **√12**. Annualized Sharpe = (12·mean) / (√12·std).
  - Daily data: × **252** trading days, √**252** (`Lecture4_backtesting.ipynb` §4.1: `np.sqrt(252)`, `n_years = len(df)/252`).
- The annualized mean is **arithmetic** (12 × the average monthly return). The course does not define a geometric/CAGR convention. If we also report CAGR, label it clearly as an extra.
- Wrong annualization (×12 for a Sharpe ratio) is one of the course's "AI bugs" (`Lecture4_backtesting.ipynb` §4.4, Bug 2).

### 2.3 Sharpe ratio
- SR = E(R − R_f) / σ(R − R_f) = average excess return / volatility (`2270_Formulae.pdf` p.2; `Lecture3_portfolio_strategies.ipynb` §3.4).
- Must use **excess** returns. Omitting R_f is a flagged bug (`Lecture4_backtesting.ipynb` §4.4, Bug 3; `Lecture3_portfolio_strategies.ipynb` §3.6, Bug 3). Class examples set `r_f = 0` only for simplicity.

### 2.4 Alpha and beta
- Regression: R_t^ex = α + β·R_t^{M,ex} + ε_t, with **both sides in excess of the risk-free rate** (`Lecture3_portfolio_strategies.ipynb` §3.3).
- β = cov(R^ex, R^{M,ex}) / var(R^{M,ex}) (`2270_Formulae.pdf` p.2). α = E[R^ex] − β·E[R^{M,ex}] (`Lecture3_portfolio_strategies.ipynb` §3.3).
- **Alpha is annualized ×12** from monthly data (the class plots `1200 * alpha` as % p.a.). **Beta is not annualized** (it is a ratio).
- The class estimates by hand (cov/var), which gives the same numbers as the OLS slope and intercept. Rolling 60-month estimates are shown, and `qs.stats.rolling_greeks` is used as a cross-check (`Lecture3_portfolio_strategies.ipynb` §3.3, code cells 9 and 11).

### 2.5 Information ratio and tracking error
- Benchmark-mandate version (formula sheet): **IR = E(R − R_b) / σ(R − R_b)** (`2270_Formulae.pdf` p.2).
- Regression version: IR = α / σ(ε) (`Lecture3_portfolio_strategies.ipynb` §3.4). For a benchmark mandate the course uses the non-regression version.
- Tracking error = R − R_b; **tracking error risk = std(R − R_b)**. Annualized IR = (12·mean(R − R_b)) / (√12·std(R − R_b)) (`Lecture3_portfolio_strategies.ipynb` §3.4, code cell 15).

### 2.6 Risk-free rate source
- The course does not prescribe a specific T-bill series. The course's source for rates and macro series is **FRED**:
  - `fredapi` with a personal API key (`Lecture3_apis_pandas.ipynb` §3.1: "get your own" key; the instructor's key in that notebook must not be reused), or
  - the **keyless CSV URL** `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>` read with `pd.read_csv(url, index_col=0, parse_dates=True)` (`Lecture3_apis_pandas.ipynb` §3.4; also `Lecture5_monte_carlo.ipynb` (USREC) and `Lecture5_private_loan.ipynb` (GS5)).
- `Lecture4_backtesting.ipynb` §4.3 uses the TBIL ETF as a "short-term bills" asset in a 60/40 example.
- **Project choice (proposed):** FRED `TB3MS` (3-month T-bill, secondary market, monthly, % p.a.) via the keyless CSV. It needs no key in Colab, and it was verified on 2026-11-27 to run through 2026-10. Monthly rf = TB3MS/100/12 (or ln(1 + TB3MS/100)/12 to match log returns; state which).
  Kenneth French's library (suggested in the setup prompt) is NOT used in class, so FRED is preferred.

### 2.7 Drawdown
- HWM_t = max_{s≤t} P_s; **DD_t = (HWM_t − P_t) / HWM_t**, a positive number; MDD = max_t DD_t (`2270_Formulae.pdf` p.2; `Lecture3_portfolio_strategies.ipynb` §3.5).
- P_t is the cumulative return index (starting at 1). Drawdowns are "the risk your clients actually feel", leading to redemptions and margin calls (`Lecture3_portfolio_strategies.ipynb` §3.5; `lecture_5.pdf` p.3).

### 2.8 Transaction costs and turnover
- Proportional cost: **cost × |change in position|**, subtracted from the period's return: `df['position'].diff(1).abs() * transaction_cost` (`Lecture4_backtesting.ipynb` §4.3). The class example uses 0.5% per change, "a conservative all-in figure for a retail investor".
- **Report turnover and show net-of-cost results.** "Turnover is a tax on your signal… A prospectus that only shows gross returns is not investable." (`Lecture4_backtesting.ipynb` §4.3, breakeven solution).
- A breakeven-cost analysis is the course's suggested robustness exercise (`Lecture4_backtesting.ipynb` §4.3, "Explore").
- Fixed weights imply rebalancing (daily if the formula is applied daily). Make the rebalancing frequency explicit (`Lecture4_backtesting.ipynb` §4.3, "A hidden assumption"; `Lecture3_portfolio_strategies.ipynb` §3.1).

### 2.9 Backtesting practice
- **Timing:** a signal that uses the close of day t can earn returns from t+1 at the earliest. `position.shift(1) * returns` is the minimum (market-on-close assumption, "slightly optimistic"); `shift(2)` is "fully safe"; lag 0 is look-ahead bias (`Lecture4_backtesting.ipynb` §4.1 Takeaway; `lecture_5.pdf` p.6).
- **Biases to discuss** (`Lecture4_backtesting.ipynb` §4.0): look-ahead bias, survivorship bias, outlier treatment, representative sample period, meeting objectives over time (rolling metrics), realistic trading (costs, slippage, spreads).
- **Universe selection with hindsight** is survivorship/selection bias in the research design (`Lecture4_backtesting.ipynb` §4.4 "deeper problem", §4.5 step 8). Justify the asset choice ex ante.
- Plot positions or weights before trusting statistics (`Lecture4_backtesting.ipynb` §4.2).
- Data-snooping: famous parameters were "searched for" on the same history (`Lecture4_backtesting.ipynb` §4.5), so report robustness across parameters.

### 2.10 Data handling
- `yf.download(tickers, start=..., end=..., interval=..., auto_adjust=True, progress=False)['Close']`: adjusted prices (splits and dividends) are "the ones returns must be computed from" (`Lecture3_apis_pandas.ipynb` §3.2).
- Total-return benchmark example: `^SP500TR` (`Lecture3_portfolio_strategies.ipynb` §3.2).
- **Four checks on every download:** shape, date range, missing values, plot (`Lecture3_apis_pandas.ipynb` §3.0, code cell 13).
- `dropna()` on a panel can silently cut the sample to the shortest history (`Lecture3_apis_pandas.ipynb` §3.3, the PLTR example). Handle NaNs knowingly (`Lecture3_portfolio_strategies.ipynb` §3.2).
- Align calendars and timezones: `tz_localize(None)` (`Lecture3_portfolio_strategies.ipynb` §3.2).
- The assignment requires code that fetches data via API; no data files (`Lecture3_apis_pandas.ipynb` §3.0).

## 3. Libraries and coding style used in class
- **Libraries:** `numpy`, `pandas`, `matplotlib.pyplot`, `yfinance`, `quantstats` (`!pip -q install quantstats`, metric cross-checks and tear sheets), `fredapi` / `requests` / `pd.read_csv` for FRED, `pycoingecko` (explore only). `statsmodels` is not used in class: beta and alpha are computed by hand.
- **Platform:** Google Colab (`Syllabus.pdf` p.3). Installs use `!pip -q install ...` inside the notebook.
- **Style:**
  - short cells with a comment header (`# --- The backtest ---`)
  - inline comments on each step
  - vectorized NumPy/pandas instead of loops (loop and vector versions are shown side by side for teaching)
  - `df.loc[:, 'col'] = ...` assignments
  - f-strings with explicit formatting (`f"{x:.2f}"`)
  - explicit "predict / discuss / check" prompts
  - print results with units
- **AI:** AI is allowed, but output must be verified against financial logic ("does this Sharpe ratio pass the smell test?", `Lecture1_Intro.pdf`). Nova's assistant `https://ai.novasbe.pt` is mentioned (`Lecture3_apis_pandas.ipynb` §3.5).

## 4. Where the setup prompt and the course differ
| Topic | Setup prompt suggestion | Course convention | Project choice |
|---|---|---|---|
| Risk-free source | Kenneth French 1-month T-bill or FRED DTB3 | FRED (fredapi or keyless CSV) | **FRED TB3MS, keyless CSV** (monthly, matches monthly metrics) |
| Alpha/beta estimation | OLS (statsmodels) | cov/var by hand (= OLS) | Compute by hand as in class; optionally cross-check with statsmodels OLS for standard errors |
| Return type | not specified | log returns | Log returns for metrics, as in class; simple returns for aggregating across assets (exact); group to confirm |
| IR | annualized active return / annualized TE | E(R−R_b)/σ(R−R_b), annualized 12/√12 | Same (they agree) |
| Transaction costs | 10 bps per unit one-way turnover | cost × abs(Δ position); 0.5% retail example | 10 bps base case for ETFs (justify: liquid ETFs), plus 0/10/25 bps sensitivity and a breakeven cost |
