from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="rate-limiting",
    title="Rate Limiting",
    summary="Fixed window, sliding log, sliding window counter, token and leaky bucket - implemented, compared, and distributed.",
    intro=[
        "A rate limiter caps how many requests a client may make in a period. It protects a service from abuse and from well-meaning clients stuck in a retry loop, it enforces paid quotas, and it keeps one tenant from starving the others. &ldquo;Design a rate limiter&rdquo; is also one of the most common interview questions, because it is small enough to finish and has real trade-offs.",
        "All five classic algorithms are implemented below with an injectable clock, so the same request pattern can be replayed against each and the differences are visible in the output.",
    ],
    sections=[
        section(
            "Where the limiter lives and what it returns",
            "A limiter can sit in the API gateway (one place, before any service work), in each service (finer-grained limits), or in the client SDK (politeness only &mdash; never trust it). Limits are keyed by something: API key, user id, IP address, or a combination like <code>(user, endpoint)</code>.",
            "When a request is rejected, return <code>429 Too Many Requests</code> with headers that tell a well-behaved client what to do, instead of letting it retry immediately and make things worse:",
            table(
                ["Header", "Meaning"],
                [
                    ["<code>Retry-After: 12</code>", "Seconds until a retry can succeed (standard HTTP)"],
                    ["<code>RateLimit-Limit: 100</code>", "Requests allowed per window"],
                    ["<code>RateLimit-Remaining: 0</code>", "Requests left in the current window"],
                    ["<code>RateLimit-Reset: 12</code>", "Seconds until the quota resets"],
                ],
            ),
        ),
        section(
            "Fixed window counter",
            "Count requests per key in the current window (<code>floor(now / window)</code>) and reject once the count reaches the limit. One integer per key, one increment per request: the cheapest possible limiter. Its flaw is the boundary: a client can send a full quota at the end of one window and another full quota at the start of the next, so twice the limit gets through in a short burst.",
            code('''
                from collections import defaultdict

                class FixedWindow:
                    def __init__(self, limit, window):
                        self.limit, self.window = limit, window
                        self.counts = defaultdict(int)

                    def allow(self, key, now):
                        bucket = (key, int(now // self.window))
                        if self.counts[bucket] >= self.limit:
                            return False
                        self.counts[bucket] += 1
                        return True

                fw = FixedWindow(limit=5, window=10)
                burst = [9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8]
                ok = [fw.allow("ann", t) for t in burst]
                print(f"{sum(ok)} of {len(burst)} allowed within 2 seconds (limit is 5 per 10 s)")
            '''),
        ),
        section(
            "Sliding window log",
            "Keep the timestamp of every accepted request; on each new request, drop timestamps older than the window and compare the count with the limit. Exact, no boundary problem &mdash; but memory grows with the limit (a limit of 10,000 per hour stores up to 10,000 timestamps per client).",
            code('''
                from collections import defaultdict, deque

                class SlidingLog:
                    def __init__(self, limit, window):
                        self.limit, self.window = limit, window
                        self.logs = defaultdict(deque)

                    def allow(self, key, now):
                        log = self.logs[key]
                        while log and log[0] <= now - self.window:
                            log.popleft()                         # outside the window
                        if len(log) >= self.limit:
                            return False
                        log.append(now)
                        return True

                sl = SlidingLog(limit=5, window=10)
                burst = [9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8]
                print(f"{sum(sl.allow('ann', t) for t in burst)} of {len(burst)} allowed")
                print("t=18.9:", sl.allow("ann", 18.9), "| t=19.0:", sl.allow("ann", 19.0))   # 9.0 has slid out
            '''),
        ),
        section(
            "Sliding window counter",
            "The usual production compromise: keep only the counts of the current and previous fixed windows, and estimate the sliding count by weighting the previous window by how much of it still overlaps. Two integers per key, and the estimate is close to exact when traffic within a window is roughly even.",
            code('''
                from collections import defaultdict

                class SlidingCounter:
                    def __init__(self, limit, window):
                        self.limit, self.window = limit, window
                        self.counts = defaultdict(int)

                    def allow(self, key, now):
                        idx = int(now // self.window)
                        elapsed = (now % self.window) / self.window      # fraction of current window
                        prev, cur = self.counts[(key, idx - 1)], self.counts[(key, idx)]
                        estimate = prev * (1 - elapsed) + cur
                        if estimate >= self.limit:
                            return False
                        self.counts[(key, idx)] += 1
                        return True

                sc = SlidingCounter(limit=5, window=10)
                burst = [9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8]
                print(f"{sum(sc.allow('ann', t) for t in burst)} of {len(burst)} allowed")
                for t in (14.0, 15.0, 16.0, 17.0, 18.0):
                    print(f"t={t}: {'allowed' if sc.allow('ann', t) else 'rejected'}")
            '''),
        ),
        section(
            "Token bucket and leaky bucket",
            "A <strong>token bucket</strong> holds up to <code>capacity</code> tokens and refills at <code>rate</code> tokens per second; each request takes one token. It allows bursts up to the capacity, then a steady rate &mdash; usually exactly what an API wants. It needs only two numbers per key (tokens, last refill time), and the refill is computed lazily on each request rather than by a timer.",
            code('''
                class TokenBucket:
                    def __init__(self, capacity, rate):
                        self.capacity, self.rate = capacity, rate
                        self.state = {}                           # key -> (tokens, last_time)

                    def allow(self, key, now, cost=1):
                        tokens, last = self.state.get(key, (self.capacity, now))
                        tokens = min(self.capacity, tokens + (now - last) * self.rate)
                        ok = tokens >= cost
                        self.state[key] = (tokens - cost if ok else tokens, now)
                        return ok

                tb = TokenBucket(capacity=5, rate=0.5)            # bursts of 5, then 1 per 2 s
                times = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 2.6, 3.0, 4.6, 10.0, 10.1]
                print(" ".join(f"{t}:{'Y' if tb.allow('ann', t) else 'n'}" for t in times))
            '''),
            "A <strong>leaky bucket</strong> is a FIFO queue drained at a fixed rate. Requests that find the queue full are rejected; the rest are delayed until their turn. Output is perfectly smooth &mdash; useful in front of a downstream that cannot take bursts (a payment provider, a legacy system) &mdash; at the cost of added latency.",
            code('''
                class LeakyBucket:
                    def __init__(self, capacity, rate):
                        self.capacity, self.interval = capacity, 1 / rate
                        self.next_free = 0.0                       # when the queue next drains a slot

                    def admit(self, now):
                        start = max(now, self.next_free)
                        queued = (start - now) / self.interval    # requests ahead of this one
                        if queued >= self.capacity:
                            return None                           # queue full: reject
                        self.next_free = start + self.interval
                        return start                              # when it will be processed

                lb = LeakyBucket(capacity=3, rate=1)               # 1 per second, 3 may wait
                for t in [0, 0, 0, 0, 0, 2.5]:
                    when = lb.admit(t)
                    print(f"arrive {t:>3}: " + ("rejected" if when is None else f"processed at {when}"))
            '''),
        ),
        section(
            "Comparing the algorithms",
            "The same traffic, replayed against all five: a burst of 20 requests at t = 0, then one request every 0.5 s for 20 seconds. Limits are set to the same long-run rate (10 per 10 s).",
            code('''
                from collections import defaultdict, deque

                class FixedWindow:
                    def __init__(s, limit, window): s.l, s.w, s.c = limit, window, defaultdict(int)
                    def allow(s, now):
                        b = int(now // s.w)
                        if s.c[b] >= s.l: return False
                        s.c[b] += 1; return True

                class SlidingLog:
                    def __init__(s, limit, window): s.l, s.w, s.log = limit, window, deque()
                    def allow(s, now):
                        while s.log and s.log[0] <= now - s.w: s.log.popleft()
                        if len(s.log) >= s.l: return False
                        s.log.append(now); return True

                class SlidingCounter:
                    def __init__(s, limit, window): s.l, s.w, s.c = limit, window, defaultdict(int)
                    def allow(s, now):
                        i = int(now // s.w); f = (now % s.w) / s.w
                        if s.c[i - 1] * (1 - f) + s.c[i] >= s.l: return False
                        s.c[i] += 1; return True

                class TokenBucket:
                    def __init__(s, cap, rate): s.cap, s.r, s.tok, s.t = cap, rate, cap, 0.0
                    def allow(s, now):
                        s.tok = min(s.cap, s.tok + (now - s.t) * s.r); s.t = now
                        if s.tok < 1: return False
                        s.tok -= 1; return True

                traffic = [0.0] * 20 + [i * 0.5 for i in range(1, 41)]
                limiters = {
                    "fixed window": FixedWindow(10, 10),
                    "sliding log": SlidingLog(10, 10),
                    "sliding counter": SlidingCounter(10, 10),
                    "token bucket (cap 10)": TokenBucket(10, 1.0),
                    "token bucket (cap 3)": TokenBucket(3, 1.0),
                }
                for name, lim in limiters.items():
                    allowed = [t for t in traffic if lim.allow(t)]
                    first_5s = sum(t < 5 for t in allowed)
                    print(f"{name:22} total {len(allowed):2}   in first 5 s {first_5s:2}")
            '''),
            table(
                ["Algorithm", "Memory per key", "Bursts", "Accuracy", "Typical use"],
                [
                    ["Fixed window", "1 counter", "Up to 2&times; at boundaries", "Approximate", "Simple quotas (per day / month)"],
                    ["Sliding log", "1 timestamp per request", "Exact limit", "Exact", "Low limits, strict enforcement"],
                    ["Sliding window counter", "2 counters", "Smoothed", "Very close", "General API rate limits"],
                    ["Token bucket", "2 numbers", "Up to capacity, by design", "Exact for its model", "APIs (AWS, Stripe), network shaping"],
                    ["Leaky bucket", "Queue / 1 timestamp", "None: output is smooth", "Exact", "Protecting a fragile downstream"],
                ],
            ),
        ),
        section(
            "Distributed rate limiting",
            "With many gateway instances, each one counting locally would let a client get N&times; the limit by spreading requests across them. The counts must live in a shared store &mdash; almost always Redis &mdash; and the check-and-increment must be atomic, or two instances can both read 99, both allow, and both write 100.",
            code('''
                import threading, time

                class FakeRedis:
                    """INCR is atomic in Redis; GET then SET from two clients is not."""
                    def __init__(self):
                        self.data, self.lock = {}, threading.Lock()
                    def get(self, k):
                        return self.data.get(k, 0)
                    def set(self, k, v):
                        self.data[k] = v
                    def incr(self, k):
                        with self.lock:                      # single-threaded server: atomic
                            self.data[k] = self.data.get(k, 0) + 1
                            return self.data[k]

                LIMIT, REQUESTS = 100, 400
                barrier = threading.Barrier(8)

                def run(atomic):
                    r, allowed = FakeRedis(), []
                    def gateway(n):
                        barrier.wait()
                        for _ in range(n):
                            if atomic:
                                ok = r.incr("ann:window") <= LIMIT
                            else:
                                count = r.get("ann:window")
                                ok = count < LIMIT
                                time.sleep(0.0005)                 # network round trip
                                if ok: r.set("ann:window", count + 1)
                            allowed.append(ok)
                    threads = [threading.Thread(target=gateway, args=(REQUESTS // 8,)) for _ in range(8)]
                    for t in threads: t.start()
                    for t in threads: t.join()
                    return sum(allowed)

                print("GET then SET  :", run(atomic=False) > LIMIT, "(more than the limit got through)")
                print("atomic INCR   :", run(atomic=True), "allowed")
            '''),
            "In real Redis: <code>INCR key</code> plus <code>EXPIRE key window</code> in a <code>MULTI</code> transaction gives a fixed window; a sliding log uses a sorted set (<code>ZADD</code>, <code>ZREMRANGEBYSCORE</code>, <code>ZCARD</code>); a token bucket is a short Lua script, because Redis runs each script atomically.",
            note("Every request now costs a Redis round trip. If Redis is slow or down, fail <em>open</em> (allow) for most APIs so the limiter cannot take the product down; fail closed only where over-use is worse than an outage, such as SMS sending."),
            caveat("At very high volume, exact global counting becomes the bottleneck. Large systems accept approximation: each node keeps local counts and syncs to the shared store every few hundred milliseconds, or gives each node a share of the global limit."),
        ),
    ],
    questions=[
        question(
            "Design a rate limiter for a public API: 100 requests per minute per API key, across 50 gateway servers.",
            "hard",
            "Requirements to confirm: per key or per key and endpoint? Hard limit, or are short bursts acceptable? What latency can the check add (usually &lt; 1&ndash;2 ms)?",
            "Design: a limiter middleware in each gateway; counters in a Redis cluster sharded by API key, so one key's counter always lives on one shard; algorithm: sliding window counter (two keys per API key, atomic via a Lua script) or a token bucket if bursts are allowed. Respond <code>429</code> with <code>Retry-After</code> and <code>RateLimit-*</code> headers. Load limit configuration (per plan, per customer overrides) from a config service and cache it in each gateway.",
            "Failure handling: if Redis is unreachable, fall back to a local in-memory limiter at limit / 50 per gateway (fail open but bounded). Observability: count 429s per key and alert on spikes. Mention the hot-key case: one very heavy key concentrates load on one Redis shard; local pre-aggregation for that key fixes it.",
        ),
        question(
            "What is the boundary problem with fixed windows, and which algorithms avoid it?",
            "medium",
            "A fixed window resets the count at fixed times, so a client can use its full quota just before the reset and again just after it: up to twice the limit in a span much shorter than the window. The sliding log avoids it exactly; the sliding window counter avoids it approximately by weighting the previous window; token and leaky buckets have no windows at all.",
        ),
        question(
            "Token bucket or leaky bucket: when would you pick each?",
            "medium",
            "Token bucket when the <em>caller</em> is the concern and bursts are fine: an API lets a client make 20 quick calls after being idle, then holds it to the sustained rate. Requests are answered immediately, allowed or rejected. Leaky bucket when the <em>downstream</em> is the concern and needs a smooth rate: requests are queued and released at a fixed pace, so the downstream never sees a burst, at the price of queueing delay and a bounded queue that rejects when full.",
        ),
        question(
            "Why is <code>count = GET key; if count &lt; limit: SET key count+1</code> wrong in a distributed limiter?",
            "medium",
            "It is a check-then-act race. Two gateways can both read 99, both decide the request is allowed, and both write 100: two requests admitted for one slot. Under heavy concurrency the overshoot can be large. The check and the increment must be one atomic operation in the store: <code>INCR</code> (which returns the new value, so compare after incrementing), a <code>MULTI/EXEC</code> transaction, or a Lua script that Redis executes atomically.",
        ),
    ],
    refs=[
        ("Stripe: Scaling your API with rate limiters", "https://stripe.com/blog/rate-limiters"),
        ("Cloudflare: How we built rate limiting capable of scaling to millions of domains", "https://blog.cloudflare.com/counting-things-a-lot-of-different-things/"),
        ("IETF draft: RateLimit header fields for HTTP", "https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/"),
        ("Redis: INCR and the rate limiter pattern", "https://redis.io/docs/latest/commands/incr/"),
    ],
)
