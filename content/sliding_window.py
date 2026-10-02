# -*- coding: utf-8 -*-
"""Sliding Window topic (NeetCode 250: Sliding Window). Same build contract
as content/dsa.py."""

PRELUDE_SW = '''import bisect
import heapq
import itertools
import random
from collections import Counter, defaultdict, deque
'''


SLIDING_WINDOW_TOPIC = dict(
    id="sliding-window",
    title="Sliding Window",
    prelude=PRELUDE_SW,
    sections=[

dict(
    id="sliding-window",
    title="Fixed and variable windows",
    idea=[
        "A window is a contiguous range <code>[left, right]</code> that you slide instead of rebuilding. Extend on the right, shrink on the left while the window is invalid, and keep just enough state (a count, a map, a deque) to update in O(1) per step. Every index enters and leaves the window once, so the whole scan is O(n).",
    ],
    problems=[

    # ------------------------------------------------------------------ 219
    dict(
        id="contains-duplicate-ii",
        lc=219, slug="contains-duplicate-ii",
        name="Contains Duplicate II",
        difficulty="easy",
        framing=[
            "Are there two equal values at most <code>k</code> positions apart? It is Contains Duplicate restricted to a window of size k + 1, which is the smallest possible sliding-window problem.",
        ],
        approaches=[
            dict(
                name="Check the next k elements from each index",
                time="O(n &middot; k)",
                space="O(1)",
                tag="brute force",
                why=[
                    "For each i, compare with <code>nums[i+1 .. i+k]</code>. Every window of size k is re-read from scratch, so the overlap between consecutive windows is wasted.",
                ],
                code='''def contains_nearby_duplicate(nums, k):
    for i in range(len(nums)):
        for j in range(i + 1, min(len(nums), i + k + 1)):
            if nums[i] == nums[j]:
                return True
    return False''',
            ),
            dict(
                name="Last index seen for each value",
                time="O(n)",
                space="O(n)",
                why=[
                    "Remember the most recent index of every value. When a value repeats, only its most recent previous occurrence can be the closest, so one comparison per element suffices.",
                    "Stores up to n values &mdash; one per distinct value ever seen, even long after they have left any useful window.",
                ],
                code='''def contains_nearby_duplicate(nums, k):
    last = {}
    for i, x in enumerate(nums):
        if x in last and i - last[x] <= k:
            return True
        last[x] = i
    return False''',
            ),
            dict(
                name="Set of the last k values",
                time="O(n)",
                space="O(min(n, k))",
                best=True,
                why=[
                    "Keep a set holding exactly the previous k values. Before adding <code>nums[i]</code>, check it against the set; after adding, evict <code>nums[i - k]</code> once the window is too big.",
                    "Same O(n) time as the map but memory bounded by k, which matters when k is small and n huge. The add-then-evict rhythm is the fixed-size window template.",
                ],
                code='''def contains_nearby_duplicate(nums, k):
    window = set()
    for i, x in enumerate(nums):
        if x in window:
            return True
        window.add(x)
        if len(window) > k:
            window.remove(nums[i - k])       # slide: drop the oldest
    return False''',
            ),
        ],
        tests='''assert contains_nearby_duplicate([1, 2, 3, 1], 3) is True
assert contains_nearby_duplicate([1, 0, 1, 1], 1) is True
assert contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2) is False
assert contains_nearby_duplicate([1, 2], 0) is False
rng = random.Random(0)
for _ in range(60):
    nums = [rng.randint(0, 6) for _ in range(rng.randint(1, 12))]
    k = rng.randint(0, 5)
    brute = any(nums[i] == nums[j] for i in range(len(nums)) for j in range(i + 1, len(nums)) if j - i <= k)
    assert contains_nearby_duplicate(nums, k) is brute''',
    ),

    # ------------------------------------------------------------------ 121
    dict(
        id="best-time-stock",
        lc=121, slug="best-time-to-buy-and-sell-stock",
        name="Best Time to Buy And Sell Stock",
        difficulty="easy",
        framing=[
            "One buy followed by one later sell; maximise profit, or return 0. Seen as a window, the buy day is the left edge and the sell day the right edge; the left edge only ever needs to move to a new minimum.",
        ],
        approaches=[
            dict(
                name="Every buy/sell pair",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=["Try every buy day with every later sell day."],
                code='''def max_profit(prices):
    best = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            best = max(best, prices[j] - prices[i])
    return best''',
            ),
            dict(
                name="Two pointers: move the buy day to any lower price",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Keep the cheapest price seen so far as the buy day. Each new price is a candidate sell day, paired with that minimum. If the new price is lower still, it becomes the buy day for everything after it &mdash; buying at a higher earlier price is never better.",
                    "One pass, two variables.",
                ],
                code='''def max_profit(prices):
    lowest, best = prices[0], 0
    for p in prices[1:]:
        best = max(best, p - lowest)       # sell today
        lowest = min(lowest, p)            # or remember a better buy day
    return best''',
            ),
            dict(
                name="Kadane on daily changes",
                time="O(n)",
                space="O(1)",
                tag="another view",
                why=[
                    "Profit from day a to day b is the sum of the daily changes between them, so the answer is the maximum-sum subarray of the difference array, floored at 0. Kadane's algorithm finds it in one pass. Recognising that equivalence is worth more than the code.",
                ],
                code='''def max_profit(prices):
    best = cur = 0
    for a, b in zip(prices, prices[1:]):
        cur = max(0, cur + b - a)          # extend the run of changes, or restart
        best = max(best, cur)
    return best''',
            ),
        ],
        tests='''assert max_profit([7, 1, 5, 3, 6, 4]) == 5
assert max_profit([7, 6, 4, 3, 1]) == 0
assert max_profit([2, 4, 1]) == 2
rng = random.Random(1)
for _ in range(50):
    p = [rng.randint(0, 30) for _ in range(rng.randint(1, 15))]
    assert max_profit(p) == max([0] + [p[j] - p[i] for i in range(len(p)) for j in range(i + 1, len(p))])''',
    ),

    # ------------------------------------------------------------------ 3
    dict(
        id="longest-substring-no-repeat",
        lc=3, slug="longest-substring-without-repeating-characters",
        name="Longest Substring Without Repeating Characters",
        difficulty="medium",
        framing=[
            "The length of the longest substring with all-distinct characters. The canonical <strong>variable-size</strong> window: grow the right edge, and whenever a repeat appears, move the left edge just past the earlier copy.",
        ],
        approaches=[
            dict(
                name="Check every substring",
                time="O(n&sup3;)",
                space="O(min(n, &Sigma;))",
                tag="brute force",
                why=[
                    "Test all O(n&sup2;) substrings for distinctness with a set, each in O(n).",
                ],
                code='''def length_of_longest_substring(s):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) == j - i + 1:
                best = max(best, j - i + 1)
    return best''',
            ),
            dict(
                name="Extend from each start until a repeat",
                time="O(n &middot; &Sigma;)",
                space="O(&Sigma;)",
                why=[
                    "From each start, extend with a set until a repeat appears. A substring without repeats has at most &Sigma; characters (the alphabet size), so each start costs at most O(&Sigma;). Better, but consecutive starts redo nearly the same work.",
                ],
                code='''def length_of_longest_substring(s):
    best = 0
    for i in range(len(s)):
        seen = set()
        for ch in s[i:]:
            if ch in seen:
                break
            seen.add(ch)
        best = max(best, len(seen))
    return best''',
            ),
            dict(
                name="Window with a set, shrink one step at a time",
                time="O(n)",
                space="O(&Sigma;)",
                why=[
                    "Keep the window's characters in a set. When <code>s[right]</code> is already inside, remove characters from the left until it is not, then add it. Each character is added once and removed at most once: at most 2n set operations.",
                ],
                code='''def length_of_longest_substring(s):
    window, left, best = set(), 0, 0
    for right, ch in enumerate(s):
        while ch in window:
            window.remove(s[left])
            left += 1
        window.add(ch)
        best = max(best, right - left + 1)
    return best''',
            ),
            dict(
                name="Window with last-seen indices, jump the left edge",
                time="O(n)",
                space="O(&Sigma;)",
                best=True,
                why=[
                    "Store the last index of each character. On a repeat, jump <code>left</code> directly to one past the previous occurrence &mdash; but never backwards, because that occurrence may already be outside the window (<code>max</code> handles it).",
                    "Exactly one step per character, no inner loop.",
                ],
                code='''def length_of_longest_substring(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last:
            left = max(left, last[ch] + 1)   # never move left backwards
        last[ch] = right
        best = max(best, right - left + 1)
    return best''',
            ),
        ],
        tests='''assert length_of_longest_substring("abcabcbb") == 3
assert length_of_longest_substring("bbbbb") == 1
assert length_of_longest_substring("pwwkew") == 3
assert length_of_longest_substring("") == 0
assert length_of_longest_substring("abba") == 2
rng = random.Random(2)
for _ in range(60):
    s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 12)))
    brute = max([0] + [j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1) if len(set(s[i:j])) == j - i])
    assert length_of_longest_substring(s) == brute''',
    ),

    # ------------------------------------------------------------------ 424
    dict(
        id="longest-repeating-replacement",
        lc=424, slug="longest-repeating-character-replacement",
        name="Longest Repeating Character Replacement",
        difficulty="medium",
        framing=[
            "You may replace at most <code>k</code> characters. What is the longest substring you can turn into a single repeated letter? A window is fixable exactly when <code>length - (count of its most frequent letter) &le; k</code>: everything that is not the majority letter gets replaced.",
        ],
        approaches=[
            dict(
                name="Every substring",
                time="O(n&sup2;)",
                space="O(26)",
                tag="brute force",
                why=[
                    "From each start, extend the end while maintaining letter counts, checking the fixable condition at each length. O(n&sup2;) windows with O(1) updates each (the max of 26 counts is O(1)).",
                ],
                code='''def character_replacement(s, k):
    best = 0
    for i in range(len(s)):
        counts = [0] * 26
        for j in range(i, len(s)):
            counts[ord(s[j]) - 65] += 1
            if j - i + 1 - max(counts) <= k:
                best = max(best, j - i + 1)
    return best''',
            ),
            dict(
                name="Sliding window, recompute the max count",
                time="O(26 &middot; n)",
                space="O(26)",
                why=[
                    "Grow the window; while it is not fixable, shrink from the left. The fixable test needs the most frequent letter in the window, recomputed from the 26 counts each time &mdash; O(26) per step.",
                ],
                code='''def character_replacement(s, k):
    counts, left, best = [0] * 26, 0, 0
    for right, ch in enumerate(s):
        counts[ord(ch) - 65] += 1
        while right - left + 1 - max(counts) > k:
            counts[ord(s[left]) - 65] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best''',
            ),
            dict(
                name="Sliding window with a never-decreasing max count",
                time="O(n)",
                space="O(26)",
                best=True,
                why=[
                    "Keep <code>max_count</code> as the highest single-letter count seen in <em>any</em> window, and never decrease it when shrinking. It can go stale, making the window look better than it is &mdash; but the window then only slides (right and left each advance by one), never grows. The answer only grows when a window with a genuinely higher letter count appears, which updates <code>max_count</code> correctly.",
                    "So the recorded best is always achievable, and a single <code>if</code> replaces the <code>while</code>: each step is O(1). A subtle argument, and a classic interview follow-up.",
                ],
                code='''def character_replacement(s, k):
    counts, left, max_count = [0] * 26, 0, 0
    for right, ch in enumerate(s):
        counts[ord(ch) - 65] += 1
        max_count = max(max_count, counts[ord(ch) - 65])
        if right - left + 1 - max_count > k:          # slide, do not shrink further
            counts[ord(s[left]) - 65] -= 1
            left += 1
    return len(s) - left''',
            ),
        ],
        tests='''assert character_replacement("ABAB", 2) == 4
assert character_replacement("AABABBA", 1) == 4
assert character_replacement("A", 0) == 1
rng = random.Random(3)
for _ in range(60):
    s = "".join(rng.choice("ABC") for _ in range(rng.randint(1, 12)))
    k = rng.randint(0, 3)
    brute = max(j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                if j - i - max(Counter(s[i:j]).values()) <= k)
    assert character_replacement(s, k) == brute''',
    ),

    # ------------------------------------------------------------------ 567
    dict(
        id="permutation-in-string",
        lc=567, slug="permutation-in-string",
        name="Permutation In String",
        difficulty="medium",
        framing=[
            "Does <code>s2</code> contain a permutation of <code>s1</code> as a substring? A permutation is an anagram, and an anagram of <code>s1</code> must have exactly its length &mdash; so this is a <strong>fixed-size</strong> window of length <code>len(s1)</code> whose letter counts must match.",
        ],
        approaches=[
            dict(
                name="Generate permutations",
                time="O(m! &middot; n)",
                space="O(m!)",
                tag="brute force",
                why=[
                    "Try every permutation of <code>s1</code> as a substring. Factorial; impractical beyond about 8 characters, but it states the problem literally.",
                ],
                code='''def check_inclusion(s1, s2):
    return any("".join(p) in s2 for p in set(itertools.permutations(s1)))''',
            ),
            dict(
                name="Sort every window",
                time="O(n &middot; m log m)",
                space="O(m)",
                why=[
                    "Compare the sorted form of each length-m window with sorted <code>s1</code>. The anagram test from Valid Anagram applied n times, without reusing anything between neighbouring windows.",
                ],
                code='''def check_inclusion(s1, s2):
    target, m = sorted(s1), len(s1)
    return any(sorted(s2[i:i + m]) == target for i in range(len(s2) - m + 1))''',
            ),
            dict(
                name="Fixed window, compare 26 counts",
                time="O(26 &middot; n)",
                space="O(26)",
                why=[
                    "Slide the window one character at a time: add the incoming letter's count, subtract the outgoing one. Comparing the two 26-entry arrays is O(26) per step.",
                ],
                code='''def check_inclusion(s1, s2):
    m = len(s1)
    if m > len(s2):
        return False
    need, have = [0] * 26, [0] * 26
    for a, b in zip(s1, s2):
        need[ord(a) - 97] += 1
        have[ord(b) - 97] += 1
    if need == have:
        return True
    for i in range(m, len(s2)):
        have[ord(s2[i]) - 97] += 1
        have[ord(s2[i - m]) - 97] -= 1
        if need == have:
            return True
    return False''',
            ),
            dict(
                name="Fixed window with a matches counter",
                time="O(n)",
                space="O(26)",
                best=True,
                why=[
                    "Track how many of the 26 letters currently have equal counts in the window and in <code>s1</code>. Changing one letter's count can only change its own match status, so the counter updates in O(1). The window is a permutation exactly when all 26 match.",
                    "This removes the O(26) comparison per step &mdash; the pattern used again in Minimum Window Substring.",
                ],
                code='''def check_inclusion(s1, s2):
    m = len(s1)
    if m > len(s2):
        return False
    need, have = [0] * 26, [0] * 26
    for a, b in zip(s1, s2):
        need[ord(a) - 97] += 1
        have[ord(b) - 97] += 1
    matches = sum(need[i] == have[i] for i in range(26))

    def change(idx, delta):
        nonlocal matches
        matches -= need[idx] == have[idx]
        have[idx] += delta
        matches += need[idx] == have[idx]

    for i in range(m, len(s2)):
        if matches == 26:
            return True
        change(ord(s2[i]) - 97, +1)
        change(ord(s2[i - m]) - 97, -1)
    return matches == 26''',
            ),
        ],
        tests='''assert check_inclusion("ab", "eidbaooo") is True
assert check_inclusion("ab", "eidboaoo") is False
assert check_inclusion("abc", "ab") is False
assert check_inclusion("a", "a") is True
rng = random.Random(4)
for _ in range(60):
    s1 = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
    s2 = "".join(rng.choice("abc") for _ in range(rng.randint(1, 10)))
    brute = any(sorted(s2[i:i + len(s1)]) == sorted(s1) for i in range(len(s2) - len(s1) + 1))
    assert check_inclusion(s1, s2) is brute''',
    ),

    # ------------------------------------------------------------------ 209
    dict(
        id="minimum-size-subarray-sum",
        lc=209, slug="minimum-size-subarray-sum",
        name="Minimum Size Subarray Sum",
        difficulty="medium",
        framing=[
            "The shortest contiguous subarray with sum at least <code>target</code>, where every number is <strong>positive</strong>. Positivity is what makes the window valid: extending always increases the sum and shrinking always decreases it. The follow-up asks for an O(n log n) solution too, which is the prefix-sum-plus-binary-search one.",
        ],
        approaches=[
            dict(
                name="Every start, extend until the target",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=["From each start, add elements until the sum reaches the target."],
                code='''def min_subarray_len(target, nums):
    best = float("inf")
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if total >= target:
                best = min(best, j - i + 1)
                break
    return 0 if best == float("inf") else best''',
            ),
            dict(
                name="Prefix sums and binary search",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Prefix sums of positive numbers are strictly increasing, so for each start i the first end whose prefix reaches <code>P[i] + target</code> can be binary-searched. This is the follow-up's answer, and the only one of these approaches that would survive if the problem asked for <em>many</em> targets.",
                ],
                code='''def min_subarray_len(target, nums):
    P = [0]
    for x in nums:
        P.append(P[-1] + x)
    best = float("inf")
    for i in range(len(nums)):
        j = bisect.bisect_left(P, P[i] + target)
        if j <= len(nums):
            best = min(best, j - i)
    return 0 if best == float("inf") else best''',
            ),
            dict(
                name="Variable window",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Extend right, adding to the sum. While the sum is at least the target, record the length and shrink from the left. Because every value is positive, shrinking is the only way to find a shorter valid window ending here, and no shorter window starting before <code>left</code> can exist later.",
                    "Each index enters and leaves once: O(n). With negative numbers this breaks, and the tool becomes a monotonic deque over prefix sums (LeetCode 862).",
                ],
                code='''def min_subarray_len(target, nums):
    left = total = 0
    best = float("inf")
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == float("inf") else best''',
            ),
        ],
        tests='''assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2
assert min_subarray_len(4, [1, 4, 4]) == 1
assert min_subarray_len(11, [1, 1, 1, 1, 1, 1, 1, 1]) == 0
rng = random.Random(5)
for _ in range(60):
    nums = [rng.randint(1, 6) for _ in range(rng.randint(1, 12))]
    t = rng.randint(1, 25)
    lens = [j - i for i in range(len(nums)) for j in range(i + 1, len(nums) + 1) if sum(nums[i:j]) >= t]
    assert min_subarray_len(t, nums) == (min(lens) if lens else 0)''',
    ),

    # ------------------------------------------------------------------ 658
    dict(
        id="find-k-closest-elements",
        lc=658, slug="find-k-closest-elements",
        name="Find K Closest Elements",
        difficulty="medium",
        framing=[
            "Return the k values closest to <code>x</code> from a sorted array, in ascending order; ties go to the smaller value. The answer is always a contiguous block of length k, so the real question is where that block starts &mdash; and that can be binary-searched.",
        ],
        approaches=[
            dict(
                name="Sort by distance",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Sort by <code>(|a - x|, a)</code>, take k, sort them back. Ignores that the input is sorted.",
                ],
                code='''def find_closest_elements(arr, k, x):
    return sorted(sorted(arr, key=lambda a: (abs(a - x), a))[:k])''',
            ),
            dict(
                name="Shrink a window from both ends",
                time="O(n - k)",
                space="O(1)",
                why=[
                    "Start with the whole array and repeatedly drop whichever end is farther from x (the right end on a tie) until k elements remain. Each step removes one element that cannot be in the answer.",
                ],
                code='''def find_closest_elements(arr, k, x):
    lo, hi = 0, len(arr) - 1
    while hi - lo + 1 > k:
        if x - arr[lo] <= arr[hi] - x:
            hi -= 1
        else:
            lo += 1
    return arr[lo:hi + 1]''',
            ),
            dict(
                name="Binary search the window's left edge",
                time="O(log(n - k) + k)",
                space="O(1)",
                best=True,
                why=[
                    "Candidate starts are <code>0 .. n - k</code>. For a start <code>mid</code>, compare the element just leaving the window on the left, <code>arr[mid]</code>, with the one just beyond it on the right, <code>arr[mid + k]</code>. If x is farther from <code>arr[mid]</code>, the window should move right; otherwise it should not. That comparison is monotonic in <code>mid</code>, so binary search finds the start.",
                    "Compare the signed differences <code>x - arr[mid]</code> and <code>arr[mid + k] - x</code>, not absolute values: that handles duplicates and x outside the array correctly.",
                ],
                code='''def find_closest_elements(arr, k, x):
    lo, hi = 0, len(arr) - k
    while lo < hi:
        mid = (lo + hi) // 2
        if x - arr[mid] > arr[mid + k] - x:
            lo = mid + 1                      # the window should start further right
        else:
            hi = mid
    return arr[lo:lo + k]''',
            ),
        ],
        tests='''assert find_closest_elements([1, 2, 3, 4, 5], 4, 3) == [1, 2, 3, 4]
assert find_closest_elements([1, 1, 2, 3, 4, 5], 4, -1) == [1, 1, 2, 3]
assert find_closest_elements([1, 1, 1, 10, 10, 10], 1, 9) == [10]
rng = random.Random(6)
for _ in range(60):
    arr = sorted(rng.randint(-5, 10) for _ in range(rng.randint(1, 10)))
    k, x = rng.randint(1, len(arr)), rng.randint(-8, 13)
    assert find_closest_elements(arr, k, x) == sorted(sorted(arr, key=lambda a: (abs(a - x), a))[:k])''',
    ),

    # ------------------------------------------------------------------ 76
    dict(
        id="minimum-window-substring",
        lc=76, slug="minimum-window-substring",
        name="Minimum Window Substring",
        difficulty="hard",
        framing=[
            "The shortest substring of <code>s</code> containing every character of <code>t</code>, counting multiplicity. The hardest standard window problem: expand until the window is valid, then shrink while it stays valid, recording the best.",
            "The validity test is the whole trick. Comparing count maps at every step costs O(&Sigma;); tracking how many required characters are already satisfied makes it O(1).",
        ],
        approaches=[
            dict(
                name="Check every substring",
                time="O(n&sup2; &middot; &Sigma;)",
                space="O(&Sigma;)",
                tag="brute force",
                why=[
                    "From each start, extend while counting; the first end at which the window covers <code>t</code> gives the shortest window from that start. Covering is checked by comparing counts, O(&Sigma;).",
                ],
                code='''def min_window(s, t):
    need, best = Counter(t), ""
    for i in range(len(s)):
        have = Counter()
        for j in range(i, len(s)):
            have[s[j]] += 1
            if all(have[c] >= n for c, n in need.items()):
                if not best or j - i + 1 < len(best):
                    best = s[i:j + 1]
                break
    return best''',
            ),
            dict(
                name="Sliding window with a 'formed' counter",
                time="O(n + m)",
                space="O(&Sigma;)",
                best=True,
                why=[
                    "<code>need</code> holds the required count per character; <code>formed</code> counts how many distinct required characters currently meet their count. Adding a character can only complete its own requirement, and removing one can only break its own, so <code>formed</code> updates in O(1).",
                    "Expand right. Whenever <code>formed</code> equals the number of distinct characters in <code>t</code>, the window is valid: record it, then shrink from the left until it stops being valid. Each index is added once and removed once: O(n + m).",
                ],
                code='''def min_window(s, t):
    need = Counter(t)
    have = defaultdict(int)
    required, formed = len(need), 0
    best, left = (float("inf"), 0, 0), 0
    for right, ch in enumerate(s):
        have[ch] += 1
        if have[ch] == need[ch]:
            formed += 1
        while formed == required:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right + 1)
            out = s[left]
            have[out] -= 1
            if have[out] < need[out]:
                formed -= 1
            left += 1
    return "" if best[0] == float("inf") else s[best[1]:best[2]]''',
            ),
        ],
        tests='''assert min_window("ADOBECODEBANC", "ABC") == "BANC"
assert min_window("a", "a") == "a"
assert min_window("a", "aa") == ""
assert min_window("aa", "aa") == "aa"
rng = random.Random(7)
for _ in range(60):
    s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 10)))
    t = "".join(rng.choice("abc") for _ in range(rng.randint(1, 3)))
    got, need = min_window(s, t), Counter(t)
    cands = [s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)
             if all(Counter(s[i:j])[c] >= n for c, n in need.items())]
    if cands:
        assert len(got) == min(map(len, cands)) and all(Counter(got)[c] >= n for c, n in need.items())
    else:
        assert got == ""''',
    ),

    # ------------------------------------------------------------------ 239
    dict(
        id="sliding-window-maximum",
        lc=239, slug="sliding-window-maximum",
        name="Sliding Window Maximum",
        difficulty="hard",
        framing=[
            "Return the maximum of every window of size k. A running max cannot simply be decremented when an element leaves, so the question is which data structure supports \"add, remove the oldest, query the max\" cheaply. A <strong>monotonic deque</strong> does all three in amortised O(1).",
        ],
        approaches=[
            dict(
                name="Max of every window",
                time="O(n &middot; k)",
                space="O(1) beyond output",
                tag="brute force",
                why=["Call <code>max</code> on each of the n - k + 1 windows."],
                code='''def max_sliding_window(nums, k):
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]''',
            ),
            dict(
                name="Max-heap with lazy deletion",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Push <code>(-value, index)</code>. Before reading the top, pop entries whose index has fallen out of the window. Stale entries are removed only when they reach the top, which is fine: the top is all we ever read.",
                ],
                code='''def max_sliding_window(nums, k):
    heap, out = [], []
    for i, x in enumerate(nums):
        heapq.heappush(heap, (-x, i))
        if i >= k - 1:
            while heap[0][1] <= i - k:
                heapq.heappop(heap)           # expired: left the window
            out.append(-heap[0][0])
    return out''',
            ),
            dict(
                name="Block prefix and suffix maxima",
                time="O(n)",
                space="O(n)",
                tag="no deque",
                why=[
                    "Split the array into blocks of size k. Any window spans at most two blocks: the tail of one and the head of the next. So precompute, within each block, the max from the block start to each index and from each index to the block end. A window's max is <code>max(suffix[i], prefix[i + k - 1])</code>. Three linear passes, no data structure beyond arrays.",
                ],
                code='''def max_sliding_window(nums, k):
    n = len(nums)
    prefix, suffix = nums[:], nums[:]
    for i in range(1, n):
        if i % k:
            prefix[i] = max(prefix[i - 1], nums[i])
    for i in range(n - 2, -1, -1):
        if (i + 1) % k:
            suffix[i] = max(suffix[i + 1], nums[i])
    return [max(suffix[i], prefix[i + k - 1]) for i in range(n - k + 1)]''',
            ),
            dict(
                name="Monotonic deque of indices",
                time="O(n)",
                space="O(k)",
                best=True,
                why=[
                    "Keep indices whose values are strictly decreasing from front to back. A new value pops every smaller value from the back first: those can never be a maximum again, because the new value is both larger and will stay in the window longer. The front is then the current maximum; pop it when its index leaves the window.",
                    "Each index is pushed once and popped at most once: O(n) total, and the deque never holds more than k indices.",
                ],
                code='''def max_sliding_window(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()                          # dominated: can never be a max
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                      # left the window
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out''',
            ),
        ],
        tests='''assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
assert max_sliding_window([1], 1) == [1]
assert max_sliding_window([9, 8, 7], 3) == [9]
rng = random.Random(8)
for _ in range(60):
    nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 15))]
    k = rng.randint(1, len(nums))
    assert max_sliding_window(nums, k) == [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]''',
    ),
    ],
),
    ],
)
