"""Write-ups for the Tries topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ implement trie
    "implement-trie": {
        "examples": [
            {"setup": 't = Trie()\nfor w in ("apple", "app", "bat"):\n    t.insert(w)',
             "call": '[t.search("app"), t.search("ap"), t.startsWith("ap"), t.search("bat"), t.startsWith("ba"), t.startsWith("c")]',
             "expect": "[True, False, True, True, True, False]"},
            {"setup": 't = Trie()\nt.insert("apple")',
             "call": '[t.search("app"), t.startsWith("app"), t.insert("app"), t.search("app")]',
             "expect": "[False, True, None, True]"},
        ],
        "approaches": {
            "Hash set of words, scan for prefixes": {
                "idea": [
                    "Whole-word lookups are exactly what a hash set is good at: <code>search</code> is one membership test.",
                    "Prefix queries are not. A set cannot answer \"does anything start with <code>ap</code>?\" without looking at every stored word.",
                    "This baseline shows precisely what a trie fixes: prefix questions that do not scan the whole collection.",
                ],
                "steps": [
                    "The constructor creates an empty set <code>self.words</code>.",
                    "<code>insert(word)</code>: <code>self.words.add(word)</code>. Inserting the same word twice changes nothing.",
                    "<code>search(word)</code>: return <code>word in self.words</code>.",
                    "<code>startsWith(prefix)</code>: return <code>any(w.startswith(prefix) for w in self.words)</code>, which stops at the first stored word that matches.",
                ],
                "why": [
                    "Both queries are the problem's definitions written directly, so they are correct by construction.",
                    "<code>insert</code> and <code>search</code> hash the whole word: <strong>O(L)</strong> for a word of length L.",
                    "<code>startsWith</code> may compare the prefix with all n stored words, each comparison up to L characters: <strong>O(n · L)</strong> per call, and a miss always pays the full price.",
                    "Space is the total length of the stored words, <strong>O(total characters)</strong>, with no sharing between words that start the same way.",
                ],
                "dry": [
                    [
                        "After the three inserts the set is {\"apple\", \"app\", \"bat\"}.",
                        "<code>search(\"app\")</code>: in the set, True. <code>search(\"ap\")</code>: not in the set, False.",
                        "<code>startsWith(\"ap\")</code>: \"apple\" starts with \"ap\", so <code>any</code> stops early: True.",
                        "<code>search(\"bat\")</code>: True. <code>startsWith(\"ba\")</code>: \"bat\" matches, True.",
                        "<code>startsWith(\"c\")</code>: all three words are checked and none matches, False.",
                        "The result is <strong>[True, False, True, True, True, False]</strong>.",
                    ],
                    [
                        "After <code>insert(\"apple\")</code> the set is {\"apple\"}.",
                        "<code>search(\"app\")</code>: \"app\" is not in the set, False, even though it is a prefix of a stored word.",
                        "<code>startsWith(\"app\")</code>: \"apple\".startswith(\"app\") is True.",
                        "<code>insert(\"app\")</code> returns None and the set becomes {\"apple\", \"app\"}. Now <code>search(\"app\")</code> is True.",
                        "The result is <strong>[False, True, None, True]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>search(\"app\")</code> False when \"apple\" is stored?",
                     "Because <code>search</code> asks whether the exact word was inserted. Being a prefix of another word is what <code>startsWith</code> answers."],
                    ["Is <code>startsWith</code> really that slow?",
                     "For one query on a small set it is fine. With many stored words and many prefix queries, every miss rereads every word, which is what a trie avoids."],
                    ["Could a sorted list and binary search fix <code>startsWith</code>?",
                     "Yes: the first word ≥ the prefix is the only candidate to check, giving O(L log n). But <code>insert</code> into a sorted list then costs O(n) for the shift."],
                ],
            },
            "Node class with a children dict": {
                "idea": [
                    "Store words as paths from a root, one character per edge. Words that share a prefix share the start of their path.",
                    "Each <code>TrieNode</code> has a <code>children</code> dictionary from character to child, plus an <code>is_end</code> flag saying a whole word ends there.",
                    "A prefix exists exactly when its path exists, and a word exists when its path ends at a node with <code>is_end</code> set.",
                ],
                "steps": [
                    "The constructor creates <code>self.root = TrieNode()</code>, an empty node standing for the empty prefix.",
                    "<code>insert</code>: start at the root and, for each <code>ch</code>, step to <code>node.children.setdefault(ch, TrieNode())</code>, creating the child only if it is missing.",
                    "After the last character, set <code>node.is_end = True</code>.",
                    "<code>_walk(s)</code>: follow <code>node.children.get(ch)</code> for each character and return <code>None</code> as soon as a child is missing; otherwise return the last node.",
                    "<code>search</code> needs the walk to succeed <em>and</em> stop on a node with <code>is_end</code>; <code>startsWith</code> only needs the walk to succeed.",
                ],
                "why": [
                    "The path for a string exists exactly when some inserted word has that string as a prefix, because <code>insert</code> creates every node along each word.",
                    "The <code>is_end</code> flag is what separates \"app was inserted\" from \"app is merely a prefix of apple\".",
                    "Every operation touches one node per character: <strong>O(L)</strong> per call, independent of how many words are stored.",
                    "Each node is created once and shared by every word through it, so space is <strong>O(total characters)</strong> in the worst case and less when prefixes overlap.",
                ],
                "dry": [
                    [
                        "\"apple\" creates the path a→p→p→l→e and marks e. \"app\" reuses a→p→p and marks that second p, with no new nodes.",
                        "\"bat\" creates b→a→t from the root and marks t.",
                        "<code>search(\"app\")</code>: the walk ends on the second p, which is marked: True. <code>search(\"ap\")</code>: the first p is not marked: False.",
                        "<code>startsWith(\"ap\")</code>: the path exists, True. <code>search(\"bat\")</code>: t is marked, True. <code>startsWith(\"ba\")</code>: True.",
                        "<code>startsWith(\"c\")</code>: <code>root.children.get(\"c\")</code> is None, so the walk fails: False.",
                        "The result is <strong>[True, False, True, True, True, False]</strong>.",
                    ],
                    [
                        "\"apple\" creates a→p→p→l→e and marks only e.",
                        "<code>search(\"app\")</code>: the walk reaches the second p, but its <code>is_end</code> is False, so False.",
                        "<code>startsWith(\"app\")</code>: the same walk succeeds, so True.",
                        "<code>insert(\"app\")</code> walks the existing nodes and sets <code>is_end</code> on the second p; it returns None.",
                        "<code>search(\"app\")</code> now ends on a marked node. The result is <strong>[False, True, None, True]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>setdefault</code> in <code>insert</code> but <code>get</code> in <code>_walk</code>?",
                     "<code>insert</code> must create missing nodes. A query must not: creating nodes during a failed search would make later <code>startsWith</code> calls return True for prefixes nobody inserted."],
                    ["Why does the root not hold a character?",
                     "The root stands for the empty prefix. Characters live on the edges, so the root's children are the possible first letters."],
                    ["What does <code>__slots__</code> do here?",
                     "It stops each node from carrying its own <code>__dict__</code>, which saves memory when there are many nodes. The algorithm is the same without it."],
                    ["What happens if the same word is inserted twice?",
                     "The second insert walks existing nodes and sets an <code>is_end</code> that is already True, so nothing changes."],
                ],
            },
            "Fixed array of 26 children": {
                "idea": [
                    "Same trie, but each node's children live in a list of 26 slots indexed by <code>ord(ch) - 97</code> instead of a dictionary.",
                    "Nodes are plain integers: <code>self.children[node]</code> is that node's slot list and <code>self.is_end[node]</code> its end flag. Node 0 is the root.",
                    "In compiled languages direct indexing beats hashing; the price is 26 slots per node even when most are empty.",
                ],
                "steps": [
                    "The constructor sets <code>children = [[None] * 26]</code> and <code>is_end = [False]</code>: just the root.",
                    "<code>_child(node, ch, create)</code> reads slot <code>ord(ch) - 97</code>. If it is empty and <code>create</code> is set, it appends a new node, whose id is <code>len(self.children)</code>, and stores that id in the slot.",
                    "<code>insert</code> walks with <code>create=True</code> and sets <code>is_end[node] = True</code> at the end.",
                    "<code>_walk</code> walks with <code>create=False</code> and returns <code>None</code> at the first empty slot.",
                    "<code>search</code> and <code>startsWith</code> use <code>_walk</code> exactly like the dictionary version.",
                ],
                "why": [
                    "The structure and invariants are those of the dictionary trie; only the storage changes from objects to parallel lists.",
                    "Each character costs one list index: <strong>O(L)</strong> per operation.",
                    "Every node allocates 26 slots whether used or not, so space is <strong>O(26 · nodes)</strong>. In Python the dictionary version is usually as fast and smaller.",
                ],
                "dry": [
                    [
                        "\"apple\" creates nodes 1 (a), 2 (p), 3 (p), 4 (l), 5 (e) and sets <code>is_end[5]</code>.",
                        "\"app\" walks 0→1→2→3 without creating anything and sets <code>is_end[3]</code>. \"bat\" creates 6 (b), 7 (a), 8 (t) and sets <code>is_end[8]</code>.",
                        "<code>search(\"app\")</code> ends at node 3, marked: True. <code>search(\"ap\")</code> ends at node 2, unmarked: False.",
                        "<code>startsWith(\"ap\")</code>: node 2 exists, True. <code>search(\"bat\")</code>: node 8 is marked, True. <code>startsWith(\"ba\")</code>: node 7, True.",
                        "<code>startsWith(\"c\")</code>: slot 2 of node 0 is None, False. The result is <strong>[True, False, True, True, True, False]</strong>.",
                    ],
                    [
                        "\"apple\" creates nodes 1 to 5; only <code>is_end[5]</code> is True.",
                        "<code>search(\"app\")</code>: the walk ends at node 3 and <code>is_end[3]</code> is False: False.",
                        "<code>startsWith(\"app\")</code>: node 3 exists: True.",
                        "<code>insert(\"app\")</code> walks 0→1→2→3 and sets <code>is_end[3] = True</code>; it returns None. Then <code>search(\"app\")</code> is True.",
                        "The result is <strong>[False, True, None, True]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>ord(ch) - 97</code>?",
                     "97 is <code>ord(\"a\")</code>, so the letters a to z map to slots 0 to 25. Any other character would index outside that range or wrap to a wrong slot, so this layout assumes lowercase letters only."],
                    ["Why number the nodes instead of making node objects?",
                     "It mirrors how an array-based trie is written in C++ or Java. A list of slot lists, indexed by node id, avoids one object per node."],
                    ["Is <code>is not None</code> needed in <code>_walk</code>'s callers?",
                     "Yes, for <code>startsWith</code> on an empty prefix: the walk returns node 0, which is falsy, so a plain truth test would wrongly say False."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add and search words
    "add-search-words": {
        "examples": [
            {"setup": 'wd = WordDictionary()\nfor w in ("bad", "dad", "mad", "be"):\n    wd.addWord(w)',
             "call": '[wd.search(p) for p in ("pad", "bad", ".ad", "b..", "b.", ".e.")]',
             "expect": "[False, True, True, True, True, False]"},
            {"setup": 'wd = WordDictionary()\nfor w in ("bat", "cat", "ca"):\n    wd.addWord(w)',
             "call": '[wd.search(p) for p in ("c.", ".a", "..t", "b.", "...t")]',
             "expect": "[True, True, True, False, False]"},
        ],
        "approaches": {
            "List of words, match each": {
                "idea": [
                    "A pattern can only match a word of the same length, so store words grouped by length in <code>by_len</code>.",
                    "Then compare the pattern with each candidate letter by letter, letting <code>.</code> match anything.",
                    "Grouping by length removes the obviously impossible candidates for free, but the rest are still checked one by one.",
                ],
                "steps": [
                    "<code>addWord</code>: append the word to <code>by_len.setdefault(len(word), [])</code>.",
                    "<code>search</code>: fetch <code>by_len.get(len(word), [])</code>, an empty list if no word has that length.",
                    "For each candidate <code>w</code>, check <code>all(p == \".\" or p == c for p, c in zip(word, w))</code>.",
                    "<code>any</code> returns True at the first matching candidate, or False after all of them fail.",
                ],
                "why": [
                    "The per-letter rule is exactly the problem's definition of a match, and only same-length words can match, so nothing is wrongly excluded.",
                    "<code>zip</code> is safe because both strings have the same length; it never silently ignores extra letters.",
                    "<code>addWord</code> is <strong>O(1)</strong> amortised. A search can compare against all n stored words of that length: <strong>O(n · L)</strong> per query.",
                    "Space is the stored words themselves: <strong>O(total characters)</strong>.",
                ],
                "dry": [
                    [
                        "<code>by_len</code> = {3: [bad, dad, mad], 2: [be]}.",
                        "\"pad\": p differs from b, d and m, so False. \"bad\": matches \"bad\", True.",
                        "\".ad\": the dot matches b, then a and d match: True. \"b..\": \"bad\" fits: True.",
                        "\"b.\": only length-2 word \"be\", b matches and the dot takes e: True.",
                        "\".e.\": every length-3 word has a in the middle, so False. The result is <strong>[False, True, True, True, True, False]</strong>.",
                    ],
                    [
                        "<code>by_len</code> = {3: [bat, cat], 2: [ca]}.",
                        "\"c.\": compared with \"ca\": c = c, dot takes a, True. \".a\": \"ca\" again, True.",
                        "\"..t\": \"bat\" matches at once, True.",
                        "\"b.\": the only length-2 word is \"ca\", and b ≠ c, so False.",
                        "\"...t\": there is no length-4 list, so <code>get</code> returns [] and <code>any</code> is False. The result is <strong>[True, True, True, False, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why group by length instead of keeping one list?",
                     "A word of another length can never match, and with one list <code>zip</code> would stop at the shorter string and report false matches, such as \"b.\" matching \"bad\"."],
                    ["When is this approach actually fine?",
                     "When there are few words or very few searches. It has the cheapest <code>addWord</code> and no tree overhead."],
                    ["Does a pattern of all dots cost less here?",
                     "No more and no less: every candidate of that length is still checked, and the first one matches immediately."],
                ],
            },
            "Trie with DFS on wildcards": {
                "idea": [
                    "Store the words in a trie made of nested dictionaries, with the key <code>\"$\"</code> marking that a word ends at that node.",
                    "A normal letter follows exactly one child. A dot could be any letter, so it tries <em>every</em> child and succeeds if any branch does.",
                    "Branches die as soon as the trie has no matching child, so even dotted searches usually touch few nodes.",
                ],
                "steps": [
                    "<code>addWord</code>: walk with <code>node.setdefault(ch, {})</code>, then set <code>node[\"$\"] = True</code>.",
                    "<code>dfs(node, i)</code> answers: can <code>word[i:]</code> be matched starting from <code>node</code>?",
                    "If <code>i == len(word)</code>, the whole pattern is consumed: return <code>\"$\" in node</code>.",
                    "If <code>word[i]</code> is a dot, return <code>any(dfs(child, i + 1))</code> over every key except <code>\"$\"</code>.",
                    "Otherwise return <code>ch in node and dfs(node[ch], i + 1)</code>; the search starts with <code>dfs(self.root, 0)</code>.",
                ],
                "why": [
                    "Every root-to-node path spells a prefix of a stored word, so the DFS explores exactly the stored words consistent with the pattern so far.",
                    "Checking <code>\"$\"</code> only when the pattern is used up enforces equal length: a prefix of a longer word does not count.",
                    "Without dots a search is a single walk: <strong>O(L)</strong>. Each dot can fan out to at most 26 children, so the worst case is <strong>O(26<sup>d</sup> · L)</strong> for d dots.",
                    "The trie stores each shared prefix once: <strong>O(total characters)</strong> space, plus O(L) recursion depth during a search.",
                ],
                "dry": [
                    [
                        "The root has children b (with a→d$ and e$), d (a→d$) and m (a→d$).",
                        "\"pad\": the root has no p, so False. \"bad\": b→a→d and <code>\"$\"</code> is there, True.",
                        "\".ad\": the dot tries b first; b→a→d ends with <code>\"$\"</code>, so <code>any</code> stops: True.",
                        "\"b..\": from b, the first dot tries a, the second tries d, and the end has <code>\"$\"</code>: True.",
                        "\"b.\": from b the dot tries a, which is not a word end, then e, which is: True. \".e.\": none of b, d, m has an e child after the first letter, False.",
                        "The result is <strong>[False, True, True, True, True, False]</strong>.",
                    ],
                    [
                        "The trie: root → b→a→t$ and c→a($)→t$, since \"ca\" marks the a under c.",
                        "\"c.\": follow c, then the dot tries a; i = 2 is the end and <code>\"$\"</code> is in that node: True.",
                        "\".a\": the dot tries b first: b→a has no <code>\"$\"</code>, False. It backtracks to c: c→a has <code>\"$\"</code>, True.",
                        "\"..t\": b, a, then t has <code>\"$\"</code>: True. \"b.\": b→a is not a word end and a is b's only child: False.",
                        "\"...t\": every three-letter path ends at a t node with no t child, so both branches fail. The result is <strong>[True, True, True, False, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why skip the <code>\"$\"</code> key when a dot fans out?",
                     "<code>\"$\"</code> is a marker, not a child. Without the check the code would call <code>dfs(True, i + 1)</code>, and treating a bool as a dictionary raises an error."],
                    ["Why does <code>any</code> matter for speed?",
                     "It short-circuits: as soon as one branch matches, the remaining children are not explored."],
                    ["Can \"$\" clash with a real letter?",
                     "Not when words are lowercase letters, as the problem guarantees. With arbitrary characters you would use a separate flag instead of a key."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ extra characters
    "extra-characters-string": {
        "examples": [
            {"call": 'min_extra_char("leetscode", ["leet", "code", "leetcode"])', "expect": "1"},
            {"call": 'min_extra_char("abcd", ["ab", "abc", "d"])', "expect": "0"},
        ],
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Look at the suffix starting at i: either character i is wasted (it costs 1), or some dictionary word starts exactly at i.",
                    "If a word <code>s[i:j]</code> starts there, use it for free and solve the rest from j.",
                    "<code>best(i)</code> is the minimum over all those choices, and the answer is <code>best(0)</code>.",
                ],
                "steps": [
                    "Put the dictionary in a set <code>words</code> for O(1) average lookups.",
                    "<code>best(len(s))</code> returns 0: an empty suffix has no extra characters.",
                    "Start with the skip option: <code>result = 1 + best(i + 1)</code>.",
                    "For every end <code>j</code> from <code>i + 1</code> to <code>len(s)</code>, if <code>s[i:j]</code> is in <code>words</code>, set <code>result = min(result, best(j))</code>.",
                    "Return <code>best(0)</code>.",
                ],
                "why": [
                    "Any split of a suffix starts with either a skipped character or a dictionary word, so the choices cover every split.",
                    "Each recursive call solves a strictly shorter suffix, so the recursion ends.",
                    "Nothing is cached, so the same suffix is solved again from every path that reaches it: <strong>O(2<sup>n</sup>)</strong> time in the worst case.",
                    "The deepest chain is one skip per character: <strong>O(n)</strong> stack space.",
                ],
                "dry": [
                    [
                        "<code>best(0)</code>: skipping 'l' gives <code>1 + best(1)</code>; \"leet\" = s[0:4] gives <code>best(4)</code>.",
                        "<code>best(1)</code> has to skip e, e, t and s before \"code\": it returns 4, so the skip route costs 5.",
                        "<code>best(4)</code>: no word starts with 's', so <code>1 + best(5)</code>.",
                        "<code>best(5)</code>: \"code\" = s[5:9] leads to <code>best(9) = 0</code>, so best(5) = 0 and best(4) = 1.",
                        "best(0) = min(5, 1) = <strong>1</strong>. \"leetcode\" never matches because of the 's'.",
                    ],
                    [
                        "<code>best(0)</code> first skips: best(1) needs best(2), best(3), best(4).",
                        "best(3): skip gives 1, but \"d\" = s[3:4] gives best(4) = 0, so 0. best(2) = 1 (c starts no word). best(1) = 2.",
                        "Back in best(0): skip costs 3. \"ab\" = s[0:2] gives best(2) = 1.",
                        "\"abc\" = s[0:3] gives best(3) = 0, which is solved a second time here.",
                        "best(0) = <strong>0</strong>: \"abc\" + \"d\" covers everything.",
                    ],
                ],
                "faq": [
                    ["Why not just take the longest word at each position?",
                     "Greed can trap you. In \"abcde\" with [\"abcd\", \"abc\", \"de\"], taking \"abcd\" leaves 'e' (1 extra), while \"abc\" + \"de\" costs 0."],
                    ["Why does the loop go up to <code>len(s) + 1</code>?",
                     "<code>j</code> is an exclusive end, so <code>s[i:len(s)]</code>, a word reaching the last character, needs <code>j = len(s)</code>."],
                    ["What would make this fast?",
                     "Caching <code>best(i)</code>, since there are only n + 1 distinct suffixes. That is exactly the bottom-up DP in the next approach."],
                ],
            },
            "DP with a hash set of words": {
                "idea": [
                    "Same recurrence, solved bottom-up: <code>dp[i]</code> is the fewest extra characters in the suffix <code>s[i:]</code>.",
                    "Filling it from the right means every <code>dp[j]</code> with <code>j &gt; i</code> is ready when <code>dp[i]</code> is computed.",
                    "Each suffix is now solved once instead of once per path.",
                ],
                "steps": [
                    "Build <code>words = set(dictionary)</code> and <code>dp = [0] * (n + 1)</code>; <code>dp[n] = 0</code> is the empty suffix.",
                    "For <code>i</code> from <code>n - 1</code> down to 0, start with the skip: <code>dp[i] = 1 + dp[i + 1]</code>.",
                    "For every <code>j</code> from <code>i + 1</code> to <code>n</code>, if <code>s[i:j]</code> is in <code>words</code>, take <code>dp[i] = min(dp[i], dp[j])</code>.",
                    "Return <code>dp[0]</code>.",
                ],
                "why": [
                    "<code>dp[i]</code> considers every first move from i, and every move lands on an already-correct <code>dp[j]</code>, so by induction from the right each cell is optimal.",
                    "There are O(n²) (i, j) pairs, and slicing and hashing <code>s[i:j]</code> costs O(j − i): <strong>O(n³)</strong> time, fine for n ≤ 50.",
                    "The table has n + 1 cells and the set holds the dictionary: <strong>O(n + total characters)</strong> space.",
                ],
                "dry": [
                    [
                        "dp[9] = 0. 'e', 'd', 'o' start no word: dp[8] = 1, dp[7] = 2, dp[6] = 3.",
                        "i=5 ('c'): skip gives 4, but \"code\" = s[5:9] gives dp[9] = 0, so dp[5] = 0.",
                        "i=4 ('s'): no word, dp[4] = 1 + 0 = 1.",
                        "i=3, 2, 1: only skipping is possible, dp = 2, 3, 4.",
                        "i=0: skip gives 5, \"leet\" = s[0:4] gives dp[4] = 1, so dp[0] = <strong>1</strong>.",
                    ],
                    [
                        "dp[4] = 0. i=3 ('d'): skip gives 1, \"d\" gives dp[4] = 0, so dp[3] = 0.",
                        "i=2 ('c'): neither \"c\" nor \"cd\" is a word, dp[2] = 1.",
                        "i=1 ('b'): no word starts with b, dp[1] = 2.",
                        "i=0: skip gives 3, \"ab\" gives dp[2] = 1, \"abc\" gives dp[3] = 0, \"abcd\" is not a word.",
                        "dp[0] = <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why fill from the right instead of the left?",
                     "<code>dp[i]</code> depends on later cells. Defining <code>dp</code> on prefixes instead and filling from the left works equally well; it is a mirror image."],
                    ["Why is the skip always tried first?",
                     "It is always available, so it gives a valid starting value. Words can only lower it."],
                    ["Where does the third factor of n come from?",
                     "From building the slice <code>s[i:j]</code> and hashing it. The trie approach removes it by extending a walk one character at a time."],
                ],
            },
            "DP walking a trie from each start": {
                "idea": [
                    "Most substrings <code>s[i:j]</code> are not even prefixes of a word, so building and hashing them is wasted work.",
                    "Put the dictionary in a trie and, from each start i, walk the trie along s. Every word-end node met gives a candidate.",
                    "Stop the walk as soon as the trie has no matching child, because no word continues that way.",
                ],
                "steps": [
                    "Build the trie of nested dictionaries, marking word ends with <code>\"$\"</code>.",
                    "For <code>i</code> from <code>n - 1</code> down to 0, start with <code>dp[i] = 1 + dp[i + 1]</code> and <code>node = root</code>.",
                    "For <code>j</code> from <code>i</code>, step <code>node = node.get(s[j])</code>; if it is <code>None</code>, break.",
                    "If <code>\"$\"</code> is in <code>node</code>, the word <code>s[i:j+1]</code> exists: <code>dp[i] = min(dp[i], dp[j + 1])</code>.",
                    "Return <code>dp[0]</code>.",
                ],
                "why": [
                    "The walk from i visits exactly the dictionary words that start at i, in order of length, so it tries the same candidates as the hash-set DP.",
                    "Each step extends the current prefix by one character in O(1), with no slicing.",
                    "Each start walks at most n − i characters: <strong>O(n²)</strong> time in the worst case, usually far less because walks die early.",
                    "The trie and the table take <strong>O(n + total characters)</strong> space.",
                ],
                "dry": [
                    [
                        "The trie holds l→e→e→t($)→c→o→d→e($) and c→o→d→e($).",
                        "i=8, 7, 6: 'e', 'd', 'o' are not root children, so each walk breaks at once: dp = 1, 2, 3.",
                        "i=5: the walk c→o→d→e reaches <code>\"$\"</code> at j=8, so dp[5] = min(4, dp[9]) = 0.",
                        "i=4: 's' is not a root child, dp[4] = 1. i=3, 2, 1 also break at once: dp = 2, 3, 4.",
                        "i=0: l→e→e→t hits <code>\"$\"</code> at j=3, so dp[0] = min(5, dp[4]) = 1; t has no 's' child, so the walk stops. The answer is <strong>1</strong>.",
                    ],
                    [
                        "The trie: a→b($)→c($) and d($).",
                        "i=3: d has <code>\"$\"</code>, so dp[3] = min(1, dp[4]) = 0.",
                        "i=2 and i=1: 'c' and 'b' are not root children, dp[2] = 1, dp[1] = 2.",
                        "i=0: a, then b has <code>\"$\"</code> (dp[2] = 1), then c has <code>\"$\"</code> (dp[3] = 0); c has no 'd' child, so the walk stops.",
                        "dp[0] = min(3, 1, 0) = <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>dp[j + 1]</code> here but <code>dp[j]</code> in the hash-set version?",
                     "Here <code>j</code> is the index of the last character matched, so the word is <code>s[i:j+1]</code> and the rest starts at <code>j + 1</code>. In the hash-set version <code>j</code> is already an exclusive end."],
                    ["Why not stop the walk at the first word end?",
                     "A longer word may lead to a better answer, as \"abc\" beats \"ab\" in \"abcd\". The walk continues until the trie runs out."],
                    ["Is the trie worth it for a tiny dictionary?",
                     "The asymptotic gain is the removed slicing cost. In practice it matters most when many substrings are not word prefixes, so the walks break almost immediately."],
                ],
            },
        },
    },
}
