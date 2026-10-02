# -*- coding: utf-8 -*-
"""Tries topic (NeetCode 250: Tries). Word Search II, the fourth Tries
problem in the list, already lives in the Backtracking topic. Same build
contract as content/dsa.py."""

PRELUDE_TRIE = '''import random
from functools import cache
'''


TRIES_TOPIC = dict(
    id="trie",
    title="Tries",
    prelude=PRELUDE_TRIE,
    sections=[

dict(
    id="tries",
    title="Prefix trees",
    idea=[
        "A trie stores strings character by character along paths from a root, so every string sharing a prefix shares that path. Looking up a word or a prefix costs O(length of the query) no matter how many words are stored &mdash; which is what a hash set cannot offer for prefixes. Word Search II, the fourth trie problem in this list, is in the Backtracking topic.",
    ],
    problems=[

    # ------------------------------------------------------------------ 208
    dict(
        id="implement-trie",
        lc=208, slug="implement-trie-prefix-tree",
        name="Implement Trie (Prefix Tree)",
        difficulty="medium",
        framing=[
            "Implement <code>insert</code>, <code>search</code> (whole word) and <code>startsWith</code> (any word with this prefix). The distinction between the last two is the <em>end-of-word marker</em>: \"app\" is a prefix of \"apple\" but is only a word if it was inserted.",
        ],
        approaches=[
            dict(
                name="Hash set of words, scan for prefixes",
                time="insert/search O(L), startsWith O(n &middot; L)",
                space="O(total characters)",
                why=[
                    "A set answers <code>search</code> in O(L). <code>startsWith</code> has to check every stored word, O(n &middot; L). Storing every prefix of every word in a second set would make it O(L) at O(L&sup2;) memory per word. This is the baseline a trie improves on.",
                ],
                code='''class Trie:
    def __init__(self):
        self.words = set()

    def insert(self, word):
        self.words.add(word)

    def search(self, word):
        return word in self.words

    def startsWith(self, prefix):
        return any(w.startswith(prefix) for w in self.words)''',
            ),
            dict(
                name="Node class with a children dict",
                time="O(L) per operation",
                space="O(total characters)",
                best=True,
                why=[
                    "Each node maps a character to a child node and has an <code>is_end</code> flag. Insert walks the word, creating missing children, and marks the last node. Search and startsWith walk the same way; search additionally requires <code>is_end</code>.",
                    "Every operation touches one node per character: O(L), independent of how many words are stored. Shared prefixes are stored once.",
                ],
                code='''class TrieNode:
    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix):
        return self._walk(prefix) is not None''',
            ),
            dict(
                name="Fixed array of 26 children",
                time="O(L) per operation",
                space="O(26 &middot; nodes)",
                tag="C-style",
                why=[
                    "Replace the dict with a list of 26 slots indexed by <code>ord(ch) - 97</code>. Lookups are plain indexing, which is faster in compiled languages, but every node pays for 26 slots even if it has one child. In Python, the dict version is usually both smaller and just as fast.",
                ],
                code='''class Trie:
    def __init__(self):
        self.children = [[None] * 26]     # node id -> child ids
        self.is_end = [False]

    def _child(self, node, ch, create):
        i = ord(ch) - 97
        nxt = self.children[node][i]
        if nxt is None and create:
            nxt = len(self.children)
            self.children.append([None] * 26)
            self.is_end.append(False)
            self.children[node][i] = nxt
        return nxt

    def insert(self, word):
        node = 0
        for ch in word:
            node = self._child(node, ch, True)
        self.is_end[node] = True

    def _walk(self, s):
        node = 0
        for ch in s:
            node = self._child(node, ch, False)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and self.is_end[node]

    def startsWith(self, prefix):
        return self._walk(prefix) is not None''',
            ),
        ],
        tests='''t = Trie()
t.insert("apple")
assert t.search("apple") is True and t.search("app") is False and t.startsWith("app") is True
t.insert("app")
assert t.search("app") is True
rng = random.Random(0)
t, words = Trie(), set()
for _ in range(300):
    w = "".join(rng.choice("abc") for _ in range(rng.randint(1, 5)))
    if rng.random() < 0.4:
        t.insert(w); words.add(w)
    else:
        assert t.search(w) == (w in words)
        assert t.startsWith(w) == any(x.startswith(w) for x in words)''',
    ),

    # ------------------------------------------------------------------ 211
    dict(
        id="add-search-words",
        lc=211, slug="design-add-and-search-words-data-structure",
        name="Design Add and Search Words Data Structure",
        difficulty="medium",
        framing=[
            "Like a trie, but <code>search</code> patterns may contain <code>.</code>, which matches any single letter. A dot turns one path into up to 26, so search becomes a DFS through the trie &mdash; still far cheaper than matching the pattern against every stored word.",
        ],
        approaches=[
            dict(
                name="List of words, match each",
                time="search O(n &middot; L)",
                space="O(total characters)",
                why=[
                    "Store words; for a query, compare it against every word of the same length, letting <code>.</code> match anything. Grouping words by length helps, but it stays linear in the number of words.",
                ],
                code='''class WordDictionary:
    def __init__(self):
        self.by_len = {}

    def addWord(self, word):
        self.by_len.setdefault(len(word), []).append(word)

    def search(self, word):
        return any(all(p == "." or p == c for p, c in zip(word, w))
                   for w in self.by_len.get(len(word), []))''',
            ),
            dict(
                name="Trie with DFS on wildcards",
                time="O(L) without dots, O(26<sup>d</sup> &middot; L) with d dots",
                space="O(total characters)",
                best=True,
                why=[
                    "Store words in a trie. Search walks the pattern: a letter follows one child; a dot tries every child and succeeds if any branch does. At the end of the pattern, the node must be the end of a word.",
                    "With no dots this is a plain O(L) trie lookup. Each dot multiplies the branching by at most 26, but branches die as soon as the trie has no matching child, so real searches touch few nodes. The constraints cap dots at 2 per query.",
                ],
                code='''class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True                         # end-of-word marker

    def search(self, word):
        def dfs(node, i):
            if i == len(word):
                return "$" in node
            ch = word[i]
            if ch == ".":
                return any(dfs(child, i + 1) for key, child in node.items() if key != "$")
            return ch in node and dfs(node[ch], i + 1)

        return dfs(self.root, 0)''',
            ),
        ],
        tests='''wd = WordDictionary()
for w in ("bad", "dad", "mad"):
    wd.addWord(w)
assert [wd.search(p) for p in ("pad", "bad", ".ad", "b..")] == [False, True, True, True]
assert wd.search("b.") is False and wd.search("...") is True and wd.search("....") is False
rng = random.Random(1)
wd, words = WordDictionary(), []
for _ in range(300):
    w = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
    if rng.random() < 0.4:
        wd.addWord(w); words.append(w)
    else:
        p = "".join(c if rng.random() < 0.6 else "." for c in w)
        expect = any(len(x) == len(p) and all(a == "." or a == b for a, b in zip(p, x)) for x in words)
        assert wd.search(p) is expect''',
    ),

    # ------------------------------------------------------------------ 2707
    dict(
        id="extra-characters-string",
        lc=2707, slug="extra-characters-in-a-string",
        name="Extra Characters in a String",
        difficulty="medium",
        framing=[
            "Split <code>s</code> into dictionary words, leaving some characters unused; minimise the unused ones. A DP over positions: at each index, either skip the character (cost 1) or jump past a dictionary word starting here. The trie makes \"which words start here?\" cheap.",
        ],
        approaches=[
            dict(
                name="Plain recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "<code>best(i)</code> = minimum extras for <code>s[i:]</code>: skip <code>s[i]</code> (1 + best(i + 1)) or, for every dictionary word starting at i, best(i + len). Without caching, the same suffixes are solved exponentially many times.",
                ],
                code='''def min_extra_char(s, dictionary):
    words = set(dictionary)

    def best(i):
        if i == len(s):
            return 0
        result = 1 + best(i + 1)
        for j in range(i + 1, len(s) + 1):
            if s[i:j] in words:
                result = min(result, best(j))
        return result

    return best(0)''',
            ),
            dict(
                name="DP with a hash set of words",
                time="O(n&sup3;)",
                space="O(n + total characters)",
                why=[
                    "Fill <code>dp[i]</code> from the end. For each i, try every end j and check <code>s[i:j]</code> in the set. The slice and its hash cost O(j - i), so the total is O(n&sup3;) &mdash; fine for n &le; 50, but the substring work is wasted when no word even starts with <code>s[i]</code>.",
                ],
                code='''def min_extra_char(s, dictionary):
    words, n = set(dictionary), len(s)
    dp = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        dp[i] = 1 + dp[i + 1]
        for j in range(i + 1, n + 1):
            if s[i:j] in words:
                dp[i] = min(dp[i], dp[j])
    return dp[0]''',
            ),
            dict(
                name="DP walking a trie from each start",
                time="O(n&sup2;)",
                space="O(n + total characters)",
                best=True,
                why=[
                    "Build a trie of the dictionary. From each start i, walk the trie along <code>s[i], s[i+1], &hellip;</code>; every node marked as a word end gives a candidate jump, and the walk stops as soon as the trie has no matching child. No substrings are built or hashed.",
                    "At most n steps per start: O(n&sup2;), and usually far fewer because most walks die within a few characters.",
                ],
                code='''def min_extra_char(s, dictionary):
    root = {}
    for w in dictionary:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = True
    n = len(s)
    dp = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        dp[i] = 1 + dp[i + 1]
        node = root
        for j in range(i, n):
            node = node.get(s[j])
            if node is None:
                break                            # no word continues this way
            if "$" in node:
                dp[i] = min(dp[i], dp[j + 1])
    return dp[0]''',
            ),
        ],
        tests='''assert min_extra_char("leetscode", ["leet", "code", "leetcode"]) == 1
assert min_extra_char("sayhelloworld", ["hello", "world"]) == 3
assert min_extra_char("abc", []) == 3
rng = random.Random(2)
for _ in range(40):
    s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 10)))
    d = list({"".join(rng.choice("ab") for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(0, 4))})
    n = len(s)
    dp = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        dp[i] = 1 + dp[i + 1]
        for j in range(i + 1, n + 1):
            if s[i:j] in d:
                dp[i] = min(dp[i], dp[j])
    assert min_extra_char(s, d) == dp[0]''',
    ),
    ],
),
    ],
)
