"""Write-ups for Dynamic Programming, part 2: the knapsack family."""

EXPLAIN = {
    # ------------------------------------------------------------------ 0/1 knapsack
    "knapsack-01": {
        "examples": [
            {"call": "knapsack(4, [5, 3, 3], [3, 2, 2])", "expect": "6"},
            {"call": "knapsack(4, [3], [2])", "expect": "3"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Look at the items one at a time, from the last one back. Each item has exactly two futures: it is <strong>left out</strong>, or it is <strong>taken</strong> (only if it still fits).",
                    "Define <code>f(i, c)</code> = the best value you can get from the first <code>i</code> items with capacity <code>c</code> left. Then <code>f(i, c) = max(f(i-1, c), val[i-1] + f(i-1, c - wt[i-1]))</code>.",
                    "Greedy rules (most valuable first, best value per weight first) fail on inputs like example 1, so every take/leave pattern has to be considered. This is the honest starting point of the ladder.",
                ],
                "steps": [
                    "Base case: <code>f(0, c) = 0</code>, because with no items left there is nothing to gain.",
                    "Start with the \"leave it\" option: <code>best = f(i - 1, c)</code>.",
                    "If <code>wt[i - 1] &lt;= c</code>, the item fits, so also try <code>val[i - 1] + f(i - 1, c - wt[i - 1])</code> and keep the larger.",
                    "Both branches move to <code>i - 1</code>, so an item can never be taken twice.",
                    "The answer is <code>f(len(val), W)</code>: all items considered, full capacity available.",
                ],
                "why": [
                    "Every subset of items corresponds to one root-to-leaf path of take/leave choices, and subsets that do not fit are cut off by the <code>wt[i - 1] &lt;= c</code> test, so the maximum is taken over exactly the feasible subsets.",
                    "Each call makes up to two calls, n levels deep, so the time is <strong>O(2<sup>n</sup>)</strong>.",
                    "Only the current path is on the call stack, so the extra space is <strong>O(n)</strong>.",
                    "The waste is that the same <code>(i, c)</code> is solved again whenever two different choice paths leave the same capacity; the next rung fixes exactly that.",
                ],
                "dry": [
                    [
                        "Items as (weight, value): (3, 5), (2, 3), (2, 3); W = 4. Call <code>f(3, 4)</code>.",
                        "Leave item 3 → <code>f(2, 4)</code>: leaving item 2 gives <code>f(1, 4)</code> = 5 (item 1 fits); taking it gives 3 + <code>f(1, 2)</code> = 3 + 0. So <code>f(2, 4)</code> = 5.",
                        "Take item 3 → 3 + <code>f(2, 2)</code>: leaving item 2 calls <code>f(1, 2)</code> = 0 <em>a second time</em>; taking it gives 3 + <code>f(1, 0)</code> = 3. So <code>f(2, 2)</code> = 3.",
                        "<code>f(3, 4)</code> = max(5, 3 + 3) = 6, after 12 calls in total.",
                        "The two light items beat the single most valuable one: <strong>6</strong>.",
                    ],
                    [
                        "One item (weight 2, value 3), W = 4. Call <code>f(1, 4)</code>.",
                        "Leave it: <code>f(0, 4)</code> = 0.",
                        "Take it (2 ≤ 4): 3 + <code>f(0, 2)</code> = 3. Index 0 means no items remain, so it cannot be taken again even though capacity 2 is left.",
                        "max(0, 3) gives <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just sort by value per weight and take greedily?",
                     "Items cannot be split. In example 1 the best ratio is item (3, 5) at 1.67, but taking it leaves capacity 1, where nothing fits: greedy gets 5, the optimum is 6."],
                    ["Why does the recursion go from the last item to the first?",
                     "It is only a convention: <code>f(i, c)</code> means \"the first i items\", which lines up with row <code>i</code> of the table later. Recursing from item 0 forwards works just as well."],
                    ["Why is the take branch guarded instead of letting c go negative?",
                     "A negative capacity would need its own base case returning minus infinity. Checking <code>wt[i - 1] &lt;= c</code> before recursing keeps every state valid and the code shorter."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> the recursion is identical, with <code>@cache</code> added on <code>f</code>.",
                    "The answer for <code>(i, c)</code> does not depend on how you got there, only on which items remain and how much room is left. So when two paths reach the same state, the second one can reuse the first result.",
                    "There are only (n + 1)·(W + 1) different states, so caching turns the exponential tree into a polynomial amount of work.",
                ],
                "steps": [
                    "Decorate <code>f(i, c)</code> with <code>@cache</code>; the body is unchanged.",
                    "On the first call for a pair, the body runs: base case, \"leave\", then \"take\" if <code>wt[i - 1] &lt;= c</code>.",
                    "The result is stored under the key <code>(i, c)</code>.",
                    "Any later call with the same pair returns the stored value at once, without recursing.",
                    "Return <code>f(len(val), W)</code>.",
                ],
                "why": [
                    "Correctness is untouched: a cached value is exactly what the plain recursion would recompute, because <code>f</code> depends only on its arguments.",
                    "Each state is computed once and does O(1) work beyond its two lookups, so the time is <strong>O(n·W)</strong>; often less, since only reachable states are visited.",
                    "The cache can hold <strong>O(n·W)</strong> entries, plus an O(n) call stack.",
                    "It only helps when states repeat; that happens a lot once n and W are realistic, because many subsets share a total weight.",
                ],
                "dry": [
                    [
                        "<code>f(3, 4)</code> → leave → <code>f(2, 4)</code> → <code>f(1, 4)</code> = 5 and <code>f(1, 2)</code> = 0; both are now cached.",
                        "<code>f(2, 4)</code> = max(5, 3 + 0) = 5, cached.",
                        "Take item 3 → <code>f(2, 2)</code> → leave → <code>f(1, 2)</code>: a cache hit, 0 straight away, no call to <code>f(0, 2)</code>.",
                        "<code>f(2, 2)</code> = max(0, 3 + <code>f(1, 0)</code>) = 3. 11 calls instead of 12, 10 distinct states.",
                        "<code>f(3, 4)</code> = max(5, 3 + 3) = <strong>6</strong>.",
                    ],
                    [
                        "<code>f(1, 4)</code> calls <code>f(0, 4)</code> = 0 and <code>f(0, 2)</code> = 0. No state repeats on this tiny input.",
                        "<code>f(1, 4)</code> = max(0, 3 + 0) = 3, stored.",
                        "The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["How does memo help on example 1 if it saves only one call?",
                     "Tiny inputs barely repeat. With 20 items and W = 100 there are at most 21·101 states but up to 2<sup>20</sup> paths, so most calls become cache hits."],
                    ["Is O(n·W) polynomial?",
                     "Only in the <em>value</em> of W, not in its number of digits, so it is called pseudo-polynomial. With W around 10<sup>9</sup> this approach is useless."],
                    ["What is the risk of the memo version in Python?",
                     "The recursion depth is n, so with thousands of items it can hit the default recursion limit. The table versions have no recursion at all."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> instead of letting recursion discover states on demand, fill every <code>dp[i][c]</code> in an order where its inputs are already known.",
                    "<code>dp[i][c]</code> reads only row <code>i - 1</code> (at <code>c</code> and <code>c - w</code>), so filling row by row from i = 1 is always safe.",
                    "No recursion means no stack-depth limit, and the whole table is kept, so you could walk back from <code>dp[n][W]</code> to list the chosen items.",
                ],
                "steps": [
                    "Create <code>dp</code> with <code>n + 1</code> rows of <code>W + 1</code> zeros; row 0 (no items) stays all zero.",
                    "For each item <code>i</code> from 1 to n, read <code>w, v = wt[i - 1], val[i - 1]</code>.",
                    "For every capacity <code>c</code> from 0 to W, first copy \"leave it\": <code>dp[i][c] = dp[i - 1][c]</code>.",
                    "If <code>w &lt;= c</code>, improve it with \"take it\": <code>max(dp[i][c], v + dp[i - 1][c - w])</code>.",
                    "Return <code>dp[n][W]</code>.",
                ],
                "why": [
                    "It is the memo recurrence evaluated in a fixed order: row <code>i - 1</code> is complete before row <code>i</code> starts, so every read sees a final value.",
                    "\"Take\" reads row <code>i - 1</code>, the row <em>without</em> item i, so item i is counted at most once.",
                    "There are (n + 1)(W + 1) cells with O(1) work each: <strong>O(n·W)</strong> time and <strong>O(n·W)</strong> space.",
                    "Unlike memo it computes every cell, even unreachable ones, but with plain loops that is usually faster in practice.",
                ],
                "dry": [
                    [
                        "Row 0: [0, 0, 0, 0, 0].",
                        "Row 1, item (3, 5): only c = 3, 4 fit, so the row is [0, 0, 0, 5, 5].",
                        "Row 2, item (2, 3): c = 2 gets 3 + dp[1][0] = 3; c = 4 gets max(5, 3 + dp[1][2] = 3) = 5. Row [0, 0, 3, 5, 5].",
                        "Row 3, item (2, 3): c = 4 gets max(dp[2][4] = 5, 3 + dp[2][2] = 6) = 6. Row [0, 0, 3, 5, 6].",
                        "dp[3][4] = <strong>6</strong>.",
                    ],
                    [
                        "Row 0: [0, 0, 0, 0, 0].",
                        "Row 1, item (2, 3): c = 0, 1 copy 0; c = 2, 3, 4 each get 3 + dp[0][c - 2] = 3.",
                        "dp[1][4] reads dp[0][2] = 0 from the row <em>above</em>, so the item is not counted twice. Row [0, 0, 3, 3, 3].",
                        "dp[1][4] = <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the table have n + 1 rows, not n?",
                     "Row 0 is the base case \"no items yet\", all zeros. It lets row 1 use the same formula as every other row instead of a special case."],
                    ["How do I recover which items were taken?",
                     "Walk back from <code>(n, W)</code>: if <code>dp[i][c] != dp[i - 1][c]</code>, item i was taken, so subtract its weight from c. Either way move to row <code>i - 1</code>."],
                    ["Can I loop capacities in any order here?",
                     "Yes. Row i reads only row i - 1, which is already finished, so upward or downward capacity order gives the same row. Order only starts to matter once the rows share memory."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> the full table is replaced by two rows, <code>prev</code> (row i - 1) and <code>cur</code> (row i).",
                    "Row i reads nothing older than row i - 1, so once a row is finished every earlier row is dead weight.",
                    "Starting <code>cur</code> as a copy of <code>prev</code> fills in \"leave the item\" for every capacity in one go.",
                ],
                "steps": [
                    "<code>prev = [0] * (W + 1)</code>: the row for zero items.",
                    "For each item <code>(w, v)</code>: <code>cur = prev[:]</code>, so leaving the item is the default.",
                    "For <code>c</code> from <code>w</code> to W, set <code>cur[c] = max(prev[c], v + prev[c - w])</code>. Capacities below w cannot take the item, so they keep the copy.",
                    "Move on with <code>prev = cur</code>.",
                    "Return <code>prev[W]</code>.",
                ],
                "why": [
                    "Every value written is exactly <code>dp[i][c]</code> from the 2-D table, because both reads come from <code>prev</code>, the untouched row i - 1.",
                    "The work per item is the same as before: <strong>O(n·W)</strong> time.",
                    "Only two rows of W + 1 numbers exist at a time: <strong>O(W)</strong> space.",
                    "The cost is one row copy per item; the next rung gets rid of that too.",
                ],
                "dry": [
                    [
                        "prev = [0, 0, 0, 0, 0].",
                        "Item (3, 5): c = 3, 4 become 5. prev = [0, 0, 0, 5, 5].",
                        "Item (2, 3): c = 2 → 3; c = 3 → max(5, 3 + prev[1]) = 5; c = 4 → max(5, 3 + prev[2] = 3) = 5. prev = [0, 0, 3, 5, 5].",
                        "Item (2, 3): c = 4 → max(5, 3 + prev[2] = 3) = 6. prev = [0, 0, 3, 5, 6].",
                        "prev[4] = <strong>6</strong>.",
                    ],
                    [
                        "prev = [0, 0, 0, 0, 0]; cur starts as a copy.",
                        "Item (2, 3): c = 2, 3, 4 each become 3 + prev[c - 2] = 3.",
                        "cur[4] reads prev[2] = 0, not the freshly written cur[2] = 3, so the item is used once.",
                        "prev = [0, 0, 3, 3, 3]; the result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the right-hand side read <code>prev</code>, not <code>cur</code>?",
                     "<code>cur[c - w]</code> may already include the current item. Reading it would let the item be taken twice, which is the unbounded knapsack."],
                    ["Can I lose the item-to-choice information this way?",
                     "Yes. With only two rows you can no longer walk back to list the chosen items. Keep the full table if the question asks for the items themselves."],
                    ["Is <code>cur = prev[:]</code> necessary?",
                     "It sets <code>cur[c]</code> for capacities below <code>w</code>, which the inner loop never touches. Without it those cells would be missing or stale."],
                ],
            },
            "One row, capacity downwards": {
                "idea": [
                    "<strong>What changed:</strong> a single row <code>dp</code> is updated in place, with capacities visited from W <em>down</em> to w.",
                    "Cell <code>c</code> needs the old values at <code>c</code> and <code>c - w</code>. Going downwards, <code>c - w</code> is smaller than <code>c</code>, so it has not been overwritten yet this round and still holds row i - 1.",
                    "Going upwards would read a <code>dp[c - w]</code> that already includes this item, letting it be taken again. That is the classic bug, and example 2 is built to expose it.",
                ],
                "steps": [
                    "<code>dp = [0] * (W + 1)</code>.",
                    "For each item <code>(w, v)</code>, loop <code>c</code> over <code>range(W, w - 1, -1)</code>.",
                    "Set <code>dp[c] = max(dp[c], v + dp[c - w])</code>: the old <code>dp[c]</code> is \"leave\", the other term is \"take\".",
                    "Capacities below <code>w</code> are untouched, which already means \"leave it\".",
                    "Return <code>dp[W]</code>.",
                ],
                "why": [
                    "When <code>dp[c]</code> is written, <code>dp[c]</code> and <code>dp[c - w]</code> both still hold row i - 1, so the update is exactly the 2-D recurrence.",
                    "The time is still <strong>O(n·W)</strong>, one max per cell.",
                    "One row and no copies: <strong>O(W)</strong> space, the smallest of the ladder.",
                    "This is the form to write in an interview, but say why the loop runs downwards.",
                ],
                "dry": [
                    [
                        "Item (3, 5): c = 4 → max(0, 5 + dp[1]) = 5; c = 3 → 5. dp = [0, 0, 0, 5, 5].",
                        "Item (2, 3): c = 4 → max(5, 3 + dp[2] = 0) = 5; c = 3 → 5; c = 2 → 3. dp = [0, 0, 3, 5, 5].",
                        "Item (2, 3): c = 4 first → max(5, 3 + dp[2]); dp[2] is still 3 from the previous item, so 6.",
                        "c = 3 → 5, c = 2 → 3. dp = [0, 0, 3, 5, 6].",
                        "dp[4] = <strong>6</strong>.",
                    ],
                    [
                        "dp = [0, 0, 0, 0, 0], item (2, 3).",
                        "c = 4 first: max(0, 3 + dp[2] = 0) = 3. dp[2] has not been touched yet.",
                        "c = 3 → 3, c = 2 → 3. dp = [0, 0, 3, 3, 3].",
                        "Upwards would set dp[2] = 3 first and then dp[4] = 3 + 3 = 6, taking the one item twice. Downwards gives <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["What exactly goes wrong if I loop upwards?",
                     "On example 2 upwards gives 6 instead of 3: dp[2] becomes 3, then dp[4] = 3 + dp[2] uses the same item again. Upwards is the right loop for the unbounded version (Coin Change)."],
                    ["Why does the loop stop at <code>w</code> instead of 0?",
                     "For <code>c &lt; w</code> the item does not fit and <code>dp[c - w]</code> would be a negative index, which Python silently wraps around. Stopping at w avoids both."],
                    ["Does the order of the items matter?",
                     "No. Any order of items gives the same final row, because the best subset does not depend on the order you consider them in."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ partition equal subset sum
    "partition-equal-subset-sum": {
        "examples": [
            {"call": "can_partition([1, 2, 3, 4])", "expect": "True"},
            {"call": "can_partition([2, 2, 3, 5])", "expect": "False"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Two halves with equal sums exist exactly when some subset sums to <code>total // 2</code>; the rest then makes the other half automatically. An odd total can be rejected at once.",
                    "So this is a 0/1 knapsack with booleans: <code>can(i, s)</code> asks \"can some of the first <code>i</code> numbers make exactly <code>s</code>?\"",
                    "Each number is either used (if <code>nums[i - 1] &lt;= s</code>) or skipped, and one success is enough.",
                ],
                "steps": [
                    "Compute <code>total</code>; if it is odd, return <code>False</code>.",
                    "<code>can(i, s)</code>: if <code>s == 0</code>, return <code>True</code> (the empty subset works).",
                    "If <code>i == 0</code> and s is still positive, return <code>False</code>.",
                    "Try using the number: if <code>nums[i - 1] &lt;= s and can(i - 1, s - nums[i - 1])</code>, return <code>True</code>.",
                    "Otherwise return <code>can(i - 1, s)</code>, skipping it. Start with <code>can(len(nums), total // 2)</code>.",
                ],
                "why": [
                    "Every subset is a path of use/skip choices, so if one sums to half, some path reaches <code>s == 0</code>.",
                    "Each call branches at most twice and the depth is n: <strong>O(2<sup>n</sup>)</strong> time in the worst case, typically a \"no\" answer that must explore everything.",
                    "The call stack is at most n deep: <strong>O(n)</strong> space.",
                    "A \"yes\" can return early, but a \"no\" (example 2) re-solves the same <code>(i, s)</code> repeatedly.",
                ],
                "dry": [
                    [
                        "total = 10, half = 5. Call <code>can(4, 5)</code>.",
                        "Use 4 → <code>can(3, 1)</code>: 3 &gt; 1, so it falls through to <code>can(2, 1)</code>; 2 &gt; 1, so <code>can(1, 1)</code>.",
                        "Use 1 → <code>can(0, 0)</code>: s == 0, True.",
                        "True bubbles straight up after only 5 calls: {4, 1} makes 5, so the result is <strong>True</strong>.",
                    ],
                    [
                        "total = 12, half = 6. Using 5 → <code>can(3, 1)</code>: nothing left fits 1, False.",
                        "Skip 5 → <code>can(3, 6)</code>: use 3 → <code>can(2, 3)</code> tries 2 + <code>can(1, 1)</code> (False) and <code>can(1, 3)</code> (False).",
                        "Skip 3 → <code>can(2, 6)</code>: <code>can(1, 4)</code> and <code>can(1, 6)</code> are both False.",
                        "<code>can(1, 1)</code> was solved twice along the way; 19 calls in all.",
                        "Reachable sums are 0, 2, 3, 4, 5, 7, … but never 6: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is an even total not enough?",
                     "Example 2 has total 12 but no subset of [2, 2, 3, 5] makes 6. Parity only rules cases out; the subset search does the real work."],
                    ["Why check <code>s == 0</code> before <code>i == 0</code>?",
                     "When the last needed number has just been used, both are zero together and the answer must be True. Checking <code>i == 0</code> first would wrongly return False."],
                    ["Why is target half and not the full total?",
                     "If one group sums to half, the other group is everything else, which also sums to half. Finding one group is enough."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> is added on <code>can</code>; nothing else.",
                    "Different use/skip choices among later numbers can leave the same <code>(i, s)</code>, and from there the answer is identical.",
                    "With at most (n + 1)·(half + 1) states, the exponential tree collapses into a table of booleans filled on demand.",
                ],
                "steps": [
                    "Reject an odd total, as before.",
                    "Wrap <code>can(i, s)</code> in <code>@cache</code>.",
                    "Base cases: <code>s == 0</code> → True, <code>i == 0</code> → False.",
                    "Try \"use\" when <code>nums[i - 1] &lt;= s</code>, then \"skip\"; the result is cached under <code>(i, s)</code>.",
                    "Return <code>can(len(nums), total // 2)</code>.",
                ],
                "why": [
                    "<code>can</code> depends only on its arguments, so a cached answer is exactly what recomputation would give.",
                    "Each state is computed once with O(1) work: <strong>O(n·S)</strong> time for S = total / 2.",
                    "The cache holds up to <strong>O(n·S)</strong> booleans, plus an O(n) stack.",
                    "On \"no\" instances, where the plain recursion is at its worst, memo gains the most.",
                ],
                "dry": [
                    [
                        "<code>can(4, 5)</code> → <code>can(3, 1)</code> → <code>can(2, 1)</code> → <code>can(1, 1)</code> → <code>can(0, 0)</code> = True.",
                        "Each state is cached as True on the way back up.",
                        "No state repeats before success, so memo changes nothing here. The result is <strong>True</strong>.",
                    ],
                    [
                        "Using 5 first: <code>can(3, 1)</code>, <code>can(2, 1)</code>, <code>can(1, 1)</code> are all cached as False.",
                        "Later, <code>can(2, 3)</code> uses a 2 and asks for <code>can(1, 1)</code>: a cache hit, False at once.",
                        "<code>can(0, 1)</code> and <code>can(0, 4)</code> are also hits when requested again.",
                        "15 distinct states are solved; <code>can(4, 6)</code> is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["What does S stand for in O(n·S)?",
                     "S is <code>total // 2</code>, the target. With n = 200 numbers up to 100 each, S is at most 10<sup>4</sup>, so about 2·10<sup>6</sup> states."],
                    ["Do I need to clear the cache between calls?",
                     "No. <code>can</code> is defined inside <code>can_partition</code>, so each call to the outer function creates a fresh cache."],
                    ["Would it help to sort the numbers in decreasing order first?",
                     "It often finds a \"yes\" sooner, and big numbers fail the <code>&lt;= s</code> test early, but the worst case is still O(n·S)."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> the states are filled in loops, row by row, instead of being discovered by recursion.",
                    "<code>dp[i][s]</code> is True when some subset of the first <code>i</code> numbers sums to exactly <code>s</code>; column 0 is True in every row.",
                    "Row i reads only row i - 1, so the order \"all of row 1, then all of row 2…\" is always valid.",
                ],
                "steps": [
                    "Reject an odd total; set <code>half, n = total // 2, len(nums)</code>.",
                    "Create <code>dp</code> as <code>(n + 1) × (half + 1)</code> False, then set <code>dp[i][0] = True</code> for every row.",
                    "For row <code>i</code> with <code>x = nums[i - 1]</code> and every <code>s</code> from 1 to half:",
                    "<code>dp[i][s] = dp[i - 1][s] or (x &lt;= s and dp[i - 1][s - x])</code>: skip x, or use it on top of a sum reachable without it.",
                    "Return <code>dp[n][half]</code>.",
                ],
                "why": [
                    "By induction on i, row i marks exactly the subset sums (up to half) of the first i numbers: each is either a sum without x, or one with x added.",
                    "Both reads use row i - 1, so x is used at most once per subset.",
                    "(n + 1)·(half + 1) cells with O(1) work: <strong>O(n·S)</strong> time and <strong>O(n·S)</strong> space.",
                    "Sums above half are never needed: if a subset reaches half, the answer is already known.",
                ],
                "dry": [
                    [
                        "half = 5. Row 0 has only sum 0.",
                        "Row 1 (x = 1): {0, 1}. Row 2 (x = 2): {0, 1, 2, 3}.",
                        "Row 3 (x = 3): dp[3][5] = dp[2][2] = True, so {0, 1, 2, 3, 4, 5}.",
                        "Row 4 (x = 4) keeps all of them.",
                        "dp[4][5] is <strong>True</strong>.",
                    ],
                    [
                        "half = 6. Row 1 (x = 2): {0, 2}. Row 2 (x = 2): {0, 2, 4}.",
                        "Row 3 (x = 3): adds 3 and 5, giving {0, 2, 3, 4, 5}; dp[3][6] needs dp[2][3], which is False.",
                        "Row 4 (x = 5): dp[4][6] = dp[3][6] or dp[3][1], both False.",
                        "The row stays {0, 2, 3, 4, 5}, so dp[4][6] is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why set <code>dp[i][0] = True</code> in every row and not just row 0?",
                     "The inner loop starts at <code>s = 1</code>, so column 0 is never written. Setting it everywhere says \"the empty subset makes 0\" for every prefix."],
                    ["Is <code>x &lt;= s and dp[i - 1][s - x]</code> safe when x &gt; s?",
                     "Yes. <code>and</code> short-circuits, so the index <code>s - x</code> (which would be negative and wrap around) is never evaluated."],
                    ["Could this table also tell me which numbers form a half?",
                     "Yes. From <code>(n, half)</code>, if <code>dp[i - 1][s]</code> is True skip number i, otherwise it was used: subtract it from s. Repeat up to row 0."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> only <code>prev</code> (row i - 1) and <code>cur</code> (row i) are stored.",
                    "Row i reads only row i - 1, so older rows can be dropped the moment the next row is done.",
                    "Copying <code>prev</code> into <code>cur</code> handles \"skip x\" for every sum at once.",
                ],
                "steps": [
                    "Reject an odd total; <code>half = total // 2</code>.",
                    "<code>prev = [True] + [False] * half</code>: only sum 0 is reachable with no numbers.",
                    "For each <code>x</code>: <code>cur = prev[:]</code>.",
                    "For <code>s</code> from x to half: <code>cur[s] = prev[s] or prev[s - x]</code>.",
                    "Set <code>prev = cur</code>; after the loop return <code>prev[half]</code>.",
                ],
                "why": [
                    "Both reads come from <code>prev</code>, so each value equals the 2-D table's <code>dp[i][s]</code>.",
                    "The work is unchanged: <strong>O(n·S)</strong> time.",
                    "Two rows of half + 1 booleans: <strong>O(S)</strong> space.",
                    "The loop starts at <code>s = x</code>, which drops the <code>x &lt;= s</code> test from the 2-D version.",
                ],
                "dry": [
                    [
                        "prev = {0}.",
                        "x = 1 → {0, 1}. x = 2 → {0, 1, 2, 3}.",
                        "x = 3 → cur[5] = prev[2] = True, giving {0, 1, 2, 3, 4, 5}.",
                        "x = 4 changes nothing new.",
                        "prev[5] is <strong>True</strong>.",
                    ],
                    [
                        "prev = {0}. x = 2 → {0, 2}. x = 2 → cur[4] = prev[2], giving {0, 2, 4}.",
                        "x = 3 → adds 3 and 5. cur[6] = prev[3] is False.",
                        "x = 5 → cur[6] = prev[6] or prev[1], both False.",
                        "prev[6] is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why read <code>prev[s - x]</code> and not <code>cur[s - x]</code>?",
                     "<code>cur[s - x]</code> may have just been set using x itself. Reading it would let one number count twice, so [1] would appear to reach every sum."],
                    ["Can this version stop early?",
                     "Yes, you could return as soon as <code>cur[half]</code> becomes True. The one-row version below does exactly that."],
                    ["Why not a set of reachable sums instead?",
                     "A set works and reads naturally, but a boolean list of fixed size is faster and has an O(S) bound. The bitset approach pushes the list idea further."],
                ],
            },
            "One row, sum downwards": {
                "idea": [
                    "<strong>What changed:</strong> one boolean row <code>can</code> is updated in place, with sums visited from <code>half</code> down to <code>x</code>.",
                    "<code>can[s]</code> needs the old <code>can[s - x]</code>, which is smaller than s. Going downwards, it has not been changed in this round yet, so each number is used at most once.",
                    "Once <code>can[half]</code> is True the answer is settled, so the loop returns early.",
                ],
                "steps": [
                    "Reject an odd total; <code>can = [True] + [False] * half</code>.",
                    "For each <code>x</code>, loop <code>s</code> over <code>range(half, x - 1, -1)</code>.",
                    "If <code>can[s - x]</code> is True, set <code>can[s] = True</code>. Sums only ever turn from False to True.",
                    "After each number, if <code>can[half]</code> is True, return True.",
                    "If all numbers are processed, return <code>can[half]</code>.",
                ],
                "why": [
                    "When <code>can[s]</code> is updated, <code>can[s - x]</code> still holds the value from before x, so the in-place row matches the two-row version exactly.",
                    "Each number costs at most S steps: <strong>O(n·S)</strong> time, often less thanks to the early return.",
                    "A single row of half + 1 booleans: <strong>O(S)</strong> space, with no copies.",
                ],
                "dry": [
                    [
                        "can = {0}. x = 1: s = 1 from can[0] → {0, 1}.",
                        "x = 2: s = 3 (can[1]), s = 2 (can[0]) → {0, 1, 2, 3}.",
                        "x = 3: s = 5 (can[2]), 4 (can[1]), 3 (can[0]) → {0, 1, 2, 3, 4, 5}.",
                        "can[5] is True, so it returns right after x = 3; the 4 is never processed.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "x = 2 → {0, 2}. x = 2: s = 4 from can[2], s = 2 already → {0, 2, 4}.",
                        "x = 3: s = 6 needs can[3] (False); s = 5 from can[2]; s = 3 from can[0] → {0, 2, 3, 4, 5}.",
                        "x = 5: s = 6 needs can[1] (False); s = 5 is already True.",
                        "can[6] never turns on: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["What if I loop s upwards here?",
                     "Each number could be reused. On example 2 the first 2 would mark 2, then 4 from can[2], then 6 from can[4], so it wrongly returns True; [1, 2, 5] also wrongly gives True (1 + 1 + 1 + 1 = 4)."],
                    ["Is the early return worth it?",
                     "It never hurts and often helps on \"yes\" inputs. For \"no\" inputs every number is processed anyway."],
                    ["Why only set True, never False?",
                     "A sum that was reachable without x is still reachable with x available (just skip x), so skip is the default and no reset is needed."],
                ],
            },
            "Bitset of reachable sums": {
                "idea": [
                    "<strong>What changed:</strong> the boolean row is packed into one Python integer, <code>bits</code>, where bit s is 1 when sum s is reachable.",
                    "Adding a number x to every reachable sum is a left shift by x, and keeping the old sums too is an OR: <code>bits |= bits &lt;&lt; x</code>.",
                    "The shift processes many sums per machine word at once, so the same O(n·S) work runs much faster in practice.",
                ],
                "steps": [
                    "Reject an odd total.",
                    "<code>bits = 1</code>: only bit 0 is on, sum 0 is reachable.",
                    "For each <code>x</code>: <code>bits |= bits &lt;&lt; x</code>.",
                    "Test bit <code>total // 2</code> with <code>bits &gt;&gt; (total // 2) &amp; 1</code>.",
                    "Return it as a <code>bool</code>.",
                ],
                "why": [
                    "<code>bits &lt;&lt; x</code> is computed from the old <code>bits</code> before the OR, so each number is added at most once, like the downward loop.",
                    "Each shift/OR touches about total / w machine words (w = 64): <strong>O(n·S / w)</strong> time.",
                    "The integer has at most total + 1 bits: <strong>O(S)</strong> bits of space, far smaller than a list of booleans.",
                    "It tracks sums above half too, which is harmless; masking them off would only save a little.",
                ],
                "dry": [
                    [
                        "bits = 1 (sum 0).",
                        "x = 1 → 0b11: {0, 1}. x = 2 → 0b1111: {0, 1, 2, 3}.",
                        "x = 3 → {0, …, 6}. x = 4 → {0, …, 10}.",
                        "Bit 5 is on: <strong>True</strong>.",
                    ],
                    [
                        "bits = 1. x = 2 → 0b101: {0, 2}. x = 2 → 0b10101: {0, 2, 4}.",
                        "x = 3 → {0, 2, 3, 4, 5, 7}.",
                        "x = 5 → {0, 2, 3, 4, 5, 7, 8, 9, 10, 12}.",
                        "Bit 6 is off: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>bits |= bits &lt;&lt; x</code> not reuse x?",
                     "The right-hand side is evaluated in full from the old value first, then OR-ed in. No sum that already includes x is shifted again in the same step."],
                    ["Does this work in languages without big integers?",
                     "In C++ you use <code>std::bitset&lt;N&gt;</code> with a fixed N at least the maximum total. Java has <code>BitSet</code>, but it has no shift, so you would write the loop yourself."],
                    ["Why <code>&amp; 1</code> after shifting right?",
                     "The shift brings bit <code>total // 2</code> to position 0; <code>&amp; 1</code> discards every higher bit, leaving 0 or 1."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ target sum
    "target-sum": {
        "examples": [
            {"call": "find_target_sum_ways([1, 2, 1], 2)", "expect": "2"},
            {"call": "find_target_sum_ways([0, 0, 1], 1)", "expect": "4"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Every number gets a <code>+</code> or a <code>-</code>, and you count the sign patterns whose total equals <code>target</code>.",
                    "Work backwards from the last number: <code>count(i, s)</code> = the number of ways to sign the first <code>i</code> numbers so they total <code>s</code>.",
                    "If number x gets <code>+</code>, the first i - 1 numbers must make <code>s - x</code>; if it gets <code>-</code>, they must make <code>s + x</code>. Add the two counts.",
                ],
                "steps": [
                    "Base case: <code>count(0, s)</code> is 1 if <code>s == 0</code> (the empty pattern totals 0), otherwise 0.",
                    "Let <code>x = nums[i - 1]</code>.",
                    "Return <code>count(i - 1, s - x) + count(i - 1, s + x)</code>; there is no \"skip\" option, every number must be signed.",
                    "The answer is <code>count(len(nums), target)</code>.",
                ],
                "why": [
                    "Each sign pattern is exactly one root-to-leaf path, and it adds 1 at its leaf only when the signed total matches, so the sum counts each valid pattern once.",
                    "Each call branches twice for n levels: <strong>O(2<sup>n</sup>)</strong> time, with no pruning possible since every pattern must be counted.",
                    "The call stack is n deep: <strong>O(n)</strong> space.",
                    "Many patterns of the first numbers land on the same partial sum, so the same <code>(i, s)</code> is recounted; memo removes that.",
                ],
                "dry": [
                    [
                        "<code>count(3, 2)</code>, x = 1 → <code>count(2, 1)</code> (+1) + <code>count(2, 3)</code> (−1).",
                        "<code>count(2, 1)</code>, x = 2 → <code>count(1, -1)</code> = 1 (−1 works) + <code>count(1, 3)</code> = 0. So 1.",
                        "<code>count(2, 3)</code>, x = 2 → <code>count(1, 1)</code> = 1 (+1 works) + <code>count(1, 5)</code> = 0. So 1.",
                        "The two patterns are −1 + 2 + 1 and +1 + 2 − 1, found in 15 calls.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "<code>count(3, 1)</code>, x = 1 → <code>count(2, 0)</code> + <code>count(2, 2)</code>.",
                        "<code>count(2, 0)</code>, x = 0: both branches are <code>count(1, 0)</code>, because s − 0 = s + 0.",
                        "Each <code>count(1, 0)</code> is 2 (+0 and −0), so <code>count(2, 0)</code> = 4; <code>count(2, 2)</code> = 0.",
                        "+0 and −0 count as different patterns, so the result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is there no \"skip\" branch, unlike knapsack?",
                     "The problem says every number gets a sign. Skipping would count patterns that leave numbers out, which are not allowed."],
                    ["Why do zeros double the answer?",
                     "+0 and −0 are different sign patterns with the same total. Example 2 has two zeros, so its single real pattern (+1) is counted 2 × 2 = 4 times."],
                    ["Can s go negative?",
                     "Yes, and that is fine: s is only a function argument here. It matters once s becomes a list index, which is why the table versions shift every sum by T."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> is added on <code>count</code>; the recurrence is the same.",
                    "<code>count(i, s)</code> depends only on which numbers are left and what they must total, so repeated states can share one answer.",
                    "The partial sum s always stays within <code>target ± T</code> (T = sum of the numbers), so there are at most about n·(2T + 1) states.",
                ],
                "steps": [
                    "Decorate <code>count(i, s)</code> with <code>@cache</code>.",
                    "Base case at <code>i == 0</code>: 1 if <code>s == 0</code> else 0.",
                    "Otherwise return <code>count(i - 1, s - x) + count(i - 1, s + x)</code> with <code>x = nums[i - 1]</code>.",
                    "Repeated <code>(i, s)</code> pairs come straight from the cache.",
                    "Return <code>count(len(nums), target)</code>.",
                ],
                "why": [
                    "A cached count equals what recomputing would return, since <code>count</code> has no hidden state.",
                    "Each state does O(1) work once: <strong>O(n·T)</strong> time.",
                    "The cache holds up to <strong>O(n·T)</strong> counts, plus an O(n) stack.",
                    "Negative s needs no special handling, because a dictionary-backed cache accepts any integer key.",
                ],
                "dry": [
                    [
                        "<code>count(3, 2)</code> → <code>count(2, 1)</code> → <code>count(1, -1)</code> calls <code>count(0, -2)</code> and <code>count(0, 0)</code>.",
                        "<code>count(1, 3)</code> calls <code>count(0, 2)</code> and <code>count(0, 4)</code>.",
                        "Inside <code>count(2, 3)</code>: <code>count(0, 0)</code>, <code>count(0, 2)</code> and <code>count(0, 4)</code> are cache hits.",
                        "12 distinct states, 3 hits. The result is <strong>2</strong>.",
                    ],
                    [
                        "<code>count(2, 0)</code> asks for <code>count(1, 0)</code> twice; the second time is a cache hit worth 2.",
                        "Inside <code>count(1, 0)</code>, the second <code>count(0, 0)</code> is a hit as well.",
                        "<code>count(2, 2)</code> → <code>count(1, 2)</code> = 0, and its twin call is a hit.",
                        "Only 7 distinct states. <code>count(3, 1)</code> = 4 + 0 = <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["What is T in O(n·T)?",
                     "T is the sum of the numbers. Every reachable partial sum lies in a range of width 2T + 1, so that bounds the states per level."],
                    ["Why does a cache work with negative sums when an array would not?",
                     "<code>@cache</code> keys on the argument tuple, so <code>(1, -1)</code> is as good a key as any. The table needs the shift by T for the same reason a list cannot take index −1 meaningfully."],
                    ["When is memo clearly better than the table here?",
                     "When few sums are reachable, e.g. a handful of large numbers: memo visits only reachable states, while the table fills all 2T + 1 columns per row."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> the states are stored in a table filled row by row, so no recursion is needed.",
                    "Sums run from −T to T, but list indices cannot be negative, so column <code>s + T</code> holds sum s.",
                    "<code>dp[i][s + T]</code> collects from the row above at <code>s - x</code> (x signed +) and <code>s + x</code> (x signed −).",
                ],
                "steps": [
                    "<code>T = sum(nums)</code>; if <code>abs(target) &gt; T</code>, no pattern can reach it, so return 0.",
                    "Create <code>dp</code> with n + 1 rows of <code>2 * T + 1</code> zeros and set <code>dp[0][T] = 1</code> (sum 0, no numbers).",
                    "For row <code>i</code> with <code>x = nums[i - 1]</code>, loop <code>s</code> from −T to T.",
                    "If <code>s - x &gt;= -T</code>, add <code>dp[i - 1][s - x + T]</code>; if <code>s + x &lt;= T</code>, add <code>dp[i - 1][s + x + T]</code>.",
                    "Return <code>dp[n][target + T]</code>.",
                ],
                "why": [
                    "Row i is complete once row i - 1 is, and each cell adds exactly the two ways number i can be signed, so by induction <code>dp[i][s + T]</code> = <code>count(i, s)</code>.",
                    "The bounds checks only skip sums outside −T..T, which no pattern can produce anyway.",
                    "(n + 1)·(2T + 1) cells with O(1) work: <strong>O(n·T)</strong> time and <strong>O(n·T)</strong> space.",
                ],
                "dry": [
                    [
                        "T = 4, columns cover −4..4. Row 0: {0: 1}.",
                        "Row 1 (x = 1): {−1: 1, 1: 1}.",
                        "Row 2 (x = 2): {−3: 1, −1: 1, 1: 1, 3: 1}.",
                        "Row 3 (x = 1): sum 2 gets dp[2][1] + dp[2][3] = 1 + 1, so {−4: 1, −2: 2, 0: 2, 2: 2, 4: 1}.",
                        "dp[3][2 + 4] = <strong>2</strong>.",
                    ],
                    [
                        "T = 1, columns cover −1..1. Row 0: {0: 1}.",
                        "Row 1 (x = 0): column 0 adds dp[0][0] twice (s − 0 and s + 0), so {0: 2}.",
                        "Row 2 (x = 0): {0: 4}.",
                        "Row 3 (x = 1): sums −1 and 1 each get 4.",
                        "dp[3][1 + 1] = <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the early <code>abs(target) &gt; T</code> check?",
                     "<code>target + T</code> would be outside the table (or negative and silently wrap around). No pattern can exceed T in absolute value, so the answer is 0."],
                    ["Why is this a \"pull\" table rather than \"push\"?",
                     "Each cell pulls from the two cells it can come from. Pushing (for each reachable sum, add to s + x and s − x in the next row) gives the same result."],
                    ["Why is the row width 2T + 1 and not T + 1?",
                     "Partial sums can be negative here, unlike knapsack capacities, so both sides of zero are needed. The subset reduction below gets rid of the negative half."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> only the previous row <code>prev</code> and a new row <code>cur</code> are kept.",
                    "<code>cur</code> starts as all zeros, not as a copy of <code>prev</code>: there is no \"skip\" option, every number moves every sum.",
                    "One row alone is not enough: cell s reads both <code>s - x</code> and <code>s + x</code>, and either loop direction would overwrite one of them first.",
                ],
                "steps": [
                    "Return 0 if <code>abs(target) &gt; T</code>.",
                    "<code>prev = [0] * (2 * T + 1)</code> with <code>prev[T] = 1</code>.",
                    "For each <code>x</code>: <code>cur = [0] * (2 * T + 1)</code>.",
                    "For every s in −T..T, add <code>prev[s - x + T]</code> and <code>prev[s + x + T]</code> when they are in range.",
                    "Set <code>prev = cur</code>; return <code>prev[target + T]</code>.",
                ],
                "why": [
                    "Each <code>cur</code> equals the corresponding row of the 2-D table, because it is built only from the previous row.",
                    "Same work as the table: <strong>O(n·T)</strong> time.",
                    "Two rows of 2T + 1 counts: <strong>O(T)</strong> space.",
                ],
                "dry": [
                    [
                        "prev = {0: 1}.",
                        "x = 1 → {−1: 1, 1: 1}. x = 2 → {−3: 1, −1: 1, 1: 1, 3: 1}.",
                        "x = 1 → cur at 2 = prev at 1 + prev at 3 = 2.",
                        "prev at 2 is <strong>2</strong>.",
                    ],
                    [
                        "prev = {0: 1}.",
                        "x = 0 → {0: 2}. x = 0 → {0: 4}.",
                        "x = 1 → {−1: 4, 1: 4}.",
                        "prev at 1 is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can't I update one row in place like 0/1 knapsack?",
                     "Knapsack reads only smaller indices, so a downward loop protects them. Here cell s reads both a smaller and a larger index, so one of them is always overwritten too early."],
                    ["Why <code>cur = [0] * …</code> instead of <code>prev[:]</code>?",
                     "Copying would mean \"number i may be left unsigned\", adding patterns that skip numbers and overcounting."],
                    ["Is there a way to get down to one row?",
                     "Yes: change the problem into a subset count, as the next approach does. Then each cell reads only smaller sums."],
                ],
            },
            "Reduce to subset count, one row": {
                "idea": [
                    "<strong>What changed:</strong> the problem is rewritten so it becomes a plain 0/1 knapsack count. Let P be the sum of the numbers signed + and N the sum of those signed −.",
                    "Then P − N = target and P + N = T, so <strong>P = (T + target) / 2</strong>. Counting sign patterns is the same as counting subsets that sum to P.",
                    "Subset counting reads only <code>ways[s]</code> and the smaller <code>ways[s - x]</code>, so one row updated downwards is enough, and the negative half of the table disappears.",
                ],
                "steps": [
                    "<code>T = sum(nums)</code>. If <code>abs(target) &gt; T</code> or <code>(T + target) % 2</code> is odd, return 0.",
                    "<code>P = (T + target) // 2</code>; <code>ways = [1] + [0] * P</code> (the empty subset makes 0).",
                    "For each <code>x</code>, loop <code>s</code> from P down to x.",
                    "<code>ways[s] += ways[s - x]</code>: subsets making s now also include those that make s − x plus x.",
                    "Return <code>ways[P]</code>.",
                ],
                "why": [
                    "Choosing the + group fixes the whole pattern, and the algebra above shows the + group must sum to exactly P, so patterns and subsets match one to one.",
                    "The downward loop keeps <code>ways[s - x]</code> at its pre-x value, so each number is in a subset at most once.",
                    "P ≤ T, so the time is <strong>O(n·P)</strong> and the space is <strong>O(P)</strong>: at most half the columns of the 2-row version, and a quarter of the space.",
                    "A zero gives <code>ways[s] += ways[s]</code>, doubling every count, which matches +0 and −0.",
                ],
                "dry": [
                    [
                        "T = 4, target = 2, so P = 3. ways = [1, 0, 0, 0].",
                        "x = 1: s = 1 gets ways[0] → [1, 1, 0, 0].",
                        "x = 2: s = 3 gets ways[1], s = 2 gets ways[0] → [1, 1, 1, 1].",
                        "x = 1: s = 3 += ways[2], s = 2 += ways[1], s = 1 += ways[0] → [1, 2, 2, 2].",
                        "ways[3] = <strong>2</strong>: the subsets {1, 2} with either 1.",
                    ],
                    [
                        "T = 1, target = 1, so P = 1. ways = [1, 0].",
                        "x = 0: the loop runs s = 1, 0; ways[0] += ways[0] doubles it → [2, 0].",
                        "x = 0: doubles again → [4, 0].",
                        "x = 1: ways[1] += ways[0] → [4, 4].",
                        "ways[1] = <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must T + target be even?",
                     "P = (T + target) / 2 must be a whole number, since it is a sum of integers. If it is odd, no split works and the answer is 0."],
                    ["Does the downward loop handle x = 0 correctly?",
                     "Yes. <code>range(P, -1, -1)</code> includes s = 0, and <code>ways[s] += ways[s]</code> doubles each count once, which is exactly the factor 2 for ±0."],
                    ["Can I use N = (T − target) / 2 instead?",
                     "Yes, counting subsets that sum to N gives the same answer. When target is positive N is smaller, so the row is shorter."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ last stone weight II
    "last-stone-weight-ii": {
        "examples": [
            {"call": "last_stone_weight_ii([3, 5, 6])", "expect": "2"},
            {"call": "last_stone_weight_ii([3, 3])", "expect": "0"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "However you smash the stones, the last weight is a signed sum: some stones end up counted +, the rest −. So the stones split into groups A and B, and the result is |A − B|.",
                    "Every split can also be achieved by some smashing order, so the task is: split the stones to make |A − B| as small as possible.",
                    "<code>f(i, a)</code>: stones from index i on are still to be placed, and group A already weighs <code>a</code>. Try each stone in A and in B.",
                ],
                "steps": [
                    "<code>total = sum(stones)</code>; B's weight is always <code>total - a</code> at the end.",
                    "Base case: when <code>i == len(stones)</code>, return <code>abs(total - 2 * a)</code>, which is |A − B|.",
                    "Otherwise put stone i in A: <code>f(i + 1, a + stones[i])</code>.",
                    "Or put it in B: <code>f(i + 1, a)</code>.",
                    "Return the smaller; start with <code>f(0, 0)</code>.",
                ],
                "why": [
                    "Every split is one leaf, and each leaf returns that split's difference, so the minimum over all leaves is the best possible split.",
                    "Two branches per stone, n levels: <strong>O(2<sup>n</sup>)</strong> time.",
                    "The call stack is n deep: <strong>O(n)</strong> space.",
                    "This direction goes forwards (i from 0 up), unlike the knapsack recursions; it makes no difference to the result.",
                ],
                "dry": [
                    [
                        "total = 14. The 8 leaves are the values of a: 14, 8, 9, 3, 11, 5, 6, 0.",
                        "Their |14 − 2a| values are 14, 2, 4, 8, 8, 4, 2, 14.",
                        "a = 8 means A = {3, 5}, B = {6}: difference 2. a = 6 is the mirror split.",
                        "15 calls and no state repeats on this input.",
                        "The minimum is <strong>2</strong>: smash 6 with 5 (leaves 1), then 3 with 1 (leaves 2).",
                    ],
                    [
                        "total = 6. <code>f(0, 0)</code> → <code>f(1, 3)</code> and <code>f(1, 0)</code>.",
                        "<code>f(1, 3)</code> → <code>f(2, 6)</code> = 6 and <code>f(2, 3)</code> = 0.",
                        "<code>f(1, 0)</code> → <code>f(2, 3)</code> = 0 again, and <code>f(2, 0)</code> = 6.",
                        "Equal groups {3} and {3} cancel: <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is every split reachable by smashing?",
                     "Repeatedly smash the heaviest stone of the heavier group against a stone of the other; differences go back into play. The tests check the result against all 2<sup>n</sup> sign patterns."],
                    ["Why not greedily smash the two heaviest stones (Last Stone Weight I)?",
                     "It is not optimal. On [2, 2, 2, 3, 3] greedy smashes 3 with 3, then 2 with 2, leaving 2; the split {2, 2, 2} against {3, 3} leaves 0."],
                    ["Why <code>abs(total - 2 * a)</code>?",
                     "A weighs a and B weighs total − a, so A − B = 2a − total. The absolute value is the leftover stone."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> is added on <code>f</code>.",
                    "Two different ways of placing the first stones can give group A the same weight; from then on the best finish is the same.",
                    "a never exceeds the total, so there are at most (n + 1)·(total + 1) states.",
                ],
                "steps": [
                    "Compute <code>total</code>.",
                    "Wrap <code>f(i, a)</code> in <code>@cache</code>.",
                    "At the end return <code>abs(total - 2 * a)</code>.",
                    "Otherwise return <code>min(f(i + 1, a + stones[i]), f(i + 1, a))</code>; the result is stored under <code>(i, a)</code>.",
                    "Return <code>f(0, 0)</code>.",
                ],
                "why": [
                    "<code>f</code> depends only on <code>(i, a)</code>, so caching does not change any result.",
                    "Each state is solved once in O(1): <strong>O(n·T)</strong> time, with T the total weight.",
                    "The cache holds <strong>O(n·T)</strong> entries, plus an O(n) stack.",
                ],
                "dry": [
                    [
                        "The weights 3, 5, 6 have all-different subset sums, so all 15 states are new.",
                        "<code>f(1, 3)</code> = min(<code>f(2, 8)</code> = 2, <code>f(2, 3)</code> = 4) = 2.",
                        "<code>f(1, 0)</code> = min(<code>f(2, 5)</code> = 4, <code>f(2, 0)</code> = 2) = 2.",
                        "<code>f(0, 0)</code> = <strong>2</strong>.",
                    ],
                    [
                        "<code>f(1, 3)</code> computes <code>f(2, 6)</code> = 6 and <code>f(2, 3)</code> = 0 and caches both.",
                        "<code>f(1, 0)</code> asks for <code>f(2, 3)</code>: a cache hit.",
                        "6 distinct states, 1 hit.",
                        "<code>f(0, 0)</code> = <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can stones with equal weights cause repeats?",
                     "Putting the first 3 in A and the second in B gives the same a as the opposite choice. Equal subset sums are exactly what memo exploits."],
                    ["Could I limit a to half the total?",
                     "Not in this recursion, because A may become the heavier group. The table versions use half by choosing A as the lighter group."],
                    ["Is memo or a table better in practice?",
                     "The table: stones ≤ 30 and weights ≤ 100 make the state count tiny, and loops avoid recursion overhead."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> instead of minimising directly, ask which weights the lighter group A can have. That is Partition Equal Subset Sum's reachability table, up to <code>total // 2</code>.",
                    "<code>can[i][a]</code> is True when some subset of the first i stones weighs exactly a.",
                    "The best split uses the largest reachable a, giving the answer <code>total - 2 * best</code>.",
                ],
                "steps": [
                    "<code>half = total // 2</code>; create <code>can</code> of size (n + 1) × (half + 1) with only <code>can[0][0] = True</code>.",
                    "For row i with <code>x = stones[i - 1]</code> and every a from 0 to half:",
                    "<code>can[i][a] = can[i - 1][a] or (x &lt;= a and can[i - 1][a - x])</code>.",
                    "<code>best = max(a for a in range(half + 1) if can[n][a])</code>; a = 0 is always reachable.",
                    "Return <code>total - 2 * best</code>.",
                ],
                "why": [
                    "Any split can be named by its lighter group, which weighs at most half, so the largest reachable a ≤ half gives the smallest difference.",
                    "Each row only reads the row above, so each stone is used at most once.",
                    "(n + 1)·(half + 1) cells: <strong>O(n·T)</strong> time and <strong>O(n·T)</strong> space.",
                ],
                "dry": [
                    [
                        "total = 14, half = 7. Row 0: {0}.",
                        "Row 1 (3): {0, 3}. Row 2 (5): {0, 3, 5}; 8 is above half and not tracked.",
                        "Row 3 (6): {0, 3, 5, 6}; 7 would need 1, which is not reachable.",
                        "best = 6, so the result is 14 − 12 = <strong>2</strong>.",
                    ],
                    [
                        "total = 6, half = 3. Row 1 (3): {0, 3}.",
                        "Row 2 (3): still {0, 3}.",
                        "best = 3 = half, a perfect split.",
                        "The result is 6 − 6 = <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only up to <code>total // 2</code>?",
                     "If A weighs more than half, swap the names of A and B. The lighter group always weighs at most half, so larger sums add nothing."],
                    ["How is this related to Partition Equal Subset Sum?",
                     "Same table. Partition asks whether half itself is reachable; here you ask how close to half you can get. The answer is 0 exactly when Partition says True."],
                    ["Why is <code>max(...)</code> always defined?",
                     "<code>can[n][0]</code> is True (the empty group), so the generator has at least one value."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> only the previous row <code>prev</code> and the current row <code>cur</code> are kept.",
                    "Row i reads only row i - 1, so all older rows can be dropped.",
                    "<code>cur = prev[:]</code> covers \"stone goes to B\" for every weight at once.",
                ],
                "steps": [
                    "<code>half = total // 2</code>; <code>prev = [True] + [False] * half</code>.",
                    "For each stone <code>x</code>: <code>cur = prev[:]</code>.",
                    "For a from x to half: <code>cur[a] = prev[a] or prev[a - x]</code>.",
                    "<code>prev = cur</code>.",
                    "<code>best</code> is the largest a with <code>prev[a]</code> True; return <code>total - 2 * best</code>.",
                ],
                "why": [
                    "Reads come only from <code>prev</code>, so each row equals the 2-D table's row.",
                    "Same work: <strong>O(n·T)</strong> time.",
                    "Two rows of half + 1 booleans: <strong>O(T)</strong> space.",
                ],
                "dry": [
                    [
                        "prev = {0}.",
                        "3 → {0, 3}. 5 → {0, 3, 5}. 6 → {0, 3, 5, 6}.",
                        "best = 6.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "prev = {0}.",
                        "3 → {0, 3}. The second 3 would add 6, which is above half = 3.",
                        "best = 3.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the inner loop start at x?",
                     "For a &lt; x the stone cannot be in A, so <code>cur[a]</code> keeps the copied value."],
                    ["Can I stop early when <code>cur[half]</code> becomes True?",
                     "Yes: best can never beat half, so the answer would be <code>total - 2 * half</code>, which is 0 or 1. The given code just finishes the loop."],
                    ["Why not keep a Python set of reachable weights?",
                     "That works too, and is easy to read, but the fixed-size boolean list is faster and has a clear O(T) bound."],
                ],
            },
            "One row, weight downwards": {
                "idea": [
                    "<strong>What changed:</strong> one boolean row <code>can</code> is updated in place, with a from <code>half</code> down to x.",
                    "<code>can[a]</code> reads <code>can[a - x]</code>, a smaller weight that has not been updated yet this round, so each stone is used at most once, as in 0/1 knapsack.",
                    "This is Partition Equal Subset Sum asking \"how close to half?\" instead of \"exactly half?\".",
                ],
                "steps": [
                    "<code>half = total // 2</code>; <code>can = [True] + [False] * half</code>.",
                    "For each stone <code>x</code>, loop <code>a</code> over <code>range(half, x - 1, -1)</code>.",
                    "If <code>can[a - x]</code>, set <code>can[a] = True</code>.",
                    "Afterwards, <code>best</code> = the largest a with <code>can[a]</code> True.",
                    "Return <code>total - 2 * best</code>.",
                ],
                "why": [
                    "The downward order keeps <code>can[a - x]</code> at its value before stone x, so the single row matches the two-row version exactly.",
                    "The time is <strong>O(n·T)</strong>.",
                    "One row of half + 1 booleans and no copies: <strong>O(T)</strong> space.",
                ],
                "dry": [
                    [
                        "half = 7, can = {0}.",
                        "x = 3: a = 3 from can[0] → {0, 3}.",
                        "x = 5: a = 7 needs can[2], a = 6 needs can[1], both False; a = 5 from can[0] → {0, 3, 5}.",
                        "x = 6: a = 7 needs can[1] (False); a = 6 from can[0] → {0, 3, 5, 6}.",
                        "best = 6, so the result is 14 − 12 = <strong>2</strong>.",
                    ],
                    [
                        "half = 3, can = {0}.",
                        "x = 3: a = 3 from can[0] → {0, 3}.",
                        "x = 3: a = 3 is already True; nothing changes.",
                        "best = 3, so the result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong with an upward loop?",
                     "A stone could join A several times. With [3, 5, 6], upwards x = 3 marks 3 and then 6 from can[3], pretending two 3s exist."],
                    ["Is <code>total - 2 * best</code> ever negative?",
                     "No. best ≤ half = total // 2, so 2·best ≤ total."],
                    ["Why can a single stone give a non-zero answer?",
                     "With [1], half is 0, best is 0, and the stone itself is left over: the answer is 1."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ ones and zeroes
    "ones-and-zeroes": {
        "examples": [
            {"call": 'find_max_form(["10", "0", "1"], 1, 1)', "expect": "2"},
            {"call": 'find_max_form(["111", "0"], 2, 2)', "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "This is 0/1 knapsack with <strong>two capacities</strong>: each string costs some zeros and some ones, and every string is worth exactly 1.",
                    "<code>f(i, z, o)</code> = the most strings you can pick from the first <code>i</code> with at most <code>z</code> zeros and <code>o</code> ones left.",
                    "String i is either left, or taken when both of its costs fit: <code>max(f(i-1, z, o), 1 + f(i-1, z - cz, o - co))</code>.",
                ],
                "steps": [
                    "Precompute <code>cost</code>: the pair (zeros, ones) for every string.",
                    "Base case: <code>f(0, z, o) = 0</code>.",
                    "Start with \"leave it\": <code>best = f(i - 1, z, o)</code>.",
                    "If <code>cz &lt;= z and co &lt;= o</code>, try <code>1 + f(i - 1, z - cz, o - co)</code> and keep the larger.",
                    "Return <code>f(len(strs), m, n)</code>.",
                ],
                "why": [
                    "Each subset of strings is one path of take/leave choices; subsets that break either limit are cut off by the double check, so the maximum is over exactly the valid subsets.",
                    "Two branches per string, L levels: <strong>O(2<sup>L</sup>)</strong> time.",
                    "The call stack is L deep: <strong>O(L)</strong> space.",
                    "Different subsets often use the same number of zeros and ones, so states repeat; memo is the next rung.",
                ],
                "dry": [
                    [
                        "Costs: \"10\" = (1, 1), \"0\" = (1, 0), \"1\" = (0, 1); m = n = 1.",
                        "Leave \"1\" → <code>f(2, 1, 1)</code>: leaving \"0\" gives <code>f(1, 1, 1)</code> = 1 (take \"10\"); taking \"0\" gives 1 + <code>f(1, 0, 1)</code> = 1. So 1.",
                        "Take \"1\" → 1 + <code>f(2, 1, 0)</code>: \"0\" still fits, so <code>f(2, 1, 0)</code> = 1 + <code>f(1, 0, 0)</code> = 1.",
                        "<code>f(3, 1, 1)</code> = max(1, 1 + 1) = 2, after 12 calls.",
                        "\"0\" and \"1\" together beat \"10\" alone: <strong>2</strong>.",
                    ],
                    [
                        "Costs: \"111\" = (0, 3), \"0\" = (1, 0); m = n = 2.",
                        "Leave \"0\" → <code>f(1, 2, 2)</code>: \"111\" needs 3 ones &gt; 2, so only leave: 0.",
                        "Take \"0\" → 1 + <code>f(1, 1, 2)</code> = 1 + 0.",
                        "Plenty of zeros cannot pay for ones: <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not take the cheapest strings first?",
                     "\"Cheapest\" is ambiguous with two budgets. With [\"11\", \"010\", \"001\", \"01\"], m = 3, n = 2, shortest-first may take \"11\" and spend both ones, ending with 1 string, while \"01\" + \"010\" gives 2."],
                    ["Why must both <code>cz &lt;= z</code> and <code>co &lt;= o</code> hold?",
                     "The limits are separate: spare zeros cannot pay for ones. Example 2 has 2 zeros and 2 ones, yet \"111\" never fits."],
                    ["What are L, m and n?",
                     "L is the number of strings, m the zero budget and n the one budget. They become the three table dimensions later."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> is added on <code>f</code>; the three-part state <code>(i, z, o)</code> is the cache key.",
                    "The best from a state depends only on which strings are left and how much of each budget remains, not on how you got there.",
                    "There are at most (L + 1)·(m + 1)·(n + 1) states, so the exponential tree becomes polynomial.",
                ],
                "steps": [
                    "Precompute <code>cost</code> as before.",
                    "Wrap <code>f(i, z, o)</code> in <code>@cache</code>.",
                    "Base case <code>i == 0</code> → 0; otherwise \"leave\", then \"take\" if both costs fit.",
                    "Repeated states are answered from the cache.",
                    "Return <code>f(len(strs), m, n)</code>.",
                ],
                "why": [
                    "<code>f</code> depends only on its arguments, so cached values equal recomputed ones.",
                    "Each state does O(1) work once: <strong>O(L·m·n)</strong> time.",
                    "The cache holds <strong>O(L·m·n)</strong> entries, plus an O(L) stack.",
                ],
                "dry": [
                    [
                        "<code>f(3, 1, 1)</code> → <code>f(2, 1, 1)</code> → <code>f(1, 1, 1)</code> computes <code>f(0, 1, 1)</code> and <code>f(0, 0, 0)</code>.",
                        "Later, <code>f(2, 1, 0)</code> takes \"0\" and reaches <code>f(1, 0, 0)</code>, which asks for <code>f(0, 0, 0)</code>: a cache hit.",
                        "11 distinct states, 1 hit.",
                        "<code>f(3, 1, 1)</code> = <strong>2</strong>.",
                    ],
                    [
                        "<code>f(2, 2, 2)</code> → <code>f(1, 2, 2)</code> → <code>f(0, 2, 2)</code> = 0; \"111\" never fits.",
                        "Take \"0\" → <code>f(1, 1, 2)</code> → <code>f(0, 1, 2)</code> = 0.",
                        "5 distinct states, no repeats.",
                        "The result is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Is a 3-part cache key a problem?",
                     "No. <code>@cache</code> hashes the whole argument tuple; it just means more possible states (L·m·n) than in one-capacity knapsack."],
                    ["How big can the state space get?",
                     "With 600 strings and m = n = 100 it is about 6 million states, which is heavy for a dictionary cache; the table versions handle that more comfortably."],
                    ["Why not count zeros inside <code>f</code>?",
                     "That would recount characters on every call. Counting once into <code>cost</code> keeps each state O(1)."],
                ],
            },
            "Bottom-up 3-D table": {
                "idea": [
                    "<strong>What changed:</strong> the states are filled in loops: layer i is a full (m + 1) × (n + 1) grid built from layer i - 1.",
                    "<code>dp[i][z][o]</code> reads only layer i - 1, at the same budgets and at the smaller <code>(z - cz, o - co)</code>, so layer by layer is a valid order.",
                    "No recursion, so no stack-depth concerns.",
                ],
                "steps": [
                    "Precompute <code>cost</code>; create <code>dp</code> of size (L + 1) × (m + 1) × (n + 1), all 0.",
                    "For each layer <code>i</code>, read <code>cz, co = cost[i - 1]</code>.",
                    "For every <code>z</code> in 0..m and <code>o</code> in 0..n, copy \"leave\": <code>dp[i][z][o] = dp[i - 1][z][o]</code>.",
                    "If both costs fit, improve with <code>1 + dp[i - 1][z - cz][o - co]</code>.",
                    "Return <code>dp[L][m][n]</code>.",
                ],
                "why": [
                    "It is the memo recurrence in a fixed order; layer i - 1 is complete before layer i reads it, and reading layer i - 1 keeps each string to one use.",
                    "(L + 1)(m + 1)(n + 1) cells with O(1) work: <strong>O(L·m·n)</strong> time.",
                    "All layers are stored: <strong>O(L·m·n)</strong> space.",
                ],
                "dry": [
                    [
                        "Layer 0 is all 0 (grids written as rows z = 0, z = 1).",
                        "Layer 1 (\"10\"): only (1, 1) fits, so [[0, 0], [0, 1]].",
                        "Layer 2 (\"0\"): (1, 0) becomes 1; (1, 1) = max(1, 1 + dp[1][0][1] = 1) = 1. Grid [[0, 0], [1, 1]].",
                        "Layer 3 (\"1\"): (0, 1) becomes 1; (1, 1) = max(1, 1 + dp[2][1][0] = 2) = 2. Grid [[0, 1], [1, 2]].",
                        "dp[3][1][1] = <strong>2</strong>.",
                    ],
                    [
                        "Layer 1 (\"111\"): co = 3 &gt; every o, so the layer is a copy of zeros.",
                        "Layer 2 (\"0\"): every cell with z ≥ 1 becomes 1 + 0 = 1.",
                        "Layer 2 = [[0, 0, 0], [1, 1, 1], [1, 1, 1]].",
                        "dp[2][2][2] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why three dimensions?",
                     "One for how many strings have been considered, and one for each budget. Knapsack with k budgets needs k + 1 dimensions in the full table."],
                    ["Does the order of the z and o loops matter here?",
                     "No. Layer i reads only layer i - 1, which is finished, so any order within a layer gives the same values."],
                    ["Is this table practical?",
                     "Only for small inputs: 600 × 101 × 101 integers is about 6 million cells. It is the clearest version, then you shrink it."],
                ],
            },
            "Two layers": {
                "idea": [
                    "<strong>What changed:</strong> only the previous 2-D layer <code>prev</code> and the current <code>cur</code> are kept, so the string dimension vanishes from memory.",
                    "Layer i reads nothing older than layer i - 1.",
                    "Copying <code>prev</code> row by row into <code>cur</code> handles \"leave the string\" everywhere.",
                ],
                "steps": [
                    "<code>prev</code> = an (m + 1) × (n + 1) grid of zeros.",
                    "For each string, count <code>cz</code> zeros and <code>co = len(s) - cz</code> ones.",
                    "<code>cur = [row[:] for row in prev]</code>: a deep copy, so rows are not shared.",
                    "For z from cz to m and o from co to n: <code>cur[z][o] = max(prev[z][o], 1 + prev[z - cz][o - co])</code>.",
                    "<code>prev = cur</code>; return <code>prev[m][n]</code>.",
                ],
                "why": [
                    "All reads come from <code>prev</code>, so each <code>cur</code> equals the corresponding layer of the 3-D table.",
                    "Same work: <strong>O(L·m·n)</strong> time.",
                    "Two grids: <strong>O(m·n)</strong> space.",
                    "Starting the loops at <code>cz</code> and <code>co</code> drops the fit test.",
                ],
                "dry": [
                    [
                        "prev = [[0, 0], [0, 1]] after \"10\".",
                        "\"0\" (1, 0): cur[1][0] = 1 + prev[0][0] = 1; cur[1][1] = max(1, 1 + prev[0][1]) = 1.",
                        "\"1\" (0, 1): cur[0][1] = 1; cur[1][1] = max(1, 1 + prev[1][0] = 2) = 2.",
                        "prev[1][1] = <strong>2</strong>.",
                    ],
                    [
                        "\"111\": <code>range(3, 3)</code> is empty, so cur is just the copied zeros.",
                        "\"0\": z runs 1..2 and o runs 0..2; each cell becomes 1 + prev[z - 1][o] = 1.",
                        "prev[2][2] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>[row[:] for row in prev]</code> and not <code>prev[:]</code>?",
                     "<code>prev[:]</code> copies only the outer list; the inner rows would be shared, so writing <code>cur[z][o]</code> would also change <code>prev</code>."],
                    ["Why compute ones as <code>len(s) - cz</code>?",
                     "The strings contain only '0' and '1', so it saves a second pass over the string."],
                    ["Can I avoid the copy?",
                     "Yes, with the in-place version below, as long as both loops run downwards."],
                ],
            },
            "One layer, both capacities downwards": {
                "idea": [
                    "<strong>What changed:</strong> a single grid <code>dp</code> is updated in place, with both <code>z</code> and <code>o</code> looping downwards.",
                    "Cell (z, o) reads itself and (z - zeros, o - ones), which is no larger in either coordinate. Going down in both, that cell has not been rewritten for this string yet.",
                    "So each string is still used at most once, exactly like the one-row 0/1 knapsack, but in two dimensions.",
                ],
                "steps": [
                    "<code>dp</code> = an (m + 1) × (n + 1) grid of zeros.",
                    "For each string, count <code>zeros</code> and <code>ones</code>.",
                    "Loop <code>z</code> from m down to <code>zeros</code>, and inside it <code>o</code> from n down to <code>ones</code>.",
                    "<code>dp[z][o] = max(dp[z][o], dp[z - zeros][o - ones] + 1)</code>.",
                    "Return <code>dp[m][n]</code>.",
                ],
                "why": [
                    "When (z, o) is written, every cell it reads lies at or below it in both coordinates, which the downward loops have not yet reached for this string, so it holds the previous layer's value.",
                    "The time is still <strong>O(L·m·n)</strong>.",
                    "One grid and no copying: <strong>O(m·n)</strong> space.",
                ],
                "dry": [
                    [
                        "\"10\" (1, 1): only (1, 1) is visited: 0 → 1.",
                        "\"0\" (1, 0): (1, 1) stays 1; (1, 0) becomes 1.",
                        "\"1\" (0, 1): (1, 1) first, reading dp[1][0] = 1 → 2; then (0, 1) → 1.",
                        "dp = [[0, 1], [1, 2]].",
                        "dp[1][1] = <strong>2</strong>.",
                    ],
                    [
                        "\"111\" (0, 3): <code>range(2, 2, -1)</code> for o is empty, nothing changes.",
                        "\"0\" (1, 0): z = 2, 1 and o = 2, 1, 0: every visited cell becomes 1.",
                        "dp = [[0, 0, 0], [1, 1, 1], [1, 1, 1]].",
                        "dp[2][2] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Do both loops really need to go down?",
                     "If either went up, a cell could read a neighbour already updated with this string and take it twice. Downwards in both keeps every read on the old layer."],
                    ["Can the z and o loops be swapped?",
                     "Yes, as long as both still run downwards; each read cell is still unvisited for this string."],
                    ["What does the upward-loop bug look like here?",
                     "It counts one string many times: with upward loops, [\"0\"] with m = 3 and n = 0 reports 3 strings instead of 1."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ coin change
    "coin-change": {
        "examples": [
            {"call": "coin_change([1, 3, 4], 6)", "expect": "2"},
            {"call": "coin_change([2], 3)", "expect": "-1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "This is the <strong>unbounded</strong> knapsack: each coin type can be used any number of times, and you minimise the number of coins.",
                    "<code>f(i, a)</code> = the fewest coins from the first <code>i</code> types that make amount <code>a</code>. Either stop using type i (<code>f(i - 1, a)</code>) or use one more of it (<code>1 + f(i, a - c)</code>).",
                    "Using a coin keeps <code>i</code> the same, which is exactly what lets it be used again; that is the one change from 0/1 knapsack.",
                ],
                "steps": [
                    "Base cases: <code>a == 0</code> → 0 coins; <code>i == 0</code> with a &gt; 0 → <code>inf</code> (impossible).",
                    "<code>best = f(i - 1, a)</code>: no more of coin type i.",
                    "If <code>c = coins[i - 1]</code> fits, <code>best = min(best, 1 + f(i, a - c))</code>.",
                    "Call <code>f(len(coins), amount)</code>.",
                    "Convert <code>inf</code> to <code>-1</code> for \"impossible\".",
                ],
                "why": [
                    "Every multiset of coins corresponds to one path (how many of each type, decided type by type), so the minimum over paths is the true minimum.",
                    "The tree's size grows exponentially with the amount and the number of types: <strong>exponential</strong> time.",
                    "The stack can reach k + A/min(coin) frames: <strong>O(k + A)</strong> space.",
                    "Each <code>(i, a)</code> pair is solved many times over; memo is the next rung.",
                ],
                "dry": [
                    [
                        "<code>f(3, 6)</code> = min(<code>f(2, 6)</code>, 1 + <code>f(3, 2)</code>) with coin 4.",
                        "<code>f(2, 6)</code> = min(<code>f(1, 6)</code> = 6, 1 + <code>f(2, 3)</code>); <code>f(2, 3)</code> = min(3, 1 + <code>f(2, 0)</code>) = 1, so 2.",
                        "<code>f(3, 2)</code>: coins 4 and 3 are too big, so only 1s: 2, giving 1 + 2 = 3.",
                        "<code>f(3, 6)</code> = min(2, 3) = 2, after 31 calls.",
                        "3 + 3 beats greedy's 4 + 1 + 1: <strong>2</strong>.",
                    ],
                    [
                        "<code>f(1, 3)</code> = min(<code>f(0, 3)</code> = inf, 1 + <code>f(1, 1)</code>).",
                        "<code>f(1, 1)</code>: coin 2 does not fit and <code>f(0, 1)</code> = inf.",
                        "Everything is inf, so 4 calls end in inf.",
                        "An odd amount from 2s is impossible: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does greedy (biggest coin first) fail?",
                     "On example 1 greedy takes 4, then 1 + 1: three coins, while 3 + 3 uses two. Greedy only works for special coin systems."],
                    ["Why <code>inf</code> instead of -1 inside the recursion?",
                     "<code>min</code> and <code>1 + …</code> handle <code>inf</code> naturally; a -1 would look like the best answer. It is converted only at the end."],
                    ["How is this different from 0/1 knapsack's recursion?",
                     "The \"use it\" branch calls <code>f(i, a - c)</code>, not <code>f(i - 1, …)</code>, so the same coin type stays available."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on <code>f</code>; the recurrence is unchanged.",
                    "Many orders of choosing coins reach the same <code>(i, a)</code>, and the best finish from there is fixed.",
                    "With k types and amount A there are at most (k + 1)·(A + 1) states.",
                ],
                "steps": [
                    "Wrap <code>f(i, a)</code> in <code>@cache</code>.",
                    "Base cases: 0 for <code>a == 0</code>, <code>inf</code> for <code>i == 0</code>.",
                    "Take the min of \"skip type i\" and \"one more coin of type i\".",
                    "Repeated states come from the cache.",
                    "Return the answer, or -1 if it is <code>inf</code>.",
                ],
                "why": [
                    "Caching does not change values, since <code>f</code> depends only on its arguments.",
                    "Each state does O(1) work once: <strong>O(k·A)</strong> time.",
                    "The cache holds <strong>O(k·A)</strong> entries; the recursion depth can reach about A when a coin of 1 exists.",
                ],
                "dry": [
                    [
                        "<code>f(2, 6)</code> → <code>f(1, 6)</code> walks down <code>f(1, 5)</code>, …, <code>f(1, 0)</code>, caching every <code>f(1, a)</code>.",
                        "<code>f(2, 3)</code> asks for <code>f(1, 3)</code>: a hit (3).",
                        "<code>f(2, 2)</code> asks for <code>f(1, 2)</code>: another hit (2).",
                        "19 distinct states, 2 hits. <code>f(3, 6)</code> = <strong>2</strong>.",
                    ],
                    [
                        "<code>f(1, 3)</code>, <code>f(0, 3)</code>, <code>f(1, 1)</code>, <code>f(0, 1)</code>: 4 states, no repeats.",
                        "All are inf.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Can the recursion depth be a problem?",
                     "Yes. With coins [1] and amount 10<sup>4</sup>, <code>f(1, a)</code> calls <code>f(1, a - 1)</code> all the way down and Python raises RecursionError. The table versions avoid this."],
                    ["Why is there no hit count advantage on example 2?",
                     "With one coin type there is only one path, so nothing repeats. Memo pays off with several coin types and larger amounts."],
                    ["Is the state <code>(i, a)</code> necessary, or would <code>a</code> alone work?",
                     "For counting the minimum, <code>a</code> alone works (try every coin as the last one), which is the 1-D version. The <code>(i, a)</code> form is kept here so the ladder matches knapsack."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> states are filled in loops: <code>dp[i][a]</code> for every coin prefix and amount.",
                    "<code>dp[i][a]</code> reads the row above (<code>dp[i - 1][a]</code>, skip the coin) and the <em>same</em> row to the left (<code>dp[i][a - c]</code>, use it again).",
                    "That same-row read is the whole difference from 0/1 knapsack, which only reads the row above. Filling left to right makes it safe.",
                ],
                "steps": [
                    "Create <code>dp</code> of (k + 1) × (amount + 1), all <code>inf</code>, and set column 0 to 0 in every row.",
                    "For row <code>i</code> with coin <code>c = coins[i - 1]</code>, loop <code>a</code> from 1 upwards.",
                    "<code>dp[i][a] = dp[i - 1][a]</code>.",
                    "If <code>c &lt;= a</code>, <code>dp[i][a] = min(dp[i][a], 1 + dp[i][a - c])</code>.",
                    "Return <code>dp[k][amount]</code>, or -1 if it is <code>inf</code>.",
                ],
                "why": [
                    "Row i - 1 is complete, and <code>dp[i][a - c]</code> was filled earlier in the same row, so every read is final.",
                    "(k + 1)(A + 1) cells, O(1) each: <strong>O(k·A)</strong> time and <strong>O(k·A)</strong> space.",
                    "No recursion, so amounts like 10<sup>4</sup> are fine.",
                ],
                "dry": [
                    [
                        "Row 1 (coin 1): [0, 1, 2, 3, 4, 5, 6].",
                        "Row 2 (coin 3): dp[2][3] = 1 + dp[2][0] = 1, dp[2][6] = 1 + dp[2][3] = 2 → [0, 1, 2, 1, 2, 3, 2].",
                        "Row 3 (coin 4): dp[3][4] = 1, dp[3][5] = 2, dp[3][6] = min(2, 1 + dp[3][2] = 3) = 2.",
                        "Row 3 = [0, 1, 2, 1, 1, 2, 2].",
                        "dp[3][6] = <strong>2</strong>.",
                    ],
                    [
                        "Row 1 (coin 2): dp[1][1] = inf, dp[1][2] = 1 + dp[1][0] = 1.",
                        "dp[1][3] = 1 + dp[1][1] = inf.",
                        "Row 1 = [0, inf, 1, inf].",
                        "dp[1][3] is inf, so the result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why read <code>dp[i][a - c]</code> and not <code>dp[i - 1][a - c]</code>?",
                     "The same row already allows coin i, so <code>dp[i][a - c]</code> may already contain some of it; adding one more is what \"unlimited\" means. The row above would allow at most one."],
                    ["Does <code>1 + inf</code> cause trouble?",
                     "No. In Python <code>1 + inf</code> is <code>inf</code>, so impossible amounts stay impossible."],
                    ["Does the order of coins matter?",
                     "No. The minimum over all multisets does not depend on the order in which coin types are introduced."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> only <code>prev</code> (row i - 1) and <code>cur</code> (row i) are kept.",
                    "The recurrence becomes <code>cur[a] = min(prev[a], 1 + cur[a - c])</code>: the reuse read is from <code>cur</code>, the skip read from <code>prev</code>.",
                    "Since <code>cur</code> starts as a copy of <code>prev</code>, <code>prev[a]</code> is just \"cur[a] before it is updated\"; that observation leads to the one-row version.",
                ],
                "steps": [
                    "<code>prev = [0] + [inf] * amount</code>: with no coins, only 0 is makeable.",
                    "For each coin <code>c</code>: <code>cur = prev[:]</code>.",
                    "For a from c upwards: <code>cur[a] = min(prev[a], 1 + cur[a - c])</code>.",
                    "<code>prev = cur</code>.",
                    "Return <code>prev[amount]</code>, or -1 if it is <code>inf</code>.",
                ],
                "why": [
                    "Each <code>cur</code> equals the corresponding row of the 2-D table.",
                    "Same work: <strong>O(k·A)</strong> time.",
                    "Two rows: <strong>O(A)</strong> space.",
                ],
                "dry": [
                    [
                        "prev = [0, inf, …]. Coin 1 → [0, 1, 2, 3, 4, 5, 6].",
                        "Coin 3 → cur[3] = 1, cur[6] = 1 + cur[3] = 2: [0, 1, 2, 1, 2, 3, 2].",
                        "Coin 4 → [0, 1, 2, 1, 1, 2, 2].",
                        "prev[6] = <strong>2</strong>.",
                    ],
                    [
                        "prev = [0, inf, inf, inf].",
                        "Coin 2 → cur[2] = 1, cur[3] = 1 + cur[1] = inf.",
                        "prev[3] is inf: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>cur[a - c]</code> here, when 0/1 knapsack's two-row version used <code>prev[c - w]</code>?",
                     "Reading <code>cur</code> lets the same coin be added again, which this problem allows. That single change switches from 0/1 to unbounded."],
                    ["Is the copy <code>cur = prev[:]</code> needed?",
                     "It fills amounts below c, which the loop does not touch, and makes <code>cur[a - c]</code> well defined at the start."],
                    ["Why is this rung often skipped in practice?",
                     "Because <code>prev[a]</code> equals the not-yet-updated <code>cur[a]</code>, so one row is enough, as shown next."],
                ],
            },
            "One row, amount upwards": {
                "idea": [
                    "<strong>What changed:</strong> a single row <code>dp</code>, updated in place with amounts going <em>upwards</em>.",
                    "When <code>dp[a]</code> is updated, its old value is the \"skip\" option, and <code>dp[a - c]</code> has already been updated with coin c, which is the \"use it again\" option.",
                    "It is the mirror image of 0/1 knapsack, which loops downwards precisely to forbid that reuse.",
                ],
                "steps": [
                    "<code>dp = [0] + [inf] * amount</code>.",
                    "For each coin <code>c</code>, loop <code>a</code> from c up to amount.",
                    "<code>dp[a] = min(dp[a], 1 + dp[a - c])</code>.",
                    "Return <code>dp[amount]</code>, or -1 if it is <code>inf</code>.",
                ],
                "why": [
                    "Upwards order makes <code>dp[a - c]</code> equal to the same-row value of the 2-D table, and the old <code>dp[a]</code> equals the row-above value, so the update matches the recurrence.",
                    "One pass per coin over the amounts: <strong>O(k·A)</strong> time.",
                    "One row: <strong>O(A)</strong> space.",
                    "This is the version most interviewers expect.",
                ],
                "dry": [
                    [
                        "After coin 1: dp = [0, 1, 2, 3, 4, 5, 6].",
                        "Coin 3: dp[3] = 1, dp[4] = 2, dp[5] = 3, then dp[6] = 1 + dp[3] = 2, using the 3 that was just placed.",
                        "Coin 4: dp[4] = 1, dp[5] = 1 + dp[1] = 2, dp[6] = min(2, 1 + dp[2] = 3) = 2.",
                        "dp = [0, 1, 2, 1, 1, 2, 2].",
                        "dp[6] = <strong>2</strong>.",
                    ],
                    [
                        "dp = [0, inf, inf, inf]; coin 2.",
                        "a = 2: 1 + dp[0] = 1. a = 3: 1 + dp[1] = inf.",
                        "dp[3] stays inf: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["What if I looped downwards here?",
                     "Each coin could then be used at most once, turning this into 0/1 knapsack. On example 1 no subset of {1, 3, 4} sums to 6, so it would wrongly return -1 instead of 2."],
                    ["Can I put amounts in the outer loop and coins inside?",
                     "Yes, for the minimum it does not matter: <code>dp[a] = min over c of 1 + dp[a - c]</code> gives the same values. Order only matters for counting (Coin Change II)."],
                    ["Why is <code>inf</code> safer than a large number like amount + 1?",
                     "Both work; amount + 1 is a common trick in other languages. <code>inf</code> just reads more clearly in Python."],
                ],
            },
            "BFS over amounts": {
                "idea": [
                    "Treat each amount from 0 to <code>amount</code> as a node, and adding one coin as an edge. The fewest coins is the shortest path from 0 to the target.",
                    "All edges have weight 1, so breadth-first search finds that shortest path level by level.",
                    "BFS stops as soon as the target is reached, often long before visiting every amount.",
                ],
                "steps": [
                    "If <code>amount == 0</code>, return 0.",
                    "Start with <code>queue = deque([(0, 0)])</code> (value, steps) and <code>seen = {0}</code>.",
                    "Pop <code>(value, steps)</code>; for each coin, <code>nxt = value + c</code>.",
                    "If <code>nxt == amount</code>, return <code>steps + 1</code>; if <code>nxt &lt; amount</code> and unseen, mark it and enqueue it.",
                    "If the queue empties, return -1.",
                ],
                "why": [
                    "BFS dequeues values in order of steps, so the first time the target is produced, it is with the fewest coins.",
                    "Each amount is enqueued at most once and tries k coins: <strong>O(k·A)</strong> time in the worst case.",
                    "<code>seen</code> and the queue hold at most A values: <strong>O(A)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop (0, 0): enqueue 1, 3, 4 at step 1.",
                        "Pop (1, 1): 2 and 5 are new; 4 is already seen. Queue [(3, 1), (4, 1), (2, 2), (5, 2)].",
                        "Pop (3, 1): 3 + 1 = 4 is seen; 3 + 3 = 6 is the amount.",
                        "Return 1 + 1 = <strong>2</strong>.",
                    ],
                    [
                        "Pop (0, 0): enqueue 2.",
                        "Pop (2, 1): 2 + 2 = 4 is past 3, ignored.",
                        "The queue is empty: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>nxt == amount</code> before enqueuing?",
                     "It returns one level earlier than checking at pop time, and the answer is the same because BFS levels are already in order."],
                    ["Why mark <code>seen</code> when enqueuing, not when popping?",
                     "Marking at enqueue stops the same amount being added to the queue several times at the same level."],
                    ["When is BFS better than the DP row?",
                     "When the answer is a small number of coins, because BFS stops at that level. When the target is unreachable, it explores everything, just like the DP."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ coin change II
    "coin-change-ii": {
        "examples": [
            {"call": "change(5, [1, 2, 5])", "expect": "4"},
            {"call": "change(3, [2])", "expect": "0"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Count <em>combinations</em>, not orderings: 1 + 2 and 2 + 1 are the same way.",
                    "Consider the coin types one at a time, deciding how many of each to use, so every combination is built in exactly one order.",
                    "<code>f(i, a)</code> = <code>f(i - 1, a)</code> (no more coins of type i) + <code>f(i, a - c)</code> (one more coin of type i).",
                ],
                "steps": [
                    "Base cases: <code>a == 0</code> → 1 (the empty combination); <code>i == 0</code> with a &gt; 0 → 0.",
                    "<code>c = coins[i - 1]</code>; <code>ways = f(i - 1, a)</code>.",
                    "If <code>c &lt;= a</code>, add <code>f(i, a - c)</code>; staying at i allows more of the same coin.",
                    "Return <code>ways</code>; the answer is <code>f(len(coins), amount)</code>.",
                ],
                "why": [
                    "Every combination is a unique count of each coin type, which is a unique path, so each is counted exactly once and never in two orders.",
                    "The number of paths grows exponentially with the amount: <strong>exponential</strong> time.",
                    "The stack depth is up to k + A/min(coin): <strong>O(k + A)</strong> space.",
                    "The same <code>(i, a)</code> is recounted along different paths; memo removes that.",
                ],
                "dry": [
                    [
                        "<code>f(3, 5)</code> = <code>f(2, 5)</code> + <code>f(3, 0)</code>; <code>f(3, 0)</code> = 1 is the combination {5}.",
                        "<code>f(2, 5)</code> = <code>f(1, 5)</code> + <code>f(2, 3)</code> = 1 + 2.",
                        "<code>f(1, 5)</code> = 1 is five 1s; <code>f(2, 3)</code> = 2 counts {2, 1} and {1, 1, 1}, each joined to the 2 already used.",
                        "26 calls in total.",
                        "{5}, {2, 2, 1}, {2, 1, 1, 1}, {1, 1, 1, 1, 1}: <strong>4</strong>.",
                    ],
                    [
                        "<code>f(1, 3)</code> = <code>f(0, 3)</code> + <code>f(1, 1)</code>.",
                        "<code>f(0, 3)</code> = 0; <code>f(1, 1)</code> = <code>f(0, 1)</code> = 0 since 2 &gt; 1.",
                        "No combination of 2s makes 3: <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does this not count 1 + 2 and 2 + 1 twice?",
                     "Coin types are decided in a fixed order: once you move from type i to i - 1 you never come back. So each combination has one canonical path."],
                    ["Why is <code>f(·, 0) = 1</code> and not 0?",
                     "It counts the one way to make 0: use no more coins. Every complete combination ends there, so it must count 1."],
                    ["How is this different from Coin Change I?",
                     "Same states and branches, but <code>+</code> replaces <code>min</code> and the base values change: 1 and 0 instead of 0 and inf."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on <code>f</code>.",
                    "The number of ways from <code>(i, a)</code> does not depend on the coins already chosen, so repeated states share one count.",
                    "At most (k + 1)·(A + 1) states.",
                ],
                "steps": [
                    "Wrap <code>f(i, a)</code> in <code>@cache</code>.",
                    "Base cases: 1 for <code>a == 0</code>, 0 for <code>i == 0</code>.",
                    "<code>ways = f(i - 1, a)</code>, plus <code>f(i, a - c)</code> if the coin fits.",
                    "Return <code>f(len(coins), amount)</code>.",
                ],
                "why": [
                    "<code>f</code> depends only on its arguments, so caching keeps every count correct.",
                    "Each state does O(1) work once: <strong>O(k·A)</strong> time.",
                    "The cache holds <strong>O(k·A)</strong> counts, with a stack up to about A deep.",
                ],
                "dry": [
                    [
                        "<code>f(2, 5)</code> → <code>f(1, 5)</code> walks down to <code>f(1, 0)</code>, caching every <code>f(1, a)</code> as 1.",
                        "<code>f(2, 5)</code> → <code>f(2, 3)</code> asks for <code>f(1, 3)</code>: a hit.",
                        "<code>f(2, 1)</code> asks for <code>f(1, 1)</code>: another hit.",
                        "16 distinct states. <code>f(3, 5)</code> = 3 + 1 = <strong>4</strong>.",
                    ],
                    [
                        "<code>f(1, 3)</code> = <code>f(0, 3)</code> + <code>f(1, 1)</code>; <code>f(0, 3)</code> = 0 is cached.",
                        "<code>f(1, 1)</code> cannot use the 2, so it is <code>f(0, 1)</code> = 0, also cached.",
                        "4 states, no repeats, so memo saves nothing on a single coin type.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Can the counts overflow?",
                     "Not in Python, whose integers are unbounded. In other languages the problem guarantees the answer fits a 32-bit integer."],
                    ["Is recursion depth a concern?",
                     "With a coin of 1 and a large amount, <code>f(1, a)</code> recurses a levels deep, so yes; the table versions avoid it."],
                    ["Why are only 2 hits on example 1?",
                     "Small amounts give few repeats. The savings grow quickly with the amount and the number of coin types."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<strong>What changed:</strong> the counts are filled in loops.",
                    "<code>dp[i][a]</code> = the row above (no coin i) + the same row to the left at <code>a - c</code> (one more coin i), exactly like Coin Change with <code>+</code> for <code>min</code>.",
                    "Column 0 is 1 in every row: there is one way to make 0.",
                ],
                "steps": [
                    "Create <code>dp</code> of (k + 1) × (amount + 1) zeros; set <code>dp[i][0] = 1</code> for all rows.",
                    "For row <code>i</code> with coin <code>c</code>, loop <code>a</code> from 1 upwards.",
                    "<code>dp[i][a] = dp[i - 1][a] + (dp[i][a - c] if c &lt;= a else 0)</code>.",
                    "Return <code>dp[k][amount]</code>.",
                ],
                "why": [
                    "The row above is complete and the same-row cell to the left was filled earlier, so every read is final.",
                    "(k + 1)(A + 1) cells: <strong>O(k·A)</strong> time and <strong>O(k·A)</strong> space.",
                    "Rows correspond to coin types, so each combination is counted in coin order only once.",
                ],
                "dry": [
                    [
                        "Row 1 (coin 1): [1, 1, 1, 1, 1, 1].",
                        "Row 2 (coin 2): dp[2][a] = dp[1][a] + dp[2][a - 2] → [1, 1, 2, 2, 3, 3].",
                        "Row 3 (coin 5): only a = 5 changes: 3 + dp[3][0] = 4.",
                        "dp[3][5] = <strong>4</strong>.",
                    ],
                    [
                        "Row 1 (coin 2): dp[1][1] = 0, dp[1][2] = 0 + dp[1][0] = 1.",
                        "dp[1][3] = 0 + dp[1][1] = 0.",
                        "dp[1][3] = <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the same row for <code>a - c</code>?",
                     "The same row still allows coin i, so a combination can contain several of it. The row above would limit it to one."],
                    ["What if the amount is 0?",
                     "The loop does nothing and <code>dp[k][0] = 1</code>: the empty combination."],
                    ["Can I reorder the coins?",
                     "Yes. The final count is the same for any order of rows; only the intermediate rows differ."],
                ],
            },
            "Two rows": {
                "idea": [
                    "<strong>What changed:</strong> only <code>prev</code> and <code>cur</code> are kept.",
                    "<code>cur[a] = prev[a] + cur[a - c]</code>: skip the coin (row above) or add one more (same row).",
                    "Copying <code>prev</code> into <code>cur</code> first fills the amounts below c, which cannot use the coin.",
                ],
                "steps": [
                    "<code>prev = [1] + [0] * amount</code>.",
                    "For each coin <code>c</code>: <code>cur = prev[:]</code>.",
                    "For a from c upwards: <code>cur[a] = prev[a] + cur[a - c]</code>.",
                    "<code>prev = cur</code>; return <code>prev[amount]</code>.",
                ],
                "why": [
                    "Each <code>cur</code> equals a row of the 2-D table.",
                    "Same work: <strong>O(k·A)</strong> time.",
                    "Two rows: <strong>O(A)</strong> space.",
                    "As in Coin Change, <code>prev[a]</code> is just <code>cur[a]</code> before its update, which makes one row enough.",
                ],
                "dry": [
                    [
                        "prev = [1, 0, 0, 0, 0, 0]. Coin 1 → [1, 1, 1, 1, 1, 1].",
                        "Coin 2 → [1, 1, 2, 2, 3, 3].",
                        "Coin 5 → cur[5] = 3 + cur[0] = 4.",
                        "prev[5] = <strong>4</strong>.",
                    ],
                    [
                        "prev = [1, 0, 0, 0].",
                        "Coin 2 → cur[2] = 0 + 1 = 1, cur[3] = 0 + cur[1] = 0.",
                        "prev[3] = <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>cur[a - c]</code> and not <code>prev[a - c]</code>?",
                     "<code>prev[a - c]</code> would allow each coin type at most once, a different problem. <code>cur</code> already allows more of coin c."],
                    ["Why start with <code>[1] + [0] * amount</code>?",
                     "With no coins only amount 0 can be made, in exactly one way."],
                    ["Is the copy needed?",
                     "Yes, for <code>cur[0..c-1]</code>; the inner loop starts at c."],
                ],
            },
            "One row, coins outer, amount upwards": {
                "idea": [
                    "<strong>What changed:</strong> a single row <code>ways</code>, updated in place: the old <code>ways[a]</code> is the \"skip\" count and the updated <code>ways[a - c]</code> is the \"one more coin c\" count.",
                    "Coins are in the <strong>outer</strong> loop, so while coin c is processed, the row only contains combinations made of earlier coins plus c. Each combination is built in coin order once.",
                    "Swapping the loops (amount outside, coins inside) counts 1 + 2 and 2 + 1 separately; that is Combination Sum IV, a different problem.",
                ],
                "steps": [
                    "<code>ways = [1] + [0] * amount</code>.",
                    "For each coin <code>c</code>, loop <code>a</code> from c up to amount.",
                    "<code>ways[a] += ways[a - c]</code>.",
                    "Return <code>ways[amount]</code>.",
                ],
                "why": [
                    "Upwards makes <code>ways[a - c]</code> include coin c already, allowing repeats; the old <code>ways[a]</code> is the row above, so the update matches the recurrence.",
                    "One pass per coin: <strong>O(k·A)</strong> time.",
                    "One row: <strong>O(A)</strong> space.",
                ],
                "dry": [
                    [
                        "ways = [1, 0, 0, 0, 0, 0].",
                        "Coin 1: each ways[a] += ways[a - 1] → [1, 1, 1, 1, 1, 1].",
                        "Coin 2: ways[2] = 2, ways[3] = 2, ways[4] = 1 + ways[2] = 3, ways[5] = 1 + ways[3] = 3.",
                        "Coin 5: ways[5] = 3 + ways[0] = 4.",
                        "The result is <strong>4</strong>.",
                    ],
                    [
                        "ways = [1, 0, 0, 0]; coin 2.",
                        "a = 2: += ways[0] → 1. a = 3: += ways[1] = 0.",
                        "ways = [1, 0, 1, 0], so the result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["What exactly happens if I swap the loops?",
                     "Orderings are counted: on example 1 the swapped loops give 9 instead of 4, because 1 + 2 + 2, 2 + 1 + 2 and 2 + 2 + 1 are all counted."],
                    ["Why does the loop go upwards, unlike 0/1 knapsack?",
                     "Coins are unlimited, so <code>ways[a - c]</code> should already include coin c. Downwards would allow each coin at most once."],
                    ["Why is Coin Change I fine with either loop order but this one is not?",
                     "A minimum is the same whichever order the coins are considered in; a count is not, because counting orderings and counting combinations give different numbers."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ perfect squares
    "perfect-squares": {
        "examples": [
            {"call": "num_squares(12)", "expect": "3"},
            {"call": "num_squares(7)", "expect": "4"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "This is Coin Change where the coins are the squares 1, 4, 9, …: find the fewest squares that sum to n.",
                    "Choose the last square k² used: <code>f(a) = 1 + min over k of f(a - k²)</code>, for every k with k² ≤ a.",
                    "Greedy (largest square first) fails: 12 = 9 + 1 + 1 + 1 uses four squares, while 4 + 4 + 4 uses three.",
                ],
                "steps": [
                    "Base case: <code>f(0) = 0</code>.",
                    "Start with <code>best = inf</code> and <code>k = 1</code>.",
                    "While <code>k * k &lt;= a</code>: <code>best = min(best, 1 + f(a - k * k))</code>, then <code>k += 1</code>.",
                    "Return <code>best</code>; the answer is <code>f(n)</code>.",
                ],
                "why": [
                    "Any representation has some last square; trying every possible last square and the best way to make the rest covers every representation.",
                    "Each call branches √a ways, and f(a − 1) alone gives a chain n deep: <strong>exponential</strong> time.",
                    "The deepest chain subtracts 1 each time: <strong>O(n)</strong> stack space.",
                    "Only n + 1 distinct values of a exist, so almost every call is a repeat; memo is the fix.",
                ],
                "dry": [
                    [
                        "<code>f(12)</code> tries <code>f(11)</code>, <code>f(8)</code> and <code>f(3)</code>.",
                        "<code>f(11)</code> = 3 (9 + 1 + 1), <code>f(8)</code> = 2 (4 + 4), <code>f(3)</code> = 3 (1 + 1 + 1).",
                        "<code>f(12)</code> = 1 + min(3, 2, 3) = 3.",
                        "That takes 104 calls for only 13 distinct values of a.",
                        "4 + 4 + 4: <strong>3</strong>.",
                    ],
                    [
                        "<code>f(7)</code> tries <code>f(6)</code> and <code>f(3)</code>.",
                        "<code>f(6)</code> = 3 (4 + 1 + 1) and <code>f(3)</code> = 3.",
                        "<code>f(7)</code> = 1 + 3 = 4, after 18 calls.",
                        "4 + 1 + 1 + 1: <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does greedy fail?",
                     "Taking 9 from 12 leaves 3, which needs three 1s. Skipping the biggest square (4 + 4 + 4) is better, so every square must be tried."],
                    ["Why is there no coin index in the state, unlike Coin Change?",
                     "Here only the minimum count matters, so trying every square as the last one is enough; order does not matter for a minimum."],
                    ["Can <code>best</code> stay <code>inf</code>?",
                     "No. For a ≥ 1 the square 1 always fits, so at least one branch returns a finite value."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "<strong>What changed:</strong> <code>@cache</code> on <code>f</code>.",
                    "<code>f(a)</code> depends only on a, so there are just n + 1 states, each trying about √a squares.",
                    "The first descent through k = 1 fills <code>f(n - 1)</code>, <code>f(n - 2)</code>, …, so every later branch is a cache hit.",
                ],
                "steps": [
                    "Wrap <code>f(a)</code> in <code>@cache</code>.",
                    "<code>f(0) = 0</code>.",
                    "Loop k while <code>k * k &lt;= a</code>, keeping <code>min(best, 1 + f(a - k * k))</code>.",
                    "Return <code>f(n)</code>.",
                ],
                "why": [
                    "Caching cannot change a value that depends only on a.",
                    "n states with up to √n squares each: <strong>O(n√n)</strong> time.",
                    "The cache and the recursion depth are both <strong>O(n)</strong>.",
                ],
                "dry": [
                    [
                        "<code>f(12)</code> → <code>f(11)</code> → … → <code>f(0)</code> via k = 1, filling the cache on the way back.",
                        "Then each other branch (f(8) from 12, f(3) from 12, …) is a cache hit.",
                        "13 states, 13 hits.",
                        "<code>f(12)</code> = 1 + min(3, 2, 3) = <strong>3</strong>.",
                    ],
                    [
                        "<code>f(7)</code> → <code>f(6)</code> → … → <code>f(0)</code> fills 8 states.",
                        "The k = 2 branches (f(3) from 7, f(2) from 6, …) are 4 hits.",
                        "<code>f(7)</code> = 1 + min(f(6), f(3)) = 1 + 3 = <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Will this hit Python's recursion limit?",
                     "Yes for large n: the k = 1 chain is n deep, so n = 2000 already raises RecursionError with the default limit of 1000. Use the table."],
                    ["Why is the cost n√n and not n²?",
                     "Each a only tries squares up to a, and there are about √a of them."],
                    ["Does the cache carry over between calls of <code>num_squares</code>?",
                     "No; <code>f</code> is created fresh inside each call. Caching across calls would make repeated queries faster."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "<strong>What changed:</strong> <code>dp[a]</code> is filled for a = 1..n in increasing order, without recursion.",
                    "<code>dp[a]</code> reads <code>dp[a - 1]</code>, <code>dp[a - 4]</code>, … as far back as a itself, so there is no fixed window and the array cannot be shrunk.",
                    "The squares are listed once up front, so the inner loop just walks a short list.",
                ],
                "steps": [
                    "<code>squares = [k * k for k in range(1, isqrt(n) + 1)]</code>.",
                    "<code>dp = [0] + [inf] * n</code>.",
                    "For each a from 1 to n, loop over <code>squares</code>, stopping (<code>break</code>) once <code>s &gt; a</code>.",
                    "If <code>dp[a - s] + 1 &lt; dp[a]</code>, set <code>dp[a] = dp[a - s] + 1</code>.",
                    "Return <code>dp[n]</code>.",
                ],
                "why": [
                    "Every <code>dp[a - s]</code> is smaller than a, so it is final when read; by induction each <code>dp[a]</code> is the true minimum.",
                    "n amounts × at most √n squares: <strong>O(n√n)</strong> time.",
                    "The table is <strong>O(n)</strong> space, with no recursion limit.",
                ],
                "dry": [
                    [
                        "squares = [1, 4, 9].",
                        "dp[1..8] = 1, 2, 3, 1, 2, 3, 4, 2; dp[9] = 1.",
                        "dp[10] = 2, dp[11] = 3.",
                        "dp[12]: s = 1 → dp[11] + 1 = 4; s = 4 → dp[8] + 1 = 3; s = 9 → dp[3] + 1 = 4.",
                        "dp[12] = <strong>3</strong>.",
                    ],
                    [
                        "squares = [1, 4].",
                        "dp = [0, 1, 2, 3, 1, 2, 3, …].",
                        "dp[7]: s = 1 → dp[6] + 1 = 4; s = 4 → dp[3] + 1 = 4.",
                        "dp[7] = <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>break</code> instead of <code>continue</code> when <code>s &gt; a</code>?",
                     "<code>squares</code> is increasing, so every later square is also too big."],
                    ["Can I loop squares outside and amounts inside, like Coin Change?",
                     "Yes, the minimum is the same in either order. The given order keeps each <code>dp[a]</code> final right after its inner loop."],
                    ["Why is a BFS from n also common here?",
                     "The answer is at most 4, so BFS finishes within four levels; the tests use exactly that as the brute-force check."],
                ],
            },
            "Lagrange's four-square theorem": {
                "idea": [
                    "Lagrange: every positive integer is a sum of at most four squares, so the answer is always 1, 2, 3 or 4.",
                    "Legendre: n needs all four exactly when n = 4<sup>a</sup>(8b + 7).",
                    "So: 1 if n is a square, 2 if n − a² is a square for some a, 4 if n has the special form, and 3 otherwise.",
                ],
                "steps": [
                    "If <code>isqrt(n) ** 2 == n</code>, return 1.",
                    "For a from 1 to <code>isqrt(n)</code>: if <code>rest = n - a * a</code> is a perfect square, return 2.",
                    "Strip factors of 4: <code>while m % 4 == 0: m //= 4</code>.",
                    "Return 4 if <code>m % 8 == 7</code>, otherwise 3.",
                ],
                "why": [
                    "The two theorems cover every case, and the checks for 1 and 2 are direct searches, so the answer is exact.",
                    "The two-square search takes √n steps and stripping 4s is O(log n): <strong>O(√n)</strong> time.",
                    "Only a few integers are kept: <strong>O(1)</strong> space.",
                    "It is a great follow-up once the DP is written, but the DP is what interviewers want to see derived.",
                ],
                "dry": [
                    [
                        "isqrt(12) = 3 and 9 ≠ 12, so not 1.",
                        "12 − 1 = 11, 12 − 4 = 8, 12 − 9 = 3: none is a square, so not 2.",
                        "m = 12 → 3 after one division by 4; 3 % 8 = 3.",
                        "Not of the form 4<sup>a</sup>(8b + 7): <strong>3</strong>.",
                    ],
                    [
                        "isqrt(7) = 2 and 4 ≠ 7, so not 1.",
                        "7 − 1 = 6 and 7 − 4 = 3 are not squares, so not 2.",
                        "7 is not divisible by 4, and 7 % 8 = 7.",
                        "The special form: <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why use <code>isqrt</code> instead of <code>int(n ** 0.5)</code>?",
                     "<code>isqrt</code> is exact for any integer size, while floating-point square roots can be off by one for large n."],
                    ["Why must the factors of 4 be stripped first?",
                     "28 = 4 · 7 needs four squares, but 28 % 8 = 4. Only after dividing out the 4 does the 7 (mod 8) show."],
                    ["Should I lead with this in an interview?",
                     "Mention it as a follow-up. It relies on theorems you are not expected to prove on the spot, so the DP comes first."],
                ],
            },
        },
    },
}
