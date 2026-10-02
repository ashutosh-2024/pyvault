"""Animations for the grid DP problems (Unique Paths itself lives in unique_paths.py)."""
from math import inf
from ._kit import Board, Story, fmt


def _input_board(grid, label_cls=""):
    b = Board(len(grid), len(grid[0]), cls=label_cls)
    for r, row in enumerate(grid):
        b.row(r, row)
    return b


# ------------------------------------------------------------------ Unique Paths II
def unique_paths_ii():
    g = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0]]
    R, C = len(g), len(g[0])
    s = Story()
    ch = s.chapter("The question")
    b = Board(R, C, cls="")
    for r in range(R):
        for c in range(C):
            if g[r][c]:
                b.set(r, c, "X", "wall")
    b.set(0, 0, "S", "start").set(R - 1, C - 1, "G", "goal")
    ch.add(b.frame("Same robot, same right/down moves, but some cells are <strong>blocked</strong>. "
                   "How many routes avoid every obstacle?"))

    ch = s.chapter("Fill the table")
    dp = [[0] * C for _ in range(R)]
    b = Board(R, C)
    for r in range(R):
        for c in range(C):
            if g[r][c]:
                b.set(r, c, 0, "wall")
    ch.add(b.frame("An obstacle cell can be reached in <strong>0</strong> ways, which automatically cuts off every route through it."))
    for r in range(R):
        for c in range(C):
            if g[r][c]:
                continue
            if r == 0 and c == 0:
                dp[0][0] = 1
                b.set(0, 0, 1, "base")
                ch.add(b.frame("The start can be reached in exactly one way.", formula="dp[0][0] = 1", marks={(0, 0): "cur"}))
                continue
            up = dp[r - 1][c] if r else 0
            left = dp[r][c - 1] if c else 0
            dp[r][c] = up + left
            b.set(r, c, dp[r][c], "done")
            marks, arrows = {(r, c): "cur"}, []
            if r: marks[(r - 1, c)] = "src"; arrows.append((r - 1, c, r, c))
            if c: marks[(r, c - 1)] = "src"; arrows.append((r, c - 1, r, c))
            note = " (an obstacle contributes 0)" if (r and g[r - 1][c]) or (c and g[r][c - 1]) else ""
            ch.add(b.frame(f"Cell ({r}, {c}): routes from above + routes from the left{note}.",
                           formula=f"dp[{r}][{c}] = {up} + {left} = {dp[r][c]}", marks=marks, arrows=arrows))
    ch.add(b.frame(f"<strong>{dp[R-1][C-1]}</strong> obstacle-free routes. Each obstacle stays 0, so every neighbour that reads "
                   "it simply gets nothing from that side &mdash; no special-case code beyond <code>if blocked: 0</code>.",
                   formula=f"answer = {dp[R-1][C-1]}", marks={(R - 1, C - 1): "answer"}))
    return s.build()


# ------------------------------------------------------------------ min-cost path helpers
def _path_back(R, C, dp, prev):
    path, cell = [], (R - 1, C - 1)
    while cell is not None:
        path.append(cell)
        cell = prev.get(cell)
    return path[::-1]


def minimum_path_sum():
    g = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]
    R, C = len(g), len(g[0])
    s = Story()
    ch = s.chapter("The question")
    ch.add(_input_board(g).frame("Each cell has a cost. Moving only right or down, find the cheapest route from top-left "
                                 "to bottom-right (the route pays every cell it visits, both ends included)."))
    ch = s.chapter("Fill the table")
    dp = [[None] * C for _ in range(R)]
    prev = {}
    b = Board(R, C)
    for r in range(R):
        for c in range(C):
            cands = []
            if r: cands.append(((r - 1, c), dp[r - 1][c]))
            if c: cands.append(((r, c - 1), dp[r][c - 1]))
            if not cands:
                dp[r][c] = g[r][c]
                b.set(r, c, dp[r][c], "base")
                ch.add(b.frame(f"The start costs its own value, {g[r][c]}.", formula=f"dp[0][0] = {g[0][0]}",
                               marks={(0, 0): "cur"}))
                continue
            (src, val) = min(cands, key=lambda x: x[1])
            dp[r][c] = g[r][c] + val
            prev[(r, c)] = src
            b.set(r, c, dp[r][c], "done")
            marks = {(r, c): "cur"}
            for (pr, pc), _ in cands:
                marks[(pr, pc)] = "src"
            which = "above" if src == (r - 1, c) else "the left"
            ch.add(b.frame(f"Cell ({r}, {c}) costs {g[r][c]}. Arrive from the cheaper neighbour: {which} ({val}).",
                           formula=f"dp[{r}][{c}] = {g[r][c]} + min(" + ", ".join(str(v) for _, v in cands) + f") = {dp[r][c]}",
                           marks=marks, arrows=[(src[0], src[1], r, c)]))
    path = _path_back(R, C, dp, prev)
    ch.add(b.frame(f"Cheapest total <strong>{dp[R-1][C-1]}</strong>. Following the arrows back from the corner gives the route "
                   f"{' &rarr; '.join(str(g[r][c]) for r, c in path)}.",
                   formula=f"answer = {dp[R-1][C-1]}", marks={p: "chosen" for p in path}, path=path))
    return s.build()


def minimum_falling_path_sum():
    g = [[2, 1, 3], [6, 5, 4], [7, 8, 9]]
    n = len(g)
    s = Story()
    ch = s.chapter("The question")
    ch.add(_input_board(g).frame("A falling path starts anywhere in the top row and moves down one row at a time, to the "
                                 "cell directly below or diagonally below. Find the smallest sum."))
    ch = s.chapter("Fill row by row")
    dp = [row[:] for row in g]
    prev = {}
    b = Board(n, n)
    b.row(0, g[0], "base")
    ch.add(b.frame("A path can start at any cell of the top row, so row 0 is its own cost.", formula="dp[0] = row 0"))
    for r in range(1, n):
        for c in range(n):
            cands = [(c + d, dp[r - 1][c + d]) for d in (-1, 0, 1) if 0 <= c + d < n]
            pc, val = min(cands, key=lambda x: x[1])
            dp[r][c] = g[r][c] + val
            prev[(r, c)] = (r - 1, pc)
            b.set(r, c, dp[r][c], "done")
            marks = {(r, c): "cur"}
            for cc, _ in cands:
                marks[(r - 1, cc)] = "src"
            ch.add(b.frame(f"Cell ({r}, {c}) costs {g[r][c]}; the cheapest of the {len(cands)} cells above it is {val}.",
                           formula=f"dp[{r}][{c}] = {g[r][c]} + min(" + ", ".join(str(v) for _, v in cands) + f") = {dp[r][c]}",
                           marks=marks, arrows=[(r - 1, cc, r, c) for cc, _ in cands]))
    end = min(range(n), key=lambda c: dp[n - 1][c])
    path, cell = [], (n - 1, end)
    while cell:
        path.append(cell); cell = prev.get(cell)
    path.reverse()
    ch.add(b.frame(f"The answer is the smallest value in the last row: <strong>{dp[n-1][end]}</strong>, along "
                   f"{' &rarr; '.join(str(g[r][c]) for r, c in path)}.",
                   formula=f"answer = min(dp[{n-1}]) = {dp[n-1][end]}", marks={p: "chosen" for p in path}, path=path))
    return s.build()


# ------------------------------------------------------------------ Triangle
def triangle():
    tri = [[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]
    n = len(tri)
    s = Story()

    def board():
        b = Board(n, n)
        for r in range(n):
            for c in range(n):
                if c > r:
                    b.set(r, c, "", "none")
        return b

    ch = s.chapter("The question")
    b = board()
    for r, row in enumerate(tri):
        for c, x in enumerate(row):
            b.set(r, c, x, "")
    ch.add(b.frame("Go from the top of the triangle to the bottom row. From position c you may step to c or c + 1 in the "
                   "row below. Find the smallest sum. (Rows are drawn left-aligned.)"))

    ch = s.chapter("Bottom-up")
    dp = [row[:] for row in tri]
    b = board()
    for c, x in enumerate(tri[-1]):
        b.set(n - 1, c, x, "base")
    ch.add(b.frame("Work <strong>upwards</strong>: from the bottom row the best path from a cell is just the cell itself.",
                   formula="dp[last row] = last row"))
    choice = {}
    for r in range(n - 2, -1, -1):
        for c in range(r + 1):
            down, diag = dp[r + 1][c], dp[r + 1][c + 1]
            pick = c if down <= diag else c + 1
            dp[r][c] = tri[r][c] + min(down, diag)
            choice[(r, c)] = (r + 1, pick)
            b.set(r, c, dp[r][c], "done")
            ch.add(b.frame(f"Cell ({r}, {c}) = {tri[r][c]} plus the better of the two cells below it ({down} and {diag}).",
                           formula=f"dp[{r}][{c}] = {tri[r][c]} + min({down}, {diag}) = {dp[r][c]}",
                           marks={(r, c): "cur", (r + 1, c): "src", (r + 1, c + 1): "src"},
                           arrows=[(r + 1, c, r, c), (r + 1, c + 1, r, c)]))
    path, cell = [(0, 0)], (0, 0)
    while cell in choice:
        cell = choice[cell]; path.append(cell)
    ch.add(b.frame(f"The apex holds the answer, <strong>{dp[0][0]}</strong>: "
                   f"{' + '.join(str(tri[r][c]) for r, c in path)}. Going bottom-up means no special cases at the edges.",
                   formula=f"answer = dp[0][0] = {dp[0][0]}", marks={p: "chosen" for p in path}, path=path))
    return s.build()


# ------------------------------------------------------------------ Dungeon game
def dungeon_game():
    d = [[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]
    R, C = len(d), len(d[0])
    s = Story()
    ch = s.chapter("The question")
    ch.add(_input_board(d).frame("A knight starts top-left and must reach the princess bottom-right, moving right or down. "
                                 "Negative rooms hurt, positive rooms heal, and health must never drop to 0. "
                                 "What is the <strong>minimum starting health</strong>?"))
    ch.add(_input_board(d).frame("Going forwards does not work: the best health so far does not tell you whether you can survive "
                                 "the rooms still ahead. Instead ask, for each room: <em>how much health do I need on entering it?</em> "
                                 "That depends only on rooms <strong>after</strong> it, so fill from the bottom-right."))
    ch = s.chapter("Fill backwards")
    need = [[None] * C for _ in range(R)]
    b = Board(R, C)
    for r in range(R - 1, -1, -1):
        for c in range(C - 1, -1, -1):
            nxt = []
            if r + 1 < R: nxt.append(((r + 1, c), need[r + 1][c]))
            if c + 1 < C: nxt.append(((r, c + 1), need[r][c + 1]))
            after = min(v for _, v in nxt) if nxt else 1
            need[r][c] = max(1, after - d[r][c])
            b.set(r, c, need[r][c], "base" if not nxt else "done")
            marks = {(r, c): "cur"}
            for p, _ in nxt:
                marks[p] = "src"
            what = ("Last room: you must leave it with at least 1 health" if not nxt
                    else f"Next you need {after} (the cheaper of {' and '.join(str(v) for _, v in nxt)})")
            ch.add(b.frame(f"Room ({r}, {c}) changes health by {d[r][c]:+d}. {what}, so enter with at least "
                           f"max(1, {after} &minus; ({d[r][c]})) = {need[r][c]}.",
                           formula=f"need[{r}][{c}] = max(1, {after} - ({d[r][c]})) = {need[r][c]}",
                           marks=marks, arrows=[(p[0], p[1], r, c) for p, v in nxt if v == after]))
    ch.add(b.frame(f"The knight needs <strong>{need[0][0]}</strong> health at the start. The <code>max(1, &hellip;)</code> matters: "
                   "a healing room cannot make up for having died before reaching it.",
                   formula=f"answer = need[0][0] = {need[0][0]}", marks={(0, 0): "answer"}))
    return s.build()


# ------------------------------------------------------------------ squares
def _square_table(s, mat, total_mode):
    R, C = len(mat), len(mat[0])
    ch = s.chapter("The question")
    ch.add(_input_board(mat).frame(
        "Count all square submatrices made only of 1s." if total_mode else
        "Find the largest square made only of 1s, and return its area."))
    ch = s.chapter("Fill the table")
    dp = [[0] * C for _ in range(R)]
    b = Board(R, C)
    total, best, best_at = 0, 0, None
    for r in range(R):
        for c in range(C):
            if mat[r][c] == 0:
                b.set(r, c, 0, "no")
                ch.add(b.frame(f"Cell ({r}, {c}) is 0: no square can end here.", formula=f"dp[{r}][{c}] = 0",
                               marks={(r, c): "cur"}))
                continue
            if r == 0 or c == 0:
                dp[r][c] = 1
                b.set(r, c, 1, "base")
                total += 1
                if 1 > best: best, best_at = 1, (r, c)
                ch.add(b.frame(f"Cell ({r}, {c}) is a 1 on the edge: only a 1&times;1 square can end here.",
                               formula=f"dp[{r}][{c}] = 1" + (f";  total = {total}" if total_mode else ""),
                               marks={(r, c): "cur"}))
                continue
            up, left, diag = dp[r - 1][c], dp[r][c - 1], dp[r - 1][c - 1]
            dp[r][c] = 1 + min(up, left, diag)
            total += dp[r][c]
            if dp[r][c] > best: best, best_at = dp[r][c], (r, c)
            b.set(r, c, dp[r][c], "done")
            ch.add(b.frame(f"Cell ({r}, {c}): a square ending here is limited by the smallest square ending above ({up}), "
                           f"left ({left}) and diagonally ({diag})." +
                           (f" It adds {dp[r][c]} squares (sizes 1..{dp[r][c]})." if total_mode else ""),
                           formula=f"dp[{r}][{c}] = 1 + min({up}, {left}, {diag}) = {dp[r][c]}" +
                                   (f";  total = {total}" if total_mode else ""),
                           marks={(r, c): "cur", (r - 1, c): "src", (r, c - 1): "src", (r - 1, c - 1): "src"},
                           arrows=[(r - 1, c, r, c), (r, c - 1, r, c), (r - 1, c - 1, r, c)]))
    if total_mode:
        ch.add(b.frame(f"<strong>{total}</strong> squares in total: each cell contributes the size of the largest square "
                       "ending there, because every smaller size ends there too.", formula=f"answer = sum(dp) = {total}"))
    else:
        r0, c0 = best_at
        marks = {(r, c): "chosen" for r in range(r0 - best + 1, r0 + 1) for c in range(c0 - best + 1, c0 + 1)}
        marks[best_at] = "answer"
        ch.add(b.frame(f"The largest value is <strong>{best}</strong>, at ({r0}, {c0}): a {best}&times;{best} square ends there, "
                       f"so the area is {best * best}.", formula=f"answer = {best}^2 = {best * best}", marks=marks))
    return s.build()


def maximal_square():
    mat = [[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]
    return _square_table(Story(), mat, total_mode=False)


def count_square_submatrices():
    mat = [[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]
    return _square_table(Story(), mat, total_mode=True)


# ------------------------------------------------------------------ Longest increasing path
def longest_increasing_path_in_a_matrix():
    g = [[9, 9, 4], [6, 6, 8], [2, 1, 1]]
    R, C = len(g), len(g[0])
    s = Story()
    ch = s.chapter("The question")
    ch.add(_input_board(g).frame("Find the longest path of <strong>strictly increasing</strong> values, moving up, down, left "
                                 "or right. There is no fixed fill order: a cell depends on whichever neighbours are larger."))
    ch.add(_input_board(g).frame("But moves only go to larger values, so a path can never loop back. That means memoised DFS "
                                 "works: <code>len(cell) = 1 + max(len(larger neighbour))</code>, computed once per cell."))
    ch = s.chapter("Memoised DFS")
    memo = {}
    b = Board(R, C)
    for r in range(R):
        for c in range(C):
            b.set(r, c, g[r][c], "")
    frames = []

    def nbrs(r, c):
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and g[nr][nc] > g[r][c]:
                yield nr, nc

    def dfs(r, c):
        if (r, c) in memo:
            return memo[(r, c)]
        best, src = 1, []
        for nr, nc in nbrs(r, c):
            v = 1 + dfs(nr, nc)
            if v > best:
                best = v
            src.append((nr, nc))
        memo[(r, c)] = best
        b.set(r, c, best, "done")
        ch.add(b.frame(f"Cell ({r}, {c}) with value {g[r][c]}: " +
                       (f"larger neighbours already solved ({', '.join(str(memo[p]) for p in src)}); take the longest + 1."
                        if src else "no larger neighbour, so the path starting here has length 1."),
                       formula=f"len({r},{c}) = {best}",
                       marks={**{p: "src" for p in src}, (r, c): "cur"},
                       arrows=[(p[0], p[1], r, c) for p in src]))
        return best

    for r in range(R):
        for c in range(C):
            dfs(r, c)
    start = max(memo, key=lambda p: memo[p])
    path, cell = [start], start
    while True:
        nxt = [p for p in nbrs(*cell) if memo[p] == memo[cell] - 1]
        if not nxt:
            break
        cell = nxt[0]; path.append(cell)
    ch.add(b.frame(f"Longest increasing path has length <strong>{memo[start]}</strong>: "
                   f"{' &rarr; '.join(str(g[r][c]) for r, c in path)}. Each cell was solved exactly once.",
                   formula=f"answer = {memo[start]}", marks={p: "chosen" for p in path}, path=path))
    return s.build()


BUILDERS = {
    "unique-paths-ii": unique_paths_ii,
    "minimum-path-sum": minimum_path_sum,
    "triangle": triangle,
    "dungeon-game": dungeon_game,
    "minimum-falling-path-sum": minimum_falling_path_sum,
    "maximal-square": maximal_square,
    "count-square-submatrices": count_square_submatrices,
    "longest-increasing-path-in-a-matrix": longest_increasing_path_in_a_matrix,
}
