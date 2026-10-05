"""Write-ups for Trees, part A: traversals, depth, level order, compare and transform."""

_T = "build([1, 2, 3, 4, 5, None, 8, None, None, 6, 7])"
_SHAPE = "The tree: 1 has children 2 and 3; 2 has 4 and 5; 5 has 6 and 7; 3 has only a right child, 8."

EXPLAIN = {
    # ------------------------------------------------------------------ preorder
    "preorder-traversal": {
        "example": {"call": f"preorder({_T})", "expect": "[1, 2, 4, 5, 6, 7, 3, 8]"},
        "approaches": {
            "Recursive": {
                "idea": [
                    "Preorder means <strong>root, left, right</strong>: record a node the moment you arrive, before visiting either subtree.",
                    "A recursive helper does exactly that; a <code>None</code> child just returns.",
                ],
                "steps": [
                    "<code>walk(node)</code>: if None, return; append <code>node.val</code>; walk the left child; walk the right child.",
                    "Call <code>walk(root)</code> and return the collected list.",
                ],
                "why": [
                    "Every node is entered once and does O(1) work, so it is O(n) time.",
                    "The call stack holds the path from the root to the current node: O(h), which is O(n) for a chain.",
                ],
                "dry": [
                    _SHAPE,
                    "Arrive at 1 (record), go left to 2 (record), left to 4 (record). 4 has no children, so return to 2.",
                    "Go right to 5 (record), then 6 and 7, back up to 1, then right to 3 (record) and 8 (record).",
                    "The result is <strong>[1, 2, 4, 5, 6, 7, 3, 8]</strong>.",
                ],
            },
            "Iterative, one stack": {
                "idea": [
                    "Replace the call stack with your own list: pop a node, record it, then push its children.",
                    "Push the <em>right</em> child first, so the left child sits on top and is popped first.",
                ],
                "steps": [
                    "<code>stack = [root]</code>.",
                    "While the stack is non-empty: pop, append the value, push right (if any), push left (if any).",
                ],
                "why": [
                    "The stack holds deferred right children, at most one per level, so it is O(h).",
                    "It cannot hit Python's recursion limit.",
                ],
                "dry": [
                    "Pop 1 → push 3, 2. Pop 2 → push 5, 4. Pop 4 (no children).",
                    "Pop 5 → push 7, 6. Pop 6, pop 7. Pop 3 → push 8. Pop 8.",
                    "The pop order is <strong>[1, 2, 4, 5, 6, 7, 3, 8]</strong>.",
                ],
            },
            "Morris traversal": {
                "idea": [
                    "To get O(1) extra space, store the \"way back up\" inside the tree.",
                    "Before descending left, find the left subtree's rightmost node (the <em>predecessor</em>) and point its <code>right</code> at the current node. This is a temporary <strong>thread</strong>.",
                    "When you later follow that thread back, you know the left side is finished, so remove the thread and go right.",
                    "For preorder, record the node when the thread is <em>created</em>, which is the first arrival.",
                ],
                "steps": [
                    "If <code>node.left</code> is None: record it and go right.",
                    "Otherwise find <code>pred</code>. If <code>pred.right</code> is None: record the node, set the thread, go left. If it already points at the node: remove the thread and go right.",
                ],
                "why": [
                    "Each edge is walked at most about three times (down, predecessor search, unthread), so it is still O(n).",
                    "No stack is needed. The tree is restored by the end, but it is modified while the loop runs.",
                ],
                "dry": [
                    "At 1: pred = 7 (rightmost under 2). Record 1, thread 7 → 1, go to 2.",
                    "At 2: pred = 4. Record 2, thread 4 → 2, go to 4. 4 has no left: record 4, follow the thread to 2. Unthread and go to 5.",
                    "At 5: record 5, thread 6 → 5. Record 6, follow the thread back to 5, unthread, go to 7. Record 7, follow 7 → 1, unthread, go to 3.",
                    "Record 3 and 8. The result is <strong>[1, 2, 4, 5, 6, 7, 3, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ inorder
    "inorder-traversal": {
        "example": {"call": f"inorder({_T})", "expect": "[4, 2, 6, 5, 7, 1, 3, 8]"},
        "approaches": {
            "Recursive": {
                "idea": [
                    "Inorder means <strong>left, root, right</strong>: record a node only after its whole left subtree is done.",
                    "It is the same walk as preorder; only the position of the append moves.",
                ],
                "steps": [
                    "<code>walk(node)</code>: walk the left child, append <code>node.val</code>, walk the right child.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                    "On a BST, inorder visits values in sorted order, which many later problems use.",
                ],
                "dry": [
                    _SHAPE,
                    "Descend 1 → 2 → 4. 4 has no left, so record 4, then back to 2: record 2.",
                    "Go into 5: its left subtree gives 6, then record 5, then 7.",
                    "Back at 1: record 1, then 3 (no left), then 8. The result is <strong>[4, 2, 6, 5, 7, 1, 3, 8]</strong>.",
                ],
            },
            "Iterative, one stack": {
                "idea": [
                    "Run left as far as possible, pushing every node you pass.",
                    "When you cannot go further left, the top of the stack is the next node in order: pop it, record it, then move to its right child.",
                    "Invariant: the stack holds nodes whose left side is finished but which have not been recorded yet.",
                ],
                "steps": [
                    "Inner loop: push and go left. Then pop, record, set <code>node = node.right</code>.",
                    "Repeat while the stack is non-empty or <code>node</code> is not None.",
                ],
                "why": [
                    "Each node is pushed once and popped once: O(n), even though the loops look nested.",
                    "The stack is O(h).",
                ],
                "dry": [
                    "Push 1, 2, 4. Pop 4 (record), its right is None. Pop 2 (record), go to 5.",
                    "Push 5, 6. Pop 6, pop 5, go to 7: push and pop 7.",
                    "Pop 1, go to 3: push and pop 3, go to 8: push and pop 8.",
                    "The result is <strong>[4, 2, 6, 5, 7, 1, 3, 8]</strong>.",
                ],
            },
            "Morris traversal": {
                "idea": [
                    "This is the same threading trick as Morris preorder: thread the predecessor's <code>right</code> back to the current node before going left.",
                    "For inorder, record the node when you <em>come back</em> along the thread, which is the moment its left side is complete.",
                ],
                "steps": [
                    "No left child: record and go right.",
                    "If <code>pred.right</code> is None: set the thread and go left. If it is the node: remove the thread, record, go right.",
                ],
                "why": [
                    "It is O(n) time and O(1) extra space; the tree is temporarily modified.",
                ],
                "dry": [
                    "At 1: thread 7 → 1, go to 2. At 2: thread 4 → 2, go to 4.",
                    "4 has no left: record 4, follow the thread to 2. The thread exists, so unthread and record 2, then go to 5.",
                    "At 5: thread 6 → 5. Record 6, return, record 5, record 7. Follow 7 → 1: record 1, go to 3, record 3, record 8.",
                    "The result is <strong>[4, 2, 6, 5, 7, 1, 3, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ postorder
    "postorder-traversal": {
        "example": {"call": f"postorder({_T})", "expect": "[4, 6, 7, 5, 2, 8, 3, 1]"},
        "approaches": {
            "Recursive": {
                "idea": [
                    "Postorder means <strong>left, right, root</strong>: record a node only after <em>both</em> subtrees are done.",
                    "That is exactly the shape you need when a node's answer depends on its children's answers (height, sums, and so on).",
                ],
                "steps": [
                    "<code>walk(node)</code>: walk the left child, walk the right child, then append <code>node.val</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    _SHAPE,
                    "4 has no children: record 4. 5's children give 6 and 7, then record 5, then 2 (both subtrees done).",
                    "On the right side: 8, then 3. Finally the root, 1.",
                    "The result is <strong>[4, 6, 7, 5, 2, 8, 3, 1]</strong>.",
                ],
            },
            "Reversed modified preorder": {
                "idea": [
                    "Postorder reversed is <strong>root, right, left</strong>, which is preorder with the children swapped.",
                    "So run that easy iterative preorder (push left first, then right), and reverse the list at the end.",
                ],
                "steps": [
                    "Pop, record, push left, push right.",
                    "<code>out.reverse()</code> at the end.",
                ],
                "why": [
                    "Reversing an order that is the exact mirror of postorder gives postorder.",
                    "It is O(n) time and O(h) stack, plus one in-place reverse.",
                ],
                "dry": [
                    "Pop 1 → push 2, 3. Pop 3 → push 8. Pop 8. Pop 2 → push 4, 5.",
                    "Pop 5 → push 6, 7. Pop 7, pop 6, pop 4.",
                    "Recorded [1, 3, 8, 2, 5, 7, 6, 4]; reversed, that is <strong>[4, 6, 7, 5, 2, 8, 3, 1]</strong>.",
                ],
            },
            "One stack, true postorder": {
                "idea": [
                    "To record in true postorder as you go, you must tell \"arrived from the left\" apart from \"returned from the right\".",
                    "Remember the last node recorded (<code>last</code>). If the top node's right child is unfinished, descend into it; otherwise the node is ready.",
                ],
                "steps": [
                    "Push left as far as possible, then peek at the top.",
                    "If <code>peek.right</code> exists and is not <code>last</code>, go right. Otherwise record <code>peek</code> and set <code>last = stack.pop()</code>.",
                ],
                "why": [
                    "Each node is pushed once and peeked a bounded number of times: O(n) time, O(h) stack.",
                ],
                "dry": [
                    "Push 1, 2, 4. 4 has no right: record 4. Peek 2: its right 5 is unfinished, so go there and push 5, 6.",
                    "Record 6. Peek 5: go right to 7, record 7. Peek 5: its right is last, so record 5. Peek 2: record 2.",
                    "Peek 1: go to 3; push 3. Its right 8 is unfinished: record 8, then 3, then 1.",
                    "The result is <strong>[4, 6, 7, 5, 2, 8, 3, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max depth
    "maximum-depth": {
        "example": {"call": "max_depth(build([3, 9, 20, None, None, 15, 7]))", "expect": "3"},
        "approaches": {
            "Recursive postorder": {
                "idea": [
                    "The depth of a tree is 1 (the root) plus the deeper of its two subtrees.",
                    "An empty tree has depth 0, which makes leaves come out as 1 automatically.",
                ],
                "steps": [
                    "<code>return 0</code> for None; otherwise <code>1 + max(depth(left), depth(right))</code>.",
                ],
                "why": [
                    "Every node is visited once: O(n). The stack is O(h); a 10,000-node chain exceeds Python's default recursion limit.",
                ],
                "dry": [
                    "The tree: 3 → (9, 20), and 20 → (15, 7).",
                    "depth(9) = 1; depth(15) = depth(7) = 1, so depth(20) = 2.",
                    "depth(3) = 1 + max(1, 2) = <strong>3</strong>.",
                ],
            },
            "BFS, counting levels": {
                "idea": [
                    "Process the tree one level at a time with a queue, and count the levels.",
                    "Snapshot <code>len(queue)</code> at the start of each level, so you remove exactly that level's nodes.",
                ],
                "steps": [
                    "<code>depth += 1</code>; pop <code>len(queue)</code> nodes, pushing their children.",
                ],
                "why": [
                    "It is O(n) time; the queue holds at most about one level, O(w).",
                    "It has no recursion limit.",
                ],
                "dry": [
                    "Level 1: [3] → queue [9, 20]. Level 2: [9, 20] → queue [15, 7].",
                    "Level 3: [15, 7] → queue empty.",
                    "There are <strong>3</strong> levels.",
                ],
            },
            "Iterative DFS with explicit depth": {
                "idea": [
                    "Put <code>(node, depth)</code> pairs on a stack, and track the largest depth seen.",
                ],
                "steps": [
                    "Pop a pair, update <code>best</code>, and push the children with depth + 1.",
                ],
                "why": [
                    "It is O(n) time and O(h) space, without recursion.",
                ],
                "dry": [
                    "Pop (3, 1) → push (9, 2), (20, 2). Pop (20, 2) → push (15, 3), (7, 3).",
                    "Pop (7, 3): best = 3. Then (15, 3) and (9, 2) change nothing.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ min depth
    "minimum-depth": {
        "example": {"call": "min_depth(build([1, 2, 3, 4, 5, None, 6]))", "expect": "3"},
        "approaches": {
            "Recursive, with the one-child case": {
                "idea": [
                    "Minimum depth is the distance to the nearest <strong>leaf</strong>, a node with no children.",
                    "The trap: if a node has only one child, the missing side is <em>not</em> a path to a leaf, so you must not take min with its 0.",
                    "So: two children → 1 + min; one child → 1 + that child's depth; no children → 1.",
                ],
                "steps": [
                    "Compute <code>left</code> and <code>right</code>.",
                    "If either child is None, return <code>1 + left + right</code> (one of them is 0); otherwise <code>1 + min(left, right)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), 2 → (4, 5), and 3 has only a right child, 6.",
                    "Node 3 has one child, so its depth is 1 + 0 + 1 = 2, <em>not</em> 1 + min(0, 1) = 1.",
                    "Node 2 = 1 + min(1, 1) = 2. Root = 1 + min(2, 2) = <strong>3</strong>.",
                ],
            },
            "BFS with early exit": {
                "idea": [
                    "BFS visits nodes in order of depth, so the <em>first leaf</em> it meets is at the minimum depth.",
                    "Return as soon as you pop a node with no children.",
                ],
                "steps": [
                    "Level by level; on the first leaf, return the current depth.",
                ],
                "why": [
                    "It is O(n) in the worst case, but it stops at the shallowest leaf, so it often explores only a few levels.",
                ],
                "dry": [
                    "Depth 1: node 1 has children. Depth 2: nodes 2 and 3 both have a child.",
                    "Depth 3: the first popped node, 4, is a leaf.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ level order
    "level-order-traversal": {
        "example": {"call": "level_order_lists(build([1, 2, 3, 4, 5, 6, 7]))", "expect": "[[1], [2, 3], [4, 5, 6, 7]]"},
        "approaches": {
            "BFS with a size snapshot": {
                "idea": [
                    "A queue visits nodes level by level, left to right.",
                    "To group them, read <code>len(queue)</code> before each level: exactly that many pops belong to the level.",
                ],
                "steps": [
                    "While the queue is non-empty: pop <code>len(queue)</code> nodes into a list, pushing their children.",
                    "Append the list to the output.",
                ],
                "why": [
                    "Each node enters and leaves the queue once: O(n). The queue holds O(w) nodes.",
                    "<code>range(len(queue))</code> is evaluated once, before the children are appended.",
                ],
                "dry": [
                    "Queue [1] → level [1]; the queue becomes [2, 3].",
                    "Snapshot 2 → level [2, 3]; the queue becomes [4, 5, 6, 7].",
                    "Snapshot 4 → level [4, 5, 6, 7]. The result is <strong>[[1], [2, 3], [4, 5, 6, 7]]</strong>.",
                ],
            },
            "DFS carrying the depth": {
                "idea": [
                    "You do not need BFS to group by level, only each node's depth.",
                    "Pass the depth down. The first time a depth is seen, start a new list. Left-before-right DFS fills each level from left to right.",
                ],
                "steps": [
                    "<code>if depth == len(out): out.append([])</code>; then <code>out[depth].append(val)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack (the BFS version uses O(w) instead).",
                ],
                "dry": [
                    "1 at depth 0 creates [1]. 2 at depth 1 creates [2]. 4 at depth 2 creates [4]; 5 joins it.",
                    "3 joins depth 1 → [2, 3]. 6 and 7 join depth 2 → [4, 5, 6, 7].",
                    "The result is <strong>[[1], [2, 3], [4, 5, 6, 7]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ level order II
    "level-order-bottom-up": {
        "example": {"call": "level_order_bottom(build([3, 9, 20, None, None, 15, 7]))", "expect": "[[15, 7], [9, 20], [3]]"},
        "approaches": {
            "BFS, then reverse once": {
                "idea": [
                    "Build the normal top-down level list, then reverse the list of levels once.",
                ],
                "steps": [
                    "Run the standard level-order BFS; then <code>out.reverse()</code>.",
                ],
                "why": [
                    "It is O(n) for the BFS plus O(L) for the reverse.",
                ],
                "dry": [
                    "Top-down: [[3], [9, 20], [15, 7]].",
                    "Reversed: <strong>[[15, 7], [9, 20], [3]]</strong>.",
                ],
            },
            "Prepend each level to a deque": {
                "idea": [
                    "Put each finished level on the <em>front</em> of a deque, so the deepest level ends up first.",
                    "<code>deque.appendleft</code> is O(1); <code>list.insert(0, …)</code> would shift everything each time.",
                ],
                "steps": [
                    "<code>out.appendleft(level)</code>; convert to a list at the end.",
                ],
                "why": [
                    "It is O(n) total.",
                ],
                "dry": [
                    "After level 1: [[3]]. After level 2: [[9, 20], [3]].",
                    "After level 3: <strong>[[15, 7], [9, 20], [3]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ zigzag
    "zigzag-level-order": {
        "example": {"call": "zigzag(build([1, 2, 3, 4, 5, 6, 7]))", "expect": "[[1], [3, 2], [4, 5, 6, 7]]"},
        "approaches": {
            "BFS, reverse alternate levels": {
                "idea": [
                    "Collect every level left to right as usual, and reverse every second level before saving it.",
                    "The traversal stays the trusted one; the zigzag is just a change in how each level is presented.",
                ],
                "steps": [
                    "Flip a <code>left_to_right</code> flag after each level; reverse when it is False.",
                ],
                "why": [
                    "Each node is in one level, so all the reversals together cost O(n).",
                ],
                "dry": [
                    "Level 1: [1] (left to right).",
                    "Level 2: [2, 3] reversed to [3, 2]. Level 3: [4, 5, 6, 7] kept.",
                    "The result is <strong>[[1], [3, 2], [4, 5, 6, 7]]</strong>.",
                ],
            },
            "Build each level into a deque": {
                "idea": [
                    "Write each value straight into a per-level deque: <code>append</code> when going left to right, <code>appendleft</code> otherwise.",
                ],
                "steps": [
                    "No reversal step; convert each deque to a list.",
                ],
                "why": [
                    "It is O(n) and O(w), with the direction handled during the traversal.",
                ],
                "dry": [
                    "Level 2 is right to left: appendleft(2) → [2], appendleft(3) → [3, 2].",
                    "Level 3 is left to right: [4, 5, 6, 7].",
                    "The result is <strong>[[1], [3, 2], [4, 5, 6, 7]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ same tree
    "same-tree": {
        "example": {"call": "is_same_tree(build([1, 2, 1]), build([1, 1, 2]))", "expect": "False"},
        "approaches": {
            "Parallel recursion": {
                "idea": [
                    "Walk both trees together, comparing nodes at the same position.",
                    "Both None means equal here; exactly one None means a different shape; different values mean different trees.",
                ],
                "steps": [
                    "Apply the three checks, then require the left pair <em>and</em> the right pair to match.",
                ],
                "why": [
                    "<code>and</code> short-circuits, so the first mismatch stops everything: O(min(n, m)).",
                ],
                "dry": [
                    "The roots are 1 and 1: equal, so compare the left children.",
                    "2 vs 1: the values differ, so return False, and the right pair is never checked.",
                    "The result is <strong>False</strong>.",
                ],
            },
            "Iterative, stack of pairs": {
                "idea": [
                    "Push node pairs onto a stack; pop each pair, check it, and push the two child pairs.",
                ],
                "steps": [
                    "Skip (None, None); return False on any mismatch; True when the stack empties.",
                ],
                "why": [
                    "It is O(min(n, m)) time and O(h) stack, with no recursion limit.",
                ],
                "dry": [
                    "Pop (1, 1): fine, so push (2, 1) (left pair) and (1, 2) (right pair).",
                    "Pop (1, 2): the values differ.",
                    "The result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ symmetric
    "symmetric-tree": {
        "example": {"call": "is_symmetric(build([1, 2, 2, 3, 4, 4, 3]))", "expect": "True"},
        "approaches": {
            "Recursive mirror helper": {
                "idea": [
                    "A tree is symmetric when its left subtree is the mirror image of its right.",
                    "Two nodes mirror each other when their values match, the <strong>outer</strong> pair (a.left, b.right) mirrors, and the <strong>inner</strong> pair (a.right, b.left) mirrors.",
                ],
                "steps": [
                    "<code>mirror(root.left, root.right)</code>, using the Same Tree base cases.",
                ],
                "why": [
                    "Each node is checked once in one pair: O(n) time and O(h) stack.",
                ],
                "dry": [
                    "mirror(2, 2): the values match.",
                    "The outer pair is (3, 3), which matches; the inner pair is (4, 4), which matches.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Iterative, queue of mirrored pairs": {
                "idea": [
                    "Every pair in the queue must mirror. Pop a pair, check it, and enqueue its outer and inner child pairs.",
                ],
                "steps": [
                    "Start with <code>(root.left, root.right)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(w) space, and it finds shallow asymmetries early.",
                ],
                "dry": [
                    "Pop (2, 2) → enqueue (3, 3) and (4, 4).",
                    "Both pairs match, and their None children pair up as well.",
                    "The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ invert
    "invert-binary-tree": {
        "example": {"call": "level_order(invert(build([4, 2, 7, 1, 3, 6, 9])))", "expect": "[4, 7, 2, 9, 6, 3, 1]"},
        "approaches": {
            "Recursive swap": {
                "idea": [
                    "Inverting a tree means swapping every node's left and right children.",
                    "Swap at this node, and invert both subtrees; the order does not matter.",
                ],
                "steps": [
                    "<code>root.left, root.right = invert(root.right), invert(root.left)</code>.",
                ],
                "why": [
                    "Each node's children are swapped once: O(n) time, O(h) stack, done in place.",
                ],
                "dry": [
                    "Under 2, children 1 and 3 swap to 3, 1. Under 7, children 6 and 9 swap to 9, 6.",
                    "At the root, 2 and 7 swap.",
                    "Level order: <strong>[4, 7, 2, 9, 6, 3, 1]</strong>.",
                ],
            },
            "Iterative with a worklist": {
                "idea": [
                    "Each swap is independent of the others, so any visiting order works.",
                    "Take a node off a stack, swap its children, and push them.",
                ],
                "steps": [
                    "<code>work = [root]</code>; pop, swap, push the children.",
                ],
                "why": [
                    "It is O(n) time; O(h) space with a stack, or O(w) with a queue.",
                ],
                "dry": [
                    "Pop 4: swap to (7, 2); push 7 and 2.",
                    "Pop 2: swap to (3, 1). Pop 7: swap to (9, 6), with the leaves done along the way.",
                    "The result is <strong>[4, 7, 2, 9, 6, 3, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge trees
    "merge-two-binary-trees": {
        "example": {"call": "level_order(merge_trees(build([1, 3, 2, 5]), build([2, 1, 3, None, 4, None, 7])))",
                    "expect": "[3, 4, 5, 5, 4, None, 7]"},
        "approaches": {
            "Recursive, reusing the first tree": {
                "idea": [
                    "Where both trees have a node, add the values into tree 1's node.",
                    "Where only one has a node, return that whole subtree as it is. That attaches it in O(1) without walking it.",
                ],
                "steps": [
                    "If either is None, return the other.",
                    "Otherwise add the values, and recurse into the left and right pairs.",
                ],
                "why": [
                    "Work happens only where both trees overlap: O(min(n, m)). It modifies tree 1.",
                ],
                "dry": [
                    "Roots: 1 + 2 = 3. Left: 3 + 1 = 4. Right: 2 + 3 = 5.",
                    "Under 4: left 5 vs None keeps 5; right None vs 4 takes 4. Under 5: right None vs 7 takes 7.",
                    "Level order: <strong>[3, 4, 5, 5, 4, None, 7]</strong>.",
                ],
            },
            "Non-destructive, allocating a new tree": {
                "idea": [
                    "Build a fresh node for every position, and copy any subtree that appears in only one tree.",
                    "Neither input is changed.",
                ],
                "steps": [
                    "Both present: <code>TreeNode(a + b)</code>; one present: <code>copy_tree</code>.",
                ],
                "why": [
                    "Every node of both trees is visited or copied: O(n + m) time and space.",
                ],
                "dry": [
                    "New nodes 3, 4 and 5 at the overlaps.",
                    "Copies of 5, 4 and 7 where only one tree has a node.",
                    "The result is <strong>[3, 4, 5, 5, 4, None, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subtree
    "subtree-of-another-tree": {
        "example": {"call": "is_subtree(build([3, 4, 5, 1, 2, None, None, None, None, 0]), build([4, 1, 2]))",
                    "expect": "False"},
        "approaches": {
            "Same-Tree at every node": {
                "idea": [
                    "A subtree means a node <em>and everything below it</em>, so it must match exactly, including the leaves.",
                    "Run the Same Tree check with every node of the host as a candidate root.",
                ],
                "steps": [
                    "If <code>same(root, sub)</code>, return True; otherwise try the left and right subtrees.",
                ],
                "why": [
                    "It is O(n·m) in the worst case (near-duplicate trees), and simple to get right.",
                ],
                "dry": [
                    "The host: 3 → (4, 5), 4 → (1, 2), and 2 has a left child 0.",
                    "At 3: the values differ. At 4: 4 = 4 and 1 = 1, but the 2 nodes differ, because the host's 2 has a child 0.",
                    "Nothing else matches. The result is <strong>False</strong>.",
                ],
            },
            "Serialise both, then substring search": {
                "idea": [
                    "Write each tree as a preorder string with <strong>null markers</strong> (<code>#</code>) and a value prefix (<code>^</code>).",
                    "A subtree then shows up as a <em>substring</em> of the host's string.",
                    "Without the markers, different shapes could produce the same string; without <code>^</code>, the value 2 would match inside 12.",
                ],
                "steps": [
                    "<code>serialise(sub) in serialise(root)</code>.",
                ],
                "why": [
                    "Building both strings takes O(n + m), and the substring search is linear in practice.",
                ],
                "dry": [
                    "sub = <code>^4(^1(##)^2(##))</code>.",
                    "The host's 4 subtree is <code>^4(^1(##)^2(^0(##)#))</code>, which is different.",
                    "The sub string never appears. The result is <strong>False</strong>.",
                ],
            },
        },
    },
}
