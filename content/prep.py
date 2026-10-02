# -*- coding: utf-8 -*-
"""Interview prep: the pattern cheat sheet and the Python complexity cheat
sheet shown on prep.html. The mock-interview tab needs no content: it draws
from the DSA problems.

Every pattern's `template` is executed by build.py with its `check` appended,
so each template is known to work. `examples` are DSA problem ids and are
validated against the DSA data, so a link can never point at nothing.
"""

PATTERNS = [

dict(
    id="two-pointers",
    name="Two pointers from both ends",
    signals=[
        "Sorted array (or you may sort it), and you are looking for a pair or triple",
        "\"Maximise area / minimise difference\" between two positions",
        "In-place reversal or palindrome check",
    ],
    idea="Start at both ends. Each comparison proves one end cannot be part of any better answer, so that pointer moves inward. O(n) instead of O(n&sup2;).",
    template='''def pair_with_sum(nums, target):          # nums sorted
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return lo, hi
        if s < target:
            lo += 1          # nums[lo] is too small for every remaining partner
        else:
            hi -= 1          # nums[hi] is too big for every remaining partner
    return None''',
    check='''assert pair_with_sum([1, 3, 4, 6, 9], 10) == (0, 4)
assert pair_with_sum([1, 2], 7) is None''',
    examples=["two-sum-ii", "three-sum", "container-most-water", "trapping-rain-water"],
),

dict(
    id="fast-slow",
    name="Fast and slow pointers",
    signals=[
        "Linked list: find the middle, detect a cycle, find the cycle's start",
        "A function applied repeatedly that must eventually repeat (happy number, i &rarr; nums[i])",
    ],
    idea="The fast pointer moves two steps per slow step. In a cycle it gains one node per step, so it catches the slow pointer within one lap; without a cycle it reaches the end. When fast reaches the end, slow is at the middle.",
    template='''def middle_and_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return "cycle"
    return slow              # the middle node (second middle for even length)''',
    check='''class N:
    def __init__(self, v, nxt=None): self.val, self.next = v, nxt
lst = N(1, N(2, N(3, N(4, N(5)))))
assert middle_and_cycle(lst).val == 3
a = N(1, N(2, N(3))); a.next.next.next = a.next
assert middle_and_cycle(a) == "cycle"''',
    examples=["linked-list-cycle", "reorder-list", "find-duplicate-number", "happy-number"],
),

dict(
    id="sliding-window",
    name="Variable sliding window",
    signals=[
        "Longest / shortest <em>contiguous</em> subarray or substring with some property",
        "The property is monotonic: extending a valid window keeps it valid, or shrinking an invalid one fixes it",
        "Non-negative numbers (with negatives, use prefix sums instead)",
    ],
    idea="Grow the right edge one step at a time; while the window is invalid, shrink from the left. Each index enters and leaves once, so the whole scan is O(n).",
    template='''def longest_with_at_most_k_distinct(s, k):
    counts, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1          # extend
        while len(counts) > k:                      # invalid: shrink
            counts[s[left]] -= 1
            if counts[s[left]] == 0:
                del counts[s[left]]
            left += 1
        best = max(best, right - left + 1)          # record the valid window
    return best''',
    check='''assert longest_with_at_most_k_distinct("eceba", 2) == 3
assert longest_with_at_most_k_distinct("aa", 1) == 2''',
    examples=["longest-substring-no-repeat", "longest-repeating-replacement", "minimum-size-subarray-sum", "minimum-window-substring"],
),

dict(
    id="prefix-sums",
    name="Prefix sums + hash map",
    signals=[
        "Count or find subarrays with sum (or XOR, or balance) exactly k",
        "Negative numbers are allowed, so a sliding window breaks",
        "Many range-sum queries on a fixed array",
    ],
    idea="A subarray (i, j] sums to <code>P[j] - P[i]</code>. So a subarray ending here sums to k exactly when an earlier prefix equals <code>P - k</code>: count earlier prefixes in a hash map. Seed it with the empty prefix.",
    template='''from collections import Counter

def count_subarrays_with_sum(nums, k):
    seen = Counter({0: 1})           # the empty prefix
    total = count = 0
    for x in nums:
        total += x
        count += seen[total - k]     # earlier prefixes that complete a sum of k
        seen[total] += 1
    return count''',
    check='''assert count_subarrays_with_sum([1, 1, 1], 2) == 2
assert count_subarrays_with_sum([1, -1, 0], 0) == 3''',
    examples=["subarray-sum-equals-k", "range-sum-query-2d", "path-sum-iii", "product-except-self"],
),

dict(
    id="binary-search-answer",
    name="Binary search on the answer",
    signals=[
        "\"Minimum X such that it is possible to ...\" or \"maximum X such that ...\"",
        "A check for a given X is easy (usually a greedy O(n) pass)",
        "Feasibility is monotonic in X",
    ],
    idea="Do not search an array; search the range of possible answers. If X works, every larger X works too (or smaller, for maximisation), so binary search finds the boundary with O(log range) checks.",
    template='''def smallest_feasible(lo, hi, feasible):
    """Smallest x in [lo, hi] with feasible(x) true; feasible must be monotonic."""
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid             # mid works: the answer is mid or smaller
        else:
            lo = mid + 1
    return lo


def min_eating_speed(piles, h):
    return smallest_feasible(1, max(piles),
                             lambda k: sum((p + k - 1) // k for p in piles) <= h)''',
    check='''assert min_eating_speed([3, 6, 7, 11], 8) == 4
assert smallest_feasible(0, 100, lambda x: x * x >= 50) == 8''',
    examples=["koko-eating-bananas", "ship-within-days", "split-array-largest-sum", "sqrt-x"],
),

dict(
    id="monotonic-stack",
    name="Monotonic stack",
    signals=[
        "\"Next greater / smaller element\", \"how many days until ...\"",
        "Spans, histograms, the nearest taller bar on each side",
    ],
    idea="Keep indices whose values are monotonic. A new element pops everything it dominates &mdash; and for each popped element, the new one is its answer. Every index is pushed and popped once: O(n).",
    template='''def next_greater(nums):
    out, stack = [-1] * len(nums), []       # stack of indices, values decreasing
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            out[stack.pop()] = x            # x is the next greater for that index
        stack.append(i)
    return out''',
    check='''assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]''',
    examples=["daily-temperatures", "online-stock-span", "largest-rectangle-histogram", "sliding-window-maximum"],
),

dict(
    id="heap-top-k",
    name="Heap of size k (top-k)",
    signals=[
        "k largest / smallest / most frequent / closest",
        "Streaming data where you keep the best k so far",
        "Merging k sorted sequences",
    ],
    idea="A min-heap of size k keeps the k largest items seen: whenever it grows past k, pop the smallest. O(n log k) instead of sorting everything; for k-way merges, the heap holds one head per list.",
    template='''import heapq

def k_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)       # drop the smallest: it is not top-k
    return sorted(heap, reverse=True)''',
    check='''assert k_largest([3, 2, 1, 5, 6, 4], 2) == [6, 5]''',
    examples=["kth-largest-element", "top-k-frequent", "merge-k-sorted-lists", "find-median-from-data-stream"],
),

dict(
    id="bfs",
    name="BFS for shortest paths (and multi-source BFS)",
    signals=[
        "Fewest steps / moves / transformations in an unweighted graph or grid",
        "Distance from every cell to the <em>nearest</em> of several sources",
        "Spreading processes that advance one step per minute",
    ],
    idea="A queue explores in rings of equal distance, so the first time a node is reached is along a shortest path. Mark nodes as seen when they are <em>enqueued</em>. Put every source in the queue at the start for nearest-source distances.",
    template='''from collections import deque

def grid_distances(grid, sources):
    """Distance from each open cell ('.') to its nearest source; -1 if unreachable."""
    m, n = len(grid), len(grid[0])
    dist = [[-1] * n for _ in range(m)]
    queue = deque(sources)
    for r, c in sources:
        dist[r][c] = 0
    while queue:
        r, c = queue.popleft()
        for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= a < m and 0 <= b < n and grid[a][b] == "." and dist[a][b] == -1:
                dist[a][b] = dist[r][c] + 1          # mark on enqueue
                queue.append((a, b))
    return dist''',
    check='''d = grid_distances(["...", ".#.", "..."], [(0, 0), (2, 2)])
assert d[0][2] == 2 and d[1][1] == -1 and d[2][0] == 2''',
    examples=["rotting-oranges", "walls-and-gates", "open-the-lock", "word-ladder"],
),

dict(
    id="dfs-flood",
    name="DFS / flood fill",
    signals=[
        "Count or measure connected regions (islands, provinces)",
        "Anything reachable from X: \"can water flow ...\", \"which cells are safe\"",
    ],
    idea="From each unvisited start, visit everything reachable and mark it. Use an explicit stack in Python: recursion depth can exceed the 1000-frame limit on large grids.",
    template='''def count_regions(grid):
    m, n = len(grid), len(grid[0])
    seen, regions = set(), 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == "1" and (r, c) not in seen:
                regions += 1
                stack = [(r, c)]
                seen.add((r, c))
                while stack:
                    x, y = stack.pop()
                    for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= a < m and 0 <= b < n and grid[a][b] == "1" and (a, b) not in seen:
                            seen.add((a, b))
                            stack.append((a, b))
    return regions''',
    check='''assert count_regions(["110", "010", "001"]) == 2''',
    examples=["number-of-islands", "max-area-of-island", "pacific-atlantic", "surrounded-regions"],
),

dict(
    id="topological-sort",
    name="Topological sort (Kahn)",
    signals=[
        "Prerequisites, build order, task dependencies",
        "\"Is there a valid order?\" = \"is this directed graph acyclic?\"",
        "Ordering constraints hidden in data (alien dictionary)",
    ],
    idea="Repeatedly take a node with no remaining incoming edges and remove its edges. If every node is taken, the order is valid; leftovers mean a cycle.",
    template='''from collections import defaultdict, deque

def topo_order(n, edges):              # edge (a, b): a must come before b
    adj, indeg = defaultdict(list), [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    queue = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return order if len(order) == n else []     # [] means a cycle''',
    check='''order = topo_order(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
assert order.index(0) < order.index(1) < order.index(3) and order.index(2) < order.index(3)
assert topo_order(2, [(0, 1), (1, 0)]) == []''',
    examples=["course-schedule", "course-schedule-ii", "alien-dictionary", "minimum-height-trees"],
),

dict(
    id="union-find",
    name="Union-find",
    signals=[
        "Edges arrive one at a time and you need connectivity after each",
        "Detect the edge that creates a cycle; count components",
        "Grouping by a transitive relation (accounts sharing an email)",
    ],
    idea="Each set is a tree; <code>find</code> walks to the root (compressing the path), <code>union</code> links roots (smaller under larger). Both are effectively O(1).",
    template='''class DSU:
    def __init__(self, n):
        self.parent, self.size = list(range(n)), [1] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                  # already connected
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True''',
    check='''d = DSU(5)
assert d.union(0, 1) and d.union(1, 2) and not d.union(0, 2)
assert d.find(2) == d.find(0) and d.find(3) != d.find(0)''',
    examples=["count-connected-components", "redundant-connection", "accounts-merge", "graph-valid-tree"],
),

dict(
    id="backtracking",
    name="Backtracking",
    signals=[
        "\"Return all\" subsets / permutations / combinations / partitions / boards",
        "Small input (n &le; 20), exponential output",
        "Constraint puzzles: N-Queens, Sudoku, word search",
    ],
    idea="Choose an option, recurse, un-choose. Prune a branch as soon as it cannot lead to a valid answer. Skip equal values at the same depth (after sorting) to avoid duplicate answers.",
    template='''def subsets_without_duplicates(nums):
    nums, out, path = sorted(nums), [], []

    def dfs(start):
        out.append(path[:])                       # every node is an answer here
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                          # same value, same depth: skip
            path.append(nums[i])                  # choose
            dfs(i + 1)                            # explore
            path.pop()                            # un-choose

    dfs(0)
    return out''',
    check='''assert sorted(map(tuple, subsets_without_duplicates([1, 2, 2]))) == [(), (1,), (1, 2), (1, 2, 2), (2,), (2, 2)]''',
    examples=["subsets", "combination-sum-ii", "permutations-ii", "n-queens"],
),

dict(
    id="dp-1d",
    name="1-D dynamic programming",
    signals=[
        "\"Number of ways\", \"minimum cost\", \"maximum value\" over a sequence",
        "The answer at i depends on a few earlier answers",
        "A brute-force recursion that recomputes the same arguments",
    ],
    idea="Name the state (<em>best answer for the prefix ending at i</em>), write the recurrence, fill it in order. If i only reads i-1 and i-2, two variables replace the table.",
    template='''def house_robber(nums):
    take, skip = 0, 0                     # best ending at i with / without robbing i
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)


def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount             # dp[a] = fewest coins to make a
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] < INF else -1''',
    check='''assert house_robber([2, 7, 9, 3, 1]) == 12
assert coin_change([1, 2, 5], 11) == 3 and coin_change([2], 3) == -1''',
    examples=["climbing-stairs", "house-robber", "coin-change", "longest-increasing-subsequence"],
),

dict(
    id="dp-2d",
    name="2-D dynamic programming on two strings or a grid",
    signals=[
        "Two strings compared position by position (edit distance, LCS)",
        "Paths through a grid moving right/down",
        "State needs two indices",
    ],
    idea="<code>dp[i][j]</code> describes the prefixes <code>a[:i]</code> and <code>b[:j]</code> (or cell (i, j)). Each cell reads its left, upper and upper-left neighbours, so one rolling row is enough memory.",
    template='''def lcs(a, b):
    prev = [0] * (len(b) + 1)             # one row: dp[i-1][*]
    for ch in a:
        cur = [0]
        for j, other in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if ch == other else max(prev[j], cur[j - 1]))
        prev = cur
    return prev[-1]''',
    check='''assert lcs("abcde", "ace") == 3 and lcs("abc", "def") == 0''',
    examples=["longest-common-subsequence", "edit-distance", "unique-paths", "interleaving-string"],
),

dict(
    id="tree-postorder",
    name="Tree recursion: return one thing, record another",
    signals=[
        "Any-node-to-any-node paths in a tree (diameter, max path sum)",
        "A node needs both children's answers first (postorder)",
        "Include/exclude choices per node (house robber on a tree)",
    ],
    idea="Each call returns what its <em>parent</em> needs (a height, the best single arm, a pair of states), and separately updates a global answer with the best path that bends at this node.",
    template='''def diameter(root):
    best = 0

    def height(node):
        nonlocal best
        if node is None:
            return 0
        l, r = height(node.left), height(node.right)
        best = max(best, l + r)           # path bending here: the answer
        return 1 + max(l, r)              # what the parent can extend

    height(root)
    return best''',
    check='''class T:
    def __init__(self, l=None, r=None): self.left, self.right = l, r
assert diameter(T(T(T(), T()), T())) == 3''',
    examples=["diameter-of-binary-tree", "binary-tree-maximum-path-sum", "house-robber-iii", "lca-binary-tree"],
),

dict(
    id="intervals",
    name="Sort intervals, then sweep",
    signals=[
        "Merge / insert / count overlapping intervals",
        "Meeting rooms, scheduling, minimum removals",
    ],
    idea="Sort by start (to merge) or by end (to select the most non-overlapping). After sorting, only the last kept interval can overlap the next one.",
    template='''def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)   # overlap: extend (may be contained)
        else:
            out.append([s, e])
    return out''',
    check='''assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge([[1, 10], [2, 3]]) == [[1, 10]]''',
    examples=["merge-intervals", "insert-interval", "non-overlapping-intervals", "meeting-rooms-ii"],
),

dict(
    id="dijkstra",
    name="Dijkstra (weighted shortest paths)",
    signals=[
        "Weighted edges, non-negative weights, cheapest path",
        "\"Minimise the maximum step\" (use max instead of +)",
    ],
    idea="Pop the closest unsettled node from a min-heap; its distance is final. Relax its edges. Skip stale heap entries instead of decreasing keys.",
    template='''import heapq

def dijkstra(adj, src):              # adj[u] = [(v, w), ...]
    dist, heap = {}, [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue                 # stale entry
        dist[u] = d
        for v, w in adj.get(u, []):
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return dist''',
    check='''g = {"a": [("b", 1), ("c", 4)], "b": [("c", 2)], "c": []}
assert dijkstra(g, "a") == {"a": 0, "b": 1, "c": 3}''',
    examples=["network-delay-time", "path-minimum-effort", "swim-rising-water", "cheapest-flights-k-stops"],
),

dict(
    id="trie",
    name="Trie",
    signals=[
        "Many prefix queries, autocomplete",
        "Searching a grid or string for many words at once",
    ],
    idea="A tree of characters where shared prefixes share a path. Lookups cost O(length of the query), independent of how many words are stored.",
    template='''def build_trie(words):
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w                 # end of a word
    return root


def has_prefix(root, prefix):
    node = root
    for ch in prefix:
        if ch not in node:
            return False
        node = node[ch]
    return True''',
    check='''t = build_trie(["apple", "app", "bat"])
assert has_prefix(t, "ap") and not has_prefix(t, "c") and t["a"]["p"]["p"]["$"] == "app"''',
    examples=["implement-trie", "add-search-words", "word-search-ii", "extra-characters-string"],
),

dict(
    id="bits",
    name="Bit tricks",
    signals=[
        "Every element appears twice except one",
        "Subsets of a small set (n &le; 20) as integers",
        "\"Without + / -\", \"count set bits\"",
    ],
    idea="<code>x ^ x = 0</code> cancels pairs; <code>x &amp; (x - 1)</code> clears the lowest set bit; <code>x &amp; -x</code> isolates it; bit i of a mask says whether item i is in the subset.",
    template='''def single_number(nums):
    r = 0
    for x in nums:
        r ^= x                        # pairs cancel
    return r


def popcount(x):
    c = 0
    while x:
        x &= x - 1                    # drop the lowest set bit
        c += 1
    return c''',
    check='''assert single_number([4, 1, 2, 1, 2]) == 4 and popcount(0b101101) == 4''',
    examples=["single-number", "counting-bits", "missing-number", "sum-of-two-integers"],
),

dict(
    id="fenwick",
    name="Fenwick tree (count while you scan)",
    signals=[
        "Range sums with point updates mixed in",
        "\"How many earlier elements are smaller / larger than this one?\"",
        "Count pairs i &lt; j with an inequality between a[i] and a[j]",
    ],
    idea="Index <code>i</code> stores a block ending at <code>i</code> of length <code>i &amp; -i</code>. Prefix query strips the lowest bit, update adds it: both O(log n). For pair counting, compress values to ranks and scan, querying before inserting.",
    template='''class Fenwick:
    def __init__(self, n):
        self.tree = [0] * (n + 1)          # 1-indexed

    def add(self, i, delta=1):
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & -i

    def prefix(self, i):                   # sum of positions 1..i
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & -i
        return s


def count_smaller_after(nums):
    rank = {v: i + 1 for i, v in enumerate(sorted(set(nums)))}
    bit, out = Fenwick(len(rank)), []
    for x in reversed(nums):
        out.append(bit.prefix(rank[x] - 1))
        bit.add(rank[x])
    return out[::-1]''',
    check='''assert count_smaller_after([5, 2, 6, 1]) == [2, 1, 1, 0]
f = Fenwick(5); f.add(2, 3); f.add(4, 1)
assert f.prefix(3) == 3 and f.prefix(5) == 4''',
    examples=["range-sum-query-mutable", "count-of-smaller-numbers-after-self", "reverse-pairs", "count-of-range-sum"],
),

dict(
    id="segment-tree",
    name="Segment tree (range min / max)",
    signals=[
        "Range queries with an operation that has no inverse: min, max, gcd",
        "Range updates (\"set / add to every element in [l, r]\") - needs lazy propagation",
        "A DP whose transition is a max over a sliding range of values",
    ],
    idea="Leaves at <code>tree[n..2n)</code>, node <code>i</code> combines <code>2i</code> and <code>2i+1</code>. Any range splits into O(log n) nodes. The iterative version is short; switch the combine function and it becomes min, max or sum.",
    template='''class SegTree:
    def __init__(self, values, combine=max, identity=float("-inf")):
        self.n, self.f, self.e = len(values), combine, identity
        self.t = [identity] * self.n + list(values)
        for i in range(self.n - 1, 0, -1):
            self.t[i] = combine(self.t[2 * i], self.t[2 * i + 1])

    def set(self, i, v):
        i += self.n
        self.t[i] = v
        while i > 1:
            i //= 2
            self.t[i] = self.f(self.t[2 * i], self.t[2 * i + 1])

    def query(self, l, r):                 # combine over [l, r)
        res, l, r = self.e, l + self.n, r + self.n
        while l < r:
            if l & 1:
                res = self.f(res, self.t[l]); l += 1
            if r & 1:
                r -= 1; res = self.f(res, self.t[r])
            l //= 2; r //= 2
        return res''',
    check='''st = SegTree([5, 1, 4, 2, 3])
assert st.query(1, 4) == 4 and st.query(0, 5) == 5
st.set(3, 9)
assert st.query(2, 5) == 9
mn = SegTree([5, 1, 4], min, float("inf"))
assert mn.query(0, 3) == 1''',
    examples=["longest-increasing-subsequence-ii", "falling-squares", "range-sum-query-mutable"],
),

dict(
    id="kmp",
    name="KMP prefix function (borders)",
    signals=[
        "Substring search with a guaranteed O(n + m)",
        "\"Longest prefix that is also a suffix\", shortest period, repeated pattern",
        "Longest palindromic prefix (border of <code>s + \"#\" + reverse(s)</code>)",
    ],
    idea="<code>pi[i]</code> = longest proper border of <code>s[:i+1]</code>. On a mismatch fall back to <code>pi[k-1]</code> instead of restarting; the text pointer never moves back. <code>n - pi[-1]</code> is the shortest period.",
    template='''def prefix_function(s):
    pi, k = [0] * len(s), 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]                  # border of the border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi


def kmp_find(text, pat):
    pi, k = prefix_function(pat), 0
    for i, ch in enumerate(text):
        while k and ch != pat[k]:
            k = pi[k - 1]
        if ch == pat[k]:
            k += 1
        if k == len(pat):
            return i - k + 1
    return -1''',
    check='''assert prefix_function("abacaba") == [0, 0, 1, 0, 1, 2, 3]
assert kmp_find("mississippi", "issip") == 4 and kmp_find("abc", "d") == -1''',
    examples=["find-first-occurrence", "repeated-substring-pattern", "longest-happy-prefix", "shortest-palindrome"],
),

dict(
    id="rolling-hash",
    name="Rolling hash (Rabin-Karp)",
    signals=[
        "Compare many substrings of the same length",
        "\"Longest repeated / common substring\" (binary search on the length)",
        "You need O(1) substring equality after O(n) preprocessing",
    ],
    idea="Prefix hashes <code>H[i+1] = H[i]&middot;B + s[i]</code> mod a big prime give any substring's hash in O(1): <code>H[r] - H[l]&middot;B<sup>r-l</sup></code>. Equal hashes mean <em>probably</em> equal &mdash; verify on a hit when correctness matters.",
    template='''import random

class Hasher:
    MOD = (1 << 61) - 1

    def __init__(self, s):
        B = random.randrange(256, 1 << 40)
        self.h, self.p = [0], [1]
        for ch in s:
            self.h.append((self.h[-1] * B + ord(ch)) % self.MOD)
            self.p.append(self.p[-1] * B % self.MOD)

    def get(self, l, r):                   # hash of s[l:r]
        return (self.h[r] - self.h[l] * self.p[r - l]) % self.MOD''',
    check='''h = Hasher("abcabcx")
assert h.get(0, 3) == h.get(3, 6) and h.get(0, 3) != h.get(1, 4)''',
    examples=["longest-duplicate-substring", "find-first-occurrence", "longest-happy-prefix"],
),
]


# Python operation costs, CPython. "k" is the size of the argument.
COMPLEXITY = [

dict(
    title="list",
    note="A dynamic array. Appending and popping at the end are cheap; anything at the front or middle shifts elements.",
    rows=[
        ["<code>x[i]</code>, <code>x[i] = v</code>, <code>len(x)</code>", "O(1)", ""],
        ["<code>x.append(v)</code>, <code>x.pop()</code>", "O(1) amortised", "Occasional resize copies everything"],
        ["<code>x.pop(0)</code>, <code>x.insert(0, v)</code>", "O(n)", "Use <code>collections.deque</code>"],
        ["<code>x.pop(i)</code>, <code>x.insert(i, v)</code>, <code>del x[i]</code>", "O(n - i)", ""],
        ["<code>v in x</code>, <code>x.index(v)</code>, <code>x.count(v)</code>, <code>x.remove(v)</code>", "O(n)", "Use a set for membership"],
        ["<code>x[a:b]</code>", "O(b - a)", "Slicing copies"],
        ["<code>x + y</code>, <code>x.extend(y)</code>", "O(len(x) + k), O(k)", ""],
        ["<code>x.sort()</code>, <code>sorted(x)</code>", "O(n log n)", "Timsort: O(n) on already-sorted runs, stable"],
        ["<code>min(x)</code>, <code>max(x)</code>, <code>sum(x)</code>", "O(n)", ""],
        ["<code>x.reverse()</code>, <code>x[::-1]</code>", "O(n)", ""],
    ],
),

dict(
    title="dict and set",
    note="Hash tables. Average costs assume a reasonable hash; adversarial keys can make any operation O(n).",
    rows=[
        ["<code>d[k]</code>, <code>d[k] = v</code>, <code>del d[k]</code>, <code>k in d</code>", "O(1) average", "O(n) worst"],
        ["<code>s.add(v)</code>, <code>s.remove(v)</code>, <code>v in s</code>", "O(1) average", ""],
        ["<code>s | t</code>, <code>s &amp; t</code>, <code>s - t</code>", "O(len(s) + len(t)), O(min), O(len(s))", "Intersection iterates the smaller set"],
        ["Iterating", "O(n)", "dicts keep insertion order (3.7+)"],
        ["<code>Counter(iterable)</code>", "O(n)", "<code>most_common(k)</code> is O(n log k)"],
        ["Key or element hashing", "O(len) for str/tuple", "Strings cache their hash after the first time"],
    ],
),

dict(
    title="collections.deque",
    note="A doubly linked list of blocks: cheap at both ends, slow in the middle.",
    rows=[
        ["<code>append</code>, <code>appendleft</code>, <code>pop</code>, <code>popleft</code>", "O(1)", "Use for queues and BFS"],
        ["<code>q[i]</code>", "O(n)", "O(1) near the ends"],
        ["<code>rotate(k)</code>", "O(k)", ""],
    ],
),

dict(
    title="heapq",
    note="A binary min-heap stored in a plain list. For a max-heap, push negated values.",
    rows=[
        ["<code>heapify(x)</code>", "O(n)", "Faster than n pushes"],
        ["<code>heappush</code>, <code>heappop</code>, <code>heappushpop</code>", "O(log n)", ""],
        ["<code>x[0]</code> (peek)", "O(1)", ""],
        ["<code>nlargest(k, it)</code>, <code>nsmallest(k, it)</code>", "O(n log k)", ""],
        ["Remove an arbitrary item", "O(n)", "Use lazy deletion instead"],
    ],
),

dict(
    title="str",
    note="Immutable. Every \"modification\" builds a new string.",
    rows=[
        ["<code>s[i]</code>, <code>len(s)</code>", "O(1)", ""],
        ["<code>s + t</code>", "O(len(s) + len(t))", "Concatenating in a loop is O(n&sup2;); join a list instead"],
        ["<code>\"\".join(parts)</code>", "O(total length)", ""],
        ["<code>t in s</code>, <code>s.find(t)</code>", "O(len(s) &middot; len(t)) worst", "Usually much faster in practice"],
        ["<code>s[a:b]</code>, <code>s[::-1]</code>", "O(b - a), O(n)", ""],
        ["<code>s.split()</code>, <code>s.replace()</code>, <code>s.lower()</code>", "O(n)", ""],
    ],
),

dict(
    title="bisect, sorting helpers, math",
    note="",
    rows=[
        ["<code>bisect_left</code>, <code>bisect_right</code>", "O(log n)", "On a sorted list"],
        ["<code>insort(x, v)</code>", "O(n)", "The search is O(log n); the insert shifts"],
        ["<code>math.gcd(a, b)</code>", "O(log min(a, b))", ""],
        ["<code>pow(a, b, m)</code>", "O(log b)", "Built-in modular exponentiation"],
        ["<code>math.comb(n, k)</code>, big-integer multiply", "super-linear in digits", "Python ints are arbitrary precision"],
        ["<code>functools.cache</code> lookup", "O(1) average + hashing the arguments", ""],
    ],
),
]


# What input size a solution can afford, assuming ~10^7 to 10^8 simple
# operations per second in Python-ish terms.
INPUT_SIZES = [
    ["n &le; 10", "O(n!), O(n &middot; n!)", "Permutations, brute-force search"],
    ["n &le; 20", "O(2<sup>n</sup>), O(n &middot; 2<sup>n</sup>)", "Subsets, bitmask DP"],
    ["n &le; 500", "O(n&sup3;)", "Floyd&ndash;Warshall, interval DP"],
    ["n &le; 5 000", "O(n&sup2;)", "2-D DP, all pairs"],
    ["n &le; 10<sup>5</sup>&ndash;10<sup>6</sup>", "O(n log n)", "Sorting, heaps, binary search on the answer"],
    ["n &le; 10<sup>7</sup>+", "O(n) or O(log n)", "One pass, two pointers, math"],
]
