"""Write-ups for Dynamic Programming, part 2: the knapsack family."""

EXPLAIN = {
    # ------------------------------------------------------------------ 0/1 knapsack
    "knapsack-01": {
        "example": {"call": "knapsack(7, [1, 4, 5, 7], [1, 3, 4, 5])", "expect": "9"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Decide items one at a time: item i is either left out, or taken if it fits.",
                    "<code>f(i, c)</code> = the best value from the first i items with capacity c = max(leave it, value + f(i-1, c - weight)).",
                ],
                "steps": [
                    "<code>f(0, c) = 0</code>.",
                    "Try leaving the item; if it fits, also try taking it.",
                ],
                "why": [
                    "Every subset of items is tried: O(2<sup>n</sup>) time, with recursion depth n.",
                ],
                "dry": [
                    "Items (weight, value): (1, 1), (3, 4), (4, 5), (5, 7); capacity 7.",
                    "The tree tries all 16 take/leave patterns that fit.",
                    "The best is to take (3, 4) and (4, 5): weight 7, value <strong>9</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Different early choices can leave the same remaining capacity, and from there the best finish is identical.",
                    "Cache each <code>(i, c)</code>, so it is solved once.",
                ],
                "steps": [
                    "Same recursion with <code>@cache</code>.",
                ],
                "why": [
                    "It is O(n·W) states at most, and only the states actually reached are computed.",
                ],
                "dry": [
                    "Taking item 1 and leaving item 2, or the reverse, can both lead to the same (i, c), which is then computed once.",
                    "f(4, 7) = max(f(3, 7), 7 + f(3, 2)) = max(9, 7 + 1) = <strong>9</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>dp[i][c]</code> = the best value using the first i items with capacity c.",
                    "Row i reads only row i-1, at the same or a smaller capacity, so fill row by row.",
                    "The full table also lets you walk back from <code>dp[n][W]</code> to see which items were taken.",
                ],
                "steps": [
                    "<code>dp[i][c] = dp[i-1][c]</code>, then also try <code>v + dp[i-1][c - w]</code> if it fits.",
                ],
                "why": [
                    "It is O(n·W) time and space.",
                ],
                "dry": [
                    "After item (1, 1): row [0, 1, 1, 1, 1, 1, 1, 1].",
                    "After (3, 4): [0, 1, 1, 4, 5, 5, 5, 5]. After (4, 5): [0, 1, 1, 4, 5, 6, 6, 9].",
                    "After (5, 7): [0, 1, 1, 4, 5, 7, 8, 9]. dp[4][7] = <strong>9</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Rows older than i-1 are never read again, so keep only the previous row and the current one.",
                    "Starting <code>cur</code> as a copy of <code>prev</code> fills in \"leave the item\" for every capacity at once.",
                ],
                "steps": [
                    "<code>cur = prev[:]</code>; for c from w to W: <code>cur[c] = max(prev[c], v + prev[c - w])</code>.",
                ],
                "why": [
                    "It is O(n·W) time and O(W) space.",
                ],
                "dry": [
                    "The same four rows as the 2-D table, but only two exist at any moment.",
                    "The final row ends in <strong>9</strong>.",
                ],
            },
            "One row, capacity downwards": {
                "idea": [
                    "Cell c reads the previous row at c and at c - w, the same capacity and a smaller one.",
                    "Update capacities from high to low: when <code>dp[c]</code> is updated, <code>dp[c - w]</code> has not been touched this round, so it still holds the previous row.",
                    "Going upwards instead would let the same item be taken twice. That is unbounded knapsack, and the most common bug in this pattern.",
                ],
                "steps": [
                    "For each item, for c from W down to w: <code>dp[c] = max(dp[c], v + dp[c - w])</code>.",
                ],
                "why": [
                    "It is O(n·W) time and O(W) space, with no copying.",
                ],
                "dry": [
                    "Item (3, 4) downwards: dp[7] = max(1, 4 + dp[4] = 5), dp[6], dp[5], dp[4] = 5, dp[3] = 4.",
                    "Item (4, 5): dp[7] = max(5, 5 + dp[3] = 4 + 5) = 9.",
                    "Item (5, 7) cannot improve dp[7]. The result is <strong>9</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ partition equal subset sum
    "partition-equal-subset-sum": {
        "example": {"call": "can_partition([1, 5, 11, 5])", "expect": "True"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Two equal halves exist exactly when some subset sums to half of the total; an odd total is impossible.",
                    "<code>can(i, s)</code>: can the first i numbers make s? Either use number i (if it fits) or skip it.",
                ],
                "steps": [
                    "Reject an odd total; <code>can(n, total // 2)</code>.",
                    "Return early as soon as one branch succeeds.",
                ],
                "why": [
                    "It tries every subset: O(2<sup>n</sup>).",
                ],
                "dry": [
                    "The total is 22, so half is 11.",
                    "Using the last 5: can(3, 6) uses 1 and 5, reaching 0.",
                    "{1, 5, 5} makes 11, so the result is <strong>True</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Many subsets of the first numbers leave the same remaining sum; cache each <code>(i, s)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on <code>can</code>.",
                ],
                "why": [
                    "It is O(n·S) for S = half the total.",
                ],
                "dry": [
                    "can(4, 11) → can(3, 6) → can(2, 1) → can(1, 0) is True.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Row i marks every sum reachable with the first i numbers; sum 0 is always reachable.",
                    "<code>dp[i][s] = dp[i-1][s] or dp[i-1][s - x]</code>.",
                ],
                "steps": [
                    "Fill row by row; return <code>dp[n][half]</code>.",
                ],
                "why": [
                    "It is O(n·S) time and space.",
                ],
                "dry": [
                    "Reachable sums: after 1: {0, 1}; after 5: {0, 1, 5, 6}; after 11: {0, 1, 5, 6, 11}.",
                    "After the second 5: {0, 1, 5, 6, 10, 11}. 11 is reachable: <strong>True</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only the previous row of reachable sums and the current one.",
                ],
                "steps": [
                    "<code>cur = prev[:]</code> (skip the number), then add <code>prev[s - x]</code> (use it).",
                ],
                "why": [
                    "It is O(n·S) time and O(S) space.",
                ],
                "dry": [
                    "The same reachable sets as the table, one row at a time.",
                    "The final row has 11, so the result is <strong>True</strong>.",
                ],
            },
            "One row, sum downwards": {
                "idea": [
                    "A single boolean row, updated from high sums to low, so each number is used at most once.",
                    "Stop as soon as the half becomes reachable.",
                ],
                "steps": [
                    "For each x, for s from half down to x: if <code>can[s - x]</code>, set <code>can[s]</code>.",
                ],
                "why": [
                    "Updating upwards would let one number be reused, so [1] would reach every sum.",
                    "It is O(n·S) time and O(S) space.",
                ],
                "dry": [
                    "After 1: {0, 1}. After 5: {0, 1, 5, 6}.",
                    "After 11: 11 is reachable (from 0 + 11), so return early.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Bitset of reachable sums": {
                "idea": [
                    "Store the one-row table as the bits of one big integer: bit s is on when sum s is reachable.",
                    "Adding a number x is <code>bits |= bits &lt;&lt; x</code>: every reachable sum also becomes reachable plus x.",
                ],
                "steps": [
                    "<code>bits = 1</code>; shift and OR for each number.",
                    "Test the bit at half.",
                ],
                "why": [
                    "The shift reads the old value, so each number is used once, and it processes a whole machine word of sums per step.",
                ],
                "dry": [
                    "After 1: bits {0, 1}. After 5: {0, 1, 5, 6}. After 11: {0, 1, 5, 6, 11, 12, 16, 17}.",
                    "After 5: {0, 1, 5, 6, 10, 11, 12, 16, 17, 21, 22}.",
                    "Bit 11 is on, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ target sum
    "target-sum": {
        "example": {"call": "find_target_sum_ways([1, 1, 1, 1, 1], 3)", "expect": "5"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Each number gets a + or a -: count the sign patterns whose total equals the target.",
                    "<code>count(i, s)</code> = count(i-1, s - x) + count(i-1, s + x).",
                ],
                "steps": [
                    "<code>count(0, s)</code> is 1 if s == 0, otherwise 0.",
                ],
                "why": [
                    "All 2<sup>n</sup> sign patterns are tried.",
                ],
                "dry": [
                    "There are 2<sup>5</sup> = 32 sign patterns.",
                    "Those with four + and one - total 3, and there are 5 of them.",
                    "The result is <strong>5</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Many sign patterns on the first numbers land on the same partial sum; cache <code>(i, s)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on <code>count</code>.",
                ],
                "why": [
                    "It is O(n·T) states for a sum range T.",
                ],
                "dry": [
                    "Every count(i, s) depends only on how many 1s are left and the sum still needed, so few distinct states appear.",
                    "The result is <strong>5</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "Columns cover the sums -T..T, shifted by T so the indices are non-negative.",
                    "<code>dp[i][s]</code> pulls from s - x and s + x in the row above.",
                ],
                "steps": [
                    "<code>dp[0][T] = 1</code> (sum 0); return 0 if |target| &gt; T.",
                ],
                "why": [
                    "It is O(n·T) time and space.",
                ],
                "dry": [
                    "Each row holds binomial counts: after k ones, sum s is reached C(k, (k + s)/2) ways.",
                    "Row 5 at sum 3 is C(5, 4) = <strong>5</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only the previous row.",
                    "One row is not enough here: cell s reads both s - x and s + x, and either loop direction would overwrite one of them first.",
                ],
                "steps": [
                    "Build each new row from the previous one.",
                ],
                "why": [
                    "It is O(n·T) time and O(T) space.",
                ],
                "dry": [
                    "Row values climb through the binomial counts.",
                    "The final value at sum 3 is <strong>5</strong>.",
                ],
            },
            "Reduce to subset count, one row": {
                "idea": [
                    "Let P be the sum of the + group and N the sum of the - group. Then P - N = target and P + N = T, so P = (T + target) / 2.",
                    "So count the subsets that sum to P, which is a 0/1-knapsack count. If T + target is odd or |target| &gt; T, the answer is 0.",
                    "That recurrence reads only the same and smaller sums, so one row updated downwards is safe.",
                ],
                "steps": [
                    "<code>ways = [1, 0, …, 0]</code> of length P + 1.",
                    "For each x, for s from P down to x: <code>ways[s] += ways[s - x]</code>.",
                ],
                "why": [
                    "It is O(n·P) time and O(P) space. Zeros double the count automatically, matching +0 and -0.",
                ],
                "dry": [
                    "T = 5, target = 3, so P = 4.",
                    "ways after each 1: [1, 1, 0, 0, 0] → [1, 2, 1, 0, 0] → [1, 3, 3, 1, 0] → [1, 4, 6, 4, 1] → [1, 5, 10, 10, 5].",
                    "ways[4] = <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ last stone weight II
    "last-stone-weight-ii": {
        "example": {"call": "last_stone_weight_ii([2, 7, 4, 1, 8, 1])", "expect": "1"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Smashing stones always ends with the difference between two groups: some stones count as +, the others as -.",
                    "So split the stones into groups A and B to make |A - B| as small as possible.",
                    "Try every split: each stone joins A or B.",
                ],
                "steps": [
                    "<code>f(i, a)</code>: at the end, return <code>|total - 2a|</code>; otherwise take the min of both choices.",
                ],
                "why": [
                    "Every split is tried: O(2<sup>n</sup>).",
                ],
                "dry": [
                    "The total is 23, so the best is a group weighing as close to 11.5 as possible.",
                    "A = {2, 1, 8} = 11 against B = 12.",
                    "|23 - 22| = <strong>1</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Many splits of the first stones give the same weight for A; cache <code>(i, a)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n·T).",
                ],
                "dry": [
                    "States like (3, 6) are reached by several splits but solved once.",
                    "The result is <strong>1</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "This is Partition's reachability table, up to <code>total // 2</code>: <code>can[i][a]</code> says whether some subset of the first i stones weighs a.",
                    "The answer uses the largest reachable a, since A can always be the lighter group.",
                ],
                "steps": [
                    "Fill the table; <code>best = max reachable a</code>; return <code>total - 2·best</code>.",
                ],
                "why": [
                    "It is O(n·T) time and space.",
                ],
                "dry": [
                    "With these stones, every weight from 0 to 11 is reachable.",
                    "best = 11, so the result is 23 - 22 = <strong>1</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep only the previous row of reachable weights.",
                ],
                "steps": [
                    "<code>cur = prev[:]</code>; add <code>prev[a - x]</code>.",
                ],
                "why": [
                    "It is O(n·T) time and O(T) space.",
                ],
                "dry": [
                    "The final row reaches 11, so the result is <strong>1</strong>.",
                ],
            },
            "One row, weight downwards": {
                "idea": [
                    "A single boolean row, updated downwards, as in 0/1 knapsack, so each stone is used once.",
                ],
                "steps": [
                    "For each stone x, for a from half down to x: <code>can[a] |= can[a - x]</code>.",
                ],
                "why": [
                    "It is O(n·T) time and O(T) space: Partition Equal Subset Sum asking \"how close?\" instead of \"exactly?\".",
                ],
                "dry": [
                    "After 2: {0, 2}. After 7: {0, 2, 7, 9}. After 4: adds 4, 6, 11.",
                    "Then 1, 8 and 1 fill in the rest of 0..11.",
                    "best = 11, so the result is <strong>1</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ ones and zeroes
    "ones-and-zeroes": {
        "example": {"call": 'find_max_form(["10", "0001", "111001", "1", "0"], 5, 3)', "expect": "4"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "This is 0/1 knapsack with two capacities: each string costs some zeros and some ones, and is worth 1.",
                    "<code>f(i, z, o)</code> = max(leave string i, 1 + f(i-1, z - zeros, o - ones) if it fits).",
                ],
                "steps": [
                    "Precompute each string's (zeros, ones) cost; recurse.",
                ],
                "why": [
                    "It tries every subset: O(2<sup>L</sup>).",
                ],
                "dry": [
                    "Costs (zeros, ones): (1, 1), (3, 1), (2, 4), (0, 1), (1, 0).",
                    "\"111001\" needs 4 ones but only 3 are allowed, so it is never taken.",
                    "The other four fit together: 5 zeros and 3 ones. The result is <strong>4</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache the three-part state <code>(i, z, o)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(L·m·n).",
                ],
                "dry": [
                    "Each (i, z, o) is solved once.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "Bottom-up 3-D table": {
                "idea": [
                    "Layer i (a whole 2-D table over zeros and ones) reads only layer i-1, at the same or smaller capacities.",
                ],
                "steps": [
                    "<code>dp[i][z][o] = max(dp[i-1][z][o], 1 + dp[i-1][z-cz][o-co])</code>.",
                ],
                "why": [
                    "It is O(L·m·n) time and space.",
                ],
                "dry": [
                    "The corner dp[i][5][3] after each string: 1, 2, 2, 3, 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "Two layers": {
                "idea": [
                    "Keep only the previous 2-D layer; the string dimension disappears from memory.",
                ],
                "steps": [
                    "<code>cur</code> copies <code>prev</code>, then takes the string where it fits.",
                ],
                "why": [
                    "It is O(L·m·n) time and O(m·n) space.",
                ],
                "dry": [
                    "The same corner values: 1, 2, 2, 3, 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "One layer, both capacities downwards": {
                "idea": [
                    "Cell (z, o) reads itself and (z - zeros, o - ones), which is smaller in both coordinates.",
                    "Loop both capacities downwards so that smaller cell still holds the previous layer, and each string is used once.",
                ],
                "steps": [
                    "For each string, for z down from m and o down from n: <code>dp[z][o] = max(dp[z][o], dp[z - zeros][o - ones] + 1)</code>.",
                ],
                "why": [
                    "It is O(L·m·n) time, O(m·n) space, and no copy per string.",
                ],
                "dry": [
                    "\"10\" makes dp[5][3] = 1, and \"0001\" makes it 2.",
                    "\"111001\" does not fit (4 ones &gt; 3). \"1\" makes it 3, and \"0\" makes it 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ coin change
    "coin-change": {
        "example": {"call": "coin_change([1, 2, 5], 11)", "expect": "3"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Consider the coin types one by one: <code>f(i, a)</code> = min(skip coin type i, 1 + f(i, a - c)).",
                    "Using coin c keeps i the same, because coins are unlimited.",
                ],
                "steps": [
                    "<code>f(·, 0) = 0</code>; <code>f(0, a) = ∞</code> for a &gt; 0.",
                ],
                "why": [
                    "It tries every multiset of coins: exponential in the amount.",
                ],
                "dry": [
                    "The search eventually finds 5 + 5 + 1, after exploring many 1-and-2 combinations.",
                    "The fewest coins is <strong>3</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, a)</code>, giving k·A states.",
                ],
                "steps": [
                    "<code>@cache</code>; an amount of 10<sup>4</sup> with a 1-coin recurses 10<sup>4</sup> deep, so prefer the table.",
                ],
                "why": [
                    "It is O(k·A).",
                ],
                "dry": [
                    "f(3, 11) = min(f(2, 11), 1 + f(3, 6)); f(3, 6) = 1 + f(3, 1) = 2.",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>dp[i][a]</code> reads the row above (skip the coin) and the same row to the left (use it again).",
                    "That same-row read is the difference from 0/1 knapsack, which reads only the row above.",
                ],
                "steps": [
                    "Fill left to right; <code>dp[i][a] = min(dp[i-1][a], 1 + dp[i][a - c])</code>.",
                ],
                "why": [
                    "It is O(k·A) time and space.",
                ],
                "dry": [
                    "Row 1 (coin 1): dp[a] = a.",
                    "Row 2 (coins 1, 2): 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6.",
                    "Row 3 (all coins): 0, 1, 1, 2, 2, 1, 2, 2, 3, 3, 2, 3. dp[11] = <strong>3</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep the previous row and the current one; <code>cur[a] = min(prev[a], 1 + cur[a - c])</code>.",
                    "Notice that <code>prev[a]</code> is just \"cur[a] before it is updated\". That leads to the one-row version.",
                ],
                "steps": [
                    "<code>cur = prev[:]</code>, then a left-to-right update.",
                ],
                "why": [
                    "It is O(k·A) time and O(A) space.",
                ],
                "dry": [
                    "The same rows as the table.",
                    "The final cell is <strong>3</strong>.",
                ],
            },
            "One row, amount upwards": {
                "idea": [
                    "A single row updated <em>upwards</em>: <code>dp[a - c]</code> may already include coin c, so the coin can be reused, which is exactly right here.",
                    "It is the mirror image of 0/1 knapsack, which loops downwards to forbid reuse.",
                    "Greedy is wrong: with coins [1, 3, 4] and amount 6, greedy takes 4 + 1 + 1 but 3 + 3 is better.",
                ],
                "steps": [
                    "For each coin, for a from c up to the amount: <code>dp[a] = min(dp[a], 1 + dp[a - c])</code>.",
                ],
                "why": [
                    "It is O(k·A) time and O(A) space.",
                ],
                "dry": [
                    "After coin 1: dp[a] = a.",
                    "After coin 2: dp[11] = 6. After coin 5: dp[5] = 1, dp[10] = 2, dp[11] = 1 + dp[6] = 1 + 2 = 3.",
                    "The result is <strong>3</strong>: 5 + 5 + 1.",
                ],
            },
            "BFS over amounts": {
                "idea": [
                    "Treat amounts as nodes and each coin as an edge; the fewest coins is the shortest path from 0 to the amount.",
                    "BFS stops at the answer's level, which is often early.",
                ],
                "steps": [
                    "Queue (value, steps); try each coin; return when the amount is hit; skip seen values.",
                ],
                "why": [
                    "It has the same worst case as the table, O(k·A).",
                ],
                "dry": [
                    "Level 1: 1, 2, 5. Level 2: 3, 4, 6, 7, 10.",
                    "Level 3: from 6, adding 5 hits 11.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ coin change II
    "coin-change-ii": {
        "example": {"call": "change(5, [1, 2, 5])", "expect": "4"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Count <em>combinations</em>, not orderings: consider coin types one at a time, so each combination is built in one order.",
                    "<code>f(i, a)</code> = f(i-1, a) (no more of coin i) + f(i, a - c) (one more coin i).",
                ],
                "steps": [
                    "<code>f(·, 0) = 1</code>; <code>f(0, a &gt; 0) = 0</code>.",
                ],
                "why": [
                    "It enumerates combinations one path at a time: exponential.",
                ],
                "dry": [
                    "The combinations for 5 are: 5; 2 + 2 + 1; 2 + 1 + 1 + 1; 1 + 1 + 1 + 1 + 1.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>(i, a)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(k·A).",
                ],
                "dry": [
                    "f(3, 5) = f(2, 5) + f(3, 0) = 3 + 1 = <strong>4</strong>.",
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "<code>dp[i][a]</code> = the row above plus the same row to the left, as in Coin Change.",
                ],
                "steps": [
                    "<code>dp[i][0] = 1</code>.",
                ],
                "why": [
                    "It is O(k·A) time and space.",
                ],
                "dry": [
                    "Coin 1: [1, 1, 1, 1, 1, 1].",
                    "Coins 1, 2: [1, 1, 2, 2, 3, 3]. All coins: [1, 1, 2, 2, 3, 4].",
                    "dp[3][5] = <strong>4</strong>.",
                ],
            },
            "Two rows": {
                "idea": [
                    "Keep the previous row: <code>cur[a] = prev[a] + cur[a - c]</code>.",
                ],
                "steps": [
                    "<code>cur = prev[:]</code>, then a left-to-right update.",
                ],
                "why": [
                    "It is O(k·A) time and O(A) space.",
                ],
                "dry": [
                    "The same rows as above, ending at <strong>4</strong>.",
                ],
            },
            "One row, coins outer, amount upwards": {
                "idea": [
                    "Coins go in the outer loop, so while coin c is processed, the row only holds ways built from earlier coins: each combination is counted once, in coin order.",
                    "Swapping the loops (amount outside, coins inside) counts 1 + 2 and 2 + 1 separately; that is Combination Sum IV, a different problem.",
                ],
                "steps": [
                    "<code>ways = [1, 0, …]</code>; for each coin, for a upwards: <code>ways[a] += ways[a - c]</code>.",
                ],
                "why": [
                    "It is O(k·A) time and O(A) space.",
                ],
                "dry": [
                    "After coin 1: [1, 1, 1, 1, 1, 1].",
                    "After coin 2: [1, 1, 2, 2, 3, 3]. After coin 5: ways[5] = 3 + ways[0] = 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ perfect squares
    "perfect-squares": {
        "example": {"call": "num_squares(12)", "expect": "3"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Choose the last square k² used: <code>f(a) = 1 + min over k of f(a - k²)</code>.",
                ],
                "steps": [
                    "<code>f(0) = 0</code>; try every k with k² ≤ a.",
                ],
                "why": [
                    "It branches once per square at every level: exponential.",
                ],
                "dry": [
                    "f(12) tries 12 - 1, 12 - 4, 12 - 9.",
                    "12 - 4 = 8 = 4 + 4 needs 2 squares, so f(12) = 3.",
                    "The result is <strong>3</strong>: 4 + 4 + 4.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>f(a)</code>, giving n states with √n work each.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n√n), with recursion up to n deep.",
                ],
                "dry": [
                    "f(8) = 2, f(11) = 3, f(3) = 3.",
                    "f(12) = 1 + min(f(11), f(8), f(3)) = 1 + 2 = <strong>3</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "Fill <code>dp[a]</code> for every a from 1 to n.",
                    "dp[a] reads dp[a - 1], dp[a - 4], … as far back as a itself, so there is no fixed window and the array cannot shrink.",
                ],
                "steps": [
                    "<code>dp[a] = min(dp[a - s] + 1)</code> over squares s ≤ a.",
                ],
                "why": [
                    "It is O(n√n) time and O(n) space.",
                ],
                "dry": [
                    "dp = [0, 1, 2, 3, 1, 2, 3, 4, 2, 1, 2, 3, 3].",
                    "dp[12] = <strong>3</strong>.",
                ],
            },
            "Lagrange's four-square theorem": {
                "idea": [
                    "Every positive integer is a sum of at most four squares, and needs all four exactly when n = 4<sup>a</sup>(8b + 7).",
                    "So the answer is 1 if n is a square, 2 if it is a sum of two squares, 4 if it has that special form, and 3 otherwise.",
                ],
                "steps": [
                    "Check for a perfect square; then check every a² for a square remainder; then test the 4<sup>a</sup>(8b + 7) form.",
                ],
                "why": [
                    "It is O(√n) time and O(1) space, a great follow-up once the DP is written.",
                ],
                "dry": [
                    "12 is not a square.",
                    "12 - 1 = 11, 12 - 4 = 8 and 12 - 9 = 3 are not squares, so the answer is not 2.",
                    "12 / 4 = 3, and 3 % 8 ≠ 7, so the result is <strong>3</strong>.",
                ],
            },
        },
    },
}
