"""Write-ups for Trees, part A: traversals, depth, level order, compare and transform."""

_T5 = "build([1, 2, 3, 4, 5])"
_RL = "build([1, None, 2, 3])"
_SHAPE5 = "The tree: 1 has children 2 and 3; 2 has children 4 and 5; 3, 4 and 5 are leaves."
_SHAPE_RL = "The tree: 1 has only a right child 2, and 2 has only a left child 3."
_T3 = "build([3, 9, 20, None, None, 15, 7])"
_SHAPE3 = "The tree: 3 has children 9 and 20; 9 is a leaf; 20 has children 15 and 7."

EXPLAIN = {
    # ------------------------------------------------------------------ preorder
    "preorder-traversal": {
        "examples": [
            {"call": f"preorder({_T5})", "expect": "[1, 2, 4, 5, 3]"},
            {"call": f"preorder({_RL})", "expect": "[1, 2, 3]"},
        ],
        "approaches": {
            "Recursive": {
                "idea": [
                    "Preorder means <strong>root, left, right</strong>: a node is recorded the moment you arrive at it, before either subtree is visited.",
                    "That order is exactly the shape of a recursive function: do the node, then recurse left, then recurse right.",
                    "A <code>None</code> child is the base case and simply returns, so leaves need no special handling.",
                ],
                "steps": [
                    "Create the result list <code>out</code> in the outer function so the helper can append to it.",
                    "Define <code>walk(node)</code>: if <code>node is None</code>, return immediately.",
                    "Otherwise append <code>node.val</code> to <code>out</code> first: this is the \"root\" step.",
                    "Call <code>walk(node.left)</code>, then <code>walk(node.right)</code>.",
                    "Call <code>walk(root)</code> once and return <code>out</code>.",
                ],
                "why": [
                    "Each node is appended before any call on its subtrees starts, and the left call finishes completely before the right one begins, which is the definition of preorder.",
                    "Every node is entered once and does O(1) work, plus one cheap call per missing child, so the time is <strong>O(n)</strong>.",
                    "The call stack holds the path from the root to the current node, so extra space is <strong>O(h)</strong>: O(log n) when balanced, O(n) for a chain (not counting the output list).",
                ],
                "dry": [
                    [
                        _SHAPE5,
                        "walk(1): append 1. Go left: walk(2) appends 2. Go left: walk(4) appends 4.",
                        "walk(4) calls walk(None) twice; both return. Back in walk(2), go right: walk(5) appends 5.",
                        "walk(2) is done, so walk(1) goes right: walk(3) appends 3.",
                        "The result is <strong>[1, 2, 4, 5, 3]</strong>.",
                    ],
                    [
                        _SHAPE_RL,
                        "walk(1): append 1. walk(None) for the missing left child returns at once.",
                        "walk(2): append 2, then walk(3) appends 3 before 2's (missing) right child is tried.",
                        "The result is <strong>[1, 2, 3]</strong>: 2 comes before 3 even though 3 is its left child, because the parent is always first.",
                    ],
                ],
                "faq": [
                    ["Why put <code>out</code> outside <code>walk</code> instead of returning lists?",
                     "Returning <code>[val] + walk(left) + walk(right)</code> also works, but it copies lists at every level and costs O(n·h). Appending to one shared list keeps it O(n)."],
                    ["Can this crash on a deep tree?",
                     "Yes. Python's default recursion limit is about 1000, so a chain of a few thousand nodes raises RecursionError. The iterative and Morris versions avoid that."],
                    ["How do I turn this into inorder or postorder?",
                     "Move the <code>out.append(node.val)</code> line: between the two calls gives inorder, after both gives postorder. Nothing else changes."],
                ],
            },
            "Iterative, one stack": {
                "idea": [
                    "Replace the call stack with your own list: pop a node, record it, then push its children for later.",
                    "A stack is last-in first-out, so push the <em>right</em> child first; the left child then sits on top and is popped next.",
                    "Because a node is recorded the moment it is popped, before its children, the output is preorder.",
                ],
                "steps": [
                    "If <code>root</code> is None, return an empty list.",
                    "Start with <code>out = []</code> and <code>stack = [root]</code>.",
                    "While the stack is non-empty, pop <code>node</code> and append <code>node.val</code>.",
                    "If <code>node.right</code> exists, push it; then if <code>node.left</code> exists, push it.",
                    "When the stack is empty, return <code>out</code>.",
                ],
                "why": [
                    "The left child is pushed last, so the whole left subtree is popped and finished before the right child underneath it comes to the top.",
                    "Each node is pushed once and popped once: <strong>O(n)</strong> time.",
                    "The stack holds the current node's pending right siblings along the path, at most about one per level, so it is <strong>O(h)</strong> space, and it never hits Python's recursion limit.",
                ],
                "dry": [
                    [
                        "stack = [1]. Pop 1, out = [1]; push 3, then 2. stack = [3, 2].",
                        "Pop 2, out = [1, 2]; push 5, then 4. stack = [3, 5, 4].",
                        "Pop 4 (leaf), out = [1, 2, 4]. Pop 5 (leaf), out = [1, 2, 4, 5].",
                        "Pop 3 (leaf), out = [1, 2, 4, 5, 3]. The stack is empty.",
                        "The result is <strong>[1, 2, 4, 5, 3]</strong>.",
                    ],
                    [
                        "stack = [1]. Pop 1, out = [1]; it has only a right child, so push 2.",
                        "Pop 2, out = [1, 2]; it has only a left child, so push 3.",
                        "Pop 3, out = [1, 2, 3]; no children. The stack is empty.",
                        "The result is <strong>[1, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["What happens if I push left before right?",
                     "The right child is popped first, so you get root, right, left. Reversing that order is actually the trick behind one of the postorder approaches."],
                    ["Why the early return for an empty tree?",
                     "Without it the stack would start as <code>[None]</code> and <code>node.val</code> would raise AttributeError on the first pop."],
                    ["Is the stack really O(h)?",
                     "Yes. Each pop of a node on the path leaves at most one pending right child on the stack, so there are at most about h pending entries plus the current path."],
                ],
            },
            "Morris traversal": {
                "idea": [
                    "To use O(1) extra space, store the \"way back up\" inside the tree itself instead of on a stack.",
                    "Before going down into a left subtree, find its rightmost node (the <em>predecessor</em> <code>pred</code>) and point <code>pred.right</code> back at the current node: a temporary <strong>thread</strong>.",
                    "Reaching a node a second time through its thread means its left side is finished: remove the thread and go right. For preorder, a node is recorded on the <em>first</em> arrival.",
                ],
                "steps": [
                    "Start with <code>node = root</code> and loop while <code>node</code> is not None.",
                    "If <code>node.left</code> is None: append <code>node.val</code> and move to <code>node.right</code> (which may be a thread).",
                    "Otherwise walk <code>pred</code> from <code>node.left</code> rightwards until <code>pred.right</code> is None or is <code>node</code>.",
                    "If <code>pred.right</code> is None (first visit): append <code>node.val</code>, set <code>pred.right = node</code>, and move to <code>node.left</code>.",
                    "If <code>pred.right is node</code> (second visit): set <code>pred.right = None</code> to restore the tree and move to <code>node.right</code>.",
                ],
                "why": [
                    "The thread from a left subtree's last node back to its parent is exactly where a stack would have returned to, so every node is reached and the left side always finishes before the right side.",
                    "Each thread is created once and removed once, and each predecessor walk only covers right edges of one left subtree; every edge is walked a constant number of times, so time is <strong>O(n)</strong>.",
                    "Only <code>node</code> and <code>pred</code> are stored, so extra space is <strong>O(1)</strong>. The tree is modified while running but is fully restored when the loop ends.",
                ],
                "dry": [
                    [
                        "node = 1: pred walks 2 → 5; 5.right is None, so append 1, thread 5.right = 1, go to 2.",
                        "node = 2: pred = 4; append 2, thread 4.right = 2, go to 4.",
                        "node = 4 has no left: append 4, follow 4.right to 2. Now pred = 4 and 4.right is 2, so unthread and go to 5.",
                        "node = 5 has no left: append 5, follow the thread to 1. pred walks 2 → 5 and finds 5.right is 1: unthread, go to 3.",
                        "node = 3 has no left: append 3, go to None. The result is <strong>[1, 2, 4, 5, 3]</strong>.",
                    ],
                    [
                        "node = 1 has no left: append 1, go to 2.",
                        "node = 2: pred = 3; 3.right is None, so append 2, thread 3.right = 2, go to 3.",
                        "node = 3 has no left: append 3, follow the thread back to 2.",
                        "node = 2 again: pred = 3 and 3.right is 2, so unthread and go to 2.right = None.",
                        "The result is <strong>[1, 2, 3]</strong>, and 3.right is None again.",
                    ],
                ],
                "faq": [
                    ["Why does the predecessor loop also stop at <code>pred.right is node</code>?",
                     "On the second visit the rightmost node's right pointer is the thread back to <code>node</code>. Without that check the loop would follow the thread and spin forever."],
                    ["What is the only difference from Morris inorder?",
                     "Where the value is appended. Preorder appends when the thread is created (first arrival); inorder appends when the thread is removed (return from the left)."],
                    ["Is it safe if the traversal is interrupted?",
                     "No. If you break out midway, some threads are still in place and the tree contains cycles. Only use it when the loop runs to the end or when nobody else reads the tree concurrently."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ inorder
    "inorder-traversal": {
        "examples": [
            {"call": f"inorder({_T5})", "expect": "[4, 2, 5, 1, 3]"},
            {"call": f"inorder({_RL})", "expect": "[1, 3, 2]"},
        ],
        "approaches": {
            "Recursive": {
                "idea": [
                    "Inorder means <strong>left, root, right</strong>: a node is recorded after its whole left subtree and before its right subtree.",
                    "On a binary search tree this visits values in sorted order, which is why inorder is the traversal most BST problems build on.",
                    "Recursion expresses it directly: recurse left, record, recurse right.",
                ],
                "steps": [
                    "Create <code>out</code> in the outer function.",
                    "Define <code>walk(node)</code>: if <code>node is None</code>, return.",
                    "Call <code>walk(node.left)</code> first.",
                    "Append <code>node.val</code>, then call <code>walk(node.right)</code>.",
                    "Call <code>walk(root)</code> and return <code>out</code>.",
                ],
                "why": [
                    "When <code>node.val</code> is appended, the left call has already returned, so every node of the left subtree is before it and none of the right subtree is.",
                    "Each node is visited once with O(1) work: <strong>O(n)</strong> time.",
                    "The recursion depth is the height of the tree, so extra space is <strong>O(h)</strong>.",
                ],
                "dry": [
                    [
                        _SHAPE5,
                        "walk(1) → walk(2) → walk(4) → walk(None) returns. Append 4.",
                        "Back in walk(2): append 2, then walk(5) appends 5.",
                        "Back in walk(1): append 1, then walk(3) appends 3.",
                        "The result is <strong>[4, 2, 5, 1, 3]</strong>.",
                    ],
                    [
                        _SHAPE_RL,
                        "walk(1): its left is None, so append 1 straight away.",
                        "walk(2): go left first, walk(3) appends 3. Then append 2.",
                        "2 has no right child, and the walk ends.",
                        "The result is <strong>[1, 3, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is inorder of a BST sorted?",
                     "Everything in a node's left subtree is smaller and everything in its right subtree is larger, and inorder places the node exactly between those two groups at every level."],
                    ["Does the result depend on how the tree was built?",
                     "Only on its shape and values. Two different shapes can give the same inorder list, which is why rebuilding a tree needs inorder plus preorder or postorder."],
                    ["What is the space without counting <code>out</code>?",
                     "Just the call stack, O(h). For a chain that is O(n), and Python's recursion limit becomes the real constraint."],
                ],
            },
            "Iterative, one stack": {
                "idea": [
                    "The recursion first dives left as far as it can, remembering every node on the way. An explicit stack can remember that path.",
                    "When the dive hits None, the top of the stack is the leftmost unvisited node: record it, then do the same thing starting from its right child.",
                    "The pattern \"push all the way left, pop one, step right\" is the standard iterative inorder.",
                ],
                "steps": [
                    "Start with <code>out = []</code>, <code>stack = []</code>, <code>node = root</code>.",
                    "Loop while the stack is non-empty or <code>node</code> is not None.",
                    "Inner loop: while <code>node</code> is not None, push it and move to <code>node.left</code>.",
                    "Pop the top into <code>node</code> and append <code>node.val</code>: its left side is fully done.",
                    "Set <code>node = node.right</code> so the next round dives into the right subtree (or pops the next ancestor if it is None).",
                ],
                "why": [
                    "A node is popped only after the inner loop has pushed and then popped everything to its left, so it is recorded after its left subtree and before its right one.",
                    "Each node is pushed once and popped once: <strong>O(n)</strong> time.",
                    "The stack holds the chain of ancestors whose left side is still in progress, at most the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "Dive from 1: push 1, 2, 4. stack = [1, 2, 4], node = None.",
                        "Pop 4, out = [4]; node = 4.right = None. Pop 2, out = [4, 2]; node = 5.",
                        "Dive from 5: push 5. Pop 5, out = [4, 2, 5]; node = None.",
                        "Pop 1, out = [4, 2, 5, 1]; node = 3. Push 3, pop 3, out = [4, 2, 5, 1, 3].",
                        "The stack is empty and node is None. The result is <strong>[4, 2, 5, 1, 3]</strong>.",
                    ],
                    [
                        "Dive from 1: push 1; 1.left is None. Pop 1, out = [1]; node = 2.",
                        "Dive from 2: push 2, push 3. stack = [2, 3].",
                        "Pop 3, out = [1, 3]; node = None. Pop 2, out = [1, 3, 2]; node = None.",
                        "Both the stack and node are empty, so the loop stops.",
                        "The result is <strong>[1, 3, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the outer loop test <code>stack or node is not None</code>?",
                     "After popping the root of a left part, the stack can be empty while <code>node</code> points at a right subtree still to visit. Testing only the stack would stop too early."],
                    ["Why not pre-push children like the preorder version?",
                     "Here a node cannot be recorded when first reached; it must wait until its left side is done. Keeping it on the stack during the dive is how it waits."],
                    ["How would I get the k-th smallest of a BST from this?",
                     "Count pops and stop at the k-th. Because the stack version can stop early, it does only O(h + k) work."],
                ],
            },
            "Morris traversal": {
                "idea": [
                    "Same threading trick as Morris preorder: link each left subtree's rightmost node back to its parent so you can climb up without a stack.",
                    "The difference is when a node is recorded: on the <em>second</em> arrival, when its thread is found and removed, because by then its left subtree is finished.",
                    "Nodes without a left child are recorded immediately, since there is nothing to their left.",
                ],
                "steps": [
                    "Start at <code>node = root</code>; loop while it is not None.",
                    "If <code>node.left</code> is None: append <code>node.val</code> and go to <code>node.right</code>.",
                    "Otherwise find <code>pred</code>, the rightmost node of the left subtree (stopping if <code>pred.right</code> is already <code>node</code>).",
                    "If <code>pred.right</code> is None: create the thread <code>pred.right = node</code> and go left, without recording.",
                    "If it is the thread: remove it, append <code>node.val</code>, and go to <code>node.right</code>.",
                ],
                "why": [
                    "A node with a left child is appended only when we come back up its thread, which happens right after its predecessor (the last node of its left subtree) is appended: exactly inorder.",
                    "Every thread is created once and removed once, and the predecessor searches together touch each edge a constant number of times: <strong>O(n)</strong> time.",
                    "No stack and no recursion, just two pointers: <strong>O(1)</strong> extra space. All threads are removed by the end, so the tree is unchanged.",
                ],
                "dry": [
                    [
                        "node = 1: pred = 5 (via 2). Thread 5.right = 1 and go to 2. node = 2: pred = 4. Thread 4.right = 2 and go to 4.",
                        "node = 4 has no left: append 4, follow the thread to 2.",
                        "node = 2: pred = 4 has the thread, so remove it, append 2, go to 5.",
                        "node = 5 has no left: append 5, follow the thread to 1. At 1, pred = 5 has the thread: remove it, append 1, go to 3.",
                        "node = 3: append 3, go to None. The result is <strong>[4, 2, 5, 1, 3]</strong>.",
                    ],
                    [
                        "node = 1 has no left: append 1, go to 2.",
                        "node = 2: pred = 3, thread 3.right = 2, go to 3 without recording 2.",
                        "node = 3 has no left: append 3, follow the thread to 2.",
                        "node = 2: the thread is found, so remove it, append 2, go to None.",
                        "The result is <strong>[1, 3, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the time O(n) when there is a nested loop?",
                     "Each predecessor search walks the right spine of one left subtree, and every edge belongs to at most one such spine. Each spine is walked twice (to create and to remove the thread), so the total is linear."],
                    ["When is Morris worth it?",
                     "When O(1) extra space is an explicit requirement, for example the follow-up \"can you do it without a stack?\". Otherwise the stack version is easier to get right."],
                    ["Does it work with duplicate values?",
                     "Yes. It compares nodes by identity (<code>pred.right is node</code>), never by value, so duplicates are irrelevant."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ postorder
    "postorder-traversal": {
        "examples": [
            {"call": f"postorder({_T5})", "expect": "[4, 5, 2, 3, 1]"},
            {"call": f"postorder({_RL})", "expect": "[3, 2, 1]"},
        ],
        "approaches": {
            "Recursive": {
                "idea": [
                    "Postorder means <strong>left, right, root</strong>: a node is recorded only after both of its subtrees are completely done.",
                    "This is the order you need whenever a node's answer depends on its children's answers, such as heights or deleting a tree.",
                    "Recursively it is two calls followed by the append.",
                ],
                "steps": [
                    "Create <code>out</code> in the outer function.",
                    "Define <code>walk(node)</code>: if <code>node is None</code>, return.",
                    "Call <code>walk(node.left)</code>, then <code>walk(node.right)</code>.",
                    "Only then append <code>node.val</code>.",
                    "Call <code>walk(root)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Both recursive calls return before the append, so every descendant of a node appears before it in <code>out</code>.",
                    "Each node does O(1) work once: <strong>O(n)</strong> time.",
                    "The call stack is as deep as the tree: <strong>O(h)</strong> extra space.",
                ],
                "dry": [
                    [
                        _SHAPE5,
                        "walk(1) → walk(2) → walk(4): both children None, append 4.",
                        "walk(2) → walk(5): append 5. Both sides of 2 are done, append 2.",
                        "walk(1) → walk(3): append 3. Both sides of 1 are done, append 1.",
                        "The result is <strong>[4, 5, 2, 3, 1]</strong>.",
                    ],
                    [
                        _SHAPE_RL,
                        "walk(1): left is None. Go right to walk(2).",
                        "walk(2) → walk(3): append 3. 2's right is None, so append 2.",
                        "Back in walk(1): append 1 last.",
                        "The result is <strong>[3, 2, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is postorder the reverse of preorder?",
                     "No. Reversed preorder is root-left-right backwards, which is right-left-root. Postorder is left-right-root; you get it by reversing a <em>right-first</em> preorder."],
                    ["Why is the root always last?",
                     "The root is an ancestor of every other node, and postorder puts each node after all its descendants."],
                    ["What real problems use this order?",
                     "Anything computed bottom-up: height, diameter, subtree sums, balanced checks, and freeing or deleting nodes safely."],
                ],
            },
            "Reversed modified preorder": {
                "idea": [
                    "A preorder that visits the <em>right</em> child before the left produces root, right, left.",
                    "Reversing that whole list gives left, right, root, which is exactly postorder.",
                    "So the easy one-stack preorder, with the push order swapped and one <code>reverse()</code> at the end, solves a problem whose direct iterative form is fiddly.",
                ],
                "steps": [
                    "If <code>root</code> is None, return an empty list.",
                    "Start with <code>stack = [root]</code>; while it is non-empty, pop <code>node</code> and append <code>node.val</code>.",
                    "Push <code>node.left</code> first, then <code>node.right</code>, so the right child is popped first.",
                    "After the loop <code>out</code> is in root-right-left order.",
                    "Call <code>out.reverse()</code> and return it.",
                ],
                "why": [
                    "The loop is a correct preorder of the mirrored tree (right before left), and reversing a root-right-left sequence turns every \"node before its subtrees\" into \"node after its subtrees\", with left before right.",
                    "Every node is pushed and popped once, and the reverse is one O(n) pass: <strong>O(n)</strong> time.",
                    "The stack is <strong>O(h)</strong>, but the output must be fully built before it can be reversed, so you cannot stream nodes in postorder as you go.",
                ],
                "dry": [
                    [
                        "Pop 1, out = [1]; push 2, then 3. stack = [2, 3].",
                        "Pop 3, out = [1, 3]. Pop 2, out = [1, 3, 2]; push 4, then 5.",
                        "Pop 5, out = [1, 3, 2, 5]. Pop 4, out = [1, 3, 2, 5, 4].",
                        "Reverse: [4, 5, 2, 3, 1].",
                        "The result is <strong>[4, 5, 2, 3, 1]</strong>.",
                    ],
                    [
                        "Pop 1, out = [1]; only a right child, push 2.",
                        "Pop 2, out = [1, 2]; only a left child, push 3.",
                        "Pop 3, out = [1, 2, 3]. The stack is empty.",
                        "Reverse: <strong>[3, 2, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why push the left child first here?",
                     "So the right child is on top and is popped first, giving root-right-left. After the reverse that becomes left-right-root."],
                    ["Is this a \"real\" postorder traversal?",
                     "It produces the right list, but nodes are not processed in postorder while running. If you need to act on a node only after its children (e.g. to combine their results), use the true one-stack version."],
                    ["Could I insert at the front instead of reversing?",
                     "Yes, with a deque and <code>appendleft</code>. Using <code>list.insert(0, x)</code> would make it O(n²) because each insert shifts the list."],
                ],
            },
            "One stack, true postorder": {
                "idea": [
                    "Dive left like iterative inorder, but do not record a node when its left side is done: it still has to wait for its right side.",
                    "Look at the stack top (<code>peek</code>). If it has a right subtree that has not been finished, go and do that subtree first.",
                    "<code>last</code> remembers the most recently recorded node; if <code>peek.right is last</code>, the right subtree has just finished and <code>peek</code> can be recorded.",
                ],
                "steps": [
                    "Start with <code>out = []</code>, <code>stack = []</code>, <code>last = None</code>, <code>node = root</code>.",
                    "While the stack or <code>node</code> is non-empty: push <code>node</code> and its left chain onto the stack.",
                    "Set <code>peek = stack[-1]</code> without popping.",
                    "If <code>peek.right</code> exists and is not <code>last</code>, set <code>node = peek.right</code> to process that subtree next.",
                    "Otherwise append <code>peek.val</code> and set <code>last = stack.pop()</code>; <code>node</code> stays None so the next round peeks again.",
                ],
                "why": [
                    "A node is popped only when it has no right child or its right child was the last node recorded; since a subtree's root is recorded last in postorder, that means the whole right subtree is done.",
                    "Each node is pushed once and popped once, and each peek either pops or moves to a new subtree: <strong>O(n)</strong> time.",
                    "The stack holds only the current root-to-node path: <strong>O(h)</strong> space. Unlike the reversal trick, nodes are emitted in true postorder as the loop runs.",
                ],
                "dry": [
                    [
                        "Dive: push 1, 2, 4. peek = 4, no right: append 4, last = 4.",
                        "peek = 2: right is 5 and 5 is not last, so node = 5. Push 5; peek = 5, no right: append 5, last = 5.",
                        "peek = 2: right is 5 = last, so append 2, last = 2.",
                        "peek = 1: right is 3, not last, so push 3; append 3, last = 3. peek = 1: right is last, append 1.",
                        "The result is <strong>[4, 5, 2, 3, 1]</strong>.",
                    ],
                    [
                        "Dive: push 1 (no left). peek = 1: right is 2, not last (None), so node = 2.",
                        "Dive: push 2, 3. peek = 3, no right: append 3, last = 3.",
                        "peek = 2: no right child, so append 2, last = 2.",
                        "peek = 1: right is 2 = last, so append 1. Stack empty.",
                        "The result is <strong>[3, 2, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why compare with <code>last</code> instead of keeping a visited set?",
                     "In postorder the right child is always the last node recorded before its parent is ready. One pointer gives the same information as a set, in O(1) space."],
                    ["Why use <code>is</code> and not <code>==</code>?",
                     "Two different nodes can have the same value. <code>is</code> checks it is the very same node object."],
                    ["What goes wrong without the <code>peek.right is not last</code> check?",
                     "After finishing the right subtree you would peek at the parent, see a right child again and go back into it forever."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum depth
    "maximum-depth": {
        "examples": [
            {"call": f"max_depth({_T3})", "expect": "3"},
            {"call": "max_depth(build([1, 2, None, 3]))", "expect": "3"},
        ],
        "approaches": {
            "Recursive postorder": {
                "idea": [
                    "The depth of a tree is one (for the root) plus the depth of its deeper subtree.",
                    "An empty tree has depth 0, which is the base case that makes a leaf come out as 1.",
                    "Each node needs both children's answers first, so this is a postorder computation.",
                ],
                "steps": [
                    "If <code>root</code> is None, return 0.",
                    "Recursively compute <code>max_depth(root.left)</code>.",
                    "Recursively compute <code>max_depth(root.right)</code>.",
                    "Return <code>1 + max(left, right)</code>.",
                ],
                "why": [
                    "The longest root-to-leaf path goes through the root and then continues entirely in one subtree, so it is 1 plus the longer of the two sub-answers. Induction on height gives correctness.",
                    "Each node makes two calls and does O(1) work: <strong>O(n)</strong> time.",
                    "The recursion depth equals the tree's height: <strong>O(h)</strong> space, O(n) for a chain.",
                ],
                "dry": [
                    [
                        _SHAPE3,
                        "max_depth(9): both children None, so 1 + max(0, 0) = 1.",
                        "max_depth(15) = 1 and max_depth(7) = 1, so max_depth(20) = 1 + max(1, 1) = 2.",
                        "max_depth(3) = 1 + max(1, 2) = 3.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "The tree is a left chain 1 → 2 → 3.",
                        "max_depth(3) = 1 + max(0, 0) = 1.",
                        "max_depth(2) = 1 + max(1, 0) = 2.",
                        "max_depth(1) = 1 + max(2, 0) = 3. The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Is depth counted in nodes or edges?",
                     "In nodes here, as LeetCode defines it: a single node has depth 1. Diameter problems count edges, so watch the definition."],
                    ["Why return 0 for None rather than -1?",
                     "With 0, a leaf gets 1 + max(0, 0) = 1, which is the node count. Returning -1 would measure edges instead."],
                    ["What about a very deep tree?",
                     "A chain of over about 1000 nodes hits Python's recursion limit. The BFS or iterative DFS versions handle that."],
                ],
            },
            "BFS, counting levels": {
                "idea": [
                    "Breadth-first search processes the tree one level at a time, so the number of levels processed is the depth.",
                    "The key is to finish exactly one level per outer-loop round: take a snapshot of the queue length and pop exactly that many nodes.",
                    "Children appended during that round belong to the next level and wait for the next round.",
                ],
                "steps": [
                    "If <code>root</code> is None, return 0.",
                    "Start with <code>depth = 0</code> and <code>queue = deque([root])</code>.",
                    "While the queue is non-empty, add 1 to <code>depth</code>.",
                    "Loop <code>len(queue)</code> times: pop from the left and append any existing children.",
                    "When the queue empties, return <code>depth</code>.",
                ],
                "why": [
                    "At the start of each round the queue holds exactly one whole level, so every round adds one level and the rounds stop after the deepest one.",
                    "Each node is enqueued and dequeued once: <strong>O(n)</strong> time.",
                    "The queue holds at most one level plus part of the next, so space is <strong>O(w)</strong>, the maximum width; that can be about n/2 for a full tree.",
                ],
                "dry": [
                    [
                        "queue = [3]. Round 1: depth = 1; pop 3, push 9 and 20.",
                        "Round 2: depth = 2; snapshot size 2. Pop 9 (no children), pop 20 and push 15, 7.",
                        "Round 3: depth = 3; pop 15 and 7, no children.",
                        "The queue is empty. The result is <strong>3</strong>.",
                    ],
                    [
                        "queue = [1]. Round 1: depth = 1; pop 1, push 2.",
                        "Round 2: depth = 2; pop 2, push 3.",
                        "Round 3: depth = 3; pop 3, nothing to push.",
                        "The queue never holds more than one node on a chain. The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>for _ in range(len(queue))</code> and not <code>while queue</code> inside?",
                     "<code>range(len(queue))</code> is evaluated once, so it counts only the current level. A <code>while queue</code> would keep going into the children just appended and merge all levels into one round."],
                    ["Why a deque and not a list?",
                     "<code>list.pop(0)</code> shifts every element and is O(n), making the whole BFS O(n²) on wide trees. <code>deque.popleft()</code> is O(1)."],
                    ["When is BFS better than recursion here?",
                     "On deep, narrow trees: BFS uses O(width) memory and no recursion. On wide, shallow trees the recursive version uses less memory."],
                ],
            },
            "Iterative DFS with explicit depth": {
                "idea": [
                    "Do a depth-first walk with your own stack, but store each node together with its depth: <code>(node, depth)</code>.",
                    "The answer is just the largest depth ever popped, kept in <code>best</code>.",
                    "Children get <code>depth + 1</code>, so no node ever needs to look at its parent.",
                ],
                "steps": [
                    "If <code>root</code> is None, return 0.",
                    "Start with <code>best = 0</code> and <code>stack = [(root, 1)]</code>.",
                    "Pop <code>(node, depth)</code>; if <code>depth &gt; best</code>, update <code>best</code>.",
                    "Push each existing child as <code>(child, depth + 1)</code>.",
                    "When the stack is empty, return <code>best</code>.",
                ],
                "why": [
                    "Each stored depth is exactly the number of nodes from the root to that node, and every node is popped once, so <code>best</code> ends as the maximum over all nodes, which is the tree's depth.",
                    "Each node is pushed and popped once: <strong>O(n)</strong> time.",
                    "The stack holds the current path plus pending siblings, <strong>O(h)</strong> space, without using Python's call stack.",
                ],
                "dry": [
                    [
                        "stack = [(3, 1)]. Pop it: best = 1; push (9, 2), (20, 2).",
                        "Pop (20, 2): best = 2; push (15, 3), (7, 3).",
                        "Pop (7, 3): best = 3. Pop (15, 3): no change.",
                        "Pop (9, 2): no change. The stack is empty.",
                        "The result is <strong>3</strong>.",
                    ],
                    [
                        "stack = [(1, 1)]. Pop: best = 1; push (2, 2).",
                        "Pop (2, 2): best = 2; push (3, 3).",
                        "Pop (3, 3): best = 3. Nothing more to push.",
                        "The result is <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Does the order in which children are pushed matter?",
                     "No. Every node is visited once whatever the order, and the maximum does not depend on visiting order."],
                    ["Why not just count pushes and pops like BFS levels?",
                     "A DFS stack mixes nodes from different levels, so there is no level boundary to count. Carrying the depth with each node solves that."],
                    ["Could I only update <code>best</code> at leaves?",
                     "Yes, the deepest node is always a leaf, but checking every node is simpler and costs the same O(n)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ minimum depth
    "minimum-depth": {
        "examples": [
            {"call": f"min_depth({_T3})", "expect": "2"},
            {"call": "min_depth(build([1, 2]))", "expect": "2"},
        ],
        "approaches": {
            "Recursive, with the one-child case": {
                "idea": [
                    "Minimum depth is the number of nodes on the shortest path from the root down to a <strong>leaf</strong>.",
                    "Mirroring max depth with <code>1 + min(left, right)</code> is wrong: a missing child returns 0, and a missing child is not a leaf.",
                    "When a node has only one child, the path must go through that child; only when both exist do you take the minimum.",
                ],
                "steps": [
                    "If <code>root</code> is None, return 0.",
                    "Compute <code>left</code> and <code>right</code> recursively.",
                    "If either child is None, return <code>1 + left + right</code>: one of the two is 0, so this is 1 plus the real child's answer (or 1 for a leaf).",
                    "Otherwise both children exist: return <code>1 + min(left, right)</code>.",
                ],
                "why": [
                    "For a leaf both sides are 0 and the answer is 1. For a one-child node the only leaves are in the existing subtree. For a two-child node the nearest leaf is in whichever subtree has the smaller answer.",
                    "The <code>left + right</code> trick works because exactly one term is non-zero (or both are zero for a leaf).",
                    "Every node is visited once: <strong>O(n)</strong> time and <strong>O(h)</strong> recursion space. It cannot stop early at a shallow leaf, which BFS can.",
                ],
                "dry": [
                    [
                        _SHAPE3,
                        "min_depth(9): both children None, so 1 + 0 + 0 = 1.",
                        "min_depth(15) = min_depth(7) = 1. Node 20 has both children: 1 + min(1, 1) = 2.",
                        "Node 3 has both children: 1 + min(1, 2) = 2.",
                        "The result is <strong>2</strong> (the path 3 → 9).",
                    ],
                    [
                        "The tree: 1 with only a left child 2.",
                        "min_depth(2) = 1 (a leaf). min_depth(None) = 0.",
                        "Node 1 has a missing right child, so it returns 1 + 1 + 0 = 2.",
                        "A plain <code>1 + min(1, 0)</code> would have said 1, treating the root as a leaf. The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["What exactly breaks with <code>1 + min(left, right)</code>?",
                     "On build([1, 2]) it returns 1, because the missing right child gives 0. But 1 is not a leaf, so the right answer is 2."],
                    ["Why <code>1 + left + right</code> instead of an if/else per side?",
                     "It is a compact way to say \"1 plus whichever side exists\". An explicit <code>if root.left is None: return 1 + right</code> is equivalent and maybe clearer."],
                    ["Is recursion a good choice here?",
                     "It is correct, but it always visits the whole tree. If a leaf is near the top of a huge tree, BFS finds it after touching only the top levels."],
                ],
            },
            "BFS with early exit": {
                "idea": [
                    "BFS visits nodes in order of depth, so the <strong>first leaf</strong> it dequeues is a shallowest leaf.",
                    "At that moment the current level number is the answer, and nothing deeper ever needs to be looked at.",
                    "This also avoids the one-child trap naturally: a node with one child is simply not a leaf, so BFS keeps going.",
                ],
                "steps": [
                    "If <code>root</code> is None, return 0.",
                    "Start with <code>depth = 1</code> and <code>queue = deque([root])</code>.",
                    "Process one level at a time using a <code>len(queue)</code> snapshot.",
                    "For each popped node: if it has no children, return <code>depth</code> immediately; otherwise enqueue its existing children.",
                    "After the level, add 1 to <code>depth</code>.",
                ],
                "why": [
                    "All nodes at depth d are dequeued before any node at depth d + 1, so the first leaf found has the minimum depth.",
                    "In the worst case (the only leaves are at the bottom) every node is processed: <strong>O(n)</strong> time; with a shallow leaf it stops far sooner.",
                    "The queue holds up to one level: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "depth = 1, queue = [3]. Pop 3: not a leaf, push 9 and 20. depth = 2.",
                        "Level 2: pop 9. It has no children, so it is a leaf.",
                        "Return immediately; 20, 15 and 7 are never expanded.",
                        "The result is <strong>2</strong>.",
                    ],
                    [
                        "depth = 1, queue = [1]. Pop 1: it has a left child, so it is not a leaf. Push 2. depth = 2.",
                        "Level 2: pop 2. No children: a leaf.",
                        "Return depth.",
                        "The result is <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the final <code>return depth</code> after the loop ever reached?",
                     "It is not, for a non-empty tree: every tree has at least one leaf, so the inner return always fires. The line just keeps the function total."],
                    ["Could I check for a leaf when enqueuing instead of dequeuing?",
                     "Yes, and you would return <code>depth + 1</code> then. Checking on dequeue keeps the depth bookkeeping simpler."],
                    ["Why is this listed as O(n) worst case?",
                     "A tree whose only leaves are all on the last level (a full tree, or a chain) forces BFS to look at every node before it finds one."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ level order
    "level-order-traversal": {
        "examples": [
            {"call": f"level_order_lists({_T3})", "expect": "[[3], [9, 20], [15, 7]]"},
            {"call": "level_order_lists(build([1, 2, 3, None, 4]))", "expect": "[[1], [2, 3], [4]]"},
        ],
        "approaches": {
            "BFS with a size snapshot": {
                "idea": [
                    "A FIFO queue visits nodes in level order: the root, then all of depth 1 left to right, then depth 2, and so on.",
                    "To group them, process the queue in rounds. At the start of a round the queue holds exactly one level, so record <code>len(queue)</code> and pop that many.",
                    "Each round collects one list; children pushed during it form the next round.",
                ],
                "steps": [
                    "If <code>root</code> is None, return <code>[]</code>.",
                    "Start with <code>out = []</code> and <code>queue = deque([root])</code>.",
                    "While the queue is non-empty, create an empty <code>level</code>.",
                    "Loop <code>len(queue)</code> times: pop a node, append its value to <code>level</code>, enqueue its left then right child if present.",
                    "Append <code>level</code> to <code>out</code>; return <code>out</code> when the queue is empty.",
                ],
                "why": [
                    "By induction, the queue at the start of each round holds exactly the nodes of one depth in left-to-right order, because they were enqueued by the previous level's nodes in left-to-right order, each left child before its right.",
                    "Every node is enqueued and dequeued once: <strong>O(n)</strong> time.",
                    "The queue holds at most one level plus part of the next: <strong>O(w)</strong> space besides the output.",
                ],
                "dry": [
                    [
                        "queue = [3]. Round 1: pop 3, level = [3]; push 9, 20. out = [[3]].",
                        "Round 2 (size 2): pop 9 (no children), pop 20 (push 15, 7). level = [9, 20].",
                        "Round 3 (size 2): pop 15, pop 7. level = [15, 7].",
                        "The queue is empty. The result is <strong>[[3], [9, 20], [15, 7]]</strong>.",
                    ],
                    [
                        "The tree: 1 has children 2 and 3; 2 has only a right child 4.",
                        "Round 1: level = [1]; push 2, 3.",
                        "Round 2: pop 2 (push 4), pop 3. level = [2, 3].",
                        "Round 3: pop 4. level = [4]. The result is <strong>[[1], [2, 3], [4]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why snapshot the size before the inner loop?",
                     "The queue grows while you pop, because children are added at the back. <code>range(len(queue))</code> is evaluated once, so it covers only the nodes that were there at the start of the level."],
                    ["Could I put (node, depth) pairs in the queue instead?",
                     "Yes, and start a new list whenever the depth changes. The snapshot avoids storing a depth per node."],
                    ["Is the space really O(w) and not O(n)?",
                     "The queue is O(w), but the output stores all n values. The bound usually quoted is the extra space beyond the answer."],
                ],
            },
            "DFS carrying the depth": {
                "idea": [
                    "Level order does not actually require BFS. Any traversal works as long as each value is appended to the list for its depth.",
                    "A preorder DFS visits left before right, so within a given depth the values still arrive left to right.",
                    "The first time a depth is reached, <code>depth == len(out)</code>, and a new empty list is added for it.",
                ],
                "steps": [
                    "Start with <code>out = []</code>.",
                    "Define <code>walk(node, depth)</code>: if <code>node</code> is None, return.",
                    "If <code>depth == len(out)</code>, append a new empty list: this is the first node at this depth.",
                    "Append <code>node.val</code> to <code>out[depth]</code>.",
                    "Recurse into <code>node.left</code> then <code>node.right</code> with <code>depth + 1</code>; call <code>walk(root, 0)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Preorder reaches depth d for the first time before any deeper node at that depth, so <code>len(out)</code> always equals the next new depth. Within a depth, left-before-right recursion gives left-to-right order.",
                    "Each node is visited once: <strong>O(n)</strong> time.",
                    "The recursion uses <strong>O(h)</strong> stack space, better than BFS on wide, shallow trees.",
                ],
                "dry": [
                    [
                        "walk(3, 0): len(out) = 0, add a list. out = [[3]].",
                        "walk(9, 1): new depth, out = [[3], [9]]. Its children are None.",
                        "walk(20, 1): depth 1 exists, out[1] = [9, 20].",
                        "walk(15, 2): new depth, out[2] = [15]. walk(7, 2): out[2] = [15, 7].",
                        "The result is <strong>[[3], [9, 20], [15, 7]]</strong>.",
                    ],
                    [
                        "walk(1, 0): out = [[1]]. walk(2, 1): out = [[1], [2]].",
                        "walk(2.left = None, 2) returns. walk(4, 2): new depth, out = [[1], [2], [4]].",
                        "Only now is walk(3, 1) called: out[1] = [2, 3]. Depth 2 was filled before depth 1 was finished.",
                        "The lists are still right because each value goes to its own depth. The result is <strong>[[1], [2, 3], [4]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>depth == len(out)</code> and not <code>depth &gt;= len(out)</code>?",
                     "Preorder never skips a depth: to reach depth d you pass through depth d − 1. So <code>depth</code> is at most <code>len(out)</code>, and equality is the only case that needs a new list."],
                    ["What if I recursed right before left?",
                     "Each level would come out right to left. That variant is the basis of the right-side-view trick."],
                    ["Why might an interviewer still prefer BFS?",
                     "BFS emits whole levels in order and can stop after any level, which matters for problems like \"first level with property X\". DFS only finishes every level at the very end."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ level order II
    "level-order-bottom-up": {
        "examples": [
            {"call": f"level_order_bottom({_T3})", "expect": "[[15, 7], [9, 20], [3]]"},
            {"call": "level_order_bottom(build([1, 2, 3, 4]))", "expect": "[[4], [2, 3], [1]]"},
        ],
        "approaches": {
            "BFS, then reverse once": {
                "idea": [
                    "Bottom-up level order is ordinary level order with the list of levels reversed. Values inside each level stay left to right.",
                    "BFS cannot easily start at the bottom, because you do not know which level is last until you get there.",
                    "So build the normal top-down list and reverse it once at the end.",
                ],
                "steps": [
                    "If <code>root</code> is None, return <code>[]</code>.",
                    "Run BFS with a <code>len(queue)</code> snapshot to build each <code>level</code>.",
                    "Append each completed <code>level</code> to <code>out</code>.",
                    "After the queue is empty, call <code>out.reverse()</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "The BFS part produces levels from depth 0 downwards, each in left-to-right order; reversing the outer list only reorders whole levels.",
                    "BFS is <strong>O(n)</strong>, and reversing a list of h levels is O(h), so the total is O(n).",
                    "The queue is <strong>O(w)</strong> space besides the output.",
                ],
                "dry": [
                    [
                        "Round 1: level = [3]. Round 2: level = [9, 20]. Round 3: level = [15, 7].",
                        "out = [[3], [9, 20], [15, 7]].",
                        "Reverse the outer list in place.",
                        "The result is <strong>[[15, 7], [9, 20], [3]]</strong>.",
                    ],
                    [
                        "The tree: 1 has children 2 and 3; 2 has a left child 4.",
                        "Round 1: [1]. Round 2: pop 2 (push 4), pop 3: [2, 3]. Round 3: [4].",
                        "out = [[1], [2, 3], [4]]; reverse it.",
                        "The result is <strong>[[4], [2, 3], [1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not reverse each level too?",
                     "The problem reverses only the order of the levels. Inside a level, values stay left to right; [2, 3] must not become [3, 2]."],
                    ["Is <code>reverse()</code> expensive?",
                     "It touches h list references, which is at most n and usually far less. It does not copy the inner lists."],
                    ["Can I use <code>out[::-1]</code> instead?",
                     "Yes. It returns a reversed copy instead of reversing in place; same result, one extra shallow list."],
                ],
            },
            "Prepend each level to a deque": {
                "idea": [
                    "Instead of reversing at the end, put each finished level at the <em>front</em> of the answer as it is produced.",
                    "A <code>deque</code> supports <code>appendleft</code> in O(1), unlike <code>list.insert(0, ...)</code>, which shifts every element.",
                    "The last level produced ends up first, which is the bottom-up order.",
                ],
                "steps": [
                    "If <code>root</code> is None, return <code>[]</code>.",
                    "Make <code>out</code> a <code>deque()</code> and run the usual size-snapshot BFS.",
                    "For each completed <code>level</code>, call <code>out.appendleft(level)</code>.",
                    "When the queue is empty, convert with <code>list(out)</code>.",
                    "Return that list.",
                ],
                "why": [
                    "Levels are produced top-down; prepending each one means the most recent (deepest) level is always at the front, so the final order is bottom-up.",
                    "Each <code>appendleft</code> is O(1), and BFS is <strong>O(n)</strong>; the final <code>list()</code> conversion is O(h).",
                    "Extra space is the BFS queue, <strong>O(w)</strong>, besides the output.",
                ],
                "dry": [
                    [
                        "Level [3] is produced: out = deque([[3]]).",
                        "Level [9, 20]: appendleft gives deque([[9, 20], [3]]).",
                        "Level [15, 7]: deque([[15, 7], [9, 20], [3]]).",
                        "Convert to a list. The result is <strong>[[15, 7], [9, 20], [3]]</strong>.",
                    ],
                    [
                        "Level [1]: out = deque([[1]]).",
                        "Level [2, 3]: deque([[2, 3], [1]]).",
                        "Level [4]: deque([[4], [2, 3], [1]]).",
                        "The result is <strong>[[4], [2, 3], [1]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not <code>out.insert(0, level)</code> on a list?",
                     "That shifts all existing levels each time, which is O(h) per insert and O(h²) in total. On a chain, where h = n, that is quadratic."],
                    ["Is this faster than reversing at the end?",
                     "Not meaningfully; both are linear. It mainly shows the deque idea, which matters when you cannot wait until the end."],
                    ["Why convert back with <code>list(out)</code>?",
                     "The expected return type is a list of lists, and a deque does not compare equal to a list."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ zigzag
    "zigzag-level-order": {
        "examples": [
            {"call": "zigzag(build([1, 2, 3, 4, 5, 6, 7]))", "expect": "[[1], [3, 2], [4, 5, 6, 7]]"},
            {"call": "zigzag(build([1, 2, 3, 4, None, None, 5]))", "expect": "[[1], [3, 2], [4, 5]]"},
        ],
        "approaches": {
            "BFS, reverse alternate levels": {
                "idea": [
                    "Zigzag order is normal level order where every second level (depth 1, 3, ...) is read right to left.",
                    "The traversal itself never changes direction: children are always enqueued left then right. Only the <em>recorded</em> list for odd levels is flipped.",
                    "A boolean <code>left_to_right</code> toggles after every level to say whether to flip.",
                ],
                "steps": [
                    "If <code>root</code> is None, return <code>[]</code>.",
                    "Start with <code>queue = deque([root])</code> and <code>left_to_right = True</code>.",
                    "For each level, pop <code>len(queue)</code> nodes into <code>level</code> and enqueue their children left then right.",
                    "If <code>left_to_right</code> is False, call <code>level.reverse()</code>; then append <code>level</code> to <code>out</code>.",
                    "Flip <code>left_to_right</code> and continue until the queue is empty.",
                ],
                "why": [
                    "The queue order is ordinary BFS order, so each <code>level</code> starts left to right; reversing exactly the odd-numbered ones gives the zigzag pattern.",
                    "BFS is O(n), and the reversals touch each value at most once more: <strong>O(n)</strong> time.",
                    "The queue holds up to one level: <strong>O(w)</strong> extra space.",
                ],
                "dry": [
                    [
                        "Level 0: [1], left_to_right is True, keep it. Flip to False.",
                        "Level 1: collected [2, 3]; reverse to [3, 2]. Flip to True.",
                        "Level 2: collected [4, 5, 6, 7]; kept as is.",
                        "The result is <strong>[[1], [3, 2], [4, 5, 6, 7]]</strong>.",
                    ],
                    [
                        "The tree: 1 has children 2 and 3; 2 has a left child 4; 3 has a right child 5.",
                        "Level 0: [1]. Level 1: [2, 3] reversed to [3, 2].",
                        "Level 2: pops 4 then 5, giving [4, 5], kept left to right.",
                        "The result is <strong>[[1], [3, 2], [4, 5]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not enqueue children right-to-left on odd levels instead?",
                     "Changing the enqueue order changes the order of the whole next level, and it gets confusing fast. Keeping BFS standard and flipping only the output is much harder to get wrong."],
                    ["Does reversing cost extra time?",
                     "Each value is moved at most once by a reverse, so it adds O(n) in total and the bound stays O(n)."],
                    ["Could I use the depth parity instead of a boolean?",
                     "Yes: <code>if len(out) % 2 == 1</code> before appending means \"odd level\". The boolean just names the idea."],
                ],
            },
            "Build each level into a deque": {
                "idea": [
                    "Instead of reversing afterwards, build each level in the right direction from the start.",
                    "Make <code>level</code> a deque: on left-to-right levels use <code>append</code>, on right-to-left levels use <code>appendleft</code>, so the first popped node ends up last.",
                    "The queue itself is still the normal left-to-right BFS.",
                ],
                "steps": [
                    "If <code>root</code> is None, return <code>[]</code>.",
                    "For each level, create <code>level = deque()</code>.",
                    "Pop <code>len(queue)</code> nodes; if <code>left_to_right</code>, <code>level.append(node.val)</code>, else <code>level.appendleft(node.val)</code>.",
                    "Enqueue children left then right as usual.",
                    "Append <code>list(level)</code> to <code>out</code> and flip <code>left_to_right</code>.",
                ],
                "why": [
                    "Nodes of a level are always popped left to right; appending at the front on odd levels stores them in reverse, which is exactly the zigzag order.",
                    "Every append and appendleft is O(1), so the total is <strong>O(n)</strong> time.",
                    "The queue and one level deque are each at most the width: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "Level 0: append 1 → [1]. Flip to right-to-left.",
                        "Level 1: pop 2, appendleft → [2]; pop 3, appendleft → [3, 2].",
                        "Level 2: append 4, 5, 6, 7 in turn → [4, 5, 6, 7].",
                        "The result is <strong>[[1], [3, 2], [4, 5, 6, 7]]</strong>.",
                    ],
                    [
                        "Level 0: [1].",
                        "Level 1: appendleft 2 then 3 → [3, 2].",
                        "Level 2: left to right again: append 4, then 5 → [4, 5].",
                        "The result is <strong>[[1], [3, 2], [4, 5]]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is this better than reversing?",
                     "Asymptotically no, both are O(n). It avoids a second pass over each odd level and shows a common deque trick."],
                    ["Why <code>list(level)</code> before appending to <code>out</code>?",
                     "The answer must be a list of lists; a deque would not compare equal to the expected lists."],
                    ["Could I use <code>level.insert(0, x)</code> on a list?",
                     "That is O(len(level)) per insert, so a wide level would cost O(w²). The deque makes it O(1)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ same tree
    "same-tree": {
        "examples": [
            {"call": "is_same_tree(build([1, 2, 3]), build([1, 2, 3]))", "expect": "True"},
            {"call": "is_same_tree(build([1, 2]), build([1, None, 2]))", "expect": "False"},
        ],
        "approaches": {
            "Parallel recursion": {
                "idea": [
                    "Two trees are the same when their roots match in value and their left subtrees are the same and their right subtrees are the same.",
                    "So walk both trees together, always comparing the node at the same position in each.",
                    "Shape matters as much as values: one side being None while the other is not is already a difference.",
                ],
                "steps": [
                    "If <code>p</code> and <code>q</code> are both None, return True: two empty subtrees are equal.",
                    "If exactly one is None, return False.",
                    "If <code>p.val != q.val</code>, return False.",
                    "Otherwise return <code>is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)</code>.",
                ],
                "why": [
                    "The three checks cover every way two positions can differ (missing node or different value), and the recursion applies them at every position, so True means the trees match everywhere.",
                    "<code>and</code> short-circuits, so the walk stops at the first difference; it visits at most the smaller tree: <strong>O(min(n, m))</strong> time.",
                    "The recursion goes as deep as the shallower matching path: <strong>O(min(h, h'))</strong> space.",
                ],
                "dry": [
                    [
                        "Compare (1, 1): both exist, values equal. Recurse left.",
                        "Compare (2, 2): equal. Their children are (None, None) twice, both True.",
                        "Compare (3, 3): equal, with (None, None) children.",
                        "Both sides return True. The result is <strong>True</strong>.",
                    ],
                    [
                        "First tree: 1 with left child 2. Second tree: 1 with right child 2.",
                        "Compare (1, 1): equal values, recurse left.",
                        "Compare (2, None): exactly one is None, return False.",
                        "<code>and</code> short-circuits, so the right side is never checked. The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the both-None check come first?",
                     "If you test <code>p.val</code> first, a None node raises AttributeError. Handling the None cases first also gives the base case of the recursion."],
                    ["Isn't comparing the two preorder lists enough?",
                     "No. build([1, 2]) and build([1, None, 2]) both have preorder [1, 2]. Without recording missing children the shape is lost."],
                    ["Why <code>and</code> instead of computing both sides?",
                     "Short-circuiting stops at the first mismatch, which can save most of the work on trees that differ early."],
                ],
            },
            "Iterative, stack of pairs": {
                "idea": [
                    "Do the same parallel comparison without recursion: keep a stack of position pairs <code>(a, b)</code> still to compare.",
                    "Each popped pair either matches (both None, or same value) or proves the trees differ.",
                    "A matching pair with nodes pushes its left pair and its right pair for later.",
                ],
                "steps": [
                    "Start with <code>stack = [(p, q)]</code>.",
                    "Pop <code>(a, b)</code>; if both are None, <code>continue</code>.",
                    "If one is None or <code>a.val != b.val</code>, return False.",
                    "Push <code>(a.left, b.left)</code> and <code>(a.right, b.right)</code>.",
                    "If the stack empties, every position matched: return True.",
                ],
                "why": [
                    "Every position present in either tree is eventually paired and checked, because each matched pair pushes both of its child positions.",
                    "It stops at the first mismatch, so the time is <strong>O(min(n, m))</strong>.",
                    "The stack plays the role of the call stack, roughly <strong>O(min(h, h'))</strong> pending pairs, and cannot overflow Python's recursion limit.",
                ],
                "dry": [
                    [
                        "stack = [(1, 1)]. Pop: equal. Push (2, 2), (3, 3).",
                        "Pop (3, 3): equal. Push (None, None) twice; both are popped and skipped.",
                        "Pop (2, 2): equal. Push two (None, None) pairs; both skipped.",
                        "The stack is empty. The result is <strong>True</strong>.",
                    ],
                    [
                        "stack = [(1, 1)]. Pop: equal. Push (2, None) for the left side, then (None, 2) for the right side.",
                        "Pop (None, 2): exactly one is None.",
                        "Return False immediately; (2, None) is never looked at.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Does it matter that the right pair is checked before the left?",
                     "No. Any order checks every position; the answer is the same and only which mismatch is found first changes."],
                    ["Why push None pairs instead of skipping them?",
                     "A (None, node) pair is exactly how a shape difference is detected. Filtering Nones before pushing would lose that check."],
                    ["Could I use a queue instead?",
                     "Yes, a deque with <code>popleft</code> gives a BFS comparison. It is equally correct and finds shallow differences sooner."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ symmetric tree
    "symmetric-tree": {
        "examples": [
            {"call": "is_symmetric(build([1, 2, 2, 3, 4, 4, 3]))", "expect": "True"},
            {"call": "is_symmetric(build([1, 2, 2, None, 3, None, 3]))", "expect": "False"},
        ],
        "approaches": {
            "Recursive mirror helper": {
                "idea": [
                    "A tree is symmetric when its left subtree is the mirror image of its right subtree.",
                    "Two trees <code>a</code> and <code>b</code> are mirrors when their roots match, <code>a.left</code> mirrors <code>b.right</code> (the outer pair) and <code>a.right</code> mirrors <code>b.left</code> (the inner pair).",
                    "This is Same Tree with the children crossed.",
                ],
                "steps": [
                    "Define <code>mirror(a, b)</code>: if both are None, return True.",
                    "If one is None or <code>a.val != b.val</code>, return False.",
                    "Return <code>mirror(a.left, b.right) and mirror(a.right, b.left)</code>.",
                    "The answer is <code>root is None or mirror(root.left, root.right)</code>.",
                ],
                "why": [
                    "Reflecting a tree swaps left and right at every level, so the outer and inner pairings are exactly the positions that must be equal for the reflection to match.",
                    "Each node is compared once as part of one pair: <strong>O(n)</strong> time.",
                    "The recursion goes down both halves together, so the depth is about the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "mirror(2, 2): values equal.",
                        "Outer pair mirror(3, 3): equal, and its children are (None, None), True.",
                        "Inner pair mirror(4, 4): equal, children None, True.",
                        "Both pairs pass. The result is <strong>True</strong>.",
                    ],
                    [
                        "The tree: both 2s have only a right child 3.",
                        "mirror(2, 2): values equal. Outer pair: mirror(left 2's left = None, right 2's right = 3).",
                        "Exactly one is None, so it returns False.",
                        "The inner pair is skipped by short-circuiting. The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not compare the inorder sequence with its reverse?",
                     "Different shapes can give a palindromic inorder. build([1, 2, 2, 2, None, 2]) has inorder [2, 2, 1, 2, 2], a palindrome, yet the tree is not symmetric."],
                    ["Why call <code>mirror(root.left, root.right)</code> and not <code>mirror(root, root)</code>?",
                     "<code>mirror(root, root)</code> also works but compares every pair twice. Starting from the two children does half the work."],
                    ["Does the root's value matter?",
                     "No. The root is on the axis of symmetry, so it is its own mirror image."],
                ],
            },
            "Iterative, queue of mirrored pairs": {
                "idea": [
                    "Put pairs of positions that must mirror each other into a queue and check them one by one.",
                    "From a matching pair <code>(a, b)</code>, the next pairs to check are <code>(a.left, b.right)</code> and <code>(a.right, b.left)</code>.",
                    "Any pair with one None or different values ends the check.",
                ],
                "steps": [
                    "If <code>root</code> is None, return True.",
                    "Start with <code>queue = deque([(root.left, root.right)])</code>.",
                    "Pop <code>(a, b)</code>; if both are None, continue.",
                    "If one is None or the values differ, return False.",
                    "Enqueue <code>(a.left, b.right)</code> and <code>(a.right, b.left)</code>; return True when the queue empties.",
                ],
                "why": [
                    "The queue contains exactly the pairs the recursive version would compare, only in level order, so it accepts and rejects the same trees.",
                    "Each node appears in one pair: <strong>O(n)</strong> time.",
                    "The queue holds pairs from about one level: <strong>O(w)</strong> space.",
                ],
                "dry": [
                    [
                        "queue = [(2, 2)]. Pop: equal; enqueue (3, 3) and (4, 4).",
                        "Pop (3, 3): equal; enqueue two (None, None) pairs.",
                        "Pop (4, 4): equal; enqueue two more (None, None) pairs.",
                        "The four None pairs are skipped. The result is <strong>True</strong>.",
                    ],
                    [
                        "queue = [(2, 2)]. Pop: equal; enqueue (None, 3) and (3, None).",
                        "Pop (None, 3): one side missing.",
                        "Return False.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why do the None pairs get enqueued?",
                     "A (None, node) pair is how a shape mismatch is detected. Two Nones are just skipped."],
                    ["Can I use a stack instead of a queue?",
                     "Yes. Any order of checking the pairs gives the same answer; a stack gives O(h) space instead of O(w)."],
                    ["Why the separate <code>root is None</code> check?",
                     "Otherwise <code>root.left</code> raises AttributeError on an empty tree, which counts as symmetric."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ invert
    "invert-binary-tree": {
        "examples": [
            {"call": "level_order(invert(build([4, 2, 7, 1, 3, 6, 9])))", "expect": "[4, 7, 2, 9, 6, 3, 1]"},
            {"call": "level_order(invert(build([1, 2])))", "expect": "[1, None, 2]"},
        ],
        "approaches": {
            "Recursive swap": {
                "idea": [
                    "Inverting a tree means swapping left and right at <strong>every</strong> node, not just the root.",
                    "The inverted tree's left child is the inverted old right subtree, and vice versa.",
                    "One recursive line does that, and the swap happens in place on the existing nodes.",
                ],
                "steps": [
                    "If <code>root</code> is None, return None.",
                    "Evaluate <code>invert(root.right)</code> and <code>invert(root.left)</code> (the right-hand side of the tuple assignment runs first).",
                    "Assign them to <code>root.left</code> and <code>root.right</code> respectively.",
                    "Return <code>root</code> so the parent can attach it.",
                ],
                "why": [
                    "By induction both subtrees come back fully inverted, and placing them on opposite sides completes the mirror image at this node.",
                    "The tuple assignment evaluates both calls before assigning, so neither original child is lost.",
                    "Each node is visited once: <strong>O(n)</strong> time, with <strong>O(h)</strong> recursion depth.",
                ],
                "dry": [
                    [
                        "The tree: 4 → (2, 7); 2 → (1, 3); 7 → (6, 9).",
                        "invert(7) runs first: its leaves 9 and 6 come back unchanged, and 7 becomes 7 → (9, 6).",
                        "invert(2): 2 becomes 2 → (3, 1).",
                        "At 4: left = inverted 7, right = inverted 2.",
                        "Level order is <strong>[4, 7, 2, 9, 6, 3, 1]</strong>.",
                    ],
                    [
                        "The tree: 1 with a left child 2.",
                        "invert(None) returns None; invert(2) swaps two Nones and returns 2.",
                        "1.left = None, 1.right = 2.",
                        "Level order is <strong>[1, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong with <code>root.left = invert(root.right)</code> then <code>root.right = invert(root.left)</code>?",
                     "The second line reads the already overwritten <code>root.left</code>, so the original left subtree is lost. The single tuple assignment avoids that."],
                    ["Does this create a new tree?",
                     "No. It rewires the existing nodes and returns the same root object."],
                    ["Does the traversal order matter?",
                     "No. Swapping children at every node in any order (pre, post, level) gives the same result."],
                ],
            },
            "Iterative with a worklist": {
                "idea": [
                    "Since every node just needs its children swapped, visit all nodes in any order and swap at each one.",
                    "A list used as a stack (<code>work</code>) holds nodes still to swap.",
                    "After swapping a node, push its children so they are swapped too.",
                ],
                "steps": [
                    "If <code>root</code> is None, return None.",
                    "Start with <code>work = [root]</code>.",
                    "Pop <code>node</code> and swap: <code>node.left, node.right = node.right, node.left</code>.",
                    "Push each existing child.",
                    "When <code>work</code> is empty, return <code>root</code>.",
                ],
                "why": [
                    "Each swap is local to one node, so doing every node exactly once in any order produces the full mirror image.",
                    "Each node is pushed and popped once: <strong>O(n)</strong> time.",
                    "As a stack it holds <strong>O(h)</strong> pending nodes; with a deque and <code>popleft</code> it would be a BFS holding O(w).",
                ],
                "dry": [
                    [
                        "work = [4]. Pop 4 and swap: 4 → (7, 2). Push 7, then 2.",
                        "Pop 2 and swap: 2 → (3, 1). Push 3, 1; pop 1 and 3 (leaves, swap Nones).",
                        "Pop 7 and swap: 7 → (9, 6). Push 9, 6; pop both.",
                        "The worklist is empty.",
                        "Level order is <strong>[4, 7, 2, 9, 6, 3, 1]</strong>.",
                    ],
                    [
                        "work = [1]. Pop 1 and swap: 1.left = None, 1.right = 2.",
                        "Push 2. Pop 2 and swap its two Nones.",
                        "The worklist is empty.",
                        "Level order is <strong>[1, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Does it matter that children are pushed after the swap?",
                     "No. Both children get pushed either way; after the swap they are just on the other sides, which is where they belong."],
                    ["Why use this over recursion?",
                     "It avoids Python's recursion limit on very deep trees."],
                    ["Can I skip leaves?",
                     "You could, but swapping two Nones is harmless and the check would cost about the same."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge trees
    "merge-two-binary-trees": {
        "examples": [
            {"call": "level_order(merge_trees(build([1, 3, 2, 5]), build([2, 1, 3, None, 4, None, 7])))", "expect": "[3, 4, 5, 5, 4, None, 7]"},
            {"call": "level_order(merge_trees(None, build([1, 2])))", "expect": "[1, 2]"},
        ],
        "approaches": {
            "Recursive, reusing the first tree": {
                "idea": [
                    "Walk both trees together. Where both have a node, the merged node holds the sum; where only one has a node, the merged tree takes that whole subtree.",
                    "Reuse <code>root1</code>'s nodes for the result: add <code>root2.val</code> into them and reattach the merged children.",
                    "When one side is missing, the other subtree is returned as it is, so it is grafted without being walked at all.",
                ],
                "steps": [
                    "If <code>root1</code> is None, return <code>root2</code>.",
                    "If <code>root2</code> is None, return <code>root1</code>.",
                    "Add: <code>root1.val += root2.val</code>.",
                    "Set <code>root1.left = merge_trees(root1.left, root2.left)</code> and the same for the right.",
                    "Return <code>root1</code>.",
                ],
                "why": [
                    "Every position present in both trees gets the sum, and every position present in only one keeps that tree's subtree, which is the definition of the merge.",
                    "Recursion only continues where both trees have a node, so the work is <strong>O(min(n, m))</strong>.",
                    "The recursion depth is at most the shallower overlap: <strong>O(min(h, h'))</strong> space. The downside is that both input trees are changed or shared by the result.",
                ],
                "dry": [
                    [
                        "Tree 1: 1 → (3, 2), 3 → (5, -). Tree 2: 2 → (1, 3), 1 → (-, 4), 3 → (-, 7).",
                        "Roots: 1 + 2 = 3. Left: 3 + 1 = 4; its left is (5, None), so 5 is kept; its right is (None, 4), so tree 2's 4 is grafted.",
                        "Right: 2 + 3 = 5; its left is (None, None) → None; its right is (None, 7), so 7 is grafted.",
                        "Tree 1's nodes now form the result.",
                        "Level order is <strong>[3, 4, 5, 5, 4, None, 7]</strong>.",
                    ],
                    [
                        "root1 is None.",
                        "Return root2 immediately, without touching any node.",
                        "The result is tree 2 itself.",
                        "Level order is <strong>[1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is it a problem that the result shares nodes with the inputs?",
                     "Only if the inputs are used afterwards: tree 1 has been modified and grafted parts of tree 2 now belong to two trees. Use the non-destructive version when the inputs must stay intact."],
                    ["Why is it O(min(n, m)) and not O(n + m)?",
                     "A subtree that exists in only one tree is attached by a single pointer assignment, never walked."],
                    ["What if both are None?",
                     "The first check returns <code>root2</code>, which is None, so that case needs no special line."],
                ],
            },
            "Non-destructive, allocating a new tree": {
                "idea": [
                    "Build a brand-new result so neither input is modified or shared.",
                    "Where both trees have a node, create <code>TreeNode(root1.val + root2.val)</code> and merge the children recursively.",
                    "Where only one has a node, that subtree must be copied with <code>copy_tree</code>, not grafted, so the result owns all its nodes.",
                ],
                "steps": [
                    "If both are None, return None.",
                    "If only one is None, return <code>copy_tree</code> of the other.",
                    "Create <code>node = TreeNode(root1.val + root2.val)</code>.",
                    "Set <code>node.left</code> and <code>node.right</code> by merging the matching children.",
                    "<code>copy_tree</code> recursively builds a fresh node for every node of a subtree.",
                ],
                "why": [
                    "The structure and values match the merge definition, and every node in the result was freshly created, so later changes to the result never affect the inputs.",
                    "Every node of both trees is either merged or copied once: <strong>O(n + m)</strong> time.",
                    "The result has up to n + m nodes: <strong>O(n + m)</strong> space, plus the recursion stack.",
                ],
                "dry": [
                    [
                        "New root: 1 + 2 = 3. New left: 3 + 1 = 4.",
                        "Under 4: left is (5, None), so copy 5; right is (None, 4), so copy 4.",
                        "New right: 2 + 3 = 5; left (None, None) → None; right (None, 7) → copy 7.",
                        "Neither input tree is changed.",
                        "Level order is <strong>[3, 4, 5, 5, 4, None, 7]</strong>.",
                    ],
                    [
                        "root1 is None and root2 is not.",
                        "copy_tree(1) creates a new 1 and copy_tree(2) a new 2 under it.",
                        "The result looks like tree 2 but shares no nodes with it.",
                        "Level order is <strong>[1, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why copy the leftover subtree instead of attaching it?",
                     "Attaching it would make the result share nodes with an input, which is exactly what this version promises not to do."],
                    ["Why is it slower than the in-place version?",
                     "It must touch every node of both trees, including the parts present in only one, to copy them."],
                    ["When would an interviewer want this one?",
                     "When they say the inputs are read-only or still needed afterwards."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ subtree
    "subtree-of-another-tree": {
        "examples": [
            {"call": "is_subtree(build([3, 4, 5, 1, 2]), build([4, 1, 2]))", "expect": "True"},
            {"call": "is_subtree(build([3, 4, 5, 1, 2, None, None, None, None, 0]), build([4, 1, 2]))", "expect": "False"},
        ],
        "approaches": {
            "Same-Tree at every node": {
                "idea": [
                    "<code>sub_root</code> is a subtree of <code>root</code> if some node of <code>root</code>, together with <em>all</em> its descendants, is identical to <code>sub_root</code>.",
                    "So try every node of <code>root</code> as a starting point and run the Same Tree check from there.",
                    "A match must include everything below the node; extra descendants make it fail.",
                ],
                "steps": [
                    "If <code>sub_root</code> is None, return True; if <code>root</code> is None, return False.",
                    "If <code>same(root, sub_root)</code>, return True.",
                    "Otherwise return <code>is_subtree(root.left, sub_root) or is_subtree(root.right, sub_root)</code>.",
                    "<code>same(a, b)</code> is the parallel recursion: both None is True, one None or different values is False, else compare both children pairs.",
                ],
                "why": [
                    "Every node of <code>root</code> is tried as the starting point unless a match is found earlier, so a matching subtree cannot be missed.",
                    "Each <code>same</code> call costs up to O(m), and it may run at all n nodes: <strong>O(n × m)</strong> time in the worst case, usually much less because mismatches stop early.",
                    "Both recursions are bounded by the height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "same(3, 4): values differ, False.",
                        "is_subtree(4): same(4, 4) compares (1, 1) and (2, 2), all leaves match.",
                        "same returns True, so is_subtree returns True without trying 5.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "The tree is the same, except node 2 now has a left child 0.",
                        "same(3, 4): False. same(4, 4): (1, 1) matches; at (2, 2) the left pair is (0, None), so False.",
                        "Try 1, 2, 0 and 5 as starting points: each fails on its value.",
                        "No node matches. The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the extra 0 make it fail?",
                     "A subtree means a node and <em>all</em> its descendants. The 4 in the big tree has a descendant (0) that the small tree lacks, so they are not identical."],
                    ["When is the O(n × m) worst case reached?",
                     "With many equal values, e.g. a tree of all 1s and a sub-tree of 1s that differs only at its very bottom: every start runs almost the full comparison."],
                    ["Why check <code>sub_root is None</code> first?",
                     "An empty tree is a subtree of every tree, including an empty one, so that check must come before the <code>root is None</code> one."],
                ],
            },
            "Serialise both, then substring search": {
                "idea": [
                    "Turn each tree into a string that uniquely describes its shape and values; then a subtree corresponds to a <strong>substring</strong>.",
                    "Preorder with a <code>#</code> for every missing child records the shape, and parentheses group each subtree.",
                    "Each value starts with <code>^</code>, so a value like 2 cannot match the tail of 12.",
                ],
                "steps": [
                    "<code>serialise(None)</code> returns <code>\"#\"</code>.",
                    "<code>serialise(node)</code> returns <code>^val(</code> + left string + right string + <code>)</code>.",
                    "Serialise <code>root</code> and <code>sub_root</code>.",
                    "Return whether the second string occurs inside the first, using Python's <code>in</code>.",
                ],
                "why": [
                    "Each subtree's serialisation is a contiguous block of its tree's string, and the markers make the encoding one-to-one, so a substring match that starts at a <code>^</code> is a real identical subtree. The <code>^</code> and balanced brackets stop matches starting in the middle of a value.",
                    "Building the strings is linear in the number of nodes (ignoring value lengths), and the search is near-linear in CPython; with KMP it is guaranteed <strong>O(n + m)</strong>.",
                    "The two strings take <strong>O(n + m)</strong> space.",
                ],
                "dry": [
                    [
                        "sub: <code>^4(^1(##)^2(##))</code>.",
                        "root: <code>^3(^4(^1(##)^2(##))^5(##))</code>.",
                        "The sub string appears right after <code>^3(</code>.",
                        "The result is <strong>True</strong>.",
                    ],
                    [
                        "sub: <code>^4(^1(##)^2(##))</code>.",
                        "root: <code>^3(^4(^1(##)^2(^0(##)#))^5(##))</code>.",
                        "Inside root, <code>^2(</code> is followed by <code>^0</code>, not <code>##</code>, so the match breaks there.",
                        "The result is <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>^</code> before each value?",
                     "Without it, the tree [12] serialises to <code>12(##)</code>, which contains <code>2(##)</code>, so [2] would wrongly count as a subtree of [12]."],
                    ["Why the <code>#</code> markers?",
                     "Without them build([1, 2]) and build([1, None, 2]) both serialise to <code>^1(^2())</code>, so different shapes would look identical."],
                    ["Is Python's <code>in</code> really linear?",
                     "Not guaranteed in every case, but CPython's string search is close to linear in practice. If an interviewer asks for a strict bound, use KMP or rolling hashes on the two strings."],
                ],
            },
        },
    },
}
