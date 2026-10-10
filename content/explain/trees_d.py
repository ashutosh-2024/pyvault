"""Write-ups for Trees, part D: distances, shape checks, tree DP, subtree aggregates."""

_LCA_T = "t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])"
_LCA_SHAPE = "The tree: 3 → (5, 1), 5 → (6, 2), 1 → (0, 8), 2 → (7, 4)."

EXPLAIN = {
    # ------------------------------------------------------------------ all nodes distance k
    "all-nodes-distance-k": {
        "examples": [
            {"setup": _LCA_T, "call": "distance_k(t, find_node(t, 5), 2)", "expect": "[1, 4, 7]"},
            {"setup": _LCA_T, "call": "distance_k(t, find_node(t, 7), 3)", "expect": "[3, 6]"},
        ],
        "approaches": {
            "Parent map, then BFS from the target": {
                "idea": [
                    "Distance in a tree can go up as well as down, and tree nodes only point down. Adding a parent link turns the tree into an undirected graph.",
                    "In that graph, the nodes at distance k are exactly BFS ring number k around the target.",
                    "A <code>seen</code> set stops the BFS from walking back the way it came.",
                ],
                "steps": [
                    "Fill <code>parent</code> with an iterative DFS from the root (the root's parent is <code>None</code>).",
                    "Start with <code>seen = {target}</code> and <code>ring = [target]</code>.",
                    "Repeat k times: for each node in <code>ring</code>, look at <code>node.left</code>, <code>node.right</code> and <code>parent[node]</code>.",
                    "Each neighbour that exists and is not in <code>seen</code> is marked and goes into <code>nxt</code>; then <code>ring = nxt</code>.",
                    "Return the sorted values of <code>ring</code>.",
                ],
                "why": [
                    "A tree has exactly one path between two nodes, so a BFS ring at step k holds precisely the nodes whose path to the target has k edges.",
                    "If the rings run out early (k larger than any distance), <code>ring</code> becomes empty and the answer is [].",
                    "The DFS and the BFS each touch every node at most once: <strong>O(n)</strong> time.",
                    "<code>parent</code> and <code>seen</code> hold up to n nodes: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        _LCA_SHAPE + " Target 5, k = 2.",
                        "Ring 0: [5].",
                        "Ring 1: 5's children 6, 2 and its parent 3: [6, 2, 3].",
                        "Ring 2: 6 adds nothing new; 2 adds 7 and 4; 3 adds 1 (its left child 5 is seen). [7, 4, 1].",
                        "Sorted: <strong>[1, 4, 7]</strong>.",
                    ],
                    [
                        "Target 7 (a leaf), k = 3.",
                        "Ring 1: only its parent 2.",
                        "Ring 2: 2's other child 4 and its parent 5: [4, 5].",
                        "Ring 3: 4 adds nothing; 5 adds 6 and its parent 3: [6, 3].",
                        "Sorted: <strong>[3, 6]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>seen</code> needed in a tree?",
                     "With parent links, every edge can be walked both ways. Without <code>seen</code>, ring 2 would contain the target again via child → parent."],
                    ["What if k is 0?",
                     "The loop does not run and <code>ring</code> is just <code>[target]</code>, so the answer is the target's own value."],
                    ["Why sort at the end?",
                     "The problem accepts any order; sorting gives one fixed order so results can be compared in tests."],
                ],
            },
            "One DFS returning distance to the target": {
                "idea": [
                    "Nodes at distance k are of two kinds: below the target at depth k, or reached by going up to some ancestor and then down its <em>other</em> side.",
                    "A DFS that returns the distance from each node down to the target tells every ancestor how far away it is.",
                    "An ancestor at distance d + 1 is itself an answer when d + 1 == k; otherwise it sends a <code>collect</code> into its other child for the remaining <code>k - d - 2</code> steps.",
                ],
                "steps": [
                    "<code>collect(node, depth)</code> adds every node exactly <code>depth</code> levels below <code>node</code> to <code>out</code>.",
                    "<code>dfs(node)</code> returns −1 if the target is not in this subtree.",
                    "At the target: <code>collect(node, k)</code> for the nodes below, and return 0.",
                    "Otherwise try each child <code>here</code> with its sibling <code>other</code>. If <code>dfs(here)</code> gives <code>d != -1</code>: add <code>node.val</code> if <code>d + 1 == k</code>, else <code>collect(other, k - d - 2)</code>. Return <code>d + 1</code>.",
                    "Call <code>dfs(root)</code> and return <code>sorted(out)</code>.",
                ],
                "why": [
                    "Every node at distance k has a unique highest point on its path to the target: either the target itself (handled by the first collect) or one ancestor (handled at that ancestor).",
                    "The sibling subtree is entered one edge below the ancestor, so it needs <code>k - (d + 1) - 1</code> more levels; a negative value means none fit and <code>collect</code> stops at once.",
                    "Each node is visited by <code>dfs</code> at most once and by <code>collect</code> at most once: <strong>O(n)</strong> time.",
                    "No parent map is stored, only the recursion: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "dfs reaches 5, the target: collect(5, 2) finds 7 and 4.",
                        "dfs(5) returns 0 to 3. At 3: d = 0, d + 1 = 1 ≠ 2.",
                        "collect(1, 2 − 0 − 2 = 0) adds 1 itself.",
                        "out = [7, 4, 1].",
                        "Sorted: <strong>[1, 4, 7]</strong>.",
                    ],
                    [
                        "At the target 7: collect(7, 3) finds nothing. Returns 0.",
                        "At 2: d = 0, collect(4, 1) finds nothing (4 is a leaf). Returns 1.",
                        "At 5: d = 1, collect(6, 0) adds 6. Returns 2.",
                        "At 3: d = 2, d + 1 == 3, so 3 itself is added.",
                        "Sorted: <strong>[3, 6]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>k - d - 2</code>?",
                     "The ancestor is <code>d + 1</code> from the target, and stepping into its other child costs one more edge. The remaining budget is <code>k - (d + 1) - 1</code>."],
                    ["Why does the ancestor return right after the first child that finds the target?",
                     "The target is in only one subtree. Once found, the other child has been handled by <code>collect</code> and there is nothing else to search."],
                    ["Which approach is easier in an interview?",
                     "The parent map plus BFS: it is harder to get wrong. The one-pass DFS saves the O(n) map, at the cost of the distance arithmetic."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find distance
    "find-distance": {
        "examples": [
            {"setup": _LCA_T, "call": "find_distance(t, 6, 4)", "expect": "3"},
            {"setup": _LCA_T, "call": "find_distance(t, 5, 7)", "expect": "2"},
        ],
        "approaches": {
            "LCA, then two depths": {
                "idea": [
                    "The path between p and q goes up to their lowest common ancestor and back down, so the distance is depth(p) + depth(q) measured from the LCA.",
                    "Find the LCA with the standard postorder search, comparing values since p and q are given as values.",
                    "Then search the LCA's subtree twice to measure each depth.",
                ],
                "steps": [
                    "<code>lca(node)</code> returns <code>node</code> if it is <code>None</code> or holds p or q; otherwise it combines the two sides as in the LCA problem.",
                    "<code>depth_of(node, val, d)</code> returns the depth of <code>val</code> below <code>node</code>, or −1 if it is not there; it tries left, then right.",
                    "Set <code>top = lca(root)</code>.",
                    "Return <code>depth_of(top, p, 0) + depth_of(top, q, 0)</code>.",
                ],
                "why": [
                    "In a tree the unique p–q path passes through the LCA, and from there it only goes down, so its length is the sum of the two depths below the LCA.",
                    "When one target is the LCA itself, its depth is 0 and the other depth is the whole distance.",
                    "Three passes, each at most O(n): <strong>O(n)</strong> time.",
                    "Only recursion: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        _LCA_SHAPE + " p = 6, q = 4.",
                        "lca: 5 gets 6 from the left and 4 from the right (via 2), so top = 5.",
                        "depth_of(5, 6) = 1.",
                        "depth_of(5, 4): the left side (6) gives −1, the right side gives 2.",
                        "1 + 2 = <strong>3</strong>.",
                    ],
                    [
                        "p = 5, q = 7.",
                        "lca returns 5 as soon as it reaches it; the right side of 3 finds nothing. top = 5.",
                        "depth_of(5, 5) = 0 and depth_of(5, 7) = 2 (5 → 2 → 7).",
                        "0 + 2 = <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["What if p == q?",
                     "<code>lca</code> returns that node and both depths are 0, so the answer is 0 with no special case."],
                    ["Why search only below <code>top</code>?",
                     "Both nodes are in the LCA's subtree by definition, and measuring from it gives the depths needed directly."],
                    ["Does this assume distinct values?",
                     "Yes. With repeated values, \"the node with value p\" is not well defined."],
                ],
            },
            "One pass: return the distance found so far": {
                "idea": [
                    "Do everything in one postorder pass. Each call returns how far below it the one target it has found is, or −1 for none.",
                    "Where both sides report a target, this node is the LCA and the distance is <code>left + right + 2</code>.",
                    "Where a node is itself a target and the other one is already below it, the distance is that depth + 1.",
                ],
                "steps": [
                    "If <code>p == q</code>, return 0.",
                    "<code>dfs(None)</code> returns −1; otherwise compute <code>left</code> and <code>right</code> first.",
                    "If <code>node.val</code> is p or q: if a target was found below, set <code>answer = below + 1</code>. Return 0.",
                    "If both sides found something, set <code>answer = left + right + 2</code> and return −1 so nothing above changes it.",
                    "Otherwise pass up <code>found + 1</code>, or −1 if nothing was found.",
                ],
                "why": [
                    "A returned value d means a target is d edges below the child, hence d + 1 below the current node, which is why the LCA adds 2 in total.",
                    "Exactly one node sets <code>answer</code>: the LCA, whether it is a separate node or one of the targets.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion only: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "6 is a target with nothing below: returns 0. 4 also returns 0.",
                        "2 gets −1 from 7 and 0 from 4: passes up 1.",
                        "5 gets left 0 and right 1: answer = 0 + 1 + 2 = 3, returns −1.",
                        "1's side finds nothing; 3 passes up −1.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "7 is a target: returns 0. 2 passes up 1.",
                        "5 is a target and gets left −1, right 1: below = 1, so answer = 2. Returns 0.",
                        "3 passes up 1, which nobody uses.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the LCA return −1 instead of a distance?",
                     "The answer is already settled. Returning −1 makes every ancestor see \"nothing found\", so it cannot overwrite <code>answer</code>."],
                    ["Why is <code>p == q</code> handled up front?",
                     "With equal values, the target node would find nothing below itself and <code>answer</code> would stay 0, which happens to be right, but the early return makes the intent clear and skips the walk."],
                    ["Why recurse before checking the node?",
                     "A target node needs to know whether the other target is in its subtree, so the children must report first: postorder."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ time to infect
    "time-to-infect": {
        "examples": [
            {"call": "amount_of_time(build([1, 5, 3, None, 4, 10, 6, 9, 2]), 3)", "expect": "4"},
            {"call": "amount_of_time(build([1, 2, None, 3, None, 4]), 4)", "expect": "3"},
        ],
        "approaches": {
            "Build the graph, BFS by minutes": {
                "idea": [
                    "Infection spreads one edge per minute in every direction, including up to the parent. That is a BFS on the tree treated as an undirected graph.",
                    "Record parents first, so every node knows its three possible neighbours.",
                    "The number of BFS rings after the first is the time until the last node is infected.",
                ],
                "steps": [
                    "Iterative DFS from the root fills <code>parent</code> and finds <code>source</code>, the node whose value is <code>start</code>.",
                    "Start with <code>seen = {source}</code>, <code>ring = [source]</code> and <code>minutes = -1</code>.",
                    "Each round: add 1 to <code>minutes</code>, then gather unseen neighbours (left, right, parent) of the ring into <code>nxt</code>.",
                    "Set <code>ring = nxt</code> and repeat while it is non-empty.",
                    "Return <code>minutes</code>.",
                ],
                "why": [
                    "Round m processes the nodes infected at minute m, so the last non-empty ring is infected at minute <code>minutes</code>.",
                    "Starting at −1 makes the round for the source itself count as minute 0.",
                    "Every node is pushed once and examined once: <strong>O(n)</strong> time.",
                    "The parent map and <code>seen</code> hold all nodes: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (5, 3), 5 → (·, 4), 4 → (9, 2), 3 → (10, 6). Start at 3.",
                        "Minute 0: [3]. Minute 1: 10, 6 and the parent 1.",
                        "Minute 2: from 1, its other child 5. Minute 3: 4.",
                        "Minute 4: 9 and 2. The next ring is empty.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "A left chain 1 → 2 → 3 → 4, starting at the leaf 4.",
                        "Minute 0: [4]. Minute 1: [3] (the parent).",
                        "Minute 2: [2]. Minute 3: [1].",
                        "Nothing is left, so it returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>minutes</code> start at −1?",
                     "The loop body runs once per ring, including the ring holding only the start node, which is minute 0."],
                    ["Can I skip <code>seen</code>?",
                     "No. Parent links make every edge two-way, so without it the infection would bounce back and the loop would never end."],
                    ["What is the answer for a single node?",
                     "The first ring finds no neighbours, so the loop runs once and returns 0."],
                ],
            },
            "One DFS: depth below and distance to start": {
                "idea": [
                    "The answer is the farthest any node is from <code>start</code>. Far nodes are either below <code>start</code>, or reached by going up to an ancestor and down its other side.",
                    "Return a single number from each subtree: its height (≥ 0) if <code>start</code> is not inside, or the negative distance to <code>start</code> if it is.",
                    "At an ancestor, the farthest node on the other side is <code>dist + other</code> away, where <code>other</code> is that side's height.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns 0. Compute <code>left</code> and <code>right</code> first.",
                    "At the start node: <code>best = max(best, left, right)</code> (its own subtree heights), and return −1.",
                    "If neither side contains start, return the height <code>1 + max(left, right)</code>.",
                    "Otherwise <code>dist = -min(left, right)</code> is this node's distance to start and <code>other</code> is the height of the side without start; update <code>best</code> with <code>dist + other</code>.",
                    "Return <code>-(dist + 1)</code> so the parent sees its own distance.",
                ],
                "why": [
                    "Every node's path from start has a highest point: start itself (covered by its subtree heights) or one ancestor (covered by <code>dist + other</code> there).",
                    "Encoding \"contains start\" as a negative number lets one return value carry both meanings, since heights are never negative.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Only recursion: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Heights: 9 and 2 are 1, 4 is 2, 5 is 3, 10 and 6 are 1.",
                        "At 3 (start): best = max(0, 1, 1) = 1. Returns −1.",
                        "At 1: left 3 and right −1. dist = 1, other = 3.",
                        "best = max(1, 1 + 3) = 4. Returns −2.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "At 4 (start): both sides empty, best = 0, returns −1.",
                        "At 3: dist 1, other 0, best = 1, returns −2.",
                        "At 2: dist 2, best = 2, returns −3.",
                        "At 1: dist 3, best = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does start return −1 and not 0?",
                     "0 is a valid height (an empty subtree), so it cannot also mean \"start is here\". −1 means distance 1 from the parent."],
                    ["Why <code>-min(left, right)</code>?",
                     "Only one side can be negative, and the negative one is the side holding start. <code>min</code> picks it and the minus sign turns it back into a distance."],
                    ["Does a value equal to <code>start</code> appear twice?",
                     "No, values are unique in this problem, so exactly one node triggers the start case."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count complete tree nodes
    "count-complete-tree-nodes": {
        "examples": [
            {"call": "count_nodes(build([1, 2, 3, 4, 5, 6]))", "expect": "6"},
            {"call": "count_nodes(build([1, 2, 3, 4]))", "expect": "4"},
        ],
        "approaches": {
            "Plain DFS count": {
                "idea": [
                    "The number of nodes in a tree is 1 for the root plus the counts of the two subtrees.",
                    "This ignores the fact that the tree is complete, so it works for any tree.",
                    "It is the baseline the faster approach is checked against.",
                ],
                "steps": [
                    "If <code>root</code> is <code>None</code>, return 0.",
                    "Count the left subtree recursively.",
                    "Count the right subtree recursively.",
                    "Return 1 plus both counts.",
                ],
                "why": [
                    "Each node is counted exactly once, by the call made on it.",
                    "Every node is visited: <strong>O(n)</strong> time.",
                    "The recursion is as deep as the tree; a complete tree has height log n, so it is <strong>O(h)</strong> = O(log n) space here.",
                    "It wastes the completeness guarantee, which lets most subtrees be counted by a formula.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 → (4, 5), 3 → (6, ·).",
                        "Leaves 4, 5, 6 each count 1.",
                        "2 counts 1 + 1 + 1 = 3. 3 counts 1 + 1 + 0 = 2.",
                        "1 counts 1 + 3 + 2.",
                        "It returns <strong>6</strong>.",
                    ],
                    [
                        "The tree: 1 → (2, 3), 2 → (4, ·).",
                        "4 counts 1; 2 counts 2; 3 counts 1.",
                        "1 counts 1 + 2 + 1.",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Is this accepted?",
                     "Yes, it is correct and O(n). The problem's challenge is to beat O(n) using completeness."],
                    ["Could it overflow the recursion?",
                     "Not for a complete tree, whose height is about log₂ n. On arbitrary skewed trees it could."],
                    ["Why mention it?",
                     "It is the obvious first answer and a reference for testing the clever one."],
                ],
            },
            "Compare left spine heights": {
                "idea": [
                    "In a complete tree, the height of any subtree can be read from its leftmost path alone, in O(log n) steps.",
                    "Compare the heights of the root's left and right subtrees. If they are equal, the last level reaches into the right subtree, so the left subtree is <strong>perfect</strong>. If not, the last level stops in the left subtree, so the right subtree is perfect, one level shorter.",
                    "A perfect subtree of height h has 2<sup>h</sup> − 1 nodes, counted instantly; recurse only into the other side.",
                ],
                "steps": [
                    "If <code>root</code> is <code>None</code>, return 0.",
                    "<code>spine(node)</code> counts nodes along left children: the height of a complete subtree.",
                    "Compute <code>left_h = spine(root.left)</code> and <code>right_h = spine(root.right)</code>.",
                    "If equal: return <code>(1 &lt;&lt; left_h) + count_nodes(root.right)</code>, which is the perfect left subtree plus the root, plus the right side.",
                    "Otherwise return <code>(1 &lt;&lt; right_h) + count_nodes(root.left)</code>.",
                ],
                "why": [
                    "Equal heights mean the bottom level has nodes in the right subtree, and since it fills from the left, the left subtree's bottom level is full.",
                    "Unequal heights mean the bottom level ends inside the left subtree, so the right subtree is perfect at height <code>right_h</code>.",
                    "Each call does two O(log n) spine walks and recurses one level down: <strong>O(log² n)</strong> time.",
                    "Recursion depth is the height: <strong>O(log n)</strong> space.",
                ],
                "dry": [
                    [
                        "Root 1: spine(2) = 2, spine(3) = 2. Equal: 2² = 4 counts the perfect left subtree plus the root; recurse on 3.",
                        "At 3: spine(6) = 1, spine(None) = 0. Unequal: 2⁰ = 1 counts node 3; recurse on 6.",
                        "At 6: both spines 0, equal: 1 + count(None) = 1.",
                        "Total 4 + 1 + 1.",
                        "It returns <strong>6</strong>.",
                    ],
                    [
                        "Root 1: spine(2) = 2, spine(3) = 1. Unequal: 2¹ = 2 counts the perfect right subtree (just 3) plus the root; recurse on 2.",
                        "At 2: spine(4) = 1, spine(None) = 0. Unequal: 1 for node 2; recurse on 4.",
                        "At 4: 1.",
                        "Total 2 + 1 + 1.",
                        "It returns <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>1 &lt;&lt; h</code> count the root too?",
                     "A perfect subtree of height h has 2<sup>h</sup> − 1 nodes; adding the root gives exactly 2<sup>h</sup>."],
                    ["Why is the left spine enough to measure height?",
                     "In a complete tree the bottom level fills from the left, so the leftmost path is always one of the longest."],
                    ["Does this work on a non-complete tree?",
                     "No. The spine can then underestimate the height and the \"perfect\" subtree may have holes, giving a wrong count."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ check completeness
    "check-completeness": {
        "examples": [
            {"call": "is_complete(build([1, 2, 3, 4, 5, None, 7]))", "expect": "False"},
            {"call": "is_complete(build([1, 2, 3, 4, 5, 6]))", "expect": "True"},
        ],
        "approaches": {
            "BFS, allowing None into the queue": {
                "idea": [
                    "A complete tree, read in level order including empty slots, is a run of real nodes followed only by empty slots.",
                    "So BFS while pushing children even when they are <code>None</code>; once the first <code>None</code> has been popped, any real node afterwards breaks completeness.",
                    "One flag, <code>seen_gap</code>, is the whole state.",
                ],
                "steps": [
                    "An empty tree is complete. Otherwise start <code>queue</code> with the root and <code>seen_gap = False</code>.",
                    "Pop a node. If it is <code>None</code>, set <code>seen_gap = True</code> and continue.",
                    "If it is real and <code>seen_gap</code> is already true, return <code>False</code>.",
                    "Otherwise push both children, empty or not.",
                    "If the queue empties without a problem, return <code>True</code>.",
                ],
                "why": [
                    "BFS with empty slots visits positions in the same order as the array numbering of a heap; complete means every used position comes before every unused one.",
                    "A real node after a gap is exactly a used position after an unused one.",
                    "Every node and each of its child slots is pushed once: <strong>O(n)</strong> time.",
                    "The queue holds about one level plus its empty slots: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 → (4, 5), 3 → (·, 7).",
                        "Pop 1, 2, 3, pushing their children; the queue becomes 4, 5, None, 7.",
                        "Pop 4 and 5 (pushing four Nones).",
                        "Pop None: seen_gap = True. Pop 7: a real node after a gap.",
                        "It returns <strong>False</strong>.",
                    ],
                    [
                        "The tree: 1 → (2, 3), 2 → (4, 5), 3 → (6, ·).",
                        "Pop 1, 2, 3; the queue becomes 4, 5, 6, None.",
                        "Pop 4, 5, 6 (pushing Nones).",
                        "Every remaining entry is None, so no real node follows the gap.",
                        "It returns <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why push <code>None</code> children at all?",
                     "The gaps are what is being checked. Skipping them would make [1, None, 2] look like [1, 2]."],
                    ["Can I stop as soon as I see the first <code>None</code>?",
                     "Only if you then check that every remaining entry is <code>None</code>, which is what the flag does as the loop continues."],
                    ["Is a perfect tree complete?",
                     "Yes. Every level is full, so all real nodes come before all gaps."],
                ],
            },
            "Index-based DFS": {
                "idea": [
                    "Number positions like a heap: the root is 1, a node at index i has children at 2i and 2i + 1.",
                    "A tree with <code>count</code> nodes is complete exactly when its positions are 1..count with no holes, that is, when the largest index equals the count.",
                    "One DFS can return both the node count and the largest index of a subtree.",
                ],
                "steps": [
                    "<code>tally(node, index)</code> returns <code>(0, 0)</code> for <code>None</code>.",
                    "Recurse left with <code>2 * index</code> and right with <code>2 * index + 1</code>.",
                    "Return <code>1 + lc + rc</code> and <code>max(index, li, ri)</code>.",
                    "Call <code>tally(root, 1)</code>.",
                    "Return <code>largest == count</code>.",
                ],
                "why": [
                    "The indices of n nodes are n distinct positive numbers, so the largest is at least n, with equality exactly when they are 1..n.",
                    "Positions 1..n with no holes is the definition of complete.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion only: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Indices: 1→1, 2→2, 3→3, 4→4, 5→5, 7→7 (right child of 3).",
                        "tally(2) = (3, 5). tally(3) = (2, 7).",
                        "tally(1) = (6, 7).",
                        "Six nodes but the largest index is 7: position 6 is a hole.",
                        "It returns <strong>False</strong>.",
                    ],
                    [
                        "Node 6 is the left child of 3, index 6.",
                        "tally(2) = (3, 5). tally(3) = (2, 6).",
                        "tally(1) = (6, 6).",
                        "It returns <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Can the indices get huge?",
                     "On a deep skewed tree, yes: depth 100 means numbers near 2¹⁰⁰. Python handles big integers, but other languages would overflow; you can stop as soon as an index exceeds the node count."],
                    ["Why <code>max(index, li, ri)</code> and not just the children?",
                     "A leaf's children report 0, so its own index must be included."],
                    ["Is this better than the BFS?",
                     "Same O(n) time. It uses O(h) instead of O(w) memory, and is a neat example of heap numbering."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum width
    "maximum-width": {
        "examples": [
            {"call": "width_of_binary_tree(build([1, 3, 2, 5, 3, None, 9]))", "expect": "4"},
            {"call": "width_of_binary_tree(build([1, 3, 2, 5, None, None, 9, 6, None, 7]))", "expect": "7"},
        ],
        "approaches": {
            "BFS with positions, re-based per level": {
                "idea": [
                    "Width counts the empty slots between the leftmost and rightmost nodes, so give every node a heap-style position: children of p are at 2p and 2p + 1.",
                    "A level's width is then last position − first position + 1.",
                    "Positions double each level and could grow huge, so each level subtracts its first position before making children's positions.",
                ],
                "steps": [
                    "Start with <code>level = [(root, 0)]</code> and <code>best = 0</code>.",
                    "For each level, take <code>base = level[0][1]</code> and update <code>best</code> with <code>level[-1][1] - base + 1</code>.",
                    "For each <code>(node, pos)</code>, re-base with <code>pos -= base</code>.",
                    "Push the left child at <code>2 * pos</code> and the right child at <code>2 * pos + 1</code>.",
                    "Move to the next level and repeat; return <code>best</code>.",
                ],
                "why": [
                    "Heap positions on one level differ by exactly the number of slots between nodes, so the difference measures the width including gaps.",
                    "Subtracting the same <code>base</code> from every position on a level shifts them all equally, so the differences on the next level are unchanged.",
                    "Each node is handled once: <strong>O(n)</strong> time.",
                    "One level is stored at a time: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (3, 2), 3 → (5, 3), 2 → (·, 9).",
                        "Level [1@0]: width 1. Level [3@0, 2@1]: width 2.",
                        "Level [5@0, 3@1, 9@3]: width 3 − 0 + 1 = 4.",
                        "The next level is empty.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "The tree adds 5 → (6, ·) and 9 → (7, ·) to 1 → (3, 2), 3 → (5, ·), 2 → (·, 9).",
                        "Levels: [1@0] width 1, [3@0, 2@1] width 2, [5@0, 9@3] width 4.",
                        "Level 4: 6 at 2·0 = 0 and 7 at 2·3 = 6. Width 7.",
                        "The gaps between 6 and 7 count even though no nodes are there.",
                        "It returns <strong>7</strong>.",
                    ],
                ],
                "faq": [
                    ["Why re-base at all in Python, where integers do not overflow?",
                     "Without it, positions grow like 2<sup>depth</sup>, and arithmetic on huge integers gets slow on a deep tree. In Java or C++ it is needed to avoid overflow."],
                    ["Why can I use <code>level[0]</code> and <code>level[-1]</code>?",
                     "Children are appended in left-to-right order, so each level list is sorted by position."],
                    ["Does the width include missing nodes beyond the ends?",
                     "No, only the gaps between the leftmost and rightmost real nodes on the level."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ all possible full binary trees
    "all-possible-full-binary-trees": {
        "examples": [
            {"call": "[level_order(t) for t in all_possible_fbt(5)]", "expect": "[[0, 0, 0, None, None, 0, 0], [0, 0, 0, 0, 0]]"},
            {"call": "all_possible_fbt(4)", "expect": "[]"},
        ],
        "approaches": {
            "Memoised recursion over sizes": {
                "idea": [
                    "A full binary tree with n nodes is a root plus a full left subtree and a full right subtree whose sizes add up to n − 1.",
                    "Full trees always have an odd number of nodes, so the left size runs over 1, 3, 5, … and the right side gets the rest.",
                    "Every combination of a left shape and a right shape gives a new tree, and the lists for small sizes are reused, so <code>@cache</code> stores them.",
                ],
                "steps": [
                    "If <code>n</code> is even, return [].",
                    "If <code>n == 1</code>, return a list with one leaf.",
                    "For each odd <code>left</code> from 1 to n − 2, take every <code>l</code> in <code>all_possible_fbt(left)</code> and every <code>r</code> in <code>all_possible_fbt(n - 1 - left)</code>.",
                    "Append <code>TreeNode(0, l, r)</code> to <code>out</code>.",
                    "Return <code>out</code>; <code>@cache</code> remembers it for this <code>n</code>.",
                ],
                "why": [
                    "Every full tree splits uniquely into root, left subtree and right subtree, so each tree is produced exactly once.",
                    "The number of trees is the Catalan number C<sub>(n−1)/2</sub>, which grows like 4<sup>n/2</sup>, so output size dominates; the bound is written as <strong>O(2<sup>n/2</sup>)</strong> per the usual convention.",
                    "Caching means each size is built once; trees share subtrees instead of copying them, so space is about one new root per output tree: <strong>O(2<sup>n/2</sup>)</strong>.",
                ],
                "dry": [
                    [
                        "n = 5: left sizes 1 and 3.",
                        "left = 1: one leaf on the left, one 3-node tree on the right, so the tree has its grandchildren on the right.",
                        "left = 3: the 3-node tree on the left, a leaf on the right.",
                        "fbt(3) was built once (from two copies of the cached leaf) and reused.",
                        "It returns <strong>[[0, 0, 0, None, None, 0, 0], [0, 0, 0, 0, 0]]</strong>.",
                    ],
                    [
                        "n = 4 is even.",
                        "A full tree has 2k + 1 nodes (k internal nodes, k + 1 leaves), so no full tree has 4 nodes.",
                        "It returns <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why are the subtrees shared between trees?",
                     "<code>@cache</code> returns the same node objects every time, so different output trees point at the same subtrees. That is fine to read, but mutating one tree would change others."],
                    ["Why skip even <code>left</code> sizes?",
                     "An even-sized subtree cannot be full, so its list is empty and the inner loops would do nothing anyway."],
                    ["Why the even check first?",
                     "It answers every even n immediately; without it the loops would run and return [] after wasted work."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ flatten to linked list
    "flatten-to-linked-list": {
        "examples": [
            {"setup": "t = build([1, 2, 5, 3, 4, None, 6])\nflatten(t)", "call": "level_order(t)", "expect": "[1, None, 2, None, 3, None, 4, None, 5, None, 6]"},
            {"setup": "t = build([1, 2, None, 3])\nflatten(t)", "call": "level_order(t)", "expect": "[1, None, 2, None, 3]"},
        ],
        "approaches": {
            "Splice the left subtree in, iteratively": {
                "idea": [
                    "In preorder, the right subtree of a node comes right after the last node of its left subtree.",
                    "That last node is the rightmost node of the left subtree. Hang the right subtree there, move the left subtree to the right, and the node now has only a right child.",
                    "Repeat at the next node down the right chain; no stack or recursion is needed.",
                ],
                "steps": [
                    "Start at <code>node = root</code>.",
                    "If <code>node.left</code> exists, walk <code>tail</code> from it along right children to its end.",
                    "Set <code>tail.right = node.right</code>.",
                    "Move the left subtree over: <code>node.right, node.left = node.left, None</code>.",
                    "Step to <code>node = node.right</code> and repeat until it is <code>None</code>.",
                ],
                "why": [
                    "Each splice keeps the preorder sequence intact: node, then its left subtree, then (after the tail) its right subtree.",
                    "After the step, <code>node</code> has no left child, so once the walk passes it, it is final.",
                    "Each tail walk goes down right edges of a left subtree, and every edge is walked by at most one tail search, so the total is <strong>O(n)</strong> time.",
                    "Only a few pointers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 5), 2 → (3, 4), 5 → (·, 6).",
                        "Node 1: tail of the left subtree is 4. 4.right = 5. Now 1 → 2, with 2 → (3, 4), 4 → 5 → 6.",
                        "Node 2: tail of the left subtree is 3. 3.right = 4. Now 2 → 3 → 4.",
                        "Nodes 3, 4, 5, 6 have no left child; the walk just moves along.",
                        "The chain reads <strong>[1, None, 2, None, 3, None, 4, None, 5, None, 6]</strong>.",
                    ],
                    [
                        "The tree is a left chain 1 → 2 → 3.",
                        "Node 1: tail is 2 (no right child). 2.right = None (1 had no right). 1.right = 2.",
                        "Node 2: tail is 3. 2.right = 3.",
                        "Node 3: nothing to do.",
                        "It gives <strong>[1, None, 2, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the rightmost node of the left subtree?",
                     "It is the last node of that subtree in preorder, so whatever follows it in the list must be the node's right subtree."],
                    ["Is the inner <code>while</code> loop quadratic?",
                     "No. A right edge inside a left subtree is walked once; after the splice that subtree sits on the main chain, where the tail search never looks again."],
                    ["Does it return anything?",
                     "No, it changes the tree in place, as the problem asks; the caller keeps the root."],
                ],
            },
            "Reverse preorder with a prev pointer": {
                "idea": [
                    "Building a linked list is easiest from the back: if you visit nodes in <em>reverse</em> preorder, each node just points to the one visited before it.",
                    "Reverse preorder is right subtree, left subtree, node.",
                    "Keep <code>prev</code>, the head of the list built so far, and prepend each node to it.",
                ],
                "steps": [
                    "Set <code>prev = None</code>.",
                    "<code>walk(node)</code> returns for <code>None</code>.",
                    "Walk <code>node.right</code>, then <code>node.left</code>.",
                    "Set <code>node.right = prev</code> and <code>node.left = None</code>, then <code>prev = node</code>.",
                    "Call <code>walk(root)</code>.",
                ],
                "why": [
                    "When a node is processed, everything after it in preorder has already been linked into a list starting at <code>prev</code>, so linking to <code>prev</code> puts it in the right place.",
                    "Both children have been fully walked before the node's pointers are overwritten, so no subtree is lost.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Visit order: 6, 5, 4, 3, 2, 1.",
                        "6.right = None, prev = 6. 5.right = 6, prev = 5.",
                        "4.right = 5, prev = 4. 3.right = 4, prev = 3.",
                        "2.right = 3 (its left cleared), then 1.right = 2.",
                        "The chain reads <strong>[1, None, 2, None, 3, None, 4, None, 5, None, 6]</strong>.",
                    ],
                    [
                        "Visit order: 3, 2, 1.",
                        "3.right = None, prev = 3.",
                        "2.right = 3, left cleared. 1.right = 2, left cleared.",
                        "It gives <strong>[1, None, 2, None, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why visit right before left?",
                     "Prepending reverses the visit order. Visiting right, left, node and then reversing gives node, left, right: preorder."],
                    ["Is it safe to overwrite <code>node.right</code>?",
                     "Yes, by then the right subtree has been walked and already linked behind <code>prev</code>."],
                    ["Why prefer the iterative splice?",
                     "It needs O(1) extra space and no recursion. This version is shorter and the idea carries over to other list-building problems."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ binary tree pruning
    "binary-tree-pruning": {
        "examples": [
            {"call": "level_order(prune_tree(build([1, 0, 1, 0, 0, 0, 1])))", "expect": "[1, None, 1, None, 1]"},
            {"call": "prune_tree(build([0, 0, 0]))", "expect": "None"},
        ],
        "approaches": {
            "Postorder, return the pruned subtree": {
                "idea": [
                    "A subtree should go when it contains no 1. That is decided bottom-up: prune the children first, then look at the node.",
                    "After its children are pruned, a node can be removed exactly when it is a 0 with no children left.",
                    "Each call returns the pruned subtree (or <code>None</code>), and the parent stores it back into its child pointer.",
                ],
                "steps": [
                    "Return <code>None</code> for an empty subtree.",
                    "Set <code>root.left = prune_tree(root.left)</code>.",
                    "Set <code>root.right = prune_tree(root.right)</code>.",
                    "If <code>root.val == 0</code> and both children are now <code>None</code>, return <code>None</code>.",
                    "Otherwise return <code>root</code>.",
                ],
                "why": [
                    "After pruning, any remaining child contains a 1, so a node is kept exactly when it is 1 or has a child subtree with a 1.",
                    "Postorder makes chains of zeros disappear in one pass: the leaf goes first, then its parent becomes a leaf and goes too.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (0, 1), left 0 → (0, 0), right 1 → (0, 1).",
                        "The left 0's children are zero leaves, so both go; it is now a zero leaf and goes too.",
                        "The right 1 loses its 0 child and keeps its 1 child.",
                        "The root is 1, so it stays.",
                        "It returns <strong>[1, None, 1, None, 1]</strong>.",
                    ],
                    [
                        "Both zero leaves are removed.",
                        "The root 0 is now a leaf with value 0, so it is removed too.",
                        "It returns <strong>None</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the children be pruned first?",
                     "Whether a 0 node stays depends on what is left below it. Deciding before the children are pruned would keep zero nodes whose subtrees are all zeros."],
                    ["Why assign the result back to <code>root.left</code>?",
                     "That is how a child is actually removed: the parent's pointer is replaced with <code>None</code>."],
                    ["What if the whole tree is zeros?",
                     "Every node is removed in turn and the root call returns <code>None</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ delete leaves with a given value
    "delete-leaves-with-value": {
        "examples": [
            {"call": "level_order(remove_leaf_nodes(build([1, 2, 3, 2, None, 2, 4]), 2))", "expect": "[1, None, 3, None, 4]"},
            {"call": "level_order(remove_leaf_nodes(build([1, 2, None, 2, None, 2]), 2))", "expect": "[1]"},
        ],
        "approaches": {
            "Postorder, re-check after children": {
                "idea": [
                    "Deleting a leaf can turn its parent into a new leaf, which might also need deleting.",
                    "Process children before the node: by the time the node is checked, any deletions below it are already done.",
                    "So a single postorder pass handles any chain of cascading deletions.",
                ],
                "steps": [
                    "Return <code>None</code> for an empty subtree.",
                    "Replace <code>root.left</code> with the result of the call on it.",
                    "Replace <code>root.right</code> the same way.",
                    "If the node is now a leaf and <code>root.val == target</code>, return <code>None</code>.",
                    "Otherwise return <code>root</code>.",
                ],
                "why": [
                    "The leaf test runs after the children are final, so it sees the tree as it will be after all deeper deletions.",
                    "A node that is not a leaf keeps at least one non-deleted child, so it must stay whatever its value.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 → (2, ·), 3 → (2, 4). Target 2.",
                        "The bottom-left 2 is a leaf: deleted. Its parent 2 becomes a leaf: deleted.",
                        "Under 3: the 2 leaf is deleted, 4 stays.",
                        "3 still has child 4; the root still has 3.",
                        "It returns <strong>[1, None, 3, None, 4]</strong>.",
                    ],
                    [
                        "A left chain 1 → 2 → 2 → 2.",
                        "The deepest 2 goes, then the next 2 is a leaf and goes, then the next.",
                        "The root 1 is a leaf but not the target.",
                        "It returns <strong>[1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not delete leaves in a loop until nothing changes?",
                     "That repeats whole-tree passes, O(n) each, up to h times. Postorder does all the cascading in one pass."],
                    ["Can the root be deleted?",
                     "Yes: if everything collapses, the root becomes a target leaf and the function returns <code>None</code>."],
                    ["How is this different from Binary Tree Pruning?",
                     "It is the same pattern with a different removal test: \"leaf with value target\" instead of \"leaf with value 0\"."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ house robber III
    "house-robber-iii": {
        "examples": [
            {"call": "rob(build([3, 2, 3, None, 3, None, 1]))", "expect": "7"},
            {"call": "rob(build([4, 1, None, 2, None, 3]))", "expect": "7"},
        ],
        "approaches": {
            "Return (with node, without node)": {
                "idea": [
                    "For each subtree, the best haul depends on one thing the parent cares about: was this node robbed or not?",
                    "So return two numbers: the best total if the node is robbed (its children must be skipped), and the best if it is skipped (each child is free to be robbed or not).",
                    "Combining two children's pairs gives the parent's pair in O(1).",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns <code>(0, 0)</code>.",
                    "Get <code>(lw, lo)</code> and <code>(rw, ro)</code> from the children.",
                    "<code>with_node = node.val + lo + ro</code>: rob this node, skip both children.",
                    "<code>without = max(lw, lo) + max(rw, ro)</code>: each child takes its own better option.",
                    "Return the pair; the answer is <code>max(dfs(root))</code>.",
                ],
                "why": [
                    "The only rule is that a parent and child cannot both be robbed, and the pair records exactly the information needed to enforce it.",
                    "Skipping a node leaves its children unconstrained, so taking the max per child is optimal.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 3 → (2, 3), 2 → (·, 3), 3 → (·, 1).",
                        "Leaves: 3 gives (3, 0), 1 gives (1, 0).",
                        "Node 2: (2 + 0, 3) = (2, 3). Right node 3: (3 + 0, 1) = (3, 1).",
                        "Root: with = 3 + 3 + 1 = 7, without = 3 + 3 = 6.",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "A left chain 4 → 1 → 2 → 3.",
                        "3: (3, 0). 2: (2, 3). 1: (1 + 3, 3) = (4, 3).",
                        "4: with = 4 + 3 = 7, without = max(4, 3) = 4.",
                        "Robbing 4 and 3 skips two houses in a row, which the pair allows.",
                        "It returns <strong>7</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just rob alternate levels?",
                     "The best plan can skip two levels in a row. In the chain 4 → 1 → 2 → 3, alternating gives 6 or 4, but 4 + 3 = 7."],
                    ["Why is <code>without</code> not <code>lo + ro</code>?",
                     "Skipping the node does not force its children to be robbed or skipped. Each child picks whichever is better."],
                    ["Why <code>max(dfs(root))</code> at the end?",
                     "The root has no parent, so both of its options are allowed."],
                ],
            },
            "Memoised grandchildren recursion": {
                "idea": [
                    "<code>best(node)</code> is the best haul in a subtree. Either rob the node and add the best of its four grandchildren's subtrees, or skip it and add the best of its two children's subtrees.",
                    "Written plainly, this recomputes the same subtrees many times, since grandchildren are also reached through children.",
                    "A <code>memo</code> dictionary keyed by node makes each subtree's answer computed once.",
                ],
                "steps": [
                    "Return 0 for <code>None</code>; return <code>memo[node]</code> if already known.",
                    "<code>take = node.val</code> plus <code>best(child.left) + best(child.right)</code> for each existing child.",
                    "<code>skip = best(node.left) + best(node.right)</code>.",
                    "Store <code>memo[node] = max(take, skip)</code>.",
                    "Return <code>best(root)</code>.",
                ],
                "why": [
                    "Robbing a node rules out its children only, so its grandchildren's subtrees are free: the recurrence covers both choices.",
                    "With the memo, each node's value is computed once and looked up at most a constant number of times (by its parent and grandparent): <strong>O(n)</strong> time.",
                    "The memo stores every node: <strong>O(n)</strong> space, more than the pair version.",
                ],
                "dry": [
                    [
                        "best(3 root): take starts at 3, adds best(3 leaf under 2) = 3 and best(1) = 1. take = 7.",
                        "skip = best(2) + best(right 3).",
                        "best(2): take 2, skip = 3, so 3 (leaf 3 is read from the memo). best(right 3): take 3, skip 1, so 3.",
                        "skip = 6; memo[root] = max(7, 6).",
                        "It returns <strong>7</strong>.",
                    ],
                    [
                        "best(4): take = 4 + best(2), skip = best(1).",
                        "best(2): take 2, skip best(3) = 3, so 3. take for 4 = 7.",
                        "best(1): take 1 + best(3) = 4, skip best(2) = 3 (memo), so 4.",
                        "memo[4] = max(7, 4).",
                        "It returns <strong>7</strong>.",
                    ],
                ],
                "faq": [
                    ["What is the cost without the memo?",
                     "Each node triggers calls on up to six descendants, and the overlap makes the work exponential in the height."],
                    ["Why key the memo by the node and not its value?",
                     "Different nodes can have the same value but different subtrees, so values would collide."],
                    ["Why prefer the pair version?",
                     "Same O(n) time, but it needs only O(h) memory and no dictionary."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ binary tree cameras
    "binary-tree-cameras": {
        "examples": [
            {"call": "min_camera_cover(build([0, 0, None, 0, 0]))", "expect": "1"},
            {"call": "min_camera_cover(build([0, 0, None, 0, None, 0, None, None, 0]))", "expect": "2"},
        ],
        "approaches": {
            "Greedy postorder with three states": {
                "idea": [
                    "A camera on a leaf covers only the leaf and its parent; a camera on the leaf's parent covers that and more. So never put cameras on leaves: put them on parents of uncovered nodes.",
                    "Work bottom-up. Each node reports one of three states: UNCOVERED (needs its parent to have a camera), CAMERA, or COVERED without a camera.",
                    "Empty children count as COVERED so that leaves report UNCOVERED and push the camera up to their parent.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns <code>COVERED</code>.",
                    "If either child is <code>UNCOVERED</code>, place a camera here: <code>cameras += 1</code>, return <code>CAMERA</code>.",
                    "Else if either child has a camera, return <code>COVERED</code>.",
                    "Else return <code>UNCOVERED</code>, leaving the job to the parent.",
                    "After the call on the root, if it is <code>UNCOVERED</code>, add one last camera there.",
                ],
                "why": [
                    "When a child is uncovered, only this node or the child can cover it, and this node covers a superset of what the child would, so choosing it never hurts.",
                    "Deferring cameras upward as far as possible means each camera covers as many new nodes as it can.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: root → (A, ·), A → (B, C), where B and C are leaves.",
                        "B and C: both children empty (COVERED), so each returns UNCOVERED.",
                        "A: a child is UNCOVERED, so a camera goes on A. cameras = 1.",
                        "Root: its child has a camera, so it is COVERED.",
                        "It returns <strong>1</strong>.",
                    ],
                    [
                        "A chain of 5 nodes: root → A → B → C → D (D is C's right child).",
                        "D: UNCOVERED. C: camera (1). B: COVERED.",
                        "A: its child is only COVERED, so A is UNCOVERED.",
                        "Root: its child is UNCOVERED, so a camera goes on the root (2).",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why are <code>None</code> children COVERED?",
                     "An empty slot needs no camera. Calling it UNCOVERED would force cameras on every leaf; calling it CAMERA would wrongly mark leaves as covered."],
                    ["Why the extra check after the root?",
                     "The root has no parent to defer to. If it is still uncovered, it needs its own camera."],
                    ["How do we know the greedy is optimal?",
                     "It is checked against the exact DP on many random trees in the tests; the exchange argument is that moving a camera from a leaf to its parent never covers fewer nodes."],
                ],
            },
            "Exact DP over three costs": {
                "idea": [
                    "Instead of a greedy rule, compute for each node the minimum cameras in its subtree under three situations, and let the parent choose.",
                    "<code>here</code>: a camera on this node. <code>by_child</code>: no camera here, but a child has one, so the node is covered. <code>waiting</code>: no camera here or on a child; the node is covered only if the parent gets a camera.",
                    "Everything below the node must be covered in all three cases.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns <code>(INF, 0, 0)</code>: an empty slot cannot hold a camera, but it is fine in the other two states.",
                    "<code>here = 1 + min(la, lb, lc) + min(ra, rb, rc)</code>: a camera covers the children, so they may be in any state.",
                    "<code>by_child = min(la + min(ra, rb), ra + min(la, lb))</code>: one child has a camera; the other must cover itself.",
                    "<code>waiting = lb + rb</code>: both children must be covered by their own children.",
                    "The root has no parent, so the answer is <code>min(here, by_child)</code> at the root.",
                ],
                "why": [
                    "The three states cover every way a node can end up covered (or covered by its parent later), so taking minimums over them is exact.",
                    "The INF for empty children stops <code>by_child</code> from pretending a missing child has a camera.",
                    "One visit per node with O(1) work: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Leaves B and C: (1, INF, 0).",
                        "A: here = 1 + 0 + 0 = 1, by_child = 1 + 1 = 2, waiting = INF. (1, 2, INF).",
                        "Root (left child A only): here = 1 + 1 + 0 = 2, by_child = A.here + 0 = 1, waiting = 2.",
                        "min(2, 1) = 1.",
                        "It returns <strong>1</strong>.",
                    ],
                    [
                        "D (leaf): (1, INF, 0). C: (1, 1, INF).",
                        "B: (2, 1, 1). A: (2, 2, 1).",
                        "Root: here = 1 + min(2, 2, 1) = 2, by_child = 2, waiting = 2.",
                        "min(2, 2) = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>waiting</code> excluded at the root?",
                     "A waiting node depends on its parent's camera, and the root has no parent, so that state would leave the root uncovered."],
                    ["Why does <code>here</code> allow children in the waiting state?",
                     "The camera on this node covers both children, so a child that was waiting for its parent is now covered."],
                    ["When would I use this over the greedy?",
                     "When the cost of a camera differs per node, or other constraints are added; the greedy argument breaks then, the DP does not."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ distribute coins
    "distribute-coins": {
        "examples": [
            {"call": "distribute_coins(build([0, 3, 0]))", "expect": "3"},
            {"call": "distribute_coins(build([0, 0, None, 3]))", "expect": "3"},
        ],
        "approaches": {
            "Postorder excess flow": {
                "idea": [
                    "Look at a single edge between a node and its parent. Every coin that crosses it costs one move, and the number that must cross is fixed: the subtree's coins minus its node count.",
                    "Call that number the subtree's <em>excess</em>. Positive means coins flow up, negative means coins flow down; either way <code>abs(excess)</code> moves use that edge.",
                    "The total answer is the sum of <code>abs(excess)</code> over all edges, and a postorder pass computes every excess.",
                ],
                "steps": [
                    "<code>excess(None)</code> returns 0.",
                    "Compute <code>left</code> and <code>right</code>, the excess of each child subtree.",
                    "Add <code>abs(left) + abs(right)</code> to <code>moves</code>: the traffic on the two child edges.",
                    "Return <code>node.val + left + right - 1</code>: this subtree's coins minus its nodes.",
                    "Call <code>excess(root)</code> and return <code>moves</code>.",
                ],
                "why": [
                    "Each subtree must end with exactly one coin per node, so exactly <code>abs(excess)</code> coins must cross its top edge, and no plan can do with fewer.",
                    "Moving coins edge by edge along these flows achieves that bound, so the sum is the minimum.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 0 → (3, 0).",
                        "Left leaf 3: excess 3 − 1 = 2. Right leaf 0: excess −1.",
                        "Root: moves += 2 + 1 = 3. Its excess is 0 + 2 − 1 − 1 = 0, as it must be.",
                        "Two coins go up the left edge and one goes down the right edge.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "A left chain 0 → 0 → 3.",
                        "Leaf 3: excess 2.",
                        "Middle 0: moves += 2. Excess 0 + 2 − 1 = 1.",
                        "Root: moves += 1, total 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can excess be negative?",
                     "A subtree with fewer coins than nodes needs coins sent down to it. The absolute value counts those moves too."],
                    ["Why is the root's own excess never added?",
                     "The root has no parent edge. The total number of coins equals the number of nodes, so its excess is 0 anyway."],
                    ["Does the order of the moves matter?",
                     "No. The count of coins crossing each edge is forced, so any valid order gives the same total."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ count good nodes
    "count-good-nodes": {
        "examples": [
            {"call": "good_nodes(build([3, 1, 4, 3, None, 1, 5]))", "expect": "4"},
            {"call": "good_nodes(build([3, 3, None, 4, 2]))", "expect": "3"},
        ],
        "approaches": {
            "Carry the path maximum down": {
                "idea": [
                    "A node is good when nothing on the path from the root to it is larger than it.",
                    "So the only fact a node needs about its path is the path's maximum. Pass it down as a parameter.",
                    "Each node compares itself with that maximum, then passes on the larger of the two.",
                ],
                "steps": [
                    "<code>dfs(node, best)</code> returns 0 for <code>None</code>.",
                    "<code>good = node.val &gt;= best</code>.",
                    "Update <code>best = max(best, node.val)</code>.",
                    "Return <code>good</code> plus the counts from both children, called with the new <code>best</code>.",
                    "Start with <code>dfs(root, root.val)</code>.",
                ],
                "why": [
                    "<code>best</code> always equals the maximum of the path from the root to the node's parent, so the comparison is exactly the definition.",
                    "Python adds a bool as 0 or 1, so <code>good + ...</code> counts it directly.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 3 → (1, 4), 1 → (3, ·), 4 → (1, 5).",
                        "Root 3 vs 3: good. Left 1 vs 3: not good.",
                        "Its child 3 vs 3: good (equal is allowed).",
                        "4 vs 3: good, best 4. Its children 1: no, 5: good.",
                        "It returns <strong>4</strong>.",
                    ],
                    [
                        "The tree: 3 → (3, ·), 3 → (4, 2).",
                        "Root 3: good. Child 3 vs 3: good.",
                        "4 vs 3: good. 2 vs 3: not good.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt;=</code> and not <code>&gt;</code>?",
                     "A node equal to the path maximum has no larger node above it, so it counts as good."],
                    ["Why start with <code>root.val</code> rather than <code>-inf</code>?",
                     "Either works; with <code>root.val</code> the root compares equal and counts as good. It does assume the root exists."],
                    ["Does updating <code>best</code> affect the sibling branch?",
                     "No. <code>best</code> is a parameter, so each call has its own copy and siblings see their parent's value."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ nodes equal to average of subtree
    "nodes-equal-average": {
        "examples": [
            {"call": "average_of_subtree(build([4, 8, 5, 0, 1, None, 6]))", "expect": "5"},
            {"call": "average_of_subtree(build([1, 2, 3]))", "expect": "2"},
        ],
        "approaches": {
            "Return (sum, size)": {
                "idea": [
                    "A subtree's average needs its sum and its size, and both combine easily: the sums and sizes of the children plus the node itself.",
                    "Return the pair from every call, so each node computes its own average in O(1).",
                    "The problem rounds the average down, which is integer division <code>//</code>.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns <code>(0, 0)</code>.",
                    "Get <code>(ls, ln)</code> and <code>(rs, rn)</code> from the children.",
                    "<code>total = ls + rs + node.val</code> and <code>size = ln + rn + 1</code>.",
                    "Add 1 to <code>count</code> if <code>total // size == node.val</code>.",
                    "Return <code>(total, size)</code>; after <code>dfs(root)</code> return <code>count</code>.",
                ],
                "why": [
                    "Each node's pair is built from its children's pairs, which are already complete in postorder.",
                    "Recomputing each subtree's sum from scratch would cost O(n²) on a chain; passing the pair up avoids that.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 4 → (8, 5), 8 → (0, 1), 5 → (·, 6).",
                        "Leaves 0, 1, 6 match their own average: count = 3.",
                        "8: sum 9, size 3, 9 // 3 = 3 ≠ 8.",
                        "5: sum 11, size 2, 5 = 5, count = 4. Root 4: sum 24, size 6, 4 = 4, count = 5.",
                        "It returns <strong>5</strong>.",
                    ],
                    [
                        "Leaves 2 and 3 match: count = 2.",
                        "Root 1: sum 6, size 3, average 2 ≠ 1.",
                        "It returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>//</code> and not <code>/</code>?",
                     "The problem defines the average as the sum divided by the count, rounded down. <code>/</code> would give 5.5 for sum 11 and size 2, which never equals 5."],
                    ["Is a leaf always counted?",
                     "Yes, its sum is its value and its size is 1."],
                    ["What does <code>count += total // size == node.val</code> add?",
                     "The comparison gives <code>True</code> or <code>False</code>, which Python adds as 1 or 0."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ most frequent subtree sum
    "most-frequent-subtree-sum": {
        "examples": [
            {"call": "sorted(find_frequent_tree_sum(build([5, 2, -3])))", "expect": "[-3, 2, 4]"},
            {"call": "find_frequent_tree_sum(build([5, 2, -5]))", "expect": "[2]"},
        ],
        "approaches": {
            "Postorder sums into a Counter": {
                "idea": [
                    "Every node defines one subtree sum: its value plus its children's subtree sums.",
                    "Compute them bottom-up and tally each one in a <code>Counter</code>.",
                    "At the end, return every sum whose tally equals the highest tally; ties all count.",
                ],
                "steps": [
                    "<code>total(None)</code> returns 0.",
                    "<code>s = node.val + total(node.left) + total(node.right)</code>.",
                    "Add 1 to <code>counts[s]</code> and return <code>s</code>.",
                    "After <code>total(root)</code>, return [] if nothing was counted (empty tree).",
                    "Find <code>top = max(counts.values())</code> and return all sums with that count.",
                ],
                "why": [
                    "Each node's subtree sum is computed once from its children's, so every sum in the tree is tallied exactly once.",
                    "One pass over the nodes plus one pass over the distinct sums: <strong>O(n)</strong> time.",
                    "The Counter can hold n distinct sums: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Leaves: 2 and −3, each counted once.",
                        "Root: 5 + 2 − 3 = 4, counted once.",
                        "All three sums appear once, so top = 1 and all are returned.",
                        "Sorted: <strong>[-3, 2, 4]</strong>.",
                    ],
                    [
                        "Leaves: 2 and −5.",
                        "Root: 5 + 2 − 5 = 2, so counts[2] = 2.",
                        "top = 2 and only sum 2 reaches it.",
                        "It returns <strong>[2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the empty check before <code>max</code>?",
                     "<code>max</code> of an empty sequence raises a ValueError, and an empty tree gives an empty Counter."],
                    ["In what order are tied sums returned?",
                     "In the order they were first counted (dictionary insertion order). The problem accepts any order, so the example sorts them."],
                    ["Could I use <code>counts.most_common(1)</code>?",
                     "It gives only one of the tied sums, so you would still need to collect all sums with that count."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find duplicate subtrees
    "find-duplicate-subtrees": {
        "examples": [
            {"call": "sorted(level_order(x) for x in find_duplicate_subtrees(build([1, 2, 3, 4, None, 2, 4, None, None, 4])))", "expect": "[[2, 4], [4]]"},
            {"call": "[level_order(x) for x in find_duplicate_subtrees(build([2, 1, 1]))]", "expect": "[[1]]"},
        ],
        "approaches": {
            "Intern each subtree as an integer id": {
                "idea": [
                    "Two subtrees are identical exactly when their roots have equal values and their left and right subtrees are identical.",
                    "So give each distinct subtree shape a small integer id: the id of a node is looked up from the triple (left id, value, right id).",
                    "Equal ids mean identical subtrees, and comparing a triple costs O(1) no matter how big the subtree is.",
                ],
                "steps": [
                    "Keep <code>ids</code> (triple → id), a <code>Counter</code> <code>seen</code>, and the output list <code>out</code>.",
                    "<code>key(None)</code> returns 0.",
                    "Build <code>triple = (key(node.left), node.val, key(node.right))</code> and get its id with <code>ids.setdefault(triple, len(ids) + 1)</code>.",
                    "Add 1 to <code>seen[uid]</code>; when it reaches exactly 2, append <code>node</code> to <code>out</code>.",
                    "Return <code>uid</code>; after <code>key(root)</code>, return <code>out</code>.",
                ],
                "why": [
                    "By induction, equal ids for the children plus an equal value means equal subtrees, so the id is a perfect fingerprint.",
                    "Appending only at count 2 reports each duplicated shape once, however many copies there are.",
                    "Each node does O(1) hashing of a three-item tuple: <strong>O(n)</strong> time.",
                    "The id table and counter have at most n entries: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 → (4, ·), 3 → (2, 4), with the inner 2 → (4, ·).",
                        "First leaf 4: (0, 4, 0) gets id 1. Left 2: (1, 2, 0) gets id 2.",
                        "Under 3: leaf 4 is id 1 again (count 2, reported); 2 is id 2 again (count 2, reported).",
                        "The last leaf 4 is id 1 a third time: not reported again. 3 gets id 3, the root id 4.",
                        "Sorted: <strong>[[2, 4], [4]]</strong>.",
                    ],
                    [
                        "Left leaf 1: (0, 1, 0) gets id 1, count 1.",
                        "Right leaf 1: same triple, id 1, count 2, reported.",
                        "Root 2: (1, 2, 1) gets id 2.",
                        "It returns <strong>[[1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>== 2</code> and not <code>&gt;= 2</code>?",
                     "Each duplicated shape should appear once in the answer. With <code>&gt;= 2</code>, a shape seen three times would be reported twice."],
                    ["Why is the empty subtree id 0?",
                     "It needs an id that no real subtree gets; real ids start at 1 because of <code>len(ids) + 1</code>."],
                    ["Why not just compare values?",
                     "Equal values in different shapes are different subtrees. The triple captures the shape as well as the values."],
                ],
            },
            "Serialize every subtree to a string": {
                "idea": [
                    "Turn each subtree into a string that fully describes it, such as <code>(2,(4,#,#),#)</code>, and count the strings.",
                    "Identical strings mean identical subtrees, because the format includes the empty-child markers.",
                    "Easy to write, but every string contains its whole subtree, so long strings are built and hashed again and again.",
                ],
                "steps": [
                    "<code>key(None)</code> returns <code>#</code>.",
                    "Build <code>s</code> from the value and the two child strings.",
                    "Add 1 to <code>seen[s]</code>; when it becomes 2, append the node to <code>out</code>.",
                    "Return <code>s</code>.",
                    "After <code>key(root)</code>, return <code>out</code>.",
                ],
                "why": [
                    "The bracketed format with <code>#</code> markers is a full preorder serialization, so different shapes give different strings.",
                    "A node's string has length proportional to its subtree size; on a chain the sizes add up to about n²/2, giving <strong>O(n²)</strong> time.",
                    "All those strings are stored as Counter keys: <strong>O(n²)</strong> space.",
                ],
                "dry": [
                    [
                        "Leaf 4 becomes \"(4,#,#)\". Left 2 becomes \"(2,(4,#,#),#)\".",
                        "Under 3 the same two strings appear again, each reaching count 2: both reported.",
                        "The third \"(4,#,#)\" reaches count 3, not reported.",
                        "3 and the root have unique strings.",
                        "Sorted: <strong>[[2, 4], [4]]</strong>.",
                    ],
                    [
                        "Both leaves are \"(1,#,#)\"; the second one reaches count 2.",
                        "The root \"(2,(1,#,#),(1,#,#))\" is unique.",
                        "It returns <strong>[[1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why are the <code>#</code> markers needed?",
                     "Without them, a node 2 with left child 4 and one with right child 4 would give the same string."],
                    ["Why the commas and brackets?",
                     "They keep values apart: without separators, 1 followed by 23 and 12 followed by 3 would look the same."],
                    ["When is this good enough?",
                     "For small trees or a first version. On large or deep trees the integer-id approach avoids the quadratic string building."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ kth smallest in a BST
    "kth-smallest-bst": {
        "examples": [
            {"call": "kth_smallest(build([5, 3, 6, 2, 4, None, None, 1]), 3)", "expect": "3"},
            {"call": "kth_smallest(build([3, 1, 4, None, 2]), 1)", "expect": "1"},
        ],
        "approaches": {
            "Iterative inorder, stop at k": {
                "idea": [
                    "An inorder traversal of a BST lists its values in sorted order, so the kth value visited is the answer.",
                    "An explicit stack lets the traversal stop the moment the kth node is reached, without visiting the rest.",
                    "Count down from k: when it hits 0, the current node is the one.",
                ],
                "steps": [
                    "Start with an empty <code>stack</code> and <code>node = root</code>.",
                    "Push <code>node</code> and move left until <code>node</code> is <code>None</code>.",
                    "Pop the next node in sorted order and subtract 1 from <code>k</code>.",
                    "If <code>k == 0</code>, return <code>node.val</code>.",
                    "Otherwise move to <code>node.right</code> and repeat.",
                ],
                "why": [
                    "The stack holds the path of nodes whose left side is done but which are not yet visited, so pops come out in increasing order.",
                    "Reaching the smallest value costs h pushes, and each further step is amortised O(1): <strong>O(h + k)</strong> time.",
                    "The stack holds at most one root-to-leaf path: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The BST: 5 → (3, 6), 3 → (2, 4), 2 → (1, ·). k = 3.",
                        "Push 5, 3, 2, 1. Pop 1: k = 2.",
                        "1 has no right child. Pop 2: k = 1.",
                        "2 has no right child. Pop 3: k = 0.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "The BST: 3 → (1, 4), 1 → (·, 2). k = 1.",
                        "Push 3, 1. 1 has no left child.",
                        "Pop 1: k = 0.",
                        "It returns <strong>1</strong> without touching 2 or 4.",
                    ],
                ],
                "faq": [
                    ["Why <code>while True</code> with no exit condition?",
                     "The problem guarantees 1 ≤ k ≤ n, so the kth node is always reached and the function returns inside the loop."],
                    ["Why not collect the whole inorder list?",
                     "That is O(n) time and space. Stopping at k costs O(h + k) and only a stack."],
                    ["What if the tree is changed often and queried often?",
                     "Store each node's subtree size. Then the kth smallest is found in O(h) by comparing k with the left subtree's size."],
                ],
            },
            "Morris inorder, stopped at k": {
                "idea": [
                    "Morris traversal does an inorder walk with O(1) extra memory by temporarily threading each node's inorder predecessor back to it.",
                    "The thread replaces the stack: after finishing a left subtree, the walk follows the thread back up to the node.",
                    "Counting down k as nodes are visited finds the answer; the walk then continues to the end so that every thread is removed and the tree is left intact.",
                ],
                "steps": [
                    "If <code>node.left</code> is <code>None</code>, visit the node (subtract 1 from k, record <code>answer</code> at 0) and go right.",
                    "Otherwise find <code>pred</code>, the rightmost node of the left subtree, stopping if its right pointer already leads back to <code>node</code>.",
                    "If <code>pred.right</code> is <code>None</code>, create the thread <code>pred.right = node</code> and go left.",
                    "Else the left side is done: remove the thread, visit the node, and go right.",
                    "When <code>node</code> becomes <code>None</code>, return <code>answer</code>.",
                ],
                "why": [
                    "A node is visited either when it has no left child or when its thread is found the second time, which is exactly after its left subtree: inorder.",
                    "Each thread is created once and removed once, and each predecessor search walks edges a constant number of times overall: <strong>O(n)</strong> time.",
                    "Only <code>node</code>, <code>pred</code>, <code>k</code> and <code>answer</code> are stored: <strong>O(1)</strong> space.",
                    "Returning early would leave threads in the tree, so the loop runs to the end; that is why the time is O(n), not O(h + k).",
                ],
                "dry": [
                    [
                        "At 5: thread 4 → 5, go left. At 3: thread 2 → 3. At 2: thread 1 → 2.",
                        "1 has no left: visit, k = 2. Follow the thread to 2.",
                        "At 2: thread found, remove it, visit, k = 1. Go to 3 via its thread: remove it, visit, k = 0, answer = 3.",
                        "The walk continues through 4 and 5 (removing 4 → 5) and 6, so the tree is restored.",
                        "It returns <strong>3</strong>.",
                    ],
                    [
                        "At 3: the predecessor is 2 (rightmost in 1's subtree). Thread 2 → 3, go left.",
                        "1 has no left: visit, k = 0, answer = 1.",
                        "The walk visits 2, follows the thread to 3, removes it, then visits 3 and 4.",
                        "It returns <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not return as soon as k hits 0?",
                     "Some threads may still be in place, which would leave the tree modified. The tests check that the tree is unchanged afterwards."],
                    ["Why does the predecessor search stop at <code>pred.right is node</code>?",
                     "That pointer is the thread made on the way down. Without the check the search would loop around through the node forever."],
                    ["When is Morris worth it?",
                     "Only when O(h) extra memory is truly not allowed. The stack version is simpler and stops early."],
                ],
            },
        },
    },
}
