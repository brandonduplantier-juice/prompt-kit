# DATA DICTIONARY

One row per column in `data/processed/clean.parquet`. Fill it once. It is the thing that
stops the same metric from meaning two things three weeks apart.

**Grain:** one row is one <state it in one sentence>.
**Key:** <column(s)>. Verified unique in 02_clean.py.
**Source:** <where raw came from, and when it was pulled>.
**Real or synthetic:** <say it plainly>.

| Column | Type | Definition | Units | Allowed values | Nullable | Derived from | Missing means |
|---|---|---|---|---|---|---|---|
| record_id | int64 | | | unique, positive | no | raw | n/a |
| age | int64 | Age at <which event, exactly> | years | 0 to 120 | no | raw | row dropped |
| category | string | | | A, B, C | no | raw, uppercased and trimmed | row dropped |
| value | float64 | | | >= 0 | yes | raw | genuinely unknown, see flag |
| value_was_missing | bool | True if value was absent in raw | | | no | derived in 02_clean | n/a |
| event_date | datetime | | | not future | no | raw, parsed as %Y-%m-%d | row dropped |
| outcome | bool | | | | no | raw, mapped 1/0 | row dropped, never imputed |

## Notes that matter

1. **"Missing means" is the column people skip and then regret.** A zero that means zero
   and a zero that means "not recorded" are different numbers with the same appearance.
2. **Any column with a `_was_missing` flag was imputed.** Say what it was imputed with and
   why in METHODS.md. Never impute the outcome.
3. **If a definition has an "as of" date or a time window baked into it, write it here.**
   "Age" is meaningless without saying age at what.
4. **When a definition changes, do not edit in place.** Add a row to the changelog below.
   A metric that quietly changed definition is how two reports disagree and nobody can
   say when it started.

## Changelog

| Date | Column | Change | Why |
|---|---|---|---|
