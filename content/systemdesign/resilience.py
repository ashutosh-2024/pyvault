from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="resilience",
    title="Timeouts, Retries and Circuit Breakers",
    summary="Why retries cause outages, backoff with jitter, retry budgets, circuit breakers, bulkheads and load shedding.",
    intro=[
        "In a system of many services, something is always slow or failing. Resilience patterns decide whether one sick dependency stays a local problem or takes everything down with it. The usual way a small failure becomes a big one is not the failure itself but the reaction to it: callers waiting forever, retrying all at once, and piling more load onto the thing that is already struggling.",
        "Each pattern below is implemented and run against a simulated failing dependency.",
    ],
    sections=[
        section(
            "Timeouts: the first defence",
            "A call without a timeout can wait forever, and while it waits it holds a thread, a connection and memory. When a dependency hangs, callers without timeouts exhaust their pools and stop serving even requests that do not touch that dependency.",
            code('''
                import random

                def run(timeout, pool=50, seconds=60, rps=20, seed=3):
                    """One server, 50 worker threads. The dependency hangs for 30 s at t=10."""
                    rng = random.Random(seed)
                    busy = []                                    # finish times of occupied workers
                    served = rejected = 0
                    for t10 in range(seconds * 10):              # 0.1 s steps
                        t = t10 / 10
                        busy = [f for f in busy if f > t]
                        for _ in range(rps // 10):
                            if len(busy) >= pool:
                                rejected += 1                    # no free worker
                                continue
                            hanging = 10 <= t < 40 and rng.random() < 0.5   # half the calls hit the bad dependency
                            duration = 30.0 if hanging else 0.05
                            busy.append(t + min(duration, timeout))
                            served += 1
                    return served, rejected

                for timeout in (float("inf"), 2.0, 0.5):
                    served, rejected = run(timeout)
                    label = "none" if timeout == float("inf") else f"{timeout} s"
                    print(f"timeout {label:5}  served={served:4}  rejected={rejected:4}")
            '''),
            "Without a timeout, the hung calls occupied every worker within a few seconds, and for the rest of the outage the server rejected every request &mdash; 40% of the minute's traffic, including the half that never needed the broken dependency. A short timeout freed workers fast enough to keep serving.",
            "Choose timeouts from measurements: a little above the dependency's p99 latency, not a round number like 30 s. And make them <strong>budgets</strong> that shrink along a call chain: if the user-facing request has 1 s, a call made after 700 ms of work gets at most the remaining 300 ms (gRPC deadlines propagate this automatically).",
        ),
        section(
            "Retries: helpful in small doses",
            "Retrying a failed call hides transient faults: a dropped packet, a server restarting, a leader election. But retries multiply load. If every layer of a five-deep call chain retries three times, one failing call at the bottom can become 3<sup>5</sup> = 243 attempts.",
            code('''
                def attempts_at_bottom(depth, retries_per_layer):
                    tries = 1 + retries_per_layer
                    return tries ** depth

                for depth in (1, 3, 5):
                    print(f"depth {depth}: {attempts_at_bottom(depth, 2):4} attempts reach the failing service")
            '''),
            "Rules that keep retries safe: retry only <strong>idempotent</strong> operations (or ones carrying an idempotency key); retry only errors that can succeed later (timeouts, 503, connection reset &mdash; not 400 or 404); retry at <em>one</em> layer, usually the one closest to the user; and cap retries with a <strong>budget</strong>, e.g. retries may add at most 10% to the request volume.",
        ),
        section(
            "Exponential backoff with jitter",
            "Retrying immediately hammers a struggling service. Exponential backoff waits longer after each failure (base &times; 2<sup>attempt</sup>, capped). But if a thousand clients failed at the same moment, they also back off in lockstep and retry in synchronised waves. <strong>Jitter</strong> &mdash; randomising each wait &mdash; spreads them out.",
            code('''
                import random
                from collections import Counter

                def schedule(strategy, clients=1000, attempts=4, base=1.0, cap=20.0, seed=1):
                    rng = random.Random(seed)
                    hits = Counter()
                    for _ in range(clients):
                        t = 0.0
                        for a in range(attempts):
                            ceiling = min(cap, base * 2 ** a)
                            if strategy == "none":
                                wait = base
                            elif strategy == "exponential":
                                wait = ceiling
                            else:                                    # "full jitter"
                                wait = rng.uniform(0, ceiling)
                            t += wait
                            hits[int(t * 10)] += 1                   # retries per 100 ms slot
                    return max(hits.values()), len(hits)

                for strategy in ("none", "exponential", "full jitter"):
                    peak, spread = schedule(strategy)
                    print(f"{strategy:12} peak {peak:4} retries in one 100 ms slot, spread over {spread:3} slots")
            '''),
            code('''
                import random

                def backoff(attempt, base=0.1, cap=10.0, rng=random.Random(0)):
                    """AWS 'full jitter': sleep a random time up to the exponential ceiling."""
                    return rng.uniform(0, min(cap, base * 2 ** attempt))

                print([round(backoff(a), 2) for a in range(8)])
            ''', label="the backoff function itself"),
        ),
        section(
            "Circuit breakers",
            "When a dependency is clearly down, continuing to call it wastes time on every request and denies it the breathing room to recover. A circuit breaker watches failures and, past a threshold, <em>opens</em>: calls fail immediately without touching the dependency. After a cool-down it goes <em>half-open</em> and lets a trial call through; success closes it, failure opens it again.",
            code('''
                class CircuitBreaker:
                    def __init__(self, threshold=3, cooldown=5.0):
                        self.threshold, self.cooldown = threshold, cooldown
                        self.state, self.failures, self.opened_at = "closed", 0, 0.0

                    def call(self, fn, now):
                        if self.state == "open":
                            if now - self.opened_at < self.cooldown:
                                return "fast-fail"                   # do not even try
                            self.state = "half-open"                 # allow one trial
                        try:
                            result = fn(now)
                        except Exception:
                            self.failures += 1
                            if self.state == "half-open" or self.failures >= self.threshold:
                                self.state, self.opened_at = "open", now
                            return "error"
                        self.state, self.failures = "closed", 0
                        return result

                def dependency(now):                                 # down between t=2 and t=12
                    if 2 <= now < 12:
                        raise ConnectionError("down")
                    return "ok"

                cb = CircuitBreaker()
                for t in range(0, 20, 1):
                    before = cb.state
                    outcome = cb.call(dependency, float(t))
                    if outcome != "ok" or before != cb.state:
                        print(f"t={t:2}  {before:9} -> {cb.state:9} {outcome}")
            '''),
            "From t = 5 the breaker stopped calling the dead service entirely and failed in microseconds instead of waiting for a timeout. It probed once per cool-down, and closed again as soon as a probe succeeded. Pair the fast failure with a <strong>fallback</strong>: a cached value, a default, a degraded page without recommendations.",
        ),
        section(
            "Bulkheads and load shedding",
            "<strong>Bulkheads</strong> give each dependency its own limited pool of threads or connections, like watertight compartments in a ship. When one dependency hangs, only its pool fills up; calls to everything else still have capacity.",
            code('''
                def serve(pools, requests):
                    """pools: name -> capacity. A hung dependency never releases its slots."""
                    used = {name: 0 for name in pools}
                    results = []
                    for dep in requests:
                        pool = dep if dep in pools else "shared"
                        if used[pool] >= pools[pool]:
                            results.append(f"{dep}:REJECT")
                            continue
                        if dep == "reviews":                          # hangs, slot never freed
                            used[pool] += 1
                        results.append(f"{dep}:ok")
                    return results

                traffic = ["reviews"] * 10 + ["checkout", "search", "checkout"]
                shared = serve({"shared": 8}, traffic)
                bulkheads = serve({"reviews": 4, "shared": 8}, traffic)
                print("one shared pool:", shared[-3:])
                print("with bulkheads :", bulkheads[-3:])
            '''),
            "<strong>Load shedding</strong> is the server-side counterpart: when overloaded, reject work early and cheaply (a fast 503) instead of accepting everything and timing out on all of it. Shed by priority &mdash; drop prefetches and analytics before checkouts &mdash; and use queue age, not just queue length, as the signal: a request that has waited longer than the client will wait is already wasted work.",
            note("Graceful degradation is the product-level version of the same idea: decide in advance which features can disappear under stress (recommendations, live counts, avatars) so the core flow keeps working."),
        ),
    ],
    questions=[
        question(
            "A downstream service had a 30-second blip, but your service was down for 20 minutes. What probably happened?",
            "hard",
            "A <em>metastable</em> failure: the trigger was short, but the system's reaction kept it overloaded after the trigger went away. Typical chain: no or long timeouts filled every worker; clients retried immediately (often at several layers), so when the downstream recovered it faced several times its normal load, failed again, and caused more retries. Caches may also have expired during the blip, sending a stampede to the database.",
            "Fixes: tight timeouts and deadlines, retries at one layer with exponential backoff, jitter and a retry budget, a circuit breaker to stop calling the dependency while it is down, load shedding so an overloaded service rejects cheaply, and request coalescing on cache misses.",
        ),
        question(
            "Which requests is it safe to retry automatically?",
            "medium",
            "Requests whose repetition cannot cause a different outcome. HTTP <code>GET</code>, <code>PUT</code> and <code>DELETE</code> are defined as idempotent; <code>POST</code> is not, unless it carries an idempotency key the server uses to deduplicate. Retry only on errors that can be transient: timeouts, connection failures, 429 (after <code>Retry-After</code>) and 502/503/504. Do not retry 4xx client errors, and be careful with timeouts on non-idempotent writes: the first attempt may have succeeded, which is exactly the case an idempotency key exists for.",
        ),
        question(
            "Why add jitter to exponential backoff?",
            "medium",
            "Clients that failed together back off by the same amounts, so they retry together, in synchronised spikes that can knock the recovering service over again. Randomising each delay (&ldquo;full jitter&rdquo;: uniform between 0 and the exponential ceiling) spreads the retries over the whole interval. The total number of retries is the same; the peak load is a fraction of it.",
        ),
        question(
            "Explain the three states of a circuit breaker and how you would tune it.",
            "medium",
            "<strong>Closed</strong>: calls pass through and failures are counted. <strong>Open</strong>: entered when failures cross a threshold; calls fail immediately for a cool-down period. <strong>Half-open</strong>: after the cool-down, a limited number of trial calls go through; success closes the breaker, failure reopens it. Tune the threshold as a failure <em>rate</em> over a sliding window with a minimum request count (so three failures out of four requests at 3 a.m. do not trip it), the cool-down from how long the dependency typically takes to recover, and the half-open probe count small. Scope breakers per dependency, and ideally per endpoint, so one failing route does not cut off healthy ones.",
        ),
    ],
    refs=[
        ("AWS Architecture Blog: Exponential backoff and jitter", "https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/"),
        ("Google SRE book: Handling overload", "https://sre.google/sre-book/handling-overload/"),
        ("Google SRE book: Addressing cascading failures", "https://sre.google/sre-book/addressing-cascading-failures/"),
        ("Martin Fowler: CircuitBreaker", "https://martinfowler.com/bliki/CircuitBreaker.html"),
        ("Metastable Failures in Distributed Systems (HotOS 2021)", "https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf"),
    ],
)
