from ._lld import code, table, note, caveat, section, question, PATTERNS_GROUP

TOPIC = dict(
    id="creational",
    title="Creational Patterns",
    group=PATTERNS_GROUP,
    summary="Factory method and registries, abstract factory, builder, prototype, singleton and object pool - and their Pythonic forms.",
    intro=[
        "Creational patterns decide <em>how objects get made</em>, so that the code using an object does not need to know its concrete class, how complicated it is to assemble, or whether it is shared. They matter whenever &ldquo;which class&rdquo; is a decision made from data (a config value, a request field) rather than written into the code.",
    ],
    sections=[
        section(
            "Factory: deciding which class to create",
            "A factory takes a description (<code>\"car\"</code>, <code>\"upi\"</code>, a config dict) and returns an instance of the right class. Callers depend on the common interface only. The extensible Python form is a <strong>registry</strong>: classes register themselves under a key, so adding a type never edits the factory.",
            code('''
                from abc import ABC, abstractmethod

                class Vehicle(ABC):
                    registry: dict[str, type["Vehicle"]] = {}
                    wheels = 0

                    def __init_subclass__(cls, kind=None, **kw):
                        super().__init_subclass__(**kw)
                        if kind:
                            Vehicle.registry[kind] = cls         # self-registration

                    @classmethod
                    def create(cls, kind, plate):                # the factory
                        try:
                            return cls.registry[kind](plate)
                        except KeyError:
                            raise ValueError(f"unknown vehicle type {kind!r}") from None

                    def __init__(self, plate):
                        self.plate = plate

                    @abstractmethod
                    def spot_size(self) -> str: ...

                class Bike(Vehicle, kind="bike"):
                    wheels = 2
                    def spot_size(self): return "small"

                class Car(Vehicle, kind="car"):
                    wheels = 4
                    def spot_size(self): return "medium"

                class Bus(Vehicle, kind="bus"):
                    wheels = 6
                    def spot_size(self): return "large"

                for kind, plate in [("car", "KA-01"), ("bike", "KA-02"), ("bus", "KA-03")]:
                    v = Vehicle.create(kind, plate)
                    print(f"{type(v).__name__:4} {v.plate} wheels={v.wheels} spot={v.spot_size()}")
                try:
                    Vehicle.create("tank", "X")
                except ValueError as e:
                    print("ValueError:", e)
            '''),
            "Python also gives you <strong>alternative constructors</strong> as <code>classmethod</code>s &mdash; <code>datetime.fromtimestamp</code>, <code>dict.fromkeys</code> &mdash; which are the factory-method idea at the scale of one class: several named ways to build the same type.",
        ),
        section(
            "Abstract factory: families that must match",
            "When objects come in families that must be used together &mdash; a dark-theme button with a dark-theme dialog, AWS storage with AWS queues &mdash; an abstract factory creates the whole family, and swapping the factory swaps all of them at once. It prevents mixing products from different families.",
            code('''
                from typing import Protocol

                class Storage(Protocol):
                    def put(self, key, data) -> str: ...

                class Queue(Protocol):
                    def publish(self, msg) -> str: ...

                class CloudFactory(Protocol):
                    def storage(self) -> Storage: ...
                    def queue(self) -> Queue: ...

                class S3:
                    def put(self, key, data): return f"s3://bucket/{key}"
                class SQS:
                    def publish(self, msg): return f"sqs <- {msg}"
                class AWS:
                    def storage(self): return S3()
                    def queue(self): return SQS()

                class GCS:
                    def put(self, key, data): return f"gs://bucket/{key}"
                class PubSub:
                    def publish(self, msg): return f"pubsub <- {msg}"
                class GCP:
                    def storage(self): return GCS()
                    def queue(self): return PubSub()

                def upload_and_notify(cloud: CloudFactory, name):     # knows no concrete class
                    url = cloud.storage().put(name, b"...")
                    return url, cloud.queue().publish(f"uploaded {url}")

                for cloud in (AWS(), GCP()):
                    print(upload_and_notify(cloud, "report.csv"))
            '''),
        ),
        section(
            "Builder: complex construction step by step",
            "Use a builder when an object has many optional parts, must be validated as a whole, or is naturally assembled in steps (a SQL query, an HTTP request, a meal order). Methods return <code>self</code> for a fluent chain, and <code>build()</code> validates and produces an immutable result.",
            code('''
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class HttpRequest:
                    method: str
                    url: str
                    headers: tuple
                    body: str | None
                    timeout: float

                class RequestBuilder:
                    def __init__(self, url):
                        self._url, self._method = url, "GET"
                        self._headers, self._body, self._timeout = {}, None, 10.0

                    def method(self, m):
                        self._method = m.upper(); return self
                    def header(self, k, v):
                        self._headers[k] = v; return self
                    def json(self, body):
                        self._body = body
                        return self.header("Content-Type", "application/json")
                    def timeout(self, seconds):
                        self._timeout = seconds; return self

                    def build(self):
                        if self._body is not None and self._method == "GET":
                            raise ValueError("GET request cannot have a body")
                        return HttpRequest(self._method, self._url, tuple(sorted(self._headers.items())),
                                           self._body, self._timeout)

                req = (RequestBuilder("https://api.example.com/orders")
                       .method("post").json('{"item": "lamp"}').header("Auth", "token").timeout(2).build())
                print(req)
                try:
                    RequestBuilder("https://x").json("{}").build()
                except ValueError as e:
                    print("ValueError:", e)
            '''),
            "For simple cases Python's keyword arguments with defaults already do most of a builder's job. Reach for a builder when construction has ordering, cross-field validation, or many steps that read better as a chain.",
        ),
        section(
            "Prototype: copy a configured object",
            "When building an object from scratch is expensive or fiddly (loaded from disk, many settings), keep a configured <em>prototype</em> and clone it. In Python that is <code>copy.deepcopy</code>, plus a <code>__deepcopy__</code> hook if some members (connections, caches) must be shared or reset rather than copied.",
            code('''
                import copy

                class Document:
                    def __init__(self, template_name):
                        print(f"  (expensive) loading template {template_name}")
                        self.styles = {"font": "Inter", "size": 11}
                        self.sections = ["header", "body", "footer"]

                registry = {"invoice": Document("invoice"), "letter": Document("letter")}

                def new_document(kind, **style):
                    doc = copy.deepcopy(registry[kind])      # no reload
                    doc.styles.update(style)
                    return doc

                a = new_document("invoice", size=14)
                b = new_document("invoice")
                print(a.styles, b.styles, a.sections is b.sections)
            '''),
        ),
        section(
            "Singleton: one shared instance",
            "A singleton guarantees one instance with global access: configuration, a registry, a connection manager. The textbook implementation overrides <code>__new__</code>. In Python, a module is already a singleton (it is created once and cached in <code>sys.modules</code>), so a module-level instance is usually the simpler answer.",
            code('''
                import threading

                class Config:
                    _instance = None
                    _lock = threading.Lock()

                    def __new__(cls):
                        if cls._instance is None:
                            with cls._lock:                       # double-checked for threads
                                if cls._instance is None:
                                    inst = super().__new__(cls)
                                    inst.settings = {"env": "prod"}
                                    cls._instance = inst
                        return cls._instance

                instances = []
                threads = [threading.Thread(target=lambda: instances.append(Config())) for _ in range(20)]
                for t in threads: t.start()
                for t in threads: t.join()
                print("distinct instances:", len({id(i) for i in instances}))
                Config().settings["env"] = "staging"
                print(Config().settings)
            '''),
            caveat("Singletons are global state in disguise: they make tests depend on each other and hide dependencies. Prefer creating one instance at start-up and passing it to whoever needs it. Use a true singleton only for things that are genuinely process-wide, and never for anything a test would want to replace."),
        ),
        section(
            "Object pool: reuse expensive objects",
            "Database connections, threads and large buffers are expensive to create. A pool creates a bounded number, lends them out, and takes them back. A context manager guarantees return even when the borrower raises.",
            code('''
                import queue
                from contextlib import contextmanager

                class Connection:
                    created = 0
                    def __init__(self):
                        Connection.created += 1
                        self.id = Connection.created
                    def query(self, sql):
                        return f"conn{self.id}: {sql}"

                class Pool:
                    def __init__(self, size):
                        self._free = queue.Queue()
                        for _ in range(size):
                            self._free.put(Connection())

                    @contextmanager
                    def connection(self, timeout=1.0):
                        conn = self._free.get(timeout=timeout)    # blocks when exhausted
                        try:
                            yield conn
                        finally:
                            self._free.put(conn)                  # always returned

                pool = Pool(2)
                results = []
                for i in range(5):
                    with pool.connection() as c:
                        results.append(c.query(f"select {i}"))
                try:
                    with pool.connection() as c:
                        raise RuntimeError("query failed")
                except RuntimeError:
                    pass
                print(results)
                print("connections ever created:", Connection.created, "| free now:", pool._free.qsize())
            '''),
        ),
    ],
    questions=[
        question(
            "Factory method vs abstract factory vs builder: how do you tell which one a problem needs?",
            "medium",
            "Factory: the question is <em>which class</em> to create from some input, one object at a time. Abstract factory: you create <em>several related objects</em> that must come from the same family, and the family is chosen once. Builder: the question is <em>how</em> to assemble one complex object with many optional parts and validation. They combine: an abstract factory's methods are often factory methods, and a factory may use a builder internally.",
        ),
        question(
            "Why is Singleton often called an anti-pattern, and when is it acceptable?",
            "medium",
            "It is global mutable state: any code can reach it, so dependencies are hidden; tests leak state into each other and cannot substitute a fake; and it makes concurrency harder. It is acceptable for things that are truly one-per-process and stateless or read-only after start-up (a logger configuration, a metrics registry), and even then a module-level object created at import time is the Pythonic way. For anything with behaviour you want to test, create one instance in the composition root and inject it.",
        ),
        question(
            "Write a thread-safe lazily-initialised singleton. Is the lock needed in CPython?",
            "hard",
            "Yes. The check <code>if cls._instance is None</code> and the assignment are separate bytecode steps, and a thread switch between them lets two threads both create an instance, with one silently lost. The double-checked lock above takes the lock only on the slow path. A module-level instance avoids writing this by hand, because module import is protected by the import lock. <code>functools.cache</code> on a factory function is a neat lazy version for single-threaded start-up, but it does not lock: two threads racing on the first call can both run the factory.",
            code('''
                from functools import cache

                @cache
                def get_settings():
                    print("  loading settings once")
                    return {"region": "ap-south-1"}

                print(get_settings() is get_settings())
            '''),
        ),
    ],
    refs=[
        ("Refactoring.Guru: Creational patterns", "https://refactoring.guru/design-patterns/creational-patterns"),
        ("python-patterns.guide: The Singleton pattern", "https://python-patterns.guide/gang-of-four/singleton/"),
        ("Python docs: __init_subclass__", "https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__"),
    ],
)
