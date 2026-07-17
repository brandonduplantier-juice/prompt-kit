"""
The decision layer. Pure function: facts in, decision out.

No API. No network. No clock. No randomness. No I/O.

That is what makes every scoring decision this system has ever made reproducible offline,
in milliseconds, with no API key. If you are ever tempted to call the model from this
file, the temptation is the bug.
"""

from dataclasses import dataclass, field

from schema import Facts

# Bump this whenever a weight or a rule changes, and log it with every decision.
# When yesterday's scores disagree with today's, this is how you tell whether the
# weights changed or the world did.
SCORER_VERSION = "2026-07-17.1"

# Your constraints, in one place, as data. Editing these is a one-line change and a
# rerun, not a prompt rewrite and a prayer.
MAX_YEARS_ACCEPTED = 3
CORE_STACK = {"sql", "postgresql", "python", "pandas", "power bi", "tableau",
              "looker", "looker studio", "excel", "snowflake", "r", "git"}

WEIGHTS = {
    "title_is_analyst": 2.0,
    "seniority_ok": 1.5,
    "years_ok": 1.5,
    "stack_overlap": 3.0,   # scaled by the fraction of core stack matched
    "no_degree_gate": 1.0,
}
MAX_SCORE = sum(WEIGHTS.values())


@dataclass
class Decision:
    verdict: str                       # "pass", "kill", or "incomplete"
    score: float                       # 0.0 to 10.0, or 0.0 when killed
    reasons: list[str] = field(default_factory=list)   # the arithmetic, in words
    kills: list[str] = field(default_factory=list)     # hard gates that fired
    scorer_version: str = SCORER_VERSION


def _norm(items):
    """Enum and string casing is not guaranteed by the model. Normalize before comparing."""
    return {str(i).strip().lower() for i in items}


def hard_kills(f: Facts) -> list[str]:
    """
    Binary gates. No weighting, no judgment. Either the posting excludes you or it does
    not. These run first because a weighted score on a role you cannot take is noise.
    """
    kills = []
    if f.remote_us is False:
        kills.append("not remote in the US")
    if _norm([f.work_mode]) & {"onsite", "hybrid"}:
        kills.append(f"work mode is {f.work_mode}")
    if f.excludes_ohio is True:
        kills.append("state restrictions exclude Ohio")
    if f.max_years_required is not None and f.max_years_required > MAX_YEARS_ACCEPTED:
        kills.append(f"requires {f.max_years_required} years, ceiling is {MAX_YEARS_ACCEPTED}")
    if f.degree_hard_required is True:
        kills.append("completed degree required with no equivalent clause")
    if _norm([f.seniority]) & {"senior", "lead"}:
        kills.append(f"seniority is {f.seniority}")
    return kills


def score(f: Facts) -> Decision:
    """Facts to decision. Every number that comes out of here shows its work."""

    if not f.source_complete:
        return Decision(verdict="incomplete", score=0.0,
                        reasons=["source text was incomplete, not scored"])

    kills = hard_kills(f)
    if kills:
        return Decision(verdict="kill", score=0.0, kills=kills)

    pts, reasons = 0.0, []

    if f.title_is_analyst:
        pts += WEIGHTS["title_is_analyst"]
        reasons.append(f"title is analyst-family (+{WEIGHTS['title_is_analyst']})")

    if _norm([f.seniority]) & {"entry", "intern", "not_stated"}:
        pts += WEIGHTS["seniority_ok"]
        reasons.append(f"seniority {f.seniority} is in range (+{WEIGHTS['seniority_ok']})")

    if f.max_years_required is not None and f.max_years_required <= MAX_YEARS_ACCEPTED:
        pts += WEIGHTS["years_ok"]
        reasons.append(f"{f.max_years_required} years required (+{WEIGHTS['years_ok']})")

    matched = _norm(f.stack_mentioned) & CORE_STACK
    if matched:
        frac = len(matched) / 4.0                       # 4 matches saturates the weight
        earned = round(min(frac, 1.0) * WEIGHTS["stack_overlap"], 2)
        pts += earned
        reasons.append(f"stack match {sorted(matched)} (+{earned})")

    if f.degree_hard_required is False:
        pts += WEIGHTS["no_degree_gate"]
        reasons.append(f"no hard degree gate (+{WEIGHTS['no_degree_gate']})")

    final = round(10.0 * pts / MAX_SCORE, 2)
    reasons.append(f"{pts} of {MAX_SCORE} weight = {final} of 10")
    return Decision(verdict="pass", score=final, reasons=reasons)
