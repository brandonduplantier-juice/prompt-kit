"""
Cleaning script skeleton.

The pattern that matters: every step goes through `step()`, which prints the row count
before and after with a reason. At the end you have a drop log you can paste straight
into METHODS.md, and you can never silently lose rows.

Reads:  data/raw/       (never written to, never edited)
Writes: data/processed/clean.parquet
        data/processed/rejects.csv
        data/processed/drop_log.md
"""

import sys
from pathlib import Path

import pandas as pd

from schema import assert_clean

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

# Values that are missing data wearing a costume. Extend per dataset. A 999 in an age
# column will average into your result and nothing will warn you.
SENTINELS = ["", " ", "NA", "N/A", "n/a", "null", "NULL", "None", "none", "-", ".",
             "unknown", "UNKNOWN", "?", "-99", "-999", "999", "9999"]

_log = []
_rejects = []


def step(df, fn, reason):
    """Apply fn, record the row delta and the reason. Every drop passes through here."""
    before = len(df)
    out = fn(df)
    after = len(out)
    _log.append((reason, before, after, before - after))
    print(f"  {before:>8,} -> {after:>8,}  ({before-after:>+7,})  {reason}")
    return out


def reject(df, mask, reason):
    """Drop rows matching mask, but keep them so you can look at what left."""
    bad = df[mask].copy()
    if len(bad):
        bad["_reject_reason"] = reason
        _rejects.append(bad)
    return step(df, lambda d: d[~mask], reason)


def main():
    src = RAW / "source.csv"
    if not src.exists():
        sys.exit(f"missing {src}. Run 01_load.py first. Raw data is never generated here.")

    # dtype=str on read, then cast deliberately. This protects leading zeros on IDs and
    # zip codes, and stops an ID column with one missing value from becoming a float and
    # turning 12345 into '12345.0', which then fails every join silently.
    df = pd.read_csv(src, dtype=str, keep_default_na=False, encoding="utf-8")
    print(f"\nloaded {len(df):,} rows, {len(df.columns)} columns from {src}")
    print("\ndrop log")
    _log.append(("loaded from raw", len(df), len(df), 0))

    df = step(df, lambda d: d.replace(SENTINELS, pd.NA), "sentinels to NA")
    df = step(df, lambda d: d.rename(columns=str.strip).rename(columns=str.lower),
              "normalize column names")

    # Types. Cast explicitly, never rely on inference.
    df["record_id"] = pd.to_numeric(df["record_id"], errors="coerce").astype("Int64")
    df["age"] = pd.to_numeric(df["age"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    # format= is deliberate. Without it pandas infers per value and 03/04 flips meaning
    # halfway down the column with no error.
    df["event_date"] = pd.to_datetime(df["event_date"], format="%Y-%m-%d", errors="coerce")
    df["category"] = df["category"].str.strip().str.upper()

    # Imputation flag before any imputation. If a value is filled, the fact that it was
    # missing must survive into the analysis.
    df["value_was_missing"] = df["value"].isna()

    df = reject(df, df["record_id"].isna(), "record_id missing or unparseable")
    df = reject(df, df["event_date"].isna(), "event_date missing or unparseable")
    df = reject(df, df["age"].notna() & ((df["age"] < 0) | (df["age"] > 120)),
                "age impossible (not merely extreme)")
    # A sentinel became NA above, so it is now missing, not impossible. The schema says
    # age is not nullable, so a decision is forced here rather than deferred. Drop or
    # impute, but you cannot skip it. Whichever you pick, say so in METHODS.md.
    df = reject(df, df["age"].isna(), "age missing (includes rows whose age was a sentinel)")
    df = reject(df, df.duplicated(subset=["record_id"], keep="first"),
                "duplicate record_id, kept first (STATE YOUR RULE, file order is not a rule)")

    df["outcome"] = df["outcome"].map({"1": True, "0": False, "true": True, "false": False})
    df = reject(df, df["outcome"].isna(), "outcome unmappable, never impute the outcome")

    df = df.astype({"record_id": "int64", "age": "int64", "outcome": "bool"})

    # Hard gate. Raises. A bad frame does not get to travel downstream.
    df = assert_clean(df)

    df.to_parquet(OUT / "clean.parquet", index=False)
    if _rejects:
        pd.concat(_rejects).to_csv(OUT / "rejects.csv", index=False)

    start, end = _log[0][1], len(df)
    pct = 100 * end / start if start else 0
    lines = ["| Step | Before | After | Dropped | Reason |", "|---|---|---|---|---|"]
    lines += [f"| {i} | {b:,} | {a:,} | {d:,} | {r} |"
              for i, (r, b, a, d) in enumerate(_log)]
    lines.append(f"\n**{end:,} of {start:,} rows survived ({pct:.1f} percent).**")
    if pct < 90:
        lines.append("\nUnder 90 percent survived. Justify this in METHODS.md, and confirm "
                     "the surviving rows are still the population the question is about.")
    (OUT / "drop_log.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\n{end:,} of {start:,} rows survived ({pct:.1f} percent)")
    print(f"wrote {OUT/'clean.parquet'} and {OUT/'drop_log.md'}")


if __name__ == "__main__":
    main()
