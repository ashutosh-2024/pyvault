"""Write-ups for the String Algorithms topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ first occurrence
    "find-first-occurrence": {
        "examples": [
            {"call": 'str_str("abxabcabcaby", "abcaby")', "expect": "6"},
            {"call": 'str_str("leetcode", "leeto")', "expect": "-1"},
        ],
        "approaches": {
            "Try every starting position": {
                "idea": [
                    "The needle can only start at positions <code>0</code> to <code>n - m</code>; any later start would run off the end of the haystack.",
                    "Place the needle at each of those starts in turn and compare the window with it. The first window that matches is the answer.",
                ],
                "steps": [
                    "Let <code>n, m = len(haystack), len(needle)</code>.",
                    "Loop <code>i</code> over <code>range(n - m + 1)</code>, every start that leaves room for the whole needle.",
                    "Compare the slice <code>haystack[i:i + m]</code> with <code>needle</code>.",
                    "Return <code>i</code> at the first equal slice, since starts are tried left to right.",
                    "If no start matches, return <code>-1</code>.",
                ],
                "why": [
                    "Every legal start is tried in increasing order, so the first one returned is the leftmost occurrence and none can be missed.",
                    "Each comparison can read up to m characters, and there are n − m + 1 starts, so the time is <strong>O(n·m)</strong>. Inputs like \"aaaa…ab\" with needle \"aab\" hit that bound.",
                    "Only the index is kept, so the extra space is <strong>O(1)</strong> apart from the temporary slice, which holds m characters.",
                ],
                "dry": [
                    [
                        "n = 12, m = 6, so starts 0..6 are tried.",
                        "i=0: \"abxabc\" fails at x. i=1 (\"bxabca\") and i=2 (\"xabcab\") fail at the first character.",
                        "i=3: \"abcabc\" agrees for five characters and fails on the last (c ≠ y). This wasted work is what KMP avoids.",
                        "i=4 and i=5 fail at once.",
                        "i=6: \"abcaby\" matches fully, so the result is <strong>6</strong>.",
                    ],
                    [
                        "n = 8, m = 5, so starts 0..3 are tried.",
                        "i=0: \"leetc\" agrees on l, e, e, t, then c ≠ o.",
                        "i=1 \"eetco\", i=2 \"etcod\", i=3 \"tcode\" fail at the first character.",
                        "The loop ends without a match: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>range(n - m + 1)</code> and not <code>range(n)</code>?",
                     "A start after <code>n - m</code> leaves fewer than m characters, so the slice would be shorter than the needle and could never be equal. The +1 keeps the last legal start, where the needle ends exactly at the end of the haystack."],
                    ["What if the needle is longer than the haystack?",
                     "Then <code>n - m + 1 ≤ 0</code>, the range is empty, and the function returns -1 without comparing anything."],
                    ["Is slicing slower than comparing characters in a loop?",
                     "Slicing copies m characters, but in C, so in Python it is usually faster than a hand-written character loop. Both are O(m) per start; neither changes the O(n·m) worst case."],
                ],
            },
            "KMP with the prefix function": {
                "idea": [
                    "Brute force forgets everything on a mismatch. KMP remembers how much of the needle still matches the text it has just read.",
                    "For each prefix of the needle, the prefix function <code>pi</code> stores the length of its longest proper <strong>border</strong>: the longest part that is both a prefix and a suffix of it.",
                    "After a mismatch with <code>k</code> characters matched, the last <code>pi[k-1]</code> characters read still equal the start of the needle, so matching continues from there and the text pointer never moves back.",
                ],
                "steps": [
                    "Build <code>pi</code> with <code>prefix_function(needle)</code>, which runs the same matching loop of the needle against itself.",
                    "Scan the haystack once with <code>i, ch</code>, keeping <code>k</code> = number of needle characters currently matched.",
                    "While <code>k</code> is positive and <code>ch != needle[k]</code>, fall back with <code>k = pi[k - 1]</code>.",
                    "If <code>ch == needle[k]</code>, extend the match: <code>k += 1</code>.",
                    "When <code>k == len(needle)</code>, the match ends at <code>i</code>, so return <code>i - k + 1</code>. If the scan ends first, return -1.",
                ],
                "why": [
                    "A match that starts inside the part already read must begin at a border of that part, and the fall-back chain visits every border from longest to shortest, so no start is skipped.",
                    "<code>k</code> rises by at most 1 per character and every fall-back lowers it, so the total number of fall-backs is at most n. The search is <strong>O(n)</strong>, building <code>pi</code> is O(m) by the same argument: <strong>O(n + m)</strong> overall.",
                    "The only extra memory is the <code>pi</code> array: <strong>O(m)</strong> space.",
                ],
                "dry": [
                    [
                        "pi for \"abcaby\" is [0, 0, 0, 1, 2, 0]; for example \"abcab\" has the border \"ab\", so pi[4] = 2.",
                        "i=0, 1 (a, b): k = 2. i=2 (x): expected c, fall back to k = pi[1] = 0; x ≠ a, so k stays 0.",
                        "i=3..7 (a, b, c, a, b): k climbs to 5, so \"abcab\" is matched.",
                        "i=8 (c): expected y. Fall back to k = pi[4] = 2, because the \"ab\" just read is still a prefix. Now c = needle[2], so k = 3.",
                        "i=9..11 (a, b, y): k reaches 6 = m.",
                        "The match ends at 11, so the result is 11 − 6 + 1 = <strong>6</strong>. The text pointer never went backwards.",
                    ],
                    [
                        "pi for \"leeto\" is [0, 0, 0, 0, 0]: no prefix has a border.",
                        "i=0..3 (l, e, e, t): k climbs to 4.",
                        "i=4 (c): expected o. Fall back to k = pi[3] = 0; c ≠ l, so k = 0.",
                        "i=5..7 (o, d, e): none equals needle[0] = l, so k stays 0.",
                        "The scan ends without k reaching 5: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>k = pi[k - 1]</code> and not <code>pi[k]</code>?",
                     "<code>k</code> is a length: the matched part is <code>needle[0..k-1]</code>, whose last index is <code>k - 1</code>. Its longest border is stored at <code>pi[k - 1]</code>."],
                    ["Why is the fall-back a <code>while</code> and not an <code>if</code>?",
                     "After one fall-back the next needle character may still not match, so you try the border of the border, and so on, until a match or k = 0. In \"aacecaaa#…\" a single character takes two fall-backs (2 → 1 → 0)."],
                    ["How can a while loop inside a for loop be linear?",
                     "Each fall-back strictly lowers <code>k</code>, and <code>k</code> only ever rises by 1 per character. It cannot fall more times in total than it rose, so all the inner loops together do at most n steps."],
                    ["Why does <code>prefix_function</code> start at <code>i = 1</code>?",
                     "A border must be proper, shorter than the string itself, so <code>pi[0]</code> is always 0. Starting at 1 also stops the needle from matching itself trivially."],
                ],
            },
            "Rabin-Karp rolling hash": {
                "idea": [
                    "Turn every length-m window into a number, a polynomial hash, and compare numbers instead of strings.",
                    "Sliding the window one step changes the hash in O(1): remove the leftmost character's term, multiply by the base, add the new character.",
                    "Equal hashes almost always mean equal strings; comparing the substring on a hash hit rules out the rare collision.",
                ],
                "steps": [
                    "If <code>m &gt; n</code>, return -1. Pick <code>MOD = 2<sup>61</sup> − 1</code> and a random base <code>B</code>, and set <code>top = B<sup>m−1</sup> mod MOD</code>, the weight of a window's first character.",
                    "In one loop over the first m characters, build <code>hp</code> (the needle's hash) and <code>hw</code> (the first window's hash).",
                    "For each start <code>i</code>: if <code>hw == hp</code> and <code>haystack[i:i + m] == needle</code>, return <code>i</code>.",
                    "If another window follows, roll: <code>hw = ((hw - ord(haystack[i]) * top) * B + ord(haystack[i + m])) % MOD</code>.",
                    "If no window matched, return -1.",
                ],
                "why": [
                    "A window is only returned after a real string comparison, so the answer is always correct; only the running time depends on the random base.",
                    "For a random base, two different windows share a hash with probability about m / 2<sup>61</sup>, so false hits are vanishingly rare and the expected time is <strong>O(n + m)</strong>.",
                    "Python's <code>%</code> always returns a non-negative result, so subtracting the old character never leaves a negative hash.",
                    "Only a few integers are kept: <strong>O(1)</strong> extra space, plus the m-character slice made on a hash hit.",
                ],
                "dry": [
                    [
                        "m = 6, so starts 0..6 are tried. The needle \"abcaby\" and the first window \"abxabc\" are hashed in one loop.",
                        "i=0: the hashes differ, so no string comparison is made. Roll: drop a, add c, giving the hash of \"bxabca\".",
                        "i=1..5: windows bxabca, xabcab, abcabc, bcabca and cabcab all hash differently from the needle.",
                        "At i=3 (\"abcabc\") brute force compared five characters; here a single number comparison rejects it.",
                        "i=6: the window is \"abcaby\". The hashes are equal and the slice check confirms it: <strong>6</strong>.",
                    ],
                    [
                        "m = 5 ≤ n = 8, so there are 4 windows. The needle \"leeto\" and the window \"leetc\" are hashed.",
                        "i=0: \"leetc\" differs from \"leeto\" in the last character, so its hash differs. Roll to \"eetco\".",
                        "i=1, 2, 3: \"eetco\", \"etcod\", \"tcode\" all have different hashes. At i=3, <code>i + m = n</code>, so there is no roll.",
                        "No window matched: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>haystack[i:i + m] == needle</code> when the hashes already match?",
                     "Different strings can share a hash (a collision). The check costs O(m) but only runs on hash hits, so it keeps the answer exact at almost no cost."],
                    ["Why a random base instead of a fixed one like 256?",
                     "With a fixed base and modulus, someone can build inputs that collide on purpose, forcing a slice check at every start and O(n·m) time. A random base makes that impossible to plan in advance."],
                    ["What does <code>top</code> do?",
                     "It is B<sup>m−1</sup>, the weight of the leftmost character in a window. Subtracting <code>ord(haystack[i]) * top</code> removes that character before the shift."],
                    ["Why the <code>if i + m &lt; n</code> guard?",
                     "On the last start there is no next character to add, and <code>haystack[i + m]</code> would raise an IndexError."],
                ],
            },
            "Z-function on pattern + separator + text": {
                "idea": [
                    "<code>z[i]</code> is the length of the longest common prefix of the whole string and the suffix that starts at <code>i</code>.",
                    "Build <code>needle + \"\\0\" + haystack</code>. A haystack position with <code>z[i] ≥ m</code> agrees with the first m characters, which are the needle, so the needle starts there.",
                    "The Z algorithm keeps a box <code>[l, r)</code>, the rightmost segment known to equal a prefix, and gets most z values from inside it without comparing.",
                ],
                "steps": [
                    "Compute <code>z = z_function(needle + \"\\0\" + haystack)</code>.",
                    "Inside <code>z_function</code>, if <code>i &lt; r</code>, start from <code>z[i] = min(r - i, z[i - l])</code>, a lower bound copied from the matching spot near the front.",
                    "Extend <code>z[i]</code> by direct comparison while <code>s[z[i]] == s[i + z[i]]</code>.",
                    "If <code>i + z[i] &gt; r</code>, move the box to <code>[i, i + z[i])</code>.",
                    "Scan positions <code>m + 1</code> onwards (the haystack part) and return <code>i - m - 1</code> at the first <code>z[i] ≥ m</code>; otherwise -1 (or 0 for an empty needle).",
                ],
                "why": [
                    "Inside the box, <code>s[l..r)</code> equals <code>s[0..r-l)</code>, so the text at <code>i</code> looks like the text at <code>i - l</code> up to <code>r</code>; that is why <code>z[i - l]</code> is a valid starting value.",
                    "The separator keeps the two parts apart, so with ordinary text no z value in the haystack part exceeds m. Correctness does not even depend on it: <code>z[i] ≥ m</code> at a haystack position always means the first m characters, the needle, appear there.",
                    "Every comparison that succeeds pushes <code>r</code> right and <code>r</code> never moves left, so there are O(n + m) comparisons: <strong>O(n + m)</strong> time.",
                    "The combined string and the <code>z</code> array both have n + m + 1 entries: <strong>O(n + m)</strong> space.",
                ],
                "dry": [
                    [
                        "The combined string is \"abcaby\\0abxabcabcaby\"; haystack index h sits at position h + 7.",
                        "Position 7 (h=0): \"ab\" matches, then x ≠ c, so z = 2.",
                        "Position 10 (h=3): \"abcab\" matches, then c ≠ y, so z = 5 and the box becomes [10, 15).",
                        "Positions 11 and 12 are inside the box and copy z[1] = z[2] = 0; one comparison each confirms 0.",
                        "Position 13: start at min(15 − 13, z[3] = 2) = 2 for free, then compare c, a, b, y: z = 6.",
                        "6 ≥ m, so the result is 13 − 6 − 1 = <strong>6</strong>.",
                    ],
                    [
                        "The combined string is \"leeto\\0leetcode\"; haystack index h sits at position h + 6.",
                        "Positions 1..5 (the needle and the separator) all get z = 0.",
                        "Position 6 (h=0): l, e, e, t match, then c ≠ o, so z = 4 and the box becomes [6, 10).",
                        "Positions 7..13 all get z = 0: inside the box they copy z[1..4] = 0, and the comparisons fail at once.",
                        "No z value reaches 5: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>min(r - i, z[i - l])</code> and not just <code>z[i - l]</code>?",
                     "The copy is only guaranteed up to the end of the box at <code>r</code>; beyond that nothing is known yet. The <code>min</code> trusts the copy only as far as the box reaches, and the while loop checks the rest."],
                    ["Why is the result <code>i - m - 1</code>?",
                     "The haystack starts after m needle characters and one separator, at position <code>m + 1</code>. Subtracting that offset turns the combined-string index back into a haystack index."],
                    ["What if the haystack or the needle contains <code>\\0</code> itself?",
                     "The answer is still right. Only positions after the separator are scanned, and <code>z[i] ≥ m</code> there means the first m characters, which are always the needle, start at <code>i</code>. The separator just keeps z values from running past m on normal text."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ rotate string
    "rotate-string": {
        "examples": [
            {"call": 'rotate_string("abcde", "cdeab")', "expect": "True"},
            {"call": 'rotate_string("abcde", "abced")', "expect": "False"},
        ],
        "approaches": {
            "Build every rotation": {
                "idea": [
                    "A rotation by <code>i</code> moves the first i characters to the end: <code>s[i:] + s[:i]</code>.",
                    "A string of length n has n rotations (shift 0 to n − 1), so build each and compare it with <code>goal</code>.",
                    "Different lengths can never be rotations, so check that first.",
                ],
                "steps": [
                    "If <code>len(s) != len(goal)</code>, the <code>and</code> short-circuits to <code>False</code>.",
                    "For each <code>i</code> in <code>range(max(1, len(s)))</code>, build <code>s[i:] + s[:i]</code>.",
                    "<code>any(...)</code> returns <code>True</code> at the first rotation equal to <code>goal</code>.",
                    "If none matches, <code>any</code> returns <code>False</code>.",
                ],
                "why": [
                    "Every rotation is generated exactly once, so if <code>goal</code> is a rotation it is found, and if it is found it is a rotation by construction.",
                    "<code>max(1, len(s))</code> makes the empty string try one rotation, \"\" itself, so <code>(\"\", \"\")</code> returns <code>True</code>.",
                    "There are n rotations, each built and compared in O(n): <strong>O(n²)</strong> time. Only one rotation exists at a time: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Lengths are both 5.",
                        "i=0: \"abcde\" ≠ \"cdeab\".",
                        "i=1: \"bcdea\" ≠ \"cdeab\".",
                        "i=2: \"cde\" + \"ab\" = \"cdeab\" equals goal, so <code>any</code> stops: <strong>True</strong>.",
                    ],
                    [
                        "Lengths are both 5.",
                        "The rotations are abcde, bcdea, cdeab, deabc, eabcd.",
                        "\"abced\" swaps two neighbours, which no rotation can do, so none of the five is equal.",
                        "<code>any</code> sees only <code>False</code>: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>range(max(1, len(s)))</code> instead of <code>range(len(s))</code>?",
                     "For two empty strings, <code>range(0)</code> is empty and <code>any</code> of nothing is <code>False</code>, but \"\" is a rotation of \"\". The <code>max</code> forces one check."],
                    ["Is the length check really needed?",
                     "Not for correctness: every rotation has length n, so a goal of another length fails every comparison anyway. Checking first just returns at once instead of building n rotations for nothing."],
                    ["Can I rotate only by shifts where <code>s[i] == goal[0]</code>?",
                     "That prunes many shifts in practice, but on strings like \"aaaa…ab\" every shift qualifies, so the worst case stays O(n²)."],
                ],
            },
            "Substring of s + s": {
                "idea": [
                    "Writing s twice in a row, <code>s + s</code>, lists every rotation as a window of length n: the window starting at i is <code>s[i:] + s[:i]</code>.",
                    "So <code>goal</code> is a rotation exactly when it has the same length and appears inside <code>s + s</code>.",
                ],
                "steps": [
                    "Check <code>len(s) == len(goal)</code>.",
                    "Build <code>s + s</code>, of length 2n.",
                    "Return whether <code>goal in s + s</code>; the <code>in</code> is a substring search.",
                    "With KMP or the Z-function as the search, the whole check is linear.",
                ],
                "why": [
                    "Any length-n window of <code>s + s</code> starting at i &lt; n reads <code>s[i:]</code> and then wraps into the second copy for <code>s[:i]</code>, which is exactly rotation i. A window starting at n is s itself, rotation 0.",
                    "Without the length check, any substring of s would pass: \"ab\" is inside \"abcabc\" but is not a rotation of \"abc\".",
                    "Building <code>s + s</code> is O(n) space. The search is <strong>O(n)</strong> with KMP; CPython's built-in search is not KMP but is fast in practice. Space is <strong>O(n)</strong>.",
                ],
                "dry": [
                    [
                        "Lengths match (5 and 5).",
                        "s + s = \"abcdeabcde\".",
                        "\"cdeab\" appears at index 2: c, d, e from the first copy, then a, b from the second.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "Lengths match (5 and 5).",
                        "s + s = \"abcdeabcde\".",
                        "The windows are abcde, bcdea, cdeab, deabc, eabcd, abcde: none is \"abced\".",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the length check come first?",
                     "<code>in</code> only asks for a substring. Without the check, \"ab\" would be reported as a rotation of \"abc\" because it appears in \"abcabc\"."],
                    ["Is Python's <code>in</code> really linear?",
                     "Not KMP, but CPython uses a fast search with good typical behaviour and a linear-time algorithm for long needles. In an interview, say \"substring search with KMP\" to justify the O(n) bound."],
                    ["Does it work for the empty string?",
                     "Yes: both lengths are 0 and \"\" is a substring of \"\", so it returns <code>True</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ repeated string match
    "repeated-string-match": {
        "examples": [
            {"call": 'repeated_string_match("abcd", "cdabcdab")', "expect": "3"},
            {"call": 'repeated_string_match("abc", "wxyz")', "expect": "-1"},
        ],
        "approaches": {
            "Keep appending until it is long enough": {
                "idea": [
                    "<code>b</code> can only fit inside the repeated text once that text is at least as long as <code>b</code>, so keep appending <code>a</code> until it is.",
                    "An occurrence of <code>b</code> may start anywhere inside the first copy of <code>a</code>, so it can spill one copy further: one extra copy is always enough.",
                    "If <code>b</code> is not in that text or in the text plus one more <code>a</code>, more copies cannot help.",
                ],
                "steps": [
                    "Start with <code>text = a</code> and <code>count = 1</code>.",
                    "While <code>len(text) &lt; len(b)</code>, append <code>a</code> and increase <code>count</code>.",
                    "If <code>b in text</code>, return <code>count</code>.",
                    "If <code>b in text + a</code>, return <code>count + 1</code>.",
                    "Otherwise return -1.",
                ],
                "why": [
                    "Any occurrence of <code>b</code> in some <code>a * k</code> can be shifted left by whole copies of <code>a</code> until it starts in the first copy; then it ends before <code>len(a) + len(b)</code>, which <code>count + 1</code> copies cover.",
                    "So if neither check finds <code>b</code>, no number of copies will, and -1 is correct.",
                    "The text has length O(n + m) and each <code>in</code> search can be O((n + m)·m) in the worst case: <strong>O((n + m)·m)</strong> time, <strong>O(n + m)</strong> space.",
                ],
                "dry": [
                    [
                        "text = \"abcd\" (4 &lt; 8): append, text = \"abcdabcd\", count = 2.",
                        "Length 8 is no longer below 8, so the loop stops.",
                        "\"cdabcdab\" is not in \"abcdabcd\": it would need \"ab\" after the last d.",
                        "\"cdabcdab\" is in \"abcdabcdabcd\" at index 2, so it returns count + 1 = <strong>3</strong>.",
                    ],
                    [
                        "text = \"abc\" (3 &lt; 4): append, text = \"abcabc\", count = 2.",
                        "\"wxyz\" is not in \"abcabc\".",
                        "\"wxyz\" is not in \"abcabcabc\" either: it uses letters <code>a</code> never has.",
                        "It returns <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is one extra copy always enough?",
                     "An occurrence can be moved by whole periods of <code>a</code> to start inside the first copy, at offset below <code>len(a)</code>. It then ends before <code>len(a) + len(b)</code>, and <code>count + 1</code> copies are at least that long."],
                    ["Why not just try <code>k = 1, 2, 3, …</code> forever?",
                     "Without the bound above you would not know when to stop and return -1. The bound turns an open-ended search into two checks."],
                    ["Can <code>b</code> already fit in fewer than <code>count</code> copies?",
                     "No: <code>count - 1</code> copies are shorter than <code>b</code>, because the loop stopped at the first length that is not."],
                ],
            },
            "KMP over the repeated text without building it": {
                "idea": [
                    "The repeated text is just <code>a</code> read in a cycle, so its i-th character is <code>a[i % len(a)]</code>. KMP only needs one character at a time, so the text never has to be built.",
                    "By the same bound as the simple version, <code>q + 1</code> copies are always enough, where <code>q</code> is the ceiling of <code>len(b) / len(a)</code>.",
                    "When KMP completes a match at text index <code>i</code>, the copies used are the one holding <code>i</code> and everything before it.",
                ],
                "steps": [
                    "Build the prefix function <code>pi</code> of <code>b</code>.",
                    "Set <code>q = -(-len(b) // len(a))</code>, the ceiling division, and <code>k = 0</code>.",
                    "For <code>i</code> in <code>range((q + 1) * len(a))</code>, read <code>ch = a[i % len(a)]</code>.",
                    "Run the usual KMP step: fall back with <code>k = pi[k - 1]</code> while <code>ch != b[k]</code>, then <code>k += 1</code> on a match.",
                    "When <code>k == len(b)</code>, return <code>i // len(a) + 1</code>, the number of copies up to index <code>i</code>. If the loop ends, return -1.",
                ],
                "why": [
                    "KMP finds the <em>first</em> occurrence, which ends at the smallest possible <code>i</code>, so <code>i // len(a) + 1</code> is the fewest copies.",
                    "If <code>b</code> is not in the first <code>q + 1</code> copies it is in none, by the shifting argument, so -1 is safe.",
                    "Building <code>pi</code> is O(m) and the scan reads (q + 1)·n = O(n + m) characters with amortised O(1) fall-backs each: <strong>O(n + m)</strong> time. Only <code>pi</code> is stored: <strong>O(m)</strong> space.",
                ],
                "dry": [
                    [
                        "pi for \"cdabcdab\" is [0, 0, 0, 0, 1, 2, 3, 4]. q = ceil(8 / 4) = 2, so up to 12 characters are read.",
                        "i=0, 1 (a, b): neither equals b[0] = c, so k = 0.",
                        "i=2..5 (c, d, a, b): k climbs to 4.",
                        "i=6..9 (c, d, a, b): k climbs to 8 = len(b) at i = 9.",
                        "It returns 9 // 4 + 1 = <strong>3</strong>: the match ends inside the third copy.",
                    ],
                    [
                        "pi for \"wxyz\" is [0, 0, 0, 0]. q = ceil(4 / 3) = 2, so up to 9 characters are read.",
                        "Each character is a, b or c, and none equals b[0] = w.",
                        "k stays 0 for all 9 characters.",
                        "The loop ends: <strong>-1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>-(-len(b) // len(a))</code>?",
                     "Floor division of a negated number rounds towards minus infinity, so negating twice gives the ceiling. It is the integer form of ceil(len(b) / len(a))."],
                    ["Why is the answer <code>i // len(a) + 1</code>?",
                     "Index <code>i</code> lies in copy number <code>i // len(a)</code>, counting from 0. The match needs that copy and all earlier ones, so the count is one more."],
                    ["Could a match ending later need fewer copies?",
                     "No. A later end index never lies in an earlier copy, and KMP reports the earliest end, so its copy count is the smallest."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ repeated substring pattern
    "repeated-substring-pattern": {
        "examples": [
            {"call": 'repeated_substring_pattern("abaababaab")', "expect": "True"},
            {"call": 'repeated_substring_pattern("aba")', "expect": "False"},
        ],
        "approaches": {
            "Try every divisor length": {
                "idea": [
                    "If s is a block repeated k ≥ 2 times, the block length L divides n and is at most n / 2.",
                    "So try every such L: take the first L characters and check whether repeating them <code>n // L</code> times rebuilds s.",
                ],
                "steps": [
                    "Let <code>n = len(s)</code>.",
                    "Loop <code>L</code> from 1 to <code>n // 2</code>.",
                    "Skip any <code>L</code> where <code>n % L != 0</code>, since the block would not tile s.",
                    "Otherwise test <code>s[:L] * (n // L) == s</code>.",
                    "<code>any(...)</code> returns <code>True</code> at the first block that works, or <code>False</code> if none does.",
                ],
                "why": [
                    "If s is a repetition, its block must be its first L characters, and L must divide n and be at most n / 2, so the loop tries it.",
                    "Stopping at <code>n // 2</code> excludes L = n, which is s repeated once and does not count.",
                    "Only divisors of n are rebuilt, each in O(n), and there are d(n) divisors: <strong>O(n · d(n))</strong> time. The rebuilt string takes <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 10, so L runs from 1 to 5.",
                        "L=1: \"a\" * 10 ≠ s. L=2: \"ab\" * 5 = \"ababababab\" ≠ s.",
                        "L=3 and L=4 do not divide 10, so they are skipped.",
                        "L=5: \"abaab\" * 2 = \"abaababaab\" = s, so it returns <strong>True</strong>.",
                    ],
                    [
                        "n = 3, so only L = 1 is tried.",
                        "L=1: \"a\" * 3 = \"aaa\" ≠ \"aba\".",
                        "No block works: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only up to <code>n // 2</code>?",
                     "A block must repeat at least twice, so it is at most half of s. L = n would always match and wrongly return <code>True</code> for every string."],
                    ["Why does <code>n % L != 0</code> short-circuit the comparison?",
                     "The <code>and</code> stops at a false left side, so non-divisors cost O(1) and only divisors pay for the O(n) rebuild."],
                    ["What about a single character like \"a\"?",
                     "<code>n // 2 = 0</code>, the range is empty, and <code>any</code> returns <code>False</code>, which is correct: one copy is not a repetition."],
                ],
            },
            "s is inside (s + s) with the ends cut off": {
                "idea": [
                    "s is a repetition exactly when some non-trivial rotation of s equals s itself.",
                    "<code>s + s</code> holds every rotation of s as a window; cutting off its first and last characters removes the two trivial ones (shift 0 and shift n).",
                    "So s is a repetition exactly when s still appears inside <code>(s + s)[1:-1]</code>.",
                ],
                "steps": [
                    "Build <code>s + s</code>.",
                    "Drop the first and last characters with <code>[1:-1]</code>.",
                    "Return whether <code>s</code> occurs in what is left.",
                    "The <code>in</code> search can be done with KMP in linear time.",
                ],
                "why": [
                    "If s = block repeated k ≥ 2 times with block length L, rotating by L gives s back, and that copy starts at index L − 1 of the cut string.",
                    "Conversely, if s equals its rotation by some 0 &lt; t &lt; n, then s has period t, and its smallest period divides n, so s is a repetition.",
                    "The doubled string has 2n characters and the search is linear with KMP: <strong>O(n)</strong> time, <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "s + s = \"abaababaababaababaab\" (20 characters).",
                        "Cutting the ends leaves \"baababaababaababaa\" (18 characters).",
                        "s = \"abaababaab\" appears in it at index 4, which is the rotation by 5 = the block length.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "s + s = \"abaaba\".",
                        "Cutting the ends leaves \"baab\".",
                        "\"aba\" does not appear in \"baab\".",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why cut both ends, not just one?",
                     "Cutting the first character removes the copy of s at index 0; cutting the last removes the copy at index n. Both are the trivial rotation, and either would make every string pass."],
                    ["Why does \"s equals a rotation\" imply \"s is a repetition\"?",
                     "Equal to its rotation by t means s has period t. By a classic result, the smallest period then divides n too, so the string is that block repeated n / p times."],
                    ["Is this faster than the prefix function?",
                     "Both are O(n). This one is a one-liner and leans on the built-in search; the prefix function also tells you the block itself."],
                ],
            },
            "Shortest period from the prefix function": {
                "idea": [
                    "The longest border of s, <code>pi[-1]</code>, gives the shortest period: <code>period = n - pi[-1]</code>.",
                    "s is a repetition of its first <code>period</code> characters exactly when that period divides n and is shorter than n.",
                ],
                "steps": [
                    "Compute <code>pi</code> for s with the usual loop: fall back with <code>k = pi[k - 1]</code> on a mismatch, extend <code>k</code> on a match.",
                    "Read the longest border of the whole string, <code>pi[-1]</code>.",
                    "Set <code>period = len(s) - pi[-1]</code>.",
                    "Return <code>pi[-1] &gt; 0 and len(s) % period == 0</code>.",
                ],
                "why": [
                    "A border of length b means <code>s[i] == s[i + n - b]</code> for every valid i, which is exactly a period of n − b; the longest border gives the shortest period.",
                    "If the shortest period p divides n, s is its first p characters repeated n / p times; if it does not divide n, no period that divides n exists except n itself.",
                    "<code>pi[-1] &gt; 0</code> rules out period = n, which is the whole string once. One prefix-function pass: <strong>O(n)</strong> time, <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "pi = [0, 0, 1, 1, 2, 3, 2, 3, 4, 5].",
                        "At i=3 (a), k=1 falls back to pi[0] = 0 and a matches s[0]; at i=6 (b), k=3 falls back to pi[2] = 1 and b matches s[1].",
                        "pi[-1] = 5: \"abaab\" is both a prefix and a suffix.",
                        "period = 10 − 5 = 5, and 10 % 5 == 0, so it returns <strong>True</strong>.",
                    ],
                    [
                        "pi = [0, 0, 1]: the final \"a\" matches the first.",
                        "pi[-1] = 1 &gt; 0, and period = 3 − 1 = 2.",
                        "3 % 2 = 1, so the period does not tile s.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>pi[-1] &gt; 0</code> check?",
                     "If there is no border, period = n and <code>n % n == 0</code> is true, so strings like \"ab\" or \"a\" would wrongly return <code>True</code>."],
                    ["If the shortest period does not divide n, could a longer one?",
                     "No. If some period q divided n, the smallest period p would divide q too (both are periods and p + q ≤ n), so p would divide n. One check is enough."],
                    ["How do I get the repeating block itself?",
                     "It is <code>s[:period]</code>, the first <code>n - pi[-1]</code> characters, when the function returns <code>True</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest happy prefix
    "longest-happy-prefix": {
        "examples": [
            {"call": 'longest_prefix("ababab")', "expect": '"abab"'},
            {"call": 'longest_prefix("abc")', "expect": '""'},
        ],
        "approaches": {
            "Try every length, longest first": {
                "idea": [
                    "A happy prefix of length <code>L</code> is a proper prefix that is also a suffix: <code>s[:L] == s[-L:]</code> with <code>L &lt; n</code>.",
                    "Trying lengths from longest to shortest means the first one that works is the answer, so the search can stop there.",
                ],
                "steps": [
                    "Loop <code>L</code> from <code>len(s) - 1</code> down to 1.",
                    "Compare the prefix <code>s[:L]</code> with the suffix <code>s[-L:]</code>.",
                    "Return <code>s[:L]</code> at the first equal pair.",
                    "If no length works, return the empty string.",
                ],
                "why": [
                    "Every proper length is tried, and the first success is the largest one because lengths are tried in decreasing order.",
                    "Starting at <code>n - 1</code> excludes the whole string, which is trivially both a prefix and a suffix but is not proper.",
                    "Up to n − 1 lengths, each comparing two slices of length up to n: <strong>O(n²)</strong> time. The slices take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 6, so L runs 5, 4, 3, 2, 1.",
                        "L=5: \"ababa\" vs \"babab\": different.",
                        "L=4: \"abab\" vs \"abab\": equal.",
                        "It returns <strong>\"abab\"</strong> without trying shorter lengths.",
                    ],
                    [
                        "n = 3, so L runs 2, 1.",
                        "L=2: \"ab\" vs \"bc\": different.",
                        "L=1: \"a\" vs \"c\": different.",
                        "No length works: <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can't I use <code>s[-0:]</code> for L = 0?",
                     "<code>s[-0:]</code> is <code>s[0:]</code>, the whole string, not the empty one. That is why the loop stops at L = 1 and the empty case is handled by the final <code>return \"\"</code>."],
                    ["Can the prefix and suffix overlap?",
                     "Yes. In \"ababab\" the prefix \"abab\" (indices 0–3) and suffix \"abab\" (indices 2–5) share two characters, and that is allowed."],
                    ["When is the O(n²) actually reached?",
                     "When many comparisons run long before failing, for example \"aaaa…ab\", where every prefix is all a's and every suffix ends in b; slice comparisons there are cheap, but strings like \"abab…\" with near misses do more work per length."],
                ],
            },
            "Prefix function": {
                "idea": [
                    "This is exactly what the prefix function computes: <code>pi[i]</code> is the length of the longest proper border of <code>s[:i + 1]</code>.",
                    "So the answer is <code>s[:pi[-1]]</code>, the longest border of the whole string.",
                    "The prefix function builds each value from the previous ones, which is what makes it linear.",
                ],
                "steps": [
                    "Set <code>pi = [0] * len(s)</code> and <code>k = 0</code>, the current border length.",
                    "For <code>i</code> from 1: while <code>k</code> is positive and <code>s[i] != s[k]</code>, fall back with <code>k = pi[k - 1]</code>.",
                    "If <code>s[i] == s[k]</code>, extend the border: <code>k += 1</code>.",
                    "Store <code>pi[i] = k</code>.",
                    "Return <code>s[:pi[-1]]</code>, or \"\" for an empty string.",
                ],
                "why": [
                    "A border of <code>s[:i + 1]</code> is a border of <code>s[:i]</code> extended by one character. Trying the borders of <code>s[:i]</code> from longest to shortest via <code>pi[k - 1]</code> finds the longest one that extends.",
                    "<code>k</code> rises by at most 1 per step and each fall-back lowers it, so the total work is <strong>O(n)</strong> time.",
                    "The <code>pi</code> array uses <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i=1 (b): k=0 and b ≠ s[0] = a, so pi[1] = 0.",
                        "i=2 (a): a = s[0], k = 1. i=3 (b): b = s[1], k = 2.",
                        "i=4 (a): a = s[2], k = 3. i=5 (b): b = s[3], k = 4.",
                        "pi = [0, 0, 1, 2, 3, 4], so pi[-1] = 4 and the result is s[:4] = <strong>\"abab\"</strong>.",
                    ],
                    [
                        "i=1 (b): b ≠ a, so pi[1] = 0.",
                        "i=2 (c): c ≠ a, so pi[2] = 0.",
                        "pi = [0, 0, 0], so pi[-1] = 0.",
                        "The result is s[:0] = <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>if s else \"\"</code>?",
                     "For an empty string <code>pi</code> is empty and <code>pi[-1]</code> would raise an IndexError."],
                    ["Why does falling back to <code>pi[k - 1]</code> try the right candidates?",
                     "The borders of a string are its longest border, the longest border of that, and so on. <code>pi[k - 1]</code> is the next one in that chain, so no candidate is skipped."],
                    ["Is <code>pi[-1]</code> always less than n?",
                     "Yes. Borders are proper by definition, and the loop starts at <code>i = 1</code>, so the string is never matched against itself at shift 0."],
                ],
            },
            "Prefix and suffix hashes grown together": {
                "idea": [
                    "Grow the prefix one character on the right and the suffix one character on the left at the same time, keeping a hash of each.",
                    "Whenever the two hashes agree, the prefix and suffix of that length are (almost certainly) equal, so remember that length.",
                    "Both hashes update in O(1) per length, so every length is checked in constant time.",
                ],
                "steps": [
                    "Pick <code>MOD = 2<sup>61</sup> − 1</code> and a random base <code>B</code>; set <code>pre = suf = 0</code>, <code>power = 1</code>, <code>best = 0</code>.",
                    "For <code>L</code> from 1 to n − 1, append <code>s[L - 1]</code> to the prefix: <code>pre = pre * B + ord(s[L - 1])</code>.",
                    "Prepend <code>s[-L]</code> to the suffix: <code>suf = ord(s[-L]) * power + suf</code>, then <code>power *= B</code> (all mod MOD).",
                    "If <code>pre == suf</code>, set <code>best = L</code>.",
                    "Return <code>s[:best]</code>.",
                ],
                "why": [
                    "Both hashes use the same polynomial: the first character gets the highest power of B. Appending multiplies the old prefix by B; prepending adds the new character times B<sup>L−1</sup>, which is <code>power</code> before it is updated.",
                    "Lengths increase, so the last length where the hashes match is the longest happy prefix, barring a collision, which a random base makes extremely unlikely.",
                    "One O(1) update per length: <strong>O(n)</strong> time and <strong>O(1)</strong> extra space beyond the returned string.",
                ],
                "dry": [
                    [
                        "L=1: prefix \"a\", suffix \"b\": hashes differ.",
                        "L=2: prefix \"ab\", suffix \"ab\": hashes equal, best = 2.",
                        "L=3: \"aba\" vs \"bab\": differ.",
                        "L=4: \"abab\" vs \"abab\": equal, best = 4. L=5: \"ababa\" vs \"babab\": differ.",
                        "It returns s[:4] = <strong>\"abab\"</strong>.",
                    ],
                    [
                        "L=1: prefix \"a\", suffix \"c\": hashes differ.",
                        "L=2: prefix \"ab\", suffix \"bc\": hashes differ.",
                        "best stays 0.",
                        "It returns <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Unlike Rabin-Karp search, there is no string comparison on a match. Is that safe?",
                     "It trades certainty for O(1) space. With a 61-bit prime modulus and a random base, a false match has probability around n / 2<sup>61</sup>, far below any test's chance of noticing; adding a slice check would make it exact."],
                    ["Why does the suffix need <code>power</code> but the prefix does not?",
                     "The prefix grows on the right, so its old characters all move up one power: multiply by B. The suffix grows on the left, so the new character takes the highest power, B<sup>L−1</sup>, and the old ones stay put."],
                    ["Why can't I stop at the first match like the brute force?",
                     "Lengths increase here, so the first match is the shortest border. The loop must run to the end and keep the last match."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ shortest palindrome
    "shortest-palindrome": {
        "examples": [
            {"call": 'shortest_palindrome("aacecaaa")', "expect": '"aaacecaaa"'},
            {"call": 'shortest_palindrome("abcd")', "expect": '"dcbabcd"'},
        ],
        "approaches": {
            "Longest palindromic prefix by direct check": {
                "idea": [
                    "Characters can only be added in front, so the original s stays at the end. The part of s that is already a palindrome at its start can be reused as the centre.",
                    "If <code>s[:L]</code> is the longest palindromic prefix, the answer puts the reverse of the rest, <code>s[L:][::-1]</code>, in front of s.",
                    "Find that L by trying lengths from n down and stopping at the first palindrome.",
                ],
                "steps": [
                    "Loop <code>L</code> from <code>len(s)</code> down to 1.",
                    "Test whether <code>s[:L] == s[:L][::-1]</code>.",
                    "At the first palindrome, return <code>s[L:][::-1] + s</code>.",
                    "If the loop never runs (empty s), return s.",
                ],
                "why": [
                    "The result has to read the same backwards and end with s; mirroring everything after the palindromic prefix achieves that, and a longer prefix means fewer added characters.",
                    "L = 1 always works because a single character is a palindrome, so for non-empty s the loop always returns.",
                    "Up to n lengths, each reversed and compared in O(n): <strong>O(n²)</strong> time and <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "L=8: \"aacecaaa\" reversed is \"aaacecaa\": not a palindrome.",
                        "L=7: \"aacecaa\" reversed is itself: a palindrome.",
                        "The rest is s[7:] = \"a\"; its reverse \"a\" goes in front.",
                        "It returns \"a\" + \"aacecaaa\" = <strong>\"aaacecaaa\"</strong>.",
                    ],
                    [
                        "L=4 \"abcd\", L=3 \"abc\", L=2 \"ab\": none is a palindrome.",
                        "L=1: \"a\" is a palindrome.",
                        "The rest is \"bcd\"; its reverse \"dcb\" goes in front.",
                        "It returns <strong>\"dcbabcd\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the longest palindromic prefix the right thing to keep?",
                     "Everything added in front must mirror the characters of s that lie outside the central palindrome. The longer that central part, the fewer characters need mirroring, and it must start at index 0 because nothing is added after s."],
                    ["Why does L = n get tried first?",
                     "If s is already a palindrome nothing needs adding, and L = n returns <code>\"\" + s</code> = s at once."],
                    ["What does it return for an empty string?",
                     "The range is empty, so the loop body never runs and the final <code>return s</code> gives \"\"."],
                ],
            },
            "KMP border of s + # + reverse(s)": {
                "idea": [
                    "A prefix of s is a palindrome exactly when it equals its own reverse, and the reverse of a prefix of s is a <em>suffix</em> of <code>reverse(s)</code>.",
                    "So the longest palindromic prefix is the longest prefix of s that is also a suffix of reverse(s): the longest border of <code>s + \"#\" + s[::-1]</code>.",
                    "The <code>#</code> stops a border from crossing the middle and growing longer than s.",
                ],
                "steps": [
                    "Build <code>t = s + \"#\" + s[::-1]</code>.",
                    "Run the prefix function over <code>t</code>, with the usual fall-back <code>k = pi[k - 1]</code> on a mismatch.",
                    "<code>pi[-1]</code> is the length of the longest palindromic prefix.",
                    "Return <code>s[pi[-1]:][::-1] + s</code>.",
                ],
                "why": [
                    "A border of t of length L means <code>t[:L] = s[:L]</code> equals the last L characters of t, which are <code>reverse(s[:L])</code>. So <code>s[:L]</code> is a palindrome.",
                    "Because <code>#</code> appears only once, no border can contain it, so every border fits inside s and the longest border is the longest palindromic prefix.",
                    "t has 2n + 1 characters and the prefix function is linear: <strong>O(n)</strong> time, <strong>O(n)</strong> space for t and <code>pi</code>.",
                ],
                "dry": [
                    [
                        "t = \"aacecaaa#aaacecaa\" (17 characters).",
                        "Over the s part pi reaches [0, 1, 0, 0, 0, 1, 2, 2]. At the <code>#</code>, k falls 2 → 1 → 0, so pi[8] = 0.",
                        "In the reversed part: a, a give k = 2; the third a mismatches c, falls to pi[1] = 1 and matches s[1], so k = 2 again.",
                        "Then c, e, c, a, a extend k to 3, 4, 5, 6, 7. pi[-1] = 7.",
                        "s[7:] = \"a\", reversed \"a\", so it returns <strong>\"aaacecaaa\"</strong>.",
                    ],
                    [
                        "t = \"abcd#dcba\".",
                        "No character before the last equals the start a, so pi stays 0 up to index 7.",
                        "The final a equals t[0], so pi[-1] = 1: only \"a\" is a palindromic prefix.",
                        "s[1:] = \"bcd\", reversed \"dcb\", so it returns <strong>\"dcbabcd\"</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong without the <code>#</code>?",
                     "The border can run past the middle. For \"aaba\", <code>s + s[::-1]</code> = \"aababaa\" has a border of length 5 &gt; 4, and the code returns \"aaba\" instead of the correct \"abaaba\"."],
                    ["Could the separator be any character?",
                     "It must not appear in s, or a border could pass through it. <code>#</code> is safe for the lowercase inputs this problem uses."],
                    ["Why do I only need <code>pi[-1]</code>?",
                     "Only borders of the whole of t matter, since they compare a prefix of s with a suffix of reverse(s). The other <code>pi</code> values are just stepping stones to compute it."],
                ],
            },
            "Forward and backward rolling hash": {
                "idea": [
                    "Scan s once, keeping two hashes of the prefix read so far: one reading it forwards, one reading it backwards.",
                    "When the two are equal, that prefix reads the same both ways, so it is (barring a collision) a palindrome; keep the largest such length.",
                ],
                "steps": [
                    "Pick <code>MOD = 2<sup>61</sup> − 1</code> and a random base <code>B</code>; set <code>fwd = bwd = 0</code>, <code>power = 1</code>, <code>best = 0</code>.",
                    "For each <code>i, ch</code>: <code>fwd = fwd * B + ord(ch)</code>, so the new character takes the lowest power.",
                    "<code>bwd = bwd + ord(ch) * power</code>, so the new character takes the highest power; then <code>power *= B</code> (all mod MOD).",
                    "If <code>fwd == bwd</code>, the prefix <code>s[:i + 1]</code> is a palindrome: <code>best = i + 1</code>.",
                    "Return <code>s[best:][::-1] + s</code>.",
                ],
                "why": [
                    "<code>fwd</code> is the hash of the prefix and <code>bwd</code> is the same polynomial applied to the reversed prefix, so they are equal exactly when the prefix equals its reverse, up to collisions.",
                    "Prefixes are scanned in increasing length, so the last match is the longest palindromic prefix, and the answer follows as in the direct check.",
                    "One O(1) update per character: <strong>O(n)</strong> time and <strong>O(1)</strong> extra space apart from the output.",
                ],
                "dry": [
                    [
                        "Prefix \"a\" (i=0) and \"aa\" (i=1) are palindromes: best = 1, then 2.",
                        "\"aac\", \"aace\", \"aacec\", \"aaceca\": forward and backward hashes differ.",
                        "\"aacecaa\" (i=6) is a palindrome: best = 7.",
                        "\"aacecaaa\" (i=7) is not, so best stays 7.",
                        "It returns \"a\" + s = <strong>\"aaacecaaa\"</strong>.",
                    ],
                    [
                        "\"a\" (i=0): both hashes are <code>ord('a')</code>, best = 1.",
                        "\"ab\", \"abc\", \"abcd\": forward and backward hashes differ.",
                        "best = 1, so the rest \"bcd\" is mirrored.",
                        "It returns <strong>\"dcbabcd\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>power</code> be used before it is multiplied?",
                     "The i-th character (0-based) must get weight B<sup>i</sup> in <code>bwd</code>. <code>power</code> holds exactly B<sup>i</sup> at that moment and is moved to B<sup>i+1</sup> for the next character."],
                    ["Can a collision give a wrong answer?",
                     "In principle yes, because nothing re-checks the palindrome. With a 61-bit prime and a random base the chance is around n / 2<sup>61</sup>; adding a direct check on the final <code>best</code> would make it exact."],
                    ["Why not stop at the first match?",
                     "Lengths grow, so the first match is just \"s[0]\". The longest palindromic prefix is the last match, so the loop must finish."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sum of scores
    "sum-of-scores-of-built-strings": {
        "examples": [
            {"call": 'sum_scores("babab")', "expect": "9"},
            {"call": 'sum_scores("aaaa")', "expect": "10"},
        ],
        "approaches": {
            "Compare every suffix with the string": {
                "idea": [
                    "The score of the suffix starting at <code>i</code> is the length of its longest common prefix with the whole string.",
                    "Measure each score directly by walking forward from <code>i</code> and from 0 together until the characters differ or the string ends.",
                ],
                "steps": [
                    "Set <code>total = 0</code> and <code>n = len(s)</code>.",
                    "For each start <code>i</code>, set <code>k = 0</code>.",
                    "While <code>i + k &lt; n</code> and <code>s[k] == s[i + k]</code>, increase <code>k</code>.",
                    "Add <code>k</code> to <code>total</code>.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "Each <code>k</code> stops at the first mismatch or the end of the string, which is exactly the common-prefix length, so each score is exact.",
                    "The suffix at <code>i = 0</code> is the whole string and scores n, which the loop counts naturally.",
                    "The comparisons for start i can run n − i steps, so the total is up to 1 + 2 + … + n: <strong>O(n²)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: the suffix is the whole string, k = 5.",
                        "i=1: a ≠ b at once, k = 0.",
                        "i=2: \"bab\" matches the first three characters and the string ends, k = 3.",
                        "i=3: a ≠ b, k = 0. i=4: \"b\" matches, k = 1.",
                        "total = 5 + 0 + 3 + 0 + 1 = <strong>9</strong>.",
                    ],
                    [
                        "i=0: k = 4.",
                        "i=1: \"aaa\" matches until the end, k = 3.",
                        "i=2: k = 2. i=3: k = 1.",
                        "Every comparison succeeds; only the string end stops k. total = 4 + 3 + 2 + 1 = <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>i + k &lt; n</code> first?",
                     "The <code>and</code> evaluates left to right, so the bounds check stops <code>s[i + k]</code> from reading past the end, as happens on every suffix of \"aaaa\"."],
                    ["Which input makes it quadratic?",
                     "A string of one repeated letter, like \"aaaa\": every comparison succeeds, giving n + (n − 1) + … + 1 steps."],
                    ["Isn't <code>s[k]</code> needed to stay in range too?",
                     "<code>k ≤ i + k &lt; n</code>, so once the second index is in range the first one is as well."],
                ],
            },
            "Z-function": {
                "idea": [
                    "The score of the suffix at <code>i</code> is exactly <code>z[i]</code>, so the answer is <code>sum(z)</code> with <code>z[0] = n</code>.",
                    "The Z algorithm computes all of them in linear time by remembering the box <code>[l, r)</code>, the rightmost stretch known to equal a prefix.",
                    "Inside the box, <code>s[i..r)</code> repeats <code>s[i-l..r-l)</code>, so <code>z[i - l]</code> gives a free head start.",
                ],
                "steps": [
                    "Set <code>z = [0] * n</code>, <code>l = r = 0</code> and <code>z[0] = n</code>.",
                    "For each <code>i</code> from 1: if <code>i &lt; r</code>, start with <code>z[i] = min(r - i, z[i - l])</code>.",
                    "Extend while <code>i + z[i] &lt; n</code> and <code>s[z[i]] == s[i + z[i]]</code>.",
                    "If <code>i + z[i] &gt; r</code>, move the box: <code>l, r = i, i + z[i]</code>.",
                    "Return <code>sum(z)</code>.",
                ],
                "why": [
                    "The copied value is correct up to <code>r</code>, the <code>min</code> stops it from trusting anything past the box, and the while loop measures the rest directly, so every <code>z[i]</code> is exact.",
                    "Each successful comparison in the while loop moves <code>r</code> right, and <code>r ≤ n</code>, so there are at most n successful comparisons plus one failure per i: <strong>O(n)</strong> time.",
                    "The <code>z</code> array uses <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "z[0] = 5. i=1 (a): outside the box, a ≠ b, z = 0.",
                        "i=2: outside the box, \"bab\" matches to the end: z = 3, box [2, 5).",
                        "i=3: inside, start at min(5 − 3, z[1] = 0) = 0; a ≠ b, z = 0.",
                        "i=4: inside, start at min(5 − 4, z[2] = 3) = 1; the string ends, so z = 1 with no comparison.",
                        "z = [5, 0, 3, 0, 1], sum = <strong>9</strong>.",
                    ],
                    [
                        "z[0] = 4. i=1: compares a, a, a to the end: z = 3, box [1, 4).",
                        "i=2: inside, start at min(4 − 2, z[1] = 3) = 2; already at the end, z = 2.",
                        "i=3: inside, start at min(4 − 3, z[2] = 2) = 1; at the end, z = 1.",
                        "Only 3 comparisons in total instead of 6 in the brute force. z = [4, 3, 2, 1], sum = <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>z[0]</code> set to n by hand?",
                     "The loop starts at 1, because at 0 the box trick has nothing to reuse. By definition the whole string matches itself, and the problem counts that suffix too."],
                    ["Why take the <code>min</code> with <code>r - i</code>?",
                     "<code>z[i - l]</code> may describe a match that runs past what the box guarantees. Beyond <code>r</code> nothing is known, so the head start is capped there and the rest is checked."],
                    ["Can the box move left?",
                     "No. It only moves when <code>i + z[i] &gt; r</code>, so <code>r</code> never decreases. That monotonic <code>r</code> is the whole reason the algorithm is linear."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest duplicate substring
    "longest-duplicate-substring": {
        "examples": [
            {"call": 'longest_dup_substring("banana")', "expect": '"ana"'},
            {"call": 'longest_dup_substring("abcd")', "expect": '""'},
        ],
        "approaches": {
            "Every length, set of substrings": {
                "idea": [
                    "Try lengths from longest to shortest; the first length with a repeated window gives the answer.",
                    "For a fixed length L, slide over every window and keep a set of the ones already seen; a window already in the set occurs twice.",
                ],
                "steps": [
                    "Loop <code>L</code> from <code>len(s) - 1</code> down to 1.",
                    "Start an empty set <code>seen</code>.",
                    "For each start <code>i</code>, take <code>w = s[i:i + L]</code>.",
                    "If <code>w</code> is in <code>seen</code>, return it; otherwise add it.",
                    "If no length has a repeat, return \"\".",
                ],
                "why": [
                    "Lengths are tried in decreasing order, so the first repeat found has the maximum length.",
                    "Two occurrences may overlap (\"ana\" at 1 and 3 in \"banana\"), and the set test allows that because it only compares contents.",
                    "There are O(n) lengths, each with O(n) windows of size O(n) to slice and hash: <strong>O(n³)</strong> time. One set holds up to n windows of length up to n: <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "L=5: \"banan\", \"anana\": no repeat.",
                        "L=4: \"bana\", \"anan\", \"nana\": no repeat.",
                        "L=3: \"ban\", \"ana\", \"nan\" are added; at i=3, \"ana\" is already in the set.",
                        "It returns <strong>\"ana\"</strong>.",
                    ],
                    [
                        "L=3: \"abc\", \"bcd\": no repeat.",
                        "L=2: \"ab\", \"bc\", \"cd\": no repeat.",
                        "L=1: \"a\", \"b\", \"c\", \"d\": all distinct.",
                        "It returns <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start at <code>len(s) - 1</code>?",
                     "A length-n window exists only once, so it can never repeat. n − 1 is the longest length that can have two windows."],
                    ["Do overlapping occurrences count?",
                     "Yes. The problem only asks for two occurrences, and \"ana\" in \"banana\" overlaps itself on the middle \"a\"."],
                    ["Why is the space O(n²)?",
                     "The set can hold about n windows, each up to n characters long, so the stored text adds up to O(n²)."],
                ],
            },
            "Binary search on length + rolling hash": {
                "idea": [
                    "If some string of length L repeats, cutting one character off it gives a repeat of length L − 1. So \"has a repeat of length L\" is true up to the answer and false after it: binary search the length.",
                    "To test one length quickly, roll a hash over every window and look for two windows with the same hash, verifying the actual strings to rule out collisions.",
                ],
                "steps": [
                    "Convert the characters to <code>codes</code> and pick <code>MOD = 2<sup>61</sup> − 1</code> and a random base <code>B</code>.",
                    "<code>check(L)</code> hashes the first window, then rolls: <code>h = ((h - codes[i - 1] * top) * B + codes[i + L - 1]) % MOD</code>.",
                    "<code>seen</code> maps each hash to the starts that produced it; on a hash hit, compare <code>s[j:j + L] == s[i:i + L]</code> and return <code>i</code> if equal, else -1 at the end.",
                    "Binary search with <code>lo, hi = 1, n - 1</code>: if <code>check(mid)</code> finds a start, record <code>best</code> and set <code>lo = mid + 1</code>; otherwise <code>hi = mid - 1</code>.",
                    "Return <code>best</code>, the last repeat found.",
                ],
                "why": [
                    "The property is monotone, so binary search over 1..n−1 ends with <code>best</code> holding a repeat of the largest length that has one.",
                    "<code>check</code> only reports a start after a real string comparison, so collisions can cost time but can never produce a wrong repeat.",
                    "Each <code>check</code> is O(n) expected and binary search calls it O(log n) times: <strong>O(n log n)</strong> expected time. <code>seen</code> and <code>codes</code> take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "n = 6, so lo = 1, hi = 5.",
                        "mid = 3: windows \"ban\", \"ana\", \"nan\", \"ana\". At i=3 the hash equals that of start 1, the strings match, so best = \"ana\" and lo = 4.",
                        "mid = 4: windows \"bana\", \"anan\", \"nana\" all differ, so hi = 3.",
                        "lo &gt; hi, so the search stops.",
                        "It returns <strong>\"ana\"</strong>.",
                    ],
                    [
                        "n = 4, so lo = 1, hi = 3.",
                        "mid = 2: \"ab\", \"bc\", \"cd\" all differ, so hi = 1.",
                        "mid = 1: \"a\", \"b\", \"c\", \"d\" all differ, so hi = 0.",
                        "best was never set: <strong>\"\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is binary search allowed here?",
                     "A repeat of length L contains a repeat of every shorter length (its prefixes), so the yes/no answer flips only once as L grows. That monotonicity is what binary search needs."],
                    ["Why does <code>seen</code> map a hash to a list of starts?",
                     "Different windows can share a hash. Keeping every start with that hash lets <code>check</code> compare against each of them, so a real repeat is not missed because of an unlucky collision."],
                    ["Why <code>lo = mid + 1</code> after a success?",
                     "<code>best</code> already stores the repeat of length <code>mid</code>, so the search only needs to look for something longer."],
                ],
            },
        },
    },
}
