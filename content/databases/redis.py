from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="redis",
    title="In-Memory Databases and Redis",
    summary="Redis's single-threaded design, its hash tables and sorted sets, memory layout, persistence and eviction.",
    intro=[
        "An in-memory database keeps the whole dataset in RAM and treats disk only as a place to recover from. That removes the buffer pool, page layout and most of the I/O path, and what is left can answer a request in a few microseconds. Redis is the example every interviewer reaches for, and it is also a deliberately simple system whose design decisions are easy to reason about.",
        "There is no Redis server in this site&rsquo;s build, so the examples are small Python models of the structures Redis actually uses: its incrementally rehashed hash table, the skiplist behind sorted sets, and approximated LRU eviction. The numbers and trade-offs they show are the real ones.",
    ],
    sections=[
        section(
            "Why Redis is fast: one thread, all in memory",
            "Redis executes every command on a single thread, one at a time, from an event loop over non-blocking sockets. That sounds like a limitation and is the core of the design:",
            "<strong>No locks.</strong> Every command sees and mutates data with no possibility of interference, so each command is atomic for free.<br><strong>No context switches</strong> on the hot path, and the working data stays in one core&rsquo;s cache.<br><strong>Simple data structures</strong> with known complexity, so a command&rsquo;s cost is predictable.",
            "The bottleneck is usually the network, not the CPU. Redis 6 added I/O threads that read and parse requests and write replies in parallel, but command execution is still single-threaded. The flip side: <em>one slow command blocks every client</em>. <code>KEYS *</code>, <code>SMEMBERS</code> on a million-element set, a large <code>DEL</code>, or a Lua script with a loop stalls the whole server for its duration.",
            table(
                ["Command", "Complexity", "Safe on a large key?"],
                [
                    ["<code>GET</code>, <code>SET</code>, <code>HGET</code>, <code>INCR</code>", "O(1)", "Yes"],
                    ["<code>ZADD</code>, <code>ZRANK</code>, <code>ZSCORE</code>", "O(log n)", "Yes"],
                    ["<code>ZRANGEBYSCORE ... LIMIT</code>", "O(log n + m)", "Yes, for small m"],
                    ["<code>HGETALL</code>, <code>SMEMBERS</code>, <code>LRANGE 0 -1</code>", "O(n)", "No: use <code>HSCAN</code>/<code>SSCAN</code>"],
                    ["<code>KEYS pattern</code>", "O(total keys)", "Never in production: use <code>SCAN</code>"],
                    ["<code>DEL</code> on a huge key", "O(n) to free memory", "Use <code>UNLINK</code> (frees in a background thread)"],
                ],
            ),
            note("Redis gives you atomicity per command, and per <code>MULTI</code>/<code>EXEC</code> block or Lua script. Anything that must read, decide and write should be one of those, never three round trips."),
        ),
        section(
            "Hash tables and incremental rehashing",
            "The keyspace itself is a hash table, and so is every Redis hash once it outgrows its compact encoding. A hash table must grow as it fills, and rehashing a table with ten million keys in one go would freeze the server for hundreds of milliseconds.",
            "Redis avoids that by keeping <em>two</em> tables during a resize and moving entries incrementally: each normal operation also migrates one bucket from the old table to the new one (and a timer migrates more when the server is idle). Lookups check both tables until the move is complete. The cost of the resize is spread over thousands of operations, and no single command pays for it.",
            code('''
                class IncrementalDict:
                    def __init__(self):
                        self.old, self.new, self.cursor = [[] for _ in range(4)], None, 0
                        self.size = 0

                    def _step(self):
                        """Move one bucket from old to new; called on every operation."""
                        if self.new is None:
                            return
                        for k, v in self.old[self.cursor]:
                            self.new[hash(k) % len(self.new)].append((k, v))
                        self.old[self.cursor] = []
                        self.cursor += 1
                        if self.cursor == len(self.old):
                            self.old, self.new, self.cursor = self.new, None, 0

                    def set(self, key, value):
                        self._step()
                        if self.new is None and self.size >= len(self.old):   # load factor 1
                            self.new = [[] for _ in range(len(self.old) * 2)]
                        table = self.new if self.new is not None else self.old
                        table[hash(key) % len(table)].append((key, value))
                        self.size += 1

                    def get(self, key):
                        self._step()
                        for table in (self.old, self.new):
                            if table is not None:
                                for k, v in table[hash(key) % len(table)]:
                                    if k == key:
                                        return v

                d = IncrementalDict()
                for i in range(12):
                    d.set(f"key{i}", i)
                    state = f"rehashing {len(d.old)}->{len(d.new)}, cursor {d.cursor}" if d.new else "stable"
                    print(f"after set #{i + 1:>2}: {state}")
                print("all readable:", all(d.get(f"key{i}") == i for i in range(12)))
            ''', label="a hash table that grows one bucket at a time"),
            "Resizes overlap with normal traffic and complete after a few operations; every key stays readable throughout, because lookups consult both tables.",
            caveat("Redis defers rehashing while a background save child process exists (unless the table gets very full), because moving entries would touch pages and defeat the copy-on-write sharing that keeps <code>fork()</code>-based snapshots cheap."),
        ),
        section(
            "Sorted sets: a skiplist plus a hash table",
            "A sorted set (<code>ZSET</code>) maps members to scores and keeps them ordered by score. It is the go-to structure for leaderboards, rate-limit windows, priority queues, time-indexed events, and &mdash; in trading contexts &mdash; price-ordered books. Redis implements it with two structures at once:",
            "<strong>A hash table</strong> from member to score, for O(1) <code>ZSCORE</code> and membership.<br><strong>A skiplist</strong> ordered by (score, member), for O(log n) insert, delete, rank and range queries.",
            "A skiplist is a sorted linked list with express lanes: each node is promoted to the next level up with probability 1/4 (in Redis), so a search skims along the top level and drops down when it would overshoot. It gives the same expected O(log n) as a balanced tree, is simple to implement, and makes range scans a walk along the bottom level. Redis also stores a <em>span</em> on each link so it can compute ranks during the search.",
            code('''
                import random

                random.seed(3)
                MAX_LEVEL, P = 8, 0.25

                class Node:
                    def __init__(self, score, member, level):
                        self.score, self.member, self.next = score, member, [None] * level

                class SkipList:
                    def __init__(self):
                        self.head, self.level = Node(float("-inf"), None, MAX_LEVEL), 1

                    def insert(self, score, member):
                        update, x = [self.head] * MAX_LEVEL, self.head
                        for lvl in reversed(range(self.level)):
                            while x.next[lvl] and (x.next[lvl].score, x.next[lvl].member) < (score, member):
                                x = x.next[lvl]
                            update[lvl] = x
                        level = 1
                        while random.random() < P and level < MAX_LEVEL:
                            level += 1
                        self.level = max(self.level, level)
                        node = Node(score, member, level)
                        for lvl in range(level):
                            node.next[lvl], update[lvl].next[lvl] = update[lvl].next[lvl], node

                    def range_by_score(self, lo, hi):
                        x, visited = self.head, 0
                        for lvl in reversed(range(self.level)):
                            while x.next[lvl] and x.next[lvl].score < lo:
                                x, visited = x.next[lvl], visited + 1
                        out, x = [], x.next[0]
                        while x and x.score <= hi:
                            out.append((x.member, x.score))
                            x = x.next[0]
                        return out, visited

                bids = SkipList()
                for i in range(10_000):
                    bids.insert(round(random.uniform(90, 110), 2), f"order{i}")
                hits, visited = bids.range_by_score(100.00, 100.02)
                print("levels used:", bids.level)
                print(f"nodes visited to find the range start: {visited} of 10,000")
                print("first matches:", hits[:3])
            ''', label="ZRANGEBYSCORE on a skiplist"),
            "Finding the start of the range touched 15 nodes out of ten thousand, and the matches were then read off the bottom level in order.",
        ),
        section(
            "Memory layout and encodings",
            "In an in-memory store the cost that matters is bytes per key, because RAM is the capacity limit. Every Redis key carries overhead: the key string, a <code>redisObject</code> header (type, encoding, LRU clock, refcount, pointer), a hash-table entry, and allocator rounding. For small values the overhead is larger than the data.",
            "Redis therefore stores small collections in compact, contiguous encodings and converts them to the full structures only when they grow:",
            table(
                ["Type", "Small encoding", "Converts to", "Threshold (defaults)"],
                [
                    ["Hash", "<code>listpack</code> (flat byte array)", "hash table", "&gt; 128 fields or a value &gt; 64 bytes"],
                    ["Sorted set", "<code>listpack</code>", "skiplist + hash table", "&gt; 128 members or a member &gt; 64 bytes"],
                    ["Set", "<code>intset</code> (sorted integers) or <code>listpack</code>", "hash table", "&gt; 512 integers / &gt; 128 strings"],
                    ["List", "<code>listpack</code>", "<code>quicklist</code> (linked list of listpacks)", "size-based"],
                    ["String", "<code>int</code> or <code>embstr</code> (header and bytes in one allocation)", "<code>raw</code>", "&gt; 44 bytes"],
                ],
            ),
            "A listpack lookup is a linear scan, but over a few hundred bytes of contiguous memory that is faster than chasing hash-table pointers, and it uses a fraction of the memory. The same effect is visible in Python:",
            code('''
                import sys

                n = 100
                as_dict = {f"field{i}": i for i in range(n)}
                as_packed = "".join(f"field{i}\\0{i}\\0" for i in range(n)).encode()

                dict_bytes = sys.getsizeof(as_dict) + sum(sys.getsizeof(k) + sys.getsizeof(v)
                                                          for k, v in as_dict.items())
                print(f"dict of {n} small fields: {dict_bytes:>6,} bytes")
                print(f"packed into one buffer:  {sys.getsizeof(as_packed):>6,} bytes")
            ''', label="object-per-field vs one contiguous buffer"),
            "Practical consequences: store an object as one hash with many fields rather than many top-level keys, keep collections under the encoding thresholds where you can, and remember that a 1&nbsp;GB dataset may need several GB of RAM once overhead, fragmentation, replication buffers and the copy-on-write headroom for snapshots are included. <code>MEMORY USAGE key</code> and <code>OBJECT ENCODING key</code> show the real numbers.",
        ),
        section(
            "Persistence trade-offs",
            "Redis offers two persistence mechanisms, and they are often combined:",
            table(
                ["", "RDB snapshot", "AOF (append-only file)"],
                [
                    ["What", "Point-in-time binary dump of the whole dataset", "Log of every write command"],
                    ["How", "<code>fork()</code>; the child writes the snapshot while the parent keeps serving, sharing memory copy-on-write", "Append each write; periodically rewrite the file compactly in a child process"],
                    ["Data lost on crash", "Everything since the last snapshot (minutes)", "Depends on <code>appendfsync</code> (below)"],
                    ["Restart speed", "Fast: load a compact file", "Slower: replay commands (mitigated by an RDB preamble)"],
                    ["Cost", "Fork latency and up to 2&times; memory under heavy writes", "Continuous disk writes and fsyncs"],
                ],
            ),
            table(
                ["<code>appendfsync</code>", "Behaviour", "Worst-case loss"],
                [
                    ["<code>always</code>", "fsync before replying to each write", "Nothing acknowledged, but every write waits for the disk"],
                    ["<code>everysec</code> (default)", "A background thread fsyncs once a second", "About one second of writes"],
                    ["<code>no</code>", "Leave flushing to the OS", "Whatever the OS had not flushed (often ~30 s)"],
                ],
            ),
            "The <code>fork()</code> detail matters for large instances: the fork itself must copy the parent&rsquo;s page tables, which for a 50&nbsp;GB process can take a significant fraction of a second, during which Redis serves nothing. Every page written while the child is saving is duplicated, so memory can spike. Transparent huge pages make both worse and should be disabled.",
            caveat("A Redis replica acknowledging a write does not make it durable: replication is asynchronous by default. <code>WAIT numreplicas timeout</code> blocks until that many replicas have received the write, which narrows the window but does not provide the guarantees of a consensus protocol."),
        ),
        section(
            "Caching with Redis: eviction and invalidation",
            "When Redis is a cache it runs with <code>maxmemory</code> and an eviction policy that decides what to drop when full:",
            table(
                ["Policy", "Evicts"],
                [
                    ["<code>noeviction</code>", "Nothing; writes fail with an error (the default &mdash; right for a database, wrong for a cache)"],
                    ["<code>allkeys-lru</code> / <code>volatile-lru</code>", "Least recently used, among all keys / keys with a TTL"],
                    ["<code>allkeys-lfu</code> / <code>volatile-lfu</code>", "Least frequently used (a decaying logarithmic counter per key)"],
                    ["<code>volatile-ttl</code>", "Keys closest to expiry"],
                    ["<code>allkeys-random</code> / <code>volatile-random</code>", "Random"],
                ],
            ),
            "Redis does not keep an exact LRU list; that would cost two pointers per key and a list update on every read. It stores a 24-bit last-access clock per key, samples a handful of keys when it needs to evict (<code>maxmemory-samples</code>, default 5), and evicts the oldest of the sample, keeping a small pool of good candidates between rounds. How close does sampling get?",
            code('''
                import random
                from collections import OrderedDict

                random.seed(11)
                KEYS, CAPACITY, REQUESTS = 5_000, 500, 60_000
                weights = [1 / (i + 1) for i in range(KEYS)]          # Zipf-like popularity
                trace = random.choices(range(KEYS), weights, k=REQUESTS)

                def exact_lru():
                    cache, hits = OrderedDict(), 0
                    for k in trace:
                        if k in cache:
                            hits += 1
                            cache.move_to_end(k)
                        else:
                            if len(cache) >= CAPACITY:
                                cache.popitem(last=False)
                            cache[k] = True
                    return hits / REQUESTS

                def sampled_lru(samples):
                    rng = random.Random(5)
                    cache, hits = {}, 0                                # key -> last access time
                    for t, k in enumerate(trace):
                        if k in cache:
                            hits += 1
                        elif len(cache) >= CAPACITY:
                            victim = min(rng.sample(list(cache), samples), key=cache.get)
                            del cache[victim]
                        cache[k] = t
                    return hits / REQUESTS

                print(f"exact LRU:            {exact_lru():.1%} hit ratio")
                for s in (1, 3, 5, 10):
                    print(f"sampled, {s:>2} per evict: {sampled_lru(s):.1%}")
            ''', label="approximated LRU vs the real thing on a skewed workload"),
            "Sampling one key is random eviction; five is already close to true LRU, at a fraction of the memory and CPU. That is the whole design philosophy of Redis in one table: exactness traded away where the difference does not matter.",
            "Eviction is only half of caching. Keeping cached values consistent with the source of truth &mdash; invalidation, stampedes, hot keys &mdash; is covered on the caching page.",
        ),
    ],
    questions=[
        question(
            "Redis is single-threaded. How does it handle 100,000+ operations per second, and when does the single thread become a problem?",
            "medium",
            "Each command is a few hundred nanoseconds to a microsecond of in-memory work on a known data structure, with no locks, no disk I/O on the request path, and no context switches. An event loop (epoll/kqueue) multiplexes thousands of connections on that thread. Pipelining lets clients send many commands per round trip, so the per-command network cost amortises. The network stack, not the CPU, is usually the limit, and Redis 6+ moves socket reads and writes to I/O threads.",
            "It becomes a problem when one command is slow, because everything queues behind it: O(n) commands on big keys (<code>KEYS</code>, <code>HGETALL</code>, <code>SMEMBERS</code>, <code>ZRANGE 0 -1</code>), deleting a large key synchronously, long Lua scripts, or the latency of <code>fork()</code> for persistence on a large dataset. It also caps one instance at one core&rsquo;s worth of command execution; beyond that you shard with Redis Cluster.",
        ),
        question(
            "How would you build a real-time leaderboard of the top 100 among 10 million players, including &ldquo;what is my rank?&rdquo;",
            "medium",
            "A sorted set with the score as the score and the player ID as the member. <code>ZADD board score player</code> (or <code>ZINCRBY</code>) updates in O(log n). <code>ZREVRANGE board 0 99 WITHSCORES</code> returns the top 100 in O(log n + 100). <code>ZREVRANK board player</code> returns a player&rsquo;s rank in O(log n), which works because the skiplist stores span counts on each link.",
            "Details worth raising: ties are ordered by member name lexicographically, so encode a tie-breaker into the score if &ldquo;who got there first&rdquo; matters (for example <code>score * 1e10 + (MAX_TS - ts)</code>, staying within a double&rsquo;s 53-bit precision). For time-windowed boards keep one set per day and use <code>ZUNIONSTORE</code> for weekly views. At 10 million members the set is roughly 1&nbsp;GB; if it outgrows one node, shard by score range or keep only the top N in Redis.",
        ),
        question(
            "Compare RDB and AOF persistence. If you run Redis as a primary store, what configuration would you choose and what can you still lose?",
            "hard",
            "RDB: periodic forked snapshots, compact and fast to load, but you lose everything since the last snapshot, and each fork costs page-table copying and copy-on-write memory. AOF: logs each write; with <code>appendfsync everysec</code> you lose at most about a second, with <code>always</code> nothing acknowledged but with a large write-latency cost. AOF rewrites keep the file bounded.",
            "For a primary store: AOF with <code>everysec</code> (or <code>always</code> if the latency budget allows) plus <code>aof-use-rdb-preamble yes</code> for fast restarts, periodic RDB snapshots shipped off the machine for backups, replicas for availability, and <code>WAIT</code> for writes that must reach a replica.",
            "What you can still lose: up to a second of writes on a crash with <code>everysec</code>; writes acknowledged by the primary but not yet replicated when a failover promotes a replica (replication is asynchronous, so a promoted replica can be behind); and everything if the disk lies about fsync. Redis is not a consensus-replicated database, and interviewers want to hear that you know it.",
        ),
        question(
            "Why does Redis approximate LRU instead of implementing it exactly? How good is the approximation?",
            "hard",
            "Exact LRU needs a doubly linked list over all keys, which costs two pointers (16 bytes) per key &mdash; significant when many values are themselves only tens of bytes &mdash; and a list splice on every read, which writes to memory on read-only operations and hurts cache behaviour.",
            "Redis instead stores a 24-bit timestamp in each object header, which it already has room for, and at eviction time samples <code>maxmemory-samples</code> keys (default 5), evicting the oldest, with a 16-entry pool that carries good candidates over to the next eviction. With 5 samples the hit ratio is within a few percent of true LRU on realistic skewed workloads; with 10 it is almost indistinguishable. The same header field holds the LFU state (an 8-bit logarithmic counter plus a decay time) when an LFU policy is selected, which is often better for caches whose popularity is stable.",
        ),
        question(
            "Implement a rate limiter of 100 requests per user per minute with Redis. What are the trade-offs between approaches?",
            "hard",
            "<strong>Fixed window:</strong> <code>INCR rate:{user}:{minute}</code>, <code>EXPIRE</code> on first increment; reject when over 100. One key and O(1), but a burst of 100 at 12:00:59 and 100 at 12:01:00 lets 200 through in two seconds.",
            "<strong>Sliding log:</strong> a sorted set per user with the request timestamp as score. In one <code>MULTI</code> or Lua script: <code>ZREMRANGEBYSCORE key 0 now-60s</code>, <code>ZCARD</code>, and if under the limit <code>ZADD key now id</code>. Exact, but memory grows with the limit (100 entries per active user).",
            "<strong>Sliding window counter:</strong> keep this minute&rsquo;s and last minute&rsquo;s counts and weight the previous one by how much of it overlaps the window. Two integers per user and close to exact.",
            "<strong>Token bucket:</strong> store tokens and last-refill time in a hash and refill lazily in a Lua script. Allows controlled bursts and is the usual choice for APIs.",
            "Whatever the algorithm, the check and the update must be atomic &mdash; one Lua script or <code>MULTI</code> &mdash; or two concurrent requests both see 99 and both pass.",
        ),
    ],
    refs=[
        ("Redis docs: key eviction", "https://redis.io/docs/latest/develop/reference/eviction/"),
        ("Redis docs: persistence", "https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/"),
        ("Redis docs: memory optimisation", "https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/memory-optimization/"),
        ("Redis source: dict.c (incremental rehashing)", "https://github.com/redis/redis/blob/unstable/src/dict.c"),
        ("Pugh — Skip Lists: A Probabilistic Alternative to Balanced Trees", "https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf"),
    ],
)
