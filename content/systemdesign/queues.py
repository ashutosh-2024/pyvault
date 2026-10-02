from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="queues",
    title="Message Queues and Delivery Guarantees",
    summary="Queues vs logs, at-most/at-least/exactly-once, idempotent consumers, the outbox pattern, ordering, DLQs and lag.",
    intro=[
        "A queue between two services turns a synchronous call into an asynchronous hand-off. The producer finishes as soon as the message is stored; the consumer works through messages at its own pace. That absorbs spikes, lets either side be deployed or fail without the other noticing, and lets many consumers share the work.",
        "The price is that delivery becomes a distributed-systems problem. Messages can be lost, delivered twice, or arrive out of order, and which of those you get depends on choices you make. This topic simulates each failure and the standard fix.",
    ],
    sections=[
        section(
            "Queues vs logs",
            "Two families of systems are both called &ldquo;message queues&rdquo;, and they behave differently.",
            table(
                ["", "Queue (RabbitMQ, SQS)", "Log (Kafka, Kinesis, Pulsar)"],
                [
                    ["After consumption", "Message is deleted once acknowledged", "Message stays for the retention period"],
                    ["Consumers", "Compete: each message goes to one consumer", "Each consumer group reads the whole log at its own offset"],
                    ["Replay", "No", "Yes: rewind the offset"],
                    ["Ordering", "Mostly FIFO, weakened by redelivery and parallel consumers", "Strict within a partition"],
                    ["Scaling consumers", "Add consumers freely", "At most one consumer per partition per group"],
                    ["Best for", "Task distribution, jobs, work queues", "Event streams, many independent readers, rebuilding state"],
                ],
            ),
            "Rule of thumb: if the message is a <em>command</em> (&ldquo;resize this image&rdquo;) that one worker should do once, a queue fits. If it is an <em>event</em> (&ldquo;order 17 was placed&rdquo;) that several systems care about &mdash; billing, email, analytics &mdash; a log fits, because each reads it independently and new readers can start from the beginning.",
        ),
        section(
            "Delivery guarantees",
            "Every consumer does two things: process the message and acknowledge it. The order of those two steps, around a crash, decides the guarantee.",
            code('''
                import random

                def run(ack_first, crash_rate=0.2, n=1000, seed=2):
                    rng = random.Random(seed)
                    queue = list(range(n))
                    processed = []
                    while queue:
                        msg = queue[0]
                        crash = rng.random() < crash_rate
                        if ack_first:
                            queue.pop(0)                     # ack, then process
                            if crash:
                                continue                     # crashed before processing: lost
                            processed.append(msg)
                        else:
                            processed.append(msg)            # process, then ack
                            if crash:
                                continue                     # crashed before ack: redelivered
                            queue.pop(0)
                    lost = n - len(set(processed))
                    duplicates = len(processed) - len(set(processed))
                    return lost, duplicates

                for name, ack_first in (("ack, then process", True), ("process, then ack", False)):
                    lost, dup = run(ack_first)
                    print(f"{name:18} lost={lost:3}  duplicates={dup:3}")
            '''),
            table(
                ["Guarantee", "How", "Consequence"],
                [
                    ["At most once", "Ack before processing (or fire and forget)", "Never duplicated, sometimes lost. Fine for metrics, logs"],
                    ["At least once", "Ack after processing; retry until acked", "Never lost, sometimes duplicated. The default for anything that matters"],
                    ["Exactly once (effectively)", "At least once + idempotent or deduplicating consumer", "Each message's <em>effect</em> happens once"],
                ],
            ),
            note("True exactly-once <em>delivery</em> over an unreliable network is impossible: the consumer can always crash between doing the work and recording that it did. What systems offer is exactly-once <em>processing</em>: at-least-once delivery plus a consumer whose effects are idempotent."),
        ),
        section(
            "Idempotent consumers",
            "An operation is idempotent if doing it twice has the same effect as once. Some are naturally idempotent (&ldquo;set status to shipped&rdquo;, upserts by key). Others are not (&ldquo;add 10 to the balance&rdquo;, &ldquo;send an email&rdquo;) and need a deduplication record: store the message id in the same transaction as the effect, and skip ids already seen.",
            code('''
                import random

                def deliver_with_duplicates(messages, rng):
                    for m in messages:
                        yield m
                        if rng.random() < 0.3:
                            yield m                          # redelivered after a lost ack

                messages = [{"id": f"m{i}", "account": "ann", "amount": 10} for i in range(100)]

                naive = 0
                for m in deliver_with_duplicates(messages, random.Random(5)):
                    naive += m["amount"]

                balance, seen = 0, set()                     # seen ids live in the same DB as balance
                for m in deliver_with_duplicates(messages, random.Random(5)):
                    if m["id"] in seen:
                        continue
                    balance += m["amount"]                   # in one transaction with...
                    seen.add(m["id"])                        # ...recording the id

                print("expected   :", 100 * 10)
                print("naive      :", naive)
                print("idempotent :", balance)
            '''),
            "The dedup store grows forever unless pruned. Keep ids for longer than the maximum redelivery window (often a few days), or use a per-key sequence number: a consumer that has applied version 7 of account <code>ann</code> ignores anything &le; 7.",
        ),
        section(
            "The dual-write problem and the outbox pattern",
            "A service that writes to its database and then publishes an event has two separate writes. If it crashes between them, the database says the order exists and no other service ever hears about it. Publishing first is no better: the event goes out for an order that was never saved.",
            "The <strong>transactional outbox</strong> fixes this: write the event into an <code>outbox</code> table in the <em>same</em> database transaction as the business change. A separate relay reads the outbox and publishes to the broker, retrying until it succeeds &mdash; at least once, so consumers stay idempotent.",
            code('''
                import random, sqlite3

                db = sqlite3.connect(":memory:")
                db.executescript("""
                    CREATE TABLE orders (id INTEGER PRIMARY KEY, item TEXT);
                    CREATE TABLE outbox (id INTEGER PRIMARY KEY, event TEXT, sent INTEGER DEFAULT 0);
                """)
                broker, rng = [], random.Random(4)

                def place_order(item):
                    with db:                                 # one transaction: both or neither
                        cur = db.execute("INSERT INTO orders (item) VALUES (?)", (item,))
                        db.execute("INSERT INTO outbox (event) VALUES (?)", (f"order_placed:{cur.lastrowid}",))

                def relay():
                    rows = db.execute("SELECT id, event FROM outbox WHERE sent = 0 ORDER BY id").fetchall()
                    for row_id, event in rows:
                        if rng.random() < 0.3:
                            print(f"  broker unavailable, will retry {event}")
                            return
                        broker.append(event)
                        with db:
                            db.execute("UPDATE outbox SET sent = 1 WHERE id = ?", (row_id,))

                for item in ("book", "lamp", "desk", "mug"):
                    place_order(item)
                while db.execute("SELECT COUNT(*) FROM outbox WHERE sent = 0").fetchone()[0]:
                    relay()
                print("orders:", db.execute("SELECT COUNT(*) FROM orders").fetchone()[0], "| events:", broker)
            '''),
            caveat("Change data capture (Debezium reading the database's write-ahead log) is the industrial version of the relay: it publishes outbox rows, or every row change, without polling."),
        ),
        section(
            "Ordering and partitions",
            "Logs keep order only within a partition, and parallel consumers of a queue can finish messages in any order. When order matters per entity (all events for one order, one account, one chat), route by a key so that entity's messages always land in the same partition and are handled by one consumer in sequence.",
            code('''
                import random, zlib
                from collections import defaultdict

                events = [(acct, step) for step in range(1, 6) for acct in ("ann", "bob", "cy", "dee")]
                PARTITIONS = 3

                def run(partition_of):
                    parts = defaultdict(list)
                    for i, e in enumerate(events):
                        parts[partition_of(i, e)].append(e)
                    rng = random.Random(2)
                    applied = defaultdict(list)
                    cursors = {p: 0 for p in parts}
                    while any(cursors[p] < len(parts[p]) for p in parts):
                        p = rng.choice([p for p in parts if cursors[p] < len(parts[p])])
                        acct, step = parts[p][cursors[p]]       # partitions progress independently
                        cursors[p] += 1
                        applied[acct].append(step)
                    return {a: s for a, s in applied.items() if s != sorted(s)}

                round_robin = lambda i, e: i % PARTITIONS
                by_key = lambda i, e: zlib.crc32(e[0].encode()) % PARTITIONS

                print("round robin, out of order:", run(round_robin))
                print("keyed,       out of order:", run(by_key))
            '''),
            "Keyed partitioning has a cost: a hot key (one huge customer) overloads one partition, and the number of partitions caps consumer parallelism. Choose the key as the smallest unit that needs ordering &mdash; order id rather than customer id, if per-order order is enough.",
        ),
        section(
            "Retries, poison messages and dead-letter queues",
            "A message that always fails (bad data, a bug) would be redelivered forever and block everything behind it. Count delivery attempts; after N, move the message to a <strong>dead-letter queue</strong> for a human or a repair job, and carry on. Transient failures (a timeout) deserve a retry with back-off; permanent ones (a validation error) should go straight to the DLQ.",
            code('''
                from collections import deque

                class TransientError(Exception): pass
                class PermanentError(Exception): pass

                def handle(msg, attempt):
                    if msg == "corrupt":
                        raise PermanentError("cannot parse")
                    if msg == "flaky" and attempt < 3:
                        raise TransientError("timeout")
                    return f"done {msg}"

                queue = deque([("a", 1), ("corrupt", 1), ("flaky", 1), ("b", 1)])
                dlq, MAX_ATTEMPTS = [], 5
                while queue:
                    msg, attempt = queue.popleft()
                    try:
                        print(" ", handle(msg, attempt))
                    except PermanentError as e:
                        dlq.append((msg, str(e)))
                    except TransientError:
                        if attempt >= MAX_ATTEMPTS:
                            dlq.append((msg, "too many attempts"))
                        else:
                            queue.append((msg, attempt + 1))   # real systems delay this retry
                print("dead letters:", dlq)
            '''),
        ),
        section(
            "Backpressure and consumer lag",
            "A queue absorbs bursts only while consumers keep up on average. <strong>Consumer lag</strong> &mdash; messages produced but not yet processed &mdash; is the metric to watch. If it grows steadily, add consumers (up to the partition count) or make processing faster; if it only grows during bursts and drains afterwards, the queue is doing its job.",
            code('''
                produce = [50] * 10 + [400] * 5 + [50] * 25        # messages per second
                capacity = 120                                      # what consumers can process

                lag, history = 0, []
                for rate in produce:
                    lag = max(0, lag + rate - capacity)
                    history.append(lag)
                peak = max(history)
                drained_at = next(i for i in range(history.index(peak), len(history)) if history[i] == 0)
                print("lag every 5 s:", history[::5])
                print(f"peak lag {peak} messages; drained {drained_at - history.index(peak)} s after the burst ended")
            '''),
        ),
    ],
    questions=[
        question(
            "How do you get exactly-once processing with Kafka?",
            "hard",
            "End to end, by combining at-least-once delivery with idempotence on every side effect. Within Kafka, the idempotent producer (sequence numbers per partition) prevents duplicates from producer retries, and transactions let a consume-transform-produce job commit its output messages and its input offsets atomically &mdash; exactly-once for Kafka-to-Kafka pipelines.",
            "Any effect outside Kafka (a database write, an email, a payment) is not covered. For those, store the consumed offset or message id in the same database transaction as the effect, or make the effect idempotent with a key (Stripe's <code>Idempotency-Key</code>, an upsert). That is where exactly-once is actually won or lost.",
        ),
        question(
            "A consumer charges a credit card for each <code>order_placed</code> event. How do you make sure no customer is charged twice?",
            "medium",
            "Assume every event can arrive more than once. Use the order id as an idempotency key: in one database transaction, insert a <code>payments(order_id UNIQUE, status)</code> row before calling the payment provider, and skip the event if the row already exists. Pass the same key to the provider's idempotency mechanism, so even a retry after a timeout (when you do not know whether the charge went through) cannot charge twice. Record the result, and reconcile with the provider's records periodically for the rare case where your write and theirs disagree.",
        ),
        question(
            "When should you not put a queue between two services?",
            "medium",
            "When the caller needs the answer to continue: a login check, a price for the page being rendered. A queue then adds latency and a request-reply correlation mechanism for no benefit. Also when ordering and consistency are simpler to get with a direct transactional call, or when the volume is tiny and the queue is one more system to run and monitor. Queues fit work that can happen later, needs buffering against spikes, or must reach several consumers.",
        ),
        question(
            "What is consumer lag and what do you do when it keeps growing?",
            "medium",
            "Lag is the gap between the newest message and the consumer's position: work accepted but not done. Steady growth means consumers are slower than producers on average. Options: add consumers (in Kafka, only up to the number of partitions &mdash; add partitions first if needed), make each message cheaper (batching writes, removing a slow synchronous call), or shed load (drop or sample low-value messages). Also check for a single slow partition caused by a hot key, which more consumers will not fix.",
        ),
    ],
    refs=[
        ("Confluent: Exactly-once semantics in Apache Kafka", "https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/"),
        ("microservices.io: Transactional outbox", "https://microservices.io/patterns/data/transactional-outbox.html"),
        ("AWS: Amazon SQS dead-letter queues", "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html"),
        ("Jay Kreps: The Log", "https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying"),
    ],
)
