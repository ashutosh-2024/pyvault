/* GENERATED FILE - do not edit by hand.
   Source: content/lld/   Build: python3 build.py
   Every code block below was executed and its output captured. */

window.GRAIL_LLD = [
  {
    "id": "approach",
    "title": "How to Approach an LLD Interview",
    "group": "Patterns",
    "tags": [],
    "level": null,
    "summary": "The step-by-step method, how to find classes, and a signal-to-pattern table for choosing a design pattern.",
    "intro": [
      "A low-level design (LLD) or machine-coding interview asks you to design the classes for something concrete &mdash; a parking lot, a vending machine, a cache &mdash; and usually to write working code for the core flow in 45&ndash;90 minutes. The interviewer is judging four things: do the classes have clear responsibilities, can the design absorb the change they are about to ask for, is the code correct and readable, and can you explain your choices.",
      "Design patterns are vocabulary for the second point. Each one is a known answer to a known kind of change. This page gives the method, then the most useful thing to memorise: <strong>which signal in a problem statement points to which pattern</strong>. The 35 design problems later in this section all follow this method."
    ],
    "sections": [
      {
        "title": "The method",
        "body": [
          {
            "type": "table",
            "head": [
              "Step",
              "What you do",
              "Output"
            ],
            "rows": [
              [
                "1. Clarify",
                "Ask about scope, actors, the core use cases and the likely extensions",
                "A short list of use cases and non-goals"
              ],
              [
                "2. Find entities",
                "Nouns in the use cases become candidate classes; verbs become methods",
                "Classes with one-line responsibilities"
              ],
              [
                "3. Relationships",
                "Who owns whom (composition), who uses whom (dependency), what is-a what (inheritance, sparingly)",
                "A rough class diagram"
              ],
              [
                "4. Find the axes of change",
                "What will vary: algorithms, states, types of things, notification channels",
                "The places that need a pattern"
              ],
              [
                "5. Apply patterns",
                "Pick the pattern that isolates each axis of change",
                "Interfaces and their implementations"
              ],
              [
                "6. Code the core flow",
                "Implement the main use case end to end, with a small demo",
                "Running code"
              ],
              [
                "7. Extend",
                "Walk through the interviewer's change and show which class absorbs it",
                "Proof the design is open for extension"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Spend the first five minutes on step 1. &ldquo;Design a parking lot&rdquo; could mean one floor of cars or a multi-level garage with motorcycles, buses, EV charging, hourly pricing and multiple entry gates. The difference is half the design."
          },
          {
            "type": "note",
            "text": "Patterns come <em>after</em> you know what varies. Starting with &ldquo;I will use a Factory and a Singleton&rdquo; before understanding the problem is the most common way to fail an LLD round."
          }
        ]
      },
      {
        "title": "Finding classes from the problem statement",
        "body": [
          {
            "type": "p",
            "html": "A simple mechanical technique gets you a first draft: underline nouns (candidate classes or attributes) and verbs (candidate methods). Then prune: a noun with no behaviour and no identity is an attribute, not a class."
          },
          {
            "type": "code",
            "src": "import re\n\nstatement = \"\"\"A library lends books to members. A member can borrow up to five books.\nEach book copy has a barcode. Members can reserve a book that is on loan and are\nnotified when it is returned. Late returns are charged a fine per day.\"\"\"\n\nnouns = {\"library\", \"book\", \"member\", \"copy\", \"barcode\", \"loan\", \"fine\", \"day\", \"reservation\"}\nverbs = {\"lends\", \"borrow\", \"reserve\", \"notified\", \"returned\", \"charged\"}\n\nwords = re.findall(r\"[a-z]+\", statement.lower())\nfound_nouns = sorted({w.rstrip(\"s\") for w in words if w.rstrip(\"s\") in nouns})\nfound_verbs = sorted({w for w in words if w in verbs})\nprint(\"candidate classes:\", found_nouns)\nprint(\"candidate methods:\", found_verbs)",
            "label": null,
            "output": "candidate classes: ['barcode', 'book', 'copy', 'day', 'fine', 'library', 'loan', 'member']\ncandidate methods: ['borrow', 'charged', 'lends', 'notified', 'reserve', 'returned']",
            "isError": false
          },
          {
            "type": "p",
            "html": "After pruning: <code>Library</code> (facade over the use cases), <code>Book</code> (title, author) and <code>BookCopy</code> (barcode, status) are separate because several copies share one book; <code>Member</code>; <code>Loan</code> (copy, member, due date) because it has its own lifecycle; <code>Reservation</code>; a <code>FinePolicy</code> because the fine rule is likely to change. <code>day</code> and <code>barcode</code> are attributes."
          }
        ]
      },
      {
        "title": "Choosing a pattern: signal to pattern",
        "body": [
          {
            "type": "p",
            "html": "Read the problem for these phrases. Each one names an axis of change, and each axis has a standard pattern that isolates it."
          },
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "What it isolates"
            ],
            "rows": [
              [
                "&ldquo;different ways to&hellip;&rdquo; calculate price, choose a spot, split a bill, match a driver",
                "<strong>Strategy</strong>",
                "An interchangeable algorithm"
              ],
              [
                "Behaviour depends on the current status; idle/selecting/dispensing; order lifecycle",
                "<strong>State</strong>",
                "State-specific behaviour and legal transitions"
              ],
              [
                "&ldquo;notify&rdquo;, &ldquo;subscribe&rdquo;, &ldquo;when X happens, update Y and Z&rdquo;",
                "<strong>Observer</strong>",
                "Who reacts to an event"
              ],
              [
                "Undo/redo, queue or log of actions, macros",
                "<strong>Command</strong> (+ Memento)",
                "An action as an object"
              ],
              [
                "Request passes through several handlers, each may handle or pass on: approvals, middleware, cash denominations",
                "<strong>Chain of Responsibility</strong>",
                "Which handler deals with a request"
              ],
              [
                "Add-ons that stack: toppings, features, wrappers (logging, retry, caching)",
                "<strong>Decorator</strong>",
                "Optional behaviour added at run time"
              ],
              [
                "Tree of parts and wholes treated uniformly: files/folders, menus, org charts, expressions",
                "<strong>Composite</strong>",
                "Leaf vs container"
              ],
              [
                "Integrate a third-party or legacy API with a different interface",
                "<strong>Adapter</strong>",
                "Interface mismatch"
              ],
              [
                "Simple front for a complex subsystem",
                "<strong>Facade</strong>",
                "Subsystem complexity"
              ],
              [
                "Create objects without the caller knowing the concrete class; &ldquo;types of&hellip;&rdquo; vehicles, payments",
                "<strong>Factory</strong> (method / registry)",
                "Which class gets instantiated"
              ],
              [
                "Families of related objects that must match (UI theme, cloud provider)",
                "<strong>Abstract Factory</strong>",
                "Which family"
              ],
              [
                "Many optional parameters, step-by-step construction, fluent API",
                "<strong>Builder</strong>",
                "Complex construction"
              ],
              [
                "Copy a configured object instead of building from scratch",
                "<strong>Prototype</strong>",
                "Costly or complex setup"
              ],
              [
                "Exactly one shared instance: config, registry, connection manager",
                "<strong>Singleton</strong> (or a module)",
                "Global access to one instance"
              ],
              [
                "Same algorithm skeleton, steps differ by subtype",
                "<strong>Template Method</strong>",
                "The varying steps"
              ],
              [
                "New operations over a fixed set of node types (export, evaluate, print)",
                "<strong>Visitor</strong>",
                "Operations vs data structure"
              ],
              [
                "Control access, lazy load, cache, or add checks in front of an object",
                "<strong>Proxy</strong>",
                "Access to the real object"
              ],
              [
                "Many objects talk to each other; centralise the coordination (chat room, air traffic)",
                "<strong>Mediator</strong>",
                "Many-to-many communication"
              ],
              [
                "Save and restore state without exposing internals",
                "<strong>Memento</strong>",
                "Snapshots"
              ],
              [
                "Expensive resources reused: connections, threads",
                "<strong>Object Pool</strong>",
                "Resource lifecycle"
              ],
              [
                "Huge number of similar objects sharing data (glyphs, map tiles)",
                "<strong>Flyweight</strong>",
                "Shared intrinsic state"
              ]
            ]
          }
        ]
      },
      {
        "title": "A worked mini-example: from requirement to pattern",
        "body": [
          {
            "type": "p",
            "html": "&ldquo;Shipping cost depends on the carrier; we will add carriers every quarter.&rdquo; The signal is &ldquo;depends on&hellip; we will add&rdquo;: an algorithm that varies and grows. The naive version is an if-chain that every new carrier edits:"
          },
          {
            "type": "code",
            "src": "def shipping_cost(carrier, weight_kg, distance_km):\n    if carrier == \"fedex\":\n        return 5 + 1.2 * weight_kg\n    elif carrier == \"ups\":\n        return 4 + 0.9 * weight_kg + 0.01 * distance_km\n    elif carrier == \"local\":\n        return 2 + 0.05 * distance_km\n    raise ValueError(carrier)          # every new carrier edits this function\n\nprint(shipping_cost(\"ups\", 10, 300))",
            "label": null,
            "output": "16.0",
            "isError": false
          },
          {
            "type": "p",
            "html": "Strategy plus a registry: each carrier is its own class with one method, and adding a carrier adds a class without touching existing code (the Open/Closed principle)."
          },
          {
            "type": "code",
            "src": "from typing import Protocol\n\nclass Carrier(Protocol):\n    def cost(self, weight_kg: float, distance_km: float) -> float: ...\n\nCARRIERS: dict[str, Carrier] = {}\n\ndef register(name):\n    def wrap(cls):\n        CARRIERS[name] = cls()\n        return cls\n    return wrap\n\n@register(\"fedex\")\nclass FedEx:\n    def cost(self, w, d): return 5 + 1.2 * w\n\n@register(\"ups\")\nclass UPS:\n    def cost(self, w, d): return 4 + 0.9 * w + 0.01 * d\n\n@register(\"drone\")                       # added next quarter: nothing else changes\nclass Drone:\n    def cost(self, w, d):\n        if w > 2:\n            raise ValueError(\"drone limit is 2 kg\")\n        return 10 + 0.5 * d\n\ndef cheapest(weight, distance):\n    options = {}\n    for name, c in CARRIERS.items():\n        try:\n            options[name] = c.cost(weight, distance)\n        except ValueError:\n            pass\n    return min(options.items(), key=lambda kv: kv[1])\n\nprint(sorted((n, round(c.cost(1.5, 12), 2)) for n, c in CARRIERS.items()))\nprint(\"cheapest for 1.5 kg, 12 km:\", cheapest(1.5, 12))\nprint(\"cheapest for 10 kg, 300 km:\", cheapest(10, 300))",
            "label": null,
            "output": "[('drone', 16.0), ('fedex', 6.8), ('ups', 5.47)]\ncheapest for 1.5 kg, 12 km: ('ups', 5.47)\ncheapest for 10 kg, 300 km: ('ups', 16.0)",
            "isError": false
          }
        ]
      },
      {
        "title": "Pythonic patterns: lighter than the textbook",
        "body": [
          {
            "type": "p",
            "html": "Most classic patterns were written for languages without first-class functions. In Python several collapse into something smaller, and an interviewer is happy to hear you say so &mdash; as long as you can also show the class-based version when asked."
          },
          {
            "type": "table",
            "head": [
              "Pattern",
              "Textbook form",
              "Often enough in Python"
            ],
            "rows": [
              [
                "Strategy",
                "Interface + one class per algorithm",
                "A function, or a dict of functions"
              ],
              [
                "Command",
                "Command interface with <code>execute()</code>",
                "A callable or <code>functools.partial</code>; a class when you need <code>undo()</code>"
              ],
              [
                "Singleton",
                "Private constructor + <code>getInstance()</code>",
                "A module-level instance (modules are created once)"
              ],
              [
                "Factory",
                "Factory class hierarchy",
                "A <code>classmethod</code> constructor or a dict registry"
              ],
              [
                "Iterator",
                "Iterator class",
                "A generator"
              ],
              [
                "Decorator (structural)",
                "Wrapper class implementing the same interface",
                "Still a class when wrapping objects; <code>@decorator</code> when wrapping functions"
              ],
              [
                "Observer",
                "Subject / Observer interfaces",
                "A list of callbacks"
              ],
              [
                "Template Method",
                "Abstract base class with hook methods",
                "Same, or pass the varying step as a function"
              ]
            ]
          },
          {
            "type": "caveat",
            "text": "Do not over-pattern. A tic-tac-toe game needs no Abstract Factory. Use a pattern where you can name the change it protects against; otherwise plain classes and functions are the better design."
          }
        ]
      },
      {
        "title": "What good LLD code looks like in Python",
        "body": [
          {
            "type": "p",
            "html": "Use <code>dataclass</code> for entities, <code>Enum</code> for fixed sets (vehicle types, states), <code>Protocol</code> or <code>ABC</code> for the seams where implementations vary, and dependency injection (pass collaborators into <code>__init__</code>) so each class can be tested alone. Keep I/O at the edges: core classes return values and raise exceptions; the demo prints."
          },
          {
            "type": "code",
            "src": "from abc import ABC, abstractmethod\nfrom dataclasses import dataclass, field\nfrom enum import Enum\n\nclass Size(Enum):\n    SMALL = 1\n    LARGE = 2\n\n@dataclass\nclass Item:\n    name: str\n    size: Size\n\nclass Storage(ABC):                       # the seam: implementations vary\n    @abstractmethod\n    def fits(self, item: Item) -> bool: ...\n\nclass Locker(Storage):\n    def fits(self, item):\n        return item.size is Size.SMALL\n\n@dataclass\nclass Warehouse:\n    storages: list[Storage]               # injected, so tests can pass fakes\n    stored: list[str] = field(default_factory=list)\n\n    def store(self, item: Item) -> bool:\n        if any(s.fits(item) for s in self.storages):\n            self.stored.append(item.name)\n            return True\n        return False\n\nw = Warehouse([Locker()])\nprint(w.store(Item(\"phone\", Size.SMALL)), w.store(Item(\"sofa\", Size.LARGE)), w.stored)",
            "label": null,
            "output": "True False ['phone']",
            "isError": false
          }
        ]
      },
      {
        "title": "Practise each pattern",
        "body": [
          {
            "type": "p",
            "html": "The 35 design problems in this section, grouped by the patterns their solutions use. Strategy and Observer dominate because most interview problems are about something that varies and something that reacts; use the filter on the section index to open them by pattern."
          },
          {
            "type": "table",
            "head": [
              "Pattern",
              "Problems",
              "Where it appears"
            ],
            "rows": [
              [
                "<strong>Strategy</strong>",
                "20",
                "Parking Lot, Elevator System, Library Management System, Movie Ticket Booking System, Hotel Reservation System, Meeting Room Scheduler, Splitwise (Expense Sharing), Ride-Sharing Service (Uber), Tic-Tac-Toe, Snakes and Ladders, Chess Game, Online Auction System, LRU / LFU Cache, Logging Framework, Notification Service, Task Scheduler, Payment Processing Module, Shopping Cart with Discount Rules, Food Delivery Order Lifecycle, Plugin System"
              ],
              [
                "<strong>Observer</strong>",
                "12",
                "Library Management System, Movie Ticket Booking System, Meeting Room Scheduler, Ride-Sharing Service (Uber), Live Cricket Scoreboard, Online Auction System, Logging Framework, In-Memory Pub/Sub Message Broker, Food Delivery Order Lifecycle, Traffic Light Controller, Plugin System, Drawing Application"
              ],
              [
                "<strong>State</strong>",
                "9",
                "Elevator System, Vending Machine, ATM, Movie Ticket Booking System, Ride-Sharing Service (Uber), Online Auction System, Payment Processing Module, Food Delivery Order Lifecycle, Traffic Light Controller"
              ],
              [
                "<strong>Factory</strong>",
                "8",
                "Parking Lot, Hotel Reservation System, Splitwise (Expense Sharing), Chess Game, Notification Service, Database Connection Pool, Payment Processing Module, Plugin System"
              ],
              [
                "<strong>Command</strong>",
                "7",
                "Elevator System, Chess Game, Live Cricket Scoreboard, Task Scheduler, Key-Value Store with Nested Transactions, Text Editor with Undo/Redo, Drawing Application"
              ],
              [
                "<strong>Composite</strong>",
                "6",
                "In-Memory File System, Shopping Cart with Discount Rules, Document Model with Multiple Export Formats, Expression Evaluator (Calculator), SQL Query Builder, Drawing Application"
              ],
              [
                "<strong>Builder</strong>",
                "4",
                "Snakes and Ladders, Coffee / Pizza Ordering System with Add-ons, Document Model with Multiple Export Formats, SQL Query Builder"
              ],
              [
                "<strong>Chain of Responsibility</strong>",
                "4",
                "ATM, Logging Framework, Shopping Cart with Discount Rules, HTTP Middleware Pipeline"
              ],
              [
                "<strong>Decorator</strong>",
                "4",
                "LRU / LFU Cache, Notification Service, Coffee / Pizza Ordering System with Add-ons, HTTP Middleware Pipeline"
              ],
              [
                "<strong>Interpreter</strong>",
                "2",
                "Expression Evaluator (Calculator), SQL Query Builder"
              ],
              [
                "<strong>Memento</strong>",
                "2",
                "Key-Value Store with Nested Transactions, Text Editor with Undo/Redo"
              ],
              [
                "<strong>Repository</strong>",
                "2",
                "Library Management System, Hotel Reservation System"
              ],
              [
                "<strong>Singleton</strong>",
                "2",
                "Parking Lot, Logging Framework"
              ],
              [
                "<strong>Visitor</strong>",
                "2",
                "Document Model with Multiple Export Formats, Expression Evaluator (Calculator)"
              ],
              [
                "<strong>Adapter</strong>",
                "1",
                "Payment Processing Module"
              ],
              [
                "<strong>Facade</strong>",
                "1",
                "ATM"
              ],
              [
                "<strong>Iterator</strong>",
                "1",
                "In-Memory File System"
              ],
              [
                "<strong>Mediator</strong>",
                "1",
                "In-Memory Pub/Sub Message Broker"
              ],
              [
                "<strong>Object Pool</strong>",
                "1",
                "Database Connection Pool"
              ],
              [
                "<strong>Prototype</strong>",
                "1",
                "Drawing Application"
              ],
              [
                "<strong>Proxy</strong>",
                "1",
                "Database Connection Pool"
              ],
              [
                "<strong>Template Method</strong>",
                "1",
                "Notification Service"
              ]
            ]
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "The interviewer says &ldquo;design a parking lot&rdquo; and nothing else. What do you ask?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Scope: how many floors and entry/exit gates? Which vehicle types (motorcycle, car, bus, EV) and spot types, and can a small vehicle use a larger spot? How is pricing done (flat, hourly, by spot type, peak hours)? Payment methods? Is there a display of free spots per floor? Do we need reservations? Is it one lot or a chain? Then state assumptions explicitly and confirm: &ldquo;I will design for multiple floors, three vehicle types, hourly pricing that may change, and gates that issue tickets. Reservations are out of scope.&rdquo;"
          }
        ]
      },
      {
        "q": "When is inheritance the wrong tool, and what do you use instead?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "When the subclasses would differ along more than one axis, or when the variation can change at run time. A <code>Duck</code> hierarchy that varies by both flying and quacking behaviour explodes into a class per combination; a car whose pricing changes during peak hours cannot change its class. Use composition: give the object a strategy or state object for each axis of variation, and swap it. Keep inheritance for genuine is-a relationships with a stable shared interface (every <code>Shape</code> has an area)."
          }
        ]
      },
      {
        "q": "How do you show your design is &ldquo;extensible&rdquo; without over-engineering it?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Identify the two or three most likely changes (from the problem statement and your clarifying questions) and put a seam &mdash; an interface with one implementation today &mdash; exactly there, and nowhere else. Then demonstrate: when the interviewer asks for a new pricing rule, a new vehicle type or a new notification channel, show that the change is one new class plus one registration line, with no edits to existing classes. Everything that is not a likely axis of change stays concrete and simple; it can be refactored when a real need appears."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Refactoring.Guru: Design patterns catalog",
        "url": "https://refactoring.guru/design-patterns/catalog"
      },
      {
        "label": "Brandon Rhodes: Python design patterns",
        "url": "https://python-patterns.guide/"
      },
      {
        "label": "Gamma, Helm, Johnson, Vlissides: Design Patterns (1994)",
        "url": "https://en.wikipedia.org/wiki/Design_Patterns"
      }
    ]
  },
  {
    "id": "solid",
    "title": "SOLID and OOP Principles in Python",
    "group": "Patterns",
    "tags": [],
    "level": null,
    "summary": "Single responsibility, open/closed, Liskov, interface segregation, dependency inversion - each shown broken, then fixed.",
    "intro": [
      "SOLID is five rules for keeping classes easy to change. Design patterns are mostly SOLID applied to a specific recurring problem, so if you understand why each principle exists, you can usually derive the pattern instead of memorising it.",
      "Each principle below starts with code that violates it, shows the concrete problem that causes, then fixes it."
    ],
    "sections": [
      {
        "title": "S: Single responsibility",
        "body": [
          {
            "type": "p",
            "html": "A class should have one reason to change. &ldquo;Reason to change&rdquo; means a stakeholder or concern: tax rules, report formatting, storage. A class that mixes them must be edited (and retested) for every one of those concerns."
          },
          {
            "type": "code",
            "src": "class Invoice:                                  # three reasons to change\n    def __init__(self, items):\n        self.items = items                      # [(name, price, qty)]\n\n    def total(self):                            # pricing rules\n        return sum(p * q for _, p, q in self.items) * 1.18\n\n    def to_html(self):                          # presentation\n        return \"<ul>\" + \"\".join(f\"<li>{n}</li>\" for n, _, _ in self.items) + \"</ul>\"\n\n    def save(self, db):                         # persistence\n        db.append(self.items)\n\nprint(Invoice([(\"pen\", 10, 3)]).total())",
            "label": "before",
            "output": "35.4",
            "isError": false
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass\nclass Invoice:                                  # data + its own invariants only\n    items: list\n\n    def subtotal(self):\n        return sum(p * q for _, p, q in self.items)\n\nclass TaxCalculator:\n    def __init__(self, rate):\n        self.rate = rate\n    def total(self, invoice):\n        return round(invoice.subtotal() * (1 + self.rate), 2)\n\nclass HtmlRenderer:\n    def render(self, invoice):\n        return \"<ul>\" + \"\".join(f\"<li>{n} x{q}</li>\" for n, _, q in invoice.items) + \"</ul>\"\n\nclass InvoiceRepository:\n    def __init__(self):\n        self.rows = []\n    def save(self, invoice):\n        self.rows.append(invoice)\n\ninv = Invoice([(\"pen\", 10, 3), (\"pad\", 25, 1)])\nprint(TaxCalculator(0.18).total(inv), TaxCalculator(0.05).total(inv))\nprint(HtmlRenderer().render(inv))",
            "label": "after",
            "output": "64.9 57.75\n<ul><li>pen x3</li><li>pad x1</li></ul>",
            "isError": false
          }
        ]
      },
      {
        "title": "O: Open for extension, closed for modification",
        "body": [
          {
            "type": "p",
            "html": "Adding a new kind of thing should mean adding code, not editing working code. The tell-tale violation is a type switch (<code>if kind == ...</code>) that grows with every new kind and lives in several places."
          },
          {
            "type": "code",
            "src": "from abc import ABC, abstractmethod\nimport math\n\nclass Shape(ABC):\n    @abstractmethod\n    def area(self) -> float: ...\n\nclass Circle(Shape):\n    def __init__(self, r): self.r = r\n    def area(self): return math.pi * self.r ** 2\n\nclass Rect(Shape):\n    def __init__(self, w, h): self.w, self.h = w, h\n    def area(self): return self.w * self.h\n\ndef total_area(shapes):                   # never changes when shapes are added\n    return round(sum(s.area() for s in shapes), 2)\n\nclass Triangle(Shape):                    # extension: a new class only\n    def __init__(self, b, h): self.b, self.h = b, h\n    def area(self): return 0.5 * self.b * self.h\n\nprint(total_area([Circle(1), Rect(2, 3), Triangle(4, 5)]))",
            "label": null,
            "output": "19.14",
            "isError": false
          },
          {
            "type": "p",
            "html": "Strategy, Decorator, Observer, Visitor and Factory registries are all ways of making a specific kind of extension possible without modification."
          }
        ]
      },
      {
        "title": "L: Liskov substitution",
        "body": [
          {
            "type": "p",
            "html": "Anything that works with a base class must keep working with any subclass. Subclasses may accept more and promise more, but never demand more or deliver less. The classic violation is a <code>Square</code> that inherits from <code>Rectangle</code>:"
          },
          {
            "type": "code",
            "src": "class Rectangle:\n    def __init__(self, w, h):\n        self.w, self.h = w, h\n    def set_width(self, w):\n        self.w = w\n    def area(self):\n        return self.w * self.h\n\nclass Square(Rectangle):\n    def __init__(self, side):\n        super().__init__(side, side)\n    def set_width(self, w):              # must keep sides equal...\n        self.w = self.h = w\n\ndef stretch(rect: Rectangle):\n    rect.set_width(10)                    # caller's expectation: only width changes\n    return rect.area()\n\nprint(\"Rectangle(2, 5):\", stretch(Rectangle(2, 5)), \"(expected 50)\")\nprint(\"Square(5):      \", stretch(Square(5)), \"(expected 50 by the Rectangle contract)\")",
            "label": null,
            "output": "Rectangle(2, 5): 50 (expected 50)\nSquare(5):       100 (expected 50 by the Rectangle contract)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Mathematically a square is a rectangle, but a <em>mutable</em> square does not honour a mutable rectangle's contract. Fixes: make shapes immutable (then <code>with_width</code> returns a new <code>Rectangle</code>), or do not relate them by inheritance at all. Other common violations: a subclass method that raises <code>NotImplementedError</code> for something the base promises (a <code>Penguin.fly()</code>), or one that tightens input rules."
          }
        ]
      },
      {
        "title": "I: Interface segregation",
        "body": [
          {
            "type": "p",
            "html": "Clients should not depend on methods they do not use. A fat interface forces every implementation to stub out methods it cannot support, and those stubs are where Liskov violations come from."
          },
          {
            "type": "code",
            "src": "from typing import Protocol\n\nclass Printer(Protocol):\n    def print(self, doc: str) -> str: ...\n\nclass Scanner(Protocol):\n    def scan(self) -> str: ...\n\nclass BasicPrinter:                          # only what it can do\n    def print(self, doc): return f\"printed {doc!r}\"\n\nclass OfficeMachine:                         # implements both small interfaces\n    def print(self, doc): return f\"printed {doc!r}\"\n    def scan(self): return \"scanned page\"\n\ndef print_all(p: Printer, docs):            # depends only on Printer\n    return [p.print(d) for d in docs]\n\ndef archive(s: Scanner):\n    return s.scan()\n\nprint(print_all(BasicPrinter(), [\"a.pdf\"]), archive(OfficeMachine()))",
            "label": null,
            "output": "[\"printed 'a.pdf'\"] scanned page",
            "isError": false
          },
          {
            "type": "p",
            "html": "In Python, <code>typing.Protocol</code> makes small interfaces cheap: a class satisfies a protocol just by having the methods, so splitting interfaces costs nothing at the implementation side."
          }
        ]
      },
      {
        "title": "D: Dependency inversion",
        "body": [
          {
            "type": "p",
            "html": "High-level policy should not depend on low-level details; both should depend on an abstraction. Concretely: do not construct your collaborators inside a class; receive them. That makes the class testable with fakes and lets the detail change (SMTP to SMS, Postgres to an in-memory store) without touching the policy."
          },
          {
            "type": "code",
            "src": "from typing import Protocol\n\nclass Notifier(Protocol):\n    def send(self, to: str, text: str) -> None: ...\n\nclass OrderService:\n    def __init__(self, notifier: Notifier):          # injected, not constructed\n        self.notifier = notifier\n\n    def place(self, customer, item):\n        order_id = f\"ord-{abs(hash((customer, item))) % 1000:03d}\"\n        self.notifier.send(customer, f\"order {item} placed\")\n        return order_id\n\nclass FakeNotifier:                                   # for tests\n    def __init__(self):\n        self.sent = []\n    def send(self, to, text):\n        self.sent.append((to, text))\n\nclass SmsNotifier:\n    def send(self, to, text):\n        print(f\"  SMS to {to}: {text}\")\n\nfake = FakeNotifier()\nOrderService(fake).place(\"ann\", \"lamp\")\nprint(\"test saw:\", fake.sent)\nOrderService(SmsNotifier()).place(\"bob\", \"desk\")",
            "label": null,
            "output": "test saw: [('ann', 'order lamp placed')]\n  SMS to bob: order desk placed",
            "isError": false
          }
        ]
      },
      {
        "title": "Composition over inheritance",
        "body": [
          {
            "type": "p",
            "html": "Inheritance fixes behaviour at class-definition time and couples the subclass to the parent's internals. Composition &mdash; holding a reference to an object that provides the behaviour &mdash; lets you mix behaviours freely and change them at run time. When two independent things vary, inheritance needs a subclass per combination; composition needs one class per variant of each."
          },
          {
            "type": "code",
            "src": "import itertools\n\nengines = [\"petrol\", \"diesel\", \"electric\"]\nbodies = [\"sedan\", \"suv\", \"hatchback\"]\ndrives = [\"fwd\", \"awd\"]\nprint(\"subclasses needed with inheritance:\", len(list(itertools.product(engines, bodies, drives))))\nprint(\"classes needed with composition:  \", len(engines) + len(bodies) + len(drives))\n\nclass Car:\n    def __init__(self, engine, body, drive):\n        self.engine, self.body, self.drive = engine, body, drive\n    def describe(self):\n        return f\"{self.body} / {self.engine} / {self.drive}\"\n\ncar = Car(\"petrol\", \"suv\", \"fwd\")\ncar.engine = \"electric\"                    # swap a part at run time\nprint(car.describe())",
            "label": null,
            "output": "subclasses needed with inheritance: 18\nclasses needed with composition:   8\nsuv / electric / fwd",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Give an example of a Liskov violation you might see in real code.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A <code>ReadOnlyList(list)</code> subclass whose <code>append</code> raises: any function written for a <code>list</code> that appends now crashes. Or a <code>CachedRepository</code> subclass whose <code>save</code> silently does nothing until <code>flush()</code>, breaking callers that read back what they saved. The fix is the same: do not inherit when you cannot honour the parent's contract. Wrap the object instead (composition) and expose only the operations you support."
          }
        ]
      },
      {
        "q": "How does dependency injection make code testable? Show it without a framework.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Pass dependencies into the constructor instead of creating them inside. In tests, pass a fake that records calls or returns canned data; in production, pass the real implementation. No framework is needed in Python &mdash; a constructor parameter (often with a sensible default) is enough."
          },
          {
            "type": "code",
            "src": "import datetime as dt\n\nclass Greeter:\n    def __init__(self, clock=dt.datetime.now):        # injectable clock\n        self.clock = clock\n    def greet(self, name):\n        hour = self.clock().hour\n        return f\"Good {'morning' if hour < 12 else 'evening'}, {name}\"\n\nprint(Greeter(clock=lambda: dt.datetime(2026, 1, 1, 9)).greet(\"ann\"))\nprint(Greeter(clock=lambda: dt.datetime(2026, 1, 1, 20)).greet(\"ann\"))",
            "label": null,
            "output": "Good morning, ann\nGood evening, ann",
            "isError": false
          }
        ]
      },
      {
        "q": "Is a class with many small methods always better than one with a few big ones?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "No. SRP is about reasons to change, not size. Splitting a cohesive algorithm into ten classes that always change together adds indirection and no flexibility. Split along lines where things change independently or are reused independently; keep together what changes together. A good test: can you describe the class's job in one sentence without &ldquo;and&rdquo;?"
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Robert C. Martin: The principles of OOD",
        "url": "http://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod"
      },
      {
        "label": "Barbara Liskov and Jeannette Wing: A behavioral notion of subtyping",
        "url": "https://dl.acm.org/doi/10.1145/197320.197383"
      },
      {
        "label": "Python docs: typing.Protocol",
        "url": "https://docs.python.org/3/library/typing.html#typing.Protocol"
      }
    ]
  },
  {
    "id": "creational",
    "title": "Creational Patterns",
    "group": "Patterns",
    "tags": [],
    "level": null,
    "summary": "Factory method and registries, abstract factory, builder, prototype, singleton and object pool - and their Pythonic forms.",
    "intro": [
      "Creational patterns decide <em>how objects get made</em>, so that the code using an object does not need to know its concrete class, how complicated it is to assemble, or whether it is shared. They matter whenever &ldquo;which class&rdquo; is a decision made from data (a config value, a request field) rather than written into the code."
    ],
    "sections": [
      {
        "title": "Factory: deciding which class to create",
        "body": [
          {
            "type": "p",
            "html": "A factory takes a description (<code>\"car\"</code>, <code>\"upi\"</code>, a config dict) and returns an instance of the right class. Callers depend on the common interface only. The extensible Python form is a <strong>registry</strong>: classes register themselves under a key, so adding a type never edits the factory."
          },
          {
            "type": "code",
            "src": "from abc import ABC, abstractmethod\n\nclass Vehicle(ABC):\n    registry: dict[str, type[\"Vehicle\"]] = {}\n    wheels = 0\n\n    def __init_subclass__(cls, kind=None, **kw):\n        super().__init_subclass__(**kw)\n        if kind:\n            Vehicle.registry[kind] = cls         # self-registration\n\n    @classmethod\n    def create(cls, kind, plate):                # the factory\n        try:\n            return cls.registry[kind](plate)\n        except KeyError:\n            raise ValueError(f\"unknown vehicle type {kind!r}\") from None\n\n    def __init__(self, plate):\n        self.plate = plate\n\n    @abstractmethod\n    def spot_size(self) -> str: ...\n\nclass Bike(Vehicle, kind=\"bike\"):\n    wheels = 2\n    def spot_size(self): return \"small\"\n\nclass Car(Vehicle, kind=\"car\"):\n    wheels = 4\n    def spot_size(self): return \"medium\"\n\nclass Bus(Vehicle, kind=\"bus\"):\n    wheels = 6\n    def spot_size(self): return \"large\"\n\nfor kind, plate in [(\"car\", \"KA-01\"), (\"bike\", \"KA-02\"), (\"bus\", \"KA-03\")]:\n    v = Vehicle.create(kind, plate)\n    print(f\"{type(v).__name__:4} {v.plate} wheels={v.wheels} spot={v.spot_size()}\")\ntry:\n    Vehicle.create(\"tank\", \"X\")\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "Car  KA-01 wheels=4 spot=medium\nBike KA-02 wheels=2 spot=small\nBus  KA-03 wheels=6 spot=large\nValueError: unknown vehicle type 'tank'",
            "isError": false
          },
          {
            "type": "p",
            "html": "Python also gives you <strong>alternative constructors</strong> as <code>classmethod</code>s &mdash; <code>datetime.fromtimestamp</code>, <code>dict.fromkeys</code> &mdash; which are the factory-method idea at the scale of one class: several named ways to build the same type."
          }
        ]
      },
      {
        "title": "Abstract factory: families that must match",
        "body": [
          {
            "type": "p",
            "html": "When objects come in families that must be used together &mdash; a dark-theme button with a dark-theme dialog, AWS storage with AWS queues &mdash; an abstract factory creates the whole family, and swapping the factory swaps all of them at once. It prevents mixing products from different families."
          },
          {
            "type": "code",
            "src": "from typing import Protocol\n\nclass Storage(Protocol):\n    def put(self, key, data) -> str: ...\n\nclass Queue(Protocol):\n    def publish(self, msg) -> str: ...\n\nclass CloudFactory(Protocol):\n    def storage(self) -> Storage: ...\n    def queue(self) -> Queue: ...\n\nclass S3:\n    def put(self, key, data): return f\"s3://bucket/{key}\"\nclass SQS:\n    def publish(self, msg): return f\"sqs <- {msg}\"\nclass AWS:\n    def storage(self): return S3()\n    def queue(self): return SQS()\n\nclass GCS:\n    def put(self, key, data): return f\"gs://bucket/{key}\"\nclass PubSub:\n    def publish(self, msg): return f\"pubsub <- {msg}\"\nclass GCP:\n    def storage(self): return GCS()\n    def queue(self): return PubSub()\n\ndef upload_and_notify(cloud: CloudFactory, name):     # knows no concrete class\n    url = cloud.storage().put(name, b\"...\")\n    return url, cloud.queue().publish(f\"uploaded {url}\")\n\nfor cloud in (AWS(), GCP()):\n    print(upload_and_notify(cloud, \"report.csv\"))",
            "label": null,
            "output": "('s3://bucket/report.csv', 'sqs <- uploaded s3://bucket/report.csv')\n('gs://bucket/report.csv', 'pubsub <- uploaded gs://bucket/report.csv')",
            "isError": false
          }
        ]
      },
      {
        "title": "Builder: complex construction step by step",
        "body": [
          {
            "type": "p",
            "html": "Use a builder when an object has many optional parts, must be validated as a whole, or is naturally assembled in steps (a SQL query, an HTTP request, a meal order). Methods return <code>self</code> for a fluent chain, and <code>build()</code> validates and produces an immutable result."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass HttpRequest:\n    method: str\n    url: str\n    headers: tuple\n    body: str | None\n    timeout: float\n\nclass RequestBuilder:\n    def __init__(self, url):\n        self._url, self._method = url, \"GET\"\n        self._headers, self._body, self._timeout = {}, None, 10.0\n\n    def method(self, m):\n        self._method = m.upper(); return self\n    def header(self, k, v):\n        self._headers[k] = v; return self\n    def json(self, body):\n        self._body = body\n        return self.header(\"Content-Type\", \"application/json\")\n    def timeout(self, seconds):\n        self._timeout = seconds; return self\n\n    def build(self):\n        if self._body is not None and self._method == \"GET\":\n            raise ValueError(\"GET request cannot have a body\")\n        return HttpRequest(self._method, self._url, tuple(sorted(self._headers.items())),\n                           self._body, self._timeout)\n\nreq = (RequestBuilder(\"https://api.example.com/orders\")\n       .method(\"post\").json('{\"item\": \"lamp\"}').header(\"Auth\", \"token\").timeout(2).build())\nprint(req)\ntry:\n    RequestBuilder(\"https://x\").json(\"{}\").build()\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "HttpRequest(method='POST', url='https://api.example.com/orders', headers=(('Auth', 'token'), ('Content-Type', 'application/json')), body='{\"item\": \"lamp\"}', timeout=2)\nValueError: GET request cannot have a body",
            "isError": false
          },
          {
            "type": "p",
            "html": "For simple cases Python's keyword arguments with defaults already do most of a builder's job. Reach for a builder when construction has ordering, cross-field validation, or many steps that read better as a chain."
          }
        ]
      },
      {
        "title": "Prototype: copy a configured object",
        "body": [
          {
            "type": "p",
            "html": "When building an object from scratch is expensive or fiddly (loaded from disk, many settings), keep a configured <em>prototype</em> and clone it. In Python that is <code>copy.deepcopy</code>, plus a <code>__deepcopy__</code> hook if some members (connections, caches) must be shared or reset rather than copied."
          },
          {
            "type": "code",
            "src": "import copy\n\nclass Document:\n    def __init__(self, template_name):\n        print(f\"  (expensive) loading template {template_name}\")\n        self.styles = {\"font\": \"Inter\", \"size\": 11}\n        self.sections = [\"header\", \"body\", \"footer\"]\n\nregistry = {\"invoice\": Document(\"invoice\"), \"letter\": Document(\"letter\")}\n\ndef new_document(kind, **style):\n    doc = copy.deepcopy(registry[kind])      # no reload\n    doc.styles.update(style)\n    return doc\n\na = new_document(\"invoice\", size=14)\nb = new_document(\"invoice\")\nprint(a.styles, b.styles, a.sections is b.sections)",
            "label": null,
            "output": "  (expensive) loading template invoice\n  (expensive) loading template letter\n{'font': 'Inter', 'size': 14} {'font': 'Inter', 'size': 11} False",
            "isError": false
          }
        ]
      },
      {
        "title": "Singleton: one shared instance",
        "body": [
          {
            "type": "p",
            "html": "A singleton guarantees one instance with global access: configuration, a registry, a connection manager. The textbook implementation overrides <code>__new__</code>. In Python, a module is already a singleton (it is created once and cached in <code>sys.modules</code>), so a module-level instance is usually the simpler answer."
          },
          {
            "type": "code",
            "src": "import threading\n\nclass Config:\n    _instance = None\n    _lock = threading.Lock()\n\n    def __new__(cls):\n        if cls._instance is None:\n            with cls._lock:                       # double-checked for threads\n                if cls._instance is None:\n                    inst = super().__new__(cls)\n                    inst.settings = {\"env\": \"prod\"}\n                    cls._instance = inst\n        return cls._instance\n\ninstances = []\nthreads = [threading.Thread(target=lambda: instances.append(Config())) for _ in range(20)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint(\"distinct instances:\", len({id(i) for i in instances}))\nConfig().settings[\"env\"] = \"staging\"\nprint(Config().settings)",
            "label": null,
            "output": "distinct instances: 1\n{'env': 'staging'}",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Singletons are global state in disguise: they make tests depend on each other and hide dependencies. Prefer creating one instance at start-up and passing it to whoever needs it. Use a true singleton only for things that are genuinely process-wide, and never for anything a test would want to replace."
          }
        ]
      },
      {
        "title": "Object pool: reuse expensive objects",
        "body": [
          {
            "type": "p",
            "html": "Database connections, threads and large buffers are expensive to create. A pool creates a bounded number, lends them out, and takes them back. A context manager guarantees return even when the borrower raises."
          },
          {
            "type": "code",
            "src": "import queue\nfrom contextlib import contextmanager\n\nclass Connection:\n    created = 0\n    def __init__(self):\n        Connection.created += 1\n        self.id = Connection.created\n    def query(self, sql):\n        return f\"conn{self.id}: {sql}\"\n\nclass Pool:\n    def __init__(self, size):\n        self._free = queue.Queue()\n        for _ in range(size):\n            self._free.put(Connection())\n\n    @contextmanager\n    def connection(self, timeout=1.0):\n        conn = self._free.get(timeout=timeout)    # blocks when exhausted\n        try:\n            yield conn\n        finally:\n            self._free.put(conn)                  # always returned\n\npool = Pool(2)\nresults = []\nfor i in range(5):\n    with pool.connection() as c:\n        results.append(c.query(f\"select {i}\"))\ntry:\n    with pool.connection() as c:\n        raise RuntimeError(\"query failed\")\nexcept RuntimeError:\n    pass\nprint(results)\nprint(\"connections ever created:\", Connection.created, \"| free now:\", pool._free.qsize())",
            "label": null,
            "output": "['conn1: select 0', 'conn2: select 1', 'conn1: select 2', 'conn2: select 3', 'conn1: select 4']\nconnections ever created: 2 | free now: 2",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Factory method vs abstract factory vs builder: how do you tell which one a problem needs?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Factory: the question is <em>which class</em> to create from some input, one object at a time. Abstract factory: you create <em>several related objects</em> that must come from the same family, and the family is chosen once. Builder: the question is <em>how</em> to assemble one complex object with many optional parts and validation. They combine: an abstract factory's methods are often factory methods, and a factory may use a builder internally."
          }
        ]
      },
      {
        "q": "Why is Singleton often called an anti-pattern, and when is it acceptable?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It is global mutable state: any code can reach it, so dependencies are hidden; tests leak state into each other and cannot substitute a fake; and it makes concurrency harder. It is acceptable for things that are truly one-per-process and stateless or read-only after start-up (a logger configuration, a metrics registry), and even then a module-level object created at import time is the Pythonic way. For anything with behaviour you want to test, create one instance in the composition root and inject it."
          }
        ]
      },
      {
        "q": "Write a thread-safe lazily-initialised singleton. Is the lock needed in CPython?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Yes. The check <code>if cls._instance is None</code> and the assignment are separate bytecode steps, and a thread switch between them lets two threads both create an instance, with one silently lost. The double-checked lock above takes the lock only on the slow path. A module-level instance avoids writing this by hand, because module import is protected by the import lock. <code>functools.cache</code> on a factory function is a neat lazy version for single-threaded start-up, but it does not lock: two threads racing on the first call can both run the factory."
          },
          {
            "type": "code",
            "src": "from functools import cache\n\n@cache\ndef get_settings():\n    print(\"  loading settings once\")\n    return {\"region\": \"ap-south-1\"}\n\nprint(get_settings() is get_settings())",
            "label": null,
            "output": "  loading settings once\nTrue",
            "isError": false
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Refactoring.Guru: Creational patterns",
        "url": "https://refactoring.guru/design-patterns/creational-patterns"
      },
      {
        "label": "python-patterns.guide: The Singleton pattern",
        "url": "https://python-patterns.guide/gang-of-four/singleton/"
      },
      {
        "label": "Python docs: __init_subclass__",
        "url": "https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__"
      }
    ]
  },
  {
    "id": "structural",
    "title": "Structural Patterns",
    "group": "Patterns",
    "tags": [],
    "level": null,
    "summary": "Adapter, decorator, composite, facade, proxy, flyweight and bridge - how objects are wrapped and assembled.",
    "intro": [
      "Structural patterns are about how objects are put together: wrapping one object to change its interface (Adapter) or add behaviour (Decorator, Proxy), treating trees of objects uniformly (Composite), hiding a subsystem behind one entry point (Facade), and sharing state to save memory (Flyweight).",
      "Several of them look alike in code &mdash; a class that holds another object and forwards calls. What distinguishes them is <em>intent</em>, and naming the intent is what the interviewer wants to hear."
    ],
    "sections": [
      {
        "title": "Adapter: make an incompatible interface fit",
        "body": [
          {
            "type": "p",
            "html": "Your code expects one interface; a third-party SDK or legacy class offers another. An adapter implements your interface by translating calls to theirs, so the rest of your code never sees the foreign API."
          },
          {
            "type": "code",
            "src": "from typing import Protocol\n\nclass PaymentGateway(Protocol):                 # what our checkout expects\n    def pay(self, amount_rupees: float, ref: str) -> bool: ...\n\nclass StripeSDK:                                 # third party: cents, dicts, exceptions\n    def create_charge(self, amount_cents, currency, metadata):\n        if amount_cents <= 0:\n            raise ValueError(\"invalid amount\")\n        return {\"status\": \"succeeded\", \"id\": \"ch_1\", \"meta\": metadata}\n\nclass StripeAdapter:\n    def __init__(self, sdk: StripeSDK):\n        self.sdk = sdk\n    def pay(self, amount_rupees, ref):\n        try:\n            r = self.sdk.create_charge(round(amount_rupees * 100), \"inr\", {\"ref\": ref})\n        except ValueError:\n            return False\n        return r[\"status\"] == \"succeeded\"\n\ndef checkout(gateway: PaymentGateway, total):\n    return \"paid\" if gateway.pay(total, \"order-42\") else \"declined\"\n\nprint(checkout(StripeAdapter(StripeSDK()), 499.5), checkout(StripeAdapter(StripeSDK()), 0))",
            "label": null,
            "output": "paid declined",
            "isError": false
          }
        ]
      },
      {
        "title": "Decorator: add behaviour by wrapping",
        "body": [
          {
            "type": "p",
            "html": "A decorator implements the same interface as the object it wraps and adds something before or after delegating. Decorators stack, so features combine freely at run time without a subclass for every combination. (Python's <code>@decorator</code> syntax applies the same idea to functions.)"
          },
          {
            "type": "code",
            "src": "from typing import Protocol\n\nclass DataSource(Protocol):\n    def write(self, data: str) -> str: ...\n\nclass FileSource:\n    def write(self, data): return data\n\nclass Compressed:\n    def __init__(self, inner: DataSource): self.inner = inner\n    def write(self, data): return self.inner.write(f\"zip({data})\")\n\nclass Encrypted:\n    def __init__(self, inner: DataSource): self.inner = inner\n    def write(self, data): return self.inner.write(f\"aes({data})\")\n\nclass Logged:\n    def __init__(self, inner: DataSource): self.inner = inner\n    def write(self, data):\n        out = self.inner.write(data)\n        print(f\"  wrote {len(out)} chars\")\n        return out\n\nprint(FileSource().write(\"salary.csv\"))\nprint(Logged(Encrypted(Compressed(FileSource()))).write(\"salary.csv\"))\nprint(Compressed(Encrypted(FileSource())).write(\"salary.csv\"))   # order matters",
            "label": null,
            "output": "salary.csv\n  wrote 20 chars\nzip(aes(salary.csv))\naes(zip(salary.csv))",
            "isError": false
          },
          {
            "type": "note",
            "text": "Decorator vs inheritance: three optional features would need 2<sup>3</sup> = 8 subclasses to cover every combination; with decorators it is three wrappers chosen at run time."
          }
        ]
      },
      {
        "title": "Composite: trees of parts and wholes",
        "body": [
          {
            "type": "p",
            "html": "When things nest &mdash; folders in folders, menu items in menus, employees under managers, sub-expressions in expressions &mdash; give leaves and containers the same interface. Client code calls one method on the root and the recursion happens inside the structure."
          },
          {
            "type": "code",
            "src": "from abc import ABC, abstractmethod\n\nclass Node(ABC):\n    def __init__(self, name): self.name = name\n    @abstractmethod\n    def size(self) -> int: ...\n    def show(self, indent=0):\n        print(\"  \" * indent + f\"{self.name} ({self.size()} B)\")\n\nclass File(Node):\n    def __init__(self, name, size):\n        super().__init__(name); self._size = size\n    def size(self): return self._size\n\nclass Folder(Node):\n    def __init__(self, name, *children):\n        super().__init__(name); self.children = list(children)\n    def size(self): return sum(c.size() for c in self.children)\n    def show(self, indent=0):\n        super().show(indent)\n        for c in self.children:\n            c.show(indent + 1)\n\nroot = Folder(\"root\", File(\"a.txt\", 120),\n              Folder(\"src\", File(\"main.py\", 800), File(\"util.py\", 300)),\n              Folder(\"empty\"))\nroot.show()",
            "label": null,
            "output": "root (1220 B)\n  a.txt (120 B)\n  src (1100 B)\n    main.py (800 B)\n    util.py (300 B)\n  empty (0 B)",
            "isError": false
          }
        ]
      },
      {
        "title": "Facade: one simple door into a subsystem",
        "body": [
          {
            "type": "p",
            "html": "A facade offers a small, task-oriented API over a set of classes with complicated interactions. Clients call <code>place_order()</code> instead of coordinating inventory, payment, shipping and notification themselves. It does not hide the subsystem from those who need it; it just gives everyone else an easy path."
          },
          {
            "type": "code",
            "src": "class Inventory:\n    def __init__(self):\n        self.stock = {\"lamp\": 2}\n    def reserve(self, item):\n        if self.stock.get(item, 0) == 0:\n            raise LookupError(f\"{item} out of stock\")\n        self.stock[item] -= 1\n    def release(self, item):\n        self.stock[item] += 1\n\nclass Payments:\n    def charge(self, user, amount): return amount < 1000\n\nclass Shipping:\n    def schedule(self, user, item): return f\"ship {item} to {user}\"\n\nclass OrderFacade:\n    def __init__(self):\n        self.inv, self.pay, self.ship = Inventory(), Payments(), Shipping()\n\n    def place_order(self, user, item, price):\n        self.inv.reserve(item)\n        if not self.pay.charge(user, price):\n            self.inv.release(item)                # compensate\n            return \"payment failed\"\n        return self.ship.schedule(user, item)\n\nshop = OrderFacade()\nprint(shop.place_order(\"ann\", \"lamp\", 40))\nprint(shop.place_order(\"bob\", \"lamp\", 5000), \"| lamps left:\", shop.inv.stock[\"lamp\"])",
            "label": null,
            "output": "ship lamp to ann\npayment failed | lamps left: 1",
            "isError": false
          }
        ]
      },
      {
        "title": "Proxy: stand in front of the real object",
        "body": [
          {
            "type": "p",
            "html": "A proxy has the same interface as the real object and controls access to it: <strong>virtual proxy</strong> (create the expensive object lazily), <strong>caching proxy</strong> (remember results), <strong>protection proxy</strong> (check permissions), <strong>remote proxy</strong> (the object lives on another machine). Same shape as a decorator; the intent is access control rather than adding features."
          },
          {
            "type": "code",
            "src": "class ReportService:\n    def __init__(self):\n        print(\"  (expensive) connecting to warehouse\")\n    def revenue(self, month):\n        return {\"jan\": 120, \"feb\": 95}[month]\n\nclass ReportProxy:\n    def __init__(self, user_role):\n        self.role, self._real, self._cache = user_role, None, {}\n\n    def revenue(self, month):\n        if self.role != \"finance\":                # protection\n            raise PermissionError(\"finance only\")\n        if month not in self._cache:              # caching\n            if self._real is None:                # virtual: lazy creation\n                self._real = ReportService()\n            self._cache[month] = self._real.revenue(month)\n        return self._cache[month]\n\np = ReportProxy(\"finance\")\nprint(\"proxy created, nothing connected yet\")\nprint(p.revenue(\"jan\"), p.revenue(\"jan\"), p.revenue(\"feb\"))\ntry:\n    ReportProxy(\"intern\").revenue(\"jan\")\nexcept PermissionError as e:\n    print(\"PermissionError:\", e)",
            "label": null,
            "output": "proxy created, nothing connected yet\n  (expensive) connecting to warehouse\n120 120 95\nPermissionError: finance only",
            "isError": false
          }
        ]
      },
      {
        "title": "Flyweight and Bridge",
        "body": [
          {
            "type": "p",
            "html": "<strong>Flyweight</strong> shares the immutable, common part of many objects (the <em>intrinsic</em> state) and keeps only the varying part per object (the <em>extrinsic</em> state). A forest of a million trees stores three tree <em>types</em> (mesh, texture) and a million (x, y, type) tuples."
          },
          {
            "type": "code",
            "src": "import sys\nfrom functools import cache\n\nclass TreeType:                                   # intrinsic, shared\n    def __init__(self, species, texture):\n        self.species, self.texture = species, texture\n\n@cache\ndef tree_type(species):\n    return TreeType(species, texture=f\"{species}.png\" * 1000)   # big shared data\n\nforest = [(x, x * 2 % 97, tree_type([\"oak\", \"pine\", \"birch\"][x % 3])) for x in range(100_000)]\ntypes = {id(t) for _, _, t in forest}\nprint(\"trees:\", len(forest), \"| distinct TreeType objects:\", len(types))\nprint(\"texture bytes stored once each:\", sys.getsizeof(forest[0][2].texture))",
            "label": null,
            "output": "trees: 100000 | distinct TreeType objects: 3\ntexture bytes stored once each: 7041",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Bridge</strong> splits one class hierarchy that varies in two independent ways into two hierarchies joined by composition: <code>Shape</code> &times; <code>Renderer</code>, <code>Notification</code> (alert, reminder) &times; <code>Channel</code> (email, SMS). It is composition over inheritance, named."
          }
        ]
      },
      {
        "title": "Telling the wrappers apart",
        "body": [
          {
            "type": "table",
            "head": [
              "Pattern",
              "Same interface as wrapped?",
              "Intent"
            ],
            "rows": [
              [
                "Adapter",
                "No: converts to a <em>different</em> interface",
                "Make incompatible things work together"
              ],
              [
                "Decorator",
                "Yes",
                "Add responsibilities, stackable"
              ],
              [
                "Proxy",
                "Yes",
                "Control access: lazy, cache, permissions, remote"
              ],
              [
                "Facade",
                "No: a new, simpler interface over many objects",
                "Simplify a subsystem"
              ],
              [
                "Composite",
                "Yes, for leaves and containers",
                "Treat a tree uniformly"
              ]
            ]
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Decorator and Proxy have the same structure. How do you explain the difference?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Intent and who decides. A decorator adds behaviour, and the client composes the stack it wants (<code>Logged(Encrypted(source))</code>), often several deep. A proxy controls access to one real subject, usually transparently &mdash; the client may not know it has a proxy &mdash; and it often manages the subject's lifecycle (creating it lazily, connecting remotely). Caching, lazy loading and permission checks are proxy jobs; compression, logging and retries layered by choice are decorator jobs."
          }
        ]
      },
      {
        "q": "How would you add retry and timing behaviour to every call of an existing API client without editing it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Wrap it in decorators that implement the same interface: a <code>Retrying</code> wrapper that re-invokes the inner client on transient errors with backoff, and a <code>Timed</code> wrapper that records latency. Compose them where the client is constructed. For a client with many methods, a generic wrapper using <code>__getattr__</code> can apply the behaviour to every method call."
          },
          {
            "type": "code",
            "src": "import time\n\nclass Flaky:\n    def __init__(self): self.calls = 0\n    def fetch(self, key):\n        self.calls += 1\n        if self.calls < 3:\n            raise ConnectionError(\"reset\")\n        return f\"value-{key}\"\n\nclass Retrying:\n    def __init__(self, inner, attempts=4):\n        self.inner, self.attempts = inner, attempts\n    def __getattr__(self, name):\n        method = getattr(self.inner, name)\n        def wrapped(*a, **kw):\n            for i in range(self.attempts):\n                try:\n                    return method(*a, **kw)\n                except ConnectionError:\n                    time.sleep(0.001 * 2 ** i)\n            raise ConnectionError(\"gave up\")\n        return wrapped\n\nclient = Retrying(Flaky())\nprint(client.fetch(\"a\"), \"after\", client.inner.calls, \"calls\")",
            "label": null,
            "output": "value-a after 3 calls",
            "isError": false
          }
        ]
      },
      {
        "q": "Where does the Composite pattern show up in systems you have used?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "File systems (files and directories), GUI toolkits (widgets containing widgets; a layout's size is computed from its children), the DOM, organisation charts, abstract syntax trees (an expression node contains sub-expressions), bill-of-materials systems (a product made of parts made of parts), and permission groups that contain users and other groups. Each time, a single operation &mdash; size, render, evaluate, cost, expand members &mdash; recurses through the tree via one interface."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Refactoring.Guru: Structural patterns",
        "url": "https://refactoring.guru/design-patterns/structural-patterns"
      },
      {
        "label": "python-patterns.guide: The Decorator pattern",
        "url": "https://python-patterns.guide/gang-of-four/decorator-pattern/"
      }
    ]
  },
  {
    "id": "behavioral-core",
    "title": "Behavioral Patterns I: Strategy, Observer, Command, State, Template Method",
    "group": "Patterns",
    "tags": [],
    "level": null,
    "summary": "The five patterns that solve most LLD problems, each with a class-based and a Pythonic version.",
    "intro": [
      "Behavioral patterns are about how responsibilities and algorithms are divided between objects. These five appear in most LLD interview answers: <strong>Strategy</strong> for interchangeable algorithms, <strong>Observer</strong> for reacting to events, <strong>Command</strong> for actions as objects (undo, queues), <strong>State</strong> for behaviour that depends on a lifecycle, and <strong>Template Method</strong> for a fixed skeleton with varying steps."
    ],
    "sections": [
      {
        "title": "Strategy",
        "body": [
          {
            "type": "p",
            "html": "Define a family of algorithms behind one interface and let the client pick one at run time. The context (a <code>Checkout</code>, a <code>ParkingLot</code>) holds a strategy and delegates to it; changing behaviour means swapping the object, not editing the context."
          },
          {
            "type": "code",
            "src": "from typing import Protocol\n\nclass PricingStrategy(Protocol):\n    def price(self, hours: float) -> float: ...\n\nclass Hourly:\n    def __init__(self, rate): self.rate = rate\n    def price(self, hours): return round(self.rate * max(1, hours), 2)\n\nclass FlatDaily:\n    def __init__(self, amount): self.amount = amount\n    def price(self, hours): return self.amount * (int(hours // 24) + 1)\n\nclass Tiered:\n    \"\"\"first 2 h at one rate, then cheaper\"\"\"\n    def price(self, hours):\n        first = min(hours, 2) * 40\n        rest = max(0, hours - 2) * 20\n        return round(first + rest, 2)\n\nclass Ticket:\n    def __init__(self, hours, strategy: PricingStrategy):\n        self.hours, self.strategy = hours, strategy\n    def fee(self):\n        return self.strategy.price(self.hours)\n\nfor s in (Hourly(30), FlatDaily(200), Tiered()):\n    print(f\"{type(s).__name__:9}\", [Ticket(h, s).fee() for h in (0.5, 3, 30)])",
            "label": null,
            "output": "Hourly    [30, 90, 900]\nFlatDaily [200, 200, 400]\nTiered    [20.0, 100, 640]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Pythonic form: when a strategy is a single method with no state, a plain function (or a dict of functions keyed by name) is a perfectly good strategy."
          }
        ]
      },
      {
        "title": "Observer",
        "body": [
          {
            "type": "p",
            "html": "A subject keeps a list of subscribers and notifies them when something happens. The subject does not know what subscribers do, so adding a reaction (send an email, update a dashboard, write an audit log) never touches the subject."
          },
          {
            "type": "code",
            "src": "from collections import defaultdict\nfrom typing import Callable\n\nclass EventBus:\n    def __init__(self):\n        self._subs: dict[str, list[Callable]] = defaultdict(list)\n\n    def subscribe(self, event, handler):\n        self._subs[event].append(handler)\n        return lambda: self._subs[event].remove(handler)    # unsubscribe handle\n\n    def publish(self, event, **data):\n        for handler in list(self._subs[event]):\n            try:\n                handler(**data)\n            except Exception as e:                           # one bad observer\n                print(f\"  observer failed: {e!r}\")           # must not stop the rest\n\nbus = EventBus()\nbus.subscribe(\"order_paid\", lambda order, amount: print(f\"  email: receipt for {order}\"))\nstop_sms = bus.subscribe(\"order_paid\", lambda order, amount: print(f\"  sms: {order} paid\"))\nbus.subscribe(\"order_paid\", lambda order, amount: 1 / 0)\nbus.subscribe(\"order_paid\", lambda order, amount: print(f\"  ledger: +{amount}\"))\n\nbus.publish(\"order_paid\", order=\"A1\", amount=499)\nstop_sms()\nprint(\"after unsubscribing sms:\")\nbus.publish(\"order_paid\", order=\"A2\", amount=99)",
            "label": null,
            "output": "  email: receipt for A1\n  sms: A1 paid\n  observer failed: ZeroDivisionError('division by zero')\n  ledger: +499\nafter unsubscribing sms:\n  email: receipt for A2\n  observer failed: ZeroDivisionError('division by zero')\n  ledger: +99",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Synchronous observers run in the publisher's thread and add their latency to it. For slow reactions (email, webhooks), publish to a queue and let workers do the work. And keep a way to unsubscribe, or long-lived subjects keep dead observers alive."
          }
        ]
      },
      {
        "title": "Command",
        "body": [
          {
            "type": "p",
            "html": "Wrap a request as an object with <code>execute()</code> (and often <code>undo()</code>). Commands can be queued, logged, retried, sent to another process, or kept on a history stack for undo/redo &mdash; things you cannot do with a plain method call."
          },
          {
            "type": "code",
            "src": "class Light:\n    def __init__(self): self.level = 0\n\nclass SetLevel:\n    def __init__(self, light, level):\n        self.light, self.level, self.prev = light, level, None\n    def execute(self):\n        self.prev, self.light.level = self.light.level, self.level\n    def undo(self):\n        self.light.level = self.prev\n\nclass Remote:\n    def __init__(self):\n        self.done, self.undone = [], []\n    def run(self, cmd):\n        cmd.execute(); self.done.append(cmd); self.undone.clear()\n    def undo(self):\n        if self.done:\n            cmd = self.done.pop(); cmd.undo(); self.undone.append(cmd)\n    def redo(self):\n        if self.undone:\n            cmd = self.undone.pop(); cmd.execute(); self.done.append(cmd)\n\nlight, remote = Light(), Remote()\nfor lvl in (30, 70, 100):\n    remote.run(SetLevel(light, lvl))\ntrace = [light.level]\nremote.undo(); trace.append(light.level)\nremote.undo(); trace.append(light.level)\nremote.redo(); trace.append(light.level)\nremote.run(SetLevel(light, 10)); trace.append(light.level)\nremote.redo(); trace.append(light.level)      # redo stack was cleared by the new command\nprint(trace)",
            "label": null,
            "output": "[100, 70, 30, 70, 10, 10]",
            "isError": false
          }
        ]
      },
      {
        "title": "State",
        "body": [
          {
            "type": "p",
            "html": "When an object's behaviour depends on its current state and the same method means different things in different states, give each state its own class. The context delegates to its current state object, and states decide the transitions. This replaces the same <code>if state == ...</code> switch repeated in every method."
          },
          {
            "type": "code",
            "src": "class State:\n    def insert_coin(self, m): raise RuntimeError(f\"cannot insert coin while {self.name}\")\n    def select(self, m, item): raise RuntimeError(f\"cannot select while {self.name}\")\n    def dispense(self, m): raise RuntimeError(f\"cannot dispense while {self.name}\")\n\nclass Idle(State):\n    name = \"idle\"\n    def insert_coin(self, m): m.state = HasCoin()\n\nclass HasCoin(State):\n    name = \"has-coin\"\n    def select(self, m, item):\n        if m.stock.get(item, 0) == 0:\n            m.state = Idle(); return f\"{item} sold out, coin returned\"\n        m.selected, m.state = item, Dispensing()\n        return f\"selected {item}\"\n\nclass Dispensing(State):\n    name = \"dispensing\"\n    def dispense(self, m):\n        m.stock[m.selected] -= 1\n        m.state = Idle()\n        return f\"here is your {m.selected}\"\n\nclass Machine:\n    def __init__(self, stock):\n        self.stock, self.state, self.selected = stock, Idle(), None\n    def insert_coin(self): return self.state.insert_coin(self)\n    def select(self, item): return self.state.select(self, item)\n    def dispense(self): return self.state.dispense(self)\n\nm = Machine({\"cola\": 1})\nm.insert_coin(); print(m.select(\"cola\"), \"|\", m.dispense())\nm.insert_coin(); print(m.select(\"cola\"))\ntry:\n    m.dispense()\nexcept RuntimeError as e:\n    print(\"RuntimeError:\", e)",
            "label": null,
            "output": "selected cola | here is your cola\ncola sold out, coin returned\nRuntimeError: cannot dispense while idle",
            "isError": false
          },
          {
            "type": "note",
            "text": "State vs Strategy: both delegate to an object. A strategy is chosen by the client and rarely changes; states replace <em>each other</em> as the object moves through its lifecycle, and each state knows its legal next states."
          }
        ]
      },
      {
        "title": "Template Method",
        "body": [
          {
            "type": "p",
            "html": "A base class fixes the skeleton of an algorithm in one method and leaves some steps to subclasses. The order of steps, and invariants like &ldquo;always validate before saving&rdquo;, live in one place."
          },
          {
            "type": "code",
            "src": "from abc import ABC, abstractmethod\n\nclass DataImporter(ABC):\n    def run(self, raw):                          # the template method\n        rows = self.parse(raw)\n        rows = [r for r in rows if self.valid(r)]\n        return self.save(rows)\n\n    @abstractmethod\n    def parse(self, raw): ...\n    def valid(self, row):                        # hook with a default\n        return bool(row)\n    def save(self, rows):\n        return f\"saved {len(rows)} rows: {rows}\"\n\nclass CsvImporter(DataImporter):\n    def parse(self, raw):\n        return [line.split(\",\") for line in raw.strip().splitlines()]\n\nclass JsonImporter(DataImporter):\n    def parse(self, raw):\n        import json\n        return json.loads(raw)\n    def valid(self, row):\n        return \"id\" in row\n\nprint(CsvImporter().run(\"1,ann\\n2,bob\\n\"))\nprint(JsonImporter().run('[{\"id\": 1}, {\"name\": \"no id\"}]'))",
            "label": null,
            "output": "saved 2 rows: [['1', 'ann'], ['2', 'bob']]\nsaved 1 rows: [{'id': 1}]",
            "isError": false
          },
          {
            "type": "p",
            "html": "The trade-off: it uses inheritance, so the varying steps are fixed per subclass. If the steps vary independently, pass them in as strategies instead."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "You have a 300-line method with a big <code>if order.status == ...</code> block in several methods. Which pattern, and how do you refactor safely?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "State. Steps: write characterisation tests for each method in each status; create a state class per status with one method per operation, initially containing the matching branch; make the order delegate to <code>self.state</code>; move transition logic into the states (each sets the next state); delete the switch. Each step is small and the tests stay green. The result: adding a status adds a class, and illegal operations fail in one obvious place."
          }
        ]
      },
      {
        "q": "How do you implement undo for operations that cannot be reversed by a simple inverse (e.g. &ldquo;apply filter&rdquo; to an image)?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Two options. Each command stores whatever is needed to undo before executing &mdash; for a destructive operation, a snapshot (Memento) of the affected state, not necessarily the whole document. Or store snapshots at checkpoints and re-execute commands forward from the nearest one (event sourcing style). Snapshots cost memory, so store diffs or compressed regions, and cap the history length."
          }
        ]
      },
      {
        "q": "Observer with synchronous callbacks: what can go wrong?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A slow observer slows the publisher; an exception in one observer can stop later ones (catch per observer); an observer that publishes another event can recurse or reorder events; subscribing inside a notification modifies the list being iterated (iterate over a copy); forgotten subscriptions leak memory (provide unsubscribe, or hold weak references). For cross-service or slow work, publish to a queue instead."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Refactoring.Guru: Behavioral patterns",
        "url": "https://refactoring.guru/design-patterns/behavioral-patterns"
      },
      {
        "label": "Python docs: functools.singledispatch (function-level polymorphism)",
        "url": "https://docs.python.org/3/library/functools.html#functools.singledispatch"
      }
    ]
  },
  {
    "id": "behavioral-more",
    "title": "Behavioral Patterns II: Chain of Responsibility, Visitor, Memento, Mediator, Iterator",
    "group": "Patterns",
    "tags": [],
    "level": null,
    "summary": "Pipelines of handlers, operations over object structures, snapshots, central coordinators and traversal.",
    "intro": [
      "The second set of behavioral patterns appears less often on its own, but each is the clear answer to a recognisable problem: a request that should pass through a sequence of handlers, new operations over a fixed set of node types, saving and restoring state, many objects that need coordinating, and walking a collection without exposing its internals."
    ],
    "sections": [
      {
        "title": "Chain of Responsibility",
        "body": [
          {
            "type": "p",
            "html": "Pass a request along a chain of handlers. Each handler either deals with it or passes it on (or does part of the work and passes on the rest). The sender does not know which handler will act, and the chain can be reconfigured without touching the sender. Expense approvals, support escalation, HTTP middleware and cash dispensing are all chains."
          },
          {
            "type": "code",
            "src": "class Approver:\n    def __init__(self, name, limit, next_=None):\n        self.name, self.limit, self.next = name, limit, next_\n\n    def approve(self, amount, reason):\n        if amount <= self.limit:\n            return f\"{self.name} approved {amount} for {reason}\"\n        if self.next is None:\n            return f\"rejected {amount}: above every limit\"\n        return self.next.approve(amount, reason)\n\nchain = Approver(\"team lead\", 1_000, Approver(\"manager\", 10_000, Approver(\"director\", 100_000)))\nfor amount in (400, 7_500, 60_000, 250_000):\n    print(chain.approve(amount, \"travel\"))",
            "label": null,
            "output": "team lead approved 400 for travel\nmanager approved 7500 for travel\ndirector approved 60000 for travel\nrejected 250000: above every limit",
            "isError": false
          },
          {
            "type": "p",
            "html": "A variant where <em>every</em> handler does part of the work &mdash; ATM denominations, or middleware that each add a header &mdash; is the same structure; the difference is only whether a handler stops the chain."
          },
          {
            "type": "code",
            "src": "def dispense(amount, notes=(2000, 500, 200, 100)):\n    plan = []\n    for note in notes:                       # each handler takes what it can\n        count, amount = divmod(amount, note)\n        if count:\n            plan.append((note, count))\n    if amount:\n        raise ValueError(f\"cannot dispense the remaining {amount}\")\n    return plan\n\nprint(dispense(4700))\ntry:\n    dispense(4750)\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "[(2000, 2), (500, 1), (200, 1)]\nValueError: cannot dispense the remaining 50",
            "isError": false
          }
        ]
      },
      {
        "title": "Visitor",
        "body": [
          {
            "type": "p",
            "html": "You have a stable set of node types (shapes, AST nodes, document elements) and keep adding <em>operations</em> over them: area, render to SVG, export to JSON, compute bounding box. Visitor moves each operation into its own class with a method per node type, so adding an operation adds one class and touches no node. Python's <code>functools.singledispatch</code> or a <code>match</code> statement on type gives the same separation with less ceremony."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass\nfrom functools import singledispatch\n\n@dataclass\nclass Heading:\n    text: str\n    level: int\n\n@dataclass\nclass Paragraph:\n    text: str\n\n@dataclass\nclass Bullet:\n    items: list\n\ndoc = [Heading(\"Report\", 1), Paragraph(\"Sales rose.\"), Bullet([\"north\", \"south\"])]\n\n@singledispatch\ndef to_html(node): raise TypeError(node)\n@to_html.register\ndef _(node: Heading): return f\"<h{node.level}>{node.text}</h{node.level}>\"\n@to_html.register\ndef _(node: Paragraph): return f\"<p>{node.text}</p>\"\n@to_html.register\ndef _(node: Bullet): return \"<ul>\" + \"\".join(f\"<li>{i}</li>\" for i in node.items) + \"</ul>\"\n\ndef to_markdown(node):                        # a second operation, via match\n    match node:\n        case Heading(text, level): return \"#\" * level + \" \" + text\n        case Paragraph(text): return text\n        case Bullet(items): return \"\\n\".join(f\"- {i}\" for i in items)\n\nprint(\"\".join(map(to_html, doc)))\nprint(\"\\n\".join(map(to_markdown, doc)))",
            "label": null,
            "output": "<h1>Report</h1><p>Sales rose.</p><ul><li>north</li><li>south</li></ul>\n# Report\nSales rose.\n- north\n- south",
            "isError": false
          },
          {
            "type": "note",
            "text": "Visitor makes new operations easy and new node types hard (every visitor must learn the new type). Ordinary polymorphism is the opposite. Choose by which of the two you expect to add more often."
          }
        ]
      },
      {
        "title": "Memento",
        "body": [
          {
            "type": "p",
            "html": "Capture an object's internal state in an opaque snapshot so it can be restored later, without exposing internals to whoever stores the snapshot. The originator creates and restores mementos; a caretaker (undo history, checkpoint manager) only keeps them."
          },
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass EditorMemento:                    # opaque to the caretaker\n    _text: str\n    _cursor: int\n\nclass Editor:\n    def __init__(self):\n        self.text, self.cursor = \"\", 0\n    def type(self, s):\n        self.text = self.text[:self.cursor] + s + self.text[self.cursor:]\n        self.cursor += len(s)\n    def save(self):\n        return EditorMemento(self.text, self.cursor)\n    def restore(self, m):\n        self.text, self.cursor = m._text, m._cursor\n\ned, history = Editor(), []\nfor word in (\"Hello\", \", world\", \"!!!\"):\n    history.append(ed.save())\n    ed.type(word)\nprint(repr(ed.text))\ned.restore(history.pop()); print(repr(ed.text))\ned.restore(history.pop()); print(repr(ed.text))",
            "label": null,
            "output": "'Hello, world!!!'\n'Hello, world'\n'Hello'",
            "isError": false
          }
        ]
      },
      {
        "title": "Mediator",
        "body": [
          {
            "type": "p",
            "html": "When many objects interact with many others, the web of references becomes unmanageable. A mediator centralises the interactions: components talk only to the mediator, which decides who else is affected. Chat rooms, air-traffic control and form validation (one field enables another) are typical."
          },
          {
            "type": "code",
            "src": "class ChatRoom:                                   # the mediator\n    def __init__(self):\n        self.members, self.log = {}, []\n    def join(self, user):\n        self.members[user.name] = user\n        user.room = self\n    def send(self, sender, text, to=None):\n        targets = [self.members[to]] if to else [u for n, u in self.members.items() if n != sender]\n        for u in targets:\n            u.receive(sender, text)\n        self.log.append((sender, to or \"*\", text))\n\nclass User:\n    def __init__(self, name):\n        self.name, self.room, self.inbox = name, None, []\n    def say(self, text, to=None):\n        self.room.send(self.name, text, to)       # knows only the room\n    def receive(self, sender, text):\n        self.inbox.append(f\"{sender}: {text}\")\n\nroom = ChatRoom()\nann, bob, cy = User(\"ann\"), User(\"bob\"), User(\"cy\")\nfor u in (ann, bob, cy):\n    room.join(u)\nann.say(\"standup in 5\")\nbob.say(\"running late\", to=\"ann\")\nprint(ann.inbox, bob.inbox, cy.inbox, sep=\"\\n\")",
            "label": null,
            "output": "['bob: running late']\n['ann: standup in 5']\n['ann: standup in 5']",
            "isError": false
          }
        ]
      },
      {
        "title": "Iterator",
        "body": [
          {
            "type": "p",
            "html": "Give sequential access to a collection without exposing its structure. In Python this is built into the language: implement <code>__iter__</code> (usually as a generator) and the object works with <code>for</code>, comprehensions and every function that takes an iterable. The Deep Dive topic on generators covers the details."
          },
          {
            "type": "code",
            "src": "class Playlist:\n    def __init__(self, *songs):\n        self._songs = list(songs)\n    def __iter__(self):                         # default order\n        yield from self._songs\n    def shuffled(self, seed):                   # an alternative traversal\n        import random\n        order = self._songs[:]\n        random.Random(seed).shuffle(order)\n        yield from order\n\np = Playlist(\"intro\", \"verse\", \"chorus\", \"outro\")\nprint(list(p), list(p.shuffled(1)))",
            "label": null,
            "output": "['intro', 'verse', 'chorus', 'outro'] ['outro', 'intro', 'chorus', 'verse']",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Chain of Responsibility vs a list of handlers in a loop: what is the difference?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Functionally they are close, and in Python a list of handler functions iterated in order is often the clearest implementation. The classic linked form lets each handler decide to stop, pass on, or wrap the rest of the chain (call next and act on its result), which is how middleware implements before/after behaviour. Use the loop for simple filters and the linked form when handlers need to wrap the remainder of the pipeline."
          }
        ]
      },
      {
        "q": "When would you choose Visitor over adding a method to each class?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "When the set of classes is stable or not yours to modify (AST node types, a third-party document model) and new operations keep arriving (type checking, pretty printing, optimisation, code generation). Each operation then lives in one place instead of being smeared across every node class. If instead new node types arrive often, adding a method per class is better, because Visitor forces every existing operation to learn each new type."
          }
        ]
      },
      {
        "q": "How would you implement Ctrl+Z for a drawing app with both Command and Memento?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Use commands for actions with a cheap inverse (move shape by dx, dy; change colour, storing the old colour) and record each on the undo stack. For actions without a cheap inverse (apply a filter, boolean shape operations), the command captures a memento of the affected objects before executing and restores it on undo. A new action clears the redo stack. Cap the history and merge consecutive tiny commands (each keystroke of a drag) into one."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Refactoring.Guru: Chain of Responsibility",
        "url": "https://refactoring.guru/design-patterns/chain-of-responsibility"
      },
      {
        "label": "Python docs: functools.singledispatch",
        "url": "https://docs.python.org/3/library/functools.html#functools.singledispatch"
      },
      {
        "label": "PEP 636: Structural pattern matching tutorial",
        "url": "https://peps.python.org/pep-0636/"
      }
    ]
  },
  {
    "id": "parking-lot",
    "title": "Design a Parking Lot",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Factory",
      "Singleton"
    ],
    "level": "medium",
    "summary": "Multi-floor lot, vehicle and spot types, pluggable spot allocation and pricing, tickets and payment.",
    "intro": [
      "Design the software for a multi-floor parking garage. Vehicles of different sizes arrive at an entry gate, get a ticket for a suitable spot, and pay on exit according to a pricing policy. The garage owner wants to change how spots are chosen and how parking is priced without rewriting the system."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "<strong>In scope:</strong> floors with spots of three sizes (small, medium, large); vehicles (motorcycle, car, bus) that fit a spot of their size or larger; issue a ticket on entry, compute the fee on exit, free the spot; report free spots per floor; pluggable spot-allocation and pricing rules."
          },
          {
            "type": "p",
            "html": "<strong>Out of scope:</strong> reservations, payment processing details, multiple garages. Stating this keeps the design focused."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "&ldquo;Owner wants to change how spots are chosen&rdquo;",
                "Strategy (allocation)",
                "Nearest-first, fill-lowest-floor, spread-load are interchangeable algorithms"
              ],
              [
                "&ldquo;&hellip;and how parking is priced&rdquo;",
                "Strategy (pricing)",
                "Hourly, flat, peak-hour pricing vary independently of allocation"
              ],
              [
                "Vehicle types created from input at the gate",
                "Factory",
                "The gate creates the right vehicle from a type string"
              ],
              [
                "One garage, shared by all gates",
                "Singleton (or one injected instance)",
                "All gates must see the same spot state"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Vehicle sizes are data, not behaviour: an <code>Enum</code> with an ordering (small &lt; medium &lt; large) is enough, so the &ldquo;fits&rdquo; rule is one comparison instead of a class hierarchy."
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Size</code> (Enum)",
                "Ordered spot/vehicle sizes"
              ],
              [
                "<code>Vehicle</code>",
                "Plate and size; created by <code>Vehicle.of(kind, plate)</code>"
              ],
              [
                "<code>Spot</code>",
                "Id, floor, size, current vehicle"
              ],
              [
                "<code>Ticket</code>",
                "Vehicle, spot, entry time"
              ],
              [
                "<code>AllocationStrategy</code>",
                "Choose a free spot for a vehicle"
              ],
              [
                "<code>PricingStrategy</code>",
                "Fee from entry and exit times"
              ],
              [
                "<code>ParkingLot</code>",
                "Facade: <code>park</code>, <code>leave</code>, <code>availability</code>; owns spots and active tickets"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field\nfrom enum import IntEnum\nfrom itertools import count\nfrom typing import Protocol\nimport math\n\nclass Size(IntEnum):\n    SMALL = 1\n    MEDIUM = 2\n    LARGE = 3\n\n@dataclass(frozen=True)\nclass Vehicle:\n    plate: str\n    size: Size\n    KINDS = {\"motorcycle\": Size.SMALL, \"car\": Size.MEDIUM, \"bus\": Size.LARGE}\n\n    @classmethod\n    def of(cls, kind, plate):                       # factory\n        return cls(plate, cls.KINDS[kind])\n\n@dataclass\nclass Spot:\n    id: str\n    floor: int\n    size: Size\n    vehicle: Vehicle | None = None\n\n    def fits(self, v): return self.vehicle is None and self.size >= v.size\n\n@dataclass\nclass Ticket:\n    id: int\n    vehicle: Vehicle\n    spot: Spot\n    entry: float\n\nclass AllocationStrategy(Protocol):\n    def choose(self, spots: list[Spot], v: Vehicle) -> Spot | None: ...\n\nclass LowestFloorBestFit:\n    \"\"\"smallest spot that fits, on the lowest floor\"\"\"\n    def choose(self, spots, v):\n        free = [s for s in spots if s.fits(v)]\n        return min(free, key=lambda s: (s.floor, s.size), default=None)\n\nclass PricingStrategy(Protocol):\n    def fee(self, ticket: Ticket, exit_time: float) -> float: ...\n\nclass HourlyBySize:\n    RATES = {Size.SMALL: 10, Size.MEDIUM: 20, Size.LARGE: 50}\n    def fee(self, t, exit_time):\n        hours = max(1, math.ceil((exit_time - t.entry) / 3600))\n        return hours * self.RATES[t.spot.size]\n\nclass ParkingLot:\n    def __init__(self, floors, layout, allocator, pricing):\n        self.spots = [Spot(f\"F{f}-{i}\", f, size)\n                      for f in range(floors) for i, size in enumerate(layout)]\n        self.allocator, self.pricing = allocator, pricing\n        self.active: dict[str, Ticket] = {}\n        self._ids = count(1)\n\n    def park(self, v: Vehicle, now: float) -> Ticket:\n        if v.plate in self.active:\n            raise ValueError(f\"{v.plate} is already parked\")\n        spot = self.allocator.choose(self.spots, v)\n        if spot is None:\n            raise LookupError(f\"no spot for {v.plate} ({v.size.name})\")\n        spot.vehicle = v\n        t = Ticket(next(self._ids), v, spot, now)\n        self.active[v.plate] = t\n        return t\n\n    def leave(self, plate: str, now: float) -> float:\n        t = self.active.pop(plate)\n        t.spot.vehicle = None\n        return self.pricing.fee(t, now)\n\n    def availability(self):\n        out = {}\n        for s in self.spots:\n            if s.vehicle is None:\n                key = (s.floor, s.size.name)\n                out[key] = out.get(key, 0) + 1\n        return out\n\nlot = ParkingLot(floors=2, layout=[Size.SMALL, Size.MEDIUM, Size.MEDIUM, Size.LARGE],\n                 allocator=LowestFloorBestFit(), pricing=HourlyBySize())\narrivals = [(\"car\", \"KA-1\"), (\"motorcycle\", \"KA-2\"), (\"bus\", \"KA-3\"), (\"car\", \"KA-4\"),\n            (\"motorcycle\", \"KA-5\"), (\"bus\", \"KA-6\"), (\"bus\", \"KA-7\")]\nfor kind, plate in arrivals:\n    try:\n        t = lot.park(Vehicle.of(kind, plate), now=0)\n        print(f\"{kind:10} {plate} -> {t.spot.id} ({t.spot.size.name})\")\n    except LookupError as e:\n        print(\"LookupError:\", e)\nprint(\"fee for KA-1 after 2.5 h:\", lot.leave(\"KA-1\", now=2.5 * 3600))\nprint(\"free:\", lot.availability())",
            "label": null,
            "output": "car        KA-1 -> F0-1 (MEDIUM)\nmotorcycle KA-2 -> F0-0 (SMALL)\nbus        KA-3 -> F0-3 (LARGE)\ncar        KA-4 -> F0-2 (MEDIUM)\nmotorcycle KA-5 -> F1-0 (SMALL)\nbus        KA-6 -> F1-3 (LARGE)\nLookupError: no spot for KA-7 (LARGE)\nfee for KA-1 after 2.5 h: 60\nfree: {(0, 'MEDIUM'): 1, (1, 'MEDIUM'): 2}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Best fit kept the small spot for the first motorcycle and the large spot for the bus instead of handing them to cars. Floor 0 was full after four vehicles, so the second motorcycle went to the small spot on floor 1. When KA-7 arrived both large spots were taken, and a bus cannot use a smaller spot."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "&ldquo;Add peak-hour pricing&rdquo; and &ldquo;spread cars across floors&rdquo; are each one new strategy class; <code>ParkingLot</code> does not change."
          },
          {
            "type": "code",
            "src": "import math\n\nclass PeakHourPricing:\n    \"\"\"wraps another pricing strategy: 1.5x if the stay overlaps 17:00-20:00\"\"\"\n    def __init__(self, base, multiplier=1.5):\n        self.base, self.multiplier = base, multiplier\n    def fee(self, t, exit_time):\n        base = self.base.fee(t, exit_time)\n        peak = any(17 <= (h % 24) < 20 for h in range(int(t.entry // 3600), math.ceil(exit_time / 3600)))\n        return base * self.multiplier if peak else base\n\nclass FakeTicket:\n    def __init__(self, entry): self.entry = entry\n\nclass Flat:\n    def fee(self, t, exit_time): return 100\n\np = PeakHourPricing(Flat())\nprint(p.fee(FakeTicket(10 * 3600), 12 * 3600), p.fee(FakeTicket(16 * 3600), 18 * 3600))",
            "label": null,
            "output": "100 150.0",
            "isError": false
          },
          {
            "type": "p",
            "html": "Other likely follow-ups: EV spots (a spot attribute plus an allocation rule), multiple entry gates (all gates share one <code>ParkingLot</code>; <code>park</code> needs a lock so two gates never assign the same spot), and a display board (an observer notified on park and leave)."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Two entry gates call <code>park()</code> at the same moment. What can go wrong and how do you fix it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Both can pick the same free spot before either marks it occupied. Make choose-and-assign atomic: a lock around <code>park</code> (simple, fine for one process), or per-floor locks for more parallelism. In a distributed setup the spot assignment must be a conditional write in the database (<code>UPDATE spots SET vehicle=? WHERE id=? AND vehicle IS NULL</code>) and the gate retries with another spot if zero rows changed."
          }
        ]
      },
      {
        "q": "Why model vehicle types as an Enum rather than subclasses?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "They differ only in data (size), not behaviour. Subclasses would add classes with no methods of their own. If vehicle types later gained real behaviour (an EV needs charging, a bus needs two spots), introduce a hierarchy or a capability then. Design for the variation you can see."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "elevator",
    "title": "Design an Elevator System",
    "group": "Design problems",
    "tags": [
      "State",
      "Strategy",
      "Command"
    ],
    "level": "hard",
    "summary": "Several cars, hall and cabin requests, direction states, a pluggable dispatching algorithm, step-based simulation.",
    "intro": [
      "Design the controller for a building with N elevators. People press up/down buttons on floors (hall calls) and floor buttons inside a car (cabin calls). The controller decides which car serves each hall call, and each car moves floor by floor, stopping where it has requests."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "<strong>In scope:</strong> multiple cars; hall calls with direction; cabin calls; each car keeps serving in its current direction while it has stops ahead (the SCAN/elevator algorithm); a dispatcher assigns hall calls to cars; a step-by-step simulation so behaviour is testable."
          },
          {
            "type": "p",
            "html": "<strong>Out of scope:</strong> door timing, weight limits, emergency modes (mention them as extensions)."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "A car behaves differently when idle, moving up or moving down",
                "State",
                "The next stop and what &ldquo;step&rdquo; means depend on direction"
              ],
              [
                "&ldquo;Which car should take this call?&rdquo; has several reasonable answers",
                "Strategy (dispatcher)",
                "Nearest car, least busy, zoning can be swapped"
              ],
              [
                "Button presses are requests to be queued and processed",
                "Command",
                "Requests are objects that can be queued, logged and replayed in tests"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Direction</code> (Enum)",
                "UP, DOWN, IDLE"
              ],
              [
                "<code>Request</code>",
                "Floor and optional direction (a hall or cabin call)"
              ],
              [
                "<code>Car</code>",
                "Current floor, direction, set of stops; <code>step()</code> moves one floor"
              ],
              [
                "<code>Dispatcher</code>",
                "Strategy: pick a car for a hall call"
              ],
              [
                "<code>Controller</code>",
                "Accepts requests, routes them, advances the simulation"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field\nfrom enum import Enum\n\nclass Direction(Enum):\n    UP = 1\n    DOWN = -1\n    IDLE = 0\n\n@dataclass\nclass Car:\n    id: int\n    floor: int = 0\n    direction: Direction = Direction.IDLE\n    stops: set = field(default_factory=set)\n    log: list = field(default_factory=list)\n\n    def add_stop(self, floor):\n        if floor != self.floor or self.direction is not Direction.IDLE:\n            self.stops.add(floor)\n\n    def step(self):\n        \"\"\"one tick: open doors here, or move one floor (SCAN)\"\"\"\n        if self.floor in self.stops:\n            self.stops.discard(self.floor)\n            self.log.append(f\"stop@{self.floor}\")\n        if not self.stops:\n            self.direction = Direction.IDLE\n            return\n        ahead = [s for s in self.stops\n                 if (s - self.floor) * self.direction.value > 0] if self.direction is not Direction.IDLE else []\n        if not ahead:                                   # reverse (or start moving)\n            nearest = min(self.stops, key=lambda s: abs(s - self.floor))\n            self.direction = Direction.UP if nearest > self.floor else Direction.DOWN\n        self.floor += self.direction.value\n\n    def cost(self, floor, direction):\n        \"\"\"rough distance if this car takes a hall call\"\"\"\n        d = abs(self.floor - floor)\n        if self.direction is Direction.IDLE:\n            return d\n        moving_toward = (floor - self.floor) * self.direction.value >= 0\n        if moving_toward and direction is self.direction:\n            return d                                      # on the way\n        return d + 2 * len(self.stops) + 10               # must finish its sweep first\n\nclass NearestCarDispatcher:\n    def pick(self, cars, floor, direction):\n        return min(cars, key=lambda c: (c.cost(floor, direction), c.id))\n\nclass Controller:\n    def __init__(self, n_cars, dispatcher):\n        self.cars = [Car(i) for i in range(n_cars)]\n        self.dispatcher = dispatcher\n\n    def hall_call(self, floor, direction):\n        car = self.dispatcher.pick(self.cars, floor, direction)\n        car.add_stop(floor)\n        return car.id\n\n    def cabin_call(self, car_id, floor):\n        self.cars[car_id].add_stop(floor)\n\n    def tick(self, n=1):\n        for _ in range(n):\n            for c in self.cars:\n                c.step()\n\nctl = Controller(2, NearestCarDispatcher())\nctl.cars[1].floor = 10                                # car 1 parked at the top\nprint(\"hall call 3 UP  -> car\", ctl.hall_call(3, Direction.UP))\nprint(\"hall call 9 DOWN-> car\", ctl.hall_call(9, Direction.DOWN))\nctl.tick(3)\nctl.cabin_call(0, 7)                                  # passenger at 3 presses 7\nctl.cabin_call(1, 1)\nctl.tick(12)\nfor c in ctl.cars:\n    print(f\"car {c.id}: floor {c.floor}, {c.direction.name}, served {c.log}\")",
            "label": null,
            "output": "hall call 3 UP  -> car 0\nhall call 9 DOWN-> car 1\ncar 0: floor 7, IDLE, served ['stop@3', 'stop@7']\ncar 1: floor 1, IDLE, served ['stop@9', 'stop@1']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Each car sweeps in one direction while it has stops ahead and only then reverses, which bounds how long any request waits &mdash; the same reason disk schedulers use SCAN instead of always serving the nearest request."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A smarter dispatcher (estimate time including stops, or zone cars to floor ranges during morning rush) is a new strategy class. Door handling and maintenance mode fit as extra <code>Car</code> states. Making requests explicit command objects lets you log every button press and replay a day of traffic against two dispatchers to compare average wait time &mdash; the honest way to choose between them."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why not always send the nearest idle car?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Nearest-first ignores direction and existing load: a car three floors away moving the other way with five stops queued may take minutes to arrive, while a car eight floors away already heading toward the caller arrives sooner. It can also starve distant floors. Cost functions that account for direction and pending stops, or simulation-based estimates of arrival time, give better average and worst-case waits."
          }
        ]
      },
      {
        "q": "How would you test an elevator controller?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Make time discrete (<code>tick()</code>) and the dispatcher injectable, as above, so tests are deterministic: feed a script of requests at given ticks and assert on stop order, final positions and that every request is served within a bound. Add property-based tests: no car ever moves past the top or bottom floor, every requested floor is eventually visited, a car never reverses while it has stops ahead."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "vending-machine",
    "title": "Design a Vending Machine",
    "group": "Design problems",
    "tags": [
      "State"
    ],
    "level": "easy",
    "summary": "Coins, selection, dispensing and change, with every illegal action rejected by the current state.",
    "intro": [
      "Design a vending machine that accepts coins, lets the user select a product, dispenses it with change, and lets the user cancel to get their money back. An operator can restock products and coins."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Accept coins of fixed denominations; show balance; select a product by code; dispense if paid enough and in stock; return change using the coins in the machine; cancel returns the inserted coins. Reject operations that make no sense in the current state (selecting with no money, inserting coins while dispensing)."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Same buttons do different things depending on what has happened so far",
                "State",
                "Each state class handles only the actions legal in that state"
              ],
              [
                "Change must be made from limited coins",
                "Greedy with a check (or DP)",
                "An algorithm detail, not a pattern; refuse the sale if change cannot be made"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>VendingMachine</code>",
                "Context: inventory, coin box, inserted amount, current state"
              ],
              [
                "<code>Idle</code>, <code>HasMoney</code>",
                "States; each implements <code>insert</code>, <code>select</code>, <code>cancel</code>"
              ],
              [
                "<code>make_change</code>",
                "Compute change from available coins, or report it is impossible"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from collections import Counter\n\ndef make_change(amount, coins: Counter):\n    \"\"\"greedy over available coins; None if exact change is impossible\"\"\"\n    out = Counter()\n    for coin in sorted(coins, reverse=True):\n        take = min(amount // coin, coins[coin])\n        if take:\n            out[coin] = take\n            amount -= take * coin\n    return out if amount == 0 else None\n\nclass State:\n    def insert(self, m, coin): raise RuntimeError(f\"cannot insert in {type(self).__name__}\")\n    def select(self, m, code): raise RuntimeError(f\"cannot select in {type(self).__name__}\")\n    def cancel(self, m): raise RuntimeError(f\"nothing to cancel in {type(self).__name__}\")\n\nclass Idle(State):\n    def insert(self, m, coin):\n        m.accept(coin)\n        m.state = HasMoney()\n\nclass HasMoney(State):\n    def insert(self, m, coin):\n        m.accept(coin)\n\n    def select(self, m, code):\n        name, price, qty = m.products[code]\n        if qty == 0:\n            return f\"{name} is sold out\"\n        if m.balance < price:\n            return f\"insert {price - m.balance} more for {name}\"\n        change = make_change(m.balance - price, m.coins)\n        if change is None:\n            return \"cannot make change, use exact amount\"\n        m.coins -= change\n        m.products[code] = (name, price, qty - 1)\n        m.balance, m.inserted = 0, Counter()\n        m.state = Idle()\n        return f\"dispensed {name}, change {dict(change) or 0}\"\n\n    def cancel(self, m):\n        refund = m.inserted\n        m.coins -= refund\n        m.balance, m.inserted = 0, Counter()\n        m.state = Idle()\n        return f\"refunded {dict(refund)}\"\n\nclass VendingMachine:\n    COINS = {1, 2, 5, 10}\n\n    def __init__(self, products, coins):\n        self.products, self.coins = products, Counter(coins)\n        self.balance, self.inserted, self.state = 0, Counter(), Idle()\n\n    def accept(self, coin):\n        if coin not in self.COINS:\n            raise ValueError(f\"coin {coin} rejected\")\n        self.balance += coin\n        self.inserted[coin] += 1\n        self.coins[coin] += 1\n\n    def insert(self, coin): return self.state.insert(self, coin)\n    def select(self, code): return self.state.select(self, code)\n    def cancel(self): return self.state.cancel(self)\n\nvm = VendingMachine({\"A1\": (\"chips\", 15, 2), \"B1\": (\"cola\", 25, 0)}, {1: 3, 2: 2, 5: 1})\ntry:\n    vm.select(\"A1\")\nexcept RuntimeError as e:\n    print(\"RuntimeError:\", e)\nvm.insert(10)\nprint(vm.select(\"A1\"))\nvm.insert(10)\nprint(vm.select(\"A1\"))\nvm.insert(10); vm.insert(5); vm.insert(10)\nprint(vm.select(\"B1\"))\nprint(vm.cancel())",
            "label": null,
            "output": "RuntimeError: cannot select in Idle\ninsert 5 more for chips\ndispensed chips, change {5: 1}\ncola is sold out\nrefunded {10: 2, 5: 1}",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A <code>Maintenance</code> state for restocking (rejects customers, accepts <code>restock</code>), card payments (a new payment input that also moves Idle to HasMoney), and a sold-out display (an observer on inventory) all slot in without changing existing states."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Greedy change-making can fail even when change is possible. When, and what would you do?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Greedy is optimal for canonical coin systems like 1/2/5/10, but with arbitrary denominations or limited coin counts it can fail: owing 6 with coins {5: 1, 3: 2} greedy takes 5 and is stuck, while 3+3 works. Use a bounded-knapsack DP over the available coins when the coin set is not canonical or stock is low; it is tiny for vending-machine amounts."
          }
        ]
      },
      {
        "q": "Why is the State pattern better here than an <code>if state == ...</code> switch?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Every operation (insert, select, cancel, restock, refund) would need its own switch over every state, and adding a state means editing all of them. With state classes, the legal actions of each state are listed in one place, illegal ones fail by default in the base class, and adding a state is a new class."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "atm",
    "title": "Design an ATM",
    "group": "Design problems",
    "tags": [
      "State",
      "Chain of Responsibility",
      "Facade"
    ],
    "level": "medium",
    "summary": "Card and PIN session states, withdrawals dispensed through a chain of note handlers, bank behind a facade.",
    "intro": [
      "Design an ATM that reads a card, verifies the PIN with the bank (three attempts), lets the user check balance or withdraw cash, and dispenses notes from its cassettes. The bank's systems are external."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Session flow: insert card &rarr; enter PIN (lock card after 3 failures) &rarr; choose transaction &rarr; eject card. Withdrawals must be multiples the machine can dispense with the notes it has; the account is debited only if dispensing is possible."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Card inserted, authenticated, card ejected: actions allowed differ by step",
                "State",
                "Session states guard the flow"
              ],
              [
                "Dispense using 2000s, then 500s, then 100s",
                "Chain of Responsibility",
                "Each cassette handles what it can and passes the remainder on"
              ],
              [
                "The ATM talks to a complex bank system",
                "Facade",
                "One narrow <code>BankService</code> interface: verify PIN, balance, debit"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>BankService</code>",
                "Facade over the bank: <code>verify</code>, <code>balance</code>, <code>debit</code>"
              ],
              [
                "<code>Cassette</code>",
                "A note denomination and count; link in the dispensing chain"
              ],
              [
                "<code>ATM</code>",
                "Session context with the current state"
              ],
              [
                "<code>NoCard</code>, <code>CardInserted</code>, <code>Authenticated</code>",
                "Session states"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "class BankService:\n    def __init__(self):\n        self.accounts = {\"4111\": {\"pin\": \"1234\", \"balance\": 12_000}}\n    def verify(self, card, pin): return self.accounts[card][\"pin\"] == pin\n    def balance(self, card): return self.accounts[card][\"balance\"]\n    def debit(self, card, amount):\n        acct = self.accounts[card]\n        if acct[\"balance\"] < amount:\n            raise ValueError(\"insufficient funds\")\n        acct[\"balance\"] -= amount\n\nclass Cassette:\n    def __init__(self, note, count, next_=None):\n        self.note, self.count, self.next = note, count, next_\n\n    def plan(self, amount):\n        \"\"\"returns [(note, n), ...] or raises; does not change counts\"\"\"\n        n = min(amount // self.note, self.count)\n        rest = amount - n * self.note\n        tail = self.next.plan(rest) if rest and self.next else []\n        if rest and not self.next:\n            raise ValueError(f\"cannot dispense {rest}\")\n        return ([(self.note, n)] if n else []) + tail\n\n    def take(self, plan):\n        for note, n in plan:\n            c = self\n            while c.note != note:\n                c = c.next\n            c.count -= n\n\nclass State:\n    def __init__(self, atm): self.atm = atm\n    def insert(self, card): return \"card already inside\"\n    def pin(self, pin): return \"insert a card first\"\n    def withdraw(self, amount): return \"not authenticated\"\n    def eject(self): return \"no card\"\n\nclass NoCard(State):\n    def insert(self, card):\n        self.atm.card, self.atm.tries = card, 0\n        self.atm.state = CardInserted(self.atm)\n        return \"enter PIN\"\n\nclass CardInserted(State):\n    def pin(self, pin):\n        if self.atm.bank.verify(self.atm.card, pin):\n            self.atm.state = Authenticated(self.atm)\n            return \"PIN ok\"\n        self.atm.tries += 1\n        if self.atm.tries >= 3:\n            self.atm.state = NoCard(self.atm)\n            return \"card retained\"\n        return f\"wrong PIN, {3 - self.atm.tries} tries left\"\n    def eject(self):\n        self.atm.state = NoCard(self.atm); return \"card ejected\"\n\nclass Authenticated(State):\n    def withdraw(self, amount):\n        try:\n            plan = self.atm.cash.plan(amount)          # can we dispense?\n            self.atm.bank.debit(self.atm.card, amount)  # then debit\n        except ValueError as e:\n            return f\"declined: {e}\"\n        self.atm.cash.take(plan)\n        return f\"dispensed {plan}\"\n    def eject(self):\n        self.atm.state = NoCard(self.atm); return \"card ejected\"\n\nclass ATM:\n    def __init__(self, bank, cash):\n        self.bank, self.cash, self.card, self.tries = bank, cash, None, 0\n        self.state = NoCard(self)\n    def __getattr__(self, action):                    # forward actions to the state\n        return getattr(self.state, action)\n\natm = ATM(BankService(), Cassette(2000, 2, Cassette(500, 4, Cassette(100, 10))))\nfor step in [(\"withdraw\", 100), (\"insert\", \"4111\"), (\"pin\", \"0000\"), (\"pin\", \"1234\"),\n             (\"withdraw\", 5600), (\"withdraw\", 5650), (\"withdraw\", 9000), (\"eject\",)]:\n    print(f\"{step[0]:8} {str(step[1:]):10} -> {getattr(atm, step[0])(*step[1:])}\")\nprint(\"bank balance:\", atm.bank.balance(\"4111\"))",
            "label": null,
            "output": "withdraw (100,)     -> not authenticated\ninsert   ('4111',)  -> enter PIN\npin      ('0000',)  -> wrong PIN, 2 tries left\npin      ('1234',)  -> PIN ok\nwithdraw (5600,)    -> dispensed [(2000, 2), (500, 3), (100, 1)]\nwithdraw (5650,)    -> declined: cannot dispense 4250\nwithdraw (9000,)    -> declined: cannot dispense 7600\neject    ()         -> card ejected\nbank balance: 6400",
            "isError": false
          },
          {
            "type": "p",
            "html": "Note the order in <code>withdraw</code>: plan the notes first, debit second, take the notes last. Debiting before checking the cassettes would take money for cash the machine cannot give."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Deposits, mini-statements and PIN change are new methods on <code>Authenticated</code>. Real ATMs also need a <em>reversal</em>: if the debit succeeded but the dispenser jams, the ATM sends a compensating credit to the bank. That is a saga step, logged durably before dispensing."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "The bank debit succeeded but the cash dispenser failed. How should the system recover?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Record a durable journal entry before each step (debit requested, debit confirmed, dispense started, dispense confirmed). On dispenser failure, send a reversal (credit) to the bank with the same transaction id, so it is idempotent if retried. If the ATM crashes mid-way, on restart it reads the journal and either completes the reversal or reconciles with the bank. Physical counts in the cassettes are reconciled at the next cash refill."
          }
        ]
      },
      {
        "q": "Why use Chain of Responsibility for dispensing instead of one function?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A single greedy function is fine for a fixed set of denominations. The chain makes each cassette an independent object with its own count and lets the machine's configuration (which cassettes exist, in what order) be assembled at start-up. A cassette that is empty or faulty is simply skipped. Either answer is acceptable if you explain the trade-off."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "library",
    "title": "Design a Library Management System",
    "group": "Design problems",
    "tags": [
      "Observer",
      "Strategy",
      "Repository"
    ],
    "level": "medium",
    "summary": "Books vs copies, loans with limits and due dates, reservations notified on return, pluggable fines.",
    "intro": [
      "Design a library system. Members borrow and return physical copies of books, can reserve a title that is fully on loan, and are notified when a reserved title comes back. Late returns are fined."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "A book (title) has many copies. A member may hold at most 3 loans. Loans last 14 days. If all copies of a title are out, a member can join a FIFO reservation queue; when a copy is returned, it is held for the first person in the queue and they are notified. Fines are computed by a policy that may change."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "&ldquo;Notify the member when the book comes back&rdquo;",
                "Observer",
                "Returning a copy publishes an event; notification channels subscribe"
              ],
              [
                "Fine rules change (per-day, capped, waived for students)",
                "Strategy",
                "Fine policy is injected"
              ],
              [
                "Look up copies, members and loans by id",
                "Repository",
                "Keeps storage details out of the domain logic (in-memory here)"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Book</code>, <code>Copy</code>",
                "A title and its physical copies (barcode, status)"
              ],
              [
                "<code>Member</code>",
                "Id, name, current loans"
              ],
              [
                "<code>Loan</code>",
                "Copy, member, due date, returned date"
              ],
              [
                "<code>FinePolicy</code>",
                "Strategy: fine for a late loan"
              ],
              [
                "<code>Library</code>",
                "Facade: <code>borrow</code>, <code>give_back</code>, <code>reserve</code>; publishes events"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from collections import defaultdict, deque\nfrom dataclasses import dataclass, field\n\n@dataclass\nclass Copy:\n    barcode: str\n    isbn: str\n    status: str = \"available\"          # available | on_loan | on_hold\n    held_for: str | None = None\n\n@dataclass\nclass Loan:\n    copy: Copy\n    member: str\n    due: int\n    returned: int | None = None\n\nclass PerDayCapped:\n    def __init__(self, per_day=5, cap=100): self.per_day, self.cap = per_day, cap\n    def fine(self, loan): return min(self.cap, max(0, loan.returned - loan.due) * self.per_day)\n\nclass Library:\n    MAX_LOANS, LOAN_DAYS = 3, 14\n\n    def __init__(self, fine_policy):\n        self.copies: dict[str, Copy] = {}\n        self.titles: dict[str, str] = {}\n        self.loans: dict[str, Loan] = {}                 # barcode -> active loan\n        self.queue: dict[str, deque] = defaultdict(deque) # isbn -> members waiting\n        self.listeners = []\n        self.fines = fine_policy\n\n    def add(self, isbn, title, *barcodes):\n        self.titles[isbn] = title\n        for b in barcodes:\n            self.copies[b] = Copy(b, isbn)\n\n    def on_event(self, fn): self.listeners.append(fn)\n    def _emit(self, *args): [fn(*args) for fn in self.listeners]\n\n    def borrow(self, member, isbn, today):\n        if sum(l.member == member for l in self.loans.values()) >= self.MAX_LOANS:\n            raise PermissionError(f\"{member} has {self.MAX_LOANS} loans\")\n        copy = next((c for c in self.copies.values() if c.isbn == isbn and\n                     (c.status == \"available\" or c.held_for == member)), None)\n        if copy is None:\n            raise LookupError(f\"no copy of {self.titles[isbn]!r} free; reserve it\")\n        if member in self.queue[isbn]:\n            self.queue[isbn].remove(member)\n        copy.status, copy.held_for = \"on_loan\", None\n        self.loans[copy.barcode] = Loan(copy, member, today + self.LOAN_DAYS)\n        return copy.barcode\n\n    def reserve(self, member, isbn):\n        self.queue[isbn].append(member)\n\n    def give_back(self, barcode, today):\n        loan = self.loans.pop(barcode)\n        loan.returned = today\n        copy = loan.copy\n        if self.queue[copy.isbn]:\n            nxt = self.queue[copy.isbn][0]\n            copy.status, copy.held_for = \"on_hold\", nxt\n            self._emit(\"hold_ready\", nxt, self.titles[copy.isbn])\n        else:\n            copy.status = \"available\"\n        return self.fines.fine(loan)\n\nlib = Library(PerDayCapped())\nlib.on_event(lambda event, who, title: print(f\"  notify {who}: {title!r} is waiting for you\"))\nlib.add(\"978-0\", \"Dune\", \"D1\")\nlib.add(\"978-1\", \"Emma\", \"E1\", \"E2\")\n\nb = lib.borrow(\"ann\", \"978-0\", today=0)\ntry:\n    lib.borrow(\"bob\", \"978-0\", today=1)\nexcept LookupError as e:\n    print(\"LookupError:\", e)\nlib.reserve(\"bob\", \"978-0\")\nprint(\"ann's fine:\", lib.give_back(b, today=20))\ntry:\n    lib.borrow(\"cy\", \"978-0\", today=21)\nexcept LookupError as e:\n    print(\"cy:\", e)\nprint(\"bob borrows:\", lib.borrow(\"bob\", \"978-0\", today=21))",
            "label": null,
            "output": "LookupError: no copy of 'Dune' free; reserve it\n  notify bob: 'Dune' is waiting for you\nann's fine: 30\ncy: no copy of 'Dune' free; reserve it\nbob borrows: D1",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Email and SMS notifications are listeners added at start-up. A student fine waiver is a different <code>FinePolicy</code>, or a decorator around one. Holds that expire after 3 days need a scheduled job that releases the hold to the next member in the queue."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why separate <code>Book</code> (title) from <code>Copy</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Different identities and lifecycles. Catalogue data (title, author, ISBN) is shared by all copies; status, barcode, condition and loans belong to each physical copy. Reservations are on the title (any copy will do), loans are on a copy. Merging them forces duplicated catalogue data or breaks as soon as the library buys a second copy."
          }
        ]
      },
      {
        "q": "How would you prevent two librarians lending the last copy to two people at once?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The status change from available to on_loan must be atomic. In one process, a lock around borrow; with a database, a conditional update (<code>UPDATE copies SET status='on_loan' WHERE barcode=? AND status='available'</code>) and check the row count, or a unique constraint on active loans per copy."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "movie-booking",
    "title": "Design a Movie Ticket Booking System",
    "group": "Design problems",
    "tags": [
      "State",
      "Strategy",
      "Observer"
    ],
    "level": "hard",
    "summary": "Shows and seats, temporary seat holds with expiry, concurrent booking without double-selling, pricing strategies.",
    "intro": [
      "Design the booking core of a BookMyShow-style app. Users pick a show, select seats, and have a few minutes to pay. Seats being paid for must not be sold to anyone else, and seats from abandoned checkouts must become available again."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Cities, cinemas, screens and movies are catalogue data; the core is a <code>Show</code> (movie, screen, time) with a seat map. Booking flow: hold selected seats (all or nothing) for 5 minutes &rarr; pay &rarr; confirm, or let the hold expire. Many users book the same show concurrently. Price depends on seat category and may include dynamic rules (weekend, demand)."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Seat is available, held, or booked; holds expire",
                "State (per seat)",
                "Legal transitions: available &rarr; held &rarr; booked, held &rarr; available on expiry"
              ],
              [
                "Many users select seats at once",
                "Lock / atomic check-and-set",
                "Concurrency control, not a GoF pattern, but the heart of the problem"
              ],
              [
                "Weekend and demand-based pricing",
                "Strategy",
                "Pricing rules vary and stack"
              ],
              [
                "Send confirmation, update analytics on booking",
                "Observer",
                "Side effects decoupled from booking"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Seat</code>",
                "Id, category, state, hold owner and expiry"
              ],
              [
                "<code>Show</code>",
                "Seat map plus a lock; <code>hold</code>, <code>confirm</code>, <code>release_expired</code>"
              ],
              [
                "<code>PricingRule</code>",
                "Strategy: adjust a base price"
              ],
              [
                "<code>BookingService</code>",
                "Orchestrates hold, price, payment, confirm; emits events"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import threading\nfrom dataclasses import dataclass\n\nHOLD_SECONDS = 300\n\n@dataclass\nclass Seat:\n    id: str\n    category: str\n    state: str = \"available\"       # available | held | booked\n    holder: str | None = None\n    expires: float = 0.0\n\nclass Show:\n    def __init__(self, seats):\n        self.seats = {s.id: s for s in seats}\n        self.lock = threading.Lock()\n\n    def _free(self, seat, now):\n        return seat.state == \"available\" or (seat.state == \"held\" and seat.expires <= now)\n\n    def hold(self, user, ids, now):\n        with self.lock:                                 # all-or-nothing, atomically\n            seats = [self.seats[i] for i in ids]\n            if not all(self._free(s, now) for s in seats):\n                return False\n            for s in seats:\n                s.state, s.holder, s.expires = \"held\", user, now + HOLD_SECONDS\n            return True\n\n    def confirm(self, user, ids, now):\n        with self.lock:\n            seats = [self.seats[i] for i in ids]\n            if not all(s.state == \"held\" and s.holder == user and s.expires > now for s in seats):\n                return False                            # hold lost or expired\n            for s in seats:\n                s.state = \"booked\"\n            return True\n\nBASE = {\"regular\": 200, \"premium\": 350}\n\nclass WeekendSurcharge:\n    def apply(self, price, ctx): return price * 1.2 if ctx[\"weekend\"] else price\n\nclass DemandSurge:\n    def apply(self, price, ctx): return price * 1.25 if ctx[\"occupancy\"] > 0.8 else price\n\nclass BookingService:\n    def __init__(self, rules, listeners=()):\n        self.rules, self.listeners = rules, list(listeners)\n\n    def quote(self, show, ids, ctx):\n        total = 0\n        for i in ids:\n            p = BASE[show.seats[i].category]\n            for r in self.rules:\n                p = r.apply(p, ctx)\n            total += p\n        return round(total)\n\n    def book(self, show, user, ids, ctx, pay, now):\n        if not show.hold(user, ids, now):\n            return f\"{user}: seats {ids} not available\"\n        amount = self.quote(show, ids, ctx)\n        if not pay(user, amount):\n            return f\"{user}: payment failed, hold will expire\"\n        if not show.confirm(user, ids, now + 60):\n            return f\"{user}: hold expired before payment\"\n        for fn in self.listeners:\n            fn(user, ids, amount)\n        return f\"{user}: booked {ids} for {amount}\"\n\nshow = Show([Seat(f\"A{i}\", \"premium\") for i in range(1, 4)] + [Seat(f\"B{i}\", \"regular\") for i in range(1, 5)])\nsvc = BookingService([WeekendSurcharge(), DemandSurge()],\n                     [lambda u, ids, amt: print(f\"  email to {u}: tickets {ids}\")])\nctx = {\"weekend\": True, \"occupancy\": 0.5}\n\n# 20 users race for the same two seats\nresults, start = [], threading.Barrier(20)\ndef attempt(i):\n    start.wait()\n    results.append(show.hold(f\"user{i}\", [\"A1\", \"A2\"], now=0))\nthreads = [threading.Thread(target=attempt, args=(i,)) for i in range(20)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint(\"holds granted for A1+A2:\", results.count(True), \"of\", len(results))\n\nprint(svc.book(show, \"ann\", [\"B1\", \"B2\"], ctx, pay=lambda u, a: True, now=0))\nprint(svc.book(show, \"bob\", [\"B2\", \"B3\"], ctx, pay=lambda u, a: True, now=0))\nprint(svc.book(show, \"cy\", [\"B3\"], ctx, pay=lambda u, a: False, now=0))\nprint(svc.book(show, \"dee\", [\"B3\"], ctx, pay=lambda u, a: True, now=HOLD_SECONDS + 1))",
            "label": null,
            "output": "holds granted for A1+A2: 1 of 20\n  email to ann: tickets ['B1', 'B2']\nann: booked ['B1', 'B2'] for 480\nbob: seats ['B2', 'B3'] not available\ncy: payment failed, hold will expire\n  email to dee: tickets ['B3']\ndee: booked ['B3'] for 240",
            "isError": false
          },
          {
            "type": "p",
            "html": "Exactly one of the twenty racing users got the two seats. Cy's failed payment left B3 held, but the hold expired, so Dee could book it five minutes later without any cleanup job running &mdash; expiry is checked lazily whenever a seat is examined."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "In a multi-server deployment the lock moves into the data store: a conditional update per seat (<code>WHERE state='available' OR expires &lt; now</code>) inside a transaction, or Redis <code>SET seat:show:A1 user NX EX 300</code> for holds. Payment callbacks carry the hold id so a late callback for an expired hold is refunded rather than confirmed."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you stop two users from buying the same seat when you have 20 app servers?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Make the state change atomic in the shared store. With SQL: in one transaction, <code>UPDATE seats SET state='held', holder=?, expires=? WHERE show_id=? AND seat_id IN (...) AND (state='available' OR (state='held' AND expires &lt; now()))</code>, and commit only if the row count equals the number of seats requested; otherwise roll back. A unique index on (show, seat) for confirmed bookings is the last line of defence. With Redis, <code>SET NX EX</code> per seat (or a Lua script for all-or-nothing). Never check availability in one request and write in another without a condition."
          }
        ]
      },
      {
        "q": "Why hold seats with an expiry instead of locking them until payment completes?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Users abandon checkouts constantly. A lock without a timeout would leave seats stuck forever when a browser closes. An expiring hold bounds how long a seat can be blocked, needs no cleanup job (expiry is checked when the seat is read), and the confirm step re-checks that the hold is still valid before marking the seat booked."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "hotel-booking",
    "title": "Design a Hotel Reservation System",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Repository",
      "Factory"
    ],
    "level": "medium",
    "summary": "Room types, availability over date ranges, overlap checks, room assignment and cancellation policies.",
    "intro": [
      "Design the reservation core for a hotel: guests search for a room type over a date range, book it, and may cancel under a policy. Rooms are assigned at booking time."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Rooms have a type (single, double, suite) and a nightly rate. A booking covers check-in to check-out (check-out day is free for the next guest). Search returns room types with at least one free room for the whole range. Cancellation refunds depend on the policy attached to the booking (flexible, moderate, non-refundable)."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Availability over date ranges",
                "Interval overlap check",
                "Two stays overlap iff <code>a.start &lt; b.end and b.start &lt; a.end</code>"
              ],
              [
                "Which free room of the type to assign",
                "Strategy",
                "Lowest floor, same room as last visit, spread wear"
              ],
              [
                "Different cancellation rules per rate plan",
                "Strategy",
                "The policy object travels with the booking"
              ],
              [
                "Bookings stored and queried by room",
                "Repository",
                "Domain code asks for &ldquo;bookings of room 101&rdquo;, not SQL"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Room</code>",
                "Number, type, nightly rate"
              ],
              [
                "<code>Booking</code>",
                "Room, guest, check-in, check-out, policy, status"
              ],
              [
                "<code>BookingRepository</code>",
                "Bookings by room; overlap queries"
              ],
              [
                "<code>CancellationPolicy</code>",
                "Strategy: refund for a cancellation date"
              ],
              [
                "<code>Hotel</code>",
                "Facade: <code>search</code>, <code>book</code>, <code>cancel</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from collections import defaultdict\nfrom dataclasses import dataclass\nfrom datetime import date, timedelta\n\n@dataclass(frozen=True)\nclass Room:\n    number: int\n    type: str\n    rate: int\n\n@dataclass\nclass Booking:\n    id: int\n    room: Room\n    guest: str\n    check_in: date\n    check_out: date\n    policy: object\n    status: str = \"confirmed\"\n\n    def nights(self): return (self.check_out - self.check_in).days\n    def overlaps(self, start, end): return self.check_in < end and start < self.check_out\n\nclass Flexible:\n    def refund(self, b, today):\n        return 1.0 if (b.check_in - today).days >= 1 else 0.0\n\nclass Moderate:\n    def refund(self, b, today):\n        days = (b.check_in - today).days\n        return 1.0 if days >= 7 else 0.5 if days >= 2 else 0.0\n\nclass NonRefundable:\n    def refund(self, b, today): return 0.0\n\nclass BookingRepository:\n    def __init__(self): self.by_room = defaultdict(list)\n    def add(self, b): self.by_room[b.room.number].append(b)\n    def is_free(self, room, start, end):\n        return not any(b.status == \"confirmed\" and b.overlaps(start, end)\n                       for b in self.by_room[room.number])\n\nclass Hotel:\n    def __init__(self, rooms, repo):\n        self.rooms, self.repo, self.next_id = rooms, repo, 1\n\n    def free_rooms(self, room_type, start, end):\n        return [r for r in self.rooms if r.type == room_type and self.repo.is_free(r, start, end)]\n\n    def search(self, start, end):\n        types = sorted({r.type for r in self.rooms})\n        return {t: len(self.free_rooms(t, start, end)) for t in types}\n\n    def book(self, guest, room_type, start, end, policy):\n        if end <= start:\n            raise ValueError(\"check-out must be after check-in\")\n        free = self.free_rooms(room_type, start, end)\n        if not free:\n            raise LookupError(f\"no {room_type} free {start}..{end}\")\n        room = min(free, key=lambda r: r.number)        # assignment strategy\n        b = Booking(self.next_id, room, guest, start, end, policy)\n        self.next_id += 1\n        self.repo.add(b)\n        return b\n\n    def cancel(self, b, today):\n        b.status = \"cancelled\"\n        return round(b.nights() * b.room.rate * b.policy.refund(b, today))\n\nd = lambda day: date(2026, 12, day)\nhotel = Hotel([Room(101, \"double\", 120), Room(102, \"double\", 120), Room(201, \"suite\", 300)],\n              BookingRepository())\nb1 = hotel.book(\"ann\", \"double\", d(20), d(23), Moderate())\nb2 = hotel.book(\"bob\", \"double\", d(22), d(24), Flexible())\nprint(\"rooms:\", b1.room.number, b2.room.number)\nprint(\"search 22-23:\", hotel.search(d(22), d(23)))\nprint(\"search 23-25:\", hotel.search(d(23), d(25)), \"(ann checks out on the 23rd)\")\ntry:\n    hotel.book(\"cy\", \"double\", d(21), d(23), NonRefundable())\nexcept LookupError as e:\n    print(\"LookupError:\", e)\nprint(\"ann cancels 10 days early, refund:\", hotel.cancel(b1, d(10)))\nprint(\"now cy can book:\", hotel.book(\"cy\", \"double\", d(21), d(23), NonRefundable()).room.number)",
            "label": null,
            "output": "rooms: 101 102\nsearch 22-23: {'double': 0, 'suite': 1}\nsearch 23-25: {'double': 1, 'suite': 1} (ann checks out on the 23rd)\nLookupError: no double free 2026-12-21..2026-12-23\nann cancels 10 days early, refund: 360\nnow cy can book: 101",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Overbooking (sell 102% of rooms and rely on cancellations) is a different availability strategy. Rate plans with seasonal prices replace <code>Room.rate</code> with a pricing strategy over dates. At scale, availability is precomputed per (room type, night) as a counter decremented atomically on booking, rather than scanning bookings."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why is the overlap condition <code>a.start &lt; b.end and b.start &lt; a.end</code>, and why half-open ranges?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Two intervals fail to overlap only if one ends before the other starts; negating that gives the condition. Using half-open ranges [check-in, check-out) means a guest checking out on the 23rd and another checking in on the 23rd do not conflict, which matches how hotels work, and the arithmetic needs no &plusmn;1 corrections."
          }
        ]
      },
      {
        "q": "How would you make availability search fast for a hotel chain with millions of bookings?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Store an inventory table keyed by (hotel, room type, night) with the count of rooms still sellable. Search for a range is a range read of N rows and a min; booking decrements every night in the range in one transaction with a <code>WHERE available &gt; 0</code> guard. Specific room assignment can happen later, at check-in. This is how large booking systems separate &ldquo;can I sell it&rdquo; from &ldquo;which physical room&rdquo;."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "meeting-room-scheduler",
    "title": "Design a Meeting Room Scheduler",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Observer"
    ],
    "level": "medium",
    "summary": "Rooms with capacity, conflict-free booking over time slots, room selection strategy, invite notifications.",
    "intro": [
      "Design a scheduler that books meeting rooms for a time slot and a number of attendees, picks a suitable room, and notifies invitees. It should also answer &ldquo;which rooms are free from 2 to 3 pm?&rdquo;."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Rooms have a name and capacity. A booking needs a slot [start, end) and attendee count; it must not overlap another booking of the same room. Choose the smallest room that fits (so big rooms stay free), but allow other strategies. Invitees are notified on booking and cancellation."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "&ldquo;Pick a suitable room&rdquo; with a preference that may change",
                "Strategy",
                "Best-fit, nearest to the organiser, preferred floor"
              ],
              [
                "Notify invitees",
                "Observer",
                "Calendar, email and chat integrations subscribe"
              ],
              [
                "No overlapping bookings per room",
                "Sorted intervals + bisect",
                "O(log n) conflict check per room"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Room</code>",
                "Name, capacity, sorted list of bookings"
              ],
              [
                "<code>RoomSelector</code>",
                "Strategy: choose among free rooms"
              ],
              [
                "<code>Scheduler</code>",
                "<code>book</code>, <code>cancel</code>, <code>free_rooms</code>; notifies listeners"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import bisect\nfrom dataclasses import dataclass, field\n\n@dataclass\nclass Room:\n    name: str\n    capacity: int\n    slots: list = field(default_factory=list)      # sorted [(start, end, title)]\n\n    def is_free(self, start, end):\n        i = bisect.bisect_left(self.slots, (start,))\n        before_ok = i == 0 or self.slots[i - 1][1] <= start\n        after_ok = i == len(self.slots) or end <= self.slots[i][0]\n        return before_ok and after_ok\n\n    def add(self, start, end, title):\n        bisect.insort(self.slots, (start, end, title))\n\nclass BestFit:\n    def choose(self, rooms, people):\n        return min(rooms, key=lambda r: (r.capacity, r.name), default=None)\n\nclass Scheduler:\n    def __init__(self, rooms, selector):\n        self.rooms, self.selector, self.listeners = rooms, selector, []\n\n    def free_rooms(self, start, end, people=1):\n        return [r for r in self.rooms if r.capacity >= people and r.is_free(start, end)]\n\n    def book(self, title, start, end, invitees):\n        room = self.selector.choose(self.free_rooms(start, end, len(invitees)), len(invitees))\n        if room is None:\n            raise LookupError(f\"no room for {len(invitees)} people {start}-{end}\")\n        room.add(start, end, title)\n        for fn in self.listeners:\n            fn(invitees, f\"{title} in {room.name} {start}-{end}\")\n        return room.name\n\nsched = Scheduler([Room(\"Pod\", 4), Room(\"Board\", 12), Room(\"Cave\", 6)], BestFit())\nsched.listeners.append(lambda who, msg: print(f\"  invite {len(who)} people: {msg}\"))\n\nprint(sched.book(\"standup\", 900, 915, [\"a\", \"b\", \"c\"]))\nprint(sched.book(\"design review\", 900, 1000, [\"a\", \"b\", \"c\", \"d\", \"e\"]))\nprint(sched.book(\"1:1\", 910, 930, [\"a\", \"b\"]))\nprint(sched.book(\"all hands\", 1000, 1100, list(\"abcdefghij\")))\nprint(\"free 9:20-9:40 for 2:\", [r.name for r in sched.free_rooms(920, 940, 2)])\ntry:\n    sched.book(\"offsite\", 1030, 1130, list(\"abcdefghij\"))\nexcept LookupError as e:\n    print(\"LookupError:\", e)",
            "label": null,
            "output": "  invite 3 people: standup in Pod 900-915\nPod\n  invite 5 people: design review in Cave 900-1000\nCave\n  invite 2 people: 1:1 in Board 910-930\nBoard\n  invite 10 people: all hands in Board 1000-1100\nBoard\nfree 9:20-9:40 for 2: ['Pod']\nLookupError: no room for 10 people 1030-1130",
            "isError": false
          },
          {
            "type": "p",
            "html": "The 1:1 at 9:10 could not use the Pod (taken by the standup until 9:15) or the Cave (design review), so best fit gave it the Board room &mdash; the only free room left. A smarter strategy might suggest moving it by five minutes instead; that is exactly the kind of change a selector strategy absorbs."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Recurring meetings expand into individual slots (or store a recurrence rule and check overlaps against its expansion). &ldquo;Find a time when all invitees are free&rdquo; merges their busy intervals and scans the gaps &mdash; the Merge Intervals problem."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you check for conflicts efficiently when a room has thousands of bookings?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Keep each room's bookings sorted by start time. A new slot [s, e) conflicts only with its neighbours in that order: the booking just before it (must end by s) and the booking just after it (must start at or after e). <code>bisect</code> finds the position in O(log n). A balanced tree or interval tree does the same with O(log n) inserts; a database does it with an index on (room, start) and a range query."
          }
        ]
      },
      {
        "q": "How would you find the earliest slot where five specific people and a room are all free?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Collect busy intervals of all five people and merge them (sort by start, merge overlaps). The gaps between merged intervals within working hours are times when everyone is free. For each gap long enough for the meeting, check rooms with sufficient capacity for a free sub-slot, earliest first. The cost is dominated by the sort, O(k log k) for k busy intervals."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "splitwise",
    "title": "Design Splitwise (Expense Sharing)",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Factory"
    ],
    "level": "medium",
    "summary": "Groups and expenses, equal/exact/percentage splits, per-person balances, and simplifying debts to few payments.",
    "intro": [
      "Design an expense-sharing app. Users add expenses paid by one person and split among several, in different ways. The app shows who owes whom and suggests the fewest payments needed to settle up."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Split types: equal, exact amounts, percentages (must total 100%). Amounts are money: use integer paise/cents to avoid floating-point drift, and distribute rounding remainders deterministically. Show net balance per user and a simplified settlement plan."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "&ldquo;Split equally, by exact amounts, or by percentage&rdquo;",
                "Strategy",
                "Each split type turns (amount, participants, params) into shares"
              ],
              [
                "Create the right split from a type name in the request",
                "Factory",
                "Map <code>\"equal\"</code>, <code>\"exact\"</code>, <code>\"percent\"</code> to strategies"
              ],
              [
                "Settle up with fewest transfers",
                "Greedy on net balances",
                "Match largest debtor with largest creditor"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>SplitStrategy</code>",
                "<code>shares(total, people, params)</code> &rarr; dict of person to amount"
              ],
              [
                "<code>Expense</code>",
                "Payer, total, shares"
              ],
              [
                "<code>Ledger</code>",
                "Net balance per person; <code>settle()</code> produces transfers"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import heapq\nfrom collections import defaultdict\n\nclass Equal:\n    def shares(self, total, people, params=None):\n        base, extra = divmod(total, len(people))\n        return {p: base + (1 if i < extra else 0) for i, p in enumerate(people)}\n\nclass Exact:\n    def shares(self, total, people, params):\n        if sum(params.values()) != total:\n            raise ValueError(f\"exact shares add up to {sum(params.values())}, not {total}\")\n        return dict(params)\n\nclass Percent:\n    def shares(self, total, people, params):\n        if sum(params.values()) != 100:\n            raise ValueError(\"percentages must add up to 100\")\n        raw = {p: total * pct // 100 for p, pct in params.items()}\n        leftover = total - sum(raw.values())\n        for p in sorted(params, key=lambda p: -params[p])[:leftover]:\n            raw[p] += 1                                  # hand out rounding cents\n        return raw\n\nSPLITS = {\"equal\": Equal(), \"exact\": Exact(), \"percent\": Percent()}   # factory\n\nclass Ledger:\n    def __init__(self):\n        self.net = defaultdict(int)                     # >0: is owed, <0: owes\n\n    def add_expense(self, payer, total, people, kind=\"equal\", params=None):\n        shares = SPLITS[kind].shares(total, people, params)\n        assert sum(shares.values()) == total\n        self.net[payer] += total\n        for p, amt in shares.items():\n            self.net[p] -= amt\n\n    def settle(self):\n        creditors = [(-v, p) for p, v in self.net.items() if v > 0]\n        debtors = [(v, p) for p, v in self.net.items() if v < 0]\n        heapq.heapify(creditors); heapq.heapify(debtors)\n        transfers = []\n        while creditors and debtors:\n            c_amt, c = heapq.heappop(creditors)\n            d_amt, d = heapq.heappop(debtors)\n            pay = min(-c_amt, -d_amt)\n            transfers.append(f\"{d} pays {c} {pay / 100:.2f}\")\n            if -c_amt > pay: heapq.heappush(creditors, (c_amt + pay, c))\n            if -d_amt > pay: heapq.heappush(debtors, (d_amt + pay, d))\n        return transfers\n\nL = Ledger()\nL.add_expense(\"ann\", 100_00, [\"ann\", \"bob\", \"cy\"])                       # 100.00 equally\nL.add_expense(\"bob\", 60_00, [\"bob\", \"cy\"], \"exact\", {\"bob\": 10_00, \"cy\": 50_00})\nL.add_expense(\"cy\", 90_00, [\"ann\", \"bob\", \"cy\", \"dee\"], \"percent\",\n              {\"ann\": 25, \"bob\": 25, \"cy\": 25, \"dee\": 25})\nprint({p: f\"{v / 100:+.2f}\" for p, v in sorted(L.net.items())})\nprint(\"sum of balances:\", sum(L.net.values()))\nfor t in L.settle():\n    print(\" \", t)\ntry:\n    L.add_expense(\"ann\", 10_00, [\"ann\", \"bob\"], \"percent\", {\"ann\": 60, \"bob\": 30})\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "{'ann': '+44.16', 'bob': '-5.83', 'cy': '-15.83', 'dee': '-22.50'}\nsum of balances: 0\n  dee pays ann 22.50\n  cy pays ann 15.83\n  bob pays ann 5.83\nValueError: percentages must add up to 100",
            "isError": false
          },
          {
            "type": "p",
            "html": "Balances always sum to zero, which is a cheap invariant to assert in tests. The greedy settlement produces at most n &minus; 1 transfers for n people with non-zero balances; finding the true minimum is NP-hard in general, and the greedy answer is what Splitwise-style apps use."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A new split type (by shares: &ldquo;ann 2 parts, bob 1 part&rdquo;) is one strategy class plus one factory entry. Multiple currencies need a currency on each expense and conversion at settle time. Groups become a ledger per group plus a cross-group view."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why store money as integer cents, and how do you split 100.00 three ways?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Binary floating point cannot represent most decimal fractions, so sums drift (<code>0.1 + 0.2 != 0.3</code>) and balances stop summing to zero. Integers are exact. 10000 cents / 3 = 3333 remainder 1, so one person (chosen deterministically, e.g. the first) gets 3334. <code>decimal.Decimal</code> with explicit rounding is the alternative when you need fractional units."
          }
        ]
      },
      {
        "q": "How does debt simplification work, and is it optimal?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Compute each person's net balance (paid minus owed); individual expenses no longer matter. Repeatedly match the largest creditor with the largest debtor and transfer the smaller of the two amounts; one of them reaches zero each time, so there are at most n &minus; 1 transfers. The true minimum can be lower when some subset of balances sums to zero (it can be settled independently), and finding the maximum number of such zero-sum subsets is NP-hard, so apps use the greedy method."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "ride-sharing",
    "title": "Design a Ride-Sharing Service (Uber)",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "State",
      "Observer"
    ],
    "level": "hard",
    "summary": "Driver matching strategies, the trip lifecycle as a state machine, fare strategies with surge, rider notifications.",
    "intro": [
      "Design the core objects of a ride-hailing app: riders request rides, the system matches a nearby available driver, the trip goes through its lifecycle, and the fare is computed at the end."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Drivers have a location, vehicle type and availability. A ride request has pickup, drop-off and vehicle type. Matching picks an available driver (nearest, or best rated nearby, or one that minimises total wait). Trip states: requested &rarr; driver assigned &rarr; arrived &rarr; in progress &rarr; completed, with cancellation allowed before pickup. Fare = base + per km + per minute, times surge. Riders and drivers are notified at each transition."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Matching policy changes and is A/B tested",
                "Strategy",
                "Nearest driver vs rating-weighted vs batch matching"
              ],
              [
                "Trip moves through a lifecycle; some actions only valid in some states",
                "State (transition table)",
                "A table of legal transitions guards every change"
              ],
              [
                "Fare rules: base, time, distance, surge, promos",
                "Strategy (+ Decorator for promos)",
                "Fare components vary by city and product"
              ],
              [
                "Rider and driver apps update on each transition",
                "Observer",
                "Push notifications subscribe to trip events"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Driver</code>",
                "Id, location, vehicle, rating, available"
              ],
              [
                "<code>Trip</code>",
                "Rider, driver, state; <code>transition(to)</code> validates against the table"
              ],
              [
                "<code>Matcher</code>",
                "Strategy: pick a driver for a request"
              ],
              [
                "<code>FareCalculator</code>",
                "Strategy: fare from distance, duration, surge"
              ],
              [
                "<code>Dispatch</code>",
                "Request &rarr; match &rarr; create trip; notifies observers"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import math\nfrom dataclasses import dataclass, field\n\n@dataclass\nclass Driver:\n    id: str\n    x: float\n    y: float\n    vehicle: str\n    rating: float\n    available: bool = True\n\nTRANSITIONS = {\n    \"requested\": {\"assigned\", \"cancelled\"},\n    \"assigned\": {\"arrived\", \"cancelled\"},\n    \"arrived\": {\"in_progress\", \"cancelled\"},\n    \"in_progress\": {\"completed\"},\n    \"completed\": set(), \"cancelled\": set(),\n}\n\n@dataclass\nclass Trip:\n    rider: str\n    driver: Driver | None = None\n    state: str = \"requested\"\n    listeners: list = field(default_factory=list)\n\n    def transition(self, to):\n        if to not in TRANSITIONS[self.state]:\n            raise ValueError(f\"illegal transition {self.state} -> {to}\")\n        self.state = to\n        if to in (\"completed\", \"cancelled\") and self.driver:\n            self.driver.available = True\n        for fn in self.listeners:\n            fn(self, to)\n\ndef dist(d, x, y): return math.hypot(d.x - x, d.y - y)\n\nclass Nearest:\n    def pick(self, drivers, x, y):\n        return min(drivers, key=lambda d: dist(d, x, y), default=None)\n\nclass RatedWithinRadius:\n    def __init__(self, radius): self.radius = radius\n    def pick(self, drivers, x, y):\n        near = [d for d in drivers if dist(d, x, y) <= self.radius]\n        return max(near, key=lambda d: (d.rating, -dist(d, x, y)), default=None)\n\nclass StandardFare:\n    def __init__(self, base, per_km, per_min): self.base, self.km, self.min = base, per_km, per_min\n    def fare(self, km, minutes, surge=1.0):\n        return round((self.base + self.km * km + self.min * minutes) * surge)\n\nclass Dispatch:\n    def __init__(self, drivers, matcher):\n        self.drivers, self.matcher = drivers, matcher\n\n    def request(self, rider, x, y, vehicle, listeners=()):\n        trip = Trip(rider, listeners=list(listeners))\n        pool = [d for d in self.drivers if d.available and d.vehicle == vehicle]\n        driver = self.matcher.pick(pool, x, y)\n        if driver is None:\n            trip.transition(\"cancelled\")\n            return trip\n        driver.available = False\n        trip.driver = driver\n        trip.transition(\"assigned\")\n        return trip\n\ndrivers = [Driver(\"d1\", 0, 1, \"sedan\", 4.2), Driver(\"d2\", 2, 2, \"sedan\", 4.9),\n           Driver(\"d3\", 0.5, 0, \"auto\", 4.7)]\nnotify = lambda trip, state: print(f\"  [{trip.rider}] trip is now {state}\"\n                                   + (f\" (driver {trip.driver.id})\" if trip.driver else \"\"))\n\nfor matcher in (Nearest(), RatedWithinRadius(3)):\n    for d in drivers: d.available = True\n    print(type(matcher).__name__, \"->\", Dispatch(drivers, matcher).request(\"ann\", 0, 0, \"sedan\").driver.id)\n\ndispatch = Dispatch(drivers, Nearest())\nfor d in drivers: d.available = True\ntrip = dispatch.request(\"bob\", 0, 0, \"sedan\", [notify])\nfor step in (\"arrived\", \"in_progress\", \"completed\"):\n    trip.transition(step)\nprint(\"fare:\", StandardFare(50, 12, 2).fare(km=8.5, minutes=22, surge=1.4))\ntry:\n    trip.transition(\"cancelled\")\nexcept ValueError as e:\n    print(\"ValueError:\", e)\nprint(\"cy asks for a bike, none on the road:\", dispatch.request(\"cy\", 0, 0, \"bike\").state)",
            "label": null,
            "output": "Nearest -> d1\nRatedWithinRadius -> d2\n  [bob] trip is now assigned (driver d1)\n  [bob] trip is now arrived (driver d1)\n  [bob] trip is now in_progress (driver d1)\n  [bob] trip is now completed (driver d1)\nfare: 274\nValueError: illegal transition completed -> cancelled\ncy asks for a bike, none on the road: cancelled",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Real matching is not one rider at a time: batch matching collects requests for a few seconds and solves an assignment problem (minimise total pickup time), which is another <code>Matcher</code>. Finding nearby drivers at scale uses a geospatial index (geohash or H3 cells) instead of scanning all drivers. Promo codes are decorators around the fare strategy."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you find the nearest available drivers among millions in real time?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Partition the map into cells (geohash, Google S2 or Uber's H3 hexagons). Each driver's location update moves it between per-cell sets kept in memory (Redis or a dedicated location service), sharded by region. A request looks up the rider's cell and its neighbours, expanding rings until enough candidates are found, then ranks those few by estimated time of arrival from a routing service. Location updates every few seconds per driver are the dominant write load."
          }
        ]
      },
      {
        "q": "Why model trip states as a transition table instead of a class per state?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Here most states differ only in which transitions are legal; the actions themselves (notify, free the driver) are the same. A table keeps all legal transitions visible in one place and is trivial to test exhaustively. When states have substantially different behaviour (pricing rules, timers per state), state classes become worth their extra code."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "tic-tac-toe",
    "title": "Design Tic-Tac-Toe",
    "group": "Design problems",
    "tags": [
      "Strategy"
    ],
    "level": "easy",
    "summary": "N x N board, O(1) win detection with counters, pluggable player strategies (human, random, unbeatable).",
    "intro": [
      "Design an N &times; N tic-tac-toe game for two players, where each player can be a human or a computer. Detecting a win must not rescan the whole board after every move."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Board of size N; players alternate placing their mark on an empty cell; a player wins with N in a row, column or diagonal; draw when the board is full. Invalid moves are rejected without changing the turn."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Human or computer players, different AIs",
                "Strategy",
                "Each player type implements <code>next_move(board)</code>"
              ],
              [
                "Win check after every move",
                "Counters per line",
                "+1 / &minus;1 per row, column and diagonal gives O(1) detection"
              ]
            ]
          },
          {
            "type": "p",
            "html": "No other pattern is needed. Resist adding factories and observers to a problem this small; say why you are not using them."
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Board</code>",
                "Cells and line counters; <code>place(r, c, player)</code> returns the winner if any"
              ],
              [
                "<code>Player</code>",
                "Strategy: <code>next_move(board)</code>"
              ],
              [
                "<code>Game</code>",
                "Turn order and the game loop"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import random\n\nclass Board:\n    def __init__(self, n):\n        self.n = n\n        self.cells = [[None] * n for _ in range(n)]\n        self.rows, self.cols = [0] * n, [0] * n\n        self.diag = self.anti = 0\n        self.moves = 0\n\n    def empty(self):\n        return [(r, c) for r in range(self.n) for c in range(self.n) if self.cells[r][c] is None]\n\n    def place(self, r, c, mark):\n        \"\"\"returns mark if this move wins, else None. O(1).\"\"\"\n        if not (0 <= r < self.n and 0 <= c < self.n) or self.cells[r][c] is not None:\n            raise ValueError(f\"illegal move {(r, c)}\")\n        self.cells[r][c] = mark\n        self.moves += 1\n        d = 1 if mark == \"X\" else -1\n        self.rows[r] += d; self.cols[c] += d\n        if r == c: self.diag += d\n        if r + c == self.n - 1: self.anti += d\n        target = d * self.n\n        if target in (self.rows[r], self.cols[c], self.diag, self.anti):\n            return mark\n        return None\n\n    def full(self): return self.moves == self.n * self.n\n\nclass Scripted:\n    def __init__(self, moves): self.moves = iter(moves)\n    def next_move(self, board, mark): return next(self.moves)\n\nclass RandomPlayer:\n    def __init__(self, seed): self.rng = random.Random(seed)\n    def next_move(self, board, mark): return self.rng.choice(board.empty())\n\nclass WinOrBlock:\n    \"\"\"take a winning cell, else block the opponent, else centre-ish\"\"\"\n    def next_move(self, board, mark):\n        other = \"O\" if mark == \"X\" else \"X\"\n        for who in (mark, other):\n            for r, c in board.empty():\n                trial = Board(board.n)\n                for rr in range(board.n):\n                    for cc in range(board.n):\n                        if board.cells[rr][cc]:\n                            trial.place(rr, cc, board.cells[rr][cc])\n                if trial.place(r, c, who):\n                    return r, c\n        return min(board.empty(), key=lambda rc: abs(rc[0] - board.n // 2) + abs(rc[1] - board.n // 2))\n\ndef play(n, x, o):\n    board, players = Board(n), [(\"X\", x), (\"O\", o)]\n    turn = 0\n    while True:\n        mark, player = players[turn % 2]\n        r, c = player.next_move(board, mark)\n        if board.place(r, c, mark):\n            return f\"{mark} wins after {board.moves} moves\"\n        if board.full():\n            return \"draw\"\n        turn += 1\n\nprint(play(3, Scripted([(0, 0), (1, 1), (2, 2)]), Scripted([(0, 1), (0, 2)])))\nprint(play(4, Scripted([(0, 3), (1, 2), (2, 1), (3, 0)]), Scripted([(0, 0), (1, 1), (2, 2)])))\nprint(play(3, WinOrBlock(), WinOrBlock()))\nresults = [play(3, WinOrBlock(), RandomPlayer(s)) for s in range(200)]\ntally = {\"X wins\": 0, \"O wins\": 0, \"draw\": 0}\nfor r in results:\n    tally[r.split(\" after\")[0]] += 1\nprint(\"smart X vs random O over 200 games:\", tally)",
            "label": null,
            "output": "X wins after 5 moves\nX wins after 7 moves\ndraw\nsmart X vs random O over 200 games: {'X wins': 182, 'O wins': 2, 'draw': 16}",
            "isError": false
          },
          {
            "type": "p",
            "html": "The counters work because X adds 1 and O subtracts 1 on every line a cell belongs to; a line reaches &plusmn;N only when one player owns all N cells. That makes each move O(1) instead of O(N) or O(N&sup2;) for a rescan."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A minimax player (perfect play on 3 &times; 3) is one more strategy. Undo is a stack of moves with the counter updates reversed. Networked play adds a <code>RemotePlayer</code> strategy whose <code>next_move</code> waits for a message."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How does the O(1) win check work, and what if the win condition were K in a row on a large board (Gomoku)?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "With N in a row on an N &times; N board, each row, column and the two diagonals has a single counter. For K &lt; N in a row, counters per line do not work; instead, after a move at (r, c), walk outward in each of the four directions counting consecutive same marks: O(K) per move, still independent of board size."
          }
        ]
      },
      {
        "q": "Where would you put input validation for a human player?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "In two places with different jobs: the human player strategy parses and re-prompts on malformed input (that is a UI concern), and <code>Board.place</code> rejects illegal moves regardless of who made them (that is a rule of the game). Never rely on the player object alone; a buggy AI or a malicious remote client must not be able to corrupt the board."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "snakes-and-ladders",
    "title": "Design Snakes and Ladders",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Builder"
    ],
    "level": "easy",
    "summary": "Board of jumps, players, pluggable dice, deterministic tests with seeded or scripted dice.",
    "intro": [
      "Design a snakes-and-ladders game for any number of players on a 100-square board. The board layout is configurable, and the game must be testable without randomness getting in the way."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Players start at 0 and move by the die roll. Landing on a ladder's foot or a snake's head moves the player to the other end. A player needs an exact roll to land on 100 (an overshoot means no move). First to 100 wins."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Dice may be one die, two dice, or scripted for tests",
                "Strategy",
                "The game asks a <code>Dice</code> for a roll; tests inject fixed rolls"
              ],
              [
                "Board layout configured from data and validated",
                "Builder",
                "Build the jump map step by step; validate no loops or conflicting starts"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>BoardBuilder</code>",
                "Adds snakes and ladders, validates, builds a <code>Board</code>"
              ],
              [
                "<code>Board</code>",
                "Size and a jump map (start &rarr; end)"
              ],
              [
                "<code>Dice</code>",
                "Strategy: <code>roll()</code>"
              ],
              [
                "<code>Game</code>",
                "Players, turn order, <code>play()</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import random\nfrom itertools import cycle\n\nclass Board:\n    def __init__(self, size, jumps):\n        self.size, self.jumps = size, jumps\n    def move(self, pos, roll):\n        target = pos + roll\n        if target > self.size:\n            return pos, \"overshoot\"\n        if target in self.jumps:\n            end = self.jumps[target]\n            return end, (\"ladder\" if end > target else \"snake\") + f\" {target}->{end}\"\n        return target, \"\"\n\nclass BoardBuilder:\n    def __init__(self, size=100):\n        self.size, self.jumps = size, {}\n    def _add(self, start, end):\n        if not (1 < start < self.size and 0 < end < self.size or end == self.size):\n            raise ValueError(f\"jump {start}->{end} is off the board\")\n        if start in self.jumps or start in self.jumps.values():\n            raise ValueError(f\"square {start} already has a jump\")\n        self.jumps[start] = end\n        return self\n    def ladder(self, bottom, top):\n        if top <= bottom: raise ValueError(\"a ladder must go up\")\n        return self._add(bottom, top)\n    def snake(self, head, tail):\n        if tail >= head: raise ValueError(\"a snake must go down\")\n        return self._add(head, tail)\n    def build(self): return Board(self.size, dict(self.jumps))\n\nclass RandomDie:\n    def __init__(self, seed=None): self.rng = random.Random(seed)\n    def roll(self): return self.rng.randint(1, 6)\n\nclass Scripted:\n    def __init__(self, rolls): self.rolls = iter(rolls)\n    def roll(self): return next(self.rolls)\n\nclass Game:\n    def __init__(self, board, players, dice):\n        self.board, self.dice = board, dice\n        self.pos = {p: 0 for p in players}\n        self.order = cycle(players)\n    def play(self, verbose=False, max_turns=10_000):\n        for turn in range(1, max_turns + 1):\n            p = next(self.order)\n            roll = self.dice.roll()\n            self.pos[p], event = self.board.move(self.pos[p], roll)\n            if verbose:\n                print(f\"  {p} rolls {roll} -> {self.pos[p]:3} {event}\")\n            if self.pos[p] == self.board.size:\n                return p, turn\n        raise RuntimeError(\"no winner\")\n\nboard = (BoardBuilder(30).ladder(3, 22).ladder(5, 8).snake(27, 1).snake(21, 9).build())\nprint(Game(board, [\"ann\", \"bob\"], Scripted([3, 5, 5, 6, 4, 6, 6, 1, 6, 6, 6, 2, 5, 6, 4])).play(verbose=True))\ntry:\n    BoardBuilder(30).ladder(3, 22).snake(22, 4)\nexcept ValueError as e:\n    print(\"ValueError:\", e)\nwins = [Game(BoardBuilder().ladder(4, 56).snake(98, 2).build(), [\"a\", \"b\"], RandomDie(s)).play()[0]\n        for s in range(500)]\nprint(\"first player wins\", round(wins.count(\"a\") / len(wins) * 100), \"% of 500 seeded games\")",
            "label": null,
            "output": "  ann rolls 3 ->  22 ladder 3->22\n  bob rolls 5 ->   8 ladder 5->8\n  ann rolls 5 ->   1 snake 27->1\n  bob rolls 6 ->  14 \n  ann rolls 4 ->   8 ladder 5->8\n  bob rolls 6 ->  20 \n  ann rolls 6 ->  14 \n  bob rolls 1 ->   9 snake 21->9\n  ann rolls 6 ->  20 \n  bob rolls 6 ->  15 \n  ann rolls 6 ->  26 \n  bob rolls 2 ->  17 \n  ann rolls 5 ->  26 overshoot\n  bob rolls 6 ->  23 \n  ann rolls 4 ->  30 \n('ann', 15)\nValueError: square 22 already has a jump\nfirst player wins 52 % of 500 seeded games",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Rule variants (roll again on a six, three sixes sends you back) belong in a <code>Rules</code> strategy consulted by <code>Game</code>. Special squares (skip a turn) generalise the jump map into square effects &mdash; a small Command per square."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you unit-test a game that depends on dice?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Inject the dice. Tests pass a scripted die that returns a fixed sequence, so every scenario &mdash; a ladder chain, an overshoot near the end, a win on an exact roll &mdash; is reproducible. For statistical properties (no infinite games, plausible win distribution), use a seeded random die and run many games."
          }
        ]
      },
      {
        "q": "What validation does the board builder need?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Jumps must stay on the board; snakes go down and ladders up; a square cannot be the start of two jumps; a jump should not end on another jump's start (or decide the rule for chained jumps explicitly); the last square should not be a snake head. Doing this once in the builder means <code>Board</code> can assume a valid layout."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "chess",
    "title": "Design a Chess Game",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Command",
      "Factory"
    ],
    "level": "hard",
    "summary": "Polymorphic pieces with move generation, move commands with undo, board set-up factory, check detection.",
    "intro": [
      "Design the core of a chess engine for two players: a board, pieces with their movement rules, move validation (including not leaving your own king in check), and undo. Castling, en passant and promotion may be discussed as extensions."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Board 8 &times; 8; each piece type generates its pseudo-legal moves; a move is legal if it does not leave the mover's king in check; moves can be undone; the game reports check and checkmate."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Each piece moves differently",
                "Strategy / polymorphism",
                "One class per piece type with <code>moves(board, sq)</code>; sliding pieces share a helper"
              ],
              [
                "Undo, move history, replay",
                "Command",
                "A <code>Move</code> records from, to and the captured piece, so it can be undone"
              ],
              [
                "Standard starting position from a layout",
                "Factory",
                "Create pieces from FEN-like letters"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Piece</code> and subclasses",
                "Colour; generate pseudo-legal target squares"
              ],
              [
                "<code>Board</code>",
                "Square &rarr; piece map, apply/undo moves, find the king, attack test"
              ],
              [
                "<code>Move</code>",
                "Command with <code>do</code> and <code>undo</code>"
              ],
              [
                "<code>Game</code>",
                "Turn, legal move filter, history, status"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "class Piece:\n    symbol = \"?\"\n    def __init__(self, white): self.white = white\n    def __repr__(self): return self.symbol.upper() if self.white else self.symbol\n    def slide(self, board, sq, dirs, max_steps=8):\n        r, c = sq\n        for dr, dc in dirs:\n            for k in range(1, max_steps + 1):\n                t = (r + dr * k, c + dc * k)\n                if not (0 <= t[0] < 8 and 0 <= t[1] < 8):\n                    break\n                other = board.get(t)\n                if other is None:\n                    yield t\n                    continue\n                if other.white != self.white:\n                    yield t                     # capture\n                break\n\nSTRAIGHT = [(1, 0), (-1, 0), (0, 1), (0, -1)]\nDIAGONAL = [(1, 1), (1, -1), (-1, 1), (-1, -1)]\n\nclass Rook(Piece):\n    symbol = \"r\"\n    def moves(self, b, sq): return self.slide(b, sq, STRAIGHT)\nclass Bishop(Piece):\n    symbol = \"b\"\n    def moves(self, b, sq): return self.slide(b, sq, DIAGONAL)\nclass Queen(Piece):\n    symbol = \"q\"\n    def moves(self, b, sq): return self.slide(b, sq, STRAIGHT + DIAGONAL)\nclass King(Piece):\n    symbol = \"k\"\n    def moves(self, b, sq): return self.slide(b, sq, STRAIGHT + DIAGONAL, max_steps=1)\nclass Knight(Piece):\n    symbol = \"n\"\n    def moves(self, b, sq):\n        for dr, dc in [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]:\n            t = (sq[0] + dr, sq[1] + dc)\n            if 0 <= t[0] < 8 and 0 <= t[1] < 8 and (b.get(t) is None or b.get(t).white != self.white):\n                yield t\nclass Pawn(Piece):\n    symbol = \"p\"\n    def moves(self, b, sq):\n        d = 1 if self.white else -1\n        r, c = sq\n        if 0 <= r + d < 8 and b.get((r + d, c)) is None:\n            yield (r + d, c)\n            if r == (1 if self.white else 6) and b.get((r + 2 * d, c)) is None:\n                yield (r + 2 * d, c)\n        for dc in (-1, 1):\n            t = (r + d, c + dc)\n            if 0 <= t[1] < 8 and b.get(t) is not None and b.get(t).white != self.white:\n                yield t\n\nPIECES = {cls.symbol: cls for cls in (Rook, Bishop, Queen, King, Knight, Pawn)}\n\ndef piece_from(letter):                      # factory\n    return PIECES[letter.lower()](letter.isupper())\n\nclass Move:                                  # command\n    def __init__(self, frm, to): self.frm, self.to, self.captured = frm, to, None\n    def do(self, board):\n        self.captured = board.pop(self.to, None)\n        board[self.to] = board.pop(self.frm)\n    def undo(self, board):\n        board[self.frm] = board.pop(self.to)\n        if self.captured is not None:\n            board[self.to] = self.captured\n    def __repr__(self):\n        f = lambda s: \"abcdefgh\"[s[1]] + str(s[0] + 1)\n        return f(self.frm) + f(self.to)\n\nclass Game:\n    def __init__(self, layout):\n        self.board = {}\n        for r, row in enumerate(layout):            # layout[0] is rank 1\n            for c, ch in enumerate(row):\n                if ch != \".\":\n                    self.board[(r, c)] = piece_from(ch)\n        self.white_to_move, self.history = True, []\n\n    def attacked(self, sq, by_white):\n        return any(p.white == by_white and sq in set(p.moves(self.board, s))\n                   for s, p in list(self.board.items()))\n\n    def in_check(self, white):\n        king = next(s for s, p in self.board.items() if isinstance(p, King) and p.white == white)\n        return self.attacked(king, not white)\n\n    def legal_moves(self):\n        out = []\n        for s, p in list(self.board.items()):\n            if p.white != self.white_to_move:\n                continue\n            for t in list(p.moves(self.board, s)):\n                m = Move(s, t); m.do(self.board)\n                if not self.in_check(self.white_to_move):\n                    out.append(m)\n                m.undo(self.board)\n        return out\n\n    def play(self, uci):\n        m = next((m for m in self.legal_moves() if repr(m) == uci), None)\n        if m is None:\n            raise ValueError(f\"illegal move {uci}\")\n        m.do(self.board); self.history.append(m)\n        self.white_to_move = not self.white_to_move\n\n    def undo(self):\n        self.history.pop().undo(self.board)\n        self.white_to_move = not self.white_to_move\n\n    def status(self):\n        moves = self.legal_moves()\n        check = self.in_check(self.white_to_move)\n        return \"checkmate\" if check and not moves else \"stalemate\" if not moves else \"check\" if check else \"ok\"\n\nSTART = [\"RNBQKBNR\", \"PPPPPPPP\", \"........\", \"........\",\n         \"........\", \"........\", \"pppppppp\", \"rnbqkbnr\"]\ng = Game(START)\nprint(\"opening moves for white:\", len(g.legal_moves()))\nfor mv in [\"f2f3\", \"e7e5\", \"g2g4\", \"d8h4\"]:          # fool's mate\n    g.play(mv)\nprint(\"after fool's mate:\", g.status(), \"| history:\", g.history)\ng.undo()\nprint(\"after undo:\", g.status(), \"| black to move:\", not g.white_to_move, \"| legal:\", len(g.legal_moves()))\ntry:\n    g.play(\"e8e6\")\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "opening moves for white: 20\nafter fool's mate: checkmate | history: [f2f3, e7e5, g2g4, d8h4]\nafter undo: ok | black to move: True | legal: 30\nValueError: illegal move e8e6",
            "isError": false
          },
          {
            "type": "p",
            "html": "Legality is checked by simulation: make each pseudo-legal move, ask whether the mover's king is attacked, undo. The Command object's undo is what makes that cheap and correct, and the same objects give the game its history."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Castling, en passant and promotion are special <code>Move</code> subclasses with their own <code>do</code>/<code>undo</code> (castling moves two pieces, promotion replaces a pawn) plus a little extra state on the game (castling rights, en passant square). A computer opponent is a strategy that searches <code>legal_moves</code> with minimax."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why generate pseudo-legal moves per piece and then filter for check, instead of making each piece check legality?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Whether a move leaves your king in check depends on the whole position (pins, discovered attacks), not on the moving piece's own rules. Keeping each piece responsible only for its movement pattern keeps piece classes simple and independent; one generic filter (do, test the king, undo) handles all the global rules uniformly. Fast engines optimise this with pin detection and attack maps, but the structure is the same."
          }
        ]
      },
      {
        "q": "What does a <code>Move</code> need to store to support undo?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The from and to squares, the captured piece (if any), and any game state the move changes that cannot be recomputed: castling rights, the en passant target square, the half-move clock for the fifty-move rule, and for promotion the original pawn. Storing these on the command keeps undo exact and O(1)."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "cricket-scoreboard",
    "title": "Design a Live Cricket Scoreboard",
    "group": "Design problems",
    "tags": [
      "Observer",
      "Command"
    ],
    "level": "medium",
    "summary": "Ball-by-ball events, derived score and stats, many live displays subscribed to updates, and correcting a wrong entry.",
    "intro": [
      "Design the scoring core of a Cricbuzz-style app. A scorer records each delivery; the score, batting stats and commentary feeds update live for many viewers. Scorers sometimes enter a ball wrongly and need to undo it."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Record deliveries: runs, extras (wide, no-ball) and wickets. Derive total, wickets, overs (legal balls only), run rate and batter stats. Push updates to subscribers (scorecard widget, commentary, push notifications for wickets and milestones). Support undoing the last ball."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Many displays update when a ball is recorded",
                "Observer",
                "Displays subscribe; the scorer does not know them"
              ],
              [
                "Each delivery is an event that can be undone",
                "Command / event sourcing",
                "Store balls, derive the score; undo = drop the last event and rebuild or reverse"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Ball</code>",
                "Immutable event: batter, runs, extra, wicket"
              ],
              [
                "<code>Innings</code>",
                "Event list, derived totals; <code>record</code>, <code>undo</code>"
              ],
              [
                "Subscribers",
                "Scorecard, milestone alerts &mdash; callables receiving the innings after each change"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Ball:\n    batter: str\n    runs: int = 0\n    extra: str | None = None          # \"wide\" | \"noball\" | None\n    wicket: bool = False\n\n    @property\n    def legal(self): return self.extra is None\n\nclass Innings:\n    def __init__(self):\n        self.balls, self.subscribers = [], []\n\n    def subscribe(self, fn): self.subscribers.append(fn)\n\n    def record(self, ball):\n        self.balls.append(ball)\n        self._notify(ball)\n\n    def undo(self):\n        ball = self.balls.pop()\n        self._notify(None)\n        return ball\n\n    def _notify(self, ball):\n        for fn in self.subscribers:\n            fn(self, ball)\n\n    @property\n    def total(self):\n        return sum(b.runs + (1 if b.extra else 0) for b in self.balls)\n\n    @property\n    def wickets(self): return sum(b.wicket for b in self.balls)\n\n    @property\n    def overs(self):\n        legal = sum(b.legal for b in self.balls)\n        return f\"{legal // 6}.{legal % 6}\"\n\n    def batter_runs(self, name):\n        return sum(b.runs for b in self.balls if b.batter == name and b.extra != \"wide\")\n\ndef scorecard(inn, ball):\n    print(f\"  {inn.total}/{inn.wickets} ({inn.overs} ov)\")\n\ndef milestones(inn, ball):\n    if ball and ball.wicket:\n        print(f\"  ALERT: wicket! {ball.batter} out for {inn.batter_runs(ball.batter)}\")\n    if ball and inn.batter_runs(ball.batter) >= 10 > inn.batter_runs(ball.batter) - ball.runs:\n        print(f\"  ALERT: {ball.batter} reaches 10\")\n\ninn = Innings()\ninn.subscribe(scorecard)\ninn.subscribe(milestones)\nfor b in [Ball(\"rohit\", 4), Ball(\"rohit\", 1), Ball(\"gill\", 0, \"wide\"), Ball(\"gill\", 6),\n          Ball(\"gill\", 4), Ball(\"gill\", 0, wicket=True), Ball(\"kohli\", 2)]:\n    inn.record(b)\nprint(\"scorer fixes a mistake:\")\ninn.undo()\nprint(\"rohit\", inn.batter_runs(\"rohit\"), \"| gill\", inn.batter_runs(\"gill\"))",
            "label": null,
            "output": "  4/0 (0.1 ov)\n  5/0 (0.2 ov)\n  6/0 (0.2 ov)\n  12/0 (0.3 ov)\n  16/0 (0.4 ov)\n  ALERT: gill reaches 10\n  16/1 (0.5 ov)\n  ALERT: wicket! gill out for 10\n  18/1 (1.0 ov)\nscorer fixes a mistake:\n  16/1 (0.5 ov)\nrohit 5 | gill 10",
            "isError": false
          },
          {
            "type": "p",
            "html": "Every number on the scorecard is derived from the list of balls, so undo is just removing the last ball and nothing can drift out of sync. Large systems keep this shape and add cached aggregates for speed, recomputed (or reversed) per event."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Viewers on phones get updates through a pub/sub fan-out (the in-process observers above become a message broker topic per match). Commentary and analytics (wagon wheel, partnerships) are more subscribers. Undo of a ball broadcasts a correction event so clients can fix their state."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Should the scoreboard store the current score or the ball-by-ball events?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Store events and derive the score (event sourcing). It makes corrections trivial and auditable, lets you add new statistics later by replaying history, and guarantees all views agree. For performance, also maintain running totals updated per event, treating them as a cache that can be rebuilt from the events."
          }
        ]
      },
      {
        "q": "Ten million people follow a match. How do updates reach them?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The scoring service publishes each ball event to a topic for that match. Edge servers holding WebSocket or SSE connections subscribe to the topic and push to their connected clients; each server serves tens of thousands of clients, so the fan-out is a tree. Clients that miss updates (reconnect, background) fetch the current state snapshot with a sequence number and then apply further events. Push notifications for wickets go through APNs/FCM in batches."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "online-auction",
    "title": "Design an Online Auction System",
    "group": "Design problems",
    "tags": [
      "State",
      "Observer",
      "Strategy"
    ],
    "level": "medium",
    "summary": "Auction lifecycle states, bid validation with increments, outbid notifications, pluggable winner rules.",
    "intro": [
      "Design an eBay-style auction. Sellers list an item with a starting price and end time; buyers place bids; bidders are notified when they are outbid; when the auction ends, the winner is determined and notified."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Lifecycle: draft &rarr; live &rarr; ended (or cancelled). Bids are accepted only while live, must exceed the current highest bid by a minimum increment, and must not come from the seller. Notify the previous leader when outbid. Winner rule: highest bid (English auction), with a reserve price; a second-price rule should be possible."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Bids allowed only while the auction is live",
                "State",
                "Each lifecycle state accepts or rejects actions"
              ],
              [
                "&ldquo;Notify bidders when outbid&rdquo; and the winner at the end",
                "Observer",
                "Notification channels subscribe to auction events"
              ],
              [
                "Highest bid wins vs second-price (Vickrey)",
                "Strategy",
                "The settlement rule is pluggable"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Auction</code>",
                "Item, seller, state, bids, listeners"
              ],
              [
                "<code>Bid</code>",
                "Bidder, amount, time"
              ],
              [
                "<code>SettlementRule</code>",
                "Strategy: winner and price from the bids"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Bid:\n    bidder: str\n    amount: int\n    t: int\n\nclass HighestBid:\n    def settle(self, bids, reserve):\n        top = max(bids, key=lambda b: (b.amount, -b.t), default=None)\n        return (top.bidder, top.amount) if top and top.amount >= reserve else (None, 0)\n\nclass SecondPrice:\n    def settle(self, bids, reserve):\n        ranked = sorted(bids, key=lambda b: (-b.amount, b.t))\n        if not ranked or ranked[0].amount < reserve:\n            return None, 0\n        second = ranked[1].amount if len(ranked) > 1 else reserve\n        return ranked[0].bidder, max(second, reserve)\n\nclass Auction:\n    def __init__(self, item, seller, start, reserve, increment, rule):\n        self.item, self.seller, self.reserve, self.increment = item, seller, reserve, increment\n        self.start, self.rule = start, rule\n        self.state, self.bids, self.listeners = \"draft\", [], []\n\n    def emit(self, event, **kw):\n        for fn in self.listeners: fn(event, kw)\n\n    def open(self):\n        if self.state != \"draft\": raise RuntimeError(f\"cannot open a {self.state} auction\")\n        self.state = \"live\"\n\n    def bid(self, bidder, amount, t):\n        if self.state != \"live\":\n            raise RuntimeError(f\"auction is {self.state}\")\n        if bidder == self.seller:\n            raise PermissionError(\"seller cannot bid\")\n        leader = self.bids[-1] if self.bids else None\n        minimum = leader.amount + self.increment if leader else self.start\n        if amount < minimum:\n            raise ValueError(f\"bid must be at least {minimum}\")\n        self.bids.append(Bid(bidder, amount, t))\n        if leader and leader.bidder != bidder:\n            self.emit(\"outbid\", who=leader.bidder, by=amount)\n\n    def close(self):\n        if self.state != \"live\": raise RuntimeError(f\"cannot close a {self.state} auction\")\n        self.state = \"ended\"\n        winner, price = self.rule.settle(self.bids, self.reserve)\n        self.emit(\"ended\", winner=winner, price=price)\n        return winner, price\n\ndef run(rule):\n    a = Auction(\"guitar\", \"sam\", start=100, reserve=150, increment=10, rule=rule)\n    a.listeners.append(lambda e, d: print(f\"  {e}: {d}\"))\n    a.open()\n    for who, amt, t in [(\"ann\", 100, 1), (\"bob\", 120, 2), (\"ann\", 125, 3), (\"ann\", 140, 4), (\"cy\", 200, 5)]:\n        try:\n            a.bid(who, amt, t)\n        except ValueError as e:\n            print(f\"  {who} {amt}: {e}\")\n    return a.close()\n\nprint(\"English:\", run(HighestBid()))\nprint(\"Second-price:\", run(SecondPrice()))\na = Auction(\"vase\", \"sam\", 50, 0, 5, HighestBid())\ntry:\n    a.bid(\"ann\", 60, 1)\nexcept RuntimeError as e:\n    print(\"RuntimeError:\", e)",
            "label": null,
            "output": "  outbid: {'who': 'ann', 'by': 120}\n  ann 125: bid must be at least 130\n  outbid: {'who': 'bob', 'by': 140}\n  outbid: {'who': 'ann', 'by': 200}\n  ended: {'winner': 'cy', 'price': 200}\nEnglish: ('cy', 200)\n  outbid: {'who': 'ann', 'by': 120}\n  ann 125: bid must be at least 130\n  outbid: {'who': 'bob', 'by': 140}\n  outbid: {'who': 'ann', 'by': 200}\n  ended: {'winner': 'cy', 'price': 150}\nSecond-price: ('cy', 150)\nRuntimeError: auction is draft",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Auto-bidding (proxy bids: &ldquo;bid for me up to 300&rdquo;) is a component that listens for outbid events on behalf of a user and places the next increment. Anti-sniping extends the end time when a bid arrives in the last minute &mdash; a rule inside the live state. Closing at the end time is a scheduled job; it must be idempotent in case it fires twice."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Two bids arrive in the same millisecond for the last increment. How do you keep bidding consistent?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Serialise bids per auction: process them through a single-threaded actor or a queue partitioned by auction id, or do a conditional write in the database (<code>UPDATE auctions SET top_bid=?, leader=? WHERE id=? AND top_bid=?</code>, retrying on failure). Either way, the &ldquo;must exceed the current leader&rdquo; check and the update happen atomically, and ties are broken by arrival order at that serialisation point."
          }
        ]
      },
      {
        "q": "Why is the settlement rule a strategy and not part of the auction?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It is the part most likely to vary by marketplace or listing type (English, second-price, Dutch, reserve or not), and it is a pure function of the bids and the reserve, which makes it easy to test in isolation. The auction keeps the lifecycle and bid validation, which are shared by every rule."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "lru-cache",
    "title": "Design an LRU / LFU Cache",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Decorator"
    ],
    "level": "medium",
    "summary": "O(1) get and put with a hash map plus doubly linked list, a pluggable eviction policy, and thread safety.",
    "intro": [
      "Design an in-memory cache with a fixed capacity that supports <code>get</code> and <code>put</code> in O(1). When full, it evicts according to a policy: least recently used by default, least frequently used as an option."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "O(1) <code>get(key)</code> and <code>put(key, value)</code>. Capacity in entries. Eviction policy pluggable (LRU, LFU). Report hit rate. Optionally safe to use from several threads."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "&ldquo;Evict by LRU, or by LFU&rdquo;",
                "Strategy",
                "The cache delegates ordering and victim choice to a policy object"
              ],
              [
                "Add thread safety or metrics without changing the cache",
                "Decorator",
                "A wrapper with the same interface adds a lock or counters"
              ],
              [
                "O(1) recency updates",
                "Hash map + doubly linked list",
                "The map finds the node; the list moves it to the front in O(1)"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Node</code>",
                "Key, value, prev, next"
              ],
              [
                "<code>LRUPolicy</code>",
                "Doubly linked list with sentinels: touch, add, pop least recent"
              ],
              [
                "<code>LFUPolicy</code>",
                "Frequency buckets of insertion-ordered keys plus the current minimum frequency"
              ],
              [
                "<code>Cache</code>",
                "Map key &rarr; value; asks the policy for the victim when full"
              ],
              [
                "<code>Locked</code>",
                "Decorator adding a lock around every call"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import threading\nfrom collections import defaultdict, OrderedDict\n\nclass Node:\n    __slots__ = (\"key\", \"prev\", \"next\")\n    def __init__(self, key=None): self.key, self.prev, self.next = key, None, None\n\nclass LRUPolicy:\n    def __init__(self):\n        self.head, self.tail = Node(), Node()          # sentinels: no edge cases\n        self.head.next, self.tail.prev = self.tail, self.head\n        self.nodes = {}\n\n    def _unlink(self, n):\n        n.prev.next, n.next.prev = n.next, n.prev\n\n    def _push_front(self, n):\n        n.next, n.prev = self.head.next, self.head\n        self.head.next.prev = n\n        self.head.next = n\n\n    def touch(self, key):\n        n = self.nodes[key]\n        self._unlink(n); self._push_front(n)\n\n    def add(self, key):\n        n = self.nodes[key] = Node(key)\n        self._push_front(n)\n\n    def victim(self):\n        n = self.tail.prev\n        self._unlink(n)\n        del self.nodes[n.key]\n        return n.key\n\nclass LFUPolicy:\n    def __init__(self):\n        self.freq = {}\n        self.buckets = defaultdict(OrderedDict)        # freq -> keys in LRU order\n        self.min_freq = 0\n\n    def touch(self, key):\n        f = self.freq[key]\n        del self.buckets[f][key]\n        if not self.buckets[f] and self.min_freq == f:\n            self.min_freq += 1\n        self.freq[key] = f + 1\n        self.buckets[f + 1][key] = None\n\n    def add(self, key):\n        self.freq[key] = 1\n        self.buckets[1][key] = None\n        self.min_freq = 1\n\n    def victim(self):\n        key, _ = self.buckets[self.min_freq].popitem(last=False)\n        del self.freq[key]\n        return key\n\nclass Cache:\n    def __init__(self, capacity, policy):\n        self.capacity, self.policy, self.data = capacity, policy, {}\n        self.hits = self.misses = 0\n\n    def get(self, key, default=None):\n        if key not in self.data:\n            self.misses += 1\n            return default\n        self.hits += 1\n        self.policy.touch(key)\n        return self.data[key]\n\n    def put(self, key, value):\n        if key in self.data:\n            self.data[key] = value\n            self.policy.touch(key)\n            return\n        if len(self.data) >= self.capacity:\n            del self.data[self.policy.victim()]\n        self.data[key] = value\n        self.policy.add(key)\n\nclass Locked:                                          # decorator: same interface\n    def __init__(self, inner):\n        self.inner, self.lock = inner, threading.Lock()\n    def get(self, *a):\n        with self.lock: return self.inner.get(*a)\n    def put(self, *a):\n        with self.lock: return self.inner.put(*a)\n\nfor policy in (LRUPolicy(), LFUPolicy()):\n    c = Cache(3, policy)\n    for k in \"abc\": c.put(k, k.upper())\n    c.get(\"a\"); c.get(\"a\"); c.get(\"b\")                  # a used twice, b once, c never\n    c.put(\"d\", \"D\")                                     # evicts one key\n    c.get(\"c\"); c.put(\"e\", \"E\")\n    print(f\"{type(policy).__name__}: keys now {sorted(c.data)}\")\n\nshared = Locked(Cache(100, LRUPolicy()))\ndef worker(i):\n    for j in range(1000):\n        shared.put(j % 150, i); shared.get(j % 120)\nts = [threading.Thread(target=worker, args=(i,)) for i in range(8)]\nfor t in ts: t.start()\nfor t in ts: t.join()\ninner = shared.inner\nprint(\"after 8 threads:\", len(inner.data), \"entries,\", len(inner.policy.nodes), \"list nodes (consistent)\")",
            "label": null,
            "output": "LRUPolicy: keys now ['b', 'd', 'e']\nLFUPolicy: keys now ['a', 'b', 'e']\nafter 8 threads: 100 entries, 100 list nodes (consistent)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Trace for LRU: after the gets the recency order is b, a, c (most recent first), so <code>d</code> evicts <code>c</code>; the next get of <code>c</code> misses, and <code>e</code> evicts <code>a</code>. LFU instead keeps the frequently used <code>a</code> and evicts the least-used keys."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "TTL support adds an expiry per key, checked on <code>get</code> plus a background sweep. A size-in-bytes capacity changes &ldquo;full&rdquo; from a count to a sum. In Python, <code>functools.lru_cache</code> and <code>OrderedDict.move_to_end</code> give an LRU for free; the interview usually wants the linked-list version to show you know why it is O(1)."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why a doubly linked list rather than a singly linked one or a list?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Moving a node to the front and removing the tail both need the node's predecessor. With a doubly linked list the node knows its predecessor, so unlinking is O(1) given the node from the hash map. A singly linked list would need an O(n) walk to find the predecessor, and a Python list would shift elements on every move."
          }
        ]
      },
      {
        "q": "How does LFU stay O(1)?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Keep a map from frequency to an insertion-ordered set of keys, each key's frequency, and the minimum frequency present. A touch moves the key from bucket f to f+1 in O(1) and bumps <code>min_freq</code> if bucket f emptied and was the minimum. A new key always has frequency 1, so <code>min_freq</code> resets to 1. Eviction pops the oldest key in the <code>min_freq</code> bucket, which breaks ties by recency."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "logging-framework",
    "title": "Design a Logging Framework",
    "group": "Design problems",
    "tags": [
      "Chain of Responsibility",
      "Strategy",
      "Observer",
      "Singleton"
    ],
    "level": "medium",
    "summary": "Levels and hierarchical loggers, handlers (console, file, memory) with their own levels, pluggable formatters.",
    "intro": [
      "Design a logging library like Python's <code>logging</code> or Log4j: application code calls <code>log.info(...)</code>; messages below a level are dropped cheaply; each message can go to several destinations, each with its own threshold and format; loggers are named hierarchically and inherit configuration."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Levels DEBUG &lt; INFO &lt; WARNING &lt; ERROR. Named loggers (<code>app.db</code>) pass records up to ancestors (<code>app</code>, root) unless propagation is off. Handlers (console, file, in-memory) each have a level and a formatter. One registry of loggers per process."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Record travels from <code>app.db</code> to <code>app</code> to root",
                "Chain of Responsibility",
                "Each logger handles the record then passes it to its parent"
              ],
              [
                "Several destinations receive each record",
                "Observer",
                "Handlers subscribe to a logger"
              ],
              [
                "Plain text vs JSON output",
                "Strategy",
                "Formatter is swappable per handler"
              ],
              [
                "<code>get_logger(name)</code> returns the same object everywhere",
                "Singleton registry",
                "One process-wide registry"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Level</code>",
                "Ordered severities"
              ],
              [
                "<code>Record</code>",
                "Logger name, level, message, context"
              ],
              [
                "<code>Formatter</code>",
                "Strategy: record &rarr; string"
              ],
              [
                "<code>Handler</code>",
                "Level threshold + formatter + destination"
              ],
              [
                "<code>Logger</code>",
                "Name, level, handlers, parent; filters and propagates"
              ],
              [
                "<code>get_logger</code>",
                "Registry creating loggers and wiring parents"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import json\nfrom dataclasses import dataclass, field\nfrom enum import IntEnum\n\nclass Level(IntEnum):\n    DEBUG = 10\n    INFO = 20\n    WARNING = 30\n    ERROR = 40\n\n@dataclass\nclass Record:\n    logger: str\n    level: Level\n    msg: str\n    ctx: dict = field(default_factory=dict)\n\nclass TextFormatter:\n    def format(self, r): return f\"{r.level.name:7} {r.logger}: {r.msg}\"\n\nclass JsonFormatter:\n    def format(self, r):\n        return json.dumps({\"lvl\": r.level.name, \"log\": r.logger, \"msg\": r.msg, **r.ctx})\n\nclass Handler:\n    def __init__(self, level=Level.DEBUG, formatter=None):\n        self.level, self.formatter = level, formatter or TextFormatter()\n    def handle(self, r):\n        if r.level >= self.level:\n            self.emit(self.formatter.format(r))\n\nclass ConsoleHandler(Handler):\n    def emit(self, line): print(\"  console |\", line)\n\nclass MemoryHandler(Handler):\n    def __init__(self, *a, **kw):\n        super().__init__(*a, **kw); self.lines = []\n    def emit(self, line): self.lines.append(line)\n\nclass Logger:\n    def __init__(self, name, parent=None):\n        self.name, self.parent = name, parent\n        self.level, self.handlers, self.propagate = None, [], True\n\n    def effective_level(self):\n        node = self\n        while node.level is None:\n            node = node.parent\n        return node.level\n\n    def log(self, level, msg, **ctx):\n        if level < self.effective_level():          # cheap early exit\n            return\n        r, node = Record(self.name, level, msg, ctx), self\n        while node:                                   # chain up the hierarchy\n            for h in node.handlers:\n                h.handle(r)\n            node = node.parent if node.propagate else None\n\n    def debug(self, m, **c): self.log(Level.DEBUG, m, **c)\n    def info(self, m, **c): self.log(Level.INFO, m, **c)\n    def error(self, m, **c): self.log(Level.ERROR, m, **c)\n\n_registry = {\"\": Logger(\"root\")}\n_registry[\"\"].level = Level.WARNING\n\ndef get_logger(name=\"\"):\n    if name not in _registry:\n        parent = get_logger(name.rpartition(\".\")[0]) if \".\" in name else _registry[\"\"]\n        _registry[name] = Logger(name, parent)\n    return _registry[name]\n\nget_logger().handlers.append(ConsoleHandler())\naudit = MemoryHandler(Level.INFO, JsonFormatter())\nget_logger(\"app\").handlers.append(audit)\nget_logger(\"app\").level = Level.INFO\n\ndb = get_logger(\"app.db\")\ndb.debug(\"connecting\")                           # below app's INFO: dropped\ndb.info(\"connected\", host=\"db1\")                 # app's JSON handler, then root's console\ndb.error(\"query failed\", table=\"orders\")         # same two handlers\nget_logger(\"lib\").info(\"noise\")                  # root is WARNING: dropped\nprint(\"audit captured:\", audit.lines)\nprint(get_logger(\"app.db\") is db)",
            "label": null,
            "output": "  console | INFO    app.db: connected\n  console | ERROR   app.db: query failed\naudit captured: ['{\"lvl\": \"INFO\", \"log\": \"app.db\", \"msg\": \"connected\", \"host\": \"db1\"}', '{\"lvl\": \"ERROR\", \"log\": \"app.db\", \"msg\": \"query failed\", \"table\": \"orders\"}']\nTrue",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "An async handler (a queue drained by a background thread) keeps slow destinations from blocking the request path. Filters (drop health-check logs, sample debug logs) are another link in the chain. Context such as a request id is added with a <code>contextvars</code> variable read by the formatter."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why check the level before building the record?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Logging calls sit on hot paths. Most debug calls are disabled in production, so the cheapest path must be a single integer comparison. Formatting messages, capturing stack info or building dicts for disabled levels wastes CPU. This is also why you pass arguments separately (<code>log.debug(\"x=%s\", x)</code>) instead of pre-formatting: formatting happens only if the record is emitted."
          }
        ]
      },
      {
        "q": "A file handler sometimes blocks for 200 ms on a slow disk. How do you stop it slowing requests?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Decouple producing from writing: the logger puts records on a bounded in-memory queue and a background thread drains it to the file (Python's <code>QueueHandler</code>/<code>QueueListener</code>). Decide what happens when the queue is full: block (safe, slow), drop debug records first, or drop and count. Flush the queue on shutdown so the last records are not lost."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "notification-service",
    "title": "Design a Notification Service",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Template Method",
      "Decorator",
      "Factory"
    ],
    "level": "medium",
    "summary": "Email, SMS and push channels behind one interface, user preferences, templates, retries and rate limits as decorators.",
    "intro": [
      "Design an internal notification library: services call <code>notify(user, event, data)</code>, and the library renders a message and delivers it over the channels the user has enabled (email, SMS, push), retrying transient failures and respecting per-user quiet hours."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Channels: email, SMS, push, more later. User preferences decide which channels each event uses. Messages are rendered from templates per event and channel. Transient failures are retried; quiet hours delay non-urgent messages. Every send is recorded."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Several channels with the same job",
                "Strategy",
                "<code>Channel.send(to, message)</code> per provider"
              ],
              [
                "Every channel: validate, render, send, record",
                "Template Method",
                "Base class fixes the steps; subclasses implement <code>deliver</code>"
              ],
              [
                "Add retries, rate limiting, logging to any channel",
                "Decorator",
                "Wrappers stack around a channel"
              ],
              [
                "Pick channel objects from preference names",
                "Factory",
                "<code>\"sms\"</code> &rarr; <code>SmsChannel</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Channel</code>",
                "Template: <code>send</code> = validate + deliver + record"
              ],
              [
                "<code>EmailChannel</code>, <code>SmsChannel</code>, <code>PushChannel</code>",
                "Concrete <code>deliver</code>"
              ],
              [
                "<code>Retrying</code>",
                "Decorator: retry transient failures"
              ],
              [
                "<code>NotificationService</code>",
                "Preferences, templates, quiet hours; fans out to channels"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "class TransientError(Exception): pass\n\nclass Channel:\n    name = \"base\"\n    def __init__(self): self.sent = []\n    def send(self, user, message):               # template method\n        to = self.address(user)\n        if not to:\n            return f\"{self.name}: skipped, no address\"\n        self.deliver(to, message)\n        self.sent.append((to, message))\n        return f\"{self.name}: sent to {to}\"\n    def address(self, user): raise NotImplementedError\n    def deliver(self, to, message): raise NotImplementedError\n\nclass EmailChannel(Channel):\n    name = \"email\"\n    def address(self, u): return u.get(\"email\")\n    def deliver(self, to, m): pass\n\nclass SmsChannel(Channel):\n    name = \"sms\"\n    def __init__(self, fail_times=0):\n        super().__init__(); self.fail_times = fail_times\n    def address(self, u): return u.get(\"phone\")\n    def deliver(self, to, m):\n        if self.fail_times:\n            self.fail_times -= 1\n            raise TransientError(\"gateway timeout\")\n\nclass PushChannel(Channel):\n    name = \"push\"\n    def address(self, u): return u.get(\"device\")\n    def deliver(self, to, m): pass\n\nclass Retrying:                                  # decorator\n    def __init__(self, inner, attempts=3):\n        self.inner, self.attempts, self.name = inner, attempts, inner.name\n    def send(self, user, message):\n        for i in range(1, self.attempts + 1):\n            try:\n                result = self.inner.send(user, message)\n                return result + (f\" (attempt {i})\" if i > 1 else \"\")\n            except TransientError:\n                continue\n        return f\"{self.name}: failed after {self.attempts} attempts\"\n\nTEMPLATES = {\n    (\"order_shipped\", \"email\"): \"Hi {name}, order {order} has shipped. Track: {url}\",\n    (\"order_shipped\", \"sms\"): \"Order {order} shipped\",\n    (\"order_shipped\", \"push\"): \"Your order is on the way\",\n    (\"otp\", \"sms\"): \"Your code is {code}\",\n}\n\nclass NotificationService:\n    def __init__(self, channels):\n        self.channels = {c.name: c for c in channels}      # factory by name\n        self.deferred = []\n\n    def notify(self, user, event, data, hour, urgent=False):\n        if not urgent and user.get(\"quiet\") and hour in range(*user[\"quiet\"]):\n            self.deferred.append((user[\"name\"], event))\n            return [f\"deferred {event}: quiet hours\"]\n        results = []\n        for ch in user[\"prefs\"].get(event, []):\n            template = TEMPLATES.get((event, ch))\n            if template:\n                results.append(self.channels[ch].send(user, template.format(name=user[\"name\"], **data)))\n        return results\n\nsvc = NotificationService([EmailChannel(), Retrying(SmsChannel(fail_times=2)), PushChannel()])\nann = {\"name\": \"Ann\", \"email\": \"ann@x.io\", \"phone\": \"+91-98\", \"quiet\": (22, 24),\n       \"prefs\": {\"order_shipped\": [\"email\", \"sms\", \"push\"], \"otp\": [\"sms\"]}}\nprint(svc.notify(ann, \"order_shipped\", {\"order\": \"A17\", \"url\": \"t.co/a17\"}, hour=10))\nprint(svc.notify(ann, \"order_shipped\", {\"order\": \"A18\", \"url\": \"t.co/a18\"}, hour=23))\nprint(svc.notify(ann, \"otp\", {\"code\": \"4821\"}, hour=23, urgent=True))\nprint(\"deferred queue:\", svc.deferred)",
            "label": null,
            "output": "['email: sent to ann@x.io', 'sms: sent to +91-98 (attempt 3)', 'push: skipped, no address']\n['deferred order_shipped: quiet hours']\n['sms: sent to +91-98']\ndeferred queue: [('Ann', 'order_shipped')]",
            "isError": false
          },
          {
            "type": "p",
            "html": "The first SMS failed twice and succeeded on the third attempt inside the <code>Retrying</code> decorator; the service never saw the failures. Ann has no device registered, so push was skipped by the template method's address step rather than by special-case code in the service."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A new channel (WhatsApp, Slack) is a <code>Channel</code> subclass plus templates. Rate limiting per user (no more than 3 SMS an hour) is another decorator. In production the service puts sends on a queue per channel so a slow provider never blocks callers, and records delivery receipts from provider webhooks."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you avoid sending the same notification twice when the caller retries?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Make <code>notify</code> idempotent with a key supplied by the caller (event id plus user plus channel). Record the key before or atomically with sending; a retry with the same key returns the earlier result. Providers that accept an idempotency key (many SMS and email APIs do) give a second layer of protection for retries after timeouts."
          }
        ]
      },
      {
        "q": "Why is retry a decorator rather than built into each channel?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Retry policy is a cross-cutting concern that should be the same across channels and configurable per deployment (attempts, backoff). As a decorator it is written once, tested once, and can be stacked with other wrappers (rate limit, metrics, circuit breaker) in whichever order is needed, without every channel duplicating loops and exception handling."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "pubsub-broker",
    "title": "Design an In-Memory Pub/Sub Message Broker",
    "group": "Design problems",
    "tags": [
      "Observer",
      "Mediator"
    ],
    "level": "hard",
    "summary": "Topics, subscriptions with offsets, consumer groups sharing work, acknowledgements, and replay.",
    "intro": [
      "Design a small in-memory message broker in the spirit of Kafka: producers publish messages to topics; each subscriber reads every message at its own pace; members of a consumer group share the messages of a topic; consumers acknowledge processed messages and can replay from an offset."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Topics are append-only logs with offsets. A subscription (group) has a committed offset. Within a group, each message is delivered to one member (round robin here). Messages are retained, so a new group can read from the beginning. Thread-safe publish and poll."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Many subscribers react to messages on a topic",
                "Observer (pull-based)",
                "Subscribers register interest; the broker tracks each one's position"
              ],
              [
                "Producers and consumers never reference each other",
                "Mediator",
                "The broker is the only thing both sides know"
              ],
              [
                "Each subscriber reads at its own pace, can replay",
                "Log + per-group offsets",
                "Retention decouples consumption from publication"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Topic</code>",
                "Append-only list of messages and a lock"
              ],
              [
                "<code>Group</code>",
                "Committed offset and members"
              ],
              [
                "<code>Broker</code>",
                "<code>publish</code>, <code>subscribe</code>, <code>poll</code>, <code>commit</code>, <code>seek</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import threading\nfrom collections import defaultdict\nfrom itertools import cycle\n\nclass Topic:\n    def __init__(self, name):\n        self.name, self.log, self.lock = name, [], threading.Lock()\n    def append(self, msg):\n        with self.lock:\n            self.log.append(msg)\n            return len(self.log) - 1\n\nclass Group:\n    def __init__(self, members):\n        self.offset = 0                     # next message to hand out\n        self.committed = 0\n        self.members = cycle(members)\n        self.lock = threading.Lock()\n\nclass Broker:\n    def __init__(self):\n        self.topics = {}\n        self.groups = defaultdict(dict)     # topic -> group name -> Group\n\n    def publish(self, topic, msg):\n        t = self.topics.setdefault(topic, Topic(topic))\n        return t.append(msg)\n\n    def subscribe(self, topic, group, members, from_beginning=True):\n        g = Group(members)\n        if not from_beginning:\n            g.offset = g.committed = len(self.topics.get(topic, Topic(topic)).log)\n        self.groups[topic][group] = g\n\n    def poll(self, topic, group, max_n=10):\n        \"\"\"hand out up to max_n messages, each to one member of the group\"\"\"\n        g, log = self.groups[topic][group], self.topics[topic].log\n        with g.lock:\n            batch = []\n            while g.offset < len(log) and len(batch) < max_n:\n                batch.append((next(g.members), g.offset, log[g.offset]))\n                g.offset += 1\n            return batch\n\n    def commit(self, topic, group, offset):\n        g = self.groups[topic][group]\n        g.committed = max(g.committed, offset + 1)\n\n    def seek(self, topic, group, offset):          # replay\n        g = self.groups[topic][group]\n        g.offset = g.committed = offset\n\nb = Broker()\nfor i in range(5):\n    b.publish(\"orders\", f\"order-{i}\")\nb.subscribe(\"orders\", \"billing\", [\"bill-1\", \"bill-2\"])\nb.subscribe(\"orders\", \"email\", [\"mailer\"])\n\nfor member, off, msg in b.poll(\"orders\", \"billing\", max_n=4):\n    print(f\"billing: {member} got {msg} @{off}\")\n    b.commit(\"orders\", \"billing\", off)\nprint(\"email gets everything too:\", [m for _, _, m in b.poll(\"orders\", \"email\")])\n\nb.subscribe(\"orders\", \"analytics\", [\"etl\"], from_beginning=False)\nb.publish(\"orders\", \"order-5\")\nprint(\"late group sees only new:\", [m for _, _, m in b.poll(\"orders\", \"analytics\")])\nb.seek(\"orders\", \"analytics\", 0)\nprint(\"after seek(0) replay:\", len(b.poll(\"orders\", \"analytics\")), \"messages\")\nprint(\"billing committed offset:\", b.groups[\"orders\"][\"billing\"].committed)",
            "label": null,
            "output": "billing: bill-1 got order-0 @0\nbilling: bill-2 got order-1 @1\nbilling: bill-1 got order-2 @2\nbilling: bill-2 got order-3 @3\nemail gets everything too: ['order-0', 'order-1', 'order-2', 'order-3', 'order-4']\nlate group sees only new: ['order-5']\nafter seek(0) replay: 6 messages\nbilling committed offset: 4",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Partitions (several logs per topic, keyed by message key) give parallelism with per-key ordering. Redelivery of unacknowledged messages needs a visibility timeout: a polled message not committed within N seconds is handed out again. Retention by size or age trims the log head. Durability means writing the log to disk before acknowledging the producer."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is the difference between the delivered offset and the committed offset?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The delivered offset is how far the broker has handed out messages; the committed offset is how far the group has confirmed processing. If a consumer crashes, the group restarts from the committed offset, so messages delivered but not committed are processed again: that is at-least-once delivery. Committing before processing gives at-most-once instead."
          }
        ]
      },
      {
        "q": "How would you guarantee ordering for all messages of one customer while still processing in parallel?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Split each topic into partitions and route messages by a hash of the customer id, so one customer's messages are always in one partition, in order. Assign each partition to exactly one member of a consumer group at a time; members process different partitions in parallel. Parallelism is capped by the partition count, and a hot customer can make one partition a bottleneck."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "task-scheduler",
    "title": "Design a Task Scheduler",
    "group": "Design problems",
    "tags": [
      "Command",
      "Strategy"
    ],
    "level": "medium",
    "summary": "One-off, delayed and recurring jobs as command objects, a min-heap by next run time, retry policies, cancellation.",
    "intro": [
      "Design a job scheduler library: callers submit tasks to run once at a time, after a delay, or repeatedly at a fixed interval; tasks can be cancelled; failed tasks are retried according to a policy. Time must be injectable so the scheduler can be tested without waiting."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "<code>schedule(task, at)</code>, <code>every(task, interval)</code>, <code>cancel(id)</code>. Tasks run in time order; ties in submission order. Recurring tasks are rescheduled after running. A failing task is retried with a delay from its retry policy, up to a limit."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Jobs are units of work stored and run later",
                "Command",
                "Each job wraps a callable with its schedule and state"
              ],
              [
                "Fixed interval vs exponential backoff retries",
                "Strategy",
                "Retry delay policy per job"
              ],
              [
                "Always run the earliest job next",
                "Min-heap",
                "O(log n) insert and pop by next run time"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Job</code>",
                "Command: callable, next run time, interval, attempts, cancelled flag"
              ],
              [
                "<code>RetryPolicy</code>",
                "Strategy: delay before attempt n, or give up"
              ],
              [
                "<code>Scheduler</code>",
                "Heap of jobs, a clock, <code>run_until(t)</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import heapq\nfrom dataclasses import dataclass, field\nfrom itertools import count\n\nclass NoRetry:\n    def delay(self, attempt): return None\n\nclass Backoff:\n    def __init__(self, base, max_attempts): self.base, self.max = base, max_attempts\n    def delay(self, attempt):\n        return self.base * 2 ** (attempt - 1) if attempt < self.max else None\n\n@dataclass(order=True)\nclass Job:\n    run_at: float\n    seq: int\n    name: str = field(compare=False)\n    fn: object = field(compare=False)\n    every: float | None = field(default=None, compare=False)\n    retry: object = field(default_factory=NoRetry, compare=False)\n    attempts: int = field(default=0, compare=False)\n    cancelled: bool = field(default=False, compare=False)\n\nclass Scheduler:\n    def __init__(self):\n        self.now, self.heap, self.jobs, self._seq = 0.0, [], {}, count()\n        self.log = []\n\n    def schedule(self, name, fn, at, every=None, retry=None):\n        job = Job(at, next(self._seq), name, fn, every, retry or NoRetry())\n        self.jobs[name] = job\n        heapq.heappush(self.heap, job)\n        return name\n\n    def cancel(self, name):\n        self.jobs[name].cancelled = True            # lazy deletion from the heap\n\n    def _push(self, job, at):\n        job.run_at, job.seq = at, next(self._seq)\n        heapq.heappush(self.heap, job)\n\n    def run_until(self, t):\n        while self.heap and self.heap[0].run_at <= t:\n            job = heapq.heappop(self.heap)\n            if job.cancelled:\n                continue\n            self.now = job.run_at\n            try:\n                job.fn()\n                job.attempts = 0\n                self.log.append(f\"t={self.now:>4}: {job.name} ok\")\n                if job.every:\n                    self._push(job, self.now + job.every)\n            except Exception as e:\n                job.attempts += 1\n                d = job.retry.delay(job.attempts)\n                self.log.append(f\"t={self.now:>4}: {job.name} failed ({e})\" +\n                                (f\", retry in {d}\" if d is not None else \", giving up\"))\n                if d is not None:\n                    self._push(job, self.now + d)\n        self.now = t\n\ncalls = {\"flaky\": 0}\ndef flaky():\n    calls[\"flaky\"] += 1\n    if calls[\"flaky\"] < 3:\n        raise ConnectionError(\"timeout\")\n\ns = Scheduler()\ns.schedule(\"heartbeat\", lambda: None, at=0, every=10)\ns.schedule(\"report\", lambda: None, at=15)\ns.schedule(\"sync\", flaky, at=5, retry=Backoff(base=2, max_attempts=5))\ns.schedule(\"broken\", lambda: 1 / 0, at=12, retry=Backoff(base=1, max_attempts=2))\ns.schedule(\"cleanup\", lambda: None, at=25)\ns.cancel(\"cleanup\")\ns.run_until(30)\nprint(\"\\n\".join(s.log))",
            "label": null,
            "output": "t=   0: heartbeat ok\nt=   5: sync failed (timeout), retry in 2\nt=   7: sync failed (timeout), retry in 4\nt=  10: heartbeat ok\nt=  11: sync ok\nt=  12: broken failed (division by zero), retry in 1\nt=  13: broken failed (division by zero), giving up\nt=  15: report ok\nt=  20: heartbeat ok\nt=  30: heartbeat ok",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Cron expressions are another way to compute the next run time (a strategy). Running jobs on a thread pool needs the scheduler loop to wait on a condition variable until the earliest run time or a new submission. Across several machines, a scheduler must ensure each job runs once: a database row lock or lease per job, taken before running."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why mark cancelled jobs instead of removing them from the heap?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Removing an arbitrary element from a binary heap is O(n) to find it plus O(log n) to fix the heap. Marking it cancelled is O(1), and the scheduler discards it when it reaches the top. The cost is that cancelled jobs occupy memory until then; if cancellations are frequent, rebuild the heap occasionally or count stale entries."
          }
        ]
      },
      {
        "q": "How do you make sure a scheduled job runs exactly once when you have three scheduler instances for availability?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Only one instance may claim each run. Store jobs in a database with their next run time; an instance claims due jobs with an atomic update (<code>UPDATE jobs SET owner=?, lease_until=? WHERE id=? AND (owner IS NULL OR lease_until &lt; now())</code>) or <code>SELECT ... FOR UPDATE SKIP LOCKED</code>. The lease expires if the owner dies, so another instance takes over. Because a crash after running but before recording can still cause a second run, the job itself should be idempotent."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "kv-store-transactions",
    "title": "Design a Key-Value Store with Nested Transactions",
    "group": "Design problems",
    "tags": [
      "Memento",
      "Command"
    ],
    "level": "medium",
    "summary": "GET/SET/DELETE plus BEGIN, ROLLBACK and COMMIT with nesting, using a stack of change sets.",
    "intro": [
      "Design an in-memory key-value store that supports transactions: <code>BEGIN</code> starts one (they can nest), <code>ROLLBACK</code> undoes everything since the matching BEGIN, <code>COMMIT</code> makes all open transactions permanent. A frequent machine-coding question."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "<code>set</code>, <code>get</code>, <code>delete</code>, <code>count(value)</code> (how many keys have that value) all O(1). Transactions nest; rollback affects only the innermost; commit applies all. Rollback with no transaction is an error."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Undo everything since BEGIN",
                "Memento (per-key undo log)",
                "Each transaction records the previous value of each key it first touches"
              ],
              [
                "Commands executed against the store, possibly from a script",
                "Command",
                "Parse lines into operations; easy to test and replay"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Copying the whole dictionary at BEGIN would also work but costs O(n) per transaction. Recording only the keys a transaction touches makes BEGIN O(1) and rollback proportional to the work done."
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Store</code>",
                "Data dict, value counts, stack of undo logs"
              ],
              [
                "<code>run(script)</code>",
                "Parses command lines and executes them"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from collections import Counter\n\nMISSING = object()\n\nclass Store:\n    def __init__(self):\n        self.data, self.counts, self.tx = {}, Counter(), []   # tx: stack of {key: old}\n\n    def _write(self, key, value):\n        if self.tx and key not in self.tx[-1]:\n            self.tx[-1][key] = self.data.get(key, MISSING)    # memento of first touch\n        old = self.data.get(key, MISSING)\n        if old is not MISSING:\n            self.counts[old] -= 1\n        if value is MISSING:\n            self.data.pop(key, None)\n        else:\n            self.data[key] = value\n            self.counts[value] += 1\n\n    def set(self, k, v): self._write(k, v)\n    def delete(self, k): self._write(k, MISSING)\n    def get(self, k): return self.data.get(k, \"NULL\")\n    def count(self, v): return self.counts[v]\n\n    def begin(self): self.tx.append({})\n\n    def rollback(self):\n        if not self.tx:\n            return \"NO TRANSACTION\"\n        undo = self.tx.pop()\n        saved, self.tx = self.tx, []                          # restore without logging\n        for k, old in undo.items():\n            self._write(k, old)\n        self.tx = saved\n\n    def commit(self):\n        if not self.tx:\n            return \"NO TRANSACTION\"\n        self.tx.clear()\n\ndef run(script):\n    s, out = Store(), []\n    for line in script.strip().splitlines():\n        line = line.strip()\n        cmd, *args = line.split()\n        result = getattr(s, cmd.lower())(*args)\n        if result is not None:\n            out.append(f\"{line:16} -> {result}\")\n    return out\n\nprint(\"\\n\".join(run(\"\"\"\n    SET a 10\n    BEGIN\n    SET a 20\n    BEGIN\n    SET a 30\n    DELETE b\n    GET a\n    ROLLBACK\n    GET a\n    COUNT 20\n    ROLLBACK\n    GET a\n    COUNT 20\n    ROLLBACK\n    BEGIN\n    SET x 5\n    BEGIN\n    SET y 5\n    COMMIT\n    COUNT 5\n    ROLLBACK\n\"\"\")))",
            "label": null,
            "output": "GET a            -> 30\nGET a            -> 20\nCOUNT 20         -> 1\nGET a            -> 10\nCOUNT 20         -> 0\nROLLBACK         -> NO TRANSACTION\nCOUNT 5          -> 2\nROLLBACK         -> NO TRANSACTION",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Isolation between concurrent clients (each sees its own uncommitted changes) needs per-client transaction stacks and a rule for conflicts at commit: optimistic concurrency with version numbers per key is the natural next step. Persistence adds a write-ahead log of committed change sets."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why record only the first old value of a key in each transaction?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Rollback must restore the value as it was when the transaction began. If a key is set three times inside one transaction, only the value before the first write matters; recording later ones would restore an intermediate value. Storing the first-touch value per key per transaction keeps the log minimal and the rollback correct."
          }
        ]
      },
      {
        "q": "How do nested commits work in this design?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Here <code>COMMIT</code> commits everything, which is the classic interview specification: the data dict already holds all changes, so commit simply discards the undo logs. An alternative semantics commits only the innermost transaction into its parent: merge its undo log into the parent's, keeping the parent's entry for any key both touched, so a later rollback of the parent still restores the original value."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "connection-pool",
    "title": "Design a Database Connection Pool",
    "group": "Design problems",
    "tags": [
      "Object Pool",
      "Proxy",
      "Factory"
    ],
    "level": "medium",
    "summary": "Bounded pool with blocking acquire and timeout, validation on borrow, a proxy that returns itself on close.",
    "intro": [
      "Design a connection pool: application threads borrow connections, use them, and give them back. Opening a connection is expensive, the database allows a limited number, and broken connections must not be handed out."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Max pool size; connections created lazily up to the max; <code>acquire(timeout)</code> blocks when all are in use and raises on timeout; connections validated on borrow and replaced if dead; <code>close()</code> on a borrowed connection returns it to the pool instead of closing it; usable as a context manager; thread-safe."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Expensive objects reused across callers",
                "Object Pool",
                "The core of the problem"
              ],
              [
                "Caller calls <code>conn.close()</code> but it must go back to the pool",
                "Proxy",
                "A wrapper intercepts <code>close</code> and forwards everything else"
              ],
              [
                "How to create a new connection is configurable",
                "Factory",
                "The pool receives a factory callable"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>RawConnection</code>",
                "The real driver connection (fake here)"
              ],
              [
                "<code>PooledConnection</code>",
                "Proxy: forwards calls; <code>close()</code> returns to pool"
              ],
              [
                "<code>Pool</code>",
                "Idle stack, in-use count, condition variable, factory, validation"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import threading, time\n\nclass RawConnection:\n    opened = 0\n    def __init__(self):\n        RawConnection.opened += 1\n        self.id, self.alive = RawConnection.opened, True\n    def execute(self, sql):\n        if not self.alive: raise ConnectionError(\"server closed the connection\")\n        return f\"conn{self.id}: {sql}\"\n    def ping(self): return self.alive\n    def close(self): self.alive = False\n\nclass PooledConnection:                               # proxy\n    def __init__(self, raw, pool): self._raw, self._pool = raw, pool\n    def __getattr__(self, name): return getattr(self._raw, name)\n    def close(self):\n        if self._raw is not None:\n            self._pool._release(self._raw)\n            self._raw = None                          # further use is a bug\n    def __enter__(self): return self\n    def __exit__(self, *exc): self.close()\n\nclass Pool:\n    def __init__(self, factory, max_size):\n        self.factory, self.max_size = factory, max_size\n        self.idle, self.in_use = [], 0\n        self.cond = threading.Condition()\n\n    def acquire(self, timeout=1.0):\n        deadline = time.monotonic() + timeout\n        with self.cond:\n            while True:\n                while self.idle:\n                    raw = self.idle.pop()\n                    if raw.ping():                    # validate on borrow\n                        self.in_use += 1\n                        return PooledConnection(raw, self)\n                if self.in_use < self.max_size:\n                    self.in_use += 1\n                    break                             # create outside the lock\n                remaining = deadline - time.monotonic()\n                if remaining <= 0 or not self.cond.wait(remaining):\n                    raise TimeoutError(f\"no connection within {timeout}s\")\n        try:\n            return PooledConnection(self.factory(), self)\n        except Exception:\n            with self.cond:\n                self.in_use -= 1; self.cond.notify()\n            raise\n\n    def _release(self, raw):\n        with self.cond:\n            self.in_use -= 1\n            self.idle.append(raw)\n            self.cond.notify()\n\npool = Pool(RawConnection, max_size=3)\nresults, lock = [], threading.Lock()\ndef worker(i):\n    with pool.acquire(timeout=2) as c:\n        time.sleep(0.01)\n        with lock: results.append(c.execute(f\"q{i}\"))\nts = [threading.Thread(target=worker, args=(i,)) for i in range(12)]\nfor t in ts: t.start()\nfor t in ts: t.join()\nprint(len(results), \"queries on\", RawConnection.opened, \"connections\")\n\ndead = pool.acquire(); dead._raw.alive = False; dead.close()   # server killed it\nwith pool.acquire() as c:\n    print(\"validated borrow:\", c.execute(\"select 1\"))\nholders = [pool.acquire() for _ in range(3)]\ntry:\n    pool.acquire(timeout=0.05)\nexcept TimeoutError as e:\n    print(\"TimeoutError:\", e)",
            "label": null,
            "output": "12 queries on 3 connections\nvalidated borrow: conn3: select 1\nTimeoutError: no connection within 0.05s",
            "isError": false
          },
          {
            "type": "p",
            "html": "Twelve threads ran their queries on three connections. The connection killed by the server was discarded on the next borrow, and the borrower transparently got another one. Creating a connection happens outside the lock, after reserving a slot, so a slow connect does not block threads returning connections."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Production pools add a minimum idle size (pre-warm), a max lifetime (recycle connections before the server or a proxy kills them), idle timeouts, leak detection (log a stack trace if a connection is held longer than N seconds) and metrics (wait time, pool usage) &mdash; the knobs you see in HikariCP or SQLAlchemy's <code>QueuePool</code>."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What happens if a thread forgets to return a connection, and how do you defend against it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The pool permanently loses a slot; after enough leaks every acquire times out. Defences: hand out connections through a context manager so return is automatic; record the borrower's stack at acquire time and log it when a connection is held longer than a threshold; optionally reclaim connections held past a hard limit (dangerous if the holder is still using it)."
          }
        ]
      },
      {
        "q": "How big should the pool be?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Smaller than people expect. A database does useful work on roughly as many concurrent queries as it has cores (plus some for I/O waits); beyond that, extra connections just queue inside the database and add context switching and memory. A common starting point is around (2 &times; cores) + disks per database server, divided across all application instances that share it. Measure: if threads wait on the pool while the database CPU is idle, grow it; if the database is saturated, a bigger pool makes latency worse."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "text-editor",
    "title": "Design a Text Editor with Undo/Redo",
    "group": "Design problems",
    "tags": [
      "Command",
      "Memento"
    ],
    "level": "medium",
    "summary": "Insert, delete and replace as command objects with undo, redo stacks, merging of consecutive typing.",
    "intro": [
      "Design the editing core of a text editor: insert text at the cursor, delete a range, find-and-replace, with unlimited undo and redo. Typing a word should undo as one step, not one step per character."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Operations: insert, delete (backspace), replace-all. <code>undo</code> reverts the last operation; <code>redo</code> re-applies it; a new edit after undo discards the redo history. Consecutive single-character inserts at adjacent positions merge into one undo step."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Undo and redo of edits",
                "Command",
                "Each edit is an object with <code>do</code> and <code>undo</code>"
              ],
              [
                "Replace-all has no cheap inverse",
                "Memento",
                "That command snapshots the text before applying"
              ],
              [
                "Typing merges into one step",
                "Command merging",
                "A new insert command can absorb itself into the previous one"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Document</code>",
                "Text buffer and cursor; low-level insert/delete"
              ],
              [
                "<code>Insert</code>, <code>Delete</code>, <code>ReplaceAll</code>",
                "Commands with <code>do</code>/<code>undo</code>; <code>Insert.merge</code>"
              ],
              [
                "<code>Editor</code>",
                "Undo and redo stacks; runs commands"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "class Document:\n    def __init__(self): self.text = \"\"\n    def insert(self, pos, s): self.text = self.text[:pos] + s + self.text[pos:]\n    def delete(self, pos, n):\n        removed = self.text[pos:pos + n]\n        self.text = self.text[:pos] + self.text[pos + n:]\n        return removed\n\nclass Insert:\n    def __init__(self, pos, s): self.pos, self.s = pos, s\n    def do(self, doc): doc.insert(self.pos, self.s)\n    def undo(self, doc): doc.delete(self.pos, len(self.s))\n    def merge(self, other):                       # typing \"c\" right after \"ab\"\n        if isinstance(other, Insert) and other.pos == self.pos + len(self.s) \\\n                and len(other.s) == 1 and \" \" not in (other.s, self.s[-1]):\n            self.s += other.s\n            return True\n        return False\n\nclass Delete:\n    def __init__(self, pos, n): self.pos, self.n, self.removed = pos, n, \"\"\n    def do(self, doc): self.removed = doc.delete(self.pos, self.n)\n    def undo(self, doc): doc.insert(self.pos, self.removed)\n    def merge(self, other): return False\n\nclass ReplaceAll:\n    def __init__(self, old, new): self.old, self.new, self.snapshot = old, new, None\n    def do(self, doc):\n        self.snapshot = doc.text                      # memento\n        doc.text = doc.text.replace(self.old, self.new)\n    def undo(self, doc): doc.text = self.snapshot\n    def merge(self, other): return False\n\nclass Editor:\n    def __init__(self):\n        self.doc, self.undos, self.redos = Document(), [], []\n\n    def run(self, cmd):\n        cmd.do(self.doc)\n        self.redos.clear()\n        if self.undos and self.undos[-1].merge(cmd):\n            return\n        self.undos.append(cmd)\n\n    def type(self, pos, text):\n        for i, ch in enumerate(text):\n            self.run(Insert(pos + i, ch))\n\n    def undo(self):\n        if self.undos:\n            cmd = self.undos.pop(); cmd.undo(self.doc); self.redos.append(cmd)\n\n    def redo(self):\n        if self.redos:\n            cmd = self.redos.pop(); cmd.do(self.doc); self.undos.append(cmd)\n\ned = Editor()\ned.type(0, \"hello world\")\nprint(repr(ed.doc.text), \"| undo steps:\", len(ed.undos))\ned.run(ReplaceAll(\"o\", \"0\"))\ned.run(Delete(0, 6))\nprint(repr(ed.doc.text))\ned.undo(); print(\"undo  ->\", repr(ed.doc.text))\ned.undo(); print(\"undo  ->\", repr(ed.doc.text))\ned.redo(); print(\"redo  ->\", repr(ed.doc.text))\ned.type(len(ed.doc.text), \"!\")\ned.redo(); print(\"redo after a new edit does nothing ->\", repr(ed.doc.text))\nfor _ in range(5): ed.undo()\nprint(\"undo everything ->\", repr(ed.doc.text))",
            "label": null,
            "output": "'hello world' | undo steps: 3\n'w0rld'\nundo  -> 'hell0 w0rld'\nundo  -> 'hello world'\nredo  -> 'hell0 w0rld'\nredo after a new edit does nothing -> 'hell0 w0rld!'\nundo everything -> ''",
            "isError": false
          },
          {
            "type": "p",
            "html": "&ldquo;hello world&rdquo; became three undo steps &mdash; &ldquo;hello&rdquo;, the space, &ldquo;world&rdquo; &mdash; because merging stops at a space, which is how real editors group typing into words."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Large files need a better buffer than a Python string (every insert copies the text): a gap buffer, a rope or a piece table makes inserts O(log n) or amortised O(1). Collaborative editing replaces the undo stack with operational transformation or CRDTs, where commands from different users are transformed against each other."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why does a new edit clear the redo stack?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Redo replays commands that were undone, assuming the document is in the state they were undone from. After a new edit the document has diverged; replaying an old command (say, an insert at position 40) could land in the wrong place or corrupt text. Editors with branching undo history (Vim's undo tree) keep the alternatives instead of discarding them."
          }
        ]
      },
      {
        "q": "Command with inverse vs Memento snapshot: when do you use which?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Use an inverse when one exists and is cheap: insert/delete store only the affected text, so memory is proportional to the edit. Use a snapshot when the operation has no simple inverse or touches the whole document (replace-all, reformat): store the previous state, ideally only the changed region. Many editors mix both, as here."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "file-system",
    "title": "Design an In-Memory File System",
    "group": "Design problems",
    "tags": [
      "Composite",
      "Iterator"
    ],
    "level": "medium",
    "summary": "Directories and files as a composite tree, path resolution, mkdir -p, ls, cat, du and find.",
    "intro": [
      "Design an in-memory file system with <code>mkdir</code> (creating parents), <code>write</code>/<code>append</code> to a file, <code>read</code>, <code>ls</code>, total size of a directory and a <code>find</code> by name pattern. LeetCode 588 is the core of it."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Absolute paths like <code>/a/b/c.txt</code>. <code>ls</code> on a file returns its name; on a directory, its sorted children. Size of a directory is the sum of its contents. Errors for missing paths and writing to a directory."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Directories contain files and directories",
                "Composite",
                "<code>File</code> and <code>Directory</code> share <code>size()</code> and <code>name</code>"
              ],
              [
                "Walk every entry for find/du",
                "Iterator (generator)",
                "A recursive generator yields (path, node) pairs"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Node</code>",
                "Common interface: name, <code>size()</code>"
              ],
              [
                "<code>File</code>",
                "Content"
              ],
              [
                "<code>Directory</code>",
                "Children dict; <code>size()</code> sums children; <code>walk()</code>"
              ],
              [
                "<code>FileSystem</code>",
                "Path parsing and the public operations"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import fnmatch\n\nclass Node:\n    def __init__(self, name): self.name = name\n\nclass File(Node):\n    def __init__(self, name): super().__init__(name); self.content = \"\"\n    def size(self): return len(self.content)\n\nclass Directory(Node):\n    def __init__(self, name): super().__init__(name); self.children = {}\n    def size(self): return sum(c.size() for c in self.children.values())\n    def walk(self, path=\"\"):\n        for name in sorted(self.children):\n            child, child_path = self.children[name], f\"{path}/{name}\"\n            yield child_path, child\n            if isinstance(child, Directory):\n                yield from child.walk(child_path)\n\nclass FileSystem:\n    def __init__(self): self.root = Directory(\"\")\n\n    @staticmethod\n    def _parts(path): return [p for p in path.split(\"/\") if p]\n\n    def _resolve(self, path):\n        node = self.root\n        for part in self._parts(path):\n            if not isinstance(node, Directory) or part not in node.children:\n                raise FileNotFoundError(path)\n            node = node.children[part]\n        return node\n\n    def mkdir(self, path):\n        node = self.root\n        for part in self._parts(path):\n            nxt = node.children.setdefault(part, Directory(part))\n            if isinstance(nxt, File):\n                raise NotADirectoryError(f\"{part} is a file\")\n            node = nxt\n\n    def write(self, path, text, append=False):\n        *dirs, name = self._parts(path)\n        parent = self._resolve(\"/\" + \"/\".join(dirs))\n        node = parent.children.setdefault(name, File(name))\n        if isinstance(node, Directory):\n            raise IsADirectoryError(path)\n        node.content = node.content + text if append else text\n\n    def read(self, path):\n        node = self._resolve(path)\n        if isinstance(node, Directory):\n            raise IsADirectoryError(path)\n        return node.content\n\n    def ls(self, path=\"/\"):\n        node = self._resolve(path)\n        return [node.name] if isinstance(node, File) else sorted(node.children)\n\n    def du(self, path=\"/\"): return self._resolve(path).size()\n\n    def find(self, pattern, path=\"/\"):\n        base = self._resolve(path)\n        prefix = path.rstrip(\"/\")\n        return [prefix + p for p, n in base.walk() if fnmatch.fnmatch(n.name, pattern)]\n\nfs = FileSystem()\nfs.mkdir(\"/home/ann/docs\")\nfs.mkdir(\"/var/log\")\nfs.write(\"/home/ann/docs/cv.txt\", \"python, sql\")\nfs.write(\"/home/ann/notes.txt\", \"buy milk\")\nfs.write(\"/home/ann/notes.txt\", \", call bob\", append=True)\nfs.write(\"/var/log/app.log\", \"x\" * 100)\nprint(fs.ls(\"/\"), fs.ls(\"/home/ann\"), fs.ls(\"/home/ann/notes.txt\"))\nprint(repr(fs.read(\"/home/ann/notes.txt\")))\nprint(\"du /home:\", fs.du(\"/home\"), \"| du /:\", fs.du(\"/\"))\nprint(\"find *.txt:\", fs.find(\"*.txt\"))\nfor bad in (lambda: fs.read(\"/home/ann\"), lambda: fs.ls(\"/nope\"), lambda: fs.mkdir(\"/home/ann/notes.txt/x\")):\n    try:\n        bad()\n    except OSError as e:\n        print(type(e).__name__, e)",
            "label": null,
            "output": "['home', 'var'] ['docs', 'notes.txt'] ['notes.txt']\n'buy milk, call bob'\ndu /home: 29 | du /: 129\nfind *.txt: ['/home/ann/docs/cv.txt', '/home/ann/notes.txt']\nIsADirectoryError /home/ann\nFileNotFoundError /nope\nNotADirectoryError notes.txt is a file",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Permissions and owners are attributes on <code>Node</code> checked during resolution. Symlinks are a third node type resolved with a depth limit to avoid loops. Caching each directory's size makes <code>du</code> O(1) but every write must update ancestors &mdash; a classic read-versus-write trade-off."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How would you support <code>mv /a/b /c/d</code> efficiently?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Resolve both parents, check that the destination is not inside the source (moving a directory into its own subtree would create a cycle), detach the node from the old parent's children and attach it under the new name. Because children are stored by reference, the move is O(path length), regardless of subtree size. Update cached sizes on both ancestor chains if you keep them."
          }
        ]
      },
      {
        "q": "Why is the Composite pattern a good fit here?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Operations like size, listing, search and permission checks must work the same whether the target is a file or a whole tree. With a common interface, <code>du</code> is one call on the root and the recursion lives in <code>Directory.size</code>; client code never type-checks every child. New node types (symlink, mount point) slot in by implementing the same interface."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "coffee-order",
    "title": "Design a Coffee / Pizza Ordering System with Add-ons",
    "group": "Design problems",
    "tags": [
      "Decorator",
      "Builder"
    ],
    "level": "easy",
    "summary": "Base drinks wrapped by stackable add-ons that change price and description, assembled with a builder.",
    "intro": [
      "Design the menu model for a coffee shop: a customer picks a base drink and any number of add-ons (extra shot, oat milk, syrup, whipped cream), possibly the same add-on twice. Each add-on changes the price and the description. New add-ons appear every season."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Compute price and description for any combination. Add-ons can repeat. Adding a new add-on must not change existing classes. Validate a few rules (at most 4 shots)."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Optional extras that stack in any combination",
                "Decorator",
                "Each add-on wraps a beverage; no subclass per combination"
              ],
              [
                "Assemble an order step by step with validation",
                "Builder",
                "A fluent builder applies add-ons and checks rules at <code>build()</code>"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Subclassing per combination (<code>LatteWithOatAndVanilla</code>) explodes combinatorially; a list of add-on names with a price table would work for price but loses per-add-on behaviour (an add-on that changes size, or whose price depends on the base)."
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Beverage</code>",
                "Interface: <code>cost()</code>, <code>description()</code>"
              ],
              [
                "<code>Espresso</code>, <code>Latte</code>",
                "Base drinks"
              ],
              [
                "<code>AddOn</code> and subclasses",
                "Decorators wrapping a beverage"
              ],
              [
                "<code>OrderBuilder</code>",
                "Fluent assembly and validation"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from abc import ABC, abstractmethod\n\nclass Beverage(ABC):\n    @abstractmethod\n    def cost(self) -> int: ...\n    @abstractmethod\n    def description(self) -> str: ...\n    def shots(self): return 0\n\nclass Espresso(Beverage):\n    def cost(self): return 120\n    def description(self): return \"espresso\"\n    def shots(self): return 1\n\nclass Latte(Beverage):\n    def cost(self): return 180\n    def description(self): return \"latte\"\n    def shots(self): return 1\n\nclass AddOn(Beverage):\n    price, label = 0, \"\"\n    def __init__(self, inner: Beverage): self.inner = inner\n    def cost(self): return self.inner.cost() + self.price\n    def description(self): return f\"{self.inner.description()} + {self.label}\"\n    def shots(self): return self.inner.shots()\n\nclass ExtraShot(AddOn):\n    price, label = 40, \"shot\"\n    def shots(self): return self.inner.shots() + 1\n\nclass OatMilk(AddOn):\n    price, label = 35, \"oat milk\"\n\nclass Vanilla(AddOn):\n    price, label = 25, \"vanilla\"\n\nclass Large(AddOn):                       # price depends on what it wraps\n    label = \"large\"\n    def cost(self): return round(self.inner.cost() * 1.3)\n\nADDONS = {cls.__name__.lower(): cls for cls in (ExtraShot, OatMilk, Vanilla, Large)}\n\nclass OrderBuilder:\n    def __init__(self, base): self.drink = base\n    def add(self, name, times=1):\n        for _ in range(times):\n            self.drink = ADDONS[name](self.drink)\n        return self\n    def build(self):\n        if self.drink.shots() > 4:\n            raise ValueError(f\"{self.drink.shots()} shots is too many\")\n        return self.drink\n\norders = [\n    OrderBuilder(Espresso()).build(),\n    OrderBuilder(Latte()).add(\"oatmilk\").add(\"vanilla\").build(),\n    OrderBuilder(Latte()).add(\"extrashot\", 2).add(\"large\").build(),\n    OrderBuilder(Latte()).add(\"large\").add(\"extrashot\", 2).build(),\n]\nfor d in orders:\n    print(f\"{d.cost():4}  {d.description()}  ({d.shots()} shots)\")\ntry:\n    OrderBuilder(Espresso()).add(\"extrashot\", 4).build()\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": " 120  espresso  (1 shots)\n 240  latte + oat milk + vanilla  (1 shots)\n 338  latte + shot + shot + large  (3 shots)\n 314  latte + large + shot + shot  (3 shots)\nValueError: 5 shots is too many",
            "isError": false
          },
          {
            "type": "p",
            "html": "The last two orders contain the same items in a different order and cost different amounts, because <code>Large</code> multiplies whatever it wraps. Whether that is a bug or a pricing policy is a product decision; the design makes it visible. To make it order-independent, apply size last in the builder."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A seasonal add-on is one new class and one registry entry. Pizzas work identically: a base (thin crust) wrapped by toppings, with rules like &ldquo;at most 2 cheese&rdquo; in the builder. Persisting an order means saving the base and the list of add-on names, and rebuilding the decorator chain on load."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Decorator vs a list of add-on names on the drink: which would you choose?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "If add-ons only add a fixed price and a label, a list plus a price table is simpler, serialises trivially and is easy to query (&ldquo;how many oat milks today?&rdquo;). Decorators earn their keep when add-ons have behaviour: pricing that depends on the base or on other add-ons, changing the size or shot count, or validation. A common compromise stores the list and builds decorators from it when pricing."
          }
        ]
      },
      {
        "q": "How does the Decorator pattern respect the Open/Closed principle here?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Existing beverages and add-ons are never modified to support a new add-on; you add a class that wraps any <code>Beverage</code>. Clients still see one interface (<code>cost</code>, <code>description</code>), so the checkout code is unchanged too."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "payment-gateway",
    "title": "Design a Payment Processing Module",
    "group": "Design problems",
    "tags": [
      "Adapter",
      "Strategy",
      "Factory",
      "State"
    ],
    "level": "medium",
    "summary": "Multiple providers behind one interface via adapters, routing strategy with failover, idempotency and payment states.",
    "intro": [
      "Design the payment module of an e-commerce backend. It must support several payment providers (each with its own SDK), choose a provider per payment (by method, cost or availability), fail over when one is down, and never charge a customer twice for one order."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Methods: card, UPI, wallet. Providers have different APIs and units. A routing rule picks providers in order of preference; on a provider outage, try the next. Payments move through created &rarr; authorised &rarr; captured, or failed / refunded. Repeated requests with the same idempotency key return the original result."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Each provider SDK has a different API",
                "Adapter",
                "One <code>PaymentProvider</code> interface; one adapter per SDK"
              ],
              [
                "Choose provider by method, fee, success rate",
                "Strategy",
                "Routing is a swappable policy"
              ],
              [
                "Create adapters from configuration",
                "Factory",
                "Provider name &rarr; adapter instance"
              ],
              [
                "Payment lifecycle with legal transitions",
                "State (transition table)",
                "No capture before authorisation, no refund of a failed payment"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>PaymentProvider</code>",
                "Interface: <code>charge(amount_paise, method, key)</code>"
              ],
              [
                "<code>RazorpayAdapter</code>, <code>StripeAdapter</code>",
                "Translate to each fake SDK"
              ],
              [
                "<code>Router</code>",
                "Strategy: ordered providers for a payment"
              ],
              [
                "<code>Payment</code>",
                "Amount, status, provider; transitions"
              ],
              [
                "<code>PaymentService</code>",
                "Idempotency, routing with failover"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "class ProviderDown(Exception): pass\n\nclass RazorpaySDK:                          # amounts in paise, returns dicts\n    def __init__(self, up=True): self.up = up\n    def create_payment(self, paise, mode):\n        if not self.up: raise ProviderDown(\"razorpay 503\")\n        return {\"razorpay_payment_id\": \"pay_R1\", \"status\": \"captured\"}\n\nclass StripeSDK:                            # amounts in rupees as float, returns objects\n    class Charge:\n        def __init__(self, ok): self.paid, self.id = ok, \"ch_S1\"\n    def charge(self, amount, currency, source):\n        return self.Charge(ok=source != \"card_declined\")\n\nclass RazorpayAdapter:\n    name, methods = \"razorpay\", {\"card\", \"upi\", \"wallet\"}\n    def __init__(self, sdk): self.sdk = sdk\n    def charge(self, paise, method, token):\n        r = self.sdk.create_payment(paise, method)\n        return r[\"status\"] == \"captured\", r[\"razorpay_payment_id\"]\n\nclass StripeAdapter:\n    name, methods = \"stripe\", {\"card\"}\n    def __init__(self, sdk): self.sdk = sdk\n    def charge(self, paise, method, token):\n        c = self.sdk.charge(paise / 100, \"inr\", token)\n        return c.paid, c.id\n\nclass CheapestFirst:\n    FEES = {\"razorpay\": 2.0, \"stripe\": 2.9}\n    def order(self, providers, method):\n        ok = [p for p in providers if method in p.methods]\n        return sorted(ok, key=lambda p: self.FEES[p.name])\n\nTRANSITIONS = {\"created\": {\"captured\", \"failed\"}, \"captured\": {\"refunded\"},\n               \"failed\": set(), \"refunded\": set()}\n\nclass Payment:\n    def __init__(self, key, paise): self.key, self.paise, self.status, self.ref = key, paise, \"created\", None\n    def move(self, to):\n        if to not in TRANSITIONS[self.status]:\n            raise ValueError(f\"{self.status} -> {to} not allowed\")\n        self.status = to\n\nclass PaymentService:\n    def __init__(self, providers, router):\n        self.providers, self.router, self.by_key = providers, router, {}\n\n    def pay(self, key, paise, method, token=\"tok\"):\n        if key in self.by_key:                        # idempotent retry\n            return self.by_key[key]\n        p = Payment(key, paise)\n        self.by_key[key] = p\n        for provider in self.router.order(self.providers, method):\n            try:\n                ok, ref = provider.charge(paise, method, token)\n            except ProviderDown as e:\n                print(f\"  {provider.name} down ({e}), failing over\")\n                continue\n            p.ref = f\"{provider.name}:{ref}\"\n            p.move(\"captured\" if ok else \"failed\")\n            return p\n        p.move(\"failed\")\n        return p\n\nsvc = PaymentService([RazorpayAdapter(RazorpaySDK(up=False)), StripeAdapter(StripeSDK())], CheapestFirst())\na = svc.pay(\"order-1\", 49_900, \"card\")\nprint(\"order-1:\", a.status, a.ref)\nagain = svc.pay(\"order-1\", 49_900, \"card\")\nprint(\"retry returns the same payment:\", again is a)\nprint(\"order-2:\", svc.pay(\"order-2\", 9_900, \"upi\").status, \"(only razorpay does UPI, and it is down)\")\nprint(\"order-3:\", svc.pay(\"order-3\", 100, \"card\", token=\"card_declined\").status)\na.move(\"refunded\"); print(\"refund order-1:\", a.status)\ntry:\n    a.move(\"captured\")\nexcept ValueError as e:\n    print(\"ValueError:\", e)",
            "label": null,
            "output": "  razorpay down (razorpay 503), failing over\norder-1: captured stripe:ch_S1\nretry returns the same payment: True\n  razorpay down (razorpay 503), failing over\norder-2: failed (only razorpay does UPI, and it is down)\n  razorpay down (razorpay 503), failing over\norder-3: failed\nrefund order-1: refunded\nValueError: refunded -> captured not allowed",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Adding a provider is one adapter plus a router entry. Routing by success rate (send traffic to whichever provider is approving most payments for this card network right now) is a smarter strategy fed by metrics. The provider's webhooks (payment captured, refunded, disputed) feed the same state machine, which is why transitions must be validated: webhooks arrive late, twice, or out of order."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "The provider call timed out. Did the charge happen? What do you do?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "You do not know, so treat the payment as pending, not failed. Never retry with a different provider blindly, or the customer may be charged twice. Retry the same provider with the same idempotency key (most providers deduplicate on it), or query the provider's status API for that key, or wait for its webhook. Only when the provider confirms the charge did not happen is failover safe. A reconciliation job compares your records with provider settlement reports daily."
          }
        ]
      },
      {
        "q": "Why put an adapter in front of every provider SDK even if you only use one today?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It confines the vendor's types, units (paise vs rupees), error classes and quirks to one class. The rest of the codebase depends on your interface, so tests can use a fake provider, an SDK upgrade touches one file, and adding a second provider for failover or cost does not ripple through checkout code."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "shopping-cart",
    "title": "Design a Shopping Cart with Discount Rules",
    "group": "Design problems",
    "tags": [
      "Strategy",
      "Composite",
      "Chain of Responsibility"
    ],
    "level": "medium",
    "summary": "Cart lines, composable promotion rules (percentage, buy-X-get-Y, threshold, coupon), best-discount selection.",
    "intro": [
      "Design the pricing of a shopping cart. Marketing keeps inventing promotions: 10% off a category, buy 2 get 1 free, &#8377;200 off orders above &#8377;2000, coupon codes. Some promotions stack, others are exclusive and the customer should get the better one."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Cart with products, quantities and categories. A discount rule computes a discount for a cart (or zero). Rules can be combined: <em>all of</em> (stack) or <em>best of</em> (exclusive). Final total never goes below zero. Show which rules applied."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Many kinds of discount, more coming",
                "Strategy",
                "Each rule is a class with <code>apply(cart)</code>"
              ],
              [
                "Rules combined as stack or best-of, nested",
                "Composite",
                "<code>AllOf</code> and <code>BestOf</code> are rules containing rules"
              ],
              [
                "Rules evaluated in sequence, each sees the previous result",
                "Chain of Responsibility",
                "Threshold rules apply to the already-discounted subtotal"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Line</code>, <code>Cart</code>",
                "Products, quantities, prices in paise"
              ],
              [
                "<code>Rule</code>",
                "Strategy: <code>discount(cart, subtotal)</code> &rarr; (amount, labels)"
              ],
              [
                "<code>PercentOffCategory</code>, <code>BuyXGetY</code>, <code>Threshold</code>, <code>Coupon</code>",
                "Concrete rules"
              ],
              [
                "<code>AllOf</code>, <code>BestOf</code>",
                "Composite rules"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass\nclass Line:\n    sku: str\n    category: str\n    price: int            # paise\n    qty: int\n\nclass Cart:\n    def __init__(self, *lines, coupon=None): self.lines, self.coupon = list(lines), coupon\n    def subtotal(self): return sum(l.price * l.qty for l in self.lines)\n\nclass PercentOffCategory:\n    def __init__(self, cat, pct): self.cat, self.pct = cat, pct\n    def discount(self, cart, running):\n        amt = sum(l.price * l.qty for l in cart.lines if l.category == self.cat) * self.pct // 100\n        return amt, [f\"{self.pct}% off {self.cat}\"] if amt else []\n\nclass BuyXGetY:\n    def __init__(self, sku, x, y): self.sku, self.x, self.y = sku, x, y\n    def discount(self, cart, running):\n        for l in cart.lines:\n            if l.sku == self.sku:\n                free = (l.qty // (self.x + self.y)) * self.y\n                if free:\n                    return free * l.price, [f\"buy {self.x} get {self.y} on {self.sku}\"]\n        return 0, []\n\nclass Threshold:\n    def __init__(self, above, off): self.above, self.off = above, off\n    def discount(self, cart, running):\n        return (self.off, [f\"{self.off // 100} off above {self.above // 100}\"]) if running > self.above else (0, [])\n\nclass Coupon:\n    def __init__(self, code, off): self.code, self.off = code, off\n    def discount(self, cart, running):\n        return (self.off, [f\"coupon {self.code}\"]) if cart.coupon == self.code else (0, [])\n\nclass AllOf:                                      # stack, in order (a chain)\n    def __init__(self, *rules): self.rules = rules\n    def discount(self, cart, running):\n        total, labels = 0, []\n        for r in self.rules:\n            amt, lab = r.discount(cart, running - total)\n            total += amt; labels += lab\n        return total, labels\n\nclass BestOf:                                     # exclusive: customer gets the best\n    def __init__(self, *rules): self.rules = rules\n    def discount(self, cart, running):\n        return max((r.discount(cart, running) for r in self.rules), key=lambda d: d[0])\n\ndef checkout(cart, rule):\n    sub = cart.subtotal()\n    off, labels = rule.discount(cart, sub)\n    off = min(off, sub)\n    return f\"subtotal {sub / 100:.0f} - {off / 100:.0f} = {(sub - off) / 100:.0f}  {labels}\"\n\npromotions = AllOf(\n    BestOf(PercentOffCategory(\"shoes\", 20), BuyXGetY(\"socks\", 2, 1)),   # exclusive pair\n    Threshold(above=2000_00, off=200_00),                               # applies after them\n    Coupon(\"WELCOME\", 100_00),\n)\ncarts = {\n    \"shoes + socks\": Cart(Line(\"runner\", \"shoes\", 3000_00, 1), Line(\"socks\", \"apparel\", 200_00, 3)),\n    \"lots of socks\": Cart(Line(\"socks\", \"apparel\", 200_00, 9)),\n    \"coupon, small\": Cart(Line(\"cap\", \"apparel\", 500_00, 1), coupon=\"WELCOME\"),\n}\nfor name, cart in carts.items():\n    print(f\"{name:14} {checkout(cart, promotions)}\")",
            "label": null,
            "output": "shoes + socks  subtotal 3600 - 800 = 2800  ['20% off shoes', '200 off above 2000']\nlots of socks  subtotal 1800 - 600 = 1200  ['buy 2 get 1 on socks']\ncoupon, small  subtotal 500 - 100 = 400  ['coupon WELCOME']",
            "isError": false
          },
          {
            "type": "p",
            "html": "In the first cart the shoe discount (600) beat the socks offer (200), so only it applied; the threshold rule then saw the already-discounted 3000 and still applied. In the second, nine socks cost 1800 before any discount, so the threshold did not apply. A rule tree like this is data: marketing changes promotions by changing the tree, not the code."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Rules can be loaded from JSON into this composite structure, so promotions are configured without deploys. Exclusions (&ldquo;not with sale items&rdquo;) are filters a rule applies to the lines it considers. For auditability, each label should carry the rule id and the amount, so customer support can explain a total."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why pass the running total into each rule?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Some rules depend on what is left after earlier discounts (a threshold on the payable amount, a percentage of the remaining total), and the order of application changes the result. Making the running total explicit puts that dependency in the interface and makes the order a visible, testable decision in the rule tree."
          }
        ]
      },
      {
        "q": "How would you guarantee the customer always gets the best combination of exclusive offers?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "For a small number of exclusive groups, evaluate each option and take the maximum, as <code>BestOf</code> does; nested combinations stay correct because each node returns its own best. With many interacting offers (one item can only be used by one offer), the problem becomes an optimisation (assignment of items to offers), solvable by search over the few relevant offers or integer programming; most shops avoid it by limiting stacking rules."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "food-delivery",
    "title": "Design a Food Delivery Order Lifecycle",
    "group": "Design problems",
    "tags": [
      "State",
      "Observer",
      "Strategy"
    ],
    "level": "medium",
    "summary": "Order states with guarded transitions per actor, cancellation and refund rules by state, notifications to all parties.",
    "intro": [
      "Design the order workflow of a Swiggy/Zomato-style app. An order passes through placed, accepted by the restaurant, preparing, picked up by a rider, delivered; it can be cancelled or rejected at some points. Customer, restaurant and rider each see updates, and refunds depend on when an order is cancelled."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Only certain actors may trigger certain transitions (the restaurant accepts; the rider picks up). Cancellation by the customer is free before acceptance, 50% refund while preparing, none after pickup. Every transition notifies the relevant parties and is recorded with a timestamp."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Allowed actions depend on the order's state",
                "State",
                "Each state class lists its transitions and who may trigger them"
              ],
              [
                "Customer, restaurant and rider apps update on each change",
                "Observer",
                "Listeners per party"
              ],
              [
                "Refund depends on the state at cancellation",
                "Strategy (per state)",
                "Each state knows its refund fraction"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>OrderState</code> subclasses",
                "Placed, Accepted, Preparing, PickedUp, Delivered, Cancelled"
              ],
              [
                "<code>Order</code>",
                "Context: amount, current state, history, listeners"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "class OrderState:\n    name = \"?\"\n    transitions: dict = {}          # action -> (actor allowed, next state class name)\n    refund = 0.0\n    def act(self, order, action, actor):\n        if action not in self.transitions:\n            raise ValueError(f\"cannot {action} when {self.name}\")\n        allowed, nxt = self.transitions[action]\n        if actor != allowed:\n            raise PermissionError(f\"{actor} cannot {action}\")\n        return STATES[nxt]()\n\nclass Placed(OrderState):\n    name, refund = \"placed\", 1.0\n    transitions = {\"accept\": (\"restaurant\", \"Accepted\"), \"reject\": (\"restaurant\", \"Cancelled\"),\n                   \"cancel\": (\"customer\", \"Cancelled\")}\nclass Accepted(OrderState):\n    name, refund = \"accepted\", 1.0\n    transitions = {\"start\": (\"restaurant\", \"Preparing\"), \"cancel\": (\"customer\", \"Cancelled\")}\nclass Preparing(OrderState):\n    name, refund = \"preparing\", 0.5\n    transitions = {\"pickup\": (\"rider\", \"PickedUp\"), \"cancel\": (\"customer\", \"Cancelled\")}\nclass PickedUp(OrderState):\n    name, refund = \"picked up\", 0.0\n    transitions = {\"deliver\": (\"rider\", \"Delivered\")}\nclass Delivered(OrderState):\n    name = \"delivered\"\nclass Cancelled(OrderState):\n    name = \"cancelled\"\n\nSTATES = {c.__name__: c for c in (Placed, Accepted, Preparing, PickedUp, Delivered, Cancelled)}\n\nclass Order:\n    def __init__(self, oid, amount):\n        self.id, self.amount, self.state = oid, amount, Placed()\n        self.history, self.listeners, self.refunded = [(\"placed\", 0)], [], 0\n\n    def act(self, action, actor, t):\n        before = self.state\n        self.state = before.act(self, action, actor)\n        if isinstance(self.state, Cancelled):\n            self.refunded = round(self.amount * before.refund)\n        self.history.append((self.state.name, t))\n        for fn in self.listeners:\n            fn(self, action, actor)\n\ndef notify(order, action, actor):\n    parties = {\"accept\": \"customer\", \"start\": \"customer\", \"pickup\": \"customer\",\n               \"deliver\": \"customer, restaurant\", \"cancel\": \"restaurant, rider\", \"reject\": \"customer\"}\n    print(f\"  [{order.id}] {actor} did {action!r} -> now {order.state.name}; notify {parties[action]}\")\n\no = Order(\"A1\", 600)\no.listeners.append(notify)\nfor action, actor, t in [(\"accept\", \"restaurant\", 1), (\"start\", \"restaurant\", 2),\n                         (\"pickup\", \"rider\", 15), (\"deliver\", \"rider\", 30)]:\n    o.act(action, actor, t)\nprint(\"timeline:\", o.history)\n\nb = Order(\"B2\", 800); b.listeners.append(notify)\nb.act(\"accept\", \"restaurant\", 1); b.act(\"start\", \"restaurant\", 3)\nfor args in [(\"pickup\", \"customer\", 4), (\"cancel\", \"customer\", 5), (\"deliver\", \"rider\", 6)]:\n    try:\n        b.act(*args)\n    except (ValueError, PermissionError) as e:\n        print(f\"  {type(e).__name__}: {e}\")\nprint(\"B2 refund:\", b.refunded)",
            "label": null,
            "output": "  [A1] restaurant did 'accept' -> now accepted; notify customer\n  [A1] restaurant did 'start' -> now preparing; notify customer\n  [A1] rider did 'pickup' -> now picked up; notify customer\n  [A1] rider did 'deliver' -> now delivered; notify customer, restaurant\ntimeline: [('placed', 0), ('accepted', 1), ('preparing', 2), ('picked up', 15), ('delivered', 30)]\n  [B2] restaurant did 'accept' -> now accepted; notify customer\n  [B2] restaurant did 'start' -> now preparing; notify customer\n  PermissionError: customer cannot pickup\n  [B2] customer did 'cancel' -> now cancelled; notify restaurant, rider\n  ValueError: cannot deliver when cancelled\nB2 refund: 400",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A &ldquo;rider assigned&rdquo; sub-flow and timeouts (auto-cancel if the restaurant does not accept within 5 minutes) are a new state and a scheduled event. Because states are data plus a small class, the state diagram can be generated from <code>transitions</code> for documentation and tested exhaustively: every (state, action, actor) combination either succeeds or raises."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "The restaurant's &ldquo;accept&rdquo; and the customer's &ldquo;cancel&rdquo; arrive at the same time. What should happen?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Transitions must be serialised per order: apply them one at a time in a single place (a database row update with a version check, or a per-order actor/queue). Whichever is applied first wins; the second is evaluated against the new state. If cancel wins, accept fails with &ldquo;cannot accept when cancelled&rdquo; and the restaurant is told; if accept wins, cancel succeeds with the refund rule of Accepted. A compare-and-set on (order id, expected state) is the usual implementation."
          }
        ]
      },
      {
        "q": "Why include the actor in the transition rules?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Authorisation is part of the workflow: a customer must not be able to mark food as picked up, and a rider must not cancel on the customer's behalf. Encoding the allowed actor next to each transition keeps the rule in one place, and the API layer only needs to pass who is calling."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "traffic-light",
    "title": "Design a Traffic Light Controller",
    "group": "Design problems",
    "tags": [
      "State",
      "Observer"
    ],
    "level": "easy",
    "summary": "Phases as states with durations, a tick-driven controller, pedestrian requests and an emergency override.",
    "intro": [
      "Design the controller for a four-way intersection: north-south and east-west roads alternate green, yellow and red; a pedestrian button shortens the current green; an emergency vehicle can force all-red."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Phases: NS green (30 s) &rarr; NS yellow (5 s) &rarr; EW green (30 s) &rarr; EW yellow (5 s) &rarr; repeat. Never green in both directions. Pedestrian request: if the current green has more than 10 s left, cut it to 10 s. Emergency: switch to all-red until cleared. Lights (displays) are notified on every change."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Fixed cycle of phases, each with its own duration and next phase",
                "State",
                "Each phase knows its duration and successor"
              ],
              [
                "Physical lights and a monitoring dashboard react to changes",
                "Observer",
                "Displays subscribe to phase changes"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Phase</code>",
                "Name, lights per direction, duration, next phase"
              ],
              [
                "<code>Controller</code>",
                "Current phase, time remaining, <code>tick</code>, <code>pedestrian</code>, <code>emergency</code>"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Phase:\n    name: str\n    ns: str\n    ew: str\n    duration: int\n    next: str\n\nPHASES = {p.name: p for p in [\n    Phase(\"NS_GREEN\", \"green\", \"red\", 30, \"NS_YELLOW\"),\n    Phase(\"NS_YELLOW\", \"yellow\", \"red\", 5, \"EW_GREEN\"),\n    Phase(\"EW_GREEN\", \"red\", \"green\", 30, \"EW_YELLOW\"),\n    Phase(\"EW_YELLOW\", \"red\", \"yellow\", 5, \"NS_GREEN\"),\n    Phase(\"ALL_RED\", \"red\", \"red\", 10**9, \"NS_GREEN\"),\n]}\nassert all(not (p.ns == \"green\" and p.ew == \"green\") for p in PHASES.values())   # safety invariant\n\nclass Controller:\n    def __init__(self):\n        self.listeners, self.t = [], 0\n        self._enter(\"NS_GREEN\")\n\n    def _enter(self, name):\n        self.phase, self.left = PHASES[name], PHASES[name].duration\n        for fn in self.listeners:\n            fn(self.t, self.phase)\n\n    def tick(self, seconds=1):\n        for _ in range(seconds):\n            self.t += 1\n            self.left -= 1\n            if self.left == 0:\n                self._enter(self.phase.next)\n\n    def pedestrian(self):\n        if \"green\" in (self.phase.ns, self.phase.ew) and self.left > 10:\n            self.left = 10\n\n    def emergency(self, on):\n        if on:\n            self._enter(\"ALL_RED\")\n        elif self.phase.name == \"ALL_RED\":\n            self._enter(\"NS_GREEN\")\n\nc = Controller()\nc.listeners.append(lambda t, p: print(f\"  t={t:3}  NS {p.ns:6} EW {p.ew:6} ({p.name})\"))\nc.tick(36)                         # NS green, NS yellow, into EW green\nc.tick(5); c.pedestrian()          # 24 s left on EW green: cut to 10\nc.tick(16)\nc.emergency(True); c.tick(20); c.emergency(False)",
            "label": null,
            "output": "  t= 30  NS yellow EW red    (NS_YELLOW)\n  t= 35  NS red    EW green  (EW_GREEN)\n  t= 51  NS red    EW yellow (EW_YELLOW)\n  t= 56  NS green  EW red    (NS_GREEN)\n  t= 57  NS red    EW red    (ALL_RED)\n  t= 77  NS green  EW red    (NS_GREEN)",
            "isError": false
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Adaptive timing (longer green for the busier road, from sensor counts) replaces fixed durations with a duration strategy per phase. A left-turn arrow is another phase in the cycle. Hardware safety is enforced twice: by the invariant in software and by a conflict monitor in hardware that forces flashing red if both directions ever show green."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you guarantee the controller can never show green in both directions?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Make it structurally impossible and then check it. Phases are a fixed table where each entry defines both directions at once, so there is no separate &ldquo;set NS green&rdquo; operation that could race with &ldquo;set EW green&rdquo;. Assert the invariant over the table at start-up (as above) and in tests over every reachable phase. Real intersections add an independent hardware conflict monitor."
          }
        ]
      },
      {
        "q": "Why drive the controller with <code>tick()</code> instead of sleeping in a loop?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Separating time from logic makes the controller deterministic and testable: a test can advance 36 simulated seconds instantly and assert exactly which phases occurred. In production a small driver calls <code>tick()</code> once a second from a real timer. The same idea (inject the clock) applies to any time-dependent design."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "document-export",
    "title": "Design a Document Model with Multiple Export Formats",
    "group": "Design problems",
    "tags": [
      "Visitor",
      "Composite",
      "Builder"
    ],
    "level": "medium",
    "summary": "A document tree of elements exported to HTML, Markdown and plain text, plus word count - without touching element classes.",
    "intro": [
      "Design the document model of a report generator. Documents contain sections, headings, paragraphs, lists and tables (sections nest). The same document must be exported to HTML, Markdown and plain text, and new outputs (PDF, a word count, a table of contents) keep being requested."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Stable set of element types; growing set of operations over them. Operations must traverse nested sections. Building a document should read well in code."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Many new operations over a fixed set of element types",
                "Visitor",
                "Each export is one visitor class; element classes never change"
              ],
              [
                "Sections contain elements, including other sections",
                "Composite",
                "A section's <code>accept</code> visits its children"
              ],
              [
                "Assembling a document in code",
                "Builder",
                "Fluent <code>.heading().para().bullets()</code> with nested sections"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Element</code> subclasses",
                "Heading, Paragraph, BulletList, Section; each has <code>accept(visitor)</code>"
              ],
              [
                "<code>HtmlExporter</code>, <code>MarkdownExporter</code>, <code>WordCounter</code>",
                "Visitors with one method per element type"
              ],
              [
                "<code>DocBuilder</code>",
                "Fluent construction with nested sections"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field\n\nclass Element:\n    def accept(self, v):\n        return getattr(v, \"visit_\" + type(self).__name__.lower())(self)   # double dispatch\n\n@dataclass\nclass Heading(Element):\n    text: str\n    level: int = 1\n\n@dataclass\nclass Paragraph(Element):\n    text: str\n\n@dataclass\nclass BulletList(Element):\n    items: list\n\n@dataclass\nclass Section(Element):\n    title: str\n    children: list = field(default_factory=list)\n\nclass HtmlExporter:\n    def visit_heading(self, h): return f\"<h{h.level}>{h.text}</h{h.level}>\"\n    def visit_paragraph(self, p): return f\"<p>{p.text}</p>\"\n    def visit_bulletlist(self, b): return \"<ul>\" + \"\".join(f\"<li>{i}</li>\" for i in b.items) + \"</ul>\"\n    def visit_section(self, s):\n        return f'<section><h2>{s.title}</h2>{\"\".join(c.accept(self) for c in s.children)}</section>'\n\nclass MarkdownExporter:\n    def __init__(self): self.depth = 1\n    def visit_heading(self, h): return \"#\" * h.level + \" \" + h.text\n    def visit_paragraph(self, p): return p.text\n    def visit_bulletlist(self, b): return \"\\n\".join(f\"- {i}\" for i in b.items)\n    def visit_section(self, s):\n        self.depth += 1\n        body = [(\"#\" * self.depth) + \" \" + s.title] + [c.accept(self) for c in s.children]\n        self.depth -= 1\n        return \"\\n\\n\".join(body)\n\nclass WordCounter:\n    def visit_heading(self, h): return len(h.text.split())\n    def visit_paragraph(self, p): return len(p.text.split())\n    def visit_bulletlist(self, b): return sum(len(i.split()) for i in b.items)\n    def visit_section(self, s): return len(s.title.split()) + sum(c.accept(self) for c in s.children)\n\nclass DocBuilder:\n    def __init__(self): self.stack = [Section(\"root\")]\n    def _add(self, e): self.stack[-1].children.append(e); return self\n    def heading(self, t, level=1): return self._add(Heading(t, level))\n    def para(self, t): return self._add(Paragraph(t))\n    def bullets(self, *items): return self._add(BulletList(list(items)))\n    def section(self, title):\n        s = Section(title); self._add(s); self.stack.append(s); return self\n    def end(self): self.stack.pop(); return self\n    def build(self): return self.stack[0].children\n\ndoc = (DocBuilder()\n       .heading(\"Q3 Report\")\n       .para(\"Revenue grew in every region.\")\n       .section(\"Highlights\").bullets(\"North +12%\", \"South +7%\")\n           .section(\"Risks\").para(\"Supply costs are rising.\").end()\n       .end()\n       .build())\n\nprint(\"\".join(e.accept(HtmlExporter()) for e in doc))\nmd = MarkdownExporter()\nprint(\"\\n\\n\".join(e.accept(md) for e in doc))\nprint(\"words:\", sum(e.accept(WordCounter()) for e in doc))",
            "label": null,
            "output": "<h1>Q3 Report</h1><p>Revenue grew in every region.</p><section><h2>Highlights</h2><ul><li>North +12%</li><li>South +7%</li></ul><section><h2>Risks</h2><p>Supply costs are rising.</p></section></section>\n# Q3 Report\n\nRevenue grew in every region.\n\n## Highlights\n\n- North +12%\n- South +7%\n\n### Risks\n\nSupply costs are rising.\nwords: 17",
            "isError": false
          },
          {
            "type": "p",
            "html": "Adding the word counter required no change to any element class. Adding a new element type (an image) would require a method in every visitor; that is the trade-off Visitor makes, and it is the right one here because outputs grow faster than element types."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "A table-of-contents visitor collects headings and section titles with their depth. PDF export is another visitor driving a PDF library. If element types ever need to grow fast, switch the dispatch to <code>functools.singledispatch</code> functions so a missing case fails loudly at one registration point."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "What is double dispatch, and how does <code>accept</code> achieve it here?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The method that runs depends on two types: the element's and the visitor's. A normal method call dispatches on one (the receiver). <code>element.accept(visitor)</code> dispatches on the element's type, and inside it the element calls the visitor method named for its own type (<code>visit_paragraph</code>), dispatching on the visitor's type. Python can shortcut this with <code>getattr</code> by name or with <code>singledispatch</code> on the element type."
          }
        ]
      },
      {
        "q": "When would you not use Visitor for exports?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "When element types change often (every new type touches every visitor), when there are only one or two operations (a method per class is simpler), or when operations need private state of the elements (visitors only see the public interface). For a handful of formats over a stable model, Visitor keeps each format in one file, which is the main win."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "expression-evaluator",
    "title": "Design an Expression Evaluator (Calculator)",
    "group": "Design problems",
    "tags": [
      "Interpreter",
      "Composite",
      "Visitor"
    ],
    "level": "medium",
    "summary": "Tokenise, parse into an AST with precedence, evaluate with variables, and pretty-print - each a separate component.",
    "intro": [
      "Design a calculator that evaluates expressions like <code>2 * (x + 3) - y / 4</code> with variables, operator precedence and parentheses, and can also print the expression back in a normalised form. New operators (power, functions) will be added."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Operators + &minus; * / with standard precedence and left associativity, unary minus, parentheses, numbers and variables. Clear errors for syntax problems and unknown variables. Evaluation and printing are separate operations over the same parsed tree."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Grammar of a small language, evaluated over a tree",
                "Interpreter",
                "Each node type knows how to evaluate itself"
              ],
              [
                "Expressions contain sub-expressions",
                "Composite",
                "<code>BinOp</code> holds two child expressions"
              ],
              [
                "Printing, simplifying, compiling are more operations on the same tree",
                "Visitor",
                "Kept separate from the node classes (here: printing)"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>tokenize</code>",
                "String &rarr; tokens"
              ],
              [
                "<code>Parser</code>",
                "Recursive descent: <code>expr</code> &rarr; <code>term</code> &rarr; <code>factor</code>"
              ],
              [
                "<code>Num</code>, <code>Var</code>, <code>Neg</code>, <code>BinOp</code>",
                "AST nodes with <code>eval(env)</code>"
              ],
              [
                "<code>to_str</code>",
                "Printer that adds only necessary parentheses"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import re\nfrom dataclasses import dataclass\n\nTOKEN = re.compile(r\"\\s*(?:(\\d+\\.?\\d*)|([A-Za-z_]\\w*)|(.))\")\n\ndef tokenize(src):\n    out = []\n    for num, name, op in TOKEN.findall(src):\n        if num: out.append((\"num\", float(num)))\n        elif name: out.append((\"var\", name))\n        elif op.strip(): out.append((\"op\", op))\n    return out + [(\"end\", None)]\n\n@dataclass\nclass Num:\n    v: float\n    def eval(self, env): return self.v\n\n@dataclass\nclass Var:\n    name: str\n    def eval(self, env):\n        if self.name not in env:\n            raise NameError(f\"unknown variable {self.name!r}\")\n        return env[self.name]\n\n@dataclass\nclass Neg:\n    e: object\n    def eval(self, env): return -self.e.eval(env)\n\nOPS = {\"+\": lambda a, b: a + b, \"-\": lambda a, b: a - b, \"*\": lambda a, b: a * b, \"/\": lambda a, b: a / b}\nPREC = {\"+\": 1, \"-\": 1, \"*\": 2, \"/\": 2}\n\n@dataclass\nclass BinOp:\n    op: str\n    l: object\n    r: object\n    def eval(self, env): return OPS[self.op](self.l.eval(env), self.r.eval(env))\n\nclass Parser:\n    \"\"\"expr := term (('+'|'-') term)* ; term := factor (('*'|'/') factor)* ;\n       factor := num | var | '-' factor | '(' expr ')'\"\"\"\n    def __init__(self, src): self.toks, self.i = tokenize(src), 0\n    def peek(self): return self.toks[self.i]\n    def take(self): self.i += 1; return self.toks[self.i - 1]\n\n    def parse(self):\n        e = self.expr()\n        if self.peek()[0] != \"end\":\n            raise SyntaxError(f\"unexpected {self.peek()[1]!r}\")\n        return e\n\n    def expr(self):\n        e = self.term()\n        while self.peek() in ((\"op\", \"+\"), (\"op\", \"-\")):\n            e = BinOp(self.take()[1], e, self.term())       # left-associative\n        return e\n\n    def term(self):\n        e = self.factor()\n        while self.peek() in ((\"op\", \"*\"), (\"op\", \"/\")):\n            e = BinOp(self.take()[1], e, self.factor())\n        return e\n\n    def factor(self):\n        kind, v = self.take()\n        if kind == \"num\": return Num(v)\n        if kind == \"var\": return Var(v)\n        if (kind, v) == (\"op\", \"-\"): return Neg(self.factor())\n        if (kind, v) == (\"op\", \"(\"):\n            e = self.expr()\n            if self.take() != (\"op\", \")\"):\n                raise SyntaxError(\"missing )\")\n            return e\n        raise SyntaxError(f\"unexpected {v!r}\")\n\ndef to_str(e, parent=0, right=False):                        # printing as a separate operation\n    match e:\n        case Num(v): return f\"{v:g}\"\n        case Var(n): return n\n        case Neg(x): return \"-\" + to_str(x, 3)\n        case BinOp(op, l, r):\n            p = PREC[op]\n            s = f\"{to_str(l, p)} {op} {to_str(r, p, right=True)}\"\n            need = p < parent or (right and p == parent and op in \"-/\")\n            return f\"({s})\" if need else s\n\nenv = {\"x\": 4, \"y\": 10}\nfor src in [\"2 * (x + 3) - y / 4\", \"((1 + 2)) + (3 * 4)\", \"10 - (4 - 3)\", \"10 - 4 - 3\", \"-(x - 1) * -2\"]:\n    tree = Parser(src).parse()\n    print(f\"{src:22} => {to_str(tree):18} = {tree.eval(env):g}\")\nfor bad in [\"2 * (3 + 4\", \"2 + * 3\", \"z + 1\"]:\n    try:\n        print(Parser(bad).parse().eval(env))\n    except (SyntaxError, NameError) as e:\n        print(f\"{bad:22} => {type(e).__name__}: {e}\")",
            "label": null,
            "output": "2 * (x + 3) - y / 4    => 2 * (x + 3) - y / 4 = 11.5\n((1 + 2)) + (3 * 4)    => 1 + 2 + 3 * 4      = 15\n10 - (4 - 3)           => 10 - (4 - 3)       = 9\n10 - 4 - 3             => 10 - 4 - 3         = 3\n-(x - 1) * -2          => -(x - 1) * -2      = 6\n2 * (3 + 4             => SyntaxError: missing )\n2 + * 3                => SyntaxError: unexpected '*'\nz + 1                  => NameError: unknown variable 'z'",
            "isError": false
          },
          {
            "type": "p",
            "html": "The printer removed redundant parentheses but kept the ones that matter: <code>10 - (4 - 3)</code> needs them because subtraction is not associative, while <code>((1 + 2)) + (3 * 4)</code> needs none."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Exponentiation (right-associative, binds tighter than unary minus) is a new grammar level and an entry in <code>OPS</code>. Functions (<code>max(a, b)</code>) add a <code>Call</code> node. A simplifier (<code>x * 1 &rarr; x</code>, constant folding) is another tree-to-tree operation like the printer."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How does the grammar encode precedence and associativity?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Each precedence level is its own rule, and lower-precedence rules are built from higher ones: <code>expr</code> combines <code>term</code>s with + and &minus;, <code>term</code> combines <code>factor</code>s with * and /. So <code>2 + 3 * 4</code> parses the multiplication inside a <code>term</code> first. Left associativity comes from the loop that folds operands left to right (<code>((10 - 4) - 3)</code>); a right-associative operator would recurse on the right instead."
          }
        ]
      },
      {
        "q": "Why not just call Python's <code>eval</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It executes arbitrary Python: <code>__import__('os').system(...)</code> in a user-supplied expression is remote code execution. Even with restricted globals it is hard to make safe. It also cannot give you a tree to print, analyse or transform. If you need Python syntax, parse with <code>ast.parse(src, mode=\"eval\")</code> and walk only an allow-listed set of node types."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "http-middleware",
    "title": "Design an HTTP Middleware Pipeline",
    "group": "Design problems",
    "tags": [
      "Chain of Responsibility",
      "Decorator"
    ],
    "level": "medium",
    "summary": "Composable middleware (logging, auth, rate limit, error handling) wrapping a handler, with short-circuiting.",
    "intro": [
      "Design the request pipeline of a small web framework. Each request passes through middleware &mdash; request id, logging, authentication, rate limiting, error handling &mdash; before reaching a route handler, and the response passes back through them in reverse. Any middleware may answer early (401, 429)."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Middleware are composable and ordered. Each can modify the request, call the next layer, modify the response, or short-circuit. Exceptions from handlers become 500 responses. Adding a middleware must not change existing ones."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Request passes through handlers in order; any may stop it",
                "Chain of Responsibility",
                "Each middleware decides whether to call <code>next</code>"
              ],
              [
                "Each layer wraps the rest and acts before and after",
                "Decorator",
                "Middleware has the same interface as a handler: request in, response out"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Request</code>, <code>Response</code>",
                "Plain data"
              ],
              [
                "Middleware",
                "Functions <code>(request, next) &rarr; response</code>"
              ],
              [
                "<code>build_pipeline</code>",
                "Folds middleware around the final handler"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "from dataclasses import dataclass, field\nfrom itertools import count\nfrom collections import defaultdict\n\n@dataclass\nclass Request:\n    path: str\n    headers: dict = field(default_factory=dict)\n    user: str | None = None\n    ctx: dict = field(default_factory=dict)\n\n@dataclass\nclass Response:\n    status: int\n    body: str\n    headers: dict = field(default_factory=dict)\n\n_ids = count(1)\ndef request_id(req, nxt):\n    req.ctx[\"id\"] = f\"req-{next(_ids)}\"\n    resp = nxt(req)\n    resp.headers[\"X-Request-Id\"] = req.ctx[\"id\"]\n    return resp\n\nlog = []\ndef logging_mw(req, nxt):\n    resp = nxt(req)\n    log.append(f\"{req.ctx['id']} {req.path} -> {resp.status}\")\n    return resp\n\ndef errors(req, nxt):\n    try:\n        return nxt(req)\n    except Exception as e:\n        return Response(500, f\"internal error ({type(e).__name__})\")\n\nTOKENS = {\"t-ann\": \"ann\"}\ndef auth(req, nxt):\n    if req.path.startswith(\"/public\"):\n        return nxt(req)\n    user = TOKENS.get(req.headers.get(\"Authorization\", \"\"))\n    if not user:\n        return Response(401, \"unauthorised\")          # short-circuit\n    req.user = user\n    return nxt(req)\n\ndef rate_limit(limit):\n    seen = defaultdict(int)\n    def mw(req, nxt):\n        key = req.user or \"anon\"\n        seen[key] += 1\n        if seen[key] > limit:\n            return Response(429, \"slow down\", {\"Retry-After\": \"60\"})\n        return nxt(req)\n    return mw\n\ndef router(req):\n    if req.path == \"/me\": return Response(200, f\"hello {req.user}\")\n    if req.path == \"/public/ping\": return Response(200, \"pong\")\n    if req.path == \"/boom\": raise KeyError(\"bug\")\n    return Response(404, \"not found\")\n\ndef build_pipeline(middleware, handler):\n    for mw in reversed(middleware):                    # outermost first in the list\n        handler = (lambda m, n: lambda req: m(req, n))(mw, handler)\n    return handler\n\napp = build_pipeline([request_id, logging_mw, errors, auth, rate_limit(2)], router)\ncalls = [(\"/public/ping\", {}), (\"/me\", {}), (\"/me\", {\"Authorization\": \"t-ann\"}),\n         (\"/boom\", {\"Authorization\": \"t-ann\"}), (\"/me\", {\"Authorization\": \"t-ann\"})]\nfor path, headers in calls:\n    r = app(Request(path, headers))\n    print(r.status, r.body, r.headers)\nprint(log)",
            "label": null,
            "output": "200 pong {'X-Request-Id': 'req-1'}\n401 unauthorised {'X-Request-Id': 'req-2'}\n200 hello ann {'X-Request-Id': 'req-3'}\n500 internal error (KeyError) {'X-Request-Id': 'req-4'}\n429 slow down {'Retry-After': '60', 'X-Request-Id': 'req-5'}\n['req-1 /public/ping -> 200', 'req-2 /me -> 401', 'req-3 /me -> 200', 'req-4 /boom -> 500', 'req-5 /me -> 429']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Order is the design. <code>errors</code> sits inside <code>logging_mw</code>, so the crashing request was logged as a 500 rather than escaping; <code>auth</code> runs before <code>rate_limit</code>, so limits are per user. The third authenticated call to <code>/me</code> was rate limited because <code>/boom</code> also counted."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "CORS, compression and caching are more middleware. Per-route middleware is a second pipeline built for each route. This is exactly how WSGI/ASGI middleware, Express and Django middleware work: each layer is a callable wrapping the next."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Where should the error-handling middleware go in the chain, and why?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Near the outside, so it catches exceptions from everything inside it (auth bugs, handler bugs) and converts them to a response &mdash; but inside the logging and request-id middleware, so failed requests are still logged with their id and the id header is still set. If it were innermost, an exception thrown by auth or rate limiting would escape unhandled."
          }
        ]
      },
      {
        "q": "How is this both Chain of Responsibility and Decorator?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Chain of Responsibility: a request is passed along a sequence of handlers, any of which can handle it and stop the chain (401, 429). Decorator: each middleware has the same interface as the handler it wraps and can add behaviour before and after the inner call (timing, headers). Middleware pipelines are the standard example of the two patterns being the same structure."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "query-builder",
    "title": "Design a SQL Query Builder",
    "group": "Design problems",
    "tags": [
      "Builder",
      "Composite",
      "Interpreter"
    ],
    "level": "medium",
    "summary": "Fluent, immutable query construction with composable conditions and parameter binding (no string concatenation).",
    "intro": [
      "Design a small query builder like SQLAlchemy Core or Knex: code builds <code>SELECT</code> queries fluently, conditions combine with AND/OR/NOT, and the output is SQL text plus bound parameters, never values pasted into the string."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "<code>select(cols).from_(table).where(cond).order_by(col).limit(n)</code>. Conditions: comparisons, IN, AND/OR/NOT nested arbitrarily. Builders are immutable (each call returns a new builder), so a base query can be reused safely. Output <code>(sql, params)</code> with <code>?</code> placeholders."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Step-by-step construction of a complex object",
                "Builder",
                "Each clause is a method; <code>build()</code> renders"
              ],
              [
                "Conditions nest: (a AND (b OR NOT c))",
                "Composite",
                "<code>And</code>/<code>Or</code>/<code>Not</code> contain conditions"
              ],
              [
                "Conditions render themselves to SQL fragments",
                "Interpreter",
                "Each node knows its SQL and its parameters"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Col</code>",
                "Column with operator methods producing conditions"
              ],
              [
                "<code>Cond</code>, <code>And</code>, <code>Or</code>, <code>Not</code>",
                "Condition tree; <code>render()</code> &rarr; (sql, params)"
              ],
              [
                "<code>Query</code>",
                "Immutable builder: each method returns a modified copy"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import sqlite3\nfrom dataclasses import dataclass, replace\n\nclass Cond:\n    def __and__(self, o): return And(self, o)\n    def __or__(self, o): return Or(self, o)\n    def __invert__(self): return Not(self)\n\n@dataclass(frozen=True)\nclass Compare(Cond):\n    col: str\n    op: str\n    value: object\n    def render(self):\n        if self.op == \"IN\":\n            marks = \", \".join(\"?\" * len(self.value))\n            return f\"{self.col} IN ({marks})\", list(self.value)\n        return f\"{self.col} {self.op} ?\", [self.value]\n\n@dataclass(frozen=True)\nclass And(Cond):\n    a: Cond\n    b: Cond\n    def render(self):\n        (sa, pa), (sb, pb) = self.a.render(), self.b.render()\n        return f\"({sa} AND {sb})\", pa + pb\n\n@dataclass(frozen=True)\nclass Or(Cond):\n    a: Cond\n    b: Cond\n    def render(self):\n        (sa, pa), (sb, pb) = self.a.render(), self.b.render()\n        return f\"({sa} OR {sb})\", pa + pb\n\n@dataclass(frozen=True)\nclass Not(Cond):\n    a: Cond\n    def render(self):\n        s, p = self.a.render()\n        return f\"NOT {s}\", p\n\nclass Col:\n    def __init__(self, name):\n        if not name.isidentifier():\n            raise ValueError(f\"bad column name {name!r}\")\n        self.name = name\n    def __eq__(self, v): return Compare(self.name, \"=\", v)\n    def __gt__(self, v): return Compare(self.name, \">\", v)\n    def __lt__(self, v): return Compare(self.name, \"<\", v)\n    def in_(self, values): return Compare(self.name, \"IN\", tuple(values))\n\n@dataclass(frozen=True)\nclass Query:\n    table: str = \"\"\n    cols: tuple = (\"*\",)\n    cond: Cond | None = None\n    order: tuple = ()\n    lim: int | None = None\n\n    def select(self, *cols): return replace(self, cols=cols)\n    def from_(self, t): return replace(self, table=t)\n    def where(self, c): return replace(self, cond=c if self.cond is None else self.cond & c)\n    def order_by(self, *cols): return replace(self, order=cols)\n    def limit(self, n): return replace(self, lim=int(n))\n\n    def build(self):\n        if not self.table:\n            raise ValueError(\"no table\")\n        sql, params = f\"SELECT {', '.join(self.cols)} FROM {self.table}\", []\n        if self.cond:\n            s, params = self.cond.render()\n            sql += f\" WHERE {s}\"\n        if self.order: sql += \" ORDER BY \" + \", \".join(self.order)\n        if self.lim is not None: sql += f\" LIMIT {self.lim}\"\n        return sql, params\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE users (name TEXT, age INT, city TEXT)\")\ndb.executemany(\"INSERT INTO users VALUES (?, ?, ?)\",\n               [(\"ann\", 34, \"Pune\"), (\"bob\", 19, \"Delhi\"), (\"cy\", 45, \"Pune\"), (\"dee\", 28, \"Goa\")])\n\nage, city, name = Col(\"age\"), Col(\"city\"), Col(\"name\")\nbase = Query().select(\"name\", \"age\").from_(\"users\")\nadults_in = base.where(age > 21).order_by(\"age\")\nq1 = adults_in.where(city.in_([\"Pune\", \"Goa\"]))\nq2 = base.where((city == \"Delhi\") | ~(age < 40)).limit(5)\nevil = base.where(name == \"x' OR '1'='1\")\n\nfor q in (q1, q2, evil):\n    sql, params = q.build()\n    print(sql, params, \"->\", db.execute(sql, params).fetchall())\nprint(\"base query untouched:\", base.build())",
            "label": null,
            "output": "SELECT name, age FROM users WHERE (age > ? AND city IN (?, ?)) ORDER BY age [21, 'Pune', 'Goa'] -> [('dee', 28), ('ann', 34), ('cy', 45)]\nSELECT name, age FROM users WHERE (city = ? OR NOT age < ?) LIMIT 5 ['Delhi', 40] -> [('bob', 19), ('cy', 45)]\nSELECT name, age FROM users WHERE name = ? [\"x' OR '1'='1\"] -> []\nbase query untouched: ('SELECT name, age FROM users', [])",
            "isError": false
          },
          {
            "type": "p",
            "html": "The injection attempt returned nothing: the value travelled as a bound parameter, so the database compared <code>name</code> with that literal string. Immutability is why <code>adults_in</code> and <code>q1</code> could both be built from <code>base</code> without either changing it."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Joins add a <code>joins</code> tuple of (table, condition). Dialects (Postgres <code>$1</code> placeholders, MySQL <code>%s</code>) are a rendering strategy. Identifiers (table and column names) cannot be parameters, so they are validated against an allow-list, as <code>Col</code> does here."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why make the builder immutable?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Queries are often built from a shared base (&ldquo;active users&rdquo;) and specialised in different places. With a mutable builder, adding a <code>where</code> in one place silently changes the base for everyone else, a bug that is hard to see. Returning a new object from each method makes every intermediate query a safe, reusable value, at the cost of small copies."
          }
        ]
      },
      {
        "q": "How does parameter binding prevent SQL injection?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The SQL text with placeholders and the values are sent to the database separately; the database parses the text once and treats values strictly as data, never as SQL. A value like <code>x' OR '1'='1</code> is compared as a literal string. Concatenating values into the SQL string lets them change the query's structure, which is the injection."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "plugin-system",
    "title": "Design a Plugin System",
    "group": "Design problems",
    "tags": [
      "Factory",
      "Strategy",
      "Observer"
    ],
    "level": "medium",
    "summary": "Plugins register themselves, declare hooks they handle, are created from config, and are isolated from each other's failures.",
    "intro": [
      "Design the extension mechanism for an application (an editor, a CI system, a data pipeline): third-party plugins add behaviour at defined hook points (on save, before build, transform record) without modifying the core. Which plugins run, and with what settings, comes from configuration."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Plugins self-register under a name. Configuration lists plugins and their options; the core instantiates them. Hooks are named; each plugin implements the hooks it cares about. One failing plugin must not break the others or the core. Plugins run in a defined order."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Create plugin objects from names in a config file",
                "Factory (registry)",
                "Name &rarr; class; plugins register via <code>__init_subclass__</code>"
              ],
              [
                "Each plugin implements a common interface differently",
                "Strategy",
                "Hook methods with a shared signature"
              ],
              [
                "Core announces hook points; plugins react",
                "Observer",
                "A hook call notifies every plugin implementing it"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Plugin</code>",
                "Base class: registry, options, optional hook methods"
              ],
              [
                "<code>PluginManager</code>",
                "Load from config, order by priority, call hooks with isolation"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "class Plugin:\n    registry = {}\n    priority = 100\n\n    def __init_subclass__(cls, name=None, **kw):\n        super().__init_subclass__(**kw)\n        Plugin.registry[name or cls.__name__.lower()] = cls\n\n    def __init__(self, **options): self.options = options\n\nclass TrimWhitespace(Plugin, name=\"trim\"):\n    priority = 10\n    def on_save(self, text): return \"\\n\".join(l.rstrip() for l in text.splitlines())\n\nclass AddHeader(Plugin, name=\"header\"):\n    def on_save(self, text): return f\"# {self.options.get('text', 'generated')}\\n{text}\"\n\nclass WordLimit(Plugin, name=\"limit\"):\n    def on_save(self, text):\n        if len(text.split()) > self.options[\"max\"]:\n            raise ValueError(f\"more than {self.options['max']} words\")\n        return text\n\nclass Stats(Plugin, name=\"stats\"):\n    def on_open(self, text): return f\"{len(text.split())} words\"\n\nclass Broken(Plugin, name=\"broken\"):\n    def on_save(self, text): return text.upper() / 2          # a buggy third-party plugin\n\nclass PluginManager:\n    def __init__(self, config):\n        self.plugins = []\n        for entry in config:\n            cls = Plugin.registry.get(entry[\"name\"])\n            if cls is None:\n                print(f\"  warning: unknown plugin {entry['name']!r} skipped\")\n                continue\n            self.plugins.append(cls(**entry.get(\"options\", {})))\n        self.plugins.sort(key=lambda p: p.priority)\n\n    def pipeline(self, hook, value):\n        \"\"\"each plugin transforms the value; failures are isolated\"\"\"\n        for p in self.plugins:\n            fn = getattr(p, hook, None)\n            if fn is None:\n                continue\n            try:\n                value = fn(value)\n            except Exception as e:\n                print(f\"  plugin {type(p).__name__} failed in {hook}: {e!r}; skipped\")\n        return value\n\n    def collect(self, hook, value):\n        return [r for p in self.plugins if (fn := getattr(p, hook, None)) for r in [fn(value)]]\n\nconfig = [\n    {\"name\": \"header\", \"options\": {\"text\": \"notes\"}},\n    {\"name\": \"trim\"},\n    {\"name\": \"broken\"},\n    {\"name\": \"limit\", \"options\": {\"max\": 6}},\n    {\"name\": \"stats\"},\n    {\"name\": \"spellcheck\"},\n]\npm = PluginManager(config)\nprint([type(p).__name__ for p in pm.plugins])\nprint(repr(pm.pipeline(\"on_save\", \"buy milk   \\ncall bob  \")))\nprint(pm.collect(\"on_open\", \"one two three\"))",
            "label": null,
            "output": "  warning: unknown plugin 'spellcheck' skipped\n['TrimWhitespace', 'AddHeader', 'Broken', 'WordLimit', 'Stats']\n  plugin Broken failed in on_save: TypeError(\"unsupported operand type(s) for /: 'str' and 'int'\"); skipped\n'# notes\\nbuy milk\\ncall bob'\n['3 words']",
            "isError": false
          },
          {
            "type": "p",
            "html": "The broken plugin raised, was reported and skipped, and every other plugin still ran; the unknown <code>spellcheck</code> entry was a warning, not a crash. Priorities put <code>trim</code> before <code>header</code> regardless of the order in the config."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Third-party packages register through entry points (<code>importlib.metadata.entry_points(group=\"myapp.plugins\")</code>), which is how pytest and many CLIs discover plugins without importing them by name. Untrusted plugins need real isolation: a separate process with a timeout, because an exception handler cannot stop a plugin that loops forever or corrupts shared state."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you keep a slow or crashing plugin from taking down the host?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Exceptions: wrap each hook call, log and skip (as above), and disable a plugin after repeated failures. Slowness and hangs: run plugin hooks with a timeout, which in Python really means in a separate process or a worker pool you can abandon, since threads cannot be killed. Resource abuse and security: separate processes with limits, or a sandbox (WASM, containers). Define a narrow API for plugins so they cannot reach into core internals."
          }
        ]
      },
      {
        "q": "Why register plugins with <code>__init_subclass__</code> instead of a manual list?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Defining the class is enough to make it available; there is no second place to forget to update. The core never imports plugins by name, so plugins can live in separate packages. The trade-off is that registration happens at import time, so the plugin module must be imported (directly or via entry points) before the registry is read."
          }
        ]
      }
    ],
    "refs": []
  },
  {
    "id": "drawing-app",
    "title": "Design a Drawing Application",
    "group": "Design problems",
    "tags": [
      "Composite",
      "Prototype",
      "Command",
      "Observer"
    ],
    "level": "hard",
    "summary": "Shapes and groups, duplicate via prototypes, move/resize/delete as undoable commands, canvas listeners.",
    "intro": [
      "Design the model of a vector drawing app (a mini Figma or Excalidraw): users add shapes, group them, duplicate shapes or groups, move and delete them, and undo any action. The canvas view redraws when the model changes."
    ],
    "sections": [
      {
        "title": "Requirements",
        "body": [
          {
            "type": "p",
            "html": "Shapes: rectangle, circle (more later). Groups contain shapes and groups; moving a group moves everything inside. Duplicate creates an independent deep copy with a new id, offset slightly. Every user action is undoable. Bounding boxes work for shapes and groups."
          }
        ]
      },
      {
        "title": "Choosing the patterns",
        "body": [
          {
            "type": "table",
            "head": [
              "Signal in the problem",
              "Pattern",
              "Why it fits"
            ],
            "rows": [
              [
                "Groups contain shapes and other groups",
                "Composite",
                "<code>move</code> and <code>bounds</code> work the same on a shape or a group"
              ],
              [
                "Duplicate an arbitrary configured shape or group",
                "Prototype",
                "<code>clone()</code> deep-copies and assigns fresh ids"
              ],
              [
                "Every action undoable",
                "Command",
                "Add, move, delete as commands on a history stack"
              ],
              [
                "View redraws on changes",
                "Observer",
                "The document notifies listeners after each command"
              ]
            ]
          }
        ]
      },
      {
        "title": "Class design",
        "body": [
          {
            "type": "table",
            "head": [
              "Class",
              "Responsibility"
            ],
            "rows": [
              [
                "<code>Shape</code>, <code>Rect</code>, <code>Circle</code>",
                "Leaves: position, size, <code>move</code>, <code>bounds</code>, <code>clone</code>"
              ],
              [
                "<code>Group</code>",
                "Composite of shapes"
              ],
              [
                "<code>AddCmd</code>, <code>MoveCmd</code>, <code>DeleteCmd</code>",
                "Commands with do/undo"
              ],
              [
                "<code>Document</code>",
                "Top-level items, history, listeners"
              ]
            ]
          }
        ]
      },
      {
        "title": "Implementation",
        "body": [
          {
            "type": "code",
            "src": "import copy\nfrom itertools import count\n\n_ids = count(1)\n\nclass Shape:\n    def __init__(self, x, y): self.id, self.x, self.y = next(_ids), x, y\n    def move(self, dx, dy): self.x += dx; self.y += dy\n    def clone(self, dx=10, dy=10):                     # prototype\n        c = copy.deepcopy(self)\n        c._renumber(); c.move(dx, dy)\n        return c\n    def _renumber(self): self.id = next(_ids)\n\nclass Rect(Shape):\n    def __init__(self, x, y, w, h): super().__init__(x, y); self.w, self.h = w, h\n    def bounds(self): return (self.x, self.y, self.x + self.w, self.y + self.h)\n    def __repr__(self): return f\"Rect#{self.id}@({self.x},{self.y})\"\n\nclass Circle(Shape):\n    def __init__(self, x, y, r): super().__init__(x, y); self.r = r\n    def bounds(self): return (self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r)\n    def __repr__(self): return f\"Circle#{self.id}@({self.x},{self.y})\"\n\nclass Group(Shape):                                    # composite\n    def __init__(self, *children):\n        self.id, self.children = next(_ids), list(children)\n    def move(self, dx, dy):\n        for c in self.children: c.move(dx, dy)\n    def bounds(self):\n        bs = [c.bounds() for c in self.children]\n        return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))\n    def _renumber(self):\n        self.id = next(_ids)\n        for c in self.children: c._renumber()\n    def __repr__(self): return f\"Group#{self.id}{self.children}\"\n\nclass AddCmd:\n    def __init__(self, item): self.item = item\n    def do(self, doc): doc.items.append(self.item)\n    def undo(self, doc): doc.items.remove(self.item)\n\nclass MoveCmd:\n    def __init__(self, item, dx, dy): self.item, self.dx, self.dy = item, dx, dy\n    def do(self, doc): self.item.move(self.dx, self.dy)\n    def undo(self, doc): self.item.move(-self.dx, -self.dy)\n\nclass DeleteCmd:\n    def __init__(self, item): self.item, self.index = item, None\n    def do(self, doc):\n        self.index = doc.items.index(self.item); doc.items.remove(self.item)\n    def undo(self, doc): doc.items.insert(self.index, self.item)\n\nclass Document:\n    def __init__(self): self.items, self.history, self.listeners = [], [], []\n    def run(self, cmd):\n        cmd.do(self); self.history.append(cmd); self._changed(type(cmd).__name__)\n    def undo(self):\n        cmd = self.history.pop(); cmd.undo(self); self._changed(\"undo \" + type(cmd).__name__)\n    def _changed(self, why):\n        for fn in self.listeners: fn(why, self)\n\ndoc = Document()\ndoc.listeners.append(lambda why, d: print(f\"  redraw after {why:16} items={d.items}\"))\nr, c = Rect(0, 0, 40, 20), Circle(60, 10, 10)\ndoc.run(AddCmd(r)); doc.run(AddCmd(c))\ng = Group(r, c)\ndoc.items[:] = [g]                                   # group them (in a real app: a GroupCmd)\ndoc.run(AddCmd(g.clone()))                           # duplicate the whole group\ndoc.run(MoveCmd(g, 5, 5))\nprint(\"group bounds:\", g.bounds(), \"| copy bounds:\", doc.items[1].bounds())\ndoc.run(DeleteCmd(g))\ndoc.undo(); doc.undo()\nprint(\"after two undos, original group back at:\", g.bounds())",
            "label": null,
            "output": "  redraw after AddCmd           items=[Rect#1@(0,0)]\n  redraw after AddCmd           items=[Rect#1@(0,0), Circle#2@(60,10)]\n  redraw after AddCmd           items=[Group#3[Rect#1@(0,0), Circle#2@(60,10)], Group#4[Rect#5@(10,10), Circle#6@(70,20)]]\n  redraw after MoveCmd          items=[Group#3[Rect#1@(5,5), Circle#2@(65,15)], Group#4[Rect#5@(10,10), Circle#6@(70,20)]]\ngroup bounds: (5, 5, 75, 25) | copy bounds: (10, 10, 80, 30)\n  redraw after DeleteCmd        items=[Group#4[Rect#5@(10,10), Circle#6@(70,20)]]\n  redraw after undo DeleteCmd   items=[Group#3[Rect#1@(5,5), Circle#2@(65,15)], Group#4[Rect#5@(10,10), Circle#6@(70,20)]]\n  redraw after undo MoveCmd     items=[Group#3[Rect#1@(0,0), Circle#2@(60,10)], Group#4[Rect#5@(10,10), Circle#6@(70,20)]]\nafter two undos, original group back at: (0, 0, 70, 20)",
            "isError": false
          },
          {
            "type": "p",
            "html": "The duplicate is fully independent: moving the original group did not move the copy, because <code>clone</code> deep-copied every child and gave each a new id. That independence is the point of Prototype here &mdash; shallow copies sharing children would make edits to one appear in the other."
          }
        ]
      },
      {
        "title": "Extending the design",
        "body": [
          {
            "type": "p",
            "html": "Grouping and ungrouping should be commands too (the demo sets <code>items</code> directly to keep it short). Real-time collaboration replaces the local history with operations sent to a server and transformed or merged (CRDTs). Rendering is a visitor over the composite: SVG export, hit-testing and snapping are more visitors."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why does <code>clone</code> need to renumber ids after <code>deepcopy</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>deepcopy</code> copies attribute values, including the id, so the copy would share identity with the original: selection, undo history and collaboration all key on ids and would confuse the two. Renumbering recursively (the group renumbers its children) gives every copied object a fresh identity while keeping all other properties."
          }
        ]
      },
      {
        "q": "A user drags a shape and the app records 200 tiny MoveCmds. How do you fix undo?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Coalesce: while a drag is in progress, update the shape directly (or merge consecutive moves of the same item into one command, as the text editor merges keystrokes), and push a single <code>MoveCmd</code> with the total offset when the mouse is released. One drag becomes one undo step, and history memory stays small."
          }
        ]
      }
    ],
    "refs": []
  }
];
