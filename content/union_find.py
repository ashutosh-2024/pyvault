# -*- coding: utf-8 -*-
"""Union Find (DSU) topic: the NeetCode 250 graph problems whose natural
solution is a disjoint-set union (261, 323, 684, 721, 2709). Same build
contract as content/dsa.py."""

PRELUDE_UF = '''import math
import random
from collections import defaultdict, deque
'''


UNION_FIND_TOPIC = dict(
    id="union-find",
    title="Union Find (DSU)",
    prelude=PRELUDE_UF,
    sections=[

dict(
    id="union-find",
    title="Disjoint-set union",
    idea=[
        "Union-find keeps a forest in which each tree is one group. <code>find(x)</code> walks to x's root; <code>union(a, b)</code> hangs one root under the other. With <strong>path compression</strong> (point nodes at their root as you walk) and <strong>union by rank or size</strong> (hang the smaller tree under the larger), both are effectively O(1) &mdash; O(&alpha;(n)), where &alpha; is the inverse Ackermann function, below 5 for any input that fits in the universe.",
        "Each problem here also has a BFS/DFS solution. DSU wins when edges arrive one at a time and you need to know, at each moment, whether two things are already connected.",
    ],
    problems=[

    # ------------------------------------------------------------------ 323
    dict(
        id="count-connected-components",
        lc=323, slug="number-of-connected-components-in-an-undirected-graph",
        name="Number of Connected Components in an Undirected Graph",
        difficulty="medium",
        tags=["Depth-First Search", "Breadth-First Search", "Union Find", "Graph"],
        statement=[
            "You have <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and a list of undirected <code>edges</code>. Return the number of connected components.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="n = 5, edges = [[0,1],[1,2],[3,4]]", output="2"),
            dict(input="n = 5, edges = [[0,1],[1,2],[2,3],[3,4]]", output="1"),
        ],
        constraints=[
            "<code>1 &lt;= n &lt;= 2000</code>, <code>0 &lt;= edges.length &lt;= 5000</code>",
            "No self-loops or repeated edges",
        ],
        approaches=[
            dict(
                name="DFS from every unvisited node",
                time="O(V + E)",
                space="O(V + E)",
                why=[
                    "Build an adjacency list. Each time you find an unvisited node, that is a new component: flood it with DFS (iterative, to avoid recursion limits), marking everything reachable. Count the floods.",
                ],
                code='''def count_components(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen, count = [False] * n, 0
    for start in range(n):
        if seen[start]:
            continue
        count += 1
        seen[start] = True
        stack = [start]
        while stack:
            for nb in adj[stack.pop()]:
                if not seen[nb]:
                    seen[nb] = True
                    stack.append(nb)
    return count''',
            ),
            dict(
                name="Union-find, one decrement per successful union",
                time="O(V + E &middot; &alpha;(V))",
                space="O(V)",
                best=True,
                why=[
                    "Start with n singleton components. Each edge that joins two <em>different</em> roots merges two components, so decrement the count; an edge inside one component changes nothing. No adjacency list is built &mdash; edges can be processed as a stream.",
                    "Path compression (here, the compact <em>path halving</em> form: point each node at its grandparent while walking) plus union by size keeps every operation near O(1).",
                ],
                code='''def count_components(n, edges):
    parent, size = list(range(n)), [1] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]        # path halving
            x = parent[x]
        return x

    count = n
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra                      # smaller tree under larger
            size[ra] += size[rb]
            count -= 1
    return count''',
            ),
        ],
        tests='''assert count_components(5, [[0, 1], [1, 2], [3, 4]]) == 2
assert count_components(5, [[0, 1], [1, 2], [2, 3], [3, 4]]) == 1
assert count_components(3, []) == 3
rng = random.Random(0)
for _ in range(50):
    n = rng.randint(1, 10)
    edges = list({tuple(sorted(rng.sample(range(n), 2))) for _ in range(rng.randint(0, n))}) if n > 1 else []
    label = list(range(n))
    for _ in range(n):
        for a, b in edges:
            label[a] = label[b] = min(label[a], label[b])
    assert count_components(n, [list(e) for e in edges]) == len(set(label))''',
    ),

    # ------------------------------------------------------------------ 261
    dict(
        id="graph-valid-tree",
        lc=261, slug="graph-valid-tree",
        name="Graph Valid Tree",
        difficulty="medium",
        tags=["Depth-First Search", "Breadth-First Search", "Union Find", "Graph"],
        statement=[
            "Given <code>n</code> nodes labelled <code>0</code> to <code>n - 1</code> and a list of undirected <code>edges</code>, return <code>true</code> if the edges form a valid tree.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="n = 5, edges = [[0,1],[0,2],[0,3],[1,4]]", output="true"),
            dict(input="n = 5, edges = [[0,1],[1,2],[2,3],[1,3],[1,4]]", output="false",
                 explanation="1-2-3 forms a cycle."),
        ],
        constraints=[
            "<code>1 &lt;= n &lt;= 2000</code>, <code>0 &lt;= edges.length &lt;= 5000</code>",
            "No self-loops or repeated edges",
        ],
        approaches=[
            dict(
                name="Edge count, then DFS for connectivity",
                time="O(V + E)",
                space="O(V + E)",
                why=[
                    "A graph on n nodes is a tree exactly when it has <strong>n - 1 edges</strong> and is <strong>connected</strong> (either condition plus \"acyclic\" also works). Check the count first &mdash; it rejects most bad inputs in O(1) &mdash; then DFS from node 0 and check that every node was reached.",
                ],
                code='''def valid_tree(n, edges):
    if len(edges) != n - 1:
        return False
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen, stack = {0}, [0]
    while stack:
        for nb in adj[stack.pop()]:
            if nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == n''',
            ),
            dict(
                name="Edge count, then union-find for cycles",
                time="O(V + E &middot; &alpha;(V))",
                space="O(V)",
                best=True,
                why=[
                    "With exactly n - 1 edges, the graph is a tree if and only if it has no cycle. An edge whose endpoints already share a root would close a cycle. If all n - 1 unions succeed, there is no cycle, and n - 1 successful unions leave exactly one component.",
                ],
                code='''def valid_tree(n, edges):
    if len(edges) != n - 1:
        return False
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False                         # this edge closes a cycle
        parent[ra] = rb
    return True''',
            ),
        ],
        tests='''assert valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]) is True
assert valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]) is False
assert valid_tree(1, []) is True
assert valid_tree(4, [[0, 1], [2, 3]]) is False
rng = random.Random(1)
for _ in range(60):
    n = rng.randint(1, 7)
    edges = list({tuple(sorted(rng.sample(range(n), 2))) for _ in range(rng.randint(0, n))}) if n > 1 else []
    label = list(range(n))
    for _ in range(n):
        for a, b in edges:
            label[a] = label[b] = min(label[a], label[b])
    assert valid_tree(n, [list(e) for e in edges]) is (len(edges) == n - 1 and len(set(label)) == 1)''',
    ),

    # ------------------------------------------------------------------ 684
    dict(
        id="redundant-connection",
        lc=684, slug="redundant-connection",
        name="Redundant Connection",
        difficulty="medium",
        framing=[
            "A tree on nodes 1..n had one extra edge added. Return an edge whose removal leaves a tree; if several qualify, the one appearing <strong>last</strong> in the input. Processing edges in order, the first edge that connects two already-connected nodes is exactly that answer &mdash; union-find's home turf.",
        ],
        approaches=[
            dict(
                name="For each edge, DFS to see if it is already connected",
                time="O(n&sup2;)",
                space="O(n)",
                why=[
                    "Add edges one at a time. Before adding <code>(a, b)</code>, DFS from a in the graph built so far; if b is reachable, this edge closes a cycle. Each DFS is O(n), done n times.",
                ],
                code='''def find_redundant_connection(edges):
    adj = defaultdict(list)
    for a, b in edges:
        seen, stack = {a}, [a]
        while stack:
            for nb in adj[stack.pop()]:
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        if b in seen:
            return [a, b]
        adj[a].append(b)
        adj[b].append(a)''',
            ),
            dict(
                name="Peel leaves until only the cycle remains",
                time="O(n)",
                space="O(n)",
                why=[
                    "Build the whole graph. A node of degree 1 cannot be on a cycle, so remove it and decrement its neighbour's degree; repeat (a queue, like topological sort). Since the graph is a tree plus one edge, what survives is exactly the single cycle. Return the cycle edge that appears last in the input.",
                    "Linear time, and a nice illustration that &ldquo;remove what cannot matter&rdquo; works on graphs too &mdash; but it needs the whole graph up front, while DSU handles edges as they arrive.",
                ],
                code='''def find_redundant_connection(edges):
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    degree = {v: len(nb) for v, nb in adj.items()}
    queue = deque(v for v, d in degree.items() if d == 1)
    removed = set()
    while queue:
        v = queue.popleft()
        removed.add(v)
        for nb in adj[v]:
            if nb not in removed:
                degree[nb] -= 1
                if degree[nb] == 1:
                    queue.append(nb)
    for a, b in reversed(edges):
        if a not in removed and b not in removed:
            return [a, b]''',
            ),
            dict(
                name="Union-find: the first edge inside one set",
                time="O(n &middot; &alpha;(n))",
                space="O(n)",
                best=True,
                why=[
                    "Union edges in input order. The first edge whose endpoints already share a root closes the cycle. Every other cycle edge came earlier, so this one is the last cycle edge in the input &mdash; exactly the tie-break the problem asks for.",
                ],
                code='''def find_redundant_connection(edges):
    parent = list(range(len(edges) + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            return [a, b]
        parent[ra] = rb''',
            ),
        ],
        tests='''assert find_redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
assert find_redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]
rng = random.Random(2)
for _ in range(60):
    n = rng.randint(3, 9)
    nodes = list(range(1, n + 1)); rng.shuffle(nodes)
    tree = [[nodes[i], nodes[rng.randrange(i)]] for i in range(1, n)]
    existing = {tuple(sorted(e)) for e in tree}
    extra = next(list(p) for p in ((a, b) for a in range(1, n + 1) for b in range(a + 1, n + 1)) if p not in existing)
    edges = tree + [extra]
    rng.shuffle(edges)
    got = find_redundant_connection([e[:] for e in edges])
    rest = [e for e in edges if e != got]
    label = {v: v for v in range(1, n + 1)}
    for _ in range(n):
        for a, b in rest:
            label[a] = label[b] = min(label[a], label[b])
    assert len(set(label.values())) == 1
    cycle_edges = []
    for i, e in enumerate(edges):
        others = edges[:i] + edges[i + 1:]
        lab = {v: v for v in range(1, n + 1)}
        for _ in range(n):
            for a, b in others:
                lab[a] = lab[b] = min(lab[a], lab[b])
        if len(set(lab.values())) == 1:
            cycle_edges.append(e)
    assert got == cycle_edges[-1]''',
    ),

    # ------------------------------------------------------------------ 721
    dict(
        id="accounts-merge",
        lc=721, slug="accounts-merge",
        name="Accounts Merge",
        difficulty="medium",
        framing=[
            "Each account is a name plus some emails. Two accounts belong to the same person if they share <em>any</em> email (and sharing is transitive). Merge them and return each person's name with their emails sorted. Emails are the nodes; each account connects its emails into one group.",
        ],
        approaches=[
            dict(
                name="Email graph, DFS per component",
                time="O(N log N)",
                space="O(N)",
                why=[
                    "Connect each account's first email to each of its other emails. Every connected component of this graph is one person. DFS each component, sort its emails. N is the total number of emails; sorting dominates.",
                ],
                code='''def accounts_merge(accounts):
    adj, owner = defaultdict(list), {}
    for name, *emails in accounts:
        for e in emails:
            owner[e] = name
            adj[emails[0]].append(e)
            adj[e].append(emails[0])
    seen, out = set(), []
    for e in owner:
        if e in seen:
            continue
        seen.add(e)
        stack, group = [e], []
        while stack:
            x = stack.pop()
            group.append(x)
            for nb in adj[x]:
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        out.append([owner[e]] + sorted(group))
    return out''',
            ),
            dict(
                name="Union-find over account indices",
                time="O(N log N)",
                space="O(N)",
                best=True,
                why=[
                    "Map each email to the first account index that listed it. When a later account lists the same email, union the two accounts. Afterwards, group every email under its account's root and sort. Working with account indices keeps the DSU small (one node per account, not per email).",
                ],
                code='''def accounts_merge(accounts):
    parent = list(range(len(accounts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    first_owner = {}
    for i, (_, *emails) in enumerate(accounts):
        for e in emails:
            if e in first_owner:
                parent[find(i)] = find(first_owner[e])
            else:
                first_owner[e] = i
    groups = defaultdict(list)
    for e, i in first_owner.items():
        groups[find(i)].append(e)
    return [[accounts[root][0]] + sorted(es) for root, es in groups.items()]''',
            ),
        ],
        tests='''acc = [["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"],
       ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]]
assert sorted(accounts_merge(acc)) == sorted([["John", "john00@mail.com", "john_newyork@mail.com", "johnsmith@mail.com"],
                                               ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]])
rng = random.Random(3)
for _ in range(40):
    accs = []
    for _ in range(rng.randint(1, 6)):
        who = rng.randint(0, 2)
        accs.append([f"n{who}"] + list({f"{who}_{rng.randint(0, 3)}" for _ in range(rng.randint(1, 3))}))
    groups = [set(a[1:]) for a in accs]
    names = [a[0] for a in accs]
    merged = True
    while merged:
        merged = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if groups[i] & groups[j]:
                    groups[i] |= groups.pop(j); names.pop(j); merged = True; break
            if merged:
                break
    expect = sorted([n] + sorted(g) for n, g in zip(names, groups))
    assert sorted(accounts_merge([a[:] for a in accs])) == expect''',
    ),

    # ------------------------------------------------------------------ 2709
    dict(
        id="gcd-traversal",
        lc=2709, slug="greatest-common-divisor-traversal",
        name="Greatest Common Divisor Traversal",
        difficulty="hard",
        framing=[
            "You can move between indices i and j when <code>gcd(nums[i], nums[j]) &gt; 1</code>. Can every pair of indices reach each other? That asks whether one graph is connected &mdash; but it has up to n&sup2; edges. The trick is to connect numbers through their <strong>prime factors</strong> instead of to each other: two numbers share a factor exactly when they share a prime.",
        ],
        pitfall="Missing the edge cases around 1: a single element is always connected, but any 1 in an array of two or more elements can never move anywhere.",
        approaches=[
            dict(
                name="Union every pair with gcd &gt; 1",
                time="O(n&sup2; log max)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Check every pair's gcd and union the ones that share a factor; answer whether one set remains. Correct, but 10<sup>5</sup> elements means 5 &times; 10<sup>9</sup> gcd calls.",
                ],
                code='''def can_traverse_all_pairs(nums):
    n = len(nums)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if math.gcd(nums[i], nums[j]) > 1:
                parent[find(i)] = find(j)
    return len({find(i) for i in range(n)}) == 1''',
            ),
            dict(
                name="Union each index with its prime factors",
                time="O(n &radic;max)",
                space="O(n + primes)",
                why=[
                    "Factor each number by trial division up to its square root, and union the index with a node for each prime factor (offset so primes and indices do not collide). Indices sharing a prime end up in the same set. At most about 6 distinct primes per number below 10<sup>5</sup>, so unions are cheap; factoring costs &radic;max per number.",
                ],
                code='''def can_traverse_all_pairs(nums):
    n = len(nums)
    if n == 1:
        return True
    if 1 in nums:
        return False
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, v in enumerate(nums):
        p = 2
        while p * p <= v:
            if v % p == 0:
                parent[find(("p", p))] = find(i)
                while v % p == 0:
                    v //= p
            p += 1
        if v > 1:
            parent[find(("p", v))] = find(i)
    return len({find(i) for i in range(n)}) == 1''',
            ),
            dict(
                name="Sieve of smallest prime factors, then union",
                time="O(M log log M + n log M)",
                space="O(M)",
                best=True,
                why=[
                    "Precompute the smallest prime factor of every value up to M = max(nums) with a sieve. Then each number factors in O(log M) by repeatedly dividing by its smallest prime factor. Union each index with its primes as before.",
                    "The sieve costs O(M log log M) once; after that, factoring is almost free, which matters when n is large and values repeat.",
                ],
                code='''def can_traverse_all_pairs(nums):
    n = len(nums)
    if n == 1:
        return True
    if 1 in nums:
        return False
    M = max(nums)
    spf = list(range(M + 1))                     # smallest prime factor
    for p in range(2, int(M ** 0.5) + 1):
        if spf[p] == p:
            for q in range(p * p, M + 1, p):
                if spf[q] == q:
                    spf[q] = p
    parent = list(range(n + M + 1))              # 0..n-1 indices, n+p primes

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, v in enumerate(nums):
        while v > 1:
            p = spf[v]
            parent[find(n + p)] = find(i)
            while v % p == 0:
                v //= p
    root = find(0)
    return all(find(i) == root for i in range(n))''',
            ),
        ],
        tests='''assert can_traverse_all_pairs([2, 3, 6]) is True
assert can_traverse_all_pairs([3, 9, 5]) is False
assert can_traverse_all_pairs([4, 3, 12, 8]) is True
assert can_traverse_all_pairs([1]) is True and can_traverse_all_pairs([1, 1]) is False
rng = random.Random(4)
for _ in range(60):
    nums = [rng.randint(1, 30) for _ in range(rng.randint(1, 7))]
    n = len(nums)
    label = list(range(n))
    for _ in range(n):
        for i in range(n):
            for j in range(n):
                if i != j and math.gcd(nums[i], nums[j]) > 1:
                    label[i] = label[j] = min(label[i], label[j])
    assert can_traverse_all_pairs(nums) is (len(set(label)) == 1)''',
    ),
    ],
),
    ],
)
