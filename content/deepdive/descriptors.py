from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="descriptors",
    title="Descriptors",
    intro=[
        "A descriptor is any object whose class defines <code>__get__</code>, <code>__set__</code> or <code>__delete__</code>, stored as a <em>class</em> attribute. When you access that attribute through an instance, Python calls those methods instead of returning the object itself.",
        "It sounds niche, but it is the machinery behind methods, <code>self</code>, <code>property</code>, <code>classmethod</code>, <code>staticmethod</code>, <code>__slots__</code>, <code>functools.cached_property</code>, and every ORM field you have used. Understanding descriptors is understanding how attribute access actually works.",
    ],
    sections=[
        section(
            "The protocol",
            "Three optional methods, plus a fourth that tells the descriptor its own name:",
            table(
                ["Method", "Called for", "Receives"],
                [
                    ["<code>__get__(self, obj, objtype)</code>", "<code>obj.attr</code> and <code>Class.attr</code>", "The instance (or <code>None</code> via the class) and the class"],
                    ["<code>__set__(self, obj, value)</code>", "<code>obj.attr = value</code>", "The instance and the new value"],
                    ["<code>__delete__(self, obj)</code>", "<code>del obj.attr</code>", "The instance"],
                    ["<code>__set_name__(self, owner, name)</code>", "Once, when the class is created", "The owning class and the attribute name"],
                ],
            ),
            code('''
                class Traced:
                    def __set_name__(self, owner, name):
                        self.name = name
                        print(f"__set_name__: {owner.__name__}.{name}")

                    def __get__(self, obj, objtype=None):
                        print(f"__get__ obj={type(obj).__name__} objtype={objtype.__name__}")
                        return 42 if obj is not None else self

                    def __set__(self, obj, value):
                        print(f"__set__ {self.name} = {value!r}")

                class Account:
                    balance = Traced()

                print("--- class created ---")
                acct = Account()
                print(acct.balance)
                acct.balance = 100
                print(Account.balance.__class__.__name__)
            '''),
            "Notice that <code>acct.balance = 100</code> did not create an instance attribute &mdash; the descriptor intercepted the assignment. And accessing through the class passed <code>obj=None</code>; returning <code>self</code> in that case is the convention, so tools can introspect the descriptor.",
        ),
        section(
            "Data vs non-data descriptors, and the lookup order",
            "A descriptor that defines <code>__set__</code> or <code>__delete__</code> is a <strong>data descriptor</strong>. One with only <code>__get__</code> is a <strong>non-data descriptor</strong>. The difference decides who wins when the instance also has an attribute of the same name.",
            code('''
                class Data:
                    def __get__(self, obj, t=None): return "from data descriptor"
                    def __set__(self, obj, v): raise AttributeError("read-only")

                class NonData:
                    def __get__(self, obj, t=None): return "from non-data descriptor"

                class C:
                    d = Data()
                    n = NonData()

                c = C()
                c.__dict__["d"] = "from instance dict"    # sneak past __set__
                c.__dict__["n"] = "from instance dict"

                print("c.d ->", c.d)
                print("c.n ->", c.n)
            '''),
            "That gives the full order <code>object.__getattribute__</code> follows for <code>obj.name</code>:",
            table(
                ["Step", "Look for", "If found"],
                [
                    ["1", "<code>name</code> in <code>type(obj).__mro__</code>", "Remember it; if it is a <strong>data descriptor</strong>, call its <code>__get__</code> and stop"],
                    ["2", "<code>name</code> in <code>obj.__dict__</code>", "Return it"],
                    ["3", "The class attribute from step 1", "If it is a non-data descriptor call <code>__get__</code>, else return it as is"],
                    ["4", "Nothing found", "Call <code>__getattr__</code> if defined, else raise <code>AttributeError</code>"],
                ],
            ),
            "Data descriptors win over the instance, so <code>property</code> cannot be bypassed by assignment. Non-data descriptors lose to the instance, so a method can be shadowed per instance and a cache can store its result in the instance dict.",
        ),
        section(
            "Functions are descriptors: how methods and self work",
            "There is no special &ldquo;method&rdquo; type in a class body. <code>def</code> inside a class makes a plain function. Functions define <code>__get__</code>, and that is where <code>self</code> comes from: looking the function up through an instance returns a <em>bound method</em> that remembers the instance.",
            code('''
                class Greeter:
                    def hello(self, name):
                        return f"{type(self).__name__} says hi to {name}"

                g = Greeter()
                raw = Greeter.__dict__["hello"]

                print(type(raw).__name__)                    # a plain function
                print(type(g.hello).__name__)                # a bound method
                bound = raw.__get__(g, Greeter)              # what g.hello does
                print(bound("ann"))
                print(bound.__self__ is g, bound.__func__ is raw)
                print(Greeter.hello(g, "bob"))               # unbound: pass self yourself
            '''),
            "Every <code>g.hello</code> builds a new bound method object, so <code>g.hello is g.hello</code> is <code>False</code> (CPython avoids actually allocating one for a direct call <code>g.hello()</code>). And because functions are non-data descriptors, an instance attribute with the same name shadows the method.",
        ),
        section(
            "property is a data descriptor",
            "<code>property</code> is not special syntax. It is a class written in C, and you can write an equivalent one in a dozen lines:",
            code('''
                class MyProperty:
                    def __init__(self, fget=None, fset=None):
                        self.fget, self.fset = fget, fset

                    def __get__(self, obj, objtype=None):
                        if obj is None:
                            return self
                        return self.fget(obj)

                    def __set__(self, obj, value):
                        if self.fset is None:
                            raise AttributeError("can't set attribute")
                        self.fset(obj, value)

                    def setter(self, fset):
                        return type(self)(self.fget, fset)   # a new descriptor, like property

                class Temperature:
                    def __init__(self, celsius):
                        self._c = celsius

                    @MyProperty
                    def fahrenheit(self):
                        return self._c * 9 / 5 + 32

                    @fahrenheit.setter
                    def fahrenheit(self, f):
                        self._c = (f - 32) * 5 / 9

                t = Temperature(100)
                print(t.fahrenheit)
                t.fahrenheit = 32
                print(t._c)
            '''),
            "Because <code>@x.setter</code> returns a <em>new</em> property, the setter function must use the same name as the getter &mdash; otherwise the class ends up with two attributes, one of which has no setter.",
        ),
        section(
            "classmethod and staticmethod",
            "Both are non-data descriptors that change what <code>__get__</code> binds:",
            code('''
                class MyClassMethod:
                    def __init__(self, f): self.f = f
                    def __get__(self, obj, objtype=None):
                        cls = objtype if objtype is not None else type(obj)
                        return self.f.__get__(cls)       # bind to the class, not the instance

                class MyStaticMethod:
                    def __init__(self, f): self.f = f
                    def __get__(self, obj, objtype=None):
                        return self.f                    # no binding at all

                class Pizza:
                    size = "medium"

                    @MyClassMethod
                    def make(cls, topping):
                        return f"{cls.__name__}({topping}, {cls.size})"

                    @MyStaticMethod
                    def slices(n):
                        return n * 8

                class Large(Pizza):
                    size = "large"

                print(Pizza.make("ham"), Large().make("olive"), Pizza.slices(2))
            '''),
            table(
                ["Decorator", "First argument", "Typical use"],
                [
                    ["none (plain function)", "The instance", "Behaviour that needs the object&rsquo;s state"],
                    ["<code>@classmethod</code>", "The class it was called on (subclass-aware)", "Alternative constructors: <code>datetime.fromtimestamp</code>, <code>dict.fromkeys</code>"],
                    ["<code>@staticmethod</code>", "Nothing", "A helper that belongs in the class namespace but needs neither"],
                ],
            ),
        ),
        section(
            "Reusable validated fields",
            "The payoff of writing your own descriptor is reuse. A property validates one attribute on one class; a descriptor class validates any attribute on any class. <code>__set_name__</code> tells each instance of the descriptor which attribute it manages, so it can store the value in the owner instance&rsquo;s own <code>__dict__</code>.",
            code('''
                class Positive:
                    def __set_name__(self, owner, name):
                        self.public = name
                        self.private = "_" + name

                    def __get__(self, obj, objtype=None):
                        if obj is None:
                            return self
                        return getattr(obj, self.private)

                    def __set__(self, obj, value):
                        if not isinstance(value, (int, float)) or value <= 0:
                            raise ValueError(f"{self.public} must be positive, got {value!r}")
                        setattr(obj, self.private, value)

                class Order:
                    quantity = Positive()
                    price = Positive()
                    def __init__(self, quantity, price):
                        self.quantity = quantity         # goes through __set__
                        self.price = price

                a, b = Order(2, 9.5), Order(5, 1.0)
                print(a.quantity, b.quantity, vars(a))
                try:
                    Order(0, 3)
                except ValueError as e:
                    print("ValueError:", e)
            '''),
            "The classic bug is storing the value on the descriptor (<code>self.value = value</code>). There is only one descriptor object per class attribute, shared by every instance:",
            code('''
                class Broken:
                    def __get__(self, obj, t=None): return self.value
                    def __set__(self, obj, value): self.value = value   # one slot for everyone

                class Order:
                    quantity = Broken()

                a, b = Order(), Order()
                a.quantity = 2
                b.quantity = 99
                print(a.quantity)
            ''', label="the bug"),
            note("This pattern &mdash; a descriptor per field, storing into the instance &mdash; is how Django model fields, SQLAlchemy columns and attrs validators work."),
        ),
        section(
            "cached_property, __getattr__ and __slots__",
            "<code>functools.cached_property</code> uses the lookup order cleverly. It is a <em>non-data</em> descriptor: on first access its <code>__get__</code> computes the value and writes it into the instance <code>__dict__</code> under the same name. From then on, step 2 of the lookup finds the instance value and the descriptor is never called again.",
            code('''
                from functools import cached_property

                class Dataset:
                    @cached_property
                    def stats(self):
                        print("  computing...")
                        return {"mean": 4.2}

                d = Dataset()
                print(d.stats)
                print(d.stats)                 # served from d.__dict__
                print("stats" in vars(d))
                del d.stats                    # invalidate: next access recomputes
                print(d.stats)
            '''),
            "<code>__getattr__</code> is the fallback at step 4: it runs only when normal lookup fails. <code>__getattribute__</code> replaces the whole algorithm and runs for <em>every</em> access, which is rarely what you want.",
            code('''
                class Lazy:
                    real = "found normally"
                    def __getattr__(self, name):
                        return f"__getattr__ made up {name!r}"

                x = Lazy()
                print(x.real)
                print(x.anything)
            '''),
            "<code>__slots__</code> works by creating one data descriptor per slot on the class. The value lives at a fixed offset inside the instance, and there is no <code>__dict__</code> to fall back to:",
            code('''
                class P:
                    __slots__ = ("x", "y")

                print(type(P.__dict__["x"]).__name__)
                print(hasattr(P.__dict__["x"], "__set__"))
            '''),
        ),
    ],
    questions=[
        question(
            "When would you write a descriptor instead of using <code>property</code>?",
            "medium",
            "When the same logic applies to several attributes or several classes. A <code>property</code> is one-off: validating ten numeric fields needs ten nearly identical getter/setter pairs. One <code>Positive</code> or <code>Typed(int)</code> descriptor class, used as <code>price = Positive()</code>, removes that duplication, and <code>__set_name__</code> gives each use its own storage name.",
            "Use <code>property</code> for a single computed or validated attribute &mdash; it is clearer to read. Reach for a descriptor when you catch yourself copying properties, or when building a framework-style API (fields, columns, typed config).",
        ),
        question(
            "<code>cached_property</code> has no <code>__set__</code>. How does it cache, and what is the catch?",
            "hard",
            "Because it is a non-data descriptor, the instance <code>__dict__</code> takes priority over it. The first access falls through to the descriptor&rsquo;s <code>__get__</code>, which computes the value and stores it in <code>obj.__dict__[name]</code>. Every later access finds the dict entry first and never reaches the descriptor. Deleting the attribute removes the dict entry and brings the descriptor back into play.",
            "The catches: it needs an instance <code>__dict__</code>, so it fails on classes with <code>__slots__</code> (unless <code>__dict__</code> is one of the slots); it can be overwritten by plain assignment; and since Python 3.12 it no longer takes a lock, so two threads can both compute the value.",
            code('''
                from functools import cached_property

                class Slotted:
                    __slots__ = ("x",)
                    @cached_property
                    def total(self):
                        return 1

                try:
                    Slotted().total
                except TypeError as e:
                    print("TypeError:", e)
            '''),
        ),
        question(
            "Is <code>obj.method is obj.method</code> true? Why or why not?",
            "hard",
            code('''
                class A:
                    def m(self): pass

                a = A()
                print(a.m is a.m)
                print(a.m == a.m)
                print(A.m is A.m)
                print(a.m.__func__ is A.m)
            '''),
            "Each access to <code>a.m</code> calls <code>function.__get__</code>, which creates a fresh bound method object. The two objects are different, so <code>is</code> is <code>False</code>; bound methods define <code>__eq__</code> as &ldquo;same function and same <code>__self__</code>&rdquo;, so <code>==</code> is <code>True</code>. Accessing through the class returns the underlying function itself, which is the same object each time.",
            "The practical consequence: registering <code>a.m</code> as a callback and later trying to unregister it with <code>is</code> fails. Compare with <code>==</code>, or keep the bound method you registered.",
        ),
        question(
            "What is the difference between <code>__getattr__</code> and <code>__getattribute__</code>, and what goes wrong with the latter?",
            "medium",
            "<code>__getattr__</code> is called only after normal lookup fails. <code>__getattribute__</code> <em>is</em> normal lookup: it is called for every attribute access on the instance, including <code>self.anything</code> inside your own implementation. Accessing <code>self.x</code> inside it recurses forever; you must delegate with <code>super().__getattribute__(name)</code> or <code>object.__getattribute__(self, name)</code>.",
            code('''
                class Audited:
                    def __init__(self):
                        self.log = []
                        self.value = 1

                    def __getattribute__(self, name):
                        log = super().__getattribute__("log")     # not self.log!
                        log.append(name)
                        return super().__getattribute__(name)

                a = Audited()
                a.value; a.value
                print(object.__getattribute__(a, "log"))
            '''),
            "Remember too that special-method lookup by operators skips both hooks: <code>len(obj)</code> goes to the type and never calls the instance&rsquo;s <code>__getattribute__</code>.",
        ),
        question(
            "Why does a validating descriptor that stores <code>self.value = value</code> break, and what are the correct places to store per-instance data?",
            "hard",
            "The descriptor is a class attribute, so there is exactly one descriptor object shared by every instance of the owner class. Storing the value on it means every instance shares one value &mdash; the last write wins.",
            "Correct options: store into the instance&rsquo;s <code>__dict__</code> under a private name learned from <code>__set_name__</code> (the usual choice); store in the instance under the <em>same</em> name as the descriptor, which works for data descriptors because they take priority over the dict; or keep a <code>weakref.WeakKeyDictionary</code> on the descriptor, keyed by instance, for classes that have no <code>__dict__</code>. A plain dict keyed by instance would leak every instance forever.",
        ),
        question(
            "What happens when you assign to a property that has no setter?",
            "medium",
            code('''
                class Circle:
                    def __init__(self, r): self.r = r
                    @property
                    def area(self): return 3.14159 * self.r ** 2

                c = Circle(2)
                c.area = 10
            ''', raises=True),
            "<code>property</code> always defines <code>__set__</code> &mdash; even without a setter function &mdash; so it is a data descriptor and wins over the instance dict. Its <code>__set__</code> raises <code>AttributeError</code> when no setter was provided. That is what makes a getter-only property genuinely read-only, rather than something a plain assignment could shadow.",
        ),
    ],
    refs=[
        ("Python docs: Descriptor HowTo Guide", "https://docs.python.org/3/howto/descriptor.html"),
        ("Python docs: Implementing descriptors", "https://docs.python.org/3/reference/datamodel.html#implementing-descriptors"),
        ("Python docs: functools.cached_property", "https://docs.python.org/3/library/functools.html#functools.cached_property"),
    ],
)
