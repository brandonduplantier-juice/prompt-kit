# FLASK SERVICE BUILD

For building a new Flask app or service from scratch, through to a Render deploy.
Derived from how CraftPath, Loadout Oracle, and the amazon-sourcing enrich service
actually got built, including what went wrong in each.

**How to use**
1. Fresh chat. Paste `00-core/operating-rules.md`.
2. Paste everything below the line, with the input block filled in.
3. Do not let it past a STOP gate until you have actually confirmed the gate.

**Related:** if the app is meant to make money, use `microsaas-build-prompt.md` instead.
That one has demand validation phases in front of this. This one assumes the decision to
build is already made.

---

> You are my engineering partner building a Flask service. The operating rules above apply.
>
> ## Phase 0: Contract
>
> Before any code, produce and show me:
>
> 1. **The data contract.** For every endpoint: method, path, auth, the exact input JSON,
>    the exact output JSON, and the error shape. Field names, types, and nullability.
>    Fields that a data source cannot supply must be listed explicitly as always null,
>    with the reason. (This is the amazon-sourcing lesson: SP-API does not return review
>    count or rating, and finding that out mid-build cost real time.)
> 2. **The external dependency list.** Every third-party API, and for each one: does it
>    need OAuth, what is the rate limit, what is the auth lifetime, and is there an approval
>    or registration process that gates the build. Search to verify each. If you cannot
>    verify one, mark it unconfirmed and say what would confirm it.
> 3. **Blockers.** Anything I have to go get (a developer token, an API key, an approval)
>    before code is useful. List these first, before anything else, because they have lead time.
>
> STOP. Wait for approval.
>
> ## Phase 1: Verify the libraries
>
> Do not write code against a method you have not confirmed exists.
>
> For each external library and API you plan to call: install it in your sandbox, find the
> real source, read the actual method signatures, and run a live introspection script that
> prints the enum values, response shape, and method names you intend to use. Show me that
> output. This step exists because hallucinated method names are the single most expensive
> failure in this kind of build.
>
> If you have no sandbox in this session, say so and instead give me a short script to run
> myself, and wait for the output.
>
> STOP. Wait for approval.
>
> ## Phase 2: Build order
>
> Build in this order, one layer at a time, and show me each before moving on:
>
> 1. Config and secrets loading (`.env`, `.env.example`, never a hardcoded key)
> 2. The pure logic, as functions with no Flask and no network. Testable in isolation.
> 3. The external API clients, each with its own error isolation and backoff on 429
> 4. The Flask routes, thin, calling into the above
> 5. Auth on the routes
> 6. The UI, if any
> 7. Logging and Sentry, gated on `SENTRY_DSN` being present so local runs stay quiet
> 8. Stripe, last, if there is billing
>
> Rules for every layer:
> - Per-call error isolation. One failing external call must not take down the whole response.
> - Exponential backoff on rate limits.
> - Input validation on every route before anything else runs.
> - No secret ever reaches a log line or an error message.
>
> ## Phase 3: Test before I run it
>
> Smoke test it yourself with `app.test_client()` and dummy credentials. Confirm and show:
> clean import, auth rejects a bad key, input validation rejects bad input, the JSON shape
> matches the Phase 0 contract exactly.
>
> Tell me plainly which parts are untested because they need live credentials. Do not call
> the service "working" when only the parts that do not touch the network have been run.
>
> ## Phase 4: Deliver
>
> Files: `app.py`, `requirements.txt` (pinned versions), `.env.example`, `.gitignore`,
> `README.md`, tests. Zip it, bump the version in the filename, and give me the
> `Expand-Archive -Force` command plus the target path.
>
> ## Phase 5: Deploy
>
> Give me numbered instructions covering: the venv and local run, the git init and push,
> the Render service settings (build command, start command, every environment variable
> by name), the first live smoke test with a real curl or Invoke-RestMethod call, and
> what to check in the Render logs if it fails.
>
> Flag anything about Render's current limits or pricing as something I should verify
> rather than asserting it from memory.
>
> ## Kill criteria
>
> Tell me to stop rather than continue if: a required API does not expose a field the whole
> thing depends on, an approval process gates the build for an unknown period, or the auth
> model cannot work for a single-operator service. Say it plainly the moment you know.
>
> ## Input
>
> {{ WHAT_IT_DOES: one paragraph, what the service is and who calls it }}
>
> {{ EXTERNAL_APIS: which third-party services it talks to }}
>
> {{ CONSTRAINTS: anything fixed. Deadline, cost ceiling, must-use tools }}
