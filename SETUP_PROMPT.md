# Claude Code — Full Setup Prompt (FM 2270 Group Project)

Paste everything below the line into Claude Code, or save this file in the project folder and tell Claude Code: "Read SETUP_PROMPT.md and carry it out section by section."

---

You are setting up my Windows laptop, my Claude Code environment and a new project folder for a university group assignment, "2270 Financial Modeling" (MSc Finance, Nova SBE).

ASSIGNMENT SUMMARY
- Deliverables:
  1. An investor prospectus in PDF, max 7 content pages plus an optional cover. References and app evidence count toward the 7 pages.
  2. A Jupyter notebook (.ipynb) that reproduces EVERY number, table and figure in the prospectus. It must run top to bottom in a FRESH Google Colab session and get its data through an API. No separate data files. Start and end dates set explicitly in the code.
  3. Optional, worth +2 marks: a Streamlit app where the user changes a meaningful assumption and sees performance vs. the benchmark. It must be deployed on Streamlit Community Cloud with its source code on GitHub. Both URLs go in the prospectus and the notebook.
- Required content:
  - target client (objectives, horizon, risk attitude)
  - assets and why they fit the client
  - allocation rule and rebalancing
  - backtest using only information available at each date
  - cumulative performance vs. at least one benchmark, both starting at 1
  - performance measures: annualized average return, volatility, Sharpe ratio, alpha, information ratio, and beta (NOT annualized), with calculation assumptions stated
  - an interpretation of every measure for the client
  - implementation: rebalancing and transaction costs
  - risks and limitations: concentration, look-ahead bias, survivorship bias
- We must disclose ALL generative-AI use: the tools, their purpose, and how we checked the outputs. The group is responsible for understanding the code and justifying the strategy.

==================================================================
GROUND RULES (apply to every section)
==================================================================
- I'm on Windows. Use PowerShell or Git Bash, whichever fits each command. Always quote paths that contain spaces.
- Check whether a tool is already installed before installing it (`git --version`, `node -v`, `where codex`, `conda env list`, etc.).
- Work ONE section at a time. After each section, verify it worked and show me a short result. If something fails, try one sensible fix, then stop and tell me. Don't loop.
- You can't do interactive logins or slash commands yourself. When a step needs one (browser login, /plugin, /codex:setup, setx with a secret), print the EXACT command for me, wait for me to say "done", then verify it.
- SECRETS: never ask me to paste API keys or passwords into this chat. Never write a secret into any file that Git tracks, the notebook, the journal or a log. Keys go in Windows user environment variables or a `.env` file listed in `.gitignore`. When you check a key, confirm it exists without printing its value.
- SECURITY:
  - Before installing ANY third-party skill or plugin (everything except the official Anthropic and OpenAI ones), clone it to a temp folder outside the project and scan it with SkillSpector.
  - Show me the verdict. If it has HIGH/CRITICAL findings or anything malicious, don't install it and ask me.
  - Never install a Python or npm package version that is listed in a current security advisory.
- Ask me before: creating a GitHub repo, making a repo public, installing Docker, or anything that costs money.
- INSTALL SCOPE: install every skill and plugin at USER/GLOBAL scope (not project scope), so I can reuse them in future projects. The only exception is project-specific files, such as the project CLAUDE.md. Tell me the install path for each one.
- JOURNAL: from the very first command, keep the project journal described in Section 8, starting with this setup session.

==================================================================
SECTION 0 — Folders
==================================================================
- My class materials (slides, notebooks, readings taught in class) are in:
  `D:\Financial Modelling`
- The project folder is a subfolder of it:
  `D:\Financial Modelling\FM2270_Group_Project`
  I've created this folder, opened it in Cursor, and launched Claude Code with:
  `claude --add-dir "D:\Financial Modelling"`
  If you can't read the parent folder, tell me how to add it with /add-dir.
- Treat everything in `D:\Financial Modelling` OUTSIDE the project folder as READ-ONLY. Never modify, move or delete class files. Don't copy them into the Git repo; reference them by path only.

==================================================================
SECTION 1 — Core tools
==================================================================
1. Check that Git for Windows is installed. Set `git config --global` user.name and user.email (ask me for the values), `init.defaultBranch main`, and `core.autocrlf true`.
2. Install Node.js LTS (v18.18 or later) if it's missing (winget).
3. Install the GitHub CLI (`winget install GitHub.cli`). Then have me run `gh auth login` (GitHub.com, HTTPS, browser).
4. Python (I have Anaconda):
   - Create a conda env `fm2270` with Python 3.12.
   - Install: pandas numpy scipy statsmodels matplotlib plotly yfinance pandas-datareader streamlit jupyter ipykernel python-dotenv nbformat nbconvert pytest requests openai markdown-pdf
   - Register it as a Jupyter kernel named "fm2270".
5. Install pipx (`python -m pip install --user pipx`, then `pipx ensurepath`).
6. Cursor extensions (use `cursor --install-extension`; if `cursor` isn't on PATH, give me the list to install by hand): anthropic.claude-code, ms-python.python, ms-toolsai.jupyter, eamodio.gitlens.

==================================================================
SECTION 2 — Codex (second-model reviewer, using my ChatGPT account)
==================================================================
1. `npm install -g @openai/codex`, then have me run `codex login` (ChatGPT sign-in).
2. Install the official OpenAI Codex plugin for Claude Code at user scope.
   - First run `claude plugin --help` to see whether non-interactive plugin commands exist. If they do, use them.
   - If not, print these lines for me to type:
     ```
     /plugin marketplace add openai/codex-plugin-cc
     /plugin install codex@openai-codex
     /reload-plugins
     /codex:setup
     ```
3. Check that /codex:review and /codex:adversarial-review are available.

==================================================================
SECTION 3 — Security scanner (install BEFORE any third-party skill)
==================================================================
1. `pipx install skillspector` (NVIDIA SkillSpector). Check `skillspector --help`.
2. Write a short global note in `~/.claude/CLAUDE.md` (see Section 7) saying every new third-party skill or plugin must be scanned with SkillSpector first.

==================================================================
SECTION 4 — Skills and plugins (all at user scope; scan each one first)
==================================================================
a) Ponytail (keeps code minimal and readable)
   - Repo: https://github.com/DietrichGebert/ponytail
   - Install: `/plugin marketplace add DietrichGebert/ponytail`, then `/plugin install ponytail@ponytail`
   - NOTE: Ponytail applies to CODE only. It must never shorten the journal, the AI-use log or the prospectus text.
b) claude-mem (persistent memory across sessions)
   - Repo: https://github.com/thedotmack/claude-mem
   - Install ONLY with the slash commands (NOT `npm install -g`): `/plugin marketplace add thedotmack/claude-mem`, then `/plugin install claude-mem`
   - It runs a local worker and a web viewer at http://localhost:37777. Tell me how to pause or disable it.
c) Agent Reach (lets the agent read GitHub, YouTube, Reddit, etc.)
   - Repo: https://github.com/Panniantong/Agent-Reach
   - Install globally: `npx -y skills add panniantong/agent-reach --skill agent-reach -g -a claude-code`
   - Core only. Don't set up social-media logins, cookies or scrapers that need my accounts.
d) Strix (AI pentesting; only for scanning my own Streamlit app later). OPTIONAL. ASK ME FIRST.
   - It needs Docker Desktop and an LLM provider (it can use my Codex login).
   - Install: `pipx install strix-agent`. Don't run any scan now.
e) The free-LLM router skill: build it in Section 5 (it's our own code, not a third-party skill).

At the end, list every installed skill and plugin with its path, and show me how to check that Claude Code sees it (/skills, /plugin).

==================================================================
SECTION 5 — Free LLM API layer with automatic model switching
==================================================================
Goal: a free "helper model" pool with automatic fallback. Claude stays the main coding model; DON'T reroute Claude Code itself to free models. Use the pool for second opinions, formula checks, proofreading and summarizing class material.

Design (our own small code, no third-party proxy):
- Providers, in order of preference:
  1. Google AI Studio (Gemini) — free key; named in the assignment as an approved resource.
  2. OpenRouter — one free key. The model `openrouter/free` picks a free model automatically. Also support a `models` fallback array of specific `:free` models.
  3. Groq — free key, very fast, used as a backup.
  4. (Optional) Cerebras or Mistral free tiers, if I get keys.
- Task profiles (choose the best available model per task):
  - `reasoning` (formula and backtest logic checks) → the strongest free reasoning model available
  - `writing` (proofreading, clarity) → a strong general model
  - `fast` (short summaries, classification) → the fastest model
  At setup time, query each provider's model-list endpoint to get CURRENT free model names (they change often). Don't hard-code stale names; store them in a config file I can edit.
- Behavior:
  - Try the providers in order for the requested profile.
  - On 429 / quota / timeout / 5xx, switch automatically to the next one.
  - Log which provider and model answered (no prompt content, no keys) to `~/.claude/tools/free_llm/usage.log`, so it can go in the AI-use disclosure.
- Build it:
  1. Walk me through creating free keys at aistudio.google.com, openrouter.ai/settings/keys and console.groq.com. I save each one myself as a Windows user environment variable in a separate terminal (`setx GEMINI_API_KEY "..."`, `setx OPENROUTER_API_KEY "..."`, `setx GROQ_API_KEY "..."`). Then check each exists without printing it.
  2. Create `~/.claude/tools/free_llm/` with:
     - `config.json` (providers, profiles, model lists)
     - `free_llm.py`: a CLI that uses only `requests` or the `openai` SDK with custom base URLs, and handles retries and fallback. Usage: `python free_llm.py --profile reasoning "prompt"`, or `--file path`.
     - `README.md`
  3. Create a USER-scope skill at `~/.claude/skills/free-llm-router/SKILL.md` that tells Claude when to use the router (second opinions, proofreading, formula cross-checks) and when NOT to (never send secrets, personal data of group members, or whole private files without a reason). It also says to always record usage in the project journal and AI-use log.
  4. Test each provider with one tiny prompt, and test the fallback by simulating a failure. Show me the results.
- Notes:
  - Free tiers may use prompts for model training. Don't send personal data.
  - Free quotas reset daily. If all providers are rate-limited, stop and tell me; don't keep retrying.

==================================================================
SECTION 6 — Project scaffold in D:\Financial Modelling\FM2270_Group_Project
==================================================================
1. `git init`, then create:
   - `.gitignore`: Python, `.ipynb_checkpoints`, `.env`, `.venv`, `__pycache__`, `*.log`, `.streamlit/secrets.toml`, data caches, OS files.
   - `.env.example`: variable names only, no values.
   - `requirements.txt` for the APP (streamlit, pandas, numpy, yfinance, pandas-datareader, statsmodels, plotly), pinned to the installed versions.
   - `README.md`: title, group name and members placeholders, how to run the notebook in Colab, how to run the app locally, and the app's deployment URL placeholder.
   - Folders: `notebook/`, `app/`, `prospectus/`, `tests/`, `journal/`, `tools/`.
   - `AI_USE_LOG.md`: a table with columns Date | Tool / model | Purpose | Input given | How the output was checked | Accepted / modified / rejected.
2. CLASS MATERIALS INDEX:
   - Scan `D:\Financial Modelling` (excluding the project folder) and read the class files (PDF, PPTX, IPYNB, PY, XLSX, DOCX).
   - Create `class_materials_index.md` in the project with:
     - each file's path and topic
     - the course's exact definitions and conventions for: annualization (12 vs 252, arithmetic vs geometric), Sharpe ratio, alpha and beta (regression form, excess returns), information ratio and tracking error, risk-free source, drawdown, transaction costs, backtesting practice
     - the Python libraries and coding style used in class
   - The project MUST follow the course's conventions wherever they exist. Cite the class file each one comes from.
3. Notebook skeleton `notebook/FM2270_backtest.ipynb`: markdown headers plus empty code cells, in this order:
   1. Title, group name, members, AI-use statement
   2. Setup: a pip install cell for Colab, plus imports
   3. Parameters: START_DATE, END_DATE, TICKERS, LOOKBACK, REBALANCE_FREQ, COST_BPS, RISK-FREE SOURCE, all set explicitly
   4. Data download via API
   5. Data adjustments: adjusted prices (dividends and splits), calendar alignment, missing values
   6. Allocation rule: inverse volatility
   7. Rebalancing and transaction costs
   8. Portfolio and benchmark returns
   9. Cumulative performance chart (all series start at 1)
   10. Performance table
   11. Robustness checks
   12. Risks and limitations notes
   13. Links: GitHub repo and Streamlit app
4. `app/app.py` (Streamlit placeholder) and `app/strategy.py`, which holds the calculation functions.
   - The notebook defines the SAME functions inline, so it runs on its own in Colab.
   - `tests/test_consistency.py` checks that the notebook functions and `app/strategy.py` give identical results on the same inputs.
5. Project `CLAUDE.md` with these permanent rules:
   - STRATEGY (chosen by the group): inverse-volatility ("risk-balanced") portfolio.
     - At each month-end t, estimate each asset's volatility σ(i,t) from trailing returns up to and including month-end t.
     - Set weights w(i,t) = (1/σ(i,t)) / Σ_j (1/σ(j,t)).
     - Apply them ONLY to returns from the first trading day of month t+1. No look-ahead.
     - Say explicitly that inverse-vol is NOT full risk parity, because correlations are ignored.
   - Start and end dates are hard-coded. Results are reproducible.
   - Use adjusted prices (total return). Document the source, sample period, frequency and adjustments.
   - Beta is NOT annualized. State the annualization factor and the risk-free source.
   - Follow the conventions in `class_materials_index.md`.
   - The notebook runs in fresh Colab with no local files.
   - The notebook and app use identical calculations; `tests/test_consistency.py` must pass.
   - Keep code simple and commented. Every group member must be able to explain each line.
   - After every meaningful change: run the code, update the journal, then `git commit` with a clear message.
   - Before finalizing any backtest change, run /codex:adversarial-review focused on look-ahead bias, survivorship bias, return/weight alignment and metric formulas. Use the free-llm-router `reasoning` profile as a third check of the metric formulas.
   - Append every AI use to `AI_USE_LOG.md` and to the journal.
6. First commit. Then ASK ME before creating a PRIVATE GitHub repo with `gh repo create` and pushing. Remind me that the repo must be made PUBLIC (or shared with the graders) before submission, because the graders need access.

==================================================================
SECTION 7 — Global Claude Code configuration (for future projects too)
==================================================================
Create or extend `~/.claude/CLAUDE.md` with general rules:
- Scan third-party skills with SkillSpector before installing them.
- Never write secrets into tracked files.
- Commit often.
- Keep a JOURNAL.md in every project.
- Use /codex:adversarial-review for important logic.
- Use the free-llm-router skill for cheap second opinions.
- Ponytail applies to code only, never to documentation.
Don't put anything project-specific in the global file.

==================================================================
SECTION 8 — Project journal (detailed, kept the whole time, exported to PDF)
==================================================================
1. Create `journal/JOURNAL.md`. Add an entry for EVERY work session, starting with this setup session. Each entry includes:
   - Date and time (Europe/Lisbon), session goal
   - Steps taken, in order: commands run (no secrets), and what each one did
   - Files created / modified / deleted (paths), with a one-line description of each change and the git commit hash
   - What was incorporated: libraries, data sources, class materials used (with file paths)
   - Models, plugins and skills used: Claude model, Codex, free-LLM router (provider and model as logged), Ponytail, claude-mem, Agent Reach, etc. For each: what it was used for and what it produced
   - Decisions made and why: assets, dates, parameters, conventions; who decided (group vs. suggested by AI)
   - Verification done: tests run, cross-checks, Codex review findings and how each was resolved
   - Problems found and fixes
   - Open items / next steps
2. At the top of the journal, keep a running "AI Disclosure Summary": every tool, its purpose, and how outputs were checked. This feeds the prospectus disclosure section directly.
3. Create `tools/build_journal_pdf.py`, which converts `journal/JOURNAL.md` into `journal/FM2270_Project_Journal.pdf` (markdown-pdf package, A4, readable font, page numbers, tables rendered).
4. Regenerate the PDF at the end of EVERY session and commit both files.
5. Add a "Pre-project history" entry and ask me to describe the AI chats we used BEFORE this setup (e.g. where the strategy options came from). Record that information accurately.

==================================================================
SECTION 9 — Strategy design recommendations (draft for the GROUP to approve)
==================================================================
Don't write backtest code yet. Write `strategy_proposal.md` with the recommendations below, marked clearly as AI-suggested, for the group to discuss and approve. Log it in the journal and the AI-use log.
- Assets (core recommendation; long histories and clear roles):
  - SPY (US equities, growth)
  - IEF (7–10y US Treasuries, diversification)
  - GLD (gold, crisis/inflation diversifier)
- Sample:
  - Data from 2005-01-03 (GLD has traded since Nov 2004), so the first weights after a 12-month lookback apply from early 2006.
  - End at the last complete month before submission, hard-coded.
  - This covers 2008, 2020 and 2022, a key stress test where stocks and bonds fell together.
- Volatility estimate:
  - Daily returns over the trailing 252 trading days, annualized ×√252, measured at each month-end.
  - Monthly rebalancing.
- Benchmarks:
  - Primary: 60/40 SPY/IEF rebalanced monthly. Same building blocks, so it isolates the allocation rule.
  - Secondary: equal-weight SPY/IEF/GLD rebalanced monthly. Separates the effect of adding gold from the effect of the inverse-vol weighting.
  - Context: SPY alone.
- Risk-free rate: 1-month T-bill from the Kenneth French data library (pandas-datareader, no key needed), or FRED DTB3. Pick whichever matches the class materials.
- Metrics:
  - Monthly returns. Annualized mean (×12), volatility (×√12), Sharpe on excess returns.
  - Alpha and beta from an OLS of portfolio excess returns on primary-benchmark excess returns (alpha annualized ×12, beta not annualized).
  - Information ratio = annualized active return / annualized tracking error.
  - Also: max drawdown, average turnover, net-of-cost results.
  - Use the class conventions if they differ.
- Transaction costs: 10 bps per unit of one-way turnover in the base case. Show gross and net.
- Robustness checks: lookback 3 / 6 / 12 months, monthly vs. quarterly rebalancing, costs 0 / 10 / 25 bps.
- Target client (proposal): moderate-risk retail / wealth-management clients in Portugal with a 5+ year horizon, who want equity-like growth with smaller drawdowns.
- Implementation section:
  - EU retail investors generally can't buy US-domiciled ETFs, so mention UCITS equivalents (an S&P 500 UCITS ETF, a 7–10y US Treasury UCITS ETF, a physical gold ETC).
  - Mention the EUR/USD currency risk and that the backtest is in USD.
- App (+2 marks):
  - Sliders: lookback window, rebalancing frequency, transaction cost, start date.
  - Outputs: cumulative chart vs. benchmarks and the metrics table.
  - Uses `app/strategy.py`.
- Data robustness:
  - yfinance (`auto_adjust=True`) as primary, with a clear error message.
  - Document a fallback API in case yfinance is rate-limited in Colab.
- Check against the class materials: if the class used a specific data API or metric definition, prefer it, and say so.

==================================================================
SECTION 10 — Accounts checklist (I do these; you check what you can)
==================================================================
- GitHub (logged in via gh); add group members as collaborators (ask me for usernames)
- Streamlit Community Cloud (share.streamlit.io, sign in with GitHub)
- Google account for Colab
- ChatGPT (Codex login)
- Google AI Studio, OpenRouter and Groq free keys (saved as environment variables)

==================================================================
FINAL REPORT
==================================================================
1. One table: Item | Status (OK / Failed / Skipped) | Version or install path | Scope (global/project) | Action still needed from me.
2. Which items need a Claude Code restart.
3. Update `journal/JOURNAL.md` with this whole setup session, regenerate `FM2270_Project_Journal.pdf`, commit, and give me the PDF path.
4. Remind me to:
   - test the notebook in a fresh Colab session before submitting
   - make the GitHub repo accessible to the graders
   - get the strategy approved per Section 9
