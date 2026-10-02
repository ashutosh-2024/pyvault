from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="url-shortener",
    title="Design a URL Shortener",
    summary="A full walkthrough: requirements, estimates, code generation (counter vs hash), storage, caching, redirects and analytics.",
    intro=[
        "The classic first design question, because it is small enough to finish in 45 minutes and still touches every step: estimation, an API, a key-generation scheme with real trade-offs, a read-heavy data path that wants a cache, and analytics that should not slow redirects down.",
        "This walkthrough follows the framework from the first topic, with the core pieces implemented and measured.",
    ],
    sections=[
        section(
            "Requirements and estimates",
            "<strong>Functional</strong>: create a short link for a long URL (optionally with a custom alias and an expiry); visiting the short link redirects to the long URL; owners can see click counts. <strong>Non-functional</strong>: redirects must be fast (p99 under ~50 ms) and highly available &mdash; a broken redirect breaks someone else's page; links must not be guessable in sequence; creation can be slower.",
            code('''
                new_links_per_day = 10_000_000
                read_write_ratio = 100
                record_bytes = 500
                years = 5

                writes_qps = new_links_per_day / 86_400
                reads_qps = writes_qps * read_write_ratio
                total_links = new_links_per_day * 365 * years
                storage_tb = total_links * record_bytes / 1e12

                print(f"writes: {writes_qps:,.0f}/s avg   reads: {reads_qps:,.0f}/s avg, ~{reads_qps * 3:,.0f}/s peak")
                print(f"links after {years} years: {total_links / 1e9:.1f} billion, {storage_tb:.1f} TB before replication")

                for length in (6, 7, 8):
                    print(f"base62, {length} chars: {62 ** length:>20,} codes "
                          f"({62 ** length / total_links:,.0f}x the links we need)")
            '''),
            "Conclusions: storage is modest (a sharded key-value store or even a large Postgres can hold it), reads dominate so the redirect path should be served from cache, and 7 base62 characters leave more than enough room.",
        ),
        section(
            "API",
            table(
                ["Endpoint", "Behaviour"],
                [
                    ["<code>POST /v1/links</code> <code>{url, alias?, expires_at?}</code>", "<code>201 {code, short_url}</code>; <code>409</code> if the alias is taken; <code>400</code> for an invalid or blocked URL"],
                    ["<code>GET /{code}</code>", "<code>302 Location: &lt;long url&gt;</code>; <code>404</code> unknown; <code>410</code> expired"],
                    ["<code>GET /v1/links/{code}/stats</code>", "Clicks by day, referrer, country (owner only)"],
                    ["<code>DELETE /v1/links/{code}</code>", "Owner disables the link"],
                ],
            ),
            "<strong>301 or 302?</strong> A <code>301 Moved Permanently</code> is cached by browsers, so repeat visits never reach your servers: cheaper, but you lose click analytics and cannot change or disable the target later. A <code>302 Found</code> (or <code>307</code>) sends every click through you. Most shorteners use 302 for that reason; say which trade-off you are making.",
        ),
        section(
            "Generating the code: hash or counter",
            "Option one: hash the long URL (MD5, SHA-256), base62-encode it and keep the first 7 characters. The same URL always gives the same code, which deduplicates for free &mdash; but truncated hashes collide, and the birthday bound says it happens far sooner than the code space suggests. Every insert must check and handle collisions (rehash with a salt).",
            code('''
                import hashlib, random, string

                ALPHABET = string.digits + string.ascii_letters          # base62

                def base62(n):
                    s = ""
                    while n:
                        n, r = divmod(n, 62)
                        s = ALPHABET[r] + s
                    return s or "0"

                def hash_code(url, length):
                    digest = int.from_bytes(hashlib.sha256(url.encode()).digest(), "big")
                    return base62(digest)[:length]

                rng = random.Random(1)
                urls = [f"https://example.com/item/{rng.getrandbits(64):x}" for _ in range(200_000)]
                for length in (4, 5, 6):
                    codes = [hash_code(u, length) for u in urls]
                    print(f"{length} chars: {len(codes) - len(set(codes)):6,} collisions in 200,000 URLs "
                          f"(space {62 ** length:,})")
            '''),
            "Option two: a <strong>unique counter</strong> &mdash; a database sequence, a Snowflake-style generator, or blocks of IDs handed to each app server from a ticket service &mdash; base62-encoded. No collisions by construction and no read-before-write. The catch: consecutive codes are guessable (<code>aB3x</code>, <code>aB3y</code>&hellip;), letting anyone crawl every link. Fix that by passing the counter through a reversible permutation before encoding, so consecutive ids map to scattered codes.",
            code('''
                import string

                ALPHABET = string.digits + string.ascii_letters
                SPACE = 62 ** 7
                MULT = 2_176_477_521_739                   # ~0.618 * SPACE, coprime with it: invertible
                MULT_INV = pow(MULT, -1, SPACE)
                SALT = 2_718_281_828

                def encode(n, length=7):
                    s = ""
                    for _ in range(length):
                        n, r = divmod(n, 62)
                        s = ALPHABET[r] + s
                    return s

                def decode(s):
                    n = 0
                    for ch in s:
                        n = n * 62 + ALPHABET.index(ch)
                    return n

                def obfuscate(counter):
                    return (counter * MULT + SALT) % SPACE   # a bijection on [0, SPACE)

                def reveal(code):
                    return ((decode(code) - SALT) * MULT_INV) % SPACE

                for counter in (1000, 1001, 1002, 1003):
                    code = encode(obfuscate(counter))
                    print(counter, "->", code, "->", reveal(code))
            '''),
            caveat("A multiplicative permutation hides order from casual browsing but is not cryptographic: anyone with a few code/id pairs can solve for the constants. If enumeration must be impossible, use random codes with a uniqueness check, or a block cipher (such as format-preserving encryption) over the counter."),
        ),
        section(
            "Storage and the redirect path",
            "The data is a key-value lookup by code: <code>code &rarr; (long_url, owner_id, created_at, expires_at)</code>. Any store that does fast point reads works: DynamoDB or Cassandra partitioned by code, or Postgres with the code as primary key, sharded by a hash of the code when it outgrows one node.",
            "Reads are 100&times; writes and popular links are extremely popular (a link in a viral post gets millions of clicks in an hour), so the redirect path reads through a cache. With link popularity following a power law, a cache holding a small fraction of links serves most traffic:",
            code('''
                import random
                from collections import OrderedDict

                class LRU:
                    def __init__(self, capacity):
                        self.capacity, self.data = capacity, OrderedDict()
                        self.hits = self.misses = 0

                    def get(self, key, load):
                        if key in self.data:
                            self.data.move_to_end(key)
                            self.hits += 1
                            return self.data[key]
                        self.misses += 1
                        value = self.data[key] = load(key)
                        if len(self.data) > self.capacity:
                            self.data.popitem(last=False)
                        return value

                rng = random.Random(42)
                links = 100_000
                weights = [1 / (rank ** 1.1) for rank in range(1, links + 1)]   # Zipf-like popularity
                clicks = rng.choices(range(links), weights=weights, k=300_000)

                for pct in (0.1, 1, 5):
                    cache = LRU(int(links * pct / 100))
                    for code in clicks:
                        cache.get(code, load=lambda c: f"https://long/{c}")
                    print(f"cache {pct:>4}% of links -> hit rate {cache.hits / len(clicks):.0%}")
            '''),
            "Layer it: a CDN or edge cache in front (redirects for the hottest links never reach your datacenter), an in-memory cache on each app server, then Redis, then the database. Negative-cache unknown codes briefly too, or a bot scanning random codes will hammer the database.",
        ),
        section(
            "Click analytics without slowing redirects",
            "Writing a row per click to the database on the redirect path would turn a read-mostly system into a write-heavy one and add latency to every redirect. Instead the redirect handler emits a click event (code, timestamp, referrer, country, user agent) to a log such as Kafka and returns immediately. A stream processor aggregates counts per code per minute and writes the aggregates to an analytics store.",
            code('''
                from collections import Counter, defaultdict

                events = [  # (code, minute, country) as emitted by the redirect handlers
                    ("aZ3kq9P", 0, "IN"), ("aZ3kq9P", 0, "US"), ("Bq81xLm", 0, "IN"),
                    ("aZ3kq9P", 1, "IN"), ("aZ3kq9P", 1, "IN"), ("Bq81xLm", 2, "DE"),
                ]

                per_minute = Counter((code, minute) for code, minute, _ in events)
                by_country = defaultdict(Counter)
                for code, _, country in events:
                    by_country[code][country] += 1

                print(dict(per_minute))
                print({code: dict(c) for code, c in by_country.items()})
            '''),
            "Approximate counts are acceptable for analytics, which allows batching, sampling under extreme load, and probabilistic structures (HyperLogLog for unique visitors).",
        ),
        section(
            "The whole picture",
            "Create: client &rarr; load balancer &rarr; API service (validate URL, check blocklist, rate-limit per user) &rarr; ID block from the ticket service &rarr; write to the database &rarr; return the short URL.",
            "Redirect: client &rarr; CDN (hit: done) &rarr; load balancer &rarr; redirect service &rarr; local cache &rarr; Redis &rarr; database &rarr; <code>302</code>; asynchronously emit a click event to Kafka &rarr; aggregator &rarr; analytics store.",
            table(
                ["Concern", "Decision"],
                [
                    ["Code generation", "Counter blocks + reversible permutation; random codes if enumeration must be impossible"],
                    ["Custom aliases", "Same key space; insert with a uniqueness constraint, <code>409</code> on conflict; reserve words like <code>api</code>, <code>admin</code>"],
                    ["Expiry", "Check <code>expires_at</code> on read; delete lazily plus a background sweep"],
                    ["Abuse", "Check URLs against malware/phishing lists at creation and periodically; rate-limit creation"],
                    ["Availability", "Redirect path is read-only and cacheable: replicas in several regions, serve from cache if the DB is down"],
                ],
            ),
        ),
    ],
    questions=[
        question(
            "Why not just use the first 7 characters of an MD5 of the URL?",
            "medium",
            "Truncation throws away the property that makes cryptographic hashes safe from collisions. With 62<sup>7</sup> &asymp; 3.5 &times; 10<sup>12</sup> codes, the birthday bound gives a 50% chance of at least one collision after about 2.2 million links, and collisions become routine at billions. So every write must read first and resolve collisions, which costs a round trip and needs care under concurrency. It also makes the same URL from two users map to one code, which breaks per-user analytics and deletion. A counter avoids collisions entirely.",
        ),
        question(
            "How would you handle 1 million redirects per second for a single viral link?",
            "hard",
            "One key, so sharding does not help: the load must be absorbed by replication of that key. Serve it from the CDN or edge (cache the 302 for a short TTL), keep it in each app server's in-process cache so most requests never leave the box, and if Redis is involved, replicate hot keys or use client-side caching so no single Redis node takes all reads. Click counting must not touch a single counter row: emit events and aggregate them, or keep per-server counters flushed periodically.",
        ),
        question(
            "301 or 302 for the redirect?",
            "medium",
            "301 is permanent: browsers and proxies cache it, so the cheapest option for load, but later clicks bypass you (no analytics, no ability to disable a malicious link or change the target). 302/307 are temporary: every click comes through you. Most shorteners choose 302 and rely on their own caching layers for efficiency; a 301 with a cache-control max-age is a middle ground some services use.",
        ),
        question(
            "How do you stop people from enumerating all short links?",
            "medium",
            "Do not expose a raw sequential counter. Either generate random codes (with a uniqueness check and retry on conflict; with a large enough space retries are rare), or permute the counter through a keyed bijection before encoding so consecutive ids give unrelated-looking codes. Add rate limits on redirects of unknown codes per IP, and allow private links that require authentication. Longer codes for private links raise the cost of guessing.",
        ),
    ],
    refs=[
        ("Bitly engineering blog", "https://word.bitly.com/"),
        ("MDN: 301 Moved Permanently vs 302 Found", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections"),
        ("Flickr: Ticket servers", "https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap/"),
    ],
)
