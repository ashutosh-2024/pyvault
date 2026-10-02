# -*- coding: utf-8 -*-
"""Binary Trees: lowest common ancestor, and distance problems that treat the
tree as an undirected graph."""

SECTIONS = [

# ---------------------------------------------------------------- LCA
dict(
    id="lca",
    title="Lowest common ancestor",
    idea=[
        "The LCA of two nodes is the deepest node that has both below it (a node counts as its own descendant). It is where the path between them bends, which is why so many distance and path problems reduce to it.",
    ],
    problems=[

    dict(
        id="lca-binary-tree",
        lc=236, slug="lowest-common-ancestor-of-a-binary-tree",
        name="Lowest Common Ancestor of a Binary Tree",
        difficulty="medium",
        framing=[
            "Given the root and two nodes <code>p</code> and <code>q</code> that are both in the tree, return their lowest common ancestor. No ordering to exploit: this is the general case.",
        ],
        approaches=[
            dict(
                name="Postorder: report what you found",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Each call returns <code>p</code> or <code>q</code> if it found one of them in its subtree (or the LCA, once both have met), and <code>None</code> otherwise. A node whose left and right calls <em>both</em> return something is where the two searches meet: it is the LCA, and it is passed upward unchanged from then on.",
                    "Returning immediately when <code>node</code> is <code>p</code> or <code>q</code> handles the case where one is an ancestor of the other: the lower one is never reached, but it does not need to be &mdash; the problem promises both exist, so the ancestor is the answer.",
                    "O(n) time, O(h) stack. The answer is correct only because both nodes are guaranteed present; if they might not be, you must count finds explicitly.",
                ],
                code='''def lowest_common_ancestor(root, p, q):
    if root is None or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root                  # p on one side, q on the other
    return left or right             # pass up whatever was found''',
            ),
            dict(
                name="Parent pointers and an ancestor set",
                time="O(n)",
                space="O(n)",
                tag="parent-pointer variant",
                why=[
                    "Record every node's parent with one traversal. Then walk up from <code>p</code> collecting its ancestors in a set, and walk up from <code>q</code> until you hit one of them.",
                    "O(n) time and O(n) extra space for the parent map. It is the right approach when the nodes already have parent pointers (LeetCode 1650), because then no traversal from the root is needed at all and it costs O(h).",
                ],
                code='''def lowest_common_ancestor(root, p, q):
    parent, stack = {root: None}, [root]
    while p not in parent or q not in parent:
        node = stack.pop()
        for child in (node.left, node.right):
            if child is not None:
                parent[child] = node
                stack.append(child)
    ancestors = set()
    while p is not None:
        ancestors.add(p)
        p = parent[p]
    while q not in ancestors:
        q = parent[q]
    return q''',
            ),
        ],
        tests='''t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
n = lambda v: find_node(t, v)
assert lowest_common_ancestor(t, n(5), n(1)) is n(3)
assert lowest_common_ancestor(t, n(5), n(4)) is n(5)
assert lowest_common_ancestor(t, n(7), n(8)) is n(3)
assert lowest_common_ancestor(t, n(6), n(4)) is n(5)
t2 = build([1, 2])
assert lowest_common_ancestor(t2, t2, t2.left) is t2''',
    ),

    dict(
        id="lca-bst",
        lc=235, slug="lowest-common-ancestor-of-a-binary-search-tree",
        name="Lowest Common Ancestor of a Binary Search Tree",
        difficulty="medium",
        framing=[
            "The same question on a BST, and the ordering changes everything: you can tell which side each node is on by comparing values, so you never need to search. Interviewers expect O(h), not O(n).",
        ],
        approaches=[
            dict(
                name="Walk down until the values split",
                time="O(h)",
                space="O(1)",
                best=True,
                why=[
                    "If both values are smaller than the current node, both nodes are in the left subtree, so the LCA is there too; if both are larger, go right. Otherwise they are on different sides (or one of them is this node), and this node is the split point: the LCA.",
                    "One step per level: O(h), and iterative, so O(1) space. On a balanced BST that is O(log n) &mdash; the whole tree is never touched.",
                ],
                code='''def lowest_common_ancestor(root, p, q):
    node = root
    while node:
        if p.val < node.val and q.val < node.val:
            node = node.left
        elif p.val > node.val and q.val > node.val:
            node = node.right
        else:
            return node              # the paths to p and q split here''',
            ),
            dict(
                name="Recursive",
                time="O(h)",
                space="O(h)",
                why=[
                    "The same decision expressed recursively. Correct, but it spends O(h) stack on what is really a loop.",
                ],
                code='''def lowest_common_ancestor(root, p, q):
    if p.val < root.val and q.val < root.val:
        return lowest_common_ancestor(root.left, p, q)
    if p.val > root.val and q.val > root.val:
        return lowest_common_ancestor(root.right, p, q)
    return root''',
            ),
        ],
        tests='''t = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
n = lambda v: find_node(t, v)
assert lowest_common_ancestor(t, n(2), n(8)) is n(6)
assert lowest_common_ancestor(t, n(2), n(4)) is n(2)
assert lowest_common_ancestor(t, n(3), n(5)) is n(4)
assert lowest_common_ancestor(t, n(7), n(9)) is n(8)''',
    ),

    dict(
        id="lca-deepest-leaves",
        lc=1123, slug="lowest-common-ancestor-of-deepest-leaves",
        name="Lowest Common Ancestor of Deepest Leaves",
        difficulty="medium",
        framing=[
            "Return the LCA of <em>all</em> the deepest leaves. There may be one deepest leaf (then it is its own answer) or many.",
            "Instead of searching for specific nodes, each subtree reports two facts: how deep it goes, and the LCA of its own deepest nodes. Returning multiple pieces of information is the whole technique.",
        ],
        approaches=[
            dict(
                name="Return (depth, lca) pairs",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "If both children reach the same depth, the deepest nodes are on both sides, so this node is their LCA. If one side is deeper, all the deepest nodes are over there, and that side's answer is passed up unchanged.",
                    "One postorder pass: O(n) time, O(h) stack. The naive alternative &mdash; compute the depth of each subtree fresh at every node &mdash; repeats work and is O(n&sup2;) on a chain.",
                ],
                code='''def lca_deepest_leaves(root):
    def dfs(node):
        """Return (depth of this subtree, LCA of its deepest nodes)."""
        if node is None:
            return 0, None
        ld, la = dfs(node.left)
        rd, ra = dfs(node.right)
        if ld == rd:
            return ld + 1, node          # deepest nodes on both sides
        return (ld + 1, la) if ld > rd else (rd + 1, ra)

    return dfs(root)[1]''',
            ),
        ],
        tests='''t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
assert lca_deepest_leaves(t) is find_node(t, 2)
t = build([1])
assert lca_deepest_leaves(t) is t
t = build([0, 1, 3, None, 2])
assert lca_deepest_leaves(t) is find_node(t, 2)
t = build([1, 2, 3, 4, 5, 6, 7])
assert lca_deepest_leaves(t) is t''',
    ),

    dict(
        id="subtree-deepest-nodes",
        lc=865, slug="smallest-subtree-with-all-the-deepest-nodes",
        name="Smallest Subtree with all the Deepest Nodes",
        difficulty="medium",
        framing=[
            "Return the root of the smallest subtree that contains every deepest node. Read carefully and it is the <em>same problem</em> as the previous one &mdash; LeetCode even says so &mdash; because the smallest subtree containing a set of nodes is rooted at their LCA.",
            "Recognising a problem you have already solved under a different name is a skill interviews test. Here it is shown with a different technique: find the deepest level with BFS, then walk the deepest nodes up together.",
        ],
        approaches=[
            dict(
                name="BFS for the deepest level, then climb with parents",
                time="O(n)",
                space="O(n)",
                why=[
                    "BFS records each node's parent and ends with the deepest level in hand. Replace that set of nodes by the set of their parents, repeatedly, until only one node remains: that is where they all meet.",
                    "Each climb step shrinks or keeps the set and each node is in it at most once: O(n) time, O(n) for the parent map.",
                ],
                code='''def subtree_with_all_deepest(root):
    parent, level = {root: None}, [root]
    while True:
        nxt = []
        for node in level:
            for child in (node.left, node.right):
                if child is not None:
                    parent[child] = node
                    nxt.append(child)
        if not nxt:
            break
        level = nxt
    group = set(level)                  # the deepest nodes
    while len(group) > 1:
        group = {parent[n] for n in group}
    return group.pop()''',
            ),
            dict(
                name="Return (depth, answer) pairs",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Identical to the previous problem's solution. One pass, no parent map, O(h) stack &mdash; which is why it is the one to pick.",
                ],
                code='''def subtree_with_all_deepest(root):
    def dfs(node):
        if node is None:
            return 0, None
        ld, la = dfs(node.left)
        rd, ra = dfs(node.right)
        if ld == rd:
            return ld + 1, node
        return (ld + 1, la) if ld > rd else (rd + 1, ra)

    return dfs(root)[1]''',
            ),
        ],
        tests='''t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
assert subtree_with_all_deepest(t) is find_node(t, 2)
t = build([1])
assert subtree_with_all_deepest(t) is t
t = build([0, 1, 3, None, 2])
assert subtree_with_all_deepest(t) is find_node(t, 2)''',
    ),

    dict(
        id="lca-binary-lifting",
        name="LCA for Many Queries: Binary Lifting",
        difficulty="hard",
        tags=["Tree", "Binary Lifting", "Dynamic Programming", "Concept"],
        statement=[
            "You are given a tree once and then <code>Q</code> queries, each asking for the LCA of two nodes. Running the O(n) postorder search per query costs O(n &middot; Q), which is too slow when both are large.",
            "Preprocess the tree so that each query takes O(log n). Not a LeetCode problem as stated, but the technique behind LeetCode 1483 (Kth Ancestor of a Tree Node) and a standard follow-up to LCA questions.",
        ],
        examples=[
            dict(input="root = [3,5,1,6,2,0,8,null,null,7,4], queries = [(7,4), (6,4), (7,8)]",
                 output="[2, 5, 3]"),
        ],
        constraints=[
            "<code>1 &lt;= n &lt;= 10<sup>5</sup></code>, <code>1 &lt;= Q &lt;= 10<sup>5</sup></code>",
            "Values are unique",
        ],
        approaches=[
            dict(
                name="Binary lifting table",
                time="O(n log n) build, O(log n) per query",
                space="O(n log n)",
                best=True,
                why=[
                    "Store <code>up[j][v]</code> = the ancestor 2<sup>j</sup> levels above <code>v</code>. Row 0 is the parent; each further row doubles: <code>up[j][v] = up[j-1][up[j-1][v]]</code>. That is O(log n) rows of n entries.",
                    "A query first lifts the deeper node until both are at the same depth, jumping by the binary digits of the depth difference. Then, from the largest jump down, it jumps both nodes together whenever that keeps them <em>different</em>. They end one step below the LCA, and one more parent step reaches it.",
                    "The pattern &mdash; precompute answers for powers of two, combine them to answer any distance &mdash; is the same one behind sparse tables and fast exponentiation.",
                ],
                code='''class LCA:
    def __init__(self, root):
        self.depth, parent, order = {root: 0}, {root: root}, [root]
        for node in order:                              # BFS: parents before children
            for child in (node.left, node.right):
                if child is not None:
                    parent[child] = node
                    self.depth[child] = self.depth[node] + 1
                    order.append(child)
        self.LOG = max(1, len(order).bit_length())
        self.up = [parent]
        for j in range(1, self.LOG):
            prev = self.up[j - 1]
            self.up.append({v: prev[prev[v]] for v in order})

    def query(self, a, b):
        if self.depth[a] < self.depth[b]:
            a, b = b, a
        diff = self.depth[a] - self.depth[b]
        for j in range(self.LOG):                       # lift a to b's depth
            if diff >> j & 1:
                a = self.up[j][a]
        if a is b:
            return a
        for j in reversed(range(self.LOG)):             # jump while still apart
            if self.up[j][a] is not self.up[j][b]:
                a, b = self.up[j][a], self.up[j][b]
        return self.up[0][a]''',
            ),
        ],
        tests='''t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
lca = LCA(t)
n = lambda v: find_node(t, v)
assert [lca.query(n(a), n(b)).val for a, b in [(7, 4), (6, 4), (7, 8), (3, 3), (5, 4)]] == [2, 5, 3, 3, 5]


def _naive(root, p, q):
    if root is None or root is p or root is q:
        return root
    l, r = _naive(root.left, p, q), _naive(root.right, p, q)
    return root if l and r else l or r

for seed in range(20):
    t = random_tree(1 + seed * 5, seed, 0, 999, distinct=True)
    lca, nodes = LCA(t), all_nodes(t)
    rng = random.Random(seed)
    for _ in range(30):
        a, b = rng.choice(nodes), rng.choice(nodes)
        assert lca.query(a, b) is _naive(t, a, b), seed''',
    ),
    ],
),

# ---------------------------------------------------------------- distance
dict(
    id="tree-as-graph",
    title="Distance problems: the tree as an undirected graph",
    idea=[
        "A tree only lets you walk down. Distance problems need to walk up too, so the standard move is to record each node's parent, after which the tree is an undirected graph and BFS from any node gives distances.",
    ],
    problems=[

    dict(
        id="all-nodes-distance-k",
        lc=863, slug="all-nodes-distance-k-in-binary-tree",
        name="All Nodes Distance K in Binary Tree",
        difficulty="medium",
        framing=[
            "Return every node exactly <code>k</code> edges from <code>target</code>. Some are below it, but others are reached by going up through its ancestors and then down other branches &mdash; which a tree cannot do without help.",
        ],
        approaches=[
            dict(
                name="Parent map, then BFS from the target",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "One traversal records every node's parent. Now each node has up to three neighbours &mdash; left, right, parent &mdash; and the problem is plain BFS on an undirected graph: expand <code>k</code> rings outward from the target, with a visited set so you never walk back.",
                    "O(n) time; O(n) for the parent map and visited set.",
                ],
                code='''def distance_k(root, target, k):
    parent, stack = {root: None}, [root]
    while stack:
        node = stack.pop()
        for child in (node.left, node.right):
            if child is not None:
                parent[child] = node
                stack.append(child)

    seen, ring = {target}, [target]
    for _ in range(k):
        nxt = []
        for node in ring:
            for nb in (node.left, node.right, parent[node]):
                if nb is not None and nb not in seen:
                    seen.add(nb)
                    nxt.append(nb)
        ring = nxt
    return sorted(n.val for n in ring)''',
            ),
            dict(
                name="One DFS returning distance to the target",
                time="O(n)",
                space="O(h)",
                tag="no parent map",
                why=[
                    "Each call returns how far the target is below it (or -1). When an ancestor learns the target is <code>d</code> edges down its left side, the nodes at distance <code>k</code> in its <em>right</em> subtree are those at depth <code>k - d - 1</code> there, and the ancestor itself qualifies when <code>d == k</code>.",
                    "Same O(n) time with only O(h) stack &mdash; at the cost of noticeably trickier code. The parent-map version is the one to write under pressure.",
                ],
                code='''def distance_k(root, target, k):
    out = []

    def collect(node, depth):
        if node is None or depth < 0:
            return
        if depth == 0:
            out.append(node.val)
            return
        collect(node.left, depth - 1)
        collect(node.right, depth - 1)

    def dfs(node):
        """Distance from node down to target, or -1 if not below."""
        if node is None:
            return -1
        if node is target:
            collect(node, k)
            return 0
        for here, other in ((node.left, node.right), (node.right, node.left)):
            d = dfs(here)
            if d != -1:
                if d + 1 == k:
                    out.append(node.val)
                else:
                    collect(other, k - d - 2)
                return d + 1
        return -1

    dfs(root)
    return sorted(out)''',
            ),
        ],
        tests='''t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
assert distance_k(t, find_node(t, 5), 2) == [1, 4, 7]
assert distance_k(t, find_node(t, 5), 0) == [5]
assert distance_k(t, find_node(t, 7), 3) == [3, 6]      # up through 2 and 5
t = build([1])
assert distance_k(t, t, 3) == []''',
    ),

    dict(
        id="find-distance",
        lc=1740, slug="find-distance-in-a-binary-tree",
        name="Find Distance in a Binary Tree",
        difficulty="medium",
        tags=["Tree", "Depth-First Search", "Lowest Common Ancestor"],
        statement=[
            "Given the root of a binary tree with unique values and two values <code>p</code> and <code>q</code> that are both in the tree, return the <strong>distance</strong> between their nodes: the number of edges on the path between them.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 0", output="3",
                 explanation="5 - 3 - 1 - 0"),
            dict(input="root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 7", output="2",
                 explanation="5 - 2 - 7"),
            dict(input="root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 5", output="0"),
        ],
        constraints=[
            "<code>1 &lt;= n &lt;= 10<sup>4</sup></code>",
            "All values are unique; <code>p</code> and <code>q</code> are values in the tree",
        ],
        approaches=[
            dict(
                name="LCA, then two depths",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "The path from <code>p</code> to <code>q</code> goes up to their LCA and down again, so the distance is <code>depth(p) + depth(q) - 2 &middot; depth(lca)</code>, or equivalently the distance from the LCA down to each.",
                    "Find the LCA with the standard postorder search, then measure the two downward distances from it. Three O(n) passes, O(h) stack.",
                ],
                code='''def find_distance(root, p, q):
    def lca(node):
        if node is None or node.val in (p, q):
            return node
        left, right = lca(node.left), lca(node.right)
        return node if left and right else left or right

    def depth_of(node, val, d):
        if node is None:
            return -1
        if node.val == val:
            return d
        found = depth_of(node.left, val, d + 1)
        return found if found != -1 else depth_of(node.right, val, d + 1)

    top = lca(root)
    return depth_of(top, p, 0) + depth_of(top, q, 0)''',
            ),
            dict(
                name="One pass: return the distance found so far",
                time="O(n)",
                space="O(h)",
                why=[
                    "Each call returns the distance from this node down to whichever of <code>p</code>/<code>q</code> it found, or -1. When both sides report a distance, this is the LCA and the answer is their sum plus two; when this node is one target and the other is below, it is the distance returned from below plus one.",
                    "One pass instead of three, at the cost of a few more cases to get right.",
                ],
                code='''def find_distance(root, p, q):
    if p == q:
        return 0
    answer = 0

    def dfs(node):
        nonlocal answer
        if node is None:
            return -1
        left, right = dfs(node.left), dfs(node.right)
        if node.val in (p, q):
            below = max(left, right)
            if below != -1:
                answer = below + 1           # the other target is under this one
            return 0
        if left != -1 and right != -1:
            answer = left + right + 2        # this node is the LCA
            return -1
        found = max(left, right)
        return found + 1 if found != -1 else -1

    dfs(root)
    return answer''',
            ),
        ],
        tests='''t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
assert find_distance(t, 5, 0) == 3
assert find_distance(t, 5, 7) == 2
assert find_distance(t, 5, 5) == 0
assert find_distance(t, 6, 4) == 3
assert find_distance(t, 3, 4) == 3''',
    ),

    dict(
        id="time-to-infect",
        lc=2385, slug="amount-of-time-for-binary-tree-to-be-infected",
        name="Amount of Time for Binary Tree to Be Infected",
        difficulty="medium",
        framing=[
            "An infection starts at the node with value <code>start</code> and spreads to every neighbour (children <em>and</em> parent) each minute. How long until the whole tree is infected? That is the largest distance from <code>start</code> to any node &mdash; the eccentricity of the start node.",
        ],
        approaches=[
            dict(
                name="Build the graph, BFS by minutes",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Record parents to make the tree undirected, find the start node, then BFS level by level. Each level is one minute; the number of levels after the first is the answer.",
                    "This is the Distance K solution run until the queue empties instead of for k rounds. O(n) time and space.",
                ],
                code='''def amount_of_time(root, start):
    parent, stack, source = {root: None}, [root], None
    while stack:
        node = stack.pop()
        if node.val == start:
            source = node
        for child in (node.left, node.right):
            if child is not None:
                parent[child] = node
                stack.append(child)

    seen, ring, minutes = {source}, [source], -1
    while ring:
        minutes += 1
        nxt = []
        for node in ring:
            for nb in (node.left, node.right, parent[node]):
                if nb is not None and nb not in seen:
                    seen.add(nb)
                    nxt.append(nb)
        ring = nxt
    return minutes''',
            ),
            dict(
                name="One DFS: depth below and distance to start",
                time="O(n)",
                space="O(h)",
                why=[
                    "The farthest node from <code>start</code> is either deepest below it, or reached by going up <code>d</code> edges to some ancestor and then down that ancestor's <em>other</em> subtree. Each call returns its subtree's depth, and signals the distance to <code>start</code> by returning it as a negative number &mdash; one integer carrying two kinds of answer.",
                    "O(n) time, O(h) stack, no parent map. Harder to write correctly; the BFS is easier to defend.",
                ],
                code='''def amount_of_time(root, start):
    best = 0

    def dfs(node):
        """Depth of subtree (>= 0), or -(distance to start) if start is below."""
        nonlocal best
        if node is None:
            return 0
        left, right = dfs(node.left), dfs(node.right)
        if node.val == start:
            best = max(best, left, right)     # infect straight down
            return -1
        if left >= 0 and right >= 0:
            return 1 + max(left, right)
        dist = -min(left, right)              # distance from node to start
        other = right if left < 0 else left   # depth of the side without start
        best = max(best, dist + other)
        return -(dist + 1)

    dfs(root)
    return best''',
            ),
        ],
        tests='''assert amount_of_time(build([1, 5, 3, None, 4, 10, 6, 9, 2]), 3) == 4
assert amount_of_time(build([1]), 1) == 0
assert amount_of_time(build([1, 2, None, 3, None, 4]), 1) == 3
assert amount_of_time(build([1, 2, None, 3, None, 4]), 4) == 3
assert amount_of_time(build([1, 2, 3, 4, 5]), 4) == 3''',
    ),
    ],
),
]
