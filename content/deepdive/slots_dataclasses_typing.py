from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="slots-dataclasses-typing",
    title="__slots__, Dataclasses and Typing",
    intro=[
        "Three features that change how you write classes. <code>__slots__</code> trades the per-instance <code>__dict__</code> for fixed storage: less memory, faster attribute access, no accidental attributes. <code>dataclasses</code> generate <code>__init__</code>, <code>__repr__</code>, <code>__eq__</code> and more from type-annotated fields. And type hints document and check all of it &mdash; without Python enforcing any of it at run time.",
        "Each is simple on its own. The interview questions live in the interactions: slots with inheritance, mutable defaults in dataclasses, frozen dataclasses and hashing, and what annotations really are at run time.",
    ],
    sections=[
        section(
            "__slots__: no per-instance dict",
            "Normally every instance carries a <code>__dict__</code>, a hash table for its attributes. Declaring <code>__slots__</code> tells the class to reserve a fixed array of slots instead. Each slot becomes a descriptor on the class that reads and writes a fixed offset in the object.",
            code('''
                import sys, tracemalloc

                class PointDict:
                    def __init__(self, x, y):
                        self.x, self.y = x, y

                class PointSlots:
                    __slots__ = ("x", "y")
                    def __init__(self, x, y):
                        self.x, self.y = x, y

                def measure(cls, n=100_000):
                    tracemalloc.start()
                    objs = [cls(i, i) for i in range(n)]
                    size = tracemalloc.get_traced_memory()[0]
                    tracemalloc.stop()
                    return size // n

                print("bytes per instance, dict :", measure(PointDict))
                print("bytes per instance, slots:", measure(PointSlots))
                print(hasattr(PointSlots(1, 2), "__dict__"), type(PointSlots.__dict__["x"]).__name__)
            '''),
            "Slots also make the attribute set closed, which turns typos into errors instead of silently creating new attributes:",
            code('''
                class Account:
                    __slots__ = ("owner", "balance")
                    def __init__(self, owner):
                        self.owner, self.balance = owner, 0

                a = Account("ann")
                try:
                    a.balanse = 100                   # typo
                except AttributeError as e:
                    print("AttributeError:", e)
            '''),
            caveat("Since CPython 3.11 a plain instance stores its attributes in a compact inline array and only creates a real <code>__dict__</code> when needed, so the saving from <code>__slots__</code> is smaller than older articles claim. It is still real, as the measurement shows, and it matters when you hold millions of small objects."),
        ),
        section(
            "Slots and inheritance",
            "Slots only take effect if <em>every</em> class in the hierarchy uses them. A subclass that does not declare <code>__slots__</code> gets a <code>__dict__</code> again, and you lose both the memory saving and the closed attribute set. Each subclass should declare only its <em>new</em> slots; repeating a parent's slot wastes space and shadows it.",
            code('''
                class Base:
                    __slots__ = ("id",)

                class Leaky(Base):                   # forgot __slots__
                    pass

                class Tight(Base):
                    __slots__ = ("name",)            # only the new attribute

                l, t = Leaky(), Tight()
                l.anything = 1                       # works: Leaky has a __dict__ again
                print(hasattr(l, "__dict__"), hasattr(t, "__dict__"))
                try:
                    t.anything = 1
                except AttributeError as e:
                    print("AttributeError:", e)
            '''),
            "Other consequences to know: instances cannot be weakly referenced unless <code>\"__weakref__\"</code> is a slot; slots and a class attribute with the same name conflict (so slot defaults must be set in <code>__init__</code>); and multiple inheritance from two classes that both have non-empty slots fails with a layout conflict.",
            code('''
                import weakref

                class A:
                    __slots__ = ("x",)
                class B:
                    __slots__ = ("y",)

                try:
                    weakref.ref(A())
                except TypeError as e:
                    print("TypeError:", e)

                try:
                    class AB(A, B): pass
                except TypeError as e:
                    print("TypeError:", e)

                try:
                    class Defaults:
                        __slots__ = ("x",)
                        x = 0                        # class attribute clashes with the slot
                except ValueError as e:
                    print("ValueError:", e)
            '''),
        ),
        section(
            "Dataclasses: what gets generated",
            "<code>@dataclass</code> reads the class's annotated fields and writes the boilerplate methods for you. It is an ordinary class afterwards &mdash; no base class, no metaclass, no run-time cost per instance beyond what you would have written by hand.",
            code('''
                from dataclasses import dataclass, field, fields, asdict, replace

                @dataclass
                class Item:
                    name: str
                    price: float
                    qty: int = 1
                    tags: list[str] = field(default_factory=list)

                a = Item("pen", 1.5)
                b = Item("pen", 1.5)
                print(a)                                # __repr__
                print(a == b, a is b)                   # __eq__ compares fields as a tuple
                print([f.name for f in fields(Item)])
                print(asdict(replace(a, qty=3)))        # copy with changes, then to dict
                print(Item.__hash__)                    # eq=True and not frozen -> unhashable
            '''),
            table(
                ["Option", "Generates / does", "Default"],
                [
                    ["<code>init</code>", "<code>__init__</code> from the fields", "True"],
                    ["<code>repr</code>", "<code>__repr__</code>", "True"],
                    ["<code>eq</code>", "<code>__eq__</code> (fields compared as a tuple, same class only)", "True"],
                    ["<code>order</code>", "<code>__lt__</code>, <code>__le__</code>, <code>__gt__</code>, <code>__ge__</code>", "False"],
                    ["<code>frozen</code>", "Assignment raises <code>FrozenInstanceError</code>; with <code>eq</code>, also <code>__hash__</code>", "False"],
                    ["<code>slots</code>", "Builds a new class with <code>__slots__</code> (3.10+)", "False"],
                    ["<code>kw_only</code>", "All fields keyword-only in <code>__init__</code> (3.10+)", "False"],
                ],
            ),
        ),
        section(
            "Mutable defaults and field()",
            "A default value is evaluated once, when the class body runs, and shared by every instance &mdash; the same trap as a mutable default argument. Dataclasses refuse the obvious cases (<code>list</code>, <code>dict</code>, <code>set</code>) outright. Use <code>field(default_factory=...)</code> so each instance gets its own.",
            code('''
                from dataclasses import dataclass, field

                try:
                    @dataclass
                    class Cart:
                        items: list = []
                except ValueError as e:
                    print("ValueError:", e)

                @dataclass
                class Cart:
                    items: list = field(default_factory=list)
                    id: int = field(default=0, repr=False, compare=False)

                c1, c2 = Cart(), Cart()
                c1.items.append("apple")
                print(c1, c2, c1.items is c2.items)
                print(Cart(["x"], id=1) == Cart(["x"], id=2))   # id excluded from __eq__
            '''),
            "The check only knows about unhashable built-ins. A mutable default of your own class, or a <code>tuple</code> containing a list, is not caught, so do not rely on it.",
        ),
        section(
            "__post_init__, InitVar and frozen dataclasses",
            "<code>__post_init__</code> runs at the end of the generated <code>__init__</code>, for validation and derived fields. <code>InitVar</code> declares an <code>__init__</code> parameter that is passed to <code>__post_init__</code> but not stored. <code>field(init=False)</code> is a stored field that <code>__init__</code> does not take.",
            code('''
                from dataclasses import dataclass, field, InitVar

                @dataclass
                class User:
                    email: str
                    password: InitVar[str]               # used once, never stored
                    password_hash: str = field(init=False, repr=False)
                    domain: str = field(init=False)

                    def __post_init__(self, password):
                        if "@" not in self.email:
                            raise ValueError(f"bad email {self.email!r}")
                        self.password_hash = f"hash({len(password)} chars)"
                        self.domain = self.email.split("@")[1]

                u = User("ann@example.com", "s3cret")
                print(u, "|", u.password_hash, "|", hasattr(u, "password"))
                try:
                    User("nope", "x")
                except ValueError as e:
                    print("ValueError:", e)
            '''),
            "<code>frozen=True</code> makes assignment raise, and together with <code>eq=True</code> generates a <code>__hash__</code> from the fields, so instances work as dict keys and set members. Inside <code>__post_init__</code> of a frozen class you need <code>object.__setattr__</code> to set derived fields.",
            code('''
                from dataclasses import dataclass, field, FrozenInstanceError

                @dataclass(frozen=True, order=True)
                class Version:
                    major: int
                    minor: int
                    label: str = field(default="", compare=False)
                    key: str = field(init=False, compare=False, repr=False)

                    def __post_init__(self):
                        object.__setattr__(self, "key", f"{self.major}.{self.minor}")

                v = Version(1, 2, "beta")
                print(sorted({Version(2, 0), v, Version(1, 2)}), v.key)   # label is not compared, so v == Version(1, 2)
                try:
                    v.major = 9
                except FrozenInstanceError as e:
                    print("FrozenInstanceError:", e)
            '''),
            note("Frozen means the fields cannot be rebound, not that the objects they point at are immutable. A frozen dataclass holding a <code>list</code> can still have that list mutated &mdash; and then hashing it fails because lists are unhashable."),
        ),
        section(
            "Choosing a record type",
            "Python has several ways to declare a bundle of named fields. They differ in mutability, memory, and whether they are a class or just a type hint over a dict.",
            code('''
                from collections import namedtuple
                from dataclasses import dataclass
                from typing import NamedTuple, TypedDict

                class P1(NamedTuple):
                    x: int
                    y: int

                @dataclass
                class P2:
                    x: int
                    y: int

                @dataclass(slots=True, frozen=True)
                class P3:
                    x: int
                    y: int

                class P4(TypedDict):
                    x: int
                    y: int

                for obj in (P1(1, 2), P2(1, 2), P3(1, 2), P4(x=1, y=2)):
                    print(f"{type(obj).__name__:5} has __dict__={hasattr(obj, '__dict__')!s:5} repr={obj!r}")

                x, y = P1(1, 2)                        # NamedTuple unpacks like a tuple
                print(P1(1, 2) == (1, 2), P2(1, 2) == (1, 2))
            '''),
            table(
                ["", "NamedTuple", "@dataclass", "@dataclass(slots, frozen)", "TypedDict"],
                [
                    ["Mutable", "No", "Yes", "No", "Yes (it is a dict)"],
                    ["Is a tuple / indexable", "Yes", "No", "No", "No"],
                    ["Equal to a plain tuple", "Yes", "No", "No", "Equal to a plain dict"],
                    ["Hashable", "Yes", "No (default)", "Yes", "No"],
                    ["Methods, validation", "Methods only", "Yes, <code>__post_init__</code>", "Yes", "No"],
                    ["Best for", "Small immutable records, tuple APIs", "General data classes", "Many small value objects", "Typing JSON-shaped dicts"],
                ],
            ),
        ),
        section(
            "Type hints are not enforced",
            "Annotations are metadata. The interpreter stores them and otherwise ignores them: a function annotated <code>-&gt; int</code> may return a string, and a dataclass field annotated <code>int</code> accepts anything. Checking happens in a separate tool (mypy, pyright) before the code runs, or in libraries that choose to read the annotations at run time (pydantic, FastAPI, dataclasses for field discovery).",
            code('''
                from dataclasses import dataclass

                def add(a: int, b: int) -> int:
                    return a + b

                @dataclass
                class Box:
                    size: int

                print(add("not ", "checked"))
                print(Box(size="large"))
                print(add.__annotations__)
            '''),
            "Python 3.14 evaluates annotations <em>lazily</em> (PEP 649): they are compiled into a function that runs only when someone asks for <code>__annotations__</code>. Forward references to classes defined later no longer need quotes, and an annotation that names something undefined only fails when it is actually inspected.",
            code('''
                import annotationlib

                class Node:
                    def link(self, other: Node) -> Tree:     # Tree does not exist yet
                        return other

                print("class created fine")
                ann = annotationlib.get_annotations(Node.link, format=annotationlib.Format.FORWARDREF)
                print(ann)

                class Tree: pass
                print(Node.link.__annotations__)              # evaluated now that Tree exists
            '''),
            caveat("Before 3.14, annotations were evaluated when the <code>def</code> or <code>class</code> ran, so <code>other: Node</code> inside <code>Node</code> was a <code>NameError</code>; code wrote <code>\"Node\"</code> in quotes or used <code>from __future__ import annotations</code>, which turns every annotation into a string."),
        ),
        section(
            "Generics, Protocols and the typing toolbox",
            "Generics let a hint say what a container holds. Python 3.12 added a compact syntax for type parameters: <code>def first[T](xs: list[T]) -&gt; T</code> declares <code>T</code> right on the function, replacing <code>T = TypeVar(\"T\")</code>.",
            code('''
                from collections.abc import Callable, Iterable

                def first[T](items: Iterable[T], default: T) -> T:
                    for x in items:
                        return x
                    return default

                class Stack[T]:
                    def __init__(self) -> None:
                        self._items: list[T] = []
                    def push(self, item: T) -> None:
                        self._items.append(item)
                    def pop(self) -> T:
                        return self._items.pop()

                type Handler = Callable[[str], None]          # 3.12 type alias statement

                s = Stack[int]()
                s.push(3)
                print(first([], 0), first("abc", "?"), s.pop())
                print(Stack.__type_params__, Handler.__value__)
            '''),
            "<strong>Protocols</strong> give static <em>duck typing</em>: any class with the right methods matches, with no inheritance. <code>@runtime_checkable</code> also lets <code>isinstance</code> check them &mdash; but only for the presence of the methods, not their signatures.",
            code('''
                from typing import Protocol, runtime_checkable

                @runtime_checkable
                class SupportsClose(Protocol):
                    def close(self) -> None: ...

                class File:
                    def close(self) -> None:
                        print("  file closed")

                class Socket:
                    def close(self, how):               # different signature!
                        print("  socket closed", how)

                def shutdown(resources: list[SupportsClose]) -> None:
                    for r in resources:
                        r.close()

                shutdown([File()])
                print(isinstance(File(), SupportsClose), isinstance(Socket(), SupportsClose),
                      isinstance("text", SupportsClose))
            '''),
            table(
                ["Hint", "Means"],
                [
                    ["<code>X | None</code> (was <code>Optional[X]</code>)", "X or None"],
                    ["<code>A | B</code> (was <code>Union[A, B]</code>)", "either type"],
                    ["<code>Literal[\"r\", \"w\"]</code>", "only these exact values"],
                    ["<code>Final</code>", "must not be reassigned"],
                    ["<code>Callable[[int, str], bool]</code>", "a function taking int, str and returning bool"],
                    ["<code>Self</code>", "the type of the current class (for fluent methods)"],
                    ["<code>Any</code> vs <code>object</code>", "<code>Any</code> turns checking off; <code>object</code> accepts anything but allows almost nothing"],
                    ["<code>TYPE_CHECKING</code>", "True only for the type checker: imports used just for hints"],
                ],
            ),
        ),
    ],
    questions=[
        question(
            "When would you use <code>__slots__</code>, and what do you give up?",
            "medium",
            "Use it for classes with many instances and a fixed set of attributes &mdash; nodes, points, records parsed from a large file &mdash; where the per-instance memory and slightly faster attribute access matter, or where you want misspelled attributes to raise. You give up dynamic attributes, the <code>__dict__</code> (so <code>vars(obj)</code> fails), weak references unless you add <code>__weakref__</code>, class-level defaults for slot names, and easy multiple inheritance. Every class in the hierarchy must declare slots or the benefit disappears.",
            "<code>@dataclass(slots=True)</code> is the low-effort way to get them: it builds the slotted class for you from the fields.",
        ),
        question(
            "Why does this dataclass raise an error, and what would happen with a plain class?",
            "medium",
            code('''
                from dataclasses import dataclass

                class Plain:
                    def __init__(self, tags=[]):
                        self.tags = tags

                a, b = Plain(), Plain()
                a.tags.append("shared!")
                print(b.tags)

                try:
                    @dataclass
                    class D:
                        tags: list = []
                except ValueError as e:
                    print("ValueError:", e)
            '''),
            "Defaults are evaluated once, when the <code>def</code> or <code>class</code> runs, and that one object is shared by every call or instance. The plain class silently shares the list. <code>dataclass</code> detects a <code>list</code>, <code>dict</code> or <code>set</code> default and refuses, pointing you to <code>field(default_factory=list)</code>, which calls the factory once per instance.",
        ),
        question(
            "A frozen dataclass is used as a dict key. A teammate removes <code>frozen=True</code> to allow updates and keys stop working. Why?",
            "hard",
            "With <code>eq=True</code> (the default), dataclass sets <code>__hash__ = None</code> unless the class is frozen, because a mutable object whose fields can change must not be hashable &mdash; its hash would change while it sat in a dict. Removing <code>frozen</code> therefore makes instances unhashable, and every dict or set that used them fails.",
            code('''
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class Key:
                    a: int

                @dataclass
                class MutableKey:
                    a: int

                print(hash(Key(1)) == hash(Key(1)), MutableKey.__hash__)
                try:
                    {MutableKey(1): "x"}
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "If updates are needed, keep the key frozen and build new values with <code>dataclasses.replace(key, a=2)</code>. Forcing <code>unsafe_hash=True</code> on a mutable class brings back the lost-in-the-wrong-bucket bug.",
        ),
        question(
            "Python ignores type hints at run time. So how do FastAPI and pydantic validate request data from them?",
            "hard",
            "Annotations are stored as data on the function or class (<code>__annotations__</code>), and any code can read them. Those libraries call <code>typing.get_type_hints</code> (or <code>annotationlib</code> on 3.14), walk the resulting types, and build validators and converters &mdash; the interpreter itself still checks nothing.",
            code('''
                import typing

                def validate(func, **kwargs):
                    hints = typing.get_type_hints(func)
                    for name, value in kwargs.items():
                        expected = hints[name]
                        if not isinstance(value, expected):
                            try:
                                kwargs[name] = expected(value)        # coerce, like pydantic
                            except (TypeError, ValueError):
                                raise TypeError(f"{name}: expected {expected.__name__}, got {value!r}")
                    return func(**kwargs)

                def create_user(name: str, age: int) -> str:
                    return f"{name} ({age})"

                print(validate(create_user, name="ann", age="34"))
                try:
                    validate(create_user, name="bob", age="old")
                except TypeError as e:
                    print("TypeError:", e)
            '''),
        ),
        question(
            "What is the difference between a <code>Protocol</code> and an abstract base class?",
            "medium",
            "An ABC is <em>nominal</em>: a class matches only if it inherits from the ABC (or is registered). A Protocol is <em>structural</em>: any class with matching methods matches, without knowing the Protocol exists. That makes Protocols the right tool for describing what a function needs from third-party objects you cannot change. ABCs can also provide shared method implementations and refuse to instantiate subclasses that miss abstract methods; Protocols are mainly for the type checker, and their <code>isinstance</code> support (with <code>@runtime_checkable</code>) checks only that the method names exist.",
        ),
    ],
    refs=[
        ("Python docs: __slots__", "https://docs.python.org/3/reference/datamodel.html#slots"),
        ("Python docs: dataclasses", "https://docs.python.org/3/library/dataclasses.html"),
        ("Python docs: typing", "https://docs.python.org/3/library/typing.html"),
        ("PEP 649: Deferred evaluation of annotations", "https://peps.python.org/pep-0649/"),
        ("PEP 695: Type parameter syntax", "https://peps.python.org/pep-0695/"),
        ("PEP 544: Protocols", "https://peps.python.org/pep-0544/"),
    ],
)
