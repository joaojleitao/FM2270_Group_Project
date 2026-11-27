# FM2270 Group Project: permanent rules

Course: 2270 Financial Modeling (MSc Finance, Nova SBE). Deliverables: prospectus PDF (≤7 content pages + cover), a Colab notebook that reproduces every number, and an optional Streamlit app (+2).
Class materials: `D:\Financial Modelling\` are READ-ONLY. Never modify, move, delete or copy them into this repo; reference them by path.
Python env: `D:\envs\fm2270` (Python 3.12 venv; Jupyter kernel "fm2270").

## Strategy (chosen by the group): inverse-volatility ("risk-balanced") portfolio
- At each month-end t, estimate each asset's volatility σ(i,t) from trailing returns up to and including month-end t.
- Weights: w(i,t) = (1/σ(i,t)) / Σⱼ (1/σ(j,t)).
- Apply them ONLY to returns from the first trading day of month t+1. No look-ahead.
- State explicitly that inverse-vol is NOT full risk parity, because it ignores correlations.
- Asset universe, sample, benchmarks and parameters: see `strategy_proposal.md` (AI-suggested; the group must approve it before any backtest code is written).

## Data and reproducibility
- Start and end dates are hard-coded. Results must be reproducible.
- Use adjusted prices (total return; `yfinance` `auto_adjust=True`). Document the source, sample period, frequency and adjustments.
- All data comes through APIs. No data files. The notebook must run in a FRESH Google Colab session with no local files.

## Metrics
- Follow the conventions in `class_materials_index.md` (cite the class file when relevant).
- Beta is NOT annualized. Always state the annualization factor (12 / √12 for monthly) and the risk-free source (FRED TB3MS unless the group decides otherwise).

## Code
- The notebook and `app/strategy.py` use IDENTICAL calculation functions. `tests/test_consistency.py` must pass (`D:\envs\fm2270\Scripts\python.exe -m pytest -q`).
- Keep code simple and commented. Every group member must be able to explain each line.
- After every meaningful change: run the code, update `journal/JOURNAL.md`, regenerate the journal PDF at the end of the session (`python tools/build_journal_pdf.py`), then `git commit` with a clear message.

## Reviews
- Before finalizing any backtest change, run `/codex:adversarial-review` focused on look-ahead bias, survivorship bias, return/weight alignment and metric formulas.
- Use the free-llm-router `reasoning` profile as a third check of the metric formulas (send formulas or short excerpts only; no personal data).

## AI disclosure
- Append EVERY AI use (Claude, Codex, free-LLM router, any chat) to `AI_USE_LOG.md` and to the journal, including how the output was checked.
- Keep the "AI Disclosure Summary" at the top of the journal up to date; it feeds the prospectus disclosure section.
- Ponytail (if installed) applies to code only, never to the journal, the AI-use log or prospectus text.

## Secrets
- Never write API keys or tokens into tracked files, the notebook, the journal or logs. Keys live in Windows user env vars or a git-ignored `.env`.
