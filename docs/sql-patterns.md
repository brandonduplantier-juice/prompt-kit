# SQL PATTERNS AND SILENT FAILURES

Reference. `prompts/sql-extract.md` drives the work, this is what you check against.

Every item here produces a **wrong answer with no error message**. That is the selection
criterion. SQL that throws an error is not dangerous, because you fix it. SQL that returns
a plausible number is dangerous, because you ship it.

Written for PostgreSQL. Most of it applies elsewhere, but the integer division and the
`BETWEEN` behavior are worth re-checking on any other engine.

## 1. The LEFT JOIN that is secretly an INNER JOIN

The most common silent bug in analytics.

```sql
-- WRONG. The WHERE clause runs after the join. Rows with no matching claim have
-- NULL status, NULL fails the predicate, and the row vanishes. Your LEFT JOIN is gone
-- and no error was raised.
SELECT p.patient_id, c.status
FROM patients p
LEFT JOIN claims c ON c.patient_id = p.patient_id
WHERE c.status = 'paid';

-- RIGHT. Filter in the ON clause and the LEFT JOIN survives.
SELECT p.patient_id, c.status
FROM patients p
LEFT JOIN claims c ON c.patient_id = p.patient_id AND c.status = 'paid';
```

The tell: your row count equals the inner join count. If a LEFT JOIN did not preserve the
left row count, it was not a LEFT JOIN.

## 2. Join fan-out

A one-to-many join multiplies rows. Then every SUM is inflated and every AVG is weighted
by whatever the multiplicity happens to be.

```sql
-- WRONG. One patient with 3 claims becomes 3 rows, so their charge counts three times.
SELECT p.region, SUM(p.charge)
FROM patients p
JOIN claims c ON c.patient_id = p.patient_id
GROUP BY p.region;

-- RIGHT. Aggregate to the grain first, then join.
WITH claim_counts AS (
  SELECT patient_id, COUNT(*) AS n_claims
  FROM claims
  GROUP BY patient_id
)
SELECT p.region, SUM(p.charge), SUM(COALESCE(cc.n_claims, 0))
FROM patients p
LEFT JOIN claim_counts cc ON cc.patient_id = p.patient_id
GROUP BY p.region;
```

**The check you run every time:**

```sql
SELECT COUNT(*) AS rows, COUNT(DISTINCT patient_id) AS keys FROM your_output;
```

If those differ and the grain is one row per patient, the extract fans out and everything
downstream is wrong.

## 3. NOT IN with NULLs returns nothing

```sql
-- WRONG. If any row in the subquery has a NULL patient_id, this returns ZERO rows.
-- Not an error. Zero rows. Because x NOT IN (1, NULL) evaluates to UNKNOWN, not TRUE.
SELECT * FROM patients
WHERE patient_id NOT IN (SELECT patient_id FROM excluded);

-- RIGHT.
SELECT p.* FROM patients p
WHERE NOT EXISTS (SELECT 1 FROM excluded e WHERE e.patient_id = p.patient_id);
```

## 4. BETWEEN on timestamps loses the last day

```sql
-- WRONG. '2025-01-31' means 2025-01-31 00:00:00, so you lose almost all of the 31st.
WHERE event_ts BETWEEN '2025-01-01' AND '2025-01-31'

-- RIGHT. Half-open interval. Also correct across timezone and precision changes.
WHERE event_ts >= '2025-01-01' AND event_ts < '2025-02-01'
```

## 5. Integer division truncates

```sql
-- WRONG. Returns 0. Every time. No warning.
SELECT readmits / admissions AS rate FROM x;

-- RIGHT.
SELECT readmits::numeric / NULLIF(admissions, 0) AS rate FROM x;
```

`NULLIF` on the denominator also saves you from divide-by-zero. A NULL rate is honest.
A crashed query is honest. A silent 0 is neither.

## 6. COUNT(*) and COUNT(col) are different questions

`COUNT(*)` counts rows. `COUNT(col)` skips NULLs. `COUNT(DISTINCT col)` skips NULLs too.
Pick deliberately and say which you meant. An analyst who reports "we have 5,000 patients"
from `COUNT(patient_id)` when 300 are NULL has reported a number nobody asked for.

## 7. LIMIT without ORDER BY is non-deterministic

There is no default order in a relational table. Same query, different rows, different day.
Never in an extract. Never as a "quick check", because a quick check you cannot reproduce
is not a check.

Related: `ORDER BY` on a non-unique column is also non-deterministic within ties. Add a
tiebreaker.

## 8. NULL never equals NULL

`NULL = NULL` is UNKNOWN, not TRUE. So an equality join on a nullable column drops those
rows. Use `IS NULL`, or `IS DISTINCT FROM` when you want NULL-safe comparison.

## 9. Aggregates ignore NULLs, and that is sometimes wrong

`AVG(col)` divides by the count of non-null values, not the row count. If 40 percent of
your column is missing, your average is the average of the 60 percent who answered, which
may be a completely different population. `COALESCE(col, 0)` gives a different, also
defensible, and completely different number. Neither is automatically right. Say which
you chose.

## 10. Window functions instead of self-joins

```sql
-- Detail plus a group total, without fanning out.
SELECT
  patient_id,
  charge,
  SUM(charge) OVER (PARTITION BY region)               AS region_total,
  charge / SUM(charge) OVER (PARTITION BY region)      AS share_of_region,
  ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY event_ts DESC) AS recency_rank
FROM claims;
```

`ROW_NUMBER() ... = 1` is the correct way to get the latest row per entity. A self-join on
`MAX(event_ts)` duplicates on ties.

## 11. Deduplicating with a stated rule

```sql
-- "Kept first" is not a rule. File order is not meaningful. State the actual rule.
WITH ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY patient_id
      ORDER BY updated_at DESC, source_id ASC   -- rule: newest, ties broken by source
    ) AS rn
  FROM raw_patients
)
SELECT * FROM ranked WHERE rn = 1;
```

## 12. The reconciliation queries you run every time

```sql
-- Grain check. Must be equal if one row = one patient.
SELECT COUNT(*), COUNT(DISTINCT patient_id) FROM output;

-- Null rate per column. An unexpected NULL rate is a failed join, not a data quirk.
SELECT
  COUNT(*)                                                     AS rows,
  COUNT(*) - COUNT(status)                                     AS status_nulls,
  ROUND(100.0 * (COUNT(*) - COUNT(status)) / COUNT(*), 1)      AS status_null_pct
FROM output;

-- Row count at each stage. Run the CTEs one at a time and watch where it moves.

-- Reconcile to something independently known.
SELECT SUM(charge) FROM output;   -- does this match the finance total you were given?
```

If nothing independent exists to reconcile against, say so out loud, because then nothing
is checking you and the extract is trusted on vibes.

## 13. Extract hygiene

1. Name every column. `SELECT *` means an upstream schema change silently changes your
   output.
2. Parameters at the top of the file, not buried in the middle.
3. Header comment: what it extracts, the grain, the expected row count, the reconciliation.
4. The query lives in a `.sql` file in the repo, not a client window.
5. Extract to `data/raw/` and never modify it. Cleaning is a separate step, in a separate
   script, with its own log.
6. On a schedule: define what happens when the source is late or partial. A pipeline that
   silently extracts half a day is worse than one that fails loudly.

## 14. Style

Not correctness, but it is what a reviewer sees first.

1. Keywords uppercase, identifiers lowercase, `snake_case` throughout.
2. One CTE per logical step, named for what it is, not `cte1`.
3. Explicit `INNER JOIN`, not bare `JOIN`. Say what you meant.
4. No table aliases like `a`, `b`, `c`. Use `p` for patients if you must be short.
5. Comment the why, never the what. The SQL already says what.
