"""Write-ups for the Two Pointers and Intervals topic (sorting)."""

EXPLAIN = {
    # ------------------------------------------------------------------ reverse string
    "reverse-string": {
        "example": {"setup": 's = list("hello")\nreverse_string(s)', "call": "s",
                    "expect": "['o', 'l', 'l', 'e', 'h']"},
        "approaches": {
            "Push onto a stack, pop back": {
                "idea": [
                    "A stack gives items back in the opposite order to the one they went in.",
                    "Push every character, then pop them back into the list from the front.",
                ],
                "steps": [
                    "<code>stack = list(s)</code>.",
                    "For each position i, <code>s[i] = stack.pop()</code>.",
                ],
                "why": [
                    "The last character is popped first and lands at index 0, and so on.",
                    "It is O(n) time, but the stack is a full copy: O(n) space, which the problem forbids.",
                ],
                "dry": [
                    "stack = [h, e, l, l, o].",
                    "Pops give o, l, l, e, h, written to indices 0..4.",
                    "s becomes <strong>['o', 'l', 'l', 'e', 'h']</strong>.",
                ],
            },
            "Recursive swap of the ends": {
                "idea": [
                    "Reversing means the first and last characters trade places, then the second and second-to-last, and so on.",
                    "Swap the two ends and recurse on the part in between.",
                ],
                "steps": [
                    "<code>go(lo, hi)</code>: if <code>lo &lt; hi</code>, swap and call <code>go(lo + 1, hi - 1)</code>.",
                ],
                "why": [
                    "Each call fixes the two outermost unsorted positions.",
                    "It copies no data, but n/2 stack frames are hidden O(n) space, and CPython's recursion limit breaks it on long inputs.",
                ],
                "dry": [
                    "go(0, 4): swap h and o, giving \"oellh\".",
                    "go(1, 3): swap e and l, giving \"olleh\".",
                    "go(2, 2): lo == hi, so stop. The result is <strong>['o', 'l', 'l', 'e', 'h']</strong>.",
                ],
            },
            "Two pointers, swap inward": {
                "idea": [
                    "The same swaps as the recursion, as a loop: one index at each end, moving towards each other.",
                    "Nothing is stored apart from the two indices.",
                ],
                "steps": [
                    "<code>lo, hi = 0, n - 1</code>.",
                    "While <code>lo &lt; hi</code>: swap, then <code>lo += 1</code> and <code>hi -= 1</code>.",
                ],
                "why": [
                    "After k swaps, the outer k characters on each side are in their final places.",
                    "It does n/2 swaps: O(n) time and O(1) space.",
                ],
                "dry": [
                    "lo = 0, hi = 4: swap h and o, giving \"oellh\".",
                    "lo = 1, hi = 3: swap e and l, giving \"olleh\".",
                    "lo = hi = 2, so stop. The result is <strong>['o', 'l', 'l', 'e', 'h']</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid palindrome
    "valid-palindrome": {
        "example": {"call": 'is_palindrome("Race, car!")', "expect": "True"},
        "approaches": {
            "Clean, then compare with the reverse": {
                "idea": [
                    "Throw away every non-alphanumeric character, lower-case the rest, and check whether the result reads the same backwards.",
                ],
                "steps": [
                    "<code>clean = [ch.lower() for ch in s if ch.isalnum()]</code>.",
                    "Return <code>clean == clean[::-1]</code>.",
                ],
                "why": [
                    "It applies the definition directly.",
                    "It is O(n) time, with two O(n) copies.",
                ],
                "dry": [
                    "clean = r, a, c, e, c, a, r.",
                    "Reversed, it is the same sequence, so the result is <strong>True</strong>.",
                ],
            },
            "Two pointers skipping non-alphanumerics": {
                "idea": [
                    "Compare from both ends at once, without building a cleaned copy.",
                    "Each pointer steps over characters that do not count (spaces, punctuation), and real characters are compared case-insensitively.",
                    "The first mismatch ends the scan.",
                ],
                "steps": [
                    "While <code>lo &lt; hi</code>: skip a non-alphanumeric character at lo or at hi.",
                    "Otherwise compare <code>s[lo].lower()</code> with <code>s[hi].lower()</code>; return <code>False</code> on a mismatch, or move both inward.",
                ],
                "why": [
                    "Each pair compared is exactly a pair the cleaned string would compare.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "lo = 0 is 'R', hi = 9 is '!', so skip it: hi = 8 is 'r'. R and r match.",
                    "a = a (indices 1, 7). c = c (indices 2, 6).",
                    "lo = 3 is 'e', and hi = 5 is ' ', so skip it; hi = 4 is ',', so skip it again; hi = 3.",
                    "lo == hi, so stop. The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid palindrome II
    "valid-palindrome-ii": {
        "example": {"call": 'valid_palindrome("abcbea")', "expect": "True"},
        "approaches": {
            "Try deleting each character": {
                "idea": [
                    "Check the string as it is, then every version with exactly one character removed.",
                ],
                "steps": [
                    "If s is a palindrome, return <code>True</code>.",
                    "For each i, build <code>s[:i] + s[i+1:]</code> and test it.",
                ],
                "why": [
                    "It covers every possible single deletion.",
                    "There are n + 1 checks of O(n) each: O(n²) time.",
                ],
                "dry": [
                    "\"abcbea\" is not a palindrome.",
                    "Deleting index 0, 1, 2 or 3 gives \"bcbea\", \"acbea\", \"abbea\", \"abcea\", none of them palindromes.",
                    "Deleting index 4 (e) gives \"abcba\", a palindrome, so the result is <strong>True</strong>.",
                ],
            },
            "Two pointers, branch once at the first mismatch": {
                "idea": [
                    "Walk inwards from both ends while the characters match; everything outside the pointers is then already paired up.",
                    "At the first mismatch, one of the two mismatched characters must be the one deleted.",
                    "So test whether the inside without the left one, or without the right one, is a palindrome. That is one branch, two linear checks.",
                ],
                "steps": [
                    "Move <code>lo</code> and <code>hi</code> inwards while <code>s[lo] == s[hi]</code>.",
                    "At a mismatch, return <code>pal(lo + 1, hi) or pal(lo, hi - 1)</code>.",
                    "If the pointers meet, the string is already a palindrome.",
                ],
                "why": [
                    "Deleting any character outside the mismatch would break pairs that already match.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "a = a (indices 0, 5).",
                    "b vs e (indices 1, 4): the first mismatch.",
                    "Deleting b: is s[2..4] = \"cbe\" a palindrome? No.",
                    "Deleting e: is s[1..3] = \"bcb\" a palindrome? Yes, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge strings alternately
    "merge-strings-alternately": {
        "example": {"call": 'merge_alternately("abcd", "pq")', "expect": '"apbqcd"'},
        "approaches": {
            "Two indices": {
                "idea": [
                    "Take one letter from each word in turn while both still have letters.",
                    "Then append whatever is left of the longer word.",
                ],
                "steps": [
                    "While <code>i</code> is within both words, append <code>word1[i]</code> and <code>word2[i]</code>.",
                    "Return the joined list plus <code>word1[i:]</code> plus <code>word2[i:]</code> (one of the two is empty).",
                ],
                "why": [
                    "Collecting into a list and joining once avoids building a new string on every step.",
                    "It is O(m + n) time and space.",
                ],
                "dry": [
                    "i=0: a, p. i=1: b, q.",
                    "i=2: \"pq\" is used up, so stop.",
                    "\"apbq\" + \"cd\" + \"\" = <strong>\"apbqcd\"</strong>.",
                ],
            },
            "zip_longest": {
                "idea": [
                    "<code>itertools.zip_longest</code> pairs the letters and pads the shorter word with empty strings, so the leftover tail needs no special case.",
                ],
                "steps": [
                    "<code>\"\".join(a + b for a, b in zip_longest(word1, word2, fillvalue=\"\"))</code>.",
                ],
                "why": [
                    "Each pair contributes its letters in order, and the padding contributes nothing.",
                    "It is O(m + n).",
                ],
                "dry": [
                    "Pairs: (a, p), (b, q), (c, \"\"), (d, \"\").",
                    "Joined: <strong>\"apbqcd\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge sorted array
    "merge-sorted-array": {
        "example": {"setup": "a = [1, 4, 7, 0, 0, 0]\nmerge(a, 3, [2, 5, 6], 3)", "call": "a", "expect": "[1, 2, 4, 5, 6, 7]"},
        "approaches": {
            "Copy in and sort": {
                "idea": [
                    "Put nums2's values into nums1's spare slots and sort, ignoring that both parts are already sorted.",
                ],
                "steps": [
                    "<code>nums1[m:] = nums2</code>.",
                    "<code>nums1.sort()</code>.",
                ],
                "why": [
                    "It is O((m + n) log(m + n)) in general. Timsort happens to merge two sorted runs in linear time, but that is the library's cleverness, not yours.",
                ],
                "dry": [
                    "After the copy: [1, 4, 7, 2, 5, 6].",
                    "After the sort: <strong>[1, 2, 4, 5, 6, 7]</strong>.",
                ],
            },
            "Copy nums1's values, merge forward": {
                "idea": [
                    "A normal front-to-back merge would overwrite nums1's own values before reading them.",
                    "So set those m values aside first, then merge them with nums2 into nums1 from the front.",
                ],
                "steps": [
                    "<code>first = nums1[:m]</code>.",
                    "Merge <code>first</code> and <code>nums2</code> into nums1, taking the smaller front value each time.",
                    "Copy any leftover tail.",
                ],
                "why": [
                    "Reading only from the copies means nothing unread is overwritten.",
                    "It is O(m + n) time and O(m) extra space.",
                ],
                "dry": [
                    "first = [1, 4, 7].",
                    "1 vs 2: take 1. 4 vs 2: take 2. 4 vs 5: take 4. 7 vs 5: take 5. 7 vs 6: take 6.",
                    "The leftover [7] is copied: <strong>[1, 2, 4, 5, 6, 7]</strong>.",
                ],
            },
            "Merge backwards into the free space": {
                "idea": [
                    "The free space is at the <em>end</em> of nums1, so fill it from the back with the largest values first.",
                    "Compare the largest remaining value of each array and write the bigger one at position k.",
                    "The write position never overtakes the read position in nums1, so nothing unread is overwritten, with no copy needed.",
                ],
                "steps": [
                    "<code>i = m - 1</code>, <code>j = n - 1</code>, <code>k = m + n - 1</code>.",
                    "While nums2 has values: write the larger of <code>nums1[i]</code> and <code>nums2[j]</code> at k.",
                    "When nums2 runs out, nums1's remaining values are already in place.",
                ],
                "why": [
                    "Each write puts the largest remaining value in its final position.",
                    "It is O(m + n) time and O(1) space.",
                ],
                "dry": [
                    "k=5: 7 vs 6, so write 7. k=4: 4 vs 6, so write 6.",
                    "k=3: 4 vs 5, so write 5. k=2: 4 vs 2, so write 4.",
                    "k=1: 1 vs 2, so write 2. nums2 is done, and the 1 is already at index 0.",
                    "The result is <strong>[1, 2, 4, 5, 6, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ remove duplicates
    "remove-duplicates-sorted": {
        "example": {"setup": "a = [0, 0, 1, 1, 1, 2, 2, 3]\nk = remove_duplicates(a)", "call": "a[:k]", "expect": "[0, 1, 2, 3]"},
        "approaches": {
            "Set, then sort back in": {
                "idea": [
                    "Collect the distinct values with a set, sort them back into order (a set does not keep order), and write them to the front.",
                ],
                "steps": [
                    "<code>uniq = sorted(set(nums))</code>.",
                    "Write <code>uniq</code> to the front of nums and return its length.",
                ],
                "why": [
                    "It works even on unsorted input, which this problem does not need.",
                    "It is O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "set gives {0, 1, 2, 3}, which sorts to [0, 1, 2, 3].",
                    "Written to the front, k = 4: <strong>[0, 1, 2, 3]</strong>.",
                ],
            },
            "Write pointer": {
                "idea": [
                    "<code>k</code> counts the distinct values kept so far, and <code>nums[k - 1]</code> is the last one kept.",
                    "Because the array is sorted, a repeat can only follow its twin, so comparing with the last kept value is enough.",
                    "Every new value is written at position k.",
                ],
                "steps": [
                    "<code>k = 1</code>, since the first value is always kept.",
                    "For each later x: if <code>x != nums[k - 1]</code>, write it at k and increment k.",
                    "Return k.",
                ],
                "why": [
                    "The prefix <code>nums[:k]</code> is always the distinct values seen so far, in order.",
                    "It is O(n) time and O(1) space. Comparing with <code>nums[k - 2]</code> instead allows each value twice.",
                ],
                "dry": [
                    "k = 1 with 0 kept. The next 0 equals 0, so skip it.",
                    "1 ≠ 0: write it at index 1, k = 2. The next two 1s are skipped.",
                    "2: write at index 2, k = 3. The next 2 is skipped. 3: write at index 3, k = 4.",
                    "a[:4] = <strong>[0, 1, 2, 3]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ two sum II
    "two-sum-ii": {
        "example": {"call": "two_sum_sorted([1, 3, 4, 6, 8, 11], 10)", "expect": "[3, 4]"},
        "approaches": {
            "Every pair": {
                "idea": [
                    "Try every pair i &lt; j and return the first whose sum hits the target.",
                ],
                "steps": [
                    "Two nested loops; return <code>[i + 1, j + 1]</code> (the indices are 1-based).",
                ],
                "why": [
                    "It is O(n²) time and O(1) space.",
                ],
                "dry": [
                    "1 pairs with nothing to make 10, and neither does 3.",
                    "4 + 6 = 10 at indices 2 and 3, so the result is <strong>[3, 4]</strong>.",
                ],
            },
            "Binary search for each complement": {
                "idea": [
                    "For each value x, the partner must be <code>target - x</code>, and the rest of the array is sorted, so binary-search for it.",
                ],
                "steps": [
                    "For each i, <code>j = bisect_left(numbers, target - x, i + 1)</code>.",
                    "If <code>numbers[j]</code> equals the complement, return the indices.",
                ],
                "why": [
                    "It uses sortedness, but each search starts from scratch: O(n log n).",
                ],
                "dry": [
                    "x = 1 looks for 9: not found. x = 3 looks for 7: not found.",
                    "x = 4 looks for 6: found at index 3.",
                    "The result is <strong>[3, 4]</strong>.",
                ],
            },
            "Two pointers from both ends": {
                "idea": [
                    "Start with the smallest and largest values.",
                    "If the sum is too small, the smallest value cannot pair with anything (its best partner, the largest, is not enough), so drop it. If the sum is too big, the largest cannot pair with anything, so drop it.",
                    "Each step removes one value for good, so at most n steps.",
                ],
                "steps": [
                    "<code>lo, hi = 0, n - 1</code>.",
                    "Equal: return. Too small: <code>lo += 1</code>. Too big: <code>hi -= 1</code>.",
                ],
                "why": [
                    "The elimination argument guarantees the answer pair is never skipped.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "1 + 11 = 12 &gt; 10: drop 11. 1 + 8 = 9 &lt; 10: drop 1.",
                    "3 + 8 = 11 &gt; 10: drop 8. 3 + 6 = 9 &lt; 10: drop 3.",
                    "4 + 6 = 10, a match, so the result is <strong>[3, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ 3Sum
    "three-sum": {
        "example": {"call": "sorted(sorted(t) for t in three_sum([-1, 0, 1, 2, -1, -4]))", "expect": "[[-1, -1, 2], [-1, 0, 1]]"},
        "approaches": {
            "Every triple, deduplicated with a set": {
                "idea": [
                    "Check every combination of three numbers.",
                    "Store each hit as a sorted tuple in a set, so the same triplet found via different indices counts once.",
                ],
                "steps": [
                    "For each 3-combination summing to 0, add <code>tuple(sorted(...))</code> to <code>found</code>.",
                ],
                "why": [
                    "It sees every triple: O(n³) time.",
                ],
                "dry": [
                    "(-1, 0, 1) appears twice, once with each -1.",
                    "(-1, 2, -1) gives the sorted tuple (-1, -1, 2).",
                    "The set holds two triplets: <strong>[[-1, -1, 2], [-1, 0, 1]]</strong>.",
                ],
            },
            "Fix one, hash set for the other two": {
                "idea": [
                    "Fix the first number; the other two must sum to its negative, which is Two Sum.",
                    "Solve that Two Sum in one pass over the later elements with a hash set of values seen.",
                ],
                "steps": [
                    "For each i, keep <code>seen</code> while scanning <code>nums[i+1:]</code>.",
                    "If <code>-nums[i] - x</code> was seen, record the sorted triplet.",
                ],
                "why": [
                    "It is O(n²) time, but duplicates still need a result set, and every i builds a hash set.",
                ],
                "dry": [
                    "i = 0 (-1): x = 1 finds 0 already seen, giving (-1, 0, 1); x = -1 finds 2 seen, giving (-1, -1, 2).",
                    "Later values of i find the same triplets again, and the set drops the repeats.",
                    "The result is <strong>[[-1, -1, 2], [-1, 0, 1]]</strong>.",
                ],
            },
            "Sort, fix one, two pointers, skip duplicates": {
                "idea": [
                    "Sort the array. Fix <code>nums[i]</code>, then find pairs in the rest summing to <code>-nums[i]</code> with two pointers, as in Two Sum II.",
                    "Duplicates are avoided by skipping: skip an i equal to the previous one, and after a hit, move <code>lo</code> past equal values.",
                    "Once <code>nums[i] &gt; 0</code>, everything after it is positive too, so stop.",
                ],
                "steps": [
                    "Sort the array.",
                    "For each i: skip repeats, then move lo and hi inwards according to the sum's sign.",
                    "On a hit, record it and skip equal neighbours.",
                ],
                "why": [
                    "Each distinct triplet is produced exactly once.",
                    "There are n two-pointer scans of O(n): O(n²) time and O(1) extra space.",
                ],
                "dry": [
                    "Sorted: [-4, -1, -1, 0, 1, 2].",
                    "i = 0 (-4) needs a pair summing to 4; the largest pair is 1 + 2 = 3, so nothing.",
                    "i = 1 (-1): -1 + 2 = 1 hits, giving [-1, -1, 2]. Then 0 + 1 = 1 hits, giving [-1, 0, 1].",
                    "i = 2 (-1) is the same value as before, so skip it. i = 3 (0): 1 + 2 &gt; 0 and nothing fits.",
                    "The result is <strong>[[-1, -1, 2], [-1, 0, 1]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ 4Sum
    "four-sum": {
        "example": {"call": "sorted(sorted(q) for q in four_sum([1, 0, -1, 0, -2, 2], 0))",
                    "expect": "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"},
        "approaches": {
            "Every quadruple": {
                "idea": [
                    "Check every combination of four numbers and keep the distinct sorted ones that hit the target.",
                ],
                "steps": [
                    "Set comprehension over <code>combinations(nums, 4)</code>.",
                ],
                "why": [
                    "It is O(n⁴).",
                ],
                "dry": [
                    "Of the 15 combinations, the matching ones are {-2, -1, 1, 2}, {-2, 0, 0, 2} and {-1, 0, 0, 1}.",
                    "The result is <strong>[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]</strong>.",
                ],
            },
            "Two fixed loops plus two pointers": {
                "idea": [
                    "Sort, then fix the first two numbers with nested loops, skipping repeated values at each level.",
                    "The last two come from a two-pointer scan of the remainder.",
                ],
                "steps": [
                    "Sort. Loop i, then j &gt; i, each skipping duplicates.",
                    "Run two pointers on <code>j+1 .. n-1</code> for <code>target - nums[i] - nums[j]</code>.",
                ],
                "why": [
                    "This is 3Sum with one more fixed level: O(n³) time and O(1) extra space.",
                ],
                "dry": [
                    "Sorted: [-2, -1, 0, 0, 1, 2].",
                    "i = -2, j = -1: a pair summing to 3 is 1 + 2, giving [-2, -1, 1, 2].",
                    "i = -2, j = 0: a pair summing to 2 is 0 + 2, giving [-2, 0, 0, 2]. The second 0 as j is skipped.",
                    "i = -1, j = 0: a pair summing to 1 is 0 + 1, giving [-1, 0, 0, 1].",
                    "Sorted, the result is <strong>[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]</strong>.",
                ],
            },
            "General k-Sum recursion": {
                "idea": [
                    "<code>k_sum(start, k, target)</code> fixes one number (skipping duplicates) and asks for <code>k - 1</code> numbers summing to the rest.",
                    "At k = 2 it switches to two pointers, so one function solves 2Sum, 3Sum, 4Sum and beyond.",
                    "Early exits help: if the smallest possible sum of k numbers from here is already too big, or the largest is too small, return immediately.",
                ],
                "steps": [
                    "Base checks: an empty range or an impossible bound returns [].",
                    "k = 2: two pointers, skipping repeated left values.",
                    "Otherwise, for each distinct <code>nums[i]</code>, prefix it to every result of <code>k_sum(i + 1, k - 1, target - nums[i])</code>.",
                ],
                "why": [
                    "It finds the same quadruplets with the same duplicate skipping, and costs O(n<sup>k-1</sup>).",
                ],
                "dry": [
                    "k_sum(0, 4, 0) fixes -2 and calls k_sum(1, 3, 2).",
                    "That fixes -1 and asks for 2 numbers summing to 3 (1 + 2); it fixes 0 and asks for 2 numbers summing to 2 (0 + 2).",
                    "Back at the top, fixing -1 leads to [0, 0, 1].",
                    "The result is <strong>[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotate array
    "rotate-array": {
        "example": {"setup": "a = [1, 2, 3, 4, 5, 6, 7]\nrotate(a, 3)", "call": "a", "expect": "[5, 6, 7, 1, 2, 3, 4]"},
        "approaches": {
            "Rotate by one, k times": {
                "idea": [
                    "Rotating right by one moves the last element to the front and shifts everything else along.",
                    "Do that k times.",
                ],
                "steps": [
                    "Repeat <code>k % n</code> times: save the last element, shift every element one place right, put the saved one at index 0.",
                ],
                "why": [
                    "It is in place, but O(n·k) time.",
                ],
                "dry": [
                    "Once: [7, 1, 2, 3, 4, 5, 6].",
                    "Twice: [6, 7, 1, 2, 3, 4, 5].",
                    "Three times: <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                ],
            },
            "Extra array": {
                "idea": [
                    "Element i ends up at <code>(i + k) % n</code>; write everything into a copy, then copy back.",
                ],
                "steps": [
                    "<code>out[(i + k) % n] = nums[i]</code>.",
                    "<code>nums[:] = out</code>.",
                ],
                "why": [
                    "It is O(n) time with an O(n) buffer.",
                ],
                "dry": [
                    "1 goes to index 3, 2 to index 4, 3 to 5, 4 to 6.",
                    "5 goes to index 0, 6 to 1, 7 to 2.",
                    "The result is <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                ],
            },
            "Three reversals": {
                "idea": [
                    "Reversing the whole array moves the last k elements to the front, but in reverse order, and the rest to the back, also reversed.",
                    "Reversing each of those two blocks again fixes their internal order.",
                ],
                "steps": [
                    "<code>k %= n</code>.",
                    "Reverse <code>[0, n)</code>, then <code>[0, k)</code>, then <code>[k, n)</code>.",
                ],
                "why": [
                    "Each element is swapped at most twice: O(n) time and O(1) space, and it is easy to get right.",
                ],
                "dry": [
                    "Reverse everything: [7, 6, 5, 4, 3, 2, 1].",
                    "Reverse the first 3: [5, 6, 7, 4, 3, 2, 1].",
                    "Reverse the rest: <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                ],
            },
            "Cyclic replacements": {
                "idea": [
                    "Pick up the element at a start index, put it at its destination, pick up the element that was there, and keep going until you return to the start.",
                    "There are gcd(n, k) such cycles. Counting the moves tells you when all n elements are placed.",
                ],
                "steps": [
                    "From <code>start</code>, repeatedly swap the carried value into <code>(i + k) % n</code>.",
                    "When the cycle closes, move to <code>start + 1</code>; stop after n moves.",
                ],
                "why": [
                    "Every element is written exactly once, the fewest writes possible, though the cycle logic is easier to get wrong.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "gcd(7, 3) = 1, so there is a single cycle starting at index 0.",
                    "Carry 1 to index 3; carry 4 to index 6; carry 7 to index 2; carry 3 to index 5.",
                    "Carry 6 to index 1; carry 2 to index 4; carry 5 to index 0, which closes the cycle after 7 moves.",
                    "The result is <strong>[5, 6, 7, 1, 2, 3, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ container with most water
    "container-most-water": {
        "example": {"call": "max_area([1, 8, 6, 2, 5, 4, 8, 3, 7])", "expect": "49"},
        "approaches": {
            "Every pair": {
                "idea": [
                    "Any two lines form a container holding <code>width × the shorter line's height</code>.",
                    "Try every pair and keep the largest.",
                ],
                "steps": [
                    "For each pair i &lt; j: <code>(j - i) · min(h[i], h[j])</code>.",
                ],
                "why": [
                    "It is O(n²) time.",
                ],
                "dry": [
                    "The best pair is index 1 (height 8) with index 8 (height 7): width 7 × height 7.",
                    "The result is <strong>49</strong>.",
                ],
            },
            "Two pointers, move the shorter side": {
                "idea": [
                    "Start with the widest container, using the two outermost lines.",
                    "Its height is set by the shorter line. Every other container using that shorter line is narrower and no taller, so it can never beat this one.",
                    "So the shorter line has already given its best: discard it and move that pointer inwards.",
                ],
                "steps": [
                    "Record <code>(hi - lo) · min(h[lo], h[hi])</code>.",
                    "Move whichever pointer has the shorter line.",
                ],
                "why": [
                    "Each step discards one line with proof, so no possible winner is skipped.",
                    "It takes n - 1 steps: O(n) time and O(1) space.",
                ],
                "dry": [
                    "lo = 0 (1), hi = 8 (7): area 8. Height 1 is shorter, so move lo.",
                    "lo = 1 (8), hi = 8 (7): area 7 × 7 = <strong>49</strong>. Height 7 is shorter, so move hi.",
                    "hi = 7 (3): 18. hi = 6 (8): 5 × 8 = 40. Heights tie, so hi moves.",
                    "The remaining containers are narrower: 16, 15, 4, 6.",
                    "The best is <strong>49</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ boats to save people
    "boats-to-save-people": {
        "example": {"call": "num_rescue_boats([3, 2, 2, 1], 3)", "expect": "3"},
        "approaches": {
            "Sort, pair heaviest with lightest": {
                "idea": [
                    "The heaviest remaining person needs a boat no matter what.",
                    "Pair them with the lightest remaining person if the two fit; if even the lightest does not fit, nobody does, so they ride alone.",
                    "Pairing with the lightest is never worse, because anyone else who could share with the heaviest is at least as heavy.",
                ],
                "steps": [
                    "Sort the weights. <code>lo</code> points at the lightest and <code>hi</code> at the heaviest.",
                    "If <code>people[lo] + people[hi] &lt;= limit</code>, then <code>lo += 1</code> as well.",
                    "Always <code>hi -= 1</code> and <code>boats += 1</code>.",
                ],
                "why": [
                    "Each boat removes one or two people from the ends: O(n) after an O(n log n) sort.",
                ],
                "dry": [
                    "Sorted: [1, 2, 2, 3].",
                    "3 + 1 = 4 &gt; 3, so 3 rides alone. boats = 1.",
                    "2 + 1 = 3 ≤ 3, so they share. boats = 2.",
                    "The other 2 is left alone. boats = <strong>3</strong>.",
                ],
            },
            "Counting sort, then the same greedy": {
                "idea": [
                    "Weights are at most <code>limit</code>, so counting sort replaces the comparison sort.",
                    "Then run exactly the same two-pointer greedy.",
                ],
                "steps": [
                    "Count each weight, then expand the counts into a sorted list.",
                    "Run the heaviest-plus-lightest greedy.",
                ],
                "why": [
                    "It is O(n + limit) time and O(limit) space.",
                ],
                "dry": [
                    "Counts: 1:1, 2:2, 3:1, which expand to [1, 2, 2, 3].",
                    "The greedy gives boats {3}, {2, 1}, {2}, so the result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ trapping rain water
    "trapping-rain-water": {
        "example": {"call": "trap([4, 2, 0, 3, 2, 5])", "expect": "9"},
        "approaches": {
            "Scan left and right from every bar": {
                "idea": [
                    "Water above bar i rises to the lower of the tallest bar on its left and the tallest on its right.",
                    "So the water at i is <code>min(left max, right max) - height[i]</code>; compute both maxima by scanning.",
                ],
                "steps": [
                    "For each i: <code>left = max(height[:i+1])</code>, <code>right = max(height[i:])</code>.",
                    "Add <code>min(left, right) - height[i]</code>.",
                ],
                "why": [
                    "It applies the formula directly, recomputing every maximum: O(n²) time.",
                ],
                "dry": [
                    "Bar 1 (2): the left max is 4 and the right max is 5, so 4 - 2 = 2.",
                    "Bar 2 (0): 4 - 0 = 4. Bar 3 (3): 4 - 3 = 1. Bar 4 (2): 4 - 2 = 2.",
                    "The end bars hold nothing. The total is <strong>9</strong>.",
                ],
            },
            "Prefix and suffix maximum arrays": {
                "idea": [
                    "The maxima to the left and right of each bar can be computed once, in two passes.",
                    "Then apply the formula with O(1) per bar.",
                ],
                "steps": [
                    "<code>left[i] = max(height[i], left[i-1])</code>, going left to right.",
                    "<code>right[i] = max(height[i], right[i+1])</code>, going right to left.",
                    "Sum <code>min(left[i], right[i]) - height[i]</code>.",
                ],
                "why": [
                    "Three linear passes: O(n) time and O(n) space.",
                ],
                "dry": [
                    "left = [4, 4, 4, 4, 4, 5]; right = [5, 5, 5, 5, 5, 5].",
                    "The water per bar is 0, 2, 4, 1, 2, 0.",
                    "The total is <strong>9</strong>.",
                ],
            },
            "Monotonic stack, fill layer by layer": {
                "idea": [
                    "Keep a stack of indices whose heights decrease from bottom to top: bars still waiting for a taller bar on their right.",
                    "When a taller bar arrives, it closes a basin. Pop the bottom of the basin; the water above it is bounded by the new bar and the bar now on top of the stack.",
                    "This counts water in horizontal layers rather than per column.",
                ],
                "steps": [
                    "While the top bar is lower than the current bar: pop it as <code>bottom</code>; if the stack is now empty, stop.",
                    "<code>depth = min(height[left], h) - height[bottom]</code>, <code>width = i - left - 1</code>; add depth × width.",
                    "Push i.",
                ],
                "why": [
                    "Each layer is counted once, when its right wall appears.",
                    "Each index is pushed and popped once: O(n) time and O(n) space.",
                ],
                "dry": [
                    "Push bars 0 (4), 1 (2), 2 (0).",
                    "Bar 3 (3): pop 2 (0) between 2 and 3, a layer of depth 2 and width 1, giving +2. Pop 1 (2) between 4 and 3, depth 1 and width 2, giving +2. The total is 4.",
                    "Push 3, then 4 (2).",
                    "Bar 5 (5): pop 4 between 3 and 5, depth 1 and width 1, giving +1. Pop 3 between 4 and 5, depth 1 and width 4, giving +4.",
                    "The total is <strong>9</strong>.",
                ],
            },
            "Two pointers with running maxima": {
                "idea": [
                    "Move inwards from both ends, tracking <code>left_max</code> and <code>right_max</code> seen so far.",
                    "If <code>left_max &lt; right_max</code>, the water at the left pointer is set by left_max alone: somewhere on its right there is a bar at least as tall as right_max, so the right side cannot be the limit.",
                    "Settle that position and move on; the same argument works on the right.",
                ],
                "steps": [
                    "Update both maxima with the current bars.",
                    "On the side with the smaller maximum, add <code>max - height</code> and move that pointer.",
                ],
                "why": [
                    "Each position is settled using a bound that is already certain.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "left_max = 4 &lt; right_max = 5, so the left side settles: bar 0 adds 0, bar 1 adds 2, bar 2 adds 4.",
                    "Bar 3 adds 4 - 3 = 1, and bar 4 adds 4 - 2 = 2.",
                    "The pointers meet at the 5.",
                    "The total is <strong>9</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ insert interval
    "insert-interval": {
        "example": {"call": "insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])", "expect": "[[1, 2], [3, 10], [12, 16]]"},
        "approaches": {
            "Append, then Merge Intervals": {
                "idea": [
                    "Add the new interval to the list and run the standard merge: sort by start, then extend or start groups.",
                ],
                "steps": [
                    "Sort <code>intervals + [new]</code>.",
                    "Merge overlapping neighbours.",
                ],
                "why": [
                    "It is correct, but it re-sorts a list that was already sorted: O(n log n).",
                ],
                "dry": [
                    "Sorted: [1, 2], [3, 5], [4, 8], [6, 7], [8, 10], [12, 16].",
                    "[1, 2] stays. [3, 5] absorbs [4, 8], [6, 7] and [8, 10], becoming [3, 10].",
                    "[12, 16] stays. The result is <strong>[[1, 2], [3, 10], [12, 16]]</strong>.",
                ],
            },
            "Three-phase linear scan": {
                "idea": [
                    "Intervals fall into three groups: those that end before the new one starts, those that overlap it, and those that start after it ends.",
                    "Copy the first group, merge the second group into the new interval (stretching its start and end), then copy the third.",
                ],
                "steps": [
                    "Copy while <code>end &lt; start</code>.",
                    "Absorb while <code>interval start &lt;= end</code>, updating start and end with min and max.",
                    "Append the merged interval, then the rest.",
                ],
                "why": [
                    "One pass, and the output may have n + 1 intervals, so O(n) is optimal.",
                ],
                "dry": [
                    "Before: [1, 2] ends at 2 &lt; 4, so copy it. [3, 5] ends at 5 ≥ 4, so stop copying.",
                    "Overlapping: [3, 5] gives [3, 8]; [6, 7] is inside; [8, 10] starts at 8 ≤ 8, giving [3, 10]. [12, 16] starts after 10, so stop.",
                    "Append [3, 10], then [12, 16].",
                    "The result is <strong>[[1, 2], [3, 10], [12, 16]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge intervals
    "merge-intervals": {
        "example": {"call": "merge([[1, 3], [8, 10], [2, 6], [9, 9], [15, 18]])", "expect": "[[1, 6], [8, 10], [15, 18]]"},
        "approaches": {
            "Overlap graph, connected components": {
                "idea": [
                    "Treat each interval as a node and connect every pair that overlaps.",
                    "Each connected component merges into one interval: the minimum start to the maximum end.",
                ],
                "steps": [
                    "Build the adjacency list over all pairs.",
                    "DFS each unvisited interval, tracking the min start and max end.",
                ],
                "why": [
                    "It needs no sorting and shows what merging means, but builds O(n²) edges.",
                ],
                "dry": [
                    "Edges: [1, 3]–[2, 6] and [8, 10]–[9, 9].",
                    "The components are {[1, 3], [2, 6]}, which becomes [1, 6]; {[8, 10], [9, 9]}, which becomes [8, 10]; and {[15, 18]}.",
                    "Sorted: <strong>[[1, 6], [8, 10], [15, 18]]</strong>.",
                ],
            },
            "Sort by start, extend the last group": {
                "idea": [
                    "After sorting by start, overlapping intervals sit next to each other.",
                    "If an interval starts at or before the end of the last merged group, it belongs to that group: extend its end, using <code>max</code> because the interval may be entirely inside.",
                    "Otherwise it starts a new group.",
                ],
                "steps": [
                    "Sort the intervals.",
                    "For each: extend the last group with <code>max</code>, or append a new group.",
                ],
                "why": [
                    "Sorting guarantees nothing earlier can overlap a later group.",
                    "Sorting dominates: O(n log n).",
                ],
                "dry": [
                    "Sorted: [1, 3], [2, 6], [8, 10], [9, 9], [15, 18].",
                    "[2, 6] starts at 2 ≤ 3, giving [1, 6]. [8, 10] starts a new group.",
                    "[9, 9] starts at 9 ≤ 10; max(10, 9) keeps it [8, 10]. Without max it would shrink to [8, 9].",
                    "[15, 18] is a new group. The result is <strong>[[1, 6], [8, 10], [15, 18]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ non-overlapping intervals
    "non-overlapping-intervals": {
        "example": {"call": "erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]])", "expect": "1"},
        "approaches": {
            "DP: longest chain of compatible intervals": {
                "idea": [
                    "Removing as few intervals as possible is the same as keeping as many non-overlapping ones as possible.",
                    "After sorting by start, <code>keep[i]</code> is the largest chain ending with interval i: one more than the best chain ending before i starts.",
                ],
                "steps": [
                    "Sort by start.",
                    "<code>keep[i] = 1 + max(keep[j])</code> over j with <code>end[j] ≤ start[i]</code>.",
                    "Return <code>n - max(keep)</code>.",
                ],
                "why": [
                    "It has the same shape as the longest increasing subsequence DP: correct, but O(n²).",
                ],
                "dry": [
                    "Sorted: [1, 2], [1, 3], [2, 3], [3, 4].",
                    "keep = [1, 1, 2, 3]: [2, 3] follows [1, 2], and [3, 4] follows [2, 3].",
                    "4 - 3 = <strong>1</strong> removal.",
                ],
            },
            "Greedy: sort by end, keep the earliest-ending": {
                "idea": [
                    "To fit the most intervals, always keep the one that frees up time soonest: the earliest end.",
                    "Sort by end, keep an interval whenever it starts at or after the last kept end, and remove the rest.",
                    "Exchange argument: swapping any optimal first choice for the earliest-ending interval keeps the selection valid and the same size.",
                ],
                "steps": [
                    "Sort by end.",
                    "If <code>start &gt;= end_of_last_kept</code>, keep it and update the end; otherwise count a removal.",
                ],
                "why": [
                    "The greedy choice is always safe, and repeating the argument covers the rest.",
                    "It is O(n log n) for the sort.",
                ],
                "dry": [
                    "By end: [1, 2], [2, 3], [1, 3], [3, 4].",
                    "Keep [1, 2] (end 2). [2, 3] starts at 2 ≥ 2, so keep it (end 3).",
                    "[1, 3] starts at 1 &lt; 3, so remove it. [3, 4] starts at 3 ≥ 3, so keep it.",
                    "Removed: <strong>1</strong>.",
                ],
            },
            "Greedy by start, drop the longer-ending one": {
                "idea": [
                    "The same principle in start order: whenever two intervals overlap, remove whichever ends later and keep the smaller end.",
                ],
                "steps": [
                    "Sort by start; <code>end</code> is the first interval's end.",
                    "If the next start is before <code>end</code>, count a removal and set <code>end = min(end, e)</code>; otherwise <code>end = e</code>.",
                ],
                "why": [
                    "Keeping the earlier end leaves the most room, the same as the end-sorted greedy.",
                    "It is O(n log n).",
                ],
                "dry": [
                    "Sorted: [1, 2], [1, 3], [2, 3], [3, 4]. end = 2.",
                    "[1, 3] starts at 1 &lt; 2: remove one, and end = min(2, 3) = 2.",
                    "[2, 3]: no overlap, so end = 3. [3, 4]: no overlap.",
                    "Removed: <strong>1</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ meeting rooms III
    "meeting-rooms-iii": {
        "example": {"call": "most_booked(2, [[0, 10], [1, 5], [2, 7], [3, 4]])", "expect": "0"},
        "approaches": {
            "Simulate by scanning all rooms": {
                "idea": [
                    "Process meetings in start order, tracking when each room becomes free.",
                    "Use the lowest-numbered free room. If none is free, wait for the room that frees up first and delay the meeting by that wait, keeping its length.",
                ],
                "steps": [
                    "Find the lowest room with <code>free_at[r] ≤ start</code>.",
                    "If there is none, take the room minimising <code>(free_at, number)</code> and shift the meeting's end by the delay.",
                    "Update that room's free time and its count; at the end, return the room with the highest count.",
                ],
                "why": [
                    "It follows the rules literally.",
                    "It is O(n) per meeting: O(m log m + m·n).",
                ],
                "dry": [
                    "[0, 10]: room 0 (free until 10). [1, 5]: room 1 (free until 5).",
                    "[2, 7]: no room is free; room 1 frees first at 5, so the meeting runs [5, 10). Room 1 has 2 meetings.",
                    "[3, 4]: both rooms are busy until 10; the tie goes to room 0, so the meeting runs [10, 11). Room 0 has 2 meetings.",
                    "The counts tie at [2, 2], so the lowest number wins: <strong>0</strong>.",
                ],
            },
            "Two heaps: free rooms and busy rooms": {
                "idea": [
                    "A min-heap of free room numbers gives the lowest free room in O(log n).",
                    "A min-heap of <code>(end time, room)</code> gives the room that frees up first, with ties broken by room number automatically.",
                    "Before each meeting, move every room that has finished by its start from busy to free.",
                ],
                "steps": [
                    "Release finished rooms: <code>busy[0][0] &lt;= start</code>.",
                    "If a room is free, pop the lowest and push <code>(end, room)</code> onto busy.",
                    "Otherwise pop the earliest busy room and push it back with the delayed end <code>finish + (end - start)</code>.",
                ],
                "why": [
                    "Each meeting does O(1) heap operations: O(m log m + m log n) overall.",
                ],
                "dry": [
                    "[0, 10]: free [0, 1], so take room 0; busy holds (10, 0).",
                    "[1, 5]: nothing has finished; take room 1; busy holds (5, 1) and (10, 0).",
                    "[2, 7]: no free room; pop (5, 1) and push (10, 1). Room 1 has 2 meetings.",
                    "[3, 4]: no free room; pop (10, 0), which beats (10, 1) on room number, and push (11, 0). Room 0 has 2 meetings.",
                    "The tie goes to the smaller room: <strong>0</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ min interval for each query
    "min-interval-each-query": {
        "example": {"call": "min_interval([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5])", "expect": "[3, 3, 1, 4]"},
        "approaches": {
            "Check every interval per query": {
                "idea": [
                    "For each query, look at every interval containing it and take the smallest size (<code>r - l + 1</code>).",
                ],
                "steps": [
                    "Collect the sizes of the intervals with <code>l ≤ q ≤ r</code>; take the minimum, or -1.",
                ],
                "why": [
                    "It is the correctness reference: O(n·q) time.",
                ],
                "dry": [
                    "q=2: [1, 4] has size 4 and [2, 4] has size 3, so 3.",
                    "q=3: sizes 4, 3, 4, so 3. q=4: sizes 4, 3, 4, 1, so 1.",
                    "q=5: only [3, 6] (size 4), so 4.",
                    "The result is <strong>[3, 3, 1, 4]</strong>.",
                ],
            },
            "Offline sweep with a min-heap": {
                "idea": [
                    "Answer the queries in increasing order (remembering their original positions).",
                    "As the query value grows, push every interval that has started onto a min-heap keyed by (size, right end).",
                    "Pop from the top any interval that has already ended. It ended before every later query too, so dropping it is safe. The top is then the smallest interval containing q.",
                ],
                "steps": [
                    "Sort the intervals by left end, and the queries by value.",
                    "For each query: push the intervals with <code>left ≤ q</code>; pop the top while <code>right &lt; q</code>.",
                    "Record the top's size at the query's original position.",
                ],
                "why": [
                    "Every interval is pushed and popped at most once: O(n log n + q log q).",
                ],
                "dry": [
                    "q=2: push [1, 4] (size 4) and [2, 4] (size 3). The top is size 3, so 3.",
                    "q=3: push [3, 6] (size 4). The top is still 3.",
                    "q=4: push [4, 4] (size 1). The top is 1.",
                    "q=5: [4, 4], [2, 4] and [1, 4] have ended and are popped; the top is [3, 6], size 4.",
                    "The result is <strong>[3, 3, 1, 4]</strong>.",
                ],
            },
        },
    },
}
