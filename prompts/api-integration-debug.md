# API INTEGRATION AND PRODUCTION DEBUG

Two related jobs in one file. Section A is for wiring up a third-party API. Section B is
for when something that used to work is now broken in production.

Both are written against real failures from your projects: Cloudflare bot protection and
OAuth scope errors on Loadout Oracle, GEOparse memory errors on the aging clock, SP-API
fields that do not exist, JSON parsing out of LLM text responses.

**How to use:** fresh chat, paste `00-core/operating-rules.md`, then one section below.

---

## SECTION A: NEW API INTEGRATION

> You are integrating a third-party API. The operating rules above apply.
>
> ### Phase 0: Reconnaissance, before any code
>
> Search and verify, then answer. Mark anything you cannot verify as unconfirmed rather
> than guessing.
>
> 1. **Auth model.** API key, OAuth 2.0, or signed request? If OAuth: which grant, which
>    scopes, what is the token lifetime, and does an unattended server-side flow work for a
>    single operator with no user login? Say how long the refresh token lasts before I have
>    to touch it by hand.
> 2. **The fields.** Does the API actually return every field I need? Name each one against
>    the real response schema. Any field it does not return, list now with the workaround
>    or the honest "there is none."
> 3. **Limits.** Rate limits, quotas, pagination, and what the error looks like when you hit
>    each. What is the retry guidance.
> 4. **Gates.** Registration, developer token approval, review process, cost. Lead time on each.
> 5. **Defenses.** Is the endpoint behind Cloudflare or bot protection? Does it require a
>    real user agent or specific headers? This has bitten this exact stack before.
>
> STOP. Wait for approval.
>
> ### Phase 1: Prove one call
>
> Get exactly one real call working end to end before building anything around it. Show me
> the raw response, not a summary of it. Everything downstream depends on the real shape,
> not the documented shape, and those differ.
>
> ### Phase 2: Client layer
>
> Then build: retry with exponential backoff on 429 and 5xx, per-call error isolation,
> a timeout on every call, no secrets in logs, and a normalization function that turns the
> raw response into my own shape so the rest of the code never sees theirs.
>
> ### Phase 3: Fixtures
>
> Save real request and response pairs as test fixtures. From here on, tests run against
> fixtures, not the live API. This is what lets me tell a logic bug from an API change later.

---

## SECTION B: PRODUCTION DEBUG

> Something that worked is broken. The operating rules above apply, and one more:
> **do not propose a fix before you can state the cause.** A fix without a cause is a guess
> that produces a clean-looking diff and changes nothing.
>
> ### Step 1: What actually changed
>
> Ask me for, and do not proceed without: the exact error text, the full traceback, the
> last deploy, and whether it ever worked. Then state which of these three it is:
> my code changed, their API changed, or the data changed. Say how you know.
>
> ### Step 2: Reproduce
>
> Reproduce it in the smallest possible script. If you cannot reproduce it, say so. Do not
> reason about a bug you have not seen.
>
> ### Step 3: Trace to the source
>
> Find where the bad value is created, not where it is noticed. These are usually different
> places, and fixing the second one is how you get a bug that comes back.
>
> Ask: if I patch here, does the real source re-introduce this on the next run? If yes,
> this is the wrong place. Say so and re-scope.
>
> ### Step 4: State the cause
>
> One paragraph. The mechanism, in plain English. If you cannot write this paragraph, you
> have not found the bug. Say that instead of proposing a fix.
>
> ### Step 5: Fix
>
> Smallest change that addresses the cause. Then: what else touches this code path, and
> what did this fix just break?
>
> ### Step 6: Prove it
>
> Run it. Show the output. Add a test that fails on the old code and passes on the new.
> If you cannot run it, say exactly what I need to run and what output confirms the fix.
> Do not say it is fixed. Say what evidence would show it is fixed.
>
> ## Input
>
> {{ SYMPTOM: what is broken, exact error text, full traceback }}
>
> {{ CONTEXT: what changed recently, when it last worked }}
>
> {{ CODE: the relevant files or repo }}
