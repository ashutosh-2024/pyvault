"""Write-ups for Trees, part B: aggregates, root-to-leaf paths, arbitrary paths."""

_PS = "build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])"

EXPLAIN = {
    # ------------------------------------------------------------------ balanced
    "balanced-binary-tree": {
        "example": {"call": "is_balanced(build([1, 2, 2, 3, 3, None, None, 4, 4]))", "expect": "False"},
        "approaches": {
            "Top-down, recomputing heights": {
                "idea": [
                    "A tree is balanced when, at <em>every</em> node, the left and right heights differ by at most 1.",
                    "The direct approach measures both heights at the root and compares them, then recurses into each child and measures again.",
                ],
                "steps": [
                    "If <code>|height(left) - height(right)| &gt; 1</code>, return False.",
                    "Otherwise require both subtrees to be balanced.",
                ],
                "why": [
                    "<code>height()</code> re-walks each subtree for every ancestor. On a balanced tree that is O(n log n) in total.",
                    "Skewed trees fail at the root almost immediately, so they are cheap.",
                ],
                "dry": [
                    "The tree: 1 → (2, 2); the left 2 → (3, 3); the left 3 → (4, 4). The right 2 is a leaf.",
                    "At the root, height(left) = 3 and height(right) = 1. The difference is 2.",
                    "The result is <strong>False</strong>.",
                ],
            },
            "Bottom-up with a sentinel": {
                "idea": [
                    "Compute each height once, on the way back up, and let the same return value report failure.",
                    "<code>check(node)</code> returns the height, or <strong>-1</strong> if something below is already unbalanced. A -1 is passed straight up without any more work.",
                ],
                "steps": [
                    "Get <code>left</code>; if it is -1, return -1. Get <code>right</code>; if it is -1, return -1.",
                    "If <code>|left - right| &gt; 1</code>, return -1; otherwise return <code>1 + max(left, right)</code>.",
                ],
                "why": [
                    "Each node's height is computed once and reused by its parent: O(n) time, O(h) stack.",
                ],
                "dry": [
                    "The 4s return 1, so the left 3 returns 2. The right 3 returns 1.",
                    "The left 2 has |2 - 1| = 1, which is fine, so it returns 3. The right 2 returns 1.",
                    "At the root, |3 - 1| = 2, so it returns -1. The result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ diameter
    "diameter-of-binary-tree": {
        "example": {"call": "diameter(build([1, 2, 3, 4, 5]))", "expect": "3"},
        "approaches": {
            "Postorder height with a nonlocal best": {
                "idea": [
                    "Every path has one highest node, where it bends. Through that node, its length is left height + right height (in edges).",
                    "So compute heights bottom-up and, at each node, try the path that bends there.",
                    "The parent needs the <em>height</em>, not the diameter, so return the height and record the diameter in a shared variable.",
                ],
                "steps": [
                    "<code>height(None) = 0</code>; at a node: <code>best = max(best, left + right)</code>; return <code>1 + max(left, right)</code>.",
                ],
                "why": [
                    "One visit per node: O(n) time and O(h) stack.",
                    "With a leaf's height counted as 1, <code>left + right</code> is already in edges.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), 2 → (4, 5).",
                    "4 and 5 each have height 1. At 2: bend = 1 + 1 = 2; height 2. At 3: height 1.",
                    "At 1: bend = 2 + 1 = 3. The result is <strong>3</strong> (the path 4 – 2 – 1 – 3).",
                ],
            },
            "Returning a (height, diameter) pair": {
                "idea": [
                    "This is the same algorithm with no shared variable. Each call returns its height <em>and</em> the best diameter found anywhere below it.",
                ],
                "steps": [
                    "<code>here = lh + rh</code>; return <code>(1 + max(lh, rh), max(ld, rd, here))</code>.",
                ],
                "why": [
                    "It has the same O(n) and O(h) bounds, and the function has no side effects.",
                ],
                "dry": [
                    "solve(4) = solve(5) = (1, 0). solve(2) = (2, 2). solve(3) = (1, 0).",
                    "solve(1) = (3, max(2, 0, 3)) = (3, 3).",
                    "The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ tilt
    "binary-tree-tilt": {
        "example": {"call": "find_tilt(build([4, 2, 9, 3, 5, None, 7]))", "expect": "15"},
        "approaches": {
            "Postorder sum with an accumulator": {
                "idea": [
                    "A node's tilt is |left subtree sum - right subtree sum|.",
                    "Return the <em>subtree sum</em> to the parent, and add the tilt to a running total along the way.",
                ],
                "steps": [
                    "<code>total += abs(left - right)</code>; return <code>val + left + right</code>.",
                ],
                "why": [
                    "Each subtree sum is computed once: O(n). Recomputing sums at every node would be O(n²) on a chain.",
                ],
                "dry": [
                    "The tree: 4 → (2, 9), 2 → (3, 5), 9 → (None, 7).",
                    "At 2: |3 - 5| = 2; its sum is 10. At 9: |0 - 7| = 7; its sum is 16. At 4: |10 - 16| = 6.",
                    "The total is 2 + 7 + 6 = <strong>15</strong>.",
                ],
            },
            "Returning a (sum, tilt) pair": {
                "idea": [
                    "This is the pure version: return the subtree sum and the tilt total accumulated below.",
                ],
                "steps": [
                    "Return <code>(val + ls + rs, lt + rt + abs(ls - rs))</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "solve(2) = (10, 2); solve(9) = (16, 7).",
                    "solve(4) = (30, 2 + 7 + 6) = (30, 15).",
                    "The result is <strong>15</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max ancestor diff
    "max-diff-node-ancestor": {
        "example": {"call": "max_ancestor_diff(build([8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13]))", "expect": "7"},
        "approaches": {
            "Top-down: carry the path's min and max": {
                "idea": [
                    "For any node, the best ancestor to pair it with is the smallest or the largest value above it.",
                    "So pass the path's <code>(lo, hi)</code> downwards. When a path ends, <code>hi - lo</code> is the best difference on that path.",
                ],
                "steps": [
                    "Update lo and hi with this node's value; return the max over both children.",
                    "At None, return <code>hi - lo</code>.",
                ],
                "why": [
                    "Every ancestor/descendant pair lies on some root-to-leaf path: O(n) time.",
                ],
                "dry": [
                    "The tree: 8 → (3, 10), 3 → (1, 6), 6 → (4, 7), 10 → (None, 14), 14 → (13).",
                    "Path 8 – 3 – 1: lo 1, hi 8, gives 7. Path 8 – 3 – 6 – 4 gives 5. Path 8 – 10 – 14 – 13 gives 6.",
                    "The result is <strong>7</strong>.",
                ],
            },
            "Bottom-up: return the subtree's min and max": {
                "idea": [
                    "Each call returns the smallest and largest values in its subtree; the node compares itself with both.",
                ],
                "steps": [
                    "For each child: update <code>best</code> with <code>|val - clo|</code> and <code>|val - chi|</code>; merge the min and max.",
                ],
                "why": [
                    "It is O(n): return one thing, record another.",
                ],
                "dry": [
                    "span(6) = (4, 7), with best 2. span(3) = (1, 7), with best |3 - 7| = 4.",
                    "span(10) = (10, 14), with best 4. At 8: |8 - 1| = 7.",
                    "The result is <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest univalue path
    "longest-univalue-path": {
        "example": {"call": "longest_univalue_path(build([1, 4, 5, 4, 4, None, 5]))", "expect": "2"},
        "approaches": {
            "Return the longest arm, record the bend": {
                "idea": [
                    "This is Diameter with a condition: a child's arm counts only if the child has the <em>same value</em>.",
                    "The arm returned upwards is the longer one-sided same-value path; the bend (left + right) is recorded globally.",
                ],
                "steps": [
                    "<code>left = arm(left) + 1</code> if the left child matches, else 0; the same for the right.",
                    "<code>best = max(best, left + right)</code>; return <code>max(left, right)</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "The tree: 1 → (4, 5), 4 → (4, 4), 5 → (None, 5).",
                    "At the 4 with two 4-children: left = 1 and right = 1, so the bend is 2. At 5: right = 1.",
                    "The root 1 matches neither child. The result is <strong>2</strong>.",
                ],
            },
            "Pure version: return (arm, best)": {
                "idea": [
                    "Return both the arm and the best path found in the subtree, with no shared variable.",
                ],
                "steps": [
                    "Return <code>(max(la, ra), max(lb, rb, la + ra))</code>.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack.",
                ],
                "dry": [
                    "solve(inner 4) = (1, 2); solve(5) = (1, 1).",
                    "The root returns (0, 2).",
                    "The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path sum
    "path-sum": {
        "example": {"call": f"has_path_sum({_PS}, 22)", "expect": "True"},
        "approaches": {
            "Recursive, subtracting as you go": {
                "idea": [
                    "Subtract each node's value from the target and pass the remainder down.",
                    "Only a <strong>leaf</strong> ends a path: it succeeds when the remainder is exactly 0.",
                ],
                "steps": [
                    "None returns False; at a leaf, compare with 0; otherwise OR the two children.",
                ],
                "why": [
                    "It is O(n) worst case and stops at the first match. O(h) stack.",
                ],
                "dry": [
                    "The tree: 5 → (4, 8), 4 → (11), 11 → (7, 2), 8 → (13, 4), 4 → (None, 1).",
                    "22 - 5 = 17, - 4 = 13, - 11 = 2. Leaf 7 gives -5 ✗; leaf 2 gives 0 ✓.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Iterative DFS with running sums": {
                "idea": [
                    "Push <code>(node, sum so far)</code> pairs: whatever the recursive call would receive goes on the stack with the node.",
                ],
                "steps": [
                    "Pop, add the value, check whether it is a leaf with the right total, push the children.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack, with no recursion limit.",
                ],
                "dry": [
                    "The right side is popped first: 5 → 8 → 4 → 1 sums to 18 ✗; 5 → 8 → 13 sums to 26 ✗.",
                    "Then 5 → 4 → 11 → 2 sums to 22 ✓.",
                    "The result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path sum II
    "path-sum-ii": {
        "example": {"call": "path_sum(build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]), 22)",
                    "expect": "[[5, 4, 11, 2], [5, 8, 4, 5]]"},
        "approaches": {
            "Backtracking with one shared path": {
                "idea": [
                    "Keep one list, <code>path</code>, holding the route from the root to the current node.",
                    "Push the node on the way down and pop it on the way up. At a matching leaf, save a <em>copy</em>.",
                ],
                "steps": [
                    "Choose (append), check the leaf, explore both children, un-choose (pop).",
                ],
                "why": [
                    "The traversal is O(n), and each match costs an O(h) copy. The copy is needed because the live list keeps changing.",
                ],
                "dry": [
                    "path [5, 4, 11, 7] sums to 27 ✗. Pop 7, push 2: [5, 4, 11, 2] sums to 22 ✓, so save a copy.",
                    "Later [5, 8, 4, 5] sums to 22 ✓; [5, 8, 4, 1] gives 18 ✗; [5, 8, 13] gives 26 ✗.",
                    "The result is <strong>[[5, 4, 11, 2], [5, 8, 4, 5]]</strong>.",
                ],
            },
            "New list per call": {
                "idea": [
                    "Pass <code>path + [val]</code> to each child, so every call owns its own list and nothing needs undoing.",
                ],
                "steps": [
                    "At a matching leaf, append that list directly.",
                ],
                "why": [
                    "Every node copies its path: O(n·h) time even with no matches.",
                ],
                "dry": [
                    "Same two matches: [5, 4, 11, 2] and [5, 8, 4, 5].",
                    "The result is <strong>[[5, 4, 11, 2], [5, 8, 4, 5]]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ binary tree paths
    "binary-tree-paths": {
        "example": {"call": "binary_tree_paths(build([1, 2, 3, None, 5]))", "expect": "['1->2->5', '1->3']"},
        "approaches": {
            "Backtracking list, join at the leaf": {
                "idea": [
                    "Keep the path as a list of strings, and only <code>\"-&gt;\".join</code> it when you reach a leaf.",
                ],
                "steps": [
                    "Append <code>str(val)</code>; at a leaf, join and save; recurse; pop.",
                ],
                "why": [
                    "Joining costs O(h) per leaf, which is the size of the output.",
                ],
                "dry": [
                    "The tree: 1 → (2, 3), and 2 has a right child 5.",
                    "path [1, 2, 5] at leaf 5 → \"1-&gt;2-&gt;5\". Pop back to [1], push 3 → \"1-&gt;3\".",
                    "The result is <strong>['1-&gt;2-&gt;5', '1-&gt;3']</strong>.",
                ],
            },
            "Iterative, carrying the string": {
                "idea": [
                    "Each stack entry carries the string built so far. Push the right child first so the left path comes out first.",
                ],
                "steps": [
                    "Pop; at a leaf, save the text; push the children with <code>text + \"-&gt;\" + val</code>.",
                ],
                "why": [
                    "It is simple and has no recursion, but each pending entry holds its own string.",
                ],
                "dry": [
                    "Pop (1, \"1\") → push (3, \"1-&gt;3\"), (2, \"1-&gt;2\").",
                    "Pop 2 → push (5, \"1-&gt;2-&gt;5\"). Pop 5: leaf, save it. Pop 3: leaf, save it.",
                    "The result is <strong>['1-&gt;2-&gt;5', '1-&gt;3']</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sum root to leaf numbers
    "sum-root-to-leaf-numbers": {
        "example": {"call": "sum_numbers(build([4, 9, 0, 5, 1]))", "expect": "1026"},
        "approaches": {
            "Carry the number down": {
                "idea": [
                    "Going down a level appends a digit: <code>current * 10 + val</code>.",
                    "A leaf returns its complete number; an inner node returns the sum of its children's results.",
                ],
                "steps": [
                    "<code>dfs(node, current)</code>, starting at 0.",
                ],
                "why": [
                    "There are no path lists or strings: O(n) time and O(h) stack.",
                ],
                "dry": [
                    "The tree: 4 → (9, 0), 9 → (5, 1).",
                    "4 → 49 → 495 (leaf) and 491 (leaf). 4 → 40 (leaf).",
                    "495 + 491 + 40 = <strong>1026</strong>.",
                ],
            },
            "BFS with (node, value) pairs": {
                "idea": [
                    "The same state, carried level by level in a queue.",
                ],
                "steps": [
                    "Pop, extend the value, add it at a leaf, enqueue the children.",
                ],
                "why": [
                    "It is O(n) time and O(w) space.",
                ],
                "dry": [
                    "Level 2: 49 and 40 (a leaf: +40). Level 3: 495 and 491 (leaves).",
                    "The total is <strong>1026</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ binary root to leaf
    "sum-root-to-leaf-binary": {
        "example": {"call": "sum_root_to_leaf(build([1, 0, 1, 0, 1, 0, 1]))", "expect": "22"},
        "approaches": {
            "Carry the number, shift left": {
                "idea": [
                    "Appending a binary digit is <code>current * 2 + bit</code>, which is <code>(current &lt;&lt; 1) | bit</code>.",
                    "Otherwise it is identical to Sum Root to Leaf Numbers.",
                ],
                "steps": [
                    "Shift and OR on the way down; leaves return their number.",
                ],
                "why": [
                    "It is O(n) time and O(h) stack. Any base b works the same way: <code>current * b + digit</code>.",
                ],
                "dry": [
                    "The four root-to-leaf paths are 100, 101, 110 and 111 in binary.",
                    "Those are 4, 5, 6 and 7.",
                    "The sum is <strong>22</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ smallest string from leaf
    "smallest-string-from-leaf": {
        "example": {"call": "smallest_from_leaf(build([0, 1, 3, None, None, None, 2, 0, 0]))", "expect": "'acda'"},
        "approaches": {
            "Backtrack the path, compare at each leaf": {
                "idea": [
                    "Greedily following the smaller child fails, because what matters is the whole string read from the leaf upwards.",
                    "Instead, keep the root-to-node letters, and at every leaf build the reversed string and keep the smallest.",
                ],
                "steps": [
                    "Append a letter; at a leaf, compare <code>\"\".join(reversed(path))</code> with the best; recurse; pop.",
                ],
                "why": [
                    "Each leaf builds an O(h) string: O(n·h) worst case.",
                ],
                "dry": [
                    "The tree: a → (b, d), d → (None, c), c → (a, a).",
                    "Leaf b gives \"ba\". Each a under c gives \"acda\".",
                    "\"acda\" &lt; \"ba\", so the result is <strong>'acda'</strong>. Greedy would have picked the smaller child b and returned \"ba\".",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pseudo-palindromic paths
    "pseudo-palindromic-paths": {
        "example": {"call": "pseudo_palindromic_paths(build([2, 3, 1, 3, 1, None, 1]))", "expect": "2"},
        "approaches": {
            "Parity bitmask": {
                "idea": [
                    "Some ordering of the digits forms a palindrome when <strong>at most one digit appears an odd number of times</strong>.",
                    "Track only the parities: bit d of <code>mask</code> flips each time digit d is seen.",
                    "At a leaf, \"at most one bit set\" is <code>mask &amp; (mask - 1) == 0</code>.",
                ],
                "steps": [
                    "<code>mask ^= 1 &lt;&lt; val</code>; at a leaf, test it; otherwise add the children's counts.",
                ],
                "why": [
                    "The mask is passed by value, so there is nothing to undo: O(n) time, O(h) stack.",
                ],
                "dry": [
                    "Path 2 – 3 – 3: bits 2 and 3 flip, then 3 flips back, leaving only bit 2. ✓",
                    "Path 2 – 3 – 1 leaves three odd digits ✗. Path 2 – 1 – 1 leaves only bit 2 ✓.",
                    "The result is <strong>2</strong>.",
                ],
            },
            "Counter with backtracking": {
                "idea": [
                    "Count the digits on the current path in a Counter; at a leaf, count how many are odd.",
                ],
                "steps": [
                    "Increment, recurse (or check at a leaf), decrement.",
                ],
                "why": [
                    "It is correct, but it scans up to 9 counts per leaf and must undo each change.",
                ],
                "dry": [
                    "Leaf counts {2: 1, 3: 2} have one odd ✓; {2: 1, 3: 1, 1: 1} have three ✗; {2: 1, 1: 2} have one ✓.",
                    "The result is <strong>2</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max path sum
    "binary-tree-maximum-path-sum": {
        "example": {"call": "max_path_sum(build([-10, 9, 20, None, None, 15, 7]))", "expect": "42"},
        "approaches": {
            "Postorder gain with a global best": {
                "idea": [
                    "<code>gain(node)</code> = the best sum of a path that starts at node and goes down <em>one</em> side. That is the only kind a parent can extend.",
                    "Clamp each child's gain at 0, since a negative arm is better left out.",
                    "The path bending here is <code>val + left + right</code>; record it globally but never return it.",
                ],
                "steps": [
                    "<code>best = max(best, val + left + right)</code>; return <code>val + max(left, right)</code>.",
                ],
                "why": [
                    "Every path bends at exactly one highest node, so checking every bend checks every path: O(n).",
                ],
                "dry": [
                    "The tree: -10 → (9, 20), 20 → (15, 7).",
                    "gain(15) = 15, gain(7) = 7. At 20: bend 20 + 15 + 7 = 42, return 35. gain(9) = 9.",
                    "At -10: bend -10 + 9 + 35 = 34 &lt; 42. The result is <strong>42</strong>.",
                ],
            },
            "Brute force: every node as the bend, recomputed": {
                "idea": [
                    "For each node, compute its best downward arm on each side from scratch, and take the best bend.",
                ],
                "steps": [
                    "Visit every node; <code>bend = val + max(0, arm(l)) + max(0, arm(r))</code>.",
                ],
                "why": [
                    "Arms are recomputed by every ancestor: O(n²) on a chain.",
                ],
                "dry": [
                    "At 20: arms 15 and 7 give 42. At -10: arm(9) = 9 and arm(20) = 35 give 34.",
                    "The result is <strong>42</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path sum III
    "path-sum-iii": {
        "example": {"call": "path_sum_iii(build([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]), 8)", "expect": "3"},
        "approaches": {
            "Prefix sums with a backtracked counter": {
                "idea": [
                    "Let <code>running</code> be the sum from the root to this node. A downward path ending here sums to the target when some <em>ancestor</em> prefix equals <code>running - target</code>.",
                    "A Counter of the prefixes on the current path answers that in O(1). This is subarray-sum-equals-k on a tree.",
                    "Remove this node's prefix after its subtree is done, so the left side's prefixes do not leak into the right.",
                ],
                "steps": [
                    "Seed <code>{0: 1}</code>; <code>found = prefixes[running - target]</code>; add, recurse, remove.",
                ],
                "why": [
                    "It is O(n) time, and the counter holds one entry per node on the current path.",
                ],
                "dry": [
                    "The tree: 10 → (5, -3), 5 → (3, 2), 3 → (3, -2), 2 → (None, 1), -3 → (None, 11).",
                    "At 10 → 5 → 3, running = 18 and 18 - 8 = 10 is a prefix: path 5 + 3 ✓. At 10 → 5 → 2 → 1, running = 18: path 5 + 2 + 1 ✓.",
                    "At 10 → -3 → 11, running = 18: path -3 + 11 ✓. The result is <strong>3</strong>.",
                ],
            },
            "Start a Path Sum search at every node": {
                "idea": [
                    "For each node, count the downward paths that start there with a second DFS, then do the same for every node.",
                ],
                "steps": [
                    "<code>from_here(root) + recurse(left) + recurse(right)</code>.",
                ],
                "why": [
                    "Each node is revisited once per ancestor: O(n·h).",
                ],
                "dry": [
                    "From 5: 5 + 3 and 5 + 2 + 1 both reach 8. From -3: -3 + 11 reaches 8.",
                    "Other starts find nothing. The result is <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ good leaf pairs
    "good-leaf-node-pairs": {
        "example": {"call": "count_pairs(build([1, 2, 3, 4, 5, 6, 7]), 3)", "expect": "2"},
        "approaches": {
            "Return a histogram of leaf depths": {
                "idea": [
                    "Each call returns <code>counts[k]</code> = the number of leaves exactly k edges below it, for k ≤ distance.",
                    "At a node, a left leaf at depth a and a right leaf at depth b are (a + 1) + (b + 1) apart, so count the pairs within the distance.",
                    "Each pair is counted once, at its lowest common ancestor.",
                ],
                "steps": [
                    "A leaf returns [1, 0, …]. Pair up the left and right counts; shift both down by one to return.",
                ],
                "why": [
                    "It is O(n·d²) with d ≤ 10: effectively linear.",
                ],
                "dry": [
                    "At 2: leaves 4 and 5 are 2 apart ≤ 3, so 1 pair; return [0, 2, 0, 0]. At 3, likewise: 1 pair.",
                    "At the root: the cross pairs are 4 apart &gt; 3, so 0.",
                    "The total is <strong>2</strong>.",
                ],
            },
            "Build a graph, BFS from every leaf": {
                "idea": [
                    "Turn the tree into an undirected graph, BFS out to the distance from each leaf, count the leaves reached, then halve.",
                ],
                "steps": [
                    "Each pair is found from both ends, so divide by 2.",
                ],
                "why": [
                    "It is O(L·n) for L leaves.",
                ],
                "dry": [
                    "Each of 4, 5, 6 and 7 reaches only its sibling within 3 steps: 4 finds in total.",
                    "4 // 2 = <strong>2</strong>.",
                ],
            },
        },
    },
}
