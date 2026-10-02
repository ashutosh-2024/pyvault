from ._lld import code, table, note, caveat, question, problem

PARKING_LOT = problem(
    id="parking-lot",
    title="Design a Parking Lot",
    level="medium",
    patterns=["Strategy", "Factory", "Singleton"],
    summary="Multi-floor lot, vehicle and spot types, pluggable spot allocation and pricing, tickets and payment.",
    statement=[
        "Design the software for a multi-floor parking garage. Vehicles of different sizes arrive at an entry gate, get a ticket for a suitable spot, and pay on exit according to a pricing policy. The garage owner wants to change how spots are chosen and how parking is priced without rewriting the system.",
    ],
    requirements=[
        "<strong>In scope:</strong> floors with spots of three sizes (small, medium, large); vehicles (motorcycle, car, bus) that fit a spot of their size or larger; issue a ticket on entry, compute the fee on exit, free the spot; report free spots per floor; pluggable spot-allocation and pricing rules.",
        "<strong>Out of scope:</strong> reservations, payment processing details, multiple garages. Stating this keeps the design focused.",
    ],
    choose=[
        ["&ldquo;Owner wants to change how spots are chosen&rdquo;", "Strategy (allocation)", "Nearest-first, fill-lowest-floor, spread-load are interchangeable algorithms"],
        ["&ldquo;&hellip;and how parking is priced&rdquo;", "Strategy (pricing)", "Hourly, flat, peak-hour pricing vary independently of allocation"],
        ["Vehicle types created from input at the gate", "Factory", "The gate creates the right vehicle from a type string"],
        ["One garage, shared by all gates", "Singleton (or one injected instance)", "All gates must see the same spot state"],
    ],
    choose_notes=[
        "Vehicle sizes are data, not behaviour: an <code>Enum</code> with an ordering (small &lt; medium &lt; large) is enough, so the &ldquo;fits&rdquo; rule is one comparison instead of a class hierarchy.",
    ],
    classes=[
        ["<code>Size</code> (Enum)", "Ordered spot/vehicle sizes"],
        ["<code>Vehicle</code>", "Plate and size; created by <code>Vehicle.of(kind, plate)</code>"],
        ["<code>Spot</code>", "Id, floor, size, current vehicle"],
        ["<code>Ticket</code>", "Vehicle, spot, entry time"],
        ["<code>AllocationStrategy</code>", "Choose a free spot for a vehicle"],
        ["<code>PricingStrategy</code>", "Fee from entry and exit times"],
        ["<code>ParkingLot</code>", "Facade: <code>park</code>, <code>leave</code>, <code>availability</code>; owns spots and active tickets"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass, field
            from enum import IntEnum
            from itertools import count
            from typing import Protocol
            import math

            class Size(IntEnum):
                SMALL = 1
                MEDIUM = 2
                LARGE = 3

            @dataclass(frozen=True)
            class Vehicle:
                plate: str
                size: Size
                KINDS = {"motorcycle": Size.SMALL, "car": Size.MEDIUM, "bus": Size.LARGE}

                @classmethod
                def of(cls, kind, plate):                       # factory
                    return cls(plate, cls.KINDS[kind])

            @dataclass
            class Spot:
                id: str
                floor: int
                size: Size
                vehicle: Vehicle | None = None

                def fits(self, v): return self.vehicle is None and self.size >= v.size

            @dataclass
            class Ticket:
                id: int
                vehicle: Vehicle
                spot: Spot
                entry: float

            class AllocationStrategy(Protocol):
                def choose(self, spots: list[Spot], v: Vehicle) -> Spot | None: ...

            class LowestFloorBestFit:
                """smallest spot that fits, on the lowest floor"""
                def choose(self, spots, v):
                    free = [s for s in spots if s.fits(v)]
                    return min(free, key=lambda s: (s.floor, s.size), default=None)

            class PricingStrategy(Protocol):
                def fee(self, ticket: Ticket, exit_time: float) -> float: ...

            class HourlyBySize:
                RATES = {Size.SMALL: 10, Size.MEDIUM: 20, Size.LARGE: 50}
                def fee(self, t, exit_time):
                    hours = max(1, math.ceil((exit_time - t.entry) / 3600))
                    return hours * self.RATES[t.spot.size]

            class ParkingLot:
                def __init__(self, floors, layout, allocator, pricing):
                    self.spots = [Spot(f"F{f}-{i}", f, size)
                                  for f in range(floors) for i, size in enumerate(layout)]
                    self.allocator, self.pricing = allocator, pricing
                    self.active: dict[str, Ticket] = {}
                    self._ids = count(1)

                def park(self, v: Vehicle, now: float) -> Ticket:
                    if v.plate in self.active:
                        raise ValueError(f"{v.plate} is already parked")
                    spot = self.allocator.choose(self.spots, v)
                    if spot is None:
                        raise LookupError(f"no spot for {v.plate} ({v.size.name})")
                    spot.vehicle = v
                    t = Ticket(next(self._ids), v, spot, now)
                    self.active[v.plate] = t
                    return t

                def leave(self, plate: str, now: float) -> float:
                    t = self.active.pop(plate)
                    t.spot.vehicle = None
                    return self.pricing.fee(t, now)

                def availability(self):
                    out = {}
                    for s in self.spots:
                        if s.vehicle is None:
                            key = (s.floor, s.size.name)
                            out[key] = out.get(key, 0) + 1
                    return out

            lot = ParkingLot(floors=2, layout=[Size.SMALL, Size.MEDIUM, Size.MEDIUM, Size.LARGE],
                             allocator=LowestFloorBestFit(), pricing=HourlyBySize())
            arrivals = [("car", "KA-1"), ("motorcycle", "KA-2"), ("bus", "KA-3"), ("car", "KA-4"),
                        ("motorcycle", "KA-5"), ("bus", "KA-6"), ("bus", "KA-7")]
            for kind, plate in arrivals:
                try:
                    t = lot.park(Vehicle.of(kind, plate), now=0)
                    print(f"{kind:10} {plate} -> {t.spot.id} ({t.spot.size.name})")
                except LookupError as e:
                    print("LookupError:", e)
            print("fee for KA-1 after 2.5 h:", lot.leave("KA-1", now=2.5 * 3600))
            print("free:", lot.availability())
        '''),
        "Best fit kept the small spot for the first motorcycle and the large spot for the bus instead of handing them to cars. Floor 0 was full after four vehicles, so the second motorcycle went to the small spot on floor 1. When KA-7 arrived both large spots were taken, and a bus cannot use a smaller spot.",
    ],
    extend=[
        "&ldquo;Add peak-hour pricing&rdquo; and &ldquo;spread cars across floors&rdquo; are each one new strategy class; <code>ParkingLot</code> does not change.",
        code('''
            import math

            class PeakHourPricing:
                """wraps another pricing strategy: 1.5x if the stay overlaps 17:00-20:00"""
                def __init__(self, base, multiplier=1.5):
                    self.base, self.multiplier = base, multiplier
                def fee(self, t, exit_time):
                    base = self.base.fee(t, exit_time)
                    peak = any(17 <= (h % 24) < 20 for h in range(int(t.entry // 3600), math.ceil(exit_time / 3600)))
                    return base * self.multiplier if peak else base

            class FakeTicket:
                def __init__(self, entry): self.entry = entry

            class Flat:
                def fee(self, t, exit_time): return 100

            p = PeakHourPricing(Flat())
            print(p.fee(FakeTicket(10 * 3600), 12 * 3600), p.fee(FakeTicket(16 * 3600), 18 * 3600))
        '''),
        "Other likely follow-ups: EV spots (a spot attribute plus an allocation rule), multiple entry gates (all gates share one <code>ParkingLot</code>; <code>park</code> needs a lock so two gates never assign the same spot), and a display board (an observer notified on park and leave).",
    ],
    questions=[
        question(
            "Two entry gates call <code>park()</code> at the same moment. What can go wrong and how do you fix it?",
            "medium",
            "Both can pick the same free spot before either marks it occupied. Make choose-and-assign atomic: a lock around <code>park</code> (simple, fine for one process), or per-floor locks for more parallelism. In a distributed setup the spot assignment must be a conditional write in the database (<code>UPDATE spots SET vehicle=? WHERE id=? AND vehicle IS NULL</code>) and the gate retries with another spot if zero rows changed.",
        ),
        question(
            "Why model vehicle types as an Enum rather than subclasses?",
            "medium",
            "They differ only in data (size), not behaviour. Subclasses would add classes with no methods of their own. If vehicle types later gained real behaviour (an EV needs charging, a bus needs two spots), introduce a hierarchy or a capability then. Design for the variation you can see.",
        ),
    ],
)


ELEVATOR = problem(
    id="elevator",
    title="Design an Elevator System",
    level="hard",
    patterns=["State", "Strategy", "Command"],
    summary="Several cars, hall and cabin requests, direction states, a pluggable dispatching algorithm, step-based simulation.",
    statement=[
        "Design the controller for a building with N elevators. People press up/down buttons on floors (hall calls) and floor buttons inside a car (cabin calls). The controller decides which car serves each hall call, and each car moves floor by floor, stopping where it has requests.",
    ],
    requirements=[
        "<strong>In scope:</strong> multiple cars; hall calls with direction; cabin calls; each car keeps serving in its current direction while it has stops ahead (the SCAN/elevator algorithm); a dispatcher assigns hall calls to cars; a step-by-step simulation so behaviour is testable.",
        "<strong>Out of scope:</strong> door timing, weight limits, emergency modes (mention them as extensions).",
    ],
    choose=[
        ["A car behaves differently when idle, moving up or moving down", "State", "The next stop and what &ldquo;step&rdquo; means depend on direction"],
        ["&ldquo;Which car should take this call?&rdquo; has several reasonable answers", "Strategy (dispatcher)", "Nearest car, least busy, zoning can be swapped"],
        ["Button presses are requests to be queued and processed", "Command", "Requests are objects that can be queued, logged and replayed in tests"],
    ],
    classes=[
        ["<code>Direction</code> (Enum)", "UP, DOWN, IDLE"],
        ["<code>Request</code>", "Floor and optional direction (a hall or cabin call)"],
        ["<code>Car</code>", "Current floor, direction, set of stops; <code>step()</code> moves one floor"],
        ["<code>Dispatcher</code>", "Strategy: pick a car for a hall call"],
        ["<code>Controller</code>", "Accepts requests, routes them, advances the simulation"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass, field
            from enum import Enum

            class Direction(Enum):
                UP = 1
                DOWN = -1
                IDLE = 0

            @dataclass
            class Car:
                id: int
                floor: int = 0
                direction: Direction = Direction.IDLE
                stops: set = field(default_factory=set)
                log: list = field(default_factory=list)

                def add_stop(self, floor):
                    if floor != self.floor or self.direction is not Direction.IDLE:
                        self.stops.add(floor)

                def step(self):
                    """one tick: open doors here, or move one floor (SCAN)"""
                    if self.floor in self.stops:
                        self.stops.discard(self.floor)
                        self.log.append(f"stop@{self.floor}")
                    if not self.stops:
                        self.direction = Direction.IDLE
                        return
                    ahead = [s for s in self.stops
                             if (s - self.floor) * self.direction.value > 0] if self.direction is not Direction.IDLE else []
                    if not ahead:                                   # reverse (or start moving)
                        nearest = min(self.stops, key=lambda s: abs(s - self.floor))
                        self.direction = Direction.UP if nearest > self.floor else Direction.DOWN
                    self.floor += self.direction.value

                def cost(self, floor, direction):
                    """rough distance if this car takes a hall call"""
                    d = abs(self.floor - floor)
                    if self.direction is Direction.IDLE:
                        return d
                    moving_toward = (floor - self.floor) * self.direction.value >= 0
                    if moving_toward and direction is self.direction:
                        return d                                      # on the way
                    return d + 2 * len(self.stops) + 10               # must finish its sweep first

            class NearestCarDispatcher:
                def pick(self, cars, floor, direction):
                    return min(cars, key=lambda c: (c.cost(floor, direction), c.id))

            class Controller:
                def __init__(self, n_cars, dispatcher):
                    self.cars = [Car(i) for i in range(n_cars)]
                    self.dispatcher = dispatcher

                def hall_call(self, floor, direction):
                    car = self.dispatcher.pick(self.cars, floor, direction)
                    car.add_stop(floor)
                    return car.id

                def cabin_call(self, car_id, floor):
                    self.cars[car_id].add_stop(floor)

                def tick(self, n=1):
                    for _ in range(n):
                        for c in self.cars:
                            c.step()

            ctl = Controller(2, NearestCarDispatcher())
            ctl.cars[1].floor = 10                                # car 1 parked at the top
            print("hall call 3 UP  -> car", ctl.hall_call(3, Direction.UP))
            print("hall call 9 DOWN-> car", ctl.hall_call(9, Direction.DOWN))
            ctl.tick(3)
            ctl.cabin_call(0, 7)                                  # passenger at 3 presses 7
            ctl.cabin_call(1, 1)
            ctl.tick(12)
            for c in ctl.cars:
                print(f"car {c.id}: floor {c.floor}, {c.direction.name}, served {c.log}")
        '''),
        "Each car sweeps in one direction while it has stops ahead and only then reverses, which bounds how long any request waits &mdash; the same reason disk schedulers use SCAN instead of always serving the nearest request.",
    ],
    extend=[
        "A smarter dispatcher (estimate time including stops, or zone cars to floor ranges during morning rush) is a new strategy class. Door handling and maintenance mode fit as extra <code>Car</code> states. Making requests explicit command objects lets you log every button press and replay a day of traffic against two dispatchers to compare average wait time &mdash; the honest way to choose between them.",
    ],
    questions=[
        question(
            "Why not always send the nearest idle car?",
            "medium",
            "Nearest-first ignores direction and existing load: a car three floors away moving the other way with five stops queued may take minutes to arrive, while a car eight floors away already heading toward the caller arrives sooner. It can also starve distant floors. Cost functions that account for direction and pending stops, or simulation-based estimates of arrival time, give better average and worst-case waits.",
        ),
        question(
            "How would you test an elevator controller?",
            "medium",
            "Make time discrete (<code>tick()</code>) and the dispatcher injectable, as above, so tests are deterministic: feed a script of requests at given ticks and assert on stop order, final positions and that every request is served within a bound. Add property-based tests: no car ever moves past the top or bottom floor, every requested floor is eventually visited, a car never reverses while it has stops ahead.",
        ),
    ],
)


VENDING_MACHINE = problem(
    id="vending-machine",
    title="Design a Vending Machine",
    level="easy",
    patterns=["State"],
    summary="Coins, selection, dispensing and change, with every illegal action rejected by the current state.",
    statement=[
        "Design a vending machine that accepts coins, lets the user select a product, dispenses it with change, and lets the user cancel to get their money back. An operator can restock products and coins.",
    ],
    requirements=[
        "Accept coins of fixed denominations; show balance; select a product by code; dispense if paid enough and in stock; return change using the coins in the machine; cancel returns the inserted coins. Reject operations that make no sense in the current state (selecting with no money, inserting coins while dispensing).",
    ],
    choose=[
        ["Same buttons do different things depending on what has happened so far", "State", "Each state class handles only the actions legal in that state"],
        ["Change must be made from limited coins", "Greedy with a check (or DP)", "An algorithm detail, not a pattern; refuse the sale if change cannot be made"],
    ],
    classes=[
        ["<code>VendingMachine</code>", "Context: inventory, coin box, inserted amount, current state"],
        ["<code>Idle</code>, <code>HasMoney</code>", "States; each implements <code>insert</code>, <code>select</code>, <code>cancel</code>"],
        ["<code>make_change</code>", "Compute change from available coins, or report it is impossible"],
    ],
    implementation=[
        code('''
            from collections import Counter

            def make_change(amount, coins: Counter):
                """greedy over available coins; None if exact change is impossible"""
                out = Counter()
                for coin in sorted(coins, reverse=True):
                    take = min(amount // coin, coins[coin])
                    if take:
                        out[coin] = take
                        amount -= take * coin
                return out if amount == 0 else None

            class State:
                def insert(self, m, coin): raise RuntimeError(f"cannot insert in {type(self).__name__}")
                def select(self, m, code): raise RuntimeError(f"cannot select in {type(self).__name__}")
                def cancel(self, m): raise RuntimeError(f"nothing to cancel in {type(self).__name__}")

            class Idle(State):
                def insert(self, m, coin):
                    m.accept(coin)
                    m.state = HasMoney()

            class HasMoney(State):
                def insert(self, m, coin):
                    m.accept(coin)

                def select(self, m, code):
                    name, price, qty = m.products[code]
                    if qty == 0:
                        return f"{name} is sold out"
                    if m.balance < price:
                        return f"insert {price - m.balance} more for {name}"
                    change = make_change(m.balance - price, m.coins)
                    if change is None:
                        return "cannot make change, use exact amount"
                    m.coins -= change
                    m.products[code] = (name, price, qty - 1)
                    m.balance, m.inserted = 0, Counter()
                    m.state = Idle()
                    return f"dispensed {name}, change {dict(change) or 0}"

                def cancel(self, m):
                    refund = m.inserted
                    m.coins -= refund
                    m.balance, m.inserted = 0, Counter()
                    m.state = Idle()
                    return f"refunded {dict(refund)}"

            class VendingMachine:
                COINS = {1, 2, 5, 10}

                def __init__(self, products, coins):
                    self.products, self.coins = products, Counter(coins)
                    self.balance, self.inserted, self.state = 0, Counter(), Idle()

                def accept(self, coin):
                    if coin not in self.COINS:
                        raise ValueError(f"coin {coin} rejected")
                    self.balance += coin
                    self.inserted[coin] += 1
                    self.coins[coin] += 1

                def insert(self, coin): return self.state.insert(self, coin)
                def select(self, code): return self.state.select(self, code)
                def cancel(self): return self.state.cancel(self)

            vm = VendingMachine({"A1": ("chips", 15, 2), "B1": ("cola", 25, 0)}, {1: 3, 2: 2, 5: 1})
            try:
                vm.select("A1")
            except RuntimeError as e:
                print("RuntimeError:", e)
            vm.insert(10)
            print(vm.select("A1"))
            vm.insert(10)
            print(vm.select("A1"))
            vm.insert(10); vm.insert(5); vm.insert(10)
            print(vm.select("B1"))
            print(vm.cancel())
        '''),
    ],
    extend=[
        "A <code>Maintenance</code> state for restocking (rejects customers, accepts <code>restock</code>), card payments (a new payment input that also moves Idle to HasMoney), and a sold-out display (an observer on inventory) all slot in without changing existing states.",
    ],
    questions=[
        question(
            "Greedy change-making can fail even when change is possible. When, and what would you do?",
            "hard",
            "Greedy is optimal for canonical coin systems like 1/2/5/10, but with arbitrary denominations or limited coin counts it can fail: owing 6 with coins {5: 1, 3: 2} greedy takes 5 and is stuck, while 3+3 works. Use a bounded-knapsack DP over the available coins when the coin set is not canonical or stock is low; it is tiny for vending-machine amounts.",
        ),
        question(
            "Why is the State pattern better here than an <code>if state == ...</code> switch?",
            "medium",
            "Every operation (insert, select, cancel, restock, refund) would need its own switch over every state, and adding a state means editing all of them. With state classes, the legal actions of each state are listed in one place, illegal ones fail by default in the base class, and adding a state is a new class.",
        ),
    ],
)


ATM = problem(
    id="atm",
    title="Design an ATM",
    level="medium",
    patterns=["State", "Chain of Responsibility", "Facade"],
    summary="Card and PIN session states, withdrawals dispensed through a chain of note handlers, bank behind a facade.",
    statement=[
        "Design an ATM that reads a card, verifies the PIN with the bank (three attempts), lets the user check balance or withdraw cash, and dispenses notes from its cassettes. The bank's systems are external.",
    ],
    requirements=[
        "Session flow: insert card &rarr; enter PIN (lock card after 3 failures) &rarr; choose transaction &rarr; eject card. Withdrawals must be multiples the machine can dispense with the notes it has; the account is debited only if dispensing is possible.",
    ],
    choose=[
        ["Card inserted, authenticated, card ejected: actions allowed differ by step", "State", "Session states guard the flow"],
        ["Dispense using 2000s, then 500s, then 100s", "Chain of Responsibility", "Each cassette handles what it can and passes the remainder on"],
        ["The ATM talks to a complex bank system", "Facade", "One narrow <code>BankService</code> interface: verify PIN, balance, debit"],
    ],
    classes=[
        ["<code>BankService</code>", "Facade over the bank: <code>verify</code>, <code>balance</code>, <code>debit</code>"],
        ["<code>Cassette</code>", "A note denomination and count; link in the dispensing chain"],
        ["<code>ATM</code>", "Session context with the current state"],
        ["<code>NoCard</code>, <code>CardInserted</code>, <code>Authenticated</code>", "Session states"],
    ],
    implementation=[
        code('''
            class BankService:
                def __init__(self):
                    self.accounts = {"4111": {"pin": "1234", "balance": 12_000}}
                def verify(self, card, pin): return self.accounts[card]["pin"] == pin
                def balance(self, card): return self.accounts[card]["balance"]
                def debit(self, card, amount):
                    acct = self.accounts[card]
                    if acct["balance"] < amount:
                        raise ValueError("insufficient funds")
                    acct["balance"] -= amount

            class Cassette:
                def __init__(self, note, count, next_=None):
                    self.note, self.count, self.next = note, count, next_

                def plan(self, amount):
                    """returns [(note, n), ...] or raises; does not change counts"""
                    n = min(amount // self.note, self.count)
                    rest = amount - n * self.note
                    tail = self.next.plan(rest) if rest and self.next else []
                    if rest and not self.next:
                        raise ValueError(f"cannot dispense {rest}")
                    return ([(self.note, n)] if n else []) + tail

                def take(self, plan):
                    for note, n in plan:
                        c = self
                        while c.note != note:
                            c = c.next
                        c.count -= n

            class State:
                def __init__(self, atm): self.atm = atm
                def insert(self, card): return "card already inside"
                def pin(self, pin): return "insert a card first"
                def withdraw(self, amount): return "not authenticated"
                def eject(self): return "no card"

            class NoCard(State):
                def insert(self, card):
                    self.atm.card, self.atm.tries = card, 0
                    self.atm.state = CardInserted(self.atm)
                    return "enter PIN"

            class CardInserted(State):
                def pin(self, pin):
                    if self.atm.bank.verify(self.atm.card, pin):
                        self.atm.state = Authenticated(self.atm)
                        return "PIN ok"
                    self.atm.tries += 1
                    if self.atm.tries >= 3:
                        self.atm.state = NoCard(self.atm)
                        return "card retained"
                    return f"wrong PIN, {3 - self.atm.tries} tries left"
                def eject(self):
                    self.atm.state = NoCard(self.atm); return "card ejected"

            class Authenticated(State):
                def withdraw(self, amount):
                    try:
                        plan = self.atm.cash.plan(amount)          # can we dispense?
                        self.atm.bank.debit(self.atm.card, amount)  # then debit
                    except ValueError as e:
                        return f"declined: {e}"
                    self.atm.cash.take(plan)
                    return f"dispensed {plan}"
                def eject(self):
                    self.atm.state = NoCard(self.atm); return "card ejected"

            class ATM:
                def __init__(self, bank, cash):
                    self.bank, self.cash, self.card, self.tries = bank, cash, None, 0
                    self.state = NoCard(self)
                def __getattr__(self, action):                    # forward actions to the state
                    return getattr(self.state, action)

            atm = ATM(BankService(), Cassette(2000, 2, Cassette(500, 4, Cassette(100, 10))))
            for step in [("withdraw", 100), ("insert", "4111"), ("pin", "0000"), ("pin", "1234"),
                         ("withdraw", 5600), ("withdraw", 5650), ("withdraw", 9000), ("eject",)]:
                print(f"{step[0]:8} {str(step[1:]):10} -> {getattr(atm, step[0])(*step[1:])}")
            print("bank balance:", atm.bank.balance("4111"))
        '''),
        "Note the order in <code>withdraw</code>: plan the notes first, debit second, take the notes last. Debiting before checking the cassettes would take money for cash the machine cannot give.",
    ],
    extend=[
        "Deposits, mini-statements and PIN change are new methods on <code>Authenticated</code>. Real ATMs also need a <em>reversal</em>: if the debit succeeded but the dispenser jams, the ATM sends a compensating credit to the bank. That is a saga step, logged durably before dispensing.",
    ],
    questions=[
        question(
            "The bank debit succeeded but the cash dispenser failed. How should the system recover?",
            "hard",
            "Record a durable journal entry before each step (debit requested, debit confirmed, dispense started, dispense confirmed). On dispenser failure, send a reversal (credit) to the bank with the same transaction id, so it is idempotent if retried. If the ATM crashes mid-way, on restart it reads the journal and either completes the reversal or reconciles with the bank. Physical counts in the cassettes are reconciled at the next cash refill.",
        ),
        question(
            "Why use Chain of Responsibility for dispensing instead of one function?",
            "medium",
            "A single greedy function is fine for a fixed set of denominations. The chain makes each cassette an independent object with its own count and lets the machine's configuration (which cassettes exist, in what order) be assembled at start-up. A cassette that is empty or faulty is simply skipped. Either answer is acceptable if you explain the trade-off.",
        ),
    ],
)


LIBRARY = problem(
    id="library",
    title="Design a Library Management System",
    level="medium",
    patterns=["Observer", "Strategy", "Repository"],
    summary="Books vs copies, loans with limits and due dates, reservations notified on return, pluggable fines.",
    statement=[
        "Design a library system. Members borrow and return physical copies of books, can reserve a title that is fully on loan, and are notified when a reserved title comes back. Late returns are fined.",
    ],
    requirements=[
        "A book (title) has many copies. A member may hold at most 3 loans. Loans last 14 days. If all copies of a title are out, a member can join a FIFO reservation queue; when a copy is returned, it is held for the first person in the queue and they are notified. Fines are computed by a policy that may change.",
    ],
    choose=[
        ["&ldquo;Notify the member when the book comes back&rdquo;", "Observer", "Returning a copy publishes an event; notification channels subscribe"],
        ["Fine rules change (per-day, capped, waived for students)", "Strategy", "Fine policy is injected"],
        ["Look up copies, members and loans by id", "Repository", "Keeps storage details out of the domain logic (in-memory here)"],
    ],
    classes=[
        ["<code>Book</code>, <code>Copy</code>", "A title and its physical copies (barcode, status)"],
        ["<code>Member</code>", "Id, name, current loans"],
        ["<code>Loan</code>", "Copy, member, due date, returned date"],
        ["<code>FinePolicy</code>", "Strategy: fine for a late loan"],
        ["<code>Library</code>", "Facade: <code>borrow</code>, <code>give_back</code>, <code>reserve</code>; publishes events"],
    ],
    implementation=[
        code('''
            from collections import defaultdict, deque
            from dataclasses import dataclass, field

            @dataclass
            class Copy:
                barcode: str
                isbn: str
                status: str = "available"          # available | on_loan | on_hold
                held_for: str | None = None

            @dataclass
            class Loan:
                copy: Copy
                member: str
                due: int
                returned: int | None = None

            class PerDayCapped:
                def __init__(self, per_day=5, cap=100): self.per_day, self.cap = per_day, cap
                def fine(self, loan): return min(self.cap, max(0, loan.returned - loan.due) * self.per_day)

            class Library:
                MAX_LOANS, LOAN_DAYS = 3, 14

                def __init__(self, fine_policy):
                    self.copies: dict[str, Copy] = {}
                    self.titles: dict[str, str] = {}
                    self.loans: dict[str, Loan] = {}                 # barcode -> active loan
                    self.queue: dict[str, deque] = defaultdict(deque) # isbn -> members waiting
                    self.listeners = []
                    self.fines = fine_policy

                def add(self, isbn, title, *barcodes):
                    self.titles[isbn] = title
                    for b in barcodes:
                        self.copies[b] = Copy(b, isbn)

                def on_event(self, fn): self.listeners.append(fn)
                def _emit(self, *args): [fn(*args) for fn in self.listeners]

                def borrow(self, member, isbn, today):
                    if sum(l.member == member for l in self.loans.values()) >= self.MAX_LOANS:
                        raise PermissionError(f"{member} has {self.MAX_LOANS} loans")
                    copy = next((c for c in self.copies.values() if c.isbn == isbn and
                                 (c.status == "available" or c.held_for == member)), None)
                    if copy is None:
                        raise LookupError(f"no copy of {self.titles[isbn]!r} free; reserve it")
                    if member in self.queue[isbn]:
                        self.queue[isbn].remove(member)
                    copy.status, copy.held_for = "on_loan", None
                    self.loans[copy.barcode] = Loan(copy, member, today + self.LOAN_DAYS)
                    return copy.barcode

                def reserve(self, member, isbn):
                    self.queue[isbn].append(member)

                def give_back(self, barcode, today):
                    loan = self.loans.pop(barcode)
                    loan.returned = today
                    copy = loan.copy
                    if self.queue[copy.isbn]:
                        nxt = self.queue[copy.isbn][0]
                        copy.status, copy.held_for = "on_hold", nxt
                        self._emit("hold_ready", nxt, self.titles[copy.isbn])
                    else:
                        copy.status = "available"
                    return self.fines.fine(loan)

            lib = Library(PerDayCapped())
            lib.on_event(lambda event, who, title: print(f"  notify {who}: {title!r} is waiting for you"))
            lib.add("978-0", "Dune", "D1")
            lib.add("978-1", "Emma", "E1", "E2")

            b = lib.borrow("ann", "978-0", today=0)
            try:
                lib.borrow("bob", "978-0", today=1)
            except LookupError as e:
                print("LookupError:", e)
            lib.reserve("bob", "978-0")
            print("ann's fine:", lib.give_back(b, today=20))
            try:
                lib.borrow("cy", "978-0", today=21)
            except LookupError as e:
                print("cy:", e)
            print("bob borrows:", lib.borrow("bob", "978-0", today=21))
        '''),
    ],
    extend=[
        "Email and SMS notifications are listeners added at start-up. A student fine waiver is a different <code>FinePolicy</code>, or a decorator around one. Holds that expire after 3 days need a scheduled job that releases the hold to the next member in the queue.",
    ],
    questions=[
        question(
            "Why separate <code>Book</code> (title) from <code>Copy</code>?",
            "medium",
            "Different identities and lifecycles. Catalogue data (title, author, ISBN) is shared by all copies; status, barcode, condition and loans belong to each physical copy. Reservations are on the title (any copy will do), loans are on a copy. Merging them forces duplicated catalogue data or breaks as soon as the library buys a second copy.",
        ),
        question(
            "How would you prevent two librarians lending the last copy to two people at once?",
            "medium",
            "The status change from available to on_loan must be atomic. In one process, a lock around borrow; with a database, a conditional update (<code>UPDATE copies SET status='on_loan' WHERE barcode=? AND status='available'</code>) and check the row count, or a unique constraint on active loans per copy.",
        ),
    ],
)

PROBLEMS = [PARKING_LOT, ELEVATOR, VENDING_MACHINE, ATM, LIBRARY]
