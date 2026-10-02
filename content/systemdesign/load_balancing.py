from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="load-balancing",
    title="Load Balancing and Horizontal Scaling",
    summary="L4 vs L7, balancing algorithms simulated, health checks, stateless services, sessions and autoscaling.",
    intro=[
        "Vertical scaling (a bigger machine) is simple and has a ceiling. Horizontal scaling (more machines) has no ceiling but needs something to spread requests across them and to stop sending traffic to the ones that fail. That something is a load balancer, and the way it chooses a server matters more than it looks: a naive choice can leave one server drowning while others idle.",
        "This topic simulates the common algorithms against a realistic workload, then covers what makes a service safe to scale out at all: no local state.",
    ],
    sections=[
        section(
            "Layer 4 vs layer 7",
            "A load balancer can work at the transport layer or the application layer. The difference is what it can see, and therefore what it can decide on.",
            table(
                ["", "L4 (TCP/UDP)", "L7 (HTTP, gRPC)"],
                [
                    ["Sees", "IPs and ports", "Full request: path, headers, cookies, body"],
                    ["Can route on", "Connection tuple only", "URL, host, header, user, A/B bucket"],
                    ["Per-request balancing", "No: a long-lived connection sticks to one server", "Yes, even across one keep-alive or HTTP/2 connection"],
                    ["TLS", "Usually passed through", "Terminated at the balancer"],
                    ["Cost", "Very cheap, millions of connections", "More CPU per request"],
                    ["Examples", "AWS NLB, IPVS, Maglev", "Nginx, Envoy, HAProxy (http mode), AWS ALB"],
                ],
            ),
            "Large systems usually stack them: DNS or anycast spreads users across regions, an L4 layer spreads connections across a fleet of L7 proxies, and the L7 proxies route each request to a service.",
            caveat("gRPC and HTTP/2 multiplex many requests over one long-lived connection. Behind an L4 balancer all of a client's requests go to one server forever, which is a common cause of badly uneven load in microservices. Use an L7 proxy or client-side balancing for them."),
        ),
        section(
            "Balancing algorithms, simulated",
            "The simulation sends 20,000 requests to 10 servers running at about 85% of their combined capacity. Most requests are quick, a few are very slow (the realistic case: a cache miss, a big report), and one server is slower than the rest (a noisy neighbour). We measure the p99 time a request waits in a queue.",
            code('''
                import random, heapq

                def simulate(choose, n_servers=10, n_requests=20_000, seed=1):
                    rng = random.Random(seed)
                    speed = [1.0] * n_servers
                    speed[0] = 0.5                               # one degraded server
                    busy_until = [0.0] * n_servers               # when each server frees up
                    active = [[] for _ in range(n_servers)]      # finish times in flight
                    waits, t = [], 0.0
                    for i in range(n_requests):
                        t += rng.expovariate(5.6)                # ~85% of total capacity
                        for s in range(n_servers):               # drop finished requests
                            while active[s] and active[s][0] <= t:
                                heapq.heappop(active[s])
                        work = rng.expovariate(1.0) if rng.random() < 0.95 else rng.uniform(5, 15)
                        s = choose(i, [len(a) for a in active], rng)
                        start = max(t, busy_until[s])
                        busy_until[s] = start + work / speed[s]
                        heapq.heappush(active[s], busy_until[s])
                        waits.append(start - t)
                    waits.sort()
                    return waits[int(len(waits) * 0.99)]

                strategies = {
                    "random":           lambda i, load, rng: rng.randrange(len(load)),
                    "round robin":      lambda i, load, rng: i % len(load),
                    "power of two":     lambda i, load, rng: min(rng.sample(range(len(load)), 2), key=lambda s: load[s]),
                    "least connections":lambda i, load, rng: min(range(len(load)), key=lambda s: load[s]),
                }
                for name, choose in strategies.items():
                    print(f"{name:18} p99 queueing delay = {simulate(choose):6.1f}")
            '''),
            "Delays are in units of an average request. Random and round robin are blind: they give the half-speed server a tenth of the traffic, which is more than it can process, so its queue grows for the whole run, and they keep stacking requests behind servers stuck on a slow one. Least connections reacts to actual load. <strong>Power of two choices</strong> &mdash; pick two servers at random, send to the less loaded &mdash; gets most of that benefit while only looking at two servers, which is why it is the default in large distributed balancers where no single node has a global view.",
            table(
                ["Algorithm", "Good for", "Weakness"],
                [
                    ["Round robin / weighted RR", "Equal, short requests; servers of known capacity", "Ignores live load"],
                    ["Least connections / least outstanding requests", "Mixed request costs", "Needs accurate, central counts"],
                    ["Power of two choices", "Many balancers, each with partial information", "Slightly worse than global least-loaded"],
                    ["Consistent hashing on a key", "Cache affinity, sticky routing by user", "Hot keys overload one server"],
                    ["Latency-aware (EWMA)", "Heterogeneous or degrading backends", "More state, can oscillate"],
                ],
            ),
        ),
        section(
            "Health checks and outlier ejection",
            "A balancer must stop sending traffic to a broken server quickly, and must not eject healthy ones on a single blip. Two mechanisms work together: <strong>active</strong> health checks (probe <code>/healthz</code> every few seconds; mark down after N failures, up after M successes) and <strong>passive</strong> outlier detection (eject a server whose real requests are failing, then retry it after a back-off).",
            code('''
                class HealthTracker:
                    def __init__(self, fall=3, rise=2):
                        self.fall, self.rise = fall, rise
                        self.healthy, self.streak = True, 0

                    def report(self, ok):
                        if ok == self.healthy:
                            self.streak = 0                     # result agrees with state
                            return self.healthy
                        self.streak += 1
                        needed = self.fall if self.healthy else self.rise
                        if self.streak >= needed:               # enough evidence to flip
                            self.healthy, self.streak = not self.healthy, 0
                        return self.healthy

                h = HealthTracker()
                probes = [1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1]
                states = ["UP" if h.report(bool(p)) else "DOWN" for p in probes]
                for p, s in zip(probes, states):
                    print("ok  " if p else "FAIL", "->", s)
            '''),
            "The single failures at the start did not flip the state (hysteresis), three in a row did, and two consecutive successes brought it back. Health endpoints should check what the server needs to serve traffic (can it reach its database?) but not deep dependencies shared by every server &mdash; otherwise one database blip marks the whole fleet down at once.",
        ),
        section(
            "Stateless services",
            "Horizontal scaling only works if any server can handle any request. That means no request depends on something stored only in one server's memory or disk: sessions, uploaded files, in-process caches that must be consistent, scheduled jobs that should run once.",
            code('''
                import random

                class Server:
                    def __init__(self, name, session_store=None):
                        self.name = name
                        self.local_sessions = {}
                        self.shared = session_store

                    def login(self, user):
                        store = self.shared if self.shared is not None else self.local_sessions
                        store[f"token-{user}"] = user
                        return f"token-{user}"

                    def whoami(self, token):
                        store = self.shared if self.shared is not None else self.local_sessions
                        return store.get(token, "<logged out>")

                random.seed(3)
                for label, shared in (("local memory", None), ("shared store", {})):
                    fleet = [Server(f"s{i}", shared) for i in range(4)]
                    token = random.choice(fleet).login("ann")
                    seen = [random.choice(fleet).whoami(token) for _ in range(6)]
                    print(f"{label:13}", seen)
            '''),
            "Fixes, in order of preference: make the client carry the state (a signed token such as a JWT, so any server can verify it); keep state in a shared store (Redis, a database); or, as a last resort, <strong>sticky sessions</strong> that pin a user to one server. Stickiness reintroduces the problem it hides: when that server dies or is drained for a deploy, its users lose their sessions, and load becomes uneven.",
            note("Twelve-factor rule of thumb: processes are disposable. If killing any one server at any moment would lose data or log users out, the service is not ready to autoscale."),
        ),
        section(
            "Autoscaling",
            "Autoscaling adds servers when a metric crosses a target and removes them when it falls. The metric matters: CPU works for compute-bound services; request concurrency or queue depth tracks I/O-bound ones better. A target-tracking policy computes the desired count directly:",
            code('''
                import math

                def desired(current, metric, target, min_n=2, max_n=50):
                    want = math.ceil(current * metric / target)
                    return max(min_n, min(max_n, want))

                # demand in "servers' worth of CPU": a morning ramp, a peak, then a quiet evening
                demand = [1.8, 2.4, 3.4, 5.0, 6.0, 6.0, 4.0, 2.5, 1.5]

                fleet = 4
                for minute, need in enumerate(demand):
                    cpu = round(100 * need / fleet)          # load spreads over the current fleet
                    new = desired(fleet, cpu, target=60)
                    if new < fleet:
                        new = max(new, fleet - 1)            # scale in slowly
                    print(f"t={minute}  cpu={cpu:3}%  servers {fleet:2} -> {new:2}")
                    fleet = new
            '''),
            "Scale out fast and in slowly: adding capacity late causes an outage, removing it late only costs money. New instances take time to boot and warm caches, so autoscaling smooths daily curves but cannot absorb a sudden spike by itself &mdash; that is what queues, rate limits and load shedding are for.",
        ),
    ],
    questions=[
        question(
            "Why is &ldquo;power of two choices&rdquo; so much better than random, when it only looks at two servers?",
            "hard",
            "With purely random placement, the most loaded of n servers ends up with about <code>log n / log log n</code> more than average, and slow requests pile up behind it. Choosing the lighter of two random servers drops the maximum excess to about <code>log log n</code> &mdash; an exponential improvement &mdash; because a server only receives a request if it beats another random server. It needs no global state and no coordination between balancers, and it avoids the herd effect of everyone picking the single least-loaded server at once based on slightly stale data.",
        ),
        question(
            "Users complain they are randomly logged out after you scaled from one server to three. What happened?",
            "medium",
            "Sessions were stored in server memory. With one server every request found its session; behind a balancer, a request that lands on a different server finds none. Move sessions to a shared store or to signed client-side tokens. Sticky sessions would hide the symptom but come back as logouts on every deploy or crash, and they prevent even balancing.",
        ),
        question(
            "Your gRPC service has 20 replicas, but two of them run at 90% CPU and the rest are idle. Why?",
            "hard",
            "gRPC uses long-lived HTTP/2 connections, and each client multiplexes all of its requests over one connection. An L4 balancer (or Kubernetes' default Service with kube-proxy) balances <em>connections</em>, not requests, so each client sticks to whichever replica it connected to first. A few busy clients produce a few hot replicas. Fixes: an L7 proxy that balances per request (Envoy, a service mesh), client-side load balancing with a resolver that sees all replicas, or periodically recycling connections (a max connection age).",
        ),
        question(
            "What should a health check endpoint check?",
            "medium",
            "Whether <em>this</em> instance can serve traffic: the process is responsive, it has finished starting up and warming caches, and its essential local dependencies work. Distinguish <em>liveness</em> (restart me if this fails: deadlocked, out of memory) from <em>readiness</em> (do not send me traffic yet: starting, draining for shutdown). Avoid failing readiness because a dependency that every instance shares is down: then the whole fleet is removed at once and a partial outage becomes a total one. Keep the check cheap, since it runs every few seconds from every balancer.",
        ),
    ],
    refs=[
        ("The Power of Two Random Choices (Mitzenmacher)", "https://www.eecs.harvard.edu/~michaelm/postscripts/handbook2001.pdf"),
        ("Google: Maglev, a fast and reliable software network load balancer", "https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/"),
        ("Envoy: load balancing overview", "https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/overview"),
        ("The Twelve-Factor App: processes", "https://12factor.net/processes"),
    ],
)
