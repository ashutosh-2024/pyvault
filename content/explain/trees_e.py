"""Write-ups for Trees, part E: BST basics, validation, inorder tricks, ranges, construction, conversion."""

_K = "build([5, 3, 6, 2, 4, None, None, 1])"
_K_SHAPE = "The tree: 5 → (3, 6), 3 → (2, 4), 2 → (1). Inorder: 1, 2, 3, 4, 5, 6."

EXPLAIN = {
    # ------------------------------------------------------------------ search
    "search-bst": {
        "example": {"setup": "t = build([4, 2, 7, 1, 3])", "call": "level_order(search_bst(t, 2))", "expect": "[2, 1, 3]"},
        "approaches": {
            "Iterative descent": {
                "idea": [
                    "In a BST, everything left of a node is smaller and everything right is larger.",
                    "So at each node there is only one direction worth taking: left if the target is smaller, right if it is larger.",
                ],
                "steps": [
                    "Loop until a match or None.",
                ],
                "why": [
                    "One node per level: O(h) time, which is O(log n) when balanced. O(1) space.",
                ],
                "dry": [
                    "At 4: 2 &lt; 4, so go left. At 2: a match.",
                    "The subtree rooted at 2 is <strong>[2, 1, 3]</strong>.",
                ],
            },
            "Recursive": {
                "idea": [
                    "The same decision as a recursive call.",
                ],
                "steps": [
                    "Return the node on a match or None; otherwise recurse into one side.",
                ],
                "why": [
                    "It is O(h) time, but CPython keeps O(h) frames (no tail-call elimination).",
                ],
                "dry": [
                    "search(4) → search(2) → match.",
                    "The result is <strong>[2, 1, 3]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ floor / ceiling
    "bst-floor-ceiling": {
        "example": {"setup": "t = build([8, 4, 12, 2, 6, 10, 14])",
                    "call": "(floor(t, 9), ceiling(t, 9), bst_min(t), bst_max(t))", "expect": "(8, 10, 2, 14)"},
        "approaches": {
            "Descend and remember the best candidate": {
                "idea": [
                    "The min and max are at the ends of the left and right spines.",
                    "Floor(x): a node ≤ x is a <em>candidate</em>, but a larger one may be to its right, so remember it and go right. A node &gt; x sends you left.",
                    "Ceiling is the mirror: a node ≥ x is a candidate, and you go left for a smaller one.",
                ],
                "steps": [
                    "One downward walk per query; the last candidate is the answer.",
                ],
                "why": [
                    "It is O(h) time and O(1) space. This is what TreeMap.floorKey and lower_bound do.",
                ],
                "dry": [
                    "The tree: 8 → (4, 12), 4 → (2, 6), 12 → (10, 14).",
                    "floor(9): 8 ≤ 9 is a candidate, go right; 12 &gt; 9, go left; 10 &gt; 9, go left; None. The floor is 8. ceiling(9): 8 &lt; 9, go right; 12 is a candidate; 10 is a better one. The ceiling is 10.",
                    "min = 2, max = 14. The result is <strong>(8, 10, 2, 14)</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ insert
    "insert-bst": {
        "example": {"call": "level_order(insert_into_bst(build([4, 2, 7, 1, 3]), 5))", "expect": "[4, 2, 7, 1, 3, 5]"},
        "approaches": {
            "Iterative: walk to the empty slot": {
                "idea": [
                    "Search for the value; where the search would fall off the tree, attach the new node.",
                    "No existing node moves, so the BST property is preserved.",
                ],
                "steps": [
                    "Go left or right; when that child is None, attach the node and return the root.",
                ],
                "why": [
                    "It is O(h) time and O(1) space.",
                ],
                "dry": [
                    "5 &gt; 4, so go right to 7. 5 &lt; 7, and 7.left is None, so attach 5 there.",
                    "The result is <strong>[4, 2, 7, 1, 3, 5]</strong>.",
                ],
            },
            "Recursive, re-linking on return": {
                "idea": [
                    "Every call returns its subtree's root, and the caller assigns it back: <code>node.left = insert(node.left, val)</code>.",
                    "That shape is what makes deletion and self-balancing trees easy later.",
                ],
                "steps": [
                    "At None, return the new node.",
                ],
                "why": [
                    "It is O(h) time and O(h) stack.",
                ],
                "dry": [
                    "insert(4) → insert(7) → insert(None) returns the new node 5, which becomes 7.left.",
                    "The result is <strong>[4, 2, 7, 1, 3, 5]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ delete
    "delete-bst": {
        "example": {"call": "vals_in(delete_node(build([5, 3, 6, 2, 4, None, 7]), 3))", "expect": "[2, 4, 5, 6, 7]"},
        "approaches": {
            "Recursive, replace with the successor": {
                "idea": [
                    "Search down and re-link on the way back, so a replaced child is hooked up automatically.",
                    "A node with zero or one child is replaced by that child (possibly None).",
                    "A node with two children takes the value of its <strong>successor</strong> (the smallest value in its right subtree), and that value is deleted from the right subtree.",
                ],
                "steps": [
                    "Find the successor; copy its value; <code>root.right = delete(root.right, succ.val)</code>.",
                ],
                "why": [
                    "The search, the successor walk and the second delete are each O(h).",
                ],
                "dry": [
                    "The tree: 5 → (3, 6), 3 → (2, 4), 6 → (None, 7). Deleting 3, which has two children.",
                    "The successor is 4 (the leftmost node in 3's right subtree). Node 3 becomes 4, and the old 4 leaf is removed.",
                    "Inorder: <strong>[2, 4, 5, 6, 7]</strong>.",
                ],
            },
            "Recursive, replace with the predecessor": {
                "idea": [
                    "The mirror image: copy the <strong>predecessor</strong> (the largest value on the left) and delete it from the left subtree.",
                    "Always using one side slowly skews a tree over many deletions; alternating helps.",
                ],
                "steps": [
                    "Find the predecessor; copy its value; <code>root.left = delete(root.left, pred.val)</code>.",
                ],
                "why": [
                    "It is O(h).",
                ],
                "dry": [
                    "The predecessor of 3 is 2. Node 3 becomes 2, and the 2 leaf is removed.",
                    "The shape differs from the successor version, but the inorder sequence is the same: <strong>[2, 4, 5, 6, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ validate
    "validate-bst": {
        "example": {"call": "is_valid_bst(build([5, 4, 6, None, None, 3, 7]))", "expect": "False"},
        "approaches": {
            "Pass down the allowed range": {
                "idea": [
                    "Checking each node only against its children is not enough: the rule covers <em>whole subtrees</em>.",
                    "Every node must lie in an open interval (lo, hi) set by its ancestors. Going left, the parent becomes the upper bound; going right, the lower bound.",
                ],
                "steps": [
                    "<code>ok(node, lo, hi)</code>, starting with (-∞, ∞).",
                ],
                "why": [
                    "It is O(n) time and O(h) stack. Use infinities, not sentinel integers.",
                ],
                "dry": [
                    "The tree: 5 → (4, 6), 6 → (3, 7).",
                    "3 is a fine left child of 6, but it lies in 5's right subtree, where the range is (5, 6). 3 is not in it.",
                    "The result is <strong>False</strong>.",
                ],
            },
            "Inorder must be strictly increasing": {
                "idea": [
                    "A tree is a BST exactly when its inorder sequence is strictly increasing.",
                    "Walk inorder iteratively and compare each value with the previous one.",
                ],
                "steps": [
                    "Return False at the first value ≤ the previous one.",
                ],
                "why": [
                    "It is O(n) and stops early.",
                ],
                "dry": [
                    "Inorder: 4, 5, then 3.",
                    "3 ≤ 5, so the result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ verify preorder
    "verify-preorder-bst": {
        "example": {"call": "verify_preorder([5, 2, 6, 1, 3])", "expect": "False"},
        "approaches": {
            "Monotonic stack with a lower bound": {
                "idea": [
                    "Simulate the traversal. The stack holds the current path of nodes whose right subtree has not started, in decreasing order.",
                    "A value larger than the top means we have moved into some ancestor's right subtree. Pop the smaller nodes; the last one popped becomes a <strong>lower bound</strong> for everything after.",
                    "A later value below that bound is impossible.",
                ],
                "steps": [
                    "Check <code>v &lt; low</code>; pop the smaller nodes and update low; push v.",
                ],
                "why": [
                    "Each value is pushed and popped once: O(n).",
                ],
                "dry": [
                    "5 → [5]. 2 → [5, 2].",
                    "6 pops 2, then 5, so low = 5 and the stack is [6].",
                    "1 &lt; low 5, which is impossible. The result is <strong>False</strong>.",
                ],
            },
            "Same idea, reusing the input as the stack": {
                "idea": [
                    "The stack never holds more than the values read so far, so the processed prefix of the array can serve as the stack, with an index <code>top</code>.",
                ],
                "steps": [
                    "Same loop with <code>preorder[top]</code> as the stack top. It modifies the input.",
                ],
                "why": [
                    "It is O(n) time and O(1) extra space.",
                ],
                "dry": [
                    "Same steps: after 6, low = 5.",
                    "1 is below it, so the result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth largest
    "kth-largest-bst": {
        "example": {"call": f"kth_largest({_K}, 2)", "expect": "5"},
        "approaches": {
            "Reverse inorder, stop at k": {
                "idea": [
                    "Inorder with the sides swapped (right, node, left) visits values in <em>decreasing</em> order. Stop at the k-th one.",
                ],
                "steps": [
                    "Push the right spine, pop, decrement k, go left.",
                ],
                "why": [
                    "It is O(h + k) time and O(h) stack.",
                ],
                "dry": [
                    _K_SHAPE,
                    "Push 5, 6. Pop 6 (k = 1). 6 has no left. Pop 5 (k = 0).",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ min abs diff
    "min-abs-diff-bst": {
        "example": {"call": "get_minimum_difference(build([1, 0, 48, None, None, 12, 49]))", "expect": "1"},
        "approaches": {
            "Inorder, compare with the previous value": {
                "idea": [
                    "Inorder gives the values in sorted order, and in a sorted list the closest pair is always adjacent.",
                    "So compare each value only with the previous one.",
                ],
                "steps": [
                    "Keep <code>prev</code>; <code>best = min(best, val - prev)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "Inorder: 0, 1, 12, 48, 49.",
                    "The gaps are 1, 11, 36 and 1.",
                    "The minimum is <strong>1</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find mode
    "find-mode-bst": {
        "example": {"call": "find_mode(build([5, 3, 7, 3, 5, 7, 7]))", "expect": "[7]"},
        "approaches": {
            "Inorder run lengths": {
                "idea": [
                    "Equal values are adjacent in inorder, so the problem becomes finding the longest runs.",
                    "Track the current run. A longer run resets the answer; an equal run adds to it.",
                ],
                "steps": [
                    "<code>run = run + 1 if val == prev else 1</code>; compare with <code>best</code>.",
                ],
                "why": [
                    "It is O(n), with no dictionary.",
                ],
                "dry": [
                    "Inorder: 3, 3, 5, 5, 7, 7, 7.",
                    "The 3-run reaches 2 (modes [3]); the 5-run ties (modes [3, 5]); the 7-run reaches 3 and resets the modes to [7].",
                    "The result is <strong>[7]</strong>.",
                ],
            },
            "Counter": {
                "idea": [
                    "Count every value and keep those with the top count. This ignores the BST property.",
                ],
                "steps": [
                    "<code>Counter(vals_in(root))</code>.",
                ],
                "why": [
                    "It is O(n) time and O(n) space.",
                ],
                "dry": [
                    "The counts are {3: 2, 5: 2, 7: 3}.",
                    "The result is <strong>[7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ increasing order search tree
    "increasing-order-search-tree": {
        "example": {"call": "level_order(increasing_bst(build([5, 3, 6, 2, 4, None, 8, 1, None, None, None, 7, 9])))",
                    "expect": "[1, None, 2, None, 3, None, 4, None, 5, None, 6, None, 7, None, 8, None, 9]"},
        "approaches": {
            "Inorder, re-link onto a tail": {
                "idea": [
                    "Visit nodes in order and hang each one off a running <code>tail</code>: clear its left pointer, set <code>tail.right = node</code>, and advance.",
                    "Start from a dummy node, so its right child is the new root.",
                ],
                "steps": [
                    "In the inorder step: <code>node.left = None; tail.right = node; tail = node</code>.",
                ],
                "why": [
                    "The node's left subtree is already done when it is re-linked, so nothing is lost. O(n).",
                ],
                "dry": [
                    "Inorder visits 1, 2, …, 9, and each is attached to the right of the previous one.",
                    "The result is the right-going chain <strong>[1, None, 2, None, 3, None, 4, None, 5, None, 6, None, 7, None, 8, None, 9]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ range sum
    "range-sum-bst": {
        "example": {"call": "range_sum_bst(build([10, 5, 15, 3, 7, None, 18]), 7, 15)", "expect": "32"},
        "approaches": {
            "DFS that prunes out-of-range subtrees": {
                "idea": [
                    "Below <code>low</code>, only the right subtree can hold values in range. Above <code>high</code>, only the left. In range: count the node and search both sides.",
                ],
                "steps": [
                    "A stack DFS that pushes only the useful children.",
                ],
                "why": [
                    "It visits the in-range nodes plus two boundary paths: O(h + m).",
                ],
                "dry": [
                    "The tree: 10 → (5, 15), 5 → (3, 7), 15 → (None, 18).",
                    "10 is in range. 15 is in range. 18 &gt; 15, so only its (empty) left is pushed. 5 &lt; 7, so only its right, 7, is pushed, and 7 is in range. 3 is never visited.",
                    "10 + 15 + 7 = <strong>32</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ trim
    "trim-bst": {
        "example": {"call": "level_order(trim_bst(build([3, 0, 4, None, 2, None, None, 1]), 1, 3))", "expect": "[3, 2, None, 1]"},
        "approaches": {
            "Recursive, return the trimmed subtree": {
                "idea": [
                    "A node below <code>low</code> is dropped together with its whole left subtree; the result is whatever trimming its right subtree produces. The same applies, mirrored, above <code>high</code>.",
                    "A node in range keeps itself and trims both children.",
                ],
                "steps": [
                    "Return the trimmed subtree's root; assign it back to the parent.",
                ],
                "why": [
                    "Dropped subtrees are skipped without being visited. The worst case is O(n).",
                ],
                "dry": [
                    "The tree: 3 → (0, 4), 0 → (None, 2), 2 → (1).",
                    "3 is in range. Its left, 0, is &lt; 1, so it is replaced by trim(2) = 2 with its child 1. Its right, 4, is &gt; 3, so it is replaced by trim(None).",
                    "The result is <strong>[3, 2, None, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ inorder successor
    "inorder-successor-bst": {
        "example": {"setup": f"t = {_K}", "call": "inorder_successor(t, find_node(t, 4)).val", "expect": "5"},
        "approaches": {
            "Descend from the root, remember the last left turn": {
                "idea": [
                    "The successor is the smallest value greater than p.val.",
                    "Walk down from the root. A node larger than p is a candidate, and anything better is to its left. Otherwise go right.",
                    "This covers both textbook cases: the minimum of p's right subtree, or the ancestor where the path last turned left.",
                ],
                "steps": [
                    "Remember the last candidate.",
                ],
                "why": [
                    "One path: O(h) time and O(1) space.",
                ],
                "dry": [
                    _K_SHAPE,
                    "At 5: 5 &gt; 4, so it is a candidate; go left. At 3: 3 ≤ 4, go right. At 4: 4 ≤ 4, go right to None.",
                    "The last candidate is <strong>5</strong>.",
                ],
            },
            "Inorder traversal, return the node after p": {
                "idea": [
                    "Walk inorder and return the node right after p. This works on any binary tree.",
                ],
                "steps": [
                    "Set a flag when p is popped; return the next pop.",
                ],
                "why": [
                    "It ignores the ordering, so it is O(n).",
                ],
                "dry": [
                    "Pops: 1, 2, 3, 4 (that is p), then 5.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sorted array to BST
    "sorted-array-to-bst": {
        "example": {"call": "level_order(sorted_array_to_bst([-10, -3, 0, 5, 9]))", "expect": "[0, -10, 5, None, -3, None, 9]"},
        "approaches": {
            "Middle as root, recurse on index ranges": {
                "idea": [
                    "Make the middle value the root. That splits the rest as evenly as possible, so the tree is balanced by construction.",
                    "Recurse on index ranges rather than slices, to avoid copying.",
                ],
                "steps": [
                    "<code>mid = (lo + hi) // 2</code>; build left from (lo, mid - 1) and right from (mid + 1, hi).",
                ],
                "why": [
                    "Each value becomes one node: O(n) time and O(log n) recursion.",
                ],
                "dry": [
                    "The whole range has mid index 2, value 0. The left range [-10, -3] has mid -10, with right child -3.",
                    "The right range [5, 9] has mid 5, with right child 9.",
                    "The result is <strong>[0, -10, 5, None, -3, None, 9]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sorted list to BST
    "sorted-list-to-bst": {
        "example": {"call": "level_order(sorted_list_to_bst(build_list([1, 2, 3, 4, 5, 6, 7])))", "expect": "[4, 2, 6, 1, 3, 5, 7]"},
        "approaches": {
            "Inorder simulation": {
                "idea": [
                    "Count the nodes, then build the tree <em>in inorder</em>: build the left half of the range, take the next list node as the root, build the right half.",
                    "Inorder consumes values in sorted order, which is exactly the order the list supplies them, so one moving pointer is enough.",
                ],
                "steps": [
                    "<code>make(lo, hi)</code>: left = make(lo, mid - 1); root = cur; advance cur; right = make(mid + 1, hi).",
                ],
                "why": [
                    "Each list node is consumed once: O(n) time and O(log n) stack.",
                ],
                "dry": [
                    "make(0, 6) first builds make(0, 2), which takes 1 as a leaf, then 2 as a root, then 3.",
                    "Then the pointer is at 4: the root. The right half takes 5, 6, 7 the same way.",
                    "The result is <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                ],
            },
            "Copy to an array": {
                "idea": [
                    "Read the list into an array and solve Sorted Array to BST.",
                ],
                "steps": [
                    "Collect the values; middle as root; recurse.",
                ],
                "why": [
                    "It is O(n) time and O(n) extra memory.",
                ],
                "dry": [
                    "vals = [1..7]; the middle 4 is the root, and 2 and 6 are the middles of the halves.",
                    "The result is <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                ],
            },
            "Fast and slow pointers for each middle": {
                "idea": [
                    "Find each range's middle node with slow/fast pointers, and split the list there.",
                ],
                "steps": [
                    "<code>recurse(head, slow)</code> for the left and <code>recurse(slow.next, tail)</code> for the right.",
                ],
                "why": [
                    "Each level of recursion walks the whole list: O(n log n).",
                ],
                "dry": [
                    "slow stops at 4 (fast reaches 7). The left part 1..3 has middle 2; the right part 5..7 has middle 6.",
                    "The result is <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ BST from preorder
    "bst-from-preorder": {
        "example": {"call": "level_order(bst_from_preorder([8, 5, 1, 7, 10, 12]))", "expect": "[8, 5, 10, 1, 7, None, 12]"},
        "approaches": {
            "One pass with value bounds": {
                "idea": [
                    "Read the values in order. The next value belongs at the current position only if it is below the inherited upper bound; otherwise this subtree is finished.",
                    "A left child's bound is its parent's value; a right child inherits the parent's bound.",
                ],
                "steps": [
                    "<code>make(hi)</code>: create a node from the next value if it fits, then build its left with <code>make(val)</code> and its right with <code>make(hi)</code>.",
                ],
                "why": [
                    "Each value is read once: O(n).",
                ],
                "dry": [
                    "8 is the root. 5 &lt; 8 goes left, and 1 &lt; 5 goes under it on the left.",
                    "7 is above 1's bound (1) and above 5's bound (5), so both are empty. It fits 5's right, whose bound is 8.",
                    "10 does not fit under 5 (bound 8), so it becomes 8's right child. 12 becomes 10's right child.",
                    "The result is <strong>[8, 5, 10, 1, 7, None, 12]</strong>.",
                ],
            },
            "Insert each value in turn": {
                "idea": [
                    "Insert the values in preorder order. Each value's ancestors were inserted before it, so the original tree is recreated.",
                ],
                "steps": [
                    "A standard BST insertion for each value.",
                ],
                "why": [
                    "Each insert is O(h): O(n²) for sorted input.",
                ],
                "dry": [
                    "Insert 8, 5 (left), 1 (left-left), 7 (left-right), 10 (right), 12 (right-right).",
                    "The result is <strong>[8, 5, 10, 1, 7, None, 12]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ greater tree
    "bst-to-greater-tree": {
        "example": {"call": "level_order(convert_bst(build([4, 1, 6, 0, 2, 5, 7, None, None, None, 3, None, None, None, 8])))",
                    "expect": "[30, 36, 21, 36, 35, 26, 15, None, None, None, 33, None, None, None, 8]"},
        "approaches": {
            "Reverse inorder with a running sum": {
                "idea": [
                    "Visit nodes from largest to smallest (right, node, left).",
                    "By the time a node is visited, every larger value has already been added to <code>running</code>, so add this node's value and write the total back.",
                ],
                "steps": [
                    "<code>running += val; node.val = running</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "The visit order is 8, 7, 6, 5, 4, 3, 2, 1, 0.",
                    "Running totals: 8, 15, 21, 26, 30, 33, 35, 36, 36.",
                    "The result is <strong>[30, 36, 21, 36, 35, 26, 15, None, None, None, 33, None, None, None, 8]</strong>.",
                ],
            },
            "Reverse Morris traversal": {
                "idea": [
                    "Morris threading with left and right swapped: thread each right subtree's leftmost node back to its ancestor, then visit in decreasing order with no stack.",
                ],
                "steps": [
                    "Visit when there is no right child, or when the thread is found and removed.",
                ],
                "why": [
                    "It is O(n) time and O(1) space; pointers are modified temporarily.",
                ],
                "dry": [
                    "The same visit order and running totals.",
                    "The result is <strong>[30, 36, 21, 36, 35, 26, 15, None, None, None, 33, None, None, None, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ balance BST
    "balance-bst": {
        "example": {"call": "level_order(balance_bst(build([1, None, 2, None, 3, None, 4, None, 5, None, 6, None, 7])))",
                    "expect": "[4, 2, 6, 1, 3, 5, 7]"},
        "approaches": {
            "Inorder to a list, rebuild from the middle": {
                "idea": [
                    "Inorder gives the nodes in sorted order; then build exactly as in Sorted Array to BST, re-using the same node objects.",
                ],
                "steps": [
                    "Collect the nodes; <code>make(lo, hi)</code> with the middle as the root.",
                ],
                "why": [
                    "Both phases are O(n), with an O(n) list.",
                ],
                "dry": [
                    "The input is a right-leaning chain 1 → 2 → … → 7.",
                    "The middle 4 becomes the root, 2 and 6 the next level, then 1, 3, 5, 7.",
                    "The result is <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                ],
            },
            "Day&ndash;Stout&ndash;Warren: rotations only": {
                "idea": [
                    "Balance in place with rotations only.",
                    "Phase 1: right-rotate until the tree is a right-leaning \"vine\" (a sorted list through the right pointers).",
                    "Phase 2: left-rotate every other node on the vine, halving its length each round. This folds it into a balanced tree.",
                ],
                "steps": [
                    "First fold the extra nodes beyond a perfect size into the bottom level; then keep halving.",
                ],
                "why": [
                    "O(n) rotations in total, each O(1): O(n) time and O(1) extra space.",
                ],
                "dry": [
                    "The chain is already a vine of 7 nodes; 7 is a perfect size, so no extra nodes need folding.",
                    "Fold 3 times → 2 – 4 – 6 on the spine; fold once → 4 at the top.",
                    "The result is <strong>[4, 2, 6, 1, 3, 5, 7]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ BST to sorted DLL
    "bst-to-sorted-dll": {
        "example": {"setup": "head = tree_to_doubly_list(build([4, 2, 5, 1, 3]))",
                    "call": "[head.val, head.right.val, head.right.right.val, head.left.val]", "expect": "[1, 2, 3, 5]"},
        "approaches": {
            "Inorder, link each node to the previous one": {
                "idea": [
                    "Walk inorder, keeping <code>prev</code> (the last node linked) and <code>head</code> (the first).",
                    "For each node: <code>prev.right = node</code> and <code>node.left = prev</code>. At the end, link head and prev to close the circle.",
                ],
                "steps": [
                    "Link in the inorder step; close the circle after the walk.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack, done in place.",
                ],
                "dry": [
                    "The tree: 4 → (2, 5), 2 → (1, 3). Inorder: 1, 2, 3, 4, 5.",
                    "Links: 1 ⇄ 2 ⇄ 3 ⇄ 4 ⇄ 5, then 5 ⇄ 1 closes the circle.",
                    "head = 1, then 2, 3, and head.left = 5. The result is <strong>[1, 2, 3, 5]</strong>.",
                ],
            },
        },
    },
}
