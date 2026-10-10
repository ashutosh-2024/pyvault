"""Write-ups for Dynamic Programming, part 3: grid problems."""

EXPLAIN = {
    # ------------------------------------------------------------------ unique paths
    "unique-paths": {
        "examples": [
            {"call": "unique_paths(3, 4)", "expect": "10"},
            {"call": "unique_paths(1, 5)", "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "The robot only moves right or down, so the <strong>last move</strong> into cell (r, c) came either from (r − 1, c) above or from (r, c − 1) on the left.",
                    "Those two groups of paths never overlap, so the count is their sum: <code>f(r, c) = f(r - 1, c) + f(r, c - 1)</code>.",
                    "A cell on the top row or the left column can only be reached by a straight line, so it has exactly one path.",
                ],
                "steps": [
                    "Define <code>f(r, c)</code> as the number of paths from (0, 0) to (r, c).",
                    "Base case: if <code>r == 0 or c == 0</code>, return 1.",
                    "Otherwise return <code>f(r - 1, c) + f(r, c - 1)</code>.",
                    "The answer is <code>f(m - 1, n - 1)</code>, the bottom-right corner.",
                ],
                "why": [
                    "Every path into (r, c) ends with exactly one of the two moves, so splitting on the last move counts each path once and only once.",
                    "Nothing is remembered, so each path is in effect walked separately: the call tree has one leaf per path, which grows like <strong>O(2<sup>m+n</sup>)</strong> time.",
                    "Each call steps one row up or one column left, so the recursion is at most m + n deep: <strong>O(m + n)</strong> stack space.",
                    "The same cell is solved again and again from different parents. That repeated work is what the memo step removes.",
                ],
                "dry": [
                    [
                        "m = 3, n = 4, so the call is f(2, 3).",
                        "f(2, 3) = f(1, 3) + f(2, 2). f(1, 3) = f(0, 3) + f(1, 2) and f(2, 2) = f(1, 2) + f(2, 1).",
                        "f(1, 2) is already computed twice here, and f(1, 1) is computed three times in total.",
                        "The leaves return 1 and add up to f(1, 3) = 4 and f(2, 2) = 6; 19 calls in all.",
                        "The result is 4 + 6 = <strong>10</strong>.",
                    ],
                    [
                        "m = 1, n = 5, so the call is f(0, 4).",
                        "r == 0 already, so the base case fires on the very first call.",
                        "A single row has only one route: four moves right.",
                        "It returns <strong>1</strong> after one call.",
                    ],
                ],
                "faq": [
                    ["Why is <code>r == 0 or c == 0</code> the base case and not just (0, 0)?",
                     "Every cell on the first row or column has exactly one path, so stopping there is correct and saves calls. Stopping only at (0, 0) would also need checks for stepping off the grid."],
                    ["Is the time really 2<sup>m+n</sup>?",
                     "That is an upper bound. The exact number of leaves is the answer itself, C(m + n − 2, m − 1), which is still exponential when m and n grow together."],
                    ["Why show this at all?",
                     "It states the recurrence in its purest form. Every later step keeps exactly this formula and only changes how the values are stored and reused."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> the same recursion, with <code>@cache</code> on <code>f</code>.",
                    "There are only m·n different (r, c) arguments, yet plain recursion makes far more calls than that. Caching means each cell is computed once and every later call is a lookup.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>, so results are stored by the key <code>(r, c)</code>.",
                    "Base case: <code>r == 0 or c == 0</code> returns 1, exactly as before.",
                    "Otherwise return <code>f(r - 1, c) + f(r, c - 1)</code>; if either value is cached, it comes back instantly.",
                    "Return <code>f(m - 1, n - 1)</code>.",
                ],
                "why": [
                    "The recurrence is unchanged, so the answer is the same. The cache only removes repeated work, it never changes a value.",
                    "Each of the m·n cells is computed once with O(1) work on top of two lookups: <strong>O(m·n)</strong> time.",
                    "The cache holds up to m·n entries and the stack is up to m + n deep, so space is <strong>O(m·n)</strong>.",
                    "The recursion still goes deep, which is the reason to move to a bottom-up table next.",
                ],
                "dry": [
                    [
                        "f(2, 3) dives to f(1, 3), then f(0, 3) = 1 and f(1, 2), which needs f(0, 2) = 1 and f(1, 1).",
                        "f(1, 1) = f(0, 1) + f(1, 0) = 2. Then f(1, 2) = 1 + 2 = 3 and f(1, 3) = 1 + 3 = 4.",
                        "f(2, 2) needs f(1, 2): cached, 3. Then f(2, 1) needs f(1, 1): cached, 2, plus f(2, 0) = 1, so f(2, 1) = 3.",
                        "f(2, 2) = 3 + 3 = 6. Only 11 cells were ever computed, against 19 calls before.",
                        "f(2, 3) = 4 + 6 = <strong>10</strong>.",
                    ],
                    [
                        "The call is f(0, 4).",
                        "r == 0, so it returns 1 and stores it in the cache.",
                        "Nothing else is ever computed: a single row needs no reuse at all.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["What does <code>@cache</code> key on?",
                     "On the arguments <code>(r, c)</code>. That is why the function must depend only on its arguments, which it does here: m and n are fixed for one call of <code>unique_paths</code>."],
                    ["Can the recursion depth still be a problem?",
                     "Yes. It is about m + n frames, so for grids in the thousands Python's default recursion limit of 1000 can be hit. The bottom-up versions avoid the stack completely."],
                    ["Is the cache shared between different calls of <code>unique_paths</code>?",
                     "No. <code>f</code> is defined inside the function, so each call builds a fresh cached function and the old one is thrown away."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> instead of recursing from the corner and caching, fill a table <code>dp</code> in an order where both inputs of every cell are already known.",
                    "Going row by row, left to right, guarantees the cell above and the cell to the left are filled before the current one.",
                    "Starting every cell at 1 handles the first row and first column for free, because the loops never touch them.",
                ],
                "steps": [
                    "Build <code>dp = [[1] * n for _ in range(m)]</code>.",
                    "Loop <code>r</code> from 1 to m − 1 and, inside, <code>c</code> from 1 to n − 1.",
                    "Set <code>dp[r][c] = dp[r - 1][c] + dp[r][c - 1]</code>.",
                    "Return <code>dp[m - 1][n - 1]</code>.",
                ],
                "why": [
                    "Each cell uses the same recurrence as the recursion, and the loop order makes sure its inputs are final when it is read.",
                    "Two nested loops over the grid do O(1) work per cell: <strong>O(m·n)</strong> time, with no recursion overhead or stack.",
                    "The table has m·n cells, so space is <strong>O(m·n)</strong>.",
                    "Row r only ever reads row r − 1 and itself, so keeping the whole table is wasteful: that is the next step.",
                ],
                "dry": [
                    [
                        "dp starts as three rows of [1, 1, 1, 1].",
                        "r = 1: dp[1][1] = 1 + 1 = 2, dp[1][2] = 1 + 2 = 3, dp[1][3] = 1 + 3 = 4. Row 1 is [1, 2, 3, 4].",
                        "r = 2: dp[2][1] = 2 + 1 = 3, dp[2][2] = 3 + 3 = 6, dp[2][3] = 4 + 6 = 10.",
                        "Row 2 is [1, 3, 6, 10].",
                        "It returns dp[2][3] = <strong>10</strong>.",
                    ],
                    [
                        "dp is one row [1, 1, 1, 1, 1].",
                        "<code>range(1, 1)</code> is empty, so the outer loop never runs.",
                        "The pre-filled 1 in the last cell is already the answer.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the loops start at 1?",
                     "Row 0 and column 0 are all 1 already, which is exactly their correct value. Starting at 1 also means <code>r - 1</code> and <code>c - 1</code> are never negative."],
                    ["Does the loop order matter?",
                     "Yes: any order that fills (r − 1, c) and (r, c − 1) before (r, c) works. Row-major or column-major both do; a reversed loop would read cells that are still the default 1."],
                    ["What does a cell mean in words?",
                     "<code>dp[r][c]</code> is the number of distinct right/down paths from the top-left corner to (r, c)."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> the table is cut down to two rows, <code>prev</code> (row r − 1) and <code>cur</code> (row r).",
                    "A cell only needs the value above it (in <code>prev</code>) and the value to its left (in <code>cur</code>), so older rows can be dropped.",
                ],
                "steps": [
                    "Start <code>prev = [1] * n</code>, which is row 0.",
                    "For each later row, build <code>cur = [1] * n</code>; its column 0 stays 1.",
                    "For <code>c</code> from 1 to n − 1, set <code>cur[c] = prev[c] + cur[c - 1]</code>.",
                    "After the row, set <code>prev = cur</code>.",
                    "Return <code>prev[-1]</code>, the last cell of the last row.",
                ],
                "why": [
                    "<code>prev[c]</code> is <code>dp[r - 1][c]</code> and <code>cur[c - 1]</code> is <code>dp[r][c - 1]</code>, so every value matches the 2-D table.",
                    "The work per cell is unchanged: <strong>O(m·n)</strong> time.",
                    "Only two rows of length n exist at a time: <strong>O(n)</strong> space.",
                    "Building a new <code>cur</code> each row is the price of keeping the old row intact. The one-row step shows it is not needed.",
                ],
                "dry": [
                    [
                        "prev = [1, 1, 1, 1].",
                        "Row 1: cur = [1, 1+1, 1+2, 1+3] = [1, 2, 3, 4]. prev = cur.",
                        "Row 2: cur[1] = 2 + 1 = 3, cur[2] = 3 + 3 = 6, cur[3] = 4 + 6 = 10.",
                        "prev = [1, 3, 6, 10].",
                        "It returns prev[-1] = <strong>10</strong>.",
                    ],
                    [
                        "prev = [1, 1, 1, 1, 1].",
                        "m = 1, so <code>range(1, 1)</code> is empty and no row is built.",
                        "prev is still row 0.",
                        "It returns prev[-1] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>prev = cur</code> and not <code>prev = cur[:]</code>?",
                     "A fresh <code>cur</code> list is created at the start of the next row, so nothing ever writes into the old one again. Sharing the reference is safe."],
                    ["Why keep rows of length n and not m?",
                     "Either works, since the problem is symmetric. Keeping the shorter side, <code>min(m, n)</code>, gives the smallest memory."],
                    ["Why not just keep the whole table?",
                     "For an answer only the last cell matters, and the rows above are dead once the next row is built. O(n) instead of O(m·n) matters on big grids."],
                ],
            },
            "One row": {
                "idea": [
                    "<strong>What changed:</strong> <code>prev</code> and <code>cur</code> are merged into a single list <code>row</code> that is updated in place.",
                    "Before <code>row[c]</code> is overwritten it still holds the value from the row above, and <code>row[c - 1]</code> was already updated to the current row: exactly the two numbers the recurrence needs.",
                ],
                "steps": [
                    "Start <code>row = [1] * n</code> (row 0).",
                    "Repeat m − 1 times, once per remaining row.",
                    "Sweep <code>c</code> from 1 to n − 1 and do <code>row[c] += row[c - 1]</code>.",
                    "Column 0 is never touched, so it stays 1 as it should.",
                    "Return <code>row[-1]</code>.",
                ],
                "why": [
                    "<code>row[c] += row[c - 1]</code> reads as <em>above (old row[c]) + left (new row[c - 1])</em>, the same recurrence as every earlier step.",
                    "The left-to-right sweep is what makes this correct: column c − 1 is already on the new row when column c is processed.",
                    "Time stays <strong>O(m·n)</strong>; space is one list, <strong>O(n)</strong>, with no new list per row.",
                ],
                "dry": [
                    [
                        "row = [1, 1, 1, 1].",
                        "Pass 1: row[1] = 1 + 1 = 2, row[2] = 1 + 2 = 3, row[3] = 1 + 3 = 4. row = [1, 2, 3, 4].",
                        "Pass 2: row[1] = 2 + 1 = 3, row[2] = 3 + 3 = 6, row[3] = 4 + 6 = 10.",
                        "row = [1, 3, 6, 10].",
                        "It returns <strong>10</strong>.",
                    ],
                    [
                        "row = [1, 1, 1, 1, 1].",
                        "m − 1 = 0, so no pass runs.",
                        "The last entry is still 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Would sweeping right to left also work?",
                     "No. Then <code>row[c - 1]</code> would still hold the old row's value, so each cell would add above + above-left, which is a different recurrence and gives wrong counts."],
                    ["Is this still O(n) space like Two rows?",
                     "Yes, asymptotically the same, but it uses one list instead of two and creates no new list per row."],
                    ["What does <code>row</code> hold halfway through a pass?",
                     "Columns 0..c − 1 belong to the current row and columns c..n − 1 still belong to the row above."],
                ],
            },
            "Binomial coefficient": {
                "idea": [
                    "<strong>What changed:</strong> no table at all. Every path is a sequence of exactly m − 1 down moves and n − 1 right moves.",
                    "A path is fixed by choosing which of the m + n − 2 moves are the downs, so the count is <code>C(m + n - 2, m - 1)</code>.",
                ],
                "steps": [
                    "Count the total moves: (m − 1) downs plus (n − 1) rights = m + n − 2.",
                    "Choose positions for the m − 1 down moves among them.",
                    "Return <code>comb(m + n - 2, m - 1)</code> from <code>math</code>.",
                    "This equals <code>comb(m + n - 2, n - 1)</code>; choosing the downs or the rights is the same thing.",
                ],
                "why": [
                    "Each choice of down positions gives one valid path and each path gives one choice, so this is a one-to-one count.",
                    "It agrees with the DP: the table is Pascal's triangle rotated, and <code>dp[r][c] = C(r + c, r)</code>.",
                    "<code>comb</code> does about min(m, n) multiplications and divisions: <strong>O(min(m, n))</strong> arithmetic steps and <strong>O(1)</strong> extra space (big integers grow, but the count of steps is what is quoted).",
                ],
                "dry": [
                    [
                        "m = 3, n = 4: 2 down moves and 3 right moves, 5 moves in all.",
                        "Choose 2 of the 5 positions for the downs: C(5, 2).",
                        "C(5, 2) = 5 · 4 / 2 = 10.",
                        "The result is <strong>10</strong>, matching the last cell of the DP table.",
                    ],
                    [
                        "m = 1, n = 5: 0 down moves and 4 right moves.",
                        "comb(4, 0) is the number of ways to choose nothing.",
                        "That is 1: the single straight path.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why m − 1 and not m?",
                     "A grid with m rows needs m − 1 down moves to go from row 0 to row m − 1. The same goes for columns and right moves."],
                    ["Does this survive obstacles?",
                     "No. Obstacles break the one-to-one mapping between paths and move sequences, which is why Unique Paths II uses the DP ladder instead."],
                    ["Can the result overflow?",
                     "Not in Python, since integers are unbounded. In fixed-width languages, compute the product step by step and divide as you go to keep values small."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ unique paths II
    "unique-paths-ii": {
        "examples": [
            {"call": "unique_paths_with_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]])", "expect": "2"},
            {"call": "unique_paths_with_obstacles([[0, 1], [1, 0]])", "expect": "0"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Same last-move split as Unique Paths: paths into (r, c) arrive from above or from the left, so <code>f(r, c) = f(r - 1, c) + f(r, c - 1)</code>.",
                    "An obstacle cell has <strong>zero</strong> paths into it, and so does any position off the grid. That one rule handles every blocked route.",
                    "Unlike Unique Paths, the first row and column are no longer always 1: an obstacle there blocks everything after it, so the only base case left is the start (0, 0).",
                ],
                "steps": [
                    "Define <code>f(r, c)</code> as the obstacle-free paths from (0, 0) to (r, c).",
                    "If <code>r &lt; 0 or c &lt; 0 or grid[r][c] == 1</code>, return 0.",
                    "If <code>r == 0 and c == 0</code>, return 1.",
                    "Otherwise return <code>f(r - 1, c) + f(r, c - 1)</code>.",
                    "Call <code>f(len(grid) - 1, len(grid[0]) - 1)</code>.",
                ],
                "why": [
                    "A path through an obstacle is impossible, and returning 0 there removes every such path from every sum above it.",
                    "The obstacle test comes before the start test, so a blocked start correctly gives 0.",
                    "Nothing is cached, so the call tree can be exponential: <strong>O(2<sup>m+n</sup>)</strong> time, and <strong>O(m + n)</strong> stack depth.",
                ],
                "dry": [
                    [
                        "Call f(2, 2) = f(1, 2) + f(2, 1).",
                        "f(1, 2) = f(0, 2) + f(1, 1). f(1, 1) is the obstacle, so 0. f(0, 2) walks the top row back to f(0, 0) = 1, so f(1, 2) = 1.",
                        "f(2, 1) = f(1, 1) + f(2, 0) = 0 + 1 = 1, with f(2, 0) walking down the left column.",
                        "15 calls in total, several of them stepping off the grid at r or c = −1.",
                        "The result is 1 + 1 = <strong>2</strong>.",
                    ],
                    [
                        "Call f(1, 1) = f(0, 1) + f(1, 0).",
                        "grid[0][1] = 1, so f(0, 1) = 0.",
                        "grid[1][0] = 1, so f(1, 0) = 0.",
                        "Both ways in are blocked; it returns <strong>0</strong> after 3 calls.",
                    ],
                ],
                "faq": [
                    ["Why check the obstacle before the start cell?",
                     "If (0, 0) itself is an obstacle there are no paths at all. Checking the start first would wrongly return 1 for <code>[[1]]</code>."],
                    ["Why is <code>r &lt; 0 or c &lt; 0</code> needed now?",
                     "Without the \"first row/column is 1\" shortcut, recursion along an edge eventually asks for (−1, c) or (r, −1). Those positions have 0 paths, and the check stops <code>grid[-1]</code> from silently wrapping around."],
                    ["Can I keep the old base case <code>r == 0 or c == 0</code> returning 1?",
                     "No. On the grid <code>[[0, 1, 0]]</code> that would return 1 for the last cell, but the obstacle in the middle blocks it."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on the same <code>f</code>, so each (r, c) is solved once.",
                    "The obstacle and boundary checks still come first; their 0 results get cached too.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Return 0 for out-of-grid positions or obstacles.",
                    "Return 1 at (0, 0).",
                    "Otherwise return <code>f(r - 1, c) + f(r, c - 1)</code>, reusing cached values.",
                    "Call <code>f</code> on the bottom-right corner.",
                ],
                "why": [
                    "The recurrence and base cases are identical to plain recursion, so the answer is identical.",
                    "At most m·n in-grid states plus O(m + n) off-grid ones are computed once each: <strong>O(m·n)</strong> time.",
                    "The cache holds those entries: <strong>O(m·n)</strong> space, plus an O(m + n) stack.",
                ],
                "dry": [
                    [
                        "f(2, 2) → f(1, 2) → f(0, 2) → f(0, 1) → f(0, 0) = 1. So f(0, 1) = 1 and f(0, 2) = 1 (the (−1, ·) calls return 0).",
                        "f(1, 1) is the obstacle: 0. So f(1, 2) = 1 + 0 = 1.",
                        "f(2, 1) needs f(1, 1): cached, 0. It also needs f(2, 0) = f(1, 0) + 0 = 1.",
                        "So f(2, 1) = 0 + 1 = 1. 13 states were cached against 15 calls before.",
                        "f(2, 2) = 1 + 1 = <strong>2</strong>.",
                    ],
                    [
                        "f(1, 1) asks f(0, 1): obstacle, cached as 0.",
                        "It asks f(1, 0): obstacle, cached as 0.",
                        "f(1, 1) = 0 + 0 = 0.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Does caching off-grid calls like f(−1, 2) waste memory?",
                     "Slightly: there are at most m + n of them. They could be avoided by checking the bounds before calling, but the code is simpler this way."],
                    ["Why is <code>grid</code> not part of the cache key?",
                     "It is captured from the outer function and never changes during one call, so (r, c) alone identifies a state."],
                    ["What if the start or the end is blocked?",
                     "The obstacle check returns 0 for that cell, and the 0 flows into the final answer."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> the recursion becomes a table <code>dp</code> filled row by row, left to right, so the cells above and to the left are always ready.",
                    "The three branches of the recursion map directly onto three branches in the loop: obstacle → 0, start → 1, otherwise up + left.",
                ],
                "steps": [
                    "Create <code>dp</code> as an m × n table of zeros.",
                    "Loop over every <code>r</code>, then every <code>c</code>.",
                    "If <code>grid[r][c] == 1</code>, set <code>dp[r][c] = 0</code>.",
                    "Else if (r, c) is (0, 0), set it to 1.",
                    "Else take <code>up = dp[r - 1][c] if r else 0</code> and <code>left = dp[r][c - 1] if c else 0</code>, and store <code>up + left</code>.",
                    "Return <code>dp[m - 1][n - 1]</code>.",
                ],
                "why": [
                    "<code>if r else 0</code> and <code>if c else 0</code> play the role of the recursion's off-grid 0, so the edges need no special pre-filling.",
                    "Each cell is filled once with O(1) work: <strong>O(m·n)</strong> time.",
                    "The full table gives <strong>O(m·n)</strong> space.",
                ],
                "dry": [
                    [
                        "Row 0: dp[0][0] = 1, then each cell is 0 + left: [1, 1, 1].",
                        "Row 1: dp[1][0] = 1 + 0 = 1. (1, 1) is the obstacle, so 0. dp[1][2] = up 1 + left 0 = 1.",
                        "Row 2: dp[2][0] = 1. dp[2][1] = up 0 + left 1 = 1. dp[2][2] = up 1 + left 1 = 2.",
                        "The table is [[1, 1, 1], [1, 0, 1], [1, 1, 2]].",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "dp[0][0] = 1. (0, 1) is an obstacle: 0.",
                        "(1, 0) is an obstacle: 0.",
                        "dp[1][1] = up 0 + left 0 = 0.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not pre-fill the first row and column with 1 like before?",
                     "An obstacle on the first row blocks every cell after it. The general up + left rule already handles that, so pre-filling would be a bug."],
                    ["Is <code>dp[r][c] = 0</code> for obstacles needed if the table starts at 0?",
                     "Not strictly, since the cell is already 0. It is kept to make the three cases explicit; the one-row version needs it for real."],
                    ["Could I use <code>dp[r - 1][c]</code> with r = 0?",
                     "Python would read <code>dp[-1][c]</code>, the last row, without an error, which is a silent bug. The <code>if r else 0</code> guard prevents it."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> only the row above, <code>prev</code>, and the current row, <code>cur</code>, are kept.",
                    "A <strong>phantom row</strong> above the grid with <code>prev[0] = 1</code> means \"one way to enter the start\", so (0, 0) needs no special branch any more.",
                ],
                "steps": [
                    "Set <code>prev = [0] * n</code> and <code>prev[0] = 1</code>.",
                    "For each row <code>cells</code>, start <code>cur = [0] * n</code>.",
                    "For each column <code>c</code>, if <code>cells[c] == 0</code>, set <code>cur[c] = prev[c] + (cur[c - 1] if c else 0)</code>; obstacles keep 0.",
                    "Set <code>prev = cur</code> after the row.",
                    "Return <code>prev[-1]</code>.",
                ],
                "why": [
                    "With the phantom row, the start cell gets 1 + 0 = 1 if it is free and 0 if it is blocked, matching the 2-D table.",
                    "Every other value equals <code>dp[r][c]</code>, since <code>prev[c]</code> is the cell above and <code>cur[c - 1]</code> the cell to the left.",
                    "<strong>O(m·n)</strong> time and <strong>O(n)</strong> space for the two rows.",
                ],
                "dry": [
                    [
                        "prev = [1, 0, 0] (phantom row).",
                        "Row 0: cur[0] = 1 + 0 = 1, cur[1] = 0 + 1 = 1, cur[2] = 0 + 1 = 1. prev = [1, 1, 1].",
                        "Row 1: cur[0] = 1. cells[1] is an obstacle, so cur[1] stays 0. cur[2] = 1 + 0 = 1. prev = [1, 0, 1].",
                        "Row 2: cur[0] = 1, cur[1] = 0 + 1 = 1, cur[2] = 1 + 1 = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "prev = [1, 0].",
                        "Row 0: cur[0] = 1, cur[1] is an obstacle: 0. prev = [1, 0].",
                        "Row 1: cur[0] is an obstacle: 0. cur[1] = prev[1] 0 + cur[0] 0 = 0.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["What is the phantom row for?",
                     "It gives the start cell an \"above\" value of 1, so the general rule produces 1 there. Without it the start needs its own <code>if</code>."],
                    ["Why start <code>cur</code> at zeros?",
                     "Obstacle cells are simply skipped by the <code>if</code>, so they must already hold 0."],
                    ["Does the phantom row affect other columns?",
                     "No. Only <code>prev[0]</code> is 1; the rest are 0, so cells on row 0 get only their left neighbour, as they should."],
                ],
            },
            "One row, zero at obstacles": {
                "idea": [
                    "<strong>What changed:</strong> <code>prev</code> and <code>cur</code> are merged into one list <code>row</code>, updated left to right.",
                    "Before the update, <code>row[c]</code> still holds the cell above; <code>row[c - 1]</code> is already the cell to the left. So <code>row[c] += row[c - 1]</code> is up + left.",
                    "An obstacle must <strong>actively reset</strong> <code>row[c]</code> to 0, because the list still holds the count from the row above.",
                ],
                "steps": [
                    "Set <code>row = [0] * n</code> and <code>row[0] = 1</code> (the phantom start).",
                    "For each row <code>cells</code>, sweep <code>c</code> from 0 to n − 1.",
                    "If <code>cells[c] == 1</code>, set <code>row[c] = 0</code>.",
                    "Else if <code>c &gt; 0</code>, do <code>row[c] += row[c - 1]</code>. Column 0 keeps its value from above.",
                    "Return <code>row[-1]</code>.",
                ],
                "why": [
                    "This is the same recurrence as the 2-D table, stored in one list: the left part is the new row, the right part still the old one.",
                    "Column 0 only has one way in, from above, so leaving it unchanged (unless blocked) is right. Once it hits an obstacle it stays 0 for all lower rows.",
                    "<strong>O(m·n)</strong> time and <strong>O(n)</strong> space for a single list.",
                ],
                "dry": [
                    [
                        "row = [1, 0, 0].",
                        "Row 0: row[1] = 0 + 1 = 1, row[2] = 0 + 1 = 1. row = [1, 1, 1].",
                        "Row 1: column 0 stays 1. cells[1] is the obstacle: row[1] = 0. row[2] = 1 + 0 = 1. row = [1, 0, 1].",
                        "Row 2: row[1] = 0 + 1 = 1, row[2] = 1 + 1 = 2. row = [1, 1, 2].",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "row = [1, 0].",
                        "Row 0: cells[1] is an obstacle, row[1] = 0. row = [1, 0].",
                        "Row 1: cells[0] is an obstacle, row[0] = 0. row[1] = 0 + 0 = 0.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must an obstacle set <code>row[c] = 0</code> instead of just being skipped?",
                     "In one list, skipping would leave the count from the row above in place, as if the obstacle were free. In <code>[[0, 0], [0, 1]]</code> that would return 1 instead of 0."],
                    ["Why the <code>elif c &gt; 0</code> guard?",
                     "For column 0, <code>row[c - 1]</code> would be <code>row[-1]</code>, the last column, which is a wrap-around bug."],
                    ["Does <code>row[0] = 1</code> break if the start is blocked?",
                     "No. The first row's sweep sees the obstacle at column 0 and resets it to 0 before anything reads it."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ minimum path sum
    "minimum-path-sum": {
        "examples": [
            {"call": "min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]])", "expect": "7"},
            {"call": "min_path_sum([[1, 2, 3], [4, 5, 6]])", "expect": "12"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Same grid and moves as Unique Paths, but now each cell has a cost and we want the <strong>cheapest</strong> path, so the sum becomes a <code>min</code>.",
                    "The cheapest path into (r, c) pays <code>grid[r][c]</code> plus the cheaper of the cheapest paths into the cell above and the cell to the left.",
                    "Off-grid positions return <code>inf</code> so <code>min</code> never picks them.",
                ],
                "steps": [
                    "Define <code>f(r, c)</code> as the cheapest path sum from (0, 0) to (r, c), including both ends.",
                    "If <code>r &lt; 0 or c &lt; 0</code>, return <code>inf</code>.",
                    "If (r, c) is (0, 0), return <code>grid[0][0]</code>.",
                    "Otherwise return <code>grid[r][c] + min(f(r - 1, c), f(r, c - 1))</code>.",
                    "Call <code>f</code> on the bottom-right corner.",
                ],
                "why": [
                    "Any cheapest path into (r, c) has a cheapest prefix: if the part before the last move could be made cheaper, the whole path could too. That is optimal substructure.",
                    "Without caching, cells are re-solved through every route: <strong>O(2<sup>m+n</sup>)</strong> time.",
                    "The call stack is at most m + n deep: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(2, 2) = 1 + min(f(1, 2), f(2, 1)).",
                        "f(1, 2) = 1 + min(f(0, 2), f(1, 1)) = 1 + min(5, 7) = 6, where f(0, 2) = 1+3+1 and f(1, 1) = 5 + min(4, 2).",
                        "f(2, 1) = 2 + min(f(1, 1), f(2, 0)) = 2 + min(7, 6) = 8.",
                        "27 calls in total; f(1, 1) alone is solved twice.",
                        "f(2, 2) = 1 + min(6, 8) = <strong>7</strong>, along 1 → 3 → 1 → 1 → 1.",
                    ],
                    [
                        "f(1, 2) = 6 + min(f(0, 2), f(1, 1)).",
                        "f(0, 2) = 3 + min(inf, f(0, 1)) = 3 + 3 = 6, along the top row.",
                        "f(1, 1) = 5 + min(f(0, 1), f(1, 0)) = 5 + min(3, 5) = 8.",
                        "f(1, 2) = 6 + min(6, 8) = <strong>12</strong>, along 1 → 2 → 3 → 6.",
                    ],
                ],
                "faq": [
                    ["Why <code>inf</code> and not 0 off the grid?",
                     "0 would look like a free route and <code>min</code> would happily take it. <code>inf</code> makes an impossible move never win."],
                    ["Does greedy (always step to the cheaper neighbour) work?",
                     "No. On example 1 greedy steps down to the 1, then down to the 4 (cheaper than the 5), then 2 and 1, for a total of 9. The best path costs 7 because it pays 3 early to reach a cheap column."],
                    ["Can costs be negative?",
                     "The recurrence still works with negatives, because there are no cycles: paths only go right and down."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on the same <code>f</code>, so each of the m·n cells is solved once.",
                    "The plain recursion solved f(1, 1) once through f(1, 2) and again through f(2, 1); with the cache the second time is a lookup.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Return <code>inf</code> off the grid and <code>grid[0][0]</code> at the start.",
                    "Otherwise return <code>grid[r][c] + min(f(r - 1, c), f(r, c - 1))</code>.",
                    "Call <code>f(len(grid) - 1, len(grid[0]) - 1)</code>.",
                ],
                "why": [
                    "Same recurrence, same answer; the cache only stops recomputation.",
                    "Each cell does O(1) work once: <strong>O(m·n)</strong> time.",
                    "The cache stores up to m·n values, plus an O(m + n) stack: <strong>O(m·n)</strong> space.",
                    "Deep recursion on large grids is the remaining weakness, fixed by the bottom-up table.",
                ],
                "dry": [
                    [
                        "f(2, 2) → f(1, 2) → f(0, 2) → f(0, 1) → f(0, 0) = 1. Cached: f(0, 1) = 4, f(0, 2) = 5.",
                        "f(1, 1) = 5 + min(f(0, 1) 4, f(1, 0) 2) = 7. So f(1, 2) = 1 + min(5, 7) = 6.",
                        "f(2, 1) = 2 + min(f(1, 1) cached 7, f(2, 0) 6) = 8.",
                        "Every cell now has one cached value, the same numbers as the 2-D table.",
                        "f(2, 2) = 1 + min(6, 8) = <strong>7</strong>.",
                    ],
                    [
                        "f(1, 2) → f(0, 2) → f(0, 1) → f(0, 0) = 1. Cached: f(0, 1) = 3, f(0, 2) = 6.",
                        "f(1, 1) = 5 + min(f(0, 1) cached 3, f(1, 0) 5) = 8.",
                        "f(1, 2) = 6 + min(6, 8) = 12.",
                        "It returns <strong>12</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the memo version need the grid to stay unchanged?",
                     "The cache assumes <code>f(r, c)</code> always has the same value. Mutating <code>grid</code> mid-run would make cached answers stale."],
                    ["Is the <code>inf</code> base case cached too?",
                     "Yes, at most m + n such entries. That is harmless."],
                    ["How do I recover the actual path, not only its sum?",
                     "Walk back from the corner: at each cell move to whichever of up or left has the smaller cached value."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> fill <code>dp</code> row by row, left to right; the cells above and to the left are always final by then.",
                    "Edges are handled by treating a missing neighbour as <code>inf</code>, mirroring the recursion's off-grid case.",
                ],
                "steps": [
                    "Create an m × n table <code>dp</code>.",
                    "At (0, 0), set <code>dp[0][0] = grid[0][0]</code> and <code>continue</code>.",
                    "Elsewhere take <code>up = dp[r - 1][c] if r else inf</code> and <code>left = dp[r][c - 1] if c else inf</code>.",
                    "Set <code>dp[r][c] = grid[r][c] + min(up, left)</code>.",
                    "Return <code>dp[m - 1][n - 1]</code>.",
                ],
                "why": [
                    "Each cell is computed from final values by the same rule as the recursion.",
                    "One pass with O(1) work per cell: <strong>O(m·n)</strong> time.",
                    "The table is <strong>O(m·n)</strong> space. Each row only reads the previous row, which the next steps exploit.",
                ],
                "dry": [
                    [
                        "Row 0: dp = 1, 1+3 = 4, 4+1 = 5 → [1, 4, 5].",
                        "Row 1: dp[1][0] = 1+1 = 2, dp[1][1] = 5 + min(4, 2) = 7, dp[1][2] = 1 + min(5, 7) = 6 → [2, 7, 6].",
                        "Row 2: dp[2][0] = 4+2 = 6, dp[2][1] = 2 + min(7, 6) = 8, dp[2][2] = 1 + min(6, 8) = 7.",
                        "The table is [[1, 4, 5], [2, 7, 6], [6, 8, 7]].",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "Row 0: [1, 3, 6].",
                        "Row 1: dp[1][0] = 1+4 = 5, dp[1][1] = 5 + min(3, 5) = 8.",
                        "dp[1][2] = 6 + min(6, 8) = 12.",
                        "It returns <strong>12</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>continue</code> at (0, 0)?",
                     "Both neighbours are missing there, so <code>min(inf, inf)</code> would add <code>inf</code>. The start is its own value."],
                    ["Can I pre-fill the first row and column as running sums instead?",
                     "Yes, that is a common style. The <code>inf</code> guards just fold that into the same loop."],
                    ["What does <code>dp[r][c]</code> mean?",
                     "The smallest sum of any right/down path from (0, 0) to (r, c), counting both endpoints."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> keep only <code>prev</code> (row above) and <code>cur</code> (current row).",
                    "A phantom row <code>prev = [0, inf, inf, ...]</code> sits above the grid: the 0 lets the start cell cost <code>grid[0][0]</code>, the <code>inf</code>s stop row 0 from coming \"from above\".",
                ],
                "steps": [
                    "Set <code>prev = [inf] * n</code>, then <code>prev[0] = 0</code>.",
                    "For each row <code>cells</code>, make <code>cur = [0] * n</code>.",
                    "For each <code>c</code>: <code>left = cur[c - 1] if c else inf</code>, then <code>cur[c] = cells[c] + min(prev[c], left)</code>.",
                    "Set <code>prev = cur</code>.",
                    "Return <code>prev[-1]</code>.",
                ],
                "why": [
                    "The phantom row makes the start cell equal <code>cells[0] + min(0, inf)</code> = <code>grid[0][0]</code>, so no special case is needed.",
                    "Each value equals the 2-D table entry, since <code>prev[c]</code> is above and <code>cur[c - 1]</code> is left.",
                    "<strong>O(m·n)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "prev = [0, inf, inf].",
                        "Row 0: cur = [1 + 0, 3 + 1, 1 + 4] = [1, 4, 5].",
                        "Row 1: cur[0] = 1 + 1 = 2, cur[1] = 5 + min(4, 2) = 7, cur[2] = 1 + min(5, 7) = 6.",
                        "Row 2: cur[0] = 4 + 2 = 6, cur[1] = 2 + min(7, 6) = 8, cur[2] = 1 + min(6, 8) = 7.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "prev = [0, inf, inf].",
                        "Row 0: cur = [1, 3, 6].",
                        "Row 1: cur[0] = 4 + 1 = 5, cur[1] = 5 + min(3, 5) = 8, cur[2] = 6 + min(6, 8) = 12.",
                        "It returns <strong>12</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>prev[0] = 0</code> and not <code>grid[0][0]</code>?",
                     "The cell adds its own cost, <code>cells[0]</code>. A 0 above means \"entering the start costs nothing extra\"."],
                    ["What would go wrong with <code>prev = [0] * n</code>?",
                     "Row 0 cells could \"come from above\" at cost 0 and skip the cells to their left, so <code>[[1, 2, 3]]</code> would give 3 instead of 6."],
                    ["Why initialise <code>cur</code> with zeros if every cell is overwritten?",
                     "The values are never read before being written; zeros are just a placeholder of the right length."],
                ],
            },
            "One row": {
                "idea": [
                    "<strong>What changed:</strong> one list <code>row</code>, updated in place left to right.",
                    "Before the update <code>row[c]</code> is the cheapest cost of the cell above, and <code>row[c - 1]</code> is already the cell to the left on this row.",
                ],
                "steps": [
                    "Set <code>row = [inf] * n</code>, then <code>row[0] = 0</code> (the phantom start).",
                    "For each row <code>cells</code>, first do <code>row[0] += cells[0]</code>: column 0 can only come from above.",
                    "For <code>c</code> from 1 to n − 1: <code>row[c] = cells[c] + min(row[c], row[c - 1])</code>.",
                    "Return <code>row[-1]</code>.",
                ],
                "why": [
                    "Column 0 is the running sum down the left edge, so <code>row[0] += cells[0]</code> is exactly its recurrence.",
                    "For c ≥ 1, <code>min(row[c], row[c - 1])</code> is min(above, left), so the values match the 2-D table.",
                    "<strong>O(m·n)</strong> time and <strong>O(n)</strong> space with one list.",
                ],
                "dry": [
                    [
                        "row = [0, inf, inf].",
                        "Row 0: row[0] = 1, row[1] = 3 + min(inf, 1) = 4, row[2] = 1 + min(inf, 4) = 5 → [1, 4, 5].",
                        "Row 1: row[0] = 2, row[1] = 5 + min(4, 2) = 7, row[2] = 1 + min(5, 7) = 6 → [2, 7, 6].",
                        "Row 2: row[0] = 6, row[1] = 2 + min(7, 6) = 8, row[2] = 1 + min(6, 8) = 7.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "row = [0, inf, inf].",
                        "Row 0: row = [1, 3, 6].",
                        "Row 1: row[0] = 5, row[1] = 5 + min(3, 5) = 8, row[2] = 6 + min(6, 8) = 12.",
                        "It returns <strong>12</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is column 0 handled outside the inner loop?",
                     "It has no left neighbour. Treating it separately avoids a <code>row[-1]</code> wrap-around."],
                    ["Why must the sweep go left to right?",
                     "Otherwise <code>row[c - 1]</code> would still be the old row's value, i.e. the up-left diagonal, which is not a legal move."],
                    ["Why start the other entries at <code>inf</code>?",
                     "On row 0 the \"above\" values must be impossible, so each cell takes its left neighbour."],
                ],
            },
            "In place": {
                "idea": [
                    "<strong>What changed:</strong> no extra table at all. Each <code>grid[r][c]</code> is overwritten with its cheapest path sum, since its own cost is never needed again once added.",
                    "The grid itself becomes the 2-D DP table.",
                ],
                "steps": [
                    "Loop over every (r, c) in row-major order, skipping (0, 0), which already equals its own cost.",
                    "Read <code>up = grid[r - 1][c] if r else inf</code> and <code>left = grid[r][c - 1] if c else inf</code>.",
                    "Do <code>grid[r][c] += min(up, left)</code>.",
                    "Return <code>grid[-1][-1]</code>.",
                ],
                "why": [
                    "When (r, c) is processed, the cells above and to the left have already been replaced by their cheapest sums, and (r, c) still holds its raw cost. So the update is the exact recurrence.",
                    "<strong>O(m·n)</strong> time, and <strong>O(1)</strong> extra space.",
                    "The trade-off is that the caller's grid is destroyed; that is only acceptable if the input may be modified.",
                ],
                "dry": [
                    [
                        "Row 0 becomes [1, 4, 5].",
                        "Row 1: 1 + 1 = 2, 5 + min(4, 2) = 7, 1 + min(5, 7) = 6 → [2, 7, 6].",
                        "Row 2: 4 + 2 = 6, 2 + min(7, 6) = 8, 1 + min(6, 8) = 7 → [6, 8, 7].",
                        "The grid now holds exactly the 2-D table.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "Row 0 becomes [1, 3, 6].",
                        "Row 1: 4 + 1 = 5, 5 + min(3, 5) = 8, 6 + min(6, 8) = 12.",
                        "The grid is now [[1, 3, 6], [5, 8, 12]].",
                        "It returns <strong>12</strong>.",
                    ],
                ],
                "faq": [
                    ["Is modifying the input acceptable in an interview?",
                     "Ask first. It saves memory, but a caller who reuses the grid will see changed values. The tests pass a copy for exactly this reason."],
                    ["Why skip (0, 0) instead of adding <code>min(inf, inf)</code>?",
                     "That would make the start <code>inf</code> and poison every later cell."],
                    ["Is this really O(1) space?",
                     "Extra space, yes: only a few scalars. The O(m·n) grid is the input itself."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ triangle
    "triangle": {
        "examples": [
            {"call": "minimum_total([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]])", "expect": "11"},
            {"call": "minimum_total([[-1], [2, 3], [1, -1, -3]])", "expect": "-1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "From position i on row r you may step to i or i + 1 on the next row, so the cheapest path down from (r, i) is its own value plus the cheaper of those two subproblems.",
                    "Working <strong>top-down from the apex towards the base</strong> means the answer is a single state, f(0, 0), instead of a minimum over every bottom cell.",
                    "Past the last row there is nothing left to pay, so f(n, i) = 0.",
                ],
                "steps": [
                    "Let <code>n = len(triangle)</code> and define <code>f(r, i)</code> as the cheapest path sum from (r, i) to the base.",
                    "If <code>r == n</code>, return 0.",
                    "Otherwise return <code>triangle[r][i] + min(f(r + 1, i), f(r + 1, i + 1))</code>.",
                    "Return <code>f(0, 0)</code>.",
                ],
                "why": [
                    "Every path from (r, i) goes through exactly one of its two children, and the rest of it must be the cheapest path from that child: optimal substructure.",
                    "Each call branches twice for n levels: <strong>O(2<sup>n</sup>)</strong> time.",
                    "The recursion is n deep: <strong>O(n)</strong> stack space.",
                    "Interior cells are reached by two parents, so they are solved many times. The memo step removes that.",
                ],
                "dry": [
                    [
                        "f(0, 0) = 2 + min(f(1, 0), f(1, 1)).",
                        "f(1, 0) = 3 + min(f(2, 0), f(2, 1)) = 3 + min(6 + min(4, 1), 5 + min(1, 8)) = 3 + min(7, 6) = 9.",
                        "f(1, 1) = 4 + min(f(2, 1), f(2, 2)) = 4 + min(6, 10) = 10, solving f(2, 1) a second time.",
                        "31 calls in total, every one of the 2<sup>5</sup> − 1 nodes of a full binary tree.",
                        "f(0, 0) = 2 + min(9, 10) = <strong>11</strong>, along 2 → 3 → 5 → 1.",
                    ],
                    [
                        "f(0, 0) = −1 + min(f(1, 0), f(1, 1)).",
                        "f(1, 0) = 2 + min(1, −1) = 1.",
                        "f(1, 1) = 3 + min(−1, −3) = 0.",
                        "f(0, 0) = −1 + min(1, 0) = <strong>-1</strong>, along −1 → 3 → −3, even though 3 looked worse than 2.",
                    ],
                ],
                "faq": [
                    ["Why recurse from the apex instead of from the bottom row?",
                     "From the apex there is a single start, so the answer is one call. Recursing from each bottom cell upward also works but needs a min over n final states and extra boundary checks."],
                    ["Does a greedy walk (always take the smaller child) work?",
                     "No. On example 2 greedy takes −1 → 2 → −1 for a total of 0, but −1 → 3 → −3 gives −1."],
                    ["Why can <code>i + 1</code> never run off the row?",
                     "Row r has r + 1 entries and row r + 1 has r + 2, so index i + 1 ≤ r + 1 is always valid one row down."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> the same <code>f</code> wrapped in <code>@cache</code>.",
                    "There are only about n²/2 cells, but the plain recursion visits 2<sup>n</sup> − 1 nodes. Each cell is now solved once.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Return 0 when <code>r == n</code>.",
                    "Otherwise return <code>triangle[r][i] + min(f(r + 1, i), f(r + 1, i + 1))</code>.",
                    "Return <code>f(0, 0)</code>.",
                ],
                "why": [
                    "Same recurrence, so the same answer; repeated subproblems become lookups.",
                    "There are n(n + 1)/2 cells, each solved once in O(1): <strong>O(n²)</strong> time.",
                    "The cache holds O(n²) values and the stack is n deep: <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "f(0,0) → f(1,0) → f(2,0) → f(3,0) = 4, f(3,1) = 1, so f(2, 0) = 6 + 1 = 7.",
                        "f(2, 1) = 5 + min(1, 8) = 6, so f(1, 0) = 3 + min(7, 6) = 9.",
                        "f(1, 1) needs f(2, 1): cached, 6. f(2, 2) = 7 + min(8, 3) = 10. f(1, 1) = 4 + 6 = 10.",
                        "Only 10 cells were computed, against 31 calls before.",
                        "f(0, 0) = 2 + min(9, 10) = <strong>11</strong>.",
                    ],
                    [
                        "f(2, 0) = 1, f(2, 1) = −1, so f(1, 0) = 2 + min(1, −1) = 1.",
                        "f(1, 1) reuses f(2, 1) = −1 and adds f(2, 2) = −3: 3 + (−3) = 0.",
                        "f(0, 0) = −1 + min(1, 0) = −1.",
                        "It returns <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the time n² and not n?",
                     "There are about n²/2 cells in the triangle, and each is a separate state that has to be solved."],
                    ["Are the f(n, i) base calls cached too?",
                     "Yes, n + 1 of them, all returning 0. They add nothing meaningful to the memory."],
                    ["Is there a recursion-depth risk?",
                     "Only n frames deep, so it is fine for the usual limit of a few hundred rows."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> fill a table from the base upward, so both children of each cell are ready before the cell itself.",
                    "An extra all-zero row <code>dp[n]</code> plays the part of the recursion's <code>r == n</code> base case.",
                ],
                "steps": [
                    "Make <code>dp</code> as an (n + 1) × (n + 1) table of zeros.",
                    "Loop <code>r</code> from n − 1 down to 0.",
                    "For each <code>i</code> in <code>range(r + 1)</code>, set <code>dp[r][i] = triangle[r][i] + min(dp[r + 1][i], dp[r + 1][i + 1])</code>.",
                    "Return <code>dp[0][0]</code>.",
                ],
                "why": [
                    "Rows are filled bottom-up, so the row below is final whenever a row is computed.",
                    "The bottom row is computed as its own values plus 0 from the zero row, so it needs no special case.",
                    "About n²/2 cells with O(1) work: <strong>O(n²)</strong> time and <strong>O(n²)</strong> space for the table.",
                ],
                "dry": [
                    [
                        "r = 3: dp[3] = [4, 1, 8, 3] (values + 0).",
                        "r = 2: dp[2] = [6 + 1, 5 + 1, 7 + 3] = [7, 6, 10].",
                        "r = 1: dp[1] = [3 + 6, 4 + 6] = [9, 10].",
                        "r = 0: dp[0][0] = 2 + min(9, 10) = 11.",
                        "It returns <strong>11</strong>.",
                    ],
                    [
                        "r = 2: dp[2] = [1, −1, −3].",
                        "r = 1: dp[1] = [2 + min(1, −1), 3 + min(−1, −3)] = [1, 0].",
                        "r = 0: dp[0][0] = −1 + min(1, 0) = −1.",
                        "It returns <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why size the table n + 1 by n + 1?",
                     "Row n is the zero base row, and the extra column makes <code>dp[r + 1][i + 1]</code> always in range."],
                    ["Can the table be filled top-down instead?",
                     "Yes, but then <code>dp[r][i]</code> means the cheapest path from the apex to (r, i), edges need special cases, and the answer is <code>min(dp[n - 1])</code>. Bottom-up is cleaner."],
                    ["Only the left part of each row is used. Is that wasteful?",
                     "Yes, about half the table is never touched. The row-based versions next fix that."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> keep only <code>below</code>, the row underneath, and build <code>cur</code> for the current row.",
                    "<code>below</code> starts as a copy of the last triangle row, which is the base-row answer, so no zero row is needed.",
                ],
                "steps": [
                    "Set <code>below = list(triangle[-1])</code>.",
                    "Loop <code>r</code> from n − 2 down to 0.",
                    "Build <code>cur</code> of length r + 1, with <code>cur[i] = triangle[r][i] + min(below[i], below[i + 1])</code>.",
                    "Set <code>below = cur</code>.",
                    "Return <code>below[0]</code>.",
                ],
                "why": [
                    "<code>below[i]</code> and <code>below[i + 1]</code> are exactly <code>dp[r + 1][i]</code> and <code>dp[r + 1][i + 1]</code>.",
                    "<strong>O(n²)</strong> time as before.",
                    "Only two rows of at most n entries: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "below = [4, 1, 8, 3].",
                        "r = 2: cur = [7, 6, 10]; below = cur.",
                        "r = 1: cur = [9, 10]; below = cur.",
                        "r = 0: cur = [2 + 9] = [11].",
                        "It returns <strong>11</strong>.",
                    ],
                    [
                        "below = [1, −1, −3].",
                        "r = 1: cur = [1, 0].",
                        "r = 0: cur = [−1 + 0] = [−1].",
                        "It returns <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why copy the last row with <code>list(...)</code>?",
                     "Here nothing writes into <code>below</code>, so it is precautionary; in the one-row version the copy is essential to keep the input intact."],
                    ["What if the triangle has one row?",
                     "The loop range is empty and <code>below[0]</code>, the single value, is returned."],
                    ["Why does <code>cur</code> shrink each row?",
                     "Row r has r + 1 entries, so the cost list for that row needs exactly that many."],
                ],
            },
            "One row": {
                "idea": [
                    "<strong>What changed:</strong> a single list <code>best</code> is overwritten in place, left to right.",
                    "Updating <code>best[i]</code> only destroys the old <code>best[i]</code>. The next index, i + 1, reads <code>best[i + 1]</code> and <code>best[i + 2]</code>, which are still the row-below values.",
                ],
                "steps": [
                    "Set <code>best = list(triangle[-1])</code>.",
                    "Loop <code>r</code> from n − 2 down to 0.",
                    "For <code>i</code> in <code>range(r + 1)</code>: <code>best[i] = triangle[r][i] + min(best[i], best[i + 1])</code>.",
                    "Return <code>best[0]</code>.",
                ],
                "why": [
                    "Each cell reads index i and i + 1, and only index i is overwritten, which no later cell in the same row reads. So in-place left-to-right is safe.",
                    "Entries past r are stale leftovers and simply never read again.",
                    "<strong>O(n²)</strong> time and <strong>O(n)</strong> space, with no new list per row.",
                ],
                "dry": [
                    [
                        "best = [4, 1, 8, 3].",
                        "r = 2: best[0] = 6 + 1 = 7, best[1] = 5 + 1 = 6, best[2] = 7 + 3 = 10 → [7, 6, 10, 3].",
                        "r = 1: best[0] = 3 + 6 = 9, best[1] = 4 + 6 = 10 → [9, 10, 10, 3].",
                        "r = 0: best[0] = 2 + 9 = 11.",
                        "It returns <strong>11</strong>.",
                    ],
                    [
                        "best = [1, −1, −3].",
                        "r = 1: best[0] = 2 + (−1) = 1, best[1] = 3 + (−3) = 0 → [1, 0, −3].",
                        "r = 0: best[0] = −1 + 0 = −1.",
                        "It returns <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is left to right safe here, when Unique Paths needed it for a different reason?",
                     "Here the dependencies point down and to the right (i and i + 1), so overwriting i never harms a later read. A right-to-left sweep would overwrite i + 1 before i reads it."],
                    ["Why copy <code>triangle[-1]</code>?",
                     "Without <code>list(...)</code>, <code>best</code> would be the input's last row itself and the updates would corrupt the caller's triangle."],
                    ["What is left in <code>best</code> at the end?",
                     "Index 0 is the answer; the other entries are leftovers from lower rows."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ dungeon game
    "dungeon-game": {
        "examples": [
            {"call": "calculate_minimum_hp([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]])", "expect": "7"},
            {"call": "calculate_minimum_hp([[2, -8], [-1, 5]])", "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "The knight must have at least 1 health at <strong>every</strong> moment, not just at the end. A forward DP of \"most health so far\" fails because a path with high health may have dipped too low earlier.",
                    "Work <strong>backwards</strong> instead: <code>need(r, c)</code> is the least health the knight must have on entering (r, c) to finish alive.",
                    "On entering (r, c) he gains <code>dungeon[r][c]</code> and must then have at least the cheaper next requirement, so <code>need = max(1, min(next) - dungeon[r][c])</code>.",
                ],
                "steps": [
                    "Off the grid (<code>r == m or c == n</code>), return <code>inf</code>, so that direction is never chosen.",
                    "At the princess cell, return <code>max(1, 1 - dungeon[r][c])</code>: he must still have 1 after this room.",
                    "Otherwise take <code>min(need(r + 1, c), need(r, c + 1))</code>, subtract <code>dungeon[r][c]</code>, and clamp to at least 1.",
                    "Return <code>need(0, 0)</code>.",
                ],
                "why": [
                    "If he enters (r, c) with h, he leaves with h + dungeon[r][c], and that must be at least the better next requirement. Solving for h gives min(next) − dungeon[r][c].",
                    "The <code>max(1, …)</code> clamp is needed because he must be alive on entering too: a big potion cannot be pre-spent to justify entering with 0.",
                    "Each call branches into two: <strong>O(2<sup>m+n</sup>)</strong> time, with <strong>O(m + n)</strong> stack depth.",
                ],
                "dry": [
                    [
                        "need(2, 2) = max(1, 1 − (−5)) = 6.",
                        "need(1, 2) = max(1, 6 − 1) = 5. need(2, 1) = max(1, 6 − 30) = 1. need(2, 0) = max(1, 1 − 10) = 1.",
                        "need(1, 1) = max(1, min(1, 5) + 10) = 11. need(1, 0) = max(1, min(1, 11) + 5) = 6. need(0, 2) = max(1, 5 − 3) = 2.",
                        "need(0, 1) = min(11, 2) + 3 = 5. 27 calls in total.",
                        "need(0, 0) = min(6, 5) + 2 = <strong>7</strong>.",
                    ],
                    [
                        "need(1, 1) = max(1, 1 − 5) = 1: the potion is a bonus, but he still needs 1.",
                        "need(1, 0) = max(1, 1 + 1) = 2. need(0, 1) = max(1, 1 + 8) = 9.",
                        "need(0, 0) = max(1, min(2, 9) − 2) = max(1, 0) = 1.",
                        "The clamp fires: the +2 at the start would cover the −1 later, but he cannot enter with 0. It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not track the best health going forwards?",
                     "Two numbers matter on a forward path, current health and the lowest point so far, and the path that is best for one can be worse for the other. Backwards, a single number per cell is enough."],
                    ["Why <code>max(1, ...)</code> and not <code>max(0, ...)</code>?",
                     "Health must stay at least 1 at all times. With 0, example 2 would return 0, which means entering dead."],
                    ["Why return <code>inf</code> off the grid?",
                     "So <code>min</code> always prefers the real neighbour. The princess cell needs its own base case because both its neighbours are off the grid."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on <code>need</code>, so each of the m·n rooms is solved once.",
                    "In plain recursion, rooms like (1, 1) and (1, 2) are reached from several parents and solved again each time.",
                ],
                "steps": [
                    "Decorate <code>need</code> with <code>@cache</code>.",
                    "Keep the three cases: off grid → <code>inf</code>, princess → <code>max(1, 1 - dungeon[r][c])</code>, otherwise the clamped formula.",
                    "Return <code>need(0, 0)</code>.",
                ],
                "why": [
                    "Same recurrence, same answer; the cache only removes repeats.",
                    "m·n rooms with O(1) work each: <strong>O(m·n)</strong> time.",
                    "The cache stores <strong>O(m·n)</strong> values, plus an O(m + n) stack.",
                    "The bottom-up table next removes the recursion entirely.",
                ],
                "dry": [
                    [
                        "need(0,0) → need(1,0) → need(2,0) → need(2,1) → need(2,2) = 6, then need(2, 1) = 1 and need(2, 0) = 1.",
                        "need(1, 1) → need(1, 2) = 5 (its down neighbour need(2, 2) is cached). need(1, 1) = 11, so need(1, 0) = 6.",
                        "need(0, 1) reuses need(1, 1) = 11; need(0, 2) reuses need(1, 2) = 5 → 2. need(0, 1) = 5.",
                        "Each of the 9 rooms is computed once.",
                        "need(0, 0) = min(6, 5) + 2 = <strong>7</strong>.",
                    ],
                    [
                        "need(1, 0) → need(1, 1) = 1, so need(1, 0) = 2.",
                        "need(0, 1) reads need(1, 1) from the cache: 1 + 8 = 9.",
                        "need(0, 0) = max(1, 2 − 2) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the result of <code>need</code> safe to cache?",
                     "It depends only on (r, c) and the fixed dungeon, never on the path taken to get there. That is exactly what working backwards buys."],
                    ["Would a forward memo on (r, c) work?",
                     "No: the best way to arrive at (r, c) depends on both current and lowest health, so (r, c) alone is not enough state going forwards."],
                    ["Does the princess base case need caching?",
                     "It is cached like any other call; it is just reached first."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> fill an (m + 1) × (n + 1) table <code>need</code> from the bottom-right corner back to (0, 0).",
                    "The extra row and column hold <code>inf</code>, except the two cells just past the princess, which hold 1: \"after the last room he must still have 1\". That removes the princess special case.",
                ],
                "steps": [
                    "Create <code>need</code> full of <code>inf</code>, size (m + 1) × (n + 1).",
                    "Set <code>need[m][n - 1] = need[m - 1][n] = 1</code>.",
                    "Loop <code>r</code> from m − 1 down to 0 and <code>c</code> from n − 1 down to 0.",
                    "Set <code>need[r][c] = max(1, min(need[r + 1][c], need[r][c + 1]) - dungeon[r][c])</code>.",
                    "Return <code>need[0][0]</code>.",
                ],
                "why": [
                    "For the princess cell the formula gives <code>max(1, min(1, 1) - dungeon)</code>, which is the old base case. Every other border cell sees one <code>inf</code> and one real neighbour.",
                    "Reverse loops make the cells below and to the right final before they are read.",
                    "<strong>O(m·n)</strong> time and <strong>O(m·n)</strong> space for the table.",
                ],
                "dry": [
                    [
                        "Row 2 (right to left): 6, then max(1, 6 − 30) = 1, then max(1, 1 − 10) = 1 → [1, 1, 6].",
                        "Row 1: max(1, 6 − 1) = 5, then min(1, 5) + 10 = 11, then min(1, 11) + 5 = 6 → [6, 11, 5].",
                        "Row 0: 5 − 3 = 2, then min(11, 2) + 3 = 5, then min(6, 5) + 2 = 7 → [7, 5, 2].",
                        "The bottom-right 6 says he needs 6 to survive the −5 room and still have 1.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "Row 1: need[1][1] = max(1, 1 − 5) = 1, need[1][0] = max(1, 1 + 1) = 2.",
                        "Row 0: need[0][1] = max(1, 1 + 8) = 9.",
                        "need[0][0] = max(1, min(2, 9) − 2) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why put 1 in both cells next to the princess?",
                     "Whichever one the <code>min</code> reads, the princess cell gets the requirement \"leave with at least 1\". Putting it in one of them is enough, but both is symmetric."],
                    ["Why must the loops go backwards?",
                     "Each cell depends on the cells below and to the right, so those must be filled first."],
                    ["What does <code>need[r][c]</code> mean in words?",
                     "The minimum health the knight must have when he steps into room (r, c) to reach the princess alive."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> keep only <code>below</code> (row r + 1) and build <code>cur</code> (row r), each of length n + 1.",
                    "A phantom row below the grid has <code>below[n - 1] = 1</code> and <code>inf</code> elsewhere, and <code>cur[n]</code> stays <code>inf</code> as the phantom right column.",
                ],
                "steps": [
                    "Set <code>below = [inf] * (n + 1)</code> and <code>below[n - 1] = 1</code>.",
                    "Loop <code>r</code> from m − 1 down to 0; build <code>cur = [inf] * (n + 1)</code>.",
                    "Loop <code>c</code> from n − 1 down to 0: <code>cur[c] = max(1, min(below[c], cur[c + 1]) - dungeon[r][c])</code>.",
                    "Set <code>below = cur</code>.",
                    "Return <code>below[0]</code>.",
                ],
                "why": [
                    "<code>below[c]</code> is the room below and <code>cur[c + 1]</code> the room to the right, so values match the 2-D table.",
                    "<strong>O(m·n)</strong> time.",
                    "Two lists of n + 1 entries: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "below = [inf, inf, 1, inf].",
                        "r = 2: cur = [1, 1, 6, inf]. below = cur.",
                        "r = 1: cur = [6, 11, 5, inf]. below = cur.",
                        "r = 0: cur = [7, 5, 2, inf].",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "below = [inf, 1, inf].",
                        "r = 1: cur[1] = max(1, 1 − 5) = 1, cur[0] = max(1, min(inf, 1) + 1) = 2.",
                        "r = 0: cur[1] = max(1, min(1, inf) + 8) = 9, cur[0] = max(1, min(2, 9) − 2) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only one 1 in the phantom row, at <code>n - 1</code>?",
                     "Only the princess column is allowed to \"exit downward\". Every other bottom-row room must go right, so its below value is <code>inf</code>."],
                    ["Why is <code>cur</code> length n + 1?",
                     "So <code>cur[c + 1]</code> exists for the last column; it is an <code>inf</code> wall."],
                    ["Could I keep columns instead of rows?",
                     "Yes; the problem is symmetric. Keeping the shorter dimension saves the most memory."],
                ],
            },
            "One row": {
                "idea": [
                    "<strong>What changed:</strong> a single list <code>need</code> of length n + 1, updated right to left.",
                    "Before the update <code>need[c]</code> still holds the room below; <code>need[c + 1]</code> was just updated to the room on the right. That is the pair the formula needs.",
                ],
                "steps": [
                    "Set <code>need = [inf] * (n + 1)</code> and <code>need[n - 1] = 1</code>.",
                    "Loop <code>r</code> from m − 1 down to 0, and <code>c</code> from n − 1 down to 0.",
                    "Do <code>need[c] = max(1, min(need[c], need[c + 1]) - dungeon[r][c])</code>.",
                    "After each row, <code>need[n] = inf</code> keeps the phantom column a wall.",
                    "Return <code>need[0]</code>.",
                ],
                "why": [
                    "Right to left is essential: column c reads c + 1 on the current row, so c + 1 must already be updated.",
                    "On the first pass only <code>need[n - 1] = 1</code> is finite, so the bottom row behaves like the phantom row of Two rows.",
                    "<strong>O(m·n)</strong> time and <strong>O(n)</strong> space for one list.",
                ],
                "dry": [
                    [
                        "need = [inf, inf, 1, inf].",
                        "r = 2: need[2] = max(1, 1 + 5) = 6, need[1] = 1, need[0] = 1 → [1, 1, 6, inf].",
                        "r = 1: need[2] = 6 − 1 = 5, need[1] = min(1, 5) + 10 = 11, need[0] = min(1, 11) + 5 = 6 → [6, 11, 5, inf].",
                        "r = 0: need[2] = 2, need[1] = min(11, 2) + 3 = 5, need[0] = min(6, 5) + 2 = 7.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "need = [inf, 1, inf].",
                        "r = 1: need[1] = 1, need[0] = 2 → [2, 1, inf].",
                        "r = 0: need[1] = 1 + 8 = 9, need[0] = max(1, 2 − 2) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>need[n] = inf</code> after each row really needed?",
                     "In this code it is a no-op: the inner loop only writes indices 0..n − 1, so <code>need[n]</code> is <code>inf</code> from the start and never changes. It just documents the wall."],
                    ["Why right to left and not left to right?",
                     "The dependency is on the right neighbour. Going left to right would read <code>need[c + 1]</code> from the row below, mixing a diagonal move into the recurrence."],
                    ["Why does the princess's 1 not leak into upper rows?",
                     "On row m − 1 it is overwritten by the princess's own requirement, so it acts only as the \"after the last room\" value."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ minimum falling path sum
    "minimum-falling-path-sum": {
        "examples": [
            {"call": "min_falling_path_sum([[2, 1, 3], [6, 5, 4], [7, 8, 9]])", "expect": "13"},
            {"call": "min_falling_path_sum([[-19, 57], [-40, -5]])", "expect": "-59"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "A falling path enters (r, c) from one of three cells above: (r − 1, c − 1), (r − 1, c) or (r − 1, c + 1).",
                    "So the cheapest path ending at (r, c) is <code>matrix[r][c]</code> plus the cheapest of those three, and the answer is the best over every cell in the last row.",
                    "Columns outside the matrix return <code>inf</code>, so <code>min</code> ignores them.",
                ],
                "steps": [
                    "Define <code>f(r, c)</code> as the cheapest falling path ending at (r, c).",
                    "If <code>c &lt; 0 or c &gt;= n</code>, return <code>inf</code>.",
                    "If <code>r == 0</code>, return <code>matrix[0][c]</code>: the path starts there.",
                    "Otherwise return <code>matrix[r][c] + min(f(r - 1, c - 1), f(r - 1, c), f(r - 1, c + 1))</code>.",
                    "Return <code>min(f(n - 1, c) for c in range(n))</code>.",
                ],
                "why": [
                    "Every falling path ends on the last row and its prefix must itself be the cheapest path to the previous cell, so the recurrence covers all paths.",
                    "Each call branches three ways for n − 1 levels, and there are n starting calls: <strong>O(n·3<sup>n</sup>)</strong> time.",
                    "The stack is n deep: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Row 1 values: f(1, 0) = 6 + min(inf, 2, 1) = 7, f(1, 1) = 5 + min(2, 1, 3) = 6, f(1, 2) = 4 + min(1, 3, inf) = 5.",
                        "f(2, 0) = 7 + min(inf, 7, 6) = 13.",
                        "f(2, 1) = 8 + min(7, 6, 5) = 13. f(2, 2) = 9 + min(6, 5, inf) = 14.",
                        "Row 1 cells are re-solved by each bottom cell: 33 calls in total.",
                        "min(13, 13, 14) = <strong>13</strong>.",
                    ],
                    [
                        "f(1, 0) = −40 + min(inf, −19, 57) = −59.",
                        "f(1, 1) = −5 + min(−19, 57, inf) = −24.",
                        "8 calls in total.",
                        "min(−59, −24) = <strong>-59</strong>.",
                    ],
                ],
                "faq": [
                    ["Why take a min over the last row instead of returning one call?",
                     "A falling path may end in any column, so each bottom cell is a candidate end."],
                    ["Can I do it the other way, starting from the top row?",
                     "Yes: define f as the cheapest path from (r, c) to the bottom and take the min over row 0. It is the same amount of work."],
                    ["Does it handle negative values?",
                     "Yes, as example 2 shows. There are no cycles, since each step moves down a row."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on <code>f</code>, so each (r, c) is solved once even though up to three cells below ask for it.",
                    "The n final calls also share the cache, so later columns of the last row reuse the work of earlier ones.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Keep the base cases: out of range → <code>inf</code>, row 0 → <code>matrix[0][c]</code>.",
                    "Recurse into the three cells above.",
                    "Return the min of <code>f(n - 1, c)</code> over all columns.",
                ],
                "why": [
                    "The recurrence is unchanged, so the answer is the same.",
                    "n² cells (plus O(n) off-grid keys) with O(1) work each: <strong>O(n²)</strong> time.",
                    "The cache holds <strong>O(n²)</strong> entries; the stack is O(n).",
                ],
                "dry": [
                    [
                        "f(2, 0) solves and caches row 0 entries 0 and 1, then f(1, 0) = 7 and f(1, 1) = 6. f(2, 0) = 13.",
                        "f(2, 1) reuses f(1, 0) and f(1, 1) and computes f(1, 2) = 5. f(2, 1) = 8 + 5 = 13.",
                        "f(2, 2) is pure lookups: 9 + min(6, 5) = 14.",
                        "Each row-1 cell was computed once.",
                        "The answer is <strong>13</strong>.",
                    ],
                    [
                        "f(1, 0) caches f(0, 0) = −19 and f(0, 1) = 57: −40 − 19 = −59.",
                        "f(1, 1) reuses both cached values: −5 − 19 = −24.",
                        "min(−59, −24) = −59.",
                        "It returns <strong>-59</strong>.",
                    ],
                ],
                "faq": [
                    ["Are the out-of-range calls cached too?",
                     "Yes, f(r, −1) and f(r, n) for each row: O(n) extra entries, harmless."],
                    ["Why does the cache help across the final <code>min(...)</code>?",
                     "The generator calls the same cached <code>f</code> for every last-row column, so shared rows above are solved only once in total."],
                    ["Why not jump straight to one row?",
                     "The memo is the easiest correct step from the recursion; the row version then removes the stack and the cache."],
                ],
            },
            "One row at a time": {
                "idea": [
                    "<strong>What changed:</strong> the memo is replaced by a bottom-up pass that keeps only the previous row of best sums, <code>prev</code>.",
                    "Padding <code>prev</code> with <code>inf</code> on both sides turns the three parents of column c into <code>padded[c]</code>, <code>padded[c + 1]</code>, <code>padded[c + 2]</code>, with no bounds checks.",
                ],
                "steps": [
                    "Start with <code>prev = matrix[0][:]</code>: on row 0 the best sum is the value itself.",
                    "For each later <code>row</code>, build <code>padded = [inf] + prev + [inf]</code>.",
                    "Make the new <code>prev</code> with <code>x + min(padded[c], padded[c + 1], padded[c + 2])</code> for each (c, x) in the row.",
                    "Return <code>min(prev)</code>.",
                ],
                "why": [
                    "<code>padded[c + 1]</code> is <code>prev[c]</code>, so the window <code>c..c + 2</code> covers columns c − 1, c, c + 1 of the previous row, with <code>inf</code> where those fall off the edge.",
                    "Each row does O(n) work for n rows: <strong>O(n²)</strong> time.",
                    "Only the previous row and its padded copy are stored: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "prev = [2, 1, 3].",
                        "Row [6, 5, 4]: padded = [inf, 2, 1, 3, inf], prev = [6 + 1, 5 + 1, 4 + 1] = [7, 6, 5].",
                        "Row [7, 8, 9]: padded = [inf, 7, 6, 5, inf], prev = [7 + 6, 8 + 5, 9 + 5] = [13, 13, 14].",
                        "min(prev) = 13.",
                        "It returns <strong>13</strong>.",
                    ],
                    [
                        "prev = [−19, 57].",
                        "Row [−40, −5]: padded = [inf, −19, 57, inf].",
                        "prev = [−40 − 19, −5 − 19] = [−59, −24].",
                        "It returns min(prev) = <strong>-59</strong>.",
                    ],
                ],
                "faq": [
                    ["Why copy row 0 with <code>[:]</code>?",
                     "It is precautionary: later rows build brand-new lists, so the input is never written, but the copy makes that obvious."],
                    ["Why not update <code>prev</code> in place?",
                     "Column c + 1 still needs the old <code>prev[c]</code>, which an in-place update would have overwritten. The list comprehension builds the new row from the untouched old one."],
                    ["What is <code>padded</code> for?",
                     "It removes the edge cases for column 0 and column n − 1, which have only two parents."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ maximal square
    "maximal-square": {
        "examples": [
            {"call": 'maximal_square([["1", "1", "0"], ["1", "1", "1"], ["0", "1", "1"]])', "expect": "4"},
            {"call": 'maximal_square([["0", "1"], ["1", "0"]])', "expect": "1"},
        ],
        "approaches": {
            "Grow a square from every cell": {
                "idea": [
                    "Treat every cell as a possible <strong>top-left corner</strong> and grow a square from it one size at a time.",
                    "Going from side k to side k + 1 only adds one new row segment at the bottom and one new column segment on the right, so only those need checking.",
                    "Stop at the first size that fails: a bigger square from the same corner would contain the failing cell too.",
                ],
                "steps": [
                    "Loop over every (r, c) with <code>k = 0</code>.",
                    "While the square of side k + 1 fits (<code>r + k &lt; m and c + k &lt; n</code>), check the new bottom row <code>matrix[r + k][c .. c + k]</code> and the new right column <code>matrix[r .. r + k][c + k]</code>.",
                    "If both are all <code>\"1\"</code>, do <code>k += 1</code>; otherwise stop growing.",
                    "Update <code>best = max(best, k)</code>.",
                    "Return <code>best * best</code>, the area.",
                ],
                "why": [
                    "The square of side k is known to be all ones, so adding the new row and column checks exactly the cells of side k + 1, and every largest square is found from its own top-left corner.",
                    "Each corner grows up to min(m, n) times, and each growth checks O(min(m, n)) cells: <strong>O(m·n·min(m,n)<sup>2</sup>)</strong> time.",
                    "Only a few counters are kept: <strong>O(1)</strong> space.",
                    "Neighbouring corners re-check the same cells again and again. The DP below reuses those results.",
                ],
                "dry": [
                    [
                        "(0, 0): side 1 ok, side 2 checks row 1 cols 0–1 and col 1 rows 0–1, all \"1\": k = 2. Side 3 would need (0, 2) = \"0\", stop. best = 2.",
                        "(0, 1): k = 1, since (0, 2) is \"0\". (0, 2): k = 0.",
                        "(1, 0): k = 1, since (2, 0) is \"0\". (1, 1): side 2 uses rows 1–2, cols 1–2, all \"1\": k = 2, a second 2 × 2.",
                        "The remaining cells reach k = 1 at most. best stays 2.",
                        "It returns 2 · 2 = <strong>4</strong>.",
                    ],
                    [
                        "(0, 0) is \"0\": k = 0.",
                        "(0, 1): k = 1, and side 2 does not fit. (1, 0): k = 1. (1, 1): k = 0.",
                        "The two ones touch only diagonally, so no 2 × 2 exists.",
                        "It returns 1 · 1 = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check only the new row and column, not the whole square?",
                     "The previous square of side k already passed, so its cells are known to be \"1\". Rechecking them would add another factor of k."],
                    ["Why does the result have to be squared?",
                     "The problem asks for the area. <code>best</code> is a side length."],
                    ["Are the matrix values strings?",
                     "Yes, <code>\"1\"</code> and <code>\"0\"</code>. Comparing with the integer 1 would never match."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Let <code>dp[r][c]</code> be the side of the largest all-ones square whose <strong>bottom-right corner</strong> is at that cell.",
                    "A square of side s ends at (r, c) only if squares of side s − 1 end at the cell above, the cell to the left, and the diagonal cell. So <code>dp = 1 + min(up, left, diag)</code>.",
                    "The smallest of the three is the bottleneck: whichever direction runs out of ones first limits the square.",
                ],
                "steps": [
                    "Make <code>dp</code> of size (m + 1) × (n + 1), all 0; the extra row and column are a zero border.",
                    "Loop <code>r</code> from 1 to m and <code>c</code> from 1 to n; cell (r, c) of <code>dp</code> stands for <code>matrix[r - 1][c - 1]</code>.",
                    "If that cell is <code>\"1\"</code>, set <code>dp[r][c] = 1 + min(dp[r - 1][c], dp[r][c - 1], dp[r - 1][c - 1])</code>; a <code>\"0\"</code> keeps 0.",
                    "Track <code>best = max(best, dp[r][c])</code>.",
                    "Return <code>best * best</code>.",
                ],
                "why": [
                    "The three overlapping squares of side s − 1 cover every cell of the s × s square except the corner itself, so the formula is both necessary and sufficient.",
                    "Each cell does O(1) work: <strong>O(m·n)</strong> time, against the cubic-plus cost of growing squares.",
                    "The table uses <strong>O(m·n)</strong> space. Each row reads only the row above, which the next step exploits.",
                ],
                "dry": [
                    [
                        "Row 1 (matrix row 0): dp = [1, 1, 0].",
                        "Row 2: dp[2][1] = 1 + min(1, 0, 0) = 1, dp[2][2] = 1 + min(1, 1, 1) = 2, dp[2][3] = 1 + min(0, 2, 1) = 1.",
                        "Row 3: matrix (2, 0) is \"0\" → 0. dp[3][2] = 1 + min(2, 0, 1) = 1. dp[3][3] = 1 + min(1, 1, 2) = 2.",
                        "best reaches 2 twice, once for each 2 × 2 block.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "Row 1: \"0\" → 0, then dp[1][2] = 1 + min(0, 0, 0) = 1.",
                        "Row 2: dp[2][1] = 1 + min(0, 0, 0) = 1, then \"0\" → 0.",
                        "best = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why bottom-right corner and not top-left?",
                     "With a row-major sweep, the cells above, left and diagonal-up-left are already done, so the bottom-right corner fits the fill order."],
                    ["Why is <code>min</code> right and not, say, <code>max</code>?",
                     "All three neighbouring squares must exist at size s − 1. Taking <code>max</code> would claim a square that has a zero inside the weaker side."],
                    ["What is the padding row and column for?",
                     "They hold 0 so first-row and first-column cells read real zeros instead of needing <code>if r</code> guards."],
                ],
            },
            "One row plus one saved diagonal": {
                "idea": [
                    "<strong>What changed:</strong> the table is reduced to one list <code>row</code> of length n + 1, updated left to right.",
                    "Before overwriting <code>row[c]</code> it holds the value <em>above</em>; <code>row[c - 1]</code> is already the value to the <em>left</em>. The diagonal, however, was overwritten one step earlier, so it is saved in <code>diag</code> before that happens.",
                ],
                "steps": [
                    "Set <code>row = [0] * (n + 1)</code> and <code>best = 0</code>.",
                    "For each <code>line</code>, reset <code>diag = 0</code> (the padding column's old value).",
                    "For c from 1 to n: save <code>above = row[c]</code>, then set <code>row[c] = 1 + min(row[c], row[c - 1], diag)</code> if <code>line[c - 1] == \"1\"</code>, else 0.",
                    "Set <code>diag = above</code>: the old value at c is the next column's diagonal.",
                    "Update <code>best</code>; return <code>best * best</code>.",
                ],
                "why": [
                    "<code>above</code> is captured before the write, so after <code>diag = above</code> the next column sees the old row's value at c, which is its up-left neighbour.",
                    "Every cell gets the same value as in the 2-D table.",
                    "<strong>O(m·n)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Line 0: row becomes [0, 1, 1, 0]; diag carries the old zeros.",
                        "Line 1: c=1: above 1, min(1, 0, diag 0) → 1. c=2: above 1, min(1, 1, diag 1) → 2. c=3: above 0, min(0, 2, diag 1) → 1. row = [0, 1, 2, 1].",
                        "Line 2: c=1 is \"0\" → 0. c=2: above 2, min(2, 0, diag 1) → 1. c=3: above 1, min(1, 1, diag 2) → 2.",
                        "best = 2.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "Line 0: c=1 \"0\" → 0; c=2: min(0, 0, 0) + 1 = 1. row = [0, 0, 1].",
                        "Line 1: c=1: min(0, 0, 0) + 1 = 1. c=2 is \"0\" → 0. row = [0, 1, 0].",
                        "best = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why reset <code>diag = 0</code> at the start of each line?",
                     "The diagonal of column 1 is the padding column, which is always 0. Without the reset it would carry the last value from the previous line."],
                    ["Why does the diagonal need saving while above and left do not?",
                     "Above is still in <code>row[c]</code> and left is the fresh <code>row[c - 1]</code>, but the old <code>row[c - 1]</code> (the diagonal) was overwritten one step earlier."],
                    ["Must a \"0\" cell write 0 explicitly?",
                     "Yes. Unlike the 2-D table, <code>row[c]</code> still holds the value from the row above, so leaving it would be wrong."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ count square submatrices
    "count-square-submatrices": {
        "examples": [
            {"call": "count_squares([[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]])", "expect": "15"},
            {"call": "count_squares([[1, 0, 1], [1, 1, 0], [1, 1, 0]])", "expect": "7"},
        ],
        "approaches": {
            "Check every square": {
                "idea": [
                    "Every square is fixed by its top-left corner (r, c) and its side k. Try them all and count the ones that are entirely 1.",
                    "If the k × k square from a corner contains a 0, every larger square from that corner contains it too, so the loop can <code>break</code>.",
                ],
                "steps": [
                    "Loop over every corner (r, c).",
                    "For <code>k</code> from 1 to <code>min(m - r, n - c)</code>, test every cell of the k × k square with <code>all(...)</code>.",
                    "If it is all ones, <code>total += 1</code>; otherwise <code>break</code>.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "Each square is counted once, at its own top-left corner and size, so nothing is double-counted or missed.",
                    "The early <code>break</code> is safe because a failing square is contained in every bigger one from the same corner.",
                    "Each corner tries up to min(m, n) sizes and checks up to k² cells each: <strong>O(m·n·min(m,n)<sup>3</sup>)</strong> time.",
                    "No extra storage: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "(0, 0) is 0: breaks at k = 1, count 0.",
                        "(0, 1): sides 1, 2 and 3 all pass (rows 0–2, cols 1–3 are all ones): 3 squares.",
                        "(0, 2): 2 squares; (0, 3): 1. Row 1 gives 1 + 2 + 2 + 1; row 2 gives 0 + 1 + 1 + 1.",
                        "Totals: 6 from row 0, 6 from row 1, 3 from row 2.",
                        "It returns <strong>15</strong>.",
                    ],
                    [
                        "(0, 0): side 1 ok, side 2 has (0, 1) = 0: 1 square.",
                        "(0, 1) = 0, (0, 2): 1. (1, 0): sides 1 and 2 (rows 1–2, cols 0–1) pass: 2 squares.",
                        "(1, 1): 1, (1, 2): 0, (2, 0): 1, (2, 1): 1, (2, 2): 0.",
                        "1 + 1 + 2 + 1 + 1 + 1 = 7.",
                        "It returns <strong>7</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the bound <code>min(m - r, n - c)</code>?",
                     "That is the largest square that still fits inside the matrix from corner (r, c)."],
                    ["Is the <code>break</code> just an optimisation?",
                     "Yes, it never changes the count, because once side k fails every larger side fails too."],
                    ["Why is this so slow?",
                     "The <code>all(...)</code> re-scans the whole k × k square each time, including the part already checked at side k − 1."],
                ],
            },
            "In-place DP": {
                "idea": [
                    "Reuse the Maximal Square recurrence: <code>dp[r][c]</code> is the side of the largest all-ones square ending at (r, c), equal to <code>1 + min(up, left, diag)</code> for a 1 cell.",
                    "Key insight: if the largest square ending at (r, c) has side s, then squares of side 1, 2, …, s all end there. So that cell contributes exactly s squares.",
                    "The answer is the sum of all dp values, and the matrix itself can serve as dp.",
                ],
                "steps": [
                    "Leave row 0 and column 0 as they are: a 1 there can only be a 1 × 1 square.",
                    "Loop <code>r</code> from 1 and <code>c</code> from 1.",
                    "If <code>matrix[r][c]</code> is 1, overwrite it with <code>1 + min(matrix[r - 1][c], matrix[r][c - 1], matrix[r - 1][c - 1])</code>.",
                    "Return <code>sum(map(sum, matrix))</code>.",
                ],
                "why": [
                    "Every square has exactly one bottom-right corner, and at that corner the squares are counted by side 1..s, so the sum counts each square once.",
                    "Cells above, left and diagonal are already overwritten with their own dp values when (r, c) is processed, while (r, c) still holds its raw 0 or 1.",
                    "One pass plus one sum: <strong>O(m·n)</strong> time, <strong>O(1)</strong> extra space (the input is modified).",
                ],
                "dry": [
                    [
                        "Row 1: (1, 1) = 1 + min(1, 1, 0) = 1, (1, 2) = 1 + min(1, 1, 1) = 2, (1, 3) = 1 + min(1, 2, 1) = 2.",
                        "Row 2: (2, 1) = 1 + min(1, 0, 1) = 1, (2, 2) = 1 + min(2, 1, 1) = 2, (2, 3) = 1 + min(2, 2, 2) = 3.",
                        "Matrix: [[0, 1, 1, 1], [1, 1, 2, 2], [0, 1, 2, 3]].",
                        "Row sums 3 + 6 + 6.",
                        "It returns <strong>15</strong>.",
                    ],
                    [
                        "Row 1: (1, 1) = 1 + min(0, 1, 1) = 1; (1, 2) is 0.",
                        "Row 2: (2, 1) = 1 + min(1, 1, 1) = 2; (2, 2) is 0.",
                        "Matrix: [[1, 0, 1], [1, 1, 0], [1, 2, 0]].",
                        "Row sums 2 + 2 + 3.",
                        "It returns <strong>7</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does a value of s mean s squares and not s² or 1?",
                     "Those are the squares with that cell as bottom-right corner: one of each side 1..s. Other squares are counted at their own corners."],
                    ["Is it OK to overwrite the input?",
                     "Only if the caller allows it. The tests pass a copy; otherwise use a separate dp table or one row as in Maximal Square."],
                    ["How is this the same as Maximal Square?",
                     "Same table. Maximal Square takes the max of it and squares it; this problem takes the sum."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ longest increasing path in a matrix
    "longest-increasing-path-in-a-matrix": {
        "examples": [
            {"call": "longest_increasing_path([[9, 9, 4], [6, 6, 8], [2, 1, 1]])", "expect": "4"},
            {"call": "longest_increasing_path([[7, 7], [7, 7]])", "expect": "1"},
        ],
        "approaches": {
            "Plain DFS from every cell": {
                "idea": [
                    "Let <code>f(r, c)</code> be the length of the longest strictly increasing path that <strong>starts</strong> at (r, c). It is 1 plus the best <code>f</code> of any larger neighbour, or just 1 if there is none.",
                    "Moves can go in all four directions, but because values must strictly increase a path can never come back to a cell, so the recursion cannot loop.",
                    "The answer is the max of <code>f</code> over every starting cell.",
                ],
                "steps": [
                    "In <code>f(r, c)</code>, start <code>best = 1</code> (the cell alone).",
                    "For each of the four neighbours (nr, nc) inside the grid with <code>matrix[nr][nc] &gt; matrix[r][c]</code>, set <code>best = max(best, 1 + f(nr, nc))</code>.",
                    "Return <code>best</code>.",
                    "Return <code>max(f(r, c) for r in range(m) for c in range(n))</code>.",
                ],
                "why": [
                    "Strictly increasing values make the \"larger neighbour\" relation a DAG, so <code>f</code> is well defined and the recursion terminates.",
                    "Without caching, the same cells are explored again from every start and every path: <strong>O(m·n·4<sup>m·n</sup>)</strong> worst case as listed (it is exponential in practice on long paths).",
                    "The stack can be as deep as the longest path: <strong>O(m·n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(0, 0) and f(0, 1) (value 9) have no larger neighbour: 1.",
                        "f(0, 2) = 1 + f(1, 2) = 2. f(1, 0) = 1 + f(0, 0) = 2. f(1, 1) = 2 via a 9 or the 8.",
                        "f(2, 0) = 1 + f(1, 0) = 3. f(2, 1) explores f(1, 1) and f(2, 0) again: max(1 + 2, 1 + 3) = 4.",
                        "f(2, 2) = 1 + f(1, 2) = 2. 23 calls in total.",
                        "The max is <strong>4</strong>, along 1 → 2 → 6 → 9.",
                    ],
                    [
                        "Every cell is 7, and 7 &gt; 7 is false.",
                        "So no neighbour qualifies from any cell; each f returns 1.",
                        "Four calls, one per start.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is no visited set needed?",
                     "Values strictly increase along a path, so returning to an earlier cell would need a smaller value. Cycles are impossible."],
                    ["Why <code>&gt;</code> and not <code>&gt;=</code>?",
                     "The path must be strictly increasing. With <code>&gt;=</code>, example 2 would recurse between equal 7s forever."],
                    ["Why try every start cell?",
                     "The longest path can start anywhere; the global answer is the best of all of them."],
                ],
            },
            "Memoised DFS": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on <code>f</code>. Since <code>f(r, c)</code> depends only on the cell, not on how we got there, it can be stored.",
                    "Each cell's answer is now computed once and reused by every smaller neighbour and every start.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Inside, start at 1 and try the four larger neighbours as before.",
                    "Call <code>f</code> for every cell and take the max.",
                    "Later starts mostly hit the cache.",
                ],
                "why": [
                    "Same recurrence on a DAG, so the same values; caching is valid because there are no cycles.",
                    "Each cell is computed once and looks at 4 neighbours: <strong>O(m·n)</strong> time.",
                    "The cache has m·n entries and the stack can reach the longest path's length: <strong>O(m·n)</strong> space.",
                    "On long snake-like paths that depth can exceed Python's recursion limit, which the bottom-up order avoids.",
                ],
                "dry": [
                    [
                        "f(0, 0) = 1 and f(0, 1) = 1 are cached first.",
                        "f(0, 2) calls f(1, 2) = 1, so 2. f(1, 0) reads cached f(0, 0): 2. f(1, 1) reads cached f(0, 1) and f(1, 2): 2.",
                        "f(2, 0) reads cached f(1, 0): 3.",
                        "f(2, 1) reads cached f(1, 1) = 2 and f(2, 0) = 3: 4. f(2, 2) reads f(1, 2): 2.",
                        "The max is <strong>4</strong>.",
                    ],
                    [
                        "No neighbour is larger, so every f is 1 and is cached immediately.",
                        "No recursive call is ever made.",
                        "The max over four cells is 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can this be memoised when general longest-path problems cannot?",
                     "General graphs have cycles, which make a cell's answer depend on the path so far. Strict increase rules out cycles, so the answer depends on the cell alone."],
                    ["Do I still need to try all starting cells?",
                     "Yes, but each start after the first is often an O(1) cache hit."],
                    ["What is the recursion-depth risk?",
                     "A path through all m·n cells recurses m·n deep; the tests raise the limit to handle a 30 × 30 snake."],
                ],
            },
            "Bottom-up in decreasing value order": {
                "idea": [
                    "<strong>What changed:</strong> no recursion. <code>f</code> of a cell depends only on <em>larger</em> neighbours, so processing cells from the largest value down guarantees those neighbours are already final.",
                    "This is a topological order of the DAG, obtained simply by sorting.",
                ],
                "steps": [
                    "Make <code>f</code> as an m × n table of 1s.",
                    "Build <code>cells</code>, every <code>(value, r, c)</code>, sorted in reverse (largest first).",
                    "For each (v, r, c), look at the four neighbours; for each larger one, set <code>f[r][c] = max(f[r][c], 1 + f[nr][nc])</code>.",
                    "Return the largest entry, <code>max(map(max, f))</code>.",
                ],
                "why": [
                    "A strictly larger neighbour comes earlier in the sorted order, so its <code>f</code> is final when read. Equal neighbours are never used, so ties in the order do not matter.",
                    "Sorting costs <strong>O(m·n·log(m·n))</strong> time; the pass after it is O(m·n).",
                    "The table and the sorted list are <strong>O(m·n)</strong> space, with no recursion stack.",
                ],
                "dry": [
                    [
                        "Order: 9 (0,1), 9 (0,0), 8 (1,2), 6 (1,1), 6 (1,0), 4 (0,2), 2 (2,0), 1 (2,2), 1 (2,1).",
                        "The 9s and the 8 have no larger neighbour: f = 1.",
                        "6 at (1, 1) → 2; 6 at (1, 0) → 2; 4 at (0, 2) → 1 + f(1, 2) = 2.",
                        "2 at (2, 0) → 1 + 2 = 3; 1 at (2, 2) → 2; 1 at (2, 1) → max(1 + f(1, 1), 1 + f(2, 0)) = 4.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "All four cells are (7, ·, ·); order among them is arbitrary.",
                        "No neighbour is strictly larger, so nothing updates.",
                        "f stays all 1s.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort in decreasing order?",
                     "Each cell needs the answers of its larger neighbours. Largest first means those are always ready."],
                    ["What happens with equal values?",
                     "They can be in any order, which is fine: equal neighbours are skipped by the strict <code>&gt; v</code> test."],
                    ["Why is this slower than the memo in big-O?",
                     "Sorting adds a log factor. In exchange there is no recursion, so no stack-overflow risk."],
                ],
            },
        },
    },
}
