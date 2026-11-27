# Generative-AI Use Log

Every use of a generative-AI tool on this project is recorded here, and also in `journal/JOURNAL.md`.
The group is responsible for understanding all code and justifying the strategy. AI output is a draft until a group member has checked it.

| Date | Tool / model | Purpose | Input given | How the output was checked | Accepted / modified / rejected |
|---|---|---|---|---|---|
| _(pre-project)_ | _[to be filled by the group: which AI chat(s) were used before setup, e.g. to brainstorm strategy options]_ | _[purpose]_ | _[input]_ | _[check]_ | _[outcome]_ |
| 2026-11-27 | Claude Code (Claude Opus 5.5, `claude-opus-5-5`) | Set up the environment, the repository scaffold, the notebook skeleton, empty function stubs and the consistency test | `SETUP_PROMPT.md` (the group's setup instructions) | Each step run and checked in the terminal (`pytest`, `nbformat` validation, `pip-audit`, Streamlit AppTest); see the journal entry for 2026-11-27 | Accepted (infrastructure only; no strategy results) |
| 2026-11-27 | Claude Code (Claude Opus 5.5) | Read the class files in `D:\Financial Modelling` and wrote `class_materials_index.md` (course conventions for metrics, data and backtesting) | Text extracted from the course PDFs and notebooks | Every convention is cited to its class file and section, so a member can check it against the source; **group to review** | Pending group review |
| 2026-11-27 | Claude Code (Claude Opus 5.5) | Drafted `strategy_proposal.md` (assets, sample, benchmarks, metrics, costs, robustness checks, client), following the setup prompt's recommendations and the course conventions | `SETUP_PROMPT.md` Section 9 + `class_materials_index.md` | Cross-checked against the class formula sheet and Lectures 3–4; **group must discuss and approve**; Codex review and free-LLM cross-check still pending (no logins/keys yet) | Pending group approval |
