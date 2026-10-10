"""Write-ups for the Heaps and Priority Queues topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ heapify
    "heapify": {
        "examples": [
            {"call": "heapify([5, 3, 8, 1, 9, 2])", "expect": "[1, 3, 2, 5, 9, 8]"},
            {"call": "heapify([4, 1, 3, 2])", "expect": "[1, 2, 3, 4]"},
        ],
        "approaches": {
            "Sift down from the last parent": {
                "idea": [
                    "A heap is an array read as a tree: the children of index i are at 2i + 1 and 2i + 2, and every parent must be ≤ its children.",
                    "Leaves, the second half of the array, are already valid one-element heaps, so only the parents need fixing.",
                    "Fix the parents from the last one back to the root, sifting each one down below its smaller child until it fits.",
                ],
                "steps": [
                    "Let <code>n = len(nums)</code>. The last parent is at <code>n // 2 - 1</code>.",
                    "Loop <code>i</code> from <code>n // 2 - 1</code> down to 0 and call <code>sift_down(nums, i, n)</code>.",
                    "In <code>sift_down</code>, set <code>smallest = i</code> and compare it with <code>left = 2 * i + 1</code> and <code>right = 2 * i + 2</code> when they exist.",
                    "If <code>smallest == i</code>, the value fits: return.",
                    "Otherwise swap <code>nums[i]</code> with <code>nums[smallest]</code> and continue from <code>i = smallest</code>, one level lower.",
                ],
                "why": [
                    "Parents are processed bottom-up, so when <code>i</code> is sifted both of its subtrees are already heaps, and one sift makes the subtree rooted at <code>i</code> a heap.",
                    "Swapping with the <em>smaller</em> child is essential: the value moved up must be ≤ the other child too.",
                    "Most nodes sit near the bottom and can only fall a level or two: the total is n · Σ k/2<sup>k+1</sup> ≤ n swaps, so <strong>O(n)</strong> time, not O(n log n).",
                    "Everything happens in place with a few index variables: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "n = 6, so parents are indices 2, 1, 0.",
                        "i=2 (8): its only child is 2, smaller, so swap: [5, 3, 2, 1, 9, 8].",
                        "i=1 (3): children 1 and 9; 1 is smaller, swap: [5, 1, 2, 3, 9, 8].",
                        "i=0 (5): children 1 and 2; swap with 1: [1, 5, 2, 3, 9, 8]. Continue at index 1: children 3 and 9, swap with 3: [1, 3, 2, 5, 9, 8].",
                        "The result is <strong>[1, 3, 2, 5, 9, 8]</strong>.",
                    ],
                    [
                        "n = 4, so parents are indices 1 and 0.",
                        "i=1 (1): its only child is 2, which is larger, so nothing moves.",
                        "i=0 (4): children 1 and 3; swap with 1: [1, 4, 3, 2].",
                        "The 4 keeps falling: at index 1 its child 2 is smaller, swap: [1, 2, 3, 4]. Index 3 has no children, stop.",
                        "The result is <strong>[1, 2, 3, 4]</strong>: the root's value fell two levels.",
                    ],
                ],
                "faq": [
                    ["Why start at <code>n // 2 - 1</code>?",
                     "Index <code>n // 2 - 1</code> is the last index with a left child, since its left child is <code>n - 1</code> or <code>n - 2</code>. Everything after it is a leaf."],
                    ["Why go from the bottom up and not from the root down?",
                     "Sift-down assumes both subtrees are already heaps. Going bottom-up guarantees that; going top-down would fix the root against unsorted subtrees."],
                    ["How can it be O(n) when one sift costs O(log n)?",
                     "Only the few nodes near the top can fall far. Half the nodes are leaves (0 work), a quarter fall at most 1 level, an eighth at most 2, and that series adds up to at most n."],
                ],
            },
            "Push one at a time": {
                "idea": [
                    "Build the heap by inserting values one by one: each new value goes at the end and sifts <em>up</em> past larger parents.",
                    "This is the natural approach when values arrive one at a time, as in a stream.",
                    "For an array you already have, it does more work than sifting down, because most values are inserted at the deep bottom level.",
                ],
                "steps": [
                    "Start with an empty list <code>out</code>.",
                    "For each <code>value</code> in <code>nums</code>, call <code>heapq.heappush(out, value)</code>, which appends and sifts the value up.",
                    "Copy the result back into the caller's list with <code>nums[:] = out</code>.",
                    "Return <code>nums</code>.",
                ],
                "why": [
                    "After every push <code>out</code> is a valid heap, because a sift-up repairs the only path the new value can break.",
                    "Each push can climb up to log n levels, and half the values land on the bottom level: <strong>O(n log n)</strong> time in the worst case.",
                    "<code>out</code> is a second list of n values: <strong>O(n)</strong> extra space.",
                ],
                "dry": [
                    [
                        "Push 5, 3, 8: 3 climbs above 5, giving [3, 5, 8].",
                        "Push 1: it lands at index 3 and climbs past 5 and then 3: [1, 3, 8, 5].",
                        "Push 9: its parent 3 is smaller, it stays: [1, 3, 8, 5, 9].",
                        "Push 2: it lands at index 5, climbs past 8 and stops below 1: [1, 3, 2, 5, 9, 8].",
                        "The result is <strong>[1, 3, 2, 5, 9, 8]</strong>, the same array as sift-down here.",
                    ],
                    [
                        "Push 4: [4]. Push 1: it climbs above 4: [1, 4].",
                        "Push 3: its parent 1 is smaller, it stays: [1, 4, 3].",
                        "Push 2: it lands at index 3, below 4, and climbs: [1, 2, 3, 4]. Its new parent 1 is smaller, stop.",
                        "The result is <strong>[1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Does this always give the same array as sift-down?",
                     "No. Both give a valid heap, but not always the same one: for [3, 2, 1] pushing gives [1, 3, 2] while sift-down gives [1, 2, 3]."],
                    ["Why <code>nums[:] = out</code> and not <code>nums = out</code>?",
                     "Slice assignment changes the caller's list in place. Rebinding the name would only change the local variable."],
                    ["What does the library do for an existing list?",
                     "<code>heapq.heapify</code> uses the bottom-up sift-down method, the O(n) one."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth largest element
    "kth-largest-element": {
        "examples": [
            {"call": "find_kth_largest([3, 2, 1, 5, 6, 4], 2)", "expect": "5"},
            {"call": "find_kth_largest([3, 1, 3, 2], 2)", "expect": "3"},
        ],
        "approaches": {
            "Min-heap of size k": {
                "idea": [
                    "Keep the k largest values seen so far in a <em>min</em>-heap.",
                    "Its root is the smallest of those k, which is exactly the k-th largest so far.",
                    "When the heap grows to k + 1 values, the root can no longer be in the top k, so pop it.",
                ],
                "steps": [
                    "Start with an empty list <code>heap</code>.",
                    "For each <code>value</code>, <code>heapq.heappush(heap, value)</code>.",
                    "If <code>len(heap) &gt; k</code>, <code>heapq.heappop(heap)</code> removes the smallest of the k + 1.",
                    "After the loop, return <code>heap[0]</code>.",
                ],
                "why": [
                    "Invariant: after each step the heap holds the k largest values of the prefix seen so far, duplicates included.",
                    "At the end that prefix is the whole array, and the smallest of the top k is the k-th largest.",
                    "Each push and pop is O(log k): <strong>O(n log k)</strong> time and <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "Push 3, 2: heap {2, 3}. Push 1: three values, pop 1: {2, 3}.",
                        "Push 5: pop 2, giving {3, 5}. Push 6: pop 3, giving {5, 6}.",
                        "Push 4: pop 4 itself, giving {5, 6}.",
                        "The root is <strong>5</strong>.",
                    ],
                    [
                        "Push 3, 1: heap {1, 3}.",
                        "Push 3: heap {1, 3, 3}, pop 1: {3, 3}. Both copies of 3 stay.",
                        "Push 2: pop 2 itself, {3, 3}.",
                        "The root is <strong>3</strong>: duplicates count separately.",
                    ],
                ],
                "faq": [
                    ["Why a <em>min</em>-heap for the k <em>largest</em>?",
                     "The value you need to throw away is the smallest of the candidates, and a min-heap gives it in O(log k)."],
                    ["Do duplicates need special care?",
                     "No. The k-th largest counts duplicates, as in [3, 1, 3, 2] where both 3s are in the top 2, and the heap keeps both copies."],
                    ["Could I use <code>heappushpop</code>?",
                     "Yes, once the heap has k values, <code>heappushpop</code> does the push and pop in one sift, and skips the work when the new value is not larger than the root."],
                ],
            },
            "nlargest / sorting": {
                "idea": [
                    "Ask the library for the k largest values, largest first, and take the last of them.",
                    "<code>heapq.nlargest</code> is the size-k heap idea packaged as one call.",
                    "Sorting the whole array and indexing <code>[-k]</code> gives the same answer at full sorting cost.",
                ],
                "steps": [
                    "Call <code>heapq.nlargest(k, nums)</code>, which returns a list of k values in descending order.",
                    "Its last element, index <code>-1</code>, is the k-th largest.",
                    "Return it.",
                    "The library handles duplicates the same way: equal values are separate entries.",
                ],
                "why": [
                    "The k largest values in descending order end with the k-th largest, by definition.",
                    "<code>nlargest</code> runs a size-k heap internally, about O(n log k); when k ≥ n it simply sorts, so <strong>O(n log n)</strong> is the safe bound.",
                    "It builds a list of k values, or a sorted copy when k ≥ n: <strong>O(n)</strong> space in the worst case.",
                ],
                "dry": [
                    [
                        "<code>nlargest(2, [3, 2, 1, 5, 6, 4])</code> returns [6, 5].",
                        "The last element is 5.",
                        "The result is <strong>5</strong>.",
                    ],
                    [
                        "<code>nlargest(2, [3, 1, 3, 2])</code> returns [3, 3].",
                        "Both copies of 3 are kept as separate entries.",
                        "The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Is using the library acceptable in an interview?",
                     "Say it first as the one-liner, then expect to be asked how it works. The size-k heap or quickselect is what is being tested."],
                    ["Why not <code>sorted(nums)[-k]</code>?",
                     "That works too, but sorts all n values when only the top k matter."],
                    ["What if I need the k-th <em>distinct</em> largest?",
                     "Then deduplicate first, for example <code>heapq.nlargest(k, set(nums))</code>. This problem does not ask for that."],
                ],
            },
            "Quickselect": {
                "idea": [
                    "Partition the array around a pivot, as in quicksort, so that every smaller value ends up on its left.",
                    "The pivot then sits at its final sorted position. If that is the target position <code>n - k</code>, it is the answer; otherwise only the side containing the target needs more work.",
                    "A random pivot makes the expected work n + n/2 + n/4 + … = O(n).",
                ],
                "steps": [
                    "Set <code>target = len(nums) - k</code>, work on a copy of <code>nums</code>, and keep the live range <code>lo</code>..<code>hi</code>.",
                    "Pick a random <code>pivot</code> index in the range and swap it to <code>hi</code>.",
                    "Walk <code>i</code> from <code>lo</code> to <code>hi - 1</code>: every value smaller than <code>nums[hi]</code> is swapped to position <code>store</code>, and <code>store</code> advances.",
                    "Swap the pivot into <code>store</code>. Now everything left of <code>store</code> is smaller and everything right is ≥ the pivot.",
                    "If <code>store == target</code>, return <code>nums[store]</code>; if it is smaller, set <code>lo = store + 1</code>; otherwise <code>hi = store - 1</code>.",
                ],
                "why": [
                    "After partitioning, the pivot's index is its rank in sorted order, so the side that cannot contain the target can be discarded.",
                    "Each round costs the size of the current range. With random pivots the range shrinks geometrically on average: <strong>O(n)</strong> expected time; a run of bad pivots gives the O(n²) worst case.",
                    "The partition itself needs <strong>O(1)</strong> extra space; the defensive copy <code>list(nums)</code> adds O(n), which you can drop if mutating the input is allowed.",
                ],
                "dry": [
                    [
                        "target = 6 − 2 = 4. The pivot is random; this is one possible run.",
                        "Say the pivot is 4 (index 5): 3, 2, 1 are smaller and move to the front, giving [3, 2, 1, 4, 6, 5] with store = 3.",
                        "3 &lt; 4, so lo = 4 and only [6, 5] is left.",
                        "Say the pivot is 5: 6 is not smaller, so 5 lands at store = 4: [3, 2, 1, 4, 5, 6].",
                        "store equals the target, so the result is <strong>5</strong>.",
                    ],
                    [
                        "target = 4 − 2 = 2. Again one possible run.",
                        "Say the pivot is 2 (index 3): only 1 is smaller, giving [1, 2, 3, 3] with store = 1.",
                        "1 &lt; 2, so lo = 2 and the range is the two 3s.",
                        "Say the pivot is the 3 at index 2: the other 3 is not strictly smaller, so the pivot lands at store = 2.",
                        "store equals the target, so the result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the target index <code>n - k</code>?",
                     "In ascending order the largest value is at n − 1, the second largest at n − 2, so the k-th largest is at n − k."],
                    ["Why a random pivot?",
                     "A fixed pivot such as the last element hits the O(n²) case on sorted input. A random one makes that astronomically unlikely."],
                    ["What about many equal values?",
                     "With the strict <code>&lt;</code> all copies of the pivot stay on the right, so an array of all-equal values degrades towards O(n²). A three-way partition fixes that."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth largest in a stream
    "kth-largest-in-stream": {
        "examples": [
            {"setup": "kth = KthLargest(3, [4, 5, 8, 2])",
             "call": "[kth.add(v) for v in (3, 5, 10, 9, 4)]", "expect": "[4, 5, 5, 8, 8]"},
            {"setup": "kth = KthLargest(2, [0])",
             "call": "[kth.add(v) for v in (-1, 7, 3)]", "expect": "[-1, 0, 3]"},
        ],
        "approaches": {
            "Min-heap capped at k": {
                "idea": [
                    "This is the size-k min-heap from the previous problem, kept alive between calls.",
                    "Each new score is pushed; if there are now more than k, the smallest is dropped. The root is always the k-th highest.",
                    "Memory stays O(k) no matter how long the stream runs.",
                ],
                "steps": [
                    "The constructor copies <code>nums</code> into <code>self.heap</code> and calls <code>heapq.heapify</code>.",
                    "It then pops while <code>len(self.heap) &gt; k</code>, leaving the k largest initial values.",
                    "<code>add(val)</code> pushes <code>val</code>.",
                    "If the heap now has more than <code>self.k</code> values, pop the smallest.",
                    "Return <code>self.heap[0]</code>.",
                ],
                "why": [
                    "Invariant: the heap holds the k largest values seen so far (or all of them while fewer than k exist), so its root is the k-th largest.",
                    "The constructor costs O(n) for heapify plus O((n − k) log n) for the pops. Each <code>add</code> is <strong>O(log k)</strong>.",
                    "The heap never holds more than k + 1 values: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "Constructor: heapify [4, 5, 8, 2], pop 2, keeping {4, 5, 8}.",
                        "add(3): push, pop 3, root 4. add(5): pop 4, {5, 5, 8}, root 5.",
                        "add(10): pop 5, {5, 8, 10}, root 5.",
                        "add(9): pop 5, {8, 9, 10}, root 8. add(4): pop 4, root 8.",
                        "The result is <strong>[4, 5, 5, 8, 8]</strong>.",
                    ],
                    [
                        "Constructor: the heap is [0], already no more than k = 2, nothing is popped.",
                        "add(−1): push, the heap {−1, 0} has exactly 2 values, no pop: root −1.",
                        "add(7): {−1, 0, 7}, pop −1: root 0.",
                        "add(3): {0, 3, 7}, pop 0: root 3.",
                        "The result is <strong>[−1, 0, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["What if the initial list has fewer than k values?",
                     "The heap simply starts short. LeetCode guarantees that by the time <code>add</code> returns there are at least k values, as in the second example."],
                    ["Why heapify first instead of pushing the initial values one by one?",
                     "Heapify builds the heap in O(n). Pushing would be O(n log n), though both are correct."],
                    ["Why not keep a max-heap of everything?",
                     "Finding the k-th largest in a max-heap needs k pops each time. The capped min-heap keeps the answer at the root."],
                ],
            },
            "Sorted list with bisect": {
                "idea": [
                    "Keep every score in a sorted list; the k-th highest is then simply <code>data[-k]</code>.",
                    "<code>bisect.insort</code> finds the place in O(log n) with binary search, then inserts.",
                    "The catch is the insert itself: every element after the slot has to shift one place.",
                ],
                "steps": [
                    "The constructor stores <code>self.k</code> and <code>self.data = sorted(nums)</code>.",
                    "<code>add(val)</code> calls <code>bisect.insort(self.data, val)</code>.",
                    "Return <code>self.data[-self.k]</code>.",
                    "Nothing is ever removed, so the list grows with the stream.",
                ],
                "why": [
                    "The list stays sorted after every insert, so the element k from the end is the k-th largest.",
                    "Binary search is O(log n) but the shift is O(n): <strong>O(n)</strong> per add, with n the number of values seen so far.",
                    "It keeps every value: <strong>O(n)</strong> space, against O(k) for the heap.",
                ],
                "dry": [
                    [
                        "Start: [2, 4, 5, 8].",
                        "add 3: [2, 3, 4, 5, 8], data[−3] = 4. add 5: [2, 3, 4, 5, 5, 8], data[−3] = 5.",
                        "add 10: [2, 3, 4, 5, 5, 8, 10], data[−3] = 5.",
                        "add 9: the last three are 8, 9, 10, so 8. add 4: still 8.",
                        "The result is <strong>[4, 5, 5, 8, 8]</strong>.",
                    ],
                    [
                        "Start: [0].",
                        "add −1: [−1, 0], data[−2] = −1.",
                        "add 7: [−1, 0, 7], data[−2] = 0. add 3: [−1, 0, 3, 7], data[−2] = 3.",
                        "The result is <strong>[−1, 0, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>insort</code> O(log n)?",
                     "Only the search is. Inserting into a Python list shifts the tail, which is O(n)."],
                    ["Could I trim the list to its top k?",
                     "Yes: values below the k-th largest are never needed again. Then it is O(k) per add, still worse than the heap's O(log k)."],
                    ["When is this approach handy?",
                     "When you also need other ranks, such as the median or the 2nd largest, from the same structure."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ top k frequent
    "top-k-frequent": {
        "examples": [
            {"call": "sorted(top_k_frequent([5, 1, 5, 2, 1, 5, 3, 1, 5], 2))", "expect": "[1, 5]"},
            {"call": "sorted(top_k_frequent([-1, -1, 2, 2, 3], 2))", "expect": "[-1, 2]"},
        ],
        "approaches": {
            "Count, then a size-k heap": {
                "idea": [
                    "Count every value, then find the k values with the largest counts.",
                    "That is \"top k\" again: a min-heap of size k keyed on count keeps the k most frequent seen so far.",
                    "Tuples <code>(freq, value)</code> compare by frequency first, so the heap root is the least frequent candidate.",
                ],
                "steps": [
                    "<code>counts = Counter(nums)</code>.",
                    "For each <code>value, freq</code> in <code>counts.items()</code>, push <code>(freq, value)</code>.",
                    "If <code>len(heap) &gt; k</code>, pop the root, the least frequent of the k + 1.",
                    "Return <code>[value for freq, value in heap]</code>, in heap order, not sorted.",
                ],
                "why": [
                    "The heap always holds the k most frequent of the distinct values processed so far, by the same argument as for the k-th largest.",
                    "Counting is O(n); with d distinct values the heap work is O(d log k): <strong>O(n log k)</strong> at most.",
                    "The counter holds d entries and the heap k + 1: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Counts: 5→4, 1→3, 2→1, 3→1.",
                        "Push (4, 5) and (3, 1).",
                        "Push (1, 2): three entries, pop (1, 2). Push (1, 3): pop it again.",
                        "The heap holds 1 and 5. Sorted: <strong>[1, 5]</strong>.",
                    ],
                    [
                        "Counts: −1→2, 2→2, 3→1.",
                        "Push (2, −1) and (2, 2).",
                        "Push (1, 3): three entries, pop (1, 3).",
                        "The heap holds −1 and 2. Sorted: <strong>[−1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the tuple need the value in it?",
                     "To know which value to return. As a bonus, equal frequencies are then broken by comparing values, which are numbers and compare fine."],
                    ["Why wrap the call in <code>sorted</code>?",
                     "The problem accepts the answer in any order, and the heap's order is an implementation detail."],
                    ["Can ties at the k-th place cause trouble?",
                     "LeetCode guarantees the answer is unique, so there is never a tie across the boundary."],
                ],
            },
            "Bucket by frequency": {
                "idea": [
                    "A frequency can be at most n, so make n + 1 buckets and put each value in the bucket for its count.",
                    "Walk the buckets from the highest count down, collecting values until k have been found.",
                    "This is a counting sort on the frequencies, with no log factor.",
                ],
                "steps": [
                    "<code>counts = Counter(nums)</code> and <code>buckets = [[] for _ in range(len(nums) + 1)]</code>.",
                    "For each <code>value, freq</code>, append <code>value</code> to <code>buckets[freq]</code>.",
                    "Loop <code>freq</code> from <code>len(buckets) - 1</code> down to 1.",
                    "Append each value in that bucket to <code>out</code>; return as soon as <code>len(out) == k</code>.",
                ],
                "why": [
                    "Buckets are visited in decreasing frequency, so the first k values collected are the k most frequent.",
                    "Counting, filling and walking are each linear: <strong>O(n)</strong> time.",
                    "The buckets and the counter take <strong>O(n)</strong> space. This only works because frequencies are integers bounded by n.",
                ],
                "dry": [
                    [
                        "n = 9, buckets 0..9: bucket 4 = [5], bucket 3 = [1], bucket 1 = [2, 3].",
                        "Walk down from 9: buckets 9 to 5 are empty.",
                        "Bucket 4 gives 5; bucket 3 gives 1, and len(out) = 2 = k, so return.",
                        "out = [5, 1]. Sorted: <strong>[1, 5]</strong>.",
                    ],
                    [
                        "n = 5: bucket 2 = [−1, 2], bucket 1 = [3].",
                        "Buckets 5, 4, 3 are empty.",
                        "Bucket 2 gives −1, then 2, and k = 2 is reached inside the bucket.",
                        "out = [−1, 2]. Sorted: <strong>[−1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>len(nums) + 1</code> buckets?",
                     "A frequency can be anything from 1 to n inclusive, so index n must exist. Bucket 0 is never used."],
                    ["Why stop at bucket 1 and not 0?",
                     "Every counted value appears at least once, so bucket 0 is always empty."],
                    ["Is the final <code>return out</code> ever reached?",
                     "Only if k exceeds the number of distinct values, which the problem rules out. It is there as a safe fallback."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sort characters by frequency
    "sort-by-frequency": {
        "examples": [
            {"call": 'frequency_sort("bcacccb")', "expect": '"ccccbba"'},
            {"call": 'frequency_sort("Aaabbb")', "expect": '"bbbaaA"'},
        ],
        "approaches": {
            "Count, then max-heap": {
                "idea": [
                    "Count each character, then output the characters from the most frequent down, each repeated by its count.",
                    "Python only has a min-heap, so push <code>(-freq, ch)</code>: the most frequent character then has the smallest key.",
                    "Repeating a character with <code>ch * freq</code> writes its whole block at once.",
                ],
                "steps": [
                    "<code>counts = Counter(s)</code>.",
                    "Build <code>heap = [(-freq, ch) for ch, freq in counts.items()]</code> and heapify it.",
                    "Pop <code>(freq, ch)</code> until the heap is empty; <code>freq</code> is negative here.",
                    "Append <code>ch * -freq</code> to <code>out</code>, then return <code>\"\".join(out)</code>.",
                ],
                "why": [
                    "Pops come out in increasing <code>-freq</code>, which is decreasing frequency, so blocks are written most frequent first.",
                    "Counting is O(n); heapify and d pops over d distinct characters cost O(d log d): <strong>O(n + d log d)</strong> time.",
                    "The counter, heap and output pieces take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Counts: b→2, c→4, a→1. The heap holds (−2, b), (−4, c), (−1, a).",
                        "Pop (−4, c): \"cccc\".",
                        "Pop (−2, b): \"bb\". Pop (−1, a): \"a\".",
                        "The result is <strong>\"ccccbba\"</strong>.",
                    ],
                    [
                        "Counts: A→1, a→2, b→3. Upper and lower case are different characters.",
                        "Pop (−3, b): \"bbb\". Pop (−2, a): \"aa\".",
                        "Pop (−1, A): \"A\".",
                        "The result is <strong>\"bbbaaA\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why negate the frequency?",
                     "<code>heapq</code> pops the smallest key. Negating flips the order, turning it into a max-heap on frequency."],
                    ["How are ties ordered?",
                     "By the character, since tuples compare element by element: for \"tree\" this gives \"eert\". Any order of tied blocks is accepted."],
                    ["Why not append one character at a time?",
                     "That works but takes n pushes and pops. Writing a whole block per pop keeps the heap work at d pops."],
                ],
            },
            "most_common": {
                "idea": [
                    "<code>Counter.most_common()</code> already returns the (character, count) pairs sorted by count, highest first.",
                    "So the whole answer is one join over that list, with no heap and no negation to get wrong.",
                    "It is the same algorithm as the heap version with the sorting hidden in the library.",
                ],
                "steps": [
                    "<code>Counter(s)</code> counts the characters.",
                    "<code>.most_common()</code> with no argument sorts all pairs by count, descending.",
                    "Build <code>ch * freq</code> for each pair.",
                    "Join the pieces into one string and return it.",
                ],
                "why": [
                    "Blocks are emitted in order of decreasing count, which is exactly what is asked.",
                    "Counting is O(n) and sorting the d pairs is O(d log d): <strong>O(n + d log d)</strong> time.",
                    "The counter and the output take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "<code>Counter(\"bcacccb\").most_common()</code> gives [(c, 4), (b, 2), (a, 1)].",
                        "The pieces are \"cccc\", \"bb\", \"a\".",
                        "The result is <strong>\"ccccbba\"</strong>.",
                    ],
                    [
                        "<code>most_common()</code> gives [(b, 3), (a, 2), (A, 1)].",
                        "The pieces are \"bbb\", \"aa\", \"A\".",
                        "The result is <strong>\"bbbaaA\"</strong>.",
                    ],
                ],
                "faq": [
                    ["How does <code>most_common</code> order ties?",
                     "Stably, by first appearance in the string. For \"tree\" it gives \"eetr\" where the heap gives \"eert\"; both are valid answers."],
                    ["Is this allowed in an interview?",
                     "Usually yes, but be ready to say it sorts the counts in O(d log d) and to write the heap or bucket version."],
                    ["Can this be O(n)?",
                     "Yes, with buckets indexed by frequency as in Top K Frequent Elements, since a count is at most n."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sort a nearly sorted array
    "sort-nearly-sorted": {
        "examples": [
            {"call": "sort_k_sorted([6, 5, 3, 2, 8, 10, 9], 3)", "expect": "[2, 3, 5, 6, 8, 9, 10]"},
            {"call": "sort_k_sorted([2, 1, 4, 3], 1)", "expect": "[1, 2, 3, 4]"},
        ],
        "approaches": {
            "Sliding min-heap of size k+1": {
                "idea": [
                    "Every element is at most k places from its sorted position, so the smallest remaining value is always among the next k + 1 elements.",
                    "Keep exactly those k + 1 candidates in a min-heap: the root is the next output.",
                    "Each time one value leaves, the next unread element joins, so the heap slides along the array.",
                ],
                "steps": [
                    "Copy the first k + 1 elements into <code>heap</code> and heapify it.",
                    "For each <code>i</code> from <code>k + 1</code> to the end, <code>heapq.heappushpop(heap, nums[i])</code> pushes the new element and pops the smallest.",
                    "Append the popped value to <code>out</code>.",
                    "When the input is used up, pop the remaining heap values in order and append them.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "The value that belongs at output position j sits at an input index ≤ j + k, and by then all of those indices have entered the heap, so the root is the correct next value.",
                    "Each <code>heappushpop</code> costs O(log k): <strong>O(n log k)</strong> time.",
                    "The heap holds k + 1 values: <strong>O(k)</strong> extra space beyond the output.",
                ],
                "dry": [
                    [
                        "Heap of the first 4: [6, 5, 3, 2] heapifies to root 2.",
                        "i=4: push 8, pop 2. i=5: push 10, pop 3.",
                        "i=6: push 9, pop 5. out = [2, 3, 5].",
                        "Drain the heap {6, 8, 9, 10} in order.",
                        "The result is <strong>[2, 3, 5, 6, 8, 9, 10]</strong>.",
                    ],
                    [
                        "k = 1, so the heap holds 2 values: [2, 1] heapifies to [1, 2].",
                        "i=2: push 4, pop 1; heap {2, 4}.",
                        "i=3: push 3, pop 2; heap {3, 4}.",
                        "Drain: 3, 4. The result is <strong>[1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why k + 1 values and not k?",
                     "The element that belongs at position 0 can be at any index from 0 to k, which is k + 1 positions. A heap of k could miss it."],
                    ["Why <code>heappushpop</code> rather than push then pop?",
                     "It does both in one sift and returns at once when the new value is smaller than the root. The result is the same."],
                    ["What happens if the input is not really k-sorted?",
                     "The output can come out unsorted, because a small value arriving late is emitted after larger ones already left."],
                ],
            },
            "Just sort it": {
                "idea": [
                    "Ignore the k-sorted guarantee and sort the whole array.",
                    "It is always correct, whatever k is and even if the guarantee is false.",
                    "It is the baseline the heap approach improves on when k is much smaller than n.",
                ],
                "steps": [
                    "Call <code>sorted(nums)</code>, which returns a new list.",
                    "Return it.",
                    "<code>k</code> is not used at all.",
                    "The input list is left unchanged.",
                ],
                "why": [
                    "A full sort produces the sorted order by definition.",
                    "Comparison sorting is <strong>O(n log n)</strong>. Timsort spots runs and does well on nearly sorted data, but that is not a guarantee in terms of k.",
                    "<code>sorted</code> makes a new list: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "<code>sorted([6, 5, 3, 2, 8, 10, 9])</code>.",
                        "k = 3 is ignored.",
                        "The result is <strong>[2, 3, 5, 6, 8, 9, 10]</strong>.",
                    ],
                    [
                        "<code>sorted([2, 1, 4, 3])</code>.",
                        "k = 1 is ignored.",
                        "The result is <strong>[1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is this a wrong answer in an interview?",
                     "No, it is correct. It just does not use the information you were given; the question is testing whether you can get O(n log k)."],
                    ["When is the difference large?",
                     "When k is tiny compared with n, for example k = 2 on a million values: log k is about 1 against log n ≈ 20."],
                    ["What about a stream that does not fit in memory?",
                     "Then sorting is impossible, while the heap only ever needs k + 1 values at a time."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge k sorted arrays
    "merge-k-sorted-arrays": {
        "examples": [
            {"call": "merge_k_arrays([[1, 4, 5], [1, 3, 4], [2, 6]])", "expect": "[1, 1, 2, 3, 4, 4, 5, 6]"},
            {"call": "merge_k_arrays([[2, 5], [], [1, 3]])", "expect": "[1, 2, 3, 5]"},
        ],
        "approaches": {
            "Min-heap of one cursor per array": {
                "idea": [
                    "The next output value is always one of the k current fronts, one per array.",
                    "Keep those fronts in a min-heap as <code>(value, which, idx)</code>: the root is the smallest front.",
                    "After taking it, advance that array's cursor and push its next value, so each array always has one representative.",
                ],
                "steps": [
                    "Build <code>heap = [(a[0], i, 0) for i, a in enumerate(arrays) if a]</code>, skipping empty arrays, and heapify it.",
                    "Pop <code>(value, which, idx)</code> and append <code>value</code> to <code>out</code>.",
                    "If <code>idx + 1 &lt; len(arrays[which])</code>, push <code>(arrays[which][idx + 1], which, idx + 1)</code>.",
                    "Repeat while the heap is not empty, then return <code>out</code>.",
                ],
                "why": [
                    "Every unread value is ≥ its own array's front, so the smallest front is the smallest unread value overall.",
                    "Each of the N values is pushed and popped once in a heap of at most k entries: <strong>O(N log k)</strong> time.",
                    "The heap holds at most k cursors: <strong>O(k)</strong> extra space beyond the output.",
                ],
                "dry": [
                    [
                        "Start: heap {(1, 0, 0), (1, 1, 0), (2, 2, 0)}.",
                        "Pop 1 from array 0, push 4. Pop 1 from array 1, push 3. Pop 2 from array 2, push 6.",
                        "Pop 3 (array 1), push 4. Pop 4 (array 0), push 5. Pop 4 (array 1), which is now finished.",
                        "Pop 5 and then 6; each array is finished and the heap empties.",
                        "The result is <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                    ],
                    [
                        "The empty middle array is skipped: heap {(2, 0, 0), (1, 2, 0)}.",
                        "Pop 1 (array 2), push 3. Pop 2 (array 0), push 5.",
                        "Pop 3; array 2 is finished. Pop 5; array 0 is finished.",
                        "The result is <strong>[1, 2, 3, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store <code>which</code> and <code>idx</code> in the tuple?",
                     "To know which array to advance after a pop. <code>which</code> also breaks ties between equal values so the tuples always compare."],
                    ["Why skip empty arrays at the start?",
                     "<code>a[0]</code> would raise an IndexError on an empty array, and an empty array contributes nothing anyway."],
                    ["Is <code>heapq.merge</code> the same thing?",
                     "Yes, <code>list(heapq.merge(*arrays))</code> runs this same heap-of-fronts merge lazily."],
                ],
            },
            "Concatenate and sort": {
                "idea": [
                    "Pour every array into one list and sort it.",
                    "It throws away the fact that each array is already sorted.",
                    "It is short and always correct, which makes it a good reference answer.",
                ],
                "steps": [
                    "Start with an empty list <code>out</code>.",
                    "For each array <code>a</code>, <code>out.extend(a)</code>; empty arrays add nothing.",
                    "Return <code>sorted(out)</code>.",
                    "N is the total number of values across all arrays.",
                ],
                "why": [
                    "Sorting all values gives the merged order by definition.",
                    "Sorting N values is <strong>O(N log N)</strong>, against O(N log k) for the heap. Timsort does merge the existing runs well in practice.",
                    "The combined list holds every value: <strong>O(N)</strong> space.",
                ],
                "dry": [
                    [
                        "After extending: [1, 4, 5, 1, 3, 4, 2, 6].",
                        "Sort it.",
                        "The result is <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                    ],
                    [
                        "After extending: [2, 5, 1, 3]; the empty array added nothing.",
                        "Sort it.",
                        "The result is <strong>[1, 2, 3, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["When is the gap between N log N and N log k large?",
                     "When there are few arrays with many values each: with k = 2, log k is 1."],
                    ["Does it handle an empty input list?",
                     "Yes: nothing is extended and <code>sorted([])</code> is []."],
                    ["Why mention this one at all?",
                     "It is the obvious first answer and the reference the heap version is tested against."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge k sorted lists
    "merge-k-sorted-lists": {
        "examples": [
            {"call": "list_vals(merge_k_lists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]))",
             "expect": "[1, 1, 2, 3, 4, 4, 5, 6]"},
            {"call": "list_vals(merge_k_lists([build_list([2, 2]), build_list([2, 2])]))", "expect": "[2, 2, 2, 2]"},
        ],
        "approaches": {
            "Min-heap of list heads": {
                "idea": [
                    "Same as merging k arrays: the next node is always one of the k current heads.",
                    "Keep the heads in a min-heap as <code>(node.val, i, node)</code> and splice the smallest onto the result.",
                    "The list index <code>i</code> sits between value and node so that equal values never make Python compare two nodes.",
                ],
                "steps": [
                    "Build <code>heap = [(node.val, i, node) for i, node in enumerate(lists) if node]</code> and heapify it.",
                    "Create a <code>dummy</code> node and a <code>tail</code> pointer at it.",
                    "Pop <code>(value, i, node)</code>, link <code>tail.next = node</code> and move <code>tail = node</code>.",
                    "If <code>node.next</code> exists, push <code>(node.next.val, i, node.next)</code>.",
                    "When the heap is empty, set <code>tail.next = None</code> and return <code>dummy.next</code>.",
                ],
                "why": [
                    "The smallest head is the smallest remaining node overall, because each list is sorted.",
                    "Each of the N nodes is pushed and popped once in a heap of at most k: <strong>O(N log k)</strong> time.",
                    "Nodes are relinked, not copied; the heap holds at most k entries: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "Start: heap {(1, 0), (1, 1), (2, 2)} as (value, list).",
                        "Pop 1 from list 0 (push 4), 1 from list 1 (push 3), 2 from list 2 (push 6).",
                        "Pop 3 (push 4 from list 1), 4 from list 0 (push 5), 4 from list 1 (end of that list).",
                        "Pop 5, then 6. Each pop was linked after <code>tail</code>.",
                        "The result is <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                    ],
                    [
                        "Start: heap {(2, 0, a1), (2, 1, b1)}; the values tie, so the index decides.",
                        "Pop (2, 0, a1), push (2, 0, a2). The heap now ties (2, 0) against (2, 1) and pops a2 next.",
                        "List 0 is finished. Pop b1, push b2, pop b2.",
                        "No two nodes were ever compared. The result is <strong>[2, 2, 2, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong without <code>i</code> in the tuple?",
                     "When two values tie, Python compares the next elements, the nodes, and raises <code>TypeError: '&lt;' not supported between instances of 'ListNode'</code>."],
                    ["Why the dummy node?",
                     "It gives <code>tail</code> somewhere to start, so the first node needs no special case."],
                    ["Is <code>tail.next = None</code> needed?",
                     "The last node popped is the end of its own list, so its <code>next</code> is already None; the line just makes the termination explicit."],
                ],
            },
            "Merge pairwise, halving each round": {
                "idea": [
                    "Merging two sorted lists is easy and linear. Merge the lists in pairs, then merge the results in pairs, like the levels of merge sort.",
                    "Each round halves the number of lists, so there are only log k rounds.",
                    "Every node takes part in one merge per round.",
                ],
                "steps": [
                    "Drop empty lists; if none remain, return None.",
                    "While more than one list remains, build <code>merged</code> by calling <code>merge_two(lists[i], lists[i + 1])</code> for i = 0, 2, 4, ...",
                    "An odd list out at the end is carried into <code>merged</code> unchanged.",
                    "<code>merge_two</code> walks both lists with a dummy and a tail, taking <code>a</code> when <code>a.val &lt;= b.val</code>, and appends the leftover with <code>tail.next = a or b</code>.",
                    "Return <code>lists[0]</code>.",
                ],
                "why": [
                    "Each <code>merge_two</code> returns a sorted list containing exactly the nodes of its inputs, so every round preserves sortedness and the set of nodes.",
                    "There are about log k rounds and each touches all N nodes once: <strong>O(N log k)</strong> time.",
                    "Nodes are relinked in place; only the list of heads is kept, so space is <strong>O(1)</strong> extra nodes (plus O(k) for the head list).",
                ],
                "dry": [
                    [
                        "Three lists: round 1 merges [1, 4, 5] with [1, 3, 4] into [1, 1, 3, 4, 4, 5]; [2, 6] is carried over.",
                        "Round 2 merges [1, 1, 3, 4, 4, 5] with [2, 6].",
                        "In that merge, 2 slots in after the two 1s and 6 is appended as the leftover.",
                        "One list remains. The result is <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                    ],
                    [
                        "Two lists, so one round with a single <code>merge_two</code>.",
                        "Both heads are 2; <code>a.val &lt;= b.val</code> takes from the first list, twice.",
                        "The first list is used up and the second is attached with <code>tail.next = a or b</code>.",
                        "The result is <strong>[2, 2, 2, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not merge the lists one after another into a growing result?",
                     "The growing result is re-walked for every list, which costs O(N · k). Pairing keeps every node at only log k merges."],
                    ["Why <code>&lt;=</code> in <code>merge_two</code>?",
                     "Taking from <code>a</code> on ties keeps the merge stable. With <code>&lt;</code> the output values are the same."],
                    ["When would I choose this over the heap?",
                     "When you want no heap at all or no tuple tie-breaking. Both are O(N log k)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ smallest range
    "smallest-range-k-lists": {
        "examples": [
            {"call": "smallest_range([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]])", "expect": "[20, 24]"},
            {"call": "smallest_range([[1, 2, 3], [1, 2, 3], [1, 2, 3]])", "expect": "[1, 1]"},
        ],
        "approaches": {
            "k-way merge tracking the window": {
                "idea": [
                    "Pick one value from each list. The range that covers them is [smallest pick, largest pick].",
                    "To shrink it, the only useful move is to raise the smallest pick: lowering the largest is impossible without dropping a list.",
                    "So run a k-way merge: a min-heap gives the smallest pick, and a variable <code>largest</code> tracks the largest one.",
                ],
                "steps": [
                    "Push <code>(row[0], i, 0)</code> for every list, heapify, and set <code>largest</code> to the biggest first element.",
                    "Start with <code>best = (heap[0][0], largest)</code>.",
                    "Pop the smallest pick <code>(value, which, idx)</code>. If <code>largest - value</code> is smaller than the width of <code>best</code>, record <code>(value, largest)</code>.",
                    "If that list has no next element, return <code>list(best)</code>: the minimum can no longer move up.",
                    "Otherwise push the next element of the same list and raise <code>largest</code> if needed.",
                ],
                "why": [
                    "When a list's current value is the minimum, any range that keeps it is no tighter than the one just measured, so advancing that list loses nothing.",
                    "Each step moves one cursor forward, so at most N heap operations of O(log k): <strong>O(N log k)</strong> time.",
                    "The heap holds one entry per list: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "Start: picks 4, 0, 5, so largest = 5 and best = (0, 5).",
                        "Pop 0 (width 5, not smaller), push 9. Pop 4 (width 5), push 10. Pop 5 (width 5), push 18.",
                        "Pop 9, 10, 12 (largest 18, widths 9, 8, 6), pushing 12, 15, 20.",
                        "Pop 15 (largest 20, width 5), push 24. Pop 18 (largest 24, width 6), push 22.",
                        "Pop 20: width 24 − 20 = 4 &lt; 5, best = (20, 24). List 1 is exhausted, so return <strong>[20, 24]</strong>.",
                    ],
                    [
                        "Start: picks 1, 1, 1, largest = 1, best = (1, 1) with width 0.",
                        "Pop the three 1s in turn; each time width 1 or 2 is not smaller than 0. Push the 2s.",
                        "Pop the three 2s; largest is now 3, nothing beats width 0. Push the 3s.",
                        "Pop 3 from list 0: it is the last element, so stop.",
                        "The result is <strong>[1, 1]</strong>, found before the loop even started.",
                    ],
                ],
                "faq": [
                    ["Why stop as soon as one list runs out?",
                     "Every remaining range must still contain a value from that list, and its last value is the one just popped. The minimum can never rise again, so no tighter range is coming."],
                    ["Why the strict <code>&lt;</code> when comparing widths?",
                     "Equal widths prefer the smaller start, and popped values only increase, so the first range found with a given width has the smallest start."],
                    ["Why measure the range after the pop rather than after the push?",
                     "The popped value is still part of the current picks at that moment. After the push it has been replaced."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth smallest in a sorted matrix
    "kth-smallest-in-sorted-matrix": {
        "examples": [
            {"call": "kth_smallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8)", "expect": "13"},
            {"call": "kth_smallest([[1, 2], [1, 3]], 2)", "expect": "1"},
        ],
        "approaches": {
            "k-way merge over the rows": {
                "idea": [
                    "Each row is a sorted list, so the matrix is n sorted lists. Merging them in order, the k-th value produced is the answer.",
                    "A min-heap of row fronts <code>(value, r, c)</code> produces values in order.",
                    "Pop k − 1 times; the root is then the k-th smallest.",
                ],
                "steps": [
                    "Push <code>(matrix[r][0], r, 0)</code> for the first <code>min(k, n)</code> rows and heapify.",
                    "Repeat <code>k - 1</code> times: pop <code>(value, r, c)</code>.",
                    "If <code>c + 1 &lt; n</code>, push the next value in that row, <code>(matrix[r][c + 1], r, c + 1)</code>.",
                    "Return <code>heap[0][0]</code>.",
                ],
                "why": [
                    "This is a k-way merge, so values leave the heap in sorted order; after k − 1 pops the root is the k-th.",
                    "Rows past the k-th cannot hold any of the k smallest, because their first value is ≥ the first value of each row above, so they are never loaded.",
                    "Each pop and push is O(log n): <strong>O(k log n)</strong> time and <strong>O(n)</strong> space for the heap.",
                ],
                "dry": [
                    [
                        "Start: heap {1 (r0), 10 (r1), 12 (r2)}.",
                        "Pop 1, push 5. Pop 5, push 9. Pop 9; row 0 is finished.",
                        "Pop 10, push 11. Pop 11, push 13 (r1).",
                        "Pop 12, push 13 (r2). Pop 13 (r1). That is 7 pops.",
                        "The root is 13 (r2), so the result is <strong>13</strong>.",
                    ],
                    [
                        "k = 2, so <code>min(k, n)</code> = 2 rows: heap {(1, 0, 0), (1, 1, 0)}.",
                        "One pop: (1, 0, 0); push (2, 0, 1).",
                        "The root is now (1, 1, 0).",
                        "The result is <strong>1</strong>: the duplicate 1 counts as the 2nd smallest.",
                    ],
                ],
                "faq": [
                    ["Why only <code>min(k, n)</code> rows?",
                     "Row r starts with a value ≥ the starts of rows 0..r−1, so row k and beyond hold at least k values ≤ theirs. They cannot contain the k-th smallest."],
                    ["Why pop k − 1 times and then peek?",
                     "After removing the k − 1 smallest, the smallest remaining is the k-th, and it sits at the root."],
                    ["Does it use the fact that columns are sorted?",
                     "Only to justify skipping rows. The binary-search approach uses both orderings more fully."],
                ],
            },
            "Binary search on the value": {
                "idea": [
                    "Instead of searching positions, search values: the answer is the smallest value <code>x</code> with at least k entries ≤ x.",
                    "That count is monotonic in x, so binary search over the range from <code>matrix[0][0]</code> to <code>matrix[n-1][n-1]</code> works.",
                    "Counting entries ≤ x takes O(n) by walking a staircase from the bottom-left corner.",
                ],
                "steps": [
                    "Set <code>lo = matrix[0][0]</code> and <code>hi = matrix[n - 1][n - 1]</code>.",
                    "While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code> and compute <code>count_le(matrix, mid)</code>.",
                    "If the count is below k, the answer is larger: <code>lo = mid + 1</code>. Otherwise <code>hi = mid</code>.",
                    "<code>count_le</code> starts at the bottom-left: if <code>matrix[r][c] &lt;= target</code> the whole column above it counts (<code>r + 1</code>) and <code>c</code> moves right; otherwise <code>r</code> moves up.",
                    "Return <code>lo</code>.",
                ],
                "why": [
                    "The search keeps the invariant that the answer lies in [lo, hi]; it stops at the smallest x with count ≥ k, and that x must be a matrix value, since a smaller count would hold for x − 1 otherwise.",
                    "The staircase walk moves up or right each step, at most 2n steps: O(n) per count.",
                    "The search takes log(hi − lo) rounds: <strong>O(n log(hi − lo))</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo = 1, hi = 15. mid = 8: entries ≤ 8 are 1, 5, so count 2 &lt; 8: lo = 9.",
                        "mid = 12: count 6 (1, 5, 9, 10, 11, 12) &lt; 8: lo = 13.",
                        "mid = 14: count 8 ≥ 8: hi = 14.",
                        "mid = 13: count 8 ≥ 8: hi = 13.",
                        "lo = hi = 13, so the result is <strong>13</strong>.",
                    ],
                    [
                        "lo = 1, hi = 3. mid = 2: entries ≤ 2 are 1, 2, 1, count 3 ≥ 2: hi = 2.",
                        "mid = 1: count 2 (both 1s) ≥ 2: hi = 1.",
                        "lo = hi = 1.",
                        "The result is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the result not be a value missing from the matrix?",
                     "If x is not in the matrix, then count(x − 1) = count(x). The search finds the smallest x with count ≥ k, so x − 1 would already qualify unless x is present."],
                    ["Why start the staircase at the bottom-left?",
                     "From there one direction only increases (right) and the other only decreases (up), so each comparison safely eliminates a whole row or column."],
                    ["Does this work with negative values?",
                     "Yes. <code>//</code> floors towards −∞, so <code>mid</code> stays in [lo, hi) and the loop always shrinks."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth smallest sum of a matrix with sorted rows
    "kth-smallest-matrix-row-sums": {
        "examples": [
            {"call": "kth_smallest([[1, 3, 11], [2, 4, 6]], 5)", "expect": "7"},
            {"call": "kth_smallest([[1, 1, 10], [2, 2, 9]], 5)", "expect": "10"},
        ],
        "approaches": {
            "Merge one row at a time, keeping k": {
                "idea": [
                    "Choosing one value per row and summing is like adding rows one at a time: the sums so far, plus each value of the next row.",
                    "Only the k smallest partial sums can ever lead to the k smallest final sums, so after each row keep just those k.",
                    "<code>heapq.nsmallest</code> does the trimming in one call.",
                ],
                "steps": [
                    "Start with <code>sums = [0]</code>: the empty choice.",
                    "For each <code>row</code>, form every <code>s + v</code> with <code>s</code> in <code>sums</code> and <code>v</code> in <code>row</code>.",
                    "Keep <code>sums = heapq.nsmallest(k, ...)</code> of those, already in ascending order.",
                    "After the last row, return <code>sums[-1]</code>, the k-th smallest.",
                ],
                "why": [
                    "A partial sum outside the k smallest has at least k partial sums ≤ it, and each of those can be extended by the same remaining choices, so it is never needed for the top k.",
                    "Each row produces at most k · n candidates and <code>nsmallest</code> keeps k of them: <strong>O(m · k · n log k)</strong> time over m rows.",
                    "The kept list has k sums; the candidates are streamed from a generator: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "Row [1, 3, 11]: sums = [1, 3, 11].",
                        "Row [2, 4, 6]: the 9 candidates are 3, 5, 7, 5, 7, 9, 13, 15, 17.",
                        "The 5 smallest are [3, 5, 5, 7, 7].",
                        "The last one is <strong>7</strong>.",
                    ],
                    [
                        "Row [1, 1, 10]: sums = [1, 1, 10]; the two 1s are separate choices.",
                        "Row [2, 2, 9]: candidates 3, 3, 10 (from the first 1), 3, 3, 10 (second 1), 12, 12, 19.",
                        "The 5 smallest are [3, 3, 3, 3, 10].",
                        "The last one is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must duplicates be kept?",
                     "Each sum is a different choice of indices. The four ways to make 3 in the second example are four separate arrays, so they occupy four ranks."],
                    ["Why start from <code>[0]</code>?",
                     "It is the sum of choosing nothing, so the first row's values become the first partial sums without a special case."],
                    ["How big can the candidate list get?",
                     "k · n per row: at most k kept sums times n values. With k ≤ 200 and n ≤ 40 on LeetCode, that is small."],
                ],
            },
            "Best-first search over index tuples": {
                "idea": [
                    "A choice is a tuple of column indices, one per row. The smallest sum is all zeros, because rows are sorted.",
                    "From any tuple, the next-larger candidates come from bumping one row's index by one, so explore tuples in order of sum with a min-heap, like Dijkstra.",
                    "A <code>seen</code> set stops the same tuple being reached from two parents and counted twice.",
                ],
                "steps": [
                    "Push <code>(first, start)</code>, where <code>start</code> is all zeros and <code>first</code> is the sum of the first column; add <code>start</code> to <code>seen</code>.",
                    "Repeat <code>k - 1</code> times: pop the smallest <code>(total, idx)</code>.",
                    "For each row <code>r</code> with <code>idx[r] + 1 &lt; n</code>, build <code>nxt</code> with that index bumped.",
                    "If <code>nxt</code> is new, add it to <code>seen</code> and push it with sum <code>total - mat[r][idx[r]] + mat[r][idx[r] + 1]</code>.",
                    "Return <code>heap[0][0]</code>, the k-th smallest sum.",
                ],
                "why": [
                    "Bumping an index never lowers the sum, so every tuple's sum is ≥ its parent's and the heap pops tuples in non-decreasing order of sum.",
                    "Every tuple except the start has a parent with one index lower, so every tuple is eventually reachable and none is skipped.",
                    "Each pop pushes up to m tuples of length m: <strong>O(k · m log(k · m))</strong>, about O(k · m log k) time (plus O(m) to build each tuple), and <strong>O(k · m)</strong> space for the heap and <code>seen</code>.",
                ],
                "dry": [
                    [
                        "Start: (3, (0, 0)).",
                        "Pop 3 (0, 0): push (5, (1, 0)) and (5, (0, 1)).",
                        "Pop 5 (0, 1): push (7, (1, 1)) and (7, (0, 2)). Pop 5 (1, 0): push (13, (2, 0)); (1, 1) is already seen.",
                        "Pop 7 (0, 2): push (9, (1, 2)). That is 4 pops.",
                        "The root is (7, (1, 1)), so the result is <strong>7</strong>.",
                    ],
                    [
                        "Start: (3, (0, 0)).",
                        "Pop 3 (0, 0): push (3, (1, 0)) and (3, (0, 1)).",
                        "Pop 3 (0, 1): push (3, (1, 1)) and (10, (0, 2)). Pop 3 (1, 0): push (12, (2, 0)).",
                        "Pop 3 (1, 1): push (12, (2, 1)) and (10, (1, 2)). Four 3s have been popped.",
                        "The root is (10, (0, 2)), so the result is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["What breaks without the <code>seen</code> set?",
                     "Tuple (1, 1) is reached from both (0, 1) and (1, 0) and gets counted twice. On the first example with k = 6 that returns 7 instead of 9."],
                    ["Why update the sum instead of recomputing it?",
                     "Swapping one row's value is O(1); re-adding all m values would be O(m)."],
                    ["Why does a tie in sum compare the tuples?",
                     "Heap entries are <code>(total, idx)</code>, so equal totals fall back to comparing index tuples, which is harmless and always defined."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ connect sticks
    "connect-sticks": {
        "examples": [
            {"call": "connect_sticks([1, 8, 3, 5])", "expect": "30"},
            {"call": "connect_sticks([2, 2, 3, 3])", "expect": "20"},
        ],
        "approaches": {
            "Always merge the two shortest": {
                "idea": [
                    "A stick's length is paid again every time the stick it is part of is joined, so short sticks should be joined early and long ones late.",
                    "That is Huffman coding: always join the two shortest sticks available, including sticks made by earlier joins.",
                    "A min-heap hands out the two shortest in O(log n) each.",
                ],
                "steps": [
                    "Copy the sticks into <code>heap</code> and heapify it.",
                    "While more than one stick remains, pop the two shortest, <code>a</code> and <code>b</code>.",
                    "Add <code>a + b</code> to <code>total</code>: that is the cost of this join.",
                    "Push the new stick <code>a + b</code> back into the heap.",
                    "Return <code>total</code>; a single stick costs 0.",
                ],
                "why": [
                    "In an optimal sequence the two shortest sticks can always be swapped into the first join without raising the cost, which is the exchange argument behind Huffman's algorithm.",
                    "There are n − 1 joins, each with two pops and a push: <strong>O(n log n)</strong> time.",
                    "The heap copy holds up to n sticks: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Heap {1, 3, 5, 8}.",
                        "Join 1 + 3 = 4: total 4, heap {4, 5, 8}.",
                        "Join 4 + 5 = 9: total 13, heap {8, 9}.",
                        "Join 8 + 9 = 17: total 30, heap {17}.",
                        "The result is <strong>30</strong>.",
                    ],
                    [
                        "Heap {2, 2, 3, 3}.",
                        "Join 2 + 2 = 4: total 4, heap {3, 3, 4}.",
                        "Join 3 + 3 = 6: the new 4 is <em>not</em> the shortest, so it waits. Total 10, heap {4, 6}.",
                        "Join 4 + 6 = 10: total 20.",
                        "The result is <strong>20</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not keep adding the next shortest original stick to one growing stick?",
                     "The growing stick gets paid on every join. On [2, 2, 3, 3] that gives 4 + 7 + 10 = 21, while joining 3 + 3 separately gives 20."],
                    ["Why can't I just sort once?",
                     "Joined sticks have new lengths that must be compared with the rest. A heap keeps the order up to date as sticks are added."],
                    ["What is the cost of one stick or none?",
                     "No joins are needed, so the loop never runs and the answer is 0."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ task scheduler
    "task-scheduler": {
        "examples": [
            {"call": 'least_interval(["A", "A", "A", "B", "B", "B"], 2)', "expect": "8"},
            {"call": 'least_interval(["A", "C", "A", "B", "D", "B"], 1)', "expect": "6"},
        ],
        "approaches": {
            "Counting formula": {
                "idea": [
                    "The most frequent task decides the shape: its <code>most</code> copies need gaps of n between them, which makes <code>most - 1</code> full frames of length n + 1, plus a last partial frame.",
                    "Every task tied for the maximum also has a copy in that last frame, so it has length <code>tied</code>.",
                    "If there are enough other tasks to overflow the frames, there are no idle slots at all and the answer is just <code>len(tasks)</code>.",
                ],
                "steps": [
                    "<code>counts = Counter(tasks)</code> and <code>most = max(counts.values())</code>.",
                    "<code>tied</code> = how many tasks have count <code>most</code>.",
                    "The frame bound is <code>(most - 1) * (n + 1) + tied</code>.",
                    "Return <code>max(len(tasks), (most - 1) * (n + 1) + tied)</code>.",
                ],
                "why": [
                    "Lower bound: the most frequent task needs <code>most - 1</code> gaps of n, and every tied task finishes after its own last copy, giving the frame length; and every task takes one slot, giving <code>len(tasks)</code>.",
                    "Both bounds are achievable: fill the frames round-robin, and when tasks overflow them, widen frames instead of idling, so the larger bound is the answer.",
                    "Counting is <strong>O(n)</strong> over the task list; at most 26 distinct letters makes space <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "Counts: A→3, B→3, so most = 3, tied = 2.",
                        "Frames: (3 − 1) · (2 + 1) + 2 = 8, laid out as A B _ A B _ A B.",
                        "len(tasks) = 6.",
                        "max(6, 8) = <strong>8</strong>.",
                    ],
                    [
                        "Counts: A→2, C→1, B→2, D→1, so most = 2, tied = 2.",
                        "Frames: (2 − 1) · (1 + 1) + 2 = 4.",
                        "But there are 6 tasks, more than the 4 frame slots, so no idling is ever needed.",
                        "max(6, 4) = <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>n + 1</code> and not n?",
                     "A frame is one copy of the frequent task plus the n slots that must pass before it can run again."],
                    ["Why add <code>tied</code> instead of 1?",
                     "Every task with the maximum count still has a copy left after the last full frame, so all of them run at the end."],
                    ["When does <code>len(tasks)</code> win?",
                     "When the other tasks are enough to fill every gap, as in the second example or whenever n = 0. Then nothing idles."],
                ],
            },
            "Max-heap with a cooldown queue": {
                "idea": [
                    "Simulate the CPU one time unit at a time, always running the task with the most copies left: that keeps the frequent tasks from piling up at the end.",
                    "A max-heap (negated counts) holds tasks that are ready to run.",
                    "A FIFO queue holds tasks that are cooling down, with the time they become ready again.",
                ],
                "steps": [
                    "Build <code>heap = [-c for c in Counter(tasks).values()]</code> and heapify it; <code>time = 0</code>, <code>cooling</code> is an empty deque.",
                    "While the heap or the queue has anything, advance <code>time</code> by 1.",
                    "If the heap is not empty, pop the biggest count and add 1 (counts are negative). If copies remain, append <code>(time + n, remaining)</code> to <code>cooling</code>.",
                    "If the front of <code>cooling</code> is ready at this <code>time</code>, push its count back into the heap.",
                    "Return <code>time</code>; units where the heap was empty were idle.",
                ],
                "why": [
                    "Running the most remaining task first is the same greedy as the frames in the formula, and it never idles while a ready task exists.",
                    "Tasks enter the queue in time order with the same delay, so the front is always the next to become ready: a deque is enough.",
                    "Each time unit costs O(log 26): <strong>O(N)</strong> over the answer's length, and the heap and queue hold at most 26 counts: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Counts −3, −3. t=1: run A, cooling (3, A×2). t=2: run B, cooling (4, B×2).",
                        "t=3: nothing ready, idle; A becomes ready at the end of t=3.",
                        "t=4: run A, cooling (6, A×1); B returns. t=5: run B. t=6: idle, A returns.",
                        "t=7: run A (done). B returns. t=8: run B (done).",
                        "Both structures are empty: <strong>8</strong>.",
                    ],
                    [
                        "Counts: A 2, C 1, B 2, D 1, n = 1.",
                        "t=1: run a task with 2 copies, it cools until t=2. t=2: run the other 2-copy task; the first returns at the end of t=2.",
                        "t=3 to t=6: the heap always has a ready task, so there is never an idle slot.",
                        "All six tasks have run at t=6: <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>time + n</code> as the ready time?",
                     "The check happens at the end of each time unit, so a task stored with <code>time + n</code> rejoins after n more units and can run again at <code>time + n + 1</code>, exactly n units later."],
                    ["Why can the queue be checked only at its front?",
                     "Every task waits the same n units and enters in time order, so ready times in the queue are increasing."],
                    ["Why does the loop run while <code>cooling</code> is non-empty even when the heap is empty?",
                     "Those are idle units: tasks are still waiting, and time must pass until they become ready."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reorganize string
    "reorganize-string": {
        "examples": [
            {"call": 'reorganize_string("aaabc")', "expect": '"abaca"'},
            {"call": 'reorganize_string("aaab")', "expect": '""'},
        ],
        "approaches": {
            "Max-heap, always take two": {
                "idea": [
                    "It is impossible exactly when one character has more than <code>(len(s) + 1) // 2</code> copies: even alternating it with everything else cannot separate them.",
                    "Otherwise, repeatedly write the two most frequent remaining characters. They differ, and taking the two largest stops any count from dominating later.",
                    "A max-heap of <code>(-count, ch)</code> gives the two most frequent in O(log 26).",
                ],
                "steps": [
                    "Count with <code>Counter</code>; if the largest count exceeds <code>(len(s) + 1) // 2</code>, return <code>\"\"</code>.",
                    "Build and heapify <code>heap = [(-c, ch)]</code>.",
                    "While at least two entries remain, pop <code>(c1, ch1)</code> and <code>(c2, ch2)</code>, append <code>ch1</code> then <code>ch2</code>.",
                    "Push each back with its count reduced, <code>c + 1</code> on the negated value, if it is not yet zero.",
                    "If one entry is left, append its character once. Join and return.",
                ],
                "why": [
                    "Each pair writes two different characters. The next pair starts with the most frequent remaining character, which is never the previous pair's second one: that one had a count no larger than the first, and on a tie the heap's tie-break by character puts the first one ahead again.",
                    "With the feasibility check passed, the leftover entry always has exactly one copy, so the final append is safe.",
                    "There are about n/2 rounds of O(log 26): <strong>O(n)</strong> time, and <strong>O(n)</strong> space for the output.",
                ],
                "dry": [
                    [
                        "Counts a→3, b→1, c→1; 3 ≤ (5 + 1) // 2 = 3, so it is feasible.",
                        "Pop (−3, a), (−1, b): write \"ab\", push back (−2, a); b is used up.",
                        "Pop (−2, a), (−1, c): write \"ac\", push back (−1, a).",
                        "One entry left: write \"a\".",
                        "The result is <strong>\"abaca\"</strong>.",
                    ],
                    [
                        "Counts a→3, b→1, len 4.",
                        "3 &gt; (4 + 1) // 2 = 2, so three a's cannot be kept apart in 4 slots.",
                        "The heap is never built.",
                        "The result is <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>(len(s) + 1) // 2</code> the limit?",
                     "The best spacing puts a character in every other slot starting at 0, which gives ceil(len / 2) slots. One more copy must touch another."],
                    ["Why take two at a time and not one?",
                     "Taking one, you would need to remember the last character and hold it out of the heap. Taking two different ones per round does that automatically."],
                    ["Could the next pair start with the character that just ended the last pair?",
                     "No. Its count was at most the first character's and both dropped by one. On a tie, tuples compare by character, and the character that won the tie last round wins it again."],
                ],
            },
            "Fill even slots, then odd": {
                "idea": [
                    "Write characters into slots 0, 2, 4, ... and, when those run out, into slots 1, 3, 5, ... Copies of a character land two apart and never touch.",
                    "The most frequent character must go first, so it gets the even slots, which are the most numerous.",
                    "The same feasibility test decides when it is impossible.",
                ],
                "steps": [
                    "Count; return <code>\"\"</code> if the largest count exceeds <code>(len(s) + 1) // 2</code>.",
                    "Create <code>out = [\"\"] * len(s)</code> and set <code>i = 0</code>.",
                    "For each <code>ch, freq</code> in <code>counts.most_common()</code>, place <code>freq</code> copies.",
                    "Before each placement, if <code>i &gt;= len(s)</code>, switch to the odd slots with <code>i = 1</code>. Write <code>out[i] = ch</code> and step <code>i += 2</code>.",
                    "Join and return.",
                ],
                "why": [
                    "Placements follow the order 0, 2, 4, …, 1, 3, …, so consecutive copies of one character are two slots apart unless they wrap from the last even slot to slot 1.",
                    "A wrap can only make a character touch itself if it has more copies than the slots allow, and the most frequent one, placed first, fits in the evens by the feasibility check; any later character has fewer than half the slots.",
                    "Counting and filling are linear and <code>most_common</code> sorts at most 26 entries: <strong>O(n)</strong> time, <strong>O(n)</strong> space for <code>out</code>.",
                ],
                "dry": [
                    [
                        "most_common gives a→3, b→1, c→1.",
                        "a goes to slots 0, 2, 4: [a, _, a, _, a].",
                        "i = 6 ≥ 5, so i = 1: b goes to slot 1. Then c goes to slot 3.",
                        "The result is <strong>\"abaca\"</strong>.",
                    ],
                    [
                        "Counts a→3, b→1 in a string of length 4.",
                        "3 &gt; (4 + 1) // 2 = 2.",
                        "Nothing is placed.",
                        "The result is <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the most frequent character go first?",
                     "If a less frequent one took the early even slots, the frequent one could spill from the evens into the odds next to itself. For \"aab\" placing b first gives \"baa\"."],
                    ["Does the order after the first character matter?",
                     "No. Every other character has at most half the slots, and the two-apart spacing keeps its copies apart even across the wrap."],
                    ["Why is <code>i &gt;= len(s)</code> checked before writing, not after?",
                     "So the switch to slot 1 happens exactly when the next even slot does not exist, wherever that falls inside a character's run."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ IPO
    "ipo": {
        "examples": [
            {"call": "find_maximized_capital(2, 0, [1, 2, 3], [0, 1, 1])", "expect": "4"},
            {"call": "find_maximized_capital(1, 0, [1, 2, 3], [1, 1, 2])", "expect": "0"},
        ],
        "approaches": {
            "Two heaps: affordable by capital, best by profit": {
                "idea": [
                    "Capital only grows, so a project that is affordable now stays affordable forever.",
                    "Each round, among the projects you can afford, take the one with the biggest profit: it raises capital the most and unlocks the most for later.",
                    "Sort projects by required capital and move them into a max-heap of profits as capital passes their threshold.",
                ],
                "steps": [
                    "<code>projects = sorted(zip(capital, profits))</code>; <code>affordable</code> is a max-heap of negated profits; <code>i = 0</code>.",
                    "Repeat k times: while <code>projects[i][0] &lt;= w</code>, push <code>-projects[i][1]</code> and advance <code>i</code>.",
                    "If <code>affordable</code> is empty, break: nothing can be started and capital will not change.",
                    "Otherwise pop the largest profit and add it: <code>w -= heapq.heappop(affordable)</code>.",
                    "Return <code>w</code>.",
                ],
                "why": [
                    "Exchange argument: if an optimal plan picks a smaller affordable profit first, swapping in the largest leaves capital at least as high at every later step, so nothing it could do becomes impossible.",
                    "Sorting is O(n log n), and each project is pushed and popped at most once: <strong>O(n log n)</strong> time.",
                    "The sorted list and the heap take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "projects = [(0, 1), (1, 2), (1, 3)].",
                        "Round 1, w = 0: only (0, 1) is affordable. Take profit 1, w = 1.",
                        "Round 2, w = 1: (1, 2) and (1, 3) join the heap. Take profit 3, w = 4.",
                        "k = 2 rounds are done.",
                        "The result is <strong>4</strong>.",
                    ],
                    [
                        "projects = [(1, 1), (1, 2), (2, 3)].",
                        "Round 1, w = 0: every project needs at least 1, so nothing joins the heap.",
                        "The heap is empty: break.",
                        "The result is <strong>0</strong>, the starting capital.",
                    ],
                ],
                "faq": [
                    ["Why is the index <code>i</code> never reset?",
                     "Capital never falls, so a project moved into the heap stays affordable. Each project is moved at most once."],
                    ["Why break instead of continuing the loop?",
                     "With nothing affordable the capital cannot change, so later rounds would find the same empty heap."],
                    ["Why not pick the project with the best profit-to-capital ratio?",
                     "Capital is not spent: it is a threshold. Only the profit changes w, so the biggest affordable profit is the right choice."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ meeting rooms
    "meeting-rooms": {
        "examples": [
            {"call": "can_attend_meetings([[7, 10], [2, 4], [4, 7]])", "expect": "True"},
            {"call": "can_attend_meetings([[0, 30], [5, 10], [15, 20]])", "expect": "False"},
        ],
        "approaches": {
            "Sort by start, compare neighbours": {
                "idea": [
                    "One person can attend everything only if no two meetings overlap.",
                    "After sorting by start time, any overlap shows up between two <em>neighbouring</em> meetings, so one pass over neighbours is enough.",
                    "A meeting may start exactly when the previous one ends: touching is not overlapping.",
                ],
                "steps": [
                    "<code>intervals.sort()</code> orders the meetings by start time (then by end).",
                    "Loop <code>i</code> from 1 to the end.",
                    "If <code>intervals[i][0] &lt; intervals[i - 1][1]</code>, meeting i starts before the previous one ends: return <code>False</code>.",
                    "If the loop finishes, return <code>True</code>.",
                ],
                "why": [
                    "If any two meetings overlap, then in sorted order the later-starting one also overlaps its immediate predecessor, or the predecessor already overlapped an earlier one; either way some neighbouring pair fails.",
                    "Sorting dominates: <strong>O(n log n)</strong> time.",
                    "The list is sorted in place and the scan uses one index: <strong>O(1)</strong> extra space (Timsort may use up to O(n) internally).",
                ],
                "dry": [
                    [
                        "Sorted: [[2, 4], [4, 7], [7, 10]].",
                        "i=1: start 4 &lt; previous end 4? No, they only touch.",
                        "i=2: start 7 &lt; previous end 7? No.",
                        "No overlap: <strong>True</strong>.",
                    ],
                    [
                        "Sorted: [[0, 30], [5, 10], [15, 20]].",
                        "i=1: start 5 &lt; previous end 30. Overlap.",
                        "It returns <strong>False</strong> without looking at [15, 20].",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;</code> and not <code>&lt;=</code>?",
                     "A meeting ending at 5 and one starting at 5 do not overlap. With <code>&lt;=</code>, [[1, 5], [5, 9]] would wrongly be rejected."],
                    ["Why is checking neighbours enough?",
                     "Starts are sorted, so if meeting i does not overlap meeting i − 1, it starts after every earlier meeting has ended, provided those did not overlap each other either."],
                    ["Is sorting the caller's list a problem?",
                     "It mutates the input. Use <code>sorted(intervals)</code> if the caller still needs the original order, at the cost of O(n) space."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ meeting rooms II
    "meeting-rooms-ii": {
        "examples": [
            {"call": "min_meeting_rooms([[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]])", "expect": "4"},
            {"call": "min_meeting_rooms([[1, 5], [5, 9], [2, 4]])", "expect": "2"},
        ],
        "approaches": {
            "Min-heap of end times": {
                "idea": [
                    "Process meetings in order of start time and keep the end time of every room in use.",
                    "A new meeting can reuse a room only if some room is free, and the room that frees up first is the one with the smallest end time.",
                    "A min-heap of end times gives that room in O(log n); its final size is the number of rooms needed.",
                ],
                "steps": [
                    "Return 0 for no meetings; otherwise sort <code>intervals</code> by start.",
                    "For each <code>start, end</code>: if <code>ends</code> is non-empty and <code>ends[0] &lt;= start</code>, the earliest room is free, so pop it.",
                    "Push <code>end</code>: the meeting occupies either the reused room or a new one.",
                    "After the loop, return <code>len(ends)</code>.",
                ],
                "why": [
                    "The heap never shrinks below the number of meetings running at a given start, and a room is opened only when every room is busy at that moment, so its size is the peak overlap.",
                    "Popping at most one room per meeting is enough: one meeting needs only one room.",
                    "Sorting plus one push and at most one pop per meeting: <strong>O(n log n)</strong> time and <strong>O(n)</strong> space for the heap.",
                ],
                "dry": [
                    [
                        "Sorted by start. [1, 10]: new room, ends {10}. [2, 7]: 10 &gt; 2, new room, {7, 10}.",
                        "[3, 19]: 7 &gt; 3, new room, {7, 10, 19}.",
                        "[8, 12]: 7 ≤ 8, reuse: {10, 12, 19}. [10, 20]: 10 ≤ 10, reuse: {12, 19, 20}.",
                        "[11, 30]: 12 &gt; 11, new room: {12, 19, 20, 30}.",
                        "The heap has 4 rooms: <strong>4</strong>.",
                    ],
                    [
                        "Sorted: [1, 5], [2, 4], [5, 9].",
                        "[1, 5]: new room, {5}. [2, 4]: 5 &gt; 2, new room, {4, 5}.",
                        "[5, 9]: 4 ≤ 5, reuse the room that freed at 4: {5, 9}.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> when comparing with the earliest end?",
                     "A room that frees at 5 can host a meeting starting at 5. With <code>&lt;</code>, [[1, 5], [5, 9]] would need 2 rooms instead of 1."],
                    ["Why only pop one room per meeting?",
                     "Rooms that ended earlier but are not popped are still counted in the heap, but reusing one room is all a single meeting needs, and the final size is still the peak."],
                    ["Why sort by start rather than end?",
                     "Rooms are assigned as meetings begin. Processing starts in order guarantees that, when a meeting arrives, every earlier meeting has been placed."],
                ],
            },
            "Sweep the endpoints": {
                "idea": [
                    "The answer is the largest number of meetings running at the same instant.",
                    "Sort all starts and all ends separately and sweep through time: each start opens a room, each end closes one.",
                    "Which meeting ends does not matter, only how many have ended before each start.",
                ],
                "steps": [
                    "<code>starts</code> and <code>ends</code> are the sorted start and end times; <code>rooms = best = 0</code>, <code>j = 0</code>.",
                    "For each <code>start</code> in order, close every meeting with <code>ends[j] &lt;= start</code>: <code>rooms -= 1</code>, <code>j += 1</code>.",
                    "Then open a room for this meeting: <code>rooms += 1</code>.",
                    "Record <code>best = max(best, rooms)</code> and return <code>best</code>.",
                ],
                "why": [
                    "At each start, <code>rooms</code> equals the number of meetings started so far minus those that have ended, which is exactly the number running at that moment.",
                    "The peak overlap always occurs at some start time, so checking only starts is enough.",
                    "Two sorts dominate: <strong>O(n log n)</strong> time; the two sorted lists take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "starts = [1, 2, 3, 8, 10, 11], ends = [7, 10, 12, 19, 20, 30].",
                        "Starts 1, 2, 3: nothing has ended, rooms 1, 2, 3.",
                        "Start 8: end 7 closes (j=1), rooms 3. Start 10: end 10 closes (j=2), rooms 3.",
                        "Start 11: end 12 &gt; 11, nothing closes, rooms 4, best 4.",
                        "The result is <strong>4</strong>.",
                    ],
                    [
                        "starts = [1, 2, 5], ends = [4, 5, 9].",
                        "Starts 1 and 2: rooms 1, then 2; best = 2.",
                        "Start 5: ends 4 and 5 are both ≤ 5, so two rooms close, j = 2; then this meeting opens one: rooms 1.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Is it wrong to separate starts from their ends?",
                     "No. The count running at time t only depends on how many starts and how many ends are ≤ t, not on which start pairs with which end."],
                    ["Can <code>j</code> run off the end of <code>ends</code>?",
                     "No. The meeting being opened has its end after its start, so at most (meetings started so far − 1) ends can be ≤ the current start."],
                    ["Why close ends with <code>&lt;=</code>?",
                     "A meeting ending exactly when another starts frees its room in time, the same rule as in the heap version."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ refueling stops
    "refueling-stops": {
        "examples": [
            {"call": "min_refuel_stops(100, 10, [[10, 60], [20, 30], [30, 30], [60, 40]])", "expect": "2"},
            {"call": "min_refuel_stops(100, 1, [[10, 100]])", "expect": "-1"},
        ],
        "approaches": {
            "Max-heap of fuel already driven past": {
                "idea": [
                    "Drive as far as the current fuel allows, and remember every station passed on the way without deciding yet whether to stop there.",
                    "When you run dry, pretend you stopped at the passed station with the most fuel. That one choice extends the reach the most.",
                    "A max-heap of the passed stations' fuel makes that retroactive choice O(log n).",
                ],
                "steps": [
                    "<code>fuel</code> is how far you can reach; <code>stops = 0</code>, <code>i = 0</code>, and <code>passed</code> is a max-heap of negated fuel.",
                    "While <code>fuel &lt; target</code>, push every station with <code>stations[i][0] &lt;= fuel</code>: those are reachable.",
                    "If <code>passed</code> is empty, no station can extend the reach: return -1.",
                    "Otherwise pop the largest fuel amount, add it to <code>fuel</code>, and count a stop.",
                    "When <code>fuel &gt;= target</code>, return <code>stops</code>.",
                ],
                "why": [
                    "With s stops, the farthest reachable distance is the start fuel plus the s largest amounts among stations reachable on the way, and taking the largest available each time builds exactly that.",
                    "Each station is pushed and popped at most once: <strong>O(n log n)</strong> time.",
                    "The heap can hold every station: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "fuel = 10: station 10 is reachable, passed = {60}. 10 &lt; 100.",
                        "Pop 60: fuel = 70, stops = 1.",
                        "Stations at 20, 30, 60 are now reachable: passed = {30, 30, 40}. 70 &lt; 100.",
                        "Pop 40: fuel = 110 ≥ 100, stops = 2.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "fuel = 1: the station at 10 is out of reach, passed is empty.",
                        "1 &lt; 100 and nothing to pop.",
                        "The result is <strong>-1</strong>, even though that station alone holds enough fuel.",
                    ],
                ],
                "faq": [
                    ["Isn't it cheating to refuel at a station already behind you?",
                     "It is a bookkeeping trick. Choosing to stop there is decided later, but the car really did pass it with fuel to spare, so the plan is a real one."],
                    ["Why can <code>fuel</code> double as the position?",
                     "Starting at 0, total fuel collected is exactly how far the car can get, since 1 litre drives 1 mile."],
                    ["Why not stop at every station with more fuel than the last?",
                     "Greedy on the way can waste stops. Delaying the decision until you must refuel always picks the single best station available."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find median from data stream
    "find-median-from-data-stream": {
        "examples": [
            {"setup": "mf = MedianFinder()",
             "call": "[mf.add_num(x) or mf.find_median() for x in (5, 15, 1, 3)]", "expect": "[5.0, 10.0, 5.0, 4.0]"},
            {"setup": "mf = MedianFinder()",
             "call": "[mf.add_num(x) or mf.find_median() for x in (-1, -2, -3)]", "expect": "[-1.0, -1.5, -2.0]"},
        ],
        "approaches": {
            "Max-heap of the low half, min-heap of the high half": {
                "idea": [
                    "Split the numbers into a lower half and an upper half. The median only needs the top of the lower half and the bottom of the upper half.",
                    "Keep the lower half in a max-heap <code>small</code> (negated values) and the upper half in a min-heap <code>large</code>.",
                    "Keep <code>small</code> the same size as <code>large</code> or one bigger, so the median is always at the roots.",
                ],
                "steps": [
                    "<code>add_num</code>: push <code>-num</code> into <code>small</code>.",
                    "Move the largest of <code>small</code> into <code>large</code>: this keeps every value in <code>small</code> ≤ every value in <code>large</code>.",
                    "If <code>large</code> is now bigger than <code>small</code>, move its smallest back to <code>small</code>.",
                    "<code>find_median</code>: if <code>small</code> is bigger, return <code>float(-small[0])</code>; otherwise return the average of the two roots.",
                ],
                "why": [
                    "Routing every number through <code>small</code> and then into <code>large</code> keeps the order invariant: max(small) ≤ min(large).",
                    "The size rule puts the middle element (odd count) at the root of <code>small</code>, or the two middle elements at the two roots (even count).",
                    "<code>add_num</code> does up to three heap operations: <strong>O(log n)</strong>. <code>find_median</code> reads two roots: <strong>O(1)</strong>. The heaps hold every number: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "add 5: small {5}, large {}. Median 5.0.",
                        "add 15: it goes through small to large: small {5}, large {15}. Median (5 + 15) / 2 = 10.0.",
                        "add 1: 1 goes into small, 5 moves up, then large is bigger so 5 moves back: small {1, 5}, large {15}. Median 5.0.",
                        "add 3: 3 into small, 5 moves up: small {1, 3}, large {5, 15}. Median (3 + 5) / 2 = 4.0.",
                        "The result is <strong>[5.0, 10.0, 5.0, 4.0]</strong>.",
                    ],
                    [
                        "add −1: small {−1}. Median −1.0.",
                        "add −2: −2 goes into small, the larger −1 moves up: small {−2}, large {−1}. Median −1.5.",
                        "add −3: −3 into small, −2 moves up, large is bigger, so −2 moves back: small {−3, −2}, large {−1}.",
                        "Median −2.0. The result is <strong>[−1.0, −1.5, −2.0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why push into <code>small</code> first and then move its top?",
                     "It decides which half the new number belongs to without comparing it by hand: whatever is largest among small plus the new value is the one that must go up."],
                    ["Why negate values in <code>small</code>?",
                     "<code>heapq</code> is a min-heap only. Storing negatives makes its root the largest original value."],
                    ["Why <code>float</code> on the odd case?",
                     "So both branches return floats, which is what the tests compare against, for example 5.0 rather than 5."],
                ],
            },
            "Sorted list with bisect": {
                "idea": [
                    "Keep every number in a sorted list; the median is then one or two direct index reads.",
                    "<code>bisect.insort</code> finds the insert position by binary search.",
                    "The insert has to shift the tail of the list, which is what makes this slower than the heaps.",
                ],
                "steps": [
                    "<code>add_num</code>: <code>bisect.insort(self.data, num)</code>.",
                    "<code>find_median</code>: let <code>n = len(self.data)</code> and <code>mid = n // 2</code>.",
                    "If n is odd, return <code>float(self.data[mid])</code>.",
                    "Otherwise return the average of <code>data[mid - 1]</code> and <code>data[mid]</code>.",
                ],
                "why": [
                    "The list is always sorted, so the middle index holds the median by definition.",
                    "Binary search is O(log n) but shifting is O(n): <strong>O(n)</strong> per <code>add_num</code>, <strong>O(1)</strong> per <code>find_median</code>.",
                    "Every number is stored: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "add 5: [5], median 5.0.",
                        "add 15: [5, 15], median 10.0.",
                        "add 1: [1, 5, 15], median 5.0.",
                        "add 3: [1, 3, 5, 15], median (3 + 5) / 2 = 4.0.",
                        "The result is <strong>[5.0, 10.0, 5.0, 4.0]</strong>.",
                    ],
                    [
                        "add −1: [−1], median −1.0.",
                        "add −2: [−2, −1], median −1.5.",
                        "add −3: [−3, −2, −1], median −2.0.",
                        "The result is <strong>[−1.0, −1.5, −2.0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>mid - 1</code> and <code>mid</code> for an even count?",
                     "With n = 4, <code>mid = 2</code>, and the two middle elements are at indices 1 and 2."],
                    ["Is this good enough in practice?",
                     "For thousands of values the shift is a fast memory move and this is fine. For a heavy stream the heaps scale better."],
                    ["What if <code>find_median</code> is called far more often than <code>add_num</code>?",
                     "Both designs answer in O(1). The difference is only in the cost of adding."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sliding window median
    "sliding-window-median": {
        "examples": [
            {"call": "median_sliding_window([1, 3, -1, -3, 5], 3)", "expect": "[1.0, -1.0, -1.0]"},
            {"call": "median_sliding_window([1, 4, 2, 3], 2)", "expect": "[2.5, 3.0, 2.5]"},
        ],
        "approaches": {
            "Sorted window with bisect": {
                "idea": [
                    "Keep the current window as a sorted list; its median is read by index.",
                    "Sliding the window removes one value and inserts one, both found by binary search.",
                    "Both list operations shift elements, so each slide costs O(k).",
                ],
                "steps": [
                    "<code>window = sorted(nums[:k])</code>; <code>half = k // 2</code> and <code>odd = k % 2</code>.",
                    "<code>median()</code> returns <code>window[half]</code> for odd k, or the average of <code>window[half - 1]</code> and <code>window[half]</code>.",
                    "Record the first median.",
                    "For each <code>i</code> from k on, remove <code>nums[i - k]</code> with <code>window.pop(bisect_left(window, nums[i - k]))</code>, then <code>insort</code> <code>nums[i]</code>.",
                    "Append the new median; return <code>out</code>.",
                ],
                "why": [
                    "The window list always holds exactly the current k values in sorted order, so the median read is correct.",
                    "<code>bisect_left</code> finds some copy of the leaving value; removing any copy of an equal value leaves the same multiset.",
                    "Each slide is O(log k) to search plus O(k) to shift: <strong>O(n k)</strong> time and <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "window = [−1, 1, 3], median 1.0.",
                        "i=3: remove 1, insert −3: [−3, −1, 3], median −1.0.",
                        "i=4: remove 3, insert 5: [−3, −1, 5], median −1.0.",
                        "The result is <strong>[1.0, −1.0, −1.0]</strong>.",
                    ],
                    [
                        "k = 2, so the median is the average of the two values. window = [1, 4], median 2.5.",
                        "i=2: remove 1, insert 2: [2, 4], median 3.0.",
                        "i=3: remove 4, insert 3: [2, 3], median 2.5.",
                        "The result is <strong>[2.5, 3.0, 2.5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>bisect_left</code> to remove instead of <code>window.remove</code>?",
                     "<code>remove</code> scans from the left in O(k) comparisons. <code>bisect_left</code> finds the position in O(log k); the pop's shift is O(k) either way."],
                    ["Does removing the 'wrong' duplicate matter?",
                     "No. Equal values are interchangeable for the median."],
                    ["When is this the better choice?",
                     "When k is small, or in an interview where clarity matters more than the log factor. It is far simpler to get right than lazy deletion."],
                ],
            },
            "Two heaps with lazy deletion": {
                "idea": [
                    "Use the two-heap median idea, <code>small</code> (max-heap, negated) for the lower half and <code>large</code> for the upper half.",
                    "Heaps cannot delete an arbitrary value cheaply, so a leaving value is only recorded in <code>delayed</code> and thrown away later, when it reaches a root.",
                    "Because stale values may still sit inside the heaps, the real sizes are tracked separately in <code>n_small</code> and <code>n_large</code>.",
                ],
                "steps": [
                    "<code>add(value)</code>: push into <code>small</code> if it is ≤ the top of <code>small</code>, else into <code>large</code>; update the count and <code>rebalance()</code>.",
                    "<code>remove(value)</code>: increment <code>delayed[value]</code>, decrement the count of the half it belongs to, and <code>prune</code> that heap if the value is its root; then <code>rebalance()</code>.",
                    "<code>prune(heap)</code> pops roots while <code>delayed</code> says they were already deleted.",
                    "<code>rebalance()</code> moves roots between heaps until <code>n_small</code> equals <code>n_large</code> or exceeds it by one, pruning the heap that lost its root.",
                    "For each index, add the new value, remove <code>nums[i - k]</code> once the window is full, and read the median from the roots.",
                ],
                "why": [
                    "Every root is kept valid by pruning after any change that could expose a stale value, so the median read from roots is always over live values.",
                    "The counts, not <code>len</code>, decide balance, so stale values never skew the halves.",
                    "Each value is pushed, moved and popped a constant number of times, each O(log n): <strong>O(n log k)</strong> time when stale values are cleared regularly. The heaps and <code>delayed</code> hold <strong>O(k)</strong> live entries, though stale ones can linger.",
                ],
                "dry": [
                    [
                        "add 1, 3, −1: small {1, −1}, large {3}. First median: the top of small, 1.0.",
                        "i=3: add −3 to small; n_small = 3 &gt; 2, so 1 moves to large: small {−1, −3}, large {1, 3}.",
                        "remove 1: delayed[1] = 1; it belongs to large and is its root, so prune pops it: large {3}. Median −1.0.",
                        "i=4: add 5 to large: {3, 5}. remove 3: it is large's root, pruned: large {5}. Median −1.0.",
                        "The result is <strong>[1.0, −1.0, −1.0]</strong>.",
                    ],
                    [
                        "add 1, 4: small {1}, large {4}. Median 2.5.",
                        "i=2: add 2 to large, rebalance moves 2 to small: small {2, 1}. remove 1: delayed[1] = 1, n_small = 1, but 1 is not small's root, so it stays as a stale value. Median (2 + 4) / 2 = 3.0.",
                        "i=3: add 3 to large, rebalance moves 3 to small: small {3, 2, 1}, large {4}.",
                        "remove 4: large's root, pruned; large is empty and n_small = 2 &gt; 0 + 1, so 3 moves to large. Median (2 + 3) / 2 = 2.5.",
                        "The stale 1 is still inside small. The result is <strong>[2.5, 3.0, 2.5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just call <code>heap.remove(value)</code> and re-heapify?",
                     "Finding the value is O(k) and re-heapifying is O(k), which brings back the O(n k) cost the heaps were meant to avoid."],
                    ["How does <code>remove</code> know which heap the value is in?",
                     "Values ≤ the top of <code>small</code> belong to the lower half by the ordering invariant, so it compares with <code>-small[0]</code>, which is always live after pruning."],
                    ["Why prune after moving a root in <code>rebalance</code>?",
                     "Moving the root can expose a stale value underneath it, and the next median read or comparison must see a live root."],
                ],
            },
        },
    },
}
