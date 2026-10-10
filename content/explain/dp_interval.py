"""Write-ups for Dynamic Programming, part 6: interval problems."""

EXPLAIN = {
    # ------------------------------------------------------------------ palindromic substrings
    "palindromic-substrings": {
        "examples": [
            {"call": 'count_substrings("abba")', "expect": "6"},
            {"call": 'count_substrings("aba")', "expect": "4"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "A range <code>s[i..j]</code> is a palindrome exactly when its two ends match <em>and</em> the inside <code>s[i+1..j-1]</code> is a palindrome.",
                    "That is a recursion on intervals: each call peels one character off both ends and asks the same question of a shorter range.",
                    "Counting is then just testing all n(n + 1)/2 ranges with that check and adding up the ones that pass.",
                ],
                "steps": [
                    "Define <code>pal(i, j)</code>: if <code>i &gt;= j</code> the range is empty or one character, so return <code>True</code>.",
                    "Otherwise return <code>s[i] == s[j] and pal(i + 1, j - 1)</code>. The <code>and</code> short-circuits, so a mismatch stops the walk at once.",
                    "Loop <code>i</code> over every start and <code>j</code> from <code>i</code> to <code>n - 1</code>.",
                    "Sum the booleans with <code>sum(...)</code>: <code>True</code> counts as 1, <code>False</code> as 0.",
                ],
                "why": [
                    "Each call removes one character from each end, so the recursion reaches the base case or a mismatch after at most n/2 levels, and the answer it gives is exactly the definition of a palindrome.",
                    "Nothing is remembered between ranges: checking <code>s[0..9]</code> re-walks <code>s[1..8]</code>, <code>s[2..7]</code>, … even if those were already checked as ranges of their own.",
                    "There are about n²/2 ranges and each can cost up to n/2 calls (think of <code>\"aaaa…\"</code>), giving <strong>O(n³)</strong> time.",
                    "Only one inward walk is active at a time, so the stack holds at most n/2 frames: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "There are 10 ranges. The four single letters hit <code>i &gt;= j</code> at once: 4 palindromes.",
                        "pal(0, 1) \"ab\" and pal(2, 3) \"ba\" fail on the first comparison. pal(1, 2) \"bb\": b = b, then pal(2, 1) has i &gt; j, so True. Count 5.",
                        "pal(0, 2) \"abb\" and pal(1, 3) \"bba\" fail at once (a ≠ b, b ≠ a).",
                        "pal(0, 3) \"abba\": a = a, then pal(1, 2) is walked <em>again</em>, then pal(2, 1). True. Count 6.",
                        "That took 13 calls for 10 ranges. The result is <strong>6</strong>.",
                    ],
                    [
                        "Three single letters: 3 palindromes.",
                        "pal(0, 1) \"ab\" and pal(1, 2) \"ba\" fail on their ends.",
                        "pal(0, 2) \"aba\": a = a, then pal(1, 1) is a single letter, True. Count 4.",
                        "7 calls in total. The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the base case <code>i &gt;= j</code> and not <code>i == j</code>?",
                     "Even-length ranges shrink past each other: \"bb\" calls pal(2, 1), where i &gt; j. That empty middle is a palindrome, so it must return True too."],
                    ["Why is it O(n³) when most checks stop after one comparison?",
                     "On random text they do, but on a string like \"aaaa…\" every range is a palindrome and every check walks all the way in. Big-O describes that worst case."],
                    ["Is <code>sum</code> over booleans safe in Python?",
                     "Yes. <code>bool</code> is a subclass of <code>int</code>, so <code>True + True == 2</code>."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: one line, <code>@cache</code> on <code>pal</code>.",
                    "The answer for a range never changes, and many outer ranges walk through the same inner ones. With a cache, each <code>(i, j)</code> is decided once and every later request is a lookup.",
                    "The recursion itself, the base case and the counting loop are identical, so it is easy to trust.",
                ],
                "steps": [
                    "Decorate <code>pal(i, j)</code> with <code>@cache</code>; the body is unchanged.",
                    "The base case <code>i &gt;= j</code> still returns <code>True</code>.",
                    "<code>s[i] == s[j] and pal(i + 1, j - 1)</code> now either computes the inner range once or reads it from the cache.",
                    "Sum <code>pal(i, j)</code> over all <code>i ≤ j</code> as before.",
                ],
                "why": [
                    "The cached value is exactly what the plain recursion would have returned, so the count is the same.",
                    "There are O(n²) distinct <code>(i, j)</code> pairs, and each does O(1) work outside its single recursive call, so the total is <strong>O(n²)</strong> time.",
                    "The cache holds up to n² entries and the stack still goes up to n/2 deep: <strong>O(n²)</strong> space.",
                    "This is the step that removes the repeated inward walks; the later steps only change how the same table is stored.",
                ],
                "dry": [
                    [
                        "The outer loop runs i = 0 first: pal(0, 0), pal(0, 1), pal(0, 2) are computed and cached.",
                        "pal(0, 3): a = a, so it computes pal(1, 2) and pal(2, 1) on the way in and caches both.",
                        "When the loop later reaches i = 1, j = 2, pal(1, 2) is a <em>cache hit</em>: no comparison is redone.",
                        "11 distinct states are computed instead of 13 calls. The result is <strong>6</strong>.",
                    ],
                    [
                        "pal(0, 0), pal(0, 1) are computed. pal(0, 2): a = a, computes and caches pal(1, 1).",
                        "At i = 1, j = 1 the loop asks for pal(1, 1) again: cache hit.",
                        "pal(1, 2) and pal(2, 2) are new. 6 states in all.",
                        "The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the memo help so little on \"abba\"?",
                     "Most ranges fail on their very first comparison and never recurse, so there is little to share. The saving is large exactly in the worst case, a long run of equal letters, where O(n³) becomes O(n²)."],
                    ["Is recursion depth a problem?",
                     "Depth is at most n/2, so for strings of a few thousand characters it can hit Python's default limit of 1000. The bottom-up versions avoid recursion entirely."],
                    ["Where is <code>cache</code> from?",
                     "<code>functools.cache</code>, which keys the cache on the arguments <code>(i, j)</code>. It needs hashable arguments, which integers are."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "What changed from the memo: the recursion is replaced by loops that fill a table <code>pal[i][j]</code> in an order where the inside is always ready first.",
                    "<code>pal[i][j]</code> reads <code>pal[i+1][j-1]</code>, which is in the row <em>below</em>. Filling <code>i</code> from n − 1 down to 0 guarantees that row is finished.",
                    "Ranges of length 1 and 2 (<code>j - i &lt; 2</code>) have no inside to look up: matching ends are enough.",
                ],
                "steps": [
                    "Create an n × n table of <code>False</code> and set <code>count = 0</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0, and <code>j</code> from <code>i</code> up to <code>n - 1</code>.",
                    "If <code>s[i] == s[j]</code> and either <code>j - i &lt; 2</code> or <code>pal[i + 1][j - 1]</code>, the range is a palindrome.",
                    "Set <code>pal[i][j] = True</code> and add 1 to <code>count</code> right there, so no second pass over the table is needed.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Every cell is decided by the same rule as the recursion, and the cell it reads is already final, so every cell is correct.",
                    "Each of the n(n + 1)/2 cells is filled once in O(1): <strong>O(n²)</strong> time, with no recursion overhead or depth limit.",
                    "The full table is <strong>O(n²)</strong> space, even though each row only ever reads the row just below it. The next step uses that.",
                ],
                "dry": [
                    [
                        "i = 3: only (3, 3) is True. i = 2: (2, 2) True, (2, 3) \"ba\" fails.",
                        "i = 1: (1, 1) True; (1, 2) \"bb\" has j − i = 1 &lt; 2 and b = b, so True; (1, 3) fails.",
                        "i = 0: (0, 0) True; (0, 1), (0, 2) fail; (0, 3) has a = a and reads pal[1][2] = True, so True.",
                        "True cells per row: 1 + 1 + 2 + 2. The count is <strong>6</strong>.",
                    ],
                    [
                        "i = 2: (2, 2) True.",
                        "i = 1: (1, 1) True; (1, 2) \"ba\" fails.",
                        "i = 0: (0, 0) True; (0, 1) fails; (0, 2) has a = a, j − i = 2, and reads pal[1][1] = True, so True.",
                        "The count is 1 + 1 + 2 = <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>i</code> go downwards?",
                     "Cell (i, j) needs (i + 1, j − 1). Going downwards, row i + 1 is complete before row i starts. Going upwards it would still be all <code>False</code>."],
                    ["What breaks if the test is <code>j - i &lt; 1</code> instead of <code>&lt; 2</code>?",
                     "Length-2 ranges would read pal[i+1][i], a cell below the diagonal that is never set, so \"bb\" is missed. On \"abba\" the count drops to 4."],
                    ["Does the order of <code>j</code> matter here?",
                     "No. Within a row, cells only read the row below, so <code>j</code> can go either way in the 2-D table."],
                ],
            },
            "Two rows": {
                "idea": [
                    "What changed from the 2-D table: only row <code>i + 1</code> is ever read while row <code>i</code> is built, so keep just that row, called <code>below</code>.",
                    "Each pass builds a fresh row <code>cur</code> from <code>below</code>, then hands it down: <code>below = cur</code>.",
                ],
                "steps": [
                    "Start with <code>below = [False] * n</code> and <code>count = 0</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0 and make a new <code>cur = [False] * n</code>.",
                    "For <code>j</code> from <code>i</code> to <code>n - 1</code>: if <code>s[i] == s[j]</code> and (<code>j - i &lt; 2</code> or <code>below[j - 1]</code>), set <code>cur[j] = True</code> and add 1 to <code>count</code>.",
                    "After the row, <code>below = cur</code>, so it becomes the row below for the next <code>i</code>.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "<code>below[j - 1]</code> holds exactly <code>pal[i+1][j-1]</code> from the full table, so every decision is the same.",
                    "The time is unchanged, <strong>O(n²)</strong>, because the same cells are computed.",
                    "Only two rows of length n exist at once: <strong>O(n)</strong> space, down from O(n²).",
                    "The count is added while filling, so throwing old rows away loses nothing.",
                ],
                "dry": [
                    [
                        "i = 3: cur = [F, F, F, T], count 1. i = 2: cur = [F, F, T, F], count 2.",
                        "i = 1: (1, 2) \"bb\" is True by the length rule. cur = [F, T, T, F], count 4.",
                        "i = 0: (0, 3) has a = a and reads below[2] = True (that is \"bb\"). cur = [T, F, F, T], count 6.",
                        "The result is <strong>6</strong>.",
                    ],
                    [
                        "i = 2: cur = [F, F, T], count 1.",
                        "i = 1: cur = [F, T, F], count 2.",
                        "i = 0: (0, 2) reads below[1] = True (the middle \"b\"). cur = [T, F, T], count 4.",
                        "The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why create a new <code>cur</code> every pass instead of reusing it?",
                     "If <code>cur</code> and <code>below</code> were the same list, writing row i would overwrite the row-below values still to be read. A fresh list keeps them apart; the one-row version shows how to avoid even that."],
                    ["Can I still recover the longest palindrome or list them all?",
                     "Not from the stored rows, since earlier rows are gone. You would have to record what you need (like the best range) while filling, which is what Longest Palindromic Substring does."],
                    ["Is creating a list per row slow?",
                     "It adds O(n) per row, which is already the cost of the row's loop, so the total stays O(n²)."],
                ],
            },
            "One row, j right to left": {
                "idea": [
                    "What changed from two rows: a single list <code>pal</code> holds both rows at once, overwritten cell by cell.",
                    "Cell j of row i reads only cell <code>j - 1</code> of the row below, the cell to its <em>left</em>. If <code>j</code> sweeps right to left, cell <code>j - 1</code> has not been overwritten yet, so it still holds row i + 1.",
                ],
                "steps": [
                    "Start with <code>pal = [False] * n</code> and <code>count = 0</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0.",
                    "Loop <code>j</code> from <code>n - 1</code> down to <code>i</code>; this direction is the whole trick.",
                    "Set <code>pal[j] = s[i] == s[j] and (j - i &lt; 2 or pal[j - 1])</code>, which overwrites row i + 1's value at j with row i's.",
                    "Add <code>pal[j]</code> to <code>count</code>, then return <code>count</code> at the end.",
                ],
                "why": [
                    "When cell j is written, cells to its left still hold row i + 1 and cells to its right already hold row i. The read only looks left, so it always sees the right row.",
                    "Every cell is assigned (not just set to True), so stale <code>True</code> values from the row below are cleared when a range fails.",
                    "Same cells, same work: <strong>O(n²)</strong> time and <strong>O(n)</strong> space, with no second list at all.",
                ],
                "dry": [
                    [
                        "After i = 3: pal = [F, F, F, T]. After i = 2: [F, F, T, F] (pal[3] reset to False for \"ba\").",
                        "i = 1, j = 3 → 1: \"bba\" False; \"bb\" True; \"b\" True. pal = [F, T, T, F], count 4.",
                        "i = 0, j = 3 first: a = a and pal[2] still holds row 1's True for \"bb\", so \"abba\" is True.",
                        "Then j = 2, 1 are False and j = 0 is True. pal = [T, F, F, T], count <strong>6</strong>.",
                    ],
                    [
                        "After i = 2: [F, F, T]. After i = 1: [F, T, F].",
                        "i = 0, j = 2: a = a and pal[1] still holds row 1's True for \"b\", so \"aba\" counts.",
                        "j = 1: \"ab\" False. j = 0: True. pal = [T, F, T].",
                        "The count is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong if <code>j</code> runs left to right?",
                     "Cell j − 1 would already hold row i, not row i + 1. On \"abba\" the count comes out as 5 and on \"aba\" as 3, both wrong."],
                    ["Why is <code>pal[j] = ...</code> an assignment rather than an <code>if</code>?",
                     "The list still holds the previous row's value. If a range is not a palindrome, the cell must be reset to False, or the next row would read a stale True."],
                    ["Is this worth it over two rows?",
                     "Both are O(n) space. One row saves a list allocation per pass and is the usual final step of a DP ladder, but two rows is easier to get right under pressure."],
                ],
            },
            "Expand around each centre": {
                "idea": [
                    "Turn the recurrence inside out: instead of asking whether a range is a palindrome, start from its middle and grow outwards while the ends match.",
                    "Every palindrome has a centre: a character (odd length) or the gap between two characters (even length). That is <code>2n - 1</code> centres in all.",
                    "Each successful step outwards is one more palindrome, so counting is just counting steps.",
                ],
                "steps": [
                    "Loop <code>centre</code> over <code>range(2 * len(s) - 1)</code>.",
                    "Set <code>lo, hi = centre // 2, (centre + 1) // 2</code>: an even <code>centre</code> gives lo = hi (a letter), an odd one gives hi = lo + 1 (a gap).",
                    "While <code>lo &gt;= 0</code>, <code>hi &lt; len(s)</code> and <code>s[lo] == s[hi]</code>: add 1 to <code>count</code>, then widen with <code>lo -= 1</code>, <code>hi += 1</code>.",
                    "Stop at the first mismatch or edge: any wider range around this centre would contain the mismatch.",
                    "Return <code>count</code>.",
                ],
                "why": [
                    "Each palindrome is found exactly once, from its own centre, and growing stops at the first failure because a wider range with the same centre includes the failing pair.",
                    "Each centre expands at most n/2 times, so the worst case (all equal letters) is <strong>O(n²)</strong> time.",
                    "Only <code>lo</code>, <code>hi</code> and <code>count</code> are stored: <strong>O(1)</strong> space, better than every table version.",
                ],
                "dry": [
                    [
                        "Centres 0, 2, 4, 6 are the four letters: each counts itself, then the next step mismatches or hits an edge. Count 4.",
                        "Centres 1 and 5 are the gaps a|b and b|a: the first comparison fails.",
                        "Centre 3 is the gap b|b: \"bb\" matches (count 5), then lo = 0, hi = 3 gives a = a, \"abba\" (count 6), then lo = −1 stops.",
                        "The result is <strong>6</strong>.",
                    ],
                    [
                        "Centre 0 (\"a\") counts 1; centre 4 (last \"a\") counts 1.",
                        "Centres 1 and 3 are gaps between different letters: 0.",
                        "Centre 2 (\"b\"): counts \"b\", then lo = 0, hi = 2 gives a = a, counts \"aba\", then lo = −1 stops.",
                        "The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>2n - 1</code> centres rather than n?",
                     "Even-length palindromes like \"bb\" are centred on a gap, not a letter. Using only the n letter centres counts 4 on \"abba\" instead of 6."],
                    ["How does <code>centre // 2, (centre + 1) // 2</code> cover both cases?",
                     "For centre = 2k both give k, a single letter. For centre = 2k + 1 they give k and k + 1, the gap between them."],
                    ["Is there anything faster?",
                     "Manacher's algorithm reuses expansions across centres and runs in O(n). It is rarely expected in interviews; this method is the standard answer."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest palindromic substring
    "longest-palindromic-substring": {
        "examples": [
            {"call": 'longest_palindrome("banana")', "expect": "'anana'"},
            {"call": 'longest_palindrome("cbbd")', "expect": "'bb'"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Use the same inward check as counting: <code>s[i..j]</code> is a palindrome when its ends match and its inside is one.",
                    "Test every range and keep the widest that passes, tracked as a half-open pair <code>lo, hi</code> so the answer is <code>s[lo:hi]</code>.",
                    "Skip any range no wider than the current best before calling <code>pal</code>: it cannot improve the answer, so there is no point checking it.",
                ],
                "steps": [
                    "Define <code>pal(i, j)</code>: <code>True</code> if <code>i &gt;= j</code>, else <code>s[i] == s[j] and pal(i + 1, j - 1)</code>.",
                    "Start with <code>lo, hi = 0, 1</code>: the first letter is always a palindrome of width 1.",
                    "Loop <code>i</code> over starts and <code>j</code> from <code>i</code> to the end.",
                    "If <code>j + 1 - i &gt; hi - lo</code> (strictly wider) and <code>pal(i, j)</code>, set <code>lo, hi = i, j + 1</code>.",
                    "Return <code>s[lo:hi]</code>.",
                ],
                "why": [
                    "Every range is either checked or provably no wider than a palindrome already found, so the widest palindrome is never skipped.",
                    "The width test runs first, so the <code>and</code> skips <code>pal</code> for ranges that cannot win. This prunes a lot in practice but not in the worst case.",
                    "Up to n²/2 ranges, each check up to n/2 calls: <strong>O(n³)</strong> time. The recursion is at most n/2 deep: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Start: best = s[0:1] = \"b\".",
                        "i = 0: \"ba\", \"ban\", \"bana\", \"banan\", \"banana\" all fail on the first comparison (b against a or n).",
                        "i = 1: \"an\" fails; \"ana\" passes → lo, hi = 1, 4; \"anan\" fails; \"anana\" checks a = a, n = n, then the middle a, passes → lo, hi = 1, 6.",
                        "From i = 2 on, no range is wider than 5, so <code>pal</code> is never called again.",
                        "The result is <strong>'anana'</strong>.",
                    ],
                    [
                        "Start: best = \"c\".",
                        "i = 0: \"cb\", \"cbb\", \"cbbd\" all fail on c.",
                        "i = 1: \"bb\" passes → lo, hi = 1, 3; \"bbd\" is wider but fails (b ≠ d).",
                        "i = 2: \"bd\" has width 2, not wider than 2, so it is skipped.",
                        "The result is <strong>'bb'</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt;</code> and not <code>&gt;=</code> in the width test?",
                     "With <code>&gt;=</code> every equal-width range would also be checked, wasting calls, and a later tie would replace the first one found. Either answer is accepted, but <code>&gt;</code> does less work."],
                    ["Why start with <code>lo, hi = 0, 1</code>?",
                     "Any single letter is a palindrome, so width 1 is a safe floor and the loop never has to handle \"nothing found\". The problem guarantees s is non-empty."],
                    ["Different approaches return different answers on \"babad\". Is that a bug?",
                     "No. \"bab\" and \"aba\" are both longest. This version scans starts left to right and returns \"bab\"; the table versions scan i downwards and return \"aba\"."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>pal</code>, so any range checked once is never walked again.",
                    "That caps the total checking work at one O(1) step per range, which removes the extra factor of n from the worst case.",
                ],
                "steps": [
                    "Decorate <code>pal(i, j)</code> with <code>@cache</code>; the body and base case are unchanged.",
                    "Start with <code>lo, hi = 0, 1</code>.",
                    "Loop every <code>(i, j)</code>; skip it unless it is strictly wider than the best.",
                    "Call <code>pal(i, j)</code>, which now reuses any inner range already decided.",
                    "On success set <code>lo, hi = i, j + 1</code>; return <code>s[lo:hi]</code>.",
                ],
                "why": [
                    "Cached answers equal the uncached ones, so the result is the same as plain recursion.",
                    "At most n² distinct states, each O(1) besides its single recursive call: <strong>O(n²)</strong> time.",
                    "The cache can hold <strong>O(n²)</strong> entries, which is the price of the speed-up.",
                ],
                "dry": [
                    [
                        "The checks are the same as plain recursion: the five ranges from i = 0, then \"an\", \"ana\", \"anan\", \"anana\".",
                        "\"ana\" caches pal(1, 3) and pal(2, 2). \"anana\" caches pal(1, 5), pal(2, 4) and pal(3, 3).",
                        "No state repeats in this run, so the cache never hits: the width test already pruned the overlap.",
                        "The result is <strong>'anana'</strong>.",
                    ],
                    [
                        "\"cb\", \"cbb\", \"cbbd\" fail at once and are cached.",
                        "\"bb\" caches pal(1, 2) and the empty middle pal(2, 1); best becomes 1..3.",
                        "\"bbd\" fails at once. Again no cache hits.",
                        "The result is <strong>'bb'</strong>.",
                    ],
                ],
                "faq": [
                    ["If the cache never hits on these examples, why bother?",
                     "The guarantee is about the worst case. On \"aaaa…\" every range is a palindrome and every check walks in; there the cache turns O(n³) into O(n²)."],
                    ["Does the width pruning still matter with a cache?",
                     "Yes, it avoids even creating cache entries for ranges that cannot win, but it does not change the O(n²) bound."],
                    ["What is the space cost compared with expand-around-centre?",
                     "O(n²) for the cache versus O(1). That is why the centre method is preferred for this problem in practice."],
                ],
            },
            "Bottom-up 2-D table": {
                "idea": [
                    "What changed from the memo: loops fill <code>pal[i][j]</code> directly, rows from the bottom up, so the inside cell <code>pal[i+1][j-1]</code> is always ready.",
                    "It is the Palindromic Substrings table, except that each True cell is compared with the best width instead of being counted.",
                ],
                "steps": [
                    "Create an n × n table of <code>False</code> and set <code>lo, hi = 0, 1</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0 and <code>j</code> from <code>i</code> to <code>n - 1</code>.",
                    "If <code>s[i] == s[j]</code> and (<code>j - i &lt; 2</code> or <code>pal[i + 1][j - 1]</code>), set <code>pal[i][j] = True</code>.",
                    "If that palindrome is strictly wider than <code>hi - lo</code>, record <code>lo, hi = i, j + 1</code>.",
                    "Return <code>s[lo:hi]</code>.",
                ],
                "why": [
                    "Each cell uses the same rule as the recursion and reads a finished cell, so every palindrome in the string is marked and compared.",
                    "Each of the n(n + 1)/2 cells takes O(1): <strong>O(n²)</strong> time, no recursion.",
                    "The table is <strong>O(n²)</strong> space, though each row only needs the one below it.",
                ],
                "dry": [
                    [
                        "i = 5, 4: only single letters, not wider than 1.",
                        "i = 3: (3, 5) \"ana\" reads pal[4][4] = True → best = 3..6.",
                        "i = 2: (2, 4) \"nan\" is True but width 3 is not wider.",
                        "i = 1: (1, 3) \"ana\" True, not wider; (1, 5) \"anana\" reads pal[2][4] = True → best = 1..6. i = 0: nothing new.",
                        "The result is <strong>'anana'</strong>.",
                    ],
                    [
                        "i = 3, 2: single letters only; (2, 3) \"bd\" fails.",
                        "i = 1: (1, 2) \"bb\" is True by the length rule → best = 1..3; (1, 3) \"bbd\" fails.",
                        "i = 0: \"c\" only; every range starting with c fails.",
                        "The result is <strong>'bb'</strong>.",
                    ],
                ],
                "faq": [
                    ["Why update the best inside the fill rather than after it?",
                     "It saves a second O(n²) scan of the table, and it lets the two-row and one-row versions work, since they throw rows away."],
                    ["Could I fill by length instead of by row?",
                     "Yes, lengths 1, 2, 3, … also guarantee the inside is ready. Row order is used here because it leads straight to the one-row trick."],
                    ["Which palindrome is returned on a tie?",
                     "The first one met in this fill order: the one with the largest start <code>i</code>, because rows are filled from the bottom. On \"babad\" that is \"aba\"."],
                ],
            },
            "Two rows": {
                "idea": [
                    "What changed from the 2-D table: row i only reads row i + 1, so keep just that row as <code>below</code> and build each new row in <code>cur</code>.",
                    "The best range is recorded while filling, so nothing is lost when old rows are dropped.",
                ],
                "steps": [
                    "Start with <code>below = [False] * n</code> and <code>lo, hi = 0, 1</code>.",
                    "For <code>i</code> from <code>n - 1</code> down to 0, make <code>cur = [False] * n</code>.",
                    "For each <code>j ≥ i</code>: if <code>s[i] == s[j]</code> and (<code>j - i &lt; 2</code> or <code>below[j - 1]</code>), set <code>cur[j] = True</code>.",
                    "If it is strictly wider than the best, set <code>lo, hi = i, j + 1</code>.",
                    "After the row, <code>below = cur</code>; finally return <code>s[lo:hi]</code>.",
                ],
                "why": [
                    "<code>below[j - 1]</code> is the same value as <code>pal[i+1][j-1]</code> in the full table, so the same palindromes are found in the same order.",
                    "<strong>O(n²)</strong> time as before; only two rows exist at once, so <strong>O(n)</strong> space.",
                    "The answer is a range, not a table cell, so <code>lo</code> and <code>hi</code> are all that needs to survive.",
                ],
                "dry": [
                    [
                        "i = 3: (3, 5) reads below[4] (row 4's \"n\") = True → best = 3..6.",
                        "i = 2: (2, 4) reads below[3] = True (\"nan\"), width 3, not wider.",
                        "i = 1: (1, 3) reads below[2] = True; (1, 5) reads below[4] = True (row 2's \"nan\") → best = 1..6.",
                        "i = 0: only \"b\".",
                        "The result is <strong>'anana'</strong>.",
                    ],
                    [
                        "i = 3: cur = [F, F, F, T]. i = 2: cur = [F, F, T, F].",
                        "i = 1: (1, 2) is True by the length rule → best = 1..3. cur = [F, T, T, F].",
                        "i = 0: (0, 3) needs c = d, fails. Only (0, 0) is True.",
                        "The result is <strong>'bb'</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>below</code> start as all <code>False</code>?",
                     "It stands for row n, which does not exist. It is only read when <code>j - i ≥ 2</code>, which cannot happen in row n − 1, so its values never matter."],
                    ["Can I reconstruct all palindromes afterwards?",
                     "No, only the best one was recorded. Keep the 2-D table if you need more than that."],
                    ["Is this better than expand-around-centre?",
                     "No. Both are O(n²) time and the centre method uses O(1) space. This step exists to show the table shrinking."],
                ],
            },
            "One row, j right to left": {
                "idea": [
                    "What changed from two rows: one list <code>pal</code> holds both rows. Cell j reads only <code>pal[j - 1]</code>, the cell to its left.",
                    "Sweeping <code>j</code> from right to left means that left cell has not been overwritten yet in this pass, so it still holds row i + 1.",
                ],
                "steps": [
                    "Start with <code>pal = [False] * n</code> and <code>lo, hi = 0, 1</code>.",
                    "Loop <code>i</code> from <code>n - 1</code> down to 0.",
                    "Loop <code>j</code> from <code>n - 1</code> down to <code>i</code>.",
                    "Assign <code>pal[j] = s[i] == s[j] and (j - i &lt; 2 or pal[j - 1])</code>.",
                    "If <code>pal[j]</code> is True and wider than the best, set <code>lo, hi = i, j + 1</code>; return <code>s[lo:hi]</code> at the end.",
                ],
                "why": [
                    "At the moment cell j is written, cells left of j still hold row i + 1, so the one read is the right one.",
                    "Assigning (not just setting True) clears stale values when a range fails.",
                    "<strong>O(n²)</strong> time and <strong>O(n)</strong> space, using a single list.",
                ],
                "dry": [
                    [
                        "i = 3, j = 5: a = a and pal[4] still holds row 4's True → \"ana\", best = 3..6.",
                        "i = 2, j = 4: n = n and pal[3] holds row 3's True → \"nan\", width 3, not wider.",
                        "i = 1, j = 5 first: pal[4] still holds row 2's True for \"nan\" → \"anana\", best = 1..6.",
                        "Later cells and i = 0 find nothing wider.",
                        "The result is <strong>'anana'</strong>.",
                    ],
                    [
                        "After i = 3: [F, F, F, T]. After i = 2: [F, F, T, F].",
                        "i = 1: j = 3 \"bbd\" False; j = 2 \"bb\" True → best = 1..3; j = 1 True.",
                        "i = 0: every range from c fails except \"c\" itself.",
                        "The result is <strong>'bb'</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is right to left essential here?",
                     "Left to right would overwrite <code>pal[j - 1]</code> with row i before cell j reads it, mixing two rows. On Palindromic Substrings that turns \"abba\" from 6 into 5."],
                    ["Why check <code>pal[j]</code> before the width?",
                     "Only palindromes may become the answer. The width test alone would accept any wide range."],
                    ["Does the best range need its own row?",
                     "No. <code>lo</code> and <code>hi</code> are two integers updated as soon as a winner appears."],
                ],
            },
            "Expand around each centre": {
                "idea": [
                    "Grow a palindrome outwards from each of the <code>2n - 1</code> centres (letters and gaps) for as long as the ends match.",
                    "The widest expansion from any centre is the answer. This needs no table at all.",
                    "The <code>while</code> loop overshoots by one on each side, so the palindrome it found is <code>s[lo + 1:hi]</code>, of width <code>hi - lo - 1</code>.",
                ],
                "steps": [
                    "Start with <code>best_lo, best_hi = 0, 0</code> (an empty best).",
                    "For each <code>centre</code>, set <code>lo, hi = centre // 2, (centre + 1) // 2</code>.",
                    "While in bounds and <code>s[lo] == s[hi]</code>: <code>lo -= 1</code>, <code>hi += 1</code>.",
                    "If <code>hi - lo - 1 &gt; best_hi - best_lo</code>, set <code>best_lo, best_hi = lo + 1, hi</code>.",
                    "Return <code>s[best_lo:best_hi]</code>.",
                ],
                "why": [
                    "Every palindrome is the maximal expansion of its centre or lies inside one, so the widest maximal expansion is the longest palindrome.",
                    "Each centre expands at most n/2 steps: <strong>O(n²)</strong> time in the worst case, and often much less.",
                    "Only a few indices are kept: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Centre 0 (\"b\"): stops at once with lo = −1, hi = 1. Width 1 → best = 0..1.",
                        "Centre 4 (the \"n\" at index 2): \"n\", then \"ana\", then b ≠ n stops with lo = 0, hi = 4. Width 3 → best = 1..4.",
                        "Centre 6 (the \"a\" at index 3): \"a\", \"nan\", \"anana\", then lo = −1 stops. lo = 0, hi = 6, width 5 → best = 1..6.",
                        "Centre 8 gives only \"ana\" again; the gaps give nothing.",
                        "The result is <strong>'anana'</strong>.",
                    ],
                    [
                        "Centre 0 (\"c\"): width 1 → best = 0..1.",
                        "Centre 3 (gap b|b): \"bb\" matches, then c ≠ d stops with lo = 0, hi = 3. Width 2 → best = 1..3.",
                        "No other centre beats width 2.",
                        "The result is <strong>'bb'</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>lo + 1</code> and <code>hi</code> rather than <code>lo</code> and <code>hi + 1</code>?",
                     "The loop exits only after stepping past the palindrome: <code>lo</code> and <code>hi</code> point at the first pair that failed or fell off the edge. The real palindrome is one in from each side."],
                    ["What does a gap centre that fails immediately do?",
                     "lo and hi are adjacent and unequal, so the width is <code>hi - lo - 1 = 0</code>. It can never beat the best, which is fine."],
                    ["Why start with an empty best rather than <code>0, 1</code>?",
                     "Centre 0 always produces width 1 and replaces it, so both work. Starting empty keeps all updates in one place."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ matrix chain
    "matrix-chain-multiplication": {
        "examples": [
            {"call": "matrix_chain_order([40, 20, 30, 10, 30])", "expect": "26000"},
            {"call": "matrix_chain_order([2, 1, 3, 4])", "expect": "20"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Matrix i has shape <code>arr[i-1] × arr[i]</code>. Whatever the bracketing, some multiplication happens <em>last</em>: it joins the product of matrices i..k with the product of k+1..j.",
                    "That last multiplication costs <code>arr[i-1] · arr[k] · arr[j]</code>, and the two sides are independent smaller problems.",
                    "Try every split point k and keep the cheapest: that is an interval recursion on <code>(i, j)</code>.",
                ],
                "steps": [
                    "Define <code>cost(i, j)</code> = the cheapest way to multiply matrices i..j (1-indexed).",
                    "If <code>i &gt;= j</code> there is at most one matrix, nothing to multiply: return 0.",
                    "Otherwise, for each <code>k</code> in <code>range(i, j)</code>, add <code>cost(i, k)</code>, <code>cost(k + 1, j)</code> and <code>arr[i - 1] * arr[k] * arr[j]</code>.",
                    "Return the <code>min</code> of those totals.",
                    "The answer is <code>cost(1, len(arr) - 1)</code>.",
                ],
                "why": [
                    "Every bracketing has exactly one last multiplication, so trying every k covers every bracketing, and each side is solved optimally by induction.",
                    "Without a cache the same sub-chains are solved over and over. The number of calls grows like the Catalan numbers, roughly 4<sup>n</sup>: <strong>exponential</strong> time.",
                    "The recursion goes at most n levels deep: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "A1 40×20, A2 20×30, A3 30×10, A4 10×30. cost(1, 4) tries k = 1, 2, 3.",
                        "k = 1: 0 + cost(2, 4) + 40·20·30 = 12000 + 24000 = 36000.",
                        "k = 2: cost(1, 2) + cost(3, 4) + 40·30·30 = 24000 + 9000 + 36000 = 69000.",
                        "k = 3: cost(1, 3) + 0 + 40·10·30 = 14000 + 12000 = 26000. cost(1, 3) itself picks k = 1: 6000 + 8000.",
                        "cost(2, 3) and cost(1, 2) are each solved twice; 27 calls in all. The result is <strong>26000</strong>.",
                    ],
                    [
                        "A1 2×1, A2 1×3, A3 3×4. cost(1, 3) tries k = 1 and k = 2.",
                        "k = 1, A1(A2A3): cost(2, 3) = 1·3·4 = 12, plus 2·1·4 = 8, total 20.",
                        "k = 2, (A1A2)A3: cost(1, 2) = 2·1·3 = 6, plus 2·3·4 = 24, total 30.",
                        "9 calls. The result is <strong>20</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>arr[i - 1] * arr[k] * arr[j]</code>?",
                     "The left product is <code>arr[i-1] × arr[k]</code> and the right is <code>arr[k] × arr[j]</code>. Multiplying a p×q by a q×r matrix costs p·q·r scalar multiplications."],
                    ["Why split on the last multiplication rather than the first?",
                     "The last one cleanly splits the chain into two independent halves. A first multiplication can happen anywhere and leaves a chain with a merged matrix in the middle, which is harder to describe as a subproblem."],
                    ["Could a greedy rule work, like always multiplying the cheapest pair first?",
                     "No simple greedy is known to be optimal here; the cost of a choice depends on shapes it creates later. That is why every split is tried."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>cost</code>.",
                    "A sub-chain <code>(i, j)</code> has one best cost no matter which outer bracketing asked for it, so solving it once and reusing the answer is safe.",
                ],
                "steps": [
                    "Decorate <code>cost(i, j)</code> with <code>@cache</code>.",
                    "Keep the base case: <code>i &gt;= j</code> returns 0.",
                    "Keep the recurrence: the <code>min</code> over <code>k</code> of left + right + <code>arr[i - 1] * arr[k] * arr[j]</code>.",
                    "Repeated sub-chains are now cache lookups.",
                    "Return <code>cost(1, len(arr) - 1)</code>.",
                ],
                "why": [
                    "The cached values are the same optimal costs, so the answer is unchanged.",
                    "There are about n²/2 sub-chains and each tries up to n splits once: <strong>O(n³)</strong> time.",
                    "The cache holds O(n²) entries, plus O(n) stack: <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "cost(1, 4), k = 1 computes cost(2, 4), which caches cost(2, 3) = 6000 and cost(3, 4) = 9000.",
                        "k = 2 computes cost(1, 2) = 24000; cost(3, 4) is a cache hit.",
                        "k = 3 computes cost(1, 3) = 14000; inside it, cost(2, 3) and cost(1, 2) are cache hits.",
                        "10 distinct states instead of 27 calls. cost(1, 4) = 14000 + 12000 = <strong>26000</strong>.",
                    ],
                    [
                        "cost(1, 3), k = 1 computes cost(1, 1) = 0 and cost(2, 3) = 12.",
                        "k = 2 computes cost(1, 2) = 6 and cost(3, 3) = 0.",
                        "6 states, nothing repeated in such a short chain. min(20, 30) = <strong>20</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is it O(n³) and not O(n²)?",
                     "There are O(n²) states, but each one loops over up to n split points. That inner loop is the third factor of n."],
                    ["Does <code>@cache</code> work with the list <code>arr</code>?",
                     "Yes, because <code>arr</code> is not an argument; it is read from the enclosing scope. Only <code>(i, j)</code> form the cache key."],
                    ["Can I also recover the bracketing?",
                     "Store the best k for each <code>(i, j)</code> alongside the cost, then rebuild the brackets recursively from <code>(1, n)</code>."],
                ],
            },
            "Bottom-up by length": {
                "idea": [
                    "What changed from the memo: the table is filled by loops instead of recursion. A chain only depends on strictly shorter chains, so fill by chain length 2, 3, …, n.",
                    "Unlike the palindrome tables, there is no row-saving step after this: a cell reads its whole row to the left and its whole column below, so the full table is needed.",
                ],
                "steps": [
                    "Let <code>n = len(arr) - 1</code> matrices and create <code>dp</code> of size (n + 1) × (n + 1), all 0. Single matrices (<code>dp[i][i]</code>) stay 0.",
                    "Loop <code>length</code> from 2 to n, and <code>i</code> from 1 to <code>n - length + 1</code>; set <code>j = i + length - 1</code>.",
                    "Set <code>dp[i][j]</code> to the min over <code>k</code> in <code>range(i, j)</code> of <code>dp[i][k] + dp[k + 1][j] + arr[i - 1] * arr[k] * arr[j]</code>.",
                    "Both <code>dp[i][k]</code> and <code>dp[k + 1][j]</code> are shorter chains, so they are already final.",
                    "Return <code>dp[1][n]</code> (or 0 if there are no matrices).",
                ],
                "why": [
                    "Filling by length is a valid order because every split produces two strictly shorter chains.",
                    "O(n²) cells, each with up to n splits: <strong>O(n³)</strong> time.",
                    "The 2-D table is <strong>O(n²)</strong> space, with no recursion.",
                ],
                "dry": [
                    [
                        "Length 2: dp[1][2] = 40·20·30 = 24000, dp[2][3] = 20·30·10 = 6000, dp[3][4] = 30·10·30 = 9000.",
                        "Length 3: dp[1][3] = min(k=1: 14000, k=2: 36000) = 14000; dp[2][4] = min(k=2: 27000, k=3: 12000) = 12000.",
                        "Length 4: dp[1][4] = min(k=1: 36000, k=2: 69000, k=3: 26000).",
                        "The result is <strong>26000</strong>.",
                    ],
                    [
                        "Length 2: dp[1][2] = 2·1·3 = 6, dp[2][3] = 1·3·4 = 12.",
                        "Length 3: dp[1][3] = min(k=1: 0 + 12 + 8 = 20, k=2: 6 + 0 + 24 = 30).",
                        "The result is <strong>20</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>i</code> stop at <code>n - length + 1</code>?",
                     "The chain must end by matrix n: <code>j = i + length - 1 ≤ n</code> gives <code>i ≤ n - length + 1</code>. The <code>range</code> end is <code>n - length + 2</code> because it is exclusive."],
                    ["Why can't this be reduced to one row like the palindrome tables?",
                     "<code>dp[i][j]</code> reads every <code>dp[i][k]</code> to its left and every <code>dp[k+1][j]</code> below it, not just one neighbouring row. All of those must be kept."],
                    ["Is anything faster known?",
                     "Hu and Shing found an O(n log n) algorithm, but it is far beyond interview scope; O(n³) DP is the expected answer."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ burst balloons
    "burst-balloons": {
        "examples": [
            {"call": "max_coins([3, 1, 5, 8])", "expect": "167"},
            {"call": "max_coins([1, 5])", "expect": "10"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Picking the <em>first</em> balloon to burst does not split the problem: its neighbours join up and change everyone else's coins.",
                    "Pick the <em>last</em> balloon <code>k</code> to burst between two walls <code>l</code> and <code>r</code> instead. When it goes, everything between the walls is gone, so its neighbours are exactly <code>vals[l]</code> and <code>vals[r]</code>, and the two sides never touch each other.",
                    "Pad the list with 1 at both ends, <code>vals = [1] + nums + [1]</code>, so the outer walls are permanent and worth 1.",
                ],
                "steps": [
                    "Define <code>best(l, r)</code> = the most coins from bursting everything strictly between <code>l</code> and <code>r</code>.",
                    "If <code>r - l &lt; 2</code> nothing lies between them: return 0.",
                    "For each <code>k</code> in <code>range(l + 1, r)</code> as the last balloon: <code>best(l, k) + vals[l] * vals[k] * vals[r] + best(k, r)</code>.",
                    "Return the <code>max</code> of those.",
                    "The answer is <code>best(0, len(vals) - 1)</code>.",
                ],
                "why": [
                    "Every burst order has a last balloon between the walls, and once it is fixed the left and right parts are independent, so trying every k covers every order.",
                    "Note the walls are shared: <code>k</code> is the right wall of the left part and the left wall of the right part, because it is still alive while they are burst.",
                    "Without a cache, overlapping intervals are re-solved many times: <strong>exponential</strong> time. The recursion depth is at most n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "vals = [1, 3, 1, 5, 8, 1]. best(0, 5) tries each balloon last: k = 1, 2, 3, 4 give 162, 52, 75, 167.",
                        "k = 4 (the 8 last): best(0, 4) + 1·8·1 + 0 = 159 + 8.",
                        "best(0, 4) = 159 with the 3 last: 0 + 1·3·8 + best(1, 4) = 24 + 135.",
                        "best(1, 4) = 135 with the 5 last: best(1, 3) + 3·5·8 = 15 + 120, where best(1, 3) = 3·1·5 = 15.",
                        "Burst order 1, 5, 3, 8 gives 15 + 120 + 24 + 8. 81 calls in all. The result is <strong>167</strong>.",
                    ],
                    [
                        "vals = [1, 1, 5, 1]. best(0, 3) tries k = 1 and k = 2.",
                        "k = 1 (the 1 last): 0 + 1·1·1 + best(1, 3) = 1 + 5 = 6, since best(1, 3) bursts the 5 between 1 and 1.",
                        "k = 2 (the 5 last): best(0, 2) + 1·5·1 + 0 = 5 + 5 = 10, since best(0, 2) bursts the 1 between 1 and 5.",
                        "The result is <strong>10</strong>: burst the small one first so the 5 is used twice.",
                    ],
                ],
                "faq": [
                    ["Why does choosing the first balloon fail to split the problem?",
                     "After bursting it, its left and right neighbours become adjacent, so the left part's coins depend on the right part. Choosing the last balloon keeps it as a fixed wall between the two parts."],
                    ["Why <code>best(l, k)</code> and <code>best(k, r)</code>, not <code>k - 1</code> and <code>k + 1</code>?",
                     "<code>l</code> and <code>r</code> are exclusive walls. Balloon k is alive during both sub-problems, so it is the wall for each."],
                    ["Does a greedy rule like bursting the smallest first work?",
                     "No. On [3, 1, 5, 8], always bursting the smallest remaining balloon earns 78, far below 167."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>best</code>.",
                    "The interval <code>(l, r)</code> fully describes a sub-problem: the walls are fixed and everything inside is unburst, regardless of what happened outside. So its answer can be stored and reused.",
                ],
                "steps": [
                    "Build <code>vals = [1] + nums + [1]</code>.",
                    "Decorate <code>best(l, r)</code> with <code>@cache</code>.",
                    "Base case: <code>r - l &lt; 2</code> returns 0.",
                    "Recurrence: the <code>max</code> over <code>k</code> of <code>best(l, k) + vals[l] * vals[k] * vals[r] + best(k, r)</code>.",
                    "Return <code>best(0, len(vals) - 1)</code>.",
                ],
                "why": [
                    "Cached values are the same optimal answers, so correctness carries over from the recursion.",
                    "There are about n²/2 intervals, each trying up to n choices of k once: <strong>O(n³)</strong> time.",
                    "The cache holds <strong>O(n²)</strong> entries; the stack is O(n).",
                ],
                "dry": [
                    [
                        "best(0, 5) with k = 1 computes best(1, 5), which in turn computes and caches best(1, 3), best(1, 4), best(2, 5), …",
                        "With k = 4 it needs best(0, 4); its sub-intervals such as best(1, 4) = 135 are cache hits.",
                        "Only 15 distinct intervals are solved instead of 81 calls.",
                        "best(0, 5) = best(0, 4) + 8 = 159 + 8 = <strong>167</strong>.",
                    ],
                    [
                        "best(0, 3), k = 1: computes best(0, 1) = 0 and best(1, 3) = 5. Total 6.",
                        "k = 2: computes best(0, 2) = 5 and best(2, 3) = 0. Total 10.",
                        "6 states. The result is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the state just <code>(l, r)</code> and not the set of burst balloons?",
                     "Because of the last-balloon choice: inside a sub-problem the walls l and r are guaranteed alive and everything between is untouched. That is a far smaller state than a subset, which would be 2<sup>n</sup>."],
                    ["What about balloons with value 0?",
                     "They work unchanged: any product involving them is 0, and the max still picks the best order. The tests include zeros."],
                    ["Why pad with 1s rather than special-casing the edges?",
                     "A missing neighbour counts as 1 in the problem, so a 1 wall gives the right product with no extra branches."],
                ],
            },
            "Bottom-up by gap": {
                "idea": [
                    "What changed from the memo: loops fill <code>dp[l][r]</code> in an order where both sub-intervals are ready. Both <code>(l, k)</code> and <code>(k, r)</code> have a smaller gap <code>r - l</code>, so fill by gap from 2 upwards.",
                    "Gaps 0 and 1 have no balloon inside and stay 0. As with Matrix Chain, each cell reads a whole row and column, so the table cannot be shrunk.",
                ],
                "steps": [
                    "Build <code>vals</code>, let <code>n = len(vals)</code>, and create an n × n table <code>dp</code> of zeros.",
                    "Loop <code>gap</code> from 2 to <code>n - 1</code>, and <code>l</code> from 0 to <code>n - gap - 1</code>; set <code>r = l + gap</code>.",
                    "Set <code>dp[l][r]</code> to the max over <code>k</code> in <code>range(l + 1, r)</code> of <code>dp[l][k] + vals[l] * vals[k] * vals[r] + dp[k][r]</code>.",
                    "Both <code>dp[l][k]</code> and <code>dp[k][r]</code> have a smaller gap, so they are final.",
                    "Return <code>dp[0][n - 1]</code>, the whole row between the two padding walls.",
                ],
                "why": [
                    "The fill order respects every dependency, and each cell applies the same last-balloon rule, so <code>dp[0][n-1]</code> is the true maximum.",
                    "O(n²) cells, each with up to n choices: <strong>O(n³)</strong> time.",
                    "The table is <strong>O(n²)</strong> space, with no recursion depth to worry about.",
                ],
                "dry": [
                    [
                        "vals = [1, 3, 1, 5, 8, 1]. Gap 2: dp[0][2] = 3, dp[1][3] = 15, dp[2][4] = 40, dp[3][5] = 40.",
                        "Gap 3: dp[0][3] = 30, dp[1][4] = max(64, 135) = 135, dp[2][5] = 48.",
                        "Gap 4: dp[0][4] = max(159, 51, 70) = 159, dp[1][5] = 159.",
                        "Gap 5: dp[0][5] = max(162, 52, 75, 167).",
                        "The result is <strong>167</strong>.",
                    ],
                    [
                        "vals = [1, 1, 5, 1]. Gap 2: dp[0][2] = 1·1·5 = 5, dp[1][3] = 1·5·1 = 5.",
                        "Gap 3: dp[0][3] = max(k=1: 0 + 1 + 5 = 6, k=2: 5 + 5 + 0 = 10).",
                        "The result is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why gap and not \"number of balloons\"?",
                     "They are the same thing shifted by one: an interval with gap g has g − 1 balloons strictly inside. Gap matches the indices used in the code."],
                    ["Could I fill by rows, <code>l</code> from right to left?",
                     "Yes: with <code>l</code> descending and <code>r</code> ascending, <code>dp[l][k]</code> is earlier in the same row and <code>dp[k][r]</code> is in a finished lower row. Either order works."],
                    ["Why is <code>dp[0][n - 1]</code> the answer?",
                     "Indices 0 and n − 1 are the padding walls, so that interval contains every real balloon."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ cut a stick
    "minimum-cost-to-cut-a-stick": {
        "examples": [
            {"call": "min_cost(7, [1, 3, 4, 5])", "expect": "16"},
            {"call": "min_cost(6, [4, 1])", "expect": "10"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "A cut costs the length of the piece being cut, so the order matters. Sort the cuts and add both ends: <code>pos = [0] + sorted(cuts) + [n]</code>.",
                    "A piece is then described by two indices into <code>pos</code>. Making the <em>first</em> cut <code>k</code> inside piece <code>(i, j)</code> costs its length <code>pos[j] - pos[i]</code> and leaves two independent pieces, <code>(i, k)</code> and <code>(k, j)</code>.",
                    "Try every first cut and keep the cheapest: an interval recursion like Matrix Chain.",
                ],
                "steps": [
                    "Build <code>pos</code> from the sorted cuts with 0 and <code>n</code> at the ends.",
                    "Define <code>cost(i, j)</code> = the cheapest way to make every cut strictly between <code>pos[i]</code> and <code>pos[j]</code>.",
                    "If <code>j - i &lt; 2</code> there is no cut inside: return 0.",
                    "Otherwise return <code>pos[j] - pos[i] + min(cost(i, k) + cost(k, j))</code> over <code>k</code> in <code>range(i + 1, j)</code>.",
                    "The answer is <code>cost(0, len(pos) - 1)</code>.",
                ],
                "why": [
                    "Whatever cut is made first in a piece, it costs that piece's full length and splits it into two pieces handled independently, so trying every first cut covers every order.",
                    "The length term does not depend on k, so it sits outside the <code>min</code>.",
                    "Without a cache the same pieces are solved over and over: <strong>exponential</strong> time. The recursion is at most m deep: <strong>O(m)</strong> space, where m is the number of cuts.",
                ],
                "dry": [
                    [
                        "pos = [0, 1, 3, 4, 5, 7]. cost(0, 5) = 7 + min over k = 1..4 of {12, 9, 10, 10}.",
                        "k = 2 (cut at 3 first) wins: cost(0, 2) + cost(2, 5) = 3 + 6.",
                        "cost(0, 2) = 3: piece 0..3, cut at 1. cost(2, 5) = 4 + 2: piece 3..7 cut at 5, then piece 3..5 cut at 4.",
                        "Order 3, 1, 5, 4 costs 7 + 3 + 4 + 2. 81 calls in all. The result is <strong>16</strong>.",
                    ],
                    [
                        "The cuts arrive unsorted; pos = [0, 1, 4, 6].",
                        "cost(0, 3) = 6 + min(k=1: 0 + cost(1, 3), k=2: cost(0, 2) + 0).",
                        "cost(1, 3) = 5 (piece 1..6, cut at 4); cost(0, 2) = 4 (piece 0..4, cut at 1). So min(5, 4) = 4.",
                        "Cut at 4 first, then at 1: 6 + 4. The result is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the cuts be sorted?",
                     "Neighbouring entries of <code>pos</code> must be neighbouring cut points on the stick, or <code>pos[j] - pos[i]</code> is not a piece length. With the unsorted [4, 1] the recursion returns 7 instead of 10."],
                    ["Why add 0 and n to <code>pos</code>?",
                     "They are the ends of the stick, so <code>cost(0, m - 1)</code> means \"the whole stick\" and every piece has two real endpoints."],
                    ["Isn't this the same as Matrix Chain?",
                     "Structurally yes: split an interval at k, pay a cost that depends on the interval, recurse on both halves. Here the cost is the piece length instead of a product of shapes."],
                ],
            },
            "Top-down memo": {
                "idea": [
                    "What changed from plain recursion: <code>@cache</code> on <code>cost</code>.",
                    "A piece <code>(i, j)</code> costs the same to finish no matter which earlier cuts produced it, so its answer can be stored once and reused.",
                ],
                "steps": [
                    "Build <code>pos = [0] + sorted(cuts) + [n]</code>.",
                    "Decorate <code>cost(i, j)</code> with <code>@cache</code>.",
                    "Base case: <code>j - i &lt; 2</code> returns 0.",
                    "Recurrence: <code>pos[j] - pos[i]</code> plus the <code>min</code> over <code>k</code> of <code>cost(i, k) + cost(k, j)</code>.",
                    "Return <code>cost(0, len(pos) - 1)</code>.",
                ],
                "why": [
                    "Cached answers equal the recursive ones, so the result is the same.",
                    "There are about m²/2 pieces, each trying up to m first cuts once: <strong>O(m³)</strong> time (plus O(m log m) for the sort).",
                    "The cache holds <strong>O(m²)</strong> entries.",
                ],
                "dry": [
                    [
                        "cost(0, 5), k = 1 computes cost(1, 5), which caches cost(1, 3), cost(1, 4), cost(2, 5), cost(3, 5), …",
                        "k = 2 needs cost(0, 2) (new, 3) and cost(2, 5), a cache hit (6).",
                        "k = 3 and k = 4 reuse cost(3, 5), cost(4, 5) and the others the same way. 15 distinct pieces instead of 81 calls.",
                        "cost(0, 5) = 7 + 9 = <strong>16</strong>.",
                    ],
                    [
                        "pos = [0, 1, 4, 6]. cost(0, 3), k = 1: computes cost(0, 1) = 0 and cost(1, 3) = 5.",
                        "k = 2: computes cost(0, 2) = 4 and cost(2, 3) = 0.",
                        "6 states. 6 + min(5, 4) = <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why are the states indices into <code>pos</code> rather than stick coordinates?",
                     "The stick length n can be huge (up to 10<sup>6</sup>), but only the m + 2 cut positions matter. Indices keep the state space at O(m²)."],
                    ["Does the cost term belong inside the <code>min</code>?",
                     "It could be, but it is the same for every k, so pulling it out is equivalent and cheaper."],
                    ["What does the sort cost?",
                     "O(m log m), which is dwarfed by the O(m³) DP."],
                ],
            },
            "Bottom-up by gap": {
                "idea": [
                    "What changed from the memo: loops fill <code>dp[i][j]</code> directly. Both pieces of any split have a smaller index gap <code>j - i</code>, so fill by gap from 2 upwards.",
                    "Gaps 0 and 1 contain no cut and stay 0. Each cell reads a whole row and column, so, like Matrix Chain, the table cannot be shrunk.",
                ],
                "steps": [
                    "Build <code>pos</code>, let <code>m = len(pos)</code>, and create an m × m table of zeros.",
                    "Loop <code>gap</code> from 2 to <code>m - 1</code>, and <code>i</code> from 0 to <code>m - gap - 1</code>; set <code>j = i + gap</code>.",
                    "Set <code>dp[i][j] = pos[j] - pos[i] + min(dp[i][k] + dp[k][j])</code> over <code>k</code> in <code>range(i + 1, j)</code>.",
                    "Every cell read has a smaller gap, so it is final.",
                    "Return <code>dp[0][m - 1]</code>.",
                ],
                "why": [
                    "The order respects every dependency and each cell applies the same first-cut rule, so <code>dp[0][m-1]</code> is the minimum.",
                    "O(m²) cells, each with up to m splits: <strong>O(m³)</strong> time.",
                    "The table is <strong>O(m²)</strong> space, with no recursion.",
                ],
                "dry": [
                    [
                        "pos = [0, 1, 3, 4, 5, 7]. Gap 2 (one cut inside): dp = 3, 3, 2, 3, just the piece lengths.",
                        "Gap 3: dp[0][3] = 4 + 3 = 7, dp[1][4] = 4 + 2 = 6, dp[2][5] = 4 + 2 = 6.",
                        "Gap 4: dp[0][4] = 5 + min(6, 5, 7) = 10, dp[1][5] = 6 + 6 = 12.",
                        "Gap 5: dp[0][5] = 7 + min(12, 9, 10, 10).",
                        "The result is <strong>16</strong>.",
                    ],
                    [
                        "pos = [0, 1, 4, 6]. Gap 2: dp[0][2] = 4, dp[1][3] = 5.",
                        "Gap 3: dp[0][3] = 6 + min(k=1: 0 + 5, k=2: 4 + 0) = 6 + 4.",
                        "The result is <strong>10</strong>.",
                    ],
                ],
                "faq": [
                    ["Why do gap-2 cells equal the piece length?",
                     "There is exactly one cut inside, so the only choice is to cut there, paying the piece length, and both halves are empty."],
                    ["Why use m, the number of positions, in the bounds?",
                     "The cost grows with the number of cuts, not with the stick length. That is what makes this fast even when n is a million."],
                    ["Could the cuts' order in the input change the answer?",
                     "No, because they are sorted first. Only which positions are cut matters, not the order you were given them in."],
                ],
            },
        },
    },
}
