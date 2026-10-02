from ._lld import code, table, note, caveat, section, question, PATTERNS_GROUP

TOPIC = dict(
    id="approach",
    title="How to Approach an LLD Interview",
    group=PATTERNS_GROUP,
    summary="The step-by-step method, how to find classes, and a signal-to-pattern table for choosing a design pattern.",
    intro=[
        "A low-level design (LLD) or machine-coding interview asks you to design the classes for something concrete &mdash; a parking lot, a vending machine, a cache &mdash; and usually to write working code for the core flow in 45&ndash;90 minutes. The interviewer is judging four things: do the classes have clear responsibilities, can the design absorb the change they are about to ask for, is the code correct and readable, and can you explain your choices.",
        "Design patterns are vocabulary for the second point. Each one is a known answer to a known kind of change. This page gives the method, then the most useful thing to memorise: <strong>which signal in a problem statement points to which pattern</strong>. The 35 design problems later in this section all follow this method.",
    ],
    sections=[
        section(
            "The method",
            table(
                ["Step", "What you do", "Output"],
                [
                    ["1. Clarify", "Ask about scope, actors, the core use cases and the likely extensions", "A short list of use cases and non-goals"],
                    ["2. Find entities", "Nouns in the use cases become candidate classes; verbs become methods", "Classes with one-line responsibilities"],
                    ["3. Relationships", "Who owns whom (composition), who uses whom (dependency), what is-a what (inheritance, sparingly)", "A rough class diagram"],
                    ["4. Find the axes of change", "What will vary: algorithms, states, types of things, notification channels", "The places that need a pattern"],
                    ["5. Apply patterns", "Pick the pattern that isolates each axis of change", "Interfaces and their implementations"],
                    ["6. Code the core flow", "Implement the main use case end to end, with a small demo", "Running code"],
                    ["7. Extend", "Walk through the interviewer's change and show which class absorbs it", "Proof the design is open for extension"],
                ],
            ),
            "Spend the first five minutes on step 1. &ldquo;Design a parking lot&rdquo; could mean one floor of cars or a multi-level garage with motorcycles, buses, EV charging, hourly pricing and multiple entry gates. The difference is half the design.",
            note("Patterns come <em>after</em> you know what varies. Starting with &ldquo;I will use a Factory and a Singleton&rdquo; before understanding the problem is the most common way to fail an LLD round."),
        ),
        section(
            "Finding classes from the problem statement",
            "A simple mechanical technique gets you a first draft: underline nouns (candidate classes or attributes) and verbs (candidate methods). Then prune: a noun with no behaviour and no identity is an attribute, not a class.",
            code('''
                import re

                statement = """A library lends books to members. A member can borrow up to five books.
                Each book copy has a barcode. Members can reserve a book that is on loan and are
                notified when it is returned. Late returns are charged a fine per day."""

                nouns = {"library", "book", "member", "copy", "barcode", "loan", "fine", "day", "reservation"}
                verbs = {"lends", "borrow", "reserve", "notified", "returned", "charged"}

                words = re.findall(r"[a-z]+", statement.lower())
                found_nouns = sorted({w.rstrip("s") for w in words if w.rstrip("s") in nouns})
                found_verbs = sorted({w for w in words if w in verbs})
                print("candidate classes:", found_nouns)
                print("candidate methods:", found_verbs)
            '''),
            "After pruning: <code>Library</code> (facade over the use cases), <code>Book</code> (title, author) and <code>BookCopy</code> (barcode, status) are separate because several copies share one book; <code>Member</code>; <code>Loan</code> (copy, member, due date) because it has its own lifecycle; <code>Reservation</code>; a <code>FinePolicy</code> because the fine rule is likely to change. <code>day</code> and <code>barcode</code> are attributes.",
        ),
        section(
            "Choosing a pattern: signal to pattern",
            "Read the problem for these phrases. Each one names an axis of change, and each axis has a standard pattern that isolates it.",
            table(
                ["Signal in the problem", "Pattern", "What it isolates"],
                [
                    ["&ldquo;different ways to&hellip;&rdquo; calculate price, choose a spot, split a bill, match a driver", "<strong>Strategy</strong>", "An interchangeable algorithm"],
                    ["Behaviour depends on the current status; idle/selecting/dispensing; order lifecycle", "<strong>State</strong>", "State-specific behaviour and legal transitions"],
                    ["&ldquo;notify&rdquo;, &ldquo;subscribe&rdquo;, &ldquo;when X happens, update Y and Z&rdquo;", "<strong>Observer</strong>", "Who reacts to an event"],
                    ["Undo/redo, queue or log of actions, macros", "<strong>Command</strong> (+ Memento)", "An action as an object"],
                    ["Request passes through several handlers, each may handle or pass on: approvals, middleware, cash denominations", "<strong>Chain of Responsibility</strong>", "Which handler deals with a request"],
                    ["Add-ons that stack: toppings, features, wrappers (logging, retry, caching)", "<strong>Decorator</strong>", "Optional behaviour added at run time"],
                    ["Tree of parts and wholes treated uniformly: files/folders, menus, org charts, expressions", "<strong>Composite</strong>", "Leaf vs container"],
                    ["Integrate a third-party or legacy API with a different interface", "<strong>Adapter</strong>", "Interface mismatch"],
                    ["Simple front for a complex subsystem", "<strong>Facade</strong>", "Subsystem complexity"],
                    ["Create objects without the caller knowing the concrete class; &ldquo;types of&hellip;&rdquo; vehicles, payments", "<strong>Factory</strong> (method / registry)", "Which class gets instantiated"],
                    ["Families of related objects that must match (UI theme, cloud provider)", "<strong>Abstract Factory</strong>", "Which family"],
                    ["Many optional parameters, step-by-step construction, fluent API", "<strong>Builder</strong>", "Complex construction"],
                    ["Copy a configured object instead of building from scratch", "<strong>Prototype</strong>", "Costly or complex setup"],
                    ["Exactly one shared instance: config, registry, connection manager", "<strong>Singleton</strong> (or a module)", "Global access to one instance"],
                    ["Same algorithm skeleton, steps differ by subtype", "<strong>Template Method</strong>", "The varying steps"],
                    ["New operations over a fixed set of node types (export, evaluate, print)", "<strong>Visitor</strong>", "Operations vs data structure"],
                    ["Control access, lazy load, cache, or add checks in front of an object", "<strong>Proxy</strong>", "Access to the real object"],
                    ["Many objects talk to each other; centralise the coordination (chat room, air traffic)", "<strong>Mediator</strong>", "Many-to-many communication"],
                    ["Save and restore state without exposing internals", "<strong>Memento</strong>", "Snapshots"],
                    ["Expensive resources reused: connections, threads", "<strong>Object Pool</strong>", "Resource lifecycle"],
                    ["Huge number of similar objects sharing data (glyphs, map tiles)", "<strong>Flyweight</strong>", "Shared intrinsic state"],
                ],
            ),
        ),
        section(
            "A worked mini-example: from requirement to pattern",
            "&ldquo;Shipping cost depends on the carrier; we will add carriers every quarter.&rdquo; The signal is &ldquo;depends on&hellip; we will add&rdquo;: an algorithm that varies and grows. The naive version is an if-chain that every new carrier edits:",
            code('''
                def shipping_cost(carrier, weight_kg, distance_km):
                    if carrier == "fedex":
                        return 5 + 1.2 * weight_kg
                    elif carrier == "ups":
                        return 4 + 0.9 * weight_kg + 0.01 * distance_km
                    elif carrier == "local":
                        return 2 + 0.05 * distance_km
                    raise ValueError(carrier)          # every new carrier edits this function

                print(shipping_cost("ups", 10, 300))
            '''),
            "Strategy plus a registry: each carrier is its own class with one method, and adding a carrier adds a class without touching existing code (the Open/Closed principle).",
            code('''
                from typing import Protocol

                class Carrier(Protocol):
                    def cost(self, weight_kg: float, distance_km: float) -> float: ...

                CARRIERS: dict[str, Carrier] = {}

                def register(name):
                    def wrap(cls):
                        CARRIERS[name] = cls()
                        return cls
                    return wrap

                @register("fedex")
                class FedEx:
                    def cost(self, w, d): return 5 + 1.2 * w

                @register("ups")
                class UPS:
                    def cost(self, w, d): return 4 + 0.9 * w + 0.01 * d

                @register("drone")                       # added next quarter: nothing else changes
                class Drone:
                    def cost(self, w, d):
                        if w > 2:
                            raise ValueError("drone limit is 2 kg")
                        return 10 + 0.5 * d

                def cheapest(weight, distance):
                    options = {}
                    for name, c in CARRIERS.items():
                        try:
                            options[name] = c.cost(weight, distance)
                        except ValueError:
                            pass
                    return min(options.items(), key=lambda kv: kv[1])

                print(sorted((n, round(c.cost(1.5, 12), 2)) for n, c in CARRIERS.items()))
                print("cheapest for 1.5 kg, 12 km:", cheapest(1.5, 12))
                print("cheapest for 10 kg, 300 km:", cheapest(10, 300))
            '''),
        ),
        section(
            "Pythonic patterns: lighter than the textbook",
            "Most classic patterns were written for languages without first-class functions. In Python several collapse into something smaller, and an interviewer is happy to hear you say so &mdash; as long as you can also show the class-based version when asked.",
            table(
                ["Pattern", "Textbook form", "Often enough in Python"],
                [
                    ["Strategy", "Interface + one class per algorithm", "A function, or a dict of functions"],
                    ["Command", "Command interface with <code>execute()</code>", "A callable or <code>functools.partial</code>; a class when you need <code>undo()</code>"],
                    ["Singleton", "Private constructor + <code>getInstance()</code>", "A module-level instance (modules are created once)"],
                    ["Factory", "Factory class hierarchy", "A <code>classmethod</code> constructor or a dict registry"],
                    ["Iterator", "Iterator class", "A generator"],
                    ["Decorator (structural)", "Wrapper class implementing the same interface", "Still a class when wrapping objects; <code>@decorator</code> when wrapping functions"],
                    ["Observer", "Subject / Observer interfaces", "A list of callbacks"],
                    ["Template Method", "Abstract base class with hook methods", "Same, or pass the varying step as a function"],
                ],
            ),
            caveat("Do not over-pattern. A tic-tac-toe game needs no Abstract Factory. Use a pattern where you can name the change it protects against; otherwise plain classes and functions are the better design."),
        ),
        section(
            "What good LLD code looks like in Python",
            "Use <code>dataclass</code> for entities, <code>Enum</code> for fixed sets (vehicle types, states), <code>Protocol</code> or <code>ABC</code> for the seams where implementations vary, and dependency injection (pass collaborators into <code>__init__</code>) so each class can be tested alone. Keep I/O at the edges: core classes return values and raise exceptions; the demo prints.",
            code('''
                from abc import ABC, abstractmethod
                from dataclasses import dataclass, field
                from enum import Enum

                class Size(Enum):
                    SMALL = 1
                    LARGE = 2

                @dataclass
                class Item:
                    name: str
                    size: Size

                class Storage(ABC):                       # the seam: implementations vary
                    @abstractmethod
                    def fits(self, item: Item) -> bool: ...

                class Locker(Storage):
                    def fits(self, item):
                        return item.size is Size.SMALL

                @dataclass
                class Warehouse:
                    storages: list[Storage]               # injected, so tests can pass fakes
                    stored: list[str] = field(default_factory=list)

                    def store(self, item: Item) -> bool:
                        if any(s.fits(item) for s in self.storages):
                            self.stored.append(item.name)
                            return True
                        return False

                w = Warehouse([Locker()])
                print(w.store(Item("phone", Size.SMALL)), w.store(Item("sofa", Size.LARGE)), w.stored)
            '''),
        ),
    ],
    questions=[
        question(
            "The interviewer says &ldquo;design a parking lot&rdquo; and nothing else. What do you ask?",
            "medium",
            "Scope: how many floors and entry/exit gates? Which vehicle types (motorcycle, car, bus, EV) and spot types, and can a small vehicle use a larger spot? How is pricing done (flat, hourly, by spot type, peak hours)? Payment methods? Is there a display of free spots per floor? Do we need reservations? Is it one lot or a chain? Then state assumptions explicitly and confirm: &ldquo;I will design for multiple floors, three vehicle types, hourly pricing that may change, and gates that issue tickets. Reservations are out of scope.&rdquo;",
        ),
        question(
            "When is inheritance the wrong tool, and what do you use instead?",
            "medium",
            "When the subclasses would differ along more than one axis, or when the variation can change at run time. A <code>Duck</code> hierarchy that varies by both flying and quacking behaviour explodes into a class per combination; a car whose pricing changes during peak hours cannot change its class. Use composition: give the object a strategy or state object for each axis of variation, and swap it. Keep inheritance for genuine is-a relationships with a stable shared interface (every <code>Shape</code> has an area).",
        ),
        question(
            "How do you show your design is &ldquo;extensible&rdquo; without over-engineering it?",
            "hard",
            "Identify the two or three most likely changes (from the problem statement and your clarifying questions) and put a seam &mdash; an interface with one implementation today &mdash; exactly there, and nowhere else. Then demonstrate: when the interviewer asks for a new pricing rule, a new vehicle type or a new notification channel, show that the change is one new class plus one registration line, with no edits to existing classes. Everything that is not a likely axis of change stays concrete and simple; it can be refactored when a real need appears.",
        ),
    ],
    refs=[
        ("Refactoring.Guru: Design patterns catalog", "https://refactoring.guru/design-patterns/catalog"),
        ("Brandon Rhodes: Python design patterns", "https://python-patterns.guide/"),
        ("Gamma, Helm, Johnson, Vlissides: Design Patterns (1994)", "https://en.wikipedia.org/wiki/Design_Patterns"),
    ],
)
