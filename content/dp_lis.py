# -*- coding: utf-8 -*-
"""DP pattern 4: the LIS family, written as a ladder."""

LIS = dict(
    id="lis",
    title="LIS family",
    summary="state = (index, last index taken); take or skip, then O(n log n) with binary search",
    idea=[
        "A subsequence skips elements, so each element is a take-or-skip choice &mdash; but whether you <em>may</em> take <code>nums[i]</code> depends on the last element you took. So the state is <code>(i, prev)</code>: where you are, and the index of the last element taken. That is O(n&sup2;) states with O(1) work each.",
        "The table over <code>(i, prev)</code> shrinks to two rows and then one, like every other 2-D table. There is also a different 1-D state worth knowing: <code>dp[i]</code> = longest subsequence <em>ending at</em> <code>i</code>, which extends any earlier <code>dp[j]</code> with a smaller value.",
        "The famous follow-up is <strong>O(n log n)</strong>. Keep <code>tails[k]</code> = the smallest possible last element of an increasing subsequence of length <code>k+1</code>. That array is always sorted, so each new number binary-searches the first tail &ge; it and overwrites it (or appends). The length of <code>tails</code> is the answer.",
        "Many problems are LIS after a sort. Russian Doll Envelopes sorts by one dimension so only the other needs an increasing subsequence; Maximum Length of Pair Chain sorts intervals so a chain becomes a subsequence. The skill is seeing which sort turns the problem into LIS &mdash; and handling ties so that equal keys cannot chain.",
    ],
    problems=[

    dict(
        id="longest-increasing-subsequence",
        lc=300, slug="longest-increasing-subsequence",
        name="Longest Increasing Subsequence",
        difficulty="medium",
        recurrence=dict(
            state="<code>f(i, prev)</code> = the length of the longest strictly increasing subsequence you can still pick from <code>nums[i:]</code>, given that the last element you took was <code>nums[prev]</code> (<code>prev = -1</code> means nothing taken yet).",
            derive=[
                "At index <code>i</code> you either skip <code>nums[i]</code> or take it.",
                "<strong>Skip:</strong> move on with the same <code>prev</code>: <code>f(i+1, prev)</code>.",
                "<strong>Take:</strong> only allowed if it is bigger than the last taken (or nothing is taken yet). It adds 1, and <code>i</code> becomes the new <code>prev</code>: <code>1 + f(i+1, i)</code>.",
                "\"Is taking allowed?\" depends on the last element taken, which is why <code>prev</code> must be part of the state.",
            ],
            formula='''f(i, prev) = max(f(i+1, prev),              skip nums[i]
                 1 + f(i+1, i))              take it, if prev == -1 or nums[prev] < nums[i]
f(n, prev) = 0                               nothing left
answer: f(0, -1)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Take or skip at every index: up to every subsequence is tried.",
                ],
                code='''def length_of_lis(nums):
    n = len(nums)

    def f(i, prev):            # best from nums[i:], last taken index prev
        if i == n:
            return 0
        best = f(i + 1, prev)
        if prev == -1 or nums[prev] < nums[i]:
            best = max(best, 1 + f(i + 1, i))
        return best
    return f(0, -1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Cache on <code>(i, prev)</code>. <code>prev &lt; i</code>, so there are about <code>n&sup2;/2</code> states.",
                why=[
                    "Many different subsequences of <code>nums[:i]</code> end at the same <code>prev</code>. From there on they have the same best future, now computed once.",
                ],
                code='''def length_of_lis(nums):
    n = len(nums)

    @cache
    def f(i, prev):
        if i == n:
            return 0
        best = f(i + 1, prev)
        if prev == -1 or nums[prev] < nums[i]:
            best = max(best, 1 + f(i + 1, i))
        return best
    return f(0, -1)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Fill <code>dp[i][prev + 1]</code> with <code>i</code> running from <code>n-1</code> down to 0. The <code>+1</code> shift gives <code>prev = -1</code> a column (column 0).",
                why=[
                    "Row <code>i</code> reads only row <code>i+1</code>, so filling <code>i</code> downwards has it ready.",
                    "Row <code>n</code> is all zeros: the base case.",
                ],
                code='''def length_of_lis(nums):
    n = len(nums)
    dp = [[0] * (n + 1) for _ in range(n + 1)]     # dp[i][prev + 1]
    for i in range(n - 1, -1, -1):
        for prev in range(i - 1, -2, -1):
            best = dp[i + 1][prev + 1]
            if prev == -1 or nums[prev] < nums[i]:
                best = max(best, 1 + dp[i + 1][i + 1])
            dp[i][prev + 1] = best
    return dp[0][0]''',
            ),
            dict(
                name="Two rows",
                time="O(n&sup2;)",
                space="O(n)",
                change="Row <code>i</code> reads only row <code>i+1</code>. Keep it as <code>nxt</code> and build <code>cur</code>.",
                why=[
                    "Space falls from <code>n&sup2;</code> to <code>2n</code>.",
                ],
                code='''def length_of_lis(nums):
    n = len(nums)
    nxt = [0] * (n + 1)        # row i+1
    for i in range(n - 1, -1, -1):
        cur = [0] * (n + 1)
        for prev in range(i - 1, -2, -1):
            best = nxt[prev + 1]
            if prev == -1 or nums[prev] < nums[i]:
                best = max(best, 1 + nxt[i + 1])
            cur[prev + 1] = best
        nxt = cur
    return nxt[0]''',
            ),
            dict(
                name="One row",
                time="O(n&sup2;)",
                space="O(n)",
                change="Update one row in place. Cell <code>prev + 1</code> reads itself and cell <code>i + 1</code>; read <code>i + 1</code> once up front.",
                why=[
                    "In pass <code>i</code> only cells <code>0..i</code> are written (because <code>prev &lt; i</code>). Cell <code>i + 1</code> is never written in this pass, so it still holds the row below.",
                    "Each written cell reads only its own old value before overwriting it. So one row serves as both.",
                ],
                code='''def length_of_lis(nums):
    n = len(nums)
    row = [0] * (n + 1)        # row[prev + 1] = f(i + 1, prev)
    for i in range(n - 1, -1, -1):
        take = 1 + row[i + 1]  # f(i+1, i): not written in this pass
        for prev in range(i - 1, -2, -1):
            if prev == -1 or nums[prev] < nums[i]:
                row[prev + 1] = max(row[prev + 1], take)
    return row[0]''',
            ),
            dict(
                name="dp[i] = longest ending at i",
                time="O(n&sup2;)",
                space="O(n)",
                tag="another state",
                why=[
                    "A different, very common 1-D state: <code>dp[i]</code> = the longest increasing subsequence that <em>ends at</em> <code>nums[i]</code>.",
                    "It extends the best earlier <code>dp[j]</code> with <code>nums[j] &lt; nums[i]</code>: <code>dp[i] = 1 + max(dp[j])</code>.",
                    "The answer is <code>max(dp)</code>, not <code>dp[-1]</code>: the longest subsequence need not end at the last element.",
                    "Same cost as the one-row version. It is the form most people write, and it is how Russian Doll and Pair Chain are usually explained.",
                ],
                code='''def length_of_lis(nums):
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
    return max(dp)''',
            ),
            dict(
                name="Patience sorting with bisect",
                time="O(n log n)",
                space="O(n)",
                best=True,
                tag="beyond DP",
                why=[
                    "<code>tails[k]</code> is the smallest last element of any increasing subsequence of length <code>k+1</code> seen so far. It is strictly increasing, so <code>bisect_left</code> finds where each number belongs.",
                    "Past the end means it extends the longest subsequence: append. Otherwise it becomes a smaller, better tail for that length: overwrite. A smaller tail never hurts, because it is easier to extend.",
                    "<code>bisect_left</code>, not <code>bisect_right</code>: an equal value must replace the tail, not extend past it, because the problem wants <em>strictly</em> increasing.",
                    "<code>tails</code> is not itself a valid subsequence &mdash; only its length is meaningful.",
                ],
                code='''def length_of_lis(nums):
    tails = []
    for x in nums:
        k = bisect.bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)''',
            ),
        ],
        tests='''assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4
assert length_of_lis([0, 1, 0, 3, 2, 3]) == 4
assert length_of_lis([7, 7, 7, 7, 7, 7, 7]) == 1
assert length_of_lis([5]) == 1
assert length_of_lis([4, 10, 4, 3, 8, 9]) == 3


def brute(nums):
    return max(r for r in range(1, len(nums) + 1)
               for c in itertools.combinations(nums, r)
               if all(a < b for a, b in zip(c, c[1:])))


random.seed(18)
for _ in range(60):
    data = [random.randint(0, 12) for _ in range(random.randint(1, 11))]
    assert length_of_lis(data) == brute(data), data''',
    ),

    dict(
        id="russian-doll-envelopes",
        lc=354, slug="russian-doll-envelopes",
        name="Russian Doll Envelopes",
        difficulty="hard",
        recurrence=dict(
            state="After sorting by width ascending and, for equal widths, height <strong>descending</strong>: <code>f(i, prev)</code> = the most envelopes you can still nest from position <code>i</code> on, given the last one taken was <code>prev</code>.",
            derive=[
                "Sort by width. Now a nesting chain is a subsequence of the sorted list whose heights strictly increase: this is LIS on the heights.",
                "The trap is equal widths. Two envelopes of width 5 cannot nest, but if their heights increase, LIS would chain them. Sorting equal widths by height <em>descending</em> makes heights decrease inside a width group, so no increasing subsequence can take two of them.",
                "After that sort, only heights need comparing. Skip envelope <code>i</code>, or take it if its height beats <code>prev</code>'s.",
            ],
            formula='''sort by (w ascending, h descending);  h[i] = height of envelope i

f(i, prev) = max(f(i+1, prev),              skip envelope i
                 1 + f(i+1, i))              take it, if prev == -1 or h[prev] < h[i]
f(n, prev) = 0
answer: f(0, -1)''',
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(n log n + 2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Sort once, then try every subsequence of the sorted envelopes.",
                ],
                code='''def max_envelopes(envelopes):
    h = [e[1] for e in sorted(envelopes, key=lambda e: (e[0], -e[1]))]
    n = len(h)

    def f(i, prev):
        if i == n:
            return 0
        best = f(i + 1, prev)
        if prev == -1 or h[prev] < h[i]:
            best = max(best, 1 + f(i + 1, i))
        return best
    return f(0, -1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Cache on <code>(i, prev)</code>.",
                why=[
                    "About <code>n&sup2;/2</code> states, O(1) each.",
                ],
                code='''def max_envelopes(envelopes):
    h = [e[1] for e in sorted(envelopes, key=lambda e: (e[0], -e[1]))]
    n = len(h)

    @cache
    def f(i, prev):
        if i == n:
            return 0
        best = f(i + 1, prev)
        if prev == -1 or h[prev] < h[i]:
            best = max(best, 1 + f(i + 1, i))
        return best
    return f(0, -1)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Fill <code>dp[i][prev + 1]</code> for <code>i</code> from <code>n-1</code> down to 0.",
                why=[
                    "Row <code>i</code> reads only row <code>i+1</code>.",
                ],
                code='''def max_envelopes(envelopes):
    h = [e[1] for e in sorted(envelopes, key=lambda e: (e[0], -e[1]))]
    n = len(h)
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for prev in range(i - 1, -2, -1):
            best = dp[i + 1][prev + 1]
            if prev == -1 or h[prev] < h[i]:
                best = max(best, 1 + dp[i + 1][i + 1])
            dp[i][prev + 1] = best
    return dp[0][0]''',
            ),
            dict(
                name="Two rows",
                time="O(n&sup2;)",
                space="O(n)",
                change="Keep only row <code>i+1</code> as <code>nxt</code>.",
                why=[
                    "Space falls from <code>n&sup2;</code> to <code>2n</code>.",
                ],
                code='''def max_envelopes(envelopes):
    h = [e[1] for e in sorted(envelopes, key=lambda e: (e[0], -e[1]))]
    n = len(h)
    nxt = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        cur = [0] * (n + 1)
        for prev in range(i - 1, -2, -1):
            best = nxt[prev + 1]
            if prev == -1 or h[prev] < h[i]:
                best = max(best, 1 + nxt[i + 1])
            cur[prev + 1] = best
        nxt = cur
    return nxt[0]''',
            ),
            dict(
                name="One row",
                time="O(n&sup2;)",
                space="O(n)",
                tag="too slow at 10<sup>5</sup>",
                change="Update one row in place; read cell <code>i + 1</code> before the pass, since the pass only writes cells <code>0..i</code>.",
                why=[
                    "Same argument as LIS: the only cell read that is not the one being written is <code>i + 1</code>, and it is not touched in this pass.",
                    "Correct, but <code>n</code> can be 10<sup>5</sup>, and 10<sup>10</sup> steps will time out. This problem needs the next step.",
                ],
                code='''def max_envelopes(envelopes):
    h = [e[1] for e in sorted(envelopes, key=lambda e: (e[0], -e[1]))]
    n = len(h)
    row = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        take = 1 + row[i + 1]
        for prev in range(i - 1, -2, -1):
            if prev == -1 or h[prev] < h[i]:
                row[prev + 1] = max(row[prev + 1], take)
    return row[0]''',
            ),
            dict(
                name="Patience sorting on heights",
                time="O(n log n)",
                space="O(n)",
                best=True,
                tag="beyond DP",
                why=[
                    "After the sort this <em>is</em> LIS on the heights, so use the O(n log n) <code>tails</code> method.",
                    "The descending tie-break matters here too: equal widths arrive tallest first, so a shorter one can only replace a tail, never extend it.",
                ],
                code='''def max_envelopes(envelopes):
    envelopes = sorted(envelopes, key=lambda e: (e[0], -e[1]))
    tails = []
    for _, h in envelopes:
        k = bisect.bisect_left(tails, h)
        if k == len(tails):
            tails.append(h)
        else:
            tails[k] = h
    return len(tails)''',
            ),
        ],
        tests='''assert max_envelopes([[5, 4], [6, 4], [6, 7], [2, 3]]) == 3
assert max_envelopes([[1, 1], [1, 1], [1, 1]]) == 1
assert max_envelopes([[4, 5], [4, 6], [6, 7], [2, 3], [1, 1]]) == 4
assert max_envelopes([[2, 100], [3, 200], [4, 300], [5, 500], [5, 400], [5, 250], [6, 370], [6, 360], [7, 380]]) == 5


def brute(env):
    best = 1
    for r in range(2, len(env) + 1):
        for c in itertools.permutations(env, r):
            if all(a[0] < b[0] and a[1] < b[1] for a, b in zip(c, c[1:])):
                best = max(best, r)
    return best


random.seed(19)
for _ in range(50):
    env = [[random.randint(1, 5), random.randint(1, 5)] for _ in range(random.randint(1, 6))]
    assert max_envelopes(env) == brute(env), env''',
        pitfall="Sorting heights ascending within the same width, which lets two same-width envelopes nest.",
    ),

    dict(
        id="maximum-length-of-pair-chain",
        lc=646, slug="maximum-length-of-pair-chain",
        name="Maximum Length of Pair Chain",
        difficulty="medium",
        recurrence=dict(
            state="After sorting pairs by start: <code>f(i, prev)</code> = the longest chain you can still build from pair <code>i</code> on, given the last pair taken was <code>prev</code>.",
            derive=[
                "In a chain <code>a &rarr; b</code> we need <code>a[1] &lt; b[0]</code>, and <code>a[0] &lt; a[1]</code>, so <code>a[0] &lt; b[0]</code>. So every chain appears in start order: sorted by start, a chain is a subsequence.",
                "Now it is LIS with a different \"may I take it?\" test: pair <code>i</code> can follow <code>prev</code> if <code>pairs[prev][1] &lt; pairs[i][0]</code>.",
            ],
            formula='''sort pairs by start

f(i, prev) = max(f(i+1, prev),              skip pair i
                 1 + f(i+1, i))              take it, if prev == -1 or pairs[prev][1] < pairs[i][0]
f(n, prev) = 0
answer: f(0, -1)''',
            notes=[
                "The DP is the pattern this section teaches. For this particular problem a greedy choice turns out to be enough, which is the last step.",
            ],
        ),
        approaches=[
            dict(
                name="Plain recursion",
                time="O(n log n + 2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Sort, then try every subsequence of pairs.",
                ],
                code='''def find_longest_chain(pairs):
    pairs = sorted(pairs)
    n = len(pairs)

    def f(i, prev):
        if i == n:
            return 0
        best = f(i + 1, prev)
        if prev == -1 or pairs[prev][1] < pairs[i][0]:
            best = max(best, 1 + f(i + 1, i))
        return best
    return f(0, -1)''',
            ),
            dict(
                name="Top-down memo",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Cache on <code>(i, prev)</code>.",
                why=[
                    "About <code>n&sup2;/2</code> states, O(1) each.",
                ],
                code='''def find_longest_chain(pairs):
    pairs = sorted(pairs)
    n = len(pairs)

    @cache
    def f(i, prev):
        if i == n:
            return 0
        best = f(i + 1, prev)
        if prev == -1 or pairs[prev][1] < pairs[i][0]:
            best = max(best, 1 + f(i + 1, i))
        return best
    return f(0, -1)''',
            ),
            dict(
                name="Bottom-up 2-D table",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                change="Fill <code>dp[i][prev + 1]</code> for <code>i</code> from <code>n-1</code> down to 0.",
                why=[
                    "Row <code>i</code> reads only row <code>i+1</code>.",
                ],
                code='''def find_longest_chain(pairs):
    pairs = sorted(pairs)
    n = len(pairs)
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for prev in range(i - 1, -2, -1):
            best = dp[i + 1][prev + 1]
            if prev == -1 or pairs[prev][1] < pairs[i][0]:
                best = max(best, 1 + dp[i + 1][i + 1])
            dp[i][prev + 1] = best
    return dp[0][0]''',
            ),
            dict(
                name="Two rows",
                time="O(n&sup2;)",
                space="O(n)",
                change="Keep only row <code>i+1</code> as <code>nxt</code>.",
                why=[
                    "Space falls from <code>n&sup2;</code> to <code>2n</code>.",
                ],
                code='''def find_longest_chain(pairs):
    pairs = sorted(pairs)
    n = len(pairs)
    nxt = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        cur = [0] * (n + 1)
        for prev in range(i - 1, -2, -1):
            best = nxt[prev + 1]
            if prev == -1 or pairs[prev][1] < pairs[i][0]:
                best = max(best, 1 + nxt[i + 1])
            cur[prev + 1] = best
        nxt = cur
    return nxt[0]''',
            ),
            dict(
                name="One row",
                time="O(n&sup2;)",
                space="O(n)",
                change="Update one row in place, reading cell <code>i + 1</code> before the pass.",
                why=[
                    "Pass <code>i</code> writes only cells <code>0..i</code>, so cell <code>i + 1</code> still belongs to the row below.",
                ],
                code='''def find_longest_chain(pairs):
    pairs = sorted(pairs)
    n = len(pairs)
    row = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        take = 1 + row[i + 1]
        for prev in range(i - 1, -2, -1):
            if prev == -1 or pairs[prev][1] < pairs[i][0]:
                row[prev + 1] = max(row[prev + 1], take)
    return row[0]''',
            ),
            dict(
                name="Greedy by earliest end",
                time="O(n log n)",
                space="O(1)",
                best=True,
                tag="beyond DP",
                why=[
                    "Sort by <em>end</em> and take every pair whose start is past the last end taken. This is activity selection.",
                    "Finishing as early as possible leaves the most room for everything after. Any optimal chain can be rewritten to start with the earliest-ending pair without getting shorter, so the greedy choice is always safe.",
                    "When the DP's best choice is always \"the one that ends first\", the table is unnecessary. Some DP-shaped problems have a greedy answer; this is one.",
                ],
                code='''def find_longest_chain(pairs):
    count, end = 0, -inf
    for a, b in sorted(pairs, key=lambda p: p[1]):
        if a > end:
            count += 1
            end = b
    return count''',
            ),
        ],
        tests='''assert find_longest_chain([[1, 2], [2, 3], [3, 4]]) == 2
assert find_longest_chain([[1, 2], [7, 8], [4, 5]]) == 3
assert find_longest_chain([[1, 5]]) == 1
assert find_longest_chain([[-10, -8], [8, 9], [-5, 0], [6, 10], [-6, -4], [1, 7], [9, 10], [-4, 7]]) == 4


def brute(pairs):
    best = 1
    for r in range(2, len(pairs) + 1):
        for c in itertools.permutations(pairs, r):
            if all(a[1] < b[0] for a, b in zip(c, c[1:])):
                best = max(best, r)
    return best


random.seed(20)
for _ in range(50):
    pairs = []
    for _ in range(random.randint(1, 6)):
        a = random.randint(-5, 5)
        pairs.append([a, a + random.randint(1, 4)])
    assert find_longest_chain(pairs) == brute(pairs), pairs''',
    ),
    ],
)

SECTIONS = [LIS]
