# FM2270 Group Project: Project Journal

Course: 2270 Financial Modeling, MSc Finance, Nova SBE (Fall 2026). Times are Europe/Lisbon (WET, UTC+0 in November).
One entry per work session. Secrets are never recorded here.

---

## AI Disclosure Summary (running; feeds the prospectus disclosure section)

| Tool | Version / model | Purpose on this project | How outputs were checked | Status |
|---|---|---|---|---|
| Claude Code (Anthropic) | CLI 2.1.332, model Claude Opus 5.5 (`claude-opus-5-5`) | Environment setup; repo scaffold; class-materials index; strategy proposal draft; **Session 2: backtest code, notebook, Streamlit app, tests, prospectus text and PDF** | Every step run and checked in the terminal (versions, `pytest`, `nbformat` validation, Streamlit AppTest, `pip-audit`, live data-API tests); conventions cited to class files for group review; proposal marked AI-suggested pending group approval | In use |
| OpenAI Codex CLI (logged in with ChatGPT) | CLI 0.172.0 (`codex exec`, read-only sandbox; model reported as `gpt-6-luna`) | Adversarial review of the backtest code (look-ahead, survivorship, alignment, metric formulas, costs, pandas compatibility) | Each finding checked against the code by Claude; 5 accepted and fixed, 3 rejected with reasons (Session 2) | Used 2026-11-27 |
| free-llm-router (own code) | Gemini / OpenRouter / Groq free tiers | Planned: third check of metric formulas; proofreading | Not used (no API keys); replaced by a hand-computed formula unit test | Built, no keys |
| _Pre-project AI chats_ | _[to be filled by the group]_ | _[e.g. brainstorming strategy options]_ | _[ ]_ | _[ ]_ |

Third-party plugins Ponytail, claude-mem and Agent Reach were **not installed**: the SkillSpector scans flagged HIGH/CRITICAL findings (see the 2026-11-27 entry). Pending the group's decision.

---

## Pre-project history (before this setup)

> **To be completed by the group (accurately).** Describe the AI chats used BEFORE this setup session:
> which tool(s) (e.g. ChatGPT, Claude.ai, Gemini, ai.novasbe.pt), roughly when, what was asked (e.g. "suggest strategy options for the assignment"), what came back (e.g. the list of strategy options, inverse-vol vs. others), and how the group chose inverse volatility.
> The setup prompt (`SETUP_PROMPT.md`) itself already records that the strategy (inverse volatility) was **chosen by the group**, and that the asset/benchmark/metric recommendations in its Section 9 came from earlier AI-assisted work.

- Date(s): _[ ]_
- Tool(s) / model(s): _[ ]_
- What was asked / produced: _[ ]_
- How it was checked / what the group decided: _[ ]_

---

## Session 1: 2026-11-27, ~15:07–16:20: environment and project setup

**Goal:** set up the laptop, the Claude Code environment and the project folder, following `SETUP_PROMPT.md` section by section. No backtest code (the strategy details still need group approval).
**Who:** run by João with Claude Code. He asked Claude to carry out the whole prompt without stopping, and to leave interactive steps (logins, key creation, slash commands) for him to do afterwards.

### Steps taken (in order)

**Section 0: Folders**
- Read `SETUP_PROMPT.md`. Listed `D:\Financial Modelling` (read access OK) and found 19 class files (see `class_materials_index.md`). Nothing outside the project folder was modified.

**Section 1: Core tools**
1. `git --version` → 2.55.0.windows.5 (already installed). The global `user.name` (joaojleitao) and `user.email` were already set. Set `git config --global init.defaultBranch main` and `core.autocrlf true`.
2. `node -v` → v24.19.0 (already ≥ 18.18; nothing installed). npm 11.17.0.
3. `gh --version` → 2.100.0, already installed. `gh auth status` → already logged in to github.com as `joaojleitao` (HTTPS, keyring).
4. Python: Anaconda found at `C:\ProgramData\Anaconda3`, but its conda (4.8.3, Python 3.8 base) **crashes** on start (`AttributeError: module 'lib' has no attribute 'X509_V_FLAG_NOTIFY_POLICY'`, an old pyOpenSSL/cryptography mismatch), so `conda create` was impossible.
   **Fix (one attempt, worked):** created the `fm2270` environment as a **venv** from the standalone Python 3.12.10 (`C:\Users\João\AppData\Local\Programs\Python\Python312`), at **`D:\envs\fm2270`** (an ASCII path, to avoid the "ã" in the user folder causing tool problems).
   - `python -m venv D:\envs\fm2270`; upgraded pip; installed pandas numpy scipy statsmodels matplotlib plotly yfinance pandas-datareader streamlit jupyter ipykernel python-dotenv nbformat nbconvert pytest requests openai markdown-pdf, plus `pip-audit` (security check) and later `pypdf` (to read the class PDFs).
   - Versions: pandas 3.1.1, numpy 2.5.5, scipy 1.18.1, statsmodels 0.15.0, matplotlib 3.11.2, plotly 7.2.0, yfinance 1.8.0, pandas-datareader 0.11.1, streamlit 1.67.0, jupyter 1.1.1, ipykernel 7.4.0, python-dotenv 1.2.4, nbformat 5.11.1, nbconvert 7.17.2, pytest 9.2.0, requests 2.34.2, openai 3.60.0, markdown_pdf 1.14.
   - `pip-audit` → **no known vulnerabilities**.
   - `python -m ipykernel install --user --name fm2270 --display-name "Python (fm2270)"` → kernel at `C:\Users\João\AppData\Roaming\jupyter\kernels\fm2270`.
   - Smoke test: yfinance downloaded SPY/IEF/GLD for Jan 2005; pandas-datareader read Fama-French factors (latest 2026-09).
5. pipx: `python -m pip install --user pipx` → pipx 1.19.1; `pipx ensurepath` (PATH updated for new terminals).
6. Cursor extensions via `cursor --install-extension`: anthropic.claude-code 2.1.332, ms-python.python, ms-toolsai.jupyter, eamodio.gitlens 19.7.0 (all now listed by `cursor --list-extensions`).

**Section 2: Codex**
1. `npm install -g @openai/codex` → codex-cli 0.172.0. `codex login status` → **Not logged in** (João must run `codex login`).
2. `claude plugin --help` showed non-interactive commands exist, so: `claude plugin marketplace add openai/codex-plugin-cc` and `claude plugin install codex@openai-codex --scope user` → codex 1.0.6, user scope, enabled. Official OpenAI plugin, so no SkillSpector scan was required.
3. `claude plugin details codex@openai-codex` lists the `review` and `adversarial-review` skills/commands (plus setup, rescue, status, result, cancel, transfer). They become usable after a Claude Code restart plus `/codex:setup`.

**Section 3: Security scanner**
1. Checked PyPI metadata (`skillspector` 2.13.7, homepage github.com/NVIDIA/skillspector, an NVIDIA org repo). `pipx install skillspector` → `C:\Users\João\.local\bin\skillspector.exe`. `skillspector --help` works.
   Windows quirks: `--output` is unsupported on Windows (so stdout was redirected instead), and output needs `PYTHONIOENCODING=utf-8`.
2. Wrote the scan-first rule into the global `~/.claude/CLAUDE.md` (Section 7).

**Section 4: Third-party skills and plugins (scan first)**
- Cloned `DietrichGebert/ponytail`, `thedotmack/claude-mem` and `Panniantong/Agent-Reach` (depth 1) into a temp folder **outside the project** (the Claude session scratchpad). Ran `skillspector scan <dir> --no-llm --format json` (static analysis only; no LLM key configured).
- **Verdicts (all flagged → none installed, per the ground rules):**

| Repo | CRITICAL | HIGH | Verdict | Assessment of the CRITICAL/HIGH findings |
|---|---|---|---|---|
| ponytail | 2 | 36 | DO_NOT_INSTALL (score 100) | CRITICAL TT3 = `benchmarks/agentic/judge.py` sending its own API key to api.anthropic.com (benchmark script, not the plugin). HIGHs are mostly test fixtures (`tests/*.js` containing "ignore previous instructions", "rm -rf" strings to test its own guards), env-var reads, and docs. Looks like false positives, but not verified line by line. |
| claude-mem (repo root → scanned the `openclaw` sub-skill) | 1 | 12 | DO_NOT_INSTALL (score 100) | `curl … | bash` installer one-liner (supply-chain pattern) in the OpenClaw skill. |
| claude-mem `plugin/` (the actual Claude Code plugin) | 1 | 16 | flagged | CRITICAL TT3 = `urlopen` to its own **localhost** worker (127.0.0.1); HIGH PE3 = bundled scripts reading their own `.env` settings file; E2/AST1 in tests. Plausibly benign, but it runs a background worker plus hooks on every tool call. |
| Agent-Reach | 2 | 25 | DO_NOT_INSTALL (score 100) | CRITICAL TT3 = loopback Chrome DevTools call; HIGH = env-var reads, SSRF blocklists (flagged because they mention metadata hosts), a curl script for a Chinese podcast site. |

- Strix (optional, needs Docker Desktop): **skipped**. The prompt says to ask first, and Docker is not installed.
- **Decision needed from João:** install any of these despite the flags (e.g. after reading the JSON reports), or skip them. The reports are in the session scratchpad (temporary).

**Section 5: Free-LLM router**
- Key check (presence only, no values): GEMINI_API_KEY, OPENROUTER_API_KEY, GROQ_API_KEY, CEREBRAS_API_KEY, MISTRAL_API_KEY → **all not set**.
- Queried OpenRouter's public `/models` endpoint: 477 models, 11 free (`openrouter/free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `google/gemma-4-31b-it:free`, `nvidia/nemotron-3.5-lightning:free`, …). These seed the profiles. Gemini/Groq/Cerebras/Mistral names are placeholders/aliases until `--refresh-models` runs with keys.
- Created `~/.claude/tools/free_llm/`: `config.json` (providers, order, profiles, available models), `free_llm.py` (requests-based CLI: `--profile`, `--file`, `--list`, `--refresh-models`, `--simulate-fail`; reads keys from env or `HKCU\Environment`; fallback on 401/403/429 → next provider, 404/5xx/timeout → next model; logs metadata only to `usage.log`), and `README.md`.
- Created the user skill `~/.claude/skills/free-llm-router/SKILL.md` (when and when not to use it; always log usage). Claude Code detected it immediately.
- **Tests:**
  - `--list` OK.
  - No-key run exits with code 2 and a clear message.
  - Offline fallback test with fake keys and a fake HTTP layer: gemini 429 → openrouter 503 (one call, with the `models` fallback array) → groq answered. The all-providers-fail case stops without retrying. `usage.log` lines contain no prompt text.
  - `--refresh-models` live: OpenRouter refreshed (11 free models); the others were skipped (no key).
  - **Live per-provider tests are pending the keys.**

**Section 6: Project scaffold**
1. `git init`. Created:
   - `.gitignore`
   - `.env.example` (names only)
   - `requirements.txt` (app deps pinned to installed versions)
   - `README.md`
   - folders `notebook/ app/ prospectus/ tests/ journal/ tools/`
   - `AI_USE_LOG.md`
2. **Class materials index:** extracted the text of all PDFs (pypdf) and notebooks (JSON) into the scratchpad, then read the formula sheet, the syllabus, the quiz PDFs, Lecture 3 (APIs, portfolio strategies) and Lecture 4 (backtesting) in full, and the headers of the other files. Wrote `class_materials_index.md` with the conventions and citations.
   Key findings:
   - log returns
   - arithmetic annualization ×12/√12 (×252/√252 daily)
   - Sharpe on excess returns
   - β = cov/var of excess returns, α ×12, β not annualized
   - IR = E(R−R_b)/σ(R−R_b)
   - DD = (HWM−P)/HWM
   - costs = c·|Δposition|, with turnover and net results required
   - `shift(1)` timing
   - FRED as the rates source (keyless CSV)

   Also flagged: the class's weighted sum of log returns is an approximation; the instructor's FRED key in Lecture 3 must not be reused.
3. **Notebook skeleton** `notebook/FM2270_backtest.ipynb`: 13 sections in the required order, parameters set explicitly (proposed values), and empty TODO cells. Generated with `nbformat` from a scratch script that copies the function stubs **verbatim** from `app/strategy.py`. Validated with `nbformat.validate`, and executed end to end with `jupyter nbconvert --execute` on the fm2270 kernel (no errors).
4. `app/strategy.py`: 4 function **stubs** with docstrings (`inverse_vol_weights`, `backtest`, `max_drawdown`, `performance_table`; they raise `NotImplementedError` until the group approves the proposal). `app/app.py`: Streamlit placeholder with the four controls. Checked with `streamlit.testing.v1.AppTest` (renders, no exceptions).
   `tests/test_consistency.py`: (a) same function names, (b) identical code via AST comparison, (c) identical numbers on synthetic data (skipped while stubs). `pytest -q` → **5 passed, 1 skipped**.
5. Project `CLAUDE.md` with the permanent rules from the setup prompt.
6. Secret scan (grep for key patterns) → only false positives such as "risk-". **First commit `52014a1`.** GitHub repo not created yet (needs João's approval; see open items).

**Section 7: Global configuration**
- Created `C:\Users\João\.claude\CLAUDE.md` (no project-specific content): scan third-party skills first, no secrets in tracked files, commit often, keep a JOURNAL.md, `/codex:adversarial-review` for important logic, free-llm-router for second opinions, Ponytail for code only.

**Section 8: Journal**
- This file. `tools/build_journal_pdf.py` (markdown-pdf, A4, Helvetica 10pt, bordered tables, "Page x of n" stamped with PyMuPDF). The PDF is regenerated at the end of each session.

**Section 9: Strategy proposal**
- Wrote `strategy_proposal.md`, marked **AI-SUGGESTED / pending group approval**, with an approval checklist.
  Verified while writing:
  - The first full 252-day window falls at month-end 31 Jan 2006 (30 Dec 2005 has only 251 returns), so weights start on 1 Feb 2006. A first draft said a 2004-12-01 start would give Jan 2006; the data check showed Nov 2005, so the draft was corrected.
  - FRED TB3MS and DTB3 are both available keyless, through 2026-10 and 2026-11-24 respectively.
  - The Stooq fallback **fails** (JS challenge; dropped from pandas-datareader 0.11), so Tiingo is documented as the fallback (untested, needs a free key).

**Review pass (checking everything above for inaccuracies, as João asked)**
- **Cost definition ambiguity (fixed):** "10 bps per unit of one-way turnover" is ambiguous, because one-way turnover is often ½Σ|Δw|, which would halve the charge. Changed `strategy_proposal.md` §6–7, the notebook (parameters comment, §7 text), the app slider label and `class_materials_index.md` §4 so they all state cost = c × Σ|Δw| (the course model: every buy and sell pays).
- **Unverified claim removed:** the notebook's risks section said bonds/gold "dominate capital" before any backtest exists. Replaced it with "quantify the typical weights once the backtest runs".
- **Risk-free details added:** TB3MS is on a discount basis (a negligible difference, but say so); timing of rf vs returns.
- **App start date:** the minimum/default moved from 2006-01-01 to 2006-02-01, matching the first-weights date checked against the trading calendar.
- **Consistency test validated:** a scratch copy with one stub changed made 5 tests fail, so the test really catches drift between the notebook and `app/strategy.py`.
- Re-ran `pytest` (5 passed / 1 skipped) and regenerated the notebook from the same builder, so the stubs stay identical.
- Checked claude-mem's docs for how to pause it, in case it is installed later: `npx claude-mem stop` stops the worker and viewer (localhost:37777), `claude plugin disable claude-mem` disables it, and `claude plugin uninstall claude-mem` / `npx claude-mem uninstall` removes it.

**Section 10: Accounts**: see the final report / open items.

**GitHub repo (João approved creating it, 2026-11-27)**
- `gh repo create FM2270_Group_Project --private --source=. --remote=origin --push` created **https://github.com/joaojleitao/FM2270_Group_Project** (PRIVATE, default branch `main`). Commits `52014a1` and `392e00b` were pushed; `git ls-remote` confirms the remote `main` = 392e00b.
- Repo URL inserted into `README.md` and notebook §13 (Links).
- ⚠ The repo must be made **PUBLIC or shared with the graders** before submission. Group members still need to be added as collaborators (usernames pending).

### Files created / modified
| Path | Change | Commit |
|---|---|---|
| `.gitignore`, `.env.example`, `requirements.txt`, `README.md`, `AI_USE_LOG.md`, `CLAUDE.md` | created (scaffold, rules, disclosure log) | 52014a1 |
| `class_materials_index.md` | created: file index + course conventions with citations | 52014a1 |
| `notebook/FM2270_backtest.ipynb` | created: 13-section skeleton, parameters, function stubs | 52014a1 |
| `app/strategy.py`, `app/app.py` | created: function stubs; Streamlit placeholder | 52014a1 |
| `tests/test_consistency.py` | created: notebook ↔ strategy.py consistency test | 52014a1 |
| `strategy_proposal.md` | created: AI-suggested strategy draft for approval | 52014a1; review fixes (cost definition, rf notes) in the session-end commit |
| `notebook/FM2270_backtest.ipynb`, `app/app.py`, `class_materials_index.md`, `tools/build_journal_pdf.py` | review fixes (cost wording, risk text, app start date, `pymupdf` import) | session-end commit |
| `tools/build_journal_pdf.py` | created: journal → PDF | 52014a1 |
| `SETUP_PROMPT.md` | added to the repo as given (setup instructions) | 52014a1 |
| `journal/JOURNAL.md`, `journal/FM2270_Project_Journal.pdf` | created: this journal and its PDF | see `git log` (session-end commit) |
| Outside the repo (user scope): `~/.claude/CLAUDE.md`, `~/.claude/tools/free_llm/{config.json,free_llm.py,README.md}`, `~/.claude/skills/free-llm-router/SKILL.md` | created | not in Git |
| Outside the repo: `D:\envs\fm2270` (venv), Jupyter kernel `fm2270`, pipx + skillspector, Codex CLI, Codex plugin, Cursor extensions | installed | not in Git |

### Incorporated
- **Libraries:** see the versions above.
- **Data sources (tested):** Yahoo Finance via yfinance (adjusted prices), FRED keyless CSV (TB3MS/DTB3), Fama-French via pandas-datareader (works, not chosen).
- **Class materials used:** `D:\Financial Modelling\2270_Formulae.pdf`, `Syllabus.pdf`, `Lecture1_Intro.pdf`, `Lecture3_apis_pandas.ipynb`, `Lecture3_portfolio_strategies.ipynb`, `Lecture4_backtesting.ipynb`, `Lecture5_monte_carlo.ipynb`, `Lecture5_private_loan.ipynb`, `lecture_2.pdf`–`lecture_5.pdf` (headers of the rest).

### Models, plugins and skills used
- **Claude Code / Claude Opus 5.5:** carried out all steps above. It wrote every file in this commit, and the conventions index and proposal text.
- Codex: installed, not used (no login). Free-LLM router: built, offline-tested only (no keys). SkillSpector: used for the 3 scans above. Ponytail / claude-mem / Agent Reach: not installed.

### Decisions made, and who made them
- **Inverse-volatility strategy:** group (pre-existing decision, `SETUP_PROMPT.md`).
- **venv instead of conda env:** Claude, forced by the broken conda. Same name, Python 3.12.
- **FRED TB3MS as the proposed risk-free rate:** AI-suggested, because the course uses FRED (keyless CSV) and French data is not in class. Pending group approval.
- **Proposed parameters (assets, dates, 252d vol, benchmarks, 10 bps):** AI-suggested from the setup prompt, pending group approval.
- **Not installing the flagged plugins:** rule from the setup prompt; João to decide.

### Verification done
- Tool versions; `pip-audit` (clean); data API smoke tests; `pytest` (5 passed / 1 skipped); `nbformat.validate` + `nbconvert --execute`; Streamlit AppTest; router offline fallback test; secret grep before the commit; trading-calendar check of the first rebalance date.
- Codex adversarial review: **not run** (no backtest code yet; Codex not logged in).

### Problems found and fixes
- Broken conda 4.8.3 → venv at `D:\envs\fm2270`.
- SkillSpector `--output` unsupported on Windows → redirected stdout; cp1252 console crash → `PYTHONIOENCODING=utf-8`.
- claude-mem's repo-root scan covered only the `openclaw` sub-skill → re-scanned `plugin/` (took ~15 minutes: 31 MB of bundled JS).
- Stooq fallback dead → Tiingo documented.
- Wrong alternative-start date in the first proposal draft → corrected after the data check.

### Open items / next steps
1. ~~`codex login`~~ done 2026-11-27: Claude started `codex login` (browser OAuth flow); João completed the ChatGPT sign-in in the browser; `codex login status` → "Logged in using ChatGPT". Still to do: restart Claude Code, run `/codex:setup`, and check `/codex:review` and `/codex:adversarial-review`.
2. **João:** create the free keys (AI Studio, OpenRouter, Groq) and `setx` them in a separate terminal; then run `free_llm.py --refresh-models` and a live test of each provider.
3. **João/group:** decide on Ponytail / claude-mem / Agent Reach (all flagged by SkillSpector) and on Strix (needs Docker).
4. **Group:** approve or amend `strategy_proposal.md`; fill in the pre-project history above; fill in the group name and members in README and notebook.
5. ~~Create a private GitHub repo~~ (done: https://github.com/joaojleitao/FM2270_Group_Project). Still to do: add the members as collaborators (usernames needed), and make the repo **public or shared with the graders** before submission.
6. Accounts: Streamlit Community Cloud (sign in with GitHub), Google account for Colab.

---

## Session 2: 2026-11-27, ~16:20–17:30: complete the assignment

**Goal:** João asked Claude to check the project against the assignment brief (`D:\Users\João\Downloads\2270_FM_group_assignment_v2.pdf`), to assume he is the only group member, and to produce all the submission documents (prospectus, notebook, app, journal).
**Who:** Claude Code (Claude Opus 5.5), with OpenAI Codex as reviewer. João did not answer the follow-up questions (cover details, making the repo public, end date), so Claude used safe defaults: placeholders for the Moodle group name and member details, repo kept **private**, end date **2026-10-31**.

### Check against the assignment brief
| Requirement (brief) | Where it is met |
|---|---|
| Target client, objectives, horizon, risk attitude | Prospectus §2 |
| Underlying assets and why they suit the client | Prospectus §3 |
| Allocation rule, weights, rebalancing, motivation | Prospectus §4, Figure 2 |
| Backtest via API; source, sample, frequency, adjustments; no look-ahead | Notebook §4–7 (yfinance + FRED); prospectus §5; look-ahead assertion in notebook §6; unit test |
| Cumulative performance vs at least one benchmark, both start at 1 | Figure 1 (60/40, equal weight, SPY; all start at 1 on 30 Dec 2005) |
| Mean, volatility, Sharpe, alpha, IR, beta (not annualized); assumptions stated | Table 1 + caption; notebook §9 |
| Interpret every measure for the client | Prospectus §7 |
| Implementation, rebalancing, transaction costs; risks (concentration, look-ahead, survivorship) | Prospectus §8–9; Tables 2–3; breakeven cost |
| PDF up to 7 content pages + cover; group name and members | 6 content pages + cover; **group name and members are placeholders for João to fill in** |
| Notebook reproduces every number, runs in a fresh Colab, explicit dates, setup instructions, API data, no data files | Notebook header + Parameters cell; the prospectus numbers are read from the notebook's `outputs/` files by `tools/build_prospectus.py` |
| Optional app: change a meaningful assumption, same calculations, deployed on Streamlit, GitHub URL in prospectus and notebook | App done (lookback, rebalancing, cost, start year); identical functions (test); **Streamlit deployment and repo access for graders are João's steps** |
| Disclose all AI use, tools, purpose, checks | Prospectus §11, notebook header, `AI_USE_LOG.md` |
| Groups of 5–6 students | ⚠ João is working alone: he should confirm with the instructors that this is allowed |
| "Ask the instructors before using AI for strategy idea generation or complete solutions" | ⚠ The strategy (inverse volatility) was the group's, but the parameters were AI-drafted and AI produced the complete solution at João's request. **João should check with the instructors**, and he must understand every line before submitting |

### Steps taken
1. Read the brief, `strategy_proposal.md`, `class_materials_index.md`, the stubs and the test.
2. **Implemented `app/strategy.py`:** `download_prices`, `download_rf`, `rebalance_dates`, `inverse_vol_weights`, `fixed_weights`, `backtest` (holdings drift between rebalances; cost = c·Σ|target − drifted|, booked in the month whose return pays it; start in cash, so the first purchase pays costs), `max_drawdown`, `performance_table` (monthly log returns; beta = cov/var of excess returns vs 60/40; alpha ×12 with a conventional OLS t-stat; IR and TE vs 60/40; MDD).
3. **Independent check:** a plain day-by-day dollar-holdings loop reproduced the gross monthly returns to 1e-15 on real data. Net returns differ only in which month each rebalance cost is booked (loop: the trade month; ours: the next month), a documented timing convention.
4. **Notebook** generated by the new `tools/build_notebook.py` (functions copied verbatim from `app/strategy.py`): setup instructions, parameters, functions, download + four checks, adjustments, weights (+ look-ahead assertion), backtests, Figure 1, Table 1, gross vs net, drawdowns, robustness (lookback 3/6/12m, quarterly, 1-day lag, costs 0/10/25/50 bps, breakeven by bisection, sub-periods), export of the numbers, limitations. Executed end to end with nbconvert (fm2270 kernel): no errors.
5. **Tests** (`tests/test_consistency.py`, now 12): notebook functions = module functions (AST) with identical results; backtest vs an independent loop; no-look-ahead truncation test; hand-computed Sharpe, beta, alpha, IR and MDD. All pass.
6. **Codex adversarial review** (`codex exec -s read-only`; the first run could not read files in the Windows sandbox, so the code was pasted into the prompt). 7 findings. Accepted and fixed: the breakeven bisection needed a bracket check and a monotonicity check; sub-periods are segments of the continuous backtest (relabelled); the look-ahead check used a fixed index (now the middle date); the survivorship wording was too strong (reworded); the alpha t-stat is now labelled "conventional OLS". Rejected: the first-month cost and the one-day-lag timing are intended, documented conventions; the 'M'/'Q' period aliases work without warnings on pandas 2.2 and 3.1.
7. **Streamlit app** (`app/app.py`): lookback 1–24 months, monthly/quarterly, cost 0–100 bps, start year 2006–2024; cumulative chart, weights, full performance table; same functions as the notebook. AppTest: no exceptions; the default settings reproduce Table 1 exactly. Screenshot taken through Chrome DevTools (`prospectus/app_screenshot.png`).
8. **Prospectus** built by `tools/build_prospectus.py`: HTML with every number read from `notebook/outputs/`, printed to PDF with headless Chrome: **cover + 6 content pages** (limit 7).
9. `requirements.txt` trimmed to what the app uses (streamlit, pandas, numpy, yfinance, matplotlib); README updated (results, deploy and rebuild instructions); AI-use log and this journal updated.

### Key results (Jan 2006 – Oct 2026, 250 months, net of 10 bps)
| | Inverse-vol | 60/40 | Equal weight | SPY |
|---|---|---|---|---|
| Mean (ann., log) | 6.57% | 7.83% | 8.15% | 10.47% |
| Volatility (ann.) | 6.86% | 9.23% | 8.71% | 15.10% |
| Sharpe | 0.71 | 0.66 | 0.74 | 0.58 |
| Beta vs 60/40 (not ann.) | 0.48 | 1.00 | 0.68 | 1.57 |
| Alpha (ann.) / t | 1.92% / 1.66 | – | 2.26% / 1.70 | −0.83% / −0.86 |
| IR vs 60/40 | −0.18 | – | 0.05 | 0.39 |
| Max drawdown | 16.1% | 29.5% | 17.7% | 50.8% |

Interpretation (in the prospectus): a lower-risk alternative to 60/40, not a higher-return one; most of the Sharpe gain comes from adding gold (equal weight has a higher Sharpe); the alpha is not significant; costs are negligible (breakeven ≈ 199 bps per unit traded).

### Files changed
| Path | Change |
|---|---|
| `app/strategy.py` | stubs → full implementation |
| `app/app.py` | placeholder → working app |
| `tests/test_consistency.py` | stub skip removed; 3 new tests (loop, look-ahead, formulas) |
| `tools/build_notebook.py`, `tools/build_prospectus.py` | new build scripts |
| `notebook/FM2270_backtest.ipynb`, `notebook/outputs/*` | executed notebook and its figures/tables |
| `prospectus/FM2270_Prospectus.pdf` (+ `.html`, `app_screenshot.png`) | the prospectus |
| `requirements.txt`, `README.md`, `strategy_proposal.md` (implementation note), `AI_USE_LOG.md`, `journal/*` | updated |

### Decisions (who)
- Proposal implemented as written (Claude, at João's request; João has **not yet ticked** the approval checklist).
- Data from 2004-12-01, so the evaluation starts in January 2006 (Claude; both start options were in the proposal).
- Metrics on monthly log returns, portfolios from simple returns (Claude, following the course and proposal §6).
- Primary benchmark 60/40 (proposal).

### Verification
- `pytest -q`: 12 passed.
- Notebook executed end to end with nbconvert on the fm2270 kernel (pandas 3.1.1): no errors.
- **Colab simulation:** a throw-away venv with pandas 2.2.2 + numpy 2.0.2 (older versions, as Colab may have) ran the whole notebook with no errors; Table 1 identical except the mean returns in the 8th decimal (Yahoo adjusted prices shift very slightly between downloads). A real fresh-Colab run is still João's step.
- Streamlit AppTest (default, quarterly/50 bps/2015, 24-month lookback from 2006 → clear warning); default output = Table 1.
- Prospectus PDF: 7 pages (cover + 6), every page inspected as an image; 724 KB. Notebook 372 KB.
- Secret scan of tracked files: clean.

### Open items for João (before submitting)
1. Fill in `GROUP_NAME` / `MEMBERS` in `tools/build_prospectus.py` and `tools/build_notebook.py`, then rebuild (README, "Rebuild everything").
2. Make the repo accessible to the graders (public, or add them), deploy on share.streamlit.io (README, "Deploy the app"), paste the URL into `APP_URL` in both build scripts, rebuild, commit, push.
3. Run the notebook once in a **fresh Google Colab** session (Runtime → Run all).
4. Read and understand all the code and the prospectus; tick the approval boxes in `strategy_proposal.md`.
5. Ask the instructors about (a) working alone and (b) the extent of AI use (the brief asks students to consult them before using AI for complete solutions). Fill in the pre-project AI history above.
6. Submit on Moodle: `prospectus/FM2270_Prospectus.pdf` and `notebook/FM2270_backtest.ipynb` (both well under 50 MB).
