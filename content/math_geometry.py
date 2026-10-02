# -*- coding: utf-8 -*-
"""Math and Geometry topic (NeetCode 250: Math & Geometry). Same build
contract as content/dsa.py."""

PRELUDE_MATH = '''import math
import random
from collections import Counter, defaultdict


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out
'''


MATH_TOPIC = dict(
    id="math",
    title="Math and Geometry",
    prelude=PRELUDE_MATH,
    sections=[

dict(
    id="math-geometry",
    title="Number tricks and matrix walks",
    idea=[
        "Two families live here. Number problems reward a known identity &mdash; Euclid's gcd, fast exponentiation, cycle detection on a digit function. Matrix problems reward thinking in <em>layers</em> or <em>index maps</em> (<code>(r, c) &rarr; (c, n-1-r)</code>) and, for the space-optimal versions, using the matrix's own first row and column as scratch memory.",
    ],
    problems=[

    # ------------------------------------------------------------------ 168
    dict(
        id="excel-column-title",
        lc=168, slug="excel-sheet-column-title",
        name="Excel Sheet Column Title",
        difficulty="easy",
        framing=[
            "Convert 1 &rarr; A, 26 &rarr; Z, 27 &rarr; AA, 28 &rarr; AB. It looks like base 26, but there is no digit for zero: the digits run 1..26. That shift-by-one is the entire problem.",
        ],
        pitfall="Using <code>n % 26</code> directly. For 26 it gives 0, which has no letter. Subtract 1 before each division step.",
        approaches=[
            dict(
                name="Recursive: title of the prefix, then the last letter",
                time="O(log n)",
                space="O(log n)",
                why=[
                    "The last letter encodes <code>(n - 1) % 26</code>, and the rest of the title is the title of <code>(n - 1) // 26</code> (empty when that is 0). Writing it recursively makes the \"digits are 1..26\" rule explicit at each level; the loop below is the same computation without the call stack.",
                ],
                code='''def convert_to_title(n):
    if n == 0:
        return ""
    q, r = divmod(n - 1, 26)
    return convert_to_title(q) + chr(65 + r)''',
            ),
            dict(
                name="Bijective base 26: subtract one per digit",
                time="O(log n)",
                space="O(log n)",
                best=True,
                why=[
                    "Each step: subtract 1 so the last digit is in 0..25, map it to a letter, then divide by 26. The subtraction converts the 1-based digit into a 0-based one; after dividing, the next digit is again 1-based, so the pattern repeats.",
                ],
                code='''def convert_to_title(n):
    out = []
    while n:
        n, r = divmod(n - 1, 26)
        out.append(chr(65 + r))
    return "".join(reversed(out))''',
            ),
        ],
        tests='''assert convert_to_title(1) == "A" and convert_to_title(28) == "AB" and convert_to_title(701) == "ZY"
assert convert_to_title(26) == "Z" and convert_to_title(52) == "AZ" and convert_to_title(2147483647) == "FXSHRXW"
def title_to_number(t):
    v = 0
    for ch in t:
        v = v * 26 + ord(ch) - 64
    return v
for n in range(1, 2000):
    assert title_to_number(convert_to_title(n)) == n''',
    ),

    # ------------------------------------------------------------------ 1071
    dict(
        id="gcd-of-strings",
        lc=1071, slug="greatest-common-divisor-of-strings",
        name="Greatest Common Divisor of Strings",
        difficulty="easy",
        framing=[
            "Return the longest string x such that both <code>str1</code> and <code>str2</code> are x repeated some number of times. The lengths behave like integers under gcd &mdash; and a single concatenation test tells you whether any common divisor exists at all.",
        ],
        approaches=[
            dict(
                name="Try every prefix length, longest first",
                time="O(min(m, n) &middot; (m + n))",
                space="O(m + n)",
                why=[
                    "For each length L dividing both lengths, check whether repeating the prefix of length L rebuilds both strings. Return the first (longest) that works.",
                ],
                code='''def gcd_of_strings(str1, str2):
    for L in range(min(len(str1), len(str2)), 0, -1):
        if len(str1) % L == 0 and len(str2) % L == 0:
            x = str1[:L]
            if x * (len(str1) // L) == str1 and x * (len(str2) // L) == str2:
                return x
    return ""''',
            ),
            dict(
                name="Concatenation test, then gcd of lengths",
                time="O(m + n)",
                space="O(m + n)",
                best=True,
                why=[
                    "If both strings are repetitions of a common x, then <code>str1 + str2 == str2 + str1</code> (both are x repeated the same number of times). The converse also holds. So test that once. If it passes, the answer is the prefix of length <code>gcd(m, n)</code>: every common divisor's length divides both lengths, and the gcd length is the longest that does.",
                ],
                code='''def gcd_of_strings(str1, str2):
    if str1 + str2 != str2 + str1:
        return ""
    return str1[:math.gcd(len(str1), len(str2))]''',
            ),
        ],
        tests='''assert gcd_of_strings("ABCABC", "ABC") == "ABC" and gcd_of_strings("ABABAB", "ABAB") == "AB"
assert gcd_of_strings("LEET", "CODE") == ""
rng = random.Random(0)
for _ in range(80):
    base = "".join(rng.choice("AB") for _ in range(rng.randint(1, 3)))
    a = base * rng.randint(1, 4)
    b = base * rng.randint(1, 4) if rng.random() < 0.7 else "".join(rng.choice("AB") for _ in range(rng.randint(1, 6)))
    brute = ""
    for L in range(min(len(a), len(b)), 0, -1):
        if len(a) % L == 0 and len(b) % L == 0 and a[:L] * (len(a) // L) == a and a[:L] * (len(b) // L) == b:
            brute = a[:L]; break
    assert gcd_of_strings(a, b) == brute''',
    ),

    # ------------------------------------------------------------------ 2807
    dict(
        id="insert-gcd-linked-list",
        lc=2807, slug="insert-greatest-common-divisors-in-linked-list",
        name="Insert Greatest Common Divisors in Linked List",
        difficulty="medium",
        framing=[
            "Between every pair of adjacent nodes, insert a new node holding their gcd. A pointer walk plus Euclid's algorithm, which is worth writing by hand once: <code>gcd(a, b) = gcd(b, a mod b)</code>.",
        ],
        approaches=[
            dict(
                name="Walk and insert, gcd by trial division",
                time="O(n &middot; min(a, b))",
                space="O(1)",
                why=[
                    "Compute each gcd by testing divisors downward from the smaller value. Correct but slow for large values (up to 1000 here, so it passes, but it scales badly).",
                ],
                code='''def insert_greatest_common_divisors(head):
    def gcd(a, b):
        for d in range(min(a, b), 0, -1):
            if a % d == 0 and b % d == 0:
                return d

    node = head
    while node and node.next:
        node.next = ListNode(gcd(node.val, node.next.val), node.next)
        node = node.next.next
    return head''',
            ),
            dict(
                name="Walk and insert, Euclid's algorithm",
                time="O(n log max)",
                space="O(1)",
                best=True,
                why=[
                    "Replace (a, b) by (b, a mod b) until b is 0. Each two steps at least halve the larger value, so it takes O(log max) iterations. Then splice the new node in and jump two nodes forward so the inserted node is not itself processed.",
                ],
                code='''def insert_greatest_common_divisors(head):
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    node = head
    while node and node.next:
        node.next = ListNode(gcd(node.val, node.next.val), node.next)
        node = node.next.next                # skip the node just inserted
    return head''',
            ),
        ],
        tests='''assert to_list(insert_greatest_common_divisors(build_list([18, 6, 10, 3]))) == [18, 6, 6, 2, 10, 1, 3]
assert to_list(insert_greatest_common_divisors(build_list([7]))) == [7]
rng = random.Random(1)
for _ in range(40):
    vals = [rng.randint(1, 100) for _ in range(rng.randint(1, 8))]
    expect = []
    for a, b in zip(vals, vals[1:]):
        expect += [a, math.gcd(a, b)]
    expect.append(vals[-1])
    assert to_list(insert_greatest_common_divisors(build_list(vals))) == expect''',
    ),

    # ------------------------------------------------------------------ 867
    dict(
        id="transpose-matrix",
        lc=867, slug="transpose-matrix",
        name="Transpose Matrix",
        difficulty="easy",
        framing=[
            "Flip a matrix over its main diagonal: <code>result[c][r] = matrix[r][c]</code>. A non-square matrix changes shape (m &times; n becomes n &times; m), so it cannot be done in place in general; a square one can.",
        ],
        approaches=[
            dict(
                name="New matrix with swapped indices",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                best=True,
                why=[
                    "Allocate an n &times; m result and copy each cell to its mirrored position. The output needs that space anyway. <code>list(map(list, zip(*matrix)))</code> is the Python idiom for the same thing.",
                ],
                code='''def transpose(matrix):
    m, n = len(matrix), len(matrix[0])
    out = [[0] * m for _ in range(n)]
    for r in range(m):
        for c in range(n):
            out[c][r] = matrix[r][c]
    return out''',
            ),
            dict(
                name="In place, square matrices only",
                time="O(n&sup2;)",
                space="O(1)",
                why=[
                    "For a square matrix, swap each cell above the diagonal with its mirror below. Only the upper triangle is visited, or every pair would be swapped twice and end where it started. This in-place transpose is the first half of Rotate Image.",
                ],
                code='''def transpose(matrix):
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        return [list(col) for col in zip(*matrix)]   # shape changes: must copy
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    return matrix''',
            ),
        ],
        tests='''assert transpose([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
assert transpose([[5]]) == [[5]]''',
    ),

    # ------------------------------------------------------------------ 48
    dict(
        id="rotate-image",
        lc=48, slug="rotate-image",
        name="Rotate Image",
        difficulty="medium",
        framing=[
            "Rotate an n &times; n matrix 90&deg; clockwise, <strong>in place</strong>. Cell <code>(r, c)</code> moves to <code>(c, n-1-r)</code>. Either apply that map in cycles of four, or notice that a rotation is a transpose followed by a horizontal flip.",
        ],
        approaches=[
            dict(
                name="Copy into a new matrix",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                tag="not in place",
                why=["Write each cell to its rotated position in a copy, then copy back. Correct, but the problem forbids the extra matrix."],
                code='''def rotate(matrix):
    n = len(matrix)
    out = [[0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            out[c][n - 1 - r] = matrix[r][c]
    matrix[:] = out''',
            ),
            dict(
                name="Transpose, then reverse each row",
                time="O(n&sup2;)",
                space="O(1)",
                best=True,
                why=[
                    "Transposing sends <code>(r, c)</code> to <code>(c, r)</code>; reversing each row then sends <code>(c, r)</code> to <code>(c, n-1-r)</code> &mdash; exactly the rotation. Two simple in-place passes that are hard to get wrong. (Counter-clockwise: transpose, then reverse each column.)",
                ],
                code='''def rotate(matrix):
    n = len(matrix)
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    for row in matrix:
        row.reverse()''',
            ),
            dict(
                name="Rotate four cells at a time, layer by layer",
                time="O(n&sup2;)",
                space="O(1)",
                why=[
                    "Each cell belongs to a cycle of four positions: top &rarr; right &rarr; bottom &rarr; left. Walk each concentric layer and move those four cells with one temporary. Every cell is written exactly once, versus twice in the transpose version &mdash; at the cost of index arithmetic that is easy to get wrong.",
                ],
                code='''def rotate(matrix):
    n = len(matrix)
    for layer in range(n // 2):
        first, last = layer, n - 1 - layer
        for i in range(first, last):
            off = i - first
            top = matrix[first][i]
            matrix[first][i] = matrix[last - off][first]     # left -> top
            matrix[last - off][first] = matrix[last][last - off]  # bottom -> left
            matrix[last][last - off] = matrix[i][last]       # right -> bottom
            matrix[i][last] = top                            # top -> right''',
            ),
        ],
        tests='''for n in range(1, 7):
    M = [[r * n + c for c in range(n)] for r in range(n)]
    expect = [list(row) for row in zip(*M[::-1])]
    rotate(M)
    assert M == expect, n''',
    ),

    # ------------------------------------------------------------------ 54
    dict(
        id="spiral-matrix",
        lc=54, slug="spiral-matrix",
        name="Spiral Matrix",
        difficulty="medium",
        framing=[
            "Return all elements in clockwise spiral order. The difficulty is purely in the boundaries &mdash; especially for non-square matrices, where the spiral can end on a single row or column that must not be walked twice.",
        ],
        approaches=[
            dict(
                name="Simulate with a visited grid",
                time="O(m &middot; n)",
                space="O(m &middot; n)",
                why=[
                    "Move in the current direction; when the next cell is off the grid or already visited, turn right. The visited grid makes the turning rule trivial, at the cost of O(m &middot; n) extra memory.",
                ],
                code='''def spiral_order(matrix):
    m, n = len(matrix), len(matrix[0])
    seen = [[False] * n for _ in range(m)]
    dr, dc = [0, 1, 0, -1], [1, 0, -1, 0]
    r = c = d = 0
    out = []
    for _ in range(m * n):
        out.append(matrix[r][c])
        seen[r][c] = True
        nr, nc = r + dr[d], c + dc[d]
        if not (0 <= nr < m and 0 <= nc < n) or seen[nr][nc]:
            d = (d + 1) % 4
            nr, nc = r + dr[d], c + dc[d]
        r, c = nr, nc
    return out''',
            ),
            dict(
                name="Shrinking boundaries",
                time="O(m &middot; n)",
                space="O(1) beyond output",
                best=True,
                why=[
                    "Keep four walls: top, bottom, left, right. Walk the top row, then the right column, then (if a row is still left) the bottom row backwards, then (if a column is still left) the left column upwards, shrinking the matching wall after each side. The two <code>if</code> checks are what stop a lone middle row or column from being read twice.",
                ],
                code='''def spiral_order(matrix):
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        out += matrix[top][left:right + 1]
        top += 1
        out += [matrix[r][right] for r in range(top, bottom + 1)]
        right -= 1
        if top <= bottom:
            out += matrix[bottom][left:right + 1][::-1]
            bottom -= 1
        if left <= right:
            out += [matrix[r][left] for r in range(bottom, top - 1, -1)]
            left += 1
    return out''',
            ),
        ],
        tests='''assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
assert spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
assert spiral_order([[1], [2], [3]]) == [1, 2, 3] and spiral_order([[1, 2, 3]]) == [1, 2, 3]
for m in range(1, 6):
    for n in range(1, 6):
        M = [[r * n + c for c in range(n)] for r in range(m)]
        got = spiral_order(M)
        assert sorted(got) == list(range(m * n)) and got[:n] == M[0]''',
    ),

    # ------------------------------------------------------------------ 73
    dict(
        id="set-matrix-zeroes",
        lc=73, slug="set-matrix-zeroes",
        name="Set Matrix Zeroes",
        difficulty="medium",
        framing=[
            "If a cell is 0, set its entire row and column to 0, in place. Zeroing as you scan is wrong &mdash; new zeros would trigger more zeroing &mdash; so first record which rows and columns to clear. The follow-up asks for O(1) extra space: store those records in the matrix itself.",
        ],
        approaches=[
            dict(
                name="Copy the matrix, read from the copy",
                time="O(m &middot; n &middot; (m + n))",
                space="O(m &middot; n)",
                tag="brute force",
                why=["For every zero in a copy of the original, clear its row and column in the real matrix. Reading from the copy prevents cascading; clearing a full row and column per zero is expensive."],
                code='''def set_zeroes(matrix):
    orig = [row[:] for row in matrix]
    m, n = len(matrix), len(matrix[0])
    for r in range(m):
        for c in range(n):
            if orig[r][c] == 0:
                for k in range(n):
                    matrix[r][k] = 0
                for k in range(m):
                    matrix[k][c] = 0''',
            ),
            dict(
                name="Row and column marker sets",
                time="O(m &middot; n)",
                space="O(m + n)",
                why=[
                    "One pass records which rows and which columns contain a zero; a second pass zeroes every cell whose row or column is marked. Linear time with m + n markers.",
                ],
                code='''def set_zeroes(matrix):
    rows, cols = set(), set()
    for r, row in enumerate(matrix):
        for c, v in enumerate(row):
            if v == 0:
                rows.add(r); cols.add(c)
    for r, row in enumerate(matrix):
        for c in range(len(row)):
            if r in rows or c in cols:
                row[c] = 0''',
            ),
            dict(
                name="Use the first row and column as the markers",
                time="O(m &middot; n)",
                space="O(1)",
                best=True,
                why=[
                    "Mark a zero at <code>(r, c)</code> by zeroing <code>matrix[r][0]</code> and <code>matrix[0][c]</code>. The first row and column now double as the marker arrays. Their own cells overlap at <code>matrix[0][0]</code>, so keep one extra flag for whether the first column itself must be cleared.",
                    "Order matters: clear the inner cells using the markers first, then the first row (from <code>matrix[0][0]</code>), and the first column last (from the flag) &mdash; otherwise the markers are destroyed before they are read.",
                ],
                code='''def set_zeroes(matrix):
    m, n = len(matrix), len(matrix[0])
    first_col_zero = any(matrix[r][0] == 0 for r in range(m))
    for r in range(m):
        for c in range(1, n):
            if matrix[r][c] == 0:
                matrix[r][0] = matrix[0][c] = 0
    for r in range(1, m):
        for c in range(1, n):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0
    if matrix[0][0] == 0:
        for c in range(n):
            matrix[0][c] = 0
    if first_col_zero:
        for r in range(m):
            matrix[r][0] = 0''',
            ),
        ],
        tests='''M = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]; set_zeroes(M); assert M == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
M = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]; set_zeroes(M); assert M == [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
rng = random.Random(2)
for _ in range(80):
    m, n = rng.randint(1, 5), rng.randint(1, 5)
    M = [[rng.choice([0, 1, 2, 3, 4]) for _ in range(n)] for _ in range(m)]
    rows = {r for r in range(m) if 0 in M[r]}
    cols = {c for c in range(n) if any(M[r][c] == 0 for r in range(m))}
    expect = [[0 if r in rows or c in cols else M[r][c] for c in range(n)] for r in range(m)]
    set_zeroes(M)
    assert M == expect''',
    ),

    # ------------------------------------------------------------------ 202
    dict(
        id="happy-number",
        lc=202, slug="happy-number",
        name="Happy Number",
        difficulty="easy",
        framing=[
            "Repeatedly replace n by the sum of the squares of its digits. It is happy if this reaches 1. Otherwise it loops forever &mdash; and detecting that loop is the problem. The sequence cannot grow without bound (a number with d digits maps to at most 81d), so it must eventually repeat.",
        ],
        approaches=[
            dict(
                name="Hash set of values seen",
                time="O(log n)",
                space="O(log n)",
                why=[
                    "Record each value; stop at 1 (happy) or at a repeat (a cycle not containing 1). The values quickly fall below 243 and stay there, so the set stays tiny.",
                ],
                code='''def is_happy(n):
    def step(x):
        return sum(int(d) ** 2 for d in str(x))

    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = step(n)
    return n == 1''',
            ),
            dict(
                name="Floyd's cycle detection",
                time="O(log n)",
                space="O(1)",
                best=True,
                why=[
                    "The sequence is a linked list defined by a function, so tortoise-and-hare finds the cycle with no memory: slow applies the step once, fast twice, until they meet. The number is happy exactly when they meet at 1 (1 maps to itself, a cycle of length one).",
                ],
                code='''def is_happy(n):
    def step(x):
        total = 0
        while x:
            x, d = divmod(x, 10)
            total += d * d
        return total

    slow, fast = n, step(n)
    while fast != 1 and slow != fast:
        slow = step(slow)
        fast = step(step(fast))
    return fast == 1''',
            ),
        ],
        tests='''assert is_happy(19) is True and is_happy(2) is False and is_happy(1) is True and is_happy(7) is True
happy_under_50 = {1, 7, 10, 13, 19, 23, 28, 31, 32, 44, 49}
for n in range(1, 50):
    assert is_happy(n) is (n in happy_under_50), n''',
    ),

    # ------------------------------------------------------------------ 66
    dict(
        id="plus-one",
        lc=66, slug="plus-one",
        name="Plus One",
        difficulty="easy",
        framing=[
            "A large integer is given as a list of digits; add one. The carry only propagates through trailing 9s, so in most cases one digit changes.",
        ],
        approaches=[
            dict(
                name="Convert to an integer and back",
                time="O(n)",
                space="O(n)",
                why=["Join the digits, add one, split again. Correct in Python; in fixed-width languages 100-digit numbers overflow, which is why the problem is phrased with digits."],
                code='''def plus_one(digits):
    return [int(d) for d in str(int("".join(map(str, digits))) + 1)]''',
            ),
            dict(
                name="Carry from the end",
                time="O(n)",
                space="O(1) (O(n) only for all 9s)",
                best=True,
                why=[
                    "Walk from the last digit: a digit below 9 is incremented and you are done; a 9 becomes 0 and the carry continues left. If the loop finishes, every digit was 9, and the answer is 1 followed by zeros.",
                    "Returns immediately in the common case &mdash; typically O(1) work.",
                ],
                code='''def plus_one(digits):
    digits = digits[:]
    for i in range(len(digits) - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0                          # 9 + 1: write 0, carry on
    return [1] + digits''',
            ),
        ],
        tests='''assert plus_one([1, 2, 3]) == [1, 2, 4] and plus_one([4, 3, 2, 1]) == [4, 3, 2, 2]
assert plus_one([9]) == [1, 0] and plus_one([9, 9, 9]) == [1, 0, 0, 0]
for x in range(0, 3000):
    assert plus_one([int(d) for d in str(x)]) == [int(d) for d in str(x + 1)]''',
    ),

    # ------------------------------------------------------------------ 13
    dict(
        id="roman-to-integer",
        lc=13, slug="roman-to-integer",
        name="Roman to Integer",
        difficulty="easy",
        framing=[
            "Convert a Roman numeral to an integer. Symbols normally add; a smaller symbol immediately <em>before</em> a larger one subtracts (IV = 4, CM = 900). One comparison with the next symbol decides the sign.",
        ],
        approaches=[
            dict(
                name="Match the two-letter pairs first",
                time="O(n)",
                space="O(1)",
                why=[
                    "List the six subtractive pairs (IV, IX, XL, XC, CD, CM) with their values; at each position, check for a pair first and consume two characters, otherwise consume one. Direct, but it enumerates special cases.",
                ],
                code='''def roman_to_int(s):
    pairs = {"IV": 4, "IX": 9, "XL": 40, "XC": 90, "CD": 400, "CM": 900}
    single = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    i = total = 0
    while i < len(s):
        if s[i:i + 2] in pairs:
            total += pairs[s[i:i + 2]]
            i += 2
        else:
            total += single[s[i]]
            i += 1
    return total''',
            ),
            dict(
                name="Subtract when smaller than the next symbol",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Add each symbol's value, unless it is smaller than the symbol after it, in which case subtract it. That single rule reproduces all six subtractive pairs without listing them.",
                ],
                code='''def roman_to_int(s):
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        v = val[ch]
        if i + 1 < len(s) and v < val[s[i + 1]]:
            total -= v                           # IV, IX, XL, ...
        else:
            total += v
    return total''',
            ),
        ],
        tests='''assert roman_to_int("III") == 3 and roman_to_int("LVIII") == 58 and roman_to_int("MCMXCIV") == 1994
def to_roman(n):
    out = ""
    for v, sym in [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                   (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= v:
            out += sym; n -= v
    return out
for n in range(1, 4000):
    assert roman_to_int(to_roman(n)) == n''',
    ),

    # ------------------------------------------------------------------ 50
    dict(
        id="pow-x-n",
        lc=50, slug="powx-n",
        name="Pow(x, n)",
        difficulty="medium",
        framing=[
            "Compute x<sup>n</sup> for integer n (possibly negative, up to 2<sup>31</sup> in magnitude). Multiplying n times is far too slow; <strong>exponentiation by squaring</strong> needs only O(log n) multiplications, because x<sup>n</sup> = (x<sup>n/2</sup>)<sup>2</sup>.",
        ],
        pitfall="Negating n in a fixed-width language: <code>-(-2<sup>31</sup>)</code> overflows a 32-bit int. Handle negative exponents by inverting x and using the magnitude in a wider type (Python has no such limit).",
        approaches=[
            dict(
                name="Multiply n times",
                time="O(n)",
                space="O(1)",
                tag="brute force",
                why=["Repeated multiplication. Two billion iterations for the largest exponent."],
                code='''def my_pow(x, n):
    if n < 0:
        x, n = 1 / x, -n
    result = 1.0
    for _ in range(n):
        result *= x
    return result''',
            ),
            dict(
                name="Recursive squaring",
                time="O(log n)",
                space="O(log n)",
                why=[
                    "x<sup>n</sup> = (x<sup>n//2</sup>)<sup>2</sup>, times one extra x when n is odd. Each call halves n, so there are O(log n) calls and multiplications.",
                ],
                code='''def my_pow(x, n):
    def go(n):
        if n == 0:
            return 1.0
        half = go(n // 2)
        return half * half * (x if n % 2 else 1)
    return go(n) if n >= 0 else 1 / go(-n)''',
            ),
            dict(
                name="Iterative binary exponentiation",
                time="O(log n)",
                space="O(1)",
                best=True,
                why=[
                    "Read n's bits from low to high while repeatedly squaring a base (x, x<sup>2</sup>, x<sup>4</sup>, &hellip;). Multiply the base into the result whenever the current bit is 1. This is how <code>pow(a, b, m)</code> and modular exponentiation in cryptography work.",
                ],
                code='''def my_pow(x, n):
    if n < 0:
        x, n = 1 / x, -n
    result = 1.0
    while n:
        if n & 1:
            result *= x
        x *= x                                 # x, x^2, x^4, x^8, ...
        n >>= 1
    return result''',
            ),
        ],
        tests='''assert abs(my_pow(2.0, 10) - 1024.0) < 1e-9
assert abs(my_pow(2.1, 3) - 9.261) < 1e-9
assert abs(my_pow(2.0, -2) - 0.25) < 1e-12
assert my_pow(1.0, 0) == 1.0
rng = random.Random(3)
for _ in range(200):
    x = rng.uniform(-2, 2) or 1.0
    n = rng.randint(-12, 12)
    assert math.isclose(my_pow(x, n), x ** n, rel_tol=1e-9, abs_tol=1e-12)''',
    ),

    # ------------------------------------------------------------------ 43
    dict(
        id="multiply-strings",
        lc=43, slug="multiply-strings",
        name="Multiply Strings",
        difficulty="medium",
        framing=[
            "Multiply two non-negative integers given as strings, without converting them to integers. Long multiplication, but with one clean observation: the product of digit i (from the right) of one number and digit j of the other contributes to position i + j of the result.",
        ],
        approaches=[
            dict(
                name="Schoolbook: add a shifted partial product per digit",
                time="O(m &middot; n + n&sup2;)",
                space="O(m + n)",
                why=[
                    "For each digit of the second number, multiply the whole first number by it (a partial product), shift by appending zeros, and add it to the running total with string addition. Exactly the pencil-and-paper method; the repeated string additions add overhead.",
                ],
                code='''def multiply(num1, num2):
    def add(a, b):
        i, j, carry, out = len(a) - 1, len(b) - 1, 0, []
        while i >= 0 or j >= 0 or carry:
            t = carry + (int(a[i]) if i >= 0 else 0) + (int(b[j]) if j >= 0 else 0)
            out.append(str(t % 10)); carry = t // 10; i -= 1; j -= 1
        return "".join(reversed(out))

    def times_digit(a, d):
        carry, out = 0, []
        for ch in reversed(a):
            t = int(ch) * d + carry
            out.append(str(t % 10)); carry = t // 10
        if carry:
            out.append(str(carry))
        return "".join(reversed(out))

    if num1 == "0" or num2 == "0":
        return "0"
    total = "0"
    for shift, ch in enumerate(reversed(num2)):
        total = add(total, times_digit(num1, int(ch)) + "0" * shift)
    return total''',
            ),
            dict(
                name="Position array: digit i &times; digit j goes to i + j",
                time="O(m &middot; n)",
                space="O(m + n)",
                best=True,
                why=[
                    "The product has at most m + n digits. Accumulate every digit product into <code>pos[i + j]</code> (indices counted from the right), then make one carry pass from the lowest position up. No intermediate strings, no repeated additions.",
                    "Strip leading zeros at the end (but keep a single 0 for a zero product).",
                ],
                code='''def multiply(num1, num2):
    m, n = len(num1), len(num2)
    pos = [0] * (m + n)
    for i, a in enumerate(reversed(num1)):
        for j, b in enumerate(reversed(num2)):
            pos[i + j] += int(a) * int(b)
    carry = 0
    for k in range(m + n):
        carry, pos[k] = divmod(pos[k] + carry, 10)
    out = "".join(map(str, reversed(pos))).lstrip("0")
    return out or "0"''',
            ),
        ],
        tests='''assert multiply("2", "3") == "6" and multiply("123", "456") == "56088" and multiply("0", "52") == "0"
rng = random.Random(4)
for _ in range(200):
    a, b = rng.randint(0, 10 ** rng.randint(1, 15)), rng.randint(0, 10 ** rng.randint(1, 15))
    assert multiply(str(a), str(b)) == str(a * b)''',
    ),

    # ------------------------------------------------------------------ 2013
    dict(
        id="detect-squares",
        lc=2013, slug="detect-squares",
        name="Detect Squares",
        difficulty="medium",
        framing=[
            "Points are added one by one (duplicates count separately). <code>count(q)</code> returns how many axis-aligned squares with positive area can be formed with q and three stored points. Fixing the diagonal corner determines the whole square, so iterate over stored points as candidate diagonal corners.",
        ],
        approaches=[
            dict(
                name="Try every triple of stored points",
                time="count O(N&sup3;)",
                space="O(N)",
                tag="brute force",
                why=["Check all ordered triples of stored points for a square with the query. Hopeless beyond a handful of points, but it pins down exactly what is being counted."],
                code='''class DetectSquares:
    def __init__(self):
        self.pts = []

    def add(self, point):
        self.pts.append(tuple(point))

    def count(self, point):
        qx, qy = point
        total = 0
        for (ax, ay) in self.pts:
            if ax == qx or ay == qy or abs(ax - qx) != abs(ay - qy):
                continue
            for (bx, by) in self.pts:
                if (bx, by) != (qx, ay):
                    continue
                for (cx, cy) in self.pts:
                    if (cx, cy) == (ax, qy):
                        total += 1
        return total''',
            ),
            dict(
                name="Counter of points, iterate diagonal corners",
                time="add O(1), count O(N)",
                space="O(N)",
                best=True,
                why=[
                    "Keep a counter of stored points. For each distinct stored point <code>(x, y)</code> that could be the diagonal opposite q &mdash; it must differ in both coordinates by the same non-zero amount &mdash; the other two corners are forced: <code>(x, qy)</code> and <code>(qx, y)</code>. The number of squares is the product of the three corners' multiplicities.",
                    "Iterating over distinct points (or only those sharing q's x-coordinate, with a per-x index) keeps count linear in the stored points.",
                ],
                code='''class DetectSquares:
    def __init__(self):
        self.cnt = Counter()

    def add(self, point):
        self.cnt[tuple(point)] += 1

    def count(self, point):
        qx, qy = point
        total = 0
        for (x, y), c in self.cnt.items():
            if x == qx or abs(x - qx) != abs(y - qy):
                continue                         # not a diagonal corner
            total += c * self.cnt[(x, qy)] * self.cnt[(qx, y)]
        return total''',
            ),
        ],
        tests='''ds = DetectSquares()
for p in ([3, 10], [11, 2], [3, 2]):
    ds.add(p)
assert ds.count([11, 10]) == 1 and ds.count([14, 8]) == 0
ds.add([11, 2])
assert ds.count([11, 10]) == 2
rng = random.Random(5)
for _ in range(20):
    ds, pts = DetectSquares(), []
    for _ in range(25):
        p = [rng.randint(0, 4), rng.randint(0, 4)]
        if rng.random() < 0.6:
            ds.add(p); pts.append(tuple(p))
        else:
            qx, qy = p
            brute = sum(1 for a in pts for b in pts for c in pts
                        if a[0] != qx and abs(a[0] - qx) == abs(a[1] - qy) and b == (qx, a[1]) and c == (a[0], qy))
            assert ds.count(p) == brute''',
    ),
    ],
),
    ],
)
