# SQL EXTRACT

For pulling data out of a database correctly. Separate from cleaning, because a wrong
extract cannot be cleaned. It just becomes a clean wrong answer.

**How to use:** fresh chat, paste `00-core/operating-rules.md`, then below the line.

**Related:** `docs/sql-patterns.md` has the failure modes and the reconciliation queries
in reference form. This prompt drives the work. That doc is what you check against.

---

> You are writing a SQL extract. The operating rules above apply, plus these.
>
> **The rule that matters most: a join can multiply rows silently.** No error, no warning,
> just a number that is wrong in a direction that usually looks plausible. Every join you
> write gets a row count before and after and an explicit statement of its cardinality.
> This is not optional and it is not paranoia. It is the single most common way an analyst
> ships a wrong number.
>
> ## Phase 0: The contract
>
> Before writing any SQL, state:
>
> 1. **The grain of the output.** One row is one what? Say it in one sentence.
> 2. **The expected row count**, with a rough order of magnitude and where it comes from.
>    You are committing to a number now so that a surprise later is visible as a surprise.
> 3. **Every table**, its grain, and its key. If you do not know a table's grain, say so.
>    Do not assume it.
> 4. **Every join**, and its cardinality: one to one, one to many, or many to many. A many
>    to many join is a bug until proven otherwise. If you write one, justify it.
> 5. **The time window and the timezone.** State whether the boundaries are inclusive.
> 6. **Filters**, and for each one, roughly how much it should remove.
>
> STOP. Wait for approval.
>
> ## Phase 1: Write it, defensively
>
> Rules, each of which exists because of a specific silent failure:
>
> 1. **Never `SELECT *` in an extract.** Name every column. A new column upstream should
>    not change your output.
> 2. **A filter on the right table of a LEFT JOIN belongs in the ON clause, not the WHERE
>    clause.** In WHERE it silently turns the LEFT JOIN into an INNER JOIN, because NULL
>    fails the predicate and the row disappears. This is the most common SQL bug that
>    produces no error.
> 3. **Never `NOT IN` with a subquery that can return NULL.** It returns zero rows. Use
>    `NOT EXISTS`, which handles NULL correctly.
> 4. **Aggregate before joining, not after**, whenever the join is one to many. Joining
>    first and aggregating after double counts, and the total looks like a plausible number.
> 5. **`LIMIT` without `ORDER BY` is non-deterministic.** Same query, different rows. Never
>    ship it in an extract, and never use it to "check" anything.
> 6. **`COUNT(*)` counts rows, `COUNT(col)` skips NULLs.** Say which you meant.
> 7. **Integer division truncates in PostgreSQL.** `1/2` is `0`. Cast before dividing.
> 8. **`NULL` is not equal to `NULL`.** Use `IS NULL`, and remember `NULL` in an equality
>    join drops the row.
> 9. **Beware `BETWEEN` on timestamps.** `BETWEEN '2025-01-01' AND '2025-01-31'` excludes
>    almost all of January 31, because the end is midnight. Use `>= start AND < next_day`.
> 10. **Window functions over `GROUP BY` when you need detail plus an aggregate.** Do not
>     self-join a table to itself to get a total. It is slower and it fans out.
> 11. CTEs for readability, one logical step each. Name them what they are.
>
> ## Phase 2: Prove it before I use it
>
> Run and show me, every time:
>
> 1. **Row count at every CTE stage.** Where does the number change and does that match
>    what you predicted in Phase 0?
> 2. **Key uniqueness on the output.** `COUNT(*)` versus `COUNT(DISTINCT key)`. If those
>    differ, the extract fans out and everything downstream is wrong.
> 3. **Reconciliation to the source.** Pick a total that exists independently, a known
>    count, a known sum, and confirm your extract reproduces it. If nothing independent
>    exists, say so plainly, because then nothing is verifying you.
> 4. **NULL rates per output column.** An unexpected NULL rate is usually a failed join.
> 5. **Spot check five rows by hand** against the source tables. Show them.
>
> If a count differs from your Phase 0 prediction, do not adjust the prediction. Explain
> the difference. The prediction is the test.
>
> ## Phase 3: Make it repeatable
>
> 1. The query lives in a `.sql` file in the repo, not in a client window.
> 2. Parameters at the top, not hardcoded in the middle.
> 3. A header comment: what it extracts, the grain, the expected row count, and the
>    reconciliation check that proves it.
> 4. If it runs on a schedule, say what happens when the source is late or partial. A
>    pipeline that silently extracts half a day is worse than one that fails.
> 5. Write to `data/raw/` as the immutable extract. Cleaning is a separate step.
>
> ## Phase 4: Performance, only if it is slow
>
> Do not optimize before it is correct. If it is slow, run `EXPLAIN ANALYZE` and show it.
> Read the actual plan. Do not guess at an index.
>
> ## Input
>
> {{ SOURCE: database, schema, tables available }}
>
> {{ NEED: what the output should contain and what it feeds }}
>
> {{ GRAIN: one row is one what }}
>
> {{ KNOWN_TOTALS: anything I already know is true that the extract should reproduce }}
