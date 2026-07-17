# DATA CLEANING

For turning a messy file into a dataset you can defend. The failure mode this is built
against: cleaning that quietly changes the answer, and nobody notices because nobody
logged what was dropped.

**How to use:** fresh chat, paste `00-core/operating-rules.md`, then below the line.

**Grounding:** the target shape is tidy data, as defined in Wickham H (2014), "Tidy Data",
Journal of Statistical Software 59(10), doi:10.18637/jss.v059.i10. One variable per column,
one observation per row, one observational unit per table.

---

> You are cleaning a dataset. The operating rules above apply, plus these.
>
> **The three rules that matter more than the rest.**
>
> 1. **Raw data is read-only and immutable.** Never edit the source file. Never overwrite
>    it. Cleaning is a script that reads raw and writes processed. If the only record of
>    what you did is the cleaned file, the work is not reproducible and neither of us can
>    say what happened.
> 2. **Every row that leaves is logged with a count and a reason.** Row count before, row
>    count after, and why, for every single step. A clean file with no drop log is a file
>    with an unknown population.
> 3. **Cleaning decisions change results.** Every judgment call is a fork in the analysis.
>    Say which forks you took and what the other branch looks like.
>
> ## Phase 0: Look before you touch
>
> Do not clean anything yet. Profile and report:
>
> 1. Shape: rows, columns, memory, file encoding, delimiter.
> 2. Per column: dtype as loaded, dtype it should be, missing count and percent, unique
>    count, and for anything low-cardinality, the actual value counts.
> 3. Duplicates: on the full row, and on whatever should be the key.
> 4. Ranges: min, max, and the five smallest and five largest values of every numeric column.
>    The extremes are where the sentinel values hide.
> 5. Impossibilities: negative counts, ages over 120, dates in the future, dates before the
>    thing existed, IDs appearing more than they should.
>
> Then answer, in words:
> - **Is this tidy?** One variable per column, one observation per row, one unit per table.
>   If not, say exactly which rule it breaks and what the reshape is.
> - **What is the grain?** One row is one what? If you cannot say this in one sentence,
>   stop, because nothing downstream will be correct.
> - **What is the intended key**, and is it actually unique?
>
> STOP. Wait for approval before changing anything.
>
> ## Phase 1: The traps, checked explicitly
>
> Go through each and report what you found, including "not present":
>
> 1. **Sentinel values posing as data.** `-1`, `999`, `9999`, `0`, `-99`, `1900-01-01`,
>    `1970-01-01`, `N/A`, `NA`, `null`, `NULL`, `none`, `-`, `unknown`, `.`, empty string.
>    A `999` in an age column is missing data that will silently average into your result.
> 2. **Dates.** Is `03/04/2025` March 4 or April 3? Say how you know rather than assuming.
>    Check for two-digit years, mixed formats in one column, Excel serial numbers, and
>    timezone. A date column that parses without error can still be wrong.
> 3. **Numbers stored as text.** Currency symbols, thousands separators, percent signs,
>    parentheses for negatives, trailing spaces, non-breaking spaces.
> 4. **Categories that are the same thing spelled differently.** Case, whitespace,
>    abbreviations, typos. Report the mapping you propose. Never merge two categories
>    without showing me the before and after counts.
> 5. **Units.** Mixed units in one column, unlabeled units, implied decimal places.
> 6. **Encoding damage.** Mojibake like `â€™` or `Ã©` means the file was read with the wrong
>    encoding. Fix the read, do not find-and-replace the symptoms.
> 7. **Leading zeros destroyed.** Zip codes, IDs, and account numbers read as integers lose
>    them permanently. Read as string.
> 8. **Float IDs.** An integer ID column with any missing value becomes a float and your
>    IDs become `12345.0`. Joins then fail silently.
>
> ## Phase 2: Missing data
>
> Missingness is information, not noise.
>
> 1. Report missingness per column and, more importantly, **whether it is patterned**. Is it
>    concentrated in one subgroup, one time period, one source system? Show it.
> 2. State which of these you believe it is and why: missing completely at random, missing
>    at random given observed variables, or missing not at random (the missingness depends
>    on the value itself, which is the dangerous one).
> 3. **Dropping rows with missing values changes the population you are analyzing.** If you
>    drop, say what the dropped rows look like compared to the kept ones. If they differ,
>    you have introduced bias and you must say so in the write-up.
> 4. Do not impute silently. If you impute, add a `<col>_was_missing` flag column, always.
> 5. Never impute the outcome variable.
>
> ## Phase 3: Duplicates and outliers
>
> 1. **Define a duplicate before removing one.** Is it identical rows, or the same entity
>    appearing twice with different values? Those need opposite handling. The second is
>    usually a real signal about the source system.
> 2. When rows conflict on the same key, say which you kept and by what rule. "First" is
>    not a rule unless the order is meaningful, and file order usually is not.
> 3. **Outliers are not errors.** An impossible value is an error. An extreme value is data.
>    Do not remove an extreme value because it is inconvenient. If you remove any value,
>    give the mechanism that makes it impossible, not the fact that it is far from the mean.
>
> ## Phase 4: Write the cleaning script
>
> Requirements:
> - Reads from `data/raw/`, writes to `data/processed/`. Never writes to raw.
> - Prints a row count after every step, with the reason for the change.
> - Ends with a hard schema assertion that raises rather than warns.
> - Deterministic. Same input gives the same output every run.
> - Every dropped row is either counted in the log or written to a rejects file.
>
> Use pandera for the schema gate. Import path `import pandera.pandas as pa`, class-based
> `pa.DataFrameModel`, and validate with `lazy=True` so it reports every failure at once
> instead of stopping at the first. See `templates/analysis-project/schema.py`.
>
> ## Phase 5: The report
>
> Produce a drop log I can paste into METHODS.md:
>
> | Step | Rows before | Rows after | Dropped | Reason |
> |---|---|---|---|---|
>
> Then answer:
> 1. **What percent of the original rows survived?** If it is under 90, that needs a
>    sentence of justification. If it is under 70, it needs a paragraph, and you should
>    tell me whether the surviving rows are still the population I think they are.
> 2. **Which cleaning decision would most change the final answer if reversed?** Name one.
> 3. **What did you have to guess?** List every assumption you could not verify from the
>    data or from me.
>
> ## Kill criteria
>
> Tell me to stop rather than continue if: the grain cannot be determined, the key is not
> unique and there is no rule to resolve it, missingness is concentrated in exactly the
> subgroup the question is about, or cleaning would drop so much that the remaining rows
> are a different population than the one asked about.
>
> ## Input
>
> {{ FILE: path, format, how it was produced }}
>
> {{ GRAIN: what one row is supposed to represent, if I know }}
>
> {{ DOWNSTREAM: what the cleaned data is for. This decides what "clean enough" means. }}
