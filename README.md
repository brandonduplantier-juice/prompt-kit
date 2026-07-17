# prompt-kit

Reusable prompts, templates, and conventions. Built from what is already in the project
history rather than from generic best practice.

## What is here

```
check.py                      the only thing here that enforces anything
hooks/pre-commit              runs check.py --staged before every commit
00-core/
  operating-rules.md          the block that goes at the top of every prompt
prompts/
  prompt-builder.md           makes new prompts from a rough idea
  prompt-checker.md           audits, tests, fixes, and loops on an existing prompt
  llm-orchestration.md        systems where the model is a component, not the product
  sql-extract.md              pulling data out correctly, before any cleaning
  data-cleaning.md            messy file to a dataset you can defend
  data-analysis-project.md    dataset and question to a defensible finding
  dashboard-build.md          Power BI, Tableau, Looker Studio, Streamlit
  flask-service-build.md      new Flask app through to a Render deploy
  api-integration-debug.md    section A, new API. section B, production debug
  portfolio-writeup.md        card, README, resume bullet, LinkedIn, interview prep
brand/
  README.md                   the signature: what it is, where it must not go
  tokens.json                 single source of truth for every color and font
  tokens.css                  CSS variables for web and Flask
  powerbi-theme.json          Power BI import
  streamlit-config.toml       copy to .streamlit/config.toml
  tableau-Preferences.tps     merge into My Tableau Repository
  brandon.mplstyle            matplotlib figures
templates/
  flask-service/              working scaffold, tests pass out of the box
  analysis-project/           schema.py + 02_clean.py both run, METHODS, data dictionary
  llm-classifier/             working: facts schema, model call, pure scorer, 22 tests
docs/
  stack-conventions.md        the environment facts you keep re-typing
  sql-patterns.md             the silent SQL failures, with the checks that catch them
  llm-patterns.md             the model extracts facts, code decides. Plus what breaks
  git-workflow.md             PowerShell git, per situation
```

## Enforcement

Everything else in this repo is a document that depends on you remembering it.
`check.py` does not. Install the hook once, from the repo root:

```powershell
git config core.hooksPath hooks
python check.py
```

From then on, every commit is checked and blocked on failure. It catches: em-dashes and
en-dashes, UTF-8 BOMs, credentials matched by shape (AWS, GitHub, Anthropic, OpenAI,
Slack, JWTs, private keys, Postgres URLs with inline passwords), files that must never be
tracked (`.env`, `__pycache__`, `.pyc`, `.venv`, `data/raw`, `.bak`), broken Python, JSON,
TOML, or XML syntax, and unpinned dependencies (warning, not a block).

`python check.py --full` also runs the template test suites. That is not in the hook,
because a slow hook gets bypassed.

Scope: the hook checks staged files. A bare `python check.py` checks tracked files **plus
untracked ones that .gitignore does not exclude**, so a new poisoned file that was never
staged still gets caught. Files inside `.gitignore` are skipped, and an untracked `.env`
sitting on disk is correct and is not flagged.

**Why the checks are deliberately narrow.** A checker that cries wolf gets bypassed. The
first time it blocks a commit for a reason you disagree with, you will type `--no-verify`,
and from then on it enforces nothing. So every check fires only on things that are
unambiguously wrong. Do not add fuzzy checks. If you find yourself using `--no-verify`
routinely, the check is wrong and should be fixed, not routed around.

`hooks/` is used via `core.hooksPath` rather than `.git/hooks` so the hook is tracked in
the repo. A hook that lives only in `.git/hooks` is invisible to git, does not survive a
fresh clone, and cannot be reviewed.

## The data pipeline, in order

The prompts are separate on purpose, because the failures are separate. A wrong extract
cannot be cleaned, it just becomes a clean wrong answer.

1. `prompts/sql-extract.md` gets the data out, with the grain declared and the row counts
   reconciled. Writes to `data/raw/`.
2. `prompts/data-cleaning.md` turns raw into processed, logging every dropped row.
3. `prompts/data-analysis-project.md` answers the question and attacks its own finding.
4. `prompts/dashboard-build.md` or `prompts/portfolio-writeup.md` presents it.

`docs/sql-patterns.md` is the reference the first step checks itself against.

## How to use it

1. Open a fresh chat.
2. Paste the block from `00-core/operating-rules.md`.
3. Paste the prompt you need from `prompts/`.
4. Fill the `{{ }}` slots.
5. Do not let it past a STOP gate until you have actually confirmed the gate. The gates
   are the part that does the work. Skipping them turns every one of these back into a
   generic prompt.

## Sources this is built on

Not invented here. Where a published standard exists, the kit uses it and says so.

1. Tidy data, the target shape for any cleaned dataset: Wickham H (2014), "Tidy Data",
   Journal of Statistical Software 59(10), doi:10.18637/jss.v059.i10
2. The colorblind-safe data palette: Okabe M, Ito K, "Color Universal Design",
   https://jfly.uni-koeln.de/color/
3. Schema validation: pandera, chosen over Great Expectations because it is pandas-first
   and needs no configuration. Great Expectations is built for multi-engine pipelines with
   governance and shared expectation suites, which is not this. Verified on pandera 0.32.1.
4. Structured outputs on the Claude API, now generally available and using constrained
   decoding: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
   API shape verified against anthropic SDK 0.117.0 by introspection, not from memory.

`docs/llm-patterns.md` is the exception. It is not derived from anything public. It is the
architecture from career-ops, written down.

## Prompts you already have that live elsewhere

These predate this kit and are not duplicated here. Point at them, do not rewrite them.

1. `microsaas-build-prompt.md` (phase-gated Flask build with 7 idea cards)
2. `idea-discovery-prompt.md` (feeds Phase 0 of the above)
3. `C:\Users\brand\career-ops\practice\daily_practice_prompt.md` (SQL and pandas drilling)

When you next touch any of them, run `prompts/prompt-checker.md` over it first.

## What this kit does not do

1. It does not make a language model accurate. It makes it say when it is not.
2. The prompt-checker runs simulated dry runs, not real benchmarks. Treat its verdict as
   a code review, not a measurement.
3. The Flask scaffold's tests pass without network access. That proves the shape, not the
   integration.
4. The Power BI theme and the Tableau palette are syntax-valid but have not been imported
   into either tool. Power BI silently ignores properties it does not recognize, so an
   ignored property looks exactly like a working one until you look.
5. `templates/analysis-project/02_clean.py` and `schema.py` were run against a file with
   six deliberate defects and caught all six. That proves the pattern, not your data.
6. `docs/sql-patterns.md` is reasoned from PostgreSQL semantics and is not machine-tested.
   Every claim in it is checkable in about a minute in DB Fiddle. Check the ones you plan
   to rely on.
7. `check.py` enforces mechanical rules only. It cannot tell you a prompt is bad, a
   finding is wrong, or a dashboard is useless. It buys back attention for the judgment
   calls, it does not make them.
8. Zero of the prompts in `prompts/` have been through `prompts/prompt-checker.md`. The
   kit does not yet meet its own standard.
9. `templates/llm-classifier/` has 22 tests that pass with no API key, which proves the
   scorer. `classify.py`'s branching was proven against an injected fake client. Neither
   proves a live call, and no live call has been made.
10. Ten prompts is more than anyone remembers. The realistic set you will reach for is
   three or four. The rest are reference, and that is fine, as long as you know which is
   which.

## Versioning

Every prompt file carries a version in its name once it has been through the checker
(`<name>-prompt-v2.md`). The changelog goes at the top of the file. Do not overwrite a
prompt in place with no record of what changed, because when output quality drops you will
have no way to tell which edit did it.
