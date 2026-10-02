# -*- coding: utf-8 -*-
"""Binary Trees: height/diameter extras, root-to-leaf paths, arbitrary paths.

EXTRA holds problems appended to sections that already exist in dsa.py.
"""

EXTRA = {
    "aggregates": [

    dict(
        id="max-diff-node-ancestor",
        lc=1026, slug="maximum-difference-between-node-and-ancestor",
        name="Maximum Difference Between Node and Ancestor",
        difficulty="medium",
        framing=[
            "Find the largest <code>|a.val - b.val|</code> where <code>a</code> is an ancestor of <code>b</code>. The pair can be far apart vertically, so comparing a node with its parent is not enough.",
            "This is the first problem where information can usefully flow in <em>either</em> direction. Top-down, each node receives the smallest and largest values on the path above it. Bottom-up, each node returns the smallest and largest values below it. Both are O(n); choosing between them is the skill.",
        ],
        approaches=[
            dict(
                name="Top-down: carry the path's min and max",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "For a fixed node, the best ancestor to pair it with is either the smallest or the largest value above it. So pass <code>(lo, hi)</code> of the root-to-node path down the recursion; each node updates them with its own value.",
                    "At a leaf, <code>hi - lo</code> is the best difference achievable on that root-to-leaf path, and every ancestor/descendant pair lies on some root-to-leaf path. The answer is the maximum over leaves.",
                    "One visit per node with constant work: O(n). The recursion stack holds one path: O(h).",
                ],
                code='''def max_ancestor_diff(root):
    def walk(node, lo, hi):
        if node is None:
            return hi - lo                 # a path just ended
        lo, hi = min(lo, node.val), max(hi, node.val)
        return max(walk(node.left, lo, hi), walk(node.right, lo, hi))

    return walk(root, root.val, root.val)''',
            ),
            dict(
                name="Bottom-up: return the subtree's min and max",
                time="O(n)",
                space="O(h)",
                tag="return two values",
                why=[
                    "Each call returns the smallest and largest values in its subtree. The node then compares itself against both &mdash; they are exactly its best descendants to pair with &mdash; and records the difference in a <code>nonlocal</code>.",
                    "Same bounds. This is the \"return one thing, record another\" shape from Diameter, returning a pair instead of a single number. Worth writing both: the top-down version is shorter here, but the bottom-up one is the pattern that generalises to Maximum Sum BST and friends.",
                ],
                code='''def max_ancestor_diff(root):
    best = 0

    def span(node):
        nonlocal best
        lo = hi = node.val
        for child in (node.left, node.right):
            if child is not None:
                clo, chi = span(child)
                best = max(best, abs(node.val - clo), abs(node.val - chi))
                lo, hi = min(lo, clo), max(hi, chi)
        return lo, hi

    span(root)
    return best''',
            ),
        ],
        tests='''assert max_ancestor_diff(build([8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13])) == 7
assert max_ancestor_diff(build([1, None, 2, None, 0, 3])) == 3
assert max_ancestor_diff(build([5, 5])) == 0


def _brute(root):
    best = 0
    def walk(node, above):
        nonlocal best
        if node is None:
            return
        for a in above:
            best = max(best, abs(a - node.val))
        walk(node.left, above + [node.val]); walk(node.right, above + [node.val])
    walk(root, [])
    return best

for seed in range(40):
    t = random_tree(2 + seed % 15, seed, 0, 50)
    assert max_ancestor_diff(t) == _brute(t), seed''',
    ),

    dict(
        id="longest-univalue-path",
        lc=687, slug="longest-univalue-path",
        name="Longest Univalue Path",
        difficulty="medium",
        framing=[
            "The longest path, in <strong>edges</strong>, on which every node has the same value. Like Diameter, the path may bend at any node and need not touch the root.",
            "The twist over Diameter is that an arm can be <em>cut</em>: a child with a different value contributes nothing, even if a long univalue path sits below it. That path is still counted &mdash; it was recorded in the global answer when the recursion was down there.",
        ],
        pitfall="Returning <code>left + right</code> to the parent. A path that bends here cannot be extended upward; the parent can only continue <em>one</em> arm.",
        approaches=[
            dict(
                name="Return the longest arm, record the bend",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Each call returns the longest downward path starting at this node whose values all equal this node's value. A child's arm counts (plus the edge to it) only when the child has the same value; otherwise that side contributes 0.",
                    "The path bending here is <code>left_arm + right_arm</code> edges, and it goes into the global best. Only the longer arm goes back to the parent, because a path through the parent can enter this node from one side only.",
                    "This is precisely the Diameter template with one extra condition on each arm. O(n) time, O(h) stack.",
                ],
                code='''def longest_univalue_path(root):
    best = 0

    def arm(node):
        nonlocal best
        if node is None:
            return 0
        left, right = arm(node.left), arm(node.right)
        left = left + 1 if node.left and node.left.val == node.val else 0
        right = right + 1 if node.right and node.right.val == node.val else 0
        best = max(best, left + right)       # the path bending here
        return max(left, right)              # the parent may extend one arm

    arm(root)
    return best''',
            ),
            dict(
                name="Pure version: return (arm, best)",
                time="O(n)",
                space="O(h)",
                tag="no shared state",
                why=[
                    "Same algorithm, with the global folded into the return value so the helper has no side effects. Each call returns its arm and the best path found anywhere in its subtree.",
                    "Identical bounds. Useful to see side by side with the Diameter pair version: the only change is the equality test on each arm.",
                ],
                code='''def longest_univalue_path(root):
    return solve(root)[1]


def solve(node):
    """Return (longest same-value arm from node, best path in subtree)."""
    if node is None:
        return 0, 0
    (la, lb), (ra, rb) = solve(node.left), solve(node.right)
    la = la + 1 if node.left and node.left.val == node.val else 0
    ra = ra + 1 if node.right and node.right.val == node.val else 0
    return max(la, ra), max(lb, rb, la + ra)''',
            ),
        ],
        tests='''assert longest_univalue_path(build([5, 4, 5, 1, 1, None, 5])) == 2
assert longest_univalue_path(build([1, 4, 5, 4, 4, None, 5])) == 2
assert longest_univalue_path(None) == 0
assert longest_univalue_path(build([1])) == 0
assert longest_univalue_path(build([1, 1, 1, 1, 1, 1, 1])) == 4
# a long same-value path hidden under a different-valued node
assert longest_univalue_path(build([9, 2, None, 2, 2, 2, None, None, 2])) == 4''',
    ),
    ],
}


SECTIONS = [

# ---------------------------------------------------------------- root to leaf
dict(
    id="root-to-leaf",
    title="Root-to-leaf paths: carry state down, backtrack on the way up",
    idea=[
        "Every problem here walks from the root to each leaf, carrying something about the path: a running sum, the path itself, a number being built digit by digit, a parity mask. Leaves are where answers are produced.",
    ],
    problems=[

    dict(
        id="path-sum",
        lc=112, slug="path-sum",
        name="Path Sum",
        difficulty="easy",
        framing=[
            "Is there a root-to-<strong>leaf</strong> path whose values add up to <code>targetSum</code>? The whole family starts here: pass the <em>remaining</em> target down, and test it at the leaves.",
        ],
        pitfall="Checking the sum at <code>None</code> instead of at a leaf. A node with one child would then \"finish\" a path at its missing side, and <code>[1, 2]</code> with target 1 returns True.",
        approaches=[
            dict(
                name="Recursive, subtracting as you go",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Subtract the node's value from the target and ask the children the smaller question. At a leaf, the path is complete, and it matches exactly when the remainder is zero.",
                    "Short-circuiting <code>or</code> stops at the first matching path, but the worst case still visits every node: O(n). The stack holds one path: O(h).",
                ],
                code='''def has_path_sum(root, target):
    if root is None:
        return False
    target -= root.val
    if root.left is None and root.right is None:
        return target == 0                 # only leaves end a path
    return has_path_sum(root.left, target) or has_path_sum(root.right, target)''',
            ),
            dict(
                name="Iterative DFS with running sums",
                time="O(n)",
                space="O(h)",
                why=[
                    "Push <code>(node, sum so far)</code> pairs. This is the general technique for making any path-state recursion iterative: whatever the recursive call received as arguments goes on the stack with the node.",
                    "Same bounds, no recursion limit.",
                ],
                code='''def has_path_sum(root, target):
    stack = [(root, 0)] if root else []
    while stack:
        node, total = stack.pop()
        total += node.val
        if node.left is None and node.right is None and total == target:
            return True
        for child in (node.left, node.right):
            if child is not None:
                stack.append((child, total))
    return False''',
            ),
        ],
        tests='''assert has_path_sum(build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]), 22) is True
assert has_path_sum(build([1, 2, 3]), 5) is False
assert has_path_sum(None, 0) is False
assert has_path_sum(build([1, 2]), 1) is False      # 1 alone is not a leaf
assert has_path_sum(build([-2, None, -3]), -5) is True''',
    ),

    dict(
        id="path-sum-ii",
        lc=113, slug="path-sum-ii",
        name="Path Sum II",
        difficulty="medium",
        framing=[
            "Return <em>every</em> root-to-leaf path that sums to the target. Now the path itself is part of the state, which introduces <strong>backtracking</strong>: one shared list that you append to on the way down and pop from on the way back up.",
        ],
        pitfall="Appending <code>path</code> itself to the results. Every result then refers to the same list, which is empty by the time you return. Append a copy.",
        approaches=[
            dict(
                name="Backtracking with one shared path",
                time="O(n &middot; h)",
                space="O(h)",
                best=True,
                why=[
                    "Push the node, recurse, pop the node. Between the push and the pop, <code>path</code> is exactly the route from the root to the current node, so at a matching leaf you copy it into the output.",
                    "The traversal is O(n). Each match costs an O(h) copy, and there can be up to O(n) leaves, so the worst case is O(n &middot; h) &mdash; O(n log n) balanced, O(n&sup2;) degenerate. That cost is the size of the output, so no algorithm does better in the worst case.",
                    "Auxiliary space is the one shared path plus the stack: O(h).",
                ],
                code='''def path_sum(root, target):
    out, path = [], []

    def dfs(node, remaining):
        if node is None:
            return
        path.append(node.val)                      # choose
        remaining -= node.val
        if node.left is None and node.right is None and remaining == 0:
            out.append(path[:])                    # copy, not the live list
        dfs(node.left, remaining)                  # explore
        dfs(node.right, remaining)
        path.pop()                                 # un-choose

    dfs(root, target)
    return out''',
            ),
            dict(
                name="New list per call",
                time="O(n &middot; h)",
                space="O(h&sup2;)",
                tag="simpler, costlier",
                why=[
                    "Pass <code>path + [node.val]</code> to each child. No pop needed, because nobody shares a list &mdash; which is exactly why it costs more: every call on the current path holds its own copy, O(h) lists of up to O(h) each.",
                    "Time also rises to O(n &middot; h) even when nothing matches, because every node copies its path. Fine for small trees; backtracking is the version to show you understand.",
                ],
                code='''def path_sum(root, target):
    out = []

    def dfs(node, remaining, path):
        if node is None:
            return
        path = path + [node.val]                   # a fresh list each call
        remaining -= node.val
        if node.left is None and node.right is None and remaining == 0:
            out.append(path)
        dfs(node.left, remaining, path)
        dfs(node.right, remaining, path)

    dfs(root, target, [])
    return out''',
            ),
        ],
        tests='''assert path_sum(build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]), 22) == [[5, 4, 11, 2], [5, 8, 4, 5]]
assert path_sum(build([1, 2, 3]), 5) == []
assert path_sum(build([1, 2]), 0) == []
assert path_sum(None, 0) == []
assert path_sum(build([1, -2, -3, 1, 3, -2, None, -1]), -1) == [[1, -2, 1, -1]]''',
    ),

    dict(
        id="binary-tree-paths",
        lc=257, slug="binary-tree-paths",
        name="Binary Tree Paths",
        difficulty="easy",
        framing=[
            "Return every root-to-leaf path as a string like <code>\"1->2->5\"</code>. The same traversal as Path Sum II with no filter; the interesting choice is how to build the strings.",
        ],
        approaches=[
            dict(
                name="Backtracking list, join at the leaf",
                time="O(n &middot; h)",
                space="O(h)",
                best=True,
                why=[
                    "Keep the path as a list of value strings and <code>\"->\".join</code> it only when you reach a leaf. Joining is where the cost goes: O(h) per leaf, and the output itself is that big.",
                    "Building strings with <code>+</code> on the way down instead would copy an ever-longer string at every node, not just at leaves.",
                ],
                code='''def binary_tree_paths(root):
    out, path = [], []

    def dfs(node):
        if node is None:
            return
        path.append(str(node.val))
        if node.left is None and node.right is None:
            out.append("->".join(path))
        dfs(node.left)
        dfs(node.right)
        path.pop()

    dfs(root)
    return out''',
            ),
            dict(
                name="Iterative, carrying the string",
                time="O(n &middot; h)",
                space="O(n &middot; h)",
                why=[
                    "Each stack entry carries the string built so far. Simple and recursion-free, but every pending entry owns a string of up to O(h) characters, so the stack can hold O(n &middot; h) characters in total on a wide tree.",
                    "Push the right child first so the left path is produced first, matching the recursive order.",
                ],
                code='''def binary_tree_paths(root):
    out, stack = [], [(root, str(root.val))] if root else []
    while stack:
        node, text = stack.pop()
        if node.left is None and node.right is None:
            out.append(text)
        for child in (node.right, node.left):
            if child is not None:
                stack.append((child, f"{text}->{child.val}"))
    return out''',
            ),
        ],
        tests='''assert binary_tree_paths(build([1, 2, 3, None, 5])) == ["1->2->5", "1->3"]
assert binary_tree_paths(build([1])) == ["1"]
assert binary_tree_paths(None) == []
assert binary_tree_paths(build([-1, 2, None, -3])) == ["-1->2->-3"]''',
    ),

    dict(
        id="sum-root-to-leaf-numbers",
        lc=129, slug="sum-root-to-leaf-numbers",
        name="Sum Root to Leaf Numbers",
        difficulty="medium",
        framing=[
            "Each root-to-leaf path spells a number (<code>1 &rarr; 2 &rarr; 3</code> is 123). Return the sum of all of them. Instead of a path list, the state carried down is a single integer built digit by digit.",
        ],
        approaches=[
            dict(
                name="Carry the number down",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Moving one level down appends a digit: <code>current * 10 + node.val</code>. At a leaf the number is complete and is returned; internal nodes return the sum of their children's totals.",
                    "No path list, no strings: O(n) time and just the O(h) stack. Carrying a <em>summary</em> of the path instead of the path itself is the optimisation that makes this medium problem shorter than Binary Tree Paths.",
                ],
                code='''def sum_numbers(root):
    def dfs(node, current):
        if node is None:
            return 0
        current = current * 10 + node.val
        if node.left is None and node.right is None:
            return current
        return dfs(node.left, current) + dfs(node.right, current)

    return dfs(root, 0)''',
            ),
            dict(
                name="BFS with (node, value) pairs",
                time="O(n)",
                space="O(w)",
                why=[
                    "Same state, level by level. Space becomes the widest level instead of the height &mdash; the usual BFS/DFS trade.",
                ],
                code='''def sum_numbers(root):
    total, queue = 0, deque([(root, 0)] if root else [])
    while queue:
        node, value = queue.popleft()
        value = value * 10 + node.val
        if node.left is None and node.right is None:
            total += value
        for child in (node.left, node.right):
            if child is not None:
                queue.append((child, value))
    return total''',
            ),
        ],
        tests='''assert sum_numbers(build([1, 2, 3])) == 25
assert sum_numbers(build([4, 9, 0, 5, 1])) == 1026
assert sum_numbers(build([0])) == 0
assert sum_numbers(build([1, 0])) == 10''',
    ),

    dict(
        id="sum-root-to-leaf-binary",
        lc=1022, slug="sum-of-root-to-leaf-binary-numbers",
        name="Sum of Root To Leaf Binary Numbers",
        difficulty="easy",
        framing=[
            "The same problem in base 2: every node is 0 or 1, each path is a binary number, and you sum them. The only change is the digit step &mdash; which makes it a good check that you understood the previous problem rather than memorised it.",
        ],
        approaches=[
            dict(
                name="Carry the number, shift left",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Appending a binary digit is <code>current * 2 + bit</code>, or equivalently <code>(current &lt;&lt; 1) | bit</code>. Everything else is identical to Sum Root to Leaf Numbers.",
                    "In general, base <em>b</em> is <code>current * b + digit</code>: the same one-line change covers any base.",
                ],
                code='''def sum_root_to_leaf(root):
    def dfs(node, current):
        if node is None:
            return 0
        current = (current << 1) | node.val
        if node.left is None and node.right is None:
            return current
        return dfs(node.left, current) + dfs(node.right, current)

    return dfs(root, 0)''',
            ),
        ],
        tests='''assert sum_root_to_leaf(build([1, 0, 1, 0, 1, 0, 1])) == 22
assert sum_root_to_leaf(build([0])) == 0
assert sum_root_to_leaf(build([1, 1])) == 3''',
    ),

    dict(
        id="smallest-string-from-leaf",
        lc=988, slug="smallest-string-starting-from-leaf",
        name="Smallest String Starting From Leaf",
        difficulty="medium",
        framing=[
            "Values 0&ndash;25 are letters a&ndash;z. Read each path from the <strong>leaf up to the root</strong> and return the lexicographically smallest such string.",
            "It is tempting to go greedy &mdash; at each node, follow the child with the smaller letter &mdash; and it is wrong. The string is read leaf-first, so what decides the comparison is at the <em>bottom</em>, and a shorter string that is a prefix of a longer one wins (<code>\"ab\" &lt; \"abz\"</code>).",
        ],
        pitfall="Comparing children greedily, or comparing <code>min(left, right)</code> of partial strings built top-down. Build the full leaf-to-root string at each leaf and compare whole strings.",
        approaches=[
            dict(
                name="Backtrack the path, compare at each leaf",
                time="O(n &middot; h)",
                space="O(h)",
                best=True,
                why=[
                    "Keep the root-to-node letters in a list. At a leaf, reverse it into a string and keep the minimum.",
                    "Each leaf builds and compares an O(h) string, so the worst case is O(n &middot; h). The comparison itself must look at whole strings, which is exactly the part greedy skipped.",
                ],
                code='''def smallest_from_leaf(root):
    best, path = None, []

    def dfs(node):
        nonlocal best
        if node is None:
            return
        path.append(chr(ord("a") + node.val))
        if node.left is None and node.right is None:
            s = "".join(reversed(path))
            if best is None or s < best:
                best = s
        dfs(node.left)
        dfs(node.right)
        path.pop()

    dfs(root)
    return best''',
            ),
        ],
        tests='''assert smallest_from_leaf(build([0, 1, 2, 3, 4, 3, 4])) == "dba"
assert smallest_from_leaf(build([25, 1, 3, 1, 3, 0, 2])) == "adz"
assert smallest_from_leaf(build([2, 2, 1, None, 1, 0, None, 0])) == "abc"
# greedy follows the smaller child "b" and returns "ba"; the answer is down the other side
assert smallest_from_leaf(build([0, 1, 3, None, None, None, 2, 0, 0])) == "acda"''',
    ),

    dict(
        id="pseudo-palindromic-paths",
        lc=1457, slug="pseudo-palindromic-paths-in-a-binary-tree",
        name="Pseudo-Palindromic Paths in a Binary Tree",
        difficulty="medium",
        framing=[
            "Values are digits 1&ndash;9. A path is pseudo-palindromic if its values can be <em>rearranged</em> into a palindrome. Count such root-to-leaf paths.",
            "A multiset can form a palindrome exactly when at most one value appears an odd number of times. So the only state a path needs is the <em>parity</em> of each digit's count &mdash; nine bits.",
        ],
        approaches=[
            dict(
                name="Parity bitmask",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Bit <code>d</code> of <code>mask</code> is 1 when digit <code>d</code> has appeared an odd number of times. Visiting a node toggles its bit: <code>mask ^ (1 &lt;&lt; val)</code>. Because the mask is passed by value, there is nothing to undo on the way back up.",
                    "At a leaf, \"at most one bit set\" is <code>mask &amp; (mask - 1) == 0</code> &mdash; clearing the lowest set bit leaves zero only if there was at most one.",
                    "Constant work per node: O(n) time, O(h) stack.",
                ],
                code='''def pseudo_palindromic_paths(root):
    def dfs(node, mask):
        if node is None:
            return 0
        mask ^= 1 << node.val
        if node.left is None and node.right is None:
            return 1 if mask & (mask - 1) == 0 else 0
        return dfs(node.left, mask) + dfs(node.right, mask)

    return dfs(root, 0)''',
            ),
            dict(
                name="Counter with backtracking",
                time="O(n &middot; 9)",
                space="O(h)",
                tag="more obvious",
                why=[
                    "Keep a <code>Counter</code> of the path's digits, increment on the way down and decrement on the way up, and at each leaf count how many digits are odd.",
                    "Correct, and the natural first attempt. The leaf check scans up to 9 counts, and the Counter must be restored on the way back &mdash; the bitmask removes both costs and all the bookkeeping.",
                ],
                code='''def pseudo_palindromic_paths(root):
    counts = Counter()

    def dfs(node):
        if node is None:
            return 0
        counts[node.val] += 1
        if node.left is None and node.right is None:
            found = 1 if sum(c % 2 for c in counts.values()) <= 1 else 0
        else:
            found = dfs(node.left) + dfs(node.right)
        counts[node.val] -= 1                      # backtrack
        return found

    return dfs(root)''',
            ),
        ],
        tests='''assert pseudo_palindromic_paths(build([2, 3, 1, 3, 1, None, 1])) == 2
assert pseudo_palindromic_paths(build([2, 1, 1, 1, 3, None, None, None, None, None, 1])) == 1
assert pseudo_palindromic_paths(build([9])) == 1''',
    ),
    ],
),

# ---------------------------------------------------------------- arbitrary paths
dict(
    id="arbitrary-paths",
    title="Any node to any node: what you return vs. what you record",
    idea=[
        "Root-to-leaf paths have one shape. Paths between arbitrary nodes go up and then down, bending at their highest node, and that changes the recursion: what a node returns to its parent must be a path that can still be extended upward, while the answer may be a path that bends here and can never be extended.",
    ],
    problems=[

    dict(
        id="binary-tree-maximum-path-sum",
        lc=124, slug="binary-tree-maximum-path-sum",
        name="Binary Tree Maximum Path Sum",
        difficulty="hard",
        framing=[
            "A path is any sequence of connected nodes, each used once, not necessarily through the root. Return the largest sum of any non-empty path. Values can be negative.",
            "This is Diameter with sums, plus one decision: a subtree whose best arm is negative should be <em>dropped</em>, not added. The key concept is keeping two quantities apart &mdash; the best arm a node offers its parent, and the best bend at the node, which only the global answer can use.",
        ],
        pitfall="Initialising the answer to 0. For <code>[-3]</code> the only path is the single node, and the answer is -3. Start from the root's value or negative infinity.",
        approaches=[
            dict(
                name="Postorder gain with a global best",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "<code>gain(node)</code> returns the best sum of a path that <em>starts at node and goes down one side</em> &mdash; the only kind of path a parent can extend. A child's gain is clamped at 0: if the best arm below is negative, the path simply stops here.",
                    "The best path that bends at this node is <code>node.val + left_gain + right_gain</code>. It goes into the global answer and is never returned, because the parent could not use both arms.",
                    "Every path has exactly one highest node, where it bends, so checking every node's bend checks every path. O(n) time, O(h) stack.",
                ],
                code='''def max_path_sum(root):
    best = float("-inf")

    def gain(node):
        nonlocal best
        if node is None:
            return 0
        left = max(gain(node.left), 0)         # a negative arm is not worth taking
        right = max(gain(node.right), 0)
        best = max(best, node.val + left + right)   # bend here: the answer
        return node.val + max(left, right)          # one arm: for the parent

    gain(root)
    return best''',
            ),
            dict(
                name="Brute force: every node as the bend, recomputed",
                time="O(n&sup2;)",
                space="O(h)",
                tag="for contrast",
                why=[
                    "For each node, compute its best downward arm on each side from scratch, and take the best bend. Each arm computation is O(subtree), so a chain costs O(n&sup2;).",
                    "Worth writing once, because the optimal version is exactly this with the arm computations shared: every node's arm is computed once and handed upward instead of being recomputed by every ancestor.",
                ],
                code='''def max_path_sum(root):
    def arm(node):
        if node is None:
            return 0
        return node.val + max(0, arm(node.left), arm(node.right))

    best = float("-inf")
    stack = [root]
    while stack:
        node = stack.pop()
        bend = node.val + max(0, arm(node.left)) + max(0, arm(node.right))
        best = max(best, bend)
        stack += [c for c in (node.left, node.right) if c is not None]
    return best''',
            ),
        ],
        tests='''assert max_path_sum(build([1, 2, 3])) == 6
assert max_path_sum(build([-10, 9, 20, None, None, 15, 7])) == 42
assert max_path_sum(build([-3])) == -3
assert max_path_sum(build([2, -1])) == 2
assert max_path_sum(build([-2, -1])) == -1
assert max_path_sum(build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])) == 48''',
    ),

    dict(
        id="path-sum-iii",
        lc=437, slug="path-sum-iii",
        name="Path Sum III",
        difficulty="medium",
        framing=[
            "Count paths that sum to the target, where a path must go <em>downward</em> but may start and end at any node. Values can be negative, so you cannot stop early when a sum overshoots.",
            "This is subarray-sum-equals-k on every root-to-node path. The array technique &mdash; prefix sums in a hash map &mdash; carries over directly, with one addition: the map must be <em>backtracked</em> so a sibling subtree never sees your prefixes.",
        ],
        approaches=[
            dict(
                name="Prefix sums with a backtracked counter",
                time="O(n)",
                space="O(h)",
                best=True,
                why=[
                    "Let <code>running</code> be the sum from the root to the current node. A downward path ending here sums to <code>target</code> exactly when some ancestor prefix equals <code>running - target</code>. A counter of the prefixes on the current path answers that in O(1).",
                    "Add this node's prefix before recursing and remove it afterwards. Without the removal, a prefix from the left subtree would be counted as an \"ancestor\" of nodes in the right subtree.",
                    "Seeding the counter with <code>{0: 1}</code> lets paths that start at the root count. O(n) time; the counter holds at most one entry per node on the current path, O(h).",
                ],
                code='''def path_sum_iii(root, target):
    prefixes = Counter({0: 1})

    def dfs(node, running):
        if node is None:
            return 0
        running += node.val
        found = prefixes[running - target]     # paths ending here
        prefixes[running] += 1
        found += dfs(node.left, running) + dfs(node.right, running)
        prefixes[running] -= 1                 # leave the path: backtrack
        return found

    return dfs(root, 0)''',
            ),
            dict(
                name="Start a Path Sum search at every node",
                time="O(n &middot; h)",
                space="O(h)",
                tag="brute force",
                why=[
                    "For each node, count downward paths starting there with a second DFS. Each node is revisited once per ancestor, so the total is O(n &middot; h): O(n log n) balanced, O(n&sup2;) for a chain.",
                    "This is the answer most people give first; the prefix-sum version is what the interviewer is waiting for.",
                ],
                code='''def path_sum_iii(root, target):
    def from_here(node, remaining):
        if node is None:
            return 0
        remaining -= node.val
        return (remaining == 0) + from_here(node.left, remaining) + from_here(node.right, remaining)

    if root is None:
        return 0
    return (from_here(root, target)
            + path_sum_iii(root.left, target)
            + path_sum_iii(root.right, target))''',
            ),
        ],
        tests='''assert path_sum_iii(build([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]), 8) == 3
assert path_sum_iii(build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]), 22) == 3
assert path_sum_iii(build([1]), 0) == 0
assert path_sum_iii(build([0, 0, 0]), 0) == 5
assert path_sum_iii(None, 0) == 0


def _brute(root, t):
    count = 0
    def down(node, s):
        nonlocal count
        if node is None:
            return
        s += node.val
        count += s == t
        down(node.left, s); down(node.right, s)
    for n in all_nodes(root):
        down(n, 0)
    return count

for seed in range(40):
    tree = random_tree(1 + seed % 12, seed, -3, 3)
    assert path_sum_iii(tree, seed % 5 - 2) == _brute(tree, seed % 5 - 2), seed''',
    ),

    dict(
        id="good-leaf-node-pairs",
        lc=1530, slug="number-of-good-leaf-nodes-pairs",
        name="Number of Good Leaf Nodes Pairs",
        difficulty="medium",
        framing=[
            "Count pairs of leaves whose shortest path is at most <code>distance</code> edges (<code>distance &le; 10</code>). The path between two leaves bends at their lowest common ancestor, so each pair should be counted at exactly that node.",
        ],
        approaches=[
            dict(
                name="Return a histogram of leaf depths",
                time="O(n &middot; d&sup2;)",
                space="O(h &middot; d)",
                best=True,
                why=[
                    "Each call returns <code>counts[k]</code> = the number of leaves exactly <code>k</code> edges below this node, for <code>k &le; distance</code>. Leaves farther than that can never be in a good pair, so they are dropped.",
                    "At a node, every pairing of a left leaf at depth <code>a</code> with a right leaf at depth <code>b</code> has path length <code>a + b</code> and bends here. Summing <code>left[a] * right[b]</code> over <code>a + b &le; distance</code> counts each good pair once, at its LCA.",
                    "Each node does O(d&sup2;) work with <code>d = distance</code>, a constant bounded by 10 &mdash; so this is O(n) in practice. The same \"return a summary, pair up the two sides at the bend\" idea solves many any-node-to-any-node counting problems.",
                ],
                code='''def count_pairs(root, distance):
    pairs = 0

    def dfs(node):
        """counts[k] = leaves k edges below node, for k <= distance."""
        nonlocal pairs
        counts = [0] * (distance + 1)
        if node is None:
            return counts
        if node.left is None and node.right is None:
            counts[0] = 1
            return counts
        left, right = dfs(node.left), dfs(node.right)
        for a in range(distance + 1):
            for b in range(distance - a - 1):           # (a + 1) + (b + 1) <= distance
                pairs += left[a] * right[b]
        for k in range(distance):
            counts[k + 1] = left[k] + right[k]          # one edge further up
        return counts

    dfs(root)
    return pairs''',
            ),
            dict(
                name="Build a graph, BFS from every leaf",
                time="O(L &middot; n)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Turn the tree into an undirected graph and BFS out to <code>distance</code> from each leaf, counting other leaves reached; divide by two. Correct, and it previews the next group of problems, but with L leaves it is O(L &middot; n) &mdash; quadratic for a bushy tree.",
                ],
                code='''def count_pairs(root, distance):
    graph, leaves, stack = defaultdict(list), [], [root]
    while stack:
        node = stack.pop()
        kids = [c for c in (node.left, node.right) if c is not None]
        if not kids:
            leaves.append(node)
        for c in kids:
            graph[node].append(c)
            graph[c].append(node)
            stack.append(c)

    leaf_set, found = set(leaves), 0
    for start in leaves:
        seen, frontier = {start}, [start]
        for _ in range(distance):
            nxt = []
            for node in frontier:
                for nb in graph[node]:
                    if nb not in seen:
                        seen.add(nb)
                        nxt.append(nb)
                        found += nb in leaf_set
            frontier = nxt
    return found // 2''',
            ),
        ],
        tests='''assert count_pairs(build([1, 2, 3, None, 4]), 3) == 1
assert count_pairs(build([1, 2, 3, 4, 5, 6, 7]), 3) == 2
assert count_pairs(build([7, 1, 4, 6, None, 5, 3, None, None, None, None, None, 2]), 3) == 1
assert count_pairs(build([1]), 1) == 0
assert count_pairs(build([1, 1, 1]), 2) == 1''',
    ),
    ],
),
]
