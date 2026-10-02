# -*- coding: utf-8 -*-
"""DP pattern 6: interval (range) DP, written as a ladder."""

INTERVAL = dict(
    id="interval",
    title="Interval (range) DP",
    summary="state = (i, j), a subarray; solve short ranges first, combine at a split point k",
    idea=[
        "The state is a range <code>[i, j]</code> of the input, and a range's answer is built from strictly shorter ranges inside it. So fill in order of <strong>length</strong>: every range of length 1, then 2, and so on up to the whole input. (Equivalently, <code>i</code> descending and <code>j</code> ascending.) Get the fill order wrong and you read cells that have not been computed yet.",
        "There are two shapes. <strong>Shrink from the ends</strong>: <code>[i, j]</code> depends on <code>[i+1, j-1]</code>, as in the palindrome problems &mdash; O(n&sup2;), and the table shrinks to two rows and then one, like any 2-D table. <strong>Pick a split point</strong>: try every <code>k</code> between <code>i</code> and <code>j</code> and combine <code>[i, k]</code> with <code>[k, j]</code>, as in Matrix Chain Multiplication &mdash; O(n&sup3;).",
        "Split-point tables <strong>do not shrink</strong>. Cell <code>[i, j]</code> reads every cell to its left in its row and every cell below it in its column, so no row or column is finished with until the very end. The ladder for them stops at the table, and each problem says why.",
        "The hard part of split-point problems is choosing what <code>k</code> <em>means</em>. In Burst Balloons, thinking of <code>k</code> as the first balloon to burst breaks the independence of the two halves; thinking of it as the <em>last</em> makes them independent. When the obvious split couples the subproblems, try reversing time.",
    ],
    problems=[

    dict(
        id="palindromic-substrings",
        lc=647, slug="palindromic-substrings",
        name="Palindromic Substrings",
        difficulty="medium",
        recurrence=dict(
            state="<code>pal(i, j)</code> = is the substring <code>s[i..j]</code> a palindrome?",
            derive=[
                "A range is a palindrome when its two ends match and the inside is a palindrome.",
                "Ranges of length 1 (and the empty inside of a length-2 range) are palindromes automatically.",
                "The answer counts every <code>(i, j)</code> for which <code>pal(i, j)</code> is true.",
            ],
            formula='''pal(i, j) = s[i] == s[j] and pal(i+1, j-1)
pal(i, j) = True   when i >= j           one character, or nothing inside
answer: count of (i, j) with i <= j and pal(i, j)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(n&sup3;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "One recursive call per level, so each <code>pal(i, j)</code> costs up to O(n) as it walks inwards.",
                    "It is called for all <code>n&sup2;/2</code> ranges: O(n&sup3;) in total.",
                ],
                code='''def count_substrings(s):
    def pal(i, j):             # is s[i..j] a palindrome?
        if i >= j:
            return True
        return s[i] == s[j] and pal(i + 1, j - 1)

    n = len(s)
    return sum(pal(i, j) for i in range(n) for j in range(i, n))''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Cache <code>pal(i, j)</code>. Each range's inside is then looked up instead of re-walked.",
                why=[
                    "<code>n&sup2;/2</code> ranges, O(1) each once cached.",
                ],
                code='''def count_substrings(s):
    @cache
    def pal(i, j):
        if i >= j:
            return True
        return s[i] == s[j] and pal(i + 1, j - 1)

    n = len(s)
    return sum(pal(i, j) for i in range(n) for j in range(i, n))''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Fill <code>pal[i][j]</code> with <code>i</code> descending, counting true cells as you go.",
                why=[
                    "<code>pal[i][j]</code> reads <code>pal[i+1][j-1]</code>, in the row below, which is already filled.",
                    "<code>j - i &lt; 2</code> covers length 1 and 2, where there is no inside to check.",
                ],
                code='''def count_substrings(s):
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    count = 0
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                count += 1
    return count''',
            ),
            dict(
                name="Two rows",
                time="O(n&sup2;)",
                space="O(n)",
                change="Row <code>i</code> reads only row <code>i+1</code>. Keep it as <code>below</code>.",
                why=[
                    "Space falls from <code>n&sup2;</code> to <code>2n</code>.",
                ],
                code='''def count_substrings(s):
    n = len(s)
    below = [False] * n        # row i+1
    count = 0
    for i in range(n - 1, -1, -1):
        cur = [False] * n
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or below[j - 1]):
                cur[j] = True
                count += 1
        below = cur
    return count''',
            ),
            dict(
                name="One row, j right to left",
                time="O(n&sup2;)",
                space="O(n)",
                change="Update one row in place, with <code>j</code> running from right to left.",
                why=[
                    "Cell <code>j</code> reads only <code>j-1</code> of the row below &mdash; the cell to its <em>left</em>.",
                    "Right to left, <code>j-1</code> has not been overwritten yet in this pass, so it still holds the row below. (Left to right would read this row's new value.)",
                ],
                code='''def count_substrings(s):
    n = len(s)
    pal = [False] * n
    count = 0
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, i - 1, -1):
            pal[j] = s[i] == s[j] and (j - i < 2 or pal[j - 1])
            count += pal[j]
    return count''',
            ),
            dict(
                name="Expand around each centre",
                time="O(n&sup2;)",
                space="O(1)",
                best=True,
                tag="beyond the table",
                why=[
                    "Every palindrome has a centre: a character (odd length) or a gap between two (even length). There are <code>2n - 1</code> centres.",
                    "From each, expand outwards while the ends match, counting one palindrome per step.",
                    "Same O(n&sup2;) worst case with no table at all. It is the recurrence read from the inside out: each expansion step is <code>pal(i, j) = s[i] == s[j] and pal(i+1, j-1)</code>.",
                ],
                code='''def count_substrings(s):
    count = 0
    for centre in range(2 * len(s) - 1):
        lo, hi = centre // 2, (centre + 1) // 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            count += 1
            lo -= 1
            hi += 1
    return count''',
            ),
        ],
        tests='''assert count_substrings("abc") == 3
assert count_substrings("aaa") == 6
assert count_substrings("a") == 1
assert count_substrings("abba") == 6
random.seed(26)
for _ in range(80):
    s = "".join(random.choice("ab") for _ in range(random.randint(1, 12)))
    expect = sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                 if s[i:j] == s[i:j][::-1])
    assert count_substrings(s) == expect, s''',
    ),

    dict(
        id="longest-palindromic-substring",
        lc=5, slug="longest-palindromic-substring",
        name="Longest Palindromic Substring",
        difficulty="medium",
        recurrence=dict(
            state="<code>pal(i, j)</code> = is <code>s[i..j]</code> a palindrome? The answer is the longest range for which it is true.",
            derive=[
                "The same recurrence as Palindromic Substrings: matching ends around a palindromic inside.",
                "Instead of counting true ranges, remember the widest one.",
                "Substring, not subsequence: it must be contiguous. The LCS-with-reverse trick from problem 516 gives the wrong answer here.",
            ],
            formula='''pal(i, j) = s[i] == s[j] and pal(i+1, j-1)
pal(i, j) = True   when i >= j
answer: s[i..j] for the widest (i, j) with pal(i, j)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(n&sup3;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Checks every range, each by walking inwards: O(n) per range, O(n&sup3;) total.",
                    "Skipping ranges no wider than the best so far saves time in practice but not in the worst case.",
                ],
                code='''def longest_palindrome(s):
    def pal(i, j):
        if i >= j:
            return True
        return s[i] == s[j] and pal(i + 1, j - 1)

    lo, hi = 0, 1
    for i in range(len(s)):
        for j in range(i, len(s)):
            if j + 1 - i > hi - lo and pal(i, j):
                lo, hi = i, j + 1
    return s[lo:hi]''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Cache <code>pal(i, j)</code>.",
                why=[
                    "Each range is decided once. The O(n&sup2;) cache is the price.",
                ],
                code='''def longest_palindrome(s):
    @cache
    def pal(i, j):
        if i >= j:
            return True
        return s[i] == s[j] and pal(i + 1, j - 1)

    lo, hi = 0, 1
    for i in range(len(s)):
        for j in range(i, len(s)):
            if j + 1 - i > hi - lo and pal(i, j):
                lo, hi = i, j + 1
    return s[lo:hi]''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Fill <code>pal[i][j]</code> with <code>i</code> descending and track the widest true cell.",
                why=[
                    "Row <code>i</code> reads only row <code>i+1</code>, filled earlier.",
                ],
                code='''def longest_palindrome(s):
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    lo, hi = 0, 1
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                if j + 1 - i > hi - lo:
                    lo, hi = i, j + 1
    return s[lo:hi]''',
            ),
            dict(
                name="Two rows",
                time="O(n&sup2;)",
                space="O(n)",
                change="Keep only row <code>i+1</code> as <code>below</code>.",
                why=[
                    "Space falls from <code>n&sup2;</code> to <code>2n</code>.",
                ],
                code='''def longest_palindrome(s):
    n = len(s)
    below = [False] * n
    lo, hi = 0, 1
    for i in range(n - 1, -1, -1):
        cur = [False] * n
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or below[j - 1]):
                cur[j] = True
                if j + 1 - i > hi - lo:
                    lo, hi = i, j + 1
        below = cur
    return s[lo:hi]''',
            ),
            dict(
                name="One row, j right to left",
                time="O(n&sup2;)",
                space="O(n)",
                change="Update one row in place with <code>j</code> descending, so <code>pal[j-1]</code> is still the row below.",
                why=[
                    "Same argument as Palindromic Substrings: the only cell read is to the left, and right-to-left has not reached it yet.",
                ],
                code='''def longest_palindrome(s):
    n = len(s)
    pal = [False] * n
    lo, hi = 0, 1
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, i - 1, -1):
            pal[j] = s[i] == s[j] and (j - i < 2 or pal[j - 1])
            if pal[j] and j + 1 - i > hi - lo:
                lo, hi = i, j + 1
    return s[lo:hi]''',
            ),
            dict(
                name="Expand around each centre",
                time="O(n&sup2;)",
                space="O(1)",
                best=True,
                tag="beyond the table",
                why=[
                    "Expand from each of the <code>2n - 1</code> centres and remember the widest window.",
                    "No table at all: the O(n) row becomes O(1).",
                    "Manacher's algorithm does this in O(n) by reusing mirror information across centres. Worth naming; rarely expected in full.",
                ],
                code='''def longest_palindrome(s):
    best_lo, best_hi = 0, 0
    for centre in range(2 * len(s) - 1):
        lo, hi = centre // 2, (centre + 1) // 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        # the loop overshoots by one on each side
        if hi - lo - 1 > best_hi - best_lo:
            best_lo, best_hi = lo + 1, hi
    return s[best_lo:best_hi]''',
            ),
        ],
        tests='''def check(s, got):
    best = max(j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
               if s[i:j] == s[i:j][::-1])
    assert got in s and got == got[::-1] and len(got) == best, (s, got)


assert longest_palindrome("babad") in ("bab", "aba")
assert longest_palindrome("cbbd") == "bb"
assert longest_palindrome("a") == "a"
assert longest_palindrome("forgeeksskeegfor") == "geeksskeeg"
random.seed(27)
for _ in range(80):
    s = "".join(random.choice("abc") for _ in range(random.randint(1, 12)))
    check(s, longest_palindrome(s))''',
    ),

    dict(
        id="matrix-chain-multiplication",
        name="Matrix Chain Multiplication",
        difficulty="hard",
        ref=("Read on GeeksforGeeks",
             "https://www.geeksforgeeks.org/dsa/matrix-chain-multiplication-dp-8/"),
        tags=["Dynamic Programming", "Interval DP", "Array"],
        statement=[
            "Given an array <code>arr</code> of length <code>n</code>, matrix <code>i</code> (for <code>1 &le; i &lt; n</code>) has dimensions <code>arr[i-1] &times; arr[i]</code>. Multiplying a <code>p &times; q</code> matrix by a <code>q &times; r</code> matrix costs <code>p&middot;q&middot;r</code> scalar multiplications. Return the minimum total cost to multiply the whole chain, choosing where to put the brackets.",
            "Matrix multiplication is associative, so every bracketing gives the same result, but the cost can differ enormously. This is the canonical split-point interval DP: every later problem in the section is this one wearing a costume.",
        ],
        examples=[
            dict(input="arr = [2, 1, 3, 4]", output="20",
                 explanation="Matrices 2×1, 1×3, 3×4. A(BC) costs 1·3·4 + 2·1·4 = 20; (AB)C costs 2·1·3 + 2·3·4 = 30."),
            dict(input="arr = [1, 2, 3, 4, 3]", output="30"),
            dict(input="arr = [3, 4]", output="0",
                 explanation="A single matrix needs no multiplication."),
        ],
        constraints=[
            "<code>2 &lt;= arr.length &lt;= 100</code>",
            "<code>1 &lt;= arr[i] &lt;= 200</code>",
        ],
        recurrence=dict(
            state="<code>cost(i, j)</code> = the cheapest way to multiply matrices <code>i</code> through <code>j</code> (1-indexed) into one.",
            derive=[
                "Ask: <em>what is the last multiplication?</em> It joins some left block <code>i..k</code> with some right block <code>k+1..j</code>.",
                "The two blocks are computed independently, so each should be as cheap as possible: <code>cost(i, k) + cost(k+1, j)</code>.",
                "The final join multiplies an <code>arr[i-1] &times; arr[k]</code> matrix by an <code>arr[k] &times; arr[j]</code> one: <code>arr[i-1]&middot;arr[k]&middot;arr[j]</code>.",
                "Try every split <code>k</code> and keep the cheapest. A single matrix costs nothing.",
            ],
            formula='''cost(i, j) = min over k in i..j-1 of
               cost(i, k) + cost(k+1, j) + arr[i-1] * arr[k] * arr[j]
cost(i, i) = 0          one matrix, nothing to multiply
answer: cost(1, n-1)    n = len(arr)''',
            notes=[
                "\"Choose the last operation, and the rest splits into independent halves\" is the idea to carry into Burst Balloons and Cutting a Stick.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="exponential (Catalan)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Tries every bracketing. The number of bracketings of <code>n</code> matrices is a Catalan number, which grows like 4<sup>n</sup>.",
                    "Recursion depth is at most <code>n</code>: each level shrinks the range by at least one.",
                ],
                code='''def matrix_chain_order(arr):
    def cost(i, j):            # multiply matrices i..j
        if i >= j:
            return 0
        return min(cost(i, k) + cost(k + 1, j) + arr[i - 1] * arr[k] * arr[j]
                   for k in range(i, j))
    return cost(1, len(arr) - 1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup3;)",
                space="O(n&sup2;)",
                change="Cache on <code>(i, j)</code>. There are <code>n&sup2;/2</code> ranges, each trying up to <code>n</code> splits.",
                why=[
                    "Different bracketings of the outside share the same inner ranges; now each range is priced once.",
                    "Often easier to get right than the table, because the recursion works out the fill order for you.",
                ],
                code='''def matrix_chain_order(arr):
    @cache
    def cost(i, j):
        if i >= j:
            return 0
        return min(cost(i, k) + cost(k + 1, j) + arr[i - 1] * arr[k] * arr[j]
                   for k in range(i, j))
    return cost(1, len(arr) - 1)''',
            ),
            dict(
                name="Bottom-up by length",
                time="O(n&sup3;)",
                space="O(n&sup2;)",
                best=True,
                change="Fill <code>dp[i][j]</code> in order of chain length: every <code>dp[i][k]</code> and <code>dp[k+1][j]</code> is shorter, so it is ready.",
                why=[
                    "Length 1 chains are 0 (the base case); then length 2, 3, &hellip; up to the whole chain.",
                    "<strong>Why no two-row or one-row version?</strong> <code>dp[i][j]</code> reads <code>dp[i][k]</code> for <em>every</em> <code>k</code> &mdash; the whole row to its left &mdash; and <code>dp[k+1][j]</code> for every <code>k</code> &mdash; the whole column below it. No row or column is finished with until the end, so there is nothing to throw away. O(n&sup2;) is the floor for this approach.",
                ],
                code='''def matrix_chain_order(arr):
    n = len(arr) - 1                     # number of matrices, 1-indexed
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] + arr[i - 1] * arr[k] * arr[j]
                           for k in range(i, j))
    return dp[1][n] if n else 0''',
            ),
        ],
        tests='''assert matrix_chain_order([2, 1, 3, 4]) == 20
assert matrix_chain_order([1, 2, 3, 4, 3]) == 30
assert matrix_chain_order([3, 4]) == 0
assert matrix_chain_order([10, 20, 30]) == 6000
assert matrix_chain_order([40, 20, 30, 10, 30]) == 26000


def brute(arr):
    def go(i, j):
        if i >= j:
            return 0
        return min(go(i, k) + go(k + 1, j) + arr[i - 1] * arr[k] * arr[j]
                   for k in range(i, j))
    return go(1, len(arr) - 1)


random.seed(28)
for _ in range(40):
    arr = [random.randint(1, 20) for _ in range(random.randint(2, 8))]
    assert matrix_chain_order(arr) == brute(arr), arr''',
    ),

    dict(
        id="burst-balloons",
        lc=312, slug="burst-balloons",
        name="Burst Balloons",
        difficulty="hard",
        recurrence=dict(
            state="Pad the array with a 1 at each end, <code>vals = [1] + nums + [1]</code>. <code>best(l, r)</code> = the most coins from bursting every balloon strictly between <code>l</code> and <code>r</code>, while <code>l</code> and <code>r</code> themselves are still standing.",
            derive=[
                "Choosing the <em>first</em> balloon to burst does not split the problem: its two neighbours become adjacent, so the left and right sides interact.",
                "Choose the <strong>last</strong> one to burst, <code>k</code>, instead. By then everything else between <code>l</code> and <code>r</code> is gone, so <code>k</code>'s neighbours are exactly <code>l</code> and <code>r</code>: it scores <code>vals[l]&middot;vals[k]&middot;vals[r]</code>.",
                "Before that, the balloons left of <code>k</code> were burst with <code>l</code> and <code>k</code> as fixed walls, and those right of <code>k</code> with <code>k</code> and <code>r</code>. Independent: <code>best(l, k) + best(k, r)</code>.",
                "No balloons strictly between <code>l</code> and <code>r</code> means no coins.",
            ],
            formula='''best(l, r) = max over k in l+1..r-1 of
               best(l, k) + vals[l] * vals[k] * vals[r] + best(k, r)
best(l, r) = 0   when r - l < 2         nothing in between
answer: best(0, len(vals) - 1)''',
            notes=[
                "That is Matrix Chain Multiplication exactly &mdash; <code>k</code> is the split, the boundaries are fixed &mdash; which is why MCM is the problem to learn first.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="exponential",
                space="O(n)",
                tag="brute force",
                why=[
                    "Tries every choice of last balloon in every range, re-solving shared ranges many times.",
                ],
                code='''def max_coins(nums):
    vals = [1] + nums + [1]

    def best(l, r):            # burst everything strictly between l and r
        if r - l < 2:
            return 0
        return max(best(l, k) + vals[l] * vals[k] * vals[r] + best(k, r)
                   for k in range(l + 1, r))
    return best(0, len(vals) - 1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup3;)",
                space="O(n&sup2;)",
                change="Cache on <code>(l, r)</code>: <code>n&sup2;/2</code> ranges, up to <code>n</code> choices of <code>k</code> each.",
                why=[
                    "Each range is solved once.",
                ],
                code='''def max_coins(nums):
    vals = [1] + nums + [1]

    @cache
    def best(l, r):
        if r - l < 2:
            return 0
        return max(best(l, k) + vals[l] * vals[k] * vals[r] + best(k, r)
                   for k in range(l + 1, r))
    return best(0, len(vals) - 1)''',
            ),
            dict(
                name="Bottom-up by gap",
                time="O(n&sup3;)",
                space="O(n&sup2;)",
                best=True,
                change="Fill <code>dp[l][r]</code> in order of the gap <code>r - l</code>, starting at 2 (one balloon inside).",
                why=[
                    "<code>dp[l][k]</code> and <code>dp[k][r]</code> both have a smaller gap, so they are ready.",
                    "<strong>Why no smaller version?</strong> As in Matrix Chain, a cell reads its whole row to the left and its whole column below. Nothing can be discarded early.",
                ],
                code='''def max_coins(nums):
    vals = [1] + nums + [1]
    n = len(vals)
    dp = [[0] * n for _ in range(n)]
    for gap in range(2, n):
        for l in range(n - gap):
            r = l + gap
            dp[l][r] = max(dp[l][k] + vals[l] * vals[k] * vals[r] + dp[k][r]
                           for k in range(l + 1, r))
    return dp[0][n - 1]''',
            ),
        ],
        tests='''assert max_coins([3, 1, 5, 8]) == 167
assert max_coins([1, 5]) == 10
assert max_coins([7]) == 7


def brute(nums):
    best = 0
    for order in itertools.permutations(range(len(nums))):
        alive, total = list(range(len(nums))), 0
        for b in order:
            p = alive.index(b)
            left = nums[alive[p - 1]] if p > 0 else 1
            right = nums[alive[p + 1]] if p + 1 < len(alive) else 1
            total += left * nums[b] * right
            alive.pop(p)
        best = max(best, total)
    return best


random.seed(29)
for _ in range(40):
    nums = [random.randint(0, 9) for _ in range(random.randint(1, 6))]
    assert max_coins(nums) == brute(nums), nums''',
        pitfall="Letting <code>k</code> be the first balloon burst. Its neighbours then depend on what happens to the other side, and the subproblems are not independent.",
    ),

    dict(
        id="minimum-cost-to-cut-a-stick",
        lc=1547, slug="minimum-cost-to-cut-a-stick",
        name="Minimum Cost to Cut a Stick",
        difficulty="hard",
        recurrence=dict(
            state="Let <code>pos = [0] + sorted(cuts) + [n]</code>. <code>cost(i, j)</code> = the cheapest way to make every cut strictly between <code>pos[i]</code> and <code>pos[j]</code>.",
            derive=[
                "The stick can be up to 10<sup>6</sup> long, but only the <code>m &le; 100</code> cut positions matter. Working over <em>indices</em> into the sorted cuts makes the state space O(m&sup2;) instead of O(n&sup2;).",
                "Pick the <strong>first</strong> cut <code>k</code> made on the piece <code>pos[i]..pos[j]</code>. It costs the piece's length, <code>pos[j] - pos[i]</code>.",
                "It splits the piece into two that never interact again: <code>cost(i, k) + cost(k, j)</code>.",
                "A piece with no cut positions inside costs nothing.",
            ],
            formula='''cost(i, j) = pos[j] - pos[i] + min over k in i+1..j-1 of cost(i, k) + cost(k, j)
cost(i, j) = 0   when j - i < 2          no cut inside
answer: cost(0, len(pos) - 1)''',
            notes=[
                "Here \"first\" works where Burst Balloons needed \"last\", because a cut really does separate the stick. The question to ask each time is: which choice makes the halves independent?",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="exponential",
                space="O(m)",
                tag="brute force",
                why=[
                    "Tries every cut as the first cut of every piece, re-solving shared pieces.",
                ],
                code='''def min_cost(n, cuts):
    pos = [0] + sorted(cuts) + [n]

    def cost(i, j):            # make every cut strictly inside pos[i]..pos[j]
        if j - i < 2:
            return 0
        return pos[j] - pos[i] + min(cost(i, k) + cost(k, j)
                                     for k in range(i + 1, j))
    return cost(0, len(pos) - 1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(m&sup3;)",
                space="O(m&sup2;)",
                change="Cache on <code>(i, j)</code>.",
                why=[
                    "<code>m&sup2;/2</code> pieces, up to <code>m</code> first cuts each. With <code>m &le; 102</code> positions the recursion is safely under Python's limit.",
                ],
                code='''def min_cost(n, cuts):
    pos = [0] + sorted(cuts) + [n]

    @cache
    def cost(i, j):
        if j - i < 2:
            return 0
        return pos[j] - pos[i] + min(cost(i, k) + cost(k, j)
                                     for k in range(i + 1, j))
    return cost(0, len(pos) - 1)''',
            ),
            dict(
                name="Bottom-up by gap",
                time="O(m&sup3;)",
                space="O(m&sup2;)",
                best=True,
                change="Fill <code>dp[i][j]</code> in order of the gap <code>j - i</code>, starting at 2 (one cut inside).",
                why=[
                    "Both halves of any split have a smaller gap, so they are ready.",
                    "<strong>Why no smaller version?</strong> A split-point cell reads its whole row and whole column, as in Matrix Chain. The table is the floor.",
                ],
                code='''def min_cost(n, cuts):
    pos = [0] + sorted(cuts) + [n]
    m = len(pos)
    dp = [[0] * m for _ in range(m)]
    for gap in range(2, m):
        for i in range(m - gap):
            j = i + gap
            dp[i][j] = pos[j] - pos[i] + min(dp[i][k] + dp[k][j]
                                             for k in range(i + 1, j))
    return dp[0][m - 1]''',
            ),
        ],
        tests='''assert min_cost(7, [1, 3, 4, 5]) == 16
assert min_cost(9, [5, 6, 1, 4, 2]) == 22
assert min_cost(10, [5]) == 10


def brute(n, cuts):
    best = inf
    for order in itertools.permutations(cuts):
        pieces, total = [(0, n)], 0
        for c in order:
            for idx, (a, b) in enumerate(pieces):
                if a < c < b:
                    total += b - a
                    pieces[idx:idx + 1] = [(a, c), (c, b)]
                    break
        best = min(best, total)
    return best


random.seed(30)
for _ in range(40):
    n = random.randint(2, 20)
    cuts = random.sample(range(1, n), random.randint(1, min(5, n - 1)))
    assert min_cost(n, list(cuts)) == brute(n, cuts), (n, cuts)''',
    ),
    ],
)

SECTIONS = [INTERVAL]
