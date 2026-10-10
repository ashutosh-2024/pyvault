"""Detailed write-ups for every DSA approach, one module per topic.

Each module defines EXPLAIN = {problem_id: entry}:

    entry = {
        "examples": [                      # worked examples, every approach dry-runs each
            {"setup": "c = LRUCache(2)",   # optional statements run first
             "call": "daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])",
             "expect": "[1, 1, 4, 2, 1, 1, 0, 0]"},
            {...},                         # at least two
        ],
        "approaches": {
            "<approach name exactly as in content/>": {
                "idea":  [str, ...],   # the intuition and the key insight
                "steps": [str, ...],   # the algorithm, in order
                "why":   [str, ...],   # why it is correct, where the cost comes from
                                       # (idea + steps + why: at least 8 pointers)
                "dry":   [[str, ...], [str, ...]],   # one dry run per worked example
                "faq":   [[question, answer], ...],  # at least 3 common doubts
            },
        },
    }

Every pointer is one or two sentences of inline HTML (code/strong/em/sub/sup).
build.py runs each approach on every worked example and fails if it does not
return `expect`, so each dry run's conclusion is checked like everything else.
The approach's animation is traced on the first worked example that fits in
one chapter, so it replays a dry run.
"""
import importlib
import pkgutil

EXPLAIN = {}
for _m in pkgutil.iter_modules(__path__):
    if _m.name.startswith("_"):
        continue
    _mod = importlib.import_module(f"{__name__}.{_m.name}")
    for _pid, _entry in _mod.EXPLAIN.items():
        if _pid in EXPLAIN:
            raise SystemExit(f"explain: {_pid} written up twice")
        EXPLAIN[_pid] = _entry

