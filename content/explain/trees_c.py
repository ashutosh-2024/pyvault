"""Write-ups for Trees, part C: views, construction, serialization, LCA."""

_LCA_T = "t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])"
_LCA_SHAPE = "The tree: 3 → (5, 1), 5 → (6, 2), 2 → (7, 4), 1 → (0, 8)."

EXPLAIN = {
    # ------------------------------------------------------------------ right side view
    "right-side-view": {
        "example": {"call": "right_side_view(build([1, 2, 3, 4, 5, 6, 7, None, 8]))", "expect": "[1, 3, 7, 8]"},
        "approaches": {
            "BFS, keep the last node of each level": {
                "idea": [
                    "From the right you see exactly one node per level: the rightmost one.",
                    "Process level by level, and keep the <em>last</em> node popped in each level.",
                ],
                "steps": [
                    "Pop <code>len(queue)</code> nodes, pushing their children; append the last node's value.",
                ],
                "why": [
                    "It is O(n) time and O(w) queue. For a left view, keep the first node instead.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), 2 → (4, 5), 3 → (6, 7), and 4 has a right child 8.",
                    "The levels are [1], [2, 3], [4, 5, 6, 7], [8], with last nodes 1, 3, 7, 8.",
                    "8 hangs under the far-left 4, yet it is visible because nothing else is that deep. The result is <strong>[1, 3, 7, 8]</strong>.",
                ],
            },
            "DFS right-first, first node per depth": {
                "idea": [
                    "Visit the right child before the left. The first node reached at each new depth is then the rightmost one.",
                    "<code>depth == len(view)</code> means this depth is being reached for the first time.",
                ],
                "steps": [
                    "Record on first arrival at a depth; recurse right, then left.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "1 (depth 0) → 3 (depth 1) → 7 (depth 2) are recorded as the first at their depths.",
                    "6, 2, 5 and 4 are not new depths. 8 at depth 3 is new, so it is recorded.",
                    "The result is <strong>[1, 3, 7, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ top / bottom view
    "top-bottom-view": {
        "example": {"call": "top_and_bottom_view(build([1, 2, 3, 4, 5, 6, 7]))", "expect": "([4, 2, 1, 3, 7], [4, 2, 6, 3, 7])"},
        "approaches": {
            "BFS with column numbers": {
                "idea": [
                    "Give each node a column: the root is 0, a left child is column - 1, a right child is column + 1.",
                    "BFS meets nodes top-down and, within a level, left to right.",
                    "So the <em>first</em> node seen in a column is the top view, and the <em>last</em> is the bottom view.",
                ],
                "steps": [
                    "<code>top.setdefault(col, val)</code>; <code>bottom[col] = val</code>.",
                    "Read the columns from min to max.",
                ],
                "why": [
                    "It is O(n), and no sort is needed because columns are consecutive integers.",
                    "DFS could reach a deep node first, so it would need explicit depth checks.",
                ],
                "dry": [
                    "Columns: 4 at -2, 2 at -1, 1, 5 and 6 at 0, 3 at 1, 7 at 2.",
                    "Column 0 is seen in the order 1, 5, 6. The top keeps 1; the bottom ends at 6.",
                    "The result is <strong>([4, 2, 1, 3, 7], [4, 2, 6, 3, 7])</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ bottom-left value
    "bottom-left-value": {
        "example": {"call": "find_bottom_left_value(build([1, 2, 3, 4, None, 5, 6, None, None, 7]))", "expect": "7"},
        "approaches": {
            "BFS right-to-left, last node wins": {
                "idea": [
                    "Enqueue the right child <em>before</em> the left.",
                    "Then the very last node dequeued is the leftmost node of the deepest level, with no level bookkeeping.",
                ],
                "steps": [
                    "Plain BFS with reversed child order; return the last node's value.",
                ],
                "why": [
                    "It is O(n) time and O(w) queue.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), 2 → (4), 3 → (5, 6), 5 → (7).",
                    "The dequeue order is 1, 3, 2, 6, 5, 4, 7.",
                    "The last node is <strong>7</strong>.",
                ],
            },
            "DFS left-first, first node at a new depth": {
                "idea": [
                    "Visit left before right, and record a node only when its depth is <em>strictly</em> greater than any seen before.",
                    "An equal depth does not replace it, so the leftmost node stays.",
                ],
                "steps": [
                    "<code>if depth &gt; best_depth</code>: update both.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "Depth 0: 1. Depth 1: 2. Depth 2: 4 (5 and 6 come later at the same depth).",
                    "Depth 3: 7.",
                    "The result is <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add one row
    "add-one-row": {
        "example": {"call": "level_order(add_one_row(build([4, 2, 6, 3, 1, 5]), 1, 2))",
                    "expect": "[4, 1, 1, 2, None, None, 6, 3, 1, 5]"},
        "approaches": {
            "BFS to the level above, then splice": {
                "idea": [
                    "Go down to the nodes at <code>depth - 1</code>. Give each of them two new children with value <code>val</code>, and hang the old children underneath.",
                    "The old left goes under the new left; the old right goes under the new right.",
                    "Depth 1 is special: the new node becomes the root, with the old tree as its left child.",
                ],
                "steps": [
                    "Advance the level list <code>depth - 2</code> times; splice each node.",
                ],
                "why": [
                    "Only the levels above the insertion point are visited.",
                ],
                "dry": [
                    "depth = 2, so splice at the root's level. Root 4 gets new 1s, with 2 under the left 1 and 6 under the right 1.",
                    "The original subtrees (3, 1 under 2; 5 under 6) move down one level unchanged.",
                    "The result is <strong>[4, 1, 1, 2, None, None, 6, 3, 1, 5]</strong>.",
                ],
            },
            "DFS carrying the depth": {
                "idea": [
                    "Recurse with the current depth; at <code>depth - 1</code>, splice and stop going deeper.",
                ],
                "steps": [
                    "<code>dfs(root, 1)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "dfs(4, 1): d == 1 == depth - 1, so splice here and return.",
                    "The result is <strong>[4, 1, 1, 2, None, None, 6, 3, 1, 5]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ average of levels
    "average-of-levels": {
        "example": {"call": "average_of_levels(build([3, 9, 20, None, None, 15, 7]))", "expect": "[3.0, 14.5, 11.0]"},
        "approaches": {
            "BFS, one level at a time": {
                "idea": [
                    "The size snapshot tells you how many nodes the level has; sum them and divide by that count.",
                ],
                "steps": [
                    "<code>out.append(total / size)</code> per level.",
                ],
                "why": [
                    "It is O(n) time and O(w) queue.",
                ],
                "dry": [
                    "[3] → 3.0. [9, 20] → 29 / 2 = 14.5. [15, 7] → 22 / 2 = 11.0.",
                    "The result is <strong>[3.0, 14.5, 11.0]</strong>.",
                ],
            },
            "DFS with per-depth sums and counts": {
                "idea": [
                    "Add each node's value to <code>sums[depth]</code> and 1 to <code>counts[depth]</code>; divide at the end.",
                ],
                "steps": [
                    "Any traversal order works.",
                ],
                "why": [
                    "It is O(n) time and O(h) extra space.",
                ],
                "dry": [
                    "sums = [3, 29, 22], counts = [1, 2, 2].",
                    "The result is <strong>[3.0, 14.5, 11.0]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ deepest leaves sum
    "deepest-leaves-sum": {
        "example": {"call": "deepest_leaves_sum(build([1, 2, 3, 4, 5, None, 6, 7, None, None, None, None, 8]))", "expect": "15"},
        "approaches": {
            "BFS, the last level's sum": {
                "idea": [
                    "Compute each level's sum, overwriting the previous one. When there are no more levels, the last sum is the deepest.",
                ],
                "steps": [
                    "<code>total = sum(level)</code>; build the next level from the children.",
                ],
                "why": [
                    "It is O(n) time and O(w) space.",
                ],
                "dry": [
                    "Level sums: 1, then 5, then 4 + 5 + 6 = 15, then 7 + 8 = 15.",
                    "The last level is [7, 8]. The result is <strong>15</strong>.",
                ],
            },
            "One-pass DFS with a reset": {
                "idea": [
                    "Track the deepest depth seen and the sum at that depth.",
                    "A deeper node resets the sum; a node at the current deepest depth adds to it.",
                ],
                "steps": [
                    "<code>if depth &gt; deepest: deepest, total = depth, 0</code>; then add if equal.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "7 reaches depth 3 first: the sum resets to 7.",
                    "Later 8 is at depth 3 too: 7 + 8.",
                    "The result is <strong>15</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ preorder + inorder
    "build-from-preorder-inorder": {
        "example": {"call": "level_order(build_tree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]))",
                    "expect": "[3, 9, 20, None, None, 15, 7]"},
        "approaches": {
            "Index map and a moving preorder pointer": {
                "idea": [
                    "The first value in preorder is the root. Its position in inorder splits the inorder list into the left subtree and the right subtree.",
                    "Preorder lists the whole left subtree before the right, so if you build left first, the next unused preorder value is always the next root.",
                    "Use a <code>{value: index}</code> map for inorder, and index ranges instead of slices.",
                ],
                "steps": [
                    "<code>make(lo, hi)</code>: take <code>preorder[nxt]</code>, find <code>mid</code>, build left from (lo, mid - 1), then right from (mid + 1, hi).",
                ],
                "why": [
                    "Each node takes O(1) work: O(n) time, plus O(n) for the map.",
                ],
                "dry": [
                    "Root 3 sits at inorder index 1, so the left is [9] and the right is [15, 20, 7].",
                    "The next preorder value, 9, becomes the left subtree (a single node). Then 20 is the right root, at index 3: left [15], right [7].",
                    "Level order: <strong>[3, 9, 20, None, None, 15, 7]</strong>.",
                ],
            },
            "Slice and search": {
                "idea": [
                    "Do the same thing literally: <code>inorder.index(root)</code>, slice both lists, recurse.",
                ],
                "steps": [
                    "The left gets <code>preorder[1:mid+1]</code> and <code>inorder[:mid]</code>; the right gets the rest.",
                ],
                "why": [
                    "Searching and slicing are O(n) per level, so a chain costs O(n²).",
                ],
                "dry": [
                    "mid = 1: left ([9], [9]), right ([20, 15, 7], [15, 20, 7]).",
                    "Recursing on the right finds mid = 1 again.",
                    "The result is <strong>[3, 9, 20, None, None, 15, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ inorder + postorder
    "build-from-inorder-postorder": {
        "example": {"call": "level_order(build_tree([9, 3, 15, 20, 7], [9, 15, 7, 20, 3]))",
                    "expect": "[3, 9, 20, None, None, 15, 7]"},
        "approaches": {
            "Index map, consume postorder from the end": {
                "idea": [
                    "Postorder ends with the root, so read it <em>backwards</em>: root, then the right subtree, then the left.",
                    "That is why the recursion builds the <strong>right</strong> subtree before the left.",
                ],
                "steps": [
                    "The pointer starts at the last index and moves left; split inorder at the root's position.",
                ],
                "why": [
                    "It is O(n) time with the index map.",
                ],
                "dry": [
                    "Read 3: the root; inorder splits into left [9] and right [15, 20, 7].",
                    "Read 20: the right root, which splits into [15] and [7]. Read 7 (right), then 15 (left), then 9 (the root's left).",
                    "The result is <strong>[3, 9, 20, None, None, 15, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ preorder + postorder
    "build-from-preorder-postorder": {
        "example": {"call": "level_order(construct_from_pre_post([1, 2, 4, 5, 3, 6, 7], [4, 5, 2, 6, 7, 3, 1]))",
                    "expect": "[1, 2, 3, 4, 5, 6, 7]"},
        "approaches": {
            "Index map on postorder": {
                "idea": [
                    "<code>pre[a]</code> is the root, and <code>pre[a+1]</code> is the root of its left subtree.",
                    "In postorder, that left root comes <em>last</em> in its subtree, so its postorder position tells you the left subtree's size.",
                    "Without inorder, a single child could be left or right; treating it as left is accepted.",
                ],
                "steps": [
                    "<code>left_size = where[pre[a+1]] - post_lo + 1</code>; recurse on both parts.",
                ],
                "why": [
                    "Each node takes O(1) work with the map: O(n).",
                ],
                "dry": [
                    "The root is 1 and the left root is 2. 2 is at postorder index 2, so left_size = 3: [2, 4, 5].",
                    "The right part is [3, 6, 7]. Inside them, 4/5 and 6/7 split the same way.",
                    "The result is <strong>[1, 2, 3, 4, 5, 6, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ tree2str
    "construct-string-from-tree": {
        "example": {"call": "tree2str(build([1, 2, 3, None, 4]))", "expect": "'1(2()(4))(3)'"},
        "approaches": {
            "Preorder with the empty-left rule": {
                "idea": [
                    "Write each node in preorder as <code>val(left)(right)</code>, dropping parentheses that are not needed.",
                    "A leaf is just <code>val</code>. With no right child, drop <code>()</code> for the right.",
                    "With a right child but no left, the empty <code>()</code> for the left must stay, or the right child would be read as a left child.",
                ],
                "steps": [
                    "Append the pieces to one list and join once at the end.",
                ],
                "why": [
                    "It is O(n). Concatenating strings on the way up would copy subtrees repeatedly.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), and 2 has only a right child, 4.",
                    "Node 2 has no left but has a right, so it becomes <code>2()(4)</code>. Node 3 is a leaf: <code>3</code>.",
                    "The result is <strong>'1(2()(4))(3)'</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum binary tree
    "maximum-binary-tree": {
        "example": {"call": "level_order(construct_maximum_binary_tree([3, 2, 1, 6, 0, 5]))",
                    "expect": "[6, 3, 5, None, 2, 0, None, None, 1]"},
        "approaches": {
            "Monotonic decreasing stack": {
                "idea": [
                    "Keep a stack of nodes with decreasing values: the right edge of the tree built so far.",
                    "A new value pops every smaller node; the <em>last</em> one popped (the largest of them) becomes its left child.",
                    "If a larger node remains on the stack, the new node becomes that node's right child.",
                ],
                "steps": [
                    "Pop the smaller nodes; <code>node.left = last</code>; <code>stack[-1].right = node</code>; push.",
                ],
                "why": [
                    "Each node is pushed and popped at most once: O(n).",
                ],
                "dry": [
                    "3 → [3]. 2 becomes 3's right child → [3, 2]. 1 becomes 2's right child → [3, 2, 1].",
                    "6 pops 1, 2 and 3, and takes 3 as its left child → [6]. 0 becomes 6's right child → [6, 0].",
                    "5 pops 0 (its left child) and replaces it as 6's right child. Level order: <strong>[6, 3, 5, None, 2, 0, None, None, 1]</strong>.",
                ],
            },
            "Recursive divide and conquer": {
                "idea": [
                    "Follow the definition: find the maximum in the range, make it the root, and recurse on the left and right parts.",
                ],
                "steps": [
                    "<code>make(lo, hi)</code>, scanning the range for the maximum each time.",
                ],
                "why": [
                    "Sorted input splits one-sidedly, giving O(n²), like quicksort with a bad pivot.",
                ],
                "dry": [
                    "The max of the whole array is 6. Left [3, 2, 1] has max 3; right [0, 5] has max 5.",
                    "Then 2 → 1 down 3's right side, and 0 to the left of 5.",
                    "The result is <strong>[6, 3, 5, None, 2, 0, None, None, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ serialize binary tree
    "serialize-deserialize-tree": {
        "example": {"setup": "codec = Codec()",
                    "call": "level_order(codec.deserialize(codec.serialize(build([1, 2, 3, None, None, 4, 5]))))",
                    "expect": "[1, 2, 3, None, None, 4, 5]"},
        "approaches": {
            "Preorder with null markers": {
                "idea": [
                    "Write the tree in preorder and put <code>#</code> wherever a child is missing. The markers record the shape.",
                    "To read it back, consume tokens in the same order: a value makes a node, then builds its left from the following tokens, then its right. A <code>#</code> ends a branch.",
                ],
                "steps": [
                    "<code>serialize</code>: preorder with #. <code>deserialize</code>: a recursive <code>make()</code> over a token iterator.",
                ],
                "why": [
                    "There are n values and n + 1 markers, so both directions are O(n).",
                ],
                "dry": [
                    "The string is <code>1,2,#,#,3,4,#,#,5,#,#</code>.",
                    "Reading: 1, then its left is 2 (both children #). Its right is 3, with left 4 and right 5.",
                    "The rebuilt level order is <strong>[1, 2, 3, None, None, 4, 5]</strong>.",
                ],
            },
            "Level order with null markers": {
                "idea": [
                    "Use the LeetCode format: BFS, writing # for missing children.",
                    "To read it back, keep a queue of parents, each waiting for its next two tokens.",
                ],
                "steps": [
                    "For each parent popped, read the left token, then the right token.",
                ],
                "why": [
                    "It is O(n), with no recursion.",
                ],
                "dry": [
                    "The string is <code>1,2,3,#,#,4,5,#,#,#,#</code>.",
                    "1 takes 2 and 3; 2 takes #, #; 3 takes 4 and 5; the leaves take the remaining #s.",
                    "The result is <strong>[1, 2, 3, None, None, 4, 5]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ serialize BST
    "serialize-deserialize-bst": {
        "example": {"setup": "codec = Codec()",
                    "call": "level_order(codec.deserialize(codec.serialize(build([5, 3, 8, 2, 4, None, 9]))))",
                    "expect": "[5, 3, 8, 2, 4, None, 9]"},
        "approaches": {
            "Preorder values only, rebuild with bounds": {
                "idea": [
                    "A BST's preorder alone fixes its shape, so no null markers are needed. This gives a more compact string.",
                    "To rebuild, give each position a valid range <code>(lo, hi)</code>. The next value belongs here only if it fits; otherwise this subtree is empty.",
                ],
                "steps": [
                    "<code>make(lo, hi)</code>: if the next value is in range, create the node, build the left with (lo, val) and the right with (val, hi).",
                ],
                "why": [
                    "Each value is read once: O(n). It is the Validate BST bounds idea, run in reverse.",
                ],
                "dry": [
                    "The string is <code>5 3 2 4 8 9</code>.",
                    "5 is the root. 3 fits (-∞, 5), so it goes left. 2 fits (-∞, 3), so it goes left. 4 does not fit 2's ranges, but it fits (3, 5): 3's right.",
                    "8 fits (5, ∞), so it goes right; 9 fits (8, ∞). The result is <strong>[5, 3, 8, 2, 4, None, 9]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LCA binary tree
    "lca-binary-tree": {
        "example": {"setup": _LCA_T,
                    "call": "lowest_common_ancestor(t, find_node(t, 6), find_node(t, 4)).val", "expect": "5"},
        "approaches": {
            "Postorder: report what you found": {
                "idea": [
                    "Each call reports what it found in its subtree: p, q, the LCA, or None.",
                    "If both the left and right calls report something, the two searches meet at this node, so it is the LCA.",
                    "If a node <em>is</em> p or q, return it right away; if the other is below it, this node is still the answer.",
                ],
                "steps": [
                    "Base case: None, p or q returns itself.",
                    "If both sides return something, return the root; otherwise return whichever side returned something.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack, relying on the guarantee that both nodes exist.",
                ],
                "dry": [
                    _LCA_SHAPE,
                    "Under 5: the left call returns 6, and the right call (under 2) returns 4.",
                    "Both are non-empty, so 5 is returned upwards, and 3's other side returns None. The result is <strong>5</strong>.",
                ],
            },
            "Parent pointers and an ancestor set": {
                "idea": [
                    "Record each node's parent; collect p's ancestors in a set; walk up from q until you hit one.",
                ],
                "steps": [
                    "Traverse until both p and q have parents recorded; then climb.",
                ],
                "why": [
                    "It is O(n) time and O(n) space, or O(h) if nodes already have parent pointers.",
                ],
                "dry": [
                    "p = 6 has ancestors {6, 5, 3}.",
                    "From q = 4: 4 is not in the set, 2 is not, 5 is.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LCA BST
    "lca-bst": {
        "example": {"setup": "t = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])",
                    "call": "lowest_common_ancestor(t, find_node(t, 3), find_node(t, 5)).val", "expect": "4"},
        "approaches": {
            "Walk down until the values split": {
                "idea": [
                    "In a BST, values tell you which side a node is on.",
                    "If both p and q are smaller than the current node, the LCA is to the left; if both are larger, it is to the right.",
                    "Otherwise they separate here (or one of them is this node), so this node is the LCA.",
                ],
                "steps": [
                    "A loop moving left or right; return when the values split.",
                ],
                "why": [
                    "One step per level: O(h) time and O(1) space.",
                ],
                "dry": [
                    "At 6: 3 and 5 are both smaller, so go left. At 2: both larger, so go right.",
                    "At 4: 3 &lt; 4 &lt; 5, so they split here.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "Recursive": {
                "idea": [
                    "The same decision written as recursion.",
                ],
                "steps": [
                    "Recurse left or right, or return the root.",
                ],
                "why": [
                    "It is O(h) time but also O(h) stack.",
                ],
                "dry": [
                    "6 → 2 → 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LCA deepest leaves
    "lca-deepest-leaves": {
        "example": {"call": "lca_deepest_leaves(build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])).val", "expect": "2"},
        "approaches": {
            "Return (depth, lca) pairs": {
                "idea": [
                    "Each call returns the depth of its subtree and the LCA of that subtree's deepest nodes.",
                    "If both sides are equally deep, the deepest nodes are on both sides, so this node is the LCA. Otherwise pass up the deeper side's answer.",
                ],
                "steps": [
                    "Return <code>(ld + 1, node)</code> if they are equal, else the deeper side's pair with depth + 1.",
                ],
                "why": [
                    "One postorder pass: O(n).",
                ],
                "dry": [
                    _LCA_SHAPE,
                    "At 2: both children have depth 1, so it returns (2, node 2). 5: depth 1 vs 2, so it passes up node 2. 1: returns (2, node 1).",
                    "At 3: depth 3 vs 2, so it passes up node 2. The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ smallest subtree with deepest
    "subtree-deepest-nodes": {
        "example": {"call": "subtree_with_all_deepest(build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])).val", "expect": "2"},
        "approaches": {
            "BFS for the deepest level, then climb with parents": {
                "idea": [
                    "BFS to the deepest level, recording parents along the way.",
                    "Then repeatedly replace the set of deepest nodes with the set of their parents, until only one node is left.",
                ],
                "steps": [
                    "<code>group = {parent[n] for n in group}</code> while it has more than one node.",
                ],
                "why": [
                    "It is O(n) time and O(n) for the parent map.",
                ],
                "dry": [
                    "The deepest level is {7, 4}.",
                    "Their parents are {2}: a single node.",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Return (depth, answer) pairs": {
                "idea": [
                    "This is exactly the previous problem's solution; the two problems are the same.",
                ],
                "steps": [
                    "Equal depths → this node; otherwise the deeper side's answer.",
                ],
                "why": [
                    "One pass with no parent map: O(n) time and O(h) stack.",
                ],
                "dry": [
                    "Node 2 sees equal depths; 5 and 3 pass it up.",
                    "The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ binary lifting
    "lca-binary-lifting": {
        "example": {"setup": _LCA_T + "\nlca = LCA(t)",
                    "call": "lca.query(find_node(t, 7), find_node(t, 8)).val", "expect": "3"},
        "approaches": {
            "Binary lifting table": {
                "idea": [
                    "Precompute <code>up[j][v]</code> = the ancestor 2<sup>j</sup> levels above v. Row 0 is the parent, and each row doubles: <code>up[j][v] = up[j-1][up[j-1][v]]</code>.",
                    "Query step 1: lift the deeper node to the same depth, jumping by the binary digits of the depth difference.",
                    "Query step 2: from the biggest jump down, jump both nodes together whenever they would still differ. They end one step below the LCA.",
                ],
                "steps": [
                    "Build depths and parents with BFS, then the doubling rows.",
                    "Query: equalise the depths; return early if the nodes are equal; jump; return the parent.",
                ],
                "why": [
                    "Building takes O(n log n). Each query is O(log n) instead of O(n).",
                ],
                "dry": [
                    _LCA_SHAPE + " Depths: 7 is at 3, 8 is at 2.",
                    "The difference is 1, so 7 lifts by 2<sup>0</sup> to 2. 2 is not 8.",
                    "Big jumps land both at the root, which is the same node, so they are skipped. The jump by 1 gives 5 vs 1, which differ, so take it.",
                    "The parent of 5 is <strong>3</strong>.",
                ],
            },
        },
    },
}
