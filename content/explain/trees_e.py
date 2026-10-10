"""Write-ups for Trees, part E: BST basics, validation, inorder tricks, ranges, construction, conversion."""

EXPLAIN = {
    # ------------------------------------------------------------------ search in a BST
    "search-bst": {
        "examples": [
            {"setup": "t = build([4, 2, 7, 1, 3])", "call": "level_order(search_bst(t, 2))", "expect": "[2, 1, 3]"},
            {"call": "search_bst(build([4, 2, 7, 1, 3]), 5)", "expect": "None"},
        ],
        "approaches": {
            "Iterative descent": {
                "idea": [
                    "In a BST everything in a node's left subtree is smaller than it and everything in its right subtree is larger.",
                    "Comparing the target with one node therefore rules out a whole subtree: there is only ever one direction worth taking.",
                    "Following that single path from the root either lands on the value or falls off the tree, which proves the value is absent.",
                ],
                "steps": [
                    "Start with <code>node = root</code>.",
                    "While <code>node</code> is not <code>None</code> and <code>node.val != val</code>, keep walking.",
                    "If <code>val &lt; node.val</code>, move to <code>node.left</code>; otherwise move to <code>node.right</code>.",
                    "The loop stops on a match or on <code>None</code>; return <code>node</code> either way.",
                ],
                "why": [
                    "Every node skipped is on the wrong side of some ancestor, so it cannot equal <code>val</code>: the search never discards the answer.",
                    "The walk visits one node per level, so time is <strong>O(h)</strong>: O(log n) for a balanced tree, O(n) for a chain.",
                    "Only the <code>node</code> pointer is stored, so space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "node = 4. 2 &lt; 4, so move left.",
                        "node = 2, which equals val, so the loop stops.",
                        "The returned node is the subtree 2 → (1, 3), whose level order is <strong>[2, 1, 3]</strong>.",
                    ],
                    [
                        "node = 4. 5 &gt; 4, so move right.",
                        "node = 7. 5 &lt; 7, so move left.",
                        "7 has no left child, so node becomes None and the loop stops.",
                        "Nothing matched: the result is <strong>None</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return the node instead of <code>True</code>/<code>False</code>?",
                     "The problem asks for the subtree rooted at the match. Returning the node gives both: it is truthy on a hit and <code>None</code> on a miss."],
                    ["What if the tree has duplicate values?",
                     "The walk stops at the first match on the path, which is the highest copy. That node's subtree contains any copies below it."],
                    ["Is this really O(log n)?",
                     "Only when the tree is balanced. A BST built from sorted input is a chain, and then the walk is O(n)."],
                ],
            },
            "Recursive": {
                "idea": [
                    "The same one-way decision, written as a call on the chosen child.",
                    "The base case covers both endings at once: an empty subtree means the value is absent, and a matching root means it is found.",
                ],
                "steps": [
                    "If <code>root</code> is <code>None</code> or <code>root.val == val</code>, return <code>root</code>.",
                    "Otherwise pick <code>root.left</code> when <code>val &lt; root.val</code>, else <code>root.right</code>.",
                    "Return whatever the recursive call on that child returns.",
                    "The answer is passed back up unchanged through every frame.",
                ],
                "why": [
                    "Each call either answers or moves one level down into the only subtree that can hold <code>val</code>, so the result is correct by induction on the height.",
                    "There is one call per level, so time is <strong>O(h)</strong>.",
                    "CPython does not eliminate tail calls, so each level keeps a frame alive: space is <strong>O(h)</strong>, unlike the O(1) loop.",
                ],
                "dry": [
                    [
                        "search_bst(4, 2): 4 ≠ 2 and 2 &lt; 4, so call on the left child.",
                        "search_bst(2, 2): a match, return this node.",
                        "The outer call passes it straight up: <strong>[2, 1, 3]</strong>.",
                    ],
                    [
                        "search_bst(4, 5): 5 &gt; 4, call on 7.",
                        "search_bst(7, 5): 5 &lt; 7, call on 7's left child, which is None.",
                        "search_bst(None, 5) returns None, and each frame returns it unchanged: <strong>None</strong>.",
                    ],
                ],
                "faq": [
                    ["Is this a tail call?",
                     "Yes, the recursive call is the last thing done, but Python does not optimise tail calls, so the stack still grows by one frame per level."],
                    ["Could a very deep tree crash it?",
                     "Yes. A chain deeper than about 1000 nodes hits Python's default recursion limit; the loop version has no such limit."],
                    ["Why check <code>root is None</code> before reading <code>root.val</code>?",
                     "The <code>or</code> short-circuits, so <code>root.val</code> is never touched when <code>root</code> is <code>None</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ floor / ceiling / min / max
    "bst-floor-ceiling": {
        "examples": [
            {"setup": "t = build([8, 4, 12, 2, 6, 10, 14])",
             "call": "(floor(t, 9), ceiling(t, 9), bst_min(t), bst_max(t))", "expect": "(8, 10, 2, 14)"},
            {"setup": "t = build([8, 4, 12, 2, 6, 10, 14])",
             "call": "(floor(t, 1), ceiling(t, 1), floor(t, 6), ceiling(t, 6))", "expect": "(None, 2, 6, 6)"},
        ],
        "approaches": {
            "Descend and remember the best candidate": {
                "idea": [
                    "The minimum is at the end of the left spine and the maximum at the end of the right spine: keep going left (or right) until you cannot.",
                    "For <code>floor(x)</code>, any node with <code>val ≤ x</code> is a candidate, but a bigger candidate can only be in its right subtree, so remember it and go right.",
                    "<code>ceiling(x)</code> is the mirror image: a node with <code>val ≥ x</code> is a candidate, and a smaller one can only be on its left.",
                ],
                "steps": [
                    "<code>bst_min</code>: follow <code>.left</code> while it exists and return that node's value (<code>None</code> for an empty tree). <code>bst_max</code> does the same with <code>.right</code>.",
                    "<code>floor</code>: start with <code>best = None</code> and walk down from the root.",
                    "If <code>root.val &gt; x</code>, the node is too big and so is its right subtree: go left.",
                    "Otherwise record <code>best = root.val</code> and go right to look for something larger but still ≤ x.",
                    "<code>ceiling</code> swaps the roles: values <code>&lt; x</code> send you right, values ≥ x become <code>best</code> and send you left.",
                    "When the walk falls off the tree, <code>best</code> is the answer.",
                ],
                "why": [
                    "Each step discards only a subtree that cannot beat the current <code>best</code>, so the true floor (or ceiling) is either already recorded or still below the walk.",
                    "Every candidate recorded later is larger (for floor) than the earlier ones, because it was found in a right subtree, so the last one is the best.",
                    "Each function walks one root-to-leaf path: <strong>O(h)</strong> time, and only <code>best</code> and the pointer are stored, so <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 8 → (4, 12), 4 → (2, 6), 12 → (10, 14).",
                        "floor(9): 8 ≤ 9 so best = 8, go right. 12 &gt; 9, go left. 10 &gt; 9, go left to None. floor = 8.",
                        "ceiling(9): 8 &lt; 9, go right. 12 ≥ 9 so best = 12, go left. 10 ≥ 9 so best = 10, go left to None. ceiling = 10.",
                        "bst_min: 8 → 4 → 2, no left child, so 2. bst_max: 8 → 12 → 14, so 14.",
                        "The result is <strong>(8, 10, 2, 14)</strong>.",
                    ],
                    [
                        "floor(1): 8, 4 and 2 are all &gt; 1, so the walk goes left three times and never records anything: None.",
                        "ceiling(1): 8, 4 and 2 are all ≥ 1, so best becomes 8, then 4, then 2: the ceiling is 2.",
                        "floor(6): 8 &gt; 6, go left. 4 ≤ 6, best = 4, go right. 6 ≤ 6, best = 6, go right to None.",
                        "ceiling(6): 8 ≥ 6, best = 8, go left. 4 &lt; 6, go right. 6 ≥ 6, best = 6, go left to None.",
                        "An exact match is both floor and ceiling: <strong>(None, 2, 6, 6)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not stop as soon as <code>root.val == x</code>?",
                     "You could, since nothing beats an exact match. The code keeps walking for simplicity; the result is the same and the cost is still O(h)."],
                    ["Why does floor go <em>right</em> after recording a candidate?",
                     "Everything to the left is smaller than the candidate, so it cannot be a better floor. Only the right subtree can hold a larger value that is still ≤ x."],
                    ["What do these return when nothing qualifies?",
                     "<code>best</code> starts as <code>None</code> and is never set, so floor below the minimum and ceiling above the maximum both return <code>None</code>."],
                    ["Where is this used in practice?",
                     "It is what <code>TreeMap.floorKey</code>/<code>ceilingKey</code> in Java and <code>lower_bound</code> on a C++ <code>std::set</code> do on a balanced tree."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ insert into a BST
    "insert-bst": {
        "examples": [
            {"call": "level_order(insert_into_bst(build([4, 2, 7, 1, 3]), 5))", "expect": "[4, 2, 7, 1, 3, 5]"},
            {"call": "level_order(insert_into_bst(None, 5))", "expect": "[5]"},
        ],
        "approaches": {
            "Iterative: walk to the empty slot": {
                "idea": [
                    "Search for the value as if it were already there. The search ends at a missing child, and that empty slot is exactly where the value belongs.",
                    "Hanging the new node there moves no existing node, so the BST order is untouched.",
                ],
                "steps": [
                    "Create <code>new = TreeNode(val)</code>. If <code>root</code> is <code>None</code>, the new node is the whole tree: return it.",
                    "Walk from <code>node = root</code> in a <code>while True</code> loop.",
                    "If <code>val &lt; node.val</code>: when <code>node.left</code> is empty, attach <code>new</code> there and return <code>root</code>; otherwise step left.",
                    "Else (val ≥ node.val): do the same on the right side.",
                    "The original <code>root</code> is returned, since the top of the tree never changes.",
                ],
                "why": [
                    "At every ancestor the new value is on the same side as the walk took, so it satisfies every ordering constraint on its path and the BST stays valid.",
                    "The walk visits one node per level and stops at a leaf slot: <strong>O(h)</strong> time.",
                    "Only <code>node</code> and <code>new</code> are stored, so space is <strong>O(1)</strong>.",
                ],
                "dry": [
                    [
                        "The tree: 4 → (2, 7), 2 → (1, 3).",
                        "node = 4: 5 ≥ 4, and 4.right exists, so step to 7.",
                        "node = 7: 5 &lt; 7, and 7.left is None, so attach 5 there and return the root.",
                        "Level order: <strong>[4, 2, 7, 1, 3, 5]</strong>.",
                    ],
                    [
                        "root is None, so the early return fires.",
                        "The new node 5 is returned as the whole tree.",
                        "Level order: <strong>[5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the empty-tree case be handled separately?",
                     "There is no parent to attach to, so the loop has nothing to start from. Returning the new node lets the caller use it as the new root."],
                    ["Where do duplicates go?",
                     "The <code>else</code> branch takes <code>val ≥ node.val</code>, so an equal value is placed in the right subtree. LeetCode guarantees the value is new, so this never matters there."],
                    ["Is the resulting tree the only valid answer?",
                     "No. Any valid BST containing all values is accepted, but attaching at the leaf slot is the simplest and changes nothing else."],
                ],
            },
            "Recursive, re-linking on return": {
                "idea": [
                    "Insert into the correct subtree and assign the result back to that child pointer.",
                    "An empty subtree returns a brand-new node, and the parent's assignment is what links it in. Every other assignment just re-stores the same child.",
                ],
                "steps": [
                    "If <code>root</code> is <code>None</code>, return <code>TreeNode(val)</code>.",
                    "If <code>val &lt; root.val</code>, set <code>root.left = insert_into_bst(root.left, val)</code>.",
                    "Otherwise set <code>root.right = insert_into_bst(root.right, val)</code>.",
                    "Return <code>root</code>, so each parent re-links the same subtree it had before.",
                ],
                "why": [
                    "The recursion follows the same path as a search, so the new node lands in the same slot as the loop version and the order is preserved.",
                    "One call per level gives <strong>O(h)</strong> time.",
                    "The pending calls form a chain as long as the path, so space is <strong>O(h)</strong>.",
                ],
                "dry": [
                    [
                        "insert(4, 5): 5 ≥ 4, so 4.right = insert(7, 5).",
                        "insert(7, 5): 5 &lt; 7, so 7.left = insert(None, 5), which returns a new node 5.",
                        "7 is returned and stored back as 4.right; 4 is returned as the root.",
                        "Level order: <strong>[4, 2, 7, 1, 3, 5]</strong>.",
                    ],
                    [
                        "insert(None, 5) hits the base case immediately.",
                        "It returns TreeNode(5), which is the new root.",
                        "Level order: <strong>[5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why reassign <code>root.left</code> when it usually does not change?",
                     "Because the code cannot know in advance which call will create the node. Writing the same pointer back is harmless and keeps the code uniform."],
                    ["Why is this pattern worth learning if the loop is simpler?",
                     "The same \"return the new subtree root\" shape is what delete, trim and self-balancing trees (AVL, treaps) use, where the subtree root really can change."],
                    ["Does it handle the empty tree?",
                     "Yes, for free: the base case returns the new node, and there is no parent to assign it to."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ delete node in a BST
    "delete-bst": {
        "examples": [
            {"call": "vals_in(delete_node(build([5, 3, 6, 2, 4, None, 7]), 3))", "expect": "[2, 4, 5, 6, 7]"},
            {"call": "vals_in(delete_node(build([5, 3, 6, 2, 4, None, 7]), 6))", "expect": "[2, 3, 4, 5, 7]"},
        ],
        "approaches": {
            "Recursive, replace with the successor": {
                "idea": [
                    "Find the node, then remove it in one of three ways: a leaf disappears, a node with one child is replaced by that child.",
                    "A node with two children cannot simply vanish. Copy in the value of its <strong>inorder successor</strong> (the smallest value in its right subtree) and delete that successor instead.",
                    "The successor has no left child, so deleting it is always one of the easy cases.",
                ],
                "steps": [
                    "If <code>root</code> is <code>None</code>, the key is absent: return <code>None</code>.",
                    "If <code>key &lt; root.val</code>, recurse left and store the result in <code>root.left</code>; if larger, do the same on the right.",
                    "On a match with no left child, return <code>root.right</code> (this also covers a leaf, returning <code>None</code>). With no right child, return <code>root.left</code>.",
                    "Otherwise walk <code>succ</code> from <code>root.right</code> down its left spine to the minimum.",
                    "Copy <code>root.val = succ.val</code>, then delete <code>succ.val</code> from <code>root.right</code>.",
                    "Return <code>root</code> so the parent re-links it.",
                ],
                "why": [
                    "The successor is larger than everything on the left and smaller than everything else on the right, so putting its value at <code>root</code> keeps the BST order.",
                    "Locating the key is one path down, finding the successor continues down, and its deletion follows the same path: <strong>O(h)</strong> time overall.",
                    "The recursion depth is at most the height, so space is <strong>O(h)</strong>.",
                ],
                "dry": [
                    [
                        "The tree: 5 → (3, 6), 3 → (2, 4), 6 → (None, 7). key = 3 &lt; 5, so recurse left.",
                        "Match at 3 with two children. succ starts at 4, which has no left child, so the successor is 4.",
                        "Copy 4 into the node, then delete 4 from its right subtree: the leaf 4 returns None.",
                        "The node now holds 4 with left child 2. Inorder: <strong>[2, 4, 5, 6, 7]</strong>.",
                    ],
                    [
                        "key = 6 &gt; 5, so recurse right.",
                        "Match at 6. Its left child is None, so return its right child 7.",
                        "5.right is re-linked to 7, skipping 6.",
                        "Inorder: <strong>[2, 3, 4, 5, 7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why copy the value instead of moving the successor node?",
                     "Copying avoids rewiring the successor's parent and children. The second recursive call removes the old copy, which has at most a right child."],
                    ["Can the second delete find two-children again and loop?",
                     "No. The successor is the leftmost node of the right subtree, so it has no left child and hits an easy case."],
                    ["What if the key is not in the tree?",
                     "The search reaches <code>None</code>, returns it to the parent, and every frame re-links the same children: the tree is unchanged."],
                ],
            },
            "Recursive, replace with the predecessor": {
                "idea": [
                    "The mirror of the successor version: for a node with two children, borrow the value of its <strong>inorder predecessor</strong>, the largest value in its left subtree.",
                    "The predecessor has no right child, so removing it from the left subtree is always an easy case.",
                ],
                "steps": [
                    "Search for the key exactly as before, re-linking <code>root.left</code> or <code>root.right</code> on the way back.",
                    "On a match with a missing child, return the other child.",
                    "With two children, walk <code>pred</code> from <code>root.left</code> down its right spine to the maximum.",
                    "Copy <code>root.val = pred.val</code> and delete <code>pred.val</code> from <code>root.left</code>.",
                    "Return <code>root</code>.",
                ],
                "why": [
                    "The predecessor is larger than everything else on the left and smaller than everything on the right, so it can stand in for the deleted value.",
                    "All the work is on one or two downward paths: <strong>O(h)</strong> time.",
                    "The recursion stack is at most the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "key = 3 &lt; 5, so recurse left to 3, which has two children.",
                        "pred starts at 2, which has no right child, so the predecessor is 2.",
                        "Copy 2 into the node, then delete the leaf 2 from the left subtree.",
                        "The node now holds 2 with right child 4. Inorder: <strong>[2, 4, 5, 6, 7]</strong>.",
                    ],
                    [
                        "key = 6 &gt; 5, so recurse right.",
                        "Match at 6 with no left child: return 7.",
                        "5.right becomes 7. Inorder: <strong>[2, 3, 4, 5, 7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Do the two versions give the same tree?",
                     "Not in general. Deleting 3 here gives level order [5, 4, 6, 2, None, None, 7] with the successor and [5, 2, 6, None, 4, None, 7] with the predecessor. Both are valid BSTs with the same values."],
                    ["Is one better than the other?",
                     "Not asymptotically. Some implementations alternate between them to avoid always shrinking one side, which helps keep a random tree balanced."],
                    ["Why <code>pred.right</code> in the loop and not <code>pred.left</code>?",
                     "The largest value in a subtree is at the end of its right spine, just as the smallest is at the end of the left spine."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ validate BST
    "validate-bst": {
        "examples": [
            {"call": "is_valid_bst(build([5, 4, 6, None, None, 3, 7]))", "expect": "False"},
            {"call": "is_valid_bst(build([2, 1, 3]))", "expect": "True"},
        ],
        "approaches": {
            "Pass down the allowed range": {
                "idea": [
                    "Checking each node against its own children is not enough: a node must be smaller than <em>every</em> ancestor it sits left of and larger than every ancestor it sits right of.",
                    "Those constraints collapse into one open interval <code>(lo, hi)</code> per node, set by the nearest ancestors on each side.",
                    "Going left tightens the upper bound to the parent's value; going right tightens the lower bound.",
                ],
                "steps": [
                    "Define <code>ok(node, lo, hi)</code>; an empty subtree is valid.",
                    "If <code>not lo &lt; node.val &lt; hi</code>, return <code>False</code>.",
                    "Check the left subtree with <code>(lo, node.val)</code> and the right subtree with <code>(node.val, hi)</code>.",
                    "Start with <code>ok(root, -inf, inf)</code>.",
                ],
                "why": [
                    "The interval for a node is exactly the set of values allowed by all its ancestors, so every BST rule is checked, and nothing more.",
                    "The comparisons are strict, so equal values anywhere in the tree are rejected.",
                    "Each node is checked once: <strong>O(n)</strong> time. The recursion depth is the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 5 → (4, 6), 6 → (3, 7).",
                        "ok(5, −inf, inf) passes. ok(4, −inf, 5) passes and both its children are empty.",
                        "ok(6, 5, inf) passes, so check its left child with ok(3, 5, 6).",
                        "3 is not greater than 5: 3 sits in 5's right subtree but is smaller. The answer is <strong>False</strong>.",
                    ],
                    [
                        "ok(2, −inf, inf) passes.",
                        "ok(1, −inf, 2) passes; ok(3, 2, inf) passes.",
                        "All children are empty: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is comparing a node with its children not enough?",
                     "In example 1 every parent–child pair is ordered correctly (3 &lt; 6 is fine locally), yet 3 is in 5's right subtree. A child-only check returns True there; the range check catches it."],
                    ["Why use infinities instead of the integer limits?",
                     "Values can equal −2<sup>31</sup> or 2<sup>31</sup> − 1. With strict comparisons against those limits a valid tree like [-2147483648, None, 2147483647] would be rejected; infinities avoid that."],
                    ["Why strict <code>&lt;</code> on both sides?",
                     "LeetCode's definition forbids duplicates, so [2, 2, 2] must be False. Using <code>&lt;=</code> would accept it."],
                ],
            },
            "Inorder must be strictly increasing": {
                "idea": [
                    "A binary tree is a BST exactly when its inorder traversal is strictly increasing.",
                    "So walk the tree in order and compare each value with the one before it; the first value that does not rise proves it invalid.",
                ],
                "steps": [
                    "Keep an explicit <code>stack</code>, the current <code>node</code>, and the previous value <code>prev</code>.",
                    "Push <code>node</code> and move left until <code>node</code> is <code>None</code>.",
                    "Pop the top: it is the next node in inorder.",
                    "If <code>prev</code> is set and <code>node.val &lt;= prev</code>, return <code>False</code>.",
                    "Set <code>prev = node.val</code>, move to <code>node.right</code>, and repeat while the stack or <code>node</code> is non-empty.",
                    "If the traversal finishes, return <code>True</code>.",
                ],
                "why": [
                    "Inorder lists left subtree, node, right subtree. It is sorted exactly when every left value is below the node and every right value above it at every level, which is the BST definition.",
                    "It can stop at the first bad pair, and each node is pushed and popped at most once: <strong>O(n)</strong> time.",
                    "The stack holds one root-to-node path: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Push 5, 4. Pop 4: prev = 4. 4 has no right child.",
                        "Pop 5: 5 &gt; 4, prev = 5. Move to 6.",
                        "Push 6, 3. Pop 3: 3 ≤ prev = 5.",
                        "The inorder sequence goes 4, 5, 3, which does not increase: <strong>False</strong>.",
                    ],
                    [
                        "Push 2, 1. Pop 1: prev = 1.",
                        "Pop 2: 2 &gt; 1, prev = 2. Move to 3.",
                        "Push 3, pop 3: 3 &gt; 2, prev = 3.",
                        "Stack empty and node None: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store <code>prev</code> as a value and start it at <code>None</code>?",
                     "<code>None</code> means \"nothing seen yet\", so no sentinel is needed. A sentinel like −inf would also work, but an integer sentinel such as −2<sup>31</sup> would break on a node with exactly that value."],
                    ["Why <code>&lt;=</code> and not <code>&lt;</code> in the check?",
                     "An equal neighbour is a duplicate, which is invalid. <code>node.val &lt;= prev</code> rejects both decreases and repeats."],
                    ["Why iterative instead of a recursive inorder?",
                     "The iterative form can return <code>False</code> the moment it finds a bad pair without unwinding flags through recursion, and it avoids the recursion limit on deep trees."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ verify preorder sequence
    "verify-preorder-bst": {
        "examples": [
            {"call": "verify_preorder([5, 2, 6, 1, 3])", "expect": "False"},
            {"call": "verify_preorder([5, 2, 1, 3, 6])", "expect": "True"},
        ],
        "approaches": {
            "Monotonic stack with a lower bound": {
                "idea": [
                    "Preorder goes down left subtrees first. While values keep falling you are going left; the first value larger than the top means you turned into some node's right subtree.",
                    "Once you turn right at an ancestor, every later value must be larger than that ancestor. That ancestor's value becomes a <strong>lower bound</strong> <code>low</code>.",
                    "A decreasing stack holds the left path still waiting for its right subtree; popping finds which ancestor you turned right at.",
                ],
                "steps": [
                    "Start with <code>low = -inf</code> and an empty <code>stack</code>.",
                    "For each value <code>v</code>: if <code>v &lt; low</code>, it belongs left of an ancestor whose right subtree has already started, so return <code>False</code>.",
                    "While the stack top is smaller than <code>v</code>, pop it into <code>low</code>: <code>v</code> lies in that node's right subtree.",
                    "Push <code>v</code>.",
                    "If the loop finishes, return <code>True</code>.",
                ],
                "why": [
                    "The last popped value is the parent whose right subtree <code>v</code> starts; all remaining values must exceed it, and <code>low</code> only ever increases, so it records the tightest such bound.",
                    "Values left on the stack are decreasing, which is exactly a chain of left children, so the stack models the open path of the tree.",
                    "Each value is pushed once and popped at most once: <strong>O(n)</strong> time. The stack can hold all values for a left chain: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "v=5: push, stack [5]. v=2: 2 &lt; 5, push, stack [5, 2].",
                        "v=6: pop 2, then pop 5 (both smaller), low = 5. Push 6: stack [6].",
                        "6 is in 5's right subtree, so every later value must exceed 5.",
                        "v=1: 1 &lt; low = 5, so it returns <strong>False</strong>.",
                    ],
                    [
                        "v=5, 2, 1: each smaller than the top, stack [5, 2, 1], low = −inf.",
                        "v=3: pop 1, pop 2, low = 2. Push 3: stack [5, 3].",
                        "v=6: pop 3, pop 5, low = 5. Push 6: stack [6].",
                        "No value fell below its bound: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the bound the <em>last</em> popped value?",
                     "Pops happen in increasing order, and the last one is the ancestor whose right subtree <code>v</code> starts. Everything after <code>v</code> in preorder is in that right subtree or further right, so all of it must exceed that ancestor."],
                    ["Can <code>low</code> ever decrease?",
                     "No. Every pop takes a value smaller than the current <code>v</code>, and <code>v</code> itself was ≥ <code>low</code>, so new bounds keep growing."],
                    ["What about duplicates?",
                     "The problem says values are distinct. With the <code>&lt;</code> comparisons as written, an equal value is neither popped nor rejected, so duplicates are not handled specially."],
                ],
            },
            "Same idea, reusing the input as the stack": {
                "idea": [
                    "The stack never holds more values than have been read so far, so the already-read prefix of <code>preorder</code> can store it.",
                    "<code>top</code> is the index of the stack's top inside the array, with <code>-1</code> meaning empty.",
                ],
                "steps": [
                    "Start with <code>low = -inf</code> and <code>top = -1</code>.",
                    "For each <code>v</code>: if <code>v &lt; low</code>, return <code>False</code>.",
                    "While <code>top &gt;= 0</code> and <code>preorder[top] &lt; v</code>, set <code>low = preorder[top]</code> and decrement <code>top</code> (a pop).",
                    "Increment <code>top</code> and write <code>preorder[top] = v</code> (a push).",
                    "Return <code>True</code> if every value passes.",
                ],
                "why": [
                    "It performs exactly the same pushes, pops and checks as the stack version, so it gives the same answer.",
                    "<code>top</code> is always less than the current loop index, so writing at <code>top</code> never overwrites a value that has not been read yet.",
                    "Time is still <strong>O(n)</strong>; extra space drops to <strong>O(1)</strong> because the input array is reused.",
                ],
                "dry": [
                    [
                        "v=5: top = 0, array [5, 2, 6, 1, 3]. v=2: top = 1, array unchanged.",
                        "v=6: pop index 1 (2) and index 0 (5), low = 5. Push at index 0: array [6, 2, 6, 1, 3].",
                        "v=1: 1 &lt; low = 5.",
                        "It returns <strong>False</strong>.",
                    ],
                    [
                        "v=5, 2, 1: pushed at indices 0, 1, 2, top = 2.",
                        "v=3: pops 1 and 2, low = 2, writes 3 at index 1: array [5, 3, 1, 3, 6].",
                        "v=6: pops 3 and 5, low = 5, writes 6 at index 0: array [6, 3, 1, 3, 6].",
                        "Every check passed: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Does this damage the caller's list?",
                     "Yes. After verifying [5, 2, 1, 3, 6] the list reads [6, 3, 1, 3, 6]. Pass a copy if the caller still needs it, which costs O(n) space again."],
                    ["Why is overwriting safe while still iterating over the same list?",
                     "The for-loop has already read every index ≤ the current one, and <code>top</code> never exceeds the current index, so only consumed slots are overwritten."],
                    ["Is this worth it in an interview?",
                     "Mention it as the follow-up answer to \"can you do it in constant space?\". The stack version is clearer and should come first."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth largest in a BST
    "kth-largest-bst": {
        "examples": [
            {"call": "kth_largest(build([5, 3, 6, 2, 4, None, None, 1]), 2)", "expect": "5"},
            {"call": "kth_largest(build([5, 3, 6, 2, 4, None, None, 1]), 4)", "expect": "3"},
        ],
        "approaches": {
            "Reverse inorder, stop at k": {
                "idea": [
                    "Inorder (left, node, right) lists a BST in increasing order, so the mirror order (right, node, left) lists it in <strong>decreasing</strong> order.",
                    "The k-th value produced by that reverse walk is the k-th largest, and the walk can stop right there.",
                ],
                "steps": [
                    "Keep a <code>stack</code> and start with <code>node = root</code>.",
                    "Push <code>node</code> and move to <code>node.right</code> until it is <code>None</code>: the stack top is now the largest unvisited value.",
                    "Pop it and decrement <code>k</code>.",
                    "If <code>k == 0</code>, return its value.",
                    "Otherwise move to <code>node.left</code>, the values just below it, and repeat.",
                ],
                "why": [
                    "Each pop yields the next smaller value, exactly like an iterative inorder with left and right swapped, so the k-th pop is the k-th largest.",
                    "Reaching the largest value costs one path of length h, and each further answer costs amortised O(1): <strong>O(h + k)</strong> time.",
                    "The stack holds one path: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 5 → (3, 6), 3 → (2, 4), 2 → (1). Push 5, 6: stack [5, 6].",
                        "Pop 6, k = 1. 6 has no left child.",
                        "Pop 5, k = 0.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "Push 5, 6. Pop 6, k = 3. Pop 5, k = 2.",
                        "Move to 5.left = 3: push 3, 4. Stack [3, 4].",
                        "Pop 4, k = 1. 4 has no left child.",
                        "Pop 3, k = 0: it returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why decrement <code>k</code> instead of collecting values in a list?",
                     "Collecting would need the whole traversal and O(n) memory. Counting down lets the walk stop after k values."],
                    ["What happens if k is larger than the number of nodes?",
                     "The stack empties and <code>stack.pop()</code> raises IndexError. The problem guarantees 1 ≤ k ≤ n, so the code does not guard against it."],
                    ["How would I answer many queries quickly?",
                     "Store each node's subtree size. Then each query walks one path, choosing the side by comparing k with the right subtree's size: O(h) per query."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum absolute difference
    "min-abs-diff-bst": {
        "examples": [
            {"call": "get_minimum_difference(build([1, 0, 48, None, None, 12, 49]))", "expect": "1"},
            {"call": "get_minimum_difference(build([236, 104, 701, None, 227, None, 911]))", "expect": "9"},
        ],
        "approaches": {
            "Inorder, compare with the previous value": {
                "idea": [
                    "In a sorted list the closest pair is always two neighbours: a value further away can only be further apart.",
                    "An inorder walk of a BST produces the values in sorted order, so only consecutive inorder values need comparing.",
                ],
                "steps": [
                    "Keep <code>best = inf</code> and <code>prev = None</code> in the enclosing scope (<code>nonlocal</code>).",
                    "Recurse into <code>node.left</code> first.",
                    "At the node: if <code>prev</code> is set, update <code>best = min(best, node.val - prev)</code>.",
                    "Set <code>prev = node.val</code>, then recurse into <code>node.right</code>.",
                    "Return <code>best</code> after the walk.",
                ],
                "why": [
                    "For sorted a &lt; b &lt; c, c − a is bigger than both b − a and c − b, so any non-adjacent pair is beaten by an adjacent one and checking neighbours is enough.",
                    "Inorder values are increasing, so <code>node.val - prev</code> is already the absolute difference.",
                    "Each node is visited once: <strong>O(n)</strong> time. The recursion depth is the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (0, 48), 48 → (12, 49). Inorder: 0, 1, 12, 48, 49.",
                        "0: prev = 0. 1: diff 1, best = 1. 12: diff 11.",
                        "48: diff 36. 49: diff 1, best stays 1.",
                        "The answer is <strong>1</strong>.",
                    ],
                    [
                        "The tree: 236 → (104, 701), 104 → (None, 227), 701 → (None, 911). Inorder: 104, 227, 236, 701, 911.",
                        "227 − 104 = 123, best = 123. 236 − 227 = 9, best = 9.",
                        "701 − 236 = 465 and 911 − 701 = 210 do not improve it.",
                        "236 and 227 are not parent and child, yet they are inorder neighbours: <strong>9</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just compare each node with its children?",
                     "The closest pair need not be parent and child. In example 2 it is 236 and 227, the root and a grandchild, which only show up as neighbours in inorder."],
                    ["Why do <code>best</code> and <code>prev</code> need <code>nonlocal</code>?",
                     "The inner function assigns to them. Without <code>nonlocal</code>, Python would treat them as new local variables and raise UnboundLocalError on the first read."],
                    ["What does it return for a single node?",
                     "<code>inf</code>, since no pair exists. The problem guarantees at least two nodes."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find mode in a BST
    "find-mode-bst": {
        "examples": [
            {"call": "find_mode(build([5, 3, 7, 3, 5, 7, 7]))", "expect": "[7]"},
            {"call": "find_mode(build([2, 1, 3]))", "expect": "[1, 2, 3]"},
        ],
        "approaches": {
            "Inorder run lengths": {
                "idea": [
                    "This BST allows duplicates (left ≤ node ≤ right), so its inorder sequence is sorted and equal values come out <strong>consecutively</strong>.",
                    "Counting a value then only needs the length of its current run, not a dictionary.",
                    "Track the best run length so far and the values that achieved it.",
                ],
                "steps": [
                    "Keep <code>modes</code>, <code>best</code>, <code>run</code> and <code>prev</code> as <code>nonlocal</code> state.",
                    "Walk the left subtree first.",
                    "At the node: <code>run</code> becomes <code>run + 1</code> if <code>node.val == prev</code>, otherwise 1. Set <code>prev = node.val</code>.",
                    "If <code>run &gt; best</code>, set <code>best = run</code> and reset <code>modes = [node.val]</code>; if <code>run == best</code>, append the value.",
                    "Walk the right subtree, then return <code>modes</code>.",
                ],
                "why": [
                    "Equal values are adjacent in inorder, so <code>run</code> reaches each value's full count at its last copy, and that moment is compared with <code>best</code>.",
                    "A value can be appended early with a partial run, but any later longer run resets <code>modes</code>, so only full-count winners survive.",
                    "One visit per node: <strong>O(n)</strong> time. Apart from the output, only the recursion stack is used: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 5 → (3, 7), 3 → (3, 5), 7 → (7, 7). Inorder: 3, 3, 5, 5, 7, 7, 7.",
                        "3: run 1 &gt; 0, best = 1, modes [3]. 3: run 2, best = 2, modes [3].",
                        "5: run 1. 5: run 2 == best, modes [3, 5].",
                        "7: run 1. 7: run 2, modes [3, 5, 7]. 7: run 3 &gt; 2, best = 3, modes reset to [7].",
                        "The answer is <strong>[7]</strong>.",
                    ],
                    [
                        "Inorder: 1, 2, 3, all distinct.",
                        "1: run 1 &gt; 0, best = 1, modes [1].",
                        "2: run 1 == best, modes [1, 2]. 3: run 1 == best, modes [1, 2, 3].",
                        "Every value ties: <strong>[1, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can 5 be appended in example 1 and then disappear?",
                     "When 5 reached run 2 it tied the best so far. The third 7 then made a longer run, which replaced the whole list, so the early entry is harmless."],
                    ["Why is <code>modes</code> in the <code>nonlocal</code> list?",
                     "The line <code>modes = [node.val]</code> rebinds the name, so Python needs <code>nonlocal</code>. Appending alone would not need it."],
                    ["Is the output sorted?",
                     "Yes, as a side effect: values are appended in inorder, which is increasing."],
                ],
            },
            "Counter": {
                "idea": [
                    "Ignore the BST structure: collect all values and count them with a <code>Counter</code>.",
                    "Every value whose count equals the maximum count is a mode.",
                ],
                "steps": [
                    "Build <code>counts = Counter(vals_in(root))</code>.",
                    "Find <code>top = max(counts.values())</code>.",
                    "Keep every value <code>v</code> with <code>c == top</code>.",
                    "Return them sorted.",
                    "This works on any binary tree, sorted or not.",
                ],
                "why": [
                    "The counter holds the exact frequency of every value, so selecting those equal to the maximum is the definition of the mode.",
                    "Counting is linear and the final sort is over the modes only: <strong>O(n)</strong> time as listed, though <code>vals_in</code>'s list concatenation can cost more on a deep tree.",
                    "The list of values and the counter take <strong>O(n)</strong> space, which is what the run-length version avoids.",
                ],
                "dry": [
                    [
                        "vals_in gives [3, 3, 5, 5, 7, 7, 7].",
                        "counts = {3: 2, 5: 2, 7: 3}, so top = 3.",
                        "Only 7 has count 3.",
                        "The answer is <strong>[7]</strong>.",
                    ],
                    [
                        "vals_in gives [1, 2, 3].",
                        "counts = {1: 1, 2: 1, 3: 1}, top = 1.",
                        "All three values qualify: <strong>[1, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why sort the result?",
                     "Counter keeps insertion order, which happens to be sorted here, but sorting makes the output deterministic regardless of how the values were collected."],
                    ["When is this the better choice?",
                     "When the tree is not a BST, or when clarity matters more than memory. The follow-up \"without extra space\" is what forces the run-length version."],
                    ["Does the counter handle negative values?",
                     "Yes. It is a dictionary, so any hashable value works."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ increasing order search tree
    "increasing-order-search-tree": {
        "examples": [
            {"call": "level_order(increasing_bst(build([4, 2, 5, 1, 3])))", "expect": "[1, None, 2, None, 3, None, 4, None, 5]"},
            {"call": "level_order(increasing_bst(build([3, 2, None, 1])))", "expect": "[1, None, 2, None, 3]"},
        ],
        "approaches": {
            "Inorder, re-link onto a tail": {
                "idea": [
                    "The result is the inorder sequence laid out as a right-only chain.",
                    "Instead of building new nodes, visit nodes in inorder and append each one to the end of the chain: clear its left pointer and hang it off the previous node's right.",
                    "A dummy node gives the chain a fixed start, so the first node is not a special case.",
                ],
                "steps": [
                    "Create <code>dummy = tail = TreeNode(0)</code>.",
                    "Walk the tree in inorder with <code>walk(node)</code>, recursing left first.",
                    "At each node: set <code>node.left = None</code>, <code>tail.right = node</code>, then <code>tail = node</code>.",
                    "Recurse into <code>node.right</code> afterwards. The right pointer is read before the node is overwritten as the chain's tail.",
                    "Return <code>dummy.right</code>, the smallest node.",
                ],
                "why": [
                    "Nodes are attached in inorder, which is increasing order, so the chain is sorted.",
                    "Clearing <code>node.left</code> is safe because the left subtree has already been fully visited when the node is processed.",
                    "Overwriting <code>tail.right</code> is safe because <code>tail</code>'s own right subtree was finished before inorder reached the current node.",
                    "Every node is visited once: <strong>O(n)</strong> time; the recursion stack gives <strong>O(h)</strong> space, and no nodes are created besides the dummy.",
                ],
                "dry": [
                    [
                        "The tree: 4 → (2, 5), 2 → (1, 3). Inorder: 1, 2, 3, 4, 5.",
                        "1: dummy.right = 1, tail = 1. 2: left (1) cleared, 1.right = 2, tail = 2.",
                        "3: 2.right was 3 already; set again, tail = 3.",
                        "4: left cleared, 3.right = 4, tail = 4. 5: 4.right = 5, tail = 5.",
                        "The chain reads <strong>[1, None, 2, None, 3, None, 4, None, 5]</strong>.",
                    ],
                    [
                        "The tree is a left chain 3 → 2 → 1. Inorder: 1, 2, 3.",
                        "1: dummy.right = 1. 2: left cleared, 1.right = 2.",
                        "3: left cleared, 2.right = 3.",
                        "The left chain becomes a right chain: <strong>[1, None, 2, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is it safe to change <code>tail.right</code> when tail's right subtree might not be visited yet?",
                     "Inorder only reaches the current node after tail's whole right subtree is done (or tail has none), so the pointer being overwritten is no longer needed."],
                    ["Why the dummy node?",
                     "Without it the first node would need an <code>if head is None</code> branch. The dummy's <code>right</code> ends up pointing at the smallest node."],
                    ["Can it be done without recursion?",
                     "Yes, with an explicit inorder stack or with Morris traversal for O(1) extra space; the re-linking step stays the same."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ range sum of BST
    "range-sum-bst": {
        "examples": [
            {"call": "range_sum_bst(build([10, 5, 15, 3, 7, None, 18]), 7, 15)", "expect": "32"},
            {"call": "range_sum_bst(build([10, 5, 15, 3, 7, 13, 18, 1, None, 6]), 6, 10)", "expect": "23"},
        ],
        "approaches": {
            "DFS that prunes out-of-range subtrees": {
                "idea": [
                    "A plain DFS would add up every node in <code>[low, high]</code>, but the BST order lets it skip whole subtrees.",
                    "If a node is below <code>low</code>, its left subtree is even smaller and can be dropped; if it is above <code>high</code>, its right subtree can be dropped.",
                    "Only nodes inside the range need both children explored.",
                ],
                "steps": [
                    "Start with <code>total = 0</code> and <code>stack = [root]</code>.",
                    "Pop a node; skip it if it is <code>None</code>.",
                    "If <code>node.val &lt; low</code>, push only <code>node.right</code>.",
                    "If <code>node.val &gt; high</code>, push only <code>node.left</code>.",
                    "Otherwise add <code>node.val</code> to <code>total</code> and push both children.",
                    "When the stack is empty, return <code>total</code>.",
                ],
                "why": [
                    "Every pruned subtree lies entirely outside the range, so no in-range value is ever skipped, and in-range nodes are counted exactly once.",
                    "Out-of-range nodes that are visited lie along the boundary paths towards <code>low</code> and <code>high</code>, so the work is <strong>O(h + m)</strong> for m nodes in range (O(n) in the worst case).",
                    "The stack holds pending siblings along the current paths: <strong>O(h)</strong> space as listed.",
                ],
                "dry": [
                    [
                        "The tree: 10 → (5, 15), 5 → (3, 7), 15 → (None, 18). Range [7, 15].",
                        "Pop 10: in range, total = 10, push 5 and 15. Pop 15: in range, total = 25, push None and 18.",
                        "Pop 18: &gt; 15, push only its left (None). The Nones are skipped.",
                        "Pop 5: &lt; 7, push only 7. Node 3 is never visited. Pop 7: total = 32.",
                        "The answer is <strong>32</strong>.",
                    ],
                    [
                        "The tree: 10 → (5, 15), 5 → (3, 7), 15 → (13, 18), 3 → (1), 7 → (6). Range [6, 10].",
                        "Pop 10: total = 10, push 5 and 15. Pop 15: &gt; 10, push only 13. Pop 13: &gt; 10, push only its empty left.",
                        "Pop 5: &lt; 6, push only 7. Pop 7: total = 17, push 6 and None.",
                        "Pop 6: total = 23. Nodes 18, 3 and 1 were never visited.",
                        "The answer is <strong>23</strong>.",
                    ],
                ],
                "faq": [
                    ["Why push <code>None</code> children and skip them later?",
                     "It keeps the push lines short; the <code>if node is None: continue</code> at the top handles them in one place."],
                    ["Are <code>low</code> and <code>high</code> inclusive?",
                     "Yes. The conditions <code>node.val &lt; low</code> and <code>node.val &gt; high</code> leave values equal to either end in the counted branch."],
                    ["Would plain DFS without pruning also be correct?",
                     "Yes, just slower: it would visit all n nodes. Pruning is what uses the BST property."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ trim a BST
    "trim-bst": {
        "examples": [
            {"call": "level_order(trim_bst(build([3, 0, 4, None, 2, None, None, 1]), 1, 3))", "expect": "[3, 2, None, 1]"},
            {"call": "level_order(trim_bst(build([1, 0, 2]), 1, 2))", "expect": "[1, None, 2]"},
        ],
        "approaches": {
            "Recursive, return the trimmed subtree": {
                "idea": [
                    "Let <code>trim_bst</code> return the root of the trimmed version of a subtree; the parent stores it as its new child.",
                    "If a node is below <code>low</code>, it and its whole left subtree are too small, so the answer is the trimmed right subtree. Above <code>high</code> is the mirror case.",
                    "If the node is in range it stays, and both its children are trimmed recursively.",
                ],
                "steps": [
                    "Return <code>None</code> for an empty subtree.",
                    "If <code>root.val &lt; low</code>, return <code>trim_bst(root.right, low, high)</code>.",
                    "If <code>root.val &gt; high</code>, return <code>trim_bst(root.left, low, high)</code>.",
                    "Otherwise set <code>root.left</code> and <code>root.right</code> to their trimmed versions.",
                    "Return <code>root</code>.",
                ],
                "why": [
                    "Discarding a node with its whole left (or right) side only removes values that are out of range, by the BST order.",
                    "Kept nodes keep their relative positions, so the result is still a BST and contains exactly the in-range values.",
                    "Each node is handled at most once: <strong>O(n)</strong> time. The recursion depth is the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 3 → (0, 4), 0 → (None, 2), 2 → (1). Range [1, 3].",
                        "3 is in range: trim its left child 0. 0 &lt; 1, so return trim(2), dropping 0.",
                        "2 is in range; its left 1 is in range; both keep empty children. 3.left = 2.",
                        "Trim 3's right child 4: 4 &gt; 3, so return trim(4.left) = None. 3.right = None.",
                        "The result is <strong>[3, 2, None, 1]</strong>.",
                    ],
                    [
                        "1 is in range [1, 2]: trim both children.",
                        "Left 0 &lt; 1: return trim(0.right) = None.",
                        "Right 2 is in range and is kept.",
                        "The result is <strong>[1, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the root itself change?",
                     "If the root is out of range it is dropped and the call returns a node from one subtree. That is why the function returns the new root rather than modifying in place only."],
                    ["Why is it O(n) and not O(h)?",
                     "In-range nodes all have to be visited to trim their children, and there can be up to n of them."],
                    ["Why not check whether the child is out of range from the parent?",
                     "It would need more cases. Returning the trimmed subtree lets each call handle only itself, and the parent re-links whatever comes back."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ inorder successor in BST
    "inorder-successor-bst": {
        "examples": [
            {"setup": "t = build([5, 3, 6, 2, 4, None, None, 1])", "call": "inorder_successor(t, find_node(t, 4)).val", "expect": "5"},
            {"setup": "t = build([5, 3, 6, 2, 4, None, None, 1])", "call": "inorder_successor(t, find_node(t, 6))", "expect": "None"},
        ],
        "approaches": {
            "Descend from the root, remember the last left turn": {
                "idea": [
                    "The successor of p is the smallest value larger than <code>p.val</code>: a ceiling search with strict \"greater than\".",
                    "Walking down from the root, any node larger than p is a candidate, and a smaller candidate can only be in its left subtree.",
                    "Nodes that are ≤ p cannot be the answer, so go right past them.",
                ],
                "steps": [
                    "Start with <code>succ = None</code> and <code>node = root</code>.",
                    "If <code>node.val &gt; p.val</code>, record <code>succ = node</code> and go left.",
                    "Otherwise go right.",
                    "When <code>node</code> becomes <code>None</code>, return <code>succ</code>.",
                ],
                "why": [
                    "Each recorded candidate is smaller than the previous one (it was found in a left subtree), and every skipped region is either ≤ p or larger than the current candidate, so the last candidate is the smallest value above p.",
                    "The walk follows one path: <strong>O(h)</strong> time.",
                    "Only two pointers are stored: <strong>O(1)</strong> space, with no parent pointers needed.",
                ],
                "dry": [
                    [
                        "The tree: 5 → (3, 6), 3 → (2, 4), 2 → (1). p = 4.",
                        "5 &gt; 4: succ = 5, go left to 3.",
                        "3 ≤ 4: go right to 4. 4 ≤ 4: go right to None.",
                        "The last left turn was at 5: <strong>5</strong>.",
                    ],
                    [
                        "p = 6. 5 ≤ 6: go right to 6.",
                        "6 ≤ 6: go right to None.",
                        "No node was larger, so succ stays <strong>None</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does going right never update <code>succ</code>?",
                     "Going right happens at nodes ≤ p, which cannot come after p in inorder."],
                    ["Does it need p to be the actual node from the tree?",
                     "No, it only reads <code>p.val</code>. Passing a separate <code>TreeNode(4)</code> still returns the node 5."],
                    ["What about the classic two-case rule (leftmost of the right subtree, else an ancestor)?",
                     "That rule needs parent pointers for the ancestor case. Descending from the root finds the same node without them."],
                ],
            },
            "Inorder traversal, return the node after p": {
                "idea": [
                    "The successor is literally the node that comes right after p in inorder.",
                    "Walk the tree in order with a flag that turns on when p is visited; the next visited node is the answer.",
                ],
                "steps": [
                    "Run an iterative inorder with <code>stack</code> and <code>node</code>.",
                    "After popping a node, if <code>seen_p</code> is already true, return that node.",
                    "Otherwise set <code>seen_p = node is p</code>.",
                    "Move to <code>node.right</code> and continue.",
                    "If the traversal ends, p was last: return <code>None</code>.",
                ],
                "why": [
                    "Inorder visits nodes in sorted order, so the node after p is by definition its successor.",
                    "It ignores the BST shortcut and may walk most of the tree: <strong>O(n)</strong> time.",
                    "The stack holds one path: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Push 5, 3, 2, 1. Pop 1, then 2, then 3: none of them is p.",
                        "Move to 3.right = 4: push 4, pop 4. It is p, so seen_p = True.",
                        "Pop 5: seen_p is already True.",
                        "It returns the node <strong>5</strong>.",
                    ],
                    [
                        "The walk pops 1, 2, 3, 4, 5 without finding p.",
                        "Move to 6: push and pop it. seen_p = True.",
                        "6 has no right child and the stack is empty, so the loop ends.",
                        "p was the last node: <strong>None</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>node is p</code> rather than comparing values?",
                     "It matches the exact node object. A consequence: if you pass a copy such as <code>TreeNode(4)</code>, the flag never turns on and the result is <code>None</code>."],
                    ["Why check <code>seen_p</code> before updating it?",
                     "The order matters: the node being popped is first tested as \"the one after p\", and only then becomes the new candidate for p."],
                    ["Why learn this if the descent is faster?",
                     "It works on any binary tree, not just a BST, which is the variant some interviews ask."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sorted array to BST
    "sorted-array-to-bst": {
        "examples": [
            {"call": "level_order(sorted_array_to_bst([-10, -3, 0, 5, 9]))", "expect": "[0, -10, 5, None, -3, None, 9]"},
            {"call": "level_order(sorted_array_to_bst([1, 2, 3, 4]))", "expect": "[2, 1, 3, None, None, None, 4]"},
        ],
        "approaches": {
            "Middle as root, recurse on index ranges": {
                "idea": [
                    "For a height-balanced BST, the root should split the values into two halves of nearly equal size: pick the middle element.",
                    "Everything left of the middle forms the left subtree and everything right forms the right subtree, built the same way.",
                    "Passing index bounds instead of slicing avoids copying the array at each level.",
                ],
                "steps": [
                    "Define <code>make(lo, hi)</code> for the inclusive range <code>nums[lo..hi]</code>.",
                    "If <code>lo &gt; hi</code>, the range is empty: return <code>None</code>.",
                    "Take <code>mid = (lo + hi) // 2</code>.",
                    "Return <code>TreeNode(nums[mid], make(lo, mid - 1), make(mid + 1, hi))</code>.",
                    "Call <code>make(0, len(nums) - 1)</code>.",
                ],
                "why": [
                    "All values left of <code>mid</code> are smaller and all right are larger because the input is sorted, so the result is a BST.",
                    "The two halves differ in size by at most one at every node, so the subtree heights differ by at most one and the tree is height-balanced.",
                    "Each element becomes exactly one node: <strong>O(n)</strong> time. Halving the range each level makes the recursion depth <strong>O(log n)</strong>, which is the extra space.",
                ],
                "dry": [
                    [
                        "make(0, 4): mid = 2, root 0.",
                        "Left make(0, 1): mid = 0, node −10; its right make(1, 1) gives −3.",
                        "Right make(3, 4): mid = 3, node 5; its right make(4, 4) gives 9.",
                        "Level order: <strong>[0, -10, 5, None, -3, None, 9]</strong>.",
                    ],
                    [
                        "make(0, 3): mid = 1, root 2. Left make(0, 0) gives 1.",
                        "Right make(2, 3): mid = 2, node 3; its right make(3, 3) gives 4.",
                        "With an even count the lower middle is chosen, so the extra node goes to the right.",
                        "Level order: <strong>[2, 1, 3, None, None, None, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is the answer unique?",
                     "No. Using <code>(lo + hi + 1) // 2</code> picks the upper middle for even ranges and gives a different, equally balanced tree; LeetCode accepts either."],
                    ["Why not slice <code>nums[:mid]</code>?",
                     "Slices copy, adding O(n) work per level and O(n log n) in total. Index bounds keep it O(n)."],
                    ["Why is the space O(log n) and not O(n)?",
                     "The output tree is not counted; the only extra memory is the recursion stack, which is as deep as the balanced tree."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sorted list to BST
    "sorted-list-to-bst": {
        "examples": [
            {"call": "level_order(sorted_list_to_bst(build_list([1, 2, 3])))", "expect": "[2, 1, 3]"},
            {"call": "level_order(sorted_list_to_bst(build_list([1, 2, 3, 4, 5, 6, 7])))", "expect": "[4, 2, 6, 1, 3, 5, 7]"},
        ],
        "approaches": {
            "Inorder simulation": {
                "idea": [
                    "A linked list cannot jump to its middle, but it can be read in order, and inorder is exactly the order in which a BST's nodes are visited.",
                    "So decide the tree's <em>shape</em> by index ranges, and fill in values as the inorder construction reaches each node, consuming the list one node at a time.",
                ],
                "steps": [
                    "Count the list length <code>n</code>, and set <code>cur = head</code>.",
                    "<code>make(lo, hi)</code> returns <code>None</code> for an empty range.",
                    "Otherwise compute <code>mid</code>, and first build <code>left = make(lo, mid - 1)</code>: this consumes all smaller values.",
                    "Now <code>cur</code> holds the middle value: create <code>root = TreeNode(cur.val, left)</code> and advance <code>cur</code>.",
                    "Build <code>root.right = make(mid + 1, hi)</code> and return <code>root</code>.",
                    "Call <code>make(0, n - 1)</code>.",
                ],
                "why": [
                    "The calls create nodes in inorder, and the list is sorted, so each node receives the value of its inorder rank: the tree is a BST.",
                    "The shape uses the same middle-split as the array version, so it is height-balanced.",
                    "Each list node is read once and each tree node made once: <strong>O(n)</strong> time. The recursion depth is <strong>O(log n)</strong>, and no array copy is made.",
                ],
                "dry": [
                    [
                        "n = 3, cur at 1. make(0, 2): mid = 1, first make(0, 0).",
                        "make(0, 0): mid = 0, left empty, creates node 1 from cur, cur → 2.",
                        "Back in make(0, 2): creates node 2 with left 1, cur → 3.",
                        "make(2, 2) creates node 3, cur → None. Level order: <strong>[2, 1, 3]</strong>.",
                    ],
                    [
                        "n = 7. make(0, 6): mid = 3, so make(0, 2) runs first and builds 2 → (1, 3), consuming 1, 2, 3.",
                        "cur is now at 4: node 4 becomes the root with left 2.",
                        "make(4, 6) consumes 5, 6, 7 and builds 6 → (5, 7).",
                        "Level order: <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the left subtree be built before the root node?",
                     "The list is consumed in increasing order. The root's value only reaches <code>cur</code> after all the smaller values have been used by the left subtree."],
                    ["Why is <code>cur</code> declared <code>nonlocal</code>?",
                     "It is shared across all recursive calls and reassigned with <code>cur = cur.next</code>, so it must refer to the enclosing variable."],
                    ["What are <code>lo</code> and <code>hi</code> for if values come from <code>cur</code>?",
                     "They only fix the shape: how many nodes each subtree gets. Values never come from them."],
                ],
            },
            "Copy to an array": {
                "idea": [
                    "Convert the problem into the sorted-array one: copy the list into a Python list for O(1) random access.",
                    "Then build from the middle of each index range.",
                ],
                "steps": [
                    "Walk the list and append each value to <code>vals</code>.",
                    "<code>make(lo, hi)</code> returns <code>None</code> when <code>lo &gt; hi</code>.",
                    "Otherwise take <code>mid = (lo + hi) // 2</code>.",
                    "Return <code>TreeNode(vals[mid], make(lo, mid - 1), make(mid + 1, hi))</code>.",
                    "Call <code>make(0, len(vals) - 1)</code>.",
                ],
                "why": [
                    "The middle value of a sorted range is a valid root that splits the rest evenly, so the tree is a height-balanced BST.",
                    "Copying and building are both linear: <strong>O(n)</strong> time.",
                    "The copy costs <strong>O(n)</strong> extra space, on top of the O(log n) recursion stack.",
                ],
                "dry": [
                    [
                        "vals = [1, 2, 3].",
                        "make(0, 2): mid = 1, root 2.",
                        "make(0, 0) gives 1 and make(2, 2) gives 3.",
                        "Level order: <strong>[2, 1, 3]</strong>.",
                    ],
                    [
                        "vals = [1, 2, 3, 4, 5, 6, 7]. make(0, 6): mid = 3, root 4.",
                        "make(0, 2): mid = 1, node 2 with children 1 and 3.",
                        "make(4, 6): mid = 5, node 6 with children 5 and 7.",
                        "Level order: <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is the extra O(n) memory a problem?",
                     "Usually not; it is the simplest correct solution. The inorder simulation is the answer to \"can you avoid the copy?\"."],
                    ["Do this and the inorder simulation build the same tree?",
                     "Yes. Both use <code>(lo + hi) // 2</code> on the same index ranges, so the shapes match exactly."],
                    ["Why not convert each half of the list recursively?",
                     "That is the fast and slow pointer approach, which pays O(n) per level to find each middle."],
                ],
            },
            "Fast and slow pointers for each middle": {
                "idea": [
                    "Treat a sublist as the half-open range <code>[head, tail)</code> and find its middle with a slow pointer moving one step while a fast one moves two.",
                    "The middle becomes the root, <code>[head, slow)</code> the left subtree and <code>[slow.next, tail)</code> the right subtree.",
                ],
                "steps": [
                    "If <code>head is tail</code>, the range is empty: return <code>None</code>.",
                    "Set <code>slow = fast = head</code>.",
                    "While <code>fast</code> and <code>fast.next</code> are both not <code>tail</code>, move <code>slow</code> one step and <code>fast</code> two.",
                    "Return <code>TreeNode(slow.val, recurse(head, slow), recurse(slow.next, tail))</code>.",
                    "The first call uses <code>tail=None</code>, the end of the list.",
                ],
                "why": [
                    "When <code>fast</code> reaches the end of the range, <code>slow</code> has gone half as far, so it is the middle and the split is balanced.",
                    "Each level of recursion scans its ranges, which together cover the list: O(n) per level over O(log n) levels, <strong>O(n log n)</strong> time.",
                    "No copy is made; the recursion is <strong>O(log n)</strong> deep.",
                ],
                "dry": [
                    [
                        "Range [1, None): slow = fast = 1. fast.next = 2 is not the tail, so slow → 2, fast → 3.",
                        "fast.next is None = tail, so the loop stops. Root 2.",
                        "Left range [1, 2): slow stays at 1, node 1. Right range [3, None): node 3.",
                        "Level order: <strong>[2, 1, 3]</strong>.",
                    ],
                    [
                        "Range [1, None): fast moves 1 → 3 → 5 → 7 while slow moves 1 → 2 → 3 → 4. Root 4.",
                        "Left range [1, 4): fast 1 → 3, slow 1 → 2. Node 2 with children from [1, 2) and [3, 4).",
                        "Right range [5, None): root 6 with children 5 and 7.",
                        "Level order: <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why a half-open range with <code>tail</code> instead of cutting the list?",
                     "It leaves the list untouched; the stopping test <code>fast is not tail</code> marks the end without setting any <code>next</code> to <code>None</code>."],
                    ["Does it pick the same middle as the index versions?",
                     "Only for odd lengths. For [1, 2, 3, 4] it picks the upper middle and returns [3, 2, 4, 1], while the index versions return [2, 1, 3, None, None, None, 4]. Both are balanced."],
                    ["When would I use this one?",
                     "When you want no extra array and do not think of the inorder trick. It is a common first answer, but it is O(n log n)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ BST from preorder
    "bst-from-preorder": {
        "examples": [
            {"call": "level_order(bst_from_preorder([8, 5, 1, 7, 10, 12]))", "expect": "[8, 5, 10, 1, 7, None, 12]"},
            {"call": "level_order(bst_from_preorder([3, 1, 2]))", "expect": "[3, 1, None, None, 2]"},
        ],
        "approaches": {
            "One pass with value bounds": {
                "idea": [
                    "In preorder the root comes first, then its whole left subtree, then its whole right subtree.",
                    "The left subtree is the run of following values that are smaller than the root, so a recursive builder can keep taking values while they fit under an upper bound <code>hi</code>.",
                    "A shared index <code>i</code> walks the array once; a value that is too big is left for an ancestor's right side.",
                ],
                "steps": [
                    "Keep a <code>nonlocal</code> index <code>i = 0</code>.",
                    "<code>make(hi)</code> returns <code>None</code> if the input is used up or <code>preorder[i] &gt; hi</code>.",
                    "Otherwise create <code>node = TreeNode(preorder[i])</code> and advance <code>i</code>.",
                    "Build <code>node.left = make(node.val)</code>: the left side may only hold values below this node.",
                    "Build <code>node.right = make(hi)</code>: the right side inherits the node's own upper bound.",
                    "Start with <code>make(float(\"inf\"))</code>.",
                ],
                "why": [
                    "Values are consumed in preorder, and each one is placed in the deepest open slot whose bound admits it, which is exactly where BST insertion would put it.",
                    "A lower bound is not needed: anything smaller than the current node would have been consumed earlier by a left subtree.",
                    "Each value is consumed once and each call either consumes a value or returns <code>None</code>: <strong>O(n)</strong> time. The recursion depth is the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "make(inf) takes 8. Its left make(8) takes 5; 5's left make(5) takes 1, whose children both reject 7.",
                        "5's right make(8) takes 7; 7's children reject 10 (10 &gt; 7 and 10 &gt; 8).",
                        "Back at 8: right make(inf) takes 10. Its left make(10) rejects 12; its right make(inf) takes 12.",
                        "i reaches the end, so all remaining calls return None.",
                        "Level order: <strong>[8, 5, 10, 1, 7, None, 12]</strong>.",
                    ],
                    [
                        "make(inf) takes 3. Left make(3) takes 1.",
                        "1's left make(1) rejects 2 (2 &gt; 1). 1's right make(3) accepts 2, since 2 ≤ 3.",
                        "Back at 3: right make(inf) finds the input used up.",
                        "Level order: <strong>[3, 1, None, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the right child get <code>hi</code> and not <code>node.val</code>?",
                     "The right subtree holds values larger than the node but still below whatever bound the node itself had to respect from its ancestors."],
                    ["Why is no lower bound checked?",
                     "Values arrive in preorder. A value smaller than the current node would belong in a left subtree that has already been finished, which a valid preorder never produces."],
                    ["Why <code>&gt;</code> and not <code>&gt;=</code> in the stop test?",
                     "The problem has distinct values, so equality never happens; with <code>&gt;</code> an equal value would go left."],
                ],
            },
            "Insert each value in turn": {
                "idea": [
                    "Inserting values into an empty BST in preorder rebuilds the original tree: each node arrives after its parent, so it lands under it.",
                    "This reuses the plain BST insert and needs no reasoning about bounds.",
                ],
                "steps": [
                    "The first value becomes <code>root</code>.",
                    "For each later <code>v</code>, walk from <code>root</code>: choose <code>side = \"left\"</code> if <code>v &lt; node.val</code>, else <code>\"right\"</code>.",
                    "If that child is empty, attach <code>TreeNode(v)</code> there with <code>setattr</code> and stop.",
                    "Otherwise move into the child and repeat.",
                    "Return <code>root</code>.",
                ],
                "why": [
                    "A node's ancestors all precede it in preorder, so by the time it is inserted its whole path exists and the walk ends exactly at its original position.",
                    "Each insert walks up to the height of the tree: <strong>O(n²)</strong> in the worst case (a sorted or reverse-sorted preorder makes a chain), O(n log n) for a balanced one.",
                    "Only the walking pointer is extra; the listed <strong>O(h)</strong> space is generous, as the loop itself uses O(1).",
                ],
                "dry": [
                    [
                        "8 becomes the root. 5 &lt; 8: left of 8.",
                        "1: 8 → 5 → left of 5. 7: 8 → 5 → right of 5.",
                        "10: right of 8. 12: 8 → 10 → right of 10.",
                        "Level order: <strong>[8, 5, 10, 1, 7, None, 12]</strong>.",
                    ],
                    [
                        "3 becomes the root.",
                        "1 &lt; 3: left of 3.",
                        "2: 2 &lt; 3, go to 1; 2 ≥ 1, attach on the right of 1.",
                        "Level order: <strong>[3, 1, None, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>getattr</code>/<code>setattr</code>?",
                     "They let one branch handle both sides by the attribute name, instead of repeating the code for left and right."],
                    ["When does it hit O(n²)?",
                     "When the tree is a chain, e.g. preorder [5, 4, 3, 2, 1]: the k-th insert walks k − 1 nodes."],
                    ["Would inserting in any other order work?",
                     "Inserting a different order may build a different tree. Preorder (or level order) guarantees parents come before children, which is what reproduces the shape."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ BST to greater tree
    "bst-to-greater-tree": {
        "examples": [
            {"call": "level_order(convert_bst(build([3, 1, 4, None, 2])))", "expect": "[7, 10, 4, None, 9]"},
            {"call": "level_order(convert_bst(build([0, None, 1])))", "expect": "[1, None, 1]"},
        ],
        "approaches": {
            "Reverse inorder with a running sum": {
                "idea": [
                    "Each node must become its value plus every larger value in the tree.",
                    "Visiting nodes from largest to smallest (right, node, left) means a running total already holds the sum of all larger values when a node is reached.",
                ],
                "steps": [
                    "Keep <code>running = 0</code> as <code>nonlocal</code> state.",
                    "In <code>walk(node)</code>, recurse into <code>node.right</code> first.",
                    "Add <code>node.val</code> to <code>running</code> and store <code>node.val = running</code>.",
                    "Recurse into <code>node.left</code>.",
                    "Return the same <code>root</code>; the tree is changed in place.",
                ],
                "why": [
                    "Reverse inorder visits values in decreasing order, so at each node <code>running</code> equals the node's own value plus all values greater than it.",
                    "Overwriting a value after it has been added is safe: smaller nodes only need the running total, not the original value.",
                    "Each node is visited once: <strong>O(n)</strong> time. The recursion stack is <strong>O(h)</strong>.",
                ],
                "dry": [
                    [
                        "The tree: 3 → (1, 4), 1 → (None, 2). Reverse inorder: 4, 3, 2, 1.",
                        "4: running = 4, node becomes 4.",
                        "3: running = 7. Then the left subtree, right side first: 2: running = 9.",
                        "1: running = 10.",
                        "Level order: <strong>[7, 10, 4, None, 9]</strong>.",
                    ],
                    [
                        "Reverse inorder: 1, 0.",
                        "1: running = 1. 0: running = 1.",
                        "Adding 0 changes nothing, so both nodes hold 1: <strong>[1, None, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why right subtree first?",
                     "The right subtree holds all the larger values below this node; they must be added to <code>running</code> before the node itself is updated."],
                    ["Does this handle negative values?",
                     "Yes. The running sum just adds whatever values appear; nothing assumes they are positive."],
                    ["Is this the same as LeetCode 1038?",
                     "Yes, \"BST to Greater Sum Tree\" is the same problem and the same code works."],
                ],
            },
            "Reverse Morris traversal": {
                "idea": [
                    "Morris traversal removes the recursion stack by temporarily threading a pointer back to the node it must return to.",
                    "For the reverse order, the node visited just before <code>node</code> is the leftmost node of its right subtree, its inorder successor. Its empty <code>left</code> pointer is borrowed to point back at <code>node</code>.",
                    "Every thread is created once and removed once, so the tree is restored as the walk finishes.",
                ],
                "steps": [
                    "Start with <code>running = 0</code> and <code>node = root</code>.",
                    "If <code>node.right</code> is <code>None</code>, update <code>running</code> and <code>node.val</code>, then move to <code>node.left</code>.",
                    "Otherwise find <code>succ</code>: go to <code>node.right</code>, then left while <code>succ.left</code> is neither <code>None</code> nor <code>node</code>.",
                    "If <code>succ.left</code> is <code>None</code>, set <code>succ.left = node</code> (the thread) and move right.",
                    "If it already points to <code>node</code>, the right side is done: remove the thread, update <code>running</code> and <code>node.val</code>, and move left.",
                ],
                "why": [
                    "The threads let the walk climb back to <code>node</code> after its right subtree, giving the same right, node, left order as the recursion.",
                    "Each edge is walked a constant number of times while finding successors (once to build the thread, once to remove it), so time stays <strong>O(n)</strong>.",
                    "Only <code>running</code>, <code>node</code> and <code>succ</code> are stored: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "node = 3: its successor is 4 (4.left is empty). Thread 4.left = 3, go right to 4.",
                        "node = 4: no right child, so running = 4, value 4, then follow the thread back to 3.",
                        "node = 3: successor 4 already points here. Remove the thread, running = 7, value 7, go left to 1.",
                        "node = 1: successor is 2; thread 2.left = 1, go to 2. Node 2 has no right: running = 9, follow the thread to 1.",
                        "node = 1: remove the thread, running = 10, go left to None. Result <strong>[7, 10, 4, None, 9]</strong>.",
                    ],
                    [
                        "node = 0: successor is 1; thread 1.left = 0, go right.",
                        "node = 1: no right child, running = 1, follow the thread back to 0.",
                        "node = 0: remove the thread, running = 1, go left to None.",
                        "The result is <strong>[1, None, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["How does it know whether it is arriving at a node for the first or second time?",
                     "By the successor's <code>left</code> pointer: empty means first visit (create the thread), pointing at <code>node</code> means the right side is finished."],
                    ["Why does the inner loop check <code>succ.left is not node</code>?",
                     "On the second visit the thread already exists. Without that check the loop would follow it back to <code>node</code> and go round forever."],
                    ["Is the tree left unchanged in shape?",
                     "Yes. Every thread is removed on the second visit, so only the values change."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ balance a BST
    "balance-bst": {
        "examples": [
            {"call": "level_order(balance_bst(build([1, None, 2, None, 3, None, 4, None, 5, None, 6, None, 7])))", "expect": "[4, 2, 6, 1, 3, 5, 7]"},
            {"call": "level_order(balance_bst(build([3, 2, None, 1])))", "expect": "[2, 1, 3]"},
        ],
        "approaches": {
            "Inorder to a list, rebuild from the middle": {
                "idea": [
                    "Inorder gives the nodes in sorted order, and a sorted sequence can be turned into a balanced BST by always using the middle as the root.",
                    "The nodes themselves are reused: only their <code>left</code> and <code>right</code> pointers are rewritten.",
                ],
                "steps": [
                    "Walk the tree in inorder and append each node object to <code>nodes</code>.",
                    "<code>make(lo, hi)</code> returns <code>None</code> for an empty range.",
                    "Pick <code>mid = (lo + hi) // 2</code> and take <code>node = nodes[mid]</code>.",
                    "Set its children to <code>make(lo, mid - 1)</code> and <code>make(mid + 1, hi)</code>.",
                    "Return <code>make(0, len(nodes) - 1)</code>.",
                ],
                "why": [
                    "The list is sorted, so the middle split keeps the BST order, and the halves differ in size by at most one, which keeps every node height-balanced.",
                    "All old pointers are overwritten during the rebuild, so no stale links survive (leaves get two <code>None</code> children).",
                    "The traversal and rebuild are both linear: <strong>O(n)</strong> time. The list of nodes costs <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree is a right chain 1 → 2 → … → 7. Inorder gives nodes [1, 2, 3, 4, 5, 6, 7].",
                        "make(0, 6): mid = 3, root 4.",
                        "make(0, 2): node 2 with children 1 and 3. make(4, 6): node 6 with children 5 and 7.",
                        "Level order: <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                    ],
                    [
                        "The tree is a left chain 3 → 2 → 1. Inorder gives nodes [1, 2, 3].",
                        "make(0, 2): mid = 1, root 2.",
                        "Its children are node 1 and node 3, both with cleared pointers.",
                        "Level order: <strong>[2, 1, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store nodes rather than values?",
                     "Reusing the nodes avoids allocating a second tree. Storing values and creating new <code>TreeNode</code>s also works."],
                    ["Is it safe to change pointers of nodes that are still in the old tree?",
                     "Yes, because the inorder walk is finished before the rebuild starts; the old shape is no longer needed."],
                    ["Can the result differ from other balanced trees?",
                     "Yes. Any height-balanced BST is accepted; for 4 nodes this version gives [2, 1, 3, None, None, None, 4] while DSW gives [3, 2, 4, 1]."],
                ],
            },
            "Day&ndash;Stout&ndash;Warren: rotations only": {
                "idea": [
                    "DSW balances a tree in place in two phases. First, right rotations straighten it into a sorted right-leaning chain, the <strong>vine</strong>.",
                    "Second, repeated passes of left rotations on every other vine node fold it into a balanced tree, halving the vine's length each pass.",
                    "A first short pass handles the leftover nodes so the final tree is complete except for the bottom level.",
                ],
                "steps": [
                    "Hang the tree off a <code>pseudo</code> root's right pointer.",
                    "Phase 1: walk <code>rest</code> down the right side. If <code>rest</code> has a left child, rotate right there (the child moves up); otherwise advance <code>tail</code> and count <code>size</code>.",
                    "Compute <code>leaves = size + 1 - 2<sup>⌊log₂(size + 1)⌋</sup></code>, the nodes beyond the largest perfect tree, and call <code>compress(leaves)</code>.",
                    "<code>compress(count)</code> does <code>count</code> left rotations, each lifting every second vine node above the one before it.",
                    "Then, while <code>size &gt; 1</code>, halve <code>size</code> and compress again.",
                    "Return <code>pseudo.right</code>.",
                ],
                "why": [
                    "Rotations keep the inorder order, so the tree stays a valid BST through every step.",
                    "Each right rotation in phase 1 puts one more node on the vine for good, so there are fewer than n of them; the compress passes do about n/2 + n/4 + … rotations: <strong>O(n)</strong> time.",
                    "No list or recursion is used, only a few pointers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "The input is already a vine: phase 1 does no rotations, size = 7.",
                        "leaves = 8 − 8 = 0, so the first compress does nothing.",
                        "size = 3: compress(3) lifts 2, 4, 6 above 1, 3, 5, giving [2, 1, 4, None, None, 3, 6, None, None, 5, 7].",
                        "size = 1: compress(1) lifts 4 above 2, giving the perfect tree.",
                        "Level order: <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                    ],
                    [
                        "rest = 3 has left child 2: rotate right, giving 2 → (1, 3).",
                        "rest = 2 has left child 1: rotate right, giving the vine 1 → 2 → 3. Then size counts to 3.",
                        "leaves = 4 − 4 = 0. size = 1: compress(1) rotates 2 above 1.",
                        "Level order: <strong>[2, 1, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["What is <code>pseudo</code> for?",
                     "Rotations at the top change the root. With a fixed parent above it, the top rotation is the same as any other, and <code>pseudo.right</code> is always the current root."],
                    ["Why the separate first compress with <code>leaves</code>?",
                     "If size + 1 is not a power of two, the extra nodes are folded down first so the rest of the vine has 2<sup>k</sup> − 1 nodes and halves evenly."],
                    ["When would anyone use this over the list rebuild?",
                     "When memory is tight or nodes cannot be copied into an array. In interviews the list rebuild is expected; DSW is the O(1)-space follow-up."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ BST to sorted doubly linked list
    "bst-to-sorted-dll": {
        "examples": [
            {"setup": "head = tree_to_doubly_list(build([4, 2, 5, 1, 3]))",
             "call": "[head.val, head.right.val, head.right.right.val, head.left.val]", "expect": "[1, 2, 3, 5]"},
            {"setup": "head = tree_to_doubly_list(build([1]))",
             "call": "(head.val, head.left is head, head.right is head)", "expect": "(1, True, True)"},
        ],
        "approaches": {
            "Inorder, link each node to the previous one": {
                "idea": [
                    "The list order is the inorder order, so walk the tree in inorder and stitch each node to the one visited just before it.",
                    "<code>left</code> becomes \"previous\" and <code>right</code> becomes \"next\".",
                    "After the walk, the first and last nodes are joined to close the circle.",
                ],
                "steps": [
                    "Return <code>None</code> for an empty tree. Keep <code>head</code> and <code>prev</code> as <code>nonlocal</code> state.",
                    "Recurse into <code>node.left</code>.",
                    "If <code>prev</code> is <code>None</code>, this is the smallest node: set <code>head = node</code>. Otherwise link <code>prev.right = node</code> and <code>node.left = prev</code>.",
                    "Set <code>prev = node</code> and recurse into <code>node.right</code>.",
                    "Finally set <code>head.left = prev</code> and <code>prev.right = head</code>.",
                ],
                "why": [
                    "Nodes are linked in inorder, so the list is sorted, and each link connects exact neighbours.",
                    "Changing <code>node.left</code> is safe because the left subtree is already finished; <code>prev.right</code> is safe because prev's right subtree finished before this node was reached.",
                    "Each node is visited once: <strong>O(n)</strong> time; the recursion uses <strong>O(h)</strong> space and no new nodes are created.",
                ],
                "dry": [
                    [
                        "The tree: 4 → (2, 5), 2 → (1, 3). Inorder: 1, 2, 3, 4, 5.",
                        "1: prev is None, head = 1. 2: link 1 ⇄ 2. 3: link 2 ⇄ 3.",
                        "4: link 3 ⇄ 4. 5: link 4 ⇄ 5. prev = 5.",
                        "Close the circle: 1.left = 5, 5.right = 1.",
                        "Reading head, next, next, and head.left gives <strong>[1, 2, 3, 5]</strong>.",
                    ],
                    [
                        "The only node 1: prev is None, so head = 1 and prev = 1.",
                        "Closing the circle sets 1.left = 1 and 1.right = 1.",
                        "A one-node circular list points to itself: <strong>(1, True, True)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the empty tree handled before the walk?",
                     "Closing the circle reads <code>head.left</code>; with no nodes <code>head</code> would be <code>None</code> and that line would crash."],
                    ["Does overwriting <code>node.left</code> break the traversal?",
                     "No. The recursion into <code>node.left</code> has already returned, so that pointer is not read again."],
                    ["How is this different from flattening to a linked list?",
                     "Flattening uses preorder and only right pointers. Here the order is inorder and both directions are kept, plus the circular link."],
                ],
            },
        },
    },
}
