from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="metaclasses",
    title="Metaclasses",
    intro=[
        "An object is created by calling its class. A class is also an object, so it too is created by calling <em>its</em> class &mdash; and the class of a class is called a <strong>metaclass</strong>. By default that is <code>type</code>. Write your own and you control what happens when a class statement runs: you can inspect, change, register or reject the class before anyone uses it.",
        "Metaclasses are powerful and almost always the wrong first tool. Since Python 3.6, <code>__init_subclass__</code>, <code>__set_name__</code> and class decorators cover most of what they were used for. This page explains how they work so you can read framework code, and when you genuinely need one.",
    ],
    sections=[
        section(
            "What a class statement really does",
            "When Python executes a <code>class</code> statement it runs these steps, in this order:",
            table(
                ["Step", "What happens"],
                [
                    ["1. Pick the metaclass", "Explicit <code>metaclass=</code>, else the most derived metaclass among the bases, else <code>type</code>"],
                    ["2. Prepare the namespace", "<code>ns = Meta.__prepare__(name, bases, **kw)</code> &mdash; a dict by default"],
                    ["3. Run the body", "The class body executes like a function, with <code>ns</code> as its locals"],
                    ["4. Create the class", "<code>cls = Meta(name, bases, ns, **kw)</code>, i.e. <code>Meta.__new__</code> then <code>Meta.__init__</code>"],
                    ["5. Inside <code>type.__new__</code>", "Calls <code>__set_name__</code> on every attribute, then <code>__init_subclass__</code> on the parent"],
                    ["6. Decorate and bind", "Class decorators run bottom-up, then the result is bound to the name"],
                ],
            ),
            "A metaclass that prints at each hook makes the order visible:",
            code('''
                class Field:
                    def __set_name__(self, owner, name):
                        print(f"5. __set_name__ {name}")

                class Meta(type):
                    @classmethod
                    def __prepare__(mcls, name, bases, **kw):
                        print(f"2. __prepare__ {name} {kw}")
                        return {}
                    def __new__(mcls, name, bases, ns, **kw):
                        print(f"4. Meta.__new__ {name}, body defined {sorted(k for k in ns if not k.startswith('__'))}")
                        return super().__new__(mcls, name, bases, ns, **kw)   # kw reaches __init_subclass__
                    def __init__(cls, name, bases, ns, **kw):
                        print(f"7. Meta.__init__ {name}")
                        super().__init__(name, bases, ns)

                class Base(metaclass=Meta):
                    def __init_subclass__(cls, **kw):
                        print(f"6. __init_subclass__ {cls.__name__} {kw}")

                def decorate(cls):
                    print(f"8. decorator {cls.__name__}")
                    return cls

                print("---")

                @decorate
                class Model(Base, table="users"):
                    print("3. body runs")
                    id = Field()
            '''),
            "The three lines above the <code>---</code> come from defining <code>Base</code> itself, which also goes through <code>Meta</code>. Below it, <code>Model</code> runs the full sequence &mdash; and the <code>table=&quot;users&quot;</code> keyword from the class line is handed to both <code>__prepare__</code> and <code>__init_subclass__</code>.",
        ),
        section(
            "Writing a metaclass",
            "A metaclass subclasses <code>type</code>. Override <code>__new__</code> to inspect or change the namespace before the class exists, or <code>__init__</code> to work with the finished class. A common real use is enforcing rules at <em>definition</em> time, so mistakes fail at import instead of in production:",
            code('''
                class InterfaceMeta(type):
                    required = ("run", "name")

                    def __new__(mcls, name, bases, ns):
                        cls = super().__new__(mcls, name, bases, ns)
                        if bases:                           # skip the abstract root
                            missing = [a for a in mcls.required if not hasattr(cls, a)]
                            if missing:
                                raise TypeError(f"{name} is missing {missing}")
                        return cls

                class Task(metaclass=InterfaceMeta):
                    pass

                class Backup(Task):
                    name = "backup"
                    def run(self): return "ok"

                print(Backup().run())

                try:
                    class Broken(Task):
                        name = "broken"
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "The error happens when <code>Broken</code> is <em>defined</em>, not when someone later calls <code>run</code>. That is the core value metaclasses offer: code that runs once, per class, at class-creation time.",
        ),
        section(
            "__call__: controlling instance creation",
            "<code>Model()</code> is a call on the class object, so it runs <code>type(Model).__call__</code>. The default <code>type.__call__</code> calls <code>__new__</code>, then <code>__init__</code> if <code>__new__</code> returned an instance of the class. Overriding it on a metaclass intercepts every instantiation:",
            code('''
                class Singleton(type):
                    _instances = {}
                    def __call__(cls, *args, **kwargs):
                        if cls not in cls._instances:
                            print(f"creating {cls.__name__}")
                            cls._instances[cls] = super().__call__(*args, **kwargs)
                        return cls._instances[cls]

                class Settings(metaclass=Singleton):
                    def __init__(self, env="dev"):
                        print(f"__init__ env={env}")
                        self.env = env

                a = Settings("prod")
                b = Settings("test")         # __init__ does not run again
                print(a is b, b.env)
            '''),
            note("Before writing a singleton, ask whether a module-level instance would do. Modules are imported once and cached, so <code>settings = Settings()</code> in <code>config.py</code> is already a singleton, with no magic."),
        ),
        section(
            "__prepare__: a custom class namespace",
            "<code>__prepare__</code> returns the mapping the class body executes in. Returning something other than a plain dict lets you observe the body as it runs &mdash; for example, catch a method being silently redefined:",
            code('''
                class NoDuplicates(dict):
                    def __setitem__(self, key, value):
                        if key in self and not key.startswith("__"):
                            raise TypeError(f"{key!r} defined twice")
                        super().__setitem__(key, value)

                class StrictMeta(type):
                    @classmethod
                    def __prepare__(mcls, name, bases):
                        return NoDuplicates()
                    def __new__(mcls, name, bases, ns):
                        return super().__new__(mcls, name, bases, dict(ns))

                try:
                    class Handlers(metaclass=StrictMeta):
                        def on_save(self): return "v1"
                        def on_load(self): return "load"
                        def on_save(self): return "v2"     # copy-paste accident
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "<code>enum.Enum</code> uses exactly this trick to reject duplicate member names. Since 3.6, the default class namespace preserves definition order, so the old reason for <code>__prepare__</code> (returning an <code>OrderedDict</code>) is gone.",
        ),
        section(
            "Lighter alternatives",
            "Most things that once needed a metaclass now have simpler tools that compose better, because a class can only have one metaclass:",
            code('''
                class Plugin:
                    registry = {}

                    def __init_subclass__(cls, name=None, **kwargs):
                        super().__init_subclass__(**kwargs)
                        cls.registry[name or cls.__name__.lower()] = cls

                class CsvExporter(Plugin, name="csv"):
                    pass

                class JsonExporter(Plugin):
                    pass

                print(Plugin.registry)
            ''', label="__init_subclass__: a plugin registry with no metaclass"),
            code('''
                def register(registry):
                    def deco(cls):
                        registry[cls.__name__] = cls
                        return cls
                    return deco

                COMMANDS = {}

                @register(COMMANDS)
                class Deploy: ...

                @register(COMMANDS)
                class Rollback: ...

                print(list(COMMANDS))
            ''', label="a class decorator: explicit, one class at a time"),
            table(
                ["Need", "Best tool", "Why"],
                [
                    ["React to subclasses being defined", "<code>__init_subclass__</code>", "Plain method, inherited, no metaclass conflicts"],
                    ["Per-attribute setup (knowing the attribute name)", "<code>__set_name__</code> on a descriptor", "Each field configures itself"],
                    ["Transform or register one class", "Class decorator", "Explicit at the use site, easy to read"],
                    ["Custom class namespace during the body", "Metaclass <code>__prepare__</code>", "Nothing else runs that early"],
                    ["Change behaviour of the class object itself (<code>len(Cls)</code>, <code>Cls[x]</code>, iteration over a class)", "Metaclass", "Special methods are looked up on the type of the class"],
                    ["Intercept every instantiation", "Metaclass <code>__call__</code> (or <code>__new__</code>)", "The call on the class goes to the metaclass"],
                ],
            ),
            "<code>__class_getitem__</code> is another escape hatch: it lets <code>MyClass[int]</code> work without a metaclass, which is how generics like <code>list[int]</code> are implemented.",
        ),
        section(
            "Metaclass conflicts",
            "A class has exactly one metaclass, and it must be a subclass of the metaclass of every base. Mix two bases whose metaclasses are unrelated and Python cannot choose:",
            code('''
                from abc import ABCMeta

                class MetaA(type): pass

                class Plugin(metaclass=MetaA): pass
                class Interface(metaclass=ABCMeta): pass

                try:
                    class Both(Plugin, Interface): pass
                except TypeError as e:
                    print("TypeError:", e)

                class CombinedMeta(MetaA, ABCMeta): pass      # derive from both

                class Both(Plugin, Interface, metaclass=CombinedMeta): pass
                print(type(Both).__mro__)
            '''),
            "This is the practical reason libraries avoid metaclasses: every one you add is a potential conflict for users who combine your classes with someone else&rsquo;s (ABCs, Qt objects, ORMs). A combined metaclass works only if both metaclasses call <code>super()</code> cooperatively.",
        ),
        section(
            "Where you meet them in the wild",
            table(
                ["Library", "Metaclass", "What it does at class creation"],
                [
                    ["<code>abc</code>", "<code>ABCMeta</code>", "Collects abstract methods, blocks instantiation until they are implemented, supports <code>register()</code> for virtual subclasses"],
                    ["<code>enum</code>", "<code>EnumType</code>", "Turns class attributes into singleton members, forbids duplicates, makes the class iterable and <code>len()</code>-able"],
                    ["Django", "<code>ModelBase</code>", "Reads field descriptors, builds <code>_meta</code>, registers the model"],
                    ["<code>typing</code>", "(mostly removed)", "Replaced by <code>__class_getitem__</code> and <code>__init_subclass__</code> in 3.7 &mdash; for speed and to stop conflicts"],
                ],
            ),
            code('''
                from enum import Enum

                class Color(Enum):
                    RED = 1
                    GREEN = 2

                print(type(Color).__name__)
                print(len(Color), [c.name for c in Color])      # len() and iteration on a class
                print(Color["RED"], Color(2))                   # indexing and calling a class
            '''),
            "Every one of those operations &mdash; <code>len</code>, iterating, indexing, calling with a value &mdash; is a special method on <code>EnumType</code>, operating on the class object.",
        ),
    ],
    questions=[
        question(
            "What is a metaclass, and when would you actually use one?",
            "medium",
            "A metaclass is the class of a class: the thing called to create a class object when a <code>class</code> statement runs. <code>type</code> is the default. Custom ones subclass <code>type</code> and override <code>__new__</code>, <code>__init__</code>, <code>__prepare__</code> or <code>__call__</code>.",
            "Genuine uses today: customising the class namespace (<code>__prepare__</code>), giving class objects their own behaviour (<code>len(Color)</code>, <code>Model.objects</code> as a class-level property), and frameworks that need to process every class in a hierarchy. For registration, validation of subclasses and per-field setup, prefer <code>__init_subclass__</code>, <code>__set_name__</code> or a class decorator. Tim Peters&rsquo; line is still the honest answer: if you are wondering whether you need one, you don&rsquo;t.",
        ),
        question(
            "Implement a singleton with <code>__new__</code> and with a metaclass. What is different?",
            "hard",
            code('''
                class ViaNew:
                    _instance = None
                    def __new__(cls, *args, **kwargs):
                        if cls._instance is None:
                            cls._instance = super().__new__(cls)
                        return cls._instance
                    def __init__(self, value):
                        print(f"ViaNew.__init__({value})")
                        self.value = value

                class SingletonMeta(type):
                    def __call__(cls, *args, **kwargs):
                        if "_instance" not in cls.__dict__:
                            cls._instance = super().__call__(*args, **kwargs)
                        return cls._instance

                class ViaMeta(metaclass=SingletonMeta):
                    def __init__(self, value):
                        print(f"ViaMeta.__init__({value})")
                        self.value = value

                a, b = ViaNew(1), ViaNew(2)
                print("ViaNew:", a is b, a.value)
                c, d = ViaMeta(1), ViaMeta(2)
                print("ViaMeta:", c is d, c.value)
            '''),
            "With <code>__new__</code>, <code>type.__call__</code> still runs <code>__init__</code> on the returned object every time, so the second call silently overwrites the state. The metaclass version short-circuits <code>__call__</code> itself, so <code>__init__</code> runs once. Checking <code>cls.__dict__</code> rather than <code>hasattr</code> also stops a subclass from inheriting its parent&rsquo;s instance.",
        ),
        question(
            "In what order do <code>__prepare__</code>, the class body, <code>__new__</code>, <code>__init__</code>, <code>__set_name__</code> and <code>__init_subclass__</code> run?",
            "hard",
            "<code>__prepare__</code> creates the namespace, the body fills it, then the metaclass is called: <code>Meta.__new__</code> runs and, inside <code>type.__new__</code>, the class object is built, <code>__set_name__</code> is called on every descriptor in the namespace, and then the parent&rsquo;s <code>__init_subclass__</code> runs. Only after <code>__new__</code> returns does <code>Meta.__init__</code> run. Class decorators come last. The trace in the first section above shows it: 2, 3, 4, 5, 6, 7, 8.",
            "The detail interviewers probe: <code>__init_subclass__</code> runs <em>before</em> <code>Meta.__init__</code>, so a metaclass that sets up attributes in <code>__init__</code> cannot rely on them being there during <code>__init_subclass__</code>. Do that setup in <code>__new__</code> instead.",
        ),
        question(
            "Build a plugin registry where defining a subclass is enough to register it.",
            "medium",
            "Use <code>__init_subclass__</code> &mdash; no metaclass needed. Accept keyword arguments from the class statement, and always forward the rest to <code>super()</code> so the hook cooperates with other base classes.",
            code('''
                class Handler:
                    handlers = {}

                    def __init_subclass__(cls, *, event, **kwargs):
                        super().__init_subclass__(**kwargs)
                        if event in Handler.handlers:
                            raise TypeError(f"duplicate handler for {event!r}")
                        Handler.handlers[event] = cls

                    @classmethod
                    def dispatch(cls, event, payload):
                        return cls.handlers[event]().handle(payload)

                class OnSignup(Handler, event="signup"):
                    def handle(self, p): return f"welcome {p}"

                class OnDelete(Handler, event="delete"):
                    def handle(self, p): return f"goodbye {p}"

                print(Handler.dispatch("signup", "ann"))
                print(sorted(Handler.handlers))
            '''),
            "Writing <code>Handler.handlers</code> rather than <code>cls.handlers</code> matters: it keeps one shared registry even if a subclass ever defines its own <code>handlers</code> attribute.",
        ),
        question(
            "Why do you get &ldquo;metaclass conflict&rdquo;, and how do you resolve it?",
            "hard",
            "A class&rsquo;s metaclass must be a (non-strict) subclass of the metaclasses of all its bases, so that every base&rsquo;s class-level behaviour still applies. If two bases have unrelated metaclasses, no candidate satisfies that and Python raises <code>TypeError</code>.",
            "Fix it by defining a metaclass that inherits from both and passing it explicitly: <code>class M(MetaA, MetaB): pass</code>, then <code>class C(A, B, metaclass=M)</code>. It only works if both metaclasses use <code>super()</code> in their <code>__new__</code>/<code>__init__</code>. The better long-term fix is removing a metaclass that could have been <code>__init_subclass__</code>.",
        ),
        question(
            "What does <code>type(name, bases, dict)</code> do, and how is it related to <code>class</code>?",
            "medium",
            "It creates a new class. It is literally step 4 of executing a <code>class</code> statement, with the namespace you pass in place of one produced by running a body. Metaclass <code>__new__</code> methods end by calling <code>super().__new__(mcls, name, bases, ns)</code>, which is this same call.",
            code('''
                def describe(self):
                    return f"{type(self).__name__}({self.__dict__})"

                Record = type("Record", (), {"__repr__": describe, "kind": "row"})
                r = Record()
                r.id = 7
                print(r, Record.kind, type(Record))
            '''),
        ),
    ],
    refs=[
        ("Python docs: Customizing class creation", "https://docs.python.org/3/reference/datamodel.html#customizing-class-creation"),
        ("PEP 487 — Simpler customisation of class creation", "https://peps.python.org/pep-0487/"),
        ("PEP 3115 — Metaclasses in Python 3000", "https://peps.python.org/pep-3115/"),
    ],
)
