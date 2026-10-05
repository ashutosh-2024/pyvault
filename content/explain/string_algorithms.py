"""Write-ups for the String Algorithms topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ first occurrence
    "find-first-occurrence": {
        "example": {"call": 'str_str("abxabcabcaby", "abcaby")', "expect": "6"},
        "approaches": {
            "Try every starting position": {
                "idea": [
                    "Place the needle at every possible start in the haystack and compare it character by character.",
                    "The first start where all characters match is the answer.",
                ],
                "steps": [
                    "For each <code>i</code> from 0 to <code>n - m</code>, compare <code>haystack[i:i+m]</code> with the needle.",
                    "Return the first <code>i</code> that matches, or -1.",
                ],
                "why": [
                    "Every possible position is checked in order, so the first match is found.",
                    "On repetitive inputs like \"aaaa…ab\", almost every start matches for a long way before failing: O(n·m) time, O(1) extra space.",
                ],
                "dry": [
                    "i=0: \"abxabc\" fails at x. i=1 and i=2 fail at once.",
                    "i=3: \"abcabc\" matches five characters, then fails on the last (c ≠ y). This wasted work is what KMP avoids.",
                    "i=4 and i=5 fail at once.",
                    "i=6: \"abcaby\" matches fully, so the result is <strong>6</strong>.",
                ],
            },
            "KMP with the prefix function": {
                "idea": [
                    "Brute force forgets everything on a mismatch. KMP remembers how much of the needle still matches the text that was just read.",
                    "For each needle prefix, the prefix function <code>pi</code> stores the length of its longest proper border: the longest part that is both a prefix and a suffix.",
                    "On a mismatch after k matched characters, the last <code>pi[k-1]</code> text characters still equal the needle's start, so continue from there instead of restarting.",
                ],
                "steps": [
                    "Build <code>pi</code> for the needle with the same scan, matching the needle against itself.",
                    "Scan the haystack once with <code>k</code> = characters currently matched.",
                    "On a mismatch, fall back with <code>k = pi[k-1]</code> until it matches or k is 0; on a match, <code>k += 1</code>.",
                    "When <code>k == m</code>, the match ends at i, so return <code>i - m + 1</code>.",
                ],
                "why": [
                    "Falling back to a border never skips a possible match, because any match must start at a border of what has been read.",
                    "The text pointer never moves back, and k falls at most as often as it rose: O(n + m) time, O(m) space for <code>pi</code>.",
                ],
                "dry": [
                    "For \"abcaby\", pi = [0, 0, 0, 1, 2, 0]; for example \"abcab\" has the border \"ab\", so pi[4] = 2.",
                    "Text a, b give k = 2. At x, the expected c fails: fall back to k = pi[1] = 0, and x ≠ a, so k = 0.",
                    "Text a, b, c, a, b (indices 3..7) give k = 5, so \"abcab\" is matched.",
                    "Index 8 is c, but y was expected. Fall back to k = pi[4] = 2, since the \"ab\" just read is still a match. Now c matches needle[2], so k = 3.",
                    "Indices 9..11 (a, b, y) give k = 6 = m.",
                    "The match ends at 11, so the result is 11 - 6 + 1 = <strong>6</strong>. The text pointer never went backwards.",
                ],
            },
            "Rabin-Karp rolling hash": {
                "idea": [
                    "Turn every length-m window into a number (a polynomial hash) and compare numbers instead of strings.",
                    "Sliding the window by one changes the hash in O(1): remove the leftmost character's term, shift, and add the new character.",
                    "Equal hashes almost always mean equal strings; checking the substring on a hash hit rules out the rare collision.",
                ],
                "steps": [
                    "Pick a large prime modulus 2<sup>61</sup> - 1 and a random base B; precompute <code>top = B^(m-1)</code>.",
                    "Hash the needle and the first window.",
                    "At each start: if the hashes are equal and the substring really matches, return i.",
                    "Roll: <code>hw = ((hw - s[i]·top)·B + s[i+m]) mod MOD</code>.",
                ],
                "why": [
                    "The verification step means a wrong answer is impossible; only the running time depends on luck.",
                    "A random base makes collisions astronomically rare: O(n + m) expected time and O(1) extra space.",
                ],
                "dry": [
                    "The needle \"abcaby\" and the window \"abxabc\" (start 0) get hashes; they differ, so no string comparison is needed.",
                    "Each roll drops the left character and adds the next: windows bxabca, xabcab, abcabc, bcabca, cabcab are all different from the needle.",
                    "At start 3 (\"abcabc\") brute force compared five characters; here one number comparison rejects it.",
                    "At start 6 the window is \"abcaby\": the hashes are equal, the substring check confirms it, and the result is <strong>6</strong>.",
                ],
            },
            "Z-function on pattern + separator + text": {
                "idea": [
                    "<code>z[i]</code> is the length of the longest common prefix of the whole string and the suffix starting at i.",
                    "Build <code>needle + \"\\0\" + haystack</code>. A position in the haystack part with <code>z[i] ≥ m</code> means the needle starts there.",
                    "The separator stops any match from running past the needle.",
                    "The Z algorithm reuses a box <code>[l, r)</code>, the rightmost segment known to equal a prefix, to get most z values without comparing.",
                ],
                "steps": [
                    "Compute z for the combined string. If i lies inside the box, start from <code>min(r - i, z[i - l])</code>, a free lower bound.",
                    "Extend by direct comparison and move the box if it reaches further right.",
                    "Return <code>i - m - 1</code> for the first haystack position with <code>z[i] ≥ m</code>.",
                ],
                "why": [
                    "Each successful comparison pushes r right, and r never decreases: O(n + m) time and space.",
                ],
                "dry": [
                    "The combined string is \"abcaby\\0abxabcabcaby\"; haystack index h sits at position h + 7.",
                    "Position 7 (h=0): \"ab\" matches, then x ≠ c, so z = 2.",
                    "Position 10 (h=3): \"abcab\" matches, then c ≠ y, so z = 5, and the box becomes [10, 15).",
                    "Positions 11 and 12 are inside the box and reuse z[1] = z[2] = 0; one comparison each confirms 0.",
                    "Position 13 is inside the box: start at min(15 - 13, z[3] = 2) = 2 for free, then compare c, a, b, y, giving z = 6.",
                    "6 ≥ m, so the result is 13 - 6 - 1 = <strong>6</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotate string
    "rotate-string": {
        "example": {"call": 'rotate_string("abcde", "cdeab")', "expect": "True"},
        "approaches": {
            "Build every rotation": {
                "idea": [
                    "A shift moves the first character to the end, so after i shifts the string is <code>s[i:] + s[:i]</code>.",
                    "There are only n different rotations, so build each one and compare it with <code>goal</code>.",
                ],
                "steps": [
                    "The lengths must be equal first.",
                    "For each i, test <code>s[i:] + s[:i] == goal</code>.",
                    "<code>any</code> stops at the first match.",
                ],
                "why": [
                    "It enumerates every reachable string, so it is correct.",
                    "There are n rotations of O(n) each: O(n²) time, O(n) space.",
                ],
                "dry": [
                    "The lengths match (5 and 5).",
                    "i=0: \"abcde\" ≠ goal. i=1: \"bcdea\" ≠ goal.",
                    "i=2: \"cdeab\" == goal, so the result is <strong>True</strong>.",
                ],
            },
            "Substring of s + s": {
                "idea": [
                    "Writing s twice in a row contains every rotation of s as a length-n window.",
                    "So <code>goal</code> is a rotation exactly when it has the same length and appears inside <code>s + s</code>.",
                ],
                "steps": [
                    "Check <code>len(s) == len(goal)</code>.",
                    "Return <code>goal in s + s</code>.",
                ],
                "why": [
                    "Window i of s + s is <code>s[i:] + s[:i]</code>, rotation i.",
                    "The length check matters: without it, \"a\" would be found inside \"aa\".",
                    "Python's substring search is fast in practice; KMP on s + s would give a guaranteed O(n).",
                ],
                "dry": [
                    "s + s = \"abcdeabcde\".",
                    "\"cdeab\" appears at index 2, which is two shifts.",
                    "The lengths are equal too, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ repeated string match
    "repeated-string-match": {
        "example": {"call": 'repeated_string_match("abcd", "cdabcdab")', "expect": "3"},
        "approaches": {
            "Keep appending until it is long enough": {
                "idea": [
                    "b can only fit inside a repetition of a that is at least as long as b.",
                    "With the smallest such count q, b either fits in q copies or, if it starts near the end of a copy, in q + 1 copies.",
                    "If it does not fit in q + 1 copies, more copies cannot help, because the text just repeats.",
                ],
                "steps": [
                    "Append copies of a until the text is at least <code>len(b)</code> long, counting copies.",
                    "If b is in the text, return the count.",
                    "If b is in the text plus one more copy, return count + 1; otherwise return -1.",
                ],
                "why": [
                    "Any match starts within the first copy of a, so it ends within q + 1 copies.",
                    "It does two substring searches over O(n + m) text: O((n + m)·m) worst case with naive search.",
                ],
                "dry": [
                    "text = \"abcd\" (1 copy) is shorter than 8, so append: \"abcdabcd\" (2 copies, length 8).",
                    "\"cdabcdab\" is not inside \"abcdabcd\"; it would need to start at index 2 and run past the end.",
                    "Add one more copy: \"abcdabcdabcd\" contains it at index 2, so the result is <strong>3</strong>.",
                ],
            },
            "KMP over the repeated text without building it": {
                "idea": [
                    "Same bound: at most q + 1 copies are ever needed.",
                    "Instead of building the long string, run KMP over a <em>virtual</em> text whose character i is <code>a[i % len(a)]</code>.",
                    "When KMP completes a match ending at i, that end lies in copy number <code>i // len(a) + 1</code>.",
                ],
                "steps": [
                    "Build the prefix function of b.",
                    "<code>q = ceil(len(b) / len(a))</code>.",
                    "Scan i over <code>(q + 1)·len(a)</code> virtual positions with the usual KMP step.",
                    "On <code>k == len(b)</code>, return <code>i // len(a) + 1</code>; after the loop, return -1.",
                ],
                "why": [
                    "KMP reads the text once without moving back, so the virtual text works as well as a real one.",
                    "It takes O(n + m) time and O(m) memory, no matter how many copies are needed.",
                ],
                "dry": [
                    "For b = \"cdabcdab\", pi = [0, 0, 0, 0, 1, 2, 3, 4], and q = 2, so scan 12 virtual characters.",
                    "i=0 (a) and i=1 (b) do not match c, so k stays 0.",
                    "i=2..9 read c, d, a, b, c, d, a, b, and k climbs to 8 = len(b).",
                    "The match ends at i=9, which is in copy 9 // 4 + 1 = <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ repeated substring pattern
    "repeated-substring-pattern": {
        "example": {"call": 'repeated_substring_pattern("abaababaab")', "expect": "True"},
        "approaches": {
            "Try every divisor length": {
                "idea": [
                    "If s is a block repeated several times, the block's length L divides n and is at most n/2.",
                    "So for each such L, check whether repeating <code>s[:L]</code> rebuilds s.",
                ],
                "steps": [
                    "For L from 1 to n // 2, skip lengths that do not divide n.",
                    "Test <code>s[:L] * (n // L) == s</code>.",
                    "Return whether any L works.",
                ],
                "why": [
                    "The candidate units are exactly the prefixes whose length divides n.",
                    "Each test is O(n) and there are d(n) divisors: O(n·d(n)) time, O(n) space.",
                ],
                "dry": [
                    "n = 10, so the divisors to try are 1, 2 and 5.",
                    "L=1: \"a\" × 10 ≠ s. L=2: \"ab\" × 5 = \"ababababab\" ≠ s.",
                    "L=3 and L=4 do not divide 10 and are skipped.",
                    "L=5: \"abaab\" × 2 = \"abaababaab\" = s, so the result is <strong>True</strong>.",
                ],
            },
            "s is inside (s + s) with the ends cut off": {
                "idea": [
                    "If s repeats with period p, rotating it by p gives s back. So s appears inside s + s at offset p, not just at 0 and n.",
                    "Cutting the first and last character of s + s removes the two trivial occurrences at 0 and n.",
                    "The converse is also true: a string equal to one of its non-trivial rotations is periodic. So this one-liner is a complete test.",
                ],
                "steps": [
                    "Build <code>(s + s)[1:-1]</code>.",
                    "Return whether s occurs in it.",
                ],
                "why": [
                    "Any occurrence at an offset strictly between 0 and n is a non-trivial rotation equal to s.",
                    "It is one substring search: linear in practice, O(n) space.",
                ],
                "dry": [
                    "s + s = \"abaababaababaababaab\".",
                    "Cutting the ends gives \"baababaababaababaa\".",
                    "s appears at index 4 of the cut string, which is offset 5 in s + s: one period.",
                    "So the result is <strong>True</strong>.",
                ],
            },
            "Shortest period from the prefix function": {
                "idea": [
                    "If s has a border of length b (a proper prefix that is also a suffix), then s has period p = n - b.",
                    "The longest border <code>pi[-1]</code> gives the shortest period.",
                    "s is a whole repetition of a block exactly when a border exists and that shortest period divides n. The block is <code>s[:p]</code>.",
                ],
                "steps": [
                    "Compute the prefix function of s.",
                    "<code>period = n - pi[-1]</code>.",
                    "Return <code>pi[-1] &gt; 0 and n % period == 0</code>.",
                ],
                "why": [
                    "Border length b means <code>s[i] = s[i + p]</code> for every valid i, which is the definition of period p.",
                    "If p divides n, the copies tile s exactly. It runs in O(n) time and space.",
                ],
                "dry": [
                    "Scanning \"abaababaab\" gives pi = [0, 0, 1, 1, 2, 3, 2, 3, 4, 5].",
                    "One fallback happens at i=3: a ≠ b, so k = pi[0] = 0, then a matches, giving 1.",
                    "Another happens at i=6: b ≠ a, so k = pi[2] = 1, then b matches, giving 2.",
                    "pi[-1] = 5, so the period is 10 - 5 = 5, and 10 % 5 == 0.",
                    "The result is <strong>True</strong>, and the block is \"abaab\".",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest happy prefix
    "longest-happy-prefix": {
        "example": {"call": 'longest_prefix("ababab")', "expect": '"abab"'},
        "approaches": {
            "Try every length, longest first": {
                "idea": [
                    "A happy prefix of length L means <code>s[:L] == s[-L:]</code> with L &lt; n.",
                    "Try lengths from longest to shortest; the first that works is the answer.",
                ],
                "steps": [
                    "For L from n - 1 down to 1, compare <code>s[:L]</code> with <code>s[-L:]</code>.",
                    "Return the first match, or \"\".",
                ],
                "why": [
                    "Going longest first means the first match is the longest.",
                    "There are n comparisons of up to O(n) each: O(n²) time, O(n) space.",
                ],
                "dry": [
                    "L=5: \"ababa\" vs \"babab\", no.",
                    "L=4: \"abab\" vs \"abab\", yes.",
                    "The result is <strong>\"abab\"</strong>.",
                ],
            },
            "Prefix function": {
                "idea": [
                    "The prefix function stores, for every prefix, the length of its longest proper border.",
                    "Its last entry is the longest border of the whole string, which is exactly a happy prefix.",
                ],
                "steps": [
                    "Run the standard prefix-function scan: extend k on a match, fall back <code>k = pi[k-1]</code> on a mismatch.",
                    "Return <code>s[:pi[-1]]</code>.",
                ],
                "why": [
                    "Every fallback step lands on the next shorter border, so pi values are always the longest borders.",
                    "It takes O(n) time and O(n) space.",
                ],
                "dry": [
                    "i=1 (b): no match, pi[1] = 0.",
                    "i=2 (a) matches s[0], so k = 1. i=3 (b) matches s[1], k = 2. i=4: k = 3. i=5: k = 4.",
                    "pi = [0, 0, 1, 2, 3, 4], and pi[-1] = 4.",
                    "The result is <strong>\"abab\"</strong>.",
                ],
            },
            "Prefix and suffix hashes grown together": {
                "idea": [
                    "For each length L, keep a hash of the first L characters and a hash of the last L characters.",
                    "Grow the prefix hash forwards (<code>h·B + c</code>) and the suffix hash backwards (<code>c·B^L + h</code>), so both use the same polynomial.",
                    "When they agree, the prefix and suffix are (almost certainly) equal; remember the largest such L.",
                ],
                "steps": [
                    "For L from 1 to n - 1: update <code>pre</code> with <code>s[L-1]</code> and <code>suf</code> with <code>s[-L]</code>.",
                    "If <code>pre == suf</code>, set <code>best = L</code>.",
                    "Return <code>s[:best]</code>.",
                ],
                "why": [
                    "Equal strings always give equal hashes; unequal ones collide only with negligible probability under a random base and a 61-bit modulus.",
                    "It takes O(n) time and O(1) extra space, but is correct only with high probability.",
                ],
                "dry": [
                    "L=1: \"a\" vs \"b\", the hashes differ.",
                    "L=2: \"ab\" vs \"ab\", equal, so best = 2.",
                    "L=3: \"aba\" vs \"bab\", they differ.",
                    "L=4: \"abab\" vs \"abab\", equal, so best = 4. L=5: \"ababa\" vs \"babab\", they differ.",
                    "The result is <strong>\"abab\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ shortest palindrome
    "shortest-palindrome": {
        "example": {"call": 'shortest_palindrome("aacecaaa")', "expect": '"aaacecaaa"'},
        "approaches": {
            "Longest palindromic prefix by direct check": {
                "idea": [
                    "Characters can only be added in front, so the original s must end up as the tail of the palindrome.",
                    "The fewest additions come from keeping the longest prefix of s that is already a palindrome.",
                    "Then mirror the leftover tail in front: the answer is <code>reverse(s[L:]) + s</code>.",
                ],
                "steps": [
                    "For L from n down to 1, test whether <code>s[:L]</code> equals its reverse.",
                    "At the first palindrome, return <code>s[L:][::-1] + s</code>.",
                ],
                "why": [
                    "Any shorter answer would imply a longer palindromic prefix.",
                    "There are up to n checks of O(n) each: O(n²) time, O(n) space.",
                ],
                "dry": [
                    "L=8: \"aacecaaa\" reversed is \"aaacecaa\", not a palindrome.",
                    "L=7: \"aacecaa\" is a palindrome.",
                    "The leftover tail is s[7:] = \"a\"; reversed it is \"a\".",
                    "The result is \"a\" + s = <strong>\"aaacecaaa\"</strong>.",
                ],
            },
            "KMP border of s + # + reverse(s)": {
                "idea": [
                    "A prefix of s is a palindrome exactly when it equals the same-length suffix of <code>reverse(s)</code>.",
                    "So the longest palindromic prefix is the longest border of <code>s + \"#\" + reverse(s)</code>.",
                    "The <code>#</code> keeps the border from spilling across the middle, so it is at most n long.",
                ],
                "steps": [
                    "Build <code>t = s + \"#\" + s[::-1]</code>.",
                    "Compute the prefix function of t.",
                    "<code>L = pi[-1]</code>; return <code>s[L:][::-1] + s</code>.",
                ],
                "why": [
                    "A border of t is a prefix of s matching a suffix of reverse(s), which is a palindromic prefix of s.",
                    "One prefix-function pass gives O(n) time and space.",
                ],
                "dry": [
                    "t = \"aacecaaa#aaacecaa\".",
                    "The scan's final value pi[-1] is 7, because \"aacecaa\" is both a prefix and a suffix of t.",
                    "So the longest palindromic prefix has length 7.",
                    "The result is reverse(\"a\") + s = <strong>\"aaacecaaa\"</strong>.",
                ],
            },
            "Forward and backward rolling hash": {
                "idea": [
                    "A prefix is a palindrome when reading it forwards and backwards gives the same string.",
                    "Keep a forward hash and a backward hash of the growing prefix; when they match, the prefix is (almost certainly) a palindrome.",
                    "Keep the largest such length, then mirror the leftover tail.",
                ],
                "steps": [
                    "For each character: <code>fwd = fwd·B + c</code>, <code>bwd = bwd + c·B^i</code>.",
                    "If they are equal, set <code>best = i + 1</code>.",
                    "Return <code>s[best:][::-1] + s</code>.",
                ],
                "why": [
                    "fwd hashes the prefix left to right and bwd hashes it right to left with the same base, so equal hashes mean a palindrome, up to collisions.",
                    "It takes O(n) time and O(1) extra space, and is correct with high probability.",
                ],
                "dry": [
                    "Lengths 1 (\"a\") and 2 (\"aa\") are palindromes, so best becomes 2.",
                    "Lengths 3 to 6 (\"aac\", \"aace\", \"aacec\", \"aaceca\") are not.",
                    "Length 7 (\"aacecaa\") is a palindrome, so best = 7. Length 8 is not.",
                    "The result is <strong>\"aaacecaaa\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sum of scores
    "sum-of-scores-of-built-strings": {
        "example": {"call": 'sum_scores("babab")', "expect": "9"},
        "approaches": {
            "Compare every suffix with the string": {
                "idea": [
                    "The strings s<sub>i</sub> built by prepending are exactly the suffixes of the final string.",
                    "So each score is the longest common prefix of the whole string and one of its suffixes.",
                    "Compute each one by comparing character by character.",
                ],
                "steps": [
                    "For each start i, count how many characters <code>s[k] == s[i + k]</code> match from the start.",
                    "Add that count to the total.",
                ],
                "why": [
                    "It computes each score directly from its definition.",
                    "A string like \"aaaa\" makes every comparison run long: O(n²) time, O(1) space.",
                ],
                "dry": [
                    "i=0: the whole string matches itself, 5.",
                    "i=1: \"abab\" vs \"babab\", the first characters differ, 0.",
                    "i=2: \"bab\" matches \"bab…\" for 3.",
                    "i=3: \"ab\", 0. i=4: \"b\", 1.",
                    "The total is 5 + 0 + 3 + 0 + 1 = <strong>9</strong>.",
                ],
            },
            "Z-function": {
                "idea": [
                    "The scores are exactly the Z-array: <code>z[i]</code> is the LCP of s and its suffix starting at i.",
                    "The Z algorithm keeps a box <code>[l, r)</code> known to equal a prefix of s, and inside it copies <code>z[i - l]</code> as a free starting value.",
                ],
                "steps": [
                    "<code>z[0] = n</code>.",
                    "For each i: inside the box, start at <code>min(r - i, z[i - l])</code>; then extend by comparison.",
                    "If the match reaches past r, move the box to <code>[i, i + z[i])</code>.",
                    "Return <code>sum(z)</code>.",
                ],
                "why": [
                    "Successful comparisons always push r right, and r is at most n, so the total work is O(n). Space is O(n).",
                ],
                "dry": [
                    "z[0] = 5.",
                    "i=1: s[0] = b vs s[1] = a, so z[1] = 0.",
                    "i=2: b, a, b match, then the string ends, so z[2] = 3 and the box becomes [2, 5).",
                    "i=3 is inside the box: z[1] = 0 gives a start of 0; one comparison (b vs a) confirms 0.",
                    "i=4 is inside the box: start at min(5 - 4, z[2] = 3) = 1, already at the end, so z[4] = 1 with no comparisons.",
                    "The sum is 5 + 0 + 3 + 0 + 1 = <strong>9</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest duplicate substring
    "longest-duplicate-substring": {
        "example": {"call": 'longest_dup_substring("banana")', "expect": '"ana"'},
        "approaches": {
            "Every length, set of substrings": {
                "idea": [
                    "Try lengths from longest to shortest. For each length, look for any window seen twice.",
                    "A set of the windows seen so far spots the first repeat.",
                ],
                "steps": [
                    "For L from n - 1 down to 1, start an empty set.",
                    "For each window <code>s[i:i+L]</code>: if it is already in the set, return it; otherwise add it.",
                    "Return \"\" if no length has a repeat.",
                ],
                "why": [
                    "Longest first means the first repeat found is a longest one.",
                    "There are O(n²) windows, each sliced and hashed in O(L): O(n³) time and O(n²) space.",
                ],
                "dry": [
                    "L=5: \"banan\" and \"anana\" are different.",
                    "L=4: \"bana\", \"anan\", \"nana\" are all different.",
                    "L=3: \"ban\", \"ana\", \"nan\", then \"ana\" again at index 3, already in the set.",
                    "The result is <strong>\"ana\"</strong>.",
                ],
            },
            "Binary search on length + rolling hash": {
                "idea": [
                    "If some length L has a duplicate, every shorter length does too (take a piece of it). So \"has a duplicate of length L\" is monotonic, and the largest such L can be binary-searched.",
                    "<code>check(L)</code> rolls a hash over all windows of length L, remembers each window's start by its hash, and compares real substrings on a hash hit.",
                ],
                "steps": [
                    "Binary search L in [1, n - 1]; keep the substring found for the largest L that works.",
                    "<code>check(L)</code>: hash the first window, then roll; on a repeated hash, compare the actual substrings so a collision can never cause a wrong answer.",
                    "If <code>check(mid)</code> finds a duplicate, search longer; otherwise search shorter.",
                ],
                "why": [
                    "Monotonicity makes binary search valid, and verifying hash hits keeps the answer exact.",
                    "There are O(log n) checks of O(n) expected time each: O(n log n) expected time and O(n) space.",
                ],
                "dry": [
                    "lo = 1, hi = 5. mid = 3: the windows ban, ana, nan, ana repeat a hash at start 3; the substring check confirms \"ana\" = \"ana\". best = \"ana\", lo = 4.",
                    "mid = (4 + 5) // 2 = 4: bana, anan, nana have no repeat, so hi = 3.",
                    "lo &gt; hi, so the search ends.",
                    "The result is <strong>\"ana\"</strong>.",
                ],
            },
        },
    },
}
