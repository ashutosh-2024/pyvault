"""Write-ups for the Stacks topic (monotonic-stack)."""

EXPLAIN = {
    # ------------------------------------------------------------------ baseball game
    "baseball-game": {
        "example": {"call": 'cal_points(["5", "-2", "4", "C", "D", "9", "+", "+"])', "expect": "27"},
        "approaches": {
            "Stack of valid scores": {
                "idea": [
                    "Every operation only ever looks at the <em>most recent</em> valid scores, which is exactly what the top of a stack gives you.",
                    "<code>C</code> undoes the last score, so after it the previous score must become the latest again; popping a stack does that for free.",
                    "<code>D</code> and <code>+</code> read the top one or two scores and record a new one, so they peek and push.",
                    "Whatever is left on the stack at the end is the record, and the answer is its sum.",
                ],
                "steps": [
                    "Start with an empty list used as a stack.",
                    "For an integer token, push <code>int(op)</code>.",
                    "For <code>+</code>, push <code>stack[-1] + stack[-2]</code>; for <code>D</code>, push <code>2 * stack[-1]</code>.",
                    "For <code>C</code>, pop the top score so it no longer counts and is no longer visible to later operations.",
                    "After the last token, return <code>sum(stack)</code>.",
                ],
                "why": [
                    "The stack always equals the current record in order, so the top is always the previous score the rules refer to.",
                    "Because <code>C</code> really removes the score, a later <code>D</code> or <code>+</code> correctly sees the score before it.",
                    "Each token does O(1) work and the final sum is O(n), so the total is O(n) time and O(n) space for the record.",
                ],
                "dry": [
                    "<code>\"5\"</code>: push 5, stack <code>[5]</code>.",
                    "<code>\"-2\"</code>: push -2, stack <code>[5, -2]</code>.",
                    "<code>\"4\"</code>: push 4, stack <code>[5, -2, 4]</code>.",
                    "<code>\"C\"</code>: pop the 4, stack <code>[5, -2]</code>; the 4 is gone for good.",
                    "<code>\"D\"</code>: double the top, 2 × -2 = -4, stack <code>[5, -2, -4]</code>.",
                    "<code>\"9\"</code>: push 9, stack <code>[5, -2, -4, 9]</code>.",
                    "<code>\"+\"</code>: -4 + 9 = 5, stack <code>[5, -2, -4, 9, 5]</code>.",
                    "<code>\"+\"</code>: 9 + 5 = 14, stack <code>[5, -2, -4, 9, 5, 14]</code>.",
                    "Sum: 5 - 2 - 4 + 9 + 5 + 14 = <strong>27</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ valid parentheses
    "valid-parentheses": {
        "example": {"call": 'is_valid("([{}])[")', "expect": "False"},
        "approaches": {
            "Repeatedly delete adjacent pairs": {
                "idea": [
                    "Any non-empty valid string must contain an innermost pair such as <code>()</code>, <code>[]</code> or <code>{}</code> with nothing between the two brackets.",
                    "Deleting that pair leaves a string that is valid exactly when the original was, so we can keep peeling pairs away.",
                    "If the string shrinks to empty it was valid; if it gets stuck with brackets left, it was not.",
                ],
                "steps": [
                    "Remember the string from the previous round in <code>prev</code>.",
                    "Remove every <code>()</code>, then every <code>[]</code>, then every <code>{}</code> using <code>str.replace</code>.",
                    "Repeat while the string still changes from one round to the next.",
                    "Return whether what is left is the empty string.",
                ],
                "why": [
                    "Removing an adjacent matched pair never turns an invalid string into a valid one or the other way round, so the final verdict is right.",
                    "Each round is O(n) and a deeply nested string such as <code>(((...)))</code> loses only one pair per round, so there can be n/2 rounds: O(n²) time.",
                    "Each <code>replace</code> builds a new string, so the extra space is O(n).",
                ],
                "dry": [
                    "Round 1: no <code>()</code> or <code>[]</code> is adjacent, but <code>{}</code> is, so <code>\"([{}])[\"</code> becomes <code>\"([])[\"</code>.",
                    "Round 2: there is no <code>()</code> yet; removing <code>[]</code> gives <code>\"()[\"</code>.",
                    "Round 3: removing <code>()</code> leaves <code>\"[\"</code>.",
                    "Round 4: nothing matches, so the string equals <code>prev</code> and the loop stops.",
                    "<code>\"[\"</code> is not empty, so the answer is <strong>False</strong>: that last opener is never closed.",
                ],
            },
            "Stack of open brackets": {
                "idea": [
                    "The bracket that must close next is always the <em>most recently opened</em> one that is still open, which is the top of a stack.",
                    "So push openers, and when a closer arrives check that it matches the top and pop it.",
                    "A closer with an empty stack or the wrong opener on top makes the string invalid immediately.",
                    "Anything still on the stack at the end was opened but never closed.",
                ],
                "steps": [
                    "Map each closer to its opener: <code>{')': '(', ']': '[', '}': '{'}</code>.",
                    "Scan the characters left to right.",
                    "Opener: push it.",
                    "Closer: if the stack is empty or the popped opener is not its partner, return <code>False</code>.",
                    "After the scan, return <code>not stack</code>, so leftover openers mean invalid.",
                ],
                "why": [
                    "Brackets must close in reverse order of opening, which is last-in-first-out, the exact order a stack gives back.",
                    "Each character is pushed or popped at most once: O(n) time, and O(n) space when the string is all openers.",
                ],
                "dry": [
                    "<code>(</code>: push, stack <code>['(']</code>.",
                    "<code>[</code>: push, stack <code>['(', '[']</code>.",
                    "<code>{</code>: push, stack <code>['(', '[', '{']</code>.",
                    "<code>}</code>: pop <code>{</code>, which matches; stack <code>['(', '[']</code>.",
                    "<code>]</code>: pop <code>[</code>, which matches; stack <code>['(']</code>.",
                    "<code>)</code>: pop <code>(</code>, which matches; the stack is empty.",
                    "<code>[</code>: push, stack <code>['[']</code>.",
                    "End of string with <code>['[']</code> still waiting, so the result is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ stack using queues
    "stack-using-queues": {
        "example": {"setup": "s = MyStack()\nfor x in (1, 2, 3):\n    s.push(x)",
                    "call": "[s.top(), s.pop(), s.pop(), s.empty()]", "expect": "[3, 3, 2, False]"},
        "approaches": {
            "Two queues, pay on pop": {
                "idea": [
                    "A queue only hands out its <em>oldest</em> element, but a stack must hand out the <em>newest</em>, which sits at the back.",
                    "To reach the back, move every element in front of it into a second queue, keeping their order.",
                    "Pushing stays a plain append, so all the work is paid when popping.",
                ],
                "steps": [
                    "<code>push(x)</code>: append <code>x</code> to the main queue <code>q</code>.",
                    "<code>pop()</code>: move all but the last element from <code>q</code> to <code>helper</code>, then take the last one.",
                    "Swap the names of <code>q</code> and <code>helper</code>, so the survivors are the main queue again.",
                    "<code>top()</code>: pop the element and push it straight back.",
                    "<code>empty()</code>: the stack is empty when <code>q</code> is.",
                ],
                "why": [
                    "Moving elements front to back preserves their relative order, so after the swap the queue holds the same stack minus its top.",
                    "<code>push</code> is O(1); <code>pop</code> and <code>top</code> move n - 1 elements, so they are O(n). Space is O(n) across both queues.",
                ],
                "dry": [
                    "After the setup <code>q = [1, 2, 3]</code> (front on the left) and <code>helper = []</code>.",
                    "<code>top()</code> calls <code>pop()</code>: 1 and 2 move to <code>helper</code>, 3 is taken, and after the swap <code>q = [1, 2]</code>.",
                    "<code>top()</code> then pushes 3 back, so <code>q = [1, 2, 3]</code>, and it returns <strong>3</strong>.",
                    "<code>pop()</code>: move 1 and 2 again, take 3, swap; <code>q = [1, 2]</code>, returns <strong>3</strong>.",
                    "<code>pop()</code>: move 1, take 2, swap; <code>q = [1]</code>, returns <strong>2</strong>.",
                    "<code>empty()</code>: <code>q</code> still holds 1, so it returns <strong>False</strong>.",
                ],
            },
            "One queue, rotate on push": {
                "idea": [
                    "Keep the queue in stack order, newest at the front, so <code>popleft</code> is exactly a stack pop.",
                    "A new element joins at the back; rotating the n - 1 older elements behind it brings it to the front.",
                    "This moves the cost to <code>push</code> and makes every read O(1).",
                ],
                "steps": [
                    "<code>push(x)</code>: append <code>x</code>, then repeat <code>len(q) - 1</code> times: <code>q.append(q.popleft())</code>.",
                    "<code>pop()</code>: <code>q.popleft()</code> returns the newest element.",
                    "<code>top()</code>: read <code>q[0]</code>.",
                    "<code>empty()</code>: <code>not q</code>.",
                ],
                "why": [
                    "Invariant: the queue from front to back lists the stack from top to bottom. Each rotation keeps the older elements in order and puts them behind the new one.",
                    "<code>push</code> rotates n - 1 elements, which is O(n); <code>pop</code>, <code>top</code> and <code>empty</code> are O(1). Space is O(n).",
                ],
                "dry": [
                    "<code>push(1)</code>: <code>q = [1]</code>; nothing to rotate.",
                    "<code>push(2)</code>: <code>[1, 2]</code>, rotate once to give <code>[2, 1]</code>.",
                    "<code>push(3)</code>: <code>[2, 1, 3]</code>, rotate twice: <code>[1, 3, 2]</code>, then <code>[3, 2, 1]</code>.",
                    "<code>top()</code> reads the front, <strong>3</strong>.",
                    "<code>pop()</code> removes the front, <strong>3</strong>, leaving <code>[2, 1]</code>.",
                    "<code>pop()</code> removes <strong>2</strong>, leaving <code>[1]</code>.",
                    "<code>empty()</code> is <strong>False</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ queue using stacks
    "queue-using-stacks": {
        "example": {"setup": "q = MyQueue()\nfor x in (1, 2, 3):\n    q.push(x)",
                    "call": "[q.pop(), q.push(4), q.pop(), q.pop(), q.pop(), q.empty()]",
                    "expect": "[1, None, 2, 3, 4, True]"},
        "approaches": {
            "Move everything on every push": {
                "idea": [
                    "A stack gives back its newest element, but a queue must give back its oldest.",
                    "If the stack is kept <em>upside down</em> (oldest on top), pop and peek become ordinary stack operations.",
                    "Keeping it that way means a new element has to go to the <em>bottom</em>, so everything above it is poured out and back.",
                ],
                "steps": [
                    "<code>push(x)</code>: pop everything from <code>s</code> onto <code>helper</code>, push <code>x</code> onto the now empty <code>s</code>, then pour <code>helper</code> back.",
                    "<code>pop()</code>: <code>s.pop()</code> returns the oldest element.",
                    "<code>peek()</code>: <code>s[-1]</code>.",
                    "<code>empty()</code>: <code>not s</code>.",
                ],
                "why": [
                    "Pouring a stack onto another reverses it, and pouring back reverses it again, so the old elements return in their original order above the new one.",
                    "Every push moves all n elements twice: O(n) per push, O(1) per pop. Space is O(n).",
                ],
                "dry": [
                    "<code>push(1)</code>: <code>s = [1]</code> (the top is on the right).",
                    "<code>push(2)</code>: pour 1 into <code>helper</code>, push 2, pour back: <code>s = [2, 1]</code>, so the oldest (1) is on top.",
                    "<code>push(3)</code>: pour to <code>helper = [1, 2]</code>, push 3, pour back: <code>s = [3, 2, 1]</code>.",
                    "<code>pop()</code> returns the top, <strong>1</strong>; <code>s = [3, 2]</code>.",
                    "<code>push(4)</code> returns <code>None</code>: pour to <code>helper = [2, 3]</code>, push 4, pour back: <code>s = [4, 3, 2]</code>.",
                    "The next three pops return <strong>2</strong>, <strong>3</strong>, <strong>4</strong> in arrival order, and <code>empty()</code> is <strong>True</strong>.",
                ],
            },
            "Input and output stacks, transfer lazily": {
                "idea": [
                    "Use two stacks: <code>inbox</code> collects new elements and <code>outbox</code> hands out old ones.",
                    "Pouring <code>inbox</code> into <code>outbox</code> reverses it, so the oldest element ends up on top of <code>outbox</code>.",
                    "Only pour when <code>outbox</code> is empty; otherwise its top is already the oldest element in the queue.",
                ],
                "steps": [
                    "<code>push(x)</code>: <code>inbox.append(x)</code>.",
                    "<code>_shift()</code>: if <code>outbox</code> is empty, pop everything from <code>inbox</code> onto <code>outbox</code>.",
                    "<code>pop()</code> and <code>peek()</code>: call <code>_shift()</code>, then pop or read the top of <code>outbox</code>.",
                    "<code>empty()</code>: both stacks are empty.",
                ],
                "why": [
                    "Everything in <code>outbox</code> arrived before everything in <code>inbox</code>, so while <code>outbox</code> has elements its top is the queue's front.",
                    "One transfer can move n elements, but each element is moved from <code>inbox</code> to <code>outbox</code> once in its life, so n operations cost O(n) in total: amortised O(1).",
                    "Space is O(n) for the elements held across the two stacks.",
                ],
                "dry": [
                    "After the setup <code>inbox = [1, 2, 3]</code> and <code>outbox = []</code>.",
                    "<code>pop()</code>: <code>outbox</code> is empty, so pour; it becomes <code>[3, 2, 1]</code> with 1 on top. Pop <strong>1</strong>.",
                    "<code>push(4)</code> returns <code>None</code>; <code>inbox = [4]</code>, while <code>outbox = [3, 2]</code> is untouched.",
                    "<code>pop()</code>: <code>outbox</code> is not empty, so there is no transfer; pop <strong>2</strong>.",
                    "<code>pop()</code>: pop <strong>3</strong>; <code>outbox</code> is now empty.",
                    "<code>pop()</code>: <code>outbox</code> is empty, so pour <code>[4]</code> across and pop <strong>4</strong>.",
                    "<code>empty()</code>: both stacks are empty, <strong>True</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ min stack
    "min-stack": {
        "example": {"setup": "m = MinStack()\nfor v in (5, 3, 7, 3, 1):\n    m.push(v)",
                    "call": "[m.getMin(), m.pop(), m.getMin(), m.pop(), m.getMin(), m.top()]",
                    "expect": "[1, None, 3, None, 3, 7]"},
        "approaches": {
            "Scan for the minimum": {
                "idea": [
                    "Store the values in a plain list and compute the minimum only when asked.",
                    "It is the obvious baseline, and it shows why the real problem asks for something smarter: <code>getMin</code> must be O(1).",
                ],
                "steps": [
                    "<code>push</code>, <code>pop</code> and <code>top</code> work on the list directly.",
                    "<code>getMin()</code> returns <code>min(self.s)</code>, a full scan.",
                ],
                "why": [
                    "<code>min</code> over the current contents is correct by definition.",
                    "Every <code>getMin</code> costs O(n), which fails the O(1) requirement; the other operations are O(1). Space is O(n).",
                ],
                "dry": [
                    "After the pushes <code>s = [5, 3, 7, 3, 1]</code>.",
                    "<code>getMin()</code> scans all five values and returns <strong>1</strong>.",
                    "<code>pop()</code> removes 1, so <code>s = [5, 3, 7, 3]</code>.",
                    "<code>getMin()</code> scans again: <strong>3</strong>.",
                    "<code>pop()</code> removes the second 3, so <code>s = [5, 3, 7]</code>.",
                    "<code>getMin()</code> is still <strong>3</strong>, thanks to the first 3, and <code>top()</code> is <strong>7</strong>.",
                ],
            },
            "Store (value, min so far) pairs": {
                "idea": [
                    "The minimum of a stack only depends on what is below the top, and the part below never changes while the top sits on it.",
                    "So remember, next to each value, the minimum of the stack <em>at the moment it was pushed</em>.",
                    "Popping removes the pair and exposes the pair below, whose stored minimum is exactly the minimum of what remains.",
                ],
                "steps": [
                    "<code>push(val)</code>: append <code>(val, min(val, previous min))</code>, or <code>(val, val)</code> if the stack is empty.",
                    "<code>pop()</code>: pop the pair.",
                    "<code>top()</code>: <code>s[-1][0]</code>; <code>getMin()</code>: <code>s[-1][1]</code>.",
                ],
                "why": [
                    "By induction, the second number in the top pair is the minimum of all values in the stack, and every operation preserves that.",
                    "Every operation is O(1). It uses O(n) space, storing two numbers per element.",
                ],
                "dry": [
                    "<code>push(5)</code> gives the pair (5, 5).",
                    "<code>push(3)</code>: min(3, 5) = 3, pair (3, 3).",
                    "<code>push(7)</code>: min(7, 3) = 3, pair (7, 3).",
                    "<code>push(3)</code>: pair (3, 3); <code>push(1)</code>: pair (1, 1).",
                    "<code>getMin()</code> reads the top pair (1, 1): <strong>1</strong>.",
                    "<code>pop()</code> drops (1, 1); the top is now (3, 3), so <code>getMin()</code> gives <strong>3</strong>.",
                    "<code>pop()</code> drops (3, 3); the top is (7, 3), so <code>getMin()</code> is still <strong>3</strong> and <code>top()</code> is <strong>7</strong>.",
                ],
            },
            "Second stack of minimums, pushed only when needed": {
                "idea": [
                    "Most pushes do not change the minimum, so there is no need to record a minimum for every element.",
                    "Keep a second stack <code>mins</code> holding only the values that were a new minimum (or a tie) when they arrived.",
                    "When such a value is popped from the main stack, pop it from <code>mins</code> too; the top of <code>mins</code> is always the current minimum.",
                ],
                "steps": [
                    "<code>push(val)</code>: push onto <code>s</code>; if <code>mins</code> is empty or <code>val &lt;= mins[-1]</code>, push onto <code>mins</code> too.",
                    "<code>pop()</code>: pop <code>s</code>; if the popped value equals <code>mins[-1]</code>, pop <code>mins</code>.",
                    "<code>top()</code>: <code>s[-1]</code>; <code>getMin()</code>: <code>mins[-1]</code>.",
                ],
                "why": [
                    "<code>mins</code> is non-increasing from bottom to top, and it holds a copy of every value that is a minimum for some prefix of the stack.",
                    "Using <code>&lt;=</code> instead of <code>&lt;</code> matters: duplicate minimums each get their own entry, so popping one copy leaves the other in place.",
                    "All operations are O(1); <code>mins</code> holds at most n values and is often much shorter.",
                ],
                "dry": [
                    "<code>push(5)</code>: <code>mins = [5]</code>. <code>push(3)</code>: 3 ≤ 5, so <code>mins = [5, 3]</code>.",
                    "<code>push(7)</code>: 7 &gt; 3, so <code>mins</code> is unchanged.",
                    "<code>push(3)</code>: 3 ≤ 3, so <code>mins = [5, 3, 3]</code>, a second copy of the tie.",
                    "<code>push(1)</code>: <code>mins = [5, 3, 3, 1]</code>; <code>getMin()</code> is <strong>1</strong>.",
                    "<code>pop()</code> removes 1, which equals the top of <code>mins</code>, so <code>mins = [5, 3, 3]</code> and <code>getMin()</code> is <strong>3</strong>.",
                    "<code>pop()</code> removes the second 3, which also matches, so <code>mins = [5, 3]</code> and <code>getMin()</code> is still <strong>3</strong>.",
                    "With <code>&lt;</code> instead, <code>mins</code> would have been <code>[5, 3, 1]</code>, and this second pop would have wrongly left 5 as the minimum.",
                    "<code>top()</code> is <strong>7</strong>.",
                ],
            },
            "One stack of differences from the minimum": {
                "idea": [
                    "Store <code>val - min</code> instead of <code>val</code>, and keep the current minimum in one variable.",
                    "A <em>negative</em> stored difference can only happen when the value was below the old minimum, so it marks a push that set a new minimum.",
                    "That negative number also remembers the old minimum: new min - diff = old min, so popping it restores the previous minimum with arithmetic.",
                ],
                "steps": [
                    "First push: store 0 and set <code>min = val</code>.",
                    "Later pushes: store <code>val - min</code>; if <code>val &lt; min</code>, set <code>min = val</code>.",
                    "<code>pop()</code>: pop the difference; if it is negative, restore <code>min -= diff</code>.",
                    "<code>top()</code>: a negative difference means the top value is <code>min</code> itself, otherwise it is <code>min + diff</code>.",
                    "<code>getMin()</code>: return <code>min</code>.",
                ],
                "why": [
                    "When <code>val &lt; min</code>, the stored <code>diff = val - old</code> is negative and <code>val</code> becomes the new min, so <code>old = new - diff</code> is recoverable.",
                    "Non-negative differences never changed the minimum, so popping them leaves <code>min</code> alone.",
                    "Every operation is O(1) and only one number is stored per element. In fixed-width languages the difference can overflow; Python integers cannot.",
                ],
                "dry": [
                    "<code>push(5)</code>: stack <code>[0]</code>, <code>min = 5</code>.",
                    "<code>push(3)</code>: 3 - 5 = -2 is stored and <code>min = 3</code>. <code>push(7)</code>: 7 - 3 = 4 is stored.",
                    "<code>push(3)</code>: 3 - 3 = 0 is stored and the minimum stays 3.",
                    "<code>push(1)</code>: 1 - 3 = -2 is stored, <code>min = 1</code>; the stack is <code>[0, -2, 4, 0, -2]</code>.",
                    "<code>getMin()</code>: <strong>1</strong>.",
                    "<code>pop()</code>: diff -2 is negative, so <code>min = 1 - (-2) = 3</code>; <code>getMin()</code> is <strong>3</strong>.",
                    "<code>pop()</code>: diff 0 is not negative, so <code>min</code> stays <strong>3</strong>.",
                    "<code>top()</code>: the top diff is 4, so the value is 3 + 4 = <strong>7</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ evaluate RPN
    "evaluate-rpn": {
        "example": {"call": 'eval_rpn(["5", "1", "2", "+", "4", "*", "+", "3", "-"])', "expect": "14"},
        "approaches": {
            "Operand stack": {
                "idea": [
                    "In postfix notation every operator comes right after its two operands, so the operands it needs are always the two most recent values.",
                    "Keep values on a stack; an operator pops two, combines them and pushes the result, which can be an operand for a later operator.",
                    "No precedence rules or parentheses are needed, because the order of the tokens already encodes them.",
                ],
                "steps": [
                    "Scan the tokens left to right.",
                    "A number: push <code>int(tok)</code>.",
                    "An operator: pop <code>b</code> (the right operand, on top), then <code>a</code>, and push <code>a op b</code>.",
                    "Division uses <code>int(a / b)</code> so it truncates toward zero, as the problem requires; <code>//</code> would round down instead.",
                    "At the end the stack holds exactly one value, the answer.",
                ],
                "why": [
                    "Each operator's result replaces its two operands, so the stack always holds the values of the sub-expressions not yet consumed.",
                    "Popping order matters for <code>-</code> and <code>/</code>: the right operand is on top.",
                    "Each token is pushed or popped a constant number of times: O(n) time and O(n) space.",
                ],
                "dry": [
                    "<code>5</code>, <code>1</code>, <code>2</code>: stack <code>[5, 1, 2]</code>.",
                    "<code>+</code>: pop 2 and 1, push 1 + 2 = 3: <code>[5, 3]</code>.",
                    "<code>4</code>: <code>[5, 3, 4]</code>.",
                    "<code>*</code>: pop 4 and 3, push 3 × 4 = 12: <code>[5, 12]</code>.",
                    "<code>+</code>: pop 12 and 5, push 17: <code>[17]</code>.",
                    "<code>3</code>: <code>[17, 3]</code>.",
                    "<code>-</code>: pop b = 3, a = 17, push 17 - 3 = 14. The answer is <strong>14</strong>, which is 5 + (1 + 2) × 4 - 3.",
                ],
            },
            "Recursion from the end": {
                "idea": [
                    "Read backwards, a postfix expression is a tree: the last token is the root, the expression just before it is its right subtree, and the one before that is its left.",
                    "A recursive function that consumes tokens from the end can rebuild that tree as it evaluates.",
                    "The call stack plays the role of the explicit stack.",
                ],
                "steps": [
                    "Copy the tokens so popping does not change the caller's list.",
                    "<code>ev()</code> pops the last token; if it is a number, return it.",
                    "If it is an operator, evaluate the right operand first (<code>b = ev()</code>), then the left (<code>a = ev()</code>), and combine them.",
                    "Return <code>ev()</code> for the whole list.",
                ],
                "why": [
                    "The right operand's tokens sit directly before the operator, so the first recursive call consumes exactly them, and the second call gets the left operand.",
                    "Each token is popped once: O(n) time, and O(n) recursion depth for a lopsided expression.",
                ],
                "dry": [
                    "<code>ev()</code> pops <code>-</code> and needs b then a.",
                    "b: pops <code>3</code>, so b = 3.",
                    "a: pops <code>+</code>; its b pops <code>*</code>, whose b is <code>4</code> and whose a pops another <code>+</code>.",
                    "That inner <code>+</code> pops <code>2</code> (b) and <code>1</code> (a) and returns 3, so <code>*</code> returns 3 × 4 = 12.",
                    "Back in the outer <code>+</code>: b = 12, and its a pops <code>5</code>, so it returns 17.",
                    "Finally <code>-</code> returns 17 - 3 = <strong>14</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ asteroid collision
    "asteroid-collision": {
        "example": {"call": "asteroid_collision([5, 10, -5, -15, 3, -3, 8])", "expect": "[-15, 8]"},
        "approaches": {
            "Resolve one collision at a time": {
                "idea": [
                    "A collision can only happen between a right-mover directly followed by a left-mover: <code>a[i] &gt; 0 &gt; a[i + 1]</code>.",
                    "Simulate literally: find such a pair, blow up the smaller (or both if equal), and look again from the start.",
                    "When no such pair is left, nothing will ever collide again.",
                ],
                "steps": [
                    "Copy the input, because elements are deleted.",
                    "Scan for the first <code>i</code> with <code>a[i] &gt; 0 &gt; a[i + 1]</code>.",
                    "Delete the smaller of the two by absolute value, or both if they are the same size, and restart the scan.",
                    "Stop when a full scan finds no such pair.",
                ],
                "why": [
                    "The final state does not depend on the order collisions are resolved in, so resolving any adjacent pair is safe.",
                    "Each collision deletes at least one asteroid, so there are at most n rounds, each an O(n) scan and delete: O(n²) time, O(n) space for the copy.",
                ],
                "dry": [
                    "<code>[5, 10, -5, -15, 3, -3, 8]</code>: the first pair is 10 and -5; 10 is bigger, so -5 explodes: <code>[5, 10, -15, 3, -3, 8]</code>.",
                    "Restart: 10 meets -15, and 10 explodes: <code>[5, -15, 3, -3, 8]</code>.",
                    "Restart: 5 meets -15, and 5 explodes: <code>[-15, 3, -3, 8]</code>.",
                    "Restart: -15 moves left with nothing ahead of it; next, 3 meets -3, a tie, so both go: <code>[-15, 8]</code>.",
                    "Restart: no right-mover is followed by a left-mover, so the loop ends with <strong>[-15, 8]</strong>.",
                ],
            },
            "Stack of survivors": {
                "idea": [
                    "Process asteroids left to right, keeping a stack of the ones that have survived so far.",
                    "Only a left-mover can hit something, and the first thing it can hit is the right-mover on <em>top</em> of the stack.",
                    "It keeps destroying smaller right-movers on top until it meets a bigger one (it dies), an equal one (both die), or runs out of right-movers (it survives).",
                ],
                "steps": [
                    "For each asteroid <code>a</code>, set <code>alive = True</code>.",
                    "While <code>a</code> moves left and the top of the stack moves right: if the top is smaller, pop it and keep going.",
                    "If the top is the same size, pop it and set <code>alive = False</code>; if it is bigger, just set <code>alive = False</code>.",
                    "If <code>a</code> is still alive, push it.",
                    "Return the stack.",
                ],
                "why": [
                    "Survivors on the stack never collide with each other: any right-mover sits above every left-mover it could have met.",
                    "A left-mover at the bottom of the stack is safe forever, because nothing to its left moves right.",
                    "Each asteroid is pushed once and popped at most once: O(n) time, O(n) space.",
                ],
                "dry": [
                    "5: push, stack <code>[5]</code>. 10: push, stack <code>[5, 10]</code>.",
                    "-5: the top 10 moves right and is bigger, so -5 dies; the stack stays <code>[5, 10]</code>.",
                    "-15: the top 10 is smaller, pop; the top 5 is smaller, pop; the stack is empty, so -15 survives: <code>[-15]</code>.",
                    "3: push, <code>[-15, 3]</code>.",
                    "-3: the top 3 is the same size, so pop it and -3 dies too: <code>[-15]</code>.",
                    "8: push, <code>[-15, 8]</code>. The answer is <strong>[-15, 8]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ daily temperatures
    "daily-temperatures": {
        "example": {"call": "daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73])", "expect": "[1, 1, 4, 2, 1, 1, 0, 0]"},
        "approaches": {
            "Scan forward from each day": {
                "idea": [
                    "Answer each day independently: walk forward from it until a strictly warmer day appears.",
                    "The distance walked is the answer, and if the walk falls off the end, the answer stays 0.",
                ],
                "steps": [
                    "Create <code>out</code> filled with zeros.",
                    "For each day <code>i</code> with temperature <code>t</code>, try <code>j = i + 1, i + 2, ...</code>.",
                    "At the first <code>temps[j] &gt; t</code>, set <code>out[i] = j - i</code> and stop.",
                ],
                "why": [
                    "It checks exactly the definition: the first later day that is warmer.",
                    "A strictly decreasing list makes every scan run to the end: O(n²) time. Extra space is O(1) beyond the output.",
                ],
                "dry": [
                    "Day 0 (73): day 1 is 74, warmer, so <code>out[0] = 1</code>.",
                    "Day 1 (74): day 2 is 75, warmer, so <code>out[1] = 1</code>.",
                    "Day 2 (75): 71, 69 and 72 are all colder, then 76 at day 6 is warmer, so <code>out[2] = 6 - 2 = 4</code>.",
                    "Day 3 (71): 69 is colder, 72 at day 5 is warmer, so <code>out[3] = 2</code>.",
                    "Day 4 (69): 72 is warmer, so <code>out[4] = 1</code>. Day 5 (72): 76 is warmer, so <code>out[5] = 1</code>.",
                    "Day 6 (76): only 73 follows, so it stays 0. Day 7 has nothing after it, 0.",
                    "The result is <strong>[1, 1, 4, 2, 1, 1, 0, 0]</strong>.",
                ],
            },
            "Monotonic decreasing stack of waiting days": {
                "idea": [
                    "Flip the question: instead of each day searching forward, let each new day <em>answer</em> the earlier days that were waiting for it.",
                    "Days still waiting for a warmer day are kept on a stack, and their temperatures decrease from bottom to top.",
                    "A new warmer day pops every colder waiting day off the top, since it is the first warmer day for all of them, then waits itself.",
                ],
                "steps": [
                    "Keep <code>stack</code> of indices of days without an answer yet.",
                    "For day <code>i</code> with temperature <code>t</code>: while the day on top is colder than <code>t</code>, pop it as <code>j</code> and set <code>out[j] = i - j</code>.",
                    "Push <code>i</code>.",
                    "Days left on the stack at the end never warmed up, so their 0 stays.",
                ],
                "why": [
                    "When a day is popped, the current day is the first warmer one, because any warmer day in between would already have popped it.",
                    "The stack stays decreasing, because a day is pushed only after everything colder than it has been popped.",
                    "Each index is pushed and popped at most once: O(n) time, O(n) space for the stack.",
                ],
                "dry": [
                    "i=0 (73): the stack is empty, push. Stack (as temperatures): [73].",
                    "i=1 (74): 73 &lt; 74, so pop day 0 and set <code>out[0] = 1</code>. Push: [74].",
                    "i=2 (75): pop day 1 and set <code>out[1] = 1</code>. Push: [75].",
                    "i=3 (71) and i=4 (69): both are colder than the top, so both wait: [75, 71, 69].",
                    "i=5 (72): pop day 4 (69), <code>out[4] = 1</code>; pop day 3 (71), <code>out[3] = 2</code>; 75 is warmer, so stop. Push: [75, 72].",
                    "i=6 (76): pop day 5 (72), <code>out[5] = 1</code>; pop day 2 (75), <code>out[2] = 4</code>. Push: [76].",
                    "i=7 (73): colder than 76, so it waits: [76, 73]. Days 6 and 7 keep 0.",
                    "The result is <strong>[1, 1, 4, 2, 1, 1, 0, 0]</strong>.",
                ],
            },
            "Right to left, jump along known answers": {
                "idea": [
                    "Fill answers from the last day backwards, so every later day's answer is already known.",
                    "To find day i's warmer day, start at the next day j. If j is not warmer, no day between j and j's own warmer day can be warmer than j either, let alone day i.",
                    "So jump straight to <code>j + out[j]</code>; the answer array works as a set of shortcuts, with no extra stack.",
                ],
                "steps": [
                    "Loop <code>i</code> from <code>n - 2</code> down to 0 (the last day's answer is always 0).",
                    "Start at <code>j = i + 1</code>.",
                    "While <code>temps[j] &lt;= temps[i]</code>: if <code>out[j] == 0</code>, nothing warmer exists, so give up; otherwise jump <code>j += out[j]</code>.",
                    "If a warmer <code>j</code> was found, set <code>out[i] = j - i</code>.",
                ],
                "why": [
                    "Every skipped day is at most <code>temps[j]</code>, which is at most <code>temps[i]</code>, so none of them could be the answer.",
                    "The jumps follow the same chains a monotonic stack would pop, so the total work is amortised O(n). Extra space is O(1) beyond the output.",
                ],
                "dry": [
                    "i=6 (76): j=7 (73) is not warmer and <code>out[7] = 0</code>, so day 6 stays 0.",
                    "i=5 (72): j=6 (76) is warmer, so <code>out[5] = 1</code>.",
                    "i=4 (69): j=5 (72) is warmer, so <code>out[4] = 1</code>.",
                    "i=3 (71): j=4 (69) is not warmer; jump by <code>out[4] = 1</code> to j=5 (72), which is warmer, so <code>out[3] = 2</code>.",
                    "i=2 (75): j=3 (71), jump by 2 to j=5 (72), jump by 1 to j=6 (76), which is warmer, so <code>out[2] = 4</code>. Two jumps skipped days 4 and 5 entirely.",
                    "i=1 (74): j=2 (75) is warmer, so <code>out[1] = 1</code>. i=0 (73): j=1 (74), so <code>out[0] = 1</code>.",
                    "The result is <strong>[1, 1, 4, 2, 1, 1, 0, 0]</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ online stock span
    "online-stock-span": {
        "example": {"setup": "s = StockSpanner()", "call": "[s.next(p) for p in [100, 80, 60, 70, 60, 75, 85]]",
                    "expect": "[1, 1, 1, 2, 1, 4, 6]"},
        "approaches": {
            "Scan back through history": {
                "idea": [
                    "The span is how many consecutive days, counting back from today, had a price no higher than today's.",
                    "Store every price and literally walk backwards until a higher price stops the count.",
                ],
                "steps": [
                    "Append today's price to <code>prices</code>.",
                    "Walk <code>reversed(prices)</code>, counting days, and stop at the first price above today's.",
                    "Return the count, which always includes today.",
                ],
                "why": [
                    "It is a direct reading of the definition.",
                    "In a steadily rising market every call walks the whole history: O(n) per call and O(n²) overall. Space is O(n).",
                ],
                "dry": [
                    "100: only itself, span <strong>1</strong>. 80: 100 &gt; 80 stops it, span <strong>1</strong>. 60: span <strong>1</strong>.",
                    "70: counts 70 and 60, then 80 &gt; 70 stops it, span <strong>2</strong>.",
                    "60: counts itself, then 70 &gt; 60 stops it, span <strong>1</strong>.",
                    "75: counts 75, 60, 70, 60, then 80 &gt; 75 stops it, span <strong>4</strong>.",
                    "85: counts 85, 75, 60, 70, 60, 80, then 100 &gt; 85 stops it, span <strong>6</strong>.",
                ],
            },
            "Monotonic stack of (price, span)": {
                "idea": [
                    "Once today's price is at least an earlier price, that earlier day can never stop a future walk before today does.",
                    "So collapse such days into today: keep <code>(price, span)</code> pairs whose prices strictly decrease, and fold each covered day's span into today's.",
                    "A future day that reaches today will also cover everything today absorbed, so the absorbed days are never needed again.",
                ],
                "steps": [
                    "Start with <code>span = 1</code> for today.",
                    "While the top pair's price is ≤ today's price, pop it and add its span to today's.",
                    "Push <code>(price, span)</code> and return <code>span</code>.",
                ],
                "why": [
                    "Each stored pair stands for a block of consecutive days ending at that day, all priced at or below it, so adding spans counts exactly the covered days.",
                    "Every price is pushed once and popped at most once: amortised O(1) per call. Space is O(n) in a falling market.",
                ],
                "dry": [
                    "100: the stack is empty, push (100, 1), span <strong>1</strong>.",
                    "80: 100 is higher, push (80, 1), span <strong>1</strong>. 60: push (60, 1), span <strong>1</strong>.",
                    "70: pop (60, 1), so span = 2; 80 is higher, stop. Push (70, 2), span <strong>2</strong>.",
                    "60: 70 is higher, push (60, 1), span <strong>1</strong>.",
                    "75: pop (60, 1) for 2, pop (70, 2) for 4; 80 is higher. Push (75, 4), span <strong>4</strong>.",
                    "85: pop (75, 4) for 5, pop (80, 1) for 6; 100 is higher. Push (85, 6), span <strong>6</strong>.",
                    "The stack ends as <code>[(100, 1), (85, 6)]</code>: two pairs stand for all seven days.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ car fleet
    "car-fleet": {
        "example": {"call": "car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3])", "expect": "3"},
        "approaches": {
            "Sort by position, stack of fleet arrival times": {
                "idea": [
                    "Cars cannot pass, so whether a car joins a fleet depends only on the cars <em>ahead</em> of it.",
                    "Work from the car closest to the target backwards, and compute each car's solo arrival time <code>(target - position) / speed</code>.",
                    "If a car would arrive no later than the fleet directly ahead, it catches up and merges; otherwise it arrives later and leads a new fleet.",
                ],
                "steps": [
                    "Pair positions with speeds and sort by position, largest first.",
                    "For each car, compute <code>t = (target - p) / s</code>.",
                    "If the stack is empty or <code>t &gt; stack[-1]</code>, push <code>t</code> as a new fleet; otherwise do nothing, because it merges.",
                    "Return the stack's length.",
                ],
                "why": [
                    "A car that merges is slowed to the fleet's arrival time, so the fleet's time on the stack stays correct for the cars behind.",
                    "Arrival times on the stack strictly increase from bottom to top, one per fleet.",
                    "Sorting costs O(n log n); the scan is O(n), with O(n) space.",
                ],
                "dry": [
                    "Sorted by position: (10, 2), (8, 4), (5, 1), (3, 3), (0, 1).",
                    "Car at 10: t = 2/2 = 1.0, the first fleet, so the stack is [1.0].",
                    "Car at 8: t = 4/4 = 1.0, not later than 1.0, so it catches up and merges.",
                    "Car at 5: t = 7/1 = 7.0 &gt; 1.0, a new fleet: [1.0, 7.0].",
                    "Car at 3: t = 9/3 = 3.0, earlier than 7.0, so it catches the car from 5 and merges.",
                    "Car at 0: t = 12/1 = 12.0 &gt; 7.0, a new fleet: [1.0, 7.0, 12.0].",
                    "Three times on the stack means <strong>3</strong> fleets.",
                ],
            },
            "Sort, track only the slowest fleet ahead": {
                "idea": [
                    "In the stack version only the top of the stack is ever compared.",
                    "So a single number, the arrival time of the most recent fleet, is enough, plus a counter.",
                ],
                "steps": [
                    "Sort by position, largest first; <code>fleets = 0</code> and <code>slowest = 0.0</code>.",
                    "For each car compute <code>t</code>; if <code>t &gt; slowest</code>, count a new fleet and set <code>slowest = t</code>.",
                    "Return <code>fleets</code>.",
                ],
                "why": [
                    "<code>slowest</code> equals the top of the stack in the previous approach, so the decisions are identical.",
                    "It takes O(n log n) for the sort and O(1) extra space beyond it.",
                ],
                "dry": [
                    "Car at 10: t = 1.0 &gt; 0.0, so fleets = 1 and slowest = 1.0.",
                    "Car at 8: t = 1.0 is not &gt; 1.0, so it merges.",
                    "Car at 5: t = 7.0, so fleets = 2 and slowest = 7.0.",
                    "Car at 3: t = 3.0 is not &gt; 7.0, so it merges.",
                    "Car at 0: t = 12.0, so fleets = <strong>3</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ simplify path
    "simplify-path": {
        "example": {"call": 'simplify_path("/home/./user//docs/../.../")', "expect": '"/home/user/..."'},
        "approaches": {
            "Split on '/', stack of directory names": {
                "idea": [
                    "A path is a walk through directories: a name goes one level down, <code>..</code> goes one level up, and <code>.</code> stays put.",
                    "The current location is a stack of names, where going down pushes and going up pops.",
                    "Splitting on <code>/</code> handles repeated slashes for free, since they turn into empty strings that we skip.",
                ],
                "steps": [
                    "Split the path on <code>/</code>.",
                    "Skip empty parts and <code>.</code>.",
                    "For <code>..</code>, pop if the stack is not empty; going up from the root stays at the root.",
                    "Push anything else, including names made of dots such as <code>...</code>.",
                    "Return <code>\"/\" + \"/\".join(stack)</code>.",
                ],
                "why": [
                    "The stack always equals the canonical path of the directory reached so far.",
                    "Each part is handled once: O(n) time and O(n) space.",
                ],
                "dry": [
                    "The split gives <code>['', 'home', '.', 'user', '', 'docs', '..', '...', '']</code>.",
                    "<code>''</code>: skip. <code>home</code>: push, giving <code>[home]</code>.",
                    "<code>.</code>: skip. <code>user</code>: push, giving <code>[home, user]</code>.",
                    "<code>''</code> (from <code>//</code>): skip. <code>docs</code>: push, giving <code>[home, user, docs]</code>.",
                    "<code>..</code>: pop <code>docs</code>, giving <code>[home, user]</code>.",
                    "<code>...</code>: a real directory name, push, giving <code>[home, user, ...]</code>. The trailing <code>''</code> is skipped.",
                    "Join: <strong>\"/home/user/...\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ decode string
    "decode-string": {
        "example": {"call": 'decode_string("2[a3[bc]]d")', "expect": '"abcbcbcabcbcbcd"'},
        "approaches": {
            "Stack of (outer string, repeat count)": {
                "idea": [
                    "Brackets nest, so when an inner <code>[</code> opens we have to pause the outer string and come back to it later, which is a stack.",
                    "On <code>[</code>, save the text built so far and the repeat count, then start building the inner text from scratch.",
                    "On <code>]</code>, the inner text is complete: restore the outer text and append the inner text repeated k times.",
                ],
                "steps": [
                    "Keep <code>cur</code> (the text at this level) and <code>num</code> (a repeat count being read).",
                    "Digit: <code>num = num * 10 + digit</code>, so counts like <code>10</code> work.",
                    "<code>[</code>: push <code>(cur, num)</code> and reset both.",
                    "<code>]</code>: pop <code>(outer, k)</code> and set <code>cur = outer + cur * k</code>.",
                    "Letter: append it to <code>cur</code>. At the end, return <code>cur</code>.",
                ],
                "why": [
                    "The stack holds one saved prefix per open bracket, so each <code>]</code> closes the innermost group first, exactly as nesting requires.",
                    "The work is proportional to the length of the output, which can be exponential in the input (as in <code>9[9[9[a]]]</code>), and space is the same.",
                ],
                "dry": [
                    "<code>2</code>: num = 2. <code>[</code>: push <code>(\"\", 2)</code>, then cur = \"\".",
                    "<code>a</code>: cur = \"a\". <code>3</code>: num = 3.",
                    "<code>[</code>: push <code>(\"a\", 3)</code>, then cur = \"\".",
                    "<code>b</code>, <code>c</code>: cur = \"bc\".",
                    "<code>]</code>: pop <code>(\"a\", 3)</code>, so cur = \"a\" + \"bc\" × 3 = \"abcbcbc\".",
                    "<code>]</code>: pop <code>(\"\", 2)</code>, so cur = \"abcbcbc\" × 2 = \"abcbcbcabcbcbc\".",
                    "<code>d</code>: append, giving <strong>\"abcbcbcabcbcbcd\"</strong>.",
                ],
            },
            "Recursive descent": {
                "idea": [
                    "The encoding is a small grammar: a sequence of letters and groups <code>k[...]</code>, where a group's inside is itself a sequence.",
                    "Write one function that decodes a sequence starting at position i and stops at a <code>]</code> or the end.",
                    "Each group calls the same function for its inside, so nesting turns into recursion.",
                ],
                "steps": [
                    "<code>parse(i)</code> collects pieces in <code>out</code> and reads a repeat count in <code>num</code>.",
                    "On a digit, extend <code>num</code>. On <code>[</code>, call <code>parse(i + 1)</code> for the inside, append <code>inner * num</code>, reset <code>num</code>, and skip the closing <code>]</code>.",
                    "On a letter, append it.",
                    "Stop at <code>]</code> or the end and return <code>(\"\".join(out), i)</code>, so the caller knows where to continue.",
                ],
                "why": [
                    "Each call handles exactly one bracket level, so the recursion depth equals the nesting depth.",
                    "Every input character is read once, and building the output costs O(output) time and space.",
                ],
                "dry": [
                    "<code>parse(0)</code>: reads <code>2</code> (num = 2), then <code>[</code> at index 1, so it calls <code>parse(2)</code>.",
                    "<code>parse(2)</code>: appends <code>a</code>, reads <code>3</code>, then <code>[</code> at index 4, so it calls <code>parse(5)</code>.",
                    "<code>parse(5)</code>: appends <code>b</code> and <code>c</code>, meets <code>]</code> at index 7, and returns <code>(\"bc\", 7)</code>.",
                    "Back in <code>parse(2)</code>: it appends \"bc\" × 3, skips to index 8, meets <code>]</code>, and returns <code>(\"abcbcbc\", 8)</code>.",
                    "Back in <code>parse(0)</code>: it appends \"abcbcbc\" × 2, skips to index 9, then appends <code>d</code>.",
                    "The result is <strong>\"abcbcbcabcbcbcd\"</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ max frequency stack
    "maximum-frequency-stack": {
        "example": {"setup": "fs = FreqStack()\nfor v in [5, 7, 5, 7, 4, 5]:\n    fs.push(v)",
                    "call": "[fs.pop() for _ in range(4)]", "expect": "[5, 7, 5, 4]"},
        "approaches": {
            "List plus counts, scan on pop": {
                "idea": [
                    "Pop has two rules: take the most frequent value, and among ties take the one pushed most recently.",
                    "Keep the push order in a list and a count per value, then search on every pop.",
                ],
                "steps": [
                    "<code>push</code>: append to <code>items</code> and increment <code>freq[val]</code>.",
                    "<code>pop</code>: find the highest count <code>top</code>.",
                    "Scan <code>items</code> from the end for the first value whose count is <code>top</code>; remove it there and decrement its count.",
                ],
                "why": [
                    "Scanning from the end finds the most recently pushed copy among the most frequent values, which is exactly the tie-break rule.",
                    "Each pop is O(n) for the max and the scan; push is O(1). Space is O(n).",
                ],
                "dry": [
                    "After the pushes, items = [5, 7, 5, 7, 4, 5] with counts 5:3, 7:2, 4:1.",
                    "Pop 1: the top count is 3 and the last item 5 has it, so return <strong>5</strong>; 5's count drops to 2.",
                    "Pop 2: the top count is 2 (5 and 7 tie). From the end: 4 has 1, then 7 has 2, so return <strong>7</strong>.",
                    "Pop 3: items = [5, 7, 5, 4] and the top count is 2 (only 5 now). From the end: 4 no, 5 yes, so return <strong>5</strong>.",
                    "Pop 4: all counts are 1, so the last item wins: <strong>4</strong>.",
                ],
            },
            "Heap keyed by (frequency, push time)": {
                "idea": [
                    "Turn both rules into one sort key: higher frequency first, then later push time.",
                    "Every push records the value's <em>new</em> frequency together with a timestamp in a max-heap (stored negated in Python's min-heap).",
                    "Older entries for the same value remain valid: after the top entry is popped, the entry for the previous frequency is still there with its own timestamp.",
                ],
                "steps": [
                    "<code>push</code>: increment the count, advance the clock, push <code>(-freq, -time, val)</code>.",
                    "<code>pop</code>: pop the smallest tuple, which is the highest frequency and then the latest time, and decrement that value's count.",
                ],
                "why": [
                    "Each push of x at frequency f leaves one heap entry, so the entries for x carry frequencies 1..f, matching the levels it reached.",
                    "Push and pop are O(log n) heap operations. Space is O(n).",
                ],
                "dry": [
                    "The pushes create (-1,-1,5), (-1,-2,7), (-2,-3,5), (-2,-4,7), (-1,-5,4), (-3,-6,5).",
                    "Pop: the smallest tuple is (-3,-6,5), giving <strong>5</strong>.",
                    "Pop: (-2,-4,7) beats (-2,-3,5) because -4 &lt; -3 (pushed later), giving <strong>7</strong>.",
                    "Pop: (-2,-3,5) gives <strong>5</strong>.",
                    "Pop: among the frequency-1 entries, (-1,-5,4) has the latest time, giving <strong>4</strong>.",
                ],
            },
            "A stack per frequency level": {
                "idea": [
                    "Think of frequency levels: the k-th copy of x lives on level k.",
                    "Keep one stack per level; pushing x when its count becomes f puts x on stack <code>group[f]</code>.",
                    "The answer to pop is the top of the highest non-empty level: the most frequent value, and the most recent among ties.",
                ],
                "steps": [
                    "<code>push</code>: increment <code>freq[val]</code> to f, push <code>val</code> onto <code>group[f]</code>, and update <code>max_freq</code>.",
                    "<code>pop</code>: pop from <code>group[max_freq]</code> and decrement that value's count.",
                    "If that level is now empty, lower <code>max_freq</code> by one.",
                ],
                "why": [
                    "A value with count c appears once on each of levels 1..c, so after a pop it still sits on the level below, and that level cannot be empty.",
                    "That is why <code>max_freq</code> only ever drops by exactly one. Every operation is O(1), and space is O(n).",
                ],
                "dry": [
                    "Push 5: level 1 = [5]. Push 7: level 1 = [5, 7]. Push 5: level 2 = [5].",
                    "Push 7: level 2 = [5, 7]. Push 4: level 1 = [5, 7, 4]. Push 5: level 3 = [5], so max_freq = 3.",
                    "Pop: level 3 gives <strong>5</strong>; level 3 is empty, so max_freq = 2.",
                    "Pop: level 2 gives <strong>7</strong> (pushed after 5 there); level 2 = [5].",
                    "Pop: level 2 gives <strong>5</strong>; it is empty, so max_freq = 1.",
                    "Pop: level 1 = [5, 7, 4] gives <strong>4</strong>.",
                ],
            },
        },
    },

    # ------------------------------------------------------------------ largest rectangle
    "largest-rectangle-histogram": {
        "example": {"call": "largest_rectangle_area([2, 1, 5, 6, 2, 3])", "expect": "10"},
        "approaches": {
            "Every pair of edges": {
                "idea": [
                    "A rectangle spans bars i..j, and its height is the shortest bar in that range.",
                    "Try every left edge and extend right one bar at a time, keeping the running minimum, so each new width is O(1) to evaluate.",
                ],
                "steps": [
                    "For each <code>i</code>, start with <code>low = heights[i]</code>.",
                    "For each <code>j ≥ i</code>, update <code>low = min(low, heights[j])</code> and the area <code>low × (j - i + 1)</code>.",
                    "Keep the best area seen.",
                ],
                "why": [
                    "Every possible rectangle is a range i..j at its minimum height, and all of them are checked.",
                    "Maintaining the minimum incrementally makes it O(n²) instead of O(n³). Space is O(1).",
                ],
                "dry": [
                    "i=0: the minimum falls to 1 at j=1, so the best is 1 × 6 = 6 at j=5.",
                    "i=1: the minimum is 1 throughout, at most 1 × 5 = 5.",
                    "i=2: j=2 gives 5; j=3 gives min(5, 6) × 2 = <strong>10</strong>; j=4 drops to 2 × 3 = 6; j=5 gives 2 × 4 = 8.",
                    "i=3: 6, then 2 × 2 = 4, then 2 × 3 = 6. i=4: 2, 4. i=5: 3.",
                    "The best over all pairs is <strong>10</strong>: bars 5 and 6 at height 5.",
                ],
            },
            "Divide and conquer at the minimum": {
                "idea": [
                    "Look at the shortest bar in a range. Either the best rectangle uses it, and then it can span the <em>whole</em> range at that height, or it does not.",
                    "If it does not use that bar, it must lie entirely to its left or entirely to its right.",
                    "So the answer is the larger of three things: min × width, the best on the left, the best on the right.",
                ],
                "steps": [
                    "<code>solve(lo, hi)</code> returns 0 for an empty range.",
                    "Find <code>m</code>, the index of the shortest bar in <code>lo..hi</code>.",
                    "Return <code>max(heights[m] × (hi - lo + 1), solve(lo, m - 1), solve(m + 1, hi))</code>.",
                ],
                "why": [
                    "Every rectangle either contains the minimum bar, and is then capped by it, or avoids it, so the three cases cover everything.",
                    "Like quicksort, balanced splits give O(n log n), but sorted input splits off one bar at a time and gives O(n²). Recursion depth is up to O(n).",
                ],
                "dry": [
                    "<code>solve(0, 5)</code>: the minimum is 1 at index 1, so the full-width option is 1 × 6 = 6.",
                    "The left side <code>solve(0, 0)</code> is the single bar of height 2, giving 2.",
                    "The right side <code>solve(2, 5)</code> = [5, 6, 2, 3]: its minimum is 2 at index 4, so 2 × 4 = 8.",
                    "Inside it, <code>solve(2, 3)</code> = [5, 6]: minimum 5, so 5 × 2 = <strong>10</strong>; <code>solve(3, 3)</code> gives 6. <code>solve(5, 5)</code> gives 3.",
                    "So <code>solve(2, 5)</code> = max(8, 10, 3) = 10, and the whole answer is max(6, 2, 10) = <strong>10</strong>.",
                ],
            },
            "Nearest shorter bar on each side, two stack passes": {
                "idea": [
                    "Give each bar its best rectangle at <em>its own</em> height: it extends left and right until it hits a strictly shorter bar.",
                    "So for each bar we need the index of the nearest shorter bar on the left and on the right, a classic monotonic-stack question.",
                    "Its rectangle is <code>height × (right - left - 1)</code>, and the answer is the best over all bars.",
                ],
                "steps": [
                    "Left pass: keep a stack of indices with increasing heights; pop while the top is ≥ the current bar; the top left behind (or -1) is the left boundary.",
                    "Right pass: the same from right to left, with <code>n</code> when no shorter bar exists.",
                    "Compute <code>h × (right[i] - left[i] - 1)</code> for every bar and take the maximum.",
                ],
                "why": [
                    "The largest rectangle has some bar as its shortest, and it is exactly that bar's rectangle, so trying every bar finds it.",
                    "Each pass pushes and pops every index once: O(n) time, O(n) space.",
                ],
                "dry": [
                    "Left pass: <code>left = [-1, -1, 1, 2, 1, 4]</code>. For example, bar 4 (height 2) pops 6 and 5 and stops at bar 1 (height 1).",
                    "Right pass: <code>right = [1, 6, 4, 4, 6, 6]</code>. For example, bar 2 (height 5) stops at bar 4 (height 2).",
                    "Areas: bar 0: 2 × (1 - (-1) - 1) = 2; bar 1: 1 × 6 = 6; bar 2: 5 × (4 - 1 - 1) = <strong>10</strong>.",
                    "Bar 3: 6 × 1 = 6; bar 4: 2 × (6 - 1 - 1) = 8; bar 5: 3 × 1 = 3.",
                    "The maximum is <strong>10</strong>.",
                ],
            },
            "One stack pass, settle bars as they are popped": {
                "idea": [
                    "Keep a stack of indices whose heights increase from bottom to top.",
                    "When a shorter bar arrives at <code>i</code>, every taller bar popped has just found its right boundary (<code>i</code>), and its left boundary is the bar below it on the stack.",
                    "So a bar's whole rectangle is known the moment it is popped, and one pass is enough.",
                ],
                "steps": [
                    "Iterate over <code>heights + [0]</code>; the final 0 forces every remaining bar to be popped.",
                    "While the top bar is ≥ the current height, pop it as <code>height</code>; its left boundary is the new top, or -1 if the stack is empty.",
                    "Update <code>best</code> with <code>height × (i - left - 1)</code>.",
                    "Push <code>i</code>.",
                ],
                "why": [
                    "Everything between the popped bar and its left neighbour on the stack was at least as tall (it was popped earlier), and so is everything up to i - 1.",
                    "Each index is pushed and popped once: O(n) time, O(n) space.",
                ],
                "dry": [
                    "i=0 (2): push. i=1 (1): pop bar 0, with an empty stack below, so 2 × (1 - (-1) - 1) = 2; push 1.",
                    "i=2 (5) and i=3 (6): taller, so push. The stack's heights are [1, 5, 6].",
                    "i=4 (2): pop bar 3 (6) with left = 2: 6 × (4 - 2 - 1) = 6. Pop bar 2 (5) with left = 1: 5 × (4 - 1 - 1) = <strong>10</strong>.",
                    "Bar 1 (1) is shorter than 2, so stop and push 4. The heights are [1, 2].",
                    "i=5 (3): push. The heights are [1, 2, 3].",
                    "i=6 (sentinel 0): pop bar 5: 3 × 1 = 3; pop bar 4: 2 × (6 - 1 - 1) = 8; pop bar 1: 1 × 6 = 6.",
                    "The best is <strong>10</strong>.",
                ],
            },
        },
    },
}
