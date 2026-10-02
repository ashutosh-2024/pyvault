from ._lld import code, table, note, caveat, question, problem

MOVIE_BOOKING = problem(
    id="movie-booking",
    title="Design a Movie Ticket Booking System",
    level="hard",
    patterns=["State", "Strategy", "Observer"],
    summary="Shows and seats, temporary seat holds with expiry, concurrent booking without double-selling, pricing strategies.",
    statement=[
        "Design the booking core of a BookMyShow-style app. Users pick a show, select seats, and have a few minutes to pay. Seats being paid for must not be sold to anyone else, and seats from abandoned checkouts must become available again.",
    ],
    requirements=[
        "Cities, cinemas, screens and movies are catalogue data; the core is a <code>Show</code> (movie, screen, time) with a seat map. Booking flow: hold selected seats (all or nothing) for 5 minutes &rarr; pay &rarr; confirm, or let the hold expire. Many users book the same show concurrently. Price depends on seat category and may include dynamic rules (weekend, demand).",
    ],
    choose=[
        ["Seat is available, held, or booked; holds expire", "State (per seat)", "Legal transitions: available &rarr; held &rarr; booked, held &rarr; available on expiry"],
        ["Many users select seats at once", "Lock / atomic check-and-set", "Concurrency control, not a GoF pattern, but the heart of the problem"],
        ["Weekend and demand-based pricing", "Strategy", "Pricing rules vary and stack"],
        ["Send confirmation, update analytics on booking", "Observer", "Side effects decoupled from booking"],
    ],
    classes=[
        ["<code>Seat</code>", "Id, category, state, hold owner and expiry"],
        ["<code>Show</code>", "Seat map plus a lock; <code>hold</code>, <code>confirm</code>, <code>release_expired</code>"],
        ["<code>PricingRule</code>", "Strategy: adjust a base price"],
        ["<code>BookingService</code>", "Orchestrates hold, price, payment, confirm; emits events"],
    ],
    implementation=[
        code('''
            import threading
            from dataclasses import dataclass

            HOLD_SECONDS = 300

            @dataclass
            class Seat:
                id: str
                category: str
                state: str = "available"       # available | held | booked
                holder: str | None = None
                expires: float = 0.0

            class Show:
                def __init__(self, seats):
                    self.seats = {s.id: s for s in seats}
                    self.lock = threading.Lock()

                def _free(self, seat, now):
                    return seat.state == "available" or (seat.state == "held" and seat.expires <= now)

                def hold(self, user, ids, now):
                    with self.lock:                                 # all-or-nothing, atomically
                        seats = [self.seats[i] for i in ids]
                        if not all(self._free(s, now) for s in seats):
                            return False
                        for s in seats:
                            s.state, s.holder, s.expires = "held", user, now + HOLD_SECONDS
                        return True

                def confirm(self, user, ids, now):
                    with self.lock:
                        seats = [self.seats[i] for i in ids]
                        if not all(s.state == "held" and s.holder == user and s.expires > now for s in seats):
                            return False                            # hold lost or expired
                        for s in seats:
                            s.state = "booked"
                        return True

            BASE = {"regular": 200, "premium": 350}

            class WeekendSurcharge:
                def apply(self, price, ctx): return price * 1.2 if ctx["weekend"] else price

            class DemandSurge:
                def apply(self, price, ctx): return price * 1.25 if ctx["occupancy"] > 0.8 else price

            class BookingService:
                def __init__(self, rules, listeners=()):
                    self.rules, self.listeners = rules, list(listeners)

                def quote(self, show, ids, ctx):
                    total = 0
                    for i in ids:
                        p = BASE[show.seats[i].category]
                        for r in self.rules:
                            p = r.apply(p, ctx)
                        total += p
                    return round(total)

                def book(self, show, user, ids, ctx, pay, now):
                    if not show.hold(user, ids, now):
                        return f"{user}: seats {ids} not available"
                    amount = self.quote(show, ids, ctx)
                    if not pay(user, amount):
                        return f"{user}: payment failed, hold will expire"
                    if not show.confirm(user, ids, now + 60):
                        return f"{user}: hold expired before payment"
                    for fn in self.listeners:
                        fn(user, ids, amount)
                    return f"{user}: booked {ids} for {amount}"

            show = Show([Seat(f"A{i}", "premium") for i in range(1, 4)] + [Seat(f"B{i}", "regular") for i in range(1, 5)])
            svc = BookingService([WeekendSurcharge(), DemandSurge()],
                                 [lambda u, ids, amt: print(f"  email to {u}: tickets {ids}")])
            ctx = {"weekend": True, "occupancy": 0.5}

            # 20 users race for the same two seats
            results, start = [], threading.Barrier(20)
            def attempt(i):
                start.wait()
                results.append(show.hold(f"user{i}", ["A1", "A2"], now=0))
            threads = [threading.Thread(target=attempt, args=(i,)) for i in range(20)]
            for t in threads: t.start()
            for t in threads: t.join()
            print("holds granted for A1+A2:", results.count(True), "of", len(results))

            print(svc.book(show, "ann", ["B1", "B2"], ctx, pay=lambda u, a: True, now=0))
            print(svc.book(show, "bob", ["B2", "B3"], ctx, pay=lambda u, a: True, now=0))
            print(svc.book(show, "cy", ["B3"], ctx, pay=lambda u, a: False, now=0))
            print(svc.book(show, "dee", ["B3"], ctx, pay=lambda u, a: True, now=HOLD_SECONDS + 1))
        '''),
        "Exactly one of the twenty racing users got the two seats. Cy's failed payment left B3 held, but the hold expired, so Dee could book it five minutes later without any cleanup job running &mdash; expiry is checked lazily whenever a seat is examined.",
    ],
    extend=[
        "In a multi-server deployment the lock moves into the data store: a conditional update per seat (<code>WHERE state='available' OR expires &lt; now</code>) inside a transaction, or Redis <code>SET seat:show:A1 user NX EX 300</code> for holds. Payment callbacks carry the hold id so a late callback for an expired hold is refunded rather than confirmed.",
    ],
    questions=[
        question(
            "How do you stop two users from buying the same seat when you have 20 app servers?",
            "hard",
            "Make the state change atomic in the shared store. With SQL: in one transaction, <code>UPDATE seats SET state='held', holder=?, expires=? WHERE show_id=? AND seat_id IN (...) AND (state='available' OR (state='held' AND expires &lt; now()))</code>, and commit only if the row count equals the number of seats requested; otherwise roll back. A unique index on (show, seat) for confirmed bookings is the last line of defence. With Redis, <code>SET NX EX</code> per seat (or a Lua script for all-or-nothing). Never check availability in one request and write in another without a condition.",
        ),
        question(
            "Why hold seats with an expiry instead of locking them until payment completes?",
            "medium",
            "Users abandon checkouts constantly. A lock without a timeout would leave seats stuck forever when a browser closes. An expiring hold bounds how long a seat can be blocked, needs no cleanup job (expiry is checked when the seat is read), and the confirm step re-checks that the hold is still valid before marking the seat booked.",
        ),
    ],
)


HOTEL_BOOKING = problem(
    id="hotel-booking",
    title="Design a Hotel Reservation System",
    level="medium",
    patterns=["Strategy", "Repository", "Factory"],
    summary="Room types, availability over date ranges, overlap checks, room assignment and cancellation policies.",
    statement=[
        "Design the reservation core for a hotel: guests search for a room type over a date range, book it, and may cancel under a policy. Rooms are assigned at booking time.",
    ],
    requirements=[
        "Rooms have a type (single, double, suite) and a nightly rate. A booking covers check-in to check-out (check-out day is free for the next guest). Search returns room types with at least one free room for the whole range. Cancellation refunds depend on the policy attached to the booking (flexible, moderate, non-refundable).",
    ],
    choose=[
        ["Availability over date ranges", "Interval overlap check", "Two stays overlap iff <code>a.start &lt; b.end and b.start &lt; a.end</code>"],
        ["Which free room of the type to assign", "Strategy", "Lowest floor, same room as last visit, spread wear"],
        ["Different cancellation rules per rate plan", "Strategy", "The policy object travels with the booking"],
        ["Bookings stored and queried by room", "Repository", "Domain code asks for &ldquo;bookings of room 101&rdquo;, not SQL"],
    ],
    classes=[
        ["<code>Room</code>", "Number, type, nightly rate"],
        ["<code>Booking</code>", "Room, guest, check-in, check-out, policy, status"],
        ["<code>BookingRepository</code>", "Bookings by room; overlap queries"],
        ["<code>CancellationPolicy</code>", "Strategy: refund for a cancellation date"],
        ["<code>Hotel</code>", "Facade: <code>search</code>, <code>book</code>, <code>cancel</code>"],
    ],
    implementation=[
        code('''
            from collections import defaultdict
            from dataclasses import dataclass
            from datetime import date, timedelta

            @dataclass(frozen=True)
            class Room:
                number: int
                type: str
                rate: int

            @dataclass
            class Booking:
                id: int
                room: Room
                guest: str
                check_in: date
                check_out: date
                policy: object
                status: str = "confirmed"

                def nights(self): return (self.check_out - self.check_in).days
                def overlaps(self, start, end): return self.check_in < end and start < self.check_out

            class Flexible:
                def refund(self, b, today):
                    return 1.0 if (b.check_in - today).days >= 1 else 0.0

            class Moderate:
                def refund(self, b, today):
                    days = (b.check_in - today).days
                    return 1.0 if days >= 7 else 0.5 if days >= 2 else 0.0

            class NonRefundable:
                def refund(self, b, today): return 0.0

            class BookingRepository:
                def __init__(self): self.by_room = defaultdict(list)
                def add(self, b): self.by_room[b.room.number].append(b)
                def is_free(self, room, start, end):
                    return not any(b.status == "confirmed" and b.overlaps(start, end)
                                   for b in self.by_room[room.number])

            class Hotel:
                def __init__(self, rooms, repo):
                    self.rooms, self.repo, self.next_id = rooms, repo, 1

                def free_rooms(self, room_type, start, end):
                    return [r for r in self.rooms if r.type == room_type and self.repo.is_free(r, start, end)]

                def search(self, start, end):
                    types = sorted({r.type for r in self.rooms})
                    return {t: len(self.free_rooms(t, start, end)) for t in types}

                def book(self, guest, room_type, start, end, policy):
                    if end <= start:
                        raise ValueError("check-out must be after check-in")
                    free = self.free_rooms(room_type, start, end)
                    if not free:
                        raise LookupError(f"no {room_type} free {start}..{end}")
                    room = min(free, key=lambda r: r.number)        # assignment strategy
                    b = Booking(self.next_id, room, guest, start, end, policy)
                    self.next_id += 1
                    self.repo.add(b)
                    return b

                def cancel(self, b, today):
                    b.status = "cancelled"
                    return round(b.nights() * b.room.rate * b.policy.refund(b, today))

            d = lambda day: date(2026, 12, day)
            hotel = Hotel([Room(101, "double", 120), Room(102, "double", 120), Room(201, "suite", 300)],
                          BookingRepository())
            b1 = hotel.book("ann", "double", d(20), d(23), Moderate())
            b2 = hotel.book("bob", "double", d(22), d(24), Flexible())
            print("rooms:", b1.room.number, b2.room.number)
            print("search 22-23:", hotel.search(d(22), d(23)))
            print("search 23-25:", hotel.search(d(23), d(25)), "(ann checks out on the 23rd)")
            try:
                hotel.book("cy", "double", d(21), d(23), NonRefundable())
            except LookupError as e:
                print("LookupError:", e)
            print("ann cancels 10 days early, refund:", hotel.cancel(b1, d(10)))
            print("now cy can book:", hotel.book("cy", "double", d(21), d(23), NonRefundable()).room.number)
        '''),
    ],
    extend=[
        "Overbooking (sell 102% of rooms and rely on cancellations) is a different availability strategy. Rate plans with seasonal prices replace <code>Room.rate</code> with a pricing strategy over dates. At scale, availability is precomputed per (room type, night) as a counter decremented atomically on booking, rather than scanning bookings.",
    ],
    questions=[
        question(
            "Why is the overlap condition <code>a.start &lt; b.end and b.start &lt; a.end</code>, and why half-open ranges?",
            "medium",
            "Two intervals fail to overlap only if one ends before the other starts; negating that gives the condition. Using half-open ranges [check-in, check-out) means a guest checking out on the 23rd and another checking in on the 23rd do not conflict, which matches how hotels work, and the arithmetic needs no &plusmn;1 corrections.",
        ),
        question(
            "How would you make availability search fast for a hotel chain with millions of bookings?",
            "hard",
            "Store an inventory table keyed by (hotel, room type, night) with the count of rooms still sellable. Search for a range is a range read of N rows and a min; booking decrements every night in the range in one transaction with a <code>WHERE available &gt; 0</code> guard. Specific room assignment can happen later, at check-in. This is how large booking systems separate &ldquo;can I sell it&rdquo; from &ldquo;which physical room&rdquo;.",
        ),
    ],
)


MEETING_ROOMS = problem(
    id="meeting-room-scheduler",
    title="Design a Meeting Room Scheduler",
    level="medium",
    patterns=["Strategy", "Observer"],
    summary="Rooms with capacity, conflict-free booking over time slots, room selection strategy, invite notifications.",
    statement=[
        "Design a scheduler that books meeting rooms for a time slot and a number of attendees, picks a suitable room, and notifies invitees. It should also answer &ldquo;which rooms are free from 2 to 3 pm?&rdquo;.",
    ],
    requirements=[
        "Rooms have a name and capacity. A booking needs a slot [start, end) and attendee count; it must not overlap another booking of the same room. Choose the smallest room that fits (so big rooms stay free), but allow other strategies. Invitees are notified on booking and cancellation.",
    ],
    choose=[
        ["&ldquo;Pick a suitable room&rdquo; with a preference that may change", "Strategy", "Best-fit, nearest to the organiser, preferred floor"],
        ["Notify invitees", "Observer", "Calendar, email and chat integrations subscribe"],
        ["No overlapping bookings per room", "Sorted intervals + bisect", "O(log n) conflict check per room"],
    ],
    classes=[
        ["<code>Room</code>", "Name, capacity, sorted list of bookings"],
        ["<code>RoomSelector</code>", "Strategy: choose among free rooms"],
        ["<code>Scheduler</code>", "<code>book</code>, <code>cancel</code>, <code>free_rooms</code>; notifies listeners"],
    ],
    implementation=[
        code('''
            import bisect
            from dataclasses import dataclass, field

            @dataclass
            class Room:
                name: str
                capacity: int
                slots: list = field(default_factory=list)      # sorted [(start, end, title)]

                def is_free(self, start, end):
                    i = bisect.bisect_left(self.slots, (start,))
                    before_ok = i == 0 or self.slots[i - 1][1] <= start
                    after_ok = i == len(self.slots) or end <= self.slots[i][0]
                    return before_ok and after_ok

                def add(self, start, end, title):
                    bisect.insort(self.slots, (start, end, title))

            class BestFit:
                def choose(self, rooms, people):
                    return min(rooms, key=lambda r: (r.capacity, r.name), default=None)

            class Scheduler:
                def __init__(self, rooms, selector):
                    self.rooms, self.selector, self.listeners = rooms, selector, []

                def free_rooms(self, start, end, people=1):
                    return [r for r in self.rooms if r.capacity >= people and r.is_free(start, end)]

                def book(self, title, start, end, invitees):
                    room = self.selector.choose(self.free_rooms(start, end, len(invitees)), len(invitees))
                    if room is None:
                        raise LookupError(f"no room for {len(invitees)} people {start}-{end}")
                    room.add(start, end, title)
                    for fn in self.listeners:
                        fn(invitees, f"{title} in {room.name} {start}-{end}")
                    return room.name

            sched = Scheduler([Room("Pod", 4), Room("Board", 12), Room("Cave", 6)], BestFit())
            sched.listeners.append(lambda who, msg: print(f"  invite {len(who)} people: {msg}"))

            print(sched.book("standup", 900, 915, ["a", "b", "c"]))
            print(sched.book("design review", 900, 1000, ["a", "b", "c", "d", "e"]))
            print(sched.book("1:1", 910, 930, ["a", "b"]))
            print(sched.book("all hands", 1000, 1100, list("abcdefghij")))
            print("free 9:20-9:40 for 2:", [r.name for r in sched.free_rooms(920, 940, 2)])
            try:
                sched.book("offsite", 1030, 1130, list("abcdefghij"))
            except LookupError as e:
                print("LookupError:", e)
        '''),
        "The 1:1 at 9:10 could not use the Pod (taken by the standup until 9:15) or the Cave (design review), so best fit gave it the Board room &mdash; the only free room left. A smarter strategy might suggest moving it by five minutes instead; that is exactly the kind of change a selector strategy absorbs.",
    ],
    extend=[
        "Recurring meetings expand into individual slots (or store a recurrence rule and check overlaps against its expansion). &ldquo;Find a time when all invitees are free&rdquo; merges their busy intervals and scans the gaps &mdash; the Merge Intervals problem.",
    ],
    questions=[
        question(
            "How do you check for conflicts efficiently when a room has thousands of bookings?",
            "medium",
            "Keep each room's bookings sorted by start time. A new slot [s, e) conflicts only with its neighbours in that order: the booking just before it (must end by s) and the booking just after it (must start at or after e). <code>bisect</code> finds the position in O(log n). A balanced tree or interval tree does the same with O(log n) inserts; a database does it with an index on (room, start) and a range query.",
        ),
        question(
            "How would you find the earliest slot where five specific people and a room are all free?",
            "hard",
            "Collect busy intervals of all five people and merge them (sort by start, merge overlaps). The gaps between merged intervals within working hours are times when everyone is free. For each gap long enough for the meeting, check rooms with sufficient capacity for a free sub-slot, earliest first. The cost is dominated by the sort, O(k log k) for k busy intervals.",
        ),
    ],
)


SPLITWISE = problem(
    id="splitwise",
    title="Design Splitwise (Expense Sharing)",
    level="medium",
    patterns=["Strategy", "Factory"],
    summary="Groups and expenses, equal/exact/percentage splits, per-person balances, and simplifying debts to few payments.",
    statement=[
        "Design an expense-sharing app. Users add expenses paid by one person and split among several, in different ways. The app shows who owes whom and suggests the fewest payments needed to settle up.",
    ],
    requirements=[
        "Split types: equal, exact amounts, percentages (must total 100%). Amounts are money: use integer paise/cents to avoid floating-point drift, and distribute rounding remainders deterministically. Show net balance per user and a simplified settlement plan.",
    ],
    choose=[
        ["&ldquo;Split equally, by exact amounts, or by percentage&rdquo;", "Strategy", "Each split type turns (amount, participants, params) into shares"],
        ["Create the right split from a type name in the request", "Factory", "Map <code>\"equal\"</code>, <code>\"exact\"</code>, <code>\"percent\"</code> to strategies"],
        ["Settle up with fewest transfers", "Greedy on net balances", "Match largest debtor with largest creditor"],
    ],
    classes=[
        ["<code>SplitStrategy</code>", "<code>shares(total, people, params)</code> &rarr; dict of person to amount"],
        ["<code>Expense</code>", "Payer, total, shares"],
        ["<code>Ledger</code>", "Net balance per person; <code>settle()</code> produces transfers"],
    ],
    implementation=[
        code('''
            import heapq
            from collections import defaultdict

            class Equal:
                def shares(self, total, people, params=None):
                    base, extra = divmod(total, len(people))
                    return {p: base + (1 if i < extra else 0) for i, p in enumerate(people)}

            class Exact:
                def shares(self, total, people, params):
                    if sum(params.values()) != total:
                        raise ValueError(f"exact shares add up to {sum(params.values())}, not {total}")
                    return dict(params)

            class Percent:
                def shares(self, total, people, params):
                    if sum(params.values()) != 100:
                        raise ValueError("percentages must add up to 100")
                    raw = {p: total * pct // 100 for p, pct in params.items()}
                    leftover = total - sum(raw.values())
                    for p in sorted(params, key=lambda p: -params[p])[:leftover]:
                        raw[p] += 1                                  # hand out rounding cents
                    return raw

            SPLITS = {"equal": Equal(), "exact": Exact(), "percent": Percent()}   # factory

            class Ledger:
                def __init__(self):
                    self.net = defaultdict(int)                     # >0: is owed, <0: owes

                def add_expense(self, payer, total, people, kind="equal", params=None):
                    shares = SPLITS[kind].shares(total, people, params)
                    assert sum(shares.values()) == total
                    self.net[payer] += total
                    for p, amt in shares.items():
                        self.net[p] -= amt

                def settle(self):
                    creditors = [(-v, p) for p, v in self.net.items() if v > 0]
                    debtors = [(v, p) for p, v in self.net.items() if v < 0]
                    heapq.heapify(creditors); heapq.heapify(debtors)
                    transfers = []
                    while creditors and debtors:
                        c_amt, c = heapq.heappop(creditors)
                        d_amt, d = heapq.heappop(debtors)
                        pay = min(-c_amt, -d_amt)
                        transfers.append(f"{d} pays {c} {pay / 100:.2f}")
                        if -c_amt > pay: heapq.heappush(creditors, (c_amt + pay, c))
                        if -d_amt > pay: heapq.heappush(debtors, (d_amt + pay, d))
                    return transfers

            L = Ledger()
            L.add_expense("ann", 100_00, ["ann", "bob", "cy"])                       # 100.00 equally
            L.add_expense("bob", 60_00, ["bob", "cy"], "exact", {"bob": 10_00, "cy": 50_00})
            L.add_expense("cy", 90_00, ["ann", "bob", "cy", "dee"], "percent",
                          {"ann": 25, "bob": 25, "cy": 25, "dee": 25})
            print({p: f"{v / 100:+.2f}" for p, v in sorted(L.net.items())})
            print("sum of balances:", sum(L.net.values()))
            for t in L.settle():
                print(" ", t)
            try:
                L.add_expense("ann", 10_00, ["ann", "bob"], "percent", {"ann": 60, "bob": 30})
            except ValueError as e:
                print("ValueError:", e)
        '''),
        "Balances always sum to zero, which is a cheap invariant to assert in tests. The greedy settlement produces at most n &minus; 1 transfers for n people with non-zero balances; finding the true minimum is NP-hard in general, and the greedy answer is what Splitwise-style apps use.",
    ],
    extend=[
        "A new split type (by shares: &ldquo;ann 2 parts, bob 1 part&rdquo;) is one strategy class plus one factory entry. Multiple currencies need a currency on each expense and conversion at settle time. Groups become a ledger per group plus a cross-group view.",
    ],
    questions=[
        question(
            "Why store money as integer cents, and how do you split 100.00 three ways?",
            "medium",
            "Binary floating point cannot represent most decimal fractions, so sums drift (<code>0.1 + 0.2 != 0.3</code>) and balances stop summing to zero. Integers are exact. 10000 cents / 3 = 3333 remainder 1, so one person (chosen deterministically, e.g. the first) gets 3334. <code>decimal.Decimal</code> with explicit rounding is the alternative when you need fractional units.",
        ),
        question(
            "How does debt simplification work, and is it optimal?",
            "hard",
            "Compute each person's net balance (paid minus owed); individual expenses no longer matter. Repeatedly match the largest creditor with the largest debtor and transfer the smaller of the two amounts; one of them reaches zero each time, so there are at most n &minus; 1 transfers. The true minimum can be lower when some subset of balances sums to zero (it can be settled independently), and finding the maximum number of such zero-sum subsets is NP-hard, so apps use the greedy method.",
        ),
    ],
)


RIDE_SHARING = problem(
    id="ride-sharing",
    title="Design a Ride-Sharing Service (Uber)",
    level="hard",
    patterns=["Strategy", "State", "Observer"],
    summary="Driver matching strategies, the trip lifecycle as a state machine, fare strategies with surge, rider notifications.",
    statement=[
        "Design the core objects of a ride-hailing app: riders request rides, the system matches a nearby available driver, the trip goes through its lifecycle, and the fare is computed at the end.",
    ],
    requirements=[
        "Drivers have a location, vehicle type and availability. A ride request has pickup, drop-off and vehicle type. Matching picks an available driver (nearest, or best rated nearby, or one that minimises total wait). Trip states: requested &rarr; driver assigned &rarr; arrived &rarr; in progress &rarr; completed, with cancellation allowed before pickup. Fare = base + per km + per minute, times surge. Riders and drivers are notified at each transition.",
    ],
    choose=[
        ["Matching policy changes and is A/B tested", "Strategy", "Nearest driver vs rating-weighted vs batch matching"],
        ["Trip moves through a lifecycle; some actions only valid in some states", "State (transition table)", "A table of legal transitions guards every change"],
        ["Fare rules: base, time, distance, surge, promos", "Strategy (+ Decorator for promos)", "Fare components vary by city and product"],
        ["Rider and driver apps update on each transition", "Observer", "Push notifications subscribe to trip events"],
    ],
    classes=[
        ["<code>Driver</code>", "Id, location, vehicle, rating, available"],
        ["<code>Trip</code>", "Rider, driver, state; <code>transition(to)</code> validates against the table"],
        ["<code>Matcher</code>", "Strategy: pick a driver for a request"],
        ["<code>FareCalculator</code>", "Strategy: fare from distance, duration, surge"],
        ["<code>Dispatch</code>", "Request &rarr; match &rarr; create trip; notifies observers"],
    ],
    implementation=[
        code('''
            import math
            from dataclasses import dataclass, field

            @dataclass
            class Driver:
                id: str
                x: float
                y: float
                vehicle: str
                rating: float
                available: bool = True

            TRANSITIONS = {
                "requested": {"assigned", "cancelled"},
                "assigned": {"arrived", "cancelled"},
                "arrived": {"in_progress", "cancelled"},
                "in_progress": {"completed"},
                "completed": set(), "cancelled": set(),
            }

            @dataclass
            class Trip:
                rider: str
                driver: Driver | None = None
                state: str = "requested"
                listeners: list = field(default_factory=list)

                def transition(self, to):
                    if to not in TRANSITIONS[self.state]:
                        raise ValueError(f"illegal transition {self.state} -> {to}")
                    self.state = to
                    if to in ("completed", "cancelled") and self.driver:
                        self.driver.available = True
                    for fn in self.listeners:
                        fn(self, to)

            def dist(d, x, y): return math.hypot(d.x - x, d.y - y)

            class Nearest:
                def pick(self, drivers, x, y):
                    return min(drivers, key=lambda d: dist(d, x, y), default=None)

            class RatedWithinRadius:
                def __init__(self, radius): self.radius = radius
                def pick(self, drivers, x, y):
                    near = [d for d in drivers if dist(d, x, y) <= self.radius]
                    return max(near, key=lambda d: (d.rating, -dist(d, x, y)), default=None)

            class StandardFare:
                def __init__(self, base, per_km, per_min): self.base, self.km, self.min = base, per_km, per_min
                def fare(self, km, minutes, surge=1.0):
                    return round((self.base + self.km * km + self.min * minutes) * surge)

            class Dispatch:
                def __init__(self, drivers, matcher):
                    self.drivers, self.matcher = drivers, matcher

                def request(self, rider, x, y, vehicle, listeners=()):
                    trip = Trip(rider, listeners=list(listeners))
                    pool = [d for d in self.drivers if d.available and d.vehicle == vehicle]
                    driver = self.matcher.pick(pool, x, y)
                    if driver is None:
                        trip.transition("cancelled")
                        return trip
                    driver.available = False
                    trip.driver = driver
                    trip.transition("assigned")
                    return trip

            drivers = [Driver("d1", 0, 1, "sedan", 4.2), Driver("d2", 2, 2, "sedan", 4.9),
                       Driver("d3", 0.5, 0, "auto", 4.7)]
            notify = lambda trip, state: print(f"  [{trip.rider}] trip is now {state}"
                                               + (f" (driver {trip.driver.id})" if trip.driver else ""))

            for matcher in (Nearest(), RatedWithinRadius(3)):
                for d in drivers: d.available = True
                print(type(matcher).__name__, "->", Dispatch(drivers, matcher).request("ann", 0, 0, "sedan").driver.id)

            dispatch = Dispatch(drivers, Nearest())
            for d in drivers: d.available = True
            trip = dispatch.request("bob", 0, 0, "sedan", [notify])
            for step in ("arrived", "in_progress", "completed"):
                trip.transition(step)
            print("fare:", StandardFare(50, 12, 2).fare(km=8.5, minutes=22, surge=1.4))
            try:
                trip.transition("cancelled")
            except ValueError as e:
                print("ValueError:", e)
            print("cy asks for a bike, none on the road:", dispatch.request("cy", 0, 0, "bike").state)
        '''),
    ],
    extend=[
        "Real matching is not one rider at a time: batch matching collects requests for a few seconds and solves an assignment problem (minimise total pickup time), which is another <code>Matcher</code>. Finding nearby drivers at scale uses a geospatial index (geohash or H3 cells) instead of scanning all drivers. Promo codes are decorators around the fare strategy.",
    ],
    questions=[
        question(
            "How do you find the nearest available drivers among millions in real time?",
            "hard",
            "Partition the map into cells (geohash, Google S2 or Uber's H3 hexagons). Each driver's location update moves it between per-cell sets kept in memory (Redis or a dedicated location service), sharded by region. A request looks up the rider's cell and its neighbours, expanding rings until enough candidates are found, then ranks those few by estimated time of arrival from a routing service. Location updates every few seconds per driver are the dominant write load.",
        ),
        question(
            "Why model trip states as a transition table instead of a class per state?",
            "medium",
            "Here most states differ only in which transitions are legal; the actions themselves (notify, free the driver) are the same. A table keeps all legal transitions visible in one place and is trivial to test exhaustively. When states have substantially different behaviour (pricing rules, timers per state), state classes become worth their extra code.",
        ),
    ],
)

PROBLEMS = [MOVIE_BOOKING, HOTEL_BOOKING, MEETING_ROOMS, SPLITWISE, RIDE_SHARING]
