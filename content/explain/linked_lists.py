"""Write-ups for the Linked Lists topic."""

COPY_SETUP = ("class Node:\n"
              "    def __init__(self, x, next=None, random=None):\n"
              "        self.val, self.next, self.random = int(x), next, random\n"
              "def dump(h):\n"
              "    nodes = []\n"
              "    while h:\n"
              "        nodes.append(h); h = h.next\n"
              "    return [(n.val, nodes.index(n.random) if n.random else None) for n in nodes]\n")

EXPLAIN = {
    # ------------------------------------------------------------------ reverse linked list
    "reverse-linked-list": {
        "examples": [
            {"call": "to_list(reverse_list(build_list([1, 2, 3, 4])))", "expect": "[4, 3, 2, 1]"},
            {"call": "to_list(reverse_list(build_list([7])))", "expect": "[7]"},
        ],
        "approaches": {
            "Copy values to a list, write them back reversed": {
                "idea": [
                    "Leave the links alone and reverse the <em>values</em> instead: the same nodes in the same order, holding their values backwards.",
                    "A Python list makes that easy: read every value into it, then hand them back last-first with <code>pop()</code>.",
                ],
                "steps": [
                    "Start with <code>vals = []</code> and <code>node = head</code>.",
                    "First pass: append each <code>node.val</code> to <code>vals</code> and move <code>node = node.next</code>.",
                    "Reset <code>node = head</code>.",
                    "Second pass: set <code>node.val = vals.pop()</code> for each node, front to back.",
                    "Return the original <code>head</code>, which now holds the last value.",
                ],
                "why": [
                    "<code>pop()</code> removes from the end, so the first node receives the last value, the second node the second-to-last, and so on: the values come out reversed.",
                    "Two passes of n steps each give <strong>O(n)</strong> time; <code>vals</code> holds all n values, so the extra space is <strong>O(n)</strong>.",
                    "It copies data instead of relinking, which interviewers usually rule out: real nodes may carry large payloads or be referenced elsewhere by identity.",
                ],
                "dry": [
                    [
                        "Pass 1 collects vals = [1, 2, 3, 4].",
                        "Pass 2, first node: pop 4. Second node: pop 3.",
                        "Third node: pop 2. Fourth node: pop 1. vals is now empty.",
                        "The same head node is returned and the list reads <strong>[4, 3, 2, 1]</strong>.",
                    ],
                    [
                        "Pass 1 collects vals = [7].",
                        "Pass 2: the only node pops 7 back into itself.",
                        "It returns the same node: <strong>[7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return <code>head</code> and not the last node?",
                     "No link was changed, so the first node is still first; only its value is different. It now holds the old last value."],
                    ["What happens for an empty list?",
                     "Both loops are skipped because <code>head</code> is <code>None</code>, and <code>None</code> is returned, which is the reversed empty list."],
                    ["Is this an acceptable interview answer?",
                     "As a first idea, yes, but it uses O(n) memory and swaps values rather than nodes. Expect to be asked for the pointer version."],
                ],
            },
            "Recursive": {
                "idea": [
                    "Trust the recursion to reverse everything <em>after</em> the head; it returns the new head, the old last node.",
                    "At that point the old second node, <code>head.next</code>, is the tail of the reversed rest, so hook the head on behind it with <code>head.next.next = head</code>.",
                    "Then cut <code>head.next</code>, because the head has become the last node.",
                ],
                "steps": [
                    "Base case: if <code>head</code> is <code>None</code> or <code>head.next</code> is <code>None</code>, the list is already reversed; return <code>head</code>.",
                    "Recurse: <code>new_head = reverse_list(head.next)</code>.",
                    "Point the old next node back: <code>head.next.next = head</code>.",
                    "Cut the forward link: <code>head.next = None</code>.",
                    "Return <code>new_head</code>, unchanged, all the way up.",
                ],
                "why": [
                    "By induction, the call on <code>head.next</code> returns the reversed rest with <code>head.next</code> as its last node; appending <code>head</code> after it reverses one more node.",
                    "Each frame flips exactly one link, so the time is <strong>O(n)</strong>.",
                    "The recursion is n frames deep, so the space is <strong>O(n)</strong> on the call stack; a list of more than about 1000 nodes passes CPython's default recursion limit.",
                ],
                "dry": [
                    [
                        "Calls go down: reverse(1) → reverse(2) → reverse(3) → reverse(4). Node 4 has no next, so it is returned as new_head.",
                        "Frame for 3: 4.next = 3, 3.next = None. From 4 the list reads 4 → 3.",
                        "Frame for 2: 3.next = 2, 2.next = None, giving 4 → 3 → 2.",
                        "Frame for 1: 2.next = 1, 1.next = None, giving 4 → 3 → 2 → 1.",
                        "new_head (4) is passed all the way up: <strong>[4, 3, 2, 1]</strong>.",
                    ],
                    [
                        "reverse(7): <code>head.next</code> is <code>None</code>, so the base case applies.",
                        "No recursion and no link changes happen.",
                        "It returns node 7: <strong>[7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>head.next = None</code>? It gets overwritten anyway, doesn't it?",
                     "Only for nodes that are not first. The original head becomes the tail, and nobody overwrites its <code>next</code>; without the cut, 1 and 2 would point at each other and form a cycle."],
                    ["Why does every frame return the same <code>new_head</code>?",
                     "The new head is the old last node, found once at the deepest call. Upper frames only fix their own link and pass it up unchanged."],
                    ["Why check <code>head.next is None</code> in the base case?",
                     "A one-node list is already reversed, and the line <code>head.next.next</code> needs <code>head.next</code> to exist. Stopping at the last node also makes it the returned new head."],
                ],
            },
            "Iterative with three pointers": {
                "idea": [
                    "Walk the list once, turning each <code>next</code> link around to point backwards.",
                    "<code>prev</code> heads the already-reversed part, <code>cur</code> is the node being flipped, and <code>nxt</code> remembers the rest of the list before the link is overwritten.",
                    "When <code>cur</code> runs off the end, <code>prev</code> is the old last node, the new head.",
                ],
                "steps": [
                    "Set <code>prev = None</code> and <code>cur = head</code>.",
                    "While <code>cur</code> exists, save <code>nxt = cur.next</code>.",
                    "Flip the link: <code>cur.next = prev</code>.",
                    "Advance both: <code>prev, cur = cur, nxt</code>.",
                    "Return <code>prev</code>.",
                ],
                "why": [
                    "After each step, <code>prev</code> heads a correctly reversed prefix and <code>cur</code> heads the untouched rest; when the rest is empty the whole list is reversed.",
                    "Saving <code>nxt</code> first is essential: once <code>cur.next</code> is overwritten, it is the only reference to the rest of the list.",
                    "Each node is visited once with constant work: <strong>O(n)</strong> time and <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "cur = 1: nxt = 2, 1 → None. prev = 1, cur = 2.",
                        "cur = 2: nxt = 3, 2 → 1. prev = 2 (2 → 1), cur = 3.",
                        "cur = 3: nxt = 4, 3 → 2. prev = 3 (3 → 2 → 1), cur = 4.",
                        "cur = 4: nxt = None, 4 → 3. prev = 4, cur = None, so the loop ends.",
                        "Return prev: <strong>[4, 3, 2, 1]</strong>.",
                    ],
                    [
                        "cur = 7: nxt = None, 7 → None (prev was None).",
                        "prev = 7, cur = None, so the loop ends after one step.",
                        "Return prev: <strong>[7]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start <code>prev</code> at <code>None</code>?",
                     "The first node becomes the last, so its <code>next</code> must end up as <code>None</code>. Starting <code>prev</code> there makes the first flip do exactly that."],
                    ["Why return <code>prev</code> and not <code>cur</code>?",
                     "The loop stops when <code>cur</code> is <code>None</code>. The last node processed, the old tail, is held in <code>prev</code>."],
                    ["Can the three updates be written as one tuple assignment?",
                     "Yes: <code>cur.next, prev, cur = prev, cur, cur.next</code> works because the right side is evaluated before any assignment. The order on the left still matters, so the explicit <code>nxt</code> version is easier to get right."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge two sorted lists
    "merge-two-sorted-lists": {
        "examples": [
            {"call": "to_list(merge_two_lists(build_list([1, 4, 7]), build_list([2, 3, 8, 9])))",
             "expect": "[1, 2, 3, 4, 7, 8, 9]"},
            {"call": "to_list(merge_two_lists(build_list([]), build_list([5, 6])))", "expect": "[5, 6]"},
        ],
        "approaches": {
            "Collect, sort, rebuild": {
                "idea": [
                    "Ignore that the inputs are sorted: pour every value into one Python list, sort it, and build a fresh linked list.",
                    "It is short and obviously correct, which makes it a good baseline before the pointer versions.",
                ],
                "steps": [
                    "Start with <code>vals = []</code>.",
                    "For each of the two heads <code>a</code> and <code>b</code>, walk the list and append every <code>node.val</code>.",
                    "Sort the values with <code>sorted(vals)</code>.",
                    "Return <code>build_list(...)</code> of the sorted values, a brand new list.",
                ],
                "why": [
                    "Sorting all m + n values gives exactly the merged order, so the output is correct no matter how the inputs interleave.",
                    "Collecting is O(m + n), but sorting costs <strong>O((m + n) log(m + n))</strong> time; it throws away the fact that the inputs are already sorted.",
                    "<code>vals</code> and the new nodes take <strong>O(m + n)</strong> extra space, and the original nodes are not reused.",
                ],
                "dry": [
                    [
                        "Walk a: vals = [1, 4, 7]. Walk b: vals = [1, 4, 7, 2, 3, 8, 9].",
                        "sorted gives [1, 2, 3, 4, 7, 8, 9].",
                        "build_list creates seven new nodes in that order.",
                        "Result: <strong>[1, 2, 3, 4, 7, 8, 9]</strong>.",
                    ],
                    [
                        "a is <code>None</code>, so its loop does nothing.",
                        "Walk b: vals = [5, 6]. sorted keeps [5, 6].",
                        "build_list makes two new nodes: <strong>[5, 6]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is this slower than the other approaches?",
                     "Sorting is O(k log k) for k values, while merging two sorted lists needs only one comparison per output node."],
                    ["Does it change the input lists?",
                     "No. It only reads them and builds new nodes, which is why it also uses O(m + n) extra memory."],
                    ["What if both lists are empty?",
                     "<code>vals</code> stays empty and <code>build_list([])</code> returns <code>None</code>, the empty list."],
                ],
            },
            "Recursive": {
                "idea": [
                    "The merged list starts with the smaller of the two heads. Everything after it is the merge of what is left.",
                    "So pick the smaller head, let the recursion merge the rest, and attach that result as its <code>next</code>.",
                ],
                "steps": [
                    "If either list is empty, return the other: <code>return a or b</code>.",
                    "If <code>a.val &lt;= b.val</code>, set <code>a.next = merge_two_lists(a.next, b)</code> and return <code>a</code>.",
                    "Otherwise set <code>b.next = merge_two_lists(a, b.next)</code> and return <code>b</code>.",
                    "Each returned node is linked in by the caller one level up.",
                ],
                "why": [
                    "The smaller head is the smallest remaining value overall, because both lists are sorted, so it belongs first; the recursive call correctly merges the rest by induction.",
                    "Using <code>&lt;=</code> takes from <code>a</code> on ties, so equal values keep their original order (a stable merge).",
                    "One call per output node gives <strong>O(m + n)</strong> time, and the recursion depth is up to m + n, so <strong>O(m + n)</strong> stack space.",
                ],
                "dry": [
                    [
                        "1 ≤ 2: keep 1, merge [4, 7] with [2, 3, 8, 9].",
                        "4 &gt; 2: keep 2, then 4 &gt; 3: keep 3, merge [4, 7] with [8, 9].",
                        "4 ≤ 8: keep 4. 7 ≤ 8: keep 7, merge [] with [8, 9].",
                        "a is empty, so [8, 9] is returned as is. On the way up, 7 → 8, 4 → 7, 3 → 4, 2 → 3, 1 → 2.",
                        "Result: <strong>[1, 2, 3, 4, 7, 8, 9]</strong>.",
                    ],
                    [
                        "a is <code>None</code>, so the base case returns <code>a or b</code> = b.",
                        "No node is relinked.",
                        "Result: <strong>[5, 6]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>a or b</code> work as the base case?",
                     "If <code>a</code> is <code>None</code> it is falsy and <code>b</code> is returned; otherwise <code>b</code> must be the empty one and <code>a</code> is returned. Either way the non-empty rest is attached unchanged."],
                    ["Is <code>&lt;</code> instead of <code>&lt;=</code> wrong?",
                     "The values come out the same, but on ties it takes from <code>b</code> first, so equal nodes from <code>a</code> end up after those from <code>b</code>. <code>&lt;=</code> keeps the merge stable."],
                    ["When would this fail in practice?",
                     "On long lists: with more than about 1000 nodes in total the depth passes CPython's default recursion limit. The iterative version avoids that."],
                ],
            },
            "Iterative with a dummy head": {
                "idea": [
                    "Build the result by repeatedly taking the smaller front node and attaching it at the end, like merging two sorted piles of cards.",
                    "A dummy node in front of the result means the first attachment is no special case: <code>tail</code> always has a node to hang the next one on.",
                    "When one list runs out, the rest of the other is already sorted, so attach it in one step.",
                ],
                "steps": [
                    "Create <code>dummy = tail = ListNode()</code>.",
                    "While both <code>a</code> and <code>b</code> exist, attach the smaller front: <code>tail.next, a = a, a.next</code> if <code>a.val &lt;= b.val</code>, else the same with <code>b</code>.",
                    "Move <code>tail = tail.next</code>.",
                    "After the loop, attach the leftover: <code>tail.next = a or b</code>.",
                    "Return <code>dummy.next</code>, skipping the dummy.",
                ],
                "why": [
                    "Every node attached is the smallest remaining one, so the result stays sorted; the leftover list is sorted and all its values are at least the last attached one.",
                    "Each loop step attaches one node with one comparison: <strong>O(m + n)</strong> time.",
                    "Only the dummy and two pointers are added, and the existing nodes are relinked: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "Compare 1 vs 2: take 1. 4 vs 2: take 2. 4 vs 3: take 3.",
                        "4 vs 8: take 4. 7 vs 8: take 7. a is now empty.",
                        "The loop ends and <code>tail.next = b</code> attaches 8 → 9 in one step.",
                        "dummy.next is node 1: <strong>[1, 2, 3, 4, 7, 8, 9]</strong>.",
                    ],
                    [
                        "a is <code>None</code>, so the while loop never runs.",
                        "<code>tail</code> is still the dummy, and <code>tail.next = a or b</code> attaches 5 → 6.",
                        "Return dummy.next: <strong>[5, 6]</strong>.",
                    ],
                ],
                "faq": [
                    ["What does the dummy node save?",
                     "Without it, the first node has to be chosen separately to become the head, and an empty input needs its own check. With it, every node is attached the same way."],
                    ["Is <code>tail.next, a = a, a.next</code> safe?",
                     "Yes. The right side is evaluated first, so <code>a.next</code> is read before anything changes; then <code>tail.next</code> becomes the old <code>a</code> and <code>a</code> moves on."],
                    ["Why not keep looping until both lists are empty?",
                     "Once one list is empty there is nothing to compare; the other list is already sorted and linked, so attaching it whole saves the remaining steps."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ linked list cycle
    "linked-list-cycle": {
        "examples": [
            {"setup": "head = build_list([3, 2, 0, -4])\nhead.next.next.next.next = head.next      # -4 links back to 2",
             "call": "has_cycle(head)", "expect": "True"},
            {"setup": "head = build_list([1, 2, 3])", "call": "has_cycle(head)", "expect": "False"},
        ],
        "approaches": {
            "Hash set of visited nodes": {
                "idea": [
                    "Follow <code>next</code> pointers and remember every node you have stood on.",
                    "If you ever arrive at a node already remembered, the walk has looped: there is a cycle. If you fall off the end, there is none.",
                ],
                "steps": [
                    "Create an empty set <code>seen</code>.",
                    "While <code>head</code> is not <code>None</code>: if <code>head in seen</code>, return <code>True</code>.",
                    "Otherwise add <code>head</code> to <code>seen</code>.",
                    "Move on: <code>head = head.next</code>.",
                    "If the loop ends at <code>None</code>, return <code>False</code>.",
                ],
                "why": [
                    "In a cycle the walk never ends and must revisit the cycle's first node after at most n steps; without a cycle it reaches <code>None</code> after n steps.",
                    "The set stores node objects, compared by identity, so two different nodes with equal values are not confused.",
                    "Each node is added and looked up once: <strong>O(n)</strong> time; the set can hold all n nodes: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Visit 3, 2, 0, -4, adding each to seen.",
                        "-4's next is the node 2.",
                        "Node 2 is already in seen, so it returns <strong>True</strong>.",
                    ],
                    [
                        "Visit 1, 2, 3, adding each to seen.",
                        "3's next is <code>None</code>, so the loop ends.",
                        "No node was seen twice: <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store nodes and not values?",
                     "Values can repeat in a list without any cycle, like [1, 1]. Only returning to the same node object means a loop."],
                    ["Can a node be hashed?",
                     "Yes. <code>ListNode</code> does not define <code>__eq__</code>, so Python hashes it by identity, which is exactly what this needs."],
                    ["When would I prefer this over Floyd?",
                     "When you also want the nodes visited, or the problem is about something else and memory is not a concern. Floyd is the answer when O(1) space is asked for."],
                ],
            },
            "Floyd's tortoise and hare": {
                "idea": [
                    "Send two pointers down the list: <code>slow</code> moves one node per step, <code>fast</code> moves two.",
                    "Without a cycle, <code>fast</code> reaches the end. With a cycle, both end up going round it, and <code>fast</code> gains one node per step, so it must land on <code>slow</code>.",
                ],
                "steps": [
                    "Set <code>slow = fast = head</code>.",
                    "While <code>fast</code> and <code>fast.next</code> exist, move <code>slow = slow.next</code> and <code>fast = fast.next.next</code>.",
                    "If <code>slow is fast</code>, return <code>True</code>.",
                    "If the loop ends, <code>fast</code> hit the end, so return <code>False</code>.",
                ],
                "why": [
                    "Once both are inside a cycle of length c, the gap from <code>fast</code> to <code>slow</code> shrinks by exactly 1 each step, so it reaches 0 within c steps; they cannot jump over each other.",
                    "<code>slow</code> enters the cycle within n steps and they meet within c more, so the time is <strong>O(n)</strong>.",
                    "Only two pointers are stored: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Start: slow = fast = 3.",
                        "Step 1: slow = 2, fast = 0.",
                        "Step 2: slow = 0, fast goes -4 → back to 2.",
                        "Step 3: slow = -4, fast goes 0 → -4. <code>slow is fast</code>, so it returns <strong>True</strong>.",
                    ],
                    [
                        "Start: slow = fast = 1.",
                        "Step 1: slow = 2, fast = 3.",
                        "fast.next is <code>None</code>, so the loop condition fails.",
                        "It returns <strong>False</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check both <code>fast</code> and <code>fast.next</code>?",
                     "<code>fast</code> takes two steps. If <code>fast.next</code> is <code>None</code>, <code>fast.next.next</code> would raise an AttributeError, so both must exist."],
                    ["Why <code>is</code> and not <code>==</code>?",
                     "The question is whether they are on the same node. <code>is</code> compares identity directly; <code>==</code> on nodes without <code>__eq__</code> does the same, but <code>is</code> says what is meant."],
                    ["Could <code>fast</code> jump over <code>slow</code> forever?",
                     "No. Relative to <code>slow</code>, <code>fast</code> moves one node per step, so the gap goes c−1, c−2, …, 0 and never skips zero."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reorder list
    "reorder-list": {
        "examples": [
            {"setup": "head = build_list([1, 2, 3, 4, 5, 6])\nreorder_list(head)", "call": "to_list(head)",
             "expect": "[1, 6, 2, 5, 3, 4]"},
            {"setup": "head = build_list([1, 2, 3, 4, 5])\nreorder_list(head)", "call": "to_list(head)",
             "expect": "[1, 5, 2, 4, 3]"},
        ],
        "approaches": {
            "Array of nodes, relink from both ends": {
                "idea": [
                    "The new order alternates first, last, second, second-to-last, … which needs walking backwards, and a singly linked list cannot do that.",
                    "Put the nodes into a Python list so both ends can be reached by index, then relink them with two indices moving towards each other.",
                ],
                "steps": [
                    "Walk the list and append every node to <code>nodes</code>.",
                    "Set <code>i, j = 0, len(nodes) - 1</code>.",
                    "While <code>i &lt; j</code>: link <code>nodes[i].next = nodes[j]</code> and move <code>i += 1</code>; if now <code>i == j</code>, stop.",
                    "Otherwise link <code>nodes[j].next = nodes[i]</code> and move <code>j -= 1</code>.",
                    "Finally set <code>nodes[i].next = None</code>, since <code>nodes[i]</code> is the new last node.",
                ],
                "why": [
                    "Each pair of links places one node from the front and one from the back, which is exactly the required alternation; the two indices meet at the middle node, which goes last.",
                    "Cutting <code>nodes[i].next</code> matters: that node used to point at its old neighbour, and leaving it would create a cycle.",
                    "One pass to collect and one to relink: <strong>O(n)</strong> time, with <strong>O(n)</strong> space for the array.",
                ],
                "dry": [
                    [
                        "nodes holds 1..6; i = 0, j = 5.",
                        "1 → 6, i = 1; 6 → 2, j = 4.",
                        "2 → 5, i = 2; 5 → 3, j = 3.",
                        "3 → 4, i = 3 = j, so the loop breaks. nodes[3] (4) gets next = None.",
                        "The list reads <strong>[1, 6, 2, 5, 3, 4]</strong>.",
                    ],
                    [
                        "nodes holds 1..5; i = 0, j = 4.",
                        "1 → 5, i = 1; 5 → 2, j = 3.",
                        "2 → 4, i = 2; 4 → 3, j = 2. Now i = j, so the loop ends.",
                        "nodes[2] (3) gets next = None: <strong>[1, 5, 2, 4, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why the <code>if i == j: break</code> in the middle?",
                     "With an even count the indices meet right after a front-to-back link. Linking <code>nodes[j].next = nodes[i]</code> then would make the node point at itself."],
                    ["Why is <code>nodes[i].next = None</code> needed?",
                     "The last node in the new order is a middle node whose old <code>next</code> still points at a node already placed earlier, which would turn the list into a loop."],
                    ["Why the <code>if nodes:</code> guard?",
                     "For an empty list <code>nodes</code> is empty and <code>nodes[0]</code> would raise an IndexError."],
                ],
            },
            "Middle, reverse the second half, merge": {
                "idea": [
                    "The answer interleaves the first half with the second half read backwards.",
                    "So split the list at the middle, reverse the second half in place, and weave the two halves together: three classic linked-list moves.",
                    "Everything is done by relinking, so no array is needed.",
                ],
                "steps": [
                    "Find the middle: move <code>slow</code> one step and <code>fast</code> two while <code>fast.next</code> and <code>fast.next.next</code> exist.",
                    "Cut after the middle: <code>second, slow.next = slow.next, None</code>.",
                    "Reverse <code>second</code> with the usual <code>prev</code> loop; the reversed half starts at <code>prev</code>.",
                    "Weave: save <code>n1, n2 = first.next, second.next</code>, link <code>first.next = second</code> and <code>second.next = n1</code>, then advance <code>first, second = n1, n2</code>.",
                    "Stop when <code>second</code> runs out; the first half is never shorter, so its tail is already correct.",
                ],
                "why": [
                    "The middle loop leaves <code>slow</code> at the end of the first half, which has ⌈n/2⌉ nodes, so the second half has at most as many and the weave never runs out of <code>first</code> nodes.",
                    "Reversing the second half turns \"last, second-to-last, …\" into a forward walk, and weaving places one node from each half alternately, which is the required order.",
                    "Each phase is one pass over at most n nodes: <strong>O(n)</strong> time, and only a few pointers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Middle: slow/fast go 1/1 → 2/3 → 3/5; 5.next.next is None, so slow = 3.",
                        "Cut: first half 1 → 2 → 3, second half 4 → 5 → 6.",
                        "Reverse the second half: 6 → 5 → 4.",
                        "Weave: 1 → 6 → 2, then 2 → 5 → 3, then 3 → 4 (whose next is None).",
                        "The list reads <strong>[1, 6, 2, 5, 3, 4]</strong>.",
                    ],
                    [
                        "Middle: slow/fast go 1/1 → 2/3 → 3/5; 5.next is None, so slow = 3.",
                        "Cut: first half 1 → 2 → 3, second half 4 → 5. Reverse: 5 → 4.",
                        "Weave: 1 → 5 → 2, then 2 → 4 → 3. second is now None, so the weave stops.",
                        "3 still ends the list because of the cut: <strong>[1, 5, 2, 4, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>fast.next and fast.next.next</code> instead of <code>fast and fast.next</code>?",
                     "This version stops <code>slow</code> on the last node of the first half (node 3 of 6), so the first half is the longer one. The other condition would stop it one node later for even lengths."],
                    ["Why is the cut <code>slow.next = None</code> necessary?",
                     "Without it, the first half would still lead into the old second half. After reversing, node 4 would be reachable twice and the result would contain a cycle."],
                    ["Does the function return anything?",
                     "No. The problem asks to reorder in place, so the head stays the same node and only the links change."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ remove nth from end
    "remove-nth-from-end": {
        "examples": [
            {"call": "to_list(remove_nth_from_end(build_list([1, 2, 3, 4, 5]), 2))", "expect": "[1, 2, 3, 5]"},
            {"call": "to_list(remove_nth_from_end(build_list([1, 2]), 2))", "expect": "[2]"},
        ],
        "approaches": {
            "Count, then walk to the predecessor": {
                "idea": [
                    "The n-th node from the end is the <code>(length - n + 1)</code>-th from the front, so count the nodes first.",
                    "To delete a node you need the one before it, and the head has no predecessor, so start from a dummy node in front of the head.",
                ],
                "steps": [
                    "First pass: count the nodes into <code>length</code>.",
                    "Create <code>dummy = ListNode(0, head)</code> and set <code>prev = dummy</code>.",
                    "Move <code>prev</code> forward <code>length - n</code> times; it now sits just before the target.",
                    "Unlink the target: <code>prev.next = prev.next.next</code>.",
                    "Return <code>dummy.next</code>, which is the new head if the old one was removed.",
                ],
                "why": [
                    "From the dummy, <code>length - n</code> steps land on node number <code>length - n</code> (counting the head as 1), which is right before the n-th from the end.",
                    "The dummy makes removing the head the same as removing any other node: <code>prev</code> simply stays on the dummy.",
                    "Two passes over the list: <strong>O(L)</strong> time. Only a few variables: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Pass 1: length = 5.",
                        "prev starts at the dummy and moves 5 − 2 = 3 times: to 1, 2, then 3.",
                        "prev.next is 4; set 3.next = 5.",
                        "Return dummy.next: <strong>[1, 2, 3, 5]</strong>.",
                    ],
                    [
                        "Pass 1: length = 2.",
                        "prev moves 2 − 2 = 0 times, so it stays on the dummy.",
                        "dummy.next = 1.next = 2, which removes the head.",
                        "Return dummy.next: <strong>[2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why return <code>dummy.next</code> and not <code>head</code>?",
                     "If the head itself is removed, <code>head</code> still points at the deleted node. <code>dummy.next</code> always points at the real first node."],
                    ["Why <code>length - n</code> steps and not <code>length - n + 1</code>?",
                     "Starting at the dummy adds one position, so <code>length - n</code> steps reach the node just before the target, which is the one whose link must change."],
                    ["Can <code>prev.next.next</code> fail?",
                     "Not for a valid n (1 ≤ n ≤ length): <code>prev.next</code> is the target and exists; its <code>next</code> may be <code>None</code>, which is fine to assign."],
                ],
            },
            "Array of nodes": {
                "idea": [
                    "Store every node, including a dummy in front, in a Python list; then the predecessor of the target is just an index away.",
                    "The target is n from the end, so its predecessor is n + 1 from the end: <code>nodes[len(nodes) - n - 1]</code>.",
                ],
                "steps": [
                    "Create <code>dummy = ListNode(0, head)</code>.",
                    "Walk from the dummy and append every node, dummy included, to <code>nodes</code>.",
                    "Take <code>prev = nodes[len(nodes) - n - 1]</code>.",
                    "Unlink: <code>prev.next = prev.next.next</code>.",
                    "Return <code>dummy.next</code>.",
                ],
                "why": [
                    "<code>nodes</code> has L + 1 entries; the target is at index <code>L + 1 - n</code>, so its predecessor is at <code>len(nodes) - n - 1</code>, which is the dummy when the head is removed.",
                    "One pass to collect plus O(1) to unlink: <strong>O(L)</strong> time.",
                    "The array stores L + 1 references: <strong>O(L)</strong> space, which the two-pointer version avoids.",
                ],
                "dry": [
                    [
                        "nodes = [dummy, 1, 2, 3, 4, 5], length 6.",
                        "prev = nodes[6 − 2 − 1] = nodes[3], the node 3.",
                        "3.next becomes 5, skipping 4.",
                        "Return dummy.next: <strong>[1, 2, 3, 5]</strong>.",
                    ],
                    [
                        "nodes = [dummy, 1, 2], length 3.",
                        "prev = nodes[3 − 2 − 1] = nodes[0], the dummy.",
                        "dummy.next becomes 2.",
                        "Return dummy.next: <strong>[2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why include the dummy in the array?",
                     "So that removing the head still has a predecessor at a valid index (0). Without it, the index would be -1, which Python reads as the last element."],
                    ["Could I use <code>nodes[-n - 1]</code>?",
                     "Yes, that is the same index written from the end; with the dummy included it never wraps around for a valid n."],
                    ["Is this better than counting?",
                     "It is one pass instead of two but costs O(L) memory, so it is usually not worth it. The gap method gets one pass with O(1) memory."],
                ],
            },
            "One pass with a gap of n": {
                "idea": [
                    "Put two pointers n + 1 nodes apart and move them together. When the front one falls off the end, the back one is exactly one node before the n-th from the end.",
                    "Starting both at a dummy node handles removing the head without a special case.",
                ],
                "steps": [
                    "Create <code>dummy = ListNode(0, head)</code> and set <code>slow = fast = dummy</code>.",
                    "Move <code>fast</code> forward <code>n + 1</code> times.",
                    "While <code>fast</code> is not <code>None</code>, move both <code>slow</code> and <code>fast</code> one step.",
                    "Unlink: <code>slow.next = slow.next.next</code>.",
                    "Return <code>dummy.next</code>.",
                ],
                "why": [
                    "The gap stays n + 1 nodes. When <code>fast</code> is <code>None</code> (one past the last node), <code>slow</code> is n + 1 positions before that, which is just before the n-th node from the end.",
                    "<code>fast</code> walks the list once: <strong>O(L)</strong> time in a single pass.",
                    "Two pointers and a dummy: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "fast moves 3 times from the dummy: 1, 2, 3.",
                        "Both move: slow 1, fast 4; slow 2, fast 5; slow 3, fast None.",
                        "slow is 3, so 3.next becomes 5.",
                        "Return dummy.next: <strong>[1, 2, 3, 5]</strong>.",
                    ],
                    [
                        "fast moves 3 times from the dummy: 1, 2, None.",
                        "fast is already None, so the loop does not run; slow stays on the dummy.",
                        "dummy.next becomes 2, removing the head.",
                        "Return dummy.next: <strong>[2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why a gap of <code>n + 1</code> and not n?",
                     "With a gap of n, <code>slow</code> would stop on the target itself. You need the node before it to change its link, which is one more step behind."],
                    ["Why must both start at the dummy?",
                     "When n equals the length, <code>slow</code> must end before the head. Only the dummy is there."],
                    ["Is this really faster than counting first?",
                     "Both are O(L). This one reads the list once, which matters when the list is streamed or very long, and it is the version interviewers expect."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ copy list with random pointer
    "copy-list-random-pointer": {
        "examples": [
            {"setup": COPY_SETUP + ("a, b, c, d = Node(7), Node(13), Node(11), Node(10)\n"
                                    "a.next, b.next, c.next = b, c, d\n"
                                    "b.random, c.random, d.random = a, d, b       # 7 has no random\n"
                                    "copy = copy_random_list(a)"),
             "call": "[dump(copy), copy is not a, dump(a)]",
             "expect": "[[(7, None), (13, 0), (11, 3), (10, 1)], True, [(7, None), (13, 0), (11, 3), (10, 1)]]"},
            {"setup": COPY_SETUP + ("x = Node(5)\n"
                                    "x.random = x                                # points at itself\n"
                                    "copy = copy_random_list(x)"),
             "call": "[dump(copy), copy is not x, copy.random is copy]",
             "expect": "[[(5, 0)], True, True]"},
        ],
        "approaches": {
            "Hash map from original to copy, two passes": {
                "idea": [
                    "The hard part is <code>random</code>: it may point at a node whose copy does not exist yet.",
                    "So first make a copy of every node and remember <code>original → copy</code> in a dictionary, then wire up the pointers once all copies exist.",
                ],
                "steps": [
                    "Start with <code>copy = {None: None}</code>, so a missing pointer maps to <code>None</code>.",
                    "Pass 1: for each node, <code>copy[node] = Node(node.val)</code>.",
                    "Pass 2: for each node, <code>copy[node].next = copy[node.next]</code>.",
                    "In the same pass, <code>copy[node].random = copy[node.random]</code>.",
                    "Return <code>copy[head]</code>.",
                ],
                "why": [
                    "After pass 1 every original has a copy, so in pass 2 every pointer target, <code>next</code> or <code>random</code>, can be translated to its copy.",
                    "The <code>{None: None}</code> entry turns missing pointers and an empty list into ordinary lookups.",
                    "Two passes with O(1) dictionary work each: <strong>O(n)</strong> time; the dictionary holds n entries: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pass 1 builds 7', 13', 11', 10' and the map from each original to its copy.",
                        "Pass 2, 7: 7'.next = 13', 7'.random = copy[None] = None.",
                        "13: 13'.next = 11', 13'.random = 7'. 11: 11'.next = 10', 11'.random = 10'.",
                        "10: 10'.next = None, 10'.random = 13'.",
                        "The copy dumps as <strong>[(7, None), (13, 0), (11, 3), (10, 1)]</strong>, uses new nodes, and the original is unchanged.",
                    ],
                    [
                        "Pass 1 builds 5' and the map {None: None, 5: 5'}.",
                        "Pass 2: 5'.next = copy[None] = None.",
                        "5'.random = copy[5] = 5', so the copy points at itself, not at the original.",
                        "Result <strong>[[(5, 0)], True, True]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can't I set <code>random</code> in the first pass?",
                     "A <code>random</code> pointer can point forward to a node not yet copied, like 11 → 10 here. Waiting for pass 2 guarantees every copy exists."],
                    ["What is <code>{None: None}</code> for?",
                     "It lets <code>copy[node.next]</code> and <code>copy[node.random]</code> work when the pointer is <code>None</code>, without an <code>if</code>. It also makes <code>copy[head]</code> return <code>None</code> for an empty list."],
                    ["Why key the dictionary by node and not by value?",
                     "Values can repeat. Only the node object identifies a position, and nodes hash by identity."],
                ],
            },
            "Recursive clone with memoisation": {
                "idea": [
                    "Treat the list as a graph where each node has two edges, <code>next</code> and <code>random</code>, and clone it with a depth-first search.",
                    "A memo from original to clone makes each node cloned once, so pointers that loop back (like a random pointing to an earlier node or to itself) reuse the existing clone.",
                ],
                "steps": [
                    "<code>clone(None)</code> returns <code>None</code>.",
                    "If <code>node</code> is already in <code>memo</code>, return its clone.",
                    "Otherwise create <code>c = memo[node] = Node(node.val)</code> <em>before</em> recursing.",
                    "Set <code>c.next = clone(node.next)</code> and <code>c.random = clone(node.random)</code>.",
                    "Return <code>c</code>; the answer is <code>clone(head)</code>.",
                ],
                "why": [
                    "Every reachable node is cloned exactly once and every pointer is translated through <code>memo</code>, so the clone has the same shape.",
                    "Storing the clone in <code>memo</code> before recursing is what stops infinite recursion on cycles such as a node whose random points at itself.",
                    "Each node is created once and each pointer followed once: <strong>O(n)</strong> time. The memo and the recursion depth (up to n along <code>next</code>) give <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "clone(7) creates 7' and recurses along next: clone(13) creates 13', clone(11) creates 11', clone(10) creates 10'.",
                        "In clone(10): next is None; random 13 is in memo, so 10'.random = 13'.",
                        "Back in clone(11): random 10 is in memo, 11'.random = 10'. Back in clone(13): random 7 is in memo, 13'.random = 7'.",
                        "Back in clone(7): random is None.",
                        "The copy dumps as <strong>[(7, None), (13, 0), (11, 3), (10, 1)]</strong>.",
                    ],
                    [
                        "clone(5) creates 5' and stores memo[5] = 5' first.",
                        "5'.next = clone(None) = None.",
                        "5'.random = clone(5): 5 is in memo, so it returns 5' instead of recursing again.",
                        "Result <strong>[[(5, 0)], True, True]</strong>.",
                    ],
                ],
                "faq": [
                    ["What happens if <code>memo[node]</code> is set after the recursive calls?",
                     "A node whose random points back to itself or an ancestor would call <code>clone</code> on a node not yet in the memo and recurse forever (or create duplicate copies)."],
                    ["Is the recursion depth a problem?",
                     "Yes for long lists: the <code>next</code> chain alone is n frames deep, so more than about 1000 nodes passes CPython's default limit."],
                    ["How is this different from the two-pass map?",
                     "Same idea, same memory. The two-pass version separates \"create\" from \"wire\"; this one creates nodes on demand as pointers are followed."],
                ],
            },
            "Interleave copies, then split": {
                "idea": [
                    "Avoid the dictionary by storing the map in the list itself: put each node's copy right after it, A → A' → B → B'.",
                    "Then the copy of any node X is simply <code>X.next</code>, so a copy's random is <code>X.random.next</code>.",
                    "Finally pull the copies out into their own list and restore the original links.",
                ],
                "steps": [
                    "Pass 1: for each node, insert <code>Node(node.val, node.next)</code> after it and jump two ahead.",
                    "Pass 2: for each original, if <code>node.random</code> exists set <code>node.next.random = node.random.next</code>.",
                    "Pass 3: with <code>c = node.next</code>, restore <code>node.next = c.next</code> and append <code>c</code> to the copy list via <code>tail.next = tail = c</code>.",
                    "Advance <code>node = node.next</code> to the next original.",
                    "Return <code>dummy.next</code>, the first copy.",
                ],
                "why": [
                    "After pass 1, every original is followed by its own copy, so <code>X.next</code> is the copy of X; pass 2 uses this to translate every random pointer.",
                    "Pass 3 undoes the interleaving: each original gets back its old <code>next</code>, and the copies are chained in the same order.",
                    "Three linear passes: <strong>O(n)</strong> time. Apart from the n new nodes of the output, only a few pointers are used: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "Pass 1: 7 → 7' → 13 → 13' → 11 → 11' → 10 → 10'.",
                        "Pass 2: 7 has no random. 13'.random = 7.next = 7'; 11'.random = 10.next = 10'; 10'.random = 13.next = 13'.",
                        "Pass 3: 7 → 13 restored, copy chain 7'; then 13 → 11, chain 7' → 13'; and so on to 10 → None.",
                        "Copy chain 7' → 13' → 11' → 10' dumps as <strong>[(7, None), (13, 0), (11, 3), (10, 1)]</strong>, and the original dumps the same.",
                    ],
                    [
                        "Pass 1: 5 → 5' → None.",
                        "Pass 2: 5.random is 5, so 5'.random = 5.next = 5'.",
                        "Pass 3: c = 5', 5.next = None again, copy chain = 5'.",
                        "Result <strong>[[(5, 0)], True, True]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must the random pointers be set before splitting?",
                     "The trick \"copy of X is X.next\" only holds while the lists are interleaved. After the split that link is gone."],
                    ["Why is <code>tail.next = tail = c</code> correct?",
                     "Python assigns left to right after evaluating <code>c</code>: first <code>tail.next = c</code> on the old tail, then <code>tail = c</code>. It appends and advances in one line."],
                    ["Why restore the original list at all?",
                     "The caller still owns the original and expects it unchanged; the tests check that it dumps the same as before."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add two numbers
    "add-two-numbers": {
        "examples": [
            {"call": "to_list(add_two_numbers(build_list([2, 4, 3]), build_list([5, 6, 4])))", "expect": "[7, 0, 8]"},
            {"call": "to_list(add_two_numbers(build_list([9, 9]), build_list([1])))", "expect": "[0, 0, 1]"},
        ],
        "approaches": {
            "Convert to integers and back": {
                "idea": [
                    "The lists store numbers with the ones digit first. Python integers have no size limit, so turn each list into an int, add, and turn the sum back into digits.",
                    "Reading digits with a growing <code>place</code> (1, 10, 100, …) matches the reversed order directly.",
                ],
                "steps": [
                    "<code>value(node)</code> adds <code>node.val * place</code> for each node, multiplying <code>place</code> by 10 each step.",
                    "Compute <code>s = value(l1) + value(l2)</code>.",
                    "Repeatedly split off the last digit with <code>s, d = divmod(s, 10)</code> and append <code>ListNode(d)</code>.",
                    "Stop after the digit that leaves <code>s == 0</code>, and return <code>dummy.next</code>.",
                ],
                "why": [
                    "<code>divmod</code> yields digits ones-first, which is exactly the order the output list needs.",
                    "The loop is <code>while True</code> with the check after appending, so a sum of 0 still produces one node [0].",
                    "It does O(m + n) loop steps, so <strong>O(m + n)</strong> time if big-int operations are counted as O(1); in reality they grow with the number's length. The digits and the integer take <strong>O(m + n)</strong> space.",
                ],
                "dry": [
                    [
                        "value(l1) = 2 + 40 + 300 = 342; value(l2) = 5 + 60 + 400 = 465.",
                        "s = 807.",
                        "divmod: (80, 7) → node 7; (8, 0) → node 0; (0, 8) → node 8 and s = 0, so stop.",
                        "Result: <strong>[7, 0, 8]</strong>.",
                    ],
                    [
                        "value(l1) = 9 + 90 = 99; value(l2) = 1.",
                        "s = 100.",
                        "divmod gives digits 0, 0, then 1 with s = 0.",
                        "Result: <strong>[0, 0, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>while True</code> instead of <code>while s</code>?",
                     "If the sum is 0, <code>while s</code> would never run and return an empty list. Checking after appending guarantees at least one digit."],
                    ["Would this work in Java or C++?",
                     "Not for long lists: the numbers can have 100 digits and overflow 64-bit integers. It only works because Python ints are unbounded."],
                    ["Is it really O(m + n)?",
                     "Counting loop steps, yes. Each big-int multiply or add costs time proportional to the number's length, so the true cost is closer to O((m + n)²) bit operations for very long inputs."],
                ],
            },
            "Digit by digit with a carry": {
                "idea": [
                    "Do grade-school addition: add the two current digits plus the carry, write down the last digit, and carry the rest.",
                    "Because the lists start at the ones digit, walking them forwards is exactly the right order.",
                    "A missing digit in the shorter list counts as 0, and a final carry becomes one extra node.",
                ],
                "steps": [
                    "Create <code>dummy = tail = ListNode()</code> and <code>carry = 0</code>.",
                    "Loop while <code>l1 or l2 or carry</code>.",
                    "<code>total = carry + (l1.val if l1 else 0) + (l2.val if l2 else 0)</code>.",
                    "<code>carry, digit = divmod(total, 10)</code>; append <code>ListNode(digit)</code> at <code>tail</code>.",
                    "Advance whichever of <code>l1</code>, <code>l2</code> still has nodes; return <code>dummy.next</code>.",
                ],
                "why": [
                    "Each step computes one column of the sum exactly as on paper; the carry is at most 1 because 9 + 9 + 1 = 19.",
                    "Including <code>carry</code> in the loop condition adds the last digit when the sum is longer than both inputs.",
                    "One step per output digit: <strong>O(max(m, n))</strong> time, and only a few variables beyond the output list: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "2 + 5 + 0 = 7: digit 7, carry 0.",
                        "4 + 6 + 0 = 10: digit 0, carry 1.",
                        "3 + 4 + 1 = 8: digit 8, carry 0. Both lists end and carry is 0, so the loop stops.",
                        "Result: <strong>[7, 0, 8]</strong>.",
                    ],
                    [
                        "9 + 1 + 0 = 10: digit 0, carry 1.",
                        "9 + 0 + 1 = 10: l2 is finished and counts as 0. Digit 0, carry 1.",
                        "Both lists are finished but carry is 1: digit 1, carry 0.",
                        "Result: <strong>[0, 0, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>carry</code> in the loop condition?",
                     "Without it, [9, 9] + [1] would stop after two digits and return [0, 0], losing the leading 1."],
                    ["Can the carry ever be 2?",
                     "No. The largest column is 9 + 9 + 1 = 19, so the carry is 0 or 1."],
                    ["What if the digits were stored most significant first?",
                     "Then you would reverse both lists first, or push the digits on stacks, because addition has to start from the ones digit."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find the duplicate number
    "find-duplicate-number": {
        "examples": [
            {"call": "find_duplicate([1, 3, 4, 2, 2])", "expect": "2"},
            {"call": "find_duplicate([3, 3, 3, 3, 3])", "expect": "3"},
        ],
        "approaches": {
            "Sort and look for neighbours": {
                "idea": [
                    "In sorted order, equal values sit next to each other.",
                    "So sort a copy and scan adjacent pairs; the first equal pair is the duplicate.",
                ],
                "steps": [
                    "Make a sorted copy <code>s = sorted(nums)</code>, leaving <code>nums</code> untouched.",
                    "Walk adjacent pairs with <code>zip(s, s[1:])</code>.",
                    "Return <code>a</code> as soon as <code>a == b</code>.",
                    "The problem guarantees a duplicate, so the loop always returns.",
                ],
                "why": [
                    "Every copy of the duplicate is adjacent after sorting, so at least one adjacent pair is equal, and no other value repeats.",
                    "Sorting dominates: <strong>O(n log n)</strong> time.",
                    "<code>sorted</code> builds a new list (and <code>s[1:]</code> another), so the space is <strong>O(n)</strong>; sorting in place would be O(1) but would modify the input, which is not allowed.",
                ],
                "dry": [
                    [
                        "s = [1, 2, 2, 3, 4].",
                        "Pair (1, 2): different.",
                        "Pair (2, 2): equal, so it returns <strong>2</strong>.",
                    ],
                    [
                        "s = [3, 3, 3, 3, 3].",
                        "The first pair (3, 3) is already equal.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>sorted(nums)</code> and not <code>nums.sort()</code>?",
                     "The problem forbids modifying the array, and the tests check that <code>nums</code> is unchanged afterwards."],
                    ["What if the duplicate appears more than twice?",
                     "All its copies are adjacent after sorting, so the first pair among them is found; the answer is the same."],
                    ["Why does the function have no final <code>return</code>?",
                     "The input always has a duplicate, so the loop always returns. On invalid input it would return <code>None</code>."],
                ],
            },
            "Hash set": {
                "idea": [
                    "Scan the numbers and remember each one in a set.",
                    "The first number that is already in the set is the duplicate.",
                ],
                "steps": [
                    "Start with an empty set <code>seen</code>.",
                    "For each <code>x</code> in <code>nums</code>: if <code>x in seen</code>, return <code>x</code>.",
                    "Otherwise add <code>x</code> to <code>seen</code>.",
                    "With a guaranteed duplicate, the loop always returns.",
                ],
                "why": [
                    "When the second copy of the duplicate is reached, the first copy is already in the set, so it is reported; no other value can be in the set twice.",
                    "One set lookup and insert per element: <strong>O(n)</strong> time on average.",
                    "The set may hold up to n values: <strong>O(n)</strong> space, which is what the problem's follow-up asks to avoid.",
                ],
                "dry": [
                    [
                        "1: add. 3: add. 4: add. 2: add. seen = {1, 2, 3, 4}.",
                        "2: already in seen.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "3: add. seen = {3}.",
                        "The second 3 is already in seen.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Does it modify <code>nums</code>?",
                     "No, it only reads it, so it satisfies the read-only rule but not the O(1) space rule."],
                    ["Could I use a boolean list instead of a set?",
                     "Yes, values are 1..n, so <code>[False] * (n + 1)</code> works the same way; it is still O(n) space."],
                    ["Why is this not the final answer?",
                     "The follow-up asks for O(1) extra space without changing the array. That rules out sets and sorting, which leads to binary search on values or Floyd."],
                ],
            },
            "Binary search on the value, counting": {
                "idea": [
                    "Binary search on the <em>value</em>, not the index. With n + 1 numbers in 1..n, count how many are ≤ <code>mid</code>.",
                    "Without a duplicate at or below <code>mid</code>, at most <code>mid</code> numbers can be ≤ <code>mid</code>. A count above <code>mid</code> means the duplicate is ≤ <code>mid</code> (pigeonhole).",
                ],
                "steps": [
                    "Set <code>lo, hi = 1, len(nums) - 1</code>, the range of possible values.",
                    "While <code>lo &lt; hi</code>, take <code>mid = (lo + hi) // 2</code>.",
                    "Count <code>sum(x &lt;= mid for x in nums)</code>.",
                    "If the count is greater than <code>mid</code>, set <code>hi = mid</code>; otherwise <code>lo = mid + 1</code>.",
                    "Return <code>lo</code> when the range has one value left.",
                ],
                "why": [
                    "The count of values ≤ v exceeds v exactly when v is at least the duplicate, so the test is monotone in v and binary search finds the smallest such v, the duplicate.",
                    "There are O(log n) rounds, each counting all n numbers: <strong>O(n log n)</strong> time.",
                    "Only a few integers are kept and the array is only read: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "lo = 1, hi = 4. mid = 2: values ≤ 2 are 1, 2, 2, count 3 &gt; 2, so hi = 2.",
                        "mid = 1: only 1 is ≤ 1, count 1, not &gt; 1, so lo = 2.",
                        "lo = hi = 2.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "lo = 1, hi = 4. mid = 2: no value is ≤ 2, count 0, so lo = 3.",
                        "mid = 3: all five values are ≤ 3, count 5 &gt; 3, so hi = 3.",
                        "lo = hi = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>count &gt; mid</code> and not <code>count &gt;= mid</code>?",
                     "With no duplicate in 1..mid, the count can be exactly <code>mid</code>. Only a count strictly above <code>mid</code> proves a repeat there."],
                    ["Does it work when some values are missing?",
                     "Yes. Missing values only lower counts; below the duplicate the count stays ≤ <code>mid</code>, and from the duplicate up it exceeds <code>mid</code>, as [3, 3, 3, 3, 3] shows."],
                    ["Why <code>hi = mid</code> and not <code>mid - 1</code>?",
                     "<code>mid</code> itself may be the duplicate, so it must stay in the range."],
                ],
            },
            "Floyd's cycle detection on i &rarr; nums[i]": {
                "idea": [
                    "Treat the array as a linked list: from index <code>i</code> go to index <code>nums[i]</code>. Values are 1..n, so every step stays inside the array.",
                    "Two indices point to the duplicate value, so that node has two incoming edges: it is where the path from 0 enters a cycle.",
                    "Floyd's algorithm finds a cycle's entrance in O(1) space, and that entrance is the duplicate.",
                ],
                "steps": [
                    "Phase 1: start <code>slow = fast = 0</code>; move <code>slow = nums[slow]</code> and <code>fast = nums[nums[fast]]</code> until they are equal.",
                    "Phase 2: reset <code>slow = 0</code>, keeping <code>fast</code> at the meeting point.",
                    "Move both one step at a time, <code>slow, fast = nums[slow], nums[fast]</code>, until they are equal.",
                    "Return <code>slow</code>, the cycle's entrance.",
                ],
                "why": [
                    "Index 0 has no incoming edge (no value is 0), so the walk from 0 forms a tail followed by a cycle, and the duplicate value is the only node with two predecessors: the cycle entrance.",
                    "If the tail has length a and they meet b steps into a cycle of length c, then a ≡ −b (mod c), so walking a steps from the start and from the meeting point lands both on the entrance.",
                    "Both phases take O(n) steps: <strong>O(n)</strong> time, with two indices: <strong>O(1)</strong> space, and the array is never modified.",
                ],
                "dry": [
                    [
                        "The edges are 0→1, 1→3, 2→4, 3→2, 4→2.",
                        "Phase 1: (slow, fast) = (1, 3), (3, 4), (2, 4), (4, 4): they meet at 4.",
                        "Phase 2: slow = 0. Steps: (1, 2), (3, 4), (2, 2): they meet at 2.",
                        "It returns <strong>2</strong>.",
                    ],
                    [
                        "Every index points to 3, and 3 points to itself.",
                        "Phase 1: slow = nums[0] = 3, fast = nums[nums[0]] = 3: they meet at once.",
                        "Phase 2: slow = 0 ≠ 3, so one step: slow = 3, fast = nums[3] = 3.",
                        "It returns <strong>3</strong>.",
                    ],
                ],
                "faq": [
                    ["Why start at index 0?",
                     "No value is 0, so nothing points to index 0. It is guaranteed to be on the tail, outside the cycle, which is what makes the entrance the duplicate."],
                    ["Why is the meeting point in phase 1 not the answer?",
                     "The pointers can meet anywhere on the cycle (index 4 in the first example). Only phase 2 lands on the entrance."],
                    ["Why is phase 1 a <code>while True</code> loop?",
                     "Both start at 0, so a <code>while slow != fast</code> condition would be false immediately. The first step has to happen before the comparison."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse linked list II
    "reverse-linked-list-ii": {
        "examples": [
            {"call": "to_list(reverse_between(build_list([1, 2, 3, 4, 5]), 2, 4))", "expect": "[1, 4, 3, 2, 5]"},
            {"call": "to_list(reverse_between(build_list([1, 2, 3]), 1, 3))", "expect": "[3, 2, 1]"},
        ],
        "approaches": {
            "Copy the segment's values, write them back reversed": {
                "idea": [
                    "Only positions <code>left</code> to <code>right</code> (1-based) change, so leave every link alone and reverse just the values in that stretch.",
                    "Collect those values in a list, then walk the same stretch again and write them back with <code>pop()</code>, which hands them out last-first.",
                ],
                "steps": [
                    "Walk positions <code>i = 1 .. right</code>; when <code>i &gt;= left</code>, append <code>node.val</code> to <code>vals</code>.",
                    "Reset <code>node = head</code>.",
                    "Walk positions <code>1 .. right</code> again; when <code>i &gt;= left</code>, set <code>node.val = vals.pop()</code>.",
                    "Nodes after <code>right</code> are never touched.",
                    "Return <code>head</code>, which is still the first node.",
                ],
                "why": [
                    "The segment's values come back in reverse order and land in the same positions, which is exactly the required list of values.",
                    "Both walks stop at <code>right</code>, so the time is <strong>O(n)</strong> at worst.",
                    "<code>vals</code> holds right − left + 1 values: <strong>O(right − left)</strong> space.",
                ],
                "dry": [
                    [
                        "Pass 1: positions 2, 3, 4 give vals = [2, 3, 4].",
                        "Pass 2: position 2 pops 4, position 3 pops 3, position 4 pops 2.",
                        "Node 5 is not visited.",
                        "The list reads <strong>[1, 4, 3, 2, 5]</strong>.",
                    ],
                    [
                        "Pass 1: positions 1, 2, 3 give vals = [1, 2, 3].",
                        "Pass 2: the three nodes receive 3, 2, 1.",
                        "The head node is unchanged as an object, now holding 3.",
                        "The list reads <strong>[3, 2, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>left = 1</code> no special case here?",
                     "No links change, so the head node stays first; only its value is swapped. The pointer version needs a dummy node for this case."],
                    ["Why loop only up to <code>right</code>?",
                     "Nothing after <code>right</code> changes, so there is no reason to walk further."],
                    ["Is swapping values allowed?",
                     "It passes the tests, but interviews usually want nodes relinked; values may be large or other code may hold references to particular nodes."],
                ],
            },
            "Head insertion in one pass": {
                "idea": [
                    "Stop at <code>prev</code>, the node just before the segment. The segment's first node, <code>cur</code>, will end up as the segment's last.",
                    "Repeatedly take the node right after <code>cur</code> and move it to the front of the segment, just after <code>prev</code>. After <code>right - left</code> moves the segment is reversed.",
                    "A dummy node in front of the head gives <code>prev</code> a place to stand when <code>left = 1</code>.",
                ],
                "steps": [
                    "Create <code>dummy = ListNode(0, head)</code> and move <code>prev</code> forward <code>left - 1</code> times.",
                    "Set <code>cur = prev.next</code>, the segment's first node.",
                    "Repeat <code>right - left</code> times: <code>move = cur.next</code>; unhook it with <code>cur.next = move.next</code>.",
                    "Insert it at the front: <code>move.next = prev.next</code>, then <code>prev.next = move</code>.",
                    "Return <code>dummy.next</code>.",
                ],
                "why": [
                    "After k moves, the first k + 1 nodes of the segment are reversed and sit between <code>prev</code> and <code>cur</code>, with <code>cur</code> last and still linked to the untouched rest.",
                    "Each move changes three links in O(1), so with the walk to <code>prev</code> the time is <strong>O(n)</strong> in one pass.",
                    "Only <code>dummy</code>, <code>prev</code>, <code>cur</code> and <code>move</code>: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "prev moves 1 step to node 1; cur = 2.",
                        "Move 1: move = 3. 2 → 4, 3 → 2, 1 → 3. List: 1, 3, 2, 4, 5.",
                        "Move 2: move = 4. 2 → 5, 4 → 3, 1 → 4. List: 1, 4, 3, 2, 5.",
                        "Return dummy.next: <strong>[1, 4, 3, 2, 5]</strong>.",
                    ],
                    [
                        "left = 1, so prev stays on the dummy; cur = 1.",
                        "Move 1: move = 2. 1 → 3, 2 → 1, dummy → 2. List: 2, 1, 3.",
                        "Move 2: move = 3. 1 → None, 3 → 2, dummy → 3. List: 3, 2, 1.",
                        "Return dummy.next: <strong>[3, 2, 1]</strong>; the head changed, which the dummy handled.",
                    ],
                ],
                "faq": [
                    ["Why doesn't <code>cur</code> ever move?",
                     "<code>cur</code> is the old first node of the segment. Each move pulls the node after it to the front, so <code>cur</code> drifts towards the end of the segment by itself and always points at the next node to move."],
                    ["Why exactly <code>right - left</code> moves?",
                     "The segment has <code>right - left + 1</code> nodes. <code>cur</code> stays put and every other node is moved once to the front."],
                    ["Why return <code>dummy.next</code>?",
                     "When <code>left = 1</code> the first node changes. <code>head</code> would still point at the old first node, which is now the end of the segment."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ design circular queue
    "design-circular-queue": {
        "examples": [
            {"setup": "q = MyCircularQueue(3)",
             "call": "[q.enQueue(1), q.enQueue(2), q.enQueue(3), q.enQueue(4), q.Rear(), q.deQueue(), q.enQueue(4), q.Front(), q.Rear(), q.isFull()]",
             "expect": "[True, True, True, False, 3, True, True, 2, 4, True]"},
            {"setup": "q = MyCircularQueue(2)",
             "call": "[q.deQueue(), q.Front(), q.enQueue(5), q.enQueue(6), q.deQueue(), q.enQueue(7), q.Front(), q.Rear(), q.isEmpty()]",
             "expect": "[False, -1, True, True, True, True, 6, 7, False]"},
        ],
        "approaches": {
            "Python list with pop(0)": {
                "idea": [
                    "A bounded queue is a list with a size cap: append at the back, remove from the front, refuse to append when full.",
                    "Python lists do all of this out of the box; the only cost is that removing from the front shifts every other element.",
                ],
                "steps": [
                    "<code>enQueue</code>: if <code>len(self.items) == self.k</code>, return <code>False</code>; otherwise append and return <code>True</code>.",
                    "<code>deQueue</code>: if the list is empty return <code>False</code>; otherwise <code>pop(0)</code> and return <code>True</code>.",
                    "<code>Front</code> and <code>Rear</code> return <code>items[0]</code> and <code>items[-1]</code>, or -1 when empty.",
                    "<code>isEmpty</code> and <code>isFull</code> compare the length with 0 and <code>k</code>.",
                ],
                "why": [
                    "The list always holds the queue's elements oldest first, so the front, rear and size checks follow directly.",
                    "<code>pop(0)</code> moves every remaining element one slot left, so <code>deQueue</code> is <strong>O(n)</strong>; all other operations are O(1).",
                    "At most k values are stored: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "enQueue 1, 2, 3 → True each; items = [1, 2, 3]. enQueue 4 → full, False.",
                        "Rear → 3.",
                        "deQueue → True; pop(0) shifts the list to [2, 3].",
                        "enQueue 4 → True, items = [2, 3, 4]. Front → 2, Rear → 4, isFull → True.",
                        "Result <strong>[True, True, True, False, 3, True, True, 2, 4, True]</strong>.",
                    ],
                    [
                        "deQueue on [] → False. Front on [] → -1.",
                        "enQueue 5, 6 → True; items = [5, 6].",
                        "deQueue → True, items = [6]. enQueue 7 → True, items = [6, 7].",
                        "Front → 6, Rear → 7, isEmpty → False.",
                        "Result <strong>[False, -1, True, True, True, True, 6, 7, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>pop(0)</code> slow?",
                     "A Python list is an array. Removing the first slot means moving every later element one place left, which is O(n)."],
                    ["Would <code>collections.deque</code> fix it?",
                     "Yes, <code>popleft</code> is O(1). But the exercise is to build the ring buffer that a deque, or a fixed-size hardware queue, is made of."],
                    ["Why return -1 from <code>Front</code> on an empty queue?",
                     "It is the problem's convention for \"no element\"; reading <code>items[0]</code> would raise an IndexError."],
                ],
            },
            "Array ring buffer with head and count": {
                "idea": [
                    "Allocate a fixed array of k slots once and let the queue wrap around it, so nothing ever moves.",
                    "<code>head</code> is the slot of the front element and <code>count</code> is how many elements there are; the rear is <code>count - 1</code> slots after <code>head</code>, modulo k.",
                    "Keeping <code>count</code> instead of a tail index makes \"empty\" (0) and \"full\" (k) easy to tell apart.",
                ],
                "steps": [
                    "<code>__init__</code>: <code>buf = [0] * k</code>, <code>head = count = 0</code>.",
                    "<code>enQueue</code>: if <code>count == k</code> return <code>False</code>; write to <code>buf[(head + count) % k]</code> and increase <code>count</code>.",
                    "<code>deQueue</code>: if <code>count == 0</code> return <code>False</code>; advance <code>head = (head + 1) % k</code> and decrease <code>count</code>.",
                    "<code>Front</code> reads <code>buf[head]</code>; <code>Rear</code> reads <code>buf[(head + count - 1) % k]</code>; both return -1 when empty.",
                    "<code>isEmpty</code> and <code>isFull</code> compare <code>count</code> with 0 and k.",
                ],
                "why": [
                    "The elements always occupy the <code>count</code> slots starting at <code>head</code>, wrapping with <code>% k</code>, so the next free slot and the rear follow from those two numbers.",
                    "<code>deQueue</code> does not erase the old value; it just stops counting it, and a later <code>enQueue</code> overwrites the slot.",
                    "Every operation is a few arithmetic steps: <strong>O(1)</strong> each. The buffer is fixed at <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "enQueue 1, 2, 3 fill slots 0, 1, 2; count = 3. enQueue 4: count == 3, False.",
                        "Rear: slot (0 + 3 − 1) % 3 = 2 → 3.",
                        "deQueue: head = 1, count = 2.",
                        "enQueue 4: slot (1 + 2) % 3 = 0, buf = [4, 2, 3], count = 3. Front: buf[1] = 2. Rear: slot (1 + 3 − 1) % 3 = 0 → 4. isFull: True.",
                        "Result <strong>[True, True, True, False, 3, True, True, 2, 4, True]</strong>.",
                    ],
                    [
                        "deQueue with count 0 → False. Front with count 0 → -1.",
                        "enQueue 5 → slot 0, enQueue 6 → slot 1; count = 2.",
                        "deQueue: head = 1, count = 1. enQueue 7 → slot (1 + 1) % 2 = 0, buf = [7, 6], count = 2.",
                        "Front: buf[1] = 6. Rear: slot (1 + 2 − 1) % 2 = 0 → 7. isEmpty: False.",
                        "Result <strong>[False, -1, True, True, True, True, 6, 7, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store <code>count</code> rather than a tail index?",
                     "With only <code>head</code> and <code>tail</code>, an empty and a full queue both have <code>head == tail</code>. Either you waste a slot or track a count; the count is simpler."],
                    ["Why doesn't <code>deQueue</code> clear the slot?",
                     "The slot is outside the counted range, so it is never read again before an <code>enQueue</code> overwrites it."],
                    ["What does <code>% k</code> do?",
                     "It wraps an index that runs past the last slot back to the start of the array, which is what makes the buffer circular."],
                ],
            },
            "Singly linked list with a size cap": {
                "idea": [
                    "A queue is naturally a linked list with pointers to both ends: add at <code>tail</code>, remove at <code>head</code>.",
                    "A <code>size</code> counter enforces the capacity k, so the list never grows past it.",
                ],
                "steps": [
                    "<code>enQueue</code>: if <code>size == k</code>, return <code>False</code>; create <code>ListNode(value)</code>, link it after <code>tail</code> (or make it <code>head</code> if empty), move <code>tail</code>, increase <code>size</code>.",
                    "<code>deQueue</code>: if <code>size == 0</code>, return <code>False</code>; move <code>head = head.next</code>, and if that empties the list, clear <code>tail</code> too; decrease <code>size</code>.",
                    "<code>Front</code> returns <code>head.val</code> and <code>Rear</code> returns <code>tail.val</code>, or -1 when empty.",
                    "<code>isEmpty</code> and <code>isFull</code> compare <code>size</code> with 0 and k.",
                ],
                "why": [
                    "Nodes are linked oldest to newest, so <code>head</code> is always the front and <code>tail</code> the rear.",
                    "Clearing <code>tail</code> when the last node leaves keeps <code>Rear</code> from returning a removed value and lets the next <code>enQueue</code> set <code>head</code> correctly.",
                    "Every operation changes a constant number of pointers: <strong>O(1)</strong> each. Memory follows the current size, up to <strong>O(k)</strong>.",
                ],
                "dry": [
                    [
                        "enQueue 1, 2, 3: list 1 → 2 → 3, size 3. enQueue 4: full, False.",
                        "Rear: tail.val = 3.",
                        "deQueue: head moves to 2, size 2.",
                        "enQueue 4: list 2 → 3 → 4. Front 2, Rear 4, isFull True.",
                        "Result <strong>[True, True, True, False, 3, True, True, 2, 4, True]</strong>.",
                    ],
                    [
                        "deQueue with size 0 → False. Front with no head → -1.",
                        "enQueue 5 (head = tail = 5), enQueue 6: list 5 → 6.",
                        "deQueue: head = 6, size 1. enQueue 7: list 6 → 7.",
                        "Front 6, Rear 7, isEmpty False.",
                        "Result <strong>[False, -1, True, True, True, True, 6, 7, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why must <code>tail</code> be reset when the queue empties?",
                     "Otherwise <code>tail</code> still points at the removed node: <code>Rear</code> would return its value, and the next <code>enQueue</code> would link after it instead of setting <code>head</code>."],
                    ["Is it really circular?",
                     "No; it behaves like the circular queue from the outside. The ring buffer is the circular one."],
                    ["Why might the ring buffer still be preferred?",
                     "It allocates once and has no per-node overhead or garbage, which matters in real-time or embedded code."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LRU cache
    "lru-cache": {
        "examples": [
            {"setup": "c = LRUCache(2)",
             "call": "[c.put(1, 1), c.put(2, 2), c.get(1), c.put(3, 3), c.get(2), c.put(4, 4), c.get(1), c.get(3), c.get(4)]",
             "expect": "[None, None, 1, None, -1, None, -1, 3, 4]"},
            {"setup": "c = LRUCache(2)",
             "call": "[c.put(1, 1), c.put(2, 2), c.put(1, 10), c.put(3, 3), c.get(2), c.get(1)]",
             "expect": "[None, None, None, None, -1, 10]"},
        ],
        "approaches": {
            "Dict plus a recency list": {
                "idea": [
                    "Keep the values in a dictionary and, separately, a list of keys ordered from least to most recently used.",
                    "Every access moves its key to the end of the list; when the cache is full, the key at the front is the one to evict.",
                ],
                "steps": [
                    "<code>get</code>: if <code>key</code> is missing, return -1. Otherwise <code>order.remove(key)</code>, <code>order.append(key)</code>, and return the value.",
                    "<code>put</code> on an existing key: remove it from <code>order</code> (it is re-appended below).",
                    "<code>put</code> on a new key with a full cache: <code>del self.vals[self.order.pop(0)]</code> evicts the least recent key.",
                    "Then store <code>vals[key] = value</code> and append <code>key</code> to <code>order</code>.",
                ],
                "why": [
                    "<code>order</code> always lists the keys by last use, so its first key is exactly the least recently used one.",
                    "<code>order.remove</code> and <code>order.pop(0)</code> scan or shift the list, so each operation is <strong>O(n)</strong> in the capacity.",
                    "The dict and the list each hold up to capacity entries: <strong>O(capacity)</strong> space.",
                ],
                "dry": [
                    [
                        "put 1, put 2: order = [1, 2]. get 1 → 1, order = [2, 1].",
                        "put 3: full and 3 is new, evict order[0] = 2. order = [1, 3].",
                        "get 2 → -1. put 4: evict 1, order = [3, 4].",
                        "get 1 → -1; get 3 → 3 (order [4, 3]); get 4 → 4.",
                        "Result <strong>[None, None, 1, None, -1, None, -1, 3, 4]</strong>.",
                    ],
                    [
                        "put 1, put 2: order = [1, 2].",
                        "put(1, 10): key 1 exists, so remove and re-append it with no eviction. order = [2, 1], vals[1] = 10.",
                        "put 3: full, evict 2. order = [1, 3].",
                        "get 2 → -1; get 1 → 10.",
                        "Result <strong>[None, None, None, None, -1, 10]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does updating an existing key not evict anything?",
                     "The number of keys does not grow. That is why the eviction is in an <code>elif</code>: it only runs for a new key."],
                    ["Why is <code>put</code> returning <code>None</code> in the results?",
                     "<code>put</code> has no return value; the example collects every call's result, so puts show up as <code>None</code>."],
                    ["What makes this too slow?",
                     "<code>list.remove</code> searches for the key and <code>pop(0)</code> shifts the list, both O(capacity). The O(1) designs replace the list with a linked structure."],
                ],
            },
            "OrderedDict": {
                "idea": [
                    "<code>OrderedDict</code> is a dictionary that remembers insertion order and can move a key to the end or pop from the front in O(1).",
                    "Treat its order as recency: the end is most recent, the front is least recent.",
                ],
                "steps": [
                    "<code>get</code>: if missing return -1; otherwise <code>move_to_end(key)</code> and return the value.",
                    "<code>put</code>: if the key exists, <code>move_to_end(key)</code> first.",
                    "Store <code>data[key] = value</code>; a new key is inserted at the end.",
                    "If <code>len(data) &gt; cap</code>, <code>popitem(last=False)</code> removes the front, least recent key.",
                ],
                "why": [
                    "Each access moves its key to the end, so keys stay ordered by last use and the front is always the eviction victim.",
                    "Evicting after inserting is safe: the new key is at the end, so the front is some other key.",
                    "<code>move_to_end</code>, insertion and <code>popitem</code> are all O(1): <strong>O(1)</strong> per operation, <strong>O(capacity)</strong> space.",
                ],
                "dry": [
                    [
                        "put 1, put 2: order 1, 2. get 1 → 1, order 2, 1.",
                        "put 3: size 3 &gt; 2, pop the front (2). Order 1, 3.",
                        "get 2 → -1. put 4: pop the front (1). Order 3, 4.",
                        "get 1 → -1, get 3 → 3, get 4 → 4.",
                        "Result <strong>[None, None, 1, None, -1, None, -1, 3, 4]</strong>.",
                    ],
                    [
                        "put 1, put 2: order 1, 2.",
                        "put(1, 10): move 1 to the end, set its value. Order 2, 1; size 2.",
                        "put 3: size 3 &gt; 2, pop 2. Order 1, 3.",
                        "get 2 → -1, get 1 → 10.",
                        "Result <strong>[None, None, None, None, -1, 10]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>move_to_end</code> before assigning in <code>put</code>?",
                     "Assigning to an existing key keeps its old position. Moving it marks the update as the most recent use."],
                    ["Is using <code>OrderedDict</code> cheating in an interview?",
                     "Often it is accepted as a first answer, but expect a follow-up asking you to build the hash map plus doubly linked list it uses inside."],
                    ["Would a plain <code>dict</code> work?",
                     "Python dicts keep insertion order too, but have no O(1) <code>move_to_end</code>; you would delete and re-insert, which also works but is less direct."],
                ],
            },
            "Hash map + doubly linked list, by hand": {
                "idea": [
                    "A doubly linked list keeps keys in recency order and lets any node be unlinked in O(1), given the node.",
                    "A hash map from key to node finds that node in O(1). Together they give O(1) <code>get</code> and <code>put</code>.",
                    "Two sentinel nodes, <code>old</code> and <code>new</code>, mark the least and most recent ends so unlinking never meets a <code>None</code>.",
                ],
                "steps": [
                    "<code>_unlink(node)</code> joins its neighbours: <code>node.prev.next, node.next.prev = node.next, node.prev</code>.",
                    "<code>_append(node)</code> inserts it just before the <code>new</code> sentinel, as the most recent.",
                    "<code>get</code>: if the key is missing return -1; otherwise unlink the node, append it, and return <code>node.val</code>.",
                    "<code>put</code>: unlink the old node if the key exists, create <code>DNode(key, value)</code>, store it in <code>map</code>, and append it.",
                    "If <code>len(self.map) &gt; self.cap</code>, take <code>lru = self.old.next</code>, unlink it and delete <code>map[lru.key]</code>.",
                ],
                "why": [
                    "The list always runs from least recent (after <code>old</code>) to most recent (before <code>new</code>), because every access moves its node to the <code>new</code> end.",
                    "Each node stores its <code>key</code> so that the evicted node can be removed from the map too.",
                    "Every step is a constant number of pointer and dict operations: <strong>O(1)</strong> per call, <strong>O(capacity)</strong> space.",
                ],
                "dry": [
                    [
                        "put 1, put 2: old ⇄ 1 ⇄ 2 ⇄ new. get 1 → 1, list old ⇄ 2 ⇄ 1 ⇄ new.",
                        "put 3: append 3, map size 3 &gt; 2, evict old.next = 2. List 1 ⇄ 3.",
                        "get 2 → -1. put 4: evict old.next = 1. List 3 ⇄ 4.",
                        "get 1 → -1; get 3 → 3 (list 4 ⇄ 3); get 4 → 4.",
                        "Result <strong>[None, None, 1, None, -1, None, -1, 3, 4]</strong>.",
                    ],
                    [
                        "put 1, put 2: list 1 ⇄ 2.",
                        "put(1, 10): unlink the old node 1, create a new node (1, 10), append it. List 2 ⇄ 1, map size 2.",
                        "put 3: size 3 &gt; 2, evict old.next = 2. List 1 ⇄ 3.",
                        "get 2 → -1; get 1 → 10.",
                        "Result <strong>[None, None, None, None, -1, 10]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why a doubly linked list and not a singly linked one?",
                     "To unlink a node in O(1) you need its predecessor. A singly linked list would have to search for it."],
                    ["What do the sentinels buy?",
                     "Every real node always has a <code>prev</code> and a <code>next</code>, so <code>_unlink</code> and <code>_append</code> never check for <code>None</code>, even for the first or last node."],
                    ["Why does <code>put</code> on an existing key create a new node?",
                     "It is simpler than updating in place: unlink the old node, then treat the put like a new key. The map entry is overwritten, so the old node is garbage collected."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LFU cache
    "lfu-cache": {
        "examples": [
            {"setup": "c = LFUCache(2)",
             "call": "[c.put(1, 1), c.put(2, 2), c.get(1), c.put(3, 3), c.get(2), c.get(3), c.put(4, 4), c.get(1), c.get(3), c.get(4)]",
             "expect": "[None, None, 1, None, -1, 3, None, -1, 3, 4]"},
            {"setup": "c = LFUCache(2)",
             "call": "[c.put(1, 1), c.put(2, 2), c.get(1), c.get(2), c.put(3, 3), c.get(1), c.get(2), c.get(3)]",
             "expect": "[None, None, 1, 2, None, -1, 2, 3]"},
        ],
        "approaches": {
            "Scan for the victim": {
                "idea": [
                    "For each key keep its value, how often it was used, and when it was last used, using a global clock <code>time</code>.",
                    "The victim is the key with the smallest count, and among equal counts the one used longest ago: the minimum of <code>(count, last_used)</code>.",
                ],
                "steps": [
                    "<code>get</code>: if the key is missing return -1; otherwise tick <code>time</code>, increase the count, set <code>last_used = time</code>, and return the value.",
                    "<code>put</code> with capacity 0 does nothing.",
                    "<code>put</code> on an existing key: tick <code>time</code>, then update value, count and last use.",
                    "<code>put</code> on a new key with a full cache: delete <code>min(self.data, key=lambda k: (count, last_used))</code>.",
                    "Insert the new key as <code>[value, 1, self.time]</code>.",
                ],
                "why": [
                    "Comparing tuples orders by count first and by last use second, which is exactly the LFU rule with LRU tie-breaking.",
                    "<code>get</code> and updates are O(1), but finding the victim scans every key: <code>put</code> is <strong>O(n)</strong> in the capacity.",
                    "One small list per key: <strong>O(capacity)</strong> space.",
                ],
                "dry": [
                    [
                        "put 1 (t1), put 2 (t2): counts 1, 1. get 1 → 1: key 1 has count 2, last 3.",
                        "put 3: full, victim is min of 1:(2, 3), 2:(1, 2) → 2. Insert 3:(1, 4).",
                        "get 2 → -1. get 3 → 3: key 3 becomes (2, 5).",
                        "put 4: candidates 1:(2, 3), 3:(2, 5); same count, 1 is older → evict 1. Insert 4.",
                        "get 1 → -1, get 3 → 3, get 4 → 4: <strong>[None, None, 1, None, -1, 3, None, -1, 3, 4]</strong>.",
                    ],
                    [
                        "put 1 (t1), put 2 (t2).",
                        "get 1 → 1: (2, 3). get 2 → 2: (2, 4).",
                        "put 3: both have count 2; key 1 was used at 3, key 2 at 4, so evict 1.",
                        "get 1 → -1, get 2 → 2, get 3 → 3.",
                        "Result <strong>[None, None, 1, 2, None, -1, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>put</code> on an existing key count as a use?",
                     "The problem says so: updating a key increases its frequency and refreshes its recency, just like <code>get</code>."],
                    ["Why the check for capacity 0?",
                     "With no room, <code>min</code> over an empty dict would raise a ValueError, and nothing should ever be stored."],
                    ["Why a clock instead of real time?",
                     "Only the order of uses matters. A counter that ticks on each use gives unique, increasing stamps without depending on the system clock."],
                ],
            },
            "Frequency buckets of ordered dicts, plus min frequency": {
                "idea": [
                    "Group keys by frequency: <code>buckets[f]</code> is an <code>OrderedDict</code> of the keys used exactly f times, oldest first.",
                    "Track <code>min_freq</code>, the smallest non-empty frequency. The victim is then the first key of <code>buckets[min_freq]</code>, found in O(1).",
                    "A use moves a key from bucket f to bucket f + 1, which only changes <code>min_freq</code> when bucket f empties and was the minimum.",
                ],
                "steps": [
                    "<code>_touch(key)</code>: remove the key from <code>buckets[f]</code>; if that bucket is now empty, delete it and, if <code>min_freq == f</code>, set <code>min_freq = f + 1</code>.",
                    "Still in <code>_touch</code>: set <code>freq[key] = f + 1</code> and add the key at the end of <code>buckets[f + 1]</code>.",
                    "<code>get</code>: return -1 if missing; otherwise <code>_touch</code> and return <code>vals[key]</code>.",
                    "<code>put</code> on an existing key: update the value and <code>_touch</code>. On a new key with a full cache, <code>popitem(last=False)</code> on <code>buckets[min_freq]</code> and delete that key's entries.",
                    "Insert the new key with frequency 1 at the end of <code>buckets[1]</code> and set <code>min_freq = 1</code>.",
                ],
                "why": [
                    "Within a bucket, keys are in order of their last use, because a key enters a bucket only when it is used; so the front of the lowest bucket is the least frequent, least recent key.",
                    "<code>min_freq</code> can only rise by one in <code>_touch</code> (the key moved to f + 1) and resets to 1 on every insert, so it never needs a search.",
                    "Every operation is a constant number of dict and OrderedDict operations: <strong>O(1)</strong>, with <strong>O(capacity)</strong> space.",
                ],
                "dry": [
                    [
                        "put 1, put 2: buckets {1: [1, 2]}, min 1. get 1 → 1: buckets {1: [2], 2: [1]}.",
                        "put 3: evict the front of bucket 1, key 2. buckets {2: [1], 1: [3]}, min 1.",
                        "get 2 → -1. get 3 → 3: bucket 1 empties and was min, so min = 2. buckets {2: [1, 3]}.",
                        "put 4: evict the front of bucket 2, key 1. Insert 4: buckets {2: [3], 1: [4]}, min 1.",
                        "get 1 → -1, get 3 → 3, get 4 → 4: <strong>[None, None, 1, None, -1, 3, None, -1, 3, 4]</strong>.",
                    ],
                    [
                        "put 1, put 2: buckets {1: [1, 2]}.",
                        "get 1 → 1: {1: [2], 2: [1]}. get 2 → 2: bucket 1 empties, min = 2, {2: [1, 2]}.",
                        "put 3: evict the front of bucket 2, key 1 (used before key 2). Insert 3: {2: [2], 1: [3]}, min 1.",
                        "get 1 → -1, get 2 → 2, get 3 → 3.",
                        "Result <strong>[None, None, 1, 2, None, -1, 2, 3]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why can <code>min_freq</code> simply become <code>f + 1</code>?",
                     "The key just touched moved from f to f + 1. If bucket f was the lowest and is now empty, the touched key itself sits in bucket f + 1, so that is the new minimum."],
                    ["Why reset <code>min_freq</code> to 1 on insert?",
                     "A new key has frequency 1, the lowest possible, so it becomes the minimum regardless of what was there."],
                    ["Why <code>OrderedDict</code> with <code>None</code> values?",
                     "It is used as an ordered set: O(1) delete of any key and O(1) pop of the oldest. The values are ignored."],
                    ["Why delete empty buckets?",
                     "So that <code>buckets</code> does not fill with empty entries. Correctness relies on <code>min_freq</code>, not on scanning buckets."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse nodes in k group
    "reverse-nodes-k-group": {
        "examples": [
            {"call": "to_list(reverse_k_group(build_list([1, 2, 3, 4, 5]), 2))", "expect": "[2, 1, 4, 3, 5]"},
            {"call": "to_list(reverse_k_group(build_list([1, 2, 3, 4, 5, 6]), 3))", "expect": "[3, 2, 1, 6, 5, 4]"},
        ],
        "approaches": {
            "Stack each group": {
                "idea": [
                    "A stack reverses whatever is pushed onto it. Push k nodes, then pop them onto the result and they come out reversed.",
                    "If fewer than k nodes are left, the group is not reversed: attach it as it is and stop.",
                ],
                "steps": [
                    "Create <code>dummy = tail = ListNode()</code> and start at <code>node = head</code>.",
                    "Push up to k nodes from <code>node</code> onto <code>stack</code>, with <code>probe</code> ending just after them.",
                    "If <code>len(stack) &lt; k</code>, attach the short group with <code>tail.next = node</code> and break.",
                    "Otherwise pop every node onto the result with <code>tail.next = tail = stack.pop()</code>, then set <code>tail.next = None</code>.",
                    "Continue from <code>node = probe</code>; return <code>dummy.next</code>.",
                ],
                "why": [
                    "Each full group is popped in reverse order and appended in turn, and a short final group is linked unchanged, which matches the specification.",
                    "<code>tail.next = None</code> cuts the last popped node's old link, which pointed back inside the group, so no cycle forms.",
                    "Each node is pushed and popped once: <strong>O(n)</strong> time; the stack holds at most k nodes: <strong>O(k)</strong> space.",
                ],
                "dry": [
                    [
                        "Group 1: stack [1, 2], probe = 3. Pop 2 then 1: result 2 → 1, 1.next = None.",
                        "Group 2: stack [3, 4], probe = 5. Pop 4, 3: result 2 → 1 → 4 → 3.",
                        "Group 3: stack [5], probe = None; 1 &lt; 2, so tail.next = 5 and break.",
                        "Return dummy.next: <strong>[2, 1, 4, 3, 5]</strong>.",
                    ],
                    [
                        "Group 1: stack [1, 2, 3], probe = 4. Pop 3, 2, 1.",
                        "Group 2: stack [4, 5, 6], probe = None. Pop 6, 5, 4; 4.next = None.",
                        "node = probe = None, so the loop ends without a short group.",
                        "Return dummy.next: <strong>[3, 2, 1, 6, 5, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>tail.next = None</code> needed after popping?",
                     "The last node popped is the group's old first node, whose <code>next</code> still points at the second node of the group. Without the cut the result would loop."],
                    ["Why use a separate <code>probe</code> instead of moving <code>node</code>?",
                     "If the group turns out short, <code>node</code> must still point at its first node so it can be attached unchanged."],
                    ["Is O(k) space allowed?",
                     "It passes, but the follow-up asks for O(1) extra space, which the iterative relinking version achieves."],
                ],
            },
            "Recursive": {
                "idea": [
                    "Check that k nodes exist from <code>head</code>. If not, return the list unchanged.",
                    "Otherwise let the recursion handle everything after the first k nodes, then reverse those k nodes onto its result.",
                ],
                "steps": [
                    "Walk <code>node</code> k steps from <code>head</code>; if it hits <code>None</code> first, return <code>head</code>.",
                    "Recurse on the rest: <code>prev = reverse_k_group(node, k)</code>.",
                    "Reverse k nodes starting at <code>cur = head</code>, each pointing to <code>prev</code>: <code>cur.next, prev, cur = prev, cur, cur.next</code>.",
                    "After k steps, <code>prev</code> is the group's old last node, now its first.",
                    "Return <code>prev</code>.",
                ],
                "why": [
                    "Starting <code>prev</code> at the already-processed rest means the group's old first node ends up pointing at it, so the groups are joined while reversing.",
                    "Each node is walked once in the check and once in the reversal: <strong>O(n)</strong> time.",
                    "There is one recursive call per full group: <strong>O(n / k)</strong> stack space.",
                ],
                "dry": [
                    [
                        "call(1): 2 nodes exist, recurse on 3. call(3): 2 nodes exist, recurse on 5.",
                        "call(5): node 5, then None at the second step, so 5 is returned unchanged.",
                        "Back in call(3): reverse 3, 4 onto 5: 4 → 3 → 5. Return 4.",
                        "Back in call(1): reverse 1, 2 onto 4: 2 → 1 → 4 → 3 → 5.",
                        "Result: <strong>[2, 1, 4, 3, 5]</strong>.",
                    ],
                    [
                        "call(1) recurses on 4; call(4) recurses on <code>None</code>.",
                        "call(None): the first check finds <code>None</code>, returns <code>None</code>.",
                        "call(4): reverse 4, 5, 6 onto None: 6 → 5 → 4. Return 6.",
                        "call(1): reverse 1, 2, 3 onto 6: 3 → 2 → 1 → 6 → 5 → 4.",
                        "Result: <strong>[3, 2, 1, 6, 5, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why recurse before reversing?",
                     "The group's first node must end up pointing at the head of the processed rest. Recursing first gives that head as the starting <code>prev</code>."],
                    ["Why does the length check return <code>head</code>?",
                     "A final group shorter than k stays in its original order, so it is returned as is."],
                    ["Why is the stack only n / k deep?",
                     "Each call consumes a whole group of k nodes before recursing, so there are at most n / k + 1 calls."],
                ],
            },
            "Iterative, group by group": {
                "idea": [
                    "Process groups left to right, keeping <code>group_prev</code>, the node just before the current group (initially a dummy).",
                    "Find the group's k-th node; if it does not exist, stop. Otherwise reverse the group in place so that its old first node points at <code>group_next</code>.",
                    "Hook the reversed group after <code>group_prev</code> and move <code>group_prev</code> to the group's new tail.",
                ],
                "steps": [
                    "Create <code>dummy = ListNode(0, head)</code> and <code>group_prev = dummy</code>.",
                    "Walk <code>kth</code> k steps from <code>group_prev</code>; if it becomes <code>None</code>, return <code>dummy.next</code>.",
                    "Save <code>group_next = kth.next</code>; reverse from <code>cur = group_prev.next</code> with <code>prev = group_next</code> until <code>cur is group_next</code>.",
                    "Save <code>first = group_prev.next</code> (the old first, now the tail) and link <code>group_prev.next = kth</code>.",
                    "Set <code>group_prev = first</code> and repeat.",
                ],
                "why": [
                    "Starting <code>prev</code> at <code>group_next</code> makes the reversed group's tail point at the rest of the list, so nothing is lost.",
                    "Only full groups are reversed, because the k-th node is found before any link changes.",
                    "Each node is visited a constant number of times: <strong>O(n)</strong> time, with a handful of pointers: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "group_prev = dummy, kth = 2, group_next = 3. Reverse 1, 2: 2 → 1 → 3. dummy → 2, group_prev = 1.",
                        "kth = 4, group_next = 5. Reverse 3, 4: 4 → 3 → 5. 1 → 4, group_prev = 3.",
                        "Walking for kth: 5, then None, so return.",
                        "Return dummy.next: <strong>[2, 1, 4, 3, 5]</strong>.",
                    ],
                    [
                        "kth = 3, group_next = 4. Reverse 1, 2, 3: 3 → 2 → 1 → 4. dummy → 3, group_prev = 1.",
                        "kth = 6, group_next = None. Reverse 4, 5, 6: 6 → 5 → 4 → None. 1 → 6, group_prev = 4.",
                        "Walking for kth: 4.next is None, so return.",
                        "Return dummy.next: <strong>[3, 2, 1, 6, 5, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why read <code>first = group_prev.next</code> after reversing?",
                     "<code>group_prev.next</code> still points at the old first node until it is relinked on the next line; that node is now the group's tail and the next <code>group_prev</code>."],
                    ["Why start <code>prev</code> at <code>group_next</code> instead of <code>None</code>?",
                     "The old first node becomes the group's tail and must point at the next group. Starting with <code>None</code> would cut the list."],
                    ["Why check for the k-th node before reversing?",
                     "If the group turns out short it must stay unchanged. Finding <code>kth</code> first avoids reversing and then undoing."],
                ],
            },
        },
    },
}
