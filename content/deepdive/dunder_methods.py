from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="dunder-methods",
    title="Magic (Dunder) Methods",
    intro=[
        "Methods whose names start and end with a double underscore &mdash; <code>__init__</code>, <code>__len__</code>, <code>__add__</code> &mdash; are called <em>special</em>, <em>magic</em> or <em>dunder</em> methods. You rarely call them yourself. Python calls them for you when you use syntax or a built-in: <code>a + b</code>, <code>len(x)</code>, <code>x[i]</code>, <code>for v in x</code>, <code>with x:</code>, <code>f\"{x}\"</code>.",
        "Together they are Python&rsquo;s <em>data model</em>: the protocol a class implements to plug into the language. A class that defines the right handful of dunders behaves like a built-in type, works with the standard library, and needs no special API of its own. This topic walks through the families of dunders, what each one is for, and the rules that are easy to get wrong.",
    ],
    sections=[
        section(
            "The mapping from syntax to dunder",
            "Every operator and many built-ins translate to a method call on the <em>type</em> of the object. Knowing the translation is most of the topic:",
            table(
                ["You write", "Python calls", "Family"],
                [
                    ["<code>C(a)</code>", "<code>C.__new__(C, a)</code>, then <code>obj.__init__(a)</code>", "Lifecycle"],
                    ["<code>repr(x)</code>, <code>str(x)</code>, <code>f\"{x:spec}\"</code>", "<code>__repr__</code>, <code>__str__</code>, <code>__format__</code>", "Representation"],
                    ["<code>a == b</code>, <code>a &lt; b</code>", "<code>__eq__</code>, <code>__lt__</code> (and friends)", "Comparison"],
                    ["<code>hash(x)</code>, <code>bool(x)</code>", "<code>__hash__</code>, <code>__bool__</code> (fallback <code>__len__</code>)", "Hashing / truth"],
                    ["<code>a + b</code>, <code>a += b</code>, <code>-a</code>", "<code>__add__</code>/<code>__radd__</code>, <code>__iadd__</code>, <code>__neg__</code>", "Arithmetic"],
                    ["<code>len(x)</code>, <code>x[k]</code>, <code>k in x</code>", "<code>__len__</code>, <code>__getitem__</code>, <code>__contains__</code>", "Containers"],
                    ["<code>for v in x</code>, <code>next(it)</code>", "<code>__iter__</code>, <code>__next__</code>", "Iteration"],
                    ["<code>x.attr</code>, <code>x.attr = v</code>", "<code>__getattribute__</code>/<code>__getattr__</code>, <code>__setattr__</code>", "Attribute access"],
                    ["<code>x(...)</code>", "<code>__call__</code>", "Callables"],
                    ["<code>with x:</code>", "<code>__enter__</code>, <code>__exit__</code>", "Context managers"],
                    ["<code>int(x)</code>, <code>round(x)</code>, <code>seq[x]</code>", "<code>__int__</code>, <code>__round__</code>, <code>__index__</code>", "Conversion"],
                ],
            ),
            "The lookup happens on the type, not the instance: <code>len(x)</code> is effectively <code>type(x).__len__(x)</code>. The object model topic shows why assigning <code>x.__len__ = ...</code> on an instance has no effect on <code>len(x)</code>.",
            note("Only implement dunders Python already defines. Inventing your own <code>__names__</code> is reserved for the language and may collide with a future version."),
        ),
        section(
            "Lifecycle: __new__, __init__, __del__",
            "Calling a class runs two steps. <code>__new__</code> is a static method that <em>creates</em> and returns the object; <code>__init__</code> then <em>initialises</em> the object it was given and must return <code>None</code>. Almost every class only needs <code>__init__</code>. You need <code>__new__</code> when the object must be decided before it exists &mdash; subclassing an immutable type, caching instances, or returning a different object altogether.",
            code('''
                class Trace:
                    def __new__(cls, *args):
                        print(f"__new__  cls={cls.__name__} args={args}")
                        return super().__new__(cls)
                    def __init__(self, value):
                        print(f"__init__ value={value}")
                        self.value = value

                t = Trace(7)
                print(t.value)
            '''),
            "Immutable built-ins like <code>int</code>, <code>str</code> and <code>tuple</code> have their value fixed by the time <code>__init__</code> runs, so a subclass that wants to change the value must do it in <code>__new__</code>:",
            code('''
                class Celsius(float):
                    def __new__(cls, value):
                        if value < -273.15:
                            raise ValueError("below absolute zero")
                        return super().__new__(cls, round(value, 1))

                    def __repr__(self):
                        return f"{float(self)}°C"

                print(Celsius(21.456), Celsius(21.456) + 1)
                try:
                    Celsius(-300)
                except ValueError as e:
                    print("ValueError:", e)
            '''),
            "If <code>__new__</code> returns something that is not an instance of the class, <code>__init__</code> is skipped. That is how an instance cache works:",
            code('''
                class Color:
                    _cache = {}
                    def __new__(cls, name):
                        if name not in cls._cache:
                            obj = super().__new__(cls)
                            obj.name = name
                            cls._cache[name] = obj
                        return cls._cache[name]

                print(Color("red") is Color("red"), Color("red") is Color("blue"))
            '''),
            "<code>__del__</code> runs when the object is about to be destroyed. In CPython that is usually when the reference count hits zero, but it is not guaranteed to run promptly (reference cycles) or at all (interpreter shutdown), and exceptions raised inside it are only printed as warnings.",
            code('''
                class Resource:
                    def __init__(self, name):
                        self.name = name
                    def __del__(self):
                        print(f"__del__ {self.name}")

                r = Resource("a")
                del r                     # refcount hits zero: runs now in CPython
                print("after del")
            '''),
            caveat("Do not use <code>__del__</code> for cleanup that must happen. Use a context manager (<code>__enter__</code>/<code>__exit__</code>) or <code>weakref.finalize</code>."),
        ),
        section(
            "Representation: __repr__, __str__, __format__",
            "<code>__repr__</code> is for developers: unambiguous, ideally valid Python that recreates the object. It is what the REPL, debuggers, logs and containers show. <code>__str__</code> is for end users; if a class does not define it, <code>str()</code> falls back to <code>__repr__</code>. <code>__format__</code> handles the part after the colon in an f-string.",
            code('''
                class Money:
                    def __init__(self, amount, currency="USD"):
                        self.amount, self.currency = amount, currency

                    def __repr__(self):
                        return f"Money({self.amount!r}, {self.currency!r})"

                    def __str__(self):
                        return f"{self.amount:,.2f} {self.currency}"

                    def __format__(self, spec):
                        if spec == "short":
                            return f"{self.amount:.0f}{self.currency[0]}"
                        return format(str(self), spec)

                m = Money(1234.5)
                print(repr(m))
                print(str(m))
                print([m])                    # containers use repr of their items
                print(f"{m}|{m!r}|{m:short}|{m:>16}|")
            '''),
            table(
                ["Method", "Called by", "Audience", "Default"],
                [
                    ["<code>__repr__</code>", "<code>repr()</code>, REPL, containers, <code>!r</code>", "Developers", "<code>&lt;Money object at 0x...&gt;</code>"],
                    ["<code>__str__</code>", "<code>str()</code>, <code>print()</code>, <code>f\"{x}\"</code>", "Users", "Falls back to <code>__repr__</code>"],
                    ["<code>__format__</code>", "<code>format()</code>, <code>f\"{x:spec}\"</code>", "Users", "<code>str(self)</code>, only an empty spec allowed"],
                    ["<code>__bytes__</code>", "<code>bytes(x)</code>", "Wire formats", "<code>TypeError</code>"],
                ],
            ),
            note("If you define only one, define <code>__repr__</code>. You get a useful <code>str()</code> for free."),
        ),
        section(
            "Comparison and NotImplemented",
            "The six rich comparison methods are <code>__eq__</code>, <code>__ne__</code>, <code>__lt__</code>, <code>__le__</code>, <code>__gt__</code>, <code>__ge__</code>. When a method does not know how to compare with the other operand it should <em>return</em> <code>NotImplemented</code> (not raise). Python then tries the reflected method on the other object: <code>a &lt; b</code> falls back to <code>b &gt; a</code>, and <code>a == b</code> to <code>b == a</code>. If both give up, <code>==</code> falls back to identity and ordering raises <code>TypeError</code>.",
            code('''
                class Version:
                    def __init__(self, text):
                        self.parts = tuple(int(p) for p in text.split("."))
                    def __repr__(self):
                        return "Version(%r)" % ".".join(map(str, self.parts))
                    def __eq__(self, other):
                        if not isinstance(other, Version):
                            return NotImplemented
                        return self.parts == other.parts
                    def __lt__(self, other):
                        if not isinstance(other, Version):
                            return NotImplemented
                        return self.parts < other.parts

                a, b = Version("1.10.0"), Version("1.9.3")
                print(a == Version("1.10.0"), a != b)   # __ne__ is derived from __eq__
                print(a < b, a > b)                     # a > b becomes b < a
                print(sorted([a, b, Version("0.1")]))
                print(a == "1.10.0")                    # both sides give up -> identity
                try:
                    a <= b                              # no __le__ or __ge__ anywhere
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "Writing all six is tedious. <code>functools.total_ordering</code> fills in the missing ones from <code>__eq__</code> plus one ordering method. <code>@dataclass(order=True)</code> generates all of them by comparing fields as a tuple.",
            code('''
                from functools import total_ordering

                @total_ordering
                class Grade:
                    order = "FDCBA"
                    def __init__(self, letter):
                        self.letter = letter
                    def __eq__(self, other):
                        return self.letter == other.letter
                    def __lt__(self, other):
                        return self.order.index(self.letter) < self.order.index(other.letter)

                a, c = Grade("A"), Grade("C")
                print(a > c, a >= c, c <= a, max([c, a, Grade("B")]).letter)
            '''),
        ),
        section(
            "Hashing and truthiness: __hash__, __bool__",
            "<code>__hash__</code> must return an int, and objects that compare equal must hash equal. Defining <code>__eq__</code> without <code>__hash__</code> sets <code>__hash__</code> to <code>None</code>, making instances unhashable. Hash the same fields you compare, and only if those fields never change.",
            code('''
                class Point:
                    __slots__ = ("x", "y")
                    def __init__(self, x, y):
                        self.x, self.y = x, y
                    def __eq__(self, other):
                        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)
                    def __hash__(self):
                        return hash((self.x, self.y))      # delegate to a tuple

                seen = {Point(1, 2), Point(1, 2), Point(3, 4)}
                print(len(seen), Point(1, 2) in seen)
            '''),
            "<code>bool(x)</code> (and every <code>if x:</code>) calls <code>__bool__</code>. If that is missing it uses <code>__len__</code> and treats zero as false. If both are missing, every instance is truthy.",
            code('''
                class Plain: pass

                class Basket:
                    def __init__(self, *items): self.items = list(items)
                    def __len__(self): return len(self.items)

                class Account:
                    def __init__(self, balance): self.balance = balance
                    def __bool__(self): return self.balance > 0

                print(bool(Plain()), bool(Basket()), bool(Basket("egg")))
                print(bool(Account(0)), bool(Account(5)))
                print("empty" if not Basket() else "has items")
            '''),
        ),
        section(
            "Arithmetic: forward, reflected and in-place",
            "Each binary operator has three dunders. For <code>+</code>: <code>__add__</code> for <code>a + b</code>, <code>__radd__</code> (reflected) when the left operand gives up, and <code>__iadd__</code> for <code>a += b</code>. The rule for <code>a + b</code> is:",
            "1. Call <code>a.__add__(b)</code>. If it returns <code>NotImplemented</code>&hellip;<br>2. call <code>b.__radd__(a)</code>. If that also returns <code>NotImplemented</code>, raise <code>TypeError</code>.<br>Exception: if <code>b</code>&rsquo;s type is a <em>subclass</em> of <code>a</code>&rsquo;s type and overrides the reflected method, <code>b.__radd__</code> is tried first.",
            code('''
                class Vector:
                    def __init__(self, *xs):
                        self.xs = tuple(xs)
                    def __repr__(self):
                        return f"Vector{self.xs}"

                    def __add__(self, other):
                        if isinstance(other, Vector):
                            return Vector(*(a + b for a, b in zip(self.xs, other.xs)))
                        return NotImplemented

                    def __mul__(self, k):
                        if isinstance(k, (int, float)):
                            return Vector(*(a * k for a in self.xs))
                        return NotImplemented
                    __rmul__ = __mul__                    # k * v is the same as v * k

                    def __matmul__(self, other):          # the @ operator: dot product
                        return sum(a * b for a, b in zip(self.xs, other.xs))

                    def __neg__(self):
                        return self * -1
                    def __abs__(self):
                        return sum(a * a for a in self.xs) ** 0.5

                v, w = Vector(3, 4), Vector(1, 1)
                print(v + w, v * 2, 2 * v, -v)
                print(v @ w, abs(v))
                try:
                    v + 1
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "Reflected methods are what let your type sit on the <em>right</em> of a built-in. <code>sum()</code> starts from <code>0</code>, so <code>0 + first_item</code> needs <code>__radd__</code>:",
            code('''
                class Cents:
                    def __init__(self, n): self.n = n
                    def __repr__(self): return f"Cents({self.n})"
                    def __add__(self, other):
                        if isinstance(other, Cents):
                            return Cents(self.n + other.n)
                        if isinstance(other, int):
                            return Cents(self.n + other)
                        return NotImplemented
                    __radd__ = __add__

                print(sum([Cents(5), Cents(10), Cents(20)]))
            '''),
            "In-place operators mutate when they can. If <code>__iadd__</code> is missing, <code>a += b</code> becomes <code>a = a + b</code> and rebinds the name to a new object. That is why <code>+=</code> changes a list in place but builds a new tuple:",
            code('''
                class Bag:
                    def __init__(self): self.items = []
                    def __iadd__(self, item):
                        self.items.append(item)
                        return self                      # must return the result

                b = Bag(); before = id(b)
                b += "apple"; b += "pear"
                print(b.items, id(b) == before)

                nums, tup = [1], (1,)
                n_id, t_id = id(nums), id(tup)
                nums += [2]; tup += (2,)
                print(id(nums) == n_id, id(tup) == t_id)
            '''),
            table(
                ["Operator", "Forward", "Reflected", "In-place"],
                [
                    ["<code>+</code> <code>-</code> <code>*</code> <code>@</code>", "<code>__add__ __sub__ __mul__ __matmul__</code>", "<code>__radd__</code> &hellip;", "<code>__iadd__</code> &hellip;"],
                    ["<code>/</code> <code>//</code> <code>%</code> <code>**</code>", "<code>__truediv__ __floordiv__ __mod__ __pow__</code>", "<code>__rtruediv__</code> &hellip;", "<code>__itruediv__</code> &hellip;"],
                    ["<code>&lt;&lt;</code> <code>&gt;&gt;</code> <code>&amp;</code> <code>|</code> <code>^</code>", "<code>__lshift__ __rshift__ __and__ __or__ __xor__</code>", "<code>__rlshift__</code> &hellip;", "<code>__ilshift__</code> &hellip;"],
                    ["<code>divmod(a, b)</code>", "<code>__divmod__</code>", "<code>__rdivmod__</code>", "&mdash;"],
                    ["unary <code>-</code> <code>+</code> <code>~</code> <code>abs()</code>", "<code>__neg__ __pos__ __invert__ __abs__</code>", "&mdash;", "&mdash;"],
                ],
            ),
            note("Return <code>NotImplemented</code> for types you do not handle, never raise <code>TypeError</code> yourself &mdash; raising stops Python from giving the other operand its turn."),
        ),
        section(
            "Containers: __len__, __getitem__, __setitem__, __contains__",
            "A container protocol is a few dunders. <code>__getitem__</code> receives whatever is inside the brackets: an int, a key, or a <code>slice</code> object for <code>x[a:b:c]</code>. <code>__contains__</code> powers <code>in</code>; without it Python falls back to iterating.",
            code('''
                class Playlist:
                    def __init__(self, *songs):
                        self._songs = list(songs)
                    def __len__(self):
                        return len(self._songs)
                    def __getitem__(self, index):
                        if isinstance(index, slice):
                            return Playlist(*self._songs[index])
                        return self._songs[index]
                    def __setitem__(self, index, song):
                        self._songs[index] = song
                    def __delitem__(self, index):
                        del self._songs[index]
                    def __contains__(self, song):
                        return song.lower() in (s.lower() for s in self._songs)
                    def __repr__(self):
                        return f"Playlist{tuple(self._songs)}"

                p = Playlist("Intro", "Verse", "Chorus", "Outro")
                print(len(p), p[0], p[-1], p[1:3])
                p[0] = "Overture"; del p[-1]
                print(p, "chorus" in p)
                print(list(reversed(p)))       # works via __len__ + __getitem__
            '''),
            "Notice that <code>reversed()</code> and even <code>for</code> loops work without <code>__iter__</code> or <code>__reversed__</code>: Python falls back to calling <code>__getitem__</code> with 0, 1, 2&hellip; until <code>IndexError</code>. That is the <em>old sequence protocol</em>; define <code>__iter__</code> for anything new.",
            "Mappings get one extra hook. A <code>dict</code> subclass can define <code>__missing__</code>, which <code>d[key]</code> calls for absent keys. This is how <code>collections.defaultdict</code> and <code>Counter</code> work:",
            code('''
                class Inventory(dict):
                    def __missing__(self, key):
                        return 0                  # no KeyError, and nothing is stored

                stock = Inventory(apple=3)
                print(stock["apple"], stock["kiwi"], "kiwi" in stock)
                print(stock.get("kiwi"))          # .get() does not call __missing__
            '''),
        ),
        section(
            "Iteration: __iter__ and __next__",
            "An <strong>iterable</strong> has <code>__iter__</code>, which returns an <strong>iterator</strong>. An iterator has <code>__next__</code>, which returns the next value or raises <code>StopIteration</code>, and an <code>__iter__</code> that returns itself. A <code>for</code> loop is <code>it = iter(x)</code> followed by <code>next(it)</code> until <code>StopIteration</code>.",
            code('''
                class Countdown:                    # an iterator: single use
                    def __init__(self, start):
                        self.current = start
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.current <= 0:
                            raise StopIteration
                        self.current -= 1
                        return self.current + 1

                c = Countdown(3)
                print(list(c), list(c))             # exhausted after one pass
            '''),
            "Keep the iterable and the iterator separate so the object can be looped over more than once. Writing <code>__iter__</code> as a generator does exactly that with no <code>__next__</code> to maintain:",
            code('''
                class Range2D:                      # an iterable: reusable
                    def __init__(self, rows, cols):
                        self.rows, self.cols = rows, cols
                    def __iter__(self):
                        for r in range(self.rows):
                            for c in range(self.cols):
                                yield (r, c)
                    def __reversed__(self):
                        return reversed(list(self))

                grid = Range2D(2, 2)
                print(list(grid))
                print(list(grid))                   # a fresh generator each time
                print(list(reversed(grid))[:2])
            '''),
            note("Iterables return a <em>new</em> iterator from <code>__iter__</code>. Iterators return <code>self</code>. Mixing the two up is how you get a loop that silently runs zero times the second time."),
        ),
        section(
            "Attribute access: __getattr__, __getattribute__, __setattr__",
            "Four hooks sit around <code>.</code> lookups. <code>__getattribute__</code> is called for <em>every</em> read. <code>__getattr__</code> is called only when normal lookup failed, which makes it the safe one to override. <code>__setattr__</code> and <code>__delattr__</code> intercept every write and delete.",
            code('''
                class Settings:
                    def __init__(self, **values):
                        # bypass our own __setattr__ while building
                        object.__setattr__(self, "_values", values)

                    def __getattr__(self, name):         # only for missing names
                        try:
                            return self._values[name]
                        except KeyError:
                            raise AttributeError(name) from None

                    def __setattr__(self, name, value):
                        raise AttributeError(f"Settings are read-only: {name}")

                    def __dir__(self):
                        return list(self._values)

                s = Settings(debug=True, workers=4)
                print(s.debug, s.workers, dir(s))
                print(getattr(s, "timeout", 30))         # default works: AttributeError
                try:
                    s.debug = False
                except AttributeError as e:
                    print("AttributeError:", e)
            '''),
            "<code>__getattr__</code> must raise <code>AttributeError</code> for unknown names. Raising anything else breaks <code>getattr(obj, name, default)</code>, <code>hasattr</code> and copy/pickle, which all rely on that exception.",
            "A common real use is delegation: wrap an object and forward everything you do not override.",
            code('''
                class LoggingList:
                    def __init__(self):
                        self._inner = []
                    def append(self, item):
                        print(f"append({item!r})")
                        self._inner.append(item)
                    def __getattr__(self, name):         # everything else goes through
                        return getattr(self._inner, name)
                    def __len__(self):                   # dunders are NOT forwarded
                        return len(self._inner)

                log = LoggingList()
                log.append(3); log.append(1)
                log.sort()
                print(log._inner, log.index(3), len(log))
            '''),
            caveat("<code>__getattr__</code> does not catch implicit dunder lookups: <code>len(log)</code> goes straight to <code>type(log).__len__</code>. A proxy must define every dunder it wants to forward."),
            "Overriding <code>__getattribute__</code> is rarely needed and easy to break: any <code>self.x</code> inside it calls itself again. Always reach the real value through <code>super().__getattribute__</code>.",
            code('''
                class Audited:
                    def __init__(self):
                        self.a, self.b = 1, 2
                    def __getattribute__(self, name):
                        if not name.startswith("_"):
                            print(f"read {name}")
                        return super().__getattribute__(name)

                x = Audited()
                print(x.a + x.b)
            '''),
        ),
        section(
            "Callables and context managers",
            "<code>__call__</code> makes instances callable, which is useful for objects that behave like functions but carry configuration or state. <code>__enter__</code> and <code>__exit__</code> make an object usable in a <code>with</code> block; the context managers topic covers them in full.",
            code('''
                import time

                class Retry:
                    def __init__(self, times):
                        self.times = times
                    def __call__(self, fn, *args):
                        for attempt in range(1, self.times + 1):
                            try:
                                return fn(*args)
                            except ValueError as e:
                                print(f"attempt {attempt} failed: {e}")
                        raise RuntimeError("gave up")

                class Timer:
                    def __enter__(self):
                        self.start = time.perf_counter()
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        self.elapsed = time.perf_counter() - self.start
                        print(f"exit: exc_type={exc_type.__name__ if exc_type else None}")
                        return False                   # do not swallow exceptions

                calls = iter([ValueError("flaky"), ValueError("flaky"), "ok"])
                def flaky():
                    r = next(calls)
                    if isinstance(r, Exception):
                        raise r
                    return r

                with Timer() as t:
                    print(Retry(3)(flaky))
                print(t.elapsed < 1)
            '''),
        ),
        section(
            "Conversion: __int__, __float__, __index__, __round__",
            "Conversion built-ins each have a dunder. The subtle one is <code>__index__</code>: it says &ldquo;this object <em>is</em> an integer&rdquo;, not merely &ldquo;can be turned into one&rdquo;. Only <code>__index__</code> lets an object be used as a list index, a slice bound, or passed to <code>bin()</code>/<code>hex()</code>. <code>float</code> has <code>__int__</code> but no <code>__index__</code>, which is why <code>[1, 2][1.0]</code> is an error.",
            code('''
                import math

                class Fraction:
                    def __init__(self, num, den):
                        self.num, self.den = num, den
                    def __float__(self):
                        return self.num / self.den
                    def __int__(self):
                        return self.num // self.den
                    def __round__(self, ndigits=None):
                        return round(float(self), ndigits)
                    def __floor__(self):
                        return math.floor(self.num / self.den)
                    def __ceil__(self):
                        return math.ceil(self.num / self.den)

                class Slot:
                    def __init__(self, n): self.n = n
                    def __index__(self): return self.n

                f = Fraction(22, 7)
                print(float(f), int(f), round(f), round(f, 3), math.floor(f), math.ceil(f))
                print(["a", "b", "c"][Slot(2)], bin(Slot(5)), "xyz"[:Slot(2)])
                try:
                    ["a", "b"][f]
                except TypeError as e:
                    print("TypeError:", e)
            '''),
        ),
        section(
            "Class-level hooks: __init_subclass__, __class_getitem__, __set_name__",
            "Some dunders are called on classes rather than instances. <code>__init_subclass__</code> runs on the parent whenever a subclass is created &mdash; a lightweight alternative to a metaclass for registries and validation. <code>__class_getitem__</code> handles <code>Cls[...]</code>, which is how <code>list[int]</code> works. <code>__set_name__</code> tells a descriptor the attribute name it was assigned to.",
            code('''
                class Plugin:
                    registry = {}
                    def __init_subclass__(cls, name=None, **kwargs):
                        super().__init_subclass__(**kwargs)
                        Plugin.registry[name or cls.__name__.lower()] = cls

                class CSVExporter(Plugin, name="csv"): pass
                class JSONExporter(Plugin): pass
                print(Plugin.registry)

                class Box:
                    def __class_getitem__(cls, item):
                        return f"{cls.__name__} of {item.__name__}"
                print(Box[int], list[int])

                class Positive:
                    def __set_name__(self, owner, name):
                        self.name = "_" + name
                    def __get__(self, obj, owner):
                        return getattr(obj, self.name)
                    def __set__(self, obj, value):
                        if value <= 0:
                            raise ValueError(f"{self.name[1:]} must be positive")
                        setattr(obj, self.name, value)

                class Order:
                    qty = Positive()
                    def __init__(self, qty): self.qty = qty

                print(Order(3).qty)
                try:
                    Order(0)
                except ValueError as e:
                    print("ValueError:", e)
            '''),
            note("<code>__get__</code>, <code>__set__</code> and <code>__delete__</code> are the descriptor protocol &mdash; the next topic explains how they drive methods and <code>property</code>."),
        ),
        section(
            "Copying and pickling: __copy__, __deepcopy__, __reduce__",
            "<code>copy.copy</code> and <code>copy.deepcopy</code> work on most objects without help. Define <code>__copy__</code>/<code>__deepcopy__</code> when some state must not be duplicated &mdash; a cache, a lock, a connection &mdash; and <code>__getstate__</code>/<code>__setstate__</code> (or <code>__reduce__</code>) to control what pickle stores.",
            code('''
                import copy, pickle

                class Model:
                    def __init__(self, weights):
                        self.weights = weights
                        self._cache = {}

                    def __deepcopy__(self, memo):
                        clone = Model(copy.deepcopy(self.weights, memo))
                        return clone                          # fresh, empty cache

                    def __getstate__(self):
                        state = self.__dict__.copy()
                        del state["_cache"]                   # do not pickle the cache
                        return state
                    def __setstate__(self, state):
                        self.__dict__.update(state, _cache={})

                m = Model([1, 2])
                m._cache["warm"] = True
                d = copy.deepcopy(m)
                d.weights.append(3)
                print(m.weights, d.weights, d._cache)

                p = pickle.loads(pickle.dumps(m))
                print(p.weights, p._cache)
            '''),
        ),
        section(
            "Putting it together",
            "A small class that implements a dozen dunders feels completely native: it prints well, compares, hashes, sorts, iterates, supports arithmetic and <code>in</code>, and works with <code>sum</code>, <code>sorted</code>, <code>set</code>, <code>dict</code> and f-strings without a single custom method name.",
            code('''
                from functools import total_ordering

                @total_ordering
                class Money:
                    __slots__ = ("cents",)
                    def __init__(self, cents): self.cents = cents
                    def __repr__(self): return f"Money({self.cents})"
                    def __str__(self): return f"${self.cents / 100:,.2f}"
                    def __eq__(self, o):
                        return isinstance(o, Money) and self.cents == o.cents
                    def __lt__(self, o):
                        if not isinstance(o, Money): return NotImplemented
                        return self.cents < o.cents
                    def __hash__(self): return hash(self.cents)
                    def __bool__(self): return self.cents != 0
                    def __add__(self, o):
                        if isinstance(o, Money): return Money(self.cents + o.cents)
                        if o == 0: return self
                        return NotImplemented
                    __radd__ = __add__
                    def __mul__(self, k):
                        if isinstance(k, int): return Money(self.cents * k)
                        return NotImplemented
                    __rmul__ = __mul__

                prices = [Money(1999), Money(500), Money(1999), Money(0)]
                print(sum(prices), max(prices), sorted(set(prices)))
                print(3 * Money(250), Money(100) >= Money(99), [p for p in prices if p])
                print(f"total: {sum(prices)}")
            '''),
        ),
    ],
    questions=[
        question(
            "What is the difference between <code>__new__</code> and <code>__init__</code>? When do you need <code>__new__</code>?",
            "medium",
            "<code>__new__</code> is an implicit static method that receives the class and <em>returns the new object</em>. <code>__init__</code> receives that object and fills it in; it must return <code>None</code>. <code>C(args)</code> is roughly <code>obj = C.__new__(C, args)</code>, then <code>obj.__init__(args)</code> if <code>obj</code> is an instance of <code>C</code>.",
            "You need <code>__new__</code> when the decision has to happen before the object exists: subclassing an immutable type (<code>int</code>, <code>str</code>, <code>tuple</code>) whose value is fixed at creation, returning a cached or singleton instance, or returning an object of a different class. Metaclasses also use <code>__new__</code> to build classes.",
            code('''
                class UpperStr(str):
                    def __new__(cls, value):
                        return super().__new__(cls, value.upper())
                    def __init__(self, value):
                        print("init sees", repr(value), "but self is", repr(str(self)))

                print(UpperStr("hello"))
            '''),
        ),
        question(
            "Why should <code>__add__</code> return <code>NotImplemented</code> instead of raising <code>TypeError</code>?",
            "medium",
            "Returning <code>NotImplemented</code> tells Python &ldquo;I do not handle this operand, ask the other side&rdquo;, so it goes on to try <code>other.__radd__(self)</code>. Raising <code>TypeError</code> ends the operation immediately, so another type that <em>does</em> know how to add itself to yours never gets asked. Python raises the <code>TypeError</code> for you once both sides have returned <code>NotImplemented</code>.",
            code('''
                class Strict:
                    def __add__(self, other):
                        raise TypeError("no")

                class Polite:
                    def __add__(self, other):
                        return NotImplemented

                class Meters:
                    def __radd__(self, other):
                        return f"Meters added to {type(other).__name__}"

                print(Polite() + Meters())
                try:
                    Strict() + Meters()
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "Note that <code>NotImplemented</code> (a singleton value) and <code>NotImplementedError</code> (an exception for abstract methods) are different things.",
        ),
        question(
            "What is the difference between <code>__getattr__</code> and <code>__getattribute__</code>?",
            "medium",
            "<code>__getattribute__</code> runs for every attribute read, before anything else, and is what implements normal lookup (instance dict, class, descriptors). <code>__getattr__</code> is only a fallback: Python calls it after normal lookup has raised <code>AttributeError</code>. Overriding <code>__getattr__</code> is safe and common (proxies, dynamic attributes). Overriding <code>__getattribute__</code> is rare, slows every access, and recurses infinitely if you read <code>self.anything</code> inside it without going through <code>super().__getattribute__</code>.",
            code('''
                class Demo:
                    x = 1
                    def __getattr__(self, name):
                        return f"fallback for {name}"

                d = Demo()
                print(d.x, "|", d.y)
            '''),
        ),
        question(
            "Explain the output: the class defines only <code>__getitem__</code>, yet <code>for</code>, <code>in</code> and <code>list()</code> all work.",
            "hard",
            code('''
                class Squares:
                    def __getitem__(self, i):
                        if i >= 5:
                            raise IndexError
                        print(f"getitem({i})", end=" ")
                        return i * i

                s = Squares()
                print(list(s))
                print(9 in s)
                print(hasattr(s, "__iter__"))
            '''),
            "When a type has no <code>__iter__</code>, <code>iter()</code> falls back to the legacy sequence protocol: it builds an iterator that calls <code>__getitem__(0)</code>, <code>__getitem__(1)</code>, &hellip; until <code>IndexError</code>. <code>in</code> without <code>__contains__</code> iterates and compares, stopping at the first match (so <code>getitem(4)</code> is never called for <code>9 in s</code>). This is why <code>collections.abc.Iterable</code> does not detect such classes &mdash; they have no <code>__iter__</code> &mdash; and why the reliable test for iterability is calling <code>iter(x)</code> and catching <code>TypeError</code>.",
        ),
        question(
            "A proxy class forwards everything with <code>__getattr__</code>, but <code>len(proxy)</code> and <code>proxy[0]</code> fail. Why, and how do you fix it?",
            "hard",
            "Implicit special method lookup (from operators and built-ins) goes directly to the type&rsquo;s slots and never touches <code>__getattr__</code> or <code>__getattribute__</code>. <code>proxy.__len__()</code> written explicitly would be forwarded; <code>len(proxy)</code> is not. The fix is to define the dunders on the proxy class &mdash; by hand, or generated in a loop:",
            code('''
                class Proxy:
                    def __init__(self, target):
                        self._target = target
                    def __getattr__(self, name):
                        return getattr(self._target, name)

                for name in ("__len__", "__getitem__", "__iter__", "__contains__"):
                    def forward(self, *args, _name=name):
                        return getattr(self._target, _name)(*args)
                    setattr(Proxy, name, forward)

                p = Proxy([10, 20, 30])
                print(len(p), p[0], 20 in p, list(p), p.count(10))
            '''),
            "Libraries such as <code>wrapt</code> and <code>unittest.mock.MagicMock</code> do the same: <code>MagicMock</code> exists precisely because a plain <code>Mock</code> cannot intercept dunder calls.",
        ),
        question(
            "Why does <code>+=</code> behave differently on a list stored in a tuple? Explain <code>t = ([1],); t[0] += [2]</code>.",
            "hard",
            code('''
                t = ([1],)
                try:
                    t[0] += [2]
                except TypeError as e:
                    print("TypeError:", e)
                print(t)
            '''),
            "<code>t[0] += [2]</code> expands to three steps: read <code>x = t[0]</code>; compute <code>x = x.__iadd__([2])</code>; store <code>t[0] = x</code>. <code>list.__iadd__</code> mutates the list in place and returns it, so the append has already happened. Then the store calls <code>tuple.__setitem__</code>, which does not exist, and raises. You get both an exception <em>and</em> a changed value. Using <code>t[0].extend([2])</code> avoids the store step entirely.",
        ),
    ],
    refs=[
        ("Python docs: Special method names", "https://docs.python.org/3/reference/datamodel.html#special-method-names"),
        ("Python docs: Emulating numeric types", "https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types"),
        ("Python docs: functools.total_ordering", "https://docs.python.org/3/library/functools.html#functools.total_ordering"),
        ("Python docs: The NotImplemented constant", "https://docs.python.org/3/library/constants.html#NotImplemented"),
    ],
)
