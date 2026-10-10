"""Write-ups for the Range Queries topic (prefix sums, Fenwick and segment trees)."""

EXPLAIN = {
    # ------------------------------------------------------------------ range sum immutable
    "range-sum-query-immutable": {
        "examples": [
            {"setup": "a = NumArray([-2, 0, 3, -5, 2, -1])",
             "call": "[a.sumRange(0, 2), a.sumRange(2, 5), a.sumRange(0, 5)]", "expect": "[1, -1, -3]"},
            {"setup": "a = NumArray([4, -1, 2])",
             "call": "[a.sumRange(1, 1), a.sumRange(0, 2), a.sumRange(1, 2)]", "expect": "[-1, 5, 1]"},
        ],
        "approaches": {
            "Sum the slice on every query": {
                "idea": [
                    "The array never changes, but the simplest design ignores that: store it and add up the requested slice each time.",
                    "Nothing is precomputed, so overlapping queries re-add the same numbers over and over.",
                ],
                "steps": [
                    "In <code>__init__</code>, keep a reference to <code>nums</code>.",
                    "<code>sumRange(left, right)</code> slices <code>nums[left:right + 1]</code>; the <code>+ 1</code> makes <code>right</code> inclusive.",
                    "Return <code>sum</code> of that slice.",
                    "Every query starts from scratch.",
                ],
                "why": [
                    "The slice holds exactly the elements <code>left..right</code>, so the sum is correct by definition.",
                    "Construction is <strong>O(1)</strong>, but each query reads up to n elements: <strong>O(n) per query</strong>, O(n·q) for q queries.",
                    "Only the reference is stored: <strong>O(1)</strong> extra space (the slice itself is a temporary O(n) copy).",
                ],
                "dry": [
                    [
                        "sumRange(0, 2): −2 + 0 + 3 = 1.",
                        "sumRange(2, 5): 3 − 5 + 2 − 1 = −1.",
                        "sumRange(0, 5): all six numbers, −3, re-adding everything the first two queries already read.",
                        "It returns <strong>[1, −1, −3]</strong>.",
                    ],
                    [
                        "sumRange(1, 1): the one-element slice [−1], so −1.",
                        "sumRange(0, 2): 4 − 1 + 2 = 5.",
                        "sumRange(1, 2): −1 + 2 = 1.",
                        "It returns <strong>[−1, 5, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>right + 1</code> in the slice?",
                     "Python slices exclude the end index, but <code>right</code> is inclusive in this problem. Without it, <code>sumRange(1, 1)</code> would sum an empty slice and return 0."],
                    ["When is this actually fine?",
                     "When there are very few queries. With up to 10<sup>4</sup> queries on 10<sup>4</sup> elements it does about 10<sup>8</sup> additions, which is what the problem is built to punish."],
                    ["Does slicing cost memory?",
                     "Yes, <code>nums[left:right + 1]</code> builds a temporary list. Summing with a loop over indices would avoid the copy but not the O(n) time."],
                ],
            },
            "Prefix sums": {
                "idea": [
                    "Since the array never changes, pay once up front: <code>pre[i]</code> = sum of the first i elements, with <code>pre[0] = 0</code>.",
                    "The sum of <code>nums[left..right]</code> is \"everything up to right\" minus \"everything before left\": <code>pre[right + 1] - pre[left]</code>.",
                    "Each query becomes one subtraction, no matter how long the range is.",
                ],
                "steps": [
                    "Build <code>pre = [0] + list(accumulate(nums))</code>; it has n + 1 entries.",
                    "<code>pre[i]</code> covers indices 0..i − 1.",
                    "<code>sumRange(left, right)</code> returns <code>pre[right + 1] - pre[left]</code>.",
                    "The leading 0 makes <code>left = 0</code> work without a special case.",
                ],
                "why": [
                    "<code>pre[right + 1]</code> covers 0..right and <code>pre[left]</code> covers 0..left − 1; subtracting leaves exactly left..right.",
                    "Building is one pass: <strong>O(n)</strong>. Each query is two lookups: <strong>O(1)</strong>.",
                    "The prefix list has n + 1 numbers: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "pre = [0, −2, −2, 1, −4, −2, −3].",
                        "sumRange(0, 2) = pre[3] − pre[0] = 1 − 0 = 1.",
                        "sumRange(2, 5) = pre[6] − pre[2] = −3 − (−2) = −1.",
                        "sumRange(0, 5) = pre[6] − pre[0] = −3.",
                        "It returns <strong>[1, −1, −3]</strong>.",
                    ],
                    [
                        "pre = [0, 4, 3, 5].",
                        "sumRange(1, 1) = pre[2] − pre[1] = 3 − 4 = −1.",
                        "sumRange(0, 2) = pre[3] − pre[0] = 5. sumRange(1, 2) = pre[3] − pre[1] = 1.",
                        "It returns <strong>[−1, 5, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the extra 0 at the front?",
                     "Without it, a query starting at 0 would need <code>pre[-1]</code>, which in Python is the last element. The 0 makes \"sum before index 0\" a real entry."],
                    ["Do negative numbers break prefix sums?",
                     "No. Subtraction works for any integers; prefix sums just stop being increasing, which matters only for tricks that binary-search them."],
                    ["What if the array could change?",
                     "One update would shift every later prefix, costing O(n). That is the Range Sum Query - Mutable problem, solved with Fenwick or segment trees."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ range sum mutable
    "range-sum-query-mutable": {
        "examples": [
            {"setup": "a = NumArray([1, 3, 5, 7, 9, 11])",
             "call": "[a.sumRange(1, 4), a.update(2, 10), a.sumRange(1, 4), a.sumRange(0, 5)]",
             "expect": "[24, None, 29, 41]"},
            {"setup": "a = NumArray([1, 3, 5])",
             "call": "[a.sumRange(0, 2), a.update(1, 2), a.sumRange(0, 2), a.sumRange(1, 1)]",
             "expect": "[9, None, 8, 2]"},
        ],
        "approaches": {
            "Plain array": {
                "idea": [
                    "Keep the raw array: an update is a single assignment, and a query sums the slice.",
                    "This makes updates as cheap as possible and queries as expensive as possible; the other approaches trade some update cost for faster queries.",
                ],
                "steps": [
                    "Copy <code>nums</code> into <code>self.nums</code>.",
                    "<code>update(index, val)</code> sets <code>self.nums[index] = val</code>.",
                    "<code>sumRange(left, right)</code> returns <code>sum(self.nums[left:right + 1])</code>.",
                    "Nothing else is stored or maintained.",
                ],
                "why": [
                    "The array always holds the current values, so summing the slice is always correct.",
                    "Update is <strong>O(1)</strong>; a query reads up to n values: <strong>O(n)</strong>.",
                    "Only the copy of the array is kept: <strong>O(1)</strong> extra space beyond the data itself.",
                ],
                "dry": [
                    [
                        "sumRange(1, 4): 3 + 5 + 7 + 9 = 24.",
                        "update(2, 10): nums = [1, 3, 10, 7, 9, 11].",
                        "sumRange(1, 4): 3 + 10 + 7 + 9 = 29.",
                        "sumRange(0, 5): all six = 41.",
                        "It returns <strong>[24, None, 29, 41]</strong>.",
                    ],
                    [
                        "sumRange(0, 2): 1 + 3 + 5 = 9.",
                        "update(1, 2): nums = [1, 2, 5].",
                        "sumRange(0, 2) = 8, sumRange(1, 1) = 2.",
                        "It returns <strong>[9, None, 8, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>update</code> appear as <code>None</code> in the result?",
                     "The example puts all calls in one list, and <code>update</code> returns nothing. The <code>None</code> just marks where the update happened."],
                    ["Why copy <code>nums</code> with <code>list(nums)</code>?",
                     "So updates do not silently change the caller's list. It costs O(n) once."],
                    ["Why not keep prefix sums instead?",
                     "Then queries are O(1) but an update must fix every later prefix, O(n). It just moves the cost from queries to updates."],
                ],
            },
            "Square-root decomposition": {
                "idea": [
                    "Cut the array into blocks of about √n elements and store each block's total in <code>blocks</code>.",
                    "A query adds a few loose elements at each ragged end plus whole block totals in the middle, so it touches at most about 3√n numbers.",
                    "An update fixes one element and one block total.",
                ],
                "steps": [
                    "<code>size = max(1, int(len(nums) ** 0.5))</code>; element i belongs to block <code>i // size</code>.",
                    "Sum each block into <code>blocks</code>.",
                    "<code>update</code> adds <code>val - self.nums[index]</code> to that element's block, then stores the new value.",
                    "<code>sumRange</code> first adds single elements until <code>left</code> sits on a block boundary (<code>left % b == 0</code>).",
                    "Then, while a whole block fits before <code>right</code>, it adds <code>blocks[left // b]</code> and jumps <code>left</code> by b.",
                    "Finally it adds the leftover single elements up to <code>right</code>.",
                ],
                "why": [
                    "Each index in left..right is counted exactly once: either individually in a ragged part or inside a whole block that lies completely within the range.",
                    "Update is <strong>O(1)</strong>. A query adds fewer than b ragged elements at each end and at most n / b blocks: <strong>O(√n)</strong> with b ≈ √n.",
                    "The block totals take <strong>O(√n)</strong> extra space.",
                ],
                "dry": [
                    [
                        "size = 2, blocks = [4, 12, 20, 0] (pairs 1+3, 5+7, 9+11, plus an unused empty block).",
                        "sumRange(1, 4): ragged start adds nums[1] = 3; block 1 adds 12; ragged end adds nums[4] = 9: 24.",
                        "update(2, 10): blocks[1] += 10 − 5, so blocks = [4, 17, 20, 0].",
                        "sumRange(1, 4): 3 + 17 + 9 = 29. sumRange(0, 5): blocks 0, 1, 2 = 4 + 17 + 20 = 41.",
                        "It returns <strong>[24, None, 29, 41]</strong>.",
                    ],
                    [
                        "n = 3, so size = int(1.73) = 1: every element is its own block, blocks = [1, 3, 5, 0].",
                        "sumRange(0, 2): no ragged parts, blocks 0..2 give 9.",
                        "update(1, 2): blocks[1] += 2 − 3, so blocks = [1, 2, 5, 0].",
                        "sumRange(0, 2) = 8; sumRange(1, 1) = block 1 = 2.",
                        "It returns <strong>[9, None, 8, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why update the block with a difference instead of re-summing it?",
                     "The block total changes by exactly <code>val - old</code>. Adding that is O(1); re-summing the block would be O(√n)."],
                    ["Why <code>max(1, ...)</code> in the block size?",
                     "For an empty array <code>int(0 ** 0.5)</code> is 0, and dividing by a block size of 0 would crash."],
                    ["Why is there an extra empty block at the end?",
                     "<code>len(nums) // size + 1</code> rounds up generously; when n is a multiple of the size the last block stays 0. It is harmless because no range ever reaches it."],
                ],
            },
            "Fenwick tree": {
                "idea": [
                    "A Fenwick (binary indexed) tree stores partial sums in a 1-indexed array where <code>tree[i]</code> covers a block of length <code>i &amp; -i</code> (the lowest set bit of i) ending at i.",
                    "Any prefix sum is the sum of at most log n such blocks, found by repeatedly dropping the lowest set bit. A point update touches at most log n blocks, found by adding the lowest set bit.",
                    "A range sum is then the difference of two prefix sums, as with prefix sums, but now updates are cheap too.",
                ],
                "steps": [
                    "Build: copy <code>nums</code> into <code>tree[1..n]</code>, then for each i push <code>tree[i]</code> into its parent <code>i + (i &amp; -i)</code>. This is an O(n) build.",
                    "<code>_prefix(i)</code> sums <code>nums[0:i]</code>: add <code>tree[i]</code>, then <code>i -= i &amp; -i</code>, until i is 0.",
                    "<code>update</code> computes <code>delta = val - nums[index]</code>, stores the new value, and adds delta to <code>tree[i]</code> for <code>i = index + 1, i + (i &amp; -i), …</code> up to n.",
                    "<code>sumRange(left, right)</code> returns <code>_prefix(right + 1) - _prefix(left)</code>.",
                ],
                "why": [
                    "Dropping lowest set bits splits [1, i] into disjoint blocks that exactly tile it, so <code>_prefix</code> is correct. Adding lowest set bits visits exactly the blocks that contain the updated position.",
                    "Each loop changes one bit per step, so it runs at most about log₂ n times: <strong>O(log n)</strong> per update and query, and an <strong>O(n)</strong> build.",
                    "The tree has n + 1 cells plus the copy of <code>nums</code>: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "After the build, tree = [_, 1, 4, 5, 16, 9, 20] (tree[4] = 1 + 3 + 5 + 7, tree[6] = 9 + 11).",
                        "sumRange(1, 4) = _prefix(5) − _prefix(1): path 5 → 4 gives 9 + 16 = 25, path 1 gives 1, so 24.",
                        "update(2, 10): delta = 5, i = 3 → 4: tree[3] = 10, tree[4] = 21.",
                        "sumRange(1, 4) = (9 + 21) − 1 = 29. sumRange(0, 5) = _prefix(6) = tree[6] + tree[4] = 20 + 21 = 41.",
                        "It returns <strong>[24, None, 29, 41]</strong>.",
                    ],
                    [
                        "tree = [_, 1, 4, 5] (tree[2] = 1 + 3).",
                        "sumRange(0, 2) = _prefix(3) = tree[3] + tree[2] = 5 + 4 = 9.",
                        "update(1, 2): delta = −1, i = 2 only (next is 4 &gt; 3): tree[2] = 3.",
                        "sumRange(0, 2) = 5 + 3 = 8. sumRange(1, 1) = _prefix(2) − _prefix(1) = 3 − 1 = 2.",
                        "It returns <strong>[9, None, 8, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the tree 1-indexed?",
                     "<code>i &amp; -i</code> is 0 when i = 0, so index 0 would never move and the loops would not terminate. Starting at 1 makes every index have a lowest set bit."],
                    ["Why keep <code>self.nums</code> as well as the tree?",
                     "The problem gives the new value, but the tree needs the change. Remembering the old value turns <code>val</code> into <code>delta</code>."],
                    ["How does the O(n) build work?",
                     "Each cell, once complete, adds itself into the one cell directly above it, <code>i + (i &amp; -i)</code>. Processing i in increasing order means every cell is complete before it is pushed up. Calling <code>update</code> n times would be O(n log n)."],
                ],
            },
            "Segment tree (iterative, bottom-up)": {
                "idea": [
                    "Store the leaves in <code>tree[n..2n − 1]</code> and every internal node i as <code>tree[2i] + tree[2i + 1]</code>, so node 1 is the total.",
                    "An update changes one leaf and walks up through its parents with <code>i //= 2</code>.",
                    "A query moves two boundaries <code>l</code> and <code>r</code> up the tree together, taking a node whenever a boundary sits on a node whose parent would stick out of the range.",
                ],
                "steps": [
                    "Build: <code>tree = [0] * n + nums</code>, then fill <code>tree[i]</code> for i from n − 1 down to 1.",
                    "<code>update</code>: set leaf <code>index + n</code>, then repeatedly halve i and recompute that node from its two children.",
                    "<code>sumRange</code>: <code>l = left + n</code>, <code>r = right + n + 1</code> (half-open).",
                    "While <code>l &lt; r</code>: if l is odd (a right child), take <code>tree[l]</code> and step l right.",
                    "If r is odd, step r left and take <code>tree[r]</code>.",
                    "Halve both and repeat; return the sum.",
                ],
                "why": [
                    "At each level the taken nodes are exactly the ones inside [l, r) whose parent is not fully inside, so every leaf in the range is counted once.",
                    "Each level costs O(1) and there are about log₂ n levels: <strong>O(log n)</strong> per update and per query, <strong>O(n)</strong> build.",
                    "The array has 2n cells: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "tree = [_, 36, 32, 4, 12, 20, 1, 3, 5, 7, 9, 11]: leaves at 6..11.",
                        "sumRange(1, 4): l, r = 7, 11. l odd → take tree[7] = 3; r odd → r = 10, take tree[10] = 9. Halve: 4, 5. r odd → r = 4, take tree[4] = 12. Sum 24.",
                        "update(2, 10): leaf 8 = 10, then nodes 4, 2, 1 become 17, 37, 41.",
                        "sumRange(1, 4) = 3 + 9 + 17 = 29. sumRange(0, 5): l, r = 6, 12 → 3, 6 takes tree[3] = 4 → 2, 3 takes tree[2] = 37. Sum 41.",
                        "It returns <strong>[24, None, 29, 41]</strong>.",
                    ],
                    [
                        "n = 3: tree = [_, 9, 8, 1, 3, 5], leaves at 3..5.",
                        "sumRange(0, 2): l, r = 3, 6. l odd → take tree[3] = 1. Halve: 2, 3. r odd → take tree[2] = 8. Sum 9.",
                        "update(1, 2): leaf 4 = 2, node 2 = 7, node 1 = 8.",
                        "sumRange(0, 2) = 1 + 7 = 8. sumRange(1, 1): l, r = 4, 5, r odd → take tree[4] = 2.",
                        "It returns <strong>[9, None, 8, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Does n need to be a power of two?",
                     "No. With n = 3 some internal nodes mix leaves from odd places (node 2 is leaves 1 and 2), but the l/r walk only takes nodes fully inside the range, so sums stay correct."],
                    ["Why make <code>r</code> exclusive?",
                     "With half-open [l, r) the rule is symmetric: an odd l is a right child to take, an odd r means r − 1 is a left child to take. An inclusive r needs different parity checks."],
                    ["Fenwick or segment tree?",
                     "For sums both are O(log n). The segment tree also handles min, max or any associative operation, and extends to lazy range updates; the Fenwick tree is shorter."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count of smaller numbers after self
    "count-of-smaller-numbers-after-self": {
        "examples": [
            {"call": "count_smaller([5, 2, 6, 1])", "expect": "[2, 1, 1, 0]"},
            {"call": "count_smaller([3, 1, 3, 1])", "expect": "[2, 0, 1, 0]"},
        ],
        "approaches": {
            "Compare every pair": {
                "idea": [
                    "For each position, look at everything to its right and count the values that are strictly smaller.",
                    "It is the definition written as code, and the reference the faster versions are tested against.",
                ],
                "steps": [
                    "Loop over <code>i, x</code> with <code>enumerate(nums)</code>.",
                    "For each one, scan <code>nums[i + 1:]</code>.",
                    "Count the values <code>y</code> with <code>y &lt; x</code>.",
                    "Collect the counts in order and return the list.",
                ],
                "why": [
                    "Every pair (i, j) with i &lt; j is examined once from i's side, so every smaller value to the right is counted.",
                    "About n²/2 comparisons: <strong>O(n²)</strong> time.",
                    "Apart from the output and the temporary slices, <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "5: right side [2, 6, 1], smaller are 2 and 1 → 2.",
                        "2: right side [6, 1], smaller is 1 → 1.",
                        "6: right side [1] → 1. 1: nothing to its right → 0.",
                        "It returns <strong>[2, 1, 1, 0]</strong>.",
                    ],
                    [
                        "3 (index 0): right side [1, 3, 1], the two 1s are smaller, the 3 is not → 2.",
                        "1 (index 1): right side [3, 1], nothing strictly smaller → 0.",
                        "3 (index 2): right side [1] → 1. Last 1 → 0.",
                        "It returns <strong>[2, 0, 1, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does an equal value not count?",
                     "The problem asks for strictly smaller numbers, so <code>y &lt; x</code>, not <code>&lt;=</code>. The second example checks this with repeated 3s and 1s."],
                    ["Is the slice <code>nums[i + 1:]</code> a problem?",
                     "It copies up to n elements each time, which is still within the O(n²) time. It does use O(n) temporary memory per step."],
                    ["When is this good enough?",
                     "For n up to a few thousand. The real limit (10<sup>5</sup>) needs O(n log n)."],
                ],
            },
            "Sorted list + bisect": {
                "idea": [
                    "Walk from the right, keeping every value seen so far (all values to the right of the current one) in a sorted list <code>seen</code>.",
                    "The number of smaller values to the right is then the insertion point of x: <code>bisect_left(seen, x)</code>.",
                ],
                "steps": [
                    "Start with empty <code>seen</code> and <code>out</code>.",
                    "For each <code>x</code> in <code>reversed(nums)</code>:",
                    "Append <code>bisect.bisect_left(seen, x)</code> to <code>out</code>: the count of values in <code>seen</code> below x.",
                    "Insert x with <code>bisect.insort(seen, x)</code>, keeping the list sorted.",
                    "Return <code>out[::-1]</code> to restore the original order.",
                ],
                "why": [
                    "When x is processed, <code>seen</code> holds exactly the elements to its right, sorted, and <code>bisect_left</code> skips over equal values, so it counts strictly smaller ones.",
                    "The binary search is O(log n), but <code>insort</code> shifts list elements, O(n) in the worst case: <strong>O(n²)</strong> worst case, though the shifting is a fast memory move in practice.",
                    "The sorted list holds up to n values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "x=1: seen = [] → 0; seen = [1].",
                        "x=6: bisect_left([1], 6) = 1; seen = [1, 6].",
                        "x=2: bisect_left([1, 6], 2) = 1; seen = [1, 2, 6].",
                        "x=5: bisect_left([1, 2, 6], 5) = 2; seen = [1, 2, 5, 6].",
                        "out = [0, 1, 1, 2], reversed: <strong>[2, 1, 1, 0]</strong>.",
                    ],
                    [
                        "x=1 → 0; seen = [1]. x=3 → 1; seen = [1, 3].",
                        "x=1: bisect_left([1, 3], 1) = 0, the equal 1 is not counted; seen = [1, 1, 3].",
                        "x=3: bisect_left([1, 1, 3], 3) = 2; seen = [1, 1, 3, 3].",
                        "Reversed: <strong>[2, 0, 1, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>bisect_left</code> and not <code>bisect_right</code>?",
                     "<code>bisect_left</code> stops before equal values, so it counts strictly smaller ones. <code>bisect_right</code> would also count equal values: for the second example it would return [3, 1, 1, 0]."],
                    ["Why process from the right?",
                     "Then the structure always holds exactly the \"after self\" elements. Going left to right you would count smaller values before each element."],
                    ["Why is it fast in practice despite O(n²)?",
                     "The shift inside <code>insort</code> is a single C-level memory move, very fast per element. For n = 10<sup>5</sup> it usually passes; a sorted container or a Fenwick tree removes the worst case."],
                ],
            },
            "Merge sort, counting right-to-left jumps": {
                "idea": [
                    "During merge sort, when an element from the left half is placed, every right-half element already placed before it is smaller and was originally to its right.",
                    "So while merging, add <code>j</code>, the number of right-half elements placed so far, to that element's count.",
                    "The sort works on indices so counts can be credited to original positions.",
                ],
                "steps": [
                    "<code>sort(idx)</code> sorts a list of indices by their values; lists of length ≤ 1 are returned as is.",
                    "Split at <code>mid</code>, recursively sort <code>left</code> and <code>right</code>.",
                    "For each index <code>i</code> in <code>left</code>, first move right-half indices with smaller values into <code>merged</code>, advancing <code>j</code>.",
                    "Then <code>res[i] += j</code> and append <code>i</code>.",
                    "Append the remaining right indices; return <code>merged</code>.",
                    "Call <code>sort</code> on all indices and return <code>res</code>.",
                ],
                "why": [
                    "Every pair (i, k) with i before k lies in different halves at exactly one merge, where i is on the left; it is counted there iff <code>nums[k] &lt; nums[i]</code>.",
                    "The strict <code>&lt;</code> keeps equal right-half values behind, so they are not counted.",
                    "Standard merge sort: <strong>O(n log n)</strong> time, with <strong>O(n)</strong> for <code>res</code> and the merged lists at each level.",
                ],
                "dry": [
                    [
                        "Merge [5] with [2]: 2 &lt; 5 moves first, j = 1, res[0] += 1.",
                        "Merge [6] with [1]: j = 1, res[2] += 1.",
                        "Merge [2, 5] with [1, 6]: for 2, the 1 moves first, j = 1, res[1] += 1; for 5, 6 is not smaller, j stays 1, res[0] += 1.",
                        "res = [2, 1, 1, 0].",
                        "It returns <strong>[2, 1, 1, 0]</strong>.",
                    ],
                    [
                        "Merge [3] with [1]: res[0] += 1. Merge [3] with [1]: res[2] += 1.",
                        "Merge [1, 3] (indices 1, 0) with [1, 3] (indices 3, 2).",
                        "For the 1 at index 1: the right 1 is not smaller, j = 0, so +0.",
                        "For the 3 at index 0: the right 1 moves, j = 1; the right 3 is not smaller, so res[0] += 1.",
                        "It returns <strong>[2, 0, 1, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort indices instead of values?",
                     "After sorting, values have moved, so the count would not know where to go. Sorting indices keeps the original position <code>i</code> to credit in <code>res[i]</code>."],
                    ["Why is <code>j</code> not reset for each left element?",
                     "Left elements arrive in increasing order, so everything smaller than an earlier one is also smaller than a later one. <code>j</code> only grows, which keeps the merge linear."],
                    ["What happens with equal values?",
                     "The left copy is placed before the equal right copy, because the while loop needs strictly smaller. So equal values never add to each other's counts."],
                ],
            },
            "Fenwick tree over value ranks": {
                "idea": [
                    "Walk from the right and keep a count of every value seen so far. For x, the answer is how many seen values are smaller: a prefix count.",
                    "A Fenwick tree gives prefix counts and point increments in O(log n), but it needs small positive indices, so values are first compressed to ranks 1..k.",
                ],
                "steps": [
                    "<code>rank</code> maps each distinct value, in sorted order, to 1, 2, …",
                    "<code>tree</code> has <code>len(rank) + 1</code> cells; <code>add(i)</code> adds 1 along <code>i += i &amp; -i</code>.",
                    "<code>prefix(i)</code> sums counts of ranks 1..i along <code>i -= i &amp; -i</code>.",
                    "For each <code>x</code> from the right: append <code>prefix(rank[x] - 1)</code>, the seen values strictly smaller, then <code>add(rank[x])</code>.",
                    "Return the list reversed.",
                ],
                "why": [
                    "Ranks keep order, so \"value smaller than x\" is \"rank at most rank[x] − 1\", and the tree counts exactly the elements to the right.",
                    "Sorting for the ranks is O(n log n), then n adds and n prefix queries at O(log n) each: <strong>O(n log n)</strong> time.",
                    "The rank map and the tree are O(n): <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "rank = {1: 1, 2: 2, 5: 3, 6: 4}.",
                        "x=1: prefix(0) = 0, add rank 1. x=6: prefix(3) = 1, add rank 4.",
                        "x=2: prefix(1) = 1 (the 1), add rank 2.",
                        "x=5: prefix(2) = 2 (the 1 and the 2), add rank 3.",
                        "out = [0, 1, 1, 2], reversed: <strong>[2, 1, 1, 0]</strong>.",
                    ],
                    [
                        "rank = {1: 1, 3: 2}.",
                        "x=1: prefix(0) = 0, add rank 1. x=3: prefix(1) = 1, add rank 2.",
                        "x=1: prefix(0) = 0, the seen 1 has the same rank and is excluded. Add rank 1.",
                        "x=3: prefix(1) = 2, the two 1s.",
                        "Reversed: <strong>[2, 0, 1, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compress values to ranks?",
                     "Values can be negative or as large as 10<sup>4</sup> in either direction, and the tree needs indices 1..k. Ranks keep only the order, which is all the comparison needs."],
                    ["Why <code>rank[x] - 1</code>?",
                     "It excludes x's own rank, so equal values are not counted as smaller."],
                    ["Merge sort or Fenwick tree?",
                     "Both are O(n log n). The Fenwick version is easier to adapt to \"larger than\", \"within a range\" or online input; the merge sort version needs no compression."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ create sorted array through instructions
    "create-sorted-array-through-instructions": {
        "examples": [
            {"call": "create_sorted_array([1, 5, 6, 2])", "expect": "1"},
            {"call": "create_sorted_array([4, 1, 4, 2, 3])", "expect": "3"},
        ],
        "approaches": {
            "Sorted list + bisect": {
                "idea": [
                    "Inserting x costs min(count strictly less than x, count strictly greater than x) among the values already inserted.",
                    "Keep the inserted values in a sorted list: <code>bisect_left</code> gives the count less than x, and <code>len - bisect_right</code> gives the count greater.",
                ],
                "steps": [
                    "Start with empty <code>seen</code> and <code>cost = 0</code>.",
                    "For each <code>x</code>: <code>less = bisect_left(seen, x)</code>.",
                    "<code>greater = len(seen) - bisect_right(seen, x)</code>; copies equal to x sit between the two bisect points and count for neither.",
                    "Add <code>min(less, greater)</code> to <code>cost</code>, then <code>insort(seen, x)</code>.",
                    "Return <code>cost % (10**9 + 7)</code>.",
                ],
                "why": [
                    "In a sorted list, <code>bisect_left</code> is the number of elements below x and <code>bisect_right</code> the number at or below x, so both counts are exact.",
                    "Each step does two O(log n) searches but an insertion that may shift O(n) elements: <strong>O(n²)</strong> worst case.",
                    "The list holds every value: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "x=1: empty, cost 0. seen = [1].",
                        "x=5: less 1, greater 0 → 0. x=6: less 2, greater 0 → 0.",
                        "x=2: seen = [1, 5, 6], less 1, greater 2 → min 1.",
                        "It returns <strong>1</strong>.",
                    ],
                    [
                        "x=4: cost 0. x=1: less 0, greater 1 → 0.",
                        "x=4: seen = [1, 4], less 1, greater 0 (the equal 4 is not greater) → 0.",
                        "x=2: seen = [1, 4, 4], less 1, greater 2 → 1.",
                        "x=3: seen = [1, 2, 4, 4], less 2, greater 2 → 2. Total 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why two different bisects?",
                     "Equal values count as neither less nor greater. <code>bisect_left</code> stops before them and <code>bisect_right</code> after them, so both counts exclude them."],
                    ["Why take the modulo only at the end?",
                     "Python integers do not overflow, so the sum is exact. The modulo only matches the required output format."],
                    ["Is O(n²) too slow here?",
                     "In theory for n = 10<sup>5</sup>, yes, though the C-level shift often passes. The Fenwick tree version has no bad case."],
                ],
            },
            "Fenwick tree over values": {
                "idea": [
                    "Values are at most 10<sup>5</sup>, so index a Fenwick tree directly by value and store how many times each value has been inserted.",
                    "\"Less than x\" is <code>prefix(x - 1)</code>; \"greater than x\" is everything inserted so far minus <code>prefix(x)</code>.",
                ],
                "steps": [
                    "<code>m = max(instructions)</code>; <code>tree</code> has m + 1 cells.",
                    "<code>add(i)</code> increments counts along <code>i += i &amp; -i</code>; <code>prefix(i)</code> sums along <code>i -= i &amp; -i</code>.",
                    "For the i-th instruction x, i values are already inserted.",
                    "<code>cost += min(prefix(x - 1), i - prefix(x))</code>, then <code>add(x)</code>.",
                    "Return <code>cost % (10**9 + 7)</code>.",
                ],
                "why": [
                    "<code>prefix(x - 1)</code> counts values ≤ x − 1, i.e. strictly less; <code>i - prefix(x)</code> counts the inserted values above x, so equal values are left out of both.",
                    "Each instruction does two prefix queries and one add, each O(log m): <strong>O(n log m)</strong> time.",
                    "The tree has m + 1 cells: <strong>O(m)</strong> space, where m is the largest value.",
                ],
                "dry": [
                    [
                        "m = 6. x=1 (i=0): min(0, 0) = 0, add 1.",
                        "x=5 (i=1): less = prefix(4) = 1, greater = 1 − prefix(5) = 0 → 0.",
                        "x=6 (i=2): less 2, greater 0 → 0.",
                        "x=2 (i=3): less = prefix(1) = 1, greater = 3 − prefix(2) = 2 → 1.",
                        "It returns <strong>1</strong>.",
                    ],
                    [
                        "m = 4. x=4: 0. x=1: less 0, greater 1 − 0 = 1 → 0.",
                        "x=4 (i=2): less = prefix(3) = 1, greater = 2 − prefix(4) = 0 → 0.",
                        "x=2 (i=3): less 1, greater 3 − 1 = 2 → 1.",
                        "x=3 (i=4): less = prefix(2) = 2, greater = 4 − 2 = 2 → 2. Total 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why no value compression here?",
                     "Values are between 1 and 10<sup>5</sup>, so they are already valid Fenwick indices and the tree stays small."],
                    ["Why <code>i - prefix(x)</code> for the greater count?",
                     "Exactly i values have been inserted before this one, and <code>prefix(x)</code> of them are ≤ x; the rest are greater."],
                    ["What would break with a value of 0?",
                     "<code>add(0)</code> would loop forever, since <code>0 &amp; -0</code> is 0. The problem guarantees values ≥ 1; otherwise shift every value by one."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse pairs
    "reverse-pairs": {
        "examples": [
            {"call": "reverse_pairs([2, 4, 3, 5, 1])", "expect": "3"},
            {"call": "reverse_pairs([-5, -5])", "expect": "1"},
        ],
        "approaches": {
            "Every pair": {
                "idea": [
                    "A reverse pair is i &lt; j with <code>nums[i] &gt; 2 * nums[j]</code>. Check every such pair.",
                    "It is the definition, and the baseline the faster methods must match.",
                ],
                "steps": [
                    "Loop <code>i</code> over every index.",
                    "Loop <code>j</code> over every index after <code>i</code>.",
                    "Count the pair when <code>nums[i] &gt; 2 * nums[j]</code>.",
                    "Return the total with <code>sum</code> over the generator.",
                ],
                "why": [
                    "Every pair with i &lt; j is tested exactly once, so nothing is missed or double counted.",
                    "n(n − 1)/2 pairs: <strong>O(n²)</strong> time.",
                    "Only loop counters: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (2): later values doubled are 8, 6, 10, 2; 2 is not greater than any of them → 0.",
                        "i=1 (4): 4 &gt; 2·1 → 1 pair. i=2 (3): 3 &gt; 2·1 → 1 pair.",
                        "i=3 (5): 5 &gt; 2·1 → 1 pair.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "Only pair (0, 1): −5 &gt; 2·(−5) = −10 is true.",
                        "Doubling a negative number makes it smaller, so equal negatives form a pair.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>[-5, -5]</code> a reverse pair?",
                     "2 · (−5) = −10 and −5 &gt; −10. With negatives, doubling moves the value down, so a pair can exist even between equal values."],
                    ["Can <code>2 * nums[j]</code> overflow?",
                     "Not in Python. In Java or C++ with 32-bit ints it can, which is why the test with 2147483647 exists; use 64-bit arithmetic there."],
                    ["Is this enough for the real limits?",
                     "No: n up to 5·10<sup>4</sup> means over 10<sup>9</sup> pairs. It is only the reference answer."],
                ],
            },
            "Merge sort with a separate counting pass": {
                "idea": [
                    "Split the array in half. Pairs inside each half are counted recursively; pairs crossing the middle have i in the left half and j in the right half.",
                    "Once both halves are sorted, the cross pairs can be counted with two pointers: for increasing x in the left half, the number of right values with <code>x &gt; 2 * right[j]</code> only grows.",
                    "The counting pass is separate from merging because the pair condition (x &gt; 2y) is not the sort order (x &gt; y).",
                ],
                "steps": [
                    "<code>sort(a)</code> returns <code>(sorted a, count)</code>; length ≤ 1 gives <code>(a, 0)</code>.",
                    "Recurse on <code>a[:mid]</code> and <code>a[mid:]</code> to get sorted halves and their counts.",
                    "Walk <code>x</code> over the sorted left half; advance <code>j</code> while <code>x &gt; 2 * right[j]</code>.",
                    "Add <code>j</code> to <code>count</code> for each x.",
                    "Return <code>sorted(left + right)</code> and the count; the answer is <code>sort(nums)[1]</code>.",
                ],
                "why": [
                    "Each pair i &lt; j is split between the two halves at exactly one level, and sorting within a half does not change which side an element is on.",
                    "Because both halves are sorted, <code>j</code> never moves back, so each counting pass is linear. With log n levels the total is <strong>O(n log n)</strong>; <code>sorted</code> on two sorted runs is a linear merge in Timsort.",
                    "The slices and merged lists use <strong>O(n)</strong> per level of recursion at a time.",
                ],
                "dry": [
                    [
                        "Split [2, 4] | [3, 5, 1]; [3, 5, 1] splits into [3] | [5, 1].",
                        "[2] vs [4]: 2 &gt; 8? no → 0. [5] vs [1]: 5 &gt; 2 → 1.",
                        "[3] vs [1, 5]: 3 &gt; 2 → j = 1, 3 &gt; 10 no → +1. Running count 2.",
                        "[2, 4] vs [1, 3, 5]: x=2: 2 &gt; 2? no → 0. x=4: 4 &gt; 2 → j = 1, 4 &gt; 6 no → +1.",
                        "Total <strong>3</strong>.",
                    ],
                    [
                        "Split [−5] | [−5].",
                        "x = −5: −5 &gt; 2·(−5) = −10, so j = 1.",
                        "Count 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not count during the merge like for inversions?",
                     "The merge compares x with y, but the pair test compares x with 2y. A separate pass keeps both conditions simple and correct."],
                    ["Why can <code>j</code> carry over from one x to the next?",
                     "x increases along the sorted left half, so any right value that satisfied x &gt; 2y for a smaller x still satisfies it."],
                    ["Does <code>sorted(left + right)</code> ruin the complexity?",
                     "No: Timsort finds the two sorted runs and merges them in linear time. A hand-written merge would be the same cost."],
                ],
            },
            "Fenwick tree over compressed values": {
                "idea": [
                    "Scan left to right. For each y, count earlier values greater than <code>2 * y</code>: all earlier values minus those ≤ 2y.",
                    "A Fenwick tree over the sorted distinct values answers \"how many seen values are ≤ t\" in O(log n), after locating t with <code>bisect_right</code>.",
                ],
                "steps": [
                    "<code>vals = sorted(set(nums))</code>; rank of a value is its position in <code>vals</code> plus 1.",
                    "For each index <code>seen</code> and value <code>y</code>:",
                    "<code>at_most = bisect_right(vals, 2 * y)</code>: the number of distinct values ≤ 2y, which is also the rank bound to query.",
                    "<code>count += seen - prefix(at_most)</code>: earlier values greater than 2y.",
                    "Insert y with <code>add(bisect_left(vals, y) + 1)</code>.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Ranks preserve order, so \"seen values ≤ 2y\" equals \"seen values with rank ≤ at_most\", even though 2y itself may not be in <code>vals</code>.",
                    "Sorting plus, per element, two binary searches and two O(log n) tree walks: <strong>O(n log n)</strong> time.",
                    "<code>vals</code> and <code>tree</code> are O(n): <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "vals = [1, 2, 3, 4, 5].",
                        "y=2: 2y = 4, nothing seen → 0. y=4: 2y = 8, all 1 seen ≤ 8 → 0.",
                        "y=3: 2y = 6 → 0. y=5: 2y = 10 → 0.",
                        "y=1: 2y = 2, at_most = 2; of 4 seen values only the 2 is ≤ 2, so 4 − 1 = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "vals = [−5].",
                        "y=−5 (seen 0): 0 − 0 = 0. Add rank 1.",
                        "y=−5 (seen 1): 2y = −10, at_most = 0, so 1 − prefix(0) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compress only the values and not 2y too?",
                     "<code>bisect_right(vals, 2 * y)</code> maps 2y to the right rank boundary without inserting it, so the tree stays one cell per distinct value."],
                    ["Why <code>bisect_right</code> for the query but <code>bisect_left</code> for the insert?",
                     "The query needs every value ≤ 2y, including equal ones, so it goes past them. The insert needs the exact rank of y, which <code>bisect_left</code> gives because y is in <code>vals</code>."],
                    ["Does this handle negative values?",
                     "Yes. Only order matters after compression, and the second example shows the negative case giving 1."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count of range sum
    "count-of-range-sum": {
        "examples": [
            {"call": "count_range_sum([-2, 5, -1], -2, 2)", "expect": "3"},
            {"call": "count_range_sum([1, -1, 1], 0, 0)", "expect": "2"},
        ],
        "approaches": {
            "Every subarray via prefix sums": {
                "idea": [
                    "With prefix sums P (P[0] = 0), the subarray from i to j − 1 sums to <code>P[j] - P[i]</code>.",
                    "So count pairs i &lt; j of prefix sums whose difference lies in [lower, upper], each in O(1).",
                ],
                "steps": [
                    "Build <code>P = [0] + list(accumulate(nums))</code>.",
                    "For every <code>j</code> from 1 to n and every <code>i &lt; j</code>:",
                    "Count it when <code>lower &lt;= P[j] - P[i] &lt;= upper</code>.",
                    "Return the count.",
                ],
                "why": [
                    "Every non-empty subarray corresponds to exactly one pair i &lt; j of prefix indices.",
                    "About n²/2 pairs with O(1) work: <strong>O(n²)</strong> time.",
                    "The prefix list: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "P = [0, −2, 3, 2].",
                        "(0, 1): −2, in range. (0, 2): 3, too big. (1, 2): 5, too big.",
                        "(0, 3): 2, in range. (1, 3): 4, too big. (2, 3): −1, in range.",
                        "It returns <strong>3</strong>: [−2], [−2, 5, −1] and [−1].",
                    ],
                    [
                        "P = [0, 1, 0, 1].",
                        "Differences equal to 0 need equal prefix sums: pairs (0, 2) and (1, 3).",
                        "Those are [1, −1] and [−1, 1].",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why prefix sums instead of summing each subarray?",
                     "Summing each subarray directly would be O(n³). The prefix difference gives each sum in O(1)."],
                    ["Why does <code>P</code> start with 0?",
                     "It represents the empty prefix, so subarrays starting at index 0 are the pairs (0, j)."],
                    ["What does this reduce the problem to?",
                     "Counting pairs i &lt; j with P[j] − upper ≤ P[i] ≤ P[j] − lower: a range count over earlier values, which the faster approaches do in log time."],
                ],
            },
            "Fenwick tree over prefix sums": {
                "idea": [
                    "Scan the prefix sums left to right. For the current p, earlier prefix values in <code>[p - upper, p - lower]</code> each give a valid subarray.",
                    "Count those with a Fenwick tree over the compressed prefix values: a range count is <code>prefix(hi) - prefix(lo)</code>.",
                ],
                "steps": [
                    "Build <code>P</code> and <code>vals = sorted(set(P))</code>.",
                    "For each <code>p</code> in <code>P</code>: <code>lo = bisect_left(vals, p - upper)</code> is the number of ranks below the window.",
                    "<code>hi = bisect_right(vals, p - lower)</code> is the number of ranks up to the window's end.",
                    "<code>count += prefix(hi) - prefix(lo)</code>: seen prefix values inside the window.",
                    "Then <code>add</code> p's rank, so it is visible to later prefixes only.",
                ],
                "why": [
                    "P[j] − P[i] ∈ [lower, upper] is the same as P[i] ∈ [P[j] − upper, P[j] − lower], and the tree holds exactly the P[i] with i &lt; j.",
                    "Sorting plus a constant number of bisects and tree walks per prefix: <strong>O(n log n)</strong> time.",
                    "<code>P</code>, <code>vals</code> and <code>tree</code>: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "P = [0, −2, 3, 2], vals = [−2, 0, 2, 3].",
                        "p=0: window [−2, 2], nothing seen → 0. Add 0.",
                        "p=−2: window [−4, 0] contains the seen 0 → 1.",
                        "p=3: window [1, 5] has no seen value → 0. p=2: window [0, 4] contains 0 and 3 → 2.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "P = [0, 1, 0, 1], vals = [0, 1].",
                        "p=0 and p=1: windows [0, 0] and [1, 1], no earlier match → 0.",
                        "p=0 (third): the first 0 is in [0, 0] → 1.",
                        "p=1 (fourth): the earlier 1 is in [1, 1] → 1.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why query before adding the current prefix?",
                     "A prefix paired with itself is an empty subarray. Adding first would count it whenever 0 is in [lower, upper]."],
                    ["Why <code>bisect_left</code> for the low end and <code>bisect_right</code> for the high end?",
                     "Both ends are inclusive. <code>bisect_left</code> excludes only values strictly below p − upper; <code>bisect_right</code> includes values equal to p − lower."],
                    ["Why compress at all?",
                     "Prefix sums can be huge or negative; the tree needs small indices. Only their order matters for range counts."],
                ],
            },
            "Merge sort on prefix sums": {
                "idea": [
                    "Run merge sort on the prefix array. Pairs (i, j) with i in the left half and j in the right half are counted at the merge, where both halves are sorted.",
                    "For each left value x, the right values in <code>[x + lower, x + upper]</code> form a contiguous block, tracked by two pointers <code>lo</code> and <code>hi</code> that only move forward.",
                ],
                "steps": [
                    "<code>sort(a)</code> returns <code>(sorted a, count)</code>; length ≤ 1 gives 0.",
                    "Recurse on both halves and add their counts.",
                    "For each <code>x</code> in the sorted left half: advance <code>lo</code> while <code>right[lo] - x &lt; lower</code>.",
                    "Advance <code>hi</code> while <code>right[hi] - x &lt;= upper</code>.",
                    "Add <code>hi - lo</code>, then return <code>sorted(left + right)</code> with the count.",
                    "Call it on <code>[0] + list(accumulate(nums))</code>.",
                ],
                "why": [
                    "Every pair i &lt; j of prefix indices is split across halves at exactly one level, with P[i] on the left and P[j] on the right, so it is counted once.",
                    "As x increases, both window ends move right, so each merge level is linear: <strong>O(n log n)</strong> time.",
                    "Slices and merged lists: <strong>O(n)</strong> space per level.",
                ],
                "dry": [
                    [
                        "Prefix list [0, −2, 3, 2] splits into [0, −2] and [3, 2].",
                        "[0] vs [−2]: −2 − 0 = −2 is in range → 1. [3] vs [2]: −1 is in range → 1.",
                        "[−2, 0] vs [2, 3]: x=−2: differences 4, 5, none → 0. x=0: 2 is in range, 3 is not → 1.",
                        "Total 1 + 1 + 1 = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "Prefix list [0, 1, 0, 1] splits into [0, 1] and [0, 1].",
                        "[0] vs [1]: difference 1 → 0. [0] vs [1] again → 0.",
                        "[0, 1] vs [0, 1]: x=0 matches the right 0 (lo 0, hi 1) → 1; x=1 matches the right 1 (lo 1, hi 2) → 1.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort prefix sums, not <code>nums</code>?",
                     "Range sums are differences of prefix sums. Sorting <code>nums</code> would lose which subarrays exist."],
                    ["Doesn't sorting the halves break the i &lt; j order?",
                     "No: sorting happens inside each half, and every left element still came before every right element in the original order."],
                    ["Why can <code>lo</code> and <code>hi</code> keep their positions between x values?",
                     "x only increases, so the lower bound x + lower and upper bound x + upper only increase. A right value that was too small stays too small."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest increasing subsequence ii
    "longest-increasing-subsequence-ii": {
        "examples": [
            {"call": "length_of_lis([3, 1, 5, 2, 4], 2)", "expect": "3"},
            {"call": "length_of_lis([2, 2, 3], 1)", "expect": "2"},
        ],
        "approaches": {
            "DP with a scan over the value window": {
                "idea": [
                    "Index the DP by <strong>value</strong>: <code>best[v]</code> is the longest valid subsequence seen so far that ends with value v.",
                    "A new x can follow any previous value in <code>[x - k, x - 1]</code>, so <code>best[x] = 1 + max(best[x - k .. x - 1])</code>.",
                    "Processing elements in order guarantees only earlier elements are used.",
                ],
                "steps": [
                    "Create <code>best = [0] * (max(nums) + 1)</code>.",
                    "For each <code>x</code>: <code>lo = max(0, x - k)</code>.",
                    "<code>best[x] = 1 + max(best[lo:x], default=0)</code>.",
                    "The slice excludes x itself, so equal values never chain.",
                    "Return <code>max(best)</code>.",
                ],
                "why": [
                    "When x is processed, <code>best</code> only reflects earlier elements, and the slice covers exactly the values allowed before x. A later equal x recomputes the same or a larger value.",
                    "Each element scans a window of k values: <strong>O(n·k)</strong> time.",
                    "The table is indexed by value: <strong>O(m)</strong> space for m = max(nums).",
                ],
                "dry": [
                    [
                        "x=3: window best[1:3] all 0 → best[3] = 1.",
                        "x=1: window best[0:1] → best[1] = 1. x=5: window best[3:5] has best[3] = 1 → best[5] = 2.",
                        "x=2: window best[0:2] has best[1] = 1 → best[2] = 2.",
                        "x=4: window best[2:4] = [2, 1] → best[4] = 3 (1, 2, 4).",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "x=2: window best[1:2] = [0] → best[2] = 1.",
                        "x=2 again: same window, best[2] stays 1: 2, 2 is not increasing.",
                        "x=3: window best[2:3] = [1] → best[3] = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can <code>best[x]</code> be overwritten safely?",
                     "A later x sees every earlier element, so its result is at least as large as the earlier one. Overwriting never loses a longer chain."],
                    ["Why index by value rather than by position?",
                     "The constraint is on values (difference at most k), so a value-indexed table turns \"which earlier elements qualify\" into a contiguous range."],
                    ["When is O(n·k) too slow?",
                     "With n and k both up to 10<sup>5</sup> it is 10<sup>10</sup> steps. The window max needs a faster structure: the segment tree."],
                ],
            },
            "Segment tree for range max": {
                "idea": [
                    "Same value-indexed DP, but the window maximum <code>max(best[x - k .. x - 1])</code> now comes from a segment tree in O(log m) instead of a scan.",
                    "Leaves are <code>best[v]</code>; each internal node stores the max of its children, and the root <code>tree[1]</code> is the answer.",
                ],
                "steps": [
                    "<code>size = max(nums) + 1</code>, <code>tree = [0] * (2 * size)</code> with leaves at <code>size..2·size − 1</code>.",
                    "<code>query(l, r)</code> returns the max over leaves [l, r) with the iterative l/r walk.",
                    "<code>update(i, val)</code> raises leaf i to <code>val</code> and recomputes its ancestors.",
                    "For each <code>x</code>: <code>update(x, query(max(0, x - k), x) + 1)</code>.",
                    "Return <code>tree[1]</code>.",
                ],
                "why": [
                    "The tree always stores the current <code>best</code> array, so the query gives exactly the window max the DP needs.",
                    "One query and one update per element, each O(log m): <strong>O(n log m)</strong> time.",
                    "2·size cells: <strong>O(m)</strong> space.",
                ],
                "dry": [
                    [
                        "size = 6, leaves for values 0..5 at tree[6..11].",
                        "x=3: query [1, 3) = 0 → leaf 3 = 1. x=1: query [0, 1) = 0 → leaf 1 = 1.",
                        "x=5: query [3, 5) visits nodes 9, 10 → 1, so leaf 5 = 2.",
                        "x=2: query [0, 2) is node 3 → 1, leaf 2 = 2. x=4: query [2, 4) is node 4 → 2, leaf 4 = 3.",
                        "The root is <strong>3</strong>.",
                    ],
                    [
                        "size = 4, leaves at tree[4..7].",
                        "x=2: query [1, 2) = leaf 1 = 0 → leaf 2 = 1.",
                        "x=2 again: same query → 1, leaf 2 stays 1.",
                        "x=3: query [2, 3) = leaf 2 = 1 → leaf 3 = 2. Root <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>update</code> take a max at the leaf?",
                     "A later equal value always gives at least the same length, so <code>max</code> just makes the update safe; it never lowers a leaf."],
                    ["Does <code>size</code> need to be a power of two?",
                     "No. The iterative tree works for any size: each query takes only nodes inside [l, r), and every leaf still reaches the root, so <code>tree[1]</code> is the overall max."],
                    ["Why the half-open query <code>[x - k, x)</code>?",
                     "It excludes x itself, which enforces strictly increasing; including x would let equal values chain."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ falling squares
    "falling-squares": {
        "examples": [
            {"call": "falling_squares([[1, 2], [2, 3], [6, 1]])", "expect": "[2, 5, 5]"},
            {"call": "falling_squares([[1, 2], [3, 2]])", "expect": "[2, 2]"},
        ],
        "approaches": {
            "Compare against every earlier square": {
                "idea": [
                    "A new square lands on the tallest earlier square it horizontally overlaps, so its top is <code>base + side</code> where <code>base</code> is that tallest top.",
                    "Overlap uses half-open intervals [left, left + side): squares that only touch at an edge do not stack.",
                    "The answer after each drop is the running max of all tops.",
                ],
                "steps": [
                    "Keep <code>tops</code> (top height of each square), <code>out</code> and <code>best</code>.",
                    "For square i, <code>right = left + side</code>, <code>base = 0</code>.",
                    "For each earlier square j, if <code>l2 &lt; right and left &lt; l2 + s2</code>, raise <code>base</code> to <code>tops[j]</code>.",
                    "Append <code>base + side</code> to <code>tops</code>, update <code>best</code>, append it to <code>out</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "A square stops at the highest surface below it; any surface it overlaps is the top of some earlier square, and <code>tops[j]</code> records the height of that top.",
                    "Square i compares with i earlier squares: <strong>O(n²)</strong> time.",
                    "<code>tops</code> and <code>out</code>: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Square [1, 3): nothing before, top 2, best 2.",
                        "Square [2, 5): overlaps square 0 (1 &lt; 5 and 2 &lt; 3), base 2, top 5, best 5.",
                        "Square [6, 7): no overlap, top 1, best stays 5.",
                        "It returns <strong>[2, 5, 5]</strong>.",
                    ],
                    [
                        "Square [1, 3): top 2.",
                        "Square [3, 5): test 1 &lt; 5 and 3 &lt; 3 fails, they only touch at x = 3.",
                        "Its base is 0 and top 2; best stays 2.",
                        "It returns <strong>[2, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why strict <code>&lt;</code> in the overlap test?",
                     "Squares sharing only an edge do not support each other. With <code>&lt;=</code> the second example would wrongly stack to [2, 4]."],
                    ["Why <code>tops[j]</code> and not the height at the exact overlap?",
                     "Each square has a flat top over its whole width, so wherever it overlaps, the surface height is <code>tops[j]</code>."],
                    ["Is O(n²) acceptable?",
                     "n is at most 1000 in the problem, so yes. The segment tree matters when n is much larger."],
                ],
            },
            "Lazy segment tree over compressed coordinates": {
                "idea": [
                    "Treat the ground as a height map. Each drop is a <strong>range max query</strong> (highest point under the square) followed by a <strong>range assign</strong> (that whole range becomes the new top).",
                    "Only square edges matter, so compress them: <code>coords</code> are the sorted edges, and slot i is the strip [coords[i], coords[i + 1]).",
                    "A lazy segment tree does both operations in O(log n): <code>lazy[node]</code> remembers a pending assignment that has not yet been pushed to the children.",
                ],
                "steps": [
                    "Collect every <code>left</code> and <code>left + side</code> into <code>coords</code>; <code>idx</code> maps an edge to its slot.",
                    "<code>push(node)</code> copies a pending assignment down to both children, then clears it.",
                    "<code>query</code> returns 0 outside [l, r), <code>mx[node]</code> when the node is fully inside, otherwise pushes and recurses on both halves.",
                    "<code>assign</code> sets <code>mx</code> and <code>lazy</code> on fully covered nodes and stops there; partial nodes push, recurse, and recompute their max.",
                    "For each square: <code>top = query(slots) + side</code>, <code>assign(slots, top)</code>, and append <code>mx[1]</code>, the tallest point overall.",
                ],
                "why": [
                    "After each drop the leaves describe the true skyline over the strips, because a square overwrites exactly the strips it covers with its top height.",
                    "Each query and assign touches O(log n) nodes thanks to lazy tags: <strong>O(n log n)</strong> time, including sorting the coordinates.",
                    "<code>mx</code> and <code>lazy</code> have 4·(2n) cells: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "coords = [1, 2, 3, 5, 6, 7]; square [1, 2] covers slots [0, 2).",
                        "Square 1: query = 0, top 2. Assign covers node 4 (slot 0) and node 10 (slot 1). mx[1] = 2.",
                        "Square 2 (slots [1, 3)): query reaches height 2 under slot 1, top 5. Assign covers node 5 = slots 1..2 in one go. mx[1] = 5.",
                        "Square 3 (slot [4, 5)): query = 0, top 1, node 14 set to 1. mx[1] stays 5.",
                        "It returns <strong>[2, 5, 5]</strong>.",
                    ],
                    [
                        "coords = [1, 3, 5]; the squares use slots [0, 1) and [1, 2).",
                        "Square 1: query 0, top 2, node 2 (slot 0) = 2.",
                        "Square 2: query over slot 1 only gives 0, because the shared edge x = 3 starts a new slot.",
                        "Top 2, node 6 (slot 1) = 2; mx[1] = 2.",
                        "It returns <strong>[2, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the tree assign instead of taking a max?",
                     "The new top is at least as high as everything under the square, because it was computed from the max plus a positive side. So overwriting is the same as raising."],
                    ["Why are slots half-open strips between edges?",
                     "A square [l, l + side) covers exactly the strips from <code>idx[l]</code> up to but not including <code>idx[l + side]</code>, so touching squares share no slot."],
                    ["What does <code>push</code> protect against?",
                     "A node with a pending assignment still has stale children. Before reading or writing inside it, the assignment must be copied down, or a later partial query would see old heights."],
                ],
            },
        },
    },
}
