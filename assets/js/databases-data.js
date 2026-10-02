/* GENERATED FILE - do not edit by hand.
   Source: content/databases/   Build: python3 build.py
   Every code block below was executed and its output captured. */

window.GRAIL_DB = [
  {
    "id": "btree-indexes",
    "title": "B-Tree and B+ Tree Indexes",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Why every index is a wide, shallow, sorted tree, and when the planner ignores it.",
    "intro": [
      "Almost every index you will create in a relational database is a B+ tree. PostgreSQL, MySQL/InnoDB, SQLite, SQL Server and Oracle all default to one. Understanding its shape explains nearly every indexing rule of thumb you have been told: why a lookup in a billion-row table touches three or four pages, why column order in a composite index matters, why <code>LIKE '%foo'</code> cannot use an index, and why an index on a boolean column is usually useless.",
      "The examples use SQLite from the standard library. Its <code>EXPLAIN QUERY PLAN</code> output is the real plan chosen by the engine that ran the snippet, so what you see is what the optimizer actually decided."
    ],
    "sections": [
      {
        "title": "How a B+ tree works",
        "body": [
          {
            "type": "p",
            "html": "A B+ tree is a balanced search tree in which every node is one <strong>page</strong> &mdash; typically 4, 8 or 16&nbsp;KB &mdash; and holds hundreds of keys, not two. Interior nodes hold only separator keys and child pointers. All the actual entries live in the <strong>leaves</strong>, which are kept in key order and linked to their neighbours."
          },
          {
            "type": "p",
            "html": "Insertion goes to the correct leaf. When a leaf overflows it splits in half and pushes one separator key up to its parent; if the parent overflows it splits too. The tree only grows taller when the root splits, so every leaf is always at the same depth. That is the &ldquo;balanced&rdquo; guarantee: no insertion order can produce a degenerate, list-shaped tree."
          },
          {
            "type": "code",
            "src": "import bisect\n\nORDER = 4  # max keys per node; real engines fit hundreds per page\n\nclass Node:\n    def __init__(self, leaf):\n        self.leaf, self.keys, self.kids, self.next = leaf, [], [], None\n\ndef insert(node, key):\n    \"\"\"Insert key below node; return (separator, new_right_node) on split.\"\"\"\n    if node.leaf:\n        bisect.insort(node.keys, key)\n    else:\n        i = bisect.bisect_right(node.keys, key)\n        split = insert(node.kids[i], key)\n        if split:\n            sep, right = split\n            node.keys.insert(i, sep)\n            node.kids.insert(i + 1, right)\n    if len(node.keys) <= ORDER:\n        return None\n    mid = len(node.keys) // 2\n    right = Node(node.leaf)\n    if node.leaf:                      # leaves keep the separator key\n        right.keys, node.keys = node.keys[mid:], node.keys[:mid]\n        right.next, node.next = node.next, right\n        return right.keys[0], right\n    sep = node.keys[mid]               # interior nodes push it up\n    right.keys, node.keys = node.keys[mid + 1:], node.keys[:mid]\n    right.kids, node.kids = node.kids[mid + 1:], node.kids[:mid + 1]\n    return sep, right\n\nroot = Node(leaf=True)\nfor k in range(1, 21):\n    split = insert(root, k)\n    if split:                          # root split: tree grows one level\n        new = Node(leaf=False)\n        new.keys, new.kids = [split[0]], [root, split[1]]\n        root = new\n\nlevel = [root]\nwhile level:\n    print(\"   \".join(str(n.keys) for n in level))\n    level = [] if level[0].leaf else [k for n in level for k in n.kids]\n\nleaf = root\nwhile not leaf.leaf:\n    leaf = leaf.kids[0]\nchain = []\nwhile leaf:\n    chain += leaf.keys\n    leaf = leaf.next\nprint(\"leaf chain:\", chain)",
            "label": "a tiny B+ tree, inserting 1..20 in order",
            "output": "[7, 13]\n[3, 5]   [9, 11]   [15, 17]\n[1, 2]   [3, 4]   [5, 6]   [7, 8]   [9, 10]   [11, 12]   [13, 14]   [15, 16]   [17, 18, 19, 20]\nleaf chain: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Two things to notice. Every leaf is at the same depth. And the leaves form a sorted linked list, so a range query (<code>BETWEEN 7 AND 15</code>) descends once to find 7 and then walks sideways, never going back up the tree."
          },
          {
            "type": "note",
            "text": "A B+ tree lookup costs one page read per level. The whole design is about keeping the number of levels tiny."
          }
        ]
      },
      {
        "title": "Why databases use them",
        "body": [
          {
            "type": "p",
            "html": "Disks and SSDs read whole pages, and a page read costs far more than anything the CPU does with the page afterwards. A binary search tree with one key per node would need about 30 page reads to find one row among a billion. A B+ tree with a few hundred keys per page needs three or four, and the top one or two levels are almost always already cached in memory."
          },
          {
            "type": "code",
            "src": "import math\n\nfor fanout in (2, 100, 500):\n    for rows in (10**6, 10**9):\n        levels = math.ceil(math.log(rows, fanout))\n        print(f\"fanout {fanout:>3}, {rows:>13,} rows -> {levels:>2} levels\")",
            "label": "height = log base fanout of rows",
            "output": "fanout   2,     1,000,000 rows -> 20 levels\nfanout   2, 1,000,000,000 rows -> 30 levels\nfanout 100,     1,000,000 rows ->  3 levels\nfanout 100, 1,000,000,000 rows ->  5 levels\nfanout 500,     1,000,000 rows ->  3 levels\nfanout 500, 1,000,000,000 rows ->  4 levels",
            "isError": false
          },
          {
            "type": "p",
            "html": "With 8&nbsp;KB pages and 8-byte keys plus 8-byte pointers, one interior page holds around 500 children, so a billion keys fit in four levels. The root and second level (500 pages, 4&nbsp;MB) stay resident in the buffer pool, so a lookup usually costs one or two actual I/Os."
          },
          {
            "type": "table",
            "head": [
              "Structure",
              "Point lookup",
              "Range scan",
              "Why it loses"
            ],
            "rows": [
              [
                "B+ tree",
                "O(log<sub>F</sub> n) pages, F in the hundreds",
                "Descend once, walk leaves",
                "&mdash; (the default for a reason)"
              ],
              [
                "Hash index",
                "O(1) expected",
                "Impossible: no order",
                "No ranges, no <code>ORDER BY</code>, no prefix match"
              ],
              [
                "Binary search tree",
                "O(log<sub>2</sub> n) pages",
                "In-order walk",
                "One key per node means ~30 page reads for a billion rows"
              ],
              [
                "Sorted array",
                "O(log n)",
                "Excellent",
                "Every insert shifts half the file"
              ],
              [
                "LSM tree",
                "Several structures to check",
                "Merge several runs",
                "Better for write-heavy workloads; see the internals page"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Why B+ rather than plain B-tree? In a classic B-tree, interior nodes also carry values. Moving all values to the leaves makes interior nodes smaller, so fanout goes up and the tree gets shorter, and the linked leaf level makes range scans a sequential walk."
          }
        ]
      },
      {
        "title": "Clustered vs non-clustered indexes",
        "body": [
          {
            "type": "p",
            "html": "A <strong>clustered</strong> index stores the table rows themselves in its leaves, in key order. There can be only one, because the rows can only be physically sorted one way. A <strong>non-clustered</strong> (secondary) index stores the key plus a pointer back to the row. Looking up a row through a secondary index is therefore two searches: find the pointer, then fetch the row."
          },
          {
            "type": "table",
            "head": [
              "Engine",
              "Table storage",
              "What a secondary index leaf points to"
            ],
            "rows": [
              [
                "MySQL InnoDB",
                "Clustered on the primary key",
                "The primary key value (so a second B+ tree descent)"
              ],
              [
                "SQL Server",
                "Clustered index optional; otherwise a heap",
                "Clustering key, or a row ID for heaps"
              ],
              [
                "PostgreSQL",
                "Unordered heap; no clustered index",
                "A physical tuple ID (page, slot)"
              ],
              [
                "SQLite",
                "Clustered on <code>rowid</code> (or on the PK for <code>WITHOUT ROWID</code>)",
                "The <code>rowid</code>"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE orders(id INTEGER PRIMARY KEY, customer INT, amount REAL)\")\ndb.execute(\"CREATE INDEX ix_customer ON orders(customer)\")\n\ndef plan(sql):\n    for row in db.execute(\"EXPLAIN QUERY PLAN \" + sql):\n        print(f\"{sql:<45} -> {row[3]}\")\n\nplan(\"SELECT * FROM orders WHERE id = 42\")\nplan(\"SELECT * FROM orders WHERE customer = 7\")",
            "label": "the clustered key vs a secondary index",
            "output": "SELECT * FROM orders WHERE id = 42            -> SEARCH orders USING INTEGER PRIMARY KEY (rowid=?)\nSELECT * FROM orders WHERE customer = 7       -> SEARCH orders USING INDEX ix_customer (customer=?)",
            "isError": false
          },
          {
            "type": "p",
            "html": "The first query searches the table's own B+ tree directly. The second searches <code>ix_customer</code>, gets back rowids, and then does a second search into the table for each one."
          },
          {
            "type": "p",
            "html": "Consequences worth knowing: in InnoDB, a wide primary key (say, a UUID string) is copied into every secondary index, bloating all of them. Random primary keys such as UUIDv4 scatter inserts across the whole clustered tree, causing page splits and poor cache locality, where an auto-increment key always appends to the rightmost leaf."
          },
          {
            "type": "caveat",
            "text": "PostgreSQL&rsquo;s <code>CLUSTER</code> command physically reorders a heap once but does not maintain the order afterwards, so it is not a clustered index in the InnoDB sense."
          }
        ]
      },
      {
        "title": "Composite indexes and the leftmost-prefix rule",
        "body": [
          {
            "type": "p",
            "html": "An index on <code>(customer, status)</code> is sorted by <code>customer</code> first, and by <code>status</code> only within equal customers &mdash; exactly like a phone book sorted by surname, then first name. It can answer anything that constrains a <em>leftmost prefix</em> of its columns, and nothing that skips the first one."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE orders(id INTEGER PRIMARY KEY, customer INT, status TEXT, amount REAL)\")\ndb.execute(\"CREATE INDEX ix_cust_status ON orders(customer, status)\")\n\nfor where in (\"customer = 7\",\n              \"customer = 7 AND status = 'open'\",\n              \"customer > 100\",\n              \"status = 'open'\"):\n    plan = db.execute(f\"EXPLAIN QUERY PLAN SELECT * FROM orders WHERE {where}\").fetchone()[3]\n    print(f\"{where:<35} {plan}\")",
            "label": "which predicates can use (customer, status)?",
            "output": "customer = 7                        SEARCH orders USING INDEX ix_cust_status (customer=?)\ncustomer = 7 AND status = 'open'    SEARCH orders USING INDEX ix_cust_status (customer=? AND status=?)\ncustomer > 100                      SEARCH orders USING INDEX ix_cust_status (customer>?)\nstatus = 'open'                     SCAN orders",
            "isError": false
          },
          {
            "type": "p",
            "html": "The last query cannot seek: <code>'open'</code> orders are scattered across every customer&rsquo;s section of the index, so the engine scans the table."
          },
          {
            "type": "p",
            "html": "Column order rules of thumb:"
          },
          {
            "type": "p",
            "html": "<strong>Equality columns first, range column last.</strong> With <code>WHERE a = ? AND b &gt; ?</code>, an index on <code>(a, b)</code> seeks to <code>a</code> and then scans a contiguous range of <code>b</code>. An index on <code>(b, a)</code> scans the whole <code>b</code> range and filters <code>a</code> row by row.<br><strong>Only one range per index is useful.</strong> After the first range column, later columns are no longer sorted within the range.<br><strong>Match the <code>ORDER BY</code>.</strong> <code>WHERE a = ? ORDER BY b</code> on <code>(a, b)</code> reads rows already sorted and skips the sort entirely."
          },
          {
            "type": "caveat",
            "text": "Some engines (Oracle, MySQL 8, PostgreSQL 18) can do a <em>skip scan</em>: when the leading column has few distinct values, they seek once per distinct value. It rescues some queries that skip the first column, but only when that column&rsquo;s cardinality is low."
          }
        ]
      },
      {
        "title": "Selectivity: when the planner decides an index is worse",
        "body": [
          {
            "type": "p",
            "html": "<strong>Selectivity</strong> is the fraction of rows a predicate matches. <code>email = ?</code> on a unique column matches one row in a million; <code>status = 'open'</code> may match a third of the table. An index is a win when it lets the engine skip most of the table. It is a loss when it doesn&rsquo;t, because each match through a secondary index is a <em>random</em> page read, while a full scan reads pages <em>sequentially</em> and gets every row on each page."
          },
          {
            "type": "code",
            "src": "ROWS, ROWS_PER_PAGE = 1_000_000, 100\nPAGES = ROWS // ROWS_PER_PAGE\nRANDOM, SEQUENTIAL = 4.0, 1.0          # PostgreSQL's default cost ratio\n\nfull_scan = PAGES * SEQUENTIAL\nprint(f\"full scan: {full_scan:>9,.0f}\")\nfor fraction in (0.0001, 0.001, 0.0025, 0.005, 0.01, 0.1, 0.33):\n    via_index = ROWS * fraction * RANDOM   # worst case: one page per match\n    winner = \"index\" if via_index < full_scan else \"scan\"\n    print(f\"match {fraction:>7.2%}: {via_index:>9,.0f}  -> {winner}\")",
            "label": "a crude cost model: random page reads vs one sequential pass",
            "output": "full scan:    10,000\nmatch   0.01%:       400  -> index\nmatch   0.10%:     4,000  -> index\nmatch   0.25%:    10,000  -> scan\nmatch   0.50%:    20,000  -> scan\nmatch   1.00%:    40,000  -> scan\nmatch  10.00%:   400,000  -> scan\nmatch  33.00%: 1,320,000  -> scan",
            "isError": false
          },
          {
            "type": "p",
            "html": "In this worst case &mdash; every match on a different page &mdash; the crossover is a quarter of a percent. Real data is kinder: matching rows often share pages, and hot pages are cached, so in practice the crossover for a row store usually lands somewhere between a fraction of a percent and a few percent. The shape is the point: past a small fraction of the table, the scan wins. That is why an index on a low-cardinality column (boolean flags, status enums, gender) rarely gets used for equality lookups on its own &mdash; unless the value you query is rare (<code>WHERE status = 'failed'</code> when 0.1% fail). The optimizer knows the difference only if it has statistics, which is what <code>ANALYZE</code> collects."
          },
          {
            "type": "p",
            "html": "<strong>Partial indexes</strong> exploit exactly this: <code>CREATE INDEX ... WHERE status = 'failed'</code> indexes only the rare rows, so the index is tiny and always selective."
          },
          {
            "type": "caveat",
            "text": "SQLite&rsquo;s planner is much simpler than PostgreSQL&rsquo;s and will often still use an index for a 33%-selective predicate. PostgreSQL and MySQL cost the plans and switch to a sequential scan. The crossover also shifts on SSDs, where random reads are cheaper; tuning <code>random_page_cost</code> down toward 1.1 tells PostgreSQL so."
          }
        ]
      },
      {
        "title": "Covering indexes and index-only scans",
        "body": [
          {
            "type": "p",
            "html": "If every column a query needs is already in the index, the engine never has to visit the table at all. That is a <strong>covering index</strong>, and the resulting plan is an <strong>index-only scan</strong>. It removes the second lookup per row, which is often most of the cost."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE orders(id INTEGER PRIMARY KEY, customer INT, status TEXT, amount REAL)\")\ndb.execute(\"CREATE INDEX ix_cust_status ON orders(customer, status)\")\n\nfor sql in (\"SELECT * FROM orders WHERE customer = 7\",\n            \"SELECT status FROM orders WHERE customer = 7\",\n            \"SELECT count(*) FROM orders WHERE customer = 7\",\n            \"SELECT id, status FROM orders WHERE customer = 7\",\n            \"SELECT amount FROM orders WHERE customer = 7\"):\n    print(f\"{sql:<50} {db.execute('EXPLAIN QUERY PLAN ' + sql).fetchone()[3]}\")",
            "label": null,
            "output": "SELECT * FROM orders WHERE customer = 7            SEARCH orders USING INDEX ix_cust_status (customer=?)\nSELECT status FROM orders WHERE customer = 7       SEARCH orders USING COVERING INDEX ix_cust_status (customer=?)\nSELECT count(*) FROM orders WHERE customer = 7     SEARCH orders USING COVERING INDEX ix_cust_status (customer=?)\nSELECT id, status FROM orders WHERE customer = 7   SEARCH orders USING COVERING INDEX ix_cust_status (customer=?)\nSELECT amount FROM orders WHERE customer = 7       SEARCH orders USING INDEX ix_cust_status (customer=?)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Note that <code>id</code> is covered for free: SQLite secondary indexes carry the rowid, just as InnoDB&rsquo;s carry the primary key. Adding <code>amount</code> as a trailing column (or, in PostgreSQL and SQL Server, via <code>INCLUDE (amount)</code>, which stores it in the leaves without making it part of the sort key) would cover the last query too."
          },
          {
            "type": "caveat",
            "text": "PostgreSQL can only return rows from an index-only scan if the heap page is marked all-visible in the <em>visibility map</em>, because MVCC visibility information lives in the heap, not in the index. On a table that has not been vacuumed recently, an &ldquo;index-only&rdquo; scan still visits the heap for many rows. <code>EXPLAIN ANALYZE</code> reports this as <code>Heap Fetches</code>."
          }
        ]
      },
      {
        "title": "When an index is not used",
        "body": [
          {
            "type": "p",
            "html": "An index is sorted by the raw column value. Anything that stops the engine from turning your predicate into &ldquo;seek to this key, walk to that key&rdquo; forces a scan."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE users(id INTEGER PRIMARY KEY, email TEXT, age INT, city TEXT)\")\ndb.execute(\"CREATE INDEX ix_email ON users(email)\")\ndb.execute(\"CREATE INDEX ix_age ON users(age)\")\n\nfor where in (\"email = 'a@x.com'\",\n              \"lower(email) = 'a@x.com'\",\n              \"email LIKE '%@x.com'\",\n              \"age + 1 = 30\",\n              \"age = 29 OR city = 'Paris'\"):\n    plan = db.execute(f\"EXPLAIN QUERY PLAN SELECT * FROM users WHERE {where}\").fetchone()[3]\n    print(f\"{where:<28} {plan}\")\n\ndb.execute(\"CREATE INDEX ix_email_lower ON users(lower(email))\")\nplan = db.execute(\"EXPLAIN QUERY PLAN SELECT * FROM users WHERE lower(email) = 'a@x.com'\").fetchone()[3]\nprint(f\"{'lower(email) = ... (indexed)':<28} {plan}\")",
            "label": "the classic index killers",
            "output": "email = 'a@x.com'            SEARCH users USING INDEX ix_email (email=?)\nlower(email) = 'a@x.com'     SCAN users\nemail LIKE '%@x.com'         SCAN users\nage + 1 = 30                 SCAN users\nage = 29 OR city = 'Paris'   SCAN users\nlower(email) = ... (indexed) SEARCH users USING INDEX ix_email_lower (<expr>=?)",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Pattern",
              "Why it cannot seek",
              "Fix"
            ],
            "rows": [
              [
                "<code>f(col) = ?</code>",
                "The index is sorted by <code>col</code>, not <code>f(col)</code>",
                "Expression index, or rewrite (<code>col &gt;= '2026-01-01' AND col &lt; '2026-02-01'</code> instead of <code>year(col)=2026</code>)"
              ],
              [
                "<code>LIKE '%foo'</code>",
                "No fixed prefix to seek to",
                "Trigram / full-text index, or store the reversed string"
              ],
              [
                "Implicit type cast (<code>varchar_col = 123</code>)",
                "The engine casts every row&rsquo;s column",
                "Compare with a value of the column&rsquo;s type"
              ],
              [
                "<code>a = ? OR b = ?</code>",
                "One index cannot serve both halves",
                "Index both and let the engine union them, or rewrite as <code>UNION</code>"
              ],
              [
                "Low selectivity",
                "Cheaper to scan (previous section)",
                "Partial index on the rare value"
              ],
              [
                "Tiny table",
                "The whole table is one or two pages",
                "Nothing; the scan is correct"
              ],
              [
                "Stale statistics",
                "The planner misjudges row counts",
                "<code>ANALYZE</code>"
              ]
            ]
          },
          {
            "type": "note",
            "text": "Every index also costs something: it slows every <code>INSERT</code>, <code>DELETE</code> and every <code>UPDATE</code> of its columns, and competes for buffer-pool memory. Index for the queries you run, not the columns you have."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why do databases use B+ trees instead of hash tables or binary search trees for indexes?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Because the cost that matters is page reads, not comparisons. A B+ tree node is a whole page with hundreds of keys, so the tree has fanout in the hundreds and height 3&ndash;4 for billions of rows; the upper levels stay in cache and a lookup typically costs one or two I/Os. A binary tree has fanout 2 and would need around 30 page reads."
          },
          {
            "type": "p",
            "html": "A hash index gives O(1) point lookups but no ordering: it cannot serve ranges, <code>ORDER BY</code>, <code>MIN/MAX</code>, or prefix matches, and it degrades when it needs rehashing. The B+ tree&rsquo;s sorted, linked leaf level serves all of those with one descent followed by a sequential walk."
          },
          {
            "type": "p",
            "html": "Moving values out of interior nodes (B+ rather than B) maximises fanout, and balancing by splitting upward guarantees every leaf sits at the same depth, so worst-case latency is predictable."
          }
        ]
      },
      {
        "q": "You have an index on <code>(last_name, first_name)</code>. Which of these queries can use it: <code>WHERE first_name = ?</code>, <code>WHERE last_name = ? ORDER BY first_name</code>, <code>WHERE last_name LIKE 'Sm%'</code>, <code>WHERE last_name &gt; 'M' AND first_name = 'Al'</code>?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<strong><code>first_name = ?</code></strong> &mdash; no seek. It skips the leading column. (A skip scan can help if <code>last_name</code> had few distinct values; it does not.)<br><strong><code>last_name = ? ORDER BY first_name</code></strong> &mdash; yes, and the sort disappears: within one last name the entries are already ordered by first name.<br><strong><code>LIKE 'Sm%'</code></strong> &mdash; yes, as a range <code>'Sm' &lt;= last_name &lt; 'Sn'</code> (subject to collation rules).<br><strong><code>last_name &gt; 'M' AND first_name = 'Al'</code></strong> &mdash; partly. It seeks to <code>'M'</code> and scans every later last name; <code>first_name</code> can only be checked as a filter on each index entry, because after a range column the next column is not sorted."
          }
        ]
      },
      {
        "q": "A query filters on an indexed column but the plan shows a full table scan. Walk through the possible reasons.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Work through them in rough order of likelihood:"
          },
          {
            "type": "p",
            "html": "<strong>1. It is cheaper.</strong> The predicate matches a large fraction of rows, so random heap fetches cost more than one sequential pass. Check estimated vs actual rows in <code>EXPLAIN ANALYZE</code>.<br><strong>2. Statistics are wrong.</strong> After a bulk load the planner may think the table is tiny or the value is common. Run <code>ANALYZE</code>.<br><strong>3. The predicate is not sargable.</strong> A function or arithmetic on the column, a leading wildcard, or an implicit cast (comparing a text column to an integer parameter is the common ORM bug).<br><strong>4. Collation or type mismatch.</strong> The index was built with a different collation or operator class than the comparison uses.<br><strong>5. Wrong column order.</strong> The query does not constrain the index&rsquo;s leading column.<br><strong>6. Parameterised generic plan.</strong> A prepared statement may use a plan built for a &ldquo;typical&rdquo; parameter, not this one.<br><strong>7. <code>OR</code> across columns</strong> that no single index serves."
          },
          {
            "type": "p",
            "html": "The fix is chosen from the cause: rewrite the predicate, add an expression or partial index, refresh statistics, or fix the parameter type."
          }
        ]
      },
      {
        "q": "What is a covering index, and what is the catch with index-only scans in PostgreSQL?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "A covering index contains every column the query reads &mdash; the filter columns as key columns and the rest either as trailing key columns or as <code>INCLUDE</code> payload. The engine can then answer from the index alone, skipping the per-row lookup into the table, which is usually the dominant cost of an index plan."
          },
          {
            "type": "p",
            "html": "The PostgreSQL catch is MVCC. Row visibility (which transaction created or deleted a version) lives in the heap tuple, not in the index. An index-only scan can skip the heap only for pages the <em>visibility map</em> marks all-visible, which <code>VACUUM</code> maintains. On a heavily updated table the map is mostly unset, so the &ldquo;index-only&rdquo; scan still fetches most heap pages. <code>EXPLAIN (ANALYZE)</code> shows the damage as <code>Heap Fetches</code>; the fix is more aggressive autovacuum on that table."
          },
          {
            "type": "p",
            "html": "The general costs still apply: a wider index is slower to write and takes more cache."
          }
        ]
      },
      {
        "q": "Why is a random UUID a poor clustered primary key in InnoDB, and what would you use instead?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "InnoDB stores rows in primary-key order. Sequential keys always insert into the rightmost leaf, which stays hot in the buffer pool, and full pages are left 15/16 full. Random UUIDv4 keys insert into a random leaf each time: the working set becomes the entire index, most inserts miss the cache and read a page from disk, and pages split in the middle and are left about half full, so the table ends up much larger."
          },
          {
            "type": "p",
            "html": "It also hurts every secondary index, because each secondary entry stores the primary key &mdash; a 36-byte string instead of an 8-byte integer."
          },
          {
            "type": "p",
            "html": "Use an auto-increment <code>BIGINT</code>, or a time-ordered identifier such as UUIDv7 or a Snowflake-style ID if you need globally unique IDs generated without coordination. Stored as <code>BINARY(16)</code> rather than text, a UUIDv7 keeps nearly the locality of an auto-increment key."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "SQLite: query planning",
        "url": "https://www.sqlite.org/queryplanner.html"
      },
      {
        "label": "SQLite: EXPLAIN QUERY PLAN",
        "url": "https://www.sqlite.org/eqp.html"
      },
      {
        "label": "PostgreSQL: index-only scans and covering indexes",
        "url": "https://www.postgresql.org/docs/current/indexes-index-only-scans.html"
      },
      {
        "label": "MySQL: clustered and secondary indexes",
        "url": "https://dev.mysql.com/doc/refman/8.4/en/innodb-index-types.html"
      },
      {
        "label": "Use The Index, Luke",
        "url": "https://use-the-index-luke.com/"
      }
    ]
  },
  {
    "id": "transactions",
    "title": "Transactions, ACID and Isolation",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "What each ACID letter promises, the read anomalies, and how MVCC gives readers a snapshot.",
    "intro": [
      "A transaction is a group of reads and writes the database treats as one unit: either all of it happens or none of it does, and concurrent transactions are kept from seeing each other&rsquo;s half-finished work. That sentence hides almost every hard question in database engineering, and interviewers know it.",
      "This page covers what ACID actually guarantees (and what it does not), commit and rollback, the isolation levels and the anomalies each one permits, and how MVCC lets readers and writers stop blocking each other. SQLite from the standard library runs the real examples; where SQLite is too strict to exhibit an anomaly, a twenty-line model of a multi-version store does."
    ],
    "sections": [
      {
        "title": "ACID, letter by letter",
        "body": [
          {
            "type": "table",
            "head": [
              "Letter",
              "Promise",
              "Mechanism",
              "Common misreading"
            ],
            "rows": [
              [
                "<strong>A</strong>tomicity",
                "All of the transaction&rsquo;s writes take effect, or none do",
                "Undo log / rollback segments, or shadow copies",
                "It is about <em>failure</em>, not concurrency"
              ],
              [
                "<strong>C</strong>onsistency",
                "A transaction moves the database from one valid state to another",
                "Constraints, triggers &mdash; and your application logic",
                "Not the C in CAP. Mostly the application&rsquo;s job"
              ],
              [
                "<strong>I</strong>solation",
                "Concurrent transactions do not see each other&rsquo;s intermediate states",
                "Locks, MVCC snapshots, conflict detection",
                "Default levels are weaker than &ldquo;as if run one at a time&rdquo;"
              ],
              [
                "<strong>D</strong>urability",
                "Once commit returns, the data survives a crash",
                "Write-ahead log flushed with <code>fsync</code> before acknowledging",
                "Only as durable as the disk&rsquo;s honesty about <code>fsync</code>, and one machine is one failure domain"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Consistency is the odd one out. The database can enforce declared constraints (<code>NOT NULL</code>, <code>CHECK</code>, foreign keys, uniqueness), but &ldquo;an order&rsquo;s total equals the sum of its lines&rdquo; or &ldquo;a trader cannot exceed their risk limit&rdquo; is only preserved if every transaction the application writes preserves it. Atomicity and isolation are the tools the database gives you to make that possible."
          },
          {
            "type": "note",
            "text": "Atomicity handles crashes and errors in the middle of one transaction. Isolation handles other transactions running at the same time. They are different problems with different machinery."
          }
        ]
      },
      {
        "title": "Commit and rollback",
        "body": [
          {
            "type": "p",
            "html": "The canonical example: move money between accounts. Two <code>UPDATE</code>s must both happen, or neither. If the second one fails &mdash; a constraint, a crash, a lost connection &mdash; the first must be undone."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\", isolation_level=None)   # we issue BEGIN ourselves\ndb.execute(\"CREATE TABLE acct(name TEXT PRIMARY KEY, bal INT CHECK (bal >= 0))\")\ndb.execute(\"INSERT INTO acct VALUES ('alice', 100), ('bob', 50)\")\n\ndef transfer(src, dst, amount):\n    db.execute(\"BEGIN\")\n    try:\n        db.execute(\"UPDATE acct SET bal = bal + ? WHERE name = ?\", (amount, dst))\n        db.execute(\"UPDATE acct SET bal = bal - ? WHERE name = ?\", (amount, src))\n        db.execute(\"COMMIT\")\n        print(f\"moved {amount}\")\n    except sqlite3.IntegrityError as e:\n        db.execute(\"ROLLBACK\")\n        print(f\"rolled back: {e}\")\n\ntransfer(\"alice\", \"bob\", 30)\ntransfer(\"alice\", \"bob\", 500)      # second UPDATE violates the CHECK\nprint(dict(db.execute(\"SELECT * FROM acct\")))",
            "label": "the credit to bob is undone when the debit fails",
            "output": "moved 30\nrolled back: CHECK constraint failed: bal >= 0\n{'alice': 70, 'bob': 80}",
            "isError": false
          },
          {
            "type": "p",
            "html": "The failed transfer credited Bob first. Without atomicity, 500 would have appeared from nowhere. With it, the rollback put the database back exactly as it was."
          },
          {
            "type": "p",
            "html": "<strong>Savepoints</strong> give partial rollback inside one transaction: <code>SAVEPOINT s</code>, then <code>ROLLBACK TO s</code> discards only the work after it. ORMs use them to implement nested transactions."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\", isolation_level=None)\ndb.execute(\"CREATE TABLE log(msg TEXT)\")\ndb.execute(\"BEGIN\")\ndb.execute(\"INSERT INTO log VALUES ('order accepted')\")\ndb.execute(\"SAVEPOINT risk\")\ndb.execute(\"INSERT INTO log VALUES ('hedge placed')\")\ndb.execute(\"ROLLBACK TO risk\")            # undo only the hedge\ndb.execute(\"INSERT INTO log VALUES ('hedge skipped')\")\ndb.execute(\"COMMIT\")\nprint([m for (m,) in db.execute(\"SELECT msg FROM log\")])",
            "label": "savepoints",
            "output": "['order accepted', 'hedge skipped']",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Python&rsquo;s <code>sqlite3</code> module historically opened transactions implicitly before DML and never before DDL, which surprised many people. Since Python 3.12 the <code>autocommit</code> connection attribute gives PEP 249-conforming behaviour. Passing <code>isolation_level=None</code>, as here, means &ldquo;do nothing implicitly; I will write BEGIN myself&rdquo;."
          }
        ]
      },
      {
        "title": "Isolation levels and the anomalies they allow",
        "body": [
          {
            "type": "p",
            "html": "Running every transaction one at a time (<em>serial</em> execution) would make isolation trivial and throughput terrible. Isolation levels are a menu of weaker guarantees that allow more concurrency. The SQL standard defines them by which anomalies they permit:"
          },
          {
            "type": "table",
            "head": [
              "Anomaly",
              "What happens"
            ],
            "rows": [
              [
                "<strong>Dirty read</strong>",
                "You read another transaction&rsquo;s uncommitted write, which may then be rolled back"
              ],
              [
                "<strong>Non-repeatable read</strong>",
                "You read a row twice and get different values, because someone committed an update in between"
              ],
              [
                "<strong>Phantom read</strong>",
                "You run the same <code>WHERE</code> query twice and get a different <em>set</em> of rows, because someone inserted or deleted a matching row"
              ],
              [
                "<strong>Lost update</strong>",
                "Two transactions read-modify-write the same row; one write silently overwrites the other"
              ],
              [
                "<strong>Write skew</strong>",
                "Two transactions read overlapping data, write <em>different</em> rows, and together break an invariant neither broke alone"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The model below is a multi-version store: every write appends a version tagged with its writer, and each isolation level is nothing more than a different rule for which versions a reader may see. Running the three classic scenarios under each rule:"
          },
          {
            "type": "code",
            "src": "class DB:\n    def __init__(self, rows):\n        self.versions = {k: [(v, 0)] for k, v in rows.items()}  # key -> [(value, writer)]\n        self.committed, self.next_id = {0}, 1\n\n    def begin(self, level):\n        return Txn(self, level)\n\nclass Txn:\n    def __init__(self, db, level):\n        self.db, self.level, self.id = db, level, db.next_id\n        db.next_id += 1\n        self.snapshot = set(db.committed)        # who had committed when we started\n\n    def visible(self, writer):\n        if writer == self.id or self.level == \"read uncommitted\":\n            return True\n        if self.level == \"read committed\":        # latest committed, per statement\n            return writer in self.db.committed\n        return writer in self.snapshot            # snapshot: frozen at BEGIN\n\n    def get(self, key):\n        for value, writer in reversed(self.db.versions.get(key, [])):\n            if self.visible(writer):\n                return value\n        return None\n\n    def keys(self):\n        return [k for k in self.db.versions if self.get(k) is not None]\n\n    def put(self, key, value):\n        self.db.versions.setdefault(key, []).append((value, self.id))\n\n    def commit(self):\n        self.db.committed.add(self.id)\n\ndef dirty(level):\n    db = DB({\"alice\": 100})\n    t1, t2 = db.begin(level), db.begin(level)\n    t2.put(\"alice\", 0)                        # not committed\n    return t1.get(\"alice\") == 0\n\ndef non_repeatable(level):\n    db = DB({\"alice\": 100})\n    t1, t2 = db.begin(level), db.begin(level)\n    first = t1.get(\"alice\")\n    t2.put(\"alice\", 0); t2.commit()\n    return t1.get(\"alice\") != first\n\ndef phantom(level):\n    db = DB({\"alice\": 100, \"bob\": 50})\n    t1, t2 = db.begin(level), db.begin(level)\n    first = len(t1.keys())\n    t2.put(\"carol\", 70); t2.commit()          # a new matching row\n    return len(t1.keys()) != first\n\nprint(f\"{'level':<17} {'dirty':>6} {'non-rep':>8} {'phantom':>8}\")\nfor level in (\"read uncommitted\", \"read committed\", \"snapshot\"):\n    row = [\"yes\" if f(level) else \"-\" for f in (dirty, non_repeatable, phantom)]\n    print(f\"{level:<17} {row[0]:>6} {row[1]:>8} {row[2]:>8}\")",
            "label": "which anomalies does each visibility rule allow?",
            "output": "level              dirty  non-rep  phantom\nread uncommitted     yes      yes      yes\nread committed         -      yes      yes\nsnapshot               -        -        -",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Read committed</strong> takes a fresh view per statement, so it never sees uncommitted data but can see different committed data on each read. <strong>Snapshot</strong> fixes the view when the transaction starts, so every read is repeatable and no phantoms appear."
          },
          {
            "type": "p",
            "html": "What the real engines do:"
          },
          {
            "type": "table",
            "head": [
              "Engine",
              "Default level",
              "Notes"
            ],
            "rows": [
              [
                "PostgreSQL",
                "Read committed",
                "<code>REPEATABLE READ</code> is snapshot isolation; <code>SERIALIZABLE</code> is SSI (detects dangerous read/write patterns and aborts)"
              ],
              [
                "MySQL InnoDB",
                "Repeatable read",
                "Plain <code>SELECT</code>s read a snapshot; locking reads and <code>UPDATE</code>s read the <em>latest</em> version and take next-key (gap) locks"
              ],
              [
                "Oracle",
                "Read committed",
                "Its <code>SERIALIZABLE</code> is actually snapshot isolation"
              ],
              [
                "SQL Server",
                "Read committed (locking)",
                "<code>READ_COMMITTED_SNAPSHOT</code> and <code>SNAPSHOT</code> are opt-in MVCC modes"
              ],
              [
                "SQLite",
                "Serializable",
                "One writer at a time for the whole database, so most anomalies cannot happen"
              ]
            ]
          },
          {
            "type": "p",
            "html": "SQLite does support one weaker mode, <code>read_uncommitted</code>, between connections that share a cache. It is the easiest place to see a real dirty read:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\nuri = \"file:bank?mode=memory&cache=shared\"\nwriter = sqlite3.connect(uri, uri=True, isolation_level=None)\nreader = sqlite3.connect(uri, uri=True, isolation_level=None)\nwriter.execute(\"CREATE TABLE acct(name TEXT PRIMARY KEY, bal INT)\")\nwriter.execute(\"INSERT INTO acct VALUES ('alice', 100)\")\n\nwriter.execute(\"BEGIN\")\nwriter.execute(\"UPDATE acct SET bal = 0 WHERE name = 'alice'\")\n\nreader.execute(\"PRAGMA read_uncommitted = 1\")\nprint(\"reader sees (dirty):\", reader.execute(\"SELECT bal FROM acct\").fetchone()[0])\n\nwriter.execute(\"ROLLBACK\")\nprint(\"after rollback:     \", reader.execute(\"SELECT bal FROM acct\").fetchone()[0])",
            "label": "a real dirty read",
            "output": "reader sees (dirty): 0\nafter rollback:      100",
            "isError": false
          },
          {
            "type": "p",
            "html": "The reader acted on a balance of 0 that never existed."
          }
        ]
      },
      {
        "title": "MVCC: readers don&rsquo;t block writers",
        "body": [
          {
            "type": "p",
            "html": "The oldest way to implement isolation is locking: readers take shared locks, writers take exclusive locks, and they wait for each other. <strong>Multi-version concurrency control</strong> instead keeps several versions of each row. A writer creates a new version rather than overwriting in place; a reader picks the version that was committed as of its snapshot. Readers never wait for writers and writers never wait for readers. Writers still conflict with other writers of the same row."
          },
          {
            "type": "table",
            "head": [
              "Engine",
              "Where old versions live",
              "Cleanup"
            ],
            "rows": [
              [
                "PostgreSQL",
                "In the table itself: each tuple has <code>xmin</code> (creating txid) and <code>xmax</code> (deleting txid); an update writes a whole new tuple",
                "<code>VACUUM</code> reclaims dead tuples"
              ],
              [
                "MySQL InnoDB, Oracle",
                "The row is updated in place; previous versions are reconstructed from the <em>undo log</em>",
                "Purge thread discards undo no snapshot needs"
              ],
              [
                "SQLite (WAL mode)",
                "Changed pages are appended to the WAL; a reader remembers how much of the WAL it may see",
                "Checkpoint copies WAL pages back into the database file"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import os, sqlite3, tempfile\n\npath = os.path.join(tempfile.mkdtemp(), \"demo.db\")\na = sqlite3.connect(path, isolation_level=None)\na.execute(\"PRAGMA journal_mode = WAL\")\na.execute(\"CREATE TABLE price(sym TEXT, px REAL)\")\na.execute(\"INSERT INTO price VALUES ('ABC', 10.0)\")\n\nb = sqlite3.connect(path, isolation_level=None)\nb.execute(\"BEGIN\")\nprint(\"b reads:\", b.execute(\"SELECT px FROM price\").fetchone()[0])  # snapshot taken here\n\na.execute(\"UPDATE price SET px = 11.0\")        # writer is not blocked by b\nprint(\"a reads:\", a.execute(\"SELECT px FROM price\").fetchone()[0])\nprint(\"b reads:\", b.execute(\"SELECT px FROM price\").fetchone()[0])  # still its snapshot\nb.execute(\"COMMIT\")\nprint(\"b, new transaction:\", b.execute(\"SELECT px FROM price\").fetchone()[0])",
            "label": "a WAL-mode reader keeps its snapshot while a writer commits",
            "output": "b reads: 10.0\na reads: 11.0\nb reads: 10.0\nb, new transaction: 11.0",
            "isError": false
          },
          {
            "type": "p",
            "html": "The cost of MVCC is garbage. Every old version must be kept until no running transaction might need it, which means <strong>one long-running transaction pins every version created after it started</strong> &mdash; across the whole database. Tables bloat, indexes bloat, and in PostgreSQL <code>VACUUM</code> can do nothing until that transaction ends."
          },
          {
            "type": "note",
            "text": "Keep transactions short. Never hold one open across a network call, a user prompt, or a <code>sleep</code>."
          }
        ]
      },
      {
        "title": "Snapshot isolation and write skew",
        "body": [
          {
            "type": "p",
            "html": "Snapshot isolation stops dirty reads, non-repeatable reads and phantoms. It also prevents lost updates, with a rule called <strong>first committer wins</strong>: if two transactions update the same row, the second to commit is aborted. SQLite enforces the same thing when a reader with an old snapshot tries to become a writer:"
          },
          {
            "type": "code",
            "src": "import os, sqlite3, tempfile\n\npath = os.path.join(tempfile.mkdtemp(), \"demo.db\")\na = sqlite3.connect(path, isolation_level=None)\na.execute(\"PRAGMA journal_mode = WAL\")\na.execute(\"CREATE TABLE counter(n INT)\")\na.execute(\"INSERT INTO counter VALUES (0)\")\n\nb = sqlite3.connect(path, isolation_level=None)   # default 5 s busy timeout\nb.execute(\"BEGIN\")\nn = b.execute(\"SELECT n FROM counter\").fetchone()[0]      # b's snapshot: n = 0\n\na.execute(\"UPDATE counter SET n = n + 1\")                 # a commits n = 1\ntry:\n    b.execute(\"UPDATE counter SET n = ?\", (n + 1,))       # would overwrite a's update\nexcept sqlite3.OperationalError as e:\n    print(f\"b refused at once: {e} ({e.sqlite_errorname})\")\n    b.execute(\"ROLLBACK\")\nprint(\"n =\", a.execute(\"SELECT n FROM counter\").fetchone()[0])",
            "label": "a stale snapshot is not allowed to write",
            "output": "b refused at once: database is locked (SQLITE_BUSY_SNAPSHOT)\nn = 1",
            "isError": false
          },
          {
            "type": "p",
            "html": "The message is SQLite&rsquo;s generic one; the extended code <code>SQLITE_BUSY_SNAPSHOT</code> means &ldquo;your snapshot is out of date, retry the whole transaction&rdquo;. Waiting would not help, so it fails immediately instead of spending the five-second busy timeout."
          },
          {
            "type": "p",
            "html": "What snapshot isolation does <em>not</em> prevent is <strong>write skew</strong>. Two transactions read the same data, each decides its write is safe, and each writes a <em>different</em> row. There is no write-write conflict to detect, so both commit. The textbook case: a hospital requires at least one doctor on call, two are on call, and both ask to go off call at the same moment."
          },
          {
            "type": "code",
            "src": "class DB:\n    def __init__(self, rows):\n        self.versions = {k: [(v, 0)] for k, v in rows.items()}  # key -> [(value, writer)]\n        self.committed, self.next_id = {0}, 1\n\n    def begin(self, level):\n        return Txn(self, level)\n\nclass Txn:\n    def __init__(self, db, level):\n        self.db, self.level, self.id = db, level, db.next_id\n        db.next_id += 1\n        self.snapshot = set(db.committed)        # who had committed when we started\n\n    def visible(self, writer):\n        if writer == self.id or self.level == \"read uncommitted\":\n            return True\n        if self.level == \"read committed\":        # latest committed, per statement\n            return writer in self.db.committed\n        return writer in self.snapshot            # snapshot: frozen at BEGIN\n\n    def get(self, key):\n        for value, writer in reversed(self.db.versions.get(key, [])):\n            if self.visible(writer):\n                return value\n        return None\n\n    def keys(self):\n        return [k for k in self.db.versions if self.get(k) is not None]\n\n    def put(self, key, value):\n        self.db.versions.setdefault(key, []).append((value, self.id))\n\n    def commit(self):\n        self.db.committed.add(self.id)\n\ndb = DB({\"alice\": \"on\", \"bob\": \"on\"})\n\ndef go_off_call(t, me):\n    on_call = [k for k in t.keys() if t.get(k) == \"on\"]\n    if len(on_call) >= 2:                 # \"someone else will still be on call\"\n        t.put(me, \"off\")\n\nt1, t2 = db.begin(\"snapshot\"), db.begin(\"snapshot\")\ngo_off_call(t1, \"alice\")\ngo_off_call(t2, \"bob\")\nt1.commit(); t2.commit()                  # different rows: no conflict\n\nfinal = db.begin(\"snapshot\")\nprint({k: final.get(k) for k in final.keys()})",
            "label": "write skew: each transaction is correct alone, together they are not",
            "output": "{'alice': 'off', 'bob': 'off'}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Nobody is on call. The same shape appears in trading systems as two orders that each pass a risk check against the same limit, or two bookings for the last seat checked against a count."
          },
          {
            "type": "p",
            "html": "Fixes, from narrowest to broadest:"
          },
          {
            "type": "p",
            "html": "<strong>Lock what you read.</strong> <code>SELECT ... FOR UPDATE</code> on the rows the decision depends on turns the read into a write-lock, so the second transaction waits.<br><strong>Materialise the conflict.</strong> If the invariant is about rows that might not exist yet, give it a row that does &mdash; a per-limit or per-shift row both transactions must update.<br><strong>Use a constraint.</strong> Where the invariant can be declared (unique, exclusion constraint), the database checks it atomically.<br><strong>Use <code>SERIALIZABLE</code>.</strong> PostgreSQL&rsquo;s serializable snapshot isolation tracks read/write dependencies and aborts one of the two; your code must then retry."
          },
          {
            "type": "caveat",
            "text": "<code>SERIALIZABLE</code> in PostgreSQL and CockroachDB will abort transactions with a serialization failure (SQLSTATE <code>40001</code>) as a normal part of operation. Code that runs at that level needs a retry loop, and the transaction body must be safe to re-run."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Two requests each run <code>SELECT qty FROM stock WHERE id = 1</code>, compute <code>qty - 1</code> in the application, and write it back under READ COMMITTED. What goes wrong and what are the fixes?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A <strong>lost update</strong>. Both read 10, both write 9, one decrement disappears. Read committed does nothing about it: each statement sees committed data, and the second write simply overwrites the first."
          },
          {
            "type": "p",
            "html": "Fixes, in order of preference:"
          },
          {
            "type": "p",
            "html": "<strong>Make it one atomic statement:</strong> <code>UPDATE stock SET qty = qty - 1 WHERE id = 1 AND qty &gt; 0</code>. The row lock taken by the <code>UPDATE</code> serialises the two; checking the affected row count tells you whether it succeeded.<br><strong>Pessimistic lock:</strong> <code>SELECT ... FOR UPDATE</code>, so the second reader waits for the first to commit.<br><strong>Optimistic check:</strong> add a <code>version</code> column and <code>UPDATE ... SET qty = ?, version = version + 1 WHERE id = 1 AND version = ?</code>; zero rows updated means someone else won, so retry.<br><strong>Raise isolation:</strong> PostgreSQL&rsquo;s <code>REPEATABLE READ</code> aborts the second writer (first committer wins)."
          }
        ]
      },
      {
        "q": "Explain the difference between REPEATABLE READ in PostgreSQL and in MySQL InnoDB.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<strong>PostgreSQL</strong>: REPEATABLE READ is snapshot isolation. Every statement, reads and writes alike, sees the snapshot taken at the transaction&rsquo;s first statement. If you try to update a row that someone else changed and committed after your snapshot, you get a serialization error and must retry. No phantoms, no lost updates; write skew is still possible."
          },
          {
            "type": "p",
            "html": "<strong>MySQL InnoDB</strong>: plain <code>SELECT</code>s read a consistent snapshot, but <code>UPDATE</code>, <code>DELETE</code> and <code>SELECT ... FOR UPDATE</code> perform <em>current reads</em> of the latest committed version and lock it. So within one transaction a <code>SELECT</code> can say a row has <code>qty = 10</code> while <code>UPDATE ... SET qty = qty - 1</code> acts on the newer 7. There is no serialization error: the update just applies to the latest data. Locking reads also take next-key (gap) locks to prevent phantoms in the ranges they scanned, which is a common source of unexpected lock waits and deadlocks."
          },
          {
            "type": "p",
            "html": "The practical upshot: the same application code can be correct on one and subtly wrong on the other, so know which one you are on."
          }
        ]
      },
      {
        "q": "What does the C in ACID mean, and how does it differ from the C in CAP?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "ACID consistency means each transaction takes the database from one state that satisfies its invariants to another. The database enforces the invariants it can see (constraints, foreign keys, uniqueness); the rest is the application&rsquo;s responsibility, using atomicity and isolation as tools. It is arguably a property of the application rather than the database."
          },
          {
            "type": "p",
            "html": "CAP consistency means <em>linearizability</em>: in a replicated system, every read returns the most recent completed write, as if there were a single copy of the data. It is about replicas agreeing, not about invariants. A single-node database can be ACID-consistent without the concept of CAP consistency even applying; a replicated store can be linearizable while holding data that violates business rules."
          }
        ]
      },
      {
        "q": "Why can a single forgotten open transaction hurt an MVCC database for hours?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "MVCC can only discard an old row version once no running transaction could need it. The oldest open snapshot sets that horizon for the whole database. An idle-in-transaction session opened this morning therefore pins every version created since this morning, on every table."
          },
          {
            "type": "p",
            "html": "Effects in PostgreSQL: <code>VACUUM</code> runs but cannot remove dead tuples, so tables and indexes bloat and scans slow down; index-only scans degrade because pages cannot be marked all-visible; in the extreme, transaction-ID wraparound protection eventually forces the database into a protective shutdown. In InnoDB the undo log (history list) grows without bound and every read that must reconstruct an old version walks a longer chain."
          },
          {
            "type": "p",
            "html": "Defences: <code>idle_in_transaction_session_timeout</code> (PostgreSQL), monitoring <code>pg_stat_activity</code> for old <code>xact_start</code> or InnoDB&rsquo;s history list length, and application discipline &mdash; never hold a transaction open across I/O you do not control. Replication slots and long-running queries on hot standbys with <code>hot_standby_feedback</code> have the same pinning effect."
          }
        ]
      },
      {
        "q": "Two risk checks run concurrently, each verifying a trader&rsquo;s total exposure is under a limit before inserting a new order row. Both pass and the limit is breached. The database runs snapshot isolation. Why, and how do you fix it?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "It is write skew. Each transaction reads the same set of existing orders from its snapshot, sees headroom, and inserts a <em>new, different</em> row. Snapshot isolation only detects two writes to the same row, so there is no conflict and both commit. (If it were a phantom-style read of a range, snapshot isolation would still not help, because the phantom is in the other transaction&rsquo;s write, not in your reads.)"
          },
          {
            "type": "p",
            "html": "Fixes: give the invariant a row to conflict on &mdash; a <code>trader_exposure</code> row updated atomically with <code>UPDATE ... SET used = used + ? WHERE trader = ? AND used + ? &lt;= limit</code> and checked for one affected row; or <code>SELECT ... FOR UPDATE</code> on the trader&rsquo;s row before the check; or run at <code>SERIALIZABLE</code> and retry on <code>40001</code>."
          },
          {
            "type": "p",
            "html": "In a latency-sensitive system the usual answer is not to use the database for this at all: route every order for one trader through a single thread that owns that trader&rsquo;s exposure in memory, so the check-and-reserve is naturally serial, and persist the result afterwards."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "PostgreSQL: transaction isolation",
        "url": "https://www.postgresql.org/docs/current/transaction-iso.html"
      },
      {
        "label": "MySQL: InnoDB transaction isolation levels",
        "url": "https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html"
      },
      {
        "label": "SQLite: isolation in SQLite",
        "url": "https://www.sqlite.org/isolation.html"
      },
      {
        "label": "Berenson et al. — A Critique of ANSI SQL Isolation Levels",
        "url": "https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/"
      },
      {
        "label": "Hermitage: testing isolation levels across databases",
        "url": "https://github.com/ept/hermitage"
      }
    ]
  },
  {
    "id": "locking",
    "title": "Concurrency and Locking",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Shared and exclusive locks, two-phase locking, deadlocks, and optimistic vs pessimistic control.",
    "intro": [
      "MVCC removed most reader/writer blocking, but writers still have to be kept from trampling each other, and <code>SELECT ... FOR UPDATE</code>, foreign-key checks, unique-index inserts and DDL all take locks even in an MVCC engine. When a production database stalls, the cause is very often a lock queue, and the most common database error in a busy service after timeouts is a deadlock.",
      "This page covers the lock modes and their compatibility, lock granularity, two-phase locking and why it makes schedules serializable, how deadlocks form and are detected, and the choice between optimistic and pessimistic concurrency &mdash; including the lock-free, single-writer designs latency-sensitive systems prefer."
    ],
    "sections": [
      {
        "title": "Shared and exclusive locks",
        "body": [
          {
            "type": "p",
            "html": "The two basic modes: a <strong>shared (S)</strong> lock lets you read and lets others read too; an <strong>exclusive (X)</strong> lock lets you write and keeps everyone else out. Whether a request is granted depends on what is already held:"
          },
          {
            "type": "table",
            "head": [
              "Held → / Requested ↓",
              "none",
              "S",
              "X"
            ],
            "rows": [
              [
                "S",
                "grant",
                "grant",
                "wait"
              ],
              [
                "X",
                "grant",
                "wait",
                "wait"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Databases lock at several granularities at once, so they add <strong>intention locks</strong>. Before taking an X lock on a row, a transaction takes an <em>intention-exclusive (IX)</em> lock on the table. Someone who wants to lock the whole table in S mode can now see, by checking one table-level lock, that a row inside it is being written &mdash; without scanning millions of row locks."
          },
          {
            "type": "table",
            "head": [
              "Held → / Requested ↓",
              "IS",
              "IX",
              "S",
              "X"
            ],
            "rows": [
              [
                "IS",
                "grant",
                "grant",
                "grant",
                "wait"
              ],
              [
                "IX",
                "grant",
                "grant",
                "wait",
                "wait"
              ],
              [
                "S",
                "grant",
                "wait",
                "grant",
                "wait"
              ],
              [
                "X",
                "wait",
                "wait",
                "wait",
                "wait"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Two transactions updating different rows both take IX on the table (compatible) and X on their own row (no conflict), so they run in parallel. A <code>LOCK TABLE ... IN SHARE MODE</code> or an <code>ALTER TABLE</code> has to wait for both."
          },
          {
            "type": "p",
            "html": "In an MVCC engine, plain reads take no row locks at all. The places you still meet S and X locks: <code>UPDATE</code>/<code>DELETE</code> (X on each row changed), <code>SELECT ... FOR UPDATE</code> (X) and <code>FOR SHARE</code> (S), foreign-key checks (a shared lock on the parent row), unique-index checks, and schema changes (a table-level exclusive lock)."
          }
        ]
      },
      {
        "title": "Row, page and table locks",
        "body": [
          {
            "type": "p",
            "html": "Finer locks allow more concurrency and cost more memory and bookkeeping; coarser locks are cheap and serialise more."
          },
          {
            "type": "table",
            "head": [
              "Granularity",
              "Who uses it",
              "Trade-off"
            ],
            "rows": [
              [
                "Row",
                "InnoDB, PostgreSQL, Oracle, SQL Server",
                "Maximum concurrency; one lock per row touched"
              ],
              [
                "Page",
                "SQL Server (sometimes), older engines",
                "Middle ground; unrelated rows on one page collide"
              ],
              [
                "Table",
                "MyISAM, DDL everywhere, <code>LOCK TABLE</code>",
                "Cheap; one writer per table"
              ],
              [
                "Database",
                "SQLite",
                "Trivial to get right; exactly one writer at a time"
              ]
            ]
          },
          {
            "type": "p",
            "html": "<strong>Lock escalation</strong>: SQL Server converts many row locks on one table (around 5,000) into a single table lock to save memory, which can suddenly block unrelated work. PostgreSQL never escalates row locks because it stores them in the tuple header rather than in a lock table."
          },
          {
            "type": "p",
            "html": "SQLite is the extreme case &mdash; one writer for the whole file. <code>BEGIN IMMEDIATE</code> takes the write lock up front; a second writer gets <code>SQLITE_BUSY</code> after its timeout:"
          },
          {
            "type": "code",
            "src": "import os, sqlite3, tempfile\n\npath = os.path.join(tempfile.mkdtemp(), \"demo.db\")\na = sqlite3.connect(path, isolation_level=None, timeout=0.1)\na.execute(\"PRAGMA journal_mode = WAL\")\na.execute(\"CREATE TABLE t(x)\")\nb = sqlite3.connect(path, isolation_level=None, timeout=0.1)\n\na.execute(\"BEGIN IMMEDIATE\")                  # a is now the writer\na.execute(\"INSERT INTO t VALUES (1)\")\nprint(\"b can still read:\", b.execute(\"SELECT count(*) FROM t\").fetchone()[0])\ntry:\n    b.execute(\"BEGIN IMMEDIATE\")\nexcept sqlite3.OperationalError as e:\n    print(\"b cannot write:\", e.sqlite_errorname)\na.execute(\"COMMIT\")\nb.execute(\"BEGIN IMMEDIATE\")\nprint(\"after a commits, b writes\")\nb.execute(\"COMMIT\")",
            "label": "one writer per database, readers unaffected (WAL mode)",
            "output": "b can still read: 0\nb cannot write: SQLITE_BUSY\nafter a commits, b writes",
            "isError": false
          },
          {
            "type": "note",
            "text": "Prefer <code>BEGIN IMMEDIATE</code> for any SQLite transaction that will write. A deferred transaction that reads first and writes later can fail at the write with <code>SQLITE_BUSY_SNAPSHOT</code> and has to be retried from the start."
          }
        ]
      },
      {
        "title": "Two-phase locking",
        "body": [
          {
            "type": "p",
            "html": "<strong>Two-phase locking (2PL)</strong> is the rule that makes lock-based concurrency serializable: a transaction has a <em>growing</em> phase in which it may acquire locks, then a <em>shrinking</em> phase in which it may release them, and once it has released any lock it may never acquire another."
          },
          {
            "type": "p",
            "html": "Why that works: at the moment a transaction holds all its locks (the <em>lock point</em>), nothing it read or wrote can be changed by anyone else. Ordering transactions by their lock points gives an equivalent serial order."
          },
          {
            "type": "p",
            "html": "Plain 2PL has a hole: if a transaction releases an X lock during its shrinking phase and then aborts, someone may already have read its uncommitted write &mdash; a cascading abort. <strong>Strict 2PL</strong> holds all exclusive locks until commit or abort; <strong>strong strict 2PL</strong> (rigorous) holds all locks until then. Real lock-based databases use the strict forms, which is why &ldquo;locks are released at commit&rdquo; is the everyday rule."
          },
          {
            "type": "code",
            "src": "class Txn:\n    def __init__(self, name):\n        self.name, self.held, self.shrinking = name, set(), False\n\n    def lock(self, item):\n        if self.shrinking:\n            raise RuntimeError(f\"{self.name}: 2PL violation, lock({item}) after an unlock\")\n        self.held.add(item)\n\n    def unlock(self, item):\n        self.shrinking = True\n        self.held.discard(item)\n\nok = Txn(\"T1\")\nok.lock(\"A\"); ok.lock(\"B\")          # growing\nok.unlock(\"A\"); ok.unlock(\"B\")      # shrinking\nprint(\"T1 followed 2PL\")\n\nbad = Txn(\"T2\")\nbad.lock(\"A\"); bad.unlock(\"A\")\ntry:\n    bad.lock(\"B\")\nexcept RuntimeError as e:\n    print(e)",
            "label": "the rule itself fits in one flag",
            "output": "T1 followed 2PL\nT2: 2PL violation, lock(B) after an unlock",
            "isError": false
          },
          {
            "type": "p",
            "html": "What goes wrong without it: T2 reads A, releases it, T1 writes A and B and commits, then T2 reads B. T2 saw A from before T1 and B from after &mdash; a state that never existed at any single point in time."
          },
          {
            "type": "caveat",
            "text": "Two-phase <em>locking</em> is unrelated to two-phase <em>commit</em>. 2PC is a protocol for committing one transaction atomically across several machines (prepare, then commit). Interviewers ask about both and like to check you do not mix them up."
          }
        ]
      },
      {
        "title": "Deadlocks: detection and prevention",
        "body": [
          {
            "type": "p",
            "html": "A deadlock is a cycle of waiting: T1 holds A and wants B, T2 holds B and wants A. Neither can proceed. 2PL makes deadlocks possible, because transactions hold locks while acquiring more."
          },
          {
            "type": "p",
            "html": "<strong>Detection.</strong> The lock manager maintains a <em>wait-for graph</em>: an edge T1 &rarr; T2 means T1 is waiting for a lock T2 holds. A cycle is a deadlock. The engine picks a victim (usually the transaction that has done the least work), aborts it, and the others continue. PostgreSQL runs this check after a lock wait exceeds <code>deadlock_timeout</code> (1&nbsp;s); InnoDB checks on every wait."
          },
          {
            "type": "code",
            "src": "def find_cycle(waits_for):\n    \"\"\"waits_for: txn -> txn it is blocked on. Return one cycle, or None.\"\"\"\n    for start in waits_for:\n        path, node = [], start\n        while node in waits_for and node not in path:\n            path.append(node)\n            node = waits_for[node]\n        if node in path:\n            return path[path.index(node):]\n    return None\n\nwork_done = {\"T1\": 40, \"T2\": 3, \"T3\": 12, \"T4\": 7}\n\ngraphs = {\n    \"chain\": {\"T1\": \"T2\", \"T2\": \"T3\"},\n    \"two-way\": {\"T1\": \"T2\", \"T2\": \"T1\"},\n    \"three-way\": {\"T1\": \"T2\", \"T2\": \"T3\", \"T3\": \"T1\", \"T4\": \"T1\"},\n}\nfor name, g in graphs.items():\n    cycle = find_cycle(g)\n    if cycle is None:\n        print(f\"{name:<10} no deadlock, just waiting\")\n    else:\n        victim = min(cycle, key=work_done.get)\n        print(f\"{name:<10} cycle {' -> '.join(cycle + cycle[:1])}; abort {victim}\")",
            "label": "a wait-for graph and victim selection",
            "output": "chain      no deadlock, just waiting\ntwo-way    cycle T1 -> T2 -> T1; abort T2\nthree-way  cycle T1 -> T2 -> T3 -> T1; abort T2",
            "isError": false
          },
          {
            "type": "p",
            "html": "T4 waits on the three-way cycle but is not part of it; aborting T2 frees the cycle and T4 simply waits a little longer."
          },
          {
            "type": "p",
            "html": "<strong>Prevention.</strong> Stop cycles forming in the first place:"
          },
          {
            "type": "table",
            "head": [
              "Technique",
              "How",
              "Cost"
            ],
            "rows": [
              [
                "Global lock order",
                "Always lock rows in the same order, e.g. by primary key",
                "Needs discipline everywhere; the standard application-level fix"
              ],
              [
                "Lock everything up front",
                "Acquire all locks at the start (conservative 2PL)",
                "Must know the lock set in advance; lower concurrency"
              ],
              [
                "Wait-die",
                "An older transaction may wait for a younger one; a younger one requesting from an older one aborts",
                "Some needless aborts; no cycles possible"
              ],
              [
                "Wound-wait",
                "An older transaction aborts (wounds) a younger holder; a younger requester waits",
                "Same idea, older transactions never wait for younger"
              ],
              [
                "Timeouts",
                "Give up after N ms (<code>lock_timeout</code>, <code>innodb_lock_wait_timeout</code>)",
                "Simple; aborts slow-but-innocent transactions too"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The same thing happens with application locks. Two threads transferring in opposite directions deadlock; sorting the locks removes the cycle:"
          },
          {
            "type": "code",
            "src": "import threading\n\ndef run(ordered):\n    locks = {\"alice\": threading.Lock(), \"bob\": threading.Lock()}\n    both_hold_first = threading.Barrier(2, timeout=0.3)\n    done = []\n\n    def transfer(src, dst):\n        first, second = sorted((src, dst)) if ordered else (src, dst)\n        with locks[first]:\n            if not ordered:\n                both_hold_first.wait()     # force the bad interleaving\n            got = locks[second].acquire(timeout=0.3)\n            if got:\n                locks[second].release()\n            done.append(got)\n\n    ts = [threading.Thread(target=transfer, args=(\"alice\", \"bob\")),\n          threading.Thread(target=transfer, args=(\"bob\", \"alice\"))]\n    for t in ts: t.start()\n    for t in ts: t.join()\n    return \"both completed\" if all(done) else \"deadlock (lock wait timed out)\"\n\nprint(\"each locks its source first ->\", run(ordered=False))\nprint(\"both lock in sorted order   ->\", run(ordered=True))",
            "label": "opposite-direction transfers",
            "output": "each locks its source first -> deadlock (lock wait timed out)\nboth lock in sorted order   -> both completed",
            "isError": false
          },
          {
            "type": "note",
            "text": "Deadlocks are a normal event in a busy OLTP database, not a bug to be eliminated entirely. Keep transactions short, touch rows in a consistent order, and wrap transactions in a retry on deadlock errors (SQLSTATE <code>40P01</code> in PostgreSQL, error 1213 in MySQL)."
          }
        ]
      },
      {
        "title": "Optimistic vs pessimistic concurrency",
        "body": [
          {
            "type": "p",
            "html": "<strong>Pessimistic</strong>: assume conflicts will happen, so lock first (<code>SELECT ... FOR UPDATE</code>) and make everyone else wait. <strong>Optimistic</strong>: assume they won&rsquo;t, so do the work without locks and check at write time whether anything changed; if it did, retry."
          },
          {
            "type": "p",
            "html": "The usual optimistic implementation is a version column and a conditional update &mdash; a compare-and-swap at the row level:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\", isolation_level=None)\ndb.execute(\"CREATE TABLE position(sym TEXT PRIMARY KEY, qty INT, version INT)\")\ndb.execute(\"INSERT INTO position VALUES ('ABC', 100, 1)\")\n\ndef read():\n    return db.execute(\"SELECT qty, version FROM position WHERE sym = 'ABC'\").fetchone()\n\ndef write(qty, seen_version):\n    cur = db.execute(\n        \"UPDATE position SET qty = ?, version = version + 1 \"\n        \"WHERE sym = 'ABC' AND version = ?\", (qty, seen_version))\n    return cur.rowcount == 1\n\nqty_a, v_a = read()                  # two clients read version 1\nqty_b, v_b = read()\nprint(\"A writes:\", write(qty_a + 10, v_a))\nprint(\"B writes:\", write(qty_b - 5, v_b))      # stale version: 0 rows match\n\nqty_b, v_b = read()                  # B retries on fresh data\nprint(\"B retry: \", write(qty_b - 5, v_b))\nprint(read())",
            "label": "optimistic concurrency with a version column",
            "output": "A writes: True\nB writes: False\nB retry:  True\n(105, 3)",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "",
              "Pessimistic",
              "Optimistic"
            ],
            "rows": [
              [
                "Conflict handling",
                "Wait for the lock",
                "Detect at commit, retry"
              ],
              [
                "Best when",
                "Contention is high, retries are expensive",
                "Contention is low, reads dominate"
              ],
              [
                "Failure mode",
                "Lock waits, deadlocks, blocked threads",
                "Retry storms under contention; starvation of long transactions"
              ],
              [
                "Holds across user think time?",
                "Never (locks held while a human reads)",
                "Yes &mdash; the classic edit form: load, edit for minutes, save with version check"
              ],
              [
                "Examples",
                "<code>FOR UPDATE</code>, 2PL, <code>synchronized</code>",
                "Version columns, ETags, SSI, CAS loops, STM"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Under high contention optimistic control degrades badly: if ten clients hammer one hot row, nine of them redo their work every round. Under low contention it wins, because nobody pays for locks they never needed."
          }
        ]
      },
      {
        "title": "Lock-free vs lock-based thinking",
        "body": [
          {
            "type": "p",
            "html": "A lock turns contention into waiting, and waiting is unbounded: a thread holding a lock can be descheduled, page-faulted or preempted, and every other thread stalls behind it. For systems measured in microseconds, that tail is the problem, not the average."
          },
          {
            "type": "p",
            "html": "<strong>Lock-free</strong> designs guarantee that some thread always makes progress. They are built on atomic hardware instructions, chiefly <em>compare-and-swap</em>: &ldquo;set this word to <em>new</em> only if it still equals <em>expected</em>&rdquo;. A CAS loop is optimistic concurrency at the level of a single memory word &mdash; the same read, compute, conditional-write, retry shape as the version column above."
          },
          {
            "type": "p",
            "html": "The design that usually wins in practice, though, avoids shared mutable state entirely: the <strong>single-writer principle</strong>. Give each piece of state exactly one owning thread. Everything else sends it messages through a queue. The owner never contends with anyone, so it needs no locks and no CAS on its data, and it can keep that data hot in its own CPU cache."
          },
          {
            "type": "code",
            "src": "import queue, threading, zlib\n\n# One owner thread per shard of symbols; order books are never shared.\nSHARDS = 2\ninboxes = [queue.Queue() for _ in range(SHARDS)]\nbooks = [{} for _ in range(SHARDS)]\n\ndef owner(i):\n    book = books[i]\n    while (msg := inboxes[i].get()) is not None:\n        sym, qty = msg\n        book[sym] = book.get(sym, 0) + qty      # no lock: only this thread writes\n\ndef route(sym, qty):\n    inboxes[zlib.crc32(sym.encode()) % SHARDS].put((sym, qty))\n\nworkers = [threading.Thread(target=owner, args=(i,)) for i in range(SHARDS)]\nfor w in workers: w.start()\nfor sym, qty in [(\"AAPL\", 100), (\"MSFT\", 50), (\"AAPL\", -30), (\"NVDA\", 10), (\"MSFT\", 5)]:\n    route(sym, qty)\nfor q in inboxes: q.put(None)\nfor w in workers: w.join()\nfor i, b in enumerate(books):\n    print(f\"shard {i}: {dict(sorted(b.items()))}\")",
            "label": "the single-writer principle: partition state, not locks",
            "output": "shard 0: {'AAPL': 70}\nshard 1: {'MSFT': 55, 'NVDA': 10}",
            "isError": false
          },
          {
            "type": "p",
            "html": "This is the LMAX Disruptor&rsquo;s central idea, and it is how matching engines, Redis (one thread executes all commands) and VoltDB (one thread per partition, no locks at all) get their throughput. The same idea at database scale is <em>partitioning</em>: route every transaction for a key to the partition that owns it."
          },
          {
            "type": "caveat",
            "text": "Python&rsquo;s <code>queue.Queue</code> uses locks internally, and the GIL serialises the threads anyway. The snippet shows the ownership structure, not the performance; the real thing uses ring buffers with atomic sequence counters in C++, Rust or Java."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Two concurrent transfers, A&rarr;B and B&rarr;A, keep deadlocking in production. Explain exactly why and give two fixes.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Each transfer runs two <code>UPDATE</code>s. Transfer 1 updates A first and holds A&rsquo;s row lock until commit; transfer 2 updates B first and holds B&rsquo;s. Transfer 1 then needs B, transfer 2 needs A: a cycle in the wait-for graph. The database detects it, aborts one (the victim gets a deadlock error), and the other proceeds."
          },
          {
            "type": "p",
            "html": "<strong>Fix 1: consistent order.</strong> Always update the two accounts in ascending ID order regardless of transfer direction. Both transactions now contend for the same first lock and simply queue.<br><strong>Fix 2: lock up front.</strong> <code>SELECT ... FROM accounts WHERE id IN (a, b) ORDER BY id FOR UPDATE</code> before either update.<br><strong>Always:</strong> retry the aborted transaction, because deadlocks can still arise from paths you did not think of (foreign keys, index maintenance, gap locks)."
          }
        ]
      },
      {
        "q": "What is two-phase locking, why does it guarantee serializability, and how is it different from two-phase commit?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "2PL: a transaction acquires locks during a growing phase and releases them during a shrinking phase, never acquiring after it has released. At its lock point it holds every lock it will ever need, so ordering transactions by lock point gives an equivalent serial schedule. Strict 2PL holds write locks until commit to avoid cascading aborts; that is what databases implement."
          },
          {
            "type": "p",
            "html": "Two-phase commit is a distributed <em>atomicity</em> protocol: a coordinator asks every participant to <em>prepare</em> (durably promise it can commit), and only if all say yes tells them all to <em>commit</em>. It says nothing about concurrency control. The two are often used together &mdash; a distributed database may use 2PL on each node and 2PC across nodes &mdash; which is exactly why the names get confused."
          }
        ]
      },
      {
        "q": "How would you implement a job queue in PostgreSQL so that many workers can pull jobs concurrently without blocking each other or taking the same job?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Use <code>SELECT ... FOR UPDATE SKIP LOCKED</code>:"
          },
          {
            "type": "p",
            "html": "<code>BEGIN;<br>SELECT id, payload FROM jobs WHERE status = 'ready' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;<br>-- do the work, or at least claim it<br>UPDATE jobs SET status = 'done' WHERE id = $1;<br>COMMIT;</code>"
          },
          {
            "type": "p",
            "html": "<code>FOR UPDATE</code> locks the chosen row so no other worker can take it. <code>SKIP LOCKED</code> makes other workers skip rows that are locked rather than queue behind them, so each worker grabs the next free job immediately. If a worker crashes, its transaction aborts, the lock is released, and the job becomes visible again."
          },
          {
            "type": "p",
            "html": "Caveats worth mentioning: holding a transaction open for the whole job is a long transaction (MVCC bloat), so for long jobs you claim with a short transaction that sets <code>status = 'running', lease_until = now() + interval</code> and have a reaper reset expired leases. Also index <code>(status, id)</code> or use a partial index <code>WHERE status = 'ready'</code> so the scan stays short as done jobs accumulate."
          }
        ]
      },
      {
        "q": "When would you choose optimistic over pessimistic concurrency, and what happens to each as contention grows?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Optimistic when conflicts are rare, when the critical section spans user think time or a remote call (you cannot hold a lock for that), or when reads vastly outnumber writes. Pessimistic when conflicts are frequent, when the work is expensive to redo, or when you need a guaranteed outcome without retry logic."
          },
          {
            "type": "p",
            "html": "As contention grows, pessimistic throughput falls gradually: transactions queue, latency rises, and deadlock rates increase but work is not wasted. Optimistic throughput can collapse: with N writers on one row, each round one commits and N&minus;1 throw away their work and retry, so wasted work grows with N and long transactions may starve forever behind short ones."
          },
          {
            "type": "p",
            "html": "A good answer adds the middle ground: reduce contention itself. Split a hot counter into N sub-counters and sum on read; make the update a single atomic statement (<code>SET n = n + 1</code>) so the lock is held for microseconds; or route all writes for the hot key through one owner."
          }
        ]
      },
      {
        "q": "Why might an INSERT deadlock with another INSERT in MySQL InnoDB at REPEATABLE READ?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Gap locks. At REPEATABLE READ, InnoDB prevents phantoms by locking not only index records but the <em>gaps</em> between them (next-key locks). A <code>SELECT ... FOR UPDATE</code> or <code>DELETE</code> on a missing key &mdash; common in &ldquo;check if exists, then insert&rdquo; code &mdash; takes a gap lock on the range where that key would go. Gap locks are compatible with each other, so two transactions can both hold one on the same gap."
          },
          {
            "type": "p",
            "html": "Each then tries to <code>INSERT</code> into that gap, which requires an <em>insert intention</em> lock that conflicts with the other&rsquo;s gap lock. Each waits for the other: deadlock."
          },
          {
            "type": "p",
            "html": "Fixes: use <code>INSERT ... ON DUPLICATE KEY UPDATE</code> (or <code>INSERT IGNORE</code>) instead of check-then-insert; rely on the unique index to reject the duplicate and handle the error; or run that code path at READ COMMITTED, where InnoDB mostly disables gap locking."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "PostgreSQL: explicit locking",
        "url": "https://www.postgresql.org/docs/current/explicit-locking.html"
      },
      {
        "label": "MySQL: InnoDB locking",
        "url": "https://dev.mysql.com/doc/refman/8.4/en/innodb-locking.html"
      },
      {
        "label": "SQLite: file locking and concurrency",
        "url": "https://www.sqlite.org/lockingv3.html"
      },
      {
        "label": "Martin Thompson — the single writer principle",
        "url": "https://mechanical-sympathy.blogspot.com/2011/09/single-writer-principle.html"
      },
      {
        "label": "LMAX Disruptor technical paper",
        "url": "https://lmax-exchange.github.io/disruptor/disruptor.html"
      }
    ]
  },
  {
    "id": "query-execution",
    "title": "Query Execution and the Optimizer",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Parsing, planning, scans, the three join algorithms, reading EXPLAIN, and why innocent queries crawl.",
    "intro": [
      "SQL says <em>what</em> you want, never <em>how</em> to get it. Between your query and the data sits a planner that chooses among many equivalent programs &mdash; which index, which join order, which join algorithm &mdash; using statistics that may be stale. Most &ldquo;the database is slow&rdquo; incidents are a bad plan, and most bad plans can be read straight off <code>EXPLAIN</code>.",
      "To measure work without relying on timings, several snippets count the SQLite virtual-machine instructions a query executes, via the connection&rsquo;s progress handler. It is deterministic and tracks rows touched closely."
    ],
    "sections": [
      {
        "title": "Parsing, planning, execution",
        "body": [
          {
            "type": "table",
            "head": [
              "Stage",
              "Does",
              "Output"
            ],
            "rows": [
              [
                "Parse",
                "Tokenise and check grammar",
                "Syntax tree"
              ],
              [
                "Bind / analyse",
                "Resolve names against the catalog, check types and permissions",
                "Query tree with resolved tables and columns"
              ],
              [
                "Rewrite",
                "Expand views, apply rules, flatten simple subqueries",
                "Equivalent, simpler query tree"
              ],
              [
                "Plan / optimise",
                "Enumerate access paths, join orders and algorithms; estimate the cost of each",
                "The cheapest physical plan it found"
              ],
              [
                "Execute",
                "Run the plan as a tree of operators pulling rows from their children",
                "Result rows"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Most engines execute the plan with the <strong>iterator (Volcano) model</strong>: every operator has <code>next()</code>, and asking the root for a row makes it ask its children, down to the scans. Analytical engines instead pass batches of a thousand-odd values between operators (vectorised execution), or compile the plan to machine code."
          },
          {
            "type": "p",
            "html": "SQLite compiles the plan into bytecode for its own virtual machine, and <code>EXPLAIN</code> (without <code>QUERY PLAN</code>) shows that program. A primary-key lookup is a handful of instructions:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, px REAL)\")\nfor addr, op, p1, p2, p3, *_ in db.execute(\"EXPLAIN SELECT px FROM trades WHERE id = 7\"):\n    print(f\"{addr:>2} {op:<12} {p1:>2} {p2:>2} {p3:>2}\")",
            "label": "the compiled program for a point lookup",
            "output": " 0 Init          0  8  0\n 1 OpenRead      0  2  0\n 2 Integer       7  1  0\n 3 SeekRowid     0  7  1\n 4 Column        0  2  2\n 5 RealAffinity  2  0  0\n 6 ResultRow     2  1  0\n 7 Halt          0  0  0\n 8 Transaction   0  0  1\n 9 Goto          0  1  0",
            "isError": false
          },
          {
            "type": "p",
            "html": "Read it top to bottom: open a read cursor on the table, load the constant 7, <code>SeekRowid</code> (jump to the end if absent), read column 2, emit a result row, halt. The planning already happened; this is what it produced."
          },
          {
            "type": "p",
            "html": "Parsing and planning are not free. For short OLTP queries planning can cost as much as execution, which is why drivers use <strong>prepared statements</strong>: parse and plan once, execute many times with different parameters."
          }
        ]
      },
      {
        "title": "The query optimizer",
        "body": [
          {
            "type": "p",
            "html": "A cost-based optimizer estimates, for each candidate plan, how many rows flow through each operator and what that costs in page reads and CPU. The estimates come from <strong>statistics</strong>: row counts, distinct values per column, most-common values, histograms. It then picks the cheapest."
          },
          {
            "type": "p",
            "html": "The difficult parts are well known:"
          },
          {
            "type": "p",
            "html": "<strong>Cardinality estimation.</strong> Estimating the row count after a filter or join is the whole game, and errors multiply through a plan. The classic mistake is assuming columns are independent: <code>city = 'Paris' AND country = 'FR'</code> is estimated as P(Paris) &times; P(FR), far too low.<br><strong>Join ordering.</strong> <em>n</em> tables can be joined in <em>n</em>! orders, times a choice of algorithm per join. PostgreSQL searches exhaustively with dynamic programming up to 12 tables (<code>geqo_threshold</code>) and switches to a genetic algorithm beyond that.<br><strong>Stale statistics.</strong> After a bulk load the planner may still think the table is empty."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE orders(id INTEGER PRIMARY KEY, side INT, account INT)\")\ndb.executemany(\"INSERT INTO orders(side, account) VALUES (?, ?)\",\n               [(i % 2, i % 1000) for i in range(20_000)])\ndb.execute(\"CREATE INDEX ix_account ON orders(account)\")   # 1,000 distinct values\ndb.execute(\"CREATE INDEX ix_side ON orders(side)\")         # 2 distinct values\n\nsql = \"SELECT * FROM orders WHERE side = 1 AND account = 7\"\nprint(\"no stats:  \", db.execute(\"EXPLAIN QUERY PLAN \" + sql).fetchone()[3])\ndb.execute(\"ANALYZE\")\nfor row in db.execute(\"SELECT idx, stat FROM sqlite_stat1 ORDER BY idx\"):\n    print(\"stat1:     \", row)\nprint(\"with stats:\", db.execute(\"EXPLAIN QUERY PLAN \" + sql).fetchone()[3])",
            "label": "statistics change the choice",
            "output": "no stats:   SEARCH orders USING INDEX ix_side (side=?)\nstat1:      ('ix_account', '20000 20')\nstat1:      ('ix_side', '20000 10000')\nwith stats: SEARCH orders USING INDEX ix_account (account=?)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Without statistics both indexes look the same to SQLite &mdash; an equality match on either is assumed to return a few rows &mdash; and it picks <code>ix_side</code>, which matches 10,000 rows. <code>ANALYZE</code> records each table&rsquo;s row count and the average rows per distinct key (<code>'20000 10000'</code> vs <code>'20000 20'</code>), and the planner switches to the index that narrows the search to 20 rows."
          },
          {
            "type": "p",
            "html": "Averages have a blind spot: skew. If one account had half of all orders, &ldquo;20 rows per account&rdquo; would badly mislead the planner for that account. Histograms and most-common-value lists (PostgreSQL&rsquo;s <code>pg_stats</code>) exist to catch exactly that."
          },
          {
            "type": "caveat",
            "text": "SQLite&rsquo;s optimizer is deliberately simple and only builds <code>sqlite_stat4</code> histograms when compiled with <code>SQLITE_ENABLE_STAT4</code>. PostgreSQL, SQL Server and Oracle keep per-value frequencies and histograms by default, and PostgreSQL can be told about correlated columns with <code>CREATE STATISTICS</code>."
          }
        ]
      },
      {
        "title": "Sequential scan vs index scan",
        "body": [
          {
            "type": "p",
            "html": "A <strong>sequential scan</strong> reads every page of the table in physical order. An <strong>index scan</strong> descends the index and, for each match, fetches the row. PostgreSQL adds a middle option, the <strong>bitmap scan</strong>: collect all matching row locations from the index, sort them by page, then read each needed page once in order &mdash; turning random reads into mostly sequential ones."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, px REAL, qty INT, ts INT)\")\ndb.executemany(\"INSERT INTO trades(sym, px, qty, ts) VALUES (?, ?, ?, ?)\",\n               [(f\"S{i % 500}\", i % 97, i % 13, i) for i in range(100_000)])\n\ndef steps(sql, args=(), every=1):\n    \"\"\"Run sql; return (VM instructions executed, to the nearest `every`; rows returned).\"\"\"\n    n = 0\n    def tick():\n        nonlocal n\n        n += every\n    db.set_progress_handler(tick, every)\n    rows = db.execute(sql, args).fetchall()\n    db.set_progress_handler(None, 0)\n    return n, len(rows)\n\ndb.execute(\"CREATE INDEX ix_sym ON trades(sym)\")\n\nfor label, sql, args in [\n    (\"seek by primary key\", \"SELECT * FROM trades WHERE id = ?\", (5000,)),\n    (\"scan: ts not indexed\", \"SELECT * FROM trades WHERE ts = ?\", (5000,)),\n    (\"index on sym, 200 hits\", \"SELECT * FROM trades WHERE sym = ?\", (\"S7\",)),\n    (\"full scan, 200 hits\", \"SELECT * FROM trades NOT INDEXED WHERE sym = ?\", (\"S7\",)),\n]:\n    n, rows = steps(sql, args)\n    print(f\"{label:<24} {rows:>4} rows  {n:>8,} VM steps\")",
            "label": "work done for the same result, with and without an access path",
            "output": "seek by primary key         1 rows        14 VM steps\nscan: ts not indexed        1 rows   300,015 VM steps\nindex on sym, 200 hits    200 rows     2,011 VM steps\nfull scan, 200 hits       200 rows   301,408 VM steps",
            "isError": false
          },
          {
            "type": "p",
            "html": "The seek touches a few pages regardless of table size. The scan&rsquo;s cost is proportional to the table. Neither is always right: the scan wins when a large fraction of rows match, which the indexing page covers under selectivity."
          }
        ]
      },
      {
        "title": "Join algorithms",
        "body": [
          {
            "type": "p",
            "html": "Every relational engine implements joins with three algorithms. Knowing when each wins is a standard interview question."
          },
          {
            "type": "code",
            "src": "import random\n\nrandom.seed(7)\norders = [(i, random.randrange(200)) for i in range(2_000)]      # (order_id, cust_id)\ncustomers = [(c, f\"cust{c}\") for c in range(200)]                 # (cust_id, name)\n\ndef nested_loop(outer, inner):\n    out, cmp = [], 0\n    for o in outer:\n        for c in inner:\n            cmp += 1\n            if o[1] == c[0]:\n                out.append((o[0], c[1]))\n    return out, cmp\n\ndef hash_join(build, probe):\n    table, work = {}, 0\n    for c in build:                        # build: hash the smaller input\n        table.setdefault(c[0], []).append(c)\n        work += 1\n    out = []\n    for o in probe:                        # probe: one lookup per row\n        work += 1\n        for c in table.get(o[1], ()):\n            out.append((o[0], c[1]))\n    return out, work\n\ndef merge_join(left, right):              # both sorted on the key\n    out, i, j, work = [], 0, 0, 0\n    while i < len(left) and j < len(right):\n        work += 1\n        if left[i][1] < right[j][0]:\n            i += 1\n        elif left[i][1] > right[j][0]:\n            j += 1\n        else:\n            out.append((left[i][0], right[j][1]))\n            i += 1                         # customers key is unique\n    return out, work\n\na, n1 = nested_loop(orders, customers)\nb, n2 = hash_join(customers, orders)\nc, n3 = merge_join(sorted(orders, key=lambda o: o[1]), customers)\nprint(\"same result:\", sorted(a) == sorted(b) == sorted(c), len(a), \"rows\")\nprint(f\"nested loop  {n1:>9,} comparisons\")\nprint(f\"hash join    {n2:>9,} inserts + probes\")\nprint(f\"merge join   {n3:>9,} steps (plus the cost of sorting)\")",
            "label": "the three algorithms on 2,000 orders x 200 customers",
            "output": "same result: True 2000 rows\nnested loop    400,000 comparisons\nhash join        2,200 inserts + probes\nmerge join       2,199 steps (plus the cost of sorting)",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Algorithm",
              "Cost",
              "Wins when",
              "Needs"
            ],
            "rows": [
              [
                "Nested loop",
                "O(N &times; M); O(N log M) with an index on the inner side",
                "Outer side is small, and the inner side has an index on the join key &mdash; the typical OLTP join",
                "Nothing; works for any condition, including <code>&lt;</code> and <code>LIKE</code>"
              ],
              [
                "Hash join",
                "O(N + M)",
                "Large, unsorted inputs with an equality condition; the smaller side fits in memory",
                "Equi-join; memory for the hash table (spills to disk in partitions if not)"
              ],
              [
                "Merge join",
                "O(N + M) once sorted; O(N log N) to sort",
                "Both inputs are already sorted on the key (from an index or an earlier sort); very large inputs",
                "Sorted inputs; equality or range conditions"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The <strong>index nested-loop join</strong> deserves emphasis: for each of a few outer rows, seek into an index on the inner table. It is why &ldquo;index your foreign keys&rdquo; is standard advice, and it is the only join SQLite has &mdash; when there is no suitable index, SQLite builds a temporary one for the duration of the query:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, qty INT)\")\ndb.execute(\"CREATE TABLE syms(sym TEXT, sector TEXT)\")\nsql = (\"SELECT s.sector, sum(t.qty) FROM trades t JOIN syms s ON s.sym = t.sym \"\n       \"GROUP BY s.sector\")\nfor row in db.execute(\"EXPLAIN QUERY PLAN \" + sql):\n    print(row[3])",
            "label": "no index on the join key: SQLite makes one on the fly",
            "output": "SCAN t\nSEARCH s USING AUTOMATIC COVERING INDEX (sym=?)\nUSE TEMP B-TREE FOR GROUP BY",
            "isError": false
          }
        ]
      },
      {
        "title": "Reading EXPLAIN",
        "body": [
          {
            "type": "p",
            "html": "<code>EXPLAIN</code> shows the plan the optimizer chose; <code>EXPLAIN ANALYZE</code> (PostgreSQL, MySQL 8) also <em>runs</em> the query and reports what actually happened at each node. The single most useful thing to do with the output is compare <strong>estimated rows</strong> with <strong>actual rows</strong> node by node. Where they diverge by orders of magnitude, the planner was working blind, and every decision above that node is suspect."
          },
          {
            "type": "table",
            "head": [
              "You see",
              "It means",
              "Look at"
            ],
            "rows": [
              [
                "<code>Seq Scan</code> / <code>SCAN</code> on a big table with a selective filter",
                "No usable index, or the planner thinks the filter is not selective",
                "Missing index, non-sargable predicate, stale stats"
              ],
              [
                "Estimated 1 row, actual 100,000",
                "Cardinality misestimate",
                "<code>ANALYZE</code>, correlated columns, skewed values"
              ],
              [
                "<code>Nested Loop</code> with a large outer side and a scan inside",
                "Quadratic join",
                "Index on the inner join key, or why a hash join was not chosen"
              ],
              [
                "<code>Sort</code> with <code>external merge Disk</code>",
                "Sort spilled to disk",
                "<code>work_mem</code>, or an index that returns rows in order"
              ],
              [
                "<code>USE TEMP B-TREE FOR ORDER BY</code> (SQLite)",
                "Explicit sort step",
                "An index matching the <code>ORDER BY</code>"
              ],
              [
                "<code>Rows Removed by Filter</code> is huge",
                "Rows read then thrown away",
                "A better index or column order"
              ],
              [
                "<code>Heap Fetches</code> on an index-only scan",
                "Visibility map not up to date",
                "Vacuum"
              ],
              [
                "<code>CORRELATED SCALAR SUBQUERY</code>",
                "Subquery runs once per outer row",
                "Rewrite as a join or <code>EXISTS</code>"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, qty INT, ts INT)\")\ndb.execute(\"CREATE TABLE syms(sym TEXT PRIMARY KEY, sector TEXT)\")\ndb.execute(\"CREATE INDEX ix_trades_sym ON trades(sym)\")\nsql = \"\"\"\n    SELECT s.sector, count(*) AS n\n    FROM syms s JOIN trades t ON t.sym = s.sym\n    WHERE t.ts > 1000\n      AND s.sym IN (SELECT sym FROM trades GROUP BY sym HAVING sum(qty) > 100)\n    GROUP BY s.sector\n    ORDER BY n DESC\n\"\"\"\ndepth = {0: -1}\nfor node, parent, _, detail in db.execute(\"EXPLAIN QUERY PLAN \" + sql):\n    depth[node] = depth[parent] + 1\n    print(\"  \" * depth[node] + detail)",
            "label": "a plan tree: scans, index searches, a subquery and two temp b-trees",
            "output": "SEARCH s USING INDEX sqlite_autoindex_syms_1 (sym=?)\nLIST SUBQUERY 1\n  SCAN trades USING INDEX ix_trades_sym\nSEARCH t USING INDEX ix_trades_sym (sym=?)\nUSE TEMP B-TREE FOR GROUP BY\nUSE TEMP B-TREE FOR ORDER BY",
            "isError": false
          },
          {
            "type": "note",
            "text": "Always <code>EXPLAIN ANALYZE</code> on production-like data. A plan on an empty development database tells you nothing, because the optimizer correctly decides that scanning three rows is cheapest."
          }
        ]
      },
      {
        "title": "Why a seemingly obvious query can be slow",
        "body": [
          {
            "type": "p",
            "html": "The most expensive queries in a real system are often the most innocent-looking. Four classics, measured:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, px REAL, qty INT, ts INT)\")\ndb.executemany(\"INSERT INTO trades(sym, px, qty, ts) VALUES (?, ?, ?, ?)\",\n               [(f\"S{i % 500}\", i % 97, i % 13, i) for i in range(100_000)])\n\ndef steps(sql, args=(), every=1):\n    \"\"\"Run sql; return (VM instructions executed, to the nearest `every`; rows returned).\"\"\"\n    n = 0\n    def tick():\n        nonlocal n\n        n += every\n    db.set_progress_handler(tick, every)\n    rows = db.execute(sql, args).fetchall()\n    db.set_progress_handler(None, 0)\n    return n, len(rows)\n\npage = \"SELECT * FROM trades ORDER BY id LIMIT 10 OFFSET ?\"\nkeyset = \"SELECT * FROM trades WHERE id > ? ORDER BY id LIMIT 10\"\nfor n in (10, 1_000, 90_000):\n    off, _ = steps(page, (n,))\n    key, _ = steps(keyset, (n,))\n    print(f\"page at row {n:>6,}: OFFSET {off:>8,} steps   keyset {key:>4,} steps\")",
            "label": "1. OFFSET pagination reads and discards every earlier row",
            "output": "page at row     10: OFFSET      130 steps   keyset   99 steps\npage at row  1,000: OFFSET    2,110 steps   keyset   98 steps\npage at row 90,000: OFFSET  180,110 steps   keyset   98 steps",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>OFFSET 90000</code> has to walk past 90,000 rows to throw them away, so deep pages get linearly slower. <strong>Keyset (seek) pagination</strong> remembers the last key seen and asks for <code>WHERE id &gt; :last</code>, which is a seek no matter how deep you are."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, px REAL, qty INT, ts INT)\")\ndb.executemany(\"INSERT INTO trades(sym, px, qty, ts) VALUES (?, ?, ?, ?)\",\n               [(f\"S{i % 500}\", i % 97, i % 13, i) for i in range(100_000)])\n\ndef steps(sql, args=(), every=1):\n    \"\"\"Run sql; return (VM instructions executed, to the nearest `every`; rows returned).\"\"\"\n    n = 0\n    def tick():\n        nonlocal n\n        n += every\n    db.set_progress_handler(tick, every)\n    rows = db.execute(sql, args).fetchall()\n    db.set_progress_handler(None, 0)\n    return n, len(rows)\n\ndb.execute(\"CREATE TABLE syms(sym TEXT PRIMARY KEY, sector TEXT)\")\ndb.executemany(\"INSERT INTO syms VALUES (?, ?)\", [(f\"S{i}\", f\"sec{i % 10}\") for i in range(500)])\n\ncorrelated = \"\"\"SELECT sym FROM syms s\n                WHERE (SELECT count(*) FROM trades t WHERE t.sym = s.sym) > 150\"\"\"\ngrouped = \"\"\"SELECT sym FROM trades GROUP BY sym HAVING count(*) > 150\"\"\"\na, ra = steps(correlated, every=1000)      # too many to count one by one\nb, rb = steps(grouped, every=1000)\nprint(f\"correlated subquery: {ra} rows, {a // 1000:>9,}k steps\")\nprint(f\"one GROUP BY pass:   {rb} rows, {b // 1000:>9,}k steps\")",
            "label": "2. a correlated subquery re-runs for every outer row",
            "output": "correlated subquery: 500 rows,   200,107k steps\none GROUP BY pass:   500 rows,     1,207k steps",
            "isError": false
          },
          {
            "type": "p",
            "html": "Without an index on <code>trades.sym</code>, the subquery scans all 100,000 trades once for each of 500 symbols. The <code>GROUP BY</code> reads the table once. (An index on <code>trades(sym)</code> would also rescue the first form &mdash; many planners decorrelate it automatically, SQLite does not.)"
          },
          {
            "type": "p",
            "html": "<strong>3. A function on the column.</strong> <code>WHERE date(ts) = '2026-09-30'</code> cannot use an index on <code>ts</code>; <code>WHERE ts &gt;= '2026-09-30' AND ts &lt; '2026-10-01'</code> can."
          },
          {
            "type": "p",
            "html": "<strong>4. The N+1 pattern.</strong> An ORM loads 500 orders, then lazily issues one query per order to fetch its customer. Each query is fast; 501 network round trips are not. Fetch with one join or one <code>WHERE id IN (...)</code>."
          },
          {
            "type": "p",
            "html": "Other regulars: <code>SELECT count(*)</code> on a huge MVCC table (each row&rsquo;s visibility must be checked, so there is no stored total); <code>ORDER BY ... LIMIT 10</code> with no index matching the order (sorts everything to return ten rows); <code>NOT IN</code> with a nullable subquery column (wrong <em>and</em> slow); implicit casts from a driver sending a parameter as the wrong type; and a plan that was good for yesterday&rsquo;s parameter distribution, cached in a prepared statement."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "When would a database choose a hash join over a nested-loop join, and when is nested loop the better choice?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Hash join wins for an equality join between two large inputs where neither side is small and there is no useful index: build a hash table on the smaller side, stream the larger side through it, O(N + M). It needs memory for the build side and only works for equality conditions."
          },
          {
            "type": "p",
            "html": "Nested loop wins when the outer side is small &mdash; after a selective filter, say 20 rows &mdash; and the inner side has an index on the join key. Then the cost is 20 index seeks, far less than hashing an entire large table. It is also the only option for non-equality conditions such as <code>a.ts BETWEEN b.start AND b.end</code> (unless merge join can use a range)."
          },
          {
            "type": "p",
            "html": "The trap: if the planner <em>underestimates</em> the outer side (expects 20 rows, gets 200,000), a nested loop becomes catastrophic. That misestimate is one of the most common causes of a query that is suddenly 1,000&times; slower."
          }
        ]
      },
      {
        "q": "A query was fast yesterday and is slow today. Nothing was deployed. What do you check?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The plan changed, or the data did. In order:"
          },
          {
            "type": "p",
            "html": "<strong>1. Compare plans.</strong> <code>EXPLAIN ANALYZE</code> now vs. a saved plan (<code>auto_explain</code>, <code>pg_stat_statements</code>, Query Store in SQL Server). Look for a flipped join algorithm or join order, or an index scan that became a sequential scan.<br><strong>2. Statistics.</strong> Did autovacuum/auto-analyze run after a large load or delete? Did a table cross a size where the estimated cost of one plan overtook another? Did the data become skewed (a new customer with 40% of rows)?<br><strong>3. Parameter sensitivity.</strong> A cached generic plan built for one parameter value is being reused for a very different one.<br><strong>4. Bloat.</strong> Dead tuples from a long-running transaction make every scan read more pages.<br><strong>5. Not the query at all.</strong> Lock waits (check <code>pg_locks</code> / wait events), a cold cache after a restart or failover, I/O contention from a backup or vacuum, or replication lag if it reads from a replica."
          }
        ]
      },
      {
        "q": "Why is OFFSET-based pagination slow on deep pages, and what do you do instead?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>LIMIT 10 OFFSET 100000</code> cannot jump to row 100,000; the engine must produce the first 100,010 rows in order and discard 100,000 of them, so cost grows linearly with page depth. It is also unstable: rows inserted or deleted between requests shift the pages, so users see duplicates or miss rows."
          },
          {
            "type": "p",
            "html": "Keyset pagination: order by a unique key (or a unique tuple such as <code>(created_at, id)</code>), remember the last value returned, and ask for <code>WHERE (created_at, id) &gt; (:last_ts, :last_id) ORDER BY created_at, id LIMIT 10</code>. With a matching index this is one seek per page at any depth, and it is stable under concurrent inserts. The trade-off is that you cannot jump straight to page 500, which most interfaces do not actually need."
          }
        ]
      },
      {
        "q": "What is cardinality estimation and why do errors in it matter so much?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "It is the optimizer&rsquo;s prediction of how many rows each operator will output. Every cost the optimizer computes &mdash; which access path, which join algorithm, which join order, how much memory to give a hash or sort &mdash; is a function of those predictions."
          },
          {
            "type": "p",
            "html": "Errors compound through a plan. If a filter is estimated at 1% but is really 30%, and its output is joined with another table whose join selectivity is also misjudged, the estimate at the top of a five-way join can be off by several orders of magnitude. The optimizer then picks a nested loop expecting 10 iterations and gets 10 million, or sizes a hash table for 1,000 rows and spills 10 million to disk."
          },
          {
            "type": "p",
            "html": "Common causes: correlated predicates assumed independent, skewed value distributions summarised by averages, predicates the estimator cannot see into (functions, <code>LIKE</code> patterns, parameters in generic plans), and stale statistics. Remedies: <code>ANALYZE</code>, raising the statistics target on skewed columns, extended statistics on correlated columns, rewriting predicates to be estimable, and as a last resort plan hints."
          }
        ]
      },
      {
        "q": "Explain the Volcano iterator model and why analytical engines moved away from it.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "In the Volcano model each plan operator implements <code>open()</code>, <code>next()</code> and <code>close()</code>. The root calls <code>next()</code> on its child, which calls its child, down to the scans, and each call returns one row. It is simple and composable, and pipelines naturally: a <code>LIMIT 10</code> stops pulling after ten rows."
          },
          {
            "type": "p",
            "html": "The cost is per-row overhead. Every row passes through a chain of virtual function calls, each processing one value with poor branch prediction and no chance for SIMD. For OLTP, which touches a handful of rows, that does not matter. For an analytical query over a billion rows it dominates."
          },
          {
            "type": "p",
            "html": "Vectorised execution (MonetDB/X100, DuckDB, ClickHouse, Snowflake) passes batches of around 1,000&ndash;64,000 values per call, so the overhead is paid once per batch and the inner loops are tight, cache-friendly and SIMD-able. Compiled execution (HyPer, Umbra, Spark&rsquo;s whole-stage codegen) instead generates one fused machine-code loop for a pipeline of operators. Both deliver roughly an order of magnitude over row-at-a-time on analytical workloads."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "SQLite: the query optimizer overview",
        "url": "https://www.sqlite.org/optoverview.html"
      },
      {
        "label": "SQLite: the next-generation query planner",
        "url": "https://www.sqlite.org/queryplanner-ng.html"
      },
      {
        "label": "PostgreSQL: using EXPLAIN",
        "url": "https://www.postgresql.org/docs/current/using-explain.html"
      },
      {
        "label": "PostgreSQL: planner statistics",
        "url": "https://www.postgresql.org/docs/current/planner-stats.html"
      },
      {
        "label": "Leis et al. — How Good Are Query Optimizers, Really?",
        "url": "https://www.vldb.org/pvldb/vol9/p204-leis.pdf"
      }
    ]
  },
  {
    "id": "internals",
    "title": "Storage Engine Internals",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Pages, the buffer pool, WAL and checkpoints, dirty pages, and LSM trees vs B-trees.",
    "intro": [
      "Underneath SQL, a storage engine does one job: keep a large amount of data on a slow device, keep the useful part in fast memory, and never lose a committed write when the power goes out. The same handful of structures &mdash; fixed-size pages, a buffer pool, a write-ahead log, checkpoints &mdash; appear in every serious engine, and the one big design fork is whether to update data in place (B-trees) or only ever append (LSM trees).",
      "SQLite exposes enough of its internals through <code>PRAGMA</code>s and the <code>dbstat</code> table to watch these mechanisms work on a real file."
    ],
    "sections": [
      {
        "title": "Pages: the unit of everything",
        "body": [
          {
            "type": "p",
            "html": "A database file is an array of fixed-size <strong>pages</strong> (SQLite 4&nbsp;KB, PostgreSQL 8&nbsp;KB, InnoDB 16&nbsp;KB). Every read from disk, every write to disk, every cache slot and every lock on the file&rsquo;s structure works in whole pages. A page is also the node size of the B+ trees from the indexing topic."
          },
          {
            "type": "p",
            "html": "A table or index page typically has a header, an array of <em>slot</em> pointers growing from the front, and the row data growing from the back, with free space in the middle. Rows are addressed by (page, slot), so a row can move within a page during compaction without changing its address."
          },
          {
            "type": "code",
            "src": "import os, sqlite3, tempfile\n\npath = os.path.join(tempfile.mkdtemp(), \"demo.db\")\ndb = sqlite3.connect(path)\ndb.execute(\"CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, note TEXT)\")\ndb.execute(\"CREATE INDEX ix_sym ON trades(sym)\")\ndb.executemany(\"INSERT INTO trades(sym, note) VALUES (?, ?)\",\n               [(f\"S{i % 300}\", \"x\" * 80) for i in range(20_000)])\ndb.commit()\n\nprint(\"page size:\", db.execute(\"PRAGMA page_size\").fetchone()[0], \"bytes\")\nprint(\"file:\", os.path.getsize(path) // 4096, \"pages\")\nfor name, kind, pages, rows in db.execute(\"\"\"\n        SELECT name, pagetype, count(*), sum(ncell) FROM dbstat\n        WHERE name IN ('trades', 'ix_sym') GROUP BY name, pagetype\n        ORDER BY name, pagetype\"\"\"):\n    print(f\"  {name:<7} {kind:<9} {pages:>4} pages {rows:>7,} cells\")",
            "label": "a 20,000-row table and its index, page by page",
            "output": "page size: 4096 bytes\nfile: 530 pages\n  ix_sym  internal     1 pages      61 cells\n  ix_sym  leaf        62 pages  19,939 cells\n  trades  internal     1 pages     464 cells\n  trades  leaf       465 pages  20,000 cells",
            "isError": false
          },
          {
            "type": "p",
            "html": "Both trees are two levels deep: one root page above the leaves. The table&rsquo;s root holds only pointers (its cells are separator keys), while the index is much smaller because its entries are only <code>(sym, rowid)</code>. Notice the index&rsquo;s 61 interior cells plus 19,939 leaf cells add up to exactly 20,000: SQLite stores table data in B+ trees but indexes in classic B-trees, where interior nodes hold real entries too. Every query you run is ultimately a walk over these pages."
          }
        ]
      },
      {
        "title": "The buffer pool",
        "body": [
          {
            "type": "p",
            "html": "The <strong>buffer pool</strong> (PostgreSQL: <code>shared_buffers</code>; InnoDB: <code>innodb_buffer_pool_size</code>; SQLite: <code>cache_size</code>) is the engine&rsquo;s own cache of pages in RAM. Every page access goes through it: if the page is present it is a <em>hit</em>; if not, the engine picks a victim frame, writes it out first if it is <strong>dirty</strong> (modified since it was read), and reads the requested page in."
          },
          {
            "type": "p",
            "html": "Frames being used by a running operation are <em>pinned</em> and cannot be evicted. The replacement policy decides which unpinned page goes. Pure LRU has a famous weakness: one big sequential scan touches every page once and flushes the entire hot working set."
          },
          {
            "type": "code",
            "src": "from collections import OrderedDict\n\nclass LRUPool:\n    def __init__(self, frames):\n        self.frames, self.pages = frames, OrderedDict()\n        self.hits = self.misses = self.writebacks = 0\n\n    def get(self, page, write=False):\n        if page in self.pages:\n            self.hits += 1\n            self.pages.move_to_end(page)\n        else:\n            self.misses += 1\n            if len(self.pages) >= self.frames:\n                _, dirty = self.pages.popitem(last=False)\n                self.writebacks += dirty      # dirty victim must be written first\n            self.pages[page] = False\n        if write:\n            self.pages[page] = True\n\ndef run(scan):\n    pool = LRUPool(frames=100)\n    for round_ in range(20):\n        for p in range(80):                    # hot working set: 80 pages\n            pool.get(p, write=(p % 4 == 0))\n        if scan and round_ == 10:\n            for p in range(1_000, 1_500):      # one report scans 500 cold pages\n                pool.get(p)\n    total = pool.hits + pool.misses\n    return f\"hit ratio {pool.hits / total:.1%}, dirty write-backs {pool.writebacks}\"\n\nprint(\"hot set only:       \", run(scan=False))\nprint(\"plus one big scan:  \", run(scan=True))",
            "label": "a scan flushing the hot pages out of an LRU pool",
            "output": "hot set only:        hit ratio 95.0%, dirty write-backs 0\nplus one big scan:   hit ratio 68.6%, dirty write-backs 20",
            "isError": false
          },
          {
            "type": "p",
            "html": "Real engines defend against this. PostgreSQL uses a clock-sweep approximation of LRU and gives large sequential scans a small private <em>ring buffer</em> so they recycle their own frames. InnoDB inserts newly read pages at the midpoint of its LRU list, and only promotes them to the hot end if they are touched again after a delay. The effect is the same: one scan cannot evict the working set."
          },
          {
            "type": "caveat",
            "text": "PostgreSQL deliberately keeps <code>shared_buffers</code> modest (often 25% of RAM) and relies on the operating system&rsquo;s page cache for the rest, so a page can be cached twice. InnoDB and most commercial engines use <code>O_DIRECT</code> to bypass the OS cache and size the buffer pool at 60&ndash;80% of RAM instead."
          }
        ]
      },
      {
        "title": "WAL, dirty pages and checkpoints",
        "body": [
          {
            "type": "p",
            "html": "Writing every modified page back to its home location at commit would be slow (random writes, a whole page for a one-byte change) and unsafe (a crash half-way through a page write leaves a torn page). Instead engines use a <strong>write-ahead log</strong>: append a description of the change to a sequential log, <code>fsync</code> the log, and only then acknowledge the commit. The modified page stays dirty in the buffer pool and is written to its home location later."
          },
          {
            "type": "p",
            "html": "The rule that makes this safe is the <strong>WAL protocol</strong>: a dirty page may not be written to the data file until the log records describing its changes are durable. After a crash, replaying the log reconstructs every committed change the data file is missing."
          },
          {
            "type": "p",
            "html": "A <strong>checkpoint</strong> bounds how much log must be replayed. It flushes dirty pages to the data files and records a point in the log before which nothing is needed for recovery, so old log segments can be recycled."
          },
          {
            "type": "code",
            "src": "import os, sqlite3, tempfile\n\npath = os.path.join(tempfile.mkdtemp(), \"demo.db\")\ndb = sqlite3.connect(path, isolation_level=None)\ndb.execute(\"PRAGMA journal_mode = WAL\")\ndb.execute(\"PRAGMA wal_autocheckpoint = 0\")        # we checkpoint by hand\ndb.execute(\"CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT)\")\n\ndef sizes(label):\n    kb = lambda f: os.path.getsize(f) // 1024\n    print(f\"{label:<28} db {kb(path):>5} KB   wal {kb(path + '-wal'):>5} KB\")\n\ndb.execute(\"BEGIN\")\ndb.executemany(\"INSERT INTO t(v) VALUES (?)\", [(\"x\" * 100,) for _ in range(10_000)])\ndb.execute(\"COMMIT\")\nsizes(\"after 10,000 inserts\")\n\ndb.execute(\"UPDATE t SET v = 'y' WHERE id = 5\")\nsizes(\"after a one-row update\")\n\nbusy, log_frames, done = db.execute(\"PRAGMA wal_checkpoint(PASSIVE)\").fetchone()\nprint(f\"checkpoint: {done} of {log_frames} WAL frames copied into the db file\")\ndb.execute(\"PRAGMA wal_checkpoint(TRUNCATE)\")\nsizes(\"after checkpoint\")",
            "label": "SQLite: commits go to the WAL; the checkpoint moves them home",
            "output": "after 10,000 inserts         db     4 KB   wal  1106 KB\nafter a one-row update       db     4 KB   wal  1110 KB\ncheckpoint: 276 of 276 WAL frames copied into the db file\nafter checkpoint             db  1092 KB   wal     0 KB",
            "isError": false
          },
          {
            "type": "p",
            "html": "Three things to notice. After the inserts commit, the main file is still essentially empty: the committed data exists only in the WAL, and readers find the newest version of each page there. A one-row update appended a whole new 4&nbsp;KB page to the WAL, not a few bytes. And the checkpoint copied every frame into the database file and allowed the log to be truncated."
          },
          {
            "type": "table",
            "head": [
              "Checkpoint style",
              "How",
              "Trade-off"
            ],
            "rows": [
              [
                "Sharp (stop the world)",
                "Block writes, flush all dirty pages",
                "Simple recovery; periodic latency spikes"
              ],
              [
                "Fuzzy",
                "Flush dirty pages in the background while transactions continue; record which pages were dirty",
                "Smooth latency; recovery logic must cope with a checkpoint that was in progress"
              ],
              [
                "Spread (PostgreSQL)",
                "Fuzzy, paced over <code>checkpoint_completion_target</code> of the interval",
                "Avoids I/O bursts; longer recovery window"
              ]
            ]
          },
          {
            "type": "note",
            "text": "Checkpoint frequency trades steady-state write cost against recovery time. Rare checkpoints mean fewer page writes (a page dirtied 100 times is flushed once) but more log to replay after a crash."
          }
        ]
      },
      {
        "title": "LSM trees vs B-trees",
        "body": [
          {
            "type": "p",
            "html": "A B-tree updates pages <em>in place</em>. A <strong>log-structured merge tree</strong> (LevelDB, RocksDB, Cassandra, ScyllaDB, the storage layer of many time-series stores) never modifies anything on disk:"
          },
          {
            "type": "p",
            "html": "<strong>1.</strong> Writes go to the WAL (for durability) and to an in-memory sorted structure, the <em>memtable</em>.<br><strong>2.</strong> When the memtable is full it is written out as an immutable sorted file, an <em>SSTable</em>, in one sequential write.<br><strong>3.</strong> Background <em>compaction</em> merges SSTables into larger ones, discarding overwritten values and deletion markers (<em>tombstones</em>).<br><strong>4.</strong> A read checks the memtable, then SSTables from newest to oldest, stopping at the first hit. Per-file Bloom filters let it skip files that certainly do not contain the key."
          },
          {
            "type": "code",
            "src": "import bisect\n\nclass LSM:\n    def __init__(self, memtable_limit=4, fanout=3):\n        self.mem, self.runs = {}, []          # runs: newest first, each sorted\n        self.limit, self.fanout = memtable_limit, fanout\n        self.user_bytes = self.disk_bytes = 0\n\n    def put(self, key, value):\n        self.user_bytes += 1\n        self.mem[key] = value\n        if len(self.mem) >= self.limit:\n            self.runs.insert(0, sorted(self.mem.items()))\n            self.disk_bytes += len(self.mem)      # flush: sequential write\n            self.mem = {}\n            if len(self.runs) > self.fanout:\n                self.compact()\n\n    def compact(self):                        # merge all runs into one\n        merged = {}\n        for run in reversed(self.runs):       # oldest first; newer wins\n            merged.update(run)\n        self.runs = [sorted(merged.items())]\n        self.disk_bytes += len(merged)        # compaction rewrites data\n\n    def get(self, key):\n        if key in self.mem:\n            return self.mem[key], 0\n        for checked, run in enumerate(self.runs, 1):\n            i = bisect.bisect_left(run, (key,))\n            if i < len(run) and run[i][0] == key:\n                return run[i][1], checked\n        return None, len(self.runs)\n\ndb = LSM()\nfor i in range(49):\n    db.put(f\"k{i % 25:02d}\", i)                # 49 writes over 25 keys\nprint(\"runs on disk:\", [len(r) for r in db.runs], \"+ memtable\", len(db.mem))\nprint(f\"write amplification: {db.disk_bytes / db.user_bytes:.2f}x\")\nfor key in (\"k23\", \"k20\", \"k02\", \"k99\"):\n    value, runs_checked = db.get(key)\n    print(f\"get({key}) = {value}, runs checked: {runs_checked}\")",
            "label": "a toy LSM tree: memtable, flushes, compaction",
            "output": "runs on disk: [4, 4, 25] + memtable 1\nwrite amplification: 2.33x\nget(k23) = 48, runs checked: 0\nget(k20) = 45, runs checked: 1\nget(k02) = 27, runs checked: 3\nget(k99) = None, runs checked: 3",
            "isError": false
          },
          {
            "type": "p",
            "html": "Even this toy shows the trade. Every write is a cheap in-memory insert and every disk write is sequential, but compaction has already rewritten the data more than twice over, and the cost of a read depends on where the key happens to be: the memtable, the newest run, or the oldest. A lookup for a key that does not exist is the worst case &mdash; it checks every run &mdash; which is why Bloom filters are essential in real LSM engines."
          },
          {
            "type": "table",
            "head": [
              "",
              "B+ tree (InnoDB, PostgreSQL)",
              "LSM tree (RocksDB, Cassandra)"
            ],
            "rows": [
              [
                "Write path",
                "Find the leaf, modify in place (plus WAL)",
                "Append to memtable (plus WAL); flush sequentially"
              ],
              [
                "Write throughput",
                "Limited by random page writes",
                "High; all disk writes are sequential"
              ],
              [
                "Point read",
                "One root-to-leaf descent",
                "Memtable, then possibly several SSTables (Bloom filters help)"
              ],
              [
                "Range scan",
                "Walk the linked leaves",
                "Merge iterators across all levels"
              ],
              [
                "Space",
                "Fragmentation; pages part-full after splits",
                "Obsolete versions until compaction; compresses well"
              ],
              [
                "Latency tail",
                "Predictable",
                "Compaction can cause stalls"
              ],
              [
                "Good fit",
                "Read-heavy OLTP, predictable latency",
                "Write-heavy ingest: logs, metrics, events, time series"
              ]
            ]
          }
        ]
      },
      {
        "title": "Write, read and space amplification",
        "body": [
          {
            "type": "p",
            "html": "The three numbers used to compare storage engines:"
          },
          {
            "type": "table",
            "head": [
              "Amplification",
              "Definition",
              "B+ tree",
              "LSM (leveled)"
            ],
            "rows": [
              [
                "<strong>Write</strong>",
                "Bytes written to disk &divide; bytes the application wrote",
                "A whole page (4&ndash;16&nbsp;KB) per modified row, plus WAL, plus full-page images after checkpoints",
                "Each byte is rewritten once per level it passes through: often 10&ndash;30&times;"
              ],
              [
                "<strong>Read</strong>",
                "Pages or files touched per logical read",
                "Tree height, mostly cached: 1&ndash;2 I/Os",
                "One per level in the worst case; Bloom filters cut point reads to about 1"
              ],
              [
                "<strong>Space</strong>",
                "Bytes on disk &divide; bytes of live data",
                "About 1.3&ndash;1.5&times; from half-full pages",
                "About 1.1&times; leveled, up to 2&times; tiered, before compaction catches up"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The <em>RUM conjecture</em> puts it formally: you can optimise for two of Read, Update and Memory (space) overhead, but not all three. B+ trees favour reads; LSM trees favour writes and space; leveled vs tiered compaction moves an LSM along the same trade-off."
          },
          {
            "type": "p",
            "html": "Write amplification is not an academic number on SSDs. Flash cells survive a limited number of program/erase cycles, and the drive&rsquo;s own garbage collection adds a second layer of amplification underneath the database&rsquo;s. An engine with 20&times; write amplification wears out a drive 20&times; faster than the application&rsquo;s write rate suggests."
          },
          {
            "type": "note",
            "text": "Ask &ldquo;what is this workload&rsquo;s read:write ratio and does it need range scans?&rdquo; before choosing an engine. Write-heavy with point reads: LSM. Read-heavy with predictable latency: B+ tree."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why does a database write to a log first instead of just writing the changed pages at commit?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Three reasons. <strong>Speed</strong>: the log is an append-only sequential write, and a commit needs only one <code>fsync</code> of the log tail, where writing pages in place means random writes to wherever each page lives. <strong>Size</strong>: a log record describes the change (often tens of bytes), while a page write is 4&ndash;16&nbsp;KB. <strong>Atomicity across pages</strong>: a transaction touching ten pages cannot write them all atomically, but it can append one commit record atomically; recovery then redoes or undoes page changes to match the log."
          },
          {
            "type": "p",
            "html": "The dirty pages are written later by the background writer and checkpoints, and a page updated many times between checkpoints is written once, so the log also absorbs repeated writes to hot pages."
          }
        ]
      },
      {
        "q": "Compare LSM trees and B+ trees. When would you choose each?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A B+ tree updates pages in place: reads are one descent through a mostly cached tree, range scans walk the leaves, and latency is predictable, but every row change dirties a whole page, so random write throughput is limited."
          },
          {
            "type": "p",
            "html": "An LSM tree buffers writes in memory and flushes immutable sorted files sequentially, merging them in the background. Writes are fast and sequential and data compresses well, but reads may consult several files (Bloom filters mitigate point reads, not range scans), compaction consumes I/O and CPU, and it can cause latency spikes."
          },
          {
            "type": "p",
            "html": "Choose an LSM for write-heavy ingest with mostly recent or point reads: event logs, metrics, time series, message stores, key-value caches of large data. Choose a B+ tree for read-heavy OLTP with range queries and strict latency requirements. RocksDB under MySQL (MyRocks) shows the choice can be made per table."
          }
        ]
      },
      {
        "q": "What is a dirty page, and what happens to dirty pages during a checkpoint and a crash?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A dirty page is one modified in the buffer pool but not yet written back to the data file. Its changes are already durable in the WAL, so being dirty is safe."
          },
          {
            "type": "p",
            "html": "During a checkpoint the engine writes dirty pages to the data files (in a fuzzy checkpoint, gradually and while transactions continue) and then records the checkpoint position in the log. Everything before that position is no longer needed for recovery."
          },
          {
            "type": "p",
            "html": "In a crash, the dirty pages in memory are lost. Recovery starts from the last checkpoint and replays the log forward, reapplying every change whose page on disk is older than the log record (it compares each page&rsquo;s LSN with the record&rsquo;s). The data files end up exactly as the buffer pool would have been."
          }
        ]
      },
      {
        "q": "Why is LRU a poor buffer-pool replacement policy, and what do real databases do instead?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "LRU treats a page accessed once as more valuable than a page accessed thousands of times, if the single access was more recent. A sequential scan of a large table &mdash; a report, a backup, an <code>ANALYZE</code> &mdash; touches each page exactly once and pushes the entire hot working set out of the pool. After the scan, every OLTP query misses until the cache warms up again. Strict LRU also needs a global list updated on every access, which becomes a contention point."
          },
          {
            "type": "p",
            "html": "PostgreSQL uses clock-sweep (each buffer has a small usage counter decremented by a sweeping hand, so frequently used pages survive several passes) and gives bulk scans, <code>VACUUM</code> and <code>COPY</code> small ring buffers. InnoDB splits its LRU list into young and old sublists; new pages enter at the old head and are promoted only if accessed again after <code>innodb_old_blocks_time</code>. Other engines use LRU-K or 2Q, which rank pages by their second-most-recent access so that one-off touches do not count."
          }
        ]
      },
      {
        "q": "What is write amplification, where does it come from in a B+ tree and in an LSM tree, and why does it matter on SSDs?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Write amplification is bytes physically written divided by bytes the application logically wrote."
          },
          {
            "type": "p",
            "html": "In a B+ tree: changing a 100-byte row dirties a 16&nbsp;KB page, which is eventually written whole; the change is also written to the WAL; PostgreSQL additionally writes a full-page image to the WAL the first time a page is modified after each checkpoint (to repair torn pages); and page splits rewrite neighbours. Double-write buffers (InnoDB) write pages twice."
          },
          {
            "type": "p",
            "html": "In an LSM tree: each byte is written to the WAL, flushed in an SSTable, and then rewritten each time compaction moves it down a level. With leveled compaction and a fanout of 10, that is roughly 10&times; per level."
          },
          {
            "type": "p",
            "html": "On SSDs it matters twice: it consumes write bandwidth that could serve application writes, and flash endures a finite number of erase cycles, so amplification directly shortens drive life. The SSD&rsquo;s internal garbage collection adds its own amplification on top, and it is worst for random small writes, which is one more reason sequential write patterns are preferred."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "SQLite: write-ahead logging",
        "url": "https://www.sqlite.org/wal.html"
      },
      {
        "label": "SQLite: database file format",
        "url": "https://www.sqlite.org/fileformat.html"
      },
      {
        "label": "PostgreSQL: WAL internals",
        "url": "https://www.postgresql.org/docs/current/wal-internals.html"
      },
      {
        "label": "RocksDB wiki: leveled compaction",
        "url": "https://github.com/facebook/rocksdb/wiki/Leveled-Compaction"
      },
      {
        "label": "O'Neil et al. — The Log-Structured Merge-Tree",
        "url": "https://www.cs.umb.edu/~poneil/lsmtree.pdf"
      },
      {
        "label": "Athanassoulis et al. — The RUM Conjecture",
        "url": "https://stratos.seas.harvard.edu/files/stratos/files/rum.pdf"
      }
    ]
  },
  {
    "id": "redis",
    "title": "In-Memory Databases and Redis",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Redis's single-threaded design, its hash tables and sorted sets, memory layout, persistence and eviction.",
    "intro": [
      "An in-memory database keeps the whole dataset in RAM and treats disk only as a place to recover from. That removes the buffer pool, page layout and most of the I/O path, and what is left can answer a request in a few microseconds. Redis is the example every interviewer reaches for, and it is also a deliberately simple system whose design decisions are easy to reason about.",
      "There is no Redis server in this site&rsquo;s build, so the examples are small Python models of the structures Redis actually uses: its incrementally rehashed hash table, the skiplist behind sorted sets, and approximated LRU eviction. The numbers and trade-offs they show are the real ones."
    ],
    "sections": [
      {
        "title": "Why Redis is fast: one thread, all in memory",
        "body": [
          {
            "type": "p",
            "html": "Redis executes every command on a single thread, one at a time, from an event loop over non-blocking sockets. That sounds like a limitation and is the core of the design:"
          },
          {
            "type": "p",
            "html": "<strong>No locks.</strong> Every command sees and mutates data with no possibility of interference, so each command is atomic for free.<br><strong>No context switches</strong> on the hot path, and the working data stays in one core&rsquo;s cache.<br><strong>Simple data structures</strong> with known complexity, so a command&rsquo;s cost is predictable."
          },
          {
            "type": "p",
            "html": "The bottleneck is usually the network, not the CPU. Redis 6 added I/O threads that read and parse requests and write replies in parallel, but command execution is still single-threaded. The flip side: <em>one slow command blocks every client</em>. <code>KEYS *</code>, <code>SMEMBERS</code> on a million-element set, a large <code>DEL</code>, or a Lua script with a loop stalls the whole server for its duration."
          },
          {
            "type": "table",
            "head": [
              "Command",
              "Complexity",
              "Safe on a large key?"
            ],
            "rows": [
              [
                "<code>GET</code>, <code>SET</code>, <code>HGET</code>, <code>INCR</code>",
                "O(1)",
                "Yes"
              ],
              [
                "<code>ZADD</code>, <code>ZRANK</code>, <code>ZSCORE</code>",
                "O(log n)",
                "Yes"
              ],
              [
                "<code>ZRANGEBYSCORE ... LIMIT</code>",
                "O(log n + m)",
                "Yes, for small m"
              ],
              [
                "<code>HGETALL</code>, <code>SMEMBERS</code>, <code>LRANGE 0 -1</code>",
                "O(n)",
                "No: use <code>HSCAN</code>/<code>SSCAN</code>"
              ],
              [
                "<code>KEYS pattern</code>",
                "O(total keys)",
                "Never in production: use <code>SCAN</code>"
              ],
              [
                "<code>DEL</code> on a huge key",
                "O(n) to free memory",
                "Use <code>UNLINK</code> (frees in a background thread)"
              ]
            ]
          },
          {
            "type": "note",
            "text": "Redis gives you atomicity per command, and per <code>MULTI</code>/<code>EXEC</code> block or Lua script. Anything that must read, decide and write should be one of those, never three round trips."
          }
        ]
      },
      {
        "title": "Hash tables and incremental rehashing",
        "body": [
          {
            "type": "p",
            "html": "The keyspace itself is a hash table, and so is every Redis hash once it outgrows its compact encoding. A hash table must grow as it fills, and rehashing a table with ten million keys in one go would freeze the server for hundreds of milliseconds."
          },
          {
            "type": "p",
            "html": "Redis avoids that by keeping <em>two</em> tables during a resize and moving entries incrementally: each normal operation also migrates one bucket from the old table to the new one (and a timer migrates more when the server is idle). Lookups check both tables until the move is complete. The cost of the resize is spread over thousands of operations, and no single command pays for it."
          },
          {
            "type": "code",
            "src": "class IncrementalDict:\n    def __init__(self):\n        self.old, self.new, self.cursor = [[] for _ in range(4)], None, 0\n        self.size = 0\n\n    def _step(self):\n        \"\"\"Move one bucket from old to new; called on every operation.\"\"\"\n        if self.new is None:\n            return\n        for k, v in self.old[self.cursor]:\n            self.new[hash(k) % len(self.new)].append((k, v))\n        self.old[self.cursor] = []\n        self.cursor += 1\n        if self.cursor == len(self.old):\n            self.old, self.new, self.cursor = self.new, None, 0\n\n    def set(self, key, value):\n        self._step()\n        if self.new is None and self.size >= len(self.old):   # load factor 1\n            self.new = [[] for _ in range(len(self.old) * 2)]\n        table = self.new if self.new is not None else self.old\n        table[hash(key) % len(table)].append((key, value))\n        self.size += 1\n\n    def get(self, key):\n        self._step()\n        for table in (self.old, self.new):\n            if table is not None:\n                for k, v in table[hash(key) % len(table)]:\n                    if k == key:\n                        return v\n\nd = IncrementalDict()\nfor i in range(12):\n    d.set(f\"key{i}\", i)\n    state = f\"rehashing {len(d.old)}->{len(d.new)}, cursor {d.cursor}\" if d.new else \"stable\"\n    print(f\"after set #{i + 1:>2}: {state}\")\nprint(\"all readable:\", all(d.get(f\"key{i}\") == i for i in range(12)))",
            "label": "a hash table that grows one bucket at a time",
            "output": "after set # 1: stable\nafter set # 2: stable\nafter set # 3: stable\nafter set # 4: stable\nafter set # 5: rehashing 4->8, cursor 0\nafter set # 6: rehashing 4->8, cursor 1\nafter set # 7: rehashing 4->8, cursor 2\nafter set # 8: rehashing 4->8, cursor 3\nafter set # 9: rehashing 8->16, cursor 0\nafter set #10: rehashing 8->16, cursor 1\nafter set #11: rehashing 8->16, cursor 2\nafter set #12: rehashing 8->16, cursor 3\nall readable: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "Resizes overlap with normal traffic and complete after a few operations; every key stays readable throughout, because lookups consult both tables."
          },
          {
            "type": "caveat",
            "text": "Redis defers rehashing while a background save child process exists (unless the table gets very full), because moving entries would touch pages and defeat the copy-on-write sharing that keeps <code>fork()</code>-based snapshots cheap."
          }
        ]
      },
      {
        "title": "Sorted sets: a skiplist plus a hash table",
        "body": [
          {
            "type": "p",
            "html": "A sorted set (<code>ZSET</code>) maps members to scores and keeps them ordered by score. It is the go-to structure for leaderboards, rate-limit windows, priority queues, time-indexed events, and &mdash; in trading contexts &mdash; price-ordered books. Redis implements it with two structures at once:"
          },
          {
            "type": "p",
            "html": "<strong>A hash table</strong> from member to score, for O(1) <code>ZSCORE</code> and membership.<br><strong>A skiplist</strong> ordered by (score, member), for O(log n) insert, delete, rank and range queries."
          },
          {
            "type": "p",
            "html": "A skiplist is a sorted linked list with express lanes: each node is promoted to the next level up with probability 1/4 (in Redis), so a search skims along the top level and drops down when it would overshoot. It gives the same expected O(log n) as a balanced tree, is simple to implement, and makes range scans a walk along the bottom level. Redis also stores a <em>span</em> on each link so it can compute ranks during the search."
          },
          {
            "type": "code",
            "src": "import random\n\nrandom.seed(3)\nMAX_LEVEL, P = 8, 0.25\n\nclass Node:\n    def __init__(self, score, member, level):\n        self.score, self.member, self.next = score, member, [None] * level\n\nclass SkipList:\n    def __init__(self):\n        self.head, self.level = Node(float(\"-inf\"), None, MAX_LEVEL), 1\n\n    def insert(self, score, member):\n        update, x = [self.head] * MAX_LEVEL, self.head\n        for lvl in reversed(range(self.level)):\n            while x.next[lvl] and (x.next[lvl].score, x.next[lvl].member) < (score, member):\n                x = x.next[lvl]\n            update[lvl] = x\n        level = 1\n        while random.random() < P and level < MAX_LEVEL:\n            level += 1\n        self.level = max(self.level, level)\n        node = Node(score, member, level)\n        for lvl in range(level):\n            node.next[lvl], update[lvl].next[lvl] = update[lvl].next[lvl], node\n\n    def range_by_score(self, lo, hi):\n        x, visited = self.head, 0\n        for lvl in reversed(range(self.level)):\n            while x.next[lvl] and x.next[lvl].score < lo:\n                x, visited = x.next[lvl], visited + 1\n        out, x = [], x.next[0]\n        while x and x.score <= hi:\n            out.append((x.member, x.score))\n            x = x.next[0]\n        return out, visited\n\nbids = SkipList()\nfor i in range(10_000):\n    bids.insert(round(random.uniform(90, 110), 2), f\"order{i}\")\nhits, visited = bids.range_by_score(100.00, 100.02)\nprint(\"levels used:\", bids.level)\nprint(f\"nodes visited to find the range start: {visited} of 10,000\")\nprint(\"first matches:\", hits[:3])",
            "label": "ZRANGEBYSCORE on a skiplist",
            "output": "levels used: 7\nnodes visited to find the range start: 15 of 10,000\nfirst matches: [('order3538', 100.0), ('order3656', 100.0), ('order5011', 100.0)]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Finding the start of the range touched 15 nodes out of ten thousand, and the matches were then read off the bottom level in order."
          }
        ]
      },
      {
        "title": "Memory layout and encodings",
        "body": [
          {
            "type": "p",
            "html": "In an in-memory store the cost that matters is bytes per key, because RAM is the capacity limit. Every Redis key carries overhead: the key string, a <code>redisObject</code> header (type, encoding, LRU clock, refcount, pointer), a hash-table entry, and allocator rounding. For small values the overhead is larger than the data."
          },
          {
            "type": "p",
            "html": "Redis therefore stores small collections in compact, contiguous encodings and converts them to the full structures only when they grow:"
          },
          {
            "type": "table",
            "head": [
              "Type",
              "Small encoding",
              "Converts to",
              "Threshold (defaults)"
            ],
            "rows": [
              [
                "Hash",
                "<code>listpack</code> (flat byte array)",
                "hash table",
                "&gt; 128 fields or a value &gt; 64 bytes"
              ],
              [
                "Sorted set",
                "<code>listpack</code>",
                "skiplist + hash table",
                "&gt; 128 members or a member &gt; 64 bytes"
              ],
              [
                "Set",
                "<code>intset</code> (sorted integers) or <code>listpack</code>",
                "hash table",
                "&gt; 512 integers / &gt; 128 strings"
              ],
              [
                "List",
                "<code>listpack</code>",
                "<code>quicklist</code> (linked list of listpacks)",
                "size-based"
              ],
              [
                "String",
                "<code>int</code> or <code>embstr</code> (header and bytes in one allocation)",
                "<code>raw</code>",
                "&gt; 44 bytes"
              ]
            ]
          },
          {
            "type": "p",
            "html": "A listpack lookup is a linear scan, but over a few hundred bytes of contiguous memory that is faster than chasing hash-table pointers, and it uses a fraction of the memory. The same effect is visible in Python:"
          },
          {
            "type": "code",
            "src": "import sys\n\nn = 100\nas_dict = {f\"field{i}\": i for i in range(n)}\nas_packed = \"\".join(f\"field{i}\\0{i}\\0\" for i in range(n)).encode()\n\ndict_bytes = sys.getsizeof(as_dict) + sum(sys.getsizeof(k) + sys.getsizeof(v)\n                                          for k, v in as_dict.items())\nprint(f\"dict of {n} small fields: {dict_bytes:>6,} bytes\")\nprint(f\"packed into one buffer:  {sys.getsizeof(as_packed):>6,} bytes\")",
            "label": "object-per-field vs one contiguous buffer",
            "output": "dict of 100 small fields: 10,918 bytes\npacked into one buffer:   1,113 bytes",
            "isError": false
          },
          {
            "type": "p",
            "html": "Practical consequences: store an object as one hash with many fields rather than many top-level keys, keep collections under the encoding thresholds where you can, and remember that a 1&nbsp;GB dataset may need several GB of RAM once overhead, fragmentation, replication buffers and the copy-on-write headroom for snapshots are included. <code>MEMORY USAGE key</code> and <code>OBJECT ENCODING key</code> show the real numbers."
          }
        ]
      },
      {
        "title": "Persistence trade-offs",
        "body": [
          {
            "type": "p",
            "html": "Redis offers two persistence mechanisms, and they are often combined:"
          },
          {
            "type": "table",
            "head": [
              "",
              "RDB snapshot",
              "AOF (append-only file)"
            ],
            "rows": [
              [
                "What",
                "Point-in-time binary dump of the whole dataset",
                "Log of every write command"
              ],
              [
                "How",
                "<code>fork()</code>; the child writes the snapshot while the parent keeps serving, sharing memory copy-on-write",
                "Append each write; periodically rewrite the file compactly in a child process"
              ],
              [
                "Data lost on crash",
                "Everything since the last snapshot (minutes)",
                "Depends on <code>appendfsync</code> (below)"
              ],
              [
                "Restart speed",
                "Fast: load a compact file",
                "Slower: replay commands (mitigated by an RDB preamble)"
              ],
              [
                "Cost",
                "Fork latency and up to 2&times; memory under heavy writes",
                "Continuous disk writes and fsyncs"
              ]
            ]
          },
          {
            "type": "table",
            "head": [
              "<code>appendfsync</code>",
              "Behaviour",
              "Worst-case loss"
            ],
            "rows": [
              [
                "<code>always</code>",
                "fsync before replying to each write",
                "Nothing acknowledged, but every write waits for the disk"
              ],
              [
                "<code>everysec</code> (default)",
                "A background thread fsyncs once a second",
                "About one second of writes"
              ],
              [
                "<code>no</code>",
                "Leave flushing to the OS",
                "Whatever the OS had not flushed (often ~30 s)"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The <code>fork()</code> detail matters for large instances: the fork itself must copy the parent&rsquo;s page tables, which for a 50&nbsp;GB process can take a significant fraction of a second, during which Redis serves nothing. Every page written while the child is saving is duplicated, so memory can spike. Transparent huge pages make both worse and should be disabled."
          },
          {
            "type": "caveat",
            "text": "A Redis replica acknowledging a write does not make it durable: replication is asynchronous by default. <code>WAIT numreplicas timeout</code> blocks until that many replicas have received the write, which narrows the window but does not provide the guarantees of a consensus protocol."
          }
        ]
      },
      {
        "title": "Caching with Redis: eviction and invalidation",
        "body": [
          {
            "type": "p",
            "html": "When Redis is a cache it runs with <code>maxmemory</code> and an eviction policy that decides what to drop when full:"
          },
          {
            "type": "table",
            "head": [
              "Policy",
              "Evicts"
            ],
            "rows": [
              [
                "<code>noeviction</code>",
                "Nothing; writes fail with an error (the default &mdash; right for a database, wrong for a cache)"
              ],
              [
                "<code>allkeys-lru</code> / <code>volatile-lru</code>",
                "Least recently used, among all keys / keys with a TTL"
              ],
              [
                "<code>allkeys-lfu</code> / <code>volatile-lfu</code>",
                "Least frequently used (a decaying logarithmic counter per key)"
              ],
              [
                "<code>volatile-ttl</code>",
                "Keys closest to expiry"
              ],
              [
                "<code>allkeys-random</code> / <code>volatile-random</code>",
                "Random"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Redis does not keep an exact LRU list; that would cost two pointers per key and a list update on every read. It stores a 24-bit last-access clock per key, samples a handful of keys when it needs to evict (<code>maxmemory-samples</code>, default 5), and evicts the oldest of the sample, keeping a small pool of good candidates between rounds. How close does sampling get?"
          },
          {
            "type": "code",
            "src": "import random\nfrom collections import OrderedDict\n\nrandom.seed(11)\nKEYS, CAPACITY, REQUESTS = 5_000, 500, 60_000\nweights = [1 / (i + 1) for i in range(KEYS)]          # Zipf-like popularity\ntrace = random.choices(range(KEYS), weights, k=REQUESTS)\n\ndef exact_lru():\n    cache, hits = OrderedDict(), 0\n    for k in trace:\n        if k in cache:\n            hits += 1\n            cache.move_to_end(k)\n        else:\n            if len(cache) >= CAPACITY:\n                cache.popitem(last=False)\n            cache[k] = True\n    return hits / REQUESTS\n\ndef sampled_lru(samples):\n    rng = random.Random(5)\n    cache, hits = {}, 0                                # key -> last access time\n    for t, k in enumerate(trace):\n        if k in cache:\n            hits += 1\n        elif len(cache) >= CAPACITY:\n            victim = min(rng.sample(list(cache), samples), key=cache.get)\n            del cache[victim]\n        cache[k] = t\n    return hits / REQUESTS\n\nprint(f\"exact LRU:            {exact_lru():.1%} hit ratio\")\nfor s in (1, 3, 5, 10):\n    print(f\"sampled, {s:>2} per evict: {sampled_lru(s):.1%}\")",
            "label": "approximated LRU vs the real thing on a skewed workload",
            "output": "exact LRU:            65.1% hit ratio\nsampled,  1 per evict: 60.5%\nsampled,  3 per evict: 64.0%\nsampled,  5 per evict: 64.6%\nsampled, 10 per evict: 65.0%",
            "isError": false
          },
          {
            "type": "p",
            "html": "Sampling one key is random eviction; five is already close to true LRU, at a fraction of the memory and CPU. That is the whole design philosophy of Redis in one table: exactness traded away where the difference does not matter."
          },
          {
            "type": "p",
            "html": "Eviction is only half of caching. Keeping cached values consistent with the source of truth &mdash; invalidation, stampedes, hot keys &mdash; is covered on the caching page."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Redis is single-threaded. How does it handle 100,000+ operations per second, and when does the single thread become a problem?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Each command is a few hundred nanoseconds to a microsecond of in-memory work on a known data structure, with no locks, no disk I/O on the request path, and no context switches. An event loop (epoll/kqueue) multiplexes thousands of connections on that thread. Pipelining lets clients send many commands per round trip, so the per-command network cost amortises. The network stack, not the CPU, is usually the limit, and Redis 6+ moves socket reads and writes to I/O threads."
          },
          {
            "type": "p",
            "html": "It becomes a problem when one command is slow, because everything queues behind it: O(n) commands on big keys (<code>KEYS</code>, <code>HGETALL</code>, <code>SMEMBERS</code>, <code>ZRANGE 0 -1</code>), deleting a large key synchronously, long Lua scripts, or the latency of <code>fork()</code> for persistence on a large dataset. It also caps one instance at one core&rsquo;s worth of command execution; beyond that you shard with Redis Cluster."
          }
        ]
      },
      {
        "q": "How would you build a real-time leaderboard of the top 100 among 10 million players, including &ldquo;what is my rank?&rdquo;",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A sorted set with the score as the score and the player ID as the member. <code>ZADD board score player</code> (or <code>ZINCRBY</code>) updates in O(log n). <code>ZREVRANGE board 0 99 WITHSCORES</code> returns the top 100 in O(log n + 100). <code>ZREVRANK board player</code> returns a player&rsquo;s rank in O(log n), which works because the skiplist stores span counts on each link."
          },
          {
            "type": "p",
            "html": "Details worth raising: ties are ordered by member name lexicographically, so encode a tie-breaker into the score if &ldquo;who got there first&rdquo; matters (for example <code>score * 1e10 + (MAX_TS - ts)</code>, staying within a double&rsquo;s 53-bit precision). For time-windowed boards keep one set per day and use <code>ZUNIONSTORE</code> for weekly views. At 10 million members the set is roughly 1&nbsp;GB; if it outgrows one node, shard by score range or keep only the top N in Redis."
          }
        ]
      },
      {
        "q": "Compare RDB and AOF persistence. If you run Redis as a primary store, what configuration would you choose and what can you still lose?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "RDB: periodic forked snapshots, compact and fast to load, but you lose everything since the last snapshot, and each fork costs page-table copying and copy-on-write memory. AOF: logs each write; with <code>appendfsync everysec</code> you lose at most about a second, with <code>always</code> nothing acknowledged but with a large write-latency cost. AOF rewrites keep the file bounded."
          },
          {
            "type": "p",
            "html": "For a primary store: AOF with <code>everysec</code> (or <code>always</code> if the latency budget allows) plus <code>aof-use-rdb-preamble yes</code> for fast restarts, periodic RDB snapshots shipped off the machine for backups, replicas for availability, and <code>WAIT</code> for writes that must reach a replica."
          },
          {
            "type": "p",
            "html": "What you can still lose: up to a second of writes on a crash with <code>everysec</code>; writes acknowledged by the primary but not yet replicated when a failover promotes a replica (replication is asynchronous, so a promoted replica can be behind); and everything if the disk lies about fsync. Redis is not a consensus-replicated database, and interviewers want to hear that you know it."
          }
        ]
      },
      {
        "q": "Why does Redis approximate LRU instead of implementing it exactly? How good is the approximation?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Exact LRU needs a doubly linked list over all keys, which costs two pointers (16 bytes) per key &mdash; significant when many values are themselves only tens of bytes &mdash; and a list splice on every read, which writes to memory on read-only operations and hurts cache behaviour."
          },
          {
            "type": "p",
            "html": "Redis instead stores a 24-bit timestamp in each object header, which it already has room for, and at eviction time samples <code>maxmemory-samples</code> keys (default 5), evicting the oldest, with a 16-entry pool that carries good candidates over to the next eviction. With 5 samples the hit ratio is within a few percent of true LRU on realistic skewed workloads; with 10 it is almost indistinguishable. The same header field holds the LFU state (an 8-bit logarithmic counter plus a decay time) when an LFU policy is selected, which is often better for caches whose popularity is stable."
          }
        ]
      },
      {
        "q": "Implement a rate limiter of 100 requests per user per minute with Redis. What are the trade-offs between approaches?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<strong>Fixed window:</strong> <code>INCR rate:{user}:{minute}</code>, <code>EXPIRE</code> on first increment; reject when over 100. One key and O(1), but a burst of 100 at 12:00:59 and 100 at 12:01:00 lets 200 through in two seconds."
          },
          {
            "type": "p",
            "html": "<strong>Sliding log:</strong> a sorted set per user with the request timestamp as score. In one <code>MULTI</code> or Lua script: <code>ZREMRANGEBYSCORE key 0 now-60s</code>, <code>ZCARD</code>, and if under the limit <code>ZADD key now id</code>. Exact, but memory grows with the limit (100 entries per active user)."
          },
          {
            "type": "p",
            "html": "<strong>Sliding window counter:</strong> keep this minute&rsquo;s and last minute&rsquo;s counts and weight the previous one by how much of it overlaps the window. Two integers per user and close to exact."
          },
          {
            "type": "p",
            "html": "<strong>Token bucket:</strong> store tokens and last-refill time in a hash and refill lazily in a Lua script. Allows controlled bursts and is the usual choice for APIs."
          },
          {
            "type": "p",
            "html": "Whatever the algorithm, the check and the update must be atomic &mdash; one Lua script or <code>MULTI</code> &mdash; or two concurrent requests both see 99 and both pass."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Redis docs: key eviction",
        "url": "https://redis.io/docs/latest/develop/reference/eviction/"
      },
      {
        "label": "Redis docs: persistence",
        "url": "https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/"
      },
      {
        "label": "Redis docs: memory optimisation",
        "url": "https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/memory-optimization/"
      },
      {
        "label": "Redis source: dict.c (incremental rehashing)",
        "url": "https://github.com/redis/redis/blob/unstable/src/dict.c"
      },
      {
        "label": "Pugh — Skip Lists: A Probabilistic Alternative to Balanced Trees",
        "url": "https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf"
      }
    ]
  },
  {
    "id": "distributed",
    "title": "Distributed Databases and Replication",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Leader/follower replication, sync vs async, quorums, failover, CAP, and split brain.",
    "intro": [
      "Copying data to several machines buys availability, read scaling and geographic locality. It also means the copies can disagree, and every distributed database is a set of decisions about what happens when they do. The interview questions in this area are really about those decisions: what can a client observe, what can be lost, and who is allowed to accept writes after a failure.",
      "The examples are small, deterministic simulations of replicas and networks. Real systems add retries, timeouts and clocks, but the failure modes are exactly these."
    ],
    "sections": [
      {
        "title": "Replication topologies",
        "body": [
          {
            "type": "table",
            "head": [
              "Topology",
              "Writes go to",
              "Used by",
              "Main hazard"
            ],
            "rows": [
              [
                "Single leader (primary/replica)",
                "One leader; followers apply its log",
                "PostgreSQL, MySQL, MongoDB replica sets, Redis",
                "Failover: who becomes leader, and what was lost"
              ],
              [
                "Multi-leader",
                "Any of several leaders (often one per region)",
                "MySQL group replication (multi-primary), CouchDB, BDR",
                "Concurrent conflicting writes must be merged"
              ],
              [
                "Leaderless",
                "Any replica; client writes to several",
                "Cassandra, ScyllaDB, DynamoDB-style stores, Riak",
                "Stale reads unless quorums overlap; read repair"
              ],
              [
                "Consensus groups",
                "Leader elected by Raft/Paxos; commit needs a majority",
                "etcd, CockroachDB, TiDB, Spanner, YugabyteDB",
                "Latency of a majority round trip; unavailable without a majority"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Single-leader replication is by far the most common, and most questions assume it. The leader writes changes to its log (the WAL, a binlog, an oplog) and streams the log to followers, which apply it in the same order. Because every follower applies the same deterministic sequence, they converge to the leader&rsquo;s state &mdash; eventually."
          },
          {
            "type": "caveat",
            "text": "Statement-based replication (shipping the SQL text) breaks on non-deterministic statements such as <code>NOW()</code>, <code>RAND()</code> or <code>UPDATE ... LIMIT</code> without <code>ORDER BY</code>. Modern systems ship either physical WAL records or logical row-level changes."
          }
        ]
      },
      {
        "title": "Synchronous vs asynchronous replication",
        "body": [
          {
            "type": "p",
            "html": "The key decision is when the leader tells the client &ldquo;committed&rdquo;:"
          },
          {
            "type": "table",
            "head": [
              "Mode",
              "Commit acknowledged after",
              "Lose data on leader failure?",
              "Latency and availability"
            ],
            "rows": [
              [
                "Asynchronous",
                "The leader&rsquo;s own WAL is durable",
                "Yes: whatever had not reached a follower",
                "Fastest; unaffected by slow followers"
              ],
              [
                "Synchronous (all)",
                "Every follower confirms",
                "No",
                "As slow as the slowest follower; any follower down blocks writes"
              ],
              [
                "Semi-synchronous / quorum",
                "At least one (or k) followers confirm",
                "No, if failover picks a confirmed follower",
                "Pays one network round trip; tolerates slow stragglers"
              ]
            ]
          },
          {
            "type": "code",
            "src": "class Replica:\n    def __init__(self, name):\n        self.name, self.log = name, []\n\ndef run(mode):\n    leader, f1, f2 = Replica(\"leader\"), Replica(\"f1\"), Replica(\"f2\")\n    acked = []\n    for i in range(1, 7):\n        write = f\"order-{i}\"\n        leader.log.append(write)\n        if i <= 5: f1.log.append(write)       # f1 is one write behind\n        if i <= 3: f2.log.append(write)       # f2 is slow\n        confirmations = sum(write in f.log for f in (f1, f2))\n        needed = {\"async\": 0, \"semi-sync\": 1, \"sync\": 2}[mode]\n        if confirmations >= needed:\n            acked.append(write)\n    # leader dies; promote the most up-to-date follower\n    new_leader = max((f1, f2), key=lambda f: len(f.log))\n    lost = [w for w in acked if w not in new_leader.log]\n    return len(acked), new_leader.name, lost\n\nfor mode in (\"async\", \"semi-sync\", \"sync\"):\n    n, who, lost = run(mode)\n    print(f\"{mode:<9} acked {n} writes; promote {who}; acknowledged but lost: {lost or 'none'}\")",
            "label": "a leader crashes: which acknowledged writes survive?",
            "output": "async     acked 6 writes; promote f1; acknowledged but lost: ['order-6']\nsemi-sync acked 5 writes; promote f1; acknowledged but lost: none\nsync      acked 3 writes; promote f1; acknowledged but lost: none",
            "isError": false
          },
          {
            "type": "p",
            "html": "Async acknowledged all six and lost one. Semi-sync only acknowledged writes a follower had, so promoting the most up-to-date follower lost nothing, but the client was told &ldquo;not yet&rdquo; about order 6 (in reality it would wait, and eventually time out). Full sync acknowledged only three, because the slow follower held everything up."
          },
          {
            "type": "p",
            "html": "PostgreSQL expresses this with <code>synchronous_standby_names = 'ANY 1 (f1, f2)'</code> and <code>synchronous_commit</code>; MySQL with semi-synchronous replication and <code>rpl_semi_sync_master_wait_for_slave_count</code>."
          },
          {
            "type": "note",
            "text": "With asynchronous replication, &ldquo;committed&rdquo; means &ldquo;committed on one machine&rdquo;. If losing the last second of acknowledged trades after a failover is unacceptable, you need at least one synchronous follower, and a failover procedure that only promotes one that is caught up."
          }
        ]
      },
      {
        "title": "Quorums",
        "body": [
          {
            "type": "p",
            "html": "Leaderless systems replicate each key to <em>N</em> nodes. A write is acknowledged once <em>W</em> of them accept it; a read asks <em>R</em> of them and takes the value with the newest version. If <strong>R + W &gt; N</strong>, every read set overlaps every write set in at least one node, so the read sees the latest acknowledged write."
          },
          {
            "type": "code",
            "src": "from itertools import combinations\n\nN = 3\nnodes = range(N)\n\ndef always_fresh(R, W):\n    \"\"\"Does every possible read quorum overlap every possible write quorum?\"\"\"\n    return all(set(r) & set(w)\n               for w in combinations(nodes, W)\n               for r in combinations(nodes, R))\n\nprint(\"N=3   R  W   R+W>N   every read sees the latest write\")\nfor R, W in [(1, 1), (1, 3), (3, 1), (2, 2), (1, 2), (2, 1)]:\n    print(f\"      {R}  {W}   {str(R + W > N):<5}   {always_fresh(R, W)}\")",
            "label": "checking the overlap condition exhaustively",
            "output": "N=3   R  W   R+W>N   every read sees the latest write\n      1  1   False   False\n      1  3   True    True\n      3  1   True    True\n      2  2   True    True\n      1  2   False   False\n      2  1   False   False",
            "isError": false
          },
          {
            "type": "p",
            "html": "Typical choices for N = 3: <code>W=2, R=2</code> (balanced, tolerates one node down for both reads and writes); <code>W=3, R=1</code> (fast reads, but any node down blocks writes); <code>W=1, R=1</code> (fast and highly available, no freshness guarantee at all)."
          },
          {
            "type": "caveat",
            "text": "R + W &gt; N is necessary, not sufficient, for strong consistency. Sloppy quorums and hinted handoff (writing to a stand-in node during a partition), concurrent writes resolved by last-write-wins with skewed clocks, and a write that succeeded on fewer than W nodes but was not rolled back can all still produce stale or lost data. Cassandra&rsquo;s <code>QUORUM</code> is not linearizable without lightweight transactions."
          }
        ]
      },
      {
        "title": "Failover and split brain",
        "body": [
          {
            "type": "p",
            "html": "When the leader fails, a follower must be promoted. Every step is harder than it sounds:"
          },
          {
            "type": "p",
            "html": "<strong>Detecting failure.</strong> Only by timeout. A leader that is merely slow (a GC pause, a saturated disk, a partitioned switch) looks exactly like a dead one. Too short a timeout causes needless failovers; too long means minutes of downtime.<br><strong>Choosing a new leader.</strong> The most up-to-date follower, which requires agreement among the survivors &mdash; a consensus problem.<br><strong>Redirecting clients</strong> and the old leader&rsquo;s followers.<br><strong>Dealing with the old leader</strong> if it comes back."
          },
          {
            "type": "p",
            "html": "The last point is <strong>split brain</strong>: the old leader was not dead, only unreachable. It still believes it is the leader and keeps accepting writes, while the new leader does too. The two histories diverge, and reconciling them usually means discarding one side&rsquo;s writes."
          },
          {
            "type": "p",
            "html": "The defence is <strong>fencing</strong>. Every leadership term gets a monotonically increasing number (an epoch, term, or generation). Storage and downstream systems remember the highest term they have seen and reject requests carrying an older one, so a zombie leader&rsquo;s writes are refused even though it does not yet know it has been replaced."
          },
          {
            "type": "code",
            "src": "class Storage:\n    def __init__(self):\n        self.highest_term, self.data = 0, []\n\n    def write(self, term, who, value):\n        if term < self.highest_term:\n            return f\"REJECTED {who} (term {term} < {self.highest_term})\"\n        self.highest_term = term\n        self.data.append(value)\n        return f\"ok       {who} (term {term})\"\n\ns = Storage()\nprint(s.write(1, \"node-A\", \"fill 100 @ 10.00\"))\n# node-A stalls in a long GC pause; the cluster elects node-B with term 2\nprint(s.write(2, \"node-B\", \"fill 50 @ 10.01\"))\n# node-A wakes up, still believing it is leader, and carries on\nprint(s.write(1, \"node-A\", \"fill 100 @ 9.99\"))\nprint(\"stored:\", s.data)",
            "label": "fencing tokens stop a zombie leader",
            "output": "ok       node-A (term 1)\nok       node-B (term 2)\nREJECTED node-A (term 1 < 2)\nstored: ['fill 100 @ 10.00', 'fill 50 @ 10.01']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Consensus protocols (Raft, Paxos, Zab) package all of this: a leader needs votes from a majority to be elected, each term has at most one leader, and an entry is committed only once a majority has it. In any partition at most one side can hold a majority, so at most one side can make progress. That is why clusters have an odd number of voting members: three tolerate one failure, five tolerate two."
          },
          {
            "type": "note",
            "text": "Two-node clusters cannot fail over safely on their own: when the link between them fails, each sees the other as dead and neither has a majority. Add a third voter (a witness or arbiter) or accept manual failover."
          }
        ]
      },
      {
        "title": "Consistency vs availability: CAP and PACELC",
        "body": [
          {
            "type": "p",
            "html": "The <strong>CAP theorem</strong>: when a network <strong>P</strong>artition separates replicas, a system must choose between <strong>C</strong>onsistency (linearizability: every read reflects the latest write, as if there were one copy) and <strong>A</strong>vailability (every request to a non-failed node gets a non-error response). You cannot drop P, because networks do partition; so the real choice is what a system does <em>during</em> one."
          },
          {
            "type": "table",
            "head": [
              "Choice during a partition",
              "Behaviour",
              "Examples"
            ],
            "rows": [
              [
                "CP",
                "The minority side refuses reads and/or writes; clients get errors or timeouts",
                "etcd, ZooKeeper, Spanner, CockroachDB, MongoDB with majority concerns, HBase"
              ],
              [
                "AP",
                "Every side keeps serving; replicas diverge and are reconciled later",
                "Cassandra and DynamoDB (default settings), Riak, CouchDB, DNS"
              ]
            ]
          },
          {
            "type": "p",
            "html": "CAP is narrow: it only describes behaviour during a partition, and it uses a very strict definition of both terms. <strong>PACELC</strong> extends it: if there is a Partition, choose Availability or Consistency; <strong>E</strong>lse, choose <strong>L</strong>atency or <strong>C</strong>onsistency. The &ldquo;else&rdquo; half is the one you live with every day: a synchronous cross-region commit costs tens of milliseconds on every write whether or not anything is failing."
          },
          {
            "type": "table",
            "head": [
              "Consistency model",
              "Guarantee",
              "Typical cost"
            ],
            "rows": [
              [
                "Linearizable",
                "Behaves like a single copy; reads see the latest completed write",
                "Consensus round trip per operation"
              ],
              [
                "Sequential",
                "All clients see operations in the same order, not necessarily real time",
                "Ordering via a single log"
              ],
              [
                "Causal",
                "Operations that depend on each other are seen in order by everyone",
                "Track dependencies (vector clocks); stays available in partitions"
              ],
              [
                "Read-your-writes / monotonic reads",
                "Session guarantees for one client",
                "Sticky routing or version tokens"
              ],
              [
                "Eventual",
                "Replicas converge if writes stop",
                "Cheapest; anything can be observed meanwhile"
              ]
            ]
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Explain the CAP theorem. Is PostgreSQL with one asynchronous replica CP or AP?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "CAP says that during a network partition a replicated system must give up either linearizable consistency or availability. It is not a menu of two from three; partitions are not optional, so the decision is only about behaviour when one happens."
          },
          {
            "type": "p",
            "html": "PostgreSQL with an async replica is neither in the strict sense. Writes go only to the primary, so a client partitioned from the primary cannot write (not available for writes). Reads from the replica can be stale (not linearizable). And if the primary fails and the replica is promoted, acknowledged writes can be lost. That is why CAP labels are a poor way to describe real systems; better to say precisely what reads can return, what writes can be lost, and what is unavailable during which failures."
          }
        ]
      },
      {
        "q": "What is split brain, and how do real systems prevent it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Split brain is two nodes both acting as leader at the same time, typically after a partition or a long pause makes a healthy leader look dead and a new one is elected. Both accept writes; the histories diverge; data is lost or corrupted when they are reconciled."
          },
          {
            "type": "p",
            "html": "Prevention has two layers. <strong>Only one leader can be elected per term</strong>: election requires votes from a strict majority, and in any partition only one side can have a majority (hence odd cluster sizes and a witness for two-node setups). <strong>A deposed leader cannot do damage</strong>: fencing tokens or epochs attached to every write let storage reject a stale leader; leases make a leader stop serving before its lease can have expired from others&rsquo; point of view; and STONITH (&ldquo;shoot the other node in the head&rdquo;) power-cycles the old leader through an out-of-band channel before promotion."
          },
          {
            "type": "p",
            "html": "The subtle part is that a node cannot know it has been deposed while it is paused, so the protection must be enforced by whoever receives its writes, not by the node itself."
          }
        ]
      },
      {
        "q": "With N = 3 replicas, which R and W would you pick for a read-heavy workload that must always see the latest write, and what happens when a node is down?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The constraint is R + W &gt; 3. For read-heavy traffic, <code>W = 3, R = 1</code> minimises read cost &mdash; any single replica is up to date &mdash; but a single node failure blocks every write. <code>W = 2, R = 2</code> keeps both reads and writes available with one node down, at the cost of reading from two replicas."
          },
          {
            "type": "p",
            "html": "Most would choose <code>R = W = 2</code>, and point out the caveats: a write that reached only one node before failing is not rolled back and may later surface (so clients must treat a failed write as &ldquo;unknown&rdquo;, not &ldquo;did not happen&rdquo;); concurrent writes need a conflict rule, and last-write-wins with wall clocks silently drops one; and sloppy quorums break the overlap argument during partitions. If true linearizability is required, use a consensus-based store instead of tuning quorums."
          }
        ]
      },
      {
        "q": "Your primary fails over to a replica and afterwards some users report that their last trades have disappeared. Explain what happened and how to stop it recurring.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "With asynchronous replication the primary acknowledged those commits after writing only its own WAL. The replica had not yet received them when the primary died. The replica was promoted, and those transactions do not exist in its history. If the old primary later rejoins, its extra WAL must be discarded (<code>pg_rewind</code>) to follow the new timeline, so the trades are gone unless recovered from the old primary&rsquo;s disk by hand."
          },
          {
            "type": "p",
            "html": "Fixes: configure at least one synchronous standby (<code>synchronous_standby_names = 'ANY 1 (...)'</code> with <code>synchronous_commit = on</code> or <code>remote_apply</code>) so every acknowledged commit exists on two machines; make the failover manager (Patroni, orchestrator) promote only a standby that was synchronous, and refuse to fail over rather than promote a lagging replica; monitor replication lag; and, for a trading system, make downstream consumers idempotent and reconcile against the exchange&rsquo;s drop copy, because the exchange&rsquo;s record is the real source of truth for fills."
          }
        ]
      },
      {
        "q": "What is the difference between linearizability and serializability?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "They answer different questions. <strong>Serializability</strong> is a transaction isolation property: the result of running transactions concurrently equals <em>some</em> serial order of them. That order need not match real time: a serializable system may order a transaction that started after yours committed before it."
          },
          {
            "type": "p",
            "html": "<strong>Linearizability</strong> is a recency property of single operations on single objects: once a write completes, every later read (in real time) sees it or something newer, as if there were one copy."
          },
          {
            "type": "p",
            "html": "<strong>Strict serializability</strong> combines them: transactions appear in a serial order consistent with real time. Spanner provides it with TrueTime; FaunaDB and CockroachDB (for most cases) aim at it. A single-node database at <code>SERIALIZABLE</code> is effectively strictly serializable; a replicated one serving reads from async replicas is serializable at best, and a read from a lagging replica is not linearizable."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "PostgreSQL: high availability, load balancing and replication",
        "url": "https://www.postgresql.org/docs/current/high-availability.html"
      },
      {
        "label": "Ongaro and Ousterhout — In Search of an Understandable Consensus Algorithm (Raft)",
        "url": "https://raft.github.io/raft.pdf"
      },
      {
        "label": "Gilbert and Lynch — Brewer's Conjecture and the Feasibility of CAP",
        "url": "https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf"
      },
      {
        "label": "Abadi — Consistency Tradeoffs in Modern Distributed Database System Design (PACELC)",
        "url": "https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf"
      },
      {
        "label": "Jepsen: consistency models",
        "url": "https://jepsen.io/consistency"
      },
      {
        "label": "Kleppmann — How to do distributed locking (fencing tokens)",
        "url": "https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html"
      }
    ]
  },
  {
    "id": "sharding",
    "title": "Partitioning and Sharding",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Hash vs range partitioning, consistent hashing, hot partitions, rebalancing and cross-shard queries.",
    "intro": [
      "Replication copies the same data to many machines. Partitioning (sharding) splits <em>different</em> data across machines, so that the dataset and the write load can exceed what one node can handle. Most real systems do both: each partition is replicated.",
      "The whole subject turns on one function &mdash; key to partition &mdash; and on what happens to it when you add a machine, when one key is far more popular than the rest, or when a query needs data from every partition."
    ],
    "sections": [
      {
        "title": "Hash partitioning vs range partitioning",
        "body": [
          {
            "type": "table",
            "head": [
              "",
              "Hash partitioning",
              "Range partitioning"
            ],
            "rows": [
              [
                "Rule",
                "partition = hash(key) mod P, or a hash range",
                "Each partition owns a contiguous key range"
              ],
              [
                "Load spread",
                "Even, for any key distribution",
                "Only as even as the keys; sequential keys all hit the last range"
              ],
              [
                "Range queries",
                "Scatter to every partition",
                "Touch only the partitions covering the range"
              ],
              [
                "Examples",
                "Cassandra, DynamoDB, Redis Cluster (16,384 hash slots), MongoDB hashed shard keys",
                "HBase, Bigtable, Spanner, CockroachDB, TiDB, MongoDB ranged shard keys"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import hashlib\nfrom collections import Counter\n\nP = 4\n# trades keyed by a timestamp: every new key is larger than the last\nkeys = [f\"2026-09-30T09:{m:02d}:{s:02d}\" for m in range(30, 60) for s in range(60)]\nrecent = keys[-300:]                                    # the last five minutes\n\ndef by_hash(k):\n    return int(hashlib.md5(k.encode()).hexdigest(), 16) % P\n\nbounds = [keys[len(keys) * i // P] for i in range(1, P)]  # split into P equal ranges\ndef by_range(k):\n    return sum(k >= b for b in bounds)\n\nfor name, f in ((\"hash\", by_hash), (\"range\", by_range)):\n    load = Counter(f(k) for k in recent)\n    print(f\"{name:<5} writes in the last 5 min per partition: {[load[p] for p in range(P)]}\")",
            "label": "sequential keys: range partitioning puts all new writes on one node",
            "output": "hash  writes in the last 5 min per partition: [78, 76, 79, 67]\nrange writes in the last 5 min per partition: [0, 0, 0, 300]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Timestamps, auto-increment IDs and anything else monotonic concentrate all current writes on the newest range. Range-partitioned systems deal with it by prefixing the key with something that spreads it (a hashed bucket, the instrument ID) at the cost of losing a single global time order &mdash; or by accepting it, as time-series databases do, since the newest partition is also the one being read."
          },
          {
            "type": "p",
            "html": "Hash partitioning also has a compound-key middle ground: Cassandra hashes only the first part of the primary key (the partition key) and sorts rows within a partition by the rest (clustering columns). <code>PRIMARY KEY ((symbol, day), ts)</code> spreads load by symbol and day while keeping each day&rsquo;s trades for one symbol sorted and together."
          }
        ]
      },
      {
        "title": "Rebalancing, and why not hash mod N",
        "body": [
          {
            "type": "p",
            "html": "Partitioning by <code>hash(key) mod N</code>, where N is the number of nodes, has a fatal flaw: changing N changes the answer for almost every key. Adding one node to ten moves about 91% of the data, all at once."
          },
          {
            "type": "code",
            "src": "import hashlib\n\ndef h(k):\n    return int(hashlib.md5(k.encode()).hexdigest(), 16)\n\nkeys = [f\"user{i}\" for i in range(100_000)]\nfor n in (4, 10, 50):\n    moved = sum(h(k) % n != h(k) % (n + 1) for k in keys)\n    print(f\"mod {n:>2} -> mod {n + 1:>2}: {moved / len(keys):.0%} of keys move \"\n          f\"(ideal: {1 / (n + 1):.0%})\")",
            "label": "adding one node under mod-N placement",
            "output": "mod  4 -> mod  5: 80% of keys move (ideal: 20%)\nmod 10 -> mod 11: 91% of keys move (ideal: 9%)\nmod 50 -> mod 51: 98% of keys move (ideal: 2%)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Two standard fixes:"
          },
          {
            "type": "p",
            "html": "<strong>Fixed number of partitions.</strong> Create many more partitions than nodes up front (say 1,000 for 10 nodes, or Redis Cluster&rsquo;s 16,384 slots) and assign whole partitions to nodes. <code>hash(key) mod 1000</code> never changes; adding a node just moves some whole partitions to it. Used by Redis Cluster, Elasticsearch, Couchbase, Riak.<br><strong>Consistent hashing</strong> (next section), which moves only about 1/N of the keys when a node joins or leaves.<br><strong>Dynamic splitting</strong> for range partitions: split a range when it grows past a size threshold and move one half. Used by HBase, Bigtable, CockroachDB, MongoDB."
          },
          {
            "type": "note",
            "text": "Rebalancing moves real data over the network while serving traffic. Automatic rebalancing on node-failure detection can turn a slow node into a cascading overload; many operators keep a human in the loop for it."
          }
        ]
      },
      {
        "title": "Consistent hashing",
        "body": [
          {
            "type": "p",
            "html": "Place both nodes and keys on a ring of hash values. Each key belongs to the first node clockwise from its position. When a node joins, it takes over only the keys between itself and its predecessor; when one leaves, only its keys move to its successor. Everything else stays put."
          },
          {
            "type": "p",
            "html": "With one position per node, the arcs are wildly uneven. The fix is <strong>virtual nodes</strong>: each physical node takes many positions on the ring, so its total share averages out, and when it leaves, its keys spread across many other nodes instead of landing on one neighbour."
          },
          {
            "type": "code",
            "src": "import bisect, hashlib\nfrom collections import Counter\n\ndef h(s):\n    return int(hashlib.md5(s.encode()).hexdigest(), 16)\n\nclass Ring:\n    def __init__(self, nodes, vnodes):\n        self.points = sorted((h(f\"{n}#{v}\"), n) for n in nodes for v in range(vnodes))\n        self.hashes = [p for p, _ in self.points]\n\n    def owner(self, key):\n        i = bisect.bisect(self.hashes, h(key)) % len(self.points)\n        return self.points[i][1]\n\nkeys = [f\"order{i}\" for i in range(50_000)]\nnodes = [\"A\", \"B\", \"C\", \"D\"]\nfor vnodes in (1, 10, 200):\n    before = Ring(nodes, vnodes)\n    load = Counter(before.owner(k) for k in keys)\n    after = Ring(nodes + [\"E\"], vnodes)\n    moved = sum(before.owner(k) != after.owner(k) for k in keys)\n    shares = \" \".join(f\"{n}:{load[n] / len(keys):>4.0%}\" for n in nodes)\n    print(f\"vnodes={vnodes:<4} load {shares}   add E -> {moved / len(keys):.0%} of keys move\")",
            "label": "load balance and data movement on a hash ring",
            "output": "vnodes=1    load A:  3% B:  1% C: 40% D: 56%   add E -> 17% of keys move\nvnodes=10   load A: 12% B: 40% C: 22% D: 26%   add E -> 25% of keys move\nvnodes=200  load A: 26% B: 26% C: 26% D: 21%   add E -> 19% of keys move",
            "isError": false
          },
          {
            "type": "p",
            "html": "With one point per node the load is badly skewed. With a couple of hundred virtual nodes each node holds close to a quarter, and adding a fifth node moves close to the ideal fifth of the keys &mdash; taken from all four existing nodes rather than from a single neighbour."
          },
          {
            "type": "caveat",
            "text": "Other schemes reach the same goal: <em>rendezvous (highest-random-weight) hashing</em> scores every node for each key and picks the highest, with no ring to maintain; <em>jump consistent hash</em> maps a key to one of N buckets with no memory at all, but only supports adding or removing the last bucket."
          }
        ]
      },
      {
        "title": "Hot partitions and hot keys",
        "body": [
          {
            "type": "p",
            "html": "Even hashing only spreads <em>keys</em> evenly. If one key receives a large share of the traffic &mdash; a celebrity account, the most traded symbol at the open, a global counter &mdash; its partition becomes the bottleneck no matter how many nodes you add."
          },
          {
            "type": "code",
            "src": "import random, zlib\nfrom collections import Counter\n\nrandom.seed(2)\nP = 8\nsymbols = [f\"SYM{i}\" for i in range(400)]\nweights = [60 if s == \"SYM0\" else 1 for s in symbols]     # one symbol is hot\ntrades = random.choices(symbols, weights, k=40_000)\n\ndef partition(key):\n    return zlib.crc32(key.encode()) % P\n\nplain = Counter(partition(s) for s in trades)\nsalted = Counter(partition(f\"{s}#{random.randrange(8)}\" if s == \"SYM0\" else s)\n                 for s in trades)\n\nfor name, load in ((\"plain\", plain), (\"salted\", salted)):\n    loads = [load[p] for p in range(P)]\n    print(f\"{name:<6} {loads}   max/avg = {max(loads) / (sum(loads) / P):.2f}\")",
            "label": "one hot symbol, and splitting it across sub-keys",
            "output": "plain  [4253, 4245, 4408, 9618, 4528, 4412, 4142, 4394]   max/avg = 1.92\nsalted [4913, 4919, 5050, 5002, 5205, 5075, 4812, 5024]   max/avg = 1.04",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Salting</strong> (appending a small random suffix to a known hot key) spreads its writes over several partitions. The price is on the read side: reading that key now means reading all its sub-keys and combining them. It suits counters and append-only events well; it suits &ldquo;read the current value&rdquo; badly."
          },
          {
            "type": "p",
            "html": "Other tools: a cache in front of hot reads (with request coalescing, see the caching page); splitting a hot range more finely than its size alone would justify (DynamoDB and CockroachDB split on load, not just size); and, for write-hot counters, buffering increments locally and flushing them in batches."
          }
        ]
      },
      {
        "title": "Cross-shard queries and transactions",
        "body": [
          {
            "type": "p",
            "html": "Partitioning is cheap exactly as long as each request touches one partition. Everything else costs:"
          },
          {
            "type": "table",
            "head": [
              "Operation",
              "What happens",
              "Cost"
            ],
            "rows": [
              [
                "Lookup by partition key",
                "Route to one shard",
                "One network hop"
              ],
              [
                "Query by a non-key column",
                "Scatter to every shard, gather and merge",
                "Latency of the slowest shard; load on all of them"
              ],
              [
                "Secondary index, local (document-partitioned)",
                "Each shard indexes its own rows; queries still scatter",
                "Cheap writes, expensive reads"
              ],
              [
                "Secondary index, global (term-partitioned)",
                "The index is itself partitioned by the indexed value",
                "Cheap reads, but every write updates a remote index shard (usually asynchronously)"
              ],
              [
                "Join across shards",
                "Ship one side to the other, or both to a coordinator",
                "Network-bound; avoid on the hot path"
              ],
              [
                "Transaction across shards",
                "Two-phase commit (or a consensus-backed variant)",
                "Extra round trips; blocking if the coordinator fails mid-protocol"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The design response is to choose the partition key so that the common access patterns stay local. Co-locate related data: shard orders, fills and positions all by account, so an account&rsquo;s transaction never leaves its shard. Accept that some queries &mdash; &ldquo;total exposure across all accounts&rdquo; &mdash; will scatter, and serve them from a separate analytical copy rather than from the OLTP shards."
          },
          {
            "type": "code",
            "src": "import heapq\n\n# each shard returns its own top 3 by notional, already sorted\nshards = {\n    \"shard0\": [(\"acct7\", 9_400), (\"acct2\", 7_100), (\"acct11\", 3_000)],\n    \"shard1\": [(\"acct4\", 12_800), (\"acct9\", 9_900), (\"acct1\", 900)],\n    \"shard2\": [(\"acct5\", 8_800), (\"acct3\", 8_700), (\"acct8\", 8_600)],\n}\nmerged = heapq.merge(*shards.values(), key=lambda r: r[1], reverse=True)\nprint(\"global top 3:\", list(merged)[:3])",
            "label": "scatter-gather: top N across shards needs top N from each",
            "output": "global top 3: [('acct4', 12800), ('acct9', 9900), ('acct7', 9400)]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Each shard must return its own top N, not just its top 1, because the global top three can all live on one shard. Here two of them do: had each shard sent only its best row, <code>acct9</code> would have been missed. The same reasoning makes <code>LIMIT</code>/<code>OFFSET</code> across shards painful: page 100 needs 100 pages&rsquo; worth of rows from every shard."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why is <code>hash(key) % N</code> a bad sharding function, and what do you use instead?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Because N changes. Going from N to N+1 nodes reassigns roughly N/(N+1) of all keys &mdash; about 90% when going from 10 to 11 &mdash; so adding capacity means moving nearly the whole dataset at once, exactly when the system is under load."
          },
          {
            "type": "p",
            "html": "Alternatives: a <strong>fixed, large number of partitions</strong> (hash mod 16,384, as in Redis Cluster) mapped to nodes through a table, so adding a node moves whole partitions; <strong>consistent hashing</strong> with virtual nodes, which moves about 1/(N+1) of keys evenly from all existing nodes; or <strong>range partitions that split dynamically</strong>. All three decouple the key-to-partition function from the node count."
          }
        ]
      },
      {
        "q": "What are virtual nodes in consistent hashing and what problems do they solve?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Each physical node is placed on the ring at many positions (tens to hundreds) instead of one. That solves three problems. <strong>Uneven load</strong>: with one position per node, random placement gives some nodes arcs several times larger than others; many positions average out. <strong>Uneven recovery</strong>: when a node leaves, its keys would all move to its single successor, doubling that node&rsquo;s load; with virtual nodes they scatter across the whole cluster. <strong>Heterogeneous hardware</strong>: a node with twice the capacity simply gets twice as many virtual nodes."
          },
          {
            "type": "p",
            "html": "The cost is a larger ring to store and search (a sorted array with binary search makes that trivial) and more, smaller ranges to track when streaming data during rebalancing."
          }
        ]
      },
      {
        "q": "Design the sharding scheme for an order management system that stores orders, fills and positions for 50,000 accounts. What is the shard key and what queries become expensive?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Shard by <strong>account ID</strong>, hashed into a fixed number of logical partitions mapped onto physical nodes. Orders, fills and positions for one account are co-located, so the core transaction &mdash; record a fill and update the position &mdash; is single-shard and needs no distributed commit. Risk checks per account are local too."
          },
          {
            "type": "p",
            "html": "Expensive: anything across accounts. Firm-wide exposure per symbol, &ldquo;all open orders for symbol X&rdquo; (needed for a symbol halt or a mass cancel), and end-of-day reports all scatter to every shard. Serve those from a separate store fed by change-data-capture: a per-symbol aggregate maintained in a stream processor, and a columnar warehouse for reporting."
          },
          {
            "type": "p",
            "html": "Also discuss hot accounts: a market-making account can generate orders of magnitude more traffic than the median. Options are giving it a dedicated partition, or splitting its orders by strategy or symbol as a sub-key while keeping its position aggregate on one partition. Re-sharding when an account outgrows its partition should move a whole logical partition, never re-hash."
          }
        ]
      },
      {
        "q": "How do secondary indexes work in a sharded database, and what are the trade-offs between local and global indexes?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<strong>Local (document-partitioned) index:</strong> each shard indexes only its own rows. Writes stay on one shard and the index is always consistent with its data. But a query by the indexed column has no idea which shard holds matches, so it scatters to all of them &mdash; tail latency is set by the slowest shard, and the cost of that query grows with cluster size. MongoDB, Cassandra (native secondary indexes) and Elasticsearch work this way."
          },
          {
            "type": "p",
            "html": "<strong>Global (term-partitioned) index:</strong> the index is partitioned by the <em>indexed value</em>, so all entries for <code>symbol = 'ABC'</code> live on one index shard. Reads go to one place. But a write to a row may have to update index shards on other nodes, which is either a distributed transaction (slow) or asynchronous (so the index lags the data). DynamoDB global secondary indexes are asynchronous; Spanner and CockroachDB keep them transactional."
          },
          {
            "type": "p",
            "html": "Choose local indexes for write-heavy data where indexed queries are rare or always include the shard key; global ones where lookups by the secondary attribute are frequent and latency-sensitive."
          }
        ]
      },
      {
        "q": "A single partition in your cluster is running at 100% CPU while the others are at 10%. Walk through diagnosing and fixing it.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "First, is it a <strong>hot key</strong> or a <strong>hot range</strong>? Look at per-key request metrics or sample traffic on that node. A single key dominating (a popular symbol, a global counter, a misbehaving client retrying one request) is different from many keys that happen to share a range (monotonically increasing keys all landing on the newest range partition)."
          },
          {
            "type": "p",
            "html": "Hot range: split the range, and if the cause is sequential keys, change the key design (prefix with a hash bucket or a high-cardinality attribute). Hot key, read-heavy: cache it in front of the database with request coalescing so a thundering herd becomes one read, or replicate the hot key&rsquo;s partition more and read from replicas. Hot key, write-heavy: salt it into sub-keys and aggregate on read, or batch updates in the application and write them periodically."
          },
          {
            "type": "p",
            "html": "Also rule out the non-data causes: a compaction or repair running only on that node, a bad disk, a noisy neighbour, or a skewed client that pins connections to one node."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Karger et al. — Consistent Hashing and Random Trees",
        "url": "https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf"
      },
      {
        "label": "DeCandia et al. — Dynamo: Amazon's Highly Available Key-value Store",
        "url": "https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf"
      },
      {
        "label": "Redis: cluster specification (hash slots)",
        "url": "https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/"
      },
      {
        "label": "Lamping and Veach — A Fast, Minimal Memory, Consistent Hash Algorithm",
        "url": "https://arxiv.org/abs/1406.2294"
      },
      {
        "label": "MongoDB: choosing a shard key",
        "url": "https://www.mongodb.com/docs/manual/core/sharding-choose-a-shard-key/"
      }
    ]
  },
  {
    "id": "durability",
    "title": "Write-Ahead Logging and Durability",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "WAL mechanics, what fsync really promises, sequential vs random I/O, and redo/undo crash recovery.",
    "intro": [
      "The D in ACID is a promise about a moment in time: once <code>COMMIT</code> returns, the data survives a crash. Keeping that promise without making every commit slow is what the write-ahead log is for, and understanding it means understanding what the operating system and the disk actually guarantee &mdash; which is less than most people assume.",
      "The storage-internals page introduced the WAL and checkpoints. This one goes deeper: the log&rsquo;s structure, <code>fsync</code> and its failure modes, why sequential I/O is cheap, and how redo and undo logging recover a database after a crash. The examples write and recover a real log file."
    ],
    "sections": [
      {
        "title": "WAL mechanics",
        "body": [
          {
            "type": "p",
            "html": "The log is an append-only sequence of records, each identified by a <strong>log sequence number</strong> (LSN), usually its byte offset. A record describes one change: which page or row, and enough information to redo it (and, in some designs, to undo it). Every data page carries the LSN of the last record applied to it, which is how recovery knows whether a page already contains a change."
          },
          {
            "type": "p",
            "html": "The protocol has two rules:"
          },
          {
            "type": "p",
            "html": "<strong>1. Log before data.</strong> A dirty page may not be written to the data file until the log is durable up to that page&rsquo;s LSN.<br><strong>2. Log before commit.</strong> A transaction is committed when its commit record is durable in the log, and not before."
          },
          {
            "type": "code",
            "src": "import json, os, struct, tempfile, zlib\n\nclass KV:\n    \"\"\"Redo-only WAL: every record is [length][crc32][json payload].\"\"\"\n    def __init__(self, path):\n        self.path, self.data = path, {}\n        self.fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND)\n        self.fsyncs = 0\n\n    def _append(self, record):\n        payload = json.dumps(record).encode()\n        os.write(self.fd, struct.pack(\">II\", len(payload), zlib.crc32(payload)) + payload)\n\n    def commit(self, txid, writes, sync=True):\n        for key, value in writes.items():\n            self._append({\"tx\": txid, \"k\": key, \"v\": value})\n        self._append({\"tx\": txid, \"commit\": True})\n        if sync:\n            os.fsync(self.fd)                  # durable before we say \"committed\"\n            self.fsyncs += 1\n        self.data.update(writes)               # then apply in memory\n\n    @staticmethod\n    def recover(path):\n        \"\"\"Replay committed transactions; stop at the first torn or corrupt record.\"\"\"\n        pending, data, good = {}, {}, 0\n        with open(path, \"rb\") as f:\n            blob = f.read()\n        pos = 0\n        while pos + 8 <= len(blob):\n            length, crc = struct.unpack(\">II\", blob[pos:pos + 8])\n            payload = blob[pos + 8:pos + 8 + length]\n            if len(payload) < length or zlib.crc32(payload) != crc:\n                break                          # torn write at the tail: ignore the rest\n            rec = json.loads(payload)\n            if rec.get(\"commit\"):\n                data.update(pending.pop(rec[\"tx\"], {}))\n                good += 1\n            else:\n                pending.setdefault(rec[\"tx\"], {})[rec[\"k\"]] = rec[\"v\"]\n            pos += 8 + length\n        return data, good, len(pending), len(blob) - pos\n\nd = tempfile.mkdtemp()\npath = os.path.join(d, \"wal.log\")\ndb = KV(path)\ndb.commit(1, {\"AAPL\": 100, \"MSFT\": 50})\ndb.commit(2, {\"AAPL\": 70})\ndb._append({\"tx\": 3, \"k\": \"MSFT\", \"v\": 0})     # tx 3 wrote but never committed\nos.close(db.fd)                                # crash: in-memory state is gone\n\ndata, committed, uncommitted, junk = KV.recover(path)\nprint(\"recovered:\", data)\nprint(f\"{committed} committed transactions replayed, {uncommitted} uncommitted ignored\")",
            "label": "a redo log: replay what committed, ignore what did not",
            "output": "recovered: {'AAPL': 70, 'MSFT': 50}\n2 committed transactions replayed, 1 uncommitted ignored",
            "isError": false
          },
          {
            "type": "p",
            "html": "Transaction 3&rsquo;s change is in the log but has no commit record, so recovery ignores it. Nothing was ever written to a separate data file here: the log alone is enough to rebuild the state, which is the key insight &mdash; the data files are just a cache of the log that makes reads fast."
          },
          {
            "type": "p",
            "html": "Real WAL records are physical or physiological (&ldquo;on page 812, slot 4, set these bytes&rdquo;) rather than logical key/value pairs, which makes redo fast and independent of higher-level structures. PostgreSQL additionally logs a <em>full page image</em> the first time a page is modified after each checkpoint, so a page torn by a crash mid-write can be restored whole."
          }
        ]
      },
      {
        "title": "fsync: what it does and does not promise",
        "body": [
          {
            "type": "p",
            "html": "<code>write()</code> copies data into the kernel&rsquo;s page cache and returns. The data may reach the disk seconds later, or never, if the machine loses power. <code>fsync(fd)</code> asks the kernel to push the file&rsquo;s dirty pages <em>and</em> tell the device to flush its own volatile cache, and returns when the device says the data is on stable storage."
          },
          {
            "type": "table",
            "head": [
              "Call",
              "Guarantees"
            ],
            "rows": [
              [
                "<code>write()</code>",
                "Data is in the OS page cache. Survives a process crash, not a power loss or kernel panic"
              ],
              [
                "<code>fsync()</code>",
                "File data and metadata are on stable storage (if the device is honest)"
              ],
              [
                "<code>fdatasync()</code>",
                "File data plus only the metadata needed to read it back (size), skipping timestamps: often one fewer write"
              ],
              [
                "<code>O_DIRECT</code>",
                "Bypasses the page cache; does <em>not</em> by itself imply durability"
              ],
              [
                "<code>O_DSYNC</code> / <code>O_SYNC</code>",
                "Every <code>write()</code> behaves as if followed by <code>fdatasync()</code> / <code>fsync()</code>"
              ],
              [
                "fsync on the directory",
                "Needed after creating or renaming a file, or the new name itself may vanish"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The places durability goes wrong in practice:"
          },
          {
            "type": "p",
            "html": "<strong>Lying hardware.</strong> Consumer drives and some virtualised storage acknowledge a flush that only reached a volatile cache. Enterprise SSDs have power-loss protection (capacitors) that makes their cache effectively durable, which is also why they can acknowledge fsync quickly.<br><strong>fsync errors.</strong> The 2018 &ldquo;fsyncgate&rdquo; discovery: on Linux, if writeback fails, the kernel may mark the pages clean and report the error once; a retried <code>fsync</code> then succeeds without the data ever reaching disk. PostgreSQL now treats any fsync failure as fatal and recovers from the WAL instead of retrying.<br><strong>macOS.</strong> <code>fsync()</code> does not flush the drive cache; <code>fcntl(F_FULLFSYNC)</code> does. SQLite has <code>PRAGMA fullfsync</code> for this.<br><strong>Configuration.</strong> <code>synchronous_commit = off</code>, <code>innodb_flush_log_at_trx_commit = 2</code> or Redis&rsquo;s <code>appendfsync everysec</code> deliberately trade the last fraction of a second of commits for speed."
          },
          {
            "type": "note",
            "text": "An fsync costs roughly 0.05&ndash;0.5&nbsp;ms on an enterprise NVMe drive with power-loss protection, and several milliseconds on consumer or network storage. That single number bounds how many durable, serial commits per second a system can do &mdash; unless commits are batched."
          }
        ]
      },
      {
        "title": "Group commit",
        "body": [
          {
            "type": "p",
            "html": "If every transaction pays for its own fsync, commit throughput is capped at 1 / fsync latency. <strong>Group commit</strong> lets transactions that commit at around the same time share one: the first waiting committer calls fsync for everything appended so far, and every transaction whose commit record was covered returns together."
          },
          {
            "type": "code",
            "src": "import json, os, struct, tempfile, zlib\n\nclass KV:\n    \"\"\"Redo-only WAL: every record is [length][crc32][json payload].\"\"\"\n    def __init__(self, path):\n        self.path, self.data = path, {}\n        self.fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND)\n        self.fsyncs = 0\n\n    def _append(self, record):\n        payload = json.dumps(record).encode()\n        os.write(self.fd, struct.pack(\">II\", len(payload), zlib.crc32(payload)) + payload)\n\n    def commit(self, txid, writes, sync=True):\n        for key, value in writes.items():\n            self._append({\"tx\": txid, \"k\": key, \"v\": value})\n        self._append({\"tx\": txid, \"commit\": True})\n        if sync:\n            os.fsync(self.fd)                  # durable before we say \"committed\"\n            self.fsyncs += 1\n        self.data.update(writes)               # then apply in memory\n\n    @staticmethod\n    def recover(path):\n        \"\"\"Replay committed transactions; stop at the first torn or corrupt record.\"\"\"\n        pending, data, good = {}, {}, 0\n        with open(path, \"rb\") as f:\n            blob = f.read()\n        pos = 0\n        while pos + 8 <= len(blob):\n            length, crc = struct.unpack(\">II\", blob[pos:pos + 8])\n            payload = blob[pos + 8:pos + 8 + length]\n            if len(payload) < length or zlib.crc32(payload) != crc:\n                break                          # torn write at the tail: ignore the rest\n            rec = json.loads(payload)\n            if rec.get(\"commit\"):\n                data.update(pending.pop(rec[\"tx\"], {}))\n                good += 1\n            else:\n                pending.setdefault(rec[\"tx\"], {})[rec[\"k\"]] = rec[\"v\"]\n            pos += 8 + length\n        return data, good, len(pending), len(blob) - pos\n\nd = tempfile.mkdtemp()\n\none_each = KV(os.path.join(d, \"a.log\"))\nfor tx in range(1, 101):\n    one_each.commit(tx, {f\"k{tx}\": tx})\n\ngrouped = KV(os.path.join(d, \"b.log\"))\nfor tx in range(1, 101):\n    grouped.commit(tx, {f\"k{tx}\": tx}, sync=False)\n    if tx % 20 == 0:                           # one flush covers 20 commit records\n        os.fsync(grouped.fd)\n        grouped.fsyncs += 1\n\nprint(\"fsync per commit:\", one_each.fsyncs, \"fsyncs for 100 commits\")\nprint(\"group commit:    \", grouped.fsyncs, \"fsyncs for 100 commits\")\nprint(\"same log recovered:\", KV.recover(one_each.path)[0] == KV.recover(grouped.path)[0])",
            "label": "100 commits, 100 fsyncs vs 5",
            "output": "fsync per commit: 100 fsyncs for 100 commits\ngroup commit:     5 fsyncs for 100 commits\nsame log recovered: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "The durability guarantee is unchanged: no transaction in a group is acknowledged until the fsync covering it returns. Each waits a little longer, and throughput rises by the group size. PostgreSQL exposes the knobs as <code>commit_delay</code> and <code>commit_siblings</code>; InnoDB and most modern engines group automatically; Kafka and trading-system journals batch the same way."
          }
        ]
      },
      {
        "title": "Sequential vs random I/O",
        "body": [
          {
            "type": "p",
            "html": "Logs are append-only because sequential writes are dramatically cheaper than random ones, on every kind of storage:"
          },
          {
            "type": "table",
            "head": [
              "Device",
              "Random 4&nbsp;KB writes",
              "Sequential writes",
              "Why"
            ],
            "rows": [
              [
                "Spinning disk (7,200 rpm)",
                "~100&ndash;200 IOPS (0.5&ndash;1&nbsp;MB/s)",
                "150&ndash;250&nbsp;MB/s",
                "Each random write waits for a seek and half a rotation, ~5&ndash;10&nbsp;ms"
              ],
              [
                "SATA SSD",
                "Tens of thousands IOPS",
                "~500&nbsp;MB/s",
                "No seek, but flash erases in large blocks; random writes fragment them and trigger garbage collection"
              ],
              [
                "NVMe SSD",
                "Hundreds of thousands IOPS",
                "Several GB/s",
                "Deep parallel queues; random is fast, but sequential still wins on write amplification and endurance"
              ],
              [
                "Network block storage",
                "Capped IOPS per volume",
                "Capped throughput",
                "Every I/O is a network round trip; IOPS are what you pay for"
              ]
            ]
          },
          {
            "type": "p",
            "html": "On an HDD the ratio is one to two orders of magnitude, which is where the WAL design came from. On SSDs random reads are nearly as fast as sequential ones, but random <em>writes</em> still cost more: the flash translation layer must erase whole blocks (often megabytes) before rewriting pages in them, and scattered small writes leave blocks partly valid, forcing the drive to copy live data around &mdash; the SSD&rsquo;s own write amplification. Sequential writes fill and invalidate whole blocks together."
          },
          {
            "type": "p",
            "html": "Other reasons sequential wins regardless of device: it allows large I/Os (fewer system calls, fewer interrupts), read-ahead and write-combining in the kernel work, and a single append position means a single fsync covers everything."
          },
          {
            "type": "note",
            "text": "This is the common thread of the WAL, LSM trees, Kafka, and exchange/trading journals: turn random updates into one sequential append stream, and build random-access structures from it lazily."
          }
        ]
      },
      {
        "title": "Crash recovery: redo, undo and ARIES",
        "body": [
          {
            "type": "p",
            "html": "Two policy choices determine what the log must contain:"
          },
          {
            "type": "table",
            "head": [
              "Policy",
              "Meaning",
              "Consequence for recovery"
            ],
            "rows": [
              [
                "<strong>Steal</strong>",
                "Dirty pages of <em>uncommitted</em> transactions may be written to disk (e.g. evicted from a full buffer pool)",
                "Disk may hold uncommitted changes, so the log needs <strong>undo</strong> information"
              ],
              [
                "<strong>No-steal</strong>",
                "Uncommitted changes never reach disk",
                "No undo needed, but a big transaction must fit in memory"
              ],
              [
                "<strong>Force</strong>",
                "All of a transaction&rsquo;s pages are written at commit",
                "No redo needed, but every commit does random writes"
              ],
              [
                "<strong>No-force</strong>",
                "Pages are written whenever convenient after commit",
                "Disk may miss committed changes, so the log needs <strong>redo</strong> information"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Real engines choose <strong>steal / no-force</strong> for performance, so they need both redo and undo. The standard algorithm is <strong>ARIES</strong>, and its three passes are worth knowing by name:"
          },
          {
            "type": "p",
            "html": "<strong>1. Analysis.</strong> Scan forward from the last checkpoint to find which transactions were active at the crash and which pages might be dirty.<br><strong>2. Redo.</strong> Replay history from the oldest relevant LSN, reapplying every logged change whose page LSN shows it is missing &mdash; <em>including</em> changes of transactions that will be rolled back. This &ldquo;repeat history&rdquo; restores the exact state at the moment of the crash.<br><strong>3. Undo.</strong> Roll back the transactions that never committed, newest change first, writing <em>compensation log records</em> as it goes so that a crash during recovery does not undo anything twice."
          },
          {
            "type": "p",
            "html": "Not every engine follows ARIES literally. PostgreSQL needs no undo pass at all: its MVCC keeps old row versions in the heap, so an aborted transaction&rsquo;s tuples are simply invisible (its transaction ID is marked aborted) and are cleaned by vacuum later. InnoDB uses a redo log plus undo logs in its rollback segments. SQLite in rollback-journal mode is the opposite design: it saves original pages to a journal before overwriting them (undo), and in WAL mode it appends new pages and never overwrites in place (redo)."
          },
          {
            "type": "code",
            "src": "import json, os, struct, tempfile, zlib\n\nclass KV:\n    \"\"\"Redo-only WAL: every record is [length][crc32][json payload].\"\"\"\n    def __init__(self, path):\n        self.path, self.data = path, {}\n        self.fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND)\n        self.fsyncs = 0\n\n    def _append(self, record):\n        payload = json.dumps(record).encode()\n        os.write(self.fd, struct.pack(\">II\", len(payload), zlib.crc32(payload)) + payload)\n\n    def commit(self, txid, writes, sync=True):\n        for key, value in writes.items():\n            self._append({\"tx\": txid, \"k\": key, \"v\": value})\n        self._append({\"tx\": txid, \"commit\": True})\n        if sync:\n            os.fsync(self.fd)                  # durable before we say \"committed\"\n            self.fsyncs += 1\n        self.data.update(writes)               # then apply in memory\n\n    @staticmethod\n    def recover(path):\n        \"\"\"Replay committed transactions; stop at the first torn or corrupt record.\"\"\"\n        pending, data, good = {}, {}, 0\n        with open(path, \"rb\") as f:\n            blob = f.read()\n        pos = 0\n        while pos + 8 <= len(blob):\n            length, crc = struct.unpack(\">II\", blob[pos:pos + 8])\n            payload = blob[pos + 8:pos + 8 + length]\n            if len(payload) < length or zlib.crc32(payload) != crc:\n                break                          # torn write at the tail: ignore the rest\n            rec = json.loads(payload)\n            if rec.get(\"commit\"):\n                data.update(pending.pop(rec[\"tx\"], {}))\n                good += 1\n            else:\n                pending.setdefault(rec[\"tx\"], {})[rec[\"k\"]] = rec[\"v\"]\n            pos += 8 + length\n        return data, good, len(pending), len(blob) - pos\n\nd = tempfile.mkdtemp()\npath = os.path.join(d, \"wal.log\")\ndb = KV(path)\ndb.commit(1, {\"cash\": 1_000})\ndb.commit(2, {\"cash\": 400, \"AAPL\": 3})\nsize = os.path.getsize(path)\ndb.commit(3, {\"cash\": 0, \"AAPL\": 5})\nos.close(db.fd)\n\nwith open(path, \"r+b\") as f:        # the machine lost power half-way through writing tx 3\n    f.truncate(size + 20)\n\ndata, committed, uncommitted, junk = KV.recover(path)\nprint(\"recovered:\", data)\nprint(f\"committed: {committed}, incomplete: {uncommitted}, torn bytes ignored: {junk}\")",
            "label": "a torn final record is detected by its checksum and discarded",
            "output": "recovered: {'cash': 400, 'AAPL': 3}\ncommitted: 2, incomplete: 0, torn bytes ignored: 20",
            "isError": false
          },
          {
            "type": "p",
            "html": "The checksum and length prefix let recovery tell a complete record from a partially written one. Transaction 3 was never acknowledged (its fsync had not returned when the power failed), so losing it breaks no promise."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Walk through exactly what happens, from the client&rsquo;s <code>COMMIT</code> to the data being on disk, in a WAL-based database.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "During the transaction each change is applied to a page in the buffer pool (making it dirty) and a log record describing it is appended to the in-memory WAL buffer. At <code>COMMIT</code> the engine appends a commit record and then flushes the WAL buffer up to that record&rsquo;s LSN: <code>write()</code> to the log file and <code>fsync()</code> (possibly shared with other transactions via group commit). When the fsync returns, the commit is durable, locks are released and the client is told it succeeded."
          },
          {
            "type": "p",
            "html": "The data pages are still only dirty in memory. They reach the data files later &mdash; when the background writer or a checkpoint flushes them, or when the buffer pool evicts them &mdash; and always after the log records covering them are durable. If replication is synchronous, the commit also waits for a standby to confirm receipt (or application) of the WAL before replying."
          }
        ]
      },
      {
        "q": "What does fsync guarantee, and name three ways data can still be lost after fsync returned successfully.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "fsync guarantees that the file&rsquo;s modified data and metadata have been handed to the storage device and that the device has reported them durable. Ways that still fails:"
          },
          {
            "type": "p",
            "html": "<strong>1. The device lies</strong>: a volatile write cache without power-loss protection acknowledges the flush; on power loss, data is gone. Common on consumer drives and some virtual disks.<br><strong>2. The directory entry was not synced</strong>: a newly created or renamed file&rsquo;s data is durable but its name is not, so after a crash the file does not exist. You must fsync the parent directory too.<br><strong>3. An earlier writeback error was swallowed</strong>: on Linux a failed background writeback can mark pages clean and report the error to only one fsync caller; a later fsync then returns success for data that never reached disk.<br><strong>4. Platform semantics</strong>: on macOS <code>fsync</code> does not flush the drive cache (<code>F_FULLFSYNC</code> does).<br><strong>5. The only copy was on one machine</strong>: fsync protects against power loss, not against the disk or server dying. Durability across hardware failure needs replication."
          }
        ]
      },
      {
        "q": "Explain steal/no-steal and force/no-force, and why most databases need both redo and undo logs.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<strong>Steal</strong> means the buffer manager may write a page containing uncommitted changes to disk, for example to make room. If the transaction then aborts or the system crashes, those changes are on disk and must be removed, so the log needs <em>undo</em> information. <strong>No-force</strong> means committed changes are not required to be on disk at commit, only in the log; after a crash they may be missing, so the log needs <em>redo</em> information."
          },
          {
            "type": "p",
            "html": "Steal/no-force is the high-performance combination: the buffer pool is not limited by the size of open transactions, and commits require only a sequential log flush rather than random page writes. The price is recovery that does both redo and undo, which is what ARIES does: analysis, redo everything (repeating history), then undo losers with compensation log records."
          },
          {
            "type": "p",
            "html": "No-steal/force would need neither log, but it would make every commit write all its pages randomly and make large transactions impossible. Shadow paging (LMDB, early System R) achieves no-undo differently: write new versions of pages elsewhere and atomically switch a root pointer at commit."
          }
        ]
      },
      {
        "q": "Why are sequential writes cheaper than random writes, even on SSDs?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "On spinning disks the reason is mechanical: a random write needs a seek and rotational delay of several milliseconds, a sequential one streams at full media speed, a difference of 100&times; or more."
          },
          {
            "type": "p",
            "html": "SSDs have no seek, and random <em>reads</em> are nearly as fast as sequential. Random <em>writes</em> are still more expensive because flash can only be written to erased pages, and erasure happens in large blocks. Small scattered writes invalidate pages spread across many blocks; to reclaim space the drive&rsquo;s garbage collector must copy the still-valid pages out of a block before erasing it. That internal copying is the SSD&rsquo;s write amplification: it consumes bandwidth, raises latency unpredictably, and wears the flash out faster. Sequential writes fill and later invalidate whole blocks together, which makes garbage collection nearly free."
          },
          {
            "type": "p",
            "html": "Beyond the device, sequential I/O allows large requests, fewer system calls, effective write-combining, and a single fsync covering all of it."
          }
        ]
      },
      {
        "q": "A trading system journals every order event before acting on it. It must sustain 200,000 events per second with durable acknowledgement, and fsync takes 100 microseconds. How?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "At 100&nbsp;&micro;s per fsync, one fsync per event caps throughput at 10,000 per second, twenty times too few. The answer is batching: accumulate events for a short window (or until N events), write them as one sequential append, fsync once, then acknowledge the whole batch. At 200,000 events per second, a batch every 100&nbsp;&micro;s holds about 20 events, and the added latency per event is at most one batch interval plus one fsync."
          },
          {
            "type": "p",
            "html": "Refinements worth mentioning: a dedicated journaling thread that owns the file descriptor (single writer, no locks), with producers handing it events through a lock-free ring buffer; preallocating the journal file so appends never extend file metadata (then <code>fdatasync</code> is cheap, or use <code>O_DSYNC</code>); an NVMe drive with power-loss protection, which is what makes 100&nbsp;&micro;s fsyncs possible at all; and, because a single disk is a single failure domain, replicating the journal to a second machine and counting an event as durable when it is in memory on two machines &mdash; which many low-latency systems prefer to a local fsync."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "PostgreSQL: reliability and the write-ahead log",
        "url": "https://www.postgresql.org/docs/current/wal-reliability.html"
      },
      {
        "label": "Mohan et al. — ARIES: A Transaction Recovery Method",
        "url": "https://cs.stanford.edu/people/chrismre/cs345/rl/aries.pdf"
      },
      {
        "label": "SQLite: atomic commit in SQLite",
        "url": "https://www.sqlite.org/atomiccommit.html"
      },
      {
        "label": "PostgreSQL wiki: fsync errors",
        "url": "https://wiki.postgresql.org/wiki/Fsync_Errors"
      },
      {
        "label": "Pillai et al. — All File Systems Are Not Created Equal",
        "url": "https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-pillai.pdf"
      }
    ]
  },
  {
    "id": "recovery",
    "title": "Replication Lag, Backups and Recovery",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "What lagging replicas let clients see, RPO and RTO, failover in practice, backups and point-in-time recovery.",
    "intro": [
      "The distributed-databases page covered how replication works and how leaders are elected. This page is about living with it: what clients observe when replicas lag, how a failover actually runs, and what you do when the problem is not a dead machine but bad data &mdash; a dropped table, a buggy deploy, a corrupted disk &mdash; which replication faithfully copies to every replica within milliseconds.",
      "Replicas protect against hardware failure. Only backups protect against mistakes. Interviewers probe whether you know the difference."
    ],
    "sections": [
      {
        "title": "Replication lag and what clients see",
        "body": [
          {
            "type": "p",
            "html": "An asynchronous follower is always some distance behind the leader: normally milliseconds, but seconds or minutes during a write burst, a long-running query on the replica, network trouble, or a large transaction the replica must apply serially. Reading from replicas scales reads, and exposes that lag to users as three distinct anomalies:"
          },
          {
            "type": "table",
            "head": [
              "Anomaly",
              "What the user sees",
              "Guarantee that prevents it"
            ],
            "rows": [
              [
                "Read-your-writes violation",
                "Submits an order, refreshes, and the order is not there",
                "Read-your-writes (read-after-write) consistency"
              ],
              [
                "Non-monotonic reads",
                "Refreshes twice and the order appears, then disappears (two replicas with different lag)",
                "Monotonic reads"
              ],
              [
                "Causality violation",
                "Sees a fill for an order that does not exist yet",
                "Consistent prefix / causal consistency"
              ]
            ]
          },
          {
            "type": "code",
            "src": "class Replica:\n    def __init__(self, name, applied):\n        self.name, self.applied = name, applied      # log position applied so far\n\nlog = [\"order 1\", \"order 2\", \"order 3 (yours)\"]\nleader_pos = 3\nr1, r2 = Replica(\"r1\", 3), Replica(\"r2\", 2)          # r2 lags by one write\n\ndef read(replica):\n    return log[:replica.applied]\n\nprint(\"read via r2:\", read(r2), \"<- your order is missing\")\nprint(\"read via r1:\", read(r1))\nprint(\"read via r2:\", read(r2), \"<- and gone again\")\n\n# fix: the client remembers the log position of its last write,\n# and only uses a replica that has applied at least that much\nmy_token = leader_pos\ndef safe_read(replicas):\n    ok = [r for r in replicas if r.applied >= my_token]\n    return (ok[0].name, read(ok[0])) if ok else (\"leader\", log[:leader_pos])\n\nprint(\"with token:\", safe_read([r2, r1]))\nprint(\"with token:\", safe_read([r2]))",
            "label": "lagging replicas, and fixing it with a position token",
            "output": "read via r2: ['order 1', 'order 2'] <- your order is missing\nread via r1: ['order 1', 'order 2', 'order 3 (yours)']\nread via r2: ['order 1', 'order 2'] <- and gone again\nwith token: ('r1', ['order 1', 'order 2', 'order 3 (yours)'])\nwith token: ('leader', ['order 1', 'order 2', 'order 3 (yours)'])",
            "isError": false
          },
          {
            "type": "p",
            "html": "Practical techniques: send a user&rsquo;s reads to the leader for a short window after they write; carry the write&rsquo;s LSN or GTID as a token and wait for (or pick) a replica that has applied it (<code>pg_last_wal_replay_lsn()</code>, MySQL&rsquo;s <code>WAIT_FOR_EXECUTED_GTID_SET</code>); pin each session to one replica for monotonic reads; and route anything that must be current &mdash; balances, positions, risk &mdash; to the leader, always."
          },
          {
            "type": "note",
            "text": "Monitor lag in <em>time</em> and in <em>bytes</em> (PostgreSQL <code>pg_stat_replication.replay_lag</code>, MySQL <code>Seconds_Behind_Source</code>), and alert on it. Lag is what turns a failover into data loss."
          }
        ]
      },
      {
        "title": "RPO and RTO",
        "body": [
          {
            "type": "p",
            "html": "Every recovery plan is judged by two numbers:"
          },
          {
            "type": "table",
            "head": [
              "",
              "Question",
              "Driven by"
            ],
            "rows": [
              [
                "<strong>RPO</strong> &mdash; recovery point objective",
                "How much recently committed data may be lost?",
                "Synchronous vs async replication, WAL archiving frequency, backup schedule"
              ],
              [
                "<strong>RTO</strong> &mdash; recovery time objective",
                "How long may the service be down?",
                "Automatic vs manual failover, restore speed, WAL replay volume, cache warm-up"
              ]
            ]
          },
          {
            "type": "table",
            "head": [
              "Failure",
              "Typical response",
              "RPO",
              "RTO"
            ],
            "rows": [
              [
                "Database process crash",
                "Restart; WAL recovery from last checkpoint",
                "0",
                "Seconds to minutes (checkpoint interval)"
              ],
              [
                "Machine or disk dies",
                "Fail over to a replica",
                "0 if sync, else the replication lag",
                "Seconds (automated) to minutes"
              ],
              [
                "Datacenter / region lost",
                "Fail over to a remote replica",
                "Usually &gt; 0: cross-region replication is async",
                "Minutes; DNS and clients must move"
              ],
              [
                "Bad data: <code>DROP TABLE</code>, buggy migration, ransomware",
                "Point-in-time restore from backups",
                "0 up to the moment before the mistake",
                "Hours for large databases"
              ],
              [
                "Silent corruption",
                "Restore from a backup taken before the corruption",
                "Whatever since that backup",
                "Hours"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Notice that replication handles the middle rows and does nothing for the last two, because it copies the mistake too."
          }
        ]
      },
      {
        "title": "Failover in practice",
        "body": [
          {
            "type": "p",
            "html": "The mechanics, once a leader is declared dead, typically run through a manager such as Patroni (PostgreSQL), Orchestrator or MySQL Group Replication, or a managed cloud service:"
          },
          {
            "type": "p",
            "html": "<strong>1. Fence the old leader.</strong> Make sure it cannot accept writes: revoke its lease in the consensus store (etcd, ZooKeeper, Consul), cut it off at the network or storage layer, or power it off.<br><strong>2. Choose the candidate.</strong> The replica with the most WAL received; with synchronous replication, only a replica that was synchronous. Refuse to promote one lagging beyond the allowed RPO.<br><strong>3. Promote.</strong> The replica finishes replaying what it has, starts a new timeline or epoch, and begins accepting writes.<br><strong>4. Repoint.</strong> Other replicas follow the new leader; clients are redirected by a virtual IP, DNS, a proxy (HAProxy, PgBouncer, ProxySQL) or a topology-aware driver.<br><strong>5. Rejoin the old leader</strong> as a replica after rewinding any WAL it wrote that the new leader never saw (<code>pg_rewind</code>)."
          },
          {
            "type": "p",
            "html": "Planned <strong>switchovers</strong> (for upgrades or maintenance) run the same steps without loss: stop writes on the old leader, wait until the candidate has applied everything, then promote. Practise them; an untested failover path usually fails the first time it is needed."
          },
          {
            "type": "caveat",
            "text": "Clients see a failover as a burst of connection errors, and any transaction in flight at that moment has an unknown outcome: it may or may not have committed on the old leader and replicated. Retrying non-idempotent writes blindly can duplicate them. Use idempotency keys (a client-generated order ID with a unique constraint) so a retry is harmless."
          }
        ]
      },
      {
        "title": "Backups",
        "body": [
          {
            "type": "table",
            "head": [
              "Kind",
              "How",
              "Pros",
              "Cons"
            ],
            "rows": [
              [
                "Logical",
                "<code>pg_dump</code>, <code>mysqldump</code>: SQL or rows",
                "Portable across versions; restore one table",
                "Slow to take and very slow to restore at scale; indexes rebuilt"
              ],
              [
                "Physical",
                "Copy data files: <code>pg_basebackup</code>, Percona XtraBackup, storage snapshots",
                "Fast restore; exact copy",
                "Same major version and architecture; whole cluster only"
              ],
              [
                "Continuous (WAL archiving)",
                "Ship every WAL segment to object storage as it fills",
                "Enables point-in-time recovery; RPO of seconds",
                "Needs a base backup to replay onto; archive must be monitored"
              ]
            ]
          },
          {
            "type": "p",
            "html": "A physical backup of a running database is copied while pages are changing, so on its own it is inconsistent. It becomes consistent by replaying the WAL generated during the copy, which is why backup tools record the start and end WAL positions. SQLite&rsquo;s online backup API makes a consistent copy of a live database page by page:"
          },
          {
            "type": "code",
            "src": "import os, sqlite3, tempfile\n\nd = tempfile.mkdtemp()\nlive = sqlite3.connect(os.path.join(d, \"live.db\"))\nlive.execute(\"CREATE TABLE fills(id INTEGER PRIMARY KEY, sym TEXT, qty INT)\")\nlive.executemany(\"INSERT INTO fills(sym, qty) VALUES (?, ?)\",\n                 [(f\"S{i % 50}\", i % 7 + 1) for i in range(20_000)])\nlive.commit()\n\ncopies = []\ndef progress(status, remaining, total):\n    copies.append(total - remaining)\n\nbackup = sqlite3.connect(os.path.join(d, \"backup.db\"))\nlive.backup(backup, pages=16, progress=progress)     # 16 pages per step\n\nprint(\"steps:\", len(copies), \"| pages copied:\", copies[-1])\nprint(\"integrity:\", backup.execute(\"PRAGMA integrity_check\").fetchone()[0])\nprint(\"rows match:\", backup.execute(\"SELECT count(*), sum(qty) FROM fills\").fetchone()\n      == live.execute(\"SELECT count(*), sum(qty) FROM fills\").fetchone())",
            "label": "an online, consistent backup with SQLite's backup API",
            "output": "steps: 5 | pages copied: 65\nintegrity: ok\nrows match: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "The rules that matter more than the tooling: keep backups off the machine and preferably in another account or region (the <strong>3-2-1 rule</strong>: three copies, two media, one off-site), make at least one copy immutable so ransomware or a compromised admin cannot delete it, encrypt them, and <strong>test restores regularly</strong>. A backup that has never been restored is a hypothesis."
          }
        ]
      },
      {
        "title": "Point-in-time recovery",
        "body": [
          {
            "type": "p",
            "html": "PITR combines a base backup with the archived WAL. Restore the base backup, then replay WAL forward and <em>stop just before</em> the mistake: <code>recovery_target_time</code>, <code>recovery_target_lsn</code> or <code>recovery_target_xid</code> in PostgreSQL, <code>mysqlbinlog --stop-datetime</code> in MySQL."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\n# the archive: every change since the base backup, with its commit time\narchive = [\n    (\"09:00:01\", \"INSERT INTO positions VALUES ('AAPL', 100)\"),\n    (\"09:30:12\", \"INSERT INTO positions VALUES ('MSFT', 250)\"),\n    (\"10:02:40\", \"UPDATE positions SET qty = 180 WHERE sym = 'AAPL'\"),\n    (\"10:05:03\", \"DELETE FROM positions\"),                  # the mistake\n    (\"10:07:55\", \"INSERT INTO positions VALUES ('NVDA', 40)\"),\n]\n\ndef restore(until=None):\n    db = sqlite3.connect(\":memory:\")\n    db.execute(\"CREATE TABLE positions(sym TEXT, qty INT)\")    # the base backup\n    for ts, sql in archive:\n        if until and ts >= until:\n            break\n        db.execute(sql)\n    return db.execute(\"SELECT * FROM positions ORDER BY sym\").fetchall()\n\nprint(\"replay everything:        \", restore())\nprint(\"recovery target 10:05:00: \", restore(until=\"10:05:00\"))",
            "label": "replaying the archive up to a moment before the mistake",
            "output": "replay everything:         [('NVDA', 40)]\nrecovery target 10:05:00:  [('AAPL', 180), ('MSFT', 250)]",
            "isError": false
          },
          {
            "type": "p",
            "html": "Stopping before the <code>DELETE</code> recovers the positions but also discards the legitimate <code>NVDA</code> insert that came after it. Real incidents usually end with a restore to a separate instance at the target time, then a careful copy of the lost data back into production, so that later valid work is kept."
          },
          {
            "type": "note",
            "text": "RTO for PITR is the time to copy the base backup plus the time to replay the WAL since it was taken. Frequent base backups keep the replay short; that trade-off, not storage cost, usually sets the backup schedule."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why is a replica not a backup?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A replica protects against the loss of a machine: it has a current copy of the data and can take over. But it is current by design, so every logical mistake &mdash; <code>DROP TABLE</code>, a <code>DELETE</code> without a <code>WHERE</code>, a migration that corrupts a column, an application bug writing garbage, ransomware encrypting rows through the database &mdash; replicates to it within milliseconds. The same applies to corruption introduced by a software bug above the storage layer."
          },
          {
            "type": "p",
            "html": "A backup is a copy from the past that the mistake cannot reach: base backups plus archived WAL, stored separately and ideally immutably, so you can restore to the moment before the problem. You need both. A delayed replica (<code>recovery_min_apply_delay</code>) is a useful middle ground, giving an hour or so to catch a mistake before it arrives, but it is not a substitute for real backups."
          }
        ]
      },
      {
        "q": "A user places an order and immediately refreshes their order list, which is served from read replicas. Sometimes the order is missing. How do you fix it without sending all reads to the primary?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It is a read-your-writes violation caused by replication lag. Options, from simplest to most precise:"
          },
          {
            "type": "p",
            "html": "<strong>Time-based stickiness:</strong> for a few seconds after a user writes, route that user&rsquo;s reads to the primary (store the last-write time in their session).<br><strong>Position tokens:</strong> return the commit&rsquo;s LSN or GTID with the write response; on the next read, pick a replica whose applied position is at least that token, or make the replica wait until it is (bounded by a timeout, then fall back to the primary).<br><strong>Route by data:</strong> data the user just changed or must see accurately (their own orders, balances) always comes from the primary; shared, slowly changing data comes from replicas."
          },
          {
            "type": "p",
            "html": "Also pin a session to one replica, or the user may see the order appear and disappear as successive reads hit replicas with different lag."
          }
        ]
      },
      {
        "q": "Someone ran <code>DELETE FROM trades</code> without a WHERE clause at 14:32 on the production primary. Walk through recovery.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<strong>Stop the damage.</strong> Confirm what happened and when (the audit log, <code>pg_stat_statements</code>, the binlog). Decide whether to halt writes; usually not &mdash; the rest of the system keeps working, and later valid writes must be preserved."
          },
          {
            "type": "p",
            "html": "<strong>Restore to the side.</strong> Provision a separate instance, restore the most recent base backup before 14:32, and replay the archived WAL with a recovery target just before the delete (ideally the transaction ID or LSN of the delete, found by inspecting the WAL with <code>pg_waldump</code> or <code>mysqlbinlog</code>, rather than a clock time)."
          },
          {
            "type": "p",
            "html": "<strong>Reconcile.</strong> Copy the deleted rows from the restored instance back into production. Rows inserted after 14:32 are already in production and must be kept; rows that were updated after the restore point need a decision. Verify counts and checksums against downstream systems."
          },
          {
            "type": "p",
            "html": "<strong>Prevent recurrence.</strong> Remove direct write access to production for humans, require reviewed migrations, set <code>sql_safe_updates</code> (MySQL) or use a transaction with a row-count check, and keep a delayed replica so the next incident can be recovered in minutes rather than hours."
          }
        ]
      },
      {
        "q": "What are RPO and RTO, and how would you achieve an RPO of zero and an RTO under 30 seconds for a PostgreSQL database?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "RPO is the maximum acceptable data loss, measured in time; RTO is the maximum acceptable downtime."
          },
          {
            "type": "p",
            "html": "RPO of zero means no acknowledged commit may be lost, so every commit must exist on at least two machines before it is acknowledged: synchronous replication with <code>synchronous_standby_names = 'ANY 1 (s1, s2)'</code> and <code>synchronous_commit = on</code> (or <code>remote_apply</code> if reads from the standby must see it). Two synchronous candidates, so one failing does not block commits."
          },
          {
            "type": "p",
            "html": "RTO under 30 seconds needs automated failover: Patroni (or similar) with a consensus store for leader election and fencing, short but not twitchy health-check timeouts, promotion restricted to synchronous standbys, and clients that reconnect quickly through a proxy or a virtual IP. Keep WAL replay on standbys current and checkpoints frequent so promotion is fast."
          },
          {
            "type": "p",
            "html": "Then state the limits: this covers machine failure, not logical errors (needs PITR, with an RTO of hours); a full region loss would still lose data unless a synchronous replica is in another region, at a latency cost on every commit."
          }
        ]
      },
      {
        "q": "What happens to in-flight transactions during a failover, and how should the application handle it?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Connections to the old leader break. For a transaction that had not sent <code>COMMIT</code>, the outcome is clear: it never committed, and the application retries it from the beginning. For a transaction whose <code>COMMIT</code> was sent but whose reply never arrived, the outcome is <em>unknown</em>: the commit might have been applied and replicated, applied on the old leader only (and lost in the failover), or never applied."
          },
          {
            "type": "p",
            "html": "The application must therefore make writes idempotent: a client-generated unique ID (an order&rsquo;s client order ID) with a unique constraint, so retrying a commit that actually succeeded fails harmlessly with a duplicate-key error the application recognises as success. For non-idempotent operations such as incrementing a balance, record the operation with its ID in the same transaction and check for it before re-applying."
          },
          {
            "type": "p",
            "html": "Connection pools should detect the failover (errors, or the server reporting it is read-only) and drain and re-establish connections rather than retrying on dead sockets; drivers with multi-host connection strings and <code>target_session_attrs=read-write</code> find the new leader automatically."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "PostgreSQL: continuous archiving and point-in-time recovery",
        "url": "https://www.postgresql.org/docs/current/continuous-archiving.html"
      },
      {
        "label": "PostgreSQL: pg_rewind",
        "url": "https://www.postgresql.org/docs/current/app-pgrewind.html"
      },
      {
        "label": "SQLite: the online backup API",
        "url": "https://www.sqlite.org/backup.html"
      },
      {
        "label": "Patroni documentation",
        "url": "https://patroni.readthedocs.io/"
      },
      {
        "label": "MySQL: point-in-time recovery using binary logs",
        "url": "https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html"
      }
    ]
  },
  {
    "id": "normalization",
    "title": "Normalization and Denormalization",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "1NF through BCNF as the removal of update anomalies, and when to deliberately undo it.",
    "intro": [
      "Normalization is a method for deciding which columns belong in which table so that each fact is stored exactly once. The normal forms sound academic, but each one exists to remove a specific way that data goes wrong: an update that changes one copy of a fact but not another, a fact you cannot record until some unrelated fact exists, or a fact that disappears when you delete something else.",
      "Denormalization deliberately reintroduces duplication to make reads cheaper. Both are tools; the interview question is always about the trade-off."
    ],
    "sections": [
      {
        "title": "Why normalize: the three anomalies",
        "body": [
          {
            "type": "p",
            "html": "Start with one wide table of trades that also records each trader&rsquo;s desk and each desk&rsquo;s head:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.execute(\"\"\"CREATE TABLE trades_wide(\n    trade_id INT PRIMARY KEY, trader TEXT, desk TEXT, desk_head TEXT,\n    sym TEXT, qty INT)\"\"\")\ndb.executemany(\"INSERT INTO trades_wide VALUES (?, ?, ?, ?, ?, ?)\", [\n    (1, \"ann\", \"rates\",  \"kim\", \"UST10Y\", 5),\n    (2, \"ann\", \"rates\",  \"kim\", \"UST2Y\",  8),\n    (3, \"bob\", \"equity\", \"lee\", \"AAPL\",   100),\n])\n\n# update anomaly: the rates desk gets a new head, but we only fix one row\ndb.execute(\"UPDATE trades_wide SET desk_head = 'raj' WHERE trade_id = 1\")\nprint(\"rates desk heads:\", db.execute(\n    \"SELECT DISTINCT desk_head FROM trades_wide WHERE desk = 'rates'\").fetchall())\n\n# deletion anomaly: bob's only trade is cancelled, and the equity desk vanishes\ndb.execute(\"DELETE FROM trades_wide WHERE trade_id = 3\")\nprint(\"desks we know:   \", db.execute(\"SELECT DISTINCT desk FROM trades_wide\").fetchall())",
            "label": "one fact, many copies",
            "output": "rates desk heads: [('raj',), ('kim',)]\ndesks we know:    [('rates',)]",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Update anomaly:</strong> a fact stored in many rows can be changed in some and not others, and the database now contradicts itself. <strong>Deletion anomaly:</strong> removing one fact (a trade) destroys an unrelated one (the equity desk exists and is run by Lee). <strong>Insertion anomaly:</strong> you cannot record a new desk and its head until someone on it trades."
          },
          {
            "type": "p",
            "html": "Each normal form below removes one class of dependency that causes these."
          }
        ]
      },
      {
        "title": "1NF, 2NF and 3NF",
        "body": [
          {
            "type": "table",
            "head": [
              "Form",
              "Rule",
              "Violation looks like",
              "Fix"
            ],
            "rows": [
              [
                "<strong>1NF</strong>",
                "Every column holds one atomic value; no repeating groups",
                "<code>symbols = 'AAPL,MSFT'</code>, or <code>phone1, phone2, phone3</code>",
                "One row per value in a child table"
              ],
              [
                "<strong>2NF</strong>",
                "1NF, and no non-key column depends on only <em>part</em> of a composite key",
                "Key <code>(order_id, line_no)</code>, but <code>customer</code> depends on <code>order_id</code> alone",
                "Move it to a table keyed by <code>order_id</code>"
              ],
              [
                "<strong>3NF</strong>",
                "2NF, and no non-key column depends on another non-key column",
                "<code>trader &rarr; desk &rarr; desk_head</code>",
                "Move <code>desk_head</code> to a <code>desks</code> table"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The memorable summary of 3NF: every non-key attribute depends on <em>the key, the whole key, and nothing but the key</em>. Applied to the table above, <code>desk</code> depends on <code>trader</code> and <code>desk_head</code> depends on <code>desk</code>, neither of which is the key:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE desks  (desk TEXT PRIMARY KEY, desk_head TEXT);\n    CREATE TABLE traders(trader TEXT PRIMARY KEY, desk TEXT REFERENCES desks);\n    CREATE TABLE trades (trade_id INT PRIMARY KEY,\n                         trader TEXT REFERENCES traders, sym TEXT, qty INT);\n    INSERT INTO desks   VALUES ('rates', 'kim'), ('equity', 'lee');\n    INSERT INTO traders VALUES ('ann', 'rates'), ('bob', 'equity');\n    INSERT INTO trades  VALUES (1, 'ann', 'UST10Y', 5), (2, 'ann', 'UST2Y', 8),\n                               (3, 'bob', 'AAPL', 100);\n\"\"\")\ndb.execute(\"UPDATE desks SET desk_head = 'raj' WHERE desk = 'rates'\")   # one row\ndb.execute(\"DELETE FROM trades WHERE trade_id = 3\")\n\nfor row in db.execute(\"\"\"\n        SELECT t.trade_id, t.trader, d.desk, d.desk_head, t.sym\n        FROM trades t JOIN traders USING (trader) JOIN desks d USING (desk)\"\"\"):\n    print(row)\nprint(\"desks we know:\", db.execute(\"SELECT * FROM desks\").fetchall())",
            "label": "the same data in 3NF: each fact stored once",
            "output": "(1, 'ann', 'rates', 'raj', 'UST10Y')\n(2, 'ann', 'rates', 'raj', 'UST2Y')\ndesks we know: [('rates', 'raj'), ('equity', 'lee')]",
            "isError": false
          },
          {
            "type": "p",
            "html": "The desk head changes in one place and every trade sees it; deleting Bob&rsquo;s trade leaves the equity desk intact. The cost is the two joins needed to reassemble the wide view."
          }
        ]
      },
      {
        "title": "BCNF",
        "body": [
          {
            "type": "p",
            "html": "<strong>Boyce&ndash;Codd normal form</strong> tightens 3NF: for <em>every</em> non-trivial functional dependency X &rarr; Y, X must be a superkey. 3NF allows one exception &mdash; Y may be part of some candidate key &mdash; and that exception is where the remaining anomalies hide."
          },
          {
            "type": "p",
            "html": "The classic case: each instructor teaches exactly one course, and a student takes each course from one instructor. The table <code>(student, course, instructor)</code> has candidate keys <code>(student, course)</code> and <code>(student, instructor)</code>, and the dependency <code>instructor &rarr; course</code>. Every attribute is part of some key, so it is in 3NF; but <code>instructor</code> is not a superkey, so it violates BCNF, and &ldquo;which course does Dr. X teach&rdquo; is repeated for every student."
          },
          {
            "type": "code",
            "src": "from itertools import combinations\n\ndef closure(attrs, fds):\n    \"\"\"All attributes determined by attrs under the dependencies fds.\"\"\"\n    result, changed = set(attrs), True\n    while changed:\n        changed = False\n        for lhs, rhs in fds:\n            if set(lhs) <= result and not set(rhs) <= result:\n                result |= set(rhs)\n                changed = True\n    return result\n\ndef candidate_keys(schema, fds):\n    keys = []\n    for n in range(1, len(schema) + 1):\n        for combo in combinations(sorted(schema), n):\n            if closure(combo, fds) == set(schema) and not any(set(k) <= set(combo) for k in keys):\n                keys.append(combo)\n    return keys\n\ndef bcnf_violations(schema, fds):\n    \"\"\"Dependencies whose left side is not a superkey.\"\"\"\n    return [(lhs, rhs) for lhs, rhs in fds\n            if not set(rhs) <= set(lhs) and closure(lhs, fds) != set(schema)]\n\nschema = {\"student\", \"course\", \"instructor\"}\nfds = [((\"student\", \"course\"), (\"instructor\",)),\n       ((\"instructor\",), (\"course\",))]\n\nprint(\"candidate keys:\", candidate_keys(schema, fds))\nprint(\"BCNF violations:\", bcnf_violations(schema, fds))\n\n# the trades example from above, before decomposition\nwide = {\"trade_id\", \"trader\", \"desk\", \"desk_head\", \"sym\", \"qty\"}\nwide_fds = [((\"trade_id\",), (\"trader\", \"sym\", \"qty\")),\n            ((\"trader\",), (\"desk\",)),\n            ((\"desk\",), (\"desk_head\",))]\nprint(\"trades_wide keys:\", candidate_keys(wide, wide_fds))\nfor lhs, rhs in bcnf_violations(wide, wide_fds):\n    print(f\"  {lhs} -> {rhs}: left side is not a key\")",
            "label": "finding keys and BCNF violations from functional dependencies",
            "output": "candidate keys: [('course', 'student'), ('instructor', 'student')]\nBCNF violations: [(('instructor',), ('course',))]\ntrades_wide keys: [('trade_id',)]\n  ('trader',) -> ('desk',): left side is not a key\n  ('desk',) -> ('desk_head',): left side is not a key",
            "isError": false
          },
          {
            "type": "p",
            "html": "Decomposing into <code>(instructor, course)</code> and <code>(student, instructor)</code> reaches BCNF, but the dependency <code>(student, course) &rarr; instructor</code> can no longer be enforced within one table: nothing stops a student being enrolled with two instructors of the same course. That is the known trade-off &mdash; BCNF decomposition is always lossless, but not always dependency-preserving, whereas 3NF always can be both."
          },
          {
            "type": "caveat",
            "text": "Higher forms exist (4NF removes multi-valued dependencies, 5NF join dependencies) but rarely come up outside a theory exam. In practice, reaching 3NF or BCNF and thinking clearly about any exceptions covers almost all real schemas."
          }
        ]
      },
      {
        "title": "Denormalization and read-heavy systems",
        "body": [
          {
            "type": "p",
            "html": "Normalized schemas optimise for correct writes. Read-heavy systems often pay for that with joins and aggregations on every request, and denormalize deliberately:"
          },
          {
            "type": "table",
            "head": [
              "Technique",
              "Example",
              "Kept correct by"
            ],
            "rows": [
              [
                "Duplicate a column",
                "Store <code>desk</code> on each trade row",
                "Application code, triggers, or accepting it as a historical snapshot"
              ],
              [
                "Precomputed aggregate",
                "A <code>positions</code> table updated on every fill instead of summing fills",
                "Updating it in the same transaction as the fill"
              ],
              [
                "Materialized view",
                "Daily P&amp;L per desk",
                "<code>REFRESH MATERIALIZED VIEW</code> (periodic) or incremental maintenance"
              ],
              [
                "Document / wide row",
                "Store an order with its fills as one JSON document",
                "Writing the whole document together"
              ],
              [
                "Separate read model (CQRS)",
                "Event stream feeds a search index or cache",
                "Asynchronous consumers; eventually consistent"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE fills(id INTEGER PRIMARY KEY, account INT, sym TEXT, qty INT);\n    CREATE TABLE positions(account INT, sym TEXT, qty INT, PRIMARY KEY (account, sym));\n    CREATE TRIGGER keep_positions AFTER INSERT ON fills BEGIN\n        INSERT INTO positions VALUES (NEW.account, NEW.sym, NEW.qty)\n        ON CONFLICT (account, sym) DO UPDATE SET qty = qty + NEW.qty;\n    END;\n\"\"\")\ndb.executemany(\"INSERT INTO fills(account, sym, qty) VALUES (?, ?, ?)\",\n               [(i % 100, f\"S{i % 40}\", (i % 7) * 10 - 20) for i in range(50_000)])\n\ndef steps(sql):\n    n = 0\n    def tick():\n        nonlocal n\n        n += 1\n    db.set_progress_handler(tick, 1)\n    rows = db.execute(sql).fetchall()\n    db.set_progress_handler(None, 0)\n    return rows, n\n\na, n1 = steps(\"SELECT sum(qty) FROM fills WHERE account = 7 AND sym = 'S7'\")\nb, n2 = steps(\"SELECT qty FROM positions WHERE account = 7 AND sym = 'S7'\")\nprint(f\"sum the fills:     {a[0][0]:>5}  ({n1:,} VM steps)\")\nprint(f\"read the position: {b[0][0]:>5}  ({n2:,} VM steps)\")",
            "label": "a position maintained on write vs. summed on read",
            "output": "sum the fills:      2470  (151,514 VM steps)\nread the position:  2470  (12 VM steps)",
            "isError": false
          },
          {
            "type": "p",
            "html": "The denormalized read is a single seek. The cost moved to the write path: every fill now also updates a position row (and contends on it, if many fills hit one account and symbol). This is the right trade whenever reads vastly outnumber writes, or when the read has a latency budget and the write does not."
          },
          {
            "type": "note",
            "text": "Denormalize from a normalized design, not instead of one. Know which copy is the source of truth, how the others are kept in step, and what a reader sees while they are out of step."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Explain 1NF, 2NF and 3NF with an example of a violation of each.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<strong>1NF</strong>: every column holds a single atomic value and there are no repeating groups. Violation: an <code>orders</code> row with <code>items = 'AAPL:100,MSFT:50'</code>. Fix: an <code>order_items</code> table with one row per item."
          },
          {
            "type": "p",
            "html": "<strong>2NF</strong>: no non-key attribute depends on part of a composite key. Violation: <code>order_items(order_id, line_no, sym, qty, customer)</code> where <code>customer</code> depends only on <code>order_id</code>. Fix: move <code>customer</code> to <code>orders</code>."
          },
          {
            "type": "p",
            "html": "<strong>3NF</strong>: no non-key attribute depends on another non-key attribute (no transitive dependencies). Violation: <code>traders(trader, desk, desk_head)</code> where <code>desk_head</code> depends on <code>desk</code>. Fix: a <code>desks(desk, desk_head)</code> table."
          },
          {
            "type": "p",
            "html": "Each violation causes update, insert and delete anomalies; each fix stores the offending fact once."
          }
        ]
      },
      {
        "q": "What is the difference between 3NF and BCNF? Give a table that is in 3NF but not BCNF.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "BCNF requires that for every non-trivial functional dependency X &rarr; Y, X is a superkey. 3NF relaxes this: the dependency is also allowed if every attribute of Y is part of some candidate key (a <em>prime</em> attribute)."
          },
          {
            "type": "p",
            "html": "Example: <code>(student, course, instructor)</code> where each instructor teaches one course, and each student takes a course from one instructor. Dependencies: <code>(student, course) &rarr; instructor</code> and <code>instructor &rarr; course</code>. Candidate keys: <code>(student, course)</code> and <code>(student, instructor)</code>. <code>instructor &rarr; course</code> has a non-superkey on the left, but <code>course</code> is prime, so it is 3NF and not BCNF. The anomaly: the fact &ldquo;Dr. X teaches Databases&rdquo; is repeated for every student of Dr. X."
          },
          {
            "type": "p",
            "html": "Decomposing to <code>(instructor, course)</code> and <code>(student, instructor)</code> gives BCNF but loses the ability to enforce <code>(student, course) &rarr; instructor</code> in a single table. That trade-off, lossless but not dependency-preserving, is the point interviewers want you to make."
          }
        ]
      },
      {
        "q": "When would you denormalize, and how do you keep denormalized data consistent?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "When a read path is hot and latency-sensitive and the normalized form requires expensive joins or aggregations on every request &mdash; positions derived from millions of fills, a dashboard summing a day&rsquo;s trades, a product page assembled from ten tables. Also when data is naturally read together and rarely changes independently (an order with its line items as one document)."
          },
          {
            "type": "p",
            "html": "Keeping it consistent, from strongest to weakest: update the copy in the same transaction as the source (triggers or application code), so they can never disagree; maintain it from the change stream (CDC, outbox pattern) and accept a short lag; or rebuild it periodically (materialized view refresh, batch job) and accept staleness up to the interval. Always keep one copy as the source of truth, and be able to rebuild the others from it."
          }
        ]
      },
      {
        "q": "Is storing a JSON array of tags in one column a violation of 1NF? When is it acceptable?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "By the textbook definition, yes: the column holds a collection, not an atomic value. The practical question is what you do with it. If the database treats the array as an opaque value that is always read and written whole, the anomalies 1NF guards against do not arise, and one column is simpler and faster than a child table. If you query into it (&ldquo;all orders tagged <code>hedge</code>&rdquo;), update single elements, or need referential integrity for the elements, the child table wins: you get indexes, constraints and normal SQL."
          },
          {
            "type": "p",
            "html": "Modern engines blur the line. PostgreSQL <code>jsonb</code> with a GIN index, or native arrays with <code>@&gt;</code>, make containment queries on a JSON column indexable. So the defensible answer is: acceptable for data that is read as a unit and not a target of relational constraints; use a table when elements have identity, relationships or independent updates."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Codd — A Relational Model of Data for Large Shared Data Banks",
        "url": "https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf"
      },
      {
        "label": "Kent — A Simple Guide to Five Normal Forms in Relational Database Theory",
        "url": "https://www.bkent.net/Doc/simple5.htm"
      },
      {
        "label": "PostgreSQL: materialized views",
        "url": "https://www.postgresql.org/docs/current/rules-materializedviews.html"
      },
      {
        "label": "SQLite: UPSERT",
        "url": "https://www.sqlite.org/lang_upsert.html"
      }
    ]
  },
  {
    "id": "sql",
    "title": "SQL Fundamentals",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Joins, grouping, window functions, CTEs, subqueries, set operations and the NULL traps.",
    "intro": [
      "Interviews for data-heavy roles still include a live SQL exercise, and the mistakes people make are consistent: a <code>LEFT JOIN</code> silently turned into an inner join by a <code>WHERE</code> clause, a filter in <code>WHERE</code> that belonged in <code>HAVING</code>, a <code>NOT IN</code> that returns nothing because of a <code>NULL</code>, and not knowing window functions exist.",
      "Every example runs against the same two small tables: five traders (one with no desk, one who has never traded) and eight trades (one by a trader ID that does not exist). Those gaps are deliberate; they are what make joins and NULLs interesting."
    ],
    "sections": [
      {
        "title": "Joins",
        "body": [
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT t.id, tr.name, t.sym FROM trades t\n        JOIN traders tr ON tr.id = t.trader_id ORDER BY t.id\"\"\")\nshow(\"\"\"SELECT tr.name, count(t.id) AS n_trades FROM traders tr\n        LEFT JOIN trades t ON t.trader_id = tr.id GROUP BY tr.name ORDER BY tr.name\"\"\")\nshow(\"\"\"SELECT tr.name, t.id AS trade FROM traders tr\n        FULL JOIN trades t ON t.trader_id = tr.id WHERE tr.id IS NULL OR t.id IS NULL\"\"\")",
            "label": "inner, left and full outer joins",
            "output": "id  name  sym\n1   ann   UST10Y\n2   ann   UST2Y\n3   bob   AAPL\n4   bob   AAPL\n5   cat   MSFT\n6   cat   AAPL\n7   ann   UST10Y\n\nname  n_trades\nann   3\nbob   2\ncat   2\ndan   0\nkim   0\n\nname  trade\nkim   NULL\ndan   NULL\nNULL  8",
            "isError": false
          },
          {
            "type": "p",
            "html": "The inner join dropped trade 8 (no such trader). The left join kept every trader and counted zero for Kim and Dan. The full join, filtered to its unmatched rows, finds orphans on both sides at once &mdash; a standard data-quality check."
          },
          {
            "type": "table",
            "head": [
              "Join",
              "Returns"
            ],
            "rows": [
              [
                "<code>INNER JOIN</code>",
                "Only rows with a match on both sides"
              ],
              [
                "<code>LEFT JOIN</code>",
                "Every left row; right columns are NULL where there is no match"
              ],
              [
                "<code>RIGHT JOIN</code>",
                "Mirror of left; usually rewritten as a left join for readability"
              ],
              [
                "<code>FULL JOIN</code>",
                "Every row from both sides, matched where possible"
              ],
              [
                "<code>CROSS JOIN</code>",
                "Every combination: rows(A) &times; rows(B)"
              ],
              [
                "Self join",
                "A table joined to itself, e.g. trader to manager"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The most common join bug: filtering the outer side in <code>WHERE</code>. The <code>WHERE</code> runs after the join, the unmatched rows have NULL there, and the condition discards them &mdash; turning the left join into an inner join. Put conditions on the optional side in the <code>ON</code> clause."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT tr.name, t.sym FROM traders tr\n        LEFT JOIN trades t ON t.trader_id = tr.id\n        WHERE t.day = '2026-09-30' ORDER BY tr.name\"\"\")\nshow(\"\"\"SELECT tr.name, t.sym FROM traders tr\n        LEFT JOIN trades t ON t.trader_id = tr.id AND t.day = '2026-09-30'\n        ORDER BY tr.name\"\"\")",
            "label": "the same filter in WHERE vs in ON",
            "output": "name  sym\nann   UST10Y\ncat   AAPL\n\nname  sym\nann   UST10Y\nbob   NULL\ncat   AAPL\ndan   NULL\nkim   NULL",
            "isError": false
          }
        ]
      },
      {
        "title": "Aggregation, GROUP BY and HAVING",
        "body": [
          {
            "type": "p",
            "html": "<code>GROUP BY</code> collapses rows into one per group; every selected column must either be grouped or aggregated. <code>WHERE</code> filters rows <em>before</em> grouping; <code>HAVING</code> filters groups <em>after</em>. The logical order of evaluation explains most confusion:"
          },
          {
            "type": "p",
            "html": "<code>FROM</code> / <code>JOIN</code> &rarr; <code>WHERE</code> &rarr; <code>GROUP BY</code> &rarr; <code>HAVING</code> &rarr; window functions &rarr; <code>SELECT</code> &rarr; <code>DISTINCT</code> &rarr; <code>ORDER BY</code> &rarr; <code>LIMIT</code>"
          },
          {
            "type": "p",
            "html": "That is why a column alias from <code>SELECT</code> cannot be used in <code>WHERE</code> (it does not exist yet), and why an aggregate cannot appear in <code>WHERE</code> (groups do not exist yet)."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT tr.desk, count(*) AS n, sum(t.qty * t.px) AS notional\n        FROM trades t JOIN traders tr ON tr.id = t.trader_id\n        WHERE t.qty > 0                          -- rows: only buys\n        GROUP BY tr.desk\n        HAVING sum(t.qty * t.px) > 10000         -- groups: only big desks\n        ORDER BY notional DESC\"\"\")",
            "label": "WHERE filters rows, HAVING filters groups",
            "output": "desk    n  notional\nequity  3  55400.0",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "SQLite and MySQL (without <code>ONLY_FULL_GROUP_BY</code>) accept a non-aggregated, non-grouped column in <code>SELECT</code> and return a value from an arbitrary row of the group. PostgreSQL and the SQL standard reject it. Do not rely on it."
          }
        ]
      },
      {
        "title": "Window functions",
        "body": [
          {
            "type": "p",
            "html": "A window function computes over a set of rows related to the current row <em>without</em> collapsing them. Syntax: <code>func() OVER (PARTITION BY ... ORDER BY ... frame)</code>. <code>PARTITION BY</code> is like <code>GROUP BY</code> but keeps the rows; <code>ORDER BY</code> defines the order within the partition, and for aggregates it makes them running totals."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT trader_id AS tid, day, sym, qty,\n               sum(qty) OVER (PARTITION BY trader_id ORDER BY day, id) AS running_qty,\n               row_number() OVER (PARTITION BY trader_id ORDER BY day, id) AS nth,\n               lag(sym) OVER (PARTITION BY trader_id ORDER BY day, id) AS prev_sym\n        FROM trades WHERE trader_id IN (2, 3) ORDER BY trader_id, day, id\"\"\")",
            "label": "running totals, numbering, and the previous row",
            "output": "tid  day         sym     qty  running_qty  nth  prev_sym\n2    2026-09-28  UST10Y  5    5            1    NULL\n2    2026-09-28  UST2Y   8    13           2    UST10Y\n2    2026-09-30  UST10Y  3    16           3    UST2Y\n3    2026-09-28  AAPL    100  100          1    NULL\n3    2026-09-29  AAPL    -40  60           2    AAPL",
            "isError": false
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT * FROM (\n          SELECT tr.desk, tr.name, sum(abs(t.qty) * t.px) AS notional,\n                 rank() OVER (PARTITION BY tr.desk ORDER BY sum(abs(t.qty) * t.px) DESC) AS rk\n          FROM trades t JOIN traders tr ON tr.id = t.trader_id\n          GROUP BY tr.desk, tr.name)\n        WHERE rk = 1\"\"\")",
            "label": "top N per group: the most common window-function question",
            "output": "desk    name  notional  rk\nequity  cat   32700.0   1\nrates   ann   1581.4    1",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Function",
              "Returns"
            ],
            "rows": [
              [
                "<code>row_number()</code>",
                "1, 2, 3, &hellip; with no ties"
              ],
              [
                "<code>rank()</code>",
                "Ties share a rank, then a gap: 1, 1, 3"
              ],
              [
                "<code>dense_rank()</code>",
                "Ties share a rank, no gap: 1, 1, 2"
              ],
              [
                "<code>lag(x, n)</code> / <code>lead(x, n)</code>",
                "Value n rows before / after"
              ],
              [
                "<code>first_value</code> / <code>last_value</code>",
                "Value at the edge of the frame (mind the default frame)"
              ],
              [
                "<code>sum</code>/<code>avg</code>/<code>count</code> <code>OVER</code>",
                "Running or moving aggregates"
              ],
              [
                "<code>ntile(n)</code>",
                "Bucket number, for quartiles and percentiles"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The frame clause controls which rows an aggregate sees: <code>ROWS BETWEEN 4 PRECEDING AND CURRENT ROW</code> is a five-row moving window. With an <code>ORDER BY</code> and no frame, the default is <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code>, which includes all rows <em>tied</em> with the current one &mdash; a classic source of surprising running totals, and why <code>last_value</code> seems to return the current row."
          }
        ]
      },
      {
        "title": "CTEs and subqueries",
        "body": [
          {
            "type": "p",
            "html": "A <strong>common table expression</strong> (<code>WITH name AS (...)</code>) names a subquery so the main query reads top to bottom. A <strong>recursive CTE</strong> can walk hierarchies and generate series, which plain SQL otherwise cannot."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"WITH RECURSIVE chain(id, name, depth, path) AS (\n            SELECT id, name, 0, name FROM traders WHERE manager_id IS NULL\n            UNION ALL\n            SELECT t.id, t.name, c.depth + 1, c.path || ' > ' || t.name\n            FROM traders t JOIN chain c ON t.manager_id = c.id\n        )\n        SELECT name, depth, path FROM chain ORDER BY path\"\"\")",
            "label": "walking the management hierarchy with a recursive CTE",
            "output": "name  depth  path\nkim   0      kim\nann   1      kim > ann\nbob   1      kim > bob\ncat   2      kim > bob > cat\ndan   2      kim > bob > dan",
            "isError": false
          },
          {
            "type": "p",
            "html": "Subqueries come in three shapes. A <strong>scalar</strong> subquery returns one value (<code>WHERE px &gt; (SELECT avg(px) FROM trades)</code>). A <strong>table</strong> subquery appears in <code>FROM</code> as a derived table. A <strong>correlated</strong> subquery refers to the outer row and conceptually runs once per row &mdash; the query-execution page shows how expensive that can be when the planner does not rewrite it."
          },
          {
            "type": "caveat",
            "text": "Whether a CTE is inlined into the main query or computed once and stored varies. PostgreSQL before 12 always materialised CTEs, which made them an optimisation fence; since 12 it inlines side-effect-free CTEs referenced once, and <code>AS MATERIALIZED</code> / <code>NOT MATERIALIZED</code> let you choose."
          }
        ]
      },
      {
        "title": "EXISTS, IN, UNION and set operations",
        "body": [
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT name FROM traders tr\n        WHERE EXISTS (SELECT 1 FROM trades t WHERE t.trader_id = tr.id AND t.sym = 'AAPL')\"\"\")\nshow(\"\"\"SELECT sym FROM trades WHERE day = '2026-09-28'\n        UNION\n        SELECT sym FROM trades WHERE day = '2026-09-30'\"\"\")\nshow(\"\"\"SELECT count(*) AS union_all_rows FROM (\n          SELECT sym FROM trades WHERE day = '2026-09-28'\n          UNION ALL\n          SELECT sym FROM trades WHERE day = '2026-09-30')\"\"\")\nshow(\"\"\"SELECT sym FROM trades WHERE day = '2026-09-28'\n        INTERSECT\n        SELECT sym FROM trades WHERE day = '2026-09-30'\"\"\")",
            "label": "EXISTS, UNION vs UNION ALL, INTERSECT",
            "output": "name\nbob\ncat\n\nsym\nAAPL\nNVDA\nUST10Y\nUST2Y\n\nunion_all_rows\n6\n\nsym\nAAPL\nUST10Y",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>EXISTS</code> asks only whether a matching row exists, so the engine can stop at the first one; it is the natural way to write a semi-join. <code>UNION</code> removes duplicates, which requires a sort or hash over the whole result; <code>UNION ALL</code> just concatenates. Use <code>UNION ALL</code> unless you actually need de-duplication. <code>INTERSECT</code> and <code>EXCEPT</code> are the set intersection and difference."
          }
        ]
      },
      {
        "title": "NULL semantics",
        "body": [
          {
            "type": "p",
            "html": "<code>NULL</code> means &ldquo;unknown&rdquo;, and SQL uses <strong>three-valued logic</strong>: a comparison involving NULL is neither true nor false but <code>UNKNOWN</code>, and <code>WHERE</code> keeps only rows that are true."
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT NULL = NULL AS eq, NULL <> 1 AS ne, NULL IS NULL AS is_null,\n               NULL AND 0 AS and_false, NULL OR 1 AS or_true, 1 + NULL AS plus\"\"\")\nshow(\"\"\"SELECT count(*) AS all_rows, count(desk) AS with_desk,\n               count(DISTINCT desk) AS desks FROM traders\"\"\")\nshow(\"\"\"SELECT desk, count(*) AS n FROM traders GROUP BY desk ORDER BY desk\"\"\")",
            "label": "NULL in comparisons, counts and groups",
            "output": "eq    ne    is_null  and_false  or_true  plus\nNULL  NULL  1        0          1        NULL\n\nall_rows  with_desk  desks\n5         4          2\n\ndesk    n\nNULL    1\nequity  2\nrates   2",
            "isError": false
          },
          {
            "type": "p",
            "html": "<code>NULL = NULL</code> is unknown, not true, so you test with <code>IS NULL</code>. <code>count(column)</code> skips NULLs while <code>count(*)</code> counts rows; <code>sum</code> and <code>avg</code> ignore NULLs too. <code>GROUP BY</code> is the exception that treats all NULLs as one group. And <code>FALSE AND NULL</code> is false, <code>TRUE OR NULL</code> is true: unknown only propagates when it could change the answer."
          },
          {
            "type": "p",
            "html": "The trap that catches everyone is <code>NOT IN</code> with a subquery that can return NULL:"
          },
          {
            "type": "code",
            "src": "import sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE traders(id INT PRIMARY KEY, name TEXT, desk TEXT, manager_id INT);\n    INSERT INTO traders VALUES\n        (1, 'kim', 'rates', NULL), (2, 'ann', 'rates', 1), (3, 'bob', 'equity', 1),\n        (4, 'cat', 'equity', 3), (5, 'dan', NULL, 3);\n    CREATE TABLE trades(id INT PRIMARY KEY, trader_id INT, sym TEXT, qty INT, px REAL, day TEXT);\n    INSERT INTO trades VALUES\n        (1, 2, 'UST10Y', 5, 98.5, '2026-09-28'), (2, 2, 'UST2Y', 8, 99.1, '2026-09-28'),\n        (3, 3, 'AAPL', 100, 227.0, '2026-09-28'), (4, 3, 'AAPL', -40, 229.5, '2026-09-29'),\n        (5, 4, 'MSFT', 60, 431.0, '2026-09-29'), (6, 4, 'AAPL', 30, 228.0, '2026-09-30'),\n        (7, 2, 'UST10Y', 3, 98.7, '2026-09-30'), (8, 9, 'NVDA', 10, 121.0, '2026-09-30');\n\"\"\")\n\ndef show(sql):\n    cur = db.execute(sql)\n    cols = [c[0] for c in cur.description]\n    rows = [[(\"NULL\" if v is None else str(v)) for v in r] for r in cur.fetchall()]\n    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]\n    print(\"  \".join(c.ljust(w) for c, w in zip(cols, widths)).rstrip())\n    for r in rows:\n        print(\"  \".join(v.ljust(w) for v, w in zip(r, widths)).rstrip())\n    print()\n\nshow(\"\"\"SELECT count(*) AS not_in_without_nulls FROM trades\n        WHERE trader_id NOT IN (SELECT manager_id FROM traders WHERE manager_id IS NOT NULL)\"\"\")\nshow(\"\"\"SELECT count(*) AS not_in FROM trades     -- kim's manager_id is NULL\n        WHERE trader_id NOT IN (SELECT manager_id FROM traders)\"\"\")\nshow(\"\"\"SELECT count(*) AS not_exists FROM trades t\n        WHERE NOT EXISTS (SELECT 1 FROM traders m WHERE m.manager_id = t.trader_id)\"\"\")",
            "label": "NOT IN returns nothing once the list contains a NULL",
            "output": "not_in_without_nulls\n6\n\nnot_in\n0\n\nnot_exists\n6",
            "isError": false
          },
          {
            "type": "p",
            "html": "The managers are traders 1 and 3, and six trades were made by someone else. But Kim has no manager, so the subquery returns <code>(1, 1, 3, 3, NULL)</code>, and <code>x NOT IN (1, 3, NULL)</code> means <code>x &lt;&gt; 1 AND x &lt;&gt; 3 AND x &lt;&gt; NULL</code>. The last term is unknown for every <code>x</code>, so the whole condition can never be true and the query returns zero rows. <code>NOT EXISTS</code> does not have the problem and is what you should write."
          },
          {
            "type": "note",
            "text": "Prefer <code>NOT EXISTS</code> to <code>NOT IN (subquery)</code>, <code>IS [NOT] DISTINCT FROM</code> for NULL-safe comparison, and <code>coalesce(x, default)</code> when a NULL should behave like a value."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Write a query for each trader&rsquo;s largest trade by notional, including ties. Then explain how you would do it without window functions.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "With a window function, rank within each trader and keep rank 1 (<code>rank</code> keeps ties; <code>row_number</code> would pick one arbitrarily):"
          },
          {
            "type": "p",
            "html": "<code>SELECT * FROM (<br>&nbsp;&nbsp;SELECT t.*, rank() OVER (PARTITION BY trader_id ORDER BY abs(qty) * px DESC) AS rk<br>&nbsp;&nbsp;FROM trades t) x<br>WHERE rk = 1;</code>"
          },
          {
            "type": "p",
            "html": "Without window functions, join to the per-trader maximum:"
          },
          {
            "type": "p",
            "html": "<code>SELECT t.* FROM trades t<br>JOIN (SELECT trader_id, max(abs(qty) * px) AS m FROM trades GROUP BY trader_id) g<br>&nbsp;&nbsp;ON g.trader_id = t.trader_id AND abs(t.qty) * t.px = g.m;</code>"
          },
          {
            "type": "p",
            "html": "or with a correlated <code>NOT EXISTS</code> (&ldquo;no trade by the same trader is larger&rdquo;). The window version reads the table once; the join version reads it twice. The PostgreSQL-specific <code>DISTINCT ON (trader_id) ... ORDER BY trader_id, notional DESC</code> is the shortest but does not return ties."
          }
        ]
      },
      {
        "q": "Why does <code>SELECT * FROM a WHERE id NOT IN (SELECT a_id FROM b)</code> sometimes return no rows at all?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Because <code>b.a_id</code> contains at least one NULL. <code>id NOT IN (1, 2, NULL)</code> expands to <code>id &lt;&gt; 1 AND id &lt;&gt; 2 AND id &lt;&gt; NULL</code>; the last comparison is UNKNOWN for every row, so the conjunction is never TRUE, and <code>WHERE</code> discards everything."
          },
          {
            "type": "p",
            "html": "Fix with <code>NOT EXISTS (SELECT 1 FROM b WHERE b.a_id = a.id)</code>, which is unaffected by NULLs and is also what optimizers turn into an efficient anti-join, or with a <code>LEFT JOIN b ... WHERE b.a_id IS NULL</code>. Adding <code>WHERE a_id IS NOT NULL</code> inside the subquery also works but is easy to forget."
          }
        ]
      },
      {
        "q": "What is the difference between WHERE and HAVING, and between UNION and UNION ALL? Which is faster and why?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>WHERE</code> filters individual rows before grouping and cannot use aggregates. <code>HAVING</code> filters groups after aggregation. A condition that does not involve an aggregate should go in <code>WHERE</code>, so rows are discarded before the grouping work (most optimizers move it there anyway)."
          },
          {
            "type": "p",
            "html": "<code>UNION</code> returns distinct rows, which needs a sort or hash over the combined result. <code>UNION ALL</code> concatenates and can stream rows without buffering. <code>UNION ALL</code> is faster and should be the default; use <code>UNION</code> only when duplicates are possible and must be removed."
          }
        ]
      },
      {
        "q": "Compute a 3-day moving average of daily traded notional per symbol, and explain the frame you chose.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "First aggregate to one row per symbol per day, then apply a window over those rows:"
          },
          {
            "type": "p",
            "html": "<code>WITH daily AS (<br>&nbsp;&nbsp;SELECT sym, day, sum(abs(qty) * px) AS notional FROM trades GROUP BY sym, day)<br>SELECT sym, day, notional,<br>&nbsp;&nbsp;avg(notional) OVER (PARTITION BY sym ORDER BY day<br>&nbsp;&nbsp;&nbsp;&nbsp;ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma3<br>FROM daily;</code>"
          },
          {
            "type": "p",
            "html": "<code>ROWS BETWEEN 2 PRECEDING AND CURRENT ROW</code> averages the current row and the two before it. Two subtleties: the first two days average fewer than three values (filter them out or use <code>count(*) OVER (...) = 3</code> if a full window is required); and <code>ROWS</code> counts rows, so days with no trading are skipped rather than counted as zero. For calendar-correct windows either generate a complete date series (a recursive CTE) and left join to it, or use a <code>RANGE</code> frame over a date or day-number column with an interval offset where the engine supports it."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "SQLite: SELECT",
        "url": "https://www.sqlite.org/lang_select.html"
      },
      {
        "label": "SQLite: window functions",
        "url": "https://www.sqlite.org/windowfunctions.html"
      },
      {
        "label": "SQLite: WITH clause (common table expressions)",
        "url": "https://www.sqlite.org/lang_with.html"
      },
      {
        "label": "PostgreSQL: window function tutorial",
        "url": "https://www.postgresql.org/docs/current/tutorial-window.html"
      },
      {
        "label": "Modern SQL — what's new in SQL",
        "url": "https://modern-sql.com/"
      }
    ]
  },
  {
    "id": "columnar",
    "title": "Columnar Databases and OLAP",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Row vs column storage, compression, zone maps, vectorized execution, and why ClickHouse is fast.",
    "intro": [
      "A row store keeps each row&rsquo;s values together; a column store keeps each column&rsquo;s values together. That single layout decision changes almost everything downstream: how much data a query reads, how well it compresses, how the CPU processes it, and which workloads the system is good at.",
      "Trading firms live on both sides of this line: an OLTP store for orders and positions, and a columnar store (ClickHouse, kdb+, DuckDB, Parquet on object storage) for tick data and research. The examples use 200,000 synthetic trades stored both ways."
    ],
    "sections": [
      {
        "title": "Row vs column storage",
        "body": [
          {
            "type": "p",
            "html": "Most analytical queries touch a few columns of many rows: <em>average price per symbol over a day</em> reads two columns out of dozens. A row store must read every page containing those rows, and so reads every column. A column store reads only the two columns asked for."
          },
          {
            "type": "code",
            "src": "import random, struct, zlib\n\nrandom.seed(4)\nN = 200_000\nSYMS = [\"AAPL\", \"MSFT\", \"NVDA\", \"AMZN\", \"GOOG\", \"META\", \"TSLA\", \"JPM\"]\nts = list(range(1_700_000_000_000, 1_700_000_000_000 + N * 5, 5))      # sorted, ms\nsym = [random.choice(SYMS) for _ in range(N)]\npx = [round(100 + random.gauss(0, 2), 2) for _ in range(N)]\nqty = [random.choice((100, 200, 300, 500, 1000)) for _ in range(N)]\nvenue = [random.choice((\"XNAS\", \"ARCX\", \"BATS\")) for _ in range(N)]\n\nrow_fmt = \"<q4sdi4s\"                        # ts, sym, px, qty, venue per row\nrow_store = b\"\".join(struct.pack(row_fmt, t, s.encode(), p, q, v.encode())\n                     for t, s, p, q, v in zip(ts, sym, px, qty, venue))\ncol_store = {\n    \"ts\": struct.pack(f\"<{N}q\", *ts),\n    \"sym\": \"\".join(sym).encode(),           # fixed width 4\n    \"px\": struct.pack(f\"<{N}d\", *px),\n    \"qty\": struct.pack(f\"<{N}i\", *qty),\n    \"venue\": \"\".join(venue).encode(),\n}\nneeded = (\"sym\", \"px\")                      # SELECT sym, avg(px) ... GROUP BY sym\nrow_bytes = len(row_store)\ncol_bytes = sum(len(col_store[c]) for c in needed)\nprint(f\"row store reads    {row_bytes / 1e6:5.1f} MB (every column of every row)\")\nprint(f\"column store reads {col_bytes / 1e6:5.1f} MB (sym and px only)\")",
            "label": "bytes read for SELECT sym, avg(px) GROUP BY sym",
            "output": "row store reads      5.6 MB (every column of every row)\ncolumn store reads   2.4 MB (sym and px only)",
            "isError": false
          },
          {
            "type": "p",
            "html": "With only five columns the saving is about 2&times;. Real fact tables have fifty or two hundred columns and queries touch three to five, so the column store reads one or two orders of magnitude less before any compression."
          },
          {
            "type": "table",
            "head": [
              "",
              "Row store",
              "Column store"
            ],
            "rows": [
              [
                "Insert or update one row",
                "One page write",
                "One write per column, often into a buffer merged later"
              ],
              [
                "Fetch one whole row by key",
                "One page read",
                "One read per column"
              ],
              [
                "Scan a few columns of many rows",
                "Reads all columns",
                "Reads only those columns"
              ],
              [
                "Compression",
                "Modest (mixed types per page)",
                "Excellent (similar values together)"
              ],
              [
                "Typical use",
                "OLTP: orders, accounts, positions",
                "OLAP: ticks, events, logs, analytics"
              ]
            ]
          }
        ]
      },
      {
        "title": "Compression",
        "body": [
          {
            "type": "p",
            "html": "Values of one column share a type and usually a narrow range, and are often sorted or repetitive. That makes them far more compressible than rows, where a timestamp sits next to a string next to a float. Column stores also apply <em>lightweight encodings</em> that can be processed without fully decompressing:"
          },
          {
            "type": "table",
            "head": [
              "Encoding",
              "Stores",
              "Great for"
            ],
            "rows": [
              [
                "Dictionary",
                "Small integer codes plus a code &rarr; value table",
                "Low-cardinality strings: symbols, venues, sides"
              ],
              [
                "Run-length (RLE)",
                "(value, count) pairs",
                "Sorted or clustered columns"
              ],
              [
                "Delta",
                "Differences between consecutive values",
                "Timestamps, sequence numbers, sorted IDs"
              ],
              [
                "Delta-of-delta / Gorilla XOR",
                "Second differences / XOR of floats",
                "Regular time series; slowly moving prices"
              ],
              [
                "Bit packing / frame of reference",
                "Values minus a base, in as few bits as they need",
                "Small integer ranges"
              ]
            ]
          },
          {
            "type": "code",
            "src": "import random, struct, zlib\n\nrandom.seed(4)\nN = 200_000\nSYMS = [\"AAPL\", \"MSFT\", \"NVDA\", \"AMZN\", \"GOOG\", \"META\", \"TSLA\", \"JPM\"]\nts = list(range(1_700_000_000_000, 1_700_000_000_000 + N * 5, 5))      # sorted, ms\nsym = [random.choice(SYMS) for _ in range(N)]\npx = [round(100 + random.gauss(0, 2), 2) for _ in range(N)]\nqty = [random.choice((100, 200, 300, 500, 1000)) for _ in range(N)]\nvenue = [random.choice((\"XNAS\", \"ARCX\", \"BATS\")) for _ in range(N)]\n\nrow_store = b\"\".join(struct.pack(\"<q4sdi4s\", t, s.encode(), p, q, v.encode())\n                     for t, s, p, q, v in zip(ts, sym, px, qty, venue))\ncols = {\n    \"ts\": struct.pack(f\"<{N}q\", *ts),\n    \"sym\": \"\".join(sym).encode(),\n    \"px\": struct.pack(f\"<{N}d\", *px),\n    \"qty\": struct.pack(f\"<{N}i\", *qty),\n    \"venue\": \"\".join(venue).encode(),\n}\n# lightweight encodings first, then a general-purpose compressor on top\ncodes = {s: i for i, s in enumerate(SYMS)}\nencoded = {\n    \"ts\": struct.pack(f\"<{N}q\", ts[0], *(b - a for a, b in zip(ts, ts[1:]))),   # delta\n    \"sym\": bytes(codes[s] for s in sym),                                          # dictionary\n    \"px\": struct.pack(f\"<{N}i\", *(round(p * 100) for p in px)),                   # fixed point\n    \"qty\": bytes((100, 200, 300, 500, 1000).index(q) for q in qty),               # dictionary\n    \"venue\": bytes((\"XNAS\", \"ARCX\", \"BATS\").index(v) for v in venue),             # dictionary\n}\nraw = len(row_store)\nrows_z = len(zlib.compress(row_store, 6))\ncols_z = sum(len(zlib.compress(c, 6)) for c in cols.values())\nenc_z = sum(len(zlib.compress(c, 6)) for c in encoded.values())\nprint(f\"raw:                          {raw / 1e6:5.2f} MB\")\nprint(f\"row-major + zlib:             {rows_z / 1e6:5.2f} MB  ({raw / rows_z:4.1f}x)\")\nprint(f\"column-major + zlib:          {cols_z / 1e6:5.2f} MB  ({raw / cols_z:4.1f}x)\")\nprint(f\"columns, encoded, then zlib:  {enc_z / 1e6:5.2f} MB  ({raw / enc_z:4.1f}x)\")\nfor name, c in encoded.items():\n    print(f\"  {name:<6} {len(zlib.compress(c, 6)):>9,} bytes\")",
            "label": "the same data compressed as rows, as columns, and as encoded columns",
            "output": "raw:                           5.60 MB\nrow-major + zlib:              1.40 MB  ( 4.0x)\ncolumn-major + zlib:           1.01 MB  ( 5.6x)\ncolumns, encoded, then zlib:   0.56 MB  (10.1x)\n  ts         2,362 bytes\n  sym       86,384 bytes\n  px       352,089 bytes\n  qty       67,828 bytes\n  venue     47,669 bytes",
            "isError": false
          },
          {
            "type": "p",
            "html": "Encoded columns end up two and a half times smaller than compressed rows, and ten times smaller than the raw data. The timestamp column, delta-encoded, shrinks almost to nothing because every delta is the same. Prices are the hardest: real market data is noisier than this, which is exactly what specialised float encodings like Gorilla target."
          },
          {
            "type": "p",
            "html": "Compression in a column store is not just about disk. Smaller data means more of it fits in memory and cache, and scans are usually bound by memory bandwidth, so compressed scans are often <em>faster</em> than uncompressed ones. Many engines evaluate predicates directly on dictionary codes (<code>sym = 'AAPL'</code> becomes <code>code = 0</code>) without decoding."
          }
        ]
      },
      {
        "title": "Skipping data: sort keys and zone maps",
        "body": [
          {
            "type": "p",
            "html": "Column stores rarely have B-tree indexes. Instead they sort data by a chosen key and store the <strong>min and max</strong> of each column for each block of a few thousand rows (a <em>zone map</em>, <em>min/max index</em>, or in ClickHouse a <em>sparse primary index</em> with one mark per 8,192 rows). A query can then skip every block whose range cannot contain a match."
          },
          {
            "type": "code",
            "src": "import random, struct, zlib\n\nrandom.seed(4)\nN = 200_000\nSYMS = [\"AAPL\", \"MSFT\", \"NVDA\", \"AMZN\", \"GOOG\", \"META\", \"TSLA\", \"JPM\"]\nts = list(range(1_700_000_000_000, 1_700_000_000_000 + N * 5, 5))      # sorted, ms\nsym = [random.choice(SYMS) for _ in range(N)]\npx = [round(100 + random.gauss(0, 2), 2) for _ in range(N)]\nqty = [random.choice((100, 200, 300, 500, 1000)) for _ in range(N)]\nvenue = [random.choice((\"XNAS\", \"ARCX\", \"BATS\")) for _ in range(N)]\n\nBLOCK = 8192\nblocks = [(ts[i], ts[min(i + BLOCK, N) - 1]) for i in range(0, N, BLOCK)]\n\nlo, hi = ts[0] + 400_000, ts[0] + 460_000                # a one-minute window\nhit = [b for b in blocks if b[1] >= lo and b[0] <= hi]\nprint(f\"{len(blocks)} blocks; one-minute query reads {len(hit)} of them\")\n\n# the same query on a column the data is NOT sorted by\npblocks = [(min(px[i:i + BLOCK]), max(px[i:i + BLOCK])) for i in range(0, N, BLOCK)]\nhit = [b for b in pblocks if b[1] >= 100.00 and b[0] <= 100.05]\nprint(f\"price between 100.00 and 100.05 reads {len(hit)} of {len(pblocks)} blocks\")",
            "label": "min/max per block: great on the sort key, useless on a random column",
            "output": "25 blocks; one-minute query reads 3 of them\nprice between 100.00 and 100.05 reads 25 of 25 blocks",
            "isError": false
          },
          {
            "type": "p",
            "html": "Choosing the sort key is the most important schema decision in a column store, the equivalent of choosing the clustered index. For market data <code>(symbol, timestamp)</code> is typical: one symbol&rsquo;s ticks over a time range become one contiguous run of blocks."
          }
        ]
      },
      {
        "title": "Vectorized execution",
        "body": [
          {
            "type": "p",
            "html": "Reading less data only helps if the CPU can keep up with it. The row-at-a-time iterator model makes a virtual function call per operator per row, with a branch per value, and cannot use SIMD. <strong>Vectorized</strong> engines pass <em>batches</em> of values (typically 1,024 to 65,536) between operators, and each operator runs a tight loop over a plain array: the per-call overhead is paid once per batch, loops are branch-light and SIMD-friendly, and data stays in the CPU cache."
          },
          {
            "type": "code",
            "src": "import random, struct, zlib\n\nrandom.seed(4)\nN = 200_000\nSYMS = [\"AAPL\", \"MSFT\", \"NVDA\", \"AMZN\", \"GOOG\", \"META\", \"TSLA\", \"JPM\"]\nts = list(range(1_700_000_000_000, 1_700_000_000_000 + N * 5, 5))      # sorted, ms\nsym = [random.choice(SYMS) for _ in range(N)]\npx = [round(100 + random.gauss(0, 2), 2) for _ in range(N)]\nqty = [random.choice((100, 200, 300, 500, 1000)) for _ in range(N)]\nvenue = [random.choice((\"XNAS\", \"ARCX\", \"BATS\")) for _ in range(N)]\n\ncalls = 0\n\ndef scan_rows():                     # iterator model: one value per next()\n    global calls\n    for p in px:\n        calls += 1\n        yield p\n\ndef filter_rows(child):\n    global calls\n    for p in child:\n        calls += 1\n        if p > 100:\n            yield p\n\ntotal = 0.0\nfor p in filter_rows(scan_rows()):\n    total += p\nrow_calls = calls\n\ncalls, BATCH = 0, 4096\ndef scan_batches():                  # vectorized: one array per next()\n    global calls\n    for i in range(0, N, BATCH):\n        calls += 1\n        yield px[i:i + BATCH]\n\nvtotal = 0.0\nfor batch in scan_batches():\n    calls += 1                       # filter + sum over the whole batch\n    vtotal += sum(p for p in batch if p > 100)\n\nprint(f\"same answer: {abs(total - vtotal) < 1e-6}\")\nprint(f\"operator calls, row at a time: {row_calls:>9,}\")\nprint(f\"operator calls, 4,096 per batch: {calls:>7,}\")",
            "label": "operator invocations: per row vs per batch",
            "output": "same answer: True\noperator calls, row at a time:   400,000\noperator calls, 4,096 per batch:      98",
            "isError": false
          },
          {
            "type": "p",
            "html": "In Python the inner loop is still interpreted, so this shows only the change in structure. In a C++ engine the inner loop over a batch compiles to SIMD instructions processing 4&ndash;16 values per instruction, and the 400,000 function calls simply disappear. NumPy and pandas are fast for the same reason."
          },
          {
            "type": "caveat",
            "text": "The alternative to vectorization is compiling the whole query into one fused machine-code loop (HyPer, Umbra, Spark whole-stage codegen). Both approaches reach similar speeds; vectorization is easier to build and debug, which is why DuckDB, ClickHouse, Velox and Snowflake use it."
          }
        ]
      },
      {
        "title": "OLTP vs OLAP",
        "body": [
          {
            "type": "table",
            "head": [
              "",
              "OLTP",
              "OLAP"
            ],
            "rows": [
              [
                "Queries",
                "Many small reads and writes by key",
                "Few large scans and aggregations"
              ],
              [
                "Rows per query",
                "One to hundreds",
                "Millions to billions"
              ],
              [
                "Latency target",
                "Milliseconds or less, per request",
                "Seconds are fine for a report"
              ],
              [
                "Data freshness",
                "Current state",
                "History; often loaded in batches or streamed"
              ],
              [
                "Writes",
                "Frequent, concurrent, small, transactional",
                "Bulk appends; updates and deletes are rare and expensive"
              ],
              [
                "Storage",
                "Row store, B+ tree indexes",
                "Column store, sort keys, zone maps, heavy compression"
              ],
              [
                "Examples",
                "PostgreSQL, MySQL, Oracle, SQL Server",
                "ClickHouse, Snowflake, BigQuery, Redshift, DuckDB, kdb+"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Running analytics on the OLTP database is the classic mistake: a long scan competes for buffer pool and I/O with latency-sensitive transactions, and in an MVCC engine a long-running query holds back cleanup. The usual architecture streams changes out of the OLTP database (change data capture) into an analytical store. <em>HTAP</em> systems (TiDB with TiFlash, SingleStore, SQL Server columnstore indexes) keep both representations of the same data inside one product."
          }
        ]
      },
      {
        "title": "Why ClickHouse is fast for analytical workloads",
        "body": [
          {
            "type": "p",
            "html": "ClickHouse is a useful case study because its speed comes from combining every technique above and adding a few of its own:"
          },
          {
            "type": "p",
            "html": "<strong>Columnar storage with per-column codecs.</strong> LZ4 or ZSTD, layered on specialised codecs such as <code>Delta</code>, <code>DoubleDelta</code>, <code>Gorilla</code> and <code>T64</code> chosen per column.<br><strong>MergeTree tables.</strong> Inserts write immutable, sorted <em>parts</em>; background merges combine them, much like an LSM tree. Inserts never modify existing data, so they are cheap and do not block reads.<br><strong>A sparse primary index.</strong> One entry per 8,192-row granule, so the index for billions of rows fits in memory and a range on the sort key reads only the matching granules. Data-skipping indexes (min/max, set, Bloom filter) add zone maps on other columns.<br><strong>Vectorized, SIMD-heavy execution</strong> written in C++, with many specialised implementations of hash tables and aggregate functions chosen by key type.<br><strong>Parallelism everywhere.</strong> A query is split across all cores, and across shards in a cluster.<br><strong>Approximation when asked.</strong> <code>uniq</code> (HyperLogLog-style), <code>quantileTDigest</code> and sampling trade exactness for speed.<br><strong>What it gives up.</strong> No full ACID transactions across tables, updates and deletes are asynchronous &ldquo;mutations&rdquo; that rewrite parts, and point lookups are relatively slow. It is built for append-mostly data scanned in bulk, which is exactly what tick data is."
          },
          {
            "type": "note",
            "text": "Columnar stores are fast because they avoid work, not because they do the same work faster: they read fewer columns, fewer bytes per value, fewer blocks, and pay per-batch rather than per-row overhead."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why are column stores faster than row stores for analytical queries and slower for transactional ones?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Analytical queries read a few columns of many rows. A column store reads only those columns, they compress far better because similar values sit together (dictionary, RLE, delta encodings, then LZ4/ZSTD), sorted data and zone maps let it skip whole blocks, and vectorized operators process each column as a tight loop over an array. Together that is often 10&ndash;100&times; less I/O and far better CPU efficiency."
          },
          {
            "type": "p",
            "html": "Transactional work reads or writes whole rows by key. In a column store, inserting one row touches every column file, updating a value inside a compressed block means rewriting the block, and fetching one full row means one lookup per column. Column stores mitigate this by buffering inserts in a row-oriented delta store and merging later, but single-row latency is still worse than a B+ tree row store."
          }
        ]
      },
      {
        "q": "You store a year of tick data (20 billion rows) in ClickHouse. What ORDER BY key would you choose, and why?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "<code>ORDER BY (symbol, timestamp)</code>, typically with <code>PARTITION BY toDate(timestamp)</code> or by month. Almost every query restricts both symbol and a time range (&ldquo;AAPL trades between 09:30 and 09:35&rdquo;), and with this key those rows are contiguous: the sparse index finds the first matching granule for the symbol, then reads consecutive granules until the time range ends. Partitioning by date lets whole days be dropped or moved to cheaper storage cheaply."
          },
          {
            "type": "p",
            "html": "Why not timestamp first? Then a single-symbol query would find matching timestamps in every granule of the time range across all symbols and read far more data. Why low cardinality first in general? Because each key column only helps skipping while the preceding columns are equal; a leading column with few values produces long runs in which the next column is sorted."
          },
          {
            "type": "p",
            "html": "Complements: <code>LowCardinality(String)</code> for symbol and venue, <code>DoubleDelta</code> or <code>Delta</code> + ZSTD for timestamps, <code>Gorilla</code> for prices, and a projection or materialized view ordered differently (by venue, say) if another access pattern matters."
          }
        ]
      },
      {
        "q": "What is a zone map, and when is it useless?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A zone map stores summary statistics &mdash; at least min and max &mdash; of each column for each block of rows. A query predicate is checked against the summary first, and any block whose range cannot contain a match is skipped without being read or decompressed. It costs almost nothing to store and maintain."
          },
          {
            "type": "p",
            "html": "It is useless when the column&rsquo;s values are randomly distributed across blocks, because every block&rsquo;s min-max range then spans nearly the full domain and nothing can be skipped. It works on the sort key, on columns correlated with it (an auto-increment ID when sorted by time), and on data naturally clustered by insertion order. That is why the sort key choice matters so much, and why engines offer Bloom-filter or set indexes for high-cardinality columns that are not sorted."
          }
        ]
      },
      {
        "q": "Explain vectorized execution and why it matters more as storage gets faster.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "In the classic iterator model every operator produces one row per <code>next()</code> call. For a billion-row scan that is billions of virtual calls, each doing a tiny amount of work, with unpredictable branches and no opportunity for SIMD. Vectorized execution passes batches of a few thousand values per call. The call overhead is amortised over the batch, each operator is a tight loop over contiguous arrays that the compiler can turn into SIMD instructions, and batches are sized to stay in L1/L2 cache."
          },
          {
            "type": "p",
            "html": "It matters more as storage gets faster because the bottleneck moves. When data came from spinning disks at 200&nbsp;MB/s, any CPU could keep up. From NVMe at several GB/s per drive, or from memory at tens of GB/s, a row-at-a-time interpreter is the bottleneck; only a vectorized or compiled engine can process data at the rate it arrives."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "ClickHouse docs: MergeTree table engine",
        "url": "https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree"
      },
      {
        "label": "ClickHouse docs: why ClickHouse is so fast",
        "url": "https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast"
      },
      {
        "label": "Abadi et al. — The Design and Implementation of Modern Column-Oriented Database Systems",
        "url": "https://stratos.seas.harvard.edu/files/stratos/files/columnstoresfntdbs.pdf"
      },
      {
        "label": "Boncz et al. — MonetDB/X100: Hyper-Pipelining Query Execution",
        "url": "https://www.cidrdb.org/cidr2005/papers/P19.pdf"
      },
      {
        "label": "Pelkonen et al. — Gorilla: A Fast, Scalable, In-Memory Time Series Database",
        "url": "https://www.vldb.org/pvldb/vol8/p1816-teller.pdf"
      }
    ]
  },
  {
    "id": "caching",
    "title": "Caching Patterns",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Cache-aside, write-through and write-back, TTLs, stampedes, hot keys, and keeping a cache honest.",
    "intro": [
      "A cache puts a copy of data somewhere faster than its source &mdash; process memory, Redis, a CDN &mdash; so most reads never reach the database. The speed-up is easy. The hard parts are the ones interviewers ask about: when the copy disagrees with the source, what happens when a popular entry expires under load, and what to do when one key is hotter than any single machine.",
      "The Redis page covered eviction policies. This page is about the patterns that sit around any cache, and the failure modes each one has."
    ],
    "sections": [
      {
        "title": "Cache-aside, write-through, write-back",
        "body": [
          {
            "type": "table",
            "head": [
              "Pattern",
              "Read path",
              "Write path",
              "Consistency risk",
              "Used for"
            ],
            "rows": [
              [
                "<strong>Cache-aside</strong> (lazy loading)",
                "App checks cache; on miss reads DB and fills cache",
                "App writes DB, then deletes (or updates) the cache entry",
                "Races can leave stale entries until TTL",
                "The default for most web and service caches"
              ],
              [
                "<strong>Read-through</strong>",
                "Cache itself loads from DB on miss",
                "(paired with one of the below)",
                "As cache-aside, but centralised",
                "Caching libraries and proxies"
              ],
              [
                "<strong>Write-through</strong>",
                "Cache always populated",
                "Write cache and DB together, synchronously",
                "Low; writes are slower",
                "Read-heavy data that must be fresh"
              ],
              [
                "<strong>Write-back</strong> (write-behind)",
                "Cache always populated",
                "Write cache only; flush to DB later in batches",
                "Data loss if the cache dies before flushing",
                "Write-heavy counters, metrics; CPU caches; buffer pools"
              ],
              [
                "<strong>Write-around</strong>",
                "Cache-aside",
                "Write DB only; do not touch cache",
                "Next read of new data misses",
                "Data written once and rarely read soon after"
              ]
            ]
          },
          {
            "type": "code",
            "src": "class DB:\n    def __init__(self):\n        self.rows, self.writes = {}, 0\n    def put(self, k, v):\n        self.rows[k] = v\n        self.writes += 1\n\ndef write_through(updates):\n    db, cache = DB(), {}\n    for k, v in updates:\n        cache[k] = v\n        db.put(k, v)                       # every write reaches the DB now\n    return db, cache, {}\n\ndef write_back(updates, flush_every=50):\n    db, cache, dirty = DB(), {}, {}\n    for i, (k, v) in enumerate(updates, 1):\n        cache[k] = v\n        dirty[k] = v                        # only the latest value per key\n        if i % flush_every == 0:\n            for dk, dv in dirty.items():\n                db.put(dk, dv)\n            dirty.clear()\n    return db, cache, dirty\n\n# 230 position updates spread over 5 symbols\nupdates = [(f\"S{i % 5}\", i) for i in range(230)]\nfor name, f in ((\"write-through\", write_through), (\"write-back\", write_back)):\n    db, cache, dirty = f(updates)\n    print(f\"{name:<13} DB writes: {db.writes:>3}   lost if the cache dies now: {sorted(dirty)}\")",
            "label": "write-through vs write-back: DB load against exposure to loss",
            "output": "write-through DB writes: 230   lost if the cache dies now: []\nwrite-back    DB writes:  20   lost if the cache dies now: ['S0', 'S1', 'S2', 'S3', 'S4']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Write-back coalesced 230 updates into 20 database writes, because only the latest value per key is flushed. The price is the list on the right: updates acknowledged to the caller that exist only in cache memory."
          }
        ]
      },
      {
        "title": "Cache invalidation and the stale-read race",
        "body": [
          {
            "type": "p",
            "html": "The standard cache-aside write is: update the database, then <strong>delete</strong> the cache entry (so the next read reloads it). Deleting is preferred to updating the cache because two concurrent writers updating the cache can apply their values in the opposite order from the database. But even delete-after-write has a race with a concurrent reader that missed:"
          },
          {
            "type": "code",
            "src": "db = {\"px:AAPL\": 227.0}\ncache = {}\nlog = []\n\ndef step(who, what):\n    log.append(f\"{who:<7} {what}\")\n\n# reader misses and reads the DB ...\nvalue = db[\"px:AAPL\"];                 step(\"reader\", f\"miss, reads DB -> {value}\")\n# ... writer updates the DB and invalidates the (empty) cache ...\ndb[\"px:AAPL\"] = 229.5;                 step(\"writer\", \"writes DB -> 229.5\")\ncache.pop(\"px:AAPL\", None);            step(\"writer\", \"deletes cache entry\")\n# ... reader, delayed (GC pause, slow network), now fills the cache\ncache[\"px:AAPL\"] = value;              step(\"reader\", f\"sets cache -> {value}\")\n\nprint(\"\\n\".join(log))\nprint(f\"DB says {db['px:AAPL']}, cache says {cache['px:AAPL']} (stale until TTL)\")",
            "label": "a slow reader repopulates the cache with an old value",
            "output": "reader  miss, reads DB -> 227.0\nwriter  writes DB -> 229.5\nwriter  deletes cache entry\nreader  sets cache -> 227.0\nDB says 229.5, cache says 227.0 (stale until TTL)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Mitigations, in increasing strength:"
          },
          {
            "type": "p",
            "html": "<strong>TTL on every entry</strong>, so any staleness is bounded. Always do this; it is the safety net for every bug you have not found.<br><strong>Delayed double delete</strong>: delete, then delete again a short time later to catch a racing reader. Cheap, heuristic.<br><strong>Versioned or conditional sets</strong>: store a version (row version, LSN, timestamp) with the value and only set if the cached version is older (a Lua script in Redis). A reader carrying an old version cannot overwrite a newer one.<br><strong>Lease / invalidation tokens</strong> (Facebook&rsquo;s memcache): a miss hands out a lease token; a delete invalidates outstanding leases, so the slow reader&rsquo;s set is rejected.<br><strong>Invalidate from the change stream</strong>: a consumer of the database&rsquo;s CDC log deletes cache keys, so invalidation cannot be skipped by a code path that forgets."
          },
          {
            "type": "note",
            "text": "&ldquo;There are only two hard things in computer science: cache invalidation and naming things.&rdquo; If a stale value is unacceptable &mdash; balances, positions, risk limits &mdash; do not serve it from a cache that is invalidated asynchronously."
          }
        ]
      },
      {
        "title": "TTL and expiry",
        "body": [
          {
            "type": "p",
            "html": "A TTL bounds staleness and lets unused entries fall out. Choosing it is a trade between freshness (short) and hit ratio and database load (long). Two refinements matter at scale:"
          },
          {
            "type": "p",
            "html": "<strong>Jitter.</strong> If many keys are written at the same moment with the same TTL &mdash; a deploy warming the cache, a nightly batch &mdash; they all expire at the same moment too, and the database takes the whole reload at once. Add randomness to every TTL:"
          },
          {
            "type": "code",
            "src": "import random\nfrom collections import Counter\n\nrandom.seed(8)\nKEYS, TTL = 10_000, 300                         # all cached at t=0 by a warm-up job\n\nfixed = Counter(TTL for _ in range(KEYS))\njittered = Counter(TTL + random.randint(-30, 30) for _ in range(KEYS))\n\nprint(f\"fixed TTL:    worst second has {max(fixed.values()):>6,} expiries\")\nprint(f\"TTL +/- 10%:  worst second has {max(jittered.values()):>6,} expiries\")",
            "label": "synchronised expiry vs jittered TTLs",
            "output": "fixed TTL:    worst second has 10,000 expiries\nTTL +/- 10%:  worst second has    195 expiries",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Refresh ahead.</strong> For hot keys, refresh the value in the background shortly before it expires, so readers never see a miss. Probabilistic early expiration (the XFetch algorithm) does this without coordination: each reader, with a probability that rises as expiry approaches, decides to recompute early, so one request refreshes the value while the rest keep reading the old one."
          }
        ]
      },
      {
        "title": "Cache stampede",
        "body": [
          {
            "type": "p",
            "html": "A <strong>stampede</strong> (dog-pile, thundering herd) happens when a popular key expires or is evicted and every concurrent request misses at once. Each one runs the same expensive query, and a database that was comfortably serving the cache&rsquo;s misses is suddenly asked for the same row a thousand times."
          },
          {
            "type": "p",
            "html": "The fix is <strong>request coalescing</strong> (single-flight): the first request to miss takes a per-key lock and loads the value; everyone else waits for that result instead of querying the database themselves. Across processes the lock is a short-lived Redis key set with <code>SET key token NX PX 5000</code>; within a process it is a mutex or a shared future."
          },
          {
            "type": "code",
            "src": "import threading, time\n\ndef run(coalesce, clients=50):\n    db_queries = 0\n    cache = {}\n    counter_lock = threading.Lock()\n    inflight = {}                             # key -> Event for the one loader\n    inflight_lock = threading.Lock()\n    start = threading.Barrier(clients)\n\n    def load(key):\n        nonlocal db_queries\n        with counter_lock:\n            db_queries += 1\n        time.sleep(0.2)                       # an expensive query\n        return f\"value of {key}\"\n\n    def get(key):\n        start.wait()                          # everyone misses at the same instant\n        if key in cache:\n            return cache[key]\n        if not coalesce:\n            cache[key] = load(key)\n            return cache[key]\n        with inflight_lock:\n            event = inflight.get(key)\n            leader = event is None\n            if leader:\n                event = inflight[key] = threading.Event()\n        if leader:\n            cache[key] = load(key)\n            event.set()\n        else:\n            event.wait()\n        return cache[key]\n\n    threads = [threading.Thread(target=get, args=(\"hot\",)) for _ in range(clients)]\n    for t in threads: t.start()\n    for t in threads: t.join()\n    return db_queries\n\nprint(\"50 concurrent misses, no coalescing:  \", run(coalesce=False), \"DB queries\")\nprint(\"50 concurrent misses, single-flight:  \", run(coalesce=True), \"DB query\")",
            "label": "a hot key expires under 50 concurrent requests",
            "output": "50 concurrent misses, no coalescing:   50 DB queries\n50 concurrent misses, single-flight:   1 DB query",
            "isError": false
          },
          {
            "type": "p",
            "html": "Other defences: serve the stale value while one request refreshes it (<em>stale-while-revalidate</em>), refresh hot keys ahead of expiry, and never let an empty or failing backend turn into a cache of errors &mdash; cache negative results briefly, but not exceptions."
          },
          {
            "type": "caveat",
            "text": "A distributed lock for coalescing must have a timeout, and the loader must not assume it still holds the lock when it finishes: if it paused past the timeout, another loader may have started. The worst outcome is a duplicate load, which is acceptable; do not use the same lock to protect correctness."
          }
        ]
      },
      {
        "title": "Hot keys",
        "body": [
          {
            "type": "p",
            "html": "Sharding a cache spreads keys, not load. A single key that receives a large fraction of all traffic &mdash; the current price of the most traded instrument, a global configuration blob, a celebrity profile &mdash; is served by one shard, whose CPU or network link saturates while the rest of the cluster idles."
          },
          {
            "type": "table",
            "head": [
              "Technique",
              "How",
              "Cost"
            ],
            "rows": [
              [
                "Local (L1) cache",
                "Keep hot keys in each application process for a short time (100&nbsp;ms&ndash;seconds) in front of the shared cache",
                "Staleness up to the local TTL; memory per process"
              ],
              [
                "Key replication",
                "Store copies as <code>key#0</code> &hellip; <code>key#N</code> on different shards; readers pick one at random",
                "Writes and invalidations must touch every copy"
              ],
              [
                "Read replicas",
                "Add replicas of the hot shard and spread reads over them",
                "Replication lag"
              ],
              [
                "Push instead of pull",
                "For values everyone needs (a price, a config), broadcast updates to subscribers rather than having all of them poll",
                "A pub/sub or multicast channel to operate"
              ],
              [
                "Detect first",
                "Sample request keys (Redis <code>--hotkeys</code> with LFU, client-side counters) to find hot keys before they hurt",
                "Monitoring work"
              ]
            ]
          },
          {
            "type": "p",
            "html": "In market-data systems the last two rows are the norm: prices are pushed over multicast or a message bus to every consumer, which keeps its own in-memory copy. Pulling the same hot key from a shared cache ten thousand times a second is the anti-pattern the cache was supposed to prevent."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "With cache-aside, should a write update the cache or delete the entry? Why?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Delete it. With two concurrent writers, updating both the database and the cache opens a race: writer A writes the DB, writer B writes the DB, B updates the cache, then A updates the cache. The DB holds B&rsquo;s value and the cache holds A&rsquo;s, indefinitely. Deleting has no ordering problem: whichever delete runs last, the next read reloads the current value from the database."
          },
          {
            "type": "p",
            "html": "Deleting also avoids computing a cache value that may never be read, which matters when the cached form is expensive (a rendered page, an aggregate)."
          },
          {
            "type": "p",
            "html": "Delete-after-write is still not perfect: a reader that missed and read the old value before the write can set the cache after the delete. Bound it with a TTL, and close it with versioned sets or lease tokens if staleness is not acceptable."
          }
        ]
      },
      {
        "q": "What is a cache stampede and how do you prevent it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "When a popular key expires or is evicted, all concurrent requests for it miss at the same instant and each queries the database for the same value. Load on the database spikes by the key&rsquo;s request rate, often enough to slow or topple it, which makes the reloads slower, which lets even more requests pile up."
          },
          {
            "type": "p",
            "html": "Prevention: <strong>request coalescing</strong> so only one caller loads a key while others wait for its result (a per-key mutex in-process, <code>SET NX PX</code> lock across processes); <strong>serve stale while revalidating</strong>, so readers get the old value while one refresh runs; <strong>refresh ahead</strong> or probabilistic early expiration for hot keys; and <strong>TTL jitter</strong> so that keys written together do not all expire together."
          }
        ]
      },
      {
        "q": "When would you choose write-back over write-through, and what are the risks?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Write-back when writes are frequent, individually low-value and coalesce well: counters, view counts, rate-limit state, metrics, a position that changes on every tick but is only persisted periodically. Many updates to the same key collapse into one database write, and the write path has cache latency rather than database latency."
          },
          {
            "type": "p",
            "html": "Risks: <strong>data loss</strong> &mdash; anything not yet flushed is lost if the cache node fails, so the cache itself must be replicated or the data must be reconstructible from another source (such as an event log); <strong>ordering and consistency</strong> &mdash; other readers of the database see stale data until the flush, and flushes must preserve per-key order; <strong>complexity</strong> &mdash; tracking dirty entries, backpressure when the database is slow, and draining on shutdown."
          },
          {
            "type": "p",
            "html": "Write-through when the database must always be current (other systems read it directly) and the write rate is modest; its cost is that every write pays database latency."
          }
        ]
      },
      {
        "q": "A trading dashboard shows positions cached in Redis with a 5-second TTL. Risk says positions must never be more than 100&nbsp;ms stale. What do you change?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "A TTL only bounds staleness from above, and a 100&nbsp;ms TTL on every position would push most reads back to the database. The better model is to stop polling and push: the position service that owns the positions (and applies fills) publishes each change on a stream or pub/sub channel, and the dashboard service keeps positions in memory and applies updates as they arrive. Staleness is then the end-to-end latency of the update pipeline, typically milliseconds, and can be measured by stamping updates with their source time."
          },
          {
            "type": "p",
            "html": "If a cache must remain, update it from the same place that updates the position, in order &mdash; the owner writes through to Redis as part of applying the fill &mdash; rather than invalidating from application code, and version each entry by fill sequence number so an out-of-order update cannot regress it. Keep a TTL as a safety net, and alert when the age of the newest update exceeds the 100&nbsp;ms budget, so staleness is a monitored property rather than an assumption."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Nishtala et al. — Scaling Memcache at Facebook",
        "url": "https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf"
      },
      {
        "label": "Vattani et al. — Optimal Probabilistic Cache Stampede Prevention (XFetch)",
        "url": "https://cseweb.ucsd.edu/~avattani/papers/cache_stampede.pdf"
      },
      {
        "label": "AWS whitepaper: database caching strategies using Redis",
        "url": "https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/welcome.html"
      },
      {
        "label": "RFC 5861 — stale-while-revalidate and stale-if-error",
        "url": "https://www.rfc-editor.org/rfc/rfc5861"
      }
    ]
  }
];
