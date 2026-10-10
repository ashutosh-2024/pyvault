"""Write-ups for the Sliding Window topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ contains duplicate II
    "contains-duplicate-ii": {
        "examples": [
            {"call": "contains_nearby_duplicate([1, 2, 3, 1, 4, 2, 4], 2)", "expect": "True"},
            {"call": "contains_nearby_duplicate([1, 2, 3, 1, 2, 3], 2)", "expect": "False"},
        ],
        "approaches": {
            "Check the next k elements from each index": {
                "idea": [
                    "Two equal values only count if their indices are <strong>at most k apart</strong>, so the distance limit is part of the question, not a detail.",
                    "For any index <code>i</code>, the only partners that can work are <code>i + 1</code> up to <code>i + k</code>. Anything further is too far by definition.",
                    "So instead of comparing every pair in the array, compare each element only with the k elements after it.",
                ],
                "steps": [
                    "Loop <code>i</code> over every index of <code>nums</code>.",
                    "For each <code>i</code>, loop <code>j</code> from <code>i + 1</code> up to <code>min(len(nums), i + k + 1)</code> (exclusive), so <code>j</code> never runs past the end.",
                    "If <code>nums[i] == nums[j]</code>, a close duplicate exists: return <code>True</code> straight away.",
                    "If the inner loop finishes, no partner for <code>i</code> exists within distance k; move to the next <code>i</code>.",
                    "If every <code>i</code> has been tried, return <code>False</code>.",
                ],
                "why": [
                    "Every pair at distance 1 to k is looked at exactly once, from its left end, so a valid pair cannot be missed.",
                    "Pairs further than k apart are never compared, and they could never count, so skipping them loses nothing.",
                    "Each index does up to k comparisons, giving <strong>O(n · k)</strong> time. Only two indices are kept, so space is <strong>O(1)</strong>.",
                    "Neighbouring windows overlap in k − 1 elements but are re-read from scratch: that repeated work is what the faster approaches remove.",
                ],
                "dry": [
                    [
                        "k = 2, so each index is compared with the next two only.",
                        "i=0 (1): compares with 2 and 3. No match.",
                        "i=1 (2): compares with 3 and 1. i=2 (3): compares with 1 and 4. No match.",
                        "i=3 (1): compares with 4 and 2. The 1 at index 0 is 3 behind, so it is never looked at.",
                        "i=4 (4): compares with 2 (index 5), then 4 (index 6). Equal at distance 2, so it returns <strong>True</strong>.",
                    ],
                    [
                        "i=0 (1): compares with 2, 3. i=1 (2): compares with 3, 1.",
                        "i=2 (3): compares with 1, 2. i=3 (1): compares with 2, 3.",
                        "i=4 (2): only index 5 is left (3). i=5: nothing after it.",
                        "Each value repeats exactly 3 positions later, one more than k allows, so no comparison matches.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>min(len(nums), i + k + 1)</code> and not just <code>i + k + 1</code>?",
                     "Near the end of the array <code>i + k</code> can be past the last index. Capping the range stops <code>nums[j]</code> from raising an IndexError."],
                    ["What if k is 0?",
                     "Then the inner range is empty for every <code>i</code>, so nothing is compared and the answer is <code>False</code>, which is correct: two different indices are always at least 1 apart."],
                    ["Is this ever the right answer in an interview?",
                     "Only as the warm-up. When k is close to n it is quadratic, so state it, give its cost, then move on to the hash map or the window."],
                ],
            },
            "Last index seen for each value": {
                "idea": [
                    "When a value appears again, the only earlier copy worth checking is the <em>most recent</em> one, because it is the closest.",
                    "If the most recent copy is too far away, every older copy is even further away, so none of them can help.",
                    "A dictionary from value to the last index where it appeared answers that check in O(1).",
                ],
                "steps": [
                    "Create an empty dictionary <code>last</code>.",
                    "Scan the array with index <code>i</code> and value <code>x</code>.",
                    "If <code>x</code> is in <code>last</code> and <code>i - last[x] &lt;= k</code>, return <code>True</code>.",
                    "Otherwise set <code>last[x] = i</code>. The newest index is always the best one to compare future copies against.",
                    "After the loop, return <code>False</code>.",
                ],
                "why": [
                    "For each element the closest earlier copy is the only candidate that matters, and the dictionary always holds exactly that index.",
                    "Overwriting <code>last[x]</code> even when the distance check fails is correct: the old index can only be worse for every later element.",
                    "One dictionary lookup and one store per element gives <strong>O(n)</strong> time.",
                    "The dictionary holds one entry per distinct value, which is <strong>O(n)</strong> space in the worst case even when k is small.",
                ],
                "dry": [
                    [
                        "i=0..2: store 1→0, 2→1, 3→2.",
                        "i=3 (1): last[1] = 0 and 3 − 0 = 3 &gt; 2, too far. Update last[1] = 3.",
                        "i=4 (4): new value, store 4→4.",
                        "i=5 (2): last[2] = 1 and 5 − 1 = 4 &gt; 2. Update last[2] = 5.",
                        "i=6 (4): last[4] = 4 and 6 − 4 = 2 ≤ 2, so it returns <strong>True</strong>.",
                    ],
                    [
                        "i=0..2: store 1→0, 2→1, 3→2.",
                        "i=3 (1): distance 3 − 0 = 3 &gt; 2. Update last[1] = 3.",
                        "i=4 (2): distance 4 − 1 = 3 &gt; 2. Update last[2] = 4.",
                        "i=5 (3): distance 5 − 2 = 3 &gt; 2. Update last[3] = 5.",
                        "The loop ends without a close pair: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why update <code>last[x]</code> even when the pair was too far apart?",
                     "Because future copies of <code>x</code> are closer to the new index than to the old one. Keeping the old index would make later checks fail when they should pass."],
                    ["Could I store a list of all indices per value instead?",
                     "You could, but only the last one is ever useful, so the list just costs memory and time."],
                    ["Why is this O(n) space when only k elements matter?",
                     "The dictionary never forgets old values. The sliding-set approach fixes that by deleting values once they are more than k behind."],
                ],
            },
            "Set of the last k values": {
                "idea": [
                    "Only the previous k elements can pair with the current one, so keep exactly those in a set: a <strong>fixed-size sliding window</strong>.",
                    "If the current value is already in the window, there is a duplicate at distance at most k.",
                    "After adding the current value, evict the element that is now k + 1 positions behind, so the window never grows past k.",
                ],
                "steps": [
                    "Create an empty set <code>window</code>.",
                    "For each index <code>i</code> with value <code>x</code>: if <code>x in window</code>, return <code>True</code>.",
                    "Add <code>x</code> to the window.",
                    "If the window now holds more than k values, remove <code>nums[i - k]</code>, the oldest one.",
                    "If the loop finishes, return <code>False</code>.",
                ],
                "why": [
                    "Just before index <code>i</code> is checked, the set holds exactly <code>nums[i-k .. i-1]</code>: the only values close enough to pair with it.",
                    "The set never holds duplicates, because a duplicate would have returned <code>True</code> before being added, so <code>len(window)</code> really is the window size.",
                    "Each element is added once and removed at most once, so the time is <strong>O(n)</strong> on average.",
                    "The set never holds more than k + 1 values, so space is <strong>O(min(n, k))</strong>, better than the dictionary when k is small.",
                ],
                "dry": [
                    [
                        "i=0..1: add 1 and 2. window = {1, 2}.",
                        "i=2 (3): add 3, size 3 &gt; 2, remove nums[0] = 1. window = {2, 3}.",
                        "i=3 (1): 1 is not in {2, 3}. Add it, remove nums[1] = 2. window = {3, 1}.",
                        "i=4 (4): not in. Add it, remove nums[2] = 3. window = {1, 4}. i=5 (2): not in. Add it, remove 1. window = {4, 2}.",
                        "i=6 (4): 4 is in {4, 2}, so it returns <strong>True</strong>.",
                    ],
                    [
                        "i=0..2: add 1, 2, 3, then remove 1. window = {2, 3}.",
                        "i=3 (1): not in. Add it, remove 2. window = {3, 1}.",
                        "i=4 (2): not in. Add it, remove 3. window = {1, 2}.",
                        "i=5 (3): not in. Add it, remove nums[3] = 1. window = {2, 3}.",
                        "Each repeat arrives just after its twin was evicted, so the answer is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why remove <code>nums[i - k]</code> and not <code>nums[i - k - 1]</code>?",
                     "The removal happens after <code>x</code> is added. The window should then hold indices <code>i-k+1 .. i</code>, ready for index <code>i+1</code>, so index <code>i-k</code> is the one that falls out."],
                    ["Is <code>len(window) &gt; k</code> safe when values repeat?",
                     "Yes. A repeat inside the window would already have returned <code>True</code>, so every value in the set is distinct and its size equals the number of positions it covers."],
                    ["When should I pick this over the dictionary?",
                     "When memory matters and k is much smaller than n. Both are O(n) time; this one keeps only k values."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ best time to buy and sell stock
    "best-time-stock": {
        "examples": [
            {"call": "max_profit([7, 1, 5, 3, 6, 4])", "expect": "5"},
            {"call": "max_profit([2, 4, 1])", "expect": "2"},
        ],
        "approaches": {
            "Every buy/sell pair": {
                "idea": [
                    "A trade is a buy day <code>i</code> and a later sell day <code>j &gt; i</code>, with profit <code>prices[j] - prices[i]</code>.",
                    "Trying every such pair and keeping the largest profit is the direct reading of the problem.",
                    "Starting <code>best</code> at 0 covers the case where every trade loses money: then you simply do not trade.",
                ],
                "steps": [
                    "Set <code>best = 0</code>.",
                    "Loop the buy day <code>i</code> over every index.",
                    "Loop the sell day <code>j</code> over every index after <code>i</code>.",
                    "Update <code>best = max(best, prices[j] - prices[i])</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Every legal trade is one (i, j) pair with i &lt; j, and every pair is tried, so the maximum cannot be missed.",
                    "Selling before buying is impossible because <code>j</code> always starts after <code>i</code>.",
                    "There are n(n − 1)/2 pairs, so it is <strong>O(n²)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (buy at 7): every later price is lower, so all profits are negative. best stays 0.",
                        "i=1 (buy at 1): sell at 5, 3, 6, 4 gives 4, 2, 5, 3. best = 5.",
                        "i=2 (buy at 5): profits −2, 1, −1. i=3 (buy at 3): profits 3, 1.",
                        "i=4 (buy at 6): profit −2. Nothing beats 5.",
                        "It returns <strong>5</strong> (buy at 1, sell at 6).",
                    ],
                    [
                        "i=0 (buy at 2): sell at 4 gives 2, sell at 1 gives −1. best = 2.",
                        "i=1 (buy at 4): sell at 1 gives −3. best stays 2.",
                        "i=2 (buy at 1): no later day to sell on.",
                        "It returns <strong>2</strong>. The cheapest price (1) comes too late to be useful.",
                    ],
                ],
                "faq": [
                    ["Why start <code>best</code> at 0 rather than <code>-inf</code>?",
                     "You are allowed to make no trade at all. A profit of 0 is always available, so a losing trade should never be the answer."],
                    ["Could I just take <code>max(prices) - min(prices)</code>?",
                     "No. The maximum might come before the minimum, as in [2, 4, 1]: 4 − 1 = 3 would mean selling before buying."],
                    ["Why mention this approach at all?",
                     "It is the definition written as code, so it is easy to trust and is what the tests compare the fast versions against."],
                ],
            },
            "Two pointers: move the buy day to any lower price": {
                "idea": [
                    "Fix the sell day. The best buy day for it is the <strong>cheapest price seen so far</strong>.",
                    "So scan once, keeping the lowest price to the left, and ask on each day: what if I sold today?",
                    "Think of it as two pointers: the buy pointer only ever jumps forward to a new low, and the sell pointer walks every day.",
                ],
                "steps": [
                    "Set <code>lowest = prices[0]</code> and <code>best = 0</code>.",
                    "For each later price <code>p</code>:",
                    "First try selling today: <code>best = max(best, p - lowest)</code>.",
                    "Then update the buy day: <code>lowest = min(lowest, p)</code>.",
                    "Return <code>best</code> after the scan.",
                ],
                "why": [
                    "Any optimal trade sells on some day j. At that moment <code>lowest</code> is the minimum of prices[0..j−1], the best possible buy price for day j.",
                    "Since every day is tried as the sell day with its best buy, the maximum over the scan is the true answer.",
                    "Selling is checked <em>before</em> <code>lowest</code> is updated, so a trade never buys and sells on the same day. That would earn 0 anyway, so it is harmless either way.",
                    "One pass with two variables: <strong>O(n)</strong> time, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start: lowest = 7, best = 0.",
                        "p=1: sell gives −6, best stays 0. lowest becomes 1.",
                        "p=5: sell gives 4, best = 4. p=3: sell gives 2.",
                        "p=6: sell gives 5, best = 5. p=4: sell gives 3.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "Start: lowest = 2, best = 0.",
                        "p=4: sell gives 2, best = 2. lowest stays 2.",
                        "p=1: sell gives −1, best stays 2. lowest becomes 1, but no later day is left to use it.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Does the order of the two updates matter?",
                     "Updating <code>lowest</code> first would let you buy and sell on the same day for a profit of 0. That never beats the real answer, so the result is the same, but checking the sale first matches the problem more closely."],
                    ["Why is this called two pointers when there is only one loop?",
                     "<code>lowest</code> is a buy pointer that only moves forward, to a cheaper day. The loop variable is the sell pointer. Together they behave like a window that resets its left edge at each new low."],
                    ["What if prices only fall?",
                     "Every sale gives a negative number, so <code>best</code> stays 0, which is correct: do not trade."],
                ],
            },
            "Kadane on daily changes": {
                "idea": [
                    "A profit from day i to day j equals the sum of the daily changes between them: (p[i+1]−p[i]) + … + (p[j]−p[j−1]).",
                    "So the best trade is the <strong>maximum subarray sum</strong> of the daily changes, which is Kadane's algorithm.",
                    "Kadane keeps the best sum of changes ending today, and restarts at 0 whenever that sum goes negative.",
                ],
                "steps": [
                    "Set <code>best = cur = 0</code>.",
                    "Walk adjacent pairs <code>(a, b)</code> of prices; the change for the day is <code>b - a</code>.",
                    "Extend the current run: <code>cur = max(0, cur + b - a)</code>. Dropping to 0 means buying fresh today.",
                    "Record the best run so far: <code>best = max(best, cur)</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "The changes telescope: summing them from i to j leaves exactly <code>p[j] - p[i]</code>.",
                    "A run with a negative sum can only lower any trade that includes it, so restarting at 0 is always at least as good.",
                    "<code>cur</code> therefore equals the best profit of a trade that sells today, the same quantity as in the two-pointer version.",
                    "One pass, two numbers: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Daily changes: −6, +4, −2, +3, −2.",
                        "−6: cur = max(0, −6) = 0. +4: cur = 4, best = 4.",
                        "−2: cur = 2. +3: cur = 5, best = 5.",
                        "−2: cur = 3.",
                        "It returns <strong>5</strong>, the run +4 −2 +3, which is buying at 1 and selling at 6.",
                    ],
                    [
                        "Daily changes: +2, −3.",
                        "+2: cur = 2, best = 2.",
                        "−3: cur = max(0, −1) = 0. The run is abandoned.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>cur</code> clamped at 0?",
                     "A negative running sum means the trade so far is losing money. Starting a new trade today (sum 0) is better than carrying that loss forward."],
                    ["Is this really different from the two-pointer approach?",
                     "Not in cost. <code>cur</code> here equals <code>p - lowest</code> there. It is worth knowing because it links this problem to Maximum Subarray."],
                    ["What does <code>zip(prices, prices[1:])</code> do with one price?",
                     "It yields no pairs, so the loop does nothing and the answer is 0, which is right: you cannot trade with one day."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest substring without repeats
    "longest-substring-no-repeat": {
        "examples": [
            {"call": 'length_of_longest_substring("abcbdab")', "expect": "4"},
            {"call": 'length_of_longest_substring("abba")', "expect": "2"},
        ],
        "approaches": {
            "Check every substring": {
                "idea": [
                    "A substring has no repeats exactly when the number of distinct characters in it equals its length.",
                    "So list every substring, test it with a set, and keep the longest one that passes.",
                    "This is the definition turned into code, with no cleverness at all.",
                ],
                "steps": [
                    "Loop the start <code>i</code> over every index.",
                    "Loop the end <code>j</code> from <code>i</code> to the last index.",
                    "Build <code>set(s[i:j + 1])</code> and compare its size with <code>j - i + 1</code>.",
                    "If they match, the substring has no repeats: <code>best = max(best, j - i + 1)</code>.",
                    "Return <code>best</code> (0 for an empty string, since the loops never run).",
                ],
                "why": [
                    "Every substring is examined, so the longest valid one is found.",
                    "There are about n²/2 substrings, and building the set for one costs up to n, so the time is <strong>O(n³)</strong>.",
                    "Only one set exists at a time, holding at most min(n, Σ) characters, where Σ is the alphabet size.",
                    "It never stops early: once <code>s[i..j]</code> has a repeat, every longer one from the same start does too, but it checks them anyway.",
                ],
                "dry": [
                    [
                        "i=0: \"a\", \"ab\", \"abc\" pass (best 3). \"abcb\" and everything longer fail.",
                        "i=1: \"b\", \"bc\" pass. \"bcb\" fails.",
                        "i=2: \"c\", \"cb\", \"cbd\", \"cbda\" pass, so best = 4. \"cbdab\" fails.",
                        "i=3..6: the longest that pass are \"bda\", \"dab\", \"ab\" and \"b\", none longer than 4.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "i=0: \"a\", \"ab\" pass (best 2). \"abb\" and \"abba\" fail.",
                        "i=1: \"b\" passes. \"bb\" fails.",
                        "i=2: \"b\", \"ba\" pass, length 2.",
                        "i=3: \"a\" passes.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compare the set's size with the length?",
                     "A set drops duplicates. If nothing was dropped, every character was different."],
                    ["Could I break out of the inner loop at the first repeat?",
                     "Yes, and that is exactly the next approach. It cuts the cost from O(n³) to O(n · Σ)."],
                    ["What is Σ in the complexity?",
                     "The number of different characters that can appear (26 for lowercase letters, 128 for ASCII). A substring with no repeats can never be longer than Σ."],
                ],
            },
            "Extend from each start until a repeat": {
                "idea": [
                    "Fix a start. Grow the substring one character at a time. The first repeat ends every longer substring from that start too.",
                    "So stop at the first repeat instead of checking longer substrings that are certain to fail.",
                    "A set of the characters taken so far makes the repeat check O(1).",
                ],
                "steps": [
                    "For each start <code>i</code>, create an empty set <code>seen</code>.",
                    "Walk characters <code>ch</code> from <code>s[i]</code> onwards.",
                    "If <code>ch</code> is already in <code>seen</code>, break: this start can go no further.",
                    "Otherwise add <code>ch</code> to <code>seen</code>.",
                    "After the walk, <code>len(seen)</code> is the longest run from <code>i</code>; update <code>best</code> with it.",
                ],
                "why": [
                    "The longest repeat-free substring starts somewhere, and from that start the walk takes characters until the first repeat, so it is measured exactly.",
                    "A walk can take at most Σ characters before a repeat is forced, so each start costs O(Σ).",
                    "The total is <strong>O(n · Σ)</strong> time, linear when the alphabet is fixed, but with a large constant and repeated work.",
                    "Space is the one set, <strong>O(Σ)</strong>.",
                ],
                "dry": [
                    [
                        "i=0: takes a, b, c, then b repeats. Length 3.",
                        "i=1: takes b, c, then b repeats. Length 2.",
                        "i=2: takes c, b, d, a, then b repeats. Length 4, best = 4.",
                        "i=3: b, d, a then b repeats: 3. i=4: d, a, b to the end: 3. i=5, 6: 2 and 1.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "i=0: takes a, b, then b repeats. Length 2.",
                        "i=1: takes b, then b repeats. Length 1.",
                        "i=2: takes b, a, end of string. Length 2.",
                        "i=3: takes a. Length 1.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can I break at the first repeat?",
                     "Every longer substring from the same start contains the same two equal characters, so none of them can be valid."],
                    ["Why is this not O(n²)?",
                     "Each walk ends within Σ + 1 steps because there are only Σ different characters. For lowercase letters that is at most 27 steps per start."],
                    ["What work is still repeated?",
                     "Start i+1 re-reads almost everything start i just read. The sliding window keeps that work and only moves the left edge."],
                ],
            },
            "Window with a set, shrink one step at a time": {
                "idea": [
                    "Keep a window <code>s[left..right]</code> that never contains a repeat, and a set of the characters inside it.",
                    "Move <code>right</code> forward one character at a time. If the new character is already inside, move <code>left</code> forward, removing characters, until it is not.",
                    "Every window the loop stops at is valid, and the longest one seen is the answer.",
                ],
                "steps": [
                    "Set <code>window = set()</code>, <code>left = 0</code>, <code>best = 0</code>.",
                    "For each <code>right</code> with character <code>ch</code>:",
                    "While <code>ch</code> is in the window, remove <code>s[left]</code> from the set and increase <code>left</code>.",
                    "Add <code>ch</code> to the window.",
                    "Update <code>best = max(best, right - left + 1)</code>, then continue.",
                ],
                "why": [
                    "For every right edge, the loop finds the smallest <code>left</code> that gives a repeat-free window ending there, which is the longest such window.",
                    "The left edge never moves backwards: if <code>s[left..right]</code> has a repeat, so does every window that starts further left.",
                    "Each character is added once and removed at most once, so the total work is <strong>O(n)</strong> even though there is a loop inside a loop.",
                    "The set holds at most Σ characters: <strong>O(Σ)</strong> space.",
                ],
                "dry": [
                    [
                        "right=0..2: add a, b, c. Window \"abc\", best = 3.",
                        "right=3 (b): b is inside. Remove a (left=1), then b (left=2). Add b. Window \"cb\".",
                        "right=4 (d): add. \"cbd\". right=5 (a): add. \"cbda\", best = 4.",
                        "right=6 (b): b is inside. Remove c (left=3), then b (left=4). Add b. Window \"dab\", length 3.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "right=0, 1: add a, b. Window \"ab\", best = 2.",
                        "right=2 (b): b is inside. Remove a (left=1), then b (left=2). Add b. Window \"b\".",
                        "right=3 (a): a is not in {b}, so add it. Window \"ba\", length 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is a <code>while</code> loop needed instead of one <code>if</code>?",
                     "The repeated character may be several places in from the left edge. Every character before it has to leave too, one step at a time."],
                    ["Isn't a loop inside a loop O(n²)?",
                     "Not here. <code>left</code> only moves forward and stops at n, so across the whole run the inner loop runs at most n times in total."],
                    ["Why update <code>best</code> after adding the character?",
                     "At that point the window is valid and includes the new character, so its length is a real candidate."],
                ],
            },
            "Window with last-seen indices, jump the left edge": {
                "idea": [
                    "The set version moves <code>left</code> one step at a time. But we can work out where it will stop: just past the previous copy of the new character.",
                    "So remember the last index of every character, and jump <code>left</code> straight to <code>last[ch] + 1</code>.",
                    "The previous copy might already be outside the window, so the jump must never move <code>left</code> backwards: take the max.",
                ],
                "steps": [
                    "Set <code>last = {}</code>, <code>left = 0</code>, <code>best = 0</code>.",
                    "For each <code>right</code> with character <code>ch</code>:",
                    "If <code>ch</code> was seen before, set <code>left = max(left, last[ch] + 1)</code>.",
                    "Record <code>last[ch] = right</code>.",
                    "Update <code>best = max(best, right - left + 1)</code>.",
                ],
                "why": [
                    "If the previous copy is inside the window, the window must start just after it to drop the repeat, and no further.",
                    "If the previous copy is before <code>left</code>, it is already out of the window, so <code>left</code> must not move. The <code>max</code> handles both cases.",
                    "Each character costs one dictionary lookup and one store: <strong>O(n)</strong> time with no inner loop at all.",
                    "The dictionary holds one entry per distinct character: <strong>O(Σ)</strong> space.",
                ],
                "dry": [
                    [
                        "right=0..2 (a, b, c): left stays 0, best = 3.",
                        "right=3 (b): last[b] = 1, so left = max(0, 2) = 2. Window \"cb\".",
                        "right=4 (d): length 3. right=5 (a): last[a] = 0, and max(2, 1) = 2, so left stays. Window \"cbda\", best = 4.",
                        "right=6 (b): last[b] = 3, so left = 4. Window \"dab\", length 3.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "right=0, 1 (a, b): best = 2.",
                        "right=2 (b): last[b] = 1, so left = 2. Window \"b\".",
                        "right=3 (a): last[a] = 0, but left = max(2, 1) stays 2. Window \"ba\", length 2.",
                        "Without the max, left would go back to 1 and the window \"bba\" would wrongly count as length 3.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>max(left, last[ch] + 1)</code> and not just <code>last[ch] + 1</code>?",
                     "The previous copy may be to the left of the window already. Jumping to it would move <code>left</code> backwards and bring a repeat back in. \"abba\" shows this."],
                    ["Do I need to delete characters from <code>last</code> when they leave the window?",
                     "No. A stale index is always below <code>left</code>, and the <code>max</code> ignores it."],
                    ["Is this faster than the set window in practice?",
                     "Same O(n), but it does one step per character instead of up to two, and never loops inside a loop."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest repeating character replacement
    "longest-repeating-replacement": {
        "examples": [
            {"call": 'character_replacement("AABABBA", 1)', "expect": "4"},
            {"call": 'character_replacement("ABCBB", 1)', "expect": "4"},
        ],
        "approaches": {
            "Every substring": {
                "idea": [
                    "A substring can become all one letter if you keep its most common letter and replace the rest.",
                    "That costs <code>length - (count of the most common letter)</code> replacements, which must be at most k.",
                    "So check every substring with a running count of letters, and keep the longest one that fits.",
                ],
                "steps": [
                    "Loop the start <code>i</code> over every index and reset <code>counts</code> to 26 zeros.",
                    "Loop the end <code>j</code> from <code>i</code> onwards, adding <code>s[j]</code> to <code>counts</code>.",
                    "Work out the replacements needed: <code>j - i + 1 - max(counts)</code>.",
                    "If that is at most k, update <code>best = max(best, j - i + 1)</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Replacing everything except the most common letter is the cheapest way to make a substring uniform, so the test is exact.",
                    "Counts are extended one character at a time from each start, so a substring is not rebuilt from scratch.",
                    "There are O(n²) substrings and <code>max(counts)</code> scans 26 entries, so the time is <strong>O(26 · n²)</strong>, written O(n²).",
                    "The count array is a fixed 26 entries: <strong>O(26)</strong> space.",
                ],
                "dry": [
                    [
                        "k = 1. i=0: A, AA, AAB (3 − 2 = 1), AABA (4 − 3 = 1) all pass, best = 4. AABAB needs 2, too many.",
                        "i=1: ABA passes (1). ABAB needs 2.",
                        "i=2: BAB (1) and BABB (4 − 3 = 1) pass, length 4 again.",
                        "i=3 onwards: the longest that pass are ABB and BBA, length 3.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "k = 1. i=0: A, AB pass (1 change). ABC needs 2.",
                        "i=1: B, BC, BCB (3 − 2 = 1), BCBB (4 − 3 = 1) pass. best = 4.",
                        "i=2: C, CB, CBB (3 − 2 = 1) pass, length 3.",
                        "i=3, 4: BB and B, shorter.",
                        "It returns <strong>4</strong>: change the C in \"BCBB\".",
                    ],
                ],
                "faq": [
                    ["Why <code>length - max(counts)</code>?",
                     "The cheapest plan keeps the letter that already appears most and changes every other character, and that number is exactly length minus the top count."],
                    ["Why does the code not break once the test fails?",
                     "It could. Once a substring needs more than k changes, longer ones from the same start need at least as many. The window approaches use that fact."],
                    ["Why <code>ord(s[j]) - 65</code>?",
                     "The input is uppercase letters, and <code>ord('A')</code> is 65, so A maps to 0 and Z to 25."],
                ],
            },
            "Sliding window, recompute the max count": {
                "idea": [
                    "If a window needs more than k changes, every window that contains it does too. So valid windows can be grown on the right and shrunk on the left.",
                    "Grow the right edge one letter at a time. While the window needs too many changes, drop letters from the left.",
                    "The check recomputes <code>max(counts)</code> each time, which is a scan of 26 entries.",
                ],
                "steps": [
                    "Set <code>counts = [0] * 26</code>, <code>left = 0</code>, <code>best = 0</code>.",
                    "For each <code>right</code>, add <code>s[right]</code> to the counts.",
                    "While <code>right - left + 1 - max(counts) &gt; k</code>, subtract <code>s[left]</code> from the counts and increase <code>left</code>.",
                    "Now the window is valid: update <code>best</code> with its length.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "For each right edge the loop finds the leftmost start that makes a valid window, which is the longest valid window ending there.",
                    "<code>left</code> never needs to go back: a start that failed for this right edge fails for every later one too.",
                    "Each index enters and leaves once, and each check costs 26, so the time is <strong>O(26 · n)</strong>.",
                    "Only the 26 counts are stored: <strong>O(26)</strong> space.",
                ],
                "dry": [
                    [
                        "right=0..3 (A A B A): needs 4 − 3 = 1 change, valid. best = 4.",
                        "right=4 (B): AABAB needs 5 − 3 = 2. Drop A (left=1): ABAB still needs 2. Drop A (left=2): BAB needs 1.",
                        "right=5 (B): BABB needs 4 − 3 = 1, valid, length 4.",
                        "right=6 (A): BABBA needs 2. Drop B (left=3): ABBA needs 2. Drop A (left=4): BBA needs 1.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "right=0, 1: AB needs 1 change, best = 2.",
                        "right=2 (C): ABC needs 2. Drop A (left=1): BC needs 1.",
                        "right=3 (B): BCB needs 1, best = 3.",
                        "right=4 (B): BCBB needs 1, best = 4.",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the window only shrink from the left?",
                     "We want the longest valid window ending at each right edge. If a start is too far left now, it stays too far left as the right edge moves on."],
                    ["Is <code>max(counts)</code> slow?",
                     "It is 26 steps, a constant. The next approach removes even that by never letting the max decrease."],
                    ["Does the window ever become invalid at the end of a step?",
                     "No. The <code>while</code> loop runs until it is valid, so every length recorded in <code>best</code> is a real answer."],
                ],
            },
            "Sliding window with a never-decreasing max count": {
                "idea": [
                    "We only care about finding a <em>longer</em> window. A longer window needs a higher top count, because length is at most top count plus k.",
                    "So keep <code>max_count</code> as the highest letter count seen in any window so far, and never decrease it.",
                    "When the window is too big, shift it right by one (drop one letter from the left) instead of shrinking it. Its size never decreases, so at the end it is the answer.",
                ],
                "steps": [
                    "Set <code>counts = [0] * 26</code>, <code>left = 0</code>, <code>max_count = 0</code>.",
                    "For each <code>right</code>, add <code>s[right]</code> and update <code>max_count</code> with that letter's count.",
                    "If <code>right - left + 1 - max_count &gt; k</code>, drop <code>s[left]</code> and increase <code>left</code> once. The window slides; it does not shrink.",
                    "Never lower <code>max_count</code>, even after dropping letters.",
                    "Return <code>len(s) - left</code>, the size the window grew to.",
                ],
                "why": [
                    "The window only grows when some letter's count reaches a new high, which means a longer valid window really exists.",
                    "When <code>max_count</code> is stale (too high for the current window), the window may hold an invalid stretch, but it has the size of a valid one found earlier, so the length is still right.",
                    "Sliding instead of shrinking keeps the best size so far, so no separate <code>best</code> variable is needed.",
                    "Every step is O(1): <strong>O(n)</strong> time, <strong>O(26)</strong> space.",
                ],
                "dry": [
                    [
                        "right=0..3 (AABA): max_count = 3, size 4 needs 1 change. The window grows to 4.",
                        "right=4 (B): size 5 − 3 = 2 &gt; 1, so slide: drop A, left = 1. Size stays 4.",
                        "right=5 (B): counts B = 3, max_count stays 3. Size 5 − 3 = 2 &gt; 1, slide: drop A, left = 2.",
                        "right=6 (A): size 5 − 3 = 2 &gt; 1, slide: drop B, left = 3.",
                        "It returns 7 − 3 = <strong>4</strong>.",
                    ],
                    [
                        "right=0, 1 (A, B): max_count = 1, size 2 needs 1 change, fine.",
                        "right=2 (C): size 3 − 1 = 2 &gt; 1, slide: drop A, left = 1.",
                        "right=3 (B): B count 2, max_count = 2. Size 3 − 2 = 1, the window grows to 3.",
                        "right=4 (B): B count 3, max_count = 3. Size 4 − 3 = 1, grows to 4.",
                        "It returns 5 − 1 = <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Isn't a stale <code>max_count</code> wrong?",
                     "It can overstate the current window, but then the window just slides at the size of an earlier valid window. The answer only changes when a real new top count appears, so it is never too large."],
                    ["Why <code>if</code> and not <code>while</code>?",
                     "Each new character makes the window at most one too big, so dropping one character from the left is enough to get back to the best size so far."],
                    ["Why return <code>len(s) - left</code>?",
                     "At the end the window is <code>s[left:]</code>, and its size is the largest valid size ever reached."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ permutation in string
    "permutation-in-string": {
        "examples": [
            {"call": 'check_inclusion("abc", "bbdcabx")', "expect": "True"},
            {"call": 'check_inclusion("ab", "eidboaoo")', "expect": "False"},
        ],
        "approaches": {
            "Generate permutations": {
                "idea": [
                    "A permutation of <code>s1</code> is any rearrangement of its letters. The question asks whether one of them appears in <code>s2</code> as a substring.",
                    "So the most literal answer is: make every rearrangement and search <code>s2</code> for each one.",
                    "Duplicate letters produce identical rearrangements, so put them in a set first.",
                ],
                "steps": [
                    "Generate <code>itertools.permutations(s1)</code>, which yields tuples of letters.",
                    "Put them in a set to drop duplicates.",
                    "For each one, join it into a string and check <code>in s2</code>.",
                    "Return <code>True</code> as soon as one is found, otherwise <code>False</code>.",
                ],
                "why": [
                    "Every possible rearrangement is tried, so if any appears in <code>s2</code> it is found.",
                    "There are up to m! permutations (m = <code>len(s1)</code>), and each substring search costs O(n), so the time is <strong>O(m! · n)</strong>.",
                    "Holding them all in a set is <strong>O(m!)</strong> space. At m = 10 that is 3.6 million strings, so this only works for tiny inputs.",
                ],
                "dry": [
                    [
                        "s1 = \"abc\" has 6 permutations: abc, acb, bac, bca, cab, cba.",
                        "s2 = \"bbdcabx\". Search for each one.",
                        "\"cab\" appears at index 3.",
                        "So <code>any(...)</code> is True and it returns <strong>True</strong>.",
                    ],
                    [
                        "s1 = \"ab\" has 2 permutations: \"ab\" and \"ba\".",
                        "s2 = \"eidboaoo\" contains b next to o, and a between o's, but never a next to b.",
                        "Neither search succeeds.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>set(...)</code>?",
                     "For s1 = \"aab\", permutations gives \"aab\" twice (the two a's swap). The set stops the same search running twice."],
                    ["Does the order of the search matter?",
                     "No. Any permutation found is enough; <code>any</code> stops at the first."],
                    ["Why show this at all?",
                     "It states what the question is. Every faster approach replaces \"is it a rearrangement?\" with \"does it have the same letter counts?\"."],
                ],
            },
            "Sort every window": {
                "idea": [
                    "Two strings are rearrangements of each other exactly when they look the same after sorting.",
                    "A match in <code>s2</code> must have the same length as <code>s1</code>, so only windows of length m need checking.",
                    "Sort each window and compare it with sorted <code>s1</code>.",
                ],
                "steps": [
                    "Compute <code>target = sorted(s1)</code> and <code>m = len(s1)</code> once.",
                    "For each start <code>i</code> from 0 to <code>len(s2) - m</code>, take the window <code>s2[i:i + m]</code>.",
                    "Sort the window and compare it with <code>target</code>.",
                    "Return <code>True</code> on the first match, otherwise <code>False</code>.",
                ],
                "why": [
                    "Sorting puts equal multisets of letters into the same order, so the comparison tests \"same letters, same counts\" exactly.",
                    "Every window of length m is checked, so any match is found.",
                    "There are about n windows, each sorted in O(m log m): <strong>O(n · m log m)</strong> time.",
                    "Each sorted window is a new list of size m: <strong>O(m)</strong> space.",
                ],
                "dry": [
                    [
                        "target = [a, b, c], m = 3.",
                        "\"bbd\" → bbd. \"bdc\" → bcd. Neither matches.",
                        "\"dca\" → acd. No match.",
                        "\"cab\" → abc, a match.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "target = [a, b], m = 2.",
                        "Windows: ei, id, db, bo, oa, ao, oo.",
                        "Sorted, they give ei, di, bd, bo, ao, ao, oo. None is ab.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why only windows of length m?",
                     "A permutation of s1 has exactly m letters, so a longer or shorter substring can never be one."],
                    ["What happens when s1 is longer than s2?",
                     "<code>range(len(s2) - m + 1)</code> is empty, so <code>any</code> returns False. That is right: s2 has no room for it."],
                    ["What is wasted here?",
                     "Neighbouring windows share m − 1 letters but each is sorted from scratch. Counting letters lets us update a window in O(1) instead."],
                ],
            },
            "Fixed window, compare 26 counts": {
                "idea": [
                    "\"Same letters with the same counts\" can be checked with two arrays of 26 counts instead of sorting.",
                    "As the window slides one place, only two counts change: the letter that enters and the letter that leaves.",
                    "So keep the window's counts up to date and compare them with <code>s1</code>'s counts after every slide.",
                ],
                "steps": [
                    "If <code>m &gt; len(s2)</code>, return <code>False</code>.",
                    "Count <code>s1</code> into <code>need</code> and the first m letters of <code>s2</code> into <code>have</code>.",
                    "If <code>need == have</code>, return <code>True</code>.",
                    "For each <code>i</code> from m onwards: add <code>s2[i]</code> and remove <code>s2[i - m]</code> from <code>have</code>.",
                    "After each slide, return <code>True</code> if <code>need == have</code>. If the slides run out, return <code>False</code>.",
                ],
                "why": [
                    "Equal count arrays mean the window is a rearrangement of s1, and the other way round.",
                    "After the slide at index i, <code>have</code> counts exactly <code>s2[i-m+1 .. i]</code>, so every window is tested once.",
                    "Each slide is O(1), but each comparison checks 26 entries: <strong>O(26 · n)</strong> time.",
                    "Two arrays of 26: <strong>O(26)</strong> space, which is O(1).",
                ],
                "dry": [
                    [
                        "need = a1 b1 c1. First window \"bbd\": have = b2 d1. Not equal.",
                        "i=3: add c, remove b: \"bdc\" = b1 c1 d1. Not equal.",
                        "i=4: add a, remove b: \"dca\" = a1 c1 d1. Not equal.",
                        "i=5: add b, remove d: \"cab\" = a1 b1 c1. Equal.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "need = a1 b1. First window \"ei\". Not equal.",
                        "Slides give id, db, bo, oa, ao, oo.",
                        "A window holding one a and one b never appears: b sits next to d and o only.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why 26 counts?",
                     "The input is lowercase English letters, so <code>ord(ch) - 97</code> maps a..z to 0..25."],
                    ["Why check before the loop as well?",
                     "The loop only checks after it slides. Without the check before it, a match in the very first window would be missed."],
                    ["Can I avoid comparing all 26 counts each time?",
                     "Yes: track how many of the 26 letters currently match, and update that number as two counts change. That is the next approach."],
                ],
            },
            "Fixed window with a matches counter": {
                "idea": [
                    "Instead of comparing 26 counts after each slide, keep <code>matches</code>: how many of the 26 letters have <code>need[x] == have[x]</code>.",
                    "A slide changes only two counts, so <code>matches</code> can change by at most two, and we can update it exactly.",
                    "The window is a permutation of s1 exactly when <code>matches == 26</code>.",
                ],
                "steps": [
                    "Return <code>False</code> early if <code>m &gt; len(s2)</code>. Count <code>s1</code> and the first window as before.",
                    "Set <code>matches</code> to the number of letters whose two counts agree.",
                    "<code>change(idx, delta)</code>: if the letter matched before the change, subtract 1 from matches; apply the delta; if it matches now, add 1.",
                    "For each <code>i</code> from m: if <code>matches == 26</code>, return <code>True</code>. Otherwise <code>change</code> the incoming letter by +1 and the outgoing one by −1.",
                    "After the loop, return <code>matches == 26</code> to cover the last window.",
                ],
                "why": [
                    "<code>change</code> removes the letter's old contribution and adds its new one, so <code>matches</code> is always correct.",
                    "<code>matches == 26</code> means every count agrees, which is the same test as <code>need == have</code>.",
                    "Every step is O(1), so the time is <strong>O(n)</strong> with no 26 factor in the loop.",
                    "Space is two count arrays: <strong>O(26)</strong>.",
                ],
                "dry": [
                    [
                        "need = a1 b1 c1, first window \"bbd\". Letters a, b, c, d disagree, 22 agree: matches = 22.",
                        "i=3: add c (now agrees, 23), remove b (2 → 1, agrees, 24). Window \"bdc\".",
                        "i=4: add a (25), remove b (1 → 0, disagrees, 24). Window \"dca\".",
                        "i=5: add b (25), remove d (1 → 0, agrees, 26). Window \"cab\".",
                        "i=6: the check sees matches == 26 and returns <strong>True</strong>.",
                    ],
                    [
                        "need = a1 b1, first window \"ei\": a, b, e, i disagree, so matches = 22.",
                        "Slides to \"id\" (22), \"db\" (24), \"bo\" (24), \"oa\" (24).",
                        "\"ao\" stays at 24 (o goes 1 → 2 → 1). \"oo\" drops to 23 when a leaves.",
                        "matches never reaches 26, and the final check fails too.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why subtract before the change and add after?",
                     "The letter's status may flip either way. Removing its old contribution and adding the new one handles all four cases (match→match, match→no, no→match, no→no) with no branches."],
                    ["Why the final <code>return matches == 26</code>?",
                     "The check at the top of the loop looks at the window before each slide. The window after the last slide is only checked here."],
                    ["Is the 26 · n approach really slower?",
                     "Both are linear for a fixed alphabet. This one matters when the alphabet is large, or when an interviewer asks for O(n) with no constant factor."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum size subarray sum
    "minimum-size-subarray-sum": {
        "examples": [
            {"call": "min_subarray_len(7, [2, 3, 1, 2, 4, 3])", "expect": "2"},
            {"call": "min_subarray_len(11, [1, 2, 3, 4, 5])", "expect": "3"},
        ],
        "approaches": {
            "Every start, extend until the target": {
                "idea": [
                    "For each start, add elements to the right until the sum reaches the target. That gives the shortest valid subarray starting there.",
                    "All numbers are positive, so once the sum reaches the target, going further only makes it longer: stop there.",
                    "The answer is the shortest of these, or 0 if no start ever reaches the target.",
                ],
                "steps": [
                    "Set <code>best = inf</code>.",
                    "For each start <code>i</code>, set <code>total = 0</code>.",
                    "Walk <code>j</code> from <code>i</code>, adding <code>nums[j]</code> to <code>total</code>.",
                    "When <code>total &gt;= target</code>, record <code>j - i + 1</code> and break.",
                    "Return 0 if <code>best</code> is still infinite, otherwise <code>best</code>.",
                ],
                "why": [
                    "The shortest valid subarray has some start, and for that start the walk stops at exactly its end.",
                    "Breaking early is safe because a longer subarray from the same start can never be shorter.",
                    "In the worst case each start walks to the end: <strong>O(n²)</strong> time.",
                    "Only a few numbers are kept: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "target = 7. i=0: 2, 5, 6, 8 reaches 7 at j=3, length 4.",
                        "i=1: 3, 4, 6, 10 at j=4, length 4. i=2: 1, 3, 7 at j=4, length 3.",
                        "i=3: 2, 6, 9 at j=5, length 3.",
                        "i=4: 4, 7 at j=5, length 2. i=5: 3 never reaches 7.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "target = 11. i=0: 1, 3, 6, 10, 15 at j=4, length 5.",
                        "i=1: 2, 5, 9, 14 at j=4, length 4.",
                        "i=2: 3, 7, 12 at j=4, length 3.",
                        "i=3: 4, 9 never reaches 11. i=4: 5, never.",
                        "It returns <strong>3</strong> ([3, 4, 5]).",
                    ],
                ],
                "faq": [
                    ["Why does positivity matter?",
                     "It makes running sums only go up, so stopping at the first point the target is reached is safe. With negative numbers that is no longer true."],
                    ["Why return 0 instead of infinity?",
                     "The problem says to return 0 when no subarray reaches the target."],
                    ["What does this do too often?",
                     "Each start re-adds almost the same numbers as the start before it. The window keeps that sum and only removes from the left."],
                ],
            },
            "Prefix sums and binary search": {
                "idea": [
                    "With prefix sums <code>P</code>, the sum of <code>nums[i:j]</code> is <code>P[j] - P[i]</code>.",
                    "For start <code>i</code> we want the smallest <code>j</code> with <code>P[j] &gt;= P[i] + target</code>.",
                    "All numbers are positive, so <code>P</code> is strictly increasing and that <code>j</code> can be binary-searched.",
                ],
                "steps": [
                    "Build <code>P</code> with <code>P[0] = 0</code> and <code>P[k+1] = P[k] + nums[k]</code>.",
                    "For each start <code>i</code>, find <code>j = bisect_left(P, P[i] + target)</code>.",
                    "If <code>j &lt;= n</code>, the subarray <code>nums[i:j]</code> reaches the target; record <code>j - i</code>.",
                    "If <code>j</code> is past the end, no subarray from <code>i</code> works; skip it.",
                    "Return 0 if nothing was recorded, else the best length.",
                ],
                "why": [
                    "<code>bisect_left</code> returns the first index whose prefix is at least <code>P[i] + target</code>, which is the shortest end for that start.",
                    "Trying every start and taking the minimum gives the answer.",
                    "n binary searches of O(log n) each: <strong>O(n log n)</strong> time.",
                    "The prefix array is <strong>O(n)</strong> extra space.",
                ],
                "dry": [
                    [
                        "P = [0, 2, 5, 6, 8, 12, 15].",
                        "i=0: search for 7, j=4 (P=8), length 4. i=1: search 9, j=5, length 4.",
                        "i=2: search 12, j=5, length 3. i=3: search 13, j=6, length 3.",
                        "i=4: search 15, j=6, length 2. i=5: search 19, j=7, past the end, skip.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "P = [0, 1, 3, 6, 10, 15].",
                        "i=0: search 11, j=5, length 5. i=1: search 12, j=5, length 4.",
                        "i=2: search 14, j=5, length 3.",
                        "i=3: search 17 and i=4: search 21 both land at 6, past the end.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>bisect_left</code> and not <code>bisect_right</code>?",
                     "We want the first prefix that is at least the goal, including one exactly equal to it. <code>bisect_right</code> would skip past an exact match."],
                    ["When is this approach the one to use?",
                     "When you need to answer many targets on the same array, since the prefix array is built once. For a single target the window is simpler and faster."],
                    ["What if numbers could be negative?",
                     "Then P is not sorted and binary search is invalid. You would need a monotonic deque over prefix sums (LeetCode 862)."],
                ],
            },
            "Variable window": {
                "idea": [
                    "Grow a window on the right until its sum reaches the target, then shrink it from the left as far as it stays valid.",
                    "Every time the window is valid, its length is a candidate.",
                    "Because all numbers are positive, both edges only ever move right, so each element is added once and removed once.",
                ],
                "steps": [
                    "Set <code>left = total = 0</code> and <code>best = inf</code>.",
                    "For each <code>right</code>, add <code>nums[right]</code> to <code>total</code>.",
                    "While <code>total &gt;= target</code>: record <code>right - left + 1</code>, subtract <code>nums[left]</code>, and increase <code>left</code>.",
                    "Continue with the next <code>right</code>.",
                    "Return 0 if <code>best</code> is still infinite, otherwise <code>best</code>.",
                ],
                "why": [
                    "For each right edge, the inner loop finds the largest left that still reaches the target, which is the shortest valid window ending there.",
                    "A start dropped by the inner loop can never be useful again: with a later right edge it would only give a longer window.",
                    "Both pointers move at most n times: <strong>O(n)</strong> time in total.",
                    "Three variables: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "right=0..3: total = 8 ≥ 7. Record 4, drop 2 (total 6, left 1).",
                        "right=4: total = 10. Record 4, drop 3 (total 7). Still ≥ 7: record 3, drop 1 (total 6, left 3).",
                        "right=5: total = 9. Record 3, drop 2 (total 7). Record 2, drop 4 (total 3, left 5).",
                        "No more elements.",
                        "It returns <strong>2</strong> ([4, 3]).",
                    ],
                    [
                        "right=0..3: total = 10, below 11.",
                        "right=4: total = 15. Record 5, drop 1 (14). Record 4, drop 2 (12).",
                        "Record 3, drop 3 (9, below 11). Stop shrinking.",
                        "The scan ends.",
                        "It returns <strong>3</strong> ([3, 4, 5]).",
                    ],
                ],
                "faq": [
                    ["Why record the length before shrinking?",
                     "The window is valid at that moment. After removing <code>nums[left]</code> it may no longer reach the target."],
                    ["Why <code>while</code> and not <code>if</code>?",
                     "One new element can make several left elements unnecessary, as in the second dry run where three were dropped."],
                    ["Does this work with zeros or negatives?",
                     "Zeros are fine. Negatives break it, because shrinking could then raise the sum and the window logic no longer holds."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find k closest elements
    "find-k-closest-elements": {
        "examples": [
            {"call": "find_closest_elements([1, 2, 3, 4, 5, 6, 7, 8], 3, 5)", "expect": "[4, 5, 6]"},
            {"call": "find_closest_elements([1, 2, 3, 4, 5], 4, 3)", "expect": "[1, 2, 3, 4]"},
        ],
        "approaches": {
            "Sort by distance": {
                "idea": [
                    "\"Closest\" is defined by distance <code>|a - x|</code>, with ties going to the smaller value. That is just a sort key.",
                    "Sort by <code>(|a - x|, a)</code>, take the first k, and sort those back into ascending order for the output.",
                    "It ignores that the input is already sorted, so it is simple but not optimal.",
                ],
                "steps": [
                    "Sort <code>arr</code> by the key <code>(abs(a - x), a)</code>.",
                    "Take the first k elements of that order.",
                    "Sort those k into ascending order.",
                    "Return them.",
                ],
                "why": [
                    "The key puts closer values first and breaks ties toward the smaller value, exactly as the problem defines it.",
                    "The first k in that order are the k closest by definition.",
                    "The sort is <strong>O(n log n)</strong> and the final sort of k items is O(k log k).",
                    "The sorted copy is <strong>O(n)</strong> extra space.",
                ],
                "dry": [
                    [
                        "x = 5. Distances: 5→0, 4→1, 6→1, 3→2, 7→2, 2→3, 8→3, 1→4.",
                        "Sorted by (distance, value): 5, 4, 6, 3, 7, 2, 8, 1.",
                        "First k = 3: 5, 4, 6.",
                        "Sorted back: <strong>[4, 5, 6]</strong>.",
                    ],
                    [
                        "x = 3. Distances: 3→0, 2→1, 4→1, 1→2, 5→2.",
                        "Ties at distance 2 go to the smaller value, so 1 comes before 5.",
                        "First k = 4: 3, 2, 4, 1.",
                        "Sorted back: <strong>[1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the tuple <code>(abs(a - x), a)</code>?",
                     "Python compares tuples left to right, so equal distances fall through to comparing the value, giving the smaller one first."],
                    ["Why sort again at the end?",
                     "The output must be in ascending order, but the first k by distance are ordered by closeness."],
                    ["What does this leave on the table?",
                     "The input is sorted, so the k closest always form one contiguous block. The next two approaches find that block directly."],
                ],
            },
            "Shrink a window from both ends": {
                "idea": [
                    "Because the array is sorted, the k closest elements are always one <strong>contiguous block</strong>.",
                    "Start with the whole array and remove one end at a time, always removing whichever end is further from x.",
                    "On a tie, drop the right end, because the smaller value wins ties.",
                ],
                "steps": [
                    "Set <code>lo = 0</code> and <code>hi = len(arr) - 1</code>.",
                    "While the window holds more than k elements:",
                    "If <code>x - arr[lo] &lt;= arr[hi] - x</code>, the right end is at least as far: <code>hi -= 1</code>.",
                    "Otherwise the left end is further: <code>lo += 1</code>.",
                    "Return <code>arr[lo:hi + 1]</code>.",
                ],
                "why": [
                    "The end that is further from x can never be in the answer while the other end is still in the window, so dropping it is safe.",
                    "Since the array is sorted, comparing <code>x - arr[lo]</code> with <code>arr[hi] - x</code> compares the two distances without needing <code>abs</code>.",
                    "Exactly n − k removals: <strong>O(n − k)</strong> time.",
                    "Two indices: <strong>O(1)</strong> space beyond the output.",
                ],
                "dry": [
                    [
                        "x = 5, window 1..8. 5 − 1 = 4 vs 8 − 5 = 3: drop 1.",
                        "2..8: 3 vs 3, tie, drop 8. 2..7: 3 vs 2, drop 2.",
                        "3..7: 2 vs 2, tie, drop 7. 3..6: 2 vs 1, drop 3.",
                        "Window 4..6 has 3 elements.",
                        "It returns <strong>[4, 5, 6]</strong>.",
                    ],
                    [
                        "x = 3, window 1..5 has 5 elements, one too many.",
                        "3 − 1 = 2 vs 5 − 3 = 2, a tie.",
                        "Ties go to the smaller value, so drop the right end, 5.",
                        "It returns <strong>[1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the answer always contiguous?",
                     "If some value v is in the answer and u lies between v and x in sorted order, then u is at least as close as v, so u is in the answer too."],
                    ["Why can I drop <code>abs</code>?",
                     "Only the ends are compared. If x is outside the window, one of the two differences is negative, which correctly makes that end the closer one."],
                    ["When is this better than binary search?",
                     "When k is close to n, since n − k is then small. When k is small, binary search wins."],
                ],
            },
            "Binary search the window's left edge": {
                "idea": [
                    "The answer is a block of k elements, so it is fixed by its left edge <code>lo</code>, somewhere in <code>0 .. n − k</code>.",
                    "Compare the window starting at <code>mid</code> with the one starting at <code>mid + 1</code>: they differ only in <code>arr[mid]</code> (dropped) and <code>arr[mid + k]</code> (added).",
                    "If <code>arr[mid]</code> is further from x than <code>arr[mid + k]</code>, the window should start further right. Otherwise it starts at <code>mid</code> or earlier.",
                ],
                "steps": [
                    "Set <code>lo = 0</code> and <code>hi = len(arr) - k</code>.",
                    "While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>.",
                    "If <code>x - arr[mid] &gt; arr[mid + k] - x</code>, set <code>lo = mid + 1</code>.",
                    "Otherwise set <code>hi = mid</code> (a tie keeps the left, smaller values).",
                    "Return <code>arr[lo:lo + k]</code>.",
                ],
                "why": [
                    "As the start moves right, the test \"should it move right again?\" goes from yes to no once and never back, so binary search applies.",
                    "Using the signed differences (no <code>abs</code>) is what makes it work when x lies outside the window. <code>abs</code> breaks ties in the wrong direction.",
                    "The search takes <strong>O(log(n − k))</strong>, plus O(k) to slice the output.",
                    "Space is <strong>O(1)</strong> beyond the output.",
                ],
                "dry": [
                    [
                        "lo = 0, hi = 5 (8 − 3).",
                        "mid=2: drop 3 (distance 2) or add 6 (distance 1)? 2 &gt; 1, so lo = 3.",
                        "mid=4: drop 5 (0) or add 8 (3)? 0 &gt; 3 is false, so hi = 4.",
                        "mid=3: drop 4 (1) or add 7 (2)? 1 &gt; 2 is false, so hi = 3. Now lo = hi = 3.",
                        "It returns arr[3:6] = <strong>[4, 5, 6]</strong>.",
                    ],
                    [
                        "lo = 0, hi = 1 (5 − 4).",
                        "mid=0: compare x − arr[0] = 2 with arr[4] − x = 2.",
                        "2 &gt; 2 is false, a tie, so hi = 0 and the smaller values stay.",
                        "It returns arr[0:4] = <strong>[1, 2, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not compare <code>abs(x - arr[mid])</code> with <code>abs(arr[mid + k] - x)</code>?",
                     "When both values are on the same side of x, abs makes them look equally far or reversed, and the search moves the wrong way. With duplicates like [1, 1, 2, 2, 2, 2, 2, 3, 3] that gives a wrong answer."],
                    ["Why is <code>hi</code> equal to <code>n - k</code> and not <code>n - 1</code>?",
                     "The window must fit: a start after n − k would run past the end."],
                    ["How does the tie rule fit in?",
                     "On equal distances the condition is false, so <code>hi = mid</code> and the window stays left, keeping the smaller value."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum window substring
    "minimum-window-substring": {
        "examples": [
            {"call": 'min_window("ADOBECODEBANC", "ABC")', "expect": '"BANC"'},
            {"call": 'min_window("baab", "aab")', "expect": '"baa"'},
        ],
        "approaches": {
            "Check every substring": {
                "idea": [
                    "A window is valid when, for every letter of <code>t</code>, it holds at least as many copies as <code>t</code> does.",
                    "For each start, extend to the right until the window first becomes valid. That is the shortest valid window from that start.",
                    "Keep the shortest across all starts.",
                ],
                "steps": [
                    "Count <code>t</code> into <code>need</code>. Set <code>best = \"\"</code>.",
                    "For each start <code>i</code>, start an empty counter <code>have</code>.",
                    "Extend <code>j</code> from <code>i</code>, adding <code>s[j]</code> to <code>have</code>.",
                    "When every letter in <code>need</code> is covered, compare with <code>best</code>, keep the shorter, and break.",
                    "Return <code>best</code> (empty if nothing was ever valid).",
                ],
                "why": [
                    "The shortest valid window has some start, and from it the scan stops exactly at that window's end.",
                    "Breaking at the first valid end is safe, since every longer window from the same start is worse.",
                    "There are O(n²) (start, end) steps, and each validity check looks at up to Σ letters: <strong>O(n² · Σ)</strong>.",
                    "The counters hold at most Σ letters: <strong>O(Σ)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0: the first valid end is j=5, giving \"ADOBEC\" (6). best = \"ADOBEC\".",
                        "i=1..4: the first valid windows run to the second A at j=10, lengths 10, 9, 8, 7. None is shorter.",
                        "i=5: \"CODEBA\" (6), a tie, not shorter. i=6: \"ODEBANC\" (7). i=7: \"DEBANC\" (6).",
                        "i=8: \"EBANC\" (5), new best. i=9: \"BANC\" (4), new best.",
                        "i=10 onwards never covers B again. It returns <strong>\"BANC\"</strong>.",
                    ],
                    [
                        "need = a2 b1.",
                        "i=0: b, ba, baa. \"baa\" covers it (a2 b1). best = \"baa\".",
                        "i=1: a, aa, aab. Also length 3, not shorter.",
                        "i=2: a, ab never has two a's. i=3: b alone.",
                        "It returns <strong>\"baa\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is \"at least as many\" the right test and not \"exactly\"?",
                     "Extra letters in the window are allowed. Only missing letters make it fail."],
                    ["Why keep the first window of the shortest length?",
                     "The code only replaces <code>best</code> when strictly shorter. LeetCode guarantees a unique answer, so ties do not matter there."],
                    ["What is slow here?",
                     "Each start rebuilds its counts and re-checks all letters. The sliding window keeps both up to date."],
                ],
            },
            "Sliding window with a 'formed' counter": {
                "idea": [
                    "Grow the right edge until the window covers <code>t</code>, then shrink the left edge as far as it stays covering, recording each valid window.",
                    "Checking coverage letter by letter is slow, so keep <code>formed</code>: the number of distinct letters of <code>t</code> whose count is fully met.",
                    "The window is valid exactly when <code>formed == required</code>, and <code>formed</code> changes only when a count crosses its need.",
                ],
                "steps": [
                    "Count <code>t</code> into <code>need</code>; <code>required = len(need)</code>; <code>formed = 0</code>.",
                    "For each <code>right</code>, add <code>s[right]</code> to <code>have</code>. If its count just reached <code>need</code>, increase <code>formed</code>.",
                    "While <code>formed == required</code>: if the window is shorter than <code>best</code>, record it.",
                    "Still inside that loop, remove <code>s[left]</code>. If its count dropped below its need, decrease <code>formed</code>. Increase <code>left</code>.",
                    "Return the recorded window, or \"\" if none was found.",
                ],
                "why": [
                    "<code>formed</code> goes up only when a count reaches its need exactly, and down only when it drops below, so it always counts the letters that are satisfied.",
                    "For each right edge, the shrink loop finds the shortest valid window ending there, and the overall shortest is among those.",
                    "Each index is added once and removed once: <strong>O(n + m)</strong> time, counting <code>t</code> included.",
                    "The two counters hold at most Σ letters: <strong>O(Σ)</strong> space.",
                ],
                "dry": [
                    [
                        "right reaches 5 (C): \"ADOBEC\" covers A, B, C. Record 6. Drop A, formed falls, left = 1.",
                        "right reaches 10 (A): covered again. Shrink: record nothing shorter, drop D, O, B (another B remains), E.",
                        "At \"CODEBA\" (6, not shorter) drop C: formed falls, left = 6.",
                        "right reaches 12 (C): \"ODEBANC\" is covered. Shrink to \"DEBANC\", \"EBANC\" (record 5), \"BANC\" (record 4). Dropping B breaks it.",
                        "It returns <strong>\"BANC\"</strong>.",
                    ],
                    [
                        "need = a2 b1, required = 2.",
                        "right=0 (b): b met, formed = 1. right=1 (a): a1, not yet.",
                        "right=2 (a): a2 met, formed = 2. Record \"baa\" (3). Drop b: formed = 1, left = 1.",
                        "right=3 (b): formed = 2. \"aab\" is 3, not shorter. Drop a: a1 &lt; 2, formed = 1.",
                        "It returns <strong>\"baa\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>have[ch] == need[ch]</code> and not <code>&gt;=</code> when increasing formed?",
                     "With <code>&gt;=</code>, a third copy of a letter that needs two would increase <code>formed</code> again. Equality fires exactly once, when the need is first met."],
                    ["What about letters in s that are not in t?",
                     "<code>need[ch]</code> is 0 for them. Their count goes from 0 to 1 and never equals 0 again, so they never touch <code>formed</code>."],
                    ["Why store <code>(length, left, right + 1)</code> instead of the substring?",
                     "Slicing a new string on every improvement is extra copying. Storing indices and slicing once at the end keeps it linear."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sliding window maximum
    "sliding-window-maximum": {
        "examples": [
            {"call": "max_sliding_window([9, 1, 2, 3, 1, 4, 0], 3)", "expect": "[9, 3, 3, 4, 4]"},
            {"call": "max_sliding_window([5, 3, 4, 1, 2], 2)", "expect": "[5, 4, 4, 2]"},
        ],
        "approaches": {
            "Max of every window": {
                "idea": [
                    "There are n − k + 1 windows of size k. Take the maximum of each one.",
                    "Python's <code>max</code> over a slice does exactly that.",
                    "It recomputes each window from scratch even though neighbouring windows share k − 1 elements.",
                ],
                "steps": [
                    "Loop <code>i</code> from 0 to <code>n - k</code>.",
                    "Slice the window <code>nums[i:i + k]</code>.",
                    "Append <code>max</code> of the slice to the output.",
                    "Return the list of maxima.",
                ],
                "why": [
                    "Each output entry is the definition applied to one window, so it is correct.",
                    "Each window costs k to slice and k to scan, so the time is <strong>O(n · k)</strong>, which is quadratic when k is about n/2.",
                    "Each slice is a temporary list of k elements, but beyond the output only one exists at a time: <strong>O(k)</strong>, listed as O(1) if you ignore the slice.",
                    "It is the baseline every faster approach is tested against.",
                ],
                "dry": [
                    [
                        "k = 3. [9, 1, 2] → 9.",
                        "[1, 2, 3] → 3. [2, 3, 1] → 3.",
                        "[3, 1, 4] → 4. [1, 4, 0] → 4.",
                        "It returns <strong>[9, 3, 3, 4, 4]</strong>.",
                    ],
                    [
                        "k = 2. [5, 3] → 5.",
                        "[3, 4] → 4. [4, 1] → 4.",
                        "[1, 2] → 2.",
                        "It returns <strong>[5, 4, 4, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is this acceptable in an interview?",
                     "As a starting point only. With n = 10⁵ and k = 5·10⁴ it does billions of steps."],
                    ["Does the slice cost extra memory?",
                     "Yes, k elements per window, freed straight away. <code>max(nums[j] for j in range(i, i + k))</code> avoids the copy but is not faster."],
                    ["What repeated work do the faster versions remove?",
                     "Moving one place only adds one element and removes one. The heap and the deque keep enough information to answer from that."],
                ],
            },
            "Max-heap with lazy deletion": {
                "idea": [
                    "A max-heap gives the largest value at once. Store <code>(-value, index)</code> because Python's <code>heapq</code> is a min-heap.",
                    "Removing the element that leaves the window from the middle of a heap is costly, so do not do it then.",
                    "Instead, when reading the top, pop it while its index is already outside the window: <strong>lazy deletion</strong>.",
                ],
                "steps": [
                    "For each index <code>i</code>, push <code>(-nums[i], i)</code>.",
                    "Once the first full window exists (<code>i &gt;= k - 1</code>), look at the top.",
                    "While the top's index is <code>&lt;= i - k</code>, it has left the window: pop it.",
                    "The top is now the maximum of the current window; append it.",
                    "Return the output list.",
                ],
                "why": [
                    "Stale entries only matter if they are at the top. An expired entry buried lower down cannot affect the answer until it rises, and it is popped then.",
                    "Every live element of the window is in the heap, so a valid top really is the window's maximum.",
                    "Each element is pushed once and popped at most once: <strong>O(n log n)</strong> time.",
                    "Expired entries may stay in the heap, so it can hold up to n entries: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Push 9, 1, 2. i=2: top 9 (index 0) is in the window. Output 9.",
                        "i=3: push 3. Top 9 has index 0 ≤ 0, expired: pop. Top 3. Output 3.",
                        "i=4: push 1. Top 3 (index 3) is fine. Output 3.",
                        "i=5: push 4, top 4. Output 4. i=6: push 0, top 4 (index 5). Output 4.",
                        "The old 2 and 1 are never popped, since they never reach the top. Result: <strong>[9, 3, 3, 4, 4]</strong>.",
                    ],
                    [
                        "k = 2. Push 5, 3. i=1: top 5 (index 0) is in. Output 5.",
                        "i=2: push 4. Top 5 has index 0 ≤ 0: pop. Top 4. Output 4.",
                        "i=3: push 1. Top 4 (index 2) is in. Output 4.",
                        "i=4: push 2. Top 4 has index 2 ≤ 2: pop. Then 3 (index 1): pop. Top 2. Output 2.",
                        "It returns <strong>[5, 4, 4, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store the index in the heap?",
                     "Without it there is no way to tell whether the top value is still inside the window."],
                    ["Why <code>-x</code>?",
                     "<code>heapq</code> only keeps the smallest item on top. Negating turns that into the largest value."],
                    ["Is it bad that expired items stay in the heap?",
                     "It costs memory (up to n entries) and some log factors, but never correctness. The deque approach gets rid of them as they expire."],
                ],
            },
            "Block prefix and suffix maxima": {
                "idea": [
                    "Cut the array into blocks of size k: indices 0..k−1, k..2k−1, and so on.",
                    "Any window of size k either matches one block exactly or spans the end of one block and the start of the next.",
                    "So precompute, within each block, the running maximum from the left (<code>prefix</code>) and from the right (<code>suffix</code>). A window's maximum is <code>max(suffix[i], prefix[i + k - 1])</code>.",
                ],
                "steps": [
                    "Copy <code>nums</code> into <code>prefix</code> and <code>suffix</code>.",
                    "Left to right: if <code>i</code> is not the start of a block (<code>i % k != 0</code>), <code>prefix[i] = max(prefix[i - 1], nums[i])</code>.",
                    "Right to left: if <code>i</code> is not the end of a block (<code>(i + 1) % k != 0</code>), <code>suffix[i] = max(suffix[i + 1], nums[i])</code>.",
                    "For each window start <code>i</code>, the answer is <code>max(suffix[i], prefix[i + k - 1])</code>.",
                    "Return the list of answers.",
                ],
                "why": [
                    "<code>suffix[i]</code> covers i to the end of its block, and <code>prefix[i + k - 1]</code> covers the start of that index's block to i + k − 1.",
                    "Together these two pieces cover exactly the window. When the window is a whole block, both are the block's maximum.",
                    "Two linear passes and one more for the answers: <strong>O(n)</strong> time with no data structures.",
                    "The two arrays are <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "k = 3, blocks [9, 1, 2] [3, 1, 4] [0].",
                        "prefix = [9, 9, 9, 3, 3, 4, 0]. suffix = [9, 2, 2, 4, 4, 4, 0].",
                        "i=0: max(9, prefix[2] = 9) = 9. i=1: max(2, prefix[3] = 3) = 3.",
                        "i=2: max(2, prefix[4] = 3) = 3. i=3: max(4, 4) = 4. i=4: max(4, prefix[6] = 0) = 4.",
                        "It returns <strong>[9, 3, 3, 4, 4]</strong>.",
                    ],
                    [
                        "k = 2, blocks [5, 3] [4, 1] [2].",
                        "prefix = [5, 5, 4, 4, 2]. suffix = [5, 3, 4, 1, 2].",
                        "i=0: max(5, 5) = 5. i=1: max(3, prefix[2] = 4) = 4.",
                        "i=2: max(4, 4) = 4. i=3: max(1, prefix[4] = 2) = 2.",
                        "It returns <strong>[5, 4, 4, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does a window touch at most two blocks?",
                     "Blocks have length k and so does the window, so it can start inside one block and end inside the next, but never reach a third."],
                    ["What about the last, shorter block?",
                     "It is handled by the same rules. Its suffix pass starts at the array's end, and no window needs anything past n − 1."],
                    ["Why learn this when the deque exists?",
                     "It needs no data structure, and the same trick (sparse block maxima) answers range-maximum queries in other problems."],
                ],
            },
            "Monotonic deque of indices": {
                "idea": [
                    "If a newer element is at least as large as an older one, the older one can never be a window's maximum again: it leaves sooner and is not bigger.",
                    "So keep a deque of indices whose values are <strong>strictly decreasing</strong>. Every element that loses this comparison is dropped for good.",
                    "The front of the deque is then the current maximum. When it slides out of the window, pop it from the front.",
                ],
                "steps": [
                    "For each index <code>i</code> with value <code>x</code>:",
                    "While the back of the deque has a value <code>&lt;= x</code>, pop it from the back.",
                    "Append <code>i</code> at the back.",
                    "If the front index is <code>&lt;= i - k</code>, it has left the window: pop it from the front.",
                    "Once <code>i &gt;= k - 1</code>, append <code>nums[dq[0]]</code> to the output.",
                ],
                "why": [
                    "The deque holds, in order, every element that could still be the maximum of some future window, and nothing else.",
                    "Values in the deque decrease from front to back, so the front is the largest live value.",
                    "Each index is pushed once and popped at most once, from one end or the other: <strong>O(n)</strong> time in total.",
                    "The deque never holds more than k indices: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0..1: deque [9, 1]. i=2 (2): pop 1, deque [9, 2]. Output 9.",
                        "i=3 (3): pop 2, deque [9, 3]. 9's index 0 has left: pop it. Output 3.",
                        "i=4 (1): deque [3, 1]. Output 3.",
                        "i=5 (4): pop 1 and 3, deque [4]. Output 4. i=6 (0): deque [4, 0]. Output 4.",
                        "It returns <strong>[9, 3, 3, 4, 4]</strong>.",
                    ],
                    [
                        "k = 2. i=0: deque [5]. i=1 (3): deque [5, 3]. Output 5.",
                        "i=2 (4): pop 3, deque [5, 4]. 5's index 0 has left: pop it. Output 4.",
                        "i=3 (1): deque [4, 1]. Output 4.",
                        "i=4 (2): pop 1, deque [4, 2]. 4's index 2 has left: pop it. Output 2.",
                        "It returns <strong>[5, 4, 4, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store indices and not values?",
                     "The front must be removed once it leaves the window, and only its index says when that happens."],
                    ["Why pop on <code>&lt;=</code> and not just <code>&lt;</code>?",
                     "An older equal value is never needed: the newer copy is just as large and stays longer. Popping it keeps the deque small. Using <code>&lt;</code> is also correct."],
                    ["Why can at most one index leave the front per step?",
                     "The window moves by one, so only index <code>i - k</code> drops out, and the deque holds it at most once."],
                ],
            },
        },
    },
}
