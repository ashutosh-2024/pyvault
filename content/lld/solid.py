from ._lld import code, table, note, caveat, section, question, PATTERNS_GROUP

TOPIC = dict(
    id="solid",
    title="SOLID and OOP Principles in Python",
    group=PATTERNS_GROUP,
    summary="Single responsibility, open/closed, Liskov, interface segregation, dependency inversion - each shown broken, then fixed.",
    intro=[
        "SOLID is five rules for keeping classes easy to change. Design patterns are mostly SOLID applied to a specific recurring problem, so if you understand why each principle exists, you can usually derive the pattern instead of memorising it.",
        "Each principle below starts with code that violates it, shows the concrete problem that causes, then fixes it.",
    ],
    sections=[
        section(
            "S: Single responsibility",
            "A class should have one reason to change. &ldquo;Reason to change&rdquo; means a stakeholder or concern: tax rules, report formatting, storage. A class that mixes them must be edited (and retested) for every one of those concerns.",
            code('''
                class Invoice:                                  # three reasons to change
                    def __init__(self, items):
                        self.items = items                      # [(name, price, qty)]

                    def total(self):                            # pricing rules
                        return sum(p * q for _, p, q in self.items) * 1.18

                    def to_html(self):                          # presentation
                        return "<ul>" + "".join(f"<li>{n}</li>" for n, _, _ in self.items) + "</ul>"

                    def save(self, db):                         # persistence
                        db.append(self.items)

                print(Invoice([("pen", 10, 3)]).total())
            ''', label="before"),
            code('''
                from dataclasses import dataclass

                @dataclass
                class Invoice:                                  # data + its own invariants only
                    items: list

                    def subtotal(self):
                        return sum(p * q for _, p, q in self.items)

                class TaxCalculator:
                    def __init__(self, rate):
                        self.rate = rate
                    def total(self, invoice):
                        return round(invoice.subtotal() * (1 + self.rate), 2)

                class HtmlRenderer:
                    def render(self, invoice):
                        return "<ul>" + "".join(f"<li>{n} x{q}</li>" for n, _, q in invoice.items) + "</ul>"

                class InvoiceRepository:
                    def __init__(self):
                        self.rows = []
                    def save(self, invoice):
                        self.rows.append(invoice)

                inv = Invoice([("pen", 10, 3), ("pad", 25, 1)])
                print(TaxCalculator(0.18).total(inv), TaxCalculator(0.05).total(inv))
                print(HtmlRenderer().render(inv))
            ''', label="after"),
        ),
        section(
            "O: Open for extension, closed for modification",
            "Adding a new kind of thing should mean adding code, not editing working code. The tell-tale violation is a type switch (<code>if kind == ...</code>) that grows with every new kind and lives in several places.",
            code('''
                from abc import ABC, abstractmethod
                import math

                class Shape(ABC):
                    @abstractmethod
                    def area(self) -> float: ...

                class Circle(Shape):
                    def __init__(self, r): self.r = r
                    def area(self): return math.pi * self.r ** 2

                class Rect(Shape):
                    def __init__(self, w, h): self.w, self.h = w, h
                    def area(self): return self.w * self.h

                def total_area(shapes):                   # never changes when shapes are added
                    return round(sum(s.area() for s in shapes), 2)

                class Triangle(Shape):                    # extension: a new class only
                    def __init__(self, b, h): self.b, self.h = b, h
                    def area(self): return 0.5 * self.b * self.h

                print(total_area([Circle(1), Rect(2, 3), Triangle(4, 5)]))
            '''),
            "Strategy, Decorator, Observer, Visitor and Factory registries are all ways of making a specific kind of extension possible without modification.",
        ),
        section(
            "L: Liskov substitution",
            "Anything that works with a base class must keep working with any subclass. Subclasses may accept more and promise more, but never demand more or deliver less. The classic violation is a <code>Square</code> that inherits from <code>Rectangle</code>:",
            code('''
                class Rectangle:
                    def __init__(self, w, h):
                        self.w, self.h = w, h
                    def set_width(self, w):
                        self.w = w
                    def area(self):
                        return self.w * self.h

                class Square(Rectangle):
                    def __init__(self, side):
                        super().__init__(side, side)
                    def set_width(self, w):              # must keep sides equal...
                        self.w = self.h = w

                def stretch(rect: Rectangle):
                    rect.set_width(10)                    # caller's expectation: only width changes
                    return rect.area()

                print("Rectangle(2, 5):", stretch(Rectangle(2, 5)), "(expected 50)")
                print("Square(5):      ", stretch(Square(5)), "(expected 50 by the Rectangle contract)")
            '''),
            "Mathematically a square is a rectangle, but a <em>mutable</em> square does not honour a mutable rectangle's contract. Fixes: make shapes immutable (then <code>with_width</code> returns a new <code>Rectangle</code>), or do not relate them by inheritance at all. Other common violations: a subclass method that raises <code>NotImplementedError</code> for something the base promises (a <code>Penguin.fly()</code>), or one that tightens input rules.",
        ),
        section(
            "I: Interface segregation",
            "Clients should not depend on methods they do not use. A fat interface forces every implementation to stub out methods it cannot support, and those stubs are where Liskov violations come from.",
            code('''
                from typing import Protocol

                class Printer(Protocol):
                    def print(self, doc: str) -> str: ...

                class Scanner(Protocol):
                    def scan(self) -> str: ...

                class BasicPrinter:                          # only what it can do
                    def print(self, doc): return f"printed {doc!r}"

                class OfficeMachine:                         # implements both small interfaces
                    def print(self, doc): return f"printed {doc!r}"
                    def scan(self): return "scanned page"

                def print_all(p: Printer, docs):            # depends only on Printer
                    return [p.print(d) for d in docs]

                def archive(s: Scanner):
                    return s.scan()

                print(print_all(BasicPrinter(), ["a.pdf"]), archive(OfficeMachine()))
            '''),
            "In Python, <code>typing.Protocol</code> makes small interfaces cheap: a class satisfies a protocol just by having the methods, so splitting interfaces costs nothing at the implementation side.",
        ),
        section(
            "D: Dependency inversion",
            "High-level policy should not depend on low-level details; both should depend on an abstraction. Concretely: do not construct your collaborators inside a class; receive them. That makes the class testable with fakes and lets the detail change (SMTP to SMS, Postgres to an in-memory store) without touching the policy.",
            code('''
                from typing import Protocol

                class Notifier(Protocol):
                    def send(self, to: str, text: str) -> None: ...

                class OrderService:
                    def __init__(self, notifier: Notifier):          # injected, not constructed
                        self.notifier = notifier

                    def place(self, customer, item):
                        order_id = f"ord-{abs(hash((customer, item))) % 1000:03d}"
                        self.notifier.send(customer, f"order {item} placed")
                        return order_id

                class FakeNotifier:                                   # for tests
                    def __init__(self):
                        self.sent = []
                    def send(self, to, text):
                        self.sent.append((to, text))

                class SmsNotifier:
                    def send(self, to, text):
                        print(f"  SMS to {to}: {text}")

                fake = FakeNotifier()
                OrderService(fake).place("ann", "lamp")
                print("test saw:", fake.sent)
                OrderService(SmsNotifier()).place("bob", "desk")
            '''),
        ),
        section(
            "Composition over inheritance",
            "Inheritance fixes behaviour at class-definition time and couples the subclass to the parent's internals. Composition &mdash; holding a reference to an object that provides the behaviour &mdash; lets you mix behaviours freely and change them at run time. When two independent things vary, inheritance needs a subclass per combination; composition needs one class per variant of each.",
            code('''
                import itertools

                engines = ["petrol", "diesel", "electric"]
                bodies = ["sedan", "suv", "hatchback"]
                drives = ["fwd", "awd"]
                print("subclasses needed with inheritance:", len(list(itertools.product(engines, bodies, drives))))
                print("classes needed with composition:  ", len(engines) + len(bodies) + len(drives))

                class Car:
                    def __init__(self, engine, body, drive):
                        self.engine, self.body, self.drive = engine, body, drive
                    def describe(self):
                        return f"{self.body} / {self.engine} / {self.drive}"

                car = Car("petrol", "suv", "fwd")
                car.engine = "electric"                    # swap a part at run time
                print(car.describe())
            '''),
        ),
    ],
    questions=[
        question(
            "Give an example of a Liskov violation you might see in real code.",
            "medium",
            "A <code>ReadOnlyList(list)</code> subclass whose <code>append</code> raises: any function written for a <code>list</code> that appends now crashes. Or a <code>CachedRepository</code> subclass whose <code>save</code> silently does nothing until <code>flush()</code>, breaking callers that read back what they saved. The fix is the same: do not inherit when you cannot honour the parent's contract. Wrap the object instead (composition) and expose only the operations you support.",
        ),
        question(
            "How does dependency injection make code testable? Show it without a framework.",
            "medium",
            "Pass dependencies into the constructor instead of creating them inside. In tests, pass a fake that records calls or returns canned data; in production, pass the real implementation. No framework is needed in Python &mdash; a constructor parameter (often with a sensible default) is enough.",
            code('''
                import datetime as dt

                class Greeter:
                    def __init__(self, clock=dt.datetime.now):        # injectable clock
                        self.clock = clock
                    def greet(self, name):
                        hour = self.clock().hour
                        return f"Good {'morning' if hour < 12 else 'evening'}, {name}"

                print(Greeter(clock=lambda: dt.datetime(2026, 1, 1, 9)).greet("ann"))
                print(Greeter(clock=lambda: dt.datetime(2026, 1, 1, 20)).greet("ann"))
            '''),
        ),
        question(
            "Is a class with many small methods always better than one with a few big ones?",
            "medium",
            "No. SRP is about reasons to change, not size. Splitting a cohesive algorithm into ten classes that always change together adds indirection and no flexibility. Split along lines where things change independently or are reused independently; keep together what changes together. A good test: can you describe the class's job in one sentence without &ldquo;and&rdquo;?",
        ),
    ],
    refs=[
        ("Robert C. Martin: The principles of OOD", "http://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod"),
        ("Barbara Liskov and Jeannette Wing: A behavioral notion of subtyping", "https://dl.acm.org/doi/10.1145/197320.197383"),
        ("Python docs: typing.Protocol", "https://docs.python.org/3/library/typing.html#typing.Protocol"),
    ],
)
