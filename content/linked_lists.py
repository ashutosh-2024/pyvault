# -*- coding: utf-8 -*-
"""Linked Lists topic (NeetCode 250: Linked List). Same build contract as
content/dsa.py."""

PRELUDE_LL = '''import random
from collections import Counter, OrderedDict, defaultdict


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build_list(values):
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def to_list(head, limit=10 ** 5):
    out = []
    while head and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out
'''


LINKED_LISTS_TOPIC = dict(
    id="linked-lists",
    title="Linked Lists",
    prelude=PRELUDE_LL,
    sections=[

dict(
    id="linked-lists",
    title="Pointer manipulation",
    idea=[
        "Three moves solve almost every linked-list problem: a <strong>dummy head</strong> so the first node is not a special case, <strong>fast and slow pointers</strong> to find middles and cycles, and <strong>in-place reversal</strong> with three pointers. The O(n)-space versions usually copy the list into an array; the O(1) versions rewire the nodes you already have.",
    ],
    problems=[

    # ------------------------------------------------------------------ 206
    dict(
        id="reverse-linked-list",
        lc=206, slug="reverse-linked-list",
        name="Reverse Linked List",
        difficulty="easy",
        framing=[
            "Reverse a singly linked list and return the new head. The most important linked-list routine: half the problems on this page call it as a step.",
        ],
        approaches=[
            dict(
                name="Copy values to a list, write them back reversed",
                time="O(n)",
                space="O(n)",
                why=[
                    "Read the values into an array and overwrite the nodes in reverse order. Correct, but it moves data instead of links and needs O(n) memory &mdash; and in real systems, nodes often carry payloads you cannot cheaply copy.",
                ],
                code='''def reverse_list(head):
    vals, node = [], head
    while node:
        vals.append(node.val)
        node = node.next
    node = head
    while node:
        node.val = vals.pop()
        node = node.next
    return head''',
            ),
            dict(
                name="Recursive",
                time="O(n)",
                space="O(n)",
                why=[
                    "Reverse everything after the head, then hook the head on at the end: <code>head.next.next = head</code> (the old second node now points back), and <code>head.next = None</code>. Elegant, but the recursion depth is n &mdash; a 10,000-node list crashes CPython's default limit.",
                ],
                code='''def reverse_list(head):
    if head is None or head.next is None:
        return head
    new_head = reverse_list(head.next)
    head.next.next = head                  # the old next now points back
    head.next = None
    return new_head''',
            ),
            dict(
                name="Iterative with three pointers",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Walk the list flipping each link: save <code>nxt = cur.next</code>, point <code>cur.next</code> at <code>prev</code>, then advance both. When <code>cur</code> falls off the end, <code>prev</code> is the new head.",
                    "Saving <code>nxt</code> before overwriting the link is the whole trick &mdash; without it the rest of the list is lost.",
                ],
                code='''def reverse_list(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next                     # save before overwriting
        cur.next = prev
        prev, cur = cur, nxt
    return prev''',
            ),
        ],
        tests='''for vals in ([1, 2, 3, 4, 5], [1, 2], [], [7]):
    assert to_list(reverse_list(build_list(vals))) == vals[::-1]''',
    ),

    # ------------------------------------------------------------------ 21
    dict(
        id="merge-two-sorted-lists",
        lc=21, slug="merge-two-sorted-lists",
        name="Merge Two Sorted Lists",
        difficulty="easy",
        framing=[
            "Splice two sorted lists into one sorted list, reusing their nodes. The introduction to the <strong>dummy head</strong>: a placeholder node before the result, so appending the first real node is no different from appending any other.",
        ],
        approaches=[
            dict(
                name="Collect, sort, rebuild",
                time="O((m + n) log(m + n))",
                space="O(m + n)",
                why=["Pour all values into an array, sort, build a new list. Ignores both sortedness and the request to reuse nodes."],
                code='''def merge_two_lists(a, b):
    vals = []
    for node in (a, b):
        while node:
            vals.append(node.val)
            node = node.next
    return build_list(sorted(vals))''',
            ),
            dict(
                name="Recursive",
                time="O(m + n)",
                space="O(m + n)",
                why=[
                    "The smaller head comes first, followed by the merge of everything else. Very short, but one stack frame per node.",
                ],
                code='''def merge_two_lists(a, b):
    if a is None or b is None:
        return a or b
    if a.val <= b.val:
        a.next = merge_two_lists(a.next, b)
        return a
    b.next = merge_two_lists(a, b.next)
    return b''',
            ),
            dict(
                name="Iterative with a dummy head",
                time="O(m + n)",
                space="O(1)",
                best=True,
                why=[
                    "A <code>tail</code> pointer starts at a dummy node. Repeatedly attach the smaller of the two current heads and advance. When one list runs out, attach the other in one step &mdash; it is already sorted.",
                    "Using <code>&lt;=</code> takes from the first list on ties, which keeps the merge stable.",
                ],
                code='''def merge_two_lists(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b                     # the rest is already sorted
    return dummy.next''',
            ),
        ],
        tests='''assert to_list(merge_two_lists(build_list([1, 2, 4]), build_list([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
assert to_list(merge_two_lists(None, None)) == []
assert to_list(merge_two_lists(None, build_list([0]))) == [0]
rng = random.Random(0)
for _ in range(50):
    x = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 6)))
    y = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 6)))
    assert to_list(merge_two_lists(build_list(x), build_list(y))) == sorted(x + y)''',
    ),

    # ------------------------------------------------------------------ 141
    dict(
        id="linked-list-cycle",
        lc=141, slug="linked-list-cycle",
        name="Linked List Cycle",
        difficulty="easy",
        framing=[
            "Does the list loop back on itself? Following <code>next</code> forever never ends in a cycle, so you need either memory of visited nodes or a second pointer that can catch the first.",
        ],
        approaches=[
            dict(
                name="Hash set of visited nodes",
                time="O(n)",
                space="O(n)",
                why=[
                    "Store each node (by identity) as you pass it; reaching a stored node means a cycle. Direct and obviously correct.",
                ],
                code='''def has_cycle(head):
    seen = set()
    while head:
        if head in seen:
            return True
        seen.add(head)
        head = head.next
    return False''',
            ),
            dict(
                name="Floyd's tortoise and hare",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "A slow pointer moves one step, a fast pointer two. Without a cycle, fast reaches the end. With one, both eventually enter the cycle, and from then on the gap between them shrinks by one node per step &mdash; so fast catches slow within one lap.",
                    "Two pointers, no memory. The same idea finds the cycle's entrance (LeetCode 142) and the duplicate in Find the Duplicate Number below.",
                ],
                code='''def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False''',
            ),
        ],
        tests='''def make(vals, pos):
    head = build_list(vals)
    if pos >= 0:
        nodes, n = [], head
        while n:
            nodes.append(n); n = n.next
        nodes[-1].next = nodes[pos]
    return head

assert has_cycle(make([3, 2, 0, -4], 1)) is True
assert has_cycle(make([1, 2], 0)) is True
assert has_cycle(make([1], -1)) is False
assert has_cycle(None) is False
for n in range(1, 8):
    for pos in range(-1, n):
        assert has_cycle(make(list(range(n)), pos)) is (pos >= 0)''',
    ),

    # ------------------------------------------------------------------ 143
    dict(
        id="reorder-list",
        lc=143, slug="reorder-list",
        name="Reorder List",
        difficulty="medium",
        framing=[
            "Rearrange <code>L0 &rarr; L1 &rarr; &hellip; &rarr; Ln</code> into <code>L0 &rarr; Ln &rarr; L1 &rarr; Ln-1 &rarr; &hellip;</code> in place. The O(1)-space solution chains three routines from this page: find the middle, reverse the second half, merge alternately.",
        ],
        approaches=[
            dict(
                name="Array of nodes, relink from both ends",
                time="O(n)",
                space="O(n)",
                why=[
                    "Put the nodes in an array, then link <code>a[0], a[n-1], a[1], a[n-2], &hellip;</code> with two indices moving inward. Random access makes it trivial, at O(n) extra memory.",
                ],
                code='''def reorder_list(head):
    nodes = []
    while head:
        nodes.append(head)
        head = head.next
    i, j = 0, len(nodes) - 1
    while i < j:
        nodes[i].next = nodes[j]
        i += 1
        if i == j:
            break
        nodes[j].next = nodes[i]
        j -= 1
    if nodes:
        nodes[i].next = None''',
            ),
            dict(
                name="Middle, reverse the second half, merge",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Slow/fast pointers find the middle. Cut the list there and reverse the second half, so its nodes come in the order <code>Ln, Ln-1, &hellip;</code>. Then weave the two halves together, one node from each.",
                    "Three linear passes over the same nodes, no extra storage. The first half is the same length as or one longer than the second, so the weave always ends cleanly.",
                ],
                code='''def reorder_list(head):
    if not head:
        return
    slow = fast = head                          # 1. middle
    while fast.next and fast.next.next:
        slow, fast = slow.next, fast.next.next
    second, slow.next = slow.next, None         # cut

    prev = None                                 # 2. reverse the second half
    while second:
        second.next, prev, second = prev, second, second.next
    second = prev

    first = head                                # 3. weave
    while second:
        n1, n2 = first.next, second.next
        first.next, second.next = second, n1
        first, second = n1, n2''',
            ),
        ],
        tests='''for n in range(0, 9):
    head = build_list(list(range(n)))
    reorder_list(head)
    expect, i, j = [], 0, n - 1
    while i <= j:
        expect.append(i)
        if i != j:
            expect.append(j)
        i, j = i + 1, j - 1
    assert to_list(head) == expect, n''',
    ),

    # ------------------------------------------------------------------ 19
    dict(
        id="remove-nth-from-end",
        lc=19, slug="remove-nth-node-from-end-of-list",
        name="Remove Nth Node From End of List",
        difficulty="medium",
        framing=[
            "Delete the n-th node from the end. The follow-up asks for one pass. Two pointers spaced n apart solve it: when the front one reaches the end, the back one is just before the node to delete.",
        ],
        pitfall="Forgetting the case where the head itself is removed (n equals the list length). A dummy node in front makes that case identical to every other.",
        approaches=[
            dict(
                name="Count, then walk to the predecessor",
                time="O(L)",
                space="O(1)",
                why=[
                    "First pass: length L. The target is at index L - n, so walk L - n steps from a dummy node to its predecessor and unlink. Two passes, constant space &mdash; perfectly good, just not one pass.",
                ],
                code='''def remove_nth_from_end(head, n):
    length, node = 0, head
    while node:
        length, node = length + 1, node.next
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(length - n):
        prev = prev.next
    prev.next = prev.next.next
    return dummy.next''',
            ),
            dict(
                name="Array of nodes",
                time="O(L)",
                space="O(L)",
                why=[
                    "Store the nodes in an array during one pass, then the predecessor is at index <code>L - n - 1</code>. One pass, but O(L) memory.",
                ],
                code='''def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    nodes, node = [], dummy
    while node:
        nodes.append(node)
        node = node.next
    prev = nodes[len(nodes) - n - 1]
    prev.next = prev.next.next
    return dummy.next''',
            ),
            dict(
                name="One pass with a gap of n",
                time="O(L)",
                space="O(1)",
                best=True,
                why=[
                    "Move <code>fast</code> n + 1 steps ahead of <code>slow</code>, both starting at a dummy node. Advance them together until <code>fast</code> falls off the end. The gap is preserved, so <code>slow</code> is now the predecessor of the n-th node from the end.",
                ],
                code='''def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        slow, fast = slow.next, fast.next
    slow.next = slow.next.next
    return dummy.next''',
            ),
        ],
        tests='''assert to_list(remove_nth_from_end(build_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
assert to_list(remove_nth_from_end(build_list([1]), 1)) == []
assert to_list(remove_nth_from_end(build_list([1, 2]), 2)) == [2]
for L in range(1, 8):
    for n in range(1, L + 1):
        vals = list(range(L))
        expect = vals[:L - n] + vals[L - n + 1:]
        assert to_list(remove_nth_from_end(build_list(vals), n)) == expect''',
    ),

    # ------------------------------------------------------------------ 138
    dict(
        id="copy-list-random-pointer",
        lc=138, slug="copy-list-with-random-pointer",
        name="Copy List With Random Pointer",
        difficulty="medium",
        framing=[
            "Deep-copy a list whose nodes also have a <code>random</code> pointer to any node (or <code>None</code>). The difficulty: when copying node A, the copy of <code>A.random</code> may not exist yet. You need a way to find \"the copy of X\" for any original X.",
        ],
        approaches=[
            dict(
                name="Hash map from original to copy, two passes",
                time="O(n)",
                space="O(n)",
                why=[
                    "First pass: create every copy and record <code>old &rarr; new</code>. Second pass: set each copy's <code>next</code> and <code>random</code> by looking up the originals' targets. The map answers \"copy of X\" in O(1).",
                ],
                code='''def copy_random_list(head):
    copy = {None: None}
    node = head
    while node:
        copy[node] = Node(node.val)
        node = node.next
    node = head
    while node:
        copy[node].next = copy[node.next]
        copy[node].random = copy[node.random]
        node = node.next
    return copy[head]''',
            ),
            dict(
                name="Recursive clone with memoisation",
                time="O(n)",
                space="O(n)",
                why=[
                    "Treat the list as a graph: <code>clone(node)</code> returns the memoised copy if one exists, else creates it, stores it <em>before</em> recursing (so cycles through <code>random</code> terminate), then clones <code>next</code> and <code>random</code>. The same code copies any graph (see Clone Graph); recursion depth can reach n.",
                ],
                code='''def copy_random_list(head):
    memo = {}

    def clone(node):
        if node is None:
            return None
        if node in memo:
            return memo[node]
        c = memo[node] = Node(node.val)       # store before recursing
        c.next = clone(node.next)
        c.random = clone(node.random)
        return c

    return clone(head)''',
            ),
            dict(
                name="Interleave copies, then split",
                time="O(n)",
                space="O(1) extra",
                best=True,
                why=[
                    "Insert each copy directly after its original: <code>A &rarr; A' &rarr; B &rarr; B'</code>. Now \"the copy of X\" is simply <code>X.next</code>, so no map is needed: <code>A'.random = A.random.next</code>. Finally unweave the two lists, restoring the original.",
                    "Three passes and no auxiliary structure beyond the copies themselves, which are the output.",
                ],
                code='''def copy_random_list(head):
    node = head
    while node:                                # 1. A -> A' -> B -> B'
        node.next = Node(node.val, node.next)
        node = node.next.next
    node = head
    while node:                                # 2. copy of X is X.next
        if node.random:
            node.next.random = node.random.next
        node = node.next.next
    dummy = tail = Node(0)
    node = head
    while node:                                # 3. unweave, restoring the original
        c = node.next
        node.next = c.next
        tail.next = tail = c
        node = node.next
    return dummy.next''',
            ),
        ],
        tests='''class Node:
    def __init__(self, x, next=None, random=None):
        self.val, self.next, self.random = int(x), next, random


def make(spec):
    nodes = [Node(v) for v, _ in spec]
    for i, (_, r) in enumerate(spec):
        nodes[i].next = nodes[i + 1] if i + 1 < len(nodes) else None
        nodes[i].random = nodes[r] if r is not None else None
    return nodes[0] if nodes else None


def dump(head):
    nodes, n = [], head
    while n:
        nodes.append(n); n = n.next
    idx = {id(x): i for i, x in enumerate(nodes)}
    return [(x.val, idx[id(x.random)] if x.random else None) for x in nodes], {id(x) for x in nodes}

for spec in ([(7, None), (13, 0), (11, 4), (10, 2), (1, 0)], [(1, 1), (2, 1)], [(3, None), (3, 0), (3, None)], []):
    head = make(spec)
    before = dump(head)
    got = copy_random_list(head)
    after, copy_ids = dump(got)
    assert after == spec
    assert dump(head)[0] == before[0]                  # the original is untouched
    assert not (copy_ids & before[1])                  # a genuinely new list''',
    ),

    # ------------------------------------------------------------------ 2
    dict(
        id="add-two-numbers",
        lc=2, slug="add-two-numbers",
        name="Add Two Numbers",
        difficulty="medium",
        framing=[
            "Two numbers are stored as lists of digits in <em>reverse</em> order (least significant first). Return their sum in the same form. Reverse order is a gift: it is the order in which you add digits by hand, carrying to the left.",
        ],
        approaches=[
            dict(
                name="Convert to integers and back",
                time="O(m + n)",
                space="O(m + n)",
                why=[
                    "Read both lists into integers, add, and write the digits back. Python's arbitrary-precision integers make this correct for 100-digit numbers; in Java or C++ it overflows beyond 19 digits, which is the reason the problem exists.",
                ],
                code='''def add_two_numbers(l1, l2):
    def value(node):
        total, place = 0, 1
        while node:
            total += node.val * place
            place *= 10
            node = node.next
        return total

    s = value(l1) + value(l2)
    dummy = tail = ListNode()
    while True:
        s, d = divmod(s, 10)
        tail.next = tail = ListNode(d)
        if s == 0:
            return dummy.next''',
            ),
            dict(
                name="Digit by digit with a carry",
                time="O(max(m, n))",
                space="O(1) beyond the output",
                best=True,
                why=[
                    "Walk both lists together, adding the two digits and the carry; write <code>total % 10</code> and carry <code>total // 10</code>. Continue while either list has digits <em>or</em> a carry remains &mdash; the final carry can add one more digit (99 + 1 = 100).",
                    "Works for numbers of any length in any language, because no number larger than 19 is ever formed.",
                ],
                code='''def add_two_numbers(l1, l2):
    dummy = tail = ListNode()
    carry = 0
    while l1 or l2 or carry:
        total = carry + (l1.val if l1 else 0) + (l2.val if l2 else 0)
        carry, digit = divmod(total, 10)
        tail.next = tail = ListNode(digit)
        l1 = l1.next if l1 else None
        l2 = l2.next if l2 else None
    return dummy.next''',
            ),
        ],
        tests='''assert to_list(add_two_numbers(build_list([2, 4, 3]), build_list([5, 6, 4]))) == [7, 0, 8]
assert to_list(add_two_numbers(build_list([0]), build_list([0]))) == [0]
assert to_list(add_two_numbers(build_list([9] * 7), build_list([9] * 4))) == [8, 9, 9, 9, 0, 0, 0, 1]
rng = random.Random(1)
for _ in range(50):
    a, b = rng.randint(0, 10 ** 12), rng.randint(0, 10 ** 12)
    digits = lambda x: [int(d) for d in str(x)[::-1]]
    assert to_list(add_two_numbers(build_list(digits(a)), build_list(digits(b)))) == digits(a + b)''',
    ),

    # ------------------------------------------------------------------ 287
    dict(
        id="find-duplicate-number",
        lc=287, slug="find-the-duplicate-number",
        name="Find The Duplicate Number",
        difficulty="medium",
        framing=[
            "n + 1 integers in <code>[1, n]</code>, exactly one value repeated (possibly many times). Find it without modifying the array and in O(1) extra space. It sits on the linked-list page because the O(n) solution treats the array as a linked list &mdash; <code>i &rarr; nums[i]</code> &mdash; and the duplicate as the entrance to a cycle.",
        ],
        approaches=[
            dict(
                name="Sort and look for neighbours",
                time="O(n log n)",
                space="O(1)&ndash;O(n)",
                tag="modifies the input",
                why=["Equal values are adjacent after sorting. Breaks the no-modification rule (or costs O(n) for a copy)."],
                code='''def find_duplicate(nums):
    s = sorted(nums)
    for a, b in zip(s, s[1:]):
        if a == b:
            return a''',
            ),
            dict(
                name="Hash set",
                time="O(n)",
                space="O(n)",
                why=["The first value seen twice. Linear time, linear memory."],
                code='''def find_duplicate(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return x
        seen.add(x)''',
            ),
            dict(
                name="Binary search on the value, counting",
                time="O(n log n)",
                space="O(1)",
                why=[
                    "Pigeonhole: if more than <code>mid</code> values are &le; mid, the duplicate is &le; mid (there are only mid distinct values in <code>[1, mid]</code>). That count is monotonic, so binary-search the smallest such mid. Read-only and constant space, at O(n) per step.",
                ],
                code='''def find_duplicate(nums):
    lo, hi = 1, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(x <= mid for x in nums) > mid:
            hi = mid                           # too many small values: dup <= mid
        else:
            lo = mid + 1
    return lo''',
            ),
            dict(
                name="Floyd's cycle detection on i &rarr; nums[i]",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Follow <code>i &rarr; nums[i]</code> from index 0. Index 0 has no incoming edge (values are &ge; 1), and the duplicate value has two incoming edges, so the walk from 0 must enter a cycle exactly at the duplicate.",
                    "Phase 1: slow moves one step, fast two, until they meet inside the cycle. Phase 2: restart one pointer at 0 and move both one step at a time; they meet at the cycle's entrance. The distance from the start to the entrance equals the distance from the meeting point to the entrance (mod the cycle length) &mdash; the standard Floyd argument.",
                ],
                code='''def find_duplicate(nums):
    slow = fast = 0
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = 0
    while slow != fast:                        # both walk to the cycle entrance
        slow, fast = nums[slow], nums[fast]
    return slow''',
            ),
        ],
        tests='''assert find_duplicate([1, 3, 4, 2, 2]) == 2
assert find_duplicate([3, 1, 3, 4, 2]) == 3
assert find_duplicate([3, 3, 3, 3, 3]) == 3
rng = random.Random(2)
for _ in range(80):
    n = rng.randint(1, 12)
    dup = rng.randint(1, n)
    rest = rng.sample([v for v in range(1, n + 1) if v != dup], rng.randint(0, n - 1))
    nums = rest + [dup] * (n + 1 - len(rest))
    rng.shuffle(nums)
    original = nums[:]
    assert find_duplicate(nums) == dup and nums == original''',
    ),

    # ------------------------------------------------------------------ 92
    dict(
        id="reverse-linked-list-ii",
        lc=92, slug="reverse-linked-list-ii",
        name="Reverse Linked List II",
        difficulty="medium",
        framing=[
            "Reverse only positions <code>left..right</code> (1-indexed) in one pass. The reversal itself is Reverse Linked List; the work is reconnecting the reversed segment to the nodes before and after it.",
        ],
        approaches=[
            dict(
                name="Copy the segment's values, write them back reversed",
                time="O(n)",
                space="O(right - left)",
                why=["Collect the segment's values and overwrite them in reverse. Easy, but moves values, not links."],
                code='''def reverse_between(head, left, right):
    node, vals = head, []
    for i in range(1, right + 1):
        if i >= left:
            vals.append(node.val)
        node = node.next
    node = head
    for i in range(1, right + 1):
        if i >= left:
            node.val = vals.pop()
        node = node.next
    return head''',
            ),
            dict(
                name="Head insertion in one pass",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "Walk a pointer <code>prev</code> to the node just before position <code>left</code> (a dummy handles <code>left = 1</code>). Then, <code>right - left</code> times, take the node after the segment's current first node and move it to the front of the segment, right after <code>prev</code>. Each move grows the reversed prefix by one.",
                    "No separate reconnection step is needed: <code>prev</code> and the tail of the segment stay linked to the rest of the list throughout.",
                ],
                code='''def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(left - 1):
        prev = prev.next
    cur = prev.next                             # becomes the segment's tail
    for _ in range(right - left):
        move = cur.next
        cur.next = move.next
        move.next = prev.next                   # to the front of the segment
        prev.next = move
    return dummy.next''',
            ),
        ],
        tests='''assert to_list(reverse_between(build_list([1, 2, 3, 4, 5]), 2, 4)) == [1, 4, 3, 2, 5]
assert to_list(reverse_between(build_list([5]), 1, 1)) == [5]
for n in range(1, 8):
    for l in range(1, n + 1):
        for r in range(l, n + 1):
            vals = list(range(n))
            expect = vals[:l - 1] + vals[l - 1:r][::-1] + vals[r:]
            assert to_list(reverse_between(build_list(vals), l, r)) == expect''',
    ),

    # ------------------------------------------------------------------ 622
    dict(
        id="design-circular-queue",
        lc=622, slug="design-circular-queue",
        name="Design Circular Queue",
        difficulty="medium",
        framing=[
            "A fixed-capacity FIFO queue with <code>enQueue</code>, <code>deQueue</code>, <code>Front</code>, <code>Rear</code>, <code>isEmpty</code>, <code>isFull</code>. The circular buffer reuses freed slots at the front by wrapping indices around with modulo arithmetic.",
        ],
        approaches=[
            dict(
                name="Python list with pop(0)",
                time="deQueue O(n)",
                space="O(k)",
                tag="naive",
                why=[
                    "Append to enqueue, <code>pop(0)</code> to dequeue. <code>pop(0)</code> shifts every remaining element, so dequeue is O(n) &mdash; the inefficiency a ring buffer exists to avoid.",
                ],
                code='''class MyCircularQueue:
    def __init__(self, k):
        self.k, self.items = k, []

    def enQueue(self, value):
        if len(self.items) == self.k:
            return False
        self.items.append(value)
        return True

    def deQueue(self):
        if not self.items:
            return False
        self.items.pop(0)
        return True

    def Front(self):
        return self.items[0] if self.items else -1

    def Rear(self):
        return self.items[-1] if self.items else -1

    def isEmpty(self):
        return not self.items

    def isFull(self):
        return len(self.items) == self.k''',
            ),
            dict(
                name="Array ring buffer with head and count",
                time="O(1) all",
                space="O(k)",
                best=True,
                why=[
                    "A fixed array of size k, a <code>head</code> index and a <code>count</code>. The tail position is <code>(head + count) % k</code>, so enqueue writes there; dequeue just advances <code>head</code>. Storing the count (instead of a separate tail) removes the classic ambiguity where head == tail could mean either empty or full.",
                ],
                code='''class MyCircularQueue:
    def __init__(self, k):
        self.buf, self.k = [0] * k, k
        self.head = self.count = 0

    def enQueue(self, value):
        if self.count == self.k:
            return False
        self.buf[(self.head + self.count) % self.k] = value
        self.count += 1
        return True

    def deQueue(self):
        if self.count == 0:
            return False
        self.head = (self.head + 1) % self.k
        self.count -= 1
        return True

    def Front(self):
        return self.buf[self.head] if self.count else -1

    def Rear(self):
        return self.buf[(self.head + self.count - 1) % self.k] if self.count else -1

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == self.k''',
            ),
            dict(
                name="Singly linked list with a size cap",
                time="O(1) all",
                space="O(current size)",
                why=[
                    "Keep head and tail nodes and a size; enqueue appends at the tail, dequeue drops the head. Also O(1), and memory follows the current size rather than the capacity, at the cost of a node allocation per element.",
                ],
                code='''class MyCircularQueue:
    def __init__(self, k):
        self.k, self.size = k, 0
        self.head = self.tail = None

    def enQueue(self, value):
        if self.size == self.k:
            return False
        node = ListNode(value)
        if self.tail:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self.size += 1
        return True

    def deQueue(self):
        if self.size == 0:
            return False
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self.size -= 1
        return True

    def Front(self):
        return self.head.val if self.head else -1

    def Rear(self):
        return self.tail.val if self.tail else -1

    def isEmpty(self):
        return self.size == 0

    def isFull(self):
        return self.size == self.k''',
            ),
        ],
        tests='''q = MyCircularQueue(3)
assert [q.enQueue(1), q.enQueue(2), q.enQueue(3), q.enQueue(4)] == [True, True, True, False]
assert q.Rear() == 3 and q.isFull() is True and q.deQueue() is True
assert q.enQueue(4) is True and q.Rear() == 4 and q.Front() == 2
rng = random.Random(3)
for _ in range(10):
    k = rng.randint(1, 5)
    q, model = MyCircularQueue(k), []
    for _ in range(100):
        r = rng.random()
        if r < 0.45:
            v = rng.randint(0, 99)
            assert q.enQueue(v) == (len(model) < k)
            if len(model) < k: model.append(v)
        elif r < 0.8:
            assert q.deQueue() == bool(model)
            if model: model.pop(0)
        assert q.Front() == (model[0] if model else -1) and q.Rear() == (model[-1] if model else -1)
        assert q.isEmpty() == (not model) and q.isFull() == (len(model) == k)''',
    ),

    # ------------------------------------------------------------------ 146
    dict(
        id="lru-cache",
        lc=146, slug="lru-cache",
        name="LRU Cache",
        difficulty="medium",
        framing=[
            "A cache of fixed capacity with <code>get</code> and <code>put</code> in O(1); when full, <code>put</code> evicts the <strong>least recently used</strong> key. A hash map finds keys in O(1); a doubly linked list keeps them in recency order with O(1) moves. The problem is how to combine the two.",
        ],
        approaches=[
            dict(
                name="Dict plus a recency list",
                time="O(n) per operation",
                space="O(capacity)",
                tag="naive",
                why=[
                    "Keep values in a dict and keys in a Python list ordered by recency. Each access removes the key from the list (O(n)) and appends it; eviction pops the front (also O(n)). Correct, but linear.",
                ],
                code='''class LRUCache:
    def __init__(self, capacity):
        self.cap, self.vals, self.order = capacity, {}, []

    def get(self, key):
        if key not in self.vals:
            return -1
        self.order.remove(key)
        self.order.append(key)
        return self.vals[key]

    def put(self, key, value):
        if key in self.vals:
            self.order.remove(key)
        elif len(self.vals) == self.cap:
            del self.vals[self.order.pop(0)]
        self.vals[key] = value
        self.order.append(key)''',
            ),
            dict(
                name="OrderedDict",
                time="O(1)",
                space="O(capacity)",
                tag="library",
                why=[
                    "<code>collections.OrderedDict</code> is exactly a hash map over a doubly linked list. <code>move_to_end</code> marks a key as most recent and <code>popitem(last=False)</code> evicts the oldest, both O(1). Mention it, then build it yourself &mdash; that is what the question is testing.",
                ],
                code='''class LRUCache:
    def __init__(self, capacity):
        self.cap, self.data = capacity, OrderedDict()

    def get(self, key):
        if key not in self.data:
            return -1
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.cap:
            self.data.popitem(last=False)''',
            ),
            dict(
                name="Hash map + doubly linked list, by hand",
                time="O(1)",
                space="O(capacity)",
                best=True,
                why=[
                    "The map stores <code>key &rarr; node</code>. The list runs from least to most recent between two sentinel nodes, so insertion and removal never need null checks. <code>get</code> unlinks the node and re-inserts it before the right sentinel. <code>put</code> does the same for an existing key, or creates a node, evicting the node after the left sentinel if over capacity.",
                    "Doubly linked is essential: removing a node from the middle in O(1) needs its predecessor, which a singly linked list does not give you.",
                ],
                code='''class DNode:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.old, self.new = DNode(), DNode()        # sentinels
        self.old.next, self.new.prev = self.new, self.old

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _append(self, node):                         # insert as most recent
        node.prev, node.next = self.new.prev, self.new
        self.new.prev.next = node
        self.new.prev = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._unlink(node)
        self._append(node)
        return node.val

    def put(self, key, value):
        if key in self.map:
            self._unlink(self.map[key])
        node = self.map[key] = DNode(key, value)
        self._append(node)
        if len(self.map) > self.cap:
            lru = self.old.next
            self._unlink(lru)
            del self.map[lru.key]''',
            ),
        ],
        tests='''c = LRUCache(2)
c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)
assert c.get(2) == -1
c.put(4, 4)
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
rng = random.Random(4)
for _ in range(10):
    cap = rng.randint(1, 4)
    c, model = LRUCache(cap), OrderedDict()
    for _ in range(200):
        k = rng.randint(0, 6)
        if rng.random() < 0.5:
            v = rng.randint(0, 99); c.put(k, v)
            model[k] = v; model.move_to_end(k)
            if len(model) > cap: model.popitem(last=False)
        else:
            expect = model[k] if k in model else -1
            if k in model: model.move_to_end(k)
            assert c.get(k) == expect''',
    ),

    # ------------------------------------------------------------------ 460
    dict(
        id="lfu-cache",
        lc=460, slug="lfu-cache",
        name="LFU Cache",
        difficulty="hard",
        framing=[
            "Evict the <strong>least frequently</strong> used key; among ties, the least recently used. Both operations in O(1). LRU needed one recency list; LFU needs one recency list <em>per frequency</em>, plus the current minimum frequency.",
        ],
        approaches=[
            dict(
                name="Scan for the victim",
                time="put O(n)",
                space="O(capacity)",
                tag="naive",
                why=[
                    "Store each key's value, use count and last-use time. On eviction, scan for the smallest <code>(count, last_used)</code>. Correct; eviction is linear.",
                ],
                code='''class LFUCache:
    def __init__(self, capacity):
        self.cap, self.time = capacity, 0
        self.data = {}                                 # key -> [value, count, last_used]

    def get(self, key):
        if key not in self.data:
            return -1
        self.time += 1
        entry = self.data[key]
        entry[1] += 1
        entry[2] = self.time
        return entry[0]

    def put(self, key, value):
        if self.cap == 0:
            return
        self.time += 1
        if key in self.data:
            e = self.data[key]
            e[0], e[1], e[2] = value, e[1] + 1, self.time
            return
        if len(self.data) == self.cap:
            victim = min(self.data, key=lambda k: (self.data[k][1], self.data[k][2]))
            del self.data[victim]
        self.data[key] = [value, 1, self.time]''',
            ),
            dict(
                name="Frequency buckets of ordered dicts, plus min frequency",
                time="O(1)",
                space="O(capacity)",
                best=True,
                why=[
                    "<code>buckets[f]</code> is an ordered dict of the keys used exactly f times, in recency order. Touching a key moves it from bucket f to the end of bucket f + 1; if bucket f became empty and was the minimum, the minimum becomes f + 1.",
                    "Eviction removes the first (least recent) key of <code>buckets[min_freq]</code>. A new key always has frequency 1, so after inserting one the minimum is reset to 1. Every step is a constant number of hash-map and linked-list operations.",
                ],
                code='''class LFUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.vals, self.freq = {}, {}
        self.buckets = defaultdict(OrderedDict)        # freq -> keys, oldest first
        self.min_freq = 0

    def _touch(self, key):
        f = self.freq[key]
        del self.buckets[f][key]
        if not self.buckets[f]:
            del self.buckets[f]
            if self.min_freq == f:
                self.min_freq = f + 1
        self.freq[key] = f + 1
        self.buckets[f + 1][key] = None

    def get(self, key):
        if key not in self.vals:
            return -1
        self._touch(key)
        return self.vals[key]

    def put(self, key, value):
        if self.cap == 0:
            return
        if key in self.vals:
            self.vals[key] = value
            self._touch(key)
            return
        if len(self.vals) == self.cap:
            victim, _ = self.buckets[self.min_freq].popitem(last=False)
            if not self.buckets[self.min_freq]:
                del self.buckets[self.min_freq]
            del self.vals[victim], self.freq[victim]
        self.vals[key], self.freq[key] = value, 1
        self.buckets[1][key] = None
        self.min_freq = 1''',
            ),
        ],
        tests='''c = LFUCache(2)
c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)
assert c.get(2) == -1 and c.get(3) == 3
c.put(4, 4)
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
rng = random.Random(5)
for _ in range(10):
    cap = rng.randint(0, 4)
    c, data, t = LFUCache(cap), {}, 0
    for _ in range(200):
        k = rng.randint(0, 6); t += 1
        if rng.random() < 0.5:
            v = rng.randint(0, 99); c.put(k, v)
            if cap == 0:
                continue
            if k in data:
                data[k] = [v, data[k][1] + 1, t]
            else:
                if len(data) == cap:
                    del data[min(data, key=lambda x: (data[x][1], data[x][2]))]
                data[k] = [v, 1, t]
        else:
            if k in data:
                data[k][1] += 1; data[k][2] = t
                assert c.get(k) == data[k][0]
            else:
                assert c.get(k) == -1''',
    ),

    # ------------------------------------------------------------------ 25
    dict(
        id="reverse-nodes-k-group",
        lc=25, slug="reverse-nodes-in-k-group",
        name="Reverse Nodes In K Group",
        difficulty="hard",
        framing=[
            "Reverse the list k nodes at a time; a final group shorter than k stays as it is. The follow-up asks for O(1) extra memory. Each group is Reverse Linked List II on a window; the difficulty is bookkeeping the links between groups.",
        ],
        approaches=[
            dict(
                name="Stack each group",
                time="O(n)",
                space="O(k)",
                why=[
                    "Push up to k nodes onto a stack. If the stack has k nodes, pop them to relink in reverse; otherwise attach the short group unchanged. A stack of size k is the only extra memory.",
                ],
                code='''def reverse_k_group(head, k):
    dummy = tail = ListNode()
    node = head
    while node:
        stack, probe = [], node
        while probe and len(stack) < k:
            stack.append(probe)
            probe = probe.next
        if len(stack) < k:
            tail.next = node                   # short tail group stays as is
            break
        while stack:
            tail.next = tail = stack.pop()
        tail.next = None
        node = probe
    return dummy.next''',
            ),
            dict(
                name="Recursive",
                time="O(n)",
                space="O(n / k)",
                why=[
                    "Check that k nodes exist; if so, reverse them and let the old group head (now its tail) point to the result of recursing on the rest. One frame per group.",
                ],
                code='''def reverse_k_group(head, k):
    node = head
    for _ in range(k):
        if node is None:
            return head                        # fewer than k: leave as is
        node = node.next
    prev, cur = reverse_k_group(node, k), head
    for _ in range(k):
        cur.next, prev, cur = prev, cur, cur.next
    return prev''',
            ),
            dict(
                name="Iterative, group by group",
                time="O(n)",
                space="O(1)",
                best=True,
                why=[
                    "<code>group_prev</code> is the node before the current group (a dummy at first). Find the group's k-th node; if it does not exist, stop. Reverse the group with the usual three-pointer loop, starting <code>prev</code> at the node <em>after</em> the group so the reversed group's tail links onward automatically. Then point <code>group_prev</code> at the new group head and move <code>group_prev</code> to the new group tail.",
                ],
                code='''def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            cur.next, prev, cur = prev, cur, cur.next
        first = group_prev.next                # old first, now the group's tail
        group_prev.next = kth
        group_prev = first''',
            ),
        ],
        tests='''assert to_list(reverse_k_group(build_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
assert to_list(reverse_k_group(build_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
for n in range(0, 10):
    for k in range(1, 6):
        vals = list(range(n))
        expect = []
        for i in range(0, n, k):
            chunk = vals[i:i + k]
            expect += chunk[::-1] if len(chunk) == k else chunk
        assert to_list(reverse_k_group(build_list(vals), k)) == expect, (n, k)''',
    ),
    ],
),
    ],
)
