# FM2270 Group Project: Project Journal

Course: 2270 Financial Modeling, MSc Finance, Nova SBE (Fall 2026). Times are Europe/Lisbon (WET, UTC+0 in November).
One entry per work session. Secrets are never recorded here.

---

## AI Disclosure Summary (running; feeds the prospectus disclosure section)

| Tool | Version / model | Purpose on this project | How outputs were checked | Status |
|---|---|---|---|---|
| Claude Code (Anthropic) | CLI 2.1.332, model Claude Opus 5.5 (`claude-opus-5-5`) | Environment setup; repo scaffold; notebook skeleton; function stubs; consistency test; class-materials index; strategy proposal draft | Every step run and checked in the terminal (versions, `pytest`, `nbformat` validation, Streamlit AppTest, `pip-audit`, live data-API tests); conventions cited to class files for group review; proposal marked AI-suggested pending group approval | In use |
| OpenAI Codex (plugin `codex@openai-codex` + Codex CLI) | plugin 1.0.6, CLI 0.172.0 | Planned: adversarial review of backtest logic (look-ahead, survivorship, alignment, metric formulas) | Not used yet (needs `codex login` + `/codex:setup`) | Installed, not configured |
| free-llm-router (own code) | Gemini / OpenRouter / Groq free tiers | Planned: third check of metric formulas; proofreading | Not used yet (no API keys yet); offline fallback test only | Built, no keys |
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
1. **João:** `codex login`, then restart Claude Code, then `/codex:setup`; check `/codex:review` and `/codex:adversarial-review`.
2. **João:** create the free keys (AI Studio, OpenRouter, Groq) and `setx` them in a separate terminal; then run `free_llm.py --refresh-models` and a live test of each provider.
3. **João/group:** decide on Ponytail / claude-mem / Agent Reach (all flagged by SkillSpector) and on Strix (needs Docker).
4. **Group:** approve or amend `strategy_proposal.md`; fill in the pre-project history above; fill in the group name and members in README and notebook.
5. ~~Create a private GitHub repo~~ (done: https://github.com/joaojleitao/FM2270_Group_Project). Still to do: add the members as collaborators (usernames needed), and make the repo **public or shared with the graders** before submission.
6. Accounts: Streamlit Community Cloud (sign in with GitHub), Google account for Colab.
