from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="caching",
    title="Caching Patterns",
    summary="Cache-aside, write-through and write-back, TTLs, stampedes, hot keys, and keeping a cache honest.",
    intro=[
        "A cache puts a copy of data somewhere faster than its source &mdash; process memory, Redis, a CDN &mdash; so most reads never reach the database. The speed-up is easy. The hard parts are the ones interviewers ask about: when the copy disagrees with the source, what happens when a popular entry expires under load, and what to do when one key is hotter than any single machine.",
        "The Redis page covered eviction policies. This page is about the patterns that sit around any cache, and the failure modes each one has.",
    ],
    sections=[
        section(
            "Cache-aside, write-through, write-back",
            table(
                ["Pattern", "Read path", "Write path", "Consistency risk", "Used for"],
                [
                    ["<strong>Cache-aside</strong> (lazy loading)", "App checks cache; on miss reads DB and fills cache", "App writes DB, then deletes (or updates) the cache entry", "Races can leave stale entries until TTL", "The default for most web and service caches"],
                    ["<strong>Read-through</strong>", "Cache itself loads from DB on miss", "(paired with one of the below)", "As cache-aside, but centralised", "Caching libraries and proxies"],
                    ["<strong>Write-through</strong>", "Cache always populated", "Write cache and DB together, synchronously", "Low; writes are slower", "Read-heavy data that must be fresh"],
                    ["<strong>Write-back</strong> (write-behind)", "Cache always populated", "Write cache only; flush to DB later in batches", "Data loss if the cache dies before flushing", "Write-heavy counters, metrics; CPU caches; buffer pools"],
                    ["<strong>Write-around</strong>", "Cache-aside", "Write DB only; do not touch cache", "Next read of new data misses", "Data written once and rarely read soon after"],
                ],
            ),
            code('''
                class DB:
                    def __init__(self):
                        self.rows, self.writes = {}, 0
                    def put(self, k, v):
                        self.rows[k] = v
                        self.writes += 1

                def write_through(updates):
                    db, cache = DB(), {}
                    for k, v in updates:
                        cache[k] = v
                        db.put(k, v)                       # every write reaches the DB now
                    return db, cache, {}

                def write_back(updates, flush_every=50):
                    db, cache, dirty = DB(), {}, {}
                    for i, (k, v) in enumerate(updates, 1):
                        cache[k] = v
                        dirty[k] = v                        # only the latest value per key
                        if i % flush_every == 0:
                            for dk, dv in dirty.items():
                                db.put(dk, dv)
                            dirty.clear()
                    return db, cache, dirty

                # 230 position updates spread over 5 symbols
                updates = [(f"S{i % 5}", i) for i in range(230)]
                for name, f in (("write-through", write_through), ("write-back", write_back)):
                    db, cache, dirty = f(updates)
                    print(f"{name:<13} DB writes: {db.writes:>3}   lost if the cache dies now: {sorted(dirty)}")
            ''', label="write-through vs write-back: DB load against exposure to loss"),
            "Write-back coalesced 230 updates into 20 database writes, because only the latest value per key is flushed. The price is the list on the right: updates acknowledged to the caller that exist only in cache memory.",
        ),
        section(
            "Cache invalidation and the stale-read race",
            "The standard cache-aside write is: update the database, then <strong>delete</strong> the cache entry (so the next read reloads it). Deleting is preferred to updating the cache because two concurrent writers updating the cache can apply their values in the opposite order from the database. But even delete-after-write has a race with a concurrent reader that missed:",
            code('''
                db = {"px:AAPL": 227.0}
                cache = {}
                log = []

                def step(who, what):
                    log.append(f"{who:<7} {what}")

                # reader misses and reads the DB ...
                value = db["px:AAPL"];                 step("reader", f"miss, reads DB -> {value}")
                # ... writer updates the DB and invalidates the (empty) cache ...
                db["px:AAPL"] = 229.5;                 step("writer", "writes DB -> 229.5")
                cache.pop("px:AAPL", None);            step("writer", "deletes cache entry")
                # ... reader, delayed (GC pause, slow network), now fills the cache
                cache["px:AAPL"] = value;              step("reader", f"sets cache -> {value}")

                print("\\n".join(log))
                print(f"DB says {db['px:AAPL']}, cache says {cache['px:AAPL']} (stale until TTL)")
            ''', label="a slow reader repopulates the cache with an old value"),
            "Mitigations, in increasing strength:",
            "<strong>TTL on every entry</strong>, so any staleness is bounded. Always do this; it is the safety net for every bug you have not found.<br><strong>Delayed double delete</strong>: delete, then delete again a short time later to catch a racing reader. Cheap, heuristic.<br><strong>Versioned or conditional sets</strong>: store a version (row version, LSN, timestamp) with the value and only set if the cached version is older (a Lua script in Redis). A reader carrying an old version cannot overwrite a newer one.<br><strong>Lease / invalidation tokens</strong> (Facebook&rsquo;s memcache): a miss hands out a lease token; a delete invalidates outstanding leases, so the slow reader&rsquo;s set is rejected.<br><strong>Invalidate from the change stream</strong>: a consumer of the database&rsquo;s CDC log deletes cache keys, so invalidation cannot be skipped by a code path that forgets.",
            note("&ldquo;There are only two hard things in computer science: cache invalidation and naming things.&rdquo; If a stale value is unacceptable &mdash; balances, positions, risk limits &mdash; do not serve it from a cache that is invalidated asynchronously."),
        ),
        section(
            "TTL and expiry",
            "A TTL bounds staleness and lets unused entries fall out. Choosing it is a trade between freshness (short) and hit ratio and database load (long). Two refinements matter at scale:",
            "<strong>Jitter.</strong> If many keys are written at the same moment with the same TTL &mdash; a deploy warming the cache, a nightly batch &mdash; they all expire at the same moment too, and the database takes the whole reload at once. Add randomness to every TTL:",
            code('''
                import random
                from collections import Counter

                random.seed(8)
                KEYS, TTL = 10_000, 300                         # all cached at t=0 by a warm-up job

                fixed = Counter(TTL for _ in range(KEYS))
                jittered = Counter(TTL + random.randint(-30, 30) for _ in range(KEYS))

                print(f"fixed TTL:    worst second has {max(fixed.values()):>6,} expiries")
                print(f"TTL +/- 10%:  worst second has {max(jittered.values()):>6,} expiries")
            ''', label="synchronised expiry vs jittered TTLs"),
            "<strong>Refresh ahead.</strong> For hot keys, refresh the value in the background shortly before it expires, so readers never see a miss. Probabilistic early expiration (the XFetch algorithm) does this without coordination: each reader, with a probability that rises as expiry approaches, decides to recompute early, so one request refreshes the value while the rest keep reading the old one.",
        ),
        section(
            "Cache stampede",
            "A <strong>stampede</strong> (dog-pile, thundering herd) happens when a popular key expires or is evicted and every concurrent request misses at once. Each one runs the same expensive query, and a database that was comfortably serving the cache&rsquo;s misses is suddenly asked for the same row a thousand times.",
            "The fix is <strong>request coalescing</strong> (single-flight): the first request to miss takes a per-key lock and loads the value; everyone else waits for that result instead of querying the database themselves. Across processes the lock is a short-lived Redis key set with <code>SET key token NX PX 5000</code>; within a process it is a mutex or a shared future.",
            code('''
                import threading, time

                def run(coalesce, clients=50):
                    db_queries = 0
                    cache = {}
                    counter_lock = threading.Lock()
                    inflight = {}                             # key -> Event for the one loader
                    inflight_lock = threading.Lock()
                    start = threading.Barrier(clients)

                    def load(key):
                        nonlocal db_queries
                        with counter_lock:
                            db_queries += 1
                        time.sleep(0.2)                       # an expensive query
                        return f"value of {key}"

                    def get(key):
                        start.wait()                          # everyone misses at the same instant
                        if key in cache:
                            return cache[key]
                        if not coalesce:
                            cache[key] = load(key)
                            return cache[key]
                        with inflight_lock:
                            event = inflight.get(key)
                            leader = event is None
                            if leader:
                                event = inflight[key] = threading.Event()
                        if leader:
                            cache[key] = load(key)
                            event.set()
                        else:
                            event.wait()
                        return cache[key]

                    threads = [threading.Thread(target=get, args=("hot",)) for _ in range(clients)]
                    for t in threads: t.start()
                    for t in threads: t.join()
                    return db_queries

                print("50 concurrent misses, no coalescing:  ", run(coalesce=False), "DB queries")
                print("50 concurrent misses, single-flight:  ", run(coalesce=True), "DB query")
            ''', label="a hot key expires under 50 concurrent requests"),
            "Other defences: serve the stale value while one request refreshes it (<em>stale-while-revalidate</em>), refresh hot keys ahead of expiry, and never let an empty or failing backend turn into a cache of errors &mdash; cache negative results briefly, but not exceptions.",
            caveat("A distributed lock for coalescing must have a timeout, and the loader must not assume it still holds the lock when it finishes: if it paused past the timeout, another loader may have started. The worst outcome is a duplicate load, which is acceptable; do not use the same lock to protect correctness."),
        ),
        section(
            "Hot keys",
            "Sharding a cache spreads keys, not load. A single key that receives a large fraction of all traffic &mdash; the current price of the most traded instrument, a global configuration blob, a celebrity profile &mdash; is served by one shard, whose CPU or network link saturates while the rest of the cluster idles.",
            table(
                ["Technique", "How", "Cost"],
                [
                    ["Local (L1) cache", "Keep hot keys in each application process for a short time (100&nbsp;ms&ndash;seconds) in front of the shared cache", "Staleness up to the local TTL; memory per process"],
                    ["Key replication", "Store copies as <code>key#0</code> &hellip; <code>key#N</code> on different shards; readers pick one at random", "Writes and invalidations must touch every copy"],
                    ["Read replicas", "Add replicas of the hot shard and spread reads over them", "Replication lag"],
                    ["Push instead of pull", "For values everyone needs (a price, a config), broadcast updates to subscribers rather than having all of them poll", "A pub/sub or multicast channel to operate"],
                    ["Detect first", "Sample request keys (Redis <code>--hotkeys</code> with LFU, client-side counters) to find hot keys before they hurt", "Monitoring work"],
                ],
            ),
            "In market-data systems the last two rows are the norm: prices are pushed over multicast or a message bus to every consumer, which keeps its own in-memory copy. Pulling the same hot key from a shared cache ten thousand times a second is the anti-pattern the cache was supposed to prevent.",
        ),
    ],
    questions=[
        question(
            "With cache-aside, should a write update the cache or delete the entry? Why?",
            "medium",
            "Delete it. With two concurrent writers, updating both the database and the cache opens a race: writer A writes the DB, writer B writes the DB, B updates the cache, then A updates the cache. The DB holds B&rsquo;s value and the cache holds A&rsquo;s, indefinitely. Deleting has no ordering problem: whichever delete runs last, the next read reloads the current value from the database.",
            "Deleting also avoids computing a cache value that may never be read, which matters when the cached form is expensive (a rendered page, an aggregate).",
            "Delete-after-write is still not perfect: a reader that missed and read the old value before the write can set the cache after the delete. Bound it with a TTL, and close it with versioned sets or lease tokens if staleness is not acceptable.",
        ),
        question(
            "What is a cache stampede and how do you prevent it?",
            "medium",
            "When a popular key expires or is evicted, all concurrent requests for it miss at the same instant and each queries the database for the same value. Load on the database spikes by the key&rsquo;s request rate, often enough to slow or topple it, which makes the reloads slower, which lets even more requests pile up.",
            "Prevention: <strong>request coalescing</strong> so only one caller loads a key while others wait for its result (a per-key mutex in-process, <code>SET NX PX</code> lock across processes); <strong>serve stale while revalidating</strong>, so readers get the old value while one refresh runs; <strong>refresh ahead</strong> or probabilistic early expiration for hot keys; and <strong>TTL jitter</strong> so that keys written together do not all expire together.",
        ),
        question(
            "When would you choose write-back over write-through, and what are the risks?",
            "hard",
            "Write-back when writes are frequent, individually low-value and coalesce well: counters, view counts, rate-limit state, metrics, a position that changes on every tick but is only persisted periodically. Many updates to the same key collapse into one database write, and the write path has cache latency rather than database latency.",
            "Risks: <strong>data loss</strong> &mdash; anything not yet flushed is lost if the cache node fails, so the cache itself must be replicated or the data must be reconstructible from another source (such as an event log); <strong>ordering and consistency</strong> &mdash; other readers of the database see stale data until the flush, and flushes must preserve per-key order; <strong>complexity</strong> &mdash; tracking dirty entries, backpressure when the database is slow, and draining on shutdown.",
            "Write-through when the database must always be current (other systems read it directly) and the write rate is modest; its cost is that every write pays database latency.",
        ),
        question(
            "A trading dashboard shows positions cached in Redis with a 5-second TTL. Risk says positions must never be more than 100&nbsp;ms stale. What do you change?",
            "hard",
            "A TTL only bounds staleness from above, and a 100&nbsp;ms TTL on every position would push most reads back to the database. The better model is to stop polling and push: the position service that owns the positions (and applies fills) publishes each change on a stream or pub/sub channel, and the dashboard service keeps positions in memory and applies updates as they arrive. Staleness is then the end-to-end latency of the update pipeline, typically milliseconds, and can be measured by stamping updates with their source time.",
            "If a cache must remain, update it from the same place that updates the position, in order &mdash; the owner writes through to Redis as part of applying the fill &mdash; rather than invalidating from application code, and version each entry by fill sequence number so an out-of-order update cannot regress it. Keep a TTL as a safety net, and alert when the age of the newest update exceeds the 100&nbsp;ms budget, so staleness is a monitored property rather than an assumption.",
        ),
    ],
    refs=[
        ("Nishtala et al. — Scaling Memcache at Facebook", "https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf"),
        ("Vattani et al. — Optimal Probabilistic Cache Stampede Prevention (XFetch)", "https://cseweb.ucsd.edu/~avattani/papers/cache_stampede.pdf"),
        ("AWS whitepaper: database caching strategies using Redis", "https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/welcome.html"),
        ("RFC 5861 — stale-while-revalidate and stale-if-error", "https://www.rfc-editor.org/rfc/rfc5861"),
    ],
)
