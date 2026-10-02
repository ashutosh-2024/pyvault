from ._lld import code, table, note, caveat, section, question, PATTERNS_GROUP

TOPIC = dict(
    id="structural",
    title="Structural Patterns",
    group=PATTERNS_GROUP,
    summary="Adapter, decorator, composite, facade, proxy, flyweight and bridge - how objects are wrapped and assembled.",
    intro=[
        "Structural patterns are about how objects are put together: wrapping one object to change its interface (Adapter) or add behaviour (Decorator, Proxy), treating trees of objects uniformly (Composite), hiding a subsystem behind one entry point (Facade), and sharing state to save memory (Flyweight).",
        "Several of them look alike in code &mdash; a class that holds another object and forwards calls. What distinguishes them is <em>intent</em>, and naming the intent is what the interviewer wants to hear.",
    ],
    sections=[
        section(
            "Adapter: make an incompatible interface fit",
            "Your code expects one interface; a third-party SDK or legacy class offers another. An adapter implements your interface by translating calls to theirs, so the rest of your code never sees the foreign API.",
            code('''
                from typing import Protocol

                class PaymentGateway(Protocol):                 # what our checkout expects
                    def pay(self, amount_rupees: float, ref: str) -> bool: ...

                class StripeSDK:                                 # third party: cents, dicts, exceptions
                    def create_charge(self, amount_cents, currency, metadata):
                        if amount_cents <= 0:
                            raise ValueError("invalid amount")
                        return {"status": "succeeded", "id": "ch_1", "meta": metadata}

                class StripeAdapter:
                    def __init__(self, sdk: StripeSDK):
                        self.sdk = sdk
                    def pay(self, amount_rupees, ref):
                        try:
                            r = self.sdk.create_charge(round(amount_rupees * 100), "inr", {"ref": ref})
                        except ValueError:
                            return False
                        return r["status"] == "succeeded"

                def checkout(gateway: PaymentGateway, total):
                    return "paid" if gateway.pay(total, "order-42") else "declined"

                print(checkout(StripeAdapter(StripeSDK()), 499.5), checkout(StripeAdapter(StripeSDK()), 0))
            '''),
        ),
        section(
            "Decorator: add behaviour by wrapping",
            "A decorator implements the same interface as the object it wraps and adds something before or after delegating. Decorators stack, so features combine freely at run time without a subclass for every combination. (Python's <code>@decorator</code> syntax applies the same idea to functions.)",
            code('''
                from typing import Protocol

                class DataSource(Protocol):
                    def write(self, data: str) -> str: ...

                class FileSource:
                    def write(self, data): return data

                class Compressed:
                    def __init__(self, inner: DataSource): self.inner = inner
                    def write(self, data): return self.inner.write(f"zip({data})")

                class Encrypted:
                    def __init__(self, inner: DataSource): self.inner = inner
                    def write(self, data): return self.inner.write(f"aes({data})")

                class Logged:
                    def __init__(self, inner: DataSource): self.inner = inner
                    def write(self, data):
                        out = self.inner.write(data)
                        print(f"  wrote {len(out)} chars")
                        return out

                print(FileSource().write("salary.csv"))
                print(Logged(Encrypted(Compressed(FileSource()))).write("salary.csv"))
                print(Compressed(Encrypted(FileSource())).write("salary.csv"))   # order matters
            '''),
            note("Decorator vs inheritance: three optional features would need 2<sup>3</sup> = 8 subclasses to cover every combination; with decorators it is three wrappers chosen at run time."),
        ),
        section(
            "Composite: trees of parts and wholes",
            "When things nest &mdash; folders in folders, menu items in menus, employees under managers, sub-expressions in expressions &mdash; give leaves and containers the same interface. Client code calls one method on the root and the recursion happens inside the structure.",
            code('''
                from abc import ABC, abstractmethod

                class Node(ABC):
                    def __init__(self, name): self.name = name
                    @abstractmethod
                    def size(self) -> int: ...
                    def show(self, indent=0):
                        print("  " * indent + f"{self.name} ({self.size()} B)")

                class File(Node):
                    def __init__(self, name, size):
                        super().__init__(name); self._size = size
                    def size(self): return self._size

                class Folder(Node):
                    def __init__(self, name, *children):
                        super().__init__(name); self.children = list(children)
                    def size(self): return sum(c.size() for c in self.children)
                    def show(self, indent=0):
                        super().show(indent)
                        for c in self.children:
                            c.show(indent + 1)

                root = Folder("root", File("a.txt", 120),
                              Folder("src", File("main.py", 800), File("util.py", 300)),
                              Folder("empty"))
                root.show()
            '''),
        ),
        section(
            "Facade: one simple door into a subsystem",
            "A facade offers a small, task-oriented API over a set of classes with complicated interactions. Clients call <code>place_order()</code> instead of coordinating inventory, payment, shipping and notification themselves. It does not hide the subsystem from those who need it; it just gives everyone else an easy path.",
            code('''
                class Inventory:
                    def __init__(self):
                        self.stock = {"lamp": 2}
                    def reserve(self, item):
                        if self.stock.get(item, 0) == 0:
                            raise LookupError(f"{item} out of stock")
                        self.stock[item] -= 1
                    def release(self, item):
                        self.stock[item] += 1

                class Payments:
                    def charge(self, user, amount): return amount < 1000

                class Shipping:
                    def schedule(self, user, item): return f"ship {item} to {user}"

                class OrderFacade:
                    def __init__(self):
                        self.inv, self.pay, self.ship = Inventory(), Payments(), Shipping()

                    def place_order(self, user, item, price):
                        self.inv.reserve(item)
                        if not self.pay.charge(user, price):
                            self.inv.release(item)                # compensate
                            return "payment failed"
                        return self.ship.schedule(user, item)

                shop = OrderFacade()
                print(shop.place_order("ann", "lamp", 40))
                print(shop.place_order("bob", "lamp", 5000), "| lamps left:", shop.inv.stock["lamp"])
            '''),
        ),
        section(
            "Proxy: stand in front of the real object",
            "A proxy has the same interface as the real object and controls access to it: <strong>virtual proxy</strong> (create the expensive object lazily), <strong>caching proxy</strong> (remember results), <strong>protection proxy</strong> (check permissions), <strong>remote proxy</strong> (the object lives on another machine). Same shape as a decorator; the intent is access control rather than adding features.",
            code('''
                class ReportService:
                    def __init__(self):
                        print("  (expensive) connecting to warehouse")
                    def revenue(self, month):
                        return {"jan": 120, "feb": 95}[month]

                class ReportProxy:
                    def __init__(self, user_role):
                        self.role, self._real, self._cache = user_role, None, {}

                    def revenue(self, month):
                        if self.role != "finance":                # protection
                            raise PermissionError("finance only")
                        if month not in self._cache:              # caching
                            if self._real is None:                # virtual: lazy creation
                                self._real = ReportService()
                            self._cache[month] = self._real.revenue(month)
                        return self._cache[month]

                p = ReportProxy("finance")
                print("proxy created, nothing connected yet")
                print(p.revenue("jan"), p.revenue("jan"), p.revenue("feb"))
                try:
                    ReportProxy("intern").revenue("jan")
                except PermissionError as e:
                    print("PermissionError:", e)
            '''),
        ),
        section(
            "Flyweight and Bridge",
            "<strong>Flyweight</strong> shares the immutable, common part of many objects (the <em>intrinsic</em> state) and keeps only the varying part per object (the <em>extrinsic</em> state). A forest of a million trees stores three tree <em>types</em> (mesh, texture) and a million (x, y, type) tuples.",
            code('''
                import sys
                from functools import cache

                class TreeType:                                   # intrinsic, shared
                    def __init__(self, species, texture):
                        self.species, self.texture = species, texture

                @cache
                def tree_type(species):
                    return TreeType(species, texture=f"{species}.png" * 1000)   # big shared data

                forest = [(x, x * 2 % 97, tree_type(["oak", "pine", "birch"][x % 3])) for x in range(100_000)]
                types = {id(t) for _, _, t in forest}
                print("trees:", len(forest), "| distinct TreeType objects:", len(types))
                print("texture bytes stored once each:", sys.getsizeof(forest[0][2].texture))
            '''),
            "<strong>Bridge</strong> splits one class hierarchy that varies in two independent ways into two hierarchies joined by composition: <code>Shape</code> &times; <code>Renderer</code>, <code>Notification</code> (alert, reminder) &times; <code>Channel</code> (email, SMS). It is composition over inheritance, named.",
        ),
        section(
            "Telling the wrappers apart",
            table(
                ["Pattern", "Same interface as wrapped?", "Intent"],
                [
                    ["Adapter", "No: converts to a <em>different</em> interface", "Make incompatible things work together"],
                    ["Decorator", "Yes", "Add responsibilities, stackable"],
                    ["Proxy", "Yes", "Control access: lazy, cache, permissions, remote"],
                    ["Facade", "No: a new, simpler interface over many objects", "Simplify a subsystem"],
                    ["Composite", "Yes, for leaves and containers", "Treat a tree uniformly"],
                ],
            ),
        ),
    ],
    questions=[
        question(
            "Decorator and Proxy have the same structure. How do you explain the difference?",
            "medium",
            "Intent and who decides. A decorator adds behaviour, and the client composes the stack it wants (<code>Logged(Encrypted(source))</code>), often several deep. A proxy controls access to one real subject, usually transparently &mdash; the client may not know it has a proxy &mdash; and it often manages the subject's lifecycle (creating it lazily, connecting remotely). Caching, lazy loading and permission checks are proxy jobs; compression, logging and retries layered by choice are decorator jobs.",
        ),
        question(
            "How would you add retry and timing behaviour to every call of an existing API client without editing it?",
            "medium",
            "Wrap it in decorators that implement the same interface: a <code>Retrying</code> wrapper that re-invokes the inner client on transient errors with backoff, and a <code>Timed</code> wrapper that records latency. Compose them where the client is constructed. For a client with many methods, a generic wrapper using <code>__getattr__</code> can apply the behaviour to every method call.",
            code('''
                import time

                class Flaky:
                    def __init__(self): self.calls = 0
                    def fetch(self, key):
                        self.calls += 1
                        if self.calls < 3:
                            raise ConnectionError("reset")
                        return f"value-{key}"

                class Retrying:
                    def __init__(self, inner, attempts=4):
                        self.inner, self.attempts = inner, attempts
                    def __getattr__(self, name):
                        method = getattr(self.inner, name)
                        def wrapped(*a, **kw):
                            for i in range(self.attempts):
                                try:
                                    return method(*a, **kw)
                                except ConnectionError:
                                    time.sleep(0.001 * 2 ** i)
                            raise ConnectionError("gave up")
                        return wrapped

                client = Retrying(Flaky())
                print(client.fetch("a"), "after", client.inner.calls, "calls")
            '''),
        ),
        question(
            "Where does the Composite pattern show up in systems you have used?",
            "medium",
            "File systems (files and directories), GUI toolkits (widgets containing widgets; a layout's size is computed from its children), the DOM, organisation charts, abstract syntax trees (an expression node contains sub-expressions), bill-of-materials systems (a product made of parts made of parts), and permission groups that contain users and other groups. Each time, a single operation &mdash; size, render, evaluate, cost, expand members &mdash; recurses through the tree via one interface.",
        ),
    ],
    refs=[
        ("Refactoring.Guru: Structural patterns", "https://refactoring.guru/design-patterns/structural-patterns"),
        ("python-patterns.guide: The Decorator pattern", "https://python-patterns.guide/gang-of-four/decorator-pattern/"),
    ],
)
