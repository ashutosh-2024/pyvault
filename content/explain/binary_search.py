"""Write-ups for the Binary Search topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ binary search
    "binary-search": {
        "examples": [
            {"call": "search([-1, 0, 3, 5, 9, 12], 9)", "expect": "4"},
            {"call": "search([-1, 0, 3, 5, 9, 12], 2)", "expect": "-1"},
        ],
        "approaches": {
            "Linear scan": {
                "idea": [
                    "Look at every element from the left and stop the moment one equals the target.",
                    "It works on any array, sorted or not, which is exactly why it wastes the one fact this problem gives you.",
                ],
                "steps": [
                    "Loop over <code>enumerate(nums)</code>, getting index <code>i</code> and value <code>x</code>.",
                    "If <code>x == target</code>, return <code>i</code> immediately.",
                    "Otherwise keep going; the order of the values is never used.",
                    "If the loop runs off the end, the target is absent: return <code>-1</code>.",
                ],
                "why": [
                    "Every index is compared with the target before <code>-1</code> is returned, so a present target cannot be missed, and the first match is returned.",
                    "In the worst case (target last or missing) all n elements are compared: <strong>O(n)</strong> time.",
                    "Only the loop variables are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: −1 ≠ 9. i=1: 0 ≠ 9. i=2: 3 ≠ 9. i=3: 5 ≠ 9.",
                        "i=4: 9 == 9, a match.",
                        "Five comparisons in total; the result is <strong>4</strong>.",
                    ],
                    [
                        "i=0..2: −1, 0, 3 are all ≠ 2.",
                        "At i=2 the value 3 is already bigger than 2, but this code does not use that and keeps scanning.",
                        "i=3..5: 5, 9, 12 also differ. The loop ends after six comparisons.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Could I stop early once <code>x &gt; target</code>?",
                     "Yes, on a sorted array that is a valid optimisation and it would stop at 3 in the second example. The worst case is still O(n), so it does not change the complexity."],
                    ["Why mention this at all if the array is sorted?",
                     "It is the baseline that makes the gain of binary search concrete: n comparisons versus about log₂ n."],
                    ["Does it return the first index if values repeat?",
                     "Yes, it scans from the left. The problem promises distinct values, so it does not matter here."],
                ],
            },
            "Recursive binary search": {
                "idea": [
                    "In a sorted array, one comparison with the middle element tells you which half the target must be in.",
                    "If <code>nums[mid]</code> is too small, everything left of it is too small as well; if it is too big, everything right of it is too big.",
                    "Recurse on the half that can still hold the target until it is found or the range is empty.",
                ],
                "steps": [
                    "<code>go(lo, hi)</code> searches the inclusive range <code>nums[lo..hi]</code>; the first call is <code>go(0, len(nums) - 1)</code>.",
                    "If <code>lo &gt; hi</code>, the range is empty: return <code>-1</code>.",
                    "Compute <code>mid = (lo + hi) // 2</code>; if <code>nums[mid] == target</code>, return <code>mid</code>.",
                    "If <code>nums[mid] &lt; target</code>, recurse on <code>go(mid + 1, hi)</code>.",
                    "Otherwise recurse on <code>go(lo, mid - 1)</code>.",
                ],
                "why": [
                    "Invariant: if the target is in the array, it is inside <code>[lo, hi]</code>. Each discarded half holds only values strictly on the wrong side of the target.",
                    "The range shrinks to less than half each call, so there are at most about log₂ n + 1 calls: <strong>O(log n)</strong> time.",
                    "Each call waits for the next one, so the call stack holds up to log n frames: <strong>O(log n)</strong> space.",
                ],
                "dry": [
                    [
                        "go(0, 5): mid = 2, nums[2] = 3 &lt; 9, so call go(3, 5).",
                        "go(3, 5): mid = 4, nums[4] = 9, a match.",
                        "The result is <strong>4</strong> after two comparisons.",
                    ],
                    [
                        "go(0, 5): mid = 2, nums[2] = 3 &gt; 2, so call go(0, 1).",
                        "go(0, 1): mid = 0, nums[0] = −1 &lt; 2, so call go(1, 1).",
                        "go(1, 1): mid = 1, nums[1] = 0 &lt; 2, so call go(2, 1).",
                        "go(2, 1): lo &gt; hi, the range is empty. The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>mid + 1</code> and <code>mid - 1</code> rather than <code>mid</code>?",
                     "<code>mid</code> has already been compared and is not the target, so it can be excluded. Keeping it could leave the range the same size forever when <code>lo == hi</code>."],
                    ["Why is the space O(log n) and not O(1)?",
                     "Python does not eliminate tail calls, so every pending <code>go</code> keeps a frame on the stack until the answer comes back."],
                    ["Can <code>(lo + hi) // 2</code> overflow?",
                     "Not in Python, whose integers are unbounded. In Java or C++ write <code>lo + (hi - lo) / 2</code>."],
                ],
            },
            "Iterative binary search": {
                "idea": [
                    "The same halving as the recursive version, but <code>lo</code> and <code>hi</code> are updated in a loop instead of passed to a new call.",
                    "The invariant is identical: if the target exists, it lies in <code>nums[lo..hi]</code>. Loop while that range is non-empty.",
                ],
                "steps": [
                    "Start with <code>lo, hi = 0, len(nums) - 1</code>, the whole array.",
                    "While <code>lo &lt;= hi</code>, compute <code>mid = (lo + hi) // 2</code>.",
                    "If <code>nums[mid] == target</code>, return <code>mid</code>.",
                    "If <code>nums[mid] &lt; target</code>, the target is to the right: <code>lo = mid + 1</code>.",
                    "Otherwise it is to the left: <code>hi = mid - 1</code>.",
                    "When the loop exits, <code>lo == hi + 1</code> and the range is empty: return <code>-1</code>.",
                ],
                "why": [
                    "Each update removes <code>mid</code> and the half beyond it, all of which are on the wrong side of the target, so the invariant holds.",
                    "The range at least halves each iteration: <strong>O(log n)</strong> time, about 20 iterations for a million elements.",
                    "Only <code>lo</code>, <code>hi</code> and <code>mid</code> are stored: <strong>O(1)</strong> space, the advantage over the recursive form.",
                ],
                "dry": [
                    [
                        "lo=0, hi=5: mid=2, nums[2]=3 &lt; 9, so lo=3.",
                        "lo=3, hi=5: mid=4, nums[4]=9, a match.",
                        "The result is <strong>4</strong>.",
                    ],
                    [
                        "lo=0, hi=5: mid=2, 3 &gt; 2, so hi=1.",
                        "lo=0, hi=1: mid=0, −1 &lt; 2, so lo=1.",
                        "lo=1, hi=1: mid=1, 0 &lt; 2, so lo=2.",
                        "lo=2 &gt; hi=1, the loop stops. The result is <strong>-1</strong>; 2 would sit at index 2 if inserted.",
                    ],
                ],
                "faq": [
                    ["Why <code>lo &lt;= hi</code> and not <code>lo &lt; hi</code>?",
                     "With inclusive bounds, <code>lo == hi</code> is a one-element range that still has to be checked. With <code>&lt;</code>, searching <code>[5]</code> for 5 would return -1."],
                    ["What does <code>lo</code> mean when the search fails?",
                     "It is the insertion point: the number of elements smaller than the target. That is why the same loop solves Search Insert Position."],
                    ["Does this find the first copy when values repeat?",
                     "Not necessarily; it returns whichever copy a <code>mid</code> lands on. Finding the first copy needs the lower-bound variant that keeps going left after a match."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search insert position
    "search-insert-position": {
        "examples": [
            {"call": "search_insert([1, 3, 5, 6, 8, 10], 7)", "expect": "4"},
            {"call": "search_insert([1, 3, 5, 6], 5)", "expect": "2"},
        ],
        "approaches": {
            "Linear scan for the first value &ge; target": {
                "idea": [
                    "The insertion point is the index of the first element that is not smaller than the target.",
                    "If the target is present, that element is the target itself, so one rule covers both cases.",
                    "If no element qualifies, the target goes after everything, at index <code>len(nums)</code>.",
                ],
                "steps": [
                    "Loop over <code>enumerate(nums)</code> with index <code>i</code> and value <code>x</code>.",
                    "If <code>x &gt;= target</code>, return <code>i</code>.",
                    "Otherwise <code>x</code> is smaller and must stay before the target; keep going.",
                    "If the loop finishes, every value is smaller: return <code>len(nums)</code>.",
                ],
                "why": [
                    "All elements before the returned <code>i</code> are smaller than the target and <code>nums[i]</code> is not, so inserting at <code>i</code> keeps the array sorted.",
                    "It stops at the first qualifying element, but a target larger than everything forces all n comparisons: <strong>O(n)</strong> time.",
                    "No extra storage: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0..3: 1, 3, 5, 6 are all &lt; 7.",
                        "i=4: 8 ≥ 7, so 7 belongs here.",
                        "The result is <strong>4</strong>.",
                    ],
                    [
                        "i=0: 1 &lt; 5. i=1: 3 &lt; 5.",
                        "i=2: 5 ≥ 5. The target exists and this is its index.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt;=</code> and not <code>&gt;</code>?",
                     "With <code>&gt;</code>, a present target would be skipped and you would return the index after it (3 instead of 2 in the second example)."],
                    ["What if the array is empty?",
                     "The loop does nothing and <code>len(nums) = 0</code> is returned, which is right."],
                    ["Is this the same as <code>bisect.bisect_left</code>?",
                     "Same answer, but <code>bisect_left</code> finds it with binary search in O(log n)."],
                ],
            },
            "Lower bound on a half-open range": {
                "idea": [
                    "The array splits into a prefix of values <code>&lt; target</code> followed by values <code>≥ target</code>. The answer is where that split happens.",
                    "Binary search for the split rather than for the target: a value smaller than the target means the split is to its right; any other value might be the split itself.",
                    "Using the half-open range <code>[lo, hi)</code> with <code>hi = len(nums)</code> allows the answer to be one past the end.",
                ],
                "steps": [
                    "Start with <code>lo, hi = 0, len(nums)</code>; the answer is somewhere in <code>[lo, hi]</code>.",
                    "While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>.",
                    "If <code>nums[mid] &lt; target</code>, the split is after <code>mid</code>: <code>lo = mid + 1</code>.",
                    "Otherwise <code>nums[mid] ≥ target</code>, so <code>mid</code> may be the answer: <code>hi = mid</code>, keeping it.",
                    "When <code>lo == hi</code>, both point at the split: return <code>lo</code>.",
                ],
                "why": [
                    "Invariant: everything before <code>lo</code> is <code>&lt; target</code> and everything from <code>hi</code> on is <code>≥ target</code>. When they meet, that index is the first element ≥ target.",
                    "<code>mid</code> is always <code>&lt; hi</code>, so both updates shrink the range and the loop ends.",
                    "The range halves each time: <strong>O(log n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0, hi=6: mid=3, nums[3]=6 &lt; 7, so lo=4.",
                        "lo=4, hi=6: mid=5, nums[5]=10 ≥ 7, so hi=5.",
                        "lo=4, hi=5: mid=4, nums[4]=8 ≥ 7, so hi=4.",
                        "lo == hi == 4. The result is <strong>4</strong>.",
                    ],
                    [
                        "lo=0, hi=4: mid=2, nums[2]=5 is not &lt; 5, so hi=2. The match is kept, not returned.",
                        "lo=0, hi=2: mid=1, nums[1]=3 &lt; 5, so lo=2.",
                        "lo == hi == 2. The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>hi = mid</code> instead of <code>hi = mid - 1</code>?",
                     "<code>nums[mid] ≥ target</code> means <code>mid</code> could be the first such index. Dropping it with <code>mid - 1</code> would lose the answer, as in the second example where index 2 is correct."],
                    ["Why does the loop not return early on an exact match?",
                     "It does not need to: an equal value goes to the <code>hi = mid</code> branch and the search narrows onto it. Without an early return it also finds the <em>first</em> copy if values repeat."],
                    ["Why start <code>hi</code> at <code>len(nums)</code>?",
                     "A target bigger than every element must be inserted at <code>len(nums)</code>. Starting at <code>len(nums) - 1</code> would make that answer unreachable."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ guess number higher or lower
    "guess-number": {
        "examples": [
            {"setup": "PICK = 6\ndef guess(num):\n    return 0 if num == PICK else (-1 if PICK < num else 1)",
             "call": "guess_number(10)", "expect": "6"},
            {"setup": "PICK = 10\ndef guess(num):\n    return 0 if num == PICK else (-1 if PICK < num else 1)",
             "call": "guess_number(10)", "expect": "10"},
        ],
        "approaches": {
            "Try every number": {
                "idea": [
                    "The pick is somewhere in <code>1..n</code>, so asking about every number in turn must hit it.",
                    "It ignores the useful part of the answer: <code>guess</code> also says whether the pick is higher or lower.",
                ],
                "steps": [
                    "Loop <code>k</code> from 1 to <code>n</code> inclusive.",
                    "Call <code>guess(k)</code>.",
                    "If it returns 0, <code>k</code> is the pick: return it.",
                    "Otherwise move on to <code>k + 1</code>; the -1 or 1 result is thrown away.",
                ],
                "why": [
                    "The pick is guaranteed to lie in <code>1..n</code>, so the loop always reaches it and returns.",
                    "It makes <code>PICK</code> calls, up to n in the worst case: <strong>O(n)</strong> calls.",
                    "Only the counter is stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "guess(1) through guess(5) each return 1: the pick is higher.",
                        "guess(6) returns 0.",
                        "Six calls; the result is <strong>6</strong>.",
                    ],
                    [
                        "guess(1) through guess(9) all return 1.",
                        "guess(10) returns 0. The pick being n is the worst case: n calls.",
                        "The result is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the function end without a <code>return</code> after the loop?",
                     "The problem guarantees the pick is in range, so the loop always returns. Without that guarantee it would fall through and return <code>None</code>."],
                    ["Is this acceptable for n up to 2<sup>31</sup> − 1?",
                     "No. Two billion calls is far too slow; binary search needs about 31."],
                    ["What does <code>guess</code> return when the pick is higher?",
                     "1, meaning your number is lower than the pick. Read the sign as \"which way the pick is\", not \"how your number compares\"."],
                ],
            },
            "Binary search on the range": {
                "idea": [
                    "Every non-zero answer from <code>guess</code> rules out half of the remaining numbers.",
                    "Keep the range <code>[lo, hi]</code> that still contains the pick and always ask about its middle.",
                ],
                "steps": [
                    "Start with <code>lo, hi = 1, n</code>.",
                    "Repeat: <code>mid = (lo + hi) // 2</code> and <code>g = guess(mid)</code>.",
                    "If <code>g == 0</code>, return <code>mid</code>.",
                    "If <code>g &lt; 0</code>, the pick is lower than <code>mid</code>: <code>hi = mid - 1</code>.",
                    "Otherwise the pick is higher: <code>lo = mid + 1</code>.",
                ],
                "why": [
                    "The pick always stays inside <code>[lo, hi]</code>, because each update only removes numbers that <code>guess</code> said are wrong.",
                    "The loop is <code>while True</code> on purpose: the range can never become empty before the pick is hit, since the pick is in it.",
                    "The range halves each call: <strong>O(log n)</strong> calls, about 31 for n = 2<sup>31</sup> − 1. Space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "lo=1, hi=10: mid=5, guess(5) = 1 (higher), so lo=6.",
                        "lo=6, hi=10: mid=8, guess(8) = −1 (lower), so hi=7.",
                        "lo=6, hi=7: mid=6, guess(6) = 0.",
                        "Three calls; the result is <strong>6</strong>.",
                    ],
                    [
                        "mid=5 → 1, lo=6. mid=8 → 1, lo=9.",
                        "lo=9, hi=10: mid=9 → 1, lo=10.",
                        "lo=hi=10: mid=10, guess(10) = 0.",
                        "Four calls instead of ten; the result is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>while True</code> rather than <code>while lo &lt;= hi</code>?",
                     "The pick is guaranteed to exist, so the loop always returns. <code>while lo &lt;= hi</code> would also work but would need an unreachable return after it."],
                    ["Is <code>g &lt; 0</code> really \"go lower\"?",
                     "Yes: -1 means your guess is higher than the pick, so the pick is below <code>mid</code> and <code>hi</code> moves down."],
                    ["Would <code>mid = lo + (hi - lo) // 2</code> change anything?",
                     "Not in Python. In 32-bit languages it avoids overflow when <code>lo + hi</code> exceeds 2<sup>31</sup> − 1, which is the original reason this problem uses n up to that size."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sqrt(x)
    "sqrt-x": {
        "examples": [
            {"call": "my_sqrt(30)", "expect": "5"},
            {"call": "my_sqrt(16)", "expect": "4"},
        ],
        "approaches": {
            "Count up": {
                "idea": [
                    "The answer is the largest <code>k</code> with <code>k * k ≤ x</code>.",
                    "Start at 0 and step up while the next number still squares to at most <code>x</code>.",
                ],
                "steps": [
                    "Set <code>k = 0</code>; 0² = 0 ≤ x for every valid input.",
                    "While <code>(k + 1) * (k + 1) &lt;= x</code>, the next integer still fits: <code>k += 1</code>.",
                    "As soon as <code>(k + 1)²</code> exceeds <code>x</code>, <code>k</code> is the largest that fits.",
                    "Return <code>k</code>.",
                ],
                "why": [
                    "Invariant: <code>k² ≤ x</code>. The loop stops exactly when <code>(k + 1)² &gt; x</code>, which is the definition of the floor square root.",
                    "The loop runs √x times: <strong>O(√x)</strong> time. For x = 2<sup>31</sup> − 1 that is about 46,000 steps.",
                    "Only <code>k</code> is stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "k=0: 1² = 1 ≤ 30, so k=1. 2² = 4 ≤ 30, so k=2.",
                        "3² = 9 and 4² = 16 fit, so k=4. 5² = 25 ≤ 30, so k=5.",
                        "6² = 36 &gt; 30, the loop stops.",
                        "The result is <strong>5</strong>.",
                    ],
                    [
                        "k climbs 0 → 1 → 2 → 3 as 1, 4, 9 fit.",
                        "4² = 16 ≤ 16: equality still counts, so k=4.",
                        "5² = 25 &gt; 16 stops the loop. The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why test <code>(k + 1)²</code> rather than <code>k²</code>?",
                     "Testing the next candidate means the loop stops with <code>k</code> already correct, with no need to step back by one afterwards."],
                    ["Why <code>&lt;=</code>?",
                     "A perfect square must return its exact root. With <code>&lt;</code>, 16 would return 3."],
                    ["Does it handle 0 and 1?",
                     "Yes. For 0 the first check 1 ≤ 0 fails and 0 is returned; for 1 it steps once to 1."],
                ],
            },
            "Binary search on the answer": {
                "idea": [
                    "The test <code>k * k ≤ x</code> is true for all small <code>k</code> and false for all large ones. The answer is the last <code>k</code> where it is true.",
                    "That monotone yes/no pattern is all binary search needs, even though there is no array.",
                    "Search <code>[0, x]</code> for the last \"yes\", using an upper middle so the range always shrinks.",
                ],
                "steps": [
                    "Start with <code>lo, hi = 0, x</code>; the answer is in <code>[lo, hi]</code>.",
                    "While <code>lo &lt; hi</code>, take the upper middle <code>mid = (lo + hi + 1) // 2</code>.",
                    "If <code>mid * mid &lt;= x</code>, <code>mid</code> is a valid answer and maybe not the last: <code>lo = mid</code>.",
                    "Otherwise <code>mid</code> is too big, and so is everything above it: <code>hi = mid - 1</code>.",
                    "When <code>lo == hi</code>, return <code>lo</code>.",
                ],
                "why": [
                    "Invariant: <code>lo² ≤ x</code> and <code>(hi + 1)² &gt; x</code> (or hi = x). When they meet, <code>lo</code> is the largest square root that fits.",
                    "The upper middle makes <code>mid &gt; lo</code>, so <code>lo = mid</code> always moves; a lower middle would loop forever when <code>hi = lo + 1</code>.",
                    "The range of size x halves each step: <strong>O(log x)</strong> time, about 31 steps for 2<sup>31</sup>. Space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "lo=0, hi=30: mid=15, 225 &gt; 30, so hi=14.",
                        "lo=0, hi=14: mid=7, 49 &gt; 30, so hi=6. Then mid=3, 9 ≤ 30, so lo=3.",
                        "lo=3, hi=6: mid=5, 25 ≤ 30, so lo=5. Then mid=6, 36 &gt; 30, so hi=5.",
                        "lo == hi == 5. The result is <strong>5</strong>.",
                    ],
                    [
                        "lo=0, hi=16: mid=8, 64 &gt; 16, so hi=7.",
                        "lo=0, hi=7: mid=4, 16 ≤ 16, so lo=4.",
                        "lo=4, hi=7: mid=6, 36 &gt; 16, so hi=5. Then mid=5, 25 &gt; 16, so hi=4.",
                        "lo == hi == 4. The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong with <code>mid = (lo + hi) // 2</code> here?",
                     "With lo=4, hi=5 it gives mid=4, which passes the test and sets lo=4 again: an infinite loop. The rule: if the \"yes\" branch is <code>lo = mid</code>, round mid up."],
                    ["Why can <code>hi</code> start at <code>x</code> and not <code>x // 2</code>?",
                     "<code>x // 2</code> is a tighter bound for x ≥ 2 but wrong for x = 1. Starting at <code>x</code> costs one extra step and needs no special case."],
                    ["Is <code>mid * mid</code> safe?",
                     "In Python yes. In 32-bit languages it overflows; compare <code>mid &lt;= x / mid</code> or use a 64-bit type."],
                ],
            },
            "Newton's method on integers": {
                "idea": [
                    "Newton's method for k² = x improves a guess <code>k</code> to the average of <code>k</code> and <code>x / k</code>.",
                    "Starting from a guess that is too big, the integer version decreases every step and settles on the floor square root.",
                    "The number of correct digits roughly doubles each step, so it needs very few iterations.",
                ],
                "steps": [
                    "If <code>x &lt; 2</code>, return <code>x</code>: 0 and 1 are their own roots.",
                    "Start with <code>k = x</code>, which is at least the root.",
                    "While <code>k * k &gt; x</code>, replace <code>k</code> with <code>(k + x // k) // 2</code>.",
                    "When <code>k * k ≤ x</code>, return <code>k</code>.",
                ],
                "why": [
                    "By the AM-GM inequality the average of <code>k</code> and <code>x / k</code> is never below √x, so the guess never falls under the answer while it is still too big, and it strictly decreases.",
                    "The first iteration where <code>k² ≤ x</code> therefore stops exactly at ⌊√x⌋.",
                    "After a short halving phase from a far-off start, convergence is quadratic: <strong>O(log log x)</strong> iterations once close, O(log x) in total from <code>k = x</code>. Space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "k=30: 900 &gt; 30, so k = (30 + 1) // 2 = 15.",
                        "k=15: 225 &gt; 30, so k = (15 + 2) // 2 = 8.",
                        "k=8: 64 &gt; 30, so k = (8 + 3) // 2 = 5.",
                        "k=5: 25 ≤ 30, the loop stops. The result is <strong>5</strong>.",
                    ],
                    [
                        "k=16: 256 &gt; 16, so k = (16 + 1) // 2 = 8.",
                        "k=8: 64 &gt; 16, so k = (8 + 2) // 2 = 5.",
                        "k=5: 25 &gt; 16, so k = (5 + 3) // 2 = 4.",
                        "k=4: 16 ≤ 16, the loop stops. The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the special case for <code>x &lt; 2</code>?",
                     "For x = 0, <code>x // k</code> with k = 0 would divide by zero. For x = 1 it would work, but the early return keeps it simple."],
                    ["Why integer division and not floats?",
                     "Floats lose precision for large x and can give an answer that is off by one. Integer Newton is exact for any size."],
                    ["Why is the stated cost O(log log x) when the dry runs look like halving?",
                     "From <code>k = x</code> the first steps roughly halve the guess; the doubling of correct digits only starts once the guess is near √x. The log log bound describes that final phase."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search a 2D matrix
    "search-2d-matrix": {
        "examples": [
            {"call": "search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 16)", "expect": "True"},
            {"call": "search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13)", "expect": "False"},
        ],
        "approaches": {
            "Scan everything": {
                "idea": [
                    "Check every row for the target with Python's <code>in</code>.",
                    "None of the ordering is used, so it is the baseline to beat.",
                ],
                "steps": [
                    "Iterate over <code>matrix</code> one <code>row</code> at a time.",
                    "For each row evaluate <code>target in row</code>, a left-to-right scan.",
                    "<code>any(...)</code> stops at the first row that contains it and returns <code>True</code>.",
                    "If no row contains it, <code>any</code> returns <code>False</code>.",
                ],
                "why": [
                    "Every cell is compared with the target unless it is found earlier, so the answer is always right.",
                    "In the worst case all m · n cells are read: <strong>O(m · n)</strong> time.",
                    "The generator holds one row reference at a time: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "Row 0 [1, 3, 5, 7]: 16 is not in it.",
                        "Row 1 [10, 11, 16, 20]: 16 is found at its third cell.",
                        "<code>any</code> stops here; the result is <strong>True</strong>.",
                    ],
                    [
                        "Row 0: four comparisons, no 13.",
                        "Row 1: four comparisons, no 13. Row 2: four comparisons, no 13.",
                        "All 12 cells were read; the result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Does <code>target in row</code> use the row being sorted?",
                     "No, <code>in</code> on a list is a plain linear scan."],
                    ["Why mention this when it is so slow?",
                     "It sets the baseline and is a useful correctness check when testing the clever versions."],
                    ["Would flattening the matrix first help?",
                     "Only if you then binary search it, and building the flat list costs O(m · n) anyway. The last approach gets the same effect without building anything."],
                ],
            },
            "Staircase from the top-right": {
                "idea": [
                    "From the top-right corner, moving left makes values smaller and moving down makes them bigger.",
                    "Comparing the corner with the target therefore removes a whole column or a whole row each step.",
                    "This only uses \"rows and columns are sorted\", so it also solves Search a 2D Matrix II where rows do not continue each other.",
                ],
                "steps": [
                    "Start at <code>r, c = 0, len(matrix[0]) - 1</code>.",
                    "While <code>r</code> is in range and <code>c &gt;= 0</code>, read <code>v = matrix[r][c]</code>.",
                    "If <code>v == target</code>, return <code>True</code>.",
                    "If <code>v &gt; target</code>, everything below in column <code>c</code> is even bigger: <code>c -= 1</code>.",
                    "Otherwise everything left in row <code>r</code> is even smaller: <code>r += 1</code>.",
                    "If the walk leaves the matrix, return <code>False</code>.",
                ],
                "why": [
                    "Invariant: if the target exists, it is in rows <code>r..m-1</code> and columns <code>0..c</code>. Each step removes a row or column that cannot contain it.",
                    "<code>r</code> only increases and <code>c</code> only decreases, so there are at most m + n steps: <strong>O(m + n)</strong> time.",
                    "Two indices: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "(0,3) = 7 &lt; 16: row 0 is too small, r=1.",
                        "(1,3) = 20 &gt; 16: column 3 is too big, c=2.",
                        "(1,2) = 16, a match. The result is <strong>True</strong>.",
                    ],
                    [
                        "(0,3) = 7 &lt; 13, r=1. (1,3) = 20 &gt; 13, c=2. (1,2) = 16 &gt; 13, c=1.",
                        "(1,1) = 11 &lt; 13, r=2.",
                        "(2,1) = 30 &gt; 13, c=0. (2,0) = 23 &gt; 13, c=−1.",
                        "The walk leaves the matrix; the result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not start at the top-left?",
                     "From the top-left both right and down increase the value, so a too-small value does not tell you which way to go. The top-right (or bottom-left) corner has one increasing and one decreasing direction."],
                    ["Is this slower than binary search here?",
                     "Yes: O(m + n) versus O(log(m · n)). It does not use the fact that each row starts after the previous one ends."],
                    ["When is the staircase the right choice?",
                     "When only rows and columns are sorted independently (LeetCode 240). There a single binary search is not possible."],
                ],
            },
            "Binary search the row, then the column": {
                "idea": [
                    "Because rows continue each other, the target can only be in the last row whose first value is ≤ target.",
                    "Find that row by binary searching the first column, then binary search inside the row.",
                ],
                "steps": [
                    "Build <code>firsts</code>, the first value of each row.",
                    "<code>r = bisect_right(firsts, target) - 1</code>: the last row starting at or below the target.",
                    "If <code>r &lt; 0</code>, the target is smaller than every value: return <code>False</code>.",
                    "In <code>row = matrix[r]</code>, <code>i = bisect_left(row, target)</code> is where the target would be.",
                    "Return whether <code>i</code> is in range and <code>row[i] == target</code>.",
                ],
                "why": [
                    "Rows after <code>r</code> start above the target, and rows before <code>r</code> end below <code>matrix[r][0]</code> ≤ target, so only row <code>r</code> can hold it.",
                    "The two bisects cost <strong>O(log m + log n)</strong>. Building <code>firsts</code> is O(m) time and space, so as written this is really O(m + log n); bisecting with a key on the rows would avoid that.",
                    "Apart from <code>firsts</code>, space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "firsts = [1, 10, 23]; bisect_right(firsts, 16) = 2, so r = 1.",
                        "row = [10, 11, 16, 20]; bisect_left(row, 16) = 2.",
                        "row[2] = 16, so the result is <strong>True</strong>.",
                    ],
                    [
                        "bisect_right(firsts, 13) = 2, so r = 1 again.",
                        "bisect_left([10, 11, 16, 20], 13) = 2: 13 would sit before 16.",
                        "row[2] = 16 ≠ 13, so the result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>bisect_right</code> for the row but <code>bisect_left</code> for the column?",
                     "For the row we want the last first-value ≤ target, so equal values must count as \"before\" the split. For the column we want the position of the target itself, which <code>bisect_left</code> gives when it exists."],
                    ["What does the <code>i &lt; len(row)</code> check protect against?",
                     "A target bigger than the whole row makes <code>bisect_left</code> return <code>len(row)</code>, and <code>row[i]</code> would raise IndexError."],
                    ["Is building <code>firsts</code> cheating on the O(log) bound?",
                     "Slightly: it is a linear pass. It is still fast in practice, and <code>bisect</code> with <code>key=</code> (Python 3.10+) removes it."],
                ],
            },
            "One binary search over the flattened index": {
                "idea": [
                    "Reading the matrix row by row gives one sorted list of m · n values.",
                    "Index <code>k</code> of that virtual list is cell <code>(k // n, k % n)</code>, so you can binary search it without building it.",
                ],
                "steps": [
                    "Set <code>m, n</code> to the dimensions and <code>lo, hi = 0, m * n - 1</code>.",
                    "While <code>lo &lt;= hi</code>, take <code>mid</code> and read <code>v = matrix[mid // n][mid % n]</code>.",
                    "If <code>v == target</code>, return <code>True</code>.",
                    "If <code>v &lt; target</code>, set <code>lo = mid + 1</code>; otherwise <code>hi = mid - 1</code>.",
                    "When the range is empty, return <code>False</code>.",
                ],
                "why": [
                    "Row-major order is sorted because each row is sorted and starts after the previous row ends, so ordinary binary search is valid on it.",
                    "There are m · n virtual positions: <strong>O(log(m · n))</strong> time, which equals O(log m + log n).",
                    "Only indices are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 4, lo=0, hi=11: mid=5 → cell (1,1) = 11 &lt; 16, so lo=6.",
                        "lo=6, hi=11: mid=8 → cell (2,0) = 23 &gt; 16, so hi=7.",
                        "lo=6, hi=7: mid=6 → cell (1,2) = 16, a match.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "mid=5 → 11 &lt; 13, so lo=6.",
                        "mid=8 → 23 &gt; 13, so hi=7.",
                        "mid=6 → (1,2) = 16 &gt; 13, so hi=5.",
                        "lo=6 &gt; hi=5: the result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why divide by <code>n</code> (columns) and not <code>m</code>?",
                     "In row-major order each row holds n cells, so the row is <code>k // n</code> and the column <code>k % n</code>. Using m only works for square matrices."],
                    ["Does this work for Search a 2D Matrix II?",
                     "No. There the flattened order is not sorted, so use the staircase."],
                    ["Is it really better than two bisects?",
                     "Asymptotically the same, but it reads no first column and needs no extra list."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ koko eating bananas
    "koko-eating-bananas": {
        "examples": [
            {"call": "min_eating_speed([3, 6, 7, 11], 8)", "expect": "4"},
            {"call": "min_eating_speed([30, 11, 23, 4, 20], 5)", "expect": "30"},
        ],
        "approaches": {
            "Try every speed from 1 upward": {
                "idea": [
                    "At speed <code>k</code>, a pile of <code>p</code> bananas takes <code>ceil(p / k)</code> hours, because a partly eaten hour is still an hour.",
                    "Faster never takes longer, so the first speed whose total fits in <code>h</code> is the answer.",
                ],
                "steps": [
                    "Start with <code>k = 1</code>.",
                    "Compute the total hours <code>sum((p + k - 1) // k for p in piles)</code>.",
                    "While that total is more than <code>h</code>, increase <code>k</code> by 1.",
                    "Return the first <code>k</code> where the total is ≤ <code>h</code>.",
                ],
                "why": [
                    "Speeds are tried in increasing order and the first feasible one is returned, so it is the minimum.",
                    "Speed <code>max(piles)</code> always finishes in n ≤ h hours, so at most <code>max(piles)</code> speeds are tried, each costing n: <strong>O(max(piles) · n)</strong> time.",
                    "No extra storage: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "k=1: 3 + 6 + 7 + 11 = 27 hours &gt; 8.",
                        "k=2: 2 + 3 + 4 + 6 = 15 &gt; 8. k=3: 1 + 2 + 3 + 4 = 10 &gt; 8.",
                        "k=4: 1 + 2 + 2 + 3 = 8 ≤ 8.",
                        "The result is <strong>4</strong>.",
                    ],
                    [
                        "h = 5 equals the number of piles, so each pile must be finished in one hour.",
                        "k=1: 88 hours. k=2: 45. k=3: 31. The totals fall slowly.",
                        "k=25 through k=29 all need 6 hours: only the pile of 30 still takes 2.",
                        "k=30: 5 hours ≤ 5. After 30 checks the result is <strong>30</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>(p + k - 1) // k</code>?",
                     "It is integer ceiling division: it rounds <code>p / k</code> up without floats. <code>p // k</code> would undercount any partial hour."],
                    ["Can the loop run forever?",
                     "No. At <code>k = max(piles)</code> every pile takes one hour, and the problem guarantees <code>h ≥ len(piles)</code>."],
                    ["When is this too slow?",
                     "Piles can be up to 10<sup>9</sup>, giving a billion speeds times n piles. Binary search on k cuts that to about 30 checks."],
                ],
            },
            "Binary search on the speed": {
                "idea": [
                    "Feasibility is monotone: if Koko finishes at speed <code>k</code>, she finishes at any faster speed.",
                    "So the speeds form \"too slow … too slow, fine … fine\" and the answer is the first \"fine\". Binary search finds a boundary like that.",
                    "Each probe costs one pass over the piles with <code>hours(k)</code>.",
                ],
                "steps": [
                    "Define <code>hours(k)</code> as the sum of <code>ceil(p / k)</code> over all piles.",
                    "Search <code>lo, hi = 1, max(piles)</code>; <code>max(piles)</code> is always feasible.",
                    "While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>.",
                    "If <code>hours(mid) &lt;= h</code>, <code>mid</code> works and might be the minimum: <code>hi = mid</code>.",
                    "Otherwise <code>mid</code> is too slow, as is everything below it: <code>lo = mid + 1</code>.",
                    "Return <code>lo</code> when the range closes.",
                ],
                "why": [
                    "Invariant: <code>hi</code> is always feasible and every speed below <code>lo</code> is infeasible. When <code>lo == hi</code>, that speed is the smallest feasible one.",
                    "The range is <code>max(piles)</code> wide, so there are about log₂ max(piles) probes, each O(n): <strong>O(n log max(piles))</strong> time.",
                    "<code>hours</code> uses a generator: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=1, hi=11: mid=6 needs 6 hours ≤ 8, so hi=6.",
                        "lo=1, hi=6: mid=3 needs 10 &gt; 8, so lo=4.",
                        "lo=4, hi=6: mid=5 needs 8 ≤ 8, so hi=5. Then mid=4 needs 8 ≤ 8, so hi=4.",
                        "lo == hi == 4. The result is <strong>4</strong>.",
                    ],
                    [
                        "lo=1, hi=30: mid=15 needs 8 &gt; 5, so lo=16.",
                        "mid=23 needs 6 &gt; 5, so lo=24. mid=27 needs 6, so lo=28.",
                        "mid=29 needs 6 (the pile of 30 takes 2 hours), so lo=30.",
                        "lo == hi == 30, the upper bound itself. The result is <strong>30</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>hi</code> start at <code>max(piles)</code>, not <code>sum(piles)</code>?",
                     "Any speed above the biggest pile still takes one hour per pile, so speeds beyond <code>max(piles)</code> are never better."],
                    ["Why <code>hi = mid</code> and not <code>mid - 1</code> on success?",
                     "<code>mid</code> itself may be the minimum; discarding it could skip the answer."],
                    ["Can I start <code>lo</code> higher than 1?",
                     "Yes, <code>ceil(sum(piles) / h)</code> is a valid lower bound, since total bananas over total hours is the least possible average speed. It saves a few probes but is not needed."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ ship within days
    "ship-within-days": {
        "examples": [
            {"call": "ship_within_days([3, 2, 2, 4, 1, 4], 3)", "expect": "6"},
            {"call": "ship_within_days([1, 2, 3, 1, 1], 4)", "expect": "3"},
        ],
        "approaches": {
            "Try every capacity upward": {
                "idea": [
                    "For a fixed capacity, the fewest days come from loading greedily: keep adding packages in order until the next one does not fit.",
                    "A bigger ship never needs more days, so try capacities from the smallest possible upward and stop at the first that fits in <code>days</code>.",
                ],
                "steps": [
                    "<code>days_needed(cap)</code> starts with <code>d, load = 1, 0</code>.",
                    "For each weight <code>w</code>: if <code>load + w &gt; cap</code>, start a new day (<code>d += 1</code>, <code>load = 0</code>); then add <code>w</code> to <code>load</code>.",
                    "Start with <code>cap = max(weights)</code>; anything smaller cannot carry the heaviest package.",
                    "While <code>days_needed(cap) &gt; days</code>, increase <code>cap</code> by 1.",
                    "Return the first capacity that fits.",
                ],
                "why": [
                    "Packages must ship in order, and filling each day as much as possible never pushes a later package to a later day than any other plan would. So the greedy count is the minimum for that capacity.",
                    "Capacities run from <code>max</code> up to at most <code>sum</code> (one day for everything), each costing a pass of n: <strong>O(n · (sum − max))</strong> time.",
                    "Only counters: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "cap=4: days [3] [2,2] [4] [1] [4] = 5 &gt; 3.",
                        "cap=5: [3,2] [2] [4,1] [4] = 4 &gt; 3.",
                        "cap=6: [3,2] [2,4] [1,4] = 3 ≤ 3.",
                        "The result is <strong>6</strong>.",
                    ],
                    [
                        "cap starts at max = 3.",
                        "cap=3: [1,2] [3] [1,1] = 3 days ≤ 4.",
                        "It fits immediately, so the heaviest package sets the answer: <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start at <code>max(weights)</code>?",
                     "A ship smaller than the heaviest package can never carry it, and <code>days_needed</code> would silently overload a day instead of failing."],
                    ["Why is it fine to use fewer days than allowed?",
                     "Using fewer days is allowed; the ship can stay idle. The problem asks for capacity, not an exact day count."],
                    ["Why reset <code>load</code> to 0 and then add <code>w</code>?",
                     "The package that did not fit becomes the first one of the new day, so the new day's load is exactly <code>w</code>."],
                ],
            },
            "Binary search on capacity with a greedy check": {
                "idea": [
                    "<code>days_needed(cap)</code> only goes down as <code>cap</code> grows, so \"fits in <code>days</code>\" is false for small capacities and true from some point on.",
                    "Binary search that point between <code>max(weights)</code> (smallest possible) and <code>sum(weights)</code> (one day for everything).",
                ],
                "steps": [
                    "Use the same greedy <code>days_needed(cap)</code> as the linear version.",
                    "Set <code>lo, hi = max(weights), sum(weights)</code>.",
                    "While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>.",
                    "If <code>days_needed(mid) &lt;= days</code>, <code>mid</code> works: <code>hi = mid</code>.",
                    "Otherwise it is too small: <code>lo = mid + 1</code>.",
                    "Return <code>lo</code>.",
                ],
                "why": [
                    "Invariant: <code>hi</code> is always feasible and everything below <code>lo</code> is not, so they meet at the minimum feasible capacity.",
                    "The range has width sum − max, so there are O(log sum) probes of O(n) each: <strong>O(n log(sum))</strong> time.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=4, hi=16: mid=10 → [3,2,2] [4,1,4] = 2 days, so hi=10.",
                        "mid=7 → [3,2,2] [4,1] [4] = 3 days, so hi=7.",
                        "mid=5 → 4 days &gt; 3, so lo=6. mid=6 → 3 days, so hi=6.",
                        "lo == hi == 6. The result is <strong>6</strong>.",
                    ],
                    [
                        "lo=3, hi=8: mid=5 → [1,2] [3,1,1] = 2 days, so hi=5.",
                        "mid=4 → [1,2] [3,1] [1] = 3 days, so hi=4.",
                        "mid=3 → [1,2] [3] [1,1] = 3 days, so hi=3.",
                        "lo == hi == 3. The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>lo</code> start at <code>max(weights)</code> and not 1?",
                     "The greedy check assumes every package fits on an empty ship. With a smaller capacity it overloads a day and reports too few days, so the search could return an impossible capacity."],
                    ["Is this the same pattern as Koko and Split Array?",
                     "Yes: a monotone yes/no check on a candidate answer plus a lower-bound binary search. Split Array Largest Sum is this exact problem with \"days\" renamed to \"parts\"."],
                    ["Why not <code>lo &lt;= hi</code> with <code>hi = mid - 1</code>?",
                     "That form needs a separate variable to remember the best feasible value. The <code>lo &lt; hi</code> / <code>hi = mid</code> form keeps the answer inside the range instead."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find minimum in rotated sorted array
    "find-min-rotated": {
        "examples": [
            {"call": "find_min([4, 5, 6, 7, 0, 1, 2])", "expect": "0"},
            {"call": "find_min([11, 13, 15, 17])", "expect": "11"},
        ],
        "approaches": {
            "Linear scan": {
                "idea": [
                    "The minimum of any list is found by looking at every element once.",
                    "Python's <code>min</code> does exactly that, ignoring that the array is a rotated sorted one.",
                ],
                "steps": [
                    "Call <code>min(nums)</code>.",
                    "It keeps a running smallest value and compares each element against it.",
                    "Return that smallest value.",
                    "Nothing about the rotation point is computed or needed.",
                ],
                "why": [
                    "Every element is compared, so the smallest cannot be missed.",
                    "n − 1 comparisons: <strong>O(n)</strong> time.",
                    "One running value: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Running minimum: 4, then 5 and 6 and 7 are bigger.",
                        "0 replaces 4; 1 and 2 are bigger.",
                        "The result is <strong>0</strong>.",
                    ],
                    [
                        "Running minimum starts at 11.",
                        "13, 15 and 17 are all bigger; the array is not rotated at all.",
                        "The result is <strong>11</strong>.",
                    ],
                ],
                "faq": [
                    ["Could I stop at the first drop <code>nums[i] &lt; nums[i - 1]</code>?",
                     "Yes, the element after the drop is the minimum, and if there is no drop the first element is. It is still O(n) in the worst case."],
                    ["Why is this not accepted in an interview?",
                     "The problem explicitly asks for O(log n), which requires using the sorted structure."],
                    ["Does it work with duplicates?",
                     "Yes, <code>min</code> does not care. The binary search needs extra care with duplicates (problem 154)."],
                ],
            },
            "Binary search against the right end": {
                "idea": [
                    "A rotated sorted array is two ascending runs, and every value of the left run is bigger than every value of the right run. The minimum starts the right run.",
                    "Comparing <code>nums[mid]</code> with <code>nums[hi]</code> tells you which run <code>mid</code> is in: bigger than <code>nums[hi]</code> means the left run, so the drop is after <code>mid</code>.",
                    "Otherwise <code>mid..hi</code> is sorted and the minimum is at <code>mid</code> or to its left.",
                ],
                "steps": [
                    "Set <code>lo, hi = 0, len(nums) - 1</code>.",
                    "While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>.",
                    "If <code>nums[mid] &gt; nums[hi]</code>, the minimum is strictly right of <code>mid</code>: <code>lo = mid + 1</code>.",
                    "Otherwise <code>mid</code> may be the minimum: <code>hi = mid</code>.",
                    "When <code>lo == hi</code>, return <code>nums[lo]</code>.",
                ],
                "why": [
                    "Invariant: the minimum's index is in <code>[lo, hi]</code>. A value bigger than <code>nums[hi]</code> cannot be the minimum, and when <code>nums[mid] ≤ nums[hi]</code> nothing in <code>mid+1..hi</code> is smaller than <code>nums[mid]</code>.",
                    "<code>mid &lt; hi</code> always, so both branches shrink the range: <strong>O(log n)</strong> time.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0, hi=6: mid=3, 7 &gt; nums[6]=2, so lo=4.",
                        "lo=4, hi=6: mid=5, 1 ≤ 2, so hi=5.",
                        "lo=4, hi=5: mid=4, 0 ≤ 1, so hi=4.",
                        "lo == hi == 4. The result is <strong>0</strong>.",
                    ],
                    [
                        "lo=0, hi=3: mid=1, 13 ≤ 17, so hi=1.",
                        "lo=0, hi=1: mid=0, 11 ≤ 13, so hi=0.",
                        "No rotation: every comparison went left. The result is <strong>11</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compare with <code>nums[hi]</code> and not <code>nums[lo]</code>?",
                     "When the array is not rotated, <code>nums[mid] ≥ nums[lo]</code> holds yet the minimum is on the left, so a <code>nums[lo]</code> test sends you the wrong way. <code>nums[hi]</code> gives a correct answer in both cases."],
                    ["Why <code>hi = mid</code> rather than <code>mid - 1</code>?",
                     "<code>nums[mid]</code> could itself be the minimum, as at index 4 in the first example."],
                    ["What changes when values can repeat?",
                     "If <code>nums[mid] == nums[hi]</code> you cannot tell the side, so you shrink with <code>hi -= 1</code>, which makes the worst case O(n)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search in rotated sorted array
    "search-rotated": {
        "examples": [
            {"call": "search_rotated([4, 5, 6, 7, 0, 1, 2], 1)", "expect": "5"},
            {"call": "search_rotated([4, 5, 6, 7, 0, 1, 2], 3)", "expect": "-1"},
        ],
        "approaches": {
            "Linear scan": {
                "idea": [
                    "<code>list.index</code> finds the target by scanning, regardless of rotation.",
                    "Check membership first because <code>index</code> raises an error when the value is missing.",
                ],
                "steps": [
                    "Evaluate <code>target in nums</code>, a linear scan.",
                    "If it is there, return <code>nums.index(target)</code>, a second scan that stops at it.",
                    "Otherwise return <code>-1</code>.",
                    "The rotation is never located or used.",
                ],
                "why": [
                    "Both operations compare against every element up to the target, so the index is exact.",
                    "Up to two passes over n elements: <strong>O(n)</strong> time.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "<code>1 in nums</code> scans 4, 5, 6, 7, 0, 1: True.",
                        "<code>nums.index(1)</code> scans again and stops at index 5.",
                        "The result is <strong>5</strong>.",
                    ],
                    [
                        "<code>3 in nums</code> scans all seven values: False.",
                        "<code>index</code> is never called.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just call <code>nums.index</code> in a try/except?",
                     "That works and saves one pass; the conditional form is simply easier to read."],
                    ["Is two passes worse than one?",
                     "It doubles the constant but stays O(n). The real problem is that O(log n) is required."],
                    ["Would sorting first help?",
                     "No: sorting is O(n log n) and destroys the original indices you must return."],
                ],
            },
            "Find the rotation point, then search one side": {
                "idea": [
                    "Split the problem in two known pieces: find the index of the minimum (the rotation point), then do a normal binary search.",
                    "Left of the pivot and from the pivot on, the array is two sorted runs. The target can only be in the run whose value range contains it.",
                ],
                "steps": [
                    "Find <code>pivot</code> with the find-minimum loop: <code>lo = mid + 1</code> if <code>nums[mid] &gt; nums[hi]</code>, else <code>hi = mid</code>.",
                    "If <code>nums[pivot] &lt;= target &lt;= nums[-1]</code>, search the right run <code>[pivot, len(nums))</code>.",
                    "Otherwise search the left run <code>[0, pivot)</code>.",
                    "Use <code>bisect.bisect_left(nums, target, lo, hi)</code> on that slice of indices.",
                    "Return <code>i</code> if it is in range and <code>nums[i] == target</code>, else <code>-1</code>.",
                ],
                "why": [
                    "The right run holds exactly the values from <code>nums[pivot]</code> to <code>nums[-1]</code>; any other present value must be in the left run, which is sorted too.",
                    "Two binary searches: <strong>O(log n)</strong> time.",
                    "<strong>O(1)</strong> space; <code>bisect</code> works on index bounds without slicing.",
                ],
                "dry": [
                    [
                        "Pivot search: mid=3 (7 &gt; 2) → lo=4; mid=5 (1 ≤ 2) → hi=5; mid=4 (0 ≤ 1) → hi=4. pivot = 4.",
                        "nums[4] = 0 ≤ 1 ≤ nums[-1] = 2, so search indices [4, 7).",
                        "bisect_left over 0, 1, 2 gives i = 5; nums[5] = 1.",
                        "The result is <strong>5</strong>.",
                    ],
                    [
                        "pivot = 4 as before.",
                        "0 ≤ 3 ≤ 2 is false, so search the left run [0, 4) = 4, 5, 6, 7.",
                        "bisect_left gives i = 0, but nums[0] = 4 ≠ 3.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compare with <code>nums[-1]</code> to pick the run?",
                     "The right run ends at the last element, so its values are exactly <code>[nums[pivot], nums[-1]]</code>. Every left-run value is bigger than <code>nums[-1]</code>."],
                    ["What if the array is not rotated?",
                     "The pivot is 0, the right run is the whole array, and the search is plain binary search."],
                    ["Why the <code>i &lt; len(nums)</code> check?",
                     "If the target is bigger than everything in the chosen run, <code>bisect_left</code> returns the run's end, which can be <code>len(nums)</code>."],
                ],
            },
            "One pass: decide which half is sorted": {
                "idea": [
                    "Split at <code>mid</code>: at least one of the two halves is a normal sorted run.",
                    "For the sorted half, a simple range check says whether the target is inside it; if not, it must be in the other half.",
                    "That keeps a single binary search with no separate pivot step.",
                ],
                "steps": [
                    "Set <code>lo, hi = 0, len(nums) - 1</code> and loop while <code>lo &lt;= hi</code>.",
                    "Return <code>mid</code> if <code>nums[mid] == target</code>.",
                    "If <code>nums[lo] &lt;= nums[mid]</code>, the left half is sorted: go left (<code>hi = mid - 1</code>) when <code>nums[lo] &lt;= target &lt; nums[mid]</code>, else go right.",
                    "Otherwise the right half is sorted: go right (<code>lo = mid + 1</code>) when <code>nums[mid] &lt; target &lt;= nums[hi]</code>, else go left.",
                    "Return <code>-1</code> when the range is empty.",
                ],
                "why": [
                    "The rotation point lies in at most one half, so the other half is sorted and its endpoints bound its values exactly. The target is kept in <code>[lo, hi]</code> if present.",
                    "Each iteration halves the range: <strong>O(log n)</strong> time.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=0, hi=6: mid=3 (7). nums[0]=4 ≤ 7, left half sorted; 4 ≤ 1 &lt; 7 fails, so lo=4.",
                        "lo=4, hi=6: mid=5, nums[5] = 1, a match.",
                        "The result is <strong>5</strong>.",
                    ],
                    [
                        "mid=3 (7): left sorted, 4 ≤ 3 fails, so lo=4.",
                        "lo=4, hi=6: mid=5 (1). nums[4]=0 ≤ 1, left sorted; 0 ≤ 3 &lt; 1 fails, so lo=6.",
                        "lo=6, hi=6: mid=6 (2). Left sorted trivially; 2 ≤ 3 &lt; 2 fails, so lo=7.",
                        "lo &gt; hi: the result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>nums[lo] &lt;= nums[mid]</code> with <code>&lt;=</code>?",
                     "When <code>lo == mid</code> the left half is the single element <code>nums[mid]</code>, which is sorted. With <code>&lt;</code> it would be treated as unsorted and the right-half test would be applied to the wrong range: searching <code>[2, 0]</code> for 0 would return -1."],
                    ["Why is one side of each range check strict?",
                     "<code>nums[mid]</code> was already ruled out by the equality test, so the bound at <code>mid</code> is strict while the outer end is inclusive."],
                    ["Does it work with duplicates?",
                     "No. With <code>nums[lo] == nums[mid] == nums[hi]</code> you cannot tell which half is sorted; that is problem II."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search in rotated sorted array II
    "search-rotated-ii": {
        "examples": [
            {"call": "search_rotated_ii([1, 0, 1, 1, 1], 0)", "expect": "True"},
            {"call": "search_rotated_ii([2, 5, 6, 0, 0, 1, 2], 3)", "expect": "False"},
        ],
        "approaches": {
            "Linear scan": {
                "idea": [
                    "The question is only whether the target exists, which <code>in</code> answers directly.",
                    "Duplicates already push the clever solution to O(n) in the worst case, so the scan is a fair baseline here.",
                ],
                "steps": [
                    "Return <code>target in nums</code>.",
                    "It compares elements left to right.",
                    "It stops at the first match.",
                    "It returns <code>False</code> after the last element otherwise.",
                ],
                "why": [
                    "Every element is compared until a match, so the answer is exact.",
                    "<strong>O(n)</strong> time in every bad case.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Compare 1 with 0: no.",
                        "Compare 0 with 0: match.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "Compare 2, 5, 6, 0, 0, 1, 2 with 3.",
                        "No match among all seven.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Is the scan actually worse than the binary search here?",
                     "In the worst case (almost all values equal) both are O(n). On typical inputs the binary search is O(log n)."],
                    ["Why return a bool instead of an index?",
                     "The problem asks only for existence; with duplicates an index would be ambiguous anyway."],
                    ["Should I mention this in an interview?",
                     "Yes, briefly, and point out that duplicates mean no algorithm can guarantee better than O(n)."],
                ],
            },
            "Binary search, shrink both ends on ambiguity": {
                "idea": [
                    "Use the problem I logic: find the sorted half, check whether the target is in its range.",
                    "Duplicates break one case: if <code>nums[lo] == nums[mid] == nums[hi]</code>, either half could contain the rotation.",
                    "In that case the two ends are equal to <code>nums[mid]</code>, which is not the target, so both can be dropped safely.",
                ],
                "steps": [
                    "Loop while <code>lo &lt;= hi</code> with <code>mid = (lo + hi) // 2</code>; return <code>True</code> on a match.",
                    "If <code>nums[lo] == nums[mid] == nums[hi]</code>, set <code>lo, hi = lo + 1, hi - 1</code> and continue.",
                    "Else if <code>nums[lo] &lt;= nums[mid]</code>, the left half is sorted: go left when <code>nums[lo] &lt;= target &lt; nums[mid]</code>, else right.",
                    "Else the right half is sorted: go right when <code>nums[mid] &lt; target &lt;= nums[hi]</code>, else left.",
                    "Return <code>False</code> when the range is empty.",
                ],
                "why": [
                    "Dropping <code>lo</code> and <code>hi</code> is safe because their values equal <code>nums[mid]</code>, already known not to be the target.",
                    "Outside the ambiguous case one half is provably sorted, as in problem I, so the target stays in range.",
                    "Usually <strong>O(log n)</strong>, but an array like [1, 1, 1, 0, 1, 1] can force the shrink step repeatedly: <strong>O(n)</strong> worst case. Space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "lo=0, hi=4: mid=2 (1). nums[0] = nums[2] = nums[4] = 1: ambiguous, so lo=1, hi=3.",
                        "lo=1, hi=3: mid=2 (1). nums[1]=0 ≤ 1, left sorted; 0 ≤ 0 &lt; 1 holds, so hi=1.",
                        "lo=1, hi=1: mid=1, nums[1] = 0, a match.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "lo=0, hi=6: mid=3 (0). Ends are 2, 0, 2: not all equal. 2 ≤ 0 fails, so the right half is sorted; 0 &lt; 3 ≤ 2 fails, so hi=2.",
                        "lo=0, hi=2: mid=1 (5). Left sorted; 2 ≤ 3 &lt; 5 holds, so hi=0.",
                        "lo=0, hi=0: mid=0 (2). 2 ≤ 3 &lt; 2 fails, so lo=1.",
                        "lo &gt; hi: the result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must all three be equal to trigger the shrink?",
                     "If only <code>nums[lo] == nums[mid]</code> but <code>nums[hi]</code> differs, the right half is still identifiable. The shrink is only needed when the comparison gives no information."],
                    ["Can shrinking skip the target?",
                     "No. The removed elements both equal <code>nums[mid]</code>, which already failed the equality test."],
                    ["Why can't any algorithm beat O(n) here?",
                     "In an array of all 1s with one 0 hidden anywhere, every probe that sees a 1 gives no hint where the 0 is, so you may have to look almost everywhere."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ time based key-value store
    "time-based-kv-store": {
        "examples": [
            {"setup": "tm = TimeMap()\ntm.set(\"foo\", \"bar\", 1)\ntm.set(\"foo\", \"bar2\", 4)\ntm.set(\"foo\", \"bar3\", 8)",
             "call": "[tm.get(\"foo\", 0), tm.get(\"foo\", 5), tm.get(\"foo\", 8), tm.get(\"baz\", 9)]",
             "expect": "[\"\", \"bar2\", \"bar3\", \"\"]"},
            {"setup": "tm = TimeMap()\ntm.set(\"a\", \"x\", 2)\ntm.set(\"b\", \"y\", 3)\ntm.set(\"a\", \"z\", 5)",
             "call": "[tm.get(\"a\", 4), tm.get(\"b\", 2), tm.get(\"a\", 10)]",
             "expect": "[\"x\", \"\", \"z\"]"},
        ],
        "approaches": {
            "Scan the key's history": {
                "idea": [
                    "Keep, per key, the list of <code>(timestamp, value)</code> pairs in the order they were set.",
                    "Timestamps arrive increasing, so walking the list backwards finds the newest entry not after the asked time first.",
                ],
                "steps": [
                    "<code>store</code> is a <code>defaultdict(list)</code> from key to its history.",
                    "<code>set</code> appends <code>(timestamp, value)</code> to <code>store[key]</code>.",
                    "<code>get</code> iterates <code>reversed(store[key])</code>.",
                    "The first pair with <code>t &lt;= timestamp</code> is the answer: return its value.",
                    "If none qualifies (or the key is unknown), return <code>\"\"</code>.",
                ],
                "why": [
                    "Because the history is sorted by time, the first qualifying entry seen from the end is the one with the largest valid timestamp.",
                    "<code>set</code> is <strong>O(1)</strong>; <code>get</code> may walk the whole history of a key: <strong>O(n)</strong>.",
                    "Every set is stored once: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "store['foo'] = [(1,'bar'), (4,'bar2'), (8,'bar3')].",
                        "get(foo, 0): 8, 4, 1 are all &gt; 0, so it returns \"\". get(foo, 5): 8 &gt; 5, then 4 ≤ 5 gives 'bar2'.",
                        "get(foo, 8): 8 ≤ 8 gives 'bar3' at once. get(baz, 9): empty history gives \"\".",
                        "The result is <strong>[\"\", \"bar2\", \"bar3\", \"\"]</strong>.",
                    ],
                    [
                        "store['a'] = [(2,'x'), (5,'z')], store['b'] = [(3,'y')].",
                        "get(a, 4): 5 &gt; 4, then 2 ≤ 4 gives 'x'.",
                        "get(b, 2): 3 &gt; 2, nothing left, so \"\". get(a, 10): 5 ≤ 10 gives 'z'.",
                        "The result is <strong>[\"x\", \"\", \"z\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why iterate in reverse?",
                     "The newest valid entry is wanted. From the end, the first match is it; from the front you would have to keep scanning to the last match."],
                    ["Does <code>store[key]</code> in <code>get</code> create entries for unknown keys?",
                     "Yes, the <code>defaultdict</code> adds an empty list. That is harmless for correctness but grows memory with many unknown lookups; <code>self.store.get(key, [])</code> avoids it."],
                    ["When is this good enough?",
                     "When histories per key are short or gets usually ask for recent times, since the reverse walk stops early."],
                ],
            },
            "Binary search each key's sorted timestamps": {
                "idea": [
                    "The timestamps of each key are appended in increasing order, so they form a sorted list for free.",
                    "<code>get</code> needs the last timestamp ≤ the query: that is <code>bisect_right(times, timestamp) - 1</code>.",
                    "Keeping times and values in parallel lists lets <code>bisect</code> work on plain integers.",
                ],
                "steps": [
                    "<code>times[key]</code> and <code>values[key]</code> are parallel lists.",
                    "<code>set</code> appends the timestamp to <code>times[key]</code> and the value to <code>values[key]</code>.",
                    "<code>get</code> computes <code>i = bisect_right(times[key], timestamp) - 1</code>.",
                    "If <code>i &gt;= 0</code>, return <code>values[key][i]</code>.",
                    "Otherwise every stored time is later than the query: return <code>\"\"</code>.",
                ],
                "why": [
                    "<code>bisect_right</code> returns the count of times ≤ the query, so index <code>count - 1</code> is the latest one not after it.",
                    "<code>set</code> is <strong>O(1)</strong> amortised; <code>get</code> is <strong>O(log n)</strong> for a key with n entries.",
                    "Each set stores one timestamp and one value: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "times['foo'] = [1, 4, 8], values = ['bar', 'bar2', 'bar3'].",
                        "get(foo, 0): bisect_right = 0, i = −1, so \"\". get(foo, 5): bisect_right = 2, i = 1, 'bar2'.",
                        "get(foo, 8): bisect_right = 3, i = 2, 'bar3'. get(baz, 9): empty list, i = −1, \"\".",
                        "The result is <strong>[\"\", \"bar2\", \"bar3\", \"\"]</strong>.",
                    ],
                    [
                        "times['a'] = [2, 5], times['b'] = [3].",
                        "get(a, 4): bisect_right = 1, i = 0, 'x'.",
                        "get(b, 2): bisect_right = 0, i = −1, \"\". get(a, 10): bisect_right = 2, i = 1, 'z'.",
                        "The result is <strong>[\"x\", \"\", \"z\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>bisect_right</code> and not <code>bisect_left</code>?",
                     "When the query equals a stored time, that entry must be returned. <code>bisect_right</code> places the cut after it; <code>bisect_left</code> would put it before and return the older value."],
                    ["What if timestamps were not increasing?",
                     "Then appending would break the sorted order; you would need <code>bisect.insort</code> (O(n) per set) or a balanced tree."],
                    ["Why two lists instead of one list of tuples?",
                     "Bisecting tuples needs a probe like <code>(timestamp, chr(127))</code> to handle ties; separate lists keep the bisect a plain integer search."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ split array largest sum
    "split-array-largest-sum": {
        "examples": [
            {"call": "split_array([7, 2, 5, 10, 8], 2)", "expect": "18"},
            {"call": "split_array([1, 4, 4], 3)", "expect": "4"},
        ],
        "approaches": {
            "Try every split recursively": {
                "idea": [
                    "Choose where the first part ends, then split the rest into <code>parts - 1</code> parts the same way.",
                    "The cost of a choice is the larger of the first part's sum and the best result for the rest; take the minimum over all choices.",
                ],
                "steps": [
                    "<code>best(i, parts)</code> is the best largest-sum for <code>nums[i:]</code> in <code>parts</code> parts.",
                    "If <code>parts == 1</code>, the rest is one part: return <code>sum(nums[i:])</code>.",
                    "Otherwise let the first part end at <code>j</code>, from <code>i</code> up to <code>len(nums) - parts</code>, leaving at least one element per remaining part.",
                    "Keep a running <code>total</code> of <code>nums[i..j]</code> and score <code>max(total, best(j + 1, parts - 1))</code>.",
                    "Return the smallest score; the answer is <code>best(0, k)</code>.",
                ],
                "why": [
                    "Every way to place the k − 1 cuts is generated exactly once, so the minimum over them is the true optimum.",
                    "There are C(n − 1, k − 1) ways to cut, up to <strong>O(n<sup>k</sup>)</strong> calls, because subproblems are recomputed.",
                    "Recursion depth is k: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "best(0, 2): the first part ends at j = 0..3; the second part takes the rest of the total 32.",
                        "j=0: max(7, 25) = 25. j=1: max(9, 23) = 23.",
                        "j=2: max(14, 18) = 18. j=3: max(24, 8) = 24.",
                        "The minimum is <strong>18</strong>, from [7, 2, 5] | [10, 8].",
                    ],
                    [
                        "best(0, 3): j can only be 0, since two more parts need two elements.",
                        "best(1, 2): j can only be 1: max(4, best(2, 1) = 4) = 4.",
                        "best(0, 3) = max(1, 4) = 4: every element is its own part.",
                        "The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>j</code> stop at <code>len(nums) - parts</code>?",
                     "Each later part needs at least one element. Stopping earlier would allow empty parts, whose <code>best</code> would be <code>inf</code> or a wrong 0."],
                    ["Why is <code>result</code> started at infinity?",
                     "So the first real candidate always replaces it inside <code>min</code>."],
                    ["What makes this slow?",
                     "<code>best(j, p)</code> is solved again for every way of reaching <code>j</code>. Caching it gives the DP approach."],
                ],
            },
            "DP over (start, parts left)": {
                "idea": [
                    "The recursive answer depends only on <code>(i, parts)</code>, and there are just n · k such pairs, so cache them.",
                    "Prefix sums <code>P</code> turn every \"sum of nums[i..j]\" into one subtraction.",
                ],
                "steps": [
                    "Build <code>P</code> with <code>P[t]</code> = sum of the first t numbers.",
                    "<code>best(i, parts)</code> is cached with <code>@cache</code>.",
                    "If <code>parts == 1</code>, return <code>P[n] - P[i]</code>.",
                    "Otherwise return the minimum over <code>j</code> in <code>[i, n - parts]</code> of <code>max(P[j + 1] - P[i], best(j + 1, parts - 1))</code>.",
                    "The answer is <code>best(0, k)</code>.",
                ],
                "why": [
                    "Same recurrence as the brute force, so it explores every split; caching only avoids repeating work.",
                    "n · k states, each scanning up to n values of <code>j</code>: <strong>O(k · n²)</strong> time.",
                    "The cache holds n · k results and the recursion is k deep: <strong>O(k · n)</strong> space.",
                ],
                "dry": [
                    [
                        "P = [0, 7, 9, 14, 24, 32].",
                        "best(0, 2) tries j = 0..3 with best(j+1, 1) = 32 − P[j+1]: scores 25, 23, 18, 24.",
                        "Each best(t, 1) is a single subtraction.",
                        "The result is <strong>18</strong>.",
                    ],
                    [
                        "P = [0, 1, 5, 9].",
                        "best(0, 3) tries only j = 0: max(1, best(1, 2)).",
                        "best(1, 2) tries only j = 1: max(P[2] − P[1] = 4, best(2, 1) = 4) = 4.",
                        "best(0, 3) = 4. The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why prefix sums instead of a running total?",
                     "Inside a generator expression there is no convenient place to keep a running total; <code>P[j + 1] - P[i]</code> gives the same value in O(1)."],
                    ["Is this fast enough for n = 1000, k = 50?",
                     "About 50 million steps, slow in Python. The binary search approach is much faster."],
                    ["Can it be done bottom-up?",
                     "Yes, fill <code>dp[parts][i]</code> for parts = 1..k. It avoids recursion limits but has the same complexity."],
                ],
            },
            "Binary search on the largest sum": {
                "idea": [
                    "Flip the question: for a cap <code>C</code>, how many parts are needed so that no part exceeds C? Greedy filling answers that.",
                    "A larger cap never needs more parts, so \"needs ≤ k parts\" is false then true as C grows. Binary search for the first true.",
                ],
                "steps": [
                    "<code>parts_needed(cap)</code>: start with one part, add numbers to <code>total</code>, and open a new part when the next number would exceed <code>cap</code>.",
                    "Search <code>lo, hi = max(nums), sum(nums)</code>.",
                    "While <code>lo &lt; hi</code>, take <code>mid</code>.",
                    "If <code>parts_needed(mid) &lt;= k</code>, <code>mid</code> is achievable: <code>hi = mid</code>.",
                    "Otherwise <code>lo = mid + 1</code>.",
                    "Return <code>lo</code>.",
                ],
                "why": [
                    "If the greedy needs at most k parts under a cap, splitting one of its parts further reaches exactly k without raising any sum, so the cap is achievable; the minimum achievable cap is the answer.",
                    "O(log(sum)) probes of an O(n) check: <strong>O(n log(sum))</strong> time.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo=10, hi=32: mid=21 → [7,2,5] [10,8] = 2 parts, so hi=21.",
                        "mid=15 → [7,2,5] [10] [8] = 3 parts, so lo=16.",
                        "mid=18 → [7,2,5] [10,8] = 2, so hi=18. mid=17 → 3 parts, so lo=18.",
                        "lo == hi == 18. The result is <strong>18</strong>.",
                    ],
                    [
                        "lo=4, hi=9: mid=6 → [1,4] [4] = 2 parts ≤ 3, so hi=6.",
                        "mid=5 → [1,4] [4] = 2, so hi=5.",
                        "mid=4 → [1] [4] [4] = 3 ≤ 3, so hi=4.",
                        "lo == hi == 4. The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["What if the greedy uses fewer than k parts?",
                     "That is fine. Any part with two or more elements can be split without increasing the maximum, so fewer parts can always be turned into exactly k (n ≥ k is guaranteed)."],
                    ["Why <code>lo = max(nums)</code>?",
                     "Some part contains the largest element, so no answer can be smaller. It also guarantees every single number fits in a part."],
                    ["Does this work with zeros?",
                     "Yes. Zeros never force a new part, and they can be split off freely to reach k parts."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ median of two sorted arrays
    "median-two-sorted-arrays": {
        "examples": [
            {"call": "find_median_sorted_arrays([1, 3, 8, 9], [2, 5, 7])", "expect": "5"},
            {"call": "find_median_sorted_arrays([1, 2], [3, 4])", "expect": "2.5"},
        ],
        "approaches": {
            "Merge fully, pick the middle": {
                "idea": [
                    "Merge the two sorted arrays into one sorted array, as in merge sort.",
                    "The median is then the middle element, or the average of the two middle elements for an even length.",
                ],
                "steps": [
                    "Walk <code>i</code> over <code>a</code> and <code>j</code> over <code>b</code>, appending the smaller front value to <code>merged</code>.",
                    "When one array runs out, append the rest of the other: <code>merged += a[i:] + b[j:]</code>.",
                    "Let <code>n = len(merged)</code>.",
                    "For odd n return <code>merged[n // 2]</code>; for even n return the average of <code>merged[n // 2 - 1]</code> and <code>merged[n // 2]</code>.",
                ],
                "why": [
                    "The merge produces the sorted union, so its middle is by definition the median.",
                    "Each element is appended once: <strong>O(m + n)</strong> time.",
                    "<code>merged</code> stores all elements: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "Merge: 1 (a), 2 (b), 3 (a), 5 (b), 7 (b), 8 (a).",
                        "<code>b</code> is used up; append the rest of <code>a</code>: 9.",
                        "merged = [1, 2, 3, 5, 7, 8, 9], n = 7, odd.",
                        "merged[3] is <strong>5</strong>.",
                    ],
                    [
                        "Merge: 1, 2 from a; a is used up, append 3, 4.",
                        "merged = [1, 2, 3, 4], n = 4, even.",
                        "(merged[1] + merged[2]) / 2 = (2 + 3) / 2 = <strong>2.5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> in <code>a[i] &lt;= b[j]</code>?",
                     "Either works for the median; <code>&lt;=</code> keeps the merge stable, taking ties from <code>a</code> first."],
                    ["Isn't <code>sorted(a + b)</code> simpler?",
                     "Yes, but it is O((m + n) log(m + n)) and ignores that both inputs are already sorted."],
                    ["Why does the even case return a float?",
                     "<code>/</code> always gives a float in Python 3, matching the expected 2.5."],
                ],
            },
            "Walk to the middle without storing": {
                "idea": [
                    "The median only needs the element at position <code>total // 2</code> and, for even totals, the one before it.",
                    "Run the merge just that far, remembering only the last two values taken.",
                ],
                "steps": [
                    "Set <code>total = len(a) + len(b)</code>, <code>i = j = 0</code> and <code>prev = cur = 0</code>.",
                    "Repeat <code>total // 2 + 1</code> times: move <code>cur</code> into <code>prev</code>.",
                    "Take from <code>a</code> if <code>b</code> is exhausted or <code>a[i] &lt;= b[j]</code> (with <code>a</code> not exhausted); otherwise take from <code>b</code>. Store it in <code>cur</code>.",
                    "For odd totals return <code>cur</code>; for even totals return <code>(prev + cur) / 2</code>.",
                ],
                "why": [
                    "After t steps, <code>cur</code> is the t-th smallest element of the union, so after <code>total // 2 + 1</code> steps it is the upper middle and <code>prev</code> the lower middle.",
                    "About half the elements are visited: <strong>O(m + n)</strong> time.",
                    "Only indices and two values: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "total = 7, so 4 steps.",
                        "Step 1: cur=1 (a). Step 2: cur=2 (b). Step 3: cur=3 (a).",
                        "Step 4: a[2]=8 &gt; b[1]=5, so cur=5, prev=3.",
                        "Odd total: the result is <strong>5</strong>.",
                    ],
                    [
                        "total = 4, so 3 steps.",
                        "Step 1: cur=1. Step 2: cur=2, prev=1.",
                        "Step 3: a is exhausted, take b[0]: cur=3, prev=2.",
                        "Even total: (2 + 3) / 2 = <strong>2.5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>total // 2 + 1</code> steps?",
                     "Indices start at 0, so the element at index <code>total // 2</code> is the <code>(total // 2 + 1)</code>-th one taken."],
                    ["Why test <code>j &gt;= len(b)</code> first?",
                     "Short-circuiting stops <code>b[j]</code> from being read once <code>b</code> is used up. The <code>i &lt; len(a)</code> check guards <code>a[i]</code> the same way."],
                    ["Is it really better than merging?",
                     "Same O(m + n) time but O(1) space, and it stops halfway."],
                ],
            },
            "Binary search the partition of the shorter array": {
                "idea": [
                    "Cut <code>a</code> after <code>i</code> elements and <code>b</code> after <code>j</code> elements so that the left sides together hold <code>half = (m + n + 1) // 2</code> elements.",
                    "The cut is right when every left value is ≤ every right value: <code>a_left ≤ b_right</code> and <code>b_left ≤ a_right</code>. Then the median sits at the cut.",
                    "Choosing <code>i</code> fixes <code>j = half - i</code>, so only <code>i</code> is searched, over the shorter array.",
                ],
                "steps": [
                    "Swap so <code>a</code> is the shorter array; set <code>half</code> and <code>lo, hi = 0, m</code>.",
                    "Take <code>i = (lo + hi) // 2</code> and <code>j = half - i</code>.",
                    "Read the four border values, using <code>-INF</code>/<code>INF</code> when a side is empty.",
                    "If <code>a_left &lt;= b_right</code> and <code>b_left &lt;= a_right</code>, return <code>max(a_left, b_left)</code> for odd totals, or its average with <code>min(a_right, b_right)</code> for even ones.",
                    "If <code>a_left &gt; b_right</code>, too many came from <code>a</code>: <code>hi = i - 1</code>. Otherwise too few: <code>lo = i + 1</code>.",
                ],
                "why": [
                    "With a correct cut, the left side is exactly the smallest <code>half</code> elements, so the largest left value is the (lower) median and the smallest right value is the next one.",
                    "When <code>a_left &gt; b_right</code>, any larger <code>i</code> makes it worse, so the search direction is always right.",
                    "Binary search over <code>0..min(m, n)</code>: <strong>O(log min(m, n))</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Swap: a = [2, 5, 7], b = [1, 3, 8, 9], half = 4, lo=0, hi=3.",
                        "i=1, j=3: a_left=2, a_right=5, b_left=8, b_right=9. b_left 8 &gt; a_right 5, so lo=2.",
                        "i=2, j=2: a_left=5, a_right=7, b_left=3, b_right=8. Both checks hold.",
                        "Odd total: max(5, 3) = <strong>5</strong>.",
                    ],
                    [
                        "No swap: m = n = 2, half = 2, lo=0, hi=2.",
                        "i=1, j=1: a_left=1, a_right=2, b_left=3, b_right=4. 3 &gt; 2, so lo=2.",
                        "i=2, j=0: a_left=2, a_right=INF, b_left=−INF, b_right=3. Both checks hold.",
                        "Even total: (max(2, −INF) + min(INF, 3)) / 2 = <strong>2.5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why search the shorter array?",
                     "It makes <code>j = half - i</code> always land in <code>0..n</code>. Searching the longer array could produce a negative <code>j</code>, and it is also slower."],
                    ["Why <code>half = (m + n + 1) // 2</code>?",
                     "For odd totals it puts the median on the left side, so <code>max(a_left, b_left)</code> is the answer without extra cases."],
                    ["Why use infinities?",
                     "When a side of the cut is empty (i = 0 or i = m, and the same for j), the comparison with it must always pass. ±INF does that without special branches."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find in mountain array
    "find-in-mountain-array": {
        "examples": [
            {"setup": "class MountainArray:\n    def __init__(self, arr):\n        self.arr = arr\n    def get(self, i):\n        return self.arr[i]\n    def length(self):\n        return len(self.arr)",
             "call": "find_in_mountain_array(3, MountainArray([1, 2, 3, 4, 5, 3, 1]))", "expect": "2"},
            {"setup": "class MountainArray:\n    def __init__(self, arr):\n        self.arr = arr\n    def get(self, i):\n        return self.arr[i]\n    def length(self):\n        return len(self.arr)",
             "call": "find_in_mountain_array(3, MountainArray([0, 1, 2, 4, 2, 1]))", "expect": "-1"},
        ],
        "approaches": {
            "Scan every index": {
                "idea": [
                    "Read indices from the left and return the first one holding the target.",
                    "Scanning from the left automatically returns the smaller index when the value appears on both slopes.",
                ],
                "steps": [
                    "Loop <code>i</code> over <code>range(mountain.length())</code>.",
                    "Call <code>mountain.get(i)</code>.",
                    "If it equals <code>target</code>, return <code>i</code>.",
                    "After the loop, return <code>-1</code>.",
                ],
                "why": [
                    "Every index is checked in order, so the first (minimum) index of the target is found.",
                    "Up to n <code>get</code> calls: <strong>O(n)</strong> calls, too many for the 100-call limit when n is large.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "get(0) = 1, get(1) = 2: no match.",
                        "get(2) = 3: match.",
                        "Three calls; the result is <strong>2</strong>.",
                    ],
                    [
                        "get(0..5) return 0, 1, 2, 4, 2, 1.",
                        "None is 3; the array jumps from 2 to 4 on the way up.",
                        "Six calls; the result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is this rejected by the judge?",
                     "The interface allows only 100 <code>get</code> calls and arrays can have 10,000 elements."],
                    ["Does it return the smaller index for duplicates on both sides?",
                     "Yes, since it scans from index 0."],
                    ["Could I cache the values?",
                     "Caching reduces repeated calls but not the n distinct ones a scan needs."],
                ],
            },
            "Peak search, then two binary searches": {
                "idea": [
                    "A mountain is an increasing run then a decreasing run, both sorted, joined at the peak.",
                    "Find the peak by comparing <code>get(mid)</code> with <code>get(mid + 1)</code>: rising means the peak is to the right.",
                    "Then binary search the rising side first (it holds the smaller index), and the falling side only if needed.",
                ],
                "steps": [
                    "Peak: <code>lo, hi = 0, n - 1</code>; while <code>lo &lt; hi</code>, if <code>get(mid) &lt; get(mid + 1)</code> set <code>lo = mid + 1</code>, else <code>hi = mid</code>. Then <code>peak = lo</code>.",
                    "<code>search(lo, hi, ascending)</code> is a normal binary search; the direction is flipped by <code>(v &lt; target) == ascending</code>.",
                    "Run <code>search(0, peak, True)</code> on the rising side.",
                    "If that returns -1, run <code>search(peak + 1, n - 1, False)</code> on the falling side.",
                    "Return whatever is found, or -1.",
                ],
                "why": [
                    "Peak search: if <code>get(mid) &lt; get(mid + 1)</code>, <code>mid</code> is on the rising slope and the peak is right of it; otherwise the peak is at <code>mid</code> or left.",
                    "Each side is sorted, so binary search is valid on it, and checking the rising side first returns the minimum index.",
                    "Three binary searches: <strong>O(log n)</strong> <code>get</code> calls, about 3 · 14 + 14 for n = 10,000, under the limit. Space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "Peak: mid=3, 4 &lt; 5 → lo=4. mid=5, 3 &lt; 1 fails → hi=5. mid=4, 5 &lt; 3 fails → hi=4. peak = 4.",
                        "search(0, 4, True): mid=2, v=3 equals the target.",
                        "The falling side is never searched.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "Peak: mid=2, 2 &lt; 4 → lo=3. mid=4, 2 &lt; 1 fails → hi=4. mid=3, 4 &lt; 2 fails → hi=3. peak = 3.",
                        "search(0, 3, True): mid=1 (1 &lt; 3) → lo=2; mid=2 (2 &lt; 3) → lo=3; mid=3 (4 &gt; 3) → hi=2. Not found.",
                        "search(4, 5, False): mid=4, v=2 &lt; 3 on a falling side means go left: hi=3. Not found.",
                        "The result is <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["How does <code>(v &lt; target) == ascending</code> work?",
                     "On the rising side a too-small value means go right; on the falling side a too-small value means go left. Comparing the test with <code>ascending</code> flips the direction in one line."],
                    ["Why search the rising side first?",
                     "The problem asks for the minimum index, and every index on the rising side is smaller than every index on the falling side."],
                    ["Can <code>mid + 1</code> go out of range in the peak search?",
                     "No. Inside <code>while lo &lt; hi</code>, <code>mid &lt; hi ≤ n - 1</code>, so <code>mid + 1 ≤ n - 1</code>."],
                ],
            },
        },
    },
}
