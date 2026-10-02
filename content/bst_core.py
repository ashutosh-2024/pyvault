# -*- coding: utf-8 -*-
"""Binary Trees: BST fundamentals, validation, inorder-based problems, range
queries, successor."""

SECTIONS = [

# ---------------------------------------------------------------- basics
dict(
    id="bst-basics",
    title="BST fundamentals: search, insert, delete",
    idea=[
        "A binary search tree keeps every value in a node's left subtree smaller than the node and every value in its right subtree larger &mdash; for the whole subtree, not just the children. Two consequences power everything that follows: each comparison discards a whole subtree, so operations cost O(h); and inorder traversal visits the values in sorted order.",
    ],
    problems=[

    dict(
        id="search-bst",
        lc=700, slug="search-in-a-binary-search-tree",
        name="Search in a Binary Search Tree",
        difficulty="easy",
        framing=[
            "Return the node with value <code>val</code>, or <code>None</code>. The first BST operation and the model for all the others: compare, then discard the half that cannot contain the answer.",
        ],
        approaches=[
            dict(
                name="Iterative descent",
                time="O(h)",
                space="O(1)",
                best=True,
                why=[
                    "Go left if the target is smaller, right if larger, stop on a match or at <code>None</code>. One node per level: O(h) &mdash; O(log n) for a balanced tree and O(n) for a degenerate one, which is the entire reason balanced BSTs exist.",
                    "A loop needs no stack, so O(1) space.",
                ],
                code='''def search_bst(root, val):
    node = root
    while node is not None and node.val != val:
        node = node.left if val < node.val else node.right
    return node''',
            ),
            dict(
                name="Recursive",
                time="O(h)",
                space="O(h)",
                why=[
                    "The same decision, recursively. It is tail recursion, but CPython does not eliminate tail calls, so it still costs O(h) frames.",
                ],
                code='''def search_bst(root, val):
    if root is None or root.val == val:
        return root
    return search_bst(root.left if val < root.val else root.right, val)''',
            ),
        ],
        tests='''t = build([4, 2, 7, 1, 3])
assert level_order(search_bst(t, 2)) == [2, 1, 3]
assert search_bst(t, 5) is None
assert search_bst(None, 1) is None''',
    ),

    dict(
        id="bst-floor-ceiling",
        name="Floor, Ceiling, Min and Max in a BST",
        difficulty="medium",
        tags=["Binary Search Tree", "Tree", "Concept"],
        statement=[
            "Implement four queries on a BST of distinct values: <code>minimum</code>, <code>maximum</code>, <code>floor(x)</code> (the largest value &le; x) and <code>ceiling(x)</code> (the smallest value &ge; x). Return <code>None</code> when no such value exists.",
            "Not a LeetCode problem, but the building blocks of predecessor, successor and range queries &mdash; and what an ordered map (Java's <code>TreeMap.floorKey</code>, C++'s <code>lower_bound</code>) does under the hood.",
        ],
        examples=[
            dict(input="bst = [8,4,12,2,6,10,14], x = 9", output="floor = 8, ceiling = 10"),
            dict(input="bst = [8,4,12,2,6,10,14], x = 1", output="floor = None, ceiling = 2"),
        ],
        constraints=["Values are distinct integers"],
        approaches=[
            dict(
                name="Descend and remember the best candidate",
                time="O(h)",
                space="O(1)",
                best=True,
                why=[
                    "Minimum and maximum are the ends of the left and right spines.",
                    "For the floor of <code>x</code>: at a node larger than <code>x</code>, the floor must be to the left. At a node &le; <code>x</code>, this node is a candidate, but a larger one could still be in the right subtree &mdash; so remember it and go right. The last candidate remembered is the answer. Ceiling is the mirror image.",
                    "Each step goes down a level: O(h), with O(1) extra space.",
                ],
                code='''def bst_min(root):
    while root is not None and root.left is not None:
        root = root.left
    return root.val if root else None


def bst_max(root):
    while root is not None and root.right is not None:
        root = root.right
    return root.val if root else None


def floor(root, x):
    best = None
    while root is not None:
        if root.val > x:
            root = root.left
        else:
            best = root.val              # a candidate; try for a bigger one
            root = root.right
    return best


def ceiling(root, x):
    best = None
    while root is not None:
        if root.val < x:
            root = root.right
        else:
            best = root.val
            root = root.left
    return best''',
            ),
        ],
        tests='''t = build([8, 4, 12, 2, 6, 10, 14])
assert (bst_min(t), bst_max(t)) == (2, 14)
assert (floor(t, 9), ceiling(t, 9)) == (8, 10)
assert (floor(t, 1), ceiling(t, 1)) == (None, 2)
assert (floor(t, 15), ceiling(t, 15)) == (14, None)
assert (floor(t, 6), ceiling(t, 6)) == (6, 6)
import bisect
for seed in range(20):
    t = random_bst(1 + seed * 2, seed, 0, 200)
    vals = vals_in(t)
    for x in range(-5, 206, 7):
        i = bisect.bisect_right(vals, x)
        assert floor(t, x) == (vals[i - 1] if i else None)
        j = bisect.bisect_left(vals, x)
        assert ceiling(t, x) == (vals[j] if j < len(vals) else None)''',
    ),

    dict(
        id="insert-bst",
        lc=701, slug="insert-into-a-binary-search-tree",
        name="Insert into a Binary Search Tree",
        difficulty="medium",
        framing=[
            "Insert a value that is not already present and return the root. There are many valid results, but the simplest is always available: search for the value, and put it where the search falls off the tree. A new value always becomes a leaf.",
        ],
        approaches=[
            dict(
                name="Iterative: walk to the empty slot",
                time="O(h)",
                space="O(1)",
                best=True,
                why=[
                    "Descend as in a search, remembering the parent. When the next step would be <code>None</code>, attach the new node there. No existing node moves, so nothing else can break.",
                ],
                code='''def insert_into_bst(root, val):
    new = TreeNode(val)
    if root is None:
        return new
    node = root
    while True:
        if val < node.val:
            if node.left is None:
                node.left = new
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = new
                return root
            node = node.right''',
            ),
            dict(
                name="Recursive, re-linking on return",
                time="O(h)",
                space="O(h)",
                why=[
                    "Return the subtree root from every call and assign it back: <code>node.left = insert(node.left, val)</code>. For insertion this re-assigns links that did not change, but the same shape is what makes deletion and the self-balancing trees (which <em>do</em> change links on the way back up) straightforward.",
                ],
                code='''def insert_into_bst(root, val):
    if root is None:
        return TreeNode(val)
    if val < root.val:
        root.left = insert_into_bst(root.left, val)
    else:
        root.right = insert_into_bst(root.right, val)
    return root''',
            ),
        ],
        tests='''assert level_order(insert_into_bst(build([4, 2, 7, 1, 3]), 5)) == [4, 2, 7, 1, 3, 5]
assert level_order(insert_into_bst(None, 5)) == [5]
rng = random.Random(1)
for trial in range(20):
    values = rng.sample(range(500), 1 + trial * 3)
    root = None
    for v in values:
        root = insert_into_bst(root, v)
    assert is_valid_bst(root) and vals_in(root) == sorted(values)''',
    ),

    dict(
        id="delete-bst",
        lc=450, slug="delete-node-in-a-bst",
        name="Delete Node in a BST",
        difficulty="medium",
        framing=[
            "Delete the node with value <code>key</code>, if present, and return the root. Three cases, and interviews check that you know all of them:",
            "<strong>A leaf</strong>: just remove it. <strong>One child</strong>: replace the node with that child. <strong>Two children</strong>: the node's place must be taken by a value that keeps the order &mdash; its <em>inorder successor</em> (the minimum of the right subtree) or its <em>inorder predecessor</em> (the maximum of the left subtree). Copy that value in, then delete it from the subtree it came from; it has at most one child, so that deletion is one of the easy cases.",
        ],
        approaches=[
            dict(
                name="Recursive, replace with the successor",
                time="O(h)",
                space="O(h)",
                best=True,
                why=[
                    "Search down, re-linking on the way back so a replaced child is hooked up automatically. At the node: zero or one child means return the other child (which may be <code>None</code>). Two children means find the smallest value in the right subtree, copy it into this node, and delete that value from the right subtree.",
                    "Search, successor search and the second delete are each O(h), so O(h) total.",
                ],
                code='''def delete_node(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = delete_node(root.left, key)
    elif key > root.val:
        root.right = delete_node(root.right, key)
    else:
        if root.left is None:
            return root.right            # leaf or right child only
        if root.right is None:
            return root.left             # left child only
        succ = root.right                # two children: inorder successor
        while succ.left is not None:
            succ = succ.left
        root.val = succ.val
        root.right = delete_node(root.right, succ.val)
    return root''',
            ),
            dict(
                name="Recursive, replace with the predecessor",
                time="O(h)",
                space="O(h)",
                why=[
                    "The mirror image: take the largest value in the left subtree. Both are correct. Always choosing the same side slowly skews the tree over many random deletions (the Hibbard deletion problem); alternating, or using a self-balancing tree, avoids that.",
                ],
                code='''def delete_node(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = delete_node(root.left, key)
    elif key > root.val:
        root.right = delete_node(root.right, key)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        pred = root.left                 # inorder predecessor
        while pred.right is not None:
            pred = pred.right
        root.val = pred.val
        root.left = delete_node(root.left, pred.val)
    return root''',
            ),
        ],
        tests='''assert is_valid_bst(delete_node(build([5, 3, 6, 2, 4, None, 7]), 3))
assert vals_in(delete_node(build([5, 3, 6, 2, 4, None, 7]), 3)) == [2, 4, 5, 6, 7]
assert level_order(delete_node(build([5, 3, 6, 2, 4, None, 7]), 0)) == [5, 3, 6, 2, 4, None, 7]
assert delete_node(None, 0) is None
assert delete_node(build([1]), 1) is None
for seed in range(25):
    t = random_bst(1 + seed * 2, seed)
    remaining = vals_in(t)
    rng = random.Random(seed)
    for key in rng.sample(remaining, len(remaining) // 2) + [-1]:
        t = delete_node(t, key)
        if key in remaining:
            remaining.remove(key)
        assert is_valid_bst(t) and vals_in(t) == remaining, seed''',
    ),
    ],
),

# ---------------------------------------------------------------- validation
dict(
    id="bst-validation",
    title="BST validation: the constraint is subtree-wide",
    idea=[
        "Checking <code>node.left.val &lt; node.val &lt; node.right.val</code> at every node is not enough: a value deep in the left subtree must be smaller than <em>every</em> ancestor it sits to the left of. Validation needs bounds that are passed down, or an inorder sweep.",
    ],
    problems=[

    dict(
        id="validate-bst",
        lc=98, slug="validate-binary-search-tree",
        name="Validate Binary Search Tree",
        difficulty="medium",
        framing=[
            "Decide whether the tree is a valid BST, with strict inequalities (duplicates are not allowed).",
        ],
        pitfall="Comparing each node only with its children. <code>[5, 4, 6, null, null, 3, 7]</code> passes that check at every node, but 3 sits in 5's right subtree and is smaller than 5.",
        approaches=[
            dict(
                name="Pass down the allowed range",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Every node must lie in an open interval <code>(lo, hi)</code> fixed by its ancestors. Going left, the node's value becomes the new upper bound; going right, the new lower bound. This checks exactly the subtree-wide rule.",
                    "Use <code>None</code> or infinities for missing bounds, not a sentinel like <code>-2<sup>31</sup></code>: LeetCode's test data includes nodes with exactly those values.",
                ],
                code='''def is_valid_bst(root):
    def ok(node, lo, hi):
        if node is None:
            return True
        if not lo < node.val < hi:
            return False
        return ok(node.left, lo, node.val) and ok(node.right, node.val, hi)

    return ok(root, float("-inf"), float("inf"))''',
            ),
            dict(
                name="Inorder must be strictly increasing",
                time="O(n)",
                space="O(h)",
                why=[
                    "A tree is a BST exactly when its inorder sequence is strictly increasing. Walk it iteratively, compare each value with the previous one, and stop at the first violation.",
                    "Same bounds, and it exits early at the first out-of-order pair.",
                ],
                code='''def is_valid_bst(root):
    stack, node, prev = [], root, None
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        if prev is not None and node.val <= prev:
            return False
        prev, node = node.val, node.right
    return True''',
            ),
        ],
        tests='''assert is_valid_bst(build([2, 1, 3])) is True
assert is_valid_bst(build([5, 1, 4, None, None, 3, 6])) is False
assert is_valid_bst(build([5, 4, 6, None, None, 3, 7])) is False     # the subtree-wide trap
assert is_valid_bst(build([2, 2, 2])) is False
assert is_valid_bst(build([-2147483648, None, 2147483647])) is True
assert is_valid_bst(None) is True''',
    ),

    dict(
        id="verify-preorder-bst",
        lc=255, slug="verify-preorder-sequence-in-binary-search-tree",
        name="Verify Preorder Sequence in Binary Search Tree",
        difficulty="medium",
        tags=["Stack", "Monotonic Stack", "Binary Search Tree"],
        statement=[
            "Given an array of <strong>unique</strong> integers <code>preorder</code>, return <code>true</code> if it is the correct preorder traversal of some binary search tree.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch. The follow-up asks for O(1) extra space.",
        ],
        examples=[
            dict(input="preorder = [5,2,1,3,6]", output="true"),
            dict(input="preorder = [5,2,6,1,3]", output="false",
                 explanation="After 6 we are in 5's right subtree, so nothing smaller than 5 may follow; 1 does."),
        ],
        constraints=[
            "<code>1 &lt;= preorder.length &lt;= 10<sup>4</sup></code>",
            "All values are unique",
        ],
        approaches=[
            dict(
                name="Monotonic stack with a lower bound",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Simulate the traversal. The stack holds the path of nodes whose right subtree has not started yet, in decreasing order. A value larger than the stack top means we have moved into some ancestor's right subtree: pop every smaller node, and the last one popped becomes a <em>lower bound</em> &mdash; nothing that follows may be smaller than it.",
                    "A value below the current lower bound is the violation. Each value is pushed and popped once: O(n).",
                ],
                code='''def verify_preorder(preorder):
    low, stack = float("-inf"), []
    for v in preorder:
        if v < low:
            return False
        while stack and stack[-1] < v:
            low = stack.pop()                # entered this node's right subtree
        stack.append(v)
    return True''',
            ),
            dict(
                name="Same idea, reusing the input as the stack",
                time="O(n)",
                space="O(1)",
                tag="follow-up",
                why=[
                    "The stack never holds more items than have been read, so the already-processed prefix of the array can serve as the stack: an index <code>top</code> marks its end. This mutates the input, which is how the O(1) follow-up is usually answered &mdash; say so explicitly.",
                ],
                code='''def verify_preorder(preorder):
    low, top = float("-inf"), -1
    for v in preorder:
        if v < low:
            return False
        while top >= 0 and preorder[top] < v:
            low = preorder[top]
            top -= 1
        top += 1
        preorder[top] = v                    # the prefix doubles as the stack
    return True''',
            ),
        ],
        tests='''assert verify_preorder([5, 2, 1, 3, 6]) is True
assert verify_preorder([5, 2, 6, 1, 3]) is False
assert verify_preorder([1]) is True
assert verify_preorder([1, 3, 2]) is True
assert verify_preorder([2, 3, 1]) is False
import itertools


def _is_preorder(seq):
    """Brute force: insert in order; valid iff the tree's preorder is seq."""
    root = None
    for v in seq:
        root = _bst_add(root, v)
    return vals_pre(root) == list(seq)

for n in range(1, 7):
    for perm in itertools.permutations(range(n)):
        assert verify_preorder(list(perm)) is _is_preorder(perm), perm''',
    ),
    ],
),

# ---------------------------------------------------------------- inorder
dict(
    id="bst-inorder",
    title="BST problems that are really sorted-array problems",
    idea=[
        "Inorder traversal turns a BST into a sorted sequence without building an array. Any question about a sorted array &mdash; neighbours, runs of equal values, k-th element &mdash; becomes an inorder walk that remembers the previous value.",
    ],
    problems=[

    dict(
        id="kth-largest-bst",
        name="Kth Largest Element in a BST",
        difficulty="medium",
        tags=["Binary Search Tree", "Depth-First Search", "Concept"],
        statement=[
            "Return the k-th largest value in a BST (<code>k = 1</code> is the maximum).",
            "LeetCode has no problem by this name &mdash; the link in many study lists points nowhere &mdash; but it is a common interview question, and the mirror image of Kth Smallest Element in a BST.",
        ],
        examples=[
            dict(input="root = [5,3,6,2,4,null,null,1], k = 3", output="4",
                 explanation="Descending order is 6, 5, 4, 3, 2, 1."),
        ],
        constraints=["<code>1 &lt;= k &lt;= n &lt;= 10<sup>4</sup></code>"],
        approaches=[
            dict(
                name="Reverse inorder, stop at k",
                time="O(h + k)",
                space="O(h)",
                best=True,
                why=[
                    "Inorder with the children swapped &mdash; right, node, left &mdash; visits values in <em>decreasing</em> order. Stop at the k-th one.",
                    "The rightmost spine is O(h) and each further step yields the next value, so O(h + k) time. Converting to kth-smallest with <code>n - k + 1</code> also works but needs n first, which costs a full O(n) pass.",
                ],
                code='''def kth_largest(root, k):
    stack, node = [], root
    while True:
        while node is not None:
            stack.append(node)
            node = node.right                # mirror of inorder
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.left''',
            ),
        ],
        tests='''t = build([5, 3, 6, 2, 4, None, None, 1])
assert [kth_largest(t, k) for k in range(1, 7)] == [6, 5, 4, 3, 2, 1]
for seed in range(15):
    t = random_bst(1 + seed * 3, seed)
    desc = sorted(vals_in(t), reverse=True)
    assert all(kth_largest(t, k) == desc[k - 1] for k in range(1, len(desc) + 1))''',
    ),

    dict(
        id="min-abs-diff-bst",
        lc=530, slug="minimum-absolute-difference-in-bst",
        name="Minimum Absolute Difference in BST",
        difficulty="easy",
        framing=[
            "The smallest difference between any two values. In a sorted list the closest pair is always adjacent, so only consecutive inorder values need comparing &mdash; n-1 comparisons instead of n&sup2;/2.",
        ],
        approaches=[
            dict(
                name="Inorder, compare with the previous value",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Carry the previous inorder value; each new value is compared only with it.",
                ],
                code='''def get_minimum_difference(root):
    best, prev = float("inf"), None

    def walk(node):
        nonlocal best, prev
        if node is None:
            return
        walk(node.left)
        if prev is not None:
            best = min(best, node.val - prev)
        prev = node.val
        walk(node.right)

    walk(root)
    return best''',
            ),
        ],
        tests='''assert get_minimum_difference(build([4, 2, 6, 1, 3])) == 1
assert get_minimum_difference(build([1, 0, 48, None, None, 12, 49])) == 1
assert get_minimum_difference(build([236, 104, 701, None, 227, None, 911])) == 9''',
    ),

    dict(
        id="find-mode-bst",
        lc=501, slug="find-mode-in-binary-search-tree",
        name="Find Mode in Binary Search Tree",
        difficulty="easy",
        framing=[
            "This BST allows duplicates (left &le; node &le; right). Return every most-frequent value. With a counter it is trivial; the follow-up asks for no extra space beyond the recursion, and inorder is what makes that possible: equal values come out <em>consecutively</em>, so a run length replaces the counter.",
        ],
        approaches=[
            dict(
                name="Inorder run lengths",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Track the current value's run length. When a run exceeds the best so far, the answer resets to that value; when it ties, the value is added. Equal values are adjacent in inorder, so each run is seen in one piece.",
                    "No dictionary: the only memory is the recursion stack and the output.",
                ],
                code='''def find_mode(root):
    modes, best, run, prev = [], 0, 0, None

    def walk(node):
        nonlocal best, run, prev, modes
        if node is None:
            return
        walk(node.left)
        run = run + 1 if node.val == prev else 1
        prev = node.val
        if run > best:
            best, modes = run, [node.val]
        elif run == best:
            modes.append(node.val)
        walk(node.right)

    walk(root)
    return modes''',
            ),
            dict(
                name="Counter",
                time="O(n)",
                space="O(n)",
                why=[
                    "Count every value and return the ones with the top count. Works on any tree, ignores the BST property, and uses O(n) extra space.",
                ],
                code='''def find_mode(root):
    counts = Counter(vals_in(root))
    top = max(counts.values())
    return sorted(v for v, c in counts.items() if c == top)''',
            ),
        ],
        tests='''assert find_mode(build([1, None, 2, 2])) == [2]
assert find_mode(build([0])) == [0]
assert find_mode(build([2, 1, 3])) == [1, 2, 3]
assert find_mode(build([5, 3, 7, 3, 5, 7, 7])) == [7]''',
    ),

    dict(
        id="increasing-order-search-tree",
        lc=897, slug="increasing-order-search-tree",
        name="Increasing Order Search Tree",
        difficulty="easy",
        framing=[
            "Rearrange the BST so the smallest node is the root and every node has only a right child, in increasing order. Inorder gives the order; the work is re-linking nodes as they are visited.",
        ],
        approaches=[
            dict(
                name="Inorder, re-link onto a tail",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Keep a <code>tail</code> starting at a dummy node. As each node is visited in order, clear its left pointer, hang it off <code>tail.right</code>, and advance the tail. The dummy's right child is the new root.",
                    "Re-linking the node that is being visited is safe because its left subtree has already been processed; its right pointer is overwritten only after the traversal has moved past it.",
                ],
                code='''def increasing_bst(root):
    dummy = tail = TreeNode(0)

    def walk(node):
        nonlocal tail
        if node is None:
            return
        walk(node.left)
        node.left = None
        tail.right = node
        tail = node
        walk(node.right)

    walk(root)
    return dummy.right''',
            ),
        ],
        tests='''t = increasing_bst(build([5, 3, 6, 2, 4, None, 8, 1, None, None, None, 7, 9]))
assert level_order(t) == [1, None, 2, None, 3, None, 4, None, 5, None, 6, None, 7, None, 8, None, 9]
assert level_order(increasing_bst(build([5, 1, 7]))) == [1, None, 5, None, 7]''',
    ),
    ],
),

# ---------------------------------------------------------------- range queries
dict(
    id="bst-range",
    title="Range queries: prune with the ordering",
    idea=[
        "When a node is below the range, its whole left subtree is too, so skip it. When it is above, skip its right subtree. The cost falls from O(n) to O(h + number of values in the range).",
    ],
    problems=[

    dict(
        id="range-sum-bst",
        lc=938, slug="range-sum-of-bst",
        name="Range Sum of BST",
        difficulty="easy",
        framing=[
            "Sum the values in <code>[low, high]</code>. Visiting every node works; the BST lets you skip entire subtrees that lie outside the range.",
        ],
        approaches=[
            dict(
                name="DFS that prunes out-of-range subtrees",
                time="O(h + m)",
                space="O(h)",
                best=True,
                why=[
                    "Below <code>low</code>: only the right subtree can hold values in range. Above <code>high</code>: only the left. Otherwise count the node and search both sides.",
                    "The visited nodes are the m in-range nodes plus the two boundary paths, so O(h + m) rather than O(n).",
                ],
                code='''def range_sum_bst(root, low, high):
    total, stack = 0, [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if node.val < low:
            stack.append(node.right)          # everything on the left is smaller
        elif node.val > high:
            stack.append(node.left)
        else:
            total += node.val
            stack += [node.left, node.right]
    return total''',
            ),
        ],
        tests='''assert range_sum_bst(build([10, 5, 15, 3, 7, None, 18]), 7, 15) == 32
assert range_sum_bst(build([10, 5, 15, 3, 7, 13, 18, 1, None, 6]), 6, 10) == 23
for seed in range(20):
    t = random_bst(1 + seed * 3, seed, 0, 300)
    lo, hi = sorted(random.Random(seed).sample(range(300), 2))
    assert range_sum_bst(t, lo, hi) == sum(v for v in vals_in(t) if lo <= v <= hi)''',
    ),

    dict(
        id="trim-bst",
        lc=669, slug="trim-a-binary-search-tree",
        name="Trim a Binary Search Tree",
        difficulty="medium",
        framing=[
            "Remove every node outside <code>[low, high]</code>, keeping the relative structure of what remains. Pruning with the ordering again &mdash; but now the pruned subtrees have to be <em>re-linked</em>, which is where returning the new subtree root pays off.",
        ],
        approaches=[
            dict(
                name="Recursive, return the trimmed subtree",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "A node below <code>low</code> is discarded along with its entire left subtree, and the answer is whatever trimming its right subtree produces. Symmetrically above <code>high</code>. A node in range keeps itself and trims both children.",
                    "Discarded subtrees are skipped without being visited, but the worst case (everything in range) still visits every node: O(n).",
                ],
                code='''def trim_bst(root, low, high):
    if root is None:
        return None
    if root.val < low:
        return trim_bst(root.right, low, high)     # drop root and its left side
    if root.val > high:
        return trim_bst(root.left, low, high)
    root.left = trim_bst(root.left, low, high)
    root.right = trim_bst(root.right, low, high)
    return root''',
            ),
        ],
        tests='''assert level_order(trim_bst(build([1, 0, 2]), 1, 2)) == [1, None, 2]
assert level_order(trim_bst(build([3, 0, 4, None, 2, None, None, 1]), 1, 3)) == [3, 2, None, 1]
assert trim_bst(build([1]), 2, 4) is None
for seed in range(20):
    t = random_bst(1 + seed * 3, seed, 0, 300)
    lo, hi = sorted(random.Random(seed).sample(range(300), 2))
    expect = [v for v in vals_in(t) if lo <= v <= hi]
    got = trim_bst(t, lo, hi)
    assert vals_in(got) == expect and is_valid_bst(got)''',
    ),
    ],
),

# ---------------------------------------------------------------- successor
dict(
    id="bst-successor",
    title="Ancestors and successors in O(h)",
    idea=[
        "In a BST the answer to an ordering question lies on one root-to-leaf path, so you should never need to traverse the whole tree. Lowest Common Ancestor of a BST, earlier in this path, is the first example; the inorder successor is the second.",
    ],
    problems=[

    dict(
        id="inorder-successor-bst",
        lc=285, slug="inorder-successor-in-bst",
        name="Inorder Successor in BST",
        difficulty="medium",
        tags=["Tree", "Binary Search Tree", "Depth-First Search"],
        statement=[
            "Given the root of a binary search tree and a node <code>p</code> in it, return the <strong>in-order successor</strong> of <code>p</code>: the node with the smallest value greater than <code>p.val</code>. Return <code>null</code> if there is none.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="root = [2,1,3], p = 1", output="2"),
            dict(input="root = [5,3,6,2,4,null,null,1], p = 6", output="null",
                 explanation="6 is the largest value, so it has no successor."),
        ],
        constraints=[
            "<code>1 &lt;= n &lt;= 10<sup>4</sup></code>",
            "All values are unique",
        ],
        approaches=[
            dict(
                name="Descend from the root, remember the last left turn",
                time="O(h)",
                space="O(1)",
                best=True,
                why=[
                    "The successor is the ceiling of <code>p.val + &epsilon;</code>. Walk down from the root: at a node larger than <code>p.val</code>, it is a candidate and anything better is to its left; otherwise the successor must be to the right. The last candidate is the answer.",
                    "This handles both textbook cases in one loop: if <code>p</code> has a right subtree the walk ends at that subtree's minimum; if not, the answer is the ancestor where the path last turned left.",
                    "One path: O(h) time, O(1) space.",
                ],
                code='''def inorder_successor(root, p):
    succ, node = None, root
    while node is not None:
        if node.val > p.val:
            succ = node                  # a candidate; look for a smaller one
            node = node.left
        else:
            node = node.right
    return succ''',
            ),
            dict(
                name="Inorder traversal, return the node after p",
                time="O(n)",
                space="O(h)",
                why=[
                    "Walk inorder and return the node that follows <code>p</code>. Works on any binary tree, which is its only advantage &mdash; it ignores the ordering and costs O(n).",
                ],
                code='''def inorder_successor(root, p):
    stack, node, seen_p = [], root, False
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        if seen_p:
            return node
        seen_p = node is p
        node = node.right
    return None''',
            ),
        ],
        tests='''t = build([2, 1, 3])
assert inorder_successor(t, find_node(t, 1)) is t
t = build([5, 3, 6, 2, 4, None, None, 1])
assert inorder_successor(t, find_node(t, 6)) is None
assert inorder_successor(t, find_node(t, 4)).val == 5
assert inorder_successor(t, find_node(t, 1)).val == 2
for seed in range(15):
    t = random_bst(1 + seed * 3, seed)
    order = vals_in(t)
    for i, v in enumerate(order):
        s = inorder_successor(t, find_node(t, v))
        assert (s.val if s else None) == (order[i + 1] if i + 1 < len(order) else None)''',
    ),
    ],
),
]
