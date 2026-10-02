from ._lld import code, table, note, caveat, question, problem

LRU_CACHE = problem(
    id="lru-cache",
    title="Design an LRU / LFU Cache",
    level="medium",
    patterns=["Strategy", "Decorator"],
    summary="O(1) get and put with a hash map plus doubly linked list, a pluggable eviction policy, and thread safety.",
    statement=[
        "Design an in-memory cache with a fixed capacity that supports <code>get</code> and <code>put</code> in O(1). When full, it evicts according to a policy: least recently used by default, least frequently used as an option.",
    ],
    requirements=[
        "O(1) <code>get(key)</code> and <code>put(key, value)</code>. Capacity in entries. Eviction policy pluggable (LRU, LFU). Report hit rate. Optionally safe to use from several threads.",
    ],
    choose=[
        ["&ldquo;Evict by LRU, or by LFU&rdquo;", "Strategy", "The cache delegates ordering and victim choice to a policy object"],
        ["Add thread safety or metrics without changing the cache", "Decorator", "A wrapper with the same interface adds a lock or counters"],
        ["O(1) recency updates", "Hash map + doubly linked list", "The map finds the node; the list moves it to the front in O(1)"],
    ],
    classes=[
        ["<code>Node</code>", "Key, value, prev, next"],
        ["<code>LRUPolicy</code>", "Doubly linked list with sentinels: touch, add, pop least recent"],
        ["<code>LFUPolicy</code>", "Frequency buckets of insertion-ordered keys plus the current minimum frequency"],
        ["<code>Cache</code>", "Map key &rarr; value; asks the policy for the victim when full"],
        ["<code>Locked</code>", "Decorator adding a lock around every call"],
    ],
    implementation=[
        code('''
            import threading
            from collections import defaultdict, OrderedDict

            class Node:
                __slots__ = ("key", "prev", "next")
                def __init__(self, key=None): self.key, self.prev, self.next = key, None, None

            class LRUPolicy:
                def __init__(self):
                    self.head, self.tail = Node(), Node()          # sentinels: no edge cases
                    self.head.next, self.tail.prev = self.tail, self.head
                    self.nodes = {}

                def _unlink(self, n):
                    n.prev.next, n.next.prev = n.next, n.prev

                def _push_front(self, n):
                    n.next, n.prev = self.head.next, self.head
                    self.head.next.prev = n
                    self.head.next = n

                def touch(self, key):
                    n = self.nodes[key]
                    self._unlink(n); self._push_front(n)

                def add(self, key):
                    n = self.nodes[key] = Node(key)
                    self._push_front(n)

                def victim(self):
                    n = self.tail.prev
                    self._unlink(n)
                    del self.nodes[n.key]
                    return n.key

            class LFUPolicy:
                def __init__(self):
                    self.freq = {}
                    self.buckets = defaultdict(OrderedDict)        # freq -> keys in LRU order
                    self.min_freq = 0

                def touch(self, key):
                    f = self.freq[key]
                    del self.buckets[f][key]
                    if not self.buckets[f] and self.min_freq == f:
                        self.min_freq += 1
                    self.freq[key] = f + 1
                    self.buckets[f + 1][key] = None

                def add(self, key):
                    self.freq[key] = 1
                    self.buckets[1][key] = None
                    self.min_freq = 1

                def victim(self):
                    key, _ = self.buckets[self.min_freq].popitem(last=False)
                    del self.freq[key]
                    return key

            class Cache:
                def __init__(self, capacity, policy):
                    self.capacity, self.policy, self.data = capacity, policy, {}
                    self.hits = self.misses = 0

                def get(self, key, default=None):
                    if key not in self.data:
                        self.misses += 1
                        return default
                    self.hits += 1
                    self.policy.touch(key)
                    return self.data[key]

                def put(self, key, value):
                    if key in self.data:
                        self.data[key] = value
                        self.policy.touch(key)
                        return
                    if len(self.data) >= self.capacity:
                        del self.data[self.policy.victim()]
                    self.data[key] = value
                    self.policy.add(key)

            class Locked:                                          # decorator: same interface
                def __init__(self, inner):
                    self.inner, self.lock = inner, threading.Lock()
                def get(self, *a):
                    with self.lock: return self.inner.get(*a)
                def put(self, *a):
                    with self.lock: return self.inner.put(*a)

            for policy in (LRUPolicy(), LFUPolicy()):
                c = Cache(3, policy)
                for k in "abc": c.put(k, k.upper())
                c.get("a"); c.get("a"); c.get("b")                  # a used twice, b once, c never
                c.put("d", "D")                                     # evicts one key
                c.get("c"); c.put("e", "E")
                print(f"{type(policy).__name__}: keys now {sorted(c.data)}")

            shared = Locked(Cache(100, LRUPolicy()))
            def worker(i):
                for j in range(1000):
                    shared.put(j % 150, i); shared.get(j % 120)
            ts = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
            for t in ts: t.start()
            for t in ts: t.join()
            inner = shared.inner
            print("after 8 threads:", len(inner.data), "entries,", len(inner.policy.nodes), "list nodes (consistent)")
        '''),
        "Trace for LRU: after the gets the recency order is b, a, c (most recent first), so <code>d</code> evicts <code>c</code>; the next get of <code>c</code> misses, and <code>e</code> evicts <code>a</code>. LFU instead keeps the frequently used <code>a</code> and evicts the least-used keys.",
    ],
    extend=[
        "TTL support adds an expiry per key, checked on <code>get</code> plus a background sweep. A size-in-bytes capacity changes &ldquo;full&rdquo; from a count to a sum. In Python, <code>functools.lru_cache</code> and <code>OrderedDict.move_to_end</code> give an LRU for free; the interview usually wants the linked-list version to show you know why it is O(1).",
    ],
    questions=[
        question(
            "Why a doubly linked list rather than a singly linked one or a list?",
            "medium",
            "Moving a node to the front and removing the tail both need the node's predecessor. With a doubly linked list the node knows its predecessor, so unlinking is O(1) given the node from the hash map. A singly linked list would need an O(n) walk to find the predecessor, and a Python list would shift elements on every move.",
        ),
        question(
            "How does LFU stay O(1)?",
            "hard",
            "Keep a map from frequency to an insertion-ordered set of keys, each key's frequency, and the minimum frequency present. A touch moves the key from bucket f to f+1 in O(1) and bumps <code>min_freq</code> if bucket f emptied and was the minimum. A new key always has frequency 1, so <code>min_freq</code> resets to 1. Eviction pops the oldest key in the <code>min_freq</code> bucket, which breaks ties by recency.",
        ),
    ],
)


LOGGER = problem(
    id="logging-framework",
    title="Design a Logging Framework",
    level="medium",
    patterns=["Chain of Responsibility", "Strategy", "Observer", "Singleton"],
    summary="Levels and hierarchical loggers, handlers (console, file, memory) with their own levels, pluggable formatters.",
    statement=[
        "Design a logging library like Python's <code>logging</code> or Log4j: application code calls <code>log.info(...)</code>; messages below a level are dropped cheaply; each message can go to several destinations, each with its own threshold and format; loggers are named hierarchically and inherit configuration.",
    ],
    requirements=[
        "Levels DEBUG &lt; INFO &lt; WARNING &lt; ERROR. Named loggers (<code>app.db</code>) pass records up to ancestors (<code>app</code>, root) unless propagation is off. Handlers (console, file, in-memory) each have a level and a formatter. One registry of loggers per process.",
    ],
    choose=[
        ["Record travels from <code>app.db</code> to <code>app</code> to root", "Chain of Responsibility", "Each logger handles the record then passes it to its parent"],
        ["Several destinations receive each record", "Observer", "Handlers subscribe to a logger"],
        ["Plain text vs JSON output", "Strategy", "Formatter is swappable per handler"],
        ["<code>get_logger(name)</code> returns the same object everywhere", "Singleton registry", "One process-wide registry"],
    ],
    classes=[
        ["<code>Level</code>", "Ordered severities"],
        ["<code>Record</code>", "Logger name, level, message, context"],
        ["<code>Formatter</code>", "Strategy: record &rarr; string"],
        ["<code>Handler</code>", "Level threshold + formatter + destination"],
        ["<code>Logger</code>", "Name, level, handlers, parent; filters and propagates"],
        ["<code>get_logger</code>", "Registry creating loggers and wiring parents"],
    ],
    implementation=[
        code('''
            import json
            from dataclasses import dataclass, field
            from enum import IntEnum

            class Level(IntEnum):
                DEBUG = 10
                INFO = 20
                WARNING = 30
                ERROR = 40

            @dataclass
            class Record:
                logger: str
                level: Level
                msg: str
                ctx: dict = field(default_factory=dict)

            class TextFormatter:
                def format(self, r): return f"{r.level.name:7} {r.logger}: {r.msg}"

            class JsonFormatter:
                def format(self, r):
                    return json.dumps({"lvl": r.level.name, "log": r.logger, "msg": r.msg, **r.ctx})

            class Handler:
                def __init__(self, level=Level.DEBUG, formatter=None):
                    self.level, self.formatter = level, formatter or TextFormatter()
                def handle(self, r):
                    if r.level >= self.level:
                        self.emit(self.formatter.format(r))

            class ConsoleHandler(Handler):
                def emit(self, line): print("  console |", line)

            class MemoryHandler(Handler):
                def __init__(self, *a, **kw):
                    super().__init__(*a, **kw); self.lines = []
                def emit(self, line): self.lines.append(line)

            class Logger:
                def __init__(self, name, parent=None):
                    self.name, self.parent = name, parent
                    self.level, self.handlers, self.propagate = None, [], True

                def effective_level(self):
                    node = self
                    while node.level is None:
                        node = node.parent
                    return node.level

                def log(self, level, msg, **ctx):
                    if level < self.effective_level():          # cheap early exit
                        return
                    r, node = Record(self.name, level, msg, ctx), self
                    while node:                                   # chain up the hierarchy
                        for h in node.handlers:
                            h.handle(r)
                        node = node.parent if node.propagate else None

                def debug(self, m, **c): self.log(Level.DEBUG, m, **c)
                def info(self, m, **c): self.log(Level.INFO, m, **c)
                def error(self, m, **c): self.log(Level.ERROR, m, **c)

            _registry = {"": Logger("root")}
            _registry[""].level = Level.WARNING

            def get_logger(name=""):
                if name not in _registry:
                    parent = get_logger(name.rpartition(".")[0]) if "." in name else _registry[""]
                    _registry[name] = Logger(name, parent)
                return _registry[name]

            get_logger().handlers.append(ConsoleHandler())
            audit = MemoryHandler(Level.INFO, JsonFormatter())
            get_logger("app").handlers.append(audit)
            get_logger("app").level = Level.INFO

            db = get_logger("app.db")
            db.debug("connecting")                           # below app's INFO: dropped
            db.info("connected", host="db1")                 # app's JSON handler, then root's console
            db.error("query failed", table="orders")         # same two handlers
            get_logger("lib").info("noise")                  # root is WARNING: dropped
            print("audit captured:", audit.lines)
            print(get_logger("app.db") is db)
        '''),
    ],
    extend=[
        "An async handler (a queue drained by a background thread) keeps slow destinations from blocking the request path. Filters (drop health-check logs, sample debug logs) are another link in the chain. Context such as a request id is added with a <code>contextvars</code> variable read by the formatter.",
    ],
    questions=[
        question(
            "Why check the level before building the record?",
            "medium",
            "Logging calls sit on hot paths. Most debug calls are disabled in production, so the cheapest path must be a single integer comparison. Formatting messages, capturing stack info or building dicts for disabled levels wastes CPU. This is also why you pass arguments separately (<code>log.debug(\"x=%s\", x)</code>) instead of pre-formatting: formatting happens only if the record is emitted.",
        ),
        question(
            "A file handler sometimes blocks for 200 ms on a slow disk. How do you stop it slowing requests?",
            "medium",
            "Decouple producing from writing: the logger puts records on a bounded in-memory queue and a background thread drains it to the file (Python's <code>QueueHandler</code>/<code>QueueListener</code>). Decide what happens when the queue is full: block (safe, slow), drop debug records first, or drop and count. Flush the queue on shutdown so the last records are not lost.",
        ),
    ],
)


NOTIFICATION_SERVICE = problem(
    id="notification-service",
    title="Design a Notification Service",
    level="medium",
    patterns=["Strategy", "Template Method", "Decorator", "Factory"],
    summary="Email, SMS and push channels behind one interface, user preferences, templates, retries and rate limits as decorators.",
    statement=[
        "Design an internal notification library: services call <code>notify(user, event, data)</code>, and the library renders a message and delivers it over the channels the user has enabled (email, SMS, push), retrying transient failures and respecting per-user quiet hours.",
    ],
    requirements=[
        "Channels: email, SMS, push, more later. User preferences decide which channels each event uses. Messages are rendered from templates per event and channel. Transient failures are retried; quiet hours delay non-urgent messages. Every send is recorded.",
    ],
    choose=[
        ["Several channels with the same job", "Strategy", "<code>Channel.send(to, message)</code> per provider"],
        ["Every channel: validate, render, send, record", "Template Method", "Base class fixes the steps; subclasses implement <code>deliver</code>"],
        ["Add retries, rate limiting, logging to any channel", "Decorator", "Wrappers stack around a channel"],
        ["Pick channel objects from preference names", "Factory", "<code>\"sms\"</code> &rarr; <code>SmsChannel</code>"],
    ],
    classes=[
        ["<code>Channel</code>", "Template: <code>send</code> = validate + deliver + record"],
        ["<code>EmailChannel</code>, <code>SmsChannel</code>, <code>PushChannel</code>", "Concrete <code>deliver</code>"],
        ["<code>Retrying</code>", "Decorator: retry transient failures"],
        ["<code>NotificationService</code>", "Preferences, templates, quiet hours; fans out to channels"],
    ],
    implementation=[
        code('''
            class TransientError(Exception): pass

            class Channel:
                name = "base"
                def __init__(self): self.sent = []
                def send(self, user, message):               # template method
                    to = self.address(user)
                    if not to:
                        return f"{self.name}: skipped, no address"
                    self.deliver(to, message)
                    self.sent.append((to, message))
                    return f"{self.name}: sent to {to}"
                def address(self, user): raise NotImplementedError
                def deliver(self, to, message): raise NotImplementedError

            class EmailChannel(Channel):
                name = "email"
                def address(self, u): return u.get("email")
                def deliver(self, to, m): pass

            class SmsChannel(Channel):
                name = "sms"
                def __init__(self, fail_times=0):
                    super().__init__(); self.fail_times = fail_times
                def address(self, u): return u.get("phone")
                def deliver(self, to, m):
                    if self.fail_times:
                        self.fail_times -= 1
                        raise TransientError("gateway timeout")

            class PushChannel(Channel):
                name = "push"
                def address(self, u): return u.get("device")
                def deliver(self, to, m): pass

            class Retrying:                                  # decorator
                def __init__(self, inner, attempts=3):
                    self.inner, self.attempts, self.name = inner, attempts, inner.name
                def send(self, user, message):
                    for i in range(1, self.attempts + 1):
                        try:
                            result = self.inner.send(user, message)
                            return result + (f" (attempt {i})" if i > 1 else "")
                        except TransientError:
                            continue
                    return f"{self.name}: failed after {self.attempts} attempts"

            TEMPLATES = {
                ("order_shipped", "email"): "Hi {name}, order {order} has shipped. Track: {url}",
                ("order_shipped", "sms"): "Order {order} shipped",
                ("order_shipped", "push"): "Your order is on the way",
                ("otp", "sms"): "Your code is {code}",
            }

            class NotificationService:
                def __init__(self, channels):
                    self.channels = {c.name: c for c in channels}      # factory by name
                    self.deferred = []

                def notify(self, user, event, data, hour, urgent=False):
                    if not urgent and user.get("quiet") and hour in range(*user["quiet"]):
                        self.deferred.append((user["name"], event))
                        return [f"deferred {event}: quiet hours"]
                    results = []
                    for ch in user["prefs"].get(event, []):
                        template = TEMPLATES.get((event, ch))
                        if template:
                            results.append(self.channels[ch].send(user, template.format(name=user["name"], **data)))
                    return results

            svc = NotificationService([EmailChannel(), Retrying(SmsChannel(fail_times=2)), PushChannel()])
            ann = {"name": "Ann", "email": "ann@x.io", "phone": "+91-98", "quiet": (22, 24),
                   "prefs": {"order_shipped": ["email", "sms", "push"], "otp": ["sms"]}}
            print(svc.notify(ann, "order_shipped", {"order": "A17", "url": "t.co/a17"}, hour=10))
            print(svc.notify(ann, "order_shipped", {"order": "A18", "url": "t.co/a18"}, hour=23))
            print(svc.notify(ann, "otp", {"code": "4821"}, hour=23, urgent=True))
            print("deferred queue:", svc.deferred)
        '''),
        "The first SMS failed twice and succeeded on the third attempt inside the <code>Retrying</code> decorator; the service never saw the failures. Ann has no device registered, so push was skipped by the template method's address step rather than by special-case code in the service.",
    ],
    extend=[
        "A new channel (WhatsApp, Slack) is a <code>Channel</code> subclass plus templates. Rate limiting per user (no more than 3 SMS an hour) is another decorator. In production the service puts sends on a queue per channel so a slow provider never blocks callers, and records delivery receipts from provider webhooks.",
    ],
    questions=[
        question(
            "How do you avoid sending the same notification twice when the caller retries?",
            "medium",
            "Make <code>notify</code> idempotent with a key supplied by the caller (event id plus user plus channel). Record the key before or atomically with sending; a retry with the same key returns the earlier result. Providers that accept an idempotency key (many SMS and email APIs do) give a second layer of protection for retries after timeouts.",
        ),
        question(
            "Why is retry a decorator rather than built into each channel?",
            "medium",
            "Retry policy is a cross-cutting concern that should be the same across channels and configurable per deployment (attempts, backoff). As a decorator it is written once, tested once, and can be stacked with other wrappers (rate limit, metrics, circuit breaker) in whichever order is needed, without every channel duplicating loops and exception handling.",
        ),
    ],
)


PUBSUB = problem(
    id="pubsub-broker",
    title="Design an In-Memory Pub/Sub Message Broker",
    level="hard",
    patterns=["Observer", "Mediator"],
    summary="Topics, subscriptions with offsets, consumer groups sharing work, acknowledgements, and replay.",
    statement=[
        "Design a small in-memory message broker in the spirit of Kafka: producers publish messages to topics; each subscriber reads every message at its own pace; members of a consumer group share the messages of a topic; consumers acknowledge processed messages and can replay from an offset.",
    ],
    requirements=[
        "Topics are append-only logs with offsets. A subscription (group) has a committed offset. Within a group, each message is delivered to one member (round robin here). Messages are retained, so a new group can read from the beginning. Thread-safe publish and poll.",
    ],
    choose=[
        ["Many subscribers react to messages on a topic", "Observer (pull-based)", "Subscribers register interest; the broker tracks each one's position"],
        ["Producers and consumers never reference each other", "Mediator", "The broker is the only thing both sides know"],
        ["Each subscriber reads at its own pace, can replay", "Log + per-group offsets", "Retention decouples consumption from publication"],
    ],
    classes=[
        ["<code>Topic</code>", "Append-only list of messages and a lock"],
        ["<code>Group</code>", "Committed offset and members"],
        ["<code>Broker</code>", "<code>publish</code>, <code>subscribe</code>, <code>poll</code>, <code>commit</code>, <code>seek</code>"],
    ],
    implementation=[
        code('''
            import threading
            from collections import defaultdict
            from itertools import cycle

            class Topic:
                def __init__(self, name):
                    self.name, self.log, self.lock = name, [], threading.Lock()
                def append(self, msg):
                    with self.lock:
                        self.log.append(msg)
                        return len(self.log) - 1

            class Group:
                def __init__(self, members):
                    self.offset = 0                     # next message to hand out
                    self.committed = 0
                    self.members = cycle(members)
                    self.lock = threading.Lock()

            class Broker:
                def __init__(self):
                    self.topics = {}
                    self.groups = defaultdict(dict)     # topic -> group name -> Group

                def publish(self, topic, msg):
                    t = self.topics.setdefault(topic, Topic(topic))
                    return t.append(msg)

                def subscribe(self, topic, group, members, from_beginning=True):
                    g = Group(members)
                    if not from_beginning:
                        g.offset = g.committed = len(self.topics.get(topic, Topic(topic)).log)
                    self.groups[topic][group] = g

                def poll(self, topic, group, max_n=10):
                    """hand out up to max_n messages, each to one member of the group"""
                    g, log = self.groups[topic][group], self.topics[topic].log
                    with g.lock:
                        batch = []
                        while g.offset < len(log) and len(batch) < max_n:
                            batch.append((next(g.members), g.offset, log[g.offset]))
                            g.offset += 1
                        return batch

                def commit(self, topic, group, offset):
                    g = self.groups[topic][group]
                    g.committed = max(g.committed, offset + 1)

                def seek(self, topic, group, offset):          # replay
                    g = self.groups[topic][group]
                    g.offset = g.committed = offset

            b = Broker()
            for i in range(5):
                b.publish("orders", f"order-{i}")
            b.subscribe("orders", "billing", ["bill-1", "bill-2"])
            b.subscribe("orders", "email", ["mailer"])

            for member, off, msg in b.poll("orders", "billing", max_n=4):
                print(f"billing: {member} got {msg} @{off}")
                b.commit("orders", "billing", off)
            print("email gets everything too:", [m for _, _, m in b.poll("orders", "email")])

            b.subscribe("orders", "analytics", ["etl"], from_beginning=False)
            b.publish("orders", "order-5")
            print("late group sees only new:", [m for _, _, m in b.poll("orders", "analytics")])
            b.seek("orders", "analytics", 0)
            print("after seek(0) replay:", len(b.poll("orders", "analytics")), "messages")
            print("billing committed offset:", b.groups["orders"]["billing"].committed)
        '''),
    ],
    extend=[
        "Partitions (several logs per topic, keyed by message key) give parallelism with per-key ordering. Redelivery of unacknowledged messages needs a visibility timeout: a polled message not committed within N seconds is handed out again. Retention by size or age trims the log head. Durability means writing the log to disk before acknowledging the producer.",
    ],
    questions=[
        question(
            "What is the difference between the delivered offset and the committed offset?",
            "medium",
            "The delivered offset is how far the broker has handed out messages; the committed offset is how far the group has confirmed processing. If a consumer crashes, the group restarts from the committed offset, so messages delivered but not committed are processed again: that is at-least-once delivery. Committing before processing gives at-most-once instead.",
        ),
        question(
            "How would you guarantee ordering for all messages of one customer while still processing in parallel?",
            "hard",
            "Split each topic into partitions and route messages by a hash of the customer id, so one customer's messages are always in one partition, in order. Assign each partition to exactly one member of a consumer group at a time; members process different partitions in parallel. Parallelism is capped by the partition count, and a hot customer can make one partition a bottleneck.",
        ),
    ],
)


TASK_SCHEDULER = problem(
    id="task-scheduler",
    title="Design a Task Scheduler",
    level="medium",
    patterns=["Command", "Strategy"],
    summary="One-off, delayed and recurring jobs as command objects, a min-heap by next run time, retry policies, cancellation.",
    statement=[
        "Design a job scheduler library: callers submit tasks to run once at a time, after a delay, or repeatedly at a fixed interval; tasks can be cancelled; failed tasks are retried according to a policy. Time must be injectable so the scheduler can be tested without waiting.",
    ],
    requirements=[
        "<code>schedule(task, at)</code>, <code>every(task, interval)</code>, <code>cancel(id)</code>. Tasks run in time order; ties in submission order. Recurring tasks are rescheduled after running. A failing task is retried with a delay from its retry policy, up to a limit.",
    ],
    choose=[
        ["Jobs are units of work stored and run later", "Command", "Each job wraps a callable with its schedule and state"],
        ["Fixed interval vs exponential backoff retries", "Strategy", "Retry delay policy per job"],
        ["Always run the earliest job next", "Min-heap", "O(log n) insert and pop by next run time"],
    ],
    classes=[
        ["<code>Job</code>", "Command: callable, next run time, interval, attempts, cancelled flag"],
        ["<code>RetryPolicy</code>", "Strategy: delay before attempt n, or give up"],
        ["<code>Scheduler</code>", "Heap of jobs, a clock, <code>run_until(t)</code>"],
    ],
    implementation=[
        code('''
            import heapq
            from dataclasses import dataclass, field
            from itertools import count

            class NoRetry:
                def delay(self, attempt): return None

            class Backoff:
                def __init__(self, base, max_attempts): self.base, self.max = base, max_attempts
                def delay(self, attempt):
                    return self.base * 2 ** (attempt - 1) if attempt < self.max else None

            @dataclass(order=True)
            class Job:
                run_at: float
                seq: int
                name: str = field(compare=False)
                fn: object = field(compare=False)
                every: float | None = field(default=None, compare=False)
                retry: object = field(default_factory=NoRetry, compare=False)
                attempts: int = field(default=0, compare=False)
                cancelled: bool = field(default=False, compare=False)

            class Scheduler:
                def __init__(self):
                    self.now, self.heap, self.jobs, self._seq = 0.0, [], {}, count()
                    self.log = []

                def schedule(self, name, fn, at, every=None, retry=None):
                    job = Job(at, next(self._seq), name, fn, every, retry or NoRetry())
                    self.jobs[name] = job
                    heapq.heappush(self.heap, job)
                    return name

                def cancel(self, name):
                    self.jobs[name].cancelled = True            # lazy deletion from the heap

                def _push(self, job, at):
                    job.run_at, job.seq = at, next(self._seq)
                    heapq.heappush(self.heap, job)

                def run_until(self, t):
                    while self.heap and self.heap[0].run_at <= t:
                        job = heapq.heappop(self.heap)
                        if job.cancelled:
                            continue
                        self.now = job.run_at
                        try:
                            job.fn()
                            job.attempts = 0
                            self.log.append(f"t={self.now:>4}: {job.name} ok")
                            if job.every:
                                self._push(job, self.now + job.every)
                        except Exception as e:
                            job.attempts += 1
                            d = job.retry.delay(job.attempts)
                            self.log.append(f"t={self.now:>4}: {job.name} failed ({e})" +
                                            (f", retry in {d}" if d is not None else ", giving up"))
                            if d is not None:
                                self._push(job, self.now + d)
                    self.now = t

            calls = {"flaky": 0}
            def flaky():
                calls["flaky"] += 1
                if calls["flaky"] < 3:
                    raise ConnectionError("timeout")

            s = Scheduler()
            s.schedule("heartbeat", lambda: None, at=0, every=10)
            s.schedule("report", lambda: None, at=15)
            s.schedule("sync", flaky, at=5, retry=Backoff(base=2, max_attempts=5))
            s.schedule("broken", lambda: 1 / 0, at=12, retry=Backoff(base=1, max_attempts=2))
            s.schedule("cleanup", lambda: None, at=25)
            s.cancel("cleanup")
            s.run_until(30)
            print("\\n".join(s.log))
        '''),
    ],
    extend=[
        "Cron expressions are another way to compute the next run time (a strategy). Running jobs on a thread pool needs the scheduler loop to wait on a condition variable until the earliest run time or a new submission. Across several machines, a scheduler must ensure each job runs once: a database row lock or lease per job, taken before running.",
    ],
    questions=[
        question(
            "Why mark cancelled jobs instead of removing them from the heap?",
            "medium",
            "Removing an arbitrary element from a binary heap is O(n) to find it plus O(log n) to fix the heap. Marking it cancelled is O(1), and the scheduler discards it when it reaches the top. The cost is that cancelled jobs occupy memory until then; if cancellations are frequent, rebuild the heap occasionally or count stale entries.",
        ),
        question(
            "How do you make sure a scheduled job runs exactly once when you have three scheduler instances for availability?",
            "hard",
            "Only one instance may claim each run. Store jobs in a database with their next run time; an instance claims due jobs with an atomic update (<code>UPDATE jobs SET owner=?, lease_until=? WHERE id=? AND (owner IS NULL OR lease_until &lt; now())</code>) or <code>SELECT ... FOR UPDATE SKIP LOCKED</code>. The lease expires if the owner dies, so another instance takes over. Because a crash after running but before recording can still cause a second run, the job itself should be idempotent.",
        ),
    ],
)


KV_STORE = problem(
    id="kv-store-transactions",
    title="Design a Key-Value Store with Nested Transactions",
    level="medium",
    patterns=["Memento", "Command"],
    summary="GET/SET/DELETE plus BEGIN, ROLLBACK and COMMIT with nesting, using a stack of change sets.",
    statement=[
        "Design an in-memory key-value store that supports transactions: <code>BEGIN</code> starts one (they can nest), <code>ROLLBACK</code> undoes everything since the matching BEGIN, <code>COMMIT</code> makes all open transactions permanent. A frequent machine-coding question.",
    ],
    requirements=[
        "<code>set</code>, <code>get</code>, <code>delete</code>, <code>count(value)</code> (how many keys have that value) all O(1). Transactions nest; rollback affects only the innermost; commit applies all. Rollback with no transaction is an error.",
    ],
    choose=[
        ["Undo everything since BEGIN", "Memento (per-key undo log)", "Each transaction records the previous value of each key it first touches"],
        ["Commands executed against the store, possibly from a script", "Command", "Parse lines into operations; easy to test and replay"],
    ],
    choose_notes=["Copying the whole dictionary at BEGIN would also work but costs O(n) per transaction. Recording only the keys a transaction touches makes BEGIN O(1) and rollback proportional to the work done."],
    classes=[
        ["<code>Store</code>", "Data dict, value counts, stack of undo logs"],
        ["<code>run(script)</code>", "Parses command lines and executes them"],
    ],
    implementation=[
        code('''
            from collections import Counter

            MISSING = object()

            class Store:
                def __init__(self):
                    self.data, self.counts, self.tx = {}, Counter(), []   # tx: stack of {key: old}

                def _write(self, key, value):
                    if self.tx and key not in self.tx[-1]:
                        self.tx[-1][key] = self.data.get(key, MISSING)    # memento of first touch
                    old = self.data.get(key, MISSING)
                    if old is not MISSING:
                        self.counts[old] -= 1
                    if value is MISSING:
                        self.data.pop(key, None)
                    else:
                        self.data[key] = value
                        self.counts[value] += 1

                def set(self, k, v): self._write(k, v)
                def delete(self, k): self._write(k, MISSING)
                def get(self, k): return self.data.get(k, "NULL")
                def count(self, v): return self.counts[v]

                def begin(self): self.tx.append({})

                def rollback(self):
                    if not self.tx:
                        return "NO TRANSACTION"
                    undo = self.tx.pop()
                    saved, self.tx = self.tx, []                          # restore without logging
                    for k, old in undo.items():
                        self._write(k, old)
                    self.tx = saved

                def commit(self):
                    if not self.tx:
                        return "NO TRANSACTION"
                    self.tx.clear()

            def run(script):
                s, out = Store(), []
                for line in script.strip().splitlines():
                    line = line.strip()
                    cmd, *args = line.split()
                    result = getattr(s, cmd.lower())(*args)
                    if result is not None:
                        out.append(f"{line:16} -> {result}")
                return out

            print("\\n".join(run("""
                SET a 10
                BEGIN
                SET a 20
                BEGIN
                SET a 30
                DELETE b
                GET a
                ROLLBACK
                GET a
                COUNT 20
                ROLLBACK
                GET a
                COUNT 20
                ROLLBACK
                BEGIN
                SET x 5
                BEGIN
                SET y 5
                COMMIT
                COUNT 5
                ROLLBACK
            """)))
        '''),
    ],
    extend=[
        "Isolation between concurrent clients (each sees its own uncommitted changes) needs per-client transaction stacks and a rule for conflicts at commit: optimistic concurrency with version numbers per key is the natural next step. Persistence adds a write-ahead log of committed change sets.",
    ],
    questions=[
        question(
            "Why record only the first old value of a key in each transaction?",
            "medium",
            "Rollback must restore the value as it was when the transaction began. If a key is set three times inside one transaction, only the value before the first write matters; recording later ones would restore an intermediate value. Storing the first-touch value per key per transaction keeps the log minimal and the rollback correct.",
        ),
        question(
            "How do nested commits work in this design?",
            "medium",
            "Here <code>COMMIT</code> commits everything, which is the classic interview specification: the data dict already holds all changes, so commit simply discards the undo logs. An alternative semantics commits only the innermost transaction into its parent: merge its undo log into the parent's, keeping the parent's entry for any key both touched, so a later rollback of the parent still restores the original value.",
        ),
    ],
)


CONNECTION_POOL = problem(
    id="connection-pool",
    title="Design a Database Connection Pool",
    level="medium",
    patterns=["Object Pool", "Proxy", "Factory"],
    summary="Bounded pool with blocking acquire and timeout, validation on borrow, a proxy that returns itself on close.",
    statement=[
        "Design a connection pool: application threads borrow connections, use them, and give them back. Opening a connection is expensive, the database allows a limited number, and broken connections must not be handed out.",
    ],
    requirements=[
        "Max pool size; connections created lazily up to the max; <code>acquire(timeout)</code> blocks when all are in use and raises on timeout; connections validated on borrow and replaced if dead; <code>close()</code> on a borrowed connection returns it to the pool instead of closing it; usable as a context manager; thread-safe.",
    ],
    choose=[
        ["Expensive objects reused across callers", "Object Pool", "The core of the problem"],
        ["Caller calls <code>conn.close()</code> but it must go back to the pool", "Proxy", "A wrapper intercepts <code>close</code> and forwards everything else"],
        ["How to create a new connection is configurable", "Factory", "The pool receives a factory callable"],
    ],
    classes=[
        ["<code>RawConnection</code>", "The real driver connection (fake here)"],
        ["<code>PooledConnection</code>", "Proxy: forwards calls; <code>close()</code> returns to pool"],
        ["<code>Pool</code>", "Idle stack, in-use count, condition variable, factory, validation"],
    ],
    implementation=[
        code('''
            import threading, time

            class RawConnection:
                opened = 0
                def __init__(self):
                    RawConnection.opened += 1
                    self.id, self.alive = RawConnection.opened, True
                def execute(self, sql):
                    if not self.alive: raise ConnectionError("server closed the connection")
                    return f"conn{self.id}: {sql}"
                def ping(self): return self.alive
                def close(self): self.alive = False

            class PooledConnection:                               # proxy
                def __init__(self, raw, pool): self._raw, self._pool = raw, pool
                def __getattr__(self, name): return getattr(self._raw, name)
                def close(self):
                    if self._raw is not None:
                        self._pool._release(self._raw)
                        self._raw = None                          # further use is a bug
                def __enter__(self): return self
                def __exit__(self, *exc): self.close()

            class Pool:
                def __init__(self, factory, max_size):
                    self.factory, self.max_size = factory, max_size
                    self.idle, self.in_use = [], 0
                    self.cond = threading.Condition()

                def acquire(self, timeout=1.0):
                    deadline = time.monotonic() + timeout
                    with self.cond:
                        while True:
                            while self.idle:
                                raw = self.idle.pop()
                                if raw.ping():                    # validate on borrow
                                    self.in_use += 1
                                    return PooledConnection(raw, self)
                            if self.in_use < self.max_size:
                                self.in_use += 1
                                break                             # create outside the lock
                            remaining = deadline - time.monotonic()
                            if remaining <= 0 or not self.cond.wait(remaining):
                                raise TimeoutError(f"no connection within {timeout}s")
                    try:
                        return PooledConnection(self.factory(), self)
                    except Exception:
                        with self.cond:
                            self.in_use -= 1; self.cond.notify()
                        raise

                def _release(self, raw):
                    with self.cond:
                        self.in_use -= 1
                        self.idle.append(raw)
                        self.cond.notify()

            pool = Pool(RawConnection, max_size=3)
            results, lock = [], threading.Lock()
            def worker(i):
                with pool.acquire(timeout=2) as c:
                    time.sleep(0.01)
                    with lock: results.append(c.execute(f"q{i}"))
            ts = [threading.Thread(target=worker, args=(i,)) for i in range(12)]
            for t in ts: t.start()
            for t in ts: t.join()
            print(len(results), "queries on", RawConnection.opened, "connections")

            dead = pool.acquire(); dead._raw.alive = False; dead.close()   # server killed it
            with pool.acquire() as c:
                print("validated borrow:", c.execute("select 1"))
            holders = [pool.acquire() for _ in range(3)]
            try:
                pool.acquire(timeout=0.05)
            except TimeoutError as e:
                print("TimeoutError:", e)
        '''),
        "Twelve threads ran their queries on three connections. The connection killed by the server was discarded on the next borrow, and the borrower transparently got another one. Creating a connection happens outside the lock, after reserving a slot, so a slow connect does not block threads returning connections.",
    ],
    extend=[
        "Production pools add a minimum idle size (pre-warm), a max lifetime (recycle connections before the server or a proxy kills them), idle timeouts, leak detection (log a stack trace if a connection is held longer than N seconds) and metrics (wait time, pool usage) &mdash; the knobs you see in HikariCP or SQLAlchemy's <code>QueuePool</code>.",
    ],
    questions=[
        question(
            "What happens if a thread forgets to return a connection, and how do you defend against it?",
            "medium",
            "The pool permanently loses a slot; after enough leaks every acquire times out. Defences: hand out connections through a context manager so return is automatic; record the borrower's stack at acquire time and log it when a connection is held longer than a threshold; optionally reclaim connections held past a hard limit (dangerous if the holder is still using it).",
        ),
        question(
            "How big should the pool be?",
            "hard",
            "Smaller than people expect. A database does useful work on roughly as many concurrent queries as it has cores (plus some for I/O waits); beyond that, extra connections just queue inside the database and add context switching and memory. A common starting point is around (2 &times; cores) + disks per database server, divided across all application instances that share it. Measure: if threads wait on the pool while the database CPU is idle, grow it; if the database is saturated, a bigger pool makes latency worse.",
        ),
    ],
)

PROBLEMS = [LRU_CACHE, LOGGER, NOTIFICATION_SERVICE, PUBSUB, TASK_SCHEDULER, KV_STORE, CONNECTION_POOL]
