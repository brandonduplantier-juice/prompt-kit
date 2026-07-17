# LLM classifier template

The pattern from career-ops, extracted so the next system starts here.

**The model extracts facts. Code makes decisions.**

```
schema.py     the facts contract. No scores. Ever.
classify.py   the model call. Structured output, temperature 0, facts only.
score.py      pure function, facts to decision. No API, no network, no clock.
test_score.py tests score.py against fixtures. No API key. Runs in milliseconds.
fixtures/     real input and real facts, captured from live runs.
```

## Why the split

Let the model return `fit: 4.5` and you lose: reproducibility, auditability, the ability
to tune a weight, and the ability to test without burning tokens. Keep the split and you
can rerun every decision the system has ever made, offline, in under a second.

The test that you got it right: `python -m pytest` passes with no `ANTHROPIC_API_KEY` set.

## Use

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m pytest -q                 # scoring tests, no API key needed

$env:ANTHROPIC_API_KEY="sk-ant-..."  # only needed for live classification
python classify.py posting.txt my_fixture_name
```

## To adapt this

1. Rewrite `schema.py` for your domain. Keep the rule: every field is checkable against
   the source. If you cannot point at the sentence that makes it true, it is a judgment
   and it does not belong there.
2. Rewrite `hard_kills` and `WEIGHTS` in `score.py`. These are your constraints as data.
3. Capture 5 to 10 real fixtures before you trust any of it.
4. Bump `SCORER_VERSION` on every weight change and log it with each decision.

## Read first

`docs/llm-patterns.md`. It has the failure catalog, including the three cases where
structured outputs do NOT guarantee your schema, which each look like a bug in your code.
