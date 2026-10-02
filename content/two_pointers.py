# -*- coding: utf-8 -*-
"""Two Pointers and Intervals topic (NeetCode 250: Two Pointers, Intervals).

Fills the planned "sorting" topic: both families are "sort first, then a
linear sweep becomes correct". Same build contract as content/dsa.py.
"""

PRELUDE_TP = '''import bisect
import heapq
import itertools
import random
from collections import Counter
'''


TWO_POINTERS_TOPIC = dict(
    id="sorting",
    title="Two Pointers and Intervals",
    prelude=PRELUDE_TP,
    sections=[

dict(
    id="two-pointers",
    title="Two pointers",
    idea=[
        "Two indices that move toward each other (or in the same direction at different speeds) replace a nested loop whenever each step can safely discard one candidate for good. On sorted data that is almost always the case.",
    ],
    problems=[

    # ------------------------------------------------------------------ 344
    dict(
        id="reverse-string",
        lc=344, slug="reverse-string",
        name="Reverse String",
        difficulty="easy",
        framing=[
            "Reverse a list of characters <strong>in place</strong> with O(1) extra memory. The simplest two-pointer problem: swap the ends and move inward.",
        ],
        approaches=[
            dict(
                name="Push onto a stack, pop back",
                time="O(n)",
                space="O(n)",
                why=[
                    "A stack reverses order by nature: push every character, then pop them back into the list. Correct, but the stack is a full copy of the input, which the problem forbids.",
                ],
                code='''def reverse_string(s):
    stack = list(s)
    for i in range(len(s)):
        s[i] = stack.pop()''',
            ),
            dict(
                name="Recursive swap of the ends",
                time="O(n)",
                space="O(n)",
                why=[
                    "Swap <code>s[lo]</code> and <code>s[hi]</code>, recurse on the inside. No copy of the data, but n/2 stack frames &mdash; hidden O(n) space, and CPython's 1000-frame limit breaks it for large inputs.",
                ],
                code='''def reverse_string(s):
    def go(lo, hi):
        if lo < hi:
            s[lo], s[hi] = s[hi], s[lo]
            go(lo + 1, hi - 1)
    go(0, len(s) - 1)''',
            ),
            dict(
                name="Two pointers, swap inward",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "The same swaps as the recursion, as a loop: two indices, n/2 swaps, nothing else stored. <code>s.reverse()</code> or <code>s[:] = s[::-1]</code> do the same in C; the second one builds a temporary copy.",
                ],
                code='''def reverse_string(s):
    lo, hi = 0, len(s) - 1
    while lo < hi:
        s[lo], s[hi] = s[hi], s[lo]
        lo, hi = lo + 1, hi - 1''',
            ),
        ],
        tests='''for word in ("hello", "Hannah", "a", "ab"):
    s = list(word)
    reverse_string(s)
    assert s == list(word[::-1])''',
    ),

    # ------------------------------------------------------------------ 125
    dict(
        id="valid-palindrome",
        lc=125, slug="valid-palindrome",
        name="Valid Palindrome",
        difficulty="easy",
        framing=[
            "Is the string a palindrome once you lower-case it and ignore everything that is not a letter or a digit? The cleaning step is where the extra memory hides.",
        ],
        approaches=[
            dict(
                name="Clean, then compare with the reverse",
                time="O(n)",
                space="O(n)",
                why=[
                    "Build the filtered, lower-cased string and compare it with its reverse. Two copies of up to n characters. Clear and perfectly acceptable unless O(1) space is asked for.",
                ],
                code='''def is_palindrome(s):
    clean = [ch.lower() for ch in s if ch.isalnum()]
    return clean == clean[::-1]''',
            ),
            dict(
                name="Two pointers skipping non-alphanumerics",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Move <code>lo</code> forward and <code>hi</code> backward past anything that is not alphanumeric, then compare the two characters case-insensitively. No filtered copy is ever built, and the first mismatch ends the scan.",
                ],
                code='''def is_palindrome(s):
    lo, hi = 0, len(s) - 1
    while lo < hi:
        if not s[lo].isalnum():
            lo += 1
        elif not s[hi].isalnum():
            hi -= 1
        elif s[lo].lower() != s[hi].lower():
            return False
        else:
            lo, hi = lo + 1, hi - 1
    return True''',
            ),
        ],
        tests='''assert is_palindrome("A man, a plan, a canal: Panama") is True
assert is_palindrome("race a car") is False
assert is_palindrome(" ") is True
assert is_palindrome("0P") is False
assert is_palindrome(".,") is True''',
    ),

    # ------------------------------------------------------------------ 680
    dict(
        id="valid-palindrome-ii",
        lc=680, slug="valid-palindrome-ii",
        name="Valid Palindrome II",
        difficulty="easy",
        framing=[
            "Can the string become a palindrome by deleting <em>at most one</em> character? Two pointers find the first mismatch; at that point one of the two mismatched characters must be the one deleted.",
        ],
        approaches=[
            dict(
                name="Try deleting each character",
                time="O(n&sup2;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Check the original, then every string with one character removed. n + 1 palindrome checks of O(n) each, plus a copy per check.",
                ],
                code='''def valid_palindrome(s):
    if s == s[::-1]:
        return True
    for i in range(len(s)):
        t = s[:i] + s[i + 1:]
        if t == t[::-1]:
            return True
    return False''',
            ),
            dict(
                name="Two pointers, branch once at the first mismatch",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Walk inward while the ends match. At the first mismatch <code>s[lo] != s[hi]</code>, everything outside is already matched, so the only candidates for deletion are <code>s[lo]</code> and <code>s[hi]</code>. Check whether either remaining inner range is a palindrome.",
                    "Only one branch point ever happens, and each branch is one linear scan: O(n) total. Allowing k deletions would need recursion (or DP) at every mismatch.",
                ],
                code='''def valid_palindrome(s):
    def pal(lo, hi):
        while lo < hi:
            if s[lo] != s[hi]:
                return False
            lo, hi = lo + 1, hi - 1
        return True

    lo, hi = 0, len(s) - 1
    while lo < hi:
        if s[lo] != s[hi]:
            return pal(lo + 1, hi) or pal(lo, hi - 1)   # delete one side
        lo, hi = lo + 1, hi - 1
    return True''',
            ),
        ],
        tests='''assert valid_palindrome("aba") is True
assert valid_palindrome("abca") is True
assert valid_palindrome("abc") is False
assert valid_palindrome("eeccccbebaeeabebccceea") is False
rng = random.Random(0)
for _ in range(60):
    s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 8)))
    brute = s == s[::-1] or any((s[:i] + s[i + 1:]) == (s[:i] + s[i + 1:])[::-1] for i in range(len(s)))
    assert valid_palindrome(s) is brute''',
    ),

    # ------------------------------------------------------------------ 1768
    dict(
        id="merge-strings-alternately",
        lc=1768, slug="merge-strings-alternately",
        name="Merge Strings Alternately",
        difficulty="easy",
        framing=[
            "Interleave two strings character by character, appending whatever is left of the longer one. A warm-up for two pointers moving in the <em>same</em> direction over two different sequences, as in the merge step of merge sort.",
        ],
        approaches=[
            dict(
                name="Two indices",
                time="O(m + n)",
                space="O(m + n)",
                best=True,
                why=[
                    "Alternate while both strings have characters, then append the tail of whichever remains. Build a list and join once: repeated <code>+=</code> on strings may copy on every step.",
                ],
                code='''def merge_alternately(word1, word2):
    out, i = [], 0
    while i < len(word1) and i < len(word2):
        out += [word1[i], word2[i]]
        i += 1
    return "".join(out) + word1[i:] + word2[i:]''',
            ),
            dict(
                name="zip_longest",
                time="O(m + n)",
                space="O(m + n)",
                tag="idiomatic",
                why=[
                    "<code>itertools.zip_longest</code> pads the shorter string with empty strings, so the tail needs no special case.",
                ],
                code='''def merge_alternately(word1, word2):
    return "".join(a + b for a, b in itertools.zip_longest(word1, word2, fillvalue=""))''',
            ),
        ],
        tests='''assert merge_alternately("abc", "pqr") == "apbqcr"
assert merge_alternately("ab", "pqrs") == "apbqrs"
assert merge_alternately("abcd", "pq") == "apbqcd"''',
    ),

    # ------------------------------------------------------------------ 88
    dict(
        id="merge-sorted-array",
        lc=88, slug="merge-sorted-array",
        name="Merge Sorted Array",
        difficulty="easy",
        framing=[
            "Merge sorted <code>nums2</code> into sorted <code>nums1</code>, which has exactly enough empty slots at the end. The follow-up is O(m + n) time with no extra array, and the trick is to fill from the <strong>back</strong>, where the free space is.",
        ],
        approaches=[
            dict(
                name="Copy in and sort",
                time="O((m + n) log(m + n))",
                space="O(1)&ndash;O(m + n)",
                why=[
                    "Drop <code>nums2</code> into the empty slots and sort. Ignores that both halves are already sorted. (Timsort does notice two sorted runs and merges them in linear time &mdash; but that is a library detail, not your algorithm.)",
                ],
                code='''def merge(nums1, m, nums2, n):
    nums1[m:] = nums2
    nums1.sort()''',
            ),
            dict(
                name="Copy nums1's values, merge forward",
                time="O(m + n)",
                space="O(m)",
                why=[
                    "A standard forward merge would overwrite <code>nums1</code>'s values before reading them, so copy them aside first. Linear time, O(m) extra space.",
                ],
                code='''def merge(nums1, m, nums2, n):
    first = nums1[:m]
    i = j = k = 0
    while i < m and j < n:
        if first[i] <= nums2[j]:
            nums1[k] = first[i]; i += 1
        else:
            nums1[k] = nums2[j]; j += 1
        k += 1
    nums1[k:] = first[i:] + nums2[j:]''',
            ),
            dict(
                name="Merge backwards into the free space",
                time="O(m + n)",
                space="O(1)",
                best=True,
                why=[
                    "Compare the largest remaining elements of each array and write the bigger one at the end of <code>nums1</code>. The write position is always at or beyond the read position in <code>nums1</code>, so nothing unread is ever overwritten.",
                    "When <code>nums2</code> is exhausted, whatever is left of <code>nums1</code> is already in place; only leftover <code>nums2</code> elements need copying.",
                ],
                code='''def merge(nums1, m, nums2, n):
    i, j, k = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]; i -= 1
        else:
            nums1[k] = nums2[j]; j -= 1
        k -= 1''',
            ),
        ],
        tests='''a = [1, 2, 3, 0, 0, 0]; merge(a, 3, [2, 5, 6], 3); assert a == [1, 2, 2, 3, 5, 6]
a = [1]; merge(a, 1, [], 0); assert a == [1]
a = [0]; merge(a, 0, [1], 1); assert a == [1]
rng = random.Random(1)
for _ in range(50):
    x = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 6)))
    y = sorted(rng.randint(-9, 9) for _ in range(rng.randint(0, 6)))
    a = x + [0] * len(y)
    merge(a, len(x), y, len(y))
    assert a == sorted(x + y)''',
    ),

    # ------------------------------------------------------------------ 26
    dict(
        id="remove-duplicates-sorted",
        lc=26, slug="remove-duplicates-from-sorted-array",
        name="Remove Duplicates From Sorted Array",
        difficulty="easy",
        framing=[
            "Keep one copy of each value, in order, in the front of the array, and return how many there are. Because the array is sorted, a value is new exactly when it differs from the last value kept &mdash; which is what makes O(1) space possible.",
        ],
        approaches=[
            dict(
                name="Set, then sort back in",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Take the distinct values with a set, sort them (a set forgets order), and write them to the front. Works on unsorted input too, which is precisely the property this problem does not need.",
                ],
                code='''def remove_duplicates(nums):
    uniq = sorted(set(nums))
    nums[:len(uniq)] = uniq
    return len(uniq)''',
            ),
            dict(
                name="Write pointer",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "<code>k</code> counts the distinct values written so far; <code>nums[k - 1]</code> is the last one. Each element that differs from it is written at <code>k</code>. Sortedness guarantees an equal value can only follow its twins, so comparing with the last kept value is enough.",
                    "Generalises neatly: to allow each value at most twice (LeetCode 80), compare with <code>nums[k - 2]</code> instead.",
                ],
                code='''def remove_duplicates(nums):
    k = 1
    for x in nums[1:]:
        if x != nums[k - 1]:
            nums[k] = x
            k += 1
    return k''',
            ),
        ],
        tests='''for nums in ([1, 1, 2], [0, 0, 1, 1, 1, 2, 2, 3, 3, 4], [5], [1, 2, 3]):
    a = nums[:]
    k = remove_duplicates(a)
    assert a[:k] == sorted(set(nums))''',
    ),

    # ------------------------------------------------------------------ 167
    dict(
        id="two-sum-ii",
        lc=167, slug="two-sum-ii-input-array-is-sorted",
        name="Two Sum II - Input Array Is Sorted",
        difficulty="medium",
        framing=[
            "Two Sum on a sorted array, returning 1-based indices, using O(1) extra space. The hash map from Two Sum would work but wastes the sortedness; two pointers use it.",
        ],
        approaches=[
            dict(
                name="Every pair",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=["The baseline: try all pairs."],
                code='''def two_sum_sorted(numbers, target):
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] + numbers[j] == target:
                return [i + 1, j + 1]''',
            ),
            dict(
                name="Binary search for each complement",
                time="O(n log n)",
                space="O(1)",
                why=[
                    "For each i, binary-search the rest of the array for <code>target - numbers[i]</code>. Uses sortedness, but only half-way: each search starts from scratch.",
                ],
                code='''def two_sum_sorted(numbers, target):
    for i, x in enumerate(numbers):
        j = bisect.bisect_left(numbers, target - x, i + 1)
        if j < len(numbers) and numbers[j] == target - x:
            return [i + 1, j + 1]''',
            ),
            dict(
                name="Two pointers from both ends",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Start at the smallest and largest values. If the sum is too small, the smallest value cannot be part of any answer with anything to its right (they are all at most the current largest), so drop it. If too big, the largest cannot pair with anything, so drop it. Each step eliminates one element permanently, so at most n steps.",
                    "That elimination argument &mdash; not the code &mdash; is what an interviewer wants to hear.",
                ],
                code='''def two_sum_sorted(numbers, target):
    lo, hi = 0, len(numbers) - 1
    while lo < hi:
        total = numbers[lo] + numbers[hi]
        if total == target:
            return [lo + 1, hi + 1]
        if total < target:
            lo += 1
        else:
            hi -= 1''',
            ),
        ],
        tests='''assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]
assert two_sum_sorted([2, 3, 4], 6) == [1, 3]
assert two_sum_sorted([-1, 0], -1) == [1, 2]
rng = random.Random(2)
for _ in range(50):
    nums = sorted(rng.sample(range(-40, 40), rng.randint(2, 12)))
    i, j = sorted(rng.sample(range(len(nums)), 2))
    a, b = two_sum_sorted(nums, nums[i] + nums[j])
    assert a < b and nums[a - 1] + nums[b - 1] == nums[i] + nums[j]''',
    ),

    # ------------------------------------------------------------------ 15
    dict(
        id="three-sum",
        lc=15, slug="3sum",
        name="3Sum",
        difficulty="medium",
        framing=[
            "Return every distinct triplet summing to zero. Fix one number and the rest is Two Sum II on a sorted array. The real difficulty is avoiding duplicate triplets <em>without</em> a set of results.",
        ],
        approaches=[
            dict(
                name="Every triple, deduplicated with a set",
                time="O(n&sup3;)",
                space="O(k)",
                tag="brute force",
                why=[
                    "Check all triples; store each as a sorted tuple in a set to remove duplicates. n&sup3;/6 triples.",
                ],
                code='''def three_sum(nums):
    found = set()
    for a, b, c in itertools.combinations(nums, 3):
        if a + b + c == 0:
            found.add(tuple(sorted((a, b, c))))
    return [list(t) for t in found]''',
            ),
            dict(
                name="Fix one, hash set for the other two",
                time="O(n&sup2;)",
                space="O(n)",
                why=[
                    "For each i, run one-pass Two Sum over the later elements with a hash set, targeting <code>-nums[i]</code>. O(n&sup2;), but duplicates still need a result set, and the per-i hash set costs memory.",
                ],
                code='''def three_sum(nums):
    found = set()
    for i in range(len(nums)):
        seen = set()
        for x in nums[i + 1:]:
            if -nums[i] - x in seen:
                found.add(tuple(sorted((nums[i], x, -nums[i] - x))))
            seen.add(x)
    return [list(t) for t in found]''',
            ),
            dict(
                name="Sort, fix one, two pointers, skip duplicates",
                time="O(n&sup2;)",
                space="O(1) beyond the output",
                best=True,
                why=[
                    "Sort. For each <code>i</code>, find pairs in the suffix summing to <code>-nums[i]</code> with two pointers. Duplicates are skipped structurally: skip an <code>i</code> equal to the previous one, and after recording a triplet, move both pointers past any equal neighbours.",
                    "Break when <code>nums[i] &gt; 0</code>: everything after it is positive too, so no triplet can reach zero. O(n log n) sort plus n two-pointer scans of O(n): O(n&sup2;) total, which is believed optimal for 3Sum in general.",
                ],
                code='''def three_sum(nums):
    nums, out = sorted(nums), []
    for i in range(len(nums) - 2):
        if nums[i] > 0:
            break
        if i and nums[i] == nums[i - 1]:
            continue                            # same first number: same triplets
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if s < 0:
                lo += 1
            elif s > 0:
                hi -= 1
            else:
                out.append([nums[i], nums[lo], nums[hi]])
                lo, hi = lo + 1, hi - 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1                     # skip equal second numbers
    return out''',
            ),
        ],
        tests='''def norm(ts):
    return sorted(tuple(sorted(t)) for t in ts)

assert norm(three_sum([-1, 0, 1, 2, -1, -4])) == [(-1, -1, 2), (-1, 0, 1)]
assert three_sum([0, 1, 1]) == []
assert norm(three_sum([0, 0, 0, 0])) == [(0, 0, 0)]
rng = random.Random(3)
for _ in range(40):
    nums = [rng.randint(-5, 5) for _ in range(rng.randint(3, 12))]
    expect = sorted({tuple(sorted(c)) for c in itertools.combinations(nums, 3) if sum(c) == 0})
    got = norm(three_sum(nums))
    assert got == expect and len(got) == len(set(got))''',
    ),

    # ------------------------------------------------------------------ 18
    dict(
        id="four-sum",
        lc=18, slug="4sum",
        name="4Sum",
        difficulty="medium",
        framing=[
            "All distinct quadruplets summing to <code>target</code>. 3Sum with one more fixed index &mdash; and a chance to write the general <strong>k-Sum</strong> recursion once instead of copying loops.",
        ],
        approaches=[
            dict(
                name="Every quadruple",
                time="O(n<sup>4</sup>)",
                space="O(k)",
                tag="brute force",
                why=["All combinations of four, deduplicated with a set of sorted tuples."],
                code='''def four_sum(nums, target):
    return [list(t) for t in {tuple(sorted(c)) for c in itertools.combinations(nums, 4) if sum(c) == target}]''',
            ),
            dict(
                name="Two fixed loops plus two pointers",
                time="O(n&sup3;)",
                space="O(1) beyond the output",
                best=True,
                why=[
                    "Sort; fix <code>i</code> and <code>j</code> (skipping repeated values at each level), then two pointers on the rest. Three nested levels of O(n): O(n&sup3;).",
                ],
                code='''def four_sum(nums, target):
    nums, n, out = sorted(nums), len(nums), []
    for i in range(n - 3):
        if i and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, n - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            lo, hi = j + 1, n - 1
            while lo < hi:
                s = nums[i] + nums[j] + nums[lo] + nums[hi]
                if s < target:
                    lo += 1
                elif s > target:
                    hi -= 1
                else:
                    out.append([nums[i], nums[j], nums[lo], nums[hi]])
                    lo, hi = lo + 1, hi - 1
                    while lo < hi and nums[lo] == nums[lo - 1]:
                        lo += 1
    return out''',
            ),
            dict(
                name="General k-Sum recursion",
                time="O(n<sup>k-1</sup>)",
                space="O(k)",
                tag="any k",
                why=[
                    "<code>k_sum(start, k, target)</code> fixes one number (skipping duplicates) and recurses with k - 1 until k = 2, where two pointers finish the job. One function solves 2Sum through k-Sum, and the interviewer's follow-up \"what about 5Sum?\" costs nothing.",
                    "Early exits keep it fast: if the smallest possible sum of k numbers from here already exceeds the target, or the largest is below it, stop.",
                ],
                code='''def four_sum(nums, target):
    nums = sorted(nums)

    def k_sum(start, k, target):
        if start == len(nums) or nums[start] * k > target or nums[-1] * k < target:
            return []
        if k == 2:
            out, lo, hi = [], start, len(nums) - 1
            while lo < hi:
                s = nums[lo] + nums[hi]
                if s < target or (lo > start and nums[lo] == nums[lo - 1]):
                    lo += 1
                elif s > target:
                    hi -= 1
                else:
                    out.append([nums[lo], nums[hi]])
                    lo, hi = lo + 1, hi - 1
            return out
        out = []
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            for rest in k_sum(i + 1, k - 1, target - nums[i]):
                out.append([nums[i]] + rest)
        return out

    return k_sum(0, 4, target)''',
            ),
        ],
        tests='''def norm(ts):
    return sorted(tuple(sorted(t)) for t in ts)

assert norm(four_sum([1, 0, -1, 0, -2, 2], 0)) == [(-2, -1, 1, 2), (-2, 0, 0, 2), (-1, 0, 0, 1)]
assert norm(four_sum([2, 2, 2, 2, 2], 8)) == [(2, 2, 2, 2)]
rng = random.Random(4)
for _ in range(30):
    nums = [rng.randint(-4, 4) for _ in range(rng.randint(4, 10))]
    t = rng.randint(-4, 4)
    expect = sorted({tuple(sorted(c)) for c in itertools.combinations(nums, 4) if sum(c) == t})
    got = norm(four_sum(nums, t))
    assert got == expect and len(got) == len(set(got))''',
    ),

    # ------------------------------------------------------------------ 189
    dict(
        id="rotate-array",
        lc=189, slug="rotate-array",
        name="Rotate Array",
        difficulty="medium",
        framing=[
            "Rotate the array right by <code>k</code> steps, in place. The follow-up asks for at least three different solutions and O(1) extra space &mdash; the reversal trick is the one to remember.",
            "First reduce <code>k %= n</code>: rotating by n is the identity.",
        ],
        approaches=[
            dict(
                name="Rotate by one, k times",
                time="O(n &middot; k)",
                space="O(1)",
                tag="brute force",
                why=[
                    "Move the last element to the front k times, shifting everything each time. In place but quadratic when k is comparable to n.",
                ],
                code='''def rotate(nums, k):
    n = len(nums)
    for _ in range(k % n):
        last = nums[-1]
        for i in range(n - 1, 0, -1):
            nums[i] = nums[i - 1]
        nums[0] = last''',
            ),
            dict(
                name="Extra array",
                time="O(n)",
                space="O(n)",
                why=[
                    "Element i goes to <code>(i + k) % n</code>. Write into a copy, then copy back. Linear, with an O(n) buffer.",
                ],
                code='''def rotate(nums, k):
    n = len(nums)
    out = [0] * n
    for i, x in enumerate(nums):
        out[(i + k) % n] = x
    nums[:] = out''',
            ),
            dict(
                name="Three reversals",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Reverse the whole array, then reverse the first k elements, then the rest. The first reversal moves the last k elements to the front (in reverse order) and the rest to the back (in reverse order); the two partial reversals fix the order within each block.",
                    "Every element is swapped at most twice: O(n) time, O(1) space, and it is easy to get right under pressure.",
                ],
                code='''def rotate(nums, k):
    n = len(nums)
    k %= n

    def rev(lo, hi):
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo, hi = lo + 1, hi - 1

    rev(0, n - 1)
    rev(0, k - 1)
    rev(k, n - 1)''',
            ),
            dict(
                name="Cyclic replacements",
                time="O(n)",
                space="O(1)",
                tag="each element moved once",
                why=[
                    "Pick up the element at a start index, drop it at its destination, pick up what was there, and continue until the cycle returns to the start. There are <code>gcd(n, k)</code> such cycles; a counter of moves tells you when every element has been placed.",
                    "Exactly n writes, one per element &mdash; the fewest possible &mdash; but the cycle logic is easier to get wrong than reversal.",
                ],
                code='''def rotate(nums, k):
    n = len(nums)
    k %= n
    moved = start = 0
    while moved < n:
        i, carry = start, nums[start]
        while True:
            j = (i + k) % n
            nums[j], carry = carry, nums[j]
            i = j
            moved += 1
            if i == start:
                break
        start += 1''',
            ),
        ],
        tests='''a = [1, 2, 3, 4, 5, 6, 7]; rotate(a, 3); assert a == [5, 6, 7, 1, 2, 3, 4]
a = [-1, -100, 3, 99]; rotate(a, 2); assert a == [3, 99, -1, -100]
for n in range(1, 10):
    for k in range(0, 20):
        a = list(range(n)); rotate(a, k)
        assert a == [(i - k) % n for i in range(n)], (n, k)''',
    ),

    # ------------------------------------------------------------------ 11
    dict(
        id="container-most-water",
        lc=11, slug="container-with-most-water",
        name="Container With Most Water",
        difficulty="medium",
        framing=[
            "Pick two lines that, with the x-axis, hold the most water: <code>(j - i) &times; min(h[i], h[j])</code>. The two-pointer solution is O(n), and the argument for why moving the shorter line is safe is the real content.",
        ],
        approaches=[
            dict(
                name="Every pair",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=["Compute the area of every pair of lines."],
                code='''def max_area(height):
    n = len(height)
    return max((j - i) * min(height[i], height[j]) for i in range(n) for j in range(i + 1, n))''',
            ),
            dict(
                name="Two pointers, move the shorter side",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Start with the widest container. The area is limited by the shorter line. Moving the <em>taller</em> line inward can only shrink the width without raising that limit, so every container it could form with the shorter line is worse than the current one. The shorter line has therefore already achieved its best, and can be discarded.",
                    "Each step discards one line with proof, so n - 1 steps check every candidate that could possibly win.",
                ],
                code='''def max_area(height):
    lo, hi, best = 0, len(height) - 1, 0
    while lo < hi:
        best = max(best, (hi - lo) * min(height[lo], height[hi]))
        if height[lo] < height[hi]:
            lo += 1                            # the shorter line cannot do better
        else:
            hi -= 1
    return best''',
            ),
        ],
        tests='''assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
assert max_area([1, 1]) == 1
rng = random.Random(5)
for _ in range(50):
    h = [rng.randint(0, 20) for _ in range(rng.randint(2, 15))]
    assert max_area(h) == max((j - i) * min(h[i], h[j]) for i in range(len(h)) for j in range(i + 1, len(h)))''',
    ),

    # ------------------------------------------------------------------ 881
    dict(
        id="boats-to-save-people",
        lc=881, slug="boats-to-save-people",
        name="Boats to Save People",
        difficulty="medium",
        framing=[
            "Each boat carries at most two people with total weight at most <code>limit</code>. Minimise the number of boats. A greedy pairing: the heaviest person should share with the lightest if anyone can.",
        ],
        approaches=[
            dict(
                name="Sort, pair heaviest with lightest",
                time="O(n log n)",
                space="O(1) or O(n)",
                best=True,
                why=[
                    "Sort. The heaviest remaining person always needs a boat. If the lightest remaining person fits alongside, putting them together is never worse: anyone else who could have shared with the heaviest is at least as heavy as the lightest, so swapping partners cannot free up a better pairing. Otherwise the heaviest rides alone.",
                    "Each boat removes one or two people from the ends: O(n) after the sort.",
                ],
                code='''def num_rescue_boats(people, limit):
    people = sorted(people)
    lo, hi, boats = 0, len(people) - 1, 0
    while lo <= hi:
        if people[lo] + people[hi] <= limit:
            lo += 1                            # lightest rides along
        hi -= 1                                # heaviest always leaves
        boats += 1
    return boats''',
            ),
            dict(
                name="Counting sort, then the same greedy",
                time="O(n + limit)",
                space="O(limit)",
                why=[
                    "Weights are bounded by <code>limit</code> (at most 3 &times; 10<sup>4</sup>), so counting sort replaces the comparison sort. Then run the same two-pointer greedy over the expanded sorted list. Linear in n + limit.",
                ],
                code='''def num_rescue_boats(people, limit):
    counts = [0] * (limit + 1)
    for w in people:
        counts[w] += 1
    ordered = [w for w in range(limit + 1) for _ in range(counts[w])]
    lo, hi, boats = 0, len(ordered) - 1, 0
    while lo <= hi:
        if ordered[lo] + ordered[hi] <= limit:
            lo += 1
        hi -= 1
        boats += 1
    return boats''',
            ),
        ],
        tests='''assert num_rescue_boats([1, 2], 3) == 1
assert num_rescue_boats([3, 2, 2, 1], 3) == 3
assert num_rescue_boats([3, 5, 3, 4], 5) == 4


def _brute(people, limit):
    from functools import lru_cache
    @lru_cache(None)
    def go(rest):
        if not rest:
            return 0
        first, others = rest[0], rest[1:]
        best = 1 + go(others)
        for i, w in enumerate(others):
            if first + w <= limit:
                best = min(best, 1 + go(others[:i] + others[i + 1:]))
        return best
    return go(tuple(sorted(people)))

rng = random.Random(6)
for _ in range(40):
    limit = rng.randint(3, 10)
    p = [rng.randint(1, limit) for _ in range(rng.randint(1, 8))]
    assert num_rescue_boats(p, limit) == _brute(p, limit)''',
    ),

    # ------------------------------------------------------------------ 42
    dict(
        id="trapping-rain-water",
        lc=42, slug="trapping-rain-water",
        name="Trapping Rain Water",
        difficulty="hard",
        framing=[
            "How much water does an elevation map trap? Water above bar i rises to <code>min(tallest to the left, tallest to the right)</code>, minus the bar's own height. Every solution computes those two maxima; they differ in how cheaply.",
        ],
        approaches=[
            dict(
                name="Scan left and right from every bar",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "For each bar, find the tallest bar on each side by scanning. The formula directly, with every maximum recomputed.",
                ],
                code='''def trap(height):
    water = 0
    for i in range(len(height)):
        left, right = max(height[:i + 1]), max(height[i:])
        water += min(left, right) - height[i]
    return water''',
            ),
            dict(
                name="Prefix and suffix maximum arrays",
                time="O(n)",
                space="O(n)",
                why=[
                    "Precompute <code>left_max[i]</code> in one pass and <code>right_max[i]</code> in another, then apply the formula. Three linear passes and two extra arrays.",
                ],
                code='''def trap(height):
    n = len(height)
    left, right = [0] * n, [0] * n
    for i in range(n):
        left[i] = max(height[i], left[i - 1] if i else 0)
    for i in range(n - 1, -1, -1):
        right[i] = max(height[i], right[i + 1] if i < n - 1 else 0)
    return sum(min(l, r) - h for l, r, h in zip(left, right, height))''',
            ),
            dict(
                name="Monotonic stack, fill layer by layer",
                time="O(n)",
                space="O(n)",
                why=[
                    "Keep a stack of indices with decreasing heights. When a taller bar arrives, it closes a basin: pop the bottom, and the water above it is bounded by the new bar and the one now on top of the stack, times the width between them. This counts water in horizontal layers instead of vertical columns.",
                    "Each index is pushed and popped once: O(n). A useful technique to know because the same stack solves Largest Rectangle in Histogram.",
                ],
                code='''def trap(height):
    stack, water = [], 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break
            left = stack[-1]
            depth = min(height[left], h) - height[bottom]
            water += depth * (i - left - 1)
        stack.append(i)
    return water''',
            ),
            dict(
                name="Two pointers with running maxima",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Move inward from both ends keeping <code>left_max</code> and <code>right_max</code> seen so far. If <code>left_max &lt; right_max</code>, the water at the left pointer is decided by <code>left_max</code> alone: there is a bar at least as tall as <code>right_max</code> somewhere on its right, so the true right maximum is no smaller. Settle that position and advance; symmetric on the right.",
                    "One pass, two variables: the optimal answer, and the reasoning is the same \"the smaller side is already decided\" argument as Container With Most Water.",
                ],
                code='''def trap(height):
    lo, hi = 0, len(height) - 1
    left_max = right_max = water = 0
    while lo < hi:
        left_max = max(left_max, height[lo])
        right_max = max(right_max, height[hi])
        if left_max < right_max:
            water += left_max - height[lo]      # bounded by left_max for sure
            lo += 1
        else:
            water += right_max - height[hi]
            hi -= 1
    return water''',
            ),
        ],
        tests='''assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
assert trap([4, 2, 0, 3, 2, 5]) == 9
assert trap([1]) == 0
rng = random.Random(7)
for _ in range(50):
    h = [rng.randint(0, 6) for _ in range(rng.randint(1, 15))]
    assert trap(h) == sum(min(max(h[:i + 1]), max(h[i:])) - h[i] for i in range(len(h)))''',
    ),
    ],
),

dict(
    id="intervals",
    title="Intervals",
    idea=[
        "Sort intervals by start (or by end), and overlap questions become a single left-to-right sweep that only ever compares an interval with the one before it.",
    ],
    problems=[

    # ------------------------------------------------------------------ 57
    dict(
        id="insert-interval",
        lc=57, slug="insert-interval",
        name="Insert Interval",
        difficulty="medium",
        framing=[
            "Insert <code>newInterval</code> into a sorted list of non-overlapping intervals, merging where necessary. The list is already sorted, so no sort is needed: the intervals fall into three runs &mdash; entirely before, overlapping, entirely after.",
        ],
        approaches=[
            dict(
                name="Append, then Merge Intervals",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Add the new interval and run the general merge. Correct, but it re-sorts a list that was sorted already.",
                ],
                code='''def insert(intervals, new):
    merged = []
    for s, e in sorted(intervals + [new]):
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged''',
            ),
            dict(
                name="Three-phase linear scan",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Copy every interval that ends before the new one starts. Then absorb every interval that starts at or before the new one's end, stretching the new interval to cover them. Append it, then copy the rest.",
                    "One pass. The output can be n + 1 intervals, so O(n) is optimal &mdash; binary search could find the overlap region in O(log n), but building the result still costs O(n).",
                ],
                code='''def insert(intervals, new):
    out, i, n = [], 0, len(intervals)
    start, end = new
    while i < n and intervals[i][1] < start:          # before
        out.append(intervals[i]); i += 1
    while i < n and intervals[i][0] <= end:           # overlapping
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    out.append([start, end])
    return out + intervals[i:]                        # after''',
            ),
        ],
        tests='''assert insert([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
assert insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) == [[1, 2], [3, 10], [12, 16]]
assert insert([], [5, 7]) == [[5, 7]]
assert insert([[1, 5]], [6, 8]) == [[1, 5], [6, 8]]
assert insert([[1, 5]], [0, 0]) == [[0, 0], [1, 5]]''',
    ),

    # ------------------------------------------------------------------ 56
    dict(
        id="merge-intervals",
        lc=56, slug="merge-intervals",
        name="Merge Intervals",
        difficulty="medium",
        framing=[
            "Merge all overlapping intervals. After sorting by start, an interval overlaps the merged group so far exactly when it starts before the group ends &mdash; only the <em>last</em> merged interval can ever be affected.",
        ],
        approaches=[
            dict(
                name="Overlap graph, connected components",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                tag="brute force",
                why=[
                    "Treat intervals as nodes and connect each overlapping pair; each connected component merges into one interval (min start, max end). Correct without sorting, but builds O(n&sup2;) edges. It shows <em>what</em> merging means; sorting shows how to do it fast.",
                ],
                code='''def merge(intervals):
    n = len(intervals)
    adj = [[j for j in range(n) if j != i and intervals[i][0] <= intervals[j][1]
            and intervals[j][0] <= intervals[i][1]] for i in range(n)]
    seen, out = [False] * n, []
    for i in range(n):
        if seen[i]:
            continue
        stack, lo, hi = [i], intervals[i][0], intervals[i][1]
        seen[i] = True
        while stack:
            k = stack.pop()
            lo, hi = min(lo, intervals[k][0]), max(hi, intervals[k][1])
            for j in adj[k]:
                if not seen[j]:
                    seen[j] = True
                    stack.append(j)
        out.append([lo, hi])
    return sorted(out)''',
            ),
            dict(
                name="Sort by start, extend the last group",
                time="O(n log n)",
                space="O(n)",
                best=True,
                why=[
                    "Sort by start. Walk through: if the interval starts at or before the end of the last merged one, extend that end with <code>max</code> (the new interval may be entirely inside); otherwise it starts a new group.",
                    "Sorting dominates. The <code>max</code> is the common bug: <code>[[1, 10], [2, 3]]</code> must stay <code>[1, 10]</code>.",
                ],
                code='''def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)   # may be fully contained
        else:
            out.append([s, e])
    return out''',
            ),
        ],
        tests='''assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge([[1, 4], [4, 5]]) == [[1, 5]]
assert merge([[1, 10], [2, 3]]) == [[1, 10]]
rng = random.Random(8)
for _ in range(50):
    iv = [sorted(rng.sample(range(20), 2)) for _ in range(rng.randint(1, 8))]
    covered = set()
    for s, e in iv:
        covered |= {x / 2 for x in range(2 * s, 2 * e + 1)}
    got = merge([x[:] for x in iv])
    assert {x / 2 for s, e in got for x in range(2 * s, 2 * e + 1)} == covered
    assert all(a[1] < b[0] for a, b in zip(got, got[1:]))''',
    ),

    # ------------------------------------------------------------------ 435
    dict(
        id="non-overlapping-intervals",
        lc=435, slug="non-overlapping-intervals",
        name="Non-overlapping Intervals",
        difficulty="medium",
        framing=[
            "Remove the fewest intervals so the rest do not overlap (touching at an endpoint is fine). Equivalently, keep the most intervals &mdash; the classic <strong>activity selection</strong> problem, where greedily keeping the interval that ends first is provably optimal.",
        ],
        approaches=[
            dict(
                name="DP: longest chain of compatible intervals",
                time="O(n&sup2;)",
                space="O(n)",
                why=[
                    "Sort by start. <code>keep[i]</code> is the most intervals that can be kept ending with interval i: one more than the best <code>keep[j]</code> over earlier intervals that end before i starts. The answer is n minus the maximum. A longest-increasing-subsequence-shaped DP, correct but quadratic.",
                ],
                code='''def erase_overlap_intervals(intervals):
    iv = sorted(intervals)
    keep = [1] * len(iv)
    for i in range(len(iv)):
        for j in range(i):
            if iv[j][1] <= iv[i][0]:
                keep[i] = max(keep[i], keep[j] + 1)
    return len(iv) - max(keep)''',
            ),
            dict(
                name="Greedy: sort by end, keep the earliest-ending",
                time="O(n log n)",
                space="O(1) beyond sorting",
                best=True,
                why=[
                    "Sort by end time. Keep the first interval; then keep each interval that starts at or after the end of the last kept one, and remove the rest.",
                    "Exchange argument: in any optimal selection, swap its first interval for the one that ends earliest. That one ends no later, so it conflicts with nothing the original conflicted with less &mdash; the selection stays valid and the same size. Repeat the argument on what remains.",
                ],
                code='''def erase_overlap_intervals(intervals):
    removed, end = 0, float("-inf")
    for s, e in sorted(intervals, key=lambda iv: iv[1]):
        if s >= end:
            end = e                           # keep it
        else:
            removed += 1
    return removed''',
            ),
            dict(
                name="Greedy by start, drop the longer-ending one",
                time="O(n log n)",
                space="O(1) beyond sorting",
                why=[
                    "Sort by start instead. On an overlap, remove whichever of the two ends later &mdash; keep the smaller end. The same greedy principle expressed in start order, useful when the data arrives sorted by start.",
                ],
                code='''def erase_overlap_intervals(intervals):
    iv = sorted(intervals)
    removed, end = 0, iv[0][1]
    for s, e in iv[1:]:
        if s < end:
            removed += 1
            end = min(end, e)                 # keep whichever ends first
        else:
            end = e
    return removed''',
            ),
        ],
        tests='''assert erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
assert erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]) == 2
assert erase_overlap_intervals([[1, 2], [2, 3]]) == 0
rng = random.Random(9)
for _ in range(40):
    iv = [sorted(rng.sample(range(12), 2)) for _ in range(rng.randint(1, 8))]
    best = 0
    for r in range(len(iv) + 1):
        for combo in itertools.combinations(sorted(iv), r):
            if all(a[1] <= b[0] for a, b in zip(combo, combo[1:])):
                best = max(best, r)
    assert erase_overlap_intervals([x[:] for x in iv]) == len(iv) - best''',
    ),

    # ------------------------------------------------------------------ 2402
    dict(
        id="meeting-rooms-iii",
        lc=2402, slug="meeting-rooms-iii",
        name="Meeting Rooms III",
        difficulty="hard",
        framing=[
            "n rooms, meetings with unique start times. Each meeting takes the lowest-numbered free room; if none is free it waits for the room that frees up earliest (lowest number on ties) and keeps its original duration. Return the room that hosted the most meetings. The simulation is the problem; the data structures decide its speed.",
        ],
        approaches=[
            dict(
                name="Simulate by scanning all rooms",
                time="O(m log m + m &middot; n)",
                space="O(n)",
                why=[
                    "Keep each room's free-at time. For each meeting in start order, scan for the lowest free room; if none, scan for the one that frees earliest and delay the meeting. Correct and simple; each meeting costs O(n).",
                ],
                code='''def most_booked(n, meetings):
    free_at, count = [0] * n, [0] * n
    for start, end in sorted(meetings):
        room = next((r for r in range(n) if free_at[r] <= start), None)
        if room is None:
            room = min(range(n), key=lambda r: (free_at[r], r))
            end += free_at[room] - start        # delayed, same duration
        free_at[room] = end
        count[room] += 1
    return count.index(max(count))''',
            ),
            dict(
                name="Two heaps: free rooms and busy rooms",
                time="O(m log m + m log n)",
                space="O(n)",
                best=True,
                why=[
                    "A min-heap of free room numbers gives the lowest free room in O(log n). A min-heap of <code>(end time, room)</code> for busy rooms gives the earliest to free up, with ties broken by room number automatically.",
                    "Before each meeting, move every busy room that has finished by its start into the free heap. If a room is free, take the lowest; otherwise pop the earliest-ending busy room and push it back with the delayed end. Each meeting does O(1) heap operations amortised.",
                ],
                code='''def most_booked(n, meetings):
    free = list(range(n))                     # already a valid heap
    busy, count = [], [0] * n                  # (end, room)
    for start, end in sorted(meetings):
        while busy and busy[0][0] <= start:
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            room = heapq.heappop(free)
            heapq.heappush(busy, (end, room))
        else:
            finish, room = heapq.heappop(busy)
            heapq.heappush(busy, (finish + end - start, room))
        count[room] += 1
    return count.index(max(count))''',
            ),
        ],
        tests='''assert most_booked(2, [[0, 10], [1, 5], [2, 7], [3, 4]]) == 0
assert most_booked(3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]]) == 1
assert most_booked(1, [[0, 1]]) == 0
rng = random.Random(10)
for _ in range(40):
    n = rng.randint(1, 4)
    starts = rng.sample(range(0, 30), rng.randint(1, 10))
    meetings = [[s, s + rng.randint(1, 8)] for s in starts]
    free_at, count = [0] * n, [0] * n
    for s, e in sorted(meetings):
        room = next((r for r in range(n) if free_at[r] <= s), None)
        if room is None:
            room = min(range(n), key=lambda r: (free_at[r], r)); e += free_at[room] - s
        free_at[room] = e; count[room] += 1
    assert most_booked(n, meetings) == count.index(max(count))''',
    ),

    # ------------------------------------------------------------------ 1851
    dict(
        id="min-interval-each-query",
        lc=1851, slug="minimum-interval-to-include-each-query",
        name="Minimum Interval to Include Each Query",
        difficulty="hard",
        framing=[
            "For each query point, return the size of the smallest interval containing it (or -1). Answering queries one by one against all intervals is O(n &middot; q). Answering them <strong>offline</strong> &mdash; sorted, sweeping left to right &mdash; lets a heap track the intervals currently covering the sweep point.",
        ],
        approaches=[
            dict(
                name="Check every interval per query",
                time="O(n &middot; q)",
                space="O(1)",
                tag="brute force",
                why=[
                    "For each query, scan all intervals and take the smallest containing it. 10<sup>5</sup> &times; 10<sup>5</sup> in the worst case &mdash; far too slow, but the correctness reference.",
                ],
                code='''def min_interval(intervals, queries):
    out = []
    for q in queries:
        sizes = [r - l + 1 for l, r in intervals if l <= q <= r]
        out.append(min(sizes) if sizes else -1)
    return out''',
            ),
            dict(
                name="Offline sweep with a min-heap",
                time="O(n log n + q log q)",
                space="O(n + q)",
                best=True,
                why=[
                    "Sort intervals by left end and queries by value (remembering original positions). Sweep the queries in increasing order: push every interval that has started (<code>left &le; q</code>) onto a heap keyed by <code>(size, right)</code>; pop from the top any interval that has already ended (<code>right &lt; q</code>). The top of the heap is then the smallest interval containing q.",
                    "Popping lazily is safe: an interval that ended before this query has also ended before every later query, since queries are processed in increasing order. Every interval is pushed and popped at most once.",
                ],
                code='''def min_interval(intervals, queries):
    intervals = sorted(intervals)
    out, heap, i = [-1] * len(queries), [], 0
    for q, pos in sorted((q, pos) for pos, q in enumerate(queries)):
        while i < len(intervals) and intervals[i][0] <= q:
            l, r = intervals[i]
            heapq.heappush(heap, (r - l + 1, r))
            i += 1
        while heap and heap[0][1] < q:
            heapq.heappop(heap)               # ended before q: gone for good
        if heap:
            out[pos] = heap[0][0]
    return out''',
            ),
        ],
        tests='''assert min_interval([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5]) == [3, 3, 1, 4]
assert min_interval([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22]) == [2, -1, 4, 6]
rng = random.Random(11)
for _ in range(40):
    iv = [sorted(rng.sample(range(15), 2)) for _ in range(rng.randint(1, 8))]
    qs = [rng.randint(0, 16) for _ in range(rng.randint(1, 8))]
    expect = []
    for q in qs:
        s = [r - l + 1 for l, r in iv if l <= q <= r]
        expect.append(min(s) if s else -1)
    assert min_interval(iv, qs) == expect''',
    ),
    ],
),
    ],
)
