"""Write-ups for Dynamic Programming, part 1: foundations and linear DP."""

EXPLAIN = {
    # ------------------------------------------------------------------ nth fibonacci
    "nth-fibonacci": {
        "examples": [
            {"call": "fib(6)", "expect": "8"},
            {"call": "fib(1)", "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "This is the starting rung of the ladder: write the definition F(n) = F(n − 1) + F(n − 2), with F(0) = 0 and F(1) = 1, straight into code.",
                    "It is obviously correct, but each call spawns two more and the <strong>same arguments are solved again and again</strong> in different branches of the call tree.",
                    "Seeing that repetition is the whole point of this rung: every later version exists to remove it.",
                ],
                "steps": [
                    "If <code>n &lt; 2</code>, return <code>n</code> itself: that covers F(0) = 0 and F(1) = 1.",
                    "Otherwise call <code>fib(n - 1)</code> and wait for its whole subtree to finish.",
                    "Then call <code>fib(n - 2)</code>, which recomputes a subtree that <code>fib(n - 1)</code> already explored.",
                    "Return the sum of the two results.",
                ],
                "why": [
                    "Each call returns exactly the recurrence applied to smaller arguments, and both base cases are handled, so by induction the result is F(n).",
                    "The number of calls itself grows like the Fibonacci numbers, about 1.618 times per extra level, so time is <strong>O(φ<sup>n</sup>)</strong>.",
                    "Only one root-to-leaf chain is on the call stack at any moment, and it is at most n deep, so space is <strong>O(n)</strong>.",
                ],
                "dry": [
                    [
                        "fib(6) calls fib(5) and fib(4); fib(5) calls fib(4) again and fib(3).",
                        "The tree keeps branching: fib(4) is computed 2 times, fib(3) 3 times, fib(2) 5 times.",
                        "The leaves are 8 calls of fib(1) returning 1 and 5 calls of fib(0) returning 0.",
                        "In total there are 25 calls for an answer that needs only 7 distinct values.",
                        "The leaves add up to <strong>8</strong>.",
                    ],
                    [
                        "fib(1): <code>n &lt; 2</code> holds immediately.",
                        "No recursive calls are made at all.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the space O(n) and not O(φ<sup>n</sup>) too?",
                     "Calls finish before their sibling starts, so the stack only ever holds one chain from the root down. The deepest chain is fib(n), fib(n − 1), …, fib(1), which is n frames."],
                    ["How slow is it in practice?",
                     "fib(30) already makes about 2.7 million calls, and every extra 1 in n multiplies the work by about 1.6. Fine for the tiny tests, hopeless beyond about n = 35."],
                    ["Why <code>n &lt; 2</code> instead of two separate base cases?",
                     "For n = 0 and n = 1 the answer equals n, so one comparison covers both. A negative n would also return itself, which is outside the problem."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: the same recursive function, wrapped in <code>@cache</code> so each argument is solved <strong>once</strong>.",
                    "There are only n + 1 distinct arguments (0..n), so once each is remembered, every repeated call becomes a dictionary lookup instead of a whole subtree.",
                    "That single decorator turns an exponential algorithm into a linear one: this is memoisation, the top-down form of DP.",
                ],
                "steps": [
                    "Define an inner function <code>f(i)</code> decorated with <code>@cache</code>.",
                    "If <code>i &lt; 2</code>, return <code>i</code>.",
                    "Otherwise return <code>f(i - 1) + f(i - 2)</code>; the cache stores the result before returning it.",
                    "Call <code>f(n)</code>. The first branch, <code>f(i - 1)</code>, runs all the way down and fills the cache.",
                    "Every second branch, <code>f(i - 2)</code>, then finds its value already cached.",
                ],
                "why": [
                    "The cache never changes what <code>f</code> returns, only how often the body runs, so correctness is inherited from plain recursion.",
                    "Each of the n + 1 states runs its body once with O(1) work, plus one extra cache hit each, giving <strong>O(n)</strong> time.",
                    "The cache holds n + 1 entries and the recursion still goes n deep, so space is <strong>O(n)</strong>.",
                ],
                "dry": [
                    [
                        "f(6) → f(5) → f(4) → f(3) → f(2) → f(1) = 1, then f(0) = 0, so f(2) = 1 is cached.",
                        "Back in f(3): its second call f(1) is a cache hit, f(3) = 2.",
                        "f(4) = f(3) + f(2) = 2 + 1 = 3, with f(2) a cache hit. f(5) = 3 + 2 = 5.",
                        "f(6) = f(5) + f(4) = 5 + 3, with f(4) a cache hit: 11 calls instead of 25.",
                        "It returns <strong>8</strong>.",
                    ],
                    [
                        "f(1) is not cached yet, so its body runs.",
                        "<code>i &lt; 2</code>, so it returns 1 and caches f(1) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why define <code>f</code> inside <code>fib</code> instead of caching <code>fib</code> itself?",
                     "Here it makes no difference to the answer; keeping the cache inner means each call to <code>fib</code> starts fresh and the pattern carries over to problems where the cache depends on the input list."],
                    ["Is there any risk left?",
                     "Recursion depth. CPython's default limit is about 1000 frames, so <code>f(5000)</code> would raise RecursionError. The bottom-up table removes the recursion."],
                    ["What does <code>@cache</code> actually store?",
                     "A dictionary from the argument tuple to the returned value. Arguments must be hashable, which plain integers are."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "What changed from the memo: instead of recursing down and caching on the way back, fill the answers <strong>from small to large in a list</strong>.",
                    "F(i) only needs F(i − 1) and F(i − 2), so if the list is filled in increasing i, both are ready when they are needed.",
                    "Removing the recursion removes the call overhead and the recursion-depth limit, with the same O(n) work.",
                ],
                "steps": [
                    "If <code>n &lt; 2</code>, return <code>n</code> straight away (the table would need index 1 to exist).",
                    "Create <code>dp = [0] * (n + 1)</code> and set <code>dp[1] = 1</code>; <code>dp[0]</code> is already 0.",
                    "For <code>i</code> from 2 to n, set <code>dp[i] = dp[i - 1] + dp[i - 2]</code>.",
                    "Return <code>dp[n]</code>.",
                ],
                "why": [
                    "Each cell is written once from two cells already final, so by induction <code>dp[i]</code> = F(i) for every i.",
                    "One loop of n − 1 constant-time steps gives <strong>O(n)</strong> time.",
                    "The table keeps every value, <strong>O(n)</strong> space, even though each step only reads the last two. The next rung exploits exactly that.",
                ],
                "dry": [
                    [
                        "dp = [0, 1, 0, 0, 0, 0, 0].",
                        "i=2: 1 + 0 = 1. i=3: 1 + 1 = 2. i=4: 2 + 1 = 3.",
                        "i=5: 3 + 2 = 5. i=6: 5 + 3 = 8.",
                        "dp = [0, 1, 1, 2, 3, 5, 8].",
                        "It returns dp[6] = <strong>8</strong>.",
                    ],
                    [
                        "n = 1, so the early return fires.",
                        "No table is built.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the early return for <code>n &lt; 2</code>?",
                     "For n = 0 the list has one cell, so <code>dp[1] = 1</code> would raise IndexError. Returning early avoids that special case."],
                    ["Is this faster than the memo even though both are O(n)?",
                     "Yes, by a constant factor: a list index and an addition are much cheaper than a function call plus a cache lookup."],
                    ["When is the full table worth keeping?",
                     "When you need many answers afterwards, for example all of F(0..n), or when you must reconstruct a choice later. For a single F(n) it is wasted memory."],
                ],
            },
            "Two variables": {
                "idea": [
                    "What changed from the table: each step reads only the <strong>last two cells</strong>, so keep just those two numbers instead of the whole list.",
                    "The pair <code>(a, b)</code> always holds (F(i), F(i + 1)); one step slides it to (F(i + 1), F(i + 2)).",
                    "Same O(n) time, but memory drops from O(n) to O(1).",
                ],
                "steps": [
                    "Start with <code>a, b = 0, 1</code>: F(0) and F(1).",
                    "Repeat n times: <code>a, b = b, a + b</code>.",
                    "The tuple assignment evaluates the right side first, so the old <code>a</code> is used in <code>a + b</code>.",
                    "After n steps <code>a</code> holds F(n): return it.",
                ],
                "why": [
                    "The invariant is that after k steps <code>(a, b)</code> = (F(k), F(k + 1)); one step keeps it true because F(k + 2) = F(k) + F(k + 1).",
                    "After n steps <code>a</code> = F(n), and n = 0 works with zero steps.",
                    "n constant-time steps: <strong>O(n)</strong> time. Two integers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start (a, b) = (0, 1).",
                        "Steps 1-3: (1, 1), (1, 2), (2, 3).",
                        "Steps 4-6: (3, 5), (5, 8), (8, 13).",
                        "a is F(6) and b is already F(7).",
                        "It returns <strong>8</strong>.",
                    ],
                    [
                        "Start (a, b) = (0, 1).",
                        "One step: (1, 1).",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return <code>a</code> and not <code>b</code>?",
                     "The loop runs n times and <code>a</code> is F(number of steps done), so it is F(n). Returning <code>b</code> would give F(n + 1)."],
                    ["What goes wrong with <code>a = b</code> then <code>b = a + b</code> on two lines?",
                     "The second line would use the new <code>a</code>, computing 2·b instead of a + b. The tuple form avoids a temporary variable."],
                    ["Is O(1) space exactly true for huge n?",
                     "In terms of numbers stored, yes. Python integers grow to about 0.7·n bits, so for very large n the arithmetic itself gets slower and bigger."],
                ],
            },
            "Fast doubling": {
                "idea": [
                    "What changed from two variables: instead of stepping from F(k) to F(k + 1), <strong>jump from k to 2k</strong> using doubling identities.",
                    "F(2k) = F(k)·(2·F(k + 1) − F(k)) and F(2k + 1) = F(k)² + F(k + 1)². Knowing the pair at k gives the pair at 2k or 2k + 1.",
                    "Halving n at every level means only about log₂ n levels, like fast exponentiation.",
                ],
                "steps": [
                    "<code>pair(k)</code> returns <code>(F(k), F(k+1))</code>; <code>pair(0)</code> is <code>(0, 1)</code>.",
                    "Otherwise get <code>a, b = pair(k // 2)</code>.",
                    "Compute <code>c = a * (2 * b - a)</code>, which is F(2m) for m = k // 2, and <code>d = a * a + b * b</code>, which is F(2m + 1).",
                    "If k is even, k = 2m and the pair is <code>(c, d)</code>.",
                    "If k is odd, k = 2m + 1 and the pair is <code>(d, c + d)</code>.",
                    "Return <code>pair(n)[0]</code>.",
                ],
                "why": [
                    "The two identities follow from the matrix form of Fibonacci, so if <code>pair(k // 2)</code> is right then <code>pair(k)</code> is right; by induction from k = 0 the whole chain is correct.",
                    "Each level does a constant number of multiplications and halves k, so there are about log₂ n levels: <strong>O(log n)</strong> arithmetic operations.",
                    "The recursion is log₂ n deep with one frame per level: <strong>O(log n)</strong> space.",
                ],
                "dry": [
                    [
                        "pair(6) → pair(3) → pair(1) → pair(0) = (0, 1).",
                        "pair(1): a=0, b=1, c = 0, d = 1. Odd, so (d, c + d) = (1, 1).",
                        "pair(3): a=1, b=1, c = 1·(2 − 1) = 1, d = 1 + 1 = 2. Odd, so (2, 3).",
                        "pair(6): a=2, b=3, c = 2·(6 − 2) = 8, d = 4 + 9 = 13. Even, so (8, 13).",
                        "It returns <strong>8</strong> after only 4 calls.",
                    ],
                    [
                        "pair(1) → pair(0) = (0, 1).",
                        "c = 0·(2 − 0) = 0 and d = 0 + 1 = 1.",
                        "1 is odd, so the pair is (1, 1).",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return the pair instead of just F(k)?",
                     "Both identities need F(k) and F(k + 1). Returning the pair keeps it one recursive call per level instead of two."],
                    ["Is it really O(log n) for huge n?",
                     "In number of arithmetic operations, yes. The numbers have about 0.7·n bits, so big-integer multiplication dominates; it is still far faster than n additions."],
                    ["Do I need this in an interview?",
                     "Rarely. It is the answer to \"can you beat O(n)?\"; mention it after the two-variable version, alongside the 2 × 2 matrix-power idea it comes from."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ climbing stairs
    "climbing-stairs": {
        "examples": [
            {"call": "climb_stairs(5)", "expect": "8"},
            {"call": "climb_stairs(1)", "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "The last move onto step i is either a 1-step from i − 1 or a 2-step from i − 2, and those two groups of routes never overlap.",
                    "So ways(i) = ways(i − 1) + ways(i − 2): the Fibonacci recurrence with different starting values.",
                    "This rung writes that recurrence directly and pays for it by recomputing the same steps many times.",
                ],
                "steps": [
                    "Define <code>f(i)</code> = number of ways to reach step <code>i</code> from the ground.",
                    "If <code>i &lt;= 1</code>, return 1: there is one way to stay on the ground and one way to reach step 1.",
                    "Otherwise return <code>f(i - 1) + f(i - 2)</code>.",
                    "Return <code>f(n)</code>.",
                ],
                "why": [
                    "Every route to step i ends with exactly one of the two last moves, so the two counts add up without double counting.",
                    "The call tree branches twice per level like Fibonacci: <strong>O(φ<sup>n</sup>)</strong> time.",
                    "The deepest chain is n frames: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(5) calls f(4) and f(3); f(4) calls f(3) again and f(2).",
                        "Across the tree f(3) runs 2 times and f(2) runs 3 times.",
                        "The leaves are 5 calls of f(1) and 3 calls of f(0), each returning 1.",
                        "15 calls in total, adding up 8 leaves of value 1.",
                        "It returns <strong>8</strong>.",
                    ],
                    [
                        "f(1): <code>i &lt;= 1</code>, return 1.",
                        "Only one way: a single 1-step.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is f(0) = 1 and not 0?",
                     "It counts the empty route: standing on the ground is one way to be at step 0. With 0 there, f(2) would come out as 1 instead of 2."],
                    ["How is this different from Fibonacci?",
                     "Only the start: f(0) = f(1) = 1, so f(n) = F(n + 1). f(5) = 8 = F(6)."],
                    ["Why does it count orders, not combinations?",
                     "The recurrence fixes the last move, so 1+2 and 2+1 are separate routes. That matches the problem, which counts distinct sequences of moves."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f</code>, so each step number is solved once.",
                    "There are only n + 1 different step numbers, so the exponential tree collapses to a chain of n + 1 computations.",
                ],
                "steps": [
                    "Decorate <code>f(i)</code> with <code>@cache</code>.",
                    "Base case: <code>i &lt;= 1</code> returns 1.",
                    "Otherwise <code>f(i - 1) + f(i - 2)</code>; the first call fills the cache all the way down.",
                    "The second call, <code>f(i - 2)</code>, is then always a cache hit.",
                    "Return <code>f(n)</code>.",
                ],
                "why": [
                    "Caching never changes a returned value, so the answer is the same as plain recursion.",
                    "Each of the n + 1 states runs its body once with O(1) work: <strong>O(n)</strong> time.",
                    "The cache has n + 1 entries and the stack goes n deep: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(5) → f(4) → f(3) → f(2) → f(1) = 1, f(0) = 1, so f(2) = 2.",
                        "f(3) = f(2) + f(1) = 2 + 1 = 3, with f(1) a cache hit.",
                        "f(4) = 3 + 2 = 5, with f(2) a cache hit.",
                        "f(5) = f(4) + f(3) = 5 + 3, with f(3) a cache hit.",
                        "It returns <strong>8</strong>.",
                    ],
                    [
                        "f(1) is not cached yet; its body runs.",
                        "The base case returns 1 and caches it.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Does the order of <code>f(i - 1)</code> and <code>f(i - 2)</code> matter?",
                     "Not for the answer. Calling <code>f(i - 1)</code> first means it fills everything below, so <code>f(i - 2)</code> is always already cached."],
                    ["Can n = 45 overflow the stack?",
                     "No, 45 frames is tiny. Only n in the thousands would hit CPython's recursion limit."],
                    ["Why <code>@cache</code> and not a dictionary by hand?",
                     "Same behaviour, less code. A hand-written <code>memo</code> dict is fine in an interview if the decorator is not allowed."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "What changed from the memo: fill <code>dp[0..n]</code> in increasing order instead of recursing.",
                    "<code>dp[i]</code> depends only on the two cells before it, so a left-to-right loop always finds them ready.",
                    "No recursion means no call overhead and no depth limit.",
                ],
                "steps": [
                    "Create <code>dp = [1] * (n + 1)</code>: this sets both base cases <code>dp[0] = dp[1] = 1</code> at once.",
                    "For <code>i</code> from 2 to n, set <code>dp[i] = dp[i - 1] + dp[i - 2]</code>.",
                    "The 1s in cells 2..n are overwritten before they are read.",
                    "Return <code>dp[n]</code>.",
                ],
                "why": [
                    "Each cell is computed from two final cells, so by induction <code>dp[i]</code> is the number of ways to reach step i.",
                    "One pass of n − 1 constant steps: <strong>O(n)</strong> time.",
                    "The list keeps all n + 1 counts: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "dp = [1, 1, 1, 1, 1, 1].",
                        "i=2: 1 + 1 = 2. i=3: 2 + 1 = 3.",
                        "i=4: 3 + 2 = 5. i=5: 5 + 3 = 8.",
                        "dp = [1, 1, 2, 3, 5, 8].",
                        "It returns <strong>8</strong>.",
                    ],
                    [
                        "dp = [1, 1].",
                        "<code>range(2, 2)</code> is empty, so the loop does nothing.",
                        "It returns dp[1] = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>[1] * (n + 1)</code> instead of zeros?",
                     "It sets both base cases in one go. The other cells are overwritten before they are read, so their starting value does not matter."],
                    ["Does it handle n = 1?",
                     "Yes. The list has two cells, the loop is empty, and <code>dp[1] = 1</code> is returned."],
                    ["Why keep the whole table?",
                     "There is no need to here; it is the step that makes the dependency pattern visible, which the two-variable version then exploits."],
                ],
            },
            "Two variables": {
                "idea": [
                    "What changed from the table: only <code>dp[i - 1]</code> and <code>dp[i - 2]</code> are ever read, so keep <strong>just those two</strong>.",
                    "<code>(a, b)</code> holds (ways to step i − 1, ways to step i) and slides forward one step per iteration.",
                    "Same O(n) time, O(1) memory.",
                ],
                "steps": [
                    "Start with <code>a, b = 1, 1</code>: f(0) and f(1).",
                    "Repeat <code>n - 1</code> times: <code>a, b = b, a + b</code>.",
                    "Each repetition moves the pair from (f(i − 1), f(i)) to (f(i), f(i + 1)).",
                    "Return <code>b</code>, which is now f(n).",
                ],
                "why": [
                    "Invariant: after k iterations <code>(a, b)</code> = (f(k), f(k + 1)). After n − 1 iterations <code>b</code> = f(n).",
                    "n − 1 constant-time iterations: <strong>O(n)</strong> time.",
                    "Two integers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start (a, b) = (1, 1), loop runs 4 times.",
                        "(1, 2), then (2, 3).",
                        "(3, 5), then (5, 8).",
                        "It returns b = <strong>8</strong>.",
                    ],
                    [
                        "Start (a, b) = (1, 1).",
                        "<code>range(0)</code> is empty: no iterations.",
                        "It returns b = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why loop <code>n - 1</code> times and return <code>b</code>?",
                     "The pair starts already holding f(1) in <code>b</code>. Each iteration advances <code>b</code> by one step, so n − 1 iterations reach f(n)."],
                    ["What if the problem allowed 1, 2 or 3 steps?",
                     "Keep three variables and add all three: f(i) = f(i − 1) + f(i − 2) + f(i − 3). The pattern generalises to any fixed set of moves."],
                    ["Is this the best possible?",
                     "For counts that fit in normal integers it is what interviewers expect. Fast doubling or matrix power gives O(log n) if ever needed."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ house robber
    "house-robber": {
        "examples": [
            {"call": "rob([2, 7, 9, 3, 1])", "expect": "12"},
            {"call": "rob([2, 1, 1, 2])", "expect": "4"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Look at the last house <code>i</code>. Either you skip it, and the best is whatever houses 0..i − 1 give, or you rob it, and house i − 1 is off limits so you add houses 0..i − 2.",
                    "That gives f(i) = max(f(i − 1), nums[i] + f(i − 2)): one choice per house, written as recursion.",
                    "Like Fibonacci, the two branches overlap heavily, so this first rung is exponential.",
                ],
                "steps": [
                    "Define <code>f(i)</code> = most money from houses 0..i.",
                    "If <code>i &lt; 0</code>, there are no houses: return 0.",
                    "Skip option: <code>f(i - 1)</code>.",
                    "Take option: <code>nums[i] + f(i - 2)</code>.",
                    "Return the larger of the two; the answer is <code>f(len(nums) - 1)</code>.",
                ],
                "why": [
                    "Any valid plan either robs house i or not; each case reduces to a smaller version of the same question, so taking the max covers every plan.",
                    "Each call spawns two, and the arguments repeat like Fibonacci: <strong>O(φ<sup>n</sup>)</strong> time.",
                    "The deepest chain is about n frames: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(4) = max(f(3), 1 + f(2)); both branches go down to f(−1) and f(−2).",
                        "f(0) = 2, f(1) = max(2, 7 + 0) = 7, f(2) = max(7, 9 + 2) = 11.",
                        "f(3) = max(11, 3 + 7) = 11, f(4) = max(11, 1 + 11) = 12.",
                        "The tree makes 25 calls in all; f(0) alone is solved 5 times.",
                        "It returns <strong>12</strong> (houses 2, 9, 1).",
                    ],
                    [
                        "f(0) = 2, f(1) = max(2, 1 + 0) = 2.",
                        "f(2) = max(f(1), 1 + f(0)) = max(2, 3) = 3.",
                        "f(3) = max(f(2), 2 + f(1)) = max(3, 4) = 4. 15 calls in all.",
                        "It returns <strong>4</strong> (the two end houses), which beats both \"every other house\" patterns (3 each).",
                    ],
                ],
                "faq": [
                    ["Why not just compare the sum of even indices with the sum of odd indices?",
                     "Because the best plan can skip two houses in a row. On [2, 1, 1, 2] both alternating sums are 3, but robbing the two ends gives 4."],
                    ["Why <code>i &lt; 0</code> as the base case?",
                     "f(i − 2) is called for i = 0 and 1, which gives −2 and −1. Treating any negative index as \"no houses\" handles both without extra cases."],
                    ["What if all values are 0?",
                     "Every option is 0, so the answer is 0. Values are non-negative here, so robbing an extra house never hurts the sum."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f</code>, so each house index is solved once.",
                    "The states are just i = −2..n − 1, so the exponential tree becomes n + 2 cheap computations.",
                ],
                "steps": [
                    "Decorate <code>f(i)</code> with <code>@cache</code>.",
                    "If <code>i &lt; 0</code>, return 0.",
                    "Return <code>max(f(i - 1), nums[i] + f(i - 2))</code>.",
                    "The first branch fills the cache all the way down; the second is always a cache hit.",
                    "Return <code>f(len(nums) - 1)</code>.",
                ],
                "why": [
                    "The decorator changes only how often the body runs, not what it returns, so correctness carries over.",
                    "About n + 2 distinct states, each doing O(1) work: <strong>O(n)</strong> time.",
                    "Cache entries plus recursion depth: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(4) → f(3) → f(2) → f(1) → f(0) → f(−1) = 0, f(−2) = 0, so f(0) = 2.",
                        "f(1) = max(f(0), 7 + f(−1)) = 7.",
                        "f(2) = max(7, 9 + 2) = 11, f(3) = max(11, 3 + 7) = 11, each second branch a cache hit.",
                        "f(4) = max(11, 1 + f(2)) = max(11, 12).",
                        "It returns <strong>12</strong>.",
                    ],
                    [
                        "Down the chain: f(0) = 2, f(1) = max(2, 1) = 2.",
                        "f(2) = max(2, 1 + 2) = 3.",
                        "f(3) = max(3, 2 + f(1)) = max(3, 4) = 4, with f(1) a cache hit.",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>nums</code> not an argument of <code>f</code>?",
                     "Lists are not hashable, so <code>@cache</code> could not key on them. <code>f</code> reads <code>nums</code> from the enclosing function, and only the index is cached."],
                    ["Does the cache leak between calls to <code>rob</code>?",
                     "No. A new <code>f</code> with a fresh cache is created every time <code>rob</code> runs."],
                    ["Is the recursion depth a problem?",
                     "For a few hundred houses no; for tens of thousands it would hit Python's recursion limit. The table and two-variable versions avoid that."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "What changed from the memo: fill the answers from left to right in a list instead of recursing.",
                    "The table is shifted by one: <code>dp[i]</code> is the best from the <strong>first i houses</strong>, so <code>dp[0] = 0</code> stands for \"no houses\" and no negative index is needed.",
                    "Each cell reads the two before it, which a left-to-right loop has already filled.",
                ],
                "steps": [
                    "Create <code>dp = [0] * (n + 1)</code>.",
                    "Set <code>dp[1] = nums[0]</code>: with one house, rob it.",
                    "For <code>i</code> from 2 to n, house <code>i - 1</code> is the newest: <code>dp[i] = max(dp[i - 1], nums[i - 1] + dp[i - 2])</code>.",
                    "Return <code>dp[n]</code>.",
                ],
                "why": [
                    "Same recurrence as the recursion, with the index shifted by one, so each cell is the best for its prefix.",
                    "One loop with constant work per house: <strong>O(n)</strong> time.",
                    "The table holds n + 1 values: <strong>O(n)</strong> space, though only two are read at each step.",
                ],
                "dry": [
                    [
                        "dp = [0, 2, 0, 0, 0, 0].",
                        "i=2 (house 7): max(2, 7 + 0) = 7. i=3 (house 9): max(7, 9 + 2) = 11.",
                        "i=4 (house 3): max(11, 3 + 7) = 11.",
                        "i=5 (house 1): max(11, 1 + 11) = 12. dp = [0, 2, 7, 11, 11, 12].",
                        "It returns <strong>12</strong>.",
                    ],
                    [
                        "dp = [0, 2, 0, 0, 0].",
                        "i=2 (house 1): max(2, 1 + 0) = 2. i=3 (house 1): max(2, 1 + 2) = 3.",
                        "i=4 (house 2): max(3, 2 + dp[2]) = max(3, 4) = 4.",
                        "dp = [0, 2, 2, 3, 4].",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why size n + 1 instead of n?",
                     "The extra cell <code>dp[0] = 0</code> means \"no houses\" and replaces the <code>i &lt; 0</code> base case, so the loop never touches a negative index."],
                    ["What if <code>nums</code> is empty?",
                     "<code>dp[1] = nums[0]</code> would raise IndexError. The problem guarantees at least one house; otherwise guard with <code>if not nums: return 0</code>."],
                    ["How would I recover which houses were robbed?",
                     "Walk back from <code>dp[n]</code>: if <code>dp[i] == dp[i - 1]</code> house i − 1 was skipped, otherwise it was robbed and you jump to i − 2. That is a reason to keep the full table."],
                ],
            },
            "Two variables": {
                "idea": [
                    "What changed from the table: the loop only ever reads <code>dp[i - 1]</code> and <code>dp[i - 2]</code>, so keep those two as <code>cur</code> and <code>prev</code>.",
                    "For each house <code>x</code> the new best is <code>max(cur, prev + x)</code>: skip it, or rob it on top of the best that ends two houses back.",
                    "Same O(n) time, O(1) memory, and no index arithmetic at all.",
                ],
                "steps": [
                    "Start with <code>prev, cur = 0, 0</code>: the best from \"two houses ago\" and \"one house ago\".",
                    "For each value <code>x</code> in <code>nums</code>:",
                    "Compute the new best <code>max(cur, prev + x)</code>.",
                    "Slide the window: <code>prev, cur = cur, new best</code> in one tuple assignment.",
                    "Return <code>cur</code>.",
                ],
                "why": [
                    "Invariant: after processing k houses, <code>cur</code> = dp[k] and <code>prev</code> = dp[k − 1]. The update is exactly the table's recurrence.",
                    "One pass with constant work per house: <strong>O(n)</strong> time.",
                    "Two integers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start (prev, cur) = (0, 0).",
                        "x=2: (0, 2). x=7: max(2, 0 + 7) → (2, 7).",
                        "x=9: max(7, 2 + 9) → (7, 11). x=3: max(11, 7 + 3) → (11, 11).",
                        "x=1: max(11, 11 + 1) → (11, 12).",
                        "It returns <strong>12</strong>.",
                    ],
                    [
                        "Start (0, 0). x=2: (0, 2).",
                        "x=1: max(2, 0 + 1) = 2 → (2, 2).",
                        "x=1: max(2, 2 + 1) = 3 → (2, 3).",
                        "x=2: max(3, 2 + 2) = 4 → (3, 4).",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the tuple assignment matter?",
                     "<code>max(cur, prev + x)</code> must use the old <code>prev</code> and <code>cur</code>. The right side is evaluated fully before either name is reassigned."],
                    ["Does it work for an empty list?",
                     "Yes: the loop never runs and it returns 0, unlike the table version."],
                    ["Where else does this exact loop appear?",
                     "House Robber II runs it twice, and Delete and Earn runs it over point totals per value. Recognising the shape is most of the work."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ house robber ii
    "house-robber-ii": {
        "examples": [
            {"call": "rob([2, 7, 9, 3, 1])", "expect": "11"},
            {"call": "rob([2, 3, 2])", "expect": "3"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "The houses form a circle, so the first and last are neighbours. Any valid plan leaves out <strong>at least one</strong> of them.",
                    "So split into two straight-line problems: houses 1..n − 1 (first left out) and houses 0..n − 2 (last left out), and take the better one.",
                    "Each line is ordinary House Robber; this rung solves it with plain recursion <code>line(lo, i)</code>.",
                ],
                "steps": [
                    "<code>line(lo, i)</code> = most money from houses <code>lo..i</code>; if <code>i &lt; lo</code> it returns 0.",
                    "Otherwise it returns <code>max(line(lo, i - 1), nums[i] + line(lo, i - 2))</code>: skip or rob house i.",
                    "With a single house there is no conflict: return <code>nums[0]</code>.",
                    "Otherwise return <code>max(line(1, n - 1), line(0, n - 2))</code>.",
                ],
                "why": [
                    "Every circular plan avoids house 0 or house n − 1 (or both), so it is a valid plan for at least one line; and every line plan is valid on the circle. The max of the two lines is the answer.",
                    "Each line recursion branches like Fibonacci: <strong>O(φ<sup>n</sup>)</strong> time.",
                    "The deepest chain is about n frames: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Line without house 0: houses 7, 9, 3, 1. Best values grow 7, 9, 10, 10, so line(1, 4) = 10.",
                        "Line without house 4: houses 2, 7, 9, 3. Best values 2, 7, 11, 11, so line(0, 3) = 11.",
                        "The two recursions make 30 calls between them.",
                        "Robbing 2, 9 and 1 (= 12) is impossible here because houses 0 and 4 touch.",
                        "It returns max(10, 11) = <strong>11</strong>.",
                    ],
                    [
                        "line(1, 2): houses 3, 2. max(skip 2 → 3, rob 2 → 2) = 3.",
                        "line(0, 1): houses 2, 3. max(2, 3) = 3.",
                        "The two 2s are the first and last house, so they can never both be robbed.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>n == 1</code> special?",
                     "With one house, both lines would be empty and give 0. But a single house has no neighbour, so you can rob it."],
                    ["Could the best plan skip both house 0 and house n − 1?",
                     "Yes, and then it is counted in both lines. Taking the max of the two still finds it, so nothing breaks."],
                    ["Why not one pass with a flag for \"house 0 was robbed\"?",
                     "That also works, but it doubles the state. Two independent line passes are simpler to get right."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>line(lo, i)</code>, so each (start, index) pair is solved once.",
                    "<code>lo</code> takes only two values, 0 and 1, so there are about 2n states in total.",
                ],
                "steps": [
                    "Decorate <code>line(lo, i)</code> with <code>@cache</code>; the cache key is the pair of arguments.",
                    "Base case <code>i &lt; lo</code> returns 0.",
                    "Otherwise <code>max(line(lo, i - 1), nums[i] + line(lo, i - 2))</code>.",
                    "Handle <code>n == 1</code> by returning <code>nums[0]</code>.",
                    "Return <code>max(line(1, n - 1), line(0, n - 2))</code>.",
                ],
                "why": [
                    "The cache does not change values, so correctness carries over from plain recursion and the two-line argument.",
                    "About 2n states with O(1) work each: <strong>O(n)</strong> time.",
                    "Cache entries plus recursion depth: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "line(1, 4) fills line(1, ·): 7, 9, 10, 10, so it is 10.",
                        "line(0, 3) fills line(0, ·): 2, 7, 11, 11, so it is 11.",
                        "The two lines share no cache entries because <code>lo</code> differs.",
                        "It returns <strong>11</strong>.",
                    ],
                    [
                        "line(1, 2): line(1, 1) = 3, then max(3, 2 + 0) = 3.",
                        "line(0, 1): line(0, 0) = 2, then max(2, 3 + 0) = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>lo</code> be part of the cache key?",
                     "line(0, 3) and line(1, 3) cover different houses and have different answers. Caching on <code>i</code> alone would mix them up."],
                    ["Are the two lines' results ever reused by each other?",
                     "No. They overlap in houses but start at different points, so their subproblems differ."],
                    ["Is this any better than running House Robber twice?",
                     "It is the same thing. The memo just shows that adding a parameter to the state is how you handle a new constraint."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "What changed from the memo: each line is solved with a small table filled left to right, no recursion.",
                    "<code>line(lo, hi)</code> now takes a half-open range: houses <code>lo..hi − 1</code>, and <code>dp[k]</code> is the best from its first k houses.",
                ],
                "steps": [
                    "Create <code>dp = [0] * (hi - lo + 1)</code>; <code>dp[0] = 0</code> means no houses yet.",
                    "For <code>k</code> from 1 up, the newest house is <code>nums[lo + k - 1]</code>.",
                    "<code>take</code> = that house plus <code>dp[k - 2]</code> (or plus 0 when k = 1).",
                    "<code>dp[k] = max(dp[k - 1], take)</code>.",
                    "Return <code>dp[-1]</code>; the answer is <code>max(line(1, n), line(0, n - 1))</code>, with <code>n == 1</code> handled first.",
                ],
                "why": [
                    "Each table is the ordinary House Robber recurrence on its own line, and the two lines cover every circular plan.",
                    "Two passes of about n steps each: <strong>O(n)</strong> time.",
                    "Each table holds about n values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "line(1, 5) over 7, 9, 3, 1: dp = [0, 7, 9, 10, 10].",
                        "At k=3: take = 3 + dp[1] = 10 beats dp[2] = 9.",
                        "line(0, 4) over 2, 7, 9, 3: dp = [0, 2, 7, 11, 11].",
                        "At k=3: take = 9 + 2 = 11.",
                        "It returns max(10, 11) = <strong>11</strong>.",
                    ],
                    [
                        "line(1, 3) over 3, 2: dp = [0, 3, 3].",
                        "line(0, 2) over 2, 3: dp = [0, 2, 3].",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the guard <code>dp[k - 2] if k &gt;= 2 else 0</code>?",
                     "For k = 1, <code>dp[k - 2]</code> would be <code>dp[-1]</code>, the last cell of the table, not \"no houses\". The guard uses 0 instead."],
                    ["Why half-open <code>(lo, hi)</code> here but inclusive in the recursion?",
                     "Half-open ranges make the table size simply <code>hi - lo + 1</code> and match Python's <code>range</code>. Both styles work if used consistently."],
                    ["Can the two tables share one list?",
                     "Yes, by reusing it, but nothing is gained: the next rung drops the tables entirely."],
                ],
            },
            "Two variables per pass": {
                "idea": [
                    "What changed from the table: each line only reads its last two cells, so <code>line</code> keeps just <code>prev</code> and <code>cur</code>.",
                    "It is the House Robber two-variable loop, run once on houses 1..n − 1 and once on houses 0..n − 2.",
                ],
                "steps": [
                    "<code>line(lo, hi)</code> starts with <code>prev, cur = 0, 0</code>.",
                    "For each <code>i</code> in <code>range(lo, hi)</code>: <code>prev, cur = cur, max(cur, prev + nums[i])</code>.",
                    "Return <code>cur</code>.",
                    "If <code>n == 1</code>, return <code>nums[0]</code>.",
                    "Otherwise return <code>max(line(1, n), line(0, n - 1))</code>.",
                ],
                "why": [
                    "Each pass is the proven House Robber recurrence on one line; the circle reduces to those two lines.",
                    "Two linear passes: <strong>O(n)</strong> time.",
                    "Two integers per pass, reused: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "line(1, 5): houses 7, 9, 3, 1 give (0, 7), (7, 9), (9, 10), (10, 10). Result 10.",
                        "line(0, 4): houses 2, 7, 9, 3 give (0, 2), (2, 7), (7, 11), (11, 11). Result 11.",
                        "max(10, 11) = 11.",
                        "It returns <strong>11</strong>.",
                    ],
                    [
                        "line(1, 3): houses 3, 2 give (0, 3), (3, 3). Result 3.",
                        "line(0, 2): houses 2, 3 give (0, 2), (2, 3). Result 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just run House Robber once and drop the first or last house afterwards?",
                     "The best line plan might use both ends, and you cannot tell which one to remove without re-solving. Two passes settle it directly."],
                    ["Does <code>n == 2</code> work?",
                     "Yes: each line has one house, so the answer is the larger of the two, which is correct since they are neighbours."],
                    ["What is the total work compared with House Robber?",
                     "About twice as many steps, still O(n) time and O(1) space."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum subarray
    "maximum-subarray": {
        "examples": [
            {"call": "max_sub_array([2, -3, 4, -1, 2])", "expect": "5"},
            {"call": "max_sub_array([-3, -1, -2])", "expect": "-1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Ask a narrower question: what is the best sum of a subarray that <strong>ends exactly at index i</strong>? Call it f(i).",
                    "Such a subarray is either <code>nums[i]</code> alone, or the best one ending at i − 1 extended by <code>nums[i]</code>. So f(i) = max(nums[i], f(i − 1) + nums[i]).",
                    "Every subarray ends somewhere, so the answer is the largest f(i). This rung recomputes the chain for every i.",
                ],
                "steps": [
                    "Define <code>f(i)</code>; if <code>i == 0</code> the only subarray ending there is <code>nums[0]</code>.",
                    "Otherwise return <code>max(nums[i], f(i - 1) + nums[i])</code>.",
                    "Call <code>f(i)</code> for every i from 0 to n − 1.",
                    "Return the maximum of those values.",
                ],
                "why": [
                    "The best subarray ending at i either starts at i or contains i − 1, in which case its part up to i − 1 must itself be the best ending at i − 1. So the recurrence is exact.",
                    "Each <code>f(i)</code> is a single chain of i + 1 calls (no branching), but the chains are recomputed for every i: 1 + 2 + … + n calls, <strong>O(n²)</strong> time.",
                    "The deepest chain is n frames: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(0) = 2.",
                        "f(1) = max(−3, 2 − 3) = −1. f(2) = max(4, −1 + 4) = 4: starting fresh wins.",
                        "f(3) = max(−1, 4 − 1) = 3. f(4) = max(2, 3 + 2) = 5.",
                        "The calls f(0..4) re-walk their chains: 1 + 2 + 3 + 4 + 5 = 15 calls.",
                        "max(2, −1, 4, 3, 5) = <strong>5</strong> (the subarray 4, −1, 2).",
                    ],
                    [
                        "f(0) = −3.",
                        "f(1) = max(−1, −3 − 1) = −1. f(2) = max(−2, −1 − 2) = −2.",
                        "6 calls in total.",
                        "max(−3, −1, −2) = <strong>−1</strong>: with all negatives the best is the single largest element.",
                    ],
                ],
                "faq": [
                    ["Why is this O(n²) and not exponential like Fibonacci?",
                     "<code>f(i)</code> makes only one recursive call, so each chain is linear. The waste is that the outer loop restarts the chain from scratch for every i."],
                    ["Why not define f(i) as the best subarray anywhere in 0..i?",
                     "That value cannot be extended: the best subarray so far may not touch i, so adding <code>nums[i]</code> to it would make a non-contiguous sum. \"Ending exactly at i\" is what makes extension valid."],
                    ["Why not start with 0 instead of <code>nums[0]</code>?",
                     "The subarray must be non-empty. With all negatives, a 0 would wrongly win over the true answer, like −1 in [−3, −1, −2]."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f</code>, so each chain link is computed once and shared by all the later calls.",
                    "The outer loop calls f(0), f(1), … in order, so each f(i) finds f(i − 1) already cached and does O(1) work.",
                ],
                "steps": [
                    "Decorate <code>f(i)</code> with <code>@cache</code>.",
                    "Base case: <code>f(0) = nums[0]</code>.",
                    "Otherwise <code>max(nums[i], f(i - 1) + nums[i])</code>.",
                    "Take <code>max(f(i) for i in range(len(nums)))</code>; each call reuses the previous one.",
                ],
                "why": [
                    "Values are the same as plain recursion, so correctness carries over.",
                    "n states with O(1) work each: <strong>O(n)</strong> time.",
                    "The cache stores n values: <strong>O(n)</strong> space. Because calls go in increasing i, the stack stays shallow here.",
                ],
                "dry": [
                    [
                        "f(0) = 2 is computed and cached.",
                        "f(1) hits the cache for f(0): max(−3, −1) = −1. f(2) uses f(1): max(4, 3) = 4.",
                        "f(3) = max(−1, 3) = 3, f(4) = max(2, 5) = 5, one step each.",
                        "5 body runs instead of 15.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "f(0) = −3, f(1) = max(−1, −4) = −1, f(2) = max(−2, −3) = −2.",
                        "Each one reuses the cached previous value.",
                        "It returns <strong>−1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the stack stay shallow even though <code>f</code> is recursive?",
                     "The generator calls f(0) first, then f(1), and so on. When f(i) runs, f(i − 1) is already cached, so it never recurses more than one level."],
                    ["Would calling only f(n − 1) be enough?",
                     "No. f(n − 1) is only the best subarray ending at the last index; the overall best may end earlier, so every f(i) is needed."],
                    ["Is the memo actually helpful here, compared with Fibonacci?",
                     "It saves a factor of n (O(n²) to O(n)) rather than an exponential, because the plain version only repeated whole chains, not branching subtrees."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "What changed from the memo: fill <code>dp[i]</code>, the best sum ending at i, in a simple left-to-right loop.",
                    "Each cell needs only the cell before it, and the answer is the largest cell.",
                ],
                "steps": [
                    "Create <code>dp</code> of length n and set <code>dp[0] = nums[0]</code>.",
                    "For <code>i</code> from 1 to n − 1: <code>dp[i] = max(nums[i], dp[i - 1] + nums[i])</code>.",
                    "If the run so far is negative, <code>nums[i]</code> alone wins and the subarray restarts at i.",
                    "Return <code>max(dp)</code>.",
                ],
                "why": [
                    "Same recurrence as before, so <code>dp[i]</code> is the best subarray ending at i, and the best overall is the max over all ends.",
                    "One pass plus one <code>max</code> over the list: <strong>O(n)</strong> time.",
                    "The table holds n values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "dp[0] = 2.",
                        "dp[1] = max(−3, −1) = −1. dp[2] = max(4, 3) = 4.",
                        "dp[3] = max(−1, 3) = 3. dp[4] = max(2, 5) = 5.",
                        "dp = [2, −1, 4, 3, 5].",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "dp[0] = −3.",
                        "dp[1] = max(−1, −4) = −1. dp[2] = max(−2, −3) = −2.",
                        "dp = [−3, −1, −2].",
                        "It returns <strong>−1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>max(dp)</code> and not <code>dp[-1]</code>?",
                     "<code>dp[-1]</code> is only the best subarray ending at the last element. In [2, −3, 4, −1, 2] it happens to be the answer, but in [5, −9] it is −4 while the answer is 5."],
                    ["How do I recover the subarray itself?",
                     "Record where each run restarts (whenever <code>nums[i]</code> beats the extension). The best subarray runs from the last restart before the max cell to that cell."],
                    ["Is the extra list needed?",
                     "No: each cell reads only the previous one, which is why the next rung keeps one variable."],
                ],
            },
            "One variable (Kadane)": {
                "idea": [
                    "What changed from the table: only <code>dp[i - 1]</code> is ever read, so keep it in one variable <code>end_here</code>, plus <code>best</code> for the running max.",
                    "This is Kadane's algorithm: extend the current run, or throw it away and restart at x when the run would only drag x down.",
                ],
                "steps": [
                    "Set <code>best = end_here = nums[0]</code>.",
                    "For each <code>x</code> in <code>nums[1:]</code>:",
                    "<code>end_here = max(x, end_here + x)</code>: restart or extend.",
                    "<code>best = max(best, end_here)</code>: remember the best end seen.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Invariant: <code>end_here</code> is dp[i] and <code>best</code> is max(dp[0..i]), exactly what the table computed.",
                    "Restarting is right because a run with a negative total can only lower any sum it is attached to.",
                    "One pass: <strong>O(n)</strong> time. Two variables: <strong>O(1)</strong> space. (The slice <code>nums[1:]</code> copies the list; iterating by index would avoid that.)",
                ],
                "dry": [
                    [
                        "best = end_here = 2.",
                        "x=−3: end_here = max(−3, −1) = −1, best 2.",
                        "x=4: end_here = max(4, 3) = 4 (restart), best 4.",
                        "x=−1: end_here = 3. x=2: end_here = 5, best 5.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "best = end_here = −3.",
                        "x=−1: end_here = max(−1, −4) = −1, best −1.",
                        "x=−2: end_here = max(−2, −3) = −2, best stays −1.",
                        "It returns <strong>−1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why initialise with <code>nums[0]</code> rather than 0?",
                     "The answer must be a non-empty subarray. Starting at 0 would return 0 for [−3, −1, −2] instead of −1."],
                    ["Isn't restarting when <code>end_here &lt; 0</code> the same thing?",
                     "Yes: <code>max(x, end_here + x)</code> picks x exactly when <code>end_here &lt; 0</code> (ties give the same value). Both forms are common."],
                    ["Does the slice <code>nums[1:]</code> break the O(1) space claim?",
                     "Strictly, it makes a copy of n − 1 elements. Looping over <code>range(1, len(nums))</code> keeps it truly O(1) extra space."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ decode ways
    "decode-ways": {
        "examples": [
            {"call": 'num_decodings("226")', "expect": "3"},
            {"call": 'num_decodings("2101")', "expect": "1"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Look at how a decoding of the prefix <code>s[:i]</code> ends: its last letter used either <strong>one digit</strong> <code>s[i-1]</code> or <strong>two digits</strong> <code>s[i-2:i]</code>.",
                    "One digit is allowed if it is not '0'. Two digits are allowed if they read 10..26. The counts for the two cases add up.",
                    "This rung writes that as f(i), the number of ways to decode <code>s[:i]</code>, with plain recursion.",
                ],
                "steps": [
                    "<code>f(0) = 1</code>: the empty prefix has one decoding (nothing).",
                    "Start <code>total</code> with <code>f(i - 1)</code> if <code>s[i - 1] != \"0\"</code>, else 0.",
                    "If <code>i &gt;= 2</code> and <code>\"10\" &lt;= s[i - 2:i] &lt;= \"26\"</code>, add <code>f(i - 2)</code>.",
                    "Return <code>total</code>; the answer is <code>f(len(s))</code>.",
                ],
                "why": [
                    "Every decoding ends in exactly one of the two ways, and each way is valid only under its digit rule, so the sum counts each decoding once.",
                    "The two-digit check is a string comparison: for two-character strings, <code>\"10\" &lt;= t &lt;= \"26\"</code> means exactly 10..26, and it rejects leading zeros like \"06\".",
                    "Up to two calls per level: <strong>O(φ<sup>n</sup>)</strong> time in the worst case (strings like \"1111…\"). The stack is <strong>O(n)</strong> deep.",
                ],
                "dry": [
                    [
                        "f(3): '6' is valid, so total = f(2); \"26\" is valid, so add f(1).",
                        "f(2): '2' valid → f(1); \"22\" valid → + f(0). f(1) = f(0) = 1, so f(2) = 2.",
                        "f(1) is computed again for f(3)'s second branch: 1.",
                        "7 calls in total: 2 + 1 = 3 (\"BBF\", \"BZ\", \"VF\").",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "f(4): '1' valid → f(3); \"01\" is not 10..26, no second term.",
                        "f(3): '0' cannot stand alone → 0; \"10\" valid → f(1).",
                        "f(1): '2' valid → f(0) = 1.",
                        "The '0' forces the pairing \"2 10 1\": only 4 calls.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compare strings instead of converting with <code>int</code>?",
                     "Both work. The string range <code>\"10\"..\"26\"</code> automatically rejects \"06\" (a leading zero), which <code>int(\"06\") = 6</code> would let through unless you also check the first digit."],
                    ["What does a '0' do to the count?",
                     "It can never be decoded alone, so it must pair with the digit before it as \"10\" or \"20\". Anything else, like \"30\" or a leading '0', makes the count 0."],
                    ["Why is f(0) = 1?",
                     "It is the empty decoding that a full string extends. With f(0) = 0 every count would collapse to 0."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f</code>, so each prefix length is counted once.",
                    "There are only n + 1 prefixes, so the exponential tree becomes a linear chain.",
                ],
                "steps": [
                    "Decorate <code>f(i)</code> with <code>@cache</code>.",
                    "<code>f(0) = 1</code>.",
                    "One-digit term <code>f(i - 1)</code> when <code>s[i - 1] != \"0\"</code>.",
                    "Two-digit term <code>f(i - 2)</code> when the pair is in \"10\"..\"26\".",
                    "Return <code>f(len(s))</code>.",
                ],
                "why": [
                    "The cache does not change results, so correctness carries over.",
                    "n + 1 states, O(1) work each (the two-character slice is constant size): <strong>O(n)</strong> time.",
                    "Cache plus recursion depth: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "f(3) → f(2) → f(1) → f(0) = 1, so f(1) = 1.",
                        "f(2) = f(1) + f(0) = 2 (\"22\" valid).",
                        "f(3) = f(2) + f(1) = 2 + 1, with f(1) a cache hit.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "f(4) → f(3) → f(1) → f(0) = 1.",
                        "f(3) = 0 + f(1) = 1 ('0' alone not allowed, \"10\" is).",
                        "f(4) = f(3) = 1 (\"01\" not allowed). f(2) is never needed.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the memo skip some states entirely?",
                     "Top-down only visits states reachable from f(n). In \"2101\", f(2) is never asked for because the '0' blocks that route."],
                    ["Is the slice <code>s[i - 2:i]</code> expensive?",
                     "It always has two characters, so it is O(1)."],
                    ["Could <code>s</code> start with '0'?",
                     "Then f(1) = 0 and every count built on it is 0, which is correct: no letter maps to '0'."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "What changed from the memo: fill <code>dp[0..n]</code> from left to right with the same two rules.",
                    "<code>dp[i]</code> is the number of decodings of <code>s[:i]</code>, and each cell reads only the two before it.",
                ],
                "steps": [
                    "Create <code>dp = [0] * (n + 1)</code> with <code>dp[0] = 1</code>.",
                    "For <code>i</code> from 1 to n: if <code>s[i - 1] != \"0\"</code>, set <code>dp[i] = dp[i - 1]</code>.",
                    "If <code>i &gt;= 2</code> and <code>s[i - 2:i]</code> is in \"10\"..\"26\", add <code>dp[i - 2]</code>.",
                    "A cell that passes neither test stays 0.",
                    "Return <code>dp[n]</code>.",
                ],
                "why": [
                    "Same recurrence filled in dependency order, so each cell is final when read.",
                    "One pass with O(1) work per character: <strong>O(n)</strong> time.",
                    "The table holds n + 1 counts: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "dp = [1, 0, 0, 0].",
                        "i=1 ('2'): dp[1] = 1.",
                        "i=2 ('2', pair \"22\"): dp[2] = 1 + 1 = 2.",
                        "i=3 ('6', pair \"26\"): dp[3] = 2 + 1 = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "i=1 ('2'): dp[1] = 1. i=2 ('1', \"21\"): dp[2] = 1 + 1 = 2.",
                        "i=3 ('0'): no single-digit term; \"10\" adds dp[1] = 1, so dp[3] = 1.",
                        "i=4 ('1'): dp[4] = dp[3] = 1; \"01\" is rejected.",
                        "dp = [1, 1, 2, 1, 1].",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>dp[3]</code> smaller than <code>dp[2]</code> in \"2101\"?",
                     "The '0' must glue to the '1' before it, which kills the decodings that used that '1' alone or as part of \"21\". Counts can go down, unlike in Climbing Stairs."],
                    ["What does a 0 in the middle of the table mean?",
                     "That prefix cannot be decoded at all, for example \"30\". Every later cell that depends on it inherits nothing from it."],
                    ["Why <code>if</code> then <code>+=</code> rather than one expression?",
                     "The two terms are independent and either can be missing; writing them separately keeps each rule readable."],
                ],
            },
            "Two variables": {
                "idea": [
                    "What changed from the table: only the last two counts are read, so keep <code>prev</code> (dp[i − 1]) and <code>cur</code> (dp[i]).",
                    "The loop now walks characters by 0-based index <code>i</code>, so the current digit is <code>s[i]</code> and the pair is <code>s[i - 1:i + 1]</code>.",
                ],
                "steps": [
                    "Start with <code>prev, cur = 0, 1</code>: dp[−1] (unused) and dp[0] = 1.",
                    "For each index <code>i</code>: <code>nxt = cur</code> if <code>s[i] != \"0\"</code>, else 0.",
                    "If <code>i &gt; 0</code> and the pair <code>s[i - 1:i + 1]</code> is in \"10\"..\"26\", add <code>prev</code>.",
                    "Slide: <code>prev, cur = cur, nxt</code>.",
                    "Return <code>cur</code>.",
                ],
                "why": [
                    "Invariant: before step i, <code>cur</code> = dp[i] and <code>prev</code> = dp[i − 1]; <code>nxt</code> is then exactly dp[i + 1].",
                    "The <code>i &gt; 0</code> guard means the placeholder <code>prev = 0</code> is never actually added.",
                    "One pass: <strong>O(n)</strong> time. Three integers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start (prev, cur) = (0, 1).",
                        "i=0 ('2'): nxt = 1 → (1, 1).",
                        "i=1 ('2', \"22\"): nxt = 1 + 1 = 2 → (1, 2).",
                        "i=2 ('6', \"26\"): nxt = 2 + 1 = 3 → (2, 3).",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "i=0 ('2'): nxt = 1 → (1, 1). i=1 ('1', \"21\"): nxt = 2 → (1, 2).",
                        "i=2 ('0'): nxt starts at 0; \"10\" adds prev = 1 → (2, 1).",
                        "i=3 ('1'): nxt = 1; \"01\" rejected → (1, 1).",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the pair use <code>s[i - 1:i + 1]</code> here but <code>s[i - 2:i]</code> in the table?",
                     "The table's <code>i</code> is a prefix length (1-based), this loop's <code>i</code> is a character index (0-based). Both slices name the same two characters."],
                    ["Can <code>cur</code> become 0 and recover later?",
                     "Only if <code>prev</code> feeds it through a valid pair, as with \"10\". Two 0s in a row (like \"100\") make both variables 0, and it stays 0 from then on."],
                    ["Why start <code>prev</code> at 0?",
                     "It is never used before being replaced, because the pair test needs <code>i &gt; 0</code>. 0 is just a safe placeholder."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ delete and earn
    "delete-and-earn": {
        "examples": [
            {"call": "delete_and_earn([2, 2, 3, 3, 3, 4])", "expect": "9"},
            {"call": "delete_and_earn([1, 1, 1, 2, 4, 5, 5])", "expect": "13"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "If you take one copy of value v, you should take <strong>all</strong> copies: the penalty (losing v − 1 and v + 1) is paid anyway. So value v is worth <code>points[v] = v · count(v)</code>.",
                    "Taking v forbids v − 1 and v + 1: exactly House Robber, with the houses being the values 0..max in order.",
                    "This rung builds <code>points</code> and then solves the robber recurrence with plain recursion.",
                ],
                "steps": [
                    "Build <code>points</code> of length <code>max(nums) + 1</code> and add each <code>x</code> into <code>points[x]</code>.",
                    "<code>f(v)</code> = most points using values 0..v; <code>f(v) = 0</code> for <code>v &lt; 0</code>.",
                    "Skip value v: <code>f(v - 1)</code>. Take it: <code>points[v] + f(v - 2)</code>.",
                    "Return <code>f(len(points) - 1)</code>.",
                ],
                "why": [
                    "Choosing a set of values with no two adjacent is exactly a robber plan on <code>points</code>, and the recurrence covers all such plans.",
                    "Building <code>points</code> is O(n), then the recursion branches like Fibonacci over m = max(nums) + 1 values: <strong>O(n + φ<sup>m</sup>)</strong> time.",
                    "<code>points</code> and the call stack both have size m: <strong>O(m)</strong> space.",
                ],
                "dry": [
                    [
                        "points = [0, 0, 4, 9, 4] (2·2, 3·3, 4·1).",
                        "f(2) = 4, f(3) = max(4, 9 + f(1)) = 9.",
                        "f(4) = max(f(3), 4 + f(2)) = max(9, 8) = 9.",
                        "25 calls in total for 5 values.",
                        "It returns <strong>9</strong>: take all three 3s.",
                    ],
                    [
                        "points = [0, 3, 2, 0, 4, 10].",
                        "f(1) = 3, f(2) = max(3, 2) = 3, f(3) = 3.",
                        "f(4) = max(3, 4 + 3) = 7: the empty slot 3 lets 4 combine with 1.",
                        "f(5) = max(7, 10 + f(3)) = 13. 41 calls in total.",
                        "It returns <strong>13</strong>: the 1s (3) plus the 5s (10).",
                    ],
                ],
                "faq": [
                    ["Why is it safe to take every copy of a value?",
                     "Once you take one v, all v − 1 and v + 1 are deleted, and the other copies of v are not neighbours of each other, so they can all be taken for free."],
                    ["What is m in the complexity?",
                     "The largest value plus one, the length of <code>points</code>. It can be much bigger than n, for example [1, 10000]."],
                    ["Why do values with no copies not matter?",
                     "They are houses worth 0. They still separate neighbours, which is what lets 1 and 4 both be taken in the second example."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>f(v)</code>, so each value is decided once.",
                    "With m values there are m + 2 states, so the recursion becomes linear in m.",
                ],
                "steps": [
                    "Build <code>points</code> as before.",
                    "Decorate <code>f(v)</code> with <code>@cache</code>; <code>f(v) = 0</code> for <code>v &lt; 0</code>.",
                    "<code>f(v) = max(f(v - 1), points[v] + f(v - 2))</code>.",
                    "Return <code>f(len(points) - 1)</code>.",
                ],
                "why": [
                    "The cache does not change values, so correctness carries over.",
                    "O(n) to build <code>points</code> plus O(1) per state: <strong>O(n + m)</strong> time.",
                    "<code>points</code>, the cache and the stack are each O(m): <strong>O(m)</strong> space.",
                ],
                "dry": [
                    [
                        "points = [0, 0, 4, 9, 4].",
                        "Down the chain: f(0) = 0, f(1) = 0, f(2) = 4.",
                        "f(3) = max(4, 9 + 0) = 9, f(4) = max(9, 4 + 4) = 9, second branches all cache hits.",
                        "It returns <strong>9</strong>.",
                    ],
                    [
                        "points = [0, 3, 2, 0, 4, 10].",
                        "f(1) = 3, f(2) = 3, f(3) = 3, f(4) = 7.",
                        "f(5) = max(7, 10 + 3) = 13.",
                        "It returns <strong>13</strong>.",
                    ],
                ],
                "faq": [
                    ["Could the recursion get too deep?",
                     "Yes: depth is about max(nums). For values up to 10<sup>4</sup> that is above CPython's default limit of 1000, so the bottom-up versions are safer."],
                    ["Why is <code>points</code> a list and not a dictionary?",
                     "The recurrence steps through every value 0..max, including missing ones, and a list gives O(1) access by value."],
                    ["Is this faster than the plain version on small inputs?",
                     "Barely matters for tiny inputs; the gap is exponential as max(nums) grows."],
                ],
            },
            "Bottom-up table": {
                "idea": [
                    "What changed from the memo: a left-to-right table over values instead of recursion.",
                    "<code>dp[v + 1]</code> is the best using values 0..v, shifted by one so <code>dp[0] = 0</code> means \"no values yet\".",
                ],
                "steps": [
                    "Build <code>points</code>.",
                    "Create <code>dp = [0] * (len(points) + 1)</code>.",
                    "For each <code>v</code>: <code>dp[v + 1] = max(dp[v], points[v] + dp[v - 1])</code>, using 0 instead of <code>dp[v - 1]</code> when v = 0.",
                    "Return <code>dp[-1]</code>.",
                ],
                "why": [
                    "Same robber recurrence over values, filled in dependency order.",
                    "O(n) to build <code>points</code> and O(m) for the loop: <strong>O(n + m)</strong> time.",
                    "<code>points</code> and <code>dp</code> are both O(m): <strong>O(m)</strong> space.",
                ],
                "dry": [
                    [
                        "points = [0, 0, 4, 9, 4], dp starts as six zeros.",
                        "v=0, 1: dp[1] = dp[2] = 0. v=2: dp[3] = max(0, 4 + 0) = 4.",
                        "v=3: dp[4] = max(4, 9 + dp[2]) = 9.",
                        "v=4: dp[5] = max(9, 4 + dp[3]) = max(9, 8) = 9.",
                        "It returns <strong>9</strong>.",
                    ],
                    [
                        "points = [0, 3, 2, 0, 4, 10].",
                        "dp fills as [0, 0, 3, 3, 3, 7, 13].",
                        "v=4: 4 + dp[3] = 7 beats 3. v=5: 10 + dp[4] = 13 beats 7.",
                        "It returns <strong>13</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the guard <code>dp[v - 1] if v &gt;= 1 else 0</code>?",
                     "For v = 0, <code>dp[-1]</code> would be the last cell of the list, not \"nothing\". The guard supplies 0."],
                    ["Does value 0 ever matter?",
                     "<code>points[0]</code> is always 0, so it never adds anything. It only exists so that list index equals value."],
                    ["Could I size the table by the number of distinct values instead?",
                     "Yes, if you handle gaps between values specially. That is exactly what the sorted-distinct-values approach does."],
                ],
            },
            "Two variables": {
                "idea": [
                    "What changed from the table: only the last two cells are read, so run the House Robber two-variable loop directly over <code>points</code>.",
                    "<code>points</code> itself still needs O(m) memory, so the DP part is O(1) but the whole approach is O(m).",
                ],
                "steps": [
                    "Build <code>points</code>.",
                    "Start with <code>prev, cur = 0, 0</code>.",
                    "For each <code>p</code> in <code>points</code>: <code>prev, cur = cur, max(cur, prev + p)</code>.",
                    "Return <code>cur</code>.",
                ],
                "why": [
                    "Invariant: after value v, <code>cur</code> is the best using 0..v and <code>prev</code> the best using 0..v − 1, the table's last two cells.",
                    "<strong>O(n + m)</strong> time: building <code>points</code> plus one pass over it.",
                    "The loop uses O(1) extra memory, but <code>points</code> is O(m), so total space is <strong>O(m)</strong>.",
                ],
                "dry": [
                    [
                        "points = [0, 0, 4, 9, 4].",
                        "p=0, 0: (0, 0). p=4: (0, 4).",
                        "p=9: max(4, 0 + 9) → (4, 9).",
                        "p=4: max(9, 4 + 4) → (9, 9).",
                        "It returns <strong>9</strong>.",
                    ],
                    [
                        "points = [0, 3, 2, 0, 4, 10].",
                        "p=0: (0, 0). p=3: (0, 3). p=2: (3, 3). p=0: (3, 3).",
                        "p=4: max(3, 3 + 4) → (3, 7).",
                        "p=10: max(7, 3 + 10) → (7, 13).",
                        "It returns <strong>13</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the space O(m) if the DP uses two variables?",
                     "The <code>points</code> array is still indexed by value and has max(nums) + 1 cells. Removing it is the job of the sorted-values approach."],
                    ["Is this identical to House Robber's loop?",
                     "Yes, character for character. The only new idea in this problem is the reduction to <code>points</code>."],
                    ["What if <code>nums</code> holds huge values like 10<sup>9</sup>?",
                     "<code>points</code> would be enormous. Use the sorted distinct values instead, which depends on n, not on the values."],
                ],
            },
            "Sorted distinct values": {
                "idea": [
                    "What changed from two variables: walk only the <strong>distinct values in sorted order</strong> instead of every integer 0..max, so huge or sparse values cost nothing extra.",
                    "If the current value is exactly one more than the previous one, it conflicts, so use the robber choice. If there is a gap, there is no conflict: add its gain on top of the best so far.",
                ],
                "steps": [
                    "Count each value with <code>Counter(nums)</code>.",
                    "Keep <code>prev</code>, <code>cur</code> (robber state) and <code>last</code>, the previous distinct value.",
                    "For each <code>v</code> in sorted order, <code>gain = v * count[v]</code>.",
                    "If <code>v == last + 1</code>: <code>prev, cur = cur, max(cur, prev + gain)</code>.",
                    "Otherwise (first value or a gap): <code>prev, cur = cur, cur + gain</code>, since nothing blocks it.",
                    "Set <code>last = v</code>; at the end return <code>cur</code>.",
                ],
                "why": [
                    "Missing values are houses worth 0. Skipping over them is the same as the gap rule: after a 0-house, the best with and without the previous value lead to taking v freely on top of <code>cur</code>.",
                    "Sorting the distinct values costs <strong>O(n log n)</strong> time; the pass itself is O(n).",
                    "The counter holds at most n keys: <strong>O(n)</strong> space, independent of how large the values are.",
                ],
                "dry": [
                    [
                        "count = {2: 2, 3: 3, 4: 1}.",
                        "v=2 (first, gain 4): (prev, cur) = (0, 4).",
                        "v=3 (adjacent, gain 9): max(4, 0 + 9) → (4, 9).",
                        "v=4 (adjacent, gain 4): max(9, 4 + 4) → (9, 9).",
                        "It returns <strong>9</strong>.",
                    ],
                    [
                        "count = {1: 3, 2: 1, 4: 1, 5: 2}.",
                        "v=1 (first, gain 3): (0, 3). v=2 (adjacent, gain 2): max(3, 2) → (3, 3).",
                        "v=4 (gap after 2, gain 4): no conflict → (3, 7).",
                        "v=5 (adjacent, gain 10): max(7, 3 + 10) → (7, 13).",
                        "It returns <strong>13</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>cur + gain</code> on a gap and not <code>prev + gain</code>?",
                     "<code>cur</code> is the best so far, and nothing in it conflicts with v because v − 1 was never present. Using <code>prev</code> would throw away the last value for no reason."],
                    ["Is O(n log n) better than O(n + m)?",
                     "It depends on m. When max(nums) is small (say ≤ 10<sup>4</sup>), the array version is faster; when values are large or sparse, this one wins."],
                    ["Why is <code>last</code> initialised to <code>None</code>?",
                     "So the first value always takes the gap branch: there is no previous value to conflict with."],
                ],
            },
        },
    },
}
