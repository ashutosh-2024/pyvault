"""Write-ups for Dynamic Programming, part 1: foundations and linear DP."""

EXPLAIN = {
    # ------------------------------------------------------------------ nth fibonacci
    "nth-fibonacci": {
        "example": {"call": "fib(6)", "expect": "8"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Translate the definition directly: F(n) = F(n-1) + F(n-2), with F(0) = 0 and F(1) = 1.",
                    "Each call makes two more calls, and the same arguments are recomputed again and again in different branches.",
                ],
                "steps": [
                    "If <code>n &lt; 2</code>, return n.",
                    "Otherwise return <code>fib(n - 1) + fib(n - 2)</code>.",
                ],
                "why": [
                    "It is correct, but the call tree grows by about 1.6× per level: O(φ<sup>n</sup>) time.",
                    "Only one root-to-leaf path is on the stack at a time, so the space is O(n).",
                ],
                "dry": [
                    "fib(6) calls fib(5) and fib(4); fib(5) calls fib(4) again, and fib(3) appears three times.",
                    "In total there are 25 calls, and fib(2) alone is computed 5 times.",
                    "The leaves add up to <strong>8</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "There are only n + 1 distinct arguments, so remember each answer the first time it is computed.",
                    "Every repeated call becomes a dictionary lookup instead of a whole subtree.",
                ],
                "steps": [
                    "Wrap the recursion in <code>@cache</code>.",
                ],
                "why": [
                    "Each state does O(1) work: O(n) time, with an O(n) cache and an O(n) stack (CPython stops at about 1000 frames).",
                ],
                "dry": [
                    "f(6) → f(5) → f(4) → f(3) → f(2) → f(1) and f(0) are each computed once on the way down.",
                    "On the way back, every second call (f(i - 2)) is a cache hit.",
                    "7 states are computed, and f(6) = <strong>8</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "Fill <code>dp[i]</code> from the smallest i upwards, so dp[i-1] and dp[i-2] are always ready.",
                    "The base cases become the first two cells of the table.",
                ],
                "steps": [
                    "<code>dp[0] = 0</code>, <code>dp[1] = 1</code>.",
                    "For i from 2 to n: <code>dp[i] = dp[i-1] + dp[i-2]</code>.",
                ],
                "why": [
                    "There is no recursion at all: O(n) time and O(n) space.",
                ],
                "dry": [
                    "dp = [0, 1, 1, 2, 3, 5, 8].",
                    "dp[6] = <strong>8</strong>.",
                ],
            },
            "Two variables": {
                "idea": [
                    "Once dp[i] is known, dp[i-2] is never read again, so keep only the last two values.",
                    "<code>a</code> holds F(i) and <code>b</code> holds F(i+1); each step slides the pair one place right.",
                ],
                "steps": [
                    "<code>a, b = 0, 1</code>.",
                    "Repeat n times: <code>a, b = b, a + b</code>. Return <code>a</code>.",
                ],
                "why": [
                    "It is O(n) time and O(1) space. Look for this in every 1-D DP: see how far back each step reads, and keep only that much.",
                ],
                "dry": [
                    "(a, b) goes (0, 1) → (1, 1) → (1, 2) → (2, 3) → (3, 5) → (5, 8) → (8, 13).",
                    "After 6 steps, a = <strong>8</strong>.",
                ],
            },
            "Fast doubling": {
                "idea": [
                    "Two identities jump from k to 2k: F(2k) = F(k)·(2F(k+1) - F(k)) and F(2k+1) = F(k)² + F(k+1)².",
                    "Halve n at every step, which needs only log n levels.",
                ],
                "steps": [
                    "<code>pair(k)</code> returns (F(k), F(k+1)) from <code>pair(k // 2)</code>.",
                    "For odd k, shift one step: return <code>(d, c + d)</code>.",
                ],
                "why": [
                    "It is O(log n), the answer to \"can you beat O(n)?\" (matrix power without the matrices).",
                ],
                "dry": [
                    "pair(0) = (0, 1). pair(1): c = 0, d = 1; k is odd, so (1, 1) = (F1, F2).",
                    "pair(3): from (1, 1), c = 1·(2 - 1) = 1, d = 1 + 1 = 2; odd, so (2, 3) = (F3, F4).",
                    "pair(6): from (2, 3), c = 2·(6 - 2) = 8, d = 4 + 9 = 13; even, so (8, 13).",
                    "F(6) = <strong>8</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ climbing stairs
    "climbing-stairs": {
        "example": {"call": "climb_stairs(5)", "expect": "8"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Look at the last move: you reached step i either from step i-1 (a 1-step) or from step i-2 (a 2-step).",
                    "So ways(i) = ways(i-1) + ways(i-2), with ways(0) = ways(1) = 1. Standing still is one way to climb zero stairs.",
                ],
                "steps": [
                    "<code>f(i)</code>: 1 if <code>i &lt;= 1</code>, otherwise <code>f(i-1) + f(i-2)</code>.",
                ],
                "why": [
                    "Every distinct climb ends with exactly one of the two last moves, so nothing is double counted.",
                    "The call tree doubles at each level: exponential time.",
                ],
                "dry": [
                    "f(5) = f(4) + f(3); f(4) = f(3) + f(2), so f(3) is computed twice already.",
                    "In total there are 15 calls.",
                    "The result is <strong>8</strong>.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "The same recursion, with each <code>f(i)</code> cached after its first computation.",
                ],
                "steps": [
                    "Decorate <code>f</code> with <code>@cache</code>.",
                ],
                "why": [
                    "Each of the n + 1 states is computed once: O(n) time, O(n) space for the cache and the stack.",
                ],
                "dry": [
                    "f(5) descends to f(1) and f(0), computing f(2) = 2, f(3) = 3, f(4) = 5 on the way back.",
                    "Each f(i - 2) is a cache hit, so f(5) = 5 + 3 = <strong>8</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "Fill <code>dp[i]</code> = ways to reach step i, from the bottom up.",
                ],
                "steps": [
                    "<code>dp[0] = dp[1] = 1</code>; <code>dp[i] = dp[i-1] + dp[i-2]</code>.",
                ],
                "why": [
                    "It is O(n) time and space, with no recursion depth limit.",
                ],
                "dry": [
                    "dp = [1, 1, 2, 3, 5, 8].",
                    "dp[5] = <strong>8</strong>.",
                ],
            },
            "Two variables": {
                "idea": [
                    "Each step reads only the previous two counts, so keep just those two.",
                ],
                "steps": [
                    "<code>a, b = 1, 1</code>; repeat n - 1 times: <code>a, b = b, a + b</code>; return <code>b</code>.",
                ],
                "why": [
                    "It is O(n) time and O(1) space. Getting the base case wrong (f(0) = 0) shifts every answer.",
                ],
                "dry": [
                    "(a, b): (1, 1) → (1, 2) → (2, 3) → (3, 5) → (5, 8).",
                    "That is 4 steps, so b = <strong>8</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ house robber
    "house-robber": {
        "example": {"call": "rob([2, 7, 9, 3, 1])", "expect": "12"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Decide about the last house i: either skip it (best of houses 0..i-1), or rob it and skip i-1 (nums[i] + best of 0..i-2).",
                    "<code>f(i) = max(f(i-1), nums[i] + f(i-2))</code>, with f(-1) = 0.",
                ],
                "steps": [
                    "Recurse from the last house.",
                ],
                "why": [
                    "Robbing never takes two adjacent houses, and both options are always tried.",
                    "It branches like Fibonacci: exponential time, O(n) stack.",
                ],
                "dry": [
                    "f(4) = max(f(3), 1 + f(2)); f(3) = max(f(2), 3 + f(1)), so f(2) is needed twice.",
                    "Subproblems repeat throughout the tree.",
                    "The best total is <strong>12</strong>: rob 2, 9 and 1.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>f(i)</code>, so each house's best is computed once.",
                ],
                "steps": [
                    "Same recursion with <code>@cache</code>.",
                ],
                "why": [
                    "It is O(n) time and O(n) space; very long streets hit the recursion limit.",
                ],
                "dry": [
                    "f(0) = 2, f(1) = max(2, 7) = 7, f(2) = max(7, 9 + 2) = 11.",
                    "f(3) = max(11, 3 + 7) = 11, f(4) = max(11, 1 + 11) = <strong>12</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "<code>dp[i]</code> = the best from the first i houses. Shifting by one puts the base case f(-1) = 0 into <code>dp[0]</code>.",
                ],
                "steps": [
                    "<code>dp[1] = nums[0]</code>; <code>dp[i] = max(dp[i-1], nums[i-1] + dp[i-2])</code>.",
                ],
                "why": [
                    "It is O(n) time and space, with no recursion.",
                ],
                "dry": [
                    "dp = [0, 2, 7, 11, 11, 12].",
                    "dp[5] = <strong>12</strong>.",
                ],
            },
            "Two variables": {
                "idea": [
                    "Keep only <code>prev</code> (best two houses back) and <code>cur</code> (best one house back).",
                    "Starting both at 0 means an empty street, so even the first house needs no special case.",
                ],
                "steps": [
                    "For each x: <code>prev, cur = cur, max(cur, prev + x)</code>.",
                ],
                "why": [
                    "It is one pass in O(1) space.",
                ],
                "dry": [
                    "(prev, cur): x=2 → (0, 2); x=7 → (2, 7); x=9 → (7, 11).",
                    "x=3 → (11, 11); x=1 → (11, 12).",
                    "The result is <strong>12</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ house robber II
    "house-robber-ii": {
        "example": {"call": "rob([2, 7, 9, 3, 1])", "expect": "11"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "On a circle, the first and last houses are neighbours, so they can never both be robbed.",
                    "So solve two straight streets, one without the last house and one without the first, and take the better.",
                    "Each street is House Robber's recursion.",
                ],
                "steps": [
                    "<code>line(lo, i)</code> = the best from houses lo..i.",
                    "Return <code>max(line(1, n-1), line(0, n-2))</code>; a single house is a special case.",
                ],
                "why": [
                    "Every valid choice leaves out the first or the last house, so it is covered by one of the two lines.",
                    "Exponential, like House Robber.",
                ],
                "dry": [
                    "Without the first house, [7, 9, 3, 1]: the best is 10 (7 + 3, or 9 + 1).",
                    "Without the last house, [2, 7, 9, 3]: the best is 11 (2 + 9).",
                    "The result is <strong>11</strong>. Robbing 2, 9 and 1 is not allowed here, because 2 and 1 are neighbours on the circle.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "The same two lines, with cached states <code>(lo, i)</code>.",
                ],
                "steps": [
                    "<code>@cache</code> on <code>line</code>.",
                ],
                "why": [
                    "It is O(n) time and space.",
                ],
                "dry": [
                    "Line 1..4: f gives 7, 9, 10, 10.",
                    "Line 0..3: f gives 2, 7, 11, 11.",
                    "max(10, 11) = <strong>11</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "Build a House Robber table for each of the two ranges.",
                ],
                "steps": [
                    "<code>dp[k]</code> = the best from the first k houses of the range, with <code>dp[0] = 0</code>.",
                ],
                "why": [
                    "Two O(n) tables: O(n).",
                ],
                "dry": [
                    "Houses 1..4: dp = [0, 7, 9, 10, 10].",
                    "Houses 0..3: dp = [0, 2, 7, 11, 11].",
                    "The result is <strong>11</strong>.",
                ],
            },
            "Two variables per pass": {
                "idea": [
                    "House Robber's rolling pair, run over each range by index.",
                    "Slicing (<code>nums[1:]</code>) would be easier to read, but it copies n elements and quietly brings back O(n) space.",
                ],
                "steps": [
                    "<code>line(lo, hi)</code> with <code>prev, cur</code> over indices lo..hi-1.",
                ],
                "why": [
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "Pass 1 (7, 9, 3, 1): cur goes 7, 9, 10, 10.",
                    "Pass 2 (2, 7, 9, 3): cur goes 2, 7, 11, 11.",
                    "The result is <strong>11</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum subarray
    "maximum-subarray": {
        "example": {"call": "max_sub_array([-2, 1, -3, 4, -1, 2, 1, -5, 4])", "expect": "6"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Let <code>f(i)</code> be the best sum of a subarray that <em>ends exactly at</em> i.",
                    "It either starts fresh at i, or extends the best subarray ending at i-1: <code>f(i) = max(nums[i], f(i-1) + nums[i])</code>.",
                    "The answer is the maximum f(i) over all i.",
                ],
                "steps": [
                    "Compute f(i) recursively for every i, and take the max.",
                ],
                "why": [
                    "There is one recursive call per level, but each f(i) walks back to f(0) again: O(n²) time.",
                ],
                "dry": [
                    "The f values are -2, 1, -2, 4, 3, 5, 6, 1, 5.",
                    "Computing them independently takes 45 calls for 9 elements.",
                    "The maximum is <strong>6</strong>, from the subarray [4, -1, 2, 1].",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>f(i)</code>, so each later call finds <code>f(i-1)</code> ready.",
                ],
                "steps": [
                    "Same recursion with <code>@cache</code>.",
                ],
                "why": [
                    "It is O(n) time and space.",
                ],
                "dry": [
                    "f(0) = -2. f(1) = max(1, -1) = 1. f(2) = max(-3, -2) = -2. f(3) = max(4, 2) = 4.",
                    "f(4) = 3, f(5) = 5, f(6) = 6, f(7) = 1, f(8) = 5.",
                    "The maximum is <strong>6</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "Fill <code>dp[i]</code> = the best sum ending at i, from left to right.",
                ],
                "steps": [
                    "<code>dp[0] = nums[0]</code>; <code>dp[i] = max(nums[i], dp[i-1] + nums[i])</code>; return <code>max(dp)</code>.",
                ],
                "why": [
                    "It is O(n) time and space.",
                ],
                "dry": [
                    "dp = [-2, 1, -2, 4, 3, 5, 6, 1, 5].",
                    "max(dp) = <strong>6</strong>.",
                ],
            },
            "One variable (Kadane)": {
                "idea": [
                    "Each dp[i] only reads dp[i-1], so one running value <code>end_here</code> replaces the table. That is Kadane's algorithm.",
                    "Start from <code>nums[0]</code>, not 0: if every number is negative, the answer is the largest single element.",
                ],
                "steps": [
                    "<code>end_here = max(x, end_here + x)</code>; <code>best = max(best, end_here)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "end_here: -2, 1, -2, 4 (a fresh start), 3, 5, 6, 1, 5.",
                    "best climbs to <strong>6</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ decode ways
    "decode-ways": {
        "example": {"call": 'num_decodings("11106")', "expect": "2"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Look at the last letter of a decoding of <code>s[:i]</code>: it used either the last digit alone (if it is not '0'), or the last two digits (if they form 10..26).",
                    "<code>f(i) = (f(i-1) if s[i-1] != '0') + (f(i-2) if s[i-2:i] in 10..26)</code>, with f(0) = 1.",
                ],
                "steps": [
                    "Recurse from <code>len(s)</code> down to 0.",
                ],
                "why": [
                    "The two cases cover every way to end a decoding. It branches like Fibonacci when both are valid.",
                ],
                "dry": [
                    "f(5): '6' is valid alone, giving f(4); \"06\" is invalid.",
                    "f(4): '0' alone is invalid; \"10\" is valid, giving f(2).",
                    "f(2) = f(1) + f(0) = 2 (\"1,1\" or \"11\"). So f(5) = <strong>2</strong>: AAJF and KJF.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>f(i)</code>, giving n + 1 states.",
                    "The comparison <code>\"10\" &lt;= s[i-2:i] &lt;= \"26\"</code> works because both strings are two characters long, so string order equals number order.",
                ],
                "steps": [
                    "Same recursion with <code>@cache</code>.",
                ],
                "why": [
                    "It is O(n) time and space.",
                ],
                "dry": [
                    "f(0) = 1, f(1) = 1, f(2) = 2, f(3) = 3, f(4) = 2, f(5) = 2.",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "Fill <code>dp[i]</code> = the number of decodings of <code>s[:i]</code>, from left to right.",
                ],
                "steps": [
                    "<code>dp[0] = 1</code>; add <code>dp[i-1]</code> if the one-digit code is valid, and <code>dp[i-2]</code> if the two-digit code is valid.",
                ],
                "why": [
                    "It is O(n) time and space.",
                ],
                "dry": [
                    "dp = [1, 1, 2, 3, 2, 2].",
                    "At i=4, '0' alone adds nothing, but \"10\" adds dp[2] = 2.",
                    "dp[5] = <strong>2</strong>.",
                ],
            },
            "Two variables": {
                "idea": [
                    "Each step reads only the previous two counts. <code>prev</code> starts at 0 (there is no dp[-1]) and <code>cur</code> at 1 (dp[0]).",
                ],
                "steps": [
                    "Compute <code>nxt</code> from the one-digit and two-digit cases, then slide the pair.",
                ],
                "why": [
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "'1': (1, 1). '1': nxt = 1 + 1 (\"11\") = 2, giving (1, 2). '1': nxt = 2 + 1 = 3, giving (2, 3).",
                    "'0': nxt = 0 + 2 (\"10\") = 2, giving (3, 2).",
                    "'6': nxt = 2 (\"06\" is invalid), giving (2, 2). The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ delete and earn
    "delete-and-earn": {
        "example": {"call": "delete_and_earn([2, 2, 3, 3, 3, 4])", "expect": "9"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Taking a value v earns v for every copy, but forbids v - 1 and v + 1. That is House Robber on the number line.",
                    "<code>points[v]</code> = v × (count of v); then <code>f(v) = max(f(v-1), points[v] + f(v-2))</code>.",
                ],
                "steps": [
                    "Bucket the values into <code>points</code>, then recurse from the largest value.",
                ],
                "why": [
                    "Neighbouring values on the number line play the role of adjacent houses.",
                    "Exponential in the largest value m.",
                ],
                "dry": [
                    "points = [0, 0, 4, 9, 4] (values 0..4).",
                    "f(4) = max(f(3), 4 + f(2)) branches like House Robber.",
                    "The best is <strong>9</strong>: take all the 3s.",
                ],
            },
            "Top-down memo": {
                "idea": [
                    "Cache <code>f(v)</code>. It is linear now, but values up to 10<sup>4</sup> mean a recursion 10<sup>4</sup> deep, so go bottom-up.",
                ],
                "steps": [
                    "<code>@cache</code> on f.",
                ],
                "why": [
                    "It is O(n + m) time.",
                ],
                "dry": [
                    "f(0) = 0, f(1) = 0, f(2) = 4, f(3) = max(4, 9) = 9, f(4) = max(9, 4 + 4) = 9.",
                    "The result is <strong>9</strong>.",
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "Fill <code>dp[v+1]</code> = the best from values 0..v; the shift keeps the v - 2 &lt; 0 case inside the table.",
                ],
                "steps": [
                    "<code>dp[v+1] = max(dp[v], points[v] + dp[v-1])</code>.",
                ],
                "why": [
                    "It is O(n + m).",
                ],
                "dry": [
                    "dp = [0, 0, 0, 4, 9, 9].",
                    "The result is <strong>9</strong>.",
                ],
            },
            "Two variables": {
                "idea": [
                    "Run House Robber's rolling pair over the <code>points</code> array.",
                ],
                "steps": [
                    "For each p in points: <code>prev, cur = cur, max(cur, prev + p)</code>.",
                ],
                "why": [
                    "It is O(n) to bucket and O(m) to scan.",
                ],
                "dry": [
                    "(prev, cur): 0 → (0, 0), 0 → (0, 0), 4 → (0, 4), 9 → (4, 9), 4 → (9, 9).",
                    "The result is <strong>9</strong>.",
                ],
            },
            "Sorted distinct values": {
                "idea": [
                    "Walk only the distinct values, in sorted order.",
                    "A value exactly one more than the previous one conflicts with it, so choose as in House Robber. After a gap there is no conflict, so just add.",
                    "This avoids an array indexed by value, which matters when values are huge and sparse.",
                ],
                "steps": [
                    "<code>gain = v · count[v]</code>; conflict: <code>max(cur, prev + gain)</code>; gap: <code>cur + gain</code>.",
                ],
                "why": [
                    "It is O(n log n) for the sort and works for values up to 10<sup>9</sup>.",
                ],
                "dry": [
                    "v=2 (gain 4): the first value, so cur = 4.",
                    "v=3 (gain 9): adjacent to 2, so cur = max(4, 0 + 9) = 9.",
                    "v=4 (gain 4): adjacent to 3, so cur = max(9, 4 + 4) = 9.",
                    "The result is <strong>9</strong>.",
                ],
            },
        },
    },
}
