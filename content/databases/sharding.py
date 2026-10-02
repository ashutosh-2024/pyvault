from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="sharding",
    title="Partitioning and Sharding",
    summary="Hash vs range partitioning, consistent hashing, hot partitions, rebalancing and cross-shard queries.",
    intro=[
        "Replication copies the same data to many machines. Partitioning (sharding) splits <em>different</em> data across machines, so that the dataset and the write load can exceed what one node can handle. Most real systems do both: each partition is replicated.",
        "The whole subject turns on one function &mdash; key to partition &mdash; and on what happens to it when you add a machine, when one key is far more popular than the rest, or when a query needs data from every partition.",
    ],
    sections=[
        section(
            "Hash partitioning vs range partitioning",
            table(
                ["", "Hash partitioning", "Range partitioning"],
                [
                    ["Rule", "partition = hash(key) mod P, or a hash range", "Each partition owns a contiguous key range"],
                    ["Load spread", "Even, for any key distribution", "Only as even as the keys; sequential keys all hit the last range"],
                    ["Range queries", "Scatter to every partition", "Touch only the partitions covering the range"],
                    ["Examples", "Cassandra, DynamoDB, Redis Cluster (16,384 hash slots), MongoDB hashed shard keys", "HBase, Bigtable, Spanner, CockroachDB, TiDB, MongoDB ranged shard keys"],
                ],
            ),
            code('''
                import hashlib
                from collections import Counter

                P = 4
                # trades keyed by a timestamp: every new key is larger than the last
                keys = [f"2026-09-30T09:{m:02d}:{s:02d}" for m in range(30, 60) for s in range(60)]
                recent = keys[-300:]                                    # the last five minutes

                def by_hash(k):
                    return int(hashlib.md5(k.encode()).hexdigest(), 16) % P

                bounds = [keys[len(keys) * i // P] for i in range(1, P)]  # split into P equal ranges
                def by_range(k):
                    return sum(k >= b for b in bounds)

                for name, f in (("hash", by_hash), ("range", by_range)):
                    load = Counter(f(k) for k in recent)
                    print(f"{name:<5} writes in the last 5 min per partition: {[load[p] for p in range(P)]}")
            ''', label="sequential keys: range partitioning puts all new writes on one node"),
            "Timestamps, auto-increment IDs and anything else monotonic concentrate all current writes on the newest range. Range-partitioned systems deal with it by prefixing the key with something that spreads it (a hashed bucket, the instrument ID) at the cost of losing a single global time order &mdash; or by accepting it, as time-series databases do, since the newest partition is also the one being read.",
            "Hash partitioning also has a compound-key middle ground: Cassandra hashes only the first part of the primary key (the partition key) and sorts rows within a partition by the rest (clustering columns). <code>PRIMARY KEY ((symbol, day), ts)</code> spreads load by symbol and day while keeping each day&rsquo;s trades for one symbol sorted and together.",
        ),
        section(
            "Rebalancing, and why not hash mod N",
            "Partitioning by <code>hash(key) mod N</code>, where N is the number of nodes, has a fatal flaw: changing N changes the answer for almost every key. Adding one node to ten moves about 91% of the data, all at once.",
            code('''
                import hashlib

                def h(k):
                    return int(hashlib.md5(k.encode()).hexdigest(), 16)

                keys = [f"user{i}" for i in range(100_000)]
                for n in (4, 10, 50):
                    moved = sum(h(k) % n != h(k) % (n + 1) for k in keys)
                    print(f"mod {n:>2} -> mod {n + 1:>2}: {moved / len(keys):.0%} of keys move "
                          f"(ideal: {1 / (n + 1):.0%})")
            ''', label="adding one node under mod-N placement"),
            "Two standard fixes:",
            "<strong>Fixed number of partitions.</strong> Create many more partitions than nodes up front (say 1,000 for 10 nodes, or Redis Cluster&rsquo;s 16,384 slots) and assign whole partitions to nodes. <code>hash(key) mod 1000</code> never changes; adding a node just moves some whole partitions to it. Used by Redis Cluster, Elasticsearch, Couchbase, Riak.<br><strong>Consistent hashing</strong> (next section), which moves only about 1/N of the keys when a node joins or leaves.<br><strong>Dynamic splitting</strong> for range partitions: split a range when it grows past a size threshold and move one half. Used by HBase, Bigtable, CockroachDB, MongoDB.",
            note("Rebalancing moves real data over the network while serving traffic. Automatic rebalancing on node-failure detection can turn a slow node into a cascading overload; many operators keep a human in the loop for it."),
        ),
        section(
            "Consistent hashing",
            "Place both nodes and keys on a ring of hash values. Each key belongs to the first node clockwise from its position. When a node joins, it takes over only the keys between itself and its predecessor; when one leaves, only its keys move to its successor. Everything else stays put.",
            "With one position per node, the arcs are wildly uneven. The fix is <strong>virtual nodes</strong>: each physical node takes many positions on the ring, so its total share averages out, and when it leaves, its keys spread across many other nodes instead of landing on one neighbour.",
            code('''
                import bisect, hashlib
                from collections import Counter

                def h(s):
                    return int(hashlib.md5(s.encode()).hexdigest(), 16)

                class Ring:
                    def __init__(self, nodes, vnodes):
                        self.points = sorted((h(f"{n}#{v}"), n) for n in nodes for v in range(vnodes))
                        self.hashes = [p for p, _ in self.points]

                    def owner(self, key):
                        i = bisect.bisect(self.hashes, h(key)) % len(self.points)
                        return self.points[i][1]

                keys = [f"order{i}" for i in range(50_000)]
                nodes = ["A", "B", "C", "D"]
                for vnodes in (1, 10, 200):
                    before = Ring(nodes, vnodes)
                    load = Counter(before.owner(k) for k in keys)
                    after = Ring(nodes + ["E"], vnodes)
                    moved = sum(before.owner(k) != after.owner(k) for k in keys)
                    shares = " ".join(f"{n}:{load[n] / len(keys):>4.0%}" for n in nodes)
                    print(f"vnodes={vnodes:<4} load {shares}   add E -> {moved / len(keys):.0%} of keys move")
            ''', label="load balance and data movement on a hash ring"),
            "With one point per node the load is badly skewed. With a couple of hundred virtual nodes each node holds close to a quarter, and adding a fifth node moves close to the ideal fifth of the keys &mdash; taken from all four existing nodes rather than from a single neighbour.",
            caveat("Other schemes reach the same goal: <em>rendezvous (highest-random-weight) hashing</em> scores every node for each key and picks the highest, with no ring to maintain; <em>jump consistent hash</em> maps a key to one of N buckets with no memory at all, but only supports adding or removing the last bucket."),
        ),
        section(
            "Hot partitions and hot keys",
            "Even hashing only spreads <em>keys</em> evenly. If one key receives a large share of the traffic &mdash; a celebrity account, the most traded symbol at the open, a global counter &mdash; its partition becomes the bottleneck no matter how many nodes you add.",
            code('''
                import random, zlib
                from collections import Counter

                random.seed(2)
                P = 8
                symbols = [f"SYM{i}" for i in range(400)]
                weights = [60 if s == "SYM0" else 1 for s in symbols]     # one symbol is hot
                trades = random.choices(symbols, weights, k=40_000)

                def partition(key):
                    return zlib.crc32(key.encode()) % P

                plain = Counter(partition(s) for s in trades)
                salted = Counter(partition(f"{s}#{random.randrange(8)}" if s == "SYM0" else s)
                                 for s in trades)

                for name, load in (("plain", plain), ("salted", salted)):
                    loads = [load[p] for p in range(P)]
                    print(f"{name:<6} {loads}   max/avg = {max(loads) / (sum(loads) / P):.2f}")
            ''', label="one hot symbol, and splitting it across sub-keys"),
            "<strong>Salting</strong> (appending a small random suffix to a known hot key) spreads its writes over several partitions. The price is on the read side: reading that key now means reading all its sub-keys and combining them. It suits counters and append-only events well; it suits &ldquo;read the current value&rdquo; badly.",
            "Other tools: a cache in front of hot reads (with request coalescing, see the caching page); splitting a hot range more finely than its size alone would justify (DynamoDB and CockroachDB split on load, not just size); and, for write-hot counters, buffering increments locally and flushing them in batches.",
        ),
        section(
            "Cross-shard queries and transactions",
            "Partitioning is cheap exactly as long as each request touches one partition. Everything else costs:",
            table(
                ["Operation", "What happens", "Cost"],
                [
                    ["Lookup by partition key", "Route to one shard", "One network hop"],
                    ["Query by a non-key column", "Scatter to every shard, gather and merge", "Latency of the slowest shard; load on all of them"],
                    ["Secondary index, local (document-partitioned)", "Each shard indexes its own rows; queries still scatter", "Cheap writes, expensive reads"],
                    ["Secondary index, global (term-partitioned)", "The index is itself partitioned by the indexed value", "Cheap reads, but every write updates a remote index shard (usually asynchronously)"],
                    ["Join across shards", "Ship one side to the other, or both to a coordinator", "Network-bound; avoid on the hot path"],
                    ["Transaction across shards", "Two-phase commit (or a consensus-backed variant)", "Extra round trips; blocking if the coordinator fails mid-protocol"],
                ],
            ),
            "The design response is to choose the partition key so that the common access patterns stay local. Co-locate related data: shard orders, fills and positions all by account, so an account&rsquo;s transaction never leaves its shard. Accept that some queries &mdash; &ldquo;total exposure across all accounts&rdquo; &mdash; will scatter, and serve them from a separate analytical copy rather than from the OLTP shards.",
            code('''
                import heapq

                # each shard returns its own top 3 by notional, already sorted
                shards = {
                    "shard0": [("acct7", 9_400), ("acct2", 7_100), ("acct11", 3_000)],
                    "shard1": [("acct4", 12_800), ("acct9", 9_900), ("acct1", 900)],
                    "shard2": [("acct5", 8_800), ("acct3", 8_700), ("acct8", 8_600)],
                }
                merged = heapq.merge(*shards.values(), key=lambda r: r[1], reverse=True)
                print("global top 3:", list(merged)[:3])
            ''', label="scatter-gather: top N across shards needs top N from each"),
            "Each shard must return its own top N, not just its top 1, because the global top three can all live on one shard. Here two of them do: had each shard sent only its best row, <code>acct9</code> would have been missed. The same reasoning makes <code>LIMIT</code>/<code>OFFSET</code> across shards painful: page 100 needs 100 pages&rsquo; worth of rows from every shard.",
        ),
    ],
    questions=[
        question(
            "Why is <code>hash(key) % N</code> a bad sharding function, and what do you use instead?",
            "medium",
            "Because N changes. Going from N to N+1 nodes reassigns roughly N/(N+1) of all keys &mdash; about 90% when going from 10 to 11 &mdash; so adding capacity means moving nearly the whole dataset at once, exactly when the system is under load.",
            "Alternatives: a <strong>fixed, large number of partitions</strong> (hash mod 16,384, as in Redis Cluster) mapped to nodes through a table, so adding a node moves whole partitions; <strong>consistent hashing</strong> with virtual nodes, which moves about 1/(N+1) of keys evenly from all existing nodes; or <strong>range partitions that split dynamically</strong>. All three decouple the key-to-partition function from the node count.",
        ),
        question(
            "What are virtual nodes in consistent hashing and what problems do they solve?",
            "medium",
            "Each physical node is placed on the ring at many positions (tens to hundreds) instead of one. That solves three problems. <strong>Uneven load</strong>: with one position per node, random placement gives some nodes arcs several times larger than others; many positions average out. <strong>Uneven recovery</strong>: when a node leaves, its keys would all move to its single successor, doubling that node&rsquo;s load; with virtual nodes they scatter across the whole cluster. <strong>Heterogeneous hardware</strong>: a node with twice the capacity simply gets twice as many virtual nodes.",
            "The cost is a larger ring to store and search (a sorted array with binary search makes that trivial) and more, smaller ranges to track when streaming data during rebalancing.",
        ),
        question(
            "Design the sharding scheme for an order management system that stores orders, fills and positions for 50,000 accounts. What is the shard key and what queries become expensive?",
            "hard",
            "Shard by <strong>account ID</strong>, hashed into a fixed number of logical partitions mapped onto physical nodes. Orders, fills and positions for one account are co-located, so the core transaction &mdash; record a fill and update the position &mdash; is single-shard and needs no distributed commit. Risk checks per account are local too.",
            "Expensive: anything across accounts. Firm-wide exposure per symbol, &ldquo;all open orders for symbol X&rdquo; (needed for a symbol halt or a mass cancel), and end-of-day reports all scatter to every shard. Serve those from a separate store fed by change-data-capture: a per-symbol aggregate maintained in a stream processor, and a columnar warehouse for reporting.",
            "Also discuss hot accounts: a market-making account can generate orders of magnitude more traffic than the median. Options are giving it a dedicated partition, or splitting its orders by strategy or symbol as a sub-key while keeping its position aggregate on one partition. Re-sharding when an account outgrows its partition should move a whole logical partition, never re-hash.",
        ),
        question(
            "How do secondary indexes work in a sharded database, and what are the trade-offs between local and global indexes?",
            "hard",
            "<strong>Local (document-partitioned) index:</strong> each shard indexes only its own rows. Writes stay on one shard and the index is always consistent with its data. But a query by the indexed column has no idea which shard holds matches, so it scatters to all of them &mdash; tail latency is set by the slowest shard, and the cost of that query grows with cluster size. MongoDB, Cassandra (native secondary indexes) and Elasticsearch work this way.",
            "<strong>Global (term-partitioned) index:</strong> the index is partitioned by the <em>indexed value</em>, so all entries for <code>symbol = 'ABC'</code> live on one index shard. Reads go to one place. But a write to a row may have to update index shards on other nodes, which is either a distributed transaction (slow) or asynchronous (so the index lags the data). DynamoDB global secondary indexes are asynchronous; Spanner and CockroachDB keep them transactional.",
            "Choose local indexes for write-heavy data where indexed queries are rare or always include the shard key; global ones where lookups by the secondary attribute are frequent and latency-sensitive.",
        ),
        question(
            "A single partition in your cluster is running at 100% CPU while the others are at 10%. Walk through diagnosing and fixing it.",
            "hard",
            "First, is it a <strong>hot key</strong> or a <strong>hot range</strong>? Look at per-key request metrics or sample traffic on that node. A single key dominating (a popular symbol, a global counter, a misbehaving client retrying one request) is different from many keys that happen to share a range (monotonically increasing keys all landing on the newest range partition).",
            "Hot range: split the range, and if the cause is sequential keys, change the key design (prefix with a hash bucket or a high-cardinality attribute). Hot key, read-heavy: cache it in front of the database with request coalescing so a thundering herd becomes one read, or replicate the hot key&rsquo;s partition more and read from replicas. Hot key, write-heavy: salt it into sub-keys and aggregate on read, or batch updates in the application and write them periodically.",
            "Also rule out the non-data causes: a compaction or repair running only on that node, a bad disk, a noisy neighbour, or a skewed client that pins connections to one node.",
        ),
    ],
    refs=[
        ("Karger et al. — Consistent Hashing and Random Trees", "https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf"),
        ("DeCandia et al. — Dynamo: Amazon's Highly Available Key-value Store", "https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf"),
        ("Redis: cluster specification (hash slots)", "https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/"),
        ("Lamping and Veach — A Fast, Minimal Memory, Consistent Hash Algorithm", "https://arxiv.org/abs/1406.2294"),
        ("MongoDB: choosing a shard key", "https://www.mongodb.com/docs/manual/core/sharding-choose-a-shard-key/"),
    ],
)
