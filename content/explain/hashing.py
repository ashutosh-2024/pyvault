"""Write-ups for the Arrays and Hashing topic."""

SUDOKU = ('B = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],'
          '["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],'
          '[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]\n'
          'bad = [row[:] for row in B]\nbad[0][0] = "8"                     # clashes with the 8 at row 3, column 0')

EXPLAIN = {
    # ------------------------------------------------------------------ concatenation of array
    "concatenation-of-array": {
        "example": {"call": "get_concatenation([1, 3, 2])", "expect": "[1, 3, 2, 1, 3, 2]"},
        "approaches": {
            "Append twice in a loop": {
                "idea": [
                    "The answer is the array followed by itself, so walk it twice, appending every element.",
                ],
                "steps": [
                    "Repeat twice: append every x of nums to <code>ans</code>.",
                ],
                "why": [
                    "Python lists over-allocate, so each append is amortised O(1): 2n appends is O(n).",
                ],
                "dry": [
                    "First pass appends 1, 3, 2. Second pass appends 1, 3, 2 again.",
                    "The result is <strong>[1, 3, 2, 1, 3, 2]</strong>.",
                ],
            },
            "Pre-allocate and fill both halves": {
                "idea": [
                    "Allocate the final 2n-length list once, then write each element into both of its positions: i and i + n.",
                ],
                "steps": [
                    "<code>ans = [0] * 2n</code>.",
                    "For each i: <code>ans[i] = ans[i + n] = nums[i]</code>.",
                ],
                "why": [
                    "There is no resizing at all; it is the formula from the statement. O(n).",
                ],
                "dry": [
                    "n = 3. i=0 writes 1 to slots 0 and 3. i=1 writes 3 to slots 1 and 4. i=2 writes 2 to slots 2 and 5.",
                    "The result is <strong>[1, 3, 2, 1, 3, 2]</strong>.",
                ],
            },
            "List concatenation": {
                "idea": [
                    "<code>nums + nums</code> builds the result in one C-level copy, with no Python bytecode per element.",
                ],
                "steps": [
                    "Return <code>nums + nums</code>.",
                ],
                "why": [
                    "It is still O(n), which the output size forces anyway, and usually much faster than a Python loop.",
                ],
                "dry": [
                    "[1, 3, 2] + [1, 3, 2] = <strong>[1, 3, 2, 1, 3, 2]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ contains duplicate
    "contains-duplicate": {
        "example": {"call": "contains_duplicate([4, 1, 7, 3, 1, 9])", "expect": "True"},
        "approaches": {
            "Compare every pair": {
                "idea": [
                    "A duplicate is a pair i &lt; j with equal values, so check every pair.",
                ],
                "steps": [
                    "Two nested loops; return <code>True</code> on the first equal pair.",
                ],
                "why": [
                    "There are n(n-1)/2 pairs: O(n²) time and O(1) space.",
                ],
                "dry": [
                    "4 is compared with 1, 7, 3, 1, 9: no match.",
                    "1 is compared with 7, 3, then 1 at index 4: a match, so the result is <strong>True</strong>.",
                ],
            },
            "Sort, then compare neighbours": {
                "idea": [
                    "After sorting, equal values sit next to each other.",
                    "So one pass comparing each element with the next one finds any duplicate.",
                ],
                "steps": [
                    "Sort a copy.",
                    "Return whether any <code>nums[i] == nums[i + 1]</code>.",
                ],
                "why": [
                    "It is O(n log n) time. Space depends on the sort; Python's Timsort uses up to O(n).",
                ],
                "dry": [
                    "Sorted: [1, 1, 3, 4, 7, 9].",
                    "The very first neighbours are 1 and 1, so the result is <strong>True</strong>.",
                ],
            },
            "Hash set, stop at the first repeat": {
                "idea": [
                    "Remember every value seen so far in a set; set membership is O(1) on average.",
                    "A value already in the set is a duplicate, so stop right away.",
                ],
                "steps": [
                    "For each x: if it is in <code>seen</code>, return <code>True</code>; otherwise add it.",
                    "Return <code>False</code> at the end.",
                ],
                "why": [
                    "It is one pass: O(n) time and O(n) space, and it often stops early.",
                ],
                "dry": [
                    "seen grows to {4, 1, 7, 3}.",
                    "The next value 1 is already in seen, so the result is <strong>True</strong> after five steps.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid anagram
    "valid-anagram": {
        "example": {"call": 'is_anagram("listen", "silent")', "expect": "True"},
        "approaches": {
            "Sort both strings": {
                "idea": [
                    "Two strings are anagrams exactly when sorting their letters gives the same result.",
                ],
                "steps": [
                    "Return <code>sorted(s) == sorted(t)</code>.",
                ],
                "why": [
                    "It works for any alphabet: O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "\"listen\" sorts to e, i, l, n, s, t, and \"silent\" sorts to e, i, l, n, s, t.",
                    "They are equal, so the result is <strong>True</strong>.",
                ],
            },
            "Count with a hash map": {
                "idea": [
                    "Add 1 for every letter of s and subtract 1 for every letter of t; anagrams cancel out to all zeros.",
                    "A length check first rejects obvious mismatches in O(1).",
                ],
                "steps": [
                    "If the lengths differ, return <code>False</code>.",
                    "For each pair <code>(a, b)</code>: <code>counts[a] += 1</code>, <code>counts[b] -= 1</code>.",
                    "Return whether every count is 0.",
                ],
                "why": [
                    "Equal letter counts are exactly the definition of an anagram.",
                    "It is O(n) time and O(k) space for k distinct letters, and works for Unicode too.",
                ],
                "dry": [
                    "Pairs (l, s), (i, i), (s, l), (t, e), (e, n), (n, t).",
                    "l gets +1 and -1, s gets -1 and +1, i gets +1 and -1, t, e and n likewise.",
                    "Every count ends at 0, so the result is <strong>True</strong>.",
                ],
            },
            "Fixed array of 26 counters": {
                "idea": [
                    "The input is lowercase English only, so a list of 26 integers indexed by <code>ord(ch) - 97</code> replaces the hash map.",
                ],
                "steps": [
                    "Check the lengths, then add and subtract in the 26 slots.",
                    "Return <code>not any(counts)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(26) = O(1) space, and indexing a list is cheaper than hashing.",
                ],
                "dry": [
                    "The same additions and subtractions happen in slots l, i, s, t, e, n.",
                    "All 26 slots end at 0, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ two sum
    "two-sum": {
        "example": {"call": "two_sum([3, 9, 2, 7, 5], 9)", "expect": "[2, 3]"},
        "approaches": {
            "Check every pair": {
                "idea": [
                    "Try every pair i &lt; j and return the first one whose values add up to the target.",
                ],
                "steps": [
                    "Two nested loops; return <code>[i, j]</code> on a match.",
                ],
                "why": [
                    "It is O(n²) time. The inner loop is really asking \"is target - nums[i] somewhere later?\", which a hash map answers in O(1).",
                ],
                "dry": [
                    "3 pairs with 9, 2, 7, 5: the sums are 12, 5, 10, 8.",
                    "9 pairs with 2, 7, 5: no 9 among the sums.",
                    "2 + 7 = 9 at indices 2 and 3, so the result is <strong>[2, 3]</strong>.",
                ],
            },
            "Sort indices, two pointers": {
                "idea": [
                    "Sort the <em>indices</em> by value, because the answer must be positions in the original array.",
                    "Then use two pointers from both ends: a sum that is too small needs a bigger left value, and a sum that is too big needs a smaller right value.",
                ],
                "steps": [
                    "<code>order = sorted(range(n), key=nums.__getitem__)</code>.",
                    "Move <code>lo</code> or <code>hi</code> by comparing the sum with the target.",
                ],
                "why": [
                    "Each step rules out one index for good: O(n) after an O(n log n) sort. This is the approach 3Sum builds on.",
                ],
                "dry": [
                    "Sorted by value: 2 (index 2), 3 (0), 5 (4), 7 (3), 9 (1).",
                    "2 + 9 = 11 &gt; 9, so move hi. 2 + 7 = 9, a match.",
                    "The indices are 2 and 3, so the result is <strong>[2, 3]</strong>.",
                ],
            },
            "One-pass hash map": {
                "idea": [
                    "Walk the array once. For each x, the partner it needs is <code>target - x</code>.",
                    "Keep a dictionary from each value seen so far to its index. If the partner is already there, the pair is found.",
                    "Storing x only after the check means x can never pair with itself.",
                ],
                "steps": [
                    "For each i, x: if <code>target - x</code> is in <code>index</code>, return <code>[index[target - x], i]</code>.",
                    "Otherwise record <code>index[x] = i</code>.",
                ],
                "why": [
                    "Every pair is checked when its second element arrives: O(n) time and O(n) space.",
                ],
                "dry": [
                    "i=0, 3: needs 6, not seen. Store 3→0.",
                    "i=1, 9: needs 0. Store 9→1. i=2, 2: needs 7. Store 2→2.",
                    "i=3, 7: needs 2, which is at index 2. The result is <strong>[2, 3]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest common prefix
    "longest-common-prefix": {
        "example": {"call": 'longest_common_prefix(["interview", "internet", "interval", "internal"])', "expect": '"inter"'},
        "approaches": {
            "Horizontal scan: shrink the prefix string by string": {
                "idea": [
                    "Start with the first word as the candidate prefix.",
                    "For each following word, trim the candidate from the end until that word starts with it.",
                ],
                "steps": [
                    "<code>prefix = strs[0]</code>.",
                    "For each word: while it does not start with <code>prefix</code>, drop the last character.",
                ],
                "why": [
                    "After processing a word, the prefix is common to every word so far.",
                    "It is O(S) over all characters; a long first word may be trimmed one character at a time.",
                ],
                "dry": [
                    "Against \"internet\": interview → intervie → intervi → interv → inter, which matches.",
                    "\"interval\" and \"internal\" both start with \"inter\".",
                    "The result is <strong>\"inter\"</strong>.",
                ],
            },
            "Vertical scan: one column at a time": {
                "idea": [
                    "Compare the first character of every word, then the second, and so on.",
                    "Stop at the first column where some word ends or disagrees.",
                ],
                "steps": [
                    "For each index i of the first word, check every other word at i.",
                    "On a mismatch or end of a word, return <code>strs[0][:i]</code>.",
                ],
                "why": [
                    "It never looks past the answer plus one column: O(n·m) at worst, and it stops early. No string copies.",
                ],
                "dry": [
                    "Columns 0..4 are i, n, t, e, r in every word.",
                    "Column 5: interview has 'v' but internet has 'n', a mismatch.",
                    "The result is <strong>\"inter\"</strong>.",
                ],
            },
            "Sort, compare first and last": {
                "idea": [
                    "In sorted order, the first and last words differ the most; any prefix they share is shared by every word in between.",
                    "<code>min</code> and <code>max</code> give those two words without a full sort.",
                ],
                "steps": [
                    "<code>first, last = min(strs), max(strs)</code>.",
                    "Count how many leading characters match.",
                ],
                "why": [
                    "It compares only two words after finding the extremes.",
                ],
                "dry": [
                    "min is \"internal\" and max is \"interview\".",
                    "They match for i, n, t, e, r, then 'n' vs 'v' differs.",
                    "The result is <strong>\"inter\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ group anagrams
    "group-anagrams": {
        "example": {"call": 'sorted(sorted(g) for g in group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))',
                    "expect": '[["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]'},
        "approaches": {
            "Compare every pair with an anagram check": {
                "idea": [
                    "For each word not yet grouped, scan the rest and pull in every word with the same letter counts.",
                ],
                "steps": [
                    "Skip used words; build the group with <code>Counter</code> comparisons.",
                ],
                "why": [
                    "It does m² comparisons of O(k) each. A hash map avoids comparing words with each other at all.",
                ],
                "dry": [
                    "\"eat\" pulls in \"tea\" and \"ate\".",
                    "\"tan\" pulls in \"nat\". \"bat\" stays alone.",
                    "The groups are <strong>[[ate, eat, tea], [bat], [nat, tan]]</strong>.",
                ],
            },
            "Sorted word as the key": {
                "idea": [
                    "Anagrams sort to the same string, so use the sorted word as a dictionary key.",
                    "Each word is processed on its own, and the dictionary does the grouping.",
                ],
                "steps": [
                    "<code>groups[\"\".join(sorted(w))].append(w)</code>.",
                    "Return the dictionary's values.",
                ],
                "why": [
                    "It is O(m · k log k) for m words of length k.",
                ],
                "dry": [
                    "Keys: eat, tea and ate become \"aet\"; tan and nat become \"ant\"; bat becomes \"abt\".",
                    "The groups are <strong>[[ate, eat, tea], [bat], [nat, tan]]</strong>.",
                ],
            },
            "Letter-count tuple as the key": {
                "idea": [
                    "Use the 26 letter counts as the key instead. Building them is O(k), with no sort.",
                    "Convert the counts to a tuple, because lists cannot be dictionary keys.",
                ],
                "steps": [
                    "Count letters into a 26-slot list.",
                    "<code>groups[tuple(counts)].append(w)</code>.",
                ],
                "why": [
                    "It is O(m·k). In Python, sorting short words in C is often just as fast; this version wins on long words.",
                ],
                "dry": [
                    "eat, tea and ate all count a:1, e:1, t:1, so they share a key.",
                    "tan and nat share a:1, n:1, t:1; bat has its own key.",
                    "The groups are <strong>[[ate, eat, tea], [bat], [nat, tan]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ remove element
    "remove-element": {
        "example": {"setup": "a = [0, 1, 2, 2, 3, 0, 4, 2]\nk = remove_element(a, 2)", "call": "sorted(a[:k])", "expect": "[0, 0, 1, 3, 4]"},
        "approaches": {
            "Build a filtered copy, write it back": {
                "idea": [
                    "Collect the elements to keep in a new list and copy them to the front of nums.",
                ],
                "steps": [
                    "<code>kept = [x for x in nums if x != val]</code>.",
                    "Copy it to the front and return its length.",
                ],
                "why": [
                    "It is correct and O(n), but it allocates a second list, which the problem forbids.",
                ],
                "dry": [
                    "kept = [0, 1, 3, 0, 4], so k = 5.",
                    "The first five, sorted: <strong>[0, 0, 1, 3, 4]</strong>.",
                ],
            },
            "Read and write pointers": {
                "idea": [
                    "A read pointer visits every element; a write pointer <code>k</code> marks where the next kept element goes.",
                    "Each element that is not val is copied to position k, and k advances.",
                ],
                "steps": [
                    "<code>k = 0</code>; for each x not equal to val, set <code>nums[k] = x</code> and <code>k += 1</code>.",
                ],
                "why": [
                    "Kept elements stay in order. It is O(n) time and O(1) space, the pattern behind every in-place compaction.",
                ],
                "dry": [
                    "0 goes to slot 0, 1 to slot 1; the two 2s are skipped.",
                    "3 goes to slot 2, 0 to slot 3, 4 to slot 4; the last 2 is skipped.",
                    "k = 5, and the front is [0, 1, 3, 0, 4], which sorts to <strong>[0, 0, 1, 3, 4]</strong>.",
                ],
            },
            "Swap with the end when removals are rare": {
                "idea": [
                    "When val is rare, copying almost every element is wasted work.",
                    "Instead, when you find val, overwrite it with the last element and shrink the array by one.",
                    "Do not advance after the swap, because the element moved into place has not been checked yet.",
                ],
                "steps": [
                    "If <code>nums[i] == val</code>: <code>nums[i] = nums[n - 1]</code> and <code>n -= 1</code>.",
                    "Otherwise <code>i += 1</code>. Return n.",
                ],
                "why": [
                    "The number of writes equals the number of removals. The order of kept elements changes, which the problem allows.",
                ],
                "dry": [
                    "i=2 holds 2: pull in the last element (also 2), so n = 7; still 2, so pull in 4, n = 6.",
                    "i=3 holds 2: pull in nums[5] = 0, so n = 5.",
                    "i reaches n = 5. The front is [0, 1, 4, 0, 3].",
                    "Sorted: <strong>[0, 0, 1, 3, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ majority element
    "majority-element": {
        "example": {"call": "majority_element([2, 2, 1, 1, 1, 2, 2])", "expect": "2"},
        "approaches": {
            "Count each candidate": {
                "idea": [
                    "For each element, count its occurrences with a full scan and return the first one above n/2.",
                ],
                "steps": [
                    "Return the first x with <code>nums.count(x) &gt; n // 2</code>.",
                ],
                "why": [
                    "It is O(n²) time.",
                ],
                "dry": [
                    "2 appears 4 times, and 4 &gt; 7 // 2 = 3.",
                    "The result is <strong>2</strong> on the first candidate.",
                ],
            },
            "Hash map of counts": {
                "idea": [
                    "Count everything once and return the value with the highest count.",
                ],
                "steps": [
                    "<code>counts = Counter(nums)</code>; return the key with the largest count.",
                ],
                "why": [
                    "It is O(n) time but up to O(n) space.",
                ],
                "dry": [
                    "counts = {2: 4, 1: 3}.",
                    "The largest count belongs to <strong>2</strong>.",
                ],
            },
            "Sort, take the middle": {
                "idea": [
                    "A value that fills more than half the positions must cover the middle index of the sorted array, wherever its run starts.",
                ],
                "steps": [
                    "Return <code>sorted(nums)[n // 2]</code>.",
                ],
                "why": [
                    "It is one line; the sort costs O(n log n).",
                ],
                "dry": [
                    "Sorted: [1, 1, 1, 2, 2, 2, 2].",
                    "Index 3 holds <strong>2</strong>.",
                ],
            },
            "Boyer-Moore voting": {
                "idea": [
                    "Keep one candidate and a vote counter. A matching element adds a vote; a different element cancels one.",
                    "When the votes reach 0, the next element becomes the new candidate.",
                    "Each cancellation removes one majority element and one other element, and the majority has more than all the others combined, so it survives.",
                ],
                "steps": [
                    "If <code>votes == 0</code>, take x as the candidate.",
                    "<code>votes += 1</code> if x equals the candidate, otherwise <code>votes -= 1</code>.",
                ],
                "why": [
                    "It is O(n) time and O(1) space. If no majority is guaranteed, a second pass must confirm the candidate.",
                ],
                "dry": [
                    "2: candidate 2, votes 1. 2: votes 2. 1: votes 1. 1: votes 0.",
                    "1: votes are 0, so 1 becomes the candidate, votes 1.",
                    "2: votes 0. 2: votes are 0, so 2 becomes the candidate, votes 1.",
                    "The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ design hashset
    "design-hashset": {
        "example": {"setup": "s = MyHashSet()\nfor key in (1, 2, 10008):\n    s.add(key)",
                    "call": "[s.contains(1), s.contains(10008), s.contains(3), s.remove(2) or s.contains(2)]",
                    "expect": "[True, True, False, False]"},
        "approaches": {
            "Direct-address boolean array": {
                "idea": [
                    "Keys are bounded (0..10<sup>6</sup>), so give every possible key its own slot: <code>present[key]</code>.",
                ],
                "steps": [
                    "<code>add</code> and <code>remove</code> set the slot to True or False; <code>contains</code> reads it.",
                ],
                "why": [
                    "Every operation is O(1), but memory follows the key range (a million slots), not the number of keys stored.",
                ],
                "dry": [
                    "add sets slots 1, 2 and 10008 to True.",
                    "contains(1) and contains(10008) give <strong>True</strong>; contains(3) gives <strong>False</strong>.",
                    "remove(2) clears slot 2, so contains(2) gives <strong>False</strong>.",
                ],
            },
            "Separate chaining with buckets": {
                "idea": [
                    "Hash each key into one of B buckets (<code>key % B</code>) and keep a small list per bucket.",
                    "Different keys can land in the same bucket (a collision); the list holds all of them.",
                    "With B near the number of keys, buckets stay short, so operations are O(1) on average.",
                ],
                "steps": [
                    "<code>add</code>: append to the bucket if the key is not already there.",
                    "<code>remove</code>: delete from the bucket. <code>contains</code>: search the bucket.",
                ],
                "why": [
                    "A prime B spreads out regular key patterns. The worst case, where every key collides, degrades to a scan.",
                ],
                "dry": [
                    "B = 10007. Key 1 goes to bucket 1, key 2 to bucket 2, and 10008 % 10007 = 1 also goes to bucket 1, a collision.",
                    "Bucket 1 holds [1, 10008], so both contains checks find their key: <strong>True</strong>, <strong>True</strong>.",
                    "Bucket 3 is empty: <strong>False</strong>.",
                    "remove(2) empties bucket 2, so contains(2) is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ design hashmap
    "design-hashmap": {
        "example": {"setup": "m = MyHashMap()\nm.put(1, 10)\nm.put(10008, 20)\nm.put(1, 30)",
                    "call": "[m.get(1), m.get(10008), m.get(5), m.remove(1) or m.get(1)]", "expect": "[30, 20, -1, -1]"},
        "approaches": {
            "Direct-address array": {
                "idea": [
                    "One slot per possible key holding its value, with -1 meaning absent.",
                ],
                "steps": [
                    "<code>put</code> writes the slot; <code>get</code> reads it; <code>remove</code> writes -1.",
                ],
                "why": [
                    "Every operation is O(1), with memory sized by the key range.",
                ],
                "dry": [
                    "Slot 1 becomes 10, then 30; slot 10008 becomes 20.",
                    "get(1) = <strong>30</strong>, get(10008) = <strong>20</strong>, get(5) = <strong>-1</strong>.",
                    "remove(1) resets slot 1, so get(1) = <strong>-1</strong>.",
                ],
            },
            "Separate chaining with (key, value) pairs": {
                "idea": [
                    "Each bucket holds <code>[key, value]</code> pairs.",
                    "<code>put</code> updates the pair if the key is already in its bucket, and appends otherwise, so there are never duplicate keys.",
                    "Pairs are small lists, not tuples, so the value can be updated in place.",
                ],
                "steps": [
                    "Bucket = <code>key % B</code>.",
                    "<code>put</code>: update or append. <code>get</code>: scan the bucket. <code>remove</code>: pop the matching pair.",
                ],
                "why": [
                    "The average bucket length is the load factor n/B, which is constant: O(1) average.",
                ],
                "dry": [
                    "Bucket 1 receives [1, 10], then [10008, 20] (a collision), then put(1, 30) updates the first pair to [1, 30].",
                    "get(1) = <strong>30</strong>, get(10008) = <strong>20</strong>; bucket 5 is empty, so <strong>-1</strong>.",
                    "remove(1) pops [1, 30], so get(1) = <strong>-1</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sort an array
    "sort-an-array": {
        "example": {"call": "sort_array([3, 1, 3, 2, 3, 0])", "expect": "[0, 1, 2, 3, 3, 3]"},
        "approaches": {
            "Insertion sort": {
                "idea": [
                    "Grow a sorted prefix. Take the next element and shift larger prefix elements right until its place opens up.",
                ],
                "steps": [
                    "For i from 1: hold <code>x = nums[i]</code>, shift while <code>nums[j] &gt; x</code>, then drop x in.",
                ],
                "why": [
                    "It is O(n²) in general but O(n) on nearly sorted input, and the fastest method on tiny arrays, which is why library sorts use it for small runs.",
                ],
                "dry": [
                    "[3] then 1 is inserted before 3: [1, 3]. The next 3 stays: [1, 3, 3].",
                    "2 shifts both 3s right: [1, 2, 3, 3]. The next 3 stays.",
                    "0 shifts everything right: <strong>[0, 1, 2, 3, 3, 3]</strong>.",
                ],
            },
            "Merge sort": {
                "idea": [
                    "Split the array in half, sort each half recursively, then merge the two sorted halves.",
                    "Using <code>&lt;=</code> in the merge takes from the left half on ties, which keeps the sort stable.",
                ],
                "steps": [
                    "Base case: length ≤ 1.",
                    "Merge with two pointers into a new list.",
                ],
                "why": [
                    "It is O(n log n) on every input and stable, with an O(n) buffer.",
                ],
                "dry": [
                    "Halves [3, 1, 3] and [2, 3, 0] sort to [1, 3, 3] and [0, 2, 3].",
                    "Merge: 0, 1, 2, then 3, 3, 3.",
                    "The result is <strong>[0, 1, 2, 3, 3, 3]</strong>.",
                ],
            },
            "Heap sort": {
                "idea": [
                    "Turn the array into a max-heap in O(n), so the largest value sits at index 0.",
                    "Repeatedly swap the maximum to the end of the unsorted part and sift the new root down over the shrinking heap.",
                ],
                "steps": [
                    "Heapify: sift down from <code>n // 2 - 1</code> to 0.",
                    "For end from n - 1 down to 1: swap <code>nums[0]</code> with <code>nums[end]</code>, then <code>sift(0, end)</code>.",
                ],
                "why": [
                    "It is O(n log n) worst case with O(1) extra space, but not stable.",
                ],
                "dry": [
                    "Heapify: index 1 (value 1) swaps with its larger child 3, giving [3, 3, 3, 2, 1, 0].",
                    "Move 3 to the end and sift: the heap holds 3, 3, 2, 1, 0 with [3] sorted at the end. Repeating moves the other 3s back.",
                    "Then 2, then 1, then 0 are placed.",
                    "The result is <strong>[0, 1, 2, 3, 3, 3]</strong>.",
                ],
            },
            "Quicksort, random pivot, three-way partition": {
                "idea": [
                    "Partition around a pivot into three regions, less than, equal to and greater than, then recurse on the outer two.",
                    "A random pivot defeats already-sorted inputs, and the equal region handles many duplicates in one step.",
                    "Recursing on the smaller side first keeps the stack at O(log n).",
                ],
                "steps": [
                    "Pick a pivot; scan with <code>lt</code>, <code>i</code>, <code>gt</code>, swapping smaller values left and larger values right.",
                    "Recurse on <code>[lo, lt)</code> and <code>(gt, hi]</code>.",
                ],
                "why": [
                    "It is O(n log n) expected and usually the fastest in practice.",
                ],
                "dry": [
                    "The seeded generator first picks index 3, so the pivot is 2.",
                    "The partition gives [0, 1 | 2 | 3, 3, 3]: less, equal, greater.",
                    "The right part is all equal to its pivot, so one more partition finishes it; the left part [0, 1] is already in order.",
                    "The result is <strong>[0, 1, 2, 3, 3, 3]</strong>.",
                ],
            },
            "Counting sort over the value range": {
                "idea": [
                    "Values are bounded, so count how often each value occurs and write them back in order.",
                    "No comparisons are made, so the n log n lower bound for comparison sorts does not apply.",
                ],
                "steps": [
                    "Counts over <code>[min, max]</code>.",
                    "Expand each value by its count.",
                ],
                "why": [
                    "It is O(n + k) for a range of k values; sensible only when k is not much larger than n.",
                ],
                "dry": [
                    "The range is 0..3, with counts [1, 1, 1, 3].",
                    "Expanded: <strong>[0, 1, 2, 3, 3, 3]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sort colors
    "sort-colors": {
        "example": {"setup": "a = [2, 0, 2, 1, 1, 0]\nsort_colors(a)", "call": "a", "expect": "[0, 0, 1, 1, 2, 2]"},
        "approaches": {
            "Any comparison sort": {
                "idea": [
                    "Just sort; this ignores that there are only three distinct values.",
                ],
                "steps": [
                    "<code>nums.sort()</code>.",
                ],
                "why": [
                    "It is O(n log n); the other approaches use the three-value structure to reach O(n).",
                ],
                "dry": [
                    "Sorted: <strong>[0, 0, 1, 1, 2, 2]</strong>.",
                ],
            },
            "Count, then overwrite": {
                "idea": [
                    "Count the 0s, 1s and 2s, then write that many of each back in order: counting sort with k = 3.",
                ],
                "steps": [
                    "One pass to count, one pass to write.",
                ],
                "why": [
                    "It is O(n) time and O(1) space, but two passes, which the follow-up asks to avoid.",
                ],
                "dry": [
                    "Counts: 0s = 2, 1s = 2, 2s = 2.",
                    "Write 0, 0, 1, 1, 2, 2: <strong>[0, 0, 1, 1, 2, 2]</strong>.",
                ],
            },
            "Dutch national flag, one pass": {
                "idea": [
                    "Three pointers split the array into four regions: 0s, 1s, not yet seen, and 2s.",
                    "Look at <code>nums[mid]</code>: a 0 swaps to <code>low</code>, a 1 stays, and a 2 swaps to <code>high</code>.",
                    "After swapping with high, do not advance mid: the value that came back is unseen.",
                ],
                "steps": [
                    "While <code>mid &lt;= high</code>: handle 0 (swap with low, advance both), 1 (advance mid) or 2 (swap with high, <code>high -= 1</code>).",
                ],
                "why": [
                    "Each step shrinks the unseen region by one: exactly n steps, O(1) space.",
                ],
                "dry": [
                    "mid=0 sees 2: swap with high=5, giving [0, 0, 2, 1, 1, 2], high = 4.",
                    "mid=0 sees 0: low = 1, mid = 1. mid=1 sees 0: low = 2, mid = 2.",
                    "mid=2 sees 2: swap with high=4, giving [0, 0, 1, 1, 2, 2], high = 3.",
                    "mid=2 sees 1, then mid=3 sees 1; mid passes high, so stop.",
                    "The result is <strong>[0, 0, 1, 1, 2, 2]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ encode and decode strings
    "encode-decode-strings": {
        "example": {"call": 'decode(encode(["4#ab", "", "/:x"]))', "expect": '["4#ab", "", "/:x"]'},
        "approaches": {
            "Escape the delimiter": {
                "idea": [
                    "End each string with a delimiter pair, <code>/:</code>, that can never appear in the escaped text.",
                    "Make that true by doubling every <code>/</code> inside the strings.",
                    "Decoding reads character by character: <code>//</code> is a literal slash and <code>/:</code> ends a string.",
                ],
                "steps": [
                    "<code>encode</code>: <code>s.replace(\"/\", \"//\") + \"/:\"</code> for each string.",
                    "<code>decode</code>: a small state machine over the characters.",
                ],
                "why": [
                    "Escaped text never contains a lone <code>/</code> followed by <code>:</code>, so string ends are unambiguous.",
                    "It is O(n), but the encoded size depends on how many slashes the strings contain.",
                ],
                "dry": [
                    "Encoded: \"4#ab/:\" + \"/:\" + \"//:x/:\" = \"4#ab/:/://:x/:\".",
                    "Decode: read 4, #, a, b, then \"/:\" ends \"4#ab\". The next \"/:\" ends an empty string.",
                    "\"//\" gives a literal \"/\", then \":\" and \"x\", then \"/:\" ends \"/:x\".",
                    "The result is <strong>[\"4#ab\", \"\", \"/:x\"]</strong>.",
                ],
            },
            "Length prefix": {
                "idea": [
                    "Write each string as its length, a <code>#</code>, and then the string itself.",
                    "The decoder reads digits up to the first <code>#</code>, then takes exactly that many characters, whatever they are.",
                    "Digits or <code>#</code> inside the payload are never interpreted, because the decoder already knows where each string ends.",
                ],
                "steps": [
                    "<code>encode</code>: <code>f\"{len(s)}#{s}\"</code> for each string.",
                    "<code>decode</code>: find <code>#</code>, parse the length, slice, and jump past the string.",
                ],
                "why": [
                    "The overhead is a few characters per string regardless of content; real wire formats work the same way.",
                    "It is O(n).",
                ],
                "dry": [
                    "Encoded: \"4#4#ab\" + \"0#\" + \"3#/:x\" = \"4#4#ab0#3#/:x\".",
                    "Length 4 gives \"4#ab\"; the # inside it is never treated as a separator.",
                    "Length 0 gives \"\". Length 3 gives \"/:x\".",
                    "The result is <strong>[\"4#ab\", \"\", \"/:x\"]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ range sum query 2D
    "range-sum-query-2d": {
        "example": {"setup": "nm = NumMatrix([[3, 0, 1, 4, 2], [5, 6, 3, 2, 1], [1, 2, 0, 1, 5], [4, 1, 0, 1, 7], [1, 0, 3, 0, 5]])",
                    "call": "[nm.sumRegion(2, 1, 4, 3), nm.sumRegion(1, 1, 2, 2)]", "expect": "[8, 11]"},
        "approaches": {
            "Sum the rectangle per query": {
                "idea": [
                    "Add up every cell inside the rectangle on each query.",
                ],
                "steps": [
                    "Sum each row's slice, for every row in range.",
                ],
                "why": [
                    "It is O(m·n) per query, which is too slow for many queries.",
                ],
                "dry": [
                    "Region (2,1)-(4,3): rows [2, 0, 1], [1, 0, 1], [0, 3, 0] sum to 3 + 2 + 3 = <strong>8</strong>.",
                    "Region (1,1)-(2,2): [6, 3] and [2, 0] sum to <strong>11</strong>.",
                ],
            },
            "Prefix sums per row": {
                "idea": [
                    "Keep running sums along each row, so a row segment is one subtraction.",
                    "A rectangle then costs one subtraction per row.",
                ],
                "steps": [
                    "<code>rows[r][c]</code> = the sum of the first c values of row r.",
                    "Sum <code>rows[r][c2+1] - rows[r][c1]</code> over the rows.",
                ],
                "why": [
                    "It is O(m·n) to build and O(m) per query: the 1-D trick applied row by row.",
                ],
                "dry": [
                    "Row 2 prefix [0, 1, 3, 3, 4, 9]: its segment from column 1 to 3 is 4 - 1 = 3.",
                    "Rows 3 and 4 give 2 and 3, so the total is <strong>8</strong>.",
                    "The second query likewise gives 9 + 2 = <strong>11</strong>.",
                ],
            },
            "2-D prefix sums": {
                "idea": [
                    "<code>P[r][c]</code> is the sum of the rectangle from the top-left corner to cell (r-1, c-1); an extra zero row and column remove edge cases.",
                    "Build: the cell, plus the rectangle above, plus the rectangle to the left, minus their overlap (counted twice).",
                    "Query: the big rectangle minus the strip above, minus the strip to the left, plus the corner that was subtracted twice.",
                ],
                "steps": [
                    "<code>P[r+1][c+1] = M[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]</code>.",
                    "<code>sum = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]</code>.",
                ],
                "why": [
                    "Inclusion and exclusion count every cell in the region exactly once.",
                    "It is O(m·n) to build and O(1) per query.",
                ],
                "dry": [
                    "Query (2,1)-(4,3): P[5][4] = 38, P[2][4] = 24, P[5][1] = 14, P[2][1] = 8.",
                    "38 - 24 - 14 + 8 = <strong>8</strong>.",
                    "Query (1,1)-(2,2): 21 - 4 - 9 + 3 = <strong>11</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ product except self
    "product-except-self": {
        "example": {"call": "product_except_self([1, 2, 3, 4])", "expect": "[24, 12, 8, 6]"},
        "approaches": {
            "Multiply everything else, per index": {
                "idea": [
                    "For each i, multiply every element except <code>nums[i]</code>.",
                ],
                "steps": [
                    "Nested loops skipping j == i.",
                ],
                "why": [
                    "It is O(n²); it recomputes the same partial products again and again.",
                ],
                "dry": [
                    "i=0: 2·3·4 = 24. i=1: 1·3·4 = 12. i=2: 1·2·4 = 8. i=3: 1·2·3 = 6.",
                    "The result is <strong>[24, 12, 8, 6]</strong>.",
                ],
            },
            "Total product and division": {
                "idea": [
                    "Divide the total product by each element. This is forbidden here, and fragile anyway: zeros need special cases and the total can overflow in fixed-width integers.",
                ],
                "steps": [
                    "Count zeros: two or more means all zeros; exactly one means only the zero's slot gets the product of the rest.",
                    "Otherwise return <code>total // x</code> for each x.",
                ],
                "why": [
                    "It is O(n), but it breaks the problem's rules.",
                ],
                "dry": [
                    "There are no zeros, and the total is 24.",
                    "24/1, 24/2, 24/3, 24/4 = <strong>[24, 12, 8, 6]</strong>.",
                ],
            },
            "Prefix and suffix product arrays": {
                "idea": [
                    "The answer at i is (the product of everything before i) × (the product of everything after i).",
                    "Compute both kinds of products in one pass each.",
                ],
                "steps": [
                    "<code>left[i] = left[i-1] · nums[i-1]</code>.",
                    "<code>right[i] = right[i+1] · nums[i+1]</code>.",
                    "Multiply them elementwise.",
                ],
                "why": [
                    "It is O(n) time and O(n) extra space.",
                ],
                "dry": [
                    "left = [1, 1, 2, 6].",
                    "right = [24, 12, 4, 1].",
                    "The products are <strong>[24, 12, 8, 6]</strong>.",
                ],
            },
            "Output array plus a running suffix": {
                "idea": [
                    "Store the prefix products directly in the output array.",
                    "Then sweep from the right, carrying the suffix product in one variable and multiplying it in.",
                ],
                "steps": [
                    "<code>out[i] = out[i-1] · nums[i-1]</code>.",
                    "From the right: <code>out[i] *= suffix</code>, then <code>suffix *= nums[i]</code>.",
                ],
                "why": [
                    "It is O(n) time and O(1) extra space beyond the output.",
                ],
                "dry": [
                    "Prefix pass: out = [1, 1, 2, 6].",
                    "i=3: 6·1 = 6, suffix 4. i=2: 2·4 = 8, suffix 12.",
                    "i=1: 1·12 = 12, suffix 24. i=0: 1·24 = 24.",
                    "The result is <strong>[24, 12, 8, 6]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid sudoku
    "valid-sudoku": {
        "example": {"setup": SUDOKU, "call": "is_valid_sudoku(bad)", "expect": "False"},
        "approaches": {
            "Three separate passes": {
                "idea": [
                    "Check every row, every column and every 3×3 box for a repeated digit, each as a separate pass.",
                ],
                "steps": [
                    "<code>ok(cells)</code>: the filled digits must all be distinct.",
                    "All rows, then all columns, then all boxes.",
                ],
                "why": [
                    "Each pass is independent and easy to get right; it reads the board three times.",
                ],
                "dry": [
                    "Every row is fine: the changed row 0 is 8, 3, 7 with no repeat.",
                    "Column 0 is 8, 6, 8, 4, 7: the 8 repeats, so it fails.",
                    "The result is <strong>False</strong>.",
                ],
            },
            "One pass, 27 sets": {
                "idea": [
                    "Keep one set per row, one per column and one per box.",
                    "Each filled cell is checked against its three sets and then added to them.",
                    "The box index is <code>(r // 3)·3 + c // 3</code>.",
                ],
                "steps": [
                    "For each filled cell, return <code>False</code> if the digit is already in its row, column or box set.",
                    "Otherwise add it to all three.",
                ],
                "why": [
                    "It is a single pass that stops at the first conflict: O(81).",
                ],
                "dry": [
                    "(0, 0) = '8' goes into row 0, column 0 and box 0.",
                    "Rows 1 and 2 add their digits without conflict.",
                    "(3, 0) = '8': column 0 already has 8, so the result is <strong>False</strong>.",
                ],
            },
            "One pass, bitmasks": {
                "idea": [
                    "Replace each set with a 9-bit integer: bit d is on once digit d has been seen.",
                    "Checking is a bitwise AND and adding is an OR.",
                ],
                "steps": [
                    "<code>bit = 1 &lt;&lt; d</code>; if <code>(rows[r] | cols[c] | boxes[b]) &amp; bit</code>, it is a conflict.",
                    "Otherwise OR the bit into all three.",
                ],
                "why": [
                    "It is the same single pass using 27 small integers, as fast Sudoku solvers do.",
                ],
                "dry": [
                    "(0, 0) sets bit 8 in cols[0].",
                    "(3, 0) = '8': cols[0] &amp; (1 &lt;&lt; 8) is non-zero.",
                    "The result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest consecutive sequence
    "longest-consecutive-sequence": {
        "example": {"call": "longest_consecutive([100, 4, 200, 1, 3, 2])", "expect": "4"},
        "approaches": {
            "Count up from every element": {
                "idea": [
                    "From each value x, count upwards (x + 1, x + 2, …) using a set for O(1) lookups.",
                ],
                "steps": [
                    "For each x, extend while <code>x + length</code> is present.",
                ],
                "why": [
                    "Every element of a run restarts the count, so a run of length L costs O(L²): O(n²) overall.",
                ],
                "dry": [
                    "100 gives 1, 4 gives 1, 200 gives 1.",
                    "1 counts up through 2, 3, 4, giving <strong>4</strong>.",
                    "3 gives 2 and 2 gives 3, recounting the same run. The best is <strong>4</strong>.",
                ],
            },
            "Sort and scan": {
                "idea": [
                    "Sort, then walk counting runs: a step of exactly 1 extends the run, a repeated value is skipped, and anything else starts over.",
                ],
                "steps": [
                    "Sort; for each neighbour pair, extend, skip or reset.",
                ],
                "why": [
                    "Forgetting the duplicate case is the classic bug. It is O(n log n).",
                ],
                "dry": [
                    "Sorted: [1, 2, 3, 4, 100, 200].",
                    "The run 1, 2, 3, 4 has length 4; 100 and 200 reset to 1.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "Hash set, count only from run starts": {
                "idea": [
                    "A value starts a run exactly when <code>x - 1</code> is not present.",
                    "Count upwards only from those starts; every other value is skipped in O(1).",
                    "Each element is counted at most once, by the single start of its run: linear in total.",
                ],
                "steps": [
                    "<code>present = set(nums)</code>.",
                    "For each x in the set with <code>x - 1</code> absent, count the run.",
                ],
                "why": [
                    "The nested loop looks quadratic but does O(n) work in total. Iterating the set avoids repeated starts from duplicates.",
                ],
                "dry": [
                    "100: 99 is absent, so it is a start, length 1. 200: a start, length 1.",
                    "1: 0 is absent, so it is a start; count 2, 3, 4, giving length <strong>4</strong>.",
                    "2, 3 and 4 have predecessors, so they are skipped.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ best time to buy and sell II
    "best-time-stock-ii": {
        "example": {"call": "max_profit([7, 1, 5, 3, 6, 4])", "expect": "7"},
        "approaches": {
            "Try every buy/sell decision": {
                "idea": [
                    "Each day you either act (buy if you hold nothing, sell if you hold a share) or wait; take whichever leads to more profit.",
                    "The state is the day and whether you are holding a share.",
                ],
                "steps": [
                    "<code>best(day, holding)</code>: compare waiting with buying or selling.",
                ],
                "why": [
                    "It explores 2<sup>n</sup> decision paths; this is the recurrence the DP below evaluates efficiently.",
                ],
                "dry": [
                    "The best path buys at 1, sells at 5, buys at 3, sells at 6.",
                    "(5 - 1) + (6 - 3) = <strong>7</strong>.",
                ],
            },
            "DP over (day, holding)": {
                "idea": [
                    "Only 2n states exist: (day, holding a share or not).",
                    "<code>cash[i]</code> is the best profit holding nothing at the end of day i; <code>hold[i]</code> is the best while holding one share.",
                ],
                "steps": [
                    "<code>cash[i] = max(cash[i-1], hold[i-1] + p)</code>, selling today or not.",
                    "<code>hold[i] = max(hold[i-1], cash[i-1] - p)</code>, buying today or not.",
                ],
                "why": [
                    "Each state is computed from the previous day's two states: O(n) time and O(n) space.",
                ],
                "dry": [
                    "Day 0: cash 0, hold -7.",
                    "p=1: cash 0, hold -1. p=5: cash 4, hold -1. p=3: cash 4, hold 1.",
                    "p=6: cash 7, hold 1. p=4: cash 7, hold 3.",
                    "The result is cash = <strong>7</strong>.",
                ],
            },
            "DP with two rolling variables": {
                "idea": [
                    "Day i only reads day i - 1, so two variables replace the two arrays.",
                ],
                "steps": [
                    "<code>cash, hold = max(cash, hold + p), max(hold, cash - p)</code> for each price.",
                ],
                "why": [
                    "It is O(n) time and O(1) space, and it extends directly to the cooldown and fee variants.",
                ],
                "dry": [
                    "The same values as the table: (0, -7) → (0, -1) → (4, -1) → (4, 1) → (7, 1) → (7, 3).",
                    "The result is <strong>7</strong>.",
                ],
            },
            "Greedy: sum every rise": {
                "idea": [
                    "Any profitable holding period equals the sum of the day-to-day changes inside it.",
                    "So collect every positive daily change and skip every negative one; no strategy can beat that.",
                ],
                "steps": [
                    "Sum <code>max(0, b - a)</code> over consecutive pairs.",
                ],
                "why": [
                    "It is O(n) time and O(1) space, but it stops working once fees or cooldowns are added.",
                ],
                "dry": [
                    "The changes are -6, +4, -2, +3, -2.",
                    "The rises are 4 and 3, summing to <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ majority element II
    "majority-element-ii": {
        "example": {"call": "sorted(majority_element_ii([1, 2, 1, 3, 1, 2, 2]))", "expect": "[1, 2]"},
        "approaches": {
            "Hash map of counts": {
                "idea": [
                    "Count everything and keep the values above n/3.",
                ],
                "steps": [
                    "<code>[x for x, c in Counter(nums).items() if c &gt; n // 3]</code>.",
                ],
                "why": [
                    "It is O(n) time and O(n) space.",
                ],
                "dry": [
                    "Counts: 1→3, 2→3, 3→1, and n // 3 = 2.",
                    "1 and 2 exceed 2: <strong>[1, 2]</strong>.",
                ],
            },
            "Sort and measure runs": {
                "idea": [
                    "After sorting, equal values form runs; keep any run longer than n/3.",
                ],
                "steps": [
                    "Sort, then measure each run's length.",
                ],
                "why": [
                    "It needs no hash map, but costs O(n log n) for the sort.",
                ],
                "dry": [
                    "Sorted: [1, 1, 1, 2, 2, 2, 3].",
                    "The runs have lengths 3, 3 and 1, so 1 and 2 qualify: <strong>[1, 2]</strong>.",
                ],
            },
            "Boyer-Moore with two candidates": {
                "idea": [
                    "At most two values can appear more than n/3 times, so keep two candidates with vote counters.",
                    "A value matching a candidate votes for it; otherwise it fills an empty slot, or, if both slots are taken, it cancels one vote from each, removing three distinct values at once.",
                    "A true answer cannot be cancelled away, but a survivor can be a false positive, so a second pass counts the candidates.",
                ],
                "steps": [
                    "Update <code>(c1, v1)</code> and <code>(c2, v2)</code> per element.",
                    "Return the candidates whose real count exceeds n // 3.",
                ],
                "why": [
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "1: c1 = 1 (v1 1). 2: c2 = 2 (v2 1). 1: v1 2.",
                    "3: matches neither, both slots taken, so cancel: v1 1, v2 0.",
                    "1: v1 2. 2: matches c2, v2 1. 2: v2 2.",
                    "The candidates 1 and 2 both have 3 &gt; 2 occurrences: <strong>[1, 2]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subarray sum equals k
    "subarray-sum-equals-k": {
        "example": {"call": "subarray_sum([1, 2, 3, -3, 3], 3)", "expect": "5"},
        "approaches": {
            "Every subarray, summed from scratch": {
                "idea": [
                    "Enumerate every (i, j) and add up the slice each time.",
                ],
                "steps": [
                    "Count the pairs with <code>sum(nums[i:j+1]) == k</code>.",
                ],
                "why": [
                    "It is O(n³) time.",
                ],
                "dry": [
                    "The matching subarrays are [1, 2], [3], [1, 2, 3, -3], [3, -3, 3] and the last [3].",
                    "The total is <strong>5</strong>.",
                ],
            },
            "Every start, running sum": {
                "idea": [
                    "Fix the start and extend the end one step at a time, keeping a running total, so no slice is re-summed.",
                ],
                "steps": [
                    "For each i, accumulate <code>total</code> while extending j, and count the hits.",
                ],
                "why": [
                    "It is O(n²) time and O(1) space.",
                ],
                "dry": [
                    "From 1: totals 1, 3 ✓, 6, 3 ✓, 6. From 2: 2, 5, 2, 5.",
                    "From 3: 3 ✓, 0, 3 ✓. From -3: -3, 0. From 3: 3 ✓.",
                    "There are 5 hits: <strong>5</strong>.",
                ],
            },
            "Prefix sums and a hash map": {
                "idea": [
                    "With running prefix sums P, a subarray ending at j sums to k exactly when some earlier prefix equals <code>P[j] - k</code>.",
                    "Keep a counter of prefixes seen so far, which answers \"how many?\" in O(1).",
                    "Seed it with {0: 1}, the empty prefix, so subarrays that start at index 0 are counted.",
                ],
                "steps": [
                    "<code>total += x</code>; <code>count += seen[total - k]</code>; <code>seen[total] += 1</code>.",
                ],
                "why": [
                    "Each earlier matching prefix marks a distinct start for a subarray summing to k.",
                    "It is one pass: O(n) time and O(n) space.",
                ],
                "dry": [
                    "x=1: total 1, needs -2, count 0. x=2: total 3, needs 0 (seen once), count 1.",
                    "x=3: total 6, needs 3 (seen once), count 2.",
                    "x=-3: total 3, needs 0, count 3. Now prefix 3 has been seen twice.",
                    "x=3: total 6, needs 3 (seen twice), count <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ first missing positive
    "first-missing-positive": {
        "example": {"call": "first_missing_positive([3, 4, -1, 1])", "expect": "2"},
        "approaches": {
            "Try 1, 2, 3, &hellip; with a linear search": {
                "idea": [
                    "Test 1, 2, 3, … in order with a linear <code>in</code> search; the first one missing is the answer.",
                ],
                "steps": [
                    "While x is in the list, increment x.",
                ],
                "why": [
                    "It is O(n²) time.",
                ],
                "dry": [
                    "1 is present. 2 is not.",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Sort, then walk": {
                "idea": [
                    "Sort, then walk upwards: the answer starts at 1 and increases each time the expected value turns up.",
                ],
                "steps": [
                    "<code>want = 1</code>; for x in sorted order, if <code>x == want</code>, increment want.",
                ],
                "why": [
                    "Non-positives and duplicates are skipped naturally. It is O(n log n).",
                ],
                "dry": [
                    "Sorted: [-1, 1, 3, 4].",
                    "-1: skipped. 1: want becomes 2. 3 ≠ 2 and 4 ≠ 2.",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Hash set": {
                "idea": [
                    "Put everything in a set, then test 1, 2, … in O(1) each.",
                ],
                "steps": [
                    "<code>present = set(nums)</code>; count up until a value is missing.",
                ],
                "why": [
                    "It is O(n) time but O(n) space, which the problem forbids.",
                ],
                "dry": [
                    "present = {3, 4, -1, 1}.",
                    "1 is in it, 2 is not, so the result is <strong>2</strong>.",
                ],
            },
            "Cyclic sort: put each value at its own index": {
                "idea": [
                    "The answer is between 1 and n + 1, so only values 1..n matter, and value v belongs at index v - 1.",
                    "Keep swapping the current value into its home until the slot holds something out of range or a duplicate.",
                    "Then the first index i whose value is not i + 1 gives the answer i + 1.",
                ],
                "steps": [
                    "For each i: while <code>1 ≤ nums[i] ≤ n</code> and its home does not already hold it, swap it home.",
                    "Scan for the first <code>nums[i] != i + 1</code>; if there is none, return n + 1.",
                ],
                "why": [
                    "Every swap places one value permanently, so there are at most n swaps in total: O(n) time and O(1) space. It does modify the input.",
                ],
                "dry": [
                    "i=0: 3 belongs at index 2, so swap: [-1, 4, 3, 1]. -1 is out of range, so stop.",
                    "i=1: 4 goes to index 3, giving [-1, 1, 3, 4]; then 1 goes to index 0, giving [1, -1, 3, 4]. -1, so stop.",
                    "i=2 and i=3 are already home.",
                    "The scan finds index 1 holding -1, so the result is <strong>2</strong>.",
                ],
            },
        },
    },
}
