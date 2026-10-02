# -*- coding: utf-8 -*-
"""Segment Trees and Fenwick Trees topic. Same build contract as
content/dsa.py: every approach runs with PRELUDE + this prelude + the
problem's tests, and the tests cross-check against a brute force."""

PRELUDE_RQ = '''import bisect
import random
from itertools import accumulate
'''


RANGE_QUERY_TOPIC = dict(
    id="range-query",
    title="Segment Trees and Fenwick Trees",
    prelude=PRELUDE_RQ,
    blurb=[
        "A prefix-sum array answers \"sum of <code>a[l..r]</code>\" in O(1), but a single update to the array invalidates O(n) of it. Fenwick trees and segment trees are the two standard ways to make <em>both</em> the query and the update O(log n).",
        "The second half of the topic is the trick that makes them show up in hard problems that never mention ranges: <strong>count pairs by inserting values into a tree as you scan</strong>. \"How many earlier elements are bigger than this one?\" is a prefix-count query over values, and a Fenwick tree indexed by value answers it in O(log n).",
    ],
    convention=[
        "<code>n</code> is the array length and <code>q</code> the number of operations. Fenwick trees here are <strong>1-indexed</strong> internally: the bit trick <code>i &amp; -i</code> needs <code>i &gt; 0</code>.",
    ],
    sections=[

dict(
    id="fenwick",
    title="Prefix sums and the Fenwick tree",
    idea=[
        "A <strong>Fenwick tree</strong> (binary indexed tree) stores, at index <code>i</code>, the sum of a block of the array that ends at <code>i</code> and whose length is the lowest set bit of <code>i</code>. Index 12 (<code>1100</code>) covers 4 elements, index 13 (<code>1101</code>) covers 1, index 16 covers 16.",
        "To get a prefix sum, add the block at <code>i</code> and jump to <code>i - (i &amp; -i)</code>, which strips the lowest set bit. To update, add to the block at <code>i</code> and jump to <code>i + (i &amp; -i)</code>, the next block that also contains position <code>i</code>. Both loops touch at most one block per bit: O(log n).",
        "It is ten lines, needs no tree nodes, and covers anything that is an invertible sum (sums, counts, XOR). When you need min/max or range updates, reach for a segment tree instead.",
    ],
    problems=[

    # ------------------------------------------------------------------ 303
    dict(
        id="range-sum-query-immutable",
        lc=303, slug="range-sum-query-immutable",
        name="Range Sum Query - Immutable",
        difficulty="easy",
        framing=[
            "The baseline for the whole topic. The array never changes, so the right answer is a prefix-sum array: O(n) once, O(1) per query. Everything later in this topic exists because updates break this.",
        ],
        approaches=[
            dict(
                name="Sum the slice on every query",
                time="O(n) per query",
                space="O(1)",
                why=[
                    "Correct and obvious. With q queries it costs O(n&middot;q), which is what the follow-up questions are designed to punish.",
                ],
                code='''class NumArray:
    def __init__(self, nums):
        self.nums = nums

    def sumRange(self, left, right):
        return sum(self.nums[left:right + 1])''',
            ),
            dict(
                name="Prefix sums",
                time="O(n) build, O(1) per query",
                space="O(n)",
                best=True,
                why=[
                    "<code>pre[i]</code> is the sum of the first <code>i</code> elements, with <code>pre[0] = 0</code>. Then <code>sum(l..r) = pre[r+1] - pre[l]</code>.",
                    "The leading zero removes the special case for <code>l = 0</code>. Off-by-one errors in this formula are the usual bug, so say the definition of <code>pre[i]</code> out loud before writing the subtraction.",
                ],
                code='''class NumArray:
    def __init__(self, nums):
        self.pre = [0] + list(accumulate(nums))

    def sumRange(self, left, right):
        return self.pre[right + 1] - self.pre[left]''',
            ),
        ],
        tests='''a = NumArray([-2, 0, 3, -5, 2, -1])
assert a.sumRange(0, 2) == 1
assert a.sumRange(2, 5) == -1
assert a.sumRange(0, 5) == -3

rng = random.Random(1)
for _ in range(50):
    nums = [rng.randint(-50, 50) for _ in range(rng.randint(1, 30))]
    obj = NumArray(nums)
    for _ in range(20):
        l = rng.randrange(len(nums)); r = rng.randrange(l, len(nums))
        assert obj.sumRange(l, r) == sum(nums[l:r + 1])''',
    ),

    # ------------------------------------------------------------------ 307
    dict(
        id="range-sum-query-mutable",
        lc=307, slug="range-sum-query-mutable",
        name="Range Sum Query - Mutable",
        difficulty="medium",
        framing=[
            "Now point updates are mixed in with range queries. A plain array makes updates O(1) and queries O(n); a prefix array makes queries O(1) and updates O(n). Either way q operations can cost O(n&middot;q). The goal is O(log n) for both.",
            "This is the problem to learn both structures on: the Fenwick tree is the short answer, the segment tree is the one that generalises.",
        ],
        approaches=[
            dict(
                name="Plain array",
                time="O(1) update, O(n) query",
                space="O(1)",
                why=[
                    "Updates are trivial and every query re-sums the slice. Fine when queries are rare.",
                ],
                code='''class NumArray:
    def __init__(self, nums):
        self.nums = list(nums)

    def update(self, index, val):
        self.nums[index] = val

    def sumRange(self, left, right):
        return sum(self.nums[left:right + 1])''',
            ),
            dict(
                name="Square-root decomposition",
                time="O(1) update, O(&radic;n) query",
                space="O(&radic;n)",
                why=[
                    "Cut the array into blocks of size about &radic;n and keep each block's sum. An update fixes one element and one block sum. A query adds whole blocks in the middle and single elements at the two ragged ends: at most 2&radic;n + &radic;n steps.",
                    "Worth knowing as the stepping stone: it is the same idea as a segment tree with only one level of blocks.",
                ],
                code='''class NumArray:
    def __init__(self, nums):
        self.nums = list(nums)
        self.size = max(1, int(len(nums) ** 0.5))
        self.blocks = [0] * (len(nums) // self.size + 1)
        for i, x in enumerate(nums):
            self.blocks[i // self.size] += x

    def update(self, index, val):
        self.blocks[index // self.size] += val - self.nums[index]
        self.nums[index] = val

    def sumRange(self, left, right):
        s, b = 0, self.size
        while left <= right and left % b:          # ragged start
            s += self.nums[left]; left += 1
        while left + b - 1 <= right:               # whole blocks
            s += self.blocks[left // b]; left += b
        while left <= right:                       # ragged end
            s += self.nums[left]; left += 1
        return s''',
            ),
            dict(
                name="Fenwick tree",
                time="O(log n) update and query",
                space="O(n)",
                best=True,
                why=[
                    "Store point <em>deltas</em>: an update adds <code>val - nums[i]</code> at position <code>i</code>. A range sum is the difference of two prefix sums.",
                    "Building by calling <code>add</code> n times is O(n log n). The loop below is the O(n) build: each index pushes its total up to its parent block <code>i + (i &amp; -i)</code> once.",
                ],
                code='''class NumArray:
    def __init__(self, nums):
        self.n = len(nums)
        self.nums = list(nums)
        self.tree = [0] + list(nums)               # 1-indexed
        for i in range(1, self.n + 1):             # O(n) build
            parent = i + (i & -i)
            if parent <= self.n:
                self.tree[parent] += self.tree[i]

    def _prefix(self, i):                          # sum of nums[0:i]
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & -i                            # drop the lowest set bit
        return s

    def update(self, index, val):
        delta, self.nums[index] = val - self.nums[index], val
        i = index + 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i                            # next block covering index

    def sumRange(self, left, right):
        return self._prefix(right + 1) - self._prefix(left)''',
            ),
            dict(
                name="Segment tree (iterative, bottom-up)",
                time="O(log n) update and query",
                space="O(n)",
                why=[
                    "Leaves live at <code>tree[n..2n-1]</code>; node <code>i</code> is the sum of children <code>2i</code> and <code>2i+1</code>. An update rewrites a leaf and walks up, recomputing parents.",
                    "A query walks two pointers up from both ends of the half-open range <code>[l, r)</code>. When the left pointer is a right child its node is entirely inside the range, so take it and step past; symmetrically on the right.",
                    "More code than the Fenwick tree, but swap <code>+</code> for <code>min</code> or <code>max</code> and it still works &mdash; the Fenwick tree does not.",
                ],
                code='''class NumArray:
    def __init__(self, nums):
        self.n = n = len(nums)
        self.tree = [0] * n + list(nums)
        for i in range(n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index, val):
        i = index + self.n
        self.tree[i] = val
        while i > 1:
            i //= 2
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def sumRange(self, left, right):
        s, l, r = 0, left + self.n, right + self.n + 1
        while l < r:
            if l & 1:                  # l is a right child: take it, move right
                s += self.tree[l]; l += 1
            if r & 1:                  # r-1 is a left child's sibling: take it
                r -= 1; s += self.tree[r]
            l //= 2; r //= 2
        return s''',
            ),
        ],
        tests='''a = NumArray([1, 3, 5])
assert a.sumRange(0, 2) == 9
a.update(1, 2)
assert a.sumRange(0, 2) == 8

rng = random.Random(7)
for _ in range(60):
    nums = [rng.randint(-100, 100) for _ in range(rng.randint(1, 40))]
    obj, ref = NumArray(nums), list(nums)
    for _ in range(60):
        if rng.random() < 0.5:
            i, v = rng.randrange(len(ref)), rng.randint(-100, 100)
            obj.update(i, v); ref[i] = v
        else:
            l = rng.randrange(len(ref)); r = rng.randrange(l, len(ref))
            assert obj.sumRange(l, r) == sum(ref[l:r + 1])''',
        pitfall="Fenwick indices are 1-based. Calling the update loop with <code>i = 0</code> never terminates, because <code>0 &amp; -0</code> is 0 and the index never moves.",
    ),

    # ------------------------------------------------------------------ 315
    dict(
        id="count-of-smaller-numbers-after-self",
        lc=315, slug="count-of-smaller-numbers-after-self",
        name="Count of Smaller Numbers After Self",
        difficulty="hard",
        framing=[
            "For each element, count the elements to its right that are smaller. The direct answer is O(n&sup2;). The insight is to scan from the right and keep the values seen so far in a structure that answers \"how many are below x?\" quickly.",
            "A Fenwick tree indexed by <em>value rank</em> does exactly that: inserting a value adds 1 at its rank, and the count below x is a prefix sum. Values can be large or negative, so compress them to ranks 1..k first.",
        ],
        approaches=[
            dict(
                name="Compare every pair",
                time="O(n&sup2;)",
                space="O(1)",
                why=[
                    "For each <code>i</code>, scan everything to its right. Times out at n = 10<sup>5</sup>.",
                ],
                code='''def count_smaller(nums):
    return [sum(1 for y in nums[i + 1:] if y < x) for i, x in enumerate(nums)]''',
            ),
            dict(
                name="Sorted list + bisect",
                time="O(n&sup2;) worst case, fast in practice",
                space="O(n)",
                why=[
                    "Scan right to left, keep a sorted list of seen values, and <code>bisect_left</code> gives the count below x. The search is O(log n) but <code>insort</code> shifts elements, so each insert is O(n).",
                    "In CPython that shift is a fast <code>memmove</code>, so this often passes. Say why it is not O(n log n) if you use it.",
                ],
                code='''def count_smaller(nums):
    seen, out = [], []
    for x in reversed(nums):
        out.append(bisect.bisect_left(seen, x))
        bisect.insort(seen, x)
    return out[::-1]''',
            ),
            dict(
                name="Merge sort, counting right-to-left jumps",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Sort indices by value with merge sort. When an element from the left half is placed, every element from the right half already placed before it is smaller and was originally to its right. Add that count to its answer.",
                    "The same counting-during-merge idea solves inversion counts and Reverse Pairs below.",
                ],
                code='''def count_smaller(nums):
    res = [0] * len(nums)

    def sort(idx):
        if len(idx) <= 1:
            return idx
        mid = len(idx) // 2
        left, right = sort(idx[:mid]), sort(idx[mid:])
        merged, j = [], 0
        for i in left:
            while j < len(right) and nums[right[j]] < nums[i]:
                merged.append(right[j]); j += 1
            res[i] += j                 # right-half elements smaller than nums[i]
            merged.append(i)
        merged.extend(right[j:])
        return merged

    sort(list(range(len(nums))))
    return res''',
            ),
            dict(
                name="Fenwick tree over value ranks",
                time="O(n log n)",
                space="O(n)",
                best=True,
                why=[
                    "Compress values to ranks 1..k. Scan right to left: the answer for x is the prefix count of ranks below rank(x); then add 1 at rank(x).",
                    "Every operation is O(log k), k &le; n. This is the reusable template: <strong>sort out the coordinates, then count with a BIT while you scan</strong>.",
                ],
                code='''def count_smaller(nums):
    rank = {v: i + 1 for i, v in enumerate(sorted(set(nums)))}
    tree = [0] * (len(rank) + 1)

    def add(i):
        while i < len(tree):
            tree[i] += 1
            i += i & -i

    def prefix(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    out = []
    for x in reversed(nums):
        out.append(prefix(rank[x] - 1))    # seen values strictly smaller
        add(rank[x])
    return out[::-1]''',
            ),
        ],
        tests='''assert count_smaller([5, 2, 6, 1]) == [2, 1, 1, 0]
assert count_smaller([-1]) == [0]
assert count_smaller([-1, -1]) == [0, 0]

def brute(a):
    return [sum(1 for y in a[i + 1:] if y < x) for i, x in enumerate(a)]

rng = random.Random(3)
for _ in range(200):
    a = [rng.randint(-20, 20) for _ in range(rng.randint(1, 40))]
    assert count_smaller(a) == brute(a)''',
    ),

    # ------------------------------------------------------------------ 1649
    dict(
        id="create-sorted-array-through-instructions",
        lc=1649, slug="create-sorted-array-through-instructions",
        name="Create Sorted Array through Instructions",
        difficulty="hard",
        framing=[
            "Insert values one by one; each insertion costs <code>min(#strictly smaller, #strictly greater)</code> among values already inserted. It is the previous problem scanned in the other direction, with two prefix-count queries per step.",
            "Values are bounded (&le; 10<sup>5</sup>), so the Fenwick tree can be indexed by value directly with no compression.",
        ],
        approaches=[
            dict(
                name="Sorted list + bisect",
                time="O(n&sup2;) worst case",
                space="O(n)",
                why=[
                    "<code>bisect_left</code> gives the count of smaller values, <code>len - bisect_right</code> the count of greater. Insertion shifts, so the worst case is quadratic.",
                ],
                code='''def create_sorted_array(instructions):
    seen, cost = [], 0
    for x in instructions:
        less = bisect.bisect_left(seen, x)
        greater = len(seen) - bisect.bisect_right(seen, x)
        cost += min(less, greater)
        bisect.insort(seen, x)
    return cost % (10**9 + 7)''',
            ),
            dict(
                name="Fenwick tree over values",
                time="O(n log m)",
                space="O(m)",
                best=True,
                why=[
                    "<code>m</code> is the largest value. Strictly smaller is <code>prefix(x - 1)</code>; strictly greater is <code>i - prefix(x)</code>, where <code>i</code> is how many values are already inserted.",
                    "Two queries and one update per value, each O(log m).",
                ],
                code='''def create_sorted_array(instructions):
    m = max(instructions)
    tree = [0] * (m + 1)

    def add(i):
        while i <= m:
            tree[i] += 1
            i += i & -i

    def prefix(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    cost = 0
    for i, x in enumerate(instructions):
        cost += min(prefix(x - 1), i - prefix(x))
        add(x)
    return cost % (10**9 + 7)''',
            ),
        ],
        tests='''assert create_sorted_array([1, 5, 6, 2]) == 1
assert create_sorted_array([1, 2, 3, 6, 5, 4]) == 3
assert create_sorted_array([1, 3, 3, 3, 2, 4, 2, 1, 2]) == 4

def brute(a):
    cost = 0
    for i, x in enumerate(a):
        cost += min(sum(y < x for y in a[:i]), sum(y > x for y in a[:i]))
    return cost

rng = random.Random(5)
for _ in range(150):
    a = [rng.randint(1, 15) for _ in range(rng.randint(1, 40))]
    assert create_sorted_array(a) == brute(a)''',
    ),
    ],
),

dict(
    id="segment-tree",
    title="Counting pairs and segment trees",
    idea=[
        "A <strong>segment tree</strong> stores an aggregate (sum, min, max, gcd&hellip;) for every node of a balanced binary split of the index range. Any range <code>[l, r]</code> decomposes into O(log n) nodes, so a query combines O(log n) stored answers, and a point update fixes the O(log n) nodes on one root-to-leaf path.",
        "The pair-counting problems below all have the shape \"count <code>i &lt; j</code> with some inequality between <code>a[i]</code> and <code>a[j]</code>\". Scan <code>j</code> left to right and ask a tree how many earlier values satisfy the inequality: a range-count over <em>values</em>. Merge sort solves the same problems by counting across halves while merging.",
        "When values matter rather than positions, the tree is indexed by value rank. Compress first with <code>sorted(set(...))</code> and <code>bisect</code>.",
    ],
    problems=[

    # ------------------------------------------------------------------ 493
    dict(
        id="reverse-pairs",
        lc=493, slug="reverse-pairs",
        name="Reverse Pairs",
        difficulty="hard",
        framing=[
            "Count pairs <code>i &lt; j</code> with <code>nums[i] &gt; 2 &middot; nums[j]</code>. Like inversion counting, except the comparison used to count differs from the one used to sort, so counting and merging have to be separate passes.",
        ],
        approaches=[
            dict(
                name="Every pair",
                time="O(n&sup2;)",
                space="O(1)",
                why=["The definition, checked directly."],
                code='''def reverse_pairs(nums):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] > 2 * nums[j])''',
            ),
            dict(
                name="Merge sort with a separate counting pass",
                time="O(n log n)",
                space="O(n)",
                best=True,
                why=[
                    "Both halves are sorted after the recursive calls. For each <code>x</code> in the left half, the right-half values with <code>x &gt; 2y</code> form a prefix of the right half, and that prefix only grows as <code>x</code> grows: a two-pointer sweep counts them in O(n).",
                    "Then merge normally. <code>sorted(left + right)</code> is used for brevity; Timsort spots the two sorted runs and merges them in linear time.",
                ],
                code='''def reverse_pairs(nums):
    def sort(a):
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, cl = sort(a[:mid])
        right, cr = sort(a[mid:])
        count, j = cl + cr, 0
        for x in left:
            while j < len(right) and x > 2 * right[j]:
                j += 1
            count += j
        return sorted(left + right), count

    return sort(nums)[1]''',
            ),
            dict(
                name="Fenwick tree over compressed values",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Scan <code>j</code> left to right. Count earlier values strictly greater than <code>2 &middot; nums[j]</code>: that is <code>inserted - prefix(rank of 2&middot;nums[j])</code>. Then insert <code>nums[j]</code>.",
                    "Compress only the values that get inserted; <code>bisect_right</code> on that sorted list finds how many of them are &le; 2&middot;nums[j] without needing 2&middot;nums[j] in the table.",
                ],
                code='''def reverse_pairs(nums):
    vals = sorted(set(nums))
    tree = [0] * (len(vals) + 1)

    def add(i):
        while i < len(tree):
            tree[i] += 1
            i += i & -i

    def prefix(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    count = 0
    for seen, y in enumerate(nums):
        at_most = bisect.bisect_right(vals, 2 * y)   # ranks with value <= 2y
        count += seen - prefix(at_most)
        add(bisect.bisect_left(vals, y) + 1)
    return count''',
            ),
        ],
        tests='''assert reverse_pairs([1, 3, 2, 3, 1]) == 2
assert reverse_pairs([2, 4, 3, 5, 1]) == 3
assert reverse_pairs([]) == 0
assert reverse_pairs([2147483647] * 5) == 0
assert reverse_pairs([-5, -5]) == 1

def brute(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > 2 * a[j])

rng = random.Random(11)
for _ in range(200):
    a = [rng.randint(-30, 30) for _ in range(rng.randint(0, 40))]
    assert reverse_pairs(a) == brute(a)''',
        pitfall="Negative numbers: <code>-5 &gt; 2 &middot; -5</code> is true. Do not \"optimise\" with <code>x // 2</code> comparisons, which round the wrong way for negatives.",
    ),

    # ------------------------------------------------------------------ 327
    dict(
        id="count-of-range-sum",
        lc=327, slug="count-of-range-sum",
        name="Count of Range Sum",
        difficulty="hard",
        framing=[
            "Count subarrays whose sum lies in <code>[lower, upper]</code>. With prefix sums <code>P</code>, a subarray <code>(i, j]</code> qualifies when <code>lower &le; P[j] - P[i] &le; upper</code>, i.e. <code>P[j] - upper &le; P[i] &le; P[j] - lower</code>.",
            "So for each <code>j</code>, count earlier prefix sums inside a window of values. That is a range-count query over values, and a Fenwick tree over compressed prefix sums answers it.",
        ],
        approaches=[
            dict(
                name="Every subarray via prefix sums",
                time="O(n&sup2;)",
                space="O(n)",
                why=["Prefix sums make each subarray sum O(1), but there are n&sup2;/2 subarrays."],
                code='''def count_range_sum(nums, lower, upper):
    P = [0] + list(accumulate(nums))
    return sum(1 for j in range(1, len(P)) for i in range(j)
               if lower <= P[j] - P[i] <= upper)''',
            ),
            dict(
                name="Fenwick tree over prefix sums",
                time="O(n log n)",
                space="O(n)",
                best=True,
                why=[
                    "Compress all prefix sums. Before handling <code>P[j]</code>, the tree holds <code>P[0..j-1]</code>. The count with value in <code>[P[j]-upper, P[j]-lower]</code> is two <code>bisect</code>s into the compressed list and two prefix queries.",
                    "Insert <code>P[0] = 0</code> first, so subarrays starting at index 0 are counted.",
                ],
                code='''def count_range_sum(nums, lower, upper):
    P = [0] + list(accumulate(nums))
    vals = sorted(set(P))
    tree = [0] * (len(vals) + 1)

    def add(i):
        while i < len(tree):
            tree[i] += 1
            i += i & -i

    def prefix(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    count = 0
    for p in P:
        lo = bisect.bisect_left(vals, p - upper)       # ranks before the window
        hi = bisect.bisect_right(vals, p - lower)      # ranks up to window end
        count += prefix(hi) - prefix(lo)
        add(bisect.bisect_left(vals, p) + 1)
    return count''',
            ),
            dict(
                name="Merge sort on prefix sums",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Sort the prefix sums with merge sort. For each <code>P[i]</code> in the left half, the right-half values within <code>[P[i]+lower, P[i]+upper]</code> form a contiguous run, and its two ends only move right as <code>P[i]</code> grows.",
                ],
                code='''def count_range_sum(nums, lower, upper):
    def sort(a):
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, cl = sort(a[:mid])
        right, cr = sort(a[mid:])
        count, lo, hi = cl + cr, 0, 0
        for x in left:
            while lo < len(right) and right[lo] - x < lower:
                lo += 1
            while hi < len(right) and right[hi] - x <= upper:
                hi += 1
            count += hi - lo
        return sorted(left + right), count

    return sort([0] + list(accumulate(nums)))[1]''',
            ),
        ],
        tests='''assert count_range_sum([-2, 5, -1], -2, 2) == 3
assert count_range_sum([0], 0, 0) == 1

def brute(a, lo, hi):
    return sum(1 for i in range(len(a)) for j in range(i, len(a)) if lo <= sum(a[i:j + 1]) <= hi)

rng = random.Random(13)
for _ in range(200):
    a = [rng.randint(-10, 10) for _ in range(rng.randint(1, 25))]
    lo = rng.randint(-15, 10); hi = lo + rng.randint(0, 15)
    assert count_range_sum(a, lo, hi) == brute(a, lo, hi)''',
    ),

    # ------------------------------------------------------------------ 2407
    dict(
        id="longest-increasing-subsequence-ii",
        lc=2407, slug="longest-increasing-subsequence-ii",
        name="Longest Increasing Subsequence II",
        difficulty="hard",
        framing=[
            "Longest strictly increasing subsequence where adjacent elements differ by at most <code>k</code>. The DP is easy: <code>best[v]</code> = longest valid subsequence ending in value <code>v</code>, and <code>best[x] = 1 + max(best[x-k .. x-1])</code>.",
            "The bottleneck is that range <em>max</em>. A Fenwick tree cannot do range max (max has no inverse), so this is the problem that needs a real segment tree.",
        ],
        approaches=[
            dict(
                name="DP with a scan over the value window",
                time="O(n&middot;k)",
                space="O(m)",
                why=[
                    "<code>m</code> is the largest value. For each <code>x</code>, scan the k values below it. Correct, but k and n are both up to 10<sup>5</sup>.",
                ],
                code='''def length_of_lis(nums, k):
    best = [0] * (max(nums) + 1)
    for x in nums:
        lo = max(0, x - k)
        best[x] = 1 + max(best[lo:x], default=0)
    return max(best)''',
            ),
            dict(
                name="Segment tree for range max",
                time="O(n log m)",
                space="O(m)",
                best=True,
                why=[
                    "Index the tree by value. For each <code>x</code>, query the max over values <code>[x-k, x-1]</code>, then set position <code>x</code> to that plus one.",
                    "The iterative bottom-up tree from Range Sum Query - Mutable works unchanged with <code>max</code> in place of <code>+</code>. Since best[x] only ever grows, the update can take the max with the old leaf.",
                ],
                code='''def length_of_lis(nums, k):
    size = max(nums) + 1
    tree = [0] * (2 * size)

    def update(i, val):
        i += size
        tree[i] = max(tree[i], val)
        while i > 1:
            i //= 2
            tree[i] = max(tree[2 * i], tree[2 * i + 1])

    def query(l, r):                       # max over [l, r)
        res, l, r = 0, l + size, r + size
        while l < r:
            if l & 1:
                res = max(res, tree[l]); l += 1
            if r & 1:
                r -= 1; res = max(res, tree[r])
            l //= 2; r //= 2
        return res

    for x in nums:
        update(x, query(max(0, x - k), x) + 1)
    return tree[1]''',
            ),
        ],
        tests='''assert length_of_lis([4, 2, 1, 4, 3, 4, 5, 8, 15], 3) == 5
assert length_of_lis([7, 4, 5, 1, 8, 12, 4, 7], 5) == 4
assert length_of_lis([1, 5], 1) == 1

def brute(a, k):
    best = [1] * len(a)
    for j in range(len(a)):
        for i in range(j):
            if a[i] < a[j] <= a[i] + k:
                best[j] = max(best[j], best[i] + 1)
    return max(best)

rng = random.Random(17)
for _ in range(200):
    a = [rng.randint(1, 30) for _ in range(rng.randint(1, 30))]
    k = rng.randint(1, 8)
    assert length_of_lis(a, k) == brute(a, k)''',
    ),

    # ------------------------------------------------------------------ 699
    dict(
        id="falling-squares",
        lc=699, slug="falling-squares",
        name="Falling Squares",
        difficulty="hard",
        framing=[
            "Squares drop onto a line and stack. After each drop, report the tallest stack. Each drop is a <em>range update</em>: set every position in <code>[left, left + side)</code> to <code>max height there + side</code>. Range assignment plus range max is the textbook use of a segment tree with <strong>lazy propagation</strong>.",
            "Coordinates go up to 10<sup>8</sup>, so compress the interval endpoints first: only the 2n endpoints can change what the skyline looks like.",
        ],
        approaches=[
            dict(
                name="Compare against every earlier square",
                time="O(n&sup2;)",
                space="O(n)",
                why=[
                    "A new square lands on the tallest earlier square that overlaps it. Keep each square's final top and check all previous ones. With n &le; 1000 this is accepted, and it is the version to write first.",
                ],
                code='''def falling_squares(positions):
    tops, out, best = [], [], 0
    for i, (left, side) in enumerate(positions):
        right, base = left + side, 0
        for j, (l2, s2) in enumerate(positions[:i]):
            if l2 < right and left < l2 + s2:          # half-open overlap
                base = max(base, tops[j])
        tops.append(base + side)
        best = max(best, base + side)
        out.append(best)
    return out''',
            ),
            dict(
                name="Lazy segment tree over compressed coordinates",
                time="O(n log n)",
                space="O(n)",
                best=True,
                why=[
                    "Compress the endpoints to indices; a square covers the half-open index range <code>[idx(left), idx(left + side))</code>.",
                    "Each node keeps the max of its range and a pending \"assign\" tag. A range assignment that fully covers a node just sets its max and tag and stops; the tag is pushed to the children only when a later operation needs to go below that node. That is what keeps range updates at O(log n).",
                    "Assignment (not max-with) is correct here because the new height is higher than everything currently in the range.",
                ],
                code='''def falling_squares(positions):
    coords = sorted({p for l, s in positions for p in (l, l + s)})
    idx = {c: i for i, c in enumerate(coords)}
    n = len(coords)
    mx, lazy = [0] * (4 * n), [None] * (4 * n)

    def push(node):
        if lazy[node] is not None:
            for ch in (2 * node, 2 * node + 1):
                mx[ch] = lazy[ch] = lazy[node]
            lazy[node] = None

    def query(node, lo, hi, l, r):                 # max over [l, r)
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return mx[node]
        push(node)
        mid = (lo + hi) // 2
        return max(query(2 * node, lo, mid, l, r), query(2 * node + 1, mid, hi, l, r))

    def assign(node, lo, hi, l, r, val):           # set [l, r) to val
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            mx[node] = lazy[node] = val
            return
        push(node)
        mid = (lo + hi) // 2
        assign(2 * node, lo, mid, l, r, val)
        assign(2 * node + 1, mid, hi, l, r, val)
        mx[node] = max(mx[2 * node], mx[2 * node + 1])

    out = []
    for left, side in positions:
        l, r = idx[left], idx[left + side]
        top = query(1, 0, n, l, r) + side
        assign(1, 0, n, l, r, top)
        out.append(mx[1])
    return out''',
            ),
        ],
        tests='''assert falling_squares([[1, 2], [2, 3], [6, 1]]) == [2, 5, 5]
assert falling_squares([[100, 100], [200, 100]]) == [100, 100]
assert falling_squares([[1, 5], [2, 2], [7, 5]]) == [5, 7, 7]

def brute(pos):
    height, out = {}, []
    for l, s in pos:
        base = max((height.get(x, 0) for x in range(l, l + s)), default=0)
        for x in range(l, l + s):
            height[x] = base + s
        out.append(max(height.values()))
    return out

rng = random.Random(19)
for _ in range(200):
    pos = [[rng.randint(1, 20), rng.randint(1, 6)] for _ in range(rng.randint(1, 15))]
    assert falling_squares(pos) == brute(pos)''',
        pitfall="Squares that only touch at an edge do not stack: <code>[1, 2]</code> covers <code>[1, 3)</code> and <code>[3, 1]</code> covers <code>[3, 4)</code>. Half-open ranges make that fall out naturally.",
    ),
    ],
),
    ],
)
