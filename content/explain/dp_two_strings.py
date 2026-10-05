"""Write-ups for Dynamic Programming, part 5: two-string problems."""

EXPLAIN = {
    # ------------------------------------------------------------------ LCS
    "longest-common-subsequence": {
        "example": {"call": 'longest_common_subsequence("abcde", "ace")', "expect": "3"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Compare the last characters of the prefixes <code>a[:i]</code> and <code>b[:j]</code>.",
                    "If they match, they can both end the LCS: 1 + f(i-1, j-1).",
                    "If not, at least one of them is unused: max(f(i-1, j), f(i, j-1)).",
                ],
                "steps": [
                    "f(0, ·) = f(·, 0) = 0; call <code>f(len(a), len(b))</code>.",
                ],
                "why": [
                    "Every mismatch branches in two: exponential in the worst case, and at most m + n deep.",
                ],
                "dry": [
                    "e == e: 1 + f(\"abcd\", \"ac\").",
                    "d ≠ c: the better branch drops the d, giving f(\"abc\", \"ac\").",
                    "c == c: 1 + f(\"ab\", \"a\"), which is 1. The total is <strong>3</strong> (\"ace\").",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Dropping a character from a then from b reaches the same (i-1, j-1) as the other order. Cache it.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "There are (m+1)(n+1) states, each O(1).",
                ],
                "dry": [
                    "f(5, 3) → f(4, 2) → f(3, 2) → f(2, 1) → … each is solved once.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>dp[i][j]</code> = the LCS of <code>a[:i]</code> and <code>b[:j]</code>; row 0 and column 0 are 0.",
                    "Each cell reads above, left and up-left, all filled earlier.",
                ],
                "steps": [
                    "On a match: <code>1 + dp[i-1][j-1]</code>; otherwise <code>max(dp[i-1][j], dp[i][j-1])</code>.",
                ],
                "why": [
                    "It is O(m·n) time and space. The full table also lets you walk back to recover the subsequence itself.",
                ],
                "dry": [
                    "Rows over b = \"ace\": a [0, 1, 1, 1]; b [0, 1, 1, 1]; c [0, 1, 2, 2].",
                    "Then d [0, 1, 2, 2]; e [0, 1, 2, 3].",
                    "dp[5][3] = <strong>3</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep the previous row: above is <code>prev[j]</code>, up-left is <code>prev[j-1]</code>, left is <code>cur[j-1]</code>.",
                ],
                "steps": [
                    "Build <code>cur</code> per character of a.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Same rows; the final row is [0, 1, 2, 3].",
                    "The result is <strong>3</strong>.",
                ],
            },
            "One row plus the diagonal": {
                "idea": [
                    "In a single row, <code>row[j]</code> before the write is \"above\" and <code>row[j-1]</code> is \"left\".",
                    "But writing <code>row[j-1]</code> destroyed the up-left value, so save each old value in <code>diag</code> before overwriting.",
                    "Swap so b is the shorter string, for O(min(m, n)) space.",
                ],
                "steps": [
                    "<code>above = row[j]</code>; write <code>row[j]</code>; <code>diag = above</code>; reset diag to 0 for each row.",
                ],
                "why": [
                    "It is O(m·n) time and O(min(m, n)) space.",
                ],
                "dry": [
                    "Here a = \"abcde\" is longer, so it stays outer.",
                    "On the 'e' row: at j = 3, diag = old row[2] = 2, and 'e' matches, so row[3] = 3.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ edit distance
    "edit-distance": {
        "example": {"call": 'min_distance("horse", "ros")', "expect": "3"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "<code>f(i, j)</code> = the edits to turn <code>a[:i]</code> into <code>b[:j]</code>.",
                    "If the last characters match, they cost nothing: f(i-1, j-1).",
                    "Otherwise, 1 + the best of replace (i-1, j-1), delete from a (i-1, j) and insert into a (i, j-1).",
                ],
                "steps": [
                    "f(0, j) = j inserts; f(i, 0) = i deletes.",
                ],
                "why": [
                    "Three branches per mismatch: O(3<sup>m+n</sup>).",
                ],
                "dry": [
                    "horse → rorse (replace h with r).",
                    "rorse → rose (delete r) → ros (delete e).",
                    "That is <strong>3</strong> edits.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, j)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(m·n).",
                ],
                "dry": [
                    "f(5, 3): 'e' ≠ 's', so 1 + min(f(4, 2), f(4, 3), f(5, 2)) = 1 + min(3, 2, 4) = <strong>3</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Row 0 is 0..n (inserts) and column 0 is 0..m (deletes); fill the inside with the three-way rule.",
                ],
                "steps": [
                    "On a match copy up-left; otherwise 1 + min(up-left, up, left).",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "Rows: [0, 1, 2, 3], h [1, 1, 2, 3], o [2, 2, 1, 2].",
                    "r [3, 2, 2, 2], s [4, 3, 3, 2], e [5, 4, 4, 3].",
                    "dp[5][3] = <strong>3</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "<code>prev</code> starts as 0..n; each new row starts with i (the deletes).",
                ],
                "steps": [
                    "Read up-left, up and left from <code>prev[j-1]</code>, <code>prev[j]</code> and <code>cur[j-1]</code>.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Same rows as the table.",
                    "The last is [5, 4, 4, 3], so the result is <strong>3</strong>.",
                ],
            },
            "One row plus the diagonal": {
                "idea": [
                    "This is LCS's single-row trick: save the old <code>row[j]</code> in <code>above</code>, then pass it to <code>diag</code>.",
                    "<code>diag, row[0] = row[0], i</code> saves the first diagonal and writes the new base case in one line.",
                ],
                "steps": [
                    "Match: <code>row[j] = diag</code>; else <code>1 + min(diag, above, row[j-1])</code>.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Row 'o': at j = 2, 'o' matches, so row[2] = diag = old row[1] = 1.",
                    "Row 'e': row[3] = 1 + min(diag 3, above 2, left 4) = 3.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ distinct subsequences
    "distinct-subsequences": {
        "example": {"call": 'num_distinct("babgbag", "bag")', "expect": "5"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "<code>f(i, j)</code> = the number of ways <code>s[:i]</code> contains <code>t[:j]</code> as a subsequence.",
                    "The last character of s is either not used (f(i-1, j)), or, if it matches t's last character, used to finish t (f(i-1, j-1)).",
                ],
                "steps": [
                    "f(·, 0) = 1 (the empty t is matched once); f(0, j&gt;0) = 0.",
                ],
                "why": [
                    "Every match branches in two: up to O(2<sup>m</sup>).",
                ],
                "dry": [
                    "The \"bag\" choices in babgbag (by index): (0, 1, 3), (0, 1, 6), (0, 5, 6), (2, 5, 6), (4, 5, 6).",
                    "That is <strong>5</strong> ways.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, j)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(m·n).",
                ],
                "dry": [
                    "f(7, 3) = f(6, 3) + f(6, 2) = 1 + 4 = <strong>5</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Column 0 is all 1s; each cell = above + (up-left if the characters match).",
                ],
                "steps": [
                    "Fill row by row over s.",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "Rows [\"\", b, ba, bag] after each character of s: b [1, 1, 0, 0], a [1, 1, 1, 0], b [1, 2, 1, 0], g [1, 2, 1, 1].",
                    "Then b [1, 3, 1, 1], a [1, 3, 4, 1], g [1, 3, 4, 5].",
                    "The result is <strong>5</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "<code>cur = prev[:]</code> is the \"not used\" term for every j; then add <code>prev[j-1]</code> wherever the characters match.",
                ],
                "steps": [
                    "Per character of s: copy, add, swap.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "Same rows; the final is [1, 3, 4, 5].",
                    "The result is <strong>5</strong>.",
                ],
            },
            "One row, j downwards": {
                "idea": [
                    "Cell j reads itself and j-1 from the previous row; looping j downwards keeps j-1 unchanged until it is read.",
                    "Looping upwards would let one character of s count twice (\"aa\" in t matched by a single 'a'). It is the 0/1 knapsack direction rule.",
                ],
                "steps": [
                    "For j from len(t) down to 1: if they match, <code>ways[j] += ways[j-1]</code>.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "The 6th character 'a': ways[2] += ways[1], so 1 + 3 = 4.",
                    "The 7th character 'g': ways[3] += ways[2], so 1 + 4 = 5.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LPS
    "longest-palindromic-subsequence": {
        "example": {"call": 'longest_palindrome_subseq("bbbab")', "expect": "4"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "<code>f(i, j)</code> = the longest palindromic subsequence inside <code>s[i..j]</code>.",
                    "Equal ends wrap the inside: 2 + f(i+1, j-1). Otherwise drop one end: max(f(i+1, j), f(i, j-1)).",
                ],
                "steps": [
                    "f(i, i) = 1; f(i, j) = 0 when i &gt; j.",
                ],
                "why": [
                    "It branches on every mismatch: exponential.",
                ],
                "dry": [
                    "The ends 'b' and 'b' match: 2 + f(\"bba\").",
                    "f(\"bba\") = max(f(\"ba\"), f(\"bb\")) = 2.",
                    "The total is <strong>4</strong> (\"bbbb\").",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Dropping the left end then the right reaches the same range as the other order. Cache <code>(i, j)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n²).",
                ],
                "dry": [
                    "f(1, 2) = 2 is shared by several branches.",
                    "f(0, 4) = <strong>4</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Fill i downwards and j upwards: <code>dp[i][j]</code> reads row i+1 and the cell to its left.",
                ],
                "steps": [
                    "<code>dp[i][i] = 1</code>; apply the rule for j &gt; i.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "Row 4: [·, ·, ·, ·, 1]. Row 3: [·, ·, ·, 1, 1]. Row 2: [·, ·, 1, 1, 3].",
                    "Row 1: [·, 1, 2, 2, 3]. Row 0: [1, 2, 3, 3, 4].",
                    "dp[0][4] = <strong>4</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only row i+1 (<code>below</code>). The neighbours are LCS's, mirrored: below-left, below, left.",
                ],
                "steps": [
                    "Build <code>cur</code> with <code>cur[i] = 1</code>.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "The final row is [1, 2, 3, 3, 4].",
                    "The result is <strong>4</strong>.",
                ],
            },
            "One row plus the diagonal": {
                "idea": [
                    "Before <code>row[j]</code> is overwritten it is f(i+1, j); <code>row[j-1]</code> is f(i, j-1); <code>diag</code> carries the old row[j-1], f(i+1, j-1).",
                    "diag starts at 0, the empty range f(i+1, i).",
                ],
                "steps": [
                    "<code>row[i] = 1</code>, then sweep j upwards, saving above into diag.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "At i = 0 and j = 4, 'b' == 'b', so row[4] = diag + 2 = old row[3] + 2 = 2 + 2 = 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "LCS of the string and its reverse": {
                "idea": [
                    "A palindrome reads the same backwards, so it is a common subsequence of s and reversed s.",
                    "The longest common one has the same length as the longest palindromic subsequence, so reuse the one-row LCS code.",
                ],
                "steps": [
                    "<code>r = s[::-1]</code>; run LCS(s, r).",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                    "Turning a one-string question into a two-string one is a recurring move.",
                ],
                "dry": [
                    "LCS(\"bbbab\", \"babbb\") = 4, the common \"bbbb\".",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ interleaving string
    "interleaving-string": {
        "example": {"call": 'is_interleave("aabcc", "dbbca", "aadbbcbcac")', "expect": "True"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "<code>f(i, j)</code>: can <code>s1[:i]</code> and <code>s2[:j]</code> form <code>s3[:i+j]</code>?",
                    "The last character of s3[:i+j] came from s1 (if it matches s1[i-1]) or from s2. Try both.",
                    "If the lengths do not add up, return False right away.",
                ],
                "steps": [
                    "f(0, 0) = True.",
                ],
                "why": [
                    "It branches whenever both strings match: exponential.",
                ],
                "dry": [
                    "One valid split of \"aadbbcbcac\" (1 = from s1, 2 = from s2): 1 1 2 2 2 2 1 1 2 1.",
                    "s1 supplies \"aa\" + \"bc\" + \"c\" = \"aabcc\"; s2 supplies \"dbbc\" + \"a\" = \"dbbca\".",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, j)</code>; the position in s3 is always i + j.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(m·n).",
                ],
                "dry": [
                    "f(5, 5) follows the split back to f(0, 0).",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>ok[i][j]</code> is True when above (s1 supplied the character) or left (s2 supplied it) works.",
                ],
                "steps": [
                    "<code>ok[0][0] = True</code>; fill row by row.",
                ],
                "why": [
                    "It is O(m·n) time and space.",
                ],
                "dry": [
                    "True cells per row (j = 0..5): row 0: {0}; row 1: {0}; row 2: {0, 1, 2, 3, 4}.",
                    "Row 3: {1, 2, 4}; row 4: {2, 3, 4, 5}; row 5: {3, 5}.",
                    "ok[5][5] = <strong>True</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Above is <code>prev[j]</code> and left is <code>cur[j-1]</code>.",
                ],
                "steps": [
                    "Build <code>cur</code> per i; swap.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "The last row has True at j = 3 and 5.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "Only above and left are read (no diagonal), so a single row needs no extra variable.",
                    "<code>ok[j]</code> before the write is above; <code>ok[j-1]</code> after its write is left.",
                ],
                "steps": [
                    "Overwrite <code>ok[j]</code> in place.",
                ],
                "why": [
                    "It is O(m·n) time and O(n) space.",
                ],
                "dry": [
                    "The row after i = 5 is [F, F, F, T, F, T].",
                    "The result is <strong>True</strong>.",
                ],
            },
        },
    },
}
