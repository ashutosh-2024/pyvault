from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="internals",
    title="Storage Engine Internals",
    summary="Pages, the buffer pool, WAL and checkpoints, dirty pages, and LSM trees vs B-trees.",
    intro=[
        "Underneath SQL, a storage engine does one job: keep a large amount of data on a slow device, keep the useful part in fast memory, and never lose a committed write when the power goes out. The same handful of structures &mdash; fixed-size pages, a buffer pool, a write-ahead log, checkpoints &mdash; appear in every serious engine, and the one big design fork is whether to update data in place (B-trees) or only ever append (LSM trees).",
        "SQLite exposes enough of its internals through <code>PRAGMA</code>s and the <code>dbstat</code> table to watch these mechanisms work on a real file.",
    ],
    sections=[
        section(
            "Pages: the unit of everything",
            "A database file is an array of fixed-size <strong>pages</strong> (SQLite 4&nbsp;KB, PostgreSQL 8&nbsp;KB, InnoDB 16&nbsp;KB). Every read from disk, every write to disk, every cache slot and every lock on the file&rsquo;s structure works in whole pages. A page is also the node size of the B+ trees from the indexing topic.",
            "A table or index page typically has a header, an array of <em>slot</em> pointers growing from the front, and the row data growing from the back, with free space in the middle. Rows are addressed by (page, slot), so a row can move within a page during compaction without changing its address.",
            code('''
                import os, sqlite3, tempfile

                path = os.path.join(tempfile.mkdtemp(), "demo.db")
                db = sqlite3.connect(path)
                db.execute("CREATE TABLE trades(id INTEGER PRIMARY KEY, sym TEXT, note TEXT)")
                db.execute("CREATE INDEX ix_sym ON trades(sym)")
                db.executemany("INSERT INTO trades(sym, note) VALUES (?, ?)",
                               [(f"S{i % 300}", "x" * 80) for i in range(20_000)])
                db.commit()

                print("page size:", db.execute("PRAGMA page_size").fetchone()[0], "bytes")
                print("file:", os.path.getsize(path) // 4096, "pages")
                for name, kind, pages, rows in db.execute("""
                        SELECT name, pagetype, count(*), sum(ncell) FROM dbstat
                        WHERE name IN ('trades', 'ix_sym') GROUP BY name, pagetype
                        ORDER BY name, pagetype"""):
                    print(f"  {name:<7} {kind:<9} {pages:>4} pages {rows:>7,} cells")
            ''', label="a 20,000-row table and its index, page by page"),
            "Both trees are two levels deep: one root page above the leaves. The table&rsquo;s root holds only pointers (its cells are separator keys), while the index is much smaller because its entries are only <code>(sym, rowid)</code>. Notice the index&rsquo;s 61 interior cells plus 19,939 leaf cells add up to exactly 20,000: SQLite stores table data in B+ trees but indexes in classic B-trees, where interior nodes hold real entries too. Every query you run is ultimately a walk over these pages.",
        ),
        section(
            "The buffer pool",
            "The <strong>buffer pool</strong> (PostgreSQL: <code>shared_buffers</code>; InnoDB: <code>innodb_buffer_pool_size</code>; SQLite: <code>cache_size</code>) is the engine&rsquo;s own cache of pages in RAM. Every page access goes through it: if the page is present it is a <em>hit</em>; if not, the engine picks a victim frame, writes it out first if it is <strong>dirty</strong> (modified since it was read), and reads the requested page in.",
            "Frames being used by a running operation are <em>pinned</em> and cannot be evicted. The replacement policy decides which unpinned page goes. Pure LRU has a famous weakness: one big sequential scan touches every page once and flushes the entire hot working set.",
            code('''
                from collections import OrderedDict

                class LRUPool:
                    def __init__(self, frames):
                        self.frames, self.pages = frames, OrderedDict()
                        self.hits = self.misses = self.writebacks = 0

                    def get(self, page, write=False):
                        if page in self.pages:
                            self.hits += 1
                            self.pages.move_to_end(page)
                        else:
                            self.misses += 1
                            if len(self.pages) >= self.frames:
                                _, dirty = self.pages.popitem(last=False)
                                self.writebacks += dirty      # dirty victim must be written first
                            self.pages[page] = False
                        if write:
                            self.pages[page] = True

                def run(scan):
                    pool = LRUPool(frames=100)
                    for round_ in range(20):
                        for p in range(80):                    # hot working set: 80 pages
                            pool.get(p, write=(p % 4 == 0))
                        if scan and round_ == 10:
                            for p in range(1_000, 1_500):      # one report scans 500 cold pages
                                pool.get(p)
                    total = pool.hits + pool.misses
                    return f"hit ratio {pool.hits / total:.1%}, dirty write-backs {pool.writebacks}"

                print("hot set only:       ", run(scan=False))
                print("plus one big scan:  ", run(scan=True))
            ''', label="a scan flushing the hot pages out of an LRU pool"),
            "Real engines defend against this. PostgreSQL uses a clock-sweep approximation of LRU and gives large sequential scans a small private <em>ring buffer</em> so they recycle their own frames. InnoDB inserts newly read pages at the midpoint of its LRU list, and only promotes them to the hot end if they are touched again after a delay. The effect is the same: one scan cannot evict the working set.",
            caveat("PostgreSQL deliberately keeps <code>shared_buffers</code> modest (often 25% of RAM) and relies on the operating system&rsquo;s page cache for the rest, so a page can be cached twice. InnoDB and most commercial engines use <code>O_DIRECT</code> to bypass the OS cache and size the buffer pool at 60&ndash;80% of RAM instead."),
        ),
        section(
            "WAL, dirty pages and checkpoints",
            "Writing every modified page back to its home location at commit would be slow (random writes, a whole page for a one-byte change) and unsafe (a crash half-way through a page write leaves a torn page). Instead engines use a <strong>write-ahead log</strong>: append a description of the change to a sequential log, <code>fsync</code> the log, and only then acknowledge the commit. The modified page stays dirty in the buffer pool and is written to its home location later.",
            "The rule that makes this safe is the <strong>WAL protocol</strong>: a dirty page may not be written to the data file until the log records describing its changes are durable. After a crash, replaying the log reconstructs every committed change the data file is missing.",
            "A <strong>checkpoint</strong> bounds how much log must be replayed. It flushes dirty pages to the data files and records a point in the log before which nothing is needed for recovery, so old log segments can be recycled.",
            code('''
                import os, sqlite3, tempfile

                path = os.path.join(tempfile.mkdtemp(), "demo.db")
                db = sqlite3.connect(path, isolation_level=None)
                db.execute("PRAGMA journal_mode = WAL")
                db.execute("PRAGMA wal_autocheckpoint = 0")        # we checkpoint by hand
                db.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT)")

                def sizes(label):
                    kb = lambda f: os.path.getsize(f) // 1024
                    print(f"{label:<28} db {kb(path):>5} KB   wal {kb(path + '-wal'):>5} KB")

                db.execute("BEGIN")
                db.executemany("INSERT INTO t(v) VALUES (?)", [("x" * 100,) for _ in range(10_000)])
                db.execute("COMMIT")
                sizes("after 10,000 inserts")

                db.execute("UPDATE t SET v = 'y' WHERE id = 5")
                sizes("after a one-row update")

                busy, log_frames, done = db.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone()
                print(f"checkpoint: {done} of {log_frames} WAL frames copied into the db file")
                db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                sizes("after checkpoint")
            ''', label="SQLite: commits go to the WAL; the checkpoint moves them home"),
            "Three things to notice. After the inserts commit, the main file is still essentially empty: the committed data exists only in the WAL, and readers find the newest version of each page there. A one-row update appended a whole new 4&nbsp;KB page to the WAL, not a few bytes. And the checkpoint copied every frame into the database file and allowed the log to be truncated.",
            table(
                ["Checkpoint style", "How", "Trade-off"],
                [
                    ["Sharp (stop the world)", "Block writes, flush all dirty pages", "Simple recovery; periodic latency spikes"],
                    ["Fuzzy", "Flush dirty pages in the background while transactions continue; record which pages were dirty", "Smooth latency; recovery logic must cope with a checkpoint that was in progress"],
                    ["Spread (PostgreSQL)", "Fuzzy, paced over <code>checkpoint_completion_target</code> of the interval", "Avoids I/O bursts; longer recovery window"],
                ],
            ),
            note("Checkpoint frequency trades steady-state write cost against recovery time. Rare checkpoints mean fewer page writes (a page dirtied 100 times is flushed once) but more log to replay after a crash."),
        ),
        section(
            "LSM trees vs B-trees",
            "A B-tree updates pages <em>in place</em>. A <strong>log-structured merge tree</strong> (LevelDB, RocksDB, Cassandra, ScyllaDB, the storage layer of many time-series stores) never modifies anything on disk:",
            "<strong>1.</strong> Writes go to the WAL (for durability) and to an in-memory sorted structure, the <em>memtable</em>.<br><strong>2.</strong> When the memtable is full it is written out as an immutable sorted file, an <em>SSTable</em>, in one sequential write.<br><strong>3.</strong> Background <em>compaction</em> merges SSTables into larger ones, discarding overwritten values and deletion markers (<em>tombstones</em>).<br><strong>4.</strong> A read checks the memtable, then SSTables from newest to oldest, stopping at the first hit. Per-file Bloom filters let it skip files that certainly do not contain the key.",
            code('''
                import bisect

                class LSM:
                    def __init__(self, memtable_limit=4, fanout=3):
                        self.mem, self.runs = {}, []          # runs: newest first, each sorted
                        self.limit, self.fanout = memtable_limit, fanout
                        self.user_bytes = self.disk_bytes = 0

                    def put(self, key, value):
                        self.user_bytes += 1
                        self.mem[key] = value
                        if len(self.mem) >= self.limit:
                            self.runs.insert(0, sorted(self.mem.items()))
                            self.disk_bytes += len(self.mem)      # flush: sequential write
                            self.mem = {}
                            if len(self.runs) > self.fanout:
                                self.compact()

                    def compact(self):                        # merge all runs into one
                        merged = {}
                        for run in reversed(self.runs):       # oldest first; newer wins
                            merged.update(run)
                        self.runs = [sorted(merged.items())]
                        self.disk_bytes += len(merged)        # compaction rewrites data

                    def get(self, key):
                        if key in self.mem:
                            return self.mem[key], 0
                        for checked, run in enumerate(self.runs, 1):
                            i = bisect.bisect_left(run, (key,))
                            if i < len(run) and run[i][0] == key:
                                return run[i][1], checked
                        return None, len(self.runs)

                db = LSM()
                for i in range(49):
                    db.put(f"k{i % 25:02d}", i)                # 49 writes over 25 keys
                print("runs on disk:", [len(r) for r in db.runs], "+ memtable", len(db.mem))
                print(f"write amplification: {db.disk_bytes / db.user_bytes:.2f}x")
                for key in ("k23", "k20", "k02", "k99"):
                    value, runs_checked = db.get(key)
                    print(f"get({key}) = {value}, runs checked: {runs_checked}")
            ''', label="a toy LSM tree: memtable, flushes, compaction"),
            "Even this toy shows the trade. Every write is a cheap in-memory insert and every disk write is sequential, but compaction has already rewritten the data more than twice over, and the cost of a read depends on where the key happens to be: the memtable, the newest run, or the oldest. A lookup for a key that does not exist is the worst case &mdash; it checks every run &mdash; which is why Bloom filters are essential in real LSM engines.",
            table(
                ["", "B+ tree (InnoDB, PostgreSQL)", "LSM tree (RocksDB, Cassandra)"],
                [
                    ["Write path", "Find the leaf, modify in place (plus WAL)", "Append to memtable (plus WAL); flush sequentially"],
                    ["Write throughput", "Limited by random page writes", "High; all disk writes are sequential"],
                    ["Point read", "One root-to-leaf descent", "Memtable, then possibly several SSTables (Bloom filters help)"],
                    ["Range scan", "Walk the linked leaves", "Merge iterators across all levels"],
                    ["Space", "Fragmentation; pages part-full after splits", "Obsolete versions until compaction; compresses well"],
                    ["Latency tail", "Predictable", "Compaction can cause stalls"],
                    ["Good fit", "Read-heavy OLTP, predictable latency", "Write-heavy ingest: logs, metrics, events, time series"],
                ],
            ),
        ),
        section(
            "Write, read and space amplification",
            "The three numbers used to compare storage engines:",
            table(
                ["Amplification", "Definition", "B+ tree", "LSM (leveled)"],
                [
                    ["<strong>Write</strong>", "Bytes written to disk &divide; bytes the application wrote", "A whole page (4&ndash;16&nbsp;KB) per modified row, plus WAL, plus full-page images after checkpoints", "Each byte is rewritten once per level it passes through: often 10&ndash;30&times;"],
                    ["<strong>Read</strong>", "Pages or files touched per logical read", "Tree height, mostly cached: 1&ndash;2 I/Os", "One per level in the worst case; Bloom filters cut point reads to about 1"],
                    ["<strong>Space</strong>", "Bytes on disk &divide; bytes of live data", "About 1.3&ndash;1.5&times; from half-full pages", "About 1.1&times; leveled, up to 2&times; tiered, before compaction catches up"],
                ],
            ),
            "The <em>RUM conjecture</em> puts it formally: you can optimise for two of Read, Update and Memory (space) overhead, but not all three. B+ trees favour reads; LSM trees favour writes and space; leveled vs tiered compaction moves an LSM along the same trade-off.",
            "Write amplification is not an academic number on SSDs. Flash cells survive a limited number of program/erase cycles, and the drive&rsquo;s own garbage collection adds a second layer of amplification underneath the database&rsquo;s. An engine with 20&times; write amplification wears out a drive 20&times; faster than the application&rsquo;s write rate suggests.",
            note("Ask &ldquo;what is this workload&rsquo;s read:write ratio and does it need range scans?&rdquo; before choosing an engine. Write-heavy with point reads: LSM. Read-heavy with predictable latency: B+ tree."),
        ),
    ],
    questions=[
        question(
            "Why does a database write to a log first instead of just writing the changed pages at commit?",
            "medium",
            "Three reasons. <strong>Speed</strong>: the log is an append-only sequential write, and a commit needs only one <code>fsync</code> of the log tail, where writing pages in place means random writes to wherever each page lives. <strong>Size</strong>: a log record describes the change (often tens of bytes), while a page write is 4&ndash;16&nbsp;KB. <strong>Atomicity across pages</strong>: a transaction touching ten pages cannot write them all atomically, but it can append one commit record atomically; recovery then redoes or undoes page changes to match the log.",
            "The dirty pages are written later by the background writer and checkpoints, and a page updated many times between checkpoints is written once, so the log also absorbs repeated writes to hot pages.",
        ),
        question(
            "Compare LSM trees and B+ trees. When would you choose each?",
            "medium",
            "A B+ tree updates pages in place: reads are one descent through a mostly cached tree, range scans walk the leaves, and latency is predictable, but every row change dirties a whole page, so random write throughput is limited.",
            "An LSM tree buffers writes in memory and flushes immutable sorted files sequentially, merging them in the background. Writes are fast and sequential and data compresses well, but reads may consult several files (Bloom filters mitigate point reads, not range scans), compaction consumes I/O and CPU, and it can cause latency spikes.",
            "Choose an LSM for write-heavy ingest with mostly recent or point reads: event logs, metrics, time series, message stores, key-value caches of large data. Choose a B+ tree for read-heavy OLTP with range queries and strict latency requirements. RocksDB under MySQL (MyRocks) shows the choice can be made per table.",
        ),
        question(
            "What is a dirty page, and what happens to dirty pages during a checkpoint and a crash?",
            "medium",
            "A dirty page is one modified in the buffer pool but not yet written back to the data file. Its changes are already durable in the WAL, so being dirty is safe.",
            "During a checkpoint the engine writes dirty pages to the data files (in a fuzzy checkpoint, gradually and while transactions continue) and then records the checkpoint position in the log. Everything before that position is no longer needed for recovery.",
            "In a crash, the dirty pages in memory are lost. Recovery starts from the last checkpoint and replays the log forward, reapplying every change whose page on disk is older than the log record (it compares each page&rsquo;s LSN with the record&rsquo;s). The data files end up exactly as the buffer pool would have been.",
        ),
        question(
            "Why is LRU a poor buffer-pool replacement policy, and what do real databases do instead?",
            "hard",
            "LRU treats a page accessed once as more valuable than a page accessed thousands of times, if the single access was more recent. A sequential scan of a large table &mdash; a report, a backup, an <code>ANALYZE</code> &mdash; touches each page exactly once and pushes the entire hot working set out of the pool. After the scan, every OLTP query misses until the cache warms up again. Strict LRU also needs a global list updated on every access, which becomes a contention point.",
            "PostgreSQL uses clock-sweep (each buffer has a small usage counter decremented by a sweeping hand, so frequently used pages survive several passes) and gives bulk scans, <code>VACUUM</code> and <code>COPY</code> small ring buffers. InnoDB splits its LRU list into young and old sublists; new pages enter at the old head and are promoted only if accessed again after <code>innodb_old_blocks_time</code>. Other engines use LRU-K or 2Q, which rank pages by their second-most-recent access so that one-off touches do not count.",
        ),
        question(
            "What is write amplification, where does it come from in a B+ tree and in an LSM tree, and why does it matter on SSDs?",
            "hard",
            "Write amplification is bytes physically written divided by bytes the application logically wrote.",
            "In a B+ tree: changing a 100-byte row dirties a 16&nbsp;KB page, which is eventually written whole; the change is also written to the WAL; PostgreSQL additionally writes a full-page image to the WAL the first time a page is modified after each checkpoint (to repair torn pages); and page splits rewrite neighbours. Double-write buffers (InnoDB) write pages twice.",
            "In an LSM tree: each byte is written to the WAL, flushed in an SSTable, and then rewritten each time compaction moves it down a level. With leveled compaction and a fanout of 10, that is roughly 10&times; per level.",
            "On SSDs it matters twice: it consumes write bandwidth that could serve application writes, and flash endures a finite number of erase cycles, so amplification directly shortens drive life. The SSD&rsquo;s internal garbage collection adds its own amplification on top, and it is worst for random small writes, which is one more reason sequential write patterns are preferred.",
        ),
    ],
    refs=[
        ("SQLite: write-ahead logging", "https://www.sqlite.org/wal.html"),
        ("SQLite: database file format", "https://www.sqlite.org/fileformat.html"),
        ("PostgreSQL: WAL internals", "https://www.postgresql.org/docs/current/wal-internals.html"),
        ("RocksDB wiki: leveled compaction", "https://github.com/facebook/rocksdb/wiki/Leveled-Compaction"),
        ("O'Neil et al. — The Log-Structured Merge-Tree", "https://www.cs.umb.edu/~poneil/lsmtree.pdf"),
        ("Athanassoulis et al. — The RUM Conjecture", "https://stratos.seas.harvard.edu/files/stratos/files/rum.pdf"),
    ],
)
