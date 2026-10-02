# -*- coding: utf-8 -*-
"""Binary Trees: shape properties (extras), modification, tree DP, subtree
aggregation, Morris traversal."""

EXTRA = {
    "shape": [

    dict(
        id="maximum-width",
        lc=662, slug="maximum-width-of-binary-tree",
        name="Maximum Width of Binary Tree",
        difficulty="medium",
        framing=[
            "The width of a level is the distance between its leftmost and rightmost non-null nodes, <em>counting the gaps</em> as if the level were full. Return the maximum. Counting nodes per level is not enough; you need each node's position in the level.",
            "Positions come from the array layout of a complete tree: root at 0, children of <code>i</code> at <code>2i</code> and <code>2i + 1</code>. Width is then <code>last - first + 1</code>.",
        ],
        pitfall="Letting positions grow unchecked. They double every level, so a 3,000-node chain reaches 2<sup>3000</sup>. Python survives it, but every operation on those numbers gets slower; in Java or C++ it overflows. Re-base each level to start at 0.",
        approaches=[
            dict(
                name="BFS with positions, re-based per level",
                time="O(n)",
                space="O(w)",
                best=True,
                why=[
                    "Carry <code>(node, position)</code> through BFS. At the start of each level, subtract the level's first position from every position in it. Widths are unchanged by the shift, but the numbers now stay bounded by the level's width instead of 2<sup>depth</sup>.",
                    "O(n) time, O(w) queue.",
                ],
                code='''def width_of_binary_tree(root):
    best, level = 0, [(root, 0)] if root else []
    while level:
        base = level[0][1]
        best = max(best, level[-1][1] - base + 1)
        nxt = []
        for node, pos in level:
            pos -= base                        # keep numbers small
            if node.left is not None:
                nxt.append((node.left, 2 * pos))
            if node.right is not None:
                nxt.append((node.right, 2 * pos + 1))
        level = nxt
    return best''',
            ),
        ],
        tests='''assert width_of_binary_tree(build([1, 3, 2, 5, 3, None, 9])) == 4
assert width_of_binary_tree(build([1, 3, 2, 5, None, None, 9, 6, None, 7])) == 7
assert width_of_binary_tree(build([1, 3, 2, 5])) == 2
assert width_of_binary_tree(build([1])) == 1''',
    ),

    dict(
        id="all-possible-full-binary-trees",
        lc=894, slug="all-possible-full-binary-trees",
        name="All Possible Full Binary Trees",
        difficulty="medium",
        framing=[
            "A <strong>full</strong> binary tree is one where every node has 0 or 2 children. Return every full binary tree with <code>n</code> nodes (all values 0). The vocabulary matters in interviews: full (0 or 2 children), <em>complete</em> (every level full except the last, which is packed left), <em>perfect</em> (every level full), <em>balanced</em> (subtree heights differ by at most 1 everywhere).",
            "A full tree's root has a full left subtree of <code>i</code> nodes and a full right subtree of <code>n - 1 - i</code>, for every odd <code>i</code>. That recurrence is a tree-shaped dynamic programme: the answer for <code>n</code> is built from answers for smaller sizes.",
        ],
        pitfall="Missing that even <code>n</code> is impossible. A full tree has 2 more nodes for every internal node, so its size is always odd.",
        approaches=[
            dict(
                name="Memoised recursion over sizes",
                time="O(2<sup>n/2</sup>)",
                space="O(2<sup>n/2</sup>)",
                best=True,
                why=[
                    "For each odd split, pair every left tree of that size with every right tree of the remaining size under a new root. Cache the list for each size so it is built once.",
                    "The number of trees is the Catalan number C<sub>(n-1)/2</sub>, which grows like 4<sup>k</sup>/k<sup>1.5</sup> with <code>k = (n-1)/2</code>, i.e. roughly 2<sup>n</sup>. You cannot beat the output size. Memoisation makes the returned trees <em>share</em> subtrees, which LeetCode accepts and which saves most of the memory &mdash; but it means mutating one returned tree can change others.",
                ],
                code='''from functools import cache


@cache
def all_possible_fbt(n):
    if n % 2 == 0:
        return []
    if n == 1:
        return [TreeNode(0)]
    out = []
    for left in range(1, n, 2):
        for l in all_possible_fbt(left):
            for r in all_possible_fbt(n - 1 - left):
                out.append(TreeNode(0, l, r))
    return out''',
            ),
        ],
        tests='''def _full(t):
    return t is None or ((t.left is None) == (t.right is None) and _full(t.left) and _full(t.right))

assert all_possible_fbt(2) == []
assert [level_order(t) for t in all_possible_fbt(1)] == [[0]]
assert [len(all_possible_fbt(n)) for n in (1, 3, 5, 7, 9, 11)] == [1, 1, 2, 5, 14, 42]
trees = all_possible_fbt(7)
assert all(_full(t) and len(all_nodes(t)) == 7 for t in trees)
assert len({shape(t) for t in trees}) == 5''',
    ),
    ],
}


SECTIONS = [

# ---------------------------------------------------------------- modification
dict(
    id="modification",
    title="Modifying a tree safely",
    idea=[
        "Mutation is where tree code breaks: overwrite a pointer before you have saved what it pointed to and a subtree is gone. The safe pattern is postorder &mdash; fix the children first, then decide about the node &mdash; with the recursion returning the (possibly new) subtree root so the parent can re-link it.",
    ],
    problems=[

    dict(
        id="flatten-to-linked-list",
        lc=114, slug="flatten-binary-tree-to-linked-list",
        name="Flatten Binary Tree to Linked List",
        difficulty="medium",
        framing=[
            "Rearrange the tree <em>in place</em> into a right-leaning chain in preorder order: every <code>left</code> becomes <code>None</code> and <code>right</code> points to the next preorder node. The challenge is the follow-up: O(1) extra space.",
        ],
        approaches=[
            dict(
                name="Splice the left subtree in, iteratively",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "At each node with a left subtree, the node's right subtree must come right after the <em>last</em> node of the left subtree in preorder &mdash; its rightmost node. So find that node, hang the right subtree off it, move the left subtree to the right, clear the left, and step right.",
                    "Each edge is walked at most twice (once while searching for rightmost nodes, once while stepping), so O(n) time and no stack at all. This is the Morris idea used for mutation instead of traversal.",
                ],
                code='''def flatten(root):
    node = root
    while node:
        if node.left is not None:
            tail = node.left
            while tail.right is not None:       # last preorder node on the left
                tail = tail.right
            tail.right = node.right             # right subtree follows it
            node.right, node.left = node.left, None
        node = node.right''',
            ),
            dict(
                name="Reverse preorder with a prev pointer",
                time="O(n)",
                space="O(h)",
                why=[
                    "Visit nodes in reverse preorder (right, left, root) and point each one's <code>right</code> at the node visited just before it. Because everything after a node in preorder has already been visited, overwriting its pointers loses nothing.",
                    "Short and elegant, with O(h) recursion stack.",
                ],
                code='''def flatten(root):
    prev = None

    def walk(node):
        nonlocal prev
        if node is None:
            return
        walk(node.right)
        walk(node.left)
        node.right, node.left = prev, None
        prev = node

    walk(root)''',
            ),
        ],
        tests='''for values in ([1, 2, 5, 3, 4, None, 6], [], [0], [1, 2, None, 3]):
    t = build(values)
    expected = vals_pre(t)
    flatten(t)
    chain, node = [], t
    while node:
        assert node.left is None
        chain.append(node.val)
        node = node.right
    assert chain == expected, values''',
    ),

    dict(
        id="binary-tree-pruning",
        lc=814, slug="binary-tree-pruning",
        name="Binary Tree Pruning",
        difficulty="medium",
        framing=[
            "Values are 0 or 1. Remove every subtree that contains no 1. A node can only be judged after its children have been pruned &mdash; a textbook postorder mutation.",
        ],
        approaches=[
            dict(
                name="Postorder, return the pruned subtree",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Prune both children and assign the results back. Then this node survives if it is a 1 or still has any child; otherwise return <code>None</code> and the parent drops it.",
                    "Returning the new subtree root is the key habit: the function never needs to know who its parent is.",
                ],
                code='''def prune_tree(root):
    if root is None:
        return None
    root.left = prune_tree(root.left)
    root.right = prune_tree(root.right)
    if root.val == 0 and root.left is None and root.right is None:
        return None
    return root''',
            ),
        ],
        tests='''assert level_order(prune_tree(build([1, None, 0, 0, 1]))) == [1, None, 0, None, 1]
assert level_order(prune_tree(build([1, 0, 1, 0, 0, 0, 1]))) == [1, None, 1, None, 1]
assert level_order(prune_tree(build([1, 1, 0, 1, 1, 0, 1, 0]))) == [1, 1, 0, 1, 1, None, 1]
assert prune_tree(build([0, 0, 0])) is None''',
    ),

    dict(
        id="delete-leaves-with-value",
        lc=1325, slug="delete-leaves-with-a-given-value",
        name="Delete Leaves With a Given Value",
        difficulty="medium",
        framing=[
            "Delete every leaf with value <code>target</code>, and keep going: a parent that becomes a leaf with that value must be deleted too. Postorder handles the cascade automatically, because a parent is examined only after its children have been deleted.",
        ],
        approaches=[
            dict(
                name="Postorder, re-check after children",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Same shape as Pruning. After deleting within both children, the node may have become a leaf; if it has and its value is the target, delete it as well. No second pass is needed.",
                    "A preorder version would miss the cascade: it decides about a node before its children have been removed.",
                ],
                code='''def remove_leaf_nodes(root, target):
    if root is None:
        return None
    root.left = remove_leaf_nodes(root.left, target)
    root.right = remove_leaf_nodes(root.right, target)
    if root.left is None and root.right is None and root.val == target:
        return None
    return root''',
            ),
        ],
        tests='''assert level_order(remove_leaf_nodes(build([1, 2, 3, 2, None, 2, 4]), 2)) == [1, None, 3, None, 4]
assert level_order(remove_leaf_nodes(build([1, 3, 3, 3, 2]), 3)) == [1, 3, None, None, 2]
assert level_order(remove_leaf_nodes(build([1, 2, None, 2, None, 2]), 2)) == [1]
assert remove_leaf_nodes(build([1, 1, 1]), 1) is None''',
    ),
    ],
),

# ---------------------------------------------------------------- tree DP
dict(
    id="tree-dp",
    title="Tree DP: combine the children's answers",
    idea=[
        "DP(node) = what the left subtree reports + what the right subtree reports + the node's own choice. The skill is choosing what to report: often a small tuple of answers under different assumptions about the node.",
    ],
    problems=[

    dict(
        id="house-robber-iii",
        lc=337, slug="house-robber-iii",
        name="House Robber III",
        difficulty="medium",
        framing=[
            "Houses form a binary tree; robbing two directly connected houses sets off the alarm. Maximise the loot. Whether you can take a node depends on whether you took its parent, so a single number per subtree is not enough &mdash; report two.",
        ],
        approaches=[
            dict(
                name="Return (with node, without node)",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "For each subtree return the best total if its root <strong>is</strong> robbed and if it <strong>is not</strong>. Robbing the node forbids both children, so it adds their <em>without</em> values. Skipping it frees each child to choose its better option.",
                    "Two numbers per node, one pass: O(n). This two-state return is the canonical tree DP, and the template for Binary Tree Cameras (three states) and Maximum Sum BST (four values).",
                ],
                code='''def rob(root):
    def dfs(node):
        """Return (best if node robbed, best if node skipped)."""
        if node is None:
            return 0, 0
        lw, lo = dfs(node.left)
        rw, ro = dfs(node.right)
        with_node = node.val + lo + ro
        without = max(lw, lo) + max(rw, ro)
        return with_node, without

    return max(dfs(root))''',
            ),
            dict(
                name="Memoised grandchildren recursion",
                time="O(n)",
                space="O(n)",
                why=[
                    "The direct translation: either rob this node and recurse into the four grandchildren, or skip it and recurse into the two children. Without a cache each node is solved many times &mdash; exponentially many on a chain. A memo keyed by node brings it to O(n) time with O(n) memory.",
                    "It works, but it is the pair-returning version that shows you see the state structure.",
                ],
                code='''def rob(root):
    memo = {}

    def best(node):
        if node is None:
            return 0
        if node not in memo:
            take = node.val
            for child in (node.left, node.right):
                if child is not None:
                    take += best(child.left) + best(child.right)
            skip = best(node.left) + best(node.right)
            memo[node] = max(take, skip)
        return memo[node]

    return best(root)''',
            ),
        ],
        tests='''assert rob(build([3, 2, 3, None, 3, None, 1])) == 7
assert rob(build([3, 4, 5, 1, 3, None, 1])) == 9
assert rob(None) == 0
assert rob(build([4, 1, None, 2, None, 3])) == 7


def _brute(node, parent_taken=False):
    if node is None:
        return 0
    skip = _brute(node.left) + _brute(node.right)
    if parent_taken:
        return skip
    return max(skip, node.val + _brute(node.left, True) + _brute(node.right, True))

for seed in range(40):
    t = random_tree(1 + seed % 14, seed, 0, 20)
    assert rob(t) == _brute(t), seed''',
    ),

    dict(
        id="binary-tree-cameras",
        lc=968, slug="binary-tree-cameras",
        name="Binary Tree Cameras",
        difficulty="hard",
        framing=[
            "A camera on a node monitors the node, its parent and its children. Find the minimum number of cameras that monitor every node.",
            "Leaves are the key. Putting a camera on a leaf covers at most two nodes; putting it on the leaf's parent covers the leaf, its sibling, the parent and the grandparent. So work bottom-up and never place a camera until a child forces you to.",
        ],
        approaches=[
            dict(
                name="Greedy postorder with three states",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Each node reports one of three states: <strong>0</strong> not covered (it needs its parent to have a camera), <strong>1</strong> has a camera, <strong>2</strong> covered without a camera. An empty child reports 2 &mdash; it needs nothing and offers nothing.",
                    "If any child is uncovered, this node <em>must</em> take a camera. Otherwise, if any child has a camera, this node is covered. Otherwise it is uncovered and leaves the decision to its parent. The root is the one node with no parent to defer to, so if it ends uncovered it gets a camera itself.",
                    "Why greedy is safe: delaying a camera to the parent never covers fewer nodes than placing it on the child. O(n) time, O(h) stack.",
                ],
                code='''def min_camera_cover(root):
    cameras = 0
    UNCOVERED, CAMERA, COVERED = 0, 1, 2

    def dfs(node):
        nonlocal cameras
        if node is None:
            return COVERED
        left, right = dfs(node.left), dfs(node.right)
        if left == UNCOVERED or right == UNCOVERED:
            cameras += 1
            return CAMERA
        if left == CAMERA or right == CAMERA:
            return COVERED
        return UNCOVERED

    if dfs(root) == UNCOVERED:
        cameras += 1                     # the root has nobody to defer to
    return cameras''',
            ),
            dict(
                name="Exact DP over three costs",
                time="O(n)",
                space="O(h)",
                tag="provably optimal",
                why=[
                    "If you do not trust the greedy argument, compute three costs per node and let <code>min</code> decide: (a) camera here; (b) no camera here but covered by a child; (c) not covered yet, relying on the parent. Each combines the children's three costs with the constraint the state implies.",
                    "Same O(n), more code. Useful to verify the greedy &mdash; the tests below run both on random trees.",
                ],
                code='''def min_camera_cover(root):
    INF = float("inf")

    def dfs(node):
        """(camera here, covered by a child, not yet covered)."""
        if node is None:
            return INF, 0, 0
        la, lb, lc = dfs(node.left)
        ra, rb, rc = dfs(node.right)
        here = 1 + min(la, lb, lc) + min(ra, rb, rc)
        by_child = min(la + min(ra, rb), ra + min(la, lb))
        waiting = lb + rb
        return here, by_child, waiting

    a, b, _ = dfs(root)
    return min(a, b)''',
            ),
        ],
        tests='''assert min_camera_cover(build([0, 0, None, 0, 0])) == 1
assert min_camera_cover(build([0, 0, None, 0, None, 0, None, None, 0])) == 2
assert min_camera_cover(build([0])) == 1
assert min_camera_cover(build([0, 0, 0])) == 1


def _exact(root):
    INF = float("inf")
    def dfs(n):
        if n is None:
            return INF, 0, 0
        la, lb, lc = dfs(n.left); ra, rb, rc = dfs(n.right)
        return (1 + min(la, lb, lc) + min(ra, rb, rc),
                min(la + min(ra, rb), ra + min(la, lb)), lb + rb)
    a, b, _ = dfs(root)
    return min(a, b)

for seed in range(60):
    t = random_tree(1 + seed % 25, seed)
    assert min_camera_cover(t) == _exact(t), seed''',
    ),

    dict(
        id="distribute-coins",
        lc=979, slug="distribute-coins-in-binary-tree",
        name="Distribute Coins in Binary Tree",
        difficulty="medium",
        framing=[
            "There are <code>n</code> coins spread over <code>n</code> nodes. A move sends one coin across one edge. Find the minimum number of moves to give every node exactly one coin. It is also a modification problem in spirit: you are rebalancing a quantity across the tree.",
        ],
        approaches=[
            dict(
                name="Postorder excess flow",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Think about each edge, not each coin. A subtree with <code>size</code> nodes and <code>coins</code> coins has an excess of <code>coins - size</code>, and exactly that many coins must cross the edge to its parent (upward if positive, downward if negative). Coins crossing an edge in opposite directions would be wasted, so the minimum is <code>|excess|</code> moves on that edge.",
                    "So return each subtree's excess and add the absolute values of both children's excess at every node. One pass, O(n), O(h).",
                ],
                code='''def distribute_coins(root):
    moves = 0

    def excess(node):
        nonlocal moves
        if node is None:
            return 0
        left, right = excess(node.left), excess(node.right)
        moves += abs(left) + abs(right)       # coins crossing the two child edges
        return node.val + left + right - 1    # what this subtree sends upward

    excess(root)
    return moves''',
            ),
        ],
        tests='''assert distribute_coins(build([3, 0, 0])) == 2
assert distribute_coins(build([0, 3, 0])) == 3
assert distribute_coins(build([1, 0, 2])) == 2
assert distribute_coins(build([1])) == 0
assert distribute_coins(build([0, 0, None, 3])) == 3''',
    ),
    ],
),

# ---------------------------------------------------------------- subtree aggregation
dict(
    id="subtree-aggregation",
    title="Counting over subtrees",
    idea=[
        "Every subtree has a size, a sum, a minimum, a maximum, an average. Computing them all is one postorder pass; the problems differ in which aggregate they need and what they do with it.",
    ],
    problems=[

    dict(
        id="count-good-nodes",
        lc=1448, slug="count-good-nodes-in-binary-tree",
        name="Count Good Nodes in Binary Tree",
        difficulty="medium",
        framing=[
            "A node is good if no node on the path from the root to it has a greater value. Count them. The aggregate here flows <em>down</em> &mdash; the maximum on the path so far &mdash; which makes it the top-down counterpart of the rest of this group.",
        ],
        approaches=[
            dict(
                name="Carry the path maximum down",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Pass the largest value seen on the path from the root. A node is good if it is at least that large, and it raises the maximum for its children.",
                    "O(n) time, O(h) stack &mdash; the same shape as Maximum Difference Between Node and Ancestor with one bound instead of two.",
                ],
                code='''def good_nodes(root):
    def dfs(node, best):
        if node is None:
            return 0
        good = node.val >= best
        best = max(best, node.val)
        return good + dfs(node.left, best) + dfs(node.right, best)

    return dfs(root, root.val)''',
            ),
        ],
        tests='''assert good_nodes(build([3, 1, 4, 3, None, 1, 5])) == 4
assert good_nodes(build([3, 3, None, 4, 2])) == 3
assert good_nodes(build([1])) == 1''',
    ),

    dict(
        id="nodes-equal-average",
        lc=2265, slug="count-nodes-equal-to-average-of-subtree",
        name="Count Nodes Equal to Average of Subtree",
        difficulty="medium",
        framing=[
            "Count nodes whose value equals the average of their subtree, rounded down. An average needs two aggregates &mdash; sum and size &mdash; so each call returns a pair.",
        ],
        approaches=[
            dict(
                name="Return (sum, size)",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Each subtree reports its sum and node count; the parent adds its own value and one node, then checks <code>total // size == node.val</code>.",
                    "Computing each subtree's sum from scratch at every node would be O(n&sup2;) on a chain. Returning the aggregates lets every ancestor reuse them: O(n).",
                ],
                code='''def average_of_subtree(root):
    count = 0

    def dfs(node):
        nonlocal count
        if node is None:
            return 0, 0
        ls, ln = dfs(node.left)
        rs, rn = dfs(node.right)
        total, size = ls + rs + node.val, ln + rn + 1
        count += total // size == node.val
        return total, size

    dfs(root)
    return count''',
            ),
        ],
        tests='''assert average_of_subtree(build([4, 8, 5, 0, 1, None, 6])) == 5
assert average_of_subtree(build([1])) == 1
assert average_of_subtree(build([1, 2, 3])) == 2''',
    ),

    dict(
        id="most-frequent-subtree-sum",
        lc=508, slug="most-frequent-subtree-sum",
        name="Most Frequent Subtree Sum",
        difficulty="medium",
        framing=[
            "Compute every subtree's sum and return the most frequent sums (all of them, if tied). One postorder pass feeds a counter.",
        ],
        approaches=[
            dict(
                name="Postorder sums into a Counter",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Each call returns its subtree sum and records it. At the end, find the top count and return every sum with that count.",
                    "O(n) time; the counter can hold n distinct sums.",
                ],
                code='''def find_frequent_tree_sum(root):
    counts = Counter()

    def total(node):
        if node is None:
            return 0
        s = node.val + total(node.left) + total(node.right)
        counts[s] += 1
        return s

    total(root)
    if not counts:
        return []
    top = max(counts.values())
    return [s for s, c in counts.items() if c == top]''',
            ),
        ],
        tests='''assert sorted(find_frequent_tree_sum(build([5, 2, -3]))) == [-3, 2, 4]
assert find_frequent_tree_sum(build([5, 2, -5])) == [2]
assert find_frequent_tree_sum(None) == []''',
    ),

    dict(
        id="find-duplicate-subtrees",
        lc=652, slug="find-duplicate-subtrees",
        name="Find Duplicate Subtrees",
        difficulty="medium",
        framing=[
            "Return one root for every subtree shape-and-value that appears more than once. To compare subtrees you need a canonical key for each; the choice of key is the difference between O(n&sup2;) and O(n).",
        ],
        approaches=[
            dict(
                name="Intern each subtree as an integer id",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Give every distinct subtree a small integer id. A subtree is identified by the triple <code>(left id, value, right id)</code>, and a dict maps triples to ids. Two subtrees are identical exactly when they get the same id.",
                    "Each triple has constant size, so each node costs O(1) hashing: O(n) overall. Record a node the second time its id is seen, so each duplicate shape is reported once.",
                ],
                code='''def find_duplicate_subtrees(root):
    ids, seen, out = {}, Counter(), []

    def key(node):
        if node is None:
            return 0
        triple = (key(node.left), node.val, key(node.right))
        uid = ids.setdefault(triple, len(ids) + 1)
        seen[uid] += 1
        if seen[uid] == 2:
            out.append(node)
        return uid

    key(root)
    return out''',
            ),
            dict(
                name="Serialize every subtree to a string",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                tag="the usual first answer",
                why=[
                    "Build a string like <code>\"(2,(4,#,#),#)\"</code> for each subtree and count them. Correct, but each string is as long as its subtree, and building it copies the children's strings: on a chain that is 1 + 2 + &hellip; + n characters, O(n&sup2;) time and memory.",
                    "The id version is the same idea with each child's string replaced by a number that stands for it.",
                ],
                code='''def find_duplicate_subtrees(root):
    seen, out = Counter(), []

    def key(node):
        if node is None:
            return "#"
        s = f"({node.val},{key(node.left)},{key(node.right)})"
        seen[s] += 1
        if seen[s] == 2:
            out.append(node)
        return s

    key(root)
    return out''',
            ),
        ],
        tests='''got = find_duplicate_subtrees(build([1, 2, 3, 4, None, 2, 4, None, None, 4]))
assert sorted(level_order(t) for t in got) == [[2, 4], [4]]
got = find_duplicate_subtrees(build([2, 1, 1]))
assert [level_order(t) for t in got] == [[1]]
got = find_duplicate_subtrees(build([2, 2, 2, 3, None, 3, None]))
assert sorted(level_order(t) for t in got) == [[2, 3], [3]]''',
    ),
    ],
),

# ---------------------------------------------------------------- Morris
dict(
    id="morris",
    title="Morris traversal: O(1) extra space",
    idea=[
        "Every traversal so far used O(h) memory for a stack, explicit or implicit. Morris traversal uses none: it temporarily threads the tree itself, pointing each left subtree's rightmost node back at its ancestor, and removes every thread before it finishes.",
    ],
    problems=[

    dict(
        id="kth-smallest-bst",
        lc=230, slug="kth-smallest-element-in-a-bst",
        name="Kth Smallest Element in a BST",
        difficulty="medium",
        framing=[
            "Return the k-th smallest value in a BST. Inorder traversal visits a BST in sorted order, so the answer is the k-th node inorder visits &mdash; and the traversal can stop there.",
            "It is also the cleanest place to practise Morris inorder (introduced with Binary Tree Inorder Traversal earlier in this path): the same O(1)-space walk, stopped early. Morris preorder differs only in emitting a node when the thread is <em>created</em> rather than when it is followed back.",
        ],
        pitfall="Stopping a Morris traversal early without removing the threads it has created. The function returns the right answer and leaves the caller's tree corrupted, with cycles in it.",
        approaches=[
            dict(
                name="Iterative inorder, stop at k",
                time="O(h + k)",
                space="O(h)",
                best=True,
                why=[
                    "Push the left spine, pop, count, move right. The first pop is the minimum after O(h) work, and each further pop is the next value in order, so the k-th pop is the answer after O(h + k) steps &mdash; the rest of the tree is never touched.",
                    "The follow-up question \"what if the BST is modified often and kth smallest is queried often?\" is answered by augmenting each node with its subtree size, which gives O(h) per query.",
                ],
                code='''def kth_smallest(root, k):
    stack, node = [], root
    while True:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right''',
            ),
            dict(
                name="Morris inorder, stopped at k",
                time="O(n)",
                space="O(1)",
                tag="no stack",
                why=[
                    "At a node with a left subtree, find that subtree's rightmost node (the node's inorder predecessor). If its <code>right</code> is empty, create a thread back to the current node and go left. If the thread is already there, the left subtree is finished: remove the thread, visit the node, go right. A node without a left subtree is visited immediately.",
                    "Each edge is walked a constant number of times, so O(n) time, and nothing is stored beyond a couple of pointers: O(1) space. The price is that the tree is temporarily modified, so it is unsafe if another thread is reading it.",
                    "To stop early at the k-th node, this version records the answer and keeps going until every thread has been removed. Finishing costs O(n) instead of O(h + k); returning immediately would be faster and would leave threads behind.",
                ],
                code='''def kth_smallest(root, k):
    answer, node = None, root
    while node is not None:
        if node.left is None:
            k -= 1
            if k == 0:
                answer = node.val
            node = node.right
            continue
        pred = node.left
        while pred.right is not None and pred.right is not node:
            pred = pred.right
        if pred.right is None:
            pred.right = node               # create the thread, go left
            node = node.left
        else:
            pred.right = None               # left side done: remove the thread
            k -= 1
            if k == 0:
                answer = node.val
            node = node.right
    return answer''',
            ),
        ],
        tests='''t = build([3, 1, 4, None, 2])
assert kth_smallest(t, 1) == 1
assert level_order(t) == [3, 1, 4, None, 2]            # the tree is left intact
t = build([5, 3, 6, 2, 4, None, None, 1])
assert [kth_smallest(t, k) for k in range(1, 7)] == [1, 2, 3, 4, 5, 6]
for seed in range(20):
    t = random_bst(1 + seed * 3, seed)
    before, values = shape(t), vals_in(t)
    k = 1 + seed % len(values)
    assert kth_smallest(t, k) == values[k - 1], seed
    assert shape(t) == before, seed''',
    ),
    ],
),
]
