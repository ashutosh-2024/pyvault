"""Write-ups for Dynamic Programming, part 4: longest increasing subsequence family."""

_TAKE_SKIP_RECURSION = [
    "<code>f(i, prev)</code> = the best length using elements i onward, when the last element taken was at index <code>prev</code> (-1 = nothing taken yet).",
    "At each index, either skip it, or take it if it fits after <code>prev</code>.",
]

EXPLAIN = {
    # ------------------------------------------------------------------ LIS
    "longest-increasing-subsequence": {
        "example": {"call": "length_of_lis([10, 9, 2, 5, 3, 7, 101, 18])", "expect": "4"},
        "approaches": {
            "Plain recursion": {
                "idea": _TAKE_SKIP_RECURSION + [
                    "Here, \"fits\" means strictly greater than <code>nums[prev]</code>.",
                ],
                "steps": [
                    "<code>f(n, ·) = 0</code>; call <code>f(0, -1)</code>.",
                ],
                "why": [
                    "It tries up to every subsequence: O(2<sup>n</sup>).",
                ],
                "dry": [
                    "One best choice: take 2, then 3 (skipping 5), then 7, then 101.",
                    "The length is <strong>4</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Only the last taken index matters for the future, not how we got there; cache <code>(i, prev)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "There are about n²/2 states, each O(1).",
                ],
                "dry": [
                    "[2, 5] and [2, 3] both reach index 5 wanting something above 5 or 3; each state is solved once.",
                    "f(0, -1) = <strong>4</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>dp[i][prev+1]</code> mirrors f, shifted by 1 so prev = -1 fits at column 0.",
                    "Row i reads only row i+1, so fill from i = n-1 down to 0.",
                ],
                "steps": [
                    "Row n is all zeros, the base case.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "Column 0 (prev = -1) from the bottom up gives the suffix answers: i = 7: 1, 6: 1, 5: 2, 4: 3, 3: 3, 2: 4, 1: 4, 0: 4.",
                    "dp[0][0] = <strong>4</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only the row for i+1.",
                ],
                "steps": [
                    "Build <code>cur</code> from <code>nxt</code>; swap.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "Same values, two rows at a time.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "Pass i writes only cells 0..i (since prev &lt; i), and the cell it needs, <code>i+1</code>, is never written in that pass.",
                    "So read <code>take = 1 + row[i+1]</code> first, then improve cells in place.",
                ],
                "steps": [
                    "For each valid prev: <code>row[prev+1] = max(row[prev+1], take)</code>.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "row[0] grows with each pass, from the last index upwards: 1, 1, 2, 3, 3, 4, 4, 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "dp[i] = longest ending at i": {
                "idea": [
                    "Use a different state: <code>dp[i]</code> = the longest increasing subsequence that <em>ends</em> at nums[i].",
                    "It extends the best earlier dp[j] whose value is smaller: dp[i] = 1 + max(dp[j]).",
                    "The answer is max(dp), not dp[-1], since the best need not end at the last element.",
                ],
                "steps": [
                    "Double loop over j &lt; i.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space, and the form most people write.",
                ],
                "dry": [
                    "dp = [1, 1, 1, 2, 2, 3, 4, 4].",
                    "7 extends 5 or 3 (each 2), giving 3; 101 and 18 extend 7, giving 4.",
                    "max = <strong>4</strong>.",
                ],
            },
            "Patience sorting with bisect": {
                "idea": [
                    "<code>tails[k]</code> = the smallest possible last element of an increasing subsequence of length k+1.",
                    "tails is always sorted, so binary-search each number into it: past the end extends the longest; otherwise it replaces a tail with a smaller, better one.",
                    "Use <code>bisect_left</code> so an equal value replaces rather than extends, since the subsequence must be strictly increasing.",
                ],
                "steps": [
                    "Append or overwrite; return <code>len(tails)</code>.",
                ],
                "why": [
                    "A smaller tail is always at least as easy to extend, so keeping the minimum loses nothing.",
                    "It is O(n log n). tails itself is not a valid subsequence; only its length means something.",
                ],
                "dry": [
                    "10 → [10]; 9 → [9]; 2 → [2]; 5 → [2, 5]; 3 → [2, 3].",
                    "7 → [2, 3, 7]; 101 → [2, 3, 7, 101]; 18 → [2, 3, 7, 18].",
                    "The length is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ russian doll envelopes
    "russian-doll-envelopes": {
        "example": {"call": "max_envelopes([[5, 4], [6, 4], [6, 7], [2, 3]])", "expect": "3"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Sort by width ascending, and by height <em>descending</em> for equal widths.",
                    "Then a nesting chain is exactly a strictly increasing subsequence of heights: LIS.",
                    "The descending tie-break stops two envelopes of the same width from being chained, because their heights then appear in decreasing order.",
                ] + _TAKE_SKIP_RECURSION,
                "steps": [
                    "Sort; take the heights; run the LIS recursion.",
                ],
                "why": [
                    "It is O(2<sup>n</sup>) after the sort.",
                ],
                "dry": [
                    "Sorted: [2, 3], [5, 4], [6, 7], [6, 4], so the heights are [3, 4, 7, 4].",
                    "The longest strictly increasing run is 3 → 4 → 7.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, prev)</code> on the height list.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n²).",
                ],
                "dry": [
                    "f(0, -1) on [3, 4, 7, 4] = <strong>3</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "The same <code>dp[i][prev+1]</code> table as LIS, on the heights.",
                ],
                "steps": [
                    "Fill i from n-1 down to 0.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "Suffix answers on [3, 4, 7, 4]: i = 3: 1, 2: 1, 1: 2, 0: 3.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only row i+1.",
                ],
                "steps": [
                    "Same as LIS.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "The final row starts with <strong>3</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "This is LIS's single-row trick: cell i+1 is not written during pass i.",
                    "It is correct but O(n²); with n up to 10<sup>5</sup> it times out, which motivates the next approach.",
                ],
                "steps": [
                    "<code>take = 1 + row[i+1]</code>; improve cells for valid prev.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "row[0] after each pass: 1, 1, 2, 3.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Patience sorting on heights": {
                "idea": [
                    "After the sort, this is LIS on heights, so use the O(n log n) tails method.",
                    "Equal widths arrive tallest first, so a shorter one can only <em>replace</em> a tail, never extend past its same-width sibling.",
                    "With an ascending tie-break, [[1, 1], [2, 2], [2, 3]] would wrongly give 3.",
                ],
                "steps": [
                    "<code>bisect_left</code> each height into tails; append or overwrite.",
                ],
                "why": [
                    "It is O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "Heights [3, 4, 7, 4].",
                    "tails: [3] → [3, 4] → [3, 4, 7] → 4 replaces 4 (still [3, 4, 7]).",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pair chain
    "maximum-length-of-pair-chain": {
        "example": {"call": "find_longest_chain([[-10, -8], [8, 9], [-5, 0], [6, 10], [-6, -4], [1, 7], [9, 10], [-4, 7]])",
                    "expect": "4"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Pairs can be used in any order, so sort them by start first; then a chain is a subsequence.",
                ] + _TAKE_SKIP_RECURSION + [
                    "Here, \"fits\" means the previous pair's end is strictly less than this pair's start.",
                ],
                "steps": [
                    "Sort; recurse from <code>f(0, -1)</code>.",
                ],
                "why": [
                    "It is O(2<sup>n</sup>).",
                ],
                "dry": [
                    "Sorted: [-10, -8], [-6, -4], [-5, 0], [-4, 7], [1, 7], [6, 10], [8, 9], [9, 10].",
                    "One best chain: [-10, -8] → [-6, -4] → [1, 7] → [8, 9].",
                    "The result is <strong>4</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, prev)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n²).",
                ],
                "dry": [
                    "f(0, -1) = <strong>4</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "This is the LIS table, with \"end &lt; start\" as the fit test.",
                ],
                "steps": [
                    "Fill i from n-1 down to 0.",
                ],
                "why": [
                    "It is O(n²) time and space.",
                ],
                "dry": [
                    "dp[0][0] = <strong>4</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only row i+1.",
                ],
                "steps": [
                    "Same as LIS.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "The result is <strong>4</strong>.",
                ],
            },
            "One row": {
                "idea": [
                    "Pass i writes only cells 0..i, and reads cell i+1 first.",
                ],
                "steps": [
                    "<code>take = 1 + row[i+1]</code>; improve cells for valid prev.",
                ],
                "why": [
                    "It is O(n²) time and O(n) space.",
                ],
                "dry": [
                    "The result is <strong>4</strong>.",
                ],
            },
            "Greedy by earliest end": {
                "idea": [
                    "Sort by <em>end</em>, and take every pair whose start is past the last end taken. This is activity selection.",
                    "Finishing as early as possible leaves the most room for later pairs.",
                    "Any optimal chain can swap its first pair for the earliest-ending one without getting shorter, so the greedy choice is safe.",
                ],
                "steps": [
                    "<code>end = -inf</code>; for each pair by end: if <code>a &gt; end</code>, count it and set <code>end = b</code>.",
                ],
                "why": [
                    "It is O(n log n) time and O(1) extra space.",
                ],
                "dry": [
                    "By end: [-10, -8] ✓ (end -8), [-6, -4] ✓ (end -4), [-5, 0] ✗, [1, 7] ✓ (end 7).",
                    "Then [-4, 7] ✗, [8, 9] ✓ (end 9), [6, 10] ✗, [9, 10] ✗ (9 is not &gt; 9).",
                    "The count is <strong>4</strong>.",
                ],
            },
        },
    },
}
