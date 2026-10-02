# -*- coding: utf-8 -*-
"""DP patterns 0 and 1: recursion -> memo -> table, and 1-D linear DP.

Every problem is written as a ladder (see content/dp.py): plain recursion,
the recurrence it encodes, top-down memo, bottom-up table, then each space
optimisation with what changed and why it is safe.
"""

# =================================================================== pattern 0
FOUNDATIONS = dict(
    id="foundations",
    title="Recursion, memo, table",
    summary="the same answer four ways: recursion, memo, table, rolling variables",
    idea=[
        "Every DP problem on this site is solved as the same ladder, and this pattern is where you learn it on problems whose recurrence is obvious:",
        "<strong>1. Plain recursion.</strong> Write the brute force that tries every choice. It is correct and usually exponential, but it is where the recurrence comes from. <strong>2. The recurrence.</strong> Name what one call means (the <em>state</em>), what choice it makes, and its base cases. <strong>3. Top-down memo.</strong> Cache each state the first time it is solved. <strong>4. Bottom-up table.</strong> Fill the same states in a loop, smallest first; no recursion limit. <strong>5. Shrink the table.</strong> Look at which cells each step reads. If row <code>i</code> only reads row <code>i-1</code>, keep two rows; if the reads can be ordered so one row is enough, keep one; if a 1-D step reads only the last two cells, keep two variables.",
        "Step 5 is where most of the interview value is, and every space step on every problem says exactly which cells are read and why overwriting is safe.",
    ],
    problems=[

    dict(
        id="nth-fibonacci",
        name="Nth Fibonacci Number",
        difficulty="easy",
        ref=("Read on GeeksforGeeks",
             "https://www.geeksforgeeks.org/dsa/program-for-nth-fibonacci-number/"),
        tags=["Dynamic Programming", "Recursion", "Memoization", "Math"],
        statement=[
            "Given a non-negative integer <code>n</code>, return the <code>n</code>-th Fibonacci number, where <code>F(0) = 0</code>, <code>F(1) = 1</code> and <code>F(n) = F(n-1) + F(n-2)</code> for <code>n &gt; 1</code>.",
            "It is here not because it is hard but because it is the cleanest possible place to see the whole ladder: recursion &rarr; memo &rarr; table &rarr; rolling variables.",
        ],
        examples=[
            dict(input="n = 5", output="5", explanation="0, 1, 1, 2, 3, 5"),
            dict(input="n = 10", output="55"),
        ],
        constraints=["<code>0 &lt;= n &lt;= 90</code>"],
        recurrence=dict(
            state="<code>f(i)</code> = the <code>i</code>-th Fibonacci number.",
            derive=[
                "The problem hands you the recurrence: each number is the sum of the two before it.",
                "The two smallest arguments cannot be split further, so they are the base cases.",
            ],
            formula='''f(i) = f(i-1) + f(i-2)        for i >= 2
f(0) = 0
f(1) = 1
answer: f(n)''',
            notes=[
                "<strong>Overlapping subproblems:</strong> the call tree has about 1.6<sup>n</sup> nodes but only <code>n + 1</code> distinct arguments. That gap is exactly what DP removes.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(&phi;<sup>n</sup>) &asymp; O(1.618<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "A direct translation of the definition. Correct, and hopeless for large <code>n</code>.",
                    "Every call makes two more calls, and the same arguments are recomputed again and again: <code>fib(40)</code> makes over 300 million calls.",
                    "Space is the recursion stack. Only one root-to-leaf path is on the stack at a time, and that path is <code>n</code> calls long.",
                ],
                code='''def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n)",
                space="O(n)",
                change="Cache each <code>f(i)</code> the first time it is computed. The recursion is unchanged.",
                why=[
                    "There are only <code>n + 1</code> distinct arguments, and each is now computed once. Every other call is a dictionary lookup.",
                    "Each state does O(1) work besides its cached calls, so time drops from exponential to O(n).",
                    "Space: the cache holds <code>n + 1</code> values and the stack is still <code>n</code> deep. CPython stops at about 1000 frames, which is the practical limit of top-down.",
                ],
                code='''def fib(n):
    @cache
    def f(i):
        if i < 2:
            return i
        return f(i - 1) + f(i - 2)
    return f(n)''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n)",
                space="O(n)",
                change="Replace the recursion with a loop that fills <code>dp[0..n]</code> from the smallest index up.",
                why=[
                    "<code>dp[i]</code> needs <code>dp[i-1]</code> and <code>dp[i-2]</code>. Filling left to right guarantees both are ready.",
                    "The base cases become the first two cells of the table instead of an <code>if</code>.",
                    "No recursion at all, so no stack and no recursion limit. The table is still O(n).",
                ],
                code='''def fib(n):
    if n < 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]''',
            ),
            dict(
                name="Two variables",
                time="O(n)",
                space="O(1)",
                best=True,
                change="<code>dp[i]</code> only ever reads the two cells just before it, so keep those two values instead of the whole table.",
                why=[
                    "Once <code>dp[i]</code> is computed, <code>dp[i-2]</code> is never read again. Everything older than two steps is dead weight.",
                    "<code>a</code> holds <code>f(i)</code> and <code>b</code> holds <code>f(i+1)</code>. Each step slides the pair one place right: <code>a, b = b, a + b</code>.",
                    "Python's tuple assignment evaluates the right-hand side first, so no temporary variable is needed.",
                    "This is the move to look for in every 1-D DP: write the table, see how far back each step reads, keep only that much.",
                ],
                code='''def fib(n):
    a, b = 0, 1          # f(i), f(i+1)
    for _ in range(n):
        a, b = b, a + b
    return a''',
            ),
            dict(
                name="Fast doubling",
                time="O(log n)",
                space="O(log n)",
                tag="beyond DP",
                why=[
                    "Uses <code>F(2k) = F(k)(2F(k+1) - F(k))</code> and <code>F(2k+1) = F(k)<sup>2</sup> + F(k+1)<sup>2</sup></code> to halve <code>n</code> at every step.",
                    "Only log n levels are needed. It is the matrix-power method without the matrices.",
                    "The answer to \"can you beat O(n)?\". Not expected unless asked.",
                ],
                code='''def fib(n):
    def pair(k):                    # returns (F(k), F(k+1))
        if k == 0:
            return 0, 1
        a, b = pair(k // 2)
        c = a * (2 * b - a)
        d = a * a + b * b
        return (d, c + d) if k % 2 else (c, d)
    return pair(n)[0]''',
            ),
        ],
        tests='''assert [fib(i) for i in range(11)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
assert fib(20) == 6765
assert fib(24) == 46368''',
    ),

    dict(
        id="climbing-stairs",
        lc=70, slug="climbing-stairs",
        name="Climbing Stairs",
        difficulty="easy",
        recurrence=dict(
            state="<code>f(i)</code> = the number of distinct ways to reach step <code>i</code>.",
            derive=[
                "Ask: <em>what was the last move?</em> You arrived at step <code>i</code> either with a 1-step from <code>i-1</code> or a 2-step from <code>i-2</code>.",
                "Those two groups of paths never overlap (their last move differs), so the counts add.",
                "Base case: there is exactly one way to be at step 0 &mdash; do nothing &mdash; and one way to reach step 1.",
            ],
            formula='''f(i) = f(i-1) + f(i-2)        for i >= 2
f(0) = 1                      one way to climb nothing
f(1) = 1
answer: f(n)''',
            notes=[
                "It is Fibonacci shifted by one place. \"Split on the last decision\" is the question that finds almost every recurrence on this site.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(&phi;<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                small=True,
                why=[
                    "Tries both possible last moves at every step, so the call tree doubles at every level.",
                    "Correct, but <code>n = 45</code> means over a billion calls.",
                ],
                code='''def climb_stairs(n):
    def f(i):                  # ways to reach step i
        if i <= 1:
            return 1
        return f(i - 1) + f(i - 2)
    return f(n)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n)",
                space="O(n)",
                change="Cache <code>f(i)</code>. Each of the <code>n + 1</code> steps is counted once.",
                why=[
                    "Same recursion; repeated calls become cache hits.",
                    "O(n) for the cache plus O(n) for the recursion stack.",
                ],
                code='''def climb_stairs(n):
    @cache
    def f(i):
        if i <= 1:
            return 1
        return f(i - 1) + f(i - 2)
    return f(n)''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n)",
                space="O(n)",
                change="Fill <code>dp[0..n]</code> left to right instead of recursing.",
                why=[
                    "<code>dp[0] = dp[1] = 1</code> are the base cases; every later cell adds the two before it.",
                    "No recursion stack, so no depth limit.",
                ],
                code='''def climb_stairs(n):
    dp = [1] * (n + 1)
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]''',
            ),
            dict(
                name="Two variables",
                time="O(n)",
                space="O(1)",
                best=True,
                change="Each cell reads only the previous two, so keep two numbers instead of the table.",
                why=[
                    "<code>a</code> is <code>f(i-1)</code>, <code>b</code> is <code>f(i)</code>. Each loop moves both one step forward.",
                    "Getting the base case wrong (<code>f(0) = 0</code>) shifts every answer by one. It is 1: standing still is one way to climb zero stairs.",
                ],
                code='''def climb_stairs(n):
    a, b = 1, 1          # f(0), f(1)
    for _ in range(n - 1):
        a, b = b, a + b
    return b''',
            ),
        ],
        tests='''assert climb_stairs(1) == 1
assert climb_stairs(2) == 2
assert climb_stairs(3) == 3
assert climb_stairs(5) == 8


def brute(n):
    return 1 if n <= 1 else brute(n - 1) + brute(n - 2)


for n in range(1, 20):
    assert climb_stairs(n) == brute(n), n
assert climb_stairs(45) == 1836311903''',
        small_tests='''assert [climb_stairs(n) for n in range(1, 16)] == [
    1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]''',
    ),
    ],
)


# =================================================================== pattern 1
LINEAR = dict(
    id="linear",
    title="1-D linear DP",
    summary="state = the best answer for the prefix ending at i",
    idea=[
        "The state is a single index: <code>f(i)</code> is the answer for the first <code>i</code> elements, or for the best choice that <em>ends</em> at element <code>i</code>. The recurrence decides what to do with element <code>i</code> given the answers for smaller prefixes &mdash; usually take it or skip it.",
        "House Robber is the template: rob house <code>i</code> and add <code>f(i-2)</code>, or skip it and keep <code>f(i-1)</code>. Nearly every problem in this pattern is that sentence with different nouns. Maximum Subarray asks \"extend the run ending at <code>i-1</code>, or start fresh?\"; Decode Ways asks \"read one digit or two?\"; Delete and Earn is House Robber after you rearrange the input.",
        "Because each step reads only the last one or two states, the ladder always ends at O(n) time and O(1) space. If your 1-D solution still uses a full array, look again.",
    ],
    problems=[

    dict(
        id="house-robber",
        lc=198, slug="house-robber",
        name="House Robber",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i)</code> = the most money you can rob from houses <code>0..i</code>.",
            derive=[
                "Look only at the last house in range, house <code>i</code>. You either rob it or you do not.",
                "<strong>Skip it:</strong> the best is whatever houses <code>0..i-1</code> give, <code>f(i-1)</code>.",
                "<strong>Rob it:</strong> you get <code>nums[i]</code>, but house <code>i-1</code> is now off limits, so add <code>f(i-2)</code>.",
                "Take the larger of the two.",
            ],
            formula='''f(i) = max(f(i-1),               skip house i
           nums[i] + f(i-2))     rob house i
f(i) = 0   for i < 0             no houses, no money
answer: f(n-1)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(&phi;<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Each call branches into skip and rob, the same shape as Fibonacci, so the call tree grows by about 1.6&times; per house.",
                    "The stack depth is n: the \"skip\" chain walks down one house at a time.",
                ],
                code='''def rob(nums):
    def f(i):                  # most money from houses 0..i
        if i < 0:
            return 0
        return max(f(i - 1), nums[i] + f(i - 2))
    return f(len(nums) - 1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n)",
                space="O(n)",
                change="Cache <code>f(i)</code>. There are only <code>n</code> distinct indices.",
                why=[
                    "Each <code>f(i)</code> is solved once in O(1) work, so O(n) time.",
                    "The cache and the stack are both O(n). Past about 1000 houses CPython hits its recursion limit.",
                ],
                code='''def rob(nums):
    @cache
    def f(i):
        if i < 0:
            return 0
        return max(f(i - 1), nums[i] + f(i - 2))
    return f(len(nums) - 1)''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n)",
                space="O(n)",
                change="Fill a table left to right. Shift the index by one, so <code>dp[i]</code> means \"the first <code>i</code> houses\" and <code>dp[0]</code> is the empty street.",
                why=[
                    "The shift puts the base case (<code>f(-1) = 0</code>) into the table as <code>dp[0] = 0</code>, so the loop needs no <code>if i &lt; 0</code> checks.",
                    "<code>dp[1] = nums[0]</code>: with one house you rob it.",
                    "<code>dp[i] = max(dp[i-1], nums[i-1] + dp[i-2])</code> is the recurrence with the shifted index.",
                ],
                code='''def rob(nums):
    n = len(nums)
    dp = [0] * (n + 1)         # dp[i] = best from the first i houses
    dp[1] = nums[0]
    for i in range(2, n + 1):
        dp[i] = max(dp[i - 1], nums[i - 1] + dp[i - 2])
    return dp[n]''',
            ),
            dict(
                name="Two variables",
                time="O(n)",
                space="O(1)",
                best=True,
                change="<code>dp[i]</code> reads only <code>dp[i-1]</code> and <code>dp[i-2]</code>. Keep those two values as <code>cur</code> and <code>prev</code>; drop the array.",
                why=[
                    "After house <code>i</code>, <code>prev</code> becomes the old <code>cur</code> and <code>cur</code> becomes the new best.",
                    "Starting both at 0 is the empty street, so even the first house needs no special case.",
                    "One pass, constant space.",
                ],
                code='''def rob(nums):
    prev, cur = 0, 0           # dp[i-2], dp[i-1]
    for x in nums:
        prev, cur = cur, max(cur, prev + x)
    return cur''',
            ),
        ],
        tests='''assert rob([1, 2, 3, 1]) == 4
assert rob([2, 7, 9, 3, 1]) == 12
assert rob([5]) == 5
assert rob([2, 1, 1, 2]) == 4


def brute(nums):
    n, best = len(nums), 0
    for mask in range(1 << n):
        if mask & (mask >> 1) == 0:
            best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


random.seed(2)
for _ in range(60):
    data = [random.randint(0, 40) for _ in range(random.randint(1, 12))]
    assert rob(data) == brute(data), data''',
        pitfall="Assuming the answer alternates houses (all evens or all odds). <code>[2, 1, 1, 2]</code> is best robbed at both ends, skipping two in a row.",
    ),

    dict(
        id="house-robber-ii",
        lc=213, slug="house-robber-ii",
        name="House Robber II",
        difficulty="medium",
        recurrence=dict(
            state="<code>line(lo, i)</code> = the most money from houses <code>lo..i</code> of a straight street &mdash; House Robber's state, with a starting point.",
            derive=[
                "The circle adds one rule: the first and last house are neighbours, so they cannot both be robbed.",
                "So at least one of them is skipped. Either the first is skipped (the answer lies in houses <code>1..n-1</code>) or the last is (houses <code>0..n-2</code>).",
                "Each of those is a straight street, which is plain House Robber. Solve both, take the better.",
                "One house is a special case: both ranges would be empty, but you can rob it.",
            ],
            formula='''line(lo, i) = max(line(lo, i-1), nums[i] + line(lo, i-2))
line(lo, i) = 0   for i < lo
answer: max(line(1, n-1), line(0, n-2))      (n == 1: nums[0])''',
            notes=[
                "\"Break the cycle by fixing one endpoint\" is the idea to carry away. It turns a circular DP into two straight ones.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(&phi;<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "House Robber's recursion, run twice with different start points.",
                    "Exponential for the same reason: skip and rob branch at every house.",
                ],
                code='''def rob(nums):
    def line(lo, i):           # most money from houses lo..i
        if i < lo:
            return 0
        return max(line(lo, i - 1), nums[i] + line(lo, i - 2))

    n = len(nums)
    if n == 1:
        return nums[0]
    return max(line(1, n - 1), line(0, n - 2))''',
            ),
            dict(
                name="Top-down memo",
                time="O(n)",
                space="O(n)",
                change="Cache on <code>(lo, i)</code>. <code>lo</code> only takes two values, so there are about <code>2n</code> states.",
                why=[
                    "Each state is solved once: O(n) time.",
                    "Cache and stack are O(n).",
                ],
                code='''def rob(nums):
    @cache
    def line(lo, i):
        if i < lo:
            return 0
        return max(line(lo, i - 1), nums[i] + line(lo, i - 2))

    n = len(nums)
    if n == 1:
        return nums[0]
    return max(line(1, n - 1), line(0, n - 2))''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n)",
                space="O(n)",
                change="For each range, fill a House Robber table left to right.",
                why=[
                    "<code>dp[k]</code> is the best from the first <code>k</code> houses of the range, with <code>dp[0] = 0</code> for the empty range.",
                    "Two tables of up to <code>n</code> cells each: still O(n).",
                ],
                code='''def rob(nums):
    def line(lo, hi):          # houses lo..hi-1
        dp = [0] * (hi - lo + 1)
        for k in range(1, hi - lo + 1):
            take = nums[lo + k - 1] + (dp[k - 2] if k >= 2 else 0)
            dp[k] = max(dp[k - 1], take)
        return dp[-1]

    n = len(nums)
    if n == 1:
        return nums[0]
    return max(line(1, n), line(0, n - 1))''',
            ),
            dict(
                name="Two variables per pass",
                time="O(n)",
                space="O(1)",
                best=True,
                change="Each cell reads only the two before it, so each pass keeps two variables. Pass index ranges rather than slices, so no copy of the list is made either.",
                why=[
                    "Exactly House Robber's rolling pair, run over <code>1..n-1</code> and then <code>0..n-2</code>.",
                    "Slicing (<code>nums[1:]</code>) would be simpler to read but copies n elements, which quietly makes the space O(n) again.",
                ],
                code='''def rob(nums):
    def line(lo, hi):          # houses lo..hi-1
        prev, cur = 0, 0
        for i in range(lo, hi):
            prev, cur = cur, max(cur, prev + nums[i])
        return cur

    n = len(nums)
    if n == 1:
        return nums[0]
    return max(line(1, n), line(0, n - 1))''',
            ),
        ],
        tests='''assert rob([2, 3, 2]) == 3
assert rob([1, 2, 3, 1]) == 4
assert rob([1, 2, 3]) == 3
assert rob([7]) == 7
assert rob([1, 7]) == 7


def brute(nums):
    n, best = len(nums), 0
    for mask in range(1 << n):
        ok = mask & (mask >> 1) == 0 and not (n > 1 and mask & 1 and mask >> (n - 1) & 1)
        if ok:
            best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


random.seed(3)
for _ in range(60):
    data = [random.randint(0, 30) for _ in range(random.randint(1, 12))]
    assert rob(data) == brute(data), data''',
    ),

    dict(
        id="maximum-subarray",
        lc=53, slug="maximum-subarray",
        name="Maximum Subarray",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i)</code> = the largest sum of a subarray that <em>ends exactly at</em> index <code>i</code>.",
            derive=[
                "\"Best subarray in the prefix\" gives no recurrence, because the best one may end anywhere. Anchor the end instead.",
                "A subarray ending at <code>i</code> is either just <code>nums[i]</code>, or a subarray ending at <code>i-1</code> with <code>nums[i]</code> added.",
                "If you extend, extend the best one ending at <code>i-1</code>: <code>f(i-1) + nums[i]</code>.",
                "The answer can end anywhere, so it is the largest <code>f(i)</code> over all <code>i</code>.",
            ],
            formula='''f(i) = max(nums[i],               start fresh at i
           f(i-1) + nums[i])     extend the best run ending at i-1
f(0) = nums[0]
answer: max(f(0), f(1), ..., f(n-1))''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(n&sup2;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Only one recursive call per level, so it is not exponential &mdash; but <code>f(i)</code> walks all the way down to <code>f(0)</code>, and it is called for every <code>i</code>.",
                    "That is 1 + 2 + &hellip; + n calls: O(n&sup2;).",
                ],
                code='''def max_sub_array(nums):
    def f(i):                  # best sum of a subarray ending exactly at i
        if i == 0:
            return nums[0]
        return max(nums[i], f(i - 1) + nums[i])
    return max(f(i) for i in range(len(nums)))''',
            ),
            dict(
                name="Top-down memo",
                time="O(n)",
                space="O(n)",
                change="Cache <code>f(i)</code>, so the chain below each <code>i</code> is walked once in total, not once per <code>i</code>.",
                why=[
                    "n states, O(1) each.",
                    "The first call, <code>f(0)</code>, is cheap; each later call finds <code>f(i-1)</code> already cached.",
                ],
                code='''def max_sub_array(nums):
    @cache
    def f(i):
        if i == 0:
            return nums[0]
        return max(nums[i], f(i - 1) + nums[i])
    return max(f(i) for i in range(len(nums)))''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n)",
                space="O(n)",
                change="Fill <code>dp[i]</code> left to right, then take the maximum.",
                why=[
                    "<code>dp[0] = nums[0]</code> is the base case.",
                    "No recursion, but the array is still n long.",
                ],
                code='''def max_sub_array(nums):
    dp = [0] * len(nums)
    dp[0] = nums[0]
    for i in range(1, len(nums)):
        dp[i] = max(nums[i], dp[i - 1] + nums[i])
    return max(dp)''',
            ),
            dict(
                name="One variable (Kadane)",
                time="O(n)",
                space="O(1)",
                best=True,
                change="<code>dp[i]</code> reads only <code>dp[i-1]</code>. Keep that one value as <code>end_here</code>, and track the running maximum instead of calling <code>max(dp)</code> at the end.",
                why=[
                    "This <em>is</em> Kadane's algorithm. It is not a separate trick; it is the table above with the array removed.",
                    "Start from <code>nums[0]</code>, not 0. With every number negative the answer is the largest single element, and 0 is not a legal answer.",
                ],
                code='''def max_sub_array(nums):
    best = end_here = nums[0]
    for x in nums[1:]:
        end_here = max(x, end_here + x)
        best = max(best, end_here)
    return best''',
            ),
        ],
        tests='''assert max_sub_array([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_sub_array([1]) == 1
assert max_sub_array([5, 4, -1, 7, 8]) == 23
assert max_sub_array([-3, -1, -2]) == -1
random.seed(4)
for _ in range(60):
    data = [random.randint(-20, 20) for _ in range(random.randint(1, 25))]
    expect = max(sum(data[i:j]) for i in range(len(data)) for j in range(i + 1, len(data) + 1))
    assert max_sub_array(data) == expect, data''',
        pitfall="Initialising the answer to 0. With every number negative the answer is the largest single element, and 0 is not a legal subarray sum.",
    ),

    dict(
        id="decode-ways",
        lc=91, slug="decode-ways",
        name="Decode Ways",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i)</code> = the number of ways to decode the first <code>i</code> characters, <code>s[:i]</code>.",
            derive=[
                "Split on the last letter decoded. It used either one digit or two.",
                "<strong>One digit</strong>, <code>s[i-1]</code>: valid unless it is <code>'0'</code>. The rest, <code>s[:i-1]</code>, decodes <code>f(i-1)</code> ways.",
                "<strong>Two digits</strong>, <code>s[i-2:i]</code>: valid if they read 10 to 26. The rest decodes <code>f(i-2)</code> ways.",
                "The two cases end differently, so no decoding is counted twice: add them.",
            ],
            formula='''f(i) = (f(i-1)  if s[i-1] != '0')
     + (f(i-2)  if i >= 2 and 10 <= int(s[i-2:i]) <= 26)
f(0) = 1          the empty prefix decodes one way: as nothing
answer: f(n)''',
            notes=[
                "It is Climbing Stairs where some steps are forbidden. The zeros are the whole difficulty: <code>'0'</code> alone decodes to nothing, so <code>\"06\"</code> has zero ways and <code>\"10\"</code> has one.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(&phi;<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Tries both a one-digit and a two-digit last letter at every position, so it branches like Fibonacci when both are valid.",
                ],
                code='''def num_decodings(s):
    def f(i):                  # ways to decode s[:i]
        if i == 0:
            return 1
        total = f(i - 1) if s[i - 1] != "0" else 0
        if i >= 2 and "10" <= s[i - 2:i] <= "26":
            total += f(i - 2)
        return total
    return f(len(s))''',
            ),
            dict(
                name="Top-down memo",
                time="O(n)",
                space="O(n)",
                change="Cache <code>f(i)</code>.",
                why=[
                    "n + 1 states, O(1) work each.",
                    "The string comparison <code>\"10\" &lt;= s[i-2:i] &lt;= \"26\"</code> works because both sides are two characters long, so string order equals number order.",
                ],
                code='''def num_decodings(s):
    @cache
    def f(i):
        if i == 0:
            return 1
        total = f(i - 1) if s[i - 1] != "0" else 0
        if i >= 2 and "10" <= s[i - 2:i] <= "26":
            total += f(i - 2)
        return total
    return f(len(s))''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n)",
                space="O(n)",
                change="Fill <code>dp[0..n]</code> left to right, with <code>dp[0] = 1</code>.",
                why=[
                    "Each cell is the recurrence verbatim; <code>dp[i-1]</code> and <code>dp[i-2]</code> are always ready.",
                ],
                code='''def num_decodings(s):
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        if s[i - 1] != "0":
            dp[i] = dp[i - 1]
        if i >= 2 and "10" <= s[i - 2:i] <= "26":
            dp[i] += dp[i - 2]
    return dp[n]''',
            ),
            dict(
                name="Two variables",
                time="O(n)",
                space="O(1)",
                best=True,
                change="Each cell reads only the two before it: keep <code>prev = dp[i-1]</code> and <code>cur = dp[i]</code>.",
                why=[
                    "<code>prev</code> starts at 0 (there is no <code>dp[-1]</code>) and <code>cur</code> at 1 (<code>dp[0]</code>).",
                    "Each character computes the next count <code>nxt</code> from the pair, then slides the pair forward.",
                ],
                code='''def num_decodings(s):
    prev, cur = 0, 1           # dp[i-1], dp[i]
    for i in range(len(s)):
        nxt = cur if s[i] != "0" else 0
        if i > 0 and "10" <= s[i - 1:i + 1] <= "26":
            nxt += prev
        prev, cur = cur, nxt
    return cur''',
            ),
        ],
        tests='''assert num_decodings("12") == 2
assert num_decodings("226") == 3
assert num_decodings("06") == 0
assert num_decodings("10") == 1
assert num_decodings("2101") == 1
assert num_decodings("100") == 0
assert num_decodings("27") == 1


def brute(s):
    if not s:
        return 1
    total = 0
    for k in (1, 2):
        if len(s) >= k and s[0] != "0" and 1 <= int(s[:k]) <= 26:
            total += brute(s[k:])
    return total


random.seed(5)
for _ in range(200):
    s = "".join(random.choice("0112226789") for _ in range(random.randint(1, 12)))
    assert num_decodings(s) == brute(s), s''',
        pitfall="Treating <code>\"0\"</code> like any other digit. It can only appear as the second half of 10 or 20.",
    ),

    dict(
        id="delete-and-earn",
        lc=740, slug="delete-and-earn",
        name="Delete and Earn",
        difficulty="medium",
        recurrence=dict(
            state="After collapsing the input into <code>points[v] = v &times; count(v)</code>, <code>f(v)</code> = the most points using values <code>0..v</code>.",
            derive=[
                "If you take one copy of <code>v</code>, you may as well take every copy: the penalty (losing <code>v-1</code> and <code>v+1</code>) is already paid. So each value is worth <code>points[v]</code>.",
                "Taking <code>v</code> rules out <code>v-1</code> and <code>v+1</code>: no two adjacent values. That is House Robber on the array <code>points</code>.",
                "<strong>Skip v:</strong> <code>f(v-1)</code>. <strong>Take v:</strong> <code>points[v] + f(v-2)</code>.",
            ],
            formula='''f(v) = max(f(v-1),                 skip value v
           points[v] + f(v-2))     take every copy of v
f(v) = 0   for v < 0
answer: f(max(nums))''',
            notes=[
                "Recognising a known problem after a transformation is the skill this one tests.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(n + &phi;<sup>m</sup>)",
                space="O(m)",
                tag="brute force",
                why=[
                    "<code>m</code> is the largest value. Building <code>points</code> is O(n + m); the recursion is House Robber's, exponential in <code>m</code>.",
                ],
                code='''def delete_and_earn(nums):
    points = [0] * (max(nums) + 1)
    for x in nums:
        points[x] += x

    def f(v):                  # most points from values 0..v
        if v < 0:
            return 0
        return max(f(v - 1), points[v] + f(v - 2))
    return f(len(points) - 1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n + m)",
                space="O(m)",
                change="Cache <code>f(v)</code>: <code>m + 1</code> states.",
                why=[
                    "Linear now. But LeetCode allows values up to 10<sup>4</sup>, which is a recursion 10<sup>4</sup> deep &mdash; far past Python's limit. Go bottom-up.",
                ],
                code='''def delete_and_earn(nums):
    points = [0] * (max(nums) + 1)
    for x in nums:
        points[x] += x

    @cache
    def f(v):
        if v < 0:
            return 0
        return max(f(v - 1), points[v] + f(v - 2))
    return f(len(points) - 1)''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n + m)",
                space="O(m)",
                change="Fill <code>dp</code> over values in increasing order, shifted by one so <code>dp[0]</code> is \"no values\".",
                why=[
                    "<code>dp[v+1]</code> = best from values <code>0..v</code>. The shift keeps the <code>v - 2 &lt; 0</code> case inside the table.",
                ],
                code='''def delete_and_earn(nums):
    points = [0] * (max(nums) + 1)
    for x in nums:
        points[x] += x
    dp = [0] * (len(points) + 1)
    for v in range(len(points)):
        dp[v + 1] = max(dp[v], points[v] + (dp[v - 1] if v >= 1 else 0))
    return dp[-1]''',
            ),
            dict(
                name="Two variables",
                time="O(n + m)",
                space="O(m)",
                best=True,
                change="The DP now keeps only two numbers. The <code>points</code> array is still O(m), but the table on top of it is gone.",
                why=[
                    "This is House Robber's loop, run over <code>points</code>.",
                    "O(n) to bucket, O(m) to scan. With m up to 10<sup>4</sup> this is cheaper than sorting.",
                ],
                code='''def delete_and_earn(nums):
    points = [0] * (max(nums) + 1)
    for x in nums:
        points[x] += x
    prev, cur = 0, 0
    for p in points:
        prev, cur = cur, max(cur, prev + p)
    return cur''',
            ),
            dict(
                name="Sorted distinct values",
                time="O(n log n)",
                space="O(n)",
                tag="sparse values",
                why=[
                    "Walk the distinct values in order. If a value is exactly one more than the previous, the two conflict: choose House Robber style. If there is a gap, there is no conflict: just add.",
                    "Better when values are huge and sparse (say up to 10<sup>9</sup>), where an array indexed by value would not fit.",
                ],
                code='''def delete_and_earn(nums):
    from collections import Counter
    count = Counter(nums)
    prev, cur, last = 0, 0, None
    for v in sorted(count):
        gain = v * count[v]
        if last is not None and v == last + 1:
            prev, cur = cur, max(cur, prev + gain)
        else:
            prev, cur = cur, cur + gain
        last = v
    return cur''',
            ),
        ],
        tests='''assert delete_and_earn([3, 4, 2]) == 6
assert delete_and_earn([2, 2, 3, 3, 3, 4]) == 9
assert delete_and_earn([1]) == 1
assert delete_and_earn([1, 1, 1, 2, 4, 5, 5, 5, 6]) == 18


def brute(nums):
    vals = sorted(set(nums))
    best = 0
    for r in range(len(vals) + 1):
        for pick in itertools.combinations(vals, r):
            if all(b - a != 1 for a, b in zip(pick, pick[1:])):
                best = max(best, sum(v * nums.count(v) for v in pick))
    return best


random.seed(6)
for _ in range(80):
    data = [random.randint(1, 10) for _ in range(random.randint(1, 12))]
    assert delete_and_earn(data) == brute(data), data''',
    ),
    ],
)

SECTIONS = [FOUNDATIONS, LINEAR]
