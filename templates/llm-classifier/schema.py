"""
The data contract between the model and your code.

The single rule: every field here is a FACT, checkable against the source text.
No scores. No judgments. No "fit". Those are computed in score.py from these facts.

If you cannot point at the sentence in the source that makes a field true, it does not
belong in this file.

Verified against anthropic SDK 0.117.0 and pydantic 2.x.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Enum casing is NOT guaranteed by structured outputs. The model may return "remote"
# for "Remote". Never define two values that differ only in capitalization, and compare
# case-insensitively downstream. See docs/llm-patterns.md.
WorkMode = Literal["remote", "hybrid", "onsite", "not_stated"]
Seniority = Literal["intern", "entry", "mid", "senior", "lead", "not_stated"]


class Facts(BaseModel):
    """
    What the model read. Not what it thinks.

    Every Optional field exists so the model has a way to say "the source does not say."
    A model with no way to say "I don't know" will guess, fluently, and you will not
    notice. That is why the prompt explicitly says null is a correct answer.
    """

    # Completeness. The model's own read on whether the input was enough to work with.
    # If this is False, do not score. Scoring a truncated posting produces a confident
    # number about nothing.
    source_complete: bool = Field(
        description="True only if the source text contains enough to answer the fields "
                    "below. False if it is truncated, a login wall, or a stub."
    )

    # Facts. Each is checkable against the text.
    remote_us: Optional[bool] = Field(
        description="True if explicitly hirable remotely from anywhere in the US. "
                    "False if it states otherwise. null if the source does not say."
    )
    work_mode: WorkMode
    max_years_required: Optional[int] = Field(
        description="The highest number of years of experience stated as REQUIRED. "
                    "null if no year count is stated. 0 if it says no experience required."
    )
    degree_hard_required: Optional[bool] = Field(
        description="True only if a completed degree is required with no equivalent-"
                    "experience clause. False if a clause exists or none is required."
    )
    seniority: Seniority
    title_is_analyst: bool = Field(
        description="True if the job title itself contains an analyst-family term."
    )
    stack_mentioned: list[str] = Field(
        description="Tools and technologies named in the source, verbatim, lowercase. "
                    "Only what appears in the text. Never inferred, never expanded."
    )
    excludes_ohio: Optional[bool] = Field(
        description="True if the source names state restrictions that exclude Ohio."
    )

    # Evidence. This is how you catch fabrication. If the quote is not in the source,
    # the fact is invented, and you found it in seconds instead of never.
    evidence_years: Optional[str] = Field(
        description="The exact sentence from the source that establishes "
                    "max_years_required. null if no year count is stated."
    )
    evidence_remote: Optional[str] = Field(
        description="The exact sentence from the source that establishes remote_us."
    )


# NOTE: there is deliberately no `fit`, no `score`, no `should_apply`, and no `priority`
# in this model. The moment one appears here, every decision this system makes becomes
# unauditable and untunable. See docs/llm-patterns.md.
