"""Write-ups for the Bit Manipulation topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ single number
    "single-number": {
        "example": {"call": "single_number([4, 1, 2, 1, 2])", "expect": "4"},
        "approaches": {
            "Count occurrences": {
                "idea": [
                    "Count how often each value appears; the answer is the only value with count 1.",
                ],
                "steps": [
                    "Build <code>Counter(nums)</code>.",
                    "Return the key whose count is 1.",
                ],
                "why": [
                    "Every other value appears exactly twice, so exactly one key has count 1.",
                    "It is O(n) time but O(n) space for the counter, which breaks the O(1)-space requirement.",
                ],
                "dry": [
                    "Counts: {4: 1, 1: 2, 2: 2}.",
                    "The only value with count 1 is <strong>4</strong>.",
                ],
            },
            "Sum trick: 2 &middot; sum(set) &minus; sum": {
                "idea": [
                    "If every distinct value appeared twice, the total would be exactly twice the sum of the distinct values.",
                    "The single value is counted once instead of twice, so the shortfall equals that value.",
                ],
                "steps": [
                    "Compute <code>2 * sum(set(nums))</code>.",
                    "Subtract <code>sum(nums)</code>.",
                ],
                "why": [
                    "2·(sum of distinct values) - (actual sum) = the one value missing its second copy.",
                    "It is O(n) time, but the set is O(n) space.",
                ],
                "dry": [
                    "set(nums) = {1, 2, 4}, sum 7, doubled 14.",
                    "sum(nums) = 4 + 1 + 2 + 1 + 2 = 10.",
                    "14 - 10 = <strong>4</strong>.",
                ],
            },
            "XOR everything": {
                "idea": [
                    "XOR has three useful properties: <code>x ^ x = 0</code>, <code>x ^ 0 = x</code>, and the order of operations does not matter.",
                    "XOR all numbers together: every pair cancels to 0, wherever its two copies sit, and only the single value is left.",
                ],
                "steps": [
                    "<code>result = 0</code>.",
                    "For each x: <code>result ^= x</code>.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "Because XOR is associative and commutative, the total equals (pairs XORed together) ^ single = 0 ^ single.",
                    "One pass and one variable: O(n) time, O(1) space.",
                ],
                "dry": [
                    "0 ^ 4 = 4 (100).",
                    "4 ^ 1 = 5 (101). 5 ^ 2 = 7 (111).",
                    "7 ^ 1 = 6 (110): the first 1 cancels. 6 ^ 2 = 4 (100): the 2 cancels.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ number of 1 bits
    "number-of-1-bits": {
        "example": {"call": "hamming_weight(44)", "expect": "3"},
        "approaches": {
            "Check each of the 32 bits": {
                "idea": [
                    "Look at the lowest bit with <code>n &amp; 1</code>, count it, then shift n right to bring the next bit down.",
                    "Stop when n becomes 0, since no set bits remain.",
                ],
                "steps": [
                    "While n is non-zero: <code>count += n &amp; 1</code>, then <code>n &gt;&gt;= 1</code>.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Every bit passes through position 0 exactly once.",
                    "It takes one iteration per bit up to the highest set bit (at most 32): O(32) time, O(1) space.",
                ],
                "dry": [
                    "44 is 101100 in binary.",
                    "The low bits read in order are 0, 0, 1, 1, 0, 1 as n goes 44 → 22 → 11 → 5 → 2 → 1 → 0.",
                    "Six iterations, three of them adding 1: the result is <strong>3</strong>.",
                ],
            },
            "Kernighan: clear the lowest set bit": {
                "idea": [
                    "<code>n - 1</code> flips the lowest set bit to 0 and every 0 below it to 1.",
                    "So <code>n &amp; (n - 1)</code> is n with exactly its lowest set bit removed.",
                    "Repeat until n is 0 and count the repetitions: one per set bit, skipping the zeros entirely.",
                ],
                "steps": [
                    "While n is non-zero: <code>n &amp;= n - 1</code>, then <code>count += 1</code>.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Each iteration removes exactly one set bit.",
                    "It runs once per set bit, so a power of two takes one step instead of 32. Space is O(1).",
                ],
                "dry": [
                    "n = 101100. n - 1 = 101011, AND gives 101000: count 1.",
                    "n = 101000. n - 1 = 100111, AND gives 100000: count 2.",
                    "n = 100000. n - 1 = 011111, AND gives 0: count 3.",
                    "Three iterations for three set bits: <strong>3</strong>.",
                ],
            },
            "Built-in popcount": {
                "idea": [
                    "Python 3.10+ has <code>int.bit_count()</code>, which counts set bits directly, often with a single hardware instruction.",
                ],
                "steps": [
                    "Return <code>n.bit_count()</code>.",
                ],
                "why": [
                    "It is the library's own popcount: O(1) for word-sized integers.",
                    "Use it in real code, and know the loops for interviews that forbid it.",
                ],
                "dry": [
                    "<code>(44).bit_count()</code> counts the 1s in 101100.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ counting bits
    "counting-bits": {
        "example": {"call": "count_bits(8)", "expect": "[0, 1, 1, 2, 1, 2, 2, 3, 1]"},
        "approaches": {
            "Popcount each number": {
                "idea": [
                    "Count the bits of each number from 0 to n independently, using Kernighan's loop.",
                ],
                "steps": [
                    "For each i: repeat <code>i &amp;= i - 1</code>, counting, until i is 0.",
                    "Append the count.",
                ],
                "why": [
                    "Each count is correct on its own.",
                    "Each number takes up to log n steps: O(n log n) time and O(1) extra space.",
                ],
                "dry": [
                    "0 → 0. 1 → 1 step. 2 (10) → 1. 3 (11) → 2. 4 (100) → 1.",
                    "5 (101) → 2. 6 (110) → 2. 7 (111) → 3 steps. 8 (1000) → 1.",
                    "The result is <strong>[0, 1, 1, 2, 1, 2, 2, 3, 1]</strong>.",
                ],
            },
            "DP on the shifted number": {
                "idea": [
                    "<code>i &gt;&gt; 1</code> is i with its lowest bit dropped, and it is smaller than i, so its count is already known.",
                    "So the count for i is the count for <code>i &gt;&gt; 1</code> plus whether i's lowest bit is set.",
                ],
                "steps": [
                    "<code>bits[0] = 0</code>.",
                    "For i from 1 to n: <code>bits[i] = bits[i &gt;&gt; 1] + (i &amp; 1)</code>.",
                ],
                "why": [
                    "Shifting right keeps every bit except the lowest, so the counts differ by exactly <code>i &amp; 1</code>.",
                    "It is O(1) per number: O(n) time.",
                ],
                "dry": [
                    "i=1: bits[0] + 1 = 1. i=2: bits[1] + 0 = 1. i=3: bits[1] + 1 = 2.",
                    "i=4: bits[2] + 0 = 1. i=5: bits[2] + 1 = 2. i=6: bits[3] + 0 = 2.",
                    "i=7: bits[3] + 1 = 3. i=8: bits[4] + 0 = 1.",
                    "The result is <strong>[0, 1, 1, 2, 1, 2, 2, 3, 1]</strong>.",
                ],
            },
            "DP on the lowest set bit": {
                "idea": [
                    "<code>i &amp; (i - 1)</code> is i with its lowest set bit removed: a smaller number with exactly one fewer set bit.",
                    "So <code>bits[i] = bits[i &amp; (i - 1)] + 1</code>.",
                ],
                "steps": [
                    "For i from 1 to n: <code>bits[i] = bits[i &amp; (i - 1)] + 1</code>.",
                ],
                "why": [
                    "The referenced entry is smaller than i, so it was already computed.",
                    "It is O(n) time; knowing both recurrences shows you understand why the DP works.",
                ],
                "dry": [
                    "i=1: 1 &amp; 0 = 0, so 0 + 1 = 1. i=2: 2 &amp; 1 = 0, so 1. i=3: 3 &amp; 2 = 2, so bits[2] + 1 = 2.",
                    "i=4: 0, so 1. i=5: 5 &amp; 4 = 4, so 2. i=6: 6 &amp; 5 = 4, so 2.",
                    "i=7: 7 &amp; 6 = 6, so bits[6] + 1 = 3. i=8: 0, so 1.",
                    "The result is <strong>[0, 1, 1, 2, 1, 2, 2, 3, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add binary
    "add-binary": {
        "example": {"call": 'add_binary("1011", "111")', "expect": '"10010"'},
        "approaches": {
            "Convert to integers": {
                "idea": [
                    "Parse both strings as base-2 integers, add them, and format the sum back to binary.",
                    "It works in Python because integers have no size limit; in Java or C++ long inputs would overflow, which is the point of the problem.",
                ],
                "steps": [
                    "<code>int(a, 2) + int(b, 2)</code>.",
                    "<code>bin(...)[2:]</code> strips the <code>0b</code> prefix.",
                ],
                "why": [
                    "Parsing, adding and formatting are each linear in the length: O(n + m).",
                ],
                "dry": [
                    "\"1011\" is 11 and \"111\" is 7.",
                    "11 + 7 = 18, and bin(18) = \"0b10010\".",
                    "The result is <strong>\"10010\"</strong>.",
                ],
            },
            "Digit by digit with a carry": {
                "idea": [
                    "Do grade-school addition in base 2, from the rightmost digit to the left.",
                    "At each position, add the two digits (missing digits count as 0) and the carry: the result digit is <code>total % 2</code> and the new carry is <code>total // 2</code>.",
                    "Keep going while either string has digits left or a carry remains.",
                ],
                "steps": [
                    "<code>i</code> and <code>j</code> point at the last digit of each string; <code>carry = 0</code>.",
                    "Each round: add the available digits and the carry, append <code>total % 2</code>, set <code>carry = total // 2</code>.",
                    "Reverse the collected digits at the end.",
                ],
                "why": [
                    "This is exactly how addition works, with 2 in place of 10.",
                    "There is one round per output digit: O(max(n, m)) time and space.",
                ],
                "dry": [
                    "Rightmost digits 1 + 1 = 2: write 0, carry 1.",
                    "Next: 1 + 1 + carry 1 = 3: write 1, carry 1.",
                    "Next: 0 + 1 + 1 = 2: write 0, carry 1.",
                    "Next: only a's 1 is left, 1 + 1 = 2: write 0, carry 1.",
                    "Only the carry is left: write 1. The digits collected are 0, 1, 0, 0, 1; reversed: <strong>\"10010\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse bits
    "reverse-bits": {
        "example": {"call": "reverse_bits(43261596)", "expect": "964176192"},
        "approaches": {
            "String reversal": {
                "idea": [
                    "Write the number as exactly 32 binary digits, including leading zeros, reverse the string, and parse it back.",
                    "The fixed width matters: leading zeros become trailing zeros, and the other way round.",
                ],
                "steps": [
                    "<code>format(n, \"032b\")</code>.",
                    "Reverse with <code>[::-1]</code> and parse with <code>int(..., 2)</code>.",
                ],
                "why": [
                    "Bit i of the input ends up at position 31 - i.",
                    "It is O(32) time and space.",
                ],
                "dry": [
                    "43261596 is 00000010100101000001111010011100.",
                    "Reversed: 00111001011110000010100101000000.",
                    "That is <strong>964176192</strong>.",
                ],
            },
            "Shift bits out one at a time": {
                "idea": [
                    "Read n's bits from the lowest up, and write them into the result from the highest down.",
                    "Each step shifts the result left to make room, ORs in n's lowest bit, and shifts n right.",
                    "After 32 steps, the first bit read sits at the top: the order is reversed.",
                ],
                "steps": [
                    "Repeat 32 times: <code>result = (result &lt;&lt; 1) | (n &amp; 1)</code>, then <code>n &gt;&gt;= 1</code>.",
                ],
                "why": [
                    "The bit read at step k ends up shifted left 31 - k more times, landing at position 31 - k.",
                    "It is exactly 32 iterations, O(1) space.",
                ],
                "dry": [
                    "n's lowest 8 bits are 10011100, read from the right as 0, 0, 1, 1, 1, 0, 0, 1.",
                    "result after each of those steps: 0, 0, 1, 3 (11), 7 (111), 14 (1110), 28 (11100), 57 (111001).",
                    "The remaining 24 bits continue the same way.",
                    "After 32 steps the result is <strong>964176192</strong>.",
                ],
            },
            "Divide and conquer with masks": {
                "idea": [
                    "Reversing 32 bits is the same as swapping the two 16-bit halves, then the two 8-bit halves within each, then 4, 2 and 1.",
                    "Each swap level is one expression: mask out alternating blocks, shift one group right and the other left, and OR them together.",
                    "Five branch-free steps, the classic systems-programming trick.",
                ],
                "steps": [
                    "Swap the 16-bit halves: <code>(n &gt;&gt; 16) | ((n &amp; 0xFFFF) &lt;&lt; 16)</code>.",
                    "Swap adjacent bytes with masks <code>0xFF00FF00</code> / <code>0x00FF00FF</code>.",
                    "Then nibbles (<code>0xF0F0F0F0</code>), bit pairs (<code>0xCCCCCCCC</code>) and single bits (<code>0xAAAAAAAA</code>).",
                ],
                "why": [
                    "After swapping at every scale, each bit has moved to its mirror position.",
                    "There are five constant-time steps, whatever the input.",
                ],
                "dry": [
                    "Start: 00000010100101000001111010011100.",
                    "Halves swapped: 00011110100111000000001010010100.",
                    "Bytes swapped: 10011100000111101001010000000010. Nibbles: 11001001111000010100100100100000.",
                    "Pairs: 00110110101101000001011010000000. Single bits: 00111001011110000010100101000000.",
                    "That is <strong>964176192</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ missing number
    "missing-number": {
        "example": {"call": "missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1])", "expect": "8"},
        "approaches": {
            "Sort, find the gap": {
                "idea": [
                    "After sorting, a complete range would satisfy <code>nums[i] == i</code> everywhere.",
                    "The first index where that fails is the missing number; if none fails, n itself is missing.",
                ],
                "steps": [
                    "Sort the array.",
                    "Return the first i with <code>sorted[i] != i</code>, otherwise <code>len(nums)</code>.",
                ],
                "why": [
                    "Everything before the gap lines up, and the gap is exactly where a value is skipped.",
                    "It costs O(n log n) for the sort.",
                ],
                "dry": [
                    "Sorted: [0, 1, 2, 3, 4, 5, 6, 7, 9].",
                    "Indices 0..7 match their values.",
                    "Index 8 holds 9, so the result is <strong>8</strong>.",
                ],
            },
            "Hash set": {
                "idea": [
                    "Put all values in a set, then test 0, 1, 2, … in order; the first one missing is the answer.",
                ],
                "steps": [
                    "<code>present = set(nums)</code>.",
                    "Return the first i in <code>range(n + 1)</code> not in <code>present</code>.",
                ],
                "why": [
                    "Exactly one number in 0..n is absent.",
                    "It is O(n) time and O(n) space.",
                ],
                "dry": [
                    "present = {0, 1, 2, 3, 4, 5, 6, 7, 9}.",
                    "0 through 7 are found, and 8 is not.",
                    "The result is <strong>8</strong>.",
                ],
            },
            "Gauss's sum": {
                "idea": [
                    "The numbers 0..n add up to <code>n(n+1)/2</code>.",
                    "The array holds all of them except one, so the difference between the expected and actual sums is the missing number.",
                ],
                "steps": [
                    "<code>n = len(nums)</code>.",
                    "Return <code>n·(n+1)//2 - sum(nums)</code>.",
                ],
                "why": [
                    "Every present number cancels, and the missing one remains.",
                    "It is O(n) time and O(1) space; in fixed-width languages the sum can overflow for very large n.",
                ],
                "dry": [
                    "n = 9, so the expected sum is 9·10/2 = 45.",
                    "The actual sum is 9 + 6 + 4 + 2 + 3 + 5 + 7 + 0 + 1 = 37.",
                    "45 - 37 = <strong>8</strong>.",
                ],
            },
            "XOR indices with values": {
                "idea": [
                    "XOR together every index 0..n and every value in the array.",
                    "Each present number appears twice (once as an index, once as a value) and cancels; the missing number appears only as an index and survives.",
                    "There is no addition, so nothing can overflow.",
                ],
                "steps": [
                    "Start with <code>result = n</code>, because index n is not produced by <code>enumerate</code>.",
                    "For each i, x: <code>result ^= i ^ x</code>.",
                ],
                "why": [
                    "<code>x ^ x = 0</code> and XOR's order does not matter, so all pairs vanish.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "Indices XORed: 0 ^ 1 ^ … ^ 9, starting from result = 9 and adding 0..8 from <code>enumerate</code>.",
                    "Values XORed: 9 ^ 6 ^ 4 ^ 2 ^ 3 ^ 5 ^ 7 ^ 0 ^ 1.",
                    "Every number except 8 appears once on each side and cancels.",
                    "The result is <strong>8</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sum of two integers
    "sum-of-two-integers": {
        "example": {"call": "get_sum(5, -3)", "expect": "2"},
        "approaches": {
            "Full adder, one bit at a time": {
                "idea": [
                    "Simulate the adder circuit in a CPU: process the 32 bit positions from low to high, carrying as you go.",
                    "The sum bit is <code>x ^ y ^ carry</code>; the new carry is 1 when at least two of the three bits are 1.",
                    "Negative numbers in two's complement just work, and the 32-bit result is converted back to Python's signed integers at the end.",
                ],
                "steps": [
                    "For i in 0..31: read bit i of a and b with <code>(a &gt;&gt; i) &amp; 1</code>.",
                    "Set result bit i to <code>x ^ y ^ carry</code> and update <code>carry</code> to the majority of the three.",
                    "If bit 31 of the result is set, subtract 2<sup>32</sup> to get the negative value.",
                ],
                "why": [
                    "This is exactly how binary addition works, bit by bit.",
                    "It is always 32 iterations, O(1) space.",
                ],
                "dry": [
                    "5 = …00101, and -3 in 32-bit two's complement = …11101 (all ones above).",
                    "Bit 0: 1 + 1 → sum 0, carry 1. Bit 1: 0 + 0 + 1 → sum 1, carry 0.",
                    "Bit 2: 1 + 1 → sum 0, carry 1. Bit 3: 0 + 1 + 1 → sum 0, carry 1.",
                    "Bits 4..31 are each 0 + 1 + 1, so sum 0 and carry 1; the final carry falls off the top.",
                    "The result is …00010, and bit 31 is 0, so it is positive: <strong>2</strong>.",
                ],
            },
            "XOR and carry loop with a 32-bit mask": {
                "idea": [
                    "<code>a ^ b</code> adds the bits without carrying; <code>(a &amp; b) &lt;&lt; 1</code> is exactly the carries, moved to where they apply.",
                    "Adding those two again produces new carries, so repeat until no carry is left.",
                    "Python integers are unbounded, so mask with <code>0xFFFFFFFF</code> after each step to emulate 32-bit wrap-around, and convert back to a signed value at the end.",
                ],
                "steps": [
                    "Mask both inputs to 32 bits.",
                    "While <code>b</code> is non-zero: <code>a, b = (a ^ b) &amp; MASK, ((a &amp; b) &lt;&lt; 1) &amp; MASK</code>.",
                    "If <code>a</code> has bit 31 set, return <code>~(a ^ MASK)</code> (the negative value); otherwise return <code>a</code>.",
                ],
                "why": [
                    "The pair (a, b) always has the same sum modulo 2<sup>32</sup>, and the carry moves at least one bit left each round, so at most 32 rounds.",
                    "It is O(32) time and O(1) space.",
                ],
                "dry": [
                    "a = 5 and b = -3 &amp; MASK = 0xFFFFFFFD.",
                    "Round 1: a = 0xFFFFFFF8, carry b = 0xA.",
                    "Round 2: a = 0xFFFFFFF2, b = 0x10. Round 3: a = 0xFFFFFFE2, b = 0x20.",
                    "The carry keeps clearing one more 1 from the top run of ones and moving up. After round 30 it falls off bit 31 and the mask drops it.",
                    "The loop ends with a = 0x2, and bit 31 is clear, so the result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse integer
    "reverse-integer": {
        "example": {"call": "reverse(1534236469)", "expect": "0"},
        "approaches": {
            "String reversal, range check": {
                "idea": [
                    "Reverse the decimal digits as a string, put the sign back, and check whether the result fits in a signed 32-bit integer.",
                ],
                "steps": [
                    "Remember the sign and reverse <code>str(abs(x))</code>.",
                    "Parse it, apply the sign, and return it if it is in [-2<sup>31</sup>, 2<sup>31</sup> - 1], else 0.",
                ],
                "why": [
                    "It gives the correct answer, but it builds the full reversed number before checking, which the 32-bit rule forbids in spirit.",
                    "It is O(digits) time and space.",
                ],
                "dry": [
                    "\"1534236469\" reversed is \"9646324351\".",
                    "9646324351 &gt; 2147483647, so it is out of range.",
                    "The result is <strong>0</strong>.",
                ],
            },
            "Pop and push digits, check before overflowing": {
                "idea": [
                    "Pop the last digit with <code>divmod(n, 10)</code> and push it onto the result with <code>result·10 + digit</code>.",
                    "Before each push, check that the new value will stay within the limit, without ever forming the oversized number.",
                    "The check <code>result &gt; (limit - digit) // 10</code> is the overflow test rearranged so nothing overflows.",
                ],
                "steps": [
                    "<code>limit = 2<sup>31</sup> - 1</code> for positive x, and 2<sup>31</sup> for negative x (its magnitude).",
                    "Work on <code>abs(x)</code>: pop a digit, and if the check fails, return 0; otherwise push it.",
                    "Restore the sign at the end.",
                ],
                "why": [
                    "result·10 + digit ≤ limit is the same as result ≤ (limit - digit) / 10, and the floor keeps it exact for integers.",
                    "It is O(digits) time and O(1) space.",
                ],
                "dry": [
                    "The digits come out as 9, 6, 4, 6, 3, 2, 4, 3, 5, 1.",
                    "result grows: 9, 96, 964, 9646, 96463, 964632, 9646324, 96463243, 964632435.",
                    "Next digit 1: is 964632435 &gt; (2147483647 - 1) // 10 = 214748364? Yes, so pushing would overflow.",
                    "The result is <strong>0</strong>, decided without ever building 9646324351.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ bitwise and of range
    "bitwise-and-range": {
        "example": {"call": "range_bitwise_and(26, 30)", "expect": "24"},
        "approaches": {
            "AND every number": {
                "idea": [
                    "AND all the numbers in the range one after another.",
                    "Once the running result hits 0 it can never come back, so stop early.",
                ],
                "steps": [
                    "<code>result = left</code>; for x from left + 1 to right: <code>result &amp;= x</code>.",
                    "Break if the result becomes 0.",
                ],
                "why": [
                    "It is correct by definition, but a range can be 2<sup>31</sup> numbers long: O(right - left) time.",
                ],
                "dry": [
                    "26 (11010) AND 27 (11011) = 11010 = 26.",
                    "AND 28 (11100) = 11000 = 24. AND 29 (11101) = 24. AND 30 (11110) = 24.",
                    "The result is <strong>24</strong>.",
                ],
            },
            "Shift both until they match": {
                "idea": [
                    "Counting from left to right flips every bit below the highest position where left and right differ, so those bits are 0 in the AND.",
                    "The bits that survive are the common binary prefix of left and right.",
                    "Find it by shifting both right until they are equal, then shift the prefix back.",
                ],
                "steps": [
                    "While <code>left != right</code>: shift both right and count the shifts.",
                    "Return <code>left &lt;&lt; shift</code>.",
                ],
                "why": [
                    "Any bit position below the first difference takes both values 0 and 1 somewhere in the range.",
                    "It takes at most 32 shifts: O(32) time, O(1) space.",
                ],
                "dry": [
                    "26 = 11010, 30 = 11110.",
                    "Shift 1: 1101 vs 1111. Shift 2: 110 vs 111. Shift 3: 11 vs 11, equal.",
                    "The common prefix is 11; shifted back three places it is 11000 = <strong>24</strong>.",
                ],
            },
            "Clear right's lowest bits until it drops to left": {
                "idea": [
                    "Clearing right's lowest set bit (<code>right &amp; (right - 1)</code>) removes a bit that varies within the range.",
                    "Keep clearing while right is still above left; what remains is the common prefix.",
                ],
                "steps": [
                    "While <code>right &gt; left</code>: <code>right &amp;= right - 1</code>.",
                    "Return <code>right</code>.",
                ],
                "why": [
                    "Every cleared bit is below the highest differing bit, so it is 0 in the answer, and the prefix is never touched.",
                    "It runs once per set bit of right: O(32) at worst.",
                ],
                "dry": [
                    "right = 30 (11110) &gt; 26, so clear the lowest set bit: 11100 = 28.",
                    "28 &gt; 26, so clear again: 11000 = 24.",
                    "24 ≤ 26, so stop. The result is <strong>24</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum array end
    "minimum-array-end": {
        "example": {"call": "min_end(4, 5)", "expect": "15"},
        "approaches": {
            "Step to the next superset of x, n - 1 times": {
                "idea": [
                    "For the AND of all elements to be x, every element must contain all of x's 1-bits, and to keep the last element small they should be the smallest such numbers.",
                    "From a valid number cur, the next valid number is <code>(cur + 1) | x</code>: increment, then turn x's bits back on.",
                    "Start at x and take n - 1 such steps.",
                ],
                "steps": [
                    "<code>cur = x</code>.",
                    "Repeat n - 1 times: <code>cur = (cur + 1) | x</code>.",
                    "Return <code>cur</code>.",
                ],
                "why": [
                    "Adding 1 and restoring x's bits gives the smallest number above cur that keeps every bit of x.",
                    "The n smallest valid numbers AND to exactly x (x is the first of them). It is O(n) time, which is too slow when n reaches 10<sup>8</sup>.",
                ],
                "dry": [
                    "x = 5 (101). cur = 5.",
                    "Step 1: 6 (110) | 101 = 111 = 7.",
                    "Step 2: 8 (1000) | 101 = 1101 = 13.",
                    "Step 3: 14 (1110) | 101 = 1111 = 15.",
                    "The result is <strong>15</strong>, from the array [5, 7, 13, 15].",
                ],
            },
            "Deposit the bits of n - 1 into x's zero bits": {
                "idea": [
                    "Valid numbers are x with its zero positions (the free bits) filled in somehow.",
                    "In increasing order, the free bits count like a binary counter: 0, 1, 2, …. So the n-th valid number uses counter value n - 1.",
                    "Build it by walking x's bits from low to high and copying the next bit of n - 1 into each zero position.",
                ],
                "steps": [
                    "<code>k = n - 1</code>, <code>result = x</code>, and <code>bit</code> starts at 1.",
                    "At each position: if x has a 0 there, copy <code>k &amp; 1</code> into it and shift k right.",
                    "Move <code>bit</code> left; stop when k runs out of bits.",
                ],
                "why": [
                    "Free positions keep their relative order, so filling them with the bits of k gives the k-th number in increasing order.",
                    "It is O(log n + log x) time and O(1) space. This is the PDEP (parallel bit deposit) operation.",
                ],
                "dry": [
                    "k = 3 (binary 11), x = 101.",
                    "Position 0: x has a 1, so skip it.",
                    "Position 1: free; k's low bit is 1, so set it: result 111. k becomes 1.",
                    "Position 2: x has a 1, so skip it.",
                    "Position 3: free; k's low bit is 1, so set it: result 1111. k becomes 0 and the loop ends.",
                    "The result is 1111 = <strong>15</strong>.",
                ],
            },
        },
    },
}
