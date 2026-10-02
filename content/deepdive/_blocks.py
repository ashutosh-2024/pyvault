"""Building blocks for Python Deep Dive topics.

A topic is prose plus runnable code. Every `code(...)` block is executed by
build.py in its own subprocess and the captured output is shipped next to it,
so no output on a Deep Dive page is written by hand.

Schema
------
topic:    id, title, intro (paragraphs), sections[], questions[], refs?
section:  title, body (blocks)
question: q, level ("medium" | "hard"), answer (blocks)

A block is one of:
  "a paragraph"        plain string, inline <code>/<strong>/<em> allowed
  code(src, ...)       executed; output captured
  table(head, rows)    comparison grid, cells may hold inline HTML
  note(text)           the rule of thumb to walk away with
  caveat(text)         a CPython implementation detail, not a guarantee
"""
from textwrap import dedent


def code(src, label=None, raises=False, run=True):
    """raises=True when the snippet is meant to end in a traceback.
    run=False only for snippets that cannot run standalone (none should)."""
    return {"type": "code", "src": dedent(src).strip("\n"),
            "label": label, "raises": raises, "run": run}


def table(head, rows):
    return {"type": "table", "head": list(head), "rows": [list(r) for r in rows]}


def note(text):
    return {"type": "note", "text": text}


def caveat(text):
    return {"type": "caveat", "text": text}


def section(title, *body):
    return {"title": title, "body": list(body)}


def question(q, level, *answer):
    return {"q": q, "level": level, "answer": list(answer)}
