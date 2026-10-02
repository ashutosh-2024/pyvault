"""Helpers the Binary Trees solutions and tests run against, on top of
dsa.PRELUDE (TreeNode, build, level_order). Never shown on the site.

Helper names are deliberately unlike anything a solution would define, so a
solution cannot shadow a helper its own tests depend on."""

TREE_PRELUDE = '''import random
from collections import Counter, defaultdict

TreeNode.next = None          # the next-pointer problems attach .next per node


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


class Node:
    """LeetCode's N-ary tree node."""
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children if children is not None else []


def build_nary(values):
    """LeetCode's N-ary format: level order, None closes each child group."""
    if not values:
        return None
    root = Node(values[0])
    queue, i = deque([root]), 2
    while queue and i < len(values):
        parent = queue.popleft()
        while i < len(values) and values[i] is not None:
            child = Node(values[i])
            parent.children.append(child)
            queue.append(child)
            i += 1
        i += 1
    return root


def vals_pre(root):
    return [] if root is None else [root.val] + vals_pre(root.left) + vals_pre(root.right)


def vals_in(root):
    return [] if root is None else vals_in(root.left) + [root.val] + vals_in(root.right)


def vals_post(root):
    return [] if root is None else vals_post(root.left) + vals_post(root.right) + [root.val]


def find_node(root, val):
    if root is None or root.val == val:
        return root
    return find_node(root.left, val) or find_node(root.right, val)


def all_nodes(root):
    return [] if root is None else [root] + all_nodes(root.left) + all_nodes(root.right)


def tree_height(root):
    return 0 if root is None else 1 + max(tree_height(root.left), tree_height(root.right))


def random_tree(n, seed, lo=0, hi=9, distinct=False):
    """A random-shaped tree of n nodes: each new node hangs off a random free slot."""
    rng = random.Random(seed)
    if n == 0:
        return None
    pool = rng.sample(range(lo, hi + 1), n) if distinct else [rng.randint(lo, hi) for _ in range(n)]
    root = TreeNode(pool[0])
    slots = [(root, "left"), (root, "right")]
    for v in pool[1:]:
        parent, side = slots.pop(rng.randrange(len(slots)))
        child = TreeNode(v)
        setattr(parent, side, child)
        slots += [(child, "left"), (child, "right")]
    return root


def random_bst(n, seed, lo=0, hi=999):
    """A BST of n distinct values inserted in random order."""
    rng = random.Random(seed)
    root = None
    for v in rng.sample(range(lo, hi + 1), n):
        root = _bst_add(root, v)
    return root


def _bst_add(node, v):
    if node is None:
        return TreeNode(v)
    if v < node.val:
        node.left = _bst_add(node.left, v)
    else:
        node.right = _bst_add(node.right, v)
    return node


def is_valid_bst(root, lo=float("-inf"), hi=float("inf")):
    if root is None:
        return True
    return lo < root.val < hi and is_valid_bst(root.left, lo, root.val) \\
        and is_valid_bst(root.right, root.val, hi)


def is_height_balanced(root):
    def h(node):
        if node is None:
            return 0
        a, b = h(node.left), h(node.right)
        if a < 0 or b < 0 or abs(a - b) > 1:
            return -1
        return 1 + max(a, b)
    return h(root) >= 0


def shape(root):
    """A hashable description of structure and values, for comparing trees."""
    return None if root is None else (root.val, shape(root.left), shape(root.right))
'''
