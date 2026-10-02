# -*- coding: utf-8 -*-
"""Binary Trees: views, construction from traversals, serialization."""

SECTIONS = [

# ---------------------------------------------------------------- views
dict(
    id="views",
    title="Tree views: what each level, or each column, shows",
    idea=[
        "A view keeps one node per level (left and right views) or per column (top and bottom views). Level-based views fall out of BFS; DFS can do them too by visiting children in the right order and recording the first node seen at each depth.",
    ],
    problems=[

    dict(
        id="right-side-view",
        lc=199, slug="binary-tree-right-side-view",
        name="Binary Tree Right Side View",
        difficulty="medium",
        framing=[
            "Standing to the right of the tree, list the values you can see from top to bottom: the <strong>last</strong> node of every level. The left view is the mirror image &mdash; the first node of every level &mdash; and the same two solutions produce it with one change each.",
        ],
        pitfall="Walking only right children. In <code>[1, 2, 3, 4]</code> the node 4 hangs off the <em>left</em> subtree, yet it is visible from the right because nothing is to its right on its level.",
        approaches=[
            dict(
                name="BFS, keep the last node of each level",
                time="O(n)",
                space="O(w)",
                best=True,
                why=[
                    "Process the tree level by level with the size snapshot; the node popped last in each level is the one seen from the right. For the left view, keep the first instead.",
                    "O(n) time, O(w) queue.",
                ],
                code='''def right_side_view(root):
    view, queue = [], deque([root] if root else [])
    while queue:
        for _ in range(len(queue)):
            node = queue.popleft()          # the last one popped is the rightmost
            for child in (node.left, node.right):
                if child is not None:
                    queue.append(child)
        view.append(node.val)
    return view''',
            ),
            dict(
                name="DFS right-first, first node per depth",
                time="O(n)",
                space="O(h)",
                why=[
                    "Visit the right child before the left. Then the first node reached at each depth is the rightmost one on that level, and it is recorded when <code>depth == len(view)</code> &mdash; the moment a new depth is first reached.",
                    "Left view: visit left first instead. O(n) time and O(h) stack, which beats BFS's O(w) on a wide, balanced tree.",
                ],
                code='''def right_side_view(root):
    view = []

    def dfs(node, depth):
        if node is None:
            return
        if depth == len(view):            # first visit to this depth
            view.append(node.val)
        dfs(node.right, depth + 1)        # right first
        dfs(node.left, depth + 1)

    dfs(root, 0)
    return view''',
            ),
        ],
        tests='''assert right_side_view(build([1, 2, 3, None, 5, None, 4])) == [1, 3, 4]
assert right_side_view(build([1, None, 3])) == [1, 3]
assert right_side_view(None) == []
assert right_side_view(build([1, 2, 3, 4])) == [1, 3, 4]
assert right_side_view(build([1, 2, 3, 4, 5, 6, 7, None, 8])) == [1, 3, 7, 8]''',
    ),

    dict(
        id="top-bottom-view",
        name="Top View and Bottom View",
        difficulty="medium",
        tags=["Tree", "Breadth-First Search", "Hash Table", "Concept"],
        statement=[
            "Give every node a <strong>column</strong>: the root is column 0, a left child is one column left of its parent, a right child one column right.",
            "The <strong>top view</strong> lists, from the leftmost column to the rightmost, the node you would see looking down from above: the <em>shallowest</em> node in each column. The <strong>bottom view</strong> lists the <em>deepest</em> node in each column; when two nodes share a column and a depth, take the one that comes later in level order (further right).",
            "Not a LeetCode problem, but a common interview question, and the natural companion to the left and right views: those keep one node per level, these keep one per column.",
        ],
        examples=[
            dict(input="root = [1,2,3,4,5,6,7]", output="top = [4,2,1,3,7], bottom = [4,2,6,3,7]",
                 explanation="Column 0 holds 1 (depth 0), then 5 and 6 (depth 2). Top keeps 1; bottom keeps 6, the later of the two deepest."),
        ],
        constraints=["<code>0 &lt;= n &lt;= 10<sup>4</sup></code>"],
        approaches=[
            dict(
                name="BFS with column numbers",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "BFS visits nodes in increasing depth, and within a depth from left to right. So for the top view, the <em>first</em> node BFS meets in each column is the answer &mdash; record it only if the column is new. For the bottom view, overwrite on every visit, so the <em>last</em> one wins.",
                    "Track the smallest and largest column seen, then read the dict from left to right: O(n) with no sort, since columns are contiguous integers.",
                    "DFS would work only if it also tracked depth and compared depths explicitly, because DFS can reach a deep node in a column before a shallow one. BFS gets the ordering for free.",
                ],
                code='''def top_and_bottom_view(root):
    if root is None:
        return [], []
    top, bottom = {}, {}
    queue = deque([(root, 0)])
    while queue:
        node, col = queue.popleft()
        top.setdefault(col, node.val)      # first seen: shallowest
        bottom[col] = node.val             # last seen: deepest, rightmost
        if node.left is not None:
            queue.append((node.left, col - 1))
        if node.right is not None:
            queue.append((node.right, col + 1))
    cols = range(min(top), max(top) + 1)
    return [top[c] for c in cols], [bottom[c] for c in cols]''',
            ),
        ],
        tests='''assert top_and_bottom_view(build([1, 2, 3, 4, 5, 6, 7])) == ([4, 2, 1, 3, 7], [4, 2, 6, 3, 7])
assert top_and_bottom_view(None) == ([], [])
assert top_and_bottom_view(build([1, 2, 3, None, 4, None, None, None, 5, None, 6])) == ([2, 1, 3, 6], [2, 4, 5, 6])''',
    ),

    dict(
        id="bottom-left-value",
        lc=513, slug="find-bottom-left-tree-value",
        name="Find Bottom Left Tree Value",
        difficulty="medium",
        framing=[
            "Return the leftmost value in the <em>last</em> row. That is the left view's final entry &mdash; but you can get it without building the whole view.",
        ],
        approaches=[
            dict(
                name="BFS right-to-left, last node wins",
                time="O(n)",
                space="O(w)",
                best=True,
                why=[
                    "Enqueue the right child before the left. The very last node dequeued is then the leftmost node of the deepest level, so no level bookkeeping is needed at all.",
                    "It is a small trick worth knowing: reversing the child order turns \"first of the last level\" into \"last of everything\".",
                ],
                code='''def find_bottom_left_value(root):
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node.right is not None:
            queue.append(node.right)       # right first ...
        if node.left is not None:
            queue.append(node.left)        # ... so the leftmost comes out last
    return node.val''',
            ),
            dict(
                name="DFS left-first, first node at a new depth",
                time="O(n)",
                space="O(h)",
                why=[
                    "Visit left before right and remember the first node seen at the deepest depth so far. A strictly greater depth replaces it; an equal depth does not, so the leftmost one stays.",
                ],
                code='''def find_bottom_left_value(root):
    best_depth, best = -1, None

    def dfs(node, depth):
        nonlocal best_depth, best
        if node is None:
            return
        if depth > best_depth:
            best_depth, best = depth, node.val
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return best''',
            ),
        ],
        tests='''assert find_bottom_left_value(build([2, 1, 3])) == 1
assert find_bottom_left_value(build([1, 2, 3, 4, None, 5, 6, None, None, 7])) == 7
assert find_bottom_left_value(build([1])) == 1
assert find_bottom_left_value(build([1, None, 2, None, 3])) == 3''',
    ),

    dict(
        id="add-one-row",
        lc=623, slug="add-one-row-to-tree",
        name="Add One Row to Tree",
        difficulty="medium",
        framing=[
            "Insert a new row of nodes with value <code>val</code> at depth <code>depth</code>. Each node at depth <code>depth - 1</code> gets two new children, and its old left subtree becomes the new left child's left subtree (right likewise). A level-based <em>edit</em> rather than a level-based read.",
        ],
        pitfall="Forgetting <code>depth == 1</code>, where there is no parent level: the new node becomes the root and the old tree hangs off its left.",
        approaches=[
            dict(
                name="BFS to the level above, then splice",
                time="O(n)",
                space="O(w)",
                best=True,
                why=[
                    "Walk down <code>depth - 2</code> levels, so the queue holds exactly the nodes at depth <code>depth - 1</code>. For each, create the two new nodes and re-hang the old children underneath them.",
                    "Only nodes above the insertion point are visited, so it is O(n) worst case but often much less.",
                ],
                code='''def add_one_row(root, val, depth):
    if depth == 1:
        return TreeNode(val, root, None)
    level = [root]
    for _ in range(depth - 2):
        level = [c for n in level for c in (n.left, n.right) if c is not None]
    for node in level:
        node.left = TreeNode(val, node.left, None)
        node.right = TreeNode(val, None, node.right)
    return root''',
            ),
            dict(
                name="DFS carrying the depth",
                time="O(n)",
                space="O(h)",
                why=[
                    "Recurse with the current depth; at <code>depth - 1</code> do the splice and stop descending.",
                ],
                code='''def add_one_row(root, val, depth):
    if depth == 1:
        return TreeNode(val, root, None)

    def dfs(node, d):
        if node is None:
            return
        if d == depth - 1:
            node.left = TreeNode(val, node.left, None)
            node.right = TreeNode(val, None, node.right)
            return
        dfs(node.left, d + 1)
        dfs(node.right, d + 1)

    dfs(root, 1)
    return root''',
            ),
        ],
        tests='''assert level_order(add_one_row(build([4, 2, 6, 3, 1, 5]), 1, 2)) == [4, 1, 1, 2, None, None, 6, 3, 1, 5]
assert level_order(add_one_row(build([4, 2, None, 3, 1]), 1, 3)) == [4, 2, None, 1, 1, 3, None, None, 1]
assert level_order(add_one_row(build([1, 2, 3]), 9, 1)) == [9, 1, None, 2, 3]
assert level_order(add_one_row(build([1, 2, 3]), 9, 3)) == [1, 2, 3, 9, 9, 9, 9]''',
    ),

    dict(
        id="average-of-levels",
        lc=637, slug="average-of-levels-in-binary-tree",
        name="Average of Levels in Binary Tree",
        difficulty="easy",
        framing=[
            "Return the average value of each level. The template is level-order traversal; the only question is whether you accumulate per level in BFS or per depth in DFS.",
        ],
        approaches=[
            dict(
                name="BFS, one level at a time",
                time="O(n)",
                space="O(w)",
                best=True,
                why=[
                    "The size snapshot tells you exactly how many nodes the level has, so the sum divided by that count is the average. Nothing is stored beyond the queue.",
                ],
                code='''def average_of_levels(root):
    out, queue = [], deque([root] if root else [])
    while queue:
        size, total = len(queue), 0
        for _ in range(size):
            node = queue.popleft()
            total += node.val
            for child in (node.left, node.right):
                if child is not None:
                    queue.append(child)
        out.append(total / size)
    return out''',
            ),
            dict(
                name="DFS with per-depth sums and counts",
                time="O(n)",
                space="O(h)",
                why=[
                    "Accumulate <code>sums[depth]</code> and <code>counts[depth]</code> in any traversal order and divide at the end. The two lists have one entry per level, which is at most O(h).",
                ],
                code='''def average_of_levels(root):
    sums, counts = [], []

    def dfs(node, depth):
        if node is None:
            return
        if depth == len(sums):
            sums.append(0); counts.append(0)
        sums[depth] += node.val
        counts[depth] += 1
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return [s / c for s, c in zip(sums, counts)]''',
            ),
        ],
        tests='''assert average_of_levels(build([3, 9, 20, None, None, 15, 7])) == [3.0, 14.5, 11.0]
assert average_of_levels(build([3, 9, 20, 15, 7])) == [3.0, 14.5, 11.0]
assert average_of_levels(build([2147483647, 2147483647, 2147483647])) == [2147483647.0, 2147483647.0]''',
    ),

    dict(
        id="deepest-leaves-sum",
        lc=1302, slug="deepest-leaves-sum",
        name="Deepest Leaves Sum",
        difficulty="medium",
        framing=[
            "Sum the values on the deepest level. BFS finds the last level by definition; a one-pass DFS needs to <em>reset</em> its running sum whenever it discovers a deeper level.",
        ],
        approaches=[
            dict(
                name="BFS, the last level's sum",
                time="O(n)",
                space="O(w)",
                best=True,
                why=[
                    "Compute each level's sum and overwrite; when the queue empties, the last value written belongs to the deepest level.",
                ],
                code='''def deepest_leaves_sum(root):
    level = [root]
    while level:
        total = sum(n.val for n in level)
        level = [c for n in level for c in (n.left, n.right) if c is not None]
    return total''',
            ),
            dict(
                name="One-pass DFS with a reset",
                time="O(n)",
                space="O(h)",
                why=[
                    "Track the deepest depth seen and the sum at that depth. A node deeper than anything so far starts a new sum; a node at the current deepest depth adds to it.",
                ],
                code='''def deepest_leaves_sum(root):
    deepest, total = -1, 0

    def dfs(node, depth):
        nonlocal deepest, total
        if node is None:
            return
        if depth > deepest:
            deepest, total = depth, 0        # a deeper level: start over
        if depth == deepest:
            total += node.val
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 0)
    return total''',
            ),
        ],
        tests='''assert deepest_leaves_sum(build([1, 2, 3, 4, 5, None, 6, 7, None, None, None, None, 8])) == 15
assert deepest_leaves_sum(build([6, 7, 8, 2, 7, 1, 3, 9, None, 1, 4, None, None, None, 5])) == 19
assert deepest_leaves_sum(build([5])) == 5''',
    ),
    ],
),

# ---------------------------------------------------------------- construction
dict(
    id="construction",
    title="Construction: rebuilding a tree from its traversals",
    idea=[
        "Preorder is root, left, right; inorder is left, root, right; postorder is left, right, root. Preorder or postorder tells you where the root is. Inorder tells you how many nodes are on each side of it. Together they pin the tree down.",
    ],
    problems=[

    dict(
        id="build-from-preorder-inorder",
        lc=105, slug="construct-binary-tree-from-preorder-and-inorder-traversal",
        name="Construct Binary Tree from Preorder and Inorder Traversal",
        difficulty="medium",
        framing=[
            "Values are unique. Rebuild the tree. The first preorder value is the root; finding it in inorder splits the remaining values into the left subtree (everything before it) and the right subtree (everything after). Recurse on both sides &mdash; divide and conquer.",
            "The two versions below differ in one thing: how they find the root in inorder. That single lookup is the difference between O(n&sup2;) and O(n).",
        ],
        approaches=[
            dict(
                name="Index map and a moving preorder pointer",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Build <code>{value: index}</code> for inorder once, so locating the root is O(1). Instead of slicing arrays, recurse on an inorder range <code>[lo, hi]</code> and consume preorder with a single pointer: because preorder lists the whole left subtree before the right, building left first always takes the next preorder value in the right order.",
                    "Each node is created once with O(1) work: O(n) time. The map is O(n) and the stack O(h).",
                ],
                code='''def build_tree(preorder, inorder):
    where = {v: i for i, v in enumerate(inorder)}
    nxt = 0

    def make(lo, hi):                       # inorder[lo..hi]
        nonlocal nxt
        if lo > hi:
            return None
        val = preorder[nxt]; nxt += 1
        mid = where[val]
        node = TreeNode(val)
        node.left = make(lo, mid - 1)       # left must be built first
        node.right = make(mid + 1, hi)
        return node

    return make(0, len(inorder) - 1)''',
            ),
            dict(
                name="Slice and search",
                time="O(n&sup2;)",
                space="O(n&sup2;)",
                tag="direct translation",
                why=[
                    "The definition, transcribed: find the root with <code>inorder.index</code> (O(n)), slice both lists, recurse. On a balanced tree it is O(n log n), but on a chain every level scans and copies O(n) elements: O(n&sup2;) time, and the slices alive on the stack add up to O(n&sup2;) memory.",
                    "Say this first to show you have the idea, then fix both costs: a hash map for the search and index ranges instead of slices.",
                ],
                code='''def build_tree(preorder, inorder):
    if not preorder:
        return None
    root = TreeNode(preorder[0])
    mid = inorder.index(preorder[0])
    root.left = build_tree(preorder[1:mid + 1], inorder[:mid])
    root.right = build_tree(preorder[mid + 1:], inorder[mid + 1:])
    return root''',
            ),
        ],
        tests='''assert level_order(build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])) == [3, 9, 20, None, None, 15, 7]
assert level_order(build_tree([-1], [-1])) == [-1]
assert build_tree([], []) is None
for seed in range(30):
    t = random_tree(1 + seed % 20, seed, 0, 99, distinct=True)
    assert shape(build_tree(vals_pre(t), vals_in(t))) == shape(t), seed''',
    ),

    dict(
        id="build-from-inorder-postorder",
        lc=106, slug="construct-binary-tree-from-inorder-and-postorder-traversal",
        name="Construct Binary Tree from Inorder and Postorder Traversal",
        difficulty="medium",
        framing=[
            "The same problem with postorder, whose <em>last</em> value is the root. Read postorder from the end and you meet root, right subtree, left subtree &mdash; so the right subtree must be built first.",
        ],
        pitfall="Building the left subtree first while consuming postorder from the end. The pointer is then handing out right-subtree values to the left subtree.",
        approaches=[
            dict(
                name="Index map, consume postorder from the end",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Exactly the previous solution mirrored: the pointer starts at the end of postorder and moves left, and the recursion builds <code>right</code> before <code>left</code> to match the order values come out.",
                    "O(n) time with the index map; O(n) for the map, O(h) stack.",
                ],
                code='''def build_tree(inorder, postorder):
    where = {v: i for i, v in enumerate(inorder)}
    nxt = len(postorder) - 1

    def make(lo, hi):
        nonlocal nxt
        if lo > hi:
            return None
        val = postorder[nxt]; nxt -= 1
        mid = where[val]
        node = TreeNode(val)
        node.right = make(mid + 1, hi)      # right first: reading backwards
        node.left = make(lo, mid - 1)
        return node

    return make(0, len(inorder) - 1)''',
            ),
        ],
        tests='''assert level_order(build_tree([9, 3, 15, 20, 7], [9, 15, 7, 20, 3])) == [3, 9, 20, None, None, 15, 7]
assert level_order(build_tree([-1], [-1])) == [-1]
for seed in range(30):
    t = random_tree(1 + seed % 20, seed, 0, 99, distinct=True)
    assert shape(build_tree(vals_in(t), vals_post(t))) == shape(t), seed''',
    ),

    dict(
        id="build-from-preorder-postorder",
        lc=889, slug="construct-binary-tree-from-preorder-and-postorder-traversal",
        name="Construct Binary Tree from Preorder and Postorder Traversal",
        difficulty="medium",
        framing=[
            "Without inorder, the answer is <strong>not unique</strong>: <code>1 &rarr; 2</code> with 2 as a left child and with 2 as a right child have the same preorder <code>[1, 2]</code> and postorder <code>[2, 1]</code>. LeetCode accepts any valid tree. When every node has zero or two children (a <em>full</em> binary tree), the answer is unique.",
            "The split comes from the second preorder value, which must be the root of the left subtree (by convention, when there is only one child). Its position in postorder marks the end of that subtree.",
        ],
        approaches=[
            dict(
                name="Index map on postorder",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "For a subtree occupying <code>pre[a..b]</code>, the root is <code>pre[a]</code> and, if there are more nodes, <code>pre[a+1]</code> is the left child. Everything up to that child's position in postorder is its subtree, so the left subtree has <code>post_index[pre[a+1]] - post_lo + 1</code> nodes. The rest is the right subtree.",
                    "With a value-to-index map for postorder, each node is O(1): O(n) total.",
                ],
                code='''def construct_from_pre_post(preorder, postorder):
    where = {v: i for i, v in enumerate(postorder)}

    def make(pre_lo, pre_hi, post_lo):
        if pre_lo > pre_hi:
            return None
        node = TreeNode(preorder[pre_lo])
        if pre_lo == pre_hi:
            return node
        left_size = where[preorder[pre_lo + 1]] - post_lo + 1
        node.left = make(pre_lo + 1, pre_lo + left_size, post_lo)
        node.right = make(pre_lo + left_size + 1, pre_hi, post_lo + left_size)
        return node

    return make(0, len(preorder) - 1, 0)''',
            ),
        ],
        tests='''t = construct_from_pre_post([1, 2, 4, 5, 3, 6, 7], [4, 5, 2, 6, 7, 3, 1])
assert level_order(t) == [1, 2, 3, 4, 5, 6, 7]
assert level_order(construct_from_pre_post([1], [1])) == [1]
# not unique in general: any tree with matching traversals is accepted
for seed in range(30):
    t = random_tree(1 + seed % 20, seed, 0, 99, distinct=True)
    got = construct_from_pre_post(vals_pre(t), vals_post(t))
    assert vals_pre(got) == vals_pre(t) and vals_post(got) == vals_post(t), seed''',
    ),

    dict(
        id="construct-string-from-tree",
        lc=606, slug="construct-string-from-binary-tree",
        name="Construct String from Binary Tree",
        difficulty="medium",
        framing=[
            "Serialize the tree in preorder with parentheses around each child, omitting empty pairs that do not change the meaning. The one pair you must keep is an empty left <code>()</code> when there is a right child &mdash; otherwise the right child would be read as the left.",
        ],
        approaches=[
            dict(
                name="Preorder with the empty-left rule",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Four cases: no children, write the value; left only, <code>val(left)</code>; right only, <code>val()(right)</code>; both, <code>val(left)(right)</code>.",
                    "Collect the pieces in one list and join once. Concatenating strings on the way back up instead copies each subtree's text at every ancestor: O(n &middot; h).",
                ],
                code='''def tree2str(root):
    parts = []

    def walk(node):
        parts.append(str(node.val))
        if node.left is None and node.right is None:
            return
        parts.append("(")
        if node.left is not None:
            walk(node.left)
        parts.append(")")
        if node.right is not None:
            parts.append("(")
            walk(node.right)
            parts.append(")")

    walk(root)
    return "".join(parts)''',
            ),
        ],
        tests='''assert tree2str(build([1, 2, 3, 4])) == "1(2(4))(3)"
assert tree2str(build([1, 2, 3, None, 4])) == "1(2()(4))(3)"
assert tree2str(build([1])) == "1"
assert tree2str(build([1, None, 2])) == "1()(2)"''',
    ),

    dict(
        id="maximum-binary-tree",
        lc=654, slug="maximum-binary-tree",
        name="Maximum Binary Tree",
        difficulty="medium",
        framing=[
            "Build a tree from an array of distinct numbers: the maximum is the root, the part to its left builds the left subtree and the part to its right builds the right subtree. The definition is already a divide-and-conquer algorithm; a monotonic stack does it in one pass.",
        ],
        approaches=[
            dict(
                name="Monotonic decreasing stack",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Scan left to right keeping a stack of nodes with decreasing values &mdash; the current right spine of the tree built so far. A new value pops every smaller node; the last one popped becomes its left child (it was the maximum of the part just to its left). If a larger node remains on the stack, the new node becomes its right child.",
                    "Every node is pushed and popped at most once: O(n). The stack is O(n) for sorted input.",
                ],
                code='''def construct_maximum_binary_tree(nums):
    stack = []
    for v in nums:
        node, last = TreeNode(v), None
        while stack and stack[-1].val < v:
            last = stack.pop()
        node.left = last                   # biggest of the smaller ones to our left
        if stack:
            stack[-1].right = node         # we are the max to its right, so far
        stack.append(node)
    return stack[0] if stack else None''',
            ),
            dict(
                name="Recursive divide and conquer",
                time="O(n&sup2;) worst",
                space="O(n)",
                why=[
                    "Find the maximum in the range, recurse on both sides. Each level of recursion scans its range, so balanced splits give O(n log n) but sorted input &mdash; one-sided splits &mdash; gives O(n&sup2;), like quicksort with a bad pivot.",
                ],
                code='''def construct_maximum_binary_tree(nums):
    def make(lo, hi):
        if lo > hi:
            return None
        m = max(range(lo, hi + 1), key=nums.__getitem__)
        return TreeNode(nums[m], make(lo, m - 1), make(m + 1, hi))

    return make(0, len(nums) - 1)''',
            ),
        ],
        tests='''assert level_order(construct_maximum_binary_tree([3, 2, 1, 6, 0, 5])) == [6, 3, 5, None, 2, 0, None, None, 1]
assert level_order(construct_maximum_binary_tree([3, 2, 1])) == [3, None, 2, None, 1]
assert level_order(construct_maximum_binary_tree([1, 2, 3])) == [3, 2, None, 1]''',
    ),
    ],
),

# ---------------------------------------------------------------- serialization
dict(
    id="serialization",
    title="Serialization: a tree to a string and back",
    idea=[
        "A traversal alone is ambiguous; a traversal with null markers is not. And when the tree is a BST, its ordering is information you do not have to write down.",
    ],
    problems=[

    dict(
        id="serialize-deserialize-tree",
        lc=297, slug="serialize-and-deserialize-binary-tree",
        name="Serialize and Deserialize Binary Tree",
        difficulty="hard",
        framing=[
            "Design <code>serialize(root) -> str</code> and <code>deserialize(str) -> root</code> so that the round trip reproduces any binary tree, including duplicate and negative values.",
            "The previous section needed two traversals because one traversal loses the shape. Writing a <strong>null marker</strong> for every missing child puts the shape back, so one traversal is enough.",
        ],
        approaches=[
            dict(
                name="Preorder with null markers",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Serialize: preorder, writing <code>#</code> for every <code>None</code>. Deserialize: read tokens in the same order &mdash; a value creates a node, then its left subtree is built from the following tokens, then its right. A <code>#</code> returns <code>None</code>, which is what tells the reader a subtree has ended.",
                    "There are n values and n + 1 markers, so the string is O(n) tokens and both directions are O(n). An iterator over the tokens replaces any index bookkeeping.",
                ],
                code='''class Codec:
    def serialize(self, root):
        out = []

        def walk(node):
            if node is None:
                out.append("#")
                return
            out.append(str(node.val))
            walk(node.left)
            walk(node.right)

        walk(root)
        return ",".join(out)

    def deserialize(self, data):
        tokens = iter(data.split(","))

        def make():
            tok = next(tokens)
            if tok == "#":
                return None
            node = TreeNode(int(tok))
            node.left = make()
            node.right = make()
            return node

        return make()''',
            ),
            dict(
                name="Level order with null markers",
                time="O(n)",
                space="O(n)",
                why=[
                    "The LeetCode format itself: BFS, writing <code>#</code> for missing children. Deserializing uses a queue of parents waiting for their two children.",
                    "Also O(n), and immune to recursion depth. Trailing markers can be trimmed to save space; this version keeps them for simplicity.",
                ],
                code='''class Codec:
    def serialize(self, root):
        out, queue = [], deque([root])
        while queue:
            node = queue.popleft()
            if node is None:
                out.append("#")
                continue
            out.append(str(node.val))
            queue.append(node.left)
            queue.append(node.right)
        return ",".join(out)

    def deserialize(self, data):
        tokens = data.split(",")
        if tokens[0] == "#":
            return None
        root = TreeNode(int(tokens[0]))
        queue, i = deque([root]), 1
        while queue:
            node = queue.popleft()
            for side in ("left", "right"):
                if tokens[i] != "#":
                    child = TreeNode(int(tokens[i]))
                    setattr(node, side, child)
                    queue.append(child)
                i += 1
        return root''',
            ),
        ],
        tests='''codec = Codec()
for values in ([1, 2, 3, None, None, 4, 5], [], [1], [-1, -1, None, -1], [1, None, 2, None, 3]):
    tree = build(values)
    assert level_order(codec.deserialize(codec.serialize(tree))) == values, values
for seed in range(30):
    t = random_tree(seed % 25, seed, -50, 50)
    assert shape(codec.deserialize(codec.serialize(t))) == shape(t), seed''',
    ),

    dict(
        id="serialize-deserialize-bst",
        lc=449, slug="serialize-and-deserialize-bst",
        name="Serialize and Deserialize BST",
        difficulty="medium",
        framing=[
            "The same task, but the tree is a BST, and the encoding should be as compact as possible. A BST's preorder alone determines it &mdash; the ordering says where every value goes &mdash; so the null markers are dead weight.",
            "This is the interview distinction: a general tree needs structural information in the string; a BST's structure is implied by its values.",
        ],
        approaches=[
            dict(
                name="Preorder values only, rebuild with bounds",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Serialize the preorder values with no markers. To rebuild, read values in order and place each one using the valid range for the current position: a value belongs to the current subtree only if it lies within <code>(lo, hi)</code>; otherwise that subtree is finished and the value belongs to an ancestor.",
                    "Each value is read once and each bound check is O(1): O(n). This is the same bounds idea as Validate BST, run in reverse.",
                ],
                code='''class Codec:
    def serialize(self, root):
        out = []

        def walk(node):
            if node is not None:
                out.append(str(node.val))
                walk(node.left)
                walk(node.right)

        walk(root)
        return " ".join(out)

    def deserialize(self, data):
        values = [int(x) for x in data.split()]
        i = 0

        def make(lo, hi):
            nonlocal i
            if i == len(values) or not lo < values[i] < hi:
                return None
            node = TreeNode(values[i]); i += 1
            node.left = make(lo, node.val)
            node.right = make(node.val, hi)
            return node

        return make(float("-inf"), float("inf"))''',
            ),
        ],
        tests='''codec = Codec()
assert codec.deserialize(codec.serialize(None)) is None
assert level_order(codec.deserialize(codec.serialize(build([2, 1, 3])))) == [2, 1, 3]
for seed in range(30):
    t = random_bst(seed % 30, seed)
    s = codec.serialize(t)
    assert "#" not in s and "None" not in s          # no structural markers at all
    assert shape(codec.deserialize(s)) == shape(t), seed''',
    ),
    ],
),
]
