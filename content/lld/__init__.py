"""Low-Level Design: pattern guides first, then design problems.
See _lld.py for the problem schema."""
from . import (approach, solid, creational, structural, behavioral_core, behavioral_more,
               problems_classic, problems_booking, problems_games, problems_infra,
               problems_apps, problems_dev)

PATTERN_TOPICS = [
    approach.TOPIC,
    solid.TOPIC,
    creational.TOPIC,
    structural.TOPIC,
    behavioral_core.TOPIC,
    behavioral_more.TOPIC,
]

PROBLEMS = (problems_classic.PROBLEMS + problems_booking.PROBLEMS + problems_games.PROBLEMS
            + problems_infra.PROBLEMS + problems_apps.PROBLEMS + problems_dev.PROBLEMS)

TOPICS = PATTERN_TOPICS + PROBLEMS


def _practice_section():
    """Pattern -> problems that use it, generated from the problems' tags so it
    can never drift out of sync. Appended to the approach page."""
    from ._lld import section, table
    by_pattern = {}
    for p in PROBLEMS:
        for tag in p["tags"]:
            by_pattern.setdefault(tag, []).append(p["title"].removeprefix("Design ").removeprefix("a ").removeprefix("an "))
    rows = [[f"<strong>{tag}</strong>", str(len(titles)), ", ".join(titles)]
            for tag, titles in sorted(by_pattern.items(), key=lambda kv: (-len(kv[1]), kv[0]))]
    return section(
        "Practise each pattern",
        f"The {len(PROBLEMS)} design problems in this section, grouped by the patterns their solutions use. "
        "Strategy and Observer dominate because most interview problems are about something that varies "
        "and something that reacts; use the filter on the section index to open them by pattern.",
        table(["Pattern", "Problems", "Where it appears"], rows),
    )


approach.TOPIC["sections"].append(_practice_section())
