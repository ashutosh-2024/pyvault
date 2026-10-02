from ._lld import code, table, note, caveat, question, problem

TEXT_EDITOR = problem(
    id="text-editor",
    title="Design a Text Editor with Undo/Redo",
    level="medium",
    patterns=["Command", "Memento"],
    summary="Insert, delete and replace as command objects with undo, redo stacks, merging of consecutive typing.",
    statement=[
        "Design the editing core of a text editor: insert text at the cursor, delete a range, find-and-replace, with unlimited undo and redo. Typing a word should undo as one step, not one step per character.",
    ],
    requirements=[
        "Operations: insert, delete (backspace), replace-all. <code>undo</code> reverts the last operation; <code>redo</code> re-applies it; a new edit after undo discards the redo history. Consecutive single-character inserts at adjacent positions merge into one undo step.",
    ],
    choose=[
        ["Undo and redo of edits", "Command", "Each edit is an object with <code>do</code> and <code>undo</code>"],
        ["Replace-all has no cheap inverse", "Memento", "That command snapshots the text before applying"],
        ["Typing merges into one step", "Command merging", "A new insert command can absorb itself into the previous one"],
    ],
    classes=[
        ["<code>Document</code>", "Text buffer and cursor; low-level insert/delete"],
        ["<code>Insert</code>, <code>Delete</code>, <code>ReplaceAll</code>", "Commands with <code>do</code>/<code>undo</code>; <code>Insert.merge</code>"],
        ["<code>Editor</code>", "Undo and redo stacks; runs commands"],
    ],
    implementation=[
        code('''
            class Document:
                def __init__(self): self.text = ""
                def insert(self, pos, s): self.text = self.text[:pos] + s + self.text[pos:]
                def delete(self, pos, n):
                    removed = self.text[pos:pos + n]
                    self.text = self.text[:pos] + self.text[pos + n:]
                    return removed

            class Insert:
                def __init__(self, pos, s): self.pos, self.s = pos, s
                def do(self, doc): doc.insert(self.pos, self.s)
                def undo(self, doc): doc.delete(self.pos, len(self.s))
                def merge(self, other):                       # typing "c" right after "ab"
                    if isinstance(other, Insert) and other.pos == self.pos + len(self.s) \\
                            and len(other.s) == 1 and " " not in (other.s, self.s[-1]):
                        self.s += other.s
                        return True
                    return False

            class Delete:
                def __init__(self, pos, n): self.pos, self.n, self.removed = pos, n, ""
                def do(self, doc): self.removed = doc.delete(self.pos, self.n)
                def undo(self, doc): doc.insert(self.pos, self.removed)
                def merge(self, other): return False

            class ReplaceAll:
                def __init__(self, old, new): self.old, self.new, self.snapshot = old, new, None
                def do(self, doc):
                    self.snapshot = doc.text                      # memento
                    doc.text = doc.text.replace(self.old, self.new)
                def undo(self, doc): doc.text = self.snapshot
                def merge(self, other): return False

            class Editor:
                def __init__(self):
                    self.doc, self.undos, self.redos = Document(), [], []

                def run(self, cmd):
                    cmd.do(self.doc)
                    self.redos.clear()
                    if self.undos and self.undos[-1].merge(cmd):
                        return
                    self.undos.append(cmd)

                def type(self, pos, text):
                    for i, ch in enumerate(text):
                        self.run(Insert(pos + i, ch))

                def undo(self):
                    if self.undos:
                        cmd = self.undos.pop(); cmd.undo(self.doc); self.redos.append(cmd)

                def redo(self):
                    if self.redos:
                        cmd = self.redos.pop(); cmd.do(self.doc); self.undos.append(cmd)

            ed = Editor()
            ed.type(0, "hello world")
            print(repr(ed.doc.text), "| undo steps:", len(ed.undos))
            ed.run(ReplaceAll("o", "0"))
            ed.run(Delete(0, 6))
            print(repr(ed.doc.text))
            ed.undo(); print("undo  ->", repr(ed.doc.text))
            ed.undo(); print("undo  ->", repr(ed.doc.text))
            ed.redo(); print("redo  ->", repr(ed.doc.text))
            ed.type(len(ed.doc.text), "!")
            ed.redo(); print("redo after a new edit does nothing ->", repr(ed.doc.text))
            for _ in range(5): ed.undo()
            print("undo everything ->", repr(ed.doc.text))
        '''),
        "&ldquo;hello world&rdquo; became three undo steps &mdash; &ldquo;hello&rdquo;, the space, &ldquo;world&rdquo; &mdash; because merging stops at a space, which is how real editors group typing into words.",
    ],
    extend=[
        "Large files need a better buffer than a Python string (every insert copies the text): a gap buffer, a rope or a piece table makes inserts O(log n) or amortised O(1). Collaborative editing replaces the undo stack with operational transformation or CRDTs, where commands from different users are transformed against each other.",
    ],
    questions=[
        question(
            "Why does a new edit clear the redo stack?",
            "medium",
            "Redo replays commands that were undone, assuming the document is in the state they were undone from. After a new edit the document has diverged; replaying an old command (say, an insert at position 40) could land in the wrong place or corrupt text. Editors with branching undo history (Vim's undo tree) keep the alternatives instead of discarding them.",
        ),
        question(
            "Command with inverse vs Memento snapshot: when do you use which?",
            "medium",
            "Use an inverse when one exists and is cheap: insert/delete store only the affected text, so memory is proportional to the edit. Use a snapshot when the operation has no simple inverse or touches the whole document (replace-all, reformat): store the previous state, ideally only the changed region. Many editors mix both, as here.",
        ),
    ],
)


FILE_SYSTEM = problem(
    id="file-system",
    title="Design an In-Memory File System",
    level="medium",
    patterns=["Composite", "Iterator"],
    summary="Directories and files as a composite tree, path resolution, mkdir -p, ls, cat, du and find.",
    statement=[
        "Design an in-memory file system with <code>mkdir</code> (creating parents), <code>write</code>/<code>append</code> to a file, <code>read</code>, <code>ls</code>, total size of a directory and a <code>find</code> by name pattern. LeetCode 588 is the core of it.",
    ],
    requirements=[
        "Absolute paths like <code>/a/b/c.txt</code>. <code>ls</code> on a file returns its name; on a directory, its sorted children. Size of a directory is the sum of its contents. Errors for missing paths and writing to a directory.",
    ],
    choose=[
        ["Directories contain files and directories", "Composite", "<code>File</code> and <code>Directory</code> share <code>size()</code> and <code>name</code>"],
        ["Walk every entry for find/du", "Iterator (generator)", "A recursive generator yields (path, node) pairs"],
    ],
    classes=[
        ["<code>Node</code>", "Common interface: name, <code>size()</code>"],
        ["<code>File</code>", "Content"],
        ["<code>Directory</code>", "Children dict; <code>size()</code> sums children; <code>walk()</code>"],
        ["<code>FileSystem</code>", "Path parsing and the public operations"],
    ],
    implementation=[
        code('''
            import fnmatch

            class Node:
                def __init__(self, name): self.name = name

            class File(Node):
                def __init__(self, name): super().__init__(name); self.content = ""
                def size(self): return len(self.content)

            class Directory(Node):
                def __init__(self, name): super().__init__(name); self.children = {}
                def size(self): return sum(c.size() for c in self.children.values())
                def walk(self, path=""):
                    for name in sorted(self.children):
                        child, child_path = self.children[name], f"{path}/{name}"
                        yield child_path, child
                        if isinstance(child, Directory):
                            yield from child.walk(child_path)

            class FileSystem:
                def __init__(self): self.root = Directory("")

                @staticmethod
                def _parts(path): return [p for p in path.split("/") if p]

                def _resolve(self, path):
                    node = self.root
                    for part in self._parts(path):
                        if not isinstance(node, Directory) or part not in node.children:
                            raise FileNotFoundError(path)
                        node = node.children[part]
                    return node

                def mkdir(self, path):
                    node = self.root
                    for part in self._parts(path):
                        nxt = node.children.setdefault(part, Directory(part))
                        if isinstance(nxt, File):
                            raise NotADirectoryError(f"{part} is a file")
                        node = nxt

                def write(self, path, text, append=False):
                    *dirs, name = self._parts(path)
                    parent = self._resolve("/" + "/".join(dirs))
                    node = parent.children.setdefault(name, File(name))
                    if isinstance(node, Directory):
                        raise IsADirectoryError(path)
                    node.content = node.content + text if append else text

                def read(self, path):
                    node = self._resolve(path)
                    if isinstance(node, Directory):
                        raise IsADirectoryError(path)
                    return node.content

                def ls(self, path="/"):
                    node = self._resolve(path)
                    return [node.name] if isinstance(node, File) else sorted(node.children)

                def du(self, path="/"): return self._resolve(path).size()

                def find(self, pattern, path="/"):
                    base = self._resolve(path)
                    prefix = path.rstrip("/")
                    return [prefix + p for p, n in base.walk() if fnmatch.fnmatch(n.name, pattern)]

            fs = FileSystem()
            fs.mkdir("/home/ann/docs")
            fs.mkdir("/var/log")
            fs.write("/home/ann/docs/cv.txt", "python, sql")
            fs.write("/home/ann/notes.txt", "buy milk")
            fs.write("/home/ann/notes.txt", ", call bob", append=True)
            fs.write("/var/log/app.log", "x" * 100)
            print(fs.ls("/"), fs.ls("/home/ann"), fs.ls("/home/ann/notes.txt"))
            print(repr(fs.read("/home/ann/notes.txt")))
            print("du /home:", fs.du("/home"), "| du /:", fs.du("/"))
            print("find *.txt:", fs.find("*.txt"))
            for bad in (lambda: fs.read("/home/ann"), lambda: fs.ls("/nope"), lambda: fs.mkdir("/home/ann/notes.txt/x")):
                try:
                    bad()
                except OSError as e:
                    print(type(e).__name__, e)
        '''),
    ],
    extend=[
        "Permissions and owners are attributes on <code>Node</code> checked during resolution. Symlinks are a third node type resolved with a depth limit to avoid loops. Caching each directory's size makes <code>du</code> O(1) but every write must update ancestors &mdash; a classic read-versus-write trade-off.",
    ],
    questions=[
        question(
            "How would you support <code>mv /a/b /c/d</code> efficiently?",
            "medium",
            "Resolve both parents, check that the destination is not inside the source (moving a directory into its own subtree would create a cycle), detach the node from the old parent's children and attach it under the new name. Because children are stored by reference, the move is O(path length), regardless of subtree size. Update cached sizes on both ancestor chains if you keep them.",
        ),
        question(
            "Why is the Composite pattern a good fit here?",
            "medium",
            "Operations like size, listing, search and permission checks must work the same whether the target is a file or a whole tree. With a common interface, <code>du</code> is one call on the root and the recursion lives in <code>Directory.size</code>; client code never type-checks every child. New node types (symlink, mount point) slot in by implementing the same interface.",
        ),
    ],
)


COFFEE_ORDER = problem(
    id="coffee-order",
    title="Design a Coffee / Pizza Ordering System with Add-ons",
    level="easy",
    patterns=["Decorator", "Builder"],
    summary="Base drinks wrapped by stackable add-ons that change price and description, assembled with a builder.",
    statement=[
        "Design the menu model for a coffee shop: a customer picks a base drink and any number of add-ons (extra shot, oat milk, syrup, whipped cream), possibly the same add-on twice. Each add-on changes the price and the description. New add-ons appear every season.",
    ],
    requirements=[
        "Compute price and description for any combination. Add-ons can repeat. Adding a new add-on must not change existing classes. Validate a few rules (at most 4 shots).",
    ],
    choose=[
        ["Optional extras that stack in any combination", "Decorator", "Each add-on wraps a beverage; no subclass per combination"],
        ["Assemble an order step by step with validation", "Builder", "A fluent builder applies add-ons and checks rules at <code>build()</code>"],
    ],
    choose_notes=["Subclassing per combination (<code>LatteWithOatAndVanilla</code>) explodes combinatorially; a list of add-on names with a price table would work for price but loses per-add-on behaviour (an add-on that changes size, or whose price depends on the base)."],
    classes=[
        ["<code>Beverage</code>", "Interface: <code>cost()</code>, <code>description()</code>"],
        ["<code>Espresso</code>, <code>Latte</code>", "Base drinks"],
        ["<code>AddOn</code> and subclasses", "Decorators wrapping a beverage"],
        ["<code>OrderBuilder</code>", "Fluent assembly and validation"],
    ],
    implementation=[
        code('''
            from abc import ABC, abstractmethod

            class Beverage(ABC):
                @abstractmethod
                def cost(self) -> int: ...
                @abstractmethod
                def description(self) -> str: ...
                def shots(self): return 0

            class Espresso(Beverage):
                def cost(self): return 120
                def description(self): return "espresso"
                def shots(self): return 1

            class Latte(Beverage):
                def cost(self): return 180
                def description(self): return "latte"
                def shots(self): return 1

            class AddOn(Beverage):
                price, label = 0, ""
                def __init__(self, inner: Beverage): self.inner = inner
                def cost(self): return self.inner.cost() + self.price
                def description(self): return f"{self.inner.description()} + {self.label}"
                def shots(self): return self.inner.shots()

            class ExtraShot(AddOn):
                price, label = 40, "shot"
                def shots(self): return self.inner.shots() + 1

            class OatMilk(AddOn):
                price, label = 35, "oat milk"

            class Vanilla(AddOn):
                price, label = 25, "vanilla"

            class Large(AddOn):                       # price depends on what it wraps
                label = "large"
                def cost(self): return round(self.inner.cost() * 1.3)

            ADDONS = {cls.__name__.lower(): cls for cls in (ExtraShot, OatMilk, Vanilla, Large)}

            class OrderBuilder:
                def __init__(self, base): self.drink = base
                def add(self, name, times=1):
                    for _ in range(times):
                        self.drink = ADDONS[name](self.drink)
                    return self
                def build(self):
                    if self.drink.shots() > 4:
                        raise ValueError(f"{self.drink.shots()} shots is too many")
                    return self.drink

            orders = [
                OrderBuilder(Espresso()).build(),
                OrderBuilder(Latte()).add("oatmilk").add("vanilla").build(),
                OrderBuilder(Latte()).add("extrashot", 2).add("large").build(),
                OrderBuilder(Latte()).add("large").add("extrashot", 2).build(),
            ]
            for d in orders:
                print(f"{d.cost():4}  {d.description()}  ({d.shots()} shots)")
            try:
                OrderBuilder(Espresso()).add("extrashot", 4).build()
            except ValueError as e:
                print("ValueError:", e)
        '''),
        "The last two orders contain the same items in a different order and cost different amounts, because <code>Large</code> multiplies whatever it wraps. Whether that is a bug or a pricing policy is a product decision; the design makes it visible. To make it order-independent, apply size last in the builder.",
    ],
    extend=[
        "A seasonal add-on is one new class and one registry entry. Pizzas work identically: a base (thin crust) wrapped by toppings, with rules like &ldquo;at most 2 cheese&rdquo; in the builder. Persisting an order means saving the base and the list of add-on names, and rebuilding the decorator chain on load.",
    ],
    questions=[
        question(
            "Decorator vs a list of add-on names on the drink: which would you choose?",
            "medium",
            "If add-ons only add a fixed price and a label, a list plus a price table is simpler, serialises trivially and is easy to query (&ldquo;how many oat milks today?&rdquo;). Decorators earn their keep when add-ons have behaviour: pricing that depends on the base or on other add-ons, changing the size or shot count, or validation. A common compromise stores the list and builds decorators from it when pricing.",
        ),
        question(
            "How does the Decorator pattern respect the Open/Closed principle here?",
            "medium",
            "Existing beverages and add-ons are never modified to support a new add-on; you add a class that wraps any <code>Beverage</code>. Clients still see one interface (<code>cost</code>, <code>description</code>), so the checkout code is unchanged too.",
        ),
    ],
)


PAYMENT_GATEWAY = problem(
    id="payment-gateway",
    title="Design a Payment Processing Module",
    level="medium",
    patterns=["Adapter", "Strategy", "Factory", "State"],
    summary="Multiple providers behind one interface via adapters, routing strategy with failover, idempotency and payment states.",
    statement=[
        "Design the payment module of an e-commerce backend. It must support several payment providers (each with its own SDK), choose a provider per payment (by method, cost or availability), fail over when one is down, and never charge a customer twice for one order.",
    ],
    requirements=[
        "Methods: card, UPI, wallet. Providers have different APIs and units. A routing rule picks providers in order of preference; on a provider outage, try the next. Payments move through created &rarr; authorised &rarr; captured, or failed / refunded. Repeated requests with the same idempotency key return the original result.",
    ],
    choose=[
        ["Each provider SDK has a different API", "Adapter", "One <code>PaymentProvider</code> interface; one adapter per SDK"],
        ["Choose provider by method, fee, success rate", "Strategy", "Routing is a swappable policy"],
        ["Create adapters from configuration", "Factory", "Provider name &rarr; adapter instance"],
        ["Payment lifecycle with legal transitions", "State (transition table)", "No capture before authorisation, no refund of a failed payment"],
    ],
    classes=[
        ["<code>PaymentProvider</code>", "Interface: <code>charge(amount_paise, method, key)</code>"],
        ["<code>RazorpayAdapter</code>, <code>StripeAdapter</code>", "Translate to each fake SDK"],
        ["<code>Router</code>", "Strategy: ordered providers for a payment"],
        ["<code>Payment</code>", "Amount, status, provider; transitions"],
        ["<code>PaymentService</code>", "Idempotency, routing with failover"],
    ],
    implementation=[
        code('''
            class ProviderDown(Exception): pass

            class RazorpaySDK:                          # amounts in paise, returns dicts
                def __init__(self, up=True): self.up = up
                def create_payment(self, paise, mode):
                    if not self.up: raise ProviderDown("razorpay 503")
                    return {"razorpay_payment_id": "pay_R1", "status": "captured"}

            class StripeSDK:                            # amounts in rupees as float, returns objects
                class Charge:
                    def __init__(self, ok): self.paid, self.id = ok, "ch_S1"
                def charge(self, amount, currency, source):
                    return self.Charge(ok=source != "card_declined")

            class RazorpayAdapter:
                name, methods = "razorpay", {"card", "upi", "wallet"}
                def __init__(self, sdk): self.sdk = sdk
                def charge(self, paise, method, token):
                    r = self.sdk.create_payment(paise, method)
                    return r["status"] == "captured", r["razorpay_payment_id"]

            class StripeAdapter:
                name, methods = "stripe", {"card"}
                def __init__(self, sdk): self.sdk = sdk
                def charge(self, paise, method, token):
                    c = self.sdk.charge(paise / 100, "inr", token)
                    return c.paid, c.id

            class CheapestFirst:
                FEES = {"razorpay": 2.0, "stripe": 2.9}
                def order(self, providers, method):
                    ok = [p for p in providers if method in p.methods]
                    return sorted(ok, key=lambda p: self.FEES[p.name])

            TRANSITIONS = {"created": {"captured", "failed"}, "captured": {"refunded"},
                           "failed": set(), "refunded": set()}

            class Payment:
                def __init__(self, key, paise): self.key, self.paise, self.status, self.ref = key, paise, "created", None
                def move(self, to):
                    if to not in TRANSITIONS[self.status]:
                        raise ValueError(f"{self.status} -> {to} not allowed")
                    self.status = to

            class PaymentService:
                def __init__(self, providers, router):
                    self.providers, self.router, self.by_key = providers, router, {}

                def pay(self, key, paise, method, token="tok"):
                    if key in self.by_key:                        # idempotent retry
                        return self.by_key[key]
                    p = Payment(key, paise)
                    self.by_key[key] = p
                    for provider in self.router.order(self.providers, method):
                        try:
                            ok, ref = provider.charge(paise, method, token)
                        except ProviderDown as e:
                            print(f"  {provider.name} down ({e}), failing over")
                            continue
                        p.ref = f"{provider.name}:{ref}"
                        p.move("captured" if ok else "failed")
                        return p
                    p.move("failed")
                    return p

            svc = PaymentService([RazorpayAdapter(RazorpaySDK(up=False)), StripeAdapter(StripeSDK())], CheapestFirst())
            a = svc.pay("order-1", 49_900, "card")
            print("order-1:", a.status, a.ref)
            again = svc.pay("order-1", 49_900, "card")
            print("retry returns the same payment:", again is a)
            print("order-2:", svc.pay("order-2", 9_900, "upi").status, "(only razorpay does UPI, and it is down)")
            print("order-3:", svc.pay("order-3", 100, "card", token="card_declined").status)
            a.move("refunded"); print("refund order-1:", a.status)
            try:
                a.move("captured")
            except ValueError as e:
                print("ValueError:", e)
        '''),
    ],
    extend=[
        "Adding a provider is one adapter plus a router entry. Routing by success rate (send traffic to whichever provider is approving most payments for this card network right now) is a smarter strategy fed by metrics. The provider's webhooks (payment captured, refunded, disputed) feed the same state machine, which is why transitions must be validated: webhooks arrive late, twice, or out of order.",
    ],
    questions=[
        question(
            "The provider call timed out. Did the charge happen? What do you do?",
            "hard",
            "You do not know, so treat the payment as pending, not failed. Never retry with a different provider blindly, or the customer may be charged twice. Retry the same provider with the same idempotency key (most providers deduplicate on it), or query the provider's status API for that key, or wait for its webhook. Only when the provider confirms the charge did not happen is failover safe. A reconciliation job compares your records with provider settlement reports daily.",
        ),
        question(
            "Why put an adapter in front of every provider SDK even if you only use one today?",
            "medium",
            "It confines the vendor's types, units (paise vs rupees), error classes and quirks to one class. The rest of the codebase depends on your interface, so tests can use a fake provider, an SDK upgrade touches one file, and adding a second provider for failover or cost does not ripple through checkout code.",
        ),
    ],
)


SHOPPING_CART = problem(
    id="shopping-cart",
    title="Design a Shopping Cart with Discount Rules",
    level="medium",
    patterns=["Strategy", "Composite", "Chain of Responsibility"],
    summary="Cart lines, composable promotion rules (percentage, buy-X-get-Y, threshold, coupon), best-discount selection.",
    statement=[
        "Design the pricing of a shopping cart. Marketing keeps inventing promotions: 10% off a category, buy 2 get 1 free, &#8377;200 off orders above &#8377;2000, coupon codes. Some promotions stack, others are exclusive and the customer should get the better one.",
    ],
    requirements=[
        "Cart with products, quantities and categories. A discount rule computes a discount for a cart (or zero). Rules can be combined: <em>all of</em> (stack) or <em>best of</em> (exclusive). Final total never goes below zero. Show which rules applied.",
    ],
    choose=[
        ["Many kinds of discount, more coming", "Strategy", "Each rule is a class with <code>apply(cart)</code>"],
        ["Rules combined as stack or best-of, nested", "Composite", "<code>AllOf</code> and <code>BestOf</code> are rules containing rules"],
        ["Rules evaluated in sequence, each sees the previous result", "Chain of Responsibility", "Threshold rules apply to the already-discounted subtotal"],
    ],
    classes=[
        ["<code>Line</code>, <code>Cart</code>", "Products, quantities, prices in paise"],
        ["<code>Rule</code>", "Strategy: <code>discount(cart, subtotal)</code> &rarr; (amount, labels)"],
        ["<code>PercentOffCategory</code>, <code>BuyXGetY</code>, <code>Threshold</code>, <code>Coupon</code>", "Concrete rules"],
        ["<code>AllOf</code>, <code>BestOf</code>", "Composite rules"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass

            @dataclass
            class Line:
                sku: str
                category: str
                price: int            # paise
                qty: int

            class Cart:
                def __init__(self, *lines, coupon=None): self.lines, self.coupon = list(lines), coupon
                def subtotal(self): return sum(l.price * l.qty for l in self.lines)

            class PercentOffCategory:
                def __init__(self, cat, pct): self.cat, self.pct = cat, pct
                def discount(self, cart, running):
                    amt = sum(l.price * l.qty for l in cart.lines if l.category == self.cat) * self.pct // 100
                    return amt, [f"{self.pct}% off {self.cat}"] if amt else []

            class BuyXGetY:
                def __init__(self, sku, x, y): self.sku, self.x, self.y = sku, x, y
                def discount(self, cart, running):
                    for l in cart.lines:
                        if l.sku == self.sku:
                            free = (l.qty // (self.x + self.y)) * self.y
                            if free:
                                return free * l.price, [f"buy {self.x} get {self.y} on {self.sku}"]
                    return 0, []

            class Threshold:
                def __init__(self, above, off): self.above, self.off = above, off
                def discount(self, cart, running):
                    return (self.off, [f"{self.off // 100} off above {self.above // 100}"]) if running > self.above else (0, [])

            class Coupon:
                def __init__(self, code, off): self.code, self.off = code, off
                def discount(self, cart, running):
                    return (self.off, [f"coupon {self.code}"]) if cart.coupon == self.code else (0, [])

            class AllOf:                                      # stack, in order (a chain)
                def __init__(self, *rules): self.rules = rules
                def discount(self, cart, running):
                    total, labels = 0, []
                    for r in self.rules:
                        amt, lab = r.discount(cart, running - total)
                        total += amt; labels += lab
                    return total, labels

            class BestOf:                                     # exclusive: customer gets the best
                def __init__(self, *rules): self.rules = rules
                def discount(self, cart, running):
                    return max((r.discount(cart, running) for r in self.rules), key=lambda d: d[0])

            def checkout(cart, rule):
                sub = cart.subtotal()
                off, labels = rule.discount(cart, sub)
                off = min(off, sub)
                return f"subtotal {sub / 100:.0f} - {off / 100:.0f} = {(sub - off) / 100:.0f}  {labels}"

            promotions = AllOf(
                BestOf(PercentOffCategory("shoes", 20), BuyXGetY("socks", 2, 1)),   # exclusive pair
                Threshold(above=2000_00, off=200_00),                               # applies after them
                Coupon("WELCOME", 100_00),
            )
            carts = {
                "shoes + socks": Cart(Line("runner", "shoes", 3000_00, 1), Line("socks", "apparel", 200_00, 3)),
                "lots of socks": Cart(Line("socks", "apparel", 200_00, 9)),
                "coupon, small": Cart(Line("cap", "apparel", 500_00, 1), coupon="WELCOME"),
            }
            for name, cart in carts.items():
                print(f"{name:14} {checkout(cart, promotions)}")
        '''),
        "In the first cart the shoe discount (600) beat the socks offer (200), so only it applied; the threshold rule then saw the already-discounted 3000 and still applied. In the second, nine socks cost 1800 before any discount, so the threshold did not apply. A rule tree like this is data: marketing changes promotions by changing the tree, not the code.",
    ],
    extend=[
        "Rules can be loaded from JSON into this composite structure, so promotions are configured without deploys. Exclusions (&ldquo;not with sale items&rdquo;) are filters a rule applies to the lines it considers. For auditability, each label should carry the rule id and the amount, so customer support can explain a total.",
    ],
    questions=[
        question(
            "Why pass the running total into each rule?",
            "medium",
            "Some rules depend on what is left after earlier discounts (a threshold on the payable amount, a percentage of the remaining total), and the order of application changes the result. Making the running total explicit puts that dependency in the interface and makes the order a visible, testable decision in the rule tree.",
        ),
        question(
            "How would you guarantee the customer always gets the best combination of exclusive offers?",
            "hard",
            "For a small number of exclusive groups, evaluate each option and take the maximum, as <code>BestOf</code> does; nested combinations stay correct because each node returns its own best. With many interacting offers (one item can only be used by one offer), the problem becomes an optimisation (assignment of items to offers), solvable by search over the few relevant offers or integer programming; most shops avoid it by limiting stacking rules.",
        ),
    ],
)


FOOD_DELIVERY = problem(
    id="food-delivery",
    title="Design a Food Delivery Order Lifecycle",
    level="medium",
    patterns=["State", "Observer", "Strategy"],
    summary="Order states with guarded transitions per actor, cancellation and refund rules by state, notifications to all parties.",
    statement=[
        "Design the order workflow of a Swiggy/Zomato-style app. An order passes through placed, accepted by the restaurant, preparing, picked up by a rider, delivered; it can be cancelled or rejected at some points. Customer, restaurant and rider each see updates, and refunds depend on when an order is cancelled.",
    ],
    requirements=[
        "Only certain actors may trigger certain transitions (the restaurant accepts; the rider picks up). Cancellation by the customer is free before acceptance, 50% refund while preparing, none after pickup. Every transition notifies the relevant parties and is recorded with a timestamp.",
    ],
    choose=[
        ["Allowed actions depend on the order's state", "State", "Each state class lists its transitions and who may trigger them"],
        ["Customer, restaurant and rider apps update on each change", "Observer", "Listeners per party"],
        ["Refund depends on the state at cancellation", "Strategy (per state)", "Each state knows its refund fraction"],
    ],
    classes=[
        ["<code>OrderState</code> subclasses", "Placed, Accepted, Preparing, PickedUp, Delivered, Cancelled"],
        ["<code>Order</code>", "Context: amount, current state, history, listeners"],
    ],
    implementation=[
        code('''
            class OrderState:
                name = "?"
                transitions: dict = {}          # action -> (actor allowed, next state class name)
                refund = 0.0
                def act(self, order, action, actor):
                    if action not in self.transitions:
                        raise ValueError(f"cannot {action} when {self.name}")
                    allowed, nxt = self.transitions[action]
                    if actor != allowed:
                        raise PermissionError(f"{actor} cannot {action}")
                    return STATES[nxt]()

            class Placed(OrderState):
                name, refund = "placed", 1.0
                transitions = {"accept": ("restaurant", "Accepted"), "reject": ("restaurant", "Cancelled"),
                               "cancel": ("customer", "Cancelled")}
            class Accepted(OrderState):
                name, refund = "accepted", 1.0
                transitions = {"start": ("restaurant", "Preparing"), "cancel": ("customer", "Cancelled")}
            class Preparing(OrderState):
                name, refund = "preparing", 0.5
                transitions = {"pickup": ("rider", "PickedUp"), "cancel": ("customer", "Cancelled")}
            class PickedUp(OrderState):
                name, refund = "picked up", 0.0
                transitions = {"deliver": ("rider", "Delivered")}
            class Delivered(OrderState):
                name = "delivered"
            class Cancelled(OrderState):
                name = "cancelled"

            STATES = {c.__name__: c for c in (Placed, Accepted, Preparing, PickedUp, Delivered, Cancelled)}

            class Order:
                def __init__(self, oid, amount):
                    self.id, self.amount, self.state = oid, amount, Placed()
                    self.history, self.listeners, self.refunded = [("placed", 0)], [], 0

                def act(self, action, actor, t):
                    before = self.state
                    self.state = before.act(self, action, actor)
                    if isinstance(self.state, Cancelled):
                        self.refunded = round(self.amount * before.refund)
                    self.history.append((self.state.name, t))
                    for fn in self.listeners:
                        fn(self, action, actor)

            def notify(order, action, actor):
                parties = {"accept": "customer", "start": "customer", "pickup": "customer",
                           "deliver": "customer, restaurant", "cancel": "restaurant, rider", "reject": "customer"}
                print(f"  [{order.id}] {actor} did {action!r} -> now {order.state.name}; notify {parties[action]}")

            o = Order("A1", 600)
            o.listeners.append(notify)
            for action, actor, t in [("accept", "restaurant", 1), ("start", "restaurant", 2),
                                     ("pickup", "rider", 15), ("deliver", "rider", 30)]:
                o.act(action, actor, t)
            print("timeline:", o.history)

            b = Order("B2", 800); b.listeners.append(notify)
            b.act("accept", "restaurant", 1); b.act("start", "restaurant", 3)
            for args in [("pickup", "customer", 4), ("cancel", "customer", 5), ("deliver", "rider", 6)]:
                try:
                    b.act(*args)
                except (ValueError, PermissionError) as e:
                    print(f"  {type(e).__name__}: {e}")
            print("B2 refund:", b.refunded)
        '''),
    ],
    extend=[
        "A &ldquo;rider assigned&rdquo; sub-flow and timeouts (auto-cancel if the restaurant does not accept within 5 minutes) are a new state and a scheduled event. Because states are data plus a small class, the state diagram can be generated from <code>transitions</code> for documentation and tested exhaustively: every (state, action, actor) combination either succeeds or raises.",
    ],
    questions=[
        question(
            "The restaurant's &ldquo;accept&rdquo; and the customer's &ldquo;cancel&rdquo; arrive at the same time. What should happen?",
            "hard",
            "Transitions must be serialised per order: apply them one at a time in a single place (a database row update with a version check, or a per-order actor/queue). Whichever is applied first wins; the second is evaluated against the new state. If cancel wins, accept fails with &ldquo;cannot accept when cancelled&rdquo; and the restaurant is told; if accept wins, cancel succeeds with the refund rule of Accepted. A compare-and-set on (order id, expected state) is the usual implementation.",
        ),
        question(
            "Why include the actor in the transition rules?",
            "medium",
            "Authorisation is part of the workflow: a customer must not be able to mark food as picked up, and a rider must not cancel on the customer's behalf. Encoding the allowed actor next to each transition keeps the rule in one place, and the API layer only needs to pass who is calling.",
        ),
    ],
)


TRAFFIC_LIGHT = problem(
    id="traffic-light",
    title="Design a Traffic Light Controller",
    level="easy",
    patterns=["State", "Observer"],
    summary="Phases as states with durations, a tick-driven controller, pedestrian requests and an emergency override.",
    statement=[
        "Design the controller for a four-way intersection: north-south and east-west roads alternate green, yellow and red; a pedestrian button shortens the current green; an emergency vehicle can force all-red.",
    ],
    requirements=[
        "Phases: NS green (30 s) &rarr; NS yellow (5 s) &rarr; EW green (30 s) &rarr; EW yellow (5 s) &rarr; repeat. Never green in both directions. Pedestrian request: if the current green has more than 10 s left, cut it to 10 s. Emergency: switch to all-red until cleared. Lights (displays) are notified on every change.",
    ],
    choose=[
        ["Fixed cycle of phases, each with its own duration and next phase", "State", "Each phase knows its duration and successor"],
        ["Physical lights and a monitoring dashboard react to changes", "Observer", "Displays subscribe to phase changes"],
    ],
    classes=[
        ["<code>Phase</code>", "Name, lights per direction, duration, next phase"],
        ["<code>Controller</code>", "Current phase, time remaining, <code>tick</code>, <code>pedestrian</code>, <code>emergency</code>"],
    ],
    implementation=[
        code('''
            from dataclasses import dataclass

            @dataclass(frozen=True)
            class Phase:
                name: str
                ns: str
                ew: str
                duration: int
                next: str

            PHASES = {p.name: p for p in [
                Phase("NS_GREEN", "green", "red", 30, "NS_YELLOW"),
                Phase("NS_YELLOW", "yellow", "red", 5, "EW_GREEN"),
                Phase("EW_GREEN", "red", "green", 30, "EW_YELLOW"),
                Phase("EW_YELLOW", "red", "yellow", 5, "NS_GREEN"),
                Phase("ALL_RED", "red", "red", 10**9, "NS_GREEN"),
            ]}
            assert all(not (p.ns == "green" and p.ew == "green") for p in PHASES.values())   # safety invariant

            class Controller:
                def __init__(self):
                    self.listeners, self.t = [], 0
                    self._enter("NS_GREEN")

                def _enter(self, name):
                    self.phase, self.left = PHASES[name], PHASES[name].duration
                    for fn in self.listeners:
                        fn(self.t, self.phase)

                def tick(self, seconds=1):
                    for _ in range(seconds):
                        self.t += 1
                        self.left -= 1
                        if self.left == 0:
                            self._enter(self.phase.next)

                def pedestrian(self):
                    if "green" in (self.phase.ns, self.phase.ew) and self.left > 10:
                        self.left = 10

                def emergency(self, on):
                    if on:
                        self._enter("ALL_RED")
                    elif self.phase.name == "ALL_RED":
                        self._enter("NS_GREEN")

            c = Controller()
            c.listeners.append(lambda t, p: print(f"  t={t:3}  NS {p.ns:6} EW {p.ew:6} ({p.name})"))
            c.tick(36)                         # NS green, NS yellow, into EW green
            c.tick(5); c.pedestrian()          # 24 s left on EW green: cut to 10
            c.tick(16)
            c.emergency(True); c.tick(20); c.emergency(False)
        '''),
    ],
    extend=[
        "Adaptive timing (longer green for the busier road, from sensor counts) replaces fixed durations with a duration strategy per phase. A left-turn arrow is another phase in the cycle. Hardware safety is enforced twice: by the invariant in software and by a conflict monitor in hardware that forces flashing red if both directions ever show green.",
    ],
    questions=[
        question(
            "How do you guarantee the controller can never show green in both directions?",
            "medium",
            "Make it structurally impossible and then check it. Phases are a fixed table where each entry defines both directions at once, so there is no separate &ldquo;set NS green&rdquo; operation that could race with &ldquo;set EW green&rdquo;. Assert the invariant over the table at start-up (as above) and in tests over every reachable phase. Real intersections add an independent hardware conflict monitor.",
        ),
        question(
            "Why drive the controller with <code>tick()</code> instead of sleeping in a loop?",
            "medium",
            "Separating time from logic makes the controller deterministic and testable: a test can advance 36 simulated seconds instantly and assert exactly which phases occurred. In production a small driver calls <code>tick()</code> once a second from a real timer. The same idea (inject the clock) applies to any time-dependent design.",
        ),
    ],
)

PROBLEMS = [TEXT_EDITOR, FILE_SYSTEM, COFFEE_ORDER, PAYMENT_GATEWAY, SHOPPING_CART, FOOD_DELIVERY, TRAFFIC_LIGHT]
