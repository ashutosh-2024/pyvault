from deepdive._blocks import code, table, note, caveat, section, question

# A small, fixed dataset and a printer, pasted into each snippet.
DATA = '''
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);
    INSERT INTO traders VALUES
        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),
        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);
    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);
    INSERT INTO trades VALUES
        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),
        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),
        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),
        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');
""")

def show(sql):
    cur = db.execute(sql)
    cols = [c[0] for c in cur.description]
    rows = [[("NULL" if v is None else str(v)) for v in r] for r in cur.fetchall()]
    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())
    for r in rows:
        print("  ".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())
    print()
'''

TOPIC = dict(
    id="sql",
    title="SQL Fundamentals",
    summary="Joins, grouping, window functions, CTEs, subqueries, set operations and the NULL traps.",
    intro=[
        "Interviews for data-heavy roles still include a live SQL exercise, and the mistakes people make are consistent: a <code>LEFT JOIN</code> silently turned into an inner join by a <code>WHERE</code> clause, a filter in <code>WHERE</code> that belonged in <code>HAVING</code>, a <code>NOT IN</code> that returns nothing because of a <code>NULL</code>, and not knowing window functions exist.",
        "Every example runs against the same two small tables: five traders (one with no desk, one who has never traded) and eight trades (one by a trader ID that does not exist). Those gaps are deliberate; they are what make joins and NULLs interesting.",
    ],
    sections=[
        section(
            "Joins",
            code(DATA + '''
show("""SELECT t.id, tr.name, t.sym FROM trades t
        JOIN traders tr ON tr.id = t.trader_id ORDER BY t.id""")
show("""SELECT tr.name, count(t.id) AS n_trades FROM traders tr
        LEFT JOIN trades t ON t.trader_id = tr.id GROUP BY tr.name ORDER BY tr.name""")
show("""SELECT tr.name, t.id AS trade FROM traders tr
        FULL JOIN trades t ON t.trader_id = tr.id WHERE tr.id IS NULL OR t.id IS NULL""")
''', label="inner, left and full outer joins"),
            "The inner join dropped trade 8 (no such trader). The left join kept every trader and counted zero for Kim and Dan. The full join, filtered to its unmatched rows, finds orphans on both sides at once &mdash; a standard data-quality check.",
            table(
                ["Join", "Returns"],
                [
                    ["<code>INNER JOIN</code>", "Only rows with a match on both sides"],
                    ["<code>LEFT JOIN</code>", "Every left row; right columns are NULL where there is no match"],
                    ["<code>RIGHT JOIN</code>", "Mirror of left; usually rewritten as a left join for readability"],
                    ["<code>FULL JOIN</code>", "Every row from both sides, matched where possible"],
                    ["<code>CROSS JOIN</code>", "Every combination: rows(A) &times; rows(B)"],
                    ["Self join", "A table joined to itself, e.g. trader to manager"],
                ],
            ),
            "The most common join bug: filtering the outer side in <code>WHERE</code>. The <code>WHERE</code> runs after the join, the unmatched rows have NULL there, and the condition discards them &mdash; turning the left join into an inner join. Put conditions on the optional side in the <code>ON</code> clause.",
            code(DATA + '''
show("""SELECT tr.name, t.sym FROM traders tr
        LEFT JOIN trades t ON t.trader_id = tr.id
        WHERE t.day = '2026-09-30' ORDER BY tr.name""")
show("""SELECT tr.name, t.sym FROM traders tr
        LEFT JOIN trades t ON t.trader_id = tr.id AND t.day = '2026-09-30'
        ORDER BY tr.name""")
''', label="the same filter in WHERE vs in ON"),
        ),
        section(
            "Aggregation, GROUP BY and HAVING",
            "<code>GROUP BY</code> collapses rows into one per group; every selected column must either be grouped or aggregated. <code>WHERE</code> filters rows <em>before</em> grouping; <code>HAVING</code> filters groups <em>after</em>. The logical order of evaluation explains most confusion:",
            "<code>FROM</code> / <code>JOIN</code> &rarr; <code>WHERE</code> &rarr; <code>GROUP BY</code> &rarr; <code>HAVING</code> &rarr; window functions &rarr; <code>SELECT</code> &rarr; <code>DISTINCT</code> &rarr; <code>ORDER BY</code> &rarr; <code>LIMIT</code>",
            "That is why a column alias from <code>SELECT</code> cannot be used in <code>WHERE</code> (it does not exist yet), and why an aggregate cannot appear in <code>WHERE</code> (groups do not exist yet).",
            code(DATA + '''
show("""SELECT tr.desk, count(*) AS n, sum(t.qty * t.px) AS notional
        FROM trades t JOIN traders tr ON tr.id = t.trader_id
        WHERE t.qty > 0                          -- rows: only buys
        GROUP BY tr.desk
        HAVING sum(t.qty * t.px) > 10000         -- groups: only big desks
        ORDER BY notional DESC""")
''', label="WHERE filters rows, HAVING filters groups"),
            caveat("SQLite and MySQL (without <code>ONLY_FULL_GROUP_BY</code>) accept a non-aggregated, non-grouped column in <code>SELECT</code> and return a value from an arbitrary row of the group. PostgreSQL and the SQL standard reject it. Do not rely on it."),
        ),
        section(
            "Window functions",
            "A window function computes over a set of rows related to the current row <em>without</em> collapsing them. Syntax: <code>func() OVER (PARTITION BY ... ORDER BY ... frame)</code>. <code>PARTITION BY</code> is like <code>GROUP BY</code> but keeps the rows; <code>ORDER BY</code> defines the order within the partition, and for aggregates it makes them running totals.",
            code(DATA + '''
show("""SELECT trader_id AS tid, day, sym, qty,
               sum(qty) OVER (PARTITION BY trader_id ORDER BY day, id) AS running_qty,
               row_number() OVER (PARTITION BY trader_id ORDER BY day, id) AS nth,
               lag(sym) OVER (PARTITION BY trader_id ORDER BY day, id) AS prev_sym
        FROM trades WHERE trader_id IN (2, 3) ORDER BY trader_id, day, id""")
''', label="running totals, numbering, and the previous row"),
            code(DATA + '''
show("""SELECT * FROM (
          SELECT tr.desk, tr.name, sum(abs(t.qty) * t.px) AS notional,
                 rank() OVER (PARTITION BY tr.desk ORDER BY sum(abs(t.qty) * t.px) DESC) AS rk
          FROM trades t JOIN traders tr ON tr.id = t.trader_id
          GROUP BY tr.desk, tr.name)
        WHERE rk = 1""")
''', label="top N per group: the most common window-function question"),
            table(
                ["Function", "Returns"],
                [
                    ["<code>row_number()</code>", "1, 2, 3, &hellip; with no ties"],
                    ["<code>rank()</code>", "Ties share a rank, then a gap: 1, 1, 3"],
                    ["<code>dense_rank()</code>", "Ties share a rank, no gap: 1, 1, 2"],
                    ["<code>lag(x, n)</code> / <code>lead(x, n)</code>", "Value n rows before / after"],
                    ["<code>first_value</code> / <code>last_value</code>", "Value at the edge of the frame (mind the default frame)"],
                    ["<code>sum</code>/<code>avg</code>/<code>count</code> <code>OVER</code>", "Running or moving aggregates"],
                    ["<code>ntile(n)</code>", "Bucket number, for quartiles and percentiles"],
                ],
            ),
            "The frame clause controls which rows an aggregate sees: <code>ROWS BETWEEN 4 PRECEDING AND CURRENT ROW</code> is a five-row moving window. With an <code>ORDER BY</code> and no frame, the default is <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>, which includes all rows <em>tied</em> with the current one &mdash; a classic source of surprising running totals, and why <code>last_value</code> seems to return the current row.",
        ),
        section(
            "CTEs and subqueries",
            "A <strong>common table expression</strong> (<code>WITH name AS (...)</code>) names a subquery so the main query reads top to bottom. A <strong>recursive CTE</strong> can walk hierarchies and generate series, which plain SQL otherwise cannot.",
            code(DATA + '''
show("""WITH RECURSIVE chain(id, name, depth, path) AS (
            SELECT id, name, 0, name FROM traders WHERE manager_id IS NULL
            UNION ALL
            SELECT t.id, t.name, c.depth + 1, c.path || ' > ' || t.name
            FROM traders t JOIN chain c ON t.manager_id = c.id
        )
        SELECT name, depth, path FROM chain ORDER BY path""")
''', label="walking the management hierarchy with a recursive CTE"),
            "Subqueries come in three shapes. A <strong>scalar</strong> subquery returns one value (<code>WHERE px &gt; (SELECT avg(px) FROM trades)</code>). A <strong>table</strong> subquery appears in <code>FROM</code> as a derived table. A <strong>correlated</strong> subquery refers to the outer row and conceptually runs once per row &mdash; the query-execution page shows how expensive that can be when the planner does not rewrite it.",
            caveat("Whether a CTE is inlined into the main query or computed once and stored varies. PostgreSQL before 12 always materialised CTEs, which made them an optimisation fence; since 12 it inlines side-effect-free CTEs referenced once, and <code>AS MATERIALIZED</code> / <code>NOT MATERIALIZED</code> let you choose."),
        ),
        section(
            "EXISTS, IN, UNION and set operations",
            code(DATA + '''
show("""SELECT name FROM traders tr
        WHERE EXISTS (SELECT 1 FROM trades t WHERE t.trader_id = tr.id AND t.sym = 'AAPL')""")
show("""SELECT sym FROM trades WHERE day = '2026-09-28'
        UNION
        SELECT sym FROM trades WHERE day = '2026-09-30'""")
show("""SELECT count(*) AS union_all_rows FROM (
          SELECT sym FROM trades WHERE day = '2026-09-28'
          UNION ALL
          SELECT sym FROM trades WHERE day = '2026-09-30')""")
show("""SELECT sym FROM trades WHERE day = '2026-09-28'
        INTERSECT
        SELECT sym FROM trades WHERE day = '2026-09-30'""")
''', label="EXISTS, UNION vs UNION ALL, INTERSECT"),
            "<code>EXISTS</code> asks only whether a matching row exists, so the engine can stop at the first one; it is the natural way to write a semi-join. <code>UNION</code> removes duplicates, which requires a sort or hash over the whole result; <code>UNION ALL</code> just concatenates. Use <code>UNION ALL</code> unless you actually need de-duplication. <code>INTERSECT</code> and <code>EXCEPT</code> are the set intersection and difference.",
        ),
        section(
            "NULL semantics",
            "<code>NULL</code> means &ldquo;unknown&rdquo;, and SQL uses <strong>three-valued logic</strong>: a comparison involving NULL is neither true nor false but <code>UNKNOWN</code>, and <code>WHERE</code> keeps only rows that are true.",
            code(DATA + '''
show("""SELECT NULL = NULL AS eq, NULL <> 1 AS ne, NULL IS NULL AS is_null,
               NULL AND 0 AS and_false, NULL OR 1 AS or_true, 1 + NULL AS plus""")
show("""SELECT count(*) AS all_rows, count(desk) AS with_desk,
               count(DISTINCT desk) AS desks FROM traders""")
show("""SELECT desk, count(*) AS n FROM traders GROUP BY desk ORDER BY desk""")
''', label="NULL in comparisons, counts and groups"),
            "<code>NULL = NULL</code> is unknown, not true, so you test with <code>IS NULL</code>. <code>count(column)</code> skips NULLs while <code>count(*)</code> counts rows; <code>sum</code> and <code>avg</code> ignore NULLs too. <code>GROUP BY</code> is the exception that treats all NULLs as one group. And <code>FALSE AND NULL</code> is false, <code>TRUE OR NULL</code> is true: unknown only propagates when it could change the answer.",
            "The trap that catches everyone is <code>NOT IN</code> with a subquery that can return NULL:",
            code(DATA + '''
show("""SELECT count(*) AS not_in_without_nulls FROM trades
        WHERE trader_id NOT IN (SELECT manager_id FROM traders WHERE manager_id IS NOT NULL)""")
show("""SELECT count(*) AS not_in FROM trades     -- kim's manager_id is NULL
        WHERE trader_id NOT IN (SELECT manager_id FROM traders)""")
show("""SELECT count(*) AS not_exists FROM trades t
        WHERE NOT EXISTS (SELECT 1 FROM traders m WHERE m.manager_id = t.trader_id)""")
''', label="NOT IN returns nothing once the list contains a NULL"),
            "The managers are traders 1 and 3, and six trades were made by someone else. But Kim has no manager, so the subquery returns <code>(1, 1, 3, 3, NULL)</code>, and <code>x NOT IN (1, 3, NULL)</code> means <code>x &lt;&gt; 1 AND x &lt;&gt; 3 AND x &lt;&gt; NULL</code>. The last term is unknown for every <code>x</code>, so the whole condition can never be true and the query returns zero rows. <code>NOT EXISTS</code> does not have the problem and is what you should write.",
            note("Prefer <code>NOT EXISTS</code> to <code>NOT IN (subquery)</code>, <code>IS [NOT] DISTINCT FROM</code> for NULL-safe comparison, and <code>coalesce(x, default)</code> when a NULL should behave like a value."),
        ),
    ],
    questions=[
        question(
            "Write a query for each trader&rsquo;s largest trade by notional, including ties. Then explain how you would do it without window functions.",
            "medium",
            "With a window function, rank within each trader and keep rank 1 (<code>rank</code> keeps ties; <code>row_number</code> would pick one arbitrarily):",
            "<code>SELECT * FROM (<br>&nbsp;&nbsp;SELECT t.*, rank() OVER (PARTITION BY trader_id ORDER BY abs(qty) * px DESC) AS rk<br>&nbsp;&nbsp;FROM trades t) x<br>WHERE rk = 1;</code>",
            "Without window functions, join to the per-trader maximum:",
            "<code>SELECT t.* FROM trades t<br>JOIN (SELECT trader_id, max(abs(qty) * px) AS m FROM trades GROUP BY trader_id) g<br>&nbsp;&nbsp;ON g.trader_id = t.trader_id AND abs(t.qty) * t.px = g.m;</code>",
            "or with a correlated <code>NOT EXISTS</code> (&ldquo;no trade by the same trader is larger&rdquo;). The window version reads the table once; the join version reads it twice. The PostgreSQL-specific <code>DISTINCT ON (trader_id) ... ORDER BY trader_id, notional DESC</code> is the shortest but does not return ties.",
        ),
        question(
            "Why does <code>SELECT * FROM a WHERE id NOT IN (SELECT a_id FROM b)</code> sometimes return no rows at all?",
            "medium",
            "Because <code>b.a_id</code> contains at least one NULL. <code>id NOT IN (1, 2, NULL)</code> expands to <code>id &lt;&gt; 1 AND id &lt;&gt; 2 AND id &lt;&gt; NULL</code>; the last comparison is UNKNOWN for every row, so the conjunction is never TRUE, and <code>WHERE</code> discards everything.",
            "Fix with <code>NOT EXISTS (SELECT 1 FROM b WHERE b.a_id = a.id)</code>, which is unaffected by NULLs and is also what optimizers turn into an efficient anti-join, or with a <code>LEFT JOIN b ... WHERE b.a_id IS NULL</code>. Adding <code>WHERE a_id IS NOT NULL</code> inside the subquery also works but is easy to forget.",
        ),
        question(
            "What is the difference between WHERE and HAVING, and between UNION and UNION ALL? Which is faster and why?",
            "medium",
            "<code>WHERE</code> filters individual rows before grouping and cannot use aggregates. <code>HAVING</code> filters groups after aggregation. A condition that does not involve an aggregate should go in <code>WHERE</code>, so rows are discarded before the grouping work (most optimizers move it there anyway).",
            "<code>UNION</code> returns distinct rows, which needs a sort or hash over the combined result. <code>UNION ALL</code> concatenates and can stream rows without buffering. <code>UNION ALL</code> is faster and should be the default; use <code>UNION</code> only when duplicates are possible and must be removed.",
        ),
        question(
            "Compute a 3-day moving average of daily traded notional per symbol, and explain the frame you chose.",
            "hard",
            "First aggregate to one row per symbol per day, then apply a window over those rows:",
            "<code>WITH daily AS (<br>&nbsp;&nbsp;SELECT sym, day, sum(abs(qty) * px) AS notional FROM trades GROUP BY sym, day)<br>SELECT sym, day, notional,<br>&nbsp;&nbsp;avg(notional) OVER (PARTITION BY sym ORDER BY day<br>&nbsp;&nbsp;&nbsp;&nbsp;ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma3<br>FROM daily;</code>",
            "<code>ROWS BETWEEN 2 PRECEDING AND CURRENT ROW</code> averages the current row and the two before it. Two subtleties: the first two days average fewer than three values (filter them out or use <code>count(*) OVER (...) = 3</code> if a full window is required); and <code>ROWS</code> counts rows, so days with no trading are skipped rather than counted as zero. For calendar-correct windows either generate a complete date series (a recursive CTE) and left join to it, or use a <code>RANGE</code> frame over a date or day-number column with an interval offset where the engine supports it.",
        ),
    ],
    refs=[
        ("SQLite: SELECT", "https://www.sqlite.org/lang_select.html"),
        ("SQLite: window functions", "https://www.sqlite.org/windowfunctions.html"),
        ("SQLite: WITH clause (common table expressions)", "https://www.sqlite.org/lang_with.html"),
        ("PostgreSQL: window function tutorial", "https://www.postgresql.org/docs/current/tutorial-window.html"),
        ("Modern SQL — what's new in SQL", "https://modern-sql.com/"),
    ],
)
