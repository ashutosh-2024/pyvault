"""Write-ups for the Math and Geometry topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ excel column title
    "excel-column-title": {
        "example": {"call": "convert_to_title(701)", "expect": '"ZY"'},
        "approaches": {
            "Recursive: title of the prefix, then the last letter": {
                "idea": [
                    "Column titles are base 26 with digits A..Z standing for 1..26; there is no zero digit (bijective base 26).",
                    "Subtracting 1 turns the last digit into 0..25, so the last letter is <code>chr(65 + (n - 1) % 26)</code>.",
                    "The rest of the title is the title of <code>(n - 1) // 26</code>, which is empty when that is 0.",
                ],
                "steps": [
                    "Base case: n = 0 gives \"\".",
                    "<code>q, r = divmod(n - 1, 26)</code>.",
                    "Return <code>convert_to_title(q) + chr(65 + r)</code>.",
                ],
                "why": [
                    "Each level peels off exactly one letter, applying the 1-based rule at every digit.",
                    "There are log<sub>26</sub>(n) levels: O(log n) time and recursion depth.",
                ],
                "dry": [
                    "701: divmod(700, 26) = (26, 24), so the last letter is chr(65 + 24) = 'Y'.",
                    "26: divmod(25, 26) = (0, 25), so the letter is 'Z'. A plain base-26 conversion would wrongly give \"A0\" here.",
                    "0 gives \"\".",
                    "The result is \"\" + \"Z\" + \"Y\" = <strong>\"ZY\"</strong>.",
                ],
            },
            "Bijective base 26: subtract one per digit": {
                "idea": [
                    "This is the same computation as a loop: at each step subtract 1, take the remainder as a 0-based letter, and divide by 26.",
                    "The letters come out lowest first, so reverse them at the end.",
                ],
                "steps": [
                    "While n is non-zero: <code>n, r = divmod(n - 1, 26)</code> and append <code>chr(65 + r)</code>.",
                    "Return the reversed letters joined together.",
                ],
                "why": [
                    "The \"minus one\" turns the 1-based digit into a 0-based one, and after dividing, the next digit is again 1-based.",
                    "It is O(log n) time and space.",
                ],
                "dry": [
                    "n = 701: divmod(700, 26) = (26, 24), append 'Y'.",
                    "n = 26: divmod(25, 26) = (0, 25), append 'Z'.",
                    "n = 0, so stop. Reversing \"YZ\" gives <strong>\"ZY\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ gcd of strings
    "gcd-of-strings": {
        "example": {"call": 'gcd_of_strings("ABABAB", "ABAB")', "expect": '"AB"'},
        "approaches": {
            "Try every prefix length, longest first": {
                "idea": [
                    "A common divisor x must be a prefix of both strings, and its length must divide both lengths.",
                    "Try lengths from longest to shortest and return the first prefix that rebuilds both strings by repetition.",
                ],
                "steps": [
                    "For L from <code>min(len1, len2)</code> down to 1, skip lengths that do not divide both.",
                    "Check <code>x * (len1 // L) == str1</code> and the same for str2.",
                ],
                "why": [
                    "Longest first means the first match is the greatest common divisor.",
                    "Each check is O(m + n), for up to min(m, n) lengths.",
                ],
                "dry": [
                    "L=4: 6 % 4 ≠ 0, skip. L=3: 4 % 3 ≠ 0, skip.",
                    "L=2: x = \"AB\". \"AB\" × 3 = \"ABABAB\" and \"AB\" × 2 = \"ABAB\", both match.",
                    "The result is <strong>\"AB\"</strong>.",
                ],
            },
            "Concatenation test, then gcd of lengths": {
                "idea": [
                    "If both strings are repetitions of a common x, gluing them in either order gives the same string: x repeated the same number of times.",
                    "The converse also holds, so a single comparison decides whether any common divisor exists.",
                    "If one exists, the longest has length <code>gcd(m, n)</code>, because every common divisor's length divides both lengths.",
                ],
                "steps": [
                    "If <code>str1 + str2 != str2 + str1</code>, return \"\".",
                    "Return <code>str1[:gcd(len1, len2)]</code>.",
                ],
                "why": [
                    "It is one string comparison and one gcd: O(m + n) time and space.",
                ],
                "dry": [
                    "\"ABABAB\" + \"ABAB\" = \"ABABABABAB\", and \"ABAB\" + \"ABABAB\" gives the same.",
                    "gcd(6, 4) = 2.",
                    "The result is <strong>\"AB\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ insert gcd in linked list
    "insert-gcd-linked-list": {
        "example": {"call": "to_list(insert_greatest_common_divisors(build_list([18, 6, 10, 3])))",
                    "expect": "[18, 6, 6, 2, 10, 1, 3]"},
        "approaches": {
            "Walk and insert, gcd by trial division": {
                "idea": [
                    "Walk the list; between each node and its successor, splice in a new node holding their gcd.",
                    "Find the gcd by testing divisors downward from the smaller value; the first common one is the greatest.",
                ],
                "steps": [
                    "For each adjacent pair, <code>node.next = ListNode(gcd(a, b), node.next)</code>.",
                    "Jump two nodes ahead so the inserted node is skipped.",
                ],
                "why": [
                    "Testing from the top down means the first divisor found is the greatest.",
                    "Each gcd costs O(min(a, b)): fine for values up to 1000, but it scales badly.",
                ],
                "dry": [
                    "gcd(18, 6): 6 divides both, so insert 6.",
                    "gcd(6, 10): 6, 5, 4 and 3 fail; 2 divides both, so insert 2.",
                    "gcd(10, 3): 3 and 2 fail; 1 works, so insert 1.",
                    "The result is <strong>[18, 6, 6, 2, 10, 1, 3]</strong>.",
                ],
            },
            "Walk and insert, Euclid's algorithm": {
                "idea": [
                    "Same walk and splice, but compute the gcd with Euclid: <code>gcd(a, b) = gcd(b, a mod b)</code>, until b is 0.",
                    "Each pair of steps at least halves the larger number, so it is logarithmic.",
                ],
                "steps": [
                    "<code>while b: a, b = b, a % b</code>; the gcd is <code>a</code>.",
                    "Splice in the new node and advance two nodes.",
                ],
                "why": [
                    "Any common divisor of a and b also divides a mod b, so the gcd never changes.",
                    "It is O(n log max) time and O(1) extra space.",
                ],
                "dry": [
                    "(18, 6) → (6, 0), so the gcd is 6.",
                    "(6, 10) → (10, 6) → (6, 4) → (4, 2) → (2, 0), so the gcd is 2.",
                    "(10, 3) → (3, 1) → (1, 0), so the gcd is 1.",
                    "The result is <strong>[18, 6, 6, 2, 10, 1, 3]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ transpose matrix
    "transpose-matrix": {
        "example": {"call": "transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9]])", "expect": "[[1, 4, 7], [2, 5, 8], [3, 6, 9]]"},
        "approaches": {
            "New matrix with swapped indices": {
                "idea": [
                    "The transpose sends the cell at (r, c) to (c, r), so an m × n matrix becomes n × m.",
                    "Allocate the result and copy each cell to its mirrored position.",
                ],
                "steps": [
                    "<code>out</code> has n rows and m columns.",
                    "<code>out[c][r] = matrix[r][c]</code> for every cell.",
                ],
                "why": [
                    "Every cell is copied exactly once: O(m·n) time and space, which the output needs anyway.",
                    "<code>list(map(list, zip(*matrix)))</code> is the Python idiom for the same thing.",
                ],
                "dry": [
                    "Row 0 [1, 2, 3] becomes column 0: out[0][0] = 1, out[1][0] = 2, out[2][0] = 3.",
                    "Row 1 [4, 5, 6] becomes column 1, and row 2 [7, 8, 9] becomes column 2.",
                    "The result is <strong>[[1, 4, 7], [2, 5, 8], [3, 6, 9]]</strong>.",
                ],
            },
            "In place, square matrices only": {
                "idea": [
                    "For a square matrix the shape does not change, so the transpose can swap cells in place.",
                    "Swap each cell above the diagonal with its mirror below it. Visit only the upper triangle, or each pair would be swapped twice and end up where it started.",
                ],
                "steps": [
                    "If the matrix is not square, fall back to building a new one.",
                    "For r &lt; c, swap <code>matrix[r][c]</code> with <code>matrix[c][r]</code>.",
                ],
                "why": [
                    "Each off-diagonal pair is swapped exactly once, and the diagonal stays put.",
                    "It is O(n²) time and O(1) space. This is the first half of Rotate Image.",
                ],
                "dry": [
                    "Swap (0, 1) ↔ (1, 0): 2 ↔ 4.",
                    "Swap (0, 2) ↔ (2, 0): 3 ↔ 7.",
                    "Swap (1, 2) ↔ (2, 1): 6 ↔ 8.",
                    "The result is <strong>[[1, 4, 7], [2, 5, 8], [3, 6, 9]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotate image
    "rotate-image": {
        "example": {"setup": "M = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\nrotate(M)",
                    "call": "M", "expect": "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]"},
        "approaches": {
            "Copy into a new matrix": {
                "idea": [
                    "Rotating 90° clockwise sends the cell at (r, c) to (c, n - 1 - r).",
                    "Write every cell to its new place in a fresh matrix, then copy it back.",
                ],
                "steps": [
                    "<code>out[c][n - 1 - r] = matrix[r][c]</code>.",
                    "<code>matrix[:] = out</code>.",
                ],
                "why": [
                    "Each cell lands exactly where the rotation puts it.",
                    "It takes O(n²) extra space, which the problem forbids.",
                ],
                "dry": [
                    "Row 0 (1, 2, 3) becomes the last column: out[0][2] = 1, out[1][2] = 2, out[2][2] = 3.",
                    "Row 1 becomes the middle column, and row 2 becomes the first.",
                    "The result is <strong>[[7, 4, 1], [8, 5, 2], [9, 6, 3]]</strong>.",
                ],
            },
            "Transpose, then reverse each row": {
                "idea": [
                    "A rotation is two simple reflections: transposing sends (r, c) to (c, r), and reversing each row then sends (c, r) to (c, n - 1 - r).",
                    "Both reflections work in place, and the combination is exactly the clockwise rotation.",
                ],
                "steps": [
                    "Transpose: swap <code>matrix[r][c]</code> and <code>matrix[c][r]</code> for r &lt; c.",
                    "Reverse every row.",
                ],
                "why": [
                    "Composing the two mappings gives (r, c) → (c, n - 1 - r).",
                    "It is O(n²) time and O(1) space, with two passes that are hard to get wrong.",
                ],
                "dry": [
                    "After the transpose: [[1, 4, 7], [2, 5, 8], [3, 6, 9]].",
                    "Reversing each row: [7, 4, 1], [8, 5, 2], [9, 6, 3].",
                    "The result is <strong>[[7, 4, 1], [8, 5, 2], [9, 6, 3]]</strong>.",
                ],
            },
            "Rotate four cells at a time, layer by layer": {
                "idea": [
                    "Under the rotation, cells move in cycles of four: top → right → bottom → left → top.",
                    "Walk each concentric square layer, and for each position move its four cells around with a single temporary variable.",
                    "Every cell is written once, but the index arithmetic is easy to get wrong.",
                ],
                "steps": [
                    "For each layer with <code>first = layer</code> and <code>last = n - 1 - layer</code>, and each i from first to last - 1:",
                    "Save top, move left → top, bottom → left, right → bottom, and saved top → right.",
                ],
                "why": [
                    "The four positions of each cycle are exactly the images of one another under the rotation.",
                    "It is O(n²) time and O(1) space.",
                ],
                "dry": [
                    "Layer 0, i=0: the four corners. 1 is saved, 7 moves to the top-left, 9 to the bottom-left, 3 to the bottom-right, and 1 to the top-right: [[7, 2, 1], [4, 5, 6], [9, 8, 3]].",
                    "i=1: the four edge middles. 2 is saved, then 4 → top, 8 → left, 6 → bottom, 2 → right: [[7, 4, 1], [8, 5, 2], [9, 6, 3]].",
                    "The centre 5 stays put. The result is <strong>[[7, 4, 1], [8, 5, 2], [9, 6, 3]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ spiral matrix
    "spiral-matrix": {
        "example": {"call": "spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])",
                    "expect": "[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]"},
        "approaches": {
            "Simulate with a visited grid": {
                "idea": [
                    "Walk like a robot: keep going in the current direction, and turn right when the next cell is off the grid or already visited.",
                    "A visited grid makes the turning rule trivial.",
                ],
                "steps": [
                    "Directions in order: right, down, left, up.",
                    "For m·n steps, record the cell, mark it, and turn if the next cell is blocked.",
                ],
                "why": [
                    "Turning right at every blocked cell traces the spiral exactly.",
                    "It is O(m·n) time and O(m·n) extra space for the visited grid.",
                ],
                "dry": [
                    "Right along the top: 1, 2, 3, 4. Off the grid, so turn down.",
                    "Down: 8, 12. Off the grid, so turn left: 11, 10, 9.",
                    "Off the grid, so turn up: 5. The next cell (1) is visited, so turn right: 6, 7.",
                    "All 12 cells are recorded: <strong>[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]</strong>.",
                ],
            },
            "Shrinking boundaries": {
                "idea": [
                    "Keep four walls: <code>top</code>, <code>bottom</code>, <code>left</code>, <code>right</code>.",
                    "Read the top row left to right, the right column downwards, the bottom row backwards and the left column upwards, moving each wall inwards after reading its side.",
                    "Two guards stop a lone middle row or column from being read twice.",
                ],
                "steps": [
                    "Top row, then <code>top += 1</code>; right column, then <code>right -= 1</code>.",
                    "If <code>top &lt;= bottom</code>: bottom row reversed, then <code>bottom -= 1</code>.",
                    "If <code>left &lt;= right</code>: left column upwards, then <code>left += 1</code>.",
                ],
                "why": [
                    "Each wall move retires one fully read row or column.",
                    "It is O(m·n) time and O(1) extra space beyond the output.",
                ],
                "dry": [
                    "Lap 1: the top row gives 1, 2, 3, 4 (top = 1); the right column gives 8, 12 (right = 2).",
                    "The bottom row reversed gives 11, 10, 9 (bottom = 1); the left column upwards gives 5 (left = 1).",
                    "Lap 2: the top row is row 1, columns 1..2: 6, 7 (top = 2). The right column has no rows left (right = 1).",
                    "top &gt; bottom, so the bottom row is skipped, and the left column has no rows either. Both guards were needed here.",
                    "The result is <strong>[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ set matrix zeroes
    "set-matrix-zeroes": {
        "example": {"setup": "M = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]\nset_zeroes(M)",
                    "call": "M", "expect": "[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]"},
        "approaches": {
            "Copy the matrix, read from the copy": {
                "idea": [
                    "Zeroing cells as you go would create new zeros that wrongly spread further.",
                    "So find the zeros in an untouched copy, and for each one clear its whole row and column in the real matrix.",
                ],
                "steps": [
                    "Copy every row.",
                    "For each zero in the copy, zero its row and column in <code>matrix</code>.",
                ],
                "why": [
                    "Reading from the copy keeps new zeros from cascading.",
                    "Each zero clears m + n cells: O(m·n·(m + n)) time and O(m·n) space.",
                ],
                "dry": [
                    "The copy has zeros at (0, 0) and (0, 3).",
                    "(0, 0) clears row 0 and column 0; (0, 3) clears row 0 and column 3.",
                    "The result is <strong>[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]</strong>.",
                ],
            },
            "Row and column marker sets": {
                "idea": [
                    "Only two facts matter: which rows contain a zero, and which columns contain a zero.",
                    "Record them in one pass, then zero every cell whose row or column is marked.",
                ],
                "steps": [
                    "Pass 1: add r to <code>rows</code> and c to <code>cols</code> for each zero.",
                    "Pass 2: zero the cell if <code>r in rows or c in cols</code>.",
                ],
                "why": [
                    "The markers are recorded before anything changes, so there is no cascading.",
                    "It is O(m·n) time and O(m + n) space.",
                ],
                "dry": [
                    "rows = {0}, cols = {0, 3}.",
                    "Row 0 becomes all zeros. Rows 1 and 2 lose columns 0 and 3.",
                    "The result is <strong>[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]</strong>.",
                ],
            },
            "Use the first row and column as the markers": {
                "idea": [
                    "Store the markers inside the matrix itself: a zero at (r, c) sets <code>matrix[r][0]</code> and <code>matrix[0][c]</code> to 0.",
                    "The first row and column now act as the marker arrays. Their markers collide at <code>matrix[0][0]</code>, so keep one extra flag for the first column.",
                    "Order is everything: clear the inner cells first, then the first row, then the first column, so no marker is wiped before it is read.",
                ],
                "steps": [
                    "<code>first_col_zero</code> records whether column 0 itself holds a zero.",
                    "Mark: for every zero with c ≥ 1, set <code>matrix[r][0] = matrix[0][c] = 0</code>.",
                    "Clear the inner cells (r, c ≥ 1) whose row or column marker is 0.",
                    "If <code>matrix[0][0] == 0</code>, clear row 0; if the flag is set, clear column 0.",
                ],
                "why": [
                    "Every marker is read before the row or column holding it is overwritten.",
                    "It is O(m·n) time and O(1) extra space.",
                ],
                "dry": [
                    "first_col_zero = True, because (0, 0) is 0.",
                    "Marking: the zero at (0, 3) sets matrix[0][3] = 0 (already 0) and matrix[0][0] = 0.",
                    "Inner pass: the column 3 marker is 0, so (1, 3) and (2, 3) become 0. The row markers 3 and 1 are non-zero.",
                    "matrix[0][0] == 0, so clear row 0. The flag is set, so clear column 0.",
                    "The result is <strong>[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ happy number
    "happy-number": {
        "example": {"call": "is_happy(19)", "expect": "True"},
        "approaches": {
            "Hash set of values seen": {
                "idea": [
                    "Repeatedly replace n with the sum of the squares of its digits.",
                    "Either 1 is reached (happy), or a value repeats, which means a cycle that never reaches 1.",
                    "Remember every value seen to detect the repeat.",
                ],
                "steps": [
                    "While n is not 1 and not yet seen: add it to <code>seen</code> and step.",
                    "Return <code>n == 1</code>.",
                ],
                "why": [
                    "Values quickly fall below 243 and stay there, so a repeat or a 1 must come soon.",
                    "The set stays tiny: effectively O(log n) time and space.",
                ],
                "dry": [
                    "19 gives 1² + 9² = 82.",
                    "82 gives 64 + 4 = 68. 68 gives 36 + 64 = 100.",
                    "100 gives 1, so stop. The result is <strong>True</strong>.",
                ],
            },
            "Floyd's cycle detection": {
                "idea": [
                    "The sequence n, step(n), step(step(n)), … behaves like a linked list defined by a function.",
                    "Tortoise and hare detect its cycle with no memory: slow takes one step, fast two, until they meet.",
                    "1 maps to itself, a cycle of length one, so n is happy exactly when fast reaches 1.",
                ],
                "steps": [
                    "<code>slow = n</code>, <code>fast = step(n)</code>.",
                    "While <code>fast != 1</code> and <code>slow != fast</code>: advance slow once and fast twice.",
                    "Return <code>fast == 1</code>.",
                ],
                "why": [
                    "Every sequence eventually cycles; Floyd finds the cycle, and the only question is whether it is {1}.",
                    "It takes O(1) space.",
                ],
                "dry": [
                    "slow = 19, fast = 82.",
                    "Round 1: slow = 82, fast = step(step(82)) = step(68) = 100.",
                    "Round 2: slow = 68, fast = step(step(100)) = step(1) = 1.",
                    "fast == 1, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ plus one
    "plus-one": {
        "example": {"call": "plus_one([1, 2, 9, 9])", "expect": "[1, 3, 0, 0]"},
        "approaches": {
            "Convert to an integer and back": {
                "idea": [
                    "Join the digits into a number, add one, and split the result back into digits.",
                    "This works in Python because integers have no size limit; fixed-width languages would overflow on long inputs.",
                ],
                "steps": [
                    "<code>int(\"\".join(map(str, digits))) + 1</code>.",
                    "Split <code>str(...)</code> back into ints.",
                ],
                "why": [
                    "It is O(n) time and space.",
                ],
                "dry": [
                    "The digits join to 1299; adding 1 gives 1300.",
                    "Split: <strong>[1, 3, 0, 0]</strong>.",
                ],
            },
            "Carry from the end": {
                "idea": [
                    "Add one at the last digit. A digit below 9 just goes up by one and you are done.",
                    "A 9 becomes 0 and the carry moves one place left.",
                    "If every digit was 9, the answer is a 1 followed by zeros.",
                ],
                "steps": [
                    "Walk from the last index: if the digit is below 9, increment it and return.",
                    "Otherwise set it to 0 and continue.",
                    "After the loop, return <code>[1] + digits</code>.",
                ],
                "why": [
                    "This is exactly decimal addition of 1.",
                    "It stops at the first non-9, so it is usually O(1) work; the all-nines case is O(n).",
                ],
                "dry": [
                    "The last digit is 9, so it becomes 0 and the carry continues.",
                    "The next 9 becomes 0 as well.",
                    "The 2 is below 9, so it becomes 3; return.",
                    "The result is <strong>[1, 3, 0, 0]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ roman to integer
    "roman-to-integer": {
        "example": {"call": 'roman_to_int("MCMXCIV")', "expect": "1994"},
        "approaches": {
            "Match the two-letter pairs first": {
                "idea": [
                    "Roman numerals add symbol values, except for six subtractive pairs: IV, IX, XL, XC, CD, CM.",
                    "At each position, check for one of those pairs first; otherwise read a single symbol.",
                ],
                "steps": [
                    "If <code>s[i:i+2]</code> is a known pair, add its value and skip 2.",
                    "Otherwise add the single symbol's value and skip 1.",
                ],
                "why": [
                    "Pairs never overlap, so a greedy left-to-right scan is safe.",
                    "It is O(n) time, but it lists the special cases one by one.",
                ],
                "dry": [
                    "M: 1000.",
                    "CM is a pair: +900, total 1900.",
                    "XC is a pair: +90, total 1990.",
                    "IV is a pair: +4, total <strong>1994</strong>.",
                ],
            },
            "Subtract when smaller than the next symbol": {
                "idea": [
                    "Every subtractive pair is a smaller symbol placed before a larger one.",
                    "So add each symbol's value, unless it is smaller than the symbol after it, in which case subtract it.",
                    "That one rule covers all six special pairs without listing them.",
                ],
                "steps": [
                    "For each symbol, compare its value with the next symbol's.",
                    "Subtract if it is smaller, otherwise add.",
                ],
                "why": [
                    "IV = -1 + 5 = 4, IX = -1 + 10 = 9, and so on: the rule reproduces every pair.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "M (1000) is not smaller than C, so +1000.",
                    "C (100) &lt; M, so -100 (900). M: +1000, total 1900.",
                    "X &lt; C, so -10 (1890). C: +100, total 1990.",
                    "I &lt; V, so -1 (1989). V: +5, total <strong>1994</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pow(x, n)
    "pow-x-n": {
        "example": {"call": "my_pow(2.0, 10)", "expect": "1024.0"},
        "approaches": {
            "Multiply n times": {
                "idea": [
                    "x<sup>n</sup> is x multiplied by itself n times; a negative n means using 1/x instead.",
                ],
                "steps": [
                    "If n &lt; 0, use <code>1 / x</code> and <code>-n</code>.",
                    "Multiply <code>result</code> by x, n times.",
                ],
                "why": [
                    "It is correct by definition, but it takes two billion iterations for the largest exponent.",
                ],
                "dry": [
                    "result goes 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024.",
                    "That is ten multiplications, giving <strong>1024.0</strong>.",
                ],
            },
            "Recursive squaring": {
                "idea": [
                    "x<sup>n</sup> = (x<sup>n/2</sup>)², with one extra factor of x when n is odd.",
                    "Each step halves the exponent, so only about log n multiplications are needed.",
                ],
                "steps": [
                    "<code>go(0) = 1</code>.",
                    "<code>half = go(n // 2)</code>; return <code>half · half · (x if n is odd else 1)</code>.",
                    "Handle a negative n with <code>1 / go(-n)</code>.",
                ],
                "why": [
                    "The exponents add up correctly: 2·(n // 2) + (n % 2) = n.",
                    "It is O(log n) time and O(log n) recursion depth.",
                ],
                "dry": [
                    "go(10) needs go(5), which needs go(2), which needs go(1), which needs go(0) = 1.",
                    "go(1) = 1 · 1 · 2 = 2. go(2) = 2 · 2 = 4.",
                    "go(5) = 4 · 4 · 2 = 32. go(10) = 32 · 32 = <strong>1024.0</strong>.",
                ],
            },
            "Iterative binary exponentiation": {
                "idea": [
                    "Write n in binary; x<sup>n</sup> is the product of x<sup>2<sup>k</sup></sup> over the set bits k of n.",
                    "Read n's bits from low to high while squaring a running base (x, x², x⁴, …), and multiply the base into the result whenever the current bit is 1.",
                ],
                "steps": [
                    "If n &lt; 0, invert x and negate n.",
                    "While n is non-zero: if <code>n &amp; 1</code>, multiply result by x; square x; shift n right.",
                ],
                "why": [
                    "Each set bit contributes exactly its power of x.",
                    "It is O(log n) time and O(1) space; modular exponentiation in cryptography works the same way.",
                ],
                "dry": [
                    "n = 10 = 1010 in binary.",
                    "Bit 0 is 0: skip. x becomes 4.",
                    "Bit 1 is 1: result = 4. x becomes 16.",
                    "Bit 2 is 0: skip. x becomes 256.",
                    "Bit 3 is 1: result = 4 · 256 = <strong>1024.0</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ multiply strings
    "multiply-strings": {
        "example": {"call": 'multiply("123", "45")', "expect": '"5535"'},
        "approaches": {
            "Schoolbook: add a shifted partial product per digit": {
                "idea": [
                    "This is pencil-and-paper multiplication: for each digit of the second number, multiply the whole first number by it.",
                    "Shift each partial product by appending zeros for its place, and add it to a running total with string addition.",
                ],
                "steps": [
                    "<code>times_digit(a, d)</code>: multiply a string by one digit, with a carry.",
                    "<code>add(a, b)</code>: add two digit strings from the right.",
                    "For the digit at position <code>shift</code> (from the right), add <code>times_digit(num1, d) + \"0\" · shift</code>.",
                ],
                "why": [
                    "The sum of the shifted partial products is the product.",
                    "It is O(m·n) for the partial products, plus repeated string additions.",
                ],
                "dry": [
                    "Digit 5 (shift 0): 123 × 5 = \"615\". The total is \"615\".",
                    "Digit 4 (shift 1): 123 × 4 = \"492\", shifted to \"4920\".",
                    "615 + 4920 = <strong>\"5535\"</strong>.",
                ],
            },
            "Position array: digit i &times; digit j goes to i + j": {
                "idea": [
                    "Counting digits from the right, digit i of num1 times digit j of num2 contributes to position i + j of the product.",
                    "Accumulate every such product into an array of m + n slots, then make one carry pass from the lowest position up.",
                    "No intermediate strings and no repeated additions are needed.",
                ],
                "steps": [
                    "<code>pos[i + j] += a · b</code> for every digit pair.",
                    "Carry: <code>carry, pos[k] = divmod(pos[k] + carry, 10)</code> for k from 0 upwards.",
                    "Reverse, strip leading zeros, and return \"0\" if nothing is left.",
                ],
                "why": [
                    "Place values multiply: 10<sup>i</sup> × 10<sup>j</sup> = 10<sup>i + j</sup>.",
                    "It is O(m·n) time and O(m + n) space.",
                ],
                "dry": [
                    "Digits from the right: num1 = 3, 2, 1 and num2 = 5, 4.",
                    "pos[0] = 3·5 = 15; pos[1] = 3·4 + 2·5 = 22; pos[2] = 2·4 + 1·5 = 13; pos[3] = 1·4 = 4.",
                    "Carry pass: 15 gives 5, carry 1; 23 gives 3, carry 2; 15 gives 5, carry 1; 5 gives 5.",
                    "Reading back: \"05535\", stripped to <strong>\"5535\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ detect squares
    "detect-squares": {
        "example": {"setup": "ds = DetectSquares()\nfor p in ([3, 10], [11, 2], [3, 2], [11, 2]):\n    ds.add(p)",
                    "call": "[ds.count([11, 10]), ds.count([14, 8])]", "expect": "[2, 0]"},
        "approaches": {
            "Try every triple of stored points": {
                "idea": [
                    "An axis-aligned square with the query q is fixed by the corner diagonally opposite q; the other two corners are then forced.",
                    "Brute force: try every stored point as that diagonal, and every pair of stored points as the two forced corners.",
                ],
                "steps": [
                    "For a diagonal candidate a, skip it unless it differs from q in both coordinates by the same amount.",
                    "Count stored points equal to <code>(qx, ay)</code>, and for each, stored points equal to <code>(ax, qy)</code>.",
                ],
                "why": [
                    "It counts exactly the ordered triples that form a square, with duplicates counted separately.",
                    "It is O(N³) per query.",
                ],
                "dry": [
                    "count(11, 10): (3, 10) shares q's y, skip. (11, 2) shares q's x, skip.",
                    "(3, 2) is 8 away in both directions, so it is a diagonal. It needs (11, 2), which is stored twice, and (3, 10), stored once: 2 squares.",
                    "The second copy of (11, 2) shares q's x, skip. Total <strong>2</strong>.",
                    "count(14, 8): no stored point is the same distance away in x and y, so <strong>0</strong>.",
                ],
            },
            "Counter of points, iterate diagonal corners": {
                "idea": [
                    "Count each stored point's multiplicity.",
                    "For each distinct stored point that can be q's diagonal (non-zero equal distance in x and y), the other two corners are <code>(x, qy)</code> and <code>(qx, y)</code>.",
                    "The number of squares is the product of the three corners' counts.",
                ],
                "steps": [
                    "<code>add</code>: <code>cnt[tuple(point)] += 1</code>.",
                    "<code>count</code>: for each (x, y) with count c that is a valid diagonal, add <code>c · cnt[(x, qy)] · cnt[(qx, y)]</code>.",
                ],
                "why": [
                    "Each square has exactly one diagonal corner, so nothing is double counted, and multiplicities multiply.",
                    "<code>add</code> is O(1) and <code>count</code> is O(distinct points).",
                ],
                "dry": [
                    "cnt = {(3, 10): 1, (11, 2): 2, (3, 2): 1}.",
                    "count(11, 10): (3, 10) has dy = 0, skip. (11, 2) has the same x, skip.",
                    "(3, 2) is a diagonal: 1 × cnt[(3, 10)] = 1 × cnt[(11, 2)] = 2, giving <strong>2</strong>.",
                    "count(14, 8): no valid diagonal, so <strong>0</strong>.",
                ],
            },
        },
    },
}
