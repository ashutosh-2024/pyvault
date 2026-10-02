from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="unique-ids",
    title="Unique ID Generation",
    summary="Auto-increment, UUIDv4 vs v7, Snowflake IDs, ticket servers, and why ID order matters to your database.",
    intro=[
        "Every stored object needs an identifier, and in a distributed system several machines must create them at once without ever colliding. The choice looks trivial and is not: it decides whether IDs leak business data, whether they sort by time, how big your indexes are, and how fast inserts are.",
        "This topic builds the main options &mdash; database sequences, random UUIDs, time-ordered UUIDs and Snowflake-style IDs &mdash; and measures their properties.",
    ],
    sections=[
        section(
            "Requirements first",
            "Ask which of these properties matter before picking a scheme:",
            table(
                ["Property", "Why it matters"],
                [
                    ["Unique without coordination", "Any server can mint IDs during a network partition, with no shared counter on the hot path"],
                    ["Roughly time-ordered", "Newest-first queries and pagination by ID; B-tree inserts land at the right edge"],
                    ["Compact", "64-bit integers are half the size of 128-bit UUIDs in every index and foreign key"],
                    ["Not guessable", "Sequential IDs let anyone enumerate <code>/invoice/1001</code>, <code>/invoice/1002</code>&hellip; and reveal volumes"],
                    ["Generated offline", "Mobile clients create objects before syncing"],
                ],
            ),
        ),
        section(
            "Database auto-increment",
            "The simplest scheme: the database hands out 1, 2, 3&hellip;. Compact, ordered, and guaranteed unique &mdash; on one database. With several writers you either route every insert through one node (a bottleneck and single point of failure) or give each node a disjoint stream.",
            code('''
                class Node:
                    """Each of k nodes owns the IDs congruent to its index mod k."""
                    def __init__(self, index, k):
                        self.next, self.step = index + 1, k

                    def new_id(self):
                        value, self.next = self.next, self.next + self.step
                        return value

                a, b, c = (Node(i, 3) for i in range(3))
                ids = [a.new_id(), a.new_id(), b.new_id(), c.new_id(), a.new_id(), c.new_id()]
                print(ids, "unique:", len(set(ids)) == len(ids))
            '''),
            "This is how MySQL's <code>auto_increment_increment</code>/<code>offset</code> multi-primary setups work. Adding a fourth node later changes the step for everyone, and the IDs are guessable. A <strong>ticket server</strong> (Flickr's design) is a variant: a dedicated database whose only job is incrementing a counter, often handing out blocks of 1,000 IDs at a time so callers rarely need to ask.",
        ),
        section(
            "UUIDv4: random",
            "A version-4 UUID is 122 random bits plus 6 version bits. No coordination, generated anywhere, unguessable. Collisions are not impossible, just absurdly unlikely: by the birthday bound they only become likely around 2<sup>61</sup> IDs (a 50% chance needs about 2.7 &times; 10<sup>18</sup>).",
            code('''
                import math, uuid

                u = uuid.uuid4()
                print(u, "version", u.version, "| bits of randomness: 122")

                def collision_probability(n, bits=122):
                    return -math.expm1(-n * n / (2 * 2 ** bits))     # birthday approximation

                for n in (10**9, 10**12, 10**15, 2**61):
                    print(f"{n:>22,} ids -> P(any collision) = {collision_probability(n):.2e}")
            '''),
            "The cost is order. Random IDs scatter inserts across the whole primary-key index: each insert touches a random leaf page, so the working set is the entire index rather than its right edge, pages split everywhere, and caches miss. On large tables with a clustered primary key (InnoDB, SQL Server) that is a well-known insert slowdown.",
        ),
        section(
            "Time-ordered IDs: UUIDv7 and ULID",
            "UUIDv7 (RFC 9562, 2024) puts a 48-bit Unix millisecond timestamp in the first bits and fills the rest with randomness. It is still a standard 128-bit UUID, generated without coordination, but IDs created later sort later, so inserts go to the right edge of the index like an auto-increment.",
            code('''
                import os, time, uuid

                def uuid7(ms=None):
                    ms = int(time.time() * 1000) if ms is None else ms
                    rand = int.from_bytes(os.urandom(10), "big")
                    value = (ms & ((1 << 48) - 1)) << 80                     # 48-bit timestamp
                    value |= 0x7 << 76                                       # version 7
                    value |= ((rand >> 62) & 0xFFF) << 64                    # 12 random bits
                    value |= 0b10 << 62                                      # RFC variant
                    value |= rand & ((1 << 62) - 1)                          # 62 random bits
                    return uuid.UUID(int=value)

                base = 1_700_000_000_000
                ids = [uuid7(base + i) for i in (0, 1, 2, 3)]
                for u in ids:
                    print(u, "version", u.version, "ms", u.int >> 80)
                print("sorted by value == creation order:", sorted(ids) == ids)
                print("v4 ids sorted == creation order?  ", (lambda v: sorted(v) == v)([uuid.uuid4() for _ in range(20)]))
            '''),
            caveat("Python 3.14 ships <code>uuid.uuid7()</code> in the standard library; the hand-written version above shows the bit layout. ULID is an older community format with the same idea (48-bit time + 80 random bits) encoded in 26 Crockford base-32 characters."),
        ),
        section(
            "Snowflake IDs",
            "Twitter's Snowflake packs a 64-bit integer: 41 bits of milliseconds since a custom epoch, 10 bits of machine id, 12 bits of per-millisecond sequence. Each machine can mint 4,096 IDs per millisecond with no coordination beyond assigning machine ids once; the IDs are time-ordered, fit in a <code>BIGINT</code>, and the creation time can be read back out of the ID.",
            code('''
                import threading

                EPOCH = 1_288_834_974_657                      # Twitter's epoch (Nov 2010), in ms

                class Snowflake:
                    def __init__(self, machine_id, clock):
                        assert 0 <= machine_id < 1024
                        self.machine, self.clock = machine_id, clock
                        self.last_ms, self.seq = -1, 0
                        self.lock = threading.Lock()

                    def next_id(self):
                        with self.lock:
                            ms = self.clock()
                            if ms < self.last_ms:
                                raise RuntimeError("clock moved backwards")
                            if ms == self.last_ms:
                                self.seq = (self.seq + 1) & 0xFFF
                                if self.seq == 0:                   # 4096 used this ms: wait
                                    while ms <= self.last_ms:
                                        ms = self.clock()
                            else:
                                self.seq = 0
                            self.last_ms = ms
                            return ((ms - EPOCH) << 22) | (self.machine << 12) | self.seq

                def decode(i):
                    return {"ms": (i >> 22) + EPOCH, "machine": (i >> 12) & 0x3FF, "seq": i & 0xFFF}

                fake_now = [1_700_000_000_000]
                gen = Snowflake(machine_id=37, clock=lambda: fake_now[0])
                ids = [gen.next_id() for _ in range(3)]
                fake_now[0] += 1
                ids.append(gen.next_id())
                for i in ids:
                    print(i, decode(i))
                print("bits used:", max(ids).bit_length(), "of 63 (sign bit kept clear)")
                print("years of ids in 41 bits:", round(2**41 / (1000 * 3600 * 24 * 365.25), 1))
            '''),
            "Two operational details carry the risk. Machine ids must be unique, so they are leased from ZooKeeper/etcd or derived from a stable pod ordinal, never picked at random. And the scheme depends on clocks: if NTP moves a clock backwards, the generator must refuse (as above) or wait, or it could repeat IDs.",
        ),
        section(
            "Comparison",
            "Insert locality, measured: how many distinct B-tree &ldquo;pages&rdquo; (blocks of 100 consecutive keys in sorted order) the last 1,000 inserts touched, out of 100,000 rows.",
            code('''
                import random, uuid, bisect

                def pages_touched(keys, page=100, recent=1000):
                    order = sorted(keys)
                    rank = {k: i for i, k in enumerate(order)}
                    return len({rank[k] // page for k in keys[-recent:]})

                n = 100_000
                sequential = list(range(n))
                v4 = [uuid.uuid4().int for _ in range(n)]
                ms0, rng = 1_700_000_000_000, random.Random(0)
                v7_like = [((ms0 + i // 10) << 80) | rng.getrandbits(80) for i in range(n)]   # 10 ids per ms

                for name, keys in (("auto-increment", sequential), ("UUIDv7", v7_like), ("UUIDv4", v4)):
                    print(f"{name:15} recent inserts touched {pages_touched(keys):4} of {n // 100} pages")
            '''),
            table(
                ["Scheme", "Size", "Ordered", "Coordination", "Guessable", "Notes"],
                [
                    ["Auto-increment", "64 bit", "Yes", "Central counter", "Yes", "Simple; bottleneck across writers"],
                    ["UUIDv4", "128 bit", "No", "None", "No", "Scattered index inserts"],
                    ["UUIDv7 / ULID", "128 bit", "By ms", "None", "Partly (time visible)", "Good default for new systems"],
                    ["Snowflake", "64 bit", "By ms", "Machine-id assignment", "Partly", "Compact; depends on clocks"],
                    ["Ticket server / blocks", "64 bit", "Mostly", "Central, amortised", "Yes", "Block hand-out avoids the hot path"],
                ],
            ),
            note("Use an ordered ID as the primary key, and if IDs are exposed in URLs where enumeration matters, expose a separate random public id (or a v4 UUID) rather than the internal key."),
        ),
    ],
    questions=[
        question(
            "Design an ID generator for a service that creates 50,000 objects per second across 100 servers, where IDs must be 64-bit and roughly sortable by time.",
            "hard",
            "Snowflake layout: 41-bit millisecond timestamp (69 years from a custom epoch), 10-bit worker id (1,024 workers), 12-bit sequence (4,096 per ms per worker). Capacity per worker is 4 million IDs per second, far above 500 per second each. Worker ids come from a coordination service lease, or from a stable ordinal such as a StatefulSet index, and are released on shutdown.",
            "Edge cases to cover: clock going backwards (refuse or wait until it catches up; alert on NTP steps), sequence exhaustion within one millisecond (spin to the next ms), restarts within the same millisecond (persist or wait out the last timestamp), and running out of worker ids (the bit split is a trade-off: fewer timestamp bits, more worker bits). IDs are k-sorted, not strictly ordered across workers within a millisecond, which is fine for feeds and pagination.",
        ),
        question(
            "Why can UUIDv4 primary keys make inserts slow, and what do you use instead?",
            "medium",
            "A B-tree primary key stores rows in key order. Random keys mean every insert goes to a random leaf page: the whole index must stay in memory to avoid disk reads, pages split all over the tree and end up half full, and write amplification grows. Sequential keys append to the rightmost page, which is always hot in cache. Use a time-ordered ID (UUIDv7, ULID, Snowflake) or an auto-increment primary key, keeping a random UUID as a separate public identifier if needed.",
        ),
        question(
            "Can two UUIDv4s collide? Should your code handle it?",
            "medium",
            "In principle yes, in practice no: with 122 random bits you would need about 2.7 quintillion IDs for a 50% collision chance, and at a billion per second that takes about 85 years. Real collisions come from bugs: a bad or unseeded random source, a forked process sharing generator state, or copying IDs. A unique constraint on the column is the right safeguard &mdash; a collision then becomes an error you can retry instead of silent data corruption.",
        ),
        question(
            "Snowflake IDs depend on time. What happens when the clock jumps backwards?",
            "hard",
            "If the generator used the earlier time, it could produce an ID with a timestamp and sequence it already issued: a duplicate. Implementations track the last timestamp used and, when the clock is behind it, either refuse to generate (fail fast, alert) or wait until the clock passes the last timestamp; small skews can be absorbed by continuing from the last timestamp with the sequence. Operationally, run NTP in slewing mode so it adjusts clock speed rather than stepping, and treat large steps as incidents.",
        ),
    ],
    refs=[
        ("RFC 9562: Universally Unique IDentifiers (UUIDv7)", "https://www.rfc-editor.org/rfc/rfc9562"),
        ("Twitter: Announcing Snowflake", "https://blog.x.com/engineering/en_us/a/2010/announcing-snowflake"),
        ("Flickr: Ticket servers, distributed unique primary keys on the cheap", "https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/"),
        ("Python docs: uuid", "https://docs.python.org/3/library/uuid.html"),
    ],
)
