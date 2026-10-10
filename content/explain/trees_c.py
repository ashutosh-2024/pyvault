"""Write-ups for Trees, part C: views, construction, serialization, LCA."""

_LCA_T = "t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])"
_LCA_SHAPE = "The tree: 3 → (5, 1), 5 → (6, 2), 1 → (0, 8), 2 → (7, 4)."
_BST_T = "t = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])"
_BST_SHAPE = "The BST: 6 → (2, 8), 2 → (0, 4), 8 → (7, 9), 4 → (3, 5)."

EXPLAIN = {
    # ------------------------------------------------------------------ right side view
    "right-side-view": {
        "examples": [
            {"call": "right_side_view(build([1, 2, 3, None, 5, None, 4]))", "expect": "[1, 3, 4]"},
            {"call": "right_side_view(build([1, 2, 3, 4]))", "expect": "[1, 3, 4]"},
        ],
        "approaches": {
            "BFS, keep the last node of each level": {
                "idea": [
                    "Looking from the right you see exactly one node per level: the rightmost node of that level.",
                    "A level-by-level BFS that pushes the left child before the right child meets each level's nodes from left to right, so the <em>last</em> node popped in a level is the visible one.",
                    "The visible node need not be a right child: if a level has only one node far on the left, that node is still the rightmost of its level.",
                ],
                "steps": [
                    "Start <code>queue</code> with the root (or empty for an empty tree) and an empty list <code>view</code>.",
                    "While the queue is not empty, read <code>len(queue)</code>: that is exactly the number of nodes on the current level.",
                    "Pop that many nodes, pushing each node's non-empty children in the order left, right.",
                    "When the inner loop ends, <code>node</code> still holds the last node popped, the rightmost of the level: append <code>node.val</code> to <code>view</code>.",
                    "Return <code>view</code> once the queue runs dry.",
                ],
                "why": [
                    "Freezing the count with <code>range(len(queue))</code> before popping keeps levels apart: children pushed during the loop belong to the next level and are not counted.",
                    "Within a level, nodes come out in left-to-right order because parents are processed left to right and push left before right, so the last one popped is the rightmost.",
                    "Every node is pushed and popped once: <strong>O(n)</strong> time.",
                    "The queue holds at most two neighbouring levels, so space is <strong>O(w)</strong>, where w is the widest level (up to about n/2 in a full tree).",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 has only a right child 5, 3 has only a right child 4.",
                        "Level 1: queue [1], pop 1, push 2 and 3. Last popped is 1, view = [1].",
                        "Level 2: size 2. Pop 2 (push 5), pop 3 (push 4). Last popped is 3, view = [1, 3].",
                        "Level 3: size 2. Pop 5, then 4. Last popped is 4, view = [1, 3, 4].",
                        "The queue is empty, so it returns <strong>[1, 3, 4]</strong>.",
                    ],
                    [
                        "The tree: 1 → (2, 3), 2 has a left child 4, 3 is a leaf.",
                        "Level 1: pop 1, push 2 and 3. view = [1].",
                        "Level 2: pop 2 (push 4), pop 3 (no children). view = [1, 3].",
                        "Level 3: only 4 is there, so it is the last popped. view = [1, 3, 4], even though 4 sits on the left side.",
                        "It returns <strong>[1, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>node</code> still defined after the inner loop?",
                     "Python loop variables survive the loop. After the last iteration <code>node</code> is the final node popped on that level, which is exactly the one we want."],
                    ["How would I get the left side view instead?",
                     "Keep the <em>first</em> node popped on each level rather than the last, or push the right child before the left and keep the last."],
                    ["Why not just follow right children from the root?",
                     "A level may have no right-side node at all. In <code>[1, 2, 3, 4]</code> the deepest level is only the left grandchild 4, and walking right from the root would never see it."],
                ],
            },
            "DFS right-first, first node per depth": {
                "idea": [
                    "If the DFS always goes right before left, the first node it reaches at any depth is the rightmost node at that depth.",
                    "<code>view</code> has one entry per depth already seen, so <code>depth == len(view)</code> is true exactly on the first arrival at a new depth.",
                    "No queue and no level bookkeeping: the depth parameter plays the role of the level.",
                ],
                "steps": [
                    "Create an empty list <code>view</code>.",
                    "Define <code>dfs(node, depth)</code>, which returns at once for <code>None</code>.",
                    "If <code>depth == len(view)</code>, this depth has never been reached: append <code>node.val</code>.",
                    "Recurse into <code>node.right</code> first, then <code>node.left</code>, both with <code>depth + 1</code>.",
                    "Call <code>dfs(root, 0)</code> and return <code>view</code>.",
                ],
                "why": [
                    "Right-first preorder visits the nodes of any one depth in right-to-left order, so the first one recorded is the rightmost.",
                    "Depths are discovered in increasing order (a node at depth d+1 is only reached through one at depth d), so <code>view[d]</code> always belongs to depth d.",
                    "Each node is visited once with O(1) work: <strong>O(n)</strong> time.",
                    "The recursion stack is as deep as the tree, <strong>O(h)</strong> space beyond the output; for a skewed tree h = n.",
                ],
                "dry": [
                    [
                        "dfs(1, 0): len(view) = 0, record 1. view = [1].",
                        "Right first: dfs(3, 1): new depth, record 3. view = [1, 3].",
                        "dfs(4, 2) (3's right child): new depth, record 4. view = [1, 3, 4].",
                        "Back at 1, go left: dfs(2, 1) and dfs(5, 2) find depths 1 and 2 already filled, so nothing is recorded.",
                        "It returns <strong>[1, 3, 4]</strong>.",
                    ],
                    [
                        "dfs(1, 0) records 1; dfs(3, 1) records 3. 3 has no children.",
                        "dfs(2, 1): depth 1 is taken, skip. 2 has no right child.",
                        "dfs(4, 2): len(view) = 2, so depth 2 is new. Record 4.",
                        "It returns <strong>[1, 3, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>depth == len(view)</code> and not a set of seen depths?",
                     "Depths are first reached in order 0, 1, 2, … so the list length is always the next unseen depth. A set would work but carries no extra information."],
                    ["What happens if I recurse left first?",
                     "Then the first node at each depth is the leftmost, and you get the left side view instead."],
                    ["Is DFS or BFS better here?",
                     "Both are O(n). DFS uses O(h) stack and BFS uses O(w) queue: DFS wins on wide bushy trees, BFS on long thin ones, and BFS cannot hit Python's recursion limit."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ top / bottom view
    "top-bottom-view": {
        "examples": [
            {"call": "top_and_bottom_view(build([1, 2, 3, 4, 5, 6, 7]))", "expect": "([4, 2, 1, 3, 7], [4, 2, 6, 3, 7])"},
            {"call": "top_and_bottom_view(build([1, 2, 3, None, 4, None, None, None, 5, None, 6]))", "expect": "([2, 1, 3, 6], [2, 4, 5, 6])"},
        ],
        "approaches": {
            "BFS with column numbers": {
                "idea": [
                    "Give every node a horizontal column: the root is 0, a left child is <code>col - 1</code>, a right child is <code>col + 1</code>. Nodes in one column stack on top of each other.",
                    "BFS reaches nodes from the top level down, so the <em>first</em> node seen in a column is the one visible from above and the <em>last</em> one seen is the one visible from below.",
                    "Two dictionaries keyed by column collect both views in a single pass.",
                ],
                "steps": [
                    "Return <code>([], [])</code> for an empty tree; otherwise start <code>queue</code> with <code>(root, 0)</code>.",
                    "Pop <code>(node, col)</code>. <code>top.setdefault(col, node.val)</code> stores the value only if the column is new.",
                    "<code>bottom[col] = node.val</code> overwrites unconditionally, so later (deeper) nodes replace earlier ones.",
                    "Push the left child with <code>col - 1</code> and the right child with <code>col + 1</code>.",
                    "Columns form one unbroken range, so read <code>range(min(top), max(top) + 1)</code> and return the two lists in column order.",
                ],
                "why": [
                    "BFS pops nodes in non-decreasing depth, so the first node popped in a column is the shallowest one there (top view) and the last is the deepest (bottom view).",
                    "When two nodes share a depth and a column, the one popped later (further right in the level) wins for the bottom view, which is the usual convention.",
                    "Each node is handled once with O(1) dictionary work: <strong>O(n)</strong> time.",
                    "The queue and the two dictionaries can each hold O(n) entries: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Columns: 1 at 0; 2 at −1, 3 at 1; 4 at −2, 5 at 0, 6 at 0, 7 at 2.",
                        "Pop 1, 2, 3: each starts a new column, so top = bottom = {0: 1, −1: 2, 1: 3}.",
                        "Pop 4 (col −2) and 7 (col 2): new columns in both maps.",
                        "Pop 5 and then 6, both in column 0: top keeps 1, bottom becomes 5 and then 6.",
                        "Columns −2..2 give <strong>([4, 2, 1, 3, 7], [4, 2, 6, 3, 7])</strong>.",
                    ],
                    [
                        "The tree is 1 → (2, 3), then a right-only chain 2 → 4 → 5 → 6.",
                        "Columns: 1 at 0, 2 at −1, 3 at 1, 4 at 0, 5 at 1, 6 at 2.",
                        "Pop order 1, 2, 3, 4, 5, 6. top keeps 1 (col 0) and 3 (col 1); bottom is overwritten by 4 (col 0) and 5 (col 1).",
                        "Column 2 holds only 6, so it appears in both views.",
                        "Columns −1..2 give <strong>([2, 1, 3, 6], [2, 4, 5, 6])</strong>.",
                    ],
                ],
                "faq": [
                    ["Why BFS and not a plain DFS?",
                     "DFS can reach a deep node in a column before a shallow one, so \"first seen\" would not mean \"highest\". A DFS version has to store the depth too and compare."],
                    ["Can columns have gaps, making <code>range(min, max + 1)</code> unsafe?",
                     "No. Every child's column is its parent's ±1, so the columns used always form one continuous range."],
                    ["Why <code>setdefault</code> for top but plain assignment for bottom?",
                     "<code>setdefault</code> writes only the first time a key appears, which keeps the shallowest node. Assignment keeps the most recent one, which is the deepest."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ bottom-left value
    "bottom-left-value": {
        "examples": [
            {"call": "find_bottom_left_value(build([1, 2, 3, 4, None, 5, 6, None, None, 7]))", "expect": "7"},
            {"call": "find_bottom_left_value(build([1, None, 2, None, 3]))", "expect": "3"},
        ],
        "approaches": {
            "BFS right-to-left, last node wins": {
                "idea": [
                    "A BFS pops nodes level by level. If each node pushes its <em>right</em> child before its left, every level comes out right to left.",
                    "Then the very last node popped is on the deepest level and is the leftmost one there: exactly the answer.",
                    "No level sizes and no depth counter are needed.",
                ],
                "steps": [
                    "Start <code>queue</code> with the root.",
                    "Pop a node.",
                    "Push <code>node.right</code> if present, then <code>node.left</code> if present.",
                    "Repeat until the queue is empty.",
                    "Return <code>node.val</code>, the last node popped.",
                ],
                "why": [
                    "BFS order is sorted by depth, so the last node popped lies on the deepest level.",
                    "Pushing right before left reverses the order within each level, so the last node of the deepest level is its leftmost node.",
                    "Each node enters and leaves the queue once: <strong>O(n)</strong> time.",
                    "The queue holds at most about two levels: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 → (4, ·), 3 → (5, 6), 5 → (7, ·).",
                        "Pop 1, push 3 then 2. Pop 3, push 6 then 5. Pop 2, push 4.",
                        "Queue is now [6, 5, 4]: level 2 read right to left.",
                        "Pop 6. Pop 5, push 7. Pop 4. Pop 7, and the queue is empty.",
                        "The last node popped is 7: <strong>7</strong>.",
                    ],
                    [
                        "The tree is a right-only chain 1 → 2 → 3.",
                        "Pop 1, push 2. Pop 2, push 3. Pop 3, nothing to push.",
                        "The deepest level holds only 3, so it is also the leftmost.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong if I push left before right?",
                     "The last node popped becomes the <em>rightmost</em> of the deepest level, so you would solve the bottom-right problem instead."],
                    ["What if the root is <code>None</code>?",
                     "The problem guarantees at least one node. With <code>None</code>, the loop would try <code>None.right</code> and crash."],
                    ["Why does the answer here have to be a right child?",
                     "It does not have to be. \"Leftmost\" means leftmost on its level; in the chain 1 → 2 → 3, node 3 is the only node on the bottom level, so it is the answer."],
                ],
            },
            "DFS left-first, first node at a new depth": {
                "idea": [
                    "A preorder that goes left before right meets the nodes of each depth in left-to-right order.",
                    "So the first node that reaches a depth deeper than anything seen so far is the leftmost node of that depth.",
                    "Remember the deepest depth so far in <code>best_depth</code> and its first node's value in <code>best</code>; the final value belongs to the deepest level.",
                ],
                "steps": [
                    "Set <code>best_depth = -1</code> and <code>best = None</code>.",
                    "<code>dfs(node, depth)</code> returns at once for <code>None</code>.",
                    "If <code>depth &gt; best_depth</code>, store <code>best_depth, best = depth, node.val</code>.",
                    "Recurse into <code>node.left</code>, then <code>node.right</code>, with <code>depth + 1</code>.",
                    "Call <code>dfs(root, 0)</code> and return <code>best</code>.",
                ],
                "why": [
                    "The strict <code>&gt;</code> means later nodes on an already-seen depth never overwrite it, and left-first order guarantees the first one there is the leftmost.",
                    "At the end <code>best_depth</code> is the maximum depth, so <code>best</code> is the leftmost node on the bottom level.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth equals the tree height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "dfs(1, 0): 0 &gt; −1, best = 1. dfs(2, 1): best = 2. dfs(4, 2): best = 4.",
                        "4 and 2 have no more children. Back to 1's right: dfs(3, 1) is not deeper than 2.",
                        "dfs(5, 2): depth 2 is not &gt; 2, skip. dfs(7, 3): 3 &gt; 2, best = 7.",
                        "dfs(6, 2): not deeper.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "dfs(1, 0): best = 1. Left is None.",
                        "dfs(2, 1): best = 2. Left is None.",
                        "dfs(3, 2): best = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt;</code> and not <code>&gt;=</code>?",
                     "With <code>&gt;=</code> every later node on the deepest level would overwrite <code>best</code>, giving the rightmost node instead of the leftmost."],
                    ["Why <code>nonlocal</code>?",
                     "The inner function assigns to <code>best_depth</code> and <code>best</code>. Without <code>nonlocal</code> Python would treat them as new local variables of <code>dfs</code>."],
                    ["Which approach should I prefer?",
                     "They are both O(n). The BFS is shorter and has no recursion limit; the DFS uses less memory on wide trees."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add one row
    "add-one-row": {
        "examples": [
            {"call": "level_order(add_one_row(build([4, 2, 6, 3, 1, 5]), 1, 3))", "expect": "[4, 2, 6, 1, 1, 1, 1, 3, None, None, 1, 5]"},
            {"call": "level_order(add_one_row(build([1, 2, 3]), 9, 1))", "expect": "[9, 1, None, 2, 3]"},
        ],
        "approaches": {
            "BFS to the level above, then splice": {
                "idea": [
                    "The new row sits at <code>depth</code>, so the nodes that change are the ones at <code>depth - 1</code>: each gets two new children.",
                    "The new left child adopts the old left subtree as <em>its</em> left; the new right child adopts the old right subtree as <em>its</em> right.",
                    "<code>depth == 1</code> has no level above it, so it is a special case: the new node becomes the root with the old tree on its left.",
                ],
                "steps": [
                    "If <code>depth == 1</code>, return <code>TreeNode(val, root, None)</code>.",
                    "Start <code>level = [root]</code>, which is depth 1.",
                    "Step down <code>depth - 2</code> times, replacing <code>level</code> with the list of its non-empty children. <code>level</code> is now the nodes at depth − 1.",
                    "For each <code>node</code> in <code>level</code>: <code>node.left = TreeNode(val, node.left, None)</code> and <code>node.right = TreeNode(val, None, node.right)</code>.",
                    "Return the original <code>root</code>.",
                ],
                "why": [
                    "Every node at depth − 1 gets both new children, even when its old child slot was empty, which is what the problem asks.",
                    "Each old subtree is reattached on the same side it came from, so nothing below the new row changes shape.",
                    "Only levels above the new row are visited, at most once each: <strong>O(n)</strong> time.",
                    "<code>level</code> holds one level of nodes at a time: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 4 → (2, 6), 2 → (3, 1), 6 → (5, ·). Insert 1s at depth 3.",
                        "level = [4]. One step down (depth − 2 = 1): level = [2, 6].",
                        "Node 2: new left 1 holding 3, new right 1 holding the old 1.",
                        "Node 6: new left 1 holding 5, new right 1 with nothing below (6 had no right child).",
                        "The level order is <strong>[4, 2, 6, 1, 1, 1, 1, 3, None, None, 1, 5]</strong>.",
                    ],
                    [
                        "depth == 1, so no level is walked.",
                        "A new node 9 is created with the whole old tree as its left child.",
                        "The old root 1 keeps its children 2 and 3.",
                        "It returns <strong>[9, 1, None, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>depth - 2</code> steps?",
                     "<code>level</code> starts at depth 1 and must end at depth − 1. That is <code>(depth - 1) - 1 = depth - 2</code> steps down."],
                    ["Should a node with no children still get the new row?",
                     "Yes. Every node at depth − 1 gets two new children with value <code>val</code>; the old (empty) subtrees hang below them."],
                    ["What if <code>depth</code> is one more than the tree's height?",
                     "Then <code>level</code> is the bottom level and the new row becomes a row of leaves, as in the problem's examples. The splice code handles it with no special case."],
                ],
            },
            "DFS carrying the depth": {
                "idea": [
                    "Walk down with the current depth <code>d</code>. Only nodes at <code>d == depth - 1</code> need changing.",
                    "At such a node, splice in the two new children and stop: nothing below needs to be visited.",
                    "The depth-1 case is handled before the walk, as in the BFS version.",
                ],
                "steps": [
                    "If <code>depth == 1</code>, return a new root with the old tree on its left.",
                    "<code>dfs(node, d)</code> returns at once for <code>None</code>.",
                    "If <code>d == depth - 1</code>, set <code>node.left = TreeNode(val, node.left, None)</code> and <code>node.right = TreeNode(val, None, node.right)</code>, then return.",
                    "Otherwise recurse into both children with <code>d + 1</code>.",
                    "Call <code>dfs(root, 1)</code> and return <code>root</code>.",
                ],
                "why": [
                    "Every node at depth − 1 is reached because the DFS explores all nodes above it, and each one is spliced exactly once.",
                    "Returning right after the splice means the walk never goes into the new nodes or the old subtrees below them, which could not match <code>depth - 1</code> anyway.",
                    "At most every node above the new row is visited: <strong>O(n)</strong> time.",
                    "Recursion depth is at most <code>depth - 1</code> ≤ h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "dfs(4, 1): 1 ≠ 2, recurse.",
                        "dfs(2, 2): d == 2, splice. 2.left = 1(3, ·), 2.right = 1(·, 1). Return.",
                        "dfs(6, 2): splice. 6.left = 1(5, ·), 6.right = 1(·, ·). Return.",
                        "Nodes 3, 1 and 5 are never visited.",
                        "The level order is <strong>[4, 2, 6, 1, 1, 1, 1, 3, None, None, 1, 5]</strong>.",
                    ],
                    [
                        "depth == 1: the DFS is never called.",
                        "Return <code>TreeNode(9, root, None)</code>.",
                        "It returns <strong>[9, 1, None, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the DFS start with <code>d = 1</code>?",
                     "The problem numbers the root's level as depth 1, so the counter must match that convention for <code>d == depth - 1</code> to hit the right level."],
                    ["Why the extra <code>None</code> in <code>TreeNode(val, node.left, None)</code>?",
                     "It makes the side explicit: the new left node keeps the old subtree on its left and has no right child. The right splice mirrors it."],
                    ["Could the DFS run into the nodes it just created?",
                     "Not with the early <code>return</code>: once a node is spliced its children are not visited at all."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ average of levels
    "average-of-levels": {
        "examples": [
            {"call": "average_of_levels(build([3, 9, 20, None, None, 15, 7]))", "expect": "[3.0, 14.5, 11.0]"},
            {"call": "average_of_levels(build([5, 2, -4, None, 1]))", "expect": "[5.0, -1.0, 1.0]"},
        ],
        "approaches": {
            "BFS, one level at a time": {
                "idea": [
                    "An average needs the sum and the count of one level, and a level-by-level BFS sees exactly one level per outer iteration.",
                    "The number of nodes on the level is <code>len(queue)</code> at the start of the iteration, so it doubles as the count.",
                    "Add up the values while popping, then divide once.",
                ],
                "steps": [
                    "Start <code>queue</code> with the root (or empty) and <code>out = []</code>.",
                    "At the start of each round set <code>size = len(queue)</code> and <code>total = 0</code>.",
                    "Pop <code>size</code> nodes, adding each <code>node.val</code> to <code>total</code> and pushing its non-empty children.",
                    "Append <code>total / size</code> to <code>out</code>.",
                    "Return <code>out</code> when the queue is empty.",
                ],
                "why": [
                    "<code>size</code> is fixed before popping, so children pushed during the round are counted in the next level only.",
                    "Each level's sum and count are therefore exact, and <code>/</code> gives a float average.",
                    "Every node is processed once: <strong>O(n)</strong> time.",
                    "The queue holds at most two levels: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 3 → (9, 20), 20 → (15, 7).",
                        "Round 1: size 1, total 3. out = [3.0]. Queue [9, 20].",
                        "Round 2: size 2, total 9 + 20 = 29. out = [3.0, 14.5]. Queue [15, 7].",
                        "Round 3: size 2, total 22. out = [3.0, 14.5, 11.0].",
                        "It returns <strong>[3.0, 14.5, 11.0]</strong>.",
                    ],
                    [
                        "The tree: 5 → (2, −4), 2 → (·, 1).",
                        "Round 1: total 5, size 1 → 5.0.",
                        "Round 2: total 2 + (−4) = −2, size 2 → −1.0.",
                        "Round 3: only node 1 → 1.0.",
                        "It returns <strong>[5.0, -1.0, 1.0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Could the sum overflow?",
                     "Not in Python, whose integers grow as needed. In Java or C++ the sum of large values must be kept in a 64-bit type or a double."],
                    ["Why <code>/</code> and not <code>//</code>?",
                     "The answer is a real average such as 14.5. <code>//</code> would round it down to 14."],
                    ["Can <code>size</code> ever be 0 in the division?",
                     "No. The loop only runs while the queue is non-empty, so every level has at least one node."],
                ],
            },
            "DFS with per-depth sums and counts": {
                "idea": [
                    "The order of visits does not matter for a sum, so any traversal works as long as each node's value is added to the right level.",
                    "Keep two lists indexed by depth: <code>sums[d]</code> and <code>counts[d]</code>.",
                    "When the DFS reaches a depth for the first time, extend both lists with a fresh 0.",
                ],
                "steps": [
                    "Create empty lists <code>sums</code> and <code>counts</code>.",
                    "<code>dfs(node, depth)</code> returns at once for <code>None</code>.",
                    "If <code>depth == len(sums)</code>, this depth is new: append 0 to both lists.",
                    "Add <code>node.val</code> to <code>sums[depth]</code> and 1 to <code>counts[depth]</code>, then recurse into both children with <code>depth + 1</code>.",
                    "After <code>dfs(root, 0)</code>, return <code>[s / c for s, c in zip(sums, counts)]</code>.",
                ],
                "why": [
                    "Every node adds itself to exactly one slot, the slot for its own depth, so each level's sum and count are complete at the end.",
                    "Depths are reached in increasing order, so appending when <code>depth == len(sums)</code> keeps the index and the depth aligned.",
                    "One visit per node and one pass over the levels: <strong>O(n)</strong> time.",
                    "Recursion stack O(h) plus two lists of length h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "dfs(3, 0): new depth. sums = [3], counts = [1].",
                        "dfs(9, 1): new depth. sums = [3, 9], counts = [1, 1].",
                        "dfs(20, 1): sums = [3, 29], counts = [1, 2].",
                        "dfs(15, 2): new depth, sums = [3, 29, 15]. dfs(7, 2): sums = [3, 29, 22], counts = [1, 2, 2].",
                        "Dividing gives <strong>[3.0, 14.5, 11.0]</strong>.",
                    ],
                    [
                        "dfs(5, 0): sums = [5]. dfs(2, 1): sums = [5, 2].",
                        "2 has only a right child: dfs(1, 2) makes sums = [5, 2, 1].",
                        "dfs(−4, 1): sums = [5, −2, 1], counts = [1, 2, 1].",
                        "It returns <strong>[5.0, -1.0, 1.0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can I append rather than insert at index <code>depth</code>?",
                     "A node at depth d is only reached through its parent at depth d − 1, so depth d − 1 already has a slot by then. The new depth is always exactly <code>len(sums)</code>."],
                    ["Why not keep one list of lists of values per depth?",
                     "That stores all n values. Two running numbers per depth are enough for an average."],
                    ["What does <code>sums.append(0); counts.append(0)</code> on one line do?",
                     "It is two statements separated by a semicolon; both lists grow together so they always have the same length."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ deepest leaves sum
    "deepest-leaves-sum": {
        "examples": [
            {"call": "deepest_leaves_sum(build([1, 2, 3, 4, 5, None, 6, 7, None, None, None, None, 8]))", "expect": "15"},
            {"call": "deepest_leaves_sum(build([1, 2, 3, 4]))", "expect": "4"},
        ],
        "approaches": {
            "BFS, the last level's sum": {
                "idea": [
                    "The deepest leaves are simply all the nodes of the last level.",
                    "Walk the tree level by level, summing each level as it goes. The sum computed last is the answer.",
                    "Building the next level as a list comprehension keeps the code to three lines.",
                ],
                "steps": [
                    "Start with <code>level = [root]</code>.",
                    "While <code>level</code> is not empty, set <code>total</code> to the sum of its values.",
                    "Replace <code>level</code> with all non-empty children of its nodes, in order.",
                    "When the next level comes out empty, the loop stops; <code>total</code> still holds the last level's sum.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "Every node on the last level is a leaf (it has no children, or there would be another level), and every deepest leaf is on that level.",
                    "<code>total</code> is overwritten once per level, so after the loop it belongs to the final non-empty level.",
                    "Each node is summed once and expanded once: <strong>O(n)</strong> time.",
                    "Two levels are alive at a time: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 → (4, 5), 3 → (·, 6), 4 → (7, ·), 6 → (·, 8).",
                        "level [1]: total 1. level [2, 3]: total 5.",
                        "level [4, 5, 6]: total 15. Leaf 5 is here, but it is not the deepest.",
                        "level [7, 8]: total 15. The next level is empty, so the loop stops.",
                        "It returns <strong>15</strong>.",
                    ],
                    [
                        "level [1]: total 1. level [2, 3]: total 5.",
                        "level [4]: total 4. Leaf 3 was on the previous level and is left out.",
                        "The next level is empty.",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>total</code> defined after the loop?",
                     "The tree has at least one node, so the loop body runs at least once and <code>total</code> is always assigned."],
                    ["Do I need to check that the nodes are leaves?",
                     "No. A node on the last level cannot have children, otherwise the level below would be non-empty."],
                    ["Is the list comprehension slower than a deque?",
                     "No. Each level is built once from the previous one, so there are no expensive pops from the front at all."],
                ],
            },
            "One-pass DFS with a reset": {
                "idea": [
                    "Keep the deepest depth seen so far, <code>deepest</code>, and the sum of nodes at that depth, <code>total</code>.",
                    "Reaching a node deeper than <code>deepest</code> means everything summed so far is too shallow: reset <code>total</code> to 0 and adopt the new depth.",
                    "Nodes on the current deepest depth are added; nodes above it are ignored.",
                ],
                "steps": [
                    "Set <code>deepest = -1</code> and <code>total = 0</code>.",
                    "<code>dfs(node, depth)</code> returns at once for <code>None</code>.",
                    "If <code>depth &gt; deepest</code>, set <code>deepest = depth</code> and <code>total = 0</code>.",
                    "If <code>depth == deepest</code>, add <code>node.val</code> to <code>total</code>.",
                    "Recurse into both children with <code>depth + 1</code>; after <code>dfs(root, 0)</code> return <code>total</code>.",
                ],
                "why": [
                    "When the DFS ends, <code>deepest</code> is the maximum depth, and <code>total</code> has been reset after the last time that depth grew.",
                    "Every node at the maximum depth is visited after that reset (the reset happens at the first such node), so all of them are added.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "1 (d0): deepest 0, total 1. 2 (d1): reset, total 2. 4 (d2): reset, total 4.",
                        "7 (d3): reset, total 7.",
                        "5 (d2), 3 (d1), 6 (d2): all shallower than 3, ignored.",
                        "8 (d3): equal to deepest, total = 7 + 8 = 15.",
                        "It returns <strong>15</strong>.",
                    ],
                    [
                        "1 (d0): total 1. 2 (d1): reset, total 2.",
                        "4 (d2): reset, total 4.",
                        "3 (d1): shallower than 2, ignored.",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why two separate <code>if</code>s instead of <code>if / elif</code>?",
                     "After a reset the current node is itself on the new deepest level and must be added. The second <code>if</code> runs right after the first one does exactly that."],
                    ["Why start <code>deepest</code> at −1?",
                     "So the root at depth 0 counts as deeper and triggers the first reset, with no special case."],
                    ["Does the DFS order matter?",
                     "No. Any order that visits every node with its correct depth gives the same final sum; resets just happen at different moments."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ preorder + inorder
    "build-from-preorder-inorder": {
        "examples": [
            {"call": "level_order(build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]))", "expect": "[3, 9, 20, None, None, 15, 7]"},
            {"call": "level_order(build_tree([1, 2, 3], [3, 2, 1]))", "expect": "[1, 2, None, 3]"},
        ],
        "approaches": {
            "Index map and a moving preorder pointer": {
                "idea": [
                    "Preorder lists a root before its subtrees, so the next unused preorder value is always the root of the subtree being built.",
                    "That root's position <code>mid</code> in the inorder list splits it: everything left of <code>mid</code> is the left subtree, everything right is the right subtree.",
                    "A dictionary from value to inorder index finds <code>mid</code> in O(1), and a single pointer <code>nxt</code> into preorder replaces all slicing.",
                ],
                "steps": [
                    "Build <code>where = {value: inorder index}</code> and set <code>nxt = 0</code>.",
                    "<code>make(lo, hi)</code> builds the subtree whose inorder values are <code>inorder[lo..hi]</code>; it returns <code>None</code> when <code>lo &gt; hi</code>.",
                    "Take <code>val = preorder[nxt]</code>, advance <code>nxt</code>, and look up <code>mid = where[val]</code>.",
                    "Build <code>node.left = make(lo, mid - 1)</code> <em>first</em>, then <code>node.right = make(mid + 1, hi)</code>.",
                    "Return <code>make(0, len(inorder) - 1)</code>.",
                ],
                "why": [
                    "Preorder is root, whole left subtree, whole right subtree. Building the left subtree first consumes exactly its preorder values, leaving <code>nxt</code> on the right subtree's root.",
                    "Values must be distinct, otherwise <code>where[val]</code> could point at the wrong copy.",
                    "Each node is created once with O(1) work: <strong>O(n)</strong> time.",
                    "The dictionary is O(n) and the recursion depth is up to n for a skewed tree: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "where = {9: 0, 3: 1, 15: 2, 20: 3, 7: 4}.",
                        "make(0, 4): val 3, mid 1. Left make(0, 0): val 9, mid 0, both children empty.",
                        "Right make(2, 4): val 20, mid 3.",
                        "Its left make(2, 2) takes 15; its right make(4, 4) takes 7.",
                        "The tree 3 → (9, 20), 20 → (15, 7): <strong>[3, 9, 20, None, None, 15, 7]</strong>.",
                    ],
                    [
                        "where = {3: 0, 2: 1, 1: 2}.",
                        "make(0, 2): val 1, mid 2. The left range is 0..1, the right range 3..2 is empty.",
                        "make(0, 1): val 2, mid 1. Left make(0, 0) takes 3; right make(2, 1) is empty.",
                        "Every node hangs to the left: 1 → 2 → 3.",
                        "It returns <strong>[1, 2, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the left subtree be built before the right?",
                     "<code>nxt</code> walks preorder in order, and preorder lists the whole left subtree before the right one. Building right first would take left-subtree values for the right side."],
                    ["What if values repeat?",
                     "Then the tree is not uniquely determined and <code>where</code> keeps only the last index of each value, so the build can go wrong. The problem promises distinct values."],
                    ["Why use <code>lo</code>/<code>hi</code> instead of slicing the lists?",
                     "Slices copy, which costs O(n) per call and O(n²) overall. Index bounds cost nothing."],
                ],
            },
            "Slice and search": {
                "idea": [
                    "The direct recursive definition: the first preorder value is the root; find it in inorder to learn the left subtree's size <code>mid</code>.",
                    "Then the next <code>mid</code> preorder values are the left subtree and the rest are the right subtree, so both sides can be sliced out and solved recursively.",
                    "Simple to write and to check, but every call copies and searches.",
                ],
                "steps": [
                    "If <code>preorder</code> is empty, return <code>None</code>.",
                    "Create <code>root</code> from <code>preorder[0]</code>.",
                    "Find <code>mid = inorder.index(preorder[0])</code>: the number of values in the left subtree.",
                    "Build the left child from <code>preorder[1:mid + 1]</code> and <code>inorder[:mid]</code>.",
                    "Build the right child from <code>preorder[mid + 1:]</code> and <code>inorder[mid + 1:]</code>, then return <code>root</code>.",
                ],
                "why": [
                    "Both lists describe the same set of nodes, and the slices split both lists into the same left and right sets, so each recursive call gets a valid pair.",
                    "Each call does an O(k) search and O(k) slicing for a subtree of size k; on a skewed tree k runs n, n−1, …, giving <strong>O(n²)</strong> time.",
                    "The copied slices along one root-to-leaf path can add up to n + (n−1) + …, which is <strong>O(n²)</strong> space in the worst case.",
                ],
                "dry": [
                    [
                        "Root 3, mid = 1: left gets [9] / [9], right gets [20, 15, 7] / [15, 20, 7].",
                        "Left: root 9, mid 0, both sides empty.",
                        "Right: root 20, mid 1: left [15] / [15], right [7] / [7].",
                        "Each one-element call makes a leaf.",
                        "It returns <strong>[3, 9, 20, None, None, 15, 7]</strong>.",
                    ],
                    [
                        "Root 1, mid = inorder.index(1) = 2: left gets [2, 3] / [3, 2], right gets [] / [].",
                        "Root 2, mid = 1: left gets [3] / [3], right is empty.",
                        "Root 3 is a leaf.",
                        "It returns <strong>[1, 2, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the left preorder slice <code>[1:mid + 1]</code>?",
                     "Index 0 is the root, and the left subtree has <code>mid</code> nodes, so its preorder occupies indices 1 through <code>mid</code>."],
                    ["Is <code>mid</code> an index or a size?",
                     "Both: in the current inorder slice, the root's index equals the number of values to its left, which is the left subtree's size."],
                    ["When is this acceptable?",
                     "For small inputs or as a first draft in an interview. For n in the thousands, switch to the index map and pointer version."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ inorder + postorder
    "build-from-inorder-postorder": {
        "examples": [
            {"call": "level_order(build_tree([9, 3, 15, 20, 7], [9, 15, 7, 20, 3]))", "expect": "[3, 9, 20, None, None, 15, 7]"},
            {"call": "level_order(build_tree([1, 2, 3], [3, 2, 1]))", "expect": "[1, None, 2, None, 3]"},
        ],
        "approaches": {
            "Index map, consume postorder from the end": {
                "idea": [
                    "Postorder ends with the root. Read backwards it is root, right subtree, left subtree: a mirrored preorder.",
                    "So take roots from the end of <code>postorder</code>, and split each one at its inorder position exactly as in the preorder version.",
                    "Because of the mirroring, the <em>right</em> subtree must be built before the left one.",
                ],
                "steps": [
                    "Build <code>where = {value: inorder index}</code> and set <code>nxt = len(postorder) - 1</code>.",
                    "<code>make(lo, hi)</code> builds the subtree for <code>inorder[lo..hi]</code>, returning <code>None</code> when <code>lo &gt; hi</code>.",
                    "Take <code>val = postorder[nxt]</code>, step <code>nxt</code> down by one, and find <code>mid = where[val]</code>.",
                    "Build <code>node.right = make(mid + 1, hi)</code> first, then <code>node.left = make(lo, mid - 1)</code>.",
                    "Return <code>make(0, len(inorder) - 1)</code>.",
                ],
                "why": [
                    "Reading postorder from the end visits root, then the whole right subtree, then the whole left subtree, so the right-first order consumes values in the order they appear.",
                    "The inorder split guarantees each recursive call gets exactly the nodes of one subtree.",
                    "Each node costs O(1): <strong>O(n)</strong> time.",
                    "The map plus a recursion depth of up to n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "where = {9: 0, 3: 1, 15: 2, 20: 3, 7: 4}, nxt = 4.",
                        "make(0, 4): val 3, mid 1. Right first: make(2, 4) takes 20, mid 3.",
                        "Inside 20: right make(4, 4) takes 7, then left make(2, 2) takes 15.",
                        "Back at 3: left make(0, 0) takes 9, the last value (nxt reaches −1).",
                        "It returns <strong>[3, 9, 20, None, None, 15, 7]</strong>.",
                    ],
                    [
                        "where = {1: 0, 2: 1, 3: 2}, nxt = 2.",
                        "make(0, 2): val 1, mid 0. Right make(1, 2): val 2, mid 1.",
                        "Right make(2, 2): val 3, a leaf. Every left range is empty.",
                        "The tree is the right-leaning chain 1 → 2 → 3.",
                        "It returns <strong>[1, None, 2, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["What breaks if I build the left subtree first?",
                     "The value at <code>postorder[nxt]</code> belongs to the right subtree, so the left subtree would be built from the wrong values and the tree comes out scrambled."],
                    ["Why does inorder have to be one of the two lists?",
                     "Inorder is what separates left from right. With only preorder and postorder, a node with one child cannot tell which side the child is on."],
                    ["Does this need distinct values?",
                     "Yes, for the same reason as the preorder version: <code>where</code> must map each value to one inorder position."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ preorder + postorder
    "build-from-preorder-postorder": {
        "examples": [
            {"call": "level_order(construct_from_pre_post([1, 2, 4, 5, 3, 6, 7], [4, 5, 2, 6, 7, 3, 1]))", "expect": "[1, 2, 3, 4, 5, 6, 7]"},
            {"call": "level_order(construct_from_pre_post([1, 2, 3], [3, 2, 1]))", "expect": "[1, 2, None, 3]"},
        ],
        "approaches": {
            "Index map on postorder": {
                "idea": [
                    "<code>preorder[pre_lo]</code> is the root, and if the subtree has more than one node, <code>preorder[pre_lo + 1]</code> is the root of the left child.",
                    "In postorder that left child's root comes <em>last</em> among its subtree's values, so its postorder position tells how many nodes the left subtree has.",
                    "With that size, both lists can be split and each half built recursively. When a node has only one child, the code puts it on the left, one of the valid answers.",
                ],
                "steps": [
                    "Build <code>where = {value: postorder index}</code>.",
                    "<code>make(pre_lo, pre_hi, post_lo)</code> builds the subtree held in <code>preorder[pre_lo..pre_hi]</code>, whose postorder block starts at <code>post_lo</code>.",
                    "Empty range: return <code>None</code>. One value: return a leaf.",
                    "Otherwise <code>left_size = where[preorder[pre_lo + 1]] - post_lo + 1</code>.",
                    "Left child: <code>make(pre_lo + 1, pre_lo + left_size, post_lo)</code>. Right child: <code>make(pre_lo + left_size + 1, pre_hi, post_lo + left_size)</code>.",
                ],
                "why": [
                    "The left subtree's postorder block starts at <code>post_lo</code> and ends with its root, so the block's length is the root's index minus <code>post_lo</code>, plus 1.",
                    "The right subtree takes whatever is left in the preorder range, and its postorder block starts right after the left block.",
                    "Each node is created once with an O(1) lookup: <strong>O(n)</strong> time.",
                    "The map plus recursion depth up to n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "where: 4→0, 5→1, 2→2, 6→3, 7→4, 3→5, 1→6.",
                        "make(0, 6, 0): root 1. Left root is 2, at post index 2, so left_size = 3.",
                        "Left make(1, 3, 0): root 2, left root 4 at index 0, left_size 1. Leaves 4 and 5.",
                        "Right make(4, 6, 3): root 3, left root 6 at index 3, left_size 1. Leaves 6 and 7.",
                        "It returns <strong>[1, 2, 3, 4, 5, 6, 7]</strong>.",
                    ],
                    [
                        "where: 3→0, 2→1, 1→2.",
                        "make(0, 2, 0): root 1, left root 2 at index 1, left_size = 2. The right range 3..2 is empty.",
                        "make(1, 2, 0): root 2, left root 3 at index 0, left_size = 1. Leaf 3 on the left.",
                        "Each single child is placed on the left; putting it on the right would match both traversals too.",
                        "It returns <strong>[1, 2, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the answer not unique?",
                     "If a node has one child, preorder and postorder look the same whether that child is on the left or the right. Only inorder can tell them apart."],
                    ["Why is <code>pre_lo == pre_hi</code> a separate case?",
                     "With one value there is no <code>preorder[pre_lo + 1]</code> inside the range to read. Returning a leaf avoids reading the next subtree's value by mistake."],
                    ["Why pass <code>post_lo</code> and not <code>post_hi</code>?",
                     "Only the start of the block is needed to compute <code>left_size</code>; its end follows from the preorder range length."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ construct string from tree
    "construct-string-from-tree": {
        "examples": [
            {"call": "tree2str(build([1, 2, 3, None, 4]))", "expect": "'1(2()(4))(3)'"},
            {"call": "tree2str(build([1, 2, 3, 4]))", "expect": "'1(2(4))(3)'"},
        ],
        "approaches": {
            "Preorder with the empty-left rule": {
                "idea": [
                    "Write each node as its value followed by its children in brackets, in preorder.",
                    "Empty brackets are dropped wherever they are not needed: a leaf gets none, and a missing right child gets none.",
                    "A missing <em>left</em> child must keep its <code>()</code> when a right child exists, otherwise the right child would be read as the left one.",
                ],
                "steps": [
                    "Collect pieces in <code>parts</code> and define <code>walk(node)</code>.",
                    "Append <code>str(node.val)</code>. If the node is a leaf, return.",
                    "Append <code>(</code>, walk the left child if it exists, then append <code>)</code>. This writes <code>()</code> for a missing left child.",
                    "If the right child exists, append <code>(</code>, walk it, append <code>)</code>.",
                    "Return <code>\"\".join(parts)</code>.",
                ],
                "why": [
                    "Any non-leaf node always prints its left brackets, so the first bracket group after a value is always the left child and the string can be parsed back unambiguously.",
                    "The right group is printed only when it is non-empty, which removes every bracket pair that carries no information.",
                    "Each node appends O(1) pieces and the final join is linear: <strong>O(n)</strong> time.",
                    "The recursion is <strong>O(h)</strong> deep; the output list itself is O(n).",
                ],
                "dry": [
                    [
                        "walk(1): \"1\", not a leaf, \"(\".",
                        "walk(2): \"2\", not a leaf, \"(\", no left child, \")\". Right child 4: \"(4)\".",
                        "Back at 1: \")\", then the right child: \"(3)\".",
                        "The pieces join into 1 ( 2 () (4) ) (3).",
                        "It returns <strong>'1(2()(4))(3)'</strong>.",
                    ],
                    [
                        "walk(1): \"1(\". walk(2): \"2(\", then walk(4) writes \"4\" (a leaf), then \")\".",
                        "2 has no right child, so nothing more for 2.",
                        "Back at 1: \")\", then \"(3)\".",
                        "It returns <strong>'1(2(4))(3)'</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>()</code> stay for a missing left child?",
                     "In <code>1()(2)</code> the empty pair says 2 is a right child. Without it, <code>1(2)</code> would mean 2 is a left child."],
                    ["Why use a list and <code>join</code> instead of <code>+=</code> on a string?",
                     "Repeated string concatenation can copy the string each time, which is O(n²) in the worst case. Appending to a list and joining once is linear."],
                    ["What if the root is <code>None</code>?",
                     "The problem guarantees at least one node. <code>walk(None)</code> would fail on <code>node.val</code>, so an empty-tree version would return \"\" first."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum binary tree
    "maximum-binary-tree": {
        "examples": [
            {"call": "level_order(construct_maximum_binary_tree([3, 2, 1, 6, 0, 5]))", "expect": "[6, 3, 5, None, 2, 0, None, None, 1]"},
            {"call": "level_order(construct_maximum_binary_tree([1, 2, 3]))", "expect": "[3, 2, None, 1]"},
        ],
        "approaches": {
            "Monotonic decreasing stack": {
                "idea": [
                    "In the finished tree, a node's parent is the <em>smaller</em> of the nearest greater value on its left and the nearest greater value on its right.",
                    "A stack of nodes with decreasing values, scanned left to right, finds both neighbours: the node below on the stack is the nearest greater on the left, and the value that pops a node is its nearest greater on the right.",
                    "When a new value arrives, the last node it pops becomes its left child, and it becomes the right child of whatever stays on top.",
                ],
                "steps": [
                    "Start with an empty <code>stack</code>. For each value <code>v</code>, create <code>node</code> and set <code>last = None</code>.",
                    "While the top of the stack is smaller than <code>v</code>, pop it into <code>last</code>.",
                    "Set <code>node.left = last</code>: the largest of the popped nodes, which already holds the others as its right descendants.",
                    "If the stack is not empty, set <code>stack[-1].right = node</code>, then push <code>node</code>.",
                    "Return <code>stack[0]</code>, the overall maximum, or <code>None</code> for an empty list.",
                ],
                "why": [
                    "The stack always holds the right spine of the tree built so far, in decreasing order, so attaching on the right of the top keeps the tree valid.",
                    "Popped nodes are smaller than <code>v</code> and lie between <code>v</code> and the next greater value on the left, so they belong in <code>v</code>'s left subtree, with the last popped (largest) as its root.",
                    "Every node is pushed once and popped at most once: <strong>O(n)</strong> time.",
                    "The stack can hold all n nodes for a decreasing input: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "v=3: stack empty, push. v=2: 3 stays, 3.right = 2, push. v=1: 2.right = 1, push. Stack [3, 2, 1].",
                        "v=6: pop 1, 2, 3 (last = 3). 6.left = 3, stack empty, push. Stack [6].",
                        "v=0: 6.right = 0, push. Stack [6, 0].",
                        "v=5: pop 0, so 5.left = 0. 6.right = 5 (replacing 0). Stack [6, 5].",
                        "Root 6: <strong>[6, 3, 5, None, 2, 0, None, None, 1]</strong>.",
                    ],
                    [
                        "v=1: push. Stack [1].",
                        "v=2: pop 1, 2.left = 1, push. Stack [2].",
                        "v=3: pop 2, 3.left = 2, push. Stack [3].",
                        "An increasing input builds a chain leaning left.",
                        "It returns <strong>[3, 2, None, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>6.right = 0</code> get overwritten later?",
                     "At that moment 0 is the best right child of 6. When 5 arrives, 0 turns out to sit between 6 and 5, so it moves under 5 and 5 takes its place."],
                    ["Why is <code>stack[0]</code> the root?",
                     "The bottom of a decreasing stack is never popped by anything after it, so it is the largest value in the whole array."],
                    ["What about equal values?",
                     "The problem says values are distinct. With <code>&lt;</code> in the loop, an equal value would stay on the stack and the new node would become its right child."],
                ],
            },
            "Recursive divide and conquer": {
                "idea": [
                    "Follow the definition: the maximum of the range is the root, the part to its left builds the left subtree and the part to its right the right subtree.",
                    "Work on index ranges <code>lo..hi</code> so no list is copied.",
                    "Simple and clearly correct, but each call scans its whole range to find the maximum.",
                ],
                "steps": [
                    "<code>make(lo, hi)</code> returns <code>None</code> if <code>lo &gt; hi</code>.",
                    "Find <code>m</code>, the index of the largest value in <code>nums[lo..hi]</code>, with <code>max(range(lo, hi + 1), key=nums.__getitem__)</code>.",
                    "Build the left child from <code>make(lo, m - 1)</code>.",
                    "Build the right child from <code>make(m + 1, hi)</code>.",
                    "Return <code>TreeNode(nums[m], left, right)</code>; the answer is <code>make(0, len(nums) - 1)</code>.",
                ],
                "why": [
                    "It is the problem statement written as recursion, so the result matches by construction.",
                    "Each level of recursion scans ranges that together cover at most n elements. A sorted input makes the tree a chain of n levels, giving <strong>O(n²)</strong> time; balanced splits give O(n log n).",
                    "The recursion depth equals the tree height, up to n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "make(0, 5): the max is 6 at index 3.",
                        "Left make(0, 2): max 3 at 0. Its right make(1, 2): max 2 at 1, whose right make(2, 2) is 1.",
                        "Right make(4, 5): max 5 at 5. Its left make(4, 4) is 0.",
                        "Every call scanned its range once to find the maximum.",
                        "It returns <strong>[6, 3, 5, None, 2, 0, None, None, 1]</strong>.",
                    ],
                    [
                        "make(0, 2): max 3 at index 2. The right range is empty.",
                        "make(0, 1): max 2 at index 1. make(0, 0): leaf 1.",
                        "The scans cost 3 + 2 + 1: the quadratic pattern of a sorted input.",
                        "It returns <strong>[3, 2, None, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["What does <code>key=nums.__getitem__</code> do?",
                     "It makes <code>max</code> compare indices by the values they point to, so it returns the index of the largest value rather than the value."],
                    ["When is this worse than the stack?",
                     "On sorted or nearly sorted input, where every split peels off one element and the scans add up to n²/2."],
                    ["Could a segment tree speed up the max query?",
                     "Yes, range-max queries in O(log n) give O(n log n) overall, but the stack approach is simpler and already linear."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ serialize / deserialize binary tree
    "serialize-deserialize-tree": {
        "examples": [
            {"setup": "codec = Codec()", "call": "level_order(codec.deserialize(codec.serialize(build([1, 2, 3, None, None, 4, 5]))))", "expect": "[1, 2, 3, None, None, 4, 5]"},
            {"setup": "codec = Codec()", "call": "level_order(codec.deserialize(codec.serialize(build([1, 2, None, None, 3]))))", "expect": "[1, 2, None, None, 3]"},
        ],
        "approaches": {
            "Preorder with null markers": {
                "idea": [
                    "A preorder list of values alone is ambiguous, but a preorder that also writes a marker <code>#</code> for every empty child is not: it pins down the exact shape.",
                    "Reading it back mirrors writing it: take a token; <code>#</code> means an empty subtree, anything else is a node whose left and then right subtrees follow.",
                    "A shared iterator over the tokens lets each recursive call consume exactly its own part of the string.",
                ],
                "steps": [
                    "<code>serialize</code>: <code>walk(node)</code> appends <code>#</code> for <code>None</code>, otherwise <code>str(node.val)</code>, then walks left and right.",
                    "Join the tokens with commas.",
                    "<code>deserialize</code>: split on commas and wrap the list in <code>iter</code> so <code>next(tokens)</code> always gives the next unread token.",
                    "<code>make()</code> reads a token: <code>#</code> returns <code>None</code>; otherwise it creates a node and fills <code>node.left = make()</code>, then <code>node.right = make()</code>.",
                    "Return <code>make()</code>.",
                ],
                "why": [
                    "With markers, each subtree's token run is self-delimiting: a subtree ends exactly when its last <code>#</code> is read, so <code>make</code> knows where the left subtree stops and the right one begins.",
                    "<code>deserialize</code> consumes tokens in the same order <code>serialize</code> produced them, so it rebuilds the identical tree.",
                    "There are n values and n + 1 markers, each handled once: <strong>O(n)</strong> time for both directions.",
                    "The string is O(n) and the recursion is as deep as the tree, up to n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 3 → (4, 5).",
                        "serialize gives \"1,2,#,#,3,4,#,#,5,#,#\": 5 values and 6 markers.",
                        "make reads 1, then its left: 2, whose two children read \"#\", \"#\".",
                        "1's right reads 3; 3's left reads 4 (then #, #), 3's right reads 5 (then #, #). Every token is used.",
                        "The rebuilt tree flattens to <strong>[1, 2, 3, None, None, 4, 5]</strong>.",
                    ],
                    [
                        "The tree: 1 → (2, ·), 2 → (·, 3).",
                        "serialize gives \"1,2,#,3,#,#,#\".",
                        "make reads 1, left reads 2. 2's left reads \"#\", 2's right reads 3, and 3's children read \"#\", \"#\".",
                        "1's right reads the last \"#\".",
                        "It returns <strong>[1, 2, None, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is preorder without markers not enough?",
                     "Trees 1 → (2, ·) and 1 → (·, 2) both give preorder [1, 2]. The <code>#</code> markers record which side each child is on."],
                    ["Why <code>iter</code> and <code>next</code> instead of an index?",
                     "The iterator remembers its position across all recursive calls without a <code>nonlocal</code> counter. An index with <code>nonlocal</code> works just as well."],
                    ["How are negative or multi-digit values handled?",
                     "Each value is written with <code>str</code> and read with <code>int</code>, and commas separate tokens, so \"-12\" round-trips as one token."],
                ],
            },
            "Level order with null markers": {
                "idea": [
                    "Write the tree the way LeetCode prints it: BFS order, with <code>#</code> for every empty child slot of a real node.",
                    "To rebuild, BFS again: each real node in the queue takes the next two tokens as its left and right child.",
                    "Only real nodes have child slots, so the tokens and the queue stay in step.",
                ],
                "steps": [
                    "<code>serialize</code>: start the queue with the root. Pop a node; <code>None</code> appends <code>#</code>; a real node appends its value and pushes both children, even empty ones.",
                    "Join with commas.",
                    "<code>deserialize</code>: if the first token is <code>#</code>, return <code>None</code>. Otherwise make the root, queue it, and set <code>i = 1</code>.",
                    "Pop a node; for <code>side</code> in left and right, if <code>tokens[i]</code> is not <code>#</code>, create the child, attach it with <code>setattr</code>, and queue it. Always advance <code>i</code>.",
                    "Return the root when the queue is empty.",
                ],
                "why": [
                    "Both functions visit real nodes in the same BFS order and handle their two child slots in the same order, so token i always describes the same slot on both sides.",
                    "Every real node writes exactly two child tokens, so the tokens never run out while the queue still holds nodes.",
                    "Each node and marker is handled once: <strong>O(n)</strong> time.",
                    "The string, token list and queue are all O(n): <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "serialize gives \"1,2,3,#,#,4,5,#,#,#,#\".",
                        "Root 1, queue [1], i = 1. Pop 1: tokens 2 and 3 become its children. Queue [2, 3], i = 3.",
                        "Pop 2: tokens \"#\", \"#\", no children. Pop 3: tokens 4 and 5. Queue [4, 5], i = 7.",
                        "Pop 4 and 5: four \"#\" tokens. i = 11, the queue is empty.",
                        "It returns <strong>[1, 2, 3, None, None, 4, 5]</strong>.",
                    ],
                    [
                        "serialize gives \"1,2,#,#,3,#,#\".",
                        "Pop 1: tokens 2 and \"#\": left child 2 only. Queue [2].",
                        "Pop 2: tokens \"#\" and 3: right child 3. Queue [3].",
                        "Pop 3: tokens \"#\", \"#\". Done.",
                        "It returns <strong>[1, 2, None, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can the loop read <code>tokens[i]</code> without a bounds check?",
                     "The serializer wrote two tokens for every real node, so every node popped here finds its two tokens. Trailing markers are not trimmed in this format."],
                    ["What does <code>setattr(node, side, child)</code> do?",
                     "It is <code>node.left = child</code> or <code>node.right = child</code> depending on the string in <code>side</code>, which avoids writing the same block twice."],
                    ["Preorder or level order: which is better?",
                     "Both are O(n). Level order is iterative, so it cannot hit the recursion limit on a deep chain; preorder is shorter to write."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ serialize / deserialize BST
    "serialize-deserialize-bst": {
        "examples": [
            {"setup": "codec = Codec()", "call": "level_order(codec.deserialize(codec.serialize(build([5, 3, 8, 2, 4, None, 9]))))", "expect": "[5, 3, 8, 2, 4, None, 9]"},
            {"setup": "codec = Codec()", "call": "codec.deserialize(codec.serialize(None))", "expect": "None"},
        ],
        "approaches": {
            "Preorder values only, rebuild with bounds": {
                "idea": [
                    "In a BST the ordering already tells you where every value goes, so no null markers are needed: preorder values alone fix the tree.",
                    "When rebuilding, each subtree has an open interval (<code>lo</code>, <code>hi</code>) its values must fall in. The next preorder value belongs to the current subtree only if it fits.",
                    "A value that does not fit ends the current subtree and is left for an ancestor's right side.",
                ],
                "steps": [
                    "<code>serialize</code>: preorder walk, appending each value; join with spaces (an empty tree gives an empty string).",
                    "<code>deserialize</code>: parse the values and set the shared index <code>i = 0</code>.",
                    "<code>make(lo, hi)</code> returns <code>None</code> if all values are used or <code>values[i]</code> is not strictly between <code>lo</code> and <code>hi</code>.",
                    "Otherwise create the node, advance <code>i</code>, build <code>node.left = make(lo, node.val)</code>, then <code>node.right = make(node.val, hi)</code>.",
                    "Return <code>make(-inf, inf)</code>.",
                ],
                "why": [
                    "In preorder, after a node come all values of its left subtree (all smaller) and then its right subtree (all larger), so the bounds decide exactly where each subtree ends.",
                    "A value that fails the check is not lost: <code>i</code> does not move, and the caller tries it under a wider interval.",
                    "Each value is consumed once and each failed check returns in O(1), with at most two per node: <strong>O(n)</strong> time.",
                    "The value list is O(n) and recursion depth is the tree height, up to n: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "serialize gives \"5 3 2 4 8 9\".",
                        "make(−inf, inf) takes 5. Left make(−inf, 5) takes 3; its left make(−inf, 3) takes 2.",
                        "2's children: 4 is not below 2 and not between 2 and 3, so both are None. 3's right make(3, 5) takes 4.",
                        "4's children reject 8, as does 3's subtree. Back at 5, right make(5, inf) takes 8; 9 fails (5, 8) but fits (8, inf).",
                        "It returns <strong>[5, 3, 8, 2, 4, None, 9]</strong>.",
                    ],
                    [
                        "serialize(None): the walk appends nothing, so the string is \"\".",
                        "deserialize: <code>\"\".split()</code> is [], so values is empty.",
                        "make(−inf, inf): <code>i == len(values)</code>, return None.",
                        "It returns <strong>None</strong>.",
                    ],
                ],
                "faq": [
                    ["Why strict <code>lo &lt; v &lt; hi</code>?",
                     "BST values here are distinct, so a value equal to a bound belongs to a different subtree. Allowing equality could place it on the wrong side."],
                    ["Why <code>split()</code> without an argument?",
                     "With no argument, an empty string splits into []. <code>\"\".split(\" \")</code> would give <code>['']</code> and <code>int('')</code> would crash."],
                    ["Would this work for a general binary tree?",
                     "No. Without the BST ordering the bounds carry no information, and preorder alone cannot fix the shape; that is why the general codec needs markers."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LCA of a binary tree
    "lca-binary-tree": {
        "examples": [
            {"setup": _LCA_T, "call": "lowest_common_ancestor(t, find_node(t, 6), find_node(t, 4)).val", "expect": "5"},
            {"setup": _LCA_T, "call": "lowest_common_ancestor(t, find_node(t, 5), find_node(t, 4)).val", "expect": "5"},
        ],
        "approaches": {
            "Postorder: report what you found": {
                "idea": [
                    "Ask each subtree a simple question: does it contain p or q? Return the node found (or the answer already found below), else <code>None</code>.",
                    "The first node where <em>both</em> sides report something is where the paths to p and q split: that is the LCA.",
                    "If the current node is p or q itself, return it straight away: whether or not the other one is below, this node is the answer for this branch.",
                ],
                "steps": [
                    "If <code>root</code> is <code>None</code>, p or q, return <code>root</code>.",
                    "Recurse into the left subtree to get <code>left</code>.",
                    "Recurse into the right subtree to get <code>right</code>.",
                    "If both are non-empty, p and q are on different sides: return <code>root</code>.",
                    "Otherwise return <code>left or right</code>, passing up whatever was found.",
                ],
                "why": [
                    "A non-empty return value is either one of the targets or their LCA already, and once the LCA is found it is the only non-empty value on its path to the top.",
                    "Stopping at p is safe because p and q both exist: if q is not elsewhere, it is below p and p is the LCA.",
                    "Each node is visited at most once: <strong>O(n)</strong> time.",
                    "The recursion is as deep as the tree: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        _LCA_SHAPE + " p = 6, q = 4.",
                        "At 5: the left call hits 6 and returns it at once.",
                        "The right call at 2: 7 returns None, 4 returns itself, so 2 passes up 4.",
                        "At 5: left = 6 and right = 4, both set, so 5 is returned. At 3 the right side (1) finds nothing.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "p = 5, q = 4, and 4 is inside 5's subtree.",
                        "At 3: the left call reaches 5, which is p, and returns 5 without looking below.",
                        "The right call through 1, 0, 8 returns None.",
                        "At 3: only left is set, so 5 is passed up.",
                        "It returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can it return p without checking that q is below?",
                     "The problem guarantees both nodes exist. If q were not under p it would be found on another branch, and the split would happen higher up."],
                    ["Why compare with <code>is</code> and not by value?",
                     "p and q are node objects, and values might repeat in a general tree. Identity is exactly what is being asked about."],
                    ["What if p or q might be missing from the tree?",
                     "Then this version can wrongly return the one that exists. You need to count how many targets were really found and only accept the answer when it is two."],
                ],
            },
            "Parent pointers and an ancestor set": {
                "idea": [
                    "If every node knew its parent, the LCA is the first node on q's path upward that also lies on p's path upward.",
                    "Fill a <code>parent</code> dictionary with a DFS, stopping as soon as both p and q have entries.",
                    "Then collect all of p's ancestors (p included) in a set and climb from q until you hit one.",
                ],
                "steps": [
                    "Set <code>parent = {root: None}</code> and push the root on <code>stack</code>.",
                    "While p or q is not yet in <code>parent</code>, pop a node and record each child's parent, pushing the child.",
                    "Walk from p up to <code>None</code>, adding every node to <code>ancestors</code>.",
                    "Climb from q with <code>q = parent[q]</code> until <code>q</code> is in <code>ancestors</code>.",
                    "Return that <code>q</code>.",
                ],
                "why": [
                    "Climbing from q meets ancestors of q from the bottom up, so the first one that is also an ancestor of p is the lowest common one.",
                    "The root is an ancestor of both, so the climb always stops.",
                    "Building the map visits each node at most once, and both climbs are at most h steps: <strong>O(n)</strong> time.",
                    "The parent map, stack and ancestor set can hold O(n) nodes: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        _LCA_SHAPE + " p = 6, q = 4.",
                        "DFS pops 3, 1, 8, 0, 5 (now 6 has a parent), then 2, which records 7 and 4. Stop.",
                        "ancestors of 6: {6, 5, 3}.",
                        "Climb from 4: 4 is not in the set, 2 is not, 5 is.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "p = 5, q = 4. The same pops 3, 1, 8, 0, 5, 2 are needed before 4 has a parent.",
                        "ancestors of 5: {5, 3}.",
                        "Climb from 4: 4 no, 2 no, 5 yes.",
                        "It returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why put p itself in <code>ancestors</code>?",
                     "p may be the answer, as when q is in p's subtree. Counting each node as its own ancestor covers that case."],
                    ["Why stop the DFS early?",
                     "Only the paths from p and q to the root are needed, and once both have parents those paths are complete. It saves work but not worst-case time."],
                    ["When is this better than the recursive version?",
                     "When the tree is very deep (no recursion limit), or when many queries share one tree: build <code>parent</code> once and answer each query by climbing."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LCA of a BST
    "lca-bst": {
        "examples": [
            {"setup": _BST_T, "call": "lowest_common_ancestor(t, find_node(t, 3), find_node(t, 5)).val", "expect": "4"},
            {"setup": _BST_T, "call": "lowest_common_ancestor(t, find_node(t, 2), find_node(t, 4)).val", "expect": "2"},
        ],
        "approaches": {
            "Walk down until the values split": {
                "idea": [
                    "In a BST the values tell you which way p and q lie. If both are smaller than the node, both are in the left subtree; if both are larger, both are on the right.",
                    "The first node where they do not go the same way (one smaller, one larger, or one equal to the node) is where their paths separate: the LCA.",
                    "No subtree search is needed, just one walk from the root.",
                ],
                "steps": [
                    "Start at <code>node = root</code>.",
                    "If <code>p.val</code> and <code>q.val</code> are both less than <code>node.val</code>, move to <code>node.left</code>.",
                    "If both are greater, move to <code>node.right</code>.",
                    "Otherwise return <code>node</code>: the values split here, or one of them is this node.",
                ],
                "why": [
                    "As long as both values are on one side, the current node is a common ancestor but not the lowest, since both targets are in a single child subtree.",
                    "At the split node, p and q are in different subtrees (or one is the node), so no deeper node contains both.",
                    "One step per level: <strong>O(h)</strong> time, O(log n) for a balanced tree and O(n) for a chain.",
                    "Only one pointer is kept: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        _BST_SHAPE + " p = 3, q = 5.",
                        "At 6: 3 and 5 are both smaller, go left.",
                        "At 2: both larger, go right.",
                        "At 4: 3 &lt; 4 &lt; 5, the values split.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "p = 2, q = 4.",
                        "At 6: both smaller, go left.",
                        "At 2: p.val equals 2, so neither \"both smaller\" nor \"both larger\" holds.",
                        "It returns <strong>2</strong>, since a node is its own ancestor.",
                    ],
                ],
                "faq": [
                    ["Why is equality handled by the <code>else</code> branch?",
                     "If p or q is the current node, the other one is in its subtree, so this node is the LCA. Both strict comparisons fail and the <code>else</code> returns it."],
                    ["Can the loop fall off the tree?",
                     "Not when p and q are in the tree: the walk stops at their LCA at the latest, which exists."],
                    ["Does this work on a plain binary tree?",
                     "No. Without the ordering, the values give no hint about which side a node is on, so you need the general postorder search."],
                ],
            },
            "Recursive": {
                "idea": [
                    "The same rule as the loop, written as recursion: both smaller, recurse left; both larger, recurse right; otherwise this node is the answer.",
                    "Each call does one comparison and at most one recursive call, so it is tail recursion in disguise.",
                    "It reads like the definition, at the cost of a call stack.",
                ],
                "steps": [
                    "If both values are less than <code>root.val</code>, return the result of recursing on <code>root.left</code>.",
                    "If both are greater, return the result of recursing on <code>root.right</code>.",
                    "Otherwise return <code>root</code>.",
                    "The first call is made on the tree's root.",
                ],
                "why": [
                    "The same argument as the loop: moving into the side that holds both targets keeps a common ancestor, and the first node where they separate is the lowest.",
                    "One call per level: <strong>O(h)</strong> time.",
                    "Python does not remove tail calls, so the stack holds one frame per level: <strong>O(h)</strong> space, compared with O(1) for the loop.",
                ],
                "dry": [
                    [
                        "lca(6): 3 and 5 are both below 6, call lca(2).",
                        "lca(2): both above 2, call lca(4).",
                        "lca(4): 3 &lt; 4 &lt; 5, return 4.",
                        "The result is passed straight back up through both frames.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "lca(6): 2 and 4 are both below 6, call lca(2).",
                        "lca(2): 2 is not below 2, and 2 is not above 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Is the iterative version always better?",
                     "It uses O(1) space instead of O(h), and on a very deep BST it avoids Python's recursion limit. The recursive one is just as fast otherwise."],
                    ["Why does it never need a <code>None</code> check?",
                     "The recursion only goes towards a side that contains both targets, so it never steps into an empty child."],
                    ["Does it matter which of p and q is smaller?",
                     "No. The conditions test both values against the node, so swapping p and q gives the same path."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LCA of deepest leaves
    "lca-deepest-leaves": {
        "examples": [
            {"call": "lca_deepest_leaves(build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])).val", "expect": "2"},
            {"call": "lca_deepest_leaves(build([0, 1, 3, None, 2])).val", "expect": "2"},
        ],
        "approaches": {
            "Return (depth, lca) pairs": {
                "idea": [
                    "For any subtree, two facts settle the question: how deep it goes, and which node is the LCA of its deepest leaves.",
                    "If the left and right subtrees are equally deep, the deepest leaves are on both sides, so the current node is their LCA.",
                    "If one side is deeper, all deepest leaves are on that side, so its answer is passed up unchanged.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns <code>(0, None)</code>.",
                    "Get <code>(ld, la)</code> from the left child and <code>(rd, ra)</code> from the right child.",
                    "If <code>ld == rd</code>, return <code>(ld + 1, node)</code>.",
                    "Otherwise return the deeper side's pair with its depth increased by one.",
                    "The answer is <code>dfs(root)[1]</code>.",
                ],
                "why": [
                    "By induction the pair from each child is correct; equal depths put deepest leaves in both subtrees, whose only common ancestor inside this subtree is the node itself.",
                    "A leaf gets equal depths (0 and 0), so it is returned as its own LCA, which is right when it is the only deepest leaf.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        _LCA_SHAPE,
                        "Leaves return (1, itself). Node 2: both sides depth 1, returns (2, 2).",
                        "Node 5: left (1, 6), right (2, 2). Right is deeper: (3, 2).",
                        "Node 1: children 0 and 8 tie, returns (2, 1).",
                        "Root 3: left 3 &gt; right 2, so it passes up (4, 2): <strong>2</strong>.",
                    ],
                    [
                        "The tree: 0 → (1, 3), 1 → (·, 2).",
                        "Leaf 2: (1, 2). Node 1: left (0, None), right (1, 2), returns (2, 2).",
                        "Leaf 3: (1, 3).",
                        "Root 0: left depth 2 &gt; right depth 1, returns (3, 2).",
                        "A single deepest leaf is its own LCA: <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the depth of an empty subtree 0 and not −1?",
                     "Only differences between the two sides matter, so any constant works as long as it is used consistently. 0 makes a leaf's depth 1."],
                    ["Why not find the deepest leaves first and then run an LCA search?",
                     "That works but takes two passes and extra memory. Returning the pair answers both questions in one postorder pass."],
                    ["Is this the same problem as \"smallest subtree with all the deepest nodes\"?",
                     "Yes, the two problems have the same answer, and this exact function solves both."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ smallest subtree with all deepest nodes
    "subtree-deepest-nodes": {
        "examples": [
            {"call": "subtree_with_all_deepest(build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])).val", "expect": "2"},
            {"call": "subtree_with_all_deepest(build([1, 2, 3, 4, 5, 6, 7])).val", "expect": "1"},
        ],
        "approaches": {
            "BFS for the deepest level, then climb with parents": {
                "idea": [
                    "First find the deepest nodes: they are simply the last level of a BFS. Record every node's parent on the way.",
                    "The smallest subtree holding all of them is rooted at their common ancestor. Climb all of them up one level at a time.",
                    "Keep them in a set: as paths merge, the set shrinks, and when one node is left it is the answer.",
                ],
                "steps": [
                    "Set <code>parent = {root: None}</code> and <code>level = [root]</code>.",
                    "Repeatedly build <code>nxt</code>, the children of <code>level</code>, recording each child's parent. Stop when <code>nxt</code> is empty; <code>level</code> is then the deepest level.",
                    "Put the deepest nodes in <code>group</code>.",
                    "While <code>group</code> has more than one node, replace it with <code>{parent[n] for n in group}</code>.",
                    "Return the single node left.",
                ],
                "why": [
                    "All deepest nodes are at the same depth, so climbing them together keeps them level; they first meet at their lowest common ancestor.",
                    "Merging in a set removes duplicates as soon as two paths join, so the size reaches 1 exactly at that ancestor.",
                    "The BFS is O(n); the climb does at most h rounds over shrinking sets whose sizes add up to at most n: <strong>O(n)</strong> time.",
                    "The parent map holds every node: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        _LCA_SHAPE,
                        "Levels: [3], [5, 1], [6, 2, 0, 8], [7, 4]. The level after [7, 4] is empty.",
                        "group = {7, 4}.",
                        "Climb: both have parent 2, so group = {2}.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "The perfect tree 1 → (2, 3), 2 → (4, 5), 3 → (6, 7).",
                        "Deepest level: [4, 5, 6, 7].",
                        "Climb: group = {2, 3}. Climb again: group = {1}.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the BFS use <code>while True</code> with a <code>break</code>?",
                     "The loop must stop one step before the level becomes empty, so that <code>level</code> still holds the deepest nodes. Checking <code>nxt</code> before replacing does that."],
                    ["What if there is only one deepest node?",
                     "Then <code>group</code> has one element from the start and that node is returned, which is correct: the smallest subtree containing it is itself."],
                    ["Why a set rather than a list?",
                     "Two siblings have the same parent; a set collapses them into one entry, which is how the climb knows paths have merged."],
                ],
            },
            "Return (depth, answer) pairs": {
                "idea": [
                    "Each subtree reports its depth and the root of the smallest subtree inside it that holds all its deepest nodes.",
                    "Equal depths on both sides mean the deepest nodes are split between them, so the current node is needed to hold them all.",
                    "Otherwise the deeper side holds every deepest node, and its answer is passed up.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns <code>(0, None)</code>.",
                    "Compute <code>(ld, la)</code> and <code>(rd, ra)</code> for the two children.",
                    "If <code>ld == rd</code>, return <code>(ld + 1, node)</code>.",
                    "Otherwise return the deeper child's answer with depth + 1.",
                    "Return <code>dfs(root)[1]</code>.",
                ],
                "why": [
                    "The depth tells which side contains the deepest nodes of the subtree; the inductive answer from that side is already minimal, and a tie forces the current node.",
                    "Every node is visited once with O(1) work: <strong>O(n)</strong> time.",
                    "Only the recursion stack is used: <strong>O(h)</strong> space, better than the BFS version's parent map.",
                ],
                "dry": [
                    [
                        "Node 2: both children are leaves at depth 1, so (2, 2).",
                        "Node 5: left (1, 6) vs right (2, 2): (3, 2).",
                        "Node 1: children 0 and 8 tie: (2, 1).",
                        "Root 3: 3 &gt; 2, so (4, 2).",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "Leaves 4, 5, 6, 7 each return (1, leaf).",
                        "Node 2: tie, (2, 2). Node 3: tie, (2, 3).",
                        "Root 1: tie at depth 2, so (3, 1).",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is a tie the only case that returns the current node?",
                     "Only then do both sides contain deepest nodes. If one side is shallower it contains none of them and is not needed."],
                    ["What about a node with one child?",
                     "The missing child has depth 0, which is less than the other side's depth, so the existing child's answer is passed up."],
                    ["Which approach is preferable?",
                     "The pair-returning DFS: one pass and O(h) memory. The BFS version is easier to picture and avoids recursion."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ binary lifting
    "lca-binary-lifting": {
        "examples": [
            {"setup": _LCA_T + "\nlca = LCA(t)", "call": "lca.query(find_node(t, 7), find_node(t, 8)).val", "expect": "3"},
            {"setup": _LCA_T + "\nlca = LCA(t)", "call": "lca.query(find_node(t, 5), find_node(t, 4)).val", "expect": "5"},
        ],
        "approaches": {
            "Binary lifting table": {
                "idea": [
                    "For many queries on one tree, precompute jumps: <code>up[j][v]</code> is the ancestor 2<sup>j</sup> levels above v (the root points to itself).",
                    "Any climb of d levels is a sum of powers of two, so it takes at most log n jumps, one per set bit of d.",
                    "A query first lifts the deeper node to the other's depth, then lifts both together with the largest jumps that keep them apart; their parent is then the LCA.",
                ],
                "steps": [
                    "BFS from the root to fill <code>parent</code> and <code>self.depth</code>; the root's parent is the root.",
                    "Set <code>LOG = max(1, n.bit_length())</code> and <code>up[0] = parent</code>; build <code>up[j][v] = up[j-1][up[j-1][v]]</code> for each level.",
                    "Query: make <code>a</code> the deeper node, and for every set bit j of <code>diff</code> jump <code>a = up[j][a]</code>.",
                    "If now <code>a is b</code>, return it.",
                    "For j from high to low, if <code>up[j][a]</code> and <code>up[j][b]</code> differ, jump both. Return <code>up[0][a]</code>.",
                ],
                "why": [
                    "After equalising depths, the jumps from high to low land a and b on the deepest pair of distinct ancestors at the same depth, the children of the LCA on their two paths.",
                    "A jump is skipped only when it would land on a common ancestor, which might be above the LCA, so the LCA is never overshot.",
                    "The table has LOG = O(log n) dictionaries of n entries: <strong>O(n log n)</strong> time and space to build, and each query does at most 2·LOG jumps: <strong>O(log n)</strong>.",
                ],
                "dry": [
                    [
                        _LCA_SHAPE + " n = 9, so LOG = 4.",
                        "Depths: 7 is at 3, 8 at 2. a = 7, b = 8, diff = 1, bit 0: a = up[0][7] = 2.",
                        "2 is not 8. j = 3, 2, 1: both land on 3 (root), skip.",
                        "j = 0: up[0][2] = 5 and up[0][8] = 1 differ, so a = 5, b = 1.",
                        "Return up[0][5] = <strong>3</strong>.",
                    ],
                    [
                        "4 is at depth 3, 5 at depth 1, so swap: a = 4, b = 5. diff = 2.",
                        "Bit 1 is set: a = up[1][4], the grandparent of 4, which is 5.",
                        "Now <code>a is b</code>: 5 is an ancestor of 4.",
                        "It returns <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the root point to itself?",
                     "Jumping past the root then stays at the root instead of failing. Both nodes end up at the root, which the \"differ\" test treats as a common ancestor and skips."],
                    ["Why go from the largest jump down?",
                     "It is like writing a number in binary: trying big steps first and keeping each one that fits finds the exact distance to just below the LCA in one pass."],
                    ["When is this worth it over a plain LCA search?",
                     "When there are many queries. One O(n) search per query costs O(n·q); this costs O(n log n + q log n)."],
                ],
            },
        },
    },
}
