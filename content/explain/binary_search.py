"""Write-ups for the Binary Search topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ binary search
    "binary-search": {
        "example": {"call": "search([-1, 0, 3, 5, 9, 12], 9)", "expect": "4"},
        "approaches": {
            "Linear scan": {
                "idea": [
                    "Check every element from the left until the target turns up.",
                    "It works on any array, which is exactly why it wastes the fact that this one is sorted.",
                ],
                "steps": [
                    "Return the first index whose value equals the target, or -1.",
                ],
                "why": [
                    "It looks at every element in the worst case: O(n) time, O(1) space.",
                ],
                "dry": [
                    "Compare -1, 0, 3 and 5: no match.",
                    "Index 4 holds 9, so the result is <strong>4</strong> after five comparisons.",
                ],
            },
            "Recursive binary search": {
                "idea": [
                    "In a sorted array, one comparison with the middle element rules out half of the array.",
                    "If the middle value is too small, the target can only be to its right; if it is too big, only to its left.",
                    "Recurse into the half that can still contain the target.",
                ],
                "steps": [
                    "<code>go(lo, hi)</code>: an empty range (lo &gt; hi) means not found.",
                    "<code>mid = (lo + hi) // 2</code>; return mid on a match.",
                    "Recurse right if <code>nums[mid] &lt; target</code>, otherwise left.",
                ],
                "why": [
                    "The target, if present, always stays inside [lo, hi].",
                    "The range halves each call: O(log n) time, with O(log n) stack frames.",
                ],
                "dry": [
                    "go(0, 5): mid = 2 holds 3, which is less than 9, so go(3, 5).",
                    "go(3, 5): mid = 4 holds 9, a match.",
                    "The result is <strong>4</strong> after two comparisons.",
                ],
            },
            "Iterative binary search": {
                "idea": [
                    "The same halving in a loop, so there is no recursion.",
                    "Keep the invariant: if the target is present, it lies in [lo, hi]. Loop while that range is non-empty.",
                ],
                "steps": [
                    "<code>lo, hi = 0, n - 1</code>.",
                    "While <code>lo &lt;= hi</code>: compare <code>nums[mid]</code>; return on a match, otherwise move <code>lo = mid + 1</code> or <code>hi = mid - 1</code>.",
                    "Return -1 when the range is empty.",
                ],
                "why": [
                    "Each step discards a half that cannot contain the target.",
                    "It is O(log n) time and O(1) space. In fixed-width languages, write <code>lo + (hi - lo) // 2</code> to avoid overflow.",
                ],
                "dry": [
                    "lo = 0, hi = 5: mid = 2 holds 3, less than 9, so lo = 3.",
                    "lo = 3, hi = 5: mid = 4 holds 9, so the result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search insert position
    "search-insert-position": {
        "example": {"call": "search_insert([1, 3, 5, 6, 8, 10], 7)", "expect": "4"},
        "approaches": {
            "Linear scan for the first value &ge; target": {
                "idea": [
                    "The insert position is the index of the first value that is at least the target, or the end of the array if there is none.",
                ],
                "steps": [
                    "Return the first i with <code>nums[i] &gt;= target</code>, otherwise <code>len(nums)</code>.",
                ],
                "why": [
                    "It reads the definition directly: O(n) time.",
                ],
                "dry": [
                    "1, 3, 5 and 6 are all less than 7.",
                    "8 at index 4 is the first value ≥ 7, so the result is <strong>4</strong>.",
                ],
            },
            "Lower bound on a half-open range": {
                "idea": [
                    "Search the half-open range <code>[lo, hi)</code> with <code>hi = len(nums)</code>, because the answer can be one past the end.",
                    "If <code>nums[mid] &lt; target</code>, the answer is strictly after mid. Otherwise mid itself may be the answer, so keep it with <code>hi = mid</code>.",
                    "When lo meets hi, a single position is left, and that is the answer. No \"not found\" special case is needed.",
                ],
                "steps": [
                    "<code>lo, hi = 0, len(nums)</code>.",
                    "While <code>lo &lt; hi</code>: move <code>lo = mid + 1</code> if <code>nums[mid] &lt; target</code>, otherwise <code>hi = mid</code>.",
                    "Return <code>lo</code>.",
                ],
                "why": [
                    "Invariant: everything before lo is less than the target, and everything from hi on is at least the target.",
                    "It is O(log n) time; it is exactly <code>bisect.bisect_left</code>.",
                ],
                "dry": [
                    "lo = 0, hi = 6: mid = 3 holds 6, less than 7, so lo = 4.",
                    "lo = 4, hi = 6: mid = 5 holds 10, not less, so hi = 5.",
                    "lo = 4, hi = 5: mid = 4 holds 8, not less, so hi = 4.",
                    "lo == hi = <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ guess number
    "guess-number": {
        "example": {"setup": "PICK = 37\ndef guess(num):\n    return 0 if num == PICK else (-1 if PICK < num else 1)",
                    "call": "guess_number(100)", "expect": "37"},
        "approaches": {
            "Try every number": {
                "idea": [
                    "Guess 1, 2, 3, … in order and ignore the higher/lower hints.",
                ],
                "steps": [
                    "For k from 1 to n, return k when <code>guess(k) == 0</code>.",
                ],
                "why": [
                    "It always finds the pick, but takes up to n calls.",
                ],
                "dry": [
                    "Guesses 1 to 36 all get the answer \"higher\".",
                    "Guess 37 returns 0, so the result is <strong>37</strong> after 37 calls.",
                ],
            },
            "Binary search on the range": {
                "idea": [
                    "Each hint tells which half of the remaining range holds the pick, so always guess the middle.",
                    "Every answer halves the range: at most about log<sub>2</sub> n + 1 guesses, 32 for n = 2<sup>31</sup>.",
                ],
                "steps": [
                    "<code>lo, hi = 1, n</code>; guess <code>mid</code>.",
                    "0 means found. -1 means the pick is lower, so <code>hi = mid - 1</code>. 1 means higher, so <code>lo = mid + 1</code>.",
                ],
                "why": [
                    "The pick always stays inside [lo, hi].",
                    "It makes O(log n) calls with O(1) space.",
                ],
                "dry": [
                    "Range [1, 100]: guess 50, the answer is \"lower\", so hi = 49.",
                    "Range [1, 49]: guess 25, the answer is \"higher\", so lo = 26.",
                    "Range [26, 49]: guess 37, correct.",
                    "The result is <strong>37</strong> after 3 calls.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sqrt(x)
    "sqrt-x": {
        "example": {"call": "my_sqrt(30)", "expect": "5"},
        "approaches": {
            "Count up": {
                "idea": [
                    "The answer is the largest k with k² ≤ x. Count k upwards while the next square still fits.",
                ],
                "steps": [
                    "<code>k = 0</code>; while <code>(k + 1)² &lt;= x</code>, increment k.",
                ],
                "why": [
                    "It stops exactly at the floor of the square root.",
                    "It takes O(√x) steps, about 46,000 for x = 2<sup>31</sup>.",
                ],
                "dry": [
                    "1, 4, 9, 16 and 25 are all ≤ 30, so k climbs to 5.",
                    "36 &gt; 30, so stop. The result is <strong>5</strong>.",
                ],
            },
            "Binary search on the answer": {
                "idea": [
                    "\"k² ≤ x\" is true up to some k and false after it, so binary-search the last k where it holds.",
                    "On success move <code>lo = mid</code>, since mid could be the answer. That needs the upper middle <code>(lo + hi + 1) // 2</code>, or the loop could get stuck when two candidates remain.",
                ],
                "steps": [
                    "<code>lo, hi = 0, x</code>.",
                    "<code>mid = (lo + hi + 1) // 2</code>; if <code>mid² &lt;= x</code>, set <code>lo = mid</code>, otherwise <code>hi = mid - 1</code>.",
                    "Return <code>lo</code>.",
                ],
                "why": [
                    "Invariant: lo² ≤ x, and every value above hi squares to more than x.",
                    "It is O(log x) time and O(1) space.",
                ],
                "dry": [
                    "[0, 30]: mid 15, 225 &gt; 30, so hi = 14. [0, 14]: mid 7, 49 &gt; 30, so hi = 6.",
                    "[0, 6]: mid 3, 9 ≤ 30, so lo = 3. [3, 6]: mid 5, 25 ≤ 30, so lo = 5.",
                    "[5, 6]: the upper middle is 6, and 36 &gt; 30, so hi = 5.",
                    "lo = hi = <strong>5</strong>.",
                ],
            },
            "Newton's method on integers": {
                "idea": [
                    "Newton's iteration for k² = x replaces k with the average of k and x/k.",
                    "Starting from any k ≥ √x, the integer version <code>k = (k + x // k) // 2</code> decreases steadily to the floor of the root.",
                    "The number of correct digits roughly doubles each step, which is essentially how <code>math.isqrt</code> works.",
                ],
                "steps": [
                    "Return x for x &lt; 2.",
                    "Start at k = x; while <code>k² &gt; x</code>, set <code>k = (k + x // k) // 2</code>.",
                ],
                "why": [
                    "It converges very fast, in O(log log x) iterations once close, using O(1) space.",
                ],
                "dry": [
                    "k = 30: 900 &gt; 30, so k = (30 + 1) // 2 = 15.",
                    "225 &gt; 30, so k = (15 + 2) // 2 = 8.",
                    "64 &gt; 30, so k = (8 + 3) // 2 = 5.",
                    "25 ≤ 30, so stop. The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search a 2D matrix
    "search-2d-matrix": {
        "example": {"call": "search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 16)", "expect": "True"},
        "approaches": {
            "Scan everything": {
                "idea": [
                    "Check every row for the target, ignoring the ordering entirely.",
                ],
                "steps": [
                    "<code>any(target in row for row in matrix)</code>.",
                ],
                "why": [
                    "It is O(m·n) time.",
                ],
                "dry": [
                    "Row 0 does not contain 16.",
                    "Row 1 does, so the result is <strong>True</strong>.",
                ],
            },
            "Staircase from the top-right": {
                "idea": [
                    "Start at the top-right corner, the largest value in its row and the smallest in its column.",
                    "If it is larger than the target, the whole column below is larger too: move left. If it is smaller, the whole row to the left is smaller: move down.",
                    "Each step discards a full row or column.",
                ],
                "steps": [
                    "<code>r = 0</code>, <code>c = last column</code>.",
                    "Equal: found. Too big: <code>c -= 1</code>. Too small: <code>r += 1</code>.",
                ],
                "why": [
                    "It only needs each row and each column to be sorted, so it also solves the harder LeetCode 240.",
                    "It is O(m + n) time.",
                ],
                "dry": [
                    "(0, 3) = 7 &lt; 16, so move down.",
                    "(1, 3) = 20 &gt; 16, so move left.",
                    "(1, 2) = 16, so the result is <strong>True</strong>.",
                ],
            },
            "Binary search the row, then the column": {
                "idea": [
                    "Rows are in order too: each row starts above the previous row's end.",
                    "So binary-search the first column for the last row whose first value is ≤ the target, then binary-search inside that row.",
                ],
                "steps": [
                    "<code>r = bisect_right(firsts, target) - 1</code>; a negative r means the target is too small.",
                    "<code>i = bisect_left(row, target)</code>; check <code>row[i] == target</code>.",
                ],
                "why": [
                    "Only that row can contain the target.",
                    "It is O(log m + log n), the same as one search over m·n values.",
                ],
                "dry": [
                    "firsts = [1, 10, 23], and bisect_right for 16 gives 2, so r = 1.",
                    "In [10, 11, 16, 20], bisect_left for 16 gives 2, and row[2] = 16.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "One binary search over the flattened index": {
                "idea": [
                    "Read row by row, the matrix is one sorted list of m·n values.",
                    "Binary-search positions 0..m·n - 1 and turn each position k into the cell <code>(k // n, k % n)</code>.",
                ],
                "steps": [
                    "<code>lo, hi = 0, m·n - 1</code>.",
                    "<code>v = matrix[mid // n][mid % n]</code>; compare it and move lo or hi as usual.",
                ],
                "why": [
                    "It is plain binary search over a virtual sorted array: O(log(m·n)) time and O(1) space.",
                ],
                "dry": [
                    "lo = 0, hi = 11: mid 5 is cell (1, 1) = 11 &lt; 16, so lo = 6.",
                    "mid 8 is cell (2, 0) = 23 &gt; 16, so hi = 7.",
                    "mid 6 is cell (1, 2) = 16, a match: <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ koko eating bananas
    "koko-eating-bananas": {
        "example": {"call": "min_eating_speed([3, 6, 7, 11], 8)", "expect": "4"},
        "approaches": {
            "Try every speed from 1 upward": {
                "idea": [
                    "At speed k, a pile of p bananas takes <code>ceil(p / k)</code> hours.",
                    "Try speeds 1, 2, 3, … and return the first one whose total time fits within h.",
                ],
                "steps": [
                    "Total hours: <code>sum((p + k - 1) // k)</code>, using integer ceiling division.",
                    "Increase k until the total is ≤ h.",
                ],
                "why": [
                    "The first speed that works is the minimum.",
                    "The answer can be as large as the biggest pile (10<sup>9</sup>): O(max · n).",
                ],
                "dry": [
                    "k=1: 27 hours. k=2: 2 + 3 + 4 + 6 = 15 hours.",
                    "k=3: 1 + 2 + 3 + 4 = 10 hours.",
                    "k=4: 1 + 2 + 2 + 3 = 8 ≤ 8, so the result is <strong>4</strong>.",
                ],
            },
            "Binary search on the speed": {
                "idea": [
                    "Eating faster never takes longer, so \"k is fast enough\" is false up to some speed and true from then on.",
                    "Binary-search the smallest feasible speed in [1, max(piles)]; at the maximum, every pile takes one hour.",
                ],
                "steps": [
                    "<code>lo, hi = 1, max(piles)</code>.",
                    "If <code>hours(mid) &lt;= h</code>, then <code>hi = mid</code> (try slower); otherwise <code>lo = mid + 1</code>.",
                ],
                "why": [
                    "Monotonic feasibility makes binary search valid.",
                    "There are O(log max) checks of O(n) each: O(n log max) time.",
                ],
                "dry": [
                    "[1, 11]: mid 6 takes 1 + 1 + 2 + 2 = 6 ≤ 8 hours, so hi = 6.",
                    "[1, 6]: mid 3 takes 10 &gt; 8, so lo = 4.",
                    "[4, 6]: mid 5 takes 1 + 2 + 2 + 3 = 8 ≤ 8, so hi = 5.",
                    "[4, 5]: mid 4 takes 8 ≤ 8, so hi = 4. The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ ship within days
    "ship-within-days": {
        "example": {"call": "ship_within_days([3, 2, 2, 4, 1, 4], 3)", "expect": "6"},
        "approaches": {
            "Try every capacity upward": {
                "idea": [
                    "For a given capacity, the fewest days come from loading each day as full as possible (a greedy count).",
                    "Try capacities from the heaviest package upwards until the day count fits.",
                ],
                "steps": [
                    "<code>days_needed(cap)</code>: start a new day whenever the next package would overflow.",
                    "Increase cap from <code>max(weights)</code> until <code>days_needed(cap) &lt;= days</code>.",
                ],
                "why": [
                    "Filling each day greedily is optimal, since starting a day early never helps.",
                    "It takes O(n) per capacity, across up to sum - max capacities.",
                ],
                "dry": [
                    "cap 4: [3], [2, 2], [4], [1], [4] is 5 days.",
                    "cap 5: [3], [2, 2], [4, 1], [4] is 4 days.",
                    "cap 6: [3, 2], [2, 4], [1, 4] is 3 days, so the result is <strong>6</strong>.",
                ],
            },
            "Binary search on capacity with a greedy check": {
                "idea": [
                    "More capacity never needs more days, so feasibility is monotonic.",
                    "Binary-search the smallest feasible capacity between the heaviest package and the total weight.",
                ],
                "steps": [
                    "<code>lo, hi = max(weights), sum(weights)</code>.",
                    "Feasible mid means <code>hi = mid</code>; otherwise <code>lo = mid + 1</code>.",
                ],
                "why": [
                    "The greedy check is exact, and binary search finds the threshold.",
                    "It is O(n log(sum)) time and O(1) space.",
                ],
                "dry": [
                    "[4, 16]: mid 10 takes [3, 2, 2], [4, 1, 4], 2 days, so hi = 10.",
                    "[4, 10]: mid 7 takes [3, 2, 2], [4, 1], [4], 3 days, so hi = 7.",
                    "[4, 7]: mid 5 takes 4 days, so lo = 6.",
                    "[6, 7]: mid 6 takes 3 days, so hi = 6. The result is <strong>6</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find min in rotated
    "find-min-rotated": {
        "example": {"call": "find_min([4, 5, 6, 7, 0, 1, 2])", "expect": "0"},
        "approaches": {
            "Linear scan": {
                "idea": [
                    "Take <code>min(nums)</code>, ignoring the rotated-sorted structure.",
                ],
                "steps": [
                    "Return <code>min(nums)</code>.",
                ],
                "why": [
                    "It is O(n), which misses the required O(log n).",
                ],
                "dry": [
                    "Scanning all seven values finds <strong>0</strong>.",
                ],
            },
            "Binary search against the right end": {
                "idea": [
                    "A rotated sorted array has one \"drop\", and the minimum sits right after it.",
                    "If <code>nums[mid] &gt; nums[hi]</code>, the drop lies between mid and hi, so the minimum is strictly right of mid. Otherwise mid..hi is sorted, so the minimum is at mid or to its left.",
                    "Comparing with the right end (not the left) also handles an array that was not rotated at all.",
                ],
                "steps": [
                    "<code>lo, hi = 0, n - 1</code>.",
                    "If <code>nums[mid] &gt; nums[hi]</code>, set <code>lo = mid + 1</code>; otherwise <code>hi = mid</code>.",
                    "Return <code>nums[lo]</code>.",
                ],
                "why": [
                    "The minimum always stays inside [lo, hi], and the range shrinks every step.",
                    "It is O(log n) time and O(1) space.",
                ],
                "dry": [
                    "[0, 6]: mid 3 holds 7, more than nums[6] = 2, so the drop is to the right: lo = 4.",
                    "[4, 6]: mid 5 holds 1, not more than 2, so hi = 5.",
                    "[4, 5]: mid 4 holds 0, not more than 1, so hi = 4.",
                    "nums[4] = <strong>0</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search in rotated sorted array
    "search-rotated": {
        "example": {"call": "search_rotated([4, 5, 6, 7, 0, 1, 2], 1)", "expect": "5"},
        "approaches": {
            "Linear scan": {
                "idea": [
                    "Use <code>list.index</code> if the target is present.",
                ],
                "steps": [
                    "<code>nums.index(target) if target in nums else -1</code>.",
                ],
                "why": [
                    "It is O(n) time.",
                ],
                "dry": [
                    "1 is found at index <strong>5</strong>.",
                ],
            },
            "Find the rotation point, then search one side": {
                "idea": [
                    "Split the problem into two easy searches. First find the index of the minimum (the rotation point), as in the previous problem.",
                    "Both pieces on either side of it are sorted. The target belongs to the right piece exactly when <code>nums[pivot] ≤ target ≤ nums[-1]</code>.",
                    "Binary-search only that piece.",
                ],
                "steps": [
                    "Find <code>pivot</code> with the compare-to-the-right-end search.",
                    "Choose the range <code>[pivot, n)</code> or <code>[0, pivot)</code>.",
                    "<code>bisect_left</code> in that range, and check for equality.",
                ],
                "why": [
                    "Each piece is sorted, and only one can contain the target.",
                    "It is two O(log n) searches, each easy to check.",
                ],
                "dry": [
                    "The pivot search finds index 4 (value 0).",
                    "0 ≤ 1 ≤ 2, so search the right piece [4, 7).",
                    "bisect_left over [0, 1, 2] lands on index 5, which holds 1.",
                    "The result is <strong>5</strong>.",
                ],
            },
            "One pass: decide which half is sorted": {
                "idea": [
                    "Around any mid, at least one half is sorted, and comparing <code>nums[lo]</code> with <code>nums[mid]</code> tells which.",
                    "If the left half is sorted, the target is there exactly when it lies in <code>[nums[lo], nums[mid])</code>; otherwise go right.",
                    "If the right half is sorted, use <code>(nums[mid], nums[hi]]</code> the same way.",
                ],
                "steps": [
                    "Return mid on a match.",
                    "Left sorted (<code>nums[lo] &lt;= nums[mid]</code>): go left if the target is in its range, otherwise right.",
                    "Right sorted: go right if the target is in its range, otherwise left.",
                ],
                "why": [
                    "In the sorted half, a simple range check decides; the other half takes everything else.",
                    "It is one loop, O(log n).",
                ],
                "dry": [
                    "[0, 6]: mid 3 holds 7. The left half [4..7] is sorted, and 1 is not in [4, 7), so go right: lo = 4.",
                    "[4, 6]: mid 5 holds 1, the target.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ search in rotated II (duplicates)
    "search-rotated-ii": {
        "example": {"call": "search_rotated_ii([1, 0, 1, 1, 1], 0)", "expect": "True"},
        "approaches": {
            "Linear scan": {
                "idea": [
                    "<code>target in nums</code>.",
                    "With duplicates, even the clever search can degrade to this in the worst case.",
                ],
                "steps": [
                    "Return <code>target in nums</code>.",
                ],
                "why": [
                    "It is O(n), the same as the worst case of any algorithm here.",
                ],
                "dry": [
                    "0 is at index 1, so the result is <strong>True</strong>.",
                ],
            },
            "Binary search, shrink both ends on ambiguity": {
                "idea": [
                    "This is the distinct-values search plus one case: when <code>nums[lo] == nums[mid] == nums[hi]</code>, you cannot tell which half is sorted.",
                    "Neither end can be the target, because both equal nums[mid], which was just checked. So drop both ends and try again.",
                    "Inputs like [1, 1, …, 1, 2, 1, 1] force that step repeatedly, so the worst case is O(n), and nothing can do better there.",
                ],
                "steps": [
                    "Return <code>True</code> on a match.",
                    "If all three are equal: <code>lo += 1</code>, <code>hi -= 1</code>.",
                    "Otherwise use the sorted-half rule from the distinct version.",
                ],
                "why": [
                    "Dropping the ends never discards the target.",
                    "It is O(log n) on typical inputs and O(n) at worst.",
                ],
                "dry": [
                    "[0, 4]: mid 2 holds 1 ≠ 0, and nums[0] = nums[2] = nums[4] = 1, so it is ambiguous: lo = 1, hi = 3.",
                    "[1, 3]: mid 2 holds 1. nums[1] = 0 ≤ 1, so the left half is sorted and 0 ≤ 0 &lt; 1: hi = 1.",
                    "[1, 1]: mid 1 holds 0, the target.",
                    "The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ time based key-value store
    "time-based-kv-store": {
        "example": {"setup": 'tm = TimeMap()\ntm.set("foo", "bar", 1)\ntm.set("foo", "bar2", 4)\ntm.set("foo", "bar3", 8)',
                    "call": '[tm.get("foo", 0), tm.get("foo", 5), tm.get("foo", 8), tm.get("baz", 9)]',
                    "expect": '["", "bar2", "bar3", ""]'},
        "approaches": {
            "Scan the key's history": {
                "idea": [
                    "Store each key's (timestamp, value) pairs in the order they were set.",
                    "For a query, walk the history backwards and return the first value whose timestamp is not after the query time.",
                ],
                "steps": [
                    "<code>set</code>: append <code>(timestamp, value)</code>.",
                    "<code>get</code>: scan backwards for <code>t &lt;= timestamp</code>; return \"\" if there is none.",
                ],
                "why": [
                    "The newest entry not after the query is the answer.",
                    "It is O(1) per set and O(n) per get.",
                ],
                "dry": [
                    "get(foo, 0): 8, 4 and 1 are all after 0, so <strong>\"\"</strong>.",
                    "get(foo, 5): 8 is after 5; 4 ≤ 5, so <strong>\"bar2\"</strong>.",
                    "get(foo, 8): 8 ≤ 8, so <strong>\"bar3\"</strong>.",
                    "get(baz, 9): no history, so <strong>\"\"</strong>.",
                ],
            },
            "Binary search each key's sorted timestamps": {
                "idea": [
                    "Timestamps arrive in increasing order, so each key's list of timestamps is already sorted.",
                    "A query wants the last timestamp ≤ t, which is <code>bisect_right(times, t) - 1</code>.",
                    "Keeping timestamps and values in parallel lists lets bisect work on plain integers.",
                ],
                "steps": [
                    "<code>set</code>: append to <code>times[key]</code> and <code>values[key]</code>.",
                    "<code>get</code>: <code>i = bisect_right(times[key], t) - 1</code>; return <code>values[key][i]</code> if i ≥ 0, otherwise \"\".",
                ],
                "why": [
                    "bisect_right counts the entries ≤ t, so i is the newest one.",
                    "It is O(1) per set and O(log n) per get.",
                ],
                "dry": [
                    "times[foo] = [1, 4, 8].",
                    "get(foo, 0): bisect_right gives 0, so i = -1 and the result is <strong>\"\"</strong>.",
                    "get(foo, 5): bisect_right gives 2, so i = 1 and the result is <strong>\"bar2\"</strong>. get(foo, 8): i = 2, <strong>\"bar3\"</strong>.",
                    "get(baz, 9): the list is empty, so i = -1 and the result is <strong>\"\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ split array largest sum
    "split-array-largest-sum": {
        "example": {"call": "split_array([7, 2, 5, 10, 8], 2)", "expect": "18"},
        "approaches": {
            "Try every split recursively": {
                "idea": [
                    "Decide where the first part ends, then solve the rest with one part fewer.",
                    "The cost of a choice is the larger of the first part's sum and the best result for the rest; take the smallest over all choices.",
                ],
                "steps": [
                    "<code>best(i, 1)</code> is the sum of <code>nums[i:]</code>.",
                    "Otherwise try every end j for the first part, leaving at least one element per remaining part.",
                ],
                "why": [
                    "It considers every split, so it is correct, but exponential without memoisation.",
                ],
                "dry": [
                    "First part [7]: max(7, rest 25) = 25. First part [7, 2]: max(9, 23) = 23.",
                    "First part [7, 2, 5]: max(14, 18) = 18. First part [7, 2, 5, 10]: max(24, 8) = 24.",
                    "The minimum is <strong>18</strong>: [7, 2, 5] and [10, 8].",
                ],
            },
            "DP over (start, parts left)": {
                "idea": [
                    "The recursion's answer depends only on (start index, parts left), so memoise it.",
                    "Prefix sums make each part's sum O(1).",
                ],
                "steps": [
                    "<code>P</code> = prefix sums.",
                    "<code>best(i, parts) = min over j of max(P[j+1] - P[i], best(j + 1, parts - 1))</code>.",
                ],
                "why": [
                    "There are k·n states with O(n) choices each: O(k·n²) time, O(k·n) memo.",
                ],
                "dry": [
                    "P = [0, 7, 9, 14, 24, 32].",
                    "best(0, 2) tries j = 0..3: max(7, 25), max(9, 23), max(14, 18), max(24, 8).",
                    "The minimum is <strong>18</strong>.",
                ],
            },
            "Binary search on the largest sum": {
                "idea": [
                    "Flip the question: for a cap S, can the array be split into at most k parts, each with sum ≤ S?",
                    "Greedily cutting a new part only when the next element would overflow S uses the fewest parts, so the check is easy.",
                    "A larger S never needs more parts, so binary-search the smallest feasible S in [max(nums), sum(nums)].",
                ],
                "steps": [
                    "<code>parts_needed(cap)</code>: greedy cuts.",
                    "If <code>parts_needed(mid) &lt;= k</code>, then <code>hi = mid</code>; otherwise <code>lo = mid + 1</code>.",
                ],
                "why": [
                    "Using fewer than k parts is fine, because a part can always be split further without raising the max.",
                    "It is O(n log(sum)) time and O(1) space.",
                ],
                "dry": [
                    "[10, 32]: cap 21 gives [7, 2, 5], [10, 8], 2 parts, so hi = 21.",
                    "[10, 21]: cap 15 gives [7, 2, 5], [10], [8], 3 parts, so lo = 16.",
                    "[16, 21]: cap 18 gives [7, 2, 5], [10, 8], 2 parts, so hi = 18.",
                    "[16, 18]: cap 17 needs 3 parts, so lo = 18. The result is <strong>18</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ median of two sorted arrays
    "median-two-sorted-arrays": {
        "example": {"call": "find_median_sorted_arrays([1, 3, 8, 9], [2, 5, 7])", "expect": "5"},
        "approaches": {
            "Merge fully, pick the middle": {
                "idea": [
                    "Merge the two sorted arrays (the merge step of merge sort) and read the middle value, or the average of the middle two.",
                ],
                "steps": [
                    "Two-pointer merge into <code>merged</code>.",
                    "An odd length gives <code>merged[n // 2]</code>; an even length averages the two middle values.",
                ],
                "why": [
                    "It is simple and correct, but O(m + n) time and space, missing the required logarithmic bound.",
                ],
                "dry": [
                    "Merged: [1, 2, 3, 5, 7, 8, 9].",
                    "The length 7 is odd, so take index 3: <strong>5</strong>.",
                ],
            },
            "Walk to the middle without storing": {
                "idea": [
                    "Run the same merge, but only count steps, remembering the last two values seen.",
                    "Stop after <code>(m + n) // 2 + 1</code> steps; the median is the last value, or the average of the last two.",
                ],
                "steps": [
                    "At each step, take the smaller front value; keep <code>prev</code> and <code>cur</code>.",
                    "Return <code>cur</code>, or <code>(prev + cur) / 2</code> for an even total.",
                ],
                "why": [
                    "It is the same order as the merge without storing it: O(m + n) time and O(1) space.",
                ],
                "dry": [
                    "Four steps are needed (7 // 2 + 1).",
                    "The values taken are 1, 2, 3, 5.",
                    "The total is odd, so the result is cur = <strong>5</strong>.",
                ],
            },
            "Binary search the partition of the shorter array": {
                "idea": [
                    "The median splits all the numbers into a left half and a right half where everything on the left is ≤ everything on the right.",
                    "Take i elements from the shorter array A and <code>j = half - i</code> from B for the left half. The split is right when <code>A[i-1] ≤ B[j]</code> and <code>B[j-1] ≤ A[i]</code>.",
                    "If <code>A[i-1] &gt; B[j]</code>, too many came from A, so move i left; otherwise move it right. Positions past the ends count as ±∞.",
                ],
                "steps": [
                    "Make A the shorter array; <code>half = (m + n + 1) // 2</code>.",
                    "Binary-search i in [0, m], computing j and the four boundary values.",
                    "Once the split is right: an odd total gives <code>max(left side)</code>; an even total averages that with <code>min(right side)</code>.",
                ],
                "why": [
                    "The split conditions are exactly what makes the left half the smallest <code>half</code> elements.",
                    "It is O(log min(m, n)) time and O(1) space.",
                ],
                "dry": [
                    "A = [2, 5, 7] (shorter), B = [1, 3, 8, 9], half = 4.",
                    "i = 1, j = 3: the left side is A[0] = 2 and B[0..2] = 1, 3, 8. B[2] = 8 &gt; A[1] = 5, so too few came from A: lo = 2.",
                    "i = 2, j = 2: the left side is 2, 5 | 1, 3. Check: 5 ≤ B[2] = 8 and 3 ≤ A[2] = 7, so the split is right.",
                    "The total is odd, so the median is max(5, 3) = <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find in mountain array
    "find-in-mountain-array": {
        "example": {"setup": ("class MountainArray:\n"
                              "    def __init__(self, arr):\n"
                              "        self.arr = arr\n"
                              "    def get(self, i):\n"
                              "        return self.arr[i]\n"
                              "    def length(self):\n"
                              "        return len(self.arr)"),
                    "call": "find_in_mountain_array(3, MountainArray([1, 2, 3, 4, 5, 3, 1]))", "expect": "2"},
        "approaches": {
            "Scan every index": {
                "idea": [
                    "Call <code>get</code> on each index in order and return the first index holding the target.",
                ],
                "steps": [
                    "For i in range(length), return i when <code>get(i) == target</code>.",
                ],
                "why": [
                    "Scanning from the left gives the minimum index, but it can take 10<sup>4</sup> calls against a limit of 100.",
                ],
                "dry": [
                    "get(0) = 1, get(1) = 2, get(2) = 3, a match.",
                    "The result is <strong>2</strong>. The other 3 at index 5 is never reached.",
                ],
            },
            "Peak search, then two binary searches": {
                "idea": [
                    "A mountain rises to a peak and then falls, and each side on its own is sorted.",
                    "Find the peak by comparing <code>get(mid)</code> with <code>get(mid + 1)</code>: rising means the peak is further right.",
                    "Binary-search the rising side first, so the smallest index wins; only if the target is not there, search the falling side with the comparison reversed.",
                ],
                "steps": [
                    "Peak: <code>lo = mid + 1</code> if rising, otherwise <code>hi = mid</code>.",
                    "Ascending search on [0, peak].",
                    "If that misses, a descending search on [peak + 1, n - 1].",
                ],
                "why": [
                    "Each part is monotonic, so binary search applies.",
                    "It makes about 3·log<sub>2</sub>(n) calls, around 42 for 10<sup>4</sup> elements, within the limit of 100.",
                ],
                "dry": [
                    "Peak: [0, 6], mid 3: 4 &lt; 5, rising, so lo = 4. Mid 5: 3 &lt; 1 is false, so hi = 5. Mid 4: 5 &lt; 3 is false, so hi = 4. The peak is at index 4.",
                    "Ascending search on [0, 4]: mid 2 holds 3, the target.",
                    "The result is <strong>2</strong>, the smaller of the two indices holding 3.",
                ],
            },
        },
    },
}
