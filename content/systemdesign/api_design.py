from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="api-design",
    title="API Design: Pagination, Idempotency, Versioning",
    summary="REST vs gRPC vs GraphQL, offset vs cursor pagination, idempotency keys, ETags and optimistic concurrency, versioning.",
    intro=[
        "The API is the part of a design that is hardest to change later, because other people's code depends on it. Interviewers use the API step to see whether you think about clients: how they page through results, what happens when they retry, how two of them editing the same thing are kept from overwriting each other, and how the API evolves without breaking them.",
        "Each of those has a standard answer, and each is demonstrated below against a small in-memory service.",
    ],
    sections=[
        section(
            "Choosing a style",
            "Most designs use more than one: a public REST or GraphQL API at the edge, gRPC between internal services, and webhooks or a stream for pushing events out.",
            table(
                ["", "REST / JSON over HTTP", "gRPC (Protobuf over HTTP/2)", "GraphQL"],
                [
                    ["Shape", "Resources and verbs", "Typed procedures", "One endpoint, client-specified queries"],
                    ["Contract", "OpenAPI (optional)", "<code>.proto</code> files, generated clients", "Schema, introspection"],
                    ["Payload", "Text, human-readable", "Binary, compact, fast", "JSON, exactly the fields asked for"],
                    ["Streaming", "SSE / WebSockets bolted on", "Built in, both directions", "Subscriptions"],
                    ["HTTP caching", "Natural (GET, ETag, CDN)", "None", "Hard: everything is POST to one URL"],
                    ["Best for", "Public APIs, browsers, simple CRUD", "Internal service-to-service calls", "Many client types needing different shapes"],
                ],
            ),
            "For a design interview, sketch REST endpoints with nouns for resources and HTTP verbs for actions (<code>POST /v1/orders</code>, <code>GET /v1/orders/{id}</code>, <code>GET /v1/users/{id}/orders?cursor=...</code>), and say what each returns and which status codes matter.",
        ),
        section(
            "Offset pagination and why it breaks",
            "<code>?offset=40&amp;limit=20</code> is easy to build: <code>ORDER BY created DESC LIMIT 20 OFFSET 40</code>. It has two problems. The database still reads and discards all skipped rows, so deep pages get slower. And if rows are inserted or deleted while a client is paging, items shift between pages: the client sees duplicates or silently misses rows.",
            code('''
                def page_offset(items, offset, limit=3):
                    return items[offset:offset + limit]

                def read_two_pages(change):
                    feed = [f"post{i}" for i in range(10, 0, -1)]   # newest first: post10 ... post1
                    seen = page_offset(feed, 0)
                    change(feed)                                    # happens between the requests
                    return seen + page_offset(feed, 3)

                inserted = read_two_pages(lambda f: f.insert(0, "post11"))
                deleted = read_two_pages(lambda f: f.remove("post9"))
                print("new post arrives:", inserted)                # post8 shown twice
                print("old post deleted:", deleted)                 # post7 never shown
            '''),
        ),
        section(
            "Cursor (keyset) pagination",
            "A cursor encodes <em>where the last page ended</em> &mdash; the sort key of its last item &mdash; and the next query asks for items strictly after it: <code>WHERE (created, id) &lt; (:c, :id) ORDER BY created DESC, id DESC LIMIT 20</code>. With an index on the sort key every page costs the same, however deep, and inserts at the front cannot shift later pages.",
            code('''
                import base64, json

                posts = [{"id": i, "ts": 1000 + i // 2} for i in range(1, 11)]   # ties in ts on purpose

                def encode(item):
                    return base64.urlsafe_b64encode(json.dumps([item["ts"], item["id"]]).encode()).decode()

                def page_cursor(cursor=None, limit=3):
                    rows = sorted(posts, key=lambda p: (p["ts"], p["id"]), reverse=True)
                    if cursor:
                        ts, pid = json.loads(base64.urlsafe_b64decode(cursor))
                        rows = [p for p in rows if (p["ts"], p["id"]) < (ts, pid)]   # strictly after
                    page = rows[:limit]
                    return [p["id"] for p in page], (encode(page[-1]) if len(page) == limit else None)

                seen, cursor, first = [], None, True
                while first or cursor:
                    ids, cursor = page_cursor(cursor)
                    seen += ids
                    if first:
                        posts += [{"id": 11, "ts": 1006}, {"id": 12, "ts": 1006}]  # arrive mid-paging
                        first = False
                print("pages:", seen)
                print("no duplicates:", len(seen) == len(set(seen)), "| all old posts seen:", set(range(1, 11)) <= set(seen))
            '''),
            "Two details make it correct: the sort key must be <strong>unique</strong>, so ties are broken by appending the id (two posts in the same second would otherwise be skipped or repeated), and the cursor should be <strong>opaque</strong> (encoded) so clients do not depend on its contents and you can change it later. The trade-off: no jumping to page 37, only next and previous.",
            note("Use offsets only for small, stable, admin-style lists. For feeds, timelines, search results and exports, use cursors."),
        ),
        section(
            "Idempotency keys",
            "Networks fail after the server has done the work but before the client hears back. The client cannot tell &ldquo;not done&rdquo; from &ldquo;done, response lost&rdquo;, so it retries &mdash; and a naive <code>POST /payments</code> charges twice. An <strong>idempotency key</strong> is a client-generated unique id sent with the request; the server stores the response under that key and returns the stored response for any retry.",
            code('''
                import uuid

                class PaymentsAPI:
                    def __init__(self):
                        self.charges, self.responses = [], {}

                    def create_charge(self, amount, idempotency_key=None):
                        if idempotency_key in self.responses:
                            return self.responses[idempotency_key]          # replay, no new charge
                        self.charges.append(amount)
                        response = {"status": 201, "charge_id": len(self.charges), "amount": amount}
                        if idempotency_key:
                            self.responses[idempotency_key] = response      # same transaction as the charge
                        return response

                def client(api, use_key):
                    key = str(uuid.uuid4()) if use_key else None
                    for attempt in range(3):                                # first two responses "time out"
                        response = api.create_charge(50, idempotency_key=key)
                        if attempt == 2:
                            return response

                for use_key in (False, True):
                    api = PaymentsAPI()
                    r = client(api, use_key)
                    print(f"idempotency key={use_key!s:5}  charges made={len(api.charges)}  final response={r}")
            '''),
            "In production the stored response and the business write go in one transaction; keys expire after a day or so; a retry that arrives while the first request is still running gets a <code>409</code> rather than running in parallel; and a retry with the same key but a different body is rejected, because it is a client bug.",
        ),
        section(
            "Conditional requests and optimistic concurrency",
            "Two clients read a document, both edit it, both save: the second save silently erases the first &mdash; a <em>lost update</em>. HTTP's answer is a version tag. <code>GET</code> returns an <code>ETag</code>; the client sends it back as <code>If-Match</code> on <code>PUT</code>; the server applies the write only if the resource has not changed since, and otherwise returns <code>412 Precondition Failed</code> so the client can re-read and merge.",
            code('''
                import hashlib, json

                class DocStore:
                    def __init__(self, doc):
                        self.doc = doc

                    def etag(self):
                        return hashlib.sha1(json.dumps(self.doc, sort_keys=True).encode()).hexdigest()[:8]

                    def get(self):
                        return dict(self.doc), self.etag()

                    def put(self, new_doc, if_match=None):
                        if if_match is not None and if_match != self.etag():
                            return 412
                        self.doc = new_doc
                        return 200

                for use_etag in (False, True):
                    store = DocStore({"title": "Plan", "owner": "ann"})
                    a_doc, a_tag = store.get()
                    b_doc, b_tag = store.get()
                    a_doc["title"] = "Plan v2"
                    b_doc["owner"] = "bob"
                    ra = store.put(a_doc, a_tag if use_etag else None)
                    rb = store.put(b_doc, b_tag if use_etag else None)
                    print(f"ETag={use_etag!s:5} A:{ra} B:{rb} final={store.doc}")
            '''),
            "The same version check in a database is <code>UPDATE ... SET ..., version = version + 1 WHERE id = ? AND version = ?</code>: zero rows updated means someone else won. ETags also save bandwidth on reads: <code>If-None-Match</code> lets the server answer <code>304 Not Modified</code> with no body.",
        ),
        section(
            "Versioning and evolution",
            "Most changes should not need a new version. <strong>Additive</strong> changes are backward compatible: new endpoints, new optional fields in requests, new fields in responses (clients must ignore unknown fields). <strong>Breaking</strong> changes need a new version: removing or renaming a field, changing a type or meaning, making an optional field required, changing error codes.",
            table(
                ["Strategy", "Example", "Notes"],
                [
                    ["URL path", "<code>/v1/orders</code>, <code>/v2/orders</code>", "Obvious, cache-friendly; the most common choice"],
                    ["Header", "<code>Accept: application/vnd.acme.v2+json</code>", "Clean URLs, harder to test in a browser"],
                    ["Dated versions", "<code>Stripe-Version: 2024-06-20</code>", "Each account pinned to the version it integrated against; the server translates"],
                    ["Field-level evolution", "Protobuf field numbers, GraphQL <code>@deprecated</code>", "Avoids whole-API versions"],
                ],
            ),
            "Whichever you choose, announce deprecations with dates, emit a <code>Deprecation</code>/<code>Sunset</code> header, measure who still calls the old version, and keep it running until they have moved.",
        ),
    ],
    questions=[
        question(
            "Design the API for a timeline: users fetch their home feed, newest first, and scroll back for days.",
            "medium",
            "<code>GET /v1/users/{id}/feed?limit=20&amp;cursor=...</code> returning <code>{items: [...], next_cursor: \"...\"}</code>, with <code>next_cursor</code> absent on the last page. Cursor pagination, because new posts arrive constantly at the top and offsets would duplicate items; the cursor encodes the (score or timestamp, post id) of the last item, opaque to clients. Cap <code>limit</code> server-side. To check for new posts at the top, a separate <code>?since=&lt;newest id&gt;</code> query or a push channel. Each item carries enough for rendering (author name, avatar URL, counts) to avoid one request per item &mdash; or the response includes a side-loaded map of users.",
        ),
        question(
            "Why is offset pagination slow on deep pages?",
            "medium",
            "<code>OFFSET 100000 LIMIT 20</code> makes the database produce the first 100,020 rows in sort order and throw away 100,000 of them: cost grows linearly with page depth, even with an index. Keyset pagination starts from an index position (<code>WHERE (ts, id) &lt; (?, ?)</code>), so every page is an index seek plus 20 rows.",
        ),
        question(
            "A mobile client retries <code>POST /orders</code> after a timeout and creates two orders. Fix it.",
            "medium",
            "Make the operation idempotent. The client generates a unique key per logical order (when the user taps &ldquo;place order&rdquo;, not per HTTP attempt) and sends it as <code>Idempotency-Key</code>. The server, in the same transaction that creates the order, records the key with the response; a retry with the same key returns the stored response with no new order. Alternatively, let the client create the order id itself (a UUID) and make <code>PUT /orders/{id}</code> the create call, which is naturally idempotent.",
        ),
        question(
            "What is the difference between <code>PUT</code> and <code>PATCH</code>, and which are idempotent?",
            "medium",
            "<code>PUT</code> replaces the whole resource with the representation sent; repeating it leaves the same state, so it is idempotent. <code>PATCH</code> applies a partial change; whether it is idempotent depends on the patch: &ldquo;set title to X&rdquo; is, &ldquo;append item&rdquo; or &ldquo;increment counter&rdquo; is not. <code>GET</code>, <code>HEAD</code>, <code>PUT</code> and <code>DELETE</code> are idempotent by definition; <code>POST</code> is not. Idempotent methods are the ones clients and proxies may retry automatically.",
        ),
    ],
    refs=[
        ("Stripe: Idempotent requests", "https://docs.stripe.com/api/idempotent_requests"),
        ("Use the Index, Luke: Paging through results (keyset pagination)", "https://use-the-index-luke.com/no-offset"),
        ("MDN: HTTP conditional requests", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests"),
        ("Google: API design guide", "https://cloud.google.com/apis/design"),
    ],
)
