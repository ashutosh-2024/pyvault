# -*- coding: utf-8 -*-
"""Heap / priority-queue topic for the DSA path.

Same contract as content/dsa.py: every `code` block is executed by build.py
with PRELUDE + this topic's `prelude` + the problem's `tests` appended.

Problems with a `slug` get their statement, examples, constraints and tags
from content/leetcode.json. Premium and non-LeetCode entries supply their own.
"""

PRELUDE_HEAP = '''import heapq
from collections import Counter, deque


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    head = tail = None
    for v in values:
        node = ListNode(v)
        if head is None:
            head = tail = node
        else:
            tail.next = node
            tail = node
    return head


def list_vals(head):
    out = []
    while head is not None:
        out.append(head.val)
        head = head.next
    return out
'''


HEAP_TOPIC = dict(
    id="heap",
    title="Heaps and Priority Queues",
    prelude=PRELUDE_HEAP,
    sections=[

    # ---------------------------------------------------------------- 1
    dict(
        id="foundations",
        title="Foundations",
        problems=[

        dict(
            id="heapify",
            name="Heapify: Building a Heap in O(n)",
            difficulty="easy",
            tags=["Heap (Priority Queue)", "Array", "Fundamentals"],
            statement=[
                "Turn an arbitrary array into a binary heap in place, so that every parent is &le; both of its children.",
                "The interesting part is not the code &mdash; Python gives you <code>heapq.heapify</code> in one line &mdash; but the cost. Inserting n items one at a time costs O(n log n). Heapifying an existing array costs <strong>O(n)</strong>. Being able to explain why is a standard follow-up.",
                "A heap is stored as a flat array with the tree structure implied by indices: the children of <code>i</code> live at <code>2i+1</code> and <code>2i+2</code>, and the parent of <code>i</code> is at <code>(i-1)//2</code>. Nothing is allocated for pointers.",
            ],
            examples=[
                dict(input="nums = [5, 3, 8, 1, 9, 2]",
                     output="[1, 3, 2, 5, 9, 8]",
                     explanation="One valid heap array. Only the heap property matters, not a unique ordering."),
            ],
            constraints=[
                "<code>0 &lt;= len(nums) &lt;= 10<sup>6</sup></code>",
                "In place: O(1) extra space",
            ],
            approaches=[
                dict(
                    name="Sift down from the last parent",
                    time="O(n)",
                    space="O(1)",
                    best=True,
                    why=[
                        "Walk backwards from the last node that has a child, at index <code>n//2 - 1</code>, and sift each one down. Everything from <code>n//2</code> onwards is a leaf and is already a valid one-element heap, so half the array needs no work at all.",
                        "The O(n) bound is the part to be able to derive. A node at height <code>k</code> above the leaves costs O(k) to sift down, and there are at most <code>n/2<sup>k+1</sup></code> such nodes. Summing, the total is n &times; &Sigma; k/2<sup>k+1</sup>, and that series converges to 1 &mdash; so the whole build is O(n), not O(n log n).",
                        "The intuition behind the algebra: almost every node is near the bottom and moves almost nowhere. Only the root can travel the full log n.",
                        "Sifting <em>up</em> from the front instead gives O(n log n), because then the expensive nodes are the many leaves rather than the single root. The direction is the whole trick.",
                    ],
                    code='''def heapify(nums):
    n = len(nums)
    for i in range(n // 2 - 1, -1, -1):   # last parent down to the root
        sift_down(nums, i, n)
    return nums


def sift_down(nums, i, n):
    while True:
        smallest = i
        left, right = 2 * i + 1, 2 * i + 2
        if left < n and nums[left] < nums[smallest]:
            smallest = left
        if right < n and nums[right] < nums[smallest]:
            smallest = right
        if smallest == i:
            return
        nums[i], nums[smallest] = nums[smallest], nums[i]
        i = smallest''',
                ),
                dict(
                    name="Push one at a time",
                    time="O(n log n)",
                    space="O(n)",
                    tag="the slower way",
                    why=[
                        "Insert each element into a growing heap. Every insert sifts up through at most log n levels, so n inserts cost O(n log n).",
                        "This is what <code>heapq.heappush</code> in a loop does. It is the obvious approach and it is asymptotically worse than <code>heapify</code> on data you already have in an array &mdash; measurably so at a million elements.",
                        "It is still the right choice when items <em>arrive</em> one at a time, because then there is no array to heapify.",
                    ],
                    code='''def heapify(nums):
    out = []
    for value in nums:
        heapq.heappush(out, value)
    nums[:] = out
    return nums''',
                ),
            ],
            tests='''import random


def valid(h):
    return all(h[i] <= h[c]
               for i in range(len(h))
               for c in (2 * i + 1, 2 * i + 2) if c < len(h))


a = [5, 3, 8, 1, 9, 2]
heapify(a)
assert valid(a) and sorted(a) == [1, 2, 3, 5, 8, 9]
assert heapify([]) == []
assert heapify([1]) == [1]
random.seed(0)
for _ in range(50):
    data = [random.randint(-50, 50) for _ in range(random.randint(0, 30))]
    original = sorted(data)
    heapify(data)
    assert valid(data), data
    assert sorted(data) == original''',
            pitfall="Starting the loop at index 0 and sifting down. You must go bottom-up; top-down sift-down does not produce a heap.",
        ),
        ],
    ),

    # ---------------------------------------------------------------- 2
    dict(
        id="top-k",
        title="Top k with a bounded heap",
        problems=[

        dict(
            id="kth-largest-element",
            lc=215, slug="kth-largest-element-in-an-array",
            name="Kth Largest Element in an Array",
            difficulty="medium",
            approaches=[
                dict(
                    name="Min-heap of size k",
                    time="O(n log k)",
                    space="O(k)",
                    best=True,
                    why=[
                        "Keep a min-heap holding the k largest values seen so far. Its root is the smallest of those k, which is exactly the k-th largest overall &mdash; so once every element has been offered, the root is the answer.",
                        "Push, then pop when the heap exceeds k. Each operation is O(log k) and there are n of them: <strong>O(n log k)</strong>, which beats sorting's O(n log n) whenever k is small, and uses only O(k) memory rather than holding the whole array.",
                        "The counter-intuitive part is using a <em>min</em>-heap to find a maximum. The reason is that you need cheap access to the weakest member of your current top-k, because that is the one to evict.",
                    ],
                    code='''def find_kth_largest(nums, k):
    heap = []
    for value in nums:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)      # drop the smallest of the k+1
    return heap[0]''',
                ),
                dict(
                    name="nlargest / sorting",
                    time="O(n log n)",
                    space="O(n)",
                    tag="one line",
                    why=[
                        "<code>sorted(nums)[-k]</code> is the shortest correct answer and is fine when n is small. <code>heapq.nlargest(k, nums)[-1]</code> is the same size-k heap idea behind a library call.",
                        "Sorting does strictly more work than the problem needs: it orders all n elements when you only care about a boundary.",
                    ],
                    code='''def find_kth_largest(nums, k):
    return heapq.nlargest(k, nums)[-1]''',
                ),
                dict(
                    name="Quickselect",
                    time="O(n) average, O(n&sup2;) worst",
                    space="O(1)",
                    tag="best average case",
                    why=[
                        "Partition around a pivot as in quicksort, but recurse into only the side that contains the k-th position. Each pass discards a fraction of the array, so the expected work is n + n/2 + n/4 + &hellip; = <strong>O(n)</strong>.",
                        "The worst case is O(n&sup2;), when every pivot is the extreme value &mdash; already-sorted input with a fixed pivot choice does it. A <em>random</em> pivot makes that vanishingly unlikely, which is why the shuffle matters and is not decoration.",
                        "Mention this when asked to beat O(n log k). It is the theoretically best answer and the one most likely to be got subtly wrong under time pressure, so write the heap first.",
                    ],
                    code='''def find_kth_largest(nums, k):
    import random
    target = len(nums) - k          # k-th largest = this index when sorted
    lo, hi = 0, len(nums) - 1
    nums = list(nums)
    while True:
        pivot = random.randint(lo, hi)
        nums[pivot], nums[hi] = nums[hi], nums[pivot]
        store = lo
        for i in range(lo, hi):
            if nums[i] < nums[hi]:
                nums[store], nums[i] = nums[i], nums[store]
                store += 1
        nums[store], nums[hi] = nums[hi], nums[store]
        if store == target:
            return nums[store]
        if store < target:
            lo = store + 1
        else:
            hi = store - 1''',
                ),
            ],
            tests='''assert find_kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
assert find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
assert find_kth_largest([1], 1) == 1
assert find_kth_largest([2, 1], 2) == 1
assert find_kth_largest([7, 7, 7], 2) == 7
import random
random.seed(1)
for _ in range(50):
    data = [random.randint(-20, 20) for _ in range(random.randint(1, 40))]
    k = random.randint(1, len(data))
    assert find_kth_largest(list(data), k) == sorted(data)[-k]''',
            pitfall="Returning the k-th <em>distinct</em> value. Duplicates count: in [3,2,3,1,2,4,5,5,6] the 4th largest is 4, not 3.",
        ),

        dict(
            id="kth-largest-in-stream",
            lc=703, slug="kth-largest-element-in-a-stream",
            name="Kth Largest Element in a Stream",
            difficulty="easy",
            approaches=[
                dict(
                    name="Min-heap capped at k",
                    time="O(log k) per add",
                    space="O(k)",
                    best=True,
                    why=[
                        "The same size-k min-heap as problem 215, kept alive between calls. This is the problem that shows <em>why</em> that structure is the right one: it is incremental. Nothing is recomputed when a value arrives.",
                        "<code>add</code> pushes and then pops if the heap is over k, both O(log k), and returns the root. Construction heapifies the initial array and trims it, which is O(n) plus O((n-k) log k).",
                        "Space stays O(k) no matter how long the stream runs &mdash; the whole point. Keeping every value and sorting on each query would be O(n) memory and O(n log n) per call.",
                    ],
                    code='''class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = list(nums)
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]''',
                ),
                dict(
                    name="Sorted list with bisect",
                    time="O(n) per add",
                    space="O(n)",
                    why=[
                        "Keep every value in a sorted list and answer with <code>data[-k]</code>. <code>bisect.insort</code> finds the position in O(log n) but the insert itself shifts the tail, so each add is O(n).",
                        "Worth knowing as the contrast: the binary search is not the cost, the memory move is. For a stream this also grows without bound, where the heap does not.",
                    ],
                    code='''import bisect


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.data = sorted(nums)

    def add(self, val):
        bisect.insort(self.data, val)
        return self.data[-self.k]''',
                ),
            ],
            tests='''kth = KthLargest(3, [4, 5, 8, 2])
assert [kth.add(v) for v in (3, 5, 10, 9, 4)] == [4, 5, 5, 8, 8]
solo = KthLargest(1, [])
assert [solo.add(v) for v in (-3, -2, -4, 0, 4)] == [-3, -2, -2, 0, 4]
start = KthLargest(2, [0])
assert start.add(-1) == -1        # 2nd largest of [0, -1]
assert start.add(7) == 0          # 2nd largest of [0, -1, 7]''',
        ),

        dict(
            id="top-k-frequent",
            lc=347, slug="top-k-frequent-elements",
            name="Top K Frequent Elements",
            difficulty="medium",
            approaches=[
                dict(
                    name="Count, then a size-k heap",
                    time="O(n log k)",
                    space="O(n)",
                    why=[
                        "Count with a <code>Counter</code> in O(n), then run the size-k min-heap over the <em>distinct</em> values, keyed on frequency. If there are d distinct values the heap phase is O(d log k), and d &le; n.",
                        "Space is O(n) for the counter regardless of approach &mdash; you cannot know frequencies without counting everything. The heap adds only O(k).",
                        "<code>Counter.most_common(k)</code> is this same algorithm in the standard library; it uses <code>heapq.nlargest</code> internally when k is given.",
                    ],
                    code='''def top_k_frequent(nums, k):
    counts = Counter(nums)
    heap = []
    for value, freq in counts.items():
        heapq.heappush(heap, (freq, value))
        if len(heap) > k:
            heapq.heappop(heap)
    return [value for freq, value in heap]''',
                ),
                dict(
                    name="Bucket by frequency",
                    time="O(n)",
                    space="O(n)",
                    best=True,
                    tag="linear",
                    why=[
                        "A frequency cannot exceed n, so make <code>n + 1</code> buckets and put each value in the bucket matching its count. Walk the buckets from the back and take the first k values.",
                        "That is a counting sort on a bounded key, so it is <strong>O(n)</strong> with no log factor at all &mdash; strictly better than the heap here, and the answer the problem's \"better than O(n log n)\" hint is pointing at.",
                        "It works only because the sort key is an integer bounded by n. The heap does not need that and generalises to unbounded or non-integer keys, which is why both are worth knowing.",
                    ],
                    code='''def top_k_frequent(nums, k):
    counts = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, freq in counts.items():
        buckets[freq].append(value)

    out = []
    for freq in range(len(buckets) - 1, 0, -1):
        for value in buckets[freq]:
            out.append(value)
            if len(out) == k:
                return out
    return out''',
                ),
            ],
            tests='''assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
assert top_k_frequent([1], 1) == [1]
assert sorted(top_k_frequent([4, 4, 4, 5, 5, 6], 3)) == [4, 5, 6]
assert sorted(top_k_frequent([-1, -1, 2, 2, 3], 2)) == [-1, 2]
got = top_k_frequent([1, 2, 3, 1, 2, 1], 2)
assert sorted(got) == [1, 2] and len(got) == 2''',
        ),

        dict(
            id="sort-by-frequency",
            lc=451, slug="sort-characters-by-frequency",
            name="Sort Characters By Frequency",
            difficulty="medium",
            approaches=[
                dict(
                    name="Count, then max-heap",
                    time="O(n + d log d)",
                    space="O(n)",
                    why=[
                        "Count the characters, push <code>(-freq, char)</code> so Python's min-heap behaves as a max-heap, then pop repeatedly and emit each character <code>freq</code> times.",
                        "With d distinct characters the heap work is O(d log d); building the output is O(n). For ASCII input d &le; 128, so the heap term is effectively constant and the whole thing is O(n).",
                        "The negation trick is the thing to remember: <code>heapq</code> has no max-heap, and negating the key is the standard workaround. It only works on numeric keys &mdash; you cannot negate a string.",
                    ],
                    code='''def frequency_sort(s):
    counts = Counter(s)
    heap = [(-freq, ch) for ch, freq in counts.items()]
    heapq.heapify(heap)

    out = []
    while heap:
        freq, ch = heapq.heappop(heap)
        out.append(ch * -freq)
    return "".join(out)''',
                ),
                dict(
                    name="most_common",
                    time="O(n + d log d)",
                    space="O(n)",
                    best=True,
                    tag="what to write",
                    why=[
                        "<code>Counter.most_common()</code> with no argument sorts the items by count, which is the same O(d log d) with none of the negation bookkeeping.",
                        "Identical complexity, three lines shorter, and no chance of getting the sign wrong. Reach for the heap only when you need the top few rather than all of them, or when items keep arriving.",
                    ],
                    code='''def frequency_sort(s):
    return "".join(ch * freq for ch, freq in Counter(s).most_common())''',
                ),
            ],
            tests='''def same_shape(got, s):
    return Counter(got) == Counter(s) and "".join(
        sorted(got, key=lambda c: -Counter(s)[c])) is not None


out = frequency_sort("tree")
assert out in ("eert", "eetr") and Counter(out) == Counter("tree")
out = frequency_sort("cccaaa")
assert out in ("cccaaa", "aaaccc")
assert frequency_sort("Aabb") in ("bbAa", "bbaA")
assert frequency_sort("") == ""
assert frequency_sort("a") == "a"
counts = Counter(frequency_sort("mississippi"))
assert counts == Counter("mississippi")
run = frequency_sort("mississippi")
freqs = [Counter("mississippi")[c] for c in run]
assert freqs == sorted(freqs, reverse=True)''',
            pitfall="Sorting characters rather than grouping them. All copies of a character must be adjacent; only the groups are ordered by frequency.",
        ),
        ],
    ),

    # ---------------------------------------------------------------- 3
    dict(
        id="k-way-merge",
        title="k-way merge",
        problems=[

        dict(
            id="sort-nearly-sorted",
            name="Sort a Nearly Sorted (K-Sorted) Array",
            difficulty="medium",
            tags=["Heap (Priority Queue)", "Array", "Sorting"],
            statement=[
                "You are given an array where every element is at most <code>k</code> positions away from where it would be in sorted order. Sort it.",
                "This is a classic that is not on LeetCode but shows up in interviews and on GeeksforGeeks. It is the cleanest illustration of a <em>sliding</em> heap: the heap is never bigger than the disorder in the data.",
            ],
            examples=[
                dict(input="nums = [6, 5, 3, 2, 8, 10, 9], k = 3",
                     output="[2, 3, 5, 6, 8, 9, 10]"),
                dict(input="nums = [10, 9, 8, 7, 4, 70, 60, 50], k = 4",
                     output="[4, 7, 8, 9, 10, 50, 60, 70]"),
            ],
            constraints=[
                "<code>0 &lt;= k &lt; len(nums)</code>",
                "Every element is at most <code>k</code> positions from its sorted position",
            ],
            approaches=[
                dict(
                    name="Sliding min-heap of size k+1",
                    time="O(n log k)",
                    space="O(k)",
                    best=True,
                    why=[
                        "Hold the next <code>k + 1</code> elements in a min-heap. The smallest remaining value must be among them &mdash; it cannot be further than k positions away &mdash; so popping the root gives the next value in sorted order.",
                        "Each element is pushed once and popped once from a heap of size k+1, so <strong>O(n log k)</strong>. When k is small relative to n this beats a full O(n log n) sort, and it uses O(k) space instead of O(n).",
                        "The invariant is the whole proof: <em>after processing index i, the heap contains every candidate for output position i.</em> The k-sorted guarantee is what makes that true; without it the algorithm is simply wrong.",
                    ],
                    code='''def sort_k_sorted(nums, k):
    heap = nums[:k + 1]
    heapq.heapify(heap)

    out = []
    for i in range(k + 1, len(nums)):
        out.append(heapq.heappushpop(heap, nums[i]))
    while heap:
        out.append(heapq.heappop(heap))
    return out''',
                ),
                dict(
                    name="Just sort it",
                    time="O(n log n)",
                    space="O(n)",
                    tag="baseline",
                    why=[
                        "<code>sorted(nums)</code> ignores the k-sorted guarantee entirely and is correct. Timsort even exploits existing runs, so on nearly-sorted data it often runs close to linear in practice.",
                        "The heap version still wins on <em>space</em> &mdash; O(k) versus O(n) &mdash; which is the real argument when the array is a stream you cannot hold in memory.",
                    ],
                    code='''def sort_k_sorted(nums, k):
    return sorted(nums)''',
                ),
            ],
            tests='''assert sort_k_sorted([6, 5, 3, 2, 8, 10, 9], 3) == [2, 3, 5, 6, 8, 9, 10]
assert sort_k_sorted([10, 9, 8, 7, 4, 70, 60, 50], 4) == [4, 7, 8, 9, 10, 50, 60, 70]
assert sort_k_sorted([1], 0) == [1]
assert sort_k_sorted([2, 1], 1) == [1, 2]
import random
random.seed(3)
for _ in range(40):
    k = random.randint(0, 4)
    base = sorted(random.randint(0, 50) for _ in range(random.randint(1, 25)))
    # Shuffling disjoint blocks of k+1 keeps every element within k of its
    # sorted position, which is exactly the precondition the algorithm needs.
    data = []
    for start in range(0, len(base), k + 1):
        block = base[start:start + k + 1]
        random.shuffle(block)
        data.extend(block)
    assert sort_k_sorted(data, k) == base''',
            pitfall="Sizing the heap at k instead of k+1. An element k positions out of place needs k+1 candidates in view.",
        ),

        dict(
            id="merge-k-sorted-arrays",
            name="Merge k Sorted Arrays",
            difficulty="medium",
            tags=["Heap (Priority Queue)", "Array", "Merge Sort"],
            statement=[
                "Given <code>k</code> sorted arrays, merge them into one sorted array.",
                "The array form of the next problem. Worth doing first because the pointer bookkeeping is visible &mdash; you push <code>(value, which array, which index)</code> and advance one cursor at a time.",
            ],
            examples=[
                dict(input="arrays = [[1, 4, 5], [1, 3, 4], [2, 6]]",
                     output="[1, 1, 2, 3, 4, 4, 5, 6]"),
            ],
            constraints=[
                "<code>0 &lt;= k</code>, each array sorted ascending",
                "Let <code>N</code> be the total number of elements across all arrays",
            ],
            approaches=[
                dict(
                    name="Min-heap of one cursor per array",
                    time="O(N log k)",
                    space="O(k)",
                    best=True,
                    why=[
                        "Seed the heap with the first element of each array. Pop the global minimum, emit it, and push the next element from whichever array it came from. The heap holds at most one entry per array, so its size is k.",
                        "Every one of the N elements is pushed and popped exactly once at O(log k), giving <strong>O(N log k)</strong>. Concatenating and sorting is O(N log N), and since k &le; N this is never worse and is much better when k is small.",
                        "The tuple carries the array index so you know which cursor to advance; the element index says where. Tie-breaking on those integers is harmless because they are unique.",
                        "<code>heapq.merge</code> does exactly this and returns a lazy iterator, which is the version to use in real code.",
                    ],
                    code='''def merge_k_arrays(arrays):
    heap = [(a[0], i, 0) for i, a in enumerate(arrays) if a]
    heapq.heapify(heap)

    out = []
    while heap:
        value, which, idx = heapq.heappop(heap)
        out.append(value)
        if idx + 1 < len(arrays[which]):
            heapq.heappush(heap, (arrays[which][idx + 1], which, idx + 1))
    return out''',
                ),
                dict(
                    name="Concatenate and sort",
                    time="O(N log N)",
                    space="O(N)",
                    tag="baseline",
                    why=[
                        "Throws away the fact that the inputs are already sorted. Fine for small k, and Timsort's run detection recovers some of the loss, but it is asymptotically worse and needs all N elements in memory at once.",
                    ],
                    code='''def merge_k_arrays(arrays):
    out = []
    for a in arrays:
        out.extend(a)
    return sorted(out)''',
                ),
            ],
            tests='''assert merge_k_arrays([[1, 4, 5], [1, 3, 4], [2, 6]]) == [1, 1, 2, 3, 4, 4, 5, 6]
assert merge_k_arrays([]) == []
assert merge_k_arrays([[]]) == []
assert merge_k_arrays([[], [1], []]) == [1]
assert merge_k_arrays([[1, 2, 3]]) == [1, 2, 3]
import random
random.seed(5)
for _ in range(40):
    arrays = [sorted(random.randint(0, 30) for _ in range(random.randint(0, 6)))
              for _ in range(random.randint(0, 5))]
    expected = sorted(v for a in arrays for v in a)
    assert merge_k_arrays(arrays) == expected''',
        ),

        dict(
            id="merge-k-sorted-lists",
            lc=23, slug="merge-k-sorted-lists",
            name="Merge k Sorted Lists",
            difficulty="hard",
            approaches=[
                dict(
                    name="Min-heap of list heads",
                    time="O(N log k)",
                    space="O(k)",
                    best=True,
                    why=[
                        "The previous problem with pointers instead of indices. Seed the heap with every list's head, pop the smallest, append it to the result, and push that node's successor.",
                        "N nodes, each pushed and popped once from a heap of size &le; k: <strong>O(N log k)</strong>. Space is O(k) for the heap; the output reuses the existing nodes, so no new list is allocated.",
                        "The detail that breaks this in Python: <code>ListNode</code> is not orderable, so when two nodes hold equal values the heap tries to compare the nodes themselves and raises <code>TypeError</code>. Push <code>(value, tiebreak, node)</code> with a unique integer in the middle &mdash; the index of the list &mdash; so the comparison never reaches the node.",
                        "A dummy head removes the special case for the first node appended.",
                    ],
                    code='''def merge_k_lists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)

    dummy = tail = ListNode()
    while heap:
        value, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next is not None:
            heapq.heappush(heap, (node.next.val, i, node.next))
    tail.next = None
    return dummy.next''',
                ),
                dict(
                    name="Merge pairwise, halving each round",
                    time="O(N log k)",
                    space="O(1)",
                    tag="no heap",
                    why=[
                        "Merge lists 1&amp;2, 3&amp;4, and so on, halving the number of lists each round until one remains. Same bound as the heap, reached differently.",
                        "Each round touches all N nodes and there are log k rounds, so O(N log k). Space is <strong>O(1)</strong> &mdash; better than the heap's O(k) &mdash; because iterative two-way merging needs no auxiliary structure.",
                        "Merging them one at a time instead (list 1 with 2, then with 3, &hellip;) is the trap: the accumulated list is re-walked every round, giving O(N k).",
                    ],
                    code='''def merge_k_lists(lists):
    lists = [node for node in lists if node]
    if not lists:
        return None
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            if i + 1 < len(lists):
                merged.append(merge_two(lists[i], lists[i + 1]))
            else:
                merged.append(lists[i])
        lists = merged
    return lists[0]


def merge_two(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next''',
                ),
            ],
            tests='''got = merge_k_lists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])])
assert list_vals(got) == [1, 1, 2, 3, 4, 4, 5, 6]
assert merge_k_lists([]) is None
assert merge_k_lists([None]) is None
assert list_vals(merge_k_lists([build_list([1])])) == [1]
# equal values must not make the heap compare ListNodes
assert list_vals(merge_k_lists([build_list([2, 2]), build_list([2, 2])])) == [2, 2, 2, 2]
import random
random.seed(7)
for _ in range(30):
    arrays = [sorted(random.randint(0, 10) for _ in range(random.randint(0, 5)))
              for _ in range(random.randint(0, 4))]
    nodes = [build_list(a) for a in arrays]
    expected = sorted(v for a in arrays for v in a)
    assert list_vals(merge_k_lists(nodes)) == expected''',
            pitfall="Pushing the node itself into the heap. Equal values then force a comparison of two <code>ListNode</code> objects and raise <code>TypeError</code> &mdash; and only on inputs with duplicates, so it passes the sample tests.",
        ),

        dict(
            id="smallest-range-k-lists",
            lc=632, slug="smallest-range-covering-elements-from-k-lists",
            name="Smallest Range Covering Elements from K Lists",
            difficulty="hard",
            approaches=[
                dict(
                    name="k-way merge tracking the window",
                    time="O(N log k)",
                    space="O(k)",
                    best=True,
                    why=[
                        "Run the k-way merge, but keep one cursor per list <em>alive at all times</em>. The heap's root is the smallest current value and you track the largest separately, so <code>[root, largest]</code> is always a range containing at least one element from every list.",
                        "Each pop advances exactly one cursor, which is the only way to shrink the window from the left. Record the range whenever it improves, and stop the moment any list runs out &mdash; from then on no valid range exists.",
                        "N total elements, each pushed and popped once from a size-k heap: <strong>O(N log k)</strong>, O(k) space.",
                        "Why tracking the maximum is cheap: values only ever get replaced by a <em>larger</em> one from the same list, since each list is sorted. So the running maximum only increases and needs no second heap.",
                    ],
                    code='''def smallest_range(nums):
    heap = [(row[0], i, 0) for i, row in enumerate(nums)]
    heapq.heapify(heap)
    largest = max(row[0] for row in nums)

    best = (heap[0][0], largest)
    while True:
        value, which, idx = heapq.heappop(heap)
        if largest - value < best[1] - best[0]:
            best = (value, largest)
        if idx + 1 == len(nums[which]):
            return list(best)              # this list is exhausted
        nxt = nums[which][idx + 1]
        largest = max(largest, nxt)
        heapq.heappush(heap, (nxt, which, idx + 1))''',
                ),
            ],
            tests='''assert smallest_range([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]) == [20, 24]
assert smallest_range([[1, 2, 3], [1, 2, 3], [1, 2, 3]]) == [1, 1]
assert smallest_range([[1], [2], [3]]) == [1, 3]
assert smallest_range([[10], [11]]) == [10, 11]
assert smallest_range([[1, 2, 3]]) == [1, 1]''',
            pitfall="Continuing after a list is exhausted. Once one list has no values left, no range can cover all k lists, so you must stop rather than keep improving.",
        ),

        dict(
            id="kth-smallest-in-sorted-matrix",
            lc=378, slug="kth-smallest-element-in-a-sorted-matrix",
            name="Kth Smallest Element in a Sorted Matrix",
            difficulty="medium",
            approaches=[
                dict(
                    name="k-way merge over the rows",
                    time="O(k log n)",
                    space="O(n)",
                    why=[
                        "Each row is sorted, so this is a k-way merge over n rows. Seed the heap with the first element of each row and pop k times.",
                        "The heap never exceeds n entries and you pop k times, so <strong>O(k log n)</strong> after an O(n) build. Since k can be as large as n&sup2;, the worst case is O(n&sup2; log n).",
                        "Seeding only <code>min(k, n)</code> rows is a free improvement: the answer cannot come from a row whose first element is already beyond position k.",
                    ],
                    code='''def kth_smallest(matrix, k):
    n = len(matrix)
    heap = [(matrix[r][0], r, 0) for r in range(min(k, n))]
    heapq.heapify(heap)

    for _ in range(k - 1):
        value, r, c = heapq.heappop(heap)
        if c + 1 < n:
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
    return heap[0][0]''',
                ),
                dict(
                    name="Binary search on the value",
                    time="O(n log(hi - lo))",
                    space="O(1)",
                    best=True,
                    tag="beats the heap",
                    why=[
                        "Do not search the matrix &mdash; search the <em>answer range</em>. For a candidate value <code>mid</code>, count how many entries are &le; mid; if that count is &lt; k the answer is larger, otherwise it is mid or smaller.",
                        "Counting is O(n) with a staircase walk: start at the bottom-left, move up when the cell is too big and right when it is not, so each of the n rows and n columns is passed at most once. No sorting, no heap.",
                        "The binary search runs over the numeric range, so it takes log(max - min) iterations &mdash; about 31 for 32-bit values. Total <strong>O(n log(hi - lo))</strong> and <strong>O(1)</strong> space, beating the heap on both when k is large.",
                        "The loop converges on a value that is actually present: the count is a step function that only jumps at real matrix values, so the smallest value with count &ge; k is in the matrix.",
                    ],
                    code='''def kth_smallest(matrix, k):
    n = len(matrix)
    lo, hi = matrix[0][0], matrix[n - 1][n - 1]
    while lo < hi:
        mid = (lo + hi) // 2
        if count_le(matrix, mid) < k:
            lo = mid + 1
        else:
            hi = mid
    return lo


def count_le(matrix, target):
    """How many entries are <= target, walking the staircase."""
    n = len(matrix)
    count, r, c = 0, n - 1, 0
    while r >= 0 and c < n:
        if matrix[r][c] <= target:
            count += r + 1        # whole column above is <= target too
            c += 1
        else:
            r -= 1
    return count''',
                ),
            ],
            tests='''m = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
assert kth_smallest(m, 8) == 13
assert kth_smallest(m, 1) == 1
assert kth_smallest(m, 9) == 15
assert kth_smallest([[-5]], 1) == -5
assert kth_smallest([[1, 2], [1, 3]], 2) == 1
assert kth_smallest([[1, 2], [1, 3]], 4) == 3
import random
random.seed(11)
for _ in range(25):
    n = random.randint(1, 6)
    rows = [sorted(random.randint(-10, 10) for _ in range(n)) for _ in range(n)]
    for c in range(n):                       # make columns sorted too
        col = sorted(rows[r][c] for r in range(n))
        for r in range(n):
            rows[r][c] = col[r]
    flat = sorted(v for row in rows for v in row)
    k = random.randint(1, n * n)
    assert kth_smallest(rows, k) == flat[k - 1]''',
            pitfall="Assuming the k-th smallest is on the diagonal, or that the matrix is sorted when read row by row. Rows and columns are each sorted; the flattened order is not.",
        ),
        ],
    ),

    # ---------------------------------------------------------------- 4
    dict(
        id="greedy-heaps",
        title="Greedy choices driven by a heap",
        problems=[

        dict(
            id="kth-smallest-matrix-row-sums",
            lc=1439, slug="find-the-kth-smallest-sum-of-a-matrix-with-sorted-rows",
            name="Find the Kth Smallest Sum of a Matrix With Sorted Rows",
            difficulty="hard",
            approaches=[
                dict(
                    name="Merge one row at a time, keeping k",
                    time="O(m &middot; k &middot; n log k)",
                    space="O(k)",
                    best=True,
                    why=[
                        "There are n<sup>m</sup> possible arrays, so enumerating them is hopeless. The insight is that you never need more than the <strong>k smallest sums so far</strong> &mdash; any partial sum outside that set can only grow, so it can never become the k-th smallest overall.",
                        "Fold the rows in one at a time. After processing row i you hold at most k running sums; combine each with each of the n values in the next row and keep the k smallest of those k&middot;n candidates.",
                        "<code>heapq.nsmallest(k, ...)</code> over k&middot;n candidates costs O(kn log k), repeated for m rows: <strong>O(m &middot; k &middot; n log k)</strong>, and only O(k) is held at any time. The pruning is what makes it tractable.",
                        "Because each row is sorted, you could also stop generating candidates for a row once the sum exceeds the current k-th best &mdash; a constant-factor win on top.",
                    ],
                    code='''def kth_smallest(mat, k):
    sums = [0]
    for row in mat:
        sums = heapq.nsmallest(k, (s + v for s in sums for v in row))
    return sums[-1]''',
                ),
                dict(
                    name="Best-first search over index tuples",
                    time="O(k &middot; m log k)",
                    space="O(k &middot; m)",
                    tag="explicit heap",
                    why=[
                        "Treat each candidate as a tuple of column indices, one per row. Start from all-zeros (the minimum possible sum) and repeatedly pop the smallest, pushing the m neighbours that advance exactly one row's index by one.",
                        "Popping k times, each pop pushing m successors into a heap that stays O(k&middot;m): <strong>O(k &middot; m log k)</strong>. A <code>visited</code> set is essential &mdash; the same tuple is reachable by different orders of increments, and without deduplication you both waste work and miscount the k-th pop.",
                        "This generalises to k-smallest over any monotone combination, which the row-folding version does not.",
                    ],
                    code='''def kth_smallest(mat, k):
    m, n = len(mat), len(mat[0])
    start = tuple([0] * m)
    first = sum(row[0] for row in mat)
    heap = [(first, start)]
    seen = {start}

    for _ in range(k - 1):
        total, idx = heapq.heappop(heap)
        for r in range(m):
            if idx[r] + 1 < n:
                nxt = idx[:r] + (idx[r] + 1,) + idx[r + 1:]
                if nxt not in seen:
                    seen.add(nxt)
                    heapq.heappush(
                        heap, (total - mat[r][idx[r]] + mat[r][idx[r] + 1], nxt))
    return heap[0][0]''',
                ),
            ],
            tests='''import itertools, random

assert kth_smallest([[1, 3, 11], [2, 4, 6]], 5) == 7
assert kth_smallest([[1, 3, 11], [2, 4, 6]], 9) == 17
assert kth_smallest([[1, 10, 10], [1, 4, 5], [2, 3, 6]], 7) == 9
assert kth_smallest([[1, 1, 10], [2, 2, 9]], 7) == 12
assert kth_smallest([[5]], 1) == 5

random.seed(13)
for _ in range(25):
    m = random.randint(1, 3)
    n = random.randint(1, 4)
    mat = [sorted(random.randint(1, 9) for _ in range(n)) for _ in range(m)]
    every = sorted(sum(c) for c in itertools.product(*mat))
    k = random.randint(1, min(len(every), 8))
    assert kth_smallest(mat, k) == every[k - 1], (mat, k)''',
            pitfall="Trying to enumerate all n<sup>m</sup> arrays. The pruning to k survivors per row is the entire problem.",
        ),

        dict(
            id="connect-sticks",
            lc=1167, slug="minimum-cost-to-connect-sticks",
            name="Minimum Cost to Connect Sticks",
            difficulty="medium",
            statement=[
                "You have sticks with positive integer lengths. You can connect any two sticks of lengths <code>x</code> and <code>y</code> into one stick of length <code>x + y</code>, at a cost of <code>x + y</code>.",
                "Connect all the sticks into one and return the minimum total cost.",
                "This is Huffman coding wearing a different hat: the cost of a stick is its length multiplied by the number of merges it takes part in, so the cheapest plan merges short sticks most often.",
            ],
            examples=[
                dict(input="sticks = [2, 4, 3]", output="14",
                     explanation="Join 2 and 3 for 5, then 5 and 4 for 9. Total 5 + 9 = 14."),
                dict(input="sticks = [1, 8, 3, 5]", output="30",
                     explanation="1+3=4, 4+5=9, 9+8=17. Total 4 + 9 + 17 = 30."),
                dict(input="sticks = [5]", output="0",
                     explanation="Already a single stick, so nothing to connect."),
            ],
            constraints=[
                "<code>1 &lt;= sticks.length &lt;= 10<sup>4</sup></code>",
                "<code>1 &lt;= sticks[i] &lt;= 10<sup>4</sup></code>",
            ],
            note="LeetCode 1167 is a <strong>premium</strong> problem, so the statement above is written here rather than fetched.",
            approaches=[
                dict(
                    name="Always merge the two shortest",
                    time="O(n log n)",
                    space="O(n)",
                    best=True,
                    why=[
                        "Heapify the lengths, then repeatedly pop the two smallest, push their sum, and add that sum to the running cost. Stop when one stick remains.",
                        "O(n) to heapify, then n-1 merges each doing two pops and a push at O(log n): <strong>O(n log n)</strong>.",
                        "Why greedy is optimal here is the part worth being able to argue. Every stick's length is paid once per merge it participates in, so the total cost is &Sigma; length &times; depth in the merge tree. Minimising that is exactly Huffman's problem, and the exchange argument applies: if a longer stick were merged deeper than a shorter one, swapping them lowers the total.",
                        "Sorting once is <em>not</em> enough. The sums you create re-enter the pool and must be re-ordered against the originals, which is precisely what the heap does cheaply.",
                    ],
                    code='''def connect_sticks(sticks):
    heap = list(sticks)
    heapq.heapify(heap)

    total = 0
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        total += a + b
        heapq.heappush(heap, a + b)
    return total''',
                ),
            ],
            tests='''assert connect_sticks([2, 4, 3]) == 14
assert connect_sticks([1, 8, 3, 5]) == 30
assert connect_sticks([5]) == 0
assert connect_sticks([1, 1]) == 2
assert connect_sticks([1, 2, 3, 4, 5]) == 33

import itertools, random


def brute(sticks):
    if len(sticks) <= 1:
        return 0
    best = None
    for i, j in itertools.combinations(range(len(sticks)), 2):
        rest = [s for n, s in enumerate(sticks) if n not in (i, j)]
        cost = sticks[i] + sticks[j] + brute(rest + [sticks[i] + sticks[j]])
        best = cost if best is None else min(best, cost)
    return best


random.seed(17)
for _ in range(20):
    data = [random.randint(1, 12) for _ in range(random.randint(1, 6))]
    assert connect_sticks(list(data)) == brute(list(data)), data''',
            pitfall="Sorting once and summing left to right. Each merged stick must be re-inserted into the ordering, which only a heap (or a second queue) gives you.",
        ),

        dict(
            id="task-scheduler",
            lc=621, slug="task-scheduler",
            name="Task Scheduler",
            difficulty="medium",
            approaches=[
                dict(
                    name="Counting formula",
                    time="O(n)",
                    space="O(1)",
                    best=True,
                    tag="no heap needed",
                    why=[
                        "Only the most frequent task matters. If it occurs <code>f</code> times it creates <code>f - 1</code> gaps, each of width <code>n + 1</code> counting the task itself, plus one final run of every task tied at that frequency.",
                        "So the answer is <code>(f - 1) &times; (n + 1) + (number of tasks with frequency f)</code> &mdash; unless there are so many distinct tasks that the gaps fill themselves, in which case no idling happens at all and the answer is simply <code>len(tasks)</code>. Taking the <code>max</code> of the two covers both.",
                        "<strong>O(n)</strong> time and O(1) space, since the counter holds at most 26 keys. This is the answer to reach for; the heap version below is the one people write first and is strictly worse.",
                    ],
                    code='''def least_interval(tasks, n):
    counts = Counter(tasks)
    most = max(counts.values())
    tied = sum(1 for c in counts.values() if c == most)
    return max(len(tasks), (most - 1) * (n + 1) + tied)''',
                ),
                dict(
                    name="Max-heap with a cooldown queue",
                    time="O(N log 26) = O(N)",
                    space="O(1)",
                    why=[
                        "Simulate it. Keep a max-heap of remaining counts and a queue of tasks cooling down with the time they become available. Each tick, run the most frequent available task; if none is available, idle.",
                        "The heap holds at most 26 entries, so each operation is O(log 26), a constant. The loop runs once per time unit and the answer can be about n times the number of tasks, so this is O(answer) rather than O(len(tasks)) &mdash; noticeably worse when <code>n</code> is large and there are few distinct tasks.",
                        "Worth writing because it generalises: the moment tasks have different durations or priorities the closed-form breaks and the simulation still works.",
                    ],
                    code='''def least_interval(tasks, n):
    heap = [-c for c in Counter(tasks).values()]
    heapq.heapify(heap)

    time = 0
    cooling = deque()          # (ready_at, remaining_count)
    while heap or cooling:
        time += 1
        if heap:
            remaining = heapq.heappop(heap) + 1     # negative counts
            if remaining:
                cooling.append((time + n, remaining))
        if cooling and cooling[0][0] == time:
            heapq.heappush(heap, cooling.popleft()[1])
    return time''',
                ),
            ],
            tests='''assert least_interval(["A", "A", "A", "B", "B", "B"], 2) == 8
assert least_interval(["A", "C", "A", "B", "D", "B"], 1) == 6
assert least_interval(["A", "A", "A", "B", "B", "B"], 0) == 6
assert least_interval(["A"], 5) == 1
assert least_interval(["A", "A", "A", "A", "B", "C", "D", "E"], 2) == 10
assert least_interval(list("AAABBBCCC"), 2) == 9''',
            pitfall="Forgetting the <code>max(len(tasks), ...)</code>. With many distinct tasks the gaps fill up and the formula alone under-counts.",
        ),

        dict(
            id="reorganize-string",
            lc=767, slug="reorganize-string",
            name="Reorganize String",
            difficulty="medium",
            approaches=[
                dict(
                    name="Max-heap, always take two",
                    time="O(n log 26) = O(n)",
                    space="O(n)",
                    why=[
                        "Pop the two most frequent remaining characters, append both, decrement each, and push back whatever is left. Taking <em>two</em> at a time guarantees you never place the same character twice in a row.",
                        "The heap holds at most 26 entries so each operation is constant; the loop runs O(n) times. Space is the output.",
                        "It is impossible exactly when one character occurs more than <code>(n + 1) // 2</code> times &mdash; there are not enough slots to separate them. Checking that up front is cheaper than discovering it mid-loop.",
                    ],
                    code='''def reorganize_string(s):
    counts = Counter(s)
    if max(counts.values()) > (len(s) + 1) // 2:
        return ""

    heap = [(-c, ch) for ch, c in counts.items()]
    heapq.heapify(heap)

    out = []
    while len(heap) > 1:
        c1, ch1 = heapq.heappop(heap)
        c2, ch2 = heapq.heappop(heap)
        out.append(ch1)
        out.append(ch2)
        if c1 + 1:
            heapq.heappush(heap, (c1 + 1, ch1))
        if c2 + 1:
            heapq.heappush(heap, (c2 + 1, ch2))
    if heap:
        out.append(heap[0][1])
    return "".join(out)''',
                ),
                dict(
                    name="Fill even slots, then odd",
                    time="O(n log 26) = O(n)",
                    space="O(n)",
                    best=True,
                    tag="no heap",
                    why=[
                        "Place the most frequent character first into positions 0, 2, 4, &hellip;; when you run off the end, continue at 1, 3, 5, &hellip;. Then place every other character the same way, continuing from where the last one stopped.",
                        "Two characters end up adjacent only if one occupies both an even index and the odd index next to it, which requires more than <code>(n+1)//2</code> copies &mdash; the case already rejected. So the construction is correct by the same counting argument.",
                        "Same O(n) bound with a much smaller constant and no heap at all: one sort of at most 26 counts, then a single pass. This is the version to write.",
                    ],
                    code='''def reorganize_string(s):
    counts = Counter(s)
    if max(counts.values()) > (len(s) + 1) // 2:
        return ""

    out = [""] * len(s)
    i = 0
    for ch, freq in counts.most_common():       # most frequent first
        for _ in range(freq):
            if i >= len(s):
                i = 1                           # switch to the odd slots
            out[i] = ch
            i += 2
    return "".join(out)''',
                ),
            ],
            tests='''def ok(s, out):
    if not out:
        return True
    return (Counter(out) == Counter(s)
            and all(a != b for a, b in zip(out, out[1:])))


for case in ("aab", "aaab", "vvvlo", "a", "ab", "aaabbb", "abbabbaab"):
    got = reorganize_string(case)
    impossible = max(Counter(case).values()) > (len(case) + 1) // 2
    assert (got == "") == impossible, (case, got)
    assert ok(case, got), (case, got)

assert reorganize_string("aaab") == ""
assert reorganize_string("aab") in ("aba",)

import random
random.seed(19)
for _ in range(60):
    case = "".join(random.choice("abc") for _ in range(random.randint(1, 12)))
    got = reorganize_string(case)
    impossible = max(Counter(case).values()) > (len(case) + 1) // 2
    assert (got == "") == impossible, (case, got)
    assert ok(case, got), (case, got)''',
            pitfall="Popping one character at a time and pushing it straight back. It is immediately the most frequent again, so you emit it twice in a row.",
        ),

        dict(
            id="ipo",
            lc=502, slug="ipo",
            name="IPO",
            difficulty="hard",
            approaches=[
                dict(
                    name="Two heaps: affordable by capital, best by profit",
                    time="O(n log n)",
                    space="O(n)",
                    best=True,
                    why=[
                        "Sort the projects by capital required. Keep a pointer that releases every project you can now afford into a <em>max</em>-heap keyed on profit, then take the best one. Repeat k times.",
                        "The greedy choice is safe because profits are non-negative: taking the most profitable affordable project can only increase your capital, which can only widen the set of affordable projects later. Nothing is foreclosed.",
                        "Sorting is O(n log n); each project enters the profit heap at most once across the whole run, so the heap work is also O(n log n) &mdash; not O(k n). The pointer never rewinds, which is what keeps it linear in pushes.",
                        "Break early when the profit heap is empty: no project is affordable and no further capital can arrive.",
                    ],
                    code='''def find_maximized_capital(k, w, profits, capital):
    projects = sorted(zip(capital, profits))
    affordable = []                 # max-heap of profits, negated
    i = 0

    for _ in range(k):
        while i < len(projects) and projects[i][0] <= w:
            heapq.heappush(affordable, -projects[i][1])
            i += 1
        if not affordable:
            break                   # nothing reachable, capital cannot grow
        w -= heapq.heappop(affordable)
    return w''',
                ),
            ],
            tests='''assert find_maximized_capital(2, 0, [1, 2, 3], [0, 1, 1]) == 4
assert find_maximized_capital(3, 0, [1, 2, 3], [0, 1, 2]) == 6
assert find_maximized_capital(1, 0, [1, 2, 3], [1, 1, 2]) == 0
assert find_maximized_capital(1, 2, [1, 2, 3], [1, 1, 2]) == 5
assert find_maximized_capital(10, 0, [1], [0]) == 1
assert find_maximized_capital(0, 5, [1, 2], [0, 0]) == 5''',
            pitfall="Re-scanning all projects on every round. The capital pointer only moves forward, so each project is released into the heap once.",
        ),
        ],
    ),

    # ---------------------------------------------------------------- 5
    dict(
        id="intervals",
        title="Intervals and reachability",
        problems=[

        dict(
            id="meeting-rooms",
            lc=252, slug="meeting-rooms",
            name="Meeting Rooms",
            difficulty="easy",
            statement=[
                "Given an array of meeting time intervals <code>[start, end]</code>, determine whether a person could attend all of them.",
                "The baseline for the next problem: no heap, just the observation that sorting by start time turns \"does any pair overlap?\" into \"does any <em>adjacent</em> pair overlap?\".",
            ],
            examples=[
                dict(input="intervals = [[0,30],[5,10],[15,20]]", output="false",
                     explanation="[0,30] overlaps [5,10]."),
                dict(input="intervals = [[7,10],[2,4]]", output="true",
                     explanation="Sorted they are [2,4] and [7,10], which do not overlap."),
            ],
            constraints=[
                "<code>0 &lt;= intervals.length &lt;= 10<sup>4</sup></code>",
                "<code>intervals[i].length == 2</code>",
                "<code>0 &lt;= start<sub>i</sub> &lt; end<sub>i</sub> &lt;= 10<sup>6</sup></code>",
            ],
            note="LeetCode 252 is a <strong>premium</strong> problem, so the statement above is written here rather than fetched.",
            approaches=[
                dict(
                    name="Sort by start, compare neighbours",
                    time="O(n log n)",
                    space="O(1)",
                    best=True,
                    why=[
                        "After sorting by start time, if any two meetings overlap then some <em>adjacent</em> pair does. So one linear scan comparing each start against the previous end settles it.",
                        "The proof is short and worth being able to give: if meeting i overlaps meeting j with i &lt; j, then <code>start[j] &lt; end[i]</code>, and since starts are sorted every meeting between them also starts before <code>end[i]</code> &mdash; so the pair at i and i+1 already overlaps.",
                        "O(n log n) dominated by the sort; the scan is O(n) and O(1) extra space.",
                        "Touching endpoints do not conflict: a meeting ending at 10 and one starting at 10 are fine, so the comparison is strict.",
                    ],
                    code='''def can_attend_meetings(intervals):
    intervals.sort()
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True''',
                ),
            ],
            tests='''assert can_attend_meetings([[0, 30], [5, 10], [15, 20]]) is False
assert can_attend_meetings([[7, 10], [2, 4]]) is True
assert can_attend_meetings([]) is True
assert can_attend_meetings([[1, 5]]) is True
assert can_attend_meetings([[1, 5], [5, 9]]) is True     # touching is fine
assert can_attend_meetings([[1, 5], [4, 9]]) is False''',
        ),

        dict(
            id="meeting-rooms-ii",
            lc=253, slug="meeting-rooms-ii",
            name="Meeting Rooms II",
            difficulty="medium",
            statement=[
                "Given an array of meeting time intervals <code>[start, end]</code>, return the minimum number of conference rooms required.",
                "The canonical min-heap interval problem. The answer is the maximum number of meetings in progress at any instant.",
            ],
            examples=[
                dict(input="intervals = [[0,30],[5,10],[15,20]]", output="2",
                     explanation="[5,10] and [15,20] can share one room; [0,30] needs its own."),
                dict(input="intervals = [[7,10],[2,4]]", output="1",
                     explanation="They do not overlap, so one room is enough."),
            ],
            constraints=[
                "<code>1 &lt;= intervals.length &lt;= 10<sup>4</sup></code>",
                "<code>0 &lt;= start<sub>i</sub> &lt; end<sub>i</sub> &lt;= 10<sup>6</sup></code>",
            ],
            note="LeetCode 253 is a <strong>premium</strong> problem, so the statement above is written here rather than fetched.",
            approaches=[
                dict(
                    name="Min-heap of end times",
                    time="O(n log n)",
                    space="O(n)",
                    best=True,
                    why=[
                        "Sort by start. Keep a min-heap of the end times of rooms currently in use. For each meeting, if the earliest-finishing room is already free (<code>heap[0] &lt;= start</code>) reuse it by popping; then push this meeting's end. The heap size is the number of rooms in use, and its maximum is the answer.",
                        "Only the <em>earliest</em> ending room ever needs checking: if that one is still busy, every other room is too. That is exactly what a min-heap gives in O(1), and it is why a heap beats scanning the rooms.",
                        "Sort O(n log n), then n pushes and at most n pops at O(log n): <strong>O(n log n)</strong> overall, O(n) space in the worst case where every meeting overlaps.",
                    ],
                    code='''def min_meeting_rooms(intervals):
    if not intervals:
        return 0
    intervals.sort()
    ends = []                       # min-heap of in-use room end times

    for start, end in intervals:
        if ends and ends[0] <= start:
            heapq.heappop(ends)     # earliest room is free, reuse it
        heapq.heappush(ends, end)
    return len(ends)''',
                ),
                dict(
                    name="Sweep the endpoints",
                    time="O(n log n)",
                    space="O(n)",
                    tag="no heap",
                    why=[
                        "Separate the starts and ends into two sorted arrays and walk them together. A start before the next end means a new room; otherwise a room frees up. The running count's maximum is the answer.",
                        "Same O(n log n) from the two sorts, but with no heap and a smaller constant. It also generalises to \"maximum concurrent X\" problems where you never need to know <em>which</em> interval is which.",
                        "The heap version is preferable when you need the rooms themselves &mdash; assigning each meeting to a specific room, say &mdash; because the sweep discards that identity.",
                    ],
                    code='''def min_meeting_rooms(intervals):
    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)

    rooms = best = 0
    j = 0
    for start in starts:
        while ends[j] <= start:
            rooms -= 1
            j += 1
        rooms += 1
        best = max(best, rooms)
    return best''',
                ),
            ],
            tests='''assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
assert min_meeting_rooms([[7, 10], [2, 4]]) == 1
assert min_meeting_rooms([[1, 5]]) == 1
assert min_meeting_rooms([[1, 5], [5, 9]]) == 1          # touching shares a room
assert min_meeting_rooms([[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]]) == 4

import random
random.seed(23)
for _ in range(40):
    data = []
    for _ in range(random.randint(1, 10)):
        s = random.randint(0, 20)
        data.append([s, s + random.randint(1, 8)])
    # brute force: busiest instant, checked on half-integer ticks
    busiest = 0
    for t in range(0, 40):
        busiest = max(busiest, sum(1 for s, e in data if s <= t < e))
    assert min_meeting_rooms([list(x) for x in data]) == busiest, data''',
        ),

        dict(
            id="refueling-stops",
            lc=871, slug="minimum-number-of-refueling-stops",
            name="Minimum Number of Refueling Stops",
            difficulty="hard",
            approaches=[
                dict(
                    name="Max-heap of fuel already driven past",
                    time="O(n log n)",
                    space="O(n)",
                    best=True,
                    why=[
                        "The trick is to refuel <em>retroactively</em>. Drive as far as the fuel allows, collecting every station you pass into a max-heap without stopping. When you run short, take the largest tank you have passed and pretend you stopped there.",
                        "That is valid because the order of refuelling does not change the total fuel available at any point past those stations &mdash; only the count of stops matters, and taking the biggest tank each time minimises that count. This is a clean exchange argument: swapping any chosen station for a larger passed one never increases the stop count.",
                        "Each station is pushed once and popped at most once: <strong>O(n log n)</strong>, O(n) space. Return <code>-1</code> when the heap empties before the target is reachable.",
                    ],
                    code='''def min_refuel_stops(target, start_fuel, stations):
    passed = []                    # max-heap of fuel amounts, negated
    fuel, stops, i = start_fuel, 0, 0

    while fuel < target:
        while i < len(stations) and stations[i][0] <= fuel:
            heapq.heappush(passed, -stations[i][1])
            i += 1
        if not passed:
            return -1              # cannot reach any further station
        fuel -= heapq.heappop(passed)
        stops += 1
    return stops''',
                ),
            ],
            tests='''assert min_refuel_stops(1, 1, []) == 0
assert min_refuel_stops(100, 1, [[10, 100]]) == -1
assert min_refuel_stops(100, 10, [[10, 60], [20, 30], [30, 30], [60, 40]]) == 2
assert min_refuel_stops(1000, 299, [[13, 21], [26, 115], [100, 47], [225, 99], [299, 141], [444, 198], [608, 190], [636, 157], [647, 255], [841, 123]]) == 4
assert min_refuel_stops(5, 5, [[1, 1]]) == 0''',
            pitfall="Greedily stopping at the first station that helps. You must defer the decision until you actually run out, then pick the best tank you have already driven past.",
        ),
        ],
    ),

    # ---------------------------------------------------------------- 6
    dict(
        id="two-heaps",
        title="Two heaps: keeping a running median",
        problems=[

        dict(
            id="find-median-from-data-stream",
            lc=295, slug="find-median-from-data-stream",
            name="Find Median from Data Stream",
            difficulty="hard",
            approaches=[
                dict(
                    name="Max-heap of the low half, min-heap of the high half",
                    time="O(log n) add, O(1) find",
                    space="O(n)",
                    best=True,
                    why=[
                        "Split the values in two. <code>small</code> is a max-heap holding the lower half, <code>large</code> is a min-heap holding the upper half. The median is then either the top of <code>small</code> or the average of the two tops &mdash; both O(1) reads.",
                        "The invariant to state: every element of <code>small</code> is &le; every element of <code>large</code>, and their sizes differ by at most one. Maintaining it is the whole implementation.",
                        "The neat way to maintain it: always push onto <code>small</code>, immediately move its top to <code>large</code>, then move back if <code>large</code> has grown too big. Two pushes and two pops keeps you from having to reason about which side the new value belongs on.",
                        "<code>add</code> is <strong>O(log n)</strong>, <code>find</code> is <strong>O(1)</strong>. A sorted list would give O(1) find but O(n) insert; a plain list gives O(1) insert but O(n log n) find.",
                    ],
                    code='''class MedianFinder:
    def __init__(self):
        self.small = []      # max-heap (negated): the lower half
        self.large = []      # min-heap: the upper half

    def add_num(self, num):
        heapq.heappush(self.small, -num)
        # hand the largest of the low half up
        heapq.heappush(self.large, -heapq.heappop(self.small))
        # keep small the same size or one bigger
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def find_median(self):
        if len(self.small) > len(self.large):
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2.0''',
                ),
                dict(
                    name="Sorted list with bisect",
                    time="O(n) add, O(1) find",
                    space="O(n)",
                    why=[
                        "<code>bisect.insort</code> keeps one sorted list, so the median is a direct index. The binary search is O(log n) but the insertion shifts the tail, making each add O(n).",
                        "For a few thousand values this is faster in practice than the two heaps, because the memory move is a fast contiguous copy while heap operations chase pointers in Python objects. Worth saying out loud &mdash; asymptotics are not the only argument &mdash; but the heaps win as n grows.",
                    ],
                    code='''import bisect


class MedianFinder:
    def __init__(self):
        self.data = []

    def add_num(self, num):
        bisect.insort(self.data, num)

    def find_median(self):
        n = len(self.data)
        mid = n // 2
        if n % 2:
            return float(self.data[mid])
        return (self.data[mid - 1] + self.data[mid]) / 2.0''',
                ),
            ],
            tests='''mf = MedianFinder()
mf.add_num(1)
mf.add_num(2)
assert mf.find_median() == 1.5
mf.add_num(3)
assert mf.find_median() == 2.0

mf = MedianFinder()
mf.add_num(-1)
assert mf.find_median() == -1.0
mf.add_num(-2)
assert mf.find_median() == -1.5
mf.add_num(-3)
assert mf.find_median() == -2.0

import random, statistics
random.seed(29)
for _ in range(30):
    mf = MedianFinder()
    seen = []
    for _ in range(random.randint(1, 40)):
        v = random.randint(-30, 30)
        mf.add_num(v)
        seen.append(v)
        assert mf.find_median() == statistics.median(seen)''',
        ),

        dict(
            id="sliding-window-median",
            lc=480, slug="sliding-window-median",
            name="Sliding Window Median",
            difficulty="hard",
            approaches=[
                dict(
                    name="Sorted window with bisect",
                    time="O(n k)",
                    space="O(k)",
                    best=True,
                    tag="what to write first",
                    why=[
                        "Keep the window as a sorted list. Each step, binary-search the outgoing value and delete it, then binary-search the incoming value and insert it. The median is two index reads.",
                        "Both <code>bisect</code> calls are O(log k), but the list operations shift elements, so each step is O(k) and the total is <strong>O(n k)</strong>.",
                        "For interview purposes this is the right first answer: it is eight lines, obviously correct, and at LeetCode's limits it passes. Offer the two-heap version as the improvement.",
                    ],
                    code='''import bisect


def median_sliding_window(nums, k):
    window = sorted(nums[:k])
    half, odd = k // 2, k % 2

    def median():
        if odd:
            return float(window[half])
        return (window[half - 1] + window[half]) / 2.0

    out = [median()]
    for i in range(k, len(nums)):
        window.pop(bisect.bisect_left(window, nums[i - k]))
        bisect.insort(window, nums[i])
        out.append(median())
    return out''',
                ),
                dict(
                    name="Two heaps with lazy deletion",
                    time="O(n log k)",
                    space="O(k)",
                    tag="asymptotically better",
                    why=[
                        "The same two-heap split as the running median, plus the one thing heaps cannot do: remove an arbitrary element. <code>heapq</code> only pops the root, and the value leaving the window is usually somewhere in the middle.",
                        "The fix is <strong>lazy deletion</strong>. Record the departing value in a <code>delayed</code> counter and adjust the logical size, but leave it in the heap. Only when a stale value surfaces at a root is it actually popped. Every element is deleted at most once, so the amortised cost stays O(log k).",
                        "This is why the sizes must be tracked in separate counters: <code>len(heap)</code> now counts ghosts. Getting that wrong is the classic bug, and it only shows up on windows where a duplicate straddles the two halves.",
                        "<strong>O(n log k)</strong> time, O(k) space. Real, but a lot of machinery &mdash; in Python, <code>sortedcontainers.SortedList</code> gives O(log k) with none of it.",
                    ],
                    code='''def median_sliding_window(nums, k):
    small, large = [], []          # max-heap (negated) | min-heap
    delayed = Counter()
    n_small = n_large = 0

    def prune(heap):
        """Drop already-deleted values sitting at the root."""
        while heap:
            value = -heap[0] if heap is small else heap[0]
            if delayed[value]:
                delayed[value] -= 1
                heapq.heappop(heap)
            else:
                break

    def rebalance():
        nonlocal n_small, n_large
        while n_small > n_large + 1:
            heapq.heappush(large, -heapq.heappop(small))
            n_small, n_large = n_small - 1, n_large + 1
            prune(small)
        while n_small < n_large:
            heapq.heappush(small, -heapq.heappop(large))
            n_small, n_large = n_small + 1, n_large - 1
            prune(large)

    def add(value):
        nonlocal n_small, n_large
        if not small or value <= -small[0]:
            heapq.heappush(small, -value)
            n_small += 1
        else:
            heapq.heappush(large, value)
            n_large += 1
        rebalance()

    def remove(value):
        nonlocal n_small, n_large
        delayed[value] += 1
        if small and value <= -small[0]:
            n_small -= 1
            if value == -small[0]:
                prune(small)
        else:
            n_large -= 1
            if large and value == large[0]:
                prune(large)
        rebalance()

    out = []
    for i, value in enumerate(nums):
        add(value)
        if i >= k:
            remove(nums[i - k])
        if i >= k - 1:
            out.append(float(-small[0]) if k % 2
                       else (-small[0] + large[0]) / 2.0)
    return out''',
                ),
            ],
            tests='''import random, statistics

got = median_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)
assert got == [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]
assert median_sliding_window([1, 2, 3, 4, 2, 3, 1, 4, 2], 3) == [2.0, 3.0, 3.0, 3.0, 2.0, 3.0, 2.0]
assert median_sliding_window([1], 1) == [1.0]
assert median_sliding_window([1, 4, 2, 3], 4) == [2.5]
assert median_sliding_window([2147483647, 2147483647], 2) == [2147483647.0]

random.seed(31)
for _ in range(40):
    n = random.randint(1, 25)
    data = [random.randint(-8, 8) for _ in range(n)]     # duplicates on purpose
    k = random.randint(1, n)
    expected = [float(statistics.median(data[i:i + k]))
                for i in range(n - k + 1)]
    assert median_sliding_window(list(data), k) == expected, (data, k)''',
            pitfall="Using <code>len(heap)</code> as the half size once lazy deletion is in play. The heaps contain values that have already logically left the window.",
        ),
        ],
    ),
    ],
)
