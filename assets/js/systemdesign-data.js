/* GENERATED FILE - do not edit by hand.
   Source: content/systemdesign/   Build: python3 build.py
   Every code block below was executed and its output captured. */

window.GRAIL_SD = [
  {
    "id": "framework",
    "title": "The Interview Framework and Estimation",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "How to run a 45-minute design interview, the numbers to know, and back-of-envelope capacity estimates.",
    "intro": [
      "A system design interview is not a quiz with one right answer. It is a 45-minute conversation where the interviewer watches how you turn a vague prompt (&ldquo;design Twitter&rdquo;) into a concrete system, which trade-offs you notice, and whether your numbers hold together. Candidates fail far more often from a missing structure than from missing knowledge.",
      "This topic gives the structure, then the estimation skills that make every later design concrete: how many requests per second, how much storage, how many machines, how much downtime a given availability allows. Every number below is computed by the code next to it.",
      "Caching, sharding, consistent hashing and replication are covered in depth in the <strong>Databases</strong> section; the topics here build on them rather than repeat them."
    ],
    "sections": [
      {
        "title": "A repeatable structure",
        "body": [
          {
            "type": "p",
            "html": "Spend the first minutes on scope, not boxes. A design for 1,000 users and one for 500 million are different systems, and the interviewer wants to see you ask."
          },
          {
            "type": "table",
            "head": [
              "Step",
              "Time",
              "What you produce"
            ],
            "rows": [
              [
                "1. Requirements",
                "~5 min",
                "Functional (what users do), non-functional (latency, availability, consistency), explicit <em>out of scope</em>"
              ],
              [
                "2. Estimation",
                "~5 min",
                "Users, QPS (average and peak), read/write ratio, storage per year, bandwidth"
              ],
              [
                "3. API",
                "~5 min",
                "The handful of endpoints or RPCs, with parameters and responses"
              ],
              [
                "4. Data model",
                "~5 min",
                "Entities, keys, access patterns, which store fits each"
              ],
              [
                "5. High-level design",
                "~10 min",
                "Clients, load balancer, services, stores, caches, queues &mdash; one request traced end to end"
              ],
              [
                "6. Deep dives",
                "~10 min",
                "The hardest 1&ndash;2 parts: scaling the hot path, consistency, failure handling"
              ],
              [
                "7. Wrap-up",
                "~5 min",
                "Bottlenecks, what you would monitor, what you would do with 10&times; traffic"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Two habits matter more than any single technology. <strong>State trade-offs out loud</strong>: &ldquo;fan-out on write makes reads fast but celebrity posts expensive, so&hellip;&rdquo;. And <strong>let numbers drive decisions</strong>: you add a cache because reads are 100&times; writes and the database cannot take 50k QPS, not because caches are good."
          },
          {
            "type": "note",
            "text": "If you are unsure what the interviewer wants to dig into, ask: &ldquo;I can go deeper on the feed generation or on storage &mdash; which is more interesting to you?&rdquo;"
          }
        ]
      },
      {
        "title": "Numbers to know",
        "body": [
          {
            "type": "p",
            "html": "You do not need exact figures, only orders of magnitude. The point of the table is the ratios: memory is ~1,000&times; faster than an SSD read, which is ~100&times; faster than a cross-continent round trip."
          },
          {
            "type": "table",
            "head": [
              "Operation",
              "Rough time",
              "Takeaway"
            ],
            "rows": [
              [
                "L1 cache reference",
                "1 ns",
                ""
              ],
              [
                "Main memory reference",
                "100 ns",
                "100&times; L1"
              ],
              [
                "Compress 1 KB (fast codec)",
                "2 &micro;s",
                "CPU is cheap"
              ],
              [
                "Read 1 MB sequentially from memory",
                "3 &micro;s",
                ""
              ],
              [
                "Random SSD read (4 KB)",
                "16&ndash;100 &micro;s",
                "~1,000&times; memory"
              ],
              [
                "Read 1 MB sequentially from SSD",
                "50&ndash;200 &micro;s",
                ""
              ],
              [
                "Round trip in the same datacenter",
                "0.5 ms",
                "Network hops add up"
              ],
              [
                "Disk (HDD) seek",
                "5&ndash;10 ms",
                "Avoid random HDD I/O"
              ],
              [
                "Round trip US &harr; Europe",
                "~80&ndash;150 ms",
                "Put data near users"
              ]
            ]
          },
          {
            "type": "p",
            "html": "And the conversions you use constantly:"
          },
          {
            "type": "code",
            "src": "SECONDS_PER_DAY = 24 * 60 * 60\nprint(f\"seconds per day   : {SECONDS_PER_DAY:,}  (~10^5, use 100k for mental math)\")\nprint(f\"seconds per month : {SECONDS_PER_DAY * 30:,}\")\nprint(f\"seconds per year  : {SECONDS_PER_DAY * 365:,} (~3 * 10^7)\")\n\nfor name, power in ((\"KB\", 1), (\"MB\", 2), (\"GB\", 3), (\"TB\", 4), (\"PB\", 5)):\n    print(f\"1 {name} = 10^{3 * power:<2} bytes (2^{10 * power} = {2 ** (10 * power):,})\")",
            "label": null,
            "output": "seconds per day   : 86,400  (~10^5, use 100k for mental math)\nseconds per month : 2,592,000\nseconds per year  : 31,536,000 (~3 * 10^7)\n1 KB = 10^3  bytes (2^10 = 1,024)\n1 MB = 10^6  bytes (2^20 = 1,048,576)\n1 GB = 10^9  bytes (2^30 = 1,073,741,824)\n1 TB = 10^12 bytes (2^40 = 1,099,511,627,776)\n1 PB = 10^15 bytes (2^50 = 1,125,899,906,842,624)",
            "isError": false
          }
        ]
      },
      {
        "title": "Traffic: from users to QPS",
        "body": [
          {
            "type": "p",
            "html": "Start from daily active users and actions per user, get an average rate, then multiply by a peak factor (2&ndash;10&times;; traffic is never flat). Reads and writes usually differ by orders of magnitude, and that ratio decides most of the architecture."
          },
          {
            "type": "code",
            "src": "def qps(daily_users, actions_per_user, peak_factor=3):\n    avg = daily_users * actions_per_user / 86_400\n    return round(avg), round(avg * peak_factor)\n\ndau = 200_000_000\nwrite_avg, write_peak = qps(dau, actions_per_user=2)       # posts per user per day\nread_avg, read_peak = qps(dau, actions_per_user=100)       # timeline reads\n\nprint(f\"writes: {write_avg:>9,} avg  {write_peak:>9,} peak QPS\")\nprint(f\"reads : {read_avg:>9,} avg  {read_peak:>9,} peak QPS\")\nprint(f\"read:write ratio = {read_avg // write_avg}:1\")",
            "label": null,
            "output": "writes:     4,630 avg     13,889 peak QPS\nreads :   231,481 avg    694,444 peak QPS\nread:write ratio = 49:1",
            "isError": false
          },
          {
            "type": "p",
            "html": "Little's law turns a rate into a concurrency figure, which is what sizes thread pools, connection pools and server counts: <strong>in-flight requests = arrival rate &times; time each one takes</strong>."
          },
          {
            "type": "code",
            "src": "peak_qps = 700_000\nlatency_s = 0.050                      # 50 ms per request\nin_flight = peak_qps * latency_s\nper_server = 500                       # concurrent requests one box handles well\n\nservers = -(-int(in_flight) // per_server)        # ceiling division\nprint(f\"in flight at peak : {in_flight:,.0f} requests\")\nprint(f\"servers needed    : {servers}  (+ headroom for a lost zone: {servers * 3 // 2})\")",
            "label": null,
            "output": "in flight at peak : 35,000 requests\nservers needed    : 70  (+ headroom for a lost zone: 105)",
            "isError": false
          }
        ]
      },
      {
        "title": "Storage and bandwidth",
        "body": [
          {
            "type": "p",
            "html": "Multiply objects per day by bytes per object, then by retention and replication. Separate small metadata (database rows) from large blobs (images, video), because they go to completely different stores."
          },
          {
            "type": "code",
            "src": "def human(n):\n    for unit in (\"B\", \"KB\", \"MB\", \"GB\", \"TB\", \"PB\"):\n        if n < 1000:\n            return f\"{n:,.1f} {unit}\"\n        n /= 1000\n    return f\"{n:,.1f} EB\"\n\nposts_per_day = 400_000_000\ntext_bytes = 300                       # id, author, text, timestamps\nphoto_share, photo_bytes = 0.2, 500_000\n\nmeta_day = posts_per_day * text_bytes\nmedia_day = posts_per_day * photo_share * photo_bytes\nyears, replicas = 5, 3\n\nprint(\"metadata / day :\", human(meta_day))\nprint(\"media / day    :\", human(media_day))\nprint(f\"5 years x{replicas}     :\", human((meta_day + media_day) * 365 * years * replicas))\nprint(\"media egress   :\", human(media_day * 50 / 86_400) + \"/s if each photo is viewed 50x\")",
            "label": null,
            "output": "metadata / day : 120.0 GB\nmedia / day    : 40.0 TB\n5 years x3     : 219.7 PB\nmedia egress   : 23.1 GB/s if each photo is viewed 50x",
            "isError": false
          },
          {
            "type": "p",
            "html": "Conclusions you can draw out loud: metadata fits in a sharded database (hundreds of TB over five years), media belongs in object storage behind a CDN, and egress bandwidth &mdash; not storage &mdash; is the dominant cost."
          }
        ]
      },
      {
        "title": "Availability: what the nines allow",
        "body": [
          {
            "type": "p",
            "html": "Availability targets translate directly into allowed downtime. Every extra nine is ten times less, and it is much more expensive to achieve: redundancy across zones, automated failover, careful deploys."
          },
          {
            "type": "code",
            "src": "minutes_per_year = 365 * 24 * 60\nfor nines in (\"99\", \"99.9\", \"99.95\", \"99.99\", \"99.999\"):\n    down = minutes_per_year * (1 - float(nines) / 100)\n    per_month = down / 12\n    print(f\"{nines + '%':8} {down:9.1f} min/year  {per_month:7.1f} min/month\")",
            "label": null,
            "output": "99%         5256.0 min/year    438.0 min/month\n99.9%        525.6 min/year     43.8 min/month\n99.95%       262.8 min/year     21.9 min/month\n99.99%        52.6 min/year      4.4 min/month\n99.999%        5.3 min/year      0.4 min/month",
            "isError": false
          },
          {
            "type": "p",
            "html": "Dependencies multiply. A request that must pass through five services, each 99.9% available, is at best 99.5% available. Redundancy multiplies the other way: two independent replicas at 99% each are both down only 0.01% of the time."
          },
          {
            "type": "code",
            "src": "from math import prod\n\nchain = [0.999] * 5\nprint(f\"5 services in series : {prod(chain):.4%}\")\n\none = 0.99\nprint(f\"2 replicas, either OK : {1 - (1 - one) ** 2:.4%}\")\nprint(f\"3 replicas, either OK : {1 - (1 - one) ** 3:.4%}\")",
            "label": null,
            "output": "5 services in series : 99.5010%\n2 replicas, either OK : 99.9900%\n3 replicas, either OK : 99.9999%",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "The redundancy formula assumes failures are independent. Replicas in the same rack, the same region or running the same bad deploy fail together, which is why real systems spread replicas across zones and roll out changes gradually."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Estimate the storage needed for a URL shortener over 10 years.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "State assumptions, then compute. 100 million new links per month; each record holds the short code (7 B), the long URL (~100 B on average, up to 2 KB), creation time, owner id and some metadata &mdash; call it 500 B with indexes."
          },
          {
            "type": "code",
            "src": "links_per_month = 100_000_000\nrecord_bytes = 500\nmonths = 12 * 10\ntotal = links_per_month * months * record_bytes\nprint(f\"{links_per_month * months / 1e9:.0f} billion links, {total / 1e12:.0f} TB raw, \"\n      f\"{total * 3 / 1e12:.0f} TB with 3x replication\")\nprint(f\"write QPS ~ {links_per_month / (30 * 86_400):.0f}, read QPS at 100:1 ~ \"\n      f\"{100 * links_per_month / (30 * 86_400):,.0f}\")",
            "label": null,
            "output": "12 billion links, 6 TB raw, 18 TB with 3x replication\nwrite QPS ~ 39, read QPS at 100:1 ~ 3,858",
            "isError": false
          },
          {
            "type": "p",
            "html": "Then interpret: under 20 TB even replicated is small for a sharded key-value store, 12 billion keys means a 7-character base62 code (62<sup>7</sup> &asymp; 3.5 trillion) has plenty of room, and the read rate says to cache popular links."
          }
        ]
      },
      {
        "q": "Why multiply by a peak factor, and how do you choose it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Systems are sized for the busiest minute, not the average one. Traffic follows daily cycles (evening peaks 2&ndash;3&times; the average), weekly cycles, and events (a match, a product launch, a push notification sent to everyone) that can briefly reach 10&times; or more. Choose the factor from the product: a consumer social app might use 3&ndash;5&times;, a ticketing site expecting on-sale moments 50&times;. Say which you picked and why; and design the spike handling (queues, autoscaling, load shedding) rather than provisioning for it permanently."
          }
        ]
      },
      {
        "q": "Your service calls four downstream services, each with 99.9% availability and a long latency tail. What availability can you promise, and what happens to your p99?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Availability at best <code>0.999<sup>4</sup> &asymp; 99.6%</code>, assuming independent failures and no retries. Latency is worse than it looks: the p99 of a sum of four calls is above any one call's p99, and a fan-out that waits for all of several <em>parallel</em> calls is dominated by the slowest one."
          },
          {
            "type": "code",
            "src": "import random\nrandom.seed(7)\n\ndef call():                              # mostly fast, occasionally slow\n    return random.expovariate(1 / 30) if random.random() < 0.98 else random.uniform(100, 400)\n\ndef p99(samples):\n    return sorted(samples)[int(len(samples) * 0.99)]\n\nN = 200_000\nsingle = [call() for _ in range(N)]\nsequential = [sum(call() for _ in range(4)) for _ in range(N // 4)]\nparallel = [max(call() for _ in range(4)) for _ in range(N // 4)]\n\nprint(f\"one call   p99 = {p99(single):5.0f} ms\")\nprint(f\"4 in a row p99 = {p99(sequential):5.0f} ms\")\nprint(f\"4 parallel p99 = {p99(parallel):5.0f} ms   (wait for all four)\")\nprint(f\"availability   = {0.999 ** 4:.2%}\")",
            "label": null,
            "output": "one call   p99 =   256 ms\n4 in a row p99 =   468 ms\n4 parallel p99 =   363 ms   (wait for all four)\navailability   = 99.60%",
            "isError": false
          },
          {
            "type": "p",
            "html": "Mitigations to mention: parallelise independent calls, set timeouts and serve partial results, hedge requests (send a second copy after the p95 time and use whichever returns first), and cache what you can."
          }
        ]
      },
      {
        "q": "What questions do you ask in the first five minutes of &ldquo;design a chat app&rdquo;?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Scope: one-to-one only, or groups too, and how large can a group get? Features: online presence, read receipts, typing indicators, media, search, end-to-end encryption? Scale: daily users, messages per user per day, peak concurrent connections? Guarantees: must messages arrive in order, exactly once, and how long is history kept? Platforms: mobile with intermittent connectivity, web, multiple devices per user that must stay in sync? Each answer removes or adds a whole component (a fan-out service for large groups, an encryption key service, a search index), which is exactly why you ask before drawing."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Jeff Dean: Numbers everyone should know (via High Scalability)",
        "url": "https://highscalability.com/numbers-everyone-should-know/"
      },
      {
        "label": "Google SRE book: Embracing risk (availability)",
        "url": "https://sre.google/sre-book/embracing-risk/"
      },
      {
        "label": "The Tail at Scale (Dean and Barroso)",
        "url": "https://research.google/pubs/the-tail-at-scale/"
      }
    ]
  },
  {
    "id": "load-balancing",
    "title": "Load Balancing and Horizontal Scaling",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "L4 vs L7, balancing algorithms simulated, health checks, stateless services, sessions and autoscaling.",
    "intro": [
      "Vertical scaling (a bigger machine) is simple and has a ceiling. Horizontal scaling (more machines) has no ceiling but needs something to spread requests across them and to stop sending traffic to the ones that fail. That something is a load balancer, and the way it chooses a server matters more than it looks: a naive choice can leave one server drowning while others idle.",
      "This topic simulates the common algorithms against a realistic workload, then covers what makes a service safe to scale out at all: no local state."
    ],
    "sections": [
      {
        "title": "Layer 4 vs layer 7",
        "body": [
          {
            "type": "p",
            "html": "A load balancer can work at the transport layer or the application layer. The difference is what it can see, and therefore what it can decide on."
          },
          {
            "type": "table",
            "head": [
              "",
              "L4 (TCP/UDP)",
              "L7 (HTTP, gRPC)"
            ],
            "rows": [
              [
                "Sees",
                "IPs and ports",
                "Full request: path, headers, cookies, body"
              ],
              [
                "Can route on",
                "Connection tuple only",
                "URL, host, header, user, A/B bucket"
              ],
              [
                "Per-request balancing",
                "No: a long-lived connection sticks to one server",
                "Yes, even across one keep-alive or HTTP/2 connection"
              ],
              [
                "TLS",
                "Usually passed through",
                "Terminated at the balancer"
              ],
              [
                "Cost",
                "Very cheap, millions of connections",
                "More CPU per request"
              ],
              [
                "Examples",
                "AWS NLB, IPVS, Maglev",
                "Nginx, Envoy, HAProxy (http mode), AWS ALB"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Large systems usually stack them: DNS or anycast spreads users across regions, an L4 layer spreads connections across a fleet of L7 proxies, and the L7 proxies route each request to a service."
          },
          {
            "type": "caveat",
            "text": "gRPC and HTTP/2 multiplex many requests over one long-lived connection. Behind an L4 balancer all of a client's requests go to one server forever, which is a common cause of badly uneven load in microservices. Use an L7 proxy or client-side balancing for them."
          }
        ]
      },
      {
        "title": "Balancing algorithms, simulated",
        "body": [
          {
            "type": "p",
            "html": "The simulation sends 20,000 requests to 10 servers running at about 85% of their combined capacity. Most requests are quick, a few are very slow (the realistic case: a cache miss, a big report), and one server is slower than the rest (a noisy neighbour). We measure the p99 time a request waits in a queue."
          },
          {
            "type": "code",
            "src": "import random, heapq\n\ndef simulate(choose, n_servers=10, n_requests=20_000, seed=1):\n    rng = random.Random(seed)\n    speed = [1.0] * n_servers\n    speed[0] = 0.5                               # one degraded server\n    busy_until = [0.0] * n_servers               # when each server frees up\n    active = [[] for _ in range(n_servers)]      # finish times in flight\n    waits, t = [], 0.0\n    for i in range(n_requests):\n        t += rng.expovariate(5.6)                # ~85% of total capacity\n        for s in range(n_servers):               # drop finished requests\n            while active[s] and active[s][0] <= t:\n                heapq.heappop(active[s])\n        work = rng.expovariate(1.0) if rng.random() < 0.95 else rng.uniform(5, 15)\n        s = choose(i, [len(a) for a in active], rng)\n        start = max(t, busy_until[s])\n        busy_until[s] = start + work / speed[s]\n        heapq.heappush(active[s], busy_until[s])\n        waits.append(start - t)\n    waits.sort()\n    return waits[int(len(waits) * 0.99)]\n\nstrategies = {\n    \"random\":           lambda i, load, rng: rng.randrange(len(load)),\n    \"round robin\":      lambda i, load, rng: i % len(load),\n    \"power of two\":     lambda i, load, rng: min(rng.sample(range(len(load)), 2), key=lambda s: load[s]),\n    \"least connections\":lambda i, load, rng: min(range(len(load)), key=lambda s: load[s]),\n}\nfor name, choose in strategies.items():\n    print(f\"{name:18} p99 queueing delay = {simulate(choose):6.1f}\")",
            "label": null,
            "output": "random             p99 queueing delay = 2095.0\nround robin        p99 queueing delay = 2234.3\npower of two       p99 queueing delay =   23.0\nleast connections  p99 queueing delay =   15.1",
            "isError": false
          },
          {
            "type": "p",
            "html": "Delays are in units of an average request. Random and round robin are blind: they give the half-speed server a tenth of the traffic, which is more than it can process, so its queue grows for the whole run, and they keep stacking requests behind servers stuck on a slow one. Least connections reacts to actual load. <strong>Power of two choices</strong> &mdash; pick two servers at random, send to the less loaded &mdash; gets most of that benefit while only looking at two servers, which is why it is the default in large distributed balancers where no single node has a global view."
          },
          {
            "type": "table",
            "head": [
              "Algorithm",
              "Good for",
              "Weakness"
            ],
            "rows": [
              [
                "Round robin / weighted RR",
                "Equal, short requests; servers of known capacity",
                "Ignores live load"
              ],
              [
                "Least connections / least outstanding requests",
                "Mixed request costs",
                "Needs accurate, central counts"
              ],
              [
                "Power of two choices",
                "Many balancers, each with partial information",
                "Slightly worse than global least-loaded"
              ],
              [
                "Consistent hashing on a key",
                "Cache affinity, sticky routing by user",
                "Hot keys overload one server"
              ],
              [
                "Latency-aware (EWMA)",
                "Heterogeneous or degrading backends",
                "More state, can oscillate"
              ]
            ]
          }
        ]
      },
      {
        "title": "Health checks and outlier ejection",
        "body": [
          {
            "type": "p",
            "html": "A balancer must stop sending traffic to a broken server quickly, and must not eject healthy ones on a single blip. Two mechanisms work together: <strong>active</strong> health checks (probe <code>/healthz</code> every few seconds; mark down after N failures, up after M successes) and <strong>passive</strong> outlier detection (eject a server whose real requests are failing, then retry it after a back-off)."
          },
          {
            "type": "code",
            "src": "class HealthTracker:\n    def __init__(self, fall=3, rise=2):\n        self.fall, self.rise = fall, rise\n        self.healthy, self.streak = True, 0\n\n    def report(self, ok):\n        if ok == self.healthy:\n            self.streak = 0                     # result agrees with state\n            return self.healthy\n        self.streak += 1\n        needed = self.fall if self.healthy else self.rise\n        if self.streak >= needed:               # enough evidence to flip\n            self.healthy, self.streak = not self.healthy, 0\n        return self.healthy\n\nh = HealthTracker()\nprobes = [1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1]\nstates = [\"UP\" if h.report(bool(p)) else \"DOWN\" for p in probes]\nfor p, s in zip(probes, states):\n    print(\"ok  \" if p else \"FAIL\", \"->\", s)",
            "label": null,
            "output": "ok   -> UP\nFAIL -> UP\nok   -> UP\nFAIL -> UP\nFAIL -> UP\nFAIL -> DOWN\nok   -> DOWN\nFAIL -> DOWN\nok   -> DOWN\nok   -> UP\nok   -> UP",
            "isError": false
          },
          {
            "type": "p",
            "html": "The single failures at the start did not flip the state (hysteresis), three in a row did, and two consecutive successes brought it back. Health endpoints should check what the server needs to serve traffic (can it reach its database?) but not deep dependencies shared by every server &mdash; otherwise one database blip marks the whole fleet down at once."
          }
        ]
      },
      {
        "title": "Stateless services",
        "body": [
          {
            "type": "p",
            "html": "Horizontal scaling only works if any server can handle any request. That means no request depends on something stored only in one server's memory or disk: sessions, uploaded files, in-process caches that must be consistent, scheduled jobs that should run once."
          },
          {
            "type": "code",
            "src": "import random\n\nclass Server:\n    def __init__(self, name, session_store=None):\n        self.name = name\n        self.local_sessions = {}\n        self.shared = session_store\n\n    def login(self, user):\n        store = self.shared if self.shared is not None else self.local_sessions\n        store[f\"token-{user}\"] = user\n        return f\"token-{user}\"\n\n    def whoami(self, token):\n        store = self.shared if self.shared is not None else self.local_sessions\n        return store.get(token, \"<logged out>\")\n\nrandom.seed(3)\nfor label, shared in ((\"local memory\", None), (\"shared store\", {})):\n    fleet = [Server(f\"s{i}\", shared) for i in range(4)]\n    token = random.choice(fleet).login(\"ann\")\n    seen = [random.choice(fleet).whoami(token) for _ in range(6)]\n    print(f\"{label:13}\", seen)",
            "label": null,
            "output": "local memory  ['ann', '<logged out>', '<logged out>', '<logged out>', '<logged out>', '<logged out>']\nshared store  ['ann', 'ann', 'ann', 'ann', 'ann', 'ann']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Fixes, in order of preference: make the client carry the state (a signed token such as a JWT, so any server can verify it); keep state in a shared store (Redis, a database); or, as a last resort, <strong>sticky sessions</strong> that pin a user to one server. Stickiness reintroduces the problem it hides: when that server dies or is drained for a deploy, its users lose their sessions, and load becomes uneven."
          },
          {
            "type": "note",
            "text": "Twelve-factor rule of thumb: processes are disposable. If killing any one server at any moment would lose data or log users out, the service is not ready to autoscale."
          }
        ]
      },
      {
        "title": "Autoscaling",
        "body": [
          {
            "type": "p",
            "html": "Autoscaling adds servers when a metric crosses a target and removes them when it falls. The metric matters: CPU works for compute-bound services; request concurrency or queue depth tracks I/O-bound ones better. A target-tracking policy computes the desired count directly:"
          },
          {
            "type": "code",
            "src": "import math\n\ndef desired(current, metric, target, min_n=2, max_n=50):\n    want = math.ceil(current * metric / target)\n    return max(min_n, min(max_n, want))\n\n# demand in \"servers' worth of CPU\": a morning ramp, a peak, then a quiet evening\ndemand = [1.8, 2.4, 3.4, 5.0, 6.0, 6.0, 4.0, 2.5, 1.5]\n\nfleet = 4\nfor minute, need in enumerate(demand):\n    cpu = round(100 * need / fleet)          # load spreads over the current fleet\n    new = desired(fleet, cpu, target=60)\n    if new < fleet:\n        new = max(new, fleet - 1)            # scale in slowly\n    print(f\"t={minute}  cpu={cpu:3}%  servers {fleet:2} -> {new:2}\")\n    fleet = new",
            "label": null,
            "output": "t=0  cpu= 45%  servers  4 ->  3\nt=1  cpu= 80%  servers  3 ->  4\nt=2  cpu= 85%  servers  4 ->  6\nt=3  cpu= 83%  servers  6 ->  9\nt=4  cpu= 67%  servers  9 -> 11\nt=5  cpu= 55%  servers 11 -> 11\nt=6  cpu= 36%  servers 11 -> 10\nt=7  cpu= 25%  servers 10 ->  9\nt=8  cpu= 17%  servers  9 ->  8",
            "isError": false
          },
          {
            "type": "p",
            "html": "Scale out fast and in slowly: adding capacity late causes an outage, removing it late only costs money. New instances take time to boot and warm caches, so autoscaling smooths daily curves but cannot absorb a sudden spike by itself &mdash; that is what queues, rate limits and load shedding are for."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why is &ldquo;power of two choices&rdquo; so much better than random, when it only looks at two servers?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "With purely random placement, the most loaded of n servers ends up with about <code>log n / log log n</code> more than average, and slow requests pile up behind it. Choosing the lighter of two random servers drops the maximum excess to about <code>log log n</code> &mdash; an exponential improvement &mdash; because a server only receives a request if it beats another random server. It needs no global state and no coordination between balancers, and it avoids the herd effect of everyone picking the single least-loaded server at once based on slightly stale data."
          }
        ]
      },
      {
        "q": "Users complain they are randomly logged out after you scaled from one server to three. What happened?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Sessions were stored in server memory. With one server every request found its session; behind a balancer, a request that lands on a different server finds none. Move sessions to a shared store or to signed client-side tokens. Sticky sessions would hide the symptom but come back as logouts on every deploy or crash, and they prevent even balancing."
          }
        ]
      },
      {
        "q": "Your gRPC service has 20 replicas, but two of them run at 90% CPU and the rest are idle. Why?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "gRPC uses long-lived HTTP/2 connections, and each client multiplexes all of its requests over one connection. An L4 balancer (or Kubernetes' default Service with kube-proxy) balances <em>connections</em>, not requests, so each client sticks to whichever replica it connected to first. A few busy clients produce a few hot replicas. Fixes: an L7 proxy that balances per request (Envoy, a service mesh), client-side load balancing with a resolver that sees all replicas, or periodically recycling connections (a max connection age)."
          }
        ]
      },
      {
        "q": "What should a health check endpoint check?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Whether <em>this</em> instance can serve traffic: the process is responsive, it has finished starting up and warming caches, and its essential local dependencies work. Distinguish <em>liveness</em> (restart me if this fails: deadlocked, out of memory) from <em>readiness</em> (do not send me traffic yet: starting, draining for shutdown). Avoid failing readiness because a dependency that every instance shares is down: then the whole fleet is removed at once and a partial outage becomes a total one. Keep the check cheap, since it runs every few seconds from every balancer."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "The Power of Two Random Choices (Mitzenmacher)",
        "url": "https://www.eecs.harvard.edu/~michaelm/postscripts/handbook2001.pdf"
      },
      {
        "label": "Google: Maglev, a fast and reliable software network load balancer",
        "url": "https://research.google/pubs/maglev-a-fast-and-reliable-software-network-load-balancer/"
      },
      {
        "label": "Envoy: load balancing overview",
        "url": "https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/overview"
      },
      {
        "label": "The Twelve-Factor App: processes",
        "url": "https://12factor.net/processes"
      }
    ]
  },
  {
    "id": "api-design",
    "title": "API Design: Pagination, Idempotency, Versioning",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "REST vs gRPC vs GraphQL, offset vs cursor pagination, idempotency keys, ETags and optimistic concurrency, versioning.",
    "intro": [
      "The API is the part of a design that is hardest to change later, because other people's code depends on it. Interviewers use the API step to see whether you think about clients: how they page through results, what happens when they retry, how two of them editing the same thing are kept from overwriting each other, and how the API evolves without breaking them.",
      "Each of those has a standard answer, and each is demonstrated below against a small in-memory service."
    ],
    "sections": [
      {
        "title": "Choosing a style",
        "body": [
          {
            "type": "p",
            "html": "Most designs use more than one: a public REST or GraphQL API at the edge, gRPC between internal services, and webhooks or a stream for pushing events out."
          },
          {
            "type": "table",
            "head": [
              "",
              "REST / JSON over HTTP",
              "gRPC (Protobuf over HTTP/2)",
              "GraphQL"
            ],
            "rows": [
              [
                "Shape",
                "Resources and verbs",
                "Typed procedures",
                "One endpoint, client-specified queries"
              ],
              [
                "Contract",
                "OpenAPI (optional)",
                "<code>.proto</code> files, generated clients",
                "Schema, introspection"
              ],
              [
                "Payload",
                "Text, human-readable",
                "Binary, compact, fast",
                "JSON, exactly the fields asked for"
              ],
              [
                "Streaming",
                "SSE / WebSockets bolted on",
                "Built in, both directions",
                "Subscriptions"
              ],
              [
                "HTTP caching",
                "Natural (GET, ETag, CDN)",
                "None",
                "Hard: everything is POST to one URL"
              ],
              [
                "Best for",
                "Public APIs, browsers, simple CRUD",
                "Internal service-to-service calls",
                "Many client types needing different shapes"
              ]
            ]
          },
          {
            "type": "p",
            "html": "For a design interview, sketch REST endpoints with nouns for resources and HTTP verbs for actions (<code>POST /v1/orders</code>, <code>GET /v1/orders/{id}</code>, <code>GET /v1/users/{id}/orders?cursor=...</code>), and say what each returns and which status codes matter."
          }
        ]
      },
      {
        "title": "Offset pagination and why it breaks",
        "body": [
          {
            "type": "p",
            "html": "<code>?offset=40&amp;limit=20</code> is easy to build: <code>ORDER BY created DESC LIMIT 20 OFFSET 40</code>. It has two problems. The database still reads and discards all skipped rows, so deep pages get slower. And if rows are inserted or deleted while a client is paging, items shift between pages: the client sees duplicates or silently misses rows."
          },
          {
            "type": "code",
            "src": "def page_offset(items, offset, limit=3):\n    return items[offset:offset + limit]\n\ndef read_two_pages(change):\n    feed = [f\"post{i}\" for i in range(10, 0, -1)]   # newest first: post10 ... post1\n    seen = page_offset(feed, 0)\n    change(feed)                                    # happens between the requests\n    return seen + page_offset(feed, 3)\n\ninserted = read_two_pages(lambda f: f.insert(0, \"post11\"))\ndeleted = read_two_pages(lambda f: f.remove(\"post9\"))\nprint(\"new post arrives:\", inserted)                # post8 shown twice\nprint(\"old post deleted:\", deleted)                 # post7 never shown",
            "label": null,
            "output": "new post arrives: ['post10', 'post9', 'post8', 'post8', 'post7', 'post6']\nold post deleted: ['post10', 'post9', 'post8', 'post6', 'post5', 'post4']",
            "isError": false
          }
        ]
      },
      {
        "title": "Cursor (keyset) pagination",
        "body": [
          {
            "type": "p",
            "html": "A cursor encodes <em>where the last page ended</em> &mdash; the sort key of its last item &mdash; and the next query asks for items strictly after it: <code>WHERE (created, id) &lt; (:c, :id) ORDER BY created DESC, id DESC LIMIT 20</code>. With an index on the sort key every page costs the same, however deep, and inserts at the front cannot shift later pages."
          },
          {
            "type": "code",
            "src": "import base64, json\n\nposts = [{\"id\": i, \"ts\": 1000 + i // 2} for i in range(1, 11)]   # ties in ts on purpose\n\ndef encode(item):\n    return base64.urlsafe_b64encode(json.dumps([item[\"ts\"], item[\"id\"]]).encode()).decode()\n\ndef page_cursor(cursor=None, limit=3):\n    rows = sorted(posts, key=lambda p: (p[\"ts\"], p[\"id\"]), reverse=True)\n    if cursor:\n        ts, pid = json.loads(base64.urlsafe_b64decode(cursor))\n        rows = [p for p in rows if (p[\"ts\"], p[\"id\"]) < (ts, pid)]   # strictly after\n    page = rows[:limit]\n    return [p[\"id\"] for p in page], (encode(page[-1]) if len(page) == limit else None)\n\nseen, cursor, first = [], None, True\nwhile first or cursor:\n    ids, cursor = page_cursor(cursor)\n    seen += ids\n    if first:\n        posts += [{\"id\": 11, \"ts\": 1006}, {\"id\": 12, \"ts\": 1006}]  # arrive mid-paging\n        first = False\nprint(\"pages:\", seen)\nprint(\"no duplicates:\", len(seen) == len(set(seen)), \"| all old posts seen:\", set(range(1, 11)) <= set(seen))",
            "label": null,
            "output": "pages: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]\nno duplicates: True | all old posts seen: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "Two details make it correct: the sort key must be <strong>unique</strong>, so ties are broken by appending the id (two posts in the same second would otherwise be skipped or repeated), and the cursor should be <strong>opaque</strong> (encoded) so clients do not depend on its contents and you can change it later. The trade-off: no jumping to page 37, only next and previous."
          },
          {
            "type": "note",
            "text": "Use offsets only for small, stable, admin-style lists. For feeds, timelines, search results and exports, use cursors."
          }
        ]
      },
      {
        "title": "Idempotency keys",
        "body": [
          {
            "type": "p",
            "html": "Networks fail after the server has done the work but before the client hears back. The client cannot tell &ldquo;not done&rdquo; from &ldquo;done, response lost&rdquo;, so it retries &mdash; and a naive <code>POST /payments</code> charges twice. An <strong>idempotency key</strong> is a client-generated unique id sent with the request; the server stores the response under that key and returns the stored response for any retry."
          },
          {
            "type": "code",
            "src": "import uuid\n\nclass PaymentsAPI:\n    def __init__(self):\n        self.charges, self.responses = [], {}\n\n    def create_charge(self, amount, idempotency_key=None):\n        if idempotency_key in self.responses:\n            return self.responses[idempotency_key]          # replay, no new charge\n        self.charges.append(amount)\n        response = {\"status\": 201, \"charge_id\": len(self.charges), \"amount\": amount}\n        if idempotency_key:\n            self.responses[idempotency_key] = response      # same transaction as the charge\n        return response\n\ndef client(api, use_key):\n    key = str(uuid.uuid4()) if use_key else None\n    for attempt in range(3):                                # first two responses \"time out\"\n        response = api.create_charge(50, idempotency_key=key)\n        if attempt == 2:\n            return response\n\nfor use_key in (False, True):\n    api = PaymentsAPI()\n    r = client(api, use_key)\n    print(f\"idempotency key={use_key!s:5}  charges made={len(api.charges)}  final response={r}\")",
            "label": null,
            "output": "idempotency key=False  charges made=3  final response={'status': 201, 'charge_id': 3, 'amount': 50}\nidempotency key=True   charges made=1  final response={'status': 201, 'charge_id': 1, 'amount': 50}",
            "isError": false
          },
          {
            "type": "p",
            "html": "In production the stored response and the business write go in one transaction; keys expire after a day or so; a retry that arrives while the first request is still running gets a <code>409</code> rather than running in parallel; and a retry with the same key but a different body is rejected, because it is a client bug."
          }
        ]
      },
      {
        "title": "Conditional requests and optimistic concurrency",
        "body": [
          {
            "type": "p",
            "html": "Two clients read a document, both edit it, both save: the second save silently erases the first &mdash; a <em>lost update</em>. HTTP's answer is a version tag. <code>GET</code> returns an <code>ETag</code>; the client sends it back as <code>If-Match</code> on <code>PUT</code>; the server applies the write only if the resource has not changed since, and otherwise returns <code>412 Precondition Failed</code> so the client can re-read and merge."
          },
          {
            "type": "code",
            "src": "import hashlib, json\n\nclass DocStore:\n    def __init__(self, doc):\n        self.doc = doc\n\n    def etag(self):\n        return hashlib.sha1(json.dumps(self.doc, sort_keys=True).encode()).hexdigest()[:8]\n\n    def get(self):\n        return dict(self.doc), self.etag()\n\n    def put(self, new_doc, if_match=None):\n        if if_match is not None and if_match != self.etag():\n            return 412\n        self.doc = new_doc\n        return 200\n\nfor use_etag in (False, True):\n    store = DocStore({\"title\": \"Plan\", \"owner\": \"ann\"})\n    a_doc, a_tag = store.get()\n    b_doc, b_tag = store.get()\n    a_doc[\"title\"] = \"Plan v2\"\n    b_doc[\"owner\"] = \"bob\"\n    ra = store.put(a_doc, a_tag if use_etag else None)\n    rb = store.put(b_doc, b_tag if use_etag else None)\n    print(f\"ETag={use_etag!s:5} A:{ra} B:{rb} final={store.doc}\")",
            "label": null,
            "output": "ETag=False A:200 B:200 final={'title': 'Plan', 'owner': 'bob'}\nETag=True  A:200 B:412 final={'title': 'Plan v2', 'owner': 'ann'}",
            "isError": false
          },
          {
            "type": "p",
            "html": "The same version check in a database is <code>UPDATE ... SET ..., version = version + 1 WHERE id = ? AND version = ?</code>: zero rows updated means someone else won. ETags also save bandwidth on reads: <code>If-None-Match</code> lets the server answer <code>304 Not Modified</code> with no body."
          }
        ]
      },
      {
        "title": "Versioning and evolution",
        "body": [
          {
            "type": "p",
            "html": "Most changes should not need a new version. <strong>Additive</strong> changes are backward compatible: new endpoints, new optional fields in requests, new fields in responses (clients must ignore unknown fields). <strong>Breaking</strong> changes need a new version: removing or renaming a field, changing a type or meaning, making an optional field required, changing error codes."
          },
          {
            "type": "table",
            "head": [
              "Strategy",
              "Example",
              "Notes"
            ],
            "rows": [
              [
                "URL path",
                "<code>/v1/orders</code>, <code>/v2/orders</code>",
                "Obvious, cache-friendly; the most common choice"
              ],
              [
                "Header",
                "<code>Accept: application/vnd.acme.v2+json</code>",
                "Clean URLs, harder to test in a browser"
              ],
              [
                "Dated versions",
                "<code>Stripe-Version: 2024-06-20</code>",
                "Each account pinned to the version it integrated against; the server translates"
              ],
              [
                "Field-level evolution",
                "Protobuf field numbers, GraphQL <code>@deprecated</code>",
                "Avoids whole-API versions"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Whichever you choose, announce deprecations with dates, emit a <code>Deprecation</code>/<code>Sunset</code> header, measure who still calls the old version, and keep it running until they have moved."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Design the API for a timeline: users fetch their home feed, newest first, and scroll back for days.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>GET /v1/users/{id}/feed?limit=20&amp;cursor=...</code> returning <code>{items: [...], next_cursor: \"...\"}</code>, with <code>next_cursor</code> absent on the last page. Cursor pagination, because new posts arrive constantly at the top and offsets would duplicate items; the cursor encodes the (score or timestamp, post id) of the last item, opaque to clients. Cap <code>limit</code> server-side. To check for new posts at the top, a separate <code>?since=&lt;newest id&gt;</code> query or a push channel. Each item carries enough for rendering (author name, avatar URL, counts) to avoid one request per item &mdash; or the response includes a side-loaded map of users."
          }
        ]
      },
      {
        "q": "Why is offset pagination slow on deep pages?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>OFFSET 100000 LIMIT 20</code> makes the database produce the first 100,020 rows in sort order and throw away 100,000 of them: cost grows linearly with page depth, even with an index. Keyset pagination starts from an index position (<code>WHERE (ts, id) &lt; (?, ?)</code>), so every page is an index seek plus 20 rows."
          }
        ]
      },
      {
        "q": "A mobile client retries <code>POST /orders</code> after a timeout and creates two orders. Fix it.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Make the operation idempotent. The client generates a unique key per logical order (when the user taps &ldquo;place order&rdquo;, not per HTTP attempt) and sends it as <code>Idempotency-Key</code>. The server, in the same transaction that creates the order, records the key with the response; a retry with the same key returns the stored response with no new order. Alternatively, let the client create the order id itself (a UUID) and make <code>PUT /orders/{id}</code> the create call, which is naturally idempotent."
          }
        ]
      },
      {
        "q": "What is the difference between <code>PUT</code> and <code>PATCH</code>, and which are idempotent?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<code>PUT</code> replaces the whole resource with the representation sent; repeating it leaves the same state, so it is idempotent. <code>PATCH</code> applies a partial change; whether it is idempotent depends on the patch: &ldquo;set title to X&rdquo; is, &ldquo;append item&rdquo; or &ldquo;increment counter&rdquo; is not. <code>GET</code>, <code>HEAD</code>, <code>PUT</code> and <code>DELETE</code> are idempotent by definition; <code>POST</code> is not. Idempotent methods are the ones clients and proxies may retry automatically."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Stripe: Idempotent requests",
        "url": "https://docs.stripe.com/api/idempotent_requests"
      },
      {
        "label": "Use the Index, Luke: Paging through results (keyset pagination)",
        "url": "https://use-the-index-luke.com/no-offset"
      },
      {
        "label": "MDN: HTTP conditional requests",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests"
      },
      {
        "label": "Google: API design guide",
        "url": "https://cloud.google.com/apis/design"
      }
    ]
  },
  {
    "id": "rate-limiting",
    "title": "Rate Limiting",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Fixed window, sliding log, sliding window counter, token and leaky bucket - implemented, compared, and distributed.",
    "intro": [
      "A rate limiter caps how many requests a client may make in a period. It protects a service from abuse and from well-meaning clients stuck in a retry loop, it enforces paid quotas, and it keeps one tenant from starving the others. &ldquo;Design a rate limiter&rdquo; is also one of the most common interview questions, because it is small enough to finish and has real trade-offs.",
      "All five classic algorithms are implemented below with an injectable clock, so the same request pattern can be replayed against each and the differences are visible in the output."
    ],
    "sections": [
      {
        "title": "Where the limiter lives and what it returns",
        "body": [
          {
            "type": "p",
            "html": "A limiter can sit in the API gateway (one place, before any service work), in each service (finer-grained limits), or in the client SDK (politeness only &mdash; never trust it). Limits are keyed by something: API key, user id, IP address, or a combination like <code>(user, endpoint)</code>."
          },
          {
            "type": "p",
            "html": "When a request is rejected, return <code>429 Too Many Requests</code> with headers that tell a well-behaved client what to do, instead of letting it retry immediately and make things worse:"
          },
          {
            "type": "table",
            "head": [
              "Header",
              "Meaning"
            ],
            "rows": [
              [
                "<code>Retry-After: 12</code>",
                "Seconds until a retry can succeed (standard HTTP)"
              ],
              [
                "<code>RateLimit-Limit: 100</code>",
                "Requests allowed per window"
              ],
              [
                "<code>RateLimit-Remaining: 0</code>",
                "Requests left in the current window"
              ],
              [
                "<code>RateLimit-Reset: 12</code>",
                "Seconds until the quota resets"
              ]
            ]
          }
        ]
      },
      {
        "title": "Fixed window counter",
        "body": [
          {
            "type": "p",
            "html": "Count requests per key in the current window (<code>floor(now / window)</code>) and reject once the count reaches the limit. One integer per key, one increment per request: the cheapest possible limiter. Its flaw is the boundary: a client can send a full quota at the end of one window and another full quota at the start of the next, so twice the limit gets through in a short burst."
          },
          {
            "type": "code",
            "src": "from collections import defaultdict\n\nclass FixedWindow:\n    def __init__(self, limit, window):\n        self.limit, self.window = limit, window\n        self.counts = defaultdict(int)\n\n    def allow(self, key, now):\n        bucket = (key, int(now // self.window))\n        if self.counts[bucket] >= self.limit:\n            return False\n        self.counts[bucket] += 1\n        return True\n\nfw = FixedWindow(limit=5, window=10)\nburst = [9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8]\nok = [fw.allow(\"ann\", t) for t in burst]\nprint(f\"{sum(ok)} of {len(burst)} allowed within 2 seconds (limit is 5 per 10 s)\")",
            "label": null,
            "output": "10 of 10 allowed within 2 seconds (limit is 5 per 10 s)",
            "isError": false
          }
        ]
      },
      {
        "title": "Sliding window log",
        "body": [
          {
            "type": "p",
            "html": "Keep the timestamp of every accepted request; on each new request, drop timestamps older than the window and compare the count with the limit. Exact, no boundary problem &mdash; but memory grows with the limit (a limit of 10,000 per hour stores up to 10,000 timestamps per client)."
          },
          {
            "type": "code",
            "src": "from collections import defaultdict, deque\n\nclass SlidingLog:\n    def __init__(self, limit, window):\n        self.limit, self.window = limit, window\n        self.logs = defaultdict(deque)\n\n    def allow(self, key, now):\n        log = self.logs[key]\n        while log and log[0] <= now - self.window:\n            log.popleft()                         # outside the window\n        if len(log) >= self.limit:\n            return False\n        log.append(now)\n        return True\n\nsl = SlidingLog(limit=5, window=10)\nburst = [9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8]\nprint(f\"{sum(sl.allow('ann', t) for t in burst)} of {len(burst)} allowed\")\nprint(\"t=18.9:\", sl.allow(\"ann\", 18.9), \"| t=19.0:\", sl.allow(\"ann\", 19.0))   # 9.0 has slid out",
            "label": null,
            "output": "5 of 10 allowed\nt=18.9: False | t=19.0: True",
            "isError": false
          }
        ]
      },
      {
        "title": "Sliding window counter",
        "body": [
          {
            "type": "p",
            "html": "The usual production compromise: keep only the counts of the current and previous fixed windows, and estimate the sliding count by weighting the previous window by how much of it still overlaps. Two integers per key, and the estimate is close to exact when traffic within a window is roughly even."
          },
          {
            "type": "code",
            "src": "from collections import defaultdict\n\nclass SlidingCounter:\n    def __init__(self, limit, window):\n        self.limit, self.window = limit, window\n        self.counts = defaultdict(int)\n\n    def allow(self, key, now):\n        idx = int(now // self.window)\n        elapsed = (now % self.window) / self.window      # fraction of current window\n        prev, cur = self.counts[(key, idx - 1)], self.counts[(key, idx)]\n        estimate = prev * (1 - elapsed) + cur\n        if estimate >= self.limit:\n            return False\n        self.counts[(key, idx)] += 1\n        return True\n\nsc = SlidingCounter(limit=5, window=10)\nburst = [9.0, 9.2, 9.4, 9.6, 9.8, 10.0, 10.2, 10.4, 10.6, 10.8]\nprint(f\"{sum(sc.allow('ann', t) for t in burst)} of {len(burst)} allowed\")\nfor t in (14.0, 15.0, 16.0, 17.0, 18.0):\n    print(f\"t={t}: {'allowed' if sc.allow('ann', t) else 'rejected'}\")",
            "label": null,
            "output": "6 of 10 allowed\nt=14.0: allowed\nt=15.0: allowed\nt=16.0: rejected\nt=17.0: allowed\nt=18.0: rejected",
            "isError": false
          }
        ]
      },
      {
        "title": "Token bucket and leaky bucket",
        "body": [
          {
            "type": "p",
            "html": "A <strong>token bucket</strong> holds up to <code>capacity</code> tokens and refills at <code>rate</code> tokens per second; each request takes one token. It allows bursts up to the capacity, then a steady rate &mdash; usually exactly what an API wants. It needs only two numbers per key (tokens, last refill time), and the refill is computed lazily on each request rather than by a timer."
          },
          {
            "type": "code",
            "src": "class TokenBucket:\n    def __init__(self, capacity, rate):\n        self.capacity, self.rate = capacity, rate\n        self.state = {}                           # key -> (tokens, last_time)\n\n    def allow(self, key, now, cost=1):\n        tokens, last = self.state.get(key, (self.capacity, now))\n        tokens = min(self.capacity, tokens + (now - last) * self.rate)\n        ok = tokens >= cost\n        self.state[key] = (tokens - cost if ok else tokens, now)\n        return ok\n\ntb = TokenBucket(capacity=5, rate=0.5)            # bursts of 5, then 1 per 2 s\ntimes = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 2.6, 3.0, 4.6, 10.0, 10.1]\nprint(\" \".join(f\"{t}:{'Y' if tb.allow('ann', t) else 'n'}\" for t in times))",
            "label": null,
            "output": "0:Y 0.1:Y 0.2:Y 0.3:Y 0.4:Y 0.5:n 0.6:n 2.6:Y 3.0:n 4.6:Y 10.0:Y 10.1:Y",
            "isError": false
          },
          {
            "type": "p",
            "html": "A <strong>leaky bucket</strong> is a FIFO queue drained at a fixed rate. Requests that find the queue full are rejected; the rest are delayed until their turn. Output is perfectly smooth &mdash; useful in front of a downstream that cannot take bursts (a payment provider, a legacy system) &mdash; at the cost of added latency."
          },
          {
            "type": "code",
            "src": "class LeakyBucket:\n    def __init__(self, capacity, rate):\n        self.capacity, self.interval = capacity, 1 / rate\n        self.next_free = 0.0                       # when the queue next drains a slot\n\n    def admit(self, now):\n        start = max(now, self.next_free)\n        queued = (start - now) / self.interval    # requests ahead of this one\n        if queued >= self.capacity:\n            return None                           # queue full: reject\n        self.next_free = start + self.interval\n        return start                              # when it will be processed\n\nlb = LeakyBucket(capacity=3, rate=1)               # 1 per second, 3 may wait\nfor t in [0, 0, 0, 0, 0, 2.5]:\n    when = lb.admit(t)\n    print(f\"arrive {t:>3}: \" + (\"rejected\" if when is None else f\"processed at {when}\"))",
            "label": null,
            "output": "arrive   0: processed at 0\narrive   0: processed at 1.0\narrive   0: processed at 2.0\narrive   0: rejected\narrive   0: rejected\narrive 2.5: processed at 3.0",
            "isError": false
          }
        ]
      },
      {
        "title": "Comparing the algorithms",
        "body": [
          {
            "type": "p",
            "html": "The same traffic, replayed against all five: a burst of 20 requests at t = 0, then one request every 0.5 s for 20 seconds. Limits are set to the same long-run rate (10 per 10 s)."
          },
          {
            "type": "code",
            "src": "from collections import defaultdict, deque\n\nclass FixedWindow:\n    def __init__(s, limit, window): s.l, s.w, s.c = limit, window, defaultdict(int)\n    def allow(s, now):\n        b = int(now // s.w)\n        if s.c[b] >= s.l: return False\n        s.c[b] += 1; return True\n\nclass SlidingLog:\n    def __init__(s, limit, window): s.l, s.w, s.log = limit, window, deque()\n    def allow(s, now):\n        while s.log and s.log[0] <= now - s.w: s.log.popleft()\n        if len(s.log) >= s.l: return False\n        s.log.append(now); return True\n\nclass SlidingCounter:\n    def __init__(s, limit, window): s.l, s.w, s.c = limit, window, defaultdict(int)\n    def allow(s, now):\n        i = int(now // s.w); f = (now % s.w) / s.w\n        if s.c[i - 1] * (1 - f) + s.c[i] >= s.l: return False\n        s.c[i] += 1; return True\n\nclass TokenBucket:\n    def __init__(s, cap, rate): s.cap, s.r, s.tok, s.t = cap, rate, cap, 0.0\n    def allow(s, now):\n        s.tok = min(s.cap, s.tok + (now - s.t) * s.r); s.t = now\n        if s.tok < 1: return False\n        s.tok -= 1; return True\n\ntraffic = [0.0] * 20 + [i * 0.5 for i in range(1, 41)]\nlimiters = {\n    \"fixed window\": FixedWindow(10, 10),\n    \"sliding log\": SlidingLog(10, 10),\n    \"sliding counter\": SlidingCounter(10, 10),\n    \"token bucket (cap 10)\": TokenBucket(10, 1.0),\n    \"token bucket (cap 3)\": TokenBucket(3, 1.0),\n}\nfor name, lim in limiters.items():\n    allowed = [t for t in traffic if lim.allow(t)]\n    first_5s = sum(t < 5 for t in allowed)\n    print(f\"{name:22} total {len(allowed):2}   in first 5 s {first_5s:2}\")",
            "label": null,
            "output": "fixed window           total 21   in first 5 s 10\nsliding log            total 21   in first 5 s 10\nsliding counter        total 20   in first 5 s 10\ntoken bucket (cap 10)  total 30   in first 5 s 14\ntoken bucket (cap 3)   total 23   in first 5 s  7",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Algorithm",
              "Memory per key",
              "Bursts",
              "Accuracy",
              "Typical use"
            ],
            "rows": [
              [
                "Fixed window",
                "1 counter",
                "Up to 2&times; at boundaries",
                "Approximate",
                "Simple quotas (per day / month)"
              ],
              [
                "Sliding log",
                "1 timestamp per request",
                "Exact limit",
                "Exact",
                "Low limits, strict enforcement"
              ],
              [
                "Sliding window counter",
                "2 counters",
                "Smoothed",
                "Very close",
                "General API rate limits"
              ],
              [
                "Token bucket",
                "2 numbers",
                "Up to capacity, by design",
                "Exact for its model",
                "APIs (AWS, Stripe), network shaping"
              ],
              [
                "Leaky bucket",
                "Queue / 1 timestamp",
                "None: output is smooth",
                "Exact",
                "Protecting a fragile downstream"
              ]
            ]
          }
        ]
      },
      {
        "title": "Distributed rate limiting",
        "body": [
          {
            "type": "p",
            "html": "With many gateway instances, each one counting locally would let a client get N&times; the limit by spreading requests across them. The counts must live in a shared store &mdash; almost always Redis &mdash; and the check-and-increment must be atomic, or two instances can both read 99, both allow, and both write 100."
          },
          {
            "type": "code",
            "src": "import threading, time\n\nclass FakeRedis:\n    \"\"\"INCR is atomic in Redis; GET then SET from two clients is not.\"\"\"\n    def __init__(self):\n        self.data, self.lock = {}, threading.Lock()\n    def get(self, k):\n        return self.data.get(k, 0)\n    def set(self, k, v):\n        self.data[k] = v\n    def incr(self, k):\n        with self.lock:                      # single-threaded server: atomic\n            self.data[k] = self.data.get(k, 0) + 1\n            return self.data[k]\n\nLIMIT, REQUESTS = 100, 400\nbarrier = threading.Barrier(8)\n\ndef run(atomic):\n    r, allowed = FakeRedis(), []\n    def gateway(n):\n        barrier.wait()\n        for _ in range(n):\n            if atomic:\n                ok = r.incr(\"ann:window\") <= LIMIT\n            else:\n                count = r.get(\"ann:window\")\n                ok = count < LIMIT\n                time.sleep(0.0005)                 # network round trip\n                if ok: r.set(\"ann:window\", count + 1)\n            allowed.append(ok)\n    threads = [threading.Thread(target=gateway, args=(REQUESTS // 8,)) for _ in range(8)]\n    for t in threads: t.start()\n    for t in threads: t.join()\n    return sum(allowed)\n\nprint(\"GET then SET  :\", run(atomic=False) > LIMIT, \"(more than the limit got through)\")\nprint(\"atomic INCR   :\", run(atomic=True), \"allowed\")",
            "label": null,
            "output": "GET then SET  : True (more than the limit got through)\natomic INCR   : 100 allowed",
            "isError": false
          },
          {
            "type": "p",
            "html": "In real Redis: <code>INCR key</code> plus <code>EXPIRE key window</code> in a <code>MULTI</code> transaction gives a fixed window; a sliding log uses a sorted set (<code>ZADD</code>, <code>ZREMRANGEBYSCORE</code>, <code>ZCARD</code>); a token bucket is a short Lua script, because Redis runs each script atomically."
          },
          {
            "type": "note",
            "text": "Every request now costs a Redis round trip. If Redis is slow or down, fail <em>open</em> (allow) for most APIs so the limiter cannot take the product down; fail closed only where over-use is worse than an outage, such as SMS sending."
          },
          {
            "type": "caveat",
            "text": "At very high volume, exact global counting becomes the bottleneck. Large systems accept approximation: each node keeps local counts and syncs to the shared store every few hundred milliseconds, or gives each node a share of the global limit."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Design a rate limiter for a public API: 100 requests per minute per API key, across 50 gateway servers.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Requirements to confirm: per key or per key and endpoint? Hard limit, or are short bursts acceptable? What latency can the check add (usually &lt; 1&ndash;2 ms)?"
          },
          {
            "type": "p",
            "html": "Design: a limiter middleware in each gateway; counters in a Redis cluster sharded by API key, so one key's counter always lives on one shard; algorithm: sliding window counter (two keys per API key, atomic via a Lua script) or a token bucket if bursts are allowed. Respond <code>429</code> with <code>Retry-After</code> and <code>RateLimit-*</code> headers. Load limit configuration (per plan, per customer overrides) from a config service and cache it in each gateway."
          },
          {
            "type": "p",
            "html": "Failure handling: if Redis is unreachable, fall back to a local in-memory limiter at limit / 50 per gateway (fail open but bounded). Observability: count 429s per key and alert on spikes. Mention the hot-key case: one very heavy key concentrates load on one Redis shard; local pre-aggregation for that key fixes it."
          }
        ]
      },
      {
        "q": "What is the boundary problem with fixed windows, and which algorithms avoid it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A fixed window resets the count at fixed times, so a client can use its full quota just before the reset and again just after it: up to twice the limit in a span much shorter than the window. The sliding log avoids it exactly; the sliding window counter avoids it approximately by weighting the previous window; token and leaky buckets have no windows at all."
          }
        ]
      },
      {
        "q": "Token bucket or leaky bucket: when would you pick each?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Token bucket when the <em>caller</em> is the concern and bursts are fine: an API lets a client make 20 quick calls after being idle, then holds it to the sustained rate. Requests are answered immediately, allowed or rejected. Leaky bucket when the <em>downstream</em> is the concern and needs a smooth rate: requests are queued and released at a fixed pace, so the downstream never sees a burst, at the price of queueing delay and a bounded queue that rejects when full."
          }
        ]
      },
      {
        "q": "Why is <code>count = GET key; if count &lt; limit: SET key count+1</code> wrong in a distributed limiter?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "It is a check-then-act race. Two gateways can both read 99, both decide the request is allowed, and both write 100: two requests admitted for one slot. Under heavy concurrency the overshoot can be large. The check and the increment must be one atomic operation in the store: <code>INCR</code> (which returns the new value, so compare after incrementing), a <code>MULTI/EXEC</code> transaction, or a Lua script that Redis executes atomically."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Stripe: Scaling your API with rate limiters",
        "url": "https://stripe.com/blog/rate-limiters"
      },
      {
        "label": "Cloudflare: How we built rate limiting capable of scaling to millions of domains",
        "url": "https://blog.cloudflare.com/counting-things-a-lot-of-different-things/"
      },
      {
        "label": "IETF draft: RateLimit header fields for HTTP",
        "url": "https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/"
      },
      {
        "label": "Redis: INCR and the rate limiter pattern",
        "url": "https://redis.io/docs/latest/commands/incr/"
      }
    ]
  },
  {
    "id": "unique-ids",
    "title": "Unique ID Generation",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Auto-increment, UUIDv4 vs v7, Snowflake IDs, ticket servers, and why ID order matters to your database.",
    "intro": [
      "Every stored object needs an identifier, and in a distributed system several machines must create them at once without ever colliding. The choice looks trivial and is not: it decides whether IDs leak business data, whether they sort by time, how big your indexes are, and how fast inserts are.",
      "This topic builds the main options &mdash; database sequences, random UUIDs, time-ordered UUIDs and Snowflake-style IDs &mdash; and measures their properties."
    ],
    "sections": [
      {
        "title": "Requirements first",
        "body": [
          {
            "type": "p",
            "html": "Ask which of these properties matter before picking a scheme:"
          },
          {
            "type": "table",
            "head": [
              "Property",
              "Why it matters"
            ],
            "rows": [
              [
                "Unique without coordination",
                "Any server can mint IDs during a network partition, with no shared counter on the hot path"
              ],
              [
                "Roughly time-ordered",
                "Newest-first queries and pagination by ID; B-tree inserts land at the right edge"
              ],
              [
                "Compact",
                "64-bit integers are half the size of 128-bit UUIDs in every index and foreign key"
              ],
              [
                "Not guessable",
                "Sequential IDs let anyone enumerate <code>/invoice/1001</code>, <code>/invoice/1002</code>&hellip; and reveal volumes"
              ],
              [
                "Generated offline",
                "Mobile clients create objects before syncing"
              ]
            ]
          }
        ]
      },
      {
        "title": "Database auto-increment",
        "body": [
          {
            "type": "p",
            "html": "The simplest scheme: the database hands out 1, 2, 3&hellip;. Compact, ordered, and guaranteed unique &mdash; on one database. With several writers you either route every insert through one node (a bottleneck and single point of failure) or give each node a disjoint stream."
          },
          {
            "type": "code",
            "src": "class Node:\n    \"\"\"Each of k nodes owns the IDs congruent to its index mod k.\"\"\"\n    def __init__(self, index, k):\n        self.next, self.step = index + 1, k\n\n    def new_id(self):\n        value, self.next = self.next, self.next + self.step\n        return value\n\na, b, c = (Node(i, 3) for i in range(3))\nids = [a.new_id(), a.new_id(), b.new_id(), c.new_id(), a.new_id(), c.new_id()]\nprint(ids, \"unique:\", len(set(ids)) == len(ids))",
            "label": null,
            "output": "[1, 4, 2, 3, 7, 6] unique: True",
            "isError": false
          },
          {
            "type": "p",
            "html": "This is how MySQL's <code>auto_increment_increment</code>/<code>offset</code> multi-primary setups work. Adding a fourth node later changes the step for everyone, and the IDs are guessable. A <strong>ticket server</strong> (Flickr's design) is a variant: a dedicated database whose only job is incrementing a counter, often handing out blocks of 1,000 IDs at a time so callers rarely need to ask."
          }
        ]
      },
      {
        "title": "UUIDv4: random",
        "body": [
          {
            "type": "p",
            "html": "A version-4 UUID is 122 random bits plus 6 version bits. No coordination, generated anywhere, unguessable. Collisions are not impossible, just absurdly unlikely: by the birthday bound they only become likely around 2<sup>61</sup> IDs (a 50% chance needs about 2.7 &times; 10<sup>18</sup>)."
          },
          {
            "type": "code",
            "src": "import math, uuid\n\nu = uuid.uuid4()\nprint(u, \"version\", u.version, \"| bits of randomness: 122\")\n\ndef collision_probability(n, bits=122):\n    return -math.expm1(-n * n / (2 * 2 ** bits))     # birthday approximation\n\nfor n in (10**9, 10**12, 10**15, 2**61):\n    print(f\"{n:>22,} ids -> P(any collision) = {collision_probability(n):.2e}\")",
            "label": null,
            "output": "d71f4e29-a1d6-419d-b100-9522acc9335e version 4 | bits of randomness: 122\n         1,000,000,000 ids -> P(any collision) = 9.40e-20\n     1,000,000,000,000 ids -> P(any collision) = 9.40e-14\n 1,000,000,000,000,000 ids -> P(any collision) = 9.40e-08\n2,305,843,009,213,693,952 ids -> P(any collision) = 3.93e-01",
            "isError": false
          },
          {
            "type": "p",
            "html": "The cost is order. Random IDs scatter inserts across the whole primary-key index: each insert touches a random leaf page, so the working set is the entire index rather than its right edge, pages split everywhere, and caches miss. On large tables with a clustered primary key (InnoDB, SQL Server) that is a well-known insert slowdown."
          }
        ]
      },
      {
        "title": "Time-ordered IDs: UUIDv7 and ULID",
        "body": [
          {
            "type": "p",
            "html": "UUIDv7 (RFC 9562, 2024) puts a 48-bit Unix millisecond timestamp in the first bits and fills the rest with randomness. It is still a standard 128-bit UUID, generated without coordination, but IDs created later sort later, so inserts go to the right edge of the index like an auto-increment."
          },
          {
            "type": "code",
            "src": "import os, time, uuid\n\ndef uuid7(ms=None):\n    ms = int(time.time() * 1000) if ms is None else ms\n    rand = int.from_bytes(os.urandom(10), \"big\")\n    value = (ms & ((1 << 48) - 1)) << 80                     # 48-bit timestamp\n    value |= 0x7 << 76                                       # version 7\n    value |= ((rand >> 62) & 0xFFF) << 64                    # 12 random bits\n    value |= 0b10 << 62                                      # RFC variant\n    value |= rand & ((1 << 62) - 1)                          # 62 random bits\n    return uuid.UUID(int=value)\n\nbase = 1_700_000_000_000\nids = [uuid7(base + i) for i in (0, 1, 2, 3)]\nfor u in ids:\n    print(u, \"version\", u.version, \"ms\", u.int >> 80)\nprint(\"sorted by value == creation order:\", sorted(ids) == ids)\nprint(\"v4 ids sorted == creation order?  \", (lambda v: sorted(v) == v)([uuid.uuid4() for _ in range(20)]))",
            "label": null,
            "output": "018bcfe5-6800-7472-8316-8f30592466a6 version 7 ms 1700000000000\n018bcfe5-6801-7bbc-be5a-2f2fec742791 version 7 ms 1700000000001\n018bcfe5-6802-7d27-801f-0fa44782ca61 version 7 ms 1700000000002\n018bcfe5-6803-7cce-89a6-aed01d766fc5 version 7 ms 1700000000003\nsorted by value == creation order: True\nv4 ids sorted == creation order?   False",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Python 3.14 ships <code>uuid.uuid7()</code> in the standard library; the hand-written version above shows the bit layout. ULID is an older community format with the same idea (48-bit time + 80 random bits) encoded in 26 Crockford base-32 characters."
          }
        ]
      },
      {
        "title": "Snowflake IDs",
        "body": [
          {
            "type": "p",
            "html": "Twitter's Snowflake packs a 64-bit integer: 41 bits of milliseconds since a custom epoch, 10 bits of machine id, 12 bits of per-millisecond sequence. Each machine can mint 4,096 IDs per millisecond with no coordination beyond assigning machine ids once; the IDs are time-ordered, fit in a <code>BIGINT</code>, and the creation time can be read back out of the ID."
          },
          {
            "type": "code",
            "src": "import threading\n\nEPOCH = 1_288_834_974_657                      # Twitter's epoch (Nov 2010), in ms\n\nclass Snowflake:\n    def __init__(self, machine_id, clock):\n        assert 0 <= machine_id < 1024\n        self.machine, self.clock = machine_id, clock\n        self.last_ms, self.seq = -1, 0\n        self.lock = threading.Lock()\n\n    def next_id(self):\n        with self.lock:\n            ms = self.clock()\n            if ms < self.last_ms:\n                raise RuntimeError(\"clock moved backwards\")\n            if ms == self.last_ms:\n                self.seq = (self.seq + 1) & 0xFFF\n                if self.seq == 0:                   # 4096 used this ms: wait\n                    while ms <= self.last_ms:\n                        ms = self.clock()\n            else:\n                self.seq = 0\n            self.last_ms = ms\n            return ((ms - EPOCH) << 22) | (self.machine << 12) | self.seq\n\ndef decode(i):\n    return {\"ms\": (i >> 22) + EPOCH, \"machine\": (i >> 12) & 0x3FF, \"seq\": i & 0xFFF}\n\nfake_now = [1_700_000_000_000]\ngen = Snowflake(machine_id=37, clock=lambda: fake_now[0])\nids = [gen.next_id() for _ in range(3)]\nfake_now[0] += 1\nids.append(gen.next_id())\nfor i in ids:\n    print(i, decode(i))\nprint(\"bits used:\", max(ids).bit_length(), \"of 63 (sign bit kept clear)\")\nprint(\"years of ids in 41 bits:\", round(2**41 / (1000 * 3600 * 24 * 365.25), 1))",
            "label": null,
            "output": "1724551110456397824 {'ms': 1700000000000, 'machine': 37, 'seq': 0}\n1724551110456397825 {'ms': 1700000000000, 'machine': 37, 'seq': 1}\n1724551110456397826 {'ms': 1700000000000, 'machine': 37, 'seq': 2}\n1724551110460592128 {'ms': 1700000000001, 'machine': 37, 'seq': 0}\nbits used: 61 of 63 (sign bit kept clear)\nyears of ids in 41 bits: 69.7",
            "isError": false
          },
          {
            "type": "p",
            "html": "Two operational details carry the risk. Machine ids must be unique, so they are leased from ZooKeeper/etcd or derived from a stable pod ordinal, never picked at random. And the scheme depends on clocks: if NTP moves a clock backwards, the generator must refuse (as above) or wait, or it could repeat IDs."
          }
        ]
      },
      {
        "title": "Comparison",
        "body": [
          {
            "type": "p",
            "html": "Insert locality, measured: how many distinct B-tree &ldquo;pages&rdquo; (blocks of 100 consecutive keys in sorted order) the last 1,000 inserts touched, out of 100,000 rows."
          },
          {
            "type": "code",
            "src": "import random, uuid, bisect\n\ndef pages_touched(keys, page=100, recent=1000):\n    order = sorted(keys)\n    rank = {k: i for i, k in enumerate(order)}\n    return len({rank[k] // page for k in keys[-recent:]})\n\nn = 100_000\nsequential = list(range(n))\nv4 = [uuid.uuid4().int for _ in range(n)]\nms0, rng = 1_700_000_000_000, random.Random(0)\nv7_like = [((ms0 + i // 10) << 80) | rng.getrandbits(80) for i in range(n)]   # 10 ids per ms\n\nfor name, keys in ((\"auto-increment\", sequential), (\"UUIDv7\", v7_like), (\"UUIDv4\", v4)):\n    print(f\"{name:15} recent inserts touched {pages_touched(keys):4} of {n // 100} pages\")",
            "label": null,
            "output": "auto-increment  recent inserts touched   10 of 1000 pages\nUUIDv7          recent inserts touched   10 of 1000 pages\nUUIDv4          recent inserts touched  612 of 1000 pages",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Scheme",
              "Size",
              "Ordered",
              "Coordination",
              "Guessable",
              "Notes"
            ],
            "rows": [
              [
                "Auto-increment",
                "64 bit",
                "Yes",
                "Central counter",
                "Yes",
                "Simple; bottleneck across writers"
              ],
              [
                "UUIDv4",
                "128 bit",
                "No",
                "None",
                "No",
                "Scattered index inserts"
              ],
              [
                "UUIDv7 / ULID",
                "128 bit",
                "By ms",
                "None",
                "Partly (time visible)",
                "Good default for new systems"
              ],
              [
                "Snowflake",
                "64 bit",
                "By ms",
                "Machine-id assignment",
                "Partly",
                "Compact; depends on clocks"
              ],
              [
                "Ticket server / blocks",
                "64 bit",
                "Mostly",
                "Central, amortised",
                "Yes",
                "Block hand-out avoids the hot path"
              ]
            ]
          },
          {
            "type": "note",
            "text": "Use an ordered ID as the primary key, and if IDs are exposed in URLs where enumeration matters, expose a separate random public id (or a v4 UUID) rather than the internal key."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Design an ID generator for a service that creates 50,000 objects per second across 100 servers, where IDs must be 64-bit and roughly sortable by time.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Snowflake layout: 41-bit millisecond timestamp (69 years from a custom epoch), 10-bit worker id (1,024 workers), 12-bit sequence (4,096 per ms per worker). Capacity per worker is 4 million IDs per second, far above 500 per second each. Worker ids come from a coordination service lease, or from a stable ordinal such as a StatefulSet index, and are released on shutdown."
          },
          {
            "type": "p",
            "html": "Edge cases to cover: clock going backwards (refuse or wait until it catches up; alert on NTP steps), sequence exhaustion within one millisecond (spin to the next ms), restarts within the same millisecond (persist or wait out the last timestamp), and running out of worker ids (the bit split is a trade-off: fewer timestamp bits, more worker bits). IDs are k-sorted, not strictly ordered across workers within a millisecond, which is fine for feeds and pagination."
          }
        ]
      },
      {
        "q": "Why can UUIDv4 primary keys make inserts slow, and what do you use instead?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "A B-tree primary key stores rows in key order. Random keys mean every insert goes to a random leaf page: the whole index must stay in memory to avoid disk reads, pages split all over the tree and end up half full, and write amplification grows. Sequential keys append to the rightmost page, which is always hot in cache. Use a time-ordered ID (UUIDv7, ULID, Snowflake) or an auto-increment primary key, keeping a random UUID as a separate public identifier if needed."
          }
        ]
      },
      {
        "q": "Can two UUIDv4s collide? Should your code handle it?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "In principle yes, in practice no: with 122 random bits you would need about 2.7 quintillion IDs for a 50% collision chance, and at a billion per second that takes about 85 years. Real collisions come from bugs: a bad or unseeded random source, a forked process sharing generator state, or copying IDs. A unique constraint on the column is the right safeguard &mdash; a collision then becomes an error you can retry instead of silent data corruption."
          }
        ]
      },
      {
        "q": "Snowflake IDs depend on time. What happens when the clock jumps backwards?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "If the generator used the earlier time, it could produce an ID with a timestamp and sequence it already issued: a duplicate. Implementations track the last timestamp used and, when the clock is behind it, either refuse to generate (fail fast, alert) or wait until the clock passes the last timestamp; small skews can be absorbed by continuing from the last timestamp with the sequence. Operationally, run NTP in slewing mode so it adjusts clock speed rather than stepping, and treat large steps as incidents."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "RFC 9562: Universally Unique IDentifiers (UUIDv7)",
        "url": "https://www.rfc-editor.org/rfc/rfc9562"
      },
      {
        "label": "Twitter: Announcing Snowflake",
        "url": "https://blog.x.com/engineering/en_us/a/2010/announcing-snowflake"
      },
      {
        "label": "Flickr: Ticket servers, distributed unique primary keys on the cheap",
        "url": "https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/"
      },
      {
        "label": "Python docs: uuid",
        "url": "https://docs.python.org/3/library/uuid.html"
      }
    ]
  },
  {
    "id": "queues",
    "title": "Message Queues and Delivery Guarantees",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Queues vs logs, at-most/at-least/exactly-once, idempotent consumers, the outbox pattern, ordering, DLQs and lag.",
    "intro": [
      "A queue between two services turns a synchronous call into an asynchronous hand-off. The producer finishes as soon as the message is stored; the consumer works through messages at its own pace. That absorbs spikes, lets either side be deployed or fail without the other noticing, and lets many consumers share the work.",
      "The price is that delivery becomes a distributed-systems problem. Messages can be lost, delivered twice, or arrive out of order, and which of those you get depends on choices you make. This topic simulates each failure and the standard fix."
    ],
    "sections": [
      {
        "title": "Queues vs logs",
        "body": [
          {
            "type": "p",
            "html": "Two families of systems are both called &ldquo;message queues&rdquo;, and they behave differently."
          },
          {
            "type": "table",
            "head": [
              "",
              "Queue (RabbitMQ, SQS)",
              "Log (Kafka, Kinesis, Pulsar)"
            ],
            "rows": [
              [
                "After consumption",
                "Message is deleted once acknowledged",
                "Message stays for the retention period"
              ],
              [
                "Consumers",
                "Compete: each message goes to one consumer",
                "Each consumer group reads the whole log at its own offset"
              ],
              [
                "Replay",
                "No",
                "Yes: rewind the offset"
              ],
              [
                "Ordering",
                "Mostly FIFO, weakened by redelivery and parallel consumers",
                "Strict within a partition"
              ],
              [
                "Scaling consumers",
                "Add consumers freely",
                "At most one consumer per partition per group"
              ],
              [
                "Best for",
                "Task distribution, jobs, work queues",
                "Event streams, many independent readers, rebuilding state"
              ]
            ]
          },
          {
            "type": "p",
            "html": "Rule of thumb: if the message is a <em>command</em> (&ldquo;resize this image&rdquo;) that one worker should do once, a queue fits. If it is an <em>event</em> (&ldquo;order 17 was placed&rdquo;) that several systems care about &mdash; billing, email, analytics &mdash; a log fits, because each reads it independently and new readers can start from the beginning."
          }
        ]
      },
      {
        "title": "Delivery guarantees",
        "body": [
          {
            "type": "p",
            "html": "Every consumer does two things: process the message and acknowledge it. The order of those two steps, around a crash, decides the guarantee."
          },
          {
            "type": "code",
            "src": "import random\n\ndef run(ack_first, crash_rate=0.2, n=1000, seed=2):\n    rng = random.Random(seed)\n    queue = list(range(n))\n    processed = []\n    while queue:\n        msg = queue[0]\n        crash = rng.random() < crash_rate\n        if ack_first:\n            queue.pop(0)                     # ack, then process\n            if crash:\n                continue                     # crashed before processing: lost\n            processed.append(msg)\n        else:\n            processed.append(msg)            # process, then ack\n            if crash:\n                continue                     # crashed before ack: redelivered\n            queue.pop(0)\n    lost = n - len(set(processed))\n    duplicates = len(processed) - len(set(processed))\n    return lost, duplicates\n\nfor name, ack_first in ((\"ack, then process\", True), (\"process, then ack\", False)):\n    lost, dup = run(ack_first)\n    print(f\"{name:18} lost={lost:3}  duplicates={dup:3}\")",
            "label": null,
            "output": "ack, then process  lost=195  duplicates=  0\nprocess, then ack  lost=  0  duplicates=243",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "Guarantee",
              "How",
              "Consequence"
            ],
            "rows": [
              [
                "At most once",
                "Ack before processing (or fire and forget)",
                "Never duplicated, sometimes lost. Fine for metrics, logs"
              ],
              [
                "At least once",
                "Ack after processing; retry until acked",
                "Never lost, sometimes duplicated. The default for anything that matters"
              ],
              [
                "Exactly once (effectively)",
                "At least once + idempotent or deduplicating consumer",
                "Each message's <em>effect</em> happens once"
              ]
            ]
          },
          {
            "type": "note",
            "text": "True exactly-once <em>delivery</em> over an unreliable network is impossible: the consumer can always crash between doing the work and recording that it did. What systems offer is exactly-once <em>processing</em>: at-least-once delivery plus a consumer whose effects are idempotent."
          }
        ]
      },
      {
        "title": "Idempotent consumers",
        "body": [
          {
            "type": "p",
            "html": "An operation is idempotent if doing it twice has the same effect as once. Some are naturally idempotent (&ldquo;set status to shipped&rdquo;, upserts by key). Others are not (&ldquo;add 10 to the balance&rdquo;, &ldquo;send an email&rdquo;) and need a deduplication record: store the message id in the same transaction as the effect, and skip ids already seen."
          },
          {
            "type": "code",
            "src": "import random\n\ndef deliver_with_duplicates(messages, rng):\n    for m in messages:\n        yield m\n        if rng.random() < 0.3:\n            yield m                          # redelivered after a lost ack\n\nmessages = [{\"id\": f\"m{i}\", \"account\": \"ann\", \"amount\": 10} for i in range(100)]\n\nnaive = 0\nfor m in deliver_with_duplicates(messages, random.Random(5)):\n    naive += m[\"amount\"]\n\nbalance, seen = 0, set()                     # seen ids live in the same DB as balance\nfor m in deliver_with_duplicates(messages, random.Random(5)):\n    if m[\"id\"] in seen:\n        continue\n    balance += m[\"amount\"]                   # in one transaction with...\n    seen.add(m[\"id\"])                        # ...recording the id\n\nprint(\"expected   :\", 100 * 10)\nprint(\"naive      :\", naive)\nprint(\"idempotent :\", balance)",
            "label": null,
            "output": "expected   : 1000\nnaive      : 1340\nidempotent : 1000",
            "isError": false
          },
          {
            "type": "p",
            "html": "The dedup store grows forever unless pruned. Keep ids for longer than the maximum redelivery window (often a few days), or use a per-key sequence number: a consumer that has applied version 7 of account <code>ann</code> ignores anything &le; 7."
          }
        ]
      },
      {
        "title": "The dual-write problem and the outbox pattern",
        "body": [
          {
            "type": "p",
            "html": "A service that writes to its database and then publishes an event has two separate writes. If it crashes between them, the database says the order exists and no other service ever hears about it. Publishing first is no better: the event goes out for an order that was never saved."
          },
          {
            "type": "p",
            "html": "The <strong>transactional outbox</strong> fixes this: write the event into an <code>outbox</code> table in the <em>same</em> database transaction as the business change. A separate relay reads the outbox and publishes to the broker, retrying until it succeeds &mdash; at least once, so consumers stay idempotent."
          },
          {
            "type": "code",
            "src": "import random, sqlite3\n\ndb = sqlite3.connect(\":memory:\")\ndb.executescript(\"\"\"\n    CREATE TABLE orders (id INTEGER PRIMARY KEY, item TEXT);\n    CREATE TABLE outbox (id INTEGER PRIMARY KEY, event TEXT, sent INTEGER DEFAULT 0);\n\"\"\")\nbroker, rng = [], random.Random(4)\n\ndef place_order(item):\n    with db:                                 # one transaction: both or neither\n        cur = db.execute(\"INSERT INTO orders (item) VALUES (?)\", (item,))\n        db.execute(\"INSERT INTO outbox (event) VALUES (?)\", (f\"order_placed:{cur.lastrowid}\",))\n\ndef relay():\n    rows = db.execute(\"SELECT id, event FROM outbox WHERE sent = 0 ORDER BY id\").fetchall()\n    for row_id, event in rows:\n        if rng.random() < 0.3:\n            print(f\"  broker unavailable, will retry {event}\")\n            return\n        broker.append(event)\n        with db:\n            db.execute(\"UPDATE outbox SET sent = 1 WHERE id = ?\", (row_id,))\n\nfor item in (\"book\", \"lamp\", \"desk\", \"mug\"):\n    place_order(item)\nwhile db.execute(\"SELECT COUNT(*) FROM outbox WHERE sent = 0\").fetchone()[0]:\n    relay()\nprint(\"orders:\", db.execute(\"SELECT COUNT(*) FROM orders\").fetchone()[0], \"| events:\", broker)",
            "label": null,
            "output": "  broker unavailable, will retry order_placed:1\n  broker unavailable, will retry order_placed:1\n  broker unavailable, will retry order_placed:2\n  broker unavailable, will retry order_placed:2\norders: 4 | events: ['order_placed:1', 'order_placed:2', 'order_placed:3', 'order_placed:4']",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "Change data capture (Debezium reading the database's write-ahead log) is the industrial version of the relay: it publishes outbox rows, or every row change, without polling."
          }
        ]
      },
      {
        "title": "Ordering and partitions",
        "body": [
          {
            "type": "p",
            "html": "Logs keep order only within a partition, and parallel consumers of a queue can finish messages in any order. When order matters per entity (all events for one order, one account, one chat), route by a key so that entity's messages always land in the same partition and are handled by one consumer in sequence."
          },
          {
            "type": "code",
            "src": "import random, zlib\nfrom collections import defaultdict\n\nevents = [(acct, step) for step in range(1, 6) for acct in (\"ann\", \"bob\", \"cy\", \"dee\")]\nPARTITIONS = 3\n\ndef run(partition_of):\n    parts = defaultdict(list)\n    for i, e in enumerate(events):\n        parts[partition_of(i, e)].append(e)\n    rng = random.Random(2)\n    applied = defaultdict(list)\n    cursors = {p: 0 for p in parts}\n    while any(cursors[p] < len(parts[p]) for p in parts):\n        p = rng.choice([p for p in parts if cursors[p] < len(parts[p])])\n        acct, step = parts[p][cursors[p]]       # partitions progress independently\n        cursors[p] += 1\n        applied[acct].append(step)\n    return {a: s for a, s in applied.items() if s != sorted(s)}\n\nround_robin = lambda i, e: i % PARTITIONS\nby_key = lambda i, e: zlib.crc32(e[0].encode()) % PARTITIONS\n\nprint(\"round robin, out of order:\", run(round_robin))\nprint(\"keyed,       out of order:\", run(by_key))",
            "label": null,
            "output": "round robin, out of order: {'cy': [2, 1, 4, 5, 3], 'bob': [1, 3, 2, 5, 4]}\nkeyed,       out of order: {}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Keyed partitioning has a cost: a hot key (one huge customer) overloads one partition, and the number of partitions caps consumer parallelism. Choose the key as the smallest unit that needs ordering &mdash; order id rather than customer id, if per-order order is enough."
          }
        ]
      },
      {
        "title": "Retries, poison messages and dead-letter queues",
        "body": [
          {
            "type": "p",
            "html": "A message that always fails (bad data, a bug) would be redelivered forever and block everything behind it. Count delivery attempts; after N, move the message to a <strong>dead-letter queue</strong> for a human or a repair job, and carry on. Transient failures (a timeout) deserve a retry with back-off; permanent ones (a validation error) should go straight to the DLQ."
          },
          {
            "type": "code",
            "src": "from collections import deque\n\nclass TransientError(Exception): pass\nclass PermanentError(Exception): pass\n\ndef handle(msg, attempt):\n    if msg == \"corrupt\":\n        raise PermanentError(\"cannot parse\")\n    if msg == \"flaky\" and attempt < 3:\n        raise TransientError(\"timeout\")\n    return f\"done {msg}\"\n\nqueue = deque([(\"a\", 1), (\"corrupt\", 1), (\"flaky\", 1), (\"b\", 1)])\ndlq, MAX_ATTEMPTS = [], 5\nwhile queue:\n    msg, attempt = queue.popleft()\n    try:\n        print(\" \", handle(msg, attempt))\n    except PermanentError as e:\n        dlq.append((msg, str(e)))\n    except TransientError:\n        if attempt >= MAX_ATTEMPTS:\n            dlq.append((msg, \"too many attempts\"))\n        else:\n            queue.append((msg, attempt + 1))   # real systems delay this retry\nprint(\"dead letters:\", dlq)",
            "label": null,
            "output": "  done a\n  done b\n  done flaky\ndead letters: [('corrupt', 'cannot parse')]",
            "isError": false
          }
        ]
      },
      {
        "title": "Backpressure and consumer lag",
        "body": [
          {
            "type": "p",
            "html": "A queue absorbs bursts only while consumers keep up on average. <strong>Consumer lag</strong> &mdash; messages produced but not yet processed &mdash; is the metric to watch. If it grows steadily, add consumers (up to the partition count) or make processing faster; if it only grows during bursts and drains afterwards, the queue is doing its job."
          },
          {
            "type": "code",
            "src": "produce = [50] * 10 + [400] * 5 + [50] * 25        # messages per second\ncapacity = 120                                      # what consumers can process\n\nlag, history = 0, []\nfor rate in produce:\n    lag = max(0, lag + rate - capacity)\n    history.append(lag)\npeak = max(history)\ndrained_at = next(i for i in range(history.index(peak), len(history)) if history[i] == 0)\nprint(\"lag every 5 s:\", history[::5])\nprint(f\"peak lag {peak} messages; drained {drained_at - history.index(peak)} s after the burst ended\")",
            "label": null,
            "output": "lag every 5 s: [0, 0, 280, 1330, 980, 630, 280, 0]\npeak lag 1400 messages; drained 20 s after the burst ended",
            "isError": false
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you get exactly-once processing with Kafka?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "End to end, by combining at-least-once delivery with idempotence on every side effect. Within Kafka, the idempotent producer (sequence numbers per partition) prevents duplicates from producer retries, and transactions let a consume-transform-produce job commit its output messages and its input offsets atomically &mdash; exactly-once for Kafka-to-Kafka pipelines."
          },
          {
            "type": "p",
            "html": "Any effect outside Kafka (a database write, an email, a payment) is not covered. For those, store the consumed offset or message id in the same database transaction as the effect, or make the effect idempotent with a key (Stripe's <code>Idempotency-Key</code>, an upsert). That is where exactly-once is actually won or lost."
          }
        ]
      },
      {
        "q": "A consumer charges a credit card for each <code>order_placed</code> event. How do you make sure no customer is charged twice?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Assume every event can arrive more than once. Use the order id as an idempotency key: in one database transaction, insert a <code>payments(order_id UNIQUE, status)</code> row before calling the payment provider, and skip the event if the row already exists. Pass the same key to the provider's idempotency mechanism, so even a retry after a timeout (when you do not know whether the charge went through) cannot charge twice. Record the result, and reconcile with the provider's records periodically for the rare case where your write and theirs disagree."
          }
        ]
      },
      {
        "q": "When should you not put a queue between two services?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "When the caller needs the answer to continue: a login check, a price for the page being rendered. A queue then adds latency and a request-reply correlation mechanism for no benefit. Also when ordering and consistency are simpler to get with a direct transactional call, or when the volume is tiny and the queue is one more system to run and monitor. Queues fit work that can happen later, needs buffering against spikes, or must reach several consumers."
          }
        ]
      },
      {
        "q": "What is consumer lag and what do you do when it keeps growing?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Lag is the gap between the newest message and the consumer's position: work accepted but not done. Steady growth means consumers are slower than producers on average. Options: add consumers (in Kafka, only up to the number of partitions &mdash; add partitions first if needed), make each message cheaper (batching writes, removing a slow synchronous call), or shed load (drop or sample low-value messages). Also check for a single slow partition caused by a hot key, which more consumers will not fix."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Confluent: Exactly-once semantics in Apache Kafka",
        "url": "https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/"
      },
      {
        "label": "microservices.io: Transactional outbox",
        "url": "https://microservices.io/patterns/data/transactional-outbox.html"
      },
      {
        "label": "AWS: Amazon SQS dead-letter queues",
        "url": "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html"
      },
      {
        "label": "Jay Kreps: The Log",
        "url": "https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying"
      }
    ]
  },
  {
    "id": "resilience",
    "title": "Timeouts, Retries and Circuit Breakers",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Why retries cause outages, backoff with jitter, retry budgets, circuit breakers, bulkheads and load shedding.",
    "intro": [
      "In a system of many services, something is always slow or failing. Resilience patterns decide whether one sick dependency stays a local problem or takes everything down with it. The usual way a small failure becomes a big one is not the failure itself but the reaction to it: callers waiting forever, retrying all at once, and piling more load onto the thing that is already struggling.",
      "Each pattern below is implemented and run against a simulated failing dependency."
    ],
    "sections": [
      {
        "title": "Timeouts: the first defence",
        "body": [
          {
            "type": "p",
            "html": "A call without a timeout can wait forever, and while it waits it holds a thread, a connection and memory. When a dependency hangs, callers without timeouts exhaust their pools and stop serving even requests that do not touch that dependency."
          },
          {
            "type": "code",
            "src": "import random\n\ndef run(timeout, pool=50, seconds=60, rps=20, seed=3):\n    \"\"\"One server, 50 worker threads. The dependency hangs for 30 s at t=10.\"\"\"\n    rng = random.Random(seed)\n    busy = []                                    # finish times of occupied workers\n    served = rejected = 0\n    for t10 in range(seconds * 10):              # 0.1 s steps\n        t = t10 / 10\n        busy = [f for f in busy if f > t]\n        for _ in range(rps // 10):\n            if len(busy) >= pool:\n                rejected += 1                    # no free worker\n                continue\n            hanging = 10 <= t < 40 and rng.random() < 0.5   # half the calls hit the bad dependency\n            duration = 30.0 if hanging else 0.05\n            busy.append(t + min(duration, timeout))\n            served += 1\n    return served, rejected\n\nfor timeout in (float(\"inf\"), 2.0, 0.5):\n    served, rejected = run(timeout)\n    label = \"none\" if timeout == float(\"inf\") else f\"{timeout} s\"\n    print(f\"timeout {label:5}  served={served:4}  rejected={rejected:4}\")",
            "label": null,
            "output": "timeout none   served= 719  rejected= 481\ntimeout 2.0 s  served=1200  rejected=   0\ntimeout 0.5 s  served=1200  rejected=   0",
            "isError": false
          },
          {
            "type": "p",
            "html": "Without a timeout, the hung calls occupied every worker within a few seconds, and for the rest of the outage the server rejected every request &mdash; 40% of the minute's traffic, including the half that never needed the broken dependency. A short timeout freed workers fast enough to keep serving."
          },
          {
            "type": "p",
            "html": "Choose timeouts from measurements: a little above the dependency's p99 latency, not a round number like 30 s. And make them <strong>budgets</strong> that shrink along a call chain: if the user-facing request has 1 s, a call made after 700 ms of work gets at most the remaining 300 ms (gRPC deadlines propagate this automatically)."
          }
        ]
      },
      {
        "title": "Retries: helpful in small doses",
        "body": [
          {
            "type": "p",
            "html": "Retrying a failed call hides transient faults: a dropped packet, a server restarting, a leader election. But retries multiply load. If every layer of a five-deep call chain retries three times, one failing call at the bottom can become 3<sup>5</sup> = 243 attempts."
          },
          {
            "type": "code",
            "src": "def attempts_at_bottom(depth, retries_per_layer):\n    tries = 1 + retries_per_layer\n    return tries ** depth\n\nfor depth in (1, 3, 5):\n    print(f\"depth {depth}: {attempts_at_bottom(depth, 2):4} attempts reach the failing service\")",
            "label": null,
            "output": "depth 1:    3 attempts reach the failing service\ndepth 3:   27 attempts reach the failing service\ndepth 5:  243 attempts reach the failing service",
            "isError": false
          },
          {
            "type": "p",
            "html": "Rules that keep retries safe: retry only <strong>idempotent</strong> operations (or ones carrying an idempotency key); retry only errors that can succeed later (timeouts, 503, connection reset &mdash; not 400 or 404); retry at <em>one</em> layer, usually the one closest to the user; and cap retries with a <strong>budget</strong>, e.g. retries may add at most 10% to the request volume."
          }
        ]
      },
      {
        "title": "Exponential backoff with jitter",
        "body": [
          {
            "type": "p",
            "html": "Retrying immediately hammers a struggling service. Exponential backoff waits longer after each failure (base &times; 2<sup>attempt</sup>, capped). But if a thousand clients failed at the same moment, they also back off in lockstep and retry in synchronised waves. <strong>Jitter</strong> &mdash; randomising each wait &mdash; spreads them out."
          },
          {
            "type": "code",
            "src": "import random\nfrom collections import Counter\n\ndef schedule(strategy, clients=1000, attempts=4, base=1.0, cap=20.0, seed=1):\n    rng = random.Random(seed)\n    hits = Counter()\n    for _ in range(clients):\n        t = 0.0\n        for a in range(attempts):\n            ceiling = min(cap, base * 2 ** a)\n            if strategy == \"none\":\n                wait = base\n            elif strategy == \"exponential\":\n                wait = ceiling\n            else:                                    # \"full jitter\"\n                wait = rng.uniform(0, ceiling)\n            t += wait\n            hits[int(t * 10)] += 1                   # retries per 100 ms slot\n    return max(hits.values()), len(hits)\n\nfor strategy in (\"none\", \"exponential\", \"full jitter\"):\n    peak, spread = schedule(strategy)\n    print(f\"{strategy:12} peak {peak:4} retries in one 100 ms slot, spread over {spread:3} slots\")",
            "label": null,
            "output": "none         peak 1000 retries in one 100 ms slot, spread over   4 slots\nexponential  peak 1000 retries in one 100 ms slot, spread over   4 slots\nfull jitter  peak  155 retries in one 100 ms slot, spread over 137 slots",
            "isError": false
          },
          {
            "type": "code",
            "src": "import random\n\ndef backoff(attempt, base=0.1, cap=10.0, rng=random.Random(0)):\n    \"\"\"AWS 'full jitter': sleep a random time up to the exponential ceiling.\"\"\"\n    return rng.uniform(0, min(cap, base * 2 ** attempt))\n\nprint([round(backoff(a), 2) for a in range(8)])",
            "label": "the backoff function itself",
            "output": "[0.08, 0.15, 0.17, 0.21, 0.82, 1.3, 5.02, 3.03]",
            "isError": false
          }
        ]
      },
      {
        "title": "Circuit breakers",
        "body": [
          {
            "type": "p",
            "html": "When a dependency is clearly down, continuing to call it wastes time on every request and denies it the breathing room to recover. A circuit breaker watches failures and, past a threshold, <em>opens</em>: calls fail immediately without touching the dependency. After a cool-down it goes <em>half-open</em> and lets a trial call through; success closes it, failure opens it again."
          },
          {
            "type": "code",
            "src": "class CircuitBreaker:\n    def __init__(self, threshold=3, cooldown=5.0):\n        self.threshold, self.cooldown = threshold, cooldown\n        self.state, self.failures, self.opened_at = \"closed\", 0, 0.0\n\n    def call(self, fn, now):\n        if self.state == \"open\":\n            if now - self.opened_at < self.cooldown:\n                return \"fast-fail\"                   # do not even try\n            self.state = \"half-open\"                 # allow one trial\n        try:\n            result = fn(now)\n        except Exception:\n            self.failures += 1\n            if self.state == \"half-open\" or self.failures >= self.threshold:\n                self.state, self.opened_at = \"open\", now\n            return \"error\"\n        self.state, self.failures = \"closed\", 0\n        return result\n\ndef dependency(now):                                 # down between t=2 and t=12\n    if 2 <= now < 12:\n        raise ConnectionError(\"down\")\n    return \"ok\"\n\ncb = CircuitBreaker()\nfor t in range(0, 20, 1):\n    before = cb.state\n    outcome = cb.call(dependency, float(t))\n    if outcome != \"ok\" or before != cb.state:\n        print(f\"t={t:2}  {before:9} -> {cb.state:9} {outcome}\")",
            "label": null,
            "output": "t= 2  closed    -> closed    error\nt= 3  closed    -> closed    error\nt= 4  closed    -> open      error\nt= 5  open      -> open      fast-fail\nt= 6  open      -> open      fast-fail\nt= 7  open      -> open      fast-fail\nt= 8  open      -> open      fast-fail\nt= 9  open      -> open      error\nt=10  open      -> open      fast-fail\nt=11  open      -> open      fast-fail\nt=12  open      -> open      fast-fail\nt=13  open      -> open      fast-fail\nt=14  open      -> closed    ok",
            "isError": false
          },
          {
            "type": "p",
            "html": "From t = 5 the breaker stopped calling the dead service entirely and failed in microseconds instead of waiting for a timeout. It probed once per cool-down, and closed again as soon as a probe succeeded. Pair the fast failure with a <strong>fallback</strong>: a cached value, a default, a degraded page without recommendations."
          }
        ]
      },
      {
        "title": "Bulkheads and load shedding",
        "body": [
          {
            "type": "p",
            "html": "<strong>Bulkheads</strong> give each dependency its own limited pool of threads or connections, like watertight compartments in a ship. When one dependency hangs, only its pool fills up; calls to everything else still have capacity."
          },
          {
            "type": "code",
            "src": "def serve(pools, requests):\n    \"\"\"pools: name -> capacity. A hung dependency never releases its slots.\"\"\"\n    used = {name: 0 for name in pools}\n    results = []\n    for dep in requests:\n        pool = dep if dep in pools else \"shared\"\n        if used[pool] >= pools[pool]:\n            results.append(f\"{dep}:REJECT\")\n            continue\n        if dep == \"reviews\":                          # hangs, slot never freed\n            used[pool] += 1\n        results.append(f\"{dep}:ok\")\n    return results\n\ntraffic = [\"reviews\"] * 10 + [\"checkout\", \"search\", \"checkout\"]\nshared = serve({\"shared\": 8}, traffic)\nbulkheads = serve({\"reviews\": 4, \"shared\": 8}, traffic)\nprint(\"one shared pool:\", shared[-3:])\nprint(\"with bulkheads :\", bulkheads[-3:])",
            "label": null,
            "output": "one shared pool: ['checkout:REJECT', 'search:REJECT', 'checkout:REJECT']\nwith bulkheads : ['checkout:ok', 'search:ok', 'checkout:ok']",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Load shedding</strong> is the server-side counterpart: when overloaded, reject work early and cheaply (a fast 503) instead of accepting everything and timing out on all of it. Shed by priority &mdash; drop prefetches and analytics before checkouts &mdash; and use queue age, not just queue length, as the signal: a request that has waited longer than the client will wait is already wasted work."
          },
          {
            "type": "note",
            "text": "Graceful degradation is the product-level version of the same idea: decide in advance which features can disappear under stress (recommendations, live counts, avatars) so the core flow keeps working."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "A downstream service had a 30-second blip, but your service was down for 20 minutes. What probably happened?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "A <em>metastable</em> failure: the trigger was short, but the system's reaction kept it overloaded after the trigger went away. Typical chain: no or long timeouts filled every worker; clients retried immediately (often at several layers), so when the downstream recovered it faced several times its normal load, failed again, and caused more retries. Caches may also have expired during the blip, sending a stampede to the database."
          },
          {
            "type": "p",
            "html": "Fixes: tight timeouts and deadlines, retries at one layer with exponential backoff, jitter and a retry budget, a circuit breaker to stop calling the dependency while it is down, load shedding so an overloaded service rejects cheaply, and request coalescing on cache misses."
          }
        ]
      },
      {
        "q": "Which requests is it safe to retry automatically?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Requests whose repetition cannot cause a different outcome. HTTP <code>GET</code>, <code>PUT</code> and <code>DELETE</code> are defined as idempotent; <code>POST</code> is not, unless it carries an idempotency key the server uses to deduplicate. Retry only on errors that can be transient: timeouts, connection failures, 429 (after <code>Retry-After</code>) and 502/503/504. Do not retry 4xx client errors, and be careful with timeouts on non-idempotent writes: the first attempt may have succeeded, which is exactly the case an idempotency key exists for."
          }
        ]
      },
      {
        "q": "Why add jitter to exponential backoff?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Clients that failed together back off by the same amounts, so they retry together, in synchronised spikes that can knock the recovering service over again. Randomising each delay (&ldquo;full jitter&rdquo;: uniform between 0 and the exponential ceiling) spreads the retries over the whole interval. The total number of retries is the same; the peak load is a fraction of it."
          }
        ]
      },
      {
        "q": "Explain the three states of a circuit breaker and how you would tune it.",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "<strong>Closed</strong>: calls pass through and failures are counted. <strong>Open</strong>: entered when failures cross a threshold; calls fail immediately for a cool-down period. <strong>Half-open</strong>: after the cool-down, a limited number of trial calls go through; success closes the breaker, failure reopens it. Tune the threshold as a failure <em>rate</em> over a sliding window with a minimum request count (so three failures out of four requests at 3 a.m. do not trip it), the cool-down from how long the dependency typically takes to recover, and the half-open probe count small. Scope breakers per dependency, and ideally per endpoint, so one failing route does not cut off healthy ones."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "AWS Architecture Blog: Exponential backoff and jitter",
        "url": "https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/"
      },
      {
        "label": "Google SRE book: Handling overload",
        "url": "https://sre.google/sre-book/handling-overload/"
      },
      {
        "label": "Google SRE book: Addressing cascading failures",
        "url": "https://sre.google/sre-book/addressing-cascading-failures/"
      },
      {
        "label": "Martin Fowler: CircuitBreaker",
        "url": "https://martinfowler.com/bliki/CircuitBreaker.html"
      },
      {
        "label": "Metastable Failures in Distributed Systems (HotOS 2021)",
        "url": "https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf"
      }
    ]
  },
  {
    "id": "url-shortener",
    "title": "Design a URL Shortener",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "A full walkthrough: requirements, estimates, code generation (counter vs hash), storage, caching, redirects and analytics.",
    "intro": [
      "The classic first design question, because it is small enough to finish in 45 minutes and still touches every step: estimation, an API, a key-generation scheme with real trade-offs, a read-heavy data path that wants a cache, and analytics that should not slow redirects down.",
      "This walkthrough follows the framework from the first topic, with the core pieces implemented and measured."
    ],
    "sections": [
      {
        "title": "Requirements and estimates",
        "body": [
          {
            "type": "p",
            "html": "<strong>Functional</strong>: create a short link for a long URL (optionally with a custom alias and an expiry); visiting the short link redirects to the long URL; owners can see click counts. <strong>Non-functional</strong>: redirects must be fast (p99 under ~50 ms) and highly available &mdash; a broken redirect breaks someone else's page; links must not be guessable in sequence; creation can be slower."
          },
          {
            "type": "code",
            "src": "new_links_per_day = 10_000_000\nread_write_ratio = 100\nrecord_bytes = 500\nyears = 5\n\nwrites_qps = new_links_per_day / 86_400\nreads_qps = writes_qps * read_write_ratio\ntotal_links = new_links_per_day * 365 * years\nstorage_tb = total_links * record_bytes / 1e12\n\nprint(f\"writes: {writes_qps:,.0f}/s avg   reads: {reads_qps:,.0f}/s avg, ~{reads_qps * 3:,.0f}/s peak\")\nprint(f\"links after {years} years: {total_links / 1e9:.1f} billion, {storage_tb:.1f} TB before replication\")\n\nfor length in (6, 7, 8):\n    print(f\"base62, {length} chars: {62 ** length:>20,} codes \"\n          f\"({62 ** length / total_links:,.0f}x the links we need)\")",
            "label": null,
            "output": "writes: 116/s avg   reads: 11,574/s avg, ~34,722/s peak\nlinks after 5 years: 18.2 billion, 9.1 TB before replication\nbase62, 6 chars:       56,800,235,584 codes (3x the links we need)\nbase62, 7 chars:    3,521,614,606,208 codes (193x the links we need)\nbase62, 8 chars:  218,340,105,584,896 codes (11,964x the links we need)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Conclusions: storage is modest (a sharded key-value store or even a large Postgres can hold it), reads dominate so the redirect path should be served from cache, and 7 base62 characters leave more than enough room."
          }
        ]
      },
      {
        "title": "API",
        "body": [
          {
            "type": "table",
            "head": [
              "Endpoint",
              "Behaviour"
            ],
            "rows": [
              [
                "<code>POST /v1/links</code> <code>{url, alias?, expires_at?}</code>",
                "<code>201 {code, short_url}</code>; <code>409</code> if the alias is taken; <code>400</code> for an invalid or blocked URL"
              ],
              [
                "<code>GET /{code}</code>",
                "<code>302 Location: &lt;long url&gt;</code>; <code>404</code> unknown; <code>410</code> expired"
              ],
              [
                "<code>GET /v1/links/{code}/stats</code>",
                "Clicks by day, referrer, country (owner only)"
              ],
              [
                "<code>DELETE /v1/links/{code}</code>",
                "Owner disables the link"
              ]
            ]
          },
          {
            "type": "p",
            "html": "<strong>301 or 302?</strong> A <code>301 Moved Permanently</code> is cached by browsers, so repeat visits never reach your servers: cheaper, but you lose click analytics and cannot change or disable the target later. A <code>302 Found</code> (or <code>307</code>) sends every click through you. Most shorteners use 302 for that reason; say which trade-off you are making."
          }
        ]
      },
      {
        "title": "Generating the code: hash or counter",
        "body": [
          {
            "type": "p",
            "html": "Option one: hash the long URL (MD5, SHA-256), base62-encode it and keep the first 7 characters. The same URL always gives the same code, which deduplicates for free &mdash; but truncated hashes collide, and the birthday bound says it happens far sooner than the code space suggests. Every insert must check and handle collisions (rehash with a salt)."
          },
          {
            "type": "code",
            "src": "import hashlib, random, string\n\nALPHABET = string.digits + string.ascii_letters          # base62\n\ndef base62(n):\n    s = \"\"\n    while n:\n        n, r = divmod(n, 62)\n        s = ALPHABET[r] + s\n    return s or \"0\"\n\ndef hash_code(url, length):\n    digest = int.from_bytes(hashlib.sha256(url.encode()).digest(), \"big\")\n    return base62(digest)[:length]\n\nrng = random.Random(1)\nurls = [f\"https://example.com/item/{rng.getrandbits(64):x}\" for _ in range(200_000)]\nfor length in (4, 5, 6):\n    codes = [hash_code(u, length) for u in urls]\n    print(f\"{length} chars: {len(codes) - len(set(codes)):6,} collisions in 200,000 URLs \"\n          f\"(space {62 ** length:,})\")",
            "label": null,
            "output": "4 chars:  1,430 collisions in 200,000 URLs (space 14,776,336)\n5 chars:     25 collisions in 200,000 URLs (space 916,132,832)\n6 chars:      0 collisions in 200,000 URLs (space 56,800,235,584)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Option two: a <strong>unique counter</strong> &mdash; a database sequence, a Snowflake-style generator, or blocks of IDs handed to each app server from a ticket service &mdash; base62-encoded. No collisions by construction and no read-before-write. The catch: consecutive codes are guessable (<code>aB3x</code>, <code>aB3y</code>&hellip;), letting anyone crawl every link. Fix that by passing the counter through a reversible permutation before encoding, so consecutive ids map to scattered codes."
          },
          {
            "type": "code",
            "src": "import string\n\nALPHABET = string.digits + string.ascii_letters\nSPACE = 62 ** 7\nMULT = 2_176_477_521_739                   # ~0.618 * SPACE, coprime with it: invertible\nMULT_INV = pow(MULT, -1, SPACE)\nSALT = 2_718_281_828\n\ndef encode(n, length=7):\n    s = \"\"\n    for _ in range(length):\n        n, r = divmod(n, 62)\n        s = ALPHABET[r] + s\n    return s\n\ndef decode(s):\n    n = 0\n    for ch in s:\n        n = n * 62 + ALPHABET.index(ch)\n    return n\n\ndef obfuscate(counter):\n    return (counter * MULT + SALT) % SPACE   # a bijection on [0, SPACE)\n\ndef reveal(code):\n    return ((decode(code) - SALT) * MULT_INV) % SPACE\n\nfor counter in (1000, 1001, 1002, 1003):\n    code = encode(obfuscate(counter))\n    print(counter, \"->\", code, \"->\", reveal(code))",
            "label": null,
            "output": "1000 -> 29Cq5hW -> 1000\n1001 -> EtldXD1 -> 1001\n1002 -> gN41PY6 -> 1002\n1003 -> T6MPIjb -> 1003",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "A multiplicative permutation hides order from casual browsing but is not cryptographic: anyone with a few code/id pairs can solve for the constants. If enumeration must be impossible, use random codes with a uniqueness check, or a block cipher (such as format-preserving encryption) over the counter."
          }
        ]
      },
      {
        "title": "Storage and the redirect path",
        "body": [
          {
            "type": "p",
            "html": "The data is a key-value lookup by code: <code>code &rarr; (long_url, owner_id, created_at, expires_at)</code>. Any store that does fast point reads works: DynamoDB or Cassandra partitioned by code, or Postgres with the code as primary key, sharded by a hash of the code when it outgrows one node."
          },
          {
            "type": "p",
            "html": "Reads are 100&times; writes and popular links are extremely popular (a link in a viral post gets millions of clicks in an hour), so the redirect path reads through a cache. With link popularity following a power law, a cache holding a small fraction of links serves most traffic:"
          },
          {
            "type": "code",
            "src": "import random\nfrom collections import OrderedDict\n\nclass LRU:\n    def __init__(self, capacity):\n        self.capacity, self.data = capacity, OrderedDict()\n        self.hits = self.misses = 0\n\n    def get(self, key, load):\n        if key in self.data:\n            self.data.move_to_end(key)\n            self.hits += 1\n            return self.data[key]\n        self.misses += 1\n        value = self.data[key] = load(key)\n        if len(self.data) > self.capacity:\n            self.data.popitem(last=False)\n        return value\n\nrng = random.Random(42)\nlinks = 100_000\nweights = [1 / (rank ** 1.1) for rank in range(1, links + 1)]   # Zipf-like popularity\nclicks = rng.choices(range(links), weights=weights, k=300_000)\n\nfor pct in (0.1, 1, 5):\n    cache = LRU(int(links * pct / 100))\n    for code in clicks:\n        cache.get(code, load=lambda c: f\"https://long/{c}\")\n    print(f\"cache {pct:>4}% of links -> hit rate {cache.hits / len(clicks):.0%}\")",
            "label": null,
            "output": "cache  0.1% of links -> hit rate 45%\ncache    1% of links -> hit rate 66%\ncache    5% of links -> hit rate 79%",
            "isError": false
          },
          {
            "type": "p",
            "html": "Layer it: a CDN or edge cache in front (redirects for the hottest links never reach your datacenter), an in-memory cache on each app server, then Redis, then the database. Negative-cache unknown codes briefly too, or a bot scanning random codes will hammer the database."
          }
        ]
      },
      {
        "title": "Click analytics without slowing redirects",
        "body": [
          {
            "type": "p",
            "html": "Writing a row per click to the database on the redirect path would turn a read-mostly system into a write-heavy one and add latency to every redirect. Instead the redirect handler emits a click event (code, timestamp, referrer, country, user agent) to a log such as Kafka and returns immediately. A stream processor aggregates counts per code per minute and writes the aggregates to an analytics store."
          },
          {
            "type": "code",
            "src": "from collections import Counter, defaultdict\n\nevents = [  # (code, minute, country) as emitted by the redirect handlers\n    (\"aZ3kq9P\", 0, \"IN\"), (\"aZ3kq9P\", 0, \"US\"), (\"Bq81xLm\", 0, \"IN\"),\n    (\"aZ3kq9P\", 1, \"IN\"), (\"aZ3kq9P\", 1, \"IN\"), (\"Bq81xLm\", 2, \"DE\"),\n]\n\nper_minute = Counter((code, minute) for code, minute, _ in events)\nby_country = defaultdict(Counter)\nfor code, _, country in events:\n    by_country[code][country] += 1\n\nprint(dict(per_minute))\nprint({code: dict(c) for code, c in by_country.items()})",
            "label": null,
            "output": "{('aZ3kq9P', 0): 2, ('Bq81xLm', 0): 1, ('aZ3kq9P', 1): 2, ('Bq81xLm', 2): 1}\n{'aZ3kq9P': {'IN': 3, 'US': 1}, 'Bq81xLm': {'IN': 1, 'DE': 1}}",
            "isError": false
          },
          {
            "type": "p",
            "html": "Approximate counts are acceptable for analytics, which allows batching, sampling under extreme load, and probabilistic structures (HyperLogLog for unique visitors)."
          }
        ]
      },
      {
        "title": "The whole picture",
        "body": [
          {
            "type": "p",
            "html": "Create: client &rarr; load balancer &rarr; API service (validate URL, check blocklist, rate-limit per user) &rarr; ID block from the ticket service &rarr; write to the database &rarr; return the short URL."
          },
          {
            "type": "p",
            "html": "Redirect: client &rarr; CDN (hit: done) &rarr; load balancer &rarr; redirect service &rarr; local cache &rarr; Redis &rarr; database &rarr; <code>302</code>; asynchronously emit a click event to Kafka &rarr; aggregator &rarr; analytics store."
          },
          {
            "type": "table",
            "head": [
              "Concern",
              "Decision"
            ],
            "rows": [
              [
                "Code generation",
                "Counter blocks + reversible permutation; random codes if enumeration must be impossible"
              ],
              [
                "Custom aliases",
                "Same key space; insert with a uniqueness constraint, <code>409</code> on conflict; reserve words like <code>api</code>, <code>admin</code>"
              ],
              [
                "Expiry",
                "Check <code>expires_at</code> on read; delete lazily plus a background sweep"
              ],
              [
                "Abuse",
                "Check URLs against malware/phishing lists at creation and periodically; rate-limit creation"
              ],
              [
                "Availability",
                "Redirect path is read-only and cacheable: replicas in several regions, serve from cache if the DB is down"
              ]
            ]
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Why not just use the first 7 characters of an MD5 of the URL?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Truncation throws away the property that makes cryptographic hashes safe from collisions. With 62<sup>7</sup> &asymp; 3.5 &times; 10<sup>12</sup> codes, the birthday bound gives a 50% chance of at least one collision after about 2.2 million links, and collisions become routine at billions. So every write must read first and resolve collisions, which costs a round trip and needs care under concurrency. It also makes the same URL from two users map to one code, which breaks per-user analytics and deletion. A counter avoids collisions entirely."
          }
        ]
      },
      {
        "q": "How would you handle 1 million redirects per second for a single viral link?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "One key, so sharding does not help: the load must be absorbed by replication of that key. Serve it from the CDN or edge (cache the 302 for a short TTL), keep it in each app server's in-process cache so most requests never leave the box, and if Redis is involved, replicate hot keys or use client-side caching so no single Redis node takes all reads. Click counting must not touch a single counter row: emit events and aggregate them, or keep per-server counters flushed periodically."
          }
        ]
      },
      {
        "q": "301 or 302 for the redirect?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "301 is permanent: browsers and proxies cache it, so the cheapest option for load, but later clicks bypass you (no analytics, no ability to disable a malicious link or change the target). 302/307 are temporary: every click comes through you. Most shorteners choose 302 and rely on their own caching layers for efficiency; a 301 with a cache-control max-age is a middle ground some services use."
          }
        ]
      },
      {
        "q": "How do you stop people from enumerating all short links?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Do not expose a raw sequential counter. Either generate random codes (with a uniqueness check and retry on conflict; with a large enough space retries are rare), or permute the counter through a keyed bijection before encoding so consecutive ids give unrelated-looking codes. Add rate limits on redirects of unknown codes per IP, and allow private links that require authentication. Longer codes for private links raise the cost of guessing."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Bitly engineering blog",
        "url": "https://word.bitly.com/"
      },
      {
        "label": "MDN: 301 Moved Permanently vs 302 Found",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections"
      },
      {
        "label": "Flickr: Ticket servers",
        "url": "https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/"
      }
    ]
  },
  {
    "id": "news-feed",
    "title": "Design a News Feed",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Fan-out on write vs read, the celebrity problem and the hybrid, timeline caches, k-way merges, ranking and pagination.",
    "intro": [
      "&ldquo;Design Twitter&rsquo;s home timeline&rdquo; (or Instagram&rsquo;s, or LinkedIn&rsquo;s) is the canonical read-heavy fan-out problem. Posting is rare and cheap; reading a feed means gathering recent posts from everyone you follow, which might be thousands of accounts, in well under a second, hundreds of thousands of times per second.",
      "The design turns on one decision &mdash; do the gathering work when a post is written, or when a feed is read &mdash; and on what to do about accounts with millions of followers, where either choice breaks."
    ],
    "sections": [
      {
        "title": "Requirements and the core numbers",
        "body": [
          {
            "type": "p",
            "html": "Functional: post (text, media), follow and unfollow, read a home feed of posts from followed accounts, newest or best first, with infinite scroll. Non-functional: feed reads fast (p99 &lt; 200 ms), posting may take a few seconds to appear for followers (eventual consistency is fine), and the system must survive accounts with tens of millions of followers."
          },
          {
            "type": "code",
            "src": "dau = 300_000_000\nposts_per_user_day = 0.5\nfeed_reads_per_user_day = 20\navg_following = 200\n\npost_qps = dau * posts_per_user_day / 86_400\nread_qps = dau * feed_reads_per_user_day / 86_400\nprint(f\"posts: {post_qps:>9,.0f}/s   feed reads: {read_qps:>9,.0f}/s   ratio 1:{read_qps / post_qps:.0f}\")\nprint(f\"fan-out on write: {post_qps * avg_following:>11,.0f} timeline inserts/s (avg {avg_following} followers)\")\nprint(f\"fan-out on read : {read_qps * avg_following:>11,.0f} author timelines read/s (follows {avg_following})\")",
            "label": null,
            "output": "posts:     1,736/s   feed reads:    69,444/s   ratio 1:40\nfan-out on write:     347,222 timeline inserts/s (avg 200 followers)\nfan-out on read :  13,888,889 author timelines read/s (follows 200)",
            "isError": false
          },
          {
            "type": "p",
            "html": "Pull does 40&times; more work in total here, simply because reads outnumber posts 40 to 1, and it does that work synchronously while the reader waits. Push does its work once per post, in the background. That is why push is the default &mdash; until an account with millions of followers posts."
          }
        ]
      },
      {
        "title": "Fan-out on write (push)",
        "body": [
          {
            "type": "p",
            "html": "When someone posts, a background worker inserts the post id into a precomputed timeline for each follower &mdash; a capped list in Redis, newest first. Reading a feed is then one list read plus hydrating the post objects: very fast."
          },
          {
            "type": "code",
            "src": "from collections import defaultdict, deque\n\nfollowers = {\"ann\": [\"bob\", \"cy\"], \"bob\": [\"cy\"], \"cy\": [\"ann\", \"bob\"]}\nTIMELINE_CAP = 800\ntimelines = defaultdict(lambda: deque(maxlen=TIMELINE_CAP))\nwork = 0\n\ndef post(author, post_id):\n    global work\n    for f in followers[author]:              # done by async workers via a queue\n        timelines[f].appendleft(post_id)\n        work += 1\n\ndef read_feed(user, n=10):\n    return list(timelines[user])[:n]          # one read, already in order\n\nfor i, author in enumerate([\"ann\", \"bob\", \"cy\", \"ann\"], start=1):\n    post(author, f\"{author}:{i}\")\nprint(\"cy's feed :\", read_feed(\"cy\"))\nprint(\"bob's feed:\", read_feed(\"bob\"))\nprint(\"timeline writes done:\", work)",
            "label": null,
            "output": "cy's feed : ['ann:4', 'bob:2', 'ann:1']\nbob's feed: ['ann:4', 'cy:3', 'ann:1']\ntimeline writes done: 7",
            "isError": false
          },
          {
            "type": "p",
            "html": "The cost lands on popular authors: one post by an account with 50 million followers means 50 million list inserts. That takes minutes to drain, delays everyone else's posts queued behind it, and stores the same post id 50 million times. Most of those followers will never scroll far enough to see it."
          }
        ]
      },
      {
        "title": "Fan-out on read (pull)",
        "body": [
          {
            "type": "p",
            "html": "Store only each author's own posts. To build a feed, fetch the recent posts of everyone the reader follows and merge them by time. Writes are trivial and celebrities cost nothing extra, but every feed read does many lookups and a merge &mdash; on the latency-critical path."
          },
          {
            "type": "p",
            "html": "The merge is a classic <strong>k-way merge</strong>: each author's list is already sorted, so a heap of size k produces the newest n posts overall in O(n log k), touching only as many posts as it outputs."
          },
          {
            "type": "code",
            "src": "import heapq\n\nauthor_posts = {   # each list newest first: (timestamp, post id)\n    \"ann\": [(105, \"ann:5\"), (101, \"ann:1\")],\n    \"bob\": [(108, \"bob:8\"), (103, \"bob:3\"), (100, \"bob:0\")],\n    \"nasa\": [(107, \"nasa:7\"), (106, \"nasa:6\"), (102, \"nasa:2\")],\n}\n\ndef read_feed(following, n=5):\n    heap = []\n    for author in following:\n        posts = author_posts.get(author, [])\n        if posts:\n            ts, pid = posts[0]\n            heap.append((-ts, pid, author, 0))   # max-heap via negated time\n    heapq.heapify(heap)\n    feed = []\n    while heap and len(feed) < n:\n        neg_ts, pid, author, i = heapq.heappop(heap)\n        feed.append(pid)\n        if i + 1 < len(author_posts[author]):\n            ts, nxt = author_posts[author][i + 1]\n            heapq.heappush(heap, (-ts, nxt, author, i + 1))\n    return feed\n\nprint(read_feed([\"ann\", \"bob\", \"nasa\"]))",
            "label": null,
            "output": "['bob:8', 'nasa:7', 'nasa:6', 'ann:5', 'bob:3']",
            "isError": false
          }
        ]
      },
      {
        "title": "The hybrid: push for most, pull for celebrities",
        "body": [
          {
            "type": "p",
            "html": "Production systems combine them. Accounts below a follower threshold fan out on write. Accounts above it (celebrities, brands) do not; their posts are pulled at read time and merged into the precomputed timeline. A reader follows only a handful of celebrities, so the read-time merge stays small."
          },
          {
            "type": "code",
            "src": "import heapq, random\nfrom collections import defaultdict\n\nrng = random.Random(7)\nusers = [f\"u{i}\" for i in range(2000)]\ncelebs = [\"star1\", \"star2\"]\nfollows = {u: set(rng.sample(users, 40)) | ({\"star1\"} if rng.random() < 0.9 else set())\n                                            | ({\"star2\"} if rng.random() < 0.7 else set())\n           for u in users}\nfollowers = defaultdict(list)\nfor u, fs in follows.items():\n    for f in fs:\n        followers[f].append(u)\n\nposts = [(t, rng.choice(users + celebs * 50)) for t in range(5000)]   # celebs post a lot\n\ndef simulate(threshold):\n    writes = 0\n    timelines = defaultdict(list)\n    own = defaultdict(list)\n    for t, author in posts:\n        own[author].append(t)\n        if len(followers[author]) < threshold:\n            for f in followers[author]:\n                timelines[f].append(t)\n                writes += 1\n    reads = 0\n    for u in users[:200]:                       # 200 feed loads\n        pulled = [own[a] for a in follows[u] if len(followers[a]) >= threshold]\n        reads += 1 + len(pulled)\n    return writes, reads / 200\n\nfor name, threshold in ((\"push only\", float(\"inf\")), (\"pull only\", 0), (\"hybrid (>=1000)\", 1000)):\n    writes, lookups = simulate(threshold)\n    print(f\"{name:16} timeline writes={writes:>9,}  lookups per feed load={lookups:5.1f}\")",
            "label": null,
            "output": "push only        timeline writes=  545,006  lookups per feed load=  1.0\npull only        timeline writes=        0  lookups per feed load= 42.6\nhybrid (>=1000)  timeline writes=  191,276  lookups per feed load=  2.6",
            "isError": false
          },
          {
            "type": "table",
            "head": [
              "",
              "Fan-out on write",
              "Fan-out on read",
              "Hybrid"
            ],
            "rows": [
              [
                "Feed read latency",
                "Lowest",
                "Highest",
                "Low"
              ],
              [
                "Cost of a celebrity post",
                "Enormous",
                "None",
                "None"
              ],
              [
                "Storage",
                "Post id &times; followers",
                "Posts only",
                "Mostly ids for normal accounts"
              ],
              [
                "Inactive users",
                "Wasted work for them",
                "No work",
                "Skip fan-out to users inactive for N days"
              ],
              [
                "Freshness",
                "Seconds behind (async)",
                "Immediate",
                "Mixed"
              ]
            ]
          },
          {
            "type": "note",
            "text": "Another standard optimisation: do not fan out to users who have not logged in for weeks. Rebuild their timeline with a pull when they come back."
          }
        ]
      },
      {
        "title": "Storage, caching and hydration",
        "body": [
          {
            "type": "p",
            "html": "Separate the pieces by access pattern. <strong>Posts</strong>: a sharded key-value or wide-column store keyed by post id (Cassandra, DynamoDB, sharded MySQL), plus an index of each author's post ids by time. <strong>Social graph</strong>: follower and following lists, sharded by user id. <strong>Timelines</strong>: Redis lists or sorted sets of post ids, capped at a few hundred per user, rebuildable from the source data. <strong>Media</strong>: object storage behind a CDN."
          },
          {
            "type": "p",
            "html": "A feed read returns ids, then <em>hydrates</em> them: fetches the post objects, author names and avatars, like counts, and whether the reader liked each post. Do that with batched multi-get calls (one round trip per store, not one per post) from caches, never N separate queries."
          },
          {
            "type": "code",
            "src": "import time\n\nPOST_CACHE = {f\"p{i}\": {\"id\": f\"p{i}\", \"author\": f\"u{i % 7}\", \"text\": f\"post {i}\"} for i in range(100)}\n\ndef get_one(pid):\n    time.sleep(0.002)                               # one network round trip\n    return POST_CACHE[pid]\n\ndef get_many(pids):\n    time.sleep(0.002)                               # one round trip for the batch\n    return [POST_CACHE[p] for p in pids]\n\nids = [f\"p{i}\" for i in range(50)]\nt = time.perf_counter(); a = [get_one(p) for p in ids]; one_by_one = time.perf_counter() - t\nt = time.perf_counter(); b = get_many(ids); batched = time.perf_counter() - t\nprint(a == b, f\"one by one ~{one_by_one * 1000:.0f} ms vs batched ~{batched * 1000:.0f} ms\")",
            "label": null,
            "output": "True one by one ~125 ms vs batched ~3 ms",
            "isError": false
          }
        ]
      },
      {
        "title": "Ranking and pagination",
        "body": [
          {
            "type": "p",
            "html": "Purely chronological feeds are simple; ranked feeds score candidate posts with features (author affinity, engagement so far, recency, media type) and sort by score. A common structure is a two-stage pipeline: <em>candidate generation</em> (the merged timeline, plus recommended posts) followed by <em>ranking</em> of a few hundred candidates with a model."
          },
          {
            "type": "code",
            "src": "import math\n\ndef score(post, now):\n    age_h = (now - post[\"ts\"]) / 3600\n    engagement = math.log1p(post[\"likes\"] + 3 * post[\"comments\"])\n    affinity = post[\"affinity\"]                      # how often the reader interacts with the author\n    return (1 + engagement) * (0.5 + affinity) / (age_h + 2) ** 1.5\n\nnow = 100_000\ncandidates = [\n    {\"id\": \"fresh, no likes\",       \"ts\": now - 600,    \"likes\": 0,   \"comments\": 0,  \"affinity\": 0.2},\n    {\"id\": \"close friend, 3h\",      \"ts\": now - 10_800, \"likes\": 4,   \"comments\": 2,  \"affinity\": 0.9},\n    {\"id\": \"viral, 6h\",             \"ts\": now - 21_600, \"likes\": 900, \"comments\": 80, \"affinity\": 0.1},\n    {\"id\": \"stranger, 1h, average\", \"ts\": now - 3_600,  \"likes\": 15,  \"comments\": 1,  \"affinity\": 0.0},\n]\nfor p in sorted(candidates, key=lambda p: score(p, now), reverse=True):\n    print(f\"{score(p, now):6.3f}  {p['id']}\")",
            "label": null,
            "output": " 0.425  close friend, 3h\n 0.380  stranger, 1h, average\n 0.219  fresh, no likes\n 0.213  viral, 6h",
            "isError": false
          },
          {
            "type": "p",
            "html": "Ranked feeds still need stable pagination: because scores change between requests, page 2 recomputed from scratch would repeat or skip posts. Snapshot the ranked list of ids for the session (cache it with a short TTL) and paginate through the snapshot with a cursor."
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "Walk through what happens when a user with 200 followers posts, and when a user with 30 million followers posts, in a hybrid design.",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The 200-follower post: the post service writes the post to the posts store and appends to the author's own post index, then enqueues a fan-out job. Fan-out workers read the follower list in pages and push the post id onto each follower's cached timeline (skipping inactive users). Within a few seconds followers see it."
          },
          {
            "type": "p",
            "html": "The 30-million-follower post: the same write to the posts store and author index, but no fan-out. When any follower loads their feed, the feed service reads their precomputed timeline, notices which followed accounts are marked as celebrities, fetches those accounts' recent post ids (heavily cached, since millions of readers ask for the same list), and merges them in with a k-way merge before ranking and hydration."
          }
        ]
      },
      {
        "q": "How do you keep the feed consistent when a user unfollows someone or deletes a post?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Make timelines a cache of ids, not the source of truth, and filter at read time. On delete, mark the post deleted in the posts store; hydration drops ids whose post is gone, so stale ids in timelines are harmless and can be cleaned lazily. On unfollow, filter the reader's timeline against their current following set at read time (or run an async cleanup job), and stop future fan-out immediately because it reads the follower list fresh. Exact real-time removal everywhere is not worth the cost; filtering on read gives the correct user-visible result."
          }
        ]
      },
      {
        "q": "Why cap each precomputed timeline at a few hundred entries?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Memory: 300 million users &times; 800 ids &times; 8 bytes is about 2 TB of Redis just for ids, and it grows linearly with the cap. Almost nobody scrolls past the first few hundred posts. Older history can be served by falling back to fan-out on read for deep pages, which is slow only for the rare user who scrolls that far."
          }
        ]
      },
      {
        "q": "The timeline cache for a region is lost. What happens and how do you recover?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "Timelines are derived data, so nothing is lost permanently, but every feed read becomes a cache miss. Rebuilding every user's timeline with fan-out on read at once would overload the posts and graph stores: a thundering herd. Recover gradually: rebuild timelines lazily on each user's next request (pull, then store), rate-limit rebuilds, coalesce concurrent rebuilds for the same user, and serve a degraded feed (only celebrities and recent posts) while the cache warms. Keeping replicas of the timeline cache in another zone avoids the scenario in the first place."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Twitter: Timelines at scale (InfoQ talk)",
        "url": "https://www.infoq.com/presentations/Twitter-Timeline-Scalability/"
      },
      {
        "label": "Instagram: Feed ranking",
        "url": "https://about.instagram.com/blog/announcements/shedding-more-light-on-how-instagram-works"
      },
      {
        "label": "Facebook: TAO, the power of the graph",
        "url": "https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/"
      }
    ]
  },
  {
    "id": "chat-system",
    "title": "Design a Chat System",
    "group": null,
    "tags": [],
    "level": null,
    "summary": "Persistent connections, routing messages between gateways, per-conversation ordering, delivery and read receipts, presence, offline sync.",
    "intro": [
      "A chat system (WhatsApp, Slack, Messenger) differs from most web services in one way that shapes everything: the server must <em>push</em> to clients, instantly, over connections that stay open for hours. That brings in connection gateways, routing a message to whichever server holds the recipient's connection, and a protocol for ordering, acknowledging and resynchronising messages over flaky mobile networks.",
      "This topic builds the core pieces &mdash; sequence numbers, acknowledgements, sync after reconnect, presence with heartbeats &mdash; and runs them against simulated network failures."
    ],
    "sections": [
      {
        "title": "Requirements and connection scale",
        "body": [
          {
            "type": "p",
            "html": "Functional: one-to-one and group messages (groups up to a few hundred members), delivery and read receipts, online presence, history synced across a user's devices, media attachments. Non-functional: low latency (sub-second delivery when online), no lost messages, correct order within a conversation, works on unreliable mobile networks."
          },
          {
            "type": "code",
            "src": "dau = 500_000_000\nconcurrent_share = 0.2                  # fraction online at peak\nconns_per_gateway = 500_000              # tuned epoll-based server, mostly idle sockets\nmessages_per_user_day = 40\n\nconcurrent = dau * concurrent_share\nprint(f\"open connections at peak : {concurrent:,.0f}\")\nprint(f\"gateway servers          : {concurrent / conns_per_gateway:,.0f} (+ headroom)\")\nprint(f\"messages per second      : {dau * messages_per_user_day / 86_400:,.0f} avg\")\nprint(f\"heartbeats per second    : {concurrent / 30:,.0f} (one every 30 s per connection)\")",
            "label": null,
            "output": "open connections at peak : 100,000,000\ngateway servers          : 200 (+ headroom)\nmessages per second      : 231,481 avg\nheartbeats per second    : 3,333,333 (one every 30 s per connection)",
            "isError": false
          },
          {
            "type": "p",
            "html": "The connection count, not the message rate, sizes the edge tier. Keeping a socket open costs memory (kernel buffers, TLS state, a few KB in the app), and every heartbeat is a small packet to process."
          }
        ]
      },
      {
        "title": "How clients stay connected",
        "body": [
          {
            "type": "table",
            "head": [
              "Technique",
              "How",
              "Trade-off"
            ],
            "rows": [
              [
                "Short polling",
                "Ask &ldquo;anything new?&rdquo; every few seconds",
                "Simple; wasteful and slow"
              ],
              [
                "Long polling",
                "Request hangs until there is a message or a timeout, then reconnect",
                "Works everywhere; one request per message burst"
              ],
              [
                "Server-Sent Events",
                "One long HTTP response streaming events",
                "Server-to-client only"
              ],
              [
                "WebSocket",
                "Upgraded HTTP connection, full duplex frames",
                "The standard for chat; needs stateful gateways"
              ],
              [
                "Mobile push (APNs/FCM)",
                "OS-level notification when the app is in the background",
                "Wakes the app; not a data channel"
              ]
            ]
          },
          {
            "type": "p",
            "html": "The architecture splits into a <strong>stateful</strong> gateway tier that holds WebSocket connections and does little else, and <strong>stateless</strong> services behind it (message service, presence, groups) that can be scaled and deployed freely. Deploying a gateway drops its connections, so clients must reconnect transparently and resync &mdash; which the protocol below handles anyway."
          }
        ]
      },
      {
        "title": "Routing a message to the right gateway",
        "body": [
          {
            "type": "p",
            "html": "Alice's connection is on gateway 3 and Bob's on gateway 17. When Alice sends, the message service must find Bob's gateway. A <strong>session registry</strong> (Redis: <code>user &rarr; {device: gateway}</code>) records where each device is connected; the message service looks it up and forwards the message to that gateway, which writes it to Bob's socket. If Bob is offline, the message waits in storage and a push notification is sent."
          },
          {
            "type": "code",
            "src": "class Gateway:\n    def __init__(self, name):\n        self.name, self.sockets = name, {}\n    def deliver(self, device, msg):\n        self.sockets[device].append(msg)\n        return True\n\nclass ChatService:\n    def __init__(self, gateways):\n        self.gateways = {g.name: g for g in gateways}\n        self.registry = {}                    # (user, device) -> gateway name\n        self.store, self.push_notifications = [], []\n\n    def connect(self, user, device, gateway):\n        self.registry[(user, device)] = gateway\n        self.gateways[gateway].sockets[device] = []\n\n    def disconnect(self, user, device):\n        self.registry.pop((user, device), None)\n\n    def send(self, sender, recipient, text):\n        msg = {\"from\": sender, \"to\": recipient, \"text\": text}\n        self.store.append(msg)                # persist first: never lose it\n        devices = [d for (u, d) in self.registry if u == recipient]\n        for d in devices:\n            self.gateways[self.registry[(recipient, d)]].deliver(d, msg)\n        if not devices:\n            self.push_notifications.append(f\"push to {recipient}: {text}\")\n        return len(devices)\n\ng = [Gateway(\"gw3\"), Gateway(\"gw17\")]\nchat = ChatService(g)\nchat.connect(\"bob\", \"bob-phone\", \"gw17\")\nchat.connect(\"bob\", \"bob-laptop\", \"gw3\")\nprint(\"delivered to\", chat.send(\"alice\", \"bob\", \"lunch?\"), \"devices\")\nchat.disconnect(\"bob\", \"bob-phone\"); chat.disconnect(\"bob\", \"bob-laptop\")\nprint(\"delivered to\", chat.send(\"alice\", \"bob\", \"you there?\"), \"devices\")\nprint(chat.push_notifications, \"| stored:\", len(chat.store))",
            "label": null,
            "output": "delivered to 2 devices\ndelivered to 0 devices\n['push to bob: you there?'] | stored: 2",
            "isError": false
          },
          {
            "type": "p",
            "html": "Alternatives to a per-message registry lookup: a pub/sub channel per user that gateways subscribe to when a device connects (Redis pub/sub, NATS), or consistent hashing of users onto gateways so the gateway is computable. Registry lookups are simple and handle multiple devices naturally."
          }
        ]
      },
      {
        "title": "Ordering: sequence numbers per conversation",
        "body": [
          {
            "type": "p",
            "html": "Timestamps from different devices cannot order messages: clocks disagree, and two messages can arrive in the opposite order of sending. The server assigns each message a <strong>sequence number per conversation</strong> when it stores it. That number is the order everyone displays, and it doubles as a cursor for syncing."
          },
          {
            "type": "code",
            "src": "import random\n\nclass Conversation:\n    def __init__(self):\n        self.next_seq, self.messages = 1, []\n\n    def append(self, sender, text):            # serialised per conversation\n        msg = (self.next_seq, sender, text)\n        self.next_seq += 1\n        self.messages.append(msg)\n        return msg\n\nclass Client:\n    def __init__(self):\n        self.view = {}\n    def receive(self, msg):\n        self.view[msg[0]] = msg               # keyed by seq: duplicates are harmless\n    def render(self):\n        return [f\"{s}:{who}:{t}\" for s, who, t in sorted(self.view.values())]\n\nconv, bob = Conversation(), Client()\nsent = [conv.append(\"ann\", \"hi\"), conv.append(\"cy\", \"hey\"), conv.append(\"ann\", \"plans?\"),\n        conv.append(\"cy\", \"dinner\")]\nnetwork = sent + [sent[1]]                    # one duplicate redelivery\nrandom.Random(4).shuffle(network)              # arrival order is scrambled\nfor m in network:\n    bob.receive(m)\nprint(\"arrival order:\", [m[0] for m in network])\nprint(\"rendered     :\", bob.render())",
            "label": null,
            "output": "arrival order: [4, 2, 1, 3, 2]\nrendered     : ['1:ann:hi', '2:cy:hey', '3:ann:plans?', '4:cy:dinner']",
            "isError": false
          },
          {
            "type": "p",
            "html": "Sequencing must be serialised per conversation: route all writes for a conversation to one partition (Kafka partition key, or a database row with an atomic counter), which also bounds the throughput of a single conversation &mdash; fine for chats, a real limit for a channel with a million members."
          }
        ]
      },
      {
        "title": "Delivery guarantees: acks, retries and resync",
        "body": [
          {
            "type": "p",
            "html": "Messages must not be lost when a connection drops mid-send. The protocol has acknowledgements on both legs. The sender's client keeps a message in an outbox, with a client-generated id, until the server acks it, retrying with the same id after a reconnect so the server can deduplicate. The server keeps the message stored and tracks, per device, the highest sequence number the device has acknowledged."
          },
          {
            "type": "p",
            "html": "On reconnect, a device sends &ldquo;my last seq in conversation X is N&rdquo; and the server replies with everything after N. That single mechanism handles dropped connections, offline periods and new devices alike."
          },
          {
            "type": "code",
            "src": "import random\n\nclass Server:\n    def __init__(self):\n        self.log, self.seen_client_ids = [], {}\n    def submit(self, client_id, text):\n        if client_id in self.seen_client_ids:          # retry of something we have\n            return self.seen_client_ids[client_id]\n        seq = len(self.log) + 1\n        self.log.append((seq, text))\n        self.seen_client_ids[client_id] = seq\n        return seq\n    def sync(self, after):\n        return [m for m in self.log if m[0] > after]\n\nclass Device:\n    def __init__(self):\n        self.last_seq, self.inbox = 0, []\n    def deliver(self, msgs):\n        for seq, text in msgs:\n            if seq == self.last_seq + 1:              # contiguous only: a gap waits for sync\n                self.inbox.append(text)\n                self.last_seq = seq\n\nrng = random.Random(9)\nserver, reader = Server(), Device()\noutbox = [(f\"c{i}\", f\"msg {i}\") for i in range(1, 9)]\n\nwhile outbox:                                         # sender with a flaky link\n    cid, text = outbox[0]\n    seq = server.submit(cid, text)\n    if rng.random() < 0.3:\n        continue                                      # ack lost: resend same id\n    outbox.pop(0)\n    if rng.random() < 0.6:                            # live push sometimes fails\n        reader.deliver([(seq, text)])\n\nreader.deliver(server.sync(after=reader.last_seq))    # reconnect: catch up\nprint(\"server log :\", len(server.log), \"messages (no duplicates from retries)\")\nprint(\"reader got :\", reader.inbox == [t for _, t in server.log], reader.inbox[:4], \"...\")",
            "label": null,
            "output": "server log : 8 messages (no duplicates from retries)\nreader got : True ['msg 1', 'msg 2', 'msg 3', 'msg 4'] ...",
            "isError": false
          },
          {
            "type": "caveat",
            "text": "The device advances <code>last_seq</code> only over contiguous messages. If it jumped ahead when a live push arrived after a gap, the next sync would start after the gap and the missing message would never arrive. Real clients buffer out-of-order pushes and request the gap rather than dropping them."
          }
        ]
      },
      {
        "title": "Receipts, presence and groups",
        "body": [
          {
            "type": "p",
            "html": "<strong>Receipts</strong>: a device acks <em>delivered</em> when the message reaches it and <em>read</em> when it is displayed; the server forwards these to the sender as tiny messages on the same path. For groups, store read positions as one &ldquo;last read seq&rdquo; per member rather than per message."
          },
          {
            "type": "p",
            "html": "<strong>Presence</strong>: each connected device heartbeats every ~30 s; a user is online if any device heartbeat is recent. Store last-seen timestamps in Redis with a TTL, and push presence changes only to users who are looking (an open chat with that contact) &mdash; broadcasting every change to every contact multiplies traffic enormously."
          },
          {
            "type": "code",
            "src": "class Presence:\n    def __init__(self, timeout=60):\n        self.timeout, self.last_beat = timeout, {}\n    def heartbeat(self, user, device, now):\n        self.last_beat[(user, device)] = now\n    def status(self, user, now):\n        beats = [t for (u, _), t in self.last_beat.items() if u == user]\n        if beats and now - max(beats) < self.timeout:\n            return \"online\"\n        return f\"last seen {now - max(beats)}s ago\" if beats else \"never seen\"\n\np = Presence()\np.heartbeat(\"ann\", \"phone\", now=0)\np.heartbeat(\"ann\", \"laptop\", now=50)\nfor t in (30, 100, 200):\n    print(f\"t={t:3}: ann is {p.status('ann', t)}\")",
            "label": null,
            "output": "t= 30: ann is online\nt=100: ann is online\nt=200: ann is last seen 150s ago",
            "isError": false
          },
          {
            "type": "p",
            "html": "<strong>Groups</strong>: a message to a group is stored once with the conversation's next seq and fanned out to each member's devices. For small groups, fan out on write; for very large channels, members pull by seq when they open the channel, like the celebrity case in the news feed topic."
          },
          {
            "type": "table",
            "head": [
              "Data",
              "Store",
              "Key / partition"
            ],
            "rows": [
              [
                "Messages",
                "Cassandra / HBase / ScyllaDB (write-heavy, time-ordered)",
                "conversation id, clustered by seq"
              ],
              [
                "Conversations, members",
                "Relational or KV",
                "conversation id; user &rarr; conversations index"
              ],
              [
                "Session registry, presence",
                "Redis with TTLs",
                "user id"
              ],
              [
                "Per-device sync state",
                "KV",
                "(device, conversation) &rarr; last acked seq"
              ],
              [
                "Media",
                "Object storage + CDN",
                "content hash; message holds a URL"
              ]
            ]
          }
        ]
      }
    ],
    "questions": [
      {
        "q": "How do you guarantee messages in a conversation are shown in the same order on every device?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Do not rely on client timestamps. The server assigns a monotonically increasing sequence number per conversation when it persists each message, by routing all writes for a conversation through one partition or an atomic counter. Every device sorts by that number, deduplicates by it, and uses the highest contiguous one as its sync cursor. Messages the user typed but the server has not yet acked are shown at the end, marked pending, and placed by their sequence number once acked."
          }
        ]
      },
      {
        "q": "A user's phone was offline for two days. What happens when it reconnects?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "The client opens a WebSocket to some gateway (any one; the registry is updated), authenticates, and sends its sync state: per conversation, the last sequence number it has. The server returns the list of conversations with newer messages and pages through each one from that seq, newest conversations first so the UI is useful quickly. Messages are acked as they are stored, delivery receipts flow back to senders, and the outbox of messages the user wrote offline is replayed with its client ids so nothing is duplicated."
          }
        ]
      },
      {
        "q": "Why separate the WebSocket gateways from the chat logic?",
        "level": "medium",
        "answer": [
          {
            "type": "p",
            "html": "Gateways are stateful (they hold live connections), and every restart forces their clients to reconnect, so you want them simple, rarely deployed and scaled purely by connection count. Chat logic &mdash; validation, storage, fan-out, receipts &mdash; changes often and scales with message volume; keeping it in stateless services means deploying it never drops a connection. The two talk over an internal RPC or pub/sub path, and the session registry tells the logic tier which gateway holds a given device."
          }
        ]
      },
      {
        "q": "How would end-to-end encryption change this design?",
        "level": "hard",
        "answer": [
          {
            "type": "p",
            "html": "The server can no longer read message content, so anything that needs content moves to clients: search, link previews, spam detection on content. Each device has a key pair; the server stores public keys and relays encrypted payloads it cannot decrypt. One-to-one chats use a key agreement and ratchet (the Signal protocol); groups encrypt the message once with a group key distributed per member device. Multi-device sync gets harder because each device needs its own encrypted copy, and history for a new device must come from another device rather than the server. Ordering, acks and routing are unchanged, since they only use metadata."
          }
        ]
      }
    ],
    "refs": [
      {
        "label": "Slack: Real-time messaging architecture",
        "url": "https://slack.engineering/real-time-messaging/"
      },
      {
        "label": "Discord: How Discord stores trillions of messages",
        "url": "https://discord.com/blog/how-discord-stores-trillions-of-messages"
      },
      {
        "label": "WhatsApp: 1 million connections per server (Erlang)",
        "url": "https://blog.whatsapp.com/1-million-is-so-2011"
      },
      {
        "label": "Signal protocol documentation",
        "url": "https://signal.org/docs/"
      }
    ]
  }
];
