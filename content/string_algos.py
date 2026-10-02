# -*- coding: utf-8 -*-
"""String Algorithms topic: KMP (prefix function), Rabin-Karp (rolling hash)
and the Z-function. Same build contract as content/dsa.py: every approach is
executed with the problem's tests, which cross-check against brute force."""

PRELUDE_STR = '''import random
'''


STRING_ALGOS_TOPIC = dict(
    id="string-algorithms",
    title="String Algorithms",
    prelude=PRELUDE_STR,
    blurb=[
        "Naive substring search compares the pattern at every starting position and can redo the same comparisons over and over: O(n&middot;m). Three linear-time ideas fix that, and each one also solves a family of problems that never say \"search\".",
        "<strong>KMP</strong> precomputes, for every prefix of the pattern, its longest <em>border</em> (a proper prefix that is also a suffix), so after a mismatch it knows how far it can shift without re-reading the text. <strong>Rabin&ndash;Karp</strong> compares O(1) rolling hashes instead of characters. The <strong>Z-function</strong> records, for every position, how long the string matches its own prefix from there.",
    ],
    convention=[
        "<code>n</code> is the text length and <code>m</code> the pattern length. In Python, <code>str.find</code> and <code>in</code> are the right tool in production (they are fast C code); these problems are about knowing what is underneath and about the border/hash ideas, which the built-ins do not expose.",
    ],
    sections=[

dict(
    id="matching",
    title="Exact matching: KMP, Rabin-Karp and Z",
    idea=[
        "The <strong>prefix function</strong> <code>pi[i]</code> is the length of the longest proper border of <code>s[:i+1]</code>. It is built in O(m) by reusing itself: if the border cannot be extended by <code>s[i]</code>, fall back to the border of the border, <code>pi[k-1]</code>, and try again. Each fall-back shortens <code>k</code>, and <code>k</code> grows by at most one per character, so the total work is linear.",
        "KMP search runs the same loop over the text with the pattern's <code>pi</code>. A neat equivalent: compute <code>pi</code> (or the Z-array) of <code>pattern + \"#\" + text</code>; every position where it reaches <code>m</code> is a match. The separator stops a match from running across the boundary.",
        "Rabin&ndash;Karp keeps <code>h = s[i]&middot;B<sup>m-1</sup> + &hellip; + s[i+m-1]</code> mod a large prime, and slides the window in O(1): remove the leading character's term, multiply by B, add the new one. Equal hashes are only a <em>probable</em> match, so verify the substring before trusting it.",
    ],
    problems=[

    # ------------------------------------------------------------------ 28
    dict(
        id="find-first-occurrence",
        lc=28, slug="find-the-index-of-the-first-occurrence-in-a-string",
        name="Find the Index of the First Occurrence in a String",
        difficulty="easy",
        framing=[
            "Labelled easy because the naive answer passes. It is the place to learn all three linear-time matchers on the simplest possible task, and to be able to explain why naive search is O(n&middot;m): text <code>aaaa&hellip;ab</code>, pattern <code>aaab</code>.",
        ],
        approaches=[
            dict(
                name="Try every starting position",
                time="O(n&middot;m)",
                space="O(1)",
                why=[
                    "Compare the pattern at each start. On repetitive inputs almost every start matches for a long way before failing, so the bound is reached.",
                ],
                code='''def str_str(haystack, needle):
    n, m = len(haystack), len(needle)
    for i in range(n - m + 1):
        if haystack[i:i + m] == needle:
            return i
    return -1''',
            ),
            dict(
                name="KMP with the prefix function",
                time="O(n + m)",
                space="O(m)",
                best=True,
                why=[
                    "<code>k</code> is how many pattern characters currently match. On a mismatch, instead of restarting, fall back to <code>pi[k-1]</code>: the longest prefix of the pattern that is still known to match the text ending here.",
                    "The text pointer never moves backwards, and <code>k</code> drops at most as often as it rose, so the scan is O(n) after an O(m) build.",
                ],
                code='''def prefix_function(s):
    pi, k = [0] * len(s), 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]              # fall back to the border of the border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi


def str_str(haystack, needle):
    if not needle:
        return 0
    pi, k = prefix_function(needle), 0
    for i, ch in enumerate(haystack):
        while k and ch != needle[k]:
            k = pi[k - 1]
        if ch == needle[k]:
            k += 1
        if k == len(needle):
            return i - k + 1
    return -1''',
            ),
            dict(
                name="Rabin-Karp rolling hash",
                time="O(n + m) expected",
                space="O(1)",
                why=[
                    "Hash the pattern and the first window, then roll: <code>h = (h - s[i]&middot;B<sup>m-1</sup>)&middot;B + s[i+m]</code>, all mod <code>2<sup>61</sup>-1</code>. Precompute <code>B<sup>m-1</sup></code> once.",
                    "On a hash hit, compare the actual substring. A random base makes an adversarial collision unlikely, so verification almost never fails and the expected time stays linear.",
                ],
                code='''def str_str(haystack, needle):
    n, m = len(haystack), len(needle)
    if m > n:
        return -1
    MOD, B = (1 << 61) - 1, random.randrange(256, 1 << 40)
    top = pow(B, m - 1, MOD)
    hp = hw = 0
    for i in range(m):
        hp = (hp * B + ord(needle[i])) % MOD
        hw = (hw * B + ord(haystack[i])) % MOD
    for i in range(n - m + 1):
        if hw == hp and haystack[i:i + m] == needle:    # verify: hashes can collide
            return i
        if i + m < n:
            hw = ((hw - ord(haystack[i]) * top) * B + ord(haystack[i + m])) % MOD
    return -1''',
            ),
            dict(
                name="Z-function on pattern + separator + text",
                time="O(n + m)",
                space="O(n + m)",
                why=[
                    "<code>z[i]</code> is the length of the longest common prefix of the string and its suffix starting at <code>i</code>. On <code>needle + \"\\0\" + haystack</code>, any <code>z[i] == m</code> marks a match.",
                    "The <code>[l, r)</code> box is the rightmost segment known to equal a prefix. Inside it, <code>z[i - l]</code> gives a free lower bound, so each character is compared successfully at most once.",
                ],
                code='''def z_function(s):
    n = len(s)
    z, l, r = [0] * n, 0, 0
    if n:
        z[0] = n
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])        # reuse the match inside [l, r)
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def str_str(haystack, needle):
    m = len(needle)
    z = z_function(needle + "\\0" + haystack)
    for i in range(m + 1, len(z)):
        if z[i] >= m:
            return i - m - 1
    return -1 if m else 0''',
            ),
        ],
        tests='''assert str_str("sadbutsad", "sad") == 0
assert str_str("leetcode", "leeto") == -1
assert str_str("a", "a") == 0
assert str_str("mississippi", "issip") == 4
assert str_str("aaaaaaaaab", "aaab") == 6

rng = random.Random(23)
for _ in range(400):
    h = "".join(rng.choice("ab") for _ in range(rng.randint(1, 30)))
    nd = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
    assert str_str(h, nd) == h.find(nd), (h, nd)''',
    ),

    # ------------------------------------------------------------------ 796
    dict(
        id="rotate-string",
        lc=796, slug="rotate-string",
        name="Rotate String",
        difficulty="easy",
        framing=[
            "Is <code>goal</code> a rotation of <code>s</code>? Every rotation of <code>s</code> appears as a substring of <code>s + s</code>, so the question is a single substring search. The classic reduction worth remembering.",
        ],
        approaches=[
            dict(
                name="Build every rotation",
                time="O(n&sup2;)",
                space="O(n)",
                why=["n rotations, each built and compared in O(n)."],
                code='''def rotate_string(s, goal):
    return len(s) == len(goal) and any(s[i:] + s[:i] == goal for i in range(max(1, len(s))))''',
            ),
            dict(
                name="Substring of s + s",
                time="O(n) with KMP",
                space="O(n)",
                best=True,
                why=[
                    "Lengths must match first, otherwise <code>\"a\"</code> would be found in <code>\"aa\"</code>-style doubled strings of the wrong size.",
                    "Python's <code>in</code> is a fast C search (a two-way / Boyer&ndash;Moore&ndash;Horspool hybrid), so the one-liner is the right production answer. If asked for a guaranteed bound, run KMP on <code>s + s</code>.",
                ],
                code='''def rotate_string(s, goal):
    return len(s) == len(goal) and goal in s + s''',
            ),
        ],
        tests='''assert rotate_string("abcde", "cdeab") is True
assert rotate_string("abcde", "abced") is False
assert rotate_string("", "") is True
assert rotate_string("a", "aa") is False

def brute(s, g):
    return len(s) == len(g) and any(s[i:] + s[:i] == g for i in range(max(1, len(s))))

rng = random.Random(29)
for _ in range(400):
    s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 8)))
    g = "".join(rng.choice("ab") for _ in range(rng.randint(0, 8)))
    assert rotate_string(s, g) == brute(s, g)''',
    ),

    # ------------------------------------------------------------------ 686
    dict(
        id="repeated-string-match",
        lc=686, slug="repeated-string-match",
        name="Repeated String Match",
        difficulty="medium",
        framing=[
            "Smallest number of copies of <code>a</code> so that <code>b</code> is a substring. The whole problem is the bound: if <code>b</code> fits anywhere, it fits in <code>q = ceil(len(b) / len(a))</code> copies or in <code>q + 1</code> (when it starts partway into a copy). More copies only repeat what is already there.",
        ],
        approaches=[
            dict(
                name="Keep appending until it is long enough",
                time="O((n + m)&middot;m)",
                space="O(n + m)",
                why=[
                    "Append copies until the text is at least as long as <code>b</code>, check, then try one more copy. Without the \"one more\" bound this loops forever on impossible inputs.",
                ],
                code='''def repeated_string_match(a, b):
    text, count = a, 1
    while len(text) < len(b):
        text += a; count += 1
    if b in text:
        return count
    if b in text + a:
        return count + 1
    return -1''',
            ),
            dict(
                name="KMP over the repeated text without building it",
                time="O(n + m)",
                space="O(m)",
                best=True,
                why=[
                    "Scan positions <code>0 .. (q+1)&middot;len(a) - 1</code> of the virtual text, reading character <code>a[i % len(a)]</code>. When KMP completes a match ending at <code>i</code>, the copies needed are <code>i // len(a) + 1</code>.",
                    "Memory stays O(m) regardless of how many copies are virtual.",
                ],
                code='''def repeated_string_match(a, b):
    pi, k = [0] * len(b), 0
    for i in range(1, len(b)):
        while k and b[i] != b[k]:
            k = pi[k - 1]
        if b[i] == b[k]:
            k += 1
        pi[i] = k

    q = -(-len(b) // len(a))
    k = 0
    for i in range((q + 1) * len(a)):
        ch = a[i % len(a)]
        while k and ch != b[k]:
            k = pi[k - 1]
        if ch == b[k]:
            k += 1
        if k == len(b):
            return i // len(a) + 1
    return -1''',
            ),
        ],
        tests='''assert repeated_string_match("abcd", "cdabcdab") == 3
assert repeated_string_match("a", "aa") == 2
assert repeated_string_match("abc", "wxyz") == -1
assert repeated_string_match("abc", "cabcabca") == 4

def brute(a, b):
    for k in range(1, len(b) // len(a) + 3):
        if b in a * k:
            return k
    return -1

rng = random.Random(31)
for _ in range(400):
    a = "".join(rng.choice("ab") for _ in range(rng.randint(1, 4)))
    b = "".join(rng.choice("ab") for _ in range(rng.randint(1, 10)))
    assert repeated_string_match(a, b) == brute(a, b)''',
    ),
    ],
),

dict(
    id="borders-and-hashing",
    title="Borders, Z-arrays and rolling hashes",
    idea=[
        "Many \"hard\" string problems are one array away. <code>pi[-1]</code> of a string is its longest border, which answers \"longest prefix that is also a suffix\", and <code>n - pi[-1]</code> is the shortest period. The Z-array answers \"how much of the prefix matches from here\" for every position at once.",
        "When the question is about <em>arbitrary</em> repeated substrings rather than prefixes, rolling hashes plus binary search on the length is the standard interview answer: if a repeated substring of length L exists, one of every shorter length does too, so the predicate is monotone.",
    ],
    problems=[

    # ------------------------------------------------------------------ 459
    dict(
        id="repeated-substring-pattern",
        lc=459, slug="repeated-substring-pattern",
        name="Repeated Substring Pattern",
        difficulty="easy",
        framing=[
            "Can <code>s</code> be built by repeating one of its substrings? Three answers of increasing insight: try every divisor; the <code>(s + s)[1:-1]</code> trick; and the period from the prefix function.",
        ],
        approaches=[
            dict(
                name="Try every divisor length",
                time="O(n &middot; d(n))",
                space="O(n)",
                why=[
                    "A repeating unit's length divides n. For each divisor L &lt; n, check <code>s[:L] * (n // L) == s</code>. <code>d(n)</code>, the number of divisors, is small in practice.",
                ],
                code='''def repeated_substring_pattern(s):
    n = len(s)
    return any(n % L == 0 and s[:L] * (n // L) == s for L in range(1, n // 2 + 1))''',
            ),
            dict(
                name="s is inside (s + s) with the ends cut off",
                time="O(n)",
                space="O(n)",
                why=[
                    "If <code>s</code> is periodic, shifting it by one period gives itself, so <code>s</code> appears in <code>s + s</code> at an offset other than 0 and n. Cutting the first and last character rules those two out.",
                    "The converse holds too (a string equal to a non-trivial rotation of itself is periodic), which is what makes the trick a full answer and not a heuristic.",
                ],
                code='''def repeated_substring_pattern(s):
    return s in (s + s)[1:-1]''',
            ),
            dict(
                name="Shortest period from the prefix function",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "The longest border <code>b = pi[-1]</code> gives the shortest period <code>p = n - b</code>. The string is a repetition exactly when there is a border and <code>p</code> divides <code>n</code>.",
                    "This is the version to explain: it says <em>why</em> and also tells you the repeating unit, <code>s[:p]</code>.",
                ],
                code='''def repeated_substring_pattern(s):
    pi, k = [0] * len(s), 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    period = len(s) - pi[-1]
    return pi[-1] > 0 and len(s) % period == 0''',
            ),
        ],
        tests='''assert repeated_substring_pattern("abab") is True
assert repeated_substring_pattern("aba") is False
assert repeated_substring_pattern("abcabcabcabc") is True
assert repeated_substring_pattern("a") is False
assert repeated_substring_pattern("abaababaab") is True

def brute(s):
    n = len(s)
    return any(n % L == 0 and s[:L] * (n // L) == s for L in range(1, n))

rng = random.Random(37)
for _ in range(500):
    unit = "".join(rng.choice("ab") for _ in range(rng.randint(1, 4)))
    s = unit * rng.randint(1, 4) if rng.random() < 0.5 else "".join(rng.choice("ab") for _ in range(rng.randint(1, 12)))
    assert repeated_substring_pattern(s) == brute(s), s''',
    ),

    # ------------------------------------------------------------------ 1392
    dict(
        id="longest-happy-prefix",
        lc=1392, slug="longest-happy-prefix",
        name="Longest Happy Prefix",
        difficulty="hard",
        framing=[
            "Longest proper prefix that is also a suffix. That is the definition of the longest border, so the answer is literally <code>s[:pi[-1]]</code>. Labelled hard because the brute force is O(n&sup2;) and n is 10<sup>5</sup>.",
        ],
        approaches=[
            dict(
                name="Try every length, longest first",
                time="O(n&sup2;)",
                space="O(n)",
                why=["Each comparison of a prefix and a suffix costs up to O(n)."],
                code='''def longest_prefix(s):
    for L in range(len(s) - 1, 0, -1):
        if s[:L] == s[-L:]:
            return s[:L]
    return ""''',
            ),
            dict(
                name="Prefix function",
                time="O(n)",
                space="O(n)",
                best=True,
                why=["<code>pi[-1]</code> is, by definition, the length of the longest proper border of the whole string."],
                code='''def longest_prefix(s):
    pi, k = [0] * len(s), 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return s[:pi[-1]] if s else ""''',
            ),
            dict(
                name="Prefix and suffix hashes grown together",
                time="O(n)",
                space="O(1)",
                why=[
                    "Grow the prefix hash forwards (<code>h&middot;B + c</code>) and the suffix hash backwards (<code>c&middot;B<sup>L</sup> + h</code>). Whenever they agree, remember L. Same polynomial, so equal strings give equal hashes.",
                    "O(1) extra space, but correct only with high probability. Mention the collision risk, and that a 61-bit Mersenne modulus with a random base makes it negligible.",
                ],
                code='''def longest_prefix(s):
    MOD, B = (1 << 61) - 1, random.randrange(256, 1 << 40)
    pre = suf = 0
    power, best = 1, 0
    for L in range(1, len(s)):
        pre = (pre * B + ord(s[L - 1])) % MOD
        suf = (ord(s[-L]) * power + suf) % MOD
        power = power * B % MOD
        if pre == suf:
            best = L
    return s[:best]''',
            ),
        ],
        tests='''assert longest_prefix("level") == "l"
assert longest_prefix("ababab") == "abab"
assert longest_prefix("a") == ""
assert longest_prefix("aaaa") == "aaa"

def brute(s):
    return next((s[:L] for L in range(len(s) - 1, 0, -1) if s[:L] == s[-L:]), "")

rng = random.Random(41)
for _ in range(500):
    s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 16)))
    assert longest_prefix(s) == brute(s), s''',
    ),

    # ------------------------------------------------------------------ 214
    dict(
        id="shortest-palindrome",
        lc=214, slug="shortest-palindrome",
        name="Shortest Palindrome",
        difficulty="hard",
        framing=[
            "Add the fewest characters to the <em>front</em> of <code>s</code> to make a palindrome. Whatever is added must mirror the end of <code>s</code>, so the problem is: find the longest prefix of <code>s</code> that is already a palindrome, then prepend the reverse of the rest.",
            "A prefix <code>p</code> of <code>s</code> is a palindrome exactly when it is also a suffix of <code>reverse(s)</code>. So the longest palindromic prefix is the longest border of <code>s + \"#\" + reverse(s)</code>.",
        ],
        approaches=[
            dict(
                name="Longest palindromic prefix by direct check",
                time="O(n&sup2;)",
                space="O(n)",
                why=["Test prefixes from longest to shortest; each test is O(n)."],
                code='''def shortest_palindrome(s):
    for L in range(len(s), 0, -1):
        if s[:L] == s[:L][::-1]:
            return s[L:][::-1] + s
    return s''',
            ),
            dict(
                name="KMP border of s + # + reverse(s)",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "The separator keeps the border from spilling across the middle, so <code>pi[-1]</code> is at most <code>len(s)</code> and equals the length of the longest palindromic prefix.",
                ],
                code='''def shortest_palindrome(s):
    t = s + "#" + s[::-1]
    pi, k = [0] * len(t), 0
    for i in range(1, len(t)):
        while k and t[i] != t[k]:
            k = pi[k - 1]
        if t[i] == t[k]:
            k += 1
        pi[i] = k
    return s[pi[-1]:][::-1] + s''',
            ),
            dict(
                name="Forward and backward rolling hash",
                time="O(n)",
                space="O(1)",
                why=[
                    "For each prefix length L, keep the hash of <code>s[:L]</code> read forwards and read backwards. When they agree, <code>s[:L]</code> is (very probably) a palindrome; keep the largest such L.",
                ],
                code='''def shortest_palindrome(s):
    MOD, B = (1 << 61) - 1, random.randrange(256, 1 << 40)
    fwd = bwd = 0
    power, best = 1, 0
    for i, ch in enumerate(s):
        fwd = (fwd * B + ord(ch)) % MOD
        bwd = (bwd + ord(ch) * power) % MOD
        power = power * B % MOD
        if fwd == bwd:
            best = i + 1
    return s[best:][::-1] + s''',
            ),
        ],
        tests='''assert shortest_palindrome("aacecaaa") == "aaacecaaa"
assert shortest_palindrome("abcd") == "dcbabcd"
assert shortest_palindrome("") == ""
assert shortest_palindrome("aba") == "aba"

def brute(s):
    for L in range(len(s), 0, -1):
        if s[:L] == s[:L][::-1]:
            return s[L:][::-1] + s
    return s

rng = random.Random(43)
for _ in range(500):
    s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 14)))
    assert shortest_palindrome(s) == brute(s), s''',
    ),

    # ------------------------------------------------------------------ 2223
    dict(
        id="sum-of-scores-of-built-strings",
        lc=2223, slug="sum-of-scores-of-built-strings",
        name="Sum of Scores of Built Strings",
        difficulty="hard",
        framing=[
            "The score of each suffix is the length of its longest common prefix with the whole string, and the answer is the sum. That is the definition of the Z-array, so the answer is <code>sum(z)</code> with <code>z[0] = n</code>. A problem that exists to test whether you know the Z-function.",
        ],
        approaches=[
            dict(
                name="Compare every suffix with the string",
                time="O(n&sup2;)",
                space="O(1)",
                why=["Each LCP is computed from scratch; <code>aaaa&hellip;</code> hits the worst case."],
                code='''def sum_scores(s):
    total, n = 0, len(s)
    for i in range(n):
        k = 0
        while i + k < n and s[k] == s[i + k]:
            k += 1
        total += k
    return total''',
            ),
            dict(
                name="Z-function",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "The <code>[l, r)</code> box reuses earlier matches. Each successful comparison pushes <code>r</code> right, and <code>r</code> never exceeds n, so the total work is linear.",
                ],
                code='''def sum_scores(s):
    n = len(s)
    z, l, r = [0] * n, 0, 0
    z[0] = n
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return sum(z)''',
            ),
        ],
        tests='''assert sum_scores("babab") == 9
assert sum_scores("azbazbzaz") == 14
assert sum_scores("a") == 1

def brute(s):
    total = 0
    for i in range(len(s)):
        k = 0
        while i + k < len(s) and s[k] == s[i + k]:
            k += 1
        total += k
    return total

rng = random.Random(47)
for _ in range(400):
    s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 20)))
    assert sum_scores(s) == brute(s)''',
    ),

    # ------------------------------------------------------------------ 1044
    dict(
        id="longest-duplicate-substring",
        lc=1044, slug="longest-duplicate-substring",
        name="Longest Duplicate Substring",
        difficulty="hard",
        framing=[
            "Longest substring that occurs at least twice (occurrences may overlap). If a duplicate of length L exists, its first L-1 characters are a duplicate of length L-1, so \"a duplicate of length L exists\" is monotone in L: <strong>binary search on L</strong>.",
            "Each check asks \"does any length-L window repeat?\", which rolling hashes answer in O(n). A suffix array solves it in O(n log n) deterministically, but is a lot to write in an interview.",
        ],
        approaches=[
            dict(
                name="Every length, set of substrings",
                time="O(n&sup3;)",
                space="O(n&sup2;)",
                why=[
                    "For each length from longest down, put every window into a set. Slicing and hashing each window costs O(L).",
                ],
                code='''def longest_dup_substring(s):
    for L in range(len(s) - 1, 0, -1):
        seen = set()
        for i in range(len(s) - L + 1):
            w = s[i:i + L]
            if w in seen:
                return w
            seen.add(w)
    return ""''',
            ),
            dict(
                name="Binary search on length + rolling hash",
                time="O(n log n) expected",
                space="O(n)",
                best=True,
                why=[
                    "<code>check(L)</code> rolls a hash over every window of length L and stores the start index per hash. On a repeated hash, compare the actual substrings so a collision can never produce a wrong answer.",
                    "Binary search finds the largest L with <code>check(L)</code> true: O(log n) checks of O(n) each.",
                ],
                code='''def longest_dup_substring(s):
    n = len(s)
    MOD, B = (1 << 61) - 1, random.randrange(256, 1 << 40)
    codes = [ord(c) for c in s]

    def check(L):
        top = pow(B, L - 1, MOD)
        h = 0
        for i in range(L):
            h = (h * B + codes[i]) % MOD
        seen = {h: [0]}
        for i in range(1, n - L + 1):
            h = ((h - codes[i - 1] * top) * B + codes[i + L - 1]) % MOD
            for j in seen.get(h, ()):
                if s[j:j + L] == s[i:i + L]:       # rule out a collision
                    return i
            seen.setdefault(h, []).append(i)
        return -1

    lo, hi, best = 1, n - 1, ""
    while lo <= hi:
        mid = (lo + hi) // 2
        at = check(mid)
        if at != -1:
            best, lo = s[at:at + mid], mid + 1
        else:
            hi = mid - 1
    return best''',
            ),
        ],
        tests='''assert longest_dup_substring("banana") == "ana"
assert longest_dup_substring("abcd") == ""
assert longest_dup_substring("aaaa") == "aaa"

def brute_len(s):
    for L in range(len(s) - 1, 0, -1):
        windows = [s[i:i + L] for i in range(len(s) - L + 1)]
        if len(set(windows)) < len(windows):
            return L
    return 0

rng = random.Random(53)
for _ in range(300):
    s = "".join(rng.choice("ab") for _ in range(rng.randint(2, 18)))
    got = longest_dup_substring(s)
    assert len(got) == brute_len(s), s
    if got:
        assert s.find(got) != s.rfind(got)       # occurs at least twice''',
        pitfall="Do not trust a hash match without comparing the strings. With a fixed small base and modulus, LeetCode's tests include inputs built to collide.",
    ),
    ],
),
    ],
)
