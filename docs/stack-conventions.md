# STACK CONVENTIONS

The things you currently re-explain in every chat. Paste this instead, or point a prompt
at it.

## Machine

1. Windows, PowerShell. Not bash. Instructions that assume bash will not run.
2. Repos live under `C:\Users\brand\`.
3. Downloads land in `D:\users\brand\downloads`.
4. Zips get extracted with `Expand-Archive -Force`, and delivered filenames carry a version
   number that goes up each time.
5. All files written UTF-8 with no BOM. A BOM breaks things quietly, which is worse than
   breaking loudly.

## Python

1. Python 3.13. One `.venv` per project, never a global install.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. `requirements.txt` is pinned to exact versions. An unpinned dependency is how a working
   Render deploy breaks with no commit.
3. Secrets in `.env`, loaded with `python-dotenv`. `.env` is gitignored. `.env.example`
   is committed with placeholder values.
4. No secret in a log line, an error message, or a commit. If one gets committed, rotating
   the key is the fix. Deleting the commit is not.

## Flask services

1. Auth on every route except `/health`. `X-API-Key` header for machine-to-machine.
2. Input validation before any work happens.
3. Every external call: timeout, exponential backoff on 429 and 5xx, and error isolation
   so one failing upstream does not kill the response.
4. Fields an upstream cannot supply stay explicitly null with the reason documented, rather
   than being dropped. Consumers depend on a stable shape.
5. Sentry initialized only when `SENTRY_DSN` is set, so local runs stay quiet.
6. Stripe goes in last, if at all.

## Deploys

1. Render for anything with a server. Push to `main` triggers the deploy.
2. Netlify for the static portfolio. Push triggers the build.
3. Streamlit Community Cloud for the notebook-style dashboards (the aging clock is there).
4. Every environment variable must be set in the host dashboard before the first deploy,
   not after the first failure.
5. Render free-tier services sleep. Verify current limits and pricing on Render's site
   rather than trusting a remembered number, including from me.

## Git

1. Remote base: `https://github.com/brandonduplantier-juice`
2. Active repos: `python-portfolio`, `career-ops`, `aging-clock`, plus per-project repos.
3. `*.bak` is gitignored. So is `.venv/`, `.env`, `data/raw/`, `__pycache__/`.
4. Commit messages containing `$` need a backtick escape in PowerShell: `` `$49k ``
5. The LF to CRLF warning on commit is normal on Windows and is not an error.

## Data and BI

1. PostgreSQL. Practice SQL on DB Fiddle set to PostgreSQL.
2. pandas for the Python side. Practice on Kaggle notebooks.
3. Shape the data upstream in SQL or pandas, not inside the BI tool.
4. Every metric gets a written definition: formula, numerator, denominator, grain, window,
   filters. Undefined metrics disagree with themselves inside a month.
5. Any number in a report or README must be printed by a script in the repo.

## Writing

1. No em-dashes and no en-dashes. Anywhere. Grep before delivering.
2. No emoji or special symbols in scripts that write to a terminal. PowerShell's codepage
   garbles them, which is how `Üá` ended up in the scan log.
3. Instructions start with `~instructions~` on its own line, then a numbered list.
4. Plain English. Explain any technical term the first time it appears.
