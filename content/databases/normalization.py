from deepdive._blocks import code, table, note, caveat, section, question

# Functional-dependency helpers shared by two snippets.
FD = '''
from itertools import combinations

def closure(attrs, fds):
    """All attributes determined by attrs under the dependencies fds."""
    result, changed = set(attrs), True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if set(lhs) <= result and not set(rhs) <= result:
                result |= set(rhs)
                changed = True
    return result

def candidate_keys(schema, fds):
    keys = []
    for n in range(1, len(schema) + 1):
        for combo in combinations(sorted(schema), n):
            if closure(combo, fds) == set(schema) and not any(set(k) <= set(combo) for k in keys):
                keys.append(combo)
    return keys

def bcnf_violations(schema, fds):
    """Dependencies whose left side is not a superkey."""
    return [(lhs, rhs) for lhs, rhs in fds
            if not set(rhs) <= set(lhs) and closure(lhs, fds) != set(schema)]
'''

TOPIC = dict(
    id="normalization",
    title="Normalization and Denormalization",
    summary="1NF through BCNF as the removal of update anomalies, and when to deliberately undo it.",
    intro=[
        "Normalization is a method for deciding which columns belong in which table so that each fact is stored exactly once. The normal forms sound academic, but each one exists to remove a specific way that data goes wrong: an update that changes one copy of a fact but not another, a fact you cannot record until some unrelated fact exists, or a fact that disappears when you delete something else.",
        "Denormalization deliberately reintroduces duplication to make reads cheaper. Both are tools; the interview question is always about the trade-off.",
    ],
    sections=[
        section(
            "Why normalize: the three anomalies",
            "Start with one wide table of trades that also records each trader&rsquo;s desk and each desk&rsquo;s head:",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("""CREATE TABLE trades_wide(
                    trade_id INT PRIMARY KEY, trader TEXT, desk TEXT, desk_head TEXT,
                    sym TEXT, qty INT)""")
                db.executemany("INSERT INTO trades_wide VALUES (?, ?, ?, ?, ?, ?)", [
                    (1, "ann", "rates",  "kim", "UST10Y", 5),
                    (2, "ann", "rates",  "kim", "UST2Y",  8),
                    (3, "bob", "equity", "lee", "AAPL",   100),
                ])

                # update anomaly: the rates desk gets a new head, but we only fix one row
                db.execute("UPDATE trades_wide SET desk_head = 'raj' WHERE trade_id = 1")
                print("rates desk heads:", db.execute(
                    "SELECT DISTINCT desk_head FROM trades_wide WHERE desk = 'rates'").fetchall())

                # deletion anomaly: bob's only trade is cancelled, and the equity desk vanishes
                db.execute("DELETE FROM trades_wide WHERE trade_id = 3")
                print("desks we know:   ", db.execute("SELECT DISTINCT desk FROM trades_wide").fetchall())
            ''', label="one fact, many copies"),
            "<strong>Update anomaly:</strong> a fact stored in many rows can be changed in some and not others, and the database now contradicts itself. <strong>Deletion anomaly:</strong> removing one fact (a trade) destroys an unrelated one (the equity desk exists and is run by Lee). <strong>Insertion anomaly:</strong> you cannot record a new desk and its head until someone on it trades.",
            "Each normal form below removes one class of dependency that causes these.",
        ),
        section(
            "1NF, 2NF and 3NF",
            table(
                ["Form", "Rule", "Violation looks like", "Fix"],
                [
                    ["<strong>1NF</strong>", "Every column holds one atomic value; no repeating groups", "<code>symbols = 'AAPL,MSFT'</code>, or <code>phone1, phone2, phone3</code>", "One row per value in a child table"],
                    ["<strong>2NF</strong>", "1NF, and no non-key column depends on only <em>part</em> of a composite key", "Key <code>(order_id, line_no)</code>, but <code>customer</code> depends on <code>order_id</code> alone", "Move it to a table keyed by <code>order_id</code>"],
                    ["<strong>3NF</strong>", "2NF, and no non-key column depends on another non-key column", "<code>trader &rarr; desk &rarr; desk_head</code>", "Move <code>desk_head</code> to a <code>desks</code> table"],
                ],
            ),
            "The memorable summary of 3NF: every non-key attribute depends on <em>the key, the whole key, and nothing but the key</em>. Applied to the table above, <code>desk</code> depends on <code>trader</code> and <code>desk_head</code> depends on <code>desk</code>, neither of which is the key:",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.executescript("""
                    CREATE TABLE desks  (desk TEXT PRIMARY KEY, desk_head TEXT);
                    CREATE TABLE traders(trader TEXT PRIMARY KEY, desk TEXT REFERENCES desks);
                    CREATE TABLE trades (trade_id INT PRIMARY KEY,
                                         trader TEXT REFERENCES traders, sym TEXT, qty INT);
                    INSERT INTO desks   VALUES ('rates', 'kim'), ('equity', 'lee');
                    INSERT INTO traders VALUES ('ann', 'rates'), ('bob', 'equity');
                    INSERT INTO trades  VALUES (1, 'ann', 'UST10Y', 5), (2, 'ann', 'UST2Y', 8),
                                               (3, 'bob', 'AAPL', 100);
                """)
                db.execute("UPDATE desks SET desk_head = 'raj' WHERE desk = 'rates'")   # one row
                db.execute("DELETE FROM trades WHERE trade_id = 3")

                for row in db.execute("""
                        SELECT t.trade_id, t.trader, d.desk, d.desk_head, t.sym
                        FROM trades t JOIN traders USING (trader) JOIN desks d USING (desk)"""):
                    print(row)
                print("desks we know:", db.execute("SELECT * FROM desks").fetchall())
            ''', label="the same data in 3NF: each fact stored once"),
            "The desk head changes in one place and every trade sees it; deleting Bob&rsquo;s trade leaves the equity desk intact. The cost is the two joins needed to reassemble the wide view.",
        ),
        section(
            "BCNF",
            "<strong>Boyce&ndash;Codd normal form</strong> tightens 3NF: for <em>every</em> non-trivial functional dependency X &rarr; Y, X must be a superkey. 3NF allows one exception &mdash; Y may be part of some candidate key &mdash; and that exception is where the remaining anomalies hide.",
            "The classic case: each instructor teaches exactly one course, and a student takes each course from one instructor. The table <code>(student, course, instructor)</code> has candidate keys <code>(student, course)</code> and <code>(student, instructor)</code>, and the dependency <code>instructor &rarr; course</code>. Every attribute is part of some key, so it is in 3NF; but <code>instructor</code> is not a superkey, so it violates BCNF, and &ldquo;which course does Dr. X teach&rdquo; is repeated for every student.",
            code(FD + '''
schema = {"student", "course", "instructor"}
fds = [(("student", "course"), ("instructor",)),
       (("instructor",), ("course",))]

print("candidate keys:", candidate_keys(schema, fds))
print("BCNF violations:", bcnf_violations(schema, fds))

# the trades example from above, before decomposition
wide = {"trade_id", "trader", "desk", "desk_head", "sym", "qty"}
wide_fds = [(("trade_id",), ("trader", "sym", "qty")),
            (("trader",), ("desk",)),
            (("desk",), ("desk_head",))]
print("trades_wide keys:", candidate_keys(wide, wide_fds))
for lhs, rhs in bcnf_violations(wide, wide_fds):
    print(f"  {lhs} -> {rhs}: left side is not a key")
''', label="finding keys and BCNF violations from functional dependencies"),
            "Decomposing into <code>(instructor, course)</code> and <code>(student, instructor)</code> reaches BCNF, but the dependency <code>(student, course) &rarr; instructor</code> can no longer be enforced within one table: nothing stops a student being enrolled with two instructors of the same course. That is the known trade-off &mdash; BCNF decomposition is always lossless, but not always dependency-preserving, whereas 3NF always can be both.",
            caveat("Higher forms exist (4NF removes multi-valued dependencies, 5NF join dependencies) but rarely come up outside a theory exam. In practice, reaching 3NF or BCNF and thinking clearly about any exceptions covers almost all real schemas."),
        ),
        section(
            "Denormalization and read-heavy systems",
            "Normalized schemas optimise for correct writes. Read-heavy systems often pay for that with joins and aggregations on every request, and denormalize deliberately:",
            table(
                ["Technique", "Example", "Kept correct by"],
                [
                    ["Duplicate a column", "Store <code>desk</code> on each trade row", "Application code, triggers, or accepting it as a historical snapshot"],
                    ["Precomputed aggregate", "A <code>positions</code> table updated on every fill instead of summing fills", "Updating it in the same transaction as the fill"],
                    ["Materialized view", "Daily P&amp;L per desk", "<code>REFRESH MATERIALIZED VIEW</code> (periodic) or incremental maintenance"],
                    ["Document / wide row", "Store an order with its fills as one JSON document", "Writing the whole document together"],
                    ["Separate read model (CQRS)", "Event stream feeds a search index or cache", "Asynchronous consumers; eventually consistent"],
                ],
            ),
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.executescript("""
                    CREATE TABLE fills(id INTEGER PRIMARY KEY, account INT, sym TEXT, qty INT);
                    CREATE TABLE positions(account INT, sym TEXT, qty INT, PRIMARY KEY (account, sym));
                    CREATE TRIGGER keep_positions AFTER INSERT ON fills BEGIN
                        INSERT INTO positions VALUES (NEW.account, NEW.sym, NEW.qty)
                        ON CONFLICT (account, sym) DO UPDATE SET qty = qty + NEW.qty;
                    END;
                """)
                db.executemany("INSERT INTO fills(account, sym, qty) VALUES (?, ?, ?)",
                               [(i % 100, f"S{i % 40}", (i % 7) * 10 - 20) for i in range(50_000)])

                def steps(sql):
                    n = 0
                    def tick():
                        nonlocal n
                        n += 1
                    db.set_progress_handler(tick, 1)
                    rows = db.execute(sql).fetchall()
                    db.set_progress_handler(None, 0)
                    return rows, n

                a, n1 = steps("SELECT sum(qty) FROM fills WHERE account = 7 AND sym = 'S7'")
                b, n2 = steps("SELECT qty FROM positions WHERE account = 7 AND sym = 'S7'")
                print(f"sum the fills:     {a[0][0]:>5}  ({n1:,} VM steps)")
                print(f"read the position: {b[0][0]:>5}  ({n2:,} VM steps)")
            ''', label="a position maintained on write vs. summed on read"),
            "The denormalized read is a single seek. The cost moved to the write path: every fill now also updates a position row (and contends on it, if many fills hit one account and symbol). This is the right trade whenever reads vastly outnumber writes, or when the read has a latency budget and the write does not.",
            note("Denormalize from a normalized design, not instead of one. Know which copy is the source of truth, how the others are kept in step, and what a reader sees while they are out of step."),
        ),
    ],
    questions=[
        question(
            "Explain 1NF, 2NF and 3NF with an example of a violation of each.",
            "medium",
            "<strong>1NF</strong>: every column holds a single atomic value and there are no repeating groups. Violation: an <code>orders</code> row with <code>items = 'AAPL:100,MSFT:50'</code>. Fix: an <code>order_items</code> table with one row per item.",
            "<strong>2NF</strong>: no non-key attribute depends on part of a composite key. Violation: <code>order_items(order_id, line_no, sym, qty, customer)</code> where <code>customer</code> depends only on <code>order_id</code>. Fix: move <code>customer</code> to <code>orders</code>.",
            "<strong>3NF</strong>: no non-key attribute depends on another non-key attribute (no transitive dependencies). Violation: <code>traders(trader, desk, desk_head)</code> where <code>desk_head</code> depends on <code>desk</code>. Fix: a <code>desks(desk, desk_head)</code> table.",
            "Each violation causes update, insert and delete anomalies; each fix stores the offending fact once.",
        ),
        question(
            "What is the difference between 3NF and BCNF? Give a table that is in 3NF but not BCNF.",
            "hard",
            "BCNF requires that for every non-trivial functional dependency X &rarr; Y, X is a superkey. 3NF relaxes this: the dependency is also allowed if every attribute of Y is part of some candidate key (a <em>prime</em> attribute).",
            "Example: <code>(student, course, instructor)</code> where each instructor teaches one course, and each student takes a course from one instructor. Dependencies: <code>(student, course) &rarr; instructor</code> and <code>instructor &rarr; course</code>. Candidate keys: <code>(student, course)</code> and <code>(student, instructor)</code>. <code>instructor &rarr; course</code> has a non-superkey on the left, but <code>course</code> is prime, so it is 3NF and not BCNF. The anomaly: the fact &ldquo;Dr. X teaches Databases&rdquo; is repeated for every student of Dr. X.",
            "Decomposing to <code>(instructor, course)</code> and <code>(student, instructor)</code> gives BCNF but loses the ability to enforce <code>(student, course) &rarr; instructor</code> in a single table. That trade-off, lossless but not dependency-preserving, is the point interviewers want you to make.",
        ),
        question(
            "When would you denormalize, and how do you keep denormalized data consistent?",
            "medium",
            "When a read path is hot and latency-sensitive and the normalized form requires expensive joins or aggregations on every request &mdash; positions derived from millions of fills, a dashboard summing a day&rsquo;s trades, a product page assembled from ten tables. Also when data is naturally read together and rarely changes independently (an order with its line items as one document).",
            "Keeping it consistent, from strongest to weakest: update the copy in the same transaction as the source (triggers or application code), so they can never disagree; maintain it from the change stream (CDC, outbox pattern) and accept a short lag; or rebuild it periodically (materialized view refresh, batch job) and accept staleness up to the interval. Always keep one copy as the source of truth, and be able to rebuild the others from it.",
        ),
        question(
            "Is storing a JSON array of tags in one column a violation of 1NF? When is it acceptable?",
            "hard",
            "By the textbook definition, yes: the column holds a collection, not an atomic value. The practical question is what you do with it. If the database treats the array as an opaque value that is always read and written whole, the anomalies 1NF guards against do not arise, and one column is simpler and faster than a child table. If you query into it (&ldquo;all orders tagged <code>hedge</code>&rdquo;), update single elements, or need referential integrity for the elements, the child table wins: you get indexes, constraints and normal SQL.",
            "Modern engines blur the line. PostgreSQL <code>jsonb</code> with a GIN index, or native arrays with <code>@&gt;</code>, make containment queries on a JSON column indexable. So the defensible answer is: acceptable for data that is read as a unit and not a target of relational constraints; use a table when elements have identity, relationships or independent updates.",
        ),
    ],
    refs=[
        ("Codd — A Relational Model of Data for Large Shared Data Banks", "https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf"),
        ("Kent — A Simple Guide to Five Normal Forms in Relational Database Theory", "https://www.bkent.net/Doc/simple5.htm"),
        ("PostgreSQL: materialized views", "https://www.postgresql.org/docs/current/rules-materializedviews.html"),
        ("SQLite: UPSERT", "https://www.sqlite.org/lang_upsert.html"),
    ],
)
