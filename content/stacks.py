# -*- coding: utf-8 -*-
"""Stacks and Monotonic Stacks topic (NeetCode 250: Stack). Same build
contract as content/dsa.py."""

PRELUDE_ST = '''import heapq
import itertools
import random
from collections import Counter, defaultdict, deque
'''


STACKS_TOPIC = dict(
    id="monotonic-stack",
    title="Stacks and Monotonic Stacks",
    prelude=PRELUDE_ST,
    sections=[

dict(
    id="stacks",
    title="Stacks, queues and monotonic stacks",
    idea=[
        "A stack remembers \"the most recent thing still open\": the last unmatched bracket, the last unresolved operand, the nearest bar still waiting for something taller. A monotonic stack keeps its contents sorted by popping everything a new element makes irrelevant, which turns \"next greater\" questions from O(n&sup2;) into O(n).",
    ],
    problems=[

    # ------------------------------------------------------------------ 682
    dict(
        id="baseball-game",
        lc=682, slug="baseball-game",
        name="Baseball Game",
        difficulty="easy",
        framing=[
            "Process score operations: a number records a score, <code>+</code> records the sum of the previous two, <code>D</code> doubles the previous, <code>C</code> cancels the previous. Every operation refers to the <em>most recent valid</em> scores, which is exactly what a stack exposes.",
        ],
        approaches=[
            dict(
                name="Stack of valid scores",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Push numbers; <code>C</code> pops (removing the score from history, so later operations see the one before it); <code>D</code> and <code>+</code> read the top one or two entries and push the result. The answer is the sum of what remains.",
                    "Each operation is O(1). There is no cleverer approach: the cancellations mean you must remember the history.",
                ],
                code='''def cal_points(operations):
    stack = []
    for op in operations:
        if op == "+":
            stack.append(stack[-1] + stack[-2])
        elif op == "D":
            stack.append(2 * stack[-1])
        elif op == "C":
            stack.pop()
        else:
            stack.append(int(op))
    return sum(stack)''',
            ),
        ],
        tests='''assert cal_points(["5", "2", "C", "D", "+"]) == 30
assert cal_points(["5", "-2", "4", "C", "D", "9", "+", "+"]) == 27
assert cal_points(["1", "C"]) == 0''',
    ),

    # ------------------------------------------------------------------ 20
    dict(
        id="valid-parentheses",
        lc=20, slug="valid-parentheses",
        name="Valid Parentheses",
        difficulty="easy",
        framing=[
            "Is a string of <code>()[]{}</code> properly nested? Every closing bracket must match the most recent <em>unmatched</em> opening bracket &mdash; \"most recent unmatched\" is the definition of a stack.",
        ],
        approaches=[
            dict(
                name="Repeatedly delete adjacent pairs",
                time="O(n&sup2;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "A valid string always contains an adjacent matched pair; removing it leaves a valid string. So delete <code>()</code>, <code>[]</code> and <code>{}</code> until nothing changes and check for emptiness. Each round is O(n) and there can be n/2 rounds.",
                ],
                code='''def is_valid(s):
    prev = None
    while prev != s:
        prev = s
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""''',
            ),
            dict(
                name="Stack of open brackets",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Push opening brackets. A closing bracket must match the top of the stack; pop it if so, fail otherwise (including on an empty stack). At the end, the stack must be empty &mdash; leftover openers are unclosed.",
                    "One pass. A map from closer to opener keeps the matching logic to a single comparison.",
                ],
                code='''def is_valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack''',
            ),
        ],
        tests='''assert is_valid("()") is True
assert is_valid("()[]{}") is True
assert is_valid("(]") is False
assert is_valid("([)]") is False
assert is_valid("{[]}") is True
assert is_valid("(") is False and is_valid("]") is False''',
    ),

    # ------------------------------------------------------------------ 225
    dict(
        id="stack-using-queues",
        lc=225, slug="implement-stack-using-queues",
        name="Implement Stack Using Queues",
        difficulty="easy",
        framing=[
            "Build a LIFO stack using only queue operations (push to back, pop from front, peek front, size). Some operation has to pay O(n) to reverse the order; the choice is which one.",
        ],
        approaches=[
            dict(
                name="Two queues, pay on pop",
                time="push O(1), pop O(n)",
                space="O(n)",
                why=[
                    "Push appends to the main queue. To pop, move all but the last element to a helper queue, take the last one, and swap the queues' roles. Cheap pushes, expensive pops.",
                ],
                code='''class MyStack:
    def __init__(self):
        self.q, self.helper = deque(), deque()

    def push(self, x):
        self.q.append(x)

    def pop(self):
        while len(self.q) > 1:
            self.helper.append(self.q.popleft())
        top = self.q.popleft()
        self.q, self.helper = self.helper, self.q
        return top

    def top(self):
        x = self.pop()
        self.push(x)
        return x

    def empty(self):
        return not self.q''',
            ),
            dict(
                name="One queue, rotate on push",
                time="push O(n), pop O(1)",
                space="O(n)",
                best=True,
                why=[
                    "After appending the new element, rotate the queue by moving the n - 1 older elements from front to back. The newest element is now at the front, so the queue's front <em>is</em> the stack's top and pop, top and empty are all O(1).",
                    "A single queue and simpler invariants; preferable when reads outnumber writes.",
                ],
                code='''class MyStack:
    def __init__(self):
        self.q = deque()

    def push(self, x):
        self.q.append(x)
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())      # newest to the front

    def pop(self):
        return self.q.popleft()

    def top(self):
        return self.q[0]

    def empty(self):
        return not self.q''',
            ),
        ],
        tests='''s = MyStack()
s.push(1); s.push(2)
assert s.top() == 2 and s.pop() == 2 and s.empty() is False and s.pop() == 1 and s.empty() is True
rng, s, model = random.Random(0), MyStack(), []
for _ in range(300):
    if model and rng.random() < 0.4:
        assert s.pop() == model.pop()
    elif model and rng.random() < 0.3:
        assert s.top() == model[-1]
    else:
        v = rng.randint(0, 99); s.push(v); model.append(v)
    assert s.empty() == (not model)''',
    ),

    # ------------------------------------------------------------------ 232
    dict(
        id="queue-using-stacks",
        lc=232, slug="implement-queue-using-stacks",
        name="Implement Queue using Stacks",
        difficulty="easy",
        framing=[
            "Build a FIFO queue from two stacks. The follow-up asks for amortised O(1) per operation, and the answer is a classic amortised-analysis argument: move elements between stacks only when the output stack runs dry.",
        ],
        approaches=[
            dict(
                name="Move everything on every push",
                time="push O(n), pop O(1)",
                space="O(n)",
                why=[
                    "Keep the stack so that its top is the queue's front: to push, pour everything into a helper, push the new element, pour everything back. Every push costs O(n).",
                ],
                code='''class MyQueue:
    def __init__(self):
        self.s, self.helper = [], []

    def push(self, x):
        while self.s:
            self.helper.append(self.s.pop())
        self.s.append(x)
        while self.helper:
            self.s.append(self.helper.pop())

    def pop(self):
        return self.s.pop()

    def peek(self):
        return self.s[-1]

    def empty(self):
        return not self.s''',
            ),
            dict(
                name="Input and output stacks, transfer lazily",
                time="amortised O(1)",
                space="O(n)",
                best=True,
                why=[
                    "Push always goes onto the <em>in</em> stack. Pop and peek read from the <em>out</em> stack; only when it is empty, pour the whole <em>in</em> stack into it, which reverses the order so the oldest element is on top.",
                    "A single transfer can cost O(n), but each element is moved from <em>in</em> to <em>out</em> exactly once in its lifetime. Across any sequence of n operations the total work is O(n): amortised O(1) per operation.",
                ],
                code='''class MyQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []

    def push(self, x):
        self.inbox.append(x)

    def _shift(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())   # reverses: oldest on top

    def pop(self):
        self._shift()
        return self.outbox.pop()

    def peek(self):
        self._shift()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox''',
            ),
        ],
        tests='''q = MyQueue()
q.push(1); q.push(2)
assert q.peek() == 1 and q.pop() == 1 and q.empty() is False
rng, q, model = random.Random(1), MyQueue(), deque()
for _ in range(300):
    if model and rng.random() < 0.4:
        assert q.pop() == model.popleft()
    elif model and rng.random() < 0.3:
        assert q.peek() == model[0]
    else:
        v = rng.randint(0, 99); q.push(v); model.append(v)
    assert q.empty() == (not model)''',
    ),

    # ------------------------------------------------------------------ 155
    dict(
        id="min-stack",
        lc=155, slug="min-stack",
        name="Min Stack",
        difficulty="medium",
        framing=[
            "A stack that also returns its minimum, with every operation in O(1). The minimum changes when elements are popped, so a single \"current min\" variable is not enough &mdash; you need the minimum <em>as of each depth</em>.",
        ],
        approaches=[
            dict(
                name="Scan for the minimum",
                time="getMin O(n)",
                space="O(n)",
                tag="brute force",
                why=["A plain stack; <code>getMin</code> scans it. Correct, but not O(1)."],
                code='''class MinStack:
    def __init__(self):
        self.s = []

    def push(self, val):
        self.s.append(val)

    def pop(self):
        self.s.pop()

    def top(self):
        return self.s[-1]

    def getMin(self):
        return min(self.s)''',
            ),
            dict(
                name="Store (value, min so far) pairs",
                time="O(1) all",
                space="O(n)",
                best=True,
                why=[
                    "Push each value together with the minimum of the stack at that moment: <code>min(val, previous min)</code>. Popping restores the previous pair and therefore the previous minimum automatically.",
                    "The simplest correct O(1) design. It stores two numbers per element.",
                ],
                code='''class MinStack:
    def __init__(self):
        self.s = []                                  # (value, min so far)

    def push(self, val):
        self.s.append((val, min(val, self.s[-1][1]) if self.s else val))

    def pop(self):
        self.s.pop()

    def top(self):
        return self.s[-1][0]

    def getMin(self):
        return self.s[-1][1]''',
            ),
            dict(
                name="Second stack of minimums, pushed only when needed",
                time="O(1) all",
                space="O(n) worst, less in practice",
                why=[
                    "Keep a separate stack that records a value only when it is <em>&le;</em> the current minimum. When popping a value equal to the top of the min stack, pop that too. For inputs where the minimum rarely changes, the min stack stays small.",
                    "The <code>&le;</code> (not <code>&lt;</code>) is essential: with duplicate minimums, popping one copy must not remove the minimum while another copy remains.",
                ],
                code='''class MinStack:
    def __init__(self):
        self.s, self.mins = [], []

    def push(self, val):
        self.s.append(val)
        if not self.mins or val <= self.mins[-1]:
            self.mins.append(val)

    def pop(self):
        if self.s.pop() == self.mins[-1]:
            self.mins.pop()

    def top(self):
        return self.s[-1]

    def getMin(self):
        return self.mins[-1]''',
            ),
            dict(
                name="One stack of differences from the minimum",
                time="O(1) all",
                space="O(1) extra beyond the values",
                tag="one number per element",
                why=[
                    "Store <code>val - min</code> instead of <code>val</code>. A negative stored difference means this push set a new minimum, and it also encodes the <em>old</em> minimum: <code>old = new - diff</code>. So popping a negative entry restores the previous minimum with arithmetic instead of a second stack.",
                    "One number per element plus one variable. In fixed-width languages the difference can overflow (values span 32 bits); Python integers do not.",
                ],
                code='''class MinStack:
    def __init__(self):
        self.s, self.min = [], None

    def push(self, val):
        if not self.s:
            self.s.append(0)
            self.min = val
        else:
            self.s.append(val - self.min)
            if val < self.min:
                self.min = val                         # diff < 0 marks a new min

    def pop(self):
        diff = self.s.pop()
        if diff < 0:
            self.min -= diff                           # restore the previous min
        if not self.s:
            self.min = None

    def top(self):
        diff = self.s[-1]
        return self.min if diff < 0 else self.min + diff

    def getMin(self):
        return self.min''',
            ),
        ],
        tests='''m = MinStack()
m.push(-2); m.push(0); m.push(-3)
assert m.getMin() == -3
m.pop()
assert m.top() == 0 and m.getMin() == -2
rng, m, model = random.Random(2), MinStack(), []
for _ in range(400):
    if model and rng.random() < 0.4:
        m.pop(); model.pop()
    else:
        v = rng.randint(-5, 5); m.push(v); model.append(v)
    if model:
        assert m.top() == model[-1] and m.getMin() == min(model)''',
    ),

    # ------------------------------------------------------------------ 150
    dict(
        id="evaluate-rpn",
        lc=150, slug="evaluate-reverse-polish-notation",
        name="Evaluate Reverse Polish Notation",
        difficulty="medium",
        framing=[
            "Evaluate an expression in postfix notation (<code>2 1 + 3 *</code> is <code>(2 + 1) &times; 3</code>). Division truncates <strong>toward zero</strong>, which is not what Python's <code>//</code> does for negative numbers.",
        ],
        pitfall="Using <code>a // b</code>. It floors, so <code>-7 // 2</code> is -4; the problem wants -3. Use <code>int(a / b)</code> (safe here because the values fit in a float exactly) or adjust the floor result.",
        approaches=[
            dict(
                name="Operand stack",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Numbers are pushed. An operator pops the right operand, then the left (order matters for <code>-</code> and <code>/</code>), and pushes the result. The final stack holds one value: the answer.",
                    "Postfix notation needs no precedence rules or parentheses, which is why compilers and old HP calculators use it.",
                ],
                code='''def eval_rpn(tokens):
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: int(a / b),        # truncate toward zero
    }
    stack = []
    for tok in tokens:
        if tok in ops:
            b, a = stack.pop(), stack.pop()   # right operand is on top
            stack.append(ops[tok](a, b))
        else:
            stack.append(int(tok))
    return stack[0]''',
            ),
            dict(
                name="Recursion from the end",
                time="O(n)",
                space="O(n)",
                why=[
                    "Read the expression backwards as a tree: the last token is the root operator, whose right operand is the sub-expression ending just before it and whose left operand ends before that. A recursive function consuming tokens from the end rebuilds exactly that tree. Same cost; the call stack replaces the explicit one.",
                ],
                code='''def eval_rpn(tokens):
    tokens = list(tokens)

    def ev():
        tok = tokens.pop()
        if tok not in "+-*/":
            return int(tok)
        b = ev()                              # right operand is evaluated first
        a = ev()
        if tok == "+": return a + b
        if tok == "-": return a - b
        if tok == "*": return a * b
        return int(a / b)

    return ev()''',
            ),
        ],
        tests='''assert eval_rpn(["2", "1", "+", "3", "*"]) == 9
assert eval_rpn(["4", "13", "5", "/", "+"]) == 6
assert eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]) == 22
assert eval_rpn(["-7", "2", "/"]) == -3''',
    ),

    # ------------------------------------------------------------------ 735
    dict(
        id="asteroid-collision",
        lc=735, slug="asteroid-collision",
        name="Asteroid Collision",
        difficulty="medium",
        framing=[
            "Asteroids move along a line (positive = right, negative = left). When two meet, the smaller explodes; equal sizes both explode. Only a right-mover followed later by a left-mover can collide, and a new left-mover hits the <em>most recent</em> surviving right-movers first &mdash; a stack.",
        ],
        approaches=[
            dict(
                name="Resolve one collision at a time",
                time="O(n&sup2;)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Scan for the first adjacent pair <code>(+, -)</code>, resolve it, and start over until no such pair exists. Each resolution removes at least one asteroid, but each rescan is O(n).",
                ],
                code='''def asteroid_collision(asteroids):
    a = list(asteroids)
    changed = True
    while changed:
        changed = False
        for i in range(len(a) - 1):
            if a[i] > 0 > a[i + 1]:
                if abs(a[i]) > abs(a[i + 1]):
                    del a[i + 1]
                elif abs(a[i]) < abs(a[i + 1]):
                    del a[i]
                else:
                    del a[i:i + 2]
                changed = True
                break
    return a''',
            ),
            dict(
                name="Stack of survivors",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "The stack holds asteroids that have survived so far. A left-mover collides with right-movers on top of the stack: pop every smaller one, stop if it meets a bigger one (it dies), pop both on a tie. If it survives everything, push it.",
                    "Each asteroid is pushed and popped at most once: O(n). Left-movers at the bottom of the stack never collide, because nothing to their left moves right toward them.",
                ],
                code='''def asteroid_collision(asteroids):
    stack = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()                   # the right-mover explodes, keep going
            elif stack[-1] == -a:
                stack.pop()
                alive = False                 # both explode
            else:
                alive = False                 # the left-mover explodes
        if alive:
            stack.append(a)
    return stack''',
            ),
        ],
        tests='''assert asteroid_collision([5, 10, -5]) == [5, 10]
assert asteroid_collision([8, -8]) == []
assert asteroid_collision([10, 2, -5]) == [10]
assert asteroid_collision([-2, -1, 1, 2]) == [-2, -1, 1, 2]
rng = random.Random(3)
for _ in range(60):
    a = [rng.choice([-1, 1]) * rng.randint(1, 5) for _ in range(rng.randint(1, 10))]
    b = list(a); changed = True
    while changed:
        changed = False
        for i in range(len(b) - 1):
            if b[i] > 0 > b[i + 1]:
                if b[i] > -b[i + 1]: del b[i + 1]
                elif b[i] < -b[i + 1]: del b[i]
                else: del b[i:i + 2]
                changed = True; break
    assert asteroid_collision(a) == b''',
    ),

    # ------------------------------------------------------------------ 739
    dict(
        id="daily-temperatures",
        lc=739, slug="daily-temperatures",
        name="Daily Temperatures",
        difficulty="medium",
        framing=[
            "For each day, how many days until a warmer one? This is \"next greater element\", the defining monotonic-stack problem: keep the days still waiting for a warmer day, and let each new day resolve every cooler day waiting on the stack.",
        ],
        approaches=[
            dict(
                name="Scan forward from each day",
                time="O(n&sup2;)",
                space="O(1) beyond output",
                tag="brute force",
                why=["For each day, walk forward until a warmer day. A long decreasing run makes this quadratic."],
                code='''def daily_temperatures(temps):
    out = [0] * len(temps)
    for i, t in enumerate(temps):
        for j in range(i + 1, len(temps)):
            if temps[j] > t:
                out[i] = j - i
                break
    return out''',
            ),
            dict(
                name="Monotonic decreasing stack of waiting days",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "The stack holds indices of days that have not yet seen a warmer day, with temperatures decreasing from bottom to top. A new day pops every colder day on top &mdash; it <em>is</em> their answer &mdash; and then waits itself.",
                    "The stack stays decreasing because a day is only pushed after everything colder has been popped. Each day is pushed and popped once: O(n).",
                ],
                code='''def daily_temperatures(temps):
    out, stack = [0] * len(temps), []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j                    # today is j's warmer day
        stack.append(i)
    return out''',
            ),
            dict(
                name="Right to left, jump along known answers",
                time="O(n)",
                space="O(1) beyond output",
                tag="no stack",
                why=[
                    "Fill answers from the last day backwards. To find day i's warmer day, start at <code>j = i + 1</code>; if <code>temps[j]</code> is not warmer, jump straight to <em>j's</em> warmer day (<code>j + out[j]</code>) &mdash; nothing in between can be warmer than <code>temps[j]</code>, let alone <code>temps[i]</code>. If <code>out[j]</code> is 0, there is no warmer day at all.",
                    "The jumps skip over resolved stretches, giving amortised O(n) with no extra structure: the output array doubles as the stack.",
                ],
                code='''def daily_temperatures(temps):
    n = len(temps)
    out = [0] * n
    for i in range(n - 2, -1, -1):
        j = i + 1
        while temps[j] <= temps[i]:
            if out[j] == 0:
                j = None
                break
            j += out[j]                       # skip days known to be colder
        if j is not None:
            out[i] = j - i
    return out''',
            ),
        ],
        tests='''assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
assert daily_temperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
assert daily_temperatures([30, 60, 90]) == [1, 1, 0]
rng = random.Random(4)
for _ in range(60):
    t = [rng.randint(30, 40) for _ in range(rng.randint(1, 15))]
    expect = [next((j - i for j in range(i + 1, len(t)) if t[j] > t[i]), 0) for i in range(len(t))]
    assert daily_temperatures(t) == expect''',
    ),

    # ------------------------------------------------------------------ 901
    dict(
        id="online-stock-span",
        lc=901, slug="online-stock-span",
        name="Online Stock Span",
        difficulty="medium",
        framing=[
            "Prices arrive one at a time; for each, return how many consecutive days (including today) had a price &le; today's. An online version of \"previous greater element\". The stack stores not just prices but the span each one already covers, so absorbed days are never looked at again.",
        ],
        approaches=[
            dict(
                name="Scan back through history",
                time="O(n) per call",
                space="O(n)",
                tag="brute force",
                why=["Keep every price; walk backwards until a bigger one. A rising market makes every call scan everything."],
                code='''class StockSpanner:
    def __init__(self):
        self.prices = []

    def next(self, price):
        self.prices.append(price)
        span = 0
        for p in reversed(self.prices):
            if p > price:
                break
            span += 1
        return span''',
            ),
            dict(
                name="Monotonic stack of (price, span)",
                time="amortised O(1) per call",
                space="O(n)",
                best=True,
                why=[
                    "Keep <code>(price, span)</code> pairs with strictly decreasing prices. A new price pops every pair with price &le; it and adds their spans to its own: those days are all covered by today, and any future day that reaches today will reach them too, so they can be collapsed into today's entry.",
                    "Each price is pushed once and popped at most once: amortised O(1).",
                ],
                code='''class StockSpanner:
    def __init__(self):
        self.stack = []                        # (price, span), prices decreasing

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]        # absorb the covered days
        self.stack.append((price, span))
        return span''',
            ),
        ],
        tests='''s = StockSpanner()
assert [s.next(p) for p in [100, 80, 60, 70, 60, 75, 85]] == [1, 1, 1, 2, 1, 4, 6]
rng = random.Random(5)
for _ in range(30):
    prices = [rng.randint(1, 10) for _ in range(rng.randint(1, 15))]
    s = StockSpanner()
    for i, p in enumerate(prices):
        k = 0
        while i - k >= 0 and prices[i - k] <= p:
            k += 1
        assert s.next(p) == k''',
    ),

    # ------------------------------------------------------------------ 853
    dict(
        id="car-fleet",
        lc=853, slug="car-fleet",
        name="Car Fleet",
        difficulty="medium",
        framing=[
            "Cars drive toward a target; a faster car that catches a slower one ahead joins it and drives at its speed. How many fleets arrive? Sort by position from closest to the target: each car either catches the fleet directly ahead (its arrival time is no greater) or forms a new, slower fleet.",
        ],
        approaches=[
            dict(
                name="Sort by position, stack of fleet arrival times",
                time="O(n log n)",
                space="O(n)",
                why=[
                    "Process cars from the one nearest the target backwards, computing each car's solo arrival time <code>(target - position) / speed</code>. If a car would arrive no later than the fleet directly ahead, it catches up and merges &mdash; it adds nothing. Otherwise it is a new fleet: push its time.",
                    "The stack's size is the answer, and its times are increasing from bottom to top.",
                ],
                code='''def car_fleet(target, position, speed):
    stack = []
    for p, s in sorted(zip(position, speed), reverse=True):
        t = (target - p) / s
        if not stack or t > stack[-1]:
            stack.append(t)                    # slower than the fleet ahead: new fleet
    return len(stack)''',
            ),
            dict(
                name="Sort, track only the slowest fleet ahead",
                time="O(n log n)",
                space="O(1) beyond sorting",
                best=True,
                why=[
                    "Only the top of that stack is ever compared, so a single variable holding the latest fleet's arrival time is enough. Count how many times a new fleet forms.",
                    "Sorting dominates. Using exact fractions avoids floating-point ties: compare <code>(target - p) * s_ahead</code> with <code>(target - p_ahead) * s</code> if precision is a worry.",
                ],
                code='''def car_fleet(target, position, speed):
    fleets, slowest = 0, 0.0
    for p, s in sorted(zip(position, speed), reverse=True):
        t = (target - p) / s
        if t > slowest:
            fleets += 1
            slowest = t
    return fleets''',
            ),
        ],
        tests='''assert car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]) == 3
assert car_fleet(10, [3], [3]) == 1
assert car_fleet(100, [0, 2, 4], [4, 2, 1]) == 1
assert car_fleet(10, [6, 8], [3, 2]) == 2''',
    ),

    # ------------------------------------------------------------------ 71
    dict(
        id="simplify-path",
        lc=71, slug="simplify-path",
        name="Simplify Path",
        difficulty="medium",
        framing=[
            "Convert a Unix absolute path to canonical form: collapse repeated slashes, drop <code>.</code>, resolve <code>..</code> by going up a directory (never above the root). <code>..</code> undoes the most recent directory, which makes the directory list a stack.",
        ],
        approaches=[
            dict(
                name="Split on '/', stack of directory names",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Splitting on <code>/</code> turns repeated slashes into empty strings, which are skipped along with <code>.</code>. A <code>..</code> pops the stack if it is not empty. Anything else &mdash; including names like <code>...</code> &mdash; is a directory and is pushed. Join with <code>/</code> and prefix the root.",
                ],
                code='''def simplify_path(path):
    stack = []
    for part in path.split("/"):
        if part == "..":
            if stack:
                stack.pop()
        elif part and part != ".":
            stack.append(part)
    return "/" + "/".join(stack)''',
            ),
        ],
        tests='''assert simplify_path("/home/") == "/home"
assert simplify_path("/home//foo/") == "/home/foo"
assert simplify_path("/home/user/Documents/../Pictures") == "/home/user/Pictures"
assert simplify_path("/../") == "/"
assert simplify_path("/.../a/../b/c/../d/./") == "/.../b/d"''',
    ),

    # ------------------------------------------------------------------ 394
    dict(
        id="decode-string",
        lc=394, slug="decode-string",
        name="Decode String",
        difficulty="medium",
        framing=[
            "Expand <code>k[encoded]</code> patterns, which may nest: <code>3[a2[c]]</code> is <code>accaccacc</code>. Nesting means the string being built must be suspended at each <code>[</code> and resumed at the matching <code>]</code> &mdash; either with an explicit stack or with recursion.",
        ],
        approaches=[
            dict(
                name="Stack of (outer string, repeat count)",
                time="O(output)",
                space="O(output)",
                best=True,
                why=[
                    "Build the current string and number as you read. At <code>[</code>, push the string built so far and the number, and start fresh. At <code>]</code>, pop them and set <code>current = outer + count &times; current</code>. Digits may be multi-digit, so accumulate <code>num = num * 10 + d</code>.",
                    "The cost is dominated by the output length, which can be exponential in the input (<code>9[9[9[a]]]</code>).",
                ],
                code='''def decode_string(s):
    stack, cur, num = [], "", 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((cur, num))
            cur, num = "", 0
        elif ch == "]":
            outer, k = stack.pop()
            cur = outer + cur * k
        else:
            cur += ch
    return cur''',
            ),
            dict(
                name="Recursive descent",
                time="O(output)",
                space="O(output)",
                why=[
                    "A function decodes from position i until it meets a <code>]</code> or the end, returning the string and the position reached. On <code>k[</code> it recurses for the inside and repeats the result. The grammar's nesting maps directly onto the call stack.",
                ],
                code='''def decode_string(s):
    def parse(i):
        out, num = [], 0
        while i < len(s) and s[i] != "]":
            ch = s[i]
            if ch.isdigit():
                num = num * 10 + int(ch)
                i += 1
            elif ch == "[":
                inner, i = parse(i + 1)
                out.append(inner * num)
                num = 0
                i += 1                         # skip the ']'
            else:
                out.append(ch)
                i += 1
        return "".join(out), i

    return parse(0)[0]''',
            ),
        ],
        tests='''assert decode_string("3[a]2[bc]") == "aaabcbc"
assert decode_string("3[a2[c]]") == "accaccacc"
assert decode_string("2[abc]3[cd]ef") == "abcabccdcdcdef"
assert decode_string("10[a]") == "a" * 10
assert decode_string("abc") == "abc"''',
    ),

    # ------------------------------------------------------------------ 895
    dict(
        id="maximum-frequency-stack",
        lc=895, slug="maximum-frequency-stack",
        name="Maximum Frequency Stack",
        difficulty="hard",
        framing=[
            "<code>push(x)</code>, and <code>pop()</code> removes the <em>most frequent</em> element, breaking ties by the most recently pushed. Both in O(1). The insight: keep a separate stack for each frequency level, so \"most frequent, most recent\" is the top of the highest-frequency stack.",
        ],
        approaches=[
            dict(
                name="List plus counts, scan on pop",
                time="push O(1), pop O(n)",
                space="O(n)",
                tag="brute force",
                why=[
                    "Keep the push order and a frequency map. To pop, find the highest frequency, then scan from the end for the latest element with that frequency.",
                ],
                code='''class FreqStack:
    def __init__(self):
        self.items, self.freq = [], Counter()

    def push(self, val):
        self.items.append(val)
        self.freq[val] += 1

    def pop(self):
        top = max(self.freq.values())
        for i in range(len(self.items) - 1, -1, -1):
            if self.freq[self.items[i]] == top:
                val = self.items.pop(i)
                self.freq[val] -= 1
                return val''',
            ),
            dict(
                name="Heap keyed by (frequency, push time)",
                time="O(log n) per operation",
                space="O(n)",
                why=[
                    "On every push, record the element's new frequency and a timestamp, and push <code>(-freq, -time, val)</code> onto a heap. The top is the most frequent, most recent entry. Popping it and decrementing the element's frequency is consistent, because the entry for its previous frequency is still in the heap with its original timestamp.",
                ],
                code='''class FreqStack:
    def __init__(self):
        self.heap, self.freq, self.time = [], Counter(), 0

    def push(self, val):
        self.freq[val] += 1
        self.time += 1
        heapq.heappush(self.heap, (-self.freq[val], -self.time, val))

    def pop(self):
        _, _, val = heapq.heappop(self.heap)
        self.freq[val] -= 1
        return val''',
            ),
            dict(
                name="A stack per frequency level",
                time="O(1) per operation",
                space="O(n)",
                best=True,
                why=[
                    "When x reaches frequency f, push it onto <code>group[f]</code>. An element with frequency 3 then appears in groups 1, 2 and 3 &mdash; once per level it reached. <code>max_freq</code> tracks the highest non-empty group.",
                    "Pop takes the top of <code>group[max_freq]</code>: the most recent element to reach the top frequency. Decrement its count; if that group is now empty, <code>max_freq</code> drops by exactly one &mdash; the popped element still sits in the level below, so that level is non-empty.",
                ],
                code='''class FreqStack:
    def __init__(self):
        self.freq = Counter()
        self.group = defaultdict(list)
        self.max_freq = 0

    def push(self, val):
        self.freq[val] += 1
        f = self.freq[val]
        self.group[f].append(val)
        self.max_freq = max(self.max_freq, f)

    def pop(self):
        val = self.group[self.max_freq].pop()
        self.freq[val] -= 1
        if not self.group[self.max_freq]:
            self.max_freq -= 1
        return val''',
            ),
        ],
        tests='''fs = FreqStack()
for v in [5, 7, 5, 7, 4, 5]:
    fs.push(v)
assert [fs.pop() for _ in range(4)] == [5, 7, 5, 4]
rng = random.Random(6)
for _ in range(20):
    fs, items, t = FreqStack(), [], 0
    for _ in range(60):
        if items and rng.random() < 0.4:
            f = Counter(v for v, _ in items)
            top = max(f.values())
            idx = max(i for i, (v, _) in enumerate(items) if f[v] == top)
            assert fs.pop() == items.pop(idx)[0]
        else:
            v = rng.randint(0, 4); t += 1; fs.push(v); items.append((v, t))''',
    ),

    # ------------------------------------------------------------------ 84
    dict(
        id="largest-rectangle-histogram",
        lc=84, slug="largest-rectangle-in-histogram",
        name="Largest Rectangle In Histogram",
        difficulty="hard",
        framing=[
            "The largest rectangle under a histogram. For every bar, the best rectangle using that bar as its <em>shortest</em> bar extends left and right until a shorter bar blocks it. So the problem is: for each bar, find the nearest shorter bar on each side &mdash; a monotonic-stack question.",
        ],
        approaches=[
            dict(
                name="Every pair of edges",
                time="O(n&sup2;)",
                space="O(1)",
                tag="brute force",
                why=[
                    "For each left edge, extend right while tracking the minimum height; area = min &times; width. The minimum is maintained incrementally, so it is O(n&sup2;) rather than O(n&sup3;).",
                ],
                code='''def largest_rectangle_area(heights):
    best = 0
    for i in range(len(heights)):
        low = heights[i]
        for j in range(i, len(heights)):
            low = min(low, heights[j])
            best = max(best, low * (j - i + 1))
    return best''',
            ),
            dict(
                name="Divide and conquer at the minimum",
                time="O(n log n) average, O(n&sup2;) worst",
                space="O(n) recursion",
                why=[
                    "The best rectangle either uses the shortest bar across the whole range (width = the whole range) or lies entirely left or right of it. Recurse on both sides. Like quicksort, it is fast on random data and quadratic on sorted input (a segment tree for range minimums brings the worst case to O(n log n)).",
                ],
                code='''def largest_rectangle_area(heights):
    def solve(lo, hi):
        if lo > hi:
            return 0
        m = min(range(lo, hi + 1), key=heights.__getitem__)
        return max(heights[m] * (hi - lo + 1), solve(lo, m - 1), solve(m + 1, hi))
    return solve(0, len(heights) - 1)''',
            ),
            dict(
                name="Nearest shorter bar on each side, two stack passes",
                time="O(n)",
                space="O(n)",
                why=[
                    "One monotonic-stack pass left to right finds, for every bar, the index of the nearest shorter bar to its left; a second pass right to left finds the nearest shorter to its right. Bar i's rectangle then spans strictly between them. Easy to reason about, two passes.",
                ],
                code='''def largest_rectangle_area(heights):
    n = len(heights)
    left, right, stack = [-1] * n, [n] * n, []
    for i in range(n):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        left[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and heights[stack[-1]] >= heights[i]:
            stack.pop()
        right[i] = stack[-1] if stack else n
        stack.append(i)
    return max(h * (right[i] - left[i] - 1) for i, h in enumerate(heights))''',
            ),
            dict(
                name="One stack pass, settle bars as they are popped",
                time="O(n)",
                space="O(n)",
                best=True,
                why=[
                    "Keep indices with increasing heights. When a shorter bar arrives at i, every taller bar popped has just found its right boundary (i), and its left boundary is whatever is below it on the stack. So its full rectangle is known at the moment it is popped.",
                    "Appending a sentinel bar of height 0 at the end flushes every remaining bar. One pass, each index pushed and popped once.",
                ],
                code='''def largest_rectangle_area(heights):
    stack, best = [], 0                       # indices, heights increasing
    for i, h in enumerate(heights + [0]):     # the 0 flushes the stack
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best''',
            ),
        ],
        tests='''assert largest_rectangle_area([2, 1, 5, 6, 2, 3]) == 10
assert largest_rectangle_area([2, 4]) == 4
assert largest_rectangle_area([1]) == 1
assert largest_rectangle_area([5, 5, 5]) == 15
rng = random.Random(7)
for _ in range(60):
    h = [rng.randint(0, 8) for _ in range(rng.randint(1, 12))]
    assert largest_rectangle_area(h) == max(min(h[i:j + 1]) * (j - i + 1) for i in range(len(h)) for j in range(i, len(h)))''',
    ),
    ],
),
    ],
)
