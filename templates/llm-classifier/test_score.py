"""
Scoring tests. No API key. No network. No cost. Runs in milliseconds.

That is the entire point of splitting classify.py from score.py. If these tests needed
an API key you would stop running them, and then the decision layer would be untested
in a system whose only job is making decisions.

    python -m pytest -q
"""

import json
from pathlib import Path

import pytest

from schema import Facts
from score import SCORER_VERSION, hard_kills, score

FIXTURES = Path(__file__).parent / "fixtures"


def make(**over) -> Facts:
    """A passing baseline. Each test overrides one thing, so a failure names its cause."""
    base = dict(
        source_complete=True, remote_us=True, work_mode="remote",
        max_years_required=2, degree_hard_required=False, seniority="entry",
        title_is_analyst=True, stack_mentioned=["sql", "python", "power bi", "tableau"],
        excludes_ohio=False, evidence_years="2+ years of experience required.",
        evidence_remote="This role is fully remote within the United States.",
    )
    base.update(over)
    return Facts(**base)


# ---------------------------------------------------------------- hard gates

def test_baseline_passes_and_scores_well():
    d = score(make())
    assert d.verdict == "pass"
    assert d.score > 8.0
    assert d.scorer_version == SCORER_VERSION


def test_not_remote_is_killed():
    assert "not remote in the US" in score(make(remote_us=False)).kills


def test_onsite_is_killed():
    assert score(make(work_mode="onsite")).verdict == "kill"


def test_too_many_years_is_killed():
    d = score(make(max_years_required=5))
    assert d.verdict == "kill"
    assert "requires 5 years" in d.kills[0]


def test_years_at_the_ceiling_is_not_killed():
    """Boundary. 3 is accepted, 4 is not. Off-by-one here silently drops good roles."""
    assert score(make(max_years_required=3)).verdict == "pass"
    assert score(make(max_years_required=4)).verdict == "kill"


def test_degree_gate_is_killed():
    assert score(make(degree_hard_required=True)).verdict == "kill"


def test_senior_is_killed():
    assert score(make(seniority="senior")).verdict == "kill"


def test_ohio_exclusion_is_killed():
    assert score(make(excludes_ohio=True)).verdict == "kill"


def test_a_kill_scores_zero_not_a_low_number():
    """A killed role must not compete on score. Zero, not 3.2."""
    assert score(make(remote_us=False)).score == 0.0


def test_multiple_kills_are_all_reported():
    d = score(make(remote_us=False, seniority="senior", degree_hard_required=True))
    assert len(d.kills) >= 3


# ---------------------------------------------------------------- the casing trap

def test_enum_casing_does_not_break_the_kill():
    """
    Structured outputs do NOT guarantee enum capitalization. The model can return
    "Onsite" for "onsite". If the scorer compared with ==, this role would silently
    PASS. This test exists because that failure is invisible.
    """
    f = make()
    object.__setattr__(f, "work_mode", "ONSITE")
    assert score(f).verdict == "kill"


def test_stack_casing_is_normalized():
    d = score(make(stack_mentioned=["SQL", "Python", "Power BI", "Tableau"]))
    assert d.verdict == "pass"
    assert d.score > 8.0


# ---------------------------------------------------------------- nulls

def test_unstated_facts_do_not_kill():
    """null means the source did not say. That is not evidence against the role."""
    d = score(make(remote_us=None, max_years_required=None, degree_hard_required=None,
                   excludes_ohio=None))
    assert d.verdict == "pass"


def test_unstated_years_earns_no_points():
    assert score(make(max_years_required=None)).score < score(make()).score


def test_incomplete_source_is_not_scored():
    """Scoring a truncated posting produces a confident number about nothing."""
    d = score(make(source_complete=False))
    assert d.verdict == "incomplete"
    assert d.score == 0.0


# ---------------------------------------------------------------- determinism

def test_scoring_is_deterministic():
    assert [score(make()).score for _ in range(50)].count(score(make()).score) == 50


def test_every_pass_shows_its_arithmetic():
    """A score with no explanation is the thing this whole design exists to prevent."""
    d = score(make())
    assert d.reasons
    assert any("of 10" in r for r in d.reasons)


def test_stack_overlap_is_monotonic():
    one = score(make(stack_mentioned=["sql"])).score
    four = score(make(stack_mentioned=["sql", "python", "tableau", "r"])).score
    assert four > one


def test_unknown_stack_items_are_ignored_not_credited():
    assert score(make(stack_mentioned=["cobol", "fortran"])).score \
        < score(make(stack_mentioned=["sql"])).score


# ---------------------------------------------------------------- fixtures

def test_no_judgment_fields_leaked_into_the_schema():
    """
    The architectural invariant, enforced. If someone adds `fit` or `score` to Facts,
    this fails. That is the whole design in one assertion.
    """
    banned = {"fit", "score", "rating", "rank", "priority", "should_apply",
              "recommendation", "verdict"}
    leaked = banned & set(Facts.model_fields)
    assert not leaked, f"judgment fields in the facts schema: {leaked}"


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.json")))
def test_fixtures_still_parse_and_score(path):
    """
    Every captured real run must still validate and score. This is what catches schema
    drift: change a field, and yesterday's real data stops loading, loudly.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    d = score(Facts(**data["facts"]))
    assert d.verdict in {"pass", "kill", "incomplete"}
    assert 0.0 <= d.score <= 10.0
