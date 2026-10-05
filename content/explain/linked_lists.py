"""Write-ups for the Linked Lists topic."""

EXPLAIN = {
    # ------------------------------------------------------------------ reverse linked list
    "reverse-linked-list": {
        "example": {"call": "to_list(reverse_list(build_list([1, 2, 3, 4])))", "expect": "[4, 3, 2, 1]"},
        "approaches": {
            "Copy values to a list, write them back reversed": {
                "idea": [
                    "Leave the links alone and reverse the <em>values</em> instead.",
                    "Read every value into a Python list, then walk the nodes again and write the values back from the end of that list.",
                ],
                "steps": [
                    "First pass: append each <code>node.val</code> to <code>vals</code>.",
                    "Second pass: set <code>node.val = vals.pop()</code> for each node, front to back.",
                    "Return the original head.",
                ],
                "why": [
                    "<code>pop()</code> hands the values back last-first, so the first node gets the last value, and so on.",
                    "It is O(n) time but O(n) extra memory, and it copies data instead of relinking, which is often unacceptable when nodes carry large payloads.",
                ],
                "dry": [
                    "Pass 1 collects vals = [1, 2, 3, 4].",
                    "Pass 2: the first node gets 4, the second 3, the third 2, the fourth 1.",
                    "The list now reads <strong>[4, 3, 2, 1]</strong>, with the same nodes in the same order holding new values.",
                ],
            },
            "Recursive": {
                "idea": [
                    "Trust recursion to reverse everything <em>after</em> the head; it returns the new head (the old last node).",
                    "At that point the old second node is the tail of the reversed rest, so hook the head on behind it: <code>head.next.next = head</code>.",
                    "Then cut <code>head.next</code>, because the head is now the last node.",
                ],
                "steps": [
                    "Base case: an empty or one-node list is already reversed.",
                    "<code>new_head = reverse_list(head.next)</code>.",
                    "<code>head.next.next = head</code>; <code>head.next = None</code>.",
                    "Return <code>new_head</code> unchanged on the way back up.",
                ],
                "why": [
                    "Each frame flips exactly one link, the one between its node and the next.",
                    "It is O(n) time, but the recursion depth is n: a list of 10,000 nodes exceeds CPython's default recursion limit.",
                ],
                "dry": [
                    "The calls go down to node 4, a single node, which is returned as new_head.",
                    "In the frame for 3: 3.next is 4, so 4.next = 3 and 3.next = None. The list from 4 reads 4 → 3.",
                    "In the frame for 2: 3.next = 2, 2.next = None, giving 4 → 3 → 2.",
                    "In the frame for 1: 2.next = 1, 1.next = None, giving 4 → 3 → 2 → 1.",
                    "new_head (4) is passed all the way up: <strong>[4, 3, 2, 1]</strong>.",
                ],
            },
            "Iterative with three pointers": {
                "idea": [
                    "Walk the list once, turning each <code>next</code> link around to point backwards.",
                    "<code>prev</code> is the already-reversed part, <code>cur</code> is the node being flipped, and <code>nxt</code> remembers the rest of the list before the link is overwritten.",
                    "When <code>cur</code> runs off the end, <code>prev</code> is the new head.",
                ],
                "steps": [
                    "<code>prev = None</code>, <code>cur = head</code>.",
                    "Loop: <code>nxt = cur.next</code>; <code>cur.next = prev</code>; <code>prev, cur = cur, nxt</code>.",
                    "Return <code>prev</code>.",
                ],
                "why": [
                    "After each step, <code>prev</code> heads a correctly reversed prefix and <code>cur</code> heads the untouched rest.",
                    "Saving <code>nxt</code> first is essential; without it the rest of the list is lost. It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "cur = 1: save nxt = 2, point 1 → None. prev = 1, cur = 2.",
                    "cur = 2: save 3, point 2 → 1. prev = 2 (2 → 1), cur = 3.",
                    "cur = 3: point 3 → 2. prev = 3 (3 → 2 → 1), cur = 4.",
                    "cur = 4: point 4 → 3. prev = 4, cur = None, so the loop ends.",
                    "Return prev: <strong>[4, 3, 2, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ merge two sorted lists
    "merge-two-sorted-lists": {
        "example": {"call": "to_list(merge_two_lists(build_list([1, 4, 7]), build_list([2, 3, 8, 9])))",
                    "expect": "[1, 2, 3, 4, 7, 8, 9]"},
        "approaches": {
            "Collect, sort, rebuild": {
                "idea": [
                    "Ignore that the inputs are sorted: pour all values into one list, sort it, and build a fresh linked list.",
                ],
                "steps": [
                    "Walk both lists, appending every value.",
                    "<code>build_list(sorted(vals))</code>.",
                ],
                "why": [
                    "Sorting all values certainly gives the merged order.",
                    "It costs O((m + n) log(m + n)) and allocates new nodes instead of splicing the existing ones, as the problem asks.",
                ],
                "dry": [
                    "Collected: [1, 4, 7, 2, 3, 8, 9].",
                    "Sorted: [1, 2, 3, 4, 7, 8, 9].",
                    "A new list is built: <strong>[1, 2, 3, 4, 7, 8, 9]</strong>.",
                ],
            },
            "Recursive": {
                "idea": [
                    "The merged list starts with the smaller of the two heads.",
                    "After that comes the merge of everything else, which is the same problem one node smaller.",
                ],
                "steps": [
                    "If either list is empty, return the other one.",
                    "If <code>a.val &lt;= b.val</code>: <code>a.next = merge(a.next, b)</code> and return <code>a</code>.",
                    "Otherwise do the same with b first.",
                ],
                "why": [
                    "Each call places exactly one node in its final position.",
                    "It is O(m + n) time, with one stack frame per node: O(m + n) space.",
                ],
                "dry": [
                    "1 ≤ 2, so the result starts with 1, followed by merge(4…, 2…).",
                    "2 &lt; 4, then 3 &lt; 4, so 2 and 3 are placed next.",
                    "4 ≤ 8, then 7 ≤ 8, so 4 and 7 are placed.",
                    "The first list is empty, so the call returns the rest of the second list, 8 → 9, in one go.",
                    "The result is <strong>[1, 2, 3, 4, 7, 8, 9]</strong>.",
                ],
            },
            "Iterative with a dummy head": {
                "idea": [
                    "Build the result by repeatedly attaching the smaller of the two current heads to a tail pointer.",
                    "A dummy node in front means the first attachment needs no special case.",
                    "When one list runs out, attach the other in one step; it is already sorted.",
                ],
                "steps": [
                    "<code>dummy = tail = ListNode()</code>.",
                    "While both lists have nodes: attach the smaller head (taking from a on ties), advance that list, then advance <code>tail</code>.",
                    "<code>tail.next = a or b</code>; return <code>dummy.next</code>.",
                ],
                "why": [
                    "The tail always ends a sorted list of the smallest nodes taken so far.",
                    "Using <code>&lt;=</code> keeps equal values in their original order (a stable merge). It is O(m + n) time and O(1) space.",
                ],
                "dry": [
                    "1 vs 2: attach 1. 4 vs 2: attach 2. 4 vs 3: attach 3.",
                    "4 vs 8: attach 4. 7 vs 8: attach 7. a is now empty.",
                    "Attach the remainder 8 → 9 with one pointer assignment.",
                    "dummy.next gives <strong>[1, 2, 3, 4, 7, 8, 9]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ linked list cycle
    "linked-list-cycle": {
        "example": {"setup": "head = build_list([3, 2, 0, -4])\nhead.next.next.next.next = head.next      # -4 links back to 2",
                    "call": "has_cycle(head)", "expect": "True"},
        "approaches": {
            "Hash set of visited nodes": {
                "idea": [
                    "Follow the links and remember every node you have stood on, by identity, not by value.",
                    "Standing on a remembered node again proves there is a loop; reaching <code>None</code> proves there is not.",
                ],
                "steps": [
                    "While the current node exists: if it is in <code>seen</code>, return <code>True</code>.",
                    "Add it and move to <code>next</code>.",
                    "Return <code>False</code> at the end of the list.",
                ],
                "why": [
                    "A list without a cycle visits each node once, and a cycle forces a revisit within n steps.",
                    "It is O(n) time and O(n) space for the set.",
                ],
                "dry": [
                    "Visit 3, 2, 0, -4, adding each to seen.",
                    "-4's next is the node 2, already in seen.",
                    "The result is <strong>True</strong>.",
                ],
            },
            "Floyd's tortoise and hare": {
                "idea": [
                    "Run two pointers: slow moves one node per step, fast moves two.",
                    "Without a cycle, fast falls off the end. With a cycle, both end up circling it, and fast gains one node per step on slow, so it must land on slow within one lap.",
                    "No memory is needed beyond the two pointers.",
                ],
                "steps": [
                    "<code>slow = fast = head</code>.",
                    "While <code>fast</code> and <code>fast.next</code> exist: advance slow by 1 and fast by 2.",
                    "If they point to the same node, return <code>True</code>; if the loop ends, return <code>False</code>.",
                ],
                "why": [
                    "Inside the cycle the gap between them shrinks by exactly one each step, so it cannot skip past zero.",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "Start: slow = fast = 3.",
                    "Step 1: slow = 2, fast = 0.",
                    "Step 2: slow = 0, fast goes -4 then back to 2.",
                    "Step 3: slow = -4, fast goes 0 then -4. They meet, so the result is <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reorder list
    "reorder-list": {
        "example": {"setup": "head = build_list([1, 2, 3, 4, 5, 6])\nreorder_list(head)",
                    "call": "to_list(head)", "expect": "[1, 6, 2, 5, 3, 4]"},
        "approaches": {
            "Array of nodes, relink from both ends": {
                "idea": [
                    "The target order alternates first, last, second, second-to-last, and so on.",
                    "With the nodes in an array, both ends can be reached instantly, so link them with two indices moving inward.",
                ],
                "steps": [
                    "Collect the nodes into <code>nodes</code>.",
                    "With <code>i = 0</code> and <code>j = n - 1</code>: link <code>nodes[i] → nodes[j]</code>, step i; if they meet, stop; link <code>nodes[j] → nodes[i]</code>, step j.",
                    "Terminate the list with <code>nodes[i].next = None</code>.",
                ],
                "why": [
                    "Each link is set exactly once in the alternating order.",
                    "It is O(n) time and O(n) extra space for the array.",
                ],
                "dry": [
                    "nodes = [1, 2, 3, 4, 5, 6].",
                    "1 → 6, then 6 → 2. Next 2 → 5, then 5 → 3.",
                    "3 → 4; i and j meet at 4, so stop.",
                    "4.next = None. The list reads <strong>[1, 6, 2, 5, 3, 4]</strong>.",
                ],
            },
            "Middle, reverse the second half, merge": {
                "idea": [
                    "The answer interleaves the first half with the <em>reversed</em> second half.",
                    "So: find the middle with slow/fast pointers, cut there, reverse the second half in place, then weave the two halves together.",
                    "Each step is a standard linked-list pattern, and nothing extra is stored.",
                ],
                "steps": [
                    "Advance slow by 1 and fast by 2 while <code>fast.next</code> and <code>fast.next.next</code> exist; slow ends at the last node of the first half.",
                    "Cut after slow and reverse the second half with three pointers.",
                    "Weave: take one node from each half in turn.",
                ],
                "why": [
                    "The first half has the same number of nodes as the second, or one more, so the weave always ends cleanly.",
                    "It is three linear passes: O(n) time and O(1) space.",
                ],
                "dry": [
                    "Middle search: slow 1 → 2 → 3 while fast 1 → 3 → 5; then fast.next.next is None, so slow = 3.",
                    "Cut: the first half is 1 → 2 → 3 and the second is 4 → 5 → 6.",
                    "Reverse the second half: 6 → 5 → 4.",
                    "Weave: 1, 6, 2, 5, 3, 4.",
                    "The result is <strong>[1, 6, 2, 5, 3, 4]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ remove nth from end
    "remove-nth-from-end": {
        "example": {"call": "to_list(remove_nth_from_end(build_list([1, 2, 3, 4, 5]), 2))", "expect": "[1, 2, 3, 5]"},
        "approaches": {
            "Count, then walk to the predecessor": {
                "idea": [
                    "The n-th node from the end is at index <code>L - n</code> from the front, once the length L is known.",
                    "To unlink it we need its predecessor, so walk <code>L - n</code> steps starting from a dummy node in front of the head.",
                ],
                "steps": [
                    "First pass: count L.",
                    "Second pass: from <code>dummy</code>, step <code>L - n</code> times to reach the predecessor.",
                    "<code>prev.next = prev.next.next</code>; return <code>dummy.next</code>.",
                ],
                "why": [
                    "The dummy handles removing the head itself (when n = L) with no special case.",
                    "It is two passes: O(L) time and O(1) space.",
                ],
                "dry": [
                    "L = 5, so the target index is 5 - 2 = 3, which is node 4.",
                    "From dummy, 3 steps reach node 3.",
                    "Unlink: 3 → 5. The result is <strong>[1, 2, 3, 5]</strong>.",
                ],
            },
            "Array of nodes": {
                "idea": [
                    "Store every node, including a dummy at the front, in an array during one pass.",
                    "Then the predecessor of the target is simply <code>nodes[len - n - 1]</code>.",
                ],
                "steps": [
                    "Collect <code>dummy</code> and all nodes into <code>nodes</code>.",
                    "<code>prev = nodes[len(nodes) - n - 1]</code>; unlink <code>prev.next</code>.",
                ],
                "why": [
                    "With random access, counting from the end is just index arithmetic.",
                    "It is one pass, but O(L) extra memory.",
                ],
                "dry": [
                    "nodes = [dummy, 1, 2, 3, 4, 5], length 6.",
                    "prev = nodes[6 - 2 - 1] = nodes[3] = node 3.",
                    "Unlink node 4: <strong>[1, 2, 3, 5]</strong>.",
                ],
            },
            "One pass with a gap of n": {
                "idea": [
                    "Put two pointers n + 1 nodes apart, both starting at a dummy, and move them together.",
                    "When the leading pointer falls off the end, the trailing pointer is exactly n + 1 nodes before the end: the predecessor of the node to remove.",
                ],
                "steps": [
                    "Advance <code>fast</code> n + 1 times from the dummy.",
                    "Move <code>slow</code> and <code>fast</code> together until <code>fast</code> is <code>None</code>.",
                    "Unlink <code>slow.next</code>.",
                ],
                "why": [
                    "The gap between the pointers never changes, so it encodes \"n from the end\" without knowing L.",
                    "It is one pass: O(L) time and O(1) space.",
                ],
                "dry": [
                    "fast moves 3 steps from dummy: 1, 2, 3.",
                    "Together: (slow 1, fast 4), (slow 2, fast 5), (slow 3, fast None).",
                    "slow is node 3; unlink node 4.",
                    "The result is <strong>[1, 2, 3, 5]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ copy list with random pointer
    "copy-list-random-pointer": {
        "example": {"setup": ("class Node:\n"
                              "    def __init__(self, x, next=None, random=None):\n"
                              "        self.val, self.next, self.random = int(x), next, random\n"
                              "a, b, c, d = Node(7), Node(13), Node(11), Node(10)\n"
                              "a.next, b.next, c.next = b, c, d\n"
                              "b.random, c.random, d.random = a, d, b       # 7 has no random\n"
                              "def dump(h):\n"
                              "    nodes = []\n"
                              "    while h:\n"
                              "        nodes.append(h); h = h.next\n"
                              "    return [(n.val, nodes.index(n.random) if n.random else None) for n in nodes]\n"
                              "copy = copy_random_list(a)"),
                    "call": "[dump(copy), copy is not a, dump(a)]",
                    "expect": "[[(7, None), (13, 0), (11, 3), (10, 1)], True, [(7, None), (13, 0), (11, 3), (10, 1)]]"},
        "approaches": {
            "Hash map from original to copy, two passes": {
                "idea": [
                    "The hard part is the <code>random</code> pointer: it may point at a node whose copy has not been made yet.",
                    "So first make a copy of every node and remember <code>original → copy</code> in a dictionary.",
                    "Then wire up each copy's <code>next</code> and <code>random</code> by looking up the copies of the originals' targets.",
                ],
                "steps": [
                    "<code>copy = {None: None}</code>, so missing pointers map to <code>None</code>.",
                    "Pass 1: <code>copy[node] = Node(node.val)</code> for every node.",
                    "Pass 2: <code>copy[node].next = copy[node.next]</code> and <code>copy[node].random = copy[node.random]</code>.",
                    "Return <code>copy[head]</code>.",
                ],
                "why": [
                    "After pass 1 every possible target has a copy, so pass 2 never looks one up too early.",
                    "It is O(n) time and O(n) space for the map.",
                ],
                "dry": [
                    "Pass 1 creates 7', 13', 11', 10' and maps each original to its copy.",
                    "Pass 2 for 13: next → copy[11] = 11', random → copy[7] = 7'.",
                    "For 11: random → copy[10] = 10'. For 10: random → copy[13] = 13'. 7' keeps random None.",
                    "The copy reads <strong>[(7, None), (13, 0), (11, 3), (10, 1)]</strong>, made of new nodes, and the original is unchanged.",
                ],
            },
            "Recursive clone with memoisation": {
                "idea": [
                    "Treat the list as a graph whose edges are <code>next</code> and <code>random</code>.",
                    "<code>clone(node)</code> returns the existing copy if there is one; otherwise it creates a copy, records it <em>before</em> recursing, and then clones the two neighbours.",
                    "Recording first is what stops random pointers that loop back from recursing forever.",
                ],
                "steps": [
                    "If node is <code>None</code>, return <code>None</code>; if it is in <code>memo</code>, return its copy.",
                    "<code>c = memo[node] = Node(node.val)</code>.",
                    "<code>c.next = clone(node.next)</code>, then <code>c.random = clone(node.random)</code>.",
                ],
                "why": [
                    "Every node is copied exactly once, and every pointer resolves to that copy.",
                    "It is O(n) time; the recursion depth can reach n through the next chain.",
                ],
                "dry": [
                    "clone(7) creates 7', then clones next: 13' is created, then its next 11', then its next 10'.",
                    "10'.next = None. 10'.random = clone(13) is already in memo, so it returns 13'.",
                    "Back in 11': random = clone(10) gives the memoised 10'. Back in 13': random = clone(7) gives the memoised 7'.",
                    "7'.random = None. The copy reads <strong>[(7, None), (13, 0), (11, 3), (10, 1)]</strong>.",
                ],
            },
            "Interleave copies, then split": {
                "idea": [
                    "Instead of a dictionary, put each copy right after its original: 7 → 7' → 13 → 13' → ….",
                    "Now \"the copy of X\" is simply <code>X.next</code>, so <code>X'.random = X.random.next</code>.",
                    "Finally pull the copies out into their own list and restore the original links.",
                ],
                "steps": [
                    "Pass 1: insert <code>Node(val)</code> after every original.",
                    "Pass 2: for each original with a random target, set <code>node.next.random = node.random.next</code>.",
                    "Pass 3: unweave: every original points past its copy again, and the copies are chained together behind a dummy.",
                ],
                "why": [
                    "The interleaving gives the original→copy mapping for free.",
                    "It is three linear passes and O(1) extra space; the copies themselves are the output.",
                ],
                "dry": [
                    "After pass 1: 7 → 7' → 13 → 13' → 11 → 11' → 10 → 10'.",
                    "Pass 2: 13'.random = 13.random.next = 7'. 11'.random = 10.next = 10'. 10'.random = 13.next = 13'.",
                    "Pass 3 splits the lists: the original goes back to 7 → 13 → 11 → 10, and the copy is 7' → 13' → 11' → 10'.",
                    "Both read <strong>[(7, None), (13, 0), (11, 3), (10, 1)]</strong>, as separate node sets.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ add two numbers
    "add-two-numbers": {
        "example": {"call": "to_list(add_two_numbers(build_list([9, 9, 9, 9]), build_list([9, 9])))",
                    "expect": "[8, 9, 0, 0, 1]"},
        "approaches": {
            "Convert to integers and back": {
                "idea": [
                    "The digits are stored least significant first, so digit i is worth 10<sup>i</sup>.",
                    "Turn each list into a Python int, add them, and write the digits of the sum back out, lowest first.",
                ],
                "steps": [
                    "<code>value(node)</code>: accumulate <code>node.val × place</code>, multiplying <code>place</code> by 10 each step.",
                    "Add the two values.",
                    "Repeatedly <code>divmod(s, 10)</code> to emit digits until s is 0.",
                ],
                "why": [
                    "Python's integers have no size limit, so even 100-digit numbers work.",
                    "In Java or C++ this overflows beyond 19 digits, which is why the problem exists. It is O(m + n) time.",
                ],
                "dry": [
                    "value([9, 9, 9, 9]) = 9999 and value([9, 9]) = 99.",
                    "9999 + 99 = 10098.",
                    "The digits emitted lowest first are 8, 9, 0, 0, 1: <strong>[8, 9, 0, 0, 1]</strong>.",
                ],
            },
            "Digit by digit with a carry": {
                "idea": [
                    "Do column addition straight on the lists; they are already in the right order (lowest digit first).",
                    "Each column adds the two digits (0 if a list has run out) and the carry, writes <code>total % 10</code>, and carries <code>total // 10</code>.",
                    "A final carry adds one more digit, as in 99 + 1 = 100.",
                ],
                "steps": [
                    "While either list has a node or <code>carry</code> is non-zero: sum the available digits and the carry.",
                    "<code>carry, digit = divmod(total, 10)</code>; append a node with <code>digit</code>.",
                    "Advance whichever lists still have nodes.",
                ],
                "why": [
                    "No number larger than 19 is ever formed, so this works in any language.",
                    "It is O(max(m, n)) time and O(1) extra space beyond the output.",
                ],
                "dry": [
                    "9 + 9 = 18: write 8, carry 1.",
                    "9 + 9 + 1 = 19: write 9, carry 1.",
                    "9 + 0 + 1 = 10: write 0, carry 1. 9 + 0 + 1 = 10: write 0, carry 1.",
                    "Both lists are empty but the carry is 1: write 1.",
                    "The result is <strong>[8, 9, 0, 0, 1]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ find the duplicate
    "find-duplicate-number": {
        "example": {"call": "find_duplicate([1, 4, 3, 2, 5, 3])", "expect": "3"},
        "approaches": {
            "Sort and look for neighbours": {
                "idea": [
                    "After sorting, equal values sit next to each other, so the duplicate is the first adjacent equal pair.",
                ],
                "steps": [
                    "<code>s = sorted(nums)</code>.",
                    "Return the first <code>a</code> with <code>a == next</code>.",
                ],
                "why": [
                    "It is correct, but it either modifies the array (forbidden) or copies it: O(n log n) time and O(n) space.",
                ],
                "dry": [
                    "Sorted: [1, 2, 3, 3, 4, 5].",
                    "The adjacent pair 3, 3 gives <strong>3</strong>.",
                ],
            },
            "Hash set": {
                "idea": [
                    "Scan and remember what you have seen; the first value seen twice is the duplicate.",
                ],
                "steps": [
                    "For each x: if it is in <code>seen</code>, return it; otherwise add it.",
                ],
                "why": [
                    "It is O(n) time but O(n) extra space, which breaks the constant-space rule.",
                ],
                "dry": [
                    "seen grows 1, 4, 3, 2, 5.",
                    "The next value 3 is already in seen, so the result is <strong>3</strong>.",
                ],
            },
            "Binary search on the value, counting": {
                "idea": [
                    "Pigeonhole: the values 1..mid can fill at most mid slots without repeating.",
                    "So if more than mid numbers are ≤ mid, the duplicate must be ≤ mid; otherwise it is above mid.",
                    "That test is monotonic in mid, so binary-search the smallest mid where it is true.",
                ],
                "steps": [
                    "<code>lo, hi = 1, n</code> (with n = len(nums) - 1).",
                    "<code>mid = (lo + hi) // 2</code>; count values ≤ mid.",
                    "If the count is greater than mid, <code>hi = mid</code>; otherwise <code>lo = mid + 1</code>. Return <code>lo</code>.",
                ],
                "why": [
                    "The array is never modified and only O(1) extra space is used.",
                    "There are O(log n) rounds of an O(n) count: O(n log n) time.",
                ],
                "dry": [
                    "lo = 1, hi = 5. mid = 3: the values ≤ 3 are 1, 3, 2, 3, which is 4 &gt; 3, so hi = 3.",
                    "mid = 2: the values ≤ 2 are 1, 2, which is 2, not more than 2, so lo = 3.",
                    "lo = hi = 3, so the result is <strong>3</strong>.",
                ],
            },
            "Floyd's cycle detection on i &rarr; nums[i]": {
                "idea": [
                    "Treat each index as a node with one outgoing edge, <code>i → nums[i]</code>.",
                    "No value is 0, so index 0 has no incoming edge and is a safe starting point; the duplicate value has two incoming edges.",
                    "Walking from 0 must therefore enter a cycle, and it enters exactly at the duplicate. Floyd's algorithm finds a cycle's entrance with two pointers.",
                ],
                "steps": [
                    "Phase 1: slow = nums[slow] and fast = nums[nums[fast]] until they meet inside the cycle.",
                    "Phase 2: reset slow to 0 and move both one step at a time.",
                    "They meet at the cycle's entrance, which is the duplicate.",
                ],
                "why": [
                    "The distance from the start to the entrance equals the distance from the meeting point to the entrance (modulo the cycle length), which is the standard Floyd argument.",
                    "It is O(n) time and O(1) space, with no modification.",
                ],
                "dry": [
                    "The walk from 0 is 0 → 1 → 4 → 5 → 3 → 2 → 3 → 2 …, so the cycle is 3 ⇄ 2 and its entrance is 3.",
                    "Phase 1: (slow, fast) = (1, 4), then (4, 3), then (5, 3), then (3, 3), so they meet at 3.",
                    "Phase 2: slow restarts at 0. (slow, fast) = (1, 2), (4, 3), (5, 2), (3, 3).",
                    "They meet at the entrance: <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse linked list II
    "reverse-linked-list-ii": {
        "example": {"call": "to_list(reverse_between(build_list([1, 2, 3, 4, 5, 6]), 2, 5))", "expect": "[1, 5, 4, 3, 2, 6]"},
        "approaches": {
            "Copy the segment's values, write them back reversed": {
                "idea": [
                    "Only positions left..right change, so collect their values and write them back in reverse order.",
                    "The links are never touched.",
                ],
                "steps": [
                    "First walk: append values at positions left..right.",
                    "Second walk: overwrite those positions with <code>vals.pop()</code>.",
                ],
                "why": [
                    "It is correct, O(n) time, with O(right - left) extra space; it moves values rather than nodes.",
                ],
                "dry": [
                    "The values at positions 2..5 are [2, 3, 4, 5].",
                    "They are written back as 5, 4, 3, 2.",
                    "The result is <strong>[1, 5, 4, 3, 2, 6]</strong>.",
                ],
            },
            "Head insertion in one pass": {
                "idea": [
                    "Stop at <code>prev</code>, the node just before the segment; <code>cur</code> is the segment's first node, which will end up as its last.",
                    "Repeatedly take the node right after <code>cur</code> and move it to the front of the segment, just after <code>prev</code>.",
                    "After <code>right - left</code> moves the whole segment is reversed, still connected to the rest of the list.",
                ],
                "steps": [
                    "Walk <code>prev</code> left - 1 steps from a dummy.",
                    "<code>cur = prev.next</code>.",
                    "Repeat right - left times: <code>move = cur.next</code>; <code>cur.next = move.next</code>; <code>move.next = prev.next</code>; <code>prev.next = move</code>.",
                ],
                "why": [
                    "Each move grows the reversed front of the segment by one node, and both <code>prev</code> and <code>cur</code> stay connected to the list.",
                    "It is one pass, O(n) time and O(1) space; the dummy handles left = 1.",
                ],
                "dry": [
                    "prev = 1, cur = 2.",
                    "Move 3 to the front: 1 → 3 → 2 → 4 → 5 → 6.",
                    "Move 4 (now after 2): 1 → 4 → 3 → 2 → 5 → 6.",
                    "Move 5: 1 → 5 → 4 → 3 → 2 → 6.",
                    "The result is <strong>[1, 5, 4, 3, 2, 6]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ design circular queue
    "design-circular-queue": {
        "example": {"setup": "q = MyCircularQueue(3)",
                    "call": "[q.enQueue(1), q.enQueue(2), q.enQueue(3), q.enQueue(4), q.Rear(), q.deQueue(), q.enQueue(4), q.Front(), q.Rear(), q.isFull()]",
                    "expect": "[True, True, True, False, 3, True, True, 2, 4, True]"},
        "approaches": {
            "Python list with pop(0)": {
                "idea": [
                    "A plain list used as a queue: append at the back and remove from the front.",
                    "The capacity check makes it bounded, but <code>pop(0)</code> shifts every remaining element left.",
                ],
                "steps": [
                    "<code>enQueue</code>: reject when full, otherwise append.",
                    "<code>deQueue</code>: reject when empty, otherwise <code>pop(0)</code>.",
                    "<code>Front</code> and <code>Rear</code> are <code>items[0]</code> and <code>items[-1]</code>, or -1 when empty.",
                ],
                "why": [
                    "It behaves correctly, but dequeue costs O(n), which is exactly what a ring buffer exists to avoid.",
                ],
                "dry": [
                    "Enqueue 1, 2, 3: items = [1, 2, 3]. Enqueue 4 is rejected: <strong>False</strong>.",
                    "Rear = <strong>3</strong>. deQueue removes 1 by shifting: [2, 3].",
                    "Enqueue 4: [2, 3, 4]. Front = <strong>2</strong>, Rear = <strong>4</strong>, isFull = <strong>True</strong>.",
                ],
            },
            "Array ring buffer with head and count": {
                "idea": [
                    "Use a fixed array of k slots and let the queue wrap around the end.",
                    "Keep <code>head</code> (the index of the front) and <code>count</code>; the next free slot is <code>(head + count) % k</code>.",
                    "Storing count (not a separate tail) removes the classic ambiguity of whether head == tail means empty or full.",
                ],
                "steps": [
                    "<code>enQueue</code>: if not full, write at <code>(head + count) % k</code> and increment count.",
                    "<code>deQueue</code>: if not empty, <code>head = (head + 1) % k</code> and decrement count.",
                    "<code>Rear</code> is at <code>(head + count - 1) % k</code>.",
                ],
                "why": [
                    "Indices wrap modulo k, so freed slots at the front are reused.",
                    "Every operation is O(1), and space is exactly k.",
                ],
                "dry": [
                    "Enqueue 1, 2, 3 fill slots 0, 1, 2; count = 3. Enqueue 4: full, <strong>False</strong>.",
                    "Rear = buf[(0 + 3 - 1) % 3] = buf[2] = <strong>3</strong>.",
                    "deQueue: head = 1, count = 2. The 1 is still in slot 0, but it is now free.",
                    "Enqueue 4 writes to slot (1 + 2) % 3 = 0, wrapping around: buf = [4, 2, 3].",
                    "Front = buf[1] = <strong>2</strong>, Rear = buf[(1 + 3 - 1) % 3] = buf[0] = <strong>4</strong>, isFull = <strong>True</strong>.",
                ],
            },
            "Singly linked list with a size cap": {
                "idea": [
                    "A linked queue with head and tail pointers, plus a size counter enforcing the capacity.",
                    "Enqueue appends at the tail, and dequeue drops the head.",
                ],
                "steps": [
                    "<code>enQueue</code>: if not full, link a new node after <code>tail</code> (or make it the head when empty).",
                    "<code>deQueue</code>: move <code>head</code> forward; clear <code>tail</code> if the queue became empty.",
                    "<code>Front</code> and <code>Rear</code> read head and tail.",
                ],
                "why": [
                    "Every operation is O(1). Memory follows the current size rather than the capacity, at the cost of one allocation per element.",
                ],
                "dry": [
                    "Enqueue 1, 2, 3 gives 1 → 2 → 3. Enqueue 4: size 3 = k, so <strong>False</strong>.",
                    "Rear = <strong>3</strong>. deQueue: head moves to 2.",
                    "Enqueue 4: 2 → 3 → 4.",
                    "Front = <strong>2</strong>, Rear = <strong>4</strong>, isFull = <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LRU cache
    "lru-cache": {
        "example": {"setup": "c = LRUCache(2)",
                    "call": "[c.put(1, 1), c.put(2, 2), c.get(1), c.put(3, 3), c.get(2), c.put(4, 4), c.get(1), c.get(3), c.get(4)]",
                    "expect": "[None, None, 1, None, -1, None, -1, 3, 4]"},
        "approaches": {
            "Dict plus a recency list": {
                "idea": [
                    "A dictionary stores the values, and a Python list keeps the keys ordered from least to most recently used.",
                    "Every access moves the key to the end of the list; eviction removes the key at the front.",
                ],
                "steps": [
                    "<code>get</code>: if present, <code>order.remove(key)</code>, append it, and return the value.",
                    "<code>put</code>: for an existing key, remove it from the order; when full, evict <code>order.pop(0)</code>.",
                    "Store the value and append the key.",
                ],
                "why": [
                    "The order list always reflects recency, so the front is the least recently used key.",
                    "<code>remove</code> and <code>pop(0)</code> are O(n), so every operation is linear.",
                ],
                "dry": [
                    "put 1, put 2: order [1, 2]. get(1) = <strong>1</strong> and moves 1 to the end: order [2, 1].",
                    "put 3 when full: evict the front, 2. order [1, 3].",
                    "get(2) = <strong>-1</strong>. put 4: evict 1. order [3, 4].",
                    "get(1) = <strong>-1</strong>, get(3) = <strong>3</strong>, get(4) = <strong>4</strong>.",
                ],
            },
            "OrderedDict": {
                "idea": [
                    "<code>collections.OrderedDict</code> is already a hash map threaded through a doubly linked list.",
                    "<code>move_to_end</code> marks a key as most recent, and <code>popitem(last=False)</code> removes the oldest, both O(1).",
                ],
                "steps": [
                    "<code>get</code>: if present, <code>move_to_end(key)</code> and return the value.",
                    "<code>put</code>: <code>move_to_end</code> if present, then assign; if over capacity, <code>popitem(last=False)</code>.",
                ],
                "why": [
                    "The dictionary's order is the recency order, maintained in O(1).",
                    "Mention it in an interview, then build the structure by hand, because that is what is being tested.",
                ],
                "dry": [
                    "put 1, put 2: order 1, 2. get(1) = <strong>1</strong>, order 2, 1.",
                    "put 3: three keys, so pop the oldest, 2.",
                    "get(2) = <strong>-1</strong>. put 4: pop the oldest, 1.",
                    "get(1) = <strong>-1</strong>, get(3) = <strong>3</strong>, get(4) = <strong>4</strong>.",
                ],
            },
            "Hash map + doubly linked list, by hand": {
                "idea": [
                    "The map finds a key's node in O(1); the doubly linked list keeps nodes in recency order and can unlink any node in O(1).",
                    "Two sentinel nodes, <code>old</code> and <code>new</code>, bracket the list, so insertions and removals never need null checks.",
                    "The node just after <code>old</code> is always the least recently used one.",
                ],
                "steps": [
                    "<code>_unlink(node)</code>: connect its neighbours to each other.",
                    "<code>_append(node)</code>: insert it just before <code>new</code>, as the most recent.",
                    "<code>get</code>: unlink and append the node, then return its value.",
                    "<code>put</code>: unlink any old node for the key, append a fresh one, and if over capacity unlink <code>old.next</code> and delete it from the map.",
                ],
                "why": [
                    "Removing a node from the middle needs its predecessor, which only a doubly linked list provides in O(1).",
                    "Every operation is O(1), and space is O(capacity).",
                ],
                "dry": [
                    "put 1, put 2: old ⇄ 1 ⇄ 2 ⇄ new.",
                    "get(1) = <strong>1</strong>: unlink 1 and append it, giving old ⇄ 2 ⇄ 1 ⇄ new.",
                    "put 3: append, giving old ⇄ 2 ⇄ 1 ⇄ 3 ⇄ new; over capacity, so evict old.next = 2.",
                    "get(2) = <strong>-1</strong>. put 4: append 4 and evict old.next = 1, giving old ⇄ 3 ⇄ 4 ⇄ new.",
                    "get(1) = <strong>-1</strong>, get(3) = <strong>3</strong>, get(4) = <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ LFU cache
    "lfu-cache": {
        "example": {"setup": "c = LFUCache(2)",
                    "call": "[c.put(1, 1), c.put(2, 2), c.get(1), c.put(3, 3), c.get(2), c.get(3), c.put(4, 4), c.get(1), c.get(3), c.get(4)]",
                    "expect": "[None, None, 1, None, -1, 3, None, -1, 3, 4]"},
        "approaches": {
            "Scan for the victim": {
                "idea": [
                    "For each key, store its value, how many times it was used, and when it was last used.",
                    "When an eviction is needed, scan for the key with the smallest (count, last-used) pair: least frequent, and among ties least recent.",
                ],
                "steps": [
                    "<code>get</code>: bump the count and the timestamp.",
                    "<code>put</code> of an existing key: update the value, count and time.",
                    "<code>put</code> of a new key when full: delete the <code>min</code> key by <code>(count, time)</code>, then insert with count 1.",
                ],
                "why": [
                    "The tuple comparison encodes the eviction rule exactly.",
                    "Eviction scans every key: O(capacity) per put.",
                ],
                "dry": [
                    "put 1 (count 1, t1), put 2 (count 1, t2). get(1) = <strong>1</strong>, so key 1 has count 2.",
                    "put 3 when full: the smallest (count, time) is key 2's (1, t2), so evict 2.",
                    "get(2) = <strong>-1</strong>. get(3) = <strong>3</strong>, so key 3 has count 2.",
                    "put 4: keys 1 and 3 both have count 2; key 1 was used earlier, so evict 1.",
                    "get(1) = <strong>-1</strong>, get(3) = <strong>3</strong>, get(4) = <strong>4</strong>.",
                ],
            },
            "Frequency buckets of ordered dicts, plus min frequency": {
                "idea": [
                    "Group keys by use count: <code>buckets[f]</code> is an ordered dict of the keys used exactly f times, oldest first.",
                    "Track <code>min_freq</code>, the lowest non-empty bucket; the victim is always the oldest key in that bucket.",
                    "Touching a key moves it from bucket f to the end of bucket f + 1, and a new key always resets <code>min_freq</code> to 1.",
                ],
                "steps": [
                    "<code>_touch(key)</code>: remove it from bucket f (deleting an empty bucket, and bumping <code>min_freq</code> if that was the minimum), then add it to bucket f + 1.",
                    "<code>get</code>: touch the key and return its value.",
                    "<code>put</code> of a new key when full: <code>popitem(last=False)</code> from <code>buckets[min_freq]</code>, then insert into bucket 1 with <code>min_freq = 1</code>.",
                ],
                "why": [
                    "Each bucket keeps recency order, so ties on frequency are broken correctly.",
                    "Every step is a constant number of dictionary operations: O(1).",
                ],
                "dry": [
                    "put 1, put 2: bucket1 = [1, 2], min 1. get(1) = <strong>1</strong>: bucket1 = [2], bucket2 = [1].",
                    "put 3: evict the oldest in bucket1, which is 2; bucket1 becomes [3].",
                    "get(2) = <strong>-1</strong>. get(3) = <strong>3</strong>: bucket2 = [1, 3]; bucket1 is empty and was the minimum, so min = 2.",
                    "put 4: evict the oldest in bucket2, which is 1. bucket1 = [4], min = 1.",
                    "get(1) = <strong>-1</strong>, get(3) = <strong>3</strong>, get(4) = <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ reverse nodes in k-group
    "reverse-nodes-k-group": {
        "example": {"call": "to_list(reverse_k_group(build_list([1, 2, 3, 4, 5, 6, 7, 8]), 3))",
                    "expect": "[3, 2, 1, 6, 5, 4, 7, 8]"},
        "approaches": {
            "Stack each group": {
                "idea": [
                    "A stack reverses whatever is pushed onto it, so push k nodes and pop them back out in reverse order.",
                    "If fewer than k nodes remain, attach them unchanged.",
                ],
                "steps": [
                    "Push up to k nodes starting from the current node.",
                    "If the stack holds k nodes, pop them one by one onto the result's tail; otherwise attach the short group as it is and stop.",
                    "Continue from the node after the group.",
                ],
                "why": [
                    "Each node is pushed and popped once: O(n) time, with an O(k) stack.",
                ],
                "dry": [
                    "Push 1, 2, 3 and pop 3, 2, 1: the result so far is 3, 2, 1.",
                    "Push 4, 5, 6 and pop 6, 5, 4: the result is 3, 2, 1, 6, 5, 4.",
                    "Push 7, 8: only 2 &lt; 3 nodes, so attach 7 → 8 unchanged.",
                    "The result is <strong>[3, 2, 1, 6, 5, 4, 7, 8]</strong>.",
                ],
            },
            "Recursive": {
                "idea": [
                    "Check that k nodes exist; if not, leave the list alone.",
                    "Otherwise recursively process everything after the first k nodes, then reverse those k nodes so the old first node (now the last) points at that result.",
                ],
                "steps": [
                    "Walk k nodes; if the list ends first, return <code>head</code> unchanged.",
                    "<code>prev = reverse_k_group(node, k)</code>, where node is the (k+1)-th.",
                    "Reverse k nodes with prev starting at that result, then return the new group head.",
                ],
                "why": [
                    "Each call handles one group and links it to the already-processed rest.",
                    "It is O(n) time, with recursion depth n / k.",
                ],
                "dry": [
                    "Call on 1: 3 nodes exist, so recurse on 4.",
                    "Call on 4: recurse on 7. Call on 7: only 7, 8 are left, so return 7 → 8 unchanged.",
                    "Back at 4: reverse 4, 5, 6 onto 7 → 8, giving 6 → 5 → 4 → 7 → 8.",
                    "Back at 1: reverse 1, 2, 3 onto that, giving <strong>[3, 2, 1, 6, 5, 4, 7, 8]</strong>.",
                ],
            },
            "Iterative, group by group": {
                "idea": [
                    "Keep <code>group_prev</code>, the node just before the current group (a dummy at first).",
                    "Find the group's k-th node; if there is none, stop.",
                    "Reverse the group with the usual three-pointer loop, but start <code>prev</code> at the node <em>after</em> the group, so the reversed group's tail links onward automatically.",
                ],
                "steps": [
                    "Walk k steps from <code>group_prev</code> to <code>kth</code>; return if the list ends first.",
                    "<code>group_next = kth.next</code>; reverse the nodes from <code>group_prev.next</code> up to <code>group_next</code>.",
                    "Point <code>group_prev.next</code> at <code>kth</code> (the new head), and move <code>group_prev</code> to the old first node (the new tail).",
                ],
                "why": [
                    "Each group is reversed in place and stitched to its neighbours in O(1).",
                    "It is O(n) time and O(1) space.",
                ],
                "dry": [
                    "group_prev = dummy. kth = 3, group_next = 4. Reverse 1, 2, 3 with prev starting at 4: 3 → 2 → 1 → 4.",
                    "dummy.next = 3, and group_prev moves to 1.",
                    "kth = 6, group_next = 7. Reverse 4, 5, 6: 6 → 5 → 4 → 7. 1.next = 6, and group_prev = 4.",
                    "Looking for the next kth runs out after 7, 8, so stop.",
                    "The result is <strong>[3, 2, 1, 6, 5, 4, 7, 8]</strong>.",
                ],
            },
        },
    },
}
