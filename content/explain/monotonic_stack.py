"""Write-ups for the Stacks topic (monotonic-stack)."""

EXPLAIN = {
    # ------------------------------------------------------------------ baseball game
    "baseball-game": {
        "examples": [
            {"call": 'cal_points(["5", "-2", "4", "C", "D", "9", "+", "+"])', "expect": "27"},
            {"call": 'cal_points(["5", "2", "C", "D", "+"])', "expect": "30"},
        ],
        "approaches": {
            "Stack of valid scores": {
                "idea": [
                    "Every operation only looks at the <em>most recent</em> valid scores, which is exactly what the top of a stack gives you.",
                    "<code>C</code> cancels the last score, so the score before it must become the latest again. Popping the stack does that for free.",
                    "<code>D</code> and <code>+</code> read the top one or two scores and record a new one: peek, then push.",
                ],
                "steps": [
                    "Start with an empty list <code>stack</code>.",
                    "Loop over each token <code>op</code> in <code>operations</code>.",
                    "For <code>\"+\"</code>, push <code>stack[-1] + stack[-2]</code>. For <code>\"D\"</code>, push <code>2 * stack[-1]</code>.",
                    "For <code>\"C\"</code>, pop the top score so it no longer counts and is no longer visible to later operations.",
                    "Anything else is a number: push <code>int(op)</code>, which also handles signs such as <code>\"-2\"</code>.",
                    "After the last token, return <code>sum(stack)</code>.",
                ],
                "why": [
                    "The stack always equals the current record of valid scores in order, so <code>stack[-1]</code> is always the “previous score” the rules talk about.",
                    "Because <code>C</code> really removes the score, a later <code>D</code> or <code>+</code> sees the score before it, as the rules require.",
                    "Each token does O(1) work and the final sum is one pass, so the time is <strong>O(n)</strong>. The stack can hold every score, so space is <strong>O(n)</strong>.",
                ],
                "dry": [
                    [
                        "<code>\"5\"</code>, <code>\"-2\"</code>, <code>\"4\"</code>: three pushes, stack = [5, −2, 4].",
                        "<code>\"C\"</code>: pop the 4, stack = [5, −2]. The 4 is gone for good.",
                        "<code>\"D\"</code>: 2 × −2 = −4, stack = [5, −2, −4]. <code>\"9\"</code>: stack = [5, −2, −4, 9].",
                        "<code>\"+\"</code>: −4 + 9 = 5, stack = [5, −2, −4, 9, 5].",
                        "<code>\"+\"</code>: 9 + 5 = 14, stack = [5, −2, −4, 9, 5, 14].",
                        "Sum: 5 − 2 − 4 + 9 + 5 + 14 = <strong>27</strong>.",
                    ],
                    [
                        "<code>\"5\"</code>, <code>\"2\"</code>: stack = [5, 2].",
                        "<code>\"C\"</code>: pop the 2, stack = [5]. The 5 is the latest score again.",
                        "<code>\"D\"</code>: doubles 5, not the cancelled 2. stack = [5, 10].",
                        "<code>\"+\"</code>: 5 + 10 = 15, stack = [5, 10, 15].",
                        "Sum: 5 + 10 + 15 = <strong>30</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not keep a running total instead of summing at the end?",
                     "You can, but <code>C</code> then has to subtract the popped value. Summing once at the end is simpler and still O(n)."],
                    ["Does <code>int(op)</code> handle negative scores?",
                     "Yes. <code>int(\"-2\")</code> is −2, and none of the operation letters can be mistaken for a number because they are checked first."],
                    ["Can <code>stack[-2]</code> fail?",
                     "Not on valid input: the problem guarantees <code>+</code> always has two previous scores and <code>C</code>/<code>D</code> always have one. On invalid input it would raise an IndexError."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid parentheses
    "valid-parentheses": {
        "examples": [
            {"call": 'is_valid("([{}])[")', "expect": "False"},
            {"call": 'is_valid("{[]}()")', "expect": "True"},
        ],
        "approaches": {
            "Repeatedly delete adjacent pairs": {
                "idea": [
                    "Any non-empty valid string contains an innermost pair such as <code>()</code>, <code>[]</code> or <code>{}</code> with nothing between the two brackets.",
                    "Deleting such a pair leaves a string that is valid exactly when the original was, so pairs can be peeled away until nothing changes.",
                    "If the string shrinks to empty it was valid. If it gets stuck with brackets left, it was not.",
                ],
                "steps": [
                    "Set <code>prev = None</code> so the loop runs at least once.",
                    "At the start of each round, remember the current string in <code>prev</code>.",
                    "Remove every <code>()</code>, then every <code>[]</code>, then every <code>{}</code> with chained <code>str.replace</code> calls.",
                    "Stop when a round leaves the string unchanged (<code>prev == s</code>).",
                    "Return <code>s == \"\"</code>.",
                ],
                "why": [
                    "Removing an adjacent matched pair never turns an invalid string into a valid one or the other way round, so the final verdict is right.",
                    "A valid non-empty string always has an adjacent pair to delete, so it cannot get stuck before reaching empty.",
                    "Each round is O(n), and a string like <code>([([([...])])])</code> loses only one pair per round, so there can be n/2 rounds: <strong>O(n²)</strong> time.",
                    "Each <code>replace</code> builds a new string, so the extra space is <strong>O(n)</strong>.",
                ],
                "dry": [
                    [
                        "Round 1: no <code>()</code> or <code>[]</code> is adjacent, but <code>{}</code> is, so <code>([{}])[</code> becomes <code>([])[</code>.",
                        "Round 2: no <code>()</code> yet; removing <code>[]</code> gives <code>()[</code>.",
                        "Round 3: removing <code>()</code> leaves <code>[</code>.",
                        "Round 4: nothing matches, so <code>s</code> equals <code>prev</code> and the loop stops.",
                        "<code>[</code> is not empty: the last opener is never closed, so it returns <strong>False</strong>.",
                    ],
                    [
                        "Round 1: removing <code>()</code> turns <code>{[]}()</code> into <code>{[]}</code>.",
                        "Still in round 1: removing <code>[]</code> gives <code>{}</code>, and removing <code>{}</code> gives the empty string.",
                        "Round 2: <code>prev</code> is <code>\"\"</code> and nothing changes, so the loop stops.",
                        "The string is empty: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Does the order of the three <code>replace</code> calls matter?",
                     "Not for correctness: any pair missed in one round is caught in a later one. The order only changes how many rounds it takes, as example 2 shows (all three layers vanish in one round)."],
                    ["Why not simply count openers and closers?",
                     "Counts cannot see order or type. <code>([)]</code> has balanced counts of every kind but is invalid; this approach gets stuck on it with nothing to delete."],
                    ["When would I use this?",
                     "Only as a quick first idea. Each round copies the string and there can be many rounds, so the stack is the expected answer."],
                ],
            },
            "Stack of open brackets": {
                "idea": [
                    "The bracket that must close next is always the <em>most recently opened</em> one still open, which is the top of a stack.",
                    "Push openers. When a closer arrives, the top must be its matching opener, and it is popped.",
                    "A closer with an empty stack or the wrong opener on top is an immediate failure; openers left at the end were never closed.",
                ],
                "steps": [
                    "Map each closer to its opener: <code>pairs = {\")\": \"(\", \"]\": \"[\", \"}\": \"{\"}</code>.",
                    "Scan the characters <code>ch</code> left to right.",
                    "If <code>ch</code> is an opener (not a key of <code>pairs</code>), push it.",
                    "If <code>ch</code> is a closer: return <code>False</code> when the stack is empty or <code>stack.pop() != pairs[ch]</code>.",
                    "After the scan, return <code>not stack</code>: valid only if every opener was closed.",
                ],
                "why": [
                    "Brackets must nest, so the opener a closer pairs with is the last unclosed one. The stack holds the unclosed openers in order, so its top is exactly that one.",
                    "Every failure mode is caught: wrong type (pop mismatch), closer with nothing open (empty stack), opener never closed (non-empty at the end).",
                    "Each character is pushed and popped at most once: <strong>O(n)</strong> time. The stack can hold all n characters, e.g. <code>((((</code>: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "<code>(</code>, <code>[</code>, <code>{</code>: pushed, stack = ['(', '[', '{'].",
                        "<code>}</code>: pops '{', which matches. stack = ['(', '['].",
                        "<code>]</code>: pops '[', matches. <code>)</code>: pops '(', matches. stack = [].",
                        "<code>[</code>: pushed, stack = ['['].",
                        "The scan ends with '[' still open, so it returns <strong>False</strong>.",
                    ],
                    [
                        "<code>{</code>, <code>[</code>: pushed, stack = ['{', '['].",
                        "<code>]</code>: pops '[', matches. <code>}</code>: pops '{', matches. stack = [].",
                        "<code>(</code>: pushed. <code>)</code>: pops '(', matches. stack = [].",
                        "The stack is empty at the end: <strong>True</strong>.",
                    ],
                ],
                "faq": [
                    ["Why check <code>not stack</code> before popping?",
                     "A closer can arrive when nothing is open, as in <code>]</code>. Popping an empty list raises an IndexError, so the empty check doubles as the “nothing to close” failure."],
                    ["Why is <code>return not stack</code> needed at the end?",
                     "A string like <code>((</code> never hits a bad closer, so the loop finishes without returning. The leftover openers make it invalid."],
                    ["Is popping inside the comparison safe when it fails?",
                     "Yes. The function returns <code>False</code> straight away, so losing that opener from the stack does not matter."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ stack using queues
    "stack-using-queues": {
        "examples": [
            {"setup": "s = MyStack()\nfor x in (1, 2, 3):\n    s.push(x)",
             "call": "[s.top(), s.pop(), s.pop(), s.empty()]", "expect": "[3, 3, 2, False]"},
            {"setup": "s = MyStack()\ns.push(1)",
             "call": "[s.pop(), s.empty(), s.push(2), s.top()]", "expect": "[1, True, None, 2]"},
        ],
        "approaches": {
            "Two queues, pay on pop": {
                "idea": [
                    "A queue only gives access to its <em>oldest</em> item, but a stack needs the <em>newest</em>. The newest is at the back of the queue.",
                    "To reach it, move every item except the last into a second queue, take the last one out, and let the second queue become the main one.",
                    "Pushes stay cheap (one <code>append</code>); the cost is paid on <code>pop</code>.",
                ],
                "steps": [
                    "<code>push(x)</code>: append <code>x</code> to the back of <code>self.q</code>.",
                    "<code>pop()</code>: while <code>self.q</code> has more than one item, move <code>popleft()</code> into <code>self.helper</code>.",
                    "The single item left is the newest: <code>popleft()</code> it as <code>top</code>.",
                    "Swap the names: <code>self.q, self.helper = self.helper, self.q</code>, so the survivors are the main queue again, still in order.",
                    "<code>top()</code> pops the newest and pushes it straight back; <code>empty()</code> checks <code>self.q</code>.",
                ],
                "why": [
                    "Moving items from one queue to another with <code>popleft</code>/<code>append</code> keeps their order, so after the swap the remaining items are oldest-to-newest as before.",
                    "Pushing the popped value back in <code>top()</code> puts it at the back again, which is where the newest belongs.",
                    "<code>push</code> is <strong>O(1)</strong>; <code>pop</code> and <code>top</code> move n − 1 items, so they are <strong>O(n)</strong>. The two queues together hold n items: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Setup: q = [1, 2, 3] (front on the left).",
                        "<code>top()</code>: moves 1, 2 to helper, takes 3, swaps so q = [1, 2]; then pushes 3 back, q = [1, 2, 3]. Returns 3.",
                        "<code>pop()</code>: same moves, returns 3, q = [1, 2].",
                        "<code>pop()</code>: moves 1 to helper, takes 2, q = [1].",
                        "<code>empty()</code>: q has 1, so False. Result <strong>[3, 3, 2, False]</strong>.",
                    ],
                    [
                        "Setup: q = [1].",
                        "<code>pop()</code>: only one item, so nothing moves; returns 1 and q = [].",
                        "<code>empty()</code>: True. <code>push(2)</code>: q = [2], returns None.",
                        "<code>top()</code>: pops 2 (q = []), pushes it back (q = [2]), returns 2.",
                        "Result <strong>[1, True, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why swap the two queues instead of moving items back?",
                     "Moving them back would cost another n − 1 operations. Swapping the two references is O(1) and leaves the same items in the same order."],
                    ["Why does <code>top()</code> pop and then push?",
                     "It reuses <code>pop</code> to reach the newest item. Pushing it back restores the stack, at the price of making <code>top</code> O(n) too."],
                    ["When is this version better than rotating on push?",
                     "When pushes far outnumber pops. Here pushes are O(1); the rotate version makes every push O(n)."],
                ],
            },
            "One queue, rotate on push": {
                "idea": [
                    "Keep the queue in <em>stack order</em>: newest at the front, so <code>popleft</code> is a stack pop.",
                    "After appending a new item at the back, rotate the queue by moving the older items behind it, one at a time.",
                    "This puts all the cost on <code>push</code> and needs only one queue.",
                ],
                "steps": [
                    "<code>push(x)</code>: append <code>x</code> to the back of <code>self.q</code>.",
                    "Then repeat <code>len(self.q) - 1</code> times: <code>self.q.append(self.q.popleft())</code>, moving each older item behind <code>x</code>.",
                    "Now <code>x</code> is at the front, followed by the older items newest-first.",
                    "<code>pop()</code> is <code>self.q.popleft()</code> and <code>top()</code> is <code>self.q[0]</code>.",
                    "<code>empty()</code> returns <code>not self.q</code>.",
                ],
                "why": [
                    "Before the push the queue is newest-first. Rotating the k old items behind <code>x</code> keeps their relative order, so afterwards the queue is <code>x</code> followed by them: still newest-first.",
                    "With that invariant, the front is always the stack's top, so <code>pop</code> and <code>top</code> are correct.",
                    "<code>push</code> rotates n − 1 items: <strong>O(n)</strong>. <code>pop</code>, <code>top</code> and <code>empty</code> are <strong>O(1)</strong>. One queue of n items: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "push(1): q = [1], no rotation.",
                        "push(2): append gives [1, 2], one rotation moves 1 behind: q = [2, 1].",
                        "push(3): [2, 1, 3], two rotations: q = [3, 2, 1].",
                        "<code>top()</code> reads 3. <code>pop()</code> gives 3, then <code>pop()</code> gives 2, q = [1].",
                        "<code>empty()</code> is False. Result <strong>[3, 3, 2, False]</strong>.",
                    ],
                    [
                        "push(1): q = [1].",
                        "<code>pop()</code>: popleft gives 1, q = []. <code>empty()</code>: True.",
                        "<code>push(2)</code>: q = [2]; the loop runs 0 times. Returns None.",
                        "<code>top()</code>: q[0] = 2.",
                        "Result <strong>[1, True, None, 2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why rotate <code>len(self.q) - 1</code> times and not <code>len(self.q)</code>?",
                     "Rotating every item, including the new one, would put the queue back exactly as it was, with <code>x</code> at the back again."],
                    ["Isn't this slower than the two-queue version?",
                     "Only on push. It wins when pops and tops are frequent, and it uses one queue instead of two."],
                    ["Does it matter that <code>deque</code> could pop from the right?",
                     "The exercise is to use only queue operations: append at the back, remove from the front. Using <code>pop()</code> on the deque would make it a stack directly and defeat the point."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ queue using stacks
    "queue-using-stacks": {
        "examples": [
            {"setup": "q = MyQueue()\nfor x in (1, 2, 3):\n    q.push(x)",
             "call": "[q.pop(), q.push(4), q.pop(), q.pop(), q.pop(), q.empty()]", "expect": "[1, None, 2, 3, 4, True]"},
            {"setup": "q = MyQueue()\nq.push(1)\nq.push(2)",
             "call": "[q.peek(), q.pop(), q.push(3), q.peek(), q.empty()]", "expect": "[1, 1, None, 2, False]"},
        ],
        "approaches": {
            "Move everything on every push": {
                "idea": [
                    "Keep the single stack <code>self.s</code> in <em>queue order</em>: oldest item on top, so <code>pop()</code> removes the oldest.",
                    "A new item belongs at the bottom. To get it there, pour everything into <code>self.helper</code>, push the new item, and pour everything back.",
                    "Pouring a stack into another reverses it, and pouring back reverses it again, so the old items end up in their original order above the new one.",
                ],
                "steps": [
                    "<code>push(x)</code>: while <code>self.s</code> is not empty, move its top to <code>self.helper</code>.",
                    "Append <code>x</code> to the now empty <code>self.s</code>: it sits at the bottom.",
                    "While <code>self.helper</code> is not empty, move its top back to <code>self.s</code>.",
                    "<code>pop()</code> is <code>self.s.pop()</code> and <code>peek()</code> is <code>self.s[-1]</code>: the top is the oldest item.",
                    "<code>empty()</code> returns <code>not self.s</code>.",
                ],
                "why": [
                    "Invariant: <code>self.s</code> lists items newest-at-bottom, oldest-on-top. Each push keeps it, because the double pour restores the old order and only adds <code>x</code> underneath.",
                    "With the oldest always on top, <code>pop</code> and <code>peek</code> behave exactly as a queue's front.",
                    "Every push moves all n items twice: <strong>O(n)</strong>. <code>pop</code>, <code>peek</code> and <code>empty</code> are <strong>O(1)</strong>. The two lists together hold n items: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "push(1): s = [1]. push(2): pour 1 out, push 2, pour back: s = [2, 1] (top on the right).",
                        "push(3): s = [3, 2, 1]. The oldest, 1, is on top.",
                        "<code>pop()</code> returns 1, s = [3, 2]. <code>push(4)</code>: s = [4, 3, 2], returns None.",
                        "<code>pop()</code> → 2, <code>pop()</code> → 3, <code>pop()</code> → 4. s = [].",
                        "<code>empty()</code> is True. Result <strong>[1, None, 2, 3, 4, True]</strong>.",
                    ],
                    [
                        "Setup: push(1), push(2) leave s = [2, 1].",
                        "<code>peek()</code>: s[-1] = 1. <code>pop()</code>: returns 1, s = [2].",
                        "<code>push(3)</code>: pour 2 into helper, push 3, pour back: s = [3, 2].",
                        "<code>peek()</code>: 2. <code>empty()</code>: False.",
                        "Result <strong>[1, 1, None, 2, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not just reverse the list on each pop?",
                     "That is the same O(n) cost, only moved to pop. The exercise asks for stack operations only, and the lazy two-stack version avoids the repeated work entirely."],
                    ["Why does the helper end up empty after every push?",
                     "The second loop pours it back completely. It is only scratch space during a push."],
                    ["When is this version acceptable?",
                     "When pushes are rare and pops or peeks are very frequent, since those are plain O(1) list operations."],
                ],
            },
            "Input and output stacks, transfer lazily": {
                "idea": [
                    "New items go onto <code>self.inbox</code>; items are taken from <code>self.outbox</code>.",
                    "Pouring the inbox into an empty outbox reverses it, so the oldest item lands on top of the outbox, ready to pop.",
                    "Only pour when the outbox is empty. Items already in the outbox are older than everything in the inbox, so they must leave first.",
                ],
                "steps": [
                    "<code>push(x)</code>: append <code>x</code> to <code>self.inbox</code>.",
                    "<code>_shift()</code>: if <code>self.outbox</code> is empty, pop everything from <code>self.inbox</code> onto <code>self.outbox</code>.",
                    "<code>pop()</code>: call <code>_shift()</code>, then <code>self.outbox.pop()</code>.",
                    "<code>peek()</code>: call <code>_shift()</code>, then read <code>self.outbox[-1]</code>.",
                    "<code>empty()</code>: true only when both stacks are empty.",
                ],
                "why": [
                    "Every item in the outbox arrived before every item in the inbox, and the outbox is stored oldest-on-top, so its top is always the queue's front.",
                    "Transferring only when the outbox is empty preserves that: a transfer while items remain would bury older items under newer ones.",
                    "Each item is pushed to the inbox once, moved once, and popped once, so any sequence of m operations costs O(m): <strong>amortised O(1)</strong> per operation, though one pop can take O(n).",
                    "The two stacks hold each item exactly once: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pushes: inbox = [1, 2, 3], outbox = [].",
                        "<code>pop()</code>: outbox is empty, so shift: outbox = [3, 2, 1]. Pop gives 1, outbox = [3, 2].",
                        "<code>push(4)</code>: inbox = [4]. It waits behind 2 and 3.",
                        "<code>pop()</code> → 2, <code>pop()</code> → 3: no shift needed while the outbox has items.",
                        "<code>pop()</code>: outbox empty, shift moves 4 across, pop gives 4. Both stacks empty.",
                        "<code>empty()</code> is True. Result <strong>[1, None, 2, 3, 4, True]</strong>.",
                    ],
                    [
                        "Setup: inbox = [1, 2], outbox = [].",
                        "<code>peek()</code>: shift, outbox = [2, 1], read 1.",
                        "<code>pop()</code>: outbox not empty, no shift; returns 1, outbox = [2].",
                        "<code>push(3)</code>: inbox = [3]. <code>peek()</code>: outbox top is 2.",
                        "<code>empty()</code>: False. Result <strong>[1, 1, None, 2, False]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not transfer on every pop?",
                     "If the outbox still has items, pouring the inbox on top would put newer items above older ones and break the order. It would also redo work."],
                    ["Why is a single pop O(n) but the average O(1)?",
                     "A pop that triggers a transfer moves everything in the inbox. Each item is moved at most once in its lifetime, though, so the total moving work over all operations is at most the number of pushes."],
                    ["Why does <code>peek()</code> also call <code>_shift()</code>?",
                     "The front might be sitting at the bottom of the inbox. Shifting first guarantees it is on top of the outbox, as in example 2's first <code>peek()</code>."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ min stack
    "min-stack": {
        "examples": [
            {"setup": "m = MinStack()\nfor v in (5, 3, 7, 3, 1):\n    m.push(v)",
             "call": "[m.getMin(), m.pop(), m.getMin(), m.pop(), m.getMin(), m.top()]",
             "expect": "[1, None, 3, None, 3, 7]"},
            {"setup": "m = MinStack()\nfor v in (-2, 0, -3):\n    m.push(v)",
             "call": "[m.getMin(), m.pop(), m.top(), m.getMin()]",
             "expect": "[-3, None, 0, -2]"},
        ],
        "approaches": {
            "Scan for the minimum": {
                "idea": [
                    "Store the values in a plain list used as a stack; push, pop and top are already O(1).",
                    "Compute the minimum only when asked, by scanning the whole list with <code>min</code>.",
                    "It is the baseline that the O(1) designs improve on: correct, but <code>getMin</code> does not meet the required cost.",
                ],
                "steps": [
                    "<code>push(val)</code>: <code>self.s.append(val)</code>.",
                    "<code>pop()</code>: <code>self.s.pop()</code>, discarding the value.",
                    "<code>top()</code>: return <code>self.s[-1]</code>.",
                    "<code>getMin()</code>: return <code>min(self.s)</code>, which looks at every stored value.",
                    "No extra state is kept, so nothing needs updating when the minimum is popped.",
                ],
                "why": [
                    "<code>min(self.s)</code> is the minimum of exactly the values currently on the stack, so it is always right, even after the minimum is popped.",
                    "<code>push</code>, <code>pop</code> and <code>top</code> are <strong>O(1)</strong>; <code>getMin</code> is <strong>O(n)</strong> because it reads the whole list.",
                    "Only the values themselves are stored: <strong>O(n)</strong> space and no extra overhead.",
                ],
                "dry": [
                    [
                        "After the pushes, s = [5, 3, 7, 3, 1].",
                        "<code>getMin()</code> scans all five values: 1.",
                        "<code>pop()</code> removes 1. <code>getMin()</code> scans [5, 3, 7, 3]: 3.",
                        "<code>pop()</code> removes the second 3. <code>getMin()</code> scans [5, 3, 7]: still 3, from the first 3.",
                        "<code>top()</code> is 7. Result <strong>[1, None, 3, None, 3, 7]</strong>.",
                    ],
                    [
                        "After the pushes, s = [−2, 0, −3].",
                        "<code>getMin()</code>: −3.",
                        "<code>pop()</code> removes −3, s = [−2, 0]. <code>top()</code>: 0.",
                        "<code>getMin()</code> rescans and finds −2.",
                        "Result <strong>[−3, None, 0, −2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why not cache the minimum in a variable?",
                     "Popping the current minimum would leave the cache stale, and recovering the previous minimum needs a rescan. The other approaches store exactly that history."],
                    ["Is <code>min(self.s)</code> on an empty stack a problem?",
                     "It raises a ValueError, but the problem guarantees <code>getMin</code> is only called on a non-empty stack."],
                    ["When is this good enough?",
                     "When <code>getMin</code> is rare compared with pushes and pops. The problem asks for O(1) on every call, though, so it is only a starting point."],
                ],
            },
            "Store (value, min so far) pairs": {
                "idea": [
                    "The minimum of a stack only depends on what is <em>below</em> the top, and that part never changes while the top item is there.",
                    "So when pushing, record the minimum of the stack at that moment alongside the value.",
                    "After any pop, the new top still carries the correct minimum for what remains.",
                ],
                "steps": [
                    "<code>push(val)</code>: if the stack is empty, push <code>(val, val)</code>.",
                    "Otherwise push <code>(val, min(val, self.s[-1][1]))</code>: the smaller of the new value and the minimum below it.",
                    "<code>pop()</code>: pop the pair; the minimum leaves with it.",
                    "<code>top()</code>: return <code>self.s[-1][0]</code>.",
                    "<code>getMin()</code>: return <code>self.s[-1][1]</code>.",
                ],
                "why": [
                    "Each pair's second field is the minimum of itself and every pair below it. Pushes and pops only touch the top, so the fields below stay valid.",
                    "So the top's second field is always the minimum of the whole stack, including after the old minimum is popped.",
                    "Every operation touches only the top pair: <strong>O(1)</strong> time. Each value is stored with one extra number: <strong>O(n)</strong> space, about twice the plain stack.",
                ],
                "dry": [
                    [
                        "Pushes give s = [(5,5), (3,3), (7,3), (3,3), (1,1)].",
                        "<code>getMin()</code>: top pair (1,1), so 1.",
                        "<code>pop()</code> removes (1,1). <code>getMin()</code>: top (3,3), so 3.",
                        "<code>pop()</code> removes (3,3). <code>getMin()</code>: top (7,3), so still 3.",
                        "<code>top()</code>: 7. Result <strong>[1, None, 3, None, 3, 7]</strong>.",
                    ],
                    [
                        "Pushes give s = [(−2,−2), (0,−2), (−3,−3)].",
                        "<code>getMin()</code>: −3.",
                        "<code>pop()</code> removes (−3,−3). <code>top()</code>: 0.",
                        "<code>getMin()</code>: the pair (0,−2) remembers −2.",
                        "Result <strong>[−3, None, 0, −2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store the minimum with every value, even when it did not change?",
                     "So that any pop can be undone instantly. Pairs like (7,3) repeat the minimum, which costs memory but keeps the logic trivial."],
                    ["Do duplicates of the minimum cause trouble?",
                     "No. Each copy has its own pair, so popping one 3 leaves the other with its own recorded minimum, as in example 1."],
                    ["Is this the answer to give in an interview?",
                     "Yes, it is the clearest O(1) design. Mention the two-stack variant if asked to save space when the minimum rarely changes."],
                ],
            },
            "Second stack of minimums, pushed only when needed": {
                "idea": [
                    "The minimum only changes when a value at least as small as it is pushed, and changes back only when that value is popped.",
                    "Keep a second stack <code>self.mins</code> holding just those minimum changes; its top is the current minimum.",
                    "Push onto <code>mins</code> with <code>&lt;=</code> so duplicate minimums are recorded once per copy.",
                ],
                "steps": [
                    "<code>push(val)</code>: append to <code>self.s</code>.",
                    "If <code>mins</code> is empty or <code>val &lt;= self.mins[-1]</code>, also append <code>val</code> to <code>mins</code>.",
                    "<code>pop()</code>: pop from <code>self.s</code>; if that value equals <code>self.mins[-1]</code>, pop <code>mins</code> as well.",
                    "<code>top()</code>: <code>self.s[-1]</code>.",
                    "<code>getMin()</code>: <code>self.mins[-1]</code>.",
                ],
                "why": [
                    "<code>mins</code> is non-increasing from bottom to top, and its top always equals the minimum of <code>s</code>: a value goes on it exactly when it becomes (or ties) the minimum.",
                    "A popped value equal to <code>mins[-1]</code> is one of the copies that was pushed there, thanks to <code>&lt;=</code>, so popping <code>mins</code> keeps both stacks in sync.",
                    "All operations are <strong>O(1)</strong>. In the worst case (a falling sequence) <code>mins</code> holds every value, so space is <strong>O(n)</strong>, but usually far less.",
                ],
                "dry": [
                    [
                        "push 5: mins = [5]. push 3: 3 ≤ 5, mins = [5, 3]. push 7: skipped.",
                        "push 3: 3 ≤ 3, mins = [5, 3, 3]. push 1: mins = [5, 3, 3, 1].",
                        "<code>getMin()</code>: 1. <code>pop()</code> removes 1, equal to mins top, so mins = [5, 3, 3].",
                        "<code>getMin()</code>: 3. <code>pop()</code> removes 3, mins = [5, 3]. <code>getMin()</code>: still 3.",
                        "<code>top()</code>: s = [5, 3, 7], so 7. Result <strong>[1, None, 3, None, 3, 7]</strong>.",
                    ],
                    [
                        "push −2: mins = [−2]. push 0: 0 &gt; −2, skipped. push −3: mins = [−2, −3].",
                        "<code>getMin()</code>: −3.",
                        "<code>pop()</code> removes −3, which equals the mins top, so mins = [−2].",
                        "<code>top()</code>: 0. <code>getMin()</code>: −2.",
                        "Result <strong>[−3, None, 0, −2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&lt;=</code> and not <code>&lt;</code> when pushing to <code>mins</code>?",
                     "With <code>&lt;</code>, example 1's second 3 would not be recorded. Popping it would then pop the only 3 from <code>mins</code>, and <code>getMin</code> would wrongly return 5 while a 3 is still on the stack."],
                    ["Why compare by value on pop rather than tracking indices?",
                     "Because <code>mins</code> holds a copy for every value that tied or beat the minimum, the value alone tells you whether the popped item was one of them."],
                    ["How is this better than storing pairs?",
                     "It only stores the values that changed the minimum. On data where the minimum rarely changes, <code>mins</code> stays tiny."],
                ],
            },
            "One stack of differences from the minimum": {
                "idea": [
                    "Store each value as its difference from the minimum at the time it was pushed, and keep one variable <code>self.min</code>.",
                    "A negative difference means the pushed value became the new minimum. It also encodes how far the minimum dropped, so the old minimum can be recovered on pop.",
                    "This keeps just one number per item plus one variable, with O(1) operations.",
                ],
                "steps": [
                    "<code>push(val)</code> on an empty stack: push 0 and set <code>self.min = val</code>.",
                    "Otherwise push <code>val - self.min</code>; if <code>val &lt; self.min</code>, set <code>self.min = val</code>.",
                    "<code>pop()</code>: pop <code>diff</code>. If <code>diff &lt; 0</code>, the popped value was the minimum, and the old one is <code>self.min - diff</code>.",
                    "If the stack becomes empty, reset <code>self.min = None</code>.",
                    "<code>top()</code>: with <code>diff = self.s[-1]</code>, return <code>self.min</code> if <code>diff &lt; 0</code>, else <code>self.min + diff</code>.",
                    "<code>getMin()</code>: return <code>self.min</code>.",
                ],
                "why": [
                    "For a non-negative <code>diff</code>, the minimum did not change on that push, so <code>value = self.min + diff</code>.",
                    "For a negative <code>diff = val − old_min</code>, the value itself is the current <code>self.min</code>, and <code>old_min = self.min − diff</code> restores the previous minimum exactly.",
                    "Every operation is a few arithmetic steps on the top: <strong>O(1)</strong>. Storage is one number per item plus <code>self.min</code>: <strong>O(n)</strong> total, <strong>O(1)</strong> beyond the values.",
                ],
                "dry": [
                    [
                        "push 5: s = [0], min = 5. push 3: diff −2, min = 3. push 7: diff 4.",
                        "push 3: diff 0 (not a new minimum). push 1: diff −2, min = 1. s = [0, −2, 4, 0, −2].",
                        "<code>getMin()</code>: 1. <code>pop()</code>: diff −2 &lt; 0, so min = 1 − (−2) = 3.",
                        "<code>getMin()</code>: 3. <code>pop()</code>: diff 0, min stays 3. <code>getMin()</code>: 3.",
                        "<code>top()</code>: diff 4 ≥ 0, so 3 + 4 = 7. Result <strong>[1, None, 3, None, 3, 7]</strong>.",
                    ],
                    [
                        "push −2: s = [0], min = −2. push 0: diff 2. push −3: diff −1, min = −3. s = [0, 2, −1].",
                        "<code>getMin()</code>: −3.",
                        "<code>pop()</code>: diff −1, so min = −3 − (−1) = −2.",
                        "<code>top()</code>: diff 2, so −2 + 2 = 0. <code>getMin()</code>: −2.",
                        "Result <strong>[−3, None, 0, −2]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does a tie with the minimum not count as a new minimum?",
                     "Its diff is 0, so popping it leaves <code>self.min</code> alone, which is right: the other copy is still there."],
                    ["Can the differences overflow?",
                     "In Python no, integers are unbounded. In languages with 32-bit ints, <code>val - self.min</code> can overflow and you would need 64-bit storage."],
                    ["Why reset <code>self.min</code> to <code>None</code> when the stack empties?",
                     "Not strictly needed, since the next push on an empty stack sets it anyway. It keeps the object from reporting a stale minimum."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ evaluate reverse polish notation
    "evaluate-rpn": {
        "examples": [
            {"call": 'eval_rpn(["5", "1", "2", "+", "4", "*", "+", "3", "-"])', "expect": "14"},
            {"call": 'eval_rpn(["4", "-7", "2", "/", "-"])', "expect": "7"},
        ],
        "approaches": {
            "Operand stack": {
                "idea": [
                    "In reverse Polish notation an operator always applies to the two most recent values that have not been used yet.",
                    "Those are the top two items of a stack of operands. Pop them, compute, and push the result as a new operand.",
                    "A valid expression leaves exactly one value on the stack: the answer.",
                ],
                "steps": [
                    "Build <code>ops</code>, mapping each operator to a two-argument function; division is <code>int(a / b)</code>.",
                    "Scan each token <code>tok</code>.",
                    "If <code>tok</code> is an operator, pop <code>b</code> first (right operand), then <code>a</code> (left operand).",
                    "Push <code>ops[tok](a, b)</code>.",
                    "Otherwise push <code>int(tok)</code>.",
                    "Return <code>stack[0]</code>.",
                ],
                "why": [
                    "Each operator's operands are the results of the two complete sub-expressions just before it, and those are exactly the top two stack entries.",
                    "Popping <code>b</code> before <code>a</code> keeps the order right for <code>-</code> and <code>/</code>, which are not symmetric.",
                    "Each token is pushed once and popped at most once: <strong>O(n)</strong> time. The stack can hold about n/2 operands: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "5, 1, 2: stack = [5, 1, 2].",
                        "<code>+</code>: b = 2, a = 1, push 3. stack = [5, 3]. Then 4: [5, 3, 4].",
                        "<code>*</code>: 3 × 4 = 12, stack = [5, 12].",
                        "<code>+</code>: 5 + 12 = 17, stack = [17]. Then 3: [17, 3].",
                        "<code>-</code>: a = 17, b = 3, 17 − 3 = 14. Returns <strong>14</strong>.",
                    ],
                    [
                        "4, −7, 2: stack = [4, −7, 2]. <code>int(\"-7\")</code> is a number, not the minus operator.",
                        "<code>/</code>: a = −7, b = 2, −7 / 2 = −3.5, truncated to −3. stack = [4, −3].",
                        "<code>-</code>: a = 4, b = −3, 4 − (−3) = 7.",
                        "Returns <strong>7</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>int(a / b)</code> and not <code>a // b</code>?",
                     "The problem truncates toward zero. <code>//</code> floors, so <code>-7 // 2</code> is −4, while <code>int(-7 / 2)</code> is −3."],
                    ["Why pop <code>b</code> before <code>a</code>?",
                     "The right operand was pushed last, so it is on top. Swapping them would compute <code>2 - 4</code> instead of <code>4 - 2</code>."],
                    ["How is <code>\"-7\"</code> told apart from <code>\"-\"</code>?",
                     "<code>tok in ops</code> checks the whole token against the dictionary keys, so only the exact one-character strings are operators."],
                ],
            },
            "Recursion from the end": {
                "idea": [
                    "Read backwards, the last token is the outermost operator, and it is followed (to its left) by its right operand, then its left operand.",
                    "That is a prefix expression read right to left, so a recursive function can parse it: take a token; if it is an operator, evaluate two sub-expressions.",
                    "The call stack does the job of the explicit operand stack.",
                ],
                "steps": [
                    "Copy <code>tokens</code> into a list so tokens can be popped from the end.",
                    "<code>ev()</code> pops the last token <code>tok</code>.",
                    "If <code>tok not in \"+-*/\"</code>, it is a number: return <code>int(tok)</code>.",
                    "Otherwise evaluate <code>b = ev()</code> first (the right operand is nearer the end), then <code>a = ev()</code>.",
                    "Apply the operator to <code>a</code> and <code>b</code>, truncating division with <code>int(a / b)</code>.",
                    "The answer is <code>ev()</code> called once.",
                ],
                "why": [
                    "Each <code>ev()</code> call consumes exactly one complete sub-expression from the end, so the two recursive calls return the right and then the left operand.",
                    "Every token is popped once: <strong>O(n)</strong> time.",
                    "The recursion depth equals the nesting depth of the expression, which can be about n/2 for an expression like <code>1 2 3 4 + + +</code>: <strong>O(n)</strong> space, plus the copied list.",
                ],
                "dry": [
                    [
                        "<code>ev()</code> pops <code>-</code>, so it evaluates b then a.",
                        "b: pops 3. a: pops <code>+</code>, which needs its own b and a.",
                        "That b pops <code>*</code>: its b pops 4, its a pops <code>+</code>, which pops 2 then 1 and returns 1 + 2 = 3. So <code>*</code> gives 3 × 4 = 12.",
                        "That a pops 5, so the inner <code>+</code> is 5 + 12 = 17.",
                        "The outer <code>-</code> is 17 − 3 = <strong>14</strong>.",
                    ],
                    [
                        "<code>ev()</code> pops <code>-</code>.",
                        "b: pops <code>/</code>, whose b pops 2 and a pops −7: <code>int(-7 / 2)</code> = −3.",
                        "a: pops 4.",
                        "4 − (−3) = <strong>7</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>tok not in \"+-*/\"</code> safe for <code>\"-7\"</code>?",
                     "Yes. On strings, <code>in</code> is a substring test, and <code>\"-7\"</code> is not a substring of <code>\"+-*/\"</code>. It works because no number token is ever a substring of that string, but a set or dict lookup is clearer."],
                    ["Why evaluate the right operand first?",
                     "Tokens are consumed from the end, and the right operand's tokens sit just before the operator, so they are reached first."],
                    ["Could deep expressions hit the recursion limit?",
                     "Yes. Python's default limit is about 1000 frames, so a very long chain of nested operators would fail. The explicit stack has no such limit."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ asteroid collision
    "asteroid-collision": {
        "examples": [
            {"call": "asteroid_collision([5, 10, -5, -15, 3, -3, 8])", "expect": "[-15, 8]"},
            {"call": "asteroid_collision([-1, 3, 2, -3])", "expect": "[-1]"},
        ],
        "approaches": {
            "Resolve one collision at a time": {
                "idea": [
                    "Two asteroids collide only when a right-mover sits directly before a left-mover: <code>a[i] &gt; 0 &gt; a[i + 1]</code>.",
                    "Simulate literally: find the first such pair, remove the smaller (or both on a tie), and start looking again from the beginning.",
                    "When a full scan finds no colliding pair, the row is stable.",
                ],
                "steps": [
                    "Copy the input into <code>a</code> and set <code>changed = True</code>.",
                    "While <code>changed</code>: reset it to <code>False</code> and scan <code>i</code> from 0 to <code>len(a) - 2</code>.",
                    "At the first <code>i</code> with <code>a[i] &gt; 0 &gt; a[i + 1]</code>, compare sizes with <code>abs</code>.",
                    "Delete <code>a[i + 1]</code> if the right-mover is larger, <code>a[i]</code> if it is smaller, or both with <code>del a[i:i + 2]</code> on a tie.",
                    "Set <code>changed = True</code> and <code>break</code>, because the list just changed under the loop.",
                    "Return <code>a</code> once a scan makes no change.",
                ],
                "why": [
                    "Collisions between different pairs do not affect each other's outcome, so resolving them one by one in any order reaches the same final row.",
                    "Pairs where the left one moves left or the right one moves right never meet, so only <code>+ −</code> neighbours need checking.",
                    "Each collision removes at least one asteroid, so there are at most n rounds, and each round scans O(n): <strong>O(n²)</strong> time. The copy is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Round 1: first + − pair is (10, −5) at i=1. 10 &gt; 5, delete −5: [5, 10, −15, 3, −3, 8].",
                        "Round 2: (10, −15) at i=1. 10 &lt; 15, delete 10: [5, −15, 3, −3, 8].",
                        "Round 3: (5, −15) at i=0. Delete 5: [−15, 3, −3, 8].",
                        "Round 4: (3, −3) at i=1, a tie, delete both: [−15, 8].",
                        "Round 5: no + − pair. Returns <strong>[−15, 8]</strong>.",
                    ],
                    [
                        "Round 1: (−1, 3) is − +, no collision. (3, 2) is + +. (2, −3) at i=2: 2 &lt; 3, delete 2: [−1, 3, −3].",
                        "Round 2: (3, −3) at i=1, a tie, delete both: [−1].",
                        "Round 3: nothing to compare.",
                        "The −1 was already moving away to the left. Returns <strong>[−1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why restart the scan from the beginning after each collision?",
                     "Deleting shifts every later index, so continuing the <code>for</code> loop would skip or misread elements. Restarting is simple and correct, just slow."],
                    ["Why do <code>[-2, 1]</code> never collide?",
                     "The −2 moves left and the 1 moves right, so they drift apart. Only a positive followed by a negative moves towards each other."],
                    ["Where does the O(n²) worst case come from?",
                     "From rows like <code>[1, 1, 1, 1, -5]</code>: each round removes only the right-mover just before the −5, but first rescans everything before it, so the rounds cost n + (n − 1) + … steps."],
                ],
            },
            "Stack of survivors": {
                "idea": [
                    "Process asteroids left to right, keeping the ones that are still alive on a stack.",
                    "A new left-mover can only hit right-movers on top of the stack. It keeps destroying smaller ones until it dies, ties, or the top is not a right-mover.",
                    "Right-movers and left-movers with nothing to hit are simply pushed.",
                ],
                "steps": [
                    "For each asteroid <code>a</code>, set <code>alive = True</code>.",
                    "While <code>alive and a &lt; 0 and stack and stack[-1] &gt; 0</code>: there is a collision with the top.",
                    "If <code>stack[-1] &lt; -a</code>, pop the top; the new asteroid survives and keeps going.",
                    "If <code>stack[-1] == -a</code>, pop the top and set <code>alive = False</code>: both explode.",
                    "Otherwise the top is bigger: set <code>alive = False</code>.",
                    "If <code>a</code> is still alive, push it. Return the stack.",
                ],
                "why": [
                    "The stack is always a stable row: no right-mover in it is followed by a left-mover, so the only possible new collision is between <code>a</code> and the top.",
                    "A left-mover that empties the stack, or reaches a left-mover on top, can never collide again, so pushing it is safe.",
                    "Each asteroid is pushed at most once and popped at most once, so the total work is <strong>O(n)</strong> even with the inner <code>while</code>. The stack is <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "5, 10: right-movers, pushed. stack = [5, 10].",
                        "−5: top 10 &gt; 5, so −5 explodes. stack = [5, 10].",
                        "−15: pops 10 (10 &lt; 15), pops 5, stack empty, push −15. stack = [−15].",
                        "3: pushed. −3: tie with 3, both gone. stack = [−15].",
                        "8: pushed. Returns <strong>[−15, 8]</strong>.",
                    ],
                    [
                        "−1: stack empty, so it is pushed. stack = [−1].",
                        "3, 2: pushed. stack = [−1, 3, 2].",
                        "−3: pops 2 (2 &lt; 3), then ties with 3: pop and <code>alive = False</code>.",
                        "The −1 on the stack is not a right-mover, so it was never in danger.",
                        "Returns <strong>[−1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does the loop require <code>stack[-1] &gt; 0</code>?",
                     "A left-mover on top is moving the same way as <code>a</code>, so they never meet. Without this check, example 2's −1 would wrongly be compared with later left-movers."],
                    ["Why is the nested loop still O(n)?",
                     "Every iteration of the <code>while</code> either pops an asteroid or ends the loop. An asteroid can only be popped once, so all the pops together cost O(n)."],
                    ["Do right-movers ever trigger the loop?",
                     "No. <code>a &lt; 0</code> fails, so they are pushed directly. Only a later left-mover can destroy them."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ daily temperatures
    "daily-temperatures": {
        "examples": [
            {"call": "daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])", "expect": "[1, 1, 4, 2, 1, 1, 0, 0]"},
            {"call": "daily_temperatures([30, 30, 20, 40])", "expect": "[3, 2, 1, 0]"},
        ],
        "approaches": {
            "Scan forward from each day": {
                "idea": [
                    "For each day, look at the following days one by one until a strictly warmer one turns up.",
                    "The distance to that day is the answer; if none turns up, the answer stays 0.",
                    "Simple and correct, but days are rescanned again and again.",
                ],
                "steps": [
                    "Create <code>out = [0] * len(temps)</code>.",
                    "Loop <code>i</code> and its temperature <code>t</code> over every day.",
                    "Loop <code>j</code> from <code>i + 1</code> to the end.",
                    "At the first <code>temps[j] &gt; t</code>, set <code>out[i] = j - i</code> and <code>break</code>.",
                    "If the inner loop never breaks, <code>out[i]</code> stays 0. Return <code>out</code>.",
                ],
                "why": [
                    "The inner loop checks later days in order, so the first warmer one it meets is the nearest.",
                    "A falling sequence makes every inner loop run to the end: n(n − 1)/2 checks, so <strong>O(n²)</strong> time.",
                    "Besides the output only two indices are kept: <strong>O(1)</strong> extra space.",
                ],
                "dry": [
                    [
                        "i=0 (73): 74 is warmer, out[0] = 1. i=1 (74): 75, out[1] = 1.",
                        "i=2 (75): checks 71, 69, 72, then 76 at j=6, out[2] = 4.",
                        "i=3 (71): 69, then 72 at j=5, out[3] = 2. i=4 (69): 72, out[4] = 1. i=5 (72): 76, out[5] = 1.",
                        "i=6 (76): only 73 follows, not warmer. i=7: nothing follows. Both stay 0.",
                        "Returns <strong>[1, 1, 4, 2, 1, 1, 0, 0]</strong>.",
                    ],
                    [
                        "i=0 (30): 30 is not strictly warmer, 20 is not either, 40 is: out[0] = 3.",
                        "i=1 (30): 20, then 40: out[1] = 2.",
                        "i=2 (20): 40: out[2] = 1.",
                        "i=3: nothing after it, stays 0.",
                        "Returns <strong>[3, 2, 1, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>&gt;</code> and not <code>&gt;=</code>?",
                     "The problem asks for a warmer day. With <code>&gt;=</code>, example 2's first 30 would stop at the second 30 and give 1 instead of 3."],
                    ["Why does <code>out</code> start as zeros?",
                     "0 is the required answer for days with no warmer day ahead, so those days need no extra handling."],
                    ["Where is the repeated work?",
                     "Day 2 (75) and day 3 (71) both walk past 69 and 72. The stack approaches answer each day once instead."],
                ],
            },
            "Monotonic decreasing stack of waiting days": {
                "idea": [
                    "Keep a stack of days still <em>waiting</em> for a warmer day. Their temperatures are non-increasing from bottom to top.",
                    "When today is warmer than the top day, today is that day's answer. Pop it, record the distance, and check the next one.",
                    "Each day is answered at the moment its warmer day arrives, so no day is scanned twice.",
                ],
                "steps": [
                    "Create <code>out = [0] * len(temps)</code> and an empty <code>stack</code> of indices.",
                    "Loop <code>i</code>, <code>t</code> over the days.",
                    "While the stack is non-empty and <code>temps[stack[-1]] &lt; t</code>, pop <code>j</code> and set <code>out[j] = i - j</code>.",
                    "Push <code>i</code>: today now waits for its own warmer day.",
                    "Days left on the stack at the end never found one and keep 0. Return <code>out</code>.",
                ],
                "why": [
                    "When day <code>j</code> is popped at day <code>i</code>, every day between them was either popped earlier or still above <code>j</code>, and all of those were ≤ <code>temps[j]</code>. So <code>i</code> is the first warmer day.",
                    "A day that is not popped is never warmer than anything below it, which keeps the stack non-increasing.",
                    "Each index is pushed once and popped at most once: <strong>O(n)</strong> time. A falling sequence keeps every index on the stack: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (73): push, stack = [0]. i=1 (74): pops 0, out[0] = 1, stack = [1]. i=2 (75): pops 1, out[1] = 1, stack = [2].",
                        "i=3 (71), i=4 (69): colder, pushed. stack = [2, 3, 4].",
                        "i=5 (72): pops 4 (out[4] = 1) and 3 (out[3] = 2), stops at 75. stack = [2, 5].",
                        "i=6 (76): pops 5 (out[5] = 1) and 2 (out[2] = 4). stack = [6]. i=7 (73): pushed, stack = [6, 7].",
                        "Days 6 and 7 are never popped. Returns <strong>[1, 1, 4, 2, 1, 1, 0, 0]</strong>.",
                    ],
                    [
                        "i=0 (30): push, stack = [0].",
                        "i=1 (30): 30 &lt; 30 is false, so no pop. stack = [0, 1].",
                        "i=2 (20): pushed, stack = [0, 1, 2].",
                        "i=3 (40): pops 2 (out = 1), 1 (out = 2), 0 (out = 3). stack = [3].",
                        "Returns <strong>[3, 2, 1, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store indices instead of temperatures?",
                     "The answer is a distance <code>i - j</code>, which needs the index. The temperature is always available as <code>temps[j]</code>."],
                    ["Why <code>&lt;</code> in the pop condition?",
                     "Equal temperatures are not warmer. Popping on <code>&lt;=</code> would give example 2's first 30 an answer of 1."],
                    ["How can a nested loop be O(n)?",
                     "Count pops, not loop iterations: each index is popped at most once over the whole run, so the inner <code>while</code> runs at most n times in total."],
                ],
            },
            "Right to left, jump along known answers": {
                "idea": [
                    "Work from the right, so every later day's answer is already in <code>out</code>.",
                    "If day <code>j</code> is not warmer than day <code>i</code>, any day between <code>j</code> and <code>j + out[j]</code> is not warmer than <code>j</code>, so it cannot beat <code>i</code> either. Jump straight to <code>j + out[j]</code>.",
                    "If <code>out[j]</code> is 0, nothing after <code>j</code> is warmer than <code>j</code>, so nothing is warmer than <code>i</code>: stop.",
                ],
                "steps": [
                    "Create <code>out = [0] * n</code>; the last day stays 0.",
                    "Loop <code>i</code> from <code>n - 2</code> down to 0 and start with <code>j = i + 1</code>.",
                    "While <code>temps[j] &lt;= temps[i]</code>: if <code>out[j] == 0</code>, set <code>j = None</code> and break.",
                    "Otherwise jump: <code>j += out[j]</code>.",
                    "When the loop ends with a real <code>j</code>, set <code>out[i] = j - i</code>.",
                    "Return <code>out</code>.",
                ],
                "why": [
                    "Every day skipped by a jump is ≤ <code>temps[j]</code> ≤ <code>temps[i]</code>, so no warmer day is ever skipped, and the first day that stops the loop is the nearest warmer one.",
                    "Each jump lands on a strictly warmer day, following the same chains of warmer days the stack approach pops, so the total work is <strong>O(n)</strong> amortised, as with the stack.",
                    "No stack is needed: <strong>O(1)</strong> extra space beyond <code>out</code>.",
                ],
                "dry": [
                    [
                        "i=6 (76): j=7 (73) is colder and out[7] = 0, so out[6] stays 0. i=5 (72): j=6 (76) is warmer, out[5] = 1.",
                        "i=4 (69): j=5 (72), out[4] = 1.",
                        "i=3 (71): j=4 (69) is colder, jump by out[4] = 1 to j=5 (72), warmer: out[3] = 2.",
                        "i=2 (75): j=3 (71), jump 2 to j=5 (72), jump 1 to j=6 (76): out[2] = 4. Day 4 is skipped entirely.",
                        "i=1 (74): j=2 is warmer, out[1] = 1. i=0 (73): out[0] = 1. Returns <strong>[1, 1, 4, 2, 1, 1, 0, 0]</strong>.",
                    ],
                    [
                        "i=2 (20): j=3 (40) is warmer, out[2] = 1.",
                        "i=1 (30): j=2 (20) is colder, jump by out[2] = 1 to j=3 (40): out[1] = 2.",
                        "i=0 (30): j=1 (30) is not warmer (≤), jump by out[1] = 2 to j=3 (40): out[0] = 3.",
                        "Returns <strong>[3, 2, 1, 0]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is it safe to stop when <code>out[j] == 0</code>?",
                     "That means no day after <code>j</code> is warmer than <code>j</code>. Since <code>temps[j] &gt;= temps[i]</code>, none of them is warmer than <code>i</code> either."],
                    ["Why <code>&lt;=</code> in the while condition?",
                     "A day with the same temperature is not warmer, so the search has to continue past it, as with example 2's two 30s."],
                    ["Why start at <code>n - 2</code>?",
                     "The last day has no later days, so its answer is always 0, which <code>out</code> already holds."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ online stock span
    "online-stock-span": {
        "examples": [
            {"setup": "s = StockSpanner()",
             "call": "[s.next(p) for p in [100, 80, 60, 70, 60, 75, 85]]", "expect": "[1, 1, 1, 2, 1, 4, 6]"},
            {"setup": "s = StockSpanner()",
             "call": "[s.next(p) for p in [5, 5, 3, 6]]", "expect": "[1, 2, 1, 4]"},
        ],
        "approaches": {
            "Scan back through history": {
                "idea": [
                    "The span of today's price is the number of consecutive days, ending today, whose price is ≤ today's.",
                    "Store every price and, on each call, walk backwards from today until a strictly higher price appears.",
                    "Correct and simple, but a long rising run is rescanned on every call.",
                ],
                "steps": [
                    "<code>__init__</code>: <code>self.prices = []</code>.",
                    "<code>next(price)</code>: append <code>price</code>, so today is included in the walk.",
                    "Set <code>span = 0</code> and loop <code>p</code> over <code>reversed(self.prices)</code>.",
                    "If <code>p &gt; price</code>, the run is broken: <code>break</code>.",
                    "Otherwise <code>span += 1</code>. Return <code>span</code> after the loop.",
                ],
                "why": [
                    "The walk starts at today and stops at the first higher price, so it counts exactly the consecutive days with price ≤ today's.",
                    "Today always counts (<code>price &gt; price</code> is false), so the span is at least 1.",
                    "One call can walk the whole history: <strong>O(n)</strong> per call, <strong>O(n²)</strong> for n rising prices. All prices are kept: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "100: only itself, span 1. 80: 100 &gt; 80 stops it, span 1. 60: span 1.",
                        "70: counts 70 and 60, stops at 80: span 2.",
                        "60: stops at 70: span 1.",
                        "75: counts 75, 60, 70, 60, stops at 80: span 4.",
                        "85: counts 85, 75, 60, 70, 60, 80, stops at 100: span 6. Result <strong>[1, 1, 1, 2, 1, 4, 6]</strong>.",
                    ],
                    [
                        "5: span 1.",
                        "5: the earlier 5 is not higher, so it counts: span 2.",
                        "3: stops at 5: span 1.",
                        "6: counts 6, 3, 5, 5 and runs out of history: span 4.",
                        "Result <strong>[1, 2, 1, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>p &gt; price</code> and not <code>p &gt;= price</code>?",
                     "Equal prices belong in the span. With <code>&gt;=</code>, example 2's second 5 would get span 1 instead of 2."],
                    ["Why append before scanning?",
                     "So today is the first item visited and counted. Otherwise you would have to start <code>span</code> at 1."],
                    ["When does this get slow?",
                     "On a rising sequence every call walks the whole history, so n calls cost about n²/2 steps."],
                ],
            },
            "Monotonic stack of (price, span)": {
                "idea": [
                    "Once a day is covered by a later, higher-or-equal price, it can never stop a future scan on its own: the later day stops it first or covers it.",
                    "So fold covered days into the day that covered them. Keep a stack of <code>(price, span)</code> with strictly decreasing prices.",
                    "Today pops every entry with price ≤ today's and adds their spans to its own.",
                ],
                "steps": [
                    "<code>__init__</code>: <code>self.stack = []</code>.",
                    "<code>next(price)</code>: start with <code>span = 1</code> for today.",
                    "While the top's price <code>self.stack[-1][0] &lt;= price</code>, pop it and add its span: <code>span += self.stack.pop()[1]</code>.",
                    "Push <code>(price, span)</code>; today now stands in for all the days it absorbed.",
                    "Return <code>span</code>.",
                ],
                "why": [
                    "Each stack entry's span counts itself plus every day it absorbed, so the entries between two neighbours on the stack cover the whole history without gaps.",
                    "Popping stops at the first strictly higher price, which is exactly where the backward scan would stop, so the sum of popped spans plus 1 is today's span.",
                    "Each price is pushed once and popped at most once: <strong>amortised O(1)</strong> per call. In a falling market nothing is popped: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "100, 80, 60: nothing to pop. stack = [(100,1), (80,1), (60,1)].",
                        "70: pops (60,1), span 2. stack = [(100,1), (80,1), (70,2)].",
                        "60: pushed with span 1.",
                        "75: pops (60,1) and (70,2), span 1 + 1 + 2 = 4. stack = [(100,1), (80,1), (75,4)].",
                        "85: pops (75,4) and (80,1), span 6. stack = [(100,1), (85,6)]. Result <strong>[1, 1, 1, 2, 1, 4, 6]</strong>.",
                    ],
                    [
                        "5: stack = [(5,1)], span 1.",
                        "5: 5 ≤ 5, pops (5,1), span 2. stack = [(5,2)].",
                        "3: pushed, stack = [(5,2), (3,1)], span 1.",
                        "6: pops (3,1) and (5,2), span 4. stack = [(6,4)].",
                        "Result <strong>[1, 2, 1, 4]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why store the span with each price?",
                     "Popped days are gone from the stack, but they still count for later spans. The stored span remembers how many days each entry represents."],
                    ["Why pop on <code>&lt;=</code> and not <code>&lt;</code>?",
                     "Equal prices extend the span. With <code>&lt;</code>, example 2's second 5 would stop at the first 5 and report 1."],
                    ["Why is it amortised and not strictly O(1)?",
                     "A single call can pop many entries, as 85 does in example 1. Each entry is popped only once, though, so n calls do at most n pops in total."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ car fleet
    "car-fleet": {
        "examples": [
            {"call": "car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3])", "expect": "3"},
            {"call": "car_fleet(10, [0, 5, 7], [2, 1, 1])", "expect": "2"},
        ],
        "approaches": {
            "Sort by position, stack of fleet arrival times": {
                "idea": [
                    "Cars cannot pass, so a car only interacts with the cars ahead of it. Process cars from closest-to-target to furthest.",
                    "For each car compute the time it would need alone: <code>(target - p) / s</code>.",
                    "If that time is no more than the time of the fleet just ahead, the car catches it before the target and joins. If it is larger, it never catches up and starts a new fleet.",
                ],
                "steps": [
                    "Pair positions with speeds and sort by position, descending: <code>sorted(zip(position, speed), reverse=True)</code>.",
                    "For each car <code>(p, s)</code>, compute <code>t = (target - p) / s</code>.",
                    "If the stack is empty or <code>t &gt; stack[-1]</code>, push <code>t</code>: a new, slower fleet.",
                    "Otherwise do nothing: the car merges into the fleet ahead and travels at its pace.",
                    "Return <code>len(stack)</code>.",
                ],
                "why": [
                    "A car that catches the fleet ahead is slowed to that fleet's arrival time, so the fleet's time does not change and the car adds nothing new.",
                    "A car with a larger time stays behind the fleet ahead all the way, so it leads a separate fleet, and cars further back are now compared with it.",
                    "Sorting costs <strong>O(n log n)</strong> and the scan O(n). The stack can hold one time per car: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Sorted: (10,2), (8,4), (5,1), (3,3), (0,1).",
                        "Car at 10: t = 1.0, stack = [1.0]. Car at 8: t = 1.0, not &gt; 1.0, joins.",
                        "Car at 5: t = 7.0 &gt; 1.0, new fleet, stack = [1.0, 7.0].",
                        "Car at 3: t = 3.0 ≤ 7.0, catches the car at 5 and joins.",
                        "Car at 0: t = 12.0, new fleet. stack = [1.0, 7.0, 12.0]: <strong>3</strong>.",
                    ],
                    [
                        "Sorted: (7,1), (5,1), (0,2).",
                        "Car at 7: t = 3.0, stack = [3.0].",
                        "Car at 5: t = 5.0 &gt; 3.0, new fleet, stack = [3.0, 5.0].",
                        "Car at 0: t = 10 / 2 = 5.0, equal to 5.0, so it reaches the car at 5 exactly at the target and joins.",
                        "Returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Why <code>t &gt; stack[-1]</code> and not <code>&gt;=</code>?",
                     "Equal times mean the cars meet exactly at the target, which counts as one fleet. With <code>&gt;=</code>, example 2 would wrongly give 3."],
                    ["Why compare only with the top of the stack?",
                     "The top is the slowest fleet so far, and it is the one directly ahead. Any car that cannot catch it cannot catch anything further ahead either."],
                    ["Why sort descending by position?",
                     "Merging is decided by the car ahead, so the car nearest the target must be processed first."],
                ],
            },
            "Sort, track only the slowest fleet ahead": {
                "idea": [
                    "In the stack version the times only ever increase, and only the top is ever read.",
                    "So the stack can be replaced by a count <code>fleets</code> and the time of the last fleet started, <code>slowest</code>.",
                    "Same logic, constant extra space after sorting.",
                ],
                "steps": [
                    "Set <code>fleets = 0</code> and <code>slowest = 0.0</code>.",
                    "Sort the cars by position, descending.",
                    "For each car compute <code>t = (target - p) / s</code>.",
                    "If <code>t &gt; slowest</code>, it starts a new fleet: <code>fleets += 1</code> and <code>slowest = t</code>.",
                    "Otherwise it joins the fleet ahead. Return <code>fleets</code>.",
                ],
                "why": [
                    "<code>slowest</code> is exactly what <code>stack[-1]</code> was, and <code>fleets</code> is the stack's length, so the answers match.",
                    "Starting <code>slowest</code> at 0.0 makes the first car always start a fleet, since every car has a positive time (it starts before the target).",
                    "Sorting dominates: <strong>O(n log n)</strong> time. Apart from the sorted list, <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "Car at 10: t = 1.0 &gt; 0.0, fleets = 1, slowest = 1.0.",
                        "Car at 8: t = 1.0, not &gt; 1.0, joins.",
                        "Car at 5: t = 7.0, fleets = 2, slowest = 7.0. Car at 3: t = 3.0, joins.",
                        "Car at 0: t = 12.0, fleets = 3.",
                        "Returns <strong>3</strong>.",
                    ],
                    [
                        "Car at 7: t = 3.0, fleets = 1, slowest = 3.0.",
                        "Car at 5: t = 5.0, fleets = 2, slowest = 5.0.",
                        "Car at 0: t = 5.0, not &gt; 5.0, joins.",
                        "Returns <strong>2</strong>.",
                    ],
                ],
                "faq": [
                    ["Is <code>slowest = 0.0</code> safe as a start value?",
                     "Yes, as long as every position is below the target, which the problem guarantees, so every time is positive."],
                    ["Can floating-point division give a wrong tie?",
                     "In principle two equal times computed differently could differ in the last bit. To be fully safe, compare <code>(target - p1) * s2</code> with <code>(target - p2) * s1</code> using integers."],
                    ["Why keep the stack version at all?",
                     "It makes the fleets visible and is the pattern interviewers expect. This one is the same idea with the unused part removed."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ simplify path
    "simplify-path": {
        "examples": [
            {"call": 'simplify_path("/home/./user//docs/../.../")', "expect": '"/home/user/..."'},
            {"call": 'simplify_path("/../a/../../b/")', "expect": '"/b"'},
        ],
        "approaches": {
            "Split on '/', stack of directory names": {
                "idea": [
                    "Splitting on <code>/</code> breaks the path into parts; repeated slashes just produce empty parts.",
                    "Walking the parts left to right is like walking the directory tree: a name goes one level down (push), <code>..</code> goes one level up (pop).",
                    "Empty parts and <code>.</code> stay in place, so they are ignored. Everything else, including <code>...</code>, is a normal name.",
                ],
                "steps": [
                    "Split <code>path</code> on <code>\"/\"</code> and loop over each <code>part</code>.",
                    "If <code>part == \"..\"</code>, pop the stack if it is not empty; at the root, <code>..</code> does nothing.",
                    "Else if <code>part</code> is non-empty and not <code>\".\"</code>, push it.",
                    "Skip empty parts and <code>\".\"</code>.",
                    "Return <code>\"/\" + \"/\".join(stack)</code>.",
                ],
                "why": [
                    "The stack always holds the directories from the root down to the current one, so the join is the canonical path.",
                    "Leading, trailing and repeated slashes only create empty parts, which are skipped, so the result has single slashes and no trailing one.",
                    "Splitting, the loop and the join are all linear: <strong>O(n)</strong> time. The parts and the stack take <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Parts: '', 'home', '.', 'user', '', 'docs', '..', '...', ''.",
                        "'' skipped, 'home' pushed, '.' skipped, 'user' pushed. stack = ['home', 'user'].",
                        "'' skipped, 'docs' pushed, '..' pops it. stack = ['home', 'user'].",
                        "'...' is a real name, pushed. The final '' is skipped.",
                        "Returns <strong>\"/home/user/...\"</strong>.",
                    ],
                    [
                        "Parts: '', '..', 'a', '..', '..', 'b', ''.",
                        "'..' at the root: the stack is empty, nothing happens.",
                        "'a' pushed, '..' pops it. The next '..' again finds an empty stack.",
                        "'b' pushed. stack = ['b'].",
                        "Returns <strong>\"/b\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is <code>...</code> kept?",
                     "Only <code>.</code> and <code>..</code> are special. Any other run of dots is an ordinary directory name, as in example 1."],
                    ["What happens with <code>/../</code>?",
                     "The <code>..</code> finds an empty stack and is ignored, so the result is <code>\"/\"</code>: you cannot go above the root."],
                    ["Why does an empty stack still return <code>\"/\"</code>?",
                     "<code>\"/\".join([])</code> is the empty string, and the leading <code>\"/\"</code> is always added, giving the root."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ decode string
    "decode-string": {
        "examples": [
            {"call": 'decode_string("2[a3[bc]]d")', "expect": '"abcbcbcabcbcbcd"'},
            {"call": 'decode_string("x10[y]z")', "expect": '"x" + "y" * 10 + "z"'},
        ],
        "approaches": {
            "Stack of (outer string, repeat count)": {
                "idea": [
                    "Brackets nest, so when a <code>[</code> opens, the text built so far has to be put aside until the matching <code>]</code>.",
                    "Push the outer text and the repeat count, then build the inner text from scratch in <code>cur</code>.",
                    "At <code>]</code>, pop them back and glue: <code>outer + cur * k</code>.",
                ],
                "steps": [
                    "Start with <code>stack = []</code>, <code>cur = \"\"</code>, <code>num = 0</code>.",
                    "Digit: <code>num = num * 10 + int(ch)</code>, so multi-digit counts are read correctly.",
                    "<code>[</code>: push <code>(cur, num)</code> and reset <code>cur = \"\"</code>, <code>num = 0</code>.",
                    "<code>]</code>: pop <code>(outer, k)</code> and set <code>cur = outer + cur * k</code>.",
                    "Letter: <code>cur += ch</code>.",
                    "Return <code>cur</code>.",
                ],
                "why": [
                    "Each stack entry is the text and count waiting outside one open bracket, and the innermost bracket is on top, so <code>]</code> always closes the right one.",
                    "After a <code>]</code>, <code>cur</code> holds the fully decoded text of the enclosing level so far, so further letters and groups append correctly.",
                    "Every output character is built a bounded number of times per nesting level, so the cost is about the output size: <strong>O(output)</strong> time and <strong>O(output)</strong> space.",
                ],
                "dry": [
                    [
                        "<code>2</code>: num = 2. <code>[</code>: push ('', 2), cur = ''.",
                        "<code>a</code>: cur = 'a'. <code>3</code>: num = 3. <code>[</code>: push ('a', 3), cur = ''.",
                        "<code>b</code>, <code>c</code>: cur = 'bc'.",
                        "<code>]</code>: pop ('a', 3), cur = 'a' + 'bc' × 3 = 'abcbcbc'. <code>]</code>: pop ('', 2), cur = 'abcbcbcabcbcbc'.",
                        "<code>d</code>: appended. Returns <strong>\"abcbcbcabcbcbcd\"</strong>.",
                    ],
                    [
                        "<code>x</code>: cur = 'x'.",
                        "<code>1</code>: num = 1. <code>0</code>: num = 1 × 10 + 0 = 10.",
                        "<code>[</code>: push ('x', 10), cur = ''. <code>y</code>: cur = 'y'.",
                        "<code>]</code>: pop ('x', 10), cur = 'x' + 'y' × 10. <code>z</code>: appended.",
                        "Returns <strong>\"xyyyyyyyyyyz\"</strong> (ten y's).",
                    ],
                ],
                "faq": [
                    ["Why <code>num * 10 + int(ch)</code> instead of <code>int(ch)</code>?",
                     "Counts can have several digits. Example 2 would otherwise read 10 as just 0."],
                    ["Why reset <code>num</code> at <code>[</code>?",
                     "The count has been saved on the stack, and the next group inside the brackets needs its own count starting from 0."],
                    ["Is repeated string concatenation slow?",
                     "Each <code>+</code> copies the string, so very long outputs with many letters can cost more than the output size. Building lists and joining avoids that, as the recursive version does."],
                ],
            },
            "Recursive descent": {
                "idea": [
                    "Each bracketed group is a smaller copy of the whole problem, so a function can decode one level and call itself for a nested group.",
                    "<code>parse(i)</code> decodes from index <code>i</code> until a <code>]</code> or the end, and returns the text and where it stopped.",
                    "The call stack plays the role of the explicit stack.",
                ],
                "steps": [
                    "<code>parse(i)</code> starts with <code>out = []</code> and <code>num = 0</code>.",
                    "Loop while <code>i &lt; len(s)</code> and <code>s[i] != \"]\"</code>.",
                    "Digit: build <code>num</code> and move on.",
                    "<code>[</code>: <code>inner, i = parse(i + 1)</code>, append <code>inner * num</code>, reset <code>num</code>, then <code>i += 1</code> to skip the <code>]</code>.",
                    "Letter: append it.",
                    "Return <code>\"\".join(out), i</code>. The answer is <code>parse(0)[0]</code>.",
                ],
                "why": [
                    "Every call stops exactly at its own closing <code>]</code> (or the end), and returns that index, so the caller resumes right after the group.",
                    "Pieces are collected in a list and joined once, so each level does work proportional to the text it produces: <strong>O(output)</strong> time.",
                    "The recursion depth is the nesting depth, and the strings built are <strong>O(output)</strong> space.",
                ],
                "dry": [
                    [
                        "<code>parse(0)</code>: reads 2, sees <code>[</code>, calls <code>parse(2)</code>.",
                        "<code>parse(2)</code>: appends 'a', reads 3, sees <code>[</code>, calls <code>parse(5)</code>.",
                        "<code>parse(5)</code>: appends b, c, stops at the <code>]</code> at index 7, returns ('bc', 7).",
                        "<code>parse(2)</code> appends 'bc' × 3, skips to 8, stops at <code>]</code>, returns ('abcbcbc', 8). <code>parse(0)</code> appends it × 2 and skips to 9.",
                        "It appends 'd' and returns <strong>\"abcbcbcabcbcbcd\"</strong>.",
                    ],
                    [
                        "<code>parse(0)</code>: appends 'x', then reads 1 and 0: num = 10.",
                        "<code>[</code> at index 3: calls <code>parse(4)</code>, which appends 'y' and returns ('y', 5).",
                        "<code>parse(0)</code> appends 'y' × 10, resets num, and skips to index 6.",
                        "It appends 'z' and reaches the end.",
                        "Returns <strong>\"xyyyyyyyyyyz\"</strong>.",
                    ],
                ],
                "faq": [
                    ["Why does <code>parse</code> return the index too?",
                     "The caller needs to know where the nested group ended to continue reading after it. Returning <code>i</code> passes that position back up."],
                    ["Why <code>i += 1</code> after the recursive call?",
                     "The inner call stops <em>on</em> the <code>]</code> without consuming it. The caller skips it."],
                    ["Can deep nesting break this?",
                     "Each bracket level is one call frame, so nesting deeper than Python's recursion limit (about 1000) would raise RecursionError. The stack version has no such limit."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ maximum frequency stack
    "maximum-frequency-stack": {
        "examples": [
            {"setup": "fs = FreqStack()\nfor v in [5, 7, 5, 7, 4, 5]:\n    fs.push(v)",
             "call": "[fs.pop() for _ in range(4)]", "expect": "[5, 7, 5, 4]"},
            {"setup": "fs = FreqStack()\nfor v in [1, 2, 1, 2]:\n    fs.push(v)",
             "call": "[fs.pop() for _ in range(4)]", "expect": "[2, 1, 2, 1]"},
        ],
        "approaches": {
            "List plus counts, scan on pop": {
                "idea": [
                    "<code>pop</code> must remove the most frequent value, and among ties the one pushed most recently.",
                    "Keep every pushed value in order in <code>self.items</code> and the current count of each value in <code>self.freq</code>.",
                    "On pop, find the top frequency, then scan from the end for the first item with that frequency: that is the most recent one.",
                ],
                "steps": [
                    "<code>push(val)</code>: append to <code>self.items</code> and do <code>self.freq[val] += 1</code>.",
                    "<code>pop()</code>: <code>top = max(self.freq.values())</code>.",
                    "Scan <code>i</code> from the last index down to 0.",
                    "At the first <code>i</code> with <code>self.freq[self.items[i]] == top</code>, remove it with <code>self.items.pop(i)</code>.",
                    "Decrement its count and return it.",
                ],
                "why": [
                    "Scanning from the end finds the latest occurrence among the most frequent values, which is exactly the tie-break the problem asks for.",
                    "The last occurrence of a value is the copy that pushed its count to its current level, so removing it keeps the counts consistent.",
                    "<code>push</code> is <strong>O(1)</strong>; <code>pop</code> scans the counts and the list and removes from the middle: <strong>O(n)</strong>. Space is <strong>O(n)</strong>.",
                ],
                "dry": [
                    [
                        "items = [5, 7, 5, 7, 4, 5], freq = {5: 3, 7: 2, 4: 1}.",
                        "pop 1: top = 3. Index 5 holds 5 (count 3): remove it, freq[5] = 2.",
                        "pop 2: top = 2. Index 4 is 4 (count 1), index 3 is 7 (count 2): remove 7.",
                        "pop 3: top = 2. Scanning from the end: 4, then 5 at index 2 with count 2: remove 5. pop 4: top = 1, last item 4 qualifies.",
                        "Returns <strong>[5, 7, 5, 4]</strong>.",
                    ],
                    [
                        "items = [1, 2, 1, 2], freq = {1: 2, 2: 2}.",
                        "pop 1: top = 2, the last item 2 qualifies: remove it, freq[2] = 1.",
                        "pop 2: top = 2, only 1 has it; scanning finds 1 at index 2.",
                        "pop 3: top = 1, the last item is 2. pop 4: 1.",
                        "Returns <strong>[2, 1, 2, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why scan from the end?",
                     "Among values with the top frequency, the problem wants the one closest to the top of the stack, which is the latest in the list."],
                    ["Do zero counts left in <code>self.freq</code> cause problems?",
                     "No. A value with count 0 is not in <code>items</code>, and it can only be the max when the stack is empty, which never happens on a valid pop."],
                    ["Why is this slow?",
                     "Each pop scans all counts and possibly the whole list, and <code>list.pop(i)</code> shifts the items after <code>i</code>."],
                ],
            },
            "Heap keyed by (frequency, push time)": {
                "idea": [
                    "The pop order depends on two keys: frequency first, then recency. A heap can order by both.",
                    "On each push, store <code>(-freq, -time, val)</code>, where <code>freq</code> is the value's count including this push.",
                    "The smallest tuple has the highest frequency and, among ties, the latest time.",
                ],
                "steps": [
                    "<code>push(val)</code>: increment <code>self.freq[val]</code> and <code>self.time</code>.",
                    "Push <code>(-self.freq[val], -self.time, val)</code> onto <code>self.heap</code>.",
                    "<code>pop()</code>: <code>heappop</code> the smallest tuple and take its <code>val</code>.",
                    "Decrement <code>self.freq[val]</code> and return <code>val</code>.",
                ],
                "why": [
                    "Each heap entry records the frequency a copy had when it was pushed. Copies are removed newest first, so the remaining entries' frequencies are still accurate.",
                    "Negating both keys turns Python's min-heap into “highest frequency, then most recent”. Times are unique, so <code>val</code> is never compared.",
                    "Each push and pop is one heap operation: <strong>O(log n)</strong>. The heap holds one entry per item: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Pushes create (−1,−1,5), (−1,−2,7), (−2,−3,5), (−2,−4,7), (−1,−5,4), (−3,−6,5).",
                        "pop 1: smallest is (−3,−6,5): returns 5.",
                        "pop 2: frequency 2 ties; −4 &lt; −3, so (−2,−4,7): returns 7.",
                        "pop 3: (−2,−3,5): returns 5. pop 4: frequency 1 ties, (−1,−5,4) is newest: returns 4.",
                        "Returns <strong>[5, 7, 5, 4]</strong>.",
                    ],
                    [
                        "Pushes create (−1,−1,1), (−1,−2,2), (−2,−3,1), (−2,−4,2).",
                        "pop 1: (−2,−4,2): returns 2.",
                        "pop 2: (−2,−3,1): returns 1.",
                        "pop 3: (−1,−2,2): returns 2. pop 4: (−1,−1,1): returns 1.",
                        "Returns <strong>[2, 1, 2, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the frequency stored at push time still valid later?",
                     "Copies of a value come out of the heap newest first, so the copy with the highest recorded frequency is always popped before lower ones."],
                    ["Why include <code>-self.time</code>?",
                     "It breaks frequency ties in favour of the latest push, as the problem requires, and stops Python from ever comparing the values themselves."],
                    ["Why decrement <code>self.freq</code> on pop?",
                     "So the next push of that value records the right frequency."],
                ],
            },
            "A stack per frequency level": {
                "idea": [
                    "When a value reaches count f, push it onto the stack for level f in <code>self.group[f]</code>. A value with count 3 appears in groups 1, 2 and 3.",
                    "The answer to <code>pop</code> is always the top of the highest non-empty group: highest frequency, and most recent within it.",
                    "Popping a value from level f simply returns it to count f − 1, where its older copy is already waiting in group f − 1.",
                ],
                "steps": [
                    "<code>push(val)</code>: <code>self.freq[val] += 1</code>, and let <code>f</code> be the new count.",
                    "Append <code>val</code> to <code>self.group[f]</code> and update <code>self.max_freq = max(self.max_freq, f)</code>.",
                    "<code>pop()</code>: pop <code>val</code> from <code>self.group[self.max_freq]</code> and decrement <code>self.freq[val]</code>.",
                    "If that group is now empty, <code>self.max_freq -= 1</code>.",
                    "Return <code>val</code>.",
                ],
                "why": [
                    "Group f holds exactly the values whose count is at least f, in the order they reached f, so its top is the most recent value at that frequency.",
                    "When the top group empties, group <code>max_freq − 1</code> is non-empty, because every value that reached f also passed through f − 1. So decrementing by one is enough.",
                    "Every operation is a few dict and list operations: <strong>O(1)</strong>. Each pushed item sits in exactly one group: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "After the pushes: group 1 = [5, 7, 4], group 2 = [5, 7], group 3 = [5], max_freq = 3.",
                        "pop 1: group 3 gives 5. Group 3 empty, max_freq = 2.",
                        "pop 2: group 2 gives 7. pop 3: group 2 gives 5; empty, max_freq = 1.",
                        "pop 4: group 1 gives 4.",
                        "Returns <strong>[5, 7, 5, 4]</strong>.",
                    ],
                    [
                        "After the pushes: group 1 = [1, 2], group 2 = [1, 2], max_freq = 2.",
                        "pop 1: group 2 gives 2. pop 2: group 2 gives 1; empty, max_freq = 1.",
                        "pop 3: group 1 gives 2.",
                        "pop 4: group 1 gives 1; empty, max_freq = 0.",
                        "Returns <strong>[2, 1, 2, 1]</strong>.",
                    ],
                ],
                "faq": [
                    ["Why is the same value stored in several groups?",
                     "Each copy marks the moment it reached that frequency. After popping it from group 3, the value still has count 2 and its entry in group 2 keeps its place in the order."],
                    ["Can <code>max_freq</code> skip a level when it decreases?",
                     "No. A value can only reach level f after passing level f − 1, so the level below a non-empty one is never empty."],
                    ["Why <code>defaultdict(list)</code>?",
                     "A new frequency level gets an empty list automatically the first time a value reaches it."],
                ],
            },
        },
    },

    # ------------------------------------------------------------------ largest rectangle in histogram
    "largest-rectangle-histogram": {
        "examples": [
            {"call": "largest_rectangle_area([2, 1, 5, 6, 2, 3])", "expect": "10"},
            {"call": "largest_rectangle_area([2, 4, 4, 1])", "expect": "8"},
        ],
        "approaches": {
            "Every pair of edges": {
                "idea": [
                    "A rectangle spans bars <code>i..j</code> and its height is the shortest bar in that range.",
                    "Fix the left edge <code>i</code> and extend the right edge <code>j</code>, keeping the running minimum <code>low</code> so it does not need recomputing.",
                    "The area for each pair is <code>low * (j - i + 1)</code>; keep the best.",
                ],
                "steps": [
                    "Set <code>best = 0</code>.",
                    "Loop <code>i</code> over every bar and start <code>low = heights[i]</code>.",
                    "Loop <code>j</code> from <code>i</code> to the end, updating <code>low = min(low, heights[j])</code>.",
                    "Update <code>best = max(best, low * (j - i + 1))</code>.",
                    "Return <code>best</code>.",
                ],
                "why": [
                    "The largest rectangle covers some contiguous range at that range's minimum height, and every range is tried.",
                    "The running minimum makes each pair O(1), so there are n(n + 1)/2 steps: <strong>O(n²)</strong> time.",
                    "Only a few variables: <strong>O(1)</strong> space.",
                ],
                "dry": [
                    [
                        "i=0 (2): areas 2, 2, 3, 4, 5, 6 as the minimum drops to 1. best = 6.",
                        "i=1 (1): areas 1 to 5. best stays 6.",
                        "i=2 (5): areas 5, then 5 × 2 = 10, then 2 × 3 = 6, 2 × 4 = 8. best = 10.",
                        "i=3, 4, 5: the best are 6, 4 and 3.",
                        "Returns <strong>10</strong>, bars 5 and 6 at height 5.",
                    ],
                    [
                        "i=0 (2): areas 2, 4, 6, then 1 × 4 = 4. best = 6.",
                        "i=1 (4): areas 4, 4 × 2 = 8, then 1 × 3 = 3. best = 8.",
                        "i=2 (4): areas 4, 2. i=3 (1): area 1.",
                        "Returns <strong>8</strong>, the two 4s.",
                    ],
                ],
                "faq": [
                    ["Why can the running minimum be reused as <code>j</code> grows?",
                     "Adding one bar to the right can only keep the minimum or lower it to that bar, so <code>min(low, heights[j])</code> is the new minimum."],
                    ["Does it need the minimum from scratch for each pair?",
                     "No, and recomputing it would make this O(n³)."],
                    ["Is it useful beyond small inputs?",
                     "It is the reference answer: easy to trust and good for checking the stack versions on random tests, as the problem's tests do."],
                ],
            },
            "Divide and conquer at the minimum": {
                "idea": [
                    "The shortest bar in a range splits the problem: a rectangle either uses the whole range at that bar's height, or lies fully on one side of it.",
                    "So the answer for <code>lo..hi</code> is the max of <code>heights[m] * (hi - lo + 1)</code> and the answers for the two sides.",
                    "Each side is solved the same way, recursively.",
                ],
                "steps": [
                    "<code>solve(lo, hi)</code> returns 0 for an empty range (<code>lo &gt; hi</code>).",
                    "Find <code>m</code>, the index of the shortest bar in <code>lo..hi</code>, with <code>min(range(...), key=heights.__getitem__)</code>.",
                    "Compute the full-width area <code>heights[m] * (hi - lo + 1)</code>.",
                    "Recurse on <code>lo..m-1</code> and <code>m+1..hi</code>.",
                    "Return the largest of the three. Start with <code>solve(0, len(heights) - 1)</code>.",
                ],
                "why": [
                    "Any rectangle that includes bar <code>m</code> is at most <code>heights[m]</code> tall, so the widest such one is the full range. Rectangles that avoid <code>m</code> lie in one half.",
                    "Each level spends O(range size) finding the minimum. Balanced splits give <strong>O(n log n)</strong>; sorted heights split off one bar at a time, giving <strong>O(n²)</strong>.",
                    "The recursion depth is O(log n) for balanced splits and <strong>O(n)</strong> in the worst case.",
                ],
                "dry": [
                    [
                        "<code>solve(0,5)</code>: minimum is 1 at m=1, full width 1 × 6 = 6.",
                        "Left <code>solve(0,0)</code>: 2.",
                        "Right <code>solve(2,5)</code>: minimum 2 at m=4, area 2 × 4 = 8. Its left side <code>solve(2,3)</code>: m=2, area 5 × 2 = 10; its right side <code>solve(5,5)</code>: 3.",
                        "<code>solve(2,5)</code> returns 10.",
                        "<code>solve(0,5)</code> returns max(6, 2, 10) = <strong>10</strong>.",
                    ],
                    [
                        "<code>solve(0,3)</code>: minimum is 1 at m=3, area 1 × 4 = 4. Only a left side.",
                        "<code>solve(0,2)</code>: minimum 2 at m=0, area 2 × 3 = 6.",
                        "Its right side <code>solve(1,2)</code>: minimum 4 at m=1 (the first of the ties), area 4 × 2 = 8; <code>solve(2,2)</code> gives 4.",
                        "Back up: 8, then max(6, 8) = 8, then max(4, 8) = 8.",
                        "Returns <strong>8</strong>.",
                    ],
                ],
                "faq": [
                    ["What happens with equal minimums?",
                     "<code>min</code> picks the first one. The other equal bars end up in the right part, where they are handled at the same height, so nothing is lost (example 2)."],
                    ["Why is the worst case quadratic?",
                     "On sorted heights the minimum is always at one end, so each call removes one bar and still scans the rest, like a bad quicksort pivot."],
                    ["Can this be made O(n log n) in the worst case?",
                     "Yes, by finding range minimums with a segment tree or sparse table, but the stack solutions are simpler and O(n)."],
                ],
            },
            "Nearest shorter bar on each side, two stack passes": {
                "idea": [
                    "The best rectangle at full height of bar <code>i</code> stretches until a strictly shorter bar on each side.",
                    "So find, for every bar, the index of the nearest shorter bar to the left (<code>left[i]</code>) and to the right (<code>right[i]</code>). Its width is <code>right[i] - left[i] - 1</code>.",
                    "Both can be found in one monotonic-stack pass each.",
                ],
                "steps": [
                    "Initialise <code>left = [-1] * n</code> and <code>right = [n] * n</code>: “no shorter bar” means the edge.",
                    "Left to right: pop while <code>heights[stack[-1]] &gt;= heights[i]</code>; the top left over is <code>left[i]</code>. Push <code>i</code>.",
                    "Right to left with a fresh stack: the same popping gives <code>right[i]</code>.",
                    "For each bar compute <code>h * (right[i] - left[i] - 1)</code>.",
                    "Return the maximum.",
                ],
                "why": [
                    "The largest rectangle has a shortest bar, and that rectangle can always be widened until the nearest shorter bars, so checking every bar at its own height finds it.",
                    "Popped bars are ≥ the current bar, so they can never be the nearest shorter bar for anything later; the stack stays increasing and its top is the answer.",
                    "Each pass pushes and pops every index once: <strong>O(n)</strong> time. The two arrays and the stack: <strong>O(n)</strong> space.",
                ],
                "dry": [
                    [
                        "Left pass: left = [−1, −1, 1, 2, 1, 4]. For example, bar 4 (2) pops 6 and 5 and stops at bar 1 (1).",
                        "Right pass: right = [1, 6, 4, 4, 6, 6]. Bar 2 (5) stops at bar 4 (2).",
                        "Areas: 2 × 1 = 2, 1 × 6 = 6, 5 × 2 = 10, 6 × 1 = 6, 2 × 4 = 8, 3 × 1 = 3.",
                        "The 5 spans bars 2..3 between the shorter bars at 1 and 4.",
                        "Returns <strong>10</strong>.",
                    ],
                    [
                        "Left pass: left = [−1, 0, 0, −1]. Bar 2 pops the equal bar 1 because of <code>&gt;=</code>, so its left is 0.",
                        "Right pass: right = [3, 3, 3, 4]. Bar 1 pops the equal bar 2 the same way.",
                        "Areas: 2 × 3 = 6, 4 × 2 = 8, 4 × 2 = 8, 1 × 4 = 4.",
                        "Both 4s see the full width of the pair.",
                        "Returns <strong>8</strong>.",
                    ],
                ],
                "faq": [
                    ["Why pop on <code>&gt;=</code> and not <code>&gt;</code>?",
                     "The boundary must be a strictly shorter bar. With <code>&gt;</code> in both passes, equal bars block each other: on example 2 each 4 gets width 1 and the function returns 6 instead of 8."],
                    ["Why <code>-1</code> and <code>n</code> as defaults?",
                     "They act as imaginary zero-height bars just outside the array, so the width formula works when nothing shorter exists."],
                    ["Why two passes instead of one?",
                     "It is easier to reason about: each pass answers one question. The one-pass version gets both boundaries at the moment a bar is popped."],
                ],
            },
            "One stack pass, settle bars as they are popped": {
                "idea": [
                    "Keep a stack of indices with increasing heights. A bar waits on the stack until a bar no taller than it arrives.",
                    "When bar <code>i</code> pops a bar, <code>i</code> is its right boundary and the bar below it on the stack is its left boundary, so its rectangle is known right then.",
                    "Appending a 0 height at the end flushes every bar still waiting.",
                ],
                "steps": [
                    "Loop <code>i, h</code> over <code>heights + [0]</code>.",
                    "While the stack is non-empty and <code>heights[stack[-1]] &gt;= h</code>, pop it and call its height <code>height</code>.",
                    "The left boundary is the new top, <code>left = stack[-1]</code>, or −1 if the stack is empty.",
                    "Update <code>best = max(best, height * (i - left - 1))</code>.",
                    "Push <code>i</code>. Return <code>best</code>.",
                ],
                "why": [
                    "The stack is increasing, so the bar below a popped bar is the nearest shorter (or equal) bar on its left, and <code>i</code> is the first bar to its right that is not taller.",
                    "With equal heights, the earlier bar is popped with a too-narrow width, but the last of the equal run is popped later with the full width, so the maximum is still found.",
                    "Each index is pushed and popped once: <strong>O(n)</strong> time, <strong>O(n)</strong> space for the stack (plus the extended list).",
                ],
                "dry": [
                    [
                        "i=0 (2): push. i=1 (1): pops bar 0, width 1, area 2. stack = [1].",
                        "i=2 (5), i=3 (6): pushed. stack = [1, 2, 3].",
                        "i=4 (2): pops 6 (left 2, area 6), then 5 (left 1, width 2, area 10). best = 10. stack = [1, 4].",
                        "i=5 (3): pushed. i=6 (the extra 0): pops 3 (area 3), 2 (left 1, area 8), 1 (left −1, area 6).",
                        "Returns <strong>10</strong>.",
                    ],
                    [
                        "i=0 (2), i=1 (4): pushed. stack = [0, 1].",
                        "i=2 (4): 4 ≥ 4 pops bar 1 with left 0: area 4 × 1 = 4, too narrow. stack = [0, 2].",
                        "i=3 (1): pops bar 2 with left 0: area 4 × 2 = 8. Pops bar 0: area 2 × 3 = 6.",
                        "i=4 (the extra 0): pops bar 3: area 1 × 4 = 4.",
                        "Returns <strong>8</strong>.",
                    ],
                ],
                "faq": [
                    ["Why append a 0 at the end?",
                     "Bars still on the stack have no shorter bar to their right. The 0 is shorter than everything, so it pops them all and settles their areas."],
                    ["Why is the width <code>i - left - 1</code>?",
                     "The rectangle spans the bars strictly between <code>left</code> and <code>i</code>, and there are <code>i - left - 1</code> of them."],
                    ["Isn't the equal-height pop wrong?",
                     "It under-counts that one bar, as in example 2 (area 4). The later equal bar covers the same rectangle with the full width, so the answer is still right."],
                ],
            },
        },
    },
}
