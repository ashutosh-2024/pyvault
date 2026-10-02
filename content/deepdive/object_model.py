from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="object-model",
    title="The Python Object Model",
    intro=[
        "&ldquo;Everything is an object&rdquo; is usually said and not explained. It means something precise: integers, strings, functions, classes, modules, even <code>type</code> itself are all values of the same basic C structure, each with an identity, a type, and a value. They can all be assigned to names, stored in containers, passed around and inspected.",
        "Once that is internalised, a lot of Python stops being magic. Decorators are just functions receiving functions. Classes are just objects created at run time. <code>len(x)</code> is just a call to a method found on <code>x</code>&rsquo;s type.",
    ],
    sections=[
        section(
            "Identity, type and value",
            "Every object has three things. <strong>Identity</strong> never changes while the object lives &mdash; <code>id()</code> returns it, <code>is</code> compares it. <strong>Type</strong> decides what operations the object supports and also never changes in practice. <strong>Value</strong> is what <code>==</code> compares, and may or may not be mutable.",
            code('''
                a = [1, 2, 3]
                b = [1, 2, 3]
                c = a

                print("a == b:", a == b)    # same value
                print("a is b:", a is b)    # different objects
                print("a is c:", a is c)    # two names, one object

                c.append(4)
                print("a:", a)              # changed through c
                print(type(a), type(len), type(3.5))
            '''),
            table(
                ["Operator", "Compares", "Can be overridden", "Use for"],
                [
                    ["<code>is</code>", "Identity (same object)", "No", "<code>None</code>, sentinels, singletons"],
                    ["<code>==</code>", "Value, via <code>__eq__</code>", "Yes", "Everything else"],
                ],
            ),
        ),
        section(
            "Functions are objects",
            "<code>def</code> is an executable statement. When it runs it creates a function object and binds it to a name. That object has a type, attributes, and can be stored and passed like any other value.",
            code('''
                def greet(name, punctuation="!"):
                    """Say hello."""
                    return f"hello {name}{punctuation}"

                print(type(greet).__name__)
                print(greet.__name__, "|", greet.__doc__, "|", greet.__defaults__)

                say = greet                     # another name, same object
                print(say("ann"))

                handlers = {"hi": greet, "shout": str.upper}
                print(handlers["shout"]("quiet"))

                greet.calls = 0                 # functions have a __dict__ too
                greet.calls += 1
                print(greet.__dict__)
            '''),
            "Because functions are values you can return them from other functions. The inner function keeps access to the outer function&rsquo;s variables through <em>closure cells</em>, which is the foundation of decorators and callbacks.",
            code('''
                def multiplier(factor):
                    def apply(x):
                        return x * factor
                    return apply

                double, triple = multiplier(2), multiplier(3)
                print(double(5), triple(5))
                print(double.__closure__[0].cell_contents)
                print(double.__code__ is triple.__code__)   # shared code, separate closures
            '''),
        ),
        section(
            "Classes are objects too",
            "<code>class</code> is also an executable statement. It runs the class body, then calls a <em>metaclass</em> &mdash; <code>type</code> by default &mdash; to build a new object: the class. So a class has a type, can be passed to functions, stored in dicts, and created on the fly.",
            code('''
                class Dog:
                    sound = "woof"
                    def speak(self):
                        return self.sound

                print(type(Dog))
                print(Dog.__name__, Dog.__bases__)

                def build(cls):                 # a class passed as an argument
                    return cls()
                print(build(Dog).speak())

                Cat = type("Cat", (), {"sound": "meow", "speak": lambda self: self.sound})
                print(type(Cat), Cat().speak())
            '''),
            "The three-argument <code>type(name, bases, namespace)</code> call is exactly what a <code>class</code> statement does after running the body. The two classes above are built the same way.",
        ),
        section(
            "type and object: the knot at the top",
            "Two built-ins hold the whole system together. <code>object</code> is the base of every class. <code>type</code> is the class of every class. And they refer to each other:",
            code('''
                print(type(object))            # object is an instance of type
                print(type(type))              # type is an instance of itself
                print(type.__bases__)          # type is a subclass of object
                print(object.__bases__)        # object has no base

                print(isinstance(type, object), isinstance(object, type))
                print(isinstance(3, object), isinstance(int, type))
            '''),
            table(
                ["Relationship", "Question it answers", "Check with"],
                [
                    ["instance-of", "What made this object?", "<code>type(x)</code>, <code>isinstance</code>"],
                    ["subclass-of", "What does this class inherit from?", "<code>C.__bases__</code>, <code>C.__mro__</code>, <code>issubclass</code>"],
                ],
            ),
            "Keep the two relationships apart and the diagram is simple: every class is a subclass of <code>object</code>; every class is an instance of <code>type</code> (or of a metaclass that subclasses <code>type</code>). The loop &mdash; <code>type</code> being its own type &mdash; is wired up in C at start-up.",
        ),
        section(
            "Where attributes live",
            "Instances and classes each have a <code>__dict__</code>. Reading <code>obj.attr</code> checks the instance first, then the class and its bases. Writing <code>obj.attr = v</code> always writes to the instance, which <em>shadows</em> the class attribute rather than changing it.",
            code('''
                class Config:
                    retries = 3
                    tags = []                  # shared by every instance!

                a, b = Config(), Config()
                a.retries = 5                  # creates an instance attribute
                a.tags.append("prod")          # mutates the shared class list

                print(vars(a), vars(b))
                print(a.retries, b.retries, Config.retries)
                print(b.tags)                  # b never touched tags
            '''),
            "Rebinding and mutating look similar and behave completely differently. <code>a.retries = 5</code> adds a key to <code>a.__dict__</code>. <code>a.tags.append(...)</code> reads <code>tags</code> (found on the class) and mutates that one shared list. Mutable defaults belong in <code>__init__</code>.",
            note("The full lookup order also involves descriptors &mdash; which is how methods, <code>property</code> and <code>__slots__</code> work. That is the next topic."),
        ),
        section(
            "Special methods are looked up on the type",
            "Operators and built-ins such as <code>len</code>, <code>+</code>, <code>iter</code> and <code>str</code> do not call <code>obj.__len__</code>. They call <code>type(obj).__len__(obj)</code>, skipping the instance entirely. That is faster, and it stops an instance from redefining what an operator means for itself.",
            code('''
                class Box:
                    def __init__(self, items):
                        self.items = items
                    def __len__(self):
                        return len(self.items)

                b = Box([1, 2, 3])
                b.__len__ = lambda: 99         # instance attribute

                print(b.__len__())             # normal attribute lookup finds it
                print(len(b))                  # len() goes to the type
            '''),
            "This also explains why you cannot make <code>len</code> work on a class by giving the class a <code>__len__</code>: <code>len(Box)</code> looks on <code>type(Box)</code>, which is the metaclass.",
            code('''
                class Sized(type):
                    def __len__(cls):
                        return 42

                class Thing(metaclass=Sized):
                    pass

                print(len(Thing))
            '''),
        ),
        section(
            "Equality, hashing and identity",
            "Objects used as dict keys or set members must be <em>hashable</em>, and equal objects must have equal hashes. By default, an instance compares and hashes by identity. Define <code>__eq__</code> and Python sets <code>__hash__</code> to <code>None</code>, because the old identity hash would now break the rule.",
            code('''
                class Point:
                    def __init__(self, x, y):
                        self.x, self.y = x, y
                    def __eq__(self, other):
                        return (self.x, self.y) == (other.x, other.y)

                print(Point(1, 2) == Point(1, 2))
                print(Point.__hash__)
                try:
                    {Point(1, 2)}
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            code('''
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class Point:
                    x: int
                    y: int

                p = Point(1, 2)
                print({p: "origin-ish"}[Point(1, 2)])
                try:
                    p.x = 5
                except Exception as e:
                    print(type(e).__name__)
            ''', label="the usual fix: an immutable value type"),
            "Only make an object hashable if the fields in its hash cannot change. A mutable object whose hash changes after it is put in a set gets lost in the wrong bucket.",
        ),
        section(
            "Callables",
            "Anything whose type defines <code>__call__</code> can be called. Functions, methods, classes (calling a class makes an instance), and your own objects:",
            code('''
                class Counter:
                    def __init__(self):
                        self.n = 0
                    def __call__(self, step=1):
                        self.n += step
                        return self.n

                tick = Counter()
                tick(); tick(); print(tick(10))

                things = {"len": len, "Counter": Counter, "tick": tick, "'text'": "text", "42": 42}
                for label, thing in things.items():
                    print(f"{label:8} callable={callable(thing)}")
            '''),
            "A callable object is a function that carries state in plain attributes. It is an alternative to a closure and is easier to inspect and test.",
        ),
    ],
    questions=[
        question(
            "What does <code>type(type)</code> return, and how can that be?",
            "medium",
            "It returns <code>type</code>. Every class is an instance of a metaclass, and <code>type</code> is the default metaclass &mdash; including for itself. It cannot be built by the usual rule (you would need <code>type</code> to exist before creating <code>type</code>), so CPython creates both <code>type</code> and <code>object</code> statically in C and links them together: <code>type</code> is an instance of <code>type</code> and a subclass of <code>object</code>; <code>object</code> is an instance of <code>type</code> and has no base.",
        ),
        question(
            "Why does assigning <code>obj.__len__ = ...</code> not change what <code>len(obj)</code> returns?",
            "medium",
            "Implicit special-method lookup bypasses the instance and goes straight to the type: <code>len(obj)</code> is <code>type(obj).__len__(obj)</code>. That makes built-in operations faster (one slot lookup in C, no dict check) and prevents surprising per-instance operator behaviour. To change it, change the class &mdash; or, for a class object itself, its metaclass.",
        ),
        question(
            "A teammate adds <code>__eq__</code> to a class and now instances can&rsquo;t go in a set. Why, and what is the correct fix?",
            "hard",
            "The rule is <em>a == b implies hash(a) == hash(b)</em>. The default hash is based on identity, which would break that rule once equality is by value, so Python sets <code>__hash__ = None</code> whenever a class defines <code>__eq__</code> without <code>__hash__</code>.",
            "The fix depends on whether the object is mutable. If it is a value that should never change, make it immutable and hash the same fields you compare &mdash; <code>@dataclass(frozen=True)</code> does both. If it is mutable, it should <em>not</em> be hashable: changing a field after insertion would leave it in the wrong hash bucket, and lookups would silently fail.",
            code('''
                class Key:
                    def __init__(self, v): self.v = v
                    def __eq__(self, o): return self.v == o.v
                    def __hash__(self): return hash(self.v)      # mutable AND hashable: a trap

                k = Key(1)
                s = {k}
                k.v = 2
                print(k in s)             # the set looks in the bucket for hash(2)
                print(any(x is k for x in s))
            '''),
        ),
        question(
            "Explain the output of this code.",
            "medium",
            code('''
                class Team:
                    members = []
                    def join(self, name):
                        self.members.append(name)

                red, blue = Team(), Team()
                red.join("ann")
                blue.join("bob")
                print(red.members, blue.members, red.members is blue.members)
            '''),
            "<code>members</code> is a class attribute: one list, created once when the class body ran. <code>self.members</code> finds no instance attribute, falls back to the class, and appends to the shared list. Both teams end up with both people. Create per-instance state in <code>__init__</code> (<code>self.members = []</code>). The same trap exists for mutable default arguments, for the same reason: the value is created once, at definition time.",
        ),
        question(
            "Create a class with a method and a class attribute without using the <code>class</code> keyword.",
            "hard",
            "Call the metaclass directly with a name, a tuple of bases and a namespace dict. Methods are just functions in that dict; they become bound methods on access, exactly as with a normal class.",
            code('''
                def __init__(self, name):
                    self.name = name

                def greet(self):
                    return f"{self.greeting}, {self.name}"

                Person = type("Person", (object,), {
                    "greeting": "hello",
                    "__init__": __init__,
                    "greet": greet,
                })

                Student = type("Student", (Person,), {"greeting": "hey"})

                print(Person("ann").greet(), "|", Student("bob").greet())
                print(Student.__mro__)
            '''),
            "Real uses: generating classes from a schema (ORMs, serializers, test parametrisation). <code>types.new_class</code> is the more complete version that also honours <code>__prepare__</code> and keyword arguments like <code>metaclass=</code>.",
        ),
        question(
            "What is the difference between <code>is</code> and <code>==</code>, and when is <code>is</code> the right choice?",
            "medium",
            "<code>is</code> checks identity and cannot be overridden. <code>==</code> calls <code>__eq__</code>, which a class can define however it likes. Use <code>is</code> only for singletons &mdash; <code>None</code>, <code>True</code>/<code>False</code>, <code>Ellipsis</code>, and your own sentinel objects &mdash; where identity <em>is</em> the meaning. Using it on numbers or strings seems to work because of caching and interning, and then fails on other values.",
            code('''
                import math

                nan = float("nan")
                print(nan == nan, nan is nan)            # NaN is not equal to itself
                print(nan in [nan])                      # containers check identity first

                MISSING = object()                       # a sentinel only 'is' can match
                def get(d, key, default=MISSING):
                    value = d.get(key, MISSING)
                    if value is MISSING:
                        return "missing" if default is MISSING else default
                    return value
                print(get({"a": None}, "a"), get({}, "a"))
            '''),
        ),
    ],
    refs=[
        ("Python docs: Data model", "https://docs.python.org/3/reference/datamodel.html"),
        ("Python docs: Special method lookup", "https://docs.python.org/3/reference/datamodel.html#special-method-lookup"),
        ("Python docs: __hash__", "https://docs.python.org/3/reference/datamodel.html#object.__hash__"),
    ],
)
