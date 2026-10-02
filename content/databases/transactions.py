from deepdive._blocks import code, table, note, caveat, section, question

# A toy multi-version store shared by several snippets on this page. Each
# snippet is executed on its own, so the source is pasted into each one.
MVCC = '''
class DB:
    def __init__(self, rows):
        self.versions = {k: [(v, 0)] for k, v in rows.items()}  # key -> [(value, writer)]
        self.committed, self.next_id = {0}, 1

    def begin(self, level):
        return Txn(self, level)

class Txn:
    def __init__(self, db, level):
        self.db, self.level, self.id = db, level, db.next_id
        db.next_id += 1
        self.snapshot = set(db.committed)        # who had committed when we started

    def visible(self, writer):
        if writer == self.id or self.level == "read uncommitted":
            return True
        if self.level == "read committed":        # latest committed, per statement
            return writer in self.db.committed
        return writer in self.snapshot            # snapshot: frozen at BEGIN

    def get(self, key):
        for value, writer in reversed(self.db.versions.get(key, [])):
            if self.visible(writer):
                return value
        return None

    def keys(self):
        return [k for k in self.db.versions if self.get(k) is not None]

    def put(self, key, value):
        self.db.versions.setdefault(key, []).append((value, self.id))

    def commit(self):
        self.db.committed.add(self.id)
'''

TOPIC = dict(
    id="transactions",
    title="Transactions, ACID and Isolation",
    summary="What each ACID letter promises, the read anomalies, and how MVCC gives readers a snapshot.",
    intro=[
        "A transaction is a group of reads and writes the database treats as one unit: either all of it happens or none of it does, and concurrent transactions are kept from seeing each other&rsquo;s half-finished work. That sentence hides almost every hard question in database engineering, and interviewers know it.",
        "This page covers what ACID actually guarantees (and what it does not), commit and rollback, the isolation levels and the anomalies each one permits, and how MVCC lets readers and writers stop blocking each other. SQLite from the standard library runs the real examples; where SQLite is too strict to exhibit an anomaly, a twenty-line model of a multi-version store does.",
    ],
    sections=[
        section(
            "ACID, letter by letter",
            table(
                ["Letter", "Promise", "Mechanism", "Common misreading"],
                [
                    ["<strong>A</strong>tomicity", "All of the transaction&rsquo;s writes take effect, or none do", "Undo log / rollback segments, or shadow copies", "It is about <em>failure</em>, not concurrency"],
                    ["<strong>C</strong>onsistency", "A transaction moves the database from one valid state to another", "Constraints, triggers &mdash; and your application logic", "Not the C in CAP. Mostly the application&rsquo;s job"],
                    ["<strong>I</strong>solation", "Concurrent transactions do not see each other&rsquo;s intermediate states", "Locks, MVCC snapshots, conflict detection", "Default levels are weaker than &ldquo;as if run one at a time&rdquo;"],
                    ["<strong>D</strong>urability", "Once commit returns, the data survives a crash", "Write-ahead log flushed with <code>fsync</code> before acknowledging", "Only as durable as the disk&rsquo;s honesty about <code>fsync</code>, and one machine is one failure domain"],
                ],
            ),
            "Consistency is the odd one out. The database can enforce declared constraints (<code>NOT NULL</code>, <code>CHECK</code>, foreign keys, uniqueness), but &ldquo;an order&rsquo;s total equals the sum of its lines&rdquo; or &ldquo;a trader cannot exceed their risk limit&rdquo; is only preserved if every transaction the application writes preserves it. Atomicity and isolation are the tools the database gives you to make that possible.",
            note("Atomicity handles crashes and errors in the middle of one transaction. Isolation handles other transactions running at the same time. They are different problems with different machinery."),
        ),
        section(
            "Commit and rollback",
            "The canonical example: move money between accounts. Two <code>UPDATE</code>s must both happen, or neither. If the second one fails &mdash; a constraint, a crash, a lost connection &mdash; the first must be undone.",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:", isolation_level=None)   # we issue BEGIN ourselves
                db.execute("CREATE TABLE acct(name TEXT PRIMARY KEY, bal INT CHECK (bal >= 0))")
                db.execute("INSERT INTO acct VALUES ('alice', 100), ('bob', 50)")

                def transfer(src, dst, amount):
                    db.execute("BEGIN")
                    try:
                        db.execute("UPDATE acct SET bal = bal + ? WHERE name = ?", (amount, dst))
                        db.execute("UPDATE acct SET bal = bal - ? WHERE name = ?", (amount, src))
                        db.execute("COMMIT")
                        print(f"moved {amount}")
                    except sqlite3.IntegrityError as e:
                        db.execute("ROLLBACK")
                        print(f"rolled back: {e}")

                transfer("alice", "bob", 30)
                transfer("alice", "bob", 500)      # second UPDATE violates the CHECK
                print(dict(db.execute("SELECT * FROM acct")))
            ''', label="the credit to bob is undone when the debit fails"),
            "The failed transfer credited Bob first. Without atomicity, 500 would have appeared from nowhere. With it, the rollback put the database back exactly as it was.",
            "<strong>Savepoints</strong> give partial rollback inside one transaction: <code>SAVEPOINT s</code>, then <code>ROLLBACK TO s</code> discards only the work after it. ORMs use them to implement nested transactions.",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:", isolation_level=None)
                db.execute("CREATE TABLE log(msg TEXT)")
                db.execute("BEGIN")
                db.execute("INSERT INTO log VALUES ('order accepted')")
                db.execute("SAVEPOINT risk")
                db.execute("INSERT INTO log VALUES ('hedge placed')")
                db.execute("ROLLBACK TO risk")            # undo only the hedge
                db.execute("INSERT INTO log VALUES ('hedge skipped')")
                db.execute("COMMIT")
                print([m for (m,) in db.execute("SELECT msg FROM log")])
            ''', label="savepoints"),
            caveat("Python&rsquo;s <code>sqlite3</code> module historically opened transactions implicitly before DML and never before DDL, which surprised many people. Since Python 3.12 the <code>autocommit</code> connection attribute gives PEP 249-conforming behaviour. Passing <code>isolation_level=None</code>, as here, means &ldquo;do nothing implicitly; I will write BEGIN myself&rdquo;."),
        ),
        section(
            "Isolation levels and the anomalies they allow",
            "Running every transaction one at a time (<em>serial</em> execution) would make isolation trivial and throughput terrible. Isolation levels are a menu of weaker guarantees that allow more concurrency. The SQL standard defines them by which anomalies they permit:",
            table(
                ["Anomaly", "What happens"],
                [
                    ["<strong>Dirty read</strong>", "You read another transaction&rsquo;s uncommitted write, which may then be rolled back"],
                    ["<strong>Non-repeatable read</strong>", "You read a row twice and get different values, because someone committed an update in between"],
                    ["<strong>Phantom read</strong>", "You run the same <code>WHERE</code> query twice and get a different <em>set</em> of rows, because someone inserted or deleted a matching row"],
                    ["<strong>Lost update</strong>", "Two transactions read-modify-write the same row; one write silently overwrites the other"],
                    ["<strong>Write skew</strong>", "Two transactions read overlapping data, write <em>different</em> rows, and together break an invariant neither broke alone"],
                ],
            ),
            "The model below is a multi-version store: every write appends a version tagged with its writer, and each isolation level is nothing more than a different rule for which versions a reader may see. Running the three classic scenarios under each rule:",
            code(MVCC + '''
def dirty(level):
    db = DB({"alice": 100})
    t1, t2 = db.begin(level), db.begin(level)
    t2.put("alice", 0)                        # not committed
    return t1.get("alice") == 0

def non_repeatable(level):
    db = DB({"alice": 100})
    t1, t2 = db.begin(level), db.begin(level)
    first = t1.get("alice")
    t2.put("alice", 0); t2.commit()
    return t1.get("alice") != first

def phantom(level):
    db = DB({"alice": 100, "bob": 50})
    t1, t2 = db.begin(level), db.begin(level)
    first = len(t1.keys())
    t2.put("carol", 70); t2.commit()          # a new matching row
    return len(t1.keys()) != first

print(f"{'level':<17} {'dirty':>6} {'non-rep':>8} {'phantom':>8}")
for level in ("read uncommitted", "read committed", "snapshot"):
    row = ["yes" if f(level) else "-" for f in (dirty, non_repeatable, phantom)]
    print(f"{level:<17} {row[0]:>6} {row[1]:>8} {row[2]:>8}")
''', label="which anomalies does each visibility rule allow?"),
            "<strong>Read committed</strong> takes a fresh view per statement, so it never sees uncommitted data but can see different committed data on each read. <strong>Snapshot</strong> fixes the view when the transaction starts, so every read is repeatable and no phantoms appear.",
            "What the real engines do:",
            table(
                ["Engine", "Default level", "Notes"],
                [
                    ["PostgreSQL", "Read committed", "<code>REPEATABLE READ</code> is snapshot isolation; <code>SERIALIZABLE</code> is SSI (detects dangerous read/write patterns and aborts)"],
                    ["MySQL InnoDB", "Repeatable read", "Plain <code>SELECT</code>s read a snapshot; locking reads and <code>UPDATE</code>s read the <em>latest</em> version and take next-key (gap) locks"],
                    ["Oracle", "Read committed", "Its <code>SERIALIZABLE</code> is actually snapshot isolation"],
                    ["SQL Server", "Read committed (locking)", "<code>READ_COMMITTED_SNAPSHOT</code> and <code>SNAPSHOT</code> are opt-in MVCC modes"],
                    ["SQLite", "Serializable", "One writer at a time for the whole database, so most anomalies cannot happen"],
                ],
            ),
            "SQLite does support one weaker mode, <code>read_uncommitted</code>, between connections that share a cache. It is the easiest place to see a real dirty read:",
            code('''
                import sqlite3

                uri = "file:bank?mode=memory&cache=shared"
                writer = sqlite3.connect(uri, uri=True, isolation_level=None)
                reader = sqlite3.connect(uri, uri=True, isolation_level=None)
                writer.execute("CREATE TABLE acct(name TEXT PRIMARY KEY, bal INT)")
                writer.execute("INSERT INTO acct VALUES ('alice', 100)")

                writer.execute("BEGIN")
                writer.execute("UPDATE acct SET bal = 0 WHERE name = 'alice'")

                reader.execute("PRAGMA read_uncommitted = 1")
                print("reader sees (dirty):", reader.execute("SELECT bal FROM acct").fetchone()[0])

                writer.execute("ROLLBACK")
                print("after rollback:     ", reader.execute("SELECT bal FROM acct").fetchone()[0])
            ''', label="a real dirty read"),
            "The reader acted on a balance of 0 that never existed.",
        ),
        section(
            "MVCC: readers don&rsquo;t block writers",
            "The oldest way to implement isolation is locking: readers take shared locks, writers take exclusive locks, and they wait for each other. <strong>Multi-version concurrency control</strong> instead keeps several versions of each row. A writer creates a new version rather than overwriting in place; a reader picks the version that was committed as of its snapshot. Readers never wait for writers and writers never wait for readers. Writers still conflict with other writers of the same row.",
            table(
                ["Engine", "Where old versions live", "Cleanup"],
                [
                    ["PostgreSQL", "In the table itself: each tuple has <code>xmin</code> (creating txid) and <code>xmax</code> (deleting txid); an update writes a whole new tuple", "<code>VACUUM</code> reclaims dead tuples"],
                    ["MySQL InnoDB, Oracle", "The row is updated in place; previous versions are reconstructed from the <em>undo log</em>", "Purge thread discards undo no snapshot needs"],
                    ["SQLite (WAL mode)", "Changed pages are appended to the WAL; a reader remembers how much of the WAL it may see", "Checkpoint copies WAL pages back into the database file"],
                ],
            ),
            code('''
                import os, sqlite3, tempfile

                path = os.path.join(tempfile.mkdtemp(), "demo.db")
                a = sqlite3.connect(path, isolation_level=None)
                a.execute("PRAGMA journal_mode = WAL")
                a.execute("CREATE TABLE price(sym TEXT, px REAL)")
                a.execute("INSERT INTO price VALUES ('ABC', 10.0)")

                b = sqlite3.connect(path, isolation_level=None)
                b.execute("BEGIN")
                print("b reads:", b.execute("SELECT px FROM price").fetchone()[0])  # snapshot taken here

                a.execute("UPDATE price SET px = 11.0")        # writer is not blocked by b
                print("a reads:", a.execute("SELECT px FROM price").fetchone()[0])
                print("b reads:", b.execute("SELECT px FROM price").fetchone()[0])  # still its snapshot
                b.execute("COMMIT")
                print("b, new transaction:", b.execute("SELECT px FROM price").fetchone()[0])
            ''', label="a WAL-mode reader keeps its snapshot while a writer commits"),
            "The cost of MVCC is garbage. Every old version must be kept until no running transaction might need it, which means <strong>one long-running transaction pins every version created after it started</strong> &mdash; across the whole database. Tables bloat, indexes bloat, and in PostgreSQL <code>VACUUM</code> can do nothing until that transaction ends.",
            note("Keep transactions short. Never hold one open across a network call, a user prompt, or a <code>sleep</code>."),
        ),
        section(
            "Snapshot isolation and write skew",
            "Snapshot isolation stops dirty reads, non-repeatable reads and phantoms. It also prevents lost updates, with a rule called <strong>first committer wins</strong>: if two transactions update the same row, the second to commit is aborted. SQLite enforces the same thing when a reader with an old snapshot tries to become a writer:",
            code('''
                import os, sqlite3, tempfile

                path = os.path.join(tempfile.mkdtemp(), "demo.db")
                a = sqlite3.connect(path, isolation_level=None)
                a.execute("PRAGMA journal_mode = WAL")
                a.execute("CREATE TABLE counter(n INT)")
                a.execute("INSERT INTO counter VALUES (0)")

                b = sqlite3.connect(path, isolation_level=None)   # default 5 s busy timeout
                b.execute("BEGIN")
                n = b.execute("SELECT n FROM counter").fetchone()[0]      # b's snapshot: n = 0

                a.execute("UPDATE counter SET n = n + 1")                 # a commits n = 1
                try:
                    b.execute("UPDATE counter SET n = ?", (n + 1,))       # would overwrite a's update
                except sqlite3.OperationalError as e:
                    print(f"b refused at once: {e} ({e.sqlite_errorname})")
                    b.execute("ROLLBACK")
                print("n =", a.execute("SELECT n FROM counter").fetchone()[0])
            ''', label="a stale snapshot is not allowed to write"),
            "The message is SQLite&rsquo;s generic one; the extended code <code>SQLITE_BUSY_SNAPSHOT</code> means &ldquo;your snapshot is out of date, retry the whole transaction&rdquo;. Waiting would not help, so it fails immediately instead of spending the five-second busy timeout.",
            "What snapshot isolation does <em>not</em> prevent is <strong>write skew</strong>. Two transactions read the same data, each decides its write is safe, and each writes a <em>different</em> row. There is no write-write conflict to detect, so both commit. The textbook case: a hospital requires at least one doctor on call, two are on call, and both ask to go off call at the same moment.",
            code(MVCC + '''
db = DB({"alice": "on", "bob": "on"})

def go_off_call(t, me):
    on_call = [k for k in t.keys() if t.get(k) == "on"]
    if len(on_call) >= 2:                 # "someone else will still be on call"
        t.put(me, "off")

t1, t2 = db.begin("snapshot"), db.begin("snapshot")
go_off_call(t1, "alice")
go_off_call(t2, "bob")
t1.commit(); t2.commit()                  # different rows: no conflict

final = db.begin("snapshot")
print({k: final.get(k) for k in final.keys()})
''', label="write skew: each transaction is correct alone, together they are not"),
            "Nobody is on call. The same shape appears in trading systems as two orders that each pass a risk check against the same limit, or two bookings for the last seat checked against a count.",
            "Fixes, from narrowest to broadest:",
            "<strong>Lock what you read.</strong> <code>SELECT ... FOR UPDATE</code> on the rows the decision depends on turns the read into a write-lock, so the second transaction waits.<br><strong>Materialise the conflict.</strong> If the invariant is about rows that might not exist yet, give it a row that does &mdash; a per-limit or per-shift row both transactions must update.<br><strong>Use a constraint.</strong> Where the invariant can be declared (unique, exclusion constraint), the database checks it atomically.<br><strong>Use <code>SERIALIZABLE</code>.</strong> PostgreSQL&rsquo;s serializable snapshot isolation tracks read/write dependencies and aborts one of the two; your code must then retry.",
            caveat("<code>SERIALIZABLE</code> in PostgreSQL and CockroachDB will abort transactions with a serialization failure (SQLSTATE <code>40001</code>) as a normal part of operation. Code that runs at that level needs a retry loop, and the transaction body must be safe to re-run."),
        ),
    ],
    questions=[
        question(
            "Two requests each run <code>SELECT qty FROM stock WHERE id = 1</code>, compute <code>qty - 1</code> in the application, and write it back under READ COMMITTED. What goes wrong and what are the fixes?",
            "medium",
            "A <strong>lost update</strong>. Both read 10, both write 9, one decrement disappears. Read committed does nothing about it: each statement sees committed data, and the second write simply overwrites the first.",
            "Fixes, in order of preference:",
            "<strong>Make it one atomic statement:</strong> <code>UPDATE stock SET qty = qty - 1 WHERE id = 1 AND qty &gt; 0</code>. The row lock taken by the <code>UPDATE</code> serialises the two; checking the affected row count tells you whether it succeeded.<br><strong>Pessimistic lock:</strong> <code>SELECT ... FOR UPDATE</code>, so the second reader waits for the first to commit.<br><strong>Optimistic check:</strong> add a <code>version</code> column and <code>UPDATE ... SET qty = ?, version = version + 1 WHERE id = 1 AND version = ?</code>; zero rows updated means someone else won, so retry.<br><strong>Raise isolation:</strong> PostgreSQL&rsquo;s <code>REPEATABLE READ</code> aborts the second writer (first committer wins).",
        ),
        question(
            "Explain the difference between REPEATABLE READ in PostgreSQL and in MySQL InnoDB.",
            "hard",
            "<strong>PostgreSQL</strong>: REPEATABLE READ is snapshot isolation. Every statement, reads and writes alike, sees the snapshot taken at the transaction&rsquo;s first statement. If you try to update a row that someone else changed and committed after your snapshot, you get a serialization error and must retry. No phantoms, no lost updates; write skew is still possible.",
            "<strong>MySQL InnoDB</strong>: plain <code>SELECT</code>s read a consistent snapshot, but <code>UPDATE</code>, <code>DELETE</code> and <code>SELECT ... FOR UPDATE</code> perform <em>current reads</em> of the latest committed version and lock it. So within one transaction a <code>SELECT</code> can say a row has <code>qty = 10</code> while <code>UPDATE ... SET qty = qty - 1</code> acts on the newer 7. There is no serialization error: the update just applies to the latest data. Locking reads also take next-key (gap) locks to prevent phantoms in the ranges they scanned, which is a common source of unexpected lock waits and deadlocks.",
            "The practical upshot: the same application code can be correct on one and subtly wrong on the other, so know which one you are on.",
        ),
        question(
            "What does the C in ACID mean, and how does it differ from the C in CAP?",
            "medium",
            "ACID consistency means each transaction takes the database from one state that satisfies its invariants to another. The database enforces the invariants it can see (constraints, foreign keys, uniqueness); the rest is the application&rsquo;s responsibility, using atomicity and isolation as tools. It is arguably a property of the application rather than the database.",
            "CAP consistency means <em>linearizability</em>: in a replicated system, every read returns the most recent completed write, as if there were a single copy of the data. It is about replicas agreeing, not about invariants. A single-node database can be ACID-consistent without the concept of CAP consistency even applying; a replicated store can be linearizable while holding data that violates business rules.",
        ),
        question(
            "Why can a single forgotten open transaction hurt an MVCC database for hours?",
            "hard",
            "MVCC can only discard an old row version once no running transaction could need it. The oldest open snapshot sets that horizon for the whole database. An idle-in-transaction session opened this morning therefore pins every version created since this morning, on every table.",
            "Effects in PostgreSQL: <code>VACUUM</code> runs but cannot remove dead tuples, so tables and indexes bloat and scans slow down; index-only scans degrade because pages cannot be marked all-visible; in the extreme, transaction-ID wraparound protection eventually forces the database into a protective shutdown. In InnoDB the undo log (history list) grows without bound and every read that must reconstruct an old version walks a longer chain.",
            "Defences: <code>idle_in_transaction_session_timeout</code> (PostgreSQL), monitoring <code>pg_stat_activity</code> for old <code>xact_start</code> or InnoDB&rsquo;s history list length, and application discipline &mdash; never hold a transaction open across I/O you do not control. Replication slots and long-running queries on hot standbys with <code>hot_standby_feedback</code> have the same pinning effect.",
        ),
        question(
            "Two risk checks run concurrently, each verifying a trader&rsquo;s total exposure is under a limit before inserting a new order row. Both pass and the limit is breached. The database runs snapshot isolation. Why, and how do you fix it?",
            "hard",
            "It is write skew. Each transaction reads the same set of existing orders from its snapshot, sees headroom, and inserts a <em>new, different</em> row. Snapshot isolation only detects two writes to the same row, so there is no conflict and both commit. (If it were a phantom-style read of a range, snapshot isolation would still not help, because the phantom is in the other transaction&rsquo;s write, not in your reads.)",
            "Fixes: give the invariant a row to conflict on &mdash; a <code>trader_exposure</code> row updated atomically with <code>UPDATE ... SET used = used + ? WHERE trader = ? AND used + ? &lt;= limit</code> and checked for one affected row; or <code>SELECT ... FOR UPDATE</code> on the trader&rsquo;s row before the check; or run at <code>SERIALIZABLE</code> and retry on <code>40001</code>.",
            "In a latency-sensitive system the usual answer is not to use the database for this at all: route every order for one trader through a single thread that owns that trader&rsquo;s exposure in memory, so the check-and-reserve is naturally serial, and persist the result afterwards.",
        ),
    ],
    refs=[
        ("PostgreSQL: transaction isolation", "https://www.postgresql.org/docs/current/transaction-iso.html"),
        ("MySQL: InnoDB transaction isolation levels", "https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html"),
        ("SQLite: isolation in SQLite", "https://www.sqlite.org/isolation.html"),
        ("Berenson et al. — A Critique of ANSI SQL Isolation Levels", "https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/"),
        ("Hermitage: testing isolation levels across databases", "https://github.com/ept/hermitage"),
    ],
)
