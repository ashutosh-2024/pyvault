"""Write-ups for Trees, part F: iterators, two BSTs, BST DP, recovery, balanced trees, n-ary, next pointers."""

_NARY = "build_nary([1, None, 3, 2, 4, None, 5, 6])"
_NARY_SHAPE = "The tree: 1 has children 3, 2, 4; 3 has children 5, 6."

EXPLAIN = {
    # ------------------------------------------------------------------ BST iterator
    "bst-iterator": {
        "example": {"setup": "it = BSTIterator(build([7, 3, 15, None, None, 9, 20]))",
                    "call": "[it.next(), it.next(), it.hasNext(), it.next(), it.next(), it.next(), it.hasNext()]",
                    "expect": "[3, 7, True, 9, 15, 20, False]"},
        "approaches": {
            "Controlled stack of the left spine": {
                "idea": [
                    "This is iterative inorder, paused between values.",
                    "The stack holds the nodes still to come, smallest on top. <code>next()</code> pops it, then pushes the left spine of its right subtree, which holds the next values in order.",
                ],
                "steps": [
                    "<code>__init__</code>: push the left spine from the root.",
                    "<code>next</code>: pop, push <code>node.right</code>'s left spine, return the value. <code>hasNext</code>: the stack is non-empty.",
                ],
                "why": [
                    "Each node is pushed and popped once over the whole iteration: O(1) amortised per call, and O(h) memory.",
                ],
                "dry": [
                    "The tree: 7 → (3, 15), 15 → (9, 20). The stack starts as [7, 3].",
                    "next() → 3 (stack [7]); next() → 7, then push 15 and 9 (stack [15, 9]). hasNext() → True.",
                    "next() → 9, 15 (pushing 20), 20; then hasNext() → False. The result is <strong>[3, 7, True, 9, 15, 20, False]</strong>.",
                ],
            },
            "Python generator": {
                "idea": [
                    "A recursive generator with <code>yield from</code> pauses the inorder walk between values; Python keeps the paused frames for you.",
                    "<code>hasNext</code> needs one value of look-ahead, stored in <code>_peek</code>.",
                ],
                "steps": [
                    "<code>next</code> returns <code>_peek</code> and fetches the following value.",
                ],
                "why": [
                    "It holds O(h) state, but nested <code>yield from</code> adds O(h) overhead per value.",
                ],
                "dry": [
                    "_peek starts at 3. Each next() returns it and fetches the next of 7, 9, 15, 20.",
                    "After 20, _peek is None, so hasNext() is False.",
                    "The result is <strong>[3, 7, True, 9, 15, 20, False]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ all elements in two BSTs
    "all-elements-two-bsts": {
        "example": {"call": "get_all_elements(build([2, 1, 4]), build([1, 0, 3]))", "expect": "[0, 1, 1, 2, 3, 4]"},
        "approaches": {
            "Merge two inorder iterators": {
                "idea": [
                    "Each BST produces its values in sorted order through an inorder iterator.",
                    "Merge the two streams as in merge sort: take whichever current value is smaller.",
                ],
                "steps": [
                    "Two left-spine stacks; pop from the one with the smaller top and push its right child's spine.",
                ],
                "why": [
                    "Each value is produced once: O(m + n) time, with only the two stacks besides the output.",
                ],
                "dry": [
                    "The streams are 1, 2, 4 and 0, 1, 3.",
                    "Take 0 (B), 1 (A, which wins ties), 1 (B), 2 (A), 3 (B), 4 (A).",
                    "The result is <strong>[0, 1, 1, 2, 3, 4]</strong>.",
                ],
            },
            "Concatenate both inorders and sort": {
                "idea": [
                    "Concatenate both inorder lists and sort. Timsort detects the two sorted runs and merges them in linear time.",
                ],
                "steps": [
                    "<code>sorted(vals_in(a) + vals_in(b))</code>.",
                ],
                "why": [
                    "It is O(m + n) in practice, and much shorter.",
                ],
                "dry": [
                    "[1, 2, 4] + [0, 1, 3] are merged as two runs.",
                    "The result is <strong>[0, 1, 1, 2, 3, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ two sum BST
    "two-sum-bst": {
        "example": {"call": "find_target(build([5, 3, 6, 2, 4, None, 7]), 9)", "expect": "True"},
        "approaches": {
            "Hash set during any traversal": {
                "idea": [
                    "This is the classic Two Sum: for each value, check whether <code>k - value</code> has been seen; otherwise remember the value.",
                ],
                "steps": [
                    "Any traversal order; a set of the values seen so far.",
                ],
                "why": [
                    "It is O(n) time and O(n) memory, and ignores the BST ordering.",
                ],
                "dry": [
                    "The tree: 5 → (3, 6), 3 → (2, 4), 6 → (None, 7).",
                    "Pop 5 (need 4, not seen), 6 (need 3), 7 (need 2), then 3: it needs 6, which has been seen.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Two pointers with forward and backward iterators": {
                "idea": [
                    "One iterator yields values ascending, another descending. This is the sorted-array two-pointer technique, run directly on the tree.",
                    "If the sum is too small, advance the low iterator; if it is too large, advance the high one; stop when they meet.",
                ],
                "steps": [
                    "<code>lo</code> holds the left spine and <code>hi</code> the right spine; compare their tops.",
                ],
                "why": [
                    "It is O(n) time and only O(h) memory, so it uses the BST.",
                ],
                "dry": [
                    "The smallest value is 2 and the largest is 7.",
                    "2 + 7 = 9 on the first comparison.",
                    "The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ unique BSTs
    "unique-bsts": {
        "example": {"call": "num_trees(4)", "expect": "14"},
        "approaches": {
            "Bottom-up DP over sizes": {
                "idea": [
                    "Pick a root r among 1..n. The values below r form the left subtree and those above form the right, independently.",
                    "Only the <em>sizes</em> matter, so <code>G[n] = Σ G[r-1] · G[n-r]</code>, with <code>G[0] = 1</code> (one empty tree).",
                ],
                "steps": [
                    "Fill G for sizes 1..n.",
                ],
                "why": [
                    "It is O(n²) time. These are the Catalan numbers.",
                ],
                "dry": [
                    "G = 1, 1, 2, 5 for sizes 0–3.",
                    "G[4] = G0·G3 + G1·G2 + G2·G1 + G3·G0 = 5 + 2 + 2 + 5.",
                    "The result is <strong>14</strong>.",
                ],
            },
            "Closed form: the Catalan number": {
                "idea": [
                    "C<sub>n</sub> = C(2n, n) / (n + 1), computed exactly with <code>math.comb</code>.",
                ],
                "steps": [
                    "<code>comb(2n, n) // (n + 1)</code>.",
                ],
                "why": [
                    "It is O(n) arithmetic.",
                ],
                "dry": [
                    "C(8, 4) = 70, and 70 / 5 = <strong>14</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ unique BSTs II
    "unique-bsts-ii": {
        "example": {"call": "sorted(level_order(t) for t in generate_trees(3))",
                    "expect": "[[1, None, 2, None, 3], [1, None, 3, 2], [2, 1, 3], [3, 1, None, None, 2], [3, 2, None, 1]]"},
        "approaches": {
            "Recursive generation over value ranges, memoised": {
                "idea": [
                    "<code>gen(lo, hi)</code> returns every BST on the values lo..hi.",
                    "For each root, pair every left tree from <code>gen(lo, root-1)</code> with every right tree from <code>gen(root+1, hi)</code>.",
                    "An empty range returns [None], one empty tree, so the products work at the edges.",
                ],
                "steps": [
                    "Cache by range, so the returned trees share subtrees.",
                ],
                "why": [
                    "The output alone is C<sub>n</sub> trees, so you cannot do asymptotically better.",
                ],
                "dry": [
                    "Root 1: right trees on {2, 3}: 2 of them. Root 2: 1 left × 1 right. Root 3: left trees on {1, 2}: 2 of them.",
                    "2 + 1 + 2 = 5 trees.",
                    "Sorted level orders: <strong>[[1, None, 2, None, 3], [1, None, 3, 2], [2, 1, 3], [3, 1, None, None, 2], [3, 2, None, 1]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max sum BST
    "max-sum-bst": {
        "example": {"call": "max_sum_bst(build([1, 4, 3, 2, 4, 2, 5, None, None, None, None, None, None, 4, 6]))", "expect": "20"},
        "approaches": {
            "Postorder returning (is_bst, min, max, sum)": {
                "idea": [
                    "A subtree is a BST exactly when both children are BSTs and <code>left.max &lt; val &lt; right.min</code>.",
                    "So each call returns four things: whether it is a BST, its min, its max, and its sum.",
                    "Empty subtrees return min = +∞ and max = -∞, so the comparison passes without special cases.",
                ],
                "steps": [
                    "If the checks pass, update <code>best</code> with the sum; otherwise return False, and every ancestor fails too.",
                ],
                "why": [
                    "One pass: O(n). Re-validating each subtree would be O(n²).",
                ],
                "dry": [
                    "The tree: 1 → (4, 3), 4 → (2, 4), 3 → (2, 5), 5 → (4, 6).",
                    "The left 4 fails (its right child 4 is not &gt; 4). 3's subtree passes: 2 &lt; 3 &lt; 4 (the min under 5).",
                    "Its sum is 3 + 2 + 5 + 4 + 6 = 20. The root fails. The result is <strong>20</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ recover BST
    "recover-bst": {
        "example": {"setup": "t = build([3, 1, 4, None, None, 2])\nrecover_tree(t)",
                    "call": "level_order(t)", "expect": "[2, 1, 4, None, None, 3]"},
        "approaches": {
            "Inorder, find the inversions": {
                "idea": [
                    "Inorder of a BST should be increasing; swapping two values creates one or two \"drops\" (prev &gt; current).",
                    "The first misplaced node is the <em>larger</em> value of the first drop; the second is the <em>smaller</em> value of the last drop.",
                    "Swap their values back.",
                ],
                "steps": [
                    "Track <code>prev</code>; set <code>first</code> once and <code>second</code> at every drop.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack, and the structure is unchanged.",
                ],
                "dry": [
                    "The tree: 3 → (1, 4), 4 → (2). Inorder: 1, 3, 2, 4.",
                    "There is one drop, 3 &gt; 2, so first = 3 and second = 2. Swap them.",
                    "The tree becomes <strong>[2, 1, 4, None, None, 3]</strong>.",
                ],
            },
            "Morris inorder": {
                "idea": [
                    "Run the same drop scan with a Morris traversal, so no stack is needed.",
                ],
                "steps": [
                    "<code>visit()</code> at each inorder step; swap at the end, after all threads are removed.",
                ],
                "why": [
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "The visits run 1, 3, 2, 4, finding the drop at 3 → 2.",
                    "The result is <strong>[2, 1, 4, None, None, 3]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ AVL
    "implement-avl-tree": {
        "example": {"setup": "t = AVLTree()\nfor k in [10, 20, 30, 40, 50, 25]:\n    t.insert(k)",
                    "call": "(t.inorder(), t.root.key, t.root.height)", "expect": "([10, 20, 25, 30, 40, 50], 30, 3)"},
        "approaches": {
            "Recursive insert and delete with rebalance on the way up": {
                "idea": [
                    "Each node stores its height. Its <strong>balance factor</strong> is height(left) - height(right), and AVL keeps it in {-1, 0, 1}.",
                    "After a normal BST insert or delete, every node on the path back up calls <code>rebalance</code>.",
                    "A factor of ±2 is fixed with rotations. LL and RR need one rotation; LR and RL first rotate the child to make it LL or RR.",
                    "A rotation re-hangs three subtrees around two nodes, keeping the inorder order and changing the height by one.",
                ],
                "steps": [
                    "<code>rebalance(n)</code>: update the height; if bf &gt; 1, maybe rotate the left child left, then rotate right; mirrored for bf &lt; -1.",
                    "Insert and delete return <code>rebalance(n)</code> instead of <code>n</code>.",
                ],
                "why": [
                    "The sparsest AVL tree of height h follows a Fibonacci-like recurrence, so h ≤ 1.44 log<sub>2</sub> n: every operation is O(log n).",
                ],
                "dry": [
                    "Insert 10, 20, 30: 10 is right-heavy (RR), so rotate left and 20 becomes the root. 40 and 50 make 30 right-heavy, and 40 replaces it.",
                    "Now 20 → (10, 40), 40 → (30, 50). Inserting 25 goes under 30, which makes 20's factor -2 while 40 leans left: the RL case.",
                    "Rotate 40 right (30 rises), then rotate 20 left. The root is 30, with 20 → (10, 25) and 40 → (None, 50).",
                    "The result is <strong>([10, 20, 25, 30, 40, 50], 30, 3)</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LLRB
    "implement-red-black-tree": {
        "example": {"setup": "t = RedBlackTree()\nfor k in range(1, 8):\n    t.insert(k)",
                    "call": "(t.inorder(), t.root.key)", "expect": "([1, 2, 3, 4, 5, 6, 7], 4)"},
        "approaches": {
            "LLRB: rotate and flip on the way up": {
                "idea": [
                    "A red link glues a node to its parent, forming a 3-node of a 2-3 tree. All leaves of a 2-3 tree are at the same depth, which is what keeps it balanced.",
                    "Left-leaning: red links may only lean left, which cuts the number of cases.",
                    "After a normal insert (the new node is red), three local fixes run on the way up: rotate a right-leaning red link left; rotate two left reds in a row right; flip colours when both children are red (splitting a 4-node).",
                ],
                "steps": [
                    "Insert: recurse, then <code>fix_up</code>; make the root black.",
                    "Delete: on the way down, borrow with <code>move_red_left</code> or <code>move_red_right</code> so the key is never in a 2-node; remove it; <code>fix_up</code> on the way back.",
                ],
                "why": [
                    "Height ≤ 2 log<sub>2</sub> n, with O(1) work per level: O(log n) per operation.",
                ],
                "dry": [
                    "Insert 1, 2: 2 is a red right child, so rotate left; 2 becomes the root. 3: both children of 2 are red, so flip.",
                    "4 is rotated under 3; 5 makes a 4-node at 4, whose flip pushes 4 up as a red right child of 2, so rotate left: 4 is the root.",
                    "6 and 7 repeat that pattern on the right. The result is <strong>([1, 2, 3, 4, 5, 6, 7], 4)</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ treap
    "implement-treap": {
        "example": {"setup": "t = Treap(seed=1)\nfor k in [5, 2, 8, 1, 9]:\n    t.insert(k)\nt.delete(2)",
                    "call": "(t.inorder(), 2 in t, 8 in t)", "expect": "([1, 5, 8, 9], False, True)"},
        "approaches": {
            "Recursive treap with rotations": {
                "idea": [
                    "A treap is a BST on the keys <em>and</em> a min-heap on random priorities given at insertion.",
                    "The resulting shape equals a BST built by inserting the keys in random order, which has expected height O(log n), whatever order the keys arrived in.",
                    "Insert: add a leaf as usual; on the way up, rotate a child above its parent if the child's priority is smaller.",
                    "Delete: rotate the node down, lifting the child with the smaller priority each time, until it has at most one child; then cut it out.",
                ],
                "steps": [
                    "Only two rotation cases, with no stored heights or colours.",
                ],
                "why": [
                    "The bounds are expected values over the random priorities: O(log n) per operation. A fixed seed makes the tests reproducible.",
                ],
                "dry": [
                    "Insert 5, 2, 8, 1 and 9 with seeded priorities; rotations keep the heap order, and 5 ends up at the root.",
                    "delete(2): find it and rotate it down until it can be removed.",
                    "The inorder is [1, 5, 8, 9]; 2 is gone and 8 is present. The result is <strong>([1, 5, 8, 9], False, True)</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ n-ary depth
    "max-depth-n-ary": {
        "example": {"call": f"max_depth({_NARY})", "expect": "3"},
        "approaches": {
            "Recursive over children": {
                "idea": [
                    "Depth = 1 + the deepest child's depth. <code>default=0</code> makes a leaf come out as 1.",
                ],
                "steps": [
                    "<code>1 + max((depth(c) for c in children), default=0)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    _NARY_SHAPE,
                    "depth(5) = depth(6) = 1, depth(3) = 2, depth(2) = depth(4) = 1.",
                    "depth(1) = 1 + 2 = <strong>3</strong>.",
                ],
            },
            "BFS counting levels": {
                "idea": [
                    "Replace each level with all of its children until nothing is left, and count the rounds.",
                ],
                "steps": [
                    "<code>level = [c for node in level for c in node.children]</code>.",
                ],
                "why": [
                    "It is O(n) time and O(w) space.",
                ],
                "dry": [
                    "[1] → [3, 2, 4] → [5, 6] → [].",
                    "That is <strong>3</strong> rounds.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ n-ary preorder
    "n-ary-preorder": {
        "example": {"call": f"preorder({_NARY})", "expect": "[1, 3, 5, 6, 2, 4]"},
        "approaches": {
            "Iterative, push children reversed": {
                "idea": [
                    "Pop a node and record it, then push its children <em>last to first</em>, so the first child is popped next.",
                ],
                "steps": [
                    "<code>stack.extend(reversed(node.children))</code>.",
                ],
                "why": [
                    "It is O(n). The stack can hold many pending siblings (O(n) for a wide root).",
                ],
                "dry": [
                    _NARY_SHAPE,
                    "Pop 1 → push 4, 2, 3. Pop 3 → push 6, 5. Pop 5, 6, 2, 4.",
                    "The result is <strong>[1, 3, 5, 6, 2, 4]</strong>.",
                ],
            },
            "Recursive": {
                "idea": [
                    "Record the node, then walk each child in order.",
                ],
                "steps": [
                    "<code>out.append(val)</code>; <code>for c in children: walk(c)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "1, then 3's subtree (3, 5, 6), then 2, then 4.",
                    "The result is <strong>[1, 3, 5, 6, 2, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ n-ary postorder
    "n-ary-postorder": {
        "example": {"call": f"postorder({_NARY})", "expect": "[5, 6, 3, 2, 4, 1]"},
        "approaches": {
            "Reversed root-right-to-left preorder": {
                "idea": [
                    "Push the children in natural order, so the last child pops first. That produces node, then children right to left.",
                    "Reversing the whole list gives children left to right, then the node: postorder.",
                ],
                "steps": [
                    "Collect, then return <code>out[::-1]</code>.",
                ],
                "why": [
                    "It is O(n) and simple, but it cannot stream values as it goes.",
                ],
                "dry": [
                    "The pop order is 1, 4, 2, 3, 6, 5.",
                    "Reversed: <strong>[5, 6, 3, 2, 4, 1]</strong>.",
                ],
            },
            "Recursive": {
                "idea": [
                    "Walk all the children first, then record the node.",
                ],
                "steps": [
                    "<code>for c in children: walk(c)</code>; <code>out.append(val)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "5, 6, then 3; then 2, 4; then 1.",
                    "The result is <strong>[5, 6, 3, 2, 4, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ n-ary level order
    "n-ary-level-order": {
        "example": {"call": f"level_order_nary({_NARY})", "expect": "[[1], [3, 2, 4], [5, 6]]"},
        "approaches": {
            "Level lists": {
                "idea": [
                    "Keep the current level as a list; the next level is every child of every node in it, in order.",
                ],
                "steps": [
                    "Append the values, then replace the level with the children.",
                ],
                "why": [
                    "Each node is in exactly one level: O(n).",
                ],
                "dry": [
                    _NARY_SHAPE,
                    "[1] → [3, 2, 4] → [5, 6].",
                    "The result is <strong>[[1], [3, 2, 4], [5, 6]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ next right pointers
    "next-right-pointers": {
        "example": {"setup": "t = build([1, 2, 3, 4, 5, 6, 7])\nconnect(t)",
                    "call": "(find_node(t, 2).next.val, find_node(t, 5).next.val, find_node(t, 7).next)", "expect": "(3, 6, None)"},
        "approaches": {
            "Use the level above as a linked list": {
                "idea": [
                    "Once a level's <code>next</code> pointers exist, you can walk that level like a linked list, without a queue.",
                    "For each node on it, link its left child to its right child, and its right child to the <em>next node's</em> left child, which crosses the gap between parents.",
                ],
                "steps": [
                    "<code>leftmost</code> walks down the left edge; the inner loop walks each level through <code>next</code>.",
                ],
                "why": [
                    "The links built on one level are the traversal structure for the next: O(n) time and O(1) space.",
                ],
                "dry": [
                    "Level 1: 2.next = 3.",
                    "Level 2, walking 2 → 3: 4 → 5, then 5 → 6 (across to 3's left child), 6 → 7. 7.next stays None.",
                    "The result is <strong>(3, 6, None)</strong>.",
                ],
            },
            "BFS, link within each level": {
                "idea": [
                    "Build each level as a list and link each node to the one after it.",
                ],
                "steps": [
                    "<code>for a, b in zip(level, level[1:]): a.next = b</code>.",
                ],
                "why": [
                    "It works on any tree, but holds a whole level: O(w).",
                ],
                "dry": [
                    "[2, 3] gives 2 → 3; [4, 5, 6, 7] gives 4 → 5 → 6 → 7.",
                    "The result is <strong>(3, 6, None)</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ next right pointers II
    "next-right-pointers-ii": {
        "example": {"setup": "t = build([1, 2, 3, 4, 5, None, 7])\nconnect(t)",
                    "call": "(find_node(t, 4).next.val, find_node(t, 5).next.val, find_node(t, 7).next)", "expect": "(5, 7, None)"},
        "approaches": {
            "Dummy head for the level below": {
                "idea": [
                    "Walk the current level through <code>next</code>, and build the level below as a linked list as you go.",
                    "A dummy node and a <code>tail</code> pointer collect the children in order; this handles missing children, which the perfect-tree trick cannot.",
                    "When the level ends, <code>dummy.next</code> is the first node of the level below.",
                ],
                "steps": [
                    "Append each child with <code>tail.next = child</code>; move to <code>dummy.next</code>.",
                ],
                "why": [
                    "The dummy removes the \"first node of the level\" special case. O(n) time and O(1) space.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), 2 → (4, 5), 3 → (None, 7).",
                    "Walking 2 → 3: append 4, 5 (from 2), then 7 (from 3, skipping its missing left child).",
                    "4 → 5 → 7. The result is <strong>(5, 7, None)</strong>.",
                ],
            },
        },
    },
}
