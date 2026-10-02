# -*- coding: utf-8 -*-
"""Binary Search topic (NeetCode 250: Binary Search). Same build contract as
content/dsa.py."""

PRELUDE_BS = '''import bisect
import math
import random
from collections import defaultdict
'''


BINARY_SEARCH_TOPIC = dict(
    id="binary-search",
    title="Binary Search",
    prelude=PRELUDE_BS,
    sections=[

dict(
    id="binary-search",
    title="Binary search on arrays and on answers",
    idea=[
        "Binary search needs a <em>monotonic</em> yes/no question: false, false, &hellip;, false, true, &hellip;, true. Find the boundary and you have the answer in O(log n) questions. The question can be about an index in a sorted array, or about a candidate answer (\"can Koko finish at speed k?\") &mdash; the second kind is where most medium and hard problems live.",
        "One loop shape avoids every off-by-one: keep <code>lo</code> on the false side and <code>hi</code> on the true side (or use the half-open <code>[lo, hi)</code> form of <code>bisect_left</code>), and always shrink toward the boundary.",
    ],
    problems=[

    # ------------------------------------------------------------------ 704
    dict(
        id="binary-search",
        lc=704, slug="binary-search",
        name="Binary Search",
        difficulty="easy",
        framing=[
            "Find <code>target</code> in a sorted array of distinct integers, or return -1. The template everything else on this page builds on.",
        ],
        approaches=[
            dict(
                name="Linear scan",
                time="O(n)",
                space="O(1)",
                tag="ignores sorting",
                why=["Correct on any array, which is exactly why it wastes the sortedness."],
                code='''def search(nums, target):
    for i, x in enumerate(nums):
        if x == target:
            return i
    return -1''',
            ),
            dict(
                name="Recursive binary search",
                time="O(log n)",
                space="O(log n)",
                why=[
                    "Compare with the middle and recurse into the half that can contain the target. Every call halves the range, so the depth is log<sub>2</sub> n &mdash; and each level is a stack frame.",
                ],
                code='''def search(nums, target):
    def go(lo, hi):
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        return go(mid + 1, hi) if nums[mid] < target else go(lo, mid - 1)
    return go(0, len(nums) - 1)''',
            ),
            dict(
                name="Iterative binary search",
                time="O(log n)",
                space="O(1)",
                best=True,
                why=[
                    "The same halving in a loop. The invariant: if the target is present, it lies in <code>[lo, hi]</code>. <code>lo &lt;= hi</code> keeps looping while that range is non-empty.",
                    "In languages with fixed-width integers, write <code>lo + (hi - lo) // 2</code> to avoid overflow; Python does not need it, but saying so shows you know why the idiom exists. <code>bisect.bisect_left</code> is the library version.",
                ],
                code='''def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1''',
            ),
        ],
        tests='''assert search([-1, 0, 3, 5, 9, 12], 9) == 4
assert search([-1, 0, 3, 5, 9, 12], 2) == -1
assert search([5], 5) == 0
rng = random.Random(0)
for _ in range(60):
    nums = sorted(rng.sample(range(-30, 30), rng.randint(1, 15)))
    t = rng.randint(-32, 32)
    assert search(nums, t) == (nums.index(t) if t in nums else -1)''',
    ),

    # ------------------------------------------------------------------ 35
    dict(
        id="search-insert-position",
        lc=35, slug="search-insert-position",
        name="Search Insert Position",
        difficulty="easy",
        framing=[
            "Return the index of <code>target</code>, or where it would be inserted to keep the array sorted. That is the <strong>lower bound</strong>: the first index whose value is &ge; target. Learning to write lower bound cleanly is worth more than any single problem here.",
        ],
        approaches=[
            dict(
                name="Linear scan for the first value &ge; target",
                time="O(n)",
                space="O(1)",
                why=["The definition, directly."],
                code='''def search_insert(nums, target):
    for i, x in enumerate(nums):
        if x >= target:
            return i
    return len(nums)''',
            ),
            dict(
                name="Lower bound on a half-open range",
                time="O(log n)",
                space="O(1)",
                best=True,
                why=[
                    "Search <code>[lo, hi)</code> with <code>hi = len(nums)</code> (the answer can be one past the end). If <code>nums[mid] &lt; target</code>, the answer is strictly after mid; otherwise mid itself might be the answer, so keep it with <code>hi = mid</code>. When <code>lo == hi</code> the range is a single position: the answer.",
                    "This loop never needs a special case for \"not found\" or \"past the end\", which is why it is the version to memorise. It is exactly <code>bisect.bisect_left</code>.",
                ],
                code='''def search_insert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid                            # mid may be the answer
    return lo''',
            ),
        ],
        tests='''assert search_insert([1, 3, 5, 6], 5) == 2
assert search_insert([1, 3, 5, 6], 2) == 1
assert search_insert([1, 3, 5, 6], 7) == 4
assert search_insert([1, 3, 5, 6], 0) == 0
rng = random.Random(1)
for _ in range(60):
    nums = sorted(rng.sample(range(40), rng.randint(1, 12)))
    t = rng.randint(-2, 42)
    assert search_insert(nums, t) == bisect.bisect_left(nums, t)''',
    ),

    # ------------------------------------------------------------------ 374
    dict(
        id="guess-number",
        lc=374, slug="guess-number-higher-or-lower",
        name="Guess Number Higher Or Lower",
        difficulty="easy",
        framing=[
            "A number is picked from <code>1..n</code>; <code>guess(num)</code> returns -1 if the pick is lower, 1 if higher, 0 if right. Minimise calls. The array is implicit &mdash; binary search over a range of values rather than a list.",
        ],
        approaches=[
            dict(
                name="Try every number",
                time="O(n) calls",
                space="O(1)",
                tag="brute force",
                why=["Guess 1, 2, 3, &hellip; ignoring the higher/lower feedback."],
                code='''def guess_number(n):
    for k in range(1, n + 1):
        if guess(k) == 0:
            return k''',
            ),
            dict(
                name="Binary search on the range",
                time="O(log n) calls",
                space="O(1)",
                best=True,
                why=[
                    "Each answer halves the remaining range, so at most about log<sub>2</sub> n + 1 guesses &mdash; 32 for n = 2<sup>31</sup>. Ternary search (two guesses per round) looks tempting but costs more calls: it removes 2/3 of the range for 2 guesses, versus 3/4 for two binary rounds.",
                ],
                code='''def guess_number(n):
    lo, hi = 1, n
    while True:
        mid = (lo + hi) // 2
        g = guess(mid)
        if g == 0:
            return mid
        if g < 0:
            hi = mid - 1                       # the pick is lower
        else:
            lo = mid + 1''',
            ),
        ],
        tests='''CALLS = [0]
def guess(num):
    CALLS[0] += 1
    return 0 if num == PICK else (-1 if PICK < num else 1)

for n, PICK in [(10, 6), (1, 1), (2, 1), (2, 2), (100, 100)]:
    assert guess_number(n) == PICK
rng = random.Random(2)
for _ in range(40):
    n = rng.randint(1, 1000); PICK = rng.randint(1, n)
    assert guess_number(n) == PICK''',
    ),

    # ------------------------------------------------------------------ 69
    dict(
        id="sqrt-x",
        lc=69, slug="sqrtx",
        name="Sqrt(x)",
        difficulty="easy",
        framing=[
            "Return <code>floor(&radic;x)</code> without <code>**</code> or <code>math.sqrt</code>. The answer is the largest k with k&sup2; &le; x &mdash; a monotonic condition, so binary search on k. Newton's method converges far faster and is worth knowing as the follow-up.",
        ],
        approaches=[
            dict(
                name="Count up",
                time="O(&radic;x)",
                space="O(1)",
                tag="brute force",
                why=["Increase k while (k + 1)&sup2; &le; x. About 46,000 steps for x = 2<sup>31</sup>."],
                code='''def my_sqrt(x):
    k = 0
    while (k + 1) * (k + 1) <= x:
        k += 1
    return k''',
            ),
            dict(
                name="Binary search on the answer",
                time="O(log x)",
                space="O(1)",
                best=True,
                why=[
                    "Search k in <code>[0, x]</code> for the last value with k&sup2; &le; x. Using the \"upper mid\" <code>(lo + hi + 1) // 2</code> with <code>lo = mid</code> on success guarantees progress when two candidates remain.",
                ],
                code='''def my_sqrt(x):
    lo, hi = 0, x
    while lo < hi:
        mid = (lo + hi + 1) // 2               # upper mid: avoids an infinite loop
        if mid * mid <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo''',
            ),
            dict(
                name="Newton's method on integers",
                time="O(log log x) iterations",
                space="O(1)",
                tag="fastest",
                why=[
                    "Newton's iteration for k&sup2; = x is <code>k &larr; (k + x / k) / 2</code>. Starting from any k &ge; &radic;x, the integer version decreases monotonically to the floor of the root, and the number of correct digits roughly doubles each step. This is essentially what <code>math.isqrt</code> does.",
                ],
                code='''def my_sqrt(x):
    if x < 2:
        return x
    k = x
    while k * k > x:
        k = (k + x // k) // 2
    return k''',
            ),
        ],
        tests='''assert my_sqrt(4) == 2 and my_sqrt(8) == 2 and my_sqrt(0) == 0 and my_sqrt(1) == 1
for x in list(range(0, 2000)) + [2 ** 31 - 1, 10 ** 12 + 7]:
    assert my_sqrt(x) == math.isqrt(x), x''',
    ),

    # ------------------------------------------------------------------ 74
    dict(
        id="search-2d-matrix",
        lc=74, slug="search-a-2d-matrix",
        name="Search a 2D Matrix",
        difficulty="medium",
        framing=[
            "Each row is sorted and each row's first value exceeds the previous row's last. Read row by row, the matrix is one sorted array of m &middot; n values &mdash; so a single binary search with index arithmetic solves it.",
        ],
        approaches=[
            dict(
                name="Scan everything",
                time="O(m &middot; n)",
                space="O(1)",
                tag="brute force",
                why=["Check every cell."],
                code='''def search_matrix(matrix, target):
    return any(target in row for row in matrix)''',
            ),
            dict(
                name="Staircase from the top-right",
                time="O(m + n)",
                space="O(1)",
                why=[
                    "From the top-right corner, a value larger than the target means the whole column below is larger: move left. Smaller means the whole row to the left is smaller: move down. Each step discards a row or column. This works even under the weaker condition of LeetCode 240 (rows and columns sorted separately), which is its real use.",
                ],
                code='''def search_matrix(matrix, target):
    r, c = 0, len(matrix[0]) - 1
    while r < len(matrix) and c >= 0:
        v = matrix[r][c]
        if v == target:
            return True
        if v > target:
            c -= 1
        else:
            r += 1
    return False''',
            ),
            dict(
                name="Binary search the row, then the column",
                time="O(log m + log n)",
                space="O(1)",
                why=[
                    "Find the last row whose first value is &le; the target, then binary-search inside it. Two searches, same total cost as one search over m &middot; n values.",
                ],
                code='''def search_matrix(matrix, target):
    firsts = [row[0] for row in matrix]
    r = bisect.bisect_right(firsts, target) - 1
    if r < 0:
        return False
    row = matrix[r]
    i = bisect.bisect_left(row, target)
    return i < len(row) and row[i] == target''',
            ),
            dict(
                name="One binary search over the flattened index",
                time="O(log(m &middot; n))",
                space="O(1)",
                best=True,
                why=[
                    "Treat index k in <code>[0, m&middot;n)</code> as cell <code>(k // n, k % n)</code> and run ordinary binary search. No row list is built and there is only one loop.",
                ],
                code='''def search_matrix(matrix, target):
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = matrix[mid // n][mid % n]
        if v == target:
            return True
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False''',
            ),
        ],
        tests='''M = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
assert search_matrix(M, 3) is True and search_matrix(M, 13) is False
assert search_matrix([[1]], 0) is False
rng = random.Random(3)
for _ in range(40):
    m, n = rng.randint(1, 5), rng.randint(1, 5)
    vals = sorted(rng.sample(range(100), m * n))
    M = [vals[i * n:(i + 1) * n] for i in range(m)]
    t = rng.randint(-1, 101)
    assert search_matrix(M, t) is (t in vals)''',
    ),

    # ------------------------------------------------------------------ 875
    dict(
        id="koko-eating-bananas",
        lc=875, slug="koko-eating-bananas",
        name="Koko Eating Bananas",
        difficulty="medium",
        framing=[
            "Find the smallest eating speed k so Koko finishes every pile within h hours (one pile per hour at most, <code>ceil(pile / k)</code> hours per pile). The first <strong>binary search on the answer</strong>: \"can she finish at speed k?\" is false for small k and true for large k, with one boundary.",
        ],
        approaches=[
            dict(
                name="Try every speed from 1 upward",
                time="O(max(piles) &middot; n)",
                space="O(1)",
                tag="brute force",
                why=[
                    "Check speeds 1, 2, 3, &hellip; until one works. The answer can be as large as the biggest pile (10<sup>9</sup>), so this can take a billion checks.",
                ],
                code='''def min_eating_speed(piles, h):
    k = 1
    while sum((p + k - 1) // k for p in piles) > h:
        k += 1
    return k''',
            ),
            dict(
                name="Binary search on the speed",
                time="O(n log max(piles))",
                space="O(1)",
                best=True,
                why=[
                    "Hours needed never increase as k increases, so feasibility is monotonic. Search k in <code>[1, max(piles)]</code> (at speed max, every pile takes one hour, and h &ge; n is guaranteed). Each check is O(n).",
                    "<code>(p + k - 1) // k</code> is integer ceiling division; avoid floats for exactness.",
                ],
                code='''def min_eating_speed(piles, h):
    def hours(k):
        return sum((p + k - 1) // k for p in piles)

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours(mid) <= h:
            hi = mid                           # feasible: try slower
        else:
            lo = mid + 1
    return lo''',
            ),
        ],
        tests='''assert min_eating_speed([3, 6, 7, 11], 8) == 4
assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30
assert min_eating_speed([30, 11, 23, 4, 20], 6) == 23
rng = random.Random(4)
for _ in range(40):
    piles = [rng.randint(1, 30) for _ in range(rng.randint(1, 6))]
    h = rng.randint(len(piles), 40)
    k = 1
    while sum((p + k - 1) // k for p in piles) > h:
        k += 1
    assert min_eating_speed(piles, h) == k''',
    ),

    # ------------------------------------------------------------------ 1011
    dict(
        id="ship-within-days",
        lc=1011, slug="capacity-to-ship-packages-within-d-days",
        name="Capacity to Ship Packages Within D Days",
        difficulty="medium",
        framing=[
            "Packages ship in order; each day's load cannot exceed the ship's capacity. Find the minimum capacity that ships everything in <code>days</code> days. Same shape as Koko: a greedy check (\"how many days at capacity c?\") that is monotonic in c.",
        ],
        approaches=[
            dict(
                name="Try every capacity upward",
                time="O(n &middot; (sum - max))",
                space="O(1)",
                tag="brute force",
                why=[
                    "The capacity must be at least the heaviest package and at most the total. Try each in turn with the greedy day count.",
                ],
                code='''def ship_within_days(weights, days):
    def days_needed(cap):
        d, load = 1, 0
        for w in weights:
            if load + w > cap:
                d, load = d + 1, 0
            load += w
        return d

    cap = max(weights)
    while days_needed(cap) > days:
        cap += 1
    return cap''',
            ),
            dict(
                name="Binary search on capacity with a greedy check",
                time="O(n log(sum))",
                space="O(1)",
                best=True,
                why=[
                    "For a fixed capacity, loading each day as full as possible (greedy) minimises the number of days &mdash; starting a new day early can never help later days. More capacity never needs more days, so binary-search the smallest feasible capacity in <code>[max, sum]</code>.",
                ],
                code='''def ship_within_days(weights, days):
    def days_needed(cap):
        d, load = 1, 0
        for w in weights:
            if load + w > cap:
                d, load = d + 1, 0
            load += w
        return d

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo''',
            ),
        ],
        tests='''assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
assert ship_within_days([3, 2, 2, 4, 1, 4], 3) == 6
assert ship_within_days([1, 2, 3, 1, 1], 4) == 3
rng = random.Random(5)
for _ in range(40):
    w = [rng.randint(1, 10) for _ in range(rng.randint(1, 8))]
    d = rng.randint(1, len(w))
    best = None
    for cap in range(max(w), sum(w) + 1):
        need, load = 1, 0
        for x in w:
            if load + x > cap:
                need, load = need + 1, 0
            load += x
        if need <= d:
            best = cap; break
    assert ship_within_days(w, d) == best''',
    ),

    # ------------------------------------------------------------------ 153
    dict(
        id="find-min-rotated",
        lc=153, slug="find-minimum-in-rotated-sorted-array",
        name="Find Minimum In Rotated Sorted Array",
        difficulty="medium",
        framing=[
            "A sorted array of distinct values was rotated. Find the minimum in O(log n). The minimum is where the rotation broke the order; comparing the middle with the <strong>right end</strong> tells you which side of the break the middle is on.",
        ],
        approaches=[
            dict(
                name="Linear scan",
                time="O(n)",
                space="O(1)",
                why=["<code>min(nums)</code>. Ignores the structure."],
                code='''def find_min(nums):
    return min(nums)''',
            ),
            dict(
                name="Binary search against the right end",
                time="O(log n)",
                space="O(1)",
                best=True,
                why=[
                    "If <code>nums[mid] &gt; nums[hi]</code>, the range from mid to hi contains the drop, so the minimum is strictly right of mid. Otherwise mid to hi is sorted, so the minimum is at mid or to its left. The range shrinks to the minimum.",
                    "Comparing with the right end rather than the left is deliberate: when the array is not rotated at all, the left comparison cannot tell \"sorted\" from \"rotated\", while the right one handles both.",
                ],
                code='''def find_min(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1                       # the drop is to the right
        else:
            hi = mid                           # mid..hi sorted: min at mid or left
    return nums[lo]''',
            ),
        ],
        tests='''assert find_min([3, 4, 5, 1, 2]) == 1
assert find_min([4, 5, 6, 7, 0, 1, 2]) == 0
assert find_min([11, 13, 15, 17]) == 11
assert find_min([2, 1]) == 1
for n in range(1, 12):
    base = list(range(n))
    for r in range(n):
        assert find_min(base[r:] + base[:r]) == 0''',
    ),

    # ------------------------------------------------------------------ 33
    dict(
        id="search-rotated",
        lc=33, slug="search-in-rotated-sorted-array",
        name="Search In Rotated Sorted Array",
        difficulty="medium",
        framing=[
            "Find a target in a rotated sorted array of distinct values in O(log n). At any midpoint, at least one half is properly sorted, and for a sorted half you can tell in O(1) whether the target lies inside it.",
        ],
        approaches=[
            dict(
                name="Linear scan",
                time="O(n)",
                space="O(1)",
                why=["Check every element."],
                code='''def search_rotated(nums, target):
    return nums.index(target) if target in nums else -1''',
            ),
            dict(
                name="Find the rotation point, then search one side",
                time="O(log n)",
                space="O(1)",
                why=[
                    "First find the index of the minimum (the previous problem). Both sides of it are sorted; pick the side whose range contains the target and binary-search it. Two clean searches, each easy to verify.",
                ],
                code='''def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    pivot = lo
    if nums[pivot] <= target <= nums[-1]:
        lo, hi = pivot, len(nums)
    else:
        lo, hi = 0, pivot
    i = bisect.bisect_left(nums, target, lo, hi)
    return i if i < len(nums) and nums[i] == target else -1''',
            ),
            dict(
                name="One pass: decide which half is sorted",
                time="O(log n)",
                space="O(1)",
                best=True,
                why=[
                    "If <code>nums[lo] &le; nums[mid]</code>, the left half is sorted: go left exactly when the target lies in <code>[nums[lo], nums[mid])</code>. Otherwise the right half is sorted: go right exactly when the target lies in <code>(nums[mid], nums[hi]]</code>. One loop, no pivot search.",
                ],
                code='''def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:                       # left half sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                           # right half sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1''',
            ),
        ],
        tests='''assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
assert search_rotated([1], 0) == -1
for n in range(1, 10):
    base = list(range(0, 2 * n, 2))
    for r in range(n):
        arr = base[r:] + base[:r]
        for t in range(-1, 2 * n + 1):
            assert search_rotated(arr, t) == (arr.index(t) if t in arr else -1)''',
    ),

    # ------------------------------------------------------------------ 81
    dict(
        id="search-rotated-ii",
        lc=81, slug="search-in-rotated-sorted-array-ii",
        name="Search In Rotated Sorted Array II",
        difficulty="medium",
        framing=[
            "The same search, but values may repeat, and you only report whether the target exists. Duplicates break the \"which half is sorted?\" test: with <code>nums[lo] == nums[mid] == nums[hi]</code>, either half could contain the rotation. The follow-up asks how that affects complexity &mdash; the honest answer is that the worst case becomes O(n).",
        ],
        approaches=[
            dict(
                name="Linear scan",
                time="O(n)",
                space="O(1)",
                why=["<code>target in nums</code>. Matches the worst case of the clever version."],
                code='''def search_rotated_ii(nums, target):
    return target in nums''',
            ),
            dict(
                name="Binary search, shrink both ends on ambiguity",
                time="O(log n) typical, O(n) worst",
                space="O(1)",
                best=True,
                why=[
                    "Same as the distinct-values version, with one addition: when <code>nums[lo] == nums[mid] == nums[hi]</code>, you cannot tell which half is sorted, but neither end can be the target (it equals mid, which was checked), so drop both ends and continue.",
                    "An array like <code>[1, 1, 1, &hellip;, 1, 2, 1, 1]</code> forces that step repeatedly, so the worst case is O(n). No algorithm can do better on such inputs: the lone different value can be anywhere.",
                ],
                code='''def search_rotated_ii(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return True
        if nums[lo] == nums[mid] == nums[hi]:
            lo, hi = lo + 1, hi - 1                     # ambiguous: shrink both ends
        elif nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False''',
            ),
        ],
        tests='''assert search_rotated_ii([2, 5, 6, 0, 0, 1, 2], 0) is True
assert search_rotated_ii([2, 5, 6, 0, 0, 1, 2], 3) is False
assert search_rotated_ii([1, 0, 1, 1, 1], 0) is True
rng = random.Random(6)
for _ in range(200):
    base = sorted(rng.randint(0, 4) for _ in range(rng.randint(1, 10)))
    r = rng.randrange(len(base))
    arr = base[r:] + base[:r]
    t = rng.randint(-1, 5)
    assert search_rotated_ii(arr, t) is (t in arr)''',
    ),

    # ------------------------------------------------------------------ 981
    dict(
        id="time-based-kv-store",
        lc=981, slug="time-based-key-value-store",
        name="Time Based Key-Value Store",
        difficulty="medium",
        framing=[
            "<code>set(key, value, timestamp)</code> and <code>get(key, timestamp)</code>, which returns the value set at the largest timestamp &le; the one asked for. Timestamps for <code>set</code> arrive strictly increasing, so each key's history is already sorted &mdash; binary search it.",
        ],
        approaches=[
            dict(
                name="Scan the key's history",
                time="set O(1), get O(n)",
                space="O(n)",
                why=["Store each key's (timestamp, value) list; walk it backwards to the first timestamp that is not too large."],
                code='''class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)

    def set(self, key, value, timestamp):
        self.store[key].append((timestamp, value))

    def get(self, key, timestamp):
        for t, v in reversed(self.store[key]):
            if t <= timestamp:
                return v
        return ""''',
            ),
            dict(
                name="Binary search each key's sorted timestamps",
                time="set O(1), get O(log n)",
                space="O(n)",
                best=True,
                why=[
                    "Appending keeps timestamps sorted for free, so <code>get</code> is an upper-bound search: <code>bisect_right(times, timestamp) - 1</code> is the last entry not after the query. Keeping timestamps and values in parallel lists lets <code>bisect</code> work on plain integers.",
                ],
                code='''class TimeMap:
    def __init__(self):
        self.times = defaultdict(list)
        self.values = defaultdict(list)

    def set(self, key, value, timestamp):
        self.times[key].append(timestamp)       # arrives in increasing order
        self.values[key].append(value)

    def get(self, key, timestamp):
        i = bisect.bisect_right(self.times[key], timestamp) - 1
        return self.values[key][i] if i >= 0 else ""''',
            ),
        ],
        tests='''tm = TimeMap()
tm.set("foo", "bar", 1)
assert tm.get("foo", 1) == "bar" and tm.get("foo", 3) == "bar"
tm.set("foo", "bar2", 4)
assert tm.get("foo", 4) == "bar2" and tm.get("foo", 5) == "bar2" and tm.get("foo", 0) == ""
assert tm.get("nope", 10) == ""''',
    ),

    # ------------------------------------------------------------------ 410
    dict(
        id="split-array-largest-sum",
        lc=410, slug="split-array-largest-sum",
        name="Split Array Largest Sum",
        difficulty="hard",
        framing=[
            "Split the array into <code>k</code> non-empty contiguous parts to minimise the largest part's sum. It is Ship Within Days in disguise &mdash; parts are days, the largest sum is the capacity &mdash; so the binary-search-on-answer solution transfers directly. A DP solution exists too and is the natural first idea.",
        ],
        approaches=[
            dict(
                name="Try every split recursively",
                time="O(n<sup>k</sup>)",
                space="O(k)",
                tag="brute force",
                why=[
                    "Choose where the first part ends, recurse on the rest with k - 1 parts, and take the best. Exponential without caching.",
                ],
                code='''def split_array(nums, k):
    def best(i, parts):
        if parts == 1:
            return sum(nums[i:])
        result, total = float("inf"), 0
        for j in range(i, len(nums) - parts + 1):
            total += nums[j]
            result = min(result, max(total, best(j + 1, parts - 1)))
        return result
    return best(0, k)''',
            ),
            dict(
                name="DP over (start, parts left)",
                time="O(k &middot; n&sup2;)",
                space="O(k &middot; n)",
                why=[
                    "The recursion only depends on <code>(i, parts)</code>, so memoise it. With prefix sums, each state tries O(n) split points: O(k &middot; n&sup2;). Fine for the constraints (n &le; 1000, k &le; 50) in a compiled language; slow in Python.",
                ],
                code='''def split_array(nums, k):
    from functools import cache
    P = [0]
    for x in nums:
        P.append(P[-1] + x)
    n = len(nums)

    @cache
    def best(i, parts):
        if parts == 1:
            return P[n] - P[i]
        return min(max(P[j + 1] - P[i], best(j + 1, parts - 1))
                   for j in range(i, n - parts + 1))

    return best(0, k)''',
            ),
            dict(
                name="Binary search on the largest sum",
                time="O(n log(sum))",
                space="O(1)",
                best=True,
                why=[
                    "For a cap S, greedily cut a new part whenever adding the next element would exceed S; that uses the fewest possible parts. If it needs at most k parts, S is feasible (extra parts can always be created by splitting further). Feasibility is monotonic in S, so binary-search S in <code>[max(nums), sum(nums)]</code>.",
                    "Linear per check, logarithmic number of checks &mdash; far better than the DP.",
                ],
                code='''def split_array(nums, k):
    def parts_needed(cap):
        parts, total = 1, 0
        for x in nums:
            if total + x > cap:
                parts, total = parts + 1, 0
            total += x
        return parts

    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if parts_needed(mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo''',
            ),
        ],
        tests='''assert split_array([7, 2, 5, 10, 8], 2) == 18
assert split_array([1, 2, 3, 4, 5], 2) == 9
assert split_array([1, 4, 4], 3) == 4
import itertools
rng = random.Random(7)
for _ in range(40):
    nums = [rng.randint(0, 10) for _ in range(rng.randint(1, 7))]
    k = rng.randint(1, len(nums))
    best = min(max(sum(nums[a:b]) for a, b in zip((0,) + cuts, cuts + (len(nums),)))
               for cuts in itertools.combinations(range(1, len(nums)), k - 1))
    assert split_array(nums, k) == best''',
    ),

    # ------------------------------------------------------------------ 4
    dict(
        id="median-two-sorted-arrays",
        lc=4, slug="median-of-two-sorted-arrays",
        name="Median of Two Sorted Arrays",
        difficulty="hard",
        framing=[
            "The median of two sorted arrays in O(log(m + n)). Merging is O(m + n) and obvious. The logarithmic solution binary-searches a <strong>partition</strong>: split both arrays so the left halves together hold half of all elements and every left element is &le; every right element. Then the median is read off the four values at the cut.",
        ],
        approaches=[
            dict(
                name="Merge fully, pick the middle",
                time="O(m + n)",
                space="O(m + n)",
                why=[
                    "Merge the two sorted arrays (the merge step of merge sort) and take the middle one or two values. Simple and correct; misses the required bound.",
                ],
                code='''def find_median_sorted_arrays(a, b):
    merged, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            merged.append(a[i]); i += 1
        else:
            merged.append(b[j]); j += 1
    merged += a[i:] + b[j:]
    n = len(merged)
    return merged[n // 2] if n % 2 else (merged[n // 2 - 1] + merged[n // 2]) / 2''',
            ),
            dict(
                name="Walk to the middle without storing",
                time="O(m + n)",
                space="O(1)",
                why=[
                    "Run the merge but only count, remembering the last two values seen, and stop after (m + n) / 2 + 1 steps. Same time, no merged array.",
                ],
                code='''def find_median_sorted_arrays(a, b):
    total = len(a) + len(b)
    i = j = 0
    prev = cur = 0
    for _ in range(total // 2 + 1):
        prev = cur
        if j >= len(b) or (i < len(a) and a[i] <= b[j]):
            cur = a[i]; i += 1
        else:
            cur = b[j]; j += 1
    return cur if total % 2 else (prev + cur) / 2''',
            ),
            dict(
                name="Binary search the partition of the shorter array",
                time="O(log min(m, n))",
                space="O(1)",
                best=True,
                why=[
                    "Take <code>i</code> elements from the shorter array A and <code>j = half - i</code> from B for the left side. The split is correct when <code>A[i-1] &le; B[j]</code> and <code>B[j-1] &le; A[i]</code>. If <code>A[i-1] &gt; B[j]</code>, too many came from A: move i left. Otherwise move it right. Out-of-range positions count as &plusmn;&infin;.",
                    "Once the split is correct, the median is <code>max(left side)</code> for odd totals, or the average of <code>max(left)</code> and <code>min(right)</code> for even. Searching only the shorter array makes the bound O(log min(m, n)) and keeps j in range.",
                ],
                code='''def find_median_sorted_arrays(a, b):
    if len(a) > len(b):
        a, b = b, a                              # search the shorter one
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    INF = float("inf")
    while True:
        i = (lo + hi) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else -INF
        a_right = a[i] if i < m else INF
        b_left = b[j - 1] if j > 0 else -INF
        b_right = b[j] if j < n else INF
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return max(a_left, b_left)
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1                           # took too many from a
        else:
            lo = i + 1''',
            ),
        ],
        tests='''assert find_median_sorted_arrays([1, 3], [2]) == 2
assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
assert find_median_sorted_arrays([], [1]) == 1
rng = random.Random(8)
for _ in range(100):
    a = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 6)))
    b = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0 if a else 1, 6)))
    c = sorted(a + b); n = len(c)
    expect = c[n // 2] if n % 2 else (c[n // 2 - 1] + c[n // 2]) / 2
    assert find_median_sorted_arrays(a, b) == expect''',
    ),

    # ------------------------------------------------------------------ 1095
    dict(
        id="find-in-mountain-array",
        lc=1095, slug="find-in-mountain-array",
        name="Find in Mountain Array",
        difficulty="hard",
        framing=[
            "The array strictly increases to a peak, then strictly decreases. It is only reachable through <code>get(i)</code> and <code>length()</code>, and you may make at most 100 <code>get</code> calls. Return the smallest index holding the target. Three binary searches: find the peak, search the rising side, then the falling side.",
        ],
        approaches=[
            dict(
                name="Scan every index",
                time="O(n) calls",
                space="O(1)",
                tag="exceeds the call limit",
                why=[
                    "Call <code>get</code> on each index until the target appears. Correct, but up to 10<sup>4</sup> calls against a limit of 100.",
                ],
                code='''def find_in_mountain_array(target, mountain):
    for i in range(mountain.length()):
        if mountain.get(i) == target:
            return i
    return -1''',
            ),
            dict(
                name="Peak search, then two binary searches",
                time="O(log n) calls",
                space="O(1)",
                best=True,
                why=[
                    "Find the peak by comparing <code>get(mid)</code> with <code>get(mid + 1)</code>: rising means the peak is to the right. Then binary-search the increasing part <code>[0, peak]</code>; only if the target is absent there, search the decreasing part with the comparison reversed. Checking the left side first guarantees the smallest index.",
                    "About 3 log<sub>2</sub>(10<sup>4</sup>) &asymp; 42 calls plus the pairs in the peak search &mdash; comfortably within 100.",
                ],
                code='''def find_in_mountain_array(target, mountain):
    n = mountain.length()
    lo, hi = 0, n - 1
    while lo < hi:                               # 1. find the peak
        mid = (lo + hi) // 2
        if mountain.get(mid) < mountain.get(mid + 1):
            lo = mid + 1
        else:
            hi = mid
    peak = lo

    def search(lo, hi, ascending):
        while lo <= hi:
            mid = (lo + hi) // 2
            v = mountain.get(mid)
            if v == target:
                return mid
            if (v < target) == ascending:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

    i = search(0, peak, True)                    # 2. the rising side first
    return i if i != -1 else search(peak + 1, n - 1, False)''',
            ),
        ],
        tests='''class MountainArray:
    def __init__(self, arr):
        self.arr, self.calls = arr, 0
    def get(self, i):
        self.calls += 1
        return self.arr[i]
    def length(self):
        return len(self.arr)

assert find_in_mountain_array(3, MountainArray([1, 2, 3, 4, 5, 3, 1])) == 2
assert find_in_mountain_array(3, MountainArray([0, 1, 2, 4, 2, 1])) == -1
rng = random.Random(9)
for _ in range(60):
    up = sorted(rng.sample(range(0, 50), rng.randint(1, 20)))
    down = sorted(rng.sample(range(0, up[-1]), min(up[-1], rng.randint(1, 20))), reverse=True)
    arr = up + down
    t = rng.choice(arr + [99])
    expect = arr.index(t) if t in arr else -1
    assert find_in_mountain_array(t, MountainArray(arr)) == expect
big = MountainArray(list(range(5000)) + list(range(4999, -1, -1))[1:])
assert find_in_mountain_array(4321, big) == 4321''',
    ),
    ],
),
    ],
)
