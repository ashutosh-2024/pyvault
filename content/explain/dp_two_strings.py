"""Write-ups for Dynamic Programming, part 5: two-string problems."""

EXPLAIN = {
    # ------------------------------------------------------------------ LCS
    "longest-common-subsequence": {
        "examples": [
            {"call": 'longest_common_subsequence("abcde", "ace")', "expect": "3"},
            {"call": 'longest_common_subsequence("ab", "ba")', "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Let <code>f(i, j)</code> be the LCS length of the prefixes <code>a[:i]</code> and <code>b[:j]</code>. The answer is <code>f(len(a), len(b))</code>.",
                    "Look only at the last characters <code>a[i - 1]</code> and <code>b[j - 1]</code>. If they are equal, they can end the common subsequence together.",
                    "If they differ, at least one of them is not used, so drop one or the other and keep the better result.",
                ],
                "steps": [
                    "Base case: if <code>i == 0</code> or <code>j == 0</code>, one prefix is empty, so return 0.",
                    "If <code>a[i - 1] == b[j - 1]</code>, return <code>1 + f(i - 1, j - 1)</code>.",
                    "Otherwise return <code>max(f(i - 1, j), f(i, j - 1))</code>: skip the last letter of <code>a</code>, or of <code>b</code>.",
                    "Call <code>f(len(a), len(b))</code> and return its value.",
                ],
                "why": [
                    "On a match, pairing the two last letters is never worse than not pairing them, so taking 1 + f(i − 1, j − 1) is safe.",
                    "On a mismatch the two last letters cannot both be in the LCS paired with each other, so one of them is unused; the max covers both cases.",
                    "Every mismatch branches into two calls and the same <code>(i, j)</code> is reached along many paths, so the time is <strong>O(2<sup>m+n</sup>)</strong> in the worst case.",
                    "Each call shrinks i + j by at least 1, so the stack is at most m + n deep: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(5, 3): 'e' == 'e', so 1 + f(4, 2).",
                        "f(4, 2): 'd' ≠ 'c', so max(f(3, 2), f(4, 1)).",
                        "f(3, 2): 'c' == 'c', so 1 + f(2, 1); f(2, 1) = max(f(1, 1), f(2, 0)) = 1 from the 'a' match. f(3, 2) = 2.",
                        "f(4, 1) = 1, but it recomputes f(2, 1) through f(3, 1): 15 calls in all for only 24 possible states.",
                        "f(4, 2) = 2, so f(5, 3) = <strong>3</strong> (\"ace\").",
                    ],
                    [
                        "f(2, 2): 'b' ≠ 'a', so max(f(1, 2), f(2, 1)).",
                        "f(1, 2): 'a' == 'a', so 1 + f(0, 1) = 1.",
                        "f(2, 1): 'b' == 'b', so 1 + f(1, 0) = 1.",
                        "Both branches tie at 1: \"a\" or \"b\", never both, because the order is reversed.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not also try <code>f(i - 1, j - 1)</code> on a mismatch?",
                     "It is already covered: f(i − 1, j) ≥ f(i − 1, j − 1), because a longer prefix can only help. Adding it would not change the max."],
                    ["Why prefixes indexed by length instead of indices of characters?",
                     "Using lengths makes the empty prefix (length 0) a natural base case, so there is no −1 index to special-case."],
                    ["Where exactly is the repeated work?",
                     "Dropping a letter from <code>a</code> then from <code>b</code> reaches the same (i − 1, j − 1) as the other order. Those overlapping calls multiply at every level."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Change from plain recursion: add <code>@cache</code> to <code>f</code>. The recurrence is untouched.",
                    "<code>f(i, j)</code> depends only on <code>i</code> and <code>j</code>, so its value can be stored the first time and reused.",
                    "There are only (m + 1)(n + 1) different arguments, so the exponential tree collapses to that many real computations.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Same base case: <code>i == 0 or j == 0</code> returns 0.",
                    "Same match rule <code>1 + f(i - 1, j - 1)</code> and mismatch rule <code>max(f(i - 1, j), f(i, j - 1))</code>.",
                    "A repeated call returns the stored value instantly instead of recursing again.",
                    "Return <code>f(len(a), len(b))</code>.",
                ],
                "why": [
                    "Caching a pure function cannot change its results, so correctness is inherited from the plain recursion.",
                    "Each state is computed once with O(1) work outside its calls: <strong>O(m · n)</strong> time.",
                    "The cache holds up to (m + 1)(n + 1) values and the stack is up to m + n deep: <strong>O(m · n)</strong> space.",
                    "It only computes states the answer actually needs, which can be far fewer than the full table.",
                ],
                "dry": [
                    [
                        "Calls go f(5, 3) → f(4, 2) → f(3, 2) → f(2, 1) → f(1, 1) → f(0, 0), then f(2, 0); f(2, 1) = 1 is stored.",
                        "f(3, 2) = 2 is stored. f(4, 2) then needs f(4, 1) → f(3, 1).",
                        "f(3, 1) asks for f(2, 1): a cache hit, 1, with no further recursion.",
                        "f(4, 1) = 1, f(4, 2) = 2. Total: 12 calls and 11 states, against 15 calls before.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "f(2, 2) → f(1, 2) → f(0, 1) = 0, so f(1, 2) = 1.",
                        "f(2, 1) → f(1, 0) = 0, so f(2, 1) = 1.",
                        "No state is requested twice here, so the cache saves nothing on such a tiny input.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["What does <code>@cache</code> actually store?",
                     "A dictionary from the argument tuple <code>(i, j)</code> to the return value. Since <code>a</code> and <code>b</code> are fixed for one call of the outer function, (i, j) is a complete key."],
                    ["Why define <code>f</code> inside the function?",
                     "So each call of <code>longest_common_subsequence</code> gets a fresh cache. A module-level cached <code>f</code> would mix up results for different strings."],
                    ["Can the recursion depth be a problem?",
                     "Yes, for strings of a few thousand characters the depth m + n exceeds Python's default limit. The bottom-up table has no recursion."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Change from the memo: instead of recursing from the top and caching, fill every <code>dp[i][j] = f(i, j)</code> in an order where the needed cells already exist.",
                    "Each cell reads the cell above, the cell to the left and the up-left diagonal, so filling row by row, left to right, works.",
                    "Row 0 and column 0 are the empty-prefix base cases and stay 0.",
                ],
                "steps": [
                    "Create <code>dp</code> with m + 1 rows and n + 1 columns of zeros.",
                    "Loop <code>i</code> from 1 to m and <code>j</code> from 1 to n.",
                    "On <code>a[i - 1] == b[j - 1]</code>, set <code>dp[i][j] = 1 + dp[i - 1][j - 1]</code>.",
                    "Otherwise set <code>dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])</code>.",
                    "Return <code>dp[m][n]</code>.",
                ],
                "why": [
                    "This is the same recurrence, so each cell equals f(i, j); the loop order guarantees every cell it reads is final.",
                    "No recursion means no stack-depth limit and no function-call overhead.",
                    "(m + 1)(n + 1) cells at O(1) each: <strong>O(m · n)</strong> time and <strong>O(m · n)</strong> space.",
                    "Keeping the full table also lets you walk back from <code>dp[m][n]</code> to recover the subsequence itself.",
                ],
                "dry": [
                    [
                        "Row 'a': matches b[0] = 'a', so [0, 1, 1, 1].",
                        "Row 'b': no match, copies the max: [0, 1, 1, 1].",
                        "Row 'c': matches 'c' at j = 2: 1 + dp[2][1] = 2, giving [0, 1, 2, 2]. Row 'd': [0, 1, 2, 2].",
                        "Row 'e': matches 'e' at j = 3: 1 + dp[4][2] = 3, giving [0, 1, 2, 3].",
                        "dp[5][3] = <strong>3</strong>.",
                    ],
                    [
                        "Row 'a': j = 1 ('b') no match, 0; j = 2 ('a') match, 1 + dp[0][1] = 1. Row = [0, 0, 1].",
                        "Row 'b': j = 1 ('b') match, 1 + dp[1][0] = 1.",
                        "j = 2 ('a'): no match, max(dp[1][2], dp[2][1]) = max(1, 1) = 1.",
                        "dp[2][2] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why are the table dimensions (m + 1) × (n + 1)?",
                     "The extra row and column hold the empty-prefix cases, so <code>dp[i - 1][...]</code> and <code>dp[...][j - 1]</code> never go out of range."],
                    ["How do I recover the actual subsequence?",
                     "Start at (m, n). On a match step diagonally and record the letter; otherwise move to whichever of up or left holds the larger value. Reverse the recorded letters."],
                    ["Is bottom-up always faster than the memo?",
                     "Usually by a constant factor, since it avoids calls and hashing. But it fills every cell, even ones the memo would never have needed."],
                ],
            },
            "Two rows": {
                "idea": [
                    "Change from the full table: row i only reads row i − 1 and itself, so all older rows can be thrown away.",
                    "Keep <code>prev</code> (row i − 1) and build <code>cur</code> (row i); then <code>cur</code> becomes the new <code>prev</code>.",
                    "Memory drops from (m + 1)(n + 1) cells to two rows of n + 1.",
                ],
                "steps": [
                    "Set <code>prev = [0] * (n + 1)</code>, the all-zero row 0.",
                    "For each character <code>ch</code> of <code>a</code>, start <code>cur = [0] * (n + 1)</code>.",
                    "For j from 1 to n: on <code>ch == b[j - 1]</code>, <code>cur[j] = 1 + prev[j - 1]</code>; else <code>cur[j] = max(prev[j], cur[j - 1])</code>.",
                    "After the row, set <code>prev = cur</code>.",
                    "Return <code>prev[n]</code>.",
                ],
                "why": [
                    "<code>prev[j - 1]</code>, <code>prev[j]</code> and <code>cur[j - 1]</code> are exactly the table's up-left, up and left cells, so every value is the same as before.",
                    "Time is unchanged at <strong>O(m · n)</strong>. Space is two rows: <strong>O(n)</strong>.",
                    "The price is that the full table is gone, so the subsequence itself can no longer be traced back.",
                ],
                "dry": [
                    [
                        "prev = [0, 0, 0, 0].",
                        "ch = 'a': cur = [0, 1, 1, 1]. ch = 'b': cur = [0, 1, 1, 1].",
                        "ch = 'c': cur[2] = 1 + prev[1] = 2, so [0, 1, 2, 2]. ch = 'd': [0, 1, 2, 2].",
                        "ch = 'e': cur[3] = 1 + prev[2] = 3, so [0, 1, 2, 3].",
                        "It returns prev[3] = <strong>3</strong>.",
                    ],
                    [
                        "prev = [0, 0, 0].",
                        "ch = 'a': cur = [0, 0, 1]; prev = cur.",
                        "ch = 'b': cur[1] = 1 + prev[0] = 1; cur[2] = max(prev[2], cur[1]) = 1.",
                        "It returns prev[2] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is a fresh <code>cur</code> list created each row?",
                     "Writing into <code>prev</code> directly would destroy <code>prev[j - 1]</code> before the next cell reads it. The one-row version fixes that with a saved diagonal."],
                    ["Does <code>prev = cur</code> copy the list?",
                     "No, it just renames it, which is fine because a brand new <code>cur</code> is made at the start of the next row."],
                    ["Which string should index the columns?",
                     "The rows can be the longer string and the columns the shorter one, giving O(min(m, n)). The next approach does that swap."],
                ],
            },
            "One row plus the diagonal": {
                "idea": [
                    "Change from two rows: update one row in place. Before cell j is overwritten it still holds the old row's value (the \"above\" cell).",
                    "The only value lost is the up-left one, <code>dp[i - 1][j - 1]</code>, which was overwritten one step earlier. Save it in <code>diag</code> before overwriting.",
                    "Swapping so that <code>b</code> is the shorter string makes the row length min(m, n) + 1.",
                ],
                "steps": [
                    "If <code>b</code> is longer than <code>a</code>, swap them. Set <code>row = [0] * (len(b) + 1)</code>.",
                    "For each <code>ch</code> in <code>a</code>, set <code>diag = 0</code> (the up-left value for column 1).",
                    "For each j: save <code>above = row[j]</code> before writing.",
                    "Write <code>row[j] = diag + 1</code> on a match, else <code>max(above, row[j - 1])</code>.",
                    "Set <code>diag = above</code> for the next column. Return <code>row[-1]</code>.",
                ],
                "why": [
                    "When cell j is computed, <code>row[j - 1]</code> is already the new left value, <code>row[j]</code> is still the old above value, and <code>diag</code> holds the old <code>row[j - 1]</code>, the up-left value.",
                    "LCS is symmetric in its two strings, so the swap does not change the answer.",
                    "Time stays <strong>O(m · n)</strong>; space is one row of the shorter string: <strong>O(min(m, n))</strong>.",
                ],
                "dry": [
                    [
                        "\"ace\" is shorter, no swap. row = [0, 0, 0, 0].",
                        "ch = 'a': j = 1 matches, row[1] = diag + 1 = 1; then max fills the rest: [0, 1, 1, 1].",
                        "ch = 'b': [0, 1, 1, 1]. ch = 'c': at j = 2, diag = old row[1] = 1, so row[2] = 2: [0, 1, 2, 2].",
                        "ch = 'd': unchanged. ch = 'e': at j = 3, diag = old row[2] = 2, so row[3] = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "Equal lengths, no swap. row = [0, 0, 0].",
                        "ch = 'a': j = 1 no match, row[1] = 0, diag = 0; j = 2 match, row[2] = 0 + 1 = 1. row = [0, 0, 1].",
                        "ch = 'b': j = 1 match, row[1] = diag + 1 = 1, diag = 0; j = 2, row[2] = max(1, 1) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>diag</code> reset to 0 at the start of each row?",
                     "For column 1 the up-left cell is column 0 of the previous row, which is always 0 for LCS."],
                    ["Why save <code>above</code> before writing?",
                     "After the write <code>row[j]</code> holds the new value. The old one is needed both for the max and as the next column's diagonal."],
                    ["Is the swap required?",
                     "No, it only reduces memory. The result is the same either way."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ edit distance
    "edit-distance": {
        "examples": [
            {"call": 'min_distance("horse", "ros")', "expect": "3"},
            {"call": 'min_distance("ab", "ba")', "expect": "2"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Let <code>f(i, j)</code> be the fewest edits that turn <code>a[:i]</code> into <code>b[:j]</code>.",
                    "If the last letters match, they cost nothing: <code>f(i - 1, j - 1)</code>.",
                    "If not, the last edit is one of three: replace (i − 1, j − 1), delete from a (i − 1, j), or insert into a (i, j − 1). Pay 1 and take the cheapest.",
                ],
                "steps": [
                    "If <code>i == 0</code>, return <code>j</code>: insert every letter of <code>b[:j]</code>.",
                    "If <code>j == 0</code>, return <code>i</code>: delete every letter of <code>a[:i]</code>.",
                    "If <code>a[i - 1] == b[j - 1]</code>, return <code>f(i - 1, j - 1)</code>.",
                    "Else return <code>1 + min(f(i - 1, j - 1), f(i - 1, j), f(i, j - 1))</code>.",
                    "Call <code>f(len(a), len(b))</code>.",
                ],
                "why": [
                    "Any optimal edit sequence handles the last letters in one of those ways, so the minimum over the options is the true minimum.",
                    "When the letters match, keeping them is never worse than editing them, so no +1 branch is needed.",
                    "Each mismatch spawns three calls: <strong>O(3<sup>m+n</sup>)</strong> time in the worst case. The stack is at most m + n deep: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(5, 3): 'e' ≠ 's', so 1 + min(f(4, 2), f(4, 3), f(5, 2)).",
                        "f(4, 3): 's' == 's', so f(3, 2), which is 2 (horse's \"hor\" → \"ro\").",
                        "f(4, 2) = 3 and f(5, 2) = 4, each found by their own deep branching.",
                        "The whole tree makes 77 calls for only 24 distinct (i, j) pairs.",
                        "f(5, 3) = 1 + 2 = <strong>3</strong>: replace h→r, delete r, delete e.",
                    ],
                    [
                        "f(2, 2): 'b' ≠ 'a', so 1 + min(f(1, 1), f(1, 2), f(2, 1)).",
                        "f(1, 1): 'a' ≠ 'b', so 1 + min(f(0, 0), f(0, 1), f(1, 0)) = 1 + 0 = 1.",
                        "f(1, 2): 'a' == 'a', so f(0, 1) = 1. f(2, 1): 'b' == 'b', so f(1, 0) = 1.",
                        "All three options give 1, so f(2, 2) = 1 + 1 = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Which branch is insert and which is delete?",
                     "<code>f(i - 1, j)</code> uses up a letter of <code>a</code> without matching anything: a delete. <code>f(i, j - 1)</code> produces a letter of <code>b</code> from nothing: an insert."],
                    ["Why are the base cases <code>j</code> and <code>i</code> rather than 0?",
                     "Turning an empty string into <code>b[:j]</code> needs j inserts, and turning <code>a[:i]</code> into an empty string needs i deletes."],
                    ["Why is this marked for small inputs only?",
                     "Three-way branching explodes fast: \"horse\"/\"ros\" already needs 77 calls, and twenty-letter strings are out of reach."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Change from plain recursion: add <code>@cache</code> so each <code>(i, j)</code> is solved once.",
                    "The three-way branching then costs nothing extra, because every branch lands on a state that is either new or already cached.",
                    "The recurrence and base cases are identical.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Base cases: <code>i == 0</code> returns j, <code>j == 0</code> returns i.",
                    "Match: <code>f(i - 1, j - 1)</code>. Mismatch: <code>1 + min</code> of the three neighbours.",
                    "A repeated state returns from the cache at once.",
                    "Return <code>f(len(a), len(b))</code>.",
                ],
                "why": [
                    "Caching does not change any value, so it is correct for the same reason as the recursion.",
                    "There are (m + 1)(n + 1) states with O(1) work each: <strong>O(m · n)</strong> time.",
                    "The cache and the stack together are <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "The first branch of f(5, 3) goes f(4, 2) → f(3, 1) → f(2, 0) and fills states down to the base cases.",
                        "f(3, 2) = 2 is computed inside f(4, 2), then reused when f(4, 3) asks for it.",
                        "f(5, 2) reuses f(4, 1) and f(4, 2) from the cache.",
                        "Only 28 calls are made and 18 states are stored, against 77 calls before.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "f(2, 2) calls f(1, 1), which computes f(0, 0) = 0, f(0, 1) = 1, f(1, 0) = 1; f(1, 1) = 1.",
                        "f(1, 2) asks for f(0, 1): a cache hit, 1.",
                        "f(2, 1) asks for f(1, 0): a cache hit, 1.",
                        "9 calls, 7 states. f(2, 2) = 1 + 1 = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does memoisation help so much more here than for LCS?",
                     "Three branches overlap more heavily than two, so plain recursion repeats far more work, and the cache removes all of it."],
                    ["Does the order of the three calls matter?",
                     "Not for the answer. It only changes which states get computed first."],
                    ["What limits this version?",
                     "Recursion depth (up to m + n) and the cache's memory. The bottom-up versions remove both concerns."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Change from the memo: fill <code>dp[i][j] = f(i, j)</code> in loops instead of on demand.",
                    "Row 0 is 0, 1, 2, … (inserts) and column 0 is 0, 1, 2, … (deletes): the base cases written out.",
                    "Every other cell reads up, left and up-left, which a row-by-row fill has already computed.",
                ],
                "steps": [
                    "Create an (m + 1) × (n + 1) table <code>dp</code>.",
                    "Set <code>dp[i][0] = i</code> for every i and <code>dp[0][j] = j</code> for every j.",
                    "For i from 1 to m, j from 1 to n: on a match, <code>dp[i][j] = dp[i - 1][j - 1]</code>.",
                    "Otherwise <code>dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])</code>.",
                    "Return <code>dp[m][n]</code>.",
                ],
                "why": [
                    "Each cell is the recurrence applied to cells already final, so it equals f(i, j).",
                    "(m + 1)(n + 1) cells, O(1) each: <strong>O(m · n)</strong> time and <strong>O(m · n)</strong> space.",
                    "The full table lets you trace back which edit was chosen at each step.",
                ],
                "dry": [
                    [
                        "Row 0 = [0, 1, 2, 3]. Row 'h': no matches, [1, 1, 2, 3].",
                        "Row 'o': 'o' matches at j = 2, dp[2][2] = dp[1][1] = 1, giving [2, 2, 1, 2].",
                        "Row 'r': 'r' matches at j = 1, dp[3][1] = dp[2][0] = 2, giving [3, 2, 2, 2].",
                        "Row 's': 's' matches at j = 3, dp[4][3] = dp[3][2] = 2: [4, 3, 3, 2]. Row 'e': [5, 4, 4, 3].",
                        "dp[5][3] = <strong>3</strong>.",
                    ],
                    [
                        "Row 0 = [0, 1, 2].",
                        "Row 'a': j = 1 ('b') 1 + min(0, 1, 1) = 1; j = 2 ('a') match, dp[0][1] = 1. Row = [1, 1, 1].",
                        "Row 'b': j = 1 ('b') match, dp[1][0] = 1; j = 2 ('a') 1 + min(1, 1, 1) = 2.",
                        "dp[2][2] = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why initialise row 0 and column 0 separately?",
                     "They are the base cases. Leaving them 0 would claim that turning \"hor\" into \"\" costs nothing."],
                    ["On a match, could replacing still be better?",
                     "No. dp[i − 1][j − 1] ≤ dp[i − 1][j] + 1 and ≤ dp[i][j − 1] + 1 always holds, so keeping the matching letters is never worse."],
                    ["Is the distance symmetric?",
                     "Yes: insert and delete swap roles when the strings swap, and both cost 1. The tests check <code>min_distance(a, b) == min_distance(b, a)</code>."],
                ],
            },
            "Two rows": {
                "idea": [
                    "Change from the full table: row i reads only row i − 1, so keep just <code>prev</code> and <code>cur</code>.",
                    "Row 0 is <code>list(range(n + 1))</code>, and each new row starts with its column-0 value <code>i</code>.",
                    "The recurrence is unchanged; only the storage shrinks.",
                ],
                "steps": [
                    "Set <code>prev = list(range(n + 1))</code>.",
                    "For i from 1 to m, make <code>cur = [i] + [0] * n</code>.",
                    "For j from 1 to n: on a match <code>cur[j] = prev[j - 1]</code>.",
                    "Otherwise <code>cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])</code>.",
                    "Set <code>prev = cur</code> after each row; return <code>prev[n]</code>.",
                ],
                "why": [
                    "<code>prev[j - 1]</code>, <code>prev[j]</code>, <code>cur[j - 1]</code> are the up-left, up and left cells, so each value matches the table.",
                    "Time is still <strong>O(m · n)</strong>; space is two rows: <strong>O(n)</strong>.",
                    "The edit path can no longer be traced back, since earlier rows are discarded.",
                ],
                "dry": [
                    [
                        "prev = [0, 1, 2, 3].",
                        "i = 1 ('h'): cur = [1, 1, 2, 3]. i = 2 ('o'): cur = [2, 2, 1, 2].",
                        "i = 3 ('r'): cur = [3, 2, 2, 2]. i = 4 ('s'): cur = [4, 3, 3, 2].",
                        "i = 5 ('e'): cur = [5, 4, 4, 3].",
                        "It returns prev[3] = <strong>3</strong>.",
                    ],
                    [
                        "prev = [0, 1, 2].",
                        "i = 1 ('a'): cur = [1, 1, 1].",
                        "i = 2 ('b'): cur[1] = prev[0] = 1 (match); cur[2] = 1 + min(1, 1, 1) = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>cur</code> start with <code>i</code>?",
                     "That is <code>dp[i][0]</code>: turning <code>a[:i]</code> into an empty string takes i deletions."],
                    ["Could I reuse <code>prev</code> instead of allocating <code>cur</code>?",
                     "Only if you save the overwritten diagonal, which is exactly the next approach."],
                    ["Which string should be the columns?",
                     "The shorter one, to make the rows short. This code always uses <code>b</code>, so its space is O(len(b))."],
                ],
            },
            "One row plus the diagonal": {
                "idea": [
                    "Change from two rows: overwrite a single <code>row</code> in place, left to right.",
                    "Before cell j is written it still holds the up value; the left value is already new. Only the up-left value has been lost, so keep it in <code>diag</code>.",
                    "Column 0 is updated at the start of each row with <code>diag, row[0] = row[0], i</code>.",
                ],
                "steps": [
                    "Set <code>row = list(range(len(b) + 1))</code>.",
                    "For each i, save the old <code>row[0]</code> into <code>diag</code> and set <code>row[0] = i</code>.",
                    "For each j, save <code>above = row[j]</code>.",
                    "On a match set <code>row[j] = diag</code>; else <code>row[j] = 1 + min(diag, above, row[j - 1])</code>.",
                    "Set <code>diag = above</code>; after all rows return <code>row[-1]</code>.",
                ],
                "why": [
                    "At column j, <code>diag</code> is the old <code>row[j - 1]</code> (up-left), <code>above</code> the old <code>row[j]</code> (up), and <code>row[j - 1]</code> the new left value.",
                    "Those are the same three values the table uses, so the result is identical.",
                    "Time <strong>O(m · n)</strong>; one row plus two integers: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "row = [0, 1, 2, 3].",
                        "'h': diag = 0, row[0] = 1; no matches, row = [1, 1, 2, 3].",
                        "'o': diag = 1, row[0] = 2; at j = 2 'o' matches, row[2] = diag = old row[1] = 1. row = [2, 2, 1, 2].",
                        "'r': [3, 2, 2, 2]. 's': [4, 3, 3, 2]. 'e': [5, 4, 4, 3].",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "row = [0, 1, 2].",
                        "'a': diag = 0, row[0] = 1. j = 1: 1 + min(0, 1, 1) = 1, diag = 1. j = 2 match: row[2] = diag = 1. row = [1, 1, 1].",
                        "'b': diag = 1, row[0] = 2. j = 1 match: row[1] = 1, diag = 1. j = 2: 1 + min(1, 1, 1) = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>diag</code> not reset to 0 like in LCS?",
                     "Column 0 here is i − 1 in the previous row, not 0. <code>diag, row[0] = row[0], i</code> picks up that old value before overwriting it."],
                    ["What if I forget <code>diag = above</code>?",
                     "The next column would read a stale diagonal from further left and give wrong distances, typically too small."],
                    ["Is this better than two rows in practice?",
                     "It halves the memory and avoids a list allocation per row. The time is the same."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ distinct subsequences
    "distinct-subsequences": {
        "examples": [
            {"call": 'num_distinct("babgbag", "bag")', "expect": "5"},
            {"call": 'num_distinct("aaa", "aa")', "expect": "3"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Let <code>f(i, j)</code> be the number of ways to pick <code>t[:j]</code> as a subsequence of <code>s[:i]</code>.",
                    "The last letter <code>s[i - 1]</code> is either not used, giving <code>f(i - 1, j)</code> ways, or used to match <code>t[j - 1]</code>, which is only possible if they are equal and gives <code>f(i - 1, j - 1)</code> ways.",
                    "These two groups never overlap, so the counts add.",
                ],
                "steps": [
                    "If <code>j == 0</code>, return 1: the empty target is matched in exactly one way.",
                    "If <code>i == 0</code>, return 0: a non-empty target cannot come from an empty string.",
                    "Set <code>ways = f(i - 1, j)</code>, the ways that skip <code>s[i - 1]</code>.",
                    "If <code>s[i - 1] == t[j - 1]</code>, add <code>f(i - 1, j - 1)</code>.",
                    "Return <code>ways</code>; the answer is <code>f(len(s), len(t))</code>.",
                ],
                "why": [
                    "Every way of choosing positions either includes the last position of s or not; the two cases are disjoint and together cover everything.",
                    "The check <code>j == 0</code> comes first so that f(0, 0) = 1.",
                    "Each matching letter adds a second branch, so the call tree can grow like <strong>O(2<sup>m</sup>)</strong>. The depth is at most m: <strong>O(m)</strong> stack space.",
                ],
                "dry": [
                    [
                        "f(7, 3): 'g' == 'g', so f(6, 3) + f(6, 2).",
                        "f(6, 3): ways to get \"bag\" from \"babgba\" = 1 (only the first g works).",
                        "f(6, 2): ways to get \"ba\" from \"babgba\" = 4.",
                        "These subcalls overlap a lot: 34 calls for 24 possible states.",
                        "f(7, 3) = 1 + 4 = <strong>5</strong>.",
                    ],
                    [
                        "f(3, 2): 'a' == 'a', so f(2, 2) + f(2, 1).",
                        "f(2, 2) = f(1, 2) + f(1, 1) = 0 + 1 = 1.",
                        "f(2, 1) = f(1, 1) + f(1, 0) = 1 + 1 = 2. f(1, 1) is computed twice.",
                        "13 calls in all. f(3, 2) = 1 + 2 = <strong>3</strong>: positions (0,1), (0,2), (1,2).",
                    ],
                ],
                "faq": [
                    ["Why is f(i, 0) equal to 1 and not 0?",
                     "There is exactly one way to choose nothing. Returning 0 would make every count 0, since all counts are built from that base."],
                    ["Why not skip <code>t[j - 1]</code> on a mismatch, as in LCS?",
                     "Every letter of t must be matched. Only letters of s may be skipped."],
                    ["Can I stop early when <code>i &lt; j</code>?",
                     "Yes, there are then zero ways, and adding that check prunes many calls. The code does not, which keeps it closest to the recurrence."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Change from plain recursion: add <code>@cache</code>, so each count <code>f(i, j)</code> is computed once.",
                    "The counts can be huge, but they are computed from a fixed set of (m + 1)(n + 1) states.",
                    "The base cases and the skip/use recurrence are unchanged.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "<code>j == 0</code> returns 1, <code>i == 0</code> returns 0.",
                    "<code>ways = f(i - 1, j)</code>, plus <code>f(i - 1, j - 1)</code> when the letters match.",
                    "Repeated states come from the cache.",
                    "Return <code>f(len(s), len(t))</code>.",
                ],
                "why": [
                    "The cache only removes duplicate computation, so the counts are the same.",
                    "Each state does O(1) work: <strong>O(m · n)</strong> time.",
                    "The cache stores up to (m + 1)(n + 1) values: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(7, 3) first follows the skip chain f(6, 3), f(5, 3), …, f(0, 3) = 0.",
                        "On the way back, matches open f(i − 1, j − 1) branches, such as f(3, 2) for the g at index 3.",
                        "Later branches such as f(6, 2) reuse f(4, 2) and others from the cache.",
                        "26 calls and 24 states, against 34 calls before.",
                        "f(7, 3) = 1 + 4 = <strong>5</strong>.",
                    ],
                    [
                        "f(3, 2) → f(2, 2) → f(1, 2) → f(0, 2) = 0, and f(1, 1) = 1, so f(2, 2) = 1.",
                        "f(2, 1) needs f(1, 1): a cache hit, 1. Plus f(1, 0) = 1, so 2.",
                        "11 calls, 9 states.",
                        "f(3, 2) = 1 + 2 = <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why are the savings small on these examples?",
                     "The inputs are tiny. On something like s = \"a\" × 30, t = \"a\" × 15, plain recursion makes hundreds of millions of calls while the memo needs a few hundred."],
                    ["Do the counts overflow?",
                     "Not in Python. LeetCode guarantees the answer fits in 32 bits, but intermediate counts in other languages may need 64-bit or modular arithmetic."],
                    ["Is the order of the two terms important?",
                     "No, addition is commutative. Computing the skip term first just mirrors the recurrence as written."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Change from the memo: fill <code>dp[i][j] = f(i, j)</code> with loops, row by row.",
                    "Column 0 is all 1s (the empty target); row 0 is 0 elsewhere.",
                    "Each cell copies the cell above and, on a match, adds the up-left cell.",
                ],
                "steps": [
                    "Create an (m + 1) × (n + 1) table of zeros, then set <code>dp[i][0] = 1</code> for every i.",
                    "For i from 1 to m and j from 1 to n: <code>dp[i][j] = dp[i - 1][j]</code>.",
                    "If <code>s[i - 1] == t[j - 1]</code>, add <code>dp[i - 1][j - 1]</code>.",
                    "Return <code>dp[m][n]</code>.",
                ],
                "why": [
                    "Row i reads only row i − 1, which is complete, so every cell equals f(i, j).",
                    "(m + 1)(n + 1) cells at O(1): <strong>O(m · n)</strong> time and <strong>O(m · n)</strong> space.",
                    "There is no recursion, so long strings do not hit the depth limit.",
                ],
                "dry": [
                    [
                        "Columns are \"\", b, ba, bag. Row 0 = [1, 0, 0, 0].",
                        "'b': [1, 1, 0, 0]. 'a': [1, 1, 1, 0]. 'b': [1, 2, 1, 0].",
                        "'g': [1, 2, 1, 1]. 'b': [1, 3, 1, 1].",
                        "'a': dp[6][2] = 1 + 3 = 4, so [1, 3, 4, 1]. 'g': dp[7][3] = 1 + 4 = 5.",
                        "dp[7][3] = <strong>5</strong>.",
                    ],
                    [
                        "Row 0 = [1, 0, 0].",
                        "First 'a': [1, 1, 0].",
                        "Second 'a': [1, 2, 1].",
                        "Third 'a': dp[3][1] = 2 + 1 = 3, dp[3][2] = 1 + 2 = 3. dp[3][2] = <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>dp[0][0]</code> 1?",
                     "Matching an empty target in an empty string is one way: choose nothing."],
                    ["Can row i be read as a meaning?",
                     "Yes: <code>dp[i][j]</code> is how many ways the first i letters of s spell the first j letters of t."],
                    ["Why is the inner loop allowed to run over all j even when j &gt; i?",
                     "Those cells simply stay 0, which is correct: a shorter string cannot contain a longer one."],
                ],
            },
            "Two rows": {
                "idea": [
                    "Change from the table: only row i − 1 is ever read, so keep <code>prev</code> and build <code>cur</code>.",
                    "Every cell starts as the one above it, so <code>cur</code> can begin as a copy of <code>prev</code>.",
                    "Then only matching positions need an addition.",
                ],
                "steps": [
                    "Set <code>prev = [1] + [0] * len(t)</code>.",
                    "For each letter <code>ch</code> of <code>s</code>, set <code>cur = prev[:]</code> (the skip case).",
                    "For j from 1 to n: if <code>t[j - 1] == ch</code>, do <code>cur[j] += prev[j - 1]</code>.",
                    "Set <code>prev = cur</code>.",
                    "Return <code>prev[-1]</code>.",
                ],
                "why": [
                    "<code>cur[j]</code> becomes <code>prev[j] + prev[j - 1]</code> on a match and <code>prev[j]</code> otherwise, which is the table recurrence.",
                    "The additions read only <code>prev</code>, which is never modified, so order inside the row does not matter.",
                    "<strong>O(m · n)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "prev = [1, 0, 0, 0].",
                        "'b': [1, 1, 0, 0]. 'a': [1, 1, 1, 0]. 'b': [1, 2, 1, 0].",
                        "'g': [1, 2, 1, 1]. 'b': [1, 3, 1, 1].",
                        "'a': cur[2] = 1 + 3 = 4, [1, 3, 4, 1]. 'g': cur[3] = 1 + 4 = 5.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "prev = [1, 0, 0].",
                        "'a': cur = [1, 1, 0].",
                        "'a': cur = [1, 2, 1].",
                        "'a': cur[1] = 2 + 1 = 3, cur[2] = 1 + 2 = 3. It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>prev[:]</code> and not <code>prev</code>?",
                     "Without the copy, <code>cur</code> and <code>prev</code> are the same list, and the additions would read values already updated in this row."],
                    ["Why can the matched letters add <code>prev[j - 1]</code> and not <code>cur[j - 1]</code>?",
                     "Using the current letter twice is not allowed. <code>prev[j - 1]</code> counts matches of <code>t[:j-1]</code> that end before this letter."],
                    ["Is there a further saving?",
                     "Yes: updating a single list from right to left makes the copy unnecessary, as in the next approach."],
                ],
            },
            "One row, j downwards": {
                "idea": [
                    "Change from two rows: update a single list <code>ways</code> in place, with no copy.",
                    "The update <code>ways[j] += ways[j - 1]</code> must read the old <code>ways[j - 1]</code>. Going from high j to low j means <code>ways[j - 1]</code> has not been touched yet this round.",
                    "This is the same trick as the 0/1 knapsack one-row version: each letter of s is used at most once.",
                ],
                "steps": [
                    "Set <code>ways = [1] + [0] * len(t)</code>.",
                    "For each letter <code>ch</code> of <code>s</code>:",
                    "Loop j from <code>len(t)</code> down to 1.",
                    "If <code>t[j - 1] == ch</code>, do <code>ways[j] += ways[j - 1]</code>.",
                    "Return <code>ways[-1]</code>.",
                ],
                "why": [
                    "When j is processed, <code>ways[j]</code> and <code>ways[j - 1]</code> both still hold row i − 1 values, so the update is exactly the recurrence.",
                    "Cells with no match are left alone, which is the \"skip\" case for free.",
                    "<strong>O(m · n)</strong> time; one list of n + 1: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "ways = [1, 0, 0, 0].",
                        "'b': [1, 1, 0, 0]. 'a': [1, 1, 1, 0]. 'b': ways[1] += 1, [1, 2, 1, 0].",
                        "'g': ways[3] += ways[2], [1, 2, 1, 1]. 'b': [1, 3, 1, 1].",
                        "'a': ways[2] += ways[1] = 1 + 3 = 4. 'g': ways[3] += ways[2] = 1 + 4 = 5.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "ways = [1, 0, 0].",
                        "First 'a': j = 2 adds ways[1] = 0, then j = 1 adds ways[0]: [1, 1, 0].",
                        "Second 'a': j = 2 adds the old ways[1] = 1, then j = 1: [1, 2, 1].",
                        "Third 'a': ways[2] = 1 + 2 = 3, ways[1] = 2 + 1 = 3. It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong if j goes upwards?",
                     "<code>ways[j - 1]</code> would already include the current letter, so one letter could match two positions of t. On \"aaa\", \"aa\" an upward loop returns 6 instead of 3."],
                    ["Why does this match the two-row result exactly?",
                     "Going downwards, every read is of a cell not yet written this round, so it is the previous row's value, just as in <code>prev</code>."],
                    ["Is this the version to give in an interview?",
                     "Yes, once the table is explained. State that the downward loop is what keeps each letter used once."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest palindromic subsequence
    "longest-palindromic-subsequence": {
        "examples": [
            {"call": 'longest_palindrome_subseq("bbbab")', "expect": "4"},
            {"call": 'longest_palindrome_subseq("cbbd")', "expect": "2"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Let <code>f(i, j)</code> be the longest palindromic subsequence inside <code>s[i..j]</code>. The two ends decide everything.",
                    "If <code>s[i] == s[j]</code>, they can be the outer pair of the palindrome: 2 plus the best inside.",
                    "Otherwise at least one end is unused, so drop the left end or the right end and keep the better result.",
                ],
                "steps": [
                    "If <code>i &gt; j</code>, the range is empty: return 0.",
                    "If <code>i == j</code>, one letter is a palindrome: return 1.",
                    "If <code>s[i] == s[j]</code>, return <code>2 + f(i + 1, j - 1)</code>.",
                    "Otherwise return <code>max(f(i + 1, j), f(i, j - 1))</code>.",
                    "Call <code>f(0, len(s) - 1)</code>.",
                ],
                "why": [
                    "With matching ends, some longest palindrome can use both, since swapping its outer letters for these ends never shortens it.",
                    "With different ends they cannot pair with each other, so one is unused and the max covers both choices.",
                    "Mismatches branch in two: <strong>O(2<sup>n</sup>)</strong> time in the worst case. The range shrinks each call, so the depth is at most n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(0, 4): 'b' == 'b', so 2 + f(1, 3).",
                        "f(1, 3): 'b' ≠ 'a', so max(f(2, 3), f(1, 2)).",
                        "f(2, 3): 'b' ≠ 'a', max(f(3, 3), f(2, 2)) = 1. f(1, 2): 'b' == 'b', 2 + f(2, 1) = 2 + 0 = 2.",
                        "f(1, 3) = 2, so f(0, 4) = 2 + 2 = <strong>4</strong> (\"bbbb\"). 7 calls.",
                    ],
                    [
                        "f(0, 3): 'c' ≠ 'd', so max(f(1, 3), f(0, 2)).",
                        "f(1, 3): 'b' ≠ 'd', max(f(2, 3) = 1, f(1, 2) = 2 + f(2, 1) = 2) = 2.",
                        "f(0, 2): 'c' ≠ 'b', max(f(1, 2), f(0, 1)). f(1, 2) is computed a second time: 2.",
                        "13 calls in all. f(0, 3) = <strong>2</strong> (\"bb\").",
                    ],
                ],
                "faq": [
                    ["Why are there two base cases?",
                     "<code>i == j</code> is a single letter (length 1). <code>i &gt; j</code> appears after peeling a matching pair from a range of length 2, like f(2, 1), and is empty."],
                    ["How is this different from longest palindromic substring?",
                     "A subsequence may skip letters, so \"bbbab\" gives \"bbbb\" (4), while the longest substring is \"bbb\" (3)."],
                    ["Why does the state use i and j, not prefix lengths?",
                     "A palindrome is defined by both ends, so the natural subproblem is a range, not a prefix of one string."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Change from plain recursion: add <code>@cache</code>, so each range <code>(i, j)</code> is solved once.",
                    "There are about n²/2 ranges, so the exponential tree becomes quadratic.",
                    "Base cases and recurrence are the same.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                    "Empty range returns 0, single letter returns 1.",
                    "Matching ends: <code>2 + f(i + 1, j - 1)</code>; else the max of dropping either end.",
                    "Return <code>f(0, len(s) - 1)</code>.",
                ],
                "why": [
                    "Caching does not change values, so it is correct for the same reasons.",
                    "O(n²) ranges at O(1) work each: <strong>O(n²)</strong> time.",
                    "The cache holds O(n²) values; the stack is O(n): <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "f(0, 4) → f(1, 3) → f(2, 3) → f(3, 3) = 1 and f(2, 2) = 1.",
                        "f(1, 2) → f(2, 1) = 0, so f(1, 2) = 2.",
                        "No range is requested twice here, so the memo makes the same 7 calls.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "f(0, 3) → f(1, 3), which stores f(2, 3) = 1 and f(1, 2) = 2; f(1, 3) = 2.",
                        "f(0, 2) asks for f(1, 2): a cache hit, 2, skipping its subcall.",
                        "f(0, 1) = max(f(1, 1), f(0, 0)) = 1, so f(0, 2) = 2.",
                        "12 calls instead of 13. It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the cache not help on \"bbbab\"?",
                     "The matching outer letters shrink both ends at once, so the paths never cross. On strings with many mismatches the overlap is large."],
                    ["How many distinct states are there?",
                     "Ranges with i ≤ j, about n²/2, plus a few empty ranges reached from matching pairs."],
                    ["What is the depth limit risk?",
                     "The depth is at most n, so strings of a few thousand letters can exceed Python's recursion limit."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Change from the memo: fill <code>dp[i][j]</code> for all ranges, smallest-first.",
                    "<code>dp[i][j]</code> reads <code>dp[i + 1][...]</code> (a row below) and <code>dp[i][j - 1]</code> (to the left). So rows go from <code>i = n - 1</code> up to 0, and within a row j goes left to right.",
                    "The diagonal <code>dp[i][i]</code> is 1; cells below the diagonal (empty ranges) stay 0.",
                ],
                "steps": [
                    "Create an n × n table of zeros.",
                    "Loop <code>i</code> from n − 1 down to 0, setting <code>dp[i][i] = 1</code>.",
                    "Loop <code>j</code> from i + 1 to n − 1.",
                    "If <code>s[i] == s[j]</code>, <code>dp[i][j] = 2 + dp[i + 1][j - 1]</code>; else <code>max(dp[i + 1][j], dp[i][j - 1])</code>.",
                    "Return <code>dp[0][n - 1]</code>.",
                ],
                "why": [
                    "Each cell reads row i + 1, already finished, and the cell to its left, already filled this row, so all inputs are final.",
                    "For j = i + 1 with matching letters, <code>dp[i + 1][i]</code> is an empty range and correctly 0.",
                    "n²/2 cells at O(1): <strong>O(n²)</strong> time and <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "i = 4: [_, _, _, _, 1]. i = 3: dp[3][4] = max(1, 1) = 1 ('a' ≠ 'b').",
                        "i = 2: dp[2][3] = 1; dp[2][4] = 2 + dp[3][3] = 3 ('b' == 'b').",
                        "i = 1: dp[1][2] = 2; dp[1][3] = 2; dp[1][4] = 2 + dp[2][3] = 3.",
                        "i = 0: dp[0][1] = 2, dp[0][2] = 3, dp[0][3] = 3, dp[0][4] = 2 + dp[1][3] = 4.",
                        "dp[0][4] = <strong>4</strong>.",
                    ],
                    [
                        "i = 3: dp[3][3] = 1. i = 2: dp[2][3] = 1 ('b' ≠ 'd').",
                        "i = 1: dp[1][2] = 2 + 0 = 2 ('b' == 'b'); dp[1][3] = max(1, 2) = 2.",
                        "i = 0: dp[0][1] = 1, dp[0][2] = 2, dp[0][3] = max(dp[1][3], dp[0][2]) = 2.",
                        "dp[0][3] = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does i go downwards?",
                     "Row i needs row i + 1 finished. Filling top-down would read rows that are still all zeros."],
                    ["Could I fill by range length instead?",
                     "Yes, looping over lengths 1..n also works. Reverse row order is simpler and lets the table shrink to one row later."],
                    ["What about the cells below the diagonal?",
                     "They represent empty ranges, and their value 0 is read only when two adjacent letters match."],
                ],
            },
            "Two rows": {
                "idea": [
                    "Change from the table: row i reads only row i + 1, so keep that row as <code>below</code> and build <code>cur</code>.",
                    "Each new row starts with <code>cur[i] = 1</code> for the single-letter range.",
                    "When the row is done it becomes <code>below</code> for the next i.",
                ],
                "steps": [
                    "Set <code>below = [0] * n</code>.",
                    "For i from n − 1 down to 0: <code>cur = [0] * n</code> and <code>cur[i] = 1</code>.",
                    "For j from i + 1: on a match <code>cur[j] = 2 + below[j - 1]</code>; else <code>max(below[j], cur[j - 1])</code>.",
                    "Set <code>below = cur</code>.",
                    "Return <code>below[n - 1]</code>.",
                ],
                "why": [
                    "<code>below[j - 1]</code>, <code>below[j]</code> and <code>cur[j - 1]</code> are exactly dp[i + 1][j − 1], dp[i + 1][j] and dp[i][j − 1].",
                    "Time stays <strong>O(n²)</strong>; space falls to two rows: <strong>O(n)</strong>.",
                    "Entries left of i in <code>cur</code> stay 0, matching the empty ranges of the table.",
                ],
                "dry": [
                    [
                        "i = 4: below = [0, 0, 0, 0, 1].",
                        "i = 3: [0, 0, 0, 1, 1]. i = 2: [0, 0, 1, 1, 3].",
                        "i = 1: [0, 1, 2, 2, 3].",
                        "i = 0: [1, 2, 3, 3, 4].",
                        "It returns below[4] = <strong>4</strong>.",
                    ],
                    [
                        "i = 3: [0, 0, 0, 1]. i = 2: [0, 0, 1, 1].",
                        "i = 1: cur[2] = 2 + below[1] = 2; cur[3] = max(1, 2) = 2. [0, 1, 2, 2].",
                        "i = 0: [1, 1, 2, 2].",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>below</code> all zeros at the start?",
                     "It plays the role of row n, which only contains empty ranges."],
                    ["Does <code>below[j - 1]</code> ever read a stale value?",
                     "For j = i + 1 it reads <code>below[i]</code>, which is 0 because row i + 1 only fills from column i + 1. That is the empty range, as required."],
                    ["Why not just the one-row version?",
                     "Two rows are easier to reason about. The one-row version saves one list but needs the saved diagonal."],
                ],
            },
            "One row plus the diagonal": {
                "idea": [
                    "Change from two rows: overwrite one <code>row</code> in place. Before writing, <code>row[j]</code> still holds row i + 1's value.",
                    "The value <code>dp[i + 1][j - 1]</code> was overwritten one step earlier, so carry it in <code>diag</code>.",
                    "At the start of row i, <code>diag = 0</code> stands for the empty range f(i + 1, i).",
                ],
                "steps": [
                    "Set <code>row = [0] * n</code>.",
                    "For i from n − 1 down to 0: <code>diag = 0</code> and <code>row[i] = 1</code>.",
                    "For each j &gt; i, save <code>above = row[j]</code>.",
                    "Write <code>row[j] = diag + 2</code> on a match, else <code>max(above, row[j - 1])</code>.",
                    "Set <code>diag = above</code>; return <code>row[n - 1]</code>.",
                ],
                "why": [
                    "At column j, <code>above</code> is f(i + 1, j), <code>row[j - 1]</code> is the new f(i, j − 1), and <code>diag</code> is the old <code>row[j - 1]</code>, f(i + 1, j − 1).",
                    "Overwriting <code>row[i]</code> with 1 is safe: the old value is f(i + 1, i) = 0, which is what <code>diag</code> starts as.",
                    "<strong>O(n²)</strong> time and a single row: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i = 4: row = [0, 0, 0, 0, 1].",
                        "i = 3: row[3] = 1; j = 4: 'a' ≠ 'b', max(1, 1) = 1.",
                        "i = 2: row[2] = 1; j = 3: 1; j = 4: match, diag = old row[3] = 1, so 3. row = [0, 0, 1, 1, 3].",
                        "i = 1: row becomes [0, 1, 2, 2, 3]. i = 0: [1, 2, 3, 3, 4].",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "i = 3: row = [0, 0, 0, 1]. i = 2: [0, 0, 1, 1].",
                        "i = 1: row[1] = 1; j = 2 matches, diag = old row[1] = 0, so 2; j = 3: max(1, 2) = 2.",
                        "i = 0: no matches, row = [1, 1, 2, 2].",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>diag</code> reset to 0 for each row?",
                     "For j = i + 1 the diagonal is f(i + 1, i), an empty range, so 0."],
                    ["Doesn't <code>row[i] = 1</code> destroy something needed?",
                     "Its old value was f(i + 1, i) = 0, and the only reader of that value is the first diagonal, which is already 0."],
                    ["Is this the same trick as in LCS?",
                     "Yes: one row overwritten left to right, plus a variable for the up-left cell. Only the direction of i differs."],
                ],
            },
            "LCS of the string and its reverse": {
                "idea": [
                    "A palindromic subsequence of s reads the same backwards, so it is also a subsequence of <code>s[::-1]</code>.",
                    "The longest one is therefore the <strong>longest common subsequence</strong> of s and its reverse.",
                    "This reuses the one-row LCS code with <code>r = s[::-1]</code>.",
                ],
                "steps": [
                    "Set <code>r = s[::-1]</code> and <code>row = [0] * (len(r) + 1)</code>.",
                    "For each <code>ch</code> in <code>s</code>, set <code>diag = 0</code>.",
                    "For each j, save <code>above = row[j]</code>.",
                    "Write <code>diag + 1</code> on <code>ch == r[j - 1]</code>, else <code>max(above, row[j - 1])</code>; then <code>diag = above</code>.",
                    "Return <code>row[-1]</code>.",
                ],
                "why": [
                    "Every palindromic subsequence is common to s and r. Conversely, the LCS of s and r always has the same length as some palindromic subsequence (a standard result), so the lengths agree.",
                    "The LCS loop is n × n cells: <strong>O(n²)</strong> time.",
                    "One row plus the reversed copy: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "r = \"babbb\". row = [0] * 6.",
                        "ch = 'b': [0, 1, 1, 1, 1, 1]. ch = 'b': [0, 1, 1, 2, 2, 2].",
                        "ch = 'b': [0, 1, 1, 2, 3, 3]. ch = 'a': [0, 1, 2, 2, 3, 3].",
                        "ch = 'b': [0, 1, 2, 3, 3, 4].",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "r = \"dbbc\". row = [0] * 5.",
                        "ch = 'c': [0, 0, 0, 0, 1]. ch = 'b': [0, 0, 1, 1, 1].",
                        "ch = 'b': [0, 0, 1, 2, 2]. ch = 'd': [0, 1, 1, 2, 2].",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Is any common subsequence of s and its reverse a palindrome?",
                     "Not necessarily: for some strings the LCS found can be a non-palindrome. Its <em>length</em> always equals the longest palindromic subsequence, which is all this problem asks for."],
                    ["Is this slower than the direct DP?",
                     "It fills n² cells instead of n²/2, so about twice the work, with the same O(n²) bound."],
                    ["When is this the better choice?",
                     "When you already have a trusted LCS function: it turns a new problem into a known one with one line."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ interleaving string
    "interleaving-string": {
        "examples": [
            {"call": 'is_interleave("ab", "ac", "acab")', "expect": "True"},
            {"call": 'is_interleave("ab", "ba", "aabb")', "expect": "False"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Let <code>f(i, j)</code> say whether <code>s1[:i]</code> and <code>s2[:j]</code> can be interleaved to form <code>s3[:i + j]</code>.",
                    "The last letter <code>s3[i + j - 1]</code> must be the last letter of one of the two prefixes. Try taking it from <code>s1</code>, then from <code>s2</code>.",
                    "If the lengths do not add up, the answer is False immediately.",
                ],
                "steps": [
                    "Return False if <code>len(s1) + len(s2) != len(s3)</code>.",
                    "Base case: <code>f(0, 0)</code> is True (empty makes empty).",
                    "Let <code>k = i + j - 1</code>. If <code>i &gt; 0</code>, <code>s1[i - 1] == s3[k]</code> and <code>f(i - 1, j)</code>, return True.",
                    "Otherwise return <code>j &gt; 0 and s2[j - 1] == s3[k] and f(i, j - 1)</code>.",
                    "Call <code>f(len(s1), len(s2))</code>.",
                ],
                "why": [
                    "Any interleaving ends with a letter from s1 or from s2, so trying both covers every case.",
                    "<code>and</code> short-circuits: a branch whose letter does not match is never explored.",
                    "When both letters match, both branches may run, so the worst case is <strong>O(2<sup>m+n</sup>)</strong> time. Depth is at most m + n: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "Lengths 2 + 2 = 4, fine. f(2, 2): k = 3, s3[3] = 'b' and s1[1] = 'b', so try f(1, 2).",
                        "f(1, 2): k = 2, s3[2] = 'a' = s1[0], so try f(0, 2).",
                        "f(0, 2): i = 0, so s2[1] = 'c' must equal s3[1] = 'c': try f(0, 1).",
                        "f(0, 1): s2[0] = 'a' = s3[0], so f(0, 0) = True.",
                        "True propagates up: <strong>True</strong> (s3 = a, c from s2 then a, b from s1).",
                    ],
                    [
                        "Lengths 2 + 2 = 4, fine. f(2, 2): k = 3, s3[3] = 'b' = s1[1], try f(1, 2).",
                        "f(1, 2): k = 2, s3[2] = 'b'; s1[0] = 'a' and s2[1] = 'a' both differ, so False.",
                        "Back in f(2, 2): s2[1] = 'a' ≠ 'b', so that branch is skipped too.",
                        "It returns <strong>False</strong> after only 2 calls.",
                    ],
                ],
                "faq": [
                    ["Why check the lengths first?",
                     "Without it, f could succeed using all of s3's prefix but not all of s3 (or run out of s3). The length check makes f(m, n) cover exactly s3."],
                    ["Why can't I greedily take from s1 whenever it matches?",
                     "When both strings offer the same letter the choice matters. On \"aabcc\", \"dbbca\", \"aadbbcbcac\" a fixed preference fails where backtracking succeeds."],
                    ["Why is <code>k = i + j - 1</code>?",
                     "The prefixes together have i + j letters, so the last one in s3 is at index i + j − 1."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Change from plain recursion: add <code>@cache</code>. A state <code>(i, j)</code> reached by two different paths is now solved once.",
                    "That matters when both strings offer the same letter repeatedly and the branches keep meeting.",
                    "The length check stays outside the cached function.",
                ],
                "steps": [
                    "Return False if the lengths do not add up.",
                    "Decorate <code>f</code> with <code>@cache</code>; <code>f(0, 0)</code> is True.",
                    "Try the s1 branch, then the s2 branch, as before.",
                    "A repeated state returns its cached True or False.",
                    "Return <code>f(len(s1), len(s2))</code>.",
                ],
                "why": [
                    "The cache does not change any result, so correctness carries over.",
                    "(m + 1)(n + 1) states with O(1) work each: <strong>O(m · n)</strong> time.",
                    "The cache and the stack: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "The calls are the same as the plain recursion: f(2, 2) → f(1, 2) → f(0, 2) → f(0, 1) → f(0, 0).",
                        "Each state is stored as True on the way back.",
                        "No state was asked for twice, so the cache made no difference here.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "f(2, 2) → f(1, 2), which is False and stored.",
                        "The s2 branch of f(2, 2) fails on the letter check.",
                        "f(2, 2) = False is stored.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["When does the memo actually save work?",
                     "When a failing state is reachable in several ways, e.g. many equal letters in s1 and s2. Without the cache each path re-explores it."],
                    ["Why does the cache store False results too?",
                     "Re-proving that a state fails is exactly the repeated work that makes the plain version exponential."],
                    ["Why is the length check outside <code>f</code>?",
                     "It is a property of the whole input, checked once. Inside, every state already has k within s3."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Change from the memo: fill a boolean table <code>ok[i][j] = f(i, j)</code> for every state, row by row.",
                    "<code>ok[i][j]</code> is True if it can be reached from above (last letter from s1) or from the left (last letter from s2).",
                    "<code>ok[0][0] = True</code> is the only seed.",
                ],
                "steps": [
                    "Return False on a length mismatch; create <code>ok</code> of size (m + 1) × (n + 1), set <code>ok[0][0] = True</code>.",
                    "Loop i from 0 to m and j from 0 to n, skipping (0, 0).",
                    "Let <code>k = i + j - 1</code>; <code>from_s1 = i &gt; 0 and ok[i - 1][j] and s1[i - 1] == s3[k]</code>.",
                    "<code>from_s2 = j &gt; 0 and ok[i][j - 1] and s2[j - 1] == s3[k]</code>.",
                    "Set <code>ok[i][j] = from_s1 or from_s2</code>; return <code>ok[m][n]</code>.",
                ],
                "why": [
                    "Each cell reads the cell above and the cell to the left, both filled earlier in row-major order.",
                    "Row 0 and column 0 are handled by the same formula thanks to the <code>i &gt; 0</code> and <code>j &gt; 0</code> guards.",
                    "(m + 1)(n + 1) cells: <strong>O(m · n)</strong> time and <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "Row 0: ok[0][1] ('a' from s2 = s3[0]) True; ok[0][2] ('c' = s3[1]) True.",
                        "Row 1: ok[1][0] True ('a'); ok[1][1]: s3[1] = 'c' is neither 'a' (s1) nor 'a' (s2), False; ok[1][2]: from above, s1[0] = 'a' = s3[2], True.",
                        "Row 2: ok[2][0]: 'b' ≠ 'c', False; ok[2][1]: both neighbours False.",
                        "ok[2][2]: from above ok[1][2] is True and s1[1] = 'b' = s3[3]: True.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "Row 0: s2 starts with 'b' but s3 starts with 'a', so ok[0][1] = ok[0][2] = False.",
                        "Row 1: ok[1][0] True; ok[1][1]: s3[1] = 'a', but above is False and s2[0] = 'b' ≠ 'a', False; ok[1][2] False.",
                        "Row 2: ok[2][0]: s1[1] = 'b' ≠ s3[1] = 'a', False. The rest are False.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the loop start at i = 0, not 1?",
                     "Row 0 (only letters from s2) is not all True or all False; it must be computed with the same rule."],
                    ["Can I stop early when a whole row is False?",
                     "Yes, no later cell could become True then. The code does not bother, since the bound is the same."],
                    ["Why use <code>or</code> and not count?",
                     "The question is only whether an interleaving exists, not how many."],
                ],
            },
            "Two rows": {
                "idea": [
                    "Change from the table: row i reads only row i − 1 (above) and itself (left), so keep <code>prev</code> and <code>cur</code>.",
                    "<code>prev</code> starts as None because row 0 never reads it: the <code>i &gt; 0</code> guard short-circuits.",
                    "Everything else is the table code with <code>ok[i - 1]</code> renamed to <code>prev</code>.",
                ],
                "steps": [
                    "Return False on a length mismatch; set <code>prev = None</code>.",
                    "For each i, create <code>cur = [False] * (n + 1)</code>.",
                    "For each j: at (0, 0) set <code>cur[0] = True</code> and continue.",
                    "Compute <code>from_s1</code> with <code>prev[j]</code> and <code>from_s2</code> with <code>cur[j - 1]</code>; set <code>cur[j]</code>.",
                    "Set <code>prev = cur</code>; return <code>prev[n]</code>.",
                ],
                "why": [
                    "<code>prev[j]</code> and <code>cur[j - 1]</code> are the table's above and left cells, so every value is the same.",
                    "For i = 0, <code>i &gt; 0</code> is False, so <code>prev[j]</code> (None) is never indexed.",
                    "<strong>O(m · n)</strong> time; two rows: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i = 0: cur = [T, T, T].",
                        "i = 1: cur = [T, F, T].",
                        "i = 2: cur[0] F, cur[1] F, cur[2]: prev[2] True and 'b' = s3[3], True.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "i = 0: cur = [T, F, F].",
                        "i = 1: cur = [T, F, F].",
                        "i = 2: cur = [F, F, F].",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>prev = None</code> safe?",
                     "Yes, because the <code>i &gt; 0</code> check comes first in the <code>and</code> chain, so <code>prev[j]</code> is never evaluated on row 0."],
                    ["Which string should be s2 here?",
                     "The shorter one, since the rows have length n + 1. The problem is symmetric, so you can swap s1 and s2 freely."],
                    ["What does <code>prev[n]</code> mean at the end?",
                     "It is ok[m][n]: all of s1 and all of s2 used to build all of s3."],
                ],
            },
            "One row": {
                "idea": [
                    "Change from two rows: a single list <code>ok</code> is enough, with no diagonal to save.",
                    "The recurrence reads only above (<code>ok[j]</code> before it is overwritten) and left (<code>ok[j - 1]</code>, already updated this row), never up-left.",
                    "So updating left to right in place gives exactly the right values.",
                ],
                "steps": [
                    "Return False on a length mismatch; set <code>ok = [False] * (n + 1)</code>.",
                    "For each i and each j: at (0, 0), set <code>ok[0] = True</code>.",
                    "Else <code>from_s1 = i &gt; 0 and ok[j] and s1[i - 1] == s3[i + j - 1]</code>, reading the old row's value.",
                    "<code>from_s2 = j &gt; 0 and ok[j - 1] and s2[j - 1] == s3[i + j - 1]</code>, reading the new left value.",
                    "Set <code>ok[j] = from_s1 or from_s2</code>; return <code>ok[n]</code>.",
                ],
                "why": [
                    "When cell j is computed, <code>ok[j]</code> still holds row i − 1 and <code>ok[j - 1]</code> already holds row i: the two inputs the recurrence needs.",
                    "No up-left value is needed, which is why this problem gets away without a <code>diag</code> variable.",
                    "<strong>O(m · n)</strong> time and one row: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i = 0: ok = [T, T, T].",
                        "i = 1: ok[0] = T ('a'); ok[1] = F; ok[2]: old ok[2] True and 'a' = s3[2], True. ok = [T, F, T].",
                        "i = 2: ok[0] = F; ok[1] = F; ok[2]: old ok[2] True and 'b' = s3[3], True.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "i = 0: ok = [T, F, F].",
                        "i = 1: ok[0] = T; ok[1] and ok[2] stay False.",
                        "i = 2: ok[0] becomes False ('b' ≠ s3[1] = 'a'); the rest stay False.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is no <code>diag</code> needed here, unlike LCS?",
                     "LCS reads the up-left cell, which gets overwritten. Interleaving reads only up and left, and both are available in one row at the right time."],
                    ["Why must <code>ok[0]</code> be recomputed each row?",
                     "Column 0 means only s1 letters are used. It can switch from True to False, as in example 2 at i = 2."],
                    ["Does the order of j matter?",
                     "Yes, it must go left to right so that <code>ok[j - 1]</code> is the current row's value."],
                ],
            },
        },
    },
}
