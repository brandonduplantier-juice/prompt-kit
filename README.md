# prompt-kit

Reusable prompts, templates, and conventions. Built from what is already in the project
history rather than from generic best practice.

## What is here

```
00-core/
  operating-rules.md          the block that goes at the top of every prompt
prompts/
  prompt-builder.md           makes new prompts from a rough idea
  prompt-checker.md           audits, tests, fixes, and loops on an existing prompt
  flask-service-build.md      new Flask app through to a Render deploy
  api-integration-debug.md    section A, new API. section B, production debug
  data-analysis-project.md    dataset and question to a defensible finding
  dashboard-build.md          Power BI, Tableau, Looker Studio, Streamlit
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
  analysis-project/           METHODS.md, README.md, repo layout
docs/
  stack-conventions.md        the environment facts you keep re-typing
  git-workflow.md             PowerShell git, per situation
```

## How to use it

1. Open a fresh chat.
2. Paste the block from `00-core/operating-rules.md`.
3. Paste the prompt you need from `prompts/`.
4. Fill the `{{ }}` slots.
5. Do not let it past a STOP gate until you have actually confirmed the gate. The gates
   are the part that does the work. Skipping them turns every one of these back into a
   generic prompt.

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

## Versioning

Every prompt file carries a version in its name once it has been through the checker
(`<name>-prompt-v2.md`). The changelog goes at the top of the file. Do not overwrite a
prompt in place with no record of what changed, because when output quality drops you will
have no way to tell which edit did it.
