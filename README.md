# FM 2270 Financial Modeling: Group Project
**Inverse-volatility ("risk-balanced") portfolio: investor prospectus, backtest notebook and app**

- **Group name:** _[GROUP NAME]_
- **Members:** _[Member 1]_, _[Member 2]_, _[Member 3]_, _[Member 4]_, _[Member 5]_, _[Member 6]_
- **Course:** 2270 Financial Modeling, MSc Finance, Nova SBE (Fall 2026)

| Deliverable | Location |
|---|---|
| Investor prospectus (PDF, max 7 content pages + cover) | `prospectus/` |
| Backtest notebook (reproduces every number, table and figure) | `notebook/FM2270_backtest.ipynb` |
| Streamlit app (optional, +2) | `app/app.py`, deployed at: _[STREAMLIT APP URL]_ |
| Source code | https://github.com/joaojleitao/FM2270_Group_Project |
| AI-use disclosure | `AI_USE_LOG.md`, `journal/JOURNAL.md` |

## Run the notebook in Google Colab
1. Open https://colab.research.google.com, then File → Open notebook → GitHub, and paste the repo URL. Or upload `notebook/FM2270_backtest.ipynb`.
2. Runtime → **Restart session and run all**. The notebook installs what it needs (first code cell), downloads all data through APIs (Yahoo Finance via `yfinance`, risk-free rate from FRED), and uses hard-coded start and end dates. No local data files are needed.
3. Check that it runs top to bottom in a **fresh** session before submitting.

## Run the app locally
```bash
pip install -r requirements.txt
streamlit run app/app.py
```
The app imports its calculations from `app/strategy.py`. The notebook defines the same functions inline (so it runs on its own in Colab), and `tests/test_consistency.py` checks that the two match:
```bash
pytest -q
```

## Repository layout
```
notebook/     backtest notebook (Colab-ready)
app/          Streamlit app + strategy.py (shared calculation functions)
tests/        consistency test between notebook and app/strategy.py
prospectus/   prospectus source and PDF
journal/      project journal (JOURNAL.md + PDF export)
tools/        helper scripts (journal → PDF)
class_materials_index.md   course conventions the project follows
strategy_proposal.md       AI-suggested strategy draft, for group approval
AI_USE_LOG.md              generative-AI use log
```

## Disclaimer
Academic project. Backtested results are hypothetical and do not guarantee future performance.
