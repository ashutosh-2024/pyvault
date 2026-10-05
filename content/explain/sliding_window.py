"""Write-ups for the Sliding Window topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ contains duplicate II
    "contains-duplicate-ii": {
        "example": {"call": "contains_nearby_duplicate([1, 2, 3, 1, 4, 2, 4], 2)", "expect": "True"},
        "approaches": {
            "Check the next k elements from each index": {
                "idea": [
                    "Two equal values count only if their indices are at most k apart.",
                    "So for every index, it is enough to look at the next k elements and nothing further.",
                ],
                "steps": [
                    "For each <code>i</code>, loop <code>j</code> from <code>i + 1</code> up to <code>i + k</code>, stopping at the array end.",
                    "If <code>nums[i] == nums[j]</code>, return <code>True</code> immediately.",
                    "If no pair is found, return <code>False</code>.",
                ],
                "why": [
                    "Every pair at distance 1..k is checked exactly once, so no valid pair is missed.",
                    "Neighbouring windows overlap almost completely but are re-read from scratch, so it costs O(n·k) time and O(1) space.",
                ],
                "dry": [
                    "i=0 (1): compares with 2 and 3, no match.",
                    "i=1 (2): compares with 3 and 1. i=2 (3): compares with 1 and 4.",
                    "i=3 (1): compares with 4 and 2. The other 1 at index 0 is 3 away, too far.",
                    "i=4 (4): compares with 2 (index 5), then 4 (index 6), a match at distance 2.",
                    "It returns <strong>True</strong>.",
                ],
            },
            "Last index seen for each value": {
                "idea": [
                    "When a value repeats, the only earlier copy worth checking is the <em>most recent</em> one, because it is the closest.",
                    "So a dictionary from value to last index seen answers each element in O(1).",
                ],
                "steps": [
                    "Scan with index <code>i</code> and value <code>x</code>.",
                    "If <code>x</code> was seen before and <code>i - last[x] &lt;= k</code>, return <code>True</code>.",
                    "Otherwise set <code>last[x] = i</code>, since the newest index is the best one for future checks.",
                    "Return <code>False</code> at the end.",
                ],
                "why": [
                    "Any older copy is even further away than the most recent one, so checking only <code>last[x]</code> loses nothing.",
                    "One dictionary lookup per element gives O(n) time, but the map keeps every distinct value: O(n) space.",
                ],
                "dry": [
                    "i=0..2: record 1→0, 2→1, 3→2.",
                    "i=3 (1): last[1] = 0 and 3 - 0 = 3 &gt; 2, too far. Update last[1] = 3.",
                    "i=4 (4): new, so last[4] = 4.",
                    "i=5 (2): last[2] = 1 and 5 - 1 = 4 &gt; 2. Update last[2] = 5.",
                    "i=6 (4): last[4] = 4 and 6 - 4 = 2 ≤ 2, so it returns <strong>True</strong>.",
                ],
            },
            "Set of the last k values": {
                "idea": [
                    "Only the previous k elements can pair with the current one, so keep exactly those in a set.",
                    "This is the fixed-size sliding window: add the newest element, and evict the one that just fell out of range.",
                    "Memory stays bounded by k instead of by the number of distinct values.",
                ],
                "steps": [
                    "For each <code>i</code>: if <code>nums[i]</code> is already in <code>window</code>, return <code>True</code>.",
                    "Add <code>nums[i]</code>.",
                    "If the set now holds more than k values, remove <code>nums[i - k]</code>, the oldest one.",
                    "Return <code>False</code> if the scan ends.",
                ],
                "why": [
                    "Before index i is checked, the set holds exactly <code>nums[i-k..i-1]</code>, the only indices within distance k.",
                    "Values in the window are distinct (a duplicate would have returned already), so the size check evicts exactly one element.",
                    "Set operations are O(1): O(n) time and O(min(n, k)) space.",
                ],
                "dry": [
                    "i=0: add 1, giving {1}. i=1: add 2, giving {1, 2}.",
                    "i=2: add 3, giving {1, 2, 3}; the size is 3 &gt; 2, so evict nums[0] = 1, leaving {2, 3}.",
                    "i=3 (1): not in the set. Add it, then evict nums[1] = 2, leaving {1, 3}.",
                    "i=4 (4): add it, then evict nums[2] = 3, leaving {1, 4}.",
                    "i=5 (2): add it, then evict nums[3] = 1, leaving {2, 4}.",
                    "i=6 (4): 4 is in the window, so it returns <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ best time to buy and sell
    "best-time-stock": {
        "example": {"call": "max_profit([7, 1, 5, 3, 6, 4])", "expect": "5"},
        "approaches": {
            "Every buy/sell pair": {
                "idea": [
                    "Profit is <code>prices[sell] - prices[buy]</code> with the sell day after the buy day.",
                    "Trying every such pair is the most direct way to find the best one.",
                ],
                "steps": [
                    "For every buy day <code>i</code> and every later day <code>j</code>, compute <code>prices[j] - prices[i]</code>.",
                    "Keep the maximum, starting from 0 so that never trading counts as profit 0.",
                ],
                "why": [
                    "All legal transactions are examined, so the maximum is correct.",
                    "There are n(n-1)/2 pairs: O(n²) time, O(1) space.",
                ],
                "dry": [
                    "Buying at 7 (day 0) loses money on every later day.",
                    "Buying at 1 (day 1): selling at 5, 3, 6, 4 gives 4, 2, <strong>5</strong>, 3.",
                    "Buying at 5 gives at most 1, buying at 3 gives at most 3, and buying at 6 gives -2.",
                    "The best over all pairs is <strong>5</strong>: buy at 1, sell at 6.",
                ],
            },
            "Two pointers: move the buy day to any lower price": {
                "idea": [
                    "For a fixed sell day, the best buy day is simply the cheapest day before it.",
                    "So scan once, remembering the lowest price so far, and treat each day as a possible sell day.",
                    "A new lower price replaces the old buy day, because buying higher earlier is never better.",
                ],
                "steps": [
                    "Start with <code>lowest = prices[0]</code> and <code>best = 0</code>.",
                    "For each later price <code>p</code>: first update <code>best = max(best, p - lowest)</code>, selling today.",
                    "Then update <code>lowest = min(lowest, p)</code> for future sell days.",
                ],
                "why": [
                    "For every sell day it pairs the best possible buy day, so the best pair overall is found.",
                    "Selling is checked before lowest is updated, so a buy and sell can never happen on the same day.",
                    "One pass and two variables: O(n) time, O(1) space.",
                ],
                "dry": [
                    "Start with lowest = 7, best = 0.",
                    "p=1: 1 - 7 = -6, so best stays 0; lowest becomes 1.",
                    "p=5: 5 - 1 = 4, so best = 4.",
                    "p=3: 3 - 1 = 2, and best stays 4.",
                    "p=6: 6 - 1 = 5, so best = <strong>5</strong>.",
                    "p=4: 3 &lt; 5. The answer is <strong>5</strong>.",
                ],
            },
            "Kadane on daily changes": {
                "idea": [
                    "Profit from day a to day b equals the sum of the daily changes between them, because the in-between days cancel out.",
                    "So the question becomes: what is the maximum-sum run of consecutive daily changes?",
                    "That is the maximum subarray problem, which Kadane's algorithm solves in one pass.",
                ],
                "steps": [
                    "Walk over consecutive pairs <code>(a, b)</code>; the change is <code>b - a</code>.",
                    "<code>cur = max(0, cur + b - a)</code> extends the current run, or restarts it when it would go negative.",
                    "<code>best = max(best, cur)</code>.",
                ],
                "why": [
                    "A run with a negative total can only hurt any run that continues it, so dropping it and restarting is optimal.",
                    "<code>cur</code> is the best profit for selling today: O(n) time, O(1) space.",
                ],
                "dry": [
                    "The daily changes are -6, +4, -2, +3, -2.",
                    "-6: cur = max(0, -6) = 0.",
                    "+4: cur = 4, best = 4. This is buying on day 1.",
                    "-2: cur = 2. +3: cur = 5, best = <strong>5</strong>, which is 4 - 2 + 3 = 6 - 1.",
                    "-2: cur = 3. The answer is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest substring without repeats
    "longest-substring-no-repeat": {
        "example": {"call": 'length_of_longest_substring("abcbdab")', "expect": "4"},
        "approaches": {
            "Check every substring": {
                "idea": [
                    "A substring has no repeats exactly when its set of characters is as large as the substring itself.",
                    "Test every substring that way and keep the longest that passes.",
                ],
                "steps": [
                    "For every pair <code>i ≤ j</code>, build <code>set(s[i:j+1])</code>.",
                    "If its size equals <code>j - i + 1</code>, update <code>best</code>.",
                ],
                "why": [
                    "Every substring is examined, so the longest valid one is found.",
                    "There are O(n²) substrings and each set costs O(n): O(n³) time. The set holds at most Σ characters (the alphabet size).",
                ],
                "dry": [
                    "From i=0: \"a\", \"ab\" and \"abc\" pass; \"abcb\" has two b's and fails.",
                    "From i=1: \"bc\" passes; \"bcb\" fails.",
                    "From i=2: \"c\", \"cb\", \"cbd\" and <strong>\"cbda\"</strong> pass (length 4); \"cbdab\" repeats b.",
                    "Later starts give at most \"bda\" and \"dab\" (length 3).",
                    "The result is <strong>4</strong>.",
                ],
            },
            "Extend from each start until a repeat": {
                "idea": [
                    "From a fixed start, extend one character at a time and stop at the first repeat: nothing longer from this start can be valid.",
                    "A set of seen characters makes each extension O(1).",
                ],
                "steps": [
                    "For each start <code>i</code>, create an empty <code>seen</code>.",
                    "Walk <code>s[i:]</code>; break on a character already in <code>seen</code>, otherwise add it.",
                    "<code>len(seen)</code> is the longest valid substring from i.",
                ],
                "why": [
                    "Once a repeat appears, every longer substring from the same start contains it too.",
                    "Each start walks at most Σ + 1 characters: O(n·Σ) time and O(Σ) space. Neighbouring starts redo almost the same work.",
                ],
                "dry": [
                    "i=0: a, b, c, then b repeats, so the length is 3.",
                    "i=1: b, c, then b repeats, so 2.",
                    "i=2: c, b, d, a, then b repeats, so <strong>4</strong>.",
                    "i=3: b, d, a gives 3. i=4: d, a, b gives 3. i=5: 2. i=6: 1.",
                    "The best is <strong>4</strong>.",
                ],
            },
            "Window with a set, shrink one step at a time": {
                "idea": [
                    "Keep a window <code>[left, right]</code> that never contains a repeat, and its characters in a set.",
                    "Move <code>right</code> forward. If the new character is already inside, shrink from the left until that older copy has left the window.",
                    "Every window considered is valid, and the longest one is the answer.",
                ],
                "steps": [
                    "For each <code>right</code>: while <code>s[right]</code> is in the set, remove <code>s[left]</code> and advance <code>left</code>.",
                    "Add <code>s[right]</code> to the set.",
                    "Update <code>best</code> with the window length <code>right - left + 1</code>.",
                ],
                "why": [
                    "For each right end the window is the longest repeat-free substring ending there, since we only shrink as much as needed.",
                    "Each character enters and leaves the set once: O(n) time and O(Σ) space.",
                ],
                "dry": [
                    "right 0..2: a, b, c are added; the window is \"abc\", best 3.",
                    "right=3 (b): b is inside, so remove a (left=1), then b (left=2). Add b; the window is \"cb\".",
                    "right=4 (d): the window is \"cbd\". right=5 (a): the window is \"cbda\", best <strong>4</strong>.",
                    "right=6 (b): remove c (left=3), then b (left=4). Add b; the window is \"dab\", length 3.",
                    "The answer is <strong>4</strong>.",
                ],
            },
            "Window with last-seen indices, jump the left edge": {
                "idea": [
                    "Instead of removing characters one by one, remember where each character was last seen.",
                    "On a repeat, the window must start just after that previous copy, so jump <code>left</code> straight there.",
                    "But never move <code>left</code> backwards: the previous copy may already be outside the window.",
                ],
                "steps": [
                    "Keep <code>last</code> (character → last index) and <code>left</code>.",
                    "If <code>s[right]</code> was seen, set <code>left = max(left, last[ch] + 1)</code>.",
                    "Record <code>last[ch] = right</code> and update <code>best</code> with <code>right - left + 1</code>.",
                ],
                "why": [
                    "The window <code>[left, right]</code> is always repeat-free, and it is the longest one ending at right.",
                    "The <code>max</code> keeps the left edge from jumping back over a repeat already excluded.",
                    "One O(1) step per character: O(n) time and O(Σ) space.",
                ],
                "dry": [
                    "right 0..2: no repeats; left = 0, best 3.",
                    "right=3 (b): last[b] = 1, so left = 2. last[b] = 3; the length is 2.",
                    "right=4 (d): the window is 2..4, length 3.",
                    "right=5 (a): last[a] = 0, but max(2, 0 + 1) keeps left = 2, because that a is already outside. The length is 4, best <strong>4</strong>.",
                    "right=6 (b): last[b] = 3, so left = 4; the length is 3.",
                    "The answer is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest repeating replacement
    "longest-repeating-replacement": {
        "example": {"call": 'character_replacement("AABABBA", 1)', "expect": "4"},
        "approaches": {
            "Every substring": {
                "idea": [
                    "A window can be made one letter if we keep its most common letter and repaint the rest.",
                    "That needs <code>length - (count of the most common letter)</code> changes, which must be ≤ k.",
                    "Check that condition for every substring, keeping letter counts as each one grows.",
                ],
                "steps": [
                    "For each start <code>i</code>, reset 26 counters.",
                    "Extend <code>j</code>, incrementing the count for <code>s[j]</code>.",
                    "If <code>(j - i + 1) - max(counts) &lt;= k</code>, update <code>best</code>.",
                ],
                "why": [
                    "Repainting everything except the majority letter is the cheapest way to make a window uniform.",
                    "There are O(n²) windows with O(26) per check: O(n²) time, O(26) space.",
                ],
                "dry": [
                    "From i=0: \"AAB\" needs 1 change and \"AABA\" needs 4 - 3 = 1, so best 4. \"AABAB\" needs 2, too many.",
                    "From i=1: \"ABA\" needs 1 (length 3); \"ABAB\" needs 2.",
                    "From i=2: \"BAB\" needs 1, and <strong>\"BABB\"</strong> needs 4 - 3 = 1, length 4; \"BABBA\" needs 2.",
                    "From i=3: \"ABB\" needs 1; \"ABBA\" needs 2.",
                    "The best is <strong>4</strong>.",
                ],
            },
            "Sliding window, recompute the max count": {
                "idea": [
                    "If a window is not fixable, every larger window with the same left edge is not fixable either.",
                    "So grow the right edge, and when the window breaks the rule, shrink from the left until it is fixable again.",
                    "Each check finds the most common letter by scanning the 26 counts.",
                ],
                "steps": [
                    "Add <code>s[right]</code> to the counts.",
                    "While <code>length - max(counts) &gt; k</code>, remove <code>s[left]</code> and advance <code>left</code>.",
                    "Update <code>best</code> with the window length.",
                ],
                "why": [
                    "For each right end the window is the longest fixable one ending there.",
                    "Each index enters and leaves once, but every check costs O(26): O(26·n) time, O(26) space.",
                ],
                "dry": [
                    "right 0..3 (\"AABA\"): A has 3 and the length is 4, so 4 - 3 = 1 ≤ 1 and best = 4.",
                    "right=4 (\"AABAB\"): 5 - 3 = 2 &gt; 1, so remove A (left=1). \"ABAB\" gives 4 - 2 = 2, so remove A again (left=2). \"BAB\" is fine.",
                    "right=5 (\"BABB\"): B has 3, 4 - 3 = 1, still best 4.",
                    "right=6 (\"BABBA\"): 5 - 3 = 2, remove B (left=3). \"ABBA\" gives 2, remove A (left=4). \"BBA\" is fine.",
                    "The best is <strong>4</strong>.",
                ],
            },
            "Sliding window with a never-decreasing max count": {
                "idea": [
                    "The answer only improves when some window has a letter count higher than ever before.",
                    "So keep <code>max_count</code> as the highest count ever seen, and never lower it when the window shrinks.",
                    "When the window looks unfixable, slide it by one instead of shrinking it, so it never gets smaller.",
                    "A stale <code>max_count</code> can only make the window <em>slide</em>, never grow, so the size recorded is always one that was truly achievable.",
                ],
                "steps": [
                    "Add <code>s[right]</code> and set <code>max_count = max(max_count, its count)</code>.",
                    "If <code>length - max_count &gt; k</code>, remove <code>s[left]</code> and advance <code>left</code> once, using <code>if</code> rather than <code>while</code>.",
                    "At the end, the window size <code>len(s) - left</code> is the answer.",
                ],
                "why": [
                    "The window size grows only when <code>max_count</code> grows, which needs a window with a genuinely higher letter count.",
                    "Each step is O(1): O(n) time and O(26) space.",
                ],
                "dry": [
                    "right 0..3 (\"AABA\"): max_count = 3, size 4, 4 - 3 = 1, fine.",
                    "right=4 (B): size 5 and 5 - 3 = 2 &gt; 1, so slide: drop s[0] = A, left = 1, size back to 4.",
                    "right=5 (B): B now has 2 in the window, max_count stays 3. 5 - 3 = 2, slide: drop s[1] = A, left = 2.",
                    "right=6 (A): 5 - 3 = 2, slide: drop s[2] = B, left = 3.",
                    "The window never grew past 4, and <code>len(s) - left = 7 - 3</code> = <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ permutation in string
    "permutation-in-string": {
        "example": {"call": 'check_inclusion("abc", "bbdcabx")', "expect": "True"},
        "approaches": {
            "Generate permutations": {
                "idea": [
                    "State the problem literally: is any rearrangement of s1 a substring of s2?",
                    "Generate every distinct permutation of s1 and test each with Python's substring search.",
                ],
                "steps": [
                    "<code>set(itertools.permutations(s1))</code> gives the distinct orderings.",
                    "Join each into a string and check <code>in s2</code>.",
                    "<code>any</code> stops at the first hit.",
                ],
                "why": [
                    "It is correct by definition.",
                    "There are up to m! orderings, each searched in O(n): factorial time and space, hopeless beyond about 8 characters.",
                ],
                "dry": [
                    "The six orderings of \"abc\" are abc, acb, bac, bca, cab, cba.",
                    "s2 = \"bbdcabx\" contains none of abc, acb, bac or bca.",
                    "It contains \"cab\" at index 3, so <code>any</code> returns <strong>True</strong>.",
                ],
            },
            "Sort every window": {
                "idea": [
                    "A window is a permutation of s1 exactly when both are anagrams, which means their sorted forms are equal.",
                    "Only windows of length m = len(s1) can match.",
                ],
                "steps": [
                    "Sort s1 once into <code>target</code>.",
                    "For every start <code>i</code>, sort <code>s2[i:i+m]</code> and compare it with <code>target</code>.",
                ],
                "why": [
                    "Sorting puts any arrangement of the same letters into one canonical form.",
                    "There are n windows, each sorted in O(m log m): O(n·m log m) time, O(m) space.",
                ],
                "dry": [
                    "target = \"abc\".",
                    "i=0: \"bbd\" sorts to \"bbd\", no. i=1: \"bdc\" sorts to \"bcd\", no.",
                    "i=2: \"dca\" sorts to \"acd\", no.",
                    "i=3: \"cab\" sorts to \"abc\", a match, so it returns <strong>True</strong>.",
                ],
            },
            "Fixed window, compare 26 counts": {
                "idea": [
                    "Instead of sorting, compare letter counts: two strings are anagrams exactly when their 26 counts match.",
                    "Neighbouring windows differ by one letter in and one letter out, so update the counts instead of rebuilding them.",
                ],
                "steps": [
                    "Count s1 into <code>need</code> and the first m letters of s2 into <code>have</code>.",
                    "If they are equal, return <code>True</code>.",
                    "Slide: add <code>s2[i]</code>, subtract <code>s2[i - m]</code>, and compare again.",
                ],
                "why": [
                    "<code>have</code> always holds the counts of the current window.",
                    "Each slide is O(1), but the list comparison is O(26): O(26·n) time, O(26) space.",
                ],
                "dry": [
                    "need = {a:1, b:1, c:1}. The first window \"bbd\" has {b:2, d:1}, not equal.",
                    "Add 'c', drop 'b': \"bdc\" has {b:1, c:1, d:1}, not equal.",
                    "Add 'a', drop 'b': \"dca\" has {a:1, c:1, d:1}, not equal.",
                    "Add 'b', drop 'd': \"cab\" has {a:1, b:1, c:1}, equal, so it returns <strong>True</strong>.",
                ],
            },
            "Fixed window with a matches counter": {
                "idea": [
                    "Comparing all 26 counts on every slide is wasted work, because only two letters change.",
                    "Track <code>matches</code>, the number of letters whose window count equals their s1 count. The window is a permutation when it is 26.",
                    "Changing one letter's count can only change that letter's match status, so <code>matches</code> updates in O(1).",
                ],
                "steps": [
                    "Build the initial counts and <code>matches = sum(need[i] == have[i])</code>.",
                    "<code>change(idx, delta)</code>: drop idx's old match status, adjust the count, add its new status.",
                    "For each slide: if <code>matches == 26</code>, return <code>True</code>; otherwise add the incoming letter and remove the outgoing one.",
                    "After the loop, check the last window.",
                ],
                "why": [
                    "<code>matches</code> is kept exactly equal to the number of agreeing letters after every change.",
                    "Every step is O(1): O(n) time and O(26) space. Minimum Window Substring reuses the same trick.",
                ],
                "dry": [
                    "Initial window \"bbd\": a (need 1, have 0), b (1 vs 2), c (1 vs 0) and d (0 vs 1) disagree, so matches = 22.",
                    "Slide in 'c': c becomes 1 = 1, so 23. Slide out 'b': b becomes 1 = 1, so 24. The window is \"bdc\".",
                    "Slide in 'a': 25. Slide out 'b': b is now 0, no longer matching, so 24. The window is \"dca\".",
                    "Slide in 'b': 25. Slide out 'd': d becomes 0 = 0, so 26. The window is \"cab\".",
                    "At the next check matches is 26, so it returns <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum size subarray sum
    "minimum-size-subarray-sum": {
        "example": {"call": "min_subarray_len(7, [2, 3, 1, 2, 4, 3])", "expect": "2"},
        "approaches": {
            "Every start, extend until the target": {
                "idea": [
                    "From a fixed start, the shortest valid subarray ends at the first point where the running sum reaches the target.",
                    "Try every start and keep the shortest of those lengths.",
                ],
                "steps": [
                    "For each start <code>i</code>, add <code>nums[j]</code> for <code>j = i, i+1, ...</code>.",
                    "At the first <code>total &gt;= target</code>, record <code>j - i + 1</code> and stop extending.",
                    "Return 0 if no start ever reaches the target.",
                ],
                "why": [
                    "All numbers are positive, so extending further from the same start only makes the subarray longer.",
                    "It costs O(n²) time in the worst case and O(1) space.",
                ],
                "dry": [
                    "i=0: 2, 5, 6, 8, which reaches 7 at j=3, length 4.",
                    "i=1: 3, 4, 6, 10, at j=4, length 4.",
                    "i=2: 1, 3, 7, at j=4, length 3. i=3: 2, 6, 9, length 3.",
                    "i=4: 4, 7, length <strong>2</strong>. i=5: 3 never reaches 7.",
                    "The answer is <strong>2</strong>, from the subarray [4, 3].",
                ],
            },
            "Prefix sums and binary search": {
                "idea": [
                    "With prefix sums <code>P</code>, the sum of <code>nums[i:j]</code> is <code>P[j] - P[i]</code>.",
                    "All numbers are positive, so <code>P</code> is strictly increasing and can be binary-searched.",
                    "For each start i, the first j with <code>P[j] ≥ P[i] + target</code> gives the shortest valid end.",
                ],
                "steps": [
                    "Build <code>P = [0, nums[0], nums[0]+nums[1], ...]</code>.",
                    "For each i, find <code>j = bisect_left(P, P[i] + target)</code>.",
                    "If <code>j &lt;= n</code>, the length is <code>j - i</code>; keep the minimum.",
                ],
                "why": [
                    "<code>bisect_left</code> returns the first index whose prefix reaches the needed value, which is the earliest valid end.",
                    "It is n binary searches: O(n log n) time and O(n) space. This version still works when many targets are asked about.",
                ],
                "dry": [
                    "P = [0, 2, 5, 6, 8, 12, 15].",
                    "i=0 needs ≥ 7, found at j=4 (8): length 4. i=1 needs ≥ 9, j=5: length 4.",
                    "i=2 needs ≥ 12, j=5: length 3. i=3 needs ≥ 13, j=6: length 3.",
                    "i=4 needs ≥ 15, j=6: length <strong>2</strong>. i=5 needs ≥ 19, which is beyond the array.",
                    "The answer is <strong>2</strong>.",
                ],
            },
            "Variable window": {
                "idea": [
                    "Grow a window to the right until its sum reaches the target, then shrink it from the left as long as it still qualifies.",
                    "Each time it qualifies, it is a candidate answer.",
                    "Positivity guarantees that shrinking only lowers the sum and growing only raises it, so neither pointer ever needs to move back.",
                ],
                "steps": [
                    "Add <code>nums[right]</code> to <code>total</code>.",
                    "While <code>total &gt;= target</code>: record the length, subtract <code>nums[left]</code>, advance <code>left</code>.",
                    "Return the best length, or 0.",
                ],
                "why": [
                    "For each right end, the loop finds the shortest valid window ending there.",
                    "Each index enters once and leaves once: O(n) time and O(1) space. With negative numbers this argument fails.",
                ],
                "dry": [
                    "right 0..3: the total grows 2, 5, 6, 8. At 8 ≥ 7, record length 4, drop 2, so total 6 and left = 1.",
                    "right=4: total 10, record length 4. Drop 3, total 7, record length 3. Drop 1, total 6, left = 3.",
                    "right=5: total 9, record length 3. Drop 2, total 7, record length <strong>2</strong>. Drop 4, total 3, left = 5.",
                    "The scan ends. The answer is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find k closest elements
    "find-k-closest-elements": {
        "example": {"call": "find_closest_elements([1, 2, 3, 4, 5, 6, 7, 8], 3, 5)", "expect": "[4, 5, 6]"},
        "approaches": {
            "Sort by distance": {
                "idea": [
                    "The problem defines a ranking: smaller <code>|a - x|</code> first, and the smaller value on a tie.",
                    "Sort by exactly that key, take the first k, and sort them back into ascending order.",
                ],
                "steps": [
                    "<code>sorted(arr, key=lambda a: (abs(a - x), a))</code>.",
                    "Keep the first k.",
                    "Sort those k for the required output order.",
                ],
                "why": [
                    "The key encodes the closeness rule exactly, ties included.",
                    "It ignores that the input is already sorted: O(n log n) time, O(n) space.",
                ],
                "dry": [
                    "Distances to 5: 1→4, 2→3, 3→2, 4→1, 5→0, 6→1, 7→2, 8→3.",
                    "Sorted by (distance, value): 5, 4, 6, 3, 7, 2, 8, 1.",
                    "The first three are 5, 4, 6, which sort to <strong>[4, 5, 6]</strong>.",
                ],
            },
            "Shrink a window from both ends": {
                "idea": [
                    "The answer is a contiguous block of the sorted array.",
                    "Start with the whole array and repeatedly drop whichever end is farther from x.",
                    "On a tie, drop the right end, because the smaller value wins ties.",
                ],
                "steps": [
                    "<code>lo, hi = 0, n - 1</code>.",
                    "While the window holds more than k: if <code>x - arr[lo] &lt;= arr[hi] - x</code>, drop <code>hi</code>, otherwise drop <code>lo</code>.",
                    "Return <code>arr[lo:hi+1]</code>.",
                ],
                "why": [
                    "The end that is farther away (or equal but larger) is ranked below everything inside the window, so it can never be in the answer.",
                    "It removes n - k elements one at a time: O(n - k) time, O(1) space.",
                ],
                "dry": [
                    "[1..8]: 1 is 4 away and 8 is 3 away, so drop 1.",
                    "[2..8]: 3 versus 3 is a tie, so drop 8.",
                    "[2..7]: 3 versus 2, so drop 2. [3..7]: 2 versus 2 is a tie, so drop 7.",
                    "[3..6]: 2 versus 1, so drop 3. [4..6] has three elements.",
                    "The result is <strong>[4, 5, 6]</strong>.",
                ],
            },
            "Binary search the window's left edge": {
                "idea": [
                    "The answer is <code>arr[s:s+k]</code> for some start s in 0..n-k, so search for s directly.",
                    "For a candidate start mid, compare <code>arr[mid]</code> (the leftmost element inside) with <code>arr[mid+k]</code> (the first element just outside on the right).",
                    "If x is farther from <code>arr[mid]</code> than from <code>arr[mid+k]</code>, shifting right is better; otherwise the start is mid or earlier. That test is monotonic in mid.",
                ],
                "steps": [
                    "<code>lo, hi = 0, n - k</code>.",
                    "<code>mid = (lo + hi) // 2</code>; if <code>x - arr[mid] &gt; arr[mid+k] - x</code>, set <code>lo = mid + 1</code>, otherwise <code>hi = mid</code>.",
                    "Return <code>arr[lo:lo+k]</code>.",
                ],
                "why": [
                    "The comparison uses signed differences, not absolute values, so it stays correct with duplicates and when x is outside the array.",
                    "The binary search costs O(log(n - k)) and slicing O(k): O(log(n - k) + k) time and O(1) extra space.",
                ],
                "dry": [
                    "lo = 0, hi = 5.",
                    "mid=2: x - arr[2] = 2 and arr[5] - x = 1. Since 2 &gt; 1, move right: lo = 3.",
                    "mid=4: x - arr[4] = 0 and arr[7] - x = 3. Not greater, so hi = 4.",
                    "mid=3: x - arr[3] = 1 and arr[6] - x = 2. Not greater, so hi = 3.",
                    "lo = hi = 3, and <code>arr[3:6]</code> = <strong>[4, 5, 6]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum window substring
    "minimum-window-substring": {
        "example": {"call": 'min_window("ADOBECODEBANC", "ABC")', "expect": '"BANC"'},
        "approaches": {
            "Check every substring": {
                "idea": [
                    "From a fixed start, the shortest covering window ends at the first point where every required character is present often enough.",
                    "Try every start, stop at that first covering end, and keep the shortest window.",
                ],
                "steps": [
                    "<code>need = Counter(t)</code>.",
                    "For each start i, extend j and count characters in <code>have</code>.",
                    "When every <code>have[c] &gt;= need[c]</code>, compare the window with <code>best</code> and stop extending.",
                ],
                "why": [
                    "Extending further from the same start only makes the window longer, so the first covering end is enough.",
                    "There are O(n²) windows, each with an O(Σ) coverage check: O(n²·Σ) time and O(Σ) space.",
                ],
                "dry": [
                    "Start 0: the first covering window is \"ADOBEC\" (length 6).",
                    "Starts 1 to 4 must reach the A at index 10, giving longer windows.",
                    "Start 5 gives \"CODEBA\" (6), start 6 gives \"ODEBANC\" (7), start 7 gives \"DEBANC\" (6).",
                    "Start 8 gives \"EBANC\" (5), and start 9 gives <strong>\"BANC\"</strong> (4).",
                    "Starts 10 and later never see a B. The answer is <strong>\"BANC\"</strong>.",
                ],
            },
            "Sliding window with a 'formed' counter": {
                "idea": [
                    "Grow the window to the right until it covers t, then shrink from the left while it still covers t, recording each covering window.",
                    "To test coverage in O(1), count how many <em>distinct</em> required characters currently meet their required count; call it <code>formed</code>.",
                    "Adding a character can only complete its own requirement and removing one can only break its own, so <code>formed</code> changes by at most one.",
                ],
                "steps": [
                    "<code>need = Counter(t)</code>, <code>required = len(need)</code>.",
                    "Add <code>s[right]</code>; if its count now equals the need exactly, <code>formed += 1</code>.",
                    "While <code>formed == required</code>: record the window if it is shorter, remove <code>s[left]</code>, and if its count drops below the need, <code>formed -= 1</code>. Advance <code>left</code>.",
                    "Return the best window, or \"\".",
                ],
                "why": [
                    "Each right end is followed by shrinking as far as coverage allows, so the shortest covering window ending there is recorded.",
                    "Each index is added once and removed once: O(n + m) time, O(Σ) space.",
                ],
                "dry": [
                    "Moving right to index 5 (C) completes A, B and C, so formed = 3. Record \"ADOBEC\" (6). Removing A breaks it (left = 1).",
                    "Indices 6..9 (O, D, E, B) add nothing new; the second B does not change formed.",
                    "Index 10 (A): formed = 3 again. Shrink, checking lengths 10, 9, 8, 7 and 6 as D, O, B and E leave (the extra B can go); none beats 6. Removing C breaks it (left = 6).",
                    "Index 12 (C): formed = 3. Shrink from 7 to 6, then 5 (\"EBANC\"), then 4 (<strong>\"BANC\"</strong>). Removing B breaks it.",
                    "The scan ends, and the best window is <strong>\"BANC\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sliding window maximum
    "sliding-window-maximum": {
        "example": {"call": "max_sliding_window([9, 1, 2, 3, 1, 4, 0], 3)", "expect": "[9, 3, 3, 4, 4]"},
        "approaches": {
            "Max of every window": {
                "idea": [
                    "There are n - k + 1 windows; compute the maximum of each one directly.",
                ],
                "steps": [
                    "For each start <code>i</code>, take <code>max(nums[i:i+k])</code>.",
                    "Collect the results in order.",
                ],
                "why": [
                    "It is exactly the definition.",
                    "Each window costs O(k): O(n·k) time and O(1) extra space beyond the output.",
                ],
                "dry": [
                    "[9, 1, 2] gives 9. [1, 2, 3] gives 3. [2, 3, 1] gives 3.",
                    "[3, 1, 4] gives 4. [1, 4, 0] gives 4.",
                    "The result is <strong>[9, 3, 3, 4, 4]</strong>.",
                ],
            },
            "Max-heap with lazy deletion": {
                "idea": [
                    "A max-heap gives the largest value in O(1), but removing the element that leaves the window from the middle of a heap is awkward.",
                    "So do not remove it right away: store <code>(-value, index)</code>, and when the top's index is outside the window, pop it.",
                    "Stale entries deeper in the heap do no harm, because only the top is ever read.",
                ],
                "steps": [
                    "Push <code>(-x, i)</code> for each element.",
                    "Once the first window is full (<code>i ≥ k - 1</code>), pop while the top's index is ≤ <code>i - k</code>.",
                    "The top's value is the window maximum.",
                ],
                "why": [
                    "After the expired tops are popped, the top is the largest value whose index is inside the window.",
                    "Every element is pushed and popped at most once: O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "i=0..2: push 9, 1, 2. The top is (9, index 0), which is in the window [0..2], so output <strong>9</strong>.",
                    "i=3: push 3. The top is still 9 at index 0, but 0 ≤ 3 - 3, so it has expired: pop it. The new top is 3, so output <strong>3</strong>.",
                    "i=4: push 1. The top is 3 at index 3, still inside, so output <strong>3</strong>.",
                    "i=5: push 4, now the top, so output <strong>4</strong>. i=6: push 0; the top is 4 at index 5, so output <strong>4</strong>.",
                    "The result is <strong>[9, 3, 3, 4, 4]</strong>.",
                ],
            },
            "Block prefix and suffix maxima": {
                "idea": [
                    "Cut the array into blocks of size k. Any window of size k covers the tail of one block and the head of the next.",
                    "Precompute, inside each block, the max from the block start to each index (prefix) and from each index to the block end (suffix).",
                    "Then a window starting at i has maximum <code>max(suffix[i], prefix[i + k - 1])</code>.",
                ],
                "steps": [
                    "<code>prefix[i]</code>: restart at each block start (<code>i % k == 0</code>), otherwise <code>max(prefix[i-1], nums[i])</code>.",
                    "<code>suffix[i]</code>: restart at each block end (<code>(i + 1) % k == 0</code>), going right to left.",
                    "For each window start i, combine <code>suffix[i]</code> and <code>prefix[i+k-1]</code>.",
                ],
                "why": [
                    "<code>suffix[i]</code> covers the window's part in its first block, and <code>prefix[i+k-1]</code> covers its part in the next block.",
                    "It takes three linear passes: O(n) time and O(n) space, with no clever data structure.",
                ],
                "dry": [
                    "The blocks are [9, 1, 2], [3, 1, 4] and [0].",
                    "prefix = [9, 9, 9, 3, 3, 4, 0]; suffix = [9, 2, 2, 4, 4, 4, 0].",
                    "Window 0: max(suffix[0] = 9, prefix[2] = 9) = <strong>9</strong>.",
                    "Window 1: max(2, prefix[3] = 3) = <strong>3</strong>. Window 2: max(2, prefix[4] = 3) = <strong>3</strong>.",
                    "Window 3: max(4, prefix[5] = 4) = <strong>4</strong>. Window 4: max(suffix[4] = 4, prefix[6] = 0) = <strong>4</strong>.",
                    "The result is <strong>[9, 3, 3, 4, 4]</strong>.",
                ],
            },
            "Monotonic deque of indices": {
                "idea": [
                    "If a newer element is at least as large as an older one, the older one can never be a window maximum again: the newer one is bigger and leaves later.",
                    "So keep a deque of candidate indices whose values strictly decrease from front to back; the front is always the current maximum.",
                    "Drop the front when it slides out of the window.",
                ],
                "steps": [
                    "For each <code>i</code>: pop from the back while <code>nums[back] &lt;= x</code>, then append <code>i</code>.",
                    "If the front index is ≤ <code>i - k</code>, pop it from the front.",
                    "Once <code>i ≥ k - 1</code>, output <code>nums[dq[0]]</code>.",
                ],
                "why": [
                    "Every index removed from the back is dominated forever, so nothing useful is lost.",
                    "Each index is pushed and popped once: O(n) time, and the deque holds at most k indices.",
                ],
                "dry": [
                    "i=0 (9): dq = [9]. i=1 (1): smaller, appended, dq = [9, 1].",
                    "i=2 (2): pop 1 because 1 ≤ 2, giving dq = [9, 2]. Output <strong>9</strong>.",
                    "i=3 (3): pop 2, giving dq = [9, 3]; the front 9 is at index 0 ≤ 0, so it has expired. dq = [3], output <strong>3</strong>.",
                    "i=4 (1): dq = [3, 1], output <strong>3</strong>.",
                    "i=5 (4): pop 1 and 3, dq = [4], output <strong>4</strong>. i=6 (0): dq = [4, 0], output <strong>4</strong>.",
                    "The result is <strong>[9, 3, 3, 4, 4]</strong>.",
                ],
            },
        },
    },
}
