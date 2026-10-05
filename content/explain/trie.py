"""Write-ups for the Tries topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ implement trie
    "implement-trie": {
        "example": {"setup": 't = Trie()\nfor w in ("apple", "app", "bat"):\n    t.insert(w)',
                    "call": '[t.search("app"), t.search("ap"), t.startsWith("ap"), t.search("bat"), t.startsWith("ba"), t.startsWith("c")]',
                    "expect": "[True, False, True, True, True, False]"},
        "approaches": {
            "Hash set of words, scan for prefixes": {
                "idea": [
                    "Whole-word lookups are exactly what a hash set is good at.",
                    "Prefix queries are not: a set cannot answer \"does anything start with <code>ap</code>\" without looking at every word.",
                    "This baseline shows what a trie fixes: prefix questions that do not scan all words.",
                ],
                "steps": [
                    "<code>insert</code>: add the word to the set.",
                    "<code>search</code>: membership test, <code>word in self.words</code>.",
                    "<code>startsWith</code>: check <code>w.startswith(prefix)</code> for every stored word.",
                ],
                "why": [
                    "Both queries are answered by definition, so they are correct.",
                    "<code>insert</code> and <code>search</code> cost O(L) for hashing, but <code>startsWith</code> costs O(n·L) over n words. Space is the total length of all words.",
                ],
                "dry": [
                    "The set is {\"apple\", \"app\", \"bat\"}.",
                    "<code>search(\"app\")</code>: in the set, <strong>True</strong>. <code>search(\"ap\")</code>: not in the set, <strong>False</strong>.",
                    "<code>startsWith(\"ap\")</code>: \"apple\" starts with it, <strong>True</strong>.",
                    "<code>search(\"bat\")</code>: <strong>True</strong>. <code>startsWith(\"ba\")</code>: \"bat\" matches, <strong>True</strong>.",
                    "<code>startsWith(\"c\")</code>: no word starts with c, so after checking all three, <strong>False</strong>.",
                ],
            },
            "Node class with a children dict": {
                "idea": [
                    "Store words as paths from a root, one character per edge. Words that share a prefix share the start of their path.",
                    "Each node has a dictionary from character to child, plus an <code>is_end</code> flag marking that a whole word ends there.",
                    "A prefix exists exactly when its path exists, and a word exists when its path ends at a node marked <code>is_end</code>.",
                ],
                "steps": [
                    "<code>insert</code>: walk from the root, creating missing children with <code>setdefault</code>, and set <code>is_end</code> on the last node.",
                    "<code>_walk(s)</code>: follow <code>children.get(ch)</code> for each character, returning <code>None</code> if the path breaks.",
                    "<code>search</code>: the walk must succeed <em>and</em> stop on a node with <code>is_end</code>.",
                    "<code>startsWith</code>: the walk only needs to succeed.",
                ],
                "why": [
                    "The path for a string exists exactly when some inserted word has that string as a prefix.",
                    "The <code>is_end</code> flag is what tells \"app\" was inserted apart from \"app\" merely being a prefix of \"apple\".",
                    "Every operation touches one node per character: O(L), no matter how many words are stored. Shared prefixes are stored once.",
                ],
                "dry": [
                    "Inserting \"apple\" creates the path a→p→p→l→e and marks e as an end.",
                    "Inserting \"app\" reuses a→p→p and marks that second p as an end, with no new nodes.",
                    "Inserting \"bat\" creates b→a→t from the root and marks t.",
                    "<code>search(\"app\")</code>: the walk reaches the second p, which is marked, so <strong>True</strong>.",
                    "<code>search(\"ap\")</code>: the walk reaches the first p, which is not marked, so <strong>False</strong>. <code>startsWith(\"ap\")</code>: the path exists, so <strong>True</strong>.",
                    "<code>search(\"bat\")</code> gives <strong>True</strong> and <code>startsWith(\"ba\")</code> gives <strong>True</strong>.",
                    "<code>startsWith(\"c\")</code>: the root has no c child, so <strong>False</strong>.",
                ],
            },
            "Fixed array of 26 children": {
                "idea": [
                    "Same trie, but each node's children live in a list of 26 slots indexed by <code>ord(ch) - 97</code> instead of a dictionary.",
                    "Nodes are numbered, and two parallel lists hold every node's child slots and its end flag.",
                    "In compiled languages direct indexing beats hashing; the price is 26 slots per node even when most are empty.",
                ],
                "steps": [
                    "Node 0 is the root: <code>children = [[None] * 26]</code>, <code>is_end = [False]</code>.",
                    "<code>_child(node, ch, create)</code>: read the slot; if it is empty and <code>create</code> is set, append a new node and link it.",
                    "<code>insert</code> walks with <code>create=True</code> and sets <code>is_end</code> at the end.",
                    "<code>search</code> and <code>startsWith</code> walk with <code>create=False</code>, exactly like the dictionary version.",
                ],
                "why": [
                    "It has the same structure and invariants as the dictionary trie, only stored differently.",
                    "Operations are O(L) and space is O(26 · nodes). In Python the dictionary version is usually just as fast and smaller.",
                ],
                "dry": [
                    "\"apple\" creates nodes 1 (a), 2 (p), 3 (p), 4 (l), 5 (e); <code>is_end[5] = True</code>.",
                    "\"app\" walks 0→1→2→3 without creating anything; <code>is_end[3] = True</code>.",
                    "\"bat\" creates nodes 6 (b), 7 (a), 8 (t); <code>is_end[8] = True</code>.",
                    "<code>search(\"app\")</code> ends at node 3, which is marked: <strong>True</strong>. <code>search(\"ap\")</code> ends at node 2, unmarked: <strong>False</strong>.",
                    "<code>startsWith(\"ap\")</code>: node 2 exists, <strong>True</strong>. <code>search(\"bat\")</code>: node 8 is marked, <strong>True</strong>. <code>startsWith(\"ba\")</code>: node 7 exists, <strong>True</strong>.",
                    "<code>startsWith(\"c\")</code>: slot 2 of node 0 is <code>None</code>, so <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add and search words
    "add-search-words": {
        "example": {"setup": 'wd = WordDictionary()\nfor w in ("bad", "dad", "mad", "be"):\n    wd.addWord(w)',
                    "call": '[wd.search(p) for p in ("pad", "bad", ".ad", "b..", "b.", ".e.")]',
                    "expect": "[False, True, True, True, True, False]"},
        "approaches": {
            "List of words, match each": {
                "idea": [
                    "A pattern can only match a word of the same length, so group stored words by length.",
                    "Then compare the pattern with each candidate letter by letter, letting <code>.</code> match anything.",
                ],
                "steps": [
                    "<code>addWord</code>: append the word to <code>by_len[len(word)]</code>.",
                    "<code>search</code>: for each word of the right length, check that every position is a <code>.</code> or the same letter.",
                    "Return <code>True</code> as soon as one word matches.",
                ],
                "why": [
                    "The per-letter rule is exactly the problem's definition of a match.",
                    "A search can compare against every same-length word: O(n·L) per query. Space is the total stored characters.",
                ],
                "dry": [
                    "by_len = {3: [bad, dad, mad], 2: [be]}.",
                    "\"pad\": p differs from b, d and m in the first letter, so <strong>False</strong>.",
                    "\"bad\": matches \"bad\", <strong>True</strong>. \".ad\": the dot matches b and \"ad\" matches, <strong>True</strong>.",
                    "\"b..\": \"bad\" fits, <strong>True</strong>. \"b.\": the only length-2 word \"be\" fits, <strong>True</strong>.",
                    "\".e.\": every length-3 word has <code>a</code> in the middle, so <strong>False</strong>.",
                ],
            },
            "Trie with DFS on wildcards": {
                "idea": [
                    "Store the words in a trie made of nested dictionaries, with <code>\"$\"</code> marking a word end.",
                    "A normal letter follows exactly one child. A dot could be any letter, so it tries <em>every</em> child and succeeds if any branch does.",
                    "Branches die as soon as the trie has no matching child, so even dotted searches usually touch few nodes.",
                ],
                "steps": [
                    "<code>addWord</code>: walk with <code>setdefault(ch, {})</code> and set <code>node[\"$\"] = True</code>.",
                    "<code>dfs(node, i)</code>: at the end of the pattern, return whether <code>\"$\"</code> is in the node.",
                    "If <code>word[i]</code> is a dot, return <code>any(dfs(child, i + 1))</code> over all real children (skipping <code>\"$\"</code>).",
                    "Otherwise follow <code>node[ch]</code> if it exists.",
                ],
                "why": [
                    "Each root-to-node path spells a prefix of a stored word, so the search explores exactly the words consistent with the pattern so far.",
                    "Without dots a search is an O(L) walk; each dot can fan out to at most 26 children (O(26^d · L) worst case), and LeetCode limits a query to 2 dots.",
                ],
                "dry": [
                    "The trie's root has children b (with a→d$ and e$), d (a→d$) and m (a→d$).",
                    "\"pad\": the root has no p, so <strong>False</strong>. \"bad\": b→a→d reaches <code>$</code>, <strong>True</strong>.",
                    "\".ad\": the dot tries b first; b→a→d has <code>$</code>, so <code>any</code> stops: <strong>True</strong>.",
                    "\"b..\": from b, the first dot tries a, the second dot tries d, the pattern ends and <code>$</code> is there: <strong>True</strong>.",
                    "\"b.\": from b, the dot tries a, but a is not a word end; it then tries e, which is: <strong>True</strong>.",
                    "\".e.\": none of b, d, m leads on to an e child, so <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ extra characters
    "extra-characters-string": {
        "example": {"call": 'min_extra_char("leetscode", ["leet", "code", "leetcode"])', "expect": "1"},
        "approaches": {
            "Plain recursion": {
                "idea": [
                    "Think about the suffix starting at i: either character i is wasted (it costs 1), or some dictionary word starts exactly at i.",
                    "If a word <code>s[i:j]</code> starts there, use it for free and solve the rest from j.",
                    "<code>best(i)</code> is the minimum of all those choices.",
                ],
                "steps": [
                    "<code>best(len(s)) = 0</code>, since an empty suffix has no extras.",
                    "Start with skipping: <code>1 + best(i + 1)</code>.",
                    "For every j with <code>s[i:j]</code> in the word set, try <code>best(j)</code>.",
                    "Return <code>best(0)</code>.",
                ],
                "why": [
                    "Every way to split a suffix starts with either a skipped character or a word, so the choices cover all splits.",
                    "Without caching, the same suffix is solved again and again: exponential time, with O(n) recursion depth.",
                ],
                "dry": [
                    "<code>best(0)</code>: skipping 'l' leads to <code>1 + best(1)</code>; the word \"leet\" = s[0:4] leads to <code>best(4)</code>.",
                    "<code>best(4)</code>: no word starts with 's', so <code>1 + best(5)</code>.",
                    "<code>best(5)</code>: \"code\" = s[5:9] leads to <code>best(9) = 0</code>, so best(5) = 0.",
                    "So best(4) = 1, and best(0) = min(1 + best(1), 1) = <strong>1</strong>, since the skip route costs at least 1.",
                    "The one extra character is the 's'. \"leetcode\" never matches, because of that 's'.",
                ],
            },
            "DP with a hash set of words": {
                "idea": [
                    "Same recurrence, solved bottom-up: <code>dp[i]</code> is the fewest extra characters in <code>s[i:]</code>.",
                    "Fill it from the end, so <code>dp[j]</code> for every <code>j &gt; i</code> is ready when computing <code>dp[i]</code>.",
                ],
                "steps": [
                    "<code>dp[n] = 0</code>.",
                    "For <code>i</code> from n - 1 down to 0: <code>dp[i] = 1 + dp[i + 1]</code> (skip <code>s[i]</code>).",
                    "For every end <code>j</code>, if <code>s[i:j]</code> is a word, <code>dp[i] = min(dp[i], dp[j])</code>.",
                    "Return <code>dp[0]</code>.",
                ],
                "why": [
                    "Each suffix is solved once.",
                    "There are O(n²) pairs (i, j), and building and hashing <code>s[i:j]</code> costs O(j - i), so O(n³) overall. That is fine for n ≤ 50.",
                ],
                "dry": [
                    "Base: dp[9] = 0. Right to left, 'e', 'd', 'o' start no word: dp[8] = 1, dp[7] = 2, dp[6] = 3.",
                    "i=5 ('c'): skipping gives 4, but \"code\" = s[5:9] gives dp[9] = 0, so dp[5] = 0.",
                    "i=4 ('s'): no word, dp[4] = 1 + 0 = 1.",
                    "i=3, 2, 1: dp = 2, 3, 4 (only skipping).",
                    "i=0: skipping gives 5, but \"leet\" = s[0:4] gives dp[4] = 1, so dp[0] = <strong>1</strong>.",
                ],
            },
            "DP walking a trie from each start": {
                "idea": [
                    "Most substrings <code>s[i:j]</code> are not even prefixes of a word, so building and hashing them is wasted.",
                    "Put the dictionary in a trie and, from each start i, walk the trie along s. Every word-end node met gives a candidate.",
                    "Stop the walk as soon as the trie has no matching child, because no word continues that way.",
                ],
                "steps": [
                    "Build the trie of dictionary words, marking ends with <code>\"$\"</code>.",
                    "For <code>i</code> from n - 1 down: <code>dp[i] = 1 + dp[i + 1]</code>.",
                    "Walk <code>node = node.get(s[j])</code> for j = i, i + 1, ...; break when it is <code>None</code>; at a <code>\"$\"</code> node, try <code>dp[j + 1]</code>.",
                    "Return <code>dp[0]</code>.",
                ],
                "why": [
                    "The walk visits exactly the dictionary words that start at i, without building any substrings.",
                    "Each start walks at most n steps: O(n²), and walks usually die after a few characters.",
                ],
                "dry": [
                    "The trie holds l→e→e→t($)→c→o→d→e($) and c→o→d→e($).",
                    "i=8, 7, 6: the walks die at once ('e', 'd', 'o' are not root children), so dp = 1, 2, 3.",
                    "i=5: the walk c→o→d→e reaches <code>$</code> at j=8, so dp[5] = min(4, dp[9] = 0) = 0.",
                    "i=4: 's' is not a root child, so the walk breaks immediately: dp[4] = 1.",
                    "i=0: the walk l→e→e→t hits <code>$</code> at j=3, so dp[0] = min(5, dp[4] = 1). The next character 's' is not a child of t, so stop.",
                    "The answer is <strong>1</strong>.",
                ],
            },
        },
    },
}
