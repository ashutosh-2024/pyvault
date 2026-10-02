# -*- coding: utf-8 -*-
"""Bit Manipulation topic (NeetCode 250: Bit Manipulation). Same build
contract as content/dsa.py."""

PRELUDE_BITS = '''import random
from collections import Counter
'''


BITS_TOPIC = dict(
    id="bits",
    title="Bit Manipulation",
    prelude=PRELUDE_BITS,
    sections=[

dict(
    id="bits",
    title="Bits, masks and XOR",
    idea=[
        "Four identities carry most of this page: <code>x ^ x = 0</code> and <code>x ^ 0 = x</code> (XOR cancels pairs), <code>x &amp; (x - 1)</code> clears the lowest set bit, <code>x &amp; -x</code> isolates it, and <code>(x &gt;&gt; i) &amp; 1</code> reads bit i.",
        "Python integers are unbounded, so there is no natural 32-bit overflow and negative numbers have infinitely many leading 1s. Problems that assume 32-bit integers need an explicit mask, <code>0xFFFFFFFF</code>, and a conversion back to signed at the end.",
    ],
    problems=[

    # ------------------------------------------------------------------ 136
    dict(
        id="single-number",
        lc=136, slug="single-number",
        name="Single Number",
        difficulty="easy",
        framing=[
            "Every element appears twice except one. Find it in O(n) time and O(1) space. The constant-space requirement rules out counting; XOR's self-cancellation is the answer.",
        ],
        approaches=[
            dict(
                name="Count occurrences",
                time="O(n)",
                space="O(n)",
                why=["A Counter, then the value with count 1."],
                code='''def single_number(nums):
    return next(x for x, c in Counter(nums).items() if c == 1)''',
            ),
            dict(
                name="Sum trick: 2 &middot; sum(set) &minus; sum",
                time="O(n)",
                space="O(n)",
                why=[
                    "If every distinct value appeared twice, the total would be twice the sum of the distinct values; the shortfall is exactly the single value. Neat arithmetic, but the set still costs O(n).",
                ],
                code='''def single_number(nums):
    return 2 * sum(set(nums)) - sum(nums)''',
            ),
            dict(
                name="XOR everything",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "XOR is associative and commutative, so the order does not matter: all the pairs cancel to 0, and <code>0 ^ x = x</code> leaves the single value. One variable, one pass.",
                ],
                code='''def single_number(nums):
    result = 0
    for x in nums:
        result ^= x
    return result''',
            ),
        ],
        tests='''assert single_number([2, 2, 1]) == 1
assert single_number([4, 1, 2, 1, 2]) == 4
assert single_number([-7]) == -7
rng = random.Random(0)
for _ in range(50):
    vals = rng.sample(range(-50, 50), rng.randint(1, 8))
    nums = vals[1:] * 2 + [vals[0]]
    rng.shuffle(nums)
    assert single_number(nums) == vals[0]''',
    ),

    # ------------------------------------------------------------------ 191
    dict(
        id="number-of-1-bits",
        lc=191, slug="number-of-1-bits",
        name="Number of 1 Bits",
        difficulty="easy",
        framing=[
            "Count the set bits of a positive integer (the \"Hamming weight\"). The follow-up asks how to optimise if the function is called many times &mdash; the answer is Kernighan's trick, whose cost depends on the number of set bits, not the width.",
        ],
        approaches=[
            dict(
                name="Check each of the 32 bits",
                time="O(32)",
                space="O(1)",
                why=["Test the low bit and shift right, 32 times (or until the number is 0)."],
                code='''def hamming_weight(n):
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count''',
            ),
            dict(
                name="Kernighan: clear the lowest set bit",
                time="O(number of set bits)",
                space="O(1)",
                best=True,
                why=[
                    "Subtracting 1 flips the lowest set bit to 0 and every bit below it to 1; ANDing with the original clears exactly that lowest set bit. So <code>n &amp;= n - 1</code> runs once per set bit: 1 iteration for a power of two, not 32.",
                ],
                code='''def hamming_weight(n):
    count = 0
    while n:
        n &= n - 1                  # drop the lowest set bit
        count += 1
    return count''',
            ),
            dict(
                name="Built-in popcount",
                time="O(1) for word-sized ints",
                space="O(1)",
                tag="library",
                why=[
                    "<code>int.bit_count()</code> (Python 3.10+) compiles down to a hardware popcount instruction where available. Use it in real code; know the loops for the interview.",
                ],
                code='''def hamming_weight(n):
    return n.bit_count()''',
            ),
        ],
        tests='''assert hamming_weight(11) == 3 and hamming_weight(128) == 1 and hamming_weight(2147483645) == 30
for n in range(0, 3000):
    assert hamming_weight(n) == bin(n).count("1")''',
    ),

    # ------------------------------------------------------------------ 338
    dict(
        id="counting-bits",
        lc=338, slug="counting-bits",
        name="Counting Bits",
        difficulty="easy",
        framing=[
            "Return the popcount of every number from 0 to n. Popcounting each number independently is O(n log n); the follow-up asks for O(n), which comes from reusing an earlier answer &mdash; a tiny dynamic programme.",
        ],
        approaches=[
            dict(
                name="Popcount each number",
                time="O(n log n)",
                space="O(1) beyond output",
                why=["Kernighan's loop per number; each costs up to log n steps."],
                code='''def count_bits(n):
    out = []
    for i in range(n + 1):
        c = 0
        while i:
            i &= i - 1
            c += 1
        out.append(c)
    return out''',
            ),
            dict(
                name="DP on the shifted number",
                time="O(n)",
                space="O(1) beyond output",
                best=True,
                why=[
                    "<code>i &gt;&gt; 1</code> is i without its lowest bit, and it is smaller than i, so its answer is already known: <code>bits[i] = bits[i &gt;&gt; 1] + (i &amp; 1)</code>.",
                ],
                code='''def count_bits(n):
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits''',
            ),
            dict(
                name="DP on the lowest set bit",
                time="O(n)",
                space="O(1) beyond output",
                why=[
                    "<code>i &amp; (i - 1)</code> is i with its lowest set bit removed &mdash; also smaller, with exactly one fewer set bit: <code>bits[i] = bits[i &amp; (i - 1)] + 1</code>. An equally valid recurrence; knowing two shows you understand why the DP works.",
                ],
                code='''def count_bits(n):
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i & (i - 1)] + 1
    return bits''',
            ),
        ],
        tests='''assert count_bits(2) == [0, 1, 1]
assert count_bits(5) == [0, 1, 1, 2, 1, 2]
assert count_bits(0) == [0]
assert count_bits(1000) == [bin(i).count("1") for i in range(1001)]''',
    ),

    # ------------------------------------------------------------------ 67
    dict(
        id="add-binary",
        lc=67, slug="add-binary",
        name="Add Binary",
        difficulty="easy",
        framing=[
            "Add two binary strings. The inputs can be 10<sup>4</sup> digits long &mdash; far beyond 64-bit integers in most languages &mdash; so the real exercise is grade-school addition with a carry, from the right.",
        ],
        approaches=[
            dict(
                name="Convert to integers",
                time="O(n + m)",
                space="O(n + m)",
                why=[
                    "<code>bin(int(a, 2) + int(b, 2))[2:]</code>. Correct in Python thanks to arbitrary-precision integers; in Java or C++ it overflows, which is the point of the problem. Mention it, then write the loop.",
                ],
                code='''def add_binary(a, b):
    return bin(int(a, 2) + int(b, 2))[2:]''',
            ),
            dict(
                name="Digit by digit with a carry",
                time="O(max(n, m))",
                space="O(max(n, m))",
                best=True,
                why=[
                    "Walk both strings from the right, adding the two bits and the carry: the result bit is <code>total % 2</code> and the carry is <code>total // 2</code>. Keep going while either string has digits or a carry remains, collect bits in a list, and reverse once at the end.",
                ],
                code='''def add_binary(a, b):
    i, j, carry, out = len(a) - 1, len(b) - 1, 0, []
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i]); i -= 1
        if j >= 0:
            total += int(b[j]); j -= 1
        out.append(str(total % 2))
        carry = total // 2
    return "".join(reversed(out))''',
            ),
        ],
        tests='''assert add_binary("11", "1") == "100"
assert add_binary("1010", "1011") == "10101"
assert add_binary("0", "0") == "0"
rng = random.Random(1)
for _ in range(60):
    x, y = rng.randint(0, 10 ** 6), rng.randint(0, 10 ** 6)
    assert add_binary(bin(x)[2:], bin(y)[2:]) == bin(x + y)[2:]''',
    ),

    # ------------------------------------------------------------------ 190
    dict(
        id="reverse-bits",
        lc=190, slug="reverse-bits",
        name="Reverse Bits",
        difficulty="easy",
        framing=[
            "Reverse the 32 bits of an unsigned integer (bit 0 becomes bit 31). Note it is always 32 bits, including leading zeros &mdash; <code>1</code> becomes <code>2<sup>31</sup></code>. The follow-up, for repeated calls, leads to the mask-swapping and lookup-table versions.",
        ],
        approaches=[
            dict(
                name="String reversal",
                time="O(32)",
                space="O(32)",
                why=["Format as a 32-character binary string, reverse it, parse it back. Short, and it makes the \"always 32 bits\" rule explicit."],
                code='''def reverse_bits(n):
    return int(format(n, "032b")[::-1], 2)''',
            ),
            dict(
                name="Shift bits out one at a time",
                time="O(32)",
                space="O(1)",
                best=True,
                why=[
                    "32 times: shift the result left, OR in n's lowest bit, shift n right. The first bit read is the last bit written, which is the reversal.",
                ],
                code='''def reverse_bits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result''',
            ),
            dict(
                name="Divide and conquer with masks",
                time="O(log 32) = 5 steps",
                space="O(1)",
                tag="no loop",
                why=[
                    "Swap the two 16-bit halves, then the 8-bit halves within each, then 4, 2 and 1, each in one expression using a mask that selects alternating blocks. Five constant-time steps, no branches &mdash; the version used in systems code.",
                ],
                code='''def reverse_bits(n):
    n = (n >> 16) | ((n & 0xFFFF) << 16)
    n = ((n & 0xFF00FF00) >> 8) | ((n & 0x00FF00FF) << 8)
    n = ((n & 0xF0F0F0F0) >> 4) | ((n & 0x0F0F0F0F) << 4)
    n = ((n & 0xCCCCCCCC) >> 2) | ((n & 0x33333333) << 2)
    n = ((n & 0xAAAAAAAA) >> 1) | ((n & 0x55555555) << 1)
    return n''',
            ),
        ],
        tests='''assert reverse_bits(43261596) == 964176192
assert reverse_bits(4294967293) == 3221225471
assert reverse_bits(1) == 2 ** 31 and reverse_bits(0) == 0
rng = random.Random(2)
for _ in range(200):
    x = rng.getrandbits(32)
    assert reverse_bits(x) == int(format(x, "032b")[::-1], 2)''',
    ),

    # ------------------------------------------------------------------ 268
    dict(
        id="missing-number",
        lc=268, slug="missing-number",
        name="Missing Number",
        difficulty="easy",
        framing=[
            "n distinct numbers from <code>[0, n]</code>; one is missing. Find it in O(n) time and O(1) space. Four solutions, and the last two are the ones interviewers look for.",
        ],
        approaches=[
            dict(
                name="Sort, find the gap",
                time="O(n log n)",
                space="O(1)&ndash;O(n)",
                why=["After sorting, the first index i where <code>nums[i] != i</code> is the answer (or n if none)."],
                code='''def missing_number(nums):
    for i, x in enumerate(sorted(nums)):
        if x != i:
            return i
    return len(nums)''',
            ),
            dict(
                name="Hash set",
                time="O(n)",
                space="O(n)",
                why=["Put everything in a set and test 0..n."],
                code='''def missing_number(nums):
    present = set(nums)
    return next(i for i in range(len(nums) + 1) if i not in present)''',
            ),
            dict(
                name="Gauss's sum",
                time="O(n)",
                space="O(1)",
                why=[
                    "0 + 1 + &hellip; + n = n(n+1)/2; subtract the actual sum. In fixed-width languages the sum can overflow for large n (the XOR version cannot).",
                ],
                code='''def missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)''',
            ),
            dict(
                name="XOR indices with values",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "XOR together every index 0..n and every value. Each present number appears twice (once as an index, once as a value) and cancels; the missing one appears only as an index and survives. No arithmetic that can overflow.",
                ],
                code='''def missing_number(nums):
    result = len(nums)
    for i, x in enumerate(nums):
        result ^= i ^ x
    return result''',
            ),
        ],
        tests='''assert missing_number([3, 0, 1]) == 2
assert missing_number([0, 1]) == 2
assert missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8
rng = random.Random(3)
for _ in range(50):
    n = rng.randint(1, 20)
    miss = rng.randint(0, n)
    nums = [v for v in range(n + 1) if v != miss]
    rng.shuffle(nums)
    assert missing_number(nums) == miss''',
    ),

    # ------------------------------------------------------------------ 371
    dict(
        id="sum-of-two-integers",
        lc=371, slug="sum-of-two-integers",
        name="Sum of Two Integers",
        difficulty="medium",
        framing=[
            "Add two 32-bit integers without <code>+</code> or <code>-</code>. XOR adds bits without carrying; AND finds where carries happen; shifting the carries left and adding again repeats until there are none. In Python you must also emulate 32-bit wrap-around, or negative numbers loop forever.",
        ],
        pitfall="Running the XOR/carry loop on raw Python integers. With a negative operand, the carry keeps shifting left into ever-higher bits forever, because Python integers have no fixed width. Mask to 32 bits on every step.",
        approaches=[
            dict(
                name="Full adder, one bit at a time",
                time="O(32)",
                space="O(1)",
                why=[
                    "Simulate the hardware: for each of the 32 bit positions, the sum bit is <code>a ^ b ^ carry</code> and the new carry is the majority of the three. Then reinterpret the 32-bit result as signed.",
                ],
                code='''def get_sum(a, b):
    result, carry = 0, 0
    for i in range(32):
        x, y = (a >> i) & 1, (b >> i) & 1
        result |= (x ^ y ^ carry) << i
        carry = (x & y) | (x & carry) | (y & carry)
    return result - (1 << 32) if result >> 31 else result      # to signed''',
            ),
            dict(
                name="XOR and carry loop with a 32-bit mask",
                time="O(32)",
                space="O(1)",
                best=True,
                why=[
                    "<code>a ^ b</code> is the sum ignoring carries; <code>(a &amp; b) &lt;&lt; 1</code> is the carries, shifted to where they apply. Replace (a, b) with those two and repeat until the carry is zero &mdash; at most 32 rounds, since each round the carries move at least one bit left.",
                    "Masking with <code>0xFFFFFFFF</code> after each step emulates 32-bit wrap-around. At the end, a value with bit 31 set represents a negative number; <code>~(a ^ MASK)</code> converts it back to Python's signed form.",
                ],
                code='''def get_sum(a, b):
    MASK = 0xFFFFFFFF
    a, b = a & MASK, b & MASK
    while b:
        a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK
    return a if a <= 0x7FFFFFFF else ~(a ^ MASK)''',
            ),
        ],
        tests='''assert get_sum(1, 2) == 3 and get_sum(2, 3) == 5
assert get_sum(-1, 1) == 0 and get_sum(-5, -7) == -12
rng = random.Random(4)
for _ in range(300):
    a, b = rng.randint(-1000, 1000), rng.randint(-1000, 1000)
    assert get_sum(a, b) == a + b''',
    ),

    # ------------------------------------------------------------------ 7
    dict(
        id="reverse-integer",
        lc=7, slug="reverse-integer",
        name="Reverse Integer",
        difficulty="medium",
        framing=[
            "Reverse the digits of a signed 32-bit integer; return 0 if the result overflows 32 bits. You are to assume the environment <em>cannot</em> store 64-bit integers, so the overflow must be detected before it happens, not after.",
        ],
        approaches=[
            dict(
                name="String reversal, range check",
                time="O(digits)",
                space="O(digits)",
                why=[
                    "Reverse the digits as a string, restore the sign, compare with the 32-bit range. Simple, but it checks the range <em>after</em> building a number that may not fit &mdash; which the problem's rule forbids in spirit.",
                ],
                code='''def reverse(x):
    sign = -1 if x < 0 else 1
    r = sign * int(str(abs(x))[::-1])
    return r if -2 ** 31 <= r <= 2 ** 31 - 1 else 0''',
            ),
            dict(
                name="Pop and push digits, check before overflowing",
                time="O(digits)",
                space="O(1)",
                best=True,
                why=[
                    "Pop the last digit with <code>% 10</code> and push it onto the result with <code>result * 10 + digit</code>. Before pushing, check that <code>result * 10 + digit</code> will stay within 2<sup>31</sup> - 1 by comparing <code>result</code> with <code>(LIMIT - digit) // 10</code> &mdash; a test that never forms the overflowing value.",
                    "Working on the absolute value and restoring the sign at the end sidesteps Python's floor-division behaviour on negatives. The negative limit is one larger in magnitude, so it gets its own bound.",
                ],
                code='''def reverse(x):
    limit = 2 ** 31 - 1 if x >= 0 else 2 ** 31     # |INT_MIN| = 2^31
    n, result = abs(x), 0
    while n:
        n, digit = divmod(n, 10)
        if result > (limit - digit) // 10:
            return 0                               # would overflow
        result = result * 10 + digit
    return result if x >= 0 else -result''',
            ),
        ],
        tests='''assert reverse(123) == 321 and reverse(-123) == -321 and reverse(120) == 21 and reverse(0) == 0
assert reverse(1534236469) == 0 and reverse(-2147483648) == 0
assert reverse(1463847412) == 2147483641
rng = random.Random(5)
for _ in range(300):
    x = rng.randint(-2 ** 31, 2 ** 31 - 1)
    s = -1 if x < 0 else 1
    r = s * int(str(abs(x))[::-1])
    assert reverse(x) == (r if -2 ** 31 <= r <= 2 ** 31 - 1 else 0)''',
    ),

    # ------------------------------------------------------------------ 201
    dict(
        id="bitwise-and-range",
        lc=201, slug="bitwise-and-of-numbers-range",
        name="Bitwise AND of Numbers Range",
        difficulty="medium",
        framing=[
            "AND together every integer in <code>[left, right]</code>. The range can hold two billion numbers, so looping is out. The insight: any bit below the common binary prefix of <code>left</code> and <code>right</code> flips somewhere in the range and becomes 0; the common prefix survives.",
        ],
        approaches=[
            dict(
                name="AND every number",
                time="O(right - left)",
                space="O(1)",
                tag="brute force",
                why=[
                    "Loop and AND. Early exit once the result is 0 helps on many inputs, but a narrow range of huge numbers still costs up to 2<sup>31</sup> steps.",
                ],
                code='''def range_bitwise_and(left, right):
    result = left
    for x in range(left + 1, right + 1):
        result &= x
        if result == 0:
            break
    return result''',
            ),
            dict(
                name="Shift both until they match",
                time="O(32)",
                space="O(1)",
                best=True,
                why=[
                    "Shift both numbers right until they are equal, counting the shifts. What remains is their common prefix; shift it back left. Every bit that was shifted off differs somewhere within the range, so it is 0 in the AND.",
                ],
                code='''def range_bitwise_and(left, right):
    shift = 0
    while left != right:
        left, right = left >> 1, right >> 1
        shift += 1
    return left << shift''',
            ),
            dict(
                name="Clear right's lowest bits until it drops to left",
                time="O(set bits)",
                space="O(1)",
                why=[
                    "Repeatedly clear <code>right</code>'s lowest set bit with Kernighan's trick while it is still greater than <code>left</code>. Each cleared bit is a bit that varies within the range. Stops as soon as <code>right &le; left</code>, leaving the common prefix.",
                ],
                code='''def range_bitwise_and(left, right):
    while right > left:
        right &= right - 1
    return right''',
            ),
        ],
        tests='''assert range_bitwise_and(5, 7) == 4 and range_bitwise_and(0, 0) == 0
assert range_bitwise_and(1, 2147483647) == 0
rng = random.Random(6)
for _ in range(200):
    a = rng.randint(0, 5000); b = a + rng.randint(0, 300)
    r = a
    for x in range(a + 1, b + 1):
        r &= x
    assert range_bitwise_and(a, b) == r''',
    ),

    # ------------------------------------------------------------------ 3133
    dict(
        id="minimum-array-end",
        lc=3133, slug="minimum-array-end",
        name="Minimum Array End",
        difficulty="medium",
        framing=[
            "Build a strictly increasing array of n positive integers whose AND is exactly <code>x</code>, minimising the last element. Every element must contain all of x's bits, so each element is x with some extra bits switched on in x's <em>zero</em> positions. The i-th smallest such number is found by writing i in binary into those free positions.",
        ],
        approaches=[
            dict(
                name="Step to the next superset of x, n - 1 times",
                time="O(n)",
                space="O(1)",
                why=[
                    "Start at x. The next number containing all of x's bits is <code>(cur + 1) | x</code>: increment, then force x's bits back on (if the increment carried through them, OR-ing restores them and the result is still larger). Repeat n - 1 times. Linear in n, which reaches 10<sup>8</sup>.",
                ],
                code='''def min_end(n, x):
    cur = x
    for _ in range(n - 1):
        cur = (cur + 1) | x
    return cur''',
            ),
            dict(
                name="Deposit the bits of n - 1 into x's zero bits",
                time="O(log n + log x)",
                space="O(1)",
                best=True,
                why=[
                    "The valid numbers, in increasing order, are exactly x with the free (zero) bit positions filled by the binary counter 0, 1, 2, &hellip;. The n-th of them uses counter value n - 1. So walk x's bits from low to high; at each zero position, copy the next bit of n - 1 into it.",
                    "This is the \"parallel bit deposit\" (PDEP) operation. Positions beyond x's highest bit are all free, so the loop simply continues until n - 1 runs out of bits.",
                ],
                code='''def min_end(n, x):
    k, result, bit = n - 1, x, 1
    while k:
        if not x & bit:                      # a free position
            if k & 1:
                result |= bit
            k >>= 1
        bit <<= 1
    return result''',
            ),
        ],
        tests='''assert min_end(3, 4) == 6 and min_end(2, 7) == 15 and min_end(1, 5) == 5
rng = random.Random(7)
for _ in range(200):
    n, x = rng.randint(1, 60), rng.randint(1, 200)
    cur = x
    for _ in range(n - 1):
        cur += 1
        while cur & x != x:
            cur += 1
    assert min_end(n, x) == cur''',
    ),
    ],
),
    ],
)
