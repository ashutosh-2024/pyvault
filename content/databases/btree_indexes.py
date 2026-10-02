from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="btree-indexes",
    title="B-Tree and B+ Tree Indexes",
    summary="Why every index is a wide, shallow, sorted tree, and when the planner ignores it.",
    intro=[
        "Almost every index you will create in a relational database is a B+ tree. PostgreSQL, MySQL/InnoDB, SQLite, SQL Server and Oracle all default to one. Understanding its shape explains nearly every indexing rule of thumb you have been told: why a lookup in a billion-row table touches three or four pages, why column order in a composite index matters, why <code>LIKE '%foo'</code> cannot use an index, and why an index on a boolean column is usually useless.",
        "The examples use SQLite from the standard library. Its <code>EXPLAIN QUERY PLAN</code> output is the real plan chosen by the engine that ran the snippet, so what you see is what the optimizer actually decided.",
    ],
    sections=[
        section(
            "How a B+ tree works",
            "A B+ tree is a balanced search tree in which every node is one <strong>page</strong> &mdash; typically 4, 8 or 16&nbsp;KB &mdash; and holds hundreds of keys, not two. Interior nodes hold only separator keys and child pointers. All the actual entries live in the <strong>leaves</strong>, which are kept in key order and linked to their neighbours.",
            "Insertion goes to the correct leaf. When a leaf overflows it splits in half and pushes one separator key up to its parent; if the parent overflows it splits too. The tree only grows taller when the root splits, so every leaf is always at the same depth. That is the &ldquo;balanced&rdquo; guarantee: no insertion order can produce a degenerate, list-shaped tree.",
            code('''
                import bisect

                ORDER = 4  # max keys per node; real engines fit hundreds per page

                class Node:
                    def __init__(self, leaf):
                        self.leaf, self.keys, self.kids, self.next = leaf, [], [], None

                def insert(node, key):
                    """Insert key below node; return (separator, new_right_node) on split."""
                    if node.leaf:
                        bisect.insort(node.keys, key)
                    else:
                        i = bisect.bisect_right(node.keys, key)
                        split = insert(node.kids[i], key)
                        if split:
                            sep, right = split
                            node.keys.insert(i, sep)
                            node.kids.insert(i + 1, right)
                    if len(node.keys) <= ORDER:
                        return None
                    mid = len(node.keys) // 2
                    right = Node(node.leaf)
                    if node.leaf:                      # leaves keep the separator key
                        right.keys, node.keys = node.keys[mid:], node.keys[:mid]
                        right.next, node.next = node.next, right
                        return right.keys[0], right
                    sep = node.keys[mid]               # interior nodes push it up
                    right.keys, node.keys = node.keys[mid + 1:], node.keys[:mid]
                    right.kids, node.kids = node.kids[mid + 1:], node.kids[:mid + 1]
                    return sep, right

                root = Node(leaf=True)
                for k in range(1, 21):
                    split = insert(root, k)
                    if split:                          # root split: tree grows one level
                        new = Node(leaf=False)
                        new.keys, new.kids = [split[0]], [root, split[1]]
                        root = new

                level = [root]
                while level:
                    print("   ".join(str(n.keys) for n in level))
                    level = [] if level[0].leaf else [k for n in level for k in n.kids]

                leaf = root
                while not leaf.leaf:
                    leaf = leaf.kids[0]
                chain = []
                while leaf:
                    chain += leaf.keys
                    leaf = leaf.next
                print("leaf chain:", chain)
            ''', label="a tiny B+ tree, inserting 1..20 in order"),
            "Two things to notice. Every leaf is at the same depth. And the leaves form a sorted linked list, so a range query (<code>BETWEEN 7 AND 15</code>) descends once to find 7 and then walks sideways, never going back up the tree.",
            note("A B+ tree lookup costs one page read per level. The whole design is about keeping the number of levels tiny."),
        ),
        section(
            "Why databases use them",
            "Disks and SSDs read whole pages, and a page read costs far more than anything the CPU does with the page afterwards. A binary search tree with one key per node would need about 30 page reads to find one row among a billion. A B+ tree with a few hundred keys per page needs three or four, and the top one or two levels are almost always already cached in memory.",
            code('''
                import math

                for fanout in (2, 100, 500):
                    for rows in (10**6, 10**9):
                        levels = math.ceil(math.log(rows, fanout))
                        print(f"fanout {fanout:>3}, {rows:>13,} rows -> {levels:>2} levels")
            ''', label="height = log base fanout of rows"),
            "With 8&nbsp;KB pages and 8-byte keys plus 8-byte pointers, one interior page holds around 500 children, so a billion keys fit in four levels. The root and second level (500 pages, 4&nbsp;MB) stay resident in the buffer pool, so a lookup usually costs one or two actual I/Os.",
            table(
                ["Structure", "Point lookup", "Range scan", "Why it loses"],
                [
                    ["B+ tree", "O(log<sub>F</sub> n) pages, F in the hundreds", "Descend once, walk leaves", "&mdash; (the default for a reason)"],
                    ["Hash index", "O(1) expected", "Impossible: no order", "No ranges, no <code>ORDER BY</code>, no prefix match"],
                    ["Binary search tree", "O(log<sub>2</sub> n) pages", "In-order walk", "One key per node means ~30 page reads for a billion rows"],
                    ["Sorted array", "O(log n)", "Excellent", "Every insert shifts half the file"],
                    ["LSM tree", "Several structures to check", "Merge several runs", "Better for write-heavy workloads; see the internals page"],
                ],
            ),
            "Why B+ rather than plain B-tree? In a classic B-tree, interior nodes also carry values. Moving all values to the leaves makes interior nodes smaller, so fanout goes up and the tree gets shorter, and the linked leaf level makes range scans a sequential walk.",
        ),
        section(
            "Clustered vs non-clustered indexes",
            "A <strong>clustered</strong> index stores the table rows themselves in its leaves, in key order. There can be only one, because the rows can only be physically sorted one way. A <strong>non-clustered</strong> (secondary) index stores the key plus a pointer back to the row. Looking up a row through a secondary index is therefore two searches: find the pointer, then fetch the row.",
            table(
                ["Engine", "Table storage", "What a secondary index leaf points to"],
                [
                    ["MySQL InnoDB", "Clustered on the primary key", "The primary key value (so a second B+ tree descent)"],
                    ["SQL Server", "Clustered index optional; otherwise a heap", "Clustering key, or a row ID for heaps"],
                    ["PostgreSQL", "Unordered heap; no clustered index", "A physical tuple ID (page, slot)"],
                    ["SQLite", "Clustered on <code>rowid</code> (or on the PK for <code>WITHOUT ROWID</code>)", "The <code>rowid</code>"],
                ],
            ),
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, customer INT, amount REAL)")
                db.execute("CREATE INDEX ix_customer ON orders(customer)")

                def plan(sql):
                    for row in db.execute("EXPLAIN QUERY PLAN " + sql):
                        print(f"{sql:<45} -> {row[3]}")

                plan("SELECT * FROM orders WHERE id = 42")
                plan("SELECT * FROM orders WHERE customer = 7")
            ''', label="the clustered key vs a secondary index"),
            "The first query searches the table's own B+ tree directly. The second searches <code>ix_customer</code>, gets back rowids, and then does a second search into the table for each one.",
            "Consequences worth knowing: in InnoDB, a wide primary key (say, a UUID string) is copied into every secondary index, bloating all of them. Random primary keys such as UUIDv4 scatter inserts across the whole clustered tree, causing page splits and poor cache locality, where an auto-increment key always appends to the rightmost leaf.",
            caveat("PostgreSQL&rsquo;s <code>CLUSTER</code> command physically reorders a heap once but does not maintain the order afterwards, so it is not a clustered index in the InnoDB sense."),
        ),
        section(
            "Composite indexes and the leftmost-prefix rule",
            "An index on <code>(customer, status)</code> is sorted by <code>customer</code> first, and by <code>status</code> only within equal customers &mdash; exactly like a phone book sorted by surname, then first name. It can answer anything that constrains a <em>leftmost prefix</em> of its columns, and nothing that skips the first one.",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, customer INT, status TEXT, amount REAL)")
                db.execute("CREATE INDEX ix_cust_status ON orders(customer, status)")

                for where in ("customer = 7",
                              "customer = 7 AND status = 'open'",
                              "customer > 100",
                              "status = 'open'"):
                    plan = db.execute(f"EXPLAIN QUERY PLAN SELECT * FROM orders WHERE {where}").fetchone()[3]
                    print(f"{where:<35} {plan}")
            ''', label="which predicates can use (customer, status)?"),
            "The last query cannot seek: <code>'open'</code> orders are scattered across every customer&rsquo;s section of the index, so the engine scans the table.",
            "Column order rules of thumb:",
            "<strong>Equality columns first, range column last.</strong> With <code>WHERE a = ? AND b &gt; ?</code>, an index on <code>(a, b)</code> seeks to <code>a</code> and then scans a contiguous range of <code>b</code>. An index on <code>(b, a)</code> scans the whole <code>b</code> range and filters <code>a</code> row by row.<br><strong>Only one range per index is useful.</strong> After the first range column, later columns are no longer sorted within the range.<br><strong>Match the <code>ORDER BY</code>.</strong> <code>WHERE a = ? ORDER BY b</code> on <code>(a, b)</code> reads rows already sorted and skips the sort entirely.",
            caveat("Some engines (Oracle, MySQL 8, PostgreSQL 18) can do a <em>skip scan</em>: when the leading column has few distinct values, they seek once per distinct value. It rescues some queries that skip the first column, but only when that column&rsquo;s cardinality is low."),
        ),
        section(
            "Selectivity: when the planner decides an index is worse",
            "<strong>Selectivity</strong> is the fraction of rows a predicate matches. <code>email = ?</code> on a unique column matches one row in a million; <code>status = 'open'</code> may match a third of the table. An index is a win when it lets the engine skip most of the table. It is a loss when it doesn&rsquo;t, because each match through a secondary index is a <em>random</em> page read, while a full scan reads pages <em>sequentially</em> and gets every row on each page.",
            code('''
                ROWS, ROWS_PER_PAGE = 1_000_000, 100
                PAGES = ROWS // ROWS_PER_PAGE
                RANDOM, SEQUENTIAL = 4.0, 1.0          # PostgreSQL's default cost ratio

                full_scan = PAGES * SEQUENTIAL
                print(f"full scan: {full_scan:>9,.0f}")
                for fraction in (0.0001, 0.001, 0.0025, 0.005, 0.01, 0.1, 0.33):
                    via_index = ROWS * fraction * RANDOM   # worst case: one page per match
                    winner = "index" if via_index < full_scan else "scan"
                    print(f"match {fraction:>7.2%}: {via_index:>9,.0f}  -> {winner}")
            ''', label="a crude cost model: random page reads vs one sequential pass"),
            "In this worst case &mdash; every match on a different page &mdash; the crossover is a quarter of a percent. Real data is kinder: matching rows often share pages, and hot pages are cached, so in practice the crossover for a row store usually lands somewhere between a fraction of a percent and a few percent. The shape is the point: past a small fraction of the table, the scan wins. That is why an index on a low-cardinality column (boolean flags, status enums, gender) rarely gets used for equality lookups on its own &mdash; unless the value you query is rare (<code>WHERE status = 'failed'</code> when 0.1% fail). The optimizer knows the difference only if it has statistics, which is what <code>ANALYZE</code> collects.",
            "<strong>Partial indexes</strong> exploit exactly this: <code>CREATE INDEX ... WHERE status = 'failed'</code> indexes only the rare rows, so the index is tiny and always selective.",
            caveat("SQLite&rsquo;s planner is much simpler than PostgreSQL&rsquo;s and will often still use an index for a 33%-selective predicate. PostgreSQL and MySQL cost the plans and switch to a sequential scan. The crossover also shifts on SSDs, where random reads are cheaper; tuning <code>random_page_cost</code> down toward 1.1 tells PostgreSQL so."),
        ),
        section(
            "Covering indexes and index-only scans",
            "If every column a query needs is already in the index, the engine never has to visit the table at all. That is a <strong>covering index</strong>, and the resulting plan is an <strong>index-only scan</strong>. It removes the second lookup per row, which is often most of the cost.",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, customer INT, status TEXT, amount REAL)")
                db.execute("CREATE INDEX ix_cust_status ON orders(customer, status)")

                for sql in ("SELECT * FROM orders WHERE customer = 7",
                            "SELECT status FROM orders WHERE customer = 7",
                            "SELECT count(*) FROM orders WHERE customer = 7",
                            "SELECT id, status FROM orders WHERE customer = 7",
                            "SELECT amount FROM orders WHERE customer = 7"):
                    print(f"{sql:<50} {db.execute('EXPLAIN QUERY PLAN ' + sql).fetchone()[3]}")
            '''),
            "Note that <code>id</code> is covered for free: SQLite secondary indexes carry the rowid, just as InnoDB&rsquo;s carry the primary key. Adding <code>amount</code> as a trailing column (or, in PostgreSQL and SQL Server, via <code>INCLUDE (amount)</code>, which stores it in the leaves without making it part of the sort key) would cover the last query too.",
            caveat("PostgreSQL can only return rows from an index-only scan if the heap page is marked all-visible in the <em>visibility map</em>, because MVCC visibility information lives in the heap, not in the index. On a table that has not been vacuumed recently, an &ldquo;index-only&rdquo; scan still visits the heap for many rows. <code>EXPLAIN ANALYZE</code> reports this as <code>Heap Fetches</code>."),
        ),
        section(
            "When an index is not used",
            "An index is sorted by the raw column value. Anything that stops the engine from turning your predicate into &ldquo;seek to this key, walk to that key&rdquo; forces a scan.",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT, age INT, city TEXT)")
                db.execute("CREATE INDEX ix_email ON users(email)")
                db.execute("CREATE INDEX ix_age ON users(age)")

                for where in ("email = 'a@x.com'",
                              "lower(email) = 'a@x.com'",
                              "email LIKE '%@x.com'",
                              "age + 1 = 30",
                              "age = 29 OR city = 'Paris'"):
                    plan = db.execute(f"EXPLAIN QUERY PLAN SELECT * FROM users WHERE {where}").fetchone()[3]
                    print(f"{where:<28} {plan}")

                db.execute("CREATE INDEX ix_email_lower ON users(lower(email))")
                plan = db.execute("EXPLAIN QUERY PLAN SELECT * FROM users WHERE lower(email) = 'a@x.com'").fetchone()[3]
                print(f"{'lower(email) = ... (indexed)':<28} {plan}")
            ''', label="the classic index killers"),
            table(
                ["Pattern", "Why it cannot seek", "Fix"],
                [
                    ["<code>f(col) = ?</code>", "The index is sorted by <code>col</code>, not <code>f(col)</code>", "Expression index, or rewrite (<code>col &gt;= '2026-01-01' AND col &lt; '2026-02-01'</code> instead of <code>year(col)=2026</code>)"],
                    ["<code>LIKE '%foo'</code>", "No fixed prefix to seek to", "Trigram / full-text index, or store the reversed string"],
                    ["Implicit type cast (<code>varchar_col = 123</code>)", "The engine casts every row&rsquo;s column", "Compare with a value of the column&rsquo;s type"],
                    ["<code>a = ? OR b = ?</code>", "One index cannot serve both halves", "Index both and let the engine union them, or rewrite as <code>UNION</code>"],
                    ["Low selectivity", "Cheaper to scan (previous section)", "Partial index on the rare value"],
                    ["Tiny table", "The whole table is one or two pages", "Nothing; the scan is correct"],
                    ["Stale statistics", "The planner misjudges row counts", "<code>ANALYZE</code>"],
                ],
            ),
            note("Every index also costs something: it slows every <code>INSERT</code>, <code>DELETE</code> and every <code>UPDATE</code> of its columns, and competes for buffer-pool memory. Index for the queries you run, not the columns you have."),
        ),
    ],
    questions=[
        question(
            "Why do databases use B+ trees instead of hash tables or binary search trees for indexes?",
            "medium",
            "Because the cost that matters is page reads, not comparisons. A B+ tree node is a whole page with hundreds of keys, so the tree has fanout in the hundreds and height 3&ndash;4 for billions of rows; the upper levels stay in cache and a lookup typically costs one or two I/Os. A binary tree has fanout 2 and would need around 30 page reads.",
            "A hash index gives O(1) point lookups but no ordering: it cannot serve ranges, <code>ORDER BY</code>, <code>MIN/MAX</code>, or prefix matches, and it degrades when it needs rehashing. The B+ tree&rsquo;s sorted, linked leaf level serves all of those with one descent followed by a sequential walk.",
            "Moving values out of interior nodes (B+ rather than B) maximises fanout, and balancing by splitting upward guarantees every leaf sits at the same depth, so worst-case latency is predictable.",
        ),
        question(
            "You have an index on <code>(last_name, first_name)</code>. Which of these queries can use it: <code>WHERE first_name = ?</code>, <code>WHERE last_name = ? ORDER BY first_name</code>, <code>WHERE last_name LIKE 'Sm%'</code>, <code>WHERE last_name &gt; 'M' AND first_name = 'Al'</code>?",
            "medium",
            "<strong><code>first_name = ?</code></strong> &mdash; no seek. It skips the leading column. (A skip scan can help if <code>last_name</code> had few distinct values; it does not.)<br><strong><code>last_name = ? ORDER BY first_name</code></strong> &mdash; yes, and the sort disappears: within one last name the entries are already ordered by first name.<br><strong><code>LIKE 'Sm%'</code></strong> &mdash; yes, as a range <code>'Sm' &lt;= last_name &lt; 'Sn'</code> (subject to collation rules).<br><strong><code>last_name &gt; 'M' AND first_name = 'Al'</code></strong> &mdash; partly. It seeks to <code>'M'</code> and scans every later last name; <code>first_name</code> can only be checked as a filter on each index entry, because after a range column the next column is not sorted.",
        ),
        question(
            "A query filters on an indexed column but the plan shows a full table scan. Walk through the possible reasons.",
            "hard",
            "Work through them in rough order of likelihood:",
            "<strong>1. It is cheaper.</strong> The predicate matches a large fraction of rows, so random heap fetches cost more than one sequential pass. Check estimated vs actual rows in <code>EXPLAIN ANALYZE</code>.<br><strong>2. Statistics are wrong.</strong> After a bulk load the planner may think the table is tiny or the value is common. Run <code>ANALYZE</code>.<br><strong>3. The predicate is not sargable.</strong> A function or arithmetic on the column, a leading wildcard, or an implicit cast (comparing a text column to an integer parameter is the common ORM bug).<br><strong>4. Collation or type mismatch.</strong> The index was built with a different collation or operator class than the comparison uses.<br><strong>5. Wrong column order.</strong> The query does not constrain the index&rsquo;s leading column.<br><strong>6. Parameterised generic plan.</strong> A prepared statement may use a plan built for a &ldquo;typical&rdquo; parameter, not this one.<br><strong>7. <code>OR</code> across columns</strong> that no single index serves.",
            "The fix is chosen from the cause: rewrite the predicate, add an expression or partial index, refresh statistics, or fix the parameter type.",
        ),
        question(
            "What is a covering index, and what is the catch with index-only scans in PostgreSQL?",
            "hard",
            "A covering index contains every column the query reads &mdash; the filter columns as key columns and the rest either as trailing key columns or as <code>INCLUDE</code> payload. The engine can then answer from the index alone, skipping the per-row lookup into the table, which is usually the dominant cost of an index plan.",
            "The PostgreSQL catch is MVCC. Row visibility (which transaction created or deleted a version) lives in the heap tuple, not in the index. An index-only scan can skip the heap only for pages the <em>visibility map</em> marks all-visible, which <code>VACUUM</code> maintains. On a heavily updated table the map is mostly unset, so the &ldquo;index-only&rdquo; scan still fetches most heap pages. <code>EXPLAIN (ANALYZE)</code> shows the damage as <code>Heap Fetches</code>; the fix is more aggressive autovacuum on that table.",
            "The general costs still apply: a wider index is slower to write and takes more cache.",
        ),
        question(
            "Why is a random UUID a poor clustered primary key in InnoDB, and what would you use instead?",
            "hard",
            "InnoDB stores rows in primary-key order. Sequential keys always insert into the rightmost leaf, which stays hot in the buffer pool, and full pages are left 15/16 full. Random UUIDv4 keys insert into a random leaf each time: the working set becomes the entire index, most inserts miss the cache and read a page from disk, and pages split in the middle and are left about half full, so the table ends up much larger.",
            "It also hurts every secondary index, because each secondary entry stores the primary key &mdash; a 36-byte string instead of an 8-byte integer.",
            "Use an auto-increment <code>BIGINT</code>, or a time-ordered identifier such as UUIDv7 or a Snowflake-style ID if you need globally unique IDs generated without coordination. Stored as <code>BINARY(16)</code> rather than text, a UUIDv7 keeps nearly the locality of an auto-increment key.",
        ),
    ],
    refs=[
        ("SQLite: query planning", "https://www.sqlite.org/queryplanner.html"),
        ("SQLite: EXPLAIN QUERY PLAN", "https://www.sqlite.org/eqp.html"),
        ("PostgreSQL: index-only scans and covering indexes", "https://www.postgresql.org/docs/current/indexes-index-only-scans.html"),
        ("MySQL: clustered and secondary indexes", "https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html"),
        ("Use The Index, Luke", "https://use-the-index-luke.com/"),
    ],
)
