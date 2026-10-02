# -*- coding: utf-8 -*-
"""DP pattern 5: LCS family and two-string DP, written as a ladder."""

TWO_STRINGS = dict(
    id="two-strings",
    title="LCS family and two-string DP",
    summary="state = (i, j), a position in each string; compare, then decide",
    idea=[
        "Two sequences, two pointers. <code>f(i, j)</code> is the answer for the prefixes <code>a[:i]</code> and <code>b[:j]</code>, and every step compares <code>a[i-1]</code> with <code>b[j-1]</code>. If they match, both pointers step back together (<code>f(i-1, j-1)</code>); if not, you choose which pointer to move (<code>f(i-1, j)</code> or <code>f(i, j-1)</code>).",
        "Longest Common Subsequence is that sentence verbatim. Edit Distance is the same table with three moves &mdash; delete, insert, replace. Distinct Subsequences counts instead of maximising. Interleaving String asks whether the next character of a third string can come from either pointer. Longest Palindromic Subsequence runs two pointers inwards over one string. Once LCS clicks the rest are a different transition in the same grid.",
        "Index the table from 0 to <code>len</code> inclusive, so row 0 and column 0 mean \"empty prefix\" and the base cases sit in the table. Each cell reads <strong>above</strong>, <strong>left</strong> and <strong>above-left</strong>. Two rows hold all three. One row holds above (not yet overwritten) and left (just written), and the above-left <em>diagonal</em> is saved in a variable just before it is overwritten &mdash; that saved diagonal is the one new trick in this pattern.",
    ],
    problems=[

    dict(
        id="longest-common-subsequence",
        lc=1143, slug="longest-common-subsequence",
        name="Longest Common Subsequence",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, j)</code> = the length of the longest common subsequence of the prefixes <code>a[:i]</code> and <code>b[:j]</code>.",
            derive=[
                "Compare the last characters of the two prefixes, <code>a[i-1]</code> and <code>b[j-1]</code>.",
                "<strong>They match:</strong> it is always safe to use that character as the last one of the LCS. Both prefixes shrink: <code>1 + f(i-1, j-1)</code>.",
                "<strong>They differ:</strong> they cannot both end the LCS, so at least one of them is not in it. Drop one or the other and take the better: <code>max(f(i-1, j), f(i, j-1))</code>.",
                "If either prefix is empty, there is nothing in common.",
            ],
            formula='''f(i, j) = 1 + f(i-1, j-1)                   if a[i-1] == b[j-1]
f(i, j) = max(f(i-1, j), f(i, j-1))         otherwise
f(0, j) = f(i, 0) = 0                       an empty prefix
answer: f(m, n)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>m+n</sup>)",
                space="O(m + n)",
                tag="brute force",
                why=[
                    "On a mismatch the call branches in two, and each branch shrinks only one string by one. With no matches at all it explores every way to interleave the drops.",
                    "The stack depth is at most <code>m + n</code>.",
                ],
                code='''def longest_common_subsequence(a, b):
    def f(i, j):               # LCS of a[:i] and b[:j]
        if i == 0 or j == 0:
            return 0
        if a[i - 1] == b[j - 1]:
            return 1 + f(i - 1, j - 1)
        return max(f(i - 1, j), f(i, j - 1))
    return f(len(a), len(b))''',
            ),
            dict(
                name="Top-down memo",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Cache on <code>(i, j)</code>: <code>(m+1)(n+1)</code> states.",
                why=[
                    "Dropping from <code>a</code> then <code>b</code> reaches the same <code>(i-1, j-1)</code> as dropping from <code>b</code> then <code>a</code>. The cache solves it once.",
                    "Recursion depth up to <code>m + n</code>: two strings of 1000 characters hit Python's limit.",
                ],
                code='''def longest_common_subsequence(a, b):
    @cache
    def f(i, j):
        if i == 0 or j == 0:
            return 0
        if a[i - 1] == b[j - 1]:
            return 1 + f(i - 1, j - 1)
        return max(f(i - 1, j), f(i, j - 1))
    return f(len(a), len(b))''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Fill <code>dp[i][j]</code> row by row. Row 0 and column 0 stay 0: the empty-prefix base cases.",
                why=[
                    "Each cell reads above, left and above-left, all filled earlier in row-by-row order.",
                    "The full table lets you walk back from <code>dp[m][n]</code> to recover the subsequence itself. The smaller versions cannot.",
                ],
                code='''def longest_common_subsequence(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]''',
            ),
            dict(
                name="Two rows",
                time="O(m&middot;n)",
                space="O(n)",
                change="Row <code>i</code> reads only row <code>i-1</code> (above, above-left) and itself (left). Keep <code>prev</code> and build <code>cur</code>.",
                why=[
                    "Above is <code>prev[j]</code>, above-left is <code>prev[j-1]</code>, left is <code>cur[j-1]</code>.",
                ],
                code='''def longest_common_subsequence(a, b):
    n = len(b)
    prev = [0] * (n + 1)
    for ch in a:
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            if ch == b[j - 1]:
                cur[j] = 1 + prev[j - 1]
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[n]''',
            ),
            dict(
                name="One row plus the diagonal",
                time="O(m&middot;n)",
                space="O(min(m, n))",
                best=True,
                change="Use one row. Save the above-left value in <code>diag</code> just before it is overwritten.",
                why=[
                    "Before <code>row[j]</code> is overwritten it still holds \"above\".",
                    "<code>row[j-1]</code> has just been overwritten, so it is \"left\" &mdash; but that also destroyed the above-left value we need.",
                    "Fix: before overwriting <code>row[j]</code>, stash its old value (\"above\") in <code>above</code>. After writing, move it into <code>diag</code>. At the next <code>j</code>, <code>diag</code> is exactly the above-left cell.",
                    "Make <code>b</code> the shorter string and the space is O(min(m, n)).",
                ],
                code='''def longest_common_subsequence(a, b):
    if len(b) > len(a):
        a, b = b, a
    row = [0] * (len(b) + 1)
    for ch in a:
        diag = 0                     # dp[i-1][j-1]
        for j in range(1, len(b) + 1):
            above = row[j]
            row[j] = diag + 1 if ch == b[j - 1] else max(above, row[j - 1])
            diag = above
    return row[-1]''',
            ),
        ],
        tests='''assert longest_common_subsequence("abcde", "ace") == 3
assert longest_common_subsequence("abc", "abc") == 3
assert longest_common_subsequence("abc", "def") == 0
assert longest_common_subsequence("a", "a") == 1
assert longest_common_subsequence("bsbininm", "jmjkbkjkv") == 1


def brute(a, b):
    subs = {"".join(c) for r in range(len(a) + 1) for c in itertools.combinations(a, r)}
    def is_sub(s, t):
        it = iter(t)
        return all(ch in it for ch in s)
    return max(len(s) for s in subs if is_sub(s, b))


random.seed(21)
for _ in range(60):
    a = "".join(random.choice("abc") for _ in range(random.randint(1, 8)))
    b = "".join(random.choice("abc") for _ in range(random.randint(1, 8)))
    assert longest_common_subsequence(a, b) == brute(a, b), (a, b)''',
    ),

    dict(
        id="edit-distance",
        lc=72, slug="edit-distance",
        name="Edit Distance",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, j)</code> = the fewest edits to turn the prefix <code>a[:i]</code> into the prefix <code>b[:j]</code>.",
            derive=[
                "Compare the last characters, <code>a[i-1]</code> and <code>b[j-1]</code>.",
                "<strong>They match:</strong> no edit needed for them: <code>f(i-1, j-1)</code>.",
                "<strong>They differ:</strong> one edit fixes the end, then solve what is left. <strong>Replace</strong> <code>a[i-1]</code> with <code>b[j-1]</code>: <code>f(i-1, j-1)</code>. <strong>Delete</strong> <code>a[i-1]</code>: <code>f(i-1, j)</code>. <strong>Insert</strong> <code>b[j-1]</code> at the end of <code>a</code>: <code>f(i, j-1)</code>. Take the cheapest, plus one.",
                "Base cases: turning a prefix into the empty string takes that many deletes; turning the empty string into a prefix takes that many inserts.",
            ],
            formula='''f(i, j) = f(i-1, j-1)                               if a[i-1] == b[j-1]
f(i, j) = 1 + min(f(i-1, j-1),       replace
                  f(i-1, j),         delete from a
                  f(i, j-1))         insert into a       otherwise
f(i, 0) = i        delete everything
f(0, j) = j        insert everything
answer: f(m, n)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(3<sup>m+n</sup>)",
                space="O(m + n)",
                tag="brute force",
                small=True,
                why=[
                    "Three branches on every mismatch. Two 9-letter words already take over a million calls.",
                ],
                code='''def min_distance(a, b):
    def f(i, j):               # edits to turn a[:i] into b[:j]
        if i == 0:
            return j
        if j == 0:
            return i
        if a[i - 1] == b[j - 1]:
            return f(i - 1, j - 1)
        return 1 + min(f(i - 1, j - 1), f(i - 1, j), f(i, j - 1))
    return f(len(a), len(b))''',
            ),
            dict(
                name="Top-down memo",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Cache on <code>(i, j)</code>.",
                why=[
                    "<code>(m+1)(n+1)</code> states, O(1) each.",
                ],
                code='''def min_distance(a, b):
    @cache
    def f(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if a[i - 1] == b[j - 1]:
            return f(i - 1, j - 1)
        return 1 + min(f(i - 1, j - 1), f(i - 1, j), f(i, j - 1))
    return f(len(a), len(b))''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Fill row by row. Column 0 is <code>0, 1, 2, &hellip;</code> and row 0 is <code>0, 1, 2, &hellip;</code>: the base cases.",
                why=[
                    "The same grid as LCS, with a three-way transition.",
                ],
                code='''def min_distance(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]''',
            ),
            dict(
                name="Two rows",
                time="O(m&middot;n)",
                space="O(n)",
                change="Keep <code>prev</code> (row <code>i-1</code>) and build <code>cur</code>. Each new row starts with <code>cur[0] = i</code>, its base case.",
                why=[
                    "Above is <code>prev[j]</code>, above-left <code>prev[j-1]</code>, left <code>cur[j-1]</code>.",
                ],
                code='''def min_distance(a, b):
    n = len(b)
    prev = list(range(n + 1))          # row 0
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])
        prev = cur
    return prev[n]''',
            ),
            dict(
                name="One row plus the diagonal",
                time="O(m&middot;n)",
                space="O(n)",
                best=True,
                change="The LCS trick: one row, saving the above-left cell in <code>diag</code>. The only difference is the left edge: each row sets <code>row[0] = i</code>, and <code>diag</code> starts as the old <code>row[0]</code>.",
                why=[
                    "<code>diag, row[0] = row[0], i</code> saves <code>dp[i-1][0]</code> as the first diagonal and writes the new base case in one line.",
                    "Inside the loop, <code>above</code> is the old <code>row[j]</code>, <code>row[j-1]</code> is the new left, and <code>diag</code> is the old <code>row[j-1]</code>.",
                ],
                code='''def min_distance(a, b):
    row = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        diag, row[0] = row[0], i
        for j in range(1, len(b) + 1):
            above = row[j]
            if a[i - 1] == b[j - 1]:
                row[j] = diag
            else:
                row[j] = 1 + min(diag, above, row[j - 1])
            diag = above
    return row[-1]''',
            ),
        ],
        tests='''assert min_distance("horse", "ros") == 3
assert min_distance("intention", "execution") == 5
assert min_distance("", "") == 0
assert min_distance("", "abc") == 3
assert min_distance("abc", "") == 3
assert min_distance("kitten", "sitting") == 3


def brute(a, b):
    if not a or not b:
        return len(a) + len(b)
    if a[0] == b[0]:
        return brute(a[1:], b[1:])
    return 1 + min(brute(a[1:], b[1:]), brute(a[1:], b), brute(a, b[1:]))


random.seed(22)
for _ in range(60):
    a = "".join(random.choice("abc") for _ in range(random.randint(0, 5)))
    b = "".join(random.choice("abc") for _ in range(random.randint(0, 5)))
    assert min_distance(a, b) == brute(a, b), (a, b)
    assert min_distance(a, b) == min_distance(b, a)''',
        small_tests='''assert min_distance("horse", "ros") == 3
assert min_distance("", "") == 0
assert min_distance("", "abc") == 3
assert min_distance("abc", "") == 3
assert min_distance("kitten", "sitting") == 3''',
        pitfall="Forgetting the base row and column. <code>f(0, j)</code> is <code>j</code>, not 0: turning the empty string into <code>b[:j]</code> takes j inserts.",
    ),

    dict(
        id="distinct-subsequences",
        lc=115, slug="distinct-subsequences",
        name="Distinct Subsequences",
        difficulty="hard",
        recurrence=dict(
            state="<code>f(i, j)</code> = the number of ways the prefix <code>s[:i]</code> contains the prefix <code>t[:j]</code> as a subsequence.",
            derive=[
                "Look at the last character of <code>s[:i]</code>, <code>s[i-1]</code>. Either it is not used in the match, or it is used as the last character of <code>t[:j]</code>.",
                "<strong>Not used:</strong> <code>f(i-1, j)</code>.",
                "<strong>Used</strong> (only possible if <code>s[i-1] == t[j-1]</code>): the rest of <code>t</code> must come from the rest of <code>s</code>: <code>f(i-1, j-1)</code>.",
                "Those are different ways (one uses <code>s[i-1]</code>, one does not), so add them.",
                "The empty target is contained exactly once in anything; a non-empty target is never in the empty string.",
            ],
            formula='''f(i, j) = f(i-1, j)                          s[i-1] not used
        + f(i-1, j-1)   if s[i-1] == t[j-1]  s[i-1] matches t[j-1]
f(i, 0) = 1           the empty target, once
f(0, j) = 0           for j > 0
answer: f(len(s), len(t))''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>m</sup>)",
                space="O(m)",
                tag="brute force",
                why=[
                    "<code>m = len(s)</code>. On a match the call branches in two, so it can enumerate every subsequence of <code>s</code>.",
                ],
                code='''def num_distinct(s, t):
    def f(i, j):               # ways s[:i] contains t[:j]
        if j == 0:
            return 1
        if i == 0:
            return 0
        ways = f(i - 1, j)
        if s[i - 1] == t[j - 1]:
            ways += f(i - 1, j - 1)
        return ways
    return f(len(s), len(t))''',
            ),
            dict(
                name="Top-down memo",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Cache on <code>(i, j)</code>.",
                why=[
                    "<code>(m+1)(n+1)</code> states with <code>n = len(t)</code>.",
                ],
                code='''def num_distinct(s, t):
    @cache
    def f(i, j):
        if j == 0:
            return 1
        if i == 0:
            return 0
        ways = f(i - 1, j)
        if s[i - 1] == t[j - 1]:
            ways += f(i - 1, j - 1)
        return ways
    return f(len(s), len(t))''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Fill row by row. Column 0 is all 1s; the rest of row 0 is 0.",
                why=[
                    "Each cell reads only the row above: straight up and up-left.",
                ],
                code='''def num_distinct(s, t):
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = 1
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j]
            if s[i - 1] == t[j - 1]:
                dp[i][j] += dp[i - 1][j - 1]
    return dp[m][n]''',
            ),
            dict(
                name="Two rows",
                time="O(m&middot;n)",
                space="O(n)",
                change="Only the row above is read. Keep it as <code>prev</code>; build <code>cur</code> as a copy and add the matches.",
                why=[
                    "<code>cur = prev[:]</code> is the \"not used\" term for every <code>j</code>; the loop adds the \"used\" term where characters match.",
                ],
                code='''def num_distinct(s, t):
    prev = [1] + [0] * len(t)
    for ch in s:
        cur = prev[:]
        for j in range(1, len(t) + 1):
            if t[j - 1] == ch:
                cur[j] += prev[j - 1]
        prev = cur
    return prev[-1]''',
            ),
            dict(
                name="One row, j downwards",
                time="O(m&middot;n)",
                space="O(n)",
                best=True,
                change="Update one row in place, with <code>j</code> running <strong>downwards</strong>.",
                why=[
                    "Cell <code>j</code> reads itself and <code>j-1</code> of the previous row. Going downwards, <code>j-1</code> has not been updated yet, so it is still the previous row.",
                    "Upwards, <code>ways[j-1]</code> might already count <code>s[i-1]</code> as a match, and the same character of <code>s</code> would be used twice. It is the 0/1 knapsack direction rule again, for the same reason.",
                ],
                code='''def num_distinct(s, t):
    ways = [1] + [0] * len(t)
    for ch in s:
        for j in range(len(t), 0, -1):
            if t[j - 1] == ch:
                ways[j] += ways[j - 1]
    return ways[-1]''',
            ),
        ],
        tests='''assert num_distinct("rabbbit", "rabbit") == 3
assert num_distinct("babgbag", "bag") == 5
assert num_distinct("abc", "") == 1
assert num_distinct("", "a") == 0
assert num_distinct("aaa", "aa") == 3


def brute(s, t):
    return sum(1 for c in itertools.combinations(range(len(s)), len(t))
               if "".join(s[i] for i in c) == t)


random.seed(23)
for _ in range(60):
    s = "".join(random.choice("ab") for _ in range(random.randint(0, 10)))
    t = "".join(random.choice("ab") for _ in range(random.randint(0, 4)))
    assert num_distinct(s, t) == brute(s, t), (s, t)''',
    ),

    dict(
        id="longest-palindromic-subsequence",
        lc=516, slug="longest-palindromic-subsequence",
        name="Longest Palindromic Subsequence",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, j)</code> = the length of the longest palindromic subsequence inside <code>s[i..j]</code> (both ends included).",
            derive=[
                "Look at the two ends, <code>s[i]</code> and <code>s[j]</code>.",
                "<strong>They match:</strong> they can wrap the best palindrome of the inside: <code>2 + f(i+1, j-1)</code>.",
                "<strong>They differ:</strong> they cannot both be the outer pair, so drop one end: <code>max(f(i+1, j), f(i, j-1))</code>.",
                "A single character is a palindrome of length 1; an empty range has length 0.",
            ],
            formula='''f(i, j) = 2 + f(i+1, j-1)                   if s[i] == s[j]
f(i, j) = max(f(i+1, j), f(i, j-1))         otherwise
f(i, i) = 1
f(i, j) = 0   when i > j                    empty range
answer: f(0, n-1)''',
            notes=[
                "This is the \"interval\" shape of the next section, but its table shrinks exactly like LCS: row <code>i</code> reads only row <code>i+1</code> and itself.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Branches in two on every mismatch, shrinking the range by one each time.",
                ],
                code='''def longest_palindrome_subseq(s):
    def f(i, j):               # best palindrome inside s[i..j]
        if i > j:
            return 0
        if i == j:
            return 1
        if s[i] == s[j]:
            return 2 + f(i + 1, j - 1)
        return max(f(i + 1, j), f(i, j - 1))
    return f(0, len(s) - 1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Cache on <code>(i, j)</code>: about <code>n&sup2;/2</code> ranges.",
                why=[
                    "Dropping the left then the right end reaches the same range as the other order. Now it is solved once.",
                ],
                code='''def longest_palindrome_subseq(s):
    @cache
    def f(i, j):
        if i > j:
            return 0
        if i == j:
            return 1
        if s[i] == s[j]:
            return 2 + f(i + 1, j - 1)
        return max(f(i + 1, j), f(i, j - 1))
    return f(0, len(s) - 1)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Fill with <code>i</code> <strong>descending</strong> and <code>j</code> ascending from <code>i</code>. Cells with <code>i &gt; j</code> stay 0.",
                why=[
                    "<code>dp[i][j]</code> reads row <code>i+1</code> (filled earlier, since <code>i</code> descends) and <code>dp[i][j-1]</code> (filled earlier in this row).",
                ],
                code='''def longest_palindrome_subseq(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = 2 + dp[i + 1][j - 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]''',
            ),
            dict(
                name="Two rows",
                time="O(n&sup2;)",
                space="O(n)",
                change="Row <code>i</code> reads only row <code>i+1</code> and itself. Keep <code>below</code> and build <code>cur</code>.",
                why=[
                    "\"Below-left\" is <code>below[j-1]</code>, \"below\" is <code>below[j]</code>, \"left\" is <code>cur[j-1]</code> &mdash; the LCS neighbours, mirrored.",
                ],
                code='''def longest_palindrome_subseq(s):
    n = len(s)
    below = [0] * n            # row i+1
    for i in range(n - 1, -1, -1):
        cur = [0] * n
        cur[i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                cur[j] = 2 + below[j - 1]
            else:
                cur[j] = max(below[j], cur[j - 1])
        below = cur
    return below[n - 1]''',
            ),
            dict(
                name="One row plus the diagonal",
                time="O(n&sup2;)",
                space="O(n)",
                best=True,
                change="One row, saving the old <code>row[j-1]</code> in <code>diag</code> before it is overwritten &mdash; the LCS trick.",
                why=[
                    "Before <code>row[j]</code> is overwritten it holds <code>f(i+1, j)</code> (\"below\"). <code>row[j-1]</code> already holds <code>f(i, j-1)</code> (\"left\").",
                    "<code>diag</code> carries the old <code>row[j-1]</code>, which is <code>f(i+1, j-1)</code>.",
                    "At <code>j = i+1</code> the diagonal is the empty range <code>f(i+1, i) = 0</code>, which is why <code>diag</code> starts at 0.",
                ],
                code='''def longest_palindrome_subseq(s):
    n = len(s)
    row = [0] * n              # row[j] = f(i + 1, j) until overwritten
    for i in range(n - 1, -1, -1):
        diag = 0               # f(i+1, i): the empty range
        row[i] = 1
        for j in range(i + 1, n):
            above = row[j]
            row[j] = diag + 2 if s[i] == s[j] else max(above, row[j - 1])
            diag = above
    return row[n - 1]''',
            ),
            dict(
                name="LCS of the string and its reverse",
                time="O(n&sup2;)",
                space="O(n)",
                tag="another view",
                why=[
                    "A palindromic subsequence reads the same backwards, so it is a common subsequence of <code>s</code> and <code>s[::-1]</code> &mdash; and the longest common one is always a palindrome of that length.",
                    "So the answer is LCS(s, reversed s), with the one-row LCS code unchanged. Spotting that a one-string question is really a two-string one is a recurring move.",
                ],
                code='''def longest_palindrome_subseq(s):
    r = s[::-1]
    row = [0] * (len(r) + 1)
    for ch in s:
        diag = 0
        for j in range(1, len(r) + 1):
            above = row[j]
            row[j] = diag + 1 if ch == r[j - 1] else max(above, row[j - 1])
            diag = above
    return row[-1]''',
            ),
        ],
        tests='''assert longest_palindrome_subseq("bbbab") == 4
assert longest_palindrome_subseq("cbbd") == 2
assert longest_palindrome_subseq("a") == 1
assert longest_palindrome_subseq("abcde") == 1
assert longest_palindrome_subseq("agbdba") == 5


def brute(s):
    return max(r for r in range(1, len(s) + 1)
               for c in itertools.combinations(s, r) if c == c[::-1])


random.seed(24)
for _ in range(60):
    s = "".join(random.choice("abc") for _ in range(random.randint(1, 10)))
    assert longest_palindrome_subseq(s) == brute(s), s''',
    ),

    dict(
        id="interleaving-string",
        lc=97, slug="interleaving-string",
        name="Interleaving String",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, j)</code> = can <code>s1[:i]</code> and <code>s2[:j]</code> be interleaved to form <code>s3[:i+j]</code>?",
            derive=[
                "The third string is not a third dimension: after using <code>i</code> characters of <code>s1</code> and <code>j</code> of <code>s2</code>, you are always at position <code>i + j</code> of <code>s3</code>.",
                "The last character of <code>s3[:i+j]</code> came from <code>s1</code> or from <code>s2</code>.",
                "<strong>From s1:</strong> needs <code>s1[i-1] == s3[i+j-1]</code> and the rest to work: <code>f(i-1, j)</code>. <strong>From s2:</strong> needs <code>s2[j-1] == s3[i+j-1]</code> and <code>f(i, j-1)</code>.",
                "If the lengths do not add up, the answer is immediately no.",
            ],
            formula='''f(i, j) = (s1[i-1] == s3[i+j-1] and f(i-1, j))      last char from s1
       or (s2[j-1] == s3[i+j-1] and f(i, j-1))      last char from s2
f(0, 0) = True
answer: len(s1) + len(s2) == len(s3) and f(m, n)''',
            notes=[
                "Greedy (take from whichever string matches) fails when both match; the DP explores both without the exponential blow-up.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>m+n</sup>)",
                space="O(m + n)",
                tag="brute force",
                why=[
                    "When both strings match the next character, both branches are tried.",
                ],
                code='''def is_interleave(s1, s2, s3):
    if len(s1) + len(s2) != len(s3):
        return False

    def f(i, j):               # can s1[:i] and s2[:j] form s3[:i+j]?
        if i == 0 and j == 0:
            return True
        k = i + j - 1
        if i > 0 and s1[i - 1] == s3[k] and f(i - 1, j):
            return True
        return j > 0 and s2[j - 1] == s3[k] and f(i, j - 1)
    return f(len(s1), len(s2))''',
            ),
            dict(
                name="Top-down memo",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Cache on <code>(i, j)</code>.",
                why=[
                    "<code>(m+1)(n+1)</code> states.",
                ],
                code='''def is_interleave(s1, s2, s3):
    if len(s1) + len(s2) != len(s3):
        return False

    @cache
    def f(i, j):
        if i == 0 and j == 0:
            return True
        k = i + j - 1
        if i > 0 and s1[i - 1] == s3[k] and f(i - 1, j):
            return True
        return j > 0 and s2[j - 1] == s3[k] and f(i, j - 1)
    return f(len(s1), len(s2))''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(m&middot;n)",
                space="O(m&middot;n)",
                change="Fill a boolean grid row by row, starting from <code>ok[0][0] = True</code>.",
                why=[
                    "Each cell reads above (<code>s1</code> supplied the character) and left (<code>s2</code> did).",
                ],
                code='''def is_interleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    ok = [[False] * (n + 1) for _ in range(m + 1)]
    ok[0][0] = True
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 and j == 0:
                continue
            k = i + j - 1
            from_s1 = i > 0 and ok[i - 1][j] and s1[i - 1] == s3[k]
            from_s2 = j > 0 and ok[i][j - 1] and s2[j - 1] == s3[k]
            ok[i][j] = from_s1 or from_s2
    return ok[m][n]''',
            ),
            dict(
                name="Two rows",
                time="O(m&middot;n)",
                space="O(n)",
                change="Keep <code>prev</code> (row <code>i-1</code>) and build <code>cur</code>.",
                why=[
                    "\"Above\" is <code>prev[j]</code>, \"left\" is <code>cur[j-1]</code>.",
                ],
                code='''def is_interleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    prev = None
    for i in range(m + 1):
        cur = [False] * (n + 1)
        for j in range(n + 1):
            if i == 0 and j == 0:
                cur[0] = True
                continue
            k = i + j - 1
            from_s1 = i > 0 and prev[j] and s1[i - 1] == s3[k]
            from_s2 = j > 0 and cur[j - 1] and s2[j - 1] == s3[k]
            cur[j] = from_s1 or from_s2
        prev = cur
    return prev[n]''',
            ),
            dict(
                name="One row",
                time="O(m&middot;n)",
                space="O(n)",
                best=True,
                change="Update one row in place: before the update <code>ok[j]</code> is \"above\"; <code>ok[j-1]</code> has just become \"left\".",
                why=[
                    "Only above and left are read &mdash; no diagonal &mdash; so no extra variable is needed.",
                    "Make <code>s2</code> the shorter string to get O(min(m, n)) space.",
                ],
                code='''def is_interleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    ok = [False] * (n + 1)
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 and j == 0:
                ok[0] = True
            else:
                from_s1 = i > 0 and ok[j] and s1[i - 1] == s3[i + j - 1]
                from_s2 = j > 0 and ok[j - 1] and s2[j - 1] == s3[i + j - 1]
                ok[j] = from_s1 or from_s2
    return ok[n]''',
            ),
        ],
        tests='''assert is_interleave("aabcc", "dbbca", "aadbbcbcac") is True
assert is_interleave("aabcc", "dbbca", "aadbbbaccc") is False
assert is_interleave("", "", "") is True
assert is_interleave("a", "", "a") is True
assert is_interleave("a", "b", "a") is False
assert is_interleave("ab", "ba", "abba") is True


def brute(s1, s2, s3):
    if not s3:
        return not s1 and not s2
    return bool((s1 and s1[0] == s3[0] and brute(s1[1:], s2, s3[1:])) or
                (s2 and s2[0] == s3[0] and brute(s1, s2[1:], s3[1:])))


random.seed(25)
for _ in range(120):
    s1 = "".join(random.choice("ab") for _ in range(random.randint(0, 5)))
    s2 = "".join(random.choice("ab") for _ in range(random.randint(0, 5)))
    s3 = list(s1 + s2)
    if random.random() < 0.5:
        random.shuffle(s3)
    s3 = "".join(s3)
    assert is_interleave(s1, s2, s3) == brute(s1, s2, s3), (s1, s2, s3)''',
    ),
    ],
)

SECTIONS = [TWO_STRINGS]
