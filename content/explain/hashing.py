"""Write-ups for the Arrays and Hashing topic."""

SUDOKU = ('B = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],'
          '["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],'
          '[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]')
SUDOKU_BAD = SUDOKU + '\nbad = [row[:] for row in B]\nbad[0][0] = "8"                     # clashes with the 8 at row 3, column 0'

EXPLAIN = {
    # ------------------------------------------------------------------ concatenation of array
    "concatenation-of-array": {
        "examples": [
            {"call": "get_concatenation([1, 3, 2])", "expect": "[1, 3, 2, 1, 3, 2]"},
            {"call": "get_concatenation([])", "expect": "[]"},
        ],
        "approaches": {
            "Append twice in a loop": {
                "idea": [
                    "The answer is <code>nums</code> followed by itself, so the most literal way to build it is to walk <code>nums</code> twice and append every element.",
                    "The outer loop only counts the two copies; it never looks at its variable, hence the <code>_</code>.",
                ],
                "steps": [
                    "Start with an empty list <code>ans</code>.",
                    "Repeat twice with <code>for _ in range(2)</code>.",
                    "Inside, loop over every <code>x</code> in <code>nums</code> and call <code>ans.append(x)</code>.",
                    "After the first pass <code>ans</code> equals <code>nums</code>; after the second it is <code>nums</code> twice.",
                    "Return <code>ans</code>.",
                ],
                "why": [
                    "Both passes read <code>nums</code> left to right, so position <code>i</code> is written by the first pass and position <code>i + n</code> by the second, which is exactly the definition.",
                    "Python lists over-allocate, so each append is amortised O(1) and 2n appends cost <strong>O(n)</strong> time.",
                    "Apart from the output itself only the loop variables are kept: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "ans = [].",
                        "First pass: append 1, 3, 2. ans = [1, 3, 2].",
                        "Second pass: append 1, 3, 2 again. ans = [1, 3, 2, 1, 3, 2].",
                        "It returns <strong>[1, 3, 2, 1, 3, 2]</strong>.",
                    ],
                    [
                        "ans = [].",
                        "First pass: <code>nums</code> is empty, so the inner loop body never runs.",
                        "Second pass: same, nothing is appended.",
                        "It returns <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>append</code> in a loop really O(n) overall?",
                     "Yes. When the list runs out of room Python grows it by a proportional amount, so the copying cost averages out to a constant per append."],
                    ["Could I write <code>ans.extend(nums)</code> twice instead?",
                     "Yes, and it does the same work in C rather than in a Python loop. The loop version is shown because it makes every write visible."],
                    ["Does this change <code>nums</code>?",
                     "No. It only reads <code>nums</code> and writes into a brand-new list."],
                ],
            },
            "Pre-allocate and fill both halves": {
                "idea": [
                    "The output length is known up front (2n), so allocate it once and fill it, instead of growing a list.",
                    "Each element belongs in exactly two places, index <code>i</code> and index <code>i + n</code>, so one pass can write both.",
                ],
                "steps": [
                    "Let <code>n = len(nums)</code>.",
                    "Allocate <code>ans = [0] * (2 * n)</code>.",
                    "Loop <code>i, x</code> over <code>enumerate(nums)</code>.",
                    "Write both copies with the chained assignment <code>ans[i] = ans[i + n] = x</code>.",
                    "Return <code>ans</code>.",
                ],
                "why": [
                    "Every index of <code>ans</code> from 0 to 2n − 1 is either some <code>i</code> or some <code>i + n</code>, so every slot is overwritten and no placeholder 0 survives.",
                    "One loop of n iterations with two O(1) writes each gives <strong>O(n)</strong> time.",
                    "There is no resizing at all; beyond the output only <code>n</code>, <code>i</code> and <code>x</code> are kept, so extra space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "n = 3, ans = [0, 0, 0, 0, 0, 0].",
                        "i=0, x=1: write slots 0 and 3. ans = [1, 0, 0, 1, 0, 0].",
                        "i=1, x=3: write slots 1 and 4. i=2, x=2: write slots 2 and 5.",
                        "It returns <strong>[1, 3, 2, 1, 3, 2]</strong>.",
                    ],
                    [
                        "n = 0, so <code>ans = [0] * 0</code> is already [].",
                        "The loop has nothing to enumerate.",
                        "It returns <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>[0] * (2 * n)</code> and not <code>[None] * (2 * n)</code>?",
                     "Either works, because every slot is overwritten. The placeholder value never reaches the output."],
                    ["How does <code>ans[i] = ans[i + n] = x</code> work?",
                     "A chained assignment evaluates <code>x</code> once and assigns it to each target in turn, left to right. It is two writes on one line."],
                    ["Is this faster than appending?",
                     "Slightly, since there are no resizes, but both are O(n). The real gain is that it mirrors the statement's formula <code>ans[i + n] = nums[i]</code> directly."],
                ],
            },
            "List concatenation": {
                "idea": [
                    "Python already has an operator for this: <code>nums + nums</code> builds a new list that is the first list followed by the second.",
                    "The copying happens inside C, so there is no Python bytecode per element.",
                ],
                "steps": [
                    "Evaluate <code>nums + nums</code>.",
                    "Python allocates a list of length 2n.",
                    "It copies the references of <code>nums</code> into the first half and again into the second half.",
                    "Return that new list.",
                ],
                "why": [
                    "List <code>+</code> is defined as concatenation, which is exactly the required output.",
                    "It must still copy 2n references, so it is <strong>O(n)</strong> time; the output size forces that anyway.",
                    "No helper structures are used, so extra space is <strong>O(1)</strong> beyond the output.",
                ],
                "dry": [
                    [
                        "[1, 3, 2] + [1, 3, 2] allocates 6 slots.",
                        "Slots 0..2 get 1, 3, 2 and slots 3..5 get 1, 3, 2.",
                        "It returns <strong>[1, 3, 2, 1, 3, 2]</strong>.",
                    ],
                    [
                        "[] + [] allocates 0 slots.",
                        "Nothing is copied.",
                        "It returns <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>nums * 2</code> the same?",
                     "Yes, for a list <code>nums * 2</code> also returns the list repeated twice, at the same O(n) cost."],
                    ["Does the result share elements with <code>nums</code>?",
                     "It holds references to the same objects. For integers that never matters, but for a list of lists both halves would point at the same inner lists."],
                    ["Is using the built-in acceptable in an interview?",
                     "Usually yes for this problem, but be ready to write one of the loop versions to show you know what the operator does."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ contains duplicate
    "contains-duplicate": {
        "examples": [
            {"call": "contains_duplicate([4, 1, 7, 3, 1, 9])", "expect": "True"},
            {"call": "contains_duplicate([3, 1, 2])", "expect": "False"},
        ],
        "approaches": {
            "Compare every pair": {
                "idea": [
                    "A duplicate is two different indices <code>i &lt; j</code> holding the same value, so the direct check is to try every such pair.",
                    "Starting <code>j</code> at <code>i + 1</code> means each pair is tried once and an element is never compared with itself.",
                ],
                "steps": [
                    "Let <code>n = len(nums)</code>.",
                    "Loop <code>i</code> over every index.",
                    "Loop <code>j</code> from <code>i + 1</code> to <code>n - 1</code>.",
                    "If <code>nums[i] == nums[j]</code>, return <code>True</code> immediately.",
                    "If both loops finish, no pair matched: return <code>False</code>.",
                ],
                "why": [
                    "If a duplicate exists at indices p &lt; q, the iteration <code>i = p, j = q</code> happens and returns <code>True</code>, so nothing is missed.",
                    "In the worst case (no duplicate) all n(n − 1)/2 pairs are compared, giving <strong>O(n²)</strong> time.",
                    "Only the two indices are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (4): compared with 1, 7, 3, 1, 9. No match.",
                        "i=1 (1): j=2 (7) no, j=3 (3) no.",
                        "j=4 (1): equal to nums[1].",
                        "It returns <strong>True</strong> without looking at index 5.",
                    ],
                    [
                        "i=0 (3): compared with 1 and 2. No match.",
                        "i=1 (1): compared with 2. No match.",
                        "i=2: no index after it.",
                        "All 3 pairs differ, so it returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>j</code> start at <code>i + 1</code> and not 0?",
                     "Starting at 0 would compare <code>nums[i]</code> with itself (always equal) and would also try every pair twice."],
                    ["When is the worst case hit?",
                     "When there is no duplicate, or the only duplicate is at the very end, because the loops cannot stop early."],
                    ["Is there any reason to use this?",
                     "It needs no extra memory and no hashable values, so it is fine for tiny inputs, but it is quadratic and should be the warm-up only."],
                ],
            },
            "Sort, then compare neighbours": {
                "idea": [
                    "After sorting, equal values sit next to each other, so a duplicate shows up as two equal <em>neighbours</em>.",
                    "That turns a search over all pairs into a single scan of adjacent pairs.",
                ],
                "steps": [
                    "Make a sorted copy: <code>nums = sorted(nums)</code>.",
                    "For each <code>i</code> from 0 to <code>len(nums) - 2</code>, compare <code>nums[i]</code> with <code>nums[i + 1]</code>.",
                    "<code>any(...)</code> returns <code>True</code> as soon as one comparison is equal.",
                    "If no neighbours are equal, <code>any</code> returns <code>False</code>.",
                ],
                "why": [
                    "In sorted order every copy of a value is contiguous, so if a value appears twice two of its copies are adjacent.",
                    "Conversely, equal neighbours are two different indices with the same value, so a <code>True</code> answer is never wrong.",
                    "Sorting costs <strong>O(n log n)</strong> and the scan O(n). <code>sorted</code> builds a copy, so space is <strong>O(n)</strong>; sorting in place with <code>nums.sort()</code> would make it O(1) extra but modify the caller's list.",
                ],
                "dry": [
                    [
                        "sorted copy: [1, 1, 3, 4, 7, 9].",
                        "i=0: nums[0] = 1 and nums[1] = 1 are equal.",
                        "<code>any</code> stops there and returns <strong>True</strong>.",
                    ],
                    [
                        "sorted copy: [1, 2, 3].",
                        "i=0: 1 vs 2, different. i=1: 2 vs 3, different.",
                        "No equal neighbours, so it returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>range(len(nums) - 1)</code>?",
                     "The last index has no right neighbour; going to <code>len(nums) - 1</code> would make <code>nums[i + 1]</code> raise an IndexError."],
                    ["What about a single-element array?",
                     "<code>range(0)</code> is empty, so <code>any</code> of nothing is <code>False</code>, which is correct."],
                    ["When would I choose this over a set?",
                     "When memory is tight and you are allowed to sort in place, or the values are not hashable but are comparable."],
                ],
            },
            "Hash set, stop at the first repeat": {
                "idea": [
                    "Walk the array once, remembering every value seen so far in a set.",
                    "If the current value is already in the set, it appeared earlier, so there is a duplicate. A set answers that membership question in O(1) on average.",
                ],
                "steps": [
                    "Create an empty set <code>seen</code>.",
                    "For each <code>x</code> in <code>nums</code>:",
                    "if <code>x in seen</code>, return <code>True</code>.",
                    "Otherwise <code>seen.add(x)</code> and continue.",
                    "If the loop ends, every value was new: return <code>False</code>.",
                ],
                "why": [
                    "When the second copy of any value is reached, the first copy is already in <code>seen</code>, so the first repeat is always caught.",
                    "Each element costs one lookup and at most one insert, both O(1) on average, so time is <strong>O(n)</strong>.",
                    "The set can hold up to n values when there is no duplicate: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "x=4: new, seen = {4}. x=1: new, seen = {4, 1}.",
                        "x=7: new. x=3: new. seen = {4, 1, 7, 3}.",
                        "x=1: already in seen.",
                        "It returns <strong>True</strong>; 9 is never read.",
                    ],
                    [
                        "x=3: new, seen = {3}.",
                        "x=1: new, seen = {3, 1}. x=2: new, seen = {3, 1, 2}.",
                        "The loop ends with no repeat, so it returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just <code>len(set(nums)) != len(nums)</code>?",
                     "That is correct and short, but it always builds the full set. The loop stops at the first repeat, which helps when duplicates appear early."],
                    ["Does this work with negative numbers or strings?",
                     "Yes. Any hashable value works; the set does not care about sign or order."],
                    ["Why is the time only O(n) on average?",
                     "Set lookups are O(1) on average. With adversarial keys that all hash to the same slot they degrade, but that does not happen with ordinary integers."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid anagram
    "valid-anagram": {
        "examples": [
            {"call": 'is_anagram("listen", "silent")', "expect": "True"},
            {"call": 'is_anagram("aacc", "ccac")', "expect": "False"},
        ],
        "approaches": {
            "Sort both strings": {
                "idea": [
                    "Two strings are anagrams exactly when they contain the same letters the same number of times.",
                    "Sorting puts the letters of each string in a canonical order, so anagrams become identical sorted lists.",
                ],
                "steps": [
                    "Compute <code>sorted(s)</code>, a list of the characters of <code>s</code> in order.",
                    "Compute <code>sorted(t)</code> the same way.",
                    "Compare the two lists with <code>==</code>.",
                    "Return the result of the comparison.",
                ],
                "why": [
                    "Sorting keeps every character and its multiplicity, and only changes order; equal sorted lists therefore mean equal letter counts, and vice versa.",
                    "Different lengths automatically give different lists, so no separate length check is needed.",
                    "Sorting costs <strong>O(n log n)</strong> time and builds two lists of characters, <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "sorted(\"listen\") = [e, i, l, n, s, t].",
                        "sorted(\"silent\") = [e, i, l, n, s, t].",
                        "The lists are equal, so it returns <strong>True</strong>.",
                    ],
                    [
                        "sorted(\"aacc\") = [a, a, c, c].",
                        "sorted(\"ccac\") = [a, c, c, c].",
                        "They differ at index 1 (a vs c): <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not compare <code>set(s) == set(t)</code>?",
                     "Sets drop multiplicity. \"aacc\" and \"ccac\" both have the set {a, c} but are not anagrams."],
                    ["Does it handle uppercase or Unicode?",
                     "Yes, <code>sorted</code> works on any characters. Whether \"A\" and \"a\" count as equal is a separate decision; normalise with <code>lower()</code> first if needed."],
                    ["Why is this not O(n)?",
                     "Comparison sorting has an n log n lower bound. Counting avoids sorting, which is what the next two approaches do."],
                ],
            },
            "Count with a hash map": {
                "idea": [
                    "Instead of sorting, count letters: add one for each letter of <code>s</code> and subtract one for each letter of <code>t</code>.",
                    "If the strings are anagrams every count returns to zero; any nonzero count is a letter one string has more of.",
                ],
                "steps": [
                    "If <code>len(s) != len(t)</code>, return <code>False</code> at once.",
                    "Create <code>counts = defaultdict(int)</code>.",
                    "Walk both strings together with <code>zip(s, t)</code>: <code>counts[a] += 1</code> and <code>counts[b] -= 1</code>.",
                    "Return <code>all(v == 0 for v in counts.values())</code>.",
                ],
                "why": [
                    "After the loop, <code>counts[c]</code> equals (copies of c in s) − (copies of c in t), so all zeros means equal multiplicities for every letter.",
                    "The length check matters: <code>zip</code> stops at the shorter string, so without it \"a\" vs \"ab\" would look balanced.",
                    "One pass over n positions plus one over the keys gives <strong>O(n)</strong> time; the map has one key per distinct character, <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "Lengths are 6 and 6. Pairs: (l,s), (i,i), (s,l), (t,e), (e,n), (n,t).",
                        "(l,s): l=1, s=−1. (i,i): i=0. (s,l): s=0, l=0.",
                        "(t,e): t=1, e=−1. (e,n): e=0, n=−1. (n,t): n=0, t=0.",
                        "Every count is 0, so it returns <strong>True</strong>.",
                    ],
                    [
                        "Lengths are 4 and 4. Pairs: (a,c), (a,c), (c,a), (c,c).",
                        "After (a,c) twice: a=2, c=−2. After (c,a): a=1, c=−1.",
                        "(c,c) adds and subtracts c: c stays −1.",
                        "a=1 and c=−1 are nonzero, so it returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the early length check?",
                     "<code>zip</code> silently stops at the shorter string. Without the check, \"a\" and \"ab\" would only compare (a, a) and wrongly return <code>True</code>."],
                    ["Can I use <code>Counter(s) == Counter(t)</code>?",
                     "Yes, that is the same idea in one line and also O(n). The manual version shows the single-map, plus-and-minus trick."],
                    ["What is k in O(k)?",
                     "The number of distinct characters. For lowercase English letters it is at most 26, which is why the next approach uses a fixed array."],
                ],
            },
            "Fixed array of 26 counters": {
                "idea": [
                    "When the input is only lowercase letters, the hash map can be replaced by a plain list of 26 counters indexed by letter.",
                    "<code>ord(ch) - 97</code> maps 'a' to 0, 'b' to 1, …, 'z' to 25.",
                ],
                "steps": [
                    "If the lengths differ, return <code>False</code>.",
                    "Create <code>counts = [0] * 26</code>.",
                    "For each pair <code>(a, b)</code> from <code>zip(s, t)</code>: <code>counts[ord(a) - 97] += 1</code> and <code>counts[ord(b) - 97] -= 1</code>.",
                    "Return <code>not any(counts)</code>: true only if every counter is 0.",
                ],
                "why": [
                    "Same argument as the hash map: each counter ends as the difference in multiplicity of its letter, so all zeros means anagrams.",
                    "The scan is <strong>O(n)</strong> time, and <code>any</code> over 26 cells is constant.",
                    "The list always has 26 cells regardless of input size, so space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "counts starts as 26 zeros.",
                        "(l,s): counts[11] = 1, counts[18] = −1. (i,i): counts[8] goes +1 then −1.",
                        "The remaining pairs bring l, s, t, e and n back to 0 in the same way as the hash map trace.",
                        "<code>any(counts)</code> is False, so it returns <strong>True</strong>.",
                    ],
                    [
                        "(a,c) twice: counts[0] = 2, counts[2] = −2.",
                        "(c,a): counts[0] = 1, counts[2] = −1. (c,c): counts[2] stays −1.",
                        "<code>any(counts)</code> is True, so it returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["What happens with uppercase letters?",
                     "The index goes wrong. 'A' gives −32, which raises IndexError, but 'Z' gives −7, which silently wraps to index 19 ('t'), so <code>is_anagram(\"Z\", \"t\")</code> returns <code>True</code>. Use the hash map for general input."],
                    ["Why <code>not any(counts)</code>?",
                     "<code>any</code> is true if some counter is nonzero. Negating it gives true exactly when all 26 counters are zero."],
                    ["Is this really faster than the dictionary?",
                     "List indexing avoids hashing, so the constant factor is smaller, but both are O(n). The real gain is the guaranteed O(1) space."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ two sum
    "two-sum": {
        "examples": [
            {"call": "two_sum([3, 9, 2, 7, 5], 9)", "expect": "[2, 3]"},
            {"call": "two_sum([3, 3], 6)", "expect": "[0, 1]"},
        ],
        "approaches": {
            "Check every pair": {
                "idea": [
                    "The answer is two different indices whose values add up to <code>target</code>, so try every pair <code>i &lt; j</code>.",
                    "The problem guarantees exactly one solution, so the first matching pair is the answer.",
                ],
                "steps": [
                    "Loop <code>i</code> over every index.",
                    "Loop <code>j</code> from <code>i + 1</code> to the end.",
                    "If <code>nums[i] + nums[j] == target</code>, return <code>[i, j]</code>.",
                    "Otherwise keep going; the guarantee means the loops never run out.",
                ],
                "why": [
                    "Every pair of distinct indices is visited once, so the solution pair cannot be skipped.",
                    "Because <code>j &gt; i</code>, the same element is never used twice and the result is already in increasing order.",
                    "Up to n(n − 1)/2 pairs are summed: <strong>O(n²)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (3): sums with 9, 2, 7, 5 are 12, 5, 10, 8. None is 9.",
                        "i=1 (9): sums with 2, 7, 5 are 11, 16, 14.",
                        "i=2 (2): j=3 (7) gives 9.",
                        "It returns <strong>[2, 3]</strong>.",
                    ],
                    [
                        "i=0 (3): j=1 (3) gives 6.",
                        "It returns <strong>[0, 1]</strong>.",
                        "The two equal values are different indices, which is allowed.",
                    ],
                ],
                "faq": [
                    ["What does it return if there is no answer?",
                     "The function falls off the end and returns <code>None</code>. The problem guarantees an answer, so that never happens in the tests."],
                    ["Why can't <code>j</code> start at <code>i</code>?",
                     "Then <code>nums[i] + nums[i]</code> would be tried, using one element twice, e.g. returning [0, 0] for target 6 in [3, 2, 4]."],
                    ["Why mention the quadratic version?",
                     "It is the obvious correct baseline. In an interview, state it with its cost and move to the hash map."],
                ],
            },
            "Sort indices, two pointers": {
                "idea": [
                    "On a sorted array, two pointers from both ends find a pair with a given sum: too small moves the left pointer up, too large moves the right one down.",
                    "Sorting the values would lose the original indices, so sort the <em>indices</em> by value instead: <code>order</code>.",
                ],
                "steps": [
                    "Build <code>order = sorted(range(len(nums)), key=nums.__getitem__)</code>, the indices in increasing value.",
                    "Set <code>lo = 0</code> and <code>hi = len(order) - 1</code>.",
                    "While <code>lo &lt; hi</code>, compute <code>total = nums[order[lo]] + nums[order[hi]]</code>.",
                    "If <code>total == target</code>, return <code>sorted([order[lo], order[hi]])</code>.",
                    "If <code>total &lt; target</code>, move <code>lo</code> up; otherwise move <code>hi</code> down.",
                ],
                "why": [
                    "If <code>total</code> is too small, the value at <code>lo</code> cannot pair with anything left of <code>hi</code> either (those are even smaller), so dropping it is safe; the mirror argument covers <code>hi</code>.",
                    "Each step discards one index, so the scan is O(n); the sort dominates at <strong>O(n log n)</strong> time.",
                    "<code>order</code> holds n indices: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "order = [2, 0, 4, 3, 1], i.e. values [2, 3, 5, 7, 9].",
                        "lo=0, hi=4: 2 + 9 = 11 &gt; 9, so hi = 3.",
                        "lo=0, hi=3: 2 + 7 = 9, a match. The indices are order[0] = 2 and order[3] = 3.",
                        "It returns <strong>[2, 3]</strong>.",
                    ],
                    [
                        "order = [0, 1] (both values are 3; the stable sort keeps index order).",
                        "lo=0, hi=1: 3 + 3 = 6, a match.",
                        "It returns <strong>[0, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort indices instead of values?",
                     "The answer must be original positions. Sorting the values would tell you which numbers work but not where they were."],
                    ["Why return <code>sorted([order[lo], order[hi]])</code>?",
                     "The smaller value is not necessarily at the smaller index, as in the first example where value 2 sits after value 3. Sorting gives a consistent [smaller, larger] answer."],
                    ["When is this better than the hash map?",
                     "When the array is already sorted (then it is O(n) time and O(1) space) or when you need all pairs in order."],
                ],
            },
            "One-pass hash map": {
                "idea": [
                    "For each value <code>x</code>, the partner it needs is <code>target - x</code>. If that partner appeared earlier, the pair is found.",
                    "A dictionary from value to index answers \"have I seen this value, and where?\" in O(1).",
                ],
                "steps": [
                    "Create an empty dict <code>index</code>.",
                    "Loop <code>i, x</code> over <code>enumerate(nums)</code>.",
                    "If <code>target - x</code> is in <code>index</code>, return <code>[index[target - x], i]</code>.",
                    "Otherwise store <code>index[x] = i</code>.",
                    "Checking before storing means <code>x</code> can never pair with itself.",
                ],
                "why": [
                    "When the loop reaches the right-hand element of the solution pair, the left-hand element is already in <code>index</code>, so the pair is always found.",
                    "Each element does one lookup and one insert, O(1) on average: <strong>O(n)</strong> time.",
                    "The dictionary may store up to n − 1 values before the answer: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0, x=3: need 6, not seen. index = {3: 0}.",
                        "i=1, x=9: need 0, not seen. index = {3: 0, 9: 1}.",
                        "i=2, x=2: need 7, not seen. index adds 2: 2.",
                        "i=3, x=7: need 2, found at index 2.",
                        "It returns <strong>[2, 3]</strong>.",
                    ],
                    [
                        "i=0, x=3: need 3, not seen yet. index = {3: 0}.",
                        "i=1, x=3: need 3, found at 0.",
                        "It returns <strong>[0, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check before inserting?",
                     "If <code>x</code> were inserted first, a value equal to <code>target / 2</code> would find itself and return the same index twice."],
                    ["What if a value repeats and is not part of the answer?",
                     "The later index overwrites the earlier one. That is harmless because only one solution exists."],
                    ["Why is the returned pair already in order?",
                     "The stored index comes from an earlier iteration, so it is always smaller than <code>i</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest common prefix
    "longest-common-prefix": {
        "examples": [
            {"call": 'longest_common_prefix(["flower", "flow", "flight"])', "expect": '"fl"'},
            {"call": 'longest_common_prefix(["dog", "racecar", "car"])', "expect": '""'},
        ],
        "approaches": {
            "Horizontal scan: shrink the prefix string by string": {
                "idea": [
                    "The common prefix of all words can only shrink as more words are considered, and it starts as the whole first word.",
                    "For each next word, chop characters off the end of the current prefix until the word starts with it.",
                ],
                "steps": [
                    "Set <code>prefix = strs[0]</code>.",
                    "For each <code>word</code> in <code>strs[1:]</code>:",
                    "while <code>not word.startswith(prefix)</code>, drop the last character with <code>prefix = prefix[:-1]</code>.",
                    "The empty string is a prefix of everything, so the inner loop always stops.",
                    "Return <code>prefix</code> after all words.",
                ],
                "why": [
                    "After processing word k, <code>prefix</code> is the longest common prefix of the first k + 1 words, because it was the longest one for the first k and was cut only as far as needed for the new word.",
                    "Each character of the first word is removed at most once overall, and each <code>startswith</code> call reads at most that many characters, so the total work is bounded by the input size S: <strong>O(S)</strong> time.",
                    "Slicing builds new strings, but only one prefix is alive at a time; beyond that the extra space is <strong>O(1)</strong> as the problem states it.",
                ],
                "dry": [
                    [
                        "prefix = \"flower\".",
                        "word \"flow\": not a prefix, cut to \"flowe\", then \"flow\". Now it matches.",
                        "word \"flight\": cut to \"flo\", then \"fl\". \"flight\" starts with \"fl\".",
                        "It returns <strong>\"fl\"</strong>.",
                    ],
                    [
                        "prefix = \"dog\".",
                        "word \"racecar\": cut to \"do\", \"d\", then \"\". Every word starts with the empty string.",
                        "word \"car\": \"\" already matches, nothing to cut.",
                        "It returns <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Can the inner <code>while</code> loop run forever?",
                     "No. Once <code>prefix</code> is \"\", <code>word.startswith(\"\")</code> is always true."],
                    ["Should I stop early once the prefix is empty?",
                     "That is a cheap optimisation: add <code>if not prefix: break</code>. The answer does not change, only the remaining words are skipped."],
                    ["Does the order of words matter?",
                     "Not for the result. It can affect speed: a short word early shrinks the prefix quickly."],
                ],
            },
            "Vertical scan: one column at a time": {
                "idea": [
                    "Read the words column by column: check position 0 of every word, then position 1, and so on.",
                    "The first column where some word is too short or has a different character ends the prefix.",
                ],
                "steps": [
                    "Loop <code>i, ch</code> over the characters of <code>strs[0]</code>.",
                    "For every other <code>word</code>, check <code>i == len(word) or word[i] != ch</code>.",
                    "If that is true, return <code>strs[0][:i]</code>, the part before this column.",
                    "If every column of the first word matches in all words, return <code>strs[0]</code>.",
                ],
                "why": [
                    "Column i is reached only if columns 0..i−1 matched everywhere, so <code>strs[0][:i]</code> is common to all words, and column i proves it cannot be longer.",
                    "The length test comes first, so <code>word[i]</code> is never read past the end.",
                    "It stops at the first mismatch, reading at most n · m characters (m = length of the answer + 1): <strong>O(n · m)</strong> time, <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "i=0, ch='f': \"flow\" and \"flight\" both have 'f'.",
                        "i=1, ch='l': both have 'l'.",
                        "i=2, ch='o': \"flow\" has 'o', but \"flight\" has 'i'.",
                        "It returns <strong>\"fl\"</strong>.",
                    ],
                    [
                        "Only the characters of \"dog\" drive the outer loop.",
                        "i=0, ch='d': \"racecar\" has 'r', a mismatch; \"car\" is never looked at.",
                        "It returns <code>strs[0][:0]</code> = <strong>\"\"</strong>, after a single comparison.",
                    ],
                ],
                "faq": [
                    ["Why check <code>i == len(word)</code> before <code>word[i]</code>?",
                     "A shorter word such as \"a\" in [\"ab\", \"a\"] runs out at i = 1. The <code>or</code> short-circuits, so the index is never read."],
                    ["Why is vertical often faster than horizontal?",
                     "It stops as soon as any word disagrees, so a very short or very different word ends the scan immediately."],
                    ["What if <code>strs[0]</code> is the shortest word?",
                     "Then the loop simply ends after its last character and returns <code>strs[0]</code> whole, which is correct if every other word starts with it."],
                ],
            },
            "Sort, compare first and last": {
                "idea": [
                    "In lexicographic order, the smallest and largest strings are the most different; whatever prefix they share, every string between them shares too.",
                    "The code does not actually sort: <code>min</code> and <code>max</code> find those two strings directly.",
                ],
                "steps": [
                    "Set <code>first, last = min(strs), max(strs)</code>.",
                    "Set <code>i = 0</code>.",
                    "While <code>i</code> is inside both strings and <code>first[i] == last[i]</code>, increase <code>i</code>.",
                    "Return <code>first[:i]</code>.",
                ],
                "why": [
                    "Any string s with first ≤ s ≤ last must agree with both on their common prefix; otherwise it would sort before <code>first</code> or after <code>last</code>.",
                    "So the common prefix of <code>first</code> and <code>last</code> is the common prefix of all strings.",
                    "<code>min</code> and <code>max</code> make one pass each over the strings, comparing character by character, so the time is bounded by the total size S. The label says <strong>O(S log n)</strong>, which is the cost if you really sort; extra space is <strong>O(1)</strong> here, or O(n) for a sorted copy.",
                ],
                "dry": [
                    [
                        "min = \"flight\", max = \"flower\".",
                        "i=0: 'f' = 'f'. i=1: 'l' = 'l'.",
                        "i=2: 'i' vs 'o' differ, stop.",
                        "It returns <strong>\"fl\"</strong>.",
                    ],
                    [
                        "min = \"car\", max = \"racecar\".",
                        "i=0: 'c' vs 'r' differ, stop.",
                        "It returns <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does comparing only two strings suffice?",
                     "Lexicographic order sorts by the first differing character. A string that differs from the shared prefix of min and max would land outside the range [min, max], which is impossible."],
                    ["What happens with an empty string in the list?",
                     "\"\" is the minimum, so <code>first</code> is \"\" and the loop exits at once, returning \"\"."],
                    ["Why do the while conditions check both lengths?",
                     "<code>first</code> is often a prefix of <code>last</code> (e.g. \"a\" and \"ab\"), so the loop must stop at the end of the shorter one before indexing."],
                ],
            },
        },
    },


    # ------------------------------------------------------------------ group anagrams
    "group-anagrams": {
        "examples": [
            {"call": 'sorted(sorted(g) for g in group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))',
             "expect": '[["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]'},
            {"call": 'sorted(sorted(g) for g in group_anagrams(["", "b", ""]))', "expect": '[["", ""], ["b"]]'},
        ],
        "approaches": {
            "Compare every pair with an anagram check": {
                "idea": [
                    "Take each word that is not yet in a group, start a new group with it, and pull in every later word that is its anagram.",
                    "A <code>used</code> flag per word stops a word from being placed in two groups.",
                    "The anagram test is <code>Counter(strs[j]) == key</code>, guarded by a cheap length check.",
                ],
                "steps": [
                    "Create <code>groups = []</code> and <code>used = [False] * len(strs)</code>.",
                    "Loop <code>i, w</code> over the words; skip <code>w</code> if <code>used[i]</code>.",
                    "Start <code>group = [w]</code> and compute <code>key = Counter(w)</code>.",
                    "For every later <code>j</code> not yet used with the same length and <code>Counter(strs[j]) == key</code>, set <code>used[j] = True</code> and append it.",
                    "Append <code>group</code> to <code>groups</code>; return <code>groups</code> at the end.",
                ],
                "why": [
                    "Being an anagram is an equivalence relation, so all words anagram to the group's first word are also anagrams of each other; one leader per group is enough.",
                    "Every word is either a leader or marked used by exactly one leader, so each lands in exactly one group.",
                    "With m words of length up to k there are O(m²) pairs, each needing an O(k) Counter: <strong>O(m² · k)</strong> time. <code>used</code> and the groups take <strong>O(m)</strong> space beyond the Counters.",
                ],
                "dry": [
                    [
                        "i=0 \"eat\": key {e,a,t}. \"tea\" matches, \"tan\" no, \"ate\" matches, \"nat\" no, \"bat\" no. Group [eat, tea, ate].",
                        "i=1 \"tea\": used, skip.",
                        "i=2 \"tan\": \"nat\" matches. Group [tan, nat]. i=3 and i=4 are used.",
                        "i=5 \"bat\": nothing after it. Group [bat].",
                        "After normalising: <strong>[[\"ate\", \"eat\", \"tea\"], [\"bat\"], [\"nat\", \"tan\"]]</strong>.",
                    ],
                    [
                        "i=0 \"\": key is an empty Counter. \"b\" has length 1, skipped by the length check.",
                        "\"\" at index 2 has length 0 and an equal (empty) Counter, so it joins. Group [\"\", \"\"].",
                        "i=1 \"b\": group [\"b\"]. i=2 is used.",
                        "After normalising: <strong>[[\"\", \"\"], [\"b\"]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the length check before comparing Counters?",
                     "Words of different lengths can never be anagrams, and comparing lengths is O(1), so it skips most expensive Counter builds."],
                    ["Why not compare each word with every group's leader instead?",
                     "That is the same idea organised differently and has the same quadratic worst case when all words are distinct."],
                    ["Why sort the groups in the example call?",
                     "The problem allows groups and words in any order. Sorting both makes the expected answer unique across all approaches."],
                ],
            },
            "Sorted word as the key": {
                "idea": [
                    "All anagrams of a word sort to the same string, so the sorted letters make a perfect <em>signature</em>.",
                    "Use that signature as a dictionary key and drop each word into its bucket: grouping becomes one pass.",
                ],
                "steps": [
                    "Create <code>groups = defaultdict(list)</code>.",
                    "For each word <code>w</code>, compute the key <code>\"\".join(sorted(w))</code>.",
                    "Append <code>w</code> to <code>groups[key]</code>; a new key starts an empty list automatically.",
                    "Return <code>list(groups.values())</code>.",
                ],
                "why": [
                    "Two words get the same key exactly when they have the same multiset of letters, i.e. exactly when they are anagrams.",
                    "Sorting each word costs O(k log k), done m times: <strong>O(m · k log k)</strong> time.",
                    "The keys and the grouped words together hold every character a constant number of times: <strong>O(m · k)</strong> space.",
                ],
                "dry": [
                    [
                        "\"eat\" → key \"aet\". \"tea\" → \"aet\". \"tan\" → \"ant\".",
                        "\"ate\" → \"aet\". \"nat\" → \"ant\". \"bat\" → \"abt\".",
                        "groups = {aet: [eat, tea, ate], ant: [tan, nat], abt: [bat]}.",
                        "After normalising: <strong>[[\"ate\", \"eat\", \"tea\"], [\"bat\"], [\"nat\", \"tan\"]]</strong>.",
                    ],
                    [
                        "\"\" → key \"\". \"b\" → key \"b\". \"\" → key \"\" again.",
                        "groups = {\"\": [\"\", \"\"], \"b\": [\"b\"]}.",
                        "After normalising: <strong>[[\"\", \"\"], [\"b\"]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why join the sorted letters into a string?",
                     "<code>sorted(w)</code> is a list, and lists are not hashable, so they cannot be dict keys. A string (or a tuple) can."],
                    ["Is the empty string handled?",
                     "Yes. It sorts to \"\", which is a valid key, so all empty strings group together."],
                    ["When is this better than the count key?",
                     "When words are short or the alphabet is large; for long lowercase words the 26-count key avoids the log factor."],
                ],
            },
            "Letter-count tuple as the key": {
                "idea": [
                    "Another signature that anagrams share is the count of each letter a..z.",
                    "Build a 26-slot count list for each word and use it, as a tuple, as the dictionary key. No sorting needed.",
                ],
                "steps": [
                    "Create <code>groups = defaultdict(list)</code>.",
                    "For each word <code>w</code>, make <code>counts = [0] * 26</code>.",
                    "For each character, do <code>counts[ord(ch) - 97] += 1</code>.",
                    "Append <code>w</code> to <code>groups[tuple(counts)]</code>.",
                    "Return <code>list(groups.values())</code>.",
                ],
                "why": [
                    "Two lowercase words have equal count vectors exactly when they are anagrams, so the key groups correctly.",
                    "Each word takes O(k) to count plus O(26) to build the tuple: <strong>O(m · k)</strong> time overall.",
                    "Each key is 26 integers and the groups hold all the words: <strong>O(m · k)</strong> space (O(26 · m) for the keys).",
                ],
                "dry": [
                    [
                        "\"eat\": counts a=1, e=1, t=1. \"tea\" and \"ate\" give the same tuple.",
                        "\"tan\" and \"nat\": a=1, n=1, t=1, a second key.",
                        "\"bat\": a=1, b=1, t=1, a third key.",
                        "After normalising: <strong>[[\"ate\", \"eat\", \"tea\"], [\"bat\"], [\"nat\", \"tan\"]]</strong>.",
                    ],
                    [
                        "\"\": all 26 counts are 0.",
                        "\"b\": counts[1] = 1, a different key. The second \"\" matches the all-zero key.",
                        "After normalising: <strong>[[\"\", \"\"], [\"b\"]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why convert <code>counts</code> to a tuple?",
                     "Lists are mutable and unhashable, so they cannot be dictionary keys. A tuple of the same numbers can."],
                    ["Does it work for uppercase or non-English letters?",
                     "No. <code>ord(ch) - 97</code> assumes 'a'..'z'. For general text, use a <code>Counter</code> frozen into a sorted tuple of items, or the sorted-word key."],
                    ["Is O(m · k) really better than O(m · k log k)?",
                     "Asymptotically yes, but each key costs 26 slots, so for very short words the sorted-string key is often just as fast in practice."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ remove element
    "remove-element": {
        "examples": [
            {"setup": "a = [0, 1, 2, 2, 3, 0, 4, 2]\nk = remove_element(a, 2)", "call": "[k, sorted(a[:k])]", "expect": "[5, [0, 0, 1, 3, 4]]"},
            {"setup": "a = [2, 2]\nk = remove_element(a, 2)", "call": "[k, a[:k]]", "expect": "[0, []]"},
        ],
        "approaches": {
            "Build a filtered copy, write it back": {
                "idea": [
                    "Collect the values to keep into a new list, then copy them over the front of <code>nums</code>.",
                    "The judge only reads the first k slots, so whatever is left after them does not matter.",
                ],
                "steps": [
                    "Build <code>kept = [x for x in nums if x != val]</code>.",
                    "Assign <code>nums[:len(kept)] = kept</code>, overwriting the first <code>len(kept)</code> slots in place.",
                    "The slice has the same length as <code>kept</code>, so the list's length does not change.",
                    "Return <code>len(kept)</code>.",
                ],
                "why": [
                    "<code>kept</code> contains exactly the elements not equal to <code>val</code>, in order, and they now occupy positions 0..k−1.",
                    "One pass to filter and one to copy: <strong>O(n)</strong> time.",
                    "<code>kept</code> can be as large as <code>nums</code>: <strong>O(n)</strong> extra space, which breaks the usual in-place requirement.",
                ],
                "dry": [
                    [
                        "kept = [0, 1, 3, 0, 4] (the three 2s are dropped).",
                        "nums[:5] = kept, so a = [0, 1, 3, 0, 4, 0, 4, 2]. The tail is left over and ignored.",
                        "It returns k = 5; sorted(a[:5]) = [0, 0, 1, 3, 4].",
                        "Result: <strong>[5, [0, 0, 1, 3, 4]]</strong>.",
                    ],
                    [
                        "kept = [] because both elements equal 2.",
                        "nums[:0] = [] changes nothing.",
                        "It returns k = 0: <strong>[0, []]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not <code>nums = kept</code>?",
                     "That only rebinds the local name. The caller's list would be unchanged, and the judge checks the caller's list."],
                    ["Does <code>nums[:len(kept)] = kept</code> shrink the list?",
                     "No. A slice assignment with equal lengths replaces elements one for one; the tail stays where it is."],
                    ["Why mention this if it uses O(n) memory?",
                     "It is the clearest correct version and a good reference; the next approach does the same thing without the copy."],
                ],
            },
            "Read and write pointers": {
                "idea": [
                    "Walk the array with a read pointer and keep a write pointer <code>k</code> marking where the next kept value goes.",
                    "Every value that is not <code>val</code> is copied to <code>nums[k]</code>; values equal to <code>val</code> are simply skipped.",
                ],
                "steps": [
                    "Set <code>k = 0</code>.",
                    "For each <code>x</code> in <code>nums</code> (the read pointer):",
                    "if <code>x != val</code>, write <code>nums[k] = x</code> and increase <code>k</code>.",
                    "Values equal to <code>val</code> do nothing, so <code>k</code> falls behind the read position.",
                    "Return <code>k</code>.",
                ],
                "why": [
                    "Invariant: <code>nums[:k]</code> always holds the kept values read so far, in order. The write never overtakes the read, so no unread value is overwritten.",
                    "Each element is read once and written at most once: <strong>O(n)</strong> time.",
                    "Only <code>k</code> is stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "x=0: keep, nums[0]=0, k=1. x=1: keep, nums[1]=1, k=2.",
                        "x=2, x=2: skipped, k stays 2.",
                        "x=3: nums[2]=3, k=3. x=0: nums[3]=0, k=4. x=4: nums[4]=4, k=5. x=2: skipped.",
                        "a[:5] = [0, 1, 3, 0, 4], so the result is <strong>[5, [0, 0, 1, 3, 4]]</strong>.",
                    ],
                    [
                        "x=2: skipped. x=2: skipped.",
                        "k never moves from 0.",
                        "Result: <strong>[0, []]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is it safe to iterate over <code>nums</code> while writing into it?",
                     "Yes here, because the list length never changes and writes only go to index <code>k</code>, which is at or behind the element being read."],
                    ["Does it keep the original order?",
                     "Yes. Kept values are written in the order they are read."],
                    ["How many writes does it do?",
                     "One per kept element, even when nothing needs to move. The swap-with-end approach writes only once per removed element."],
                ],
            },
            "Swap with the end when removals are rare": {
                "idea": [
                    "When <code>val</code> is rare, shifting every kept element is wasteful. Instead, overwrite a bad element with the <em>last</em> element and shrink the array by one.",
                    "Order is not preserved, which the problem allows.",
                ],
                "steps": [
                    "Set <code>i = 0</code> and <code>n = len(nums)</code>; <code>n</code> is the current logical length.",
                    "While <code>i &lt; n</code>: if <code>nums[i] == val</code>, copy <code>nums[n - 1]</code> into slot <code>i</code> and do <code>n -= 1</code>.",
                    "Do not advance <code>i</code> in that case: the value just moved in has not been checked yet.",
                    "Otherwise <code>nums[i]</code> is good, so <code>i += 1</code>.",
                    "Return <code>n</code>.",
                ],
                "why": [
                    "Invariant: <code>nums[:i]</code> holds only good values and <code>nums[i:n]</code> is still unchecked. Each step either grows the good part or shrinks the unchecked part.",
                    "Each iteration moves <code>i</code> up or <code>n</code> down, so there are at most n iterations: <strong>O(n)</strong> time, with one write per removed element.",
                    "Only <code>i</code> and <code>n</code> are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (0), i=1 (1): good, i=2.",
                        "i=2 holds 2: copy nums[7]=2 in, n=7. Still 2: copy nums[6]=4 in, n=6.",
                        "i=2 now 4: good, i=3. i=3 holds 2: copy nums[5]=0 in, n=5.",
                        "i=3 (0) and i=4 (3) are good; i=5 = n stops. a[:5] = [0, 1, 4, 0, 3].",
                        "Result: <strong>[5, [0, 0, 1, 3, 4]]</strong>.",
                    ],
                    [
                        "i=0 holds 2: copy nums[1] into slot 0, n=1.",
                        "i=0 still holds 2: copy nums[0] onto itself, n=0.",
                        "i=0 is not &lt; 0, so the loop ends. Result: <strong>[0, []]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not increase <code>i</code> after a swap?",
                     "The value copied from the end might itself be <code>val</code>, as in the first example where a 2 replaced a 2. It must be checked before moving on."],
                    ["Why <code>nums[n - 1]</code> and not <code>nums[-1]</code>?",
                     "The physical end of the list never changes; <code>n - 1</code> is the last <em>unchecked</em> slot, which shrinks after each removal."],
                    ["When is this better than read/write pointers?",
                     "When few elements equal <code>val</code>: it does only one write per removal instead of one per kept element."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ majority element
    "majority-element": {
        "examples": [
            {"call": "majority_element([2, 2, 1, 1, 1, 2, 2])", "expect": "2"},
            {"call": "majority_element([6, 5, 5])", "expect": "5"},
        ],
        "approaches": {
            "Count each candidate": {
                "idea": [
                    "The majority element appears more than <code>n // 2</code> times. Test each element in turn by counting it.",
                    "The first element whose count passes the threshold is the answer.",
                ],
                "steps": [
                    "Loop <code>x</code> over <code>nums</code>.",
                    "Count it with <code>nums.count(x)</code>, a full scan of the list.",
                    "If the count is greater than <code>len(nums) // 2</code>, return <code>x</code>.",
                    "Otherwise try the next element; a majority is guaranteed to exist.",
                ],
                "why": [
                    "The majority element appears somewhere in <code>nums</code>, so the loop reaches it and its count passes the test. No other value can pass, since two values cannot both exceed half.",
                    "Each <code>count</code> is O(n), done up to n times: <strong>O(n²)</strong> time.",
                    "No extra structures: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n // 2 = 3.",
                        "x=2 (index 0): nums.count(2) = 4.",
                        "4 &gt; 3, so it returns <strong>2</strong> on the first try.",
                    ],
                    [
                        "n // 2 = 1.",
                        "x=6: count 1, not &gt; 1.",
                        "x=5: count 2 &gt; 1, so it returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt; len(nums) // 2</code> and not <code>&gt;=</code>?",
                     "Majority means strictly more than half. With n = 4, a value appearing exactly 2 times is not a majority; <code>&gt;=</code> would accept it."],
                    ["When does this hit the quadratic worst case?",
                     "When the majority's first occurrence comes late, so many minority values are counted first, each at full O(n) cost."],
                    ["What if there were no majority?",
                     "The loop would end and the function would return <code>None</code>. The problem guarantees one exists."],
                ],
            },
            "Hash map of counts": {
                "idea": [
                    "Count every value once with a <code>Counter</code>, then return the value with the highest count.",
                    "Since a majority exists, the most frequent value is the majority.",
                ],
                "steps": [
                    "Build <code>counts = Counter(nums)</code> in one pass.",
                    "Pick <code>max(counts, key=counts.get)</code>: the key with the largest count.",
                    "Return it.",
                    "No threshold test is needed because the majority is guaranteed.",
                ],
                "why": [
                    "The majority's count exceeds n/2, so every other value has fewer than n/2 occurrences; the maximum is unique and is the majority.",
                    "Counting is O(n) and the max over at most n keys is O(n): <strong>O(n)</strong> time.",
                    "The Counter holds one entry per distinct value: <strong>O(n)</strong> space in the worst case.",
                ],
                "dry": [
                    [
                        "counts = {2: 4, 1: 3}.",
                        "max by count compares 4 and 3.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "counts = {6: 1, 5: 2}.",
                        "max by count picks 5.",
                        "It returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>key=counts.get</code>?",
                     "<code>max(counts)</code> alone would compare the keys themselves (the values in <code>nums</code>), not their counts."],
                    ["Could I use <code>counts.most_common(1)[0][0]</code>?",
                     "Yes, it returns the same thing and is equally O(n) for one item."],
                    ["Can there be a tie for the maximum?",
                     "Not when a majority exists: one value has more than half, so all others together have less than half."],
                ],
            },
            "Sort, take the middle": {
                "idea": [
                    "A value occupying more than half the positions must cover the middle index once the array is sorted.",
                    "So sort and read <code>sorted(nums)[len(nums) // 2]</code>.",
                ],
                "steps": [
                    "Sort a copy with <code>sorted(nums)</code>.",
                    "Compute the middle index <code>len(nums) // 2</code>.",
                    "Return the element at that index.",
                    "No counting is needed.",
                ],
                "why": [
                    "In sorted order the majority forms one contiguous run longer than n/2. Wherever that run starts, it cannot end before the middle index, and it cannot start after it.",
                    "Sorting dominates: <strong>O(n log n)</strong> time.",
                    "<code>sorted</code> makes a copy: <strong>O(n)</strong> space (O(1) extra with <code>nums.sort()</code>, at the cost of mutating the input).",
                ],
                "dry": [
                    [
                        "sorted = [1, 1, 1, 2, 2, 2, 2].",
                        "middle index = 7 // 2 = 3.",
                        "sorted[3] = 2, so it returns <strong>2</strong>.",
                    ],
                    [
                        "sorted = [5, 5, 6].",
                        "middle index = 3 // 2 = 1.",
                        "sorted[1] = 5, so it returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Does it work for even n?",
                     "Yes. With n = 4 the majority appears at least 3 times, so it covers index 2 whether it is the smallest or largest value."],
                    ["Would <code>(len(nums) - 1) // 2</code> work too?",
                     "Yes: for even n that is the lower middle, and a run longer than n/2 covers both middles."],
                    ["Why not use this in practice?",
                     "It pays O(n log n) for a question that counting or Boyer-Moore answers in O(n)."],
                ],
            },
            "Boyer-Moore voting": {
                "idea": [
                    "Pair each occurrence of the majority with a different value and cancel both. Because the majority has more than half, some copies survive.",
                    "The code does this cancelling on the fly with one <code>candidate</code> and a <code>votes</code> counter.",
                ],
                "steps": [
                    "Start with <code>candidate = None</code> and <code>votes = 0</code>.",
                    "For each <code>x</code>: if <code>votes == 0</code>, make <code>x</code> the new <code>candidate</code>.",
                    "Then add one vote if <code>x == candidate</code>, otherwise subtract one.",
                    "Return <code>candidate</code> after the loop.",
                ],
                "why": [
                    "Each time <code>votes</code> drops to 0, the prefix read so far splits into pairs of different values, so the majority still holds a majority in the rest of the array.",
                    "Applied to the final stretch, that means the last surviving candidate is the majority.",
                    "One pass and two variables: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "2: candidate 2, votes 1. 2: votes 2. 1: votes 1. 1: votes 0.",
                        "1: votes is 0, so candidate 1, votes 1.",
                        "2: votes 0. 2: votes is 0, so candidate 2, votes 1.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "6: candidate 6, votes 1.",
                        "5: different, votes 0.",
                        "5: votes is 0, so candidate 5, votes 1.",
                        "It returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Does the final <code>votes</code> equal the majority's count?",
                     "No. It is only the surplus left after cancelling; the first example ends with votes 1 although 2 appears 4 times."],
                    ["What if no majority is guaranteed?",
                     "The algorithm still returns some value, which may be wrong. Verify with a second pass using <code>nums.count(candidate)</code>."],
                    ["Why reset the candidate only when <code>votes == 0</code>?",
                     "A positive vote count means the current candidate still has unmatched copies; switching then would throw those away."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ design hashset
    "design-hashset": {
        "examples": [
            {"setup": "s = MyHashSet()\nfor key in (1, 2, 10008):\n    s.add(key)",
             "call": "[s.contains(1), s.contains(10008), s.contains(3), s.remove(2) or s.contains(2)]",
             "expect": "[True, True, False, False]"},
            {"setup": "s = MyHashSet()\ns.add(5)\ns.add(5)\ns.remove(5)",
             "call": "[s.contains(5), s.remove(7) or s.contains(7)]", "expect": "[False, False]"},
        ],
        "approaches": {
            "Direct-address boolean array": {
                "idea": [
                    "Keys are limited to 0..10<sup>6</sup>, so give every possible key its own slot and store whether it is present.",
                    "The key <em>is</em> the index, so no hashing or collision handling is needed.",
                ],
                "steps": [
                    "In <code>__init__</code>, allocate <code>self.present = [False] * (10 ** 6 + 1)</code>.",
                    "<code>add(key)</code>: set <code>self.present[key] = True</code>.",
                    "<code>remove(key)</code>: set <code>self.present[key] = False</code>; removing an absent key is a harmless no-op.",
                    "<code>contains(key)</code>: return <code>self.present[key]</code>.",
                ],
                "why": [
                    "Each key maps to a unique index, so two keys never interfere and the flag is exactly membership.",
                    "Every operation is one list index: <strong>O(1) per operation</strong>.",
                    "The array has one slot per possible key, <strong>O(key range)</strong> space (about a million entries) no matter how few keys are stored.",
                ],
                "dry": [
                    [
                        "add 1, 2, 10008 sets present[1], present[2], present[10008] to True.",
                        "contains(1) and contains(10008) read True; contains(3) reads False.",
                        "remove(2) returns None, so <code>or</code> evaluates contains(2): False.",
                        "Result: <strong>[True, True, False, False]</strong>.",
                    ],
                    [
                        "add(5) twice sets present[5] = True twice; the second write changes nothing.",
                        "remove(5) sets it back to False, so contains(5) is False.",
                        "remove(7) on an absent key writes False over False; contains(7) is False.",
                        "Result: <strong>[False, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>10 ** 6 + 1</code> slots?",
                     "Keys go up to and including 10<sup>6</sup>, so indices 0..10<sup>6</sup> are needed, which is one more than a million."],
                    ["Why does adding twice and removing once leave it absent?",
                     "A set has no multiplicity. The flag is either True or False, so one remove clears it."],
                    ["When is this a bad design?",
                     "When the key range is huge or unknown (e.g. 64-bit integers or strings). Then a real hash table is required."],
                ],
            },
            "Separate chaining with buckets": {
                "idea": [
                    "Use a fixed number of buckets, <code>B = 10007</code> (a prime), and put each key in bucket <code>key % B</code>.",
                    "Keys that land in the same bucket (collisions) are stored together in a small list, the <em>chain</em>.",
                ],
                "steps": [
                    "In <code>__init__</code>, create <code>self.buckets</code>, a list of B empty lists.",
                    "<code>_bucket(key)</code> returns <code>self.buckets[key % self.B]</code>.",
                    "<code>add</code>: append the key to its bucket only if <code>key not in b</code>, so no duplicates.",
                    "<code>remove</code>: if the key is in its bucket, <code>b.remove(key)</code>.",
                    "<code>contains</code>: return <code>key in self._bucket(key)</code>.",
                ],
                "why": [
                    "A key always maps to the same bucket, so add, remove and contains all look in the one place it could be.",
                    "With n keys spread over B buckets a chain has about n/B entries, so operations are <strong>O(1) average</strong>; if many keys share one bucket a chain can grow to <strong>O(n) worst</strong>.",
                    "B bucket lists plus one entry per stored key: <strong>O(buckets + n)</strong> space.",
                ],
                "dry": [
                    [
                        "1 → bucket 1, 2 → bucket 2, 10008 → 10008 % 10007 = bucket 1. Bucket 1 = [1, 10008].",
                        "contains(1) and contains(10008) scan bucket 1 and find them. contains(3): bucket 3 is empty.",
                        "remove(2) empties bucket 2 and returns None, so contains(2) runs: False.",
                        "Result: <strong>[True, True, False, False]</strong>.",
                    ],
                    [
                        "add(5): bucket 5 = [5]. add(5) again: 5 is already there, nothing appended.",
                        "remove(5): bucket 5 = []. contains(5) is False.",
                        "remove(7): 7 is not in bucket 7, so nothing happens; contains(7) is False.",
                        "Result: <strong>[False, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>key not in b</code> before appending?",
                     "Without it, adding 5 twice would store two copies, and one remove would leave a copy behind, so contains(5) would wrongly stay True."],
                    ["Why a prime number of buckets?",
                     "With <code>key % B</code>, keys sharing a common factor with B cluster in a few buckets. A prime B spreads patterned keys (like multiples of 10) more evenly."],
                    ["Why does <code>remove</code> check membership first?",
                     "<code>list.remove</code> raises ValueError if the item is missing, and removing an absent key must be allowed."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ design hashmap
    "design-hashmap": {
        "examples": [
            {"setup": "m = MyHashMap()\nm.put(1, 10)\nm.put(10008, 20)\nm.put(1, 30)",
             "call": "[m.get(1), m.get(10008), m.get(5), m.remove(1) or m.get(1)]", "expect": "[30, 20, -1, -1]"},
            {"setup": "m = MyHashMap()\nm.put(7, 1)\nm.put(10014, 2)\nm.remove(7)",
             "call": "[m.get(7), m.get(10014)]", "expect": "[-1, 2]"},
        ],
        "approaches": {
            "Direct-address array": {
                "idea": [
                    "Keys are limited to 0..10<sup>6</sup>, so allocate one slot per possible key and store the value there.",
                    "Use <code>-1</code> as the \"absent\" marker, since that is exactly what <code>get</code> must return for a missing key.",
                ],
                "steps": [
                    "In <code>__init__</code>, allocate <code>self.slots = [-1] * (10 ** 6 + 1)</code>.",
                    "<code>put(key, value)</code>: <code>self.slots[key] = value</code>; a second put simply overwrites.",
                    "<code>get(key)</code>: return <code>self.slots[key]</code>, which is -1 if never set or removed.",
                    "<code>remove(key)</code>: reset the slot to -1.",
                ],
                "why": [
                    "Each key has its own slot, so no two keys can overwrite each other.",
                    "Every operation is a single index: <strong>O(1) per operation</strong>.",
                    "The array is sized by the key range, not the number of keys: <strong>O(key range)</strong> space.",
                ],
                "dry": [
                    [
                        "put(1, 10): slots[1] = 10. put(10008, 20): slots[10008] = 20. put(1, 30): slots[1] = 30.",
                        "get(1) = 30, get(10008) = 20, get(5) = −1 (never set).",
                        "remove(1) resets slots[1] to −1 and returns None, so get(1) runs: −1.",
                        "Result: <strong>[30, 20, -1, -1]</strong>.",
                    ],
                    [
                        "put(7, 1): slots[7] = 1. put(10014, 2): slots[10014] = 2.",
                        "remove(7): slots[7] = −1.",
                        "get(7) = −1 and get(10014) = 2; the two keys never interact.",
                        "Result: <strong>[-1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["What if someone stores the value −1?",
                     "Then <code>get</code> cannot tell it apart from \"absent\". The problem's values are non-negative, so −1 is a safe sentinel here."],
                    ["Why is this allowed when it is not really hashing?",
                     "It is the degenerate hash function h(key) = key with a table as big as the key space. It is valid exactly because the range is small and fixed."],
                    ["Is creating a million-slot list expensive?",
                     "It costs a few megabytes and is done once in the constructor; after that every operation is O(1)."],
                ],
            },
            "Separate chaining with (key, value) pairs": {
                "idea": [
                    "Use <code>B = 10007</code> buckets and store each entry as a <code>[key, value]</code> pair in bucket <code>key % B</code>.",
                    "Unlike a set, a map must remember which key a value belongs to, because different keys share a bucket.",
                ],
                "steps": [
                    "In <code>__init__</code>, create B empty bucket lists.",
                    "<code>put</code>: scan the bucket; if a pair has the same key, update <code>pair[1] = value</code> and return; otherwise append <code>[key, value]</code>.",
                    "<code>get</code>: scan the bucket for the key and return its value, or −1 if not found.",
                    "<code>remove</code>: find the pair's position <code>i</code> in the bucket and <code>bucket.pop(i)</code>.",
                    "Pairs are lists, not tuples, so the value can be updated in place.",
                ],
                "why": [
                    "Every operation searches only the key's own bucket, and each key appears at most once there because <code>put</code> updates instead of duplicating.",
                    "Chains average n/B entries, so operations are <strong>O(1) average</strong> (O(n) if all keys collide).",
                    "B bucket lists plus one pair per key: <strong>O(buckets + n)</strong> space.",
                ],
                "dry": [
                    [
                        "put(1, 10): bucket 1 = [[1, 10]]. put(10008, 20): 10008 % 10007 = 1, bucket 1 = [[1, 10], [10008, 20]].",
                        "put(1, 30): finds [1, 10] and updates it to [1, 30].",
                        "get(1) = 30, get(10008) = 20, get(5): bucket 5 is empty, −1.",
                        "remove(1) pops index 0 of bucket 1; get(1) is then −1. Result: <strong>[30, 20, -1, -1]</strong>.",
                    ],
                    [
                        "put(7, 1): bucket 7 = [[7, 1]]. put(10014, 2): 10014 % 10007 = 7, bucket 7 = [[7, 1], [10014, 2]].",
                        "remove(7): pops index 0, bucket 7 = [[10014, 2]].",
                        "get(7) scans bucket 7 and finds no key 7: −1. get(10014) finds 2.",
                        "Result: <strong>[-1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store the key in the bucket and not just the value?",
                     "Keys 7 and 10014 share bucket 7. Without the key, <code>get(7)</code> could not tell which value is its own."],
                    ["Is it safe to <code>pop</code> inside the enumerate loop?",
                     "Yes, because the method returns immediately after popping, before the loop would advance over the shifted list."],
                    ["Why lists <code>[key, value]</code> instead of tuples?",
                     "<code>put</code> updates an existing value with <code>pair[1] = value</code>; tuples are immutable and would have to be replaced."],
                ],
            },
        },
    },


    # ------------------------------------------------------------------ sort an array
    "sort-an-array": {
        "examples": [
            {"call": "sort_array([3, 1, 3, 0])", "expect": "[0, 1, 3, 3]"},
            {"call": "sort_array([0, -2, 5, -2])", "expect": "[-2, -2, 0, 5]"},
        ],
        "approaches": {
            "Insertion sort": {
                "idea": [
                    "Grow a sorted prefix one element at a time, like sorting cards in your hand.",
                    "Take the next value <code>x</code>, slide every larger value in the prefix one step right, and drop <code>x</code> into the gap.",
                ],
                "steps": [
                    "Copy the input: <code>nums = nums[:]</code>.",
                    "For <code>i</code> from 1 to n − 1, set <code>x = nums[i]</code> and <code>j = i - 1</code>.",
                    "While <code>j &gt;= 0</code> and <code>nums[j] &gt; x</code>, shift <code>nums[j + 1] = nums[j]</code> and decrease <code>j</code>.",
                    "Place <code>x</code> at <code>nums[j + 1]</code>.",
                    "Return <code>nums</code>.",
                ],
                "why": [
                    "Invariant: before step <code>i</code>, <code>nums[:i]</code> is sorted. Inserting <code>x</code> after the last value ≤ x keeps it sorted, so after the last step the whole list is.",
                    "Using strict <code>&gt;</code> means equal values are not passed over, so the sort is stable.",
                    "Each insertion may shift up to i elements: <strong>O(n²)</strong> time worst case (O(n) on sorted input). Shifting is in place, so the sort uses <strong>O(1)</strong> extra space beyond the copy.",
                ],
                "dry": [
                    [
                        "i=1, x=1: 3 &gt; 1 shifts right. [1, 3, 3, 0].",
                        "i=2, x=3: nums[1] = 3 is not &gt; 3, so it stays. [1, 3, 3, 0].",
                        "i=3, x=0: 3, 3 and 1 all shift right, x lands at index 0.",
                        "It returns <strong>[0, 1, 3, 3]</strong>.",
                    ],
                    [
                        "i=1, x=−2: 0 shifts right. [−2, 0, 5, −2].",
                        "i=2, x=5: 0 is not &gt; 5, stays put.",
                        "i=3, x=−2: 5 and 0 shift; −2 is not &gt; −2, so x lands at index 1.",
                        "It returns <strong>[-2, -2, 0, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>nums[j] &gt; x</code> and not <code>&gt;=</code>?",
                     "<code>&gt;=</code> would also shift equal values, doing extra moves and putting equal elements in reversed order, which breaks stability."],
                    ["Why copy the list first?",
                     "The function returns a sorted list without changing the caller's list. The copy is O(n); the sorting itself is in place."],
                    ["When is insertion sort actually a good choice?",
                     "On tiny or nearly sorted inputs, where it runs close to O(n). Real library sorts like Timsort use it for short runs."],
                ],
            },
            "Merge sort": {
                "idea": [
                    "Split the list in half, sort each half recursively, then <em>merge</em> two sorted lists into one.",
                    "Merging is easy: repeatedly take the smaller front element of the two lists.",
                ],
                "steps": [
                    "Base case: a list of length 0 or 1 is sorted; return a copy.",
                    "Split at <code>mid = len(nums) // 2</code> and sort <code>left</code> and <code>right</code> recursively.",
                    "Merge with indices <code>i</code> and <code>j</code>: append <code>left[i]</code> if <code>left[i] &lt;= right[j]</code>, else <code>right[j]</code>.",
                    "When one side runs out, append the rest of both: <code>out + left[i:] + right[j:]</code>.",
                    "Return the merged list.",
                ],
                "why": [
                    "By induction both halves come back sorted, and the merge always takes the smallest remaining element, so the output is sorted.",
                    "The recursion has log n levels and each level merges n elements in total: <strong>O(n log n)</strong> time, in every case.",
                    "Merging builds new lists of total size n per level, but only one level's lists are alive at once: <strong>O(n)</strong> space plus O(log n) recursion.",
                ],
                "dry": [
                    [
                        "Split [3, 1, 3, 0] into [3, 1] and [3, 0].",
                        "[3, 1] → [3] and [1] → merged [1, 3]. [3, 0] → merged [0, 3].",
                        "Merge [1, 3] with [0, 3]: take 0 (right), 1 (left), then 3 vs 3 takes left's 3 because of <code>&lt;=</code>; append right's leftover 3.",
                        "It returns <strong>[0, 1, 3, 3]</strong>.",
                    ],
                    [
                        "Split into [0, −2] and [5, −2].",
                        "[0, −2] → [−2, 0]. [5, −2] → [−2, 5].",
                        "Merge: −2 vs −2 takes left; 0 vs −2 takes right; 0 vs 5 takes 0; leftover 5.",
                        "It returns <strong>[-2, -2, 0, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> in the merge?",
                     "On ties it takes from the left half first, so equal elements keep their original order. That makes merge sort stable."],
                    ["Is it fine to append both leftovers?",
                     "Yes. When the loop ends one of <code>left[i:]</code> and <code>right[j:]</code> is empty and the other is already sorted and not smaller than <code>out</code>."],
                    ["Why prefer merge sort over quicksort?",
                     "Guaranteed O(n log n) and stability. The price is O(n) extra memory."],
                ],
            },
            "Heap sort": {
                "idea": [
                    "Turn the array into a max-heap in place, so the largest value is at index 0.",
                    "Swap it to the end, shrink the heap by one, and restore the heap with <code>sift</code>. Repeat until the heap is empty.",
                ],
                "steps": [
                    "<code>sift(i, n)</code> moves <code>nums[i]</code> down: swap with the larger child (<code>2i+1</code> or <code>2i+2</code>, only within the first n slots) until neither child is bigger.",
                    "Heapify: call <code>sift(i, n)</code> for <code>i</code> from <code>n // 2 - 1</code> down to 0.",
                    "For <code>end</code> from n − 1 down to 1: swap <code>nums[0]</code> with <code>nums[end]</code>.",
                    "Then <code>sift(0, end)</code> to fix the heap in <code>nums[:end]</code>.",
                    "Return <code>nums</code>.",
                ],
                "why": [
                    "After heapify every parent is ≥ its children, so <code>nums[0]</code> is the max. Each round moves the max of the heap to just before the already-sorted tail.",
                    "Heapify is O(n) and each of the n − 1 extractions sifts down at most log n levels: <strong>O(n log n)</strong> time.",
                    "All swaps happen inside the list, so the sort is <strong>O(1)</strong> extra space; the defensive copy <code>nums[:]</code> adds O(n).",
                ],
                "dry": [
                    [
                        "Heapify [3, 1, 3, 0]: node 1 (1) has child 0, fine; node 0 (3) has children 1 and 3, none strictly bigger. Already a heap.",
                        "end=3: swap → [0, 1, 3, 3]; sift 0 swaps with the 3 at index 2 → [3, 1, 0, 3].",
                        "end=2: swap → [0, 1, 3, 3]; sift swaps with the 1 → [1, 0, 3, 3].",
                        "end=1: swap → [0, 1, 3, 3]. It returns <strong>[0, 1, 3, 3]</strong>.",
                    ],
                    [
                        "Heapify: node 1 (−2) vs child −2, no swap; node 0 (0) swaps with 5 → [5, −2, 0, −2].",
                        "end=3: swap → [−2, −2, 0, 5]; sift swaps the root with 0 → [0, −2, −2, 5].",
                        "end=2: swap → [−2, −2, 0, 5]; child −2 is not bigger, no sift. end=1: swaps equal values.",
                        "It returns <strong>[-2, -2, 0, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does heapify start at <code>n // 2 - 1</code>?",
                     "Indices from <code>n // 2</code> onwards are leaves, which are already valid one-element heaps. The last parent is at <code>n // 2 - 1</code>."],
                    ["Why is heapify O(n) and not O(n log n)?",
                     "Most nodes are near the bottom and sift only a level or two; summing the heights over all nodes gives O(n)."],
                    ["Is heap sort stable?",
                     "No. The swap of the root with the end can jump an element past equal ones."],
                ],
            },
            "Quicksort, random pivot, three-way partition": {
                "idea": [
                    "Pick a random pivot and partition the range into three parts: <code>&lt; pivot</code>, <code>== pivot</code>, <code>&gt; pivot</code>. The middle part is already in its final place.",
                    "Recurse into the smaller outer part and loop on the larger one, which bounds the stack depth.",
                ],
                "steps": [
                    "<code>qs(lo, hi)</code> loops while <code>lo &lt; hi</code>; the pivot is <code>nums[rng.randint(lo, hi)]</code>.",
                    "Partition with <code>lt</code>, <code>i</code>, <code>gt</code>: a small value swaps to <code>lt</code> (both advance), a big value swaps to <code>gt</code> (only <code>gt</code> moves), an equal value just advances <code>i</code>.",
                    "When <code>i &gt; gt</code>, <code>nums[lt..gt]</code> equals the pivot.",
                    "If the left part <code>lo..lt-1</code> is smaller, recurse on it and set <code>lo = gt + 1</code>; otherwise recurse on the right and set <code>hi = lt - 1</code>.",
                    "Call <code>qs(0, len(nums) - 1)</code> and return <code>nums</code>.",
                ],
                "why": [
                    "After a partition every value left of <code>lt</code> is smaller and every value right of <code>gt</code> is larger than the pivot, so sorting the two outer parts sorts the range.",
                    "A random pivot splits reasonably on average, giving <strong>O(n log n) expected</strong> time; three-way partitioning stops many duplicates from causing O(n²).",
                    "Recursing only on the smaller side halves the size each level of the stack: <strong>O(log n) expected</strong> space (worst case O(log n) too).",
                ],
                "dry": [
                    [
                        "qs(0, 3): pivot 0. Partition [3, 1, 3, 0] → [0, 3, 1, 3], lt=0, gt=0. Left part is empty, so lo = 1.",
                        "Same call, range 1..3: pivot 1. Partition → [0, 1, 3, 3], lt=gt=1. Left part empty again, lo = 2.",
                        "Range 2..3: pivot 3. Both are equal: lt=2, gt=3. Sides are both empty; hi = 1 ends the loop.",
                        "It returns <strong>[0, 1, 3, 3]</strong>.",
                    ],
                    [
                        "qs(0, 3): pivot −2. Partition [0, −2, 5, −2] → [−2, −2, 5, 0], lt=0, gt=1.",
                        "Left part is empty, so lo = 2. Range 2..3: pivot 0. Partition → [−2, −2, 0, 5], lt=gt=2.",
                        "lo = 3, and the loop ends.",
                        "It returns <strong>[-2, -2, 0, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not advance <code>i</code> after swapping with <code>gt</code>?",
                     "The value that came from <code>gt</code> has not been looked at yet, so it must be classified on the next iteration."],
                    ["Why three-way rather than the classic two-way partition?",
                     "With many equal values (e.g. <code>[2] * 300</code> in the tests) a two-way split can be very lopsided. The equal block is removed in one go here."],
                    ["Why <code>random.Random(0)</code> instead of <code>random</code>?",
                     "A seeded generator makes runs reproducible, which helps testing, while still avoiding a fixed pivot that sorted input could exploit."],
                ],
            },
            "Counting sort over the value range": {
                "idea": [
                    "When values are integers in a small range, count how many times each value appears and write them back in order.",
                    "Offsetting by <code>lo = min(nums)</code> lets negative numbers use list indices starting at 0.",
                ],
                "steps": [
                    "Return <code>[]</code> for an empty input (<code>min</code> would fail).",
                    "Set <code>lo = min(nums)</code> and <code>counts = [0] * (max(nums) - lo + 1)</code>.",
                    "For each <code>x</code>, increment <code>counts[x - lo]</code>.",
                    "Walk <code>offset, c</code> over <code>counts</code> and extend <code>out</code> with <code>c</code> copies of <code>offset + lo</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Offsets are visited in increasing order and each value is written exactly as many times as it appeared, so <code>out</code> is the sorted input.",
                    "Counting is O(n) and the write-back is O(n + k), where k = max − min + 1: <strong>O(n + k)</strong> time.",
                    "The count array has k cells: <strong>O(k)</strong> space, which is only reasonable when k is not much bigger than n.",
                ],
                "dry": [
                    [
                        "lo = 0, max = 3, counts has 4 cells.",
                        "Counting 3, 1, 3, 0 gives counts = [1, 1, 0, 2].",
                        "Write one 0, one 1, no 2, two 3s.",
                        "It returns <strong>[0, 1, 3, 3]</strong>.",
                    ],
                    [
                        "lo = −2, max = 5, counts has 8 cells.",
                        "−2 → offset 0 (twice), 0 → offset 2, 5 → offset 7. counts = [2, 0, 1, 0, 0, 0, 0, 1].",
                        "Write −2, −2, then 0, then 5.",
                        "It returns <strong>[-2, -2, 0, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why subtract <code>lo</code>?",
                     "List indices cannot be negative in the intended way (−2 would index from the end). Shifting by the minimum maps the smallest value to index 0."],
                    ["When is counting sort a bad idea?",
                     "When the range is huge compared to n, e.g. [0, 10<sup>9</sup>]: the count array would be enormous even for two elements."],
                    ["Is it a comparison sort?",
                     "No. It never compares elements, which is why it can beat the n log n lower bound."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sort colors
    "sort-colors": {
        "examples": [
            {"setup": "a = [2, 0, 2, 1, 1, 0]\nsort_colors(a)", "call": "a", "expect": "[0, 0, 1, 1, 2, 2]"},
            {"setup": "a = [2, 0, 1]\nsort_colors(a)", "call": "a", "expect": "[0, 1, 2]"},
        ],
        "approaches": {
            "Any comparison sort": {
                "idea": [
                    "Colours are just the integers 0, 1 and 2, so sorting the list puts all 0s, then 1s, then 2s.",
                    "<code>nums.sort()</code> sorts in place, which is what the problem asks for.",
                ],
                "steps": [
                    "Call <code>nums.sort()</code>.",
                    "Python's Timsort rearranges the caller's list in place.",
                    "Nothing is returned; the caller reads the modified list.",
                    "The setup in the examples sorts <code>a</code> and then the call reads <code>a</code>.",
                ],
                "why": [
                    "Sorting by value is exactly the required order 0, 1, 2.",
                    "A general comparison sort costs <strong>O(n log n)</strong> time, although Timsort is often faster on inputs with long runs.",
                    "Timsort can use up to O(n) temporary memory, so space is <strong>O(1)–O(n)</strong>.",
                ],
                "dry": [
                    [
                        "a = [2, 0, 2, 1, 1, 0].",
                        "<code>a.sort()</code> reorders it in place.",
                        "a is now <strong>[0, 0, 1, 1, 2, 2]</strong>.",
                    ],
                    [
                        "a = [2, 0, 1].",
                        "<code>a.sort()</code> reorders it in place.",
                        "a is now <strong>[0, 1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>nums.sort()</code> and not <code>sorted(nums)</code>?",
                     "<code>sorted</code> returns a new list and leaves <code>nums</code> unchanged. The problem checks the original list."],
                    ["Is this allowed in an interview?",
                     "It is correct, but the problem explicitly invites a one-pass, constant-space solution without the library sort."],
                    ["Why is this O(n log n) when there are only 3 values?",
                     "A comparison sort does not know that; it treats the data like any other. The counting and Dutch flag approaches exploit the 3 values."],
                ],
            },
            "Count, then overwrite": {
                "idea": [
                    "There are only three possible values, so count how many of each there are.",
                    "Then overwrite the array: that many 0s, then 1s, then 2s.",
                ],
                "steps": [
                    "Create <code>c = [0, 0, 0]</code>.",
                    "For each <code>x</code> in <code>nums</code>, do <code>c[x] += 1</code>.",
                    "Set a write index <code>i = 0</code>.",
                    "For <code>color</code> in 0, 1, 2, write <code>color</code> into <code>nums[i]</code> <code>c[color]</code> times, advancing <code>i</code>.",
                ],
                "why": [
                    "The output has exactly the same multiset of values as the input, laid out in increasing order, which is the sorted array.",
                    "Two passes over n elements: <strong>O(n)</strong> time.",
                    "Only three counters and an index: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Counting [2, 0, 2, 1, 1, 0] gives c = [2, 2, 2].",
                        "Write 0, 0 at indices 0–1, then 1, 1 at 2–3, then 2, 2 at 4–5.",
                        "a is now <strong>[0, 0, 1, 1, 2, 2]</strong>.",
                    ],
                    [
                        "Counting [2, 0, 1] gives c = [1, 1, 1].",
                        "Write 0 at index 0, 1 at index 1, 2 at index 2.",
                        "a is now <strong>[0, 1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can I just overwrite the values?",
                     "The values are plain integers with no identity beyond their number, so writing a fresh 0 is the same as moving an old one."],
                    ["What does this cost compared with Dutch flag?",
                     "Both are O(n) time and O(1) space. This one reads the array twice; Dutch flag finishes in a single pass."],
                    ["Would it work with more colours?",
                     "Yes, with k counters it becomes counting sort, O(n + k)."],
                ],
            },
            "Dutch national flag, one pass": {
                "idea": [
                    "Keep three regions with pointers: <code>nums[:low]</code> are 0s, <code>nums[low:mid]</code> are 1s, <code>nums[high+1:]</code> are 2s, and <code>nums[mid:high+1]</code> is unseen.",
                    "Look at <code>nums[mid]</code> and move it into the right region with at most one swap.",
                ],
                "steps": [
                    "Set <code>low = mid = 0</code> and <code>high = len(nums) - 1</code>.",
                    "While <code>mid &lt;= high</code>: if <code>nums[mid] == 0</code>, swap it with <code>nums[low]</code> and advance both <code>low</code> and <code>mid</code>.",
                    "If it is 1, just advance <code>mid</code>.",
                    "If it is 2, swap it with <code>nums[high]</code> and decrease <code>high</code>, but do not move <code>mid</code>.",
                    "The loop ends when the unseen region is empty.",
                ],
                "why": [
                    "Each case keeps the region invariant. A 0 swapped from <code>low</code> brings back a 1 (or the same 0), already checked, so <code>mid</code> can advance; a value from <code>high</code> is unseen, so <code>mid</code> must stay.",
                    "Every iteration shrinks the unseen region by one: at most n iterations, <strong>O(n)</strong> time in one pass.",
                    "Three indices only: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "mid=0 is 2: swap with high=5 → [0, 0, 2, 1, 1, 2], high=4.",
                        "mid=0 is 0: swap with itself, low=mid=1. mid=1 is 0: low=mid=2.",
                        "mid=2 is 2: swap with high=4 → [0, 0, 1, 1, 2, 2], high=3.",
                        "mid=2 and mid=3 are 1s: mid=4 &gt; high=3, stop. a is <strong>[0, 0, 1, 1, 2, 2]</strong>.",
                    ],
                    [
                        "mid=0 is 2: swap with high=2 → [1, 0, 2], high=1.",
                        "mid=0 is 1: mid=1.",
                        "mid=1 is 0: swap with low=0 → [0, 1, 2], low=1, mid=2 &gt; high=1, stop.",
                        "a is <strong>[0, 1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>mid</code> not advance after swapping a 2?",
                     "The value brought in from <code>high</code> has not been examined; it could be 0, 1 or 2. In the first example the first swap brings in a 0 that is then handled on the next step."],
                    ["Why can <code>mid</code> advance after swapping a 0?",
                     "<code>nums[low]</code> is in the 1s region (or <code>low == mid</code>), so what comes back to <code>mid</code> is a 1 or the same 0, both already in the right place."],
                    ["Why <code>mid &lt;= high</code> and not <code>&lt;</code>?",
                     "When <code>mid == high</code> there is still one unseen element; stopping early would leave it unclassified, e.g. a 0 left at the end."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ encode and decode strings
    "encode-decode-strings": {
        "examples": [
            {"call": 'decode(encode(["4#ab", "", "/:x"]))', "expect": '["4#ab", "", "/:x"]'},
            {"call": 'decode(encode(["12#", "/"]))', "expect": '["12#", "/"]'},
        ],
        "approaches": {
            "Escape the delimiter": {
                "idea": [
                    "End each string with the two-character marker <code>/:</code>. To keep a real <code>/</code> from being mistaken for the start of a marker, double it to <code>//</code>.",
                    "When decoding, a <code>/</code> is always followed by a second character that says what it means: <code>/</code> is a literal slash, <code>:</code> ends a string.",
                ],
                "steps": [
                    "<code>encode</code>: for each string, <code>s.replace(\"/\", \"//\")</code> and append <code>\"/:\"</code>; join everything.",
                    "<code>decode</code>: walk with index <code>i</code>, collecting characters in <code>cur</code>.",
                    "If <code>s[i]</code> is <code>/</code> and <code>s[i + 1]</code> is <code>/</code>, append a literal <code>/</code>; otherwise it is <code>/:</code>, so push <code>\"\".join(cur)</code> to <code>out</code> and reset <code>cur</code>. Either way <code>i += 2</code>.",
                    "Any other character is appended to <code>cur</code> and <code>i += 1</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "After escaping, every <code>/</code> in the encoded text starts a two-character pair, so the decoder never splits a pair and every <code>/:</code> it sees is a true terminator.",
                    "Because every string ends with a terminator, empty strings and an empty list both round-trip.",
                    "Encoding and decoding each read every character once: <strong>O(n)</strong> time and <strong>O(n)</strong> space for the encoded string and the output.",
                ],
                "dry": [
                    [
                        "encode: \"4#ab\" → \"4#ab/:\", \"\" → \"/:\", \"/:x\" → \"//:x/:\". Joined: <code>4#ab/:/://:x/:</code>.",
                        "decode: 4, #, a, b go into cur; <code>/:</code> pushes \"4#ab\".",
                        "<code>/:</code> pushes \"\". <code>//</code> adds a literal /, then ':' and 'x' are plain characters.",
                        "The final <code>/:</code> pushes \"/:x\". Result: <strong>[\"4#ab\", \"\", \"/:x\"]</strong>.",
                    ],
                    [
                        "encode: \"12#\" → \"12#/:\", \"/\" → \"///:\". Joined: <code>12#/:///:</code>.",
                        "decode: 1, 2, # collected; <code>/:</code> pushes \"12#\".",
                        "<code>//</code> adds \"/\", then <code>/:</code> pushes \"/\".",
                        "Result: <strong>[\"12#\", \"/\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not use a single separator character like <code>,</code>?",
                     "Any character can appear inside a string, so a lone separator is ambiguous. Escaping is what makes the marker unambiguous."],
                    ["Can <code>s[i + 1]</code> go out of range?",
                     "Not for output of <code>encode</code>: a <code>/</code> is always half of a <code>//</code> or <code>/:</code> pair, so it is never the last character."],
                    ["Why is the original string ':x' after '//' not read as a terminator?",
                     "The decoder consumes <code>//</code> as one unit and moves <code>i</code> past both slashes, so the following ':' is seen as a plain character."],
                ],
            },
            "Length prefix": {
                "idea": [
                    "Write each string as its length, a <code>#</code>, then the string itself: <code>len#s</code>.",
                    "The decoder reads the number up to the first <code>#</code>, then takes exactly that many characters, so the content is never inspected for delimiters.",
                ],
                "steps": [
                    "<code>encode</code>: join <code>f\"{len(s)}#{s}\"</code> for every string.",
                    "<code>decode</code>: start at <code>i = 0</code>.",
                    "Find the next <code>#</code> from <code>i</code>: <code>j = s.index(\"#\", i)</code>, and parse <code>length = int(s[i:j])</code>.",
                    "Take <code>s[j + 1:j + 1 + length]</code> as the next string and jump <code>i</code> to just after it.",
                    "Repeat until <code>i</code> reaches the end; return <code>out</code>.",
                ],
                "why": [
                    "The decoder only ever searches for <code>#</code> at the start of a record, where the text is digits followed by <code>#</code>; a <code>#</code> inside a string is skipped because the length says how far to jump.",
                    "Each character is visited a constant number of times: <strong>O(n)</strong> time.",
                    "The encoded string and the output list are <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "encode gives <code>4#4#ab0#3#/:x</code>.",
                        "i=0: '#' at 1, length 4 → \"4#ab\", i=6.",
                        "i=6: '#' at 7, length 0 → \"\", i=8. i=8: '#' at 9, length 3 → \"/:x\", i=13.",
                        "Result: <strong>[\"4#ab\", \"\", \"/:x\"]</strong>.",
                    ],
                    [
                        "encode gives <code>3#12#1#/</code>.",
                        "i=0: '#' at 1, length 3 → \"12#\", i=5. The '#' inside \"12#\" is jumped over.",
                        "i=5: '#' at 6, length 1 → \"/\", i=8 = end.",
                        "Result: <strong>[\"12#\", \"/\"]</strong>.",
                    ],
                ],
                "faq": [
                    ["What if a string itself starts with digits and a <code>#</code>, like \"12#\"?",
                     "It does not matter: the decoder reads \"3#\" first and takes the next 3 characters blindly, as the second example shows."],
                    ["Why not use a fixed-width length instead of <code>#</code>?",
                     "That also works (e.g. 4 bytes per length) and avoids the search; the <code>#</code> version is easier to read and handles any length."],
                    ["How does an empty list encode?",
                     "As the empty string, and <code>decode(\"\")</code> never enters the loop, returning []."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ range sum query 2d
    "range-sum-query-2d": {
        "examples": [
            {"setup": "nm = NumMatrix([[3, 0, 1], [5, 6, 3], [1, 2, 0]])",
             "call": "[nm.sumRegion(1, 1, 2, 2), nm.sumRegion(0, 0, 1, 1)]", "expect": "[11, 14]"},
            {"setup": "nm = NumMatrix([[1, -2], [3, 4]])",
             "call": "[nm.sumRegion(0, 0, 1, 1), nm.sumRegion(1, 0, 1, 0)]", "expect": "[6, 3]"},
        ],
        "approaches": {
            "Sum the rectangle per query": {
                "idea": [
                    "Store the matrix as it is and, for each query, add up every cell in the rectangle.",
                    "No preprocessing at all, so every query pays for its full area.",
                ],
                "steps": [
                    "<code>__init__</code> just keeps a reference: <code>self.m = matrix</code>.",
                    "<code>sumRegion(r1, c1, r2, c2)</code> loops <code>r</code> from <code>r1</code> to <code>r2</code> inclusive.",
                    "For each row, sum the slice <code>self.m[r][c1:c2 + 1]</code>.",
                    "Return the sum of those row sums.",
                ],
                "why": [
                    "The rectangle is exactly the union of those row slices, so the total is the region sum.",
                    "Construction is O(1); each query touches up to m · n cells: <strong>O(1) build, O(m · n) per query</strong>.",
                    "Only a reference to the input is kept: <strong>O(1)</strong> extra space (each slice is a short temporary).",
                ],
                "dry": [
                    [
                        "sumRegion(1, 1, 2, 2): row 1 slice [6, 3] = 9, row 2 slice [2, 0] = 2. Total 11.",
                        "sumRegion(0, 0, 1, 1): row 0 slice [3, 0] = 3, row 1 slice [5, 6] = 11. Total 14.",
                        "Result: <strong>[11, 14]</strong>.",
                    ],
                    [
                        "sumRegion(0, 0, 1, 1): rows [1, −2] = −1 and [3, 4] = 7. Total 6.",
                        "sumRegion(1, 0, 1, 0): row 1 slice [3] = 3.",
                        "Result: <strong>[6, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>c2 + 1</code> in the slice?",
                     "The query bounds are inclusive, but Python slices exclude the end, so the end must be one past <code>c2</code>."],
                    ["When is this actually fine?",
                     "When there are very few queries, since there is nothing to build. With many queries the repeated work dominates."],
                    ["Does it handle negative values?",
                     "Yes, it just adds numbers. Sums with negatives need no special care."],
                ],
            },
            "Prefix sums per row": {
                "idea": [
                    "Precompute, for each row, a prefix-sum list <code>acc</code> where <code>acc[c]</code> is the sum of the first c cells.",
                    "Any horizontal slice then costs one subtraction, so a query only loops over rows.",
                ],
                "steps": [
                    "For each row, build <code>acc = [0]</code> and append <code>acc[-1] + v</code> for each value <code>v</code>.",
                    "Store all of them in <code>self.rows</code>.",
                    "<code>sumRegion</code> sums <code>self.rows[r][c2 + 1] - self.rows[r][c1]</code> for <code>r</code> from <code>r1</code> to <code>r2</code>.",
                    "Return that total.",
                ],
                "why": [
                    "<code>acc[c2 + 1] - acc[c1]</code> is the sum of cells c1..c2 in that row, so adding over the rows gives the rectangle.",
                    "Building visits every cell once; a query does one subtraction per row: <strong>O(m · n) build, O(m) per query</strong>.",
                    "Each row stores n + 1 prefix values: <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "rows = [[0, 3, 3, 4], [0, 5, 11, 14], [0, 1, 3, 3]].",
                        "sumRegion(1, 1, 2, 2): row 1 gives 14 − 5 = 9, row 2 gives 3 − 1 = 2. Total 11.",
                        "sumRegion(0, 0, 1, 1): row 0 gives 3 − 0 = 3, row 1 gives 11 − 0 = 11. Total 14.",
                        "Result: <strong>[11, 14]</strong>.",
                    ],
                    [
                        "rows = [[0, 1, −1], [0, 3, 7]].",
                        "sumRegion(0, 0, 1, 1): (−1 − 0) + (7 − 0) = 6.",
                        "sumRegion(1, 0, 1, 0): 3 − 0 = 3. Result: <strong>[6, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start each <code>acc</code> with 0?",
                     "It makes <code>acc[c]</code> the sum of the first c cells, so a slice starting at column 0 is <code>acc[c2 + 1] - acc[0]</code> with no special case."],
                    ["Why <code>c2 + 1</code> and <code>c1</code>?",
                     "<code>acc[c2 + 1]</code> covers columns 0..c2 and <code>acc[c1]</code> covers 0..c1−1; their difference is exactly c1..c2."],
                    ["Is this a good compromise?",
                     "It is simpler than 2-D prefix sums and uses the same memory, but queries are O(m) instead of O(1), so the 2-D version is preferred."],
                ],
            },
            "2-D prefix sums": {
                "idea": [
                    "Let <code>P[r][c]</code> be the sum of the rectangle from (0, 0) to (r − 1, c − 1). Then any rectangle is four lookups by inclusion–exclusion.",
                    "<code>P</code> has an extra row and column of zeros so that rectangles touching the top or left edge need no special case.",
                ],
                "steps": [
                    "Allocate <code>P</code> of size (m + 1) × (n + 1), all zeros.",
                    "For each cell: <code>P[r+1][c+1] = matrix[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]</code>.",
                    "<code>sumRegion</code> returns <code>P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]</code>.",
                    "The first term is everything up to the bottom-right corner; the two subtractions remove the strips above and to the left; the last term adds back the corner removed twice.",
                ],
                "why": [
                    "The build formula adds the area above and the area to the left, which overlap in <code>P[r][c]</code>, so that overlap is subtracted once.",
                    "The query formula is the same inclusion–exclusion read backwards, so it gives exactly the rectangle sum.",
                    "Every cell is filled once and a query is four lookups: <strong>O(m · n) build, O(1) per query</strong>, with <strong>O(m · n)</strong> space for <code>P</code>.",
                ],
                "dry": [
                    [
                        "P = [[0, 0, 0, 0], [0, 3, 3, 4], [0, 8, 14, 18], [0, 9, 17, 21]].",
                        "sumRegion(1, 1, 2, 2) = P[3][3] − P[1][3] − P[3][1] + P[1][1] = 21 − 4 − 9 + 3 = 11.",
                        "sumRegion(0, 0, 1, 1) = P[2][2] − P[0][2] − P[2][0] + P[0][0] = 14.",
                        "Result: <strong>[11, 14]</strong>.",
                    ],
                    [
                        "P = [[0, 0, 0], [0, 1, −1], [0, 4, 6]].",
                        "sumRegion(0, 0, 1, 1) = P[2][2] = 6.",
                        "sumRegion(1, 0, 1, 0) = P[2][1] − P[1][1] − P[2][0] + P[1][0] = 4 − 1 − 0 + 0 = 3.",
                        "Result: <strong>[6, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>P[r1][c1]</code> added back?",
                     "The strip above and the strip to the left both contain the top-left block (0, 0)..(r1−1, c1−1), so it was subtracted twice and must be added once."],
                    ["Why the extra zero row and column?",
                     "With them, <code>P[r1][…]</code> when r1 = 0 is just 0. Without them every query would need <code>if r1 &gt; 0</code> style checks."],
                    ["Does it work with negative numbers?",
                     "Yes. Prefix sums only add and subtract; nothing assumes values are positive, as the second example shows."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ product of array except self
    "product-except-self": {
        "examples": [
            {"call": "product_except_self([1, 2, 3, 4])", "expect": "[24, 12, 8, 6]"},
            {"call": "product_except_self([2, 0, 3])", "expect": "[0, 6, 0]"},
        ],
        "approaches": {
            "Multiply everything else, per index": {
                "idea": [
                    "Answer each position separately: multiply every element except the one at that index.",
                    "It is the definition, so it handles zeros and negatives without any special cases.",
                ],
                "steps": [
                    "Create <code>out = []</code>.",
                    "For each index <code>i</code>, set <code>p = 1</code>.",
                    "Loop <code>j, x</code> over <code>enumerate(nums)</code>; when <code>j != i</code>, multiply <code>p *= x</code>.",
                    "Append <code>p</code> to <code>out</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Each <code>out[i]</code> is literally the product of all other elements, so it is correct by construction.",
                    "n products of n − 1 factors: <strong>O(n²)</strong> time.",
                    "Only <code>p</code> and the loop indices beyond the output: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: 2 · 3 · 4 = 24. i=1: 1 · 3 · 4 = 12.",
                        "i=2: 1 · 2 · 4 = 8. i=3: 1 · 2 · 3 = 6.",
                        "It returns <strong>[24, 12, 8, 6]</strong>.",
                    ],
                    [
                        "i=0: 0 · 3 = 0.",
                        "i=1: 2 · 3 = 6 (the zero is skipped because it is at index 1).",
                        "i=2: 2 · 0 = 0. It returns <strong>[0, 6, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compare indices (<code>j != i</code>) and not values?",
                     "Values can repeat. Skipping by value would drop every copy, e.g. all 2s in [2, 2, 3]."],
                    ["Is division ever needed here?",
                     "No, which is why it has no trouble with zeros."],
                    ["Why bother with it?",
                     "It is the reference answer the tests compare against; mention it, then improve it."],
                ],
            },
            "Total product and division": {
                "idea": [
                    "Product of everything except <code>x</code> is the total product divided by <code>x</code>, but division by zero needs care.",
                    "Count the zeros and compute the product of the <em>nonzero</em> values; the zero count decides the shape of the answer.",
                ],
                "steps": [
                    "<code>zeros = nums.count(0)</code>; <code>total</code> = product of all nonzero values.",
                    "If <code>zeros &gt; 1</code>, every answer includes a zero: return all 0s.",
                    "If <code>zeros == 1</code>, only the zero's own position gets <code>total</code>; all others get 0.",
                    "Otherwise return <code>total // x</code> for each <code>x</code>.",
                ],
                "why": [
                    "With no zeros, <code>total</code> is the product of all elements and <code>x</code> divides it exactly, so integer division is exact even for negatives.",
                    "With one zero, any position other than the zero includes it, and the zero's position gets the product of all the rest, which is <code>total</code>.",
                    "Two passes over the array: <strong>O(n)</strong> time, <strong>O(1)</strong> extra space. Interviewers often forbid division, which is why the next approaches exist.",
                ],
                "dry": [
                    [
                        "zeros = 0, total = 1 · 2 · 3 · 4 = 24.",
                        "No zeros, so divide: 24 // 1, 24 // 2, 24 // 3, 24 // 4.",
                        "It returns <strong>[24, 12, 8, 6]</strong>.",
                    ],
                    [
                        "zeros = 1, total = 2 · 3 = 6 (the 0 is skipped).",
                        "One zero: index 1 (the zero) gets 6, the others get 0.",
                        "It returns <strong>[0, 6, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why skip zeros when computing <code>total</code>?",
                     "Including a zero would make <code>total</code> 0 and lose the product needed at the zero's own position."],
                    ["Is <code>//</code> safe with negative numbers?",
                     "Here, yes: <code>x</code> always divides <code>total</code> exactly, so floor division and true division agree."],
                    ["Why is this approach often rejected?",
                     "The problem statement usually says \"without using division\", and with floats division also brings rounding error."],
                ],
            },
            "Prefix and suffix product arrays": {
                "idea": [
                    "The product of everything except index i is (product of everything to the left) × (product of everything to the right).",
                    "Precompute both in two arrays, <code>left</code> and <code>right</code>, then multiply them position by position.",
                ],
                "steps": [
                    "Create <code>left = [1] * n</code> and <code>right = [1] * n</code>.",
                    "Forward: <code>left[i] = left[i - 1] * nums[i - 1]</code> for i from 1.",
                    "Backward: <code>right[i] = right[i + 1] * nums[i + 1]</code> for i from n − 2 down to 0.",
                    "Return <code>[a * b for a, b in zip(left, right)]</code>.",
                ],
                "why": [
                    "<code>left[i]</code> is the product of <code>nums[:i]</code> and <code>right[i]</code> of <code>nums[i+1:]</code>; together they are every element except <code>nums[i]</code>.",
                    "No division is used, so zeros need no special handling.",
                    "Three linear passes: <strong>O(n)</strong> time; two extra arrays of length n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "left = [1, 1, 2, 6].",
                        "right = [24, 12, 4, 1].",
                        "Multiply pairwise: 24, 12, 8, 6. It returns <strong>[24, 12, 8, 6]</strong>.",
                    ],
                    [
                        "left = [1, 2, 0] (the zero affects only what comes after it).",
                        "right = [0, 3, 1].",
                        "Multiply pairwise: 0, 6, 0. It returns <strong>[0, 6, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start both arrays filled with 1?",
                     "1 is the empty product. <code>left[0]</code> and <code>right[n-1]</code> have nothing on that side, so they must be 1."],
                    ["Why <code>nums[i - 1]</code> and not <code>nums[i]</code>?",
                     "<code>left[i]</code> must exclude <code>nums[i]</code>; it stops just before index i."],
                    ["Can I avoid the second array?",
                     "Yes, the next approach stores the prefix products in the output and keeps the suffix product in a single variable."],
                ],
            },
            "Output array plus a running suffix": {
                "idea": [
                    "Same left × right idea, but store the prefix products directly in <code>out</code>.",
                    "Then walk backwards with one variable <code>suffix</code> holding the product of everything to the right, multiplying it in as you go.",
                ],
                "steps": [
                    "Create <code>out = [1] * n</code>.",
                    "Forward: <code>out[i] = out[i - 1] * nums[i - 1]</code>, so <code>out[i]</code> is the prefix product.",
                    "Set <code>suffix = 1</code>.",
                    "Backward from n − 1 to 0: <code>out[i] *= suffix</code>, then <code>suffix *= nums[i]</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "When index i is processed in the backward loop, <code>suffix</code> is the product of <code>nums[i+1:]</code>, because <code>nums[i]</code> is multiplied in only after <code>out[i]</code> is updated.",
                    "Two passes: <strong>O(n)</strong> time.",
                    "Only <code>suffix</code> is used beyond the output: <strong>O(1) beyond the output</strong>.",
                ],
                "dry": [
                    [
                        "Forward: out = [1, 1, 2, 6].",
                        "i=3: out[3] = 6 · 1 = 6, suffix = 4. i=2: out[2] = 2 · 4 = 8, suffix = 12.",
                        "i=1: out[1] = 1 · 12 = 12, suffix = 24. i=0: out[0] = 1 · 24 = 24.",
                        "It returns <strong>[24, 12, 8, 6]</strong>.",
                    ],
                    [
                        "Forward: out = [1, 2, 0].",
                        "i=2: out[2] = 0 · 1 = 0, suffix = 3. i=1: out[1] = 2 · 3 = 6, suffix = 0.",
                        "i=0: out[0] = 1 · 0 = 0.",
                        "It returns <strong>[0, 6, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why update <code>out[i]</code> before <code>suffix</code>?",
                     "<code>out[i]</code> must not include <code>nums[i]</code>. Multiplying it into <code>suffix</code> first would do exactly that."],
                    ["Why is this called O(1) space when <code>out</code> has n entries?",
                     "The output is required anyway, so by convention it does not count as extra space."],
                    ["Does it handle zeros?",
                     "Yes. There is no division, so a zero simply makes some prefix or suffix products 0, which is correct."],
                ],
            },
        },
    },


    # ------------------------------------------------------------------ valid sudoku
    "valid-sudoku": {
        "examples": [
            {"setup": SUDOKU_BAD, "call": "is_valid_sudoku(bad)", "expect": "False"},
            {"setup": SUDOKU, "call": "is_valid_sudoku(B)", "expect": "True"},
        ],
        "approaches": {
            "Three separate passes": {
                "idea": [
                    "The board is valid when no digit repeats in any row, any column or any 3×3 box. Check each of the three families separately.",
                    "One helper <code>ok(cells)</code> answers the question for any group of 9 cells: drop the dots and compare the count with the count of distinct digits.",
                ],
                "steps": [
                    "<code>ok(cells)</code> keeps <code>digits = [c for c in cells if c != \".\"]</code> and returns <code>len(digits) == len(set(digits))</code>.",
                    "<code>rows</code>: <code>ok(row)</code> for all 9 rows.",
                    "<code>cols</code>: build column c as <code>[board[r][c] for r in range(9)]</code> and check all 9.",
                    "<code>boxes</code>: for each top-left corner <code>(br, bc)</code> in {0, 3, 6}², collect its 9 cells and check them.",
                    "Return <code>rows and cols and boxes</code>.",
                ],
                "why": [
                    "A set removes duplicates, so the lengths differ exactly when some digit repeats in that group. The 27 groups are precisely the Sudoku rules.",
                    "Only filled cells are checked; the board does not have to be solvable, just consistent.",
                    "Each of the 3 passes reads 81 cells: <strong>O(81 × 3)</strong>, i.e. constant time for a fixed 9×9 board. Each <code>ok</code> call builds a set of at most 9 digits: <strong>O(9)</strong> space.",
                ],
                "dry": [
                    [
                        "Rows: every row passes; row 0 is now 8, 3, 7, with no repeat.",
                        "Columns: column 0 is 8, 6, 4, 7 plus another 8 at row 3. 5 digits but only 4 distinct, so <code>cols</code> is False.",
                        "Boxes: box 0 holds 8, 3, 6, 9, 8, so it fails too.",
                        "It returns <strong>False</strong>.",
                    ],
                    [
                        "Rows: all 9 pass.",
                        "Columns: all 9 pass.",
                        "Boxes: all 9 pass.",
                        "It returns <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Does it stop as soon as a row fails?",
                     "Within one family yes, because <code>all</code> short-circuits. But <code>rows</code>, <code>cols</code> and <code>boxes</code> are computed as separate statements, so all three families are always evaluated."],
                    ["Why ignore the dots?",
                     "Empty cells repeat all the time; only filled digits must be unique."],
                    ["Is this checking whether the puzzle is solvable?",
                     "No. A board with no conflicts can still have no solution; the problem only asks about conflicts among the filled cells."],
                ],
            },
            "One pass, 27 sets": {
                "idea": [
                    "Visit each cell once and remember, for its row, its column and its box, which digits have been seen.",
                    "The box index <code>b = (r // 3) * 3 + c // 3</code> numbers the nine boxes 0..8 left to right, top to bottom.",
                ],
                "steps": [
                    "Create 9 empty sets each for <code>rows</code>, <code>cols</code> and <code>boxes</code>.",
                    "Loop over every cell <code>(r, c)</code>; skip it if <code>d == \".\"</code>.",
                    "Compute <code>b = (r // 3) * 3 + c // 3</code>.",
                    "If <code>d</code> is already in <code>rows[r]</code>, <code>cols[c]</code> or <code>boxes[b]</code>, return <code>False</code>.",
                    "Otherwise add <code>d</code> to all three sets. Return <code>True</code> after the last cell.",
                ],
                "why": [
                    "When the second copy of a digit in some row, column or box is reached, the first copy is already in that group's set, so every conflict is caught at that moment.",
                    "It can stop at the first conflict instead of finishing three passes.",
                    "Each of the 81 cells costs three set lookups: <strong>O(81)</strong> time; the 27 sets hold at most 81 digits in total: <strong>O(81)</strong> space.",
                ],
                "dry": [
                    [
                        "Row 0: 8 (box 0), 3 (box 0), 7 (box 1). Row 1: 6 goes into box 0, then 1, 9, 5 into box 1.",
                        "Row 2: (2, 1) = 9 goes into box 0, which is now {8, 3, 6, 9}.",
                        "(2, 2) = 8: box 0 already has 8 (from (0, 0)).",
                        "It returns <strong>False</strong> before ever reaching the column clash at row 3.",
                    ],
                    [
                        "All 30 filled cells are visited in row order.",
                        "Every digit is new to its row, column and box when reached.",
                        "It returns <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["How does <code>(r // 3) * 3 + c // 3</code> work?",
                     "<code>r // 3</code> is the box row (0–2) and <code>c // 3</code> the box column (0–2). Multiplying the box row by 3 and adding the box column gives a unique number 0–8."],
                    ["Why check all three sets before adding?",
                     "Adding first would make the check always succeed. The digit must be compared against what was there before this cell."],
                    ["Could one set of tuples replace the 27 sets?",
                     "Yes: store <code>(\"r\", r, d)</code>, <code>(\"c\", c, d)</code> and <code>(\"b\", b, d)</code> in one set. Same idea, just a different container."],
                ],
            },
            "One pass, bitmasks": {
                "idea": [
                    "Same single pass, but each row, column and box keeps its seen digits as bits of one integer instead of a set.",
                    "Digit d is bit d: <code>bit = 1 &lt;&lt; int(d)</code>. A clash is a bit that is already set.",
                ],
                "steps": [
                    "Create <code>rows</code>, <code>cols</code>, <code>boxes</code> as 9 zeros each.",
                    "For each filled cell, compute <code>bit = 1 &lt;&lt; int(board[r][c])</code> and the box <code>b</code>.",
                    "If <code>(rows[r] | cols[c] | boxes[b]) &amp; bit</code> is nonzero, the digit was already seen in one of the three: return <code>False</code>.",
                    "Otherwise set the bit in all three with <code>|=</code>.",
                    "Return <code>True</code> after the loop.",
                ],
                "why": [
                    "OR-ing the three masks gives every digit already present in the cell's row, column or box; AND with <code>bit</code> tests one of them in a single step.",
                    "The logic is identical to the set version, so it is correct for the same reason.",
                    "81 cells with O(1) bit operations each: <strong>O(81)</strong> time, and the state is just <strong>O(27) integers</strong>.",
                ],
                "dry": [
                    [
                        "(0, 0) = 8: bit = 256. boxes[0] becomes 256, and so do rows[0] and cols[0].",
                        "Later cells add bits 3, 6 and 9 to boxes[0].",
                        "(2, 2) = 8: boxes[0] &amp; 256 is nonzero.",
                        "It returns <strong>False</strong>.",
                    ],
                    [
                        "Each of the 30 filled cells finds its bit clear in all three masks.",
                        "Each one sets its bit in rows[r], cols[c] and boxes[b].",
                        "It returns <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>1 &lt;&lt; int(d)</code> and not <code>1 &lt;&lt; (int(d) - 1)</code>?",
                     "Either works. Using bit d wastes bit 0 but avoids an off-by-one; all that matters is that each digit gets its own bit."],
                    ["Why OR the three masks before the test?",
                     "It checks all three groups with one AND instead of three separate tests."],
                    ["Is this faster than sets?",
                     "Integer bit operations are cheaper than hashing, so yes by a constant factor. Both are constant time for a 9×9 board."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest consecutive sequence
    "longest-consecutive-sequence": {
        "examples": [
            {"call": "longest_consecutive([100, 4, 200, 1, 3, 2])", "expect": "4"},
            {"call": "longest_consecutive([1, 2, 2, 3])", "expect": "3"},
        ],
        "approaches": {
            "Count up from every element": {
                "idea": [
                    "Put all values in a set so that \"is x + 1 present?\" is O(1).",
                    "From every element, count how far the run continues upwards: x, x + 1, x + 2, …",
                ],
                "steps": [
                    "Build <code>present = set(nums)</code> and set <code>best = 0</code>.",
                    "For each <code>x</code> in <code>nums</code>, start <code>length = 1</code>.",
                    "While <code>x + length</code> is in <code>present</code>, increase <code>length</code>.",
                    "Update <code>best = max(best, length)</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "The longest run starts at some value s, and counting up from s measures it fully, so <code>best</code> reaches its length.",
                    "Counting from the middle of a run gives a shorter length, which never beats the start's count.",
                    "A run of length L is re-counted from every member, so a single long run costs about L²/2 steps: <strong>O(n²)</strong> time, with <strong>O(n)</strong> space for the set.",
                ],
                "dry": [
                    [
                        "x=100: 101 missing, length 1. x=4: 5 missing, length 1. x=200: length 1.",
                        "x=1: 2, 3, 4 present, 5 missing. length 4, best = 4.",
                        "x=3: 4 present, length 2. x=2: 3, 4 present, length 3.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "present = {1, 2, 3}.",
                        "x=1: 2, 3 present, length 3. best = 3.",
                        "x=2: length 2. x=2 again: length 2 (duplicates are re-counted). x=3: length 1.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why use a set instead of <code>x + length in nums</code>?",
                     "Membership in a list is O(n), which would make the whole thing cubic. The set makes each test O(1)."],
                    ["What does an empty input return?",
                     "The loop never runs, so <code>best</code> stays 0, which is correct."],
                    ["What is the one change that makes this linear?",
                     "Only count from values where <code>x - 1</code> is absent, i.e. run starts. That is the hash set approach below."],
                ],
            },
            "Sort and scan": {
                "idea": [
                    "After sorting, consecutive values sit next to each other, so a run is a stretch where each value is the previous plus one.",
                    "Duplicates sit next to each other too and must be skipped without breaking the run.",
                ],
                "steps": [
                    "Return 0 for an empty list.",
                    "Sort; set <code>best = cur = 1</code>.",
                    "For adjacent pairs <code>(a, b)</code>: if <code>b == a + 1</code>, extend with <code>cur += 1</code> and update <code>best</code>.",
                    "Else if <code>b != a</code>, the run broke: <code>cur = 1</code>.",
                    "If <code>b == a</code>, do nothing. Return <code>best</code>.",
                ],
                "why": [
                    "In sorted order, a consecutive run with duplicates appears as one stretch where every step is +1 or +0, so <code>cur</code> counts its distinct values.",
                    "A step bigger than 1 ends the run, and <code>cur</code> restarts at the new value.",
                    "Sorting is <strong>O(n log n)</strong> time; the sorted copy is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "sorted = [1, 2, 3, 4, 100, 200].",
                        "(1,2), (2,3), (3,4) each extend: cur = 4, best = 4.",
                        "(4,100) breaks: cur = 1. (100,200) breaks: cur = 1.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "sorted = [1, 2, 2, 3].",
                        "(1,2): cur = 2, best = 2. (2,2): equal, nothing changes.",
                        "(2,3): cur = 3, best = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>elif b != a</code> instead of a plain <code>else</code>?",
                     "With a plain <code>else</code> a duplicate would reset the run: [1, 2, 2, 3] would give 2 instead of 3."],
                    ["Why start <code>best</code> at 1?",
                     "Any non-empty input has a run of length at least 1, and a list with a single value never enters the loop."],
                    ["Is O(n log n) acceptable?",
                     "It is simple and robust, but the problem explicitly asks for O(n), which needs the hash set."],
                ],
            },
            "Hash set, count only from run starts": {
                "idea": [
                    "A value <code>x</code> starts a run exactly when <code>x - 1</code> is not present. Only count from those starts.",
                    "Then every run is walked once, from its start, instead of once from every member.",
                ],
                "steps": [
                    "Build <code>present = set(nums)</code>, <code>best = 0</code>.",
                    "Loop <code>x</code> over <code>present</code> (so duplicates are seen once).",
                    "If <code>x - 1 not in present</code>, x starts a run: count <code>length</code> while <code>x + length</code> is present.",
                    "Update <code>best</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Every run has exactly one start, and counting from it measures the whole run, so the longest run is found.",
                    "The inner <code>while</code> runs only from starts, and each value belongs to one run, so all inner steps together total at most n: <strong>O(n)</strong> time overall.",
                    "The set holds the distinct values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "The set iterates as 1, 2, 3, 100, 4, 200.",
                        "x=1: 0 missing, so a start. 2, 3, 4 present: length 4, best = 4.",
                        "x=2, 3, 4: their predecessors exist, skipped.",
                        "x=100 and x=200: starts with length 1. It returns <strong>4</strong>.",
                    ],
                    [
                        "present = {1, 2, 3}; the duplicate 2 is gone.",
                        "x=1: a start. 2, 3 present: length 3.",
                        "x=2 and x=3 are skipped.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why loop over <code>present</code> rather than <code>nums</code>?",
                     "Looping over <code>nums</code> would re-count a run start once per duplicate, e.g. [1, 1, 1, …, 2, 3, …] could become quadratic."],
                    ["There is a while loop inside a for loop. Why is it not O(n²)?",
                     "The while only runs from run starts, and runs do not overlap, so across the whole loop it advances at most n times in total."],
                    ["Does it handle negative numbers?",
                     "Yes. <code>x - 1</code> and <code>x + length</code> are just integer arithmetic on set members."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ best time to buy and sell stock II
    "best-time-stock-ii": {
        "examples": [
            {"call": "max_profit([1, 5, 3, 6])", "expect": "7"},
            {"call": "max_profit([5, 3, 1])", "expect": "0"},
        ],
        "approaches": {
            "Try every buy/sell decision": {
                "idea": [
                    "Each day you either act or skip. If you hold a share you may sell; if not, you may buy.",
                    "<code>best(day, holding)</code> tries both choices recursively and returns the best total profit from that day on.",
                ],
                "steps": [
                    "If <code>day == len(prices)</code>, no days remain: return 0.",
                    "<code>skip = best(day + 1, holding)</code>: do nothing today.",
                    "If holding, the alternative is to sell: <code>prices[day] + best(day + 1, False)</code>.",
                    "If not holding, the alternative is to buy: <code>-prices[day] + best(day + 1, True)</code>.",
                    "Return the max; the answer is <code>best(0, False)</code>.",
                ],
                "why": [
                    "Every valid sequence of buys and sells corresponds to one path of choices, and the recursion takes the maximum over all paths.",
                    "Each call spawns up to two calls, so with n days there are up to 2<sup>n+1</sup> − 1 calls: <strong>O(2<sup>n</sup>)</strong> time.",
                    "The recursion is n levels deep: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "best(0, False) explores 31 calls in total for 4 days.",
                        "The winning path: buy at 1 (−1), sell at 5 (+5), buy at 3 (−3), sell at 6 (+6).",
                        "Alternatives such as buying at 1 and holding to 6 give only 5.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "best(0, False) explores 15 calls for 3 days.",
                        "Every buy is followed only by lower prices, so any trade loses money.",
                        "Skipping every day gives 0, the maximum.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["What if the path ends while still holding?",
                     "The base case returns 0, so the purchase price is simply lost. Such a path is never better than not buying, so it never wins."],
                    ["How do I make this efficient?",
                     "There are only 2n distinct (day, holding) states. Memoising them, or filling them bottom-up, gives the O(n) DP below."],
                    ["Why is it marked small?",
                     "Exponential time: it is only run on tiny inputs to illustrate the state space."],
                ],
            },
            "DP over (day, holding)": {
                "idea": [
                    "Track two numbers per day: <code>cash[i]</code>, the best profit at the end of day i holding nothing, and <code>hold[i]</code>, the best profit holding one share.",
                    "Each is either yesterday's same state (do nothing) or the other state plus today's trade.",
                ],
                "steps": [
                    "Create <code>cash</code> and <code>hold</code> of length n; <code>hold[0] = -prices[0]</code> (bought on day 0), <code>cash[0] = 0</code>.",
                    "For each day i from 1: <code>cash[i] = max(cash[i-1], hold[i-1] + prices[i])</code>, keep cash or sell today.",
                    "<code>hold[i] = max(hold[i-1], cash[i-1] - prices[i])</code>, keep holding or buy today.",
                    "Return <code>cash[-1]</code>: ending without a share is always at least as good.",
                ],
                "why": [
                    "Any strategy's state at the end of day i is either \"holding\" or \"not holding\", and its best value depends only on day i − 1's two values, so the recurrence covers all strategies.",
                    "One loop of n − 1 steps: <strong>O(n)</strong> time.",
                    "Two arrays of length n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Day 0: cash 0, hold −1.",
                        "Day 1 (5): cash = max(0, −1 + 5) = 4, hold = max(−1, 0 − 5) = −1.",
                        "Day 2 (3): cash = max(4, −1 + 3) = 4, hold = max(−1, 4 − 3) = 1.",
                        "Day 3 (6): cash = max(4, 1 + 6) = 7. It returns <strong>7</strong>.",
                    ],
                    [
                        "Day 0: cash 0, hold −5.",
                        "Day 1 (3): cash = max(0, −2) = 0, hold = max(−5, −3) = −3.",
                        "Day 2 (1): cash = max(0, −2) = 0, hold = −1.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return <code>cash[-1]</code> and not <code>max(cash[-1], hold[-1])</code>?",
                     "<code>hold[-1]</code> counts a share bought but not sold; selling it would only add its price, so <code>cash[-1]</code> is always at least as large."],
                    ["Can I buy and sell on the same day?",
                     "Here it makes no difference: it earns 0. Both updates use yesterday's values, so the recurrence never needs it."],
                    ["What does it do on an empty list?",
                     "<code>prices[0]</code> would raise IndexError. The problem guarantees at least one price."],
                ],
            },
            "DP with two rolling variables": {
                "idea": [
                    "Day i only needs day i − 1's <code>cash</code> and <code>hold</code>, so keep just two variables instead of two arrays.",
                    "A tuple assignment updates both from the old values at once.",
                ],
                "steps": [
                    "Start with <code>cash, hold = 0, -prices[0]</code>.",
                    "For each later price <code>p</code>:",
                    "<code>cash, hold = max(cash, hold + p), max(hold, cash - p)</code>.",
                    "The right side is evaluated fully before either name is rebound, so both use yesterday's values.",
                    "Return <code>cash</code>.",
                ],
                "why": [
                    "It is the same recurrence as the array version, with the arrays shrunk to their last entry.",
                    "One pass: <strong>O(n)</strong> time.",
                    "Two variables: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start: cash 0, hold −1.",
                        "p=5: cash 4, hold −1. p=3: cash 4, hold 1.",
                        "p=6: cash 7, hold 1.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "Start: cash 0, hold −5.",
                        "p=3: cash 0, hold −3.",
                        "p=1: cash 0, hold −1.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong with two separate assignments?",
                     "If <code>cash</code> is updated first, <code>hold = max(hold, cash - p)</code> would use today's new cash, allowing a sell and re-buy using today's value. It happens to give the same answer here, but the tuple form is the faithful recurrence."],
                    ["Is this the same as the greedy approach?",
                     "It produces the same number. The DP generalises to fees and cooldowns, where greedy does not."],
                    ["Why <code>prices[1:]</code>?",
                     "Day 0 is already accounted for in the starting values."],
                ],
            },
            "Greedy: sum every rise": {
                "idea": [
                    "With unlimited trades, any rising stretch can be captured fully by buying at its bottom and selling at its top.",
                    "That profit equals the sum of the daily increases inside it, so just add every positive day-to-day change.",
                ],
                "steps": [
                    "Pair each day with the next: <code>zip(prices, prices[1:])</code>.",
                    "For each pair <code>(a, b)</code>, take <code>max(0, b - a)</code>.",
                    "Sum them.",
                    "Return the total.",
                ],
                "why": [
                    "Any trade from day i to j earns the sum of the changes between them, which is at most the sum of the positive changes in that range, so no strategy beats the greedy total.",
                    "The greedy total is achievable: buy before each rise, sell after it.",
                    "One pass: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Changes: 1→5 = +4, 5→3 = −2, 3→6 = +3.",
                        "Keep the positives: 4 + 0 + 3.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "Changes: 5→3 = −2, 3→1 = −2.",
                        "Both clipped to 0.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Does it model real trades?",
                     "Yes. Consecutive rises like 1→2→3 are one buy at 1 and one sell at 3; the sum 1 + 1 equals 3 − 1."],
                    ["Why does this fail for problem I (one transaction)?",
                     "With one trade you cannot skip the dips in between, so adding separate rises overcounts."],
                    ["What about a single price?",
                     "<code>prices[1:]</code> is empty, so there are no pairs and the sum is 0."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ majority element II
    "majority-element-ii": {
        "examples": [
            {"call": "sorted(majority_element_ii([1, 2, 1, 3, 1, 2, 2]))", "expect": "[1, 2]"},
            {"call": "sorted(majority_element_ii([1, 2, 3]))", "expect": "[]"},
        ],
        "approaches": {
            "Hash map of counts": {
                "idea": [
                    "Count every value and keep those with more than <code>n // 3</code> occurrences.",
                    "At most two values can pass, since three would need more than n elements.",
                ],
                "steps": [
                    "Build <code>Counter(nums)</code>.",
                    "Compute the threshold <code>len(nums) // 3</code>.",
                    "Keep every <code>x</code> whose count <code>c</code> is greater than the threshold.",
                    "Return that list.",
                ],
                "why": [
                    "Exact counts make the test exact; nothing is guessed.",
                    "Counting and filtering are both linear: <strong>O(n)</strong> time.",
                    "The Counter may hold n distinct keys: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "counts = {1: 3, 2: 3, 3: 1}, threshold 7 // 3 = 2.",
                        "1 and 2 have 3 &gt; 2; 3 has 1.",
                        "It returns [1, 2], sorted: <strong>[1, 2]</strong>.",
                    ],
                    [
                        "counts = {1: 1, 2: 1, 3: 1}, threshold 1.",
                        "No count is greater than 1.",
                        "It returns <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt; n // 3</code> and not <code>&gt; n / 3</code>?",
                     "For integer counts they are equivalent: c &gt; n/3 exactly when c &gt; floor(n/3). Integer division just avoids floats."],
                    ["Can the answer have three values?",
                     "No. Three values each with more than n/3 copies would need more than n elements."],
                    ["Why sort in the example call?",
                     "The order of the result depends on the approach, so sorting makes the expected answer unique."],
                ],
            },
            "Sort and measure runs": {
                "idea": [
                    "After sorting, each value's copies form one contiguous run, so its count is the run length.",
                    "Walk the runs and keep values whose run is longer than <code>n // 3</code>.",
                ],
                "steps": [
                    "Sort into <code>nums</code>; start <code>i = 0</code>.",
                    "Advance <code>j</code> from <code>i</code> while <code>nums[j] == nums[i]</code>; the run is <code>nums[i:j]</code>.",
                    "If <code>j - i &gt; len(nums) // 3</code>, append <code>nums[i]</code>.",
                    "Jump <code>i = j</code> to the next run.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Every value is measured by exactly one run, so the counts are exact.",
                    "<code>i</code> and <code>j</code> only move forward, so after sorting the scan is O(n): <strong>O(n log n)</strong> total.",
                    "<code>sorted</code> makes a copy: <strong>O(n)</strong> space (O(1) extra if sorting in place were allowed).",
                ],
                "dry": [
                    [
                        "sorted = [1, 1, 1, 2, 2, 2, 3], threshold 2.",
                        "Run of 1s: length 3 &gt; 2, keep. Run of 2s: length 3, keep.",
                        "Run of 3: length 1, skip.",
                        "It returns <strong>[1, 2]</strong>.",
                    ],
                    [
                        "sorted = [1, 2, 3], threshold 1.",
                        "Three runs of length 1, none longer than 1.",
                        "It returns <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the inner while not quadratic?",
                     "<code>i</code> jumps to <code>j</code>, so every index is passed by <code>j</code> once overall."],
                    ["Does it need the bounds check <code>j &lt; len(nums)</code>?",
                     "Yes. The last run reaches the end of the list, and without the check <code>nums[j]</code> would raise IndexError."],
                    ["Is the output sorted?",
                     "Yes, as a side effect, since runs are visited in increasing order."],
                ],
            },
            "Boyer-Moore with two candidates": {
                "idea": [
                    "Generalise majority voting: keep two candidates with vote counts, and cancel <em>three distinct values</em> at a time.",
                    "Any value with more than n/3 copies cannot be fully cancelled, so it survives as a candidate. Candidates must then be verified by counting.",
                ],
                "steps": [
                    "Start with <code>c1 = c2 = None</code>, <code>v1 = v2 = 0</code>.",
                    "For each <code>x</code>: if it equals <code>c1</code> or <code>c2</code>, add a vote to that one.",
                    "Else if a slot is empty (<code>v1 == 0</code>, then <code>v2 == 0</code>), make <code>x</code> its candidate with 1 vote.",
                    "Otherwise <code>x</code> differs from both: decrement both votes (one triple cancelled).",
                    "Return the candidates that are not <code>None</code> and whose real count exceeds <code>len(nums) // 3</code>.",
                ],
                "why": [
                    "Each cancellation removes three different values. A value with more than n/3 copies cannot lose all of them, since there are fewer than n/3 triples, so it ends as a candidate.",
                    "Surviving candidates may still be below the threshold, which is why the final <code>nums.count</code> check is required.",
                    "One voting pass plus up to two counting passes: <strong>O(n)</strong> time, and four variables: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "1: c1=1 (1). 2: c2=2 (1). 1: v1=2. 3: differs, v1=1, v2=0.",
                        "1: v1=2. 2: v2 is 0 but 2 == c2, so v2=1. 2: v2=2.",
                        "Candidates 1 and 2; counts 3 and 3, both &gt; 2.",
                        "It returns <strong>[1, 2]</strong> after sorting.",
                    ],
                    [
                        "1: c1=1. 2: c2=2.",
                        "3: differs from both, v1=0, v2=0.",
                        "Candidates 1 and 2 each appear once, not &gt; 1.",
                        "It returns <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>x == c1</code> and <code>x == c2</code> before the empty slots?",
                     "A candidate whose votes dropped to 0 can still match. Checking equality first stops the same value from taking both slots."],
                    ["Why is the verification step required?",
                     "In [1, 2, 3] the candidates 1 and 2 survive but appear only once each. Without counting they would be returned wrongly."],
                    ["Why iterate over <code>{c1, c2}</code>?",
                     "If both slots ended with the same value, the set prevents reporting it twice."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subarray sum equals k
    "subarray-sum-equals-k": {
        "examples": [
            {"call": "subarray_sum([1, 2, 3, -3, 3], 3)", "expect": "5"},
            {"call": "subarray_sum([1, -1, 0], 0)", "expect": "3"},
        ],
        "approaches": {
            "Every subarray, summed from scratch": {
                "idea": [
                    "A subarray is a start <code>i</code> and an end <code>j ≥ i</code>. Enumerate every pair and sum the slice.",
                    "Count how many slices sum exactly to <code>k</code>.",
                ],
                "steps": [
                    "Let <code>n = len(nums)</code>.",
                    "Generate every <code>(i, j)</code> with <code>0 ≤ i ≤ j &lt; n</code>.",
                    "Compute <code>sum(nums[i:j + 1])</code> for each.",
                    "Count those equal to <code>k</code> and return the count.",
                ],
                "why": [
                    "Every subarray is exactly one (i, j) pair, so all are counted once.",
                    "There are about n²/2 pairs and each slice sum is O(n): <strong>O(n³)</strong> time.",
                    "The generator keeps one slice at a time; nothing grows with the number of pairs (the label says <strong>O(1)</strong>, ignoring the temporary slice).",
                ],
                "dry": [
                    [
                        "Start 0: [1, 2] = 3 and [1, 2, 3, −3] = 3 match.",
                        "Start 2: [3] = 3 and [3, −3, 3] = 3 match.",
                        "Start 4: [3] = 3 matches. Starts 1 and 3 give none.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "Start 0: [1, −1] = 0 and [1, −1, 0] = 0 match.",
                        "Start 1: [−1] and [−1, 0] are −1.",
                        "Start 2: [0] = 0 matches. It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>j + 1</code> in the slice?",
                     "The subarray includes index j, and slices exclude their end."],
                    ["Why not a sliding window?",
                     "With negative numbers, growing the window can lower the sum, so there is no rule for which end to move."],
                    ["Is this ever useful?",
                     "Only as a reference checker for tiny inputs; the tests use exactly this as the brute force."],
                ],
            },
            "Every start, running sum": {
                "idea": [
                    "For a fixed start <code>i</code>, extending the end by one only adds <code>nums[j]</code> to the previous sum.",
                    "Keep a running <code>total</code> instead of re-summing each slice.",
                ],
                "steps": [
                    "Set <code>count = 0</code>.",
                    "For each start <code>i</code>, reset <code>total = 0</code>.",
                    "For <code>j</code> from <code>i</code> to the end: <code>total += nums[j]</code>.",
                    "Add 1 to <code>count</code> when <code>total == k</code> (<code>count += total == k</code> adds True as 1).",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "After the inner step for j, <code>total</code> is exactly <code>sum(nums[i:j+1])</code>, so every subarray is tested once.",
                    "n starts with up to n extensions each: <strong>O(n²)</strong> time.",
                    "Just <code>count</code> and <code>total</code>: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: totals 1, 3, 6, 3, 6 → 2 matches.",
                        "i=1: totals 2, 5, 2, 5 → 0. i=2: totals 3, 0, 3 → 2.",
                        "i=3: totals −3, 0 → 0. i=4: total 3 → 1.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "i=0: totals 1, 0, 0 → 2 matches.",
                        "i=1: totals −1, −1 → 0.",
                        "i=2: total 0 → 1. It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not stop when <code>total</code> exceeds <code>k</code>?",
                     "Negative numbers can bring it back down: from start 0 the total goes 6 then back to 3."],
                    ["Is <code>count += total == k</code> safe?",
                     "Yes. <code>True</code> and <code>False</code> are the integers 1 and 0 in Python."],
                    ["What does the hash map version improve?",
                     "It removes the inner loop by remembering how many earlier prefixes had each sum."],
                ],
            },
            "Prefix sums and a hash map": {
                "idea": [
                    "The sum of <code>nums[i:j+1]</code> is prefix(j + 1) − prefix(i). It equals <code>k</code> exactly when an earlier prefix equals <code>total - k</code>.",
                    "Keep a Counter <code>seen</code> of how many earlier prefixes had each value, and add that many to the answer at each step.",
                ],
                "steps": [
                    "Start with <code>seen = Counter({0: 1})</code>: the empty prefix has sum 0.",
                    "Set <code>total = count = 0</code>.",
                    "For each <code>x</code>: <code>total += x</code>.",
                    "Add <code>seen[total - k]</code> to <code>count</code>: one subarray ending here for each earlier matching prefix.",
                    "Then record the current prefix: <code>seen[total] += 1</code>. Return <code>count</code>.",
                ],
                "why": [
                    "Each subarray ending at the current index corresponds to exactly one earlier prefix, and it sums to k exactly when that prefix is <code>total - k</code>, so the Counter lookup counts them all.",
                    "Recording the current prefix <em>after</em> the lookup prevents counting an empty subarray when k = 0.",
                    "One pass with O(1) Counter work per element: <strong>O(n)</strong> time; up to n + 1 distinct prefixes: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "x=1: total 1, need −2, add 0. seen = {0:1, 1:1}.",
                        "x=2: total 3, need 0, add 1 (count 1). x=3: total 6, need 3, add 1 (count 2).",
                        "x=−3: total 3, need 0, add 1 (count 3). seen[3] = 2.",
                        "x=3: total 6, need 3, add 2 (count 5). It returns <strong>5</strong>.",
                    ],
                    [
                        "x=1: total 1, need 1, add 0. seen = {0:1, 1:1}.",
                        "x=−1: total 0, need 0, add 1 (count 1). seen[0] = 2.",
                        "x=0: total 0, need 0, add 2 (count 3). seen[0] = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why initialise <code>seen</code> with <code>{0: 1}</code>?",
                     "It stands for the empty prefix before index 0. Without it, a subarray starting at index 0, like [1, 2] in the first example, would never be counted."],
                    ["Why look up before incrementing <code>seen[total]</code>?",
                     "Otherwise, with k = 0 the lookup finds the current prefix itself and counts an empty subarray: [1, −1, 0] would give 6 instead of 3."],
                    ["Why a count per prefix and not a set?",
                     "Several earlier prefixes can share a value (sum 3 appears twice in the first example), and each one starts a different subarray."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ first missing positive
    "first-missing-positive": {
        "examples": [
            {"call": "first_missing_positive([3, 4, -1, 1])", "expect": "2"},
            {"call": "first_missing_positive([2, 2, 1])", "expect": "3"},
        ],
        "approaches": {
            "Try 1, 2, 3, &hellip; with a linear search": {
                "idea": [
                    "Ask directly: is 1 in the list? Is 2? Stop at the first number that is not.",
                    "The answer is at most n + 1, because n numbers can cover at most 1..n.",
                ],
                "steps": [
                    "Set <code>x = 1</code>.",
                    "While <code>x in nums</code> (a linear scan of the list), increase <code>x</code>.",
                    "The loop stops at the first positive integer not present.",
                    "Return <code>x</code>.",
                ],
                "why": [
                    "Candidates are tried in increasing order, so the first one missing is the smallest missing positive.",
                    "Up to n + 1 candidates, each costing an O(n) list scan: <strong>O(n²)</strong> time.",
                    "No extra storage: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "x=1: found at index 3.",
                        "x=2: scan all four elements, not found.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "x=1: found.",
                        "x=2: found. x=3: not found.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Can the loop run forever?",
                     "No. A list of n elements can contain at most n of the values 1, 2, 3, …, so some x ≤ n + 1 is missing."],
                    ["What about negatives and zero?",
                     "They are never asked about, since x starts at 1 and only grows."],
                    ["How is the hash set version different?",
                     "It is exactly this loop with <code>in</code> on a set, which turns each O(n) scan into O(1)."],
                ],
            },
            "Sort, then walk": {
                "idea": [
                    "In sorted order, the positives appear increasing. Keep <code>want</code>, the smallest positive not seen yet.",
                    "Every time the next value equals <code>want</code>, the next positive becomes the target.",
                ],
                "steps": [
                    "Set <code>want = 1</code>.",
                    "Loop <code>x</code> over <code>sorted(nums)</code>.",
                    "If <code>x == want</code>, increase <code>want</code>.",
                    "Everything else (negatives, zero, duplicates, values past a gap) is ignored.",
                    "Return <code>want</code>.",
                ],
                "why": [
                    "Values come in increasing order, so if <code>want</code> is present it is reached before anything larger; once it is skipped past, it can never appear later.",
                    "Duplicates do no harm: the second copy no longer equals <code>want</code>.",
                    "Sorting is <strong>O(n log n)</strong> time; the copy is <strong>O(n)</strong> space (O(1) with an in-place sort).",
                ],
                "dry": [
                    [
                        "sorted = [−1, 1, 3, 4].",
                        "−1: not 1. 1: equals want, want = 2.",
                        "3 and 4: not 2.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "sorted = [1, 2, 2].",
                        "1: want = 2. 2: want = 3.",
                        "2 (duplicate): not 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not break as soon as <code>x &gt; want</code>?",
                     "You could; it is a valid early exit. The answer is the same either way."],
                    ["Why do duplicates not cause problems?",
                     "After the first copy matched, <code>want</code> has moved on, so the next copy is just ignored."],
                    ["Is sorting allowed by the problem?",
                     "It gives the right answer, but the problem asks for O(n) time and O(1) space, which needs cyclic sort."],
                ],
            },
            "Hash set": {
                "idea": [
                    "Same as trying 1, 2, 3, … but with a set, so each membership test is O(1).",
                    "Only one pass is needed to build the set.",
                ],
                "steps": [
                    "Build <code>present = set(nums)</code>.",
                    "Set <code>x = 1</code>.",
                    "While <code>x in present</code>, increase <code>x</code>.",
                    "Return <code>x</code>.",
                ],
                "why": [
                    "Candidates are tried in increasing order, so the first one missing from the set is the answer.",
                    "The while loop runs at most n + 1 times, each O(1): <strong>O(n)</strong> time.",
                    "The set holds up to n values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "present = {3, 4, −1, 1}.",
                        "1 is present; 2 is not.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "present = {1, 2} (the duplicate 2 collapses).",
                        "1 and 2 are present; 3 is not.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the while loop bounded by n + 1?",
                     "The set has at most n elements, so it cannot contain all of 1..n + 1."],
                    ["Do I need to filter out negatives?",
                     "No. They sit in the set but are never asked about."],
                    ["Why not stop here in an interview?",
                     "It is O(n) time but uses O(n) memory; the problem's follow-up wants O(1) extra space."],
                ],
            },
            "Cyclic sort: put each value at its own index": {
                "idea": [
                    "The answer is in 1..n + 1, so only values in 1..n matter. Use the array itself as the set: value v belongs at index v − 1.",
                    "Swap values to their home slots; afterwards the first index i whose value is not i + 1 gives the answer.",
                ],
                "steps": [
                    "For each index <code>i</code>: while <code>1 &lt;= nums[i] &lt;= n</code> and <code>nums[nums[i] - 1] != nums[i]</code>, swap <code>nums[i]</code> into its home <code>j = nums[i] - 1</code>.",
                    "The second condition stops when the home already holds the right value, which also handles duplicates.",
                    "Values out of range (≤ 0 or &gt; n) are left wherever they are.",
                    "Scan again: return <code>i + 1</code> for the first <code>nums[i] != i + 1</code>.",
                    "If every slot is correct, return <code>n + 1</code>.",
                ],
                "why": [
                    "After the first loop, every value v in 1..n that appears is at index v − 1, so slot i holds i + 1 exactly when i + 1 is present.",
                    "Each swap places one value in its final home, where it is never moved again, so there are at most n swaps in total: <strong>O(n)</strong> time despite the nested loop.",
                    "Swaps are done in place: <strong>O(1)</strong> extra space (the input list is modified).",
                ],
                "dry": [
                    [
                        "i=0: 3 goes to index 2 → [−1, 4, 3, 1]; −1 is out of range, stop.",
                        "i=1: 4 goes to index 3 → [−1, 1, 3, 4]; then 1 goes to index 0 → [1, −1, 3, 4]; −1 stops.",
                        "i=2 and i=3 already hold 3 and 4.",
                        "Scan: index 1 holds −1, not 2. It returns <strong>2</strong>.",
                    ],
                    [
                        "i=0: 2's home index 1 already holds 2 (a duplicate), so no swap.",
                        "i=1: 2 is home. i=2: 1 goes to index 0 → [1, 2, 2]; now 2's home already holds 2, stop.",
                        "Scan: indices 0 and 1 are correct; index 2 holds 2, not 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>nums[nums[i] - 1] != nums[i]</code> rather than <code>nums[i] != i + 1</code>?",
                     "With duplicates the second test loops forever: in [2, 2, 1] the 2 at index 0 is not home, but its home already has a 2, so swapping changes nothing. Comparing with the home slot stops that."],
                    ["Why save <code>j = nums[i] - 1</code> before swapping?",
                     "The tuple swap assigns <code>nums[i]</code> first; if the index were written as <code>nums[nums[i] - 1]</code> it would be re-evaluated with the new value and write to the wrong slot; on [3, 4, −1, 1] that version never terminates."],
                    ["Is modifying the input acceptable?",
                     "The O(1)-space requirement essentially forces it. If the caller needs the original, they must pass a copy."],
                ],
            },
        },
    },
}
