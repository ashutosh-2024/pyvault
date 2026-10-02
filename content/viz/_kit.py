"""Small toolkit for writing animation generators.

    s = Story()
    ch = s.chapter("Fill the table")
    b = Board(rows, cols, row_labels=[...], col_labels=[...])
    b.set(r, c, value, "done")
    ch.add(b.frame("caption", formula="...", marks={(r, c): "cur"}, arrows=[(r1, c1, r, c)]))
    return s.build()

`marks` and `arrows` apply to that frame only; `set` changes the board for good.
`CallTrace` records a plain recursion so `heat_chapter` can show repeated work.
"""
from math import inf


def fmt(x):
    if x is None:
        return ""
    if x is True:
        return "T"
    if x is False:
        return "F"
    if x == inf:
        return "∞"
    if x == -inf:
        return "-∞"
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


class Board:
    def __init__(self, rows, cols, row_labels=None, col_labels=None, value="", cls="empty"):
        self.rows, self.cols = rows, cols
        self.v = [[value] * cols for _ in range(rows)]
        self.c = [[cls] * cols for _ in range(rows)]
        self.row_labels = [str(x) for x in row_labels] if row_labels is not None else None
        self.col_labels = [str(x) for x in col_labels] if col_labels is not None else None

    def set(self, r, c, value=None, cls=None):
        if value is not None:
            self.v[r][c] = fmt(value)
        if cls is not None:
            self.c[r][c] = cls
        return self

    def row(self, r, values, cls=None):
        for c, x in enumerate(values):
            self.set(r, c, x, cls)
        return self

    def fill_cls(self, cls, where=None):
        for r in range(self.rows):
            for c in range(self.cols):
                if where is None or where(r, c):
                    self.c[r][c] = cls
        return self

    def frame(self, caption, formula=None, marks=None, arrows=None, path=None, array=None):
        v = [row[:] for row in self.v]
        c = [row[:] for row in self.c]
        for (r, cc), k in (marks or {}).items():
            c[r][cc] = k
        grid = {"v": v, "cls": c}
        if self.row_labels:
            grid["rowLabels"] = self.row_labels
        if self.col_labels:
            grid["colLabels"] = self.col_labels
        f = {"caption": caption, "grid": grid}
        if formula:
            f["formula"] = formula
        if arrows:
            f["arrows"] = [list(a) for a in arrows if a[:2] != a[2:]]
        if path:
            f["path"] = [list(p) for p in path]
        if array:
            f["array"] = array
        return f


class Chapter:
    def __init__(self, title):
        self.title, self.frames = title, []

    def add(self, frame):
        self.frames.append(frame)
        return frame


class Story:
    def __init__(self):
        self.chapters = []

    def chapter(self, title):
        ch = Chapter(title)
        self.chapters.append(ch)
        return ch

    def build(self):
        return {"chapters": [{"title": c.title, "frames": c.frames} for c in self.chapters if c.frames]}


class CallTrace:
    """Record calls of a plain recursion: wrap the body with `with t.call(key):`."""
    def __init__(self):
        self.events, self.stack, self.counts = [], [], {}

    def call(self, key):
        trace = self

        class _Ctx:
            def __enter__(self_):
                trace.counts[key] = trace.counts.get(key, 0) + 1
                trace.events.append((key, list(trace.stack), dict(trace.counts)))
                trace.stack.append(key)

            def __exit__(self_, *exc):
                trace.stack.pop()

        return _Ctx()


def heat(k):
    return "" if not k else f"heat{min(5, k)}"


def heat_chapter(story, title, trace, make_board, cell_of, intro, describe, outro, max_frames=60):
    """One frame per recorded call: the cell being computed, cells waiting on
    the stack, and how many times each cell has been computed so far."""
    ch = story.chapter(title)
    b = make_board()
    ch.add(b.frame(intro))
    events = trace.events
    step = max(1, -(-len(events) // max_frames))       # sample long traces evenly
    shown = events[::step]
    if shown[-1] is not events[-1]:
        shown.append(events[-1])
    for key, stack, counts in shown:
        b = make_board()
        for k2, n in counts.items():
            r, c = cell_of(k2)
            b.set(r, c, n, heat(n))
        marks = {cell_of(s): "stack" for s in stack}
        marks[cell_of(key)] = "cur"
        ch.add(b.frame(describe(key, counts[key]), formula=f"calls so far: {sum(counts.values())}", marks=marks))
    b = make_board()
    for k2, n in trace.counts.items():
        r, c = cell_of(k2)
        b.set(r, c, n, heat(n))
    ch.add(b.frame(outro(len(events), trace.counts), formula=f"{len(events)} calls vs {len(trace.counts)} distinct sub-problems"))
    return ch
