from deepdive._blocks import code, table, note, caveat, section, question

# A tiny key-value store with a real write-ahead log file, shared by two snippets.
KV = '''
import json, os, struct, tempfile, zlib

class KV:
    """Redo-only WAL: every record is [length][crc32][json payload]."""
    def __init__(self, path):
        self.path, self.data = path, {}
        self.fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND)
        self.fsyncs = 0

    def _append(self, record):
        payload = json.dumps(record).encode()
        os.write(self.fd, struct.pack(">II", len(payload), zlib.crc32(payload)) + payload)

    def commit(self, txid, writes, sync=True):
        for key, value in writes.items():
            self._append({"tx": txid, "k": key, "v": value})
        self._append({"tx": txid, "commit": True})
        if sync:
            os.fsync(self.fd)                  # durable before we say "committed"
            self.fsyncs += 1
        self.data.update(writes)               # then apply in memory

    @staticmethod
    def recover(path):
        """Replay committed transactions; stop at the first torn or corrupt record."""
        pending, data, good = {}, {}, 0
        with open(path, "rb") as f:
            blob = f.read()
        pos = 0
        while pos + 8 <= len(blob):
            length, crc = struct.unpack(">II", blob[pos:pos + 8])
            payload = blob[pos + 8:pos + 8 + length]
            if len(payload) < length or zlib.crc32(payload) != crc:
                break                          # torn write at the tail: ignore the rest
            rec = json.loads(payload)
            if rec.get("commit"):
                data.update(pending.pop(rec["tx"], {}))
                good += 1
            else:
                pending.setdefault(rec["tx"], {})[rec["k"]] = rec["v"]
            pos += 8 + length
        return data, good, len(pending), len(blob) - pos
'''

TOPIC = dict(
    id="durability",
    title="Write-Ahead Logging and Durability",
    summary="WAL mechanics, what fsync really promises, sequential vs random I/O, and redo/undo crash recovery.",
    intro=[
        "The D in ACID is a promise about a moment in time: once <code>COMMIT</code> returns, the data survives a crash. Keeping that promise without making every commit slow is what the write-ahead log is for, and understanding it means understanding what the operating system and the disk actually guarantee &mdash; which is less than most people assume.",
        "The storage-internals page introduced the WAL and checkpoints. This one goes deeper: the log&rsquo;s structure, <code>fsync</code> and its failure modes, why sequential I/O is cheap, and how redo and undo logging recover a database after a crash. The examples write and recover a real log file.",
    ],
    sections=[
        section(
            "WAL mechanics",
            "The log is an append-only sequence of records, each identified by a <strong>log sequence number</strong> (LSN), usually its byte offset. A record describes one change: which page or row, and enough information to redo it (and, in some designs, to undo it). Every data page carries the LSN of the last record applied to it, which is how recovery knows whether a page already contains a change.",
            "The protocol has two rules:",
            "<strong>1. Log before data.</strong> A dirty page may not be written to the data file until the log is durable up to that page&rsquo;s LSN.<br><strong>2. Log before commit.</strong> A transaction is committed when its commit record is durable in the log, and not before.",
            code(KV + '''
d = tempfile.mkdtemp()
path = os.path.join(d, "wal.log")
db = KV(path)
db.commit(1, {"AAPL": 100, "MSFT": 50})
db.commit(2, {"AAPL": 70})
db._append({"tx": 3, "k": "MSFT", "v": 0})     # tx 3 wrote but never committed
os.close(db.fd)                                # crash: in-memory state is gone

data, committed, uncommitted, junk = KV.recover(path)
print("recovered:", data)
print(f"{committed} committed transactions replayed, {uncommitted} uncommitted ignored")
''', label="a redo log: replay what committed, ignore what did not"),
            "Transaction 3&rsquo;s change is in the log but has no commit record, so recovery ignores it. Nothing was ever written to a separate data file here: the log alone is enough to rebuild the state, which is the key insight &mdash; the data files are just a cache of the log that makes reads fast.",
            "Real WAL records are physical or physiological (&ldquo;on page 812, slot 4, set these bytes&rdquo;) rather than logical key/value pairs, which makes redo fast and independent of higher-level structures. PostgreSQL additionally logs a <em>full page image</em> the first time a page is modified after each checkpoint, so a page torn by a crash mid-write can be restored whole.",
        ),
        section(
            "fsync: what it does and does not promise",
            "<code>write()</code> copies data into the kernel&rsquo;s page cache and returns. The data may reach the disk seconds later, or never, if the machine loses power. <code>fsync(fd)</code> asks the kernel to push the file&rsquo;s dirty pages <em>and</em> tell the device to flush its own volatile cache, and returns when the device says the data is on stable storage.",
            table(
                ["Call", "Guarantees"],
                [
                    ["<code>write()</code>", "Data is in the OS page cache. Survives a process crash, not a power loss or kernel panic"],
                    ["<code>fsync()</code>", "File data and metadata are on stable storage (if the device is honest)"],
                    ["<code>fdatasync()</code>", "File data plus only the metadata needed to read it back (size), skipping timestamps: often one fewer write"],
                    ["<code>O_DIRECT</code>", "Bypasses the page cache; does <em>not</em> by itself imply durability"],
                    ["<code>O_DSYNC</code> / <code>O_SYNC</code>", "Every <code>write()</code> behaves as if followed by <code>fdatasync()</code> / <code>fsync()</code>"],
                    ["fsync on the directory", "Needed after creating or renaming a file, or the new name itself may vanish"],
                ],
            ),
            "The places durability goes wrong in practice:",
            "<strong>Lying hardware.</strong> Consumer drives and some virtualised storage acknowledge a flush that only reached a volatile cache. Enterprise SSDs have power-loss protection (capacitors) that makes their cache effectively durable, which is also why they can acknowledge fsync quickly.<br><strong>fsync errors.</strong> The 2018 &ldquo;fsyncgate&rdquo; discovery: on Linux, if writeback fails, the kernel may mark the pages clean and report the error once; a retried <code>fsync</code> then succeeds without the data ever reaching disk. PostgreSQL now treats any fsync failure as fatal and recovers from the WAL instead of retrying.<br><strong>macOS.</strong> <code>fsync()</code> does not flush the drive cache; <code>fcntl(F_FULLFSYNC)</code> does. SQLite has <code>PRAGMA fullfsync</code> for this.<br><strong>Configuration.</strong> <code>synchronous_commit = off</code>, <code>innodb_flush_log_at_trx_commit = 2</code> or Redis&rsquo;s <code>appendfsync everysec</code> deliberately trade the last fraction of a second of commits for speed.",
            note("An fsync costs roughly 0.05&ndash;0.5&nbsp;ms on an enterprise NVMe drive with power-loss protection, and several milliseconds on consumer or network storage. That single number bounds how many durable, serial commits per second a system can do &mdash; unless commits are batched."),
        ),
        section(
            "Group commit",
            "If every transaction pays for its own fsync, commit throughput is capped at 1 / fsync latency. <strong>Group commit</strong> lets transactions that commit at around the same time share one: the first waiting committer calls fsync for everything appended so far, and every transaction whose commit record was covered returns together.",
            code(KV + '''
d = tempfile.mkdtemp()

one_each = KV(os.path.join(d, "a.log"))
for tx in range(1, 101):
    one_each.commit(tx, {f"k{tx}": tx})

grouped = KV(os.path.join(d, "b.log"))
for tx in range(1, 101):
    grouped.commit(tx, {f"k{tx}": tx}, sync=False)
    if tx % 20 == 0:                           # one flush covers 20 commit records
        os.fsync(grouped.fd)
        grouped.fsyncs += 1

print("fsync per commit:", one_each.fsyncs, "fsyncs for 100 commits")
print("group commit:    ", grouped.fsyncs, "fsyncs for 100 commits")
print("same log recovered:", KV.recover(one_each.path)[0] == KV.recover(grouped.path)[0])
''', label="100 commits, 100 fsyncs vs 5"),
            "The durability guarantee is unchanged: no transaction in a group is acknowledged until the fsync covering it returns. Each waits a little longer, and throughput rises by the group size. PostgreSQL exposes the knobs as <code>commit_delay</code> and <code>commit_siblings</code>; InnoDB and most modern engines group automatically; Kafka and trading-system journals batch the same way.",
        ),
        section(
            "Sequential vs random I/O",
            "Logs are append-only because sequential writes are dramatically cheaper than random ones, on every kind of storage:",
            table(
                ["Device", "Random 4&nbsp;KB writes", "Sequential writes", "Why"],
                [
                    ["Spinning disk (7,200 rpm)", "~100&ndash;200 IOPS (0.5&ndash;1&nbsp;MB/s)", "150&ndash;250&nbsp;MB/s", "Each random write waits for a seek and half a rotation, ~5&ndash;10&nbsp;ms"],
                    ["SATA SSD", "Tens of thousands IOPS", "~500&nbsp;MB/s", "No seek, but flash erases in large blocks; random writes fragment them and trigger garbage collection"],
                    ["NVMe SSD", "Hundreds of thousands IOPS", "Several GB/s", "Deep parallel queues; random is fast, but sequential still wins on write amplification and endurance"],
                    ["Network block storage", "Capped IOPS per volume", "Capped throughput", "Every I/O is a network round trip; IOPS are what you pay for"],
                ],
            ),
            "On an HDD the ratio is one to two orders of magnitude, which is where the WAL design came from. On SSDs random reads are nearly as fast as sequential ones, but random <em>writes</em> still cost more: the flash translation layer must erase whole blocks (often megabytes) before rewriting pages in them, and scattered small writes leave blocks partly valid, forcing the drive to copy live data around &mdash; the SSD&rsquo;s own write amplification. Sequential writes fill and invalidate whole blocks together.",
            "Other reasons sequential wins regardless of device: it allows large I/Os (fewer system calls, fewer interrupts), read-ahead and write-combining in the kernel work, and a single append position means a single fsync covers everything.",
            note("This is the common thread of the WAL, LSM trees, Kafka, and exchange/trading journals: turn random updates into one sequential append stream, and build random-access structures from it lazily."),
        ),
        section(
            "Crash recovery: redo, undo and ARIES",
            "Two policy choices determine what the log must contain:",
            table(
                ["Policy", "Meaning", "Consequence for recovery"],
                [
                    ["<strong>Steal</strong>", "Dirty pages of <em>uncommitted</em> transactions may be written to disk (e.g. evicted from a full buffer pool)", "Disk may hold uncommitted changes, so the log needs <strong>undo</strong> information"],
                    ["<strong>No-steal</strong>", "Uncommitted changes never reach disk", "No undo needed, but a big transaction must fit in memory"],
                    ["<strong>Force</strong>", "All of a transaction&rsquo;s pages are written at commit", "No redo needed, but every commit does random writes"],
                    ["<strong>No-force</strong>", "Pages are written whenever convenient after commit", "Disk may miss committed changes, so the log needs <strong>redo</strong> information"],
                ],
            ),
            "Real engines choose <strong>steal / no-force</strong> for performance, so they need both redo and undo. The standard algorithm is <strong>ARIES</strong>, and its three passes are worth knowing by name:",
            "<strong>1. Analysis.</strong> Scan forward from the last checkpoint to find which transactions were active at the crash and which pages might be dirty.<br><strong>2. Redo.</strong> Replay history from the oldest relevant LSN, reapplying every logged change whose page LSN shows it is missing &mdash; <em>including</em> changes of transactions that will be rolled back. This &ldquo;repeat history&rdquo; restores the exact state at the moment of the crash.<br><strong>3. Undo.</strong> Roll back the transactions that never committed, newest change first, writing <em>compensation log records</em> as it goes so that a crash during recovery does not undo anything twice.",
            "Not every engine follows ARIES literally. PostgreSQL needs no undo pass at all: its MVCC keeps old row versions in the heap, so an aborted transaction&rsquo;s tuples are simply invisible (its transaction ID is marked aborted) and are cleaned by vacuum later. InnoDB uses a redo log plus undo logs in its rollback segments. SQLite in rollback-journal mode is the opposite design: it saves original pages to a journal before overwriting them (undo), and in WAL mode it appends new pages and never overwrites in place (redo).",
            code(KV + '''
d = tempfile.mkdtemp()
path = os.path.join(d, "wal.log")
db = KV(path)
db.commit(1, {"cash": 1_000})
db.commit(2, {"cash": 400, "AAPL": 3})
size = os.path.getsize(path)
db.commit(3, {"cash": 0, "AAPL": 5})
os.close(db.fd)

with open(path, "r+b") as f:        # the machine lost power half-way through writing tx 3
    f.truncate(size + 20)

data, committed, uncommitted, junk = KV.recover(path)
print("recovered:", data)
print(f"committed: {committed}, incomplete: {uncommitted}, torn bytes ignored: {junk}")
''', label="a torn final record is detected by its checksum and discarded"),
            "The checksum and length prefix let recovery tell a complete record from a partially written one. Transaction 3 was never acknowledged (its fsync had not returned when the power failed), so losing it breaks no promise.",
        ),
    ],
    questions=[
        question(
            "Walk through exactly what happens, from the client&rsquo;s <code>COMMIT</code> to the data being on disk, in a WAL-based database.",
            "medium",
            "During the transaction each change is applied to a page in the buffer pool (making it dirty) and a log record describing it is appended to the in-memory WAL buffer. At <code>COMMIT</code> the engine appends a commit record and then flushes the WAL buffer up to that record&rsquo;s LSN: <code>write()</code> to the log file and <code>fsync()</code> (possibly shared with other transactions via group commit). When the fsync returns, the commit is durable, locks are released and the client is told it succeeded.",
            "The data pages are still only dirty in memory. They reach the data files later &mdash; when the background writer or a checkpoint flushes them, or when the buffer pool evicts them &mdash; and always after the log records covering them are durable. If replication is synchronous, the commit also waits for a standby to confirm receipt (or application) of the WAL before replying.",
        ),
        question(
            "What does fsync guarantee, and name three ways data can still be lost after fsync returned successfully.",
            "hard",
            "fsync guarantees that the file&rsquo;s modified data and metadata have been handed to the storage device and that the device has reported them durable. Ways that still fails:",
            "<strong>1. The device lies</strong>: a volatile write cache without power-loss protection acknowledges the flush; on power loss, data is gone. Common on consumer drives and some virtual disks.<br><strong>2. The directory entry was not synced</strong>: a newly created or renamed file&rsquo;s data is durable but its name is not, so after a crash the file does not exist. You must fsync the parent directory too.<br><strong>3. An earlier writeback error was swallowed</strong>: on Linux a failed background writeback can mark pages clean and report the error to only one fsync caller; a later fsync then returns success for data that never reached disk.<br><strong>4. Platform semantics</strong>: on macOS <code>fsync</code> does not flush the drive cache (<code>F_FULLFSYNC</code> does).<br><strong>5. The only copy was on one machine</strong>: fsync protects against power loss, not against the disk or server dying. Durability across hardware failure needs replication.",
        ),
        question(
            "Explain steal/no-steal and force/no-force, and why most databases need both redo and undo logs.",
            "hard",
            "<strong>Steal</strong> means the buffer manager may write a page containing uncommitted changes to disk, for example to make room. If the transaction then aborts or the system crashes, those changes are on disk and must be removed, so the log needs <em>undo</em> information. <strong>No-force</strong> means committed changes are not required to be on disk at commit, only in the log; after a crash they may be missing, so the log needs <em>redo</em> information.",
            "Steal/no-force is the high-performance combination: the buffer pool is not limited by the size of open transactions, and commits require only a sequential log flush rather than random page writes. The price is recovery that does both redo and undo, which is what ARIES does: analysis, redo everything (repeating history), then undo losers with compensation log records.",
            "No-steal/force would need neither log, but it would make every commit write all its pages randomly and make large transactions impossible. Shadow paging (LMDB, early System R) achieves no-undo differently: write new versions of pages elsewhere and atomically switch a root pointer at commit.",
        ),
        question(
            "Why are sequential writes cheaper than random writes, even on SSDs?",
            "medium",
            "On spinning disks the reason is mechanical: a random write needs a seek and rotational delay of several milliseconds, a sequential one streams at full media speed, a difference of 100&times; or more.",
            "SSDs have no seek, and random <em>reads</em> are nearly as fast as sequential. Random <em>writes</em> are still more expensive because flash can only be written to erased pages, and erasure happens in large blocks. Small scattered writes invalidate pages spread across many blocks; to reclaim space the drive&rsquo;s garbage collector must copy the still-valid pages out of a block before erasing it. That internal copying is the SSD&rsquo;s write amplification: it consumes bandwidth, raises latency unpredictably, and wears the flash out faster. Sequential writes fill and later invalidate whole blocks together, which makes garbage collection nearly free.",
            "Beyond the device, sequential I/O allows large requests, fewer system calls, effective write-combining, and a single fsync covering all of it.",
        ),
        question(
            "A trading system journals every order event before acting on it. It must sustain 200,000 events per second with durable acknowledgement, and fsync takes 100 microseconds. How?",
            "hard",
            "At 100&nbsp;&micro;s per fsync, one fsync per event caps throughput at 10,000 per second, twenty times too few. The answer is batching: accumulate events for a short window (or until N events), write them as one sequential append, fsync once, then acknowledge the whole batch. At 200,000 events per second, a batch every 100&nbsp;&micro;s holds about 20 events, and the added latency per event is at most one batch interval plus one fsync.",
            "Refinements worth mentioning: a dedicated journaling thread that owns the file descriptor (single writer, no locks), with producers handing it events through a lock-free ring buffer; preallocating the journal file so appends never extend file metadata (then <code>fdatasync</code> is cheap, or use <code>O_DSYNC</code>); an NVMe drive with power-loss protection, which is what makes 100&nbsp;&micro;s fsyncs possible at all; and, because a single disk is a single failure domain, replicating the journal to a second machine and counting an event as durable when it is in memory on two machines &mdash; which many low-latency systems prefer to a local fsync.",
        ),
    ],
    refs=[
        ("PostgreSQL: reliability and the write-ahead log", "https://www.postgresql.org/docs/current/wal-reliability.html"),
        ("Mohan et al. — ARIES: A Transaction Recovery Method", "https://cs.stanford.edu/people/chrismre/cs345/rl/aries.pdf"),
        ("SQLite: atomic commit in SQLite", "https://www.sqlite.org/atomiccommit.html"),
        ("PostgreSQL wiki: fsync errors", "https://wiki.postgresql.org/wiki/Fsync_Errors"),
        ("Pillai et al. — All File Systems Are Not Created Equal", "https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-pillai.pdf"),
    ],
)
