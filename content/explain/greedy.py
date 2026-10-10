"""Write-ups for the Greedy topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ lemonade change
    "lemonade-change": {
        "examples": [
            {"call": "lemonade_change([5, 5, 10, 20, 5, 5, 5, 20])", "expect": "True"},
            {"call": "lemonade_change([5, 5, 10, 10, 20])", "expect": "False"},
        ],
        "approaches": {
            "Try both ways of making change (search)": {
                "idea": [
                    "The only real choice in the whole problem is how to break a $20: with $10 + $5, or with three $5s. A $5 needs no change and a $10 has exactly one way.",
                    "Without any insight, try both options whenever both are possible, and succeed if either branch manages to serve everyone.",
                    "The full state is (customer index, number of $5s, number of $10s), so <code>@cache</code> on <code>ok(i, fives, tens)</code> stops the same situation being explored twice.",
                ],
                "steps": [
                    "<code>ok(i, fives, tens)</code> answers: starting with customer <code>i</code> and this cash, can everyone still be served?",
                    "If <code>i == len(bills)</code>, every customer was served: return <code>True</code>.",
                    "A $5 needs no change: recurse with <code>fives + 1</code>.",
                    "A $10 needs one $5 back: if <code>fives &gt; 0</code>, recurse with one fewer five and one more ten, otherwise the <code>and</code> short-circuits to <code>False</code>.",
                    "A $20 first tries $10 + $5 (needs <code>tens &gt; 0 and fives &gt; 0</code>), and if that branch fails, tries three $5s (needs <code>fives &gt;= 3</code>).",
                    "Return <code>ok(0, 0, 0)</code>: the stall opens with no cash.",
                ],
                "why": [
                    "Every possible way of giving change is explored, so if any plan serves everyone, one branch finds it.",
                    "Each $20 can branch twice, so without the cache the worst case is <strong>O(2<sup>n</sup>)</strong> calls; the cache caps it at the number of distinct (i, fives, tens) states.",
                    "The recursion depth is one level per customer, so the stack (plus the cache) uses <strong>O(n)</strong> space at minimum.",
                    "This search is what the greedy argument makes unnecessary: it shows one branch always dominates the other.",
                ],
                "dry": [
                    [
                        "ok(0,0,0) → $5 → ok(1,1,0) → $5 → ok(2,2,0).",
                        "$10: a five goes back → ok(3,1,1).",
                        "$20: $10 + $5 is possible → ok(4,0,0).",
                        "Three $5s → ok(5,1,0), ok(6,2,0), ok(7,3,0).",
                        "$20: no ten, so the first branch is skipped; three fives works → ok(8,0,0), past the end.",
                        "Every branch taken succeeded, so it returns <strong>True</strong>.",
                    ],
                    [
                        "ok(0,0,0) → ok(1,1,0) → ok(2,2,0).",
                        "First $10: one five back → ok(3,1,1).",
                        "Second $10: the last five goes back → ok(4,0,2).",
                        "$20: <code>fives &gt; 0</code> fails for $10 + $5, and <code>fives &gt;= 3</code> fails too.",
                        "No branch is left: <strong>False</strong>. Two tens are useless when the customer needs $15 back.",
                    ],
                ],
                "faq": [
                    ["Why is there no branch for a $10 customer?",
                     "The only way to give $5 back is a single $5 bill. There is nothing to choose, so the function simply checks <code>fives &gt; 0</code>."],
                    ["Why are $20 bills not tracked?",
                     "A $20 is never useful as change, because the most anyone needs back is $15. Leaving it out keeps the state smaller."],
                    ["Does the cache matter on these examples?",
                     "No: with no real choices made, every state is visited once. It matters on long inputs with many $20s, where both branches can lead to the same (i, fives, tens)."],
                ],
            },
            "Count bills, prefer giving a $10": {
                "idea": [
                    "A $5 can make change for both $10 and $20 payments; a $10 only helps with $20s. So $5s are the more valuable bill to keep.",
                    "When a $20 arrives, hand back $10 + $5 if possible and keep the fives; only fall back to three $5s.",
                    "Paying with the $10 always leaves at least as many fives as the alternative (two more, in fact), so it can never hurt a later customer.",
                ],
                "steps": [
                    "Track <code>fives</code> and <code>tens</code>, both starting at 0.",
                    "$5: <code>fives += 1</code>.",
                    "$10: if there is no five, return <code>False</code>; otherwise trade one five for one ten.",
                    "$20: if <code>tens and fives</code>, give one of each back.",
                    "Otherwise, if <code>fives &gt;= 3</code>, give three fives; otherwise return <code>False</code>.",
                    "If the loop finishes, everyone was served: return <code>True</code>.",
                ],
                "why": [
                    "Exchange argument: take any successful plan that answers some $20 with three fives when a ten was available. Swapping in ten + five leaves two extra fives and one fewer ten, and anything a ten can do later, two fives can do too.",
                    "So the greedy choice never turns a winnable sequence into a failure, and it fails only when no plan exists.",
                    "One pass with two counters: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "$5, $5: fives = 2.",
                        "$10: fives = 1, tens = 1.",
                        "$20: a ten and a five are there, so fives = 0, tens = 0.",
                        "$5, $5, $5: fives = 3.",
                        "$20: no ten, but fives ≥ 3, so fives = 0. Everyone is served: <strong>True</strong>.",
                    ],
                    [
                        "$5, $5: fives = 2.",
                        "$10: fives = 1, tens = 1.",
                        "$10: fives = 0, tens = 2.",
                        "$20: <code>tens and fives</code> is false (no five), and <code>fives &gt;= 3</code> is false.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong if a $20 gets three fives whenever possible?",
                     "On <code>[5, 5, 5, 5, 10, 20, 10, 10]</code> that rule spends three fives on the $20 and then has no five for the last $10, returning False. Preferring the ten keeps two fives and serves everyone."],
                    ["Why check <code>tens and fives</code> before <code>fives &gt;= 3</code>?",
                     "That order is the greedy rule itself: use the less useful ten first. Swapping the two branches gives the wrong rule from the previous question."],
                    ["Can the function stop early?",
                     "Yes. As soon as one customer cannot get change the answer is False, because the queue is served strictly in order."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max circular subarray
    "max-circular-subarray": {
        "examples": [
            {"call": "max_subarray_sum_circular([3, -1, -6, 4, 2])", "expect": "9"},
            {"call": "max_subarray_sum_circular([-3, -2, -3])", "expect": "-2"},
        ],
        "approaches": {
            "Every start, every length": {
                "idea": [
                    "In a circular array a subarray is a start index plus a length from 1 to n, and indices wrap round with <code>% n</code>.",
                    "Growing each start one element at a time gives every subarray's sum with a running total, so no inner re-summing is needed.",
                ],
                "steps": [
                    "Set <code>best = -inf</code> so even an all-negative array has an answer.",
                    "Loop the start <code>i</code> over every index and reset <code>total = 0</code>.",
                    "Loop <code>k</code> from 0 to n − 1, adding <code>nums[(i + k) % n]</code> to <code>total</code>: that is the sum of the subarray of length k + 1 starting at <code>i</code>.",
                    "After each addition, update <code>best = max(best, total)</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Every (start, length) pair is one circular subarray, and every pair is visited, so the maximum cannot be missed.",
                    "The length stops at n, so no element is ever used twice in one subarray.",
                    "n starts times n lengths gives <strong>O(n²)</strong> time; only <code>total</code> and <code>best</code> are kept, so space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "i=0: running sums 3, 2, −4, 0, 2. best = 3.",
                        "i=1: −1, −7, −3, −1, 2. best stays 3.",
                        "i=2: −6, −2, 0, 3, 2. best stays 3.",
                        "i=3: 4, 6, 9 (4 + 2 + 3, wrapping round), 8, 2. best = 9.",
                        "i=4: 2, 5, 4, −2, 2. It returns <strong>9</strong>.",
                    ],
                    [
                        "i=0: running sums −3, −5, −8. best = −3.",
                        "i=1: −2, −5, −8. best = −2.",
                        "i=2: −3, −6, −8.",
                        "It returns <strong>-2</strong>, the single largest element.",
                    ],
                ],
                "faq": [
                    ["Why <code>-inf</code> and not 0 for the start?",
                     "The subarray must be non-empty. With all-negative input the answer is negative, and starting at 0 would wrongly report 0."],
                    ["Why does <code>k</code> stop at n − 1?",
                     "A subarray of length n already uses every element once. Going further would count elements twice, which the problem forbids."],
                    ["Is this only useful as a checker?",
                     "Mostly. It is the definition written as code, so it is easy to trust, and the faster approaches are tested against it."],
                ],
            },
            "Best prefix plus best suffix": {
                "idea": [
                    "The best circular subarray either does not wrap (plain Kadane finds it) or wraps: it is a <strong>suffix</strong> of the array glued to a <strong>prefix</strong>.",
                    "For a wrapping answer, fix where the suffix starts at <code>j</code>. The best partner is the largest prefix sum that ends before <code>j</code>, which a precomputed array answers in O(1).",
                ],
                "steps": [
                    "Run Kadane over <code>nums</code> to get <code>best</code>, the best non-wrapping sum.",
                    "Build <code>right_max[i]</code> = the largest prefix sum among <code>nums[:1]</code> … <code>nums[:i+1]</code>, using a running <code>prefix</code>.",
                    "Walk <code>j</code> from n − 1 down to 1, adding <code>nums[j]</code> to <code>suffix</code>, so <code>suffix</code> is the sum of <code>nums[j:]</code>.",
                    "Pair it with the best prefix that stops before <code>j</code>: <code>best = max(best, suffix + right_max[j - 1])</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Every wrapping subarray is some suffix <code>nums[j:]</code> plus some prefix <code>nums[:i+1]</code> with i &lt; j, and for each j the code uses the best such prefix, so the best wrap is found.",
                    "Stopping <code>j</code> at 1 keeps the prefix non-empty and the two pieces disjoint; an empty prefix is just a normal subarray, already covered by Kadane.",
                    "Three linear passes give <strong>O(n)</strong> time, and the <code>right_max</code> array is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Kadane on 3, −1, −6, 4, 2: best = 6 (the run 4, 2).",
                        "Prefix sums 3, 2, −4, 0, 2, so right_max = [3, 3, 3, 3, 3].",
                        "j=4: suffix = 2, plus right_max[3] = 3 gives 5. best stays 6.",
                        "j=3: suffix = 6, plus right_max[2] = 3 gives 9. best = 9.",
                        "j=2: suffix = 0 → 3. j=1: suffix = −1 → 2. It returns <strong>9</strong> (4, 2 then wrap to 3).",
                    ],
                    [
                        "Kadane on −3, −2, −3: best = −2.",
                        "right_max = [−3, −3, −3].",
                        "j=2: suffix = −3, plus −3 gives −6. j=1: suffix = −5, plus −3 gives −8.",
                        "No wrap helps, so it returns <strong>-2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>right_max</code> hold a running maximum rather than the plain prefix sum?",
                     "For a suffix starting at <code>j</code>, any prefix ending before <code>j</code> may be used. The running maximum gives the best of those in one lookup."],
                    ["Why does the loop stop at <code>j = 1</code>?",
                     "At <code>j = 0</code> the suffix is the whole array and there is no room for a separate prefix. The whole array is a normal subarray, already counted by Kadane."],
                    ["Can the suffix and prefix overlap?",
                     "No. The prefix ends at index <code>j - 1</code> at the latest and the suffix starts at <code>j</code>, so together they use each element at most once."],
                ],
            },
            "Kadane for max and min together": {
                "idea": [
                    "A wrapping subarray is everything <em>except</em> a contiguous middle block. Its sum is <code>total - (middle block)</code>, which is largest when the middle block is the <strong>minimum subarray</strong>.",
                    "So run Kadane twice in the same loop: once for the maximum subarray, once for the minimum, and compare <code>best</code> with <code>total - worst</code>.",
                    "One special case: if every number is negative the minimum subarray is the whole array and <code>total - worst</code> is 0, the sum of an empty subarray, which is not allowed.",
                ],
                "steps": [
                    "Keep <code>total</code>, the running <code>cur_max</code>/<code>cur_min</code> and the overall <code>best</code>/<code>worst</code>.",
                    "For each <code>x</code>: add it to <code>total</code>.",
                    "<code>cur_max = max(x, cur_max + x)</code> and <code>cur_min = min(x, cur_min + x)</code>: extend the run ending here or start fresh at <code>x</code>.",
                    "Update <code>best</code> and <code>worst</code> from them.",
                    "If <code>best &lt; 0</code> every element is negative: return <code>best</code>. Otherwise return <code>max(best, total - worst)</code>.",
                ],
                "why": [
                    "Removing the minimum contiguous block leaves the maximum wrapping block, because <code>total</code> is fixed.",
                    "If <code>best &lt; 0</code>, all numbers are negative, the best answer is the largest single element, and the empty-complement case must be ignored.",
                    "One pass with a handful of variables: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "x=3: total 3, cur_max 3, cur_min 3, best 3, worst 3.",
                        "x=−1: total 2, cur_max 2, cur_min −1, worst −1.",
                        "x=−6: total −4, cur_max −4, cur_min −7, worst −7.",
                        "x=4: cur_max 4, best 4. x=2: total 2, cur_max 6, best 6.",
                        "best ≥ 0, so compare 6 with total − worst = 2 − (−7) = 9. It returns <strong>9</strong>.",
                    ],
                    [
                        "x=−3: total −3, best −3, worst −3.",
                        "x=−2: total −5, cur_max −2, best −2, cur_min −5, worst −5.",
                        "x=−3: total −8, cur_min −8, worst −8.",
                        "total − worst = 0 would mean taking nothing. best &lt; 0, so it returns <strong>-2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>best &lt; 0</code> be special-cased?",
                     "When all numbers are negative, <code>worst</code> equals <code>total</code> and <code>total - worst = 0</code>, the empty subarray. On [−3, −2, −3] that would return 0 instead of −2."],
                    ["Why does <code>cur_min</code> start at 0 rather than infinity?",
                     "<code>min(x, cur_min + x)</code> with <code>cur_min = 0</code> gives <code>x</code> on the first step, so 0 behaves as an empty run. The same holds for <code>cur_max</code>."],
                    ["Can <code>total - worst</code> still be the empty complement when <code>best &gt;= 0</code>?",
                     "Yes: on [−5, 1, −5] the minimum block is the whole array, so <code>total - worst = 0</code>. It does no harm, because then <code>best</code> (here 1) is at least 0 and <code>max</code> picks it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest turbulent subarray
    "longest-turbulent-subarray": {
        "examples": [
            {"call": "max_turbulence_size([4, 2, 5, 3, 3, 1, 6])", "expect": "4"},
            {"call": "max_turbulence_size([4, 8, 12, 16])", "expect": "2"},
        ],
        "approaches": {
            "Extend from every start": {
                "idea": [
                    "A turbulent run alternates: up, down, up, … or down, up, down, … with no equal neighbours.",
                    "Fix a start <code>i</code> and push the end <code>j</code> right while each new comparison is strict and points the other way from the previous one.",
                    "The first pair that breaks the pattern ends the run, because every longer subarray from <code>i</code> contains that broken pair.",
                ],
                "steps": [
                    "Set <code>best = 1</code>: any single element is turbulent.",
                    "For each start <code>i</code>, set <code>j = i + 1</code>.",
                    "While <code>j</code> is in range, <code>arr[j] != arr[j - 1]</code>, and either <code>j == i + 1</code> (the first pair has no previous direction) or the direction of <code>(arr[j-1], arr[j])</code> differs from <code>(arr[j-2], arr[j-1])</code>, advance <code>j</code>.",
                    "The run is <code>arr[i:j]</code>, so update <code>best = max(best, j - i)</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Every turbulent subarray starts at some <code>i</code> and is a prefix of the maximal run from <code>i</code>, so the longest one is found.",
                    "The comparison <code>(arr[j] &gt; arr[j - 1]) != (arr[j - 1] &gt; arr[j - 2])</code> is safe as a direction test because equal neighbours were already rejected.",
                    "Each start can scan to the end, so the time is <strong>O(n²)</strong>; only indices are stored, so space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "i=0: 4 &gt; 2, 2 &lt; 5, 5 &gt; 3, then 3 = 3 stops it. j = 4, length 4, best = 4.",
                        "i=1: 2, 5, 3 then the equal pair: length 3.",
                        "i=2: 5, 3 (length 2). i=3: the pair 3, 3 fails at once (length 1).",
                        "i=4: 3 &gt; 1, 1 &lt; 6: length 3. i=5: 2. i=6: 1.",
                        "It returns <strong>4</strong> ([4, 2, 5, 3]).",
                    ],
                    [
                        "i=0: 4 &lt; 8 is accepted as the first pair; 8 &lt; 12 goes the same way, so j stops at 2. Length 2.",
                        "i=1: 8, 12 then 12 &lt; 16 is the same direction. Length 2.",
                        "i=2: 12, 16. i=3: just 16.",
                        "It returns <strong>2</strong>: any two different neighbours are turbulent.",
                    ],
                ],
                "faq": [
                    ["Why is <code>j == i + 1</code> special?",
                     "The first pair in a run has nothing before it to alternate with, so it only needs to be unequal. Without the special case the code would compare with <code>arr[i - 1]</code>, which lies outside the run."],
                    ["Why can I stop at the first broken pair?",
                     "Any longer subarray from the same start still contains that pair, so it cannot be turbulent either."],
                    ["What does it return for <code>[9, 9]</code>?",
                     "1. The pair is equal, so every run has length 1."],
                ],
            },
            "DP: longest run ending here going up or down": {
                "idea": [
                    "Track two numbers for the run ending at the current element: <code>up</code> (the last step went up) and <code>down</code> (the last step went down).",
                    "A step up can only extend a run whose previous step went down, so the new <code>up</code> is the old <code>down + 1</code>. A step down mirrors that.",
                    "An equal pair breaks every run, so both reset to 1.",
                ],
                "steps": [
                    "Start <code>up = down = best = 1</code>.",
                    "Walk adjacent pairs <code>(a, b)</code>.",
                    "If <code>b &gt; a</code>: <code>up, down = down + 1, 1</code>.",
                    "If <code>b &lt; a</code>: <code>up, down = 1, up + 1</code>. The tuple assignment uses the old <code>up</code>.",
                    "If <code>b == a</code>: <code>up = down = 1</code>.",
                    "Record <code>best = max(best, up, down)</code> and return it.",
                ],
                "why": [
                    "Any turbulent run ending in an up-step is a run ending in a down-step one element earlier, plus this step, so the recurrence covers every run.",
                    "The longest turbulent subarray ends somewhere, and at that point <code>up</code> or <code>down</code> equals its length, so <code>best</code> catches it.",
                    "One pass with three variables: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "4→2 down: up 1, down 2. 2→5 up: up 3, down 1. best 3.",
                        "5→3 down: up 1, down 4. best 4.",
                        "3→3 equal: up = down = 1.",
                        "3→1 down: down 2. 1→6 up: up 3.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "4→8 up: up = down + 1 = 2, down 1. best 2.",
                        "8→12 up: up = old down + 1 = 2 again.",
                        "12→16 up: same, up 2.",
                        "Two ups in a row never chain, so it returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the update be a single tuple assignment?",
                     "<code>down = up + 1</code> needs the <em>old</em> <code>up</code>. Writing <code>up = 1</code> on a separate line first would make <code>down</code> always 2."],
                    ["Why reset the other counter to 1 instead of leaving it?",
                     "After a step up, no run can end here with a down-step, so the down-run is just this single element."],
                    ["Is this the same idea as Kadane?",
                     "In spirit, yes: each counter is the best run ending at the current index, and a broken pattern restarts it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ jump game
    "jump-game": {
        "examples": [
            {"call": "can_jump([2, 3, 1, 1, 4])", "expect": "True"},
            {"call": "can_jump([3, 2, 1, 0, 4])", "expect": "False"},
        ],
        "approaches": {
            "Try every jump recursively": {
                "idea": [
                    "From index <code>i</code> you may jump 1 to <code>nums[i]</code> steps. The direct question is: does any of those jumps lead to the end?",
                    "Recursion explores that tree of choices; trying the longest jump first tends to reach the end sooner.",
                ],
                "steps": [
                    "<code>go(i)</code> returns whether the last index can be reached from <code>i</code>.",
                    "If <code>i &gt;= len(nums) - 1</code>, the end is reached: return <code>True</code>.",
                    "Otherwise try <code>go(i + k)</code> for <code>k</code> from <code>nums[i]</code> down to 1.",
                    "<code>any(...)</code> stops at the first jump that succeeds.",
                    "A zero at <code>nums[i]</code> gives an empty range, so <code>any</code> returns <code>False</code>.",
                    "Return <code>go(0)</code>.",
                ],
                "why": [
                    "Every sequence of jumps is a path in the recursion tree, so if any path reaches the end it is found.",
                    "Without memoisation the same index can be explored again and again from different paths, which is <strong>O(2<sup>n</sup>)</strong> in the worst case.",
                    "The recursion stack is at most one frame per index, <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "go(0): nums[0] = 2, so try go(2) first.",
                        "go(2): nums[2] = 1, try go(3).",
                        "go(3): nums[3] = 1, try go(4).",
                        "go(4): 4 ≥ 4, the end. Every <code>any</code> on the way stops early: <strong>True</strong>.",
                    ],
                    [
                        "go(0): try go(3), go(2), go(1) in that order.",
                        "go(3): nums[3] = 0, no jumps, False.",
                        "go(2): only go(3), False again. go(1): go(3), then go(2) → go(3) once more.",
                        "go(3) is explored four times, a small taste of the blow-up.",
                        "Every branch dies on the 0: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why try the longest jump first?",
                     "It often reaches the end with fewer calls. Correctness does not depend on the order, only speed."],
                    ["Why <code>i &gt;= len(nums) - 1</code> and not <code>==</code>?",
                     "A jump may overshoot the last index. Landing past it still means the end was reachable, because a shorter jump would land exactly on it."],
                    ["How would I make this polynomial?",
                     "Memoise <code>go</code> with <code>@cache</code>. Each index is then solved once, with up to n jumps tried, which is the O(n²) DP."],
                ],
            },
            "DP: which indices can reach the end": {
                "idea": [
                    "Call an index <strong>good</strong> if the end can be reached from it. The last index is good by definition.",
                    "Index <code>i</code> is good exactly when one of the indices it can jump to is good, and all of those lie to its right.",
                    "So fill <code>good</code> from right to left; every answer needed is already known.",
                ],
                "steps": [
                    "Create <code>good = [False] * n</code> and set <code>good[-1] = True</code>.",
                    "Loop <code>i</code> from n − 2 down to 0.",
                    "Set <code>good[i] = any(good[j] ...)</code> for <code>j</code> in <code>i + 1 .. min(n, i + nums[i] + 1) - 1</code>.",
                    "The <code>min</code> clips jumps that would run past the array.",
                    "Return <code>good[0]</code>.",
                ],
                "why": [
                    "By induction from the right: when <code>i</code> is processed, every <code>good[j]</code> with <code>j &gt; i</code> is final, so <code>good[i]</code> is correct.",
                    "Each index scans up to <code>nums[i]</code> targets, so the time is <strong>O(n²)</strong> in the worst case.",
                    "The <code>good</code> array is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "good[4] = True.",
                        "i=3: can reach 4, good. i=2: can reach 3, good.",
                        "i=1: nums[1] = 3 reaches 2, 3, 4, all good.",
                        "i=0: reaches 1 and 2, good.",
                        "good = [T, T, T, T, T], so it returns <strong>True</strong>.",
                    ],
                    [
                        "good[4] = True.",
                        "i=3: nums[3] = 0, empty range, False.",
                        "i=2: reaches only 3, False. i=1: reaches 2, 3, False.",
                        "i=0: reaches 1, 2, 3, all False.",
                        "good = [F, F, F, F, T], so it returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why go right to left?",
                     "Each index depends only on indices to its right. Processing them first means every lookup is already final."],
                    ["Why <code>min(n, i + nums[i] + 1)</code>?",
                     "Without it the range could run past the end of <code>good</code> and raise an IndexError."],
                    ["How does this lead to the greedy?",
                     "Only the leftmost good index to the right of <code>i</code> matters. Keeping just that one index instead of the whole array gives the backward greedy."],
                ],
            },
            "Greedy: pull the goal backwards": {
                "idea": [
                    "Keep <code>goal</code>: the leftmost index known to reach the end. At first it is the last index itself.",
                    "Walking left, if <code>i</code> can jump at least to <code>goal</code>, then <code>i</code> reaches the end too, so the goal moves to <code>i</code>.",
                    "At the end, the question is simply whether the goal was pulled all the way back to 0.",
                ],
                "steps": [
                    "Set <code>goal = len(nums) - 1</code>.",
                    "Loop <code>i</code> from <code>len(nums) - 2</code> down to 0.",
                    "If <code>i + nums[i] &gt;= goal</code>, set <code>goal = i</code>.",
                    "Otherwise leave the goal where it is.",
                    "Return <code>goal == 0</code>.",
                ],
                "why": [
                    "If <code>i</code> can reach <code>goal</code>, it can land on it exactly (jumps may be shorter than the maximum), and from there reach the end.",
                    "If <code>i</code> cannot reach the leftmost good index, it cannot reach any good index, because all others lie further right.",
                    "One backwards pass with one variable: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "goal = 4.",
                        "i=3: 3 + 1 = 4 ≥ 4, goal = 3.",
                        "i=2: 2 + 1 = 3 ≥ 3, goal = 2.",
                        "i=1: 1 + 3 = 4 ≥ 2, goal = 1. i=0: 0 + 2 ≥ 1, goal = 0.",
                        "goal == 0: <strong>True</strong>.",
                    ],
                    [
                        "goal = 4.",
                        "i=3: 3 + 0 = 3 &lt; 4, goal stays 4.",
                        "i=2: 2 + 1 = 3 &lt; 4. i=1: 1 + 2 = 3 &lt; 4.",
                        "i=0: 0 + 3 = 3 &lt; 4. Everything stalls at index 3.",
                        "goal is still 4: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why may <code>i</code> overshoot the goal and still count?",
                     "A jump can be any length from 1 to <code>nums[i]</code>. If the maximum reaches past the goal, a shorter jump lands on it exactly."],
                    ["Why is only the leftmost good index kept?",
                     "It is the easiest one to reach from the left. If an index cannot reach it, every other good index is even further away."],
                    ["Can this give the number of jumps?",
                     "No. It answers only yes or no. Jump Game II needs a forward, level-by-level greedy."],
                ],
            },
            "Greedy: track the farthest reachable index": {
                "idea": [
                    "Walk forward keeping <code>reach</code>, the farthest index reachable using the indices seen so far.",
                    "Every index up to <code>reach</code> is reachable, because jumps can be shorter than their maximum.",
                    "If the walk ever arrives at an index beyond <code>reach</code>, there is a gap nobody can cross.",
                ],
                "steps": [
                    "Set <code>reach = 0</code>.",
                    "For each index <code>i</code> with jump length <code>jump</code>:",
                    "If <code>i &gt; reach</code>, return <code>False</code>: index <code>i</code> cannot be reached.",
                    "Otherwise extend <code>reach = max(reach, i + jump)</code>.",
                    "If the loop finishes, the last index was reachable: return <code>True</code>.",
                ],
                "why": [
                    "The reachable indices always form one block <code>0 .. reach</code>: any index inside it is reachable, and from it you can land anywhere up to <code>i + jump</code>.",
                    "So the first index past <code>reach</code> can never be reached, and neither can anything after it.",
                    "One pass with one variable: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: reach = max(0, 2) = 2.",
                        "i=1: 1 ≤ 2, reach = max(2, 4) = 4.",
                        "i=2, 3: reach stays 4.",
                        "i=4: 4 ≤ 4, reach = 8.",
                        "The loop ends without a gap: <strong>True</strong>.",
                    ],
                    [
                        "i=0: reach = 3.",
                        "i=1: reach = max(3, 3) = 3. i=2: still 3.",
                        "i=3: jump 0, reach stays 3.",
                        "i=4: 4 &gt; 3, a gap.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does every index up to <code>reach</code> count as reachable?",
                     "<code>reach</code> came from some reachable index <code>i</code> with <code>i + jump = reach</code>. From <code>i</code> any shorter jump is also allowed, so every index between them is reachable too."],
                    ["Could I return True as soon as <code>reach &gt;= n - 1</code>?",
                     "Yes, that is a harmless early exit. The plain version just runs to the end of the loop."],
                    ["What about <code>[0]</code>?",
                     "i=0 is not past reach 0, so the loop ends and it returns True: you start on the last index."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ jump game II
    "jump-game-ii": {
        "examples": [
            {"call": "jump([2, 3, 1, 1, 4])", "expect": "2"},
            {"call": "jump([1, 2, 1, 1, 1])", "expect": "3"},
        ],
        "approaches": {
            "DP: fewest jumps to each index": {
                "idea": [
                    "Let <code>jumps[j]</code> be the fewest jumps needed to land on index <code>j</code>. Index 0 needs none.",
                    "Every index <code>i</code> pushes its answer forward: each target <code>j</code> it can reach costs at most <code>jumps[i] + 1</code>.",
                    "Processing indices left to right means <code>jumps[i]</code> is final before it is pushed, because only earlier indices can reach it.",
                ],
                "steps": [
                    "Create <code>jumps = [0] + [inf] * (n - 1)</code>.",
                    "Loop <code>i</code> over every index.",
                    "For each <code>j</code> from <code>i + 1</code> to <code>min(n, i + nums[i] + 1) - 1</code>, set <code>jumps[j] = min(jumps[j], jumps[i] + 1)</code>.",
                    "Unreached indices stay at infinity, but the problem guarantees the end is reachable.",
                    "Return <code>jumps[-1]</code>.",
                ],
                "why": [
                    "Any optimal path's last jump comes from some <code>i &lt; j</code>, and that relaxation is applied, so <code>jumps[j]</code> ends at the true minimum.",
                    "Each index pushes to up to <code>nums[i]</code> targets, giving <strong>O(n²)</strong> time in the worst case.",
                    "The <code>jumps</code> array is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Start: [0, ∞, ∞, ∞, ∞].",
                        "i=0 (jump 2): indices 1, 2 get 1 → [0, 1, 1, ∞, ∞].",
                        "i=1 (jump 3): indices 2, 3, 4 get min(…, 2) → [0, 1, 1, 2, 2].",
                        "i=2, 3, 4: nothing improves.",
                        "It returns <strong>2</strong> (0 → 1 → 4).",
                    ],
                    [
                        "Start: [0, ∞, ∞, ∞, ∞].",
                        "i=0 (jump 1): index 1 gets 1.",
                        "i=1 (jump 2): indices 2, 3 get 2.",
                        "i=2: index 3 stays 2. i=3: index 4 gets 3.",
                        "It returns <strong>3</strong> (0 → 1 → 3 → 4).",
                    ],
                ],
                "faq": [
                    ["Why push forward instead of pulling from the left?",
                     "Either works. Pushing means each index's range is read once from <code>nums[i]</code>, while pulling would need to know which earlier indices reach <code>j</code>."],
                    ["Can <code>jumps[i]</code> still be infinity when <code>i</code> is processed?",
                     "Only if <code>i</code> is unreachable; then <code>inf + 1</code> is still infinity and changes nothing."],
                    ["Why is this not O(n · max jump) instead?",
                     "It is, really: the inner loop runs at most <code>nums[i]</code> times. In the worst case that is n, so it is quoted as O(n²)."],
                ],
            },
            "Greedy BFS over index ranges": {
                "idea": [
                    "Think of BFS: level 0 is index 0, level 1 is every index one jump can reach, and so on. Each level is a <strong>contiguous range</strong> of indices.",
                    "So there is no queue: just remember where the current level ends (<code>end</code>) and the farthest index any index in it can reach (<code>farthest</code>).",
                    "When the scan reaches <code>end</code>, the current level is used up, one more jump is needed, and the next level ends at <code>farthest</code>.",
                ],
                "steps": [
                    "Set <code>jumps = end = farthest = 0</code>.",
                    "Loop <code>i</code> from 0 to <code>len(nums) - 2</code> (the last index never needs to jump).",
                    "Update <code>farthest = max(farthest, i + nums[i])</code>.",
                    "If <code>i == end</code>, the level is exhausted: <code>jumps += 1</code> and <code>end = farthest</code>.",
                    "Return <code>jumps</code>.",
                ],
                "why": [
                    "Indices in the range for level k are exactly those reachable in k jumps and no fewer, so the level containing the last index is the minimum number of jumps.",
                    "The loop stops before the last index, so arriving exactly at it does not open a useless extra level.",
                    "Each index is scanned once: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: farthest = 2. i == end 0, so jumps = 1, end = 2.",
                        "i=1: farthest = 4.",
                        "i=2: farthest stays 4. i == end, so jumps = 2, end = 4.",
                        "i=3: farthest 4, i ≠ end. The loop stops before index 4.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "i=0: farthest = 1, end reached: jumps = 1, end = 1.",
                        "i=1: farthest = 3, end reached: jumps = 2, end = 3.",
                        "i=2: farthest stays 3.",
                        "i=3: farthest = 4, end reached: jumps = 3, end = 4.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why loop to <code>len(nums) - 1</code> and not over every index?",
                     "Standing on the last index needs no jump. Including it would add one when <code>i == end</code> lands there: on [2, 3, 1, 1, 4] the result would be 3 instead of 2, and [0] would give 1 instead of 0."],
                    ["Why is <code>farthest</code> updated before the <code>i == end</code> check?",
                     "Index <code>end</code> belongs to the current level, so its own jump must count towards the next level's boundary."],
                    ["Where is the greedy choice?",
                     "Each level jumps to the farthest boundary any of its indices allows. Reaching further with the same number of jumps can only help, never hurt."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ jump game VII
    "jump-game-vii": {
        "examples": [
            {"call": 'can_reach("011010", 2, 3)', "expect": "True"},
            {"call": 'can_reach("01101110", 2, 3)', "expect": "False"},
        ],
        "approaches": {
            "BFS, scanning each full range": {
                "idea": [
                    "Indices are nodes; from <code>i</code> you may move to any <code>j</code> in <code>[i + min_jump, i + max_jump]</code> with <code>s[j] == \"0\"</code>.",
                    "Reachability in a graph is plain BFS: start at index 0, and mark each newly reached index so it is queued only once.",
                ],
                "steps": [
                    "Start with <code>seen = {0}</code> and <code>queue = deque([0])</code>.",
                    "Pop <code>i</code> from the front of the queue.",
                    "Scan <code>j</code> from <code>i + min_jump</code> to <code>min(n - 1, i + max_jump)</code>.",
                    "Each <code>j</code> with <code>s[j] == \"0\"</code> that is not yet in <code>seen</code> is added to <code>seen</code> and queued.",
                    "When the queue empties, return <code>n - 1 in seen</code>.",
                ],
                "why": [
                    "BFS visits every index reachable from 0, so the last index is in <code>seen</code> exactly when it is reachable.",
                    "Each index is queued once, but each pop scans its whole range of up to <code>max_jump - min_jump + 1</code> indices, so the time is <strong>O(n · (maxJump − minJump))</strong>.",
                    "Overlapping ranges of neighbouring indices are rescanned again and again; that waste is what the next approach removes.",
                    "The set and the queue hold up to n indices: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 6. Pop 0: range [2, 3]. s[2] = '1', s[3] = '0', so seen = {0, 3}, queue [3].",
                        "Pop 3: range [5, 5]. s[5] = '0', seen = {0, 3, 5}, queue [5].",
                        "Pop 5: range [7, 5] is empty.",
                        "The queue is empty and 5 is in seen: <strong>True</strong>.",
                    ],
                    [
                        "n = 8. Pop 0: range [2, 3]. Only index 3 is '0', queue [3].",
                        "Pop 3: range [5, 6]. Both are '1'.",
                        "The queue is empty; seen = {0, 3}.",
                        "Index 7 was never reached: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>min(n - 1, i + max_jump)</code>?",
                     "It keeps <code>j</code> inside the string; indices past the end do not exist."],
                    ["Why mark an index as seen when it is queued, not when it is popped?",
                     "Marking on push stops the same index being queued many times by different sources before it is popped."],
                    ["Does the order of the queue matter here?",
                     "Not for correctness: only reachability is asked, so DFS would work too. BFS just makes the farthest-pointer trick in the next approach possible."],
                ],
            },
            "BFS that never rescans (farthest pointer)": {
                "idea": [
                    "Indices come off the BFS queue in increasing order, so their ranges <code>[i + min_jump, i + max_jump]</code> slide to the right.",
                    "Everything up to <code>farthest</code> (the right end of earlier ranges) has already been looked at, so each new scan can start at <code>farthest + 1</code>.",
                    "That way every index is scanned at most once in total.",
                ],
                "steps": [
                    "Start with <code>queue = deque([0])</code> and <code>farthest = 0</code>.",
                    "Pop <code>i</code>. Scan <code>j</code> from <code>max(i + min_jump, farthest + 1)</code> to <code>min(n - 1, i + max_jump)</code>.",
                    "If <code>s[j] == \"0\"</code>: return <code>True</code> if <code>j == n - 1</code>, otherwise queue <code>j</code>.",
                    "After the scan, set <code>farthest = max(farthest, i + max_jump)</code>.",
                    "If the queue empties, return <code>n == 1</code> (only a one-character string starts on its own end).",
                ],
                "why": [
                    "Queued indices increase, so each range ends no earlier than the previous one; skipping up to <code>farthest</code> only skips indices already examined.",
                    "No <code>seen</code> set is needed: an index is scanned once, so it is queued at most once.",
                    "Total scanning is <strong>O(n)</strong> time; the queue is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop 0: scan [2, 3]. Index 3 is '0' and not the end, queue [3]. farthest = 3.",
                        "Pop 3: scan from max(5, 4) = 5 to 5.",
                        "s[5] = '0' and 5 is the last index.",
                        "It returns <strong>True</strong> straight away.",
                    ],
                    [
                        "Pop 0: scan [2, 3], queue [3], farthest = 3.",
                        "Pop 3: scan [5, 6]; both are '1'. farthest = 6.",
                        "The queue is empty and n = 8 ≠ 1.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does it end with <code>return n == 1</code>?",
                     "The loop only returns True when it lands on the last index by a jump. If the string has one character you start on the end, which no jump would report."],
                    ["Why is it safe to skip indices up to <code>farthest</code>?",
                     "Each of them was in an earlier range and was already queued if it was a '0'. Rescanning could only find indices already handled."],
                    ["Why update <code>farthest</code> after the loop, not before?",
                     "The scan needs the old value to know where to start. Updating first would make the range empty."],
                ],
            },
            "DP with a sliding count of reachable sources": {
                "idea": [
                    "<code>ok[j]</code> is true when <code>s[j] == \"0\"</code> and some reachable index lies in <code>[j - max_jump, j - min_jump]</code>.",
                    "That window of sources slides right by one as <code>j</code> grows, so keep a running count <code>window</code> of reachable indices in it instead of rescanning it.",
                ],
                "steps": [
                    "Set <code>ok = [False] * n</code>, <code>ok[0] = True</code> and <code>window = 0</code>.",
                    "For each <code>j</code> from 1: if <code>j &gt;= min_jump</code>, index <code>j - min_jump</code> enters the window, so add <code>ok[j - min_jump]</code>.",
                    "If <code>j &gt; max_jump</code>, index <code>j - max_jump - 1</code> leaves the window, so subtract <code>ok[j - max_jump - 1]</code>.",
                    "Set <code>ok[j] = s[j] == \"0\" and window &gt; 0</code>.",
                    "Return <code>ok[-1]</code>.",
                ],
                "why": [
                    "After the two updates <code>window</code> counts exactly the reachable indices in <code>[j - max_jump, j - min_jump]</code>, the only places a jump to <code>j</code> can start.",
                    "Booleans add as 0 and 1, so the count stays exact.",
                    "Constant work per index: <strong>O(n)</strong> time, with the <code>ok</code> array as <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "j=1: window 0, s[1] = '1', ok False.",
                        "j=2: ok[0] enters, window 1, but s[2] = '1'.",
                        "j=3: ok[1] enters (0), window 1, s[3] = '0', ok[3] = True.",
                        "j=4: ok[2] enters, ok[0] leaves: window 0. j=5: ok[3] enters, ok[1] leaves: window 1, s[5] = '0'.",
                        "ok[5] = True: <strong>True</strong>.",
                    ],
                    [
                        "j=3: window 1 (index 0), ok[3] = True.",
                        "j=4: index 0 leaves, window 0.",
                        "j=5, 6: window 1 (index 3), but both are '1'.",
                        "j=7: index 3 leaves and index 5 (False) enters, window 0.",
                        "ok[7] = False: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the window for <code>j</code> run from <code>j - max_jump</code> to <code>j - min_jump</code>?",
                     "A jump from <code>i</code> lands in <code>[i + min_jump, i + max_jump]</code>. Solving for <code>i</code> given the landing spot <code>j</code> gives that range."],
                    ["Why the conditions <code>j &gt;= min_jump</code> and <code>j &gt; max_jump</code>?",
                     "They make sure the index entering or leaving exists (is ≥ 0). Before that there is nothing to add or remove."],
                    ["Is this the same as a prefix-sum approach?",
                     "Yes in effect: <code>window</code> is a difference of two prefix counts, maintained incrementally instead of stored."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ gas station
    "gas-station": {
        "examples": [
            {"call": "can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])", "expect": "3"},
            {"call": "can_complete_circuit([2, 3, 4], [3, 4, 3])", "expect": "-1"},
        ],
        "approaches": {
            "Simulate from every start": {
                "idea": [
                    "Try each station as the start and drive round, adding <code>gas[i] - cost[i]</code> to the tank at each stop.",
                    "If the tank ever goes negative, that start fails; if it survives all n legs, it is the answer.",
                ],
                "steps": [
                    "Loop <code>start</code> over every station with <code>tank = 0</code>.",
                    "For <code>k</code> from 0 to n − 1, visit <code>i = (start + k) % n</code> and add <code>gas[i] - cost[i]</code>.",
                    "If <code>tank &lt; 0</code>, <code>break</code>: the car cannot reach the next station.",
                    "The <code>for … else</code> branch runs only when no break happened: return <code>start</code>.",
                    "If every start breaks, return <code>-1</code>.",
                ],
                "why": [
                    "This is a direct simulation of the trip from every start, so it is correct by definition.",
                    "Each start can drive up to n legs: <strong>O(n²)</strong> time. A couple of counters: <strong>O(1)</strong> space.",
                    "It throws away everything learned when a start fails, which the one-pass version exploits.",
                ],
                "dry": [
                    [
                        "start 0: 1 − 3 = −2, fails at once.",
                        "start 1: −2 fails. start 2: −2 fails.",
                        "start 3: tank 3, 6, then station 0 → 4, station 1 → 2, station 2 → 0.",
                        "The tank never drops below 0, so it returns <strong>3</strong>.",
                    ],
                    [
                        "start 0: 2 − 3 = −1, fails.",
                        "start 1: 3 − 4 = −1, fails.",
                        "start 2: tank 1, 0, then −1 at station 1, fails.",
                        "It returns <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is a tank of exactly 0 allowed?",
                     "Arriving with an empty tank is fine; you refuel at the station. Only a negative tank means you ran out on the road."],
                    ["What does <code>for … else</code> do?",
                     "The <code>else</code> block runs when the loop finishes without <code>break</code>, which here means the full circuit succeeded."],
                    ["Could there be two valid starts?",
                     "The problem guarantees a unique answer when one exists, so returning the first success is correct."],
                ],
            },
            "One pass: restart after every failure": {
                "idea": [
                    "If the total gas is less than the total cost, no start can work. Otherwise a valid start exists.",
                    "Key fact: if starting at <code>start</code> runs dry at station <code>i</code>, then <strong>no</strong> station between <code>start</code> and <code>i</code> works either, so the next candidate is <code>i + 1</code>.",
                    "One left-to-right sweep therefore finds the only candidate left standing.",
                ],
                "steps": [
                    "If <code>sum(gas) &lt; sum(cost)</code>, return <code>-1</code>.",
                    "Set <code>start = tank = 0</code>.",
                    "For each station <code>i</code>, add <code>gas[i] - cost[i]</code> to <code>tank</code>.",
                    "If <code>tank &lt; 0</code>, rule out everything up to <code>i</code>: <code>start, tank = i + 1, 0</code>.",
                    "Return <code>start</code>.",
                ],
                "why": [
                    "Any station <code>s</code> between <code>start</code> and <code>i</code> was reached with a tank ≥ 0, so starting at <code>s</code> with an empty tank is no better, and it also runs dry by <code>i</code>.",
                    "The final <code>start</code> reaches the end of the array with a non-negative tank, and since the total surplus is ≥ 0, the deficit of the part before it is covered on the way round.",
                    "Two sums and one pass: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Totals 15 and 15: a start exists.",
                        "i=0: tank −2 → start 1, tank 0.",
                        "i=1: −2 → start 2. i=2: −2 → start 3.",
                        "i=3: tank 3. i=4: tank 6.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "sum(gas) = 9, sum(cost) = 10.",
                        "9 &lt; 10: there is not enough fuel in the whole circuit.",
                        "The loop never runs.",
                        "It returns <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the total check needed?",
                     "Without it the sweep always returns some index. On the second example it would return 2, even though no start works."],
                    ["Why never check the part of the trip that wraps round?",
                     "From <code>start</code> to the end the tank stays ≥ 0, and the surplus of the whole circuit is ≥ 0, so what is left is enough to cover the earlier part."],
                    ["Why reset <code>tank</code> to 0 at a restart?",
                     "The new candidate begins with an empty tank, exactly as the problem says."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ hand of straights
    "hand-of-straights": {
        "examples": [
            {"call": "is_n_straight_hand([1, 2, 3, 6, 2, 3, 4, 7, 8], 3)", "expect": "True"},
            {"call": "is_n_straight_hand([1, 1, 2, 3, 3, 4], 3)", "expect": "False"},
        ],
        "approaches": {
            "Sort, then build groups from the smallest card": {
                "idea": [
                    "The smallest card left has nothing below it, so it <strong>must</strong> start a group: <code>v, v + 1, …, v + k − 1</code>.",
                    "So repeatedly take the smallest remaining value and remove one straight starting there; if a card is missing, the hand cannot be split.",
                ],
                "steps": [
                    "If <code>len(hand) % k</code> is non-zero, return <code>False</code>.",
                    "Count cards with <code>Counter(hand)</code>.",
                    "Go through values <code>v</code> in sorted order. While <code>count[v] &gt; 0</code>, build one group from <code>v</code>.",
                    "For each <code>x</code> in <code>v .. v + k − 1</code>: if <code>count[x] == 0</code>, return <code>False</code>; otherwise decrement it.",
                    "If every value is used up, return <code>True</code>.",
                ],
                "why": [
                    "The smallest remaining card can only sit at the bottom of a group, so starting a group there is forced, not a guess.",
                    "Sorting the distinct values costs <strong>O(n log n)</strong>, and each group costs k steps: <strong>O(n log n + n · k)</strong> time in total.",
                    "The counter holds one entry per distinct value: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Counts: 1:1, 2:2, 3:2, 4:1, 6:1, 7:1, 8:1.",
                        "v=1: group 1, 2, 3. Now 2:1, 3:1.",
                        "v=2: group 2, 3, 4.",
                        "v=3, 4: counts are 0, skipped. v=6: group 6, 7, 8.",
                        "Every card is used: <strong>True</strong>.",
                    ],
                    [
                        "Counts: 1:2, 2:1, 3:2, 4:1.",
                        "v=1: group 1, 2, 3. Now 1:1, 2:0, 3:1.",
                        "v=1 again (count 1): x=2 has count 0.",
                        "The second 1 cannot start a straight: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>len(hand) % k</code> first?",
                     "If the size is not a multiple of k, equal groups are impossible. It also stops the loop doing work for nothing."],
                    ["Why can <code>count[x]</code> be looked up for values not in the hand?",
                     "A <code>Counter</code> returns 0 for missing keys, which correctly means that card is absent."],
                    ["Does the order of values matter?",
                     "Yes. Starting from a value that is not the smallest remaining could strand smaller cards. Sorting is what makes each choice forced."],
                ],
            },
            "Start whole batches of groups at once": {
                "idea": [
                    "If the smallest value <code>v</code> appears <code>c</code> times, all <code>c</code> copies must start groups at <code>v</code>.",
                    "So instead of building those groups one at a time, subtract <code>c</code> from each of <code>v .. v + k − 1</code> in one go.",
                ],
                "steps": [
                    "Return <code>False</code> if <code>len(hand) % k</code> is non-zero; count the cards.",
                    "Go through values <code>v</code> in sorted order and read <code>c = count[v]</code>.",
                    "If <code>c == 0</code>, these cards were used by earlier groups: skip.",
                    "For each <code>x</code> in <code>v .. v + k − 1</code>: if <code>count[x] &lt; c</code>, return <code>False</code>; otherwise subtract <code>c</code>.",
                    "Return <code>True</code> at the end.",
                ],
                "why": [
                    "Every remaining copy of the smallest value must begin a group, so all <code>c</code> groups are forced, and each needs one copy of every value above it.",
                    "Every batch removes at least k cards, so there are at most n / k batches of k steps each, which is O(n); the sort dominates, giving <strong>O(n log n)</strong> time.",
                    "The counter is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "v=1, c=1: subtract 1 from 1, 2, 3.",
                        "v=2, c=1: subtract 1 from 2, 3, 4.",
                        "v=3, v=4: c = 0, skipped.",
                        "v=6, c=1: subtract from 6, 7, 8. v=7, 8 skipped.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "Counts: 1:2, 2:1, 3:2, 4:1.",
                        "v=1, c=2: two groups must start at 1.",
                        "x=1 has 2, fine. x=2 has only 1 &lt; 2.",
                        "It returns <strong>False</strong> without building anything.",
                    ],
                ],
                "faq": [
                    ["Why read <code>c</code> before the inner loop?",
                     "The loop changes <code>count[v]</code> on its first step. Reading it first fixes how many groups start at <code>v</code>."],
                    ["How is this faster than the first approach?",
                     "The first one runs the k-step loop once per group; this one once per distinct starting value, removing the n · k term."],
                    ["What if values have gaps, like 1 and 3?",
                     "When <code>v = 1</code> needs a 2, <code>count[2]</code> is 0, which is less than <code>c</code>, so it returns False."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ dota2 senate
    "dota2-senate": {
        "examples": [
            {"call": 'predict_party_victory("DDRRR")', "expect": '"Dire"'},
            {"call": 'predict_party_victory("DRRDR")', "expect": '"Radiant"'},
        ],
        "approaches": {
            "Simulate with a list and deletions": {
                "idea": [
                    "On a senator's turn, the best move is to ban the <strong>next</strong> opposing senator in the round order, since that one would act soonest against your party.",
                    "Simulate the rounds directly on a list: the current senator deletes the first opponent after them, wrapping round the circle.",
                ],
                "steps": [
                    "Copy the string into a list <code>s</code> and set <code>i = 0</code>.",
                    "While both parties remain (<code>len(set(s)) &gt; 1</code>), let <code>me = s[i]</code>.",
                    "Move <code>j</code> forward from <code>i + 1</code>, wrapping with <code>% len(s)</code>, until <code>s[j]</code> is an opponent; delete it.",
                    "If the deleted index was before <code>i</code>, shift <code>i</code> back one, because the list moved left.",
                    "Advance <code>i = (i + 1) % len(s)</code> to the next senator.",
                    "Return the party of the survivors.",
                ],
                "why": [
                    "Banning the nearest upcoming opponent removes the biggest immediate threat; banning someone further away lets a nearer opponent act first.",
                    "Each ban scans and deletes in a list, both <strong>O(n)</strong>, and there are fewer than n bans: <strong>O(n²)</strong> time.",
                    "The list copy is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "DDRRR, i=0 (D): bans the R at 2 → DDRR.",
                        "i=1 (D): bans the R at 2 → DDR.",
                        "i=2 (R): wraps and bans the D at 0 → DR; i shifts back, then wraps to 0.",
                        "i=0 (D): bans the R → D.",
                        "Only Dire is left: <strong>\"Dire\"</strong>.",
                    ],
                    [
                        "DRRDR, i=0 (D): bans the R at 1 → DRDR.",
                        "i=1 (R): bans the D at 2 → DRR.",
                        "i=2 (R): wraps and bans the D at 0 → RR.",
                        "Only Radiant is left: <strong>\"Radiant\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>i</code> move back when <code>j &lt; i</code>?",
                     "Deleting an element before <code>i</code> shifts everything after it one place left, so the current senator now sits at <code>i - 1</code>."],
                    ["Why does the majority not always win?",
                     "Order matters: in DDRRR the two Ds act first and ban two Rs before any R gets a turn."],
                    ["Why is <code>len(set(s))</code> slow here?",
                     "It rebuilds a set every round, O(n) each time. It does not change the O(n²) total but adds a constant factor."],
                ],
            },
            "Two queues of turn indices": {
                "idea": [
                    "Keep each party's senators as a queue of their turn numbers. The front of each queue is the next one of that party to act.",
                    "Compare the two fronts: the one with the smaller turn acts first and bans the other.",
                    "The winner acts again next round, so it rejoins its queue with turn <code>+ n</code>.",
                ],
                "steps": [
                    "Build <code>r</code> and <code>d</code>, deques of the indices of R and D senators.",
                    "While both are non-empty, pop <code>a</code> from <code>r</code> and <code>b</code> from <code>d</code>.",
                    "If <code>a &lt; b</code>, R acts first: the D is banned and <code>a + n</code> goes to the back of <code>r</code>.",
                    "Otherwise D wins the duel and <code>b + n</code> goes to the back of <code>d</code>.",
                    "Return \"Radiant\" if <code>r</code> is non-empty, else \"Dire\".",
                ],
                "why": [
                    "The senator with the smaller turn acts before the other, and the greedy best ban is the next opponent to act, which is the other queue's front.",
                    "Adding n puts the survivor after everyone still waiting in this round, which is exactly when it acts again.",
                    "Each duel removes one senator, so there are at most n duels of O(1) each: <strong>O(n)</strong> time and <strong>O(n)</strong> space for the queues.",
                ],
                "dry": [
                    [
                        "r = [2, 3, 4], d = [0, 1], n = 5.",
                        "2 vs 0: D first, d = [1, 5]. 3 vs 1: D first, d = [5, 6].",
                        "4 vs 5: R first, r = [9].",
                        "9 vs 6: D first, d = [11], r is empty.",
                        "It returns <strong>\"Dire\"</strong>.",
                    ],
                    [
                        "r = [1, 2, 4], d = [0, 3].",
                        "1 vs 0: D first, d = [3, 5].",
                        "2 vs 3: R first, r = [4, 7]. 4 vs 5: R first, r = [7, 9].",
                        "d is empty: <strong>\"Radiant\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why add <code>n</code> and not 1?",
                     "The survivor's next turn comes after every senator still waiting in this round, whose turns are all below <code>a + n</code>. Adding 1 could put it ahead of them."],
                    ["Why can each duel be resolved by the two fronts only?",
                     "The earlier of the two fronts is the very next senator to act, and their best ban is the earliest opponent, which is the other front."],
                    ["Is the answer ever a tie?",
                     "No. Each duel removes one senator, so eventually one queue is empty."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ merge triplets
    "merge-triplets": {
        "examples": [
            {"call": "merge_triplets([[2, 5, 3], [1, 8, 4], [1, 7, 5]], [2, 7, 5])", "expect": "True"},
            {"call": "merge_triplets([[3, 4, 5], [4, 5, 6]], [3, 2, 5])", "expect": "False"},
        ],
        "approaches": {
            "Try every subset": {
                "idea": [
                    "Merging any number of triplets gives their coordinate-wise maximum, and the order of merges does not matter.",
                    "So the question is whether <strong>some subset</strong> of triplets has coordinate-wise max equal to <code>target</code>; try them all.",
                ],
                "steps": [
                    "Loop the subset size <code>r</code> from 1 to the number of triplets.",
                    "For each <code>combo</code> in <code>itertools.combinations(triplets, r)</code>:",
                    "Compute <code>[max(t[i] for t in combo) for i in range(3)]</code>.",
                    "If it equals <code>list(target)</code>, return <code>True</code>.",
                    "If no subset matches, return <code>False</code>.",
                ],
                "why": [
                    "Any sequence of merge operations produces the max over the triplets used, and every subset is tried, so a valid one cannot be missed.",
                    "There are 2<sup>n</sup> − 1 non-empty subsets, each costing up to O(n) to merge: <strong>O(2<sup>n</sup>)</strong> subsets, exponential time.",
                    "<code>combinations</code> yields one tuple at a time, so space is <strong>O(n)</strong> for the current combo.",
                ],
                "dry": [
                    [
                        "Size 1: [2, 5, 3], [1, 8, 4], [1, 7, 5]; none equals [2, 7, 5].",
                        "Size 2: [2, 5, 3] + [1, 8, 4] → [2, 8, 4]. No.",
                        "[2, 5, 3] + [1, 7, 5] → [2, 7, 5]. Match.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "Size 1: [3, 4, 5] and [4, 5, 6]; neither is [3, 2, 5].",
                        "Size 2: both → [4, 5, 6].",
                        "Every triplet has a middle value above 2, so no subset can match.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can merges be treated as a subset?",
                     "Each merge takes coordinate-wise maxima, and max is associative and commutative, so the result depends only on which triplets were used."],
                    ["Why <code>list(target)</code>?",
                     "The comprehension builds a list; converting <code>target</code> makes the comparison work even if it was passed as a tuple."],
                    ["How large can n be for this?",
                     "Only about 20. It exists to check the linear greedy."],
                ],
            },
            "Keep the safe triplets, check each coordinate is hit": {
                "idea": [
                    "A triplet with any coordinate <strong>above</strong> the target can never be used: a max can only go up, so that coordinate would overshoot forever.",
                    "Every other triplet is safe: merging all of them never overshoots. Merging more safe triplets can only help.",
                    "So the answer is yes exactly when, among the safe triplets, each of the three coordinates is matched by at least one of them.",
                ],
                "steps": [
                    "Start with an empty set <code>hit</code> of matched coordinates.",
                    "For each triplet <code>t</code>, skip it unless <code>t[i] &lt;= target[i]</code> for all three <code>i</code>.",
                    "For a safe triplet, add every <code>i</code> with <code>t[i] == target[i]</code> to <code>hit</code>.",
                    "Return <code>len(hit) == 3</code>.",
                ],
                "why": [
                    "Merging all safe triplets gives a max that is ≤ target in every coordinate, and equals it in coordinate <code>i</code> exactly when some safe triplet matches it there.",
                    "Unsafe triplets can never appear in a valid merge, so ignoring them loses nothing.",
                    "One pass over the triplets: <strong>O(n)</strong> time; <code>hit</code> has at most 3 entries: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "[2, 5, 3]: safe; coordinate 0 matches. hit = {0}.",
                        "[1, 8, 4]: 8 &gt; 7, unsafe, skipped.",
                        "[1, 7, 5]: safe; coordinates 1 and 2 match. hit = {0, 1, 2}.",
                        "All three coordinates are hit: <strong>True</strong>.",
                    ],
                    [
                        "[3, 4, 5]: 4 &gt; 2, unsafe.",
                        "[4, 5, 6]: unsafe in every coordinate.",
                        "hit stays empty.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why may every safe triplet be merged without harm?",
                     "Each safe triplet is ≤ target in every coordinate, so their max is too. Adding one can only raise coordinates towards the target, never past it."],
                    ["Does it matter that different triplets hit different coordinates?",
                     "No. Merging them combines their hits, which is why a set of coordinates is enough."],
                    ["What if one safe triplet equals the target exactly?",
                     "It adds all three coordinates at once, and the answer is True."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ partition labels
    "partition-labels": {
        "examples": [
            {"call": 'partition_labels("abacdcdef")', "expect": "[3, 4, 1, 1]"},
            {"call": 'partition_labels("eccbbbbdec")', "expect": "[10]"},
        ],
        "approaches": {
            "Letter spans as intervals, then merge": {
                "idea": [
                    "Every letter must sit in one part, so the part must cover the letter's whole span, from its first to its last occurrence.",
                    "Spans that overlap must share a part. That is exactly <strong>merge intervals</strong>: the merged blocks are the parts.",
                ],
                "steps": [
                    "Record <code>first[ch]</code> and <code>last[ch]</code> for every letter in one scan.",
                    "Sort the spans <code>(first, last)</code> by start.",
                    "Keep the current block <code>start .. end</code>, starting from the first span.",
                    "For each next span <code>(a, b)</code>: if <code>a &gt; end</code>, close the block, append <code>end - start + 1</code> and set <code>start = a</code>; in every case, <code>end = max(end, b)</code>.",
                    "Append the last block's size and return <code>sizes</code>.",
                ],
                "why": [
                    "Merged blocks are the smallest unions of overlapping spans, so each part is as small as possible, which gives the most parts.",
                    "The scan is O(n); there are at most Σ spans, so sorting them is O(Σ log Σ), a constant for a fixed alphabet: <strong>O(n)</strong> time.",
                    "The two dictionaries and the span list are <strong>O(Σ)</strong> space.",
                ],
                "dry": [
                    [
                        "Spans: a (0, 2), b (1, 1), c (3, 5), d (4, 6), e (7, 7), f (8, 8).",
                        "Block 0..2; b (1, 1) is inside.",
                        "c starts at 3 &gt; 2: close size 3. Block 3..5, then d extends it to 6.",
                        "e at 7 &gt; 6: close size 4. f at 8 &gt; 7: close size 1.",
                        "The last block adds 1: <strong>[3, 4, 1, 1]</strong>.",
                    ],
                    [
                        "Spans: e (0, 8), c (1, 9), b (3, 6), d (7, 7).",
                        "Block 0..8, then c extends it to 9.",
                        "b and d lie inside 0..9.",
                        "One block of size 10: <strong>[10]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort the spans?",
                     "Merging works left to right only if spans arrive in order of start. Dictionary order is by first appearance, which happens to be sorted already, but sorting makes it explicit."],
                    ["Why does <code>end = max(end, b)</code> run even after closing a block?",
                     "After a close, <code>end</code> is the old block's end and <code>b</code> is larger, so the max simply starts the new block at <code>b</code>."],
                    ["Is this the same answer as the one-sweep version?",
                     "Yes. The sweep does the same merge without building the spans."],
                ],
            },
            "One sweep extending the current part's end": {
                "idea": [
                    "Record where each letter appears last. Walking left to right, the current part must stretch at least to the last occurrence of every letter seen in it.",
                    "When the index catches up with that stretch, no letter inside the part continues past here, so it is safe to cut.",
                ],
                "steps": [
                    "Build <code>last = {ch: i}</code>; later indices overwrite earlier ones.",
                    "Set <code>start = end = 0</code> and <code>sizes = []</code>.",
                    "For each <code>i, ch</code>: <code>end = max(end, last[ch])</code>.",
                    "If <code>i == end</code>, append <code>end - start + 1</code> and set <code>start = i + 1</code>.",
                    "Return <code>sizes</code>.",
                ],
                "why": [
                    "A cut at <code>i</code> is valid exactly when every letter in <code>s[start..i]</code> ends by <code>i</code>, which is <code>i == end</code>.",
                    "Cutting at the first valid point makes each part as short as possible, so the number of parts is maximal.",
                    "Two linear scans: <strong>O(n)</strong> time; <code>last</code> has one entry per letter: <strong>O(Σ)</strong> space.",
                ],
                "dry": [
                    [
                        "last: a 2, b 1, c 5, d 6, e 7, f 8.",
                        "i=0 a: end 2. i=1 b: end 2. i=2: i == end, cut size 3.",
                        "i=3 c: end 5. i=4 d: end 6. i=5 c: still 6. i=6: cut size 4.",
                        "i=7 e: end 7, cut size 1. i=8 f: cut size 1.",
                        "It returns <strong>[3, 4, 1, 1]</strong>.",
                    ],
                    [
                        "last: e 8, c 9, b 6, d 7.",
                        "i=0 e: end 8. i=1 c: end 9.",
                        "i=2..8: end stays 9, so no cut.",
                        "i=9: i == end, cut size 10: <strong>[10]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>max(end, last[ch])</code> and not just <code>last[ch]</code>?",
                     "An earlier letter in the part may end later than the current one. Taking only <code>last[ch]</code> could shrink the end and cut too early."],
                    ["Why <code>end - start + 1</code>?",
                     "The part is the closed range <code>start .. end</code>, which holds that many characters."],
                    ["Does the alphabet size matter?",
                     "Only for space: <code>last</code> holds at most Σ entries, 26 for lowercase letters."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid parenthesis string
    "valid-parenthesis-string": {
        "examples": [
            {"call": 'check_valid_string("((*)")', "expect": "True"},
            {"call": 'check_valid_string("*(")', "expect": "False"},
        ],
        "approaches": {
            "Try every assignment of the stars": {
                "idea": [
                    "Each <code>*</code> can be <code>(</code>, <code>)</code> or nothing. Try all three and see whether any choice gives a balanced string.",
                    "Track only <code>open_</code>, the number of unmatched <code>(</code> so far: it must never go negative and must end at 0.",
                ],
                "steps": [
                    "<code>go(i, open_)</code>: if <code>open_ &lt; 0</code>, a <code>)</code> had no partner: return <code>False</code>.",
                    "If <code>i == len(s)</code>, return <code>open_ == 0</code>.",
                    "A <code>(</code> recurses with <code>open_ + 1</code>; a <code>)</code> with <code>open_ - 1</code>.",
                    "A <code>*</code> tries <code>open_ + 1</code>, then <code>open_ - 1</code>, then <code>open_</code>, stopping at the first success.",
                    "Return <code>go(0, 0)</code>.",
                ],
                "why": [
                    "A string of brackets is balanced exactly when the running count never dips below 0 and ends at 0; every star assignment is tried against that test.",
                    "With k stars there are 3<sup>k</sup> assignments, each checked in O(n): <strong>O(3<sup>k</sup> · n)</strong> time.",
                    "The recursion is one level per character: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "go(0,0) → '(' → go(1,1) → '(' → go(2,2).",
                        "'*' as '(': go(3,3) → ')' → go(4,2): end with 2 open, False.",
                        "'*' as ')': go(3,1) → ')' → go(4,0): end with 0 open.",
                        "Seven calls in total: <strong>True</strong>.",
                    ],
                    [
                        "go(0,0): '*' as '(' → go(1,1) → '(' → go(2,2), ends with 2 open.",
                        "'*' as ')' → go(1,−1): negative, False.",
                        "'*' as nothing → go(1,0) → go(2,1), ends with 1 open.",
                        "Every choice fails: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>open_ &lt; 0</code> before the end of the string?",
                     "A <code>)</code> that closes nothing can never be fixed by later characters, so that branch can stop at once."],
                    ["Why only count opens rather than keep a stack?",
                     "There is a single bracket type, so the only thing that matters is how many are still open."],
                    ["Why does the order of the three star choices not matter?",
                     "<code>or</code> returns True if any branch succeeds; the order only changes how soon it is found."],
                ],
            },
            "DP over (index, open count)": {
                "idea": [
                    "The recursion's answer depends only on <code>(i, open_)</code>, and many star assignments reach the same pair.",
                    "Caching <code>go</code> with <code>@cache</code> solves each pair once, turning 3<sup>k</sup> paths into at most n² states.",
                ],
                "steps": [
                    "Same function as the brute force: <code>go(i, open_)</code> with the negative and end-of-string checks.",
                    "<code>(</code> and <code>)</code> move to <code>open_ ± 1</code>.",
                    "<code>*</code> tries all three options.",
                    "<code>@cache</code> stores each <code>(i, open_)</code> result, so a repeated pair returns immediately.",
                    "Return <code>go(0, 0)</code>.",
                ],
                "why": [
                    "The cached result is exactly what the recursion would compute, so correctness is unchanged.",
                    "<code>i</code> ranges over n + 1 values and <code>open_</code> over at most n + 1, so there are <strong>O(n²)</strong> states with O(1) work each: <strong>O(n²)</strong> time.",
                    "The cache holds up to <strong>O(n²)</strong> entries.",
                ],
                "dry": [
                    [
                        "go(0,0) → go(1,1) → go(2,2).",
                        "'*' as '(': go(3,3) → go(4,2), False.",
                        "'*' as ')': go(3,1) → go(4,0), True.",
                        "No pair repeats on this input, so the calls match the brute force: <strong>True</strong>.",
                    ],
                    [
                        "go(0,0): go(1,1) → go(2,2) False.",
                        "go(1,−1) False.",
                        "go(1,0) → go(2,1) False.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["When does the cache actually save work?",
                     "With several stars, different assignments reach the same <code>(i, open_)</code>, e.g. '(' then ')' and ')' then '(' both leave the count unchanged."],
                    ["Can <code>open_</code> exceed n?",
                     "No. It goes up by at most one per character, so it stays between 0 and n on any branch that is still alive."],
                    ["Is O(n²) good enough?",
                     "For interviews it is a fine middle step, but the range greedy solves it in O(n) time and O(1) space."],
                ],
            },
            "Two stacks of indices": {
                "idea": [
                    "Match each <code>)</code> with an unmatched <code>(</code> if possible, else with a <code>*</code>. Using a real <code>(</code> first saves stars, which are more flexible.",
                    "Leftover <code>(</code> must then be closed by stars that come <strong>after</strong> them, so store indices, not counts.",
                ],
                "steps": [
                    "Keep <code>opens</code> and <code>stars</code>, stacks of indices.",
                    "<code>(</code> pushes onto <code>opens</code>; <code>*</code> pushes onto <code>stars</code>.",
                    "<code>)</code> pops <code>opens</code> if non-empty, else pops <code>stars</code>, else returns <code>False</code>.",
                    "Afterwards, pair the latest open with the latest star: if the open's index is larger, the star is before it and cannot close it: return <code>False</code>.",
                    "Return <code>not opens</code>: every open must be matched; spare stars become empty.",
                ],
                "why": [
                    "Popping the most recent open for a <code>)</code> is always safe; using a star only when no open is left keeps as many stars as possible.",
                    "In the final phase, pairing from the top of both stacks matches each open with the latest star, the best chance of being after it.",
                    "Every index is pushed and popped at most once: <strong>O(n)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0, 1: opens = [0, 1].",
                        "i=2 '*': stars = [2].",
                        "i=3 ')': pops open 1, opens = [0].",
                        "Final phase: open 0 vs star 2, 0 &lt; 2, fine. opens is empty: <strong>True</strong>.",
                    ],
                    [
                        "i=0 '*': stars = [0].",
                        "i=1 '(': opens = [1].",
                        "Final phase: open 1 vs star 0.",
                        "1 &gt; 0, the star comes before the '(': <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why prefer an open bracket over a star when matching ')'?",
                     "A star can later serve as '(' or ')' or nothing, so it is the more valuable one to keep."],
                    ["Why compare indices in the final phase?",
                     "A star can only close an open bracket that comes before it. In \"*(\" there is a star and an open, but in the wrong order."],
                    ["Why <code>return not opens</code> rather than checking stars too?",
                     "Leftover stars can be treated as empty strings, so only leftover open brackets are a problem."],
                ],
            },
            "Greedy range of possible open counts": {
                "idea": [
                    "Instead of fixing what each star is, track the <strong>range</strong> of open counts that some assignment could give: <code>lo</code> to <code>hi</code>.",
                    "<code>(</code> raises both ends, <code>)</code> lowers both, and <code>*</code> widens the range by one each way.",
                    "If even <code>hi</code> drops below 0, there are too many ')'. At the end, the string is valid when 0 is in the range, i.e. <code>lo == 0</code>.",
                ],
                "steps": [
                    "Start <code>lo = hi = 0</code>.",
                    "'(': both + 1. ')': both − 1. '*': <code>lo - 1</code>, <code>hi + 1</code>.",
                    "If <code>hi &lt; 0</code>, return <code>False</code>.",
                    "Clamp <code>lo = max(lo, 0)</code>: a negative count is not a real option.",
                    "Return <code>lo == 0</code> after the scan.",
                ],
                "why": [
                    "Every count between <code>lo</code> and <code>hi</code> is achievable, because each star can shift the count by one in either direction or not at all.",
                    "<code>hi</code> is the most opens any assignment could have; if it is negative, no assignment survives.",
                    "One pass with two integers: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "'(': lo 1, hi 1. '(': lo 2, hi 2.",
                        "'*': lo 1, hi 3.",
                        "')': lo 0, hi 2.",
                        "lo == 0: <strong>True</strong>.",
                    ],
                    [
                        "'*': lo −1 → clamped to 0, hi 1.",
                        "'(': lo 1, hi 2.",
                        "The scan ends with lo = 1: at least one '(' is always left open.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why clamp <code>lo</code> at 0?",
                     "A count below 0 means a ')' without a partner, which is never allowed. Clamping drops those impossible choices while keeping the valid ones."],
                    ["Why return <code>lo == 0</code> and not <code>lo &lt;= 0 &lt;= hi</code>?",
                     "After clamping, <code>lo</code> is never negative, so 0 is in the range exactly when <code>lo == 0</code>."],
                    ["How does this catch \"*(\" when no ')' appears?",
                     "The '(' after the star lifts <code>lo</code> to 1, and nothing later lowers it, so the final check fails."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ candy
    "candy": {
        "examples": [
            {"call": "candy([1, 2, 3, 2, 1, 0])", "expect": "13"},
            {"call": "candy([1, 2, 2, 1])", "expect": "6"},
        ],
        "approaches": {
            "Relax until stable": {
                "idea": [
                    "Start everyone at 1 candy. Whenever a child has a higher rating than a neighbour but not more candy, give them one more than that neighbour.",
                    "Repeat full passes until a pass changes nothing; then every rule holds.",
                ],
                "steps": [
                    "Set <code>c = [1] * n</code> and <code>changed = True</code>.",
                    "While <code>changed</code>: reset it to <code>False</code> and scan <code>i</code> from left to right.",
                    "If <code>ratings[i] &gt; ratings[i - 1]</code> and <code>c[i] &lt;= c[i - 1]</code>, set <code>c[i] = c[i - 1] + 1</code>.",
                    "If <code>ratings[i] &gt; ratings[i + 1]</code> and <code>c[i] &lt;= c[i + 1]</code>, set <code>c[i] = c[i + 1] + 1</code>.",
                    "Any fix sets <code>changed = True</code>. Return <code>sum(c)</code>.",
                ],
                "why": [
                    "Values only grow, and each raise is the smallest that fixes a broken rule, so the stable result is the minimum valid assignment.",
                    "A long decreasing run needs about one pass per element to push its values left, so up to n passes of n steps: <strong>O(n²)</strong> time.",
                    "The candy array is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pass 1: c becomes [1, 2, 3, 2, 2, 1].",
                        "Pass 2: c becomes [1, 2, 3, 3, 2, 1].",
                        "Pass 3: the peak must beat 3: c = [1, 2, 4, 3, 2, 1].",
                        "Pass 4 changes nothing.",
                        "Sum: <strong>13</strong>.",
                    ],
                    [
                        "Pass 1: index 1 beats index 0 → 2; index 2 beats index 3 → 2. c = [1, 2, 2, 1].",
                        "The two equal ratings impose nothing on each other.",
                        "Pass 2 changes nothing.",
                        "Sum: <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the passes not stop after one?",
                     "A fix on the right of a descending run raises an element the scan has already passed; only the next pass carries it further left."],
                    ["Do equal ratings need equal candy?",
                     "No. The rule only applies to strictly higher ratings, so equal neighbours can get any amounts."],
                    ["Why does it give the minimum and not just a valid answer?",
                     "Each raise is forced by a rule and goes up by the least possible amount, so no candy is ever handed out that a valid answer could avoid."],
                ],
            },
            "Two sweeps": {
                "idea": [
                    "Split the rule in two: beat the left neighbour if rated higher, and beat the right neighbour if rated higher.",
                    "A left-to-right sweep satisfies the left rule; a right-to-left sweep then satisfies the right rule while <code>max</code> keeps the left one.",
                ],
                "steps": [
                    "Set <code>c = [1] * n</code>.",
                    "Left to right: if <code>ratings[i] &gt; ratings[i - 1]</code>, set <code>c[i] = c[i - 1] + 1</code>.",
                    "Right to left: if <code>ratings[i] &gt; ratings[i + 1]</code>, set <code>c[i] = max(c[i], c[i + 1] + 1)</code>.",
                    "Return <code>sum(c)</code>.",
                ],
                "why": [
                    "After the first sweep, <code>c[i]</code> is the length of the increasing run ending at <code>i</code>, the least that satisfies the left rule.",
                    "The second sweep raises <code>c[i]</code> only when the right rule demands it, and <code>max</code> never lowers a value, so both rules hold with the smallest values.",
                    "Two linear sweeps: <strong>O(n)</strong> time; the candy array is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Left sweep: [1, 2, 3, 1, 1, 1].",
                        "Right sweep: index 4 → 2, index 3 → 3.",
                        "Index 2: max(3, 3 + 1) = 4.",
                        "c = [1, 2, 4, 3, 2, 1]: <strong>13</strong>.",
                    ],
                    [
                        "Left sweep: [1, 2, 1, 1]; index 2 equals its left neighbour, so it stays 1.",
                        "Right sweep: index 2 beats index 3, so max(1, 2) = 2.",
                        "Indexes 1 and 0 need nothing more.",
                        "c = [1, 2, 2, 1]: <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>max</code> in the second sweep?",
                     "<code>c[i]</code> may already be large from the left sweep (a peak). Replacing it with <code>c[i + 1] + 1</code> could break the left rule."],
                    ["Why not do both checks in one sweep?",
                     "The right rule depends on values to the right, which a left-to-right sweep has not finished yet."],
                    ["Why does an equal neighbour reset to 1?",
                     "Equal ratings impose no rule, so the run of increases starts over."],
                ],
            },
            "One pass counting slopes": {
                "idea": [
                    "Candy depends only on runs: an increasing run of length <code>up</code> needs 1, 2, …; a decreasing run needs …, 2, 1 counted from its bottom.",
                    "Count candies as the slopes are walked: on the way up add <code>up + 1</code>; on the way down add <code>down</code>, which is like adding 1 to the new bottom and pushing everyone above it up by one.",
                    "<code>peak</code> remembers the height of the last climb; once the descent is longer than it, the peak must grow too, so add one more.",
                ],
                "steps": [
                    "If there is one child, return 1. Otherwise start <code>total = 1</code> and <code>up = down = peak = 0</code>.",
                    "Rising: <code>up += 1</code>, <code>down = 0</code>, <code>peak = up</code>, <code>total += up + 1</code>.",
                    "Equal: reset <code>up = down = peak = 0</code> and add 1.",
                    "Falling: <code>up = 0</code>, <code>down += 1</code>, add <code>down</code>, plus 1 more when <code>down &gt; peak</code>.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "The minimum for a peak is max(climb length, descent length) + 1; adding the extra 1 only once <code>down</code> passes <code>peak</code> grows the peak exactly then.",
                    "Every child is counted once, with the same values the two sweeps would give, so the sum matches.",
                    "One pass and four integers: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start total 1. 2 &gt; 1: up 1, peak 1, total 3. 3 &gt; 2: up 2, peak 2, total 6.",
                        "2 &lt; 3: down 1 ≤ peak, total 7.",
                        "1 &lt; 2: down 2 ≤ peak, total 9.",
                        "0 &lt; 1: down 3 &gt; peak 2, so add 3 + 1, total 13.",
                        "It returns <strong>13</strong>.",
                    ],
                    [
                        "Start total 1. 2 &gt; 1: up 1, peak 1, total 3.",
                        "2 = 2: everything resets to 0, total 4.",
                        "1 &lt; 2: down 1 &gt; peak 0, so add 1 + 1, total 6: the second 2 grows to 2 candies.",
                        "It returns <strong>6</strong>.",
                    ],
                ],
                "faq": [
                    ["Why add <code>down</code> and not 1 on each falling step?",
                     "The new child gets 1, and every child above it in the descent must go up by one to stay above it: that is 1 + (down − 1) = <code>down</code>."],
                    ["What does <code>peak</code> stand for?",
                     "How many candies above 1 the top of the last climb already has. Until the descent is longer than that, the peak is high enough."],
                    ["Why reset <code>peak</code> on equal ratings?",
                     "Equal neighbours impose no rule, so the next descent starts from a child with no climb behind it; its first step must lift it, which the <code>down &gt; peak</code> extra handles."],
                ],
            },
        },
    },
}
