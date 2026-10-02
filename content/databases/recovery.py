from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="recovery",
    title="Replication Lag, Backups and Recovery",
    summary="What lagging replicas let clients see, RPO and RTO, failover in practice, backups and point-in-time recovery.",
    intro=[
        "The distributed-databases page covered how replication works and how leaders are elected. This page is about living with it: what clients observe when replicas lag, how a failover actually runs, and what you do when the problem is not a dead machine but bad data &mdash; a dropped table, a buggy deploy, a corrupted disk &mdash; which replication faithfully copies to every replica within milliseconds.",
        "Replicas protect against hardware failure. Only backups protect against mistakes. Interviewers probe whether you know the difference.",
    ],
    sections=[
        section(
            "Replication lag and what clients see",
            "An asynchronous follower is always some distance behind the leader: normally milliseconds, but seconds or minutes during a write burst, a long-running query on the replica, network trouble, or a large transaction the replica must apply serially. Reading from replicas scales reads, and exposes that lag to users as three distinct anomalies:",
            table(
                ["Anomaly", "What the user sees", "Guarantee that prevents it"],
                [
                    ["Read-your-writes violation", "Submits an order, refreshes, and the order is not there", "Read-your-writes (read-after-write) consistency"],
                    ["Non-monotonic reads", "Refreshes twice and the order appears, then disappears (two replicas with different lag)", "Monotonic reads"],
                    ["Causality violation", "Sees a fill for an order that does not exist yet", "Consistent prefix / causal consistency"],
                ],
            ),
            code('''
                class Replica:
                    def __init__(self, name, applied):
                        self.name, self.applied = name, applied      # log position applied so far

                log = ["order 1", "order 2", "order 3 (yours)"]
                leader_pos = 3
                r1, r2 = Replica("r1", 3), Replica("r2", 2)          # r2 lags by one write

                def read(replica):
                    return log[:replica.applied]

                print("read via r2:", read(r2), "<- your order is missing")
                print("read via r1:", read(r1))
                print("read via r2:", read(r2), "<- and gone again")

                # fix: the client remembers the log position of its last write,
                # and only uses a replica that has applied at least that much
                my_token = leader_pos
                def safe_read(replicas):
                    ok = [r for r in replicas if r.applied >= my_token]
                    return (ok[0].name, read(ok[0])) if ok else ("leader", log[:leader_pos])

                print("with token:", safe_read([r2, r1]))
                print("with token:", safe_read([r2]))
            ''', label="lagging replicas, and fixing it with a position token"),
            "Practical techniques: send a user&rsquo;s reads to the leader for a short window after they write; carry the write&rsquo;s LSN or GTID as a token and wait for (or pick) a replica that has applied it (<code>pg_last_wal_replay_lsn()</code>, MySQL&rsquo;s <code>WAIT_FOR_EXECUTED_GTID_SET</code>); pin each session to one replica for monotonic reads; and route anything that must be current &mdash; balances, positions, risk &mdash; to the leader, always.",
            note("Monitor lag in <em>time</em> and in <em>bytes</em> (PostgreSQL <code>pg_stat_replication.replay_lag</code>, MySQL <code>Seconds_Behind_Source</code>), and alert on it. Lag is what turns a failover into data loss."),
        ),
        section(
            "RPO and RTO",
            "Every recovery plan is judged by two numbers:",
            table(
                ["", "Question", "Driven by"],
                [
                    ["<strong>RPO</strong> &mdash; recovery point objective", "How much recently committed data may be lost?", "Synchronous vs async replication, WAL archiving frequency, backup schedule"],
                    ["<strong>RTO</strong> &mdash; recovery time objective", "How long may the service be down?", "Automatic vs manual failover, restore speed, WAL replay volume, cache warm-up"],
                ],
            ),
            table(
                ["Failure", "Typical response", "RPO", "RTO"],
                [
                    ["Database process crash", "Restart; WAL recovery from last checkpoint", "0", "Seconds to minutes (checkpoint interval)"],
                    ["Machine or disk dies", "Fail over to a replica", "0 if sync, else the replication lag", "Seconds (automated) to minutes"],
                    ["Datacenter / region lost", "Fail over to a remote replica", "Usually &gt; 0: cross-region replication is async", "Minutes; DNS and clients must move"],
                    ["Bad data: <code>DROP TABLE</code>, buggy migration, ransomware", "Point-in-time restore from backups", "0 up to the moment before the mistake", "Hours for large databases"],
                    ["Silent corruption", "Restore from a backup taken before the corruption", "Whatever since that backup", "Hours"],
                ],
            ),
            "Notice that replication handles the middle rows and does nothing for the last two, because it copies the mistake too.",
        ),
        section(
            "Failover in practice",
            "The mechanics, once a leader is declared dead, typically run through a manager such as Patroni (PostgreSQL), Orchestrator or MySQL Group Replication, or a managed cloud service:",
            "<strong>1. Fence the old leader.</strong> Make sure it cannot accept writes: revoke its lease in the consensus store (etcd, ZooKeeper, Consul), cut it off at the network or storage layer, or power it off.<br><strong>2. Choose the candidate.</strong> The replica with the most WAL received; with synchronous replication, only a replica that was synchronous. Refuse to promote one lagging beyond the allowed RPO.<br><strong>3. Promote.</strong> The replica finishes replaying what it has, starts a new timeline or epoch, and begins accepting writes.<br><strong>4. Repoint.</strong> Other replicas follow the new leader; clients are redirected by a virtual IP, DNS, a proxy (HAProxy, PgBouncer, ProxySQL) or a topology-aware driver.<br><strong>5. Rejoin the old leader</strong> as a replica after rewinding any WAL it wrote that the new leader never saw (<code>pg_rewind</code>).",
            "Planned <strong>switchovers</strong> (for upgrades or maintenance) run the same steps without loss: stop writes on the old leader, wait until the candidate has applied everything, then promote. Practise them; an untested failover path usually fails the first time it is needed.",
            caveat("Clients see a failover as a burst of connection errors, and any transaction in flight at that moment has an unknown outcome: it may or may not have committed on the old leader and replicated. Retrying non-idempotent writes blindly can duplicate them. Use idempotency keys (a client-generated order ID with a unique constraint) so a retry is harmless."),
        ),
        section(
            "Backups",
            table(
                ["Kind", "How", "Pros", "Cons"],
                [
                    ["Logical", "<code>pg_dump</code>, <code>mysqldump</code>: SQL or rows", "Portable across versions; restore one table", "Slow to take and very slow to restore at scale; indexes rebuilt"],
                    ["Physical", "Copy data files: <code>pg_basebackup</code>, Percona XtraBackup, storage snapshots", "Fast restore; exact copy", "Same major version and architecture; whole cluster only"],
                    ["Continuous (WAL archiving)", "Ship every WAL segment to object storage as it fills", "Enables point-in-time recovery; RPO of seconds", "Needs a base backup to replay onto; archive must be monitored"],
                ],
            ),
            "A physical backup of a running database is copied while pages are changing, so on its own it is inconsistent. It becomes consistent by replaying the WAL generated during the copy, which is why backup tools record the start and end WAL positions. SQLite&rsquo;s online backup API makes a consistent copy of a live database page by page:",
            code('''
                import os, sqlite3, tempfile

                d = tempfile.mkdtemp()
                live = sqlite3.connect(os.path.join(d, "live.db"))
                live.execute("CREATE TABLE fills(id INTEGER PRIMARY KEY, sym TEXT, qty INT)")
                live.executemany("INSERT INTO fills(sym, qty) VALUES (?, ?)",
                                 [(f"S{i % 50}", i % 7 + 1) for i in range(20_000)])
                live.commit()

                copies = []
                def progress(status, remaining, total):
                    copies.append(total - remaining)

                backup = sqlite3.connect(os.path.join(d, "backup.db"))
                live.backup(backup, pages=16, progress=progress)     # 16 pages per step

                print("steps:", len(copies), "| pages copied:", copies[-1])
                print("integrity:", backup.execute("PRAGMA integrity_check").fetchone()[0])
                print("rows match:", backup.execute("SELECT count(*), sum(qty) FROM fills").fetchone()
                      == live.execute("SELECT count(*), sum(qty) FROM fills").fetchone())
            ''', label="an online, consistent backup with SQLite's backup API"),
            "The rules that matter more than the tooling: keep backups off the machine and preferably in another account or region (the <strong>3-2-1 rule</strong>: three copies, two media, one off-site), make at least one copy immutable so ransomware or a compromised admin cannot delete it, encrypt them, and <strong>test restores regularly</strong>. A backup that has never been restored is a hypothesis.",
        ),
        section(
            "Point-in-time recovery",
            "PITR combines a base backup with the archived WAL. Restore the base backup, then replay WAL forward and <em>stop just before</em> the mistake: <code>recovery_target_time</code>, <code>recovery_target_lsn</code> or <code>recovery_target_xid</code> in PostgreSQL, <code>mysqlbinlog --stop-datetime</code> in MySQL.",
            code('''
                import sqlite3

                # the archive: every change since the base backup, with its commit time
                archive = [
                    ("09:00:01", "INSERT INTO positions VALUES ('AAPL', 100)"),
                    ("09:30:12", "INSERT INTO positions VALUES ('MSFT', 250)"),
                    ("10:02:40", "UPDATE positions SET qty = 180 WHERE sym = 'AAPL'"),
                    ("10:05:03", "DELETE FROM positions"),                  # the mistake
                    ("10:07:55", "INSERT INTO positions VALUES ('NVDA', 40)"),
                ]

                def restore(until=None):
                    db = sqlite3.connect(":memory:")
                    db.execute("CREATE TABLE positions(sym TEXT, qty INT)")    # the base backup
                    for ts, sql in archive:
                        if until and ts >= until:
                            break
                        db.execute(sql)
                    return db.execute("SELECT * FROM positions ORDER BY sym").fetchall()

                print("replay everything:        ", restore())
                print("recovery target 10:05:00: ", restore(until="10:05:00"))
            ''', label="replaying the archive up to a moment before the mistake"),
            "Stopping before the <code>DELETE</code> recovers the positions but also discards the legitimate <code>NVDA</code> insert that came after it. Real incidents usually end with a restore to a separate instance at the target time, then a careful copy of the lost data back into production, so that later valid work is kept.",
            note("RTO for PITR is the time to copy the base backup plus the time to replay the WAL since it was taken. Frequent base backups keep the replay short; that trade-off, not storage cost, usually sets the backup schedule."),
        ),
    ],
    questions=[
        question(
            "Why is a replica not a backup?",
            "medium",
            "A replica protects against the loss of a machine: it has a current copy of the data and can take over. But it is current by design, so every logical mistake &mdash; <code>DROP TABLE</code>, a <code>DELETE</code> without a <code>WHERE</code>, a migration that corrupts a column, an application bug writing garbage, ransomware encrypting rows through the database &mdash; replicates to it within milliseconds. The same applies to corruption introduced by a software bug above the storage layer.",
            "A backup is a copy from the past that the mistake cannot reach: base backups plus archived WAL, stored separately and ideally immutably, so you can restore to the moment before the problem. You need both. A delayed replica (<code>recovery_min_apply_delay</code>) is a useful middle ground, giving an hour or so to catch a mistake before it arrives, but it is not a substitute for real backups.",
        ),
        question(
            "A user places an order and immediately refreshes their order list, which is served from read replicas. Sometimes the order is missing. How do you fix it without sending all reads to the primary?",
            "medium",
            "It is a read-your-writes violation caused by replication lag. Options, from simplest to most precise:",
            "<strong>Time-based stickiness:</strong> for a few seconds after a user writes, route that user&rsquo;s reads to the primary (store the last-write time in their session).<br><strong>Position tokens:</strong> return the commit&rsquo;s LSN or GTID with the write response; on the next read, pick a replica whose applied position is at least that token, or make the replica wait until it is (bounded by a timeout, then fall back to the primary).<br><strong>Route by data:</strong> data the user just changed or must see accurately (their own orders, balances) always comes from the primary; shared, slowly changing data comes from replicas.",
            "Also pin a session to one replica, or the user may see the order appear and disappear as successive reads hit replicas with different lag.",
        ),
        question(
            "Someone ran <code>DELETE FROM trades</code> without a WHERE clause at 14:32 on the production primary. Walk through recovery.",
            "hard",
            "<strong>Stop the damage.</strong> Confirm what happened and when (the audit log, <code>pg_stat_statements</code>, the binlog). Decide whether to halt writes; usually not &mdash; the rest of the system keeps working, and later valid writes must be preserved.",
            "<strong>Restore to the side.</strong> Provision a separate instance, restore the most recent base backup before 14:32, and replay the archived WAL with a recovery target just before the delete (ideally the transaction ID or LSN of the delete, found by inspecting the WAL with <code>pg_waldump</code> or <code>mysqlbinlog</code>, rather than a clock time).",
            "<strong>Reconcile.</strong> Copy the deleted rows from the restored instance back into production. Rows inserted after 14:32 are already in production and must be kept; rows that were updated after the restore point need a decision. Verify counts and checksums against downstream systems.",
            "<strong>Prevent recurrence.</strong> Remove direct write access to production for humans, require reviewed migrations, set <code>sql_safe_updates</code> (MySQL) or use a transaction with a row-count check, and keep a delayed replica so the next incident can be recovered in minutes rather than hours.",
        ),
        question(
            "What are RPO and RTO, and how would you achieve an RPO of zero and an RTO under 30 seconds for a PostgreSQL database?",
            "hard",
            "RPO is the maximum acceptable data loss, measured in time; RTO is the maximum acceptable downtime.",
            "RPO of zero means no acknowledged commit may be lost, so every commit must exist on at least two machines before it is acknowledged: synchronous replication with <code>synchronous_standby_names = 'ANY 1 (s1, s2)'</code> and <code>synchronous_commit = on</code> (or <code>remote_apply</code> if reads from the standby must see it). Two synchronous candidates, so one failing does not block commits.",
            "RTO under 30 seconds needs automated failover: Patroni (or similar) with a consensus store for leader election and fencing, short but not twitchy health-check timeouts, promotion restricted to synchronous standbys, and clients that reconnect quickly through a proxy or a virtual IP. Keep WAL replay on standbys current and checkpoints frequent so promotion is fast.",
            "Then state the limits: this covers machine failure, not logical errors (needs PITR, with an RTO of hours); a full region loss would still lose data unless a synchronous replica is in another region, at a latency cost on every commit.",
        ),
        question(
            "What happens to in-flight transactions during a failover, and how should the application handle it?",
            "hard",
            "Connections to the old leader break. For a transaction that had not sent <code>COMMIT</code>, the outcome is clear: it never committed, and the application retries it from the beginning. For a transaction whose <code>COMMIT</code> was sent but whose reply never arrived, the outcome is <em>unknown</em>: the commit might have been applied and replicated, applied on the old leader only (and lost in the failover), or never applied.",
            "The application must therefore make writes idempotent: a client-generated unique ID (an order&rsquo;s client order ID) with a unique constraint, so retrying a commit that actually succeeded fails harmlessly with a duplicate-key error the application recognises as success. For non-idempotent operations such as incrementing a balance, record the operation with its ID in the same transaction and check for it before re-applying.",
            "Connection pools should detect the failover (errors, or the server reporting it is read-only) and drain and re-establish connections rather than retrying on dead sockets; drivers with multi-host connection strings and <code>target_session_attrs=read-write</code> find the new leader automatically.",
        ),
    ],
    refs=[
        ("PostgreSQL: continuous archiving and point-in-time recovery", "https://www.postgresql.org/docs/current/continuous-archiving.html"),
        ("PostgreSQL: pg_rewind", "https://www.postgresql.org/docs/current/app-pgrewind.html"),
        ("SQLite: the online backup API", "https://www.sqlite.org/backup.html"),
        ("Patroni documentation", "https://patroni.readthedocs.io/"),
        ("MySQL: point-in-time recovery using binary logs", "https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html"),
    ],
)
