"""Write-ups for Trees, part B: aggregates, root-to-leaf paths, arbitrary paths."""

_T3 = "build([3, 9, 20, None, None, 15, 7])"
_SHAPE3 = "The tree: 3 has children 9 and 20; 9 is a leaf; 20 has children 15 and 7."

EXPLAIN = {
    # ------------------------------------------------------------------ balanced
    "balanced-binary-tree": {
        "examples": [
            {"call": f"is_balanced({_T3})", "expect": "True"},
            {"call": "is_balanced(build([1, 2, None, 3]))", "expect": "False"},
        ],
        "approaches": {
            "Top-down, recomputing heights": {
                "idea": [
                    "A tree is height-balanced when, at <em>every</em> node, the heights of the left and right subtrees differ by at most 1.",
                    "The direct reading: measure both heights at the root and compare, then ask the same question of each child.",
                    "It is simple but wasteful, because <code>height()</code> re-walks the same subtrees for every ancestor.",
                ],
                "steps": [
                    "If <code>root</code> is None, return True.",
                    "Compute <code>height(root.left)</code> and <code>height(root.right)</code> with a separate recursive helper.",
                    "If they differ by more than 1, return False.",
                    "Otherwise return <code>is_balanced(root.left) and is_balanced(root.right)</code>.",
                    "<code>height(None) = 0</code>, and <code>height(node) = 1 + max(...)</code> of its children.",
                ],
                "why": [
                    "It checks the balance condition at every node, which is exactly the definition, so it is correct.",
                    "A node at depth d has its subtree measured by each of its d ancestors' height calls. On a balanced tree the depth is O(log n), so the total is <strong>O(n log n)</strong> time.",
                    "Both recursions are bounded by the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        _SHAPE3,
                        "At 3: height(9) = 1, height(20) = 2. Difference 1, fine.",
                        "is_balanced(9): heights 0 and 0. Its None children return True.",
                        "is_balanced(20): heights 1 and 1; 15 and 7 are leaves, also fine.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "The tree is a left chain 1 → 2 → 3.",
                        "At 1: height(2) walks 2 and 3 and returns 2. height(None) = 0.",
                        "The difference is 2 &gt; 1, so it returns False at once.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Isn't it enough to compare the two heights at the root?",
                     "No. build([1, 2, 2, 3, None, None, 3, 4, None, None, 4]) has both root subtrees of height 3, but each 2 has one child chain of length 2 and nothing on the other side."],
                    ["Why is a balanced input the slow case?",
                     "An unbalanced root fails immediately. Only when every check passes does the recursion go everywhere, re-measuring each subtree once per ancestor."],
                    ["How do I make it O(n)?",
                     "Compute heights bottom-up once and let the same pass report failure, as in the sentinel approach."],
                ],
            },
            "Bottom-up with a sentinel": {
                "idea": [
                    "Compute each height exactly once, on the way back up, and check the balance at the same time.",
                    "<code>check(node)</code> returns the subtree's height, or <strong>-1</strong> if the subtree is already unbalanced; a real height is never negative, so -1 cannot be confused with one.",
                    "Once a -1 appears, every ancestor just passes it up without doing any more work.",
                ],
                "steps": [
                    "<code>check(None)</code> returns 0.",
                    "Compute <code>left = check(node.left)</code>; if it is -1, return -1 without looking right.",
                    "Compute <code>right = check(node.right)</code>; if it is -1, return -1.",
                    "If <code>abs(left - right) &gt; 1</code>, return -1; otherwise return <code>1 + max(left, right)</code>.",
                    "<code>is_balanced</code> returns <code>check(root) != -1</code>.",
                ],
                "why": [
                    "A non-negative return is the correct height of a subtree whose every node passed the check, so the balance condition is tested at every node with correct heights.",
                    "Each node is visited once with O(1) work: <strong>O(n)</strong> time.",
                    "Only the recursion stack is used: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "check(9): 0 and 0, returns 1.",
                        "check(15) = 1, check(7) = 1, so check(20) returns 2.",
                        "At 3: |1 − 2| = 1, so it returns 3.",
                        "3 != -1. The result is <strong>True</strong>.",
                    ],
                    [
                        "check(3) returns 1.",
                        "check(2): left 1, right 0, |1 − 0| = 1, returns 2.",
                        "check(1): left 2, right 0, difference 2, returns -1.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why -1 as the failure signal?",
                     "Heights are always 0 or more, so -1 is free to mean \"unbalanced\". It lets one integer carry both answers without a tuple."],
                    ["Why check <code>left == -1</code> before computing <code>right</code>?",
                     "If the left side already failed, the right side cannot change the answer, so skipping it saves work."],
                    ["Could I return a (balanced, height) pair instead?",
                     "Yes, it is the same algorithm and some find it clearer. The sentinel just avoids building tuples."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ diameter
    "diameter-of-binary-tree": {
        "examples": [
            {"call": "diameter(build([1, 2, 3, 4, 5]))", "expect": "3"},
            {"call": "diameter(build([1, 2, None, 3, 4, 5, None, None, 6]))", "expect": "4"},
        ],
        "approaches": {
            "Postorder height with a nonlocal best": {
                "idea": [
                    "Every path has one highest node where it bends. Through that node its length is left height + right height, counted in edges.",
                    "So compute heights bottom-up and, at each node, try the path that bends there.",
                    "The parent needs the <em>height</em>, not the diameter, so return the height and record the diameter in a shared <code>best</code>.",
                ],
                "steps": [
                    "Set <code>best = 0</code>.",
                    "<code>height(None)</code> returns 0.",
                    "At a node, compute <code>left</code> and <code>right</code> heights recursively.",
                    "Update <code>best = max(best, left + right)</code>: the path that bends here.",
                    "Return <code>1 + max(left, right)</code>; after <code>height(root)</code>, return <code>best</code>.",
                ],
                "why": [
                    "The longest path bends at some node, and at that node it is the deepest leaf on the left plus the deepest on the right, which is exactly <code>left + right</code>; trying every node finds it.",
                    "With a leaf's height counted as 1, <code>left + right</code> already counts edges: each side contributes the edge from the bend node down.",
                    "One visit per node: <strong>O(n)</strong> time and <strong>O(h)</strong> stack space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3), 2 → (4, 5).",
                        "4 and 5 return height 1. At 2: best = 1 + 1 = 2; return 2.",
                        "At 3: best stays 2; return 1.",
                        "At 1: 2 + 1 = 3, best = 3.",
                        "The result is <strong>3</strong> (4 – 2 – 1 – 3).",
                    ],
                    [
                        "The tree: 1 → 2 (left only); 2 → (3, 4); 3 has a left child 5; 4 has a right child 6.",
                        "5 and 6 return 1. At 3: best = 1, return 2. At 4: best stays 1, return 2.",
                        "At 2: 2 + 2 = 4, best = 4; return 3.",
                        "At 1: 3 + 0 = 3, which does not beat 4.",
                        "The result is <strong>4</strong> (5 – 3 – 2 – 4 – 6), a path that does not go through the root.",
                    ],
                ],
                "faq": [
                    ["Why not just return <code>height(left) + height(right)</code> at the root?",
                     "The longest path may not go through the root. In the second example the root gives 3, but the answer is 4, bending at node 2."],
                    ["Why <code>nonlocal best</code>?",
                     "The helper assigns to <code>best</code>; without <code>nonlocal</code> Python would treat it as a new local variable and raise UnboundLocalError."],
                    ["Is the answer in nodes or edges?",
                     "Edges. If a problem wanted nodes, it would be <code>left + right + 1</code>."],
                ],
            },
            "Returning a (height, diameter) pair": {
                "idea": [
                    "The same algorithm without a shared variable: each call returns its height <em>and</em> the best diameter anywhere inside its subtree.",
                    "A node's best diameter is the largest of its left subtree's best, its right subtree's best, and the path bending at itself.",
                    "Pure functions like this are easier to test and reason about.",
                ],
                "steps": [
                    "<code>solve(None)</code> returns <code>(0, 0)</code>.",
                    "Get <code>(lh, ld)</code> from the left child and <code>(rh, rd)</code> from the right.",
                    "Let <code>here = lh + rh</code>, the path bending at this node.",
                    "Return <code>(1 + max(lh, rh), max(ld, rd, here))</code>.",
                    "<code>diameter</code> returns <code>solve(root)[1]</code>.",
                ],
                "why": [
                    "Every path in a subtree either bends at its root or lies entirely in one child subtree, so the max of the three covers all cases.",
                    "One call per node: <strong>O(n)</strong> time.",
                    "Recursion depth h: <strong>O(h)</strong> space; the tuples are constant-size.",
                ],
                "dry": [
                    [
                        "4 and 5 return (1, 0). At 2: here = 2, returns (2, 2).",
                        "3 returns (1, 0).",
                        "At 1: here = 2 + 1 = 3, returns (3, max(2, 0, 3)) = (3, 3).",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "5 returns (1, 0); 3 returns (2, 1). 6 returns (1, 0); 4 returns (2, 1).",
                        "At 2: here = 4, returns (3, max(1, 1, 4)) = (3, 4).",
                        "At 1: lh = 3, rh = 0, here = 3; returns (4, max(4, 0, 3)) = (4, 4).",
                        "The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why carry the diameter up instead of just the height?",
                     "Without a shared variable, the only way a deep best path can reach the top is through the return values."],
                    ["Does the tuple make it slower?",
                     "Only by a constant factor; it is still O(n)."],
                    ["Which version should I write in an interview?",
                     "Either. The nonlocal version is shorter; the pair version shows you know how to avoid global state."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ tilt
    "binary-tree-tilt": {
        "examples": [
            {"call": "find_tilt(build([4, 2, 9, 3, 5, None, 7]))", "expect": "15"},
            {"call": "find_tilt(build([1, 2, 3]))", "expect": "1"},
        ],
        "approaches": {
            "Postorder sum with an accumulator": {
                "idea": [
                    "A node's tilt is |sum of its left subtree − sum of its right subtree|, and the answer is the sum of all tilts.",
                    "Both subtree sums are needed before a node's tilt can be computed, so this is postorder.",
                    "The helper returns the subtree <em>sum</em> (what the parent needs) and adds the tilt to a shared <code>total</code>.",
                ],
                "steps": [
                    "Set <code>total = 0</code>.",
                    "<code>subtree_sum(None)</code> returns 0.",
                    "At a node, get <code>left</code> and <code>right</code> sums recursively.",
                    "Add <code>abs(left - right)</code> to <code>total</code>.",
                    "Return <code>node.val + left + right</code>; after the call on the root, return <code>total</code>.",
                ],
                "why": [
                    "Each subtree sum is computed once, bottom-up, and each node's tilt uses the exact sums of its two subtrees.",
                    "One visit per node: <strong>O(n)</strong> time.",
                    "Recursion stack only: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 4 → (2, 9); 2 → (3, 5); 9 has a right child 7.",
                        "Leaves 3, 5, 7 have tilt 0 and return their values.",
                        "At 2: |3 − 5| = 2, total = 2, returns 10. At 9: |0 − 7| = 7, total = 9, returns 16.",
                        "At 4: |10 − 16| = 6, total = 15.",
                        "The result is <strong>15</strong>.",
                    ],
                    [
                        "Leaves 2 and 3 have tilt 0.",
                        "At 1: |2 − 3| = 1, total = 1.",
                        "It returns the sum 6, which is not used.",
                        "The result is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return the sum and not the tilt?",
                     "The parent's tilt needs the sums of its subtrees, not their tilts. The tilts are collected separately in <code>total</code>."],
                    ["Does the node's own value enter its tilt?",
                     "No, only the two subtree sums. It is included in the sum returned to the parent."],
                    ["What about negative values?",
                     "<code>abs</code> handles them; sums and tilts work the same with any integers."],
                ],
            },
            "Returning a (sum, tilt) pair": {
                "idea": [
                    "A pure version: each call returns its subtree sum and the total tilt of all nodes inside its subtree.",
                    "A node's accumulated tilt is the left subtree's tilt + the right subtree's tilt + its own tilt.",
                    "No shared variable is needed.",
                ],
                "steps": [
                    "<code>solve(None)</code> returns <code>(0, 0)</code>.",
                    "Get <code>(ls, lt)</code> from the left and <code>(rs, rt)</code> from the right.",
                    "The sum is <code>node.val + ls + rs</code>.",
                    "The tilt is <code>lt + rt + abs(ls - rs)</code>.",
                    "<code>find_tilt</code> returns <code>solve(root)[1]</code>.",
                ],
                "why": [
                    "Every node's tilt is added exactly once, at that node, and is then carried up inside its ancestors' totals.",
                    "One call per node: <strong>O(n)</strong> time.",
                    "<strong>O(h)</strong> recursion depth.",
                ],
                "dry": [
                    [
                        "3 → (3, 0), 5 → (5, 0), so 2 → (10, 0 + 0 + 2) = (10, 2).",
                        "7 → (7, 0), so 9 → (16, 7).",
                        "4 → (4 + 10 + 16, 2 + 7 + 6) = (30, 15).",
                        "The result is <strong>15</strong>.",
                    ],
                    [
                        "2 → (2, 0) and 3 → (3, 0).",
                        "1 → (6, 0 + 0 + 1) = (6, 1).",
                        "Take the tilt part.",
                        "The result is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Is it different in complexity from the accumulator version?",
                     "No, both are O(n) time and O(h) space."],
                    ["Why might I prefer it?",
                     "No hidden state: the function's output depends only on its input, which is easier to test."],
                    ["Could I compute subtree sums first and tilts in a second pass?",
                     "Yes, storing sums in a dictionary, but that costs O(n) extra space for no gain."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max ancestor diff
    "max-diff-node-ancestor": {
        "examples": [
            {"call": "max_ancestor_diff(build([8, 3, 10, 1, 6]))", "expect": "7"},
            {"call": "max_ancestor_diff(build([1, None, 2, None, 0, 3]))", "expect": "3"},
        ],
        "approaches": {
            "Top-down: carry the path's min and max": {
                "idea": [
                    "For a fixed node, the best ancestor to compare with is either the smallest or the largest value above it.",
                    "So pass the minimum <code>lo</code> and maximum <code>hi</code> of the current root-to-node path down the recursion.",
                    "The biggest |difference| on a path is <code>hi - lo</code> at its end, so return that when the path ends at None.",
                ],
                "steps": [
                    "Define <code>walk(node, lo, hi)</code>.",
                    "If <code>node</code> is None, return <code>hi - lo</code>: the spread of the path that just ended.",
                    "Update <code>lo = min(lo, node.val)</code> and <code>hi = max(hi, node.val)</code>.",
                    "Return the max of <code>walk</code> on both children.",
                    "Start with <code>walk(root, root.val, root.val)</code>.",
                ],
                "why": [
                    "Any ancestor–descendant pair lies on one root-to-leaf path, and the largest difference on a path is its max minus its min, so the answer is the largest spread over all paths.",
                    "Each node is visited once: <strong>O(n)</strong> time.",
                    "Only two numbers per call: <strong>O(h)</strong> stack space.",
                ],
                "dry": [
                    [
                        "The tree: 8 → (3, 10); 3 → (1, 6).",
                        "walk(8): lo = hi = 8. walk(3): lo = 3, hi = 8.",
                        "walk(1): lo = 1, hi = 8; its None children return 8 − 1 = 7. walk(6): lo 3, hi 8, returns 5. So 3 gives 7.",
                        "walk(10): lo 8, hi 10, returns 2. max(7, 2) = 7.",
                        "The result is <strong>7</strong> (8 and 1).",
                    ],
                    [
                        "The tree is a chain 1 → 2 → 0 → 3 (right, right, left).",
                        "walk(1): lo = hi = 1; its missing left child returns 0.",
                        "walk(2): (1, 2). walk(0): (0, 2). walk(3): (0, 3); its None children return 3.",
                        "Going back up the maximum stays 3.",
                        "The result is <strong>3</strong> (0 and its descendant 3).",
                    ],
                ],
                "faq": [
                    ["Why only the min and max, not the whole path?",
                     "|a − x| over ancestors a is largest at an extreme ancestor value, so the min and max are all that matter."],
                    ["Why return <code>hi - lo</code> at None rather than at leaves?",
                     "It is simpler and still correct: every path ends in None, and a one-child node's None side just repeats its own spread."],
                    ["Why start with <code>root.val</code> for both bounds?",
                     "The root is on every path. Starting at ±infinity would give infinite differences at the first None."],
                ],
            },
            "Bottom-up: return the subtree's min and max": {
                "idea": [
                    "Flip the view: for a fixed ancestor, the best descendant is the smallest or the largest value in its subtree.",
                    "So <code>span(node)</code> returns the min and max of its subtree, and each node compares itself with its children's spans.",
                    "<code>best</code> records the largest difference seen.",
                ],
                "steps": [
                    "Set <code>best = 0</code>.",
                    "In <code>span(node)</code>, start with <code>lo = hi = node.val</code>.",
                    "For each existing child, get <code>(clo, chi) = span(child)</code>.",
                    "Update <code>best</code> with <code>abs(node.val - clo)</code> and <code>abs(node.val - chi)</code>, then widen <code>lo</code> and <code>hi</code>.",
                    "Return <code>(lo, hi)</code>; after <code>span(root)</code>, return <code>best</code>.",
                ],
                "why": [
                    "Each node is compared with the extremes of its descendants, which are the best possible partners for it as the ancestor.",
                    "One call per node with O(1) work: <strong>O(n)</strong> time.",
                    "<strong>O(h)</strong> recursion space.",
                ],
                "dry": [
                    [
                        "span(1) = (1, 1). At 3: best = |3 − 1| = 2; lo 1, hi 3.",
                        "span(6) = (6, 6). At 3: best = 3; returns (1, 6).",
                        "At 8 with (1, 6): best = |8 − 1| = 7. With 10's (10, 10): 2, no change.",
                        "span(8) = (1, 10).",
                        "The result is <strong>7</strong>.",
                    ],
                    [
                        "span(3) = (3, 3). At 0: best = |0 − 3| = 3; returns (0, 3).",
                        "At 2: |2 − 0| = 2 and |2 − 3| = 1, best stays 3; returns (0, 3).",
                        "At 1: |1 − 0| = 1 and |1 − 3| = 2; returns (0, 3).",
                        "The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>abs</code> here when the top-down version uses <code>hi - lo</code>?",
                     "Here the node's value is compared with one bound at a time, and the descendant can be larger or smaller, so the sign is unknown."],
                    ["What if the tree is empty?",
                     "<code>span(None)</code> would fail on <code>node.val</code>. The problem guarantees at least two nodes; add a guard otherwise."],
                    ["Which direction is more natural?",
                     "Top-down is shorter; bottom-up is the pattern you need when a parent must combine facts about whole subtrees."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ longest univalue path
    "longest-univalue-path": {
        "examples": [
            {"call": "longest_univalue_path(build([1, 4, 5, 4, 4, None, 5]))", "expect": "2"},
            {"call": "longest_univalue_path(build([9, 2, None, 2, 2, 2, None, None, 2]))", "expect": "4"},
        ],
        "approaches": {
            "Return the longest arm, record the bend": {
                "idea": [
                    "This is the diameter pattern restricted to equal values: a path bends at its top node and has a left arm and a right arm.",
                    "An <em>arm</em> from a node is the longest downward run of nodes with the same value, measured in edges.",
                    "A child's arm only extends to the parent if the child has the parent's value; otherwise the arm through that side is 0.",
                ],
                "steps": [
                    "Set <code>best = 0</code>; <code>arm(None)</code> returns 0.",
                    "Compute both children's arms first, recursively, even if their values differ (their subtrees may hide long paths).",
                    "<code>left = left + 1</code> if <code>node.left</code> exists and has <code>node.val</code>, else 0; the same for <code>right</code>.",
                    "Update <code>best = max(best, left + right)</code>: the path bending here.",
                    "Return <code>max(left, right)</code>: a parent can extend only one arm.",
                ],
                "why": [
                    "Every same-value path has a highest node, and there its length is the left arm plus the right arm; trying every node finds the longest.",
                    "Recursing into every child regardless of value matters: a different-valued child may contain its own longer path, which is recorded in <code>best</code> while its arm resets to 0 for the parent.",
                    "One visit per node: <strong>O(n)</strong> time and <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (4, 5); 4 → (4, 4); 5 has a right child 5.",
                        "The leaf 4s return 0. At the inner 4: both children are 4, so left = right = 1; best = 2; return 1.",
                        "The leaf 5 returns 0. At the upper 5: right = 1, left = 0; best stays 2; return 1.",
                        "At 1: neither child is 1, so both arms are 0.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "The tree: 9 → 2a (left); 2a → (2b, 2c); 2b has a left 2; 2c has a right 2.",
                        "At 2b: left arm 1, best = 1, return 1. At 2c: right arm 1, return 1.",
                        "At 2a: left = 1 + 1 = 2, right = 1 + 1 = 2; best = 4; return 2.",
                        "At 9: its child is 2, not 9, so the arm is 0; best stays 4.",
                        "The result is <strong>4</strong>, found entirely below the root.",
                    ],
                ],
                "faq": [
                    ["Why are both recursive calls made before checking values?",
                     "A child with a different value can still contain a long same-value path underneath it, as in the second example. Skipping it would miss that."],
                    ["Why <code>left + right</code> and not <code>left + right + 1</code>?",
                     "The answer counts edges. Each arm already counts the edge to the child, so adding them gives the path length in edges."],
                    ["Why return only the longer arm?",
                     "A path that continues up to the parent cannot use both arms; it would fork."],
                ],
            },
            "Pure version: return (arm, best)": {
                "idea": [
                    "The same algorithm without a nonlocal: each call returns its longest same-value arm and the best path anywhere in its subtree.",
                    "The best for a node is the largest of its children's bests and the path bending at itself.",
                    "Arms are extended or reset to 0 by comparing with the children's values, exactly as before.",
                ],
                "steps": [
                    "<code>solve(None)</code> returns <code>(0, 0)</code>.",
                    "Unpack <code>(la, lb)</code> and <code>(ra, rb)</code> from the two children.",
                    "Set <code>la = la + 1</code> if the left child has the same value, else 0; the same for <code>ra</code>.",
                    "Return <code>(max(la, ra), max(lb, rb, la + ra))</code>.",
                    "The answer is <code>solve(root)[1]</code>.",
                ],
                "why": [
                    "Any same-value path in a subtree either bends at its root or lies inside one child, so the max of the three is right.",
                    "One call per node: <strong>O(n)</strong> time.",
                    "<strong>O(h)</strong> recursion depth.",
                ],
                "dry": [
                    [
                        "Leaf 4s return (0, 0). Inner 4: la = ra = 1, returns (1, 2).",
                        "Leaf 5 returns (0, 0). Upper 5: ra = 1, returns (1, 1).",
                        "At 1: la = ra = 0; returns (0, max(2, 1, 0)) = (0, 2).",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "The deepest 2s return (0, 0). 2b returns (1, 1); 2c returns (1, 1).",
                        "2a: la = 2, ra = 2, returns (2, max(1, 1, 4)) = (2, 4).",
                        "9: its child differs, la = 0; returns (0, 4).",
                        "The result is <strong>4</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the empty tree give 0?",
                     "<code>solve(None)</code> returns (0, 0), and the answer is its second part."],
                    ["Is <code>node.left and ...</code> safe when the child is None?",
                     "Yes. <code>and</code> short-circuits, so <code>node.left.val</code> is never read when the child is missing."],
                    ["Any advantage over the nonlocal version?",
                     "Only style: no shared mutable state. Complexity is the same."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path sum
    "path-sum": {
        "examples": [
            {"call": "has_path_sum(build([1, 2, 3, 4]), 7)", "expect": "True"},
            {"call": "has_path_sum(build([1, 2]), 1)", "expect": "False"},
        ],
        "approaches": {
            "Recursive, subtracting as you go": {
                "idea": [
                    "Instead of summing the path and comparing at the end, subtract each node's value from <code>target</code> on the way down.",
                    "A path works when the remaining target is exactly 0 <strong>at a leaf</strong>; reaching 0 at an inner node does not count.",
                    "Any one successful branch is enough, so combine the children with <code>or</code>.",
                ],
                "steps": [
                    "If <code>root</code> is None, return False.",
                    "Subtract: <code>target -= root.val</code>.",
                    "If <code>root</code> is a leaf, return <code>target == 0</code>.",
                    "Otherwise return <code>has_path_sum(root.left, target) or has_path_sum(root.right, target)</code>.",
                ],
                "why": [
                    "The remaining target at a node equals the original target minus the sum of the path to it, so 0 at a leaf means the full root-to-leaf sum is right.",
                    "Each node is visited at most once, and <code>or</code> stops on the first success: <strong>O(n)</strong> time.",
                    "<strong>O(h)</strong> recursion depth.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3); 2 has a left child 4. target = 7.",
                        "At 1: remaining 6, not a leaf. At 2: remaining 4, not a leaf.",
                        "At 4: remaining 0 and 4 is a leaf, so True.",
                        "<code>or</code> stops; 3 is never visited.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "The tree: 1 with a left child 2. target = 1.",
                        "At 1: remaining 0, but 1 has a child, so it is not a leaf.",
                        "At 2: remaining −2, a leaf, so False. The missing right child returns False.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not return True as soon as the remaining target hits 0?",
                     "That would accept a path that stops at an inner node. On build([1, 2]) with target 1 it would return True, but the only root-to-leaf path sums to 3."],
                    ["Can I prune when the remaining target goes negative?",
                     "No. Values can be negative, so a later node can bring it back up."],
                    ["What does an empty tree give with target 0?",
                     "False. There is no root-to-leaf path at all, so no path can sum to anything."],
                ],
            },
            "Iterative DFS with running sums": {
                "idea": [
                    "Replace recursion with a stack of <code>(node, total)</code> pairs, where <code>total</code> is the sum of the path above that node.",
                    "Add the node's value when it is popped, and test at leaves.",
                    "Every root-to-leaf path is followed once, so a match cannot be missed.",
                ],
                "steps": [
                    "Start with <code>stack = [(root, 0)]</code>, or empty if <code>root</code> is None.",
                    "Pop <code>(node, total)</code> and add <code>node.val</code> to <code>total</code>.",
                    "If <code>node</code> is a leaf and <code>total == target</code>, return True.",
                    "Push each existing child with the updated <code>total</code>.",
                    "If the stack empties, return False.",
                ],
                "why": [
                    "The <code>total</code> stored with a child is exactly the sum of its ancestors, so at a leaf it is the full path sum.",
                    "Each node is pushed and popped once: <strong>O(n)</strong> time.",
                    "The stack holds <strong>O(h)</strong> pending pairs for a DFS, and it avoids Python's recursion limit.",
                ],
                "dry": [
                    [
                        "stack = [(1, 0)]. Pop: total 1; push (2, 1), (3, 1).",
                        "Pop (3, 1): total 4; a leaf, but 4 ≠ 7.",
                        "Pop (2, 1): total 3; push (4, 3).",
                        "Pop (4, 3): total 7; a leaf and equal to 7.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "stack = [(1, 0)]. Pop: total 1, equal to the target, but 1 is not a leaf. Push (2, 1).",
                        "Pop (2, 1): total 3, a leaf, 3 ≠ 1.",
                        "The stack is empty.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store the total with each node?",
                     "Different branches have different path sums. Storing it per stack entry means no undoing is needed when you jump to another branch."],
                    ["Does the order of pushing children matter?",
                     "No, only which leaf is found first."],
                    ["Why <code>[(root, 0)] if root else []</code>?",
                     "An empty tree has no paths, and an empty stack makes the loop return False straight away."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path sum II
    "path-sum-ii": {
        "examples": [
            {"call": "path_sum(build([1, 2, 3, 3, None, 2]), 6)", "expect": "[[1, 2, 3], [1, 3, 2]]"},
            {"call": "path_sum(build([1, -2, -3, 1, 3, -2, None, -1]), -1)", "expect": "[[1, -2, 1, -1]]"},
        ],
        "approaches": {
            "Backtracking with one shared path": {
                "idea": [
                    "Now every matching root-to-leaf path must be returned, so the current path has to be kept.",
                    "Keep one list <code>path</code>: append a node when entering it and pop it when leaving (choose, explore, un-choose).",
                    "At a leaf with remaining target 0, store a <strong>copy</strong> of the path, because the live list keeps changing.",
                ],
                "steps": [
                    "Set <code>out = []</code> and <code>path = []</code>.",
                    "<code>dfs(node, remaining)</code>: return on None; append <code>node.val</code> and subtract it from <code>remaining</code>.",
                    "If <code>node</code> is a leaf and <code>remaining == 0</code>, append <code>path[:]</code> to <code>out</code>.",
                    "Recurse into both children with the new <code>remaining</code>.",
                    "Pop from <code>path</code> before returning; call <code>dfs(root, target)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Because each node is popped when its call ends, <code>path</code> always equals the root-to-current-node path, so recorded copies are correct paths.",
                    "Each node is visited once, but copying a path of length up to h at each matching leaf costs O(h): <strong>O(n · h)</strong> time in the worst case.",
                    "Besides the output, <code>path</code> and the recursion are <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3); 2 has a left child 3; 3 has a left child 2. target = 6.",
                        "dfs(1): path [1], remaining 5. dfs(2): [1, 2], 3. dfs(3): [1, 2, 3], 0 at a leaf: record [1, 2, 3]; pop.",
                        "Back to [1, 2]; its right child is None; pop to [1].",
                        "dfs(3): [1, 3], 2. dfs(2): [1, 3, 2], 0 at a leaf: record it; pop twice.",
                        "The result is <strong>[[1, 2, 3], [1, 3, 2]]</strong>.",
                    ],
                    [
                        "The tree: 1 → (−2, −3); −2 → (1, 3); −3 → (−2, -); the lower 1 has a left child −1. target = −1.",
                        "1: remaining −2. −2: remaining 0, but this is not a leaf, so keep going.",
                        "1: remaining −1. −1: remaining 0 at a leaf: record [1, −2, 1, −1].",
                        "3: remaining −3, no. −3 then −2: remaining 1 then 3, no.",
                        "The result is <strong>[[1, −2, 1, −1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>path[:]</code> and not <code>path</code>?",
                     "<code>path</code> is one list that is popped empty by the end. Appending it directly stores the same object several times, and every entry ends up as []."],
                    ["Why is the time O(n · h) and not O(n)?",
                     "The walk is O(n), but each recorded path costs a copy of up to h values, and there can be about n/2 leaves."],
                    ["Can I stop when remaining is 0 at an inner node?",
                     "No. In the second example remaining is 0 at −2, yet the right path continues to 1 and −1, which sum back to 0."],
                ],
            },
            "New list per call": {
                "idea": [
                    "Avoid backtracking by giving each call its own list: <code>path = path + [node.val]</code> builds a fresh list.",
                    "Nothing is ever undone, because the parent's list is never modified.",
                    "At a matching leaf the list can be stored directly, since nobody else will change it.",
                ],
                "steps": [
                    "<code>dfs(node, remaining, path)</code>: return on None.",
                    "Build <code>path = path + [node.val]</code> and subtract from <code>remaining</code>.",
                    "If at a leaf and <code>remaining == 0</code>, append <code>path</code> to <code>out</code>.",
                    "Recurse into both children with the new list.",
                    "Start with <code>dfs(root, target, [])</code>.",
                ],
                "why": [
                    "Each call's list is exactly its root-to-node path, so recorded lists are correct and independent.",
                    "Every call copies a list of up to h items: <strong>O(n · h)</strong> time, even for paths that do not match.",
                    "All lists on the current recursion path are alive at once, 1 + 2 + … + h items: <strong>O(h²)</strong> space.",
                ],
                "dry": [
                    [
                        "dfs(1): path [1], remaining 5.",
                        "dfs(2): new list [1, 2], 3. dfs(3): new list [1, 2, 3], 0 at a leaf: store it.",
                        "dfs(3) on the right: new list [1, 3], 2; dfs(2): [1, 3, 2], 0: store it.",
                        "The parent's lists were never changed.",
                        "The result is <strong>[[1, 2, 3], [1, 3, 2]]</strong>.",
                    ],
                    [
                        "Lists grow [1] → [1, −2] → [1, −2, 1] → [1, −2, 1, −1], remaining −2, 0, −1, 0.",
                        "At −1 (a leaf) remaining is 0: store the list.",
                        "[1, −2, 3] ends at −3; [1, −3, −2] ends at 3. Neither is stored.",
                        "The result is <strong>[[1, −2, 1, −1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is this slower than backtracking?",
                     "It copies a list at every node, not only at matching leaves. Backtracking copies only when it records a result."],
                    ["Why is no copy needed when storing?",
                     "Each list is created fresh in its own call and never modified afterwards."],
                    ["When is this style worth it?",
                     "When clarity matters more than speed, or when the recursion is made parallel or iterative and a shared list would be awkward."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ binary tree paths
    "binary-tree-paths": {
        "examples": [
            {"call": "binary_tree_paths(build([1, 2, 3, None, 5]))", "expect": "['1->2->5', '1->3']"},
            {"call": "binary_tree_paths(build([-1, 2, None, -3]))", "expect": "['-1->2->-3']"},
        ],
        "approaches": {
            "Backtracking list, join at the leaf": {
                "idea": [
                    "Every root-to-leaf path must be returned as a string like <code>\"1-&gt;2-&gt;5\"</code>.",
                    "Keep the current path as a list of strings, appending on entry and popping on exit.",
                    "Only at a leaf join it with <code>\"-&gt;\"</code>, so strings are built once per path, not once per node.",
                ],
                "steps": [
                    "Set <code>out = []</code> and <code>path = []</code>.",
                    "<code>dfs(node)</code>: return on None; append <code>str(node.val)</code>.",
                    "If <code>node</code> is a leaf, append <code>\"-&gt;\".join(path)</code> to <code>out</code>.",
                    "Recurse into the left then the right child.",
                    "Pop the last entry before returning.",
                ],
                "why": [
                    "<code>path</code> always holds the current root-to-node path, so the joined string at each leaf is that leaf's path.",
                    "Each node is visited once, and each join costs O(h): <strong>O(n · h)</strong> time in the worst case.",
                    "Besides the output, <strong>O(h)</strong> space for <code>path</code> and the recursion.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3); 2 has a right child 5.",
                        "path ['1'] → ['1', '2']; 2's left is None.",
                        "['1', '2', '5'] at a leaf: record \"1-&gt;2-&gt;5\". Pop 5, pop 2.",
                        "['1', '3'] at a leaf: record \"1-&gt;3\".",
                        "The result is <strong>['1-&gt;2-&gt;5', '1-&gt;3']</strong>.",
                    ],
                    [
                        "The tree: −1 → 2 → −3, all left children.",
                        "path ['-1'] → ['-1', '2'] → ['-1', '2', '-3'].",
                        "−3 is a leaf: record the join.",
                        "The minus signs are part of each value's string, so joining is not confused by them.",
                        "The result is <strong>['-1-&gt;2-&gt;-3']</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store strings in <code>path</code> rather than ints?",
                     "<code>join</code> needs strings. Converting once on entry avoids converting the same value again for every leaf below it."],
                    ["Why not build the string as I go?",
                     "That works too (see the iterative version), but every node then creates a new string of growing length."],
                    ["What is the order of the result?",
                     "Left subtree paths first, because the left child is explored first."],
                ],
            },
            "Iterative, carrying the string": {
                "idea": [
                    "Use a stack of <code>(node, text)</code> pairs, where <code>text</code> is the finished path string up to that node.",
                    "A child gets <code>f\"{text}-&gt;{child.val}\"</code>; a leaf's text is a complete answer.",
                    "Push the right child first so the left one is popped first, matching the recursive order.",
                ],
                "steps": [
                    "Start with <code>stack = [(root, str(root.val))]</code>, or empty for no root.",
                    "Pop <code>(node, text)</code>.",
                    "If <code>node</code> is a leaf, append <code>text</code> to <code>out</code>.",
                    "For <code>child</code> in <code>(node.right, node.left)</code>, push it with the extended string.",
                    "Return <code>out</code> when the stack is empty.",
                ],
                "why": [
                    "Each stacked string is exactly the path to its node, because it was built from its parent's string.",
                    "Each node creates a string of up to O(h) characters: <strong>O(n · h)</strong> time.",
                    "Pending strings on the stack and in the output total <strong>O(n · h)</strong> space.",
                ],
                "dry": [
                    [
                        "stack = [(1, \"1\")]. Pop: push (3, \"1-&gt;3\"), then (2, \"1-&gt;2\").",
                        "Pop 2: push (5, \"1-&gt;2-&gt;5\").",
                        "Pop 5: a leaf, record it. Pop 3: a leaf, record it.",
                        "The result is <strong>['1-&gt;2-&gt;5', '1-&gt;3']</strong>.",
                    ],
                    [
                        "stack = [(−1, \"-1\")]. Pop: push (2, \"-1-&gt;2\").",
                        "Pop 2: push (−3, \"-1-&gt;2-&gt;-3\").",
                        "Pop −3: a leaf, record it.",
                        "The result is <strong>['-1-&gt;2-&gt;-3']</strong>.",
                    ],
                ],
                "faq": [
                    ["Why push the right child first?",
                     "The stack pops the last push first, so pushing right then left makes the left subtree come out first, like the recursive version."],
                    ["Why is the space O(n · h)?",
                     "Each pending stack entry holds its own string, and strings for different nodes are not shared."],
                    ["Does an empty tree work?",
                     "Yes, the stack starts empty and <code>[]</code> is returned."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sum root to leaf numbers
    "sum-root-to-leaf-numbers": {
        "examples": [
            {"call": "sum_numbers(build([1, 2, 3]))", "expect": "25"},
            {"call": "sum_numbers(build([4, 9, 0, 5, 1]))", "expect": "1026"},
        ],
        "approaches": {
            "Carry the number down": {
                "idea": [
                    "Each root-to-leaf path spells a number, one digit per node.",
                    "Going down one level appends a digit: <code>current * 10 + node.val</code>.",
                    "At a leaf the number is complete; add the leaf numbers from both subtrees.",
                ],
                "steps": [
                    "Define <code>dfs(node, current)</code>; if <code>node</code> is None, return 0.",
                    "Update <code>current = current * 10 + node.val</code>.",
                    "If <code>node</code> is a leaf, return <code>current</code>.",
                    "Otherwise return <code>dfs(node.left, current) + dfs(node.right, current)</code>.",
                    "The answer is <code>dfs(root, 0)</code>.",
                ],
                "why": [
                    "Shifting by ×10 and adding the next digit is how decimal numbers are read left to right, so <code>current</code> is the number of the path so far.",
                    "Only leaves return a number, and a None child returns 0, so each path is counted exactly once.",
                    "One visit per node: <strong>O(n)</strong> time, <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "dfs(1, 0): current 1, not a leaf.",
                        "dfs(2, 1): current 12, a leaf, return 12.",
                        "dfs(3, 1): current 13, a leaf, return 13.",
                        "The result is <strong>25</strong>.",
                    ],
                    [
                        "The tree: 4 → (9, 0); 9 → (5, 1).",
                        "4 → 49 → leaves 495 and 491; 9 returns 986.",
                        "4 → 40: 0 is a leaf, return 40.",
                        "986 + 40 = 1026.",
                        "The result is <strong>1026</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return the number only at leaves and not at None?",
                     "Returning <code>current</code> at None counts each leaf twice (once per missing child) and one-child nodes as paths. On build([1, 2, 3]) that gives 50 instead of 25."],
                    ["What about a 0 digit?",
                     "It is handled like any other digit: 4 then 0 gives 40."],
                    ["Can the numbers overflow?",
                     "Not in Python, whose ints are unbounded. In other languages LeetCode guarantees the answer fits in 32 bits."],
                ],
            },
            "BFS with (node, value) pairs": {
                "idea": [
                    "The same calculation in breadth-first order: each queue entry carries the number formed above it.",
                    "When a node is popped, append its digit; leaves add their number to <code>total</code>.",
                    "Children inherit the updated value.",
                ],
                "steps": [
                    "Start with <code>total = 0</code> and a queue holding <code>(root, 0)</code> if the root exists.",
                    "Pop <code>(node, value)</code> and set <code>value = value * 10 + node.val</code>.",
                    "If <code>node</code> is a leaf, add <code>value</code> to <code>total</code>.",
                    "Enqueue each existing child with <code>value</code>.",
                    "Return <code>total</code>.",
                ],
                "why": [
                    "Each entry's value is the number of the path above it, so a leaf's value is its full path number.",
                    "Each node is enqueued once: <strong>O(n)</strong> time.",
                    "The queue holds up to one level: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop (1, 0): value 1; enqueue (2, 1), (3, 1).",
                        "Pop (2, 1): 12, a leaf, total 12.",
                        "Pop (3, 1): 13, a leaf, total 25.",
                        "The result is <strong>25</strong>.",
                    ],
                    [
                        "Pop (4, 0): 4; enqueue (9, 4), (0, 4).",
                        "Pop 9: 49; enqueue (5, 49), (1, 49). Pop 0: 40, a leaf, total 40.",
                        "Pop 5: 495, total 535. Pop 1: 491, total 1026.",
                        "The result is <strong>1026</strong>.",
                    ],
                ],
                "faq": [
                    ["Does BFS order change the answer?",
                     "No. Addition is order-independent, so any traversal gives the same total."],
                    ["When is BFS preferable here?",
                     "On very deep, narrow trees, where recursion could hit the limit."],
                    ["Why carry the value in the queue rather than in a dict?",
                     "Each value is used only by its node's children, so the queue entry is the natural place for it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ sum binary root to leaf
    "sum-root-to-leaf-binary": {
        "examples": [
            {"call": "sum_root_to_leaf(build([1, 0, 1, 0, 1, 0, 1]))", "expect": "22"},
            {"call": "sum_root_to_leaf(build([1, 1]))", "expect": "3"},
        ],
        "approaches": {
            "Carry the number, shift left": {
                "idea": [
                    "Each root-to-leaf path is a binary number, most significant bit at the root.",
                    "Going down one level shifts the number left one bit and ORs in the new bit: <code>(current &lt;&lt; 1) | node.val</code>.",
                    "It is Sum Root to Leaf Numbers in base 2 instead of base 10.",
                ],
                "steps": [
                    "Define <code>dfs(node, current)</code>; return 0 for None.",
                    "Set <code>current = (current &lt;&lt; 1) | node.val</code>.",
                    "If <code>node</code> is a leaf, return <code>current</code>.",
                    "Otherwise return the sum of <code>dfs</code> on both children.",
                    "The answer is <code>dfs(root, 0)</code>.",
                ],
                "why": [
                    "Shifting left doubles the number and frees the lowest bit, and OR places the new bit there, which is how binary numbers are read left to right.",
                    "Only leaves contribute, and None returns 0, so each path is counted once.",
                    "One visit per node: <strong>O(n)</strong> time, <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (0, 1); both have children (0, 1).",
                        "Root: 1. Left 0: (1 &lt;&lt; 1) | 0 = 2; its leaves give 4 (100) and 5 (101).",
                        "Right 1: 3; its leaves give 6 (110) and 7 (111).",
                        "4 + 5 + 6 + 7 = 22.",
                        "The result is <strong>22</strong>.",
                    ],
                    [
                        "Root: 1, not a leaf.",
                        "Left child 1: (1 &lt;&lt; 1) | 1 = 3, a leaf.",
                        "The missing right child returns 0.",
                        "The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>| node.val</code> the same as <code>+ node.val</code>?",
                     "Here yes: after the shift the lowest bit is 0 and <code>node.val</code> is 0 or 1. <code>current * 2 + node.val</code> is equivalent."],
                    ["Why not build a string and call <code>int(s, 2)</code>?",
                     "It works but costs O(h) per leaf. The shift is O(1) per node."],
                    ["What about a single-node tree?",
                     "The root is a leaf, so the answer is its bit, 0 or 1."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ smallest string from leaf
    "smallest-string-from-leaf": {
        "examples": [
            {"call": "smallest_from_leaf(build([0, 1, 2, 3, 4, 3, 4]))", "expect": "'dba'"},
            {"call": "smallest_from_leaf(build([0, 1, 3, None, None, None, 2, 0, 0]))", "expect": "'acda'"},
        ],
        "approaches": {
            "Backtrack the path, compare at each leaf": {
                "idea": [
                    "Each leaf-to-root path spells a string (value 0 is <code>'a'</code>, 1 is <code>'b'</code>, ...). The answer is the lexicographically smallest one.",
                    "Strings are read from the leaf upwards, so a greedy walk from the root that picks the smaller child does not work: the deciding letters are at the bottom.",
                    "So collect the path with backtracking and, at every leaf, build its reversed string and compare it with the best so far.",
                ],
                "steps": [
                    "Set <code>best = None</code> and <code>path = []</code>.",
                    "<code>dfs(node)</code>: return on None; append <code>chr(ord(\"a\") + node.val)</code>.",
                    "At a leaf, build <code>s = \"\".join(reversed(path))</code>; if <code>best</code> is None or <code>s &lt; best</code>, set <code>best = s</code>.",
                    "Recurse into both children.",
                    "Pop the letter before returning; return <code>best</code> after <code>dfs(root)</code>.",
                ],
                "why": [
                    "Every leaf's full string is built and compared, so the minimum over all leaves cannot be missed.",
                    "Building and comparing a string of length up to h at each leaf gives <strong>O(n · h)</strong> time in the worst case.",
                    "<code>path</code>, one candidate string and the recursion take <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: a → (b, c); b → (d, e); c → (d, e).",
                        "Leaf d under b: path [a, b, d] gives \"dba\"; best = \"dba\".",
                        "Leaf e under b: \"eba\" is larger. Leaf d under c: \"dca\" &gt; \"dba\" at the second letter.",
                        "Leaf e under c: \"eca\", larger.",
                        "The result is <strong>'dba'</strong>.",
                    ],
                    [
                        "The tree: a → (b, d); b is a leaf; d → c (right); c → (a, a).",
                        "Leaf b: \"ba\"; best = \"ba\". A greedy walk from the root would stop here.",
                        "Leaf a under c: path [a, d, c, a] gives \"acda\" &lt; \"ba\"; best = \"acda\".",
                        "The other a leaf gives \"acda\" again, not smaller.",
                        "The result is <strong>'acda'</strong>.",
                    ],
                ],
                "faq": [
                    ["Why doesn't picking the smaller child at each step work?",
                     "The string starts at the leaf, so the root's choice affects the <em>last</em> letters. In the second example greedy follows 'b' and returns \"ba\", but \"acda\" is smaller."],
                    ["Why can't I compare without building the whole string?",
                     "You can with care, but strings of different lengths compare by prefix (\"ab\" &lt; \"abc\"), and building the string is the simple, safe way."],
                    ["Why start <code>best</code> as None?",
                     "Any sentinel string could compare wrongly; None means \"nothing yet\" and the first leaf always replaces it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ pseudo-palindromic paths
    "pseudo-palindromic-paths": {
        "examples": [
            {"call": "pseudo_palindromic_paths(build([2, 3, 1, 3, 1, None, 1]))", "expect": "2"},
            {"call": "pseudo_palindromic_paths(build([1, 2, 3]))", "expect": "0"},
        ],
        "approaches": {
            "Parity bitmask": {
                "idea": [
                    "A multiset of digits can be rearranged into a palindrome when <strong>at most one</strong> digit appears an odd number of times.",
                    "Only the parity of each count matters, so keep one bit per digit 1–9 and flip it with XOR on every occurrence.",
                    "At a leaf the path is pseudo-palindromic exactly when the mask has at most one set bit: <code>mask &amp; (mask - 1) == 0</code>.",
                ],
                "steps": [
                    "Define <code>dfs(node, mask)</code>; return 0 for None.",
                    "Flip this digit's bit: <code>mask ^= 1 &lt;&lt; node.val</code>.",
                    "At a leaf, return 1 if <code>mask &amp; (mask - 1) == 0</code>, else 0.",
                    "Otherwise return the sum of <code>dfs</code> on both children.",
                    "The answer is <code>dfs(root, 0)</code>.",
                ],
                "why": [
                    "After the XORs, bit d is 1 exactly when digit d occurs an odd number of times on the path; <code>mask &amp; (mask - 1)</code> clears the lowest set bit, so it is 0 only when at most one bit was set.",
                    "The mask is an int passed by value, so each branch has its own copy and nothing needs undoing.",
                    "O(1) per node: <strong>O(n)</strong> time, <strong>O(h)</strong> recursion space.",
                ],
                "dry": [
                    [
                        "The tree: 2 → (3, 1); 3 → (3, 1); 1 has a right child 1.",
                        "At 2: mask = 100 (binary, bit 2). At 3: 1100. Leaf 3: 0100, one bit set, count 1.",
                        "Leaf 1 under 3: 1110, three bits set, 0.",
                        "Right 1: 0110; leaf 1 below it: 0100, one bit, count 1.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "At 1: mask = 10 (binary).",
                        "Leaf 2: 110, two bits set (1 and 2 both odd), 0.",
                        "Leaf 3: 1010, two bits set, 0.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>mask &amp; (mask - 1)</code> test for at most one bit?",
                     "Subtracting 1 flips the lowest set bit and every bit below it, so the AND removes exactly that lowest bit. The result is 0 only if no other bit was set."],
                    ["Why <code>1 &lt;&lt; node.val</code> and not <code>1 &lt;&lt; (node.val - 1)</code>?",
                     "Either works as long as it is consistent. Using the value directly wastes bit 0, which is harmless."],
                    ["Why no backtracking here?",
                     "Ints are immutable and each call gets its own <code>mask</code>, so a child's changes never leak back to the parent."],
                ],
            },
            "Counter with backtracking": {
                "idea": [
                    "Count each digit on the current path in a shared <code>Counter</code>, incrementing on entry and decrementing on exit.",
                    "At a leaf, count how many digits have an odd count; at most one means the path can form a palindrome.",
                    "This is the direct version of the parity idea, without bit tricks.",
                ],
                "steps": [
                    "Create <code>counts = Counter()</code>.",
                    "<code>dfs(node)</code>: return 0 on None; do <code>counts[node.val] += 1</code>.",
                    "At a leaf, <code>found = 1</code> if <code>sum(c % 2 for c in counts.values()) &lt;= 1</code>, else 0.",
                    "Otherwise <code>found</code> is the sum of <code>dfs</code> on both children.",
                    "Decrement <code>counts[node.val]</code> (backtrack) and return <code>found</code>.",
                ],
                "why": [
                    "Thanks to the decrement on exit, <code>counts</code> always describes exactly the current root-to-node path.",
                    "Each node is O(1), and each leaf scans at most 9 keys: <strong>O(n · 9)</strong>, i.e. O(n), time.",
                    "The counter holds at most 9 keys, so space is the recursion depth, <strong>O(h)</strong>.",
                ],
                "dry": [
                    [
                        "Path 2, 3, 3: counts {2: 1, 3: 2}, one odd, found 1. Back out of the leaf: 3 drops to 1.",
                        "Path 2, 3, 1: {2: 1, 3: 1, 1: 1}, three odd, 0.",
                        "Path 2, 1, 1: {2: 1, 1: 2} (3 is now 0), one odd, 1.",
                        "Each count returns to 0 as the recursion unwinds.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "Path 1, 2: {1: 1, 2: 1}, two odd, 0. Back out: 2 drops to 0.",
                        "Path 1, 3: {1: 1, 2: 0, 3: 1}, two odd, 0.",
                        "Zero counts are even, so leftover keys do no harm.",
                        "The result is <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the decrement happen even at a leaf?",
                     "The leaf's digit was added on entry. Without removing it, it would be counted on the sibling's path too."],
                    ["Is the bitmask version faster?",
                     "Slightly: it checks the leaf in O(1) instead of scanning up to 9 counts. Both are O(n)."],
                    ["Why keep keys with count 0 in the Counter?",
                     "They are even, so they do not affect the odd count; deleting them would only save a little scanning."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max path sum
    "binary-tree-maximum-path-sum": {
        "examples": [
            {"call": "max_path_sum(build([-10, 9, 20, None, None, 15, 7]))", "expect": "42"},
            {"call": "max_path_sum(build([-2, -1]))", "expect": "-1"},
        ],
        "approaches": {
            "Postorder gain with a global best": {
                "idea": [
                    "A path bends at its highest node; its sum is that node's value plus the best downward arm on each side.",
                    "A negative arm only hurts, so clamp each arm at 0: taking no arm is always allowed.",
                    "The parent can only extend one arm, so <code>gain</code> returns <code>node.val + max(left, right)</code> while the two-armed bend updates <code>best</code>.",
                ],
                "steps": [
                    "Set <code>best = float(\"-inf\")</code>; <code>gain(None)</code> returns 0.",
                    "<code>left = max(gain(node.left), 0)</code> and <code>right = max(gain(node.right), 0)</code>.",
                    "Update <code>best = max(best, node.val + left + right)</code>: the path bending here.",
                    "Return <code>node.val + max(left, right)</code> to the parent.",
                    "Call <code>gain(root)</code> and return <code>best</code>.",
                ],
                "why": [
                    "Every path has one top node, and the best path with that top uses the best non-negative arm on each side, which is exactly what is tried there.",
                    "Each node is visited once: <strong>O(n)</strong> time, <strong>O(h)</strong> recursion space.",
                    "<code>best</code> starts at minus infinity because the path must contain at least one node, and all values may be negative.",
                ],
                "dry": [
                    [
                        "The tree: −10 → (9, 20); 20 → (15, 7).",
                        "gain(9): best = 9, returns 9. gain(15): best = 15, returns 15. gain(7) returns 7.",
                        "gain(20): bend 20 + 15 + 7 = 42, best = 42; returns 35.",
                        "gain(−10): bend −10 + 9 + 35 = 34, best stays 42.",
                        "The result is <strong>42</strong> (15 – 20 – 7).",
                    ],
                    [
                        "The tree: −2 with a left child −1.",
                        "gain(−1): bend −1, best = −1; returns −1.",
                        "At −2: left = max(−1, 0) = 0, right = 0; bend −2, best stays −1.",
                        "The result is <strong>−1</strong>, a single node.",
                    ],
                ],
                "faq": [
                    ["Why start <code>best</code> at minus infinity instead of 0?",
                     "With 0, an all-negative tree like the second example returns 0, but the path must contain at least one node, so the answer is −1."],
                    ["Why return only one arm to the parent?",
                     "A path through the parent can enter this node from above and continue down one side only; using both would fork the path."],
                    ["Why clamp arms at 0 but not the node's own value?",
                     "Arms are optional, so a negative arm is dropped. The bend node itself is the path's top and must be included."],
                ],
            },
            "Brute force: every node as the bend, recomputed": {
                "idea": [
                    "Try every node as the top of the path and compute its best downward arms from scratch.",
                    "<code>arm(node)</code> is the best downward path starting at <code>node</code>: its value plus the better non-negative child arm.",
                    "This repeats the same arm computations many times, which is what the postorder version avoids.",
                ],
                "steps": [
                    "<code>arm(None)</code> returns 0; otherwise <code>node.val + max(0, arm(left), arm(right))</code>.",
                    "Set <code>best = -inf</code> and walk all nodes with a stack.",
                    "For each <code>node</code>, compute <code>bend = node.val + max(0, arm(node.left)) + max(0, arm(node.right))</code>.",
                    "Update <code>best</code> and push the existing children.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "Each node's bend is the best path whose top is that node, and every node is tried, so the maximum is found.",
                    "Each <code>arm</code> call walks a whole subtree, and every node is walked once per ancestor: <strong>O(n²)</strong> on a chain (O(n log n) when balanced).",
                    "The arm recursion and the stack are <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop −10: arm(9) = 9, arm(20) = 20 + 15 = 35; bend 34, best = 34.",
                        "Pop 20: arm(15) = 15, arm(7) = 7; bend 42, best = 42.",
                        "Pop 7 (bend 7), 15 (bend 15), 9 (bend 9): no improvement.",
                        "The arms under 20 were computed twice.",
                        "The result is <strong>42</strong>.",
                    ],
                    [
                        "Pop −2: arm(−1) = −1, clamped to 0; bend −2, best = −2.",
                        "Push −1. Pop −1: no children, bend −1, best = −1.",
                        "The stack is empty.",
                        "The result is <strong>−1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is it quadratic on a chain?",
                     "Each node's arm walks everything below it: n + (n − 1) + … + 1 steps."],
                    ["Why does <code>arm</code> use <code>max(0, ...)</code> on the children only?",
                     "The arm must start at <code>node</code>, so its value is always included; only the continuation is optional."],
                    ["What is it good for?",
                     "As a reference to test the O(n) version against, and as a stepping stone to the idea of returning arms bottom-up."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ path sum III
    "path-sum-iii": {
        "examples": [
            {"call": "path_sum_iii(build([10, 5, -3, 3, 2, None, 11]), 8)", "expect": "2"},
            {"call": "path_sum_iii(build([0, 0, 0]), 0)", "expect": "5"},
        ],
        "approaches": {
            "Prefix sums with a backtracked counter": {
                "idea": [
                    "A downward path from an ancestor to the current node sums to <code>running - earlier</code>, where both are prefix sums along the root-to-node path.",
                    "So the number of valid paths ending at the current node is how many earlier prefixes equal <code>running - target</code>: the subarray-sum-equals-k trick, on a tree path.",
                    "The counter must describe only the current root-to-node path, so each prefix is removed when its node's call ends.",
                ],
                "steps": [
                    "Start with <code>prefixes = Counter({0: 1})</code>: the empty prefix before the root.",
                    "In <code>dfs(node, running)</code>, return 0 on None; add <code>node.val</code> to <code>running</code>.",
                    "<code>found = prefixes[running - target]</code>: paths ending here.",
                    "Add <code>running</code> to the counter, add the results from both children.",
                    "Decrement <code>prefixes[running]</code> before returning <code>found</code>.",
                ],
                "why": [
                    "Each prefix in the counter belongs to an ancestor (or the empty start), so every match is a real downward path ending at this node, and every such path is matched once.",
                    "O(1) average Counter work per node: <strong>O(n)</strong> time.",
                    "The counter holds at most h + 1 live prefixes and the recursion is h deep: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 10 → (5, −3); 5 → (3, 2); −3 has a right child 11. target 8.",
                        "10: running 10, look up 2: 0. 5: running 15, look up 7: 0.",
                        "3: running 18, look up 10: 1 (the path 5 → 3). 2: running 17, look up 9: 0.",
                        "−3: running 7, look up −1: 0. 11: running 18, look up 10: 1 (−3 → 11).",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "Root 0: running 0, look up 0: 1 (just the root); counter {0: 2}.",
                        "Left 0: running 0, look up 0: 2 (the leaf alone, and root → leaf); then the counter goes back to {0: 2}.",
                        "Right 0: also 2.",
                        "1 + 2 + 2 = 5.",
                        "The result is <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start with <code>{0: 1}</code>?",
                     "It stands for the empty prefix before the root, so paths that start at the root itself are counted."],
                    ["What breaks without the decrement?",
                     "Prefixes from a finished sibling branch stay in the counter. On build([1, 2, 3]) with target 1, the right leaf would match the left leaf's prefix and the count would be 2 instead of 1."],
                    ["Why look up before adding the current prefix?",
                     "Adding first would let a node match its own prefix when the target is 0, counting an empty path."],
                ],
            },
            "Start a Path Sum search at every node": {
                "idea": [
                    "Every downward path has a starting node. For each node, count the paths that start there and go down.",
                    "<code>from_here(node, remaining)</code> counts paths from <code>node</code> downward whose sum equals <code>remaining</code>; it never stops early because negative values can follow.",
                    "The outer function adds the count for the root and recurses to start from every other node.",
                ],
                "steps": [
                    "<code>from_here(None, ...)</code> returns 0.",
                    "Subtract <code>node.val</code> from <code>remaining</code>; count 1 if it is 0.",
                    "Add <code>from_here</code> on both children with the new remaining.",
                    "<code>path_sum_iii(root)</code> returns <code>from_here(root, target)</code> plus <code>path_sum_iii</code> of both children.",
                ],
                "why": [
                    "Each downward path is counted exactly once, from its starting node, at the point where it ends.",
                    "Each node is scanned once per ancestor (and itself): <strong>O(n · h)</strong> time, which is O(n²) for a chain.",
                    "Two nested recursions, each at most h deep: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "From 10: sums 10, 15, 18, 17, 7, 18 never hit 8: 0.",
                        "From 5: 5, then 8 at 3 (count 1), 7 at 2.",
                        "From 3, 2: no. From −3: −3, then 8 at 11 (count 1).",
                        "From 11: no.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "From the root: the root alone, root → left, root → right all sum to 0: 3.",
                        "From the left 0: 1. From the right 0: 1.",
                        "Leaves give from_here(None) = 0 below them.",
                        "The result is <strong>5</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not stop once the sum reaches the target?",
                     "Further nodes could sum to zero, like the zeros in the second example, giving more valid paths."],
                    ["Why is it O(n · h)?",
                     "A node is included in the scan started from each of its ancestors, and it has at most h of them."],
                    ["When is it acceptable?",
                     "On balanced trees it is O(n log n) and easy to write; on a chain it degrades to O(n²)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ good leaf node pairs
    "good-leaf-node-pairs": {
        "examples": [
            {"call": "count_pairs(build([1, 2, 3, None, 4]), 3)", "expect": "1"},
            {"call": "count_pairs(build([1, 2, 3, 4, 5, 6, 7]), 3)", "expect": "2"},
        ],
        "approaches": {
            "Return a histogram of leaf depths": {
                "idea": [
                    "Two leaves meet at their lowest common ancestor; their distance is the depth of one below it plus the depth of the other.",
                    "So each node returns <code>counts[k]</code>: how many leaves sit k edges below it (only up to <code>distance</code>).",
                    "At a node, pair every left leaf at depth a+1 with every right leaf at depth b+1 when the total is within <code>distance</code>.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns all zeros; a leaf returns <code>counts[0] = 1</code>.",
                    "Get <code>left</code> and <code>right</code> histograms from the children.",
                    "For each <code>a</code> and each <code>b</code> in <code>range(distance - a - 1)</code>, add <code>left[a] * right[b]</code> to <code>pairs</code>: (a + 1) + (b + 1) ≤ distance.",
                    "Shift up one edge: <code>counts[k + 1] = left[k] + right[k]</code>.",
                    "Return <code>counts</code>; the answer is <code>pairs</code> after <code>dfs(root)</code>.",
                ],
                "why": [
                    "Each pair of leaves is counted at exactly one node, their lowest common ancestor, where they are on opposite sides.",
                    "Each node does a double loop over at most d + 1 depths: <strong>O(n · d²)</strong> time.",
                    "Each live call holds a list of d + 1 counts: <strong>O(h · d)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (2, 3); 2 has a right child 4. distance 3, lists have 4 slots.",
                        "Leaf 4: [1, 0, 0, 0]. At 2: left is all zero, no pairs; counts = [0, 1, 0, 0].",
                        "Leaf 3: [1, 0, 0, 0].",
                        "At 1: a = 1, b = 0: left[1] · right[0] = 1, total distance 2 + 1 = 3. pairs = 1.",
                        "The result is <strong>1</strong>.",
                    ],
                    [
                        "Leaves 4, 5, 6, 7 each return [1, 0, 0, 0].",
                        "At 2: a = 0, b = 0: 1 · 1 = 1 pair (4, 5); counts [0, 2, 0, 0]. At 3: the pair (6, 7); counts [0, 2, 0, 0].",
                        "At 1: a = 1 allows only b = 0, and right[0] = 0. Cross pairs would be 4 apart.",
                        "pairs = 2.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>range(distance - a - 1)</code>?",
                     "The left leaf is a + 1 edges from this node and the right leaf b + 1. Requiring (a + 1) + (b + 1) ≤ distance means b ≤ distance − a − 2."],
                    ["Why cap the histogram at <code>distance</code>?",
                     "A leaf deeper than that below a node can never pair through it or any ancestor, so it can be dropped."],
                    ["Why count at the common ancestor only?",
                     "Pairs on the same side were already counted lower down; counting them again would double them."],
                ],
            },
            "Build a graph, BFS from every leaf": {
                "idea": [
                    "Turn the tree into an undirected graph so you can walk up as well as down.",
                    "From each leaf, BFS out to <code>distance</code> steps and count the other leaves reached.",
                    "Each pair is found from both ends, so divide by 2.",
                ],
                "steps": [
                    "Walk the tree with a stack; add parent–child edges both ways to <code>graph</code> and collect <code>leaves</code>.",
                    "For each <code>start</code> leaf, BFS level by level for <code>distance</code> rounds with a <code>seen</code> set.",
                    "Each newly reached node that is in <code>leaf_set</code> adds 1 to <code>found</code>.",
                    "Return <code>found // 2</code>.",
                ],
                "why": [
                    "BFS reaches exactly the nodes within <code>distance</code> edges, and tree paths are unique, so each good pair is counted once from each end.",
                    "Each of the L leaves may BFS over the whole tree: <strong>O(L · n)</strong> time.",
                    "The graph and the BFS sets are <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Leaves are 3 and 4. Edges: 1–2, 1–3, 2–4.",
                        "From 3: step 1 reaches 1, step 2 reaches 2, step 3 reaches 4, a leaf: found = 1.",
                        "From 4: step 1 reaches 2, step 2 reaches 1, step 3 reaches 3: found = 2.",
                        "2 // 2 = 1.",
                        "The result is <strong>1</strong>.",
                    ],
                    [
                        "Leaves in stack order: 7, 6, 5, 4.",
                        "From 7: step 1 reaches 3; step 2 reaches 6 (a leaf, +1) and 1; step 3 reaches 2.",
                        "Each leaf finds only its sibling; 4, 5 are 4 steps from 6, 7. found = 4.",
                        "4 // 2 = 2.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why divide by 2?",
                     "Each pair (x, y) is found once from x and once from y."],
                    ["Why the <code>seen</code> set in a tree?",
                     "The graph edges go both ways, so without it BFS would step straight back to the node it came from."],
                    ["When would I prefer this?",
                     "It is simpler to reason about but slower; the histogram version is the expected answer for large trees."],
                ],
            },
        },
    },
}
