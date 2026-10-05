"""Write-ups for the Heaps and Priority Queues topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ heapify
    "heapify": {
        "example": {"call": "heapify([5, 3, 8, 1, 9, 2])", "expect": "[1, 3, 2, 5, 9, 8]"},
        "approaches": {
            "Sift down from the last parent": {
                "idea": [
                    "A heap is an array read as a tree: the children of index i are at 2i+1 and 2i+2, and every parent must be ≤ its children.",
                    "Leaves (the second half of the array) are already valid one-element heaps.",
                    "Fix the parents from the last one back to the root, sifting each down below its smaller child until it fits.",
                ],
                "steps": [
                    "For i from <code>n // 2 - 1</code> down to 0, call <code>sift_down(i)</code>.",
                    "<code>sift_down</code>: find the smallest of i and its children; if it is not i, swap and continue from that child.",
                ],
                "why": [
                    "When i is sifted, both of its subtrees are already heaps, so a single sift fixes the subtree rooted at i.",
                    "Most nodes are near the bottom and move only a little: the total work is n·Σ k/2<sup>k+1</sup> = O(n), not O(n log n).",
                ],
                "dry": [
                    "Start: [5, 3, 8, 1, 9, 2]. The last parent is index 2.",
                    "i=2 (8): its child 2 is smaller, so swap: [5, 3, 2, 1, 9, 8].",
                    "i=1 (3): the smaller child is 1 (index 3), so swap: [5, 1, 2, 3, 9, 8].",
                    "i=0 (5): the smaller child is 1, so swap: [1, 5, 2, 3, 9, 8]. Continue at index 1: its child 3 is smaller, so swap: [1, 3, 2, 5, 9, 8].",
                    "The result is <strong>[1, 3, 2, 5, 9, 8]</strong>.",
                ],
            },
            "Push one at a time": {
                "idea": [
                    "Build the heap by inserting values one by one: each new value goes at the end and sifts <em>up</em> past larger parents.",
                    "This is the natural approach when values arrive one at a time, but for an existing array it is slower.",
                ],
                "steps": [
                    "For each value: <code>heapq.heappush(out, value)</code>.",
                    "Copy the result back.",
                ],
                "why": [
                    "Each push restores the heap property along one path.",
                    "Each insert can climb log n levels, and most values sit at the bottom: O(n log n).",
                ],
                "dry": [
                    "Push 5, 3, 8: [3, 5, 8].",
                    "Push 1: it goes in at index 3 and climbs past 5 and then 3: [1, 3, 8, 5].",
                    "Push 9: its parent 3 is smaller, so it stays: [1, 3, 8, 5, 9].",
                    "Push 2: it climbs past 8 and stops below 1: <strong>[1, 3, 2, 5, 9, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth largest element
    "kth-largest-element": {
        "example": {"call": "find_kth_largest([3, 2, 1, 5, 6, 4], 2)", "expect": "5"},
        "approaches": {
            "Min-heap of size k": {
                "idea": [
                    "Keep the k largest values seen so far in a <em>min</em>-heap.",
                    "Its root is the smallest of those k, which is exactly the k-th largest so far.",
                    "When a value arrives, push it; if the heap grows past k, pop the smallest, because it can no longer be in the top k.",
                ],
                "steps": [
                    "Push each value; whenever <code>len(heap) &gt; k</code>, pop.",
                    "Return <code>heap[0]</code>.",
                ],
                "why": [
                    "The heap always holds the top k of the prefix seen so far.",
                    "Each step is O(log k): O(n log k) time and O(k) space.",
                ],
                "dry": [
                    "Push 3, 2: {2, 3}. Push 1: three values, so pop 1: {2, 3}.",
                    "Push 5: pop 2, giving {3, 5}. Push 6: pop 3, giving {5, 6}.",
                    "Push 4: pop 4 itself, giving {5, 6}.",
                    "The root is <strong>5</strong>.",
                ],
            },
            "nlargest / sorting": {
                "idea": [
                    "Ask the library for the k largest values and take the last one.",
                ],
                "steps": [
                    "<code>heapq.nlargest(k, nums)[-1]</code>.",
                ],
                "why": [
                    "This is the same size-k heap idea behind a library call. Sorting everything would be O(n log n) for an answer that only needs one boundary.",
                ],
                "dry": [
                    "nlargest(2) gives [6, 5].",
                    "The last of them is <strong>5</strong>.",
                ],
            },
            "Quickselect": {
                "idea": [
                    "Partition the array around a pivot, as in quicksort, so that everything smaller is on its left.",
                    "The pivot then sits at its final sorted position. If that is the target position <code>n - k</code>, we are done; otherwise continue only on the side that contains the target.",
                    "A random pivot makes the expected work n + n/2 + n/4 + … = O(n).",
                ],
                "steps": [
                    "<code>target = n - k</code>.",
                    "Swap a random pivot to the end, move every smaller value to the front, and put the pivot at <code>store</code>.",
                    "Compare <code>store</code> with <code>target</code> and shrink <code>lo</code> or <code>hi</code>.",
                ],
                "why": [
                    "After partitioning, the pivot's index is its rank, so one side can be thrown away.",
                    "It is O(n) on average and O(n²) in the worst case, which a random pivot makes very unlikely; O(1) extra space.",
                ],
                "dry": [
                    "target = 6 - 2 = 4 (index 4 of the sorted array). The pivot is random; here is one possible run.",
                    "Say the pivot is 4: the smaller values 3, 2, 1 move to the front, giving [3, 2, 1, 4, 6, 5] with 4 at index 3.",
                    "3 &lt; 4, so search only [6, 5] (indices 4..5).",
                    "Say the pivot is 5: 6 is not smaller, so 5 lands at index 4, which is the target.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth largest in a stream
    "kth-largest-in-stream": {
        "example": {"setup": "kth = KthLargest(3, [4, 5, 8, 2])",
                    "call": "[kth.add(v) for v in (3, 5, 10, 9, 4)]", "expect": "[4, 5, 5, 8, 8]"},
        "approaches": {
            "Min-heap capped at k": {
                "idea": [
                    "This is the size-k min-heap from the previous problem, kept alive between calls.",
                    "Each new score is pushed; if there are now more than k, the smallest is dropped. The root is always the k-th highest.",
                    "Memory stays O(k) no matter how long the stream runs.",
                ],
                "steps": [
                    "Constructor: heapify the initial scores and pop down to k.",
                    "<code>add</code>: push, pop if over k, return <code>heap[0]</code>.",
                ],
                "why": [
                    "The heap is exactly the top k scores so far.",
                    "Each add is O(log k).",
                ],
                "dry": [
                    "Start: heapify [4, 5, 8, 2], then pop 2, keeping {4, 5, 8}.",
                    "add(3): push, then pop 3, so {4, 5, 8} with root <strong>4</strong>. add(5): pop 4, so {5, 5, 8} with root <strong>5</strong>.",
                    "add(10): pop 5, so {5, 8, 10} with root <strong>5</strong>.",
                    "add(9): pop 5, so {8, 9, 10} with root <strong>8</strong>. add(4): pop 4, root <strong>8</strong>.",
                    "The result is <strong>[4, 5, 5, 8, 8]</strong>.",
                ],
            },
            "Sorted list with bisect": {
                "idea": [
                    "Keep every score in a sorted list; the k-th highest is <code>data[-k]</code>.",
                    "<code>bisect.insort</code> finds the place in O(log n) but has to shift the elements after it.",
                ],
                "steps": [
                    "<code>insort(data, val)</code>, then return <code>data[-k]</code>.",
                ],
                "why": [
                    "Each add is O(n) because of the shift, and memory grows with the stream.",
                ],
                "dry": [
                    "Start: [2, 4, 5, 8].",
                    "add 3 gives [2, 3, 4, 5, 8], so data[-3] = <strong>4</strong>. add 5 gives [2, 3, 4, 5, 5, 8], so <strong>5</strong>.",
                    "add 10, so <strong>5</strong>. add 9: the last three are 8, 9, 10, so <strong>8</strong>.",
                    "add 4: still <strong>8</strong>. The result is <strong>[4, 5, 5, 8, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ top k frequent
    "top-k-frequent": {
        "example": {"call": "sorted(top_k_frequent([5, 1, 5, 2, 1, 5, 3, 1, 5], 2))", "expect": "[1, 5]"},
        "approaches": {
            "Count, then a size-k heap": {
                "idea": [
                    "Count every value, then find the k values with the largest counts.",
                    "That is \"top k\" again: a min-heap of size k keyed on count keeps the k most frequent seen so far.",
                ],
                "steps": [
                    "<code>counts = Counter(nums)</code>.",
                    "Push <code>(freq, value)</code>; pop when there are more than k.",
                    "Return the values left in the heap.",
                ],
                "why": [
                    "The heap always holds the k most frequent distinct values seen so far.",
                    "It is O(n) to count plus O(d log k) for d distinct values; O(n) space for the counter.",
                ],
                "dry": [
                    "Counts: 5→4, 1→3, 2→1, 3→1.",
                    "Push (4, 5) and (3, 1).",
                    "Push (1, 2): three entries, so pop (1, 2). Push (1, 3): pop it again.",
                    "The heap holds 1 and 5: <strong>[1, 5]</strong>.",
                ],
            },
            "Bucket by frequency": {
                "idea": [
                    "A count can be at most n, so make n + 1 buckets and put each value in the bucket for its count.",
                    "Walk the buckets from the highest count down, collecting values until k are found.",
                    "This is a counting sort on the frequency, with no log factor.",
                ],
                "steps": [
                    "<code>buckets[freq].append(value)</code>.",
                    "Walk from the top bucket down and stop at k values.",
                ],
                "why": [
                    "Buckets are visited in order of decreasing frequency, so the first k values collected are the most frequent.",
                    "It is O(n) time and O(n) space. It only works because counts are integers bounded by n.",
                ],
                "dry": [
                    "Buckets: 4 → [5], 3 → [1], 1 → [2, 3].",
                    "Walk down from 9: the first non-empty bucket is 4, which gives 5; bucket 3 gives 1, and k = 2 is reached.",
                    "Sorted: <strong>[1, 5]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sort characters by frequency
    "sort-by-frequency": {
        "example": {"call": 'frequency_sort("bcacccb")', "expect": '"ccccbba"'},
        "approaches": {
            "Count, then max-heap": {
                "idea": [
                    "Count each character, then output characters from the most frequent down, each repeated by its count.",
                    "Python only has a min-heap, so push <code>(-freq, char)</code> to make the most frequent come out first.",
                ],
                "steps": [
                    "<code>heap = [(-freq, ch)]</code>, then heapify.",
                    "Pop repeatedly and emit <code>ch * freq</code>.",
                ],
                "why": [
                    "Negating the key turns the min-heap into a max-heap.",
                    "It is O(n + d log d) for d distinct characters.",
                ],
                "dry": [
                    "Counts: c→4, b→2, a→1.",
                    "Popped in order: (-4, c), (-2, b), (-1, a).",
                    "Output: \"cccc\" + \"bb\" + \"a\" = <strong>\"ccccbba\"</strong>.",
                ],
            },
            "most_common": {
                "idea": [
                    "<code>Counter.most_common()</code> already returns the characters sorted by count, so there is no heap and no negation to get wrong.",
                ],
                "steps": [
                    "Join <code>ch * freq</code> over <code>most_common()</code>.",
                ],
                "why": [
                    "It has the same O(n + d log d) cost as the heap version and is shorter.",
                ],
                "dry": [
                    "most_common() gives [(c, 4), (b, 2), (a, 1)].",
                    "Joined: <strong>\"ccccbba\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sort a nearly sorted array
    "sort-nearly-sorted": {
        "example": {"call": "sort_k_sorted([6, 5, 3, 2, 8, 10, 9], 3)", "expect": "[2, 3, 5, 6, 8, 9, 10]"},
        "approaches": {
            "Sliding min-heap of size k+1": {
                "idea": [
                    "Every element is at most k places from its sorted position, so the smallest remaining value is always among the next k + 1 elements.",
                    "Keep those k + 1 in a min-heap: pop the root to output it, then push the next element.",
                ],
                "steps": [
                    "Heapify the first k + 1 elements.",
                    "For each later element: <code>heappushpop</code> it and output what pops out.",
                    "Drain the heap at the end.",
                ],
                "why": [
                    "The k-sorted guarantee makes the root the correct next output every time.",
                    "It is O(n log k) time and O(k) space.",
                ],
                "dry": [
                    "Heap of the first 4: {6, 5, 3, 2}, root 2.",
                    "8 in, 2 out. 10 in, 3 out. 9 in, 5 out.",
                    "Drain: 6, 8, 9, 10.",
                    "The result is <strong>[2, 3, 5, 6, 8, 9, 10]</strong>.",
                ],
            },
            "Just sort it": {
                "idea": [
                    "Ignore the k-sorted guarantee and sort.",
                ],
                "steps": [
                    "<code>sorted(nums)</code>.",
                ],
                "why": [
                    "It is O(n log n) time and O(n) space. Timsort runs close to linear on nearly sorted data, but it still needs the whole array in memory.",
                ],
                "dry": [
                    "sorted gives <strong>[2, 3, 5, 6, 8, 9, 10]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge k sorted arrays
    "merge-k-sorted-arrays": {
        "example": {"call": "merge_k_arrays([[1, 4, 5], [1, 3, 4], [2, 6]])", "expect": "[1, 1, 2, 3, 4, 4, 5, 6]"},
        "approaches": {
            "Min-heap of one cursor per array": {
                "idea": [
                    "The next value of the merged output is the smallest among the current front of each array.",
                    "A heap of <code>(value, array index, element index)</code>, one entry per array, gives that minimum in O(log k).",
                    "After popping, push the next element from the same array.",
                ],
                "steps": [
                    "Seed the heap with each array's first element.",
                    "Pop the minimum, output it, and advance that array's cursor.",
                ],
                "why": [
                    "The heap always holds each array's next unmerged value.",
                    "Each of the N elements is pushed and popped once: O(N log k) time and O(k) space.",
                ],
                "dry": [
                    "Seed: (1, a0), (1, a1), (2, a2).",
                    "Pop 1 (a0), push 4. Pop 1 (a1), push 3. Pop 2 (a2), push 6.",
                    "Pop 3, push 4. Pop 4 (a0), push 5. Pop 4 (a1). Pop 5. Pop 6.",
                    "The result is <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                ],
            },
            "Concatenate and sort": {
                "idea": [
                    "Pour every array into one list and sort it, ignoring that each input is already sorted.",
                ],
                "steps": [
                    "<code>out.extend(a)</code> for each array, then <code>sorted(out)</code>.",
                ],
                "why": [
                    "It is O(N log N) time and needs all N values in memory at once.",
                ],
                "dry": [
                    "Concatenated: [1, 4, 5, 1, 3, 4, 2, 6].",
                    "Sorted: <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge k sorted lists
    "merge-k-sorted-lists": {
        "example": {"call": "list_vals(merge_k_lists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])]))",
                    "expect": "[1, 1, 2, 3, 4, 4, 5, 6]"},
        "approaches": {
            "Min-heap of list heads": {
                "idea": [
                    "This is the previous problem with linked lists: keep each list's current head in a min-heap.",
                    "Pop the smallest node, append it to the result, and push its successor.",
                    "Push <code>(val, list index, node)</code>. The unique index breaks ties so Python never has to compare two nodes, which would raise <code>TypeError</code>.",
                ],
                "steps": [
                    "Heapify the non-empty heads.",
                    "Pop, link the node after <code>tail</code>, and push <code>node.next</code> if it exists.",
                ],
                "why": [
                    "Each of the N nodes passes through the heap once: O(N log k) time and O(k) space.",
                    "The output reuses the existing nodes.",
                ],
                "dry": [
                    "Heads: 1 (list 0), 1 (list 1), 2 (list 2).",
                    "Pop 1 (list 0) and push 4. Pop 1 (list 1) and push 3. Pop 2 and push 6.",
                    "Pop 3 and push 4. Pop 4 and push 5. Pop 4, then 5, then 6.",
                    "The merged list is <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                ],
            },
            "Merge pairwise, halving each round": {
                "idea": [
                    "Merge lists in pairs (1 with 2, 3 with 4, …), which halves the number of lists each round, until one is left.",
                    "Every round touches all N nodes and there are log k rounds.",
                    "Merging one list at a time into a growing result would instead re-walk the result every round: O(N·k).",
                ],
                "steps": [
                    "Drop empty lists.",
                    "Each round, <code>merge_two</code> adjacent pairs; an odd list out carries over.",
                ],
                "why": [
                    "It is O(N log k) time and O(1) extra space, since no heap is needed.",
                ],
                "dry": [
                    "Round 1: merge [1, 4, 5] with [1, 3, 4], giving [1, 1, 3, 4, 4, 5]; [2, 6] carries over.",
                    "Round 2: merge those two, giving [1, 1, 2, 3, 4, 4, 5, 6].",
                    "One list is left: <strong>[1, 1, 2, 3, 4, 4, 5, 6]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ smallest range covering k lists
    "smallest-range-k-lists": {
        "example": {"call": "smallest_range([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]])", "expect": "[20, 24]"},
        "approaches": {
            "k-way merge tracking the window": {
                "idea": [
                    "Keep one current element from every list. The range from the smallest to the largest of them covers all lists.",
                    "The only way to possibly shrink that range is to advance the list holding the smallest element, which a min-heap provides.",
                    "Track the largest separately; it only ever grows, because each list is sorted. Stop when any list runs out.",
                ],
                "steps": [
                    "Heap of <code>(value, list, index)</code> with each list's first element; <code>largest</code> = the maximum of those.",
                    "Pop the minimum; if <code>largest - value</code> beats the best range, record it.",
                    "If that list is exhausted, return; otherwise push its next element and update <code>largest</code>.",
                ],
                "why": [
                    "Every candidate range that could be optimal is examined as its left end is popped.",
                    "Each element is pushed and popped once: O(N log k) time and O(k) space.",
                ],
                "dry": [
                    "Start: 4, 0, 5, so the range is [0, 5] (width 5).",
                    "Pop 0 (largest 9), pop 4 (largest 10), pop 5 (largest 18). Widths 9, 6, 13: no improvement.",
                    "Pop 9, 10, 12 (largest 20), then pop 15 (largest 24) and 18. Widths 9, 8, 6, 5, 6: none below 5.",
                    "Pop 20 with largest 24: width 4, a new best, [20, 24].",
                    "List 1 is now exhausted, so the result is <strong>[20, 24]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth smallest in sorted matrix
    "kth-smallest-in-sorted-matrix": {
        "example": {"call": "kth_smallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8)", "expect": "13"},
        "approaches": {
            "k-way merge over the rows": {
                "idea": [
                    "Each row is sorted, so merging the rows produces the matrix in sorted order; the k-th value merged is the answer.",
                    "A min-heap holding one cursor per row does the merge; pop k - 1 times and read the top.",
                ],
                "steps": [
                    "Seed the heap with the first element of up to k rows.",
                    "Pop k - 1 times, each time pushing the next element of the same row.",
                    "Return <code>heap[0]</code>.",
                ],
                "why": [
                    "It is O(k log n) time and O(n) space; k can be as large as n².",
                ],
                "dry": [
                    "Seed: 1, 10, 12.",
                    "Pops: 1, 5, 9 (row 0 is done), 10, 11, 12, 13. That is 7 pops.",
                    "The top is now 13 from row 2, so the result is <strong>13</strong>.",
                ],
            },
            "Binary search on the value": {
                "idea": [
                    "Search over values instead of positions: for a candidate m, count how many entries are ≤ m.",
                    "If fewer than k, the answer is larger; otherwise it is m or smaller.",
                    "Counting takes O(n) with a staircase walk from the bottom-left corner, moving right or up.",
                ],
                "steps": [
                    "<code>lo, hi</code> = the smallest and largest entries.",
                    "If <code>count_le(mid) &lt; k</code>, set <code>lo = mid + 1</code>; otherwise <code>hi = mid</code>.",
                ],
                "why": [
                    "The count jumps only at real matrix values, so the search ends on a value that is in the matrix.",
                    "It is O(n log(range)) time and O(1) space.",
                ],
                "dry": [
                    "[1, 15]: mid 8 has 2 entries ≤ 8, fewer than 8, so lo = 9.",
                    "[9, 15]: mid 12 has 6 entries, so lo = 13.",
                    "[13, 15]: mid 14 has 8 entries, enough, so hi = 14. mid 13 also has 8, so hi = 13.",
                    "The result is <strong>13</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth smallest sum of matrix rows
    "kth-smallest-matrix-row-sums": {
        "example": {"call": "kth_smallest([[1, 3, 11], [2, 4, 6]], 5)", "expect": "7"},
        "approaches": {
            "Merge one row at a time, keeping k": {
                "idea": [
                    "A sum picks one value from each row; there are n<sup>m</sup> of them, far too many to list.",
                    "Fold the rows in one at a time, keeping only the k smallest partial sums: a partial sum outside the k smallest can never end up among the k smallest totals.",
                ],
                "steps": [
                    "<code>sums = [0]</code>.",
                    "For each row: <code>sums = nsmallest(k, s + v for every s, v)</code>.",
                    "Return <code>sums[-1]</code>.",
                ],
                "why": [
                    "Adding later rows only increases sums, so dropping the larger partial sums is safe.",
                    "It is O(m · k·n log k) time and O(k) space.",
                ],
                "dry": [
                    "Row 1: sums = [1, 3, 11].",
                    "Row 2 candidates: 3, 5, 7, 5, 7, 9, 13, 15, 17.",
                    "The 5 smallest are [3, 5, 5, 7, 7], and the last is <strong>7</strong>.",
                ],
            },
            "Best-first search over index tuples": {
                "idea": [
                    "Describe a choice as a tuple of column indices, one per row. All zeros is the smallest sum.",
                    "Pop the smallest choice from a heap, then push its neighbours: the choices that move exactly one row's index forward by one.",
                    "The k-th pop is the k-th smallest sum. A visited set stops the same tuple being pushed twice by different paths.",
                ],
                "steps": [
                    "Start with <code>(sum of the first column, (0, …, 0))</code>.",
                    "Pop k - 1 times; for each row r, push the tuple with <code>idx[r] + 1</code> if it is unseen.",
                    "Return <code>heap[0][0]</code>.",
                ],
                "why": [
                    "Neighbours never have a smaller sum, so sums come out of the heap in sorted order.",
                    "It is O(k·m log k) time and O(k·m) space.",
                ],
                "dry": [
                    "Pop (0, 0) with sum 3; push (1, 0) with 5 and (0, 1) with 5.",
                    "Pop (0, 1) with 5; push (1, 1) with 7 and (0, 2) with 7.",
                    "Pop (1, 0) with 5; push (2, 0) with 13.",
                    "Pop (0, 2) with 7; push (1, 2) with 9. That is 4 pops.",
                    "The top is (1, 1) with sum <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ connect sticks
    "connect-sticks": {
        "example": {"call": "connect_sticks([1, 8, 3, 5])", "expect": "30"},
        "approaches": {
            "Always merge the two shortest": {
                "idea": [
                    "Each stick's length is paid again in every merge it takes part in, so short sticks should be merged early and often, and long ones late.",
                    "That is Huffman coding: always merge the two shortest sticks currently available.",
                    "The merged stick goes back into the pool, so a heap is needed to keep picking the two smallest.",
                ],
                "steps": [
                    "Heapify the lengths.",
                    "While more than one stick is left: pop two, add their sum to the cost, push the sum.",
                ],
                "why": [
                    "Exchange argument: if a longer stick were merged more often than a shorter one, swapping them would lower the total.",
                    "It is O(n log n).",
                ],
                "dry": [
                    "Pool {1, 3, 5, 8}: merge 1 + 3 = 4, cost 4.",
                    "Pool {4, 5, 8}: merge 4 + 5 = 9, cost 13.",
                    "Pool {8, 9}: merge 8 + 9 = 17, cost 30.",
                    "The result is <strong>30</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ task scheduler
    "task-scheduler": {
        "example": {"call": 'least_interval(["A", "A", "A", "B", "B", "B"], 2)', "expect": "8"},
        "approaches": {
            "Counting formula": {
                "idea": [
                    "The most frequent task sets the shape: f copies of it need f - 1 gaps of length n between them.",
                    "That gives (f - 1) blocks of (n + 1) slots, plus a final slot for every task that is tied at frequency f.",
                    "If there are so many other tasks that every gap fills up, there is no idling at all and the answer is just the number of tasks.",
                ],
                "steps": [
                    "<code>most = max(counts)</code>, <code>tied</code> = how many tasks have that count.",
                    "Return <code>max(len(tasks), (most - 1)·(n + 1) + tied)</code>.",
                ],
                "why": [
                    "Other tasks fill the gaps first, and idle slots appear only when they run out.",
                    "It is O(n) time and O(1) space (at most 26 counts).",
                ],
                "dry": [
                    "Counts: A→3, B→3, so most = 3 and tied = 2.",
                    "(3 - 1)·(2 + 1) + 2 = 8, and the number of tasks is 6.",
                    "The result is <strong>8</strong>, for example A B idle A B idle A B.",
                ],
            },
            "Max-heap with a cooldown queue": {
                "idea": [
                    "Simulate the clock. A max-heap holds the remaining counts of tasks ready to run; a queue holds tasks cooling down with the time they become ready.",
                    "Each tick, run the most frequent ready task (or idle), and release any task whose cooldown ends.",
                ],
                "steps": [
                    "Each tick: pop the heap if it is not empty; if the task has copies left, queue it with <code>ready = time + n</code>.",
                    "If the front of the queue is ready, push it back onto the heap.",
                    "Stop when both are empty.",
                ],
                "why": [
                    "Running the most frequent ready task first is the greedy choice that avoids idling later.",
                    "It is O(answer) time, but it extends to tasks with different durations or priorities, where no formula exists.",
                ],
                "dry": [
                    "t1: run A (2 left, ready at 3). t2: run B (2 left, ready at 4).",
                    "t3: nothing ready, so idle; A becomes ready. t4: run A (ready at 6); B becomes ready.",
                    "t5: run B (ready at 7). t6: idle; A becomes ready. t7: run A (none left); B becomes ready.",
                    "t8: run B. Everything is done at time <strong>8</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reorganize string
    "reorganize-string": {
        "example": {"call": 'reorganize_string("aaabc")', "expect": '"abaca"'},
        "approaches": {
            "Max-heap, always take two": {
                "idea": [
                    "It is impossible exactly when some character appears more than <code>(n + 1) // 2</code> times; check that first.",
                    "Otherwise repeatedly take the two most frequent remaining characters and place them side by side. They are different, so no two neighbours repeat.",
                ],
                "steps": [
                    "Max-heap of <code>(-count, ch)</code>.",
                    "Pop two, append both, decrement, and push back any with copies left.",
                    "If one character is left over, append it.",
                ],
                "why": [
                    "Always placing the most frequent characters first keeps the leftover counts balanced.",
                    "It is O(n log 26) = O(n).",
                ],
                "dry": [
                    "Counts: a3, b1, c1. 3 ≤ (5 + 1) // 2, so it is feasible.",
                    "Pop a and b, giving \"ab\"; a has 2 left.",
                    "Pop a and c, giving \"abac\"; a has 1 left.",
                    "Only a is left, so append it: <strong>\"abaca\"</strong>.",
                ],
            },
            "Fill even slots, then odd": {
                "idea": [
                    "Place the most frequent character at positions 0, 2, 4, …; when those run out, continue at 1, 3, 5, ….",
                    "Every other character follows on from where the previous one stopped.",
                    "Two equal characters can only end up adjacent if one character has more copies than there are even slots, which the feasibility check rules out.",
                ],
                "steps": [
                    "Reject if <code>max count &gt; (n + 1) // 2</code>.",
                    "For characters in <code>most_common()</code> order, write each copy at i and do <code>i += 2</code>, wrapping to 1 when past the end.",
                ],
                "why": [
                    "Copies of one character always land at least two apart.",
                    "It is O(n) with a tiny constant and no heap.",
                ],
                "dry": [
                    "a (3 copies) goes to slots 0, 2, 4.",
                    "i = 6 is past the end, so it wraps to 1: b goes to slot 1.",
                    "c goes to slot 3.",
                    "The result is <strong>\"abaca\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ IPO
    "ipo": {
        "example": {"call": "find_maximized_capital(2, 0, [1, 2, 3], [0, 1, 1])", "expect": "4"},
        "approaches": {
            "Two heaps: affordable by capital, best by profit": {
                "idea": [
                    "At any moment, choose the most profitable project you can afford. Profits are non-negative, so this only grows your capital and never closes off options.",
                    "Sort projects by required capital and release them into a max-heap of profits as your capital reaches them.",
                    "Repeat k times, stopping early if nothing is affordable.",
                ],
                "steps": [
                    "Sort <code>(capital, profit)</code> pairs.",
                    "Each round, push every newly affordable project's profit, then pop the largest and add it to <code>w</code>.",
                ],
                "why": [
                    "The pointer never moves back, so each project enters the heap once: O(n log n).",
                ],
                "dry": [
                    "Sorted projects: (0, 1), (1, 2), (1, 3).",
                    "Round 1, w = 0: only (0, 1) is affordable; take it, so w = 1.",
                    "Round 2, w = 1: (1, 2) and (1, 3) become affordable; take 3, so w = 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ meeting rooms
    "meeting-rooms": {
        "example": {"call": "can_attend_meetings([[7, 10], [2, 4], [4, 7]])", "expect": "True"},
        "approaches": {
            "Sort by start, compare neighbours": {
                "idea": [
                    "After sorting by start time, if any two meetings overlap, then some adjacent pair overlaps too.",
                    "So a single scan comparing each start with the previous end is enough.",
                ],
                "steps": [
                    "Sort the intervals.",
                    "If any <code>start &lt; previous end</code>, return <code>False</code>.",
                ],
                "why": [
                    "Touching endpoints do not conflict, which is why the comparison is a strict &lt;.",
                    "It is O(n log n) for the sort.",
                ],
                "dry": [
                    "Sorted: [2, 4], [4, 7], [7, 10].",
                    "4 &lt; 4? No. 7 &lt; 7? No. The meetings only touch.",
                    "The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ meeting rooms II
    "meeting-rooms-ii": {
        "example": {"call": "min_meeting_rooms([[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]])", "expect": "4"},
        "approaches": {
            "Min-heap of end times": {
                "idea": [
                    "Process meetings by start time, with a min-heap of the end times of rooms in use.",
                    "Only the room that frees up first matters: if even it is still busy, every room is busy, so a new room is needed.",
                    "The heap's size is the number of rooms in use, and its final size is the answer.",
                ],
                "steps": [
                    "Sort by start.",
                    "If <code>ends[0] &lt;= start</code>, pop it (reuse that room).",
                    "Push this meeting's end.",
                ],
                "why": [
                    "It is O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "[1, 10]: rooms {10}. [2, 7]: 10 &gt; 2, so a new room: {7, 10}. [3, 19]: a new room: {7, 10, 19}.",
                    "[8, 12]: 7 ≤ 8, so reuse that room: {10, 12, 19}.",
                    "[10, 20]: 10 ≤ 10, so reuse: {12, 19, 20}.",
                    "[11, 30]: 12 &gt; 11, so a new room: {12, 19, 20, 30}. The result is <strong>4</strong>.",
                ],
            },
            "Sweep the endpoints": {
                "idea": [
                    "Only counts matter, not which room is which: sort all starts and all ends separately.",
                    "Walk the starts; before each one, release every meeting whose end has passed. The running count's peak is the answer.",
                ],
                "steps": [
                    "<code>starts</code> and <code>ends</code>, each sorted.",
                    "For each start, while <code>ends[j] &lt;= start</code>, decrement rooms and advance j; then increment rooms.",
                ],
                "why": [
                    "It is O(n log n) for the two sorts and needs no heap.",
                ],
                "dry": [
                    "starts = [1, 2, 3, 8, 10, 11], ends = [7, 10, 12, 19, 20, 30].",
                    "1, 2, 3: rooms 1, 2, 3.",
                    "8: end 7 has passed, so 2, then +1 = 3. 10: end 10 has passed, so 2, then +1 = 3.",
                    "11: end 12 has not passed, so rooms = 4. The peak is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum refueling stops
    "refueling-stops": {
        "example": {"call": "min_refuel_stops(100, 10, [[10, 60], [20, 30], [30, 30], [60, 40]])", "expect": "2"},
        "approaches": {
            "Max-heap of fuel already driven past": {
                "idea": [
                    "Drive as far as your fuel allows, noting every station you pass in a max-heap, without stopping yet.",
                    "When you need more fuel, pretend you stopped at the largest station you passed.",
                    "Taking the biggest tank first minimises the number of stops, and the order of refuelling does not matter once you are past those stations.",
                ],
                "steps": [
                    "While <code>fuel &lt; target</code>: push every station within reach.",
                    "If the heap is empty, return -1; otherwise pop the largest and add it to <code>fuel</code>, counting a stop.",
                ],
                "why": [
                    "Exchange argument: swapping a chosen station for a larger one already passed never adds stops.",
                    "It is O(n log n).",
                ],
                "dry": [
                    "fuel = 10 reaches the station at 10, so the heap is {60}.",
                    "Refuel 60, so fuel = 70 after 1 stop. Stations at 20, 30 and 60 are now within reach: {30, 30, 40}.",
                    "Refuel 40, so fuel = 110 ≥ 100 after 2 stops.",
                    "The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find median from data stream
    "find-median-from-data-stream": {
        "example": {"setup": "mf = MedianFinder()",
                    "call": "[mf.add_num(x) or mf.find_median() for x in (5, 15, 1, 3)]",
                    "expect": "[5.0, 10.0, 5.0, 4.0]"},
        "approaches": {
            "Max-heap of the low half, min-heap of the high half": {
                "idea": [
                    "Split the numbers into a lower half and an upper half. The median sits at the boundary.",
                    "Keep the lower half in a max-heap (<code>small</code>, stored negated) and the upper half in a min-heap (<code>large</code>).",
                    "Invariant: everything in small ≤ everything in large, and small has the same size as large or one more. Then the median is small's top, or the average of the two tops.",
                ],
                "steps": [
                    "<code>add_num</code>: push into small, move small's largest to large, and move one back if large got bigger.",
                    "<code>find_median</code>: read the tops.",
                ],
                "why": [
                    "Routing every value through small then large keeps the halves ordered without reasoning about where it belongs.",
                    "<code>add_num</code> is O(log n) and <code>find_median</code> is O(1).",
                ],
                "dry": [
                    "The call adds a number, then reads the median, because <code>add_num</code> returns <code>None</code>.",
                    "Add 5: small = {5}, so the median is <strong>5.0</strong>.",
                    "Add 15: it goes through small and ends in large. small = {5}, large = {15}, median <strong>10.0</strong>.",
                    "Add 1: small's max 5 moves to large, then large is too big, so 5 moves back. small = {1, 5}, large = {15}, median <strong>5.0</strong>.",
                    "Add 3: small = {1, 3}, large = {5, 15}, median (3 + 5) / 2 = <strong>4.0</strong>.",
                ],
            },
            "Sorted list with bisect": {
                "idea": [
                    "Keep every number in a sorted list; the median is one or two index reads.",
                    "Insertion uses <code>bisect.insort</code>, which shifts the tail.",
                ],
                "steps": [
                    "<code>insort(data, num)</code>.",
                    "Return the middle value, or the mean of the two middle values.",
                ],
                "why": [
                    "Each add is O(n) for the shift; it is fast in practice for small n because the shift is a contiguous memory move.",
                ],
                "dry": [
                    "[5], median <strong>5.0</strong>. [5, 15], median <strong>10.0</strong>.",
                    "[1, 5, 15], median <strong>5.0</strong>. [1, 3, 5, 15], median <strong>4.0</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sliding window median
    "sliding-window-median": {
        "example": {"call": "median_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)", "expect": "[1.0, -1.0, -1.0, 3.0, 5.0, 6.0]"},
        "approaches": {
            "Sorted window with bisect": {
                "idea": [
                    "Keep the current window in a sorted list, so the median is a direct index read.",
                    "Sliding means deleting the outgoing value and inserting the incoming one, each found by binary search.",
                ],
                "steps": [
                    "Start with the first k values, sorted.",
                    "Each step: <code>pop(bisect_left(window, old))</code>, then <code>insort(window, new)</code>, then read the median.",
                ],
                "why": [
                    "The binary searches are O(log k), but the list shifts make each step O(k): O(n·k) overall.",
                ],
                "dry": [
                    "[-1, 1, 3], median <strong>1.0</strong>.",
                    "Out 1, in -3: [-3, -1, 3], median <strong>-1.0</strong>. Out 3, in 5: [-3, -1, 5], median <strong>-1.0</strong>.",
                    "Out -1, in 3: [-3, 3, 5], median <strong>3.0</strong>. Out -3, in 6: [3, 5, 6], median <strong>5.0</strong>.",
                    "Out 5, in 7: [3, 6, 7], median <strong>6.0</strong>.",
                ],
            },
            "Two heaps with lazy deletion": {
                "idea": [
                    "Use the two-heap median structure, but a window also needs to <em>remove</em> the value leaving it, and a heap can only remove its top.",
                    "So remove lazily: count the value in <code>delayed</code>, adjust the logical sizes, and leave it in the heap. If it ever reaches a heap's top, pop it then.",
                    "Because the heaps now contain these hidden leftovers, their sizes are tracked in separate counters, not with <code>len</code>.",
                ],
                "steps": [
                    "<code>add</code>: push to the correct side, then rebalance the logical sizes.",
                    "<code>remove</code>: mark it as delayed, decrement that side's count, prune if it sits at the top, then rebalance.",
                    "The median comes from the tops, which pruning keeps clean.",
                ],
                "why": [
                    "Each value is truly popped at most once: O(n log k) time and O(k) space.",
                ],
                "dry": [
                    "The first window [1, 3, -1] gives the median <strong>1.0</strong>.",
                    "-3 enters and 1 leaves. 1 is at the top of <code>large</code>, so it is popped right away. Median <strong>-1.0</strong>.",
                    "5 enters and 3 leaves (also at a top, popped). Median <strong>-1.0</strong>. Then 3 enters and -1 leaves (popped). Median <strong>3.0</strong>.",
                    "6 enters and -3 leaves, but -3 is buried inside <code>small</code>, so it is only marked delayed. Median <strong>5.0</strong>.",
                    "7 enters and 5 leaves from small's top. Median <strong>6.0</strong>, giving <strong>[1.0, -1.0, -1.0, 3.0, 5.0, 6.0]</strong>.",
                ],
            },
        },
    },
}
