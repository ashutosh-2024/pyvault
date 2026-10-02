from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="news-feed",
    title="Design a News Feed",
    summary="Fan-out on write vs read, the celebrity problem and the hybrid, timeline caches, k-way merges, ranking and pagination.",
    intro=[
        "&ldquo;Design Twitter&rsquo;s home timeline&rdquo; (or Instagram&rsquo;s, or LinkedIn&rsquo;s) is the canonical read-heavy fan-out problem. Posting is rare and cheap; reading a feed means gathering recent posts from everyone you follow, which might be thousands of accounts, in well under a second, hundreds of thousands of times per second.",
        "The design turns on one decision &mdash; do the gathering work when a post is written, or when a feed is read &mdash; and on what to do about accounts with millions of followers, where either choice breaks.",
    ],
    sections=[
        section(
            "Requirements and the core numbers",
            "Functional: post (text, media), follow and unfollow, read a home feed of posts from followed accounts, newest or best first, with infinite scroll. Non-functional: feed reads fast (p99 &lt; 200 ms), posting may take a few seconds to appear for followers (eventual consistency is fine), and the system must survive accounts with tens of millions of followers.",
            code('''
                dau = 300_000_000
                posts_per_user_day = 0.5
                feed_reads_per_user_day = 20
                avg_following = 200

                post_qps = dau * posts_per_user_day / 86_400
                read_qps = dau * feed_reads_per_user_day / 86_400
                print(f"posts: {post_qps:>9,.0f}/s   feed reads: {read_qps:>9,.0f}/s   ratio 1:{read_qps / post_qps:.0f}")
                print(f"fan-out on write: {post_qps * avg_following:>11,.0f} timeline inserts/s (avg {avg_following} followers)")
                print(f"fan-out on read : {read_qps * avg_following:>11,.0f} author timelines read/s (follows {avg_following})")
            '''),
            "Pull does 40&times; more work in total here, simply because reads outnumber posts 40 to 1, and it does that work synchronously while the reader waits. Push does its work once per post, in the background. That is why push is the default &mdash; until an account with millions of followers posts.",
        ),
        section(
            "Fan-out on write (push)",
            "When someone posts, a background worker inserts the post id into a precomputed timeline for each follower &mdash; a capped list in Redis, newest first. Reading a feed is then one list read plus hydrating the post objects: very fast.",
            code('''
                from collections import defaultdict, deque

                followers = {"ann": ["bob", "cy"], "bob": ["cy"], "cy": ["ann", "bob"]}
                TIMELINE_CAP = 800
                timelines = defaultdict(lambda: deque(maxlen=TIMELINE_CAP))
                work = 0

                def post(author, post_id):
                    global work
                    for f in followers[author]:              # done by async workers via a queue
                        timelines[f].appendleft(post_id)
                        work += 1

                def read_feed(user, n=10):
                    return list(timelines[user])[:n]          # one read, already in order

                for i, author in enumerate(["ann", "bob", "cy", "ann"], start=1):
                    post(author, f"{author}:{i}")
                print("cy's feed :", read_feed("cy"))
                print("bob's feed:", read_feed("bob"))
                print("timeline writes done:", work)
            '''),
            "The cost lands on popular authors: one post by an account with 50 million followers means 50 million list inserts. That takes minutes to drain, delays everyone else's posts queued behind it, and stores the same post id 50 million times. Most of those followers will never scroll far enough to see it.",
        ),
        section(
            "Fan-out on read (pull)",
            "Store only each author's own posts. To build a feed, fetch the recent posts of everyone the reader follows and merge them by time. Writes are trivial and celebrities cost nothing extra, but every feed read does many lookups and a merge &mdash; on the latency-critical path.",
            "The merge is a classic <strong>k-way merge</strong>: each author's list is already sorted, so a heap of size k produces the newest n posts overall in O(n log k), touching only as many posts as it outputs.",
            code('''
                import heapq

                author_posts = {   # each list newest first: (timestamp, post id)
                    "ann": [(105, "ann:5"), (101, "ann:1")],
                    "bob": [(108, "bob:8"), (103, "bob:3"), (100, "bob:0")],
                    "nasa": [(107, "nasa:7"), (106, "nasa:6"), (102, "nasa:2")],
                }

                def read_feed(following, n=5):
                    heap = []
                    for author in following:
                        posts = author_posts.get(author, [])
                        if posts:
                            ts, pid = posts[0]
                            heap.append((-ts, pid, author, 0))   # max-heap via negated time
                    heapq.heapify(heap)
                    feed = []
                    while heap and len(feed) < n:
                        neg_ts, pid, author, i = heapq.heappop(heap)
                        feed.append(pid)
                        if i + 1 < len(author_posts[author]):
                            ts, nxt = author_posts[author][i + 1]
                            heapq.heappush(heap, (-ts, nxt, author, i + 1))
                    return feed

                print(read_feed(["ann", "bob", "nasa"]))
            '''),
        ),
        section(
            "The hybrid: push for most, pull for celebrities",
            "Production systems combine them. Accounts below a follower threshold fan out on write. Accounts above it (celebrities, brands) do not; their posts are pulled at read time and merged into the precomputed timeline. A reader follows only a handful of celebrities, so the read-time merge stays small.",
            code('''
                import heapq, random
                from collections import defaultdict

                rng = random.Random(7)
                users = [f"u{i}" for i in range(2000)]
                celebs = ["star1", "star2"]
                follows = {u: set(rng.sample(users, 40)) | ({"star1"} if rng.random() < 0.9 else set())
                                                            | ({"star2"} if rng.random() < 0.7 else set())
                           for u in users}
                followers = defaultdict(list)
                for u, fs in follows.items():
                    for f in fs:
                        followers[f].append(u)

                posts = [(t, rng.choice(users + celebs * 50)) for t in range(5000)]   # celebs post a lot

                def simulate(threshold):
                    writes = 0
                    timelines = defaultdict(list)
                    own = defaultdict(list)
                    for t, author in posts:
                        own[author].append(t)
                        if len(followers[author]) < threshold:
                            for f in followers[author]:
                                timelines[f].append(t)
                                writes += 1
                    reads = 0
                    for u in users[:200]:                       # 200 feed loads
                        pulled = [own[a] for a in follows[u] if len(followers[a]) >= threshold]
                        reads += 1 + len(pulled)
                    return writes, reads / 200

                for name, threshold in (("push only", float("inf")), ("pull only", 0), ("hybrid (>=1000)", 1000)):
                    writes, lookups = simulate(threshold)
                    print(f"{name:16} timeline writes={writes:>9,}  lookups per feed load={lookups:5.1f}")
            '''),
            table(
                ["", "Fan-out on write", "Fan-out on read", "Hybrid"],
                [
                    ["Feed read latency", "Lowest", "Highest", "Low"],
                    ["Cost of a celebrity post", "Enormous", "None", "None"],
                    ["Storage", "Post id &times; followers", "Posts only", "Mostly ids for normal accounts"],
                    ["Inactive users", "Wasted work for them", "No work", "Skip fan-out to users inactive for N days"],
                    ["Freshness", "Seconds behind (async)", "Immediate", "Mixed"],
                ],
            ),
            note("Another standard optimisation: do not fan out to users who have not logged in for weeks. Rebuild their timeline with a pull when they come back."),
        ),
        section(
            "Storage, caching and hydration",
            "Separate the pieces by access pattern. <strong>Posts</strong>: a sharded key-value or wide-column store keyed by post id (Cassandra, DynamoDB, sharded MySQL), plus an index of each author's post ids by time. <strong>Social graph</strong>: follower and following lists, sharded by user id. <strong>Timelines</strong>: Redis lists or sorted sets of post ids, capped at a few hundred per user, rebuildable from the source data. <strong>Media</strong>: object storage behind a CDN.",
            "A feed read returns ids, then <em>hydrates</em> them: fetches the post objects, author names and avatars, like counts, and whether the reader liked each post. Do that with batched multi-get calls (one round trip per store, not one per post) from caches, never N separate queries.",
            code('''
                import time

                POST_CACHE = {f"p{i}": {"id": f"p{i}", "author": f"u{i % 7}", "text": f"post {i}"} for i in range(100)}

                def get_one(pid):
                    time.sleep(0.002)                               # one network round trip
                    return POST_CACHE[pid]

                def get_many(pids):
                    time.sleep(0.002)                               # one round trip for the batch
                    return [POST_CACHE[p] for p in pids]

                ids = [f"p{i}" for i in range(50)]
                t = time.perf_counter(); a = [get_one(p) for p in ids]; one_by_one = time.perf_counter() - t
                t = time.perf_counter(); b = get_many(ids); batched = time.perf_counter() - t
                print(a == b, f"one by one ~{one_by_one * 1000:.0f} ms vs batched ~{batched * 1000:.0f} ms")
            '''),
        ),
        section(
            "Ranking and pagination",
            "Purely chronological feeds are simple; ranked feeds score candidate posts with features (author affinity, engagement so far, recency, media type) and sort by score. A common structure is a two-stage pipeline: <em>candidate generation</em> (the merged timeline, plus recommended posts) followed by <em>ranking</em> of a few hundred candidates with a model.",
            code('''
                import math

                def score(post, now):
                    age_h = (now - post["ts"]) / 3600
                    engagement = math.log1p(post["likes"] + 3 * post["comments"])
                    affinity = post["affinity"]                      # how often the reader interacts with the author
                    return (1 + engagement) * (0.5 + affinity) / (age_h + 2) ** 1.5

                now = 100_000
                candidates = [
                    {"id": "fresh, no likes",       "ts": now - 600,    "likes": 0,   "comments": 0,  "affinity": 0.2},
                    {"id": "close friend, 3h",      "ts": now - 10_800, "likes": 4,   "comments": 2,  "affinity": 0.9},
                    {"id": "viral, 6h",             "ts": now - 21_600, "likes": 900, "comments": 80, "affinity": 0.1},
                    {"id": "stranger, 1h, average", "ts": now - 3_600,  "likes": 15,  "comments": 1,  "affinity": 0.0},
                ]
                for p in sorted(candidates, key=lambda p: score(p, now), reverse=True):
                    print(f"{score(p, now):6.3f}  {p['id']}")
            '''),
            "Ranked feeds still need stable pagination: because scores change between requests, page 2 recomputed from scratch would repeat or skip posts. Snapshot the ranked list of ids for the session (cache it with a short TTL) and paginate through the snapshot with a cursor.",
        ),
    ],
    questions=[
        question(
            "Walk through what happens when a user with 200 followers posts, and when a user with 30 million followers posts, in a hybrid design.",
            "hard",
            "The 200-follower post: the post service writes the post to the posts store and appends to the author's own post index, then enqueues a fan-out job. Fan-out workers read the follower list in pages and push the post id onto each follower's cached timeline (skipping inactive users). Within a few seconds followers see it.",
            "The 30-million-follower post: the same write to the posts store and author index, but no fan-out. When any follower loads their feed, the feed service reads their precomputed timeline, notices which followed accounts are marked as celebrities, fetches those accounts' recent post ids (heavily cached, since millions of readers ask for the same list), and merges them in with a k-way merge before ranking and hydration.",
        ),
        question(
            "How do you keep the feed consistent when a user unfollows someone or deletes a post?",
            "medium",
            "Make timelines a cache of ids, not the source of truth, and filter at read time. On delete, mark the post deleted in the posts store; hydration drops ids whose post is gone, so stale ids in timelines are harmless and can be cleaned lazily. On unfollow, filter the reader's timeline against their current following set at read time (or run an async cleanup job), and stop future fan-out immediately because it reads the follower list fresh. Exact real-time removal everywhere is not worth the cost; filtering on read gives the correct user-visible result.",
        ),
        question(
            "Why cap each precomputed timeline at a few hundred entries?",
            "medium",
            "Memory: 300 million users &times; 800 ids &times; 8 bytes is about 2 TB of Redis just for ids, and it grows linearly with the cap. Almost nobody scrolls past the first few hundred posts. Older history can be served by falling back to fan-out on read for deep pages, which is slow only for the rare user who scrolls that far.",
        ),
        question(
            "The timeline cache for a region is lost. What happens and how do you recover?",
            "hard",
            "Timelines are derived data, so nothing is lost permanently, but every feed read becomes a cache miss. Rebuilding every user's timeline with fan-out on read at once would overload the posts and graph stores: a thundering herd. Recover gradually: rebuild timelines lazily on each user's next request (pull, then store), rate-limit rebuilds, coalesce concurrent rebuilds for the same user, and serve a degraded feed (only celebrities and recent posts) while the cache warms. Keeping replicas of the timeline cache in another zone avoids the scenario in the first place.",
        ),
    ],
    refs=[
        ("Twitter: Timelines at scale (InfoQ talk)", "https://www.infoq.com/presentations/Twitter-Timeline-Scalability/"),
        ("Instagram: Feed ranking", "https://about.instagram.com/blog/announcements/shedding-more-light-on-how-instagram-works"),
        ("Facebook: TAO, the power of the graph", "https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/"),
    ],
)
