# -*- coding: utf-8 -*-
"""Arrays and Hashing topic for the DSA path (NeetCode 250: Arrays & Hashing).

Same contract as content/dsa.py: every `code` block is executed by build.py
with PRELUDE + this topic's `prelude` + the problem's `tests` appended. Each
problem walks the ladder from brute force to time-optimal to space-optimal,
and the tests cross-check against a brute force wherever one is cheap.
"""

PRELUDE_HASH = '''import random
from collections import Counter, defaultdict
'''


HASHING_TOPIC = dict(
    id="hashing",
    title="Arrays and Hashing",
    prelude=PRELUDE_HASH,
    sections=[

dict(
    id="arrays-hashing",
    title="Arrays and hashing",
    idea=[
        "A hash set or hash map turns \"have I seen this?\" and \"how many of these?\" into O(1) questions. Most problems here are an O(n&sup2;) double loop that becomes O(n) once one of the loops is replaced by a lookup &mdash; and a few then go further, getting rid of the hash table by reusing the input array itself.",
    ],
    problems=[

    # ------------------------------------------------------------------ 1929
    dict(
        id="concatenation-of-array",
        lc=1929, slug="concatenation-of-array",
        name="Concatenation of Array",
        difficulty="easy",
        framing=[
            "Return <code>ans</code> of length 2n with <code>ans[i] = ans[i + n] = nums[i]</code>. There is no algorithmic trick; the point is to see that every approach is O(n) because the output itself has 2n elements, and to notice the constant-factor differences between building a list element by element and letting the runtime copy memory in bulk.",
        ],
        approaches=[
            dict(
                name="Append twice in a loop",
                time="O(n)",
                space="O(1) beyond the output",
                why=[
                    "Loop over the array twice, appending each element. This is what the definition says, and it is how you would write it in a language without list operations.",
                    "Each append is amortised O(1): Python lists over-allocate, so an occasional resize copies everything but the average cost per append stays constant. 2n appends, O(n) total.",
                ],
                code='''def get_concatenation(nums):
    ans = []
    for _ in range(2):
        for x in nums:
            ans.append(x)
    return ans''',
            ),
            dict(
                name="Pre-allocate and fill both halves",
                time="O(n)",
                space="O(1) beyond the output",
                why=[
                    "Allocate the result once at its final size and write <code>ans[i]</code> and <code>ans[i + n]</code> in the same loop. No resizing ever happens, and this is exactly the formula in the problem statement.",
                    "Same O(n); it is the version to write in C++ or Java, where you size arrays up front.",
                ],
                code='''def get_concatenation(nums):
    n = len(nums)
    ans = [0] * (2 * n)
    for i, x in enumerate(nums):
        ans[i] = ans[i + n] = x
    return ans''',
            ),
            dict(
                name="List concatenation",
                time="O(n)",
                space="O(1) beyond the output",
                best=True,
                why=[
                    "<code>nums + nums</code> (or <code>nums * 2</code>) allocates the result once and copies both halves with a C-level memory copy. Asymptotically identical, but typically an order of magnitude faster than a Python loop because no bytecode runs per element.",
                    "In an interview, write this and say why it is fine: the problem has no hidden constraint, and the output size already forces O(n).",
                ],
                code='''def get_concatenation(nums):
    return nums + nums''',
            ),
        ],
        tests='''assert get_concatenation([1, 2, 1]) == [1, 2, 1, 1, 2, 1]
assert get_concatenation([1, 3, 2, 1]) == [1, 3, 2, 1, 1, 3, 2, 1]
assert get_concatenation([7]) == [7, 7]''',
    ),

    # ------------------------------------------------------------------ 217
    dict(
        id="contains-duplicate",
        lc=217, slug="contains-duplicate",
        name="Contains Duplicate",
        difficulty="easy",
        framing=[
            "Does any value appear at least twice? The canonical first hashing problem, and the cleanest demonstration of the three-way trade between comparing everything (slow, no memory), sorting (medium, little memory) and hashing (fast, linear memory).",
        ],
        approaches=[
            dict(
                name="Compare every pair",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "Check <code>nums[i] == nums[j]</code> for every <code>i &lt; j</code>. Correct and memory-free, but there are n(n-1)/2 pairs &mdash; about 5 &times; 10<sup>9</sup> for n = 10<sup>5</sup>, which is minutes of Python.",
                    "Always say this one out loud first. It fixes the baseline, and the two improvements below are both \"avoid comparing pairs that cannot matter\".",
                ],
                code='''def contains_duplicate(nums):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] == nums[j]:
                return True
    return False''',
            ),
            dict(
                name="Sort, then compare neighbours",
                time="O(n log n)",
                space="O(1) or O(n)",
                why=[
                    "After sorting, equal values are adjacent, so one pass comparing each element with the next finds any duplicate. The pair comparisons drop from n&sup2;/2 to n - 1.",
                    "Space depends on the sort. An in-place sort such as heapsort is O(1). Python's <code>list.sort</code> is Timsort, which needs up to n/2 extra slots for merging &mdash; so in Python this is O(n) in practice. It also mutates the caller's list unless you copy it first.",
                    "Pick this when memory is tight and you are allowed to reorder the input.",
                ],
                code='''def contains_duplicate(nums):
    nums = sorted(nums)
    return any(nums[i] == nums[i + 1] for i in range(len(nums) - 1))''',
            ),
            dict(
                name="Hash set, stop at the first repeat",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Walk the array keeping a set of values seen so far. A value already in the set is a duplicate; stop immediately. Set membership and insertion are O(1) on average, so the whole scan is O(n).",
                    "The early exit matters: on an input whose second element repeats the first, this does two steps where the sort does a full O(n log n). The price is up to n stored values.",
                    "<code>len(set(nums)) != len(nums)</code> is the one-line version &mdash; also O(n), but it always builds the full set and cannot stop early.",
                ],
                code='''def contains_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False''',
            ),
        ],
        tests='''assert contains_duplicate([1, 2, 3, 1]) is True
assert contains_duplicate([1, 2, 3, 4]) is False
assert contains_duplicate([1, 1, 1, 3, 3, 4, 3, 2, 4, 2]) is True
assert contains_duplicate([5]) is False
rng = random.Random(0)
for _ in range(50):
    nums = [rng.randint(-5, 30) for _ in range(rng.randint(1, 20))]
    assert contains_duplicate(nums) is (len(set(nums)) != len(nums))''',
    ),

    # ------------------------------------------------------------------ 242
    dict(
        id="valid-anagram",
        lc=242, slug="valid-anagram",
        name="Valid Anagram",
        difficulty="easy",
        framing=[
            "Are <code>s</code> and <code>t</code> rearrangements of each other? Two strings are anagrams exactly when they contain the same characters with the same counts, so the question is how cheaply you can compare two multisets.",
            "The follow-up (\"what if the inputs contain Unicode?\") is about which approach survives a large alphabet.",
        ],
        approaches=[
            dict(
                name="Sort both strings",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Anagrams have identical sorted forms. Sort both and compare. Simple, correct for any alphabet, and dominated by the sort.",
                    "Python strings are immutable, so <code>sorted</code> builds lists of length n: O(n) space.",
                ],
                code='''def is_anagram(s, t):
    return sorted(s) == sorted(t)''',
            ),
            dict(
                name="Count with a hash map",
                time="O(n)",
                space="O(k)",
                why=[
                    "Count each character of <code>s</code>, subtract each character of <code>t</code>, and check that every count is back to zero. k is the number of distinct characters, so this also handles Unicode without change &mdash; the answer to the follow-up.",
                    "An early length check rejects strings of different lengths in O(1).",
                ],
                code='''def is_anagram(s, t):
    if len(s) != len(t):
        return False
    counts = defaultdict(int)
    for a, b in zip(s, t):
        counts[a] += 1
        counts[b] -= 1
    return all(v == 0 for v in counts.values())''',
            ),
            dict(
                name="Fixed array of 26 counters",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "The constraints say lowercase English letters only, so a list of 26 integers indexed by <code>ord(ch) - ord('a')</code> replaces the hash map. Space is O(26) = O(1) regardless of n, and indexing a list is cheaper than hashing.",
                    "<code>Counter(s) == Counter(t)</code> is the idiomatic Python one-liner and is O(n) too; mention it, but be ready to write the counting yourself.",
                ],
                code='''def is_anagram(s, t):
    if len(s) != len(t):
        return False
    counts = [0] * 26
    for a, b in zip(s, t):
        counts[ord(a) - 97] += 1
        counts[ord(b) - 97] -= 1
    return not any(counts)''',
            ),
        ],
        tests='''assert is_anagram("anagram", "nagaram") is True
assert is_anagram("rat", "car") is False
assert is_anagram("a", "ab") is False
assert is_anagram("aacc", "ccac") is False
rng = random.Random(1)
for _ in range(50):
    s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 8)))
    t = "".join(rng.sample(s, len(s))) if rng.random() < 0.5 else "".join(rng.choice("abc") for _ in range(len(s)))
    assert is_anagram(s, t) is (sorted(s) == sorted(t))''',
    ),

    # ------------------------------------------------------------------ 1
    dict(
        id="two-sum",
        lc=1, slug="two-sum",
        name="Two Sum",
        difficulty="easy",
        framing=[
            "Return the indices of the two numbers that add up to <code>target</code>; exactly one answer exists and an element cannot be used twice. The most famous interview question, and the template for \"replace the inner loop with a lookup\".",
        ],
        pitfall="Filling the hash map with every value first and then looking up <code>target - x</code>. When <code>target = 2x</code> the lookup finds <code>x</code> itself. Look up before inserting, and the element can only ever pair with an earlier one.",
        approaches=[
            dict(
                name="Check every pair",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "Try each <code>i &lt; j</code>. The inner loop answers \"is there a later element equal to <code>target - nums[i]</code>?\" &mdash; a question a hash map answers in O(1).",
                ],
                code='''def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]''',
            ),
            dict(
                name="Sort indices, two pointers",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Sort the indices by value, then move a left pointer up and a right pointer down: a sum that is too small needs a bigger left value, too big needs a smaller right value. Each step discards one candidate for good, so the scan is O(n) after the O(n log n) sort.",
                    "The indices must be sorted rather than the values, because the answer is positions in the original array. This is the approach that generalises to 3Sum and 4Sum.",
                ],
                code='''def two_sum(nums, target):
    order = sorted(range(len(nums)), key=nums.__getitem__)
    lo, hi = 0, len(order) - 1
    while lo < hi:
        total = nums[order[lo]] + nums[order[hi]]
        if total == target:
            return sorted([order[lo], order[hi]])
        if total < target:
            lo += 1
        else:
            hi -= 1''',
            ),
            dict(
                name="One-pass hash map",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Walk the array once. For each value, ask whether its complement <code>target - x</code> has already been seen; if so, the pair is found. Otherwise record <code>x</code>'s index. The map holds values seen so far, so one pass suffices and no element pairs with itself.",
                    "O(n) time and up to n stored entries. When memory is the constraint and the input may be reordered, the sort-based approach is the fallback.",
                ],
                code='''def two_sum(nums, target):
    index = {}
    for i, x in enumerate(nums):
        if target - x in index:
            return [index[target - x], i]
        index[x] = i''',
            ),
        ],
        tests='''assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert sorted(two_sum([3, 2, 4], 6)) == [1, 2]
assert two_sum([3, 3], 6) == [0, 1]
rng = random.Random(2)
for _ in range(50):
    nums = rng.sample(range(-50, 50), rng.randint(2, 15))
    i, j = sorted(rng.sample(range(len(nums)), 2))
    target = nums[i] + nums[j]
    a, b = sorted(two_sum(nums, target))
    assert a != b and nums[a] + nums[b] == target''',
    ),

    # ------------------------------------------------------------------ 14
    dict(
        id="longest-common-prefix",
        lc=14, slug="longest-common-prefix",
        name="Longest Common Prefix",
        difficulty="easy",
        framing=[
            "The longest string that every word starts with. Every approach does the same total work in the worst case &mdash; all characters of the prefix, in every string, must be looked at &mdash; so the differences are in how early each one can stop.",
            "Let n be the number of strings and m the length of the shortest. The answer is at most m characters long.",
        ],
        approaches=[
            dict(
                name="Horizontal scan: shrink the prefix string by string",
                time="O(S)",
                space="O(1)",
                why=[
                    "Start with the first word as the candidate prefix and cut it down against each following word until that word starts with it. S is the total number of characters across all strings.",
                    "Weakness: a long first word is trimmed one character at a time even when a much shorter word later makes most of it impossible.",
                ],
                code='''def longest_common_prefix(strs):
    prefix = strs[0]
    for word in strs[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
    return prefix''',
            ),
            dict(
                name="Vertical scan: one column at a time",
                time="O(n &middot; m)",
                space="O(1)",
                best=True,
                why=[
                    "Compare the first character of every word, then the second, and stop at the first column where a word ends or disagrees. It never looks past the answer plus one column, so it is at most O(n &middot; m) and stops early on short answers.",
                    "This is the version to give: short, early-exiting, and no string copies.",
                ],
                code='''def longest_common_prefix(strs):
    for i, ch in enumerate(strs[0]):
        for word in strs[1:]:
            if i == len(word) or word[i] != ch:
                return strs[0][:i]
    return strs[0]''',
            ),
            dict(
                name="Sort, compare first and last",
                time="O(S log n)",
                space="O(n)",
                why=[
                    "After sorting lexicographically, the first and last words are the most different pair; whatever prefix they share, every word between them shares too. So only two words need comparing &mdash; after a sort that costs more than the scan it saves.",
                    "A neat observation to mention; <code>min</code> and <code>max</code> give the same two words in O(S) without sorting.",
                ],
                code='''def longest_common_prefix(strs):
    first, last = min(strs), max(strs)
    i = 0
    while i < len(first) and i < len(last) and first[i] == last[i]:
        i += 1
    return first[:i]''',
            ),
        ],
        tests='''assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
assert longest_common_prefix(["dog", "racecar", "car"]) == ""
assert longest_common_prefix(["a"]) == "a"
assert longest_common_prefix(["", "b"]) == ""
assert longest_common_prefix(["ab", "a"]) == "a"
import os
rng = random.Random(3)
for _ in range(50):
    ws = ["".join(rng.choice("ab") for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(1, 5))]
    assert longest_common_prefix(ws) == os.path.commonprefix(ws)''',
    ),

    # ------------------------------------------------------------------ 49
    dict(
        id="group-anagrams",
        lc=49, slug="group-anagrams",
        name="Group Anagrams",
        difficulty="medium",
        framing=[
            "Group the words that are anagrams of each other. The whole problem is choosing a <strong>canonical key</strong>: something every anagram of a word maps to, and no non-anagram does. Then a dict from key to list does the grouping.",
            "With m words of length up to k, the key choice decides the cost.",
        ],
        approaches=[
            dict(
                name="Compare every pair with an anagram check",
                time="O(m&sup2; &middot; k)",
                space="O(m)",
                tag="brute force",
                why=[
                    "For each ungrouped word, scan the rest and pull in every anagram, using a counting check. m&sup2; comparisons of O(k) each.",
                    "It is the approach a hash map is meant to replace: instead of comparing words to each other, compute something about each word alone and let the dict do the matching.",
                ],
                code='''def group_anagrams(strs):
    groups, used = [], [False] * len(strs)
    for i, w in enumerate(strs):
        if used[i]:
            continue
        group, key = [w], Counter(w)
        for j in range(i + 1, len(strs)):
            if not used[j] and len(strs[j]) == len(w) and Counter(strs[j]) == key:
                used[j] = True
                group.append(strs[j])
        groups.append(group)
    return groups''',
            ),
            dict(
                name="Sorted word as the key",
                time="O(m &middot; k log k)",
                space="O(m &middot; k)",
                why=[
                    "Anagrams sort to the same string, so <code>\"\".join(sorted(w))</code> is a valid key. Each word is sorted once: O(k log k), and the dict groups them in one pass.",
                    "This is the answer most people give and it is fine for short words.",
                ],
                code='''def group_anagrams(strs):
    groups = defaultdict(list)
    for w in strs:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())''',
            ),
            dict(
                name="Letter-count tuple as the key",
                time="O(m &middot; k)",
                space="O(m &middot; k)",
                best=True,
                why=[
                    "Count the 26 letters and use the tuple of counts as the key. Building it is O(k) per word, removing the log factor. Tuples are hashable, lists are not &mdash; that is why it is converted.",
                    "In practice the sort-based key is often faster in Python for short words because <code>sorted</code> runs in C; the counting key wins asymptotically and for long words. Saying that is a good sign you understand both.",
                ],
                code='''def group_anagrams(strs):
    groups = defaultdict(list)
    for w in strs:
        counts = [0] * 26
        for ch in w:
            counts[ord(ch) - 97] += 1
        groups[tuple(counts)].append(w)
    return list(groups.values())''',
            ),
        ],
        tests='''def norm(groups):
    return sorted(sorted(g) for g in groups)

assert norm(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
assert norm(group_anagrams([""])) == [[""]]
assert norm(group_anagrams(["a"])) == [["a"]]
rng = random.Random(4)
for _ in range(30):
    ws = ["".join(rng.choice("abc") for _ in range(rng.randint(0, 3))) for _ in range(rng.randint(1, 10))]
    ref = defaultdict(list)
    for w in ws:
        ref[tuple(sorted(w))].append(w)
    assert norm(group_anagrams(ws)) == norm(ref.values())''',
    ),

    # ------------------------------------------------------------------ 27
    dict(
        id="remove-element",
        lc=27, slug="remove-element",
        name="Remove Element",
        difficulty="easy",
        framing=[
            "Remove every occurrence of <code>val</code> <em>in place</em> and return how many elements remain; those must occupy the first k slots, in any order. The in-place requirement is what the problem is about: the output lives inside the input.",
        ],
        approaches=[
            dict(
                name="Build a filtered copy, write it back",
                time="O(n)",
                space="O(n)",
                why=[
                    "Collect the elements to keep in a new list and copy them into the front of <code>nums</code>. Correct and easy, but it allocates a second array, which the problem forbids.",
                ],
                code='''def remove_element(nums, val):
    kept = [x for x in nums if x != val]
    nums[:len(kept)] = kept
    return len(kept)''',
            ),
            dict(
                name="Read and write pointers",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "A read pointer scans every element; a write pointer marks where the next kept element goes. Copy each non-<code>val</code> element to the write position and advance it. Kept elements stay in their original order.",
                    "Every element is read once, and each kept element written once: O(n) time, O(1) space. This read/write-pointer pattern is the backbone of every \"compact the array in place\" problem.",
                ],
                code='''def remove_element(nums, val):
    k = 0
    for x in nums:
        if x != val:
            nums[k] = x
            k += 1
    return k''',
            ),
            dict(
                name="Swap with the end when removals are rare",
                time="O(n)",
                space="O(1)",
                tag="fewest writes",
                why=[
                    "When <code>val</code> is rare, the previous version still rewrites almost every element. Instead, when you find <code>val</code>, overwrite it with the last element and shrink the array by one &mdash; without advancing, since the moved element has not been checked yet.",
                    "Writes drop to the number of removed elements. The order of the kept elements changes, which the problem allows.",
                ],
                code='''def remove_element(nums, val):
    i, n = 0, len(nums)
    while i < n:
        if nums[i] == val:
            nums[i] = nums[n - 1]
            n -= 1
        else:
            i += 1
    return n''',
            ),
        ],
        tests='''for nums, val in [([3, 2, 2, 3], 3), ([0, 1, 2, 2, 3, 0, 4, 2], 2), ([], 1), ([1], 1), ([4, 5], 6)]:
    expect = sorted(x for x in nums if x != val)
    arr = nums[:]
    k = remove_element(arr, val)
    assert k == len(expect) and sorted(arr[:k]) == expect''',
    ),

    # ------------------------------------------------------------------ 169
    dict(
        id="majority-element",
        lc=169, slug="majority-element",
        name="Majority Element",
        difficulty="easy",
        framing=[
            "Find the element that appears more than n/2 times; one is guaranteed to exist. The follow-up asks for O(n) time and O(1) space, which rules out both counting (memory) and sorting (time) and leads to one of the prettiest algorithms in interviews: Boyer-Moore voting.",
        ],
        approaches=[
            dict(
                name="Count each candidate",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "For each element, count its occurrences with a full scan and return the first one above n/2.",
                ],
                code='''def majority_element(nums):
    for x in nums:
        if nums.count(x) > len(nums) // 2:
            return x''',
            ),
            dict(
                name="Hash map of counts",
                time="O(n)",
                space="O(n)",
                why=[
                    "Count everything once and return the value with the top count. Linear time, but up to n/2 distinct values are stored.",
                ],
                code='''def majority_element(nums):
    counts = Counter(nums)
    return max(counts, key=counts.get)''',
            ),
            dict(
                name="Sort, take the middle",
                time="O(n log n)",
                space="O(1) or O(n)",
                why=[
                    "An element filling more than half the positions must cover the middle index of the sorted array, wherever its run starts. One line, no counting; the cost is the sort.",
                ],
                code='''def majority_element(nums):
    return sorted(nums)[len(nums) // 2]''',
            ),
            dict(
                name="Boyer-Moore voting",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Keep a candidate and a counter. A matching element adds a vote; a different one cancels a vote; at zero, the next element becomes the new candidate.",
                    "Why it works: think of each cancellation as removing one majority element and one other element from the array. The majority has more than half of all elements, so it can never be fully cancelled by the rest &mdash; it is the candidate left standing.",
                    "O(n) time, two variables of state. If a majority is <em>not</em> guaranteed, a second pass must verify the candidate's count.",
                ],
                code='''def majority_element(nums):
    candidate, votes = None, 0
    for x in nums:
        if votes == 0:
            candidate = x
        votes += 1 if x == candidate else -1
    return candidate''',
            ),
        ],
        tests='''assert majority_element([3, 2, 3]) == 3
assert majority_element([2, 2, 1, 1, 1, 2, 2]) == 2
assert majority_element([1]) == 1
rng = random.Random(5)
for _ in range(50):
    n = rng.randint(1, 15)
    maj = rng.randint(0, 9)
    nums = [maj] * (n // 2 + 1) + [rng.randint(0, 9) for _ in range(n - n // 2 - 1)]
    rng.shuffle(nums)
    assert majority_element(nums) == Counter(nums).most_common(1)[0][0]''',
    ),

    # ------------------------------------------------------------------ 705
    dict(
        id="design-hashset",
        lc=705, slug="design-hashset",
        name="Design HashSet",
        difficulty="easy",
        framing=[
            "Implement <code>add</code>, <code>remove</code> and <code>contains</code> without a built-in hash table. Keys are integers in <code>[0, 10<sup>6</sup>]</code> and there are at most 10<sup>4</sup> calls. The interesting part is the design trade: a direct-address table is trivially fast but sized by the key range; a real hash table is sized by the number of keys actually stored.",
        ],
        approaches=[
            dict(
                name="Direct-address boolean array",
                time="O(1) per operation",
                space="O(key range)",
                why=[
                    "One slot per possible key: <code>present[key]</code>. Every operation is a single index. The catch is memory proportional to the key <em>range</em> &mdash; a million slots to store at most ten thousand keys, and unusable if keys were arbitrary 64-bit integers.",
                ],
                code='''class MyHashSet:
    def __init__(self):
        self.present = [False] * (10 ** 6 + 1)

    def add(self, key):
        self.present[key] = True

    def remove(self, key):
        self.present[key] = False

    def contains(self, key):
        return self.present[key]''',
            ),
            dict(
                name="Separate chaining with buckets",
                time="O(1) average, O(n) worst",
                space="O(buckets + n)",
                best=True,
                why=[
                    "Hash each key to one of B buckets (<code>key % B</code>) and keep a small list per bucket. Operations scan only their bucket. With B around the expected number of keys, buckets hold O(1) keys on average &mdash; the <em>load factor</em> n/B stays constant.",
                    "Pick B prime (here 1009 &times; ... ; any prime not close to a power of two), so that keys with a common pattern &mdash; say all multiples of 1000 &mdash; do not pile into a few buckets.",
                    "The worst case, when every key collides, degrades to a linear scan. Production tables resize (double B and rehash) when the load factor grows; that keeps the average O(1) as n grows, with O(1) amortised cost per resize.",
                ],
                code='''class MyHashSet:
    B = 10007                                   # a prime bucket count

    def __init__(self):
        self.buckets = [[] for _ in range(self.B)]

    def _bucket(self, key):
        return self.buckets[key % self.B]

    def add(self, key):
        b = self._bucket(key)
        if key not in b:
            b.append(key)

    def remove(self, key):
        b = self._bucket(key)
        if key in b:
            b.remove(key)

    def contains(self, key):
        return key in self._bucket(key)''',
            ),
        ],
        tests='''s = MyHashSet()
s.add(1); s.add(2)
assert s.contains(1) is True and s.contains(3) is False
s.add(2)
assert s.contains(2) is True
s.remove(2)
assert s.contains(2) is False
rng, s, model = random.Random(6), MyHashSet(), set()
for _ in range(3000):
    k, op = rng.randint(0, 10 ** 6), rng.random()
    k = k if rng.random() < 0.5 else k % 50          # plenty of repeats
    if op < 0.4:
        s.add(k); model.add(k)
    elif op < 0.7:
        s.remove(k); model.discard(k)
    else:
        assert s.contains(k) == (k in model)''',
    ),

    # ------------------------------------------------------------------ 706
    dict(
        id="design-hashmap",
        lc=706, slug="design-hashmap",
        name="Design HashMap",
        difficulty="easy",
        framing=[
            "The same exercise with values: <code>put(key, value)</code>, <code>get(key)</code> (or -1), <code>remove(key)</code>. The one new detail is that <code>put</code> on an existing key must <em>update</em> it, not add a second entry.",
        ],
        approaches=[
            dict(
                name="Direct-address array",
                time="O(1) per operation",
                space="O(key range)",
                why=[
                    "One slot per possible key storing the value, with -1 meaning absent. Constant time, memory sized by the range of keys rather than how many are stored.",
                ],
                code='''class MyHashMap:
    def __init__(self):
        self.slots = [-1] * (10 ** 6 + 1)

    def put(self, key, value):
        self.slots[key] = value

    def get(self, key):
        return self.slots[key]

    def remove(self, key):
        self.slots[key] = -1''',
            ),
            dict(
                name="Separate chaining with (key, value) pairs",
                time="O(1) average",
                space="O(buckets + n)",
                best=True,
                why=[
                    "Each bucket holds <code>[key, value]</code> pairs. <code>put</code> scans its bucket and updates in place if the key is there, else appends; <code>remove</code> deletes the pair. Average bucket length is the load factor n/B, a constant when B is chosen well.",
                    "Storing pairs as small lists (not tuples) is what lets <code>put</code> update the value without removing and re-adding.",
                ],
                code='''class MyHashMap:
    B = 10007

    def __init__(self):
        self.buckets = [[] for _ in range(self.B)]

    def put(self, key, value):
        bucket = self.buckets[key % self.B]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value                 # update, do not duplicate
                return
        bucket.append([key, value])

    def get(self, key):
        for k, v in self.buckets[key % self.B]:
            if k == key:
                return v
        return -1

    def remove(self, key):
        bucket = self.buckets[key % self.B]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                return''',
            ),
        ],
        tests='''m = MyHashMap()
m.put(1, 1); m.put(2, 2)
assert m.get(1) == 1 and m.get(3) == -1
m.put(2, 1)
assert m.get(2) == 1
m.remove(2)
assert m.get(2) == -1
rng, m, model = random.Random(7), MyHashMap(), {}
for _ in range(3000):
    k = rng.randint(0, 10 ** 6) if rng.random() < 0.5 else rng.randint(0, 40)
    op = rng.random()
    if op < 0.4:
        v = rng.randint(0, 10 ** 6); m.put(k, v); model[k] = v
    elif op < 0.6:
        m.remove(k); model.pop(k, None)
    else:
        assert m.get(k) == model.get(k, -1)''',
    ),

    # ------------------------------------------------------------------ 912
    dict(
        id="sort-an-array",
        lc=912, slug="sort-an-array",
        name="Sort an Array",
        difficulty="medium",
        framing=[
            "Sort the array without built-in sort functions, in O(n log n) time and with the smallest space you can. This is where you show you know the classic sorts and, more importantly, their trade-offs: stability, extra memory, worst cases and when a non-comparison sort wins.",
            "LeetCode's tests include large arrays of equal values and already-sorted arrays, which break naive quicksort.",
        ],
        approaches=[
            dict(
                name="Insertion sort",
                time="O(n&sup2;)",
                space="O(1)",
                tag="too slow here",
                why=[
                    "Grow a sorted prefix, inserting each new element by shifting larger ones right. O(n&sup2;) in general but O(n) on nearly sorted input, and the fastest method for tiny arrays &mdash; which is why Timsort and introsort switch to it below about 16&ndash;64 elements.",
                ],
                code='''def sort_array(nums):
    nums = nums[:]
    for i in range(1, len(nums)):
        x, j = nums[i], i - 1
        while j >= 0 and nums[j] > x:
            nums[j + 1] = nums[j]
            j -= 1
        nums[j + 1] = x
    return nums''',
            ),
            dict(
                name="Merge sort",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Split in half, sort each half, merge. Guaranteed O(n log n) on every input and <strong>stable</strong> (equal elements keep their order), at the cost of an O(n) buffer for merging. Python's own Timsort is a highly tuned merge sort.",
                ],
                code='''def sort_array(nums):
    if len(nums) <= 1:
        return nums[:]
    mid = len(nums) // 2
    left, right = sort_array(nums[:mid]), sort_array(nums[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:              # <= keeps it stable
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]''',
            ),
            dict(
                name="Heap sort",
                time="O(n log n)",
                space="O(1)",
                best=True,
                tag="least space",
                why=[
                    "Heapify the array into a max-heap in O(n), then repeatedly swap the maximum to the end and sift the new root down over the shrinking prefix. Guaranteed O(n log n) and genuinely in place: O(1) extra space.",
                    "Not stable, and slower in practice than quicksort because its memory accesses jump around the array &mdash; but it is the answer when the interviewer asks for O(n log n) worst case <em>and</em> O(1) space together.",
                ],
                code='''def sort_array(nums):
    nums = nums[:]

    def sift(i, n):
        while True:
            big, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n and nums[l] > nums[big]:
                big = l
            if r < n and nums[r] > nums[big]:
                big = r
            if big == i:
                return
            nums[i], nums[big] = nums[big], nums[i]
            i = big

    n = len(nums)
    for i in range(n // 2 - 1, -1, -1):      # O(n) heapify
        sift(i, n)
    for end in range(n - 1, 0, -1):
        nums[0], nums[end] = nums[end], nums[0]
        sift(0, end)
    return nums''',
            ),
            dict(
                name="Quicksort, random pivot, three-way partition",
                time="O(n log n) expected",
                space="O(log n) expected",
                why=[
                    "Partition around a pivot into less-than, equal and greater-than regions, then recurse on the two outer regions. A <em>random</em> pivot defeats sorted inputs (the O(n&sup2;) case for a first-element pivot), and the <em>three-way</em> partition defeats arrays of equal values (the O(n&sup2;) case for a two-way partition).",
                    "Recursing on the smaller side first bounds the stack at O(log n). Usually the fastest comparison sort in practice thanks to sequential memory access, but its worst case is only probabilistically avoided.",
                ],
                code='''def sort_array(nums):
    nums, rng = nums[:], random.Random(0)

    def qs(lo, hi):
        while lo < hi:
            pivot = nums[rng.randint(lo, hi)]
            lt, i, gt = lo, lo, hi            # < pivot | == pivot | unseen | > pivot
            while i <= gt:
                if nums[i] < pivot:
                    nums[lt], nums[i] = nums[i], nums[lt]; lt += 1; i += 1
                elif nums[i] > pivot:
                    nums[gt], nums[i] = nums[i], nums[gt]; gt -= 1
                else:
                    i += 1
            if lt - lo < hi - gt:              # recurse on the smaller side
                qs(lo, lt - 1); lo = gt + 1
            else:
                qs(gt + 1, hi); hi = lt - 1

    qs(0, len(nums) - 1)
    return nums''',
            ),
            dict(
                name="Counting sort over the value range",
                time="O(n + k)",
                space="O(k)",
                tag="non-comparison",
                why=[
                    "The constraints bound values to <code>[-5 &middot; 10<sup>4</sup>, 5 &middot; 10<sup>4</sup>]</code>, a range of k = 10<sup>5</sup>. Count occurrences of each value, then write them back in order. No comparisons at all, so the n log n lower bound for comparison sorts does not apply.",
                    "Only sensible when k is not much larger than n; for arbitrary integers, radix sort extends the idea digit by digit.",
                ],
                code='''def sort_array(nums):
    if not nums:
        return []
    lo = min(nums)
    counts = [0] * (max(nums) - lo + 1)
    for x in nums:
        counts[x - lo] += 1
    out = []
    for offset, c in enumerate(counts):
        out.extend([offset + lo] * c)
    return out''',
            ),
        ],
        tests='''assert sort_array([5, 2, 3, 1]) == [1, 2, 3, 5]
assert sort_array([5, 1, 1, 2, 0, 0]) == [0, 0, 1, 1, 2, 5]
assert sort_array([]) == [] and sort_array([1]) == [1]
rng = random.Random(8)
for _ in range(40):
    nums = [rng.randint(-50, 50) for _ in range(rng.randint(0, 40))]
    assert sort_array(nums) == sorted(nums)
assert sort_array([2] * 300) == [2] * 300''',
    ),

    # ------------------------------------------------------------------ 75
    dict(
        id="sort-colors",
        lc=75, slug="sort-colors",
        name="Sort Colors",
        difficulty="medium",
        framing=[
            "Sort an array of 0s, 1s and 2s in place, without the library sort. The follow-up asks for a single pass with O(1) space &mdash; Dijkstra's <strong>Dutch national flag</strong> partition, which is also the three-way partition inside good quicksorts.",
        ],
        approaches=[
            dict(
                name="Any comparison sort",
                time="O(n log n)",
                space="O(1)&ndash;O(n)",
                tag="ignores the structure",
                why=[
                    "Correct, but it throws away the fact that there are only three distinct values &mdash; which is exactly what lets the next two approaches run in linear time.",
                ],
                code='''def sort_colors(nums):
    nums.sort()''',
            ),
            dict(
                name="Count, then overwrite",
                time="O(n)",
                space="O(1)",
                why=[
                    "Count the 0s, 1s and 2s in one pass, then write that many of each in a second pass. Linear and constant space &mdash; counting sort with k = 3. It needs two passes, which the follow-up asks you to avoid.",
                ],
                code='''def sort_colors(nums):
    c = [0, 0, 0]
    for x in nums:
        c[x] += 1
    i = 0
    for color in range(3):
        for _ in range(c[color]):
            nums[i] = color
            i += 1''',
            ),
            dict(
                name="Dutch national flag, one pass",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Three pointers split the array into four regions: <code>[0, low)</code> is all 0s, <code>[low, mid)</code> all 1s, <code>[mid, high]</code> not yet seen, <code>(high, end)</code> all 2s. Look at <code>nums[mid]</code>: a 0 swaps to <code>low</code> (both advance), a 1 stays (only <code>mid</code> advances), a 2 swaps to <code>high</code> and <code>high</code> moves in.",
                    "After swapping with <code>high</code>, <code>mid</code> must <strong>not</strong> advance: the value that came back from the unseen region has not been examined yet. That one line is where most bugs are.",
                    "Each step shrinks the unseen region by one, so exactly n steps: one pass, O(1) space.",
                ],
                code='''def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1                            # do not advance mid: unseen value''',
            ),
        ],
        tests='''for nums in ([2, 0, 2, 1, 1, 0], [2, 0, 1], [0], [1, 1], [2, 2, 0, 0]):
    a = nums[:]
    sort_colors(a)
    assert a == sorted(nums)
rng = random.Random(9)
for _ in range(50):
    nums = [rng.randint(0, 2) for _ in range(rng.randint(1, 20))]
    a = nums[:]
    sort_colors(a)
    assert a == sorted(nums)''',
    ),

    # ------------------------------------------------------------------ 271
    dict(
        id="encode-decode-strings",
        lc=271, slug="encode-and-decode-strings",
        name="Encode and Decode Strings",
        difficulty="medium",
        tags=["Array", "String", "Design"],
        statement=[
            "Design an algorithm to encode a <strong>list of strings</strong> into a single string, and decode that string back into the original list. The strings may contain <em>any</em> characters &mdash; including whatever delimiter you might be tempted to use.",
            "Implement <code>encode(strs) -&gt; str</code> and <code>decode(s) -&gt; list</code> so that <code>decode(encode(strs)) == strs</code> for every input. You may not use serialization libraries such as <code>json</code> or <code>pickle</code>.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input='strs = ["neet","code","love","you"]', output='["neet","code","love","you"]'),
            dict(input='strs = ["", "#", "4#ab"]', output='["", "#", "4#ab"]',
                 explanation="Empty strings and strings that look like your own framing must survive the round trip."),
        ],
        constraints=[
            "<code>0 &lt;= strs.length &lt; 200</code>",
            "<code>0 &lt;= strs[i].length &lt; 200</code>; any of the 256 ASCII characters may appear",
        ],
        pitfall="Joining on a delimiter such as <code>\",\"</code> and splitting on it later. It works until a string contains the delimiter, and choosing a rarer one only moves the failure. It also cannot tell <code>[]</code> from <code>[\"\"]</code>. Any correct scheme must either escape the delimiter or make the decoder never look for one.",
        approaches=[
            dict(
                name="Escape the delimiter",
                time="O(n)",
                space="O(n)",
                why=[
                    "Double every occurrence of an escape character inside the strings and end each string with an escape-delimiter pair that can never appear in escaped text. Decoding reads character by character, undoing the escapes. Correct for any content, but the encoded size depends on how often the escape character appears, and decoding is a small state machine.",
                ],
                code='''def encode(strs):
    return "".join(s.replace("/", "//") + "/:" for s in strs)

def decode(s):
    out, cur, i = [], [], 0
    while i < len(s):
        if s[i] == "/":
            if s[i + 1] == "/":
                cur.append("/")
            else:                               # "/:" ends a string
                out.append("".join(cur))
                cur = []
            i += 2
        else:
            cur.append(s[i])
            i += 1
    return out''',
            ),
            dict(
                name="Length prefix",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Write each string as <code>length + \"#\" + string</code>. The decoder reads digits up to the first <code>#</code>, then takes exactly that many characters, <em>whatever they are</em> &mdash; a <code>#</code> or digits inside the string are never interpreted, because the decoder already knows where the string ends.",
                    "Overhead is a few characters per string, independent of content, and decoding never has to inspect the payload. This is how real wire formats (HTTP chunked encoding, Redis, protobuf) frame variable-length data.",
                ],
                code='''def encode(strs):
    return "".join(f"{len(s)}#{s}" for s in strs)

def decode(s):
    out, i = [], 0
    while i < len(s):
        j = s.index("#", i)
        length = int(s[i:j])
        out.append(s[j + 1:j + 1 + length])
        i = j + 1 + length
    return out''',
            ),
        ],
        tests='''for strs in (["neet", "code", "love", "you"], ["we", "say", ":", "yes"], [], [""], ["", ""], ["a/b", "//", "/:x"]):
    assert decode(encode(strs)) == strs, strs
for strs in (["", "#", "4#ab"], ["12#", "3", "#1#"], [chr(0), "x"], ["/", "/:", ":/"]):
    assert decode(encode(strs)) == strs, strs
rng = random.Random(17)
for _ in range(100):
    strs = ["".join(rng.choice("ab#/:0123") for _ in range(rng.randint(0, 6))) for _ in range(rng.randint(0, 5))]
    assert decode(encode(strs)) == strs, strs''',
    ),

    # ------------------------------------------------------------------ 304
    dict(
        id="range-sum-query-2d",
        lc=304, slug="range-sum-query-2d-immutable",
        name="Range Sum Query 2D - Immutable",
        difficulty="medium",
        framing=[
            "Answer many queries for the sum of a rectangle in a fixed matrix. The matrix never changes, so it is worth spending time up front to make every query cheap &mdash; the classic <strong>precompute</strong> trade.",
        ],
        approaches=[
            dict(
                name="Sum the rectangle per query",
                time="O(1) build, O(m &middot; n) per query",
                space="O(1)",
                tag="brute force",
                why=[
                    "Add up every cell in the rectangle each time. With 10<sup>4</sup> queries on a 200 &times; 200 matrix that is up to 4 &times; 10<sup>8</sup> additions.",
                ],
                code='''class NumMatrix:
    def __init__(self, matrix):
        self.m = matrix

    def sumRegion(self, r1, c1, r2, c2):
        return sum(sum(self.m[r][c1:c2 + 1]) for r in range(r1, r2 + 1))''',
            ),
            dict(
                name="Prefix sums per row",
                time="O(m &middot; n) build, O(m) per query",
                space="O(m &middot; n)",
                why=[
                    "Store running sums along each row. A row segment's sum is then one subtraction, and a rectangle needs one subtraction per row. A good intermediate step: it is the 1-D prefix-sum trick applied row by row.",
                ],
                code='''class NumMatrix:
    def __init__(self, matrix):
        self.rows = []
        for row in matrix:
            acc = [0]
            for v in row:
                acc.append(acc[-1] + v)
            self.rows.append(acc)

    def sumRegion(self, r1, c1, r2, c2):
        return sum(self.rows[r][c2 + 1] - self.rows[r][c1] for r in range(r1, r2 + 1))''',
            ),
            dict(
                name="2-D prefix sums",
                time="O(m &middot; n) build, O(1) per query",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "<code>P[r][c]</code> is the sum of the rectangle from the origin to cell <code>(r-1, c-1)</code>, with an extra zero row and column so no edge cases are needed. It builds in one pass: the cell, plus the rectangle above, plus the one to the left, minus their overlap counted twice.",
                    "A query uses the same inclusion&ndash;exclusion in reverse: the big rectangle, minus the strip above, minus the strip to the left, plus the corner that was subtracted twice. Four lookups, O(1).",
                ],
                code='''class NumMatrix:
    def __init__(self, matrix):
        m, n = len(matrix), len(matrix[0])
        P = [[0] * (n + 1) for _ in range(m + 1)]
        for r in range(m):
            for c in range(n):
                P[r + 1][c + 1] = matrix[r][c] + P[r][c + 1] + P[r + 1][c] - P[r][c]
        self.P = P

    def sumRegion(self, r1, c1, r2, c2):
        P = self.P
        return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]''',
            ),
        ],
        tests='''M = [[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]]
nm = NumMatrix(M)
assert [nm.sumRegion(2, 1, 4, 3), nm.sumRegion(1, 1, 2, 2), nm.sumRegion(1, 2, 2, 4)] == [8, 11, 12]
rng = random.Random(10)
for _ in range(10):
    m, n = rng.randint(1, 6), rng.randint(1, 6)
    M = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(m)]
    nm = NumMatrix(M)
    for _ in range(20):
        r1, r2 = sorted(rng.randint(0, m - 1) for _ in range(2))
        c1, c2 = sorted(rng.randint(0, n - 1) for _ in range(2))
        assert nm.sumRegion(r1, c1, r2, c2) == sum(M[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))''',
    ),

    # ------------------------------------------------------------------ 238
    dict(
        id="product-except-self",
        lc=238, slug="product-of-array-except-self",
        name="Product of Array Except Self",
        difficulty="medium",
        framing=[
            "Return <code>answer[i]</code> = the product of every element except <code>nums[i]</code>, in O(n) and <strong>without division</strong>. The follow-up asks for O(1) extra space, not counting the output array.",
            "The insight: the product of everything except i is (product of everything left of i) &times; (product of everything right of i).",
        ],
        approaches=[
            dict(
                name="Multiply everything else, per index",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "For each i, loop over all j &ne; i. Every product is recomputed from scratch; the prefix/suffix idea is exactly the sharing this misses.",
                ],
                code='''def product_except_self(nums):
    out = []
    for i in range(len(nums)):
        p = 1
        for j, x in enumerate(nums):
            if j != i:
                p *= x
        out.append(p)
    return out''',
            ),
            dict(
                name="Total product and division",
                time="O(n)",
                space="O(1)",
                tag="not allowed",
                why=[
                    "Divide the total product by each element. Forbidden by the problem, and worth explaining why it is fragile even when allowed: zeros need special handling (one zero makes every other answer 0; two make everything 0), and in fixed-width integers the total can overflow even when every answer fits.",
                ],
                code='''def product_except_self(nums):
    zeros = nums.count(0)
    total = 1
    for x in nums:
        if x:
            total *= x
    if zeros > 1:
        return [0] * len(nums)
    if zeros == 1:
        return [total if x == 0 else 0 for x in nums]
    return [total // x for x in nums]''',
            ),
            dict(
                name="Prefix and suffix product arrays",
                time="O(n)",
                space="O(n)",
                why=[
                    "<code>left[i]</code> is the product of everything before i, <code>right[i]</code> of everything after. Each is one pass, and the answer is their elementwise product. Three passes, O(n) time, two extra arrays.",
                ],
                code='''def product_except_self(nums):
    n = len(nums)
    left, right = [1] * n, [1] * n
    for i in range(1, n):
        left[i] = left[i - 1] * nums[i - 1]
    for i in range(n - 2, -1, -1):
        right[i] = right[i + 1] * nums[i + 1]
    return [a * b for a, b in zip(left, right)]''',
            ),
            dict(
                name="Output array plus a running suffix",
                time="O(n)",
                space="O(1) beyond the output",
                best=True,
                why=[
                    "Fill the output with prefix products directly, then sweep from the right carrying the suffix product in a single variable and multiply it in. The output array doubles as the prefix array, and the suffix array collapses to one number.",
                    "Two passes, O(1) extra space &mdash; the answer to the follow-up.",
                ],
                code='''def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    for i in range(1, n):
        out[i] = out[i - 1] * nums[i - 1]        # prefix products
    suffix = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suffix
        suffix *= nums[i]
    return out''',
            ),
        ],
        tests='''assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
assert product_except_self([0, 0, 2]) == [0, 0, 0]
rng = random.Random(11)
for _ in range(40):
    nums = [rng.randint(-3, 3) for _ in range(rng.randint(2, 10))]
    expect = []
    for i in range(len(nums)):
        p = 1
        for j, x in enumerate(nums):
            if j != i:
                p *= x
        expect.append(p)
    assert product_except_self(nums) == expect''',
    ),

    # ------------------------------------------------------------------ 36
    dict(
        id="valid-sudoku",
        lc=36, slug="valid-sudoku",
        name="Valid Sudoku",
        difficulty="medium",
        framing=[
            "Check that the filled cells of a 9 &times; 9 board break no rule: no digit repeats in a row, a column, or a 3 &times; 3 box. The board need not be solvable. The only real idea is mapping a cell to its box: <code>(r // 3, c // 3)</code>.",
            "The board size is fixed, so every approach is technically O(1); what differs is how many passes and how much bookkeeping.",
        ],
        approaches=[
            dict(
                name="Three separate passes",
                time="O(81 &times; 3)",
                space="O(9)",
                why=[
                    "Check each row with a set, then each column, then each box. Easy to get right because each pass is independent; it just reads the board three times.",
                ],
                code='''def is_valid_sudoku(board):
    def ok(cells):
        digits = [c for c in cells if c != "."]
        return len(digits) == len(set(digits))

    rows = all(ok(row) for row in board)
    cols = all(ok([board[r][c] for r in range(9)]) for c in range(9))
    boxes = all(ok([board[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)])
                for br in (0, 3, 6) for bc in (0, 3, 6))
    return rows and cols and boxes''',
            ),
            dict(
                name="One pass, 27 sets",
                time="O(81)",
                space="O(81)",
                best=True,
                why=[
                    "Keep a set per row, per column and per box. Each filled cell is checked against its three sets and added to them; any hit is a violation. A single pass over the board, returning at the first conflict.",
                ],
                code='''def is_valid_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d == ".":
                continue
            b = (r // 3) * 3 + c // 3
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                return False
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)
    return True''',
            ),
            dict(
                name="One pass, bitmasks",
                time="O(81)",
                space="O(27) integers",
                tag="least memory",
                why=[
                    "Replace each set with a 9-bit integer: bit d is set when digit d has been seen. Testing and adding are one AND and one OR. Same single pass, 27 small integers instead of 27 hash sets &mdash; the representation used in fast Sudoku solvers.",
                ],
                code='''def is_valid_sudoku(board):
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    for r in range(9):
        for c in range(9):
            if board[r][c] == ".":
                continue
            bit = 1 << int(board[r][c])
            b = (r // 3) * 3 + c // 3
            if (rows[r] | cols[c] | boxes[b]) & bit:
                return False
            rows[r] |= bit; cols[c] |= bit; boxes[b] |= bit
    return True''',
            ),
        ],
        tests='''B = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]
assert is_valid_sudoku(B) is True
bad = [row[:] for row in B]; bad[0][0] = "8"
assert is_valid_sudoku(bad) is False                # column clash with row 3
box = [row[:] for row in B]; box[1][1] = "9"
assert is_valid_sudoku(box) is False                # box clash only
assert is_valid_sudoku([["."] * 9 for _ in range(9)]) is True''',
    ),

    # ------------------------------------------------------------------ 128
    dict(
        id="longest-consecutive-sequence",
        lc=128, slug="longest-consecutive-sequence",
        name="Longest Consecutive Sequence",
        difficulty="medium",
        framing=[
            "Find the length of the longest run of consecutive integers present in an unsorted array, in O(n). Sorting solves it in O(n log n); the O(n) solution is a hash-set trick worth memorising: only start counting from the <em>beginning</em> of a run.",
        ],
        approaches=[
            dict(
                name="Count up from every element",
                time="O(n&sup2;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "For each value, keep checking <code>x + 1, x + 2, &hellip;</code> in a set. Every element of a run of length L restarts the count, so one run costs L + (L-1) + &hellip; = O(L&sup2;).",
                ],
                code='''def longest_consecutive(nums):
    present, best = set(nums), 0
    for x in nums:
        length = 1
        while x + length in present:
            length += 1
        best = max(best, length)
    return best''',
            ),
            dict(
                name="Sort and scan",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Sort, then walk counting runs: a step of exactly 1 extends the run, a repeated value is skipped (it neither extends nor breaks the run), anything else starts a new run.",
                    "Forgetting the duplicate case is the classic bug: <code>[1, 2, 2, 3]</code> is a run of 3.",
                ],
                code='''def longest_consecutive(nums):
    if not nums:
        return 0
    nums = sorted(nums)
    best = cur = 1
    for a, b in zip(nums, nums[1:]):
        if b == a + 1:
            cur += 1
            best = max(best, cur)
        elif b != a:
            cur = 1
    return best''',
            ),
            dict(
                name="Hash set, count only from run starts",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "A value starts a run exactly when <code>x - 1</code> is absent. Only from those values, count upward. Every other value is skipped in O(1).",
                    "Why O(n): each element is visited by the upward count at most once &mdash; by the single run start below it &mdash; and each element is checked once as a potential start. The nested loop looks quadratic and is linear in total, a standard amortised argument.",
                    "Iterate over the <em>set</em>, not the list, so that a value repeated a million times is not a million identical starts.",
                ],
                code='''def longest_consecutive(nums):
    present, best = set(nums), 0
    for x in present:
        if x - 1 not in present:               # x starts a run
            length = 1
            while x + length in present:
                length += 1
            best = max(best, length)
    return best''',
            ),
        ],
        tests='''assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
assert longest_consecutive([]) == 0
assert longest_consecutive([1, 2, 2, 3]) == 3
rng = random.Random(12)
for _ in range(50):
    nums = [rng.randint(-10, 10) for _ in range(rng.randint(0, 15))]
    s, best = set(nums), 0
    for x in s:
        k = 0
        while x + k in s:
            k += 1
        best = max(best, k)
    assert longest_consecutive(nums) == best''',
    ),

    # ------------------------------------------------------------------ 122
    dict(
        id="best-time-stock-ii",
        lc=122, slug="best-time-to-buy-and-sell-stock-ii",
        name="Best Time to Buy And Sell Stock II",
        difficulty="medium",
        framing=[
            "Buy and sell as many times as you like (holding at most one share) to maximise profit. The problem is a small dynamic programme with two states per day &mdash; holding or not &mdash; and it collapses to a one-line greedy once you see that every upward step can be captured.",
        ],
        approaches=[
            dict(
                name="Try every buy/sell decision",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "On each day, either act (buy if not holding, sell if holding) or do nothing, and take the better outcome. Correct, but the decision tree has 2<sup>n</sup> paths. It is the recurrence the DP below evaluates efficiently.",
                ],
                code='''def max_profit(prices):
    def best(day, holding):
        if day == len(prices):
            return 0
        skip = best(day + 1, holding)
        if holding:
            return max(skip, prices[day] + best(day + 1, False))
        return max(skip, -prices[day] + best(day + 1, True))

    return best(0, False)''',
            ),
            dict(
                name="DP over (day, holding)",
                time="O(n)",
                space="O(n)",
                why=[
                    "The recursion only ever asks about <code>(day, holding)</code> &mdash; 2n distinct states &mdash; so a table fills it bottom-up. <code>cash[i]</code> is the best profit at the end of day i holding nothing, <code>hold[i]</code> the best while holding a share.",
                ],
                code='''def max_profit(prices):
    n = len(prices)
    cash, hold = [0] * n, [0] * n
    hold[0] = -prices[0]
    for i in range(1, n):
        cash[i] = max(cash[i - 1], hold[i - 1] + prices[i])    # sell today, or not
        hold[i] = max(hold[i - 1], cash[i - 1] - prices[i])    # buy today, or not
    return cash[-1]''',
            ),
            dict(
                name="DP with two rolling variables",
                time="O(n)",
                space="O(1)",
                why=[
                    "Day i only reads day i - 1, so two variables replace the two arrays. This is the version that generalises to the cooldown and transaction-fee variants.",
                ],
                code='''def max_profit(prices):
    cash, hold = 0, -prices[0]
    for p in prices[1:]:
        cash, hold = max(cash, hold + p), max(hold, cash - p)
    return cash''',
            ),
            dict(
                name="Greedy: sum every rise",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Any profitable holding period from day a to day b equals the sum of the day-to-day changes in between. Taking <em>every</em> positive change &mdash; buying before each rise and selling after it &mdash; collects all the gains and none of the losses, and no strategy can do better, since each day's change is either captured or not.",
                    "One pass, O(1). The DP is still worth knowing: the greedy breaks as soon as a fee or cooldown is added.",
                ],
                code='''def max_profit(prices):
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))''',
            ),
        ],
        tests='''assert max_profit([7, 1, 5, 3, 6, 4]) == 7
assert max_profit([1, 2, 3, 4, 5]) == 4
assert max_profit([7, 6, 4, 3, 1]) == 0
assert max_profit([5]) == 0
rng = random.Random(13)
for _ in range(40):
    p = [rng.randint(0, 20) for _ in range(rng.randint(1, 12))]
    assert max_profit(p) == sum(max(0, b - a) for a, b in zip(p, p[1:]))''',
    ),

    # ------------------------------------------------------------------ 229
    dict(
        id="majority-element-ii",
        lc=229, slug="majority-element-ii",
        name="Majority Element II",
        difficulty="medium",
        framing=[
            "Return every element that appears more than n/3 times, in O(n) time and O(1) space. At most two such elements can exist (three would need more than n elements), which is exactly why Boyer-Moore voting extends to two candidates.",
        ],
        approaches=[
            dict(
                name="Hash map of counts",
                time="O(n)",
                space="O(n)",
                why=[
                    "Count everything, keep what exceeds n/3. Direct, linear time, linear memory.",
                ],
                code='''def majority_element_ii(nums):
    return [x for x, c in Counter(nums).items() if c > len(nums) // 3]''',
            ),
            dict(
                name="Sort and measure runs",
                time="O(n log n)",
                space="O(1) or O(n)",
                why=[
                    "After sorting, equal values form runs; any run longer than n/3 qualifies. Uses no hash map, at the cost of the sort.",
                ],
                code='''def majority_element_ii(nums):
    nums, out, i = sorted(nums), [], 0
    while i < len(nums):
        j = i
        while j < len(nums) and nums[j] == nums[i]:
            j += 1
        if j - i > len(nums) // 3:
            out.append(nums[i])
        i = j
    return out''',
            ),
            dict(
                name="Boyer-Moore with two candidates",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Keep two candidates with vote counts. A value matching either candidate votes for it; otherwise it fills an empty slot if there is one, and if not it cancels one vote from <em>each</em> candidate &mdash; removing three distinct values at once.",
                    "An element with more than n/3 occurrences cannot be wiped out by such triple cancellations, so every true answer survives as a candidate. The reverse is not guaranteed &mdash; a survivor may be a false positive &mdash; so a second pass counts the two candidates and keeps those above n/3.",
                ],
                code='''def majority_element_ii(nums):
    c1 = c2 = None
    v1 = v2 = 0
    for x in nums:
        if x == c1:
            v1 += 1
        elif x == c2:
            v2 += 1
        elif v1 == 0:
            c1, v1 = x, 1
        elif v2 == 0:
            c2, v2 = x, 1
        else:
            v1 -= 1                            # cancel three distinct values
            v2 -= 1
    return [c for c in {c1, c2} if c is not None and nums.count(c) > len(nums) // 3]''',
            ),
        ],
        tests='''assert sorted(majority_element_ii([3, 2, 3])) == [3]
assert sorted(majority_element_ii([1])) == [1]
assert sorted(majority_element_ii([1, 2])) == [1, 2]
rng = random.Random(14)
for _ in range(60):
    nums = [rng.randint(0, 4) for _ in range(rng.randint(1, 15))]
    assert sorted(majority_element_ii(nums)) == sorted(x for x, c in Counter(nums).items() if c > len(nums) // 3)''',
    ),

    # ------------------------------------------------------------------ 560
    dict(
        id="subarray-sum-equals-k",
        lc=560, slug="subarray-sum-equals-k",
        name="Subarray Sum Equals K",
        difficulty="medium",
        framing=[
            "Count the contiguous subarrays summing to <code>k</code>. Values can be <strong>negative</strong>, so a sliding window does not work &mdash; extending a window can decrease its sum. The fix is prefix sums plus a hash map, the most reusable trick on this page.",
        ],
        pitfall="Reaching for a sliding window. It assumes adding an element never decreases the sum, which fails with negatives.",
        approaches=[
            dict(
                name="Every subarray, summed from scratch",
                time="O(n&sup3;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "Enumerate every <code>(i, j)</code> and sum the slice. n&sup2;/2 subarrays, each summed in O(n).",
                ],
                code='''def subarray_sum(nums, k):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i, n) if sum(nums[i:j + 1]) == k)''',
            ),
            dict(
                name="Every start, running sum",
                time="O(n&sup2;)",
                space="O(1)",
                why=[
                    "Fix the start and extend the end one step at a time, keeping a running total. Removes the inner summation: O(n&sup2;).",
                ],
                code='''def subarray_sum(nums, k):
    count = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            count += total == k
    return count''',
            ),
            dict(
                name="Prefix sums and a hash map",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Let <code>P</code> be the running prefix sum. The subarray <code>(i, j]</code> sums to <code>P[j] - P[i]</code>, so a subarray ending at j sums to k exactly when an earlier prefix equals <code>P[j] - k</code>. A counter of prefixes seen so far answers \"how many?\" in O(1).",
                    "Seed the counter with <code>{0: 1}</code>: the empty prefix, so subarrays starting at index 0 are counted. This single seed is the most common bug.",
                    "One pass, O(n). The same idea solves Path Sum III on trees, and \"longest subarray with sum k\" if you store the <em>first index</em> of each prefix instead of a count.",
                ],
                code='''def subarray_sum(nums, k):
    seen = Counter({0: 1})                     # the empty prefix
    total = count = 0
    for x in nums:
        total += x
        count += seen[total - k]
        seen[total] += 1
    return count''',
            ),
        ],
        tests='''assert subarray_sum([1, 1, 1], 2) == 2
assert subarray_sum([1, 2, 3], 3) == 2
assert subarray_sum([1, -1, 0], 0) == 3
assert subarray_sum([3], 3) == 1
rng = random.Random(15)
for _ in range(50):
    nums = [rng.randint(-3, 3) for _ in range(rng.randint(1, 12))]
    k = rng.randint(-3, 3)
    brute = sum(1 for i in range(len(nums)) for j in range(i, len(nums)) if sum(nums[i:j + 1]) == k)
    assert subarray_sum(nums, k) == brute''',
    ),

    # ------------------------------------------------------------------ 41
    dict(
        id="first-missing-positive",
        lc=41, slug="first-missing-positive",
        name="First Missing Positive",
        difficulty="hard",
        framing=[
            "Return the smallest positive integer not in the array, in O(n) time and O(1) extra space. The key observation: for an array of length n, the answer is always in <code>1..n+1</code>. Values outside that range are irrelevant, and the array's own indices can serve as a presence table for the ones inside it.",
        ],
        approaches=[
            dict(
                name="Try 1, 2, 3, &hellip; with a linear search",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "Test each candidate from 1 upward with <code>in</code> on the list. At most n + 1 candidates, each an O(n) scan.",
                ],
                code='''def first_missing_positive(nums):
    x = 1
    while x in nums:
        x += 1
    return x''',
            ),
            dict(
                name="Sort, then walk",
                time="O(n log n)",
                space="O(1) or O(n)",
                why=[
                    "Sort, then scan the positives: the answer starts at 1 and increases each time the expected value is found. Duplicates and non-positives are skipped naturally.",
                ],
                code='''def first_missing_positive(nums):
    want = 1
    for x in sorted(nums):
        if x == want:
            want += 1
    return want''',
            ),
            dict(
                name="Hash set",
                time="O(n)",
                space="O(n)",
                why=[
                    "Put everything in a set and test 1, 2, &hellip; in O(1) each. Linear time, but linear memory, which the problem forbids.",
                ],
                code='''def first_missing_positive(nums):
    present = set(nums)
    x = 1
    while x in present:
        x += 1
    return x''',
            ),
            dict(
                name="Cyclic sort: put each value at its own index",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Value v belongs at index <code>v - 1</code>. Walk the array and keep swapping the current value into its home until the current slot holds either the right value, something out of range, or a duplicate of what is already home. Then the first index i with <code>nums[i] != i + 1</code> gives the answer i + 1; if there is none, it is n + 1.",
                    "The inner <code>while</code> looks quadratic, but every swap places one value in its final position, and a value in place is never moved again &mdash; so there are at most n swaps in total: O(n) time, and the only storage is the input itself.",
                    "An alternative with the same bounds marks presence by making <code>nums[v - 1]</code> negative after first replacing non-positives with n + 1. Both mutate the input; say so.",
                ],
                code='''def first_missing_positive(nums):
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]      # send nums[i] home
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1''',
            ),
        ],
        tests='''assert first_missing_positive([1, 2, 0]) == 3
assert first_missing_positive([3, 4, -1, 1]) == 2
assert first_missing_positive([7, 8, 9, 11, 12]) == 1
assert first_missing_positive([1, 1]) == 2
rng = random.Random(16)
for _ in range(60):
    nums = [rng.randint(-3, 8) for _ in range(rng.randint(1, 10))]
    s, x = set(nums), 1
    while x in s:
        x += 1
    assert first_missing_positive(nums[:]) == x''',
    ),
    ],
),
    ],
)
