from deepdive._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="chat-system",
    title="Design a Chat System",
    summary="Persistent connections, routing messages between gateways, per-conversation ordering, delivery and read receipts, presence, offline sync.",
    intro=[
        "A chat system (WhatsApp, Slack, Messenger) differs from most web services in one way that shapes everything: the server must <em>push</em> to clients, instantly, over connections that stay open for hours. That brings in connection gateways, routing a message to whichever server holds the recipient's connection, and a protocol for ordering, acknowledging and resynchronising messages over flaky mobile networks.",
        "This topic builds the core pieces &mdash; sequence numbers, acknowledgements, sync after reconnect, presence with heartbeats &mdash; and runs them against simulated network failures.",
    ],
    sections=[
        section(
            "Requirements and connection scale",
            "Functional: one-to-one and group messages (groups up to a few hundred members), delivery and read receipts, online presence, history synced across a user's devices, media attachments. Non-functional: low latency (sub-second delivery when online), no lost messages, correct order within a conversation, works on unreliable mobile networks.",
            code('''
                dau = 500_000_000
                concurrent_share = 0.2                  # fraction online at peak
                conns_per_gateway = 500_000              # tuned epoll-based server, mostly idle sockets
                messages_per_user_day = 40

                concurrent = dau * concurrent_share
                print(f"open connections at peak : {concurrent:,.0f}")
                print(f"gateway servers          : {concurrent / conns_per_gateway:,.0f} (+ headroom)")
                print(f"messages per second      : {dau * messages_per_user_day / 86_400:,.0f} avg")
                print(f"heartbeats per second    : {concurrent / 30:,.0f} (one every 30 s per connection)")
            '''),
            "The connection count, not the message rate, sizes the edge tier. Keeping a socket open costs memory (kernel buffers, TLS state, a few KB in the app), and every heartbeat is a small packet to process.",
        ),
        section(
            "How clients stay connected",
            table(
                ["Technique", "How", "Trade-off"],
                [
                    ["Short polling", "Ask &ldquo;anything new?&rdquo; every few seconds", "Simple; wasteful and slow"],
                    ["Long polling", "Request hangs until there is a message or a timeout, then reconnect", "Works everywhere; one request per message burst"],
                    ["Server-Sent Events", "One long HTTP response streaming events", "Server-to-client only"],
                    ["WebSocket", "Upgraded HTTP connection, full duplex frames", "The standard for chat; needs stateful gateways"],
                    ["Mobile push (APNs/FCM)", "OS-level notification when the app is in the background", "Wakes the app; not a data channel"],
                ],
            ),
            "The architecture splits into a <strong>stateful</strong> gateway tier that holds WebSocket connections and does little else, and <strong>stateless</strong> services behind it (message service, presence, groups) that can be scaled and deployed freely. Deploying a gateway drops its connections, so clients must reconnect transparently and resync &mdash; which the protocol below handles anyway.",
        ),
        section(
            "Routing a message to the right gateway",
            "Alice's connection is on gateway 3 and Bob's on gateway 17. When Alice sends, the message service must find Bob's gateway. A <strong>session registry</strong> (Redis: <code>user &rarr; {device: gateway}</code>) records where each device is connected; the message service looks it up and forwards the message to that gateway, which writes it to Bob's socket. If Bob is offline, the message waits in storage and a push notification is sent.",
            code('''
                class Gateway:
                    def __init__(self, name):
                        self.name, self.sockets = name, {}
                    def deliver(self, device, msg):
                        self.sockets[device].append(msg)
                        return True

                class ChatService:
                    def __init__(self, gateways):
                        self.gateways = {g.name: g for g in gateways}
                        self.registry = {}                    # (user, device) -> gateway name
                        self.store, self.push_notifications = [], []

                    def connect(self, user, device, gateway):
                        self.registry[(user, device)] = gateway
                        self.gateways[gateway].sockets[device] = []

                    def disconnect(self, user, device):
                        self.registry.pop((user, device), None)

                    def send(self, sender, recipient, text):
                        msg = {"from": sender, "to": recipient, "text": text}
                        self.store.append(msg)                # persist first: never lose it
                        devices = [d for (u, d) in self.registry if u == recipient]
                        for d in devices:
                            self.gateways[self.registry[(recipient, d)]].deliver(d, msg)
                        if not devices:
                            self.push_notifications.append(f"push to {recipient}: {text}")
                        return len(devices)

                g = [Gateway("gw3"), Gateway("gw17")]
                chat = ChatService(g)
                chat.connect("bob", "bob-phone", "gw17")
                chat.connect("bob", "bob-laptop", "gw3")
                print("delivered to", chat.send("alice", "bob", "lunch?"), "devices")
                chat.disconnect("bob", "bob-phone"); chat.disconnect("bob", "bob-laptop")
                print("delivered to", chat.send("alice", "bob", "you there?"), "devices")
                print(chat.push_notifications, "| stored:", len(chat.store))
            '''),
            "Alternatives to a per-message registry lookup: a pub/sub channel per user that gateways subscribe to when a device connects (Redis pub/sub, NATS), or consistent hashing of users onto gateways so the gateway is computable. Registry lookups are simple and handle multiple devices naturally.",
        ),
        section(
            "Ordering: sequence numbers per conversation",
            "Timestamps from different devices cannot order messages: clocks disagree, and two messages can arrive in the opposite order of sending. The server assigns each message a <strong>sequence number per conversation</strong> when it stores it. That number is the order everyone displays, and it doubles as a cursor for syncing.",
            code('''
                import random

                class Conversation:
                    def __init__(self):
                        self.next_seq, self.messages = 1, []

                    def append(self, sender, text):            # serialised per conversation
                        msg = (self.next_seq, sender, text)
                        self.next_seq += 1
                        self.messages.append(msg)
                        return msg

                class Client:
                    def __init__(self):
                        self.view = {}
                    def receive(self, msg):
                        self.view[msg[0]] = msg               # keyed by seq: duplicates are harmless
                    def render(self):
                        return [f"{s}:{who}:{t}" for s, who, t in sorted(self.view.values())]

                conv, bob = Conversation(), Client()
                sent = [conv.append("ann", "hi"), conv.append("cy", "hey"), conv.append("ann", "plans?"),
                        conv.append("cy", "dinner")]
                network = sent + [sent[1]]                    # one duplicate redelivery
                random.Random(4).shuffle(network)              # arrival order is scrambled
                for m in network:
                    bob.receive(m)
                print("arrival order:", [m[0] for m in network])
                print("rendered     :", bob.render())
            '''),
            "Sequencing must be serialised per conversation: route all writes for a conversation to one partition (Kafka partition key, or a database row with an atomic counter), which also bounds the throughput of a single conversation &mdash; fine for chats, a real limit for a channel with a million members.",
        ),
        section(
            "Delivery guarantees: acks, retries and resync",
            "Messages must not be lost when a connection drops mid-send. The protocol has acknowledgements on both legs. The sender's client keeps a message in an outbox, with a client-generated id, until the server acks it, retrying with the same id after a reconnect so the server can deduplicate. The server keeps the message stored and tracks, per device, the highest sequence number the device has acknowledged.",
            "On reconnect, a device sends &ldquo;my last seq in conversation X is N&rdquo; and the server replies with everything after N. That single mechanism handles dropped connections, offline periods and new devices alike.",
            code('''
                import random

                class Server:
                    def __init__(self):
                        self.log, self.seen_client_ids = [], {}
                    def submit(self, client_id, text):
                        if client_id in self.seen_client_ids:          # retry of something we have
                            return self.seen_client_ids[client_id]
                        seq = len(self.log) + 1
                        self.log.append((seq, text))
                        self.seen_client_ids[client_id] = seq
                        return seq
                    def sync(self, after):
                        return [m for m in self.log if m[0] > after]

                class Device:
                    def __init__(self):
                        self.last_seq, self.inbox = 0, []
                    def deliver(self, msgs):
                        for seq, text in msgs:
                            if seq == self.last_seq + 1:              # contiguous only: a gap waits for sync
                                self.inbox.append(text)
                                self.last_seq = seq

                rng = random.Random(9)
                server, reader = Server(), Device()
                outbox = [(f"c{i}", f"msg {i}") for i in range(1, 9)]

                while outbox:                                         # sender with a flaky link
                    cid, text = outbox[0]
                    seq = server.submit(cid, text)
                    if rng.random() < 0.3:
                        continue                                      # ack lost: resend same id
                    outbox.pop(0)
                    if rng.random() < 0.6:                            # live push sometimes fails
                        reader.deliver([(seq, text)])

                reader.deliver(server.sync(after=reader.last_seq))    # reconnect: catch up
                print("server log :", len(server.log), "messages (no duplicates from retries)")
                print("reader got :", reader.inbox == [t for _, t in server.log], reader.inbox[:4], "...")
            '''),
            caveat("The device advances <code>last_seq</code> only over contiguous messages. If it jumped ahead when a live push arrived after a gap, the next sync would start after the gap and the missing message would never arrive. Real clients buffer out-of-order pushes and request the gap rather than dropping them."),
        ),
        section(
            "Receipts, presence and groups",
            "<strong>Receipts</strong>: a device acks <em>delivered</em> when the message reaches it and <em>read</em> when it is displayed; the server forwards these to the sender as tiny messages on the same path. For groups, store read positions as one &ldquo;last read seq&rdquo; per member rather than per message.",
            "<strong>Presence</strong>: each connected device heartbeats every ~30 s; a user is online if any device heartbeat is recent. Store last-seen timestamps in Redis with a TTL, and push presence changes only to users who are looking (an open chat with that contact) &mdash; broadcasting every change to every contact multiplies traffic enormously.",
            code('''
                class Presence:
                    def __init__(self, timeout=60):
                        self.timeout, self.last_beat = timeout, {}
                    def heartbeat(self, user, device, now):
                        self.last_beat[(user, device)] = now
                    def status(self, user, now):
                        beats = [t for (u, _), t in self.last_beat.items() if u == user]
                        if beats and now - max(beats) < self.timeout:
                            return "online"
                        return f"last seen {now - max(beats)}s ago" if beats else "never seen"

                p = Presence()
                p.heartbeat("ann", "phone", now=0)
                p.heartbeat("ann", "laptop", now=50)
                for t in (30, 100, 200):
                    print(f"t={t:3}: ann is {p.status('ann', t)}")
            '''),
            "<strong>Groups</strong>: a message to a group is stored once with the conversation's next seq and fanned out to each member's devices. For small groups, fan out on write; for very large channels, members pull by seq when they open the channel, like the celebrity case in the news feed topic.",
            table(
                ["Data", "Store", "Key / partition"],
                [
                    ["Messages", "Cassandra / HBase / ScyllaDB (write-heavy, time-ordered)", "conversation id, clustered by seq"],
                    ["Conversations, members", "Relational or KV", "conversation id; user &rarr; conversations index"],
                    ["Session registry, presence", "Redis with TTLs", "user id"],
                    ["Per-device sync state", "KV", "(device, conversation) &rarr; last acked seq"],
                    ["Media", "Object storage + CDN", "content hash; message holds a URL"],
                ],
            ),
        ),
    ],
    questions=[
        question(
            "How do you guarantee messages in a conversation are shown in the same order on every device?",
            "medium",
            "Do not rely on client timestamps. The server assigns a monotonically increasing sequence number per conversation when it persists each message, by routing all writes for a conversation through one partition or an atomic counter. Every device sorts by that number, deduplicates by it, and uses the highest contiguous one as its sync cursor. Messages the user typed but the server has not yet acked are shown at the end, marked pending, and placed by their sequence number once acked.",
        ),
        question(
            "A user's phone was offline for two days. What happens when it reconnects?",
            "medium",
            "The client opens a WebSocket to some gateway (any one; the registry is updated), authenticates, and sends its sync state: per conversation, the last sequence number it has. The server returns the list of conversations with newer messages and pages through each one from that seq, newest conversations first so the UI is useful quickly. Messages are acked as they are stored, delivery receipts flow back to senders, and the outbox of messages the user wrote offline is replayed with its client ids so nothing is duplicated.",
        ),
        question(
            "Why separate the WebSocket gateways from the chat logic?",
            "medium",
            "Gateways are stateful (they hold live connections), and every restart forces their clients to reconnect, so you want them simple, rarely deployed and scaled purely by connection count. Chat logic &mdash; validation, storage, fan-out, receipts &mdash; changes often and scales with message volume; keeping it in stateless services means deploying it never drops a connection. The two talk over an internal RPC or pub/sub path, and the session registry tells the logic tier which gateway holds a given device.",
        ),
        question(
            "How would end-to-end encryption change this design?",
            "hard",
            "The server can no longer read message content, so anything that needs content moves to clients: search, link previews, spam detection on content. Each device has a key pair; the server stores public keys and relays encrypted payloads it cannot decrypt. One-to-one chats use a key agreement and ratchet (the Signal protocol); groups encrypt the message once with a group key distributed per member device. Multi-device sync gets harder because each device needs its own encrypted copy, and history for a new device must come from another device rather than the server. Ordering, acks and routing are unchanged, since they only use metadata.",
        ),
    ],
    refs=[
        ("Slack: Real-time messaging architecture", "https://slack.engineering/real-time-messaging/"),
        ("Discord: How Discord stores trillions of messages", "https://discord.com/blog/how-discord-stores-trillions-of-messages"),
        ("WhatsApp: 1 million connections per server (Erlang)", "https://blog.whatsapp.com/1-million-is-so-2011"),
        ("Signal protocol documentation", "https://signal.org/docs/"),
    ],
)
