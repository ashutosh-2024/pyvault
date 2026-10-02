# -*- coding: utf-8 -*-
"""Binary Trees: building, converting and iterating BSTs, two BSTs at once,
BST DP, and recovering a corrupted BST."""

SECTIONS = [

# ---------------------------------------------------------------- construction
dict(
    id="bst-construction",
    title="Building a balanced BST",
    idea=[
        "Sorted input plus \"pick the middle as the root\" gives a height-balanced BST, because each side then gets half the values. The problems differ in how cheaply you can reach the middle.",
    ],
    problems=[

    dict(
        id="sorted-array-to-bst",
        lc=108, slug="convert-sorted-array-to-binary-search-tree",
        name="Convert Sorted Array to Binary Search Tree",
        difficulty="easy",
        framing=[
            "Build a <em>height-balanced</em> BST from a sorted array. The middle element is the root; the halves on either side build the subtrees recursively.",
        ],
        approaches=[
            dict(
                name="Middle as root, recurse on index ranges",
                time="O(n)",
                space="O(log n)",
                best=True,
                why=[
                    "Choosing the middle splits the remaining values as evenly as possible, so the two subtree sizes differ by at most one at every node, which keeps the heights within one: balanced by construction.",
                    "Each value becomes one node with O(1) work: O(n). Recursing on <code>(lo, hi)</code> indices instead of slices avoids O(n log n) copying, and the recursion depth is the tree height, O(log n).",
                ],
                code='''def sorted_array_to_bst(nums):
    def make(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(nums[mid], make(lo, mid - 1), make(mid + 1, hi))

    return make(0, len(nums) - 1)''',
            ),
        ],
        tests='''for n in range(0, 40):
    t = sorted_array_to_bst(list(range(n)))
    assert vals_in(t) == list(range(n)) and is_height_balanced(t), n
assert level_order(sorted_array_to_bst([-10, -3, 0, 5, 9])) == [0, -10, 5, None, -3, None, 9]''',
    ),

    dict(
        id="sorted-list-to-bst",
        lc=109, slug="convert-sorted-list-to-binary-search-tree",
        name="Convert Sorted List to Binary Search Tree",
        difficulty="medium",
        framing=[
            "The same task from a sorted <em>linked list</em>, where reaching the middle is no longer O(1). Three answers, each trading something different.",
        ],
        approaches=[
            dict(
                name="Inorder simulation",
                time="O(n)",
                space="O(log n)",
                best=True,
                why=[
                    "Count the nodes, then build the tree in <em>inorder</em>: recursively build the left half of the range, then consume the next list node as the root, then build the right half. Inorder visits values in sorted order, which is exactly the order the list supplies them, so a single pointer walking the list is always at the right value.",
                    "Each list node is consumed once: O(n), with only the O(log n) recursion stack. This is the answer interviewers are looking for.",
                ],
                code='''def sorted_list_to_bst(head):
    n, node = 0, head
    while node:
        n, node = n + 1, node.next
    cur = head

    def make(lo, hi):
        nonlocal cur
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        left = make(lo, mid - 1)             # everything smaller is consumed first
        root = TreeNode(cur.val, left)
        cur = cur.next
        root.right = make(mid + 1, hi)
        return root

    return make(0, n - 1)''',
            ),
            dict(
                name="Copy to an array",
                time="O(n)",
                space="O(n)",
                why=[
                    "Read the list into an array and solve the previous problem. Linear time and perfectly acceptable &mdash; it just spends O(n) extra memory.",
                ],
                code='''def sorted_list_to_bst(head):
    vals = []
    while head:
        vals.append(head.val)
        head = head.next

    def make(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(vals[mid], make(lo, mid - 1), make(mid + 1, hi))

    return make(0, len(vals) - 1)''',
            ),
            dict(
                name="Fast and slow pointers for each middle",
                time="O(n log n)",
                space="O(log n)",
                why=[
                    "Find each range's middle with slow/fast pointers and split the list there. Every level of the recursion walks the whole list once, and there are O(log n) levels: O(n log n).",
                ],
                code='''def sorted_list_to_bst(head, tail=None):
    if head is tail:
        return None
    slow = fast = head
    while fast is not tail and fast.next is not tail:
        slow, fast = slow.next, fast.next.next
    return TreeNode(slow.val,
                    sorted_list_to_bst(head, slow),
                    sorted_list_to_bst(slow.next, tail))''',
            ),
        ],
        tests='''for n in range(0, 30):
    t = sorted_list_to_bst(build_list(list(range(n))))
    assert vals_in(t) == list(range(n)) and is_height_balanced(t), n''',
    ),

    dict(
        id="bst-from-preorder",
        lc=1008, slug="construct-binary-search-tree-from-preorder-traversal",
        name="Construct Binary Search Tree from Preorder Traversal",
        difficulty="medium",
        framing=[
            "Rebuild a BST from its preorder traversal. For a general tree you needed inorder as well; for a BST, inorder is just the sorted values, so preorder alone is enough. Better still, the bounds trick from Serialize and Deserialize BST builds it in one pass.",
        ],
        approaches=[
            dict(
                name="One pass with value bounds",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Read values in order. The next value belongs at the current position only if it fits the bounds inherited from the ancestors; if not, this subtree is complete and the value belongs further up.",
                    "Each value is read once: O(n) time, O(h) recursion.",
                ],
                code='''def bst_from_preorder(preorder):
    i = 0

    def make(hi):
        nonlocal i
        if i == len(preorder) or preorder[i] > hi:
            return None
        node = TreeNode(preorder[i]); i += 1
        node.left = make(node.val)          # smaller values go left
        node.right = make(hi)
        return node

    return make(float("inf"))''',
            ),
            dict(
                name="Insert each value in turn",
                time="O(n&sup2;) worst",
                space="O(h)",
                why=[
                    "Inserting the values in preorder order recreates exactly the original tree, because each value's ancestors were inserted before it. Each insert is O(h), so O(n log n) balanced and O(n&sup2;) for sorted input.",
                ],
                code='''def bst_from_preorder(preorder):
    root = None
    for v in preorder:
        if root is None:
            root = TreeNode(v)
            continue
        node = root
        while True:
            side = "left" if v < node.val else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, TreeNode(v))
                break
            node = child
    return root''',
            ),
        ],
        tests='''assert level_order(bst_from_preorder([8, 5, 1, 7, 10, 12])) == [8, 5, 10, 1, 7, None, 12]
assert level_order(bst_from_preorder([1, 3])) == [1, None, 3]
for seed in range(25):
    t = random_bst(1 + seed * 2, seed)
    assert shape(bst_from_preorder(vals_pre(t))) == shape(t), seed''',
    ),
    ],
),

# ---------------------------------------------------------------- conversion
dict(
    id="bst-conversion",
    title="Converting a BST in place",
    idea=[
        "Inorder visits nodes in sorted order; reverse inorder visits them in descending order. Rewriting values or pointers during that walk converts the tree without an intermediate list.",
    ],
    problems=[

    dict(
        id="bst-to-greater-tree",
        lc=538, slug="convert-bst-to-greater-tree",
        name="Convert BST to Greater Tree",
        difficulty="medium",
        framing=[
            "Replace every value with itself plus the sum of all larger values. In descending order, each node needs the running total of everything visited so far &mdash; which is reverse inorder with an accumulator.",
        ],
        approaches=[
            dict(
                name="Reverse inorder with a running sum",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Visit right, node, left. By the time a node is visited, every larger value has already been added to <code>running</code>, so add the node's value and write the total back.",
                ],
                code='''def convert_bst(root):
    running = 0

    def walk(node):
        nonlocal running
        if node is None:
            return
        walk(node.right)
        running += node.val
        node.val = running
        walk(node.left)

    walk(root)
    return root''',
            ),
            dict(
                name="Reverse Morris traversal",
                time="O(n)",
                space="O(1)",
                why=[
                    "The Morris threading trick with left and right swapped: thread each right subtree's leftmost node back to its ancestor. Same result with no stack, at the cost of temporarily modifying pointers.",
                ],
                code='''def convert_bst(root):
    running, node = 0, root
    while node is not None:
        if node.right is None:
            running += node.val
            node.val = running
            node = node.left
            continue
        succ = node.right
        while succ.left is not None and succ.left is not node:
            succ = succ.left
        if succ.left is None:
            succ.left = node                 # thread back, go right first
            node = node.right
        else:
            succ.left = None
            running += node.val
            node.val = running
            node = node.left
    return root''',
            ),
        ],
        tests='''t = convert_bst(build([4, 1, 6, 0, 2, 5, 7, None, None, None, 3, None, None, None, 8]))
assert level_order(t) == [30, 36, 21, 36, 35, 26, 15, None, None, None, 33, None, None, None, 8]
assert level_order(convert_bst(build([0, None, 1]))) == [1, None, 1]''',
    ),

    dict(
        id="balance-bst",
        lc=1382, slug="balance-a-binary-search-tree",
        name="Balance a Binary Search Tree",
        difficulty="medium",
        framing=[
            "Return a height-balanced BST with the same values. It is the bridge to self-balancing trees: those keep a tree balanced on every insert, whereas this rebuilds it once, after the fact.",
        ],
        approaches=[
            dict(
                name="Inorder to a list, rebuild from the middle",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Inorder gives the nodes in sorted order; then build exactly as in Convert Sorted Array to BST, re-using the existing node objects. Both phases are O(n).",
                ],
                code='''def balance_bst(root):
    nodes = []

    def walk(node):
        if node is not None:
            walk(node.left)
            nodes.append(node)
            walk(node.right)

    walk(root)

    def make(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = nodes[mid]
        node.left, node.right = make(lo, mid - 1), make(mid + 1, hi)
        return node

    return make(0, len(nodes) - 1)''',
            ),
            dict(
                name="Day&ndash;Stout&ndash;Warren: rotations only",
                time="O(n)",
                space="O(1)",
                tag="no extra memory",
                why=[
                    "DSW balances in place with rotations. First, right-rotate until the tree is a right-leaning \"vine\" (a sorted linked list through <code>right</code>). Then repeatedly left-rotate every other node on the vine, halving its length each round, which folds it into a balanced tree.",
                    "Every rotation is O(1) and there are O(n) of them in total, with no list and no recursion: O(1) extra space. The rotation used here is the same one AVL and red-black trees are built on.",
                ],
                code='''def balance_bst(root):
    pseudo = TreeNode(0, None, root)

    # 1. flatten into a right-leaning vine with right rotations
    tail, rest, size = pseudo, root, 0
    while rest is not None:
        if rest.left is None:
            tail, rest = rest, rest.right
            size += 1
        else:
            child = rest.left
            rest.left, child.right = child.right, rest
            rest = tail.right = child

    # 2. fold the vine: left-rotate every other node, halving each round
    def compress(count):
        scanner = pseudo
        for _ in range(count):
            child = scanner.right
            scanner.right = child.right
            scanner = scanner.right
            child.right, scanner.left = scanner.left, child

    leaves = size + 1 - (1 << (size + 1).bit_length() - 1)
    compress(leaves)
    size -= leaves
    while size > 1:
        size //= 2
        compress(size)
    return pseudo.right''',
            ),
        ],
        tests='''for seed in range(30):
    t = random_bst(seed * 3, seed)
    values = vals_in(t)
    got = balance_bst(t)
    assert vals_in(got) == values and is_height_balanced(got), seed
chain = build([1, None, 2, None, 3, None, 4])
got = balance_bst(chain)
assert vals_in(got) == [1, 2, 3, 4] and is_height_balanced(got)''',
    ),

    dict(
        id="bst-to-sorted-dll",
        lc=426, slug="convert-binary-search-tree-to-sorted-doubly-linked-list",
        name="Convert BST to Sorted Doubly Linked List",
        difficulty="medium",
        tags=["Linked List", "Stack", "Tree", "Binary Search Tree"],
        statement=[
            "Convert a BST into a sorted <strong>circular</strong> doubly linked list <em>in place</em>. Use each node's <code>left</code> pointer as <em>previous</em> and <code>right</code> as <em>next</em>. The last node's <code>right</code> points to the first node and the first node's <code>left</code> points to the last. Return the smallest node.",
            "This is a LeetCode Premium problem, so the statement here is written from scratch.",
        ],
        examples=[
            dict(input="root = [4,2,5,1,3]", output="1 &harr; 2 &harr; 3 &harr; 4 &harr; 5, circular"),
            dict(input="root = []", output="null"),
        ],
        constraints=[
            "<code>0 &lt;= n &lt;= 2000</code>",
            "All values are unique",
        ],
        approaches=[
            dict(
                name="Inorder, link each node to the previous one",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Walk inorder keeping <code>prev</code> (the last node linked) and <code>head</code> (the first). For each node, set <code>prev.right = node</code> and <code>node.left = prev</code>. At the end, join <code>head</code> and <code>prev</code> to close the circle.",
                    "It is the same shape as Increasing Order Search Tree, with the back pointers filled in as well. O(n) time, O(h) stack.",
                ],
                code='''def tree_to_doubly_list(root):
    if root is None:
        return None
    head = prev = None

    def walk(node):
        nonlocal head, prev
        if node is None:
            return
        walk(node.left)
        if prev is None:
            head = node
        else:
            prev.right, node.left = node, prev
        prev = node
        walk(node.right)

    walk(root)
    head.left, prev.right = prev, head         # close the circle
    return head''',
            ),
        ],
        tests='''assert tree_to_doubly_list(None) is None
for seed in range(20):
    t = random_bst(1 + seed * 2, seed)
    values = vals_in(t)
    head = tree_to_doubly_list(t)
    forward, node = [], head
    for _ in range(len(values)):
        forward.append(node.val)
        assert node.right.left is node
        node = node.right
    assert node is head and forward == values, seed''',
    ),
    ],
),

# ---------------------------------------------------------------- iterator
dict(
    id="bst-iterator",
    title="Lazy inorder: the BST iterator",
    idea=[
        "BST &rarr; inorder &rarr; a sorted stream, produced one value at a time without materialising the whole sorted array. The explicit-stack inorder traversal, paused between values, is exactly that.",
    ],
    problems=[

    dict(
        id="bst-iterator",
        lc=173, slug="binary-search-tree-iterator",
        name="Binary Search Tree Iterator",
        difficulty="medium",
        framing=[
            "Implement <code>next()</code> (the next smallest value) and <code>hasNext()</code> over a BST, using O(h) memory and average O(1) time per call. Flattening the tree into a list up front meets the time bound but not the memory bound.",
        ],
        approaches=[
            dict(
                name="Controlled stack of the left spine",
                time="O(1) amortised per call",
                space="O(h)",
                best=True,
                why=[
                    "The stack holds the path of nodes whose values are still to come, smallest on top. <code>next()</code> pops the top, then pushes the left spine of its right subtree &mdash; exactly the next values in order.",
                    "A single call can push O(h) nodes, but each node is pushed and popped exactly once over the whole iteration, so n calls cost O(n) in total: O(1) amortised. The stack never holds more than one root-to-leaf path: O(h).",
                ],
                code='''class BSTIterator:
    def __init__(self, root):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node):
        while node is not None:
            self.stack.append(node)
            node = node.left

    def next(self):
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val

    def hasNext(self):
        return bool(self.stack)''',
            ),
            dict(
                name="Python generator",
                time="O(1) amortised per call",
                space="O(h)",
                tag="idiomatic Python",
                why=[
                    "A recursive generator with <code>yield from</code> suspends the traversal between values: Python keeps the paused frames for you, one per level, so it is the same O(h) state as the explicit stack. Peeking for <code>hasNext</code> needs one value of look-ahead.",
                    "Nesting <code>yield from</code> O(h) deep adds O(h) overhead per value in CPython, so on a deep tree the explicit stack is faster; the generator is the more readable version.",
                ],
                code='''class BSTIterator:
    def __init__(self, root):
        self._gen = self._inorder(root)
        self._peek = next(self._gen, None)

    def _inorder(self, node):
        if node is not None:
            yield from self._inorder(node.left)
            yield node.val
            yield from self._inorder(node.right)

    def next(self):
        val, self._peek = self._peek, next(self._gen, None)
        return val

    def hasNext(self):
        return self._peek is not None''',
            ),
        ],
        tests='''it = BSTIterator(build([7, 3, 15, None, None, 9, 20]))
out = []
while it.hasNext():
    out.append(it.next())
assert out == [3, 7, 9, 15, 20]
for seed in range(15):
    t = random_bst(seed * 4, seed)
    it, got = BSTIterator(t), []
    while it.hasNext():
        got.append(it.next())
    assert got == vals_in(t), seed''',
    ),
    ],
),

# ---------------------------------------------------------------- two BSTs
dict(
    id="two-bsts",
    title="Two sorted streams",
    idea=[
        "Each BST is a sorted stream. Two streams can be merged, and one stream read from both ends at once gives the two-pointer technique &mdash; all with iterators, in O(h) memory.",
    ],
    problems=[

    dict(
        id="all-elements-two-bsts",
        lc=1305, slug="all-elements-in-two-binary-search-trees",
        name="All Elements in Two Binary Search Trees",
        difficulty="medium",
        framing=[
            "Return all values from both trees in ascending order. Each tree is already sorted in inorder, so this is the merge step of merge sort, driven by two BST iterators.",
        ],
        approaches=[
            dict(
                name="Merge two inorder iterators",
                time="O(m + n)",
                space="O(h<sub>1</sub> + h<sub>2</sub>)",
                best=True,
                why=[
                    "Advance whichever iterator has the smaller current value. Each value is produced once, and only the two stacks are held besides the output.",
                ],
                code='''def get_all_elements(root1, root2):
    def spine(node, stack):
        while node:
            stack.append(node)
            node = node.left

    s1, s2, out = [], [], []
    spine(root1, s1)
    spine(root2, s2)
    while s1 or s2:
        if not s2 or (s1 and s1[-1].val <= s2[-1].val):
            node = s1.pop(); spine(node.right, s1)
        else:
            node = s2.pop(); spine(node.right, s2)
        out.append(node.val)
    return out''',
            ),
            dict(
                name="Concatenate both inorders and sort",
                time="O(m + n) in CPython",
                space="O(m + n)",
                tag="surprisingly fast",
                why=[
                    "Traverse both, concatenate, call <code>sorted</code>. Nominally O((m + n) log(m + n)) &mdash; but CPython's Timsort detects the two already-sorted runs and merges them in linear time, so in practice this is as fast as the hand-written merge and much shorter.",
                    "Saying that in an interview shows you know the library; still be ready to write the merge, since that is what is being tested.",
                ],
                code='''def get_all_elements(root1, root2):
    return sorted(vals_in(root1) + vals_in(root2))''',
            ),
        ],
        tests='''assert get_all_elements(build([2, 1, 4]), build([1, 0, 3])) == [0, 1, 1, 2, 3, 4]
assert get_all_elements(build([1, None, 8]), build([8, 1])) == [1, 1, 8, 8]
assert get_all_elements(None, build([1])) == [1]
for seed in range(15):
    a, b = random_bst(seed * 2, seed), random_bst(seed * 3, seed + 100)
    assert get_all_elements(a, b) == sorted(vals_in(a) + vals_in(b))''',
    ),

    dict(
        id="two-sum-bst",
        lc=653, slug="two-sum-iv-input-is-a-bst",
        name="Two Sum IV - Input is a BST",
        difficulty="easy",
        framing=[
            "Do two <em>different</em> nodes sum to <code>k</code>? The hash-set answer from array Two Sum works on any tree. The BST allows the sorted-array answer instead &mdash; two pointers closing in from both ends &mdash; using a forward and a backward iterator over the same tree.",
        ],
        approaches=[
            dict(
                name="Hash set during any traversal",
                time="O(n)",
                space="O(n)",
                why=[
                    "For each value, check whether <code>k - value</code> has been seen. Ignores the ordering entirely; O(n) time and O(n) memory.",
                ],
                code='''def find_target(root, k):
    seen, stack = set(), [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if k - node.val in seen:
            return True
        seen.add(node.val)
        stack += [node.left, node.right]
    return False''',
            ),
            dict(
                name="Two pointers with forward and backward iterators",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "One iterator yields values ascending (inorder), the other descending (reverse inorder). If the sum is too small, advance the low one; too large, advance the high one; stop when they meet.",
                    "Each value is produced at most once by each iterator: O(n) time. Memory is two stacks, O(h) &mdash; this is the version that uses the BST.",
                ],
                code='''def find_target(root, k):
    def push(stack, node, forward):
        while node:
            stack.append(node)
            node = node.left if forward else node.right

    lo, hi = [], []
    push(lo, root, True)
    push(hi, root, False)
    while lo and hi and lo[-1] is not hi[-1]:
        total = lo[-1].val + hi[-1].val
        if total == k:
            return True
        if total < k:
            node = lo.pop(); push(lo, node.right, True)
        else:
            node = hi.pop(); push(hi, node.left, False)
    return False''',
            ),
        ],
        tests='''t = build([5, 3, 6, 2, 4, None, 7])
assert find_target(t, 9) is True
assert find_target(t, 28) is False
assert find_target(build([1]), 2) is False          # one node cannot pair with itself
assert find_target(build([2, 1, 3]), 4) is True
for seed in range(15):
    t = random_bst(seed * 2, seed, 0, 60)
    vals = vals_in(t)
    for k in range(0, 121, 5):
        expect = any(vals[i] + vals[j] == k for i in range(len(vals)) for j in range(i + 1, len(vals)))
        assert find_target(t, k) is expect''',
    ),
    ],
),

# ---------------------------------------------------------------- BST DP
dict(
    id="bst-dp",
    title="Counting and building BSTs with DP",
    idea=[
        "Choosing a root splits the values into a left set and a right set, and the two sides are independent. That independence is what makes counting, generating and optimising over BSTs a dynamic programme.",
    ],
    problems=[

    dict(
        id="unique-bsts",
        lc=96, slug="unique-binary-search-trees",
        name="Unique Binary Search Trees",
        difficulty="medium",
        framing=[
            "How many structurally different BSTs store the values <code>1..n</code>? Pick root <code>r</code>: the left subtree is a BST of <code>r - 1</code> values and the right one of <code>n - r</code>, and any left shape can pair with any right shape.",
        ],
        approaches=[
            dict(
                name="Bottom-up DP over sizes",
                time="O(n&sup2;)",
                space="O(n)",
                best=True,
                why=[
                    "<code>G[n] = &Sigma; G[r-1] &middot; G[n-r]</code> for <code>r = 1..n</code>, with <code>G[0] = 1</code> (one empty tree). Only the <em>size</em> of each side matters, not which values it holds, which is why a 1-D table suffices.",
                    "These are the Catalan numbers. Recognising the recurrence is worth more than the code: the same numbers count balanced parenthesisations, triangulations and full binary trees.",
                ],
                code='''def num_trees(n):
    G = [1] + [0] * n
    for size in range(1, n + 1):
        for root in range(1, size + 1):
            G[size] += G[root - 1] * G[size - root]
    return G[n]''',
            ),
            dict(
                name="Closed form: the Catalan number",
                time="O(n)",
                space="O(1)",
                why=[
                    "C<sub>n</sub> = C(2n, n) / (n + 1). <code>math.comb</code> computes the binomial exactly with Python's big integers.",
                ],
                code='''from math import comb


def num_trees(n):
    return comb(2 * n, n) // (n + 1)''',
            ),
        ],
        tests='''assert [num_trees(n) for n in range(1, 8)] == [1, 2, 5, 14, 42, 132, 429]
assert num_trees(19) == 1767263190''',
    ),

    dict(
        id="unique-bsts-ii",
        lc=95, slug="unique-binary-search-trees-ii",
        name="Unique Binary Search Trees II",
        difficulty="medium",
        framing=[
            "Now return the trees themselves. The counting recurrence becomes a generating one: for each root, combine every left tree over the smaller values with every right tree over the larger ones.",
        ],
        approaches=[
            dict(
                name="Recursive generation over value ranges, memoised",
                time="O(n &middot; C<sub>n</sub>)",
                space="O(n &middot; C<sub>n</sub>)",
                best=True,
                why=[
                    "<code>gen(lo, hi)</code> returns every BST on the values <code>lo..hi</code>. Unlike the counting version, the values matter here, so the key is the range, not just its size. Caching by range lets the returned trees share subtrees.",
                    "The output alone is C<sub>n</sub> trees of n nodes, so nothing can be asymptotically faster than the output size.",
                ],
                code='''from functools import cache


def generate_trees(n):
    @cache
    def gen(lo, hi):
        if lo > hi:
            return [None]
        out = []
        for root in range(lo, hi + 1):
            for left in gen(lo, root - 1):
                for right in gen(root + 1, hi):
                    out.append(TreeNode(root, left, right))
        return out

    return gen(1, n) if n else []''',
            ),
        ],
        tests='''trees = generate_trees(3)
assert sorted(level_order(t) for t in trees) == sorted([
    [1, None, 2, None, 3], [1, None, 3, 2], [2, 1, 3], [3, 1, None, None, 2], [3, 2, None, 1]])
for n in range(1, 8):
    trees = generate_trees(n)
    assert len(trees) == [1, 2, 5, 14, 42, 132, 429][n - 1]
    assert all(vals_in(t) == list(range(1, n + 1)) for t in trees)
    assert len({shape(t) for t in trees}) == len(trees)''',
    ),

    dict(
        id="max-sum-bst",
        lc=1373, slug="maximum-sum-bst-in-binary-tree",
        name="Maximum Sum BST in Binary Tree",
        difficulty="hard",
        framing=[
            "In an arbitrary binary tree, find the subtree that is a valid BST with the largest sum of keys (an empty BST has sum 0). Each node must know whether its children's subtrees are BSTs and, if so, their minimum, maximum and sum &mdash; four pieces of information returned together.",
        ],
        approaches=[
            dict(
                name="Postorder returning (is_bst, min, max, sum)",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "A node's subtree is a BST exactly when both children's are, and <code>left.max &lt; node.val &lt; right.min</code>. Its min, max and sum follow from the children's. Empty subtrees report min = +&infin; and max = -&infin;, which make the comparison succeed without special cases.",
                    "Once any subtree fails, every ancestor fails too, so a failed subtree just reports <code>False</code> and its contents stop mattering. One pass: O(n). Validating each subtree from scratch instead would be O(n&sup2;).",
                ],
                code='''def max_sum_bst(root):
    best = 0
    INF = float("inf")

    def dfs(node):
        """Return (is_bst, min, max, sum) for this subtree."""
        nonlocal best
        if node is None:
            return True, INF, -INF, 0
        lb, lmin, lmax, lsum = dfs(node.left)
        rb, rmin, rmax, rsum = dfs(node.right)
        if lb and rb and lmax < node.val < rmin:
            total = lsum + rsum + node.val
            best = max(best, total)
            return True, min(lmin, node.val), max(rmax, node.val), total
        return False, 0, 0, 0

    dfs(root)
    return best''',
            ),
        ],
        tests='''assert max_sum_bst(build([1, 4, 3, 2, 4, 2, 5, None, None, None, None, None, None, 4, 6])) == 20
assert max_sum_bst(build([4, 3, None, 1, 2])) == 2
assert max_sum_bst(build([-4, -2, -5])) == 0
assert max_sum_bst(build([2, 1, 3])) == 6
assert max_sum_bst(build([5, 4, 8, 3, None, 6, 3])) == 7


def _brute(root):
    def is_bst(n, lo, hi):
        return n is None or (lo < n.val < hi and is_bst(n.left, lo, n.val) and is_bst(n.right, n.val, hi))
    def total(n):
        return 0 if n is None else n.val + total(n.left) + total(n.right)
    inf = float("inf")
    return max([0] + [total(n) for n in all_nodes(root) if is_bst(n, -inf, inf)])

for seed in range(40):
    t = random_tree(1 + seed % 15, seed, -10, 10)
    assert max_sum_bst(t) == _brute(t), seed''',
    ),
    ],
),

# ---------------------------------------------------------------- recover
dict(
    id="recover-bst",
    title="Recovering a corrupted BST",
    idea=[
        "Inorder of a BST is sorted, so a corruption shows up as inversions in that sequence. Two swapped values create one inversion if they were adjacent in order and two if they were not.",
    ],
    problems=[

    dict(
        id="recover-bst",
        lc=99, slug="recover-binary-search-tree",
        name="Recover Binary Search Tree",
        difficulty="medium",
        framing=[
            "Exactly two nodes of a BST had their values swapped by mistake. Restore the tree without changing its structure. The follow-up asks for O(1) extra space, which is the reason to learn Morris traversal.",
        ],
        approaches=[
            dict(
                name="Inorder, find the inversions",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Walk inorder comparing each node with the previous one. At the first inversion (<code>prev.val &gt; node.val</code>), the <em>larger</em> value, <code>prev</code>, is out of place. At the last inversion, the <em>smaller</em> value, <code>node</code>, is. If there is only one inversion, both come from it. Swap the two values back.",
                    "Example: sorted <code>1 2 3 4 5</code> with 2 and 4 swapped reads <code>1 4 3 2 5</code>. The inversions are 4&gt;3 and 3&gt;2: first gives 4, last gives 2.",
                    "O(n) time, O(h) stack.",
                ],
                code='''def recover_tree(root):
    first = second = prev = None

    def walk(node):
        nonlocal first, second, prev
        if node is None:
            return
        walk(node.left)
        if prev is not None and prev.val > node.val:
            if first is None:
                first = prev              # larger value of the first inversion
            second = node                 # smaller value of the last inversion
        prev = node
        walk(node.right)

    walk(root)
    first.val, second.val = second.val, first.val''',
            ),
            dict(
                name="Morris inorder",
                time="O(n)",
                space="O(1)",
                tag="follow-up",
                why=[
                    "The same inversion scan driven by Morris traversal, so no stack at all. Every thread is removed as the traversal completes, and the swap happens at the end, leaving the structure exactly as it was.",
                ],
                code='''def recover_tree(root):
    first = second = prev = None
    node = root

    def visit(cur):
        nonlocal first, second, prev
        if prev is not None and prev.val > cur.val:
            if first is None:
                first = prev
            second = cur
        prev = cur

    while node is not None:
        if node.left is None:
            visit(node)
            node = node.right
            continue
        pred = node.left
        while pred.right is not None and pred.right is not node:
            pred = pred.right
        if pred.right is None:
            pred.right = node
            node = node.left
        else:
            pred.right = None
            visit(node)
            node = node.right
    first.val, second.val = second.val, first.val''',
            ),
        ],
        tests='''t = build([1, 3, None, None, 2])
recover_tree(t)
assert level_order(t) == [3, 1, None, None, 2]
t = build([3, 1, 4, None, None, 2])
recover_tree(t)
assert level_order(t) == [2, 1, 4, None, None, 3]
for seed in range(30):
    t = random_bst(2 + seed, seed)
    before = shape(t)
    a, b = random.Random(seed).sample(all_nodes(t), 2)
    a.val, b.val = b.val, a.val
    recover_tree(t)
    assert shape(t) == before, seed''',
    ),
    ],
),
]
