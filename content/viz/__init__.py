"""Step-by-step animations for DSA problems.

Each module here defines `build()` returning a viz dict for one problem; the
registry below maps problem id -> module. build.py calls it, validates the
result and ships it as `viz` on the problem. Frames are produced by actually
running the algorithm (with tracing), never typed by hand, so what the reader
watches is what the code does.

Schema
------
viz:      {"chapters": [chapter, ...]}
chapter:  {"title": str, "frames": [frame, ...]}
frame:    {
  "caption": html (code/strong/em/sub/sup allowed),
  "formula": str (optional, shown in mono),
  "grid":    {"v": [[str]], "cls": [[str]], "rowLabels"?: [str], "colLabels"?: [str]}  (optional)
  "array":   {"label": str, "v": [str], "cls": [str]}                                  (optional)
  "arrows":  [[r1, c1, r2, c2], ...]   grid cell -> grid cell                            (optional)
  "path":    [[r, c], ...]             polyline through grid cells                        (optional)
}
Cell classes: see CELL_CLASSES. The renderer (assets/js/viz.js) maps each to a style.
"""
from . import unique_paths, linear, knapsack, grid, lis, strings, interval

CELL_CLASSES = {
    "",          # plain
    "empty",     # not computed yet
    "base",      # base case
    "cur",       # being computed now
    "src",       # read to compute the current cell
    "done",      # computed
    "dim",       # no longer needed
    "path",      # on the highlighted path
    "start", "goal", "answer",
    "stack",     # on the recursion stack
    "heat1", "heat2", "heat3", "heat4", "heat5",   # repeated work, light -> heavy
    "none",      # not part of the shape (ragged triangle)
    "wall",      # obstacle
    "yes", "no", # boolean tables
    "chosen",    # part of the reconstructed answer
}

REGISTRY = {
    "unique-paths": unique_paths.build,
    **linear.BUILDERS,
    **knapsack.BUILDERS,
    **grid.BUILDERS,
    **lis.BUILDERS,
    **strings.BUILDERS,
    **interval.BUILDERS,
}

# Every problem in these DSA topics must have an animation; build.py enforces it.
# Problems without a hand-written one above get one traced by auto.py.
REQUIRED_TOPICS = {"dp", "trees", "heap", "backtracking", "hashing", "sorting", "sliding-window",
                   "monotonic-stack", "binary-search", "linked-lists", "trie", "union-find", "bits",
                   "greedy", "math", "graphs", "range-query", "string-algorithms"}
