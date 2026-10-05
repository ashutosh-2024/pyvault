"""Write-ups for the Range Queries topic (prefix sums, Fenwick and segment trees)."""

EXPLAIN = {
    # ------------------------------------------------------------------ range sum immutable
    "range-sum-query-immutable": {
        "example": {"setup": "a = NumArray([-2, 0, 3, -5, 2, -1])",
                    "call": "[a.sumRange(0, 2), a.sumRange(2, 5), a.sumRange(0, 5)]", "expect": "[1, -1, -3]"},
        "approaches": {
            "Sum the slice on every query": {
                "idea": [
                    "Answer each query by adding up the requested slice.",
                    "Nothing is precomputed, so repeated queries redo the same additions.",
                ],
                "steps": [
                    "Store the array.",
                    "<code>sumRange(l, r)</code> returns <code>sum(nums[l:r+1])</code>.",
                ],
                "why": [
                    "It is correct by definition.",
                    "Each query is O(n), so q queries cost O(n·q), which the problem's many queries are designed to punish.",
                ],
                "dry": [
                    "<code>sumRange(0, 2)</code> adds -2 + 0 + 3 = <strong>1</strong>.",
                    "<code>sumRange(2, 5)</code> adds 3 - 5 + 2 - 1 = <strong>-1</strong>.",
                    "<code>sumRange(0, 5)</code> adds all six numbers = <strong>-3</strong>, re-reading values the first two queries already summed.",
                ],
            },
            "Prefix sums": {
                "idea": [
                    "Precompute running totals once: <code>pre[i]</code> is the sum of the first i elements, with <code>pre[0] = 0</code>.",
                    "Then the sum of <code>nums[l..r]</code> is everything up to r minus everything before l: <code>pre[r+1] - pre[l]</code>.",
                    "Every query becomes one subtraction.",
                ],
                "steps": [
                    "<code>pre = [0] + list(accumulate(nums))</code>.",
                    "<code>sumRange(l, r)</code> returns <code>pre[r + 1] - pre[l]</code>.",
                ],
                "why": [
                    "<code>pre[r+1]</code> covers indices 0..r and <code>pre[l]</code> covers 0..l-1, so their difference is exactly l..r.",
                    "The leading zero removes the special case for l = 0. It is O(n) to build, O(1) per query, O(n) space.",
                ],
                "dry": [
                    "pre = [0, -2, -2, 1, -4, -2, -3].",
                    "<code>sumRange(0, 2)</code> = pre[3] - pre[0] = 1 - 0 = <strong>1</strong>.",
                    "<code>sumRange(2, 5)</code> = pre[6] - pre[2] = -3 - (-2) = <strong>-1</strong>.",
                    "<code>sumRange(0, 5)</code> = pre[6] - pre[0] = <strong>-3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ range sum mutable
    "range-sum-query-mutable": {
        "example": {"setup": "a = NumArray([1, 3, 5, 7, 9, 11])",
                    "call": "[a.sumRange(1, 4), a.update(2, 10), a.sumRange(1, 4), a.sumRange(0, 5)]",
                    "expect": "[24, None, 29, 41]"},
        "approaches": {
            "Plain array": {
                "idea": [
                    "Keep the raw array: an update is a single assignment, and a query sums the slice.",
                    "This is the right choice only when queries are rare.",
                ],
                "steps": [
                    "<code>update</code>: <code>nums[index] = val</code>.",
                    "<code>sumRange</code>: <code>sum(nums[l:r+1])</code>.",
                ],
                "why": [
                    "It is correct by definition: O(1) update, O(n) query.",
                ],
                "dry": [
                    "<code>sumRange(1, 4)</code> = 3 + 5 + 7 + 9 = <strong>24</strong>.",
                    "<code>update(2, 10)</code> sets nums[2] = 10 and returns <code>None</code>.",
                    "<code>sumRange(1, 4)</code> = 3 + 10 + 7 + 9 = <strong>29</strong>.",
                    "<code>sumRange(0, 5)</code> = 1 + 3 + 10 + 7 + 9 + 11 = <strong>41</strong>.",
                ],
            },
            "Square-root decomposition": {
                "idea": [
                    "Cut the array into blocks of about √n elements and keep each block's sum.",
                    "A query adds whole block sums in the middle and single elements only at the two ragged ends.",
                    "An update changes one element and adjusts one block sum by the difference.",
                ],
                "steps": [
                    "<code>size = int(√n)</code>; <code>blocks[i // size]</code> accumulates every element.",
                    "<code>update</code>: <code>blocks[index // size] += val - nums[index]</code>, then store <code>val</code>.",
                    "<code>sumRange</code>: add single elements until <code>left</code> reaches a block boundary, then whole blocks while one fits, then single elements to <code>right</code>.",
                ],
                "why": [
                    "Each element is counted once, either alone or inside its block's sum.",
                    "A query does at most about 3√n steps and an update is O(1). It is a one-level version of a segment tree.",
                ],
                "dry": [
                    "size = 2, so the block sums are [1+3, 5+7, 9+11, 0] = [4, 12, 20, 0].",
                    "<code>sumRange(1, 4)</code>: index 1 is mid-block, so take 3; block 1 (indices 2..3) fits, so take 12; index 4 is ragged, so take 9. Total <strong>24</strong>.",
                    "<code>update(2, 10)</code>: block 1 grows by 10 - 5 = 5, to 17.",
                    "<code>sumRange(1, 4)</code> = 3 + 17 + 9 = <strong>29</strong>.",
                    "<code>sumRange(0, 5)</code> = whole blocks 4 + 17 + 20 = <strong>41</strong>.",
                ],
            },
            "Fenwick tree": {
                "idea": [
                    "A Fenwick tree (binary indexed tree) stores partial sums so that any prefix sum is the sum of at most log n stored values.",
                    "Slot i (1-indexed) covers the <code>i &amp; -i</code> elements ending at i; for example slot 4 covers 1..4 and slot 6 covers 5..6.",
                    "A prefix sum hops downward by removing the lowest set bit; an update hops upward by adding it, touching every slot that covers the index.",
                ],
                "steps": [
                    "Build in O(n): copy nums into slots 1..n, and push each slot's total into its parent <code>i + (i &amp; -i)</code>.",
                    "<code>_prefix(i)</code>: add <code>tree[i]</code>, then <code>i -= i &amp; -i</code>, until i is 0.",
                    "<code>update</code>: compute <code>delta</code>, then add it at <code>i = index + 1</code> and keep jumping <code>i += i &amp; -i</code>.",
                    "<code>sumRange(l, r) = _prefix(r + 1) - _prefix(l)</code>.",
                ],
                "why": [
                    "The covered ranges along a downward hop chain tile 1..i exactly, so <code>_prefix</code> is right.",
                    "The upward chain visits exactly the slots whose ranges contain the index. Both chains are O(log n) long, and space is O(n).",
                ],
                "dry": [
                    "After the build, the tree is [_, 1, 4, 5, 16, 9, 20]: slot 2 = 1 + 3, slot 4 = 1 + 3 + 5 + 7, slot 6 = 9 + 11.",
                    "<code>sumRange(1, 4)</code>: prefix(5) = slot 5 + slot 4 = 9 + 16 = 25; prefix(1) = slot 1 = 1. 25 - 1 = <strong>24</strong>.",
                    "<code>update(2, 10)</code>: delta = 5, added to slot 3 (now 10) and then slot 4 (now 21), since 3 + 1 = 4 and 4 + 4 = 8 &gt; n.",
                    "<code>sumRange(1, 4)</code> = (9 + 21) - 1 = <strong>29</strong>.",
                    "<code>sumRange(0, 5)</code> = prefix(6) = slot 6 + slot 4 = 20 + 21 = <strong>41</strong>.",
                ],
            },
            "Segment tree (iterative, bottom-up)": {
                "idea": [
                    "Lay the array out as the leaves of a binary tree at positions n..2n-1; each internal node i stores the sum of children 2i and 2i+1.",
                    "An update rewrites a leaf and recomputes the log n ancestors above it.",
                    "A query walks two pointers up from both ends of the half-open range <code>[l, r)</code>, taking a node whenever it lies entirely inside the range.",
                ],
                "steps": [
                    "Build: leaves are nums, and for i from n-1 down to 1, <code>tree[i] = tree[2i] + tree[2i+1]</code>.",
                    "<code>update</code>: set the leaf, then repeatedly halve i and recompute.",
                    "<code>sumRange</code>: <code>l = left + n</code>, <code>r = right + n + 1</code>. While <code>l &lt; r</code>: if l is odd, take <code>tree[l]</code> and step <code>l += 1</code>; if r is odd, step <code>r -= 1</code> and take <code>tree[r]</code>; then halve both.",
                ],
                "why": [
                    "An odd l is a right child whose parent would stick out past the range, so take it on its own; the same holds on the right.",
                    "It is O(log n) per operation and O(n) space. Swap + for min or max and it still works, which a Fenwick tree cannot do.",
                ],
                "dry": [
                    "Leaves tree[6..11] = 1, 3, 5, 7, 9, 11. Internal: tree[5] = 20, tree[4] = 12, tree[3] = 4, tree[2] = 32, tree[1] = 36.",
                    "<code>sumRange(1, 4)</code>: l = 7, r = 11. l is odd, so take tree[7] = 3 and l = 8; r is odd, so r = 10 and take tree[10] = 9. Halve: l = 4, r = 5.",
                    "r = 5 is odd, so r = 4 and take tree[4] = 12. Halve: l = r = 2, stop. Total 3 + 9 + 12 = <strong>24</strong>.",
                    "<code>update(2, 10)</code>: leaf 8 becomes 10, then tree[4] = 17, tree[2] = 37, tree[1] = 41.",
                    "<code>sumRange(1, 4)</code> now takes 3 + 9 + 17 = <strong>29</strong>, and <code>sumRange(0, 5)</code> takes tree[3] + tree[2] = 4 + 37 = <strong>41</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count of smaller after self
    "count-of-smaller-numbers-after-self": {
        "example": {"call": "count_smaller([5, 2, 6, 1, 3])", "expect": "[3, 1, 2, 0, 0]"},
        "approaches": {
            "Compare every pair": {
                "idea": [
                    "For every element, look at everything to its right and count the smaller values.",
                ],
                "steps": [
                    "For each i, count <code>y &lt; nums[i]</code> over <code>nums[i+1:]</code>.",
                ],
                "why": [
                    "It is the definition, so it is correct. It costs O(n²) time and is too slow for n = 10<sup>5</sup>.",
                ],
                "dry": [
                    "5: the values 2, 1, 3 to its right are smaller, so 3.",
                    "2: only 1 is smaller, so 1. 6: 1 and 3 are smaller, so 2.",
                    "1: nothing smaller, so 0. 3: nothing to its right, so 0.",
                    "The result is <strong>[3, 1, 2, 0, 0]</strong>.",
                ],
            },
            "Sorted list + bisect": {
                "idea": [
                    "Scan from the right, keeping every value already seen in a sorted list.",
                    "The number of seen values below x is exactly where x would be inserted: <code>bisect_left</code>.",
                ],
                "steps": [
                    "For x in <code>reversed(nums)</code>: record <code>bisect_left(seen, x)</code>, then <code>insort(seen, x)</code>.",
                    "Reverse the recorded answers back into input order.",
                ],
                "why": [
                    "Values seen during a right-to-left scan are exactly the elements to the right of x.",
                    "Each search is O(log n), but <code>insort</code> shifts elements: O(n) per insert and O(n²) worst case, though CPython's fast memmove often hides it.",
                ],
                "dry": [
                    "3: seen = [], so 0; seen = [3].",
                    "1: the insertion point in [3] is 0; seen = [1, 3].",
                    "6: the insertion point in [1, 3] is 2; seen = [1, 3, 6].",
                    "2: the insertion point in [1, 3, 6] is 1; seen = [1, 2, 3, 6].",
                    "5: the insertion point in [1, 2, 3, 6] is 3.",
                    "The answers in reverse scan order are [0, 0, 2, 1, 3], so the result is <strong>[3, 1, 2, 0, 0]</strong>.",
                ],
            },
            "Merge sort, counting right-to-left jumps": {
                "idea": [
                    "Merge sort the <em>indices</em> by value. During a merge, every element of the left half started out to the left of every element of the right half.",
                    "When a left-half element is placed, the right-half elements already placed before it are smaller and were originally to its right.",
                    "Add that count, j, to its answer; across all merge levels this counts every smaller element to the right exactly once.",
                ],
                "steps": [
                    "Recursively sort both halves of the index list.",
                    "Merge: for each left index i, first move every right index with a smaller value into the output (advancing j).",
                    "Add j to <code>res[i]</code>, then output i; append whatever is left of the right half.",
                ],
                "why": [
                    "Each pair (i, j) with i left of j sits on opposite sides of exactly one merge, and is counted there if <code>nums[j] &lt; nums[i]</code>.",
                    "It is merge sort: O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "Splits: [5, 2] | [6, 1, 3], and then [6] | [1, 3].",
                    "Merge [5] with [2]: 2 &lt; 5 jumps ahead, so 5 gets +1.",
                    "Merge [1] with [3]: nothing jumps 1. Merge [6] with [1, 3]: both jump ahead of 6, so 6 gets +2.",
                    "Top merge [2, 5] with [1, 3, 6]: before 2, only 1 jumps (2 gets +1); before 5, 3 also jumps (5 gets +2, making 3 in total).",
                    "The result is <strong>[3, 1, 2, 0, 0]</strong>.",
                ],
            },
            "Fenwick tree over value ranks": {
                "idea": [
                    "Scan from the right. \"How many seen values are below x\" is a prefix count over values, which a Fenwick tree answers in O(log n).",
                    "Values can be huge or negative, so first compress them to ranks 1..k by sorting the distinct values.",
                ],
                "steps": [
                    "<code>rank[v]</code> is v's position among the sorted distinct values, starting at 1.",
                    "For x from the right: the answer is <code>prefix(rank[x] - 1)</code>, the count of seen ranks strictly below x; then <code>add(rank[x])</code>.",
                    "Reverse the answers.",
                ],
                "why": [
                    "The tree holds exactly the counts of elements to the right of the current position.",
                    "Each step is two O(log k) operations: O(n log n) time and O(n) space. This is the reusable compress-then-count template.",
                ],
                "dry": [
                    "Ranks: 1→1, 2→2, 3→3, 5→4, 6→5.",
                    "3 (rank 3): prefix(2) = 0; add rank 3. 1 (rank 1): prefix(0) = 0; add rank 1.",
                    "6 (rank 5): prefix(4) counts ranks 1 and 3, so 2; add rank 5.",
                    "2 (rank 2): prefix(1) counts rank 1, so 1; add rank 2.",
                    "5 (rank 4): prefix(3) counts ranks 1, 2 and 3, so 3.",
                    "Reversed, the result is <strong>[3, 1, 2, 0, 0]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ create sorted array
    "create-sorted-array-through-instructions": {
        "example": {"call": "create_sorted_array([1, 3, 3, 3, 2, 4, 2, 1, 2])", "expect": "4"},
        "approaches": {
            "Sorted list + bisect": {
                "idea": [
                    "Keep the inserted values in a sorted list.",
                    "The count strictly below x is <code>bisect_left</code>, and the count strictly above is everything after <code>bisect_right</code>.",
                    "The cost of each insertion is the smaller of the two.",
                ],
                "steps": [
                    "For each x: <code>less = bisect_left(seen, x)</code>, <code>greater = len(seen) - bisect_right(seen, x)</code>.",
                    "Add <code>min(less, greater)</code>, then <code>insort(seen, x)</code>.",
                    "Return the total modulo 10<sup>9</sup> + 7.",
                ],
                "why": [
                    "The bisects split the sorted list into below, equal and above x.",
                    "The searches are O(log n), but each insert shifts elements: O(n²) worst case.",
                ],
                "dry": [
                    "1, 3, 3, 3 each cost 0, since nothing is smaller or nothing is larger.",
                    "2 into [1, 3, 3, 3]: 1 smaller, 3 greater, so the cost is 1 (total 1).",
                    "4: nothing is greater, so 0.",
                    "2 into [1, 2, 3, 3, 3, 4]: 1 smaller, 4 greater, so 1 (total 2).",
                    "1: nothing is smaller, so 0.",
                    "2 into [1, 1, 2, 2, 3, 3, 3, 4]: 2 smaller, 4 greater, so 2 (total <strong>4</strong>).",
                ],
            },
            "Fenwick tree over values": {
                "idea": [
                    "Count how many inserted values are ≤ v with a Fenwick tree indexed directly by value; values are at most 10<sup>5</sup>, so no compression is needed.",
                    "Strictly smaller is <code>prefix(x - 1)</code>. Strictly greater is the number inserted so far minus <code>prefix(x)</code>.",
                ],
                "steps": [
                    "<code>m = max(instructions)</code>, and the tree has m + 1 slots.",
                    "For the i-th value x (0-based, so i values are already in): add <code>min(prefix(x - 1), i - prefix(x))</code>.",
                    "Then <code>add(x)</code>.",
                ],
                "why": [
                    "<code>prefix(x)</code> counts the inserted values ≤ x, so <code>i - prefix(x)</code> counts the ones above x.",
                    "It is three O(log m) operations per value: O(n log m) time and O(m) space.",
                ],
                "dry": [
                    "i=0..3 (1, 3, 3, 3): every cost is 0.",
                    "i=4, x=2: prefix(1) = 1 smaller; 4 - prefix(2) = 4 - 1 = 3 greater. Cost 1.",
                    "i=5, x=4: 5 - prefix(4) = 0 greater. Cost 0.",
                    "i=6, x=2: prefix(1) = 1; 6 - prefix(2) = 6 - 2 = 4. Cost 1.",
                    "i=7, x=1: prefix(0) = 0. Cost 0.",
                    "i=8, x=2: prefix(1) = 2; 8 - prefix(2) = 8 - 4 = 4. Cost 2. The total is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse pairs
    "reverse-pairs": {
        "example": {"call": "reverse_pairs([2, 4, 3, 5, 1])", "expect": "3"},
        "approaches": {
            "Every pair": {
                "idea": [
                    "Check the condition <code>nums[i] &gt; 2·nums[j]</code> for every pair with i &lt; j.",
                ],
                "steps": [
                    "Two nested loops, counting the pairs that satisfy the condition.",
                ],
                "why": [
                    "It is the definition: O(n²) time and O(1) space.",
                ],
                "dry": [
                    "Against the last value 1 (2 × 1 = 2): 4, 3 and 5 are all greater than 2, which is 3 pairs; 2 is not.",
                    "No other pair qualifies, since 2·3 = 6 and 2·5 = 10 exceed every earlier value.",
                    "The total is <strong>3</strong>.",
                ],
            },
            "Merge sort with a separate counting pass": {
                "idea": [
                    "Split the array, and count pairs inside each half recursively. Pairs that cross the split have i in the left half and j in the right half.",
                    "Once both halves are sorted, the right-half values y with x &gt; 2y form a prefix of the right half, and that prefix only grows as x grows.",
                    "So one two-pointer sweep counts all crossing pairs in linear time; then merge normally.",
                ],
                "steps": [
                    "Recursively sort and count both halves.",
                    "For each x in the sorted left half, advance j while <code>x &gt; 2·right[j]</code>, and add j.",
                    "Return the merged sorted list and the total count.",
                ],
                "why": [
                    "Sorting inside a half does not change which side of the split an element is on, so crossing pairs are counted correctly.",
                    "There are O(n) per level and O(log n) levels: O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "Split [2, 4] | [3, 5, 1]. [2, 4] has no pair.",
                    "[3, 5, 1] splits into [3] | [5, 1]. Inside [5, 1]: 5 &gt; 2, so 1 pair, giving sorted [1, 5].",
                    "Crossing [3] with [1, 5]: 3 &gt; 2·1 counts 1; 3 &gt; 10 fails. [3, 5, 1] has 2 pairs and sorts to [1, 3, 5].",
                    "The top crossing pass, [2, 4] against [1, 3, 5]: 2 &gt; 2 fails (0); 4 &gt; 2 counts 1 and 4 &gt; 6 fails, so 1.",
                    "The total is 0 + 2 + 1 = <strong>3</strong>.",
                ],
            },
            "Fenwick tree over compressed values": {
                "idea": [
                    "Scan j left to right. The pairs ending at j are the earlier values strictly greater than <code>2·nums[j]</code>.",
                    "Keep the earlier values in a Fenwick tree over compressed ranks; \"greater than 2y\" is the total inserted minus the count ≤ 2y.",
                    "<code>bisect_right</code> on the sorted distinct values finds how many ranks are ≤ 2y, even though 2y itself is not in the table.",
                ],
                "steps": [
                    "<code>vals</code> = sorted distinct values.",
                    "For j with value y: <code>at_most = bisect_right(vals, 2y)</code>; add <code>seen - prefix(at_most)</code>.",
                    "Insert y at rank <code>bisect_left(vals, y) + 1</code>.",
                ],
                "why": [
                    "Before step j the tree holds exactly the values at indices before j.",
                    "Each step is O(log n): O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "vals = [1, 2, 3, 4, 5].",
                    "y=2: there is nothing before it. y=4: one earlier value (2), none &gt; 8. y=3: none &gt; 6. y=5: none &gt; 10.",
                    "y=1: 2y = 2 and bisect_right gives 2 ranks ≤ 2. The tree has 1 value among them (the 2), so 4 - 1 = 3 earlier values exceed 2.",
                    "The total is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count of range sum
    "count-of-range-sum": {
        "example": {"call": "count_range_sum([-2, 5, -1], -2, 2)", "expect": "3"},
        "approaches": {
            "Every subarray via prefix sums": {
                "idea": [
                    "With prefix sums P, the subarray from i to j-1 sums to <code>P[j] - P[i]</code>.",
                    "Check every pair i &lt; j and count those whose difference lies in [lower, upper].",
                ],
                "steps": [
                    "<code>P = [0] + accumulate(nums)</code>.",
                    "Count the pairs <code>i &lt; j</code> with <code>lower ≤ P[j] - P[i] ≤ upper</code>.",
                ],
                "why": [
                    "Every subarray corresponds to exactly one pair (i, j).",
                    "Each sum is O(1), but there are n²/2 pairs: O(n²) time and O(n) space.",
                ],
                "dry": [
                    "P = [0, -2, 3, 2].",
                    "Pairs: -2 - 0 = -2 ✓, 3 - 0 = 3, 3 - (-2) = 5, 2 - 0 = 2 ✓, 2 - (-2) = 4, 2 - 3 = -1 ✓.",
                    "The subarrays counted are [-2], [-2, 5, -1] and [-1], so the result is <strong>3</strong>.",
                ],
            },
            "Fenwick tree over prefix sums": {
                "idea": [
                    "For each j, count earlier prefix sums P[i] with <code>P[j] - upper ≤ P[i] ≤ P[j] - lower</code>.",
                    "Keep the earlier prefix sums in a Fenwick tree over compressed values; a value window is a difference of two prefix counts.",
                    "Insert <code>P[0] = 0</code> first so that subarrays starting at index 0 are counted.",
                ],
                "steps": [
                    "Compress all prefix sums into <code>vals</code>.",
                    "For each p in P: <code>lo = bisect_left(vals, p - upper)</code>, <code>hi = bisect_right(vals, p - lower)</code>; add <code>prefix(hi) - prefix(lo)</code>.",
                    "Then insert p.",
                ],
                "why": [
                    "The tree holds exactly the earlier prefix sums, and the two bisects turn the value window into a rank window.",
                    "It is O(log n) per step: O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "vals = [-2, 0, 2, 3].",
                    "p=0: the tree is empty, 0. Insert 0.",
                    "p=-2: window [-4, 0] contains the 0, so count 1. Insert -2.",
                    "p=3: window [1, 5] contains nothing yet, 0. Insert 3.",
                    "p=2: window [0, 4] contains 0 and 3, so count 2.",
                    "The total is <strong>3</strong>.",
                ],
            },
            "Merge sort on prefix sums": {
                "idea": [
                    "Run merge sort on the prefix sums. A pair (i, j) with i in the left half and j in the right half is counted during that merge.",
                    "Once both halves are sorted, the right-half values within <code>[x + lower, x + upper]</code> form a contiguous run for each left value x.",
                    "Both ends of that run only move right as x grows, so two pointers count all crossing pairs in linear time.",
                ],
                "steps": [
                    "Recursively sort and count both halves.",
                    "For each x in the left half, advance <code>lo</code> past values with <code>right[lo] - x &lt; lower</code> and <code>hi</code> past values with <code>right[hi] - x ≤ upper</code>; add <code>hi - lo</code>.",
                    "Merge and return the count.",
                ],
                "why": [
                    "Sorting a half keeps every element on the same side, so the index order i &lt; j across the split is preserved.",
                    "It is merge sort with a linear counting pass: O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "Sort P = [0, -2, 3, 2], split [0, -2] | [3, 2].",
                    "Inside [0, -2]: -2 - 0 = -2 is in range, 1 pair. Sorted: [-2, 0].",
                    "Inside [3, 2]: 2 - 3 = -1 is in range, 1 pair. Sorted: [2, 3].",
                    "Crossing [-2, 0] with [2, 3]: for -2, the differences are 4 and 5, so 0; for 0, the differences are 2 ✓ and 3, so 1.",
                    "The total is 1 + 1 + 1 = <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LIS II
    "longest-increasing-subsequence-ii": {
        "example": {"call": "length_of_lis([4, 2, 1, 4, 3, 4, 5, 8, 15], 3)", "expect": "5"},
        "approaches": {
            "DP with a scan over the value window": {
                "idea": [
                    "Let <code>best[v]</code> be the longest valid subsequence seen so far that ends with value v.",
                    "A new value x can extend any subsequence ending in a value from <code>x - k</code> to <code>x - 1</code>.",
                    "So <code>best[x] = 1 + max(best[x-k .. x-1])</code>, scanning that window of values.",
                ],
                "steps": [
                    "<code>best</code> is an array indexed by value, all zeros.",
                    "For each x in order: <code>best[x] = 1 + max(best[max(0, x-k):x])</code>.",
                    "Return <code>max(best)</code>.",
                ],
                "why": [
                    "Processing in array order makes sure only earlier elements are extended.",
                    "Each step scans k values: O(n·k) time and O(max value) space, too slow when both are 10<sup>5</sup>.",
                ],
                "dry": [
                    "4: window [1..3] is empty, so best[4] = 1. 2: best[2] = 1. 1: best[1] = 1.",
                    "4 again: window [1..3] has best 1, so best[4] = 2 (for example 1, 4).",
                    "3: window [0..2] has 1, so best[3] = 2. 4: window [1..3] has best[3] = 2, so best[4] = 3.",
                    "5: window [2..4] has best[4] = 3, so best[5] = 4. 8: window [5..7] has best[5] = 4, so best[8] = 5.",
                    "15: window [12..14] is empty, so 1. The maximum is <strong>5</strong>: 1, 3, 4, 5, 8.",
                ],
            },
            "Segment tree for range max": {
                "idea": [
                    "Same recurrence; the slow part was the max over a window of values.",
                    "A segment tree indexed by value answers \"max over [x-k, x)\" in O(log m) and updates one value in O(log m).",
                    "The bottom-up tree from the mutable range-sum problem works unchanged with <code>max</code> in place of <code>+</code>.",
                ],
                "steps": [
                    "<code>size = max(nums) + 1</code>; leaves are at <code>size .. 2·size - 1</code>.",
                    "For each x: <code>v = query(max(0, x-k), x) + 1</code>, then <code>update(x, v)</code>, keeping the larger value at the leaf.",
                    "The root <code>tree[1]</code> is the overall maximum.",
                ],
                "why": [
                    "The query returns exactly the max over the allowed predecessors.",
                    "It is O(log m) per element: O(n log m) time and O(m) space.",
                ],
                "dry": [
                    "The values set are identical to the scan version, but each window max comes from O(log m) tree nodes.",
                    "For example, at x=8 the query over [5, 8) combines the leaves for 5, 6 and 7 and finds best[5] = 4, so leaf 8 becomes 5.",
                    "After 15 (query [12, 15) gives 0, so leaf 15 = 1), the root holds the max of all leaves.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ falling squares
    "falling-squares": {
        "example": {"call": "falling_squares([[1, 2], [2, 3], [6, 1]])", "expect": "[2, 5, 5]"},
        "approaches": {
            "Compare against every earlier square": {
                "idea": [
                    "A falling square lands on the tallest earlier square that overlaps it horizontally, or on the ground.",
                    "Overlap means the half-open ranges <code>[left, left + side)</code> intersect; just touching edges do not count.",
                    "Its top is that base plus its side, and the answer after each drop is the tallest top so far.",
                ],
                "steps": [
                    "For square i covering <code>[left, right)</code>, set <code>base = 0</code>.",
                    "For every earlier square j that overlaps, <code>base = max(base, tops[j])</code>.",
                    "Record <code>tops[i] = base + side</code> and append the running maximum.",
                ],
                "why": [
                    "Only overlapping squares can support the new one, and it stops at the highest of them.",
                    "It is O(n²) time and O(n) space, which is fine for n ≤ 1000.",
                ],
                "dry": [
                    "Square [1, 3), side 2: nothing below, so its top is 2. The answer is <strong>2</strong>.",
                    "Square [2, 5), side 3: it overlaps [1, 3), whose top is 2, so it lands at 2 and its top is 5. The answer is <strong>5</strong>.",
                    "Square [6, 7), side 1: no overlap, so its top is 1. The tallest is still <strong>5</strong>.",
                    "The result is <strong>[2, 5, 5]</strong>.",
                ],
            },
            "Lazy segment tree over compressed coordinates": {
                "idea": [
                    "Track the height of the skyline over x. A square queries the max height over its range, then <em>sets</em> the whole range to its new top.",
                    "Compress the endpoints to indices so the tree only needs O(n) leaves.",
                    "Range assignment is lazy: a node fully covered by the update just stores the value and a pending tag, which is pushed to its children only when a later operation needs to go below it.",
                ],
                "steps": [
                    "<code>coords</code> = sorted endpoints; a square covers index range <code>[idx(left), idx(left + side))</code>.",
                    "<code>query</code> returns the max over a range, pushing tags down as it descends.",
                    "<code>assign</code> sets a range to a value, tagging fully covered nodes and recomputing partial ones.",
                    "After each square, the root's max is the tallest stack.",
                ],
                "why": [
                    "Assignment (not max) is correct because the new top is above everything currently under the square.",
                    "Lazy tags keep both operations at O(log n): O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "The coordinates [1, 2, 3, 5, 6, 7] become indices 0..5.",
                    "Square (1, 2) covers [0, 2): max 0, so top 2. Assign 2 there; root max 2, answer <strong>2</strong>.",
                    "Square (2, 3) covers [1, 3): index 1 has height 2, so top 2 + 3 = 5. Assign 5; root max 5, answer <strong>5</strong>.",
                    "Square (6, 1) covers [4, 5): height 0, so top 1. The root max stays 5, answer <strong>5</strong>.",
                    "The result is <strong>[2, 5, 5]</strong>.",
                ],
            },
        },
    },
}
