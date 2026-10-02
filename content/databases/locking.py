from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="locking",
    title="Concurrency and Locking",
    summary="Shared and exclusive locks, two-phase locking, deadlocks, and optimistic vs pessimistic control.",
    intro=[
        "MVCC removed most reader/writer blocking, but writers still have to be kept from trampling each other, and <code>SELECT ... FOR UPDATE</code>, foreign-key checks, unique-index inserts and DDL all take locks even in an MVCC engine. When a production database stalls, the cause is very often a lock queue, and the most common database error in a busy service after timeouts is a deadlock.",
        "This page covers the lock modes and their compatibility, lock granularity, two-phase locking and why it makes schedules serializable, how deadlocks form and are detected, and the choice between optimistic and pessimistic concurrency &mdash; including the lock-free, single-writer designs latency-sensitive systems prefer.",
    ],
    sections=[
        section(
            "Shared and exclusive locks",
            "The two basic modes: a <strong>shared (S)</strong> lock lets you read and lets others read too; an <strong>exclusive (X)</strong> lock lets you write and keeps everyone else out. Whether a request is granted depends on what is already held:",
            table(
                ["Held → / Requested ↓", "none", "S", "X"],
                [
                    ["S", "grant", "grant", "wait"],
                    ["X", "grant", "wait", "wait"],
                ],
            ),
            "Databases lock at several granularities at once, so they add <strong>intention locks</strong>. Before taking an X lock on a row, a transaction takes an <em>intention-exclusive (IX)</em> lock on the table. Someone who wants to lock the whole table in S mode can now see, by checking one table-level lock, that a row inside it is being written &mdash; without scanning millions of row locks.",
            table(
                ["Held → / Requested ↓", "IS", "IX", "S", "X"],
                [
                    ["IS", "grant", "grant", "grant", "wait"],
                    ["IX", "grant", "grant", "wait", "wait"],
                    ["S", "grant", "wait", "grant", "wait"],
                    ["X", "wait", "wait", "wait", "wait"],
                ],
            ),
            "Two transactions updating different rows both take IX on the table (compatible) and X on their own row (no conflict), so they run in parallel. A <code>LOCK TABLE ... IN SHARE MODE</code> or an <code>ALTER TABLE</code> has to wait for both.",
            "In an MVCC engine, plain reads take no row locks at all. The places you still meet S and X locks: <code>UPDATE</code>/<code>DELETE</code> (X on each row changed), <code>SELECT ... FOR UPDATE</code> (X) and <code>FOR SHARE</code> (S), foreign-key checks (a shared lock on the parent row), unique-index checks, and schema changes (a table-level exclusive lock).",
        ),
        section(
            "Row, page and table locks",
            "Finer locks allow more concurrency and cost more memory and bookkeeping; coarser locks are cheap and serialise more.",
            table(
                ["Granularity", "Who uses it", "Trade-off"],
                [
                    ["Row", "InnoDB, PostgreSQL, Oracle, SQL Server", "Maximum concurrency; one lock per row touched"],
                    ["Page", "SQL Server (sometimes), older engines", "Middle ground; unrelated rows on one page collide"],
                    ["Table", "MyISAM, DDL everywhere, <code>LOCK TABLE</code>", "Cheap; one writer per table"],
                    ["Database", "SQLite", "Trivial to get right; exactly one writer at a time"],
                ],
            ),
            "<strong>Lock escalation</strong>: SQL Server converts many row locks on one table (around 5,000) into a single table lock to save memory, which can suddenly block unrelated work. PostgreSQL never escalates row locks because it stores them in the tuple header rather than in a lock table.",
            "SQLite is the extreme case &mdash; one writer for the whole file. <code>BEGIN IMMEDIATE</code> takes the write lock up front; a second writer gets <code>SQLITE_BUSY</code> after its timeout:",
            code('''
                import os, sqlite3, tempfile

                path = os.path.join(tempfile.mkdtemp(), "demo.db")
                a = sqlite3.connect(path, isolation_level=None, timeout=0.1)
                a.execute("PRAGMA journal_mode = WAL")
                a.execute("CREATE TABLE t(x)")
                b = sqlite3.connect(path, isolation_level=None, timeout=0.1)

                a.execute("BEGIN IMMEDIATE")                  # a is now the writer
                a.execute("INSERT INTO t VALUES (1)")
                print("b can still read:", b.execute("SELECT count(*) FROM t").fetchone()[0])
                try:
                    b.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError as e:
                    print("b cannot write:", e.sqlite_errorname)
                a.execute("COMMIT")
                b.execute("BEGIN IMMEDIATE")
                print("after a commits, b writes")
                b.execute("COMMIT")
            ''', label="one writer per database, readers unaffected (WAL mode)"),
            note("Prefer <code>BEGIN IMMEDIATE</code> for any SQLite transaction that will write. A deferred transaction that reads first and writes later can fail at the write with <code>SQLITE_BUSY_SNAPSHOT</code> and has to be retried from the start."),
        ),
        section(
            "Two-phase locking",
            "<strong>Two-phase locking (2PL)</strong> is the rule that makes lock-based concurrency serializable: a transaction has a <em>growing</em> phase in which it may acquire locks, then a <em>shrinking</em> phase in which it may release them, and once it has released any lock it may never acquire another.",
            "Why that works: at the moment a transaction holds all its locks (the <em>lock point</em>), nothing it read or wrote can be changed by anyone else. Ordering transactions by their lock points gives an equivalent serial order.",
            "Plain 2PL has a hole: if a transaction releases an X lock during its shrinking phase and then aborts, someone may already have read its uncommitted write &mdash; a cascading abort. <strong>Strict 2PL</strong> holds all exclusive locks until commit or abort; <strong>strong strict 2PL</strong> (rigorous) holds all locks until then. Real lock-based databases use the strict forms, which is why &ldquo;locks are released at commit&rdquo; is the everyday rule.",
            code('''
                class Txn:
                    def __init__(self, name):
                        self.name, self.held, self.shrinking = name, set(), False

                    def lock(self, item):
                        if self.shrinking:
                            raise RuntimeError(f"{self.name}: 2PL violation, lock({item}) after an unlock")
                        self.held.add(item)

                    def unlock(self, item):
                        self.shrinking = True
                        self.held.discard(item)

                ok = Txn("T1")
                ok.lock("A"); ok.lock("B")          # growing
                ok.unlock("A"); ok.unlock("B")      # shrinking
                print("T1 followed 2PL")

                bad = Txn("T2")
                bad.lock("A"); bad.unlock("A")
                try:
                    bad.lock("B")
                except RuntimeError as e:
                    print(e)
            ''', label="the rule itself fits in one flag"),
            "What goes wrong without it: T2 reads A, releases it, T1 writes A and B and commits, then T2 reads B. T2 saw A from before T1 and B from after &mdash; a state that never existed at any single point in time.",
            caveat("Two-phase <em>locking</em> is unrelated to two-phase <em>commit</em>. 2PC is a protocol for committing one transaction atomically across several machines (prepare, then commit). Interviewers ask about both and like to check you do not mix them up."),
        ),
        section(
            "Deadlocks: detection and prevention",
            "A deadlock is a cycle of waiting: T1 holds A and wants B, T2 holds B and wants A. Neither can proceed. 2PL makes deadlocks possible, because transactions hold locks while acquiring more.",
            "<strong>Detection.</strong> The lock manager maintains a <em>wait-for graph</em>: an edge T1 &rarr; T2 means T1 is waiting for a lock T2 holds. A cycle is a deadlock. The engine picks a victim (usually the transaction that has done the least work), aborts it, and the others continue. PostgreSQL runs this check after a lock wait exceeds <code>deadlock_timeout</code> (1&nbsp;s); InnoDB checks on every wait.",
            code('''
                def find_cycle(waits_for):
                    """waits_for: txn -> txn it is blocked on. Return one cycle, or None."""
                    for start in waits_for:
                        path, node = [], start
                        while node in waits_for and node not in path:
                            path.append(node)
                            node = waits_for[node]
                        if node in path:
                            return path[path.index(node):]
                    return None

                work_done = {"T1": 40, "T2": 3, "T3": 12, "T4": 7}

                graphs = {
                    "chain": {"T1": "T2", "T2": "T3"},
                    "two-way": {"T1": "T2", "T2": "T1"},
                    "three-way": {"T1": "T2", "T2": "T3", "T3": "T1", "T4": "T1"},
                }
                for name, g in graphs.items():
                    cycle = find_cycle(g)
                    if cycle is None:
                        print(f"{name:<10} no deadlock, just waiting")
                    else:
                        victim = min(cycle, key=work_done.get)
                        print(f"{name:<10} cycle {' -> '.join(cycle + cycle[:1])}; abort {victim}")
            ''', label="a wait-for graph and victim selection"),
            "T4 waits on the three-way cycle but is not part of it; aborting T2 frees the cycle and T4 simply waits a little longer.",
            "<strong>Prevention.</strong> Stop cycles forming in the first place:",
            table(
                ["Technique", "How", "Cost"],
                [
                    ["Global lock order", "Always lock rows in the same order, e.g. by primary key", "Needs discipline everywhere; the standard application-level fix"],
                    ["Lock everything up front", "Acquire all locks at the start (conservative 2PL)", "Must know the lock set in advance; lower concurrency"],
                    ["Wait-die", "An older transaction may wait for a younger one; a younger one requesting from an older one aborts", "Some needless aborts; no cycles possible"],
                    ["Wound-wait", "An older transaction aborts (wounds) a younger holder; a younger requester waits", "Same idea, older transactions never wait for younger"],
                    ["Timeouts", "Give up after N ms (<code>lock_timeout</code>, <code>innodb_lock_wait_timeout</code>)", "Simple; aborts slow-but-innocent transactions too"],
                ],
            ),
            "The same thing happens with application locks. Two threads transferring in opposite directions deadlock; sorting the locks removes the cycle:",
            code('''
                import threading

                def run(ordered):
                    locks = {"alice": threading.Lock(), "bob": threading.Lock()}
                    both_hold_first = threading.Barrier(2, timeout=0.3)
                    done = []

                    def transfer(src, dst):
                        first, second = sorted((src, dst)) if ordered else (src, dst)
                        with locks[first]:
                            if not ordered:
                                both_hold_first.wait()     # force the bad interleaving
                            got = locks[second].acquire(timeout=0.3)
                            if got:
                                locks[second].release()
                            done.append(got)

                    ts = [threading.Thread(target=transfer, args=("alice", "bob")),
                          threading.Thread(target=transfer, args=("bob", "alice"))]
                    for t in ts: t.start()
                    for t in ts: t.join()
                    return "both completed" if all(done) else "deadlock (lock wait timed out)"

                print("each locks its source first ->", run(ordered=False))
                print("both lock in sorted order   ->", run(ordered=True))
            ''', label="opposite-direction transfers"),
            note("Deadlocks are a normal event in a busy OLTP database, not a bug to be eliminated entirely. Keep transactions short, touch rows in a consistent order, and wrap transactions in a retry on deadlock errors (SQLSTATE <code>40P01</code> in PostgreSQL, error 1213 in MySQL)."),
        ),
        section(
            "Optimistic vs pessimistic concurrency",
            "<strong>Pessimistic</strong>: assume conflicts will happen, so lock first (<code>SELECT ... FOR UPDATE</code>) and make everyone else wait. <strong>Optimistic</strong>: assume they won&rsquo;t, so do the work without locks and check at write time whether anything changed; if it did, retry.",
            "The usual optimistic implementation is a version column and a conditional update &mdash; a compare-and-swap at the row level:",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:", isolation_level=None)
                db.execute("CREATE TABLE position(sym TEXT PRIMARY KEY, qty INT, version INT)")
                db.execute("INSERT INTO position VALUES ('ABC', 100, 1)")

                def read():
                    return db.execute("SELECT qty, version FROM position WHERE sym = 'ABC'").fetchone()

                def write(qty, seen_version):
                    cur = db.execute(
                        "UPDATE position SET qty = ?, version = version + 1 "
                        "WHERE sym = 'ABC' AND version = ?", (qty, seen_version))
                    return cur.rowcount == 1

                qty_a, v_a = read()                  # two clients read version 1
                qty_b, v_b = read()
                print("A writes:", write(qty_a + 10, v_a))
                print("B writes:", write(qty_b - 5, v_b))      # stale version: 0 rows match

                qty_b, v_b = read()                  # B retries on fresh data
                print("B retry: ", write(qty_b - 5, v_b))
                print(read())
            ''', label="optimistic concurrency with a version column"),
            table(
                ["", "Pessimistic", "Optimistic"],
                [
                    ["Conflict handling", "Wait for the lock", "Detect at commit, retry"],
                    ["Best when", "Contention is high, retries are expensive", "Contention is low, reads dominate"],
                    ["Failure mode", "Lock waits, deadlocks, blocked threads", "Retry storms under contention; starvation of long transactions"],
                    ["Holds across user think time?", "Never (locks held while a human reads)", "Yes &mdash; the classic edit form: load, edit for minutes, save with version check"],
                    ["Examples", "<code>FOR UPDATE</code>, 2PL, <code>synchronized</code>", "Version columns, ETags, SSI, CAS loops, STM"],
                ],
            ),
            "Under high contention optimistic control degrades badly: if ten clients hammer one hot row, nine of them redo their work every round. Under low contention it wins, because nobody pays for locks they never needed.",
        ),
        section(
            "Lock-free vs lock-based thinking",
            "A lock turns contention into waiting, and waiting is unbounded: a thread holding a lock can be descheduled, page-faulted or preempted, and every other thread stalls behind it. For systems measured in microseconds, that tail is the problem, not the average.",
            "<strong>Lock-free</strong> designs guarantee that some thread always makes progress. They are built on atomic hardware instructions, chiefly <em>compare-and-swap</em>: &ldquo;set this word to <em>new</em> only if it still equals <em>expected</em>&rdquo;. A CAS loop is optimistic concurrency at the level of a single memory word &mdash; the same read, compute, conditional-write, retry shape as the version column above.",
            "The design that usually wins in practice, though, avoids shared mutable state entirely: the <strong>single-writer principle</strong>. Give each piece of state exactly one owning thread. Everything else sends it messages through a queue. The owner never contends with anyone, so it needs no locks and no CAS on its data, and it can keep that data hot in its own CPU cache.",
            code('''
                import queue, threading, zlib

                # One owner thread per shard of symbols; order books are never shared.
                SHARDS = 2
                inboxes = [queue.Queue() for _ in range(SHARDS)]
                books = [{} for _ in range(SHARDS)]

                def owner(i):
                    book = books[i]
                    while (msg := inboxes[i].get()) is not None:
                        sym, qty = msg
                        book[sym] = book.get(sym, 0) + qty      # no lock: only this thread writes

                def route(sym, qty):
                    inboxes[zlib.crc32(sym.encode()) % SHARDS].put((sym, qty))

                workers = [threading.Thread(target=owner, args=(i,)) for i in range(SHARDS)]
                for w in workers: w.start()
                for sym, qty in [("AAPL", 100), ("MSFT", 50), ("AAPL", -30), ("NVDA", 10), ("MSFT", 5)]:
                    route(sym, qty)
                for q in inboxes: q.put(None)
                for w in workers: w.join()
                for i, b in enumerate(books):
                    print(f"shard {i}: {dict(sorted(b.items()))}")
            ''', label="the single-writer principle: partition state, not locks"),
            "This is the LMAX Disruptor&rsquo;s central idea, and it is how matching engines, Redis (one thread executes all commands) and VoltDB (one thread per partition, no locks at all) get their throughput. The same idea at database scale is <em>partitioning</em>: route every transaction for a key to the partition that owns it.",
            caveat("Python&rsquo;s <code>queue.Queue</code> uses locks internally, and the GIL serialises the threads anyway. The snippet shows the ownership structure, not the performance; the real thing uses ring buffers with atomic sequence counters in C++, Rust or Java."),
        ),
    ],
    questions=[
        question(
            "Two concurrent transfers, A&rarr;B and B&rarr;A, keep deadlocking in production. Explain exactly why and give two fixes.",
            "medium",
            "Each transfer runs two <code>UPDATE</code>s. Transfer 1 updates A first and holds A&rsquo;s row lock until commit; transfer 2 updates B first and holds B&rsquo;s. Transfer 1 then needs B, transfer 2 needs A: a cycle in the wait-for graph. The database detects it, aborts one (the victim gets a deadlock error), and the other proceeds.",
            "<strong>Fix 1: consistent order.</strong> Always update the two accounts in ascending ID order regardless of transfer direction. Both transactions now contend for the same first lock and simply queue.<br><strong>Fix 2: lock up front.</strong> <code>SELECT ... FROM accounts WHERE id IN (a, b) ORDER BY id FOR UPDATE</code> before either update.<br><strong>Always:</strong> retry the aborted transaction, because deadlocks can still arise from paths you did not think of (foreign keys, index maintenance, gap locks).",
        ),
        question(
            "What is two-phase locking, why does it guarantee serializability, and how is it different from two-phase commit?",
            "medium",
            "2PL: a transaction acquires locks during a growing phase and releases them during a shrinking phase, never acquiring after it has released. At its lock point it holds every lock it will ever need, so ordering transactions by lock point gives an equivalent serial schedule. Strict 2PL holds write locks until commit to avoid cascading aborts; that is what databases implement.",
            "Two-phase commit is a distributed <em>atomicity</em> protocol: a coordinator asks every participant to <em>prepare</em> (durably promise it can commit), and only if all say yes tells them all to <em>commit</em>. It says nothing about concurrency control. The two are often used together &mdash; a distributed database may use 2PL on each node and 2PC across nodes &mdash; which is exactly why the names get confused.",
        ),
        question(
            "How would you implement a job queue in PostgreSQL so that many workers can pull jobs concurrently without blocking each other or taking the same job?",
            "hard",
            "Use <code>SELECT ... FOR UPDATE SKIP LOCKED</code>:",
            "<code>BEGIN;<br>SELECT id, payload FROM jobs WHERE status = 'ready' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;<br>-- do the work, or at least claim it<br>UPDATE jobs SET status = 'done' WHERE id = $1;<br>COMMIT;</code>",
            "<code>FOR UPDATE</code> locks the chosen row so no other worker can take it. <code>SKIP LOCKED</code> makes other workers skip rows that are locked rather than queue behind them, so each worker grabs the next free job immediately. If a worker crashes, its transaction aborts, the lock is released, and the job becomes visible again.",
            "Caveats worth mentioning: holding a transaction open for the whole job is a long transaction (MVCC bloat), so for long jobs you claim with a short transaction that sets <code>status = 'running', lease_until = now() + interval</code> and have a reaper reset expired leases. Also index <code>(status, id)</code> or use a partial index <code>WHERE status = 'ready'</code> so the scan stays short as done jobs accumulate.",
        ),
        question(
            "When would you choose optimistic over pessimistic concurrency, and what happens to each as contention grows?",
            "hard",
            "Optimistic when conflicts are rare, when the critical section spans user think time or a remote call (you cannot hold a lock for that), or when reads vastly outnumber writes. Pessimistic when conflicts are frequent, when the work is expensive to redo, or when you need a guaranteed outcome without retry logic.",
            "As contention grows, pessimistic throughput falls gradually: transactions queue, latency rises, and deadlock rates increase but work is not wasted. Optimistic throughput can collapse: with N writers on one row, each round one commits and N&minus;1 throw away their work and retry, so wasted work grows with N and long transactions may starve forever behind short ones.",
            "A good answer adds the middle ground: reduce contention itself. Split a hot counter into N sub-counters and sum on read; make the update a single atomic statement (<code>SET n = n + 1</code>) so the lock is held for microseconds; or route all writes for the hot key through one owner.",
        ),
        question(
            "Why might an INSERT deadlock with another INSERT in MySQL InnoDB at REPEATABLE READ?",
            "hard",
            "Gap locks. At REPEATABLE READ, InnoDB prevents phantoms by locking not only index records but the <em>gaps</em> between them (next-key locks). A <code>SELECT ... FOR UPDATE</code> or <code>DELETE</code> on a missing key &mdash; common in &ldquo;check if exists, then insert&rdquo; code &mdash; takes a gap lock on the range where that key would go. Gap locks are compatible with each other, so two transactions can both hold one on the same gap.",
            "Each then tries to <code>INSERT</code> into that gap, which requires an <em>insert intention</em> lock that conflicts with the other&rsquo;s gap lock. Each waits for the other: deadlock.",
            "Fixes: use <code>INSERT ... ON DUPLICATE KEY UPDATE</code> (or <code>INSERT IGNORE</code>) instead of check-then-insert; rely on the unique index to reject the duplicate and handle the error; or run that code path at READ COMMITTED, where InnoDB mostly disables gap locking.",
        ),
    ],
    refs=[
        ("PostgreSQL: explicit locking", "https://www.postgresql.org/docs/current/explicit-locking.html"),
        ("MySQL: InnoDB locking", "https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html"),
        ("SQLite: file locking and concurrency", "https://www.sqlite.org/lockingv3.html"),
        ("Martin Thompson — the single writer principle", "https://mechanical-sympathy.blogspot.com/2011/09/single-writer-principle.html"),
        ("LMAX Disruptor technical paper", "https://lmax-exchange.github.io/disruptor/disruptor.html"),
    ],
)
