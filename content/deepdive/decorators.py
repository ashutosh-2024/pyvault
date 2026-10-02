from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="decorators",
    title="Decorators",
    intro=[
        "<code>@decorator</code> above a <code>def</code> is one line of syntax sugar: <code>func = decorator(func)</code>. That is all the language does. What makes decorators powerful is everything that single call can do &mdash; wrap the function, replace it, register it, attach data to it, or turn it into a completely different kind of object such as a <code>property</code>.",
        "This page goes from the rebinding rule to closures, <code>functools.wraps</code>, decorators with arguments, stacking order, class-based decorators and the descriptor bug they hit on methods, class decorators, and the standard-library decorators worth knowing cold.",
    ],
    sections=[
        section(
            "The one rule: decoration is rebinding, at definition time",
            "A decorator is any callable that takes the object being defined and returns something. The name is then bound to whatever it returned. It runs <em>once</em>, when the <code>def</code> executes &mdash; usually at import &mdash; not on every call.",
            code('''
                def announce(func):
                    print(f"decorating {func.__name__}")
                    return func

                @announce
                def greet():
                    return "hi"

                # exactly the same as:
                def wave():
                    return "o/"
                wave = announce(wave)

                print("--- now calling ---")
                print(greet(), wave())
            '''),
            "Because the result replaces the name, a decorator can return something that is not a function at all:",
            code('''
                def run_now(func):
                    return func()

                @run_now
                def config():
                    return {"debug": True}

                print(config)            # the name now holds the return value
            '''),
        ),
        section(
            "Wrapping: closures and functools.wraps",
            "Most decorators return a new function that calls the original. The wrapper reaches the original through a closure, and accepts <code>*args, **kwargs</code> so it fits any signature.",
            code('''
                import functools, time

                def timed(func):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        start = time.perf_counter()
                        try:
                            return func(*args, **kwargs)
                        finally:
                            elapsed = time.perf_counter() - start
                            print(f"{func.__name__} took under 1s: {elapsed < 1}")
                    return wrapper

                @timed
                def add(a, b):
                    """Add two numbers."""
                    return a + b

                print(add(2, 3))
                print(add.__name__, "|", add.__doc__, "|", add.__wrapped__)
            '''),
            "Without <code>functools.wraps</code> the decorated function would report the wrapper&rsquo;s name and docstring. That breaks logs, <code>help()</code>, test runners, web frameworks that route by function name, and pickling. <code>wraps</code> copies <code>__name__</code>, <code>__qualname__</code>, <code>__doc__</code>, <code>__module__</code>, <code>__dict__</code> and annotations, and sets <code>__wrapped__</code> so <code>inspect.signature</code> shows the real parameters.",
            code('''
                import functools, inspect

                def bare(func):
                    def wrapper(*args, **kwargs):
                        return func(*args, **kwargs)
                    return wrapper

                def wrapped(func):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        return func(*args, **kwargs)
                    return wrapper

                def area(width: float, height: float = 1.0) -> float:
                    return width * height

                for deco in (bare, wrapped):
                    f = deco(area)
                    print(f"{deco.__name__:8} name={f.__name__:8} signature={inspect.signature(f)}")
            ''', label="what tools see, with and without wraps"),
            note("Put <code>@functools.wraps(func)</code> on every wrapper you write. There is no situation where leaving it off is better."),
        ),
        section(
            "Decorators that take arguments",
            "<code>@retry(times=3)</code> first <em>calls</em> <code>retry(times=3)</code>, and the result of that call is the decorator. So a configurable decorator is three nested functions: the factory taking the options, the decorator taking the function, and the wrapper taking the call&rsquo;s arguments.",
            code('''
                import functools

                def retry(times=3, exceptions=(Exception,)):
                    def decorator(func):
                        @functools.wraps(func)
                        def wrapper(*args, **kwargs):
                            for attempt in range(1, times + 1):
                                try:
                                    return func(*args, **kwargs)
                                except exceptions as e:
                                    print(f"  attempt {attempt} failed: {e}")
                                    if attempt == times:
                                        raise
                        return wrapper
                    return decorator

                calls = {"n": 0}

                @retry(times=4, exceptions=(ConnectionError,))
                def flaky():
                    calls["n"] += 1
                    if calls["n"] < 3:
                        raise ConnectionError("timeout")
                    return "connected"

                print(flaky())
            '''),
            table(
                ["Layer", "Called when", "Receives", "Returns"],
                [
                    ["<code>retry(...)</code>", "The <code>@</code> line is evaluated", "Options", "The decorator"],
                    ["<code>decorator(func)</code>", "Right after, at definition time", "The function", "The wrapper"],
                    ["<code>wrapper(*args)</code>", "Every call", "The call&rsquo;s arguments", "The result"],
                ],
            ),
        ),
        section(
            "Stacking order",
            "Stacked decorators are applied bottom-up &mdash; the one closest to <code>def</code> wraps first &mdash; so the top one ends up outermost and runs first on each call.",
            code('''
                import functools

                def tag(name):
                    def decorator(func):
                        print(f"applying {name}")
                        @functools.wraps(func)
                        def wrapper(*a, **k):
                            print(f"  enter {name}")
                            result = func(*a, **k)
                            print(f"  exit  {name}")
                            return result
                        return wrapper
                    return decorator

                @tag("outer")
                @tag("inner")
                def work():
                    print("  work")

                print("--- call ---")
                work()
            '''),
            "This matters in real code. <code>@app.route</code> must be on top so the framework registers the fully decorated function; <code>@login_required</code> placed <em>above</em> the route decorator would never run, because the router already holds a reference to the undecorated inner function. Similarly <code>@classmethod</code> and <code>@staticmethod</code> go on top of other decorators, since they produce descriptors rather than plain functions.",
        ),
        section(
            "Stateful decorators: function attributes and classes",
            "A decorator often needs state that survives between calls &mdash; a counter, a cache, a rate-limit window. Either keep it in the closure and expose it as an attribute of the wrapper, or write the decorator as a class with <code>__call__</code>.",
            code('''
                import functools

                def count_calls(func):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        wrapper.calls += 1
                        return func(*args, **kwargs)
                    wrapper.calls = 0
                    return wrapper

                class CountCalls:
                    def __init__(self, func):
                        functools.update_wrapper(self, func)
                        self.func = func
                        self.calls = 0
                    def __call__(self, *args, **kwargs):
                        self.calls += 1
                        return self.func(*args, **kwargs)

                @count_calls
                def ping(): return "pong"

                @CountCalls
                def pong(): return "ping"

                ping(); ping(); pong()
                print(ping.calls, pong.calls, pong.__name__)
            '''),
            "The class-based version reads well but hides a trap: put it on a <em>method</em> and <code>self</code> goes missing.",
            code('''
                import functools

                class CountCalls:
                    def __init__(self, func):
                        functools.update_wrapper(self, func)
                        self.func, self.calls = func, 0
                    def __call__(self, *args, **kwargs):
                        self.calls += 1
                        return self.func(*args, **kwargs)

                class Service:
                    @CountCalls
                    def status(self):
                        return "up"

                Service().status()
            ''', raises=True, label="the bug"),
            "Functions become methods because they are descriptors (<code>__get__</code> binds <code>self</code>). An instance of <code>CountCalls</code> is not, so <code>Service().status</code> returns the <code>CountCalls</code> object unbound and <code>self</code> is never passed. Adding <code>__get__</code> fixes it:",
            code('''
                import functools, types

                class CountCalls:
                    def __init__(self, func):
                        functools.update_wrapper(self, func)
                        self.func, self.calls = func, 0
                    def __call__(self, *args, **kwargs):
                        self.calls += 1
                        return self.func(*args, **kwargs)
                    def __get__(self, obj, objtype=None):
                        if obj is None:
                            return self
                        return types.MethodType(self, obj)      # bind like a function would

                class Service:
                    @CountCalls
                    def status(self):
                        return "up"

                s = Service()
                print(s.status(), s.status(), Service.status.calls)
            ''', label="the fix"),
        ),
        section(
            "Class decorators",
            "A decorator on a <code>class</code> receives the finished class. It can add methods, register the class, or check it &mdash; a lighter alternative to a metaclass that affects only the class it is written on.",
            code('''
                def auto_repr(cls):
                    fields = list(cls.__init__.__code__.co_varnames[1:cls.__init__.__code__.co_argcount])
                    def __repr__(self):
                        args = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
                        return f"{cls.__name__}({args})"
                    cls.__repr__ = __repr__
                    return cls

                @auto_repr
                class User:
                    def __init__(self, name, age):
                        self.name, self.age = name, age

                print(User("ann", 31))
            '''),
            "<code>@dataclass</code> is the famous one: it reads the class&rsquo;s annotations and generates <code>__init__</code>, <code>__repr__</code> and <code>__eq__</code> (and more, on request). <code>@functools.total_ordering</code> fills in the missing comparison methods from <code>__eq__</code> plus one of <code>__lt__</code>/<code>__gt__</code>.",
            code('''
                from dataclasses import dataclass, field
                from functools import total_ordering

                @dataclass(order=True)
                class Version:
                    major: int
                    minor: int = 0
                    tags: list = field(default_factory=list, compare=False)

                print(Version(1, 2), Version(1, 2) < Version(1, 10))

                @total_ordering
                class Money:
                    def __init__(self, cents): self.cents = cents
                    def __eq__(self, o): return self.cents == o.cents
                    def __lt__(self, o): return self.cents < o.cents

                print(Money(5) >= Money(3), Money(5) <= Money(3))
            '''),
        ),
        section(
            "Standard-library decorators worth knowing",
            table(
                ["Decorator", "What it does", "Watch out for"],
                [
                    ["<code>@functools.cache</code> / <code>@lru_cache(maxsize=n)</code>", "Memoizes by arguments", "Arguments must be hashable; on methods it keeps every <code>self</code> alive"],
                    ["<code>@functools.cached_property</code>", "Compute once per instance, store on the instance", "Needs <code>__dict__</code>; not thread-locked since 3.12"],
                    ["<code>@functools.singledispatch</code>", "Overload a function on its first argument&rsquo;s type", "Dispatches on the first argument only; use <code>singledispatchmethod</code> in classes"],
                    ["<code>@contextlib.contextmanager</code>", "Turn a generator into a <code>with</code>-able object", "Wrap the <code>yield</code> in <code>try/finally</code>"],
                    ["<code>@property</code>, <code>@classmethod</code>, <code>@staticmethod</code>", "Build descriptors", "Keep them outermost when stacking"],
                    ["<code>@typing.override</code>, <code>@typing.final</code>", "Mark intent for type checkers (3.12+ for <code>override</code>)", "No run-time effect beyond setting an attribute"],
                ],
            ),
            code('''
                from functools import cache, singledispatch

                @cache
                def fib(n):
                    return n if n < 2 else fib(n - 1) + fib(n - 2)

                print(fib(80), fib.cache_info().hits)

                @singledispatch
                def describe(x):
                    return f"something: {x!r}"

                @describe.register
                def _(x: int):
                    return f"an int, doubled {x * 2}"

                @describe.register
                def _(x: list):
                    return f"a list of {len(x)}"

                print(describe(21), "|", describe([1, 2]), "|", describe(2.5))
            '''),
        ),
    ],
    questions=[
        question(
            "Write a decorator that works both as <code>@log</code> and as <code>@log(level=&quot;debug&quot;)</code>.",
            "hard",
            "The two forms call the decorator differently: bare <code>@log</code> passes the function as the first positional argument; <code>@log(...)</code> passes only keywords and expects a decorator back. Make the function the optional first positional parameter and the options keyword-only, then branch on whether it was given.",
            code('''
                import functools

                def log(func=None, *, level="info"):
                    if func is None:                       # called as @log(...)
                        return functools.partial(log, level=level)

                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        print(f"[{level}] {func.__name__}{args}")
                        return func(*args, **kwargs)
                    return wrapper

                @log
                def a(x): return x

                @log(level="debug")
                def b(x): return x

                a(1); b(2)
            '''),
            "The keyword-only <code>*</code> is what makes it safe: without it, <code>@log(&quot;debug&quot;)</code> would pass a string as <code>func</code> and try to wrap it.",
        ),
        question(
            "What does <code>functools.wraps</code> do, and what breaks without it?",
            "medium",
            "It copies the wrapped function&rsquo;s metadata &mdash; <code>__name__</code>, <code>__qualname__</code>, <code>__doc__</code>, <code>__module__</code>, <code>__annotations__</code>, and <code>__dict__</code> &mdash; onto the wrapper, and sets <code>wrapper.__wrapped__ = func</code>.",
            "Without it: every decorated function is called <code>wrapper</code> in tracebacks and logs; <code>help()</code> shows no docstring; <code>inspect.signature</code> shows <code>(*args, **kwargs)</code>, which breaks frameworks that inspect parameters (FastAPI, pytest fixtures, Click); two decorated view functions can collide in a router that keys on <code>__name__</code>; and <code>pickle</code> cannot find the function by name. <code>__wrapped__</code> also lets you reach the original, e.g. to test it without the decorator.",
        ),
        question(
            "What does this print, and in what order?",
            "medium",
            code('''
                def a(f):
                    print("a applied")
                    return lambda: "a(" + f() + ")"

                def b(f):
                    print("b applied")
                    return lambda: "b(" + f() + ")"

                @a
                @b
                def core():
                    return "core"

                print(core())
            '''),
            "Decorators apply bottom-up at definition time, so <code>b</code> runs first, then <code>a</code> wraps <code>b</code>&rsquo;s result: <code>core = a(b(core))</code>. At call time the outermost wrapper runs first, which is why <code>a</code>&rsquo;s text is on the outside.",
        ),
        question(
            "Implement <code>@rate_limit(calls, per_seconds)</code> that raises if called too often.",
            "hard",
            "Keep a sliding window of recent call times in the closure. A <code>deque</code> makes dropping old timestamps cheap. Taking the clock as a parameter makes it testable without sleeping.",
            code('''
                import functools, time
                from collections import deque

                class RateLimited(Exception):
                    pass

                def rate_limit(calls, per_seconds, clock=time.monotonic):
                    def decorator(func):
                        recent = deque()
                        @functools.wraps(func)
                        def wrapper(*args, **kwargs):
                            now = clock()
                            while recent and now - recent[0] >= per_seconds:
                                recent.popleft()
                            if len(recent) >= calls:
                                raise RateLimited(f"{func.__name__}: max {calls} per {per_seconds}s")
                            recent.append(now)
                            return func(*args, **kwargs)
                        return wrapper
                    return decorator

                fake_now = [0.0]

                @rate_limit(2, per_seconds=10, clock=lambda: fake_now[0])
                def send(msg): return f"sent {msg}"

                print(send("a"), send("b"))
                try:
                    send("c")
                except RateLimited as e:
                    print("RateLimited:", e)
                fake_now[0] = 10.5
                print(send("d"))
            '''),
            "Follow-ups to expect: make it thread-safe (guard the deque with a <code>threading.Lock</code>), make it per-user (a dict of deques keyed by an argument), or make it block instead of raise (sleep until <code>recent[0] + per_seconds</code>).",
        ),
        question(
            "Why does a class-based decorator break when applied to a method, and how do you fix it?",
            "hard",
            "Methods get <code>self</code> because functions are descriptors: accessing a function through an instance calls <code>function.__get__</code>, which returns a bound method. When a decorator replaces the function with an instance of a class that has <code>__call__</code> but no <code>__get__</code>, attribute access returns that object unchanged, so the call arrives without <code>self</code> and fails with a missing-argument <code>TypeError</code>.",
            "The fix is to implement <code>__get__</code> and return <code>types.MethodType(self, obj)</code> (or <code>functools.partial(self.__call__, obj)</code>). The simpler alternative is to write the decorator as a function returning a closure, which is a real function and binds automatically.",
        ),
        question(
            "<code>@lru_cache</code> raises <code>TypeError: unhashable type: 'list'</code>. Why, and what are your options?",
            "medium",
            "<code>lru_cache</code> builds a dict key from the call&rsquo;s arguments, so every argument must be hashable. A list is mutable &mdash; if it could be a key, mutating it after caching would silently return a stale result.",
            code('''
                from functools import lru_cache

                @lru_cache
                def total(values):
                    return sum(values)

                print(total((1, 2, 3)))          # tuple: fine
                try:
                    total([1, 2, 3])
                except TypeError as e:
                    print("TypeError:", e)
                print(total.cache_info())
            '''),
            "Options: have callers pass tuples or frozensets; add a thin wrapper that converts <code>tuple(values)</code> before calling the cached function; or key the cache on something that identifies the data (an ID or version number) rather than the data itself.",
        ),
    ],
    refs=[
        ("PEP 318 — Decorators for functions and methods", "https://peps.python.org/pep-0318/"),
        ("PEP 3129 — Class decorators", "https://peps.python.org/pep-3129/"),
        ("Python docs: functools", "https://docs.python.org/3/library/functools.html"),
    ],
)
