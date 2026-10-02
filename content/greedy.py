# -*- coding: utf-8 -*-
"""Greedy topic (NeetCode 250: Greedy). Maximum Subarray, also in the NeetCode
Greedy list, already lives in the Dynamic Programming topic. Same build
contract as content/dsa.py."""

PRELUDE_GREEDY = '''import heapq
import itertools
import random
from collections import Counter, deque
from functools import cache
'''


GREEDY_TOPIC = dict(
    id="greedy",
    title="Greedy",
    prelude=PRELUDE_GREEDY,
    sections=[

dict(
    id="greedy",
    title="Locally best, provably globally best",
    idea=[
        "A greedy algorithm commits to the best-looking choice at each step and never revisits it. It is only correct when you can argue that some optimal answer agrees with that choice &mdash; usually an <strong>exchange argument</strong> (\"swapping any optimal solution's choice for mine does not make it worse\"). Most problems here start as a DP or brute force whose state collapses to one or two variables once that argument is made. Maximum Subarray, also in this NeetCode list, is covered under Dynamic Programming.",
    ],
    problems=[

    # ------------------------------------------------------------------ 860
    dict(
        id="lemonade-change",
        lc=860, slug="lemonade-change",
        name="Lemonade Change",
        difficulty="easy",
        framing=[
            "Lemonade costs $5; customers pay with $5, $10 or $20 bills, in order, and you start with no change. Can you give everyone correct change? The only real choice is how to make $15 for a $20: one $10 and one $5, or three $5s.",
        ],
        approaches=[
            dict(
                name="Try both ways of making change (search)",
                time="O(2<sup>n</sup>) worst",
                space="O(n)",
                tag="brute force",
                why=[
                    "Whenever a $20 can be broken both ways, try both and see whether either leads to serving everyone. Correct without any insight, and exponential. It is the search the greedy argument below makes unnecessary.",
                ],
                code='''def lemonade_change(bills):
    @cache
    def ok(i, fives, tens):
        if i == len(bills):
            return True
        b = bills[i]
        if b == 5:
            return ok(i + 1, fives + 1, tens)
        if b == 10:
            return fives > 0 and ok(i + 1, fives - 1, tens + 1)
        return ((tens > 0 and fives > 0 and ok(i + 1, fives - 1, tens - 1))
                or (fives >= 3 and ok(i + 1, fives - 3, tens)))
    return ok(0, 0, 0)''',
            ),
            dict(
                name="Count bills, prefer giving a $10",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "$5 bills are strictly more useful than $10s: they can make change for both $10 and $20 payments, while a $10 only helps with $20s. So when a $20 arrives, spend a $10 if you have one and keep the $5s. Any sequence that succeeds by paying three $5s would also succeed paying $10 + $5 instead, since you end up with at least as many $5s.",
                    "Two counters; $20 bills are never given as change, so they need no counter.",
                ],
                code='''def lemonade_change(bills):
    fives = tens = 0
    for b in bills:
        if b == 5:
            fives += 1
        elif b == 10:
            if not fives:
                return False
            fives, tens = fives - 1, tens + 1
        elif tens and fives:                     # $20: keep the more useful $5s
            fives, tens = fives - 1, tens - 1
        elif fives >= 3:
            fives -= 3
        else:
            return False
    return True''',
            ),
        ],
        tests='''assert lemonade_change([5, 5, 5, 10, 20]) is True
assert lemonade_change([5, 5, 10, 10, 20]) is False
assert lemonade_change([10]) is False
rng = random.Random(0)
for _ in range(80):
    bills = [rng.choice([5, 5, 10, 20]) for _ in range(rng.randint(1, 10))]
    def search(i, f, t):
        if i == len(bills): return True
        b = bills[i]
        if b == 5: return search(i + 1, f + 1, t)
        if b == 10: return f > 0 and search(i + 1, f - 1, t + 1)
        return (t > 0 and f > 0 and search(i + 1, f - 1, t - 1)) or (f >= 3 and search(i + 1, f - 3, t))
    assert lemonade_change(bills) is search(0, 0, 0)''',
    ),

    # ------------------------------------------------------------------ 918
    dict(
        id="max-circular-subarray",
        lc=918, slug="maximum-sum-circular-subarray",
        name="Maximum Sum Circular Subarray",
        difficulty="medium",
        framing=[
            "Maximum subarray sum where the array wraps around. A wrapping subarray is everything <em>except</em> a contiguous middle piece, so its best value is <code>total - (minimum subarray sum)</code>. The answer is the better of the ordinary Kadane maximum and that wrapped value &mdash; with one trap.",
        ],
        pitfall="When every element is negative, the minimum subarray is the whole array and <code>total - min</code> is 0, which corresponds to an <em>empty</em> subarray. Return the plain maximum in that case.",
        approaches=[
            dict(
                name="Every start, every length",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=["For each start, extend around the circle up to n elements, tracking the running sum."],
                code='''def max_subarray_sum_circular(nums):
    n, best = len(nums), float("-inf")
    for i in range(n):
        total = 0
        for k in range(n):
            total += nums[(i + k) % n]
            best = max(best, total)
    return best''',
            ),
            dict(
                name="Best prefix plus best suffix",
                time="O(n)",
                space="O(n)",
                why=[
                    "A wrapping subarray is a suffix followed by a prefix that do not overlap. Precompute, for each i, the best prefix sum ending at or before i. Then for every suffix starting at j, pair it with the best prefix ending before j. Combine with ordinary Kadane for the non-wrapping case.",
                ],
                code='''def max_subarray_sum_circular(nums):
    n = len(nums)
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    right_max = [0] * n                          # best prefix sum within nums[:i+1]
    prefix = right_max[0] = nums[0]
    for i in range(1, n):
        prefix += nums[i]
        right_max[i] = max(right_max[i - 1], prefix)
    suffix = 0
    for j in range(n - 1, 0, -1):
        suffix += nums[j]
        best = max(best, suffix + right_max[j - 1])
    return best''',
            ),
            dict(
                name="Kadane for max and min together",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "One pass runs Kadane twice at once: the maximum subarray (non-wrapping answer) and the minimum subarray. The wrapping answer is <code>total - min</code>. If the maximum is negative, every element is negative and the wrap would be empty, so return the maximum.",
                ],
                code='''def max_subarray_sum_circular(nums):
    total = 0
    cur_max = cur_min = 0
    best, worst = float("-inf"), float("inf")
    for x in nums:
        total += x
        cur_max = max(x, cur_max + x)
        cur_min = min(x, cur_min + x)
        best = max(best, cur_max)
        worst = min(worst, cur_min)
    return best if best < 0 else max(best, total - worst)''',
            ),
        ],
        tests='''assert max_subarray_sum_circular([1, -2, 3, -2]) == 3
assert max_subarray_sum_circular([5, -3, 5]) == 10
assert max_subarray_sum_circular([-3, -2, -3]) == -2
rng = random.Random(1)
for _ in range(80):
    nums = [rng.randint(-6, 6) for _ in range(rng.randint(1, 10))]
    n = len(nums)
    brute = max(sum(nums[(i + k) % n] for k in range(L)) for i in range(n) for L in range(1, n + 1))
    assert max_subarray_sum_circular(nums) == brute''',
    ),

    # ------------------------------------------------------------------ 978
    dict(
        id="longest-turbulent-subarray",
        lc=978, slug="longest-turbulent-subarray",
        name="Longest Turbulent Subarray",
        difficulty="medium",
        framing=[
            "A subarray is turbulent when the comparison sign flips between every adjacent pair: <code>a &lt; b &gt; c &lt; d</code> or the reverse. Find the longest. Equal neighbours break any turbulent run.",
        ],
        approaches=[
            dict(
                name="Extend from every start",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=["From each start, extend while the signs keep alternating."],
                code='''def max_turbulence_size(arr):
    best = 1
    for i in range(len(arr)):
        j = i + 1
        while j < len(arr) and arr[j] != arr[j - 1] and (j == i + 1 or (arr[j] > arr[j - 1]) != (arr[j - 1] > arr[j - 2])):
            j += 1
        best = max(best, j - i)
    return best''',
            ),
            dict(
                name="DP: longest run ending here going up or down",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "<code>up</code> is the longest turbulent run ending at i whose last step went up; <code>down</code> the same ending with a down step. A rise extends the previous <code>down</code> run by one; a fall extends the previous <code>up</code>; equality resets both to 1.",
                    "Two variables, one pass. The same up/down state machine solves Wiggle Subsequence.",
                ],
                code='''def max_turbulence_size(arr):
    up = down = best = 1
    for a, b in zip(arr, arr[1:]):
        if b > a:
            up, down = down + 1, 1
        elif b < a:
            up, down = 1, up + 1
        else:
            up = down = 1
        best = max(best, up, down)
    return best''',
            ),
        ],
        tests='''assert max_turbulence_size([9, 4, 2, 10, 7, 8, 8, 1, 9]) == 5
assert max_turbulence_size([4, 8, 12, 16]) == 2
assert max_turbulence_size([100]) == 1
assert max_turbulence_size([9, 9]) == 1
rng = random.Random(2)
for _ in range(80):
    arr = [rng.randint(0, 4) for _ in range(rng.randint(1, 12))]
    def turb(s):
        if len(s) == 1: return True
        c = [(y > x) - (y < x) for x, y in zip(s, s[1:])]
        return all(v != 0 for v in c) and all(p != q for p, q in zip(c, c[1:]))
    brute = max(j - i for i in range(len(arr)) for j in range(i + 1, len(arr) + 1) if turb(arr[i:j]))
    assert max_turbulence_size(arr) == brute''',
    ),

    # ------------------------------------------------------------------ 55
    dict(
        id="jump-game",
        lc=55, slug="jump-game",
        name="Jump Game",
        difficulty="medium",
        framing=[
            "From index i you may jump up to <code>nums[i]</code> steps. Can you reach the last index? The natural DP asks, per index, \"can I get from here to the end?\"; the greedy observation is that you only ever need the farthest index reachable so far.",
        ],
        approaches=[
            dict(
                name="Try every jump recursively",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=["From each index try every jump length. Exponential on inputs like <code>[n, n-1, ..., 1, 0, 1]</code>."],
                code='''def can_jump(nums):
    def go(i):
        if i >= len(nums) - 1:
            return True
        return any(go(i + k) for k in range(nums[i], 0, -1))
    return go(0)''',
            ),
            dict(
                name="DP: which indices can reach the end",
                time="O(n&sup2;)",
                space="O(n)",
                why=[
                    "Fill <code>good[i]</code> from the right: index i is good if some jump from it lands on a good index. The last index is good. Each index checks up to <code>nums[i]</code> targets.",
                ],
                code='''def can_jump(nums):
    n = len(nums)
    good = [False] * n
    good[-1] = True
    for i in range(n - 2, -1, -1):
        good[i] = any(good[j] for j in range(i + 1, min(n, i + nums[i] + 1)))
    return good[0]''',
            ),
            dict(
                name="Greedy: pull the goal backwards",
                time="O(n)",
                space="O(1)",
                why=[
                    "In the DP, only the <em>leftmost</em> good index matters: an index is good exactly when it can reach that one. So keep a single <code>goal</code>, and move it to i whenever <code>i + nums[i] &ge; goal</code>. The answer is whether the goal reaches 0.",
                ],
                code='''def can_jump(nums):
    goal = len(nums) - 1
    for i in range(len(nums) - 2, -1, -1):
        if i + nums[i] >= goal:
            goal = i
    return goal == 0''',
            ),
            dict(
                name="Greedy: track the farthest reachable index",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Walk forward keeping <code>reach</code>, the farthest index reachable so far. Every index up to <code>reach</code> is reachable (jumps can be shorter than the maximum). If the walk arrives at an index beyond <code>reach</code>, it is stuck.",
                ],
                code='''def can_jump(nums):
    reach = 0
    for i, jump in enumerate(nums):
        if i > reach:
            return False                         # a gap nobody can cross
        reach = max(reach, i + jump)
    return True''',
            ),
        ],
        tests='''assert can_jump([2, 3, 1, 1, 4]) is True
assert can_jump([3, 2, 1, 0, 4]) is False
assert can_jump([0]) is True
rng = random.Random(3)
for _ in range(80):
    nums = [rng.randint(0, 3) for _ in range(rng.randint(1, 12))]
    reach = {0}
    for i in range(len(nums)):
        if i in reach:
            reach |= set(range(i, i + nums[i] + 1))
    assert can_jump(nums) is (len(nums) - 1 in reach)''',
    ),

    # ------------------------------------------------------------------ 45
    dict(
        id="jump-game-ii",
        lc=45, slug="jump-game-ii",
        name="Jump Game II",
        difficulty="medium",
        framing=[
            "Now the end is guaranteed reachable; minimise the number of jumps. It is a shortest-path problem on an implicit graph, and BFS by levels solves it &mdash; where each \"level\" is simply a range of indices, so no queue is needed.",
        ],
        approaches=[
            dict(
                name="DP: fewest jumps to each index",
                time="O(n&sup2;)",
                space="O(n)",
                why=[
                    "<code>jumps[j]</code> = fewest jumps to reach j. For each i, relax every index it can reach. Correct, quadratic in the worst case.",
                ],
                code='''def jump(nums):
    n = len(nums)
    jumps = [0] + [float("inf")] * (n - 1)
    for i in range(n):
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            jumps[j] = min(jumps[j], jumps[i] + 1)
    return jumps[-1]''',
            ),
            dict(
                name="Greedy BFS over index ranges",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "All indices reachable with k jumps form a contiguous range <code>[start, end]</code>. The next range runs from <code>end + 1</code> to the farthest point any index in the current range can reach. Count ranges until one contains the last index.",
                    "This is BFS where each level is an interval, so the \"queue\" is two integers.",
                ],
                code='''def jump(nums):
    jumps, end, farthest = 0, 0, 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == end:                             # this level is exhausted
            jumps += 1
            end = farthest
    return jumps''',
            ),
        ],
        tests='''assert jump([2, 3, 1, 1, 4]) == 2
assert jump([2, 3, 0, 1, 4]) == 2
assert jump([0]) == 0
rng = random.Random(4)
for _ in range(80):
    nums = [rng.randint(1, 4) for _ in range(rng.randint(1, 12))]
    n = len(nums)
    d = [0] + [float("inf")] * (n - 1)
    for i in range(n):
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            d[j] = min(d[j], d[i] + 1)
    assert jump(nums) == d[-1]''',
    ),

    # ------------------------------------------------------------------ 1871
    dict(
        id="jump-game-vii",
        lc=1871, slug="jump-game-vii",
        name="Jump Game VII",
        difficulty="medium",
        framing=[
            "A binary string; you may jump from i to any j with <code>i + minJump &le; j &le; i + maxJump</code> if <code>s[j] == '0'</code>. Can you reach the end? The naive BFS rescans overlapping ranges; both fixes make sure each index is looked at a constant number of times.",
        ],
        approaches=[
            dict(
                name="BFS, scanning each full range",
                time="O(n &middot; (maxJump - minJump))",
                space="O(n)",
                tag="brute force",
                why=["BFS from 0; from each reachable index, scan its whole jump range. Ranges overlap heavily, so the same indices are scanned again and again."],
                code='''def can_reach(s, min_jump, max_jump):
    n = len(s)
    seen, queue = {0}, deque([0])
    while queue:
        i = queue.popleft()
        for j in range(i + min_jump, min(n - 1, i + max_jump) + 1):
            if s[j] == "0" and j not in seen:
                seen.add(j)
                queue.append(j)
    return n - 1 in seen''',
            ),
            dict(
                name="BFS that never rescans (farthest pointer)",
                time="O(n)",
                space="O(n)",
                why=[
                    "BFS pops indices in increasing order, so their ranges start in increasing order. Keep <code>farthest</code>, the end of everything already scanned, and start each new scan from <code>max(i + minJump, farthest + 1)</code>. Every index is scanned at most once.",
                ],
                code='''def can_reach(s, min_jump, max_jump):
    n = len(s)
    queue, farthest = deque([0]), 0
    while queue:
        i = queue.popleft()
        for j in range(max(i + min_jump, farthest + 1), min(n - 1, i + max_jump) + 1):
            if s[j] == "0":
                if j == n - 1:
                    return True
                queue.append(j)
        farthest = max(farthest, i + max_jump)
    return n == 1''',
            ),
            dict(
                name="DP with a sliding count of reachable sources",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "<code>ok[j]</code> is true if <code>s[j] == '0'</code> and some reachable i lies in <code>[j - maxJump, j - minJump]</code>. Maintain the number of reachable indices in that window as it slides: add <code>ok[j - minJump]</code> as it enters, subtract <code>ok[j - maxJump - 1]</code> as it leaves.",
                    "A clean DP with O(1) work per index &mdash; the sliding-window-over-DP pattern that also appears in harder problems.",
                ],
                code='''def can_reach(s, min_jump, max_jump):
    n = len(s)
    ok = [False] * n
    ok[0] = True
    window = 0                                   # reachable indices in [j-max, j-min]
    for j in range(1, n):
        if j >= min_jump:
            window += ok[j - min_jump]
        if j > max_jump:
            window -= ok[j - max_jump - 1]
        ok[j] = s[j] == "0" and window > 0
    return ok[-1]''',
            ),
        ],
        tests='''assert can_reach("011010", 2, 3) is True
assert can_reach("01101110", 2, 3) is False
assert can_reach("0", 1, 1) is True
rng = random.Random(5)
for _ in range(80):
    s = "0" + "".join(rng.choice("0001") for _ in range(rng.randint(0, 12)))
    lo = rng.randint(1, 3); hi = rng.randint(lo, 5)
    reach = {0}
    for i in range(len(s)):
        if i in reach:
            reach |= {j for j in range(i + lo, min(len(s) - 1, i + hi) + 1) if s[j] == "0"}
    assert can_reach(s, lo, hi) is (len(s) - 1 in reach)''',
    ),

    # ------------------------------------------------------------------ 134
    dict(
        id="gas-station",
        lc=134, slug="gas-station",
        name="Gas Station",
        difficulty="medium",
        framing=[
            "Stations in a circle; at station i you gain <code>gas[i]</code> and spend <code>cost[i]</code> to drive to the next. Find the unique starting station from which you can complete the loop, or -1. Two facts give an O(n) answer: a solution exists iff total gas &ge; total cost, and a failed start rules out every station it passed.",
        ],
        approaches=[
            dict(
                name="Simulate from every start",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=["Try each start and drive around, failing as soon as the tank goes negative."],
                code='''def can_complete_circuit(gas, cost):
    n = len(gas)
    for start in range(n):
        tank = 0
        for k in range(n):
            i = (start + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                break
        else:
            return start
    return -1''',
            ),
            dict(
                name="One pass: restart after every failure",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Drive from a candidate start. If the tank goes negative on the way to station i + 1, no station between the start and i can work either: each of them would arrive at i with no more fuel than the start did (the start arrived at them with a non-negative tank). So the next candidate is i + 1.",
                    "If the total gas covers the total cost, the last candidate standing is the answer; otherwise nothing works.",
                ],
                code='''def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0               # everything up to i is ruled out
    return start''',
            ),
        ],
        tests='''assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1
assert can_complete_circuit([5], [4]) == 0
rng = random.Random(6)
for _ in range(80):
    n = rng.randint(1, 8)
    gas = [rng.randint(0, 5) for _ in range(n)]; cost = [rng.randint(0, 5) for _ in range(n)]
    ok = []
    for s in range(n):
        t = 0
        for k in range(n):
            t += gas[(s + k) % n] - cost[(s + k) % n]
            if t < 0: break
        else:
            ok.append(s)
    got = can_complete_circuit(gas, cost)
    assert (got == -1 and not ok) or got in ok''',
    ),

    # ------------------------------------------------------------------ 846
    dict(
        id="hand-of-straights",
        lc=846, slug="hand-of-straights",
        name="Hand of Straights",
        difficulty="medium",
        framing=[
            "Can the cards be split into groups of <code>groupSize</code> consecutive values? The smallest card left must <em>start</em> a group (nothing smaller exists to precede it), so repeatedly building a group from the smallest remaining card is forced, not just greedy.",
        ],
        approaches=[
            dict(
                name="Sort, then build groups from the smallest card",
                time="O(n log n + n &middot; k)",
                space="O(n)",
                why=[
                    "Count the cards. Walk the distinct values in sorted order; while the current value still has copies, it starts a group, so take one of each of the next k values (failing if any is missing).",
                ],
                code='''def is_n_straight_hand(hand, k):
    if len(hand) % k:
        return False
    count = Counter(hand)
    for v in sorted(count):
        while count[v] > 0:
            for x in range(v, v + k):
                if count[x] == 0:
                    return False
                count[x] -= 1
    return True''',
            ),
            dict(
                name="Start whole batches of groups at once",
                time="O(n log n)",
                space="O(n)",
                best=True,
                why=[
                    "If the smallest value v has c copies, exactly c groups must start at v, so subtract c from each of v..v+k-1 in one go. Each distinct value is touched k times at most, and values that reach zero are skipped &mdash; no inner loop per card.",
                ],
                code='''def is_n_straight_hand(hand, k):
    if len(hand) % k:
        return False
    count = Counter(hand)
    for v in sorted(count):
        c = count[v]
        if c == 0:
            continue
        for x in range(v, v + k):
            if count[x] < c:
                return False
            count[x] -= c                       # c groups all start at v
    return True''',
            ),
        ],
        tests='''assert is_n_straight_hand([1, 2, 3, 6, 2, 3, 4, 7, 8], 3) is True
assert is_n_straight_hand([1, 2, 3, 4, 5], 4) is False
assert is_n_straight_hand([1], 1) is True
rng = random.Random(7)
for _ in range(60):
    k = rng.randint(1, 3)
    hand = [rng.randint(0, 6) for _ in range(rng.randint(1, 9))]
    def brute(cards):
        if not cards: return True
        v = min(cards)
        c = Counter(cards)
        for x in range(v, v + k):
            if c[x] == 0: return False
            c[x] -= 1
        return brute(list(c.elements()))
    assert is_n_straight_hand(hand, k) is (len(hand) % k == 0 and brute(hand))''',
    ),

    # ------------------------------------------------------------------ 649
    dict(
        id="dota2-senate",
        lc=649, slug="dota2-senate",
        name="Dota2 Senate",
        difficulty="medium",
        framing=[
            "Senators from two parties (R and D) act in rounds, in order; each can ban one opposing senator. The best move is always to ban the <strong>next</strong> opponent due to act &mdash; the one who would otherwise ban one of yours soonest. Simulating that greedy efficiently is the problem.",
        ],
        approaches=[
            dict(
                name="Simulate with a list and deletions",
                time="O(n&sup2;)",
                space="O(n)",
                why=[
                    "Loop through the senators; each surviving one deletes the next opponent (searching forward, wrapping around). Deleting from a list is O(n), and there are n bans.",
                ],
                code='''def predict_party_victory(senate):
    s = list(senate)
    i = 0
    while len(set(s)) > 1:
        me = s[i]
        j = i + 1
        while s[j % len(s)] == me:
            j += 1
        j %= len(s)
        del s[j]
        if j < i:
            i -= 1                               # removal shifted our position
        i = (i + 1) % len(s)
    return "Radiant" if s[0] == "R" else "Dire"''',
            ),
            dict(
                name="Two queues of turn indices",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Keep each party's senators as a queue of their turn indices. Compare the two fronts: the earlier one acts, bans the other front (pop it for good), and rejoins its queue with index + n &mdash; its turn in the next round. When one queue empties, the other party wins.",
                    "Each ban costs O(1) and there are fewer than n bans.",
                ],
                code='''def predict_party_victory(senate):
    n = len(senate)
    r = deque(i for i, c in enumerate(senate) if c == "R")
    d = deque(i for i, c in enumerate(senate) if c == "D")
    while r and d:
        a, b = r.popleft(), d.popleft()
        if a < b:
            r.append(a + n)                      # R acts first and bans this D
        else:
            d.append(b + n)
    return "Radiant" if r else "Dire"''',
            ),
        ],
        tests='''assert predict_party_victory("RD") == "Radiant"
assert predict_party_victory("RDD") == "Dire"
assert predict_party_victory("DDRRR") == "Dire"
rng = random.Random(8)
for _ in range(60):
    s = "".join(rng.choice("RD") for _ in range(rng.randint(1, 10)))
    ts = list(s); i = 0
    while len(set(ts)) > 1:
        j = i + 1
        while ts[j % len(ts)] == ts[i]: j += 1
        j %= len(ts); del ts[j]
        if j < i: i -= 1
        i = (i + 1) % len(ts)
    assert predict_party_victory(s) == ("Radiant" if ts[0] == "R" else "Dire")''',
    ),

    # ------------------------------------------------------------------ 1899
    dict(
        id="merge-triplets",
        lc=1899, slug="merge-triplets-to-form-target-triplet",
        name="Merge Triplets to Form Target Triplet",
        difficulty="medium",
        framing=[
            "Merging two triplets takes the element-wise maximum. Can some sequence of merges produce <code>target</code> exactly? Merging can only raise values, so any triplet with a component <em>above</em> the target can never be used; every other triplet is harmless to merge.",
        ],
        approaches=[
            dict(
                name="Try every subset",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=["Merge every subset of triplets and see whether any gives the target. Exponential; it is what the greedy argument replaces."],
                code='''def merge_triplets(triplets, target):
    for r in range(1, len(triplets) + 1):
        for combo in itertools.combinations(triplets, r):
            if [max(t[i] for t in combo) for i in range(3)] == list(target):
                return True
    return False''',
            ),
            dict(
                name="Keep the safe triplets, check each coordinate is hit",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "A triplet is safe if none of its values exceeds the target's. Merging <em>all</em> safe triplets gives the largest reachable result that stays at or below the target in every coordinate. So the target is reachable exactly when, for each of the three positions, some safe triplet matches the target there.",
                ],
                code='''def merge_triplets(triplets, target):
    hit = set()
    for t in triplets:
        if all(t[i] <= target[i] for i in range(3)):
            hit |= {i for i in range(3) if t[i] == target[i]}
    return len(hit) == 3''',
            ),
        ],
        tests='''assert merge_triplets([[2, 5, 3], [1, 8, 4], [1, 7, 5]], [2, 7, 5]) is True
assert merge_triplets([[3, 4, 5], [4, 5, 6]], [3, 2, 5]) is False
assert merge_triplets([[2, 5, 3], [2, 3, 4], [1, 2, 5], [5, 2, 3]], [5, 5, 5]) is True
rng = random.Random(9)
for _ in range(80):
    ts = [[rng.randint(1, 4) for _ in range(3)] for _ in range(rng.randint(1, 6))]
    tgt = [rng.randint(1, 4) for _ in range(3)]
    brute = any([max(t[i] for t in c) for i in range(3)] == tgt
                for r in range(1, len(ts) + 1) for c in itertools.combinations(ts, r))
    assert merge_triplets(ts, tgt) is brute''',
    ),

    # ------------------------------------------------------------------ 763
    dict(
        id="partition-labels",
        lc=763, slug="partition-labels",
        name="Partition Labels",
        difficulty="medium",
        framing=[
            "Split the string into as many parts as possible so that each letter appears in at most one part; return the part sizes. A part that contains a letter must extend at least to that letter's last occurrence &mdash; so each part ends exactly where the last occurrences of its letters run out.",
        ],
        approaches=[
            dict(
                name="Letter spans as intervals, then merge",
                time="O(n)",
                space="O(&Sigma;)",
                why=[
                    "Each letter covers the interval from its first to its last occurrence. Letters with overlapping intervals must share a part, so merge overlapping intervals (they are already in order of first occurrence); each merged interval is one part.",
                    "It shows the connection to Merge Intervals explicitly.",
                ],
                code='''def partition_labels(s):
    first, last = {}, {}
    for i, ch in enumerate(s):
        first.setdefault(ch, i)
        last[ch] = i
    spans = sorted((first[c], last[c]) for c in first)
    sizes, start, end = [], spans[0][0], spans[0][1]
    for a, b in spans[1:]:
        if a > end:
            sizes.append(end - start + 1)
            start = a
        end = max(end, b)
    sizes.append(end - start + 1)
    return sizes''',
            ),
            dict(
                name="One sweep extending the current part's end",
                time="O(n)",
                space="O(&Sigma;)",
                best=True,
                why=[
                    "Record every letter's last index. Sweep, extending the current part's end to the last index of each letter seen. When the sweep reaches that end, every letter inside the part has no occurrences later: cut here. Each cut is as early as possible, which maximises the number of parts.",
                ],
                code='''def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}
    sizes, start, end = [], 0, 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:                            # nothing inside continues past here
            sizes.append(end - start + 1)
            start = i + 1
    return sizes''',
            ),
        ],
        tests='''assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]
assert partition_labels("eccbbbbdec") == [10]
assert partition_labels("abc") == [1, 1, 1]''',
    ),

    # ------------------------------------------------------------------ 678
    dict(
        id="valid-parenthesis-string",
        lc=678, slug="valid-parenthesis-string",
        name="Valid Parenthesis String",
        difficulty="medium",
        framing=[
            "The string has <code>(</code>, <code>)</code> and <code>*</code>, where each star may be a <code>(</code>, a <code>)</code> or nothing. Is some choice valid? Trying all 3<sup>k</sup> choices works; the greedy tracks only the <em>range</em> of possible open-bracket counts.",
        ],
        approaches=[
            dict(
                name="Try every assignment of the stars",
                time="O(3<sup>k</sup> &middot; n)",
                space="O(n)",
                tag="brute force",
                why=["Recurse through the string, branching three ways at each star and tracking the open count; fail if it goes negative."],
                code='''def check_valid_string(s):
    def go(i, open_):
        if open_ < 0:
            return False
        if i == len(s):
            return open_ == 0
        ch = s[i]
        if ch == "(":
            return go(i + 1, open_ + 1)
        if ch == ")":
            return go(i + 1, open_ - 1)
        return go(i + 1, open_ + 1) or go(i + 1, open_ - 1) or go(i + 1, open_)
    return go(0, 0)''',
            ),
            dict(
                name="DP over (index, open count)",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                why=[
                    "The recursion's state is just <code>(i, open)</code>, at most n &times; n values, so memoising it removes the exponential blow-up.",
                ],
                code='''def check_valid_string(s):
    @cache
    def go(i, open_):
        if open_ < 0:
            return False
        if i == len(s):
            return open_ == 0
        ch = s[i]
        if ch == "(":
            return go(i + 1, open_ + 1)
        if ch == ")":
            return go(i + 1, open_ - 1)
        return go(i + 1, open_ + 1) or go(i + 1, open_ - 1) or go(i + 1, open_)
    return go(0, 0)''',
            ),
            dict(
                name="Two stacks of indices",
                time="O(n)",
                space="O(n)",
                why=[
                    "Push indices of <code>(</code> and <code>*</code> on two stacks. A <code>)</code> matches an open bracket if possible, else a star. Afterwards, each remaining <code>(</code> needs a star <em>after</em> it to close it: pair them from the top, checking positions.",
                ],
                code='''def check_valid_string(s):
    opens, stars = [], []
    for i, ch in enumerate(s):
        if ch == "(":
            opens.append(i)
        elif ch == "*":
            stars.append(i)
        elif opens:
            opens.pop()
        elif stars:
            stars.pop()
        else:
            return False
    while opens and stars:
        if opens.pop() > stars.pop():
            return False                         # the star is before the '('
    return not opens''',
            ),
            dict(
                name="Greedy range of possible open counts",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Track <code>lo</code> and <code>hi</code>, the fewest and most unmatched <code>(</code> possible so far. <code>(</code> raises both; <code>)</code> lowers both; <code>*</code> lowers lo and raises hi. If hi drops below 0, even treating every star as <code>(</code> fails. Clamp lo at 0 (a negative count is never a real option). The string is valid iff lo ends at 0.",
                    "Every count between lo and hi is achievable, which is why two numbers summarise all 3<sup>k</sup> choices.",
                ],
                code='''def check_valid_string(s):
    lo = hi = 0
    for ch in s:
        if ch == "(":
            lo, hi = lo + 1, hi + 1
        elif ch == ")":
            lo, hi = lo - 1, hi - 1
        else:
            lo, hi = lo - 1, hi + 1
        if hi < 0:
            return False
        lo = max(lo, 0)
    return lo == 0''',
            ),
        ],
        tests='''assert check_valid_string("()") is True and check_valid_string("(*)") is True and check_valid_string("(*))") is True
assert check_valid_string("*(") is False and check_valid_string("((*") is False
rng = random.Random(10)
for _ in range(150):
    s = "".join(rng.choice("()*") for _ in range(rng.randint(0, 9)))
    def brute(i, o):
        if o < 0: return False
        if i == len(s): return o == 0
        if s[i] == "(": return brute(i + 1, o + 1)
        if s[i] == ")": return brute(i + 1, o - 1)
        return brute(i + 1, o + 1) or brute(i + 1, o - 1) or brute(i + 1, o)
    assert check_valid_string(s) is brute(0, 0)''',
    ),

    # ------------------------------------------------------------------ 135
    dict(
        id="candy",
        lc=135, slug="candy",
        name="Candy",
        difficulty="hard",
        framing=[
            "Give each child at least one candy, and any child with a higher rating than a neighbour must get more than that neighbour. Minimise the total. Each child's constraint comes from both sides; handling them in two separate sweeps is the key idea.",
        ],
        approaches=[
            dict(
                name="Relax until stable",
                time="O(n&sup2;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Start everyone at 1 and repeatedly fix any violated neighbour pair by raising the higher-rated child, until a full pass changes nothing. Each pass is O(n) and up to n passes may be needed on a long slope.",
                ],
                code='''def candy(ratings):
    n, c = len(ratings), [1] * len(ratings)
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if i > 0 and ratings[i] > ratings[i - 1] and c[i] <= c[i - 1]:
                c[i] = c[i - 1] + 1; changed = True
            if i < n - 1 and ratings[i] > ratings[i + 1] and c[i] <= c[i + 1]:
                c[i] = c[i + 1] + 1; changed = True
    return sum(c)''',
            ),
            dict(
                name="Two sweeps",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Left to right: if a child beats its left neighbour, give it one more than that neighbour. Right to left: if it beats its right neighbour, make sure it has more than that neighbour, keeping the larger of the two requirements with <code>max</code>. Each sweep enforces one side's rule without breaking the other, and every value is the smallest satisfying both.",
                ],
                code='''def candy(ratings):
    n = len(ratings)
    c = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)''',
            ),
            dict(
                name="One pass counting slopes",
                time="O(n)",
                space="O(1)",
                why=[
                    "Candies along a rising run are 1, 2, 3, &hellip;; along a falling run they are the same, read backwards. Walk the ratings counting the lengths of rising and falling runs and add arithmetic-series totals directly. The peak between an up-run and a down-run belongs to whichever run is longer, which needs one correction.",
                    "Constant space, at the cost of noticeably trickier bookkeeping than the two sweeps.",
                ],
                code='''def candy(ratings):
    n = len(ratings)
    if n == 1:
        return 1
    total, up, down, peak = 1, 0, 0, 0
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            up += 1; down = 0; peak = up
            total += up + 1
        elif ratings[i] == ratings[i - 1]:
            up = down = peak = 0
            total += 1
        else:
            up = 0; down += 1
            total += down + (0 if down <= peak else 1)   # the peak may need to grow
    return total''',
            ),
        ],
        tests='''assert candy([1, 0, 2]) == 5 and candy([1, 2, 2]) == 4 and candy([1]) == 1
assert candy([1, 3, 4, 5, 2]) == 11 and candy([1, 2, 87, 87, 87, 2, 1]) == 13
rng = random.Random(11)
for _ in range(100):
    r = [rng.randint(0, 4) for _ in range(rng.randint(1, 12))]
    c = [1] * len(r)
    for i in range(1, len(r)):
        if r[i] > r[i - 1]: c[i] = c[i - 1] + 1
    for i in range(len(r) - 2, -1, -1):
        if r[i] > r[i + 1]: c[i] = max(c[i], c[i + 1] + 1)
    assert candy(r) == sum(c)''',
    ),
    ],
),
    ],
)
