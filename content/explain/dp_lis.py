"""Write-ups for Dynamic Programming, part 4: longest increasing subsequence family."""

EXPLAIN = {
    # ------------------------------------------------------------------ LIS
    "longest-increasing-subsequence": {
        "examples": [
            {"call": "length_of_lis([2, 5, 3, 7])", "expect": "3"},
            {"call": "length_of_lis([7, 7, 7])", "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Walk the array left to right and, at each element, make the subsequence choice directly: <strong>skip</strong> it, or <strong>take</strong> it if it is bigger than the last element taken.",
                    "The future only depends on two things: where you are (<code>i</code>) and what was taken last (<code>prev</code>, an index, or −1 for nothing yet). So the state is <code>f(i, prev)</code>.",
                    "Trying both choices everywhere explores every increasing subsequence.",
                ],
                "steps": [
                    "Define <code>f(i, prev)</code> = the longest increasing subsequence you can still build from <code>nums[i:]</code>, given the last taken index <code>prev</code>.",
                    "If <code>i == n</code>, nothing is left: return 0.",
                    "Skip: <code>best = f(i + 1, prev)</code>.",
                    "Take, allowed only if <code>prev == -1 or nums[prev] &lt; nums[i]</code>: <code>best = max(best, 1 + f(i + 1, i))</code>.",
                    "Return <code>best</code>; the answer is <code>f(0, -1)</code>.",
                ],
                "why": [
                    "Any increasing subsequence is one sequence of take/skip decisions where every take passes the check, so the maximum over both branches is the true LIS length.",
                    "The strict <code>&lt;</code> enforces strictly increasing: equal values cannot both be taken.",
                    "Each level can branch in two, so up to <strong>O(2<sup>n</sup>)</strong> calls; the recursion is n deep, so <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(0, −1): skip the 2 → f(1, −1), or take it → 1 + f(1, 0).",
                        "f(1, 0) (last = 2): take 5 → 1 + f(2, 1); then 3 &lt; 5 cannot be taken, 7 can: f(2, 1) = 1. Or skip 5 → f(2, 0) = 2 (take 3, then 7).",
                        "So f(1, 0) = 2 and taking the 2 gives 1 + 2 = 3. The skip branch f(1, −1) only reaches 2.",
                        "Both [2, 5, 7] and [2, 3, 7] have length 3. 25 calls in all; the result is <strong>3</strong>.",
                    ],
                    [
                        "f(0, −1): take the first 7 → 1 + f(1, 0).",
                        "In f(1, 0) and below, <code>nums[0] &lt; nums[i]</code> is 7 &lt; 7, False, so only skips happen and they return 0.",
                        "Skipping first and taking a later 7 also gives 1.",
                        "10 calls; the result is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store <code>prev</code> as an index and not a value?",
                     "Either works for this recursion, but an index has only n + 1 possibilities (including −1), which is what makes the memo and table versions small and easy to index."],
                    ["Why <code>&lt;</code> and not <code>&lt;=</code>?",
                     "The problem asks for strictly increasing. With <code>&lt;=</code>, [7, 7, 7] would give 3 instead of 1."],
                    ["Why <code>prev == -1</code>?",
                     "At the start nothing has been taken, so any first element is allowed. −1 is a sentinel for \"no previous element\"."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f</code>.",
                    "Different histories reach the same state. [5] alone and [2, 5] both arrive at index 2 with the 5 as the last taken element; what can follow is the same, so the answer is computed once.",
                    "There are only about n²/2 valid <code>(i, prev)</code> pairs (prev &lt; i), so the exponential tree collapses to a quadratic number of states.",
                ],
                "steps": [
                    "Decorate <code>f(i, prev)</code> with <code>@cache</code>; the body is unchanged.",
                    "Base case <code>i == n</code> returns 0.",
                    "Skip: <code>f(i + 1, prev)</code>.",
                    "Take if it fits: <code>1 + f(i + 1, i)</code>.",
                    "Return <code>f(0, -1)</code>.",
                ],
                "why": [
                    "A state's answer depends only on <code>i</code> and <code>prev</code>, never on how it was reached, so caching is safe.",
                    "O(n²) states, each doing O(1) work besides two lookups: <strong>O(n²)</strong> time.",
                    "The cache holds <strong>O(n²)</strong> entries and the recursion is n deep.",
                ],
                "dry": [
                    [
                        "f(1, −1) takes the 5 and computes f(2, 1) = 1 (only the 7 can follow).",
                        "Later f(1, 0) also takes the 5 and asks for f(2, 1) again: a cache hit.",
                        "15 distinct states are computed instead of 25 calls.",
                        "f(0, −1) = <strong>3</strong>.",
                    ],
                    [
                        "No take after the first one ever passes, so each state is reached by a single path.",
                        "10 distinct states, 10 calls: the cache never hits on such a short input.",
                        "f(0, −1) = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>prev</code> part of the key and not just <code>i</code>?",
                     "What may come next depends on the last value taken. f(2, 1) (last was 5) gives 1, f(2, 0) (last was 2) gives 2."],
                    ["Will this hit Python's recursion limit?",
                     "Yes for n above roughly 1000, because every call goes one index deeper. The bottom-up versions have no such limit."],
                    ["Is O(n²) memory a problem?",
                     "For n = 2500 that is over six million cache entries, which is heavy in Python. The one-row and dp-ending-at-i versions use O(n)."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "What changed from the memo: the same states are stored in a table <code>dp[i][prev + 1]</code> and filled by loops. The column is shifted by 1 so <code>prev = -1</code> lands in column 0.",
                    "Row i reads only row i + 1, so filling <code>i</code> from n − 1 down to 0 always has the needed row ready. Row n is all zeros, the base case.",
                ],
                "steps": [
                    "Create <code>dp</code> of size (n + 1) × (n + 1), all 0.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0 and <code>prev</code> from <code>i - 1</code> down to −1.",
                    "Skip: <code>best = dp[i + 1][prev + 1]</code>.",
                    "Take if <code>prev == -1 or nums[prev] &lt; nums[i]</code>: <code>best = max(best, 1 + dp[i + 1][i + 1])</code>.",
                    "Store <code>dp[i][prev + 1] = best</code>; return <code>dp[0][0]</code>.",
                ],
                "why": [
                    "Each cell is the recursion's rule applied to finished cells, so <code>dp[i][prev + 1] = f(i, prev)</code> for every valid pair.",
                    "Only prev &lt; i is filled, about n²/2 cells in O(1) each: <strong>O(n²)</strong> time, no recursion.",
                    "The table is <strong>O(n²)</strong> space, even though each row only reads the next one.",
                ],
                "dry": [
                    [
                        "Row 3 (the 7): every prev allows taking it, so dp[3] = [1, 1, 1, 1, ·].",
                        "Row 2 (the 3): prev −1 or 0 (the 2) may take it → 1 + dp[3][3] = 2; prev 1 (the 5) cannot → dp[3][2] = 1. dp[2] = [2, 2, 1, ·].",
                        "Row 1 (the 5): prev −1 or 0 → max(skip 2, take 1 + dp[2][2] = 2) = 2. dp[1] = [2, 2, ·].",
                        "Row 0 (the 2): max(skip dp[1][0] = 2, take 1 + dp[1][1] = 3) = 3.",
                        "dp[0][0] = <strong>3</strong>.",
                    ],
                    [
                        "Row 2: prev −1 takes the 7 → 1; prev 0 and 1 cannot (7 &lt; 7 is false) → 0.",
                        "Row 1: column 0 = max(skip 1, take 1 + dp[2][2] = 1) = 1; column 1 = 0.",
                        "Row 0: column 0 = max(skip 1, take 1 + dp[1][1] = 1) = 1.",
                        "dp[0][0] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>prev + 1</code> shift?",
                     "Python would read index −1 as the last column. Shifting every prev by one puts \"nothing taken\" in column 0 and keeps indices non-negative."],
                    ["What about cells with <code>prev &gt;= i</code>?",
                     "They are impossible states (the last taken index must be before i), so they are never filled and never read."],
                    ["Does the order of the <code>prev</code> loop matter?",
                     "No. Cells in row i only read row i + 1, so prev can go either way."],
                ],
            },
            "Two rows": {
                "idea": [
                    "What changed from the 2-D table: row i reads only row i + 1, so keep just that row, <code>nxt</code>, and build row i in a fresh <code>cur</code>.",
                    "After each pass, <code>nxt = cur</code>. At the end, <code>nxt</code> holds row 0.",
                ],
                "steps": [
                    "Start with <code>nxt = [0] * (n + 1)</code>, which is row n.",
                    "For <code>i</code> from <code>n - 1</code> down to 0, make <code>cur = [0] * (n + 1)</code>.",
                    "For each <code>prev</code> from <code>i - 1</code> down to −1: <code>best = nxt[prev + 1]</code>; if the take is allowed, <code>best = max(best, 1 + nxt[i + 1])</code>.",
                    "Store <code>cur[prev + 1] = best</code>.",
                    "Set <code>nxt = cur</code>; return <code>nxt[0]</code>.",
                ],
                "why": [
                    "<code>nxt</code> is exactly row i + 1 of the full table, so every cell gets the same value.",
                    "Same work as the table: <strong>O(n²)</strong> time.",
                    "Two rows of n + 1 cells: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "After i = 3: nxt = [1, 1, 1, 1, 0].",
                        "After i = 2: nxt = [2, 2, 1, 0, 0]. After i = 1: nxt = [2, 2, 0, 0, 0].",
                        "i = 0: cur[0] = max(nxt[0] = 2, 1 + nxt[1] = 3) = 3.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "After i = 2: nxt = [1, 0, 0, 0].",
                        "After i = 1: nxt = [1, 0, 0, 0]. Taking a 7 after a 7 is never allowed, so only column 0 is 1.",
                        "i = 0: cur[0] = max(1, 1 + nxt[1] = 1) = 1.",
                        "The result is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return <code>nxt[0]</code> and not <code>cur[0]</code>?",
                     "After the last pass, <code>nxt = cur</code> has already happened, so both name row 0. <code>nxt</code> also works when n = 0 and the loop never runs."],
                    ["Why a new <code>cur</code> each pass?",
                     "Writing into <code>nxt</code> directly could overwrite values row i still needs. The one-row version shows when that is actually safe."],
                    ["Can I rebuild the subsequence?",
                     "Not from two rows; earlier rows are gone. Use the dp-ending-at-i version with parent pointers for that."],
                ],
            },
            "One row": {
                "idea": [
                    "What changed from two rows: a single list <code>row</code>, updated in place. Pass i writes only cells 0..i (prev &lt; i), and the one cell it reads, <code>row[i + 1]</code>, is outside that range.",
                    "So read <code>take = 1 + row[i + 1]</code> once at the start of the pass, then improve cells in place. A skipped cell already holds the right value, since skip copies the row below unchanged.",
                ],
                "steps": [
                    "Start with <code>row = [0] * (n + 1)</code>; <code>row[prev + 1]</code> means f(i + 1, prev).",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0.",
                    "Compute <code>take = 1 + row[i + 1]</code> = 1 + f(i + 1, i) before any writes.",
                    "For each <code>prev</code> from <code>i - 1</code> down to −1 that allows taking <code>nums[i]</code>: <code>row[prev + 1] = max(row[prev + 1], take)</code>.",
                    "Return <code>row[0]</code>.",
                ],
                "why": [
                    "Before pass i, <code>row[prev + 1]</code> is f(i + 1, prev), which is the skip value; the update adds the take option, giving f(i, prev). Cells that cannot take keep their skip value, which is correct.",
                    "<code>take</code> is the same for every prev, so it is computed once per pass.",
                    "<strong>O(n²)</strong> time and <strong>O(n)</strong> space with one list.",
                ],
                "dry": [
                    [
                        "i = 3 (7): take = 1 + row[4] = 1; every prev allows it → row = [1, 1, 1, 1, 0].",
                        "i = 2 (3): take = 1 + row[3] = 2; prev 1 (5) cannot; prev 0 and −1 can → row = [2, 2, 1, 1, 0].",
                        "i = 1 (5): take = 1 + row[2] = 2; row[1] and row[0] are already 2.",
                        "i = 0 (2): take = 1 + row[1] = 3 → row[0] = 3.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "i = 2: take = 1 + row[3] = 1; only prev −1 passes → row = [1, 0, 0, 0].",
                        "i = 1: take = 1 + row[2] = 1; only prev −1 passes, row[0] stays 1.",
                        "i = 0: take = 1 + row[1] = 1; row[0] stays 1.",
                        "The result is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>take</code> be read before the loop?",
                     "It reads <code>row[i + 1]</code>. The loop never writes that cell, so reading it inside would also work, but reading once makes it obvious that it is the row-below value and saves repeated work."],
                    ["Does the <code>prev</code> direction matter here?",
                     "No. Each cell is updated from its own old value and <code>take</code>, never from a neighbour, so ascending prev gives the same answers (checked on random inputs)."],
                    ["Why is there no <code>else</code> branch?",
                     "When the take is not allowed, f(i, prev) = f(i + 1, prev), and the cell already holds exactly that."],
                ],
            },
            "dp[i] = longest ending at i": {
                "idea": [
                    "A different state: instead of \"best from here on\", use <code>dp[i]</code> = the length of the longest increasing subsequence that <em>ends</em> at <code>nums[i]</code>.",
                    "Such a subsequence is either <code>nums[i]</code> alone, or some earlier one ending at <code>nums[j] &lt; nums[i]</code> with <code>nums[i]</code> appended. So <code>dp[i] = 1 + max(dp[j])</code> over those j.",
                    "The answer is <code>max(dp)</code>, because the best subsequence can end anywhere.",
                ],
                "steps": [
                    "Start with <code>dp = [1] * len(nums)</code>: every element alone is length 1.",
                    "Loop <code>i</code> over every index, and <code>j</code> over every index before it.",
                    "If <code>nums[j] &lt; nums[i]</code> and <code>dp[j] + 1 &gt; dp[i]</code>, set <code>dp[i] = dp[j] + 1</code>.",
                    "All <code>dp[j]</code> with j &lt; i are final when row i is computed.",
                    "Return <code>max(dp)</code>.",
                ],
                "why": [
                    "The last two elements of any LIS ending at i are some j and i with <code>nums[j] &lt; nums[i]</code>, and the part ending at j is best possible by induction, so the max over j is correct.",
                    "Two nested loops: <strong>O(n²)</strong> time. One list: <strong>O(n)</strong> space.",
                    "This one-dimensional state is simpler than <code>(i, prev)</code> and easy to extend with parent pointers to rebuild the subsequence.",
                ],
                "dry": [
                    [
                        "dp starts [1, 1, 1, 1].",
                        "i = 1 (5): j = 0 (2 &lt; 5) → dp[1] = 2.",
                        "i = 2 (3): j = 0 (2 &lt; 3) → dp[2] = 2; j = 1 (5) is not smaller.",
                        "i = 3 (7): j = 0 → 2, j = 1 → 3, j = 2 gives 3, not larger. dp = [1, 2, 2, 3].",
                        "max(dp) = <strong>3</strong>.",
                    ],
                    [
                        "dp starts [1, 1, 1].",
                        "Every comparison is 7 &lt; 7, which is false, so nothing is extended.",
                        "dp = [1, 1, 1].",
                        "max(dp) = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>max(dp)</code> and not <code>dp[-1]</code>?",
                     "The LIS need not end at the last element. On [3, 4, 1], dp[-1] is 1 but the answer is 2."],
                    ["How is this related to the <code>(i, prev)</code> ladder?",
                     "It is a different, smaller state that answers the same question. The ladder shows how a general take/skip recursion is mechanically turned into an O(n)-space DP; this is the form most people write directly."],
                    ["How do I get the actual subsequence?",
                     "Record <code>parent[i] = j</code> whenever dp[i] improves, then walk back from the index of the maximum."],
                ],
            },
            "Patience sorting with bisect": {
                "idea": [
                    "Keep <code>tails[k]</code> = the <em>smallest</em> possible last element of any increasing subsequence of length k + 1 seen so far.",
                    "A smaller tail is never worse: anything that extends a bigger tail also extends it. So when a new number can end a length-(k+1) subsequence more cheaply, overwrite <code>tails[k]</code>.",
                    "<code>tails</code> stays sorted, so the right slot for each number is found by binary search.",
                ],
                "steps": [
                    "Start with <code>tails = []</code>.",
                    "For each <code>x</code>, find <code>k = bisect_left(tails, x)</code>, the first tail that is ≥ x.",
                    "If <code>k == len(tails)</code>, x is bigger than every tail: append it, extending the longest subsequence by one.",
                    "Otherwise set <code>tails[k] = x</code>: a subsequence of length k + 1 can now end lower.",
                    "Return <code>len(tails)</code>.",
                ],
                "why": [
                    "Invariant: for every length L ≤ len(tails), <code>tails[L-1]</code> is the minimum ending value over all increasing subsequences of length L so far. Appending or replacing at <code>bisect_left</code> keeps it true, so the length of <code>tails</code> is the LIS length.",
                    "<code>bisect_left</code> (not right) means an equal value replaces instead of extending, which enforces strict increase.",
                    "n binary searches: <strong>O(n log n)</strong> time; <code>tails</code> holds at most n values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "2: tails empty → append. tails = [2].",
                        "5: k = 1 = len → append. tails = [2, 5].",
                        "3: k = 1 (5 is the first tail ≥ 3) → replace. tails = [2, 3]: length 2 can now end at 3.",
                        "7: k = 2 = len → append. tails = [2, 3, 7].",
                        "The length is <strong>3</strong>.",
                    ],
                    [
                        "7: append. tails = [7].",
                        "7: bisect_left finds k = 0 (the equal 7), so it replaces, not appends. tails = [7].",
                        "7: the same again.",
                        "The length is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>tails</code> itself an increasing subsequence?",
                     "Not necessarily. Its entries can come from different subsequences; only its length is meaningful. Rebuilding the actual LIS needs extra parent bookkeeping."],
                    ["What changes with <code>bisect_right</code>?",
                     "An equal value would be appended after itself, counting non-decreasing runs. On [7, 7, 7] it returns 3 instead of 1."],
                    ["Why is it called patience sorting?",
                     "It mirrors the card game: each tail is the top card of a pile, and a card goes on the leftmost pile whose top is not smaller. The number of piles is the LIS length."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ russian doll envelopes
    "russian-doll-envelopes": {
        "examples": [
            {"call": "max_envelopes([[5, 4], [6, 4], [6, 7], [2, 3]])", "expect": "3"},
            {"call": "max_envelopes([[1, 1], [2, 2], [2, 3]])", "expect": "2"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Sort by width ascending, and by height <em>descending</em> when widths tie. Then any nesting chain appears left to right, and only heights still need checking.",
                    "With the descending tie-break, two envelopes of equal width have their heights in decreasing order, so a strictly increasing height sequence can never pick both. A chain becomes exactly a strictly increasing subsequence of <code>h</code>.",
                    "Run the take/skip LIS recursion <code>f(i, prev)</code> on the height list.",
                ],
                "steps": [
                    "Sort with key <code>(e[0], -e[1])</code> and keep the heights in <code>h</code>.",
                    "Define <code>f(i, prev)</code>: if <code>i == n</code> return 0.",
                    "Skip: <code>best = f(i + 1, prev)</code>.",
                    "Take if <code>prev == -1 or h[prev] &lt; h[i]</code>: <code>best = max(best, 1 + f(i + 1, i))</code>.",
                    "Return <code>f(0, -1)</code>.",
                ],
                "why": [
                    "After the sort, a valid chain needs strictly increasing widths and heights. Widths never decrease left to right, and equal widths cannot both appear in an increasing height run, so increasing heights imply strictly increasing widths too.",
                    "The recursion is the LIS one, so it finds the longest such run.",
                    "<strong>O(n log n + 2<sup>n</sup>)</strong> time: the sort plus the exponential search. <strong>O(n)</strong> space for the stack and <code>h</code>.",
                ],
                "dry": [
                    [
                        "Sorted: [2, 3], [5, 4], [6, 7], [6, 4], so h = [3, 4, 7, 4]. The two width-6 envelopes come tallest first.",
                        "Take 3, take 4, take 7: each is bigger than the last. The final 4 is not bigger than 7.",
                        "Branches that take the final 4 after the first 4 fail (4 &lt; 4 is false).",
                        "25 calls; the best is 3 → 4 → 7. The result is <strong>3</strong>.",
                    ],
                    [
                        "Sorted: [1, 1], [2, 3], [2, 2], so h = [1, 3, 2].",
                        "Take 1, then 3 or 2, but not both: 3 then 2 is decreasing.",
                        "So [2, 2] and [2, 3] are never chained, as they should not be.",
                        "13 calls. The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort heights descending for equal widths?",
                     "Equal widths cannot nest. Descending heights make them unable to form an increasing pair. With an ascending tie-break, example 2's heights become [1, 2, 3] and the answer wrongly becomes 3."],
                    ["Why not sort by area?",
                     "Nesting needs both dimensions strictly smaller. A smaller area says nothing about each side, e.g. [1, 10] and [2, 3]."],
                    ["Can two identical envelopes nest?",
                     "No. Equal widths are blocked by the tie-break and equal heights by the strict <code>&lt;</code>."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f</code>, exactly as in LIS.",
                    "The state <code>(i, prev)</code> on the sorted height list fully decides the future, so it can be stored and reused.",
                ],
                "steps": [
                    "Sort and extract <code>h</code> as before.",
                    "Decorate <code>f(i, prev)</code> with <code>@cache</code>.",
                    "Base case <code>i == n</code> returns 0.",
                    "Skip, or take when <code>prev == -1 or h[prev] &lt; h[i]</code>.",
                    "Return <code>f(0, -1)</code>.",
                ],
                "why": [
                    "The cached values are the same LIS answers, so the result is unchanged.",
                    "About n²/2 states in O(1) each, plus the sort: <strong>O(n²)</strong> time.",
                    "<strong>O(n²)</strong> space for the cache.",
                ],
                "dry": [
                    [
                        "h = [3, 4, 7, 4].",
                        "f(2, 1) (next is the 7, last taken was the first 4) is reached both after taking 3 and 4, and after taking only 4: the second time is a cache hit.",
                        "15 distinct states instead of 25 calls.",
                        "f(0, −1) = <strong>3</strong>.",
                    ],
                    [
                        "h = [1, 3, 2].",
                        "10 distinct states instead of 13 calls.",
                        "f(0, −1) = 1 + f(1, 0) = 1 + 1 = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Is O(n²) good enough here?",
                     "Not for the LeetCode limits (n up to 10<sup>5</sup>). It is a stepping stone; patience sorting is the accepted solution."],
                    ["Should the cache key include the envelopes?",
                     "No. <code>h</code> is fixed for the whole call and read from the enclosing scope; only <code>(i, prev)</code> varies."],
                    ["Does the memo change the tie-break logic?",
                     "No. The sort happens once before any call, so every version sees the same <code>h</code>."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "What changed from the memo: the same states in a table <code>dp[i][prev + 1]</code>, filled from <code>i = n - 1</code> down to 0 because row i reads only row i + 1.",
                    "It is the LIS table run on <code>h</code>; the column shift puts prev = −1 in column 0.",
                ],
                "steps": [
                    "Sort, extract <code>h</code>, and create an (n + 1) × (n + 1) table of zeros.",
                    "Loop <code>i</code> downwards and <code>prev</code> from <code>i - 1</code> down to −1.",
                    "Skip value: <code>dp[i + 1][prev + 1]</code>.",
                    "Take value, if <code>h[prev] &lt; h[i]</code> or prev is −1: <code>1 + dp[i + 1][i + 1]</code>.",
                    "Store the larger in <code>dp[i][prev + 1]</code>; return <code>dp[0][0]</code>.",
                ],
                "why": [
                    "Each cell is the recursion's rule on finished cells, so it equals f(i, prev).",
                    "About n²/2 cells: <strong>O(n²)</strong> time with no recursion.",
                    "The full table is <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "h = [3, 4, 7, 4]. Row 3 (the last 4): prev −1 and 0 (3) can take it → 1; prev 1 (4) and 2 (7) cannot → 0. Row 3 = [1, 1, 0, 0].",
                        "Row 2 (the 7): every prev can take it, 1 + dp[3][3] = 1. Row 2 = [1, 1, 1].",
                        "Row 1 (the 4): prev −1 or 0 → max(1, 1 + dp[2][2] = 2) = 2. Row 1 = [2, 2].",
                        "Row 0 (the 3): max(dp[1][0] = 2, 1 + dp[1][1] = 3) = 3.",
                        "dp[0][0] = <strong>3</strong>.",
                    ],
                    [
                        "h = [1, 3, 2]. Row 2 (the 2): prev −1 and 0 → 1; prev 1 (3) → 0. Row 2 = [1, 1, 0].",
                        "Row 1 (the 3): column 0 = max(1, 1 + dp[2][2] = 1) = 1; column 1 = 1.",
                        "Row 0 (the 1): max(dp[1][0] = 1, 1 + dp[1][1] = 2) = 2.",
                        "dp[0][0] = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the take value in example 2's row 1 only 1?",
                     "It is 1 + dp[2][2], and dp[2][2] = f(2, 1) = 0: after taking the 3, the remaining 2 is too short to follow it."],
                    ["Is anything envelope-specific in the table?",
                     "No. All envelope logic is in the sort; after that it is plain LIS on <code>h</code>."],
                    ["Which cells are unused?",
                     "Those with prev ≥ i. They stay 0 and are never read."],
                ],
            },
            "Two rows": {
                "idea": [
                    "What changed from the 2-D table: keep only row i + 1 as <code>nxt</code> and build row i in <code>cur</code>.",
                    "Same values as the table, but only two rows exist at any time.",
                ],
                "steps": [
                    "Start with <code>nxt = [0] * (n + 1)</code>.",
                    "For <code>i</code> from <code>n - 1</code> down to 0, make <code>cur = [0] * (n + 1)</code>.",
                    "For each <code>prev</code>: <code>best = nxt[prev + 1]</code>; if <code>h[prev] &lt; h[i]</code> or prev is −1, compare with <code>1 + nxt[i + 1]</code>.",
                    "Store <code>cur[prev + 1] = best</code>, then <code>nxt = cur</code>.",
                    "Return <code>nxt[0]</code>.",
                ],
                "why": [
                    "<code>nxt</code> equals row i + 1 of the full table, so every value matches.",
                    "<strong>O(n²)</strong> time, unchanged.",
                    "<strong>O(n)</strong> space for the two rows (plus the sorted heights).",
                ],
                "dry": [
                    [
                        "After i = 3: nxt = [1, 1, 0, 0, 0]. After i = 2: [1, 1, 1, 0, 0].",
                        "After i = 1: [2, 2, 0, 0, 0].",
                        "i = 0: cur[0] = max(2, 1 + nxt[1] = 3) = 3.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "After i = 2: nxt = [1, 1, 0, 0].",
                        "After i = 1: nxt = [1, 1, 0, 0].",
                        "i = 0: cur[0] = max(1, 1 + nxt[1] = 2) = 2.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Does saving memory make it faster?",
                     "Not asymptotically; it is still O(n²). It just avoids an (n + 1)² table."],
                    ["What does <code>nxt</code> start as?",
                     "Row n, the base case where nothing is left, which is all zeros."],
                    ["Why rebuild <code>cur</code> from zeros?",
                     "Every needed cell is assigned in the pass, so the zeros only matter for unused cells; a fresh list keeps the old row safe while reading it."],
                ],
            },
            "One row": {
                "idea": [
                    "What changed from two rows: one list <code>row</code> updated in place. Pass i writes only cells 0..i and reads only <code>row[i + 1]</code>, so reading <code>take</code> first is safe.",
                    "Correct but still O(n²): with n up to 10<sup>5</sup> it is too slow, which is why the last step switches to binary search.",
                ],
                "steps": [
                    "Start with <code>row = [0] * (n + 1)</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0.",
                    "Compute <code>take = 1 + row[i + 1]</code>.",
                    "For each prev that can take <code>h[i]</code>: <code>row[prev + 1] = max(row[prev + 1], take)</code>.",
                    "Return <code>row[0]</code>.",
                ],
                "why": [
                    "Before pass i, <code>row[prev + 1]</code> is the skip value f(i + 1, prev); adding the take option turns it into f(i, prev).",
                    "<strong>O(n²)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i = 3 (4): take = 1; prev −1 and 0 pass → row = [1, 1, 0, 0, 0].",
                        "i = 2 (7): take = 1 + row[3] = 1; all prev pass → row = [1, 1, 1, 0, 0].",
                        "i = 1 (4): take = 1 + row[2] = 2; prev 0 and −1 pass → row = [2, 2, 1, 0, 0].",
                        "i = 0 (3): take = 1 + row[1] = 3 → row[0] = 3.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "i = 2 (2): take = 1; prev 1 (3) fails, prev 0 and −1 pass → row = [1, 1, 0, 0].",
                        "i = 1 (3): take = 1 + row[2] = 1; no change.",
                        "i = 0 (1): take = 1 + row[1] = 2 → row[0] = 2.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can <code>row[i + 1]</code> be read safely?",
                     "During pass i, prev &lt; i, so the writes go to cells 0..i. Cell i + 1 still holds f(i + 1, i) from the previous pass."],
                    ["Is this the answer to give in an interview?",
                     "No, it times out on large inputs. Use it to explain the DP, then give the sort-plus-bisect solution."],
                    ["Why is there no write when the take fails?",
                     "Then f(i, prev) equals the skip value, which the cell already holds."],
                ],
            },
            "Patience sorting on heights": {
                "idea": [
                    "After the width-ascending, height-descending sort, the problem is LIS on heights, so use the O(n log n) <code>tails</code> method.",
                    "Equal widths arrive tallest first, so a shorter envelope of the same width can only <em>replace</em> a tail, never extend past its sibling.",
                ],
                "steps": [
                    "Sort with key <code>(e[0], -e[1])</code>.",
                    "Start with <code>tails = []</code>.",
                    "For each height <code>h</code>, find <code>k = bisect_left(tails, h)</code>.",
                    "Append if <code>k == len(tails)</code>, otherwise set <code>tails[k] = h</code>.",
                    "Return <code>len(tails)</code>.",
                ],
                "why": [
                    "<code>tails</code> keeps the smallest ending height for each chain length; the sort guarantees increasing heights also mean increasing widths, so its length is the longest chain.",
                    "Sorting and n binary searches: <strong>O(n log n)</strong> time.",
                    "The sorted copy and <code>tails</code>: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Heights in sorted order: [3, 4, 7, 4].",
                        "3 → [3]; 4 → [3, 4]; 7 → [3, 4, 7].",
                        "4: bisect_left finds the equal 4 at k = 1 and replaces it. tails stays [3, 4, 7].",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "Heights in sorted order: [1, 3, 2].",
                        "1 → [1]; 3 → [1, 3].",
                        "2: k = 1, replace the 3. tails = [1, 2]. The two width-2 envelopes share one slot.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["What if I sort heights ascending for equal widths?",
                     "Then [[1, 1], [2, 2], [2, 3]] gives heights [1, 2, 3] and the answer 3, nesting two envelopes of the same width. The descending tie-break is the whole trick."],
                    ["Why <code>bisect_left</code>?",
                     "Equal heights cannot nest. bisect_left lands on the equal tail and replaces it instead of appending."],
                    ["Does this give the actual chain?",
                     "No, only its length. Rebuilding it needs parent indices stored alongside <code>tails</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pair chain
    "maximum-length-of-pair-chain": {
        "examples": [
            {"call": "find_longest_chain([[3, 4], [1, 8], [1, 2], [5, 6]])", "expect": "3"},
            {"call": "find_longest_chain([[1, 2], [2, 3], [3, 4]])", "expect": "2"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Pairs can be chained in any order, so sort them by start first; then any chain appears left to right as a subsequence.",
                    "Run the LIS take/skip recursion <code>f(i, prev)</code>, where \"fits\" now means the previous pair's end is strictly less than this pair's start: <code>pairs[prev][1] &lt; pairs[i][0]</code>.",
                ],
                "steps": [
                    "Sort: <code>pairs = sorted(pairs)</code>.",
                    "Define <code>f(i, prev)</code>: if <code>i == n</code> return 0.",
                    "Skip: <code>best = f(i + 1, prev)</code>.",
                    "Take if <code>prev == -1 or pairs[prev][1] &lt; pairs[i][0]</code>: <code>best = max(best, 1 + f(i + 1, i))</code>.",
                    "Return <code>f(0, -1)</code>.",
                ],
                "why": [
                    "In a chain each pair starts after the previous one ends, so starts are increasing; sorting by start therefore lists every chain in order, and the recursion tries every subsequence.",
                    "The strict <code>&lt;</code> matches the rule that [1, 2] cannot be followed by [2, 3].",
                    "<strong>O(n log n + 2<sup>n</sup>)</strong> time and <strong>O(n)</strong> space for the stack.",
                ],
                "dry": [
                    [
                        "Sorted: [1, 2], [1, 8], [3, 4], [5, 6].",
                        "Take [1, 2]; [1, 8] does not fit (2 &lt; 1 is false); take [3, 4] (2 &lt; 3); take [5, 6] (4 &lt; 5).",
                        "Any chain using [1, 8] has length 1, since nothing starts after 8.",
                        "20 calls. The result is <strong>3</strong>.",
                    ],
                    [
                        "Sorted order is unchanged.",
                        "[1, 2] then [2, 3] fails (2 &lt; 2 is false); [1, 2] then [3, 4] works.",
                        "[2, 3] then [3, 4] fails the same way.",
                        "11 calls. The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["What if I skip the sort?",
                     "The recursion only builds chains in input order. On example 1 unsorted it finds 2 instead of 3."],
                    ["Why strict <code>&lt;</code>?",
                     "The problem says pair (c, d) follows (a, b) only if b &lt; c, so touching ends do not chain."],
                    ["Is sorting by start the only valid order?",
                     "Sorting by end also lists every chain in order. The greedy approach relies on the end order."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f</code>.",
                    "The future depends only on the next index and the last pair taken, so each <code>(i, prev)</code> is solved once.",
                ],
                "steps": [
                    "Sort the pairs.",
                    "Decorate <code>f(i, prev)</code> with <code>@cache</code>.",
                    "Base case <code>i == n</code> returns 0.",
                    "Skip, or take when <code>pairs[prev][1] &lt; pairs[i][0]</code> (or prev is −1).",
                    "Return <code>f(0, -1)</code>.",
                ],
                "why": [
                    "Cached values equal the recursive ones, so the answer is the same.",
                    "About n²/2 states, O(1) each: <strong>O(n²)</strong> time.",
                    "<strong>O(n²)</strong> space for the cache.",
                ],
                "dry": [
                    [
                        "f(3, 2) (next [5, 6], last taken [3, 4]) is reached both after [1, 2], [3, 4] and after [3, 4] alone: the second time is a cache hit.",
                        "15 distinct states instead of 20 calls.",
                        "f(0, −1) = <strong>3</strong>.",
                    ],
                    [
                        "10 distinct states instead of 11 calls.",
                        "f(0, −1) = 1 + f(1, 0) = 1 + 1.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does sorting need to happen outside <code>f</code>?",
                     "The indices in the state refer to the sorted list. Sorting once before any call keeps them consistent."],
                    ["Is O(n²) acceptable?",
                     "For n ≤ 1000 (the LeetCode limit) yes, but the greedy is simpler and faster."],
                    ["Why is the cache key not the pair values?",
                     "Indices are enough and cheaper to hash; the values are read from the sorted list."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "What changed from the memo: the states go in <code>dp[i][prev + 1]</code>, filled from the last pair upwards because row i reads only row i + 1.",
                    "This is the LIS table with \"previous end &lt; this start\" as the fit test.",
                ],
                "steps": [
                    "Sort and create an (n + 1) × (n + 1) table of zeros.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0 and <code>prev</code> from <code>i - 1</code> down to −1.",
                    "Skip value: <code>dp[i + 1][prev + 1]</code>.",
                    "Take value, if the pair fits: <code>1 + dp[i + 1][i + 1]</code>.",
                    "Store the larger; return <code>dp[0][0]</code>.",
                ],
                "why": [
                    "Each cell is the recursion's rule on finished cells, so it equals f(i, prev).",
                    "<strong>O(n²)</strong> time, no recursion.",
                    "<strong>O(n²)</strong> space for the table.",
                ],
                "dry": [
                    [
                        "Sorted: [1, 2], [1, 8], [3, 4], [5, 6]. Row 3 ([5, 6]): fits after −1, [1, 2], [3, 4] but not [1, 8]. Row 3 = [1, 1, 0, 1].",
                        "Row 2 ([3, 4]): fits after −1 and [1, 2] → 1 + dp[3][3] = 2; after [1, 8] → skip value 0. Row 2 = [2, 2, 0].",
                        "Row 1 ([1, 8]): column 0 = max(2, 1 + dp[2][2] = 1) = 2; column 1 (after [1, 2]) cannot take → 2. Row 1 = [2, 2].",
                        "Row 0 ([1, 2]): max(dp[1][0] = 2, 1 + dp[1][1] = 3) = 3.",
                        "dp[0][0] = <strong>3</strong>.",
                    ],
                    [
                        "Row 2 ([3, 4]): fits after −1 and [1, 2], not after [2, 3]. Row 2 = [1, 1, 0].",
                        "Row 1 ([2, 3]): column 0 = max(1, 1 + 0) = 1; column 1 (after [1, 2]) cannot take → 1.",
                        "Row 0 ([1, 2]): max(1, 1 + dp[1][1] = 2) = 2.",
                        "dp[0][0] = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>dp[2][2]</code> zero in example 1?",
                     "It is f(2, 1): the last pair taken is [1, 8], and neither [3, 4] nor [5, 6] starts after 8."],
                    ["Can the table give the chain itself?",
                     "Yes, by walking from <code>dp[0][0]</code> and checking at each row whether taking or skipping produced the value."],
                    ["Why not use this over the greedy?",
                     "It is O(n²) time and space where the greedy is O(n log n). It exists to show the general DP the greedy shortcuts."],
                ],
            },
            "Two rows": {
                "idea": [
                    "What changed from the 2-D table: keep only row i + 1 (<code>nxt</code>) and build row i in <code>cur</code>.",
                    "The values are identical; memory drops from a square table to two rows.",
                ],
                "steps": [
                    "Sort; start with <code>nxt = [0] * (n + 1)</code>.",
                    "For <code>i</code> from <code>n - 1</code> down to 0, make <code>cur = [0] * (n + 1)</code>.",
                    "For each <code>prev</code>: <code>best = nxt[prev + 1]</code>, and if the pair fits, compare with <code>1 + nxt[i + 1]</code>.",
                    "Store <code>cur[prev + 1] = best</code>, then <code>nxt = cur</code>.",
                    "Return <code>nxt[0]</code>.",
                ],
                "why": [
                    "<code>nxt</code> is row i + 1 of the table, so every value matches.",
                    "<strong>O(n²)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "After i = 3: nxt = [1, 1, 0, 1, 0]. After i = 2: [2, 2, 0, 0, 0].",
                        "After i = 1: [2, 2, 0, 0, 0].",
                        "i = 0: cur[0] = max(2, 1 + nxt[1] = 3) = 3.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "After i = 2: nxt = [1, 1, 0, 0]. After i = 1: [1, 1, 0, 0].",
                        "i = 0: cur[0] = max(1, 1 + nxt[1] = 2) = 2.",
                        "Only [1, 2] → [3, 4] (or one of them with [2, 3]) is possible.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>nxt[0]</code> right if there is one pair?",
                     "Yes. One pass builds row 0 with column 0 = 1, and <code>nxt</code> then points at it."],
                    ["Why not reuse one list?",
                     "You can; the next step does exactly that once it is clear which cells are read and written."],
                    ["What does the sort cost here?",
                     "O(n log n), dominated by the O(n²) fill."],
                ],
            },
            "One row": {
                "idea": [
                    "What changed from two rows: one list, updated in place. Pass i writes cells 0..i and reads only <code>row[i + 1]</code>, which no write in the pass touches.",
                    "Read <code>take = 1 + row[i + 1]</code> first, then improve every cell whose prev allows the take.",
                ],
                "steps": [
                    "Sort; start with <code>row = [0] * (n + 1)</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0.",
                    "Compute <code>take = 1 + row[i + 1]</code>.",
                    "For each prev with <code>prev == -1 or pairs[prev][1] &lt; pairs[i][0]</code>: <code>row[prev + 1] = max(row[prev + 1], take)</code>.",
                    "Return <code>row[0]</code>.",
                ],
                "why": [
                    "Before pass i each cell holds the skip value f(i + 1, prev); adding the take option makes it f(i, prev).",
                    "<strong>O(n²)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i = 3 ([5, 6]): take = 1; prev −1, 0, 2 fit → row = [1, 1, 0, 1, 0].",
                        "i = 2 ([3, 4]): take = 1 + row[3] = 2; prev −1 and 0 fit → row = [2, 2, 0, 1, 0].",
                        "i = 1 ([1, 8]): take = 1 + row[2] = 1; only prev −1 fits, and row[0] is already 2.",
                        "i = 0 ([1, 2]): take = 1 + row[1] = 3 → row[0] = 3.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "i = 2 ([3, 4]): take = 1; prev −1 and 0 fit → row = [1, 1, 0, 0].",
                        "i = 1 ([2, 3]): take = 1 + row[2] = 1; nothing improves.",
                        "i = 0 ([1, 2]): take = 1 + row[1] = 2 → row[0] = 2.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does pass i never write <code>row[i + 1]</code>?",
                     "It writes <code>row[prev + 1]</code> with prev ≤ i − 1, so the highest cell touched is <code>row[i]</code>."],
                    ["Why is there no update when the pair does not fit?",
                     "Then the only option is to skip, and the cell already holds the skip value."],
                    ["Does the order of prev matter?",
                     "No. Each cell depends only on itself and <code>take</code>."],
                ],
            },
            "Greedy by earliest end": {
                "idea": [
                    "Sort by <em>end</em> and take every pair whose start is past the end of the last pair taken. This is activity selection.",
                    "Finishing as early as possible leaves the most room for later pairs.",
                    "Exchange argument: any optimal chain can swap its first pair for the earliest-ending pair without breaking the chain, so the greedy first choice is safe, and the same holds for each later choice.",
                ],
                "steps": [
                    "Set <code>count, end = 0, -inf</code>.",
                    "Loop over <code>sorted(pairs, key=lambda p: p[1])</code> as <code>a, b</code>.",
                    "If <code>a &gt; end</code>, the pair fits: add 1 to <code>count</code> and set <code>end = b</code>.",
                    "Otherwise skip it: it overlaps the chain, and keeping the earlier end is never worse.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "After each take, the greedy chain has the earliest possible end for its length, so no other chain of the same length can fit more pairs afterwards.",
                    "Sorting dominates: <strong>O(n log n)</strong> time.",
                    "<strong>O(1)</strong> extra variables, though <code>sorted</code> makes an O(n) copy of the list.",
                ],
                "dry": [
                    [
                        "By end: [1, 2], [3, 4], [5, 6], [1, 8].",
                        "[1, 2]: 1 &gt; −inf, take, end = 2. [3, 4]: 3 &gt; 2, take, end = 4.",
                        "[5, 6]: 5 &gt; 4, take, end = 6.",
                        "[1, 8]: 1 &gt; 6 is false, skip.",
                        "The count is <strong>3</strong>.",
                    ],
                    [
                        "By end: [1, 2], [2, 3], [3, 4].",
                        "[1, 2]: take, end = 2.",
                        "[2, 3]: 2 &gt; 2 is false, skip. [3, 4]: 3 &gt; 2, take, end = 4.",
                        "The count is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort by end and not by start?",
                     "A pair that starts early may end very late and block everything. On [[1, 10], [2, 3], [4, 5]], greedy by start takes [1, 10] and gets 1; by end it gets 2."],
                    ["Why <code>a &gt; end</code> and not <code>&gt;=</code>?",
                     "Chaining needs the previous end strictly less than the next start. With <code>&gt;=</code>, example 2 would wrongly count 3."],
                    ["Why does this work here but not for LIS?",
                     "Here only the end of the last pair matters and earlier is always better. In LIS-style problems with weights or two dimensions, there is no single \"best so far\" to keep, so DP is needed."],
                ],
            },
        },
    },
}
