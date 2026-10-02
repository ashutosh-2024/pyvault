# -*- coding: utf-8 -*-
"""Binary Trees: self-balancing BSTs implemented from scratch, other ordered
trees, N-ary trees, next pointers."""

SECTIONS = [

# ---------------------------------------------------------------- AVL
dict(
    id="avl",
    title="Balanced BSTs I: AVL trees",
    idea=[
        "Every BST operation is O(h), and inserting sorted data makes h = n. A self-balancing tree restores balance after each insert or delete with O(1) rotations per level, so h stays O(log n) whatever order the data arrives in.",
    ],
    problems=[

    dict(
        id="implement-avl-tree",
        name="Implement an AVL Tree",
        difficulty="hard",
        tags=["Binary Search Tree", "Balanced BST", "Design", "Concept"],
        statement=[
            "Implement a set of integers backed by an <strong>AVL tree</strong>, supporting <code>insert(key)</code>, <code>delete(key)</code>, <code>key in tree</code> and <code>inorder()</code>, each insert, delete and lookup in O(log n) worst case.",
            "An AVL tree is a BST in which, at every node, the heights of the two subtrees differ by at most 1. The difference <code>height(left) - height(right)</code> is the node's <strong>balance factor</strong>; each node stores its height so the factor is O(1) to compute.",
            "After an insert or delete, walk back up the path and fix any node whose balance factor has become &plusmn;2. There are four cases, named after where the extra height is: <strong>LL</strong> (left child's left subtree: one right rotation), <strong>RR</strong> (mirror: one left rotation), <strong>LR</strong> (left child's right subtree: rotate the child left, then the node right) and <strong>RL</strong> (the mirror).",
            "LeetCode has no problem that makes you write rotations &mdash; Balance a Binary Search Tree rebuilds instead &mdash; so implementing one yourself is the way to learn it.",
        ],
        examples=[
            dict(input="insert 1, 2, 3, 4, 5, 6, 7 in that order",
                 output="a perfect tree rooted at 4, height 3",
                 explanation="A plain BST would be a chain of height 7. Each RR imbalance is fixed by a left rotation as it appears."),
        ],
        constraints=[
            "Keys are distinct integers; inserting an existing key does nothing",
            "Height must stay below 1.44 &middot; log<sub>2</sub>(n + 2)",
        ],
        approaches=[
            dict(
                name="Recursive insert and delete with rebalance on the way up",
                time="O(log n) per operation",
                space="O(log n) recursion",
                best=True,
                why=[
                    "A rotation re-hangs three subtrees around two nodes, preserving the inorder order, and changes the height of the rotated part by one. <code>rebalance</code> recomputes the node's height, and if the factor is +2 (left heavy) checks the left child: leaning the other way means LR, so first rotate the child. Then rotate the node. The right-heavy side is symmetric.",
                    "Insert and delete are ordinary BST operations written in the return-the-subtree style, with <code>return rebalance(node)</code> instead of <code>return node</code>. That one change fixes every node on the path, bottom-up.",
                    "Why O(log n): the sparsest AVL tree of height h has N(h) = N(h-1) + N(h-2) + 1 nodes, a Fibonacci recurrence, so n &ge; &phi;<sup>h</sup> roughly, which gives h &le; 1.44 log<sub>2</sub> n. An insertion needs at most one (single or double) rotation; a deletion may need one per level, O(log n).",
                    "AVL vs. red-black: AVL trees are more rigidly balanced, so lookups are slightly faster; red-black trees do fewer rotations on updates. Databases and read-heavy indexes lean AVL; most standard-library maps (C++ <code>std::map</code>, Java <code>TreeMap</code>) are red-black.",
                ],
                code='''class AVLNode:
    __slots__ = ("key", "left", "right", "height")

    def __init__(self, key):
        self.key, self.left, self.right, self.height = key, None, None, 1


def height(n):
    return n.height if n else 0


def update(n):
    n.height = 1 + max(height(n.left), height(n.right))


def balance_factor(n):
    return height(n.left) - height(n.right)


def rotate_right(y):
    x = y.left
    y.left, x.right = x.right, y
    update(y); update(x)                  # y is now below x: update it first
    return x


def rotate_left(x):
    y = x.right
    x.right, y.left = y.left, x
    update(x); update(y)
    return y


def rebalance(n):
    update(n)
    bf = balance_factor(n)
    if bf > 1:                            # left heavy
        if balance_factor(n.left) < 0:    # LR: straighten it into LL first
            n.left = rotate_left(n.left)
        return rotate_right(n)            # LL
    if bf < -1:                           # right heavy
        if balance_factor(n.right) > 0:   # RL
            n.right = rotate_right(n.right)
        return rotate_left(n)             # RR
    return n


class AVLTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, n, key):
        if n is None:
            return AVLNode(key)
        if key < n.key:
            n.left = self._insert(n.left, key)
        elif key > n.key:
            n.right = self._insert(n.right, key)
        else:
            return n                      # already present
        return rebalance(n)

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, n, key):
        if n is None:
            return None
        if key < n.key:
            n.left = self._delete(n.left, key)
        elif key > n.key:
            n.right = self._delete(n.right, key)
        else:
            if n.left is None:
                return n.right
            if n.right is None:
                return n.left
            succ = n.right                # two children: take the successor
            while succ.left is not None:
                succ = succ.left
            n.key = succ.key
            n.right = self._delete(n.right, succ.key)
        return rebalance(n)

    def __contains__(self, key):
        n = self.root
        while n is not None and n.key != key:
            n = n.left if key < n.key else n.right
        return n is not None

    def inorder(self):
        out, stack, n = [], [], self.root
        while stack or n:
            while n:
                stack.append(n)
                n = n.left
            n = stack.pop()
            out.append(n.key)
            n = n.right
        return out''',
            ),
        ],
        tests='''import math


def _check(n):
    """Return the true height; assert stored heights, balance and order."""
    if n is None:
        return 0
    hl, hr = _check(n.left), _check(n.right)
    assert n.height == 1 + max(hl, hr), "stale height"
    assert abs(hl - hr) <= 1, "unbalanced"
    assert n.left is None or n.left.key < n.key
    assert n.right is None or n.right.key > n.key
    return n.height

t = AVLTree()
for k in range(1, 8):
    t.insert(k)
assert t.root.key == 4 and t.root.height == 3

t = AVLTree()
for k in range(1, 1001):                  # sorted input: the worst case for a plain BST
    t.insert(k)
assert _check(t.root) <= 1.44 * math.log2(1000 + 2)

rng, t, model = random.Random(7), AVLTree(), set()
for step in range(3000):
    k = rng.randrange(400)
    if rng.random() < 0.6:
        t.insert(k); model.add(k)
    else:
        t.delete(k); model.discard(k)
    if step % 50 == 0:
        h = _check(t.root)
        assert h <= 1.45 * math.log2(len(model) + 2)
assert t.inorder() == sorted(model)
assert all((k in t) == (k in model) for k in range(400))''',
    ),
    ],
),

# ---------------------------------------------------------------- red-black
dict(
    id="red-black",
    title="Balanced BSTs II: red-black trees",
    idea=[
        "A red-black tree tolerates more imbalance than AVL (height up to 2 log n) in exchange for cheaper updates. Its rules are easiest to understand through 2-3 trees, and the left-leaning variant makes that correspondence exact.",
    ],
    problems=[

    dict(
        id="implement-red-black-tree",
        name="Implement a Left-Leaning Red-Black Tree",
        difficulty="hard",
        tags=["Binary Search Tree", "Balanced BST", "Design", "Concept"],
        statement=[
            "Implement an integer set backed by a <strong>red-black tree</strong> with <code>insert</code>, <code>delete</code>, membership and <code>inorder</code>, all O(log n) worst case.",
            "The classic red-black rules: every node is red or black; the root is black; a red node has no red child; and every path from a node down to a missing child passes through the same number of black nodes (the <strong>black-height</strong>). Together they force height &le; 2 log<sub>2</sub>(n + 1): the shortest root-to-leaf path is all black, the longest alternates red and black, so no path is more than twice another.",
            "Why colours at all? A red link glues a node to its parent to form a 3-node of a <strong>2-3 tree</strong>, a tree whose nodes hold one or two keys and whose leaves are all at the same depth. Perfect balance in the 2-3 tree is the black-height rule; \"no two reds in a row\" says no node holds three keys.",
            "Sedgewick's <strong>left-leaning</strong> red-black tree (LLRB) adds one rule &mdash; red links lean left &mdash; which makes the correspondence with 2-3 trees one-to-one and cuts the insertion cases to three lines. Implement that variant. There is no LeetCode problem for red-black trees; writing one is the exercise.",
        ],
        examples=[
            dict(input="insert 1..1000 in order", output="height &le; 2 log<sub>2</sub>(1001) &asymp; 19.9"),
        ],
        constraints=[
            "Keys are distinct integers",
            "After every operation: root black, no red right links, no two reds in a row, equal black-height on every path",
        ],
        approaches=[
            dict(
                name="LLRB: rotate and flip on the way up",
                time="O(log n) per operation",
                space="O(log n) recursion",
                best=True,
                why=[
                    "Insert as in a plain BST, colouring the new node red (it joins an existing 2-3 node). On the way back up, three local fixes restore the rules: a right-leaning red link is rotated left; two reds in a row on the left are rotated right; a node with two red children has its colours <strong>flipped</strong> &mdash; which in 2-3 terms splits a temporary 4-node and passes the middle key up to the parent.",
                    "Deletion keeps the invariant that the current node is not a 2-node (a node with only one key) on the way down, borrowing from a sibling with <code>move_red_left</code>/<code>move_red_right</code>, so the key can be removed from the bottom without breaking the black-height. The same <code>fix_up</code> repairs the path on the way back.",
                    "Each level does O(1) work, and the height is at most 2 log<sub>2</sub> n. Classic (non-left-leaning) red-black trees are what libraries use: they need at most 2 rotations per insert and 3 per delete, against O(log n) for AVL deletion, which is why they win for write-heavy workloads.",
                ],
                code='''RED, BLACK = True, False


class RBNode:
    __slots__ = ("key", "left", "right", "color")

    def __init__(self, key):
        self.key, self.left, self.right, self.color = key, None, None, RED


def is_red(n):
    return n is not None and n.color is RED


def rotate_left(h):
    x = h.right
    h.right, x.left = x.left, h
    x.color, h.color = h.color, RED
    return x


def rotate_right(h):
    x = h.left
    h.left, x.right = x.right, h
    x.color, h.color = h.color, RED
    return x


def flip_colors(h):
    h.color = not h.color
    h.left.color = not h.left.color
    h.right.color = not h.right.color


def fix_up(h):
    if is_red(h.right) and not is_red(h.left):
        h = rotate_left(h)                        # red links lean left
    if is_red(h.left) and is_red(h.left.left):
        h = rotate_right(h)                       # no two reds in a row
    if is_red(h.left) and is_red(h.right):
        flip_colors(h)                            # split a 4-node
    return h


def move_red_left(h):
    flip_colors(h)
    if is_red(h.right.left):
        h.right = rotate_right(h.right)
        h = rotate_left(h)
        flip_colors(h)
    return h


def move_red_right(h):
    flip_colors(h)
    if is_red(h.left.left):
        h = rotate_right(h)
        flip_colors(h)
    return h


class RedBlackTree:
    def __init__(self):
        self.root = None

    def __contains__(self, key):
        n = self.root
        while n is not None and n.key != key:
            n = n.left if key < n.key else n.right
        return n is not None

    def insert(self, key):
        self.root = self._insert(self.root, key)
        self.root.color = BLACK

    def _insert(self, h, key):
        if h is None:
            return RBNode(key)
        if key < h.key:
            h.left = self._insert(h.left, key)
        elif key > h.key:
            h.right = self._insert(h.right, key)
        return fix_up(h)

    def delete(self, key):
        if key not in self:
            return
        if not is_red(self.root.left) and not is_red(self.root.right):
            self.root.color = RED
        self.root = self._delete(self.root, key)
        if self.root is not None:
            self.root.color = BLACK

    def _delete_min(self, h):
        if h.left is None:
            return None
        if not is_red(h.left) and not is_red(h.left.left):
            h = move_red_left(h)
        h.left = self._delete_min(h.left)
        return fix_up(h)

    def _delete(self, h, key):
        if key < h.key:
            if not is_red(h.left) and not is_red(h.left.left):
                h = move_red_left(h)
            h.left = self._delete(h.left, key)
        else:
            if is_red(h.left):
                h = rotate_right(h)
            if key == h.key and h.right is None:
                return None
            if not is_red(h.right) and not is_red(h.right.left):
                h = move_red_right(h)
            if key == h.key:
                m = h.right
                while m.left is not None:
                    m = m.left
                h.key = m.key
                h.right = self._delete_min(h.right)
            else:
                h.right = self._delete(h.right, key)
        return fix_up(h)

    def inorder(self):
        out = []
        def walk(n):
            if n:
                walk(n.left); out.append(n.key); walk(n.right)
        walk(self.root)
        return out''',
            ),
        ],
        tests='''import math


def _check(n):
    """Return the black-height; assert every red-black and BST rule."""
    if n is None:
        return 1
    assert not is_red(n.right), "red link leans right"
    assert not (is_red(n) and is_red(n.left)), "two reds in a row"
    assert n.left is None or n.left.key < n.key
    assert n.right is None or n.right.key > n.key
    bl, br = _check(n.left), _check(n.right)
    assert bl == br, "black-height differs"
    return bl + (not is_red(n))


def _height(n):
    return 0 if n is None else 1 + max(_height(n.left), _height(n.right))

t = RedBlackTree()
for k in range(1, 1001):
    t.insert(k)
_check(t.root)
assert not is_red(t.root)
assert _height(t.root) <= 2 * math.log2(1001)

rng, t, model = random.Random(11), RedBlackTree(), set()
for step in range(3000):
    k = rng.randrange(400)
    if rng.random() < 0.6:
        t.insert(k); model.add(k)
    else:
        t.delete(k); model.discard(k)
    if step % 50 == 0 and t.root is not None:
        assert not is_red(t.root)
        _check(t.root)
        assert _height(t.root) <= 2 * math.log2(len(model) + 1)
assert t.inorder() == sorted(model)
assert all((k in t) == (k in model) for k in range(400))''',
    ),
    ],
),

# ---------------------------------------------------------------- other ordered trees
dict(
    id="other-ordered-trees",
    title="Other ordered trees: treaps, splay trees, B-trees",
    idea=[
        "Beyond AVL and red-black trees, a handful of other ordered trees are worth knowing by purpose: treaps for simplicity, splay trees for skewed access, and B-trees and B+ trees for disks and databases.",
    ],
    problems=[

    dict(
        id="implement-treap",
        name="Implement a Treap (and Know Splay Trees and B-Trees)",
        difficulty="medium",
        tags=["Binary Search Tree", "Balanced BST", "Randomized", "Concept"],
        statement=[
            "Implement an integer set as a <strong>treap</strong>: a BST on the keys that is simultaneously a <strong>heap</strong> on random priorities assigned at insertion. Support <code>insert</code>, <code>delete</code>, membership and <code>inorder</code> in expected O(log n).",
            "Why it balances: the tree a treap produces is exactly the BST you would get by inserting the keys in increasing order of priority &mdash; that is, in random order. A randomly built BST has expected height O(log n), whatever order the keys actually arrived in. Rotations are the only tool needed, and far fewer cases arise than in AVL or red-black trees.",
            "<strong>Splay trees</strong> keep no balance information at all. Every access rotates the accessed node to the root (\"splaying\"). A single operation can cost O(n), but any sequence of m operations costs O(m log n): an <em>amortised</em> guarantee. Recently used keys end up near the top, so skewed workloads (caches, the same few keys again and again) get faster than any statically balanced tree.",
            "<strong>B-trees</strong> are multi-way search trees: each node holds up to 2t - 1 sorted keys and has one more child than keys, and every leaf is at the same depth. A full node is <em>split</em> in two, pushing its middle key up; the tree grows at the root, never at the leaves. With hundreds of keys per node, a billion keys need only four or five levels &mdash; and each level is one disk read, which is why databases and file systems use them instead of binary trees.",
            "<strong>B+ trees</strong> keep all records in the leaves, use internal nodes purely as an index, and link the leaves in a list. A range query finds its start in O(log n) and then walks the leaf chain sequentially. This is the structure behind MySQL InnoDB and PostgreSQL indexes.",
        ],
        examples=[
            dict(input="insert 1..1000 in order", output="expected height about 2&ndash;3 &times; log<sub>2</sub> n, not 1000"),
        ],
        constraints=["Keys are distinct integers"],
        approaches=[
            dict(
                name="Recursive treap with rotations",
                time="O(log n) expected",
                space="O(log n) expected recursion",
                best=True,
                why=[
                    "Insert: add the key as a leaf, as in a plain BST, with a random priority. On the way back up, if a child's priority is smaller than its parent's (a min-heap on priorities), rotate the child above the parent. The heap property is then restored all the way up.",
                    "Delete: find the key and rotate it <em>down</em>, each time lifting whichever child has the smaller priority, until it is a leaf; then cut it off.",
                    "Every bound is in expectation over the random priorities, not worst case: an adversary who cannot see the priorities cannot force a bad shape. Seeding the generator makes the tests reproducible.",
                ],
                code='''class TreapNode:
    __slots__ = ("key", "prio", "left", "right")

    def __init__(self, key, prio):
        self.key, self.prio, self.left, self.right = key, prio, None, None


def rotate_right(y):
    x = y.left
    y.left, x.right = x.right, y
    return x


def rotate_left(x):
    y = x.right
    x.right, y.left = y.left, x
    return y


class Treap:
    def __init__(self, seed=0):
        self.root = None
        self.rng = random.Random(seed)

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, n, key):
        if n is None:
            return TreapNode(key, self.rng.random())
        if key < n.key:
            n.left = self._insert(n.left, key)
            if n.left.prio < n.prio:
                n = rotate_right(n)          # lift the child: heap order
        elif key > n.key:
            n.right = self._insert(n.right, key)
            if n.right.prio < n.prio:
                n = rotate_left(n)
        return n

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, n, key):
        if n is None:
            return None
        if key < n.key:
            n.left = self._delete(n.left, key)
        elif key > n.key:
            n.right = self._delete(n.right, key)
        else:
            if n.left is None:
                return n.right
            if n.right is None:
                return n.left
            if n.left.prio < n.right.prio:   # rotate the node down, then retry
                n = rotate_right(n)
                n.right = self._delete(n.right, key)
            else:
                n = rotate_left(n)
                n.left = self._delete(n.left, key)
        return n

    def __contains__(self, key):
        n = self.root
        while n is not None and n.key != key:
            n = n.left if key < n.key else n.right
        return n is not None

    def inorder(self):
        out = []
        def walk(n):
            if n:
                walk(n.left); out.append(n.key); walk(n.right)
        walk(self.root)
        return out''',
            ),
        ],
        tests='''import math


def _check(n):
    if n is None:
        return 0
    for c in (n.left, n.right):
        assert c is None or c.prio >= n.prio, "heap order broken"
    assert n.left is None or n.left.key < n.key
    assert n.right is None or n.right.key > n.key
    return 1 + max(_check(n.left), _check(n.right))

t = Treap(seed=1)
for k in range(1, 1001):
    t.insert(k)
assert _check(t.root) <= 4 * math.log2(1001)

rng, t, model = random.Random(3), Treap(seed=5), set()
for step in range(3000):
    k = rng.randrange(400)
    if rng.random() < 0.6:
        t.insert(k); model.add(k)
    else:
        t.delete(k); model.discard(k)
    if step % 100 == 0:
        _check(t.root)
assert t.inorder() == sorted(model)
assert all((k in t) == (k in model) for k in range(400))''',
    ),
    ],
),

# ---------------------------------------------------------------- N-ary
dict(
    id="n-ary",
    title="N-ary trees",
    idea=[
        "Replace <code>left</code> and <code>right</code> with a <code>children</code> list and every binary-tree traversal carries over; the only question is how to iterate the children, and in which order to push them onto a stack.",
    ],
    problems=[

    dict(
        id="max-depth-n-ary",
        lc=559, slug="maximum-depth-of-n-ary-tree",
        name="Maximum Depth of N-ary Tree",
        difficulty="easy",
        framing=[
            "Maximum Depth of Binary Tree with <code>max</code> taken over a list of children instead of two. The input format is LeetCode's N-ary serialization: level order, with <code>null</code> closing each node's list of children.",
        ],
        approaches=[
            dict(
                name="Recursive over children",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "<code>1 + max(depth of each child)</code>, with <code>default=0</code> so a leaf needs no special case.",
                ],
                code='''def max_depth(root):
    if root is None:
        return 0
    return 1 + max((max_depth(c) for c in root.children), default=0)''',
            ),
            dict(
                name="BFS counting levels",
                time="O(n)",
                space="O(w)",
                why=[
                    "Replace each level with all of its nodes' children until nothing is left; count the rounds.",
                ],
                code='''def max_depth(root):
    depth, level = 0, [root] if root else []
    while level:
        depth += 1
        level = [c for node in level for c in node.children]
    return depth''',
            ),
        ],
        tests='''assert max_depth(build_nary([1, None, 3, 2, 4, None, 5, 6])) == 3
assert max_depth(build_nary([1, None, 2, 3, 4, 5, None, None, 6, 7, None, 8, None, 9, 10, None, None, 11, None, 12, None, 13, None, None, 14])) == 5
assert max_depth(None) == 0''',
    ),

    dict(
        id="n-ary-preorder",
        lc=589, slug="n-ary-tree-preorder-traversal",
        name="N-ary Tree Preorder Traversal",
        difficulty="easy",
        framing=[
            "Node first, then each child's subtree left to right. The follow-up asks for an iterative version, which has one trap: a stack pops in reverse, so children must be pushed in reverse.",
        ],
        approaches=[
            dict(
                name="Iterative, push children reversed",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Pop a node, record it, push its children from last to first, so the first child is popped next. The stack can hold all the pending siblings along the current path, which is O(n) in the worst case (a root with n - 1 children).",
                ],
                code='''def preorder(root):
    out, stack = [], [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        stack.extend(reversed(node.children))
    return out''',
            ),
            dict(
                name="Recursive",
                time="O(n)",
                space="O(h)",
                why=["The definition written out."],
                code='''def preorder(root):
    out = []

    def walk(node):
        if node is None:
            return
        out.append(node.val)
        for c in node.children:
            walk(c)

    walk(root)
    return out''',
            ),
        ],
        tests='''assert preorder(build_nary([1, None, 3, 2, 4, None, 5, 6])) == [1, 3, 5, 6, 2, 4]
assert preorder(build_nary([1, None, 2, 3, 4, 5, None, None, 6, 7, None, 8, None, 9, 10, None, None, 11, None, 12, None, 13, None, None, 14])) == [1, 2, 3, 6, 7, 11, 14, 4, 8, 12, 5, 9, 13, 10]
assert preorder(None) == []''',
    ),

    dict(
        id="n-ary-postorder",
        lc=590, slug="n-ary-tree-postorder-traversal",
        name="N-ary Tree Postorder Traversal",
        difficulty="easy",
        framing=[
            "Every child's subtree left to right, then the node. Iteratively, the neat trick is that postorder is the <em>reverse</em> of a preorder that visits children right to left.",
        ],
        approaches=[
            dict(
                name="Reversed root-right-to-left preorder",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Do a preorder that pushes children in their natural order (so the last child is popped first), producing node, children right-to-left. Reversing that list gives children left-to-right, then node: postorder.",
                    "The same trick works for binary postorder; it trades a true streaming traversal for simplicity, since the output has to be reversed at the end.",
                ],
                code='''def postorder(root):
    out, stack = [], [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        stack.extend(node.children)      # last child popped first
    return out[::-1]''',
            ),
            dict(
                name="Recursive",
                time="O(n)",
                space="O(h)",
                why=["Children first, then the node."],
                code='''def postorder(root):
    out = []

    def walk(node):
        if node is None:
            return
        for c in node.children:
            walk(c)
        out.append(node.val)

    walk(root)
    return out''',
            ),
        ],
        tests='''assert postorder(build_nary([1, None, 3, 2, 4, None, 5, 6])) == [5, 6, 3, 2, 4, 1]
assert postorder(build_nary([1, None, 2, 3, 4, 5, None, None, 6, 7, None, 8, None, 9, 10, None, None, 11, None, 12, None, 13, None, None, 14])) == [2, 6, 14, 11, 7, 3, 12, 8, 4, 13, 9, 10, 5, 1]
assert postorder(None) == []''',
    ),

    dict(
        id="n-ary-level-order",
        lc=429, slug="n-ary-tree-level-order-traversal",
        name="N-ary Tree Level Order Traversal",
        difficulty="medium",
        framing=[
            "Values level by level. The binary version's size snapshot carries over unchanged; building the next level as a list comprehension over every node's children is the Pythonic form.",
        ],
        approaches=[
            dict(
                name="Level lists",
                time="O(n)",
                space="O(w)",
                best=True,
                why=[
                    "Hold the current level as a list; the next level is every child of every node in it. Each node is placed in exactly one level: O(n).",
                ],
                code='''def level_order_nary(root):
    out, level = [], [root] if root else []
    while level:
        out.append([n.val for n in level])
        level = [c for n in level for c in n.children]
    return out''',
            ),
        ],
        tests='''assert level_order_nary(build_nary([1, None, 3, 2, 4, None, 5, 6])) == [[1], [3, 2, 4], [5, 6]]
assert level_order_nary(build_nary([1, None, 2, 3, 4, 5, None, None, 6, 7, None, 8, None, 9, 10, None, None, 11, None, 12, None, 13, None, None, 14])) == [[1], [2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13], [14]]
assert level_order_nary(None) == []''',
    ),
    ],
),

# ---------------------------------------------------------------- next pointers
dict(
    id="next-pointers",
    title="Next pointers: linking each level",
    idea=[
        "Once a level's nodes are linked left to right with <code>next</code>, that level can be walked like a linked list &mdash; and used to link the level below it without any queue. That is what turns level-order from O(w) space into O(1).",
    ],
    problems=[

    dict(
        id="next-right-pointers",
        lc=116, slug="populating-next-right-pointers-in-each-node",
        name="Populating Next Right Pointers in Each Node",
        difficulty="medium",
        framing=[
            "In a <strong>perfect</strong> binary tree, point each node's <code>next</code> at the node to its right on the same level (<code>None</code> at the end of a level). The follow-up asks for O(1) extra space, and the perfect shape makes it easy: every node has either zero or two children.",
        ],
        approaches=[
            dict(
                name="Use the level above as a linked list",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Walk each level through its already-built <code>next</code> pointers. For each node, link its left child to its right child, and its right child to the <em>next</em> node's left child. When a level is done, move to the leftmost node of the level below.",
                    "No queue: the links built on one level are the traversal structure for the next. O(n) time, O(1) space.",
                ],
                code='''def connect(root):
    leftmost = root
    while leftmost is not None and leftmost.left is not None:
        node = leftmost
        while node is not None:
            node.left.next = node.right
            if node.next is not None:
                node.right.next = node.next.left      # across the gap between parents
            node = node.next
        leftmost = leftmost.left
    return root''',
            ),
            dict(
                name="BFS, link within each level",
                time="O(n)",
                space="O(w)",
                why=[
                    "Level-order with the size snapshot, linking each popped node to the queue's front if it belongs to the same level. Works on any tree, but the queue holds a whole level: O(n) on a perfect tree.",
                ],
                code='''def connect(root):
    level = [root] if root else []
    while level:
        for a, b in zip(level, level[1:]):
            a.next = b
        level = [c for n in level for c in (n.left, n.right) if c is not None]
    return root''',
            ),
        ],
        tests='''def _check_next(root):
    level = [root] if root else []
    while level:
        for i, node in enumerate(level):
            assert node.next is (level[i + 1] if i + 1 < len(level) else None)
        level = [c for n in level for c in (n.left, n.right) if c is not None]

for n in (0, 1, 3, 7, 15, 31):
    t = connect(build(list(range(1, n + 1))))
    _check_next(t)''',
    ),

    dict(
        id="next-right-pointers-ii",
        lc=117, slug="populating-next-right-pointers-in-each-node-ii",
        name="Populating Next Right Pointers in Each Node II",
        difficulty="medium",
        framing=[
            "The same task on an <strong>arbitrary</strong> binary tree. Children may be missing anywhere, so \"the next node's left child\" might not exist and the next node on the level below can be several parents away. O(1) space is still possible with one more idea: a dummy head for the level being built.",
        ],
        approaches=[
            dict(
                name="Dummy head for the level below",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Walk the current level through <code>next</code>. Keep a <code>tail</code> pointer into the level below, starting at a dummy node. Every child you meet is appended with <code>tail.next = child</code>. When the level ends, <code>dummy.next</code> is the first node of the level below: move there and reset the dummy.",
                    "The dummy removes the \"is this the first node of the level?\" special case, exactly as in linked-list problems. O(n) time, O(1) space.",
                ],
                code='''def connect(root):
    head = root
    while head is not None:
        dummy = tail = TreeNode(0)
        node = head
        while node is not None:
            for child in (node.left, node.right):
                if child is not None:
                    tail.next = child
                    tail = child
            node = node.next
        head = dummy.next                 # first node of the level below
    return root''',
            ),
        ],
        tests='''def _check_next(root):
    level = [root] if root else []
    while level:
        for i, node in enumerate(level):
            assert node.next is (level[i + 1] if i + 1 < len(level) else None)
        level = [c for n in level for c in (n.left, n.right) if c is not None]

_check_next(connect(build([1, 2, 3, 4, 5, None, 7])))
assert connect(None) is None
for seed in range(30):
    _check_next(connect(random_tree(seed * 2, seed)))''',
    ),
    ],
),
]
