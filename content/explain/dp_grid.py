"""Write-ups for Dynamic Programming, part 3: grid problems."""

EXPLAIN = {
    # ------------------------------------------------------------------ unique paths
    "unique-paths": {
        "example": {"call": "unique_paths(3, 4)", "expect": "10"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "The last move into (r, c) came either from above or from the left, so <code>f(r, c) = f(r-1, c) + f(r, c-1)</code>.",
                    "Every cell on the top row or the left column has exactly one path: a straight line.",
                ],
                "steps": [
                    "Return 1 if r == 0 or c == 0; otherwise add the two recursive counts.",
                    "Call <code>f(m-1, n-1)</code>.",
                ],
                "why": [
                    "Every path is counted by walking it, and there are exponentially many paths.",
                    "The recursion is at most m + n deep.",
                ],
                "dry": [
                    "f(2, 3) = f(1, 3) + f(2, 2).",
                    "f(1, 3) = 4 (one down move placed among 4 moves), and f(2, 2) = 6.",
                    "The result is 4 + 6 = <strong>10</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "f(1, 2) is reached both through f(2, 2) and through f(1, 3); cache it so each cell is computed once.",
                ],
                "steps": [
                    "Same recursion with <code>@cache</code>.",
                ],
                "why": [
                    "There are m·n distinct cells, each doing O(1) work.",
                ],
                "dry": [
                    "Cached values: f(1, 1) = 2, f(1, 2) = 3, f(2, 1) = 3, f(1, 3) = 4, f(2, 2) = 6.",
                    "f(2, 3) = 4 + 6 = <strong>10</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Start the whole table at 1, which handles the top row and the left column.",
                    "Fill inner cells row by row: above and left are always ready.",
                ],
                "steps": [
                    "For r ≥ 1 and c ≥ 1: <code>dp[r][c] = dp[r-1][c] + dp[r][c-1]</code>.",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "Row 0: [1, 1, 1, 1].",
                    "Row 1: [1, 2, 3, 4].",
                    "Row 2: [1, 3, 6, 10]. The bottom-right cell is <strong>10</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Row r reads only row r-1, so keep just that one plus the row being built.",
                ],
                "steps": [
                    "<code>cur[0] = 1</code>; <code>cur[c] = prev[c] + cur[c-1]</code>; then <code>prev = cur</code>.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "prev = [1, 1, 1, 1] → [1, 2, 3, 4] → [1, 3, 6, 10].",
                    "The result is <strong>10</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "Before it is updated, <code>row[c]</code> still holds the value from above; <code>row[c-1]</code> already holds the value to the left.",
                    "So <code>row[c] += row[c-1]</code> is the whole recurrence.",
                ],
                "steps": [
                    "Repeat the left-to-right running sum m-1 times.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space, with no new list per row.",
                ],
                "dry": [
                    "First pass: [1, 1, 1, 1] becomes [1, 2, 3, 4], a running sum.",
                    "Second pass: [1, 3, 6, 10].",
                    "The result is <strong>10</strong>.",
                ],
            },
            "Binomial coefficient": {
                "idea": [
                    "Every path is exactly m-1 downs and n-1 rights in some order.",
                    "Choosing which of the m+n-2 moves are downs fixes the path: C(m+n-2, m-1).",
                ],
                "steps": [
                    "<code>comb(m + n - 2, m - 1)</code>.",
                ],
                "why": [
                    "Choosing the down positions picks exactly one path, and every path is picked once.",
                    "It is a neat shortcut, but the DP is what extends to obstacles.",
                ],
                "dry": [
                    "m + n - 2 = 5 moves, of which 2 are downs.",
                    "C(5, 2) = <strong>10</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ unique paths II
    "unique-paths-ii": {
        "example": {"call": "unique_paths_with_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]])", "expect": "2"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "This is the Unique Paths recurrence, but an obstacle cell (or a cell off the grid) contributes 0 paths.",
                    "The start contributes 1, unless it is itself an obstacle.",
                ],
                "steps": [
                    "Check for off-grid or obstacle first, then the start, then add up and left.",
                ],
                "why": [
                    "It walks every obstacle-free path: exponential.",
                ],
                "dry": [
                    "The centre (1, 1) is blocked.",
                    "The surviving paths go along the edges: right-right-down-down and down-down-right-right.",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache each cell's path count.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(m·n).",
                ],
                "dry": [
                    "f(2, 2) = f(1, 2) + f(2, 1) = 1 + 1.",
                    "Each of those has only one route, because the centre is 0.",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Fill row by row; obstacles become 0, and missing neighbours on the top row or left column count as 0.",
                ],
                "steps": [
                    "<code>dp[r][c] = up + left</code>, unless the cell is an obstacle.",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "Row 0: [1, 1, 1].",
                    "Row 1: [1, 0, 1] (the obstacle is 0).",
                    "Row 2: [1, 1, 2]. The result is <strong>2</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Start with a phantom row above the grid, [1, 0, 0], that feeds exactly one path into the start.",
                    "Then every cell, the start included, uses the same formula.",
                ],
                "steps": [
                    "<code>cur[c] = prev[c] + cur[c-1]</code> for free cells; obstacles stay 0.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Phantom [1, 0, 0] → [1, 1, 1] → [1, 0, 1] → [1, 1, 2].",
                    "The result is <strong>2</strong>.",
                ],
            },
            "One row, zero at obstacles": {
                "idea": [
                    "Use one row with the running-sum update, but set the row to 0 at an obstacle.",
                    "A 0 in column 0 then stays 0 for every row below, which is correct: nothing can get past it from above.",
                ],
                "steps": [
                    "<code>row[c] = 0</code> at an obstacle; otherwise <code>row[c] += row[c-1]</code> when c &gt; 0.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Start [1, 0, 0]. After row 0: [1, 1, 1].",
                    "After row 1: [1, 0, 1].",
                    "After row 2: [1, 1, 2]. The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum path sum
    "minimum-path-sum": {
        "example": {"call": "min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]])", "expect": "7"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "The cheapest way into (r, c) = its own cost + the cheaper of the best ways into the cell above and the cell to the left.",
                    "Off-grid cells are infinitely expensive, so they are never chosen.",
                ],
                "steps": [
                    "Base case: the start costs <code>grid[0][0]</code>.",
                ],
                "why": [
                    "It prices every path separately: exponential.",
                ],
                "dry": [
                    "The best path is 1 → 3 → 1 → 1 → 1 (right, right, down, down).",
                    "Its cost is <strong>7</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache each cell's best cost.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(m·n).",
                ],
                "dry": [
                    "f(1, 2) = 1 + min(f(0, 2) = 5, f(1, 1) = 7) = 6.",
                    "f(2, 2) = 1 + min(6, f(2, 1) = 8) = <strong>7</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Fill row by row; the start is the one cell with no finite neighbour.",
                ],
                "steps": [
                    "<code>dp[r][c] = grid[r][c] + min(up, left)</code>, with inf for a missing side.",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "Row 0: [1, 4, 5].",
                    "Row 1: [2, 7, 6].",
                    "Row 2: [6, 8, 7]. The result is <strong>7</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Use a phantom row [0, inf, inf] above the grid, so the start needs no special case.",
                ],
                "steps": [
                    "<code>cur[c] = cell + min(prev[c], cur[c-1])</code>.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "[0, inf, inf] → [1, 4, 5] → [2, 7, 6] → [6, 8, 7].",
                    "The result is <strong>7</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "<code>row[c]</code> before the update is \"above\", and <code>row[c-1]</code> after its update is \"left\".",
                    "Column 0 has only \"above\", so it just accumulates.",
                ],
                "steps": [
                    "<code>row[0] += cells[0]</code>; then <code>row[c] = cells[c] + min(row[c], row[c-1])</code>.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Row 0: [1, 4, 5]. Row 1: row[0] = 2, row[1] = 5 + min(4, 2) = 7, row[2] = 1 + min(5, 7) = 6.",
                    "Row 2: row[0] = 6, row[1] = 2 + min(7, 6) = 8, row[2] = 1 + min(6, 8) = 7.",
                    "The result is <strong>7</strong>.",
                ],
            },
            "In place": {
                "idea": [
                    "Overwrite each cell with its best cost; its neighbours above and to the left were already converted.",
                ],
                "steps": [
                    "Skip (0, 0); <code>grid[r][c] += min(up, left)</code>.",
                ],
                "why": [
                    "It uses O(1) extra space, but destroys the input. Mention that in an interview.",
                ],
                "dry": [
                    "The grid becomes [[1, 4, 5], [2, 7, 6], [6, 8, 7]].",
                    "The result is <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ triangle
    "triangle": {
        "example": {"call": "minimum_total([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]])", "expect": "11"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "From (r, i) you go to (r+1, i) or (r+1, i+1). The best path down = this cell + the better of the two below.",
                    "Working top-down from the apex means there is a single answer cell, f(0, 0), not a min over the base.",
                ],
                "steps": [
                    "<code>f(n, i) = 0</code>, past the base.",
                ],
                "why": [
                    "Two choices per row gives 2<sup>n-1</sup> paths.",
                ],
                "dry": [
                    "The best path is 2 → 3 → 5 → 1.",
                    "Its sum is <strong>11</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Neighbouring cells share a child: (1, 0) and (1, 1) both use (2, 1). Cache it.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n²), one computation per cell.",
                ],
                "dry": [
                    "f(2, 1) = 5 + min(1, 8) = 6 is computed once and used by both parents.",
                    "f(0, 0) = 2 + min(9, 10) = <strong>11</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Fill from the base upwards: row r needs only row r+1.",
                ],
                "steps": [
                    "<code>dp[r][i] = tri[r][i] + min(dp[r+1][i], dp[r+1][i+1])</code>.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "Base row: [4, 1, 8, 3].",
                    "Row 2: [6+1, 5+1, 7+3] = [7, 6, 10]. Row 1: [3+6, 4+6] = [9, 10].",
                    "Row 0: 2 + 9 = <strong>11</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only the row below; start it as a copy of the base row.",
                ],
                "steps": [
                    "Build each shorter row from <code>below</code>.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "[4, 1, 8, 3] → [7, 6, 10] → [9, 10] → [11].",
                    "The result is <strong>11</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "Cell i reads <code>best[i]</code> and <code>best[i+1]</code>. Going left to right, <code>best[i+1]</code> has not been overwritten yet, so it still holds the row below.",
                ],
                "steps": [
                    "<code>best[i] = tri[r][i] + min(best[i], best[i+1])</code>.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "best = [4, 1, 8, 3] → [7, 6, 10, 3] → [9, 10, 10, 3] → [11, …].",
                    "The result is <strong>11</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ dungeon game
    "dungeon-game": {
        "example": {"call": "calculate_minimum_hp([[-2, -3, 3], [-5, -10, 1], [10, 30, -5]])", "expect": "7"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Going forward fails: the best path so far can depend on health you have not met yet.",
                    "So work backwards: <code>need(r, c)</code> = the least health on entering (r, c) that is enough to finish alive.",
                    "need = max(1, min(need of down, need of right) - room). Health must never drop below 1.",
                ],
                "steps": [
                    "At the princess: <code>max(1, 1 - room)</code>; off the grid: inf.",
                ],
                "why": [
                    "It explores every path to the princess: exponential.",
                ],
                "dry": [
                    "The best route is right → right → down → down: -2, -3, +3, +1, -5.",
                    "Starting with 7: 5, 2, 5, 6, 1. Health stays ≥ 1.",
                    "The result is <strong>7</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>need(r, c)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on need.",
                ],
                "why": [
                    "It is O(m·n).",
                ],
                "dry": [
                    "need(0, 2) = max(1, 5 - 3) = 2, and need(0, 1) = max(1, min(11, 2) + 3) = 5.",
                    "need(0, 0) = max(1, min(6, 5) + 2) = <strong>7</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Pad the grid with an extra row and column of inf, except the two cells beside the princess, which are 1 (\"1 health after rescuing her\").",
                    "Fill from bottom-right to top-left.",
                ],
                "steps": [
                    "<code>need[r][c] = max(1, min(need[r+1][c], need[r][c+1]) - room)</code>.",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "Row 2 (right to left): 6, 1, 1.",
                    "Row 1: 5, 11, 6. Row 0: 2, 5, 7.",
                    "need[0][0] = <strong>7</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only the row below; it starts as the phantom row [inf, inf, 1, inf].",
                ],
                "steps": [
                    "Build each row right to left from <code>below</code> and the cell to the right.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Rows (left to right): [1, 1, 6] → [6, 11, 5] → [7, 5, 2].",
                    "The result is <strong>7</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "<code>need[c]</code> before the update is \"down\", and <code>need[c+1]</code> after its update is \"right\".",
                    "Reset the phantom column to inf after the first row; only the princess's row had a real exit there.",
                ],
                "steps": [
                    "Sweep right to left per row, from the bottom row upwards.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "After row 2: [1, 1, 6]. After row 1: [6, 11, 5].",
                    "After row 0: [7, 5, 2].",
                    "need[0] = <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum falling path sum
    "minimum-falling-path-sum": {
        "example": {"call": "min_falling_path_sum([[2, 1, 3], [6, 5, 4], [7, 8, 9]])", "expect": "13"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "The best path ending at (r, c) = its value + the best of the three cells above it (up-left, up, up-right).",
                    "The answer is the minimum over the bottom row.",
                ],
                "steps": [
                    "Off-grid columns are inf; row 0 returns its own value.",
                ],
                "why": [
                    "Three branches per row: O(n·3<sup>n</sup>).",
                ],
                "dry": [
                    "The best path is 1 → 5 → 7 (or 1 → 4 → 8).",
                    "Its sum is <strong>13</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache each cell's best value.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n²).",
                ],
                "dry": [
                    "Row 1 values: [7, 6, 5]. Row 2: 7 + 6 = 13, 8 + 5 = 13, 9 + 5 = 14.",
                    "The minimum is <strong>13</strong>.",
                ],
            },
            "One row at a time": {
                "idea": [
                    "Each row needs only the previous row.",
                    "Pad that row with inf on both sides so the edge columns need no special case.",
                ],
                "steps": [
                    "<code>prev = [x + min(three padded cells above)]</code> for each row.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                    "One row updated in place does not work here: both diagonals are read, so one of them would already be overwritten.",
                ],
                "dry": [
                    "prev = [2, 1, 3].",
                    "Row 1: [6+1, 5+1, 4+1] = [7, 6, 5]. Row 2: [7+6, 8+5, 9+5] = [13, 13, 14].",
                    "The minimum is <strong>13</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximal square
    "maximal-square": {
        "example": {"setup": 'M = [["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]',
                    "call": "maximal_square(M)", "expect": "4"},
        "approaches": {
            "Grow a square from every cell": {
                "idea": [
                    "Treat each cell as a top-left corner, and grow the side while the new bottom row and right column are all ones.",
                ],
                "steps": [
                    "Track the largest side; return its square.",
                ],
                "why": [
                    "The same cells are re-checked for every corner: O(m·n·k²).",
                ],
                "dry": [
                    "From (1, 2) the side grows to 2: rows 1–2, columns 2–3 are all ones.",
                    "Side 3 fails (row 3 has zeros).",
                    "The area is <strong>4</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>dp[r][c]</code> = the side of the largest all-ones square whose <em>bottom-right</em> corner is (r, c).",
                    "It is 1 + min(above, left, up-left): the smallest of those three squares limits how far this one can extend.",
                ],
                "steps": [
                    "Pad with a zero row and column; 0 cells stay 0.",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "dp rows: [1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 2, 2], [1, 0, 0, 1, 0].",
                    "(2, 3) = 1 + min(1, 1, 1) = 2.",
                    "The largest side is 2, so the area is <strong>4</strong>.",
                ],
            },
            "One row plus one saved diagonal": {
                "idea": [
                    "One row holds \"above\" before the write and \"left\" after it.",
                    "The up-left value is overwritten one step earlier, so save it in <code>diag</code> before writing.",
                ],
                "steps": [
                    "<code>above = row[c]</code>; compute <code>row[c]</code>; <code>diag = above</code>.",
                    "Reset <code>diag = 0</code> at the start of each row.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "At row 2, column 3: above = 1, left = 1, diag = 1, so row[3] = 2.",
                    "The best side is 2, so the area is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count square submatrices
    "count-square-submatrices": {
        "example": {"call": "count_squares([[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]])", "expect": "15"},
        "approaches": {
            "Check every square": {
                "idea": [
                    "Try every top-left corner and every size, and test every cell inside.",
                    "Stop growing at the first failure: a larger square contains the failed one.",
                ],
                "steps": [
                    "Count each size that passes.",
                ],
                "why": [
                    "It is O(m·n·k³).",
                ],
                "dry": [
                    "There are 10 size-1 squares (the ones), 4 of size 2 and 1 of size 3.",
                    "The total is <strong>15</strong>.",
                ],
            },
            "In-place DP": {
                "idea": [
                    "This is the Maximal Square recurrence: a cell with value k ends exactly k squares (sizes 1..k) at its bottom-right corner.",
                    "So the answer is the sum of all the dp values.",
                ],
                "steps": [
                    "For r, c ≥ 1, if the cell is 1: <code>cell = 1 + min(up, left, up-left)</code>.",
                    "Return the sum of the whole matrix.",
                ],
                "why": [
                    "It is O(m·n) time and O(1) extra space (it mutates the input).",
                ],
                "dry": [
                    "The matrix becomes [[0, 1, 1, 1], [1, 1, 2, 2], [0, 1, 2, 3]].",
                    "The cell with 3 ends squares of sizes 1, 2 and 3.",
                    "The sum is 3 + 6 + 6 = <strong>15</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest increasing path in a matrix
    "longest-increasing-path-in-a-matrix": {
        "example": {"call": "longest_increasing_path([[9, 9, 4], [6, 6, 8], [2, 1, 1]])", "expect": "4"},
        "approaches": {
            "Plain DFS from every cell": {
                "idea": [
                    "<code>f(r, c)</code> = the longest increasing path starting at (r, c) = 1 + the best f among the larger neighbours.",
                    "No visited set is needed: values strictly increase, so a path can never loop.",
                ],
                "steps": [
                    "Return the max of f over every cell.",
                ],
                "why": [
                    "The same tails are re-walked from every start: exponential in the worst case.",
                ],
                "dry": [
                    "From the 1 at (2, 1): 1 → 2 → 6 → 9.",
                    "The length is <strong>4</strong>.",
                ],
            },
            "Memoised DFS": {
                "idea": [
                    "The \"larger neighbour\" edges form a DAG (no cycles), so f(r, c) has a fixed answer. Cache it.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(m·n): each cell is computed once and checks 4 neighbours.",
                    "Recursion can go m·n deep.",
                ],
                "dry": [
                    "f grid: [[1, 1, 2], [2, 2, 1], [3, 4, 2]].",
                    "The maximum is f(2, 1) = <strong>4</strong>.",
                ],
            },
            "Bottom-up in decreasing value order": {
                "idea": [
                    "Process cells from the largest value to the smallest, so every larger neighbour is already final: a topological order made by sorting.",
                ],
                "steps": [
                    "Sort the cells in descending order of value; <code>f = 1 + max f of larger neighbours</code>.",
                ],
                "why": [
                    "It is O(m·n log(m·n)), with no recursion.",
                ],
                "dry": [
                    "The 9s get 1; 8 gets 1; 6 at (1, 0) gets 2 (from 9).",
                    "2 gets 3 (from 6); 1 at (2, 1) gets 4 (from 2).",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },
}
