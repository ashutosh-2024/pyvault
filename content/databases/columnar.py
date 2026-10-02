from deepdive._blocks import code, table, note, caveat, section, question

# 200k synthetic trades, stored both ways. Pasted into several snippets.
TRADES = '''
import random, struct, zlib

random.seed(4)
N = 200_000
SYMS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOG", "META", "TSLA", "JPM"]
ts = list(range(1_700_000_000_000, 1_700_000_000_000 + N * 5, 5))      # sorted, ms
sym = [random.choice(SYMS) for _ in range(N)]
px = [round(100 + random.gauss(0, 2), 2) for _ in range(N)]
qty = [random.choice((100, 200, 300, 500, 1000)) for _ in range(N)]
venue = [random.choice(("XNAS", "ARCX", "BATS")) for _ in range(N)]
'''

TOPIC = dict(
    id="columnar",
    title="Columnar Databases and OLAP",
    summary="Row vs column storage, compression, zone maps, vectorized execution, and why ClickHouse is fast.",
    intro=[
        "A row store keeps each row&rsquo;s values together; a column store keeps each column&rsquo;s values together. That single layout decision changes almost everything downstream: how much data a query reads, how well it compresses, how the CPU processes it, and which workloads the system is good at.",
        "Trading firms live on both sides of this line: an OLTP store for orders and positions, and a columnar store (ClickHouse, kdb+, DuckDB, Parquet on object storage) for tick data and research. The examples use 200,000 synthetic trades stored both ways.",
    ],
    sections=[
        section(
            "Row vs column storage",
            "Most analytical queries touch a few columns of many rows: <em>average price per symbol over a day</em> reads two columns out of dozens. A row store must read every page containing those rows, and so reads every column. A column store reads only the two columns asked for.",
            code(TRADES + '''
row_fmt = "<q4sdi4s"                        # ts, sym, px, qty, venue per row
row_store = b"".join(struct.pack(row_fmt, t, s.encode(), p, q, v.encode())
                     for t, s, p, q, v in zip(ts, sym, px, qty, venue))
col_store = {
    "ts": struct.pack(f"<{N}q", *ts),
    "sym": "".join(sym).encode(),           # fixed width 4
    "px": struct.pack(f"<{N}d", *px),
    "qty": struct.pack(f"<{N}i", *qty),
    "venue": "".join(venue).encode(),
}
needed = ("sym", "px")                      # SELECT sym, avg(px) ... GROUP BY sym
row_bytes = len(row_store)
col_bytes = sum(len(col_store[c]) for c in needed)
print(f"row store reads    {row_bytes / 1e6:5.1f} MB (every column of every row)")
print(f"column store reads {col_bytes / 1e6:5.1f} MB (sym and px only)")
''', label="bytes read for SELECT sym, avg(px) GROUP BY sym"),
            "With only five columns the saving is about 2&times;. Real fact tables have fifty or two hundred columns and queries touch three to five, so the column store reads one or two orders of magnitude less before any compression.",
            table(
                ["", "Row store", "Column store"],
                [
                    ["Insert or update one row", "One page write", "One write per column, often into a buffer merged later"],
                    ["Fetch one whole row by key", "One page read", "One read per column"],
                    ["Scan a few columns of many rows", "Reads all columns", "Reads only those columns"],
                    ["Compression", "Modest (mixed types per page)", "Excellent (similar values together)"],
                    ["Typical use", "OLTP: orders, accounts, positions", "OLAP: ticks, events, logs, analytics"],
                ],
            ),
        ),
        section(
            "Compression",
            "Values of one column share a type and usually a narrow range, and are often sorted or repetitive. That makes them far more compressible than rows, where a timestamp sits next to a string next to a float. Column stores also apply <em>lightweight encodings</em> that can be processed without fully decompressing:",
            table(
                ["Encoding", "Stores", "Great for"],
                [
                    ["Dictionary", "Small integer codes plus a code &rarr; value table", "Low-cardinality strings: symbols, venues, sides"],
                    ["Run-length (RLE)", "(value, count) pairs", "Sorted or clustered columns"],
                    ["Delta", "Differences between consecutive values", "Timestamps, sequence numbers, sorted IDs"],
                    ["Delta-of-delta / Gorilla XOR", "Second differences / XOR of floats", "Regular time series; slowly moving prices"],
                    ["Bit packing / frame of reference", "Values minus a base, in as few bits as they need", "Small integer ranges"],
                ],
            ),
            code(TRADES + '''
row_store = b"".join(struct.pack("<q4sdi4s", t, s.encode(), p, q, v.encode())
                     for t, s, p, q, v in zip(ts, sym, px, qty, venue))
cols = {
    "ts": struct.pack(f"<{N}q", *ts),
    "sym": "".join(sym).encode(),
    "px": struct.pack(f"<{N}d", *px),
    "qty": struct.pack(f"<{N}i", *qty),
    "venue": "".join(venue).encode(),
}
# lightweight encodings first, then a general-purpose compressor on top
codes = {s: i for i, s in enumerate(SYMS)}
encoded = {
    "ts": struct.pack(f"<{N}q", ts[0], *(b - a for a, b in zip(ts, ts[1:]))),   # delta
    "sym": bytes(codes[s] for s in sym),                                          # dictionary
    "px": struct.pack(f"<{N}i", *(round(p * 100) for p in px)),                   # fixed point
    "qty": bytes((100, 200, 300, 500, 1000).index(q) for q in qty),               # dictionary
    "venue": bytes(("XNAS", "ARCX", "BATS").index(v) for v in venue),             # dictionary
}
raw = len(row_store)
rows_z = len(zlib.compress(row_store, 6))
cols_z = sum(len(zlib.compress(c, 6)) for c in cols.values())
enc_z = sum(len(zlib.compress(c, 6)) for c in encoded.values())
print(f"raw:                          {raw / 1e6:5.2f} MB")
print(f"row-major + zlib:             {rows_z / 1e6:5.2f} MB  ({raw / rows_z:4.1f}x)")
print(f"column-major + zlib:          {cols_z / 1e6:5.2f} MB  ({raw / cols_z:4.1f}x)")
print(f"columns, encoded, then zlib:  {enc_z / 1e6:5.2f} MB  ({raw / enc_z:4.1f}x)")
for name, c in encoded.items():
    print(f"  {name:<6} {len(zlib.compress(c, 6)):>9,} bytes")
''', label="the same data compressed as rows, as columns, and as encoded columns"),
            "Encoded columns end up two and a half times smaller than compressed rows, and ten times smaller than the raw data. The timestamp column, delta-encoded, shrinks almost to nothing because every delta is the same. Prices are the hardest: real market data is noisier than this, which is exactly what specialised float encodings like Gorilla target.",
            "Compression in a column store is not just about disk. Smaller data means more of it fits in memory and cache, and scans are usually bound by memory bandwidth, so compressed scans are often <em>faster</em> than uncompressed ones. Many engines evaluate predicates directly on dictionary codes (<code>sym = 'AAPL'</code> becomes <code>code = 0</code>) without decoding.",
        ),
        section(
            "Skipping data: sort keys and zone maps",
            "Column stores rarely have B-tree indexes. Instead they sort data by a chosen key and store the <strong>min and max</strong> of each column for each block of a few thousand rows (a <em>zone map</em>, <em>min/max index</em>, or in ClickHouse a <em>sparse primary index</em> with one mark per 8,192 rows). A query can then skip every block whose range cannot contain a match.",
            code(TRADES + '''
BLOCK = 8192
blocks = [(ts[i], ts[min(i + BLOCK, N) - 1]) for i in range(0, N, BLOCK)]

lo, hi = ts[0] + 400_000, ts[0] + 460_000                # a one-minute window
hit = [b for b in blocks if b[1] >= lo and b[0] <= hi]
print(f"{len(blocks)} blocks; one-minute query reads {len(hit)} of them")

# the same query on a column the data is NOT sorted by
pblocks = [(min(px[i:i + BLOCK]), max(px[i:i + BLOCK])) for i in range(0, N, BLOCK)]
hit = [b for b in pblocks if b[1] >= 100.00 and b[0] <= 100.05]
print(f"price between 100.00 and 100.05 reads {len(hit)} of {len(pblocks)} blocks")
''', label="min/max per block: great on the sort key, useless on a random column"),
            "Choosing the sort key is the most important schema decision in a column store, the equivalent of choosing the clustered index. For market data <code>(symbol, timestamp)</code> is typical: one symbol&rsquo;s ticks over a time range become one contiguous run of blocks.",
        ),
        section(
            "Vectorized execution",
            "Reading less data only helps if the CPU can keep up with it. The row-at-a-time iterator model makes a virtual function call per operator per row, with a branch per value, and cannot use SIMD. <strong>Vectorized</strong> engines pass <em>batches</em> of values (typically 1,024 to 65,536) between operators, and each operator runs a tight loop over a plain array: the per-call overhead is paid once per batch, loops are branch-light and SIMD-friendly, and data stays in the CPU cache.",
            code(TRADES + '''
calls = 0

def scan_rows():                     # iterator model: one value per next()
    global calls
    for p in px:
        calls += 1
        yield p

def filter_rows(child):
    global calls
    for p in child:
        calls += 1
        if p > 100:
            yield p

total = 0.0
for p in filter_rows(scan_rows()):
    total += p
row_calls = calls

calls, BATCH = 0, 4096
def scan_batches():                  # vectorized: one array per next()
    global calls
    for i in range(0, N, BATCH):
        calls += 1
        yield px[i:i + BATCH]

vtotal = 0.0
for batch in scan_batches():
    calls += 1                       # filter + sum over the whole batch
    vtotal += sum(p for p in batch if p > 100)

print(f"same answer: {abs(total - vtotal) < 1e-6}")
print(f"operator calls, row at a time: {row_calls:>9,}")
print(f"operator calls, 4,096 per batch: {calls:>7,}")
''', label="operator invocations: per row vs per batch"),
            "In Python the inner loop is still interpreted, so this shows only the change in structure. In a C++ engine the inner loop over a batch compiles to SIMD instructions processing 4&ndash;16 values per instruction, and the 400,000 function calls simply disappear. NumPy and pandas are fast for the same reason.",
            caveat("The alternative to vectorization is compiling the whole query into one fused machine-code loop (HyPer, Umbra, Spark whole-stage codegen). Both approaches reach similar speeds; vectorization is easier to build and debug, which is why DuckDB, ClickHouse, Velox and Snowflake use it."),
        ),
        section(
            "OLTP vs OLAP",
            table(
                ["", "OLTP", "OLAP"],
                [
                    ["Queries", "Many small reads and writes by key", "Few large scans and aggregations"],
                    ["Rows per query", "One to hundreds", "Millions to billions"],
                    ["Latency target", "Milliseconds or less, per request", "Seconds are fine for a report"],
                    ["Data freshness", "Current state", "History; often loaded in batches or streamed"],
                    ["Writes", "Frequent, concurrent, small, transactional", "Bulk appends; updates and deletes are rare and expensive"],
                    ["Storage", "Row store, B+ tree indexes", "Column store, sort keys, zone maps, heavy compression"],
                    ["Examples", "PostgreSQL, MySQL, Oracle, SQL Server", "ClickHouse, Snowflake, BigQuery, Redshift, DuckDB, kdb+"],
                ],
            ),
            "Running analytics on the OLTP database is the classic mistake: a long scan competes for buffer pool and I/O with latency-sensitive transactions, and in an MVCC engine a long-running query holds back cleanup. The usual architecture streams changes out of the OLTP database (change data capture) into an analytical store. <em>HTAP</em> systems (TiDB with TiFlash, SingleStore, SQL Server columnstore indexes) keep both representations of the same data inside one product.",
        ),
        section(
            "Why ClickHouse is fast for analytical workloads",
            "ClickHouse is a useful case study because its speed comes from combining every technique above and adding a few of its own:",
            "<strong>Columnar storage with per-column codecs.</strong> LZ4 or ZSTD, layered on specialised codecs such as <code>Delta</code>, <code>DoubleDelta</code>, <code>Gorilla</code> and <code>T64</code> chosen per column.<br><strong>MergeTree tables.</strong> Inserts write immutable, sorted <em>parts</em>; background merges combine them, much like an LSM tree. Inserts never modify existing data, so they are cheap and do not block reads.<br><strong>A sparse primary index.</strong> One entry per 8,192-row granule, so the index for billions of rows fits in memory and a range on the sort key reads only the matching granules. Data-skipping indexes (min/max, set, Bloom filter) add zone maps on other columns.<br><strong>Vectorized, SIMD-heavy execution</strong> written in C++, with many specialised implementations of hash tables and aggregate functions chosen by key type.<br><strong>Parallelism everywhere.</strong> A query is split across all cores, and across shards in a cluster.<br><strong>Approximation when asked.</strong> <code>uniq</code> (HyperLogLog-style), <code>quantileTDigest</code> and sampling trade exactness for speed.<br><strong>What it gives up.</strong> No full ACID transactions across tables, updates and deletes are asynchronous &ldquo;mutations&rdquo; that rewrite parts, and point lookups are relatively slow. It is built for append-mostly data scanned in bulk, which is exactly what tick data is.",
            note("Columnar stores are fast because they avoid work, not because they do the same work faster: they read fewer columns, fewer bytes per value, fewer blocks, and pay per-batch rather than per-row overhead."),
        ),
    ],
    questions=[
        question(
            "Why are column stores faster than row stores for analytical queries and slower for transactional ones?",
            "medium",
            "Analytical queries read a few columns of many rows. A column store reads only those columns, they compress far better because similar values sit together (dictionary, RLE, delta encodings, then LZ4/ZSTD), sorted data and zone maps let it skip whole blocks, and vectorized operators process each column as a tight loop over an array. Together that is often 10&ndash;100&times; less I/O and far better CPU efficiency.",
            "Transactional work reads or writes whole rows by key. In a column store, inserting one row touches every column file, updating a value inside a compressed block means rewriting the block, and fetching one full row means one lookup per column. Column stores mitigate this by buffering inserts in a row-oriented delta store and merging later, but single-row latency is still worse than a B+ tree row store.",
        ),
        question(
            "You store a year of tick data (20 billion rows) in ClickHouse. What ORDER BY key would you choose, and why?",
            "hard",
            "<code>ORDER BY (symbol, timestamp)</code>, typically with <code>PARTITION BY toDate(timestamp)</code> or by month. Almost every query restricts both symbol and a time range (&ldquo;AAPL trades between 09:30 and 09:35&rdquo;), and with this key those rows are contiguous: the sparse index finds the first matching granule for the symbol, then reads consecutive granules until the time range ends. Partitioning by date lets whole days be dropped or moved to cheaper storage cheaply.",
            "Why not timestamp first? Then a single-symbol query would find matching timestamps in every granule of the time range across all symbols and read far more data. Why low cardinality first in general? Because each key column only helps skipping while the preceding columns are equal; a leading column with few values produces long runs in which the next column is sorted.",
            "Complements: <code>LowCardinality(String)</code> for symbol and venue, <code>DoubleDelta</code> or <code>Delta</code> + ZSTD for timestamps, <code>Gorilla</code> for prices, and a projection or materialized view ordered differently (by venue, say) if another access pattern matters.",
        ),
        question(
            "What is a zone map, and when is it useless?",
            "medium",
            "A zone map stores summary statistics &mdash; at least min and max &mdash; of each column for each block of rows. A query predicate is checked against the summary first, and any block whose range cannot contain a match is skipped without being read or decompressed. It costs almost nothing to store and maintain.",
            "It is useless when the column&rsquo;s values are randomly distributed across blocks, because every block&rsquo;s min-max range then spans nearly the full domain and nothing can be skipped. It works on the sort key, on columns correlated with it (an auto-increment ID when sorted by time), and on data naturally clustered by insertion order. That is why the sort key choice matters so much, and why engines offer Bloom-filter or set indexes for high-cardinality columns that are not sorted.",
        ),
        question(
            "Explain vectorized execution and why it matters more as storage gets faster.",
            "hard",
            "In the classic iterator model every operator produces one row per <code>next()</code> call. For a billion-row scan that is billions of virtual calls, each doing a tiny amount of work, with unpredictable branches and no opportunity for SIMD. Vectorized execution passes batches of a few thousand values per call. The call overhead is amortised over the batch, each operator is a tight loop over contiguous arrays that the compiler can turn into SIMD instructions, and batches are sized to stay in L1/L2 cache.",
            "It matters more as storage gets faster because the bottleneck moves. When data came from spinning disks at 200&nbsp;MB/s, any CPU could keep up. From NVMe at several GB/s per drive, or from memory at tens of GB/s, a row-at-a-time interpreter is the bottleneck; only a vectorized or compiled engine can process data at the rate it arrives.",
        ),
    ],
    refs=[
        ("ClickHouse docs: MergeTree table engine", "https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree"),
        ("ClickHouse docs: why ClickHouse is so fast", "https://clickhouse.com/docs/concepts/why-clickhouse-is-so-fast"),
        ("Abadi et al. — The Design and Implementation of Modern Column-Oriented Database Systems", "https://stratos.seas.harvard.edu/files/stratos/files/columnstoresfntdbs.pdf"),
        ("Boncz et al. — MonetDB/X100: Hyper-Pipelining Query Execution", "https://www.cidrdb.org/cidr2005/papers/P19.pdf"),
        ("Pelkonen et al. — Gorilla: A Fast, Scalable, In-Memory Time Series Database", "https://www.vldb.org/pvldb/vol8/p1816-teller.pdf"),
    ],
)
