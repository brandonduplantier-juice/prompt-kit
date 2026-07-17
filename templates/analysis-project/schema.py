"""
The data contract. Import this in 02_clean.py and in any downstream script.

Verified against pandera 0.32.1. Two things worth knowing:
  1. The pandas backend import path is `import pandera.pandas as pa`, not `import pandera`.
  2. `lazy=True` reports every failure at once. Without it, validation stops at the first
     one and you fix problems one slow run at a time.

Replace the model below with your actual columns. Delete what does not apply.
"""

import pandera.pandas as pa
from pandera.typing import Series


class Clean(pa.DataFrameModel):
    """One row is one <state the grain here, in one sentence>."""

    record_id: Series[int] = pa.Field(unique=True, nullable=False)
    subject_id: Series[int] = pa.Field(nullable=False)
    age: Series[int] = pa.Field(ge=0, le=120, nullable=False)
    category: Series[str] = pa.Field(isin=["A", "B", "C"], nullable=False)
    value: Series[float] = pa.Field(ge=0, nullable=True)
    value_was_missing: Series[bool] = pa.Field(nullable=False)
    event_date: Series[pa.typing.DateTime] = pa.Field(nullable=False)
    outcome: Series[bool] = pa.Field(nullable=False)

    class Config:
        # strict: an unexpected column is an error, not a shrug. Upstream added a column
        # and you want to know, not inherit it silently.
        strict = True
        # coerce: cast to the declared dtype, and fail loudly if a value cannot be cast.
        coerce = True

    @pa.check("event_date", name="not_in_the_future")
    def _not_future(cls, s: Series) -> Series[bool]:
        import pandas as pd
        return s <= pd.Timestamp.now()


def assert_clean(df):
    """
    Hard gate. Raises rather than warns. Call this at the end of cleaning and at the
    start of analysis, so a bad file cannot travel.
    """
    return Clean.validate(df, lazy=True)
