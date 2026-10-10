"""Write-ups for the Math and Geometry topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ excel column title
    "excel-column-title": {
        "examples": [
            {"call": "convert_to_title(701)", "expect": '"ZY"'},
            {"call": "convert_to_title(52)", "expect": '"AZ"'},
        ],
        "approaches": {
            "Recursive: title of the prefix, then the last letter": {
                "idea": [
                    "Column titles are numbers written in base 26, except the digits are A..Z standing for 1..26. There is no zero digit, which is called <strong>bijective base 26</strong>.",
                    "Subtracting 1 shifts the last digit from 1..26 down to 0..25, so the last letter is <code>chr(65 + (n - 1) % 26)</code> and the rest of the title belongs to <code>(n - 1) // 26</code>.",
                    "That rest is itself a column number, so the same function can produce it recursively.",
                ],
                "steps": [
                    "Base case: if <code>n == 0</code>, there are no letters left, so return <code>\"\"</code>.",
                    "Compute <code>q, r = divmod(n - 1, 26)</code>. <code>r</code> is the 0-based last letter and <code>q</code> is the number the remaining letters spell.",
                    "Turn <code>r</code> into a letter with <code>chr(65 + r)</code> (65 is the code of 'A').",
                    "Return <code>convert_to_title(q) + chr(65 + r)</code>: the prefix's title followed by the last letter.",
                ],
                "why": [
                    "Writing n = 26·q + (r + 1) with 0 ≤ r ≤ 25 is exactly what <code>divmod(n - 1, 26)</code> computes, and a bijective base-26 number ends in digit r + 1 with the prefix worth q.",
                    "The \"minus one\" is applied freshly at every level, so every digit uses the 1-based rule, not only the last one.",
                    "Each call removes one letter and divides n by about 26, so there are about log<sub>26</sub> n calls: <strong>O(log n)</strong> time.",
                    "The recursion stack and the string being built are both one entry per letter: <strong>O(log n)</strong> space.",
                ],
                "dry": [
                    [
                        "convert_to_title(701): divmod(700, 26) = (26, 24), so the last letter is chr(65 + 24) = 'Y'.",
                        "convert_to_title(26): divmod(25, 26) = (0, 25), so the letter is 'Z'. A plain base-26 conversion would give \"A0\" here.",
                        "convert_to_title(0) returns \"\".",
                        "Unwinding: \"\" + \"Z\" = \"Z\", then \"Z\" + \"Y\" = <strong>\"ZY\"</strong>.",
                    ],
                    [
                        "convert_to_title(52): divmod(51, 26) = (1, 25), so the last letter is 'Z'.",
                        "convert_to_title(1): divmod(0, 26) = (0, 0), so the letter is 'A'.",
                        "convert_to_title(0) returns \"\".",
                        "Unwinding gives \"A\" then \"AZ\": <strong>\"AZ\"</strong>. Plain <code>divmod(52, 26)</code> would have said (2, 0), the wrong split.",
                    ],
                ],
                "faq": [
                    ["Why not just use <code>n % 26</code> and <code>n // 26</code>?",
                     "Because 26 must map to 'Z', but <code>26 % 26</code> is 0 and there is no letter for 0. Subtracting 1 first maps 1..26 onto 0..25, which lines up with A..Z."],
                    ["Why is the base case <code>n == 0</code> and not <code>n &lt;= 26</code>?",
                     "With n = 0 as the stop, the last letter is produced by the same divmod as every other letter, so there is no special case to get wrong. The extra call costs nothing."],
                    ["Can the recursion get too deep?",
                     "No. Even 2<sup>31</sup> − 1 is only 7 letters long (\"FXSHRXW\"), so the depth is at most 7 for 32-bit inputs."],
                ],
            },
            "Bijective base 26: subtract one per digit": {
                "idea": [
                    "This is the recursive idea written as a loop: peel off the last letter, then continue with what is left.",
                    "Each round subtracts 1, takes the remainder as a 0-based letter, and divides by 26.",
                    "Letters come out last-first, so they are collected in a list and reversed at the end.",
                ],
                "steps": [
                    "Start with an empty list <code>out</code>.",
                    "While <code>n</code> is not 0, compute <code>n, r = divmod(n - 1, 26)</code>.",
                    "Append <code>chr(65 + r)</code> to <code>out</code>; this is the lowest letter not yet produced.",
                    "When <code>n</code> reaches 0, every letter is in <code>out</code>, lowest first.",
                    "Return <code>\"\".join(reversed(out))</code>.",
                ],
                "why": [
                    "After <code>n, r = divmod(n - 1, 26)</code>, the new n is the value of the remaining prefix, which is again a 1-based column number, so the next round applies the same rule.",
                    "The loop stops exactly when no letters remain, because only n = 0 has an empty title.",
                    "One round per letter: <strong>O(log n)</strong> time, and the list holds one character per letter, <strong>O(log n)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 701: divmod(700, 26) = (26, 24). Append 'Y', n = 26.",
                        "n = 26: divmod(25, 26) = (0, 25). Append 'Z', n = 0.",
                        "The loop stops with out = ['Y', 'Z'].",
                        "Reversed and joined: <strong>\"ZY\"</strong>.",
                    ],
                    [
                        "n = 52: divmod(51, 26) = (1, 25). Append 'Z', n = 1.",
                        "n = 1: divmod(0, 26) = (0, 0). Append 'A', n = 0.",
                        "The loop stops with out = ['Z', 'A'].",
                        "Reversed and joined: <strong>\"AZ\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why collect into a list and reverse, rather than prepend to a string?",
                     "Prepending copies the whole string each time. For a handful of letters it does not matter, but append-then-reverse is the habit that stays linear."],
                    ["How do I go the other way, title to number?",
                     "Read left to right with <code>v = v * 26 + (ord(ch) - 64)</code>. Because the digits are 1..26 there is no subtraction needed in that direction."],
                    ["What happens for n = 0?",
                     "The loop never runs and the answer is the empty string. The problem guarantees n ≥ 1, so this never reaches a caller."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ gcd of strings
    "gcd-of-strings": {
        "examples": [
            {"call": 'gcd_of_strings("ABABAB", "ABAB")', "expect": '"AB"'},
            {"call": 'gcd_of_strings("ABAB", "ABA")', "expect": '""'},
        ],
        "approaches": {
            "Try every prefix length, longest first": {
                "idea": [
                    "A string x divides s when s is x repeated some whole number of times. Any common divisor must be a <strong>prefix of both</strong> strings.",
                    "Its length L must also divide both <code>len(str1)</code> and <code>len(str2)</code>, otherwise whole copies cannot fit.",
                    "Trying lengths from longest to shortest means the first one that works is the greatest.",
                ],
                "steps": [
                    "Loop <code>L</code> from <code>min(len(str1), len(str2))</code> down to 1.",
                    "Skip <code>L</code> unless it divides both lengths.",
                    "Take the candidate <code>x = str1[:L]</code>.",
                    "If <code>x * (len(str1) // L) == str1</code> and <code>x * (len(str2) // L) == str2</code>, return <code>x</code>.",
                    "If no length works, return <code>\"\"</code>.",
                ],
                "why": [
                    "Every possible divisor has some length L ≤ the shorter length and must equal <code>str1[:L]</code>, so the loop considers every candidate.",
                    "Going from long to short, the first success is the longest common divisor.",
                    "Each candidate that passes the length test costs O(m + n) to rebuild and compare, and up to min(m, n) lengths are tried: <strong>O(min(m, n) · (m + n))</strong> time.",
                    "The repeated strings built for the comparison take <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "Lengths 6 and 4; L starts at 4.",
                        "L = 4: 6 % 4 = 2, skip. L = 3: 4 % 3 = 1, skip.",
                        "L = 2: divides both. x = \"AB\"; \"AB\" × 3 = \"ABABAB\" and \"AB\" × 2 = \"ABAB\". Both match.",
                        "It returns <strong>\"AB\"</strong> without trying L = 1.",
                    ],
                    [
                        "Lengths 4 and 3; L starts at 3.",
                        "L = 3: 4 % 3 = 1, skip. L = 2: 3 % 2 = 1, skip.",
                        "L = 1: divides both. x = \"A\", but \"A\" × 4 = \"AAAA\" ≠ \"ABAB\".",
                        "No length worked, so it returns <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only prefixes of <code>str1</code>?",
                     "If x repeats to form str1, then str1 starts with x. So the only candidate of length L is <code>str1[:L]</code>; nothing else needs trying."],
                    ["Is checking the length divisibility first just an optimisation?",
                     "It is required as well as fast. Without it, <code>len(str1) // L</code> rounds down and a too-short repetition could never equal the string, so the check would fail anyway, but skipping early avoids building those strings."],
                    ["What is the worst case?",
                     "Strings like \"AAAA…\" where many lengths divide both: each costs a full rebuild, giving roughly quadratic work. The concatenation test avoids all of that."],
                ],
            },
            "Concatenation test, then gcd of lengths": {
                "idea": [
                    "If both strings are repeats of the same block x, then <code>str1 + str2</code> and <code>str2 + str1</code> are both x repeated the same number of times, so they are equal.",
                    "The converse also holds: if the two concatenations are equal, both strings are powers of one common block.",
                    "Once a common block exists, the greatest one has length <code>gcd(len(str1), len(str2))</code>.",
                ],
                "steps": [
                    "Compare <code>str1 + str2</code> with <code>str2 + str1</code>.",
                    "If they differ, no common divisor exists: return <code>\"\"</code>.",
                    "Otherwise compute <code>g = math.gcd(len(str1), len(str2))</code>.",
                    "Return the prefix <code>str1[:g]</code>.",
                ],
                "why": [
                    "Equal concatenations mean the strings commute, and strings that commute are powers of a common primitive word p (a classical result on words).",
                    "Both lengths are multiples of <code>len(p)</code>, so their gcd is too, and the prefix of length gcd is p repeated, which divides both. No longer block can divide both lengths.",
                    "Building and comparing the two concatenations is <strong>O(m + n)</strong> time; the gcd of the lengths is negligible.",
                    "The two concatenated strings take <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "str1 + str2 = \"ABABAB\" + \"ABAB\" = \"ABABABABAB\".",
                        "str2 + str1 = \"ABAB\" + \"ABABAB\" = \"ABABABABAB\". They are equal.",
                        "gcd(6, 4) = 2.",
                        "It returns str1[:2] = <strong>\"AB\"</strong>.",
                    ],
                    [
                        "str1 + str2 = \"ABAB\" + \"ABA\" = \"ABABABA\".",
                        "str2 + str1 = \"ABA\" + \"ABAB\" = \"ABAABAB\".",
                        "They first differ at index 3 (B vs A), so the strings are not powers of a common block.",
                        "It returns <strong>\"\"</strong> without computing a gcd.",
                    ],
                ],
                "faq": [
                    ["Why is the prefix of length gcd guaranteed to divide both strings?",
                     "Both strings are repeats of the primitive block p, and the gcd of the lengths is a multiple of <code>len(p)</code>. So <code>str1[:g]</code> is a whole number of copies of p, and both strings are whole numbers of copies of it."],
                    ["Is the concatenation check really needed? Could I just test <code>str1[:g]</code>?",
                     "Testing the gcd prefix by repetition is also correct, because if any divisor exists the gcd-length prefix is one. The concatenation check is just a shorter way to write that test."],
                    ["What do \"ABAB\" and \"ABA\" show?",
                     "They share a long prefix, but 3 is odd, so \"ABA\" cannot be copies of \"AB\". The concatenation test catches this immediately."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ insert gcd in linked list
    "insert-gcd-linked-list": {
        "examples": [
            {"call": "to_list(insert_greatest_common_divisors(build_list([18, 6, 10, 3])))", "expect": "[18, 6, 6, 2, 10, 1, 3]"},
            {"call": "to_list(insert_greatest_common_divisors(build_list([7])))", "expect": "[7]"},
        ],
        "approaches": {
            "Walk and insert, gcd by trial division": {
                "idea": [
                    "Between every two neighbouring nodes, splice in a new node holding their greatest common divisor.",
                    "The gcd here is found the obvious way: try every candidate from <code>min(a, b)</code> downwards and return the first one that divides both.",
                    "After inserting, jump past the new node so it is never treated as an original value.",
                ],
                "steps": [
                    "Set <code>node = head</code>.",
                    "While <code>node</code> and <code>node.next</code> both exist, compute <code>gcd(node.val, node.next.val)</code>.",
                    "Inside <code>gcd</code>, loop <code>d</code> from <code>min(a, b)</code> down to 1 and return the first <code>d</code> with <code>a % d == 0 and b % d == 0</code>.",
                    "Splice: <code>node.next = ListNode(g, node.next)</code>, so the new node points at the old successor.",
                    "Move <code>node = node.next.next</code>, skipping the inserted node to land on the next original node.",
                    "Return <code>head</code>, which never changes.",
                ],
                "why": [
                    "Every original adjacent pair is visited once, and inserting does not disturb the pairs still ahead, so each gap gets exactly one gcd node.",
                    "Trial division always succeeds by d = 1, and the first hit going downwards is the greatest divisor.",
                    "Each gcd can take up to <code>min(a, b)</code> tries, so the time is <strong>O(n · min(a, b))</strong>, which depends on the values, not just the length.",
                    "Apart from the new nodes that form the output, only a couple of variables are used: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "node = 18, next 6: trial starts at 6, and 6 divides both on the first try. Insert 6: 18 → 6 → 6 → 10 → 3.",
                        "node jumps to the original 6, next 10: tries 6, 5, 4, 3, then 2 divides both. Insert 2.",
                        "node = 10, next 3: tries 3, 2, then 1. Insert 1.",
                        "node = 3 has no next, so the loop stops.",
                        "The list is <strong>[18, 6, 6, 2, 10, 1, 3]</strong>.",
                    ],
                    [
                        "node = 7, and <code>node.next</code> is None.",
                        "The loop condition fails before any gcd is computed.",
                        "No nodes are inserted, and head is returned unchanged.",
                        "The list is <strong>[7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>node = node.next.next</code> and not <code>node = node.next</code>?",
                     "After the splice, <code>node.next</code> is the new gcd node. Stepping onto it would compute a gcd between the gcd and the next value and insert nodes forever."],
                    ["Can <code>gcd</code> fall off the loop and return None?",
                     "No, the values are positive and d = 1 always divides both, so the loop returns by then at the latest."],
                    ["Why is this slow for large values?",
                     "Two large coprime values such as 99991 and 99989 need about 100,000 tries. Euclid's algorithm needs only a handful of steps for the same pair."],
                ],
            },
            "Walk and insert, Euclid's algorithm": {
                "idea": [
                    "The list walk is the same: splice a gcd node into every gap and skip over it.",
                    "The gcd uses <strong>Euclid's algorithm</strong>: gcd(a, b) = gcd(b, a mod b), and gcd(a, 0) = a.",
                    "Each step shrinks the numbers quickly, so the cost per pair is logarithmic in the values.",
                ],
                "steps": [
                    "Set <code>node = head</code> and loop while <code>node and node.next</code>.",
                    "In <code>gcd(a, b)</code>, repeat <code>a, b = b, a % b</code> while <code>b</code> is non-zero, then return <code>a</code>.",
                    "Insert <code>ListNode(gcd(node.val, node.next.val), node.next)</code> after <code>node</code>.",
                    "Advance with <code>node = node.next.next</code> to the next original node.",
                    "Return <code>head</code>.",
                ],
                "why": [
                    "Any number dividing a and b also divides a mod b, and the other way round, so each step keeps the set of common divisors and the gcd is unchanged.",
                    "When b becomes 0, gcd(a, 0) = a, which is the answer.",
                    "The remainder at least halves every two steps, so each gcd is O(log max) and the whole walk is <strong>O(n log max)</strong> time.",
                    "Only a few variables beyond the output nodes: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "gcd(18, 6): (18, 6) → (6, 0), so 6. Insert it after 18.",
                        "gcd(6, 10): (6, 10) → (10, 6) → (6, 4) → (4, 2) → (2, 0), so 2. Insert it.",
                        "gcd(10, 3): (10, 3) → (3, 1) → (1, 0), so 1. Insert it.",
                        "node lands on 3, which has no next, so the loop ends.",
                        "The list is <strong>[18, 6, 6, 2, 10, 1, 3]</strong>.",
                    ],
                    [
                        "head is the single node 7 with no next.",
                        "The while condition is false at once, so <code>gcd</code> is never called.",
                        "head is returned as it was.",
                        "The list is <strong>[7]</strong>.",
                    ],
                ],
                "faq": [
                    ["What if <code>a &lt; b</code> at the start, like gcd(6, 10)?",
                     "The first step does the swap for free: 6 % 10 = 6, so (6, 10) becomes (10, 6). No explicit ordering is needed."],
                    ["Why not use <code>math.gcd</code>?",
                     "In real code you should. Writing it out shows the algorithm an interviewer usually wants to hear about."],
                    ["Does inserting while walking break the loop?",
                     "No. The new node is placed between <code>node</code> and the old successor, and the jump of two lands exactly on that old successor."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ transpose matrix
    "transpose-matrix": {
        "examples": [
            {"call": "transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9]])", "expect": "[[1, 4, 7], [2, 5, 8], [3, 6, 9]]"},
            {"call": "transpose([[1, 2, 3], [4, 5, 6]])", "expect": "[[1, 4], [2, 5], [3, 6]]"},
        ],
        "approaches": {
            "New matrix with swapped indices": {
                "idea": [
                    "The transpose turns rows into columns: the value at row r, column c moves to row c, column r.",
                    "An m × n matrix becomes n × m, so the result generally needs a different shape and a fresh grid.",
                    "Copy every cell once into its swapped position.",
                ],
                "steps": [
                    "Read <code>m, n = len(matrix), len(matrix[0])</code>.",
                    "Create <code>out</code> with n rows of m zeros each.",
                    "Loop <code>r</code> over 0..m−1 and <code>c</code> over 0..n−1.",
                    "Set <code>out[c][r] = matrix[r][c]</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Each output cell <code>out[c][r]</code> is written exactly once, from the one input cell that defines it.",
                    "The shapes match: c ranges over n columns of the input, which are the n rows of <code>out</code>.",
                    "Every cell is touched once: <strong>O(m · n)</strong> time, and the new grid is <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "m = n = 3, out is a 3 × 3 grid of zeros.",
                        "Row 0: out[0][0] = 1, out[1][0] = 2, out[2][0] = 3. The first row becomes the first column.",
                        "Row 1: 4, 5, 6 go into column 1. Row 2: 7, 8, 9 go into column 2.",
                        "It returns <strong>[[1, 4, 7], [2, 5, 8], [3, 6, 9]]</strong>.",
                    ],
                    [
                        "m = 2, n = 3, so out has 3 rows of 2: [[0, 0], [0, 0], [0, 0]].",
                        "Row 0: out[0][0] = 1, out[1][0] = 2, out[2][0] = 3.",
                        "Row 1: out[0][1] = 4, out[1][1] = 5, out[2][1] = 6.",
                        "It returns <strong>[[1, 4], [2, 5], [3, 6]]</strong>, a 3 × 2 matrix.",
                    ],
                ],
                "faq": [
                    ["Why <code>[[0] * m for _ in range(n)]</code> and not <code>[[0] * m] * n</code>?",
                     "The second form repeats one inner list n times, so writing to <code>out[0][0]</code> would change every row. The comprehension builds n separate lists."],
                    ["Why is it n rows of m and not m rows of n?",
                     "The output has one row per input column. Getting this backwards only shows up on non-square inputs like the 2 × 3 example."],
                    ["Is there a one-liner?",
                     "<code>[list(col) for col in zip(*matrix)]</code> does the same thing: <code>zip(*matrix)</code> yields the columns."],
                ],
            },
            "In place, square matrices only": {
                "idea": [
                    "For a square matrix the shape does not change, so the transpose is a set of swaps: <code>matrix[r][c]</code> with <code>matrix[c][r]</code>.",
                    "Each swap fixes two cells at once, so only the cells <strong>above the diagonal</strong> (c &gt; r) need visiting. The diagonal stays put.",
                    "A non-square matrix changes shape, so it cannot be done in place; the code falls back to a copy.",
                ],
                "steps": [
                    "Set <code>n = len(matrix)</code>. If any row's length differs from n, return <code>[list(col) for col in zip(*matrix)]</code>.",
                    "Otherwise loop <code>r</code> over 0..n−1.",
                    "Loop <code>c</code> from <code>r + 1</code> to n−1, only the upper triangle.",
                    "Swap <code>matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]</code>.",
                    "Return the same <code>matrix</code> object.",
                ],
                "why": [
                    "Every off-diagonal pair {(r, c), (c, r)} is swapped exactly once, when visited from its upper-triangle cell, and diagonal cells are their own transpose.",
                    "Visiting the whole matrix instead would swap each pair twice and undo the work.",
                    "There are n(n − 1)/2 swaps: <strong>O(n²)</strong> time. No extra grid is used for squares, so <strong>O(1)</strong> space; the non-square fallback costs O(m · n).",
                ],
                "dry": [
                    [
                        "Every row has length 3, so the square path is taken.",
                        "r = 0: swap (0,1)↔(1,0): 2 and 4. Swap (0,2)↔(2,0): 3 and 7.",
                        "r = 1: swap (1,2)↔(2,1): 6 and 8. r = 2: no cells right of the diagonal.",
                        "It returns <strong>[[1, 4, 7], [2, 5, 8], [3, 6, 9]]</strong>, the same list object, now changed.",
                    ],
                    [
                        "n = len(matrix) = 2, but the rows have length 3.",
                        "The shape check fires, so no swaps happen.",
                        "<code>zip(*matrix)</code> yields columns (1, 4), (2, 5), (3, 6), each turned into a list.",
                        "It returns <strong>[[1, 4], [2, 5], [3, 6]]</strong>, a new matrix.",
                    ],
                ],
                "faq": [
                    ["Why does <code>c</code> start at <code>r + 1</code>?",
                     "Starting at 0 would visit each pair twice, swapping it and then swapping it back. Starting at r would include the diagonal, which is harmless but pointless."],
                    ["Why can't a 2 × 3 matrix be transposed in place?",
                     "The result is 3 × 2: it needs a different number of rows, each of a different length. Python lists could be resized, but that is a rebuild, not swapping."],
                    ["Where is this trick used?",
                     "It is the first half of rotating a square image by 90° in place, which is the next problem."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotate image
    "rotate-image": {
        "examples": [
            {"setup": "M = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\nrotate(M)", "call": "M", "expect": "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]"},
            {"setup": "M = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]\nrotate(M)", "call": "M",
             "expect": "[[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]]"},
        ],
        "approaches": {
            "Copy into a new matrix": {
                "idea": [
                    "Rotating clockwise by 90° sends row r to column <code>n − 1 − r</code>: the top row becomes the right column.",
                    "Within that row, column c becomes row c. So <code>matrix[r][c]</code> lands at <code>out[c][n - 1 - r]</code>.",
                    "Writing into a separate grid means no value is overwritten before it is read.",
                ],
                "steps": [
                    "Create <code>out</code>, an n × n grid of zeros.",
                    "Loop over every <code>r</code> and <code>c</code>.",
                    "Set <code>out[c][n - 1 - r] = matrix[r][c]</code>.",
                    "Copy back with <code>matrix[:] = out</code>, so the caller's list now holds the rotated rows.",
                ],
                "why": [
                    "The map (r, c) → (c, n − 1 − r) is a bijection on the grid, so every output cell gets exactly one value.",
                    "All reads come from the untouched original, so the order of the loops does not matter.",
                    "Each cell is copied once: <strong>O(n²)</strong> time. The second grid is <strong>O(n²)</strong> extra space, which the problem asks you to avoid.",
                ],
                "dry": [
                    [
                        "Row 0 (1, 2, 3) has r = 0, so it goes to column 2: out[0][2] = 1, out[1][2] = 2, out[2][2] = 3.",
                        "Row 1 (4, 5, 6) goes to column 1. Row 2 (7, 8, 9) goes to column 0.",
                        "out = [[7, 4, 1], [8, 5, 2], [9, 6, 3]].",
                        "<code>matrix[:] = out</code> puts these rows into M: <strong>[[7, 4, 1], [8, 5, 2], [9, 6, 3]]</strong>.",
                    ],
                    [
                        "n = 4. Row 0 (1..4) goes to column 3, row 1 (5..8) to column 2.",
                        "Row 2 (9..12) goes to column 1, row 3 (13..16) to column 0.",
                        "Reading out row by row: [13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4].",
                        "M becomes <strong>[[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>matrix[:] = out</code> and not <code>matrix = out</code>?",
                     "<code>matrix = out</code> only rebinds the local name; the caller's list would be unchanged. Slice assignment replaces the contents of the caller's list."],
                    ["How do I remember the index formula?",
                     "Check one corner: the top-left (0, 0) must end at the top-right (0, n − 1). Plugging in gives out[0][n − 1], which matches."],
                    ["Why is this not accepted as \"in place\"?",
                     "It allocates a second n × n grid. The task asks for O(1) extra space, which the next two approaches achieve."],
                ],
            },
            "Transpose, then reverse each row": {
                "idea": [
                    "A clockwise rotation equals two simple moves: <strong>transpose</strong> (flip over the main diagonal), then <strong>mirror left-right</strong>.",
                    "Both moves are easy to do in place: the transpose with swaps above the diagonal, the mirror with <code>row.reverse()</code>.",
                    "No cell is lost because each move is made of swaps.",
                ],
                "steps": [
                    "For each <code>r</code> and each <code>c &gt; r</code>, swap <code>matrix[r][c]</code> and <code>matrix[c][r]</code>.",
                    "After this loop, row r holds what was column r.",
                    "Call <code>row.reverse()</code> on every row.",
                    "The function returns nothing; <code>matrix</code> itself is now rotated.",
                ],
                "why": [
                    "Transposing sends (r, c) to (c, r); reversing a row sends (c, r) to (c, n − 1 − r). Together that is (r, c) → (c, n − 1 − r), the rotation formula.",
                    "Both passes only swap pairs of cells, so no value is overwritten before it is moved.",
                    "Each pass touches every cell a constant number of times: <strong>O(n²)</strong> time, and <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "Transpose: swap 2↔4, 3↔7, 6↔8. M = [[1, 4, 7], [2, 5, 8], [3, 6, 9]].",
                        "Reverse row 0: [7, 4, 1]. Row 1: [8, 5, 2]. Row 2: [9, 6, 3].",
                        "No other work is done.",
                        "M is <strong>[[7, 4, 1], [8, 5, 2], [9, 6, 3]]</strong>.",
                    ],
                    [
                        "Transpose makes 6 swaps (the upper triangle of a 4 × 4).",
                        "M = [[1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15], [4, 8, 12, 16]].",
                        "Reversing each row gives [13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4].",
                        "M is <strong>[[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]]</strong>.",
                    ],
                ],
                "faq": [
                    ["How do I rotate counter-clockwise instead?",
                     "Transpose, then reverse each <em>column</em> (equivalently, reverse the order of the rows). Or reverse each row first and then transpose."],
                    ["Does the order of the two steps matter?",
                     "Yes. Reversing rows first and then transposing gives the counter-clockwise rotation."],
                    ["Is this slower than the layer method?",
                     "It touches each cell about twice instead of once, but both are O(n²). This version is much easier to get right under pressure."],
                ],
            },
            "Rotate four cells at a time, layer by layer": {
                "idea": [
                    "A rotation moves cells in cycles of four: top → right → bottom → left → top. Saving one value in <code>top</code> lets the other three shift without loss.",
                    "Work from the outer ring inwards. Each ring (\"layer\") has sides from <code>first</code> to <code>last</code>.",
                    "Along a side, <code>off = i - first</code> says how far from the corner the current cell is, which locates its three partners.",
                ],
                "steps": [
                    "Loop <code>layer</code> over 0..n//2 − 1, with <code>first = layer</code> and <code>last = n - 1 - layer</code>.",
                    "Loop <code>i</code> from <code>first</code> to <code>last - 1</code>, and set <code>off = i - first</code>.",
                    "Save <code>top = matrix[first][i]</code>.",
                    "Move left → top, bottom → left, right → bottom: <code>matrix[first][i] = matrix[last - off][first]</code>, <code>matrix[last - off][first] = matrix[last][last - off]</code>, <code>matrix[last][last - off] = matrix[i][last]</code>.",
                    "Finish the cycle with <code>matrix[i][last] = top</code>.",
                ],
                "why": [
                    "The four cells in one cycle are exactly the images of each other under the rotation, so moving them in a ring places all four correctly.",
                    "The inner loop stops at <code>last - 1</code> because the last cell of the top side is the first cell of the right side, already handled.",
                    "Every cell is moved once: <strong>O(n²)</strong> time. Only <code>top</code> is stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Only one layer: first = 0, last = 2. The centre 5 never moves.",
                        "i = 0: top = 1. Corners cycle: [0][0] = 7, [2][0] = 9, [2][2] = 3, [0][2] = 1. M = [[7, 2, 1], [4, 5, 6], [9, 8, 3]].",
                        "i = 1, off = 1: top = 2. [0][1] = 4, [1][0] = 8, [2][1] = 6, [1][2] = 2.",
                        "M is <strong>[[7, 4, 1], [8, 5, 2], [9, 6, 3]]</strong>.",
                    ],
                    [
                        "Layer 0 (first = 0, last = 3) has three cycles: i = 0 moves the corners 1, 4, 16, 13.",
                        "i = 1 moves 2, 8, 15, 9, and i = 2 moves 3, 12, 14, 5. The outer ring is now 13, 9, 5, 1 along the top.",
                        "Layer 1 (first = 1, last = 2) has one cycle: 6, 7, 11, 10.",
                        "M is <strong>[[13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3], [16, 12, 8, 4]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the outer loop run <code>n // 2</code> times?",
                     "Each layer removes one ring from all four sides. For odd n the single centre cell is left, and it does not move under rotation."],
                    ["Why <code>last - off</code> rather than <code>last - i</code>?",
                     "Partners are measured from the layer's corner, not from the matrix edge. On inner layers <code>first</code> is not 0, so using <code>i</code> would read the wrong cells."],
                    ["Why assign in the order left → top, bottom → left, right → bottom?",
                     "Each assignment overwrites a cell that has just been copied out. Going the other way round would overwrite a value before it was saved."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ spiral matrix
    "spiral-matrix": {
        "examples": [
            {"call": "spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])", "expect": "[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]"},
            {"call": "spiral_order([[1], [2], [3]])", "expect": "[1, 2, 3]"},
        ],
        "approaches": {
            "Simulate with a visited grid": {
                "idea": [
                    "Walk the matrix like a robot: go right, and whenever the next step would leave the grid or hit a cell already visited, <strong>turn clockwise</strong>.",
                    "The four directions right, down, left, up are stored in <code>dr</code> and <code>dc</code>, and <code>d</code> picks one.",
                    "A <code>seen</code> grid tells the robot where it has been.",
                ],
                "steps": [
                    "Create <code>seen</code> (m × n, all False) and start at <code>r = c = d = 0</code>.",
                    "Repeat m · n times: append <code>matrix[r][c]</code> to <code>out</code> and mark <code>seen[r][c]</code>.",
                    "Compute the next cell <code>nr, nc = r + dr[d], c + dc[d]</code>.",
                    "If it is out of bounds or already seen, turn: <code>d = (d + 1) % 4</code>, and recompute <code>nr, nc</code>.",
                    "Move to <code>(nr, nc)</code>. Return <code>out</code> after the last cell.",
                ],
                "why": [
                    "The spiral turns exactly when it reaches the grid edge or the already-walked ring, which is what the test checks.",
                    "One turn is always enough: after turning, the new direction leads into the next unvisited ring, until the last cell.",
                    "The loop runs exactly m · n times, so it is <strong>O(m · n)</strong> time; the <code>seen</code> grid is <strong>O(m · n)</strong> extra space.",
                ],
                "dry": [
                    [
                        "Right along row 0: 1, 2, 3, 4. The next step (0, 4) is out of bounds, so turn down.",
                        "Down: 8, 12. (3, 3) is out, so turn left: 11, 10, 9. (2, −1) is out, so turn up.",
                        "Up: 5. The next cell (0, 0) is seen, so turn right: 6, 7.",
                        "After 12 cells the loop ends: <strong>[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]</strong>.",
                    ],
                    [
                        "m = 3, n = 1. Take 1 at (0, 0); the step right to (0, 1) is out, so turn down.",
                        "Take 2 at (1, 0), then 3 at (2, 0).",
                        "At (2, 0) the step down is out, so it turns left to (2, −1), but the loop has already run 3 times and stops.",
                        "It returns <strong>[1, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Doesn't the last move go to an invalid cell?",
                     "It can compute one, as in the single-column example, but the loop ends before reading it, so no index error occurs."],
                    ["Why is one turn enough?",
                     "Until the final cell, there is always an unvisited neighbour in the next clockwise direction, because the spiral keeps the unvisited cells as one rectangle."],
                    ["Can I avoid the <code>seen</code> grid?",
                     "Yes, by overwriting visited cells with a marker if you may modify the input, or by tracking the four boundaries, which is the next approach."],
                ],
            },
            "Shrinking boundaries": {
                "idea": [
                    "Keep the unvisited part as a rectangle with edges <code>top</code>, <code>bottom</code>, <code>left</code>, <code>right</code>.",
                    "Peel one ring: the top row left to right, the right column downwards, the bottom row right to left, the left column upwards. After each side, move that edge inwards.",
                    "When the rectangle becomes one row or one column, the last two sides must be skipped or values repeat; the two <code>if</code> checks do that.",
                ],
                "steps": [
                    "Set <code>top, bottom, left, right</code> to the outer edges.",
                    "While <code>top &lt;= bottom and left &lt;= right</code>: add <code>matrix[top][left:right + 1]</code>, then <code>top += 1</code>.",
                    "Add the right column for rows <code>top..bottom</code>, then <code>right -= 1</code>.",
                    "If <code>top &lt;= bottom</code>, add the bottom row reversed, then <code>bottom -= 1</code>.",
                    "If <code>left &lt;= right</code>, add the left column from <code>bottom</code> up to <code>top</code>, then <code>left += 1</code>.",
                ],
                "why": [
                    "Each side is read only within the current rectangle and that edge then moves in, so every cell is output exactly once.",
                    "The checks before the bottom row and left column stop a single remaining row or column from being read twice in opposite directions.",
                    "Every cell is appended once: <strong>O(m · n)</strong> time. Only four integers are kept: <strong>O(1)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "Ring 1: top row 1, 2, 3, 4 (top = 1); right column 8, 12 (right = 2).",
                        "Bottom row reversed: 11, 10, 9 (bottom = 1); left column upwards: 5 (left = 1).",
                        "Ring 2: top = bottom = 1, left = 1, right = 2. Top row gives 6, 7, then top = 2.",
                        "The right column range is empty, right = 1; <code>top &lt;= bottom</code> fails; the left column range is empty. Result <strong>[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]</strong>.",
                    ],
                    [
                        "top = 0, bottom = 2, left = right = 0.",
                        "Top row gives [1], top = 1. Right column, rows 1..2, gives 2, 3, then right = −1.",
                        "<code>top &lt;= bottom</code> holds, but the slice <code>[0:0]</code> is empty; bottom = 1. <code>left &lt;= right</code> is 0 ≤ −1, false, so the left column is skipped.",
                        "The while condition now fails: <strong>[1, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong without the two <code>if</code> checks?",
                     "On a single column like [[1], [2], [3]], the left-column step would read 3 and 2 again going upwards, duplicating values."],
                    ["Why don't the first two sides need a check?",
                     "The while condition guarantees the top row is non-empty, and the right column's range is simply empty when top has passed bottom."],
                    ["Is this better than the visited grid?",
                     "It has the same time but no extra grid, and it never computes an out-of-range cell. It is the usual interview answer."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ set matrix zeroes
    "set-matrix-zeroes": {
        "examples": [
            {"setup": "M = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]\nset_zeroes(M)", "call": "M", "expect": "[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]"},
            {"setup": "M = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]\nset_zeroes(M)", "call": "M", "expect": "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]"},
        ],
        "approaches": {
            "Copy the matrix, read from the copy": {
                "idea": [
                    "The trap: if you zero a row as soon as you see a 0, the new zeros look like original zeros and wipe out everything.",
                    "Keep an untouched copy <code>orig</code> and decide only from it, while writing into <code>matrix</code>.",
                    "For every original zero, clear its whole row and its whole column.",
                ],
                "steps": [
                    "Make <code>orig = [row[:] for row in matrix]</code>, a copy of every row.",
                    "Loop over every <code>(r, c)</code>.",
                    "If <code>orig[r][c] == 0</code>, set <code>matrix[r][k] = 0</code> for every column <code>k</code>.",
                    "Also set <code>matrix[k][c] = 0</code> for every row <code>k</code>.",
                    "The function changes <code>matrix</code> in place and returns nothing.",
                ],
                "why": [
                    "Decisions read only <code>orig</code>, which never changes, so zeros created along the way cannot trigger more clearing.",
                    "A cell ends up 0 exactly when its row or column held an original zero, which is the requirement.",
                    "For each zero, m + n cells are cleared, and up to m · n cells can be zero: <strong>O(m · n · (m + n))</strong> time. The copy is <strong>O(m · n)</strong> space.",
                ],
                "dry": [
                    [
                        "orig has zeros at (0, 0) and (0, 3).",
                        "(0, 0): clear row 0 and column 0. matrix = [[0, 0, 0, 0], [0, 4, 5, 2], [0, 3, 1, 5]].",
                        "(0, 1), (0, 2) in matrix are now 0, but orig still has 1 and 2 there, so nothing more happens.",
                        "(0, 3): clear row 0 again and column 3. No other cell of orig is 0.",
                        "M is <strong>[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]</strong>.",
                    ],
                    [
                        "orig has one zero, at (1, 1).",
                        "Cells before it are 1 in orig, so nothing happens.",
                        "(1, 1): clear row 1 and column 1. matrix = [[1, 0, 1], [0, 0, 0], [1, 0, 1]].",
                        "The new zeros at (0, 1), (1, 0), (1, 2), (2, 1) are 1 in orig and are ignored. M is <strong>[[1, 0, 1], [0, 0, 0], [1, 0, 1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>matrix.copy()</code> not enough?",
                     "It copies only the outer list; the rows are shared, so writes would show up in the \"copy\" too. Each row must be copied with <code>row[:]</code>."],
                    ["What does the naive in-place version do on example 2?",
                     "Zeroing row 1 creates zeros at (1, 0) and (1, 2), which then clear columns 0 and 2, and the whole matrix becomes 0."],
                    ["Why is the time bound so loose?",
                     "A row or column can be cleared many times, once per zero in it. The marker approaches clear each cell at most once."],
                ],
            },
            "Row and column marker sets": {
                "idea": [
                    "What matters is only <strong>which rows</strong> and <strong>which columns</strong> contain a zero, not where exactly.",
                    "Record them in two sets in a first pass, then clear in a second pass.",
                    "Separating reading from writing avoids the cascade without copying the matrix.",
                ],
                "steps": [
                    "Create empty sets <code>rows</code> and <code>cols</code>.",
                    "First pass: for every cell with <code>v == 0</code>, add <code>r</code> to <code>rows</code> and <code>c</code> to <code>cols</code>.",
                    "Second pass: for every cell, if <code>r in rows or c in cols</code>, set it to 0.",
                    "The matrix is changed in place.",
                ],
                "why": [
                    "The first pass finishes before any write, so the sets describe only the original zeros.",
                    "A cell is cleared exactly when its row or column is marked, which is the rule.",
                    "Two passes with O(1) set lookups: <strong>O(m · n)</strong> time. The sets hold at most m + n numbers: <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "First pass: zeros at (0, 0) and (0, 3), so rows = {0}, cols = {0, 3}.",
                        "Row 0 is marked, so all of it becomes 0.",
                        "Row 1: columns 0 and 3 are marked, so [3, 4, 5, 2] becomes [0, 4, 5, 0].",
                        "Row 2: [1, 3, 1, 5] becomes [0, 3, 1, 0].",
                        "M is <strong>[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]</strong>.",
                    ],
                    [
                        "First pass: one zero at (1, 1), so rows = {1}, cols = {1}.",
                        "Row 0: only column 1 is marked, giving [1, 0, 1].",
                        "Row 1 is marked, giving [0, 0, 0]. Row 2 gives [1, 0, 1].",
                        "M is <strong>[[1, 0, 1], [0, 0, 0], [1, 0, 1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sets instead of two boolean lists?",
                     "Either works. Boolean lists of length m and n are slightly faster; sets read naturally when there are few zeros."],
                    ["Is this the answer interviewers expect?",
                     "It is the clean O(m + n) answer. The follow-up is usually \"now do it in O(1) space\", which is the next approach."],
                    ["Can I stop the first pass early?",
                     "No. Any cell could be a zero, so every cell has to be read once."],
                ],
            },
            "Use the first row and column as the markers": {
                "idea": [
                    "Store the marker sets inside the matrix itself: <code>matrix[r][0] = 0</code> means \"row r has a zero\", <code>matrix[0][c] = 0</code> means \"column c has a zero\".",
                    "Those cells would be zeroed anyway if their row or column is marked, so using them as flags loses nothing.",
                    "One clash remains: <code>matrix[0][0]</code> would serve both row 0 and column 0. Column 0 gets its own flag, <code>first_col_zero</code>.",
                ],
                "steps": [
                    "Set <code>first_col_zero</code> to whether column 0 has any zero.",
                    "Mark: for every cell with <code>c ≥ 1</code> that is 0, set <code>matrix[r][0] = matrix[0][c] = 0</code>.",
                    "Clear the inner part: for <code>r ≥ 1, c ≥ 1</code>, zero the cell if <code>matrix[r][0] == 0 or matrix[0][c] == 0</code>.",
                    "If <code>matrix[0][0] == 0</code>, row 0 had a zero: clear all of row 0.",
                    "If <code>first_col_zero</code>, clear all of column 0.",
                ],
                "why": [
                    "After marking, <code>matrix[r][0]</code> is 0 exactly when row r had a zero (for r ≥ 1, counting column 0 itself), and <code>matrix[0][c]</code> exactly when column c had one (c ≥ 1).",
                    "The inner cells are cleared before row 0 and column 0, so the flags are still intact while they are read.",
                    "<code>matrix[0][0]</code> is set to 0 by a zero anywhere in row 0, so it acts as row 0's flag; column 0 uses the separate boolean.",
                    "A few passes over the grid: <strong>O(m · n)</strong> time, and one boolean: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Column 0 holds 0, 3, 1, so first_col_zero = True.",
                        "Marking: (0, 3) is 0, so matrix[0][0] = matrix[0][3] = 0 (already 0). No other zeros in c ≥ 1.",
                        "Inner pass: column 3 is flagged, so (1, 3) and (2, 3) become 0. Rows 1 and 2 are not flagged.",
                        "matrix[0][0] == 0, so row 0 is cleared. first_col_zero is True, so column 0 is cleared.",
                        "M is <strong>[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]</strong>.",
                    ],
                    [
                        "Column 0 is 1, 1, 1, so first_col_zero = False.",
                        "Marking: (1, 1) is 0, so matrix[1][0] = 0 and matrix[0][1] = 0. M = [[1, 0, 1], [0, 0, 1], [1, 1, 1]].",
                        "Inner pass: row 1 is flagged, so (1, 2) = 0; column 1 is flagged, so (2, 1) = 0.",
                        "matrix[0][0] is 1, so row 0 is left; first_col_zero is False, so column 0 is left (its 0 at (1, 0) is a flag that was due anyway).",
                        "M is <strong>[[1, 0, 1], [0, 0, 0], [1, 0, 1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does column 0 need its own flag but row 0 doesn't?",
                     "Only one of them can use <code>matrix[0][0]</code>. Here it belongs to row 0, so column 0's information is kept in <code>first_col_zero</code> before any marking overwrites it."],
                    ["Why must row 0 and column 0 be cleared last?",
                     "They hold the flags. Clearing them first would set every flag to 0 and the inner pass would wipe the whole matrix."],
                    ["Why does the marking loop start at <code>c = 1</code>?",
                     "Zeros in column 0 are already recorded by <code>first_col_zero</code>. Starting at 0 would also write <code>matrix[0][0] = 0</code> for them, wrongly flagging row 0."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ happy number
    "happy-number": {
        "examples": [
            {"call": "is_happy(19)", "expect": "True"},
            {"call": "is_happy(2)", "expect": "False"},
        ],
        "approaches": {
            "Hash set of values seen": {
                "idea": [
                    "Repeatedly replacing n by the sum of the squares of its digits either reaches 1 or <strong>falls into a loop</strong> that never contains 1.",
                    "It cannot grow forever: any number with 4 or more digits maps to a smaller number, so the values stay bounded.",
                    "Remember every value seen; meeting one again proves a loop.",
                ],
                "steps": [
                    "Define <code>step(x)</code> as the sum of <code>int(d) ** 2</code> over the digits of <code>str(x)</code>.",
                    "Start with an empty set <code>seen</code>.",
                    "While <code>n != 1</code> and <code>n</code> is not in <code>seen</code>: add <code>n</code> to <code>seen</code>, then <code>n = step(n)</code>.",
                    "The loop stops either at 1 or at a repeated value.",
                    "Return <code>n == 1</code>.",
                ],
                "why": [
                    "The sequence is deterministic, so once a value repeats, everything after it repeats too. If 1 was not reached before the repeat, it never will be.",
                    "1 maps to itself, so reaching 1 is the only way to be happy.",
                    "A d-digit number maps to at most 81·d, so after O(log n) work the values fall below a few hundred and only a bounded number more steps are possible: <strong>O(log n)</strong> time.",
                    "The set holds those values: <strong>O(log n)</strong> space by the same argument.",
                ],
                "dry": [
                    [
                        "n = 19: not seen. Add it; 1² + 9² = 82.",
                        "n = 82: add it; 64 + 4 = 68. n = 68: add it; 36 + 64 = 100.",
                        "n = 100: add it; 1 + 0 + 0 = 1.",
                        "n == 1 stops the loop, so it returns <strong>True</strong>.",
                    ],
                    [
                        "2 → 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20, each added to seen.",
                        "step(20) = 4.",
                        "4 is already in seen, so the loop stops with n = 4.",
                        "4 ≠ 1, so it returns <strong>False</strong>. The loop is 4 → 16 → … → 20 → 4.",
                    ],
                ],
                "faq": [
                    ["How do we know the sequence can't grow forever?",
                     "A number with d digits is at least 10<sup>d−1</sup>, but its digit-square sum is at most 81·d. For d ≥ 4 the sum is smaller than the number, so values shrink until they are below 1000 and stay there."],
                    ["Why check <code>n != 1</code> separately?",
                     "1 maps to 1, so it would also be caught as a repeat, but stopping at 1 directly saves a step and makes the return value obvious."],
                    ["Is there only one unhappy loop?",
                     "Yes, every unhappy number ends in the cycle 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4, so checking for 4 also works, but that is a fact to remember rather than derive."],
                ],
            },
            "Floyd's cycle detection": {
                "idea": [
                    "The sequence n, step(n), step(step(n)), … is like a linked list whose next pointer is <code>step</code>, and it must end in a cycle.",
                    "Run a <strong>slow</strong> pointer one step at a time and a <strong>fast</strong> one two steps at a time. Inside a cycle the fast one catches up with the slow one.",
                    "If the cycle is the one-element loop at 1, fast reaches 1 first. That gives the answer with no set.",
                ],
                "steps": [
                    "Write <code>step(x)</code> with <code>divmod(x, 10)</code> to peel digits, adding <code>d * d</code>.",
                    "Start with <code>slow = n</code> and <code>fast = step(n)</code>.",
                    "While <code>fast != 1</code> and <code>slow != fast</code>: <code>slow = step(slow)</code>, <code>fast = step(step(fast))</code>.",
                    "When the loop stops, either fast reached 1 or the pointers met inside a cycle.",
                    "Return <code>fast == 1</code>.",
                ],
                "why": [
                    "Once both pointers are in the cycle, the gap between them shrinks by one each round, so they meet within one lap.",
                    "If the sequence reaches 1, fast gets there first (it is ahead) and the loop stops at once.",
                    "The number of rounds is bounded by the tail length plus the cycle length, as in the set version: <strong>O(log n)</strong> time.",
                    "Only two numbers are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "slow = 19, fast = step(19) = 82.",
                        "Round 1: slow = 82, fast = step(step(82)) = step(68) = 100.",
                        "Round 2: slow = 68, fast = step(step(100)) = step(1) = 1.",
                        "fast == 1 stops the loop: <strong>True</strong>.",
                    ],
                    [
                        "slow = 2, fast = 4.",
                        "Rounds: (4, 37), (16, 89), (37, 42), (58, 4), (89, 37), (145, 89).",
                        "Next round: slow = 42, fast = step(step(89)) = step(145) = 42. They meet.",
                        "fast is 42, not 1, so it returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start fast at <code>step(n)</code> instead of at <code>n</code>?",
                     "With both at n the loop condition <code>slow != fast</code> would fail before the first move. Starting one step ahead lets the loop run."],
                    ["Can fast skip over 1?",
                     "No. Once it reaches 1 it stays at 1 because step(1) = 1, and the loop checks <code>fast != 1</code> every round."],
                    ["When is this worth it over the set?",
                     "Only when memory is tight. Here the set is tiny anyway; the point is recognising the linked-list cycle pattern."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ plus one
    "plus-one": {
        "examples": [
            {"call": "plus_one([1, 2, 9, 9])", "expect": "[1, 3, 0, 0]"},
            {"call": "plus_one([9, 9])", "expect": "[1, 0, 0]"},
        ],
        "approaches": {
            "Convert to an integer and back": {
                "idea": [
                    "The digits are just a number written out. Glue them into a string, convert to an int, add 1, and split it back into digits.",
                    "Python integers have no size limit, so even a 100-digit number is fine.",
                    "Carrying is done by the built-in arithmetic, so there is nothing to get wrong.",
                ],
                "steps": [
                    "Turn each digit into a character with <code>map(str, digits)</code> and join them.",
                    "Convert the string with <code>int(...)</code> and add 1.",
                    "Turn the result back into a string with <code>str(...)</code>.",
                    "Return <code>[int(d) for d in ...]</code>, one int per character.",
                ],
                "why": [
                    "The string round trip is exact, so the result equals the number plus one, digit for digit.",
                    "Each conversion handles n digits; arbitrary-precision addition of 1 is O(n). So the time is <strong>O(n)</strong> for this addition, though parsing long decimal strings can cost more in some Python versions.",
                    "The string, integer and result list are each <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "\"\".join gives \"1299\".",
                        "int(\"1299\") + 1 = 1300.",
                        "str(1300) = \"1300\".",
                        "It returns <strong>[1, 3, 0, 0]</strong>.",
                    ],
                    [
                        "\"\".join gives \"99\".",
                        "int(\"99\") + 1 = 100, one digit longer.",
                        "str(100) = \"100\".",
                        "It returns <strong>[1, 0, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why would an interviewer not accept this?",
                     "It sidesteps the point of the question, which is carrying by hand. In languages with fixed-size integers it overflows for long inputs."],
                    ["Does it handle leading zeros?",
                     "The problem guarantees none except the number 0 itself, [0], which becomes \"0\" → 1 → [1] correctly."],
                    ["Is it really O(n)?",
                     "Joining and splitting are linear, but converting a very long decimal string to an int is super-linear in CPython. For realistic lengths it does not matter."],
                ],
            },
            "Carry from the end": {
                "idea": [
                    "Adding 1 only affects the trailing 9s and the digit just before them.",
                    "Walk from the last digit: a 9 becomes 0 and the carry moves left; the first digit below 9 is increased and the work is done.",
                    "If every digit was 9, the answer is a 1 followed by zeros, one digit longer.",
                ],
                "steps": [
                    "Copy the input with <code>digits = digits[:]</code> so the caller's list is not changed.",
                    "Loop <code>i</code> from the last index down to 0.",
                    "If <code>digits[i] &lt; 9</code>, add 1 to it and return <code>digits</code> immediately.",
                    "Otherwise it is 9: set it to 0 and continue left (the carry).",
                    "If the loop ends, every digit was 9: return <code>[1] + digits</code>.",
                ],
                "why": [
                    "This is schoolbook addition of 1, where the carry can only continue through 9s.",
                    "Stopping at the first digit below 9 is safe: adding 1 there produces no further carry.",
                    "In the worst case (all 9s) every digit is visited: <strong>O(n)</strong> time. Apart from the copy, extra space is <strong>O(1)</strong>, and the all-9s case builds a new list of n + 1.",
                ],
                "dry": [
                    [
                        "i = 3: digit 9, set to 0. digits = [1, 2, 9, 0].",
                        "i = 2: digit 9, set to 0. digits = [1, 2, 0, 0].",
                        "i = 1: digit 2 &lt; 9, becomes 3.",
                        "It returns at once: <strong>[1, 3, 0, 0]</strong>.",
                    ],
                    [
                        "i = 1: 9 becomes 0. digits = [9, 0].",
                        "i = 0: 9 becomes 0. digits = [0, 0].",
                        "The loop ends without returning, so every digit was 9.",
                        "It returns [1] + [0, 0] = <strong>[1, 0, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why copy the list first?",
                     "So that calling the function does not change the caller's data. LeetCode does not care, but it keeps tests that reuse the input honest."],
                    ["Why is the final list just a 1 followed by the zeros?",
                     "The loop only falls through when every digit was 9 and has been set to 0, so the number was 99…9 and the answer is 100…0."],
                    ["Why can I return as soon as a digit is below 9?",
                     "That digit absorbs the carry without overflowing, so no digit to its left changes."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ roman to integer
    "roman-to-integer": {
        "examples": [
            {"call": 'roman_to_int("MCMXCIV")', "expect": "1994"},
            {"call": 'roman_to_int("LVIII")', "expect": "58"},
        ],
        "approaches": {
            "Match the two-letter pairs first": {
                "idea": [
                    "Roman numerals add up their symbols, except for six special two-letter pairs where a smaller symbol comes before a larger one: IV, IX, XL, XC, CD, CM.",
                    "Read left to right. If the next two letters form one of those pairs, take its value and jump two; otherwise take the single letter.",
                    "Two lookup tables, <code>pairs</code> and <code>single</code>, hold all the values.",
                ],
                "steps": [
                    "Set <code>i = total = 0</code>.",
                    "While <code>i &lt; len(s)</code>, look at <code>s[i:i + 2]</code>.",
                    "If it is in <code>pairs</code>, add its value and advance <code>i</code> by 2.",
                    "Otherwise add <code>single[s[i]]</code> and advance <code>i</code> by 1.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "In a valid numeral, the subtractive pairs are exactly those six, and they never overlap, so greedily matching a pair first reads each symbol once with the right meaning.",
                    "At the last character the slice <code>s[i:i + 2]</code> has one letter, which is never a pair, so there is no index error.",
                    "Each step consumes one or two characters: <strong>O(n)</strong> time; the tables are fixed size: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i = 0: \"MC\" is not a pair. Add M = 1000.",
                        "i = 1: \"CM\" is a pair, add 900 (1900), i = 3.",
                        "i = 3: \"XC\" is a pair, add 90 (1990), i = 5.",
                        "i = 5: \"IV\" is a pair, add 4 (1994), i = 7, which ends the loop.",
                        "It returns <strong>1994</strong>.",
                    ],
                    [
                        "i = 0: \"LV\" is not a pair. Add 50.",
                        "i = 1: \"VI\" is not a pair. Add 5 (55).",
                        "i = 2, 3: \"II\" is not a pair either time. Add 1 each (57).",
                        "i = 4: the slice is just \"I\". Add 1.",
                        "It returns <strong>58</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check the pair before the single letter?",
                     "\"IV\" read letter by letter would be 1 + 5 = 6. Checking the pair first gives 4."],
                    ["What about invalid input like \"IIV\"?",
                     "The problem guarantees a valid numeral, so the code does not validate. On \"IIV\" it would return 1 + 4 = 5."],
                    ["Why is space O(1)?",
                     "The tables have 6 and 7 entries regardless of the input, and only two integers are updated."],
                ],
            },
            "Subtract when smaller than the next symbol": {
                "idea": [
                    "The six special pairs share one rule: a symbol is <strong>subtracted</strong> when the symbol after it is larger.",
                    "So a single table of seven values is enough: look one character ahead to decide the sign.",
                    "Every symbol is then either added or subtracted exactly once.",
                ],
                "steps": [
                    "Set <code>total = 0</code>.",
                    "For each index <code>i</code> and letter <code>ch</code>, let <code>v = val[ch]</code>.",
                    "If there is a next letter and <code>v &lt; val[s[i + 1]]</code>, do <code>total -= v</code>.",
                    "Otherwise do <code>total += v</code>.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "A pair like CM is worth 1000 − 100. Subtracting C and then adding M gives exactly that.",
                    "In a valid numeral, symbols otherwise appear in non-increasing order, so every other symbol is added.",
                    "One pass with a constant-time lookup per letter: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "M (next C, smaller): +1000. C (next M, larger): −100 → 900.",
                        "M (next X): +1000 → 1900. X (next C, larger): −10 → 1890.",
                        "C (next I): +100 → 1990. I (next V, larger): −1 → 1989.",
                        "V is last: +5 → 1994.",
                        "It returns <strong>1994</strong>.",
                    ],
                    [
                        "L (next V, smaller): +50.",
                        "V (next I, smaller): +5 → 55.",
                        "I (next I, equal, not smaller): +1 → 56. Again: +1 → 57.",
                        "The last I has no next letter: +1 → 58.",
                        "It returns <strong>58</strong>.",
                    ],
                ],
                "faq": [
                    ["Why strictly smaller (<code>&lt;</code>) and not <code>&lt;=</code>?",
                     "Equal neighbours like the two Is in \"II\" are both added. With <code>&lt;=</code>, \"II\" would come out as 0."],
                    ["Why the <code>i + 1 &lt; len(s)</code> check?",
                     "The last symbol has no neighbour, and <code>s[i + 1]</code> would raise an IndexError. The last symbol is always added."],
                    ["Could I scan right to left instead?",
                     "Yes: keep the previous (right-hand) value and subtract the current one if it is smaller. It is the same rule seen from the other side."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pow(x, n)
    "pow-x-n": {
        "examples": [
            {"call": "my_pow(2.0, 10)", "expect": "1024.0"},
            {"call": "my_pow(2.0, -2)", "expect": "0.25"},
        ],
        "approaches": {
            "Multiply n times": {
                "idea": [
                    "x<sup>n</sup> is x multiplied by itself n times, so do exactly that.",
                    "A negative exponent means 1 / x<sup>|n|</sup>, which is the same as raising <code>1 / x</code> to the power <code>-n</code>.",
                    "Start the product at 1.0 so that n = 0 gives 1.",
                ],
                "steps": [
                    "If <code>n &lt; 0</code>, replace <code>x, n</code> with <code>1 / x, -n</code>.",
                    "Set <code>result = 1.0</code>.",
                    "Repeat n times: <code>result *= x</code>.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "After the sign fix the exponent is non-negative, and the loop literally builds x · x · … · x with n factors.",
                    "(1/x)<sup>k</sup> = 1 / x<sup>k</sup>, so flipping x handles negative n.",
                    "There are |n| multiplications: <strong>O(n)</strong> time, which is far too slow for n near 2<sup>31</sup>. Only one number is stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 10 is not negative. result = 1.0.",
                        "After 1, 2, 3 multiplications: 2.0, 4.0, 8.0.",
                        "… after 9: 512.0, after 10: 1024.0.",
                        "It returns <strong>1024.0</strong>.",
                    ],
                    [
                        "n = −2 &lt; 0, so x = 0.5 and n = 2.",
                        "result = 1.0 × 0.5 = 0.5.",
                        "result = 0.5 × 0.5 = 0.25.",
                        "It returns <strong>0.25</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>1 / x</code> rather than computing x<sup>|n|</sup> and dividing at the end?",
                     "Both are correct. Dividing at the end can overflow to infinity first when x<sup>|n|</sup> is huge, whereas flipping first keeps numbers small."],
                    ["What about x = 0 with negative n?",
                     "That is 1/0, undefined; the problem rules it out. This code would raise ZeroDivisionError."],
                    ["Why mention this at all?",
                     "It is the definition, and it sets up the key observation for the fast versions: most of these multiplications repeat work."],
                ],
            },
            "Recursive squaring": {
                "idea": [
                    "x<sup>n</sup> = (x<sup>n/2</sup>)² when n is even, and x · (x<sup>⌊n/2⌋</sup>)² when n is odd.",
                    "So one recursive call on <code>n // 2</code> plus one or two multiplications is enough: the exponent halves each level.",
                    "Negative n is handled once at the top by returning <code>1 / go(-n)</code>.",
                ],
                "steps": [
                    "Inner function <code>go(n)</code>: if <code>n == 0</code>, return 1.0.",
                    "Compute <code>half = go(n // 2)</code> once.",
                    "Return <code>half * half</code>, times <code>x</code> if <code>n</code> is odd.",
                    "At the top, return <code>go(n)</code> if <code>n &gt;= 0</code>, else <code>1 / go(-n)</code>.",
                ],
                "why": [
                    "n = 2·(n // 2) + (n % 2), so x<sup>n</sup> = (x<sup>n // 2</sup>)² · x<sup>n % 2</sup>, which is what is returned.",
                    "Computing <code>half</code> once is essential; calling <code>go(n // 2)</code> twice would bring back O(n) calls.",
                    "The exponent halves each level, so there are about log<sub>2</sub> n levels: <strong>O(log n)</strong> time and <strong>O(log n)</strong> recursion stack.",
                ],
                "dry": [
                    [
                        "go(10) calls go(5), which calls go(2), go(1), go(0).",
                        "go(0) = 1.0. go(1): half = 1.0, odd, so 1 · 1 · 2 = 2.0.",
                        "go(2): half = 2.0, even, 4.0. go(5): half = 4.0, odd, 4 · 4 · 2 = 32.0.",
                        "go(10): half = 32.0, even, 32 · 32 = 1024.0.",
                        "It returns <strong>1024.0</strong>.",
                    ],
                    [
                        "n = −2 is negative, so the answer is 1 / go(2).",
                        "go(2) calls go(1), which calls go(0) = 1.0.",
                        "go(1) = 2.0; go(2) = 2.0 · 2.0 = 4.0.",
                        "1 / 4.0 = <strong>0.25</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>half</code> be stored instead of calling twice?",
                     "<code>go(n // 2) * go(n // 2)</code> doubles the calls at every level, and doubling over log n levels gives n calls: back to linear time."],
                    ["Does <code>-n</code> overflow for n = −2<sup>31</sup>?",
                     "Not in Python, whose integers are unbounded. In Java or C++ you would widen to a 64-bit type first."],
                    ["Why is the space O(log n)?",
                     "Each recursive call waits for the one below it, and there are about log<sub>2</sub> n of them on the stack at the deepest point."],
                ],
            },
            "Iterative binary exponentiation": {
                "idea": [
                    "Write n in binary. x<sup>n</sup> is the product of x<sup>2<sup>k</sup></sup> over the bits k that are set: 10 = 8 + 2, so x<sup>10</sup> = x<sup>8</sup> · x<sup>2</sup>.",
                    "Square <code>x</code> each round to get x, x², x⁴, x⁸, …, and multiply it into <code>result</code> when the current lowest bit of n is 1.",
                    "Shifting n right one bit per round reads the bits from lowest to highest.",
                ],
                "steps": [
                    "If <code>n &lt; 0</code>, set <code>x, n = 1 / x, -n</code>.",
                    "Set <code>result = 1.0</code>.",
                    "While <code>n</code> is non-zero: if <code>n &amp; 1</code>, do <code>result *= x</code>.",
                    "Then <code>x *= x</code> and <code>n &gt;&gt;= 1</code>.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "At the start of round k, <code>x</code> holds the original x<sup>2<sup>k</sup></sup>, and <code>n &amp; 1</code> is bit k of the original exponent.",
                    "So <code>result</code> collects exactly the powers whose bits are set, whose product is x<sup>n</sup>.",
                    "One round per bit: <strong>O(log n)</strong> time. Unlike the recursive version, there is no stack: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 10 (binary 1010). Bit 0 is 0: skip; x = 4.0, n = 5.",
                        "Bit 1 is 1: result = 4.0; x = 16.0, n = 2.",
                        "Bit 2 is 0: skip; x = 256.0, n = 1.",
                        "Bit 3 is 1: result = 4.0 × 256.0 = 1024.0; x = 65536.0, n = 0.",
                        "It returns <strong>1024.0</strong>.",
                    ],
                    [
                        "n = −2, so x = 0.5 and n = 2 (binary 10).",
                        "Bit 0 is 0: skip; x = 0.25, n = 1.",
                        "Bit 1 is 1: result = 0.25; x = 0.0625, n = 0.",
                        "It returns <strong>0.25</strong>.",
                    ],
                ],
                "faq": [
                    ["Isn't the last <code>x *= x</code> wasted?",
                     "Yes, the final squaring is never used. It costs one multiplication and keeps the loop simple."],
                    ["Can this overflow even if the answer is small?",
                     "The spare squaring of x can become huge or <code>inf</code>, but it is never multiplied into <code>result</code>, so the answer is unaffected."],
                    ["Where else is this pattern used?",
                     "Modular exponentiation in cryptography and matrix powers for fast Fibonacci use the same square-and-multiply loop."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ multiply strings
    "multiply-strings": {
        "examples": [
            {"call": 'multiply("123", "45")', "expect": '"5535"'},
            {"call": 'multiply("0", "52")', "expect": '"0"'},
        ],
        "approaches": {
            "Schoolbook: add a shifted partial product per digit": {
                "idea": [
                    "Do long multiplication as on paper: multiply <code>num1</code> by one digit of <code>num2</code> at a time, shift the partial product by appending zeros, and add it to a running total.",
                    "Two helpers carry the work: <code>times_digit(a, d)</code> multiplies a digit string by one digit, and <code>add(a, b)</code> adds two digit strings.",
                    "Both helpers process digits from the right with a carry, just like hand arithmetic.",
                ],
                "steps": [
                    "If either input is \"0\", return \"0\" straight away (avoids results like \"000\").",
                    "Set <code>total = \"0\"</code>.",
                    "For each digit <code>ch</code> of <code>num2</code> from the right, with position <code>shift</code>:",
                    "Compute <code>times_digit(num1, int(ch)) + \"0\" * shift</code>, the shifted partial product.",
                    "Set <code>total = add(total, partial)</code>. Return <code>total</code> after the last digit.",
                ],
                "why": [
                    "num1 × num2 = Σ num1 × digit<sub>k</sub> × 10<sup>k</sup>, and each term is exactly one shifted partial product.",
                    "Each <code>times_digit</code> is O(m), and each <code>add</code> runs over the total, which grows to m + n digits, with up to n shift zeros on the partial: <strong>O(m · n + n²)</strong> time.",
                    "The running total and one partial product are <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "Neither input is \"0\". total = \"0\".",
                        "shift 0, digit 5: times_digit(\"123\", 5) = \"615\". total = add(\"0\", \"615\") = \"615\".",
                        "shift 1, digit 4: times_digit(\"123\", 4) = \"492\", shifted to \"4920\".",
                        "add(\"615\", \"4920\"): 5+0=5, 1+2=3, 6+9=15 (write 5, carry 1), 0+4+1=5, giving \"5535\".",
                        "It returns <strong>\"5535\"</strong>.",
                    ],
                    [
                        "num1 == \"0\", so the early return fires.",
                        "No partial products are built.",
                        "Without this check the total would be built from \"0\" partials, which works here, but the guard keeps the code simple.",
                        "It returns <strong>\"0\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just <code>str(int(num1) * int(num2))</code>?",
                     "The problem forbids converting to integers. In Python it would work, but the point is to implement the arithmetic."],
                    ["Where does the n² term come from?",
                     "The k-th partial product has k zeros appended, and <code>add</code> walks all of them. Summed over n digits that is about n²/2 extra work."],
                    ["Why does <code>times_digit</code> append the final carry separately?",
                     "The loop only writes one digit per input digit. A carry left at the end, like the 8 in 99 × 9 = 891, needs one more digit in front of the digits written so far."],
                ],
            },
            "Position array: digit i &times; digit j goes to i + j": {
                "idea": [
                    "Index digits from the right. The product of digit i of num1 and digit j of num2 is worth that product × 10<sup>i+j</sup>, so it belongs in column <code>i + j</code>.",
                    "Accumulate every digit product into an array <code>pos</code> of m + n columns first, ignoring carries.",
                    "Then make one pass from the lowest column, turning each column into a single digit and pushing the rest as a carry.",
                ],
                "steps": [
                    "Create <code>pos = [0] * (m + n)</code>; a product of m and n digits has at most m + n digits.",
                    "For each <code>i, a</code> in reversed <code>num1</code> and <code>j, b</code> in reversed <code>num2</code>, do <code>pos[i + j] += int(a) * int(b)</code>.",
                    "Normalise: for k from 0 upwards, <code>carry, pos[k] = divmod(pos[k] + carry, 10)</code>.",
                    "Read <code>pos</code> from the highest column down into a string and strip leading zeros.",
                    "Return the string, or \"0\" if nothing is left.",
                ],
                "why": [
                    "num1 × num2 = Σ<sub>i,j</sub> a<sub>i</sub> b<sub>j</sub> 10<sup>i+j</sup>, which is Σ<sub>k</sub> pos[k] · 10<sup>k</sup>; the carry pass rewrites the same value with digits 0..9.",
                    "The final carry is 0 because the true product has at most m + n digits.",
                    "The double loop does m · n products and the carry pass m + n steps: <strong>O(m · n)</strong> time. The array is <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "Reversed digits: num1 → 3, 2, 1 and num2 → 5, 4. pos has 5 slots.",
                        "Products: column 0 gets 3·5 = 15; column 1 gets 3·4 + 2·5 = 22; column 2 gets 2·4 + 1·5 = 13; column 3 gets 1·4 = 4. pos = [15, 22, 13, 4, 0].",
                        "Carry pass: 15 → 5 carry 1; 23 → 3 carry 2; 15 → 5 carry 1; 5 → 5 carry 0; 0 → 0.",
                        "pos = [5, 3, 5, 5, 0]; read backwards \"05535\", stripped to \"5535\".",
                        "It returns <strong>\"5535\"</strong>.",
                    ],
                    [
                        "m = 1, n = 2, pos has 3 slots.",
                        "Every product has the digit 0, so pos stays [0, 0, 0] and every carry is 0.",
                        "Read backwards: \"000\", and <code>lstrip(\"0\")</code> leaves the empty string.",
                        "<code>out or \"0\"</code> returns <strong>\"0\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Can a column overflow before the carry pass?",
                     "Not in Python. A column collects at most min(m, n) products of up to 81 each, which is fine even in fixed-width languages for normal lengths."],
                    ["Why m + n slots?",
                     "A number with m digits is below 10<sup>m</sup>, so the product is below 10<sup>m+n</sup> and has at most m + n digits."],
                    ["Why is the <code>or \"0\"</code> needed?",
                     "When the product is 0, stripping leading zeros leaves an empty string, as in example 2."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ detect squares
    "detect-squares": {
        "examples": [
            {"setup": "ds = DetectSquares()\nfor p in ([3, 10], [11, 2], [3, 2], [11, 2]):\n    ds.add(p)",
             "call": "[ds.count([11, 10]), ds.count([14, 8])]", "expect": "[2, 0]"},
            {"setup": "ds = DetectSquares()\nfor p in ([0, 0], [2, 0], [0, 2], [0, 4], [2, 4]):\n    ds.add(p)",
             "call": "ds.count([2, 2])", "expect": "2"},
        ],
        "approaches": {
            "Try every triple of stored points": {
                "idea": [
                    "An axis-aligned square with the query q as one corner is fixed by the <strong>diagonal corner</strong> a: the other two corners must be <code>(qx, ay)</code> and <code>(ax, qy)</code>.",
                    "So try every stored point as a, then search the stored points for those two partners.",
                    "Duplicate points are stored separately, so each copy counts as a different square.",
                ],
                "steps": [
                    "<code>add</code> appends the point as a tuple to <code>self.pts</code>.",
                    "In <code>count</code>, loop over every stored point <code>(ax, ay)</code>.",
                    "Skip it unless <code>ax != qx</code>, <code>ay != qy</code> and <code>abs(ax - qx) == abs(ay - qy)</code>: it must be a true diagonal of a positive-area square.",
                    "For each stored point equal to <code>(qx, ay)</code>, loop again over stored points equal to <code>(ax, qy)</code>, adding 1 per match.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "Every square with corner q has exactly one corner diagonally opposite q, so counting by diagonal corner counts each square once per choice of stored copies.",
                    "Equal side lengths come from the <code>abs</code> test, and positive area from the two inequality checks.",
                    "Three nested loops over N stored points: <strong>O(N³)</strong> per <code>count</code> in the worst case, <strong>O(1)</strong> per <code>add</code>, and <strong>O(N)</strong> space for the list.",
                ],
                "dry": [
                    [
                        "pts = [(3,10), (11,2), (3,2), (11,2)]. count((11, 10)):",
                        "a = (3,10): ay == qy, skip. a = (11,2): ax == qx, skip (both copies).",
                        "a = (3,2): |8| == |8|. Partner (11,2) matches twice; for each, partner (3,10) matches once. total = 2.",
                        "count((14, 8)): no point has |dx| == |dy| (11 vs 2, 3 vs 6, 11 vs 6), so 0.",
                        "It returns <strong>[2, 0]</strong>.",
                    ],
                    [
                        "pts = [(0,0), (2,0), (0,2), (0,4), (2,4)]. count((2, 2)):",
                        "a = (0,0): |2| == |2|. Partners (2,0) and (0,2) exist once each: total = 1.",
                        "a = (2,0), (2,4): ax == qx, skip. a = (0,2): ay == qy, skip.",
                        "a = (0,4): |2| == |2|. Partners (2,4) and (0,2) exist: total = 2.",
                        "It returns <strong>2</strong>: one square below the query and one above.",
                    ],
                ],
                "faq": [
                    ["Why skip points with <code>ay == qy</code>?",
                     "If ax ≠ qx they fail the equal-sides test anyway, and if both match it is the query point itself, which would make a square of side 0."],
                    ["Why count matches instead of checking existence?",
                     "Duplicates count separately: in example 1 there are two copies of (11, 2), and each forms its own square."],
                    ["Why is this too slow?",
                     "With thousands of points and thousands of queries, N³ per query is far beyond any time limit. The counter turns the inner searches into lookups."],
                ],
            },
            "Counter of points, iterate diagonal corners": {
                "idea": [
                    "Store how many times each point was added in a <code>Counter</code>, instead of a list.",
                    "For each distinct diagonal corner (x, y), the number of squares is <code>c × cnt[(x, qy)] × cnt[(qx, y)]</code>: every copy of each corner can be combined with every copy of the others.",
                    "The two inner searches of the brute force become two O(1) lookups.",
                ],
                "steps": [
                    "<code>add</code> does <code>self.cnt[tuple(point)] += 1</code>.",
                    "In <code>count</code>, loop over <code>(x, y), c</code> in <code>self.cnt.items()</code>.",
                    "Skip when <code>x == qx</code> or <code>abs(x - qx) != abs(y - qy)</code>: not a diagonal corner.",
                    "Add <code>c * self.cnt[(x, qy)] * self.cnt[(qx, y)]</code> to <code>total</code>.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "The diagonal corner fixes the square, and the product counts every choice of stored copy for the three corners, matching the brute force.",
                    "A point with <code>y == qy</code> but <code>x != qx</code> fails the <code>abs</code> test because 0 ≠ |x − qx|, so a zero-area square cannot slip through.",
                    "<code>add</code> is <strong>O(1)</strong>; <code>count</code> visits each distinct point once with O(1) lookups: <strong>O(N)</strong>. The counter holds at most N entries: <strong>O(N)</strong> space.",
                ],
                "dry": [
                    [
                        "cnt = {(3,10): 1, (11,2): 2, (3,2): 1}. count((11, 10)):",
                        "(3,10): |8| ≠ |0|, skip. (11,2): x == qx, skip.",
                        "(3,2): |8| == |8|. Add 1 × cnt[(3,10)] × cnt[(11,2)] = 1 × 1 × 2 = 2.",
                        "count((14, 8)): every point fails the abs test, so 0.",
                        "It returns <strong>[2, 0]</strong>.",
                    ],
                    [
                        "cnt has five points, each once. count((2, 2)):",
                        "(0,0): diagonal. Add 1 × cnt[(0,2)] × cnt[(2,0)] = 1. total = 1.",
                        "(2,0), (2,4): x == qx, skip. (0,2): |2| ≠ |0|, skip.",
                        "(0,4): diagonal. Add 1 × cnt[(0,2)] × cnt[(2,4)] = 1. total = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Doesn't <code>self.cnt[(x, qy)]</code> add a key while looping over the Counter?",
                     "No. A Counter returns 0 for a missing key without inserting it, so the dictionary does not change size during the loop."],
                    ["Why multiply the counts instead of adding them?",
                     "Each square picks one copy of each corner independently, so the number of choices is the product. With two copies of (11, 2) the answer doubles."],
                    ["Could I loop over points with the same x as the query instead?",
                     "Yes, a variant indexes points by x and tries each side length from those. It has the same worst case; looping over diagonal corners is simpler."],
                ],
            },
        },
    },
}
