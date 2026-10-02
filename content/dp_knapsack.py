# -*- coding: utf-8 -*-
"""DP pattern 2: knapsack, 0/1 and unbounded, written as a ladder."""

KNAPSACK = dict(
    id="knapsack",
    title="Knapsack: 0/1 and unbounded",
    summary="state = (item, capacity); take it or leave it, once or as often as you like",
    idea=[
        "You have items and a budget &mdash; weight, a target sum, a count of zeros and ones. The state is <code>(i, c)</code>: using only the first <code>i</code> items, what is the best (or the number of ways) with capacity <code>c</code>? Item <code>i</code> is either left out, <code>f(i-1, c)</code>, or taken, <code>f(i-1, c - w) + v</code>.",
        "Row <code>i</code> of the table only reads row <code>i-1</code>, so the table always collapses to two rows, and then to one. In the one-row version the <strong>loop direction</strong> carries the meaning. In <strong>0/1 knapsack</strong> each item is used at most once, so capacity runs <em>downwards</em>: when you read <code>dp[c - w]</code> it still holds the previous row. In <strong>unbounded knapsack</strong> items are reusable, so capacity runs <em>upwards</em>: <code>dp[c - w]</code> may already include this item, which is exactly what reuse means.",
        "In counting problems, Coin Change II counts <em>combinations</em>, so coins go in the outer loop. Swap the loops and you count <em>permutations</em> instead &mdash; a different problem with a bigger answer.",
        "Many problems here are knapsack in disguise. Partition, Target Sum and Last Stone Weight II all reduce to \"which subset sums are reachable?\" after a line of algebra. Finding that line is the interview.",
    ],
    problems=[

    dict(
        id="knapsack-01",
        name="0/1 Knapsack",
        difficulty="medium",
        ref=("Read on GeeksforGeeks",
             "https://www.geeksforgeeks.org/dsa/0-1-knapsack-problem-dp-10/"),
        tags=["Dynamic Programming", "Array", "Knapsack"],
        statement=[
            "Given <code>n</code> items, where item <code>i</code> has weight <code>wt[i]</code> and value <code>val[i]</code>, and a bag of capacity <code>W</code>, return the maximum total value of items you can put in the bag. Each item is either taken whole or left out, and each can be used at most once.",
            "This is the concept problem for the whole pattern. Every problem after it in this section is this table with a different cell type (boolean, count, minimum) or a different loop direction.",
        ],
        examples=[
            dict(input="W = 4, val = [1, 2, 3], wt = [4, 5, 1]", output="3",
                 explanation="Only item 3 (weight 1) and item 1 (weight 4) fit alone; together they weigh 5. Item 3 is worth more."),
            dict(input="W = 3, val = [1, 2, 3], wt = [4, 5, 6]", output="0",
                 explanation="Nothing fits."),
        ],
        constraints=[
            "<code>1 &lt;= n &lt;= 10<sup>3</sup></code>",
            "<code>1 &lt;= W &lt;= 10<sup>3</sup></code>",
            "<code>1 &lt;= wt[i], val[i] &lt;= 10<sup>3</sup></code>",
        ],
        recurrence=dict(
            state="<code>f(i, c)</code> = the most value you can get from the <em>first <code>i</code> items</em> with a bag of capacity <code>c</code>.",
            derive=[
                "Look at the last item in play, item <code>i-1</code>. You either leave it or take it.",
                "<strong>Leave it:</strong> nothing changes except that it is gone: <code>f(i-1, c)</code>.",
                "<strong>Take it</strong> (only if <code>wt[i-1] &le; c</code>): gain its value, lose its weight from the bag, and it is gone: <code>val[i-1] + f(i-1, c - wt[i-1])</code>.",
                "Both options move to <code>i-1</code>: an item can be taken at most once. That is what makes it 0/1.",
            ],
            formula='''f(i, c) = max(f(i-1, c),                             leave item i-1
              val[i-1] + f(i-1, c - wt[i-1]))       take it, if wt[i-1] <= c
f(0, c) = 0          no items, no value
answer: f(n, W)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Every item is either left or taken, so the call tree is a full binary tree of depth <code>n</code>: every subset is tried.",
                    "Stack depth is <code>n</code>, one level per item.",
                ],
                code='''def knapsack(W, val, wt):
    def f(i, c):               # best from the first i items, capacity c
        if i == 0:
            return 0
        best = f(i - 1, c)
        if wt[i - 1] <= c:
            best = max(best, val[i - 1] + f(i - 1, c - wt[i - 1]))
        return best
    return f(len(val), W)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&middot;W)",
                space="O(n&middot;W)",
                change="Cache on <code>(i, c)</code>. There are <code>(n+1)(W+1)</code> distinct states, however many subsets reach them.",
                why=[
                    "Two different subsets of the first few items can leave the same capacity; after that their futures are identical. The cache solves that future once.",
                    "Only the <code>(i, c)</code> pairs actually reached get computed, which can be far fewer than n&middot;W when weights are large.",
                ],
                code='''def knapsack(W, val, wt):
    @cache
    def f(i, c):
        if i == 0:
            return 0
        best = f(i - 1, c)
        if wt[i - 1] <= c:
            best = max(best, val[i - 1] + f(i - 1, c - wt[i - 1]))
        return best
    return f(len(val), W)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&middot;W)",
                space="O(n&middot;W)",
                change="Fill <code>dp[i][c]</code> row by row, <code>i</code> from 1 to <code>n</code>. Row 0 is all zeros: the base case.",
                why=[
                    "Every cell in row <code>i</code> reads only row <code>i-1</code>, at the same or a smaller capacity. So filling row by row means everything needed is ready.",
                    "The full table lets you walk back from <code>dp[n][W]</code> to recover <em>which</em> items were taken. The smaller versions below cannot.",
                ],
                code='''def knapsack(W, val, wt):
    n = len(val)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = wt[i - 1], val[i - 1]
        for c in range(W + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c:
                dp[i][c] = max(dp[i][c], v + dp[i - 1][c - w])
    return dp[n][W]''',
            ),
            dict(
                name="Two rows",
                time="O(n&middot;W)",
                space="O(W)",
                change="Row <code>i</code> reads only row <code>i-1</code>. Keep <code>prev</code> (row <code>i-1</code>) and build <code>cur</code> (row <code>i</code>); then <code>cur</code> becomes <code>prev</code>.",
                why=[
                    "Rows older than <code>i-1</code> are never read again, so storing them was wasted space.",
                    "<code>cur = prev[:]</code> fills in the \"leave it\" option for every capacity at once; the loop then only updates the capacities where taking the item fits.",
                    "Space drops from <code>(n+1)(W+1)</code> to <code>2(W+1)</code>.",
                ],
                code='''def knapsack(W, val, wt):
    prev = [0] * (W + 1)       # row i-1
    for w, v in zip(wt, val):
        cur = prev[:]          # leaving the item is the default
        for c in range(w, W + 1):
            cur[c] = max(prev[c], v + prev[c - w])
        prev = cur
    return prev[W]''',
            ),
            dict(
                name="One row, capacity downwards",
                time="O(n&middot;W)",
                space="O(W)",
                best=True,
                change="Drop <code>cur</code> and write into <code>prev</code> directly, looping capacity from <code>W</code> <strong>down</strong> to <code>w</code>.",
                why=[
                    "Cell <code>c</code> reads <code>prev[c]</code> and <code>prev[c - w]</code> &mdash; the same capacity and a <em>smaller</em> one.",
                    "Going downwards, when you update <code>dp[c]</code>, the smaller cell <code>dp[c - w]</code> has not been touched yet this round. It still holds the previous row. So one array serves as both rows.",
                    "Go upwards instead and <code>dp[c - w]</code> may already include this item, so the item can be taken twice. That is unbounded knapsack, and it is the most common bug in this pattern.",
                    "Same big-O space as two rows, but half the memory and no copying.",
                ],
                code='''def knapsack(W, val, wt):
    dp = [0] * (W + 1)
    for w, v in zip(wt, val):
        for c in range(W, w - 1, -1):     # downwards: each item once
            dp[c] = max(dp[c], v + dp[c - w])
    return dp[W]''',
            ),
        ],
        tests='''assert knapsack(4, [1, 2, 3], [4, 5, 1]) == 3
assert knapsack(3, [1, 2, 3], [4, 5, 6]) == 0
assert knapsack(50, [60, 100, 120], [10, 20, 30]) == 220
assert knapsack(5, [10, 40, 30, 50], [5, 4, 6, 3]) == 50


def brute(W, val, wt):
    best = 0
    for mask in range(1 << len(val)):
        items = [i for i in range(len(val)) if mask >> i & 1]
        if sum(wt[i] for i in items) <= W:
            best = max(best, sum(val[i] for i in items))
    return best


random.seed(7)
for _ in range(60):
    n = random.randint(1, 10)
    val = [random.randint(1, 30) for _ in range(n)]
    wt = [random.randint(1, 15) for _ in range(n)]
    W = random.randint(1, 40)
    assert knapsack(W, val, wt) == brute(W, val, wt), (W, val, wt)''',
        pitfall="Looping capacity upwards in the one-row version, which silently lets each item be taken many times.",
    ),

    dict(
        id="partition-equal-subset-sum",
        lc=416, slug="partition-equal-subset-sum",
        name="Partition Equal Subset Sum",
        difficulty="medium",
        recurrence=dict(
            state="<code>can(i, s)</code> = can some subset of the first <code>i</code> numbers sum to exactly <code>s</code>?",
            derive=[
                "Two equal halves exist exactly when some subset sums to <code>total / 2</code>. If the total is odd, stop: the answer is no.",
                "So the question is subset sum: 0/1 knapsack where each cell is True/False instead of a value.",
                "<strong>Leave</strong> <code>nums[i-1]</code>: <code>can(i-1, s)</code>. <strong>Use it</strong> (if it is not bigger than <code>s</code>): <code>can(i-1, s - nums[i-1])</code>.",
                "Either one working is enough, so combine with <code>or</code>.",
            ],
            formula='''can(i, s) = can(i-1, s)                            leave nums[i-1]
         or can(i-1, s - nums[i-1])                 use it, if nums[i-1] <= s
can(i, 0) = True           the empty subset sums to 0
can(0, s) = False          for s > 0: no numbers left
answer: total is even and can(n, total // 2)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Tries every subset: each number is used or not.",
                    "Returns as soon as one branch succeeds, which helps on yes-instances but not on no-instances.",
                ],
                code='''def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False

    def can(i, s):             # can the first i numbers make s?
        if s == 0:
            return True
        if i == 0:
            return False
        if nums[i - 1] <= s and can(i - 1, s - nums[i - 1]):
            return True
        return can(i - 1, s)
    return can(len(nums), total // 2)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&middot;S)",
                space="O(n&middot;S)",
                change="Cache on <code>(i, s)</code>, where <code>S</code> is the half-sum. At most <code>(n+1)(S+1)</code> states.",
                why=[
                    "Many subsets of the first few numbers leave the same remaining sum; the cache answers each <code>(i, s)</code> once.",
                ],
                code='''def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False

    @cache
    def can(i, s):
        if s == 0:
            return True
        if i == 0:
            return False
        if nums[i - 1] <= s and can(i - 1, s - nums[i - 1]):
            return True
        return can(i - 1, s)
    return can(len(nums), total // 2)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&middot;S)",
                space="O(n&middot;S)",
                change="Fill a boolean table <code>dp[i][s]</code> row by row. Column 0 is all True, row 0 is False elsewhere.",
                why=[
                    "Each row reads only the row above, at the same or a smaller sum.",
                    "Row <code>i</code> is \"every sum reachable using the first <code>i</code> numbers\".",
                ],
                code='''def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    half, n = total // 2, len(nums)
    dp = [[False] * (half + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = True
    for i in range(1, n + 1):
        x = nums[i - 1]
        for s in range(1, half + 1):
            dp[i][s] = dp[i - 1][s] or (x <= s and dp[i - 1][s - x])
    return dp[n][half]''',
            ),
            dict(
                name="Two rows",
                time="O(n&middot;S)",
                space="O(S)",
                change="Only row <code>i-1</code> is ever read. Keep it as <code>prev</code> and build <code>cur</code> from it.",
                why=[
                    "Space falls from <code>n&middot;S</code> to <code>2S</code>.",
                    "<code>cur = prev[:]</code> covers \"leave the number\" for every sum; the loop adds \"use it\".",
                ],
                code='''def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    half = total // 2
    prev = [True] + [False] * half
    for x in nums:
        cur = prev[:]
        for s in range(x, half + 1):
            cur[s] = prev[s] or prev[s - x]
        prev = cur
    return prev[half]''',
            ),
            dict(
                name="One row, sum downwards",
                time="O(n&middot;S)",
                space="O(S)",
                best=True,
                change="Update one array in place, running <code>s</code> from <code>half</code> <strong>down</strong> to <code>x</code>, and stop early once <code>half</code> is reachable.",
                why=[
                    "Cell <code>s</code> reads <code>s</code> and the smaller <code>s - x</code>. Going downwards, <code>s - x</code> has not been updated yet this round, so it still means \"reachable without <code>x</code>\". Each number is used once.",
                    "Upwards would let <code>x</code> be used repeatedly: <code>[1]</code> would reach every sum.",
                    "<code>S</code> is at most 10<sup>4</sup> here, so about 2&times;10<sup>6</sup> steps.",
                ],
                code='''def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    half = total // 2
    can = [True] + [False] * half
    for x in nums:
        for s in range(half, x - 1, -1):
            if can[s - x]:
                can[s] = True
        if can[half]:
            return True
    return can[half]''',
            ),
            dict(
                name="Bitset of reachable sums",
                time="O(n&middot;S / w)",
                space="O(S)",
                tag="Python int trick",
                why=[
                    "Store the one-row table as the bits of a single integer: bit <code>s</code> is set if <code>s</code> is reachable.",
                    "Adding <code>x</code> is <code>bits |= bits &lt;&lt; x</code>: every reachable sum also becomes reachable plus <code>x</code>. The shift reads the old value, so each number is used once, just like the downward loop.",
                    "Each shift processes a whole machine word of cells at once. Typically an order of magnitude faster in Python.",
                ],
                code='''def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    bits = 1                   # only sum 0 reachable
    for x in nums:
        bits |= bits << x
    return bool(bits >> (total // 2) & 1)''',
            ),
        ],
        tests='''assert can_partition([1, 5, 11, 5]) is True
assert can_partition([1, 2, 3, 5]) is False
assert can_partition([1]) is False
assert can_partition([2, 2]) is True
assert can_partition([1, 2, 5]) is False


def brute(nums):
    total = sum(nums)
    return any(2 * sum(c) == total
               for r in range(len(nums) + 1)
               for c in itertools.combinations(nums, r))


random.seed(8)
for _ in range(80):
    data = [random.randint(1, 20) for _ in range(random.randint(1, 12))]
    assert can_partition(data) == brute(data), data''',
    ),

    dict(
        id="target-sum",
        lc=494, slug="target-sum",
        name="Target Sum",
        difficulty="medium",
        recurrence=dict(
            state="<code>count(i, s)</code> = the number of ways to put a sign on each of the first <code>i</code> numbers so that they add up to <code>s</code>.",
            derive=[
                "Look at the last number in play, <code>x = nums[i-1]</code>. It got either a <code>+</code> or a <code>-</code>.",
                "If it got <code>+</code>, the first <code>i-1</code> numbers had to make <code>s - x</code>. If it got <code>-</code>, they had to make <code>s + x</code>.",
                "The two cases differ in the sign of <code>x</code>, so they never double count: add them.",
            ],
            formula='''count(i, s) = count(i-1, s - x)        x = nums[i-1] got a +
            + count(i-1, s + x)        x got a -
count(0, s) = 1 if s == 0 else 0
answer: count(n, target)''',
            notes=[
                "This is the direct model of the problem. It gets you to two rows. Step 5 uses a line of algebra to turn it into a subset-count knapsack, which is what gets you to one row.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Two signs per number: every one of the 2<sup>n</sup> sign patterns is tried.",
                ],
                code='''def find_target_sum_ways(nums, target):
    def count(i, s):           # sign the first i numbers to make s
        if i == 0:
            return 1 if s == 0 else 0
        x = nums[i - 1]
        return count(i - 1, s - x) + count(i - 1, s + x)
    return count(len(nums), target)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&middot;T)",
                space="O(n&middot;T)",
                change="Cache on <code>(i, s)</code>. The sums that matter lie in <code>[-T, T]</code> where <code>T = sum(nums)</code>, so there are at most <code>n(2T + 1)</code> states.",
                why=[
                    "Different sign patterns on the first few numbers often land on the same partial sum. The cache counts the rest once.",
                ],
                code='''def find_target_sum_ways(nums, target):
    @cache
    def count(i, s):
        if i == 0:
            return 1 if s == 0 else 0
        x = nums[i - 1]
        return count(i - 1, s - x) + count(i - 1, s + x)
    return count(len(nums), target)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&middot;T)",
                space="O(n&middot;T)",
                change="Sums can be negative, so shift them: column <code>s + T</code> holds sum <code>s</code>. Fill row by row.",
                why=[
                    "<code>dp[i][s + T]</code> pulls from <code>s - x</code> and <code>s + x</code> in row <code>i-1</code>, when those are inside <code>[-T, T]</code>.",
                    "If <code>|target| &gt; T</code> it is unreachable, and it would not even have a column.",
                ],
                code='''def find_target_sum_ways(nums, target):
    T = sum(nums)
    if abs(target) > T:
        return 0
    n = len(nums)
    dp = [[0] * (2 * T + 1) for _ in range(n + 1)]
    dp[0][T] = 1                       # column s + T holds sum s
    for i in range(1, n + 1):
        x = nums[i - 1]
        for s in range(-T, T + 1):
            if s - x >= -T:
                dp[i][s + T] += dp[i - 1][s - x + T]
            if s + x <= T:
                dp[i][s + T] += dp[i - 1][s + x + T]
    return dp[n][target + T]''',
            ),
            dict(
                name="Two rows",
                time="O(n&middot;T)",
                space="O(T)",
                change="Each row reads only the row before. Keep <code>prev</code>, build a fresh <code>cur</code>.",
                why=[
                    "Why not one row? Cell <code>s</code> reads <em>both</em> <code>s - x</code> and <code>s + x</code>: one smaller, one larger. Whichever direction you loop, one of those two has already been overwritten. So this model stops at two rows.",
                ],
                code='''def find_target_sum_ways(nums, target):
    T = sum(nums)
    if abs(target) > T:
        return 0
    prev = [0] * (2 * T + 1)
    prev[T] = 1
    for x in nums:
        cur = [0] * (2 * T + 1)
        for s in range(-T, T + 1):
            if s - x >= -T:
                cur[s + T] += prev[s - x + T]
            if s + x <= T:
                cur[s + T] += prev[s + x + T]
        prev = cur
    return prev[target + T]''',
            ),
            dict(
                name="Reduce to subset count, one row",
                time="O(n&middot;P)",
                space="O(P)",
                best=True,
                change="Change the model. Let <code>P</code> be the sum of the numbers given <code>+</code>. Then the answer is the number of subsets summing to <code>P = (T + target) / 2</code> &mdash; a counting 0/1 knapsack that reads only one side, so one row works.",
                why=[
                    "<strong>The algebra:</strong> call the plus-group's sum <code>P</code> and the minus-group's <code>N</code>. Then <code>P - N = target</code> and <code>P + N = T</code>. Add them: <code>P = (T + target) / 2</code>.",
                    "If <code>T + target</code> is odd, or <code>|target| &gt; T</code>, no split works: return 0.",
                    "<strong>New recurrence:</strong> <code>ways(i, s) = ways(i-1, s) + ways(i-1, s - x)</code>. It reads only the same and a <em>smaller</em> sum, so looping <code>s</code> downwards makes one row safe, as in 0/1 knapsack.",
                    "The range also shrinks from <code>2T + 1</code> columns to <code>P + 1 &le; T + 1</code>.",
                    "Zeros need no special case: <code>ways[s] += ways[s - 0]</code> doubles the count, matching <code>+0</code> and <code>-0</code>.",
                ],
                code='''def find_target_sum_ways(nums, target):
    T = sum(nums)
    if abs(target) > T or (T + target) % 2:
        return 0
    P = (T + target) // 2
    ways = [1] + [0] * P
    for x in nums:
        for s in range(P, x - 1, -1):     # downwards: each number once
            ways[s] += ways[s - x]
    return ways[P]''',
            ),
        ],
        tests='''assert find_target_sum_ways([1, 1, 1, 1, 1], 3) == 5
assert find_target_sum_ways([1], 1) == 1
assert find_target_sum_ways([1], 2) == 0
assert find_target_sum_ways([0, 0, 1], 1) == 4
assert find_target_sum_ways([100], -200) == 0


def brute(nums, target):
    return sum(1 for signs in itertools.product((1, -1), repeat=len(nums))
               if sum(s * x for s, x in zip(signs, nums)) == target)


random.seed(9)
for _ in range(60):
    data = [random.randint(0, 6) for _ in range(random.randint(1, 10))]
    t = random.randint(-10, 10)
    assert find_target_sum_ways(data, t) == brute(data, t), (data, t)''',
    ),

    dict(
        id="last-stone-weight-ii",
        lc=1049, slug="last-stone-weight-ii",
        name="Last Stone Weight II",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, a)</code> = the smallest possible final stone, once stones <code>i..n-1</code> are still to be placed and the stones already placed in group A weigh <code>a</code>.",
            derive=[
                "Every smash subtracts one stone from another, so the final stone is a signed sum <code>&plusmn;s<sub>1</sub> &plusmn; s<sub>2</sub> &hellip;</code>: the stones split into two groups A and B, and what is left is <code>|A - B| = |total - 2A|</code>.",
                "Every split can actually be produced by some smash order, so the question is just: which split makes <code>|total - 2A|</code> smallest?",
                "Each stone goes into A or into B. Try both.",
            ],
            formula='''f(i, a) = min(f(i+1, a + stones[i]),     stone i joins group A
              f(i+1, a))                  stone i joins group B
f(n, a) = |total - 2a|
answer: f(0, 0)''',
            notes=[
                "For the table, flip the question round: which weights <code>a</code> can group A reach using the first <code>i</code> stones? That is subset sum again, and the answer is <code>total - 2a</code> for the largest reachable <code>a &le; total / 2</code>.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Every stone goes into A or B: all 2<sup>n</sup> splits are tried.",
                ],
                code='''def last_stone_weight_ii(stones):
    total = sum(stones)

    def f(i, a):               # stones i.. still to place, group A weighs a
        if i == len(stones):
            return abs(total - 2 * a)
        return min(f(i + 1, a + stones[i]), f(i + 1, a))
    return f(0, 0)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&middot;T)",
                space="O(n&middot;T)",
                change="Cache on <code>(i, a)</code>. <code>a</code> never exceeds <code>T = total</code>, so there are at most <code>n(T + 1)</code> states.",
                why=[
                    "Many splits of the first few stones give the same weight in A. From there the best finish is the same, so it is solved once.",
                ],
                code='''def last_stone_weight_ii(stones):
    total = sum(stones)

    @cache
    def f(i, a):
        if i == len(stones):
            return abs(total - 2 * a)
        return min(f(i + 1, a + stones[i]), f(i + 1, a))
    return f(0, 0)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&middot;T)",
                space="O(n&middot;T)",
                change="Build forwards instead: <code>can[i][a]</code> = can group A weigh exactly <code>a</code> using the first <code>i</code> stones? Only weights up to <code>total // 2</code> matter.",
                why=[
                    "This is Partition's table. <code>can[i][a] = can[i-1][a] or can[i-1][a - stone]</code>.",
                    "Group A can always be taken as the lighter group, so only <code>a &le; total // 2</code> is needed. The best answer uses the largest reachable such <code>a</code>.",
                ],
                code='''def last_stone_weight_ii(stones):
    total = sum(stones)
    half, n = total // 2, len(stones)
    can = [[False] * (half + 1) for _ in range(n + 1)]
    can[0][0] = True
    for i in range(1, n + 1):
        x = stones[i - 1]
        for a in range(half + 1):
            can[i][a] = can[i - 1][a] or (x <= a and can[i - 1][a - x])
    best = max(a for a in range(half + 1) if can[n][a])
    return total - 2 * best''',
            ),
            dict(
                name="Two rows",
                time="O(n&middot;T)",
                space="O(T)",
                change="Only the previous row is read: keep <code>prev</code>, build <code>cur</code>.",
                why=[
                    "Space falls from <code>n&middot;T</code> to <code>2 &middot; (T/2)</code>.",
                ],
                code='''def last_stone_weight_ii(stones):
    total = sum(stones)
    half = total // 2
    prev = [True] + [False] * half
    for x in stones:
        cur = prev[:]
        for a in range(x, half + 1):
            cur[a] = prev[a] or prev[a - x]
        prev = cur
    best = max(a for a in range(half + 1) if prev[a])
    return total - 2 * best''',
            ),
            dict(
                name="One row, weight downwards",
                time="O(n&middot;T)",
                space="O(T)",
                best=True,
                change="Update one array in place with <code>a</code> running <strong>downwards</strong>.",
                why=[
                    "Cell <code>a</code> reads <code>a</code> and the smaller <code>a - x</code>. Downwards, <code>a - x</code> still holds the previous row, so each stone is used once. The same argument as 0/1 knapsack.",
                    "Once the reduction is seen, this is Partition Equal Subset Sum asking \"how close?\" instead of \"exactly?\".",
                ],
                code='''def last_stone_weight_ii(stones):
    total = sum(stones)
    half = total // 2
    can = [True] + [False] * half
    for x in stones:
        for a in range(half, x - 1, -1):
            if can[a - x]:
                can[a] = True
    best = max(a for a in range(half + 1) if can[a])
    return total - 2 * best''',
            ),
        ],
        tests='''assert last_stone_weight_ii([2, 7, 4, 1, 8, 1]) == 1
assert last_stone_weight_ii([31, 26, 33, 21, 40]) == 5
assert last_stone_weight_ii([1]) == 1
assert last_stone_weight_ii([3, 3]) == 0


def brute(stones):
    return min(abs(sum(s * x for s, x in zip(signs, stones)))
               for signs in itertools.product((1, -1), repeat=len(stones)))


random.seed(10)
for _ in range(60):
    data = [random.randint(1, 30) for _ in range(random.randint(1, 10))]
    assert last_stone_weight_ii(data) == brute(data), data''',
    ),

    dict(
        id="ones-and-zeroes",
        lc=474, slug="ones-and-zeroes",
        name="Ones and Zeroes",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, z, o)</code> = the most strings you can pick from the first <code>i</code> strings using at most <code>z</code> zeros and <code>o</code> ones.",
            derive=[
                "Each string is an item with <em>two</em> weights, its count of zeros and its count of ones, and value 1.",
                "The bag has two capacities, <code>m</code> zeros and <code>n</code> ones. So the state gains one dimension compared with 0/1 knapsack.",
                "<strong>Leave</strong> string <code>i-1</code>: <code>f(i-1, z, o)</code>. <strong>Take it</strong> if both its counts fit: <code>1 + f(i-1, z - zeros, o - ones)</code>.",
            ],
            formula='''f(i, z, o) = max(f(i-1, z, o),                          leave string i-1
                 1 + f(i-1, z - zeros, o - ones))        take it, if it fits
f(0, z, o) = 0
answer: f(L, m, n)          L = len(strs)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>L</sup>)",
                space="O(L)",
                tag="brute force",
                why=[
                    "Each string is left or taken: every subset of strings is tried.",
                ],
                code='''def find_max_form(strs, m, n):
    cost = [(s.count("0"), s.count("1")) for s in strs]

    def f(i, z, o):            # most of the first i strings within z zeros, o ones
        if i == 0:
            return 0
        best = f(i - 1, z, o)
        cz, co = cost[i - 1]
        if cz <= z and co <= o:
            best = max(best, 1 + f(i - 1, z - cz, o - co))
        return best
    return f(len(strs), m, n)''',
            ),
            dict(
                name="Top-down memo",
                time="O(L&middot;m&middot;n)",
                space="O(L&middot;m&middot;n)",
                change="Cache on <code>(i, z, o)</code>: at most <code>(L+1)(m+1)(n+1)</code> states.",
                why=[
                    "Three-dimensional state, so the cache is three-dimensional too.",
                ],
                code='''def find_max_form(strs, m, n):
    cost = [(s.count("0"), s.count("1")) for s in strs]

    @cache
    def f(i, z, o):
        if i == 0:
            return 0
        best = f(i - 1, z, o)
        cz, co = cost[i - 1]
        if cz <= z and co <= o:
            best = max(best, 1 + f(i - 1, z - cz, o - co))
        return best
    return f(len(strs), m, n)''',
            ),
            dict(
                name="Bottom-up 3-D table",
                time="O(L&middot;m&middot;n)",
                space="O(L&middot;m&middot;n)",
                change="Fill <code>dp[i][z][o]</code> one layer (one value of <code>i</code>) at a time.",
                why=[
                    "Layer <code>i</code> reads only layer <code>i-1</code>, at the same or smaller <code>(z, o)</code>.",
                    "Here the \"rows\" of the other problems are whole 2-D layers, but the same shrinking steps apply.",
                ],
                code='''def find_max_form(strs, m, n):
    cost = [(s.count("0"), s.count("1")) for s in strs]
    L = len(strs)
    dp = [[[0] * (n + 1) for _ in range(m + 1)] for _ in range(L + 1)]
    for i in range(1, L + 1):
        cz, co = cost[i - 1]
        for z in range(m + 1):
            for o in range(n + 1):
                dp[i][z][o] = dp[i - 1][z][o]
                if cz <= z and co <= o:
                    dp[i][z][o] = max(dp[i][z][o], 1 + dp[i - 1][z - cz][o - co])
    return dp[L][m][n]''',
            ),
            dict(
                name="Two layers",
                time="O(L&middot;m&middot;n)",
                space="O(m&middot;n)",
                change="Only layer <code>i-1</code> is read. Keep it as <code>prev</code> (an <code>(m+1) &times; (n+1)</code> grid) and build <code>cur</code>.",
                why=[
                    "The string dimension disappears from memory: space falls by a factor of <code>L</code>.",
                ],
                code='''def find_max_form(strs, m, n):
    prev = [[0] * (n + 1) for _ in range(m + 1)]
    for s in strs:
        cz = s.count("0")
        co = len(s) - cz
        cur = [row[:] for row in prev]
        for z in range(cz, m + 1):
            for o in range(co, n + 1):
                cur[z][o] = max(prev[z][o], 1 + prev[z - cz][o - co])
        prev = cur
    return prev[m][n]''',
            ),
            dict(
                name="One layer, both capacities downwards",
                time="O(L&middot;m&middot;n)",
                space="O(m&middot;n)",
                best=True,
                change="Update one grid in place, with <strong>both</strong> <code>z</code> and <code>o</code> running downwards.",
                why=[
                    "Cell <code>(z, o)</code> reads itself and <code>(z - cz, o - co)</code>, which is smaller in both coordinates.",
                    "Downwards in both, that smaller cell has not been touched yet for this string, so it still belongs to the previous layer. Each string is used once.",
                    "No copy per string, so it is also faster than two layers.",
                ],
                code='''def find_max_form(strs, m, n):
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for s in strs:
        zeros = s.count("0")
        ones = len(s) - zeros
        for z in range(m, zeros - 1, -1):
            for o in range(n, ones - 1, -1):
                dp[z][o] = max(dp[z][o], dp[z - zeros][o - ones] + 1)
    return dp[m][n]''',
            ),
        ],
        tests='''assert find_max_form(["10", "0001", "111001", "1", "0"], 5, 3) == 4
assert find_max_form(["10", "0", "1"], 1, 1) == 2
assert find_max_form(["111"], 5, 2) == 0


def brute(strs, m, n):
    best = 0
    for r in range(len(strs) + 1):
        for pick in itertools.combinations(strs, r):
            text = "".join(pick)
            if text.count("0") <= m and text.count("1") <= n:
                best = max(best, r)
    return best


random.seed(11)
for _ in range(50):
    strs = ["".join(random.choice("01") for _ in range(random.randint(1, 4)))
            for _ in range(random.randint(1, 8))]
    m, n = random.randint(0, 6), random.randint(0, 6)
    assert find_max_form(strs, m, n) == brute(strs, m, n), (strs, m, n)''',
    ),

    dict(
        id="coin-change",
        lc=322, slug="coin-change",
        name="Coin Change",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, a)</code> = the fewest coins needed to make amount <code>a</code> using only the first <code>i</code> coin types.",
            derive=[
                "Look at coin type <code>i-1</code>, with value <code>c</code>. Either you never use it, or you use it at least once more.",
                "<strong>Never use it:</strong> <code>f(i-1, a)</code>.",
                "<strong>Use one more:</strong> <code>1 + f(i, a - c)</code>. Note it stays at <code>i</code>, not <code>i-1</code>: the coin is still available. <em>That one index is the whole difference between 0/1 and unbounded knapsack.</em>",
                "An amount that cannot be made is infinity, so it always loses a <code>min</code>.",
            ],
            formula='''f(i, a) = min(f(i-1, a),                 never use coin i-1
              1 + f(i, a - c))          use it once more, if c <= a   (c = coins[i-1])
f(i, 0) = 0                  nothing left to make
f(0, a) = inf   for a > 0    no coins left
answer: f(k, amount), or -1 if it is inf''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="exponential",
                space="O(k + A)",
                tag="brute force",
                small=True,
                why=[
                    "Tries every multiset of coins. The count of those grows exponentially with the amount.",
                    "The stack can be <code>k + A</code> deep: <code>A</code> uses of a 1-coin plus one level per coin type skipped.",
                ],
                code='''def coin_change(coins, amount):
    def f(i, a):               # fewest of the first i coin types making a
        if a == 0:
            return 0
        if i == 0:
            return inf
        best = f(i - 1, a)
        c = coins[i - 1]
        if c <= a:
            best = min(best, 1 + f(i, a - c))
        return best
    ans = f(len(coins), amount)
    return ans if ans != inf else -1''',
            ),
            dict(
                name="Top-down memo",
                time="O(k&middot;A)",
                space="O(k&middot;A)",
                change="Cache on <code>(i, a)</code>: <code>(k+1)(A+1)</code> states, each O(1).",
                why=[
                    "<code>k</code> coin types, amount <code>A</code>.",
                    "With a 1-coin and <code>A = 10<sup>4</sup></code> the recursion is 10<sup>4</sup> deep, past Python's limit. The table is the safe version.",
                ],
                code='''def coin_change(coins, amount):
    @cache
    def f(i, a):
        if a == 0:
            return 0
        if i == 0:
            return inf
        best = f(i - 1, a)
        c = coins[i - 1]
        if c <= a:
            best = min(best, 1 + f(i, a - c))
        return best
    ans = f(len(coins), amount)
    return ans if ans != inf else -1''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(k&middot;A)",
                space="O(k&middot;A)",
                change="Fill <code>dp[i][a]</code> row by row, amounts left to right. Row 0 is <code>[0, inf, inf, &hellip;]</code>.",
                why=[
                    "<code>dp[i][a]</code> reads <code>dp[i-1][a]</code> (row above) and <code>dp[i][a - c]</code> &mdash; the <em>same</em> row, to the left.",
                    "Left to right guarantees that same-row cell is already filled. Compare with 0/1 knapsack, which read <code>dp[i-1][c - w]</code> in the row above.",
                ],
                code='''def coin_change(coins, amount):
    k = len(coins)
    dp = [[inf] * (amount + 1) for _ in range(k + 1)]
    for i in range(k + 1):
        dp[i][0] = 0
    for i in range(1, k + 1):
        c = coins[i - 1]
        for a in range(1, amount + 1):
            dp[i][a] = dp[i - 1][a]
            if c <= a:
                dp[i][a] = min(dp[i][a], 1 + dp[i][a - c])
    return dp[k][amount] if dp[k][amount] != inf else -1''',
            ),
            dict(
                name="Two rows",
                time="O(k&middot;A)",
                space="O(A)",
                change="Keep <code>prev</code> (row <code>i-1</code>) and build <code>cur</code> (row <code>i</code>). <code>cur</code> reads itself to the left, as the table did.",
                why=[
                    "Space falls from <code>k&middot;A</code> to <code>2A</code>.",
                    "Look at what <code>cur[a]</code> needs: <code>prev[a]</code> and <code>cur[a - c]</code>. If <code>cur</code> started as a copy of <code>prev</code>, then <code>prev[a]</code> is just \"<code>cur[a]</code> before it is updated\". That observation is the next step.",
                ],
                code='''def coin_change(coins, amount):
    prev = [0] + [inf] * amount
    for c in coins:
        cur = prev[:]
        for a in range(c, amount + 1):
            cur[a] = min(prev[a], 1 + cur[a - c])
        prev = cur
    return prev[amount] if prev[amount] != inf else -1''',
            ),
            dict(
                name="One row, amount upwards",
                time="O(k&middot;A)",
                space="O(A)",
                best=True,
                change="Use one array. Before <code>dp[a]</code> is updated it still holds the previous row; <code>dp[a - c]</code> to its left is already this row. Looping amount <strong>upwards</strong> gives exactly those two.",
                why=[
                    "Upwards means <code>dp[a - c]</code> may already use coin <code>c</code>, so <code>c</code> can be used again. For unbounded knapsack that is correct.",
                    "It is the mirror image of 0/1 knapsack, where the loop ran downwards precisely to forbid this.",
                    "Greedy (always take the biggest coin) is wrong: with coins [1, 3, 4] and amount 6, greedy takes 4+1+1 = 3 coins but 3+3 is 2.",
                ],
                code='''def coin_change(coins, amount):
    dp = [0] + [inf] * amount
    for c in coins:
        for a in range(c, amount + 1):     # upwards: coin c reusable
            dp[a] = min(dp[a], 1 + dp[a - c])
    return dp[amount] if dp[amount] != inf else -1''',
            ),
            dict(
                name="BFS over amounts",
                time="O(k&middot;A)",
                space="O(A)",
                tag="shortest-path view",
                why=[
                    "Amounts are nodes and each coin is an edge of weight 1, so the fewest coins is the shortest path from 0 to <code>A</code>.",
                    "Same worst case as the table, but it stops at the answer's level, which is often much sooner.",
                ],
                code='''def coin_change(coins, amount):
    from collections import deque
    if amount == 0:
        return 0
    seen = {0}
    queue = deque([(0, 0)])
    while queue:
        value, steps = queue.popleft()
        for c in coins:
            nxt = value + c
            if nxt == amount:
                return steps + 1
            if nxt < amount and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, steps + 1))
    return -1''',
            ),
        ],
        tests='''assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1
assert coin_change([1], 0) == 0
assert coin_change([1, 3, 4], 6) == 2
assert coin_change([186, 419, 83, 408], 6249) == 20


def brute(coins, amount):
    @cache
    def go(a):
        if a == 0:
            return 0
        opts = [go(a - c) for c in coins if c <= a]
        opts = [o for o in opts if o >= 0]
        return 1 + min(opts) if opts else -1
    return go(amount)


random.seed(12)
for _ in range(60):
    coins = random.sample(range(1, 15), random.randint(1, 4))
    amount = random.randint(0, 60)
    assert coin_change(coins, amount) == brute(coins, amount), (coins, amount)''',
        small_tests='''assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1
assert coin_change([1], 0) == 0
assert coin_change([1, 3, 4], 6) == 2


def brute(coins, amount):
    @cache
    def go(a):
        if a == 0:
            return 0
        opts = [go(a - c) for c in coins if c <= a]
        opts = [o for o in opts if o >= 0]
        return 1 + min(opts) if opts else -1
    return go(amount)


random.seed(12)
for _ in range(40):
    coins = random.sample(range(1, 10), random.randint(1, 3))
    amount = random.randint(0, 18)
    assert coin_change(coins, amount) == brute(coins, amount), (coins, amount)''',
    ),

    dict(
        id="coin-change-ii",
        lc=518, slug="coin-change-ii",
        name="Coin Change II",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, a)</code> = the number of <em>combinations</em> of the first <code>i</code> coin types that make amount <code>a</code>.",
            derive=[
                "Same split as Coin Change, but counting instead of minimising: never use coin <code>i-1</code> again, or use it once more.",
                "<strong>Never again:</strong> <code>f(i-1, a)</code>. <strong>Once more:</strong> <code>f(i, a - c)</code>, staying at <code>i</code> because coins are reusable.",
                "Once you move past a coin you never come back to it. So every combination is built in coin order, and <code>1+2</code> and <code>2+1</code> are the same path. That is why this counts combinations, not orderings.",
            ],
            formula='''f(i, a) = f(i-1, a)             never use coin i-1 again
        + f(i, a - c)           use it once more, if c <= a   (c = coins[i-1])
f(i, 0) = 1                     one way to make 0: take nothing
f(0, a) = 0   for a > 0
answer: f(k, amount)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="exponential",
                space="O(k + A)",
                tag="brute force",
                small=True,
                why=[
                    "Enumerates every combination one path at a time, so it is at least as slow as the answer is large.",
                ],
                code='''def change(amount, coins):
    def f(i, a):               # combinations of the first i coin types making a
        if a == 0:
            return 1
        if i == 0:
            return 0
        c = coins[i - 1]
        ways = f(i - 1, a)
        if c <= a:
            ways += f(i, a - c)
        return ways
    return f(len(coins), amount)''',
            ),
            dict(
                name="Top-down memo",
                time="O(k&middot;A)",
                space="O(k&middot;A)",
                change="Cache on <code>(i, a)</code>.",
                why=[
                    "<code>(k+1)(A+1)</code> states, O(1) each.",
                ],
                code='''def change(amount, coins):
    @cache
    def f(i, a):
        if a == 0:
            return 1
        if i == 0:
            return 0
        c = coins[i - 1]
        ways = f(i - 1, a)
        if c <= a:
            ways += f(i, a - c)
        return ways
    return f(len(coins), amount)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(k&middot;A)",
                space="O(k&middot;A)",
                change="Fill <code>dp[i][a]</code> row by row, amounts left to right. Column 0 is all 1.",
                why=[
                    "<code>dp[i][a]</code> reads the row above and the same row to the left, as in Coin Change.",
                ],
                code='''def change(amount, coins):
    k = len(coins)
    dp = [[0] * (amount + 1) for _ in range(k + 1)]
    for i in range(k + 1):
        dp[i][0] = 1
    for i in range(1, k + 1):
        c = coins[i - 1]
        for a in range(1, amount + 1):
            dp[i][a] = dp[i - 1][a] + (dp[i][a - c] if c <= a else 0)
    return dp[k][amount]''',
            ),
            dict(
                name="Two rows",
                time="O(k&middot;A)",
                space="O(A)",
                change="Keep only the previous row as <code>prev</code>; build <code>cur</code>, reading <code>cur</code> to the left.",
                why=[
                    "Space falls from <code>k&middot;A</code> to <code>2A</code>.",
                ],
                code='''def change(amount, coins):
    prev = [1] + [0] * amount
    for c in coins:
        cur = prev[:]
        for a in range(c, amount + 1):
            cur[a] = prev[a] + cur[a - c]
        prev = cur
    return prev[amount]''',
            ),
            dict(
                name="One row, coins outer, amount upwards",
                time="O(k&middot;A)",
                space="O(A)",
                best=True,
                change="One array: before the update <code>ways[a]</code> is the previous row, and <code>ways[a - c]</code> is already this row. Amount runs upwards.",
                why=[
                    "<strong>The loop order is the whole problem.</strong> Coins are the outer loop, so while coin <code>c</code> is being processed the table only holds ways built from earlier coins. Every combination is counted once, in coin order.",
                    "Put amount outside and coins inside and every amount tries every coin as its <em>last</em> coin. That counts <code>1+2</code> and <code>2+1</code> separately: it is Combination Sum IV (LeetCode 377), not this problem.",
                    "In Coin Change I the order did not matter, because a minimum does not care how many orders reach it.",
                ],
                code='''def change(amount, coins):
    ways = [1] + [0] * amount
    for c in coins:
        for a in range(c, amount + 1):
            ways[a] += ways[a - c]
    return ways[amount]''',
            ),
        ],
        tests='''assert change(5, [1, 2, 5]) == 4
assert change(3, [2]) == 0
assert change(10, [10]) == 1
assert change(0, [7]) == 1


def brute(amount, coins):
    def go(i, a):
        if a == 0:
            return 1
        if i == len(coins):
            return 0
        return sum(go(i + 1, a - k * coins[i]) for k in range(a // coins[i] + 1))
    return go(0, amount)


random.seed(13)
for _ in range(60):
    coins = random.sample(range(1, 12), random.randint(1, 4))
    amount = random.randint(0, 40)
    assert change(amount, coins) == brute(amount, coins), (amount, coins)''',
        small_tests='''assert change(5, [1, 2, 5]) == 4
assert change(3, [2]) == 0
assert change(10, [10]) == 1
assert change(0, [7]) == 1


def brute(amount, coins):
    def go(i, a):
        if a == 0:
            return 1
        if i == len(coins):
            return 0
        return sum(go(i + 1, a - k * coins[i]) for k in range(a // coins[i] + 1))
    return go(0, amount)


random.seed(13)
for _ in range(40):
    coins = random.sample(range(1, 10), random.randint(1, 3))
    amount = random.randint(0, 18)
    assert change(amount, coins) == brute(amount, coins), (amount, coins)''',
        pitfall="Nesting the loops the other way round, which counts ordered sequences: <code>change(5, [1, 2, 5])</code> becomes 9 instead of 4.",
    ),

    dict(
        id="perfect-squares",
        lc=279, slug="perfect-squares",
        name="Perfect Squares",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(a)</code> = the fewest perfect squares that add up to <code>a</code>.",
            derive=[
                "Split on the last square used, <code>k&sup2;</code>. What is left, <code>a - k&sup2;</code>, must be made as cheaply as possible.",
                "Try every square that fits and keep the cheapest.",
                "This is Coin Change where the coins are <code>1, 4, 9, &hellip;</code>. Because the \"coins\" are fixed by <code>a</code>, a 1-D state is natural here.",
            ],
            formula='''f(a) = 1 + min(f(a - k*k)  for k = 1, 2, ...  while k*k <= a)
f(0) = 0
answer: f(n)''',
            notes=[
                "An answer always exists because 1 is a square, so there is no -1 case.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="exponential",
                space="O(n)",
                tag="brute force",
                small=True,
                why=[
                    "Every call branches once per square up to <code>a</code>. <code>f(a-1)</code> alone chains <code>n</code> calls deep, so the stack is O(n).",
                ],
                code='''def num_squares(n):
    def f(a):                  # fewest squares summing to a
        if a == 0:
            return 0
        best = inf
        k = 1
        while k * k <= a:
            best = min(best, 1 + f(a - k * k))
            k += 1
        return best
    return f(n)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&radic;n)",
                space="O(n)",
                change="Cache <code>f(a)</code>. There are <code>n + 1</code> amounts, each trying about <code>&radic;a</code> squares.",
                why=[
                    "O(n&radic;n) total. The recursion is up to <code>n</code> deep, fine for this problem's <code>n &le; 10<sup>4</sup></code> only if you raise the limit.",
                ],
                code='''def num_squares(n):
    @cache
    def f(a):
        if a == 0:
            return 0
        best = inf
        k = 1
        while k * k <= a:
            best = min(best, 1 + f(a - k * k))
            k += 1
        return best
    return f(n)''',
            ),
            dict(
                name="Bottom-up table",
                time="O(n&radic;n)",
                space="O(n)",
                best=True,
                change="Fill <code>dp[0..n]</code> from 0 upwards; every <code>dp[a - k&sup2;]</code> is smaller than <code>a</code>, so it is ready.",
                why=[
                    "<strong>Why stop here?</strong> <code>dp[a]</code> reads <code>dp[a-1]</code>, <code>dp[a-4]</code>, &hellip; up to <code>dp[a - &lfloor;&radic;a&rfloor;&sup2;]</code> &mdash; as far back as <code>a</code> itself. There is no fixed window to keep, so the array cannot shrink.",
                    "Compare Fibonacci, where every step looked back exactly two cells. The shape of the reads decides how far space can go.",
                ],
                code='''def num_squares(n):
    squares = [k * k for k in range(1, isqrt(n) + 1)]
    dp = [0] + [inf] * n
    for a in range(1, n + 1):
        for s in squares:
            if s > a:
                break
            if dp[a - s] + 1 < dp[a]:
                dp[a] = dp[a - s] + 1
    return dp[n]''',
            ),
            dict(
                name="Lagrange's four-square theorem",
                time="O(&radic;n)",
                space="O(1)",
                tag="math shortcut",
                why=[
                    "Every positive integer is a sum of at most four squares. It needs all four exactly when <code>n = 4<sup>a</sup>(8b + 7)</code>.",
                    "So: 1 if <code>n</code> is a square, 2 if it splits into two squares, 4 if it has that form, otherwise 3.",
                    "A great follow-up once the DP is written; not something you are expected to derive.",
                ],
                code='''def num_squares(n):
    if isqrt(n) ** 2 == n:
        return 1
    for a in range(1, isqrt(n) + 1):
        rest = n - a * a
        if isqrt(rest) ** 2 == rest:
            return 2
    m = n
    while m % 4 == 0:
        m //= 4
    return 4 if m % 8 == 7 else 3''',
            ),
        ],
        tests='''assert num_squares(12) == 3
assert num_squares(13) == 2
assert num_squares(1) == 1
assert num_squares(7) == 4
assert num_squares(28) == 4


def brute(n):
    from collections import deque
    seen, queue = {n}, deque([(n, 0)])
    while queue:
        v, d = queue.popleft()
        if v == 0:
            return d
        k = 1
        while k * k <= v:
            if v - k * k not in seen:
                seen.add(v - k * k)
                queue.append((v - k * k, d + 1))
            k += 1


for n in range(1, 300):
    assert num_squares(n) == brute(n), n''',
        small_tests='''assert num_squares(12) == 3
assert num_squares(13) == 2
assert num_squares(1) == 1
assert num_squares(7) == 4
assert [num_squares(n) for n in range(1, 21)] == [
    1, 2, 3, 1, 2, 3, 4, 2, 1, 2, 3, 3, 2, 3, 4, 1, 2, 2, 3, 2]''',
    ),
    ],
)

SECTIONS = [KNAPSACK]
