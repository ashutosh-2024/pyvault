from ._lld import code, table, note, caveat, section, question, PATTERNS_GROUP

TOPIC = dict(
    id="behavioral-core",
    title="Behavioral Patterns I: Strategy, Observer, Command, State, Template Method",
    group=PATTERNS_GROUP,
    summary="The five patterns that solve most LLD problems, each with a class-based and a Pythonic version.",
    intro=[
        "Behavioral patterns are about how responsibilities and algorithms are divided between objects. These five appear in most LLD interview answers: <strong>Strategy</strong> for interchangeable algorithms, <strong>Observer</strong> for reacting to events, <strong>Command</strong> for actions as objects (undo, queues), <strong>State</strong> for behaviour that depends on a lifecycle, and <strong>Template Method</strong> for a fixed skeleton with varying steps.",
    ],
    sections=[
        section(
            "Strategy",
            "Define a family of algorithms behind one interface and let the client pick one at run time. The context (a <code>Checkout</code>, a <code>ParkingLot</code>) holds a strategy and delegates to it; changing behaviour means swapping the object, not editing the context.",
            code('''
                from typing import Protocol

                class PricingStrategy(Protocol):
                    def price(self, hours: float) -> float: ...

                class Hourly:
                    def __init__(self, rate): self.rate = rate
                    def price(self, hours): return round(self.rate * max(1, hours), 2)

                class FlatDaily:
                    def __init__(self, amount): self.amount = amount
                    def price(self, hours): return self.amount * (int(hours // 24) + 1)

                class Tiered:
                    """first 2 h at one rate, then cheaper"""
                    def price(self, hours):
                        first = min(hours, 2) * 40
                        rest = max(0, hours - 2) * 20
                        return round(first + rest, 2)

                class Ticket:
                    def __init__(self, hours, strategy: PricingStrategy):
                        self.hours, self.strategy = hours, strategy
                    def fee(self):
                        return self.strategy.price(self.hours)

                for s in (Hourly(30), FlatDaily(200), Tiered()):
                    print(f"{type(s).__name__:9}", [Ticket(h, s).fee() for h in (0.5, 3, 30)])
            '''),
            "Pythonic form: when a strategy is a single method with no state, a plain function (or a dict of functions keyed by name) is a perfectly good strategy.",
        ),
        section(
            "Observer",
            "A subject keeps a list of subscribers and notifies them when something happens. The subject does not know what subscribers do, so adding a reaction (send an email, update a dashboard, write an audit log) never touches the subject.",
            code('''
                from collections import defaultdict
                from typing import Callable

                class EventBus:
                    def __init__(self):
                        self._subs: dict[str, list[Callable]] = defaultdict(list)

                    def subscribe(self, event, handler):
                        self._subs[event].append(handler)
                        return lambda: self._subs[event].remove(handler)    # unsubscribe handle

                    def publish(self, event, **data):
                        for handler in list(self._subs[event]):
                            try:
                                handler(**data)
                            except Exception as e:                           # one bad observer
                                print(f"  observer failed: {e!r}")           # must not stop the rest

                bus = EventBus()
                bus.subscribe("order_paid", lambda order, amount: print(f"  email: receipt for {order}"))
                stop_sms = bus.subscribe("order_paid", lambda order, amount: print(f"  sms: {order} paid"))
                bus.subscribe("order_paid", lambda order, amount: 1 / 0)
                bus.subscribe("order_paid", lambda order, amount: print(f"  ledger: +{amount}"))

                bus.publish("order_paid", order="A1", amount=499)
                stop_sms()
                print("after unsubscribing sms:")
                bus.publish("order_paid", order="A2", amount=99)
            '''),
            caveat("Synchronous observers run in the publisher's thread and add their latency to it. For slow reactions (email, webhooks), publish to a queue and let workers do the work. And keep a way to unsubscribe, or long-lived subjects keep dead observers alive."),
        ),
        section(
            "Command",
            "Wrap a request as an object with <code>execute()</code> (and often <code>undo()</code>). Commands can be queued, logged, retried, sent to another process, or kept on a history stack for undo/redo &mdash; things you cannot do with a plain method call.",
            code('''
                class Light:
                    def __init__(self): self.level = 0

                class SetLevel:
                    def __init__(self, light, level):
                        self.light, self.level, self.prev = light, level, None
                    def execute(self):
                        self.prev, self.light.level = self.light.level, self.level
                    def undo(self):
                        self.light.level = self.prev

                class Remote:
                    def __init__(self):
                        self.done, self.undone = [], []
                    def run(self, cmd):
                        cmd.execute(); self.done.append(cmd); self.undone.clear()
                    def undo(self):
                        if self.done:
                            cmd = self.done.pop(); cmd.undo(); self.undone.append(cmd)
                    def redo(self):
                        if self.undone:
                            cmd = self.undone.pop(); cmd.execute(); self.done.append(cmd)

                light, remote = Light(), Remote()
                for lvl in (30, 70, 100):
                    remote.run(SetLevel(light, lvl))
                trace = [light.level]
                remote.undo(); trace.append(light.level)
                remote.undo(); trace.append(light.level)
                remote.redo(); trace.append(light.level)
                remote.run(SetLevel(light, 10)); trace.append(light.level)
                remote.redo(); trace.append(light.level)      # redo stack was cleared by the new command
                print(trace)
            '''),
        ),
        section(
            "State",
            "When an object's behaviour depends on its current state and the same method means different things in different states, give each state its own class. The context delegates to its current state object, and states decide the transitions. This replaces the same <code>if state == ...</code> switch repeated in every method.",
            code('''
                class State:
                    def insert_coin(self, m): raise RuntimeError(f"cannot insert coin while {self.name}")
                    def select(self, m, item): raise RuntimeError(f"cannot select while {self.name}")
                    def dispense(self, m): raise RuntimeError(f"cannot dispense while {self.name}")

                class Idle(State):
                    name = "idle"
                    def insert_coin(self, m): m.state = HasCoin()

                class HasCoin(State):
                    name = "has-coin"
                    def select(self, m, item):
                        if m.stock.get(item, 0) == 0:
                            m.state = Idle(); return f"{item} sold out, coin returned"
                        m.selected, m.state = item, Dispensing()
                        return f"selected {item}"

                class Dispensing(State):
                    name = "dispensing"
                    def dispense(self, m):
                        m.stock[m.selected] -= 1
                        m.state = Idle()
                        return f"here is your {m.selected}"

                class Machine:
                    def __init__(self, stock):
                        self.stock, self.state, self.selected = stock, Idle(), None
                    def insert_coin(self): return self.state.insert_coin(self)
                    def select(self, item): return self.state.select(self, item)
                    def dispense(self): return self.state.dispense(self)

                m = Machine({"cola": 1})
                m.insert_coin(); print(m.select("cola"), "|", m.dispense())
                m.insert_coin(); print(m.select("cola"))
                try:
                    m.dispense()
                except RuntimeError as e:
                    print("RuntimeError:", e)
            '''),
            note("State vs Strategy: both delegate to an object. A strategy is chosen by the client and rarely changes; states replace <em>each other</em> as the object moves through its lifecycle, and each state knows its legal next states."),
        ),
        section(
            "Template Method",
            "A base class fixes the skeleton of an algorithm in one method and leaves some steps to subclasses. The order of steps, and invariants like &ldquo;always validate before saving&rdquo;, live in one place.",
            code('''
                from abc import ABC, abstractmethod

                class DataImporter(ABC):
                    def run(self, raw):                          # the template method
                        rows = self.parse(raw)
                        rows = [r for r in rows if self.valid(r)]
                        return self.save(rows)

                    @abstractmethod
                    def parse(self, raw): ...
                    def valid(self, row):                        # hook with a default
                        return bool(row)
                    def save(self, rows):
                        return f"saved {len(rows)} rows: {rows}"

                class CsvImporter(DataImporter):
                    def parse(self, raw):
                        return [line.split(",") for line in raw.strip().splitlines()]

                class JsonImporter(DataImporter):
                    def parse(self, raw):
                        import json
                        return json.loads(raw)
                    def valid(self, row):
                        return "id" in row

                print(CsvImporter().run("1,ann\\n2,bob\\n"))
                print(JsonImporter().run('[{"id": 1}, {"name": "no id"}]'))
            '''),
            "The trade-off: it uses inheritance, so the varying steps are fixed per subclass. If the steps vary independently, pass them in as strategies instead.",
        ),
    ],
    questions=[
        question(
            "You have a 300-line method with a big <code>if order.status == ...</code> block in several methods. Which pattern, and how do you refactor safely?",
            "hard",
            "State. Steps: write characterisation tests for each method in each status; create a state class per status with one method per operation, initially containing the matching branch; make the order delegate to <code>self.state</code>; move transition logic into the states (each sets the next state); delete the switch. Each step is small and the tests stay green. The result: adding a status adds a class, and illegal operations fail in one obvious place.",
        ),
        question(
            "How do you implement undo for operations that cannot be reversed by a simple inverse (e.g. &ldquo;apply filter&rdquo; to an image)?",
            "medium",
            "Two options. Each command stores whatever is needed to undo before executing &mdash; for a destructive operation, a snapshot (Memento) of the affected state, not necessarily the whole document. Or store snapshots at checkpoints and re-execute commands forward from the nearest one (event sourcing style). Snapshots cost memory, so store diffs or compressed regions, and cap the history length.",
        ),
        question(
            "Observer with synchronous callbacks: what can go wrong?",
            "medium",
            "A slow observer slows the publisher; an exception in one observer can stop later ones (catch per observer); an observer that publishes another event can recurse or reorder events; subscribing inside a notification modifies the list being iterated (iterate over a copy); forgotten subscriptions leak memory (provide unsubscribe, or hold weak references). For cross-service or slow work, publish to a queue instead.",
        ),
    ],
    refs=[
        ("Refactoring.Guru: Behavioral patterns", "https://refactoring.guru/design-patterns/behavioral-patterns"),
        ("Python docs: functools.singledispatch (function-level polymorphism)", "https://docs.python.org/3/library/functools.html#functools.singledispatch"),
    ],
)
