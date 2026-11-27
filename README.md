# FM 2270 Financial Modeling: Group Project
**Inverse-volatility ("risk-balanced") portfolio: investor prospectus, backtest notebook and app**

- **Moodle group:** Project Group C
- **Members:** _[Full name, student number]_
- **Course:** 2270 Financial Modeling, MSc Finance, Nova SBE (Fall 2026)

| Deliverable | Location |
|---|---|
| Investor prospectus (PDF: cover + 6 content pages) | `prospectus/FM2270_Prospectus.pdf` |
| Backtest notebook (reproduces every number, table and figure) | `notebook/FM2270_backtest.ipynb` |
| Streamlit app (optional, +2) | `app/app.py`, deployed at: _[STREAMLIT APP URL]_ |
| Source code | https://github.com/joaojleitao/FM2270_Group_Project |
| AI-use disclosure | `AI_USE_LOG.md`, `journal/JOURNAL.md` |

## Run the notebook in Google Colab
1. Open https://colab.research.google.com, then File → Open notebook → GitHub, and paste the repo URL. Or upload `notebook/FM2270_backtest.ipynb`.
2. Runtime → **Restart session and run all**. The notebook installs what it needs (first code cell), downloads all data through APIs (Yahoo Finance via `yfinance`, risk-free rate from FRED), and uses hard-coded start and end dates. No local data files are needed.
3. Check that it runs top to bottom in a **fresh** session before submitting.

## Results in one line
Jan 2006 – Oct 2026, net of 10 bps costs: inverse-vol 6.57% p.a., volatility 6.86%, Sharpe 0.71, max drawdown 16.1%,
vs. 60/40 SPY/IEF 7.83%, 9.23%, 0.66, 29.5% (beta 0.48, not annualized; alpha 1.92% p.a., t = 1.66; IR −0.18).

## Run the app locally
```bash
pip install -r requirements.txt
streamlit run app/app.py
```
Python 3.11+ is required (pandas 3). The app imports its calculations from `app/strategy.py`. The notebook defines the same functions inline (so it runs on its own in Colab), and `tests/test_consistency.py` checks that the two match:
```bash
pytest -q
```

## Deploy the app (Streamlit Community Cloud)
1. Sign in at https://share.streamlit.io with GitHub.
2. *Create app* → *Deploy a public app from GitHub* → repository `joaojleitao/FM2270_Group_Project`, branch `main`, main file `app/app.py`.
3. *Advanced settings* → Python 3.12. Deploy. Then paste the app URL into `tools/build_notebook.py` and `tools/build_prospectus.py`
   (`APP_URL`) and rebuild (see below).

## Rebuild everything (local, fm2270 env)
```bash
python tools/build_notebook.py                     # notebook from app/strategy.py (identical functions)
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=fm2270 notebook/FM2270_backtest.ipynb
python tools/build_prospectus.py                   # prospectus PDF from notebook/outputs/ (needs Google Chrome)
pytest -q
```

## Repository layout
```
notebook/     backtest notebook (Colab-ready)
app/          Streamlit app + strategy.py (shared calculation functions)
tests/        consistency test between notebook and app/strategy.py
prospectus/   prospectus PDF, its HTML source and the app screenshot
journal/      project journal (JOURNAL.md + PDF export)
tools/        build scripts: notebook, prospectus, journal → PDF
class_materials_index.md   course conventions the project follows
strategy_proposal.md       AI-suggested strategy draft, for group approval
AI_USE_LOG.md              generative-AI use log
```

## Disclaimer
Academic project. Backtested results are hypothetical and do not guarantee future performance.
