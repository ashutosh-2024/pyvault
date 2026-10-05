"""Detailed write-ups for every DSA approach, one module per topic.

Each module defines EXPLAIN = {problem_id: entry}:

    entry = {
        "example": {                       # one input shared by all approaches
            "setup": "c = LRUCache(2)",    # optional statements run first
            "call": "daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])",
            "expect": "[1, 1, 4, 2, 1, 1, 0, 0]",
        },
        "approaches": {
            "<approach name exactly as in content/>": {
                "idea":  [str, ...],   # the intuition and the key insight
                "steps": [str, ...],   # the algorithm, in order
                "why":   [str, ...],   # why it is correct, where the cost comes from
                "dry":   [str, ...],   # a dry run of this approach on the example
            },
        },
    }

Every pointer is one or two sentences of inline HTML (code/strong/em/sub/sup).
build.py runs each approach on the example and fails if it does not return
`expect`, so the dry run's conclusion is checked like everything else.
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

PARTS = ("idea", "steps", "why", "dry")
