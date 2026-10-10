"""Write-ups for the Bit Manipulation topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ single number
    "single-number": {
        "examples": [
            {"call": "single_number([4, 1, 2, 1, 2])", "expect": "4"},
            {"call": "single_number([2, -3, 2])", "expect": "-3"},
        ],
        "approaches": {
            "Count occurrences": {
                "idea": [
                    "Every value appears twice except one, so the answer is the only value whose count is 1.",
                    "A <code>Counter</code> tallies every value in one pass, and a second pass over its entries picks out the lone one.",
                ],
                "steps": [
                    "Build <code>Counter(nums)</code>, mapping each value to how often it appears.",
                    "Walk its <code>items()</code> as <code>(x, c)</code> pairs.",
                    "The generator yields <code>x</code> only when <code>c == 1</code>.",
                    "<code>next(...)</code> takes the first such value and stops.",
                    "Return it.",
                ],
                "why": [
                    "Exactly one value has count 1 and all others have count 2, so the first match is the answer.",
                    "Counting is one pass and scanning the counts is another: <strong>O(n)</strong> time.",
                    "The counter stores about n / 2 distinct values: <strong>O(n)</strong> space, which is what the XOR trick avoids.",
                ],
                "dry": [
                    [
                        "Counter: {4: 1, 1: 2, 2: 2}.",
                        "First item: 4 with count 1.",
                        "<code>next</code> stops at once.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "Counter: {2: 2, -3: 1}.",
                        "2 has count 2, skipped.",
                        "−3 has count 1.",
                        "It returns <strong>-3</strong>.",
                    ],
                ],
                "faq": [
                    ["What if no value had count 1?",
                     "<code>next</code> would raise StopIteration. The problem guarantees one exists, so no default is given."],
                    ["Does the order of <code>items()</code> matter?",
                     "No. Only one item has count 1, so whichever order the counter uses, the same value is found."],
                    ["Would a plain dict work?",
                     "Yes; <code>Counter</code> is just a dict with the counting loop built in."],
                ],
            },
            "Sum trick: 2 &middot; sum(set) &minus; sum": {
                "idea": [
                    "If every value appeared twice, the total would be <code>2 · sum(set(nums))</code>.",
                    "The real total is short by exactly the single value, because it appears once instead of twice.",
                ],
                "steps": [
                    "Build <code>set(nums)</code>: each distinct value once.",
                    "Double its sum: what the total would be if every value were paired.",
                    "Subtract <code>sum(nums)</code>, the real total.",
                    "The difference is the value that is missing its pair.",
                    "Return it.",
                ],
                "why": [
                    "Paired values contribute 2x to both sides and cancel; the single value contributes 2x on the left and x on the right, leaving x.",
                    "Building the set and two sums are linear: <strong>O(n)</strong> time.",
                    "The set holds up to about n / 2 values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "set = {1, 2, 4}, sum 7, doubled 14.",
                        "sum(nums) = 4 + 1 + 2 + 1 + 2 = 10.",
                        "14 − 10 = 4.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "set = {2, −3}, sum −1, doubled −2.",
                        "sum(nums) = 2 − 3 + 2 = 1.",
                        "−2 − 1 = −3.",
                        "It returns <strong>-3</strong>.",
                    ],
                ],
                "faq": [
                    ["Do negative numbers break it?",
                     "No. The algebra holds for any integers, as the second example shows."],
                    ["Can it overflow?",
                     "Not in Python, whose integers are unbounded. In a fixed-width language the doubled sum could overflow, another reason to prefer XOR."],
                    ["Why is this still O(n) space?",
                     "The set needs memory for every distinct value. Only the XOR approach is truly O(1)."],
                ],
            },
            "XOR everything": {
                "idea": [
                    "XOR has three useful facts: <code>x ^ x = 0</code>, <code>x ^ 0 = x</code>, and the order of XORs does not matter.",
                    "XOR all numbers together and each pair cancels to 0 wherever it sits, leaving only the single value.",
                ],
                "steps": [
                    "Set <code>result = 0</code>.",
                    "For each <code>x</code> in <code>nums</code>, do <code>result ^= x</code>.",
                    "Pairs cancel bit by bit, no matter how far apart they are.",
                    "The single value is XORed with 0 overall, so it survives unchanged.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "XOR is commutative and associative, so the list can be regrouped as (pair) ^ (pair) ^ … ^ single = 0 ^ … ^ single = single.",
                    "One pass: <strong>O(n)</strong> time.",
                    "Only <code>result</code> is kept: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "result = 0 ^ 4 = 4 (100).",
                        "^ 1 → 5 (101). ^ 2 → 7 (111).",
                        "^ 1 → 6 (110): the 1 cancels.",
                        "^ 2 → 4 (100): the 2 cancels.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "result = 0 ^ 2 = 2.",
                        "2 ^ −3 = −1 (in two's complement, …1111).",
                        "−1 ^ 2 = −3: the 2 cancels.",
                        "It returns <strong>-3</strong>.",
                    ],
                ],
                "faq": [
                    ["Does XOR work on negative numbers in Python?",
                     "Yes. Python treats negatives as infinitely sign-extended two's complement, so <code>^</code> behaves bit by bit and pairs still cancel."],
                    ["Why must result start at 0?",
                     "0 is the identity for XOR: <code>0 ^ x = x</code>. Starting anywhere else would mix that value into the answer."],
                    ["Does this work if the others appear three times?",
                     "No: <code>x ^ x ^ x = x</code>, so triples do not cancel. That variant needs per-bit counting modulo 3."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ number of 1 bits
    "number-of-1-bits": {
        "examples": [
            {"call": "hamming_weight(44)", "expect": "3"},
            {"call": "hamming_weight(128)", "expect": "1"},
        ],
        "approaches": {
            "Check each of the 32 bits": {
                "idea": [
                    "The lowest bit of <code>n</code> is <code>n &amp; 1</code>. Shifting right moves the next bit into that position.",
                    "Add up the lowest bit and shift until nothing is left.",
                ],
                "steps": [
                    "Set <code>count = 0</code>.",
                    "While <code>n</code> is non-zero:",
                    "Add <code>n &amp; 1</code> (0 or 1) to <code>count</code>.",
                    "Shift <code>n &gt;&gt;= 1</code> to drop the bit just counted.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Every bit reaches position 0 exactly once before it is shifted out, so each set bit is counted once.",
                    "The loop runs once per bit up to the highest set bit, at most 32 for a 32-bit input: <strong>O(32)</strong> time.",
                    "Only <code>count</code> and <code>n</code>: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "44 = 101100.",
                        "Bits 0 and 1 are 0: n becomes 22, then 11, count 0.",
                        "11 &amp; 1 = 1 → count 1, n 5. 5 &amp; 1 = 1 → count 2, n 2.",
                        "2 &amp; 1 = 0, n 1. 1 &amp; 1 = 1 → count 3, n 0.",
                        "It returns <strong>3</strong> after 6 iterations.",
                    ],
                    [
                        "128 = 10000000.",
                        "Seven shifts find only zeros: n goes 64, 32, …, 1.",
                        "The eighth iteration counts the 1 and n becomes 0.",
                        "It returns <strong>1</strong>, after 8 iterations for a single bit.",
                    ],
                ],
                "faq": [
                    ["What happens with a negative <code>n</code> in Python?",
                     "<code>-1 &gt;&gt; 1</code> is still −1, so the loop never ends. The problem passes an unsigned 32-bit value, so <code>n</code> is never negative."],
                    ["Why <code>while n</code> instead of exactly 32 iterations?",
                     "Once <code>n</code> is 0 every remaining bit is 0, so stopping early is safe and faster for small numbers."],
                    ["Is <code>n % 2</code> the same as <code>n &amp; 1</code>?",
                     "For non-negative numbers, yes. <code>&amp;</code> just states the bit intent more directly."],
                ],
            },
            "Kernighan: clear the lowest set bit": {
                "idea": [
                    "Subtracting 1 flips the lowest set bit to 0 and every 0 below it to 1. ANDing with the original clears exactly that lowest set bit.",
                    "So <code>n &amp;= n - 1</code> removes one set bit per iteration, and the number of iterations is the answer.",
                ],
                "steps": [
                    "Set <code>count = 0</code>.",
                    "While <code>n</code> is non-zero:",
                    "Replace <code>n</code> with <code>n &amp; (n - 1)</code>.",
                    "Add 1 to <code>count</code>.",
                    "Return <code>count</code> when <code>n</code> reaches 0.",
                ],
                "why": [
                    "Bits above the lowest set bit are the same in <code>n</code> and <code>n - 1</code>, so they survive the AND; the lowest set bit and everything below become 0.",
                    "Each iteration removes exactly one set bit: <strong>O(number of set bits)</strong> time, never more than 32.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 101100 (44).",
                        "44 &amp; 43 = 101000 (40), count 1.",
                        "40 &amp; 39 = 100000 (32), count 2.",
                        "32 &amp; 31 = 0, count 3.",
                        "It returns <strong>3</strong> after 3 iterations instead of 6.",
                    ],
                    [
                        "n = 10000000 (128).",
                        "128 &amp; 127 = 0, count 1.",
                        "The loop ends immediately.",
                        "It returns <strong>1</strong> after a single iteration.",
                    ],
                ],
                "faq": [
                    ["Why does <code>n - 1</code> flip the bits below the lowest 1?",
                     "Subtraction borrows from the lowest 1: it becomes 0 and each 0 below it becomes 1, like 1000 − 1 = 0111."],
                    ["When is this faster than shifting?",
                     "When few bits are set but the highest one is far up, like 128: one iteration instead of eight."],
                    ["Where else is <code>n &amp; (n - 1)</code> used?",
                     "<code>n &amp; (n - 1) == 0</code> tests for a power of two, and Counting Bits uses it as a DP step."],
                ],
            },
            "Built-in popcount": {
                "idea": [
                    "Python 3.10 added <code>int.bit_count()</code>, which returns the number of 1 bits directly.",
                    "It is implemented in C and often maps to a single CPU popcount instruction.",
                ],
                "steps": [
                    "Call <code>n.bit_count()</code>.",
                    "It counts the 1s in the binary representation of <code>abs(n)</code>.",
                    "For the non-negative inputs here that is exactly the Hamming weight.",
                    "Return the result.",
                ],
                "why": [
                    "It computes the same count as the loops, just in native code.",
                    "For word-sized integers it is <strong>O(1)</strong> time; for huge integers it is linear in their number of machine words.",
                    "<strong>O(1)</strong> space.",
                    "Before 3.10 the equivalent is <code>bin(n).count(\"1\")</code>, which builds a string first.",
                ],
                "dry": [
                    [
                        "n = 44 = 0b101100.",
                        "<code>bit_count()</code> counts the 1s at positions 2, 3 and 5.",
                        "No Python-level loop runs.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "n = 128 = 0b10000000.",
                        "Only bit 7 is set.",
                        "One call does the work.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["What does it return for negative numbers?",
                     "The count for the absolute value: <code>(-7).bit_count()</code> is 3, not the 32-bit two's-complement count."],
                    ["Is it fine to use in an interview?",
                     "Mention it, but expect to be asked for a manual version; Kernighan's trick is the usual follow-up."],
                    ["Is <code>bin(n).count(\"1\")</code> just as good?",
                     "It gives the same answer but creates a string, so it is slower and uses O(log n) extra memory."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ counting bits
    "counting-bits": {
        "examples": [
            {"call": "count_bits(5)", "expect": "[0, 1, 1, 2, 1, 2]"},
            {"call": "count_bits(0)", "expect": "[0]"},
        ],
        "approaches": {
            "Popcount each number": {
                "idea": [
                    "The answer for each <code>i</code> from 0 to <code>n</code> is just its number of set bits.",
                    "Count them one number at a time with Kernighan's <code>i &amp;= i - 1</code> loop.",
                ],
                "steps": [
                    "Start an empty list <code>out</code>.",
                    "For each <code>i</code> in <code>0 .. n</code>, set <code>c = 0</code>.",
                    "While <code>i</code> is non-zero, clear its lowest set bit with <code>i &amp;= i - 1</code> and add 1 to <code>c</code>.",
                    "Append <code>c</code> to <code>out</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Each count is correct by Kernighan's argument: one iteration per set bit.",
                    "A number up to <code>n</code> has at most log₂ n + 1 bits, so the total is <strong>O(n log n)</strong> time.",
                    "Besides the output list, only <code>c</code> is kept: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "i=0: no iterations, 0. i=1: 1 → 0, count 1. i=2: 1.",
                        "i=3 (11): 3 → 2 → 0, count 2.",
                        "i=4 (100): count 1. i=5 (101): 5 → 4 → 0, count 2.",
                        "It returns <strong>[0, 1, 1, 2, 1, 2]</strong>.",
                    ],
                    [
                        "Only i = 0 is in range.",
                        "0 has no set bits, so the inner loop does not run.",
                        "out = [0].",
                        "It returns <strong>[0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Does reassigning <code>i</code> inside the loop break the <code>for</code>?",
                     "No. The <code>for</code> takes the next value from <code>range</code> regardless, so changing the local <code>i</code> is harmless."],
                    ["Why is this O(n log n) and not O(n)?",
                     "Each number pays for its own bits separately. The DP approaches reuse an earlier answer instead, at O(1) per number."],
                    ["Why use Kernighan rather than shifting?",
                     "It loops once per set bit instead of once per bit position, which is never slower."],
                ],
            },
            "DP on the shifted number": {
                "idea": [
                    "<code>i &gt;&gt; 1</code> is <code>i</code> with its lowest bit removed, and it is smaller than <code>i</code>, so its count is already known.",
                    "So <code>bits[i] = bits[i &gt;&gt; 1] + (i &amp; 1)</code>: the bits of the half, plus the lowest bit itself.",
                ],
                "steps": [
                    "Create <code>bits = [0] * (n + 1)</code>; <code>bits[0] = 0</code> is the base case.",
                    "Loop <code>i</code> from 1 to <code>n</code>.",
                    "Look up <code>bits[i &gt;&gt; 1]</code>, the count without the lowest bit.",
                    "Add <code>i &amp; 1</code>, which is 1 for odd <code>i</code> and 0 for even.",
                    "Return <code>bits</code>.",
                ],
                "why": [
                    "Shifting right drops exactly one bit, the lowest, and keeps the rest, so the recurrence is exact.",
                    "<code>i &gt;&gt; 1 &lt; i</code> for every <code>i ≥ 1</code>, so the needed entry is always filled first.",
                    "One O(1) step per number: <strong>O(n)</strong> time, with <strong>O(1)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "i=1: bits[0] + 1 = 1. i=2: bits[1] + 0 = 1.",
                        "i=3: bits[1] + 1 = 2.",
                        "i=4: bits[2] + 0 = 1.",
                        "i=5: bits[2] + 1 = 2.",
                        "It returns <strong>[0, 1, 1, 2, 1, 2]</strong>.",
                    ],
                    [
                        "bits = [0].",
                        "range(1, 1) is empty, so nothing is filled.",
                        "The base case is the whole answer.",
                        "It returns <strong>[0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>bits[i &gt;&gt; 1]</code> always ready?",
                     "Halving makes the number strictly smaller for <code>i ≥ 1</code>, and the loop fills entries in increasing order."],
                    ["Could I write <code>i // 2</code> and <code>i % 2</code>?",
                     "Yes, for non-negative <code>i</code> they are the same values; the bit operators just show the idea."],
                    ["How is this different from the lowest-set-bit DP?",
                     "This one removes the lowest <em>bit</em> (0 or 1); the other removes the lowest <em>set</em> bit, so it always adds exactly 1."],
                ],
            },
            "DP on the lowest set bit": {
                "idea": [
                    "<code>i &amp; (i - 1)</code> is <code>i</code> with its lowest set bit cleared: exactly one fewer 1, and a smaller number.",
                    "So <code>bits[i] = bits[i &amp; (i - 1)] + 1</code>.",
                ],
                "steps": [
                    "Create <code>bits = [0] * (n + 1)</code>.",
                    "Loop <code>i</code> from 1 to <code>n</code>.",
                    "Compute <code>i &amp; (i - 1)</code>, the number with one set bit removed.",
                    "Set <code>bits[i]</code> to its count plus 1.",
                    "Return <code>bits</code>.",
                ],
                "why": [
                    "Kernighan's step removes exactly one set bit, so the counts differ by exactly 1.",
                    "<code>i &amp; (i - 1) &lt; i</code> for <code>i ≥ 1</code>, so the entry is filled already.",
                    "One O(1) step per number: <strong>O(n)</strong> time and <strong>O(1)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "i=1: 1 &amp; 0 = 0, bits = 0 + 1 = 1.",
                        "i=2: 2 &amp; 1 = 0 → 1. i=3: 3 &amp; 2 = 2 → bits[2] + 1 = 2.",
                        "i=4: 4 &amp; 3 = 0 → 1.",
                        "i=5: 5 &amp; 4 = 4 → bits[4] + 1 = 2.",
                        "It returns <strong>[0, 1, 1, 2, 1, 2]</strong>.",
                    ],
                    [
                        "bits = [0].",
                        "The loop does not run for n = 0.",
                        "Nothing else is needed.",
                        "It returns <strong>[0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>i &amp; (i - 1)</code> smaller than <code>i</code>?",
                     "It equals <code>i</code> with a 1 turned into a 0, which can only make the number smaller."],
                    ["Which DP should I present?",
                     "Either; both are O(n). The shift version is often easier to explain, this one links neatly to Kernighan."],
                    ["What does <code>i &amp; (i - 1)</code> give for a power of two?",
                     "0, since a power of two has a single set bit. So every power of two gets <code>bits[0] + 1 = 1</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add binary
    "add-binary": {
        "examples": [
            {"call": 'add_binary("1011", "111")', "expect": '"10010"'},
            {"call": 'add_binary("0", "0")', "expect": '"0"'},
        ],
        "approaches": {
            "Convert to integers": {
                "idea": [
                    "Python parses binary strings with <code>int(s, 2)</code> and prints integers in binary with <code>bin</code>.",
                    "Its integers are unbounded, so converting, adding and converting back is exact for any length.",
                ],
                "steps": [
                    "Parse <code>a</code> and <code>b</code> with <code>int(…, 2)</code>.",
                    "Add the two integers.",
                    "Format the sum with <code>bin(...)</code>, which gives a string like <code>\"0b10010\"</code>.",
                    "Slice off the <code>\"0b\"</code> prefix with <code>[2:]</code>.",
                    "Return the rest.",
                ],
                "why": [
                    "Parsing and formatting are exact inverses and Python addition never overflows, so the result is correct.",
                    "Parsing and printing are linear in the number of digits: <strong>O(n + m)</strong> time.",
                    "The integers and the output string take <strong>O(n + m)</strong> space.",
                ],
                "dry": [
                    [
                        "int(\"1011\", 2) = 11, int(\"111\", 2) = 7.",
                        "11 + 7 = 18.",
                        "bin(18) = \"0b10010\".",
                        "Without the prefix: <strong>\"10010\"</strong>.",
                    ],
                    [
                        "Both parse to 0.",
                        "0 + 0 = 0.",
                        "bin(0) = \"0b0\".",
                        "Without the prefix: <strong>\"0\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>[2:]</code>?",
                     "<code>bin</code> always starts with <code>\"0b\"</code>; the problem wants only the digits."],
                    ["Does this work in languages with fixed-size integers?",
                     "Only for short strings. Long inputs overflow, which is why interviewers want the digit-by-digit version."],
                    ["Does it keep leading zeros?",
                     "No, <code>bin</code> never prints them, which matches what the problem expects."],
                ],
            },
            "Digit by digit with a carry": {
                "idea": [
                    "Add the way you would on paper: from the rightmost digit, sum the two digits plus the carry.",
                    "The sum is 0 to 3: its last bit (<code>total % 2</code>) is the output digit and its high bit (<code>total // 2</code>) is the next carry.",
                ],
                "steps": [
                    "Set <code>i</code> and <code>j</code> to the last indices of <code>a</code> and <code>b</code>, <code>carry = 0</code>, <code>out = []</code>.",
                    "Loop while either string has digits left or <code>carry</code> is 1.",
                    "<code>total = carry</code>, plus <code>a[i]</code> if <code>i &gt;= 0</code> and <code>b[j]</code> if <code>j &gt;= 0</code>, moving each index left.",
                    "Append <code>str(total % 2)</code> and set <code>carry = total // 2</code>.",
                    "Digits were produced right to left, so return <code>\"\".join(reversed(out))</code>.",
                ],
                "why": [
                    "This is schoolbook addition in base 2, so each output digit and carry is correct by induction from the right.",
                    "Keeping <code>carry</code> in the loop condition writes the final extra 1 when the sum is longer than both inputs.",
                    "One step per output digit: <strong>O(max(n, m))</strong> time, and the output list is <strong>O(max(n, m))</strong> space.",
                ],
                "dry": [
                    [
                        "1 + 1 = 2 → digit 0, carry 1.",
                        "1 + 1 + 1 = 3 → digit 1, carry 1.",
                        "0 + 1 + 1 = 2 → digit 0, carry 1. Then <code>b</code> is used up.",
                        "1 + 1 = 2 → digit 0, carry 1. Only the carry is left → digit 1.",
                        "out = 0, 1, 0, 0, 1 reversed: <strong>\"10010\"</strong>.",
                    ],
                    [
                        "i = j = 0, carry 0.",
                        "0 + 0 = 0 → digit 0, carry 0.",
                        "Both indices are −1 and carry is 0, so the loop stops.",
                        "It returns <strong>\"0\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>carry</code> part of the loop condition?",
                     "Without it, \"1\" + \"1\" would stop after writing 0 and return \"0\" instead of \"10\"."],
                    ["Why build a list and reverse it?",
                     "Digits come out right to left. Appending then reversing once is O(n), while prepending to a string each time is O(n²)."],
                    ["What if the strings have different lengths?",
                     "The shorter one's index goes negative first and simply stops contributing, like padding it with zeros."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse bits
    "reverse-bits": {
        "examples": [
            {"call": "reverse_bits(11)", "expect": "3489660928"},
            {"call": "reverse_bits(1)", "expect": "2147483648"},
        ],
        "approaches": {
            "String reversal": {
                "idea": [
                    "Write the number as exactly 32 binary digits, reverse the string, and read it back as binary.",
                    "The padding to 32 digits matters: leading zeros become trailing zeros after the reversal.",
                ],
                "steps": [
                    "<code>format(n, \"032b\")</code> gives a 32-character string padded with leading zeros.",
                    "Reverse it with <code>[::-1]</code>.",
                    "Parse the result with <code>int(…, 2)</code>.",
                    "Return the integer.",
                ],
                "why": [
                    "Character <code>k</code> of the padded string is bit 31 − k, so reversing the string maps bit k to bit 31 − k exactly.",
                    "The string always has 32 characters: <strong>O(32)</strong> time.",
                    "The temporary strings take <strong>O(32)</strong> space.",
                ],
                "dry": [
                    [
                        "format(11, \"032b\") = 28 zeros then 1011.",
                        "Reversed: 1101 then 28 zeros.",
                        "That is 0xD0000000.",
                        "It returns <strong>3489660928</strong>.",
                    ],
                    [
                        "format(1, \"032b\") = 31 zeros then 1.",
                        "Reversed: 1 then 31 zeros.",
                        "That is 2<sup>31</sup>.",
                        "It returns <strong>2147483648</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not reverse <code>bin(n)[2:]</code>?",
                     "<code>bin</code> drops leading zeros. For 11 it gives \"1011\", which reverses to 13 instead of 3489660928."],
                    ["Is the result signed?",
                     "No. Python reads the string as a plain non-negative number, which is what an unsigned 32-bit answer should be."],
                    ["Is this acceptable in an interview?",
                     "As a first answer, yes; then show the bit-shifting version."],
                ],
            },
            "Shift bits out one at a time": {
                "idea": [
                    "Read bits from the low end of <code>n</code> and push them onto the low end of <code>result</code>.",
                    "The first bit read ends up shifted left 31 times, so it lands in the top position: the order is reversed.",
                ],
                "steps": [
                    "Set <code>result = 0</code>.",
                    "Repeat exactly 32 times:",
                    "Shift <code>result</code> left one place and OR in <code>n &amp; 1</code>, the current lowest bit of <code>n</code>.",
                    "Shift <code>n</code> right one place.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "Bit k of <code>n</code> is read on iteration k and then shifted left 31 − k more times, ending at position 31 − k.",
                    "Running exactly 32 times, not until <code>n</code> is 0, keeps the trailing zeros that leading zeros turn into.",
                    "32 iterations: <strong>O(32)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 1011. Iterations 0–3 read 1, 1, 0, 1: result = 1, 11, 110, 1101.",
                        "n is now 0.",
                        "Iterations 4–31 shift in 28 zeros.",
                        "result = 1101 followed by 28 zeros = 0xD0000000.",
                        "It returns <strong>3489660928</strong>.",
                    ],
                    [
                        "Iteration 0 reads the 1: result = 1, n = 0.",
                        "Iterations 1–31 shift it left 31 places in total.",
                        "result = 2<sup>31</sup>.",
                        "It returns <strong>2147483648</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not stop when <code>n</code> becomes 0?",
                     "The remaining shifts are what move the early bits to the top. Stopping early would return 13 for 11."],
                    ["Why OR and not add?",
                     "After the shift the lowest bit of <code>result</code> is 0, so OR and + give the same value; OR states the intent."],
                    ["Could I build it with <code>result |= (n &gt;&gt; k &amp; 1) &lt;&lt; (31 - k)</code>?",
                     "Yes, that places each bit directly. It is the same O(32) work."],
                ],
            },
            "Divide and conquer with masks": {
                "idea": [
                    "Reversing 32 bits = swap the two 16-bit halves, then reverse each half. Recursing, swap bytes inside halves, nibbles inside bytes, pairs inside nibbles, and finally bits inside pairs.",
                    "Each level is one line: a mask selects the left or right blocks in every position at once, and shifts swap them in parallel.",
                ],
                "steps": [
                    "Swap halves: <code>(n &gt;&gt; 16) | ((n &amp; 0xFFFF) &lt;&lt; 16)</code>.",
                    "Swap bytes inside each half with masks <code>0xFF00FF00</code> / <code>0x00FF00FF</code> and shifts of 8.",
                    "Swap nibbles with <code>0xF0F0F0F0</code> / <code>0x0F0F0F0F</code> and shifts of 4.",
                    "Swap bit pairs with <code>0xCCCCCCCC</code> / <code>0x33333333</code> and shifts of 2.",
                    "Swap single bits with <code>0xAAAAAAAA</code> / <code>0x55555555</code> and shifts of 1, then return <code>n</code>.",
                ],
                "why": [
                    "Each level flips one bit of every bit's position number (the 16s, 8s, 4s, 2s and 1s digit); flipping all five turns position k into 31 − k.",
                    "Five fixed steps: <strong>O(log 32) = 5</strong> operations, <strong>O(1)</strong> space.",
                    "The masks keep the value inside 32 bits, so Python's unbounded integers do not leak extra high bits.",
                ],
                "dry": [
                    [
                        "n = 0x0000000B.",
                        "Halves: 0x000B0000. Bytes: 0x0B000000.",
                        "Nibbles: 0xB0000000 (B = 1011).",
                        "Pairs: 10|11 → 11|10, so 0xE0000000. Bits: 11|10 → 11|01, so 0xD0000000.",
                        "It returns <strong>3489660928</strong>.",
                    ],
                    [
                        "n = 0x00000001.",
                        "Halves → 0x00010000. Bytes → 0x01000000. Nibbles → 0x10000000.",
                        "Pairs → 0x40000000.",
                        "Bits → 0x80000000.",
                        "It returns <strong>2147483648</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the first line not masked on the left part?",
                     "<code>n &gt;&gt; 16</code> already drops the low half and the input has only 32 bits, so nothing extra survives."],
                    ["Where do the mask values come from?",
                     "0xA = 1010 selects the left bit of each pair, 0xC = 1100 the left pair of each nibble, 0xF0 the left nibble of each byte, and so on."],
                    ["Is this faster than the loop in Python?",
                     "Slightly, but the real win is in C or hardware, where it is a handful of instructions with no loop."],
                ],
            },
        },
    },
    # ------------------------------------------------------------------ missing number
    "missing-number": {
        "examples": [
            {"call": "missing_number([3, 0, 1])", "expect": "2"},
            {"call": "missing_number([0, 1])", "expect": "2"},
        ],
        "approaches": {
            "Sort, find the gap": {
                "idea": [
                    "Sorted, the numbers <code>0 .. n</code> with one missing line up with their indices until the gap: the first index <code>i</code> holding something other than <code>i</code> is the missing value.",
                    "If no index mismatches, the missing number is <code>n</code> itself, the one past the end.",
                ],
                "steps": [
                    "Sort the numbers.",
                    "Walk them with <code>enumerate</code> as <code>(i, x)</code>.",
                    "At the first <code>x != i</code>, return <code>i</code>.",
                    "Every value before the gap sits at its own index, so this is the first absent value.",
                    "If the loop ends, return <code>len(nums)</code>.",
                ],
                "why": [
                    "Before the missing value every number matches its index; from the gap onwards each number is one more than its index.",
                    "Sorting dominates: <strong>O(n log n)</strong> time.",
                    "<code>sorted</code> builds a new list, <strong>O(n)</strong>; sorting in place with <code>nums.sort()</code> would make it <strong>O(1)</strong> extra, hence the O(1)–O(n) range.",
                ],
                "dry": [
                    [
                        "sorted = [0, 1, 3].",
                        "i=0: 0 matches. i=1: 1 matches.",
                        "i=2: 3 ≠ 2.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "sorted = [0, 1].",
                        "i=0 and i=1 both match.",
                        "The loop ends without a gap, so the missing number is n.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return <code>len(nums)</code> after the loop?",
                     "The range is <code>0 .. n</code> with n = len(nums). If 0 to n − 1 are all present, n is the missing one."],
                    ["Does the problem allow duplicates?",
                     "No: the values are distinct, which is what makes \"value equals index\" hold before the gap."],
                    ["Why mention this at all if it is slower?",
                     "It is the most obvious idea, and it uses no arithmetic tricks, so it is a safe starting point."],
                ],
            },
            "Hash set": {
                "idea": [
                    "Put every number in a set, then check <code>0, 1, …, n</code> in order; the first one not in the set is missing.",
                    "Set lookups are O(1) on average, so there is no need to sort.",
                ],
                "steps": [
                    "Build <code>present = set(nums)</code>.",
                    "Loop <code>i</code> over <code>range(len(nums) + 1)</code>, the full range 0 .. n.",
                    "The generator yields the <code>i</code>s that are not in <code>present</code>.",
                    "<code>next(...)</code> returns the first one.",
                ],
                "why": [
                    "Exactly one value from 0 to n is absent, so the first absent one is the answer.",
                    "Building the set and scanning the range are both linear: <strong>O(n)</strong> time.",
                    "The set holds n values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "present = {0, 1, 3}.",
                        "0 is present, 1 is present.",
                        "2 is not.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "present = {0, 1}.",
                        "The range is 0, 1, 2.",
                        "0 and 1 are present; 2 is not.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>len(nums) + 1</code> in the range?",
                     "The values go up to n inclusive, and n itself may be the missing one, as in the second example."],
                    ["Can <code>next</code> ever raise StopIteration here?",
                     "No. n + 1 candidates and n distinct values means at least one candidate is absent."],
                    ["Is this better than sorting?",
                     "It is faster, O(n) instead of O(n log n), but uses a full set of extra memory."],
                ],
            },
            "Gauss's sum": {
                "idea": [
                    "The sum of <code>0 .. n</code> is <code>n(n + 1) / 2</code>. The array holds all of them but one.",
                    "So the missing value is the expected sum minus the actual sum.",
                ],
                "steps": [
                    "Let <code>n = len(nums)</code>.",
                    "Compute the expected total <code>n * (n + 1) // 2</code>.",
                    "Subtract <code>sum(nums)</code>.",
                    "Return the difference.",
                ],
                "why": [
                    "Every present value appears on both sides and cancels; only the missing value is left.",
                    "One pass for <code>sum</code>: <strong>O(n)</strong> time.",
                    "A couple of numbers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 3, expected 3 · 4 / 2 = 6.",
                        "sum([3, 0, 1]) = 4.",
                        "6 − 4 = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "n = 2, expected 2 · 3 / 2 = 3.",
                        "sum([0, 1]) = 1.",
                        "3 − 1 = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>//</code> and not <code>/</code>?",
                     "<code>n(n + 1)</code> is always even, so <code>//</code> is exact and keeps the result an int; <code>/</code> would give a float."],
                    ["Can this overflow?",
                     "Not in Python. In a 32-bit language, n(n + 1) can overflow for large n, which the XOR version avoids."],
                    ["Does the input need to be sorted?",
                     "No. Addition does not care about order."],
                ],
            },
            "XOR indices with values": {
                "idea": [
                    "XOR together every index <code>0 .. n − 1</code>, the number <code>n</code>, and every value. Each present value is matched by an equal index or by <code>n</code>, and cancels.",
                    "What survives is the one number from <code>0 .. n</code> that has no partner among the values: the missing one.",
                ],
                "steps": [
                    "Start <code>result = len(nums)</code>, which covers the index n that <code>enumerate</code> never produces.",
                    "For each <code>(i, x)</code>, do <code>result ^= i ^ x</code>.",
                    "Pairs of equal numbers cancel, whatever order they arrive in.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "The XOR contains every number in <code>0 .. n</code> once (as indices and the starting <code>n</code>) and every present value once more, so all but the missing number appear twice.",
                    "One pass: <strong>O(n)</strong> time.",
                    "One integer: <strong>O(1)</strong> space, with no risk of overflow even in fixed-width languages.",
                ],
                "dry": [
                    [
                        "result = 3.",
                        "i=0, x=3: 3 ^ 0 ^ 3 = 0.",
                        "i=1, x=0: 0 ^ 1 ^ 0 = 1.",
                        "i=2, x=1: 1 ^ 2 ^ 1 = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "result = 2.",
                        "i=0, x=0: they cancel, result 2.",
                        "i=1, x=1: they cancel, result 2.",
                        "The starting n was never cancelled: <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start at <code>len(nums)</code> instead of 0?",
                     "Indices only run to n − 1, but the range of values goes to n. Starting at n puts that last number into the XOR."],
                    ["Is this just Single Number in disguise?",
                     "Yes: indices plus values form a list where every number appears twice except the missing one."],
                    ["Why prefer it over Gauss's sum?",
                     "Both are O(n) and O(1). XOR cannot overflow, which matters in languages with fixed-width integers."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sum of two integers
    "sum-of-two-integers": {
        "examples": [
            {"call": "get_sum(5, -3)", "expect": "2"},
            {"call": "get_sum(-5, -7)", "expect": "-12"},
        ],
        "approaches": {
            "Full adder, one bit at a time": {
                "idea": [
                    "Build the sum the way hardware does: for each of the 32 bit positions, add the two input bits and the incoming carry.",
                    "The sum bit is <code>x ^ y ^ carry</code>; the next carry is 1 when at least two of the three are 1.",
                    "Negative numbers work because Python's <code>&gt;&gt;</code> reads their two's-complement bits; at the end, the 32-bit result is turned back into a signed value.",
                ],
                "steps": [
                    "Set <code>result = carry = 0</code>.",
                    "For <code>i</code> in 0 .. 31: read <code>x = (a &gt;&gt; i) &amp; 1</code> and <code>y = (b &gt;&gt; i) &amp; 1</code>.",
                    "Set bit <code>i</code> of <code>result</code> to <code>x ^ y ^ carry</code>.",
                    "Update <code>carry = (x &amp; y) | (x &amp; carry) | (y &amp; carry)</code>, the majority of the three.",
                    "If bit 31 of <code>result</code> is set, the value is negative: return <code>result - (1 &lt;&lt; 32)</code>; otherwise return <code>result</code>.",
                ],
                "why": [
                    "Each position is a correct one-bit full adder, so the 32 bits are the true sum modulo 2<sup>32</sup>.",
                    "Subtracting 2<sup>32</sup> when bit 31 is set is the standard two's-complement reading, giving the signed answer.",
                    "Exactly 32 iterations: <strong>O(32)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "5 = …0101, −3 = …1101 (all higher bits 1).",
                        "Bit 0: 1 + 1 → sum 0, carry 1.",
                        "Bit 1: 0 + 0 + 1 → sum 1, carry 0. result = 0b10.",
                        "Bit 2: 1 + 1 → sum 0, carry 1. Bits 3..31: 0 + 1 + 1 → sum 0, carry 1.",
                        "result = 0x2, bit 31 clear: <strong>2</strong>.",
                    ],
                    [
                        "−5 = …11011, −7 = …11001.",
                        "Bit 0: 1 + 1 → 0, carry 1. Bit 1: 1 + 0 + 1 → 0, carry 1.",
                        "Bit 2: 0 + 0 + 1 → 1, carry 0. Bit 3: 1 + 1 → 0, carry 1.",
                        "Bits 4..31: 1 + 1 + 1 → 1, carry 1. result = 0xFFFFFFF4.",
                        "Bit 31 is set: 0xFFFFFFF4 − 2<sup>32</sup> = <strong>-12</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>(a &gt;&gt; i) &amp; 1</code> work for negative <code>a</code>?",
                     "Python shifts negatives arithmetically, as if they had infinitely many leading 1s, so each read gives the two's-complement bit."],
                    ["What happens to the carry out of bit 31?",
                     "It is dropped, exactly as in 32-bit hardware. That is what makes 5 + (−3) wrap round to 2."],
                    ["Is this allowed if <code>+</code> is banned?",
                     "The bit work uses only <code>^</code>, <code>&amp;</code>, <code>|</code> and shifts. The final <code>- (1 &lt;&lt; 32)</code> is a sign conversion; <code>~(result ^ 0xFFFFFFFF)</code> does the same without arithmetic."],
                ],
            },
            "XOR and carry loop with a 32-bit mask": {
                "idea": [
                    "<code>a ^ b</code> adds without carrying, and <code>(a &amp; b) &lt;&lt; 1</code> is exactly the carries. Their sum is still <code>a + b</code>.",
                    "Repeat with those two numbers until the carry is 0; then the XOR alone is the sum.",
                    "Python integers are unbounded, so a <code>0xFFFFFFFF</code> mask simulates 32-bit wraparound, otherwise a negative carry would march left forever.",
                ],
                "steps": [
                    "Mask both inputs to 32 bits: <code>a, b = a &amp; MASK, b &amp; MASK</code>.",
                    "While <code>b</code> (the carry) is non-zero: <code>a, b = (a ^ b) &amp; MASK, ((a &amp; b) &lt;&lt; 1) &amp; MASK</code>.",
                    "When the carry is 0, <code>a</code> holds the 32-bit sum.",
                    "If <code>a &lt;= 0x7FFFFFFF</code> it is non-negative: return it.",
                    "Otherwise turn it into a negative Python int with <code>~(a ^ MASK)</code>.",
                ],
                "why": [
                    "Each round keeps <code>a + b</code> unchanged modulo 2<sup>32</sup> and moves the carry at least one bit left, so after at most 32 rounds it falls off the mask.",
                    "<code>a ^ MASK</code> flips the low 32 bits and <code>~</code> flips everything, which leaves the low bits as they were and fills the top with 1s: the negative value.",
                    "At most 32 rounds: <strong>O(32)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "a = 0x5, b = 0xFFFFFFFD.",
                        "Round 1: a = 0xFFFFFFF8, carry 0xA. Round 2: a = 0xFFFFFFF2, carry 0x10.",
                        "The single carry bit then marches left one place per round: 0x20, 0x40, …, 0x80000000.",
                        "Round 30: the carry falls off the mask, a = 0x2.",
                        "0x2 ≤ 0x7FFFFFFF: <strong>2</strong>.",
                    ],
                    [
                        "a = 0xFFFFFFFB, b = 0xFFFFFFF9.",
                        "Round 1: a = 0x2, carry 0xFFFFFFF2.",
                        "Round 2: a = 0xFFFFFFF0, carry 0x4. Round 3: a = 0xFFFFFFF4, carry 0.",
                        "a is above 0x7FFFFFFF, so ~(0xFFFFFFF4 ^ MASK) = ~0xB.",
                        "It returns <strong>-12</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong without the mask?",
                     "With 5 and −3 the carry never becomes 0: Python keeps shifting a negative carry left, so the loop runs forever."],
                    ["Why <code>~(a ^ MASK)</code> instead of <code>a - 2**32</code>?",
                     "Both give the same value. The XOR form avoids arithmetic, in the spirit of the problem."],
                    ["How many rounds can it take?",
                     "Up to 32: a carry can travel the whole width, as in the first example, which needs 30."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse integer
    "reverse-integer": {
        "examples": [
            {"call": "reverse(-120)", "expect": "-21"},
            {"call": "reverse(1534236469)", "expect": "0"},
        ],
        "approaches": {
            "String reversal, range check": {
                "idea": [
                    "Reverse the digits of <code>abs(x)</code> as a string, put the sign back, and check the 32-bit range afterwards.",
                    "Python integers do not overflow, so the check can simply be done on the finished number.",
                ],
                "steps": [
                    "Set <code>sign</code> to −1 for negative <code>x</code>, else 1.",
                    "Reverse <code>str(abs(x))</code> with <code>[::-1]</code> and parse it with <code>int</code>; leading zeros vanish.",
                    "Multiply by <code>sign</code>.",
                    "Return the result if it lies in <code>[-2<sup>31</sup>, 2<sup>31</sup> − 1]</code>, otherwise 0.",
                ],
                "why": [
                    "Reversing the digit string is reversing the number, and <code>int</code> drops the zeros that were trailing in <code>x</code>.",
                    "The work is proportional to the number of digits: <strong>O(digits)</strong> time.",
                    "The temporary strings are <strong>O(digits)</strong> space.",
                ],
                "dry": [
                    [
                        "sign = −1, abs(x) = 120.",
                        "\"120\" reversed is \"021\", which parses to 21.",
                        "With the sign: −21, inside the range.",
                        "It returns <strong>-21</strong>.",
                    ],
                    [
                        "sign = 1, \"1534236469\" reversed is \"9646324351\".",
                        "That is 9,646,324,351.",
                        "It is above 2<sup>31</sup> − 1 = 2,147,483,647.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why work on <code>abs(x)</code>?",
                     "Reversing \"-123\" would put the minus sign at the end. Handling the sign separately avoids that."],
                    ["Is checking after the fact allowed?",
                     "In Python it is safe. The problem says to assume a 32-bit environment, which is why interviewers ask for the pop-and-push version."],
                    ["What about 0?",
                     "\"0\" reversed is \"0\", and the result is 0."],
                ],
            },
            "Pop and push digits, check before overflowing": {
                "idea": [
                    "Pop the last digit with <code>divmod(n, 10)</code> and push it onto <code>result</code> with <code>result * 10 + digit</code>.",
                    "Before pushing, check that the new value would still fit; that way no intermediate number ever exceeds 32 bits.",
                ],
                "steps": [
                    "Pick <code>limit</code>: 2<sup>31</sup> − 1 for non-negative <code>x</code>, 2<sup>31</sup> for negative.",
                    "Work on <code>n = abs(x)</code> with <code>result = 0</code>.",
                    "While <code>n</code>: <code>n, digit = divmod(n, 10)</code>.",
                    "If <code>result &gt; (limit - digit) // 10</code>, pushing would exceed the limit: return 0.",
                    "Otherwise <code>result = result * 10 + digit</code>. At the end, restore the sign.",
                ],
                "why": [
                    "<code>result * 10 + digit &lt;= limit</code> is equivalent to <code>result &lt;= (limit - digit) // 10</code> for integers, so the check rejects exactly the overflowing pushes.",
                    "Each loop pops one digit: <strong>O(digits)</strong> time.",
                    "A few integers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "limit = 2<sup>31</sup>, n = 120.",
                        "Pop 0: result 0. Pop 2: result 2.",
                        "Pop 1: result 21. Every check passes easily.",
                        "x was negative: <strong>-21</strong>.",
                    ],
                    [
                        "limit = 2<sup>31</sup> − 1. Pops 9, 6, 4, 3, 2, 4, 3, 2, 5 build 964632435.",
                        "The last digit is 1; (limit − 1) // 10 = 214748364.",
                        "964632435 &gt; 214748364, so pushing would overflow.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the limit 2<sup>31</sup> for negative numbers?",
                     "The 32-bit range is asymmetric: −2<sup>31</sup> fits but +2<sup>31</sup> does not. The magnitude of a negative result may reach 2<sup>31</sup>."],
                    ["Why <code>(limit - digit) // 10</code> instead of computing <code>result * 10 + digit</code>?",
                     "In a 32-bit language that product could itself overflow before you compare it. Rearranging keeps every intermediate value in range."],
                    ["Why use <code>abs(x)</code> with <code>divmod</code>?",
                     "Python's <code>divmod</code> floors towards −∞, so on negatives it gives digits like 7 for −123 % 10. Working on the magnitude avoids that."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ bitwise AND of range
    "bitwise-and-range": {
        "examples": [
            {"call": "range_bitwise_and(26, 30)", "expect": "24"},
            {"call": "range_bitwise_and(1, 2147483647)", "expect": "0"},
        ],
        "approaches": {
            "AND every number": {
                "idea": [
                    "Apply the definition: AND <code>left</code>, <code>left + 1</code>, …, <code>right</code> together.",
                    "AND can only clear bits, so once the result is 0 it stays 0 and the loop can stop.",
                ],
                "steps": [
                    "Set <code>result = left</code>.",
                    "Loop <code>x</code> from <code>left + 1</code> to <code>right</code>.",
                    "Do <code>result &amp;= x</code>.",
                    "If <code>result == 0</code>, <code>break</code>.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "It is the definition, so it is correct.",
                    "Up to <code>right - left</code> ANDs: <strong>O(right − left)</strong> time, which can be billions without the early exit.",
                    "<strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "result = 26 (11010).",
                        "&amp; 27 (11011) = 26.",
                        "&amp; 28 (11100) = 24 (11000).",
                        "&amp; 29 and &amp; 30 keep 24.",
                        "It returns <strong>24</strong>.",
                    ],
                    [
                        "result = 1.",
                        "&amp; 2 = 0.",
                        "result is 0, so it breaks after one step instead of two billion.",
                        "It returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the early exit safe?",
                     "AND never sets a bit, so after reaching 0 every further AND gives 0."],
                    ["When is this approach too slow?",
                     "When the range is huge and the result stays non-zero for long, e.g. [2<sup>30</sup>, 2<sup>31</sup> − 1] keeps bit 30 set the whole way."],
                    ["Does starting at <code>left</code> handle <code>left == right</code>?",
                     "Yes. The loop is empty and <code>left</code> is returned."],
                ],
            },
            "Shift both until they match": {
                "idea": [
                    "Between <code>left</code> and <code>right</code> every lower bit flips at some point, so only the <strong>common binary prefix</strong> of the two survives the AND.",
                    "Find that prefix by shifting both right until they are equal, then shift it back into place with zeros below.",
                ],
                "steps": [
                    "Set <code>shift = 0</code>.",
                    "While <code>left != right</code>, shift both right by one and add 1 to <code>shift</code>.",
                    "Now <code>left</code> is the common prefix.",
                    "Return <code>left &lt;&lt; shift</code>.",
                ],
                "why": [
                    "Below the first differing bit, the range contains a number with a 0 in every position (just after <code>right</code>'s prefix bit flips), so those bits are all 0 in the AND.",
                    "The common prefix is shared by every number in the range, so it survives.",
                    "At most 32 shifts: <strong>O(32)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "26 = 11010, 30 = 11110.",
                        "Shift 1: 1101 and 1111. Shift 2: 110 and 111.",
                        "Shift 3: 11 and 11, equal.",
                        "11 &lt;&lt; 3 = 11000.",
                        "It returns <strong>24</strong>.",
                    ],
                    [
                        "1 and 2<sup>31</sup> − 1 (31 ones).",
                        "After one shift left is 0; right is still 30 ones.",
                        "It takes 31 shifts for right to reach 0 as well.",
                        "0 &lt;&lt; 31 = <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does any differing bit wipe out everything below it?",
                     "If <code>left</code> has 0 and <code>right</code> has 1 at bit k, the number with the prefix, a 1 at k and zeros below lies in the range, and so does the one just before it, with all ones below k and 0 at k. Together they clear bits k and lower."],
                    ["What if <code>left == right</code>?",
                     "The loop does not run and the number itself is returned."],
                    ["Why is this O(32) and not O(log(right − left))?",
                     "It shifts until the prefixes match, which depends on where the first differing bit is; that can be bit 30 even for a small range like [2<sup>30</sup> − 1, 2<sup>30</sup>]."],
                ],
            },
            "Clear right's lowest bits until it drops to left": {
                "idea": [
                    "Keep clearing the lowest set bit of <code>right</code> with <code>right &amp;= right - 1</code>. Each step removes a low bit that some number in the range has as 0.",
                    "Stop as soon as <code>right</code> is no larger than <code>left</code>: what is left is the common prefix.",
                ],
                "steps": [
                    "While <code>right &gt; left</code>:",
                    "Clear the lowest set bit: <code>right &amp;= right - 1</code>.",
                    "When the loop stops, <code>right</code> is at most <code>left</code>.",
                    "Return <code>right</code>.",
                ],
                "why": [
                    "While <code>right &gt; left</code>, the number <code>right - 1</code> is in the range and lacks <code>right</code>'s lowest set bit, so that bit cannot be in the answer.",
                    "Clearing stops at the common prefix with zeros below, the same value the shifting approach finds.",
                    "One iteration per cleared set bit: <strong>O(set bits)</strong> time, at most 32; <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "right = 30 (11110) &gt; 26.",
                        "Clear → 28 (11100), still &gt; 26.",
                        "Clear → 24 (11000), now ≤ 26.",
                        "It returns <strong>24</strong>.",
                    ],
                    [
                        "right = 2<sup>31</sup> − 1, 31 set bits.",
                        "Each step clears the lowest: 2<sup>31</sup> − 2, 2<sup>31</sup> − 4, … all still &gt; 1.",
                        "After 30 steps right = 2<sup>30</sup>; step 31 clears it to 0.",
                        "0 ≤ 1, so it returns <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the result end up below <code>left</code>?",
                     "The last clear may drop a bit that <code>left</code> has too, but that bit is still unset in some number of the range, so it really is 0 in the AND."],
                    ["Is this faster than shifting?",
                     "It runs once per set bit of <code>right</code> below the prefix rather than once per bit position, so it is never slower."],
                    ["Why not loop while <code>right != left</code>?",
                     "<code>right</code> may jump past <code>left</code> without ever equalling it, as in the first example (28 → 24, skipping 26)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum array end
    "minimum-array-end": {
        "examples": [
            {"call": "min_end(3, 4)", "expect": "6"},
            {"call": "min_end(2, 7)", "expect": "15"},
        ],
        "approaches": {
            "Step to the next superset of x, n - 1 times": {
                "idea": [
                    "The AND of all elements is <code>x</code> only if every element contains all of <code>x</code>'s bits; the first element can be <code>x</code> itself.",
                    "To keep the array small, each next element should be the smallest number above the current one that still contains <code>x</code>.",
                    "<code>(cur + 1) | x</code> is exactly that: add 1, then force <code>x</code>'s bits back on.",
                ],
                "steps": [
                    "Set <code>cur = x</code>, the first element.",
                    "Repeat <code>n - 1</code> times:",
                    "Set <code>cur = (cur + 1) | x</code>.",
                    "Return <code>cur</code>, the last element.",
                ],
                "why": [
                    "Numbers containing <code>x</code> are <code>x</code> plus some pattern in the free bits; adding 1 and OR-ing <code>x</code> moves to the next pattern in increasing order, skipping nothing.",
                    "Every element contains <code>x</code> and the first is <code>x</code>, so the AND is exactly <code>x</code>.",
                    "n − 1 steps: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "x = 4 (100), cur = 4.",
                        "Step 1: (5) | 4 = 5 (101).",
                        "Step 2: (6) | 4 = 6 (110).",
                        "It returns <strong>6</strong>: the array is [4, 5, 6].",
                    ],
                    [
                        "x = 7 (111), cur = 7.",
                        "Step 1: 8 | 7 = 15 (1111).",
                        "Every number between 7 and 15 misses a bit of 7.",
                        "It returns <strong>15</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the array be strictly increasing in the reasoning?",
                     "The problem requires it, so elements are distinct; the smallest choice at every step keeps the final one minimal."],
                    ["Why does the OR never skip a valid number?",
                     "Adding 1 carries through the forced bits, which are reset by the OR, so the free bits simply count up by one pattern each step."],
                    ["When is this too slow?",
                     "n can be up to 10<sup>8</sup>, so n steps may be too many; the bit-depositing approach does it in O(log n)."],
                ],
            },
            "Deposit the bits of n - 1 into x's zero bits": {
                "idea": [
                    "The valid numbers are <code>x</code> with some pattern in its zero bits, and in increasing order those patterns count 0, 1, 2, …",
                    "So the n-th number (counting from 0) puts the binary digits of <code>n - 1</code> into <code>x</code>'s zero positions, lowest first.",
                ],
                "steps": [
                    "Set <code>k = n - 1</code>, <code>result = x</code> and <code>bit = 1</code>.",
                    "While <code>k</code> has bits left: if <code>bit</code> is a free position (<code>not x &amp; bit</code>), copy <code>k</code>'s lowest bit there and shift <code>k</code> right.",
                    "If <code>bit</code> is taken by <code>x</code>, skip it without touching <code>k</code>.",
                    "Move to the next position: <code>bit &lt;&lt;= 1</code>.",
                    "Return <code>result</code>.",
                ],
                "why": [
                    "Comparing two supersets of <code>x</code> means comparing their free-bit patterns read as binary numbers, so the k-th smallest uses the pattern k.",
                    "The loop runs over <code>k</code>'s bits plus the occupied bits of <code>x</code> skipped on the way: <strong>O(log n + log x)</strong> time.",
                    "A few integers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "k = 2 (10), x = 100, result = 100.",
                        "bit 1: free; k's low bit is 0, k becomes 1.",
                        "bit 2: free; k's low bit is 1, so result = 110; k becomes 0.",
                        "It returns <strong>6</strong>.",
                    ],
                    [
                        "k = 1, x = 111, result = 111.",
                        "bits 1, 2, 4 are all taken by x, skipped.",
                        "bit 8: free; k's bit is 1, result = 1111, k = 0.",
                        "It returns <strong>15</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>n - 1</code> and not <code>n</code>?",
                     "The first element uses pattern 0 (x itself), so the n-th element uses pattern n − 1."],
                    ["Why is <code>k</code> shifted only at free positions?",
                     "Each bit of <code>k</code> must land in a free slot. Taken slots belong to <code>x</code> and must stay 1."],
                    ["Is this the same idea as the PDEP CPU instruction?",
                     "Yes: it deposits the bits of one number into the zero positions of a mask, in order."],
                ],
            },
        },
    },
}
