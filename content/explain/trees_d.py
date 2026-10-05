"""Write-ups for Trees, part D: tree as graph, shape, modification, tree DP, aggregation."""

_LCA_T = "t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])"
_LCA_SHAPE = "The tree: 3 → (5, 1), 5 → (6, 2), 2 → (7, 4), 1 → (0, 8)."

EXPLAIN = {
    # ------------------------------------------------------------------ distance K
    "all-nodes-distance-k": {
        "example": {"setup": _LCA_T, "call": "distance_k(t, find_node(t, 7), 3)", "expect": "[3, 6]"},
        "approaches": {
            "Parent map, then BFS from the target": {
                "idea": [
                    "Distance can go <em>up</em> through parents, which child pointers do not allow.",
                    "So record every node's parent first. Then each node has up to three neighbours (left, right, parent), and this is plain BFS on an undirected graph.",
                    "Expand k rings out from the target, with a visited set so you never walk back.",
                ],
                "steps": [
                    "Build the parent map with one traversal.",
                    "Run BFS for k rounds; the last ring is the answer, sorted.",
                ],
                "why": [
                    "It is O(n) time and O(n) for the map and the set.",
                ],
                "dry": [
                    _LCA_SHAPE,
                    "Ring 0: {7}. Ring 1: {2}. Ring 2: {4, 5}.",
                    "Ring 3: 4 adds nothing new; 5 adds 6 and 3. The result is <strong>[3, 6]</strong>.",
                ],
            },
            "One DFS returning distance to the target": {
                "idea": [
                    "Each call returns how far the target is below it (-1 if it is not below).",
                    "When an ancestor learns the target is d edges down one side, the nodes at distance k on its <em>other</em> side are k - d - 2 levels below that other child.",
                    "The ancestor itself counts when d + 1 == k. At the target, collect everything k levels down.",
                ],
                "steps": [
                    "<code>collect(node, depth)</code> gathers the nodes exactly <code>depth</code> levels below.",
                ],
                "why": [
                    "It is O(n) time with only O(h) stack, but trickier to get right.",
                ],
                "dry": [
                    "At 7 (the target): nothing is 3 below it. It returns 0.",
                    "At 2: d = 0, so collect(4, 1), which finds nothing. Return 1. At 5: d = 1, so collect(6, 0) adds 6. Return 2.",
                    "At 3: d + 1 = 3 = k, so add 3. The result is <strong>[3, 6]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find distance
    "find-distance": {
        "example": {"setup": _LCA_T, "call": "find_distance(t, 6, 4)", "expect": "3"},
        "approaches": {
            "LCA, then two depths": {
                "idea": [
                    "The path from p to q goes up to their LCA and back down.",
                    "So the distance = (LCA down to p) + (LCA down to q).",
                ],
                "steps": [
                    "Find the LCA with the standard postorder search; measure both depths from it.",
                ],
                "why": [
                    "Three O(n) passes with O(h) stack.",
                ],
                "dry": [
                    _LCA_SHAPE,
                    "LCA(6, 4) = 5. From 5: 6 is 1 down and 4 is 2 down.",
                    "1 + 2 = <strong>3</strong>.",
                ],
            },
            "One pass: return the distance found so far": {
                "idea": [
                    "Each call returns the distance down to whichever target it found, or -1.",
                    "If both sides report a distance, this node is the LCA: answer = left + right + 2.",
                    "If this node is a target and the other is below it, answer = below + 1.",
                ],
                "steps": [
                    "A postorder pass that sets <code>answer</code> once.",
                ],
                "why": [
                    "One pass instead of three, with more cases to handle.",
                ],
                "dry": [
                    "6 is a target, so it returns 0. Under 2, 4 is a target and returns 0, so 2 returns 1.",
                    "At 5: left 0 and right 1 are both found, so answer = 0 + 1 + 2.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ time to infect
    "time-to-infect": {
        "example": {"call": "amount_of_time(build([1, 5, 3, None, 4, 10, 6, 9, 2]), 3)", "expect": "4"},
        "approaches": {
            "Build the graph, BFS by minutes": {
                "idea": [
                    "Infection spreads to all neighbours, parent included, so add parent links and BFS from the start node.",
                    "Each BFS ring is one minute; the answer is the number of rings after the start.",
                ],
                "steps": [
                    "Record parents and find the start node; BFS until nothing new is reached.",
                ],
                "why": [
                    "This is Distance K run until the queue is empty: O(n).",
                ],
                "dry": [
                    "The tree: 1 → (5, 3), 5 → (None, 4), 4 → (9, 2), 3 → (10, 6).",
                    "Minute 0: {3}. 1: {10, 6, 1}. 2: {5}. 3: {4}. 4: {9, 2}.",
                    "The result is <strong>4</strong>.",
                ],
            },
            "One DFS: depth below and distance to start": {
                "idea": [
                    "The farthest node from the start is either deep below it, or up d edges at some ancestor and then down that ancestor's <em>other</em> subtree.",
                    "Return a subtree's depth as a positive number, or the distance to the start as a <em>negative</em> number when the start is inside. One integer carries both kinds of answer.",
                ],
                "steps": [
                    "At the start: <code>best = max(left, right)</code>; return -1.",
                    "At an ancestor: <code>best = max(best, dist + other side's depth)</code>; return <code>-(dist + 1)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack, with no parent map.",
                ],
                "dry": [
                    "At 3 (the start): both children have depth 1, so best = 1. It returns -1.",
                    "5's subtree has depth 3. At 1: the distance to the start is 1, and the other side's depth is 3, so best = 4.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count complete tree nodes
    "count-complete-tree-nodes": {
        "example": {"call": "count_nodes(build([1, 2, 3, 4, 5, 6]))", "expect": "6"},
        "approaches": {
            "Plain DFS count": {
                "idea": [
                    "Count = 1 + left count + right count. This ignores the \"complete\" guarantee entirely.",
                ],
                "steps": [
                    "Recurse into both children.",
                ],
                "why": [
                    "It is O(n), and the problem asks for better.",
                ],
                "dry": [
                    "Visits all 6 nodes.",
                    "The result is <strong>6</strong>.",
                ],
            },
            "Compare left spine heights": {
                "idea": [
                    "In a complete tree, walking left children from a node gives that subtree's height in O(log n).",
                    "Compare the left child's spine with the right child's. If they are equal, the <em>left</em> subtree is perfect: 2<sup>h</sup> - 1 nodes by formula.",
                    "If they differ, the <em>right</em> subtree is perfect, one level shorter.",
                    "Either way, recurse into only one child.",
                ],
                "steps": [
                    "Equal: <code>(1 &lt;&lt; lh) + count(right)</code>. Different: <code>(1 &lt;&lt; rh) + count(left)</code>. The 1 &lt;&lt; h already includes the root.",
                ],
                "why": [
                    "There are O(log n) levels of recursion, each doing an O(log n) spine walk: O(log² n).",
                ],
                "dry": [
                    "At 1: the left spine (2 → 4) is 2 and the right spine (3 → 6) is 2. They are equal, so 4 + count(3).",
                    "At 3: the spines are 1 vs 0, so 1 + count(6). count(6) = 1.",
                    "4 + 1 + 1 = <strong>6</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ completeness
    "check-completeness": {
        "example": {"call": "is_complete(build([1, 2, 3, 4, 5, None, 7]))", "expect": "False"},
        "approaches": {
            "BFS, allowing None into the queue": {
                "idea": [
                    "Enqueue children even when they are None. BFS then visits positions in the order an array heap would.",
                    "The tree is complete exactly when no real node comes after the first None.",
                ],
                "steps": [
                    "On None, set <code>seen_gap</code>; on a real node after a gap, return False.",
                ],
                "why": [
                    "It is O(n) time and O(w) queue.",
                ],
                "dry": [
                    "Order: 1, 2, 3, 4, 5, None (3's missing left child), 7.",
                    "7 comes after a gap.",
                    "The result is <strong>False</strong>.",
                ],
            },
            "Index-based DFS": {
                "idea": [
                    "Number the nodes like a heap: root 1, children 2i and 2i + 1.",
                    "The tree is complete exactly when the largest index equals the node count.",
                ],
                "steps": [
                    "Return <code>(count, largest index)</code> from each subtree.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack, but indices double per level, so very deep trees produce huge numbers.",
                ],
                "dry": [
                    "Indices: 1, 2, 3, 4, 5, and 7 for the node 7.",
                    "There are 6 nodes but the largest index is 7.",
                    "The result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum width
    "maximum-width": {
        "example": {"call": "width_of_binary_tree(build([1, 3, 2, 5, None, None, 9, 6, None, 7]))", "expect": "7"},
        "approaches": {
            "BFS with positions, re-based per level": {
                "idea": [
                    "Give each node its heap position (left child 2p, right child 2p + 1). A level's width is last - first + 1, counting the gaps.",
                    "Subtract the level's first position from every position at the start of the level, so the numbers stay small.",
                ],
                "steps": [
                    "Per level: update <code>best</code>; build the next level with re-based positions.",
                ],
                "why": [
                    "It is O(n) time and O(w) queue.",
                ],
                "dry": [
                    "The tree: 1 → (3, 2), 3 → (5), 2 → (None, 9), 5 → (6), 9 → (7).",
                    "Level 2: 5 at 0 and 9 at 3, width 4. Level 3: 6 at 0 and 7 at 2·3 = 6, width 7.",
                    "The result is <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ all full binary trees
    "all-possible-full-binary-trees": {
        "example": {"call": "len(all_possible_fbt(7))", "expect": "5"},
        "approaches": {
            "Memoised recursion over sizes": {
                "idea": [
                    "A full tree of n nodes is a root with a full left tree of odd size L and a full right tree of size n - 1 - L.",
                    "Pair every left tree with every right tree for every split, and cache the list for each size.",
                    "Even n is impossible, so return [].",
                ],
                "steps": [
                    "<code>for left in range(1, n, 2)</code>: combine <code>fbt(left)</code> × <code>fbt(n - 1 - left)</code>.",
                ],
                "why": [
                    "The output size is a Catalan number, so you cannot do better. Cached trees share subtrees.",
                ],
                "dry": [
                    "fbt(1) has 1 tree, fbt(3) has 1, fbt(5) has 1·1 + 1·1 = 2.",
                    "fbt(7): splits (1, 5), (3, 3), (5, 1) give 2 + 1 + 2.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ flatten
    "flatten-to-linked-list": {
        "example": {"setup": "t = build([1, 2, 5, 3, 4, None, 6])\nflatten(t)",
                    "call": "level_order(t)", "expect": "[1, None, 2, None, 3, None, 4, None, 5, None, 6]"},
        "approaches": {
            "Splice the left subtree in, iteratively": {
                "idea": [
                    "In preorder, a node's right subtree comes right after the <em>last</em> node of its left subtree, which is that subtree's rightmost node.",
                    "So hang the right subtree off that rightmost node, move the left subtree to the right, clear the left, and step right.",
                ],
                "steps": [
                    "Find <code>tail</code>; <code>tail.right = node.right</code>; <code>node.right, node.left = node.left, None</code>.",
                ],
                "why": [
                    "Each edge is walked at most twice: O(n) time with O(1) space.",
                ],
                "dry": [
                    "The tree: 1 → (2, 5), 2 → (3, 4), 5 → (None, 6).",
                    "At 1: the tail of the left subtree is 4, so 4.right = 5, and 1.right = 2. At 2: the tail is 3, so 3.right = 4, and 2.right = 3.",
                    "Stepping right: 3, 4, 5, 6. The list reads 1 → 2 → 3 → 4 → 5 → 6, so the level order is <strong>[1, None, 2, None, 3, None, 4, None, 5, None, 6]</strong>.",
                ],
            },
            "Reverse preorder with a prev pointer": {
                "idea": [
                    "Visit nodes in reverse preorder (right, left, root), and point each node's right at the node visited just before it.",
                    "Everything after a node in preorder is already linked, so nothing is lost.",
                ],
                "steps": [
                    "<code>node.right, node.left = prev, None</code>; <code>prev = node</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "The visit order is 6, 5, 4, 3, 2, 1, each pointing right at the previous one.",
                    "The result is <strong>[1, None, 2, None, 3, None, 4, None, 5, None, 6]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pruning
    "binary-tree-pruning": {
        "example": {"call": "level_order(prune_tree(build([1, 0, 1, 0, 0, 0, 1])))", "expect": "[1, None, 1, None, 1]"},
        "approaches": {
            "Postorder, return the pruned subtree": {
                "idea": [
                    "Prune both children first and assign the results back.",
                    "Then this node survives if it is a 1 or still has a child; otherwise return None and the parent drops it.",
                ],
                "steps": [
                    "<code>root.left = prune(root.left)</code>, the same for the right, then decide.",
                ],
                "why": [
                    "Returning the new subtree root means the function never needs to know its parent: O(n).",
                ],
                "dry": [
                    "The tree: 1 → (0, 1), 0 → (0, 0), 1 → (0, 1).",
                    "The left 0's children are both 0-leaves, so they are removed, and then it is a childless 0, so it goes too. On the right, the 0-leaf goes and the 1 stays.",
                    "The result is <strong>[1, None, 1, None, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ delete leaves
    "delete-leaves-with-value": {
        "example": {"call": "level_order(remove_leaf_nodes(build([1, 2, 3, 2, None, 2, 4]), 2))", "expect": "[1, None, 3, None, 4]"},
        "approaches": {
            "Postorder, re-check after children": {
                "idea": [
                    "After deleting within both children, a node may <em>become</em> a leaf. Check it after its children, so the deletions cascade upwards in one pass.",
                ],
                "steps": [
                    "Recurse into both children; if the node is now a leaf with the target value, return None.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack. Preorder would miss the cascade.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), 2 → (2), 3 → (2, 4).",
                    "The leaf 2s are deleted. Then the upper 2 has become a leaf, so it is deleted too.",
                    "The result is <strong>[1, None, 3, None, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ house robber III
    "house-robber-iii": {
        "example": {"call": "rob(build([3, 4, 5, 1, 3, None, 1]))", "expect": "9"},
        "approaches": {
            "Return (with node, without node)": {
                "idea": [
                    "For each subtree, return two numbers: the best total if its root is robbed, and if it is not.",
                    "Robbing a node forbids both children, so add their <em>without</em> values. Skipping it lets each child pick its better option.",
                ],
                "steps": [
                    "<code>with = val + lo + ro</code>; <code>without = max(lw, lo) + max(rw, ro)</code>.",
                ],
                "why": [
                    "Two numbers per node in one pass: O(n). This is the standard two-state tree DP.",
                ],
                "dry": [
                    "The tree: 3 → (4, 5), 4 → (1, 3), 5 → (None, 1).",
                    "Node 4: (4, 1 + 3) = (4, 4). Node 5: (5, 1).",
                    "Root: with = 3 + 4 + 1 = 8, without = 4 + 5 = 9. The result is <strong>9</strong>.",
                ],
            },
            "Memoised grandchildren recursion": {
                "idea": [
                    "Either rob this node and continue at the four grandchildren, or skip it and continue at the two children. Cache by node.",
                ],
                "steps": [
                    "<code>memo[node] = max(take, skip)</code>.",
                ],
                "why": [
                    "Without the memo it is exponential; with it, O(n) time and O(n) memory.",
                ],
                "dry": [
                    "best(4) = max(4, 1 + 3) = 4; best(5) = max(5, 1) = 5.",
                    "Root: take = 3 + 1 + 3 + 1 = 8, skip = 4 + 5 = 9.",
                    "The result is <strong>9</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ cameras
    "binary-tree-cameras": {
        "example": {"call": "min_camera_cover(build([0, 0, None, 0, None, 0, None, None, 0]))", "expect": "2"},
        "approaches": {
            "Greedy postorder with three states": {
                "idea": [
                    "Each node reports one of three states: UNCOVERED, CAMERA, or COVERED (without a camera). An empty child counts as COVERED.",
                    "If any child is uncovered, this node must have a camera. If a child has a camera, this node is covered. Otherwise leave it uncovered for the parent to handle.",
                    "Putting cameras as high as possible is never worse. The root has no parent, so if it ends uncovered it gets a camera itself.",
                ],
                "steps": [
                    "Postorder; count cameras; fix up the root at the end.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "The tree is a chain of five: a → b → c → d → e (e is d's right child).",
                    "e is UNCOVERED, so d takes a camera (1). c is COVERED, b is UNCOVERED, so a takes a camera (2).",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Exact DP over three costs": {
                "idea": [
                    "Compute three costs per node: (a) camera here, (b) covered by a child, (c) not covered yet. Let <code>min</code> decide instead of trusting the greedy rule.",
                ],
                "steps": [
                    "<code>a = 1 + min(all left) + min(all right)</code>; <code>b</code> = a child has a camera; <code>c = lb + rb</code>.",
                ],
                "why": [
                    "It is O(n) with more code, and useful for checking the greedy answer.",
                ],
                "dry": [
                    "Triples from e upwards: (1, ∞, 0), (1, 1, ∞), (2, 1, 1), (2, 2, 1), (2, 2, 2).",
                    "The root's min(a, b) = <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ distribute coins
    "distribute-coins": {
        "example": {"call": "distribute_coins(build([0, 3, 0]))", "expect": "3"},
        "approaches": {
            "Postorder excess flow": {
                "idea": [
                    "Think per edge, not per coin. A subtree with <code>coins - nodes = e</code> must send |e| coins across the edge to its parent (up if positive, down if negative).",
                    "So return each subtree's excess, and add <code>|left| + |right|</code> at every node.",
                ],
                "steps": [
                    "<code>moves += abs(left) + abs(right)</code>; return <code>val + left + right - 1</code>.",
                ],
                "why": [
                    "Moving coins both ways across one edge would be wasted, so |excess| moves per edge is the minimum. O(n).",
                ],
                "dry": [
                    "The left child has 3 coins for 1 node: excess +2. The right has 0: excess -1.",
                    "At the root: moves = 2 + 1.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ good nodes
    "count-good-nodes": {
        "example": {"call": "good_nodes(build([3, 1, 4, 3, None, 1, 5]))", "expect": "4"},
        "approaches": {
            "Carry the path maximum down": {
                "idea": [
                    "A node is good if no node above it is larger, so pass down the largest value on the path.",
                    "A node is good if it is ≥ that maximum, and it raises the maximum for its children.",
                ],
                "steps": [
                    "<code>good = val &gt;= best</code>; recurse with <code>max(best, val)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "The tree: 3 → (1, 4), 1 → (3), 4 → (1, 5).",
                    "Good: the root 3, the 3 under 1 (path max 3), 4, and 5. Not good: both 1s.",
                    "The result is <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ nodes equal average
    "nodes-equal-average": {
        "example": {"call": "average_of_subtree(build([4, 8, 5, 0, 1, None, 6]))", "expect": "5"},
        "approaches": {
            "Return (sum, size)": {
                "idea": [
                    "Each subtree reports its sum and node count; the parent adds itself and checks <code>total // size == val</code>.",
                ],
                "steps": [
                    "Postorder returning pairs; count the matches.",
                ],
                "why": [
                    "Reusing children's aggregates gives O(n) instead of O(n²).",
                ],
                "dry": [
                    "The leaves 0, 1 and 6 match themselves. 8: 9 // 3 = 3 ≠ 8. 5: 11 // 2 = 5 ✓.",
                    "The root 4: 24 // 6 = 4 ✓.",
                    "The result is <strong>5</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ most frequent subtree sum
    "most-frequent-subtree-sum": {
        "example": {"call": "find_frequent_tree_sum(build([5, 2, -5]))", "expect": "[2]"},
        "approaches": {
            "Postorder sums into a Counter": {
                "idea": [
                    "Each call returns its subtree sum and records it in a Counter. At the end, return every sum with the top count.",
                ],
                "steps": [
                    "<code>counts[s] += 1</code>; then filter by the maximum count.",
                ],
                "why": [
                    "It is O(n) time and O(n) for the counter.",
                ],
                "dry": [
                    "The sums are 2 (the leaf), -5 (the leaf), and 5 + 2 - 5 = 2 (the root).",
                    "2 appears twice.",
                    "The result is <strong>[2]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ duplicate subtrees
    "find-duplicate-subtrees": {
        "example": {"call": "sorted(level_order(x) for x in find_duplicate_subtrees(build([1, 2, 3, 4, None, 2, 4, None, None, 4])))",
                    "expect": "[[2, 4], [4]]"},
        "approaches": {
            "Intern each subtree as an integer id": {
                "idea": [
                    "Identify a subtree by the triple <code>(left id, value, right id)</code>, and give each distinct triple a small integer id.",
                    "Two subtrees are identical exactly when they get the same id. Report a node the <em>second</em> time its id appears.",
                ],
                "steps": [
                    "<code>uid = ids.setdefault(triple, len(ids) + 1)</code>; count it.",
                ],
                "why": [
                    "Each triple has a constant size, so this is O(n).",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), 2 → (4), 3 → (2, 4), and that second 2 → (4).",
                    "A leaf 4 is (0, 4, 0), id 1. A 2 with a left 4 is (1, 2, 0), id 2.",
                    "The second leaf 4 and the second 2 are duplicates. Sorted level orders: <strong>[[2, 4], [4]]</strong>.",
                ],
            },
            "Serialize every subtree to a string": {
                "idea": [
                    "Build a string like <code>(2,(4,#,#),#)</code> for each subtree and count them.",
                ],
                "steps": [
                    "Report a node on the second occurrence of its string.",
                ],
                "why": [
                    "Strings copy their children: O(n²) on a chain. The integer ids above fix this.",
                ],
                "dry": [
                    "\"(4,#,#)\" appears three times; \"(2,(4,#,#),#)\" appears twice.",
                    "The result is <strong>[[2, 4], [4]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth smallest
    "kth-smallest-bst": {
        "example": {"call": "kth_smallest(build([5, 3, 6, 2, 4, None, None, 1]), 3)", "expect": "3"},
        "approaches": {
            "Iterative inorder, stop at k": {
                "idea": [
                    "Inorder on a BST yields values in sorted order, so the k-th pop is the answer.",
                    "The iterative version can stop right there, leaving the rest of the tree untouched.",
                ],
                "steps": [
                    "Push the left spine, pop, decrement k, go right.",
                ],
                "why": [
                    "It is O(h + k) time and O(h) stack.",
                ],
                "dry": [
                    "The tree: 5 → (3, 6), 3 → (2, 4), 2 → (1).",
                    "Push 5, 3, 2, 1. Pop 1 (k = 2), pop 2 (k = 1), pop 3 (k = 0).",
                    "The result is <strong>3</strong>.",
                ],
            },
            "Morris inorder, stopped at k": {
                "idea": [
                    "Morris inorder visits in sorted order with O(1) space, using temporary threads.",
                    "It records the k-th value but keeps going, so every thread is removed and the tree is restored.",
                ],
                "steps": [
                    "Visit a node when it has no left child, or when its thread is found and removed.",
                ],
                "why": [
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "The visit order is 1, 2, 3, 4, 5, 6. The third visit records 3.",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },
}
