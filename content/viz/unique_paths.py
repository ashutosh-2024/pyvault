"""Unique Paths (LC 62): four chapters, every number produced by running the
algorithm being shown."""
from math import comb

M, N = 3, 7            # the grid from LeetCode's example 1 (answer 28)
RM, RN = 3, 4          # smaller grid for the recursion chapter, so the call trace stays short


def _blank(rows, cols, value="", cls=""):
    return [[value] * cols for _ in range(rows)], [[cls] * cols for _ in range(rows)]


def _frame(caption, grid=None, cls=None, **extra):
    f = {"caption": caption}
    if grid is not None:
        f["grid"] = {"v": [row[:] for row in grid], "cls": [row[:] for row in cls]}
    f.update({k: v for k, v in extra.items() if v is not None})
    return f


# ---------------------------------------------------------------- chapter 1
def _chapter_question():
    frames = []
    v, c = _blank(M, N)
    v[0][0], c[0][0] = "S", "start"
    v[M - 1][N - 1], c[M - 1][N - 1] = "G", "goal"
    frames.append(_frame(
        f"A robot starts at the top-left of a {M} &times; {N} grid and wants the bottom-right. "
        "It may only move <strong>right</strong> or <strong>down</strong>. How many different routes are there?",
        v, c))

    routes = ["RRRRRRDD", "DDRRRRRR", "RRDRRRDR"]
    for k, moves in enumerate(routes, 1):
        r = col = 0
        path = [[0, 0]]
        for m in moves:
            r, col = (r + 1, col) if m == "D" else (r, col + 1)
            path.append([r, col])
        pv, pc = [row[:] for row in v], [row[:] for row in c]
        for pr, pcol in path[1:-1]:
            pc[pr][pcol] = "path"
        frames.append(_frame(
            f"Route {k}: <code>{' '.join(moves)}</code>. Every route makes exactly "
            f"{M - 1} downs and {N - 1} rights &mdash; only the order differs.",
            pv, pc, path=path))

    frames.append(_frame(
        f"Listing routes one by one does not scale: a 20 &times; 20 grid has {comb(38, 19):,} of them. "
        "We need to <strong>count</strong> them without walking each one.",
        v, c))
    return {"title": "The question", "frames": frames}


# ---------------------------------------------------------------- chapter 2
def _chapter_recursion():
    """Trace the plain recursion f(r, c) = f(r-1, c) + f(r, c-1) on a small grid."""
    calls = [[0] * RN for _ in range(RM)]
    stack, events = [], []

    def f(r, c):
        calls[r][c] += 1
        events.append(((r, c), [s for s in stack], [row[:] for row in calls]))
        if r == 0 or c == 0:
            return 1
        stack.append((r, c))
        out = f(r - 1, c) + f(r, c - 1)
        stack.pop()
        return out

    total = f(RM - 1, RN - 1)
    assert total == comb(RM + RN - 2, RM - 1)
    n_calls = len(events)
    assert n_calls == 2 * total - 1

    def heat(k):
        return "" if k == 0 else f"heat{min(5, k)}"

    frames = [_frame(
        f"The direct idea: the last move into a cell came from <strong>above</strong> or from the <strong>left</strong>, "
        f"so <code>f(r, c) = f(r-1, c) + f(r, c-1)</code>. Let&rsquo;s run that recursion on a smaller "
        f"{RM} &times; {RN} grid and count how often each cell gets computed.",
        *_blank(RM, RN, "", "empty"))]

    for (cell, on_stack, snapshot) in events:
        r, c = cell
        v = [[str(k) if k else "" for k in row] for row in snapshot]
        cl = [[heat(k) for k in row] for row in snapshot]
        for sr, sc in on_stack:
            cl[sr][sc] = "stack"
        cl[r][c] = "cur"
        base = r == 0 or c == 0
        what = "base case: returns 1" if base else "not a base case: calls above and left"
        frames.append(_frame(
            f"Call <code>f({r}, {c})</code> &mdash; {what}. "
            f"This cell has now been computed <strong>{snapshot[r][c]}</strong> time{'s' if snapshot[r][c] > 1 else ''}.",
            v, cl, formula=f"calls so far: {sum(map(sum, snapshot))}"))

    worst = max((calls[r][c], (r, c)) for r in range(RM) for c in range(RN))
    v = [[str(k) if k else "" for k in row] for row in calls]
    cl = [[heat(k) for k in row] for row in calls]
    frames.append(_frame(
        f"Done: <strong>{n_calls} calls</strong> to count {total} routes on a grid of only {RM * RN} cells. "
        f"Cell {worst[1]} was computed {worst[0]} times. The same sub-answers are recomputed over and over, "
        "and on bigger grids the call count grows exponentially. Fix: compute each cell <strong>once</strong>.",
        v, cl, formula=f"{n_calls} calls vs {RM * RN} cells"))
    return {"title": "Why plain recursion is slow", "frames": frames}


# ---------------------------------------------------------------- chapter 3
def _chapter_table():
    dp = [[None] * N for _ in range(M)]
    frames = [_frame(
        f"Build a table where <code>dp[r][c]</code> = number of routes from the start to cell (r, c). "
        "Fill it so that whenever we compute a cell, the cells it needs are already done.",
        *_blank(M, N, "", "empty"))]

    for r in range(M):
        for c in range(N):
            if r == 0 or c == 0:
                dp[r][c] = 1

    def snapshot():
        v = [["" if x is None else str(x) for x in row] for row in dp]
        cl = [["empty" if x is None else ("base" if (r == 0 or c == 0) else "done")
               for c, x in enumerate(row)] for r, row in enumerate(dp)]
        return v, cl

    frames.append(_frame(
        "Base cases: every cell in the <strong>top row</strong> can only be reached by going right, "
        "and every cell in the <strong>left column</strong> only by going down. Exactly one route each.",
        *snapshot(), formula="dp[0][c] = 1,  dp[r][0] = 1"))

    for r in range(1, M):
        for c in range(1, N):
            above, left = dp[r - 1][c], dp[r][c - 1]
            dp[r][c] = above + left
            v, cl = snapshot()
            cl[r][c] = "cur"
            cl[r - 1][c] = "src"
            cl[r][c - 1] = "src"
            frames.append(_frame(
                f"Cell ({r}, {c}): routes arriving from above ({above}) plus routes arriving from the left ({left}). "
                "They end with different moves, so none is counted twice.",
                v, cl, arrows=[[r - 1, c, r, c], [r, c - 1, r, c]],
                formula=f"dp[{r}][{c}] = dp[{r-1}][{c}] + dp[{r}][{c-1}] = {above} + {left} = {dp[r][c]}"))

    assert dp[M - 1][N - 1] == comb(M + N - 2, M - 1)
    v, cl = snapshot()
    cl[M - 1][N - 1] = "answer"
    frames.append(_frame(
        f"The bottom-right cell holds the answer: <strong>{dp[M - 1][N - 1]} routes</strong>. "
        f"Each of the {M * N} cells was computed once, so the work is O(m&middot;n) instead of exponential.",
        v, cl, formula=f"answer = dp[{M-1}][{N-1}] = {dp[M - 1][N - 1]}"))
    return {"title": "Fill the table", "frames": frames}


# ---------------------------------------------------------------- chapter 4
def _chapter_one_row():
    row = [1] * N
    done_rows = [[1] * N]                       # rows already finished (for the faded grid)

    def grid(r, upto):
        """finished rows faded; row r shows the values written so far (up to column `upto`)"""
        v, cl = _blank(M, N, "", "empty")
        for rr, values in enumerate(done_rows):
            for c, x in enumerate(values):
                v[rr][c], cl[rr][c] = str(x), "dim"
        if r < M:
            for c in range(upto + 1):
                v[r][c], cl[r][c] = str(row[c]), "done"
            if upto > 0:
                cl[r][upto] = "cur"
        return v, cl

    def arr(cls_at=None):
        cls = ["done"] * N
        for i, k in (cls_at or {}).items():
            cls[i] = k
        return {"label": "row", "v": [str(x) for x in row], "cls": cls}

    frames = [_frame(
        "Look at what each cell reads: the cell <strong>above</strong> and the cell to the <strong>left</strong>. "
        "Rows older than the previous one are never read again &mdash; so keep just one row of numbers.",
        *grid(M, 0), array=arr())]

    for r in range(1, M):
        for c in range(1, N):
            old = row[c]
            row[c] += row[c - 1]
            v, cl = grid(r, c)
            frames.append(_frame(
                f"Row {r}, column {c}: before the update <code>row[{c}]</code> still holds the value from the row above "
                f"({old}); <code>row[{c - 1}]</code> was just updated, so it is the cell to the left ({row[c - 1]}).",
                v, cl, array=arr({c: "cur", c - 1: "src"}),
                formula=f"row[{c}] += row[{c-1}]   ->   {old} + {row[c - 1]} = {row[c]}"))
        done_rows.append(row[:])

    assert row[-1] == comb(M + N - 2, M - 1)
    v, cl = grid(M, 0)
    frames.append(_frame(
        f"Same answer, <strong>{row[-1]}</strong>, using {N} numbers of memory instead of {M * N}. "
        "That single line, <code>row[c] += row[c-1]</code>, is the whole optimised solution.",
        v, cl, array=arr({N - 1: "answer"}), formula=f"answer = row[-1] = {row[-1]}"))
    return {"title": "Shrink to one row", "frames": frames}


def build():
    return {"chapters": [_chapter_question(), _chapter_recursion(), _chapter_table(), _chapter_one_row()]}
