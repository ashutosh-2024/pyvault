from deepdive._blocks import code, table, note, caveat, section, question

# Shared setup pasted into several snippets: a 100k-row trades table and a
# helper that counts SQLite virtual-machine instructions executed by a query,
# a deterministic stand-in for "how much work did this take".
SETUP = '''
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, px REAL, qty INT, ts INT)")
db.executemany("INSERT INTO trades(sym, px, qty, ts) VALUES (?, ?, ?, ?)",
               [(f"S{i % 500}", i % 97, i % 13, i) for i in range(100_000)])

def steps(sql, args=(), every=1):
    """Run sql; return (VM instructions executed, to the nearest `every`; rows returned)."""
    n = 0
    def tick():
        nonlocal n
        n += every
    db.set_progress_handler(tick, every)
    rows = db.execute(sql, args).fetchall()
    db.set_progress_handler(None, 0)
    return n, len(rows)
'''

TOPIC = dict(
    id="query-execution",
    title="Query Execution and the Optimizer",
    summary="Parsing, planning, scans, the three join algorithms, reading EXPLAIN, and why innocent queries crawl.",
    intro=[
        "SQL says <em>what</em> you want, never <em>how</em> to get it. Between your query and the data sits a planner that chooses among many equivalent programs &mdash; which index, which join order, which join algorithm &mdash; using statistics that may be stale. Most &ldquo;the database is slow&rdquo; incidents are a bad plan, and most bad plans can be read straight off <code>EXPLAIN</code>.",
        "To measure work without relying on timings, several snippets count the SQLite virtual-machine instructions a query executes, via the connection&rsquo;s progress handler. It is deterministic and tracks rows touched closely.",
    ],
    sections=[
        section(
            "Parsing, planning, execution",
            table(
                ["Stage", "Does", "Output"],
                [
                    ["Parse", "Tokenise and check grammar", "Syntax tree"],
                    ["Bind / analyse", "Resolve names against the catalog, check types and permissions", "Query tree with resolved tables and columns"],
                    ["Rewrite", "Expand views, apply rules, flatten simple subqueries", "Equivalent, simpler query tree"],
                    ["Plan / optimise", "Enumerate access paths, join orders and algorithms; estimate the cost of each", "The cheapest physical plan it found"],
                    ["Execute", "Run the plan as a tree of operators pulling rows from their children", "Result rows"],
                ],
            ),
            "Most engines execute the plan with the <strong>iterator (Volcano) model</strong>: every operator has <code>next()</code>, and asking the root for a row makes it ask its children, down to the scans. Analytical engines instead pass batches of a thousand-odd values between operators (vectorised execution), or compile the plan to machine code.",
            "SQLite compiles the plan into bytecode for its own virtual machine, and <code>EXPLAIN</code> (without <code>QUERY PLAN</code>) shows that program. A primary-key lookup is a handful of instructions:",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, px REAL)")
                for addr, op, p1, p2, p3, *_ in db.execute("EXPLAIN SELECT px FROM trades WHERE id = 7"):
                    print(f"{addr:>2} {op:<12} {p1:>2} {p2:>2} {p3:>2}")
            ''', label="the compiled program for a point lookup"),
            "Read it top to bottom: open a read cursor on the table, load the constant 7, <code>SeekRowid</code> (jump to the end if absent), read column 2, emit a result row, halt. The planning already happened; this is what it produced.",
            "Parsing and planning are not free. For short OLTP queries planning can cost as much as execution, which is why drivers use <strong>prepared statements</strong>: parse and plan once, execute many times with different parameters.",
        ),
        section(
            "The query optimizer",
            "A cost-based optimizer estimates, for each candidate plan, how many rows flow through each operator and what that costs in page reads and CPU. The estimates come from <strong>statistics</strong>: row counts, distinct values per column, most-common values, histograms. It then picks the cheapest.",
            "The difficult parts are well known:",
            "<strong>Cardinality estimation.</strong> Estimating the row count after a filter or join is the whole game, and errors multiply through a plan. The classic mistake is assuming columns are independent: <code>city = 'Paris' AND country = 'FR'</code> is estimated as P(Paris) &times; P(FR), far too low.<br><strong>Join ordering.</strong> <em>n</em> tables can be joined in <em>n</em>! orders, times a choice of algorithm per join. PostgreSQL searches exhaustively with dynamic programming up to 12 tables (<code>geqo_threshold</code>) and switches to a genetic algorithm beyond that.<br><strong>Stale statistics.</strong> After a bulk load the planner may still think the table is empty.",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, side INT, account INT)")
                db.executemany("INSERT INTO orders(side, account) VALUES (?, ?)",
                               [(i % 2, i % 1000) for i in range(20_000)])
                db.execute("CREATE INDEX ix_account ON orders(account)")   # 1,000 distinct values
                db.execute("CREATE INDEX ix_side ON orders(side)")         # 2 distinct values

                sql = "SELECT * FROM orders WHERE side = 1 AND account = 7"
                print("no stats:  ", db.execute("EXPLAIN QUERY PLAN " + sql).fetchone()[3])
                db.execute("ANALYZE")
                for row in db.execute("SELECT idx, stat FROM sqlite_stat1 ORDER BY idx"):
                    print("stat1:     ", row)
                print("with stats:", db.execute("EXPLAIN QUERY PLAN " + sql).fetchone()[3])
            ''', label="statistics change the choice"),
            "Without statistics both indexes look the same to SQLite &mdash; an equality match on either is assumed to return a few rows &mdash; and it picks <code>ix_side</code>, which matches 10,000 rows. <code>ANALYZE</code> records each table&rsquo;s row count and the average rows per distinct key (<code>'20000 10000'</code> vs <code>'20000 20'</code>), and the planner switches to the index that narrows the search to 20 rows.",
            "Averages have a blind spot: skew. If one account had half of all orders, &ldquo;20 rows per account&rdquo; would badly mislead the planner for that account. Histograms and most-common-value lists (PostgreSQL&rsquo;s <code>pg_stats</code>) exist to catch exactly that.",
            caveat("SQLite&rsquo;s optimizer is deliberately simple and only builds <code>sqlite_stat4</code> histograms when compiled with <code>SQLITE_ENABLE_STAT4</code>. PostgreSQL, SQL Server and Oracle keep per-value frequencies and histograms by default, and PostgreSQL can be told about correlated columns with <code>CREATE STATISTICS</code>."),
        ),
        section(
            "Sequential scan vs index scan",
            "A <strong>sequential scan</strong> reads every page of the table in physical order. An <strong>index scan</strong> descends the index and, for each match, fetches the row. PostgreSQL adds a middle option, the <strong>bitmap scan</strong>: collect all matching row locations from the index, sort them by page, then read each needed page once in order &mdash; turning random reads into mostly sequential ones.",
            code(SETUP + '''
db.execute("CREATE INDEX ix_sym ON trades(sym)")

for label, sql, args in [
    ("seek by primary key", "SELECT * FROM trades WHERE id = ?", (5000,)),
    ("scan: ts not indexed", "SELECT * FROM trades WHERE ts = ?", (5000,)),
    ("index on sym, 200 hits", "SELECT * FROM trades WHERE sym = ?", ("S7",)),
    ("full scan, 200 hits", "SELECT * FROM trades NOT INDEXED WHERE sym = ?", ("S7",)),
]:
    n, rows = steps(sql, args)
    print(f"{label:<24} {rows:>4} rows  {n:>8,} VM steps")
''', label="work done for the same result, with and without an access path"),
            "The seek touches a few pages regardless of table size. The scan&rsquo;s cost is proportional to the table. Neither is always right: the scan wins when a large fraction of rows match, which the indexing page covers under selectivity.",
        ),
        section(
            "Join algorithms",
            "Every relational engine implements joins with three algorithms. Knowing when each wins is a standard interview question.",
            code('''
                import random

                random.seed(7)
                orders = [(i, random.randrange(200)) for i in range(2_000)]      # (order_id, cust_id)
                customers = [(c, f"cust{c}") for c in range(200)]                 # (cust_id, name)

                def nested_loop(outer, inner):
                    out, cmp = [], 0
                    for o in outer:
                        for c in inner:
                            cmp += 1
                            if o[1] == c[0]:
                                out.append((o[0], c[1]))
                    return out, cmp

                def hash_join(build, probe):
                    table, work = {}, 0
                    for c in build:                        # build: hash the smaller input
                        table.setdefault(c[0], []).append(c)
                        work += 1
                    out = []
                    for o in probe:                        # probe: one lookup per row
                        work += 1
                        for c in table.get(o[1], ()):
                            out.append((o[0], c[1]))
                    return out, work

                def merge_join(left, right):              # both sorted on the key
                    out, i, j, work = [], 0, 0, 0
                    while i < len(left) and j < len(right):
                        work += 1
                        if left[i][1] < right[j][0]:
                            i += 1
                        elif left[i][1] > right[j][0]:
                            j += 1
                        else:
                            out.append((left[i][0], right[j][1]))
                            i += 1                         # customers key is unique
                    return out, work

                a, n1 = nested_loop(orders, customers)
                b, n2 = hash_join(customers, orders)
                c, n3 = merge_join(sorted(orders, key=lambda o: o[1]), customers)
                print("same result:", sorted(a) == sorted(b) == sorted(c), len(a), "rows")
                print(f"nested loop  {n1:>9,} comparisons")
                print(f"hash join    {n2:>9,} inserts + probes")
                print(f"merge join   {n3:>9,} steps (plus the cost of sorting)")
            ''', label="the three algorithms on 2,000 orders x 200 customers"),
            table(
                ["Algorithm", "Cost", "Wins when", "Needs"],
                [
                    ["Nested loop", "O(N &times; M); O(N log M) with an index on the inner side", "Outer side is small, and the inner side has an index on the join key &mdash; the typical OLTP join", "Nothing; works for any condition, including <code>&lt;</code> and <code>LIKE</code>"],
                    ["Hash join", "O(N + M)", "Large, unsorted inputs with an equality condition; the smaller side fits in memory", "Equi-join; memory for the hash table (spills to disk in partitions if not)"],
                    ["Merge join", "O(N + M) once sorted; O(N log N) to sort", "Both inputs are already sorted on the key (from an index or an earlier sort); very large inputs", "Sorted inputs; equality or range conditions"],
                ],
            ),
            "The <strong>index nested-loop join</strong> deserves emphasis: for each of a few outer rows, seek into an index on the inner table. It is why &ldquo;index your foreign keys&rdquo; is standard advice, and it is the only join SQLite has &mdash; when there is no suitable index, SQLite builds a temporary one for the duration of the query:",
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, qty INT)")
                db.execute("CREATE TABLE syms(sym TEXT, sector TEXT)")
                sql = ("SELECT s.sector, sum(t.qty) FROM trades t JOIN syms s ON s.sym = t.sym "
                       "GROUP BY s.sector")
                for row in db.execute("EXPLAIN QUERY PLAN " + sql):
                    print(row[3])
            ''', label="no index on the join key: SQLite makes one on the fly"),
        ),
        section(
            "Reading EXPLAIN",
            "<code>EXPLAIN</code> shows the plan the optimizer chose; <code>EXPLAIN ANALYZE</code> (PostgreSQL, MySQL 8) also <em>runs</em> the query and reports what actually happened at each node. The single most useful thing to do with the output is compare <strong>estimated rows</strong> with <strong>actual rows</strong> node by node. Where they diverge by orders of magnitude, the planner was working blind, and every decision above that node is suspect.",
            table(
                ["You see", "It means", "Look at"],
                [
                    ["<code>Seq Scan</code> / <code>SCAN</code> on a big table with a selective filter", "No usable index, or the planner thinks the filter is not selective", "Missing index, non-sargable predicate, stale stats"],
                    ["Estimated 1 row, actual 100,000", "Cardinality misestimate", "<code>ANALYZE</code>, correlated columns, skewed values"],
                    ["<code>Nested Loop</code> with a large outer side and a scan inside", "Quadratic join", "Index on the inner join key, or why a hash join was not chosen"],
                    ["<code>Sort</code> with <code>external merge Disk</code>", "Sort spilled to disk", "<code>work_mem</code>, or an index that returns rows in order"],
                    ["<code>USE TEMP B-TREE FOR ORDER BY</code> (SQLite)", "Explicit sort step", "An index matching the <code>ORDER BY</code>"],
                    ["<code>Rows Removed by Filter</code> is huge", "Rows read then thrown away", "A better index or column order"],
                    ["<code>Heap Fetches</code> on an index-only scan", "Visibility map not up to date", "Vacuum"],
                    ["<code>CORRELATED SCALAR SUBQUERY</code>", "Subquery runs once per outer row", "Rewrite as a join or <code>EXISTS</code>"],
                ],
            ),
            code('''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, qty INT, ts INT)")
                db.execute("CREATE TABLE syms(sym TEXT PRIMARY KEY, sector TEXT)")
                db.execute("CREATE INDEX ix_trades_sym ON trades(sym)")
                sql = """
                    SELECT s.sector, count(*) AS n
                    FROM syms s JOIN trades t ON t.sym = s.sym
                    WHERE t.ts > 1000
                      AND s.sym IN (SELECT sym FROM trades GROUP BY sym HAVING sum(qty) > 100)
                    GROUP BY s.sector
                    ORDER BY n DESC
                """
                depth = {0: -1}
                for node, parent, _, detail in db.execute("EXPLAIN QUERY PLAN " + sql):
                    depth[node] = depth[parent] + 1
                    print("  " * depth[node] + detail)
            ''', label="a plan tree: scans, index searches, a subquery and two temp b-trees"),
            note("Always <code>EXPLAIN ANALYZE</code> on production-like data. A plan on an empty development database tells you nothing, because the optimizer correctly decides that scanning three rows is cheapest."),
        ),
        section(
            "Why a seemingly obvious query can be slow",
            "The most expensive queries in a real system are often the most innocent-looking. Four classics, measured:",
            code(SETUP + '''
page = "SELECT * FROM trades ORDER BY id LIMIT 10 OFFSET ?"
keyset = "SELECT * FROM trades WHERE id > ? ORDER BY id LIMIT 10"
for n in (10, 1_000, 90_000):
    off, _ = steps(page, (n,))
    key, _ = steps(keyset, (n,))
    print(f"page at row {n:>6,}: OFFSET {off:>8,} steps   keyset {key:>4,} steps")
''', label="1. OFFSET pagination reads and discards every earlier row"),
            "<code>OFFSET 90000</code> has to walk past 90,000 rows to throw them away, so deep pages get linearly slower. <strong>Keyset (seek) pagination</strong> remembers the last key seen and asks for <code>WHERE id &gt; :last</code>, which is a seek no matter how deep you are.",
            code(SETUP + '''
db.execute("CREATE TABLE syms(sym TEXT PRIMARY KEY, sector TEXT)")
db.executemany("INSERT INTO syms VALUES (?, ?)", [(f"S{i}", f"sec{i % 10}") for i in range(500)])

correlated = """SELECT sym FROM syms s
                WHERE (SELECT count(*) FROM trades t WHERE t.sym = s.sym) > 150"""
grouped = """SELECT sym FROM trades GROUP BY sym HAVING count(*) > 150"""
a, ra = steps(correlated, every=1000)      # too many to count one by one
b, rb = steps(grouped, every=1000)
print(f"correlated subquery: {ra} rows, {a // 1000:>9,}k steps")
print(f"one GROUP BY pass:   {rb} rows, {b // 1000:>9,}k steps")
''', label="2. a correlated subquery re-runs for every outer row"),
            "Without an index on <code>trades.sym</code>, the subquery scans all 100,000 trades once for each of 500 symbols. The <code>GROUP BY</code> reads the table once. (An index on <code>trades(sym)</code> would also rescue the first form &mdash; many planners decorrelate it automatically, SQLite does not.)",
            "<strong>3. A function on the column.</strong> <code>WHERE date(ts) = '2026-09-30'</code> cannot use an index on <code>ts</code>; <code>WHERE ts &gt;= '2026-09-30' AND ts &lt; '2026-10-01'</code> can.",
            "<strong>4. The N+1 pattern.</strong> An ORM loads 500 orders, then lazily issues one query per order to fetch its customer. Each query is fast; 501 network round trips are not. Fetch with one join or one <code>WHERE id IN (...)</code>.",
            "Other regulars: <code>SELECT count(*)</code> on a huge MVCC table (each row&rsquo;s visibility must be checked, so there is no stored total); <code>ORDER BY ... LIMIT 10</code> with no index matching the order (sorts everything to return ten rows); <code>NOT IN</code> with a nullable subquery column (wrong <em>and</em> slow); implicit casts from a driver sending a parameter as the wrong type; and a plan that was good for yesterday&rsquo;s parameter distribution, cached in a prepared statement.",
        ),
    ],
    questions=[
        question(
            "When would a database choose a hash join over a nested-loop join, and when is nested loop the better choice?",
            "medium",
            "Hash join wins for an equality join between two large inputs where neither side is small and there is no useful index: build a hash table on the smaller side, stream the larger side through it, O(N + M). It needs memory for the build side and only works for equality conditions.",
            "Nested loop wins when the outer side is small &mdash; after a selective filter, say 20 rows &mdash; and the inner side has an index on the join key. Then the cost is 20 index seeks, far less than hashing an entire large table. It is also the only option for non-equality conditions such as <code>a.ts BETWEEN b.start AND b.end</code> (unless merge join can use a range).",
            "The trap: if the planner <em>underestimates</em> the outer side (expects 20 rows, gets 200,000), a nested loop becomes catastrophic. That misestimate is one of the most common causes of a query that is suddenly 1,000&times; slower.",
        ),
        question(
            "A query was fast yesterday and is slow today. Nothing was deployed. What do you check?",
            "hard",
            "The plan changed, or the data did. In order:",
            "<strong>1. Compare plans.</strong> <code>EXPLAIN ANALYZE</code> now vs. a saved plan (<code>auto_explain</code>, <code>pg_stat_statements</code>, Query Store in SQL Server). Look for a flipped join algorithm or join order, or an index scan that became a sequential scan.<br><strong>2. Statistics.</strong> Did autovacuum/auto-analyze run after a large load or delete? Did a table cross a size where the estimated cost of one plan overtook another? Did the data become skewed (a new customer with 40% of rows)?<br><strong>3. Parameter sensitivity.</strong> A cached generic plan built for one parameter value is being reused for a very different one.<br><strong>4. Bloat.</strong> Dead tuples from a long-running transaction make every scan read more pages.<br><strong>5. Not the query at all.</strong> Lock waits (check <code>pg_locks</code> / wait events), a cold cache after a restart or failover, I/O contention from a backup or vacuum, or replication lag if it reads from a replica.",
        ),
        question(
            "Why is OFFSET-based pagination slow on deep pages, and what do you do instead?",
            "medium",
            "<code>LIMIT 10 OFFSET 100000</code> cannot jump to row 100,000; the engine must produce the first 100,010 rows in order and discard 100,000 of them, so cost grows linearly with page depth. It is also unstable: rows inserted or deleted between requests shift the pages, so users see duplicates or miss rows.",
            "Keyset pagination: order by a unique key (or a unique tuple such as <code>(created_at, id)</code>), remember the last value returned, and ask for <code>WHERE (created_at, id) &gt; (:last_ts, :last_id) ORDER BY created_at, id LIMIT 10</code>. With a matching index this is one seek per page at any depth, and it is stable under concurrent inserts. The trade-off is that you cannot jump straight to page 500, which most interfaces do not actually need.",
        ),
        question(
            "What is cardinality estimation and why do errors in it matter so much?",
            "hard",
            "It is the optimizer&rsquo;s prediction of how many rows each operator will output. Every cost the optimizer computes &mdash; which access path, which join algorithm, which join order, how much memory to give a hash or sort &mdash; is a function of those predictions.",
            "Errors compound through a plan. If a filter is estimated at 1% but is really 30%, and its output is joined with another table whose join selectivity is also misjudged, the estimate at the top of a five-way join can be off by several orders of magnitude. The optimizer then picks a nested loop expecting 10 iterations and gets 10 million, or sizes a hash table for 1,000 rows and spills 10 million to disk.",
            "Common causes: correlated predicates assumed independent, skewed value distributions summarised by averages, predicates the estimator cannot see into (functions, <code>LIKE</code> patterns, parameters in generic plans), and stale statistics. Remedies: <code>ANALYZE</code>, raising the statistics target on skewed columns, extended statistics on correlated columns, rewriting predicates to be estimable, and as a last resort plan hints.",
        ),
        question(
            "Explain the Volcano iterator model and why analytical engines moved away from it.",
            "hard",
            "In the Volcano model each plan operator implements <code>open()</code>, <code>next()</code> and <code>close()</code>. The root calls <code>next()</code> on its child, which calls its child, down to the scans, and each call returns one row. It is simple and composable, and pipelines naturally: a <code>LIMIT 10</code> stops pulling after ten rows.",
            "The cost is per-row overhead. Every row passes through a chain of virtual function calls, each processing one value with poor branch prediction and no chance for SIMD. For OLTP, which touches a handful of rows, that does not matter. For an analytical query over a billion rows it dominates.",
            "Vectorised execution (MonetDB/X100, DuckDB, ClickHouse, Snowflake) passes batches of around 1,000&ndash;64,000 values per call, so the overhead is paid once per batch and the inner loops are tight, cache-friendly and SIMD-able. Compiled execution (HyPer, Umbra, Spark&rsquo;s whole-stage codegen) instead generates one fused machine-code loop for a pipeline of operators. Both deliver roughly an order of magnitude over row-at-a-time on analytical workloads.",
        ),
    ],
    refs=[
        ("SQLite: the query optimizer overview", "https://www.sqlite.org/optoverview.html"),
        ("SQLite: the next-generation query planner", "https://www.sqlite.org/queryplanner-ng.html"),
        ("PostgreSQL: using EXPLAIN", "https://www.postgresql.org/docs/current/using-explain.html"),
        ("PostgreSQL: planner statistics", "https://www.postgresql.org/docs/current/planner-stats.html"),
        ("Leis et al. — How Good Are Query Optimizers, Really?", "https://www.vldb.org/pvldb/vol9/p204-leis.pdf"),
    ],
)
