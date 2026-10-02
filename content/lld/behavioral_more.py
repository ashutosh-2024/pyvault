from ._lld import code, table, note, caveat, section, question, PATTERNS_GROUP

TOPIC = dict(
    id="behavioral-more",
    title="Behavioral Patterns II: Chain of Responsibility, Visitor, Memento, Mediator, Iterator",
    group=PATTERNS_GROUP,
    summary="Pipelines of handlers, operations over object structures, snapshots, central coordinators and traversal.",
    intro=[
        "The second set of behavioral patterns appears less often on its own, but each is the clear answer to a recognisable problem: a request that should pass through a sequence of handlers, new operations over a fixed set of node types, saving and restoring state, many objects that need coordinating, and walking a collection without exposing its internals.",
    ],
    sections=[
        section(
            "Chain of Responsibility",
            "Pass a request along a chain of handlers. Each handler either deals with it or passes it on (or does part of the work and passes on the rest). The sender does not know which handler will act, and the chain can be reconfigured without touching the sender. Expense approvals, support escalation, HTTP middleware and cash dispensing are all chains.",
            code('''
                class Approver:
                    def __init__(self, name, limit, next_=None):
                        self.name, self.limit, self.next = name, limit, next_

                    def approve(self, amount, reason):
                        if amount <= self.limit:
                            return f"{self.name} approved {amount} for {reason}"
                        if self.next is None:
                            return f"rejected {amount}: above every limit"
                        return self.next.approve(amount, reason)

                chain = Approver("team lead", 1_000, Approver("manager", 10_000, Approver("director", 100_000)))
                for amount in (400, 7_500, 60_000, 250_000):
                    print(chain.approve(amount, "travel"))
            '''),
            "A variant where <em>every</em> handler does part of the work &mdash; ATM denominations, or middleware that each add a header &mdash; is the same structure; the difference is only whether a handler stops the chain.",
            code('''
                def dispense(amount, notes=(2000, 500, 200, 100)):
                    plan = []
                    for note in notes:                       # each handler takes what it can
                        count, amount = divmod(amount, note)
                        if count:
                            plan.append((note, count))
                    if amount:
                        raise ValueError(f"cannot dispense the remaining {amount}")
                    return plan

                print(dispense(4700))
                try:
                    dispense(4750)
                except ValueError as e:
                    print("ValueError:", e)
            '''),
        ),
        section(
            "Visitor",
            "You have a stable set of node types (shapes, AST nodes, document elements) and keep adding <em>operations</em> over them: area, render to SVG, export to JSON, compute bounding box. Visitor moves each operation into its own class with a method per node type, so adding an operation adds one class and touches no node. Python's <code>functools.singledispatch</code> or a <code>match</code> statement on type gives the same separation with less ceremony.",
            code('''
                from dataclasses import dataclass
                from functools import singledispatch

                @dataclass
                class Heading:
                    text: str
                    level: int

                @dataclass
                class Paragraph:
                    text: str

                @dataclass
                class Bullet:
                    items: list

                doc = [Heading("Report", 1), Paragraph("Sales rose."), Bullet(["north", "south"])]

                @singledispatch
                def to_html(node): raise TypeError(node)
                @to_html.register
                def _(node: Heading): return f"<h{node.level}>{node.text}</h{node.level}>"
                @to_html.register
                def _(node: Paragraph): return f"<p>{node.text}</p>"
                @to_html.register
                def _(node: Bullet): return "<ul>" + "".join(f"<li>{i}</li>" for i in node.items) + "</ul>"

                def to_markdown(node):                        # a second operation, via match
                    match node:
                        case Heading(text, level): return "#" * level + " " + text
                        case Paragraph(text): return text
                        case Bullet(items): return "\\n".join(f"- {i}" for i in items)

                print("".join(map(to_html, doc)))
                print("\\n".join(map(to_markdown, doc)))
            '''),
            note("Visitor makes new operations easy and new node types hard (every visitor must learn the new type). Ordinary polymorphism is the opposite. Choose by which of the two you expect to add more often."),
        ),
        section(
            "Memento",
            "Capture an object's internal state in an opaque snapshot so it can be restored later, without exposing internals to whoever stores the snapshot. The originator creates and restores mementos; a caretaker (undo history, checkpoint manager) only keeps them.",
            code('''
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class EditorMemento:                    # opaque to the caretaker
                    _text: str
                    _cursor: int

                class Editor:
                    def __init__(self):
                        self.text, self.cursor = "", 0
                    def type(self, s):
                        self.text = self.text[:self.cursor] + s + self.text[self.cursor:]
                        self.cursor += len(s)
                    def save(self):
                        return EditorMemento(self.text, self.cursor)
                    def restore(self, m):
                        self.text, self.cursor = m._text, m._cursor

                ed, history = Editor(), []
                for word in ("Hello", ", world", "!!!"):
                    history.append(ed.save())
                    ed.type(word)
                print(repr(ed.text))
                ed.restore(history.pop()); print(repr(ed.text))
                ed.restore(history.pop()); print(repr(ed.text))
            '''),
        ),
        section(
            "Mediator",
            "When many objects interact with many others, the web of references becomes unmanageable. A mediator centralises the interactions: components talk only to the mediator, which decides who else is affected. Chat rooms, air-traffic control and form validation (one field enables another) are typical.",
            code('''
                class ChatRoom:                                   # the mediator
                    def __init__(self):
                        self.members, self.log = {}, []
                    def join(self, user):
                        self.members[user.name] = user
                        user.room = self
                    def send(self, sender, text, to=None):
                        targets = [self.members[to]] if to else [u for n, u in self.members.items() if n != sender]
                        for u in targets:
                            u.receive(sender, text)
                        self.log.append((sender, to or "*", text))

                class User:
                    def __init__(self, name):
                        self.name, self.room, self.inbox = name, None, []
                    def say(self, text, to=None):
                        self.room.send(self.name, text, to)       # knows only the room
                    def receive(self, sender, text):
                        self.inbox.append(f"{sender}: {text}")

                room = ChatRoom()
                ann, bob, cy = User("ann"), User("bob"), User("cy")
                for u in (ann, bob, cy):
                    room.join(u)
                ann.say("standup in 5")
                bob.say("running late", to="ann")
                print(ann.inbox, bob.inbox, cy.inbox, sep="\\n")
            '''),
        ),
        section(
            "Iterator",
            "Give sequential access to a collection without exposing its structure. In Python this is built into the language: implement <code>__iter__</code> (usually as a generator) and the object works with <code>for</code>, comprehensions and every function that takes an iterable. The Deep Dive topic on generators covers the details.",
            code('''
                class Playlist:
                    def __init__(self, *songs):
                        self._songs = list(songs)
                    def __iter__(self):                         # default order
                        yield from self._songs
                    def shuffled(self, seed):                   # an alternative traversal
                        import random
                        order = self._songs[:]
                        random.Random(seed).shuffle(order)
                        yield from order

                p = Playlist("intro", "verse", "chorus", "outro")
                print(list(p), list(p.shuffled(1)))
            '''),
        ),
    ],
    questions=[
        question(
            "Chain of Responsibility vs a list of handlers in a loop: what is the difference?",
            "medium",
            "Functionally they are close, and in Python a list of handler functions iterated in order is often the clearest implementation. The classic linked form lets each handler decide to stop, pass on, or wrap the rest of the chain (call next and act on its result), which is how middleware implements before/after behaviour. Use the loop for simple filters and the linked form when handlers need to wrap the remainder of the pipeline.",
        ),
        question(
            "When would you choose Visitor over adding a method to each class?",
            "hard",
            "When the set of classes is stable or not yours to modify (AST node types, a third-party document model) and new operations keep arriving (type checking, pretty printing, optimisation, code generation). Each operation then lives in one place instead of being smeared across every node class. If instead new node types arrive often, adding a method per class is better, because Visitor forces every existing operation to learn each new type.",
        ),
        question(
            "How would you implement Ctrl+Z for a drawing app with both Command and Memento?",
            "medium",
            "Use commands for actions with a cheap inverse (move shape by dx, dy; change colour, storing the old colour) and record each on the undo stack. For actions without a cheap inverse (apply a filter, boolean shape operations), the command captures a memento of the affected objects before executing and restores it on undo. A new action clears the redo stack. Cap the history and merge consecutive tiny commands (each keystroke of a drag) into one.",
        ),
    ],
    refs=[
        ("Refactoring.Guru: Chain of Responsibility", "https://refactoring.guru/design-patterns/chain-of-responsibility"),
        ("Python docs: functools.singledispatch", "https://docs.python.org/3/library/functools.html#functools.singledispatch"),
        ("PEP 636: Structural pattern matching tutorial", "https://peps.python.org/pep-0636/"),
    ],
)
