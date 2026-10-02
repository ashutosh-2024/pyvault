/* GENERATED FILE - do not edit by hand.
   Source: content/prep.py   Build: python3 build.py
   Every pattern template below was executed against its check. */

window.GRAIL_PREP = {
  "patterns": [
    {
      "id": "two-pointers",
      "name": "Two pointers from both ends",
      "signals": [
        "Sorted array (or you may sort it), and you are looking for a pair or triple",
        "\"Maximise area / minimise difference\" between two positions",
        "In-place reversal or palindrome check"
      ],
      "idea": "Start at both ends. Each comparison proves one end cannot be part of any better answer, so that pointer moves inward. O(n) instead of O(n&sup2;).",
      "template": "def pair_with_sum(nums, target):          # nums sorted\n    lo, hi = 0, len(nums) - 1\n    while lo < hi:\n        s = nums[lo] + nums[hi]\n        if s == target:\n            return lo, hi\n        if s < target:\n            lo += 1          # nums[lo] is too small for every remaining partner\n        else:\n            hi -= 1          # nums[hi] is too big for every remaining partner\n    return None",
      "examples": [
        "two-sum-ii",
        "three-sum",
        "container-most-water",
        "trapping-rain-water"
      ]
    },
    {
      "id": "fast-slow",
      "name": "Fast and slow pointers",
      "signals": [
        "Linked list: find the middle, detect a cycle, find the cycle's start",
        "A function applied repeatedly that must eventually repeat (happy number, i &rarr; nums[i])"
      ],
      "idea": "The fast pointer moves two steps per slow step. In a cycle it gains one node per step, so it catches the slow pointer within one lap; without a cycle it reaches the end. When fast reaches the end, slow is at the middle.",
      "template": "def middle_and_cycle(head):\n    slow = fast = head\n    while fast and fast.next:\n        slow, fast = slow.next, fast.next.next\n        if slow is fast:\n            return \"cycle\"\n    return slow              # the middle node (second middle for even length)",
      "examples": [
        "linked-list-cycle",
        "reorder-list",
        "find-duplicate-number",
        "happy-number"
      ]
    },
    {
      "id": "sliding-window",
      "name": "Variable sliding window",
      "signals": [
        "Longest / shortest <em>contiguous</em> subarray or substring with some property",
        "The property is monotonic: extending a valid window keeps it valid, or shrinking an invalid one fixes it",
        "Non-negative numbers (with negatives, use prefix sums instead)"
      ],
      "idea": "Grow the right edge one step at a time; while the window is invalid, shrink from the left. Each index enters and leaves once, so the whole scan is O(n).",
      "template": "def longest_with_at_most_k_distinct(s, k):\n    counts, left, best = {}, 0, 0\n    for right, ch in enumerate(s):\n        counts[ch] = counts.get(ch, 0) + 1          # extend\n        while len(counts) > k:                      # invalid: shrink\n            counts[s[left]] -= 1\n            if counts[s[left]] == 0:\n                del counts[s[left]]\n            left += 1\n        best = max(best, right - left + 1)          # record the valid window\n    return best",
      "examples": [
        "longest-substring-no-repeat",
        "longest-repeating-replacement",
        "minimum-size-subarray-sum",
        "minimum-window-substring"
      ]
    },
    {
      "id": "prefix-sums",
      "name": "Prefix sums + hash map",
      "signals": [
        "Count or find subarrays with sum (or XOR, or balance) exactly k",
        "Negative numbers are allowed, so a sliding window breaks",
        "Many range-sum queries on a fixed array"
      ],
      "idea": "A subarray (i, j] sums to <code>P[j] - P[i]</code>. So a subarray ending here sums to k exactly when an earlier prefix equals <code>P - k</code>: count earlier prefixes in a hash map. Seed it with the empty prefix.",
      "template": "from collections import Counter\n\ndef count_subarrays_with_sum(nums, k):\n    seen = Counter({0: 1})           # the empty prefix\n    total = count = 0\n    for x in nums:\n        total += x\n        count += seen[total - k]     # earlier prefixes that complete a sum of k\n        seen[total] += 1\n    return count",
      "examples": [
        "subarray-sum-equals-k",
        "range-sum-query-2d",
        "path-sum-iii",
        "product-except-self"
      ]
    },
    {
      "id": "binary-search-answer",
      "name": "Binary search on the answer",
      "signals": [
        "\"Minimum X such that it is possible to ...\" or \"maximum X such that ...\"",
        "A check for a given X is easy (usually a greedy O(n) pass)",
        "Feasibility is monotonic in X"
      ],
      "idea": "Do not search an array; search the range of possible answers. If X works, every larger X works too (or smaller, for maximisation), so binary search finds the boundary with O(log range) checks.",
      "template": "def smallest_feasible(lo, hi, feasible):\n    \"\"\"Smallest x in [lo, hi] with feasible(x) true; feasible must be monotonic.\"\"\"\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if feasible(mid):\n            hi = mid             # mid works: the answer is mid or smaller\n        else:\n            lo = mid + 1\n    return lo\n\n\ndef min_eating_speed(piles, h):\n    return smallest_feasible(1, max(piles),\n                             lambda k: sum((p + k - 1) // k for p in piles) <= h)",
      "examples": [
        "koko-eating-bananas",
        "ship-within-days",
        "split-array-largest-sum",
        "sqrt-x"
      ]
    },
    {
      "id": "monotonic-stack",
      "name": "Monotonic stack",
      "signals": [
        "\"Next greater / smaller element\", \"how many days until ...\"",
        "Spans, histograms, the nearest taller bar on each side"
      ],
      "idea": "Keep indices whose values are monotonic. A new element pops everything it dominates &mdash; and for each popped element, the new one is its answer. Every index is pushed and popped once: O(n).",
      "template": "def next_greater(nums):\n    out, stack = [-1] * len(nums), []       # stack of indices, values decreasing\n    for i, x in enumerate(nums):\n        while stack and nums[stack[-1]] < x:\n            out[stack.pop()] = x            # x is the next greater for that index\n        stack.append(i)\n    return out",
      "examples": [
        "daily-temperatures",
        "online-stock-span",
        "largest-rectangle-histogram",
        "sliding-window-maximum"
      ]
    },
    {
      "id": "heap-top-k",
      "name": "Heap of size k (top-k)",
      "signals": [
        "k largest / smallest / most frequent / closest",
        "Streaming data where you keep the best k so far",
        "Merging k sorted sequences"
      ],
      "idea": "A min-heap of size k keeps the k largest items seen: whenever it grows past k, pop the smallest. O(n log k) instead of sorting everything; for k-way merges, the heap holds one head per list.",
      "template": "import heapq\n\ndef k_largest(nums, k):\n    heap = []\n    for x in nums:\n        heapq.heappush(heap, x)\n        if len(heap) > k:\n            heapq.heappop(heap)       # drop the smallest: it is not top-k\n    return sorted(heap, reverse=True)",
      "examples": [
        "kth-largest-element",
        "top-k-frequent",
        "merge-k-sorted-lists",
        "find-median-from-data-stream"
      ]
    },
    {
      "id": "bfs",
      "name": "BFS for shortest paths (and multi-source BFS)",
      "signals": [
        "Fewest steps / moves / transformations in an unweighted graph or grid",
        "Distance from every cell to the <em>nearest</em> of several sources",
        "Spreading processes that advance one step per minute"
      ],
      "idea": "A queue explores in rings of equal distance, so the first time a node is reached is along a shortest path. Mark nodes as seen when they are <em>enqueued</em>. Put every source in the queue at the start for nearest-source distances.",
      "template": "from collections import deque\n\ndef grid_distances(grid, sources):\n    \"\"\"Distance from each open cell ('.') to its nearest source; -1 if unreachable.\"\"\"\n    m, n = len(grid), len(grid[0])\n    dist = [[-1] * n for _ in range(m)]\n    queue = deque(sources)\n    for r, c in sources:\n        dist[r][c] = 0\n    while queue:\n        r, c = queue.popleft()\n        for a, b in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):\n            if 0 <= a < m and 0 <= b < n and grid[a][b] == \".\" and dist[a][b] == -1:\n                dist[a][b] = dist[r][c] + 1          # mark on enqueue\n                queue.append((a, b))\n    return dist",
      "examples": [
        "rotting-oranges",
        "walls-and-gates",
        "open-the-lock",
        "word-ladder"
      ]
    },
    {
      "id": "dfs-flood",
      "name": "DFS / flood fill",
      "signals": [
        "Count or measure connected regions (islands, provinces)",
        "Anything reachable from X: \"can water flow ...\", \"which cells are safe\""
      ],
      "idea": "From each unvisited start, visit everything reachable and mark it. Use an explicit stack in Python: recursion depth can exceed the 1000-frame limit on large grids.",
      "template": "def count_regions(grid):\n    m, n = len(grid), len(grid[0])\n    seen, regions = set(), 0\n    for r in range(m):\n        for c in range(n):\n            if grid[r][c] == \"1\" and (r, c) not in seen:\n                regions += 1\n                stack = [(r, c)]\n                seen.add((r, c))\n                while stack:\n                    x, y = stack.pop()\n                    for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):\n                        if 0 <= a < m and 0 <= b < n and grid[a][b] == \"1\" and (a, b) not in seen:\n                            seen.add((a, b))\n                            stack.append((a, b))\n    return regions",
      "examples": [
        "number-of-islands",
        "max-area-of-island",
        "pacific-atlantic",
        "surrounded-regions"
      ]
    },
    {
      "id": "topological-sort",
      "name": "Topological sort (Kahn)",
      "signals": [
        "Prerequisites, build order, task dependencies",
        "\"Is there a valid order?\" = \"is this directed graph acyclic?\"",
        "Ordering constraints hidden in data (alien dictionary)"
      ],
      "idea": "Repeatedly take a node with no remaining incoming edges and remove its edges. If every node is taken, the order is valid; leftovers mean a cycle.",
      "template": "from collections import defaultdict, deque\n\ndef topo_order(n, edges):              # edge (a, b): a must come before b\n    adj, indeg = defaultdict(list), [0] * n\n    for a, b in edges:\n        adj[a].append(b)\n        indeg[b] += 1\n    queue = deque(v for v in range(n) if indeg[v] == 0)\n    order = []\n    while queue:\n        u = queue.popleft()\n        order.append(u)\n        for v in adj[u]:\n            indeg[v] -= 1\n            if indeg[v] == 0:\n                queue.append(v)\n    return order if len(order) == n else []     # [] means a cycle",
      "examples": [
        "course-schedule",
        "course-schedule-ii",
        "alien-dictionary",
        "minimum-height-trees"
      ]
    },
    {
      "id": "union-find",
      "name": "Union-find",
      "signals": [
        "Edges arrive one at a time and you need connectivity after each",
        "Detect the edge that creates a cycle; count components",
        "Grouping by a transitive relation (accounts sharing an email)"
      ],
      "idea": "Each set is a tree; <code>find</code> walks to the root (compressing the path), <code>union</code> links roots (smaller under larger). Both are effectively O(1).",
      "template": "class DSU:\n    def __init__(self, n):\n        self.parent, self.size = list(range(n)), [1] * n\n\n    def find(self, x):\n        while self.parent[x] != x:\n            self.parent[x] = self.parent[self.parent[x]]   # path halving\n            x = self.parent[x]\n        return x\n\n    def union(self, a, b):\n        ra, rb = self.find(a), self.find(b)\n        if ra == rb:\n            return False                                  # already connected\n        if self.size[ra] < self.size[rb]:\n            ra, rb = rb, ra\n        self.parent[rb] = ra\n        self.size[ra] += self.size[rb]\n        return True",
      "examples": [
        "count-connected-components",
        "redundant-connection",
        "accounts-merge",
        "graph-valid-tree"
      ]
    },
    {
      "id": "backtracking",
      "name": "Backtracking",
      "signals": [
        "\"Return all\" subsets / permutations / combinations / partitions / boards",
        "Small input (n &le; 20), exponential output",
        "Constraint puzzles: N-Queens, Sudoku, word search"
      ],
      "idea": "Choose an option, recurse, un-choose. Prune a branch as soon as it cannot lead to a valid answer. Skip equal values at the same depth (after sorting) to avoid duplicate answers.",
      "template": "def subsets_without_duplicates(nums):\n    nums, out, path = sorted(nums), [], []\n\n    def dfs(start):\n        out.append(path[:])                       # every node is an answer here\n        for i in range(start, len(nums)):\n            if i > start and nums[i] == nums[i - 1]:\n                continue                          # same value, same depth: skip\n            path.append(nums[i])                  # choose\n            dfs(i + 1)                            # explore\n            path.pop()                            # un-choose\n\n    dfs(0)\n    return out",
      "examples": [
        "subsets",
        "combination-sum-ii",
        "permutations-ii",
        "n-queens"
      ]
    },
    {
      "id": "dp-1d",
      "name": "1-D dynamic programming",
      "signals": [
        "\"Number of ways\", \"minimum cost\", \"maximum value\" over a sequence",
        "The answer at i depends on a few earlier answers",
        "A brute-force recursion that recomputes the same arguments"
      ],
      "idea": "Name the state (<em>best answer for the prefix ending at i</em>), write the recurrence, fill it in order. If i only reads i-1 and i-2, two variables replace the table.",
      "template": "def house_robber(nums):\n    take, skip = 0, 0                     # best ending at i with / without robbing i\n    for x in nums:\n        take, skip = skip + x, max(take, skip)\n    return max(take, skip)\n\n\ndef coin_change(coins, amount):\n    INF = float(\"inf\")\n    dp = [0] + [INF] * amount             # dp[a] = fewest coins to make a\n    for a in range(1, amount + 1):\n        for c in coins:\n            if c <= a and dp[a - c] + 1 < dp[a]:\n                dp[a] = dp[a - c] + 1\n    return dp[amount] if dp[amount] < INF else -1",
      "examples": [
        "climbing-stairs",
        "house-robber",
        "coin-change",
        "longest-increasing-subsequence"
      ]
    },
    {
      "id": "dp-2d",
      "name": "2-D dynamic programming on two strings or a grid",
      "signals": [
        "Two strings compared position by position (edit distance, LCS)",
        "Paths through a grid moving right/down",
        "State needs two indices"
      ],
      "idea": "<code>dp[i][j]</code> describes the prefixes <code>a[:i]</code> and <code>b[:j]</code> (or cell (i, j)). Each cell reads its left, upper and upper-left neighbours, so one rolling row is enough memory.",
      "template": "def lcs(a, b):\n    prev = [0] * (len(b) + 1)             # one row: dp[i-1][*]\n    for ch in a:\n        cur = [0]\n        for j, other in enumerate(b, 1):\n            cur.append(prev[j - 1] + 1 if ch == other else max(prev[j], cur[j - 1]))\n        prev = cur\n    return prev[-1]",
      "examples": [
        "longest-common-subsequence",
        "edit-distance",
        "unique-paths",
        "interleaving-string"
      ]
    },
    {
      "id": "tree-postorder",
      "name": "Tree recursion: return one thing, record another",
      "signals": [
        "Any-node-to-any-node paths in a tree (diameter, max path sum)",
        "A node needs both children's answers first (postorder)",
        "Include/exclude choices per node (house robber on a tree)"
      ],
      "idea": "Each call returns what its <em>parent</em> needs (a height, the best single arm, a pair of states), and separately updates a global answer with the best path that bends at this node.",
      "template": "def diameter(root):\n    best = 0\n\n    def height(node):\n        nonlocal best\n        if node is None:\n            return 0\n        l, r = height(node.left), height(node.right)\n        best = max(best, l + r)           # path bending here: the answer\n        return 1 + max(l, r)              # what the parent can extend\n\n    height(root)\n    return best",
      "examples": [
        "diameter-of-binary-tree",
        "binary-tree-maximum-path-sum",
        "house-robber-iii",
        "lca-binary-tree"
      ]
    },
    {
      "id": "intervals",
      "name": "Sort intervals, then sweep",
      "signals": [
        "Merge / insert / count overlapping intervals",
        "Meeting rooms, scheduling, minimum removals"
      ],
      "idea": "Sort by start (to merge) or by end (to select the most non-overlapping). After sorting, only the last kept interval can overlap the next one.",
      "template": "def merge(intervals):\n    out = []\n    for s, e in sorted(intervals):\n        if out and s <= out[-1][1]:\n            out[-1][1] = max(out[-1][1], e)   # overlap: extend (may be contained)\n        else:\n            out.append([s, e])\n    return out",
      "examples": [
        "merge-intervals",
        "insert-interval",
        "non-overlapping-intervals",
        "meeting-rooms-ii"
      ]
    },
    {
      "id": "dijkstra",
      "name": "Dijkstra (weighted shortest paths)",
      "signals": [
        "Weighted edges, non-negative weights, cheapest path",
        "\"Minimise the maximum step\" (use max instead of +)"
      ],
      "idea": "Pop the closest unsettled node from a min-heap; its distance is final. Relax its edges. Skip stale heap entries instead of decreasing keys.",
      "template": "import heapq\n\ndef dijkstra(adj, src):              # adj[u] = [(v, w), ...]\n    dist, heap = {}, [(0, src)]\n    while heap:\n        d, u = heapq.heappop(heap)\n        if u in dist:\n            continue                 # stale entry\n        dist[u] = d\n        for v, w in adj.get(u, []):\n            if v not in dist:\n                heapq.heappush(heap, (d + w, v))\n    return dist",
      "examples": [
        "network-delay-time",
        "path-minimum-effort",
        "swim-rising-water",
        "cheapest-flights-k-stops"
      ]
    },
    {
      "id": "trie",
      "name": "Trie",
      "signals": [
        "Many prefix queries, autocomplete",
        "Searching a grid or string for many words at once"
      ],
      "idea": "A tree of characters where shared prefixes share a path. Lookups cost O(length of the query), independent of how many words are stored.",
      "template": "def build_trie(words):\n    root = {}\n    for w in words:\n        node = root\n        for ch in w:\n            node = node.setdefault(ch, {})\n        node[\"$\"] = w                 # end of a word\n    return root\n\n\ndef has_prefix(root, prefix):\n    node = root\n    for ch in prefix:\n        if ch not in node:\n            return False\n        node = node[ch]\n    return True",
      "examples": [
        "implement-trie",
        "add-search-words",
        "word-search-ii",
        "extra-characters-string"
      ]
    },
    {
      "id": "bits",
      "name": "Bit tricks",
      "signals": [
        "Every element appears twice except one",
        "Subsets of a small set (n &le; 20) as integers",
        "\"Without + / -\", \"count set bits\""
      ],
      "idea": "<code>x ^ x = 0</code> cancels pairs; <code>x &amp; (x - 1)</code> clears the lowest set bit; <code>x &amp; -x</code> isolates it; bit i of a mask says whether item i is in the subset.",
      "template": "def single_number(nums):\n    r = 0\n    for x in nums:\n        r ^= x                        # pairs cancel\n    return r\n\n\ndef popcount(x):\n    c = 0\n    while x:\n        x &= x - 1                    # drop the lowest set bit\n        c += 1\n    return c",
      "examples": [
        "single-number",
        "counting-bits",
        "missing-number",
        "sum-of-two-integers"
      ]
    },
    {
      "id": "fenwick",
      "name": "Fenwick tree (count while you scan)",
      "signals": [
        "Range sums with point updates mixed in",
        "\"How many earlier elements are smaller / larger than this one?\"",
        "Count pairs i &lt; j with an inequality between a[i] and a[j]"
      ],
      "idea": "Index <code>i</code> stores a block ending at <code>i</code> of length <code>i &amp; -i</code>. Prefix query strips the lowest bit, update adds it: both O(log n). For pair counting, compress values to ranks and scan, querying before inserting.",
      "template": "class Fenwick:\n    def __init__(self, n):\n        self.tree = [0] * (n + 1)          # 1-indexed\n\n    def add(self, i, delta=1):\n        while i < len(self.tree):\n            self.tree[i] += delta\n            i += i & -i\n\n    def prefix(self, i):                   # sum of positions 1..i\n        s = 0\n        while i > 0:\n            s += self.tree[i]\n            i -= i & -i\n        return s\n\n\ndef count_smaller_after(nums):\n    rank = {v: i + 1 for i, v in enumerate(sorted(set(nums)))}\n    bit, out = Fenwick(len(rank)), []\n    for x in reversed(nums):\n        out.append(bit.prefix(rank[x] - 1))\n        bit.add(rank[x])\n    return out[::-1]",
      "examples": [
        "range-sum-query-mutable",
        "count-of-smaller-numbers-after-self",
        "reverse-pairs",
        "count-of-range-sum"
      ]
    },
    {
      "id": "segment-tree",
      "name": "Segment tree (range min / max)",
      "signals": [
        "Range queries with an operation that has no inverse: min, max, gcd",
        "Range updates (\"set / add to every element in [l, r]\") - needs lazy propagation",
        "A DP whose transition is a max over a sliding range of values"
      ],
      "idea": "Leaves at <code>tree[n..2n)</code>, node <code>i</code> combines <code>2i</code> and <code>2i+1</code>. Any range splits into O(log n) nodes. The iterative version is short; switch the combine function and it becomes min, max or sum.",
      "template": "class SegTree:\n    def __init__(self, values, combine=max, identity=float(\"-inf\")):\n        self.n, self.f, self.e = len(values), combine, identity\n        self.t = [identity] * self.n + list(values)\n        for i in range(self.n - 1, 0, -1):\n            self.t[i] = combine(self.t[2 * i], self.t[2 * i + 1])\n\n    def set(self, i, v):\n        i += self.n\n        self.t[i] = v\n        while i > 1:\n            i //= 2\n            self.t[i] = self.f(self.t[2 * i], self.t[2 * i + 1])\n\n    def query(self, l, r):                 # combine over [l, r)\n        res, l, r = self.e, l + self.n, r + self.n\n        while l < r:\n            if l & 1:\n                res = self.f(res, self.t[l]); l += 1\n            if r & 1:\n                r -= 1; res = self.f(res, self.t[r])\n            l //= 2; r //= 2\n        return res",
      "examples": [
        "longest-increasing-subsequence-ii",
        "falling-squares",
        "range-sum-query-mutable"
      ]
    },
    {
      "id": "kmp",
      "name": "KMP prefix function (borders)",
      "signals": [
        "Substring search with a guaranteed O(n + m)",
        "\"Longest prefix that is also a suffix\", shortest period, repeated pattern",
        "Longest palindromic prefix (border of <code>s + \"#\" + reverse(s)</code>)"
      ],
      "idea": "<code>pi[i]</code> = longest proper border of <code>s[:i+1]</code>. On a mismatch fall back to <code>pi[k-1]</code> instead of restarting; the text pointer never moves back. <code>n - pi[-1]</code> is the shortest period.",
      "template": "def prefix_function(s):\n    pi, k = [0] * len(s), 0\n    for i in range(1, len(s)):\n        while k and s[i] != s[k]:\n            k = pi[k - 1]                  # border of the border\n        if s[i] == s[k]:\n            k += 1\n        pi[i] = k\n    return pi\n\n\ndef kmp_find(text, pat):\n    pi, k = prefix_function(pat), 0\n    for i, ch in enumerate(text):\n        while k and ch != pat[k]:\n            k = pi[k - 1]\n        if ch == pat[k]:\n            k += 1\n        if k == len(pat):\n            return i - k + 1\n    return -1",
      "examples": [
        "find-first-occurrence",
        "repeated-substring-pattern",
        "longest-happy-prefix",
        "shortest-palindrome"
      ]
    },
    {
      "id": "rolling-hash",
      "name": "Rolling hash (Rabin-Karp)",
      "signals": [
        "Compare many substrings of the same length",
        "\"Longest repeated / common substring\" (binary search on the length)",
        "You need O(1) substring equality after O(n) preprocessing"
      ],
      "idea": "Prefix hashes <code>H[i+1] = H[i]&middot;B + s[i]</code> mod a big prime give any substring's hash in O(1): <code>H[r] - H[l]&middot;B<sup>r-l</sup></code>. Equal hashes mean <em>probably</em> equal &mdash; verify on a hit when correctness matters.",
      "template": "import random\n\nclass Hasher:\n    MOD = (1 << 61) - 1\n\n    def __init__(self, s):\n        B = random.randrange(256, 1 << 40)\n        self.h, self.p = [0], [1]\n        for ch in s:\n            self.h.append((self.h[-1] * B + ord(ch)) % self.MOD)\n            self.p.append(self.p[-1] * B % self.MOD)\n\n    def get(self, l, r):                   # hash of s[l:r]\n        return (self.h[r] - self.h[l] * self.p[r - l]) % self.MOD",
      "examples": [
        "longest-duplicate-substring",
        "find-first-occurrence",
        "longest-happy-prefix"
      ]
    }
  ],
  "complexity": [
    {
      "title": "list",
      "note": "A dynamic array. Appending and popping at the end are cheap; anything at the front or middle shifts elements.",
      "rows": [
        [
          "<code>x[i]</code>, <code>x[i] = v</code>, <code>len(x)</code>",
          "O(1)",
          ""
        ],
        [
          "<code>x.append(v)</code>, <code>x.pop()</code>",
          "O(1) amortised",
          "Occasional resize copies everything"
        ],
        [
          "<code>x.pop(0)</code>, <code>x.insert(0, v)</code>",
          "O(n)",
          "Use <code>collections.deque</code>"
        ],
        [
          "<code>x.pop(i)</code>, <code>x.insert(i, v)</code>, <code>del x[i]</code>",
          "O(n - i)",
          ""
        ],
        [
          "<code>v in x</code>, <code>x.index(v)</code>, <code>x.count(v)</code>, <code>x.remove(v)</code>",
          "O(n)",
          "Use a set for membership"
        ],
        [
          "<code>x[a:b]</code>",
          "O(b - a)",
          "Slicing copies"
        ],
        [
          "<code>x + y</code>, <code>x.extend(y)</code>",
          "O(len(x) + k), O(k)",
          ""
        ],
        [
          "<code>x.sort()</code>, <code>sorted(x)</code>",
          "O(n log n)",
          "Timsort: O(n) on already-sorted runs, stable"
        ],
        [
          "<code>min(x)</code>, <code>max(x)</code>, <code>sum(x)</code>",
          "O(n)",
          ""
        ],
        [
          "<code>x.reverse()</code>, <code>x[::-1]</code>",
          "O(n)",
          ""
        ]
      ]
    },
    {
      "title": "dict and set",
      "note": "Hash tables. Average costs assume a reasonable hash; adversarial keys can make any operation O(n).",
      "rows": [
        [
          "<code>d[k]</code>, <code>d[k] = v</code>, <code>del d[k]</code>, <code>k in d</code>",
          "O(1) average",
          "O(n) worst"
        ],
        [
          "<code>s.add(v)</code>, <code>s.remove(v)</code>, <code>v in s</code>",
          "O(1) average",
          ""
        ],
        [
          "<code>s | t</code>, <code>s &amp; t</code>, <code>s - t</code>",
          "O(len(s) + len(t)), O(min), O(len(s))",
          "Intersection iterates the smaller set"
        ],
        [
          "Iterating",
          "O(n)",
          "dicts keep insertion order (3.7+)"
        ],
        [
          "<code>Counter(iterable)</code>",
          "O(n)",
          "<code>most_common(k)</code> is O(n log k)"
        ],
        [
          "Key or element hashing",
          "O(len) for str/tuple",
          "Strings cache their hash after the first time"
        ]
      ]
    },
    {
      "title": "collections.deque",
      "note": "A doubly linked list of blocks: cheap at both ends, slow in the middle.",
      "rows": [
        [
          "<code>append</code>, <code>appendleft</code>, <code>pop</code>, <code>popleft</code>",
          "O(1)",
          "Use for queues and BFS"
        ],
        [
          "<code>q[i]</code>",
          "O(n)",
          "O(1) near the ends"
        ],
        [
          "<code>rotate(k)</code>",
          "O(k)",
          ""
        ]
      ]
    },
    {
      "title": "heapq",
      "note": "A binary min-heap stored in a plain list. For a max-heap, push negated values.",
      "rows": [
        [
          "<code>heapify(x)</code>",
          "O(n)",
          "Faster than n pushes"
        ],
        [
          "<code>heappush</code>, <code>heappop</code>, <code>heappushpop</code>",
          "O(log n)",
          ""
        ],
        [
          "<code>x[0]</code> (peek)",
          "O(1)",
          ""
        ],
        [
          "<code>nlargest(k, it)</code>, <code>nsmallest(k, it)</code>",
          "O(n log k)",
          ""
        ],
        [
          "Remove an arbitrary item",
          "O(n)",
          "Use lazy deletion instead"
        ]
      ]
    },
    {
      "title": "str",
      "note": "Immutable. Every \"modification\" builds a new string.",
      "rows": [
        [
          "<code>s[i]</code>, <code>len(s)</code>",
          "O(1)",
          ""
        ],
        [
          "<code>s + t</code>",
          "O(len(s) + len(t))",
          "Concatenating in a loop is O(n&sup2;); join a list instead"
        ],
        [
          "<code>\"\".join(parts)</code>",
          "O(total length)",
          ""
        ],
        [
          "<code>t in s</code>, <code>s.find(t)</code>",
          "O(len(s) &middot; len(t)) worst",
          "Usually much faster in practice"
        ],
        [
          "<code>s[a:b]</code>, <code>s[::-1]</code>",
          "O(b - a), O(n)",
          ""
        ],
        [
          "<code>s.split()</code>, <code>s.replace()</code>, <code>s.lower()</code>",
          "O(n)",
          ""
        ]
      ]
    },
    {
      "title": "bisect, sorting helpers, math",
      "note": "",
      "rows": [
        [
          "<code>bisect_left</code>, <code>bisect_right</code>",
          "O(log n)",
          "On a sorted list"
        ],
        [
          "<code>insort(x, v)</code>",
          "O(n)",
          "The search is O(log n); the insert shifts"
        ],
        [
          "<code>math.gcd(a, b)</code>",
          "O(log min(a, b))",
          ""
        ],
        [
          "<code>pow(a, b, m)</code>",
          "O(log b)",
          "Built-in modular exponentiation"
        ],
        [
          "<code>math.comb(n, k)</code>, big-integer multiply",
          "super-linear in digits",
          "Python ints are arbitrary precision"
        ],
        [
          "<code>functools.cache</code> lookup",
          "O(1) average + hashing the arguments",
          ""
        ]
      ]
    }
  ],
  "sizes": [
    [
      "n &le; 10",
      "O(n!), O(n &middot; n!)",
      "Permutations, brute-force search"
    ],
    [
      "n &le; 20",
      "O(2<sup>n</sup>), O(n &middot; 2<sup>n</sup>)",
      "Subsets, bitmask DP"
    ],
    [
      "n &le; 500",
      "O(n&sup3;)",
      "Floyd&ndash;Warshall, interval DP"
    ],
    [
      "n &le; 5 000",
      "O(n&sup2;)",
      "2-D DP, all pairs"
    ],
    [
      "n &le; 10<sup>5</sup>&ndash;10<sup>6</sup>",
      "O(n log n)",
      "Sorting, heaps, binary search on the answer"
    ],
    [
      "n &le; 10<sup>7</sup>+",
      "O(n) or O(log n)",
      "One pass, two pointers, math"
    ]
  ]
};
