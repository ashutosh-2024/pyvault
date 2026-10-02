# -*- coding: utf-8 -*-
"""Backtracking topic for the DSA path.

Same contract as content/dsa.py: every `code` block is executed by build.py
with PRELUDE + this topic's `prelude` + the problem's `tests` appended. Tests
compare against itertools or a brute force wherever one is cheap, because the
point of a backtracking solution is that it produces *exactly* the right set.

Problems appear in the order they were requested. Premium problems supply
their own statement, since LeetCode returns no content for them.
"""

PRELUDE_BT = '''import itertools
import random
from collections import Counter, defaultdict
from functools import cache


def as_set(lists):
    """Order-insensitive view of a list of lists, for comparing outputs."""
    return sorted(tuple(x) for x in lists)
'''


BACKTRACKING_TOPIC = dict(
    id="backtracking",
    title="Backtracking",
    prelude=PRELUDE_BT,
    sections=[

# ---------------------------------------------------------------- 1
dict(
    id="choose-explore-unchoose",
    title="Subsets, combinations and permutations",
    idea=[
        "Every backtracking solution is the same loop: choose an option, explore everything that follows from it, un-choose it, try the next option. The problems differ in what the options are, when a partial answer is complete, and which branches can be cut early.",
    ],
    problems=[

    dict(
        id="synonymous-sentences",
        lc=1258, slug="synonymous-sentences",
        name="Synonymous Sentences",
        difficulty="medium",
        tags=["Array", "Hash Table", "String", "Backtracking", "Union Find"],
        statement=[
            "You are given a list of equivalent word pairs <code>synonyms</code>, where <code>synonyms[i] = [s<sub>i</sub>, t<sub>i</sub>]</code> means the two words are synonyms, and a sentence <code>text</code>. Synonymy is transitive: if a~b and b~c, then a~c.",
            "Return <strong>all</strong> sentences that can be produced by replacing any words of <code>text</code> with their synonyms, sorted lexicographically.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input='synonyms = [["happy","joy"],["sad","sorrow"],["joy","cheerful"]], text = "I am happy today but was sad yesterday"',
                 output='["I am cheerful today but was sad yesterday", "I am cheerful today but was sorrow yesterday", "I am happy today but was sad yesterday", "I am happy today but was sorrow yesterday", "I am joy today but was sad yesterday", "I am joy today but was sorrow yesterday"]',
                 explanation="happy, joy and cheerful form one group; sad and sorrow another. 3 &times; 2 = 6 sentences."),
        ],
        constraints=[
            "<code>0 &lt;= synonyms.length &lt;= 10</code>",
            "Words consist of English letters; <code>text</code> has at most 10 words separated by single spaces",
        ],
        approaches=[
            dict(
                name="Union-find groups, then backtrack word by word",
                time="O(n + S &middot; L)",
                space="O(n + L)",
                best=True,
                why=[
                    "Transitivity is the first half of the problem: happy~joy and joy~cheerful put all three in one group. Union-find (or a BFS over the synonym graph) builds the groups in near-linear time.",
                    "The second half is a textbook backtrack. Position <code>i</code> of the sentence offers the options in its word's group (or just the word itself); choose one, recurse on <code>i + 1</code>, un-choose. S sentences of length L come out, which is the size of the answer and therefore a lower bound.",
                    "Sorting each group once also sorts the output: sentences are compared word by word, and a space sorts before any letter, so choosing options in sorted order emits sentences in sorted order &mdash; no final sort needed.",
                ],
                code='''def generate_sentences(synonyms, text):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]        # path halving
            x = parent[x]
        return x

    for a, b in synonyms:
        parent[find(a)] = find(b)
    groups = defaultdict(list)
    for w in parent:
        groups[find(w)].append(w)
    for g in groups.values():
        g.sort()

    words, out, path = text.split(), [], []

    def dfs(i):
        if i == len(words):
            out.append(" ".join(path))
            return
        w = words[i]
        for option in (groups[find(w)] if w in parent else [w]):
            path.append(option)                  # choose
            dfs(i + 1)                           # explore
            path.pop()                           # un-choose

    dfs(0)
    return out''',
            ),
            dict(
                name="BFS over whole sentences",
                time="O(S &middot; L &middot; P)",
                space="O(S &middot; L)",
                tag="no union-find",
                why=[
                    "Start from <code>text</code>; from each sentence, produce every sentence that differs by one direct synonym swap, and keep a seen-set. Transitivity is handled by the BFS itself. Correct, but every sentence is generated once per neighbour and stored in full, so it does P times more work (P = number of pairs) and keeps all S sentences in memory.",
                ],
                code='''def generate_sentences(synonyms, text):
    graph = defaultdict(set)
    for a, b in synonyms:
        graph[a].add(b)
        graph[b].add(a)
    seen, queue = {text}, deque([text])
    while queue:
        words = queue.popleft().split()
        for i, w in enumerate(words):
            for alt in graph[w]:
                nxt = " ".join(words[:i] + [alt] + words[i + 1:])
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return sorted(seen)''',
            ),
        ],
        tests='''syn = [["happy", "joy"], ["sad", "sorrow"], ["joy", "cheerful"]]
assert generate_sentences(syn, "I am happy today but was sad yesterday") == [
    "I am cheerful today but was sad yesterday", "I am cheerful today but was sorrow yesterday",
    "I am happy today but was sad yesterday", "I am happy today but was sorrow yesterday",
    "I am joy today but was sad yesterday", "I am joy today but was sorrow yesterday"]
assert generate_sentences([["happy", "joy"], ["cheerful", "glad"]], "I am happy today but was sad yesterday") == [
    "I am happy today but was sad yesterday", "I am joy today but was sad yesterday"]
assert generate_sentences([], "hello world") == ["hello world"]
assert generate_sentences([["a", "ab"]], "a a") == ["a a", "a ab", "ab a", "ab ab"]''',
    ),

    dict(
        id="subset-xor-totals",
        lc=1863, slug="sum-of-all-subset-xor-totals",
        name="Sum of All Subset XOR Totals",
        difficulty="easy",
        framing=[
            "Sum the XOR of every subset. The warm-up for this whole page: each element is either in or out, so the subsets are the leaves of a binary decision tree of depth n.",
        ],
        approaches=[
            dict(
                name="Include / exclude recursion",
                time="O(2<sup>n</sup>)",
                space="O(n)",
                why=[
                    "At index <code>i</code>, branch twice: XOR the element in, or leave it out. At the end of the array one subset is complete; return its XOR. Every subset is visited exactly once, and nothing is copied because the running XOR is a single integer.",
                    "This is the shape to be able to write in your sleep. The include/exclude tree is the skeleton of Subsets, Combination Sum and every partition problem further down.",
                ],
                code='''def subset_xor_sum(nums):
    def dfs(i, acc):
        if i == len(nums):
            return acc
        return dfs(i + 1, acc ^ nums[i]) + dfs(i + 1, acc)   # take it, or not

    return dfs(0, 0)''',
            ),
            dict(
                name="Bit contribution: OR &times; 2<sup>n-1</sup>",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Look at one bit position. If no element has that bit, no subset's XOR does. If at least one does, fix one such element <code>x</code>: pairing every subset with the same subset toggled on <code>x</code> flips that bit, so exactly half of the 2<sup>n</sup> subsets have it set.",
                    "Each bit present anywhere therefore contributes <code>2<sup>bit</sup> &middot; 2<sup>n-1</sup></code>, and the total is <code>(OR of all) &lt;&lt; (n - 1)</code>. A good interview moment: enumerate first to show you can, then notice the structure.",
                ],
                code='''from functools import reduce
from operator import or_


def subset_xor_sum(nums):
    return reduce(or_, nums, 0) << (len(nums) - 1)''',
            ),
        ],
        tests='''assert subset_xor_sum([1, 3]) == 6
assert subset_xor_sum([5, 1, 6]) == 28
assert subset_xor_sum([3, 4, 5, 6, 7, 8]) == 480
rng = random.Random(0)
for _ in range(30):
    nums = [rng.randint(1, 20) for _ in range(rng.randint(1, 8))]
    brute = 0
    for r in range(len(nums) + 1):
        for combo in itertools.combinations(nums, r):
            x = 0
            for v in combo:
                x ^= v
            brute += x
    assert subset_xor_sum(nums) == brute''',
    ),

    dict(
        id="subsets",
        lc=78, slug="subsets",
        name="Subsets",
        difficulty="medium",
        framing=[
            "Return all 2<sup>n</sup> subsets of distinct integers. Three ways to enumerate them, each worth knowing: a backtracking loop, iterative doubling, and bitmasks.",
        ],
        approaches=[
            dict(
                name="Backtracking with a start index",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(n)",
                best=True,
                why=[
                    "Every node of the recursion is a subset, not just the leaves: record <code>path</code> on entry, then try adding each element after the last one used. The start index is what stops <code>[1, 2]</code> and <code>[2, 1]</code> both appearing &mdash; elements are only ever added in increasing index order.",
                    "2<sup>n</sup> subsets, each copied in O(n): O(n &middot; 2<sup>n</sup>), which is the output size. Auxiliary space is the path and the recursion, O(n).",
                ],
                code='''def subsets(nums):
    out, path = [], []

    def dfs(start):
        out.append(path[:])                   # every node is an answer
        for i in range(start, len(nums)):
            path.append(nums[i])
            dfs(i + 1)                        # only later elements from here on
            path.pop()

    dfs(0)
    return out''',
            ),
            dict(
                name="Iterative doubling",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(1) beyond output",
                why=[
                    "Start with <code>[[]]</code>. For each new element, every existing subset either takes it or does not &mdash; so append a copy of each existing subset with the element added. The list doubles each step.",
                ],
                code='''def subsets(nums):
    out = [[]]
    for x in nums:
        out += [s + [x] for s in out]
    return out''',
            ),
            dict(
                name="Bitmasks",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(1) beyond output",
                why=[
                    "The integers <code>0 .. 2<sup>n</sup> - 1</code> are exactly the subsets: bit <code>i</code> of the mask says whether <code>nums[i]</code> is in. No recursion at all, and a mask is a handy key when a later problem needs to memoise on \"which elements are used\".",
                ],
                code='''def subsets(nums):
    n = len(nums)
    return [[nums[i] for i in range(n) if mask >> i & 1] for mask in range(1 << n)]''',
            ),
        ],
        tests='''assert as_set(subsets([1, 2, 3])) == as_set([[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]])
assert as_set(subsets([0])) == as_set([[], [0]])
nums = list(range(8))
got = subsets(nums)
assert len(got) == 256 and len(set(map(tuple, got))) == 256''',
    ),

    dict(
        id="combination-sum",
        lc=39, slug="combination-sum",
        name="Combination Sum",
        difficulty="medium",
        framing=[
            "Distinct candidates, each usable <strong>any number of times</strong>. Return every combination summing to the target. Two changes to the Subsets loop: recurse with the <em>same</em> index (reuse allowed), and stop as soon as the remainder goes negative.",
        ],
        approaches=[
            dict(
                name="Sorted candidates, recurse on the same index, break early",
                time="O(N<sup>T/m + 1</sup>)",
                space="O(T/m)",
                best=True,
                why=[
                    "Recursing on <code>i</code> rather than <code>i + 1</code> lets a candidate be taken again, while still never going back to an earlier one &mdash; so each multiset is produced once, in non-decreasing order.",
                    "Sorting turns the bound check into a <code>break</code>: once one candidate overshoots, every later one does too. That pruning is where nearly all the speed comes from in practice.",
                    "The worst case is loose: with N candidates, target T and smallest candidate m, the tree is at most T/m deep with N branches per level. The recursion depth, and so the auxiliary space, is at most T/m.",
                ],
                code='''def combination_sum(candidates, target):
    candidates = sorted(candidates)
    out, path = [], []

    def dfs(start, remaining):
        if remaining == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                          # sorted: everything after is bigger
            path.append(c)
            dfs(i, remaining - c)              # i, not i + 1: reuse allowed
            path.pop()

    dfs(0, target)
    return out''',
            ),
            dict(
                name="DP table of combinations per amount",
                time="O(N &middot; T &middot; K)",
                space="O(T &middot; K)",
                tag="bottom-up",
                why=[
                    "The unbounded-knapsack loop, storing lists instead of counts: for each candidate in order, <code>ways[a] += [combo + [c] for combo in ways[a - c]]</code>. Iterating candidates in the outer loop keeps combinations in non-decreasing order, so no duplicates appear.",
                    "It stores every partial combination for every amount (K = combinations per amount), which is far more memory than the backtracking path. It shows the link to DP; backtracking is the better answer here.",
                ],
                code='''def combination_sum(candidates, target):
    ways = [[] for _ in range(target + 1)]
    ways[0] = [[]]
    for c in sorted(candidates):
        for amount in range(c, target + 1):
            ways[amount] += [combo + [c] for combo in ways[amount - c]]
    return ways[target]''',
            ),
        ],
        tests='''assert as_set(combination_sum([2, 3, 6, 7], 7)) == as_set([[2, 2, 3], [7]])
assert as_set(combination_sum([2, 3, 5], 8)) == as_set([[2, 2, 2, 2], [2, 3, 3], [3, 5]])
assert combination_sum([2], 1) == []
got = combination_sum([2, 3, 5, 7], 20)
assert all(sum(c) == 20 for c in got) and len(set(map(tuple, map(sorted, got)))) == len(got)''',
    ),

    dict(
        id="combination-sum-ii",
        lc=40, slug="combination-sum-ii",
        name="Combination Sum II",
        difficulty="medium",
        framing=[
            "Now the candidates may contain <strong>duplicates</strong> and each may be used <strong>at most once</strong>, but the answer must not repeat a combination. This introduces the single most important backtracking trick: skipping equal values <em>at the same depth</em>.",
        ],
        pitfall="Skipping every repeated value, or deduplicating with a set of tuples afterwards. The first drops valid answers like <code>[1, 1, 6]</code>; the second is correct but explores every duplicate branch before throwing the results away.",
        approaches=[
            dict(
                name="Sort, then skip equal siblings",
                time="O(2<sup>n</sup> &middot; n)",
                space="O(n)",
                best=True,
                why=[
                    "After sorting, equal values are adjacent. At one level of the recursion, the loop chooses <em>which value comes next</em>. Choosing the second <code>1</code> after the first has already been tried at this level would rebuild exactly the same combinations, so skip it: <code>if i &gt; start and c[i] == c[i-1]: continue</code>.",
                    "The <code>i &gt; start</code> part is the subtle bit. The first 1 may still be followed by the second 1 one level <em>deeper</em> &mdash; that is how <code>[1, 1, 6]</code> is produced. Only siblings are skipped, never a value that extends the path.",
                    "Recurse with <code>i + 1</code> since each element is used once. At most 2<sup>n</sup> combinations of length up to n.",
                ],
                code='''def combination_sum2(candidates, target):
    c = sorted(candidates)
    out, path = [], []

    def dfs(start, remaining):
        if remaining == 0:
            out.append(path[:])
            return
        for i in range(start, len(c)):
            if i > start and c[i] == c[i - 1]:
                continue                       # same value, same depth: already tried
            if c[i] > remaining:
                break
            path.append(c[i])
            dfs(i + 1, remaining - c[i])       # each element at most once
            path.pop()

    dfs(0, target)
    return out''',
            ),
        ],
        tests='''assert as_set(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)) == as_set([[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]])
assert as_set(combination_sum2([2, 5, 2, 1, 2], 5)) == as_set([[1, 2, 2], [5]])
rng = random.Random(1)
for _ in range(30):
    nums = [rng.randint(1, 6) for _ in range(rng.randint(1, 10))]
    t = rng.randint(1, 15)
    brute = {tuple(sorted(cmb)) for r in range(len(nums) + 1)
             for cmb in itertools.combinations(nums, r) if sum(cmb) == t}
    assert as_set(combination_sum2(nums, t)) == sorted(brute)''',
    ),

    dict(
        id="combinations",
        lc=77, slug="combinations",
        name="Combinations",
        difficulty="medium",
        framing=[
            "All combinations of <code>k</code> numbers from <code>1..n</code>. Subsets with a fixed size &mdash; and a clean place to learn <strong>bound pruning</strong>: stop a branch as soon as there are too few numbers left to finish it.",
        ],
        approaches=[
            dict(
                name="Backtracking with an upper bound on the next choice",
                time="O(k &middot; C(n, k))",
                space="O(k)",
                best=True,
                why=[
                    "With <code>len(path)</code> numbers chosen, <code>k - len(path)</code> are still needed, so the next choice can be at most <code>n - (k - len(path)) + 1</code>. Anything larger leaves too few values to complete the combination and would be a dead branch.",
                    "With that bound no branch ever fails: every path reaches length k. The work is then proportional to the output, C(n, k) combinations of length k.",
                ],
                code='''def combine(n, k):
    out, path = [], []

    def dfs(start):
        if len(path) == k:
            out.append(path[:])
            return
        last = n - (k - len(path)) + 1         # leave room for the rest
        for v in range(start, last + 1):
            path.append(v)
            dfs(v + 1)
            path.pop()

    dfs(1)
    return out''',
            ),
            dict(
                name="itertools.combinations",
                time="O(k &middot; C(n, k))",
                space="O(k)",
                tag="library",
                why=[
                    "The standard library implements exactly this, in C. Mention it; then write the backtracking version, since that is what is being tested.",
                ],
                code='''def combine(n, k):
    return [list(c) for c in itertools.combinations(range(1, n + 1), k)]''',
            ),
        ],
        tests='''assert as_set(combine(4, 2)) == as_set([[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]])
assert combine(1, 1) == [[1]]
for n in range(1, 9):
    for k in range(1, n + 1):
        assert as_set(combine(n, k)) == as_set(itertools.combinations(range(1, n + 1), k))''',
    ),

    dict(
        id="permutations",
        lc=46, slug="permutations",
        name="Permutations",
        difficulty="medium",
        framing=[
            "All orderings of distinct integers. Unlike subsets and combinations, order matters, so there is no start index: every unused element is a candidate at every position.",
        ],
        approaches=[
            dict(
                name="Used flags",
                time="O(n &middot; n!)",
                space="O(n)",
                best=True,
                why=[
                    "Fill positions one at a time; any element not yet on the path may go next. A boolean array marks what is in use and is reset on the way back.",
                    "n! permutations of length n: O(n &middot; n!) is the output size. This version is the one that extends directly to Permutations II below.",
                ],
                code='''def permute(nums):
    out, path, used = [], [], [False] * len(nums)

    def dfs():
        if len(path) == len(nums):
            out.append(path[:])
            return
        for i, x in enumerate(nums):
            if not used[i]:
                used[i] = True
                path.append(x)
                dfs()
                path.pop()
                used[i] = False

    dfs()
    return out''',
            ),
            dict(
                name="Swap into place",
                time="O(n &middot; n!)",
                space="O(n)",
                why=[
                    "Position <code>i</code> is filled by swapping each of <code>nums[i:]</code> into it, recursing on <code>i + 1</code>, and swapping back. The prefix is the permutation built so far and the suffix is the unused pool, so no flags or path list are needed.",
                ],
                code='''def permute(nums):
    nums, out = nums[:], []

    def dfs(i):
        if i == len(nums):
            out.append(nums[:])
            return
        for j in range(i, len(nums)):
            nums[i], nums[j] = nums[j], nums[i]    # choose nums[j] for slot i
            dfs(i + 1)
            nums[i], nums[j] = nums[j], nums[i]    # un-choose

    dfs(0)
    return out''',
            ),
        ],
        tests='''assert as_set(permute([1, 2, 3])) == as_set(itertools.permutations([1, 2, 3]))
assert permute([1]) == [[1]]
got = permute(list(range(6)))
assert len(got) == 720 and as_set(got) == as_set(itertools.permutations(range(6)))''',
    ),

    dict(
        id="subsets-ii",
        lc=90, slug="subsets-ii",
        name="Subsets II",
        difficulty="medium",
        framing=[
            "Subsets of a list that may contain duplicates, without duplicate subsets. Subsets plus the skip-equal-siblings rule from Combination Sum II &mdash; the same one line.",
        ],
        approaches=[
            dict(
                name="Sort, skip equal siblings",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(n)",
                best=True,
                why=[
                    "Sort so duplicates are adjacent. In the loop at one depth, a value equal to its left neighbour has already been tried as the next element, so skip it. A duplicate can still follow its twin one level deeper, which is how <code>[2, 2]</code> appears.",
                ],
                code='''def subsets_with_dup(nums):
    nums = sorted(nums)
    out, path = [], []

    def dfs(start):
        out.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            dfs(i + 1)
            path.pop()

    dfs(0)
    return out''',
            ),
            dict(
                name="Counts per distinct value",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(n)",
                why=[
                    "Group equal values: for a value that occurs c times, a subset contains it 0, 1, &hellip; or c times. Extending every existing subset with each of those counts builds the answer with no duplicates to skip at all.",
                ],
                code='''def subsets_with_dup(nums):
    out = [[]]
    for value, count in sorted(Counter(nums).items()):
        out = [s + [value] * k for s in out for k in range(count + 1)]
    return out''',
            ),
        ],
        tests='''assert as_set(subsets_with_dup([1, 2, 2])) == as_set([[], [1], [1, 2], [1, 2, 2], [2], [2, 2]])
assert as_set(subsets_with_dup([0])) == as_set([[], [0]])
rng = random.Random(2)
for _ in range(30):
    nums = [rng.randint(0, 3) for _ in range(rng.randint(0, 8))]
    brute = {tuple(sorted(c)) for r in range(len(nums) + 1) for c in itertools.combinations(nums, r)}
    got = subsets_with_dup(nums)
    assert len(got) == len(brute) and {tuple(sorted(s)) for s in got} == brute''',
    ),

    dict(
        id="permutations-ii",
        lc=47, slug="permutations-ii",
        name="Permutations II",
        difficulty="medium",
        framing=[
            "Unique permutations of a list with duplicates. The skip rule needs one more condition than for subsets, and getting that condition right is the whole problem.",
        ],
        pitfall="Writing only <code>nums[i] == nums[i-1]</code> as the skip test. That also blocks the second copy when the first is already on the path, so no permutation containing both copies is ever produced.",
        approaches=[
            dict(
                name="Sort, skip a duplicate whose twin is unused",
                time="O(n &middot; n!)",
                space="O(n)",
                best=True,
                why=[
                    "Sort, then insist that equal values are placed in their original left-to-right order: the second <code>1</code> may be placed only after the first one is already on the path. Condition: skip <code>i</code> if <code>nums[i] == nums[i-1]</code> and <code>nums[i-1]</code> is <em>not</em> in use.",
                    "Every multiset permutation then has exactly one way to be built, so nothing is generated twice. The worst case, all values distinct, is the same as Permutations.",
                ],
                code='''def permute_unique(nums):
    nums = sorted(nums)
    out, path, used = [], [], [False] * len(nums)

    def dfs():
        if len(path) == len(nums):
            out.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue                        # equal values go in order
            used[i] = True
            path.append(nums[i])
            dfs()
            path.pop()
            used[i] = False

    dfs()
    return out''',
            ),
            dict(
                name="Choose from a Counter of remaining values",
                time="O(n &middot; P)",
                space="O(n)",
                tag="no skip rule",
                why=[
                    "Loop over <em>distinct</em> values that still have copies left, decrement, recurse, increment. Since the loop never sees the same value twice at one depth, duplicates cannot arise and no skip condition is needed. P is the number of unique permutations.",
                ],
                code='''def permute_unique(nums):
    counts, out, path = Counter(nums), [], []

    def dfs():
        if len(path) == len(nums):
            out.append(path[:])
            return
        for v in list(counts):
            if counts[v]:
                counts[v] -= 1
                path.append(v)
                dfs()
                path.pop()
                counts[v] += 1

    dfs()
    return out''',
            ),
        ],
        tests='''assert as_set(permute_unique([1, 1, 2])) == as_set([[1, 1, 2], [1, 2, 1], [2, 1, 1]])
assert as_set(permute_unique([1, 2, 3])) == as_set(itertools.permutations([1, 2, 3]))
rng = random.Random(3)
for _ in range(25):
    nums = [rng.randint(0, 2) for _ in range(rng.randint(1, 7))]
    got = permute_unique(nums)
    assert len(got) == len(set(itertools.permutations(nums)))
    assert set(map(tuple, got)) == set(itertools.permutations(nums))''',
    ),
    ],
),

# ---------------------------------------------------------------- 2
dict(
    id="constrained-construction",
    title="Building strings and walking grids",
    idea=[
        "Here each choice is a character, a cut, or a step on a grid, and a rule decides whether the partial answer can still become valid. The better the rule, the earlier a dead branch is cut.",
    ],
    problems=[

    dict(
        id="generate-parentheses",
        lc=22, slug="generate-parentheses",
        name="Generate Parentheses",
        difficulty="medium",
        framing=[
            "All well-formed strings of <code>n</code> pairs of parentheses. The generate-everything-then-filter answer works; the backtracking answer never builds an invalid prefix in the first place.",
        ],
        approaches=[
            dict(
                name="Add only what keeps the prefix valid",
                time="O(4<sup>n</sup> / &radic;n)",
                space="O(n)",
                best=True,
                why=[
                    "A prefix can become valid exactly when it has used at most n opening brackets and never more closing than opening ones. So add <code>(</code> while <code>open &lt; n</code>, and <code>)</code> while <code>close &lt; open</code>. Every branch then ends in a valid string.",
                    "The count of answers is the Catalan number C<sub>n</sub> &asymp; 4<sup>n</sup> / (n<sup>1.5</sup>&radic;&pi;), each of length 2n, giving the bound shown.",
                ],
                code='''def generate_parenthesis(n):
    out, path = [], []

    def dfs(open_, close):
        if len(path) == 2 * n:
            out.append("".join(path))
            return
        if open_ < n:
            path.append("(")
            dfs(open_ + 1, close)
            path.pop()
        if close < open_:
            path.append(")")
            dfs(open_, close + 1)
            path.pop()

    dfs(0, 0)
    return out''',
            ),
            dict(
                name="Generate all 2<sup>2n</sup> strings, keep the valid ones",
                time="O(n &middot; 4<sup>n</sup>)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Every string of length 2n over <code>()</code>, checked with a balance counter. Almost all of them are invalid, so it does roughly &radic;n times more work than necessary &mdash; the gap is exactly what pruning buys.",
                ],
                code='''def generate_parenthesis(n):
    def valid(s):
        balance = 0
        for ch in s:
            balance += 1 if ch == "(" else -1
            if balance < 0:
                return False
        return balance == 0

    return [s for s in map("".join, itertools.product("()", repeat=2 * n)) if valid(s)]''',
            ),
        ],
        tests='''assert sorted(generate_parenthesis(3)) == ["((()))", "(()())", "(())()", "()(())", "()()()"]
assert generate_parenthesis(1) == ["()"]
assert [len(generate_parenthesis(n)) for n in range(1, 8)] == [1, 2, 5, 14, 42, 132, 429]''',
    ),

    dict(
        id="word-search",
        lc=79, slug="word-search",
        name="Word Search",
        difficulty="medium",
        framing=[
            "Can <code>word</code> be traced through horizontally or vertically adjacent cells, using each cell at most once? This is backtracking on a grid: mark a cell as used on the way in, unmark it on the way out.",
            "The follow-up asks how to prune. Two cheap checks cut many hopeless searches before they start.",
        ],
        approaches=[
            dict(
                name="DFS with in-place marking and pruning",
                time="O(R &middot; C &middot; 3<sup>L</sup>)",
                space="O(L)",
                best=True,
                why=[
                    "From each cell matching <code>word[0]</code>, try to extend one letter at a time. Overwriting the cell with <code>#</code> while it is on the path is the \"used\" marker, and restoring it afterwards is the un-choose. After the first step there are at most 3 directions that are not going straight back, hence 3<sup>L</sup>.",
                    "Pruning: if the board lacks enough copies of some letter, the answer is <code>False</code> without searching. And if the word's last letter is rarer on the board than its first, search for the <em>reversed</em> word &mdash; fewer starting cells means fewer searches.",
                    "Auxiliary space is the recursion depth, O(L). The board is modified but always restored.",
                ],
                code='''def exist(board, word):
    R, C = len(board), len(board[0])
    have = Counter(ch for row in board for ch in row)
    if any(have[ch] < k for ch, k in Counter(word).items()):
        return False                                   # not enough letters at all
    if have[word[0]] > have[word[-1]]:
        word = word[::-1]                              # start from the rarer end

    def dfs(r, c, i):
        if board[r][c] != word[i]:
            return False
        if i == len(word) - 1:
            return True
        board[r][c] = "#"                              # mark as used
        found = any(0 <= nr < R and 0 <= nc < C and dfs(nr, nc, i + 1)
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)))
        board[r][c] = word[i]                          # restore
        return found

    return any(dfs(r, c, 0) for r in range(R) for c in range(C))''',
            ),
        ],
        tests='''B = lambda: [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
assert exist(B(), "ABCCED") is True
assert exist(B(), "SEE") is True
assert exist(B(), "ABCB") is False
board = B()
exist(board, "ABCCED")
assert board == B()                                    # the board is restored
assert exist([["a"] * 6 for _ in range(6)], "a" * 35 + "b") is False   # letter-count pruning''',
    ),

    dict(
        id="palindrome-partitioning",
        lc=131, slug="palindrome-partitioning",
        name="Palindrome Partitioning",
        difficulty="medium",
        framing=[
            "Split <code>s</code> into pieces that are all palindromes; return every such split. Each choice is <em>where the next cut goes</em>, and a cut is allowed only if the piece before it is a palindrome.",
        ],
        approaches=[
            dict(
                name="Precomputed palindrome table + backtracking",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(n&sup2;)",
                best=True,
                why=[
                    "<code>pal[i][j]</code> says whether <code>s[i..j]</code> is a palindrome. It fills in O(n&sup2;) from the inside out: equal ends and a palindromic middle. Then the backtracking tries every end <code>j</code> for the piece starting at <code>i</code>, with an O(1) check.",
                    "There can be 2<sup>n-1</sup> partitions (a string of one repeated letter), each of total length n, so the output bounds the time.",
                ],
                code='''def partition(s):
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1])

    out, path = [], []

    def dfs(i):
        if i == n:
            out.append(path[:])
            return
        for j in range(i, n):
            if pal[i][j]:
                path.append(s[i:j + 1])
                dfs(j + 1)
                path.pop()

    dfs(0)
    return out''',
            ),
            dict(
                name="Check each piece by slicing",
                time="O(n&sup2; &middot; 2<sup>n</sup>)",
                space="O(n)",
                why=[
                    "Test <code>piece == piece[::-1]</code> on the spot. Simpler, but the same substrings are re-checked in many branches at O(n) each. The table spends O(n&sup2;) memory once to make every check O(1).",
                ],
                code='''def partition(s):
    out, path = [], []

    def dfs(i):
        if i == len(s):
            out.append(path[:])
            return
        for j in range(i + 1, len(s) + 1):
            piece = s[i:j]
            if piece == piece[::-1]:
                path.append(piece)
                dfs(j)
                path.pop()

    dfs(0)
    return out''',
            ),
        ],
        tests='''assert as_set(partition("aab")) == as_set([["a", "a", "b"], ["aa", "b"]])
assert partition("a") == [["a"]]
assert len(partition("aaaa")) == 8
assert all(all(p == p[::-1] for p in parts) and "".join(parts) == "racecar" for parts in partition("racecar"))''',
    ),

    dict(
        id="restore-ip-addresses",
        lc=93, slug="restore-ip-addresses",
        name="Restore IP Addresses",
        difficulty="medium",
        framing=[
            "Insert three dots into a digit string to make every valid IPv4 address: four parts, each 0&ndash;255, with no leading zeros. The search space is tiny, which makes it a good exercise in writing tight pruning conditions correctly.",
        ],
        approaches=[
            dict(
                name="Backtracking with length bounds",
                time="O(1)",
                space="O(1)",
                best=True,
                why=[
                    "Each part is 1&ndash;3 digits, so there are at most 3<sup>4</sup> = 81 ways to cut, whatever the input: constant time. A string longer than 12 digits is rejected immediately.",
                    "Two prunings keep it clean. If the digits left cannot fill the remaining parts (fewer than one each, or more than three each), stop. And a part starting with <code>0</code> must be exactly <code>\"0\"</code>, while a part over 255 cannot be fixed by taking more digits &mdash; both mean <code>break</code>, not <code>continue</code>.",
                ],
                code='''def restore_ip_addresses(s):
    out, parts = [], []

    def dfs(i):
        left = 4 - len(parts)
        if left == 0:
            if i == len(s):
                out.append(".".join(parts))
            return
        if not left <= len(s) - i <= 3 * left:
            return                              # too few or too many digits left
        for size in (1, 2, 3):
            seg = s[i:i + size]
            if len(seg) < size or (size > 1 and seg[0] == "0") or int(seg) > 255:
                break                           # a longer piece cannot fix it
            parts.append(seg)
            dfs(i + size)
            parts.pop()

    dfs(0)
    return out''',
            ),
        ],
        tests='''assert sorted(restore_ip_addresses("25525511135")) == ["255.255.11.135", "255.255.111.35"]
assert restore_ip_addresses("0000") == ["0.0.0.0"]
assert sorted(restore_ip_addresses("101023")) == ["1.0.10.23", "1.0.102.3", "10.1.0.23", "10.10.2.3", "101.0.2.3"]
assert restore_ip_addresses("1111111111111") == []
assert restore_ip_addresses("010010") == ["0.10.0.10", "0.100.1.0"]''',
    ),

    dict(
        id="letter-combinations-phone",
        lc=17, slug="letter-combinations-of-a-phone-number",
        name="Letter Combinations of a Phone Number",
        difficulty="medium",
        framing=[
            "Every string a digit sequence could spell on a phone keypad. There is no pruning here: every branch succeeds. The problem is the Cartesian product of the digits' letter sets, which makes it the purest form of the choose/explore/un-choose loop.",
        ],
        approaches=[
            dict(
                name="Backtracking one digit at a time",
                time="O(n &middot; 4<sup>n</sup>)",
                space="O(n)",
                best=True,
                why=[
                    "Position i chooses one letter of digit i. At most 4 letters per digit (7 and 9), n digits, and each answer is joined in O(n).",
                    "Watch the empty input: the answer is <code>[]</code>, not <code>[\"\"]</code>.",
                ],
                code='''KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def letter_combinations(digits):
    if not digits:
        return []
    out, path = [], []

    def dfs(i):
        if i == len(digits):
            out.append("".join(path))
            return
        for ch in KEYS[digits[i]]:
            path.append(ch)
            dfs(i + 1)
            path.pop()

    dfs(0)
    return out''',
            ),
            dict(
                name="itertools.product",
                time="O(n &middot; 4<sup>n</sup>)",
                space="O(n)",
                tag="library",
                why=["The same product, computed by the standard library."],
                code='''KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def letter_combinations(digits):
    if not digits:
        return []
    return ["".join(p) for p in itertools.product(*(KEYS[d] for d in digits))]''',
            ),
        ],
        tests='''assert sorted(letter_combinations("23")) == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
assert letter_combinations("") == []
assert sorted(letter_combinations("2")) == ["a", "b", "c"]
assert len(letter_combinations("7979")) == 256''',
    ),
    ],
),

# ---------------------------------------------------------------- 3
dict(
    id="buckets",
    title="Partitioning into equal buckets",
    idea=[
        "Assign every item to one of k buckets so that each bucket hits the same target. Without pruning the tree has k<sup>n</sup> leaves; sorting large items first and never trying two equally-filled buckets for the same item cuts it down dramatically.",
    ],
    problems=[

    dict(
        id="matchsticks-to-square",
        lc=473, slug="matchsticks-to-square",
        name="Matchsticks to Square",
        difficulty="medium",
        framing=[
            "Use every matchstick exactly once to form a square. Equivalently: split the lengths into four groups with equal sums. The idea from here carries straight into the next problem with k groups.",
        ],
        approaches=[
            dict(
                name="Fill four sides, longest sticks first",
                time="O(4<sup>n</sup>) worst",
                space="O(n)",
                best=True,
                why=[
                    "Reject early: the total must be divisible by 4 and no stick may exceed a side. Then place sticks one at a time into any side that has room.",
                    "Two prunings do most of the work. Sorting <strong>descending</strong> places the hardest sticks while there are still few options, so failures surface near the root. And if two sides currently have the same length, putting the stick on either leads to the same situation, so try only one of them &mdash; the <code>seen</code> set per call.",
                    "Once every stick is placed with no side overflowing, all four sides must equal the target, because they sum to four targets and none exceeds one.",
                ],
                code='''def makesquare(matchsticks):
    total = sum(matchsticks)
    if len(matchsticks) < 4 or total % 4:
        return False
    side = total // 4
    sticks = sorted(matchsticks, reverse=True)       # hardest first
    if sticks[0] > side:
        return False
    sides = [0] * 4

    def dfs(i):
        if i == len(sticks):
            return True
        tried = set()
        for k in range(4):
            if sides[k] + sticks[i] <= side and sides[k] not in tried:
                tried.add(sides[k])                   # equal sides are interchangeable
                sides[k] += sticks[i]
                if dfs(i + 1):
                    return True
                sides[k] -= sticks[i]
        return False

    return dfs(0)''',
            ),
            dict(
                name="Bitmask DP over used sticks",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(2<sup>n</sup>)",
                tag="guaranteed bound",
                why=[
                    "Fill the sides one after another. For a set of used sticks (a bitmask), what matters is only how full the current side is: <code>(sum of used) mod side</code>. <code>reach[mask]</code> is True if that set can be placed so that every completed side is exact. A stick can be added if it fits in the current side.",
                    "2<sup>n</sup> masks with n transitions each: a hard O(n &middot; 2<sup>n</sup>) regardless of input, which is safer than backtracking on adversarial data but uses 2<sup>n</sup> memory.",
                ],
                code='''def makesquare(matchsticks):
    total, n = sum(matchsticks), len(matchsticks)
    if n < 4 or total % 4:
        return False
    side = total // 4
    fill = [-1] * (1 << n)          # fill of the current side, -1 = unreachable
    fill[0] = 0
    for mask in range(1 << n):
        if fill[mask] < 0:
            continue
        for i in range(n):
            if not mask >> i & 1 and fill[mask] + matchsticks[i] <= side:
                fill[mask | 1 << i] = (fill[mask] + matchsticks[i]) % side
    return fill[-1] == 0''',
            ),
        ],
        tests='''assert makesquare([1, 1, 2, 2, 2]) is True
assert makesquare([3, 3, 3, 3, 4]) is False
assert makesquare([5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3]) is True
assert makesquare([1, 1, 1]) is False
rng = random.Random(4)
for _ in range(40):
    sticks = [rng.randint(1, 6) for _ in range(rng.randint(4, 8))]
    brute = sum(sticks) % 4 == 0 and any(
        all(sum(s for s, g in zip(sticks, assign) if g == k) == sum(sticks) // 4 for k in range(4))
        for assign in itertools.product(range(4), repeat=len(sticks)))
    assert makesquare(sticks) is brute, sticks''',
    ),

    dict(
        id="partition-k-equal-subsets",
        lc=698, slug="partition-to-k-equal-sum-subsets",
        name="Partition to K Equal Sum Subsets",
        difficulty="medium",
        framing=[
            "Matchsticks to Square with k buckets instead of 4 (<code>k &le; 16</code>, <code>n &le; 16</code>). The same two techniques apply: bucket-filling backtracking with symmetry pruning, or DP over bitmasks.",
        ],
        approaches=[
            dict(
                name="Bucket filling with symmetry pruning",
                time="O(k<sup>n</sup>) worst",
                space="O(n + k)",
                best=True,
                why=[
                    "Place numbers largest first into any bucket with room, skipping buckets whose current sum has already been tried for this number. The empty-bucket case is the important special case of that rule: all empty buckets are identical, so a number is tried in at most one of them.",
                    "The worst case stays exponential, but on typical inputs this is very fast because the large numbers fail early.",
                ],
                code='''def can_partition_k_subsets(nums, k):
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    nums = sorted(nums, reverse=True)
    if nums[0] > target:
        return False
    buckets = [0] * k

    def dfs(i):
        if i == len(nums):
            return True
        tried = set()
        for b in range(k):
            if buckets[b] + nums[i] <= target and buckets[b] not in tried:
                tried.add(buckets[b])
                buckets[b] += nums[i]
                if dfs(i + 1):
                    return True
                buckets[b] -= nums[i]
        return False

    return dfs(0)''',
            ),
            dict(
                name="Bitmask DP",
                time="O(n &middot; 2<sup>n</sup>)",
                space="O(2<sup>n</sup>)",
                why=[
                    "Identical to the matchstick DP with <code>target = total / k</code>: for each set of used numbers, record how full the current bucket is. With n &le; 16 that is 65,536 masks &times; 16 transitions &mdash; about a million steps, guaranteed.",
                ],
                code='''def can_partition_k_subsets(nums, k):
    total, n = sum(nums), len(nums)
    if total % k:
        return False
    target = total // k
    fill = [-1] * (1 << n)
    fill[0] = 0
    for mask in range(1 << n):
        if fill[mask] < 0:
            continue
        for i in range(n):
            if not mask >> i & 1 and fill[mask] + nums[i] <= target:
                fill[mask | 1 << i] = (fill[mask] + nums[i]) % target
    return fill[-1] == 0''',
            ),
        ],
        tests='''assert can_partition_k_subsets([4, 3, 2, 3, 5, 2, 1], 4) is True
assert can_partition_k_subsets([1, 2, 3, 4], 3) is False
assert can_partition_k_subsets([2, 2, 2, 2, 3, 4, 5], 4) is False
assert can_partition_k_subsets([1] * 16, 16) is True
rng = random.Random(5)
for _ in range(40):
    nums = [rng.randint(1, 6) for _ in range(rng.randint(2, 7))]
    k = rng.randint(1, 3)
    brute = sum(nums) % k == 0 and any(
        all(sum(v for v, g in zip(nums, assign) if g == b) == sum(nums) // k for b in range(k))
        for assign in itertools.product(range(k), repeat=len(nums)))
    assert can_partition_k_subsets(nums, k) is brute, (nums, k)''',
    ),
    ],
),

# ---------------------------------------------------------------- 4
dict(
    id="premium-classics",
    title="Four premium classics",
    idea=[
        "Factorisations, brace expansion, pattern matching and the Android lock screen: four problems whose search spaces are small enough to enumerate but large enough that the pruning and the state you carry matter.",
    ],
    problems=[

    dict(
        id="factor-combinations",
        lc=254, slug="factor-combinations",
        name="Factor Combinations",
        difficulty="medium",
        tags=["Backtracking"],
        statement=[
            "Numbers can be written as products of their factors; for example, 8 = 2 &times; 2 &times; 2 = 2 &times; 4. Given an integer <code>n</code>, return all possible combinations of its factors, where each factor is in the range <code>[2, n - 1]</code>. Each combination should list its factors in non-decreasing order; the combinations may be returned in any order.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="n = 12", output="[[2,6],[3,4],[2,2,3]]"),
            dict(input="n = 37", output="[]", explanation="37 is prime, and n itself is not a valid factor."),
            dict(input="n = 1", output="[]"),
        ],
        constraints=["<code>1 &lt;= n &lt;= 10<sup>7</sup></code>"],
        approaches=[
            dict(
                name="Factors in non-decreasing order, up to &radic;n",
                time="O(&radic;n &middot; F)",
                space="O(log n)",
                best=True,
                why=[
                    "Pick the smallest factor first. For each divisor <code>f</code> with <code>f &ge; start</code> and <code>f&sup2; &le; n</code>, the pair <code>path + [f, n/f]</code> is one answer, and <code>n/f</code> can be broken down further using factors &ge; <code>f</code>. Requiring non-decreasing factors is what removes duplicates like <code>[2, 6]</code> vs <code>[6, 2]</code>.",
                    "Stopping at <code>f&sup2; &le; n</code> matters: any factor above &radic;n would have to be paired with a smaller one, which would already have been tried. Depth is at most log<sub>2</sub> n, since every factor is at least 2. F is the number of combinations produced.",
                ],
                code='''def get_factors(n):
    out, path = [], []

    def dfs(n, start):
        f = start
        while f * f <= n:
            if n % f == 0:
                out.append(path + [f, n // f])     # stop here: f * (n / f)
                path.append(f)
                dfs(n // f, f)                    # or split n / f further
                path.pop()
            f += 1

    dfs(n, 2)
    return out''',
            ),
        ],
        tests='''assert as_set(get_factors(12)) == as_set([[2, 6], [3, 4], [2, 2, 3]])
assert get_factors(37) == [] and get_factors(1) == []
assert as_set(get_factors(32)) == as_set([[2, 16], [2, 2, 8], [2, 2, 2, 4], [2, 2, 2, 2, 2], [2, 4, 4], [4, 8]])
from math import prod
for n in range(2, 200):
    got = get_factors(n)
    assert all(prod(c) == n and c == sorted(c) and min(c) >= 2 for c in got)
    assert len(set(map(tuple, got))) == len(got)''',
    ),

    dict(
        id="brace-expansion",
        lc=1087, slug="brace-expansion",
        name="Brace Expansion",
        difficulty="medium",
        tags=["String", "Backtracking", "Breadth-First Search"],
        statement=[
            "A string <code>s</code> describes a list of words. Each letter outside braces is a fixed character; each group in braces, like <code>{a,b,c}</code>, is a choice of one of its comma-separated letters. For example, <code>\"{a,b}c{d,e}f\"</code> describes <code>[\"acdf\", \"acef\", \"bcdf\", \"bcef\"]</code>.",
            "Return all the words, sorted lexicographically. Braces are never nested, and each option is a single lowercase letter.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input='s = "{a,b}c{d,e}f"', output='["acdf","acef","bcdf","bcef"]'),
            dict(input='s = "abcd"', output='["abcd"]'),
        ],
        constraints=[
            "<code>1 &lt;= s.length &lt;= 50</code>",
            "No nested braces; letters within a group are distinct",
        ],
        approaches=[
            dict(
                name="Parse into option groups, backtrack in sorted order",
                time="O(W &middot; L)",
                space="O(L)",
                best=True,
                why=[
                    "Parse once into a list of groups: a fixed letter is a group of one. Sort each group, then backtrack choosing one letter per position. Every word has the same length L, so choosing letters in sorted order at each position emits the words in sorted order with no final sort.",
                    "W words of length L come out, which bounds the work from below.",
                ],
                code='''def expand(s):
    groups, i = [], 0
    while i < len(s):
        if s[i] == "{":
            j = s.index("}", i)
            groups.append(sorted(s[i + 1:j].split(",")))
            i = j + 1
        else:
            groups.append([s[i]])
            i += 1

    out, path = [], []

    def dfs(g):
        if g == len(groups):
            out.append("".join(path))
            return
        for ch in groups[g]:
            path.append(ch)
            dfs(g + 1)
            path.pop()

    dfs(0)
    return out''',
            ),
        ],
        tests='''assert expand("{a,b}c{d,e}f") == ["acdf", "acef", "bcdf", "bcef"]
assert expand("abcd") == ["abcd"]
assert expand("{c,a,b}") == ["a", "b", "c"]
assert expand("{a,b}{c,d}") == ["ac", "ad", "bc", "bd"]''',
    ),

    dict(
        id="word-pattern-ii",
        lc=291, slug="word-pattern-ii",
        name="Word Pattern II",
        difficulty="medium",
        tags=["Hash Table", "String", "Backtracking"],
        statement=[
            "Given a <code>pattern</code> and a string <code>s</code>, return <code>true</code> if <code>s</code> <strong>matches</strong> the pattern: there is a bijective mapping from each letter of the pattern to a non-empty string, such that replacing every letter with its string produces <code>s</code>. Different letters must map to different strings.",
            "Unlike Word Pattern (290), there are no spaces in <code>s</code> telling you where each word ends &mdash; you have to guess the split, which is why this needs backtracking.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input='pattern = "abab", s = "redblueredblue"', output="true", explanation='a &rarr; "red", b &rarr; "blue"'),
            dict(input='pattern = "aaaa", s = "asdasdasdasd"', output="true", explanation='a &rarr; "asd"'),
            dict(input='pattern = "aabb", s = "xyzabcxzyabc"', output="false"),
        ],
        constraints=[
            "<code>1 &lt;= pattern.length, s.length &lt;= 20</code>",
            "Both consist of lowercase English letters",
        ],
        approaches=[
            dict(
                name="Backtrack over the length of each new mapping",
                time="O(n<sup>p</sup>) worst",
                space="O(p)",
                best=True,
                why=[
                    "Walk the pattern. A letter that is already mapped leaves no choice: its string must appear next in <code>s</code>, or this branch fails. An unmapped letter tries every possible next substring &mdash; skipping any string already claimed by another letter, which is what makes the mapping a bijection.",
                    "Prune the lengths tried: the remaining pattern letters each need at least one character, so the new string cannot eat into their share. The worst case is exponential in the number of distinct letters, which is why the input is capped at 20.",
                ],
                code='''def word_pattern_match(pattern, s):
    mapping, claimed = {}, set()

    def dfs(i, j):
        if i == len(pattern):
            return j == len(s)
        ch = pattern[i]
        if ch in mapping:                            # forced: must match
            w = mapping[ch]
            return s.startswith(w, j) and dfs(i + 1, j + len(w))
        last = len(s) - (len(pattern) - i - 1)       # leave 1 char per later letter
        for end in range(j + 1, last + 1):
            w = s[j:end]
            if w in claimed:
                continue                             # bijection
            mapping[ch] = w
            claimed.add(w)
            if dfs(i + 1, end):
                return True
            del mapping[ch]
            claimed.discard(w)
        return False

    return dfs(0, 0)''',
            ),
        ],
        tests='''assert word_pattern_match("abab", "redblueredblue") is True
assert word_pattern_match("aaaa", "asdasdasdasd") is True
assert word_pattern_match("aabb", "xyzabcxzyabc") is False
assert word_pattern_match("ab", "aa") is False            # a and b cannot both be "a"
assert word_pattern_match("a", "") is False
assert word_pattern_match("abba", "dogcatcatdog") is True''',
    ),

    dict(
        id="android-unlock-patterns",
        lc=351, slug="android-unlock-patterns",
        name="Android Unlock Patterns",
        difficulty="medium",
        tags=["Dynamic Programming", "Backtracking", "Bit Manipulation", "Bitmask"],
        statement=[
            "The Android lock screen is a 3 &times; 3 grid of keys numbered 1&ndash;9. An unlock pattern is a sequence of distinct keys in which every consecutive pair is joined by a line segment, subject to one rule: a segment that passes through the <strong>centre</strong> of another key is only allowed if that key already appears earlier in the pattern. (1 &rarr; 3 passes through 2; 1 &rarr; 9 passes through 5; 2 &rarr; 9 passes through no key centre and is always allowed.)",
            "Given <code>m</code> and <code>n</code>, return how many distinct unlock patterns use at least <code>m</code> and at most <code>n</code> keys.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="m = 1, n = 1", output="9"),
            dict(input="m = 1, n = 2", output="65",
                 explanation="9 one-key patterns plus 56 valid two-key ones: of the 72 ordered pairs, 16 jump over an unvisited key."),
        ],
        constraints=["<code>1 &lt;= m, n &lt;= 9</code>"],
        approaches=[
            dict(
                name="Backtracking with a skip table and symmetry",
                time="O(9!)",
                space="O(1)",
                best=True,
                why=[
                    "Precompute <code>skip[a][b]</code>: the key a straight segment from a to b passes through, or 0 if none. A move to <code>b</code> is legal when <code>b</code> is unvisited and its skip key is 0 or already visited.",
                    "Count from each start with the usual mark/recurse/unmark. Symmetry cuts the work to a third: the four corners (1, 3, 7, 9) are rotations of each other, as are the four edges (2, 4, 6, 8), so count from 1, 2 and 5 and weight by 4, 4 and 1.",
                    "The search tree has at most 9! leaves, a constant, so this is O(1) in any meaningful sense &mdash; the interest is in the modelling.",
                ],
                code='''def number_of_patterns(m, n):
    skip = [[0] * 10 for _ in range(10)]
    for a, b, mid in [(1, 3, 2), (4, 6, 5), (7, 9, 8), (1, 7, 4), (2, 8, 5),
                      (3, 9, 6), (1, 9, 5), (3, 7, 5)]:
        skip[a][b] = skip[b][a] = mid
    visited = [False] * 10

    def dfs(cur, length):
        count = 1 if length >= m else 0
        if length == n:
            return count
        visited[cur] = True
        for nxt in range(1, 10):
            mid = skip[cur][nxt]
            if not visited[nxt] and (mid == 0 or visited[mid]):
                count += dfs(nxt, length + 1)
        visited[cur] = False
        return count

    return 4 * dfs(1, 1) + 4 * dfs(2, 1) + dfs(5, 1)   # corner, edge, centre''',
            ),
            dict(
                name="Backtracking from all nine keys",
                time="O(9!)",
                space="O(1)",
                why=[
                    "The same search without the symmetry argument: start from every key. Three times the work, and a useful cross-check that the symmetry weighting is right.",
                ],
                code='''def number_of_patterns(m, n):
    skip = [[0] * 10 for _ in range(10)]
    for a, b, mid in [(1, 3, 2), (4, 6, 5), (7, 9, 8), (1, 7, 4), (2, 8, 5),
                      (3, 9, 6), (1, 9, 5), (3, 7, 5)]:
        skip[a][b] = skip[b][a] = mid
    visited = [False] * 10

    def dfs(cur, length):
        count = 1 if length >= m else 0
        if length == n:
            return count
        visited[cur] = True
        for nxt in range(1, 10):
            mid = skip[cur][nxt]
            if not visited[nxt] and (mid == 0 or visited[mid]):
                count += dfs(nxt, length + 1)
        visited[cur] = False
        return count

    return sum(dfs(k, 1) for k in range(1, 10))''',
            ),
        ],
        tests='''assert number_of_patterns(1, 1) == 9
assert number_of_patterns(1, 2) == 65
assert number_of_patterns(4, 9) == 389112          # the real Android count
assert number_of_patterns(1, 9) == 389497
assert number_of_patterns(3, 2) == 0''',
    ),
    ],
),

# ---------------------------------------------------------------- 5
dict(
    id="hard",
    title="The hard ones",
    idea=[
        "Each of these adds one idea to plain backtracking: constant-time conflict checks (N-Queens), memoisation of dead ends (Word Break II), a movement model without coordinates (Robot Room Cleaner), and a trie that searches many words at once (Word Search II).",
    ],
    problems=[

    dict(
        id="n-queens",
        lc=51, slug="n-queens",
        name="N-Queens",
        difficulty="hard",
        framing=[
            "Place n queens on an n &times; n board so that none attack each other; return every arrangement. One queen per row is forced, so the choice at row r is only its column &mdash; and the whole difficulty is checking attacks quickly.",
        ],
        approaches=[
            dict(
                name="One row at a time, three sets of attacked lines",
                time="O(n!)",
                space="O(n)",
                best=True,
                why=[
                    "A queen attacks its column and its two diagonals. On one diagonal <code>r - c</code> is constant; on the other, <code>r + c</code> is. Three sets of attacked columns and diagonals make every placement check O(1) instead of scanning the board.",
                    "Row r has at most n - r safe columns, so the tree has at most n! leaves; attacks prune it far below that (n = 8 has only 92 solutions). Boards are built only when a complete solution is found.",
                ],
                code='''def solve_n_queens(n):
    out, cols, diag, anti, place = [], set(), set(), set(), []

    def dfs(r):
        if r == n:
            out.append(["." * c + "Q" + "." * (n - c - 1) for c in place])
            return
        for c in range(n):
            if c in cols or r - c in diag or r + c in anti:
                continue
            cols.add(c); diag.add(r - c); anti.add(r + c); place.append(c)
            dfs(r + 1)
            cols.remove(c); diag.remove(r - c); anti.remove(r + c); place.pop()

    dfs(0)
    return out''',
            ),
        ],
        tests='''assert sorted(solve_n_queens(4)) == sorted([[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]])
assert solve_n_queens(1) == [["Q"]]
assert [len(solve_n_queens(n)) for n in range(1, 9)] == [1, 0, 0, 2, 10, 4, 40, 92]
for board in solve_n_queens(6):
    qs = [(r, row.index("Q")) for r, row in enumerate(board)]
    assert len({c for _, c in qs}) == 6 and len({r - c for r, c in qs}) == 6 and len({r + c for r, c in qs}) == 6''',
    ),

    dict(
        id="n-queens-ii",
        lc=52, slug="n-queens-ii",
        name="N-Queens II",
        difficulty="hard",
        framing=[
            "Count the solutions instead of listing them. Without boards to build, the attack sets can be replaced by bitmasks, and the whole search becomes integer arithmetic.",
        ],
        approaches=[
            dict(
                name="Bitmask backtracking",
                time="O(n!)",
                space="O(n)",
                best=True,
                why=[
                    "Keep three n-bit integers: occupied columns, and the columns attacked on the current row by each family of diagonals. Free squares are <code>~(cols | d1 | d2) &amp; full</code>. Take the lowest free bit with <code>free &amp; -free</code>, place it, and recurse &mdash; shifting the diagonal masks by one as they move down a row.",
                    "Same search tree as the set version, with every operation a handful of bit instructions, typically several times faster in Python.",
                ],
                code='''def total_n_queens(n):
    full = (1 << n) - 1

    def dfs(cols, d1, d2):
        if cols == full:
            return 1
        count, free = 0, full & ~(cols | d1 | d2)
        while free:
            bit = free & -free                  # lowest free column
            free ^= bit
            count += dfs(cols | bit, (d1 | bit) << 1 & full, (d2 | bit) >> 1)
        return count

    return dfs(0, 0, 0)''',
            ),
            dict(
                name="Sets of attacked lines",
                time="O(n!)",
                space="O(n)",
                why=[
                    "The N-Queens solution returning a count instead of boards.",
                ],
                code='''def total_n_queens(n):
    cols, diag, anti = set(), set(), set()

    def dfs(r):
        if r == n:
            return 1
        count = 0
        for c in range(n):
            if c in cols or r - c in diag or r + c in anti:
                continue
            cols.add(c); diag.add(r - c); anti.add(r + c)
            count += dfs(r + 1)
            cols.remove(c); diag.remove(r - c); anti.remove(r + c)
        return count

    return dfs(0)''',
            ),
        ],
        tests='''assert [total_n_queens(n) for n in range(1, 10)] == [1, 0, 0, 2, 10, 4, 40, 92, 352]''',
    ),

    dict(
        id="word-break-ii",
        lc=140, slug="word-break-ii",
        name="Word Break II",
        difficulty="hard",
        framing=[
            "Return every way to split <code>s</code> into dictionary words, as sentences. Plain backtracking is correct but can explode on inputs with no answer at all &mdash; like <code>\"aaaa&hellip;ab\"</code> with <code>[\"a\", \"aa\", \"aaa\"]</code>, where exponentially many prefixes all fail at the final <code>b</code>. The fix is remembering which suffixes are dead.",
        ],
        approaches=[
            dict(
                name="Memoised sentences per suffix",
                time="O(n&sup2; + output)",
                space="O(n &middot; output)",
                best=True,
                why=[
                    "<code>sentences(i)</code> returns every way to split <code>s[i:]</code>. It depends only on <code>i</code>, so cache it. A dead suffix is computed once and returns <code>[]</code>; every later branch that reaches it gets that answer instantly.",
                    "Without the output, the work is O(n&sup2;) substring checks. The output itself can be exponential (think <code>\"aaaa&hellip;\"</code> with every length of <code>a</code> in the dictionary), and no algorithm can avoid producing it.",
                ],
                code='''def word_break(s, word_dict):
    words = set(word_dict)
    longest = max(map(len, words), default=0)

    @cache
    def sentences(i):
        if i == len(s):
            return [""]
        out = []
        for j in range(i + 1, min(len(s), i + longest) + 1):
            w = s[i:j]
            if w in words:
                for rest in sentences(j):
                    out.append(w + " " + rest if rest else w)
        return out

    return sentences(0)''',
            ),
            dict(
                name="Backtracking pruned by a word-break table",
                time="O(n&sup2; + output &middot; n)",
                space="O(n)",
                why=[
                    "First run Word Break I backwards: <code>ok[i]</code> is True if <code>s[i:]</code> can be split at all. Then backtrack normally, but only step to positions where <code>ok</code> is True. Every branch taken now leads to at least one sentence, so there are no dead ends to explore.",
                    "Less memory than caching every suffix's sentence list, at the cost of rebuilding shared suffixes for each prefix that reaches them.",
                ],
                code='''def word_break(s, word_dict):
    words, n = set(word_dict), len(s)
    ok = [False] * n + [True]
    for i in range(n - 1, -1, -1):
        ok[i] = any(s[i:j] in words and ok[j] for j in range(i + 1, n + 1))

    out, path = [], []

    def dfs(i):
        if i == n:
            out.append(" ".join(path))
            return
        for j in range(i + 1, n + 1):
            if ok[j] and s[i:j] in words:
                path.append(s[i:j])
                dfs(j)
                path.pop()

    if ok[0]:
        dfs(0)
    return out''',
            ),
        ],
        tests='''assert sorted(word_break("catsanddog", ["cat", "cats", "and", "sand", "dog"])) == ["cat sand dog", "cats and dog"]
assert sorted(word_break("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"])) == [
    "pine apple pen apple", "pine applepen apple", "pineapple pen apple"]
assert word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) == []
assert word_break("a" * 40 + "b", ["a", "aa", "aaa"]) == []        # exponential without pruning
assert len(word_break("a" * 10, ["a", "aa"])) == 89''',
    ),

    dict(
        id="robot-room-cleaner",
        lc=489, slug="robot-room-cleaner",
        name="Robot Room Cleaner",
        difficulty="hard",
        tags=["Backtracking", "Interactive"],
        statement=[
            "A robot is in a room modelled as a grid of open cells and walls, but you are <strong>not</strong> given the grid, the robot's position, or which way it faces. You control it only through this API:",
            "<code>move()</code> moves one cell forward and returns <code>true</code>, or returns <code>false</code> and stays put if a wall or the edge is in front. <code>turnLeft()</code> and <code>turnRight()</code> rotate 90&deg; in place. <code>clean()</code> cleans the current cell.",
            "Write <code>clean_room(robot)</code> so that every open cell reachable from the start is cleaned.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="room = [[1,1,1],[1,0,1],[1,1,1]] (0 = wall), start = (0,0)",
                 output="all 8 open cells cleaned"),
        ],
        constraints=[
            "The room has at most 100 &times; 200 cells",
            "The robot starts on an open cell",
        ],
        approaches=[
            dict(
                name="DFS in the robot's own coordinates, physically backtracking",
                time="O(N)",
                space="O(N)",
                best=True,
                why=[
                    "Invent coordinates: call the start <code>(0, 0)</code> and the robot's initial heading \"up\". Every move updates the position in this private frame, so a visited set works as in any grid DFS, even though the real position is unknown.",
                    "From each cell, try the four directions in clockwise order by turning right after each attempt; four right turns bring the robot back to the heading it arrived with. After exploring a neighbour, the robot must physically return: turn around, move, turn around again. That is the un-choose step, and it is what makes this a backtracking problem rather than an ordinary graph search.",
                    "Each open cell is entered once and each move is undone once: O(N) moves for N reachable cells, O(N) for the visited set and the recursion.",
                ],
                code='''def clean_room(robot):
    DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]       # up, right, down, left: clockwise
    visited = set()

    def go_back():
        robot.turnRight(); robot.turnRight()
        robot.move()
        robot.turnRight(); robot.turnRight()

    def dfs(cell, d):
        visited.add(cell)
        robot.clean()
        for k in range(4):
            nd = (d + k) % 4
            nxt = (cell[0] + DIRS[nd][0], cell[1] + DIRS[nd][1])
            if nxt not in visited and robot.move():
                dfs(nxt, nd)
                go_back()                             # un-choose: return physically
            robot.turnRight()                         # next direction clockwise

    dfs((0, 0), 0)''',
            ),
        ],
        tests='''class _Robot:
    STEP = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    def __init__(self, room, r, c, d):
        self.room, self.r, self.c, self.d = room, r, c, d
        self.cleaned = set()
    def move(self):
        dr, dc = self.STEP[self.d]
        nr, nc = self.r + dr, self.c + dc
        if 0 <= nr < len(self.room) and 0 <= nc < len(self.room[0]) and self.room[nr][nc]:
            self.r, self.c = nr, nc
            return True
        return False
    def turnLeft(self):
        self.d = (self.d - 1) % 4
    def turnRight(self):
        self.d = (self.d + 1) % 4
    def clean(self):
        self.cleaned.add((self.r, self.c))


def _reachable(room, r, c):
    seen, stack = {(r, c)}, [(r, c)]
    while stack:
        a, b = stack.pop()
        for da, db in _Robot.STEP:
            x, y = a + da, b + db
            if 0 <= x < len(room) and 0 <= y < len(room[0]) and room[x][y] and (x, y) not in seen:
                seen.add((x, y)); stack.append((x, y))
    return seen

room = [[1, 1, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 0, 1, 1],
        [1, 0, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1]]
bot = _Robot(room, 1, 3, 0)
clean_room(bot)
assert bot.cleaned == _reachable(room, 1, 3)
rng = random.Random(6)
for trial in range(20):
    R, C = rng.randint(1, 8), rng.randint(1, 8)
    room = [[1 if rng.random() < 0.7 else 0 for _ in range(C)] for _ in range(R)]
    r, c = rng.randrange(R), rng.randrange(C)
    room[r][c] = 1
    bot = _Robot(room, r, c, rng.randrange(4))            # unknown heading
    clean_room(bot)
    assert bot.cleaned == _reachable(room, r, c), trial''',
    ),

    dict(
        id="word-search-ii",
        lc=212, slug="word-search-ii",
        name="Word Search II",
        difficulty="hard",
        framing=[
            "Find every word from a list that can be traced on the board. Running Word Search once per word repeats the same grid walks for words sharing a prefix. A <strong>trie</strong> lets one walk search for all words at once: the DFS follows the board and the trie together, and stops the moment the current path is not a prefix of any word.",
        ],
        approaches=[
            dict(
                name="Trie-guided DFS, pruning found words",
                time="O(R &middot; C &middot; 3<sup>L</sup>)",
                space="O(total word length)",
                best=True,
                why=[
                    "Build a trie of the words; a node stores the complete word at its end. Start a DFS from each cell whose letter begins some word, and only step to a neighbour whose letter is a child of the current trie node. Every path explored is a prefix of a real word.",
                    "Two refinements matter at scale. Remove a word from the trie once found, so it is never reported twice. And delete trie branches that become empty on the way back, so later searches do not re-walk exhausted prefixes.",
                    "The worst-case bound (L is the longest word) is the same as Word Search, but it is paid once for all words, not once per word.",
                ],
                code='''def find_words(board, words):
    trie = {}
    for w in words:
        node = trie
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w
    R, C, out = len(board), len(board[0]), []

    def dfs(r, c, parent):
        ch = board[r][c]
        node = parent[ch]
        if "$" in node:
            out.append(node.pop("$"))              # found: never report it again
        board[r][c] = "#"
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and board[nr][nc] in node:
                dfs(nr, nc, node)
        board[r][c] = ch
        if not node:
            parent.pop(ch)                         # prune an exhausted branch

    for r in range(R):
        for c in range(C):
            if board[r][c] in trie:
                dfs(r, c, trie)
    return out''',
            ),
            dict(
                name="Word Search once per word",
                time="O(W &middot; R &middot; C &middot; 3<sup>L</sup>)",
                space="O(L)",
                tag="baseline",
                why=[
                    "Correct, and fine for a handful of words. With thousands of words sharing prefixes, every one of them repeats the walk the trie would have shared.",
                ],
                code='''def find_words(board, words):
    R, C = len(board), len(board[0])

    def exist(word):
        def dfs(r, c, i):
            if board[r][c] != word[i]:
                return False
            if i == len(word) - 1:
                return True
            board[r][c] = "#"
            found = any(0 <= nr < R and 0 <= nc < C and dfs(nr, nc, i + 1)
                        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)))
            board[r][c] = word[i]
            return found
        return any(dfs(r, c, 0) for r in range(R) for c in range(C))

    return [w for w in dict.fromkeys(words) if exist(w)]''',
            ),
        ],
        tests='''board = [["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]]
assert sorted(find_words([row[:] for row in board], ["oath", "pea", "eat", "rain"])) == ["eat", "oath"]
assert find_words([["a", "b"], ["c", "d"]], ["abcb"]) == []
assert sorted(find_words([["a", "a"]], ["a", "aa", "aaa"])) == ["a", "aa"]
rng = random.Random(7)
for _ in range(15):
    R, C = rng.randint(1, 4), rng.randint(1, 4)
    b = [[rng.choice("abc") for _ in range(C)] for _ in range(R)]
    ws = list({"".join(rng.choice("abc") for _ in range(rng.randint(1, 5))) for _ in range(12)})
    expect = set()
    for w in ws:
        def dfs(r, c, i, seen):
            if b[r][c] != w[i] or (r, c) in seen:
                return False
            if i == len(w) - 1:
                return True
            return any(0 <= x < R and 0 <= y < C and dfs(x, y, i + 1, seen | {(r, c)})
                       for x, y in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)))
        if any(dfs(r, c, 0, frozenset()) for r in range(R) for c in range(C)):
            expect.add(w)
    assert set(find_words([row[:] for row in b], ws)) == expect''',
    ),
    ],
),
    ],
)
