"""Write-ups for Trees, part F: BST iterators, merging, counting, repair, balanced trees, N-ary trees, next pointers."""

EXPLAIN = {
    # ------------------------------------------------------------------ BST iterator
    "bst-iterator": {
        "examples": [
            {"setup": "it = BSTIterator(build([7, 3, 15, None, None, 9, 20]))",
             "call": "[it.next(), it.next(), it.hasNext(), it.next(), it.next(), it.next(), it.hasNext()]",
             "expect": "[3, 7, True, 9, 15, 20, False]"},
            {"setup": "it = BSTIterator(build([3, 1, None, None, 2]))",
             "call": "[it.next(), it.next(), it.hasNext(), it.next(), it.hasNext()]",
             "expect": "[1, 2, True, 3, False]"},
        ],
        "approaches": {
            "Controlled stack of the left spine": {
                "idea": [
                    "This is an iterative inorder traversal cut into pieces: each <code>next()</code> runs it just far enough to produce one value.",
                    "The stack holds the nodes whose left side has been entered but which have not been returned yet; the top is always the next smallest value.",
                    "After returning a node, the next values come from its right subtree, starting with that subtree's leftmost node.",
                ],
                "steps": [
                    "<code>_push_left(node)</code> pushes <code>node</code> and every node down its left spine.",
                    "The constructor calls <code>_push_left(root)</code>, so the smallest value is on top.",
                    "<code>next()</code> pops the top <code>node</code>, calls <code>_push_left(node.right)</code>, and returns <code>node.val</code>.",
                    "<code>hasNext()</code> returns whether the stack is non-empty.",
                ],
                "why": [
                    "Every node still on the stack is larger than everything already returned and smaller than everything in its own right subtree, so the top is always the next value in order.",
                    "Each node is pushed once and popped once over the whole iteration, so n calls do O(n) work: <strong>O(1) amortised per call</strong>, though one call can push up to h nodes.",
                    "The stack holds at most one root-to-leaf path: <strong>O(h)</strong> space, not O(n).",
                ],
                "dry": [
                    [
                        "The tree: 7 → (3, 15), 15 → (9, 20). The constructor pushes 7, 3: stack [7, 3].",
                        "next(): pop 3, no right child. Returns 3. next(): pop 7, push 15's left spine: stack [15, 9]. Returns 7.",
                        "hasNext(): stack non-empty, True. next(): pop 9, returns 9.",
                        "next(): pop 15, push 20, returns 15. next(): pop 20, returns 20. hasNext(): False.",
                        "The calls give <strong>[3, 7, True, 9, 15, 20, False]</strong>.",
                    ],
                    [
                        "The tree: 3 → (1, None), 1 → (None, 2). The constructor pushes 3, 1: stack [3, 1].",
                        "next(): pop 1, push its right child 2: stack [3, 2]. Returns 1.",
                        "next(): pop 2, returns 2. hasNext(): stack [3], True.",
                        "next(): pop 3, returns 3. hasNext(): False.",
                        "The calls give <strong>[1, 2, True, 3, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not store the whole inorder list in the constructor?",
                     "That works but costs O(n) memory. The follow-up asks for O(h), which is what the left-spine stack achieves."],
                    ["Isn't a single <code>next()</code> sometimes O(h)?",
                     "Yes, when it pushes a long left spine. The guarantee is amortised: across all n calls the total pushes are n."],
                    ["What does <code>next()</code> do when nothing is left?",
                     "It raises IndexError from <code>pop()</code>. The problem promises <code>next()</code> is only called when <code>hasNext()</code> is true."],
                ],
            },
            "Python generator": {
                "idea": [
                    "A recursive generator yields an inorder sequence lazily, pausing between values, so the language keeps the traversal state for you.",
                    "Since a generator cannot be asked \"is there more?\" without advancing it, the class keeps one value of look-ahead in <code>_peek</code>.",
                ],
                "steps": [
                    "<code>_inorder(node)</code> yields from the left subtree, yields <code>node.val</code>, then yields from the right subtree.",
                    "The constructor creates the generator and fetches the first value into <code>_peek</code> with <code>next(self._gen, None)</code>.",
                    "<code>next()</code> returns the current <code>_peek</code> and fetches the following value into it.",
                    "<code>hasNext()</code> is <code>_peek is not None</code>.",
                ],
                "why": [
                    "The generator produces exactly the inorder sequence, and the look-ahead never skips or repeats a value.",
                    "The suspended generators form a chain along the current path, so memory is <strong>O(h)</strong>.",
                    "Each value is produced once, giving the listed <strong>O(1) amortised per call</strong>; note that each resume passes through the chain of <code>yield from</code> frames, so a single call can cost up to O(h).",
                ],
                "dry": [
                    [
                        "The constructor advances the generator to 3: _peek = 3.",
                        "next() returns 3, _peek = 7. next() returns 7, _peek = 9. hasNext(): True.",
                        "next() returns 9 (_peek = 15), then 15 (_peek = 20), then 20 (_peek = None).",
                        "hasNext(): _peek is None, so False.",
                        "The calls give <strong>[3, 7, True, 9, 15, 20, False]</strong>.",
                    ],
                    [
                        "The constructor goes left from 3 to 1, which has no left child: _peek = 1.",
                        "next() returns 1, _peek = 2. next() returns 2, _peek = 3.",
                        "hasNext(): True. next() returns 3, and the generator is exhausted: _peek = None.",
                        "The calls give <strong>[1, 2, True, 3, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the look-ahead value?",
                     "Generators have no \"has more\" test. Fetching one value early is the only way to answer <code>hasNext()</code> without losing a value."],
                    ["Does <code>_peek is not None</code> break when a node's value is 0?",
                     "No. It compares with <code>None</code>, not truthiness, so a 0 value still counts. It would only break if a node's value were <code>None</code> itself."],
                    ["Is this acceptable in an interview?",
                     "It shows good Python, but interviewers usually want the explicit stack because it shows you understand the traversal state the generator hides."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ all elements in two BSTs
    "all-elements-two-bsts": {
        "examples": [
            {"call": "get_all_elements(build([2, 1, 4]), build([1, 0, 3]))", "expect": "[0, 1, 1, 2, 3, 4]"},
            {"call": "get_all_elements(build([1, None, 8]), build([8, 1]))", "expect": "[1, 1, 8, 8]"},
        ],
        "approaches": {
            "Merge two inorder iterators": {
                "idea": [
                    "Each BST yields a sorted stream through an iterative inorder walk, and two sorted streams merge like in merge sort.",
                    "Each stream is a left-spine stack, as in the BST iterator; its top is that tree's next smallest value.",
                    "Repeatedly take the smaller of the two tops.",
                ],
                "steps": [
                    "<code>spine(node, stack)</code> pushes <code>node</code> and its left descendants.",
                    "Fill <code>s1</code> from <code>root1</code> and <code>s2</code> from <code>root2</code>.",
                    "While either stack is non-empty: take from <code>s1</code> if <code>s2</code> is empty or <code>s1[-1].val &lt;= s2[-1].val</code>; otherwise take from <code>s2</code>.",
                    "Pop the chosen node, push the left spine of its right child onto the same stack.",
                    "Append the node's value to <code>out</code>; return <code>out</code> at the end.",
                ],
                "why": [
                    "Each stack's top is the minimum of its remaining values, so the smaller top is the minimum of everything remaining, and <code>out</code> is built in sorted order.",
                    "Every node is pushed and popped once: <strong>O(m + n)</strong> time.",
                    "The stacks hold one path per tree: <strong>O(h<sub>1</sub> + h<sub>2</sub>)</strong> extra space beyond the output.",
                ],
                "dry": [
                    [
                        "s1 = [2, 1], s2 = [1, 0]. 0 &lt; 1, so take 0 from s2.",
                        "Tops 1 and 1: the tie goes to s1, take 1. Then take 1 from s2, which pushes its right child 3: s2 = [3].",
                        "Tops 2 and 3: take 2, which pushes 4: s1 = [4]. Tops 4 and 3: take 3.",
                        "s2 is empty, so take 4.",
                        "The merged list is <strong>[0, 1, 1, 2, 3, 4]</strong>.",
                    ],
                    [
                        "Tree 1 is 1 → (None, 8); tree 2 is 8 → (1, None). s1 = [1], s2 = [8, 1].",
                        "Tops 1 and 1: take from s1, which pushes 8: s1 = [8].",
                        "Tops 8 and 1: take 1 from s2. Tops 8 and 8: take from s1.",
                        "s1 is empty, so take 8 from s2.",
                        "The merged list is <strong>[1, 1, 8, 8]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> rather than <code>&lt;</code>?",
                     "Either works for correctness, since equal values are interchangeable. <code>&lt;=</code> just decides ties consistently in favour of the first tree."],
                    ["Why check <code>not s2</code> first?",
                     "When one tree is exhausted, reading <code>s2[-1]</code> would raise IndexError. The condition order means an empty <code>s2</code> always sends the choice to <code>s1</code>, and the loop guard guarantees <code>s1</code> is then non-empty."],
                    ["Does it handle an empty tree?",
                     "Yes. <code>spine(None, ...)</code> pushes nothing, so the merge simply drains the other stack."],
                ],
            },
            "Concatenate both inorders and sort": {
                "idea": [
                    "Collect both inorder lists, concatenate them, and sort.",
                    "Python's sort (Timsort) detects already-sorted runs, and here the input is exactly two sorted runs, so it merges them in linear time.",
                ],
                "steps": [
                    "Compute <code>vals_in(root1)</code> and <code>vals_in(root2)</code>, each a sorted list.",
                    "Concatenate them with <code>+</code>.",
                    "Call <code>sorted</code> on the result.",
                    "Return the sorted list.",
                ],
                "why": [
                    "Sorting the union gives the required output by definition.",
                    "Timsort finds the two ascending runs and does a single merge: <strong>O(m + n) in CPython</strong>; a general sort would be O((m + n) log(m + n)).",
                    "The lists of values take <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "vals_in gives [1, 2, 4] and [0, 1, 3].",
                        "Concatenated: [1, 2, 4, 0, 1, 3], two ascending runs.",
                        "Timsort merges the runs.",
                        "The result is <strong>[0, 1, 1, 2, 3, 4]</strong>.",
                    ],
                    [
                        "vals_in gives [1, 8] and [1, 8].",
                        "Concatenated: [1, 8, 1, 8].",
                        "Sorting gives <strong>[1, 1, 8, 8]</strong>.",
                    ],
                ],
                "faq": [
                    ["Is this really linear?",
                     "The sort is, because Timsort merges natural runs. The helper <code>vals_in</code> builds lists with repeated concatenation, which can cost more than linear on deep trees."],
                    ["Would an interviewer accept it?",
                     "As a first answer, yes, but expect to be asked for the explicit merge, which does not depend on Python's sort implementation."],
                    ["Why not use <code>heapq.merge</code>?",
                     "That also works and is linear: <code>list(heapq.merge(vals_in(root1), vals_in(root2)))</code>. It is the library form of the merge approach."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ two sum IV
    "two-sum-bst": {
        "examples": [
            {"call": "find_target(build([5, 3, 6, 2, 4, None, 7]), 9)", "expect": "True"},
            {"call": "find_target(build([2, 1, 3]), 6)", "expect": "False"},
        ],
        "approaches": {
            "Hash set during any traversal": {
                "idea": [
                    "The classic two-sum trick works on any collection: for each value x, check whether <code>k - x</code> has already been seen.",
                    "The tree order does not matter, so any traversal will do; this one is an iterative DFS.",
                ],
                "steps": [
                    "Start with <code>seen = set()</code> and <code>stack = [root]</code>.",
                    "Pop a node; skip <code>None</code>.",
                    "If <code>k - node.val</code> is in <code>seen</code>, return <code>True</code>.",
                    "Add <code>node.val</code> to <code>seen</code> and push both children.",
                    "If the stack empties, return <code>False</code>.",
                ],
                "why": [
                    "For any valid pair, whichever of the two nodes is visited second finds its partner already in <code>seen</code>.",
                    "The check happens before adding the current value, so a node can never pair with itself.",
                    "Each node costs O(1) on average: <strong>O(n)</strong> time, and the set can hold all values: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop 5: 4 not seen, seen {5}. Pop 6: 3 not seen, seen {5, 6}.",
                        "Pop 7: 2 not seen, seen {5, 6, 7}. The empty children are skipped.",
                        "Pop 3: 9 − 3 = 6 is in seen.",
                        "It returns <strong>True</strong>.",
                    ],
                    [
                        "Pop 2: 4 not seen, seen {2}.",
                        "Pop 3: 3 not in {2} (3 is only added after the check), seen {2, 3}.",
                        "Pop 1: 5 not seen.",
                        "The stack empties: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check before adding?",
                     "With k = 6 and a node 3, adding first would find 3 in the set and wrongly pair the node with itself."],
                    ["What if the tree has two equal values?",
                     "Then the second copy finds the first in <code>seen</code>, which is a valid pair of different nodes."],
                    ["Why not use the BST property here?",
                     "This version does not need it, which makes it work on any binary tree. The two-pointer version uses it to save memory."],
                ],
            },
            "Two pointers with forward and backward iterators": {
                "idea": [
                    "On a sorted array, two-sum uses a left pointer and a right pointer moving towards each other.",
                    "A BST gives the same thing without an array: an inorder iterator for the smallest values (<code>lo</code>) and a reverse-inorder iterator for the largest (<code>hi</code>).",
                    "Each iterator is a stack whose top is the current pointer.",
                ],
                "steps": [
                    "<code>push(stack, node, forward)</code> pushes a left spine (forward) or a right spine (backward).",
                    "Initialise <code>lo</code> with the left spine and <code>hi</code> with the right spine of the root.",
                    "While both are non-empty and their tops are different nodes, compute <code>total</code>.",
                    "If <code>total == k</code>, return <code>True</code>. If smaller, advance <code>lo</code> (pop, push the left spine of its right child); if larger, advance <code>hi</code> (pop, push the right spine of its left child).",
                    "When the pointers meet, return <code>False</code>.",
                ],
                "why": [
                    "A too-small sum means the current low value cannot pair with anything (the high pointer is the largest left), so it can be discarded; the mirror holds for too-large sums.",
                    "The pointers stop when they reach the same node, so a node is never paired with itself.",
                    "Each node is pushed and popped at most once by each iterator: <strong>O(n)</strong> time, with two stacks of height h: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "lo = [5, 3, 2] (top 2), hi = [5, 6, 7] (top 7).",
                        "total = 2 + 7 = 9, which equals k.",
                        "It returns <strong>True</strong> on the first comparison.",
                    ],
                    [
                        "lo = [2, 1], hi = [2, 3]. total = 1 + 3 = 4 &lt; 6: advance lo, lo = [2].",
                        "total = 2 + 3 = 5 &lt; 6: advance lo, which pops 2 and pushes 3: lo = [3].",
                        "Now both tops are the same node 3, so the loop stops.",
                        "It returns <strong>False</strong>: 3 + 3 would reuse one node.",
                    ],
                ],
                "faq": [
                    ["Why compare nodes with <code>is not</code> instead of values?",
                     "Two different nodes can hold equal values and be a valid pair. Comparing identity stops only when both pointers are on the same node."],
                    ["Why can the pointers never cross without meeting?",
                     "They walk the same sorted order from opposite ends one node at a time, so the first time they would overlap they are on the same node."],
                    ["When is this better than the hash set?",
                     "When memory matters: it uses O(h) instead of O(n), at the cost of more code."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ unique BSTs (count)
    "unique-bsts": {
        "examples": [
            {"call": "num_trees(4)", "expect": "14"},
            {"call": "num_trees(1)", "expect": "1"},
        ],
        "approaches": {
            "Bottom-up DP over sizes": {
                "idea": [
                    "Pick a root r among 1..n. The values below r form the left subtree and the values above form the right subtree, and the two choices are independent.",
                    "The number of BSTs depends only on how many values there are, not which ones, so let <code>G[size]</code> be the count for <code>size</code> values.",
                    "Then <code>G[size] = Σ G[root − 1] · G[size − root]</code> over every root.",
                ],
                "steps": [
                    "Start with <code>G = [1] + [0] * n</code>: one empty tree.",
                    "For each <code>size</code> from 1 to n, loop <code>root</code> from 1 to <code>size</code>.",
                    "Add <code>G[root - 1] * G[size - root]</code> to <code>G[size]</code>: left choices times right choices.",
                    "Return <code>G[n]</code>.",
                ],
                "why": [
                    "Different roots give different trees, and for a fixed root every left/right combination is a distinct BST, so the sum counts every tree exactly once.",
                    "Both sizes on the right are smaller than <code>size</code>, so they are already final when used.",
                    "The double loop does about n²/2 multiplications: <strong>O(n²)</strong> time and an <strong>O(n)</strong> table.",
                ],
                "dry": [
                    [
                        "G[0] = 1. G[1] = G[0]·G[0] = 1.",
                        "G[2] = G[0]·G[1] + G[1]·G[0] = 2.",
                        "G[3] = G[0]·G[2] + G[1]·G[1] + G[2]·G[0] = 2 + 1 + 2 = 5.",
                        "G[4] = G[0]·G[3] + G[1]·G[2] + G[2]·G[1] + G[3]·G[0] = 5 + 2 + 2 + 5.",
                        "The answer is <strong>14</strong>.",
                    ],
                    [
                        "G = [1, 0].",
                        "size = 1, root = 1: G[1] += G[0]·G[0] = 1.",
                        "A single value makes exactly one tree: <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>G[0]</code> 1 and not 0?",
                     "An empty subtree is one valid choice. With 0 every product with an empty side would vanish and the counts would all be 0."],
                    ["Why multiply rather than add the two sides?",
                     "Each left subtree can be combined with each right subtree, so the choices multiply."],
                    ["Why does only the size matter?",
                     "Any k consecutive values form the same set of shapes; relabelling 1..k to a..a+k−1 does not change the count."],
                ],
            },
            "Closed form: the Catalan number": {
                "idea": [
                    "The recurrence above is the defining recurrence of the <strong>Catalan numbers</strong>, so the answer is C<sub>n</sub>.",
                    "C<sub>n</sub> has the closed form <code>comb(2n, n) / (n + 1)</code>.",
                ],
                "steps": [
                    "Compute <code>comb(2 * n, n)</code>, the central binomial coefficient.",
                    "Integer-divide it by <code>n + 1</code>.",
                    "Return the result; the division is always exact.",
                    "Python integers are unbounded, so there is no overflow for large n.",
                ],
                "why": [
                    "G satisfies the Catalan recurrence with the same start value G[0] = 1, so G[n] = C<sub>n</sub> = (2n)! / ((n + 1)! n!).",
                    "<code>math.comb</code> does O(n) multiplications: <strong>O(n)</strong> arithmetic steps (on growing big integers).",
                    "Only a few numbers are stored: <strong>O(1)</strong> space, ignoring the size of the big integers.",
                ],
                "dry": [
                    [
                        "comb(8, 4) = 70.",
                        "70 // 5 = 14.",
                        "The answer is <strong>14</strong>.",
                    ],
                    [
                        "comb(2, 1) = 2.",
                        "2 // 2 = 1.",
                        "The answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>//</code> safe here?",
                     "Yes. comb(2n, n) is always divisible by n + 1, which is why Catalan numbers are integers."],
                    ["Would I be expected to know this formula?",
                     "Recognising the Catalan pattern is a bonus. The DP is what interviewers expect you to derive."],
                    ["What else counts with Catalan numbers?",
                     "Balanced parentheses strings, full binary trees, triangulations of a polygon and monotone lattice paths that stay under the diagonal."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ unique BSTs II (generate)
    "unique-bsts-ii": {
        "examples": [
            {"call": "sorted(level_order(t) for t in generate_trees(3))",
             "expect": "[[1, None, 2, None, 3], [1, None, 3, 2], [2, 1, 3], [3, 1, None, None, 2], [3, 2, None, 1]]"},
            {"call": "generate_trees(0)", "expect": "[]"},
        ],
        "approaches": {
            "Recursive generation over value ranges, memoised": {
                "idea": [
                    "Same split as the counting problem, but building the trees: for each root, combine every left tree from the smaller values with every right tree from the larger values.",
                    "<code>gen(lo, hi)</code> returns all BSTs on the values <code>lo..hi</code>; an empty range returns <code>[None]</code>, one empty tree.",
                    "Memoising on <code>(lo, hi)</code> avoids rebuilding the same sub-lists, at the price of sharing subtree objects between trees.",
                ],
                "steps": [
                    "If <code>lo &gt; hi</code>, return <code>[None]</code>.",
                    "For each <code>root</code> in <code>lo..hi</code>, loop <code>left</code> over <code>gen(lo, root - 1)</code> and <code>right</code> over <code>gen(root + 1, hi)</code>.",
                    "Append <code>TreeNode(root, left, right)</code> for every pair.",
                    "Return the list; <code>@cache</code> stores it for that range.",
                    "Return <code>gen(1, n)</code>, or <code>[]</code> when n is 0.",
                ],
                "why": [
                    "Every BST on <code>lo..hi</code> has some root, and its subtrees are BSTs on the two sub-ranges, so the loops produce each tree exactly once.",
                    "The output has C<sub>n</sub> trees with n nodes each, and each one gets a fresh root node: about <strong>O(n · C<sub>n</sub>)</strong> time and space as listed.",
                    "Returning <code>[None]</code> rather than <code>[]</code> for an empty range is what lets the product loops run when one side is empty.",
                ],
                "dry": [
                    [
                        "gen(1, 3), root 1: left [None], right gen(2, 3) gives two trees (2 → 3 and 3 → 2). Two trees.",
                        "Root 2: gen(1, 1) = [1], gen(3, 3) = [3]. One tree.",
                        "Root 3: gen(1, 2) gives two trees, right [None]. Two trees.",
                        "That makes 5 trees, C<sub>3</sub>. Sorted by level order: <strong>[[1, None, 2, None, 3], [1, None, 3, 2], [2, 1, 3], [3, 1, None, None, 2], [3, 2, None, 1]]</strong>.",
                    ],
                    [
                        "n = 0, so <code>gen</code> is never called.",
                        "Without the guard, gen(1, 0) would return [None], a list containing one empty tree.",
                        "The problem wants no trees at all: <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>[None]</code> for an empty range?",
                     "The nested loops need one choice for an empty side. With <code>[]</code> the inner loop would never run and no tree with an empty child would ever be built."],
                    ["Do the returned trees share nodes?",
                     "Yes. Because of <code>@cache</code>, the same subtree object is reused: for n = 3 the five trees have 15 node slots but only 12 distinct node objects. Mutating one tree can change another."],
                    ["Why is n = 0 special-cased?",
                     "LeetCode expects an empty list there, while gen(1, 0) would give <code>[None]</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum sum BST in binary tree
    "max-sum-bst": {
        "examples": [
            {"call": "max_sum_bst(build([5, 4, 8, 3, None, 6, 3]))", "expect": "7"},
            {"call": "max_sum_bst(build([-4, -2, -5]))", "expect": "0"},
        ],
        "approaches": {
            "Postorder returning (is_bst, min, max, sum)": {
                "idea": [
                    "Whether a subtree is a BST can be decided from its children alone if each child reports whether it is a BST, its minimum and maximum, and its sum.",
                    "A node forms a BST when both children do and <code>left max &lt; node.val &lt; right min</code>.",
                    "Postorder computes children first, so every subtree is checked once, and the best BST sum is tracked along the way.",
                ],
                "steps": [
                    "<code>dfs(None)</code> returns <code>(True, INF, -INF, 0)</code>: an empty tree is a BST that never blocks its parent.",
                    "Recurse on both children to get <code>(lb, lmin, lmax, lsum)</code> and <code>(rb, rmin, rmax, rsum)</code>.",
                    "If <code>lb and rb and lmax &lt; node.val &lt; rmin</code>: compute <code>total</code>, update <code>best</code>, and return <code>(True, min(lmin, node.val), max(rmax, node.val), total)</code>.",
                    "Otherwise return <code>(False, 0, 0, 0)</code>; the other fields are never read.",
                    "Return <code>best</code>, which starts at 0 so an all-negative tree gives 0 (the empty BST).",
                ],
                "why": [
                    "The BST property of a subtree is exactly: both children are BSTs and the node lies between the left max and right min, so the check is complete.",
                    "Once a subtree is not a BST, no ancestor can be one either, so returning False upward is correct.",
                    "Each node is processed once with O(1) work: <strong>O(n)</strong> time, and the recursion depth gives <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 5 → (4, 8), 4 → (3, None), 8 → (6, 3).",
                        "Leaf 3: BST, sum 3, best = 3. Node 4: 3 &lt; 4 &lt; inf, BST with sum 7, best = 7.",
                        "Leaves 6 and 3 under 8 are BSTs (sums 6 and 3). Node 8: needs 6 &lt; 8 &lt; 3, fails, so it returns False.",
                        "Node 5: its right child is not a BST, so it returns False.",
                        "The best BST is the subtree 4 → 3: <strong>7</strong>.",
                    ],
                    [
                        "The tree: −4 → (−2, −5).",
                        "Leaf −2: BST with sum −2; best stays 0. Leaf −5: sum −5; best stays 0.",
                        "Node −4: needs −2 &lt; −4, fails.",
                        "Every BST sum is negative, so the empty BST wins: <strong>0</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does an empty child return min = INF and max = −INF?",
                     "Those values make <code>lmax &lt; node.val &lt; rmin</code> automatically true on the empty side, so a leaf or one-child node needs no special case."],
                    ["Why is <code>best</code> initialised to 0 rather than −inf?",
                     "The problem counts the empty tree as a BST with sum 0, so the answer is never negative."],
                    ["Why not validate every subtree separately?",
                     "That repeats work: each node would be checked once per ancestor, O(n²) on a chain. Passing summaries up makes it O(n)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ recover BST
    "recover-bst": {
        "examples": [
            {"setup": "t = build([3, 1, 4, None, None, 2])\nrecover_tree(t)", "call": "level_order(t)", "expect": "[2, 1, 4, None, None, 3]"},
            {"setup": "t = build([1, 3, None, None, 2])\nrecover_tree(t)", "call": "level_order(t)", "expect": "[3, 1, None, None, 2]"},
        ],
        "approaches": {
            "Inorder, find the inversions": {
                "idea": [
                    "The inorder sequence of a BST is sorted. Swapping two values creates one or two <strong>inversions</strong>: places where a value is bigger than the one after it.",
                    "The first misplaced node is the larger value of the first inversion; the second is the smaller value of the last inversion.",
                    "If the swapped values were neighbours in inorder there is just one inversion, and it contains both nodes.",
                ],
                "steps": [
                    "Walk the tree in inorder, keeping <code>prev</code>, the previously visited node.",
                    "When <code>prev.val &gt; node.val</code>: if <code>first</code> is unset, set <code>first = prev</code>; in every case set <code>second = node</code>.",
                    "Set <code>prev = node</code> and continue.",
                    "After the walk, swap <code>first.val</code> and <code>second.val</code>.",
                ],
                "why": [
                    "Moving a large value earlier makes it bigger than its successor, and moving a small value later makes it smaller than its predecessor, so the two nodes sit at the outer ends of the inversions.",
                    "Overwriting <code>second</code> at each inversion handles both the one-inversion and two-inversion cases with the same code.",
                    "One inorder pass: <strong>O(n)</strong> time; the recursion stack gives <strong>O(h)</strong> space. Only values are swapped, so the shape is unchanged.",
                ],
                "dry": [
                    [
                        "The tree: 3 → (1, 4), 4 → (2, None). Inorder: 1, 3, 2, 4.",
                        "1 → 3 is fine. 3 → 2 is an inversion: first = 3, second = 2.",
                        "2 → 4 is fine.",
                        "Swap 3 and 2: <strong>[2, 1, 4, None, None, 3]</strong>.",
                    ],
                    [
                        "The tree: 1 → (3, None), 3 → (None, 2). Inorder: 3, 2, 1.",
                        "3 → 2: first inversion, first = 3, second = 2.",
                        "2 → 1: second inversion, second = 1.",
                        "Swap 3 and 1: <strong>[3, 1, None, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>second</code> be set at the first inversion too?",
                     "If the swapped nodes are inorder neighbours, there is only one inversion. Setting <code>second</code> there is the only chance to record the smaller node."],
                    ["Why swap values instead of relinking nodes?",
                     "Values are all that is wrong; the shape is correct. Swapping two integers is far simpler than rewiring parents and children."],
                    ["Can this fix more than two swapped nodes?",
                     "No. It relies on exactly one swap. With more misplaced values the inversions no longer identify the culprits."],
                ],
            },
            "Morris inorder": {
                "idea": [
                    "Same inversion logic, but the inorder walk uses Morris threading to avoid a stack: before going left, link the rightmost node of the left subtree back to the current node.",
                    "Each node is \"visited\" (checked against <code>prev</code>) either when it has no left child or when its thread is found and removed.",
                ],
                "steps": [
                    "<code>visit(cur)</code> does the inversion check and updates <code>prev</code>, exactly as before.",
                    "If <code>node.left</code> is <code>None</code>, visit it and go right.",
                    "Otherwise find <code>pred</code>, the rightmost node of the left subtree, stopping if <code>pred.right</code> already points to <code>node</code>.",
                    "If <code>pred.right</code> is empty, set the thread <code>pred.right = node</code> and go left.",
                    "If it points to <code>node</code>, remove it, visit <code>node</code>, and go right.",
                    "After the loop, swap <code>first.val</code> and <code>second.val</code>.",
                ],
                "why": [
                    "The threads return the walk to each node after its left subtree, giving exact inorder order, so the inversion logic sees the same sequence.",
                    "Each edge is walked a constant number of times while finding predecessors: <strong>O(n)</strong> time.",
                    "No stack or recursion: <strong>O(1)</strong> extra space, the follow-up the problem asks for. All threads are removed by the end.",
                ],
                "dry": [
                    [
                        "node 3: pred is 1; thread 1.right = 3, go to 1. Node 1 has no left: visit 1, follow the thread to 3.",
                        "node 3: thread found, remove it, visit 3 (1 &lt; 3), go to 4.",
                        "node 4: pred is 2; thread 2.right = 4, go to 2. Visit 2: 3 &gt; 2, first = 3, second = 2. Follow the thread to 4.",
                        "node 4: remove the thread, visit 4, go right to None. Swap 3 and 2.",
                        "The tree is <strong>[2, 1, 4, None, None, 3]</strong>.",
                    ],
                    [
                        "node 1: pred is 2 (via 3 → 2); thread 2.right = 1, go to 3.",
                        "Node 3 has no left: visit 3, go right to 2. Node 2 has no left: visit 2, inversion: first = 3, second = 2. Follow the thread to 1.",
                        "node 1: thread found, remove it, visit 1: 2 &gt; 1, second = 1. Go right to None.",
                        "Swap 3 and 1: <strong>[3, 1, None, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the predecessor search stop at <code>pred.right is node</code>?",
                     "On the second arrival the thread already exists; following it would loop back to <code>node</code> forever."],
                    ["Is it safe to swap values while threads exist?",
                     "The swap happens after the loop, when all threads are removed. Swapping values never affects threads anyway, since they are pointers."],
                    ["Is Morris worth it in an interview?",
                     "Only when O(1) space is required, as in this problem's follow-up. It is easy to get wrong, so start with the recursive version."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ AVL tree
    "implement-avl-tree": {
        "examples": [
            {"setup": "t = AVLTree()\nfor k in [30, 10, 20]:\n    t.insert(k)",
             "call": "(t.inorder(), t.root.key, t.root.height)", "expect": "([10, 20, 30], 20, 2)"},
            {"setup": "t = AVLTree()\nfor k in [20, 10, 30, 5]:\n    t.insert(k)\nt.delete(30)",
             "call": "(t.inorder(), t.root.key, t.root.height)", "expect": "([5, 10, 20], 10, 2)"},
        ],
        "approaches": {
            "Recursive insert and delete with rebalance on the way up": {
                "idea": [
                    "An AVL tree is a BST where every node's two subtree heights differ by at most 1. Each node stores its <code>height</code> so this can be checked in O(1).",
                    "Insert and delete work like a plain BST; on the way back up, each ancestor updates its height and, if its <strong>balance factor</strong> reaches ±2, fixes itself with one or two rotations.",
                    "Four shapes need fixing: LL and RR take a single rotation, LR and RL first rotate the child to turn them into LL or RR.",
                ],
                "steps": [
                    "<code>update(n)</code> sets <code>n.height = 1 + max(height(n.left), height(n.right))</code>; <code>balance_factor</code> is left height minus right height.",
                    "<code>rotate_right(y)</code> lifts <code>y.left</code> above <code>y</code>; <code>rotate_left</code> is the mirror. Each updates the lower node first, then the new top.",
                    "<code>rebalance(n)</code>: update, then if <code>bf &gt; 1</code> (left heavy) rotate the left child left when it leans right (LR), then rotate <code>n</code> right; the mirror for <code>bf &lt; -1</code>.",
                    "<code>_insert</code> recurses into the correct side, ignores duplicates, and returns <code>rebalance(n)</code>.",
                    "<code>_delete</code> removes like a BST (successor copy for two children) and also returns <code>rebalance(n)</code>.",
                ],
                "why": [
                    "Rotations preserve inorder order and restore the height difference to at most 1 at the node, and every ancestor on the changed path is rebalanced as the recursion unwinds.",
                    "An AVL tree of height h has at least F(h + 2) − 1 nodes (Fibonacci), so h ≤ about 1.44 log₂ n and every operation is <strong>O(log n)</strong>.",
                    "The recursion follows one path: <strong>O(log n)</strong> stack space.",
                ],
                "dry": [
                    [
                        "Insert 30, then 10 on its left. Insert 20: it goes 30 → 10 → right.",
                        "Rebalance 10: height 2, bf −1, fine.",
                        "Rebalance 30: height 3, bf +2 (left heavy) and its left child 10 leans right (bf −1): the LR case.",
                        "Rotate 10 left (20 above 10), then rotate 30 right (20 above 30).",
                        "Root 20 with children 10 and 30, height 2: <strong>([10, 20, 30], 20, 2)</strong>.",
                    ],
                    [
                        "After the inserts the tree is 20 → (10, 30), 10 → (5). Delete 30: it is a leaf, so it returns None.",
                        "Rebalance 20: left height 2, right height 0, bf +2.",
                        "Its left child 10 has bf +1 (not negative), so it is LL: one right rotation at 20.",
                        "10 becomes the root with children 5 and 20; heights update to 1 and 2.",
                        "The result is <strong>([5, 10, 20], 10, 2)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why update the lower node before the upper one in a rotation?",
                     "The new top's height depends on the old top's height, which has just become its child. Updating in the other order would use a stale value."],
                    ["Why <code>balance_factor(n.left) &lt; 0</code> and not <code>&lt;= 0</code> for the double rotation?",
                     "A child with balance 0 can only occur after a delete, and a single rotation already fixes it. Using a double rotation there would leave the tree unbalanced."],
                    ["How many rotations can one operation need?",
                     "Insert needs at most one single or double rotation. Delete can need one at every level on the way up, so O(log n) rotations."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ left-leaning red-black tree
    "implement-red-black-tree": {
        "examples": [
            {"setup": "t = RedBlackTree()\nfor k in [1, 2, 3, 4]:\n    t.insert(k)",
             "call": "(t.inorder(), t.root.key, is_red(t.root.right.left))", "expect": "([1, 2, 3, 4], 2, True)"},
            {"setup": "t = RedBlackTree()\nfor k in [1, 2, 3]:\n    t.insert(k)\nt.delete(1)",
             "call": "(t.inorder(), t.root.key, is_red(t.root.left))", "expect": "([2, 3], 3, True)"},
        ],
        "approaches": {
            "LLRB: rotate and flip on the way up": {
                "idea": [
                    "A left-leaning red-black tree encodes a 2-3 tree as a BST: a <strong>red</strong> link glues a node to its parent to form a 3-node, and red links may only lean left.",
                    "Rules: no right-leaning red link, no two reds in a row, and every path from the root to an empty link has the same number of black links. Those rules keep the height under 2 log₂ n.",
                    "Inserts add a red node at the bottom and repair the rules on the way up with three local fixes; deletes push a red link down ahead of the search so the node removed is never a lone black node.",
                ],
                "steps": [
                    "<code>fix_up(h)</code>: rotate left if the right link is red and the left is not; rotate right if the left link and its left link are both red; flip colours if both children are red.",
                    "<code>_insert</code> places a new red <code>RBNode</code> at the bottom like a BST and calls <code>fix_up</code> on every node on the way back; <code>insert</code> then blackens the root.",
                    "<code>delete</code> first reddens the root if both its children are black, so there is a red link to push down.",
                    "Going left, <code>move_red_left</code> borrows from the sibling when the left path has no red; going right, a red left link is rotated right and <code>move_red_right</code> is used.",
                    "When the key is found, it is replaced by its successor and <code>_delete_min</code> removes the successor; every frame calls <code>fix_up</code>.",
                ],
                "why": [
                    "Rotations and colour flips never change inorder order or any path's black count, so the tree stays a BST with perfect black balance after every step.",
                    "With equal black heights and no two reds in a row, the longest path is at most twice the shortest: height ≤ 2 log₂ n, so each operation is <strong>O(log n)</strong>.",
                    "The recursion follows one root-to-leaf path: <strong>O(log n)</strong> space.",
                ],
                "dry": [
                    [
                        "Insert 1: a red node, then the root is made black.",
                        "Insert 2: red on the right of 1. fix_up rotates left: 2 is black on top, 1 is a red left child.",
                        "Insert 3: red right of 2, so 2 has two red children. fix_up flips colours; the root is re-blackened: 2 → (1, 3), all black.",
                        "Insert 4: red right of 3. fix_up at 3 rotates left: 4 is black, 3 hangs red on its left.",
                        "The result is <strong>([1, 2, 3, 4], 2, True)</strong>: the red node 3 is the root's right child's left child.",
                    ],
                    [
                        "After the inserts: 2 → (1, 3), all black. Both root children are black, so the root is made red.",
                        "1 &lt; 2 and the left path has no red, so move_red_left flips colours: 2 black, 1 and 3 red.",
                        "At 1: key found with no right child, so it returns None and 2.left becomes empty.",
                        "fix_up(2): right link red, left not, so rotate left: 3 is black on top with 2 red on its left.",
                        "The result is <strong>([2, 3], 3, True)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must red links lean left?",
                     "It removes symmetric cases: each 3-node has only one representation, so insert and delete need far fewer cases than a classic red-black tree."],
                    ["Why does <code>flip_colors</code> toggle rather than set colours?",
                     "Insertion uses it to split a 4-node (children black, parent red) and deletion uses it to combine nodes (the reverse). Toggling serves both."],
                    ["Why check <code>key not in self</code> before deleting?",
                     "The descent assumes the key exists when it reaches the bottom; a missing key would make it read children of an empty link. Checking first avoids that."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ treap
    "implement-treap": {
        "examples": [
            {"setup": "t = Treap(seed=1)\nfor k in [5, 2, 8, 1, 9]:\n    t.insert(k)\nt.delete(2)",
             "call": "(t.inorder(), 2 in t, 8 in t)", "expect": "([1, 5, 8, 9], False, True)"},
            {"setup": "t = Treap(seed=0)\nfor k in [3, 1, 3, 2]:\n    t.insert(k)\nt.delete(3)",
             "call": "(t.inorder(), 3 in t, t.root.key)", "expect": "([1, 2], False, 2)"},
        ],
        "approaches": {
            "Recursive treap with rotations": {
                "idea": [
                    "A treap is a BST by <code>key</code> and a min-heap by a random <code>prio</code> at the same time.",
                    "For distinct keys and priorities there is exactly one such tree, and it is the BST you would get by inserting keys in increasing priority order: a random insertion order, so the expected height is O(log n).",
                    "Rotations keep the BST order while moving a node up or down to repair heap order.",
                ],
                "steps": [
                    "<code>_insert</code> places a new <code>TreapNode</code> with a random priority at the bottom like a BST; duplicates are ignored.",
                    "On the way up, if the child just inserted into has a smaller <code>prio</code> than <code>n</code>, rotate it above <code>n</code> (<code>rotate_right</code> for a left child, <code>rotate_left</code> for a right child).",
                    "<code>_delete</code> searches for the key. A node with one or no children is replaced by its child.",
                    "A node with two children is rotated down towards the child with the smaller priority, then the deletion continues in the subtree it moved into.",
                    "<code>__contains__</code> is a plain BST search, and <code>inorder</code> lists keys in sorted order.",
                ],
                "why": [
                    "Each rotation fixes the heap order between one parent–child pair without breaking BST order, and rotating the smaller-priority child up keeps the heap valid on the deletion path.",
                    "With random priorities the expected depth of any node is O(log n), so insert, delete and search are <strong>O(log n) expected</strong>.",
                    "The recursion follows one path: <strong>O(log n) expected</strong> stack space.",
                ],
                "dry": [
                    [
                        "With seed 1 the priorities are 5: 0.134, 2: 0.847, 8: 0.764, 1: 0.255, 9: 0.495.",
                        "5 is the root; 2 and 8 hang below it with larger priorities, so no rotation.",
                        "1 goes left of 2, but 0.255 &lt; 0.847, so it rotates up: 1 with 2 as its right child.",
                        "9 goes right of 8 and 0.495 &lt; 0.764, so it rotates up: 9 with 8 on its left. Delete 2: a leaf, removed.",
                        "Tree 5 → (1, 9), 9 → (8): <strong>([1, 5, 8, 9], False, True)</strong>.",
                    ],
                    [
                        "With seed 0: 3 gets 0.844 and becomes the root. 1 gets 0.758, goes left, and rotates above 3.",
                        "The second 3 finds an equal key and returns without drawing a priority.",
                        "2 gets 0.421: inserted left of 3, rotates above 3, then above 1. Tree 2 → (1, 3).",
                        "Delete 3: it is a leaf, so it is removed. The tree is 2 → (1).",
                        "The result is <strong>([1, 2], False, 2)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the shape unique for given priorities?",
                     "The node with the smallest priority must be the root (heap order), the BST order then splits the rest into left and right, and the same argument repeats in each part."],
                    ["Why does delete rotate towards the child with the <em>smaller</em> priority?",
                     "That child becomes the parent of the other one, so it must have the smaller priority to keep the heap order."],
                    ["How do splay trees and B-trees compare?",
                     "Splay trees move each accessed key to the root and give O(log n) amortised bounds without storing extra data. B-trees keep many keys per node to cut disk reads, which is why databases use them."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max depth of N-ary tree
    "max-depth-n-ary": {
        "examples": [
            {"call": "max_depth(build_nary([1, None, 3, 2, 4, None, 5, 6]))", "expect": "3"},
            {"call": "max_depth(build_nary([1]))", "expect": "1"},
        ],
        "approaches": {
            "Recursive over children": {
                "idea": [
                    "A tree's depth is one more than the deepest of its children's depths; a leaf has depth 1.",
                    "With N children instead of two, take the maximum over the list of children.",
                ],
                "steps": [
                    "If <code>root</code> is <code>None</code>, return 0.",
                    "Compute <code>max_depth(c)</code> for every child <code>c</code>.",
                    "Take the maximum, using <code>default=0</code> so a leaf with no children works.",
                    "Return 1 plus that maximum.",
                ],
                "why": [
                    "The deepest path from a node goes through one of its children, so the formula is correct by induction.",
                    "Each node is visited once: <strong>O(n)</strong> time.",
                    "The recursion depth equals the tree height: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "The tree: 1 → (3, 2, 4), 3 → (5, 6).",
                        "Leaves 5, 6, 2, 4 have no children: depth 1 each.",
                        "Node 3: 1 + max(1, 1) = 2. Node 1: 1 + max(2, 1, 1) = 3.",
                        "The answer is <strong>3</strong>.",
                    ],
                    [
                        "A single node with an empty children list.",
                        "max over an empty generator falls back to the default 0.",
                        "The answer is 1 + 0 = <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["What does <code>default=0</code> protect against?",
                     "<code>max</code> of an empty sequence raises ValueError. Every leaf has an empty children list, so without the default the code would crash on the first leaf."],
                    ["Why a generator inside <code>max</code>?",
                     "It avoids building a list of depths; <code>max</code> consumes the values one by one."],
                    ["Is depth counted in nodes or edges?",
                     "In nodes, as LeetCode defines it: a single node has depth 1."],
                ],
            },
            "BFS counting levels": {
                "idea": [
                    "Process the tree one level at a time; the depth is the number of levels.",
                    "Each new level is simply all children of the nodes in the current level.",
                ],
                "steps": [
                    "Start with <code>depth = 0</code> and <code>level = [root]</code> (or empty for no tree).",
                    "While <code>level</code> is non-empty, add 1 to <code>depth</code>.",
                    "Replace <code>level</code> with every child of every node in it.",
                    "Return <code>depth</code> when a level comes out empty.",
                ],
                "why": [
                    "Level k holds exactly the nodes at depth k, so the loop runs once per level and counts them.",
                    "Each node appears in one level: <strong>O(n)</strong> time.",
                    "Only one level is stored at a time: <strong>O(w)</strong> space, where w is the widest level.",
                ],
                "dry": [
                    [
                        "level = [1]: depth 1. Next level [3, 2, 4].",
                        "depth 2. Next level: children of 3 only, [5, 6].",
                        "depth 3. Next level is empty.",
                        "The answer is <strong>3</strong>.",
                    ],
                    [
                        "level = [1]: depth 1.",
                        "Node 1 has no children, so the next level is empty.",
                        "The answer is <strong>1</strong>.",
                    ],
                ],
                "faq": [
                    ["When is BFS better than recursion here?",
                     "On very deep, narrow trees, where recursion would hit Python's limit. On very wide trees the level list gets large instead."],
                    ["Why a list rather than a deque?",
                     "The whole level is replaced at once, never popped from the front, so a list comprehension is enough."],
                    ["How is the empty tree handled?",
                     "<code>level</code> starts empty, the loop never runs, and the depth is 0."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ N-ary preorder
    "n-ary-preorder": {
        "examples": [
            {"call": "preorder(build_nary([1, None, 3, 2, 4, None, 5, 6]))", "expect": "[1, 3, 5, 6, 2, 4]"},
            {"call": "preorder(build_nary([1, None, 2, 3, None, 4, None, 5]))", "expect": "[1, 2, 4, 3, 5]"},
        ],
        "approaches": {
            "Iterative, push children reversed": {
                "idea": [
                    "Preorder visits a node, then each child subtree from left to right.",
                    "With a stack, the last item pushed is the first popped, so pushing the children in reverse order makes the leftmost child come out next.",
                ],
                "steps": [
                    "Start with <code>stack = [root]</code> (empty for no tree) and <code>out = []</code>.",
                    "Pop a node and append its value to <code>out</code>.",
                    "Push <code>reversed(node.children)</code> onto the stack.",
                    "Repeat until the stack is empty, then return <code>out</code>.",
                ],
                "why": [
                    "A node's whole subtree is processed before its next sibling is popped, because the subtree's nodes are pushed above that sibling.",
                    "Each node is pushed and popped once: <strong>O(n)</strong> time.",
                    "Pending siblings at every level can sit on the stack together: <strong>O(n)</strong> space in the worst case, as listed.",
                ],
                "dry": [
                    [
                        "Pop 1, out [1]. Push 4, 2, 3: stack [4, 2, 3].",
                        "Pop 3, out [1, 3]. Push 6, 5: stack [4, 2, 6, 5].",
                        "Pop 5, then 6, then 2, then 4.",
                        "The order is <strong>[1, 3, 5, 6, 2, 4]</strong>.",
                    ],
                    [
                        "The tree: 1 → (2, 3), 2 → (4), 3 → (5).",
                        "Pop 1, push 3, 2. Pop 2, push 4: stack [3, 4].",
                        "Pop 4. Pop 3, push 5. Pop 5.",
                        "The order is <strong>[1, 2, 4, 3, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["What goes wrong without <code>reversed</code>?",
                     "The rightmost child would be popped first, giving root, then children right to left: a mirrored preorder."],
                    ["Why is space O(n) and not O(h)?",
                     "A node with many children pushes them all at once. A root with n − 1 children puts them all on the stack together."],
                    ["Does <code>reversed</code> copy the list?",
                     "No, it returns an iterator over the original list, and <code>extend</code> consumes it."],
                ],
            },
            "Recursive": {
                "idea": [
                    "Write the definition directly: record the node, then recurse into each child in order.",
                    "A shared <code>out</code> list collects values as they are visited.",
                ],
                "steps": [
                    "Create <code>out = []</code>.",
                    "<code>walk(node)</code> returns for <code>None</code>; otherwise appends <code>node.val</code>.",
                    "Then it calls <code>walk(c)</code> for each child <code>c</code> from left to right.",
                    "Call <code>walk(root)</code> and return <code>out</code>.",
                ],
                "why": [
                    "Values are appended when a node is first reached, before any of its descendants, which is preorder.",
                    "Each node is visited once: <strong>O(n)</strong> time.",
                    "The call stack is as deep as the tree: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "walk(1): out [1]. walk(3): out [1, 3]; walk(5), walk(6): out [1, 3, 5, 6].",
                        "walk(2): out [..., 2]. walk(4): out [..., 4].",
                        "The order is <strong>[1, 3, 5, 6, 2, 4]</strong>.",
                    ],
                    [
                        "walk(1): out [1]. walk(2): out [1, 2]; walk(4): out [1, 2, 4].",
                        "walk(3): out [1, 2, 4, 3]; walk(5): out [1, 2, 4, 3, 5].",
                        "The order is <strong>[1, 2, 4, 3, 5]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>out</code> shared instead of returned and concatenated?",
                     "Concatenating lists at every node copies values repeatedly and can cost O(n²) on a deep tree. Appending to one list is O(1) per node."],
                    ["Does <code>walk</code> need <code>nonlocal out</code>?",
                     "No. It only calls <code>out.append</code>, which mutates the list without rebinding the name."],
                    ["When would the iterative version be needed?",
                     "When the tree can be deeper than Python's recursion limit (about 1000)."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ N-ary postorder
    "n-ary-postorder": {
        "examples": [
            {"call": "postorder(build_nary([1, None, 3, 2, 4, None, 5, 6]))", "expect": "[5, 6, 3, 2, 4, 1]"},
            {"call": "postorder(build_nary([1, None, 2, 3, None, 4, None, 5]))", "expect": "[4, 2, 5, 3, 1]"},
        ],
        "approaches": {
            "Reversed root-right-to-left preorder": {
                "idea": [
                    "Postorder is children left to right, then the node. Reversed, that is: node, then children right to left.",
                    "That reversed order is an easy preorder-style stack walk, so produce it and reverse the list at the end.",
                ],
                "steps": [
                    "Start with <code>stack = [root]</code> (empty for no tree).",
                    "Pop a node and append its value to <code>out</code>.",
                    "Push the children in their normal order, so the last child is popped first.",
                    "When the stack is empty, return <code>out[::-1]</code>.",
                ],
                "why": [
                    "The walk produces node, then subtrees from right to left; reversing that sequence gives subtrees left to right, then node, which is postorder.",
                    "Each node is pushed and popped once, plus one reversal: <strong>O(n)</strong> time.",
                    "<code>out</code> and the stack can both hold O(n) items: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pop 1, push 3, 2, 4. Pop 4, then 2.",
                        "Pop 3, push 5, 6. Pop 6, then 5.",
                        "out = [1, 4, 2, 3, 6, 5].",
                        "Reversed: <strong>[5, 6, 3, 2, 4, 1]</strong>.",
                    ],
                    [
                        "Pop 1, push 2, 3. Pop 3, push 5. Pop 5.",
                        "Pop 2, push 4. Pop 4.",
                        "out = [1, 3, 5, 2, 4], reversed: <strong>[4, 2, 5, 3, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not push children reversed as in preorder?",
                     "Then the walk would be node, children left to right, and reversing it would give children right to left before the node: the wrong order."],
                    ["Isn't the final reversal extra work?",
                     "It is one O(n) pass, which does not change the overall bound and avoids tracking which children were already visited."],
                    ["Does this trick work for binary trees too?",
                     "Yes: a node, right, left walk reversed is the binary postorder, a common way to write it with one stack."],
                ],
            },
            "Recursive": {
                "idea": [
                    "Recurse into every child first, then record the node.",
                    "The same shape as preorder with the append moved after the loop.",
                ],
                "steps": [
                    "Create <code>out = []</code>.",
                    "<code>walk(node)</code> returns for <code>None</code>.",
                    "Otherwise call <code>walk(c)</code> for each child in order, then append <code>node.val</code>.",
                    "Call <code>walk(root)</code> and return <code>out</code>.",
                ],
                "why": [
                    "A node is recorded only after all of its descendants, children in order, which is postorder by definition.",
                    "Each node is visited once: <strong>O(n)</strong> time.",
                    "The recursion is as deep as the tree: <strong>O(h)</strong> space.",
                ],
                "dry": [
                    [
                        "walk(1) → walk(3) → walk(5) appends 5, walk(6) appends 6; then 3 is appended.",
                        "walk(2) appends 2, walk(4) appends 4.",
                        "Finally 1: <strong>[5, 6, 3, 2, 4, 1]</strong>.",
                    ],
                    [
                        "walk(1) → walk(2) → walk(4) appends 4, then 2.",
                        "walk(3) → walk(5) appends 5, then 3.",
                        "Finally 1: <strong>[4, 2, 5, 3, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Where is postorder useful?",
                     "Whenever a node's answer depends on its children's answers, like deleting a tree, computing sizes or heights."],
                    ["Why <code>if node is None</code> when children lists never contain None?",
                     "It handles the empty tree passed in as <code>root</code>; inside the tree every child is a real node."],
                    ["Can the recursion overflow?",
                     "Yes, past Python's recursion limit on a very deep tree; the stack version avoids that."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ N-ary level order
    "n-ary-level-order": {
        "examples": [
            {"call": "level_order_nary(build_nary([1, None, 3, 2, 4, None, 5, 6]))", "expect": "[[1], [3, 2, 4], [5, 6]]"},
            {"call": "level_order_nary(None)", "expect": "[]"},
        ],
        "approaches": {
            "Level lists": {
                "idea": [
                    "Keep the current level as a list of nodes. Its values form one row of the answer.",
                    "The next level is all children of the current level, in order, so left-to-right order is preserved automatically.",
                ],
                "steps": [
                    "Start with <code>level = [root]</code>, or an empty list for no tree.",
                    "While <code>level</code> is non-empty, append <code>[n.val for n in level]</code> to <code>out</code>.",
                    "Set <code>level</code> to every child of every node in it, in order.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Children of level-k nodes are exactly the level-(k + 1) nodes, and walking parents left to right lists them left to right.",
                    "Each node is placed in one level once: <strong>O(n)</strong> time.",
                    "Two levels exist at most at once: <strong>O(w)</strong> space for the widest level, besides the output.",
                ],
                "dry": [
                    [
                        "level [1]: out [[1]]. Next level [3, 2, 4].",
                        "out gets [3, 2, 4]. Next level: children of 3, [5, 6].",
                        "out gets [5, 6]. The next level is empty.",
                        "The answer is <strong>[[1], [3, 2, 4], [5, 6]]</strong>.",
                    ],
                    [
                        "root is None, so level starts empty.",
                        "The loop never runs.",
                        "The answer is <strong>[]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not a deque with a size counter?",
                     "That also works. Rebuilding the level list is simpler in Python and makes the level boundaries explicit."],
                    ["Why <code>[root] if root else []</code>?",
                     "Without the guard the first row would try to read <code>None.val</code> and crash."],
                    ["How would I get bottom-up order?",
                     "Build the same list and reverse it at the end: <code>out[::-1]</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ next right pointers (perfect tree)
    "next-right-pointers": {
        "examples": [
            {"setup": "t = build([1, 2, 3, 4, 5, 6, 7])\nconnect(t)",
             "call": "(find_node(t, 2).next.val, find_node(t, 5).next.val, find_node(t, 7).next)", "expect": "(3, 6, None)"},
            {"setup": "t = build([1, 2, 3])\nconnect(t)",
             "call": "(t.next, find_node(t, 2).next.val, find_node(t, 3).next)", "expect": "(None, 3, None)"},
        ],
        "approaches": {
            "Use the level above as a linked list": {
                "idea": [
                    "Once a level is linked by <code>next</code> pointers, it can be walked like a linked list without a queue.",
                    "While walking one level, wire up the level below: a node's left child points to its right child, and its right child points to the left child of <code>node.next</code>.",
                    "The tree is perfect, so every internal node has both children and those two rules cover every link.",
                ],
                "steps": [
                    "Start with <code>leftmost = root</code>.",
                    "While <code>leftmost</code> has a left child (there is a level below), walk <code>node</code> along the level from <code>leftmost</code>.",
                    "Set <code>node.left.next = node.right</code>.",
                    "If <code>node.next</code> exists, set <code>node.right.next = node.next.left</code>, crossing the gap between parents.",
                    "Move <code>node = node.next</code>; when the level ends, move <code>leftmost = leftmost.left</code>.",
                ],
                "why": [
                    "Two neighbours on a level are either siblings (handled by the first rule) or the right child and left child of neighbouring parents (handled by the second), so every link is made.",
                    "Each node is visited once as a parent: <strong>O(n)</strong> time.",
                    "Only <code>leftmost</code> and <code>node</code> are stored: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "leftmost = 1: set 2.next = 3. 1.next is None, so the level ends.",
                        "leftmost = 2: set 4.next = 5, and 5.next = 2.next.left = 6.",
                        "node = 3: set 6.next = 7; 3.next is None.",
                        "leftmost = 4 has no left child, so stop. The last node of each level keeps next = None.",
                        "The result is <strong>(3, 6, None)</strong>.",
                    ],
                    [
                        "leftmost = 1: set 2.next = 3. The root has no right neighbour.",
                        "leftmost = 2 has no children, so stop.",
                        "The root's next stays None and so does 3's: <strong>(None, 3, None)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the loop condition <code>leftmost.left is not None</code>?",
                     "The loop links the level below <code>leftmost</code>. When there is no level below, there is nothing left to do."],
                    ["Why does this need a perfect tree?",
                     "It assumes every node on a non-last level has both children. Missing children break the two rules; the problem II version handles that."],
                    ["Where does the last node's <code>next = None</code> come from?",
                     "From the default: <code>TreeNode.next</code> is <code>None</code> and the code never assigns the last node of a level."],
                ],
            },
            "BFS, link within each level": {
                "idea": [
                    "Build each level as a list and link consecutive nodes with <code>next</code>.",
                    "It is the standard level-order traversal, plus one linking pass per level.",
                ],
                "steps": [
                    "Start with <code>level = [root]</code> (empty for no tree).",
                    "For each consecutive pair <code>a, b</code> in the level, set <code>a.next = b</code>.",
                    "Build the next level from the non-<code>None</code> children, left to right.",
                    "Repeat until the level is empty, then return <code>root</code>.",
                ],
                "why": [
                    "The level list holds the nodes of one depth in left-to-right order, so linking consecutive entries is exactly what is asked.",
                    "Each node is linked and expanded once: <strong>O(n)</strong> time.",
                    "The level list holds up to the widest level: <strong>O(w)</strong> space, about n/2 for the last level of a perfect tree.",
                ],
                "dry": [
                    [
                        "level [1]: nothing to link.",
                        "level [2, 3]: 2.next = 3.",
                        "level [4, 5, 6, 7]: 4 → 5 → 6 → 7.",
                        "The next level is empty. The result is <strong>(3, 6, None)</strong>.",
                    ],
                    [
                        "level [1]: nothing to link.",
                        "level [2, 3]: 2.next = 3.",
                        "The next level is empty: <strong>(None, 3, None)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>zip(level, level[1:])</code>?",
                     "It yields each pair of neighbours, so the last node is never given a <code>next</code> and keeps <code>None</code>."],
                    ["Does this need the tree to be perfect?",
                     "No. It skips missing children, so it also solves problem II, but it uses O(w) space instead of O(1)."],
                    ["Why mention it if the O(1) version exists?",
                     "It is the version most people write first and the easiest to get right; the follow-up asks for constant space."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ next right pointers II (any tree)
    "next-right-pointers-ii": {
        "examples": [
            {"setup": "t = build([1, 2, 3, 4, 5, None, 7])\nconnect(t)",
             "call": "(find_node(t, 4).next.val, find_node(t, 5).next.val, find_node(t, 7).next)", "expect": "(5, 7, None)"},
            {"setup": "t = build([1, 2, 3, 4, None, None, 5])\nconnect(t)",
             "call": "(find_node(t, 4).next.val, find_node(t, 3).next)", "expect": "(5, None)"},
        ],
        "approaches": {
            "Dummy head for the level below": {
                "idea": [
                    "In an arbitrary tree, children can be missing anywhere, so the perfect-tree rules do not work.",
                    "Instead, walk the current level through its <code>next</code> pointers and build the level below as a linked list, appending each child found to a <code>tail</code>.",
                    "A <code>dummy</code> node in front of that list means the first child needs no special case, and <code>dummy.next</code> is where the next level starts.",
                ],
                "steps": [
                    "Start with <code>head = root</code>.",
                    "For each level, create <code>dummy = tail = TreeNode(0)</code> and walk <code>node</code> from <code>head</code> along <code>next</code>.",
                    "For each non-<code>None</code> child of <code>node</code> (left, then right), set <code>tail.next = child</code> and <code>tail = child</code>.",
                    "When the level ends, set <code>head = dummy.next</code>, the first node of the level below (or <code>None</code>).",
                    "Stop when <code>head</code> is <code>None</code> and return <code>root</code>.",
                ],
                "why": [
                    "The current level is visited left to right and each one's children are taken left to right, so the level below is appended in order and every neighbour pair is linked.",
                    "Each node is appended once and visited once as a parent: <strong>O(n)</strong> time.",
                    "Only <code>head</code>, <code>node</code>, <code>dummy</code> and <code>tail</code> are used: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "head = 1: append 2 then 3, giving 2 → 3. head = 2.",
                        "node 2: append 4, then 5 (4 → 5). node 3: left is missing, append 7 (5 → 7).",
                        "head = 4: none of 4, 5, 7 has children, so dummy.next stays None and the loop stops.",
                        "The result is <strong>(5, 7, None)</strong>.",
                    ],
                    [
                        "head = 1: append 2 and 3. head = 2.",
                        "node 2: append 4 (its right is missing). node 3: its left is missing, append 5. So 4.next = 5 across the gap.",
                        "head = 4: no children below, so the loop ends. 3 is last on its level.",
                        "The result is <strong>(5, None)</strong>.",
                    ],
                ],
                "faq": [
                    ["Why a fresh dummy for every level?",
                     "Its <code>next</code> must point to the first child of the new level. Reusing an old dummy would keep the previous level's head when the new level is empty and loop forever."],
                    ["How can a level be walked before it is linked?",
                     "It was linked while the level above it was processed. The root's level is a single node, so it needs no links."],
                    ["Does the dummy's <code>next</code> pointer leak into the tree?",
                     "No. The dummy is never attached to the tree; only real nodes receive <code>next</code> pointers."],
                ],
            },
        },
    },
}
