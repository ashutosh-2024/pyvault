from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="framework",
    title="The Interview Framework and Estimation",
    summary="How to run a 45-minute design interview, the numbers to know, and back-of-envelope capacity estimates.",
    intro=[
        "A system design interview is not a quiz with one right answer. It is a 45-minute conversation where the interviewer watches how you turn a vague prompt (&ldquo;design Twitter&rdquo;) into a concrete system, which trade-offs you notice, and whether your numbers hold together. Candidates fail far more often from a missing structure than from missing knowledge.",
        "This topic gives the structure, then the estimation skills that make every later design concrete: how many requests per second, how much storage, how many machines, how much downtime a given availability allows. Every number below is computed by the code next to it.",
        "Caching, sharding, consistent hashing and replication are covered in depth in the <strong>Databases</strong> section; the topics here build on them rather than repeat them.",
    ],
    sections=[
        section(
            "A repeatable structure",
            "Spend the first minutes on scope, not boxes. A design for 1,000 users and one for 500 million are different systems, and the interviewer wants to see you ask.",
            table(
                ["Step", "Time", "What you produce"],
                [
                    ["1. Requirements", "~5 min", "Functional (what users do), non-functional (latency, availability, consistency), explicit <em>out of scope</em>"],
                    ["2. Estimation", "~5 min", "Users, QPS (average and peak), read/write ratio, storage per year, bandwidth"],
                    ["3. API", "~5 min", "The handful of endpoints or RPCs, with parameters and responses"],
                    ["4. Data model", "~5 min", "Entities, keys, access patterns, which store fits each"],
                    ["5. High-level design", "~10 min", "Clients, load balancer, services, stores, caches, queues &mdash; one request traced end to end"],
                    ["6. Deep dives", "~10 min", "The hardest 1&ndash;2 parts: scaling the hot path, consistency, failure handling"],
                    ["7. Wrap-up", "~5 min", "Bottlenecks, what you would monitor, what you would do with 10&times; traffic"],
                ],
            ),
            "Two habits matter more than any single technology. <strong>State trade-offs out loud</strong>: &ldquo;fan-out on write makes reads fast but celebrity posts expensive, so&hellip;&rdquo;. And <strong>let numbers drive decisions</strong>: you add a cache because reads are 100&times; writes and the database cannot take 50k QPS, not because caches are good.",
            note("If you are unsure what the interviewer wants to dig into, ask: &ldquo;I can go deeper on the feed generation or on storage &mdash; which is more interesting to you?&rdquo;"),
        ),
        section(
            "Numbers to know",
            "You do not need exact figures, only orders of magnitude. The point of the table is the ratios: memory is ~1,000&times; faster than an SSD read, which is ~100&times; faster than a cross-continent round trip.",
            table(
                ["Operation", "Rough time", "Takeaway"],
                [
                    ["L1 cache reference", "1 ns", ""],
                    ["Main memory reference", "100 ns", "100&times; L1"],
                    ["Compress 1 KB (fast codec)", "2 &micro;s", "CPU is cheap"],
                    ["Read 1 MB sequentially from memory", "3 &micro;s", ""],
                    ["Random SSD read (4 KB)", "16&ndash;100 &micro;s", "~1,000&times; memory"],
                    ["Read 1 MB sequentially from SSD", "50&ndash;200 &micro;s", ""],
                    ["Round trip in the same datacenter", "0.5 ms", "Network hops add up"],
                    ["Disk (HDD) seek", "5&ndash;10 ms", "Avoid random HDD I/O"],
                    ["Round trip US &harr; Europe", "~80&ndash;150 ms", "Put data near users"],
                ],
            ),
            "And the conversions you use constantly:",
            code('''
                SECONDS_PER_DAY = 24 * 60 * 60
                print(f"seconds per day   : {SECONDS_PER_DAY:,}  (~10^5, use 100k for mental math)")
                print(f"seconds per month : {SECONDS_PER_DAY * 30:,}")
                print(f"seconds per year  : {SECONDS_PER_DAY * 365:,} (~3 * 10^7)")

                for name, power in (("KB", 1), ("MB", 2), ("GB", 3), ("TB", 4), ("PB", 5)):
                    print(f"1 {name} = 10^{3 * power:<2} bytes (2^{10 * power} = {2 ** (10 * power):,})")
            '''),
        ),
        section(
            "Traffic: from users to QPS",
            "Start from daily active users and actions per user, get an average rate, then multiply by a peak factor (2&ndash;10&times;; traffic is never flat). Reads and writes usually differ by orders of magnitude, and that ratio decides most of the architecture.",
            code('''
                def qps(daily_users, actions_per_user, peak_factor=3):
                    avg = daily_users * actions_per_user / 86_400
                    return round(avg), round(avg * peak_factor)

                dau = 200_000_000
                write_avg, write_peak = qps(dau, actions_per_user=2)       # posts per user per day
                read_avg, read_peak = qps(dau, actions_per_user=100)       # timeline reads

                print(f"writes: {write_avg:>9,} avg  {write_peak:>9,} peak QPS")
                print(f"reads : {read_avg:>9,} avg  {read_peak:>9,} peak QPS")
                print(f"read:write ratio = {read_avg // write_avg}:1")
            '''),
            "Little's law turns a rate into a concurrency figure, which is what sizes thread pools, connection pools and server counts: <strong>in-flight requests = arrival rate &times; time each one takes</strong>.",
            code('''
                peak_qps = 700_000
                latency_s = 0.050                      # 50 ms per request
                in_flight = peak_qps * latency_s
                per_server = 500                       # concurrent requests one box handles well

                servers = -(-int(in_flight) // per_server)        # ceiling division
                print(f"in flight at peak : {in_flight:,.0f} requests")
                print(f"servers needed    : {servers}  (+ headroom for a lost zone: {servers * 3 // 2})")
            '''),
        ),
        section(
            "Storage and bandwidth",
            "Multiply objects per day by bytes per object, then by retention and replication. Separate small metadata (database rows) from large blobs (images, video), because they go to completely different stores.",
            code('''
                def human(n):
                    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
                        if n < 1000:
                            return f"{n:,.1f} {unit}"
                        n /= 1000
                    return f"{n:,.1f} EB"

                posts_per_day = 400_000_000
                text_bytes = 300                       # id, author, text, timestamps
                photo_share, photo_bytes = 0.2, 500_000

                meta_day = posts_per_day * text_bytes
                media_day = posts_per_day * photo_share * photo_bytes
                years, replicas = 5, 3

                print("metadata / day :", human(meta_day))
                print("media / day    :", human(media_day))
                print(f"5 years x{replicas}     :", human((meta_day + media_day) * 365 * years * replicas))
                print("media egress   :", human(media_day * 50 / 86_400) + "/s if each photo is viewed 50x")
            '''),
            "Conclusions you can draw out loud: metadata fits in a sharded database (hundreds of TB over five years), media belongs in object storage behind a CDN, and egress bandwidth &mdash; not storage &mdash; is the dominant cost.",
        ),
        section(
            "Availability: what the nines allow",
            "Availability targets translate directly into allowed downtime. Every extra nine is ten times less, and it is much more expensive to achieve: redundancy across zones, automated failover, careful deploys.",
            code('''
                minutes_per_year = 365 * 24 * 60
                for nines in ("99", "99.9", "99.95", "99.99", "99.999"):
                    down = minutes_per_year * (1 - float(nines) / 100)
                    per_month = down / 12
                    print(f"{nines + '%':8} {down:9.1f} min/year  {per_month:7.1f} min/month")
            '''),
            "Dependencies multiply. A request that must pass through five services, each 99.9% available, is at best 99.5% available. Redundancy multiplies the other way: two independent replicas at 99% each are both down only 0.01% of the time.",
            code('''
                from math import prod

                chain = [0.999] * 5
                print(f"5 services in series : {prod(chain):.4%}")

                one = 0.99
                print(f"2 replicas, either OK : {1 - (1 - one) ** 2:.4%}")
                print(f"3 replicas, either OK : {1 - (1 - one) ** 3:.4%}")
            '''),
            caveat("The redundancy formula assumes failures are independent. Replicas in the same rack, the same region or running the same bad deploy fail together, which is why real systems spread replicas across zones and roll out changes gradually."),
        ),
    ],
    questions=[
        question(
            "Estimate the storage needed for a URL shortener over 10 years.",
            "medium",
            "State assumptions, then compute. 100 million new links per month; each record holds the short code (7 B), the long URL (~100 B on average, up to 2 KB), creation time, owner id and some metadata &mdash; call it 500 B with indexes.",
            code('''
                links_per_month = 100_000_000
                record_bytes = 500
                months = 12 * 10
                total = links_per_month * months * record_bytes
                print(f"{links_per_month * months / 1e9:.0f} billion links, {total / 1e12:.0f} TB raw, "
                      f"{total * 3 / 1e12:.0f} TB with 3x replication")
                print(f"write QPS ~ {links_per_month / (30 * 86_400):.0f}, read QPS at 100:1 ~ "
                      f"{100 * links_per_month / (30 * 86_400):,.0f}")
            '''),
            "Then interpret: under 20 TB even replicated is small for a sharded key-value store, 12 billion keys means a 7-character base62 code (62<sup>7</sup> &asymp; 3.5 trillion) has plenty of room, and the read rate says to cache popular links.",
        ),
        question(
            "Why multiply by a peak factor, and how do you choose it?",
            "medium",
            "Systems are sized for the busiest minute, not the average one. Traffic follows daily cycles (evening peaks 2&ndash;3&times; the average), weekly cycles, and events (a match, a product launch, a push notification sent to everyone) that can briefly reach 10&times; or more. Choose the factor from the product: a consumer social app might use 3&ndash;5&times;, a ticketing site expecting on-sale moments 50&times;. Say which you picked and why; and design the spike handling (queues, autoscaling, load shedding) rather than provisioning for it permanently.",
        ),
        question(
            "Your service calls four downstream services, each with 99.9% availability and a long latency tail. What availability can you promise, and what happens to your p99?",
            "hard",
            "Availability at best <code>0.999<sup>4</sup> &asymp; 99.6%</code>, assuming independent failures and no retries. Latency is worse than it looks: the p99 of a sum of four calls is above any one call's p99, and a fan-out that waits for all of several <em>parallel</em> calls is dominated by the slowest one.",
            code('''
                import random
                random.seed(7)

                def call():                              # mostly fast, occasionally slow
                    return random.expovariate(1 / 30) if random.random() < 0.98 else random.uniform(100, 400)

                def p99(samples):
                    return sorted(samples)[int(len(samples) * 0.99)]

                N = 200_000
                single = [call() for _ in range(N)]
                sequential = [sum(call() for _ in range(4)) for _ in range(N // 4)]
                parallel = [max(call() for _ in range(4)) for _ in range(N // 4)]

                print(f"one call   p99 = {p99(single):5.0f} ms")
                print(f"4 in a row p99 = {p99(sequential):5.0f} ms")
                print(f"4 parallel p99 = {p99(parallel):5.0f} ms   (wait for all four)")
                print(f"availability   = {0.999 ** 4:.2%}")
            '''),
            "Mitigations to mention: parallelise independent calls, set timeouts and serve partial results, hedge requests (send a second copy after the p95 time and use whichever returns first), and cache what you can.",
        ),
        question(
            "What questions do you ask in the first five minutes of &ldquo;design a chat app&rdquo;?",
            "medium",
            "Scope: one-to-one only, or groups too, and how large can a group get? Features: online presence, read receipts, typing indicators, media, search, end-to-end encryption? Scale: daily users, messages per user per day, peak concurrent connections? Guarantees: must messages arrive in order, exactly once, and how long is history kept? Platforms: mobile with intermittent connectivity, web, multiple devices per user that must stay in sync? Each answer removes or adds a whole component (a fan-out service for large groups, an encryption key service, a search index), which is exactly why you ask before drawing.",
        ),
    ],
    refs=[
        ("Jeff Dean: Numbers everyone should know (via High Scalability)", "https://highscalability.com/numbers-everyone-should-know/"),
        ("Google SRE book: Embracing risk (availability)", "https://sre.google/sre-book/embracing-risk/"),
        ("The Tail at Scale (Dean and Barroso)", "https://research.google/pubs/the-tail-at-scale/"),
    ],
)
