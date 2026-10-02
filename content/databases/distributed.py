from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="distributed",
    title="Distributed Databases and Replication",
    summary="Leader/follower replication, sync vs async, quorums, failover, CAP, and split brain.",
    intro=[
        "Copying data to several machines buys availability, read scaling and geographic locality. It also means the copies can disagree, and every distributed database is a set of decisions about what happens when they do. The interview questions in this area are really about those decisions: what can a client observe, what can be lost, and who is allowed to accept writes after a failure.",
        "The examples are small, deterministic simulations of replicas and networks. Real systems add retries, timeouts and clocks, but the failure modes are exactly these.",
    ],
    sections=[
        section(
            "Replication topologies",
            table(
                ["Topology", "Writes go to", "Used by", "Main hazard"],
                [
                    ["Single leader (primary/replica)", "One leader; followers apply its log", "PostgreSQL, MySQL, MongoDB replica sets, Redis", "Failover: who becomes leader, and what was lost"],
                    ["Multi-leader", "Any of several leaders (often one per region)", "MySQL group replication (multi-primary), CouchDB, BDR", "Concurrent conflicting writes must be merged"],
                    ["Leaderless", "Any replica; client writes to several", "Cassandra, ScyllaDB, DynamoDB-style stores, Riak", "Stale reads unless quorums overlap; read repair"],
                    ["Consensus groups", "Leader elected by Raft/Paxos; commit needs a majority", "etcd, CockroachDB, TiDB, Spanner, YugabyteDB", "Latency of a majority round trip; unavailable without a majority"],
                ],
            ),
            "Single-leader replication is by far the most common, and most questions assume it. The leader writes changes to its log (the WAL, a binlog, an oplog) and streams the log to followers, which apply it in the same order. Because every follower applies the same deterministic sequence, they converge to the leader&rsquo;s state &mdash; eventually.",
            caveat("Statement-based replication (shipping the SQL text) breaks on non-deterministic statements such as <code>NOW()</code>, <code>RAND()</code> or <code>UPDATE ... LIMIT</code> without <code>ORDER BY</code>. Modern systems ship either physical WAL records or logical row-level changes."),
        ),
        section(
            "Synchronous vs asynchronous replication",
            "The key decision is when the leader tells the client &ldquo;committed&rdquo;:",
            table(
                ["Mode", "Commit acknowledged after", "Lose data on leader failure?", "Latency and availability"],
                [
                    ["Asynchronous", "The leader&rsquo;s own WAL is durable", "Yes: whatever had not reached a follower", "Fastest; unaffected by slow followers"],
                    ["Synchronous (all)", "Every follower confirms", "No", "As slow as the slowest follower; any follower down blocks writes"],
                    ["Semi-synchronous / quorum", "At least one (or k) followers confirm", "No, if failover picks a confirmed follower", "Pays one network round trip; tolerates slow stragglers"],
                ],
            ),
            code('''
                class Replica:
                    def __init__(self, name):
                        self.name, self.log = name, []

                def run(mode):
                    leader, f1, f2 = Replica("leader"), Replica("f1"), Replica("f2")
                    acked = []
                    for i in range(1, 7):
                        write = f"order-{i}"
                        leader.log.append(write)
                        if i <= 5: f1.log.append(write)       # f1 is one write behind
                        if i <= 3: f2.log.append(write)       # f2 is slow
                        confirmations = sum(write in f.log for f in (f1, f2))
                        needed = {"async": 0, "semi-sync": 1, "sync": 2}[mode]
                        if confirmations >= needed:
                            acked.append(write)
                    # leader dies; promote the most up-to-date follower
                    new_leader = max((f1, f2), key=lambda f: len(f.log))
                    lost = [w for w in acked if w not in new_leader.log]
                    return len(acked), new_leader.name, lost

                for mode in ("async", "semi-sync", "sync"):
                    n, who, lost = run(mode)
                    print(f"{mode:<9} acked {n} writes; promote {who}; acknowledged but lost: {lost or 'none'}")
            ''', label="a leader crashes: which acknowledged writes survive?"),
            "Async acknowledged all six and lost one. Semi-sync only acknowledged writes a follower had, so promoting the most up-to-date follower lost nothing, but the client was told &ldquo;not yet&rdquo; about order 6 (in reality it would wait, and eventually time out). Full sync acknowledged only three, because the slow follower held everything up.",
            "PostgreSQL expresses this with <code>synchronous_standby_names = 'ANY 1 (f1, f2)'</code> and <code>synchronous_commit</code>; MySQL with semi-synchronous replication and <code>rpl_semi_sync_master_wait_for_slave_count</code>.",
            note("With asynchronous replication, &ldquo;committed&rdquo; means &ldquo;committed on one machine&rdquo;. If losing the last second of acknowledged trades after a failover is unacceptable, you need at least one synchronous follower, and a failover procedure that only promotes one that is caught up."),
        ),
        section(
            "Quorums",
            "Leaderless systems replicate each key to <em>N</em> nodes. A write is acknowledged once <em>W</em> of them accept it; a read asks <em>R</em> of them and takes the value with the newest version. If <strong>R + W &gt; N</strong>, every read set overlaps every write set in at least one node, so the read sees the latest acknowledged write.",
            code('''
                from itertools import combinations

                N = 3
                nodes = range(N)

                def always_fresh(R, W):
                    """Does every possible read quorum overlap every possible write quorum?"""
                    return all(set(r) & set(w)
                               for w in combinations(nodes, W)
                               for r in combinations(nodes, R))

                print("N=3   R  W   R+W>N   every read sees the latest write")
                for R, W in [(1, 1), (1, 3), (3, 1), (2, 2), (1, 2), (2, 1)]:
                    print(f"      {R}  {W}   {str(R + W > N):<5}   {always_fresh(R, W)}")
            ''', label="checking the overlap condition exhaustively"),
            "Typical choices for N = 3: <code>W=2, R=2</code> (balanced, tolerates one node down for both reads and writes); <code>W=3, R=1</code> (fast reads, but any node down blocks writes); <code>W=1, R=1</code> (fast and highly available, no freshness guarantee at all).",
            caveat("R + W &gt; N is necessary, not sufficient, for strong consistency. Sloppy quorums and hinted handoff (writing to a stand-in node during a partition), concurrent writes resolved by last-write-wins with skewed clocks, and a write that succeeded on fewer than W nodes but was not rolled back can all still produce stale or lost data. Cassandra&rsquo;s <code>QUORUM</code> is not linearizable without lightweight transactions."),
        ),
        section(
            "Failover and split brain",
            "When the leader fails, a follower must be promoted. Every step is harder than it sounds:",
            "<strong>Detecting failure.</strong> Only by timeout. A leader that is merely slow (a GC pause, a saturated disk, a partitioned switch) looks exactly like a dead one. Too short a timeout causes needless failovers; too long means minutes of downtime.<br><strong>Choosing a new leader.</strong> The most up-to-date follower, which requires agreement among the survivors &mdash; a consensus problem.<br><strong>Redirecting clients</strong> and the old leader&rsquo;s followers.<br><strong>Dealing with the old leader</strong> if it comes back.",
            "The last point is <strong>split brain</strong>: the old leader was not dead, only unreachable. It still believes it is the leader and keeps accepting writes, while the new leader does too. The two histories diverge, and reconciling them usually means discarding one side&rsquo;s writes.",
            "The defence is <strong>fencing</strong>. Every leadership term gets a monotonically increasing number (an epoch, term, or generation). Storage and downstream systems remember the highest term they have seen and reject requests carrying an older one, so a zombie leader&rsquo;s writes are refused even though it does not yet know it has been replaced.",
            code('''
                class Storage:
                    def __init__(self):
                        self.highest_term, self.data = 0, []

                    def write(self, term, who, value):
                        if term < self.highest_term:
                            return f"REJECTED {who} (term {term} < {self.highest_term})"
                        self.highest_term = term
                        self.data.append(value)
                        return f"ok       {who} (term {term})"

                s = Storage()
                print(s.write(1, "node-A", "fill 100 @ 10.00"))
                # node-A stalls in a long GC pause; the cluster elects node-B with term 2
                print(s.write(2, "node-B", "fill 50 @ 10.01"))
                # node-A wakes up, still believing it is leader, and carries on
                print(s.write(1, "node-A", "fill 100 @ 9.99"))
                print("stored:", s.data)
            ''', label="fencing tokens stop a zombie leader"),
            "Consensus protocols (Raft, Paxos, Zab) package all of this: a leader needs votes from a majority to be elected, each term has at most one leader, and an entry is committed only once a majority has it. In any partition at most one side can hold a majority, so at most one side can make progress. That is why clusters have an odd number of voting members: three tolerate one failure, five tolerate two.",
            note("Two-node clusters cannot fail over safely on their own: when the link between them fails, each sees the other as dead and neither has a majority. Add a third voter (a witness or arbiter) or accept manual failover."),
        ),
        section(
            "Consistency vs availability: CAP and PACELC",
            "The <strong>CAP theorem</strong>: when a network <strong>P</strong>artition separates replicas, a system must choose between <strong>C</strong>onsistency (linearizability: every read reflects the latest write, as if there were one copy) and <strong>A</strong>vailability (every request to a non-failed node gets a non-error response). You cannot drop P, because networks do partition; so the real choice is what a system does <em>during</em> one.",
            table(
                ["Choice during a partition", "Behaviour", "Examples"],
                [
                    ["CP", "The minority side refuses reads and/or writes; clients get errors or timeouts", "etcd, ZooKeeper, Spanner, CockroachDB, MongoDB with majority concerns, HBase"],
                    ["AP", "Every side keeps serving; replicas diverge and are reconciled later", "Cassandra and DynamoDB (default settings), Riak, CouchDB, DNS"],
                ],
            ),
            "CAP is narrow: it only describes behaviour during a partition, and it uses a very strict definition of both terms. <strong>PACELC</strong> extends it: if there is a Partition, choose Availability or Consistency; <strong>E</strong>lse, choose <strong>L</strong>atency or <strong>C</strong>onsistency. The &ldquo;else&rdquo; half is the one you live with every day: a synchronous cross-region commit costs tens of milliseconds on every write whether or not anything is failing.",
            table(
                ["Consistency model", "Guarantee", "Typical cost"],
                [
                    ["Linearizable", "Behaves like a single copy; reads see the latest completed write", "Consensus round trip per operation"],
                    ["Sequential", "All clients see operations in the same order, not necessarily real time", "Ordering via a single log"],
                    ["Causal", "Operations that depend on each other are seen in order by everyone", "Track dependencies (vector clocks); stays available in partitions"],
                    ["Read-your-writes / monotonic reads", "Session guarantees for one client", "Sticky routing or version tokens"],
                    ["Eventual", "Replicas converge if writes stop", "Cheapest; anything can be observed meanwhile"],
                ],
            ),
        ),
    ],
    questions=[
        question(
            "Explain the CAP theorem. Is PostgreSQL with one asynchronous replica CP or AP?",
            "medium",
            "CAP says that during a network partition a replicated system must give up either linearizable consistency or availability. It is not a menu of two from three; partitions are not optional, so the decision is only about behaviour when one happens.",
            "PostgreSQL with an async replica is neither in the strict sense. Writes go only to the primary, so a client partitioned from the primary cannot write (not available for writes). Reads from the replica can be stale (not linearizable). And if the primary fails and the replica is promoted, acknowledged writes can be lost. That is why CAP labels are a poor way to describe real systems; better to say precisely what reads can return, what writes can be lost, and what is unavailable during which failures.",
        ),
        question(
            "What is split brain, and how do real systems prevent it?",
            "medium",
            "Split brain is two nodes both acting as leader at the same time, typically after a partition or a long pause makes a healthy leader look dead and a new one is elected. Both accept writes; the histories diverge; data is lost or corrupted when they are reconciled.",
            "Prevention has two layers. <strong>Only one leader can be elected per term</strong>: election requires votes from a strict majority, and in any partition only one side can have a majority (hence odd cluster sizes and a witness for two-node setups). <strong>A deposed leader cannot do damage</strong>: fencing tokens or epochs attached to every write let storage reject a stale leader; leases make a leader stop serving before its lease can have expired from others&rsquo; point of view; and STONITH (&ldquo;shoot the other node in the head&rdquo;) power-cycles the old leader through an out-of-band channel before promotion.",
            "The subtle part is that a node cannot know it has been deposed while it is paused, so the protection must be enforced by whoever receives its writes, not by the node itself.",
        ),
        question(
            "With N = 3 replicas, which R and W would you pick for a read-heavy workload that must always see the latest write, and what happens when a node is down?",
            "hard",
            "The constraint is R + W &gt; 3. For read-heavy traffic, <code>W = 3, R = 1</code> minimises read cost &mdash; any single replica is up to date &mdash; but a single node failure blocks every write. <code>W = 2, R = 2</code> keeps both reads and writes available with one node down, at the cost of reading from two replicas.",
            "Most would choose <code>R = W = 2</code>, and point out the caveats: a write that reached only one node before failing is not rolled back and may later surface (so clients must treat a failed write as &ldquo;unknown&rdquo;, not &ldquo;did not happen&rdquo;); concurrent writes need a conflict rule, and last-write-wins with wall clocks silently drops one; and sloppy quorums break the overlap argument during partitions. If true linearizability is required, use a consensus-based store instead of tuning quorums.",
        ),
        question(
            "Your primary fails over to a replica and afterwards some users report that their last trades have disappeared. Explain what happened and how to stop it recurring.",
            "hard",
            "With asynchronous replication the primary acknowledged those commits after writing only its own WAL. The replica had not yet received them when the primary died. The replica was promoted, and those transactions do not exist in its history. If the old primary later rejoins, its extra WAL must be discarded (<code>pg_rewind</code>) to follow the new timeline, so the trades are gone unless recovered from the old primary&rsquo;s disk by hand.",
            "Fixes: configure at least one synchronous standby (<code>synchronous_standby_names = 'ANY 1 (...)'</code> with <code>synchronous_commit = on</code> or <code>remote_apply</code>) so every acknowledged commit exists on two machines; make the failover manager (Patroni, orchestrator) promote only a standby that was synchronous, and refuse to fail over rather than promote a lagging replica; monitor replication lag; and, for a trading system, make downstream consumers idempotent and reconcile against the exchange&rsquo;s drop copy, because the exchange&rsquo;s record is the real source of truth for fills.",
        ),
        question(
            "What is the difference between linearizability and serializability?",
            "hard",
            "They answer different questions. <strong>Serializability</strong> is a transaction isolation property: the result of running transactions concurrently equals <em>some</em> serial order of them. That order need not match real time: a serializable system may order a transaction that started after yours committed before it.",
            "<strong>Linearizability</strong> is a recency property of single operations on single objects: once a write completes, every later read (in real time) sees it or something newer, as if there were one copy.",
            "<strong>Strict serializability</strong> combines them: transactions appear in a serial order consistent with real time. Spanner provides it with TrueTime; FaunaDB and CockroachDB (for most cases) aim at it. A single-node database at <code>SERIALIZABLE</code> is effectively strictly serializable; a replicated one serving reads from async replicas is serializable at best, and a read from a lagging replica is not linearizable.",
        ),
    ],
    refs=[
        ("PostgreSQL: high availability, load balancing and replication", "https://www.postgresql.org/docs/current/high-availability.html"),
        ("Ongaro and Ousterhout — In Search of an Understandable Consensus Algorithm (Raft)", "https://raft.github.io/raft.pdf"),
        ("Gilbert and Lynch — Brewer's Conjecture and the Feasibility of CAP", "https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf"),
        ("Abadi — Consistency Tradeoffs in Modern Distributed Database System Design (PACELC)", "https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf"),
        ("Jepsen: consistency models", "https://jepsen.io/consistency"),
        ("Kleppmann — How to do distributed locking (fencing tokens)", "https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html"),
    ],
)
