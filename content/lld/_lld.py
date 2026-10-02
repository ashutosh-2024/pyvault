"""Helpers for the Low-Level Design section.

Pattern guides are ordinary long-form topics (see deepdive/_blocks.py) with
group="Patterns". Design problems are built with `problem()`, which gives every
one the same shape, in the order you would work through it in an interview:

  Requirements            what to build, what is out of scope
  Choosing the patterns   signal in the problem -> pattern -> why it fits
  Class design            each class and its single responsibility
  Implementation          the complete code, executed by build.py with a demo
  Extending the design    the follow-up change, and how the design absorbs it

Every code block is executed; its output is shown under it.
"""
from deepdive._blocks import code, table, note, caveat, section, question

PATTERNS_GROUP = "Patterns"
PROBLEMS_GROUP = "Design problems"


def problem(id, title, level, patterns, summary, statement, requirements,
            choose, classes, implementation, extend=(), questions=(), refs=(),
            choose_notes=()):
    """Build a design-problem topic.

    choose:   rows of (signal in the problem, pattern, why it fits)
    classes:  rows of (class, responsibility)
    the rest: lists of blocks (strings, code(...), table(...), note(...))
    """
    sections = [
        section("Requirements", *requirements),
        section("Choosing the patterns",
                table(["Signal in the problem", "Pattern", "Why it fits"], choose),
                *choose_notes),
        section("Class design", table(["Class", "Responsibility"], classes)),
        section("Implementation", *implementation),
    ]
    if extend:
        sections.append(section("Extending the design", *extend))
    return dict(
        id=id,
        title=title,
        group=PROBLEMS_GROUP,
        level=level,
        tags=list(patterns),
        summary=summary,
        intro=list(statement),
        sections=sections,
        questions=list(questions),
        refs=list(refs),
    )


__all__ = ["code", "table", "note", "caveat", "section", "question", "problem",
           "PATTERNS_GROUP", "PROBLEMS_GROUP"]
