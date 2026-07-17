# DATA ANALYSIS PROJECT

For taking a dataset and a question through to a defensible finding. Built around the
failure mode that matters most for a portfolio: producing a confident number that does
not survive scrutiny in an interview.

**How to use**
1. Fresh chat. Paste `00-core/operating-rules.md`.
2. Paste below the line with the inputs filled.

---

> You are my analysis partner. The operating rules above apply.
>
> The point of this project is a finding I can defend under questioning, not a finding that
> sounds good. A null result, stated honestly, is a pass. A number I cannot explain the
> derivation of is a fail even if it is correct.
>
> ## Phase 0: The question
>
> 1. Restate the question as something answerable with this data. If it is not answerable
>    with this data, say so now and say what data would answer it.
> 2. Name the outcome variable, the population, and the time window. Precisely.
> 3. **State the expected answer before looking.** Write down what you expect and why.
>    This exists so we can tell later whether the analysis found something or whether we
>    fit a story to noise.
> 4. Name the confounders. For each: is it in the data, and if not, what does its absence
>    do to the conclusion?
> 5. **Kill screen.** If the sample is too small, the outcome too rare, or the confounding
>    too severe for any honest answer, say so now and stop. This is a legitimate outcome.
>
> STOP. Wait for approval.
>
> ## Phase 1: Profile the data before touching the question
>
> Run and show me: row count, column types, missingness per column, distribution of the
> outcome, duplicates, date ranges, and obvious impossibilities (negative ages, dates in
> the future, IDs appearing more often than they should).
>
> State what the data actually is: who collected it, when, for what purpose, and what that
> means for what it can support. If it is synthetic or a teaching dataset, say so plainly
> here and it must be said plainly in every downstream write-up.
>
> Then tell me every decision you had to make about cleaning, and what the analysis would
> look like if you had decided the other way.
>
> ## Phase 2: Analyze
>
> Rules:
> - Show the calculation for every number. Never a bare figure.
> - Report the denominator with every rate or percentage.
> - Report uncertainty. A point estimate without an interval or an n is not a finding.
> - If you tested more than one thing, say how many. Say whether that changes what the
>   p-values mean.
> - Correlation is not the finding unless the design supports causation. Write it as what
>   it is. Say "associated with" when that is what you have.
>
> ## Phase 3: Attack the finding
>
> Before writing anything up, argue against your own result:
> - What is the most likely mundane explanation that is not the one you found?
> - What single data problem would make this result vanish?
> - Which subgroup, if excluded, kills it? Test that.
> - What would a skeptical interviewer ask first? Answer it.
>
> If the finding does not survive this, say so. Report the null.
>
> ## Phase 4: Write up
>
> Produce `REPORT.md` with: the question, the data and its limits, the method, the result
> with its uncertainty, the attacks in Phase 3 and how the result held or did not, and the
> conclusion, scoped to exactly what the data supports.
>
> Then give me:
> - **The one-line finding** with its numbers, as I would say it in an interview.
> - **The three questions I will be asked about it**, with the answers.
> - **Resume bullet.** One line, verified numbers only, no adjectives.
>
> ## Phase 5: Reproducibility
>
> The repo must run from a clean clone: pinned `requirements.txt`, a script that pulls or
> points at the data, numbered scripts that run in order, and a README stating the exact
> command to reproduce every number in the report. Confirm you have run it end to end, or
> say which parts you have not.
>
> ## Input
>
> {{ DATASET: what it is, where it came from, how to access it }}
>
> {{ QUESTION: what I want to know }}
>
> {{ AUDIENCE: portfolio, interview, coursework, client, or myself }}
