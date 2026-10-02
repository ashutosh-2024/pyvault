from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="mro",
    title="Method Resolution Order",
    intro=[
        "When you call <code>obj.method()</code> and several classes in the hierarchy define <code>method</code>, Python needs one unambiguous answer to &ldquo;which one?&rdquo;. It gets it by flattening the inheritance graph into a single ordered list &mdash; the <strong>method resolution order</strong> &mdash; and taking the first class in that list that defines the name.",
        "With single inheritance the list is obvious. With multiple inheritance it is computed by the <strong>C3 linearization</strong> algorithm, and it is also what <code>super()</code> walks. Most confusion about <code>super()</code> disappears once you see that it means &ldquo;the next class in the MRO&rdquo;, not &ldquo;my parent&rdquo;.",
    ],
    sections=[
        section(
            "The MRO is a list you can read",
            "Every class has a <code>__mro__</code> tuple. Attribute lookup walks it left to right and stops at the first class whose <code>__dict__</code> has the name.",
            code('''
                class Animal:
                    def speak(self): return "..."
                    def move(self):  return "moves"

                class Dog(Animal):
                    def speak(self): return "woof"

                class Puppy(Dog):
                    pass

                print([c.__name__ for c in Puppy.__mro__])
                p = Puppy()
                print(p.speak(), p.move())

                for name in ("speak", "move"):
                    owner = next(c for c in Puppy.__mro__ if name in c.__dict__)
                    print(f"{name} found on {owner.__name__}")
            '''),
        ),
        section(
            "The diamond",
            "Multiple inheritance gets interesting when two bases share an ancestor. Should <code>D</code> look in <code>A</code> before or after <code>C</code>?",
            code('''
                class A:
                    def who(self): return "A"

                class B(A):
                    pass

                class C(A):
                    def who(self): return "C"

                class D(B, C):
                    pass

                print([k.__name__ for k in D.__mro__])
                print(D().who())
            '''),
            "Python 2&rsquo;s old-style classes used depth-first search, which would have visited <code>D, B, A</code> and returned <code>&quot;A&quot;</code> &mdash; ignoring <code>C</code>&rsquo;s override even though <code>C</code> is a more specific class than <code>A</code>. C3 guarantees a class always comes before its own bases, so <code>A</code> is pushed after both <code>B</code> and <code>C</code>.",
            "C3 enforces three rules together:",
            table(
                ["Rule", "Meaning"],
                [
                    ["Children before parents", "A class always appears before every one of its bases"],
                    ["Local order is kept", "If a class lists <code>(B, C)</code>, B comes before C in the result"],
                    ["Monotonic", "A class&rsquo;s MRO is consistent with each of its bases&rsquo; MROs &mdash; a subclass never reorders what its parents agreed on"],
                ],
            ),
        ),
        section(
            "Computing C3 by hand",
            "The rule: <em>L[C] = C + merge(L[B1], L[B2], &hellip;, [B1, B2, &hellip;])</em>. To merge, repeatedly take the first head of a list that does not appear in the <em>tail</em> (anything after the first element) of any other list; remove it everywhere and repeat. If no head qualifies, there is no consistent order.",
            code('''
                def c3(cls):
                    if cls is object:
                        return [object]
                    seqs = [c3(b) for b in cls.__bases__] + [list(cls.__bases__)]
                    result = [cls]
                    while any(seqs):
                        for seq in seqs:
                            if not seq:
                                continue
                            head = seq[0]
                            if not any(head in s[1:] for s in seqs):
                                break
                        else:
                            raise TypeError("no consistent MRO")
                        result.append(head)
                        seqs = [[x for x in s if x is not head] for s in seqs]
                    return result

                class A: pass
                class B(A): pass
                class C(A): pass
                class D(B, C): pass
                class E: pass
                class F(D, E): pass

                print([k.__name__ for k in c3(F)])
                print(c3(F) == list(F.__mro__))
            '''),
            "Walking it for <code>D(B, C)</code>: merge <code>[B, A, object]</code>, <code>[C, A, object]</code>, <code>[B, C]</code>. Take <code>B</code> (not in any tail). Now <code>A</code> heads the first list but is in the tail of <code>[C, A, object]</code>, so skip it and take <code>C</code>. Now <code>A</code> is free, then <code>object</code>. Result: <code>D, B, C, A, object</code>.",
        ),
        section(
            "When no order exists",
            "If two bases demand opposite orders, C3 refuses rather than guessing, and the class statement fails:",
            code('''
                class X: pass
                class Y: pass
                class XY(X, Y): pass      # says X before Y
                class YX(Y, X): pass      # says Y before X

                try:
                    class Z(XY, YX): pass
                except TypeError as e:
                    print("TypeError:", e)

                try:
                    class Bad(object, X): pass    # base listed before its subclass
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "The second case catches a common beginner mistake: listing a general base before a more specific one. Put more specific classes (mixins, subclasses) first and general ones last.",
        ),
        section(
            "super() means &ldquo;next in the MRO&rdquo;",
            "<code>super()</code> does not look at the class&rsquo;s parent. It looks at the MRO of the <em>instance&rsquo;s actual type</em> and continues from the class where the method is defined. In a diamond that means <code>B</code>&rsquo;s <code>super()</code> can call <code>C</code> &mdash; a class <code>B</code> knows nothing about.",
            code('''
                class Base:
                    def save(self):
                        print("Base.save")

                class Timestamped(Base):
                    def save(self):
                        mro = type(self).__mro__
                        print("Timestamped.save, next is", mro[mro.index(Timestamped) + 1].__name__)
                        super().save()

                class Validated(Base):
                    def save(self):
                        print("Validated.save")
                        super().save()

                class Model(Timestamped, Validated):
                    def save(self):
                        print("Model.save")
                        super().save()

                print([c.__name__ for c in Model.__mro__])
                Model().save()
                print("--- same class, alone ---")
                Timestamped().save()
            '''),
            "<code>Timestamped.save</code> calls <code>super().save()</code> both times, but in a <code>Model</code> the next class is <code>Validated</code>, and in a plain <code>Timestamped</code> it is <code>Base</code>. Every method in the chain runs exactly once, and <code>Base.save</code> runs last. This is <strong>cooperative multiple inheritance</strong>: it works only if every class in the chain calls <code>super()</code>.",
        ),
        section(
            "Cooperative __init__",
            "Constructors are where cooperation usually breaks, because each class wants different arguments and does not know who comes next. The pattern: take the keyword arguments you need, pass the rest on with <code>**kwargs</code>, and let the root class receive nothing extra.",
            code('''
                class Shape:
                    def __init__(self, **kwargs):
                        super().__init__(**kwargs)          # object.__init__ takes no args

                class Colored(Shape):
                    def __init__(self, color="black", **kwargs):
                        self.color = color
                        super().__init__(**kwargs)

                class Named(Shape):
                    def __init__(self, name="?", **kwargs):
                        self.name = name
                        super().__init__(**kwargs)

                class Label(Colored, Named):
                    def __init__(self, text, **kwargs):
                        self.text = text
                        super().__init__(**kwargs)

                l = Label("hi", color="red", name="title")
                print(vars(l))

                try:
                    Label("hi", colour="red")               # typo reaches object.__init__
                except TypeError as e:
                    print("TypeError:", e)
            '''),
            "The typo check is a feature: an unknown keyword travels all the way up and <code>object.__init__</code> rejects it, so misspelt options fail loudly instead of being silently ignored.",
            note("Use keyword arguments throughout a cooperative hierarchy. Positional arguments cannot be routed safely, because no class knows which position belongs to which class in the final MRO."),
        ),
        section(
            "Mixins and why order matters",
            "A mixin is a small class that adds one behaviour and is meant to be combined with others. Because the MRO is ordered left to right, a mixin listed <em>first</em> wraps the classes after it:",
            code('''
                class Store:
                    def get(self, key):
                        return f"value-of-{key}"

                class LoggingMixin:
                    def get(self, key):
                        result = super().get(key)
                        print(f"  log: get({key!r}) -> {result!r}")
                        return result

                class CachingMixin:
                    def get(self, key):
                        cache = self.__dict__.setdefault("_cache", {})
                        if key not in cache:
                            print(f"  miss: {key!r}")
                            cache[key] = super().get(key)
                        return cache[key]

                class LogThenCache(LoggingMixin, CachingMixin, Store): pass
                class CacheThenLog(CachingMixin, LoggingMixin, Store): pass

                for cls in (LogThenCache, CacheThenLog):
                    print(cls.__name__)
                    s = cls()
                    s.get("a"); s.get("a")
            '''),
            "With logging outermost, every call is logged, including cache hits. With caching outermost, hits return before the logger is reached, so only misses are logged. Same classes, different program: the order of bases is part of the design.",
        ),
    ],
    questions=[
        question(
            "What is printed?",
            "medium",
            code('''
                class A:
                    def go(self): return ["A"]
                class B(A):
                    def go(self): return ["B"] + super().go()
                class C(A):
                    def go(self): return ["C"] + super().go()
                class D(B, C):
                    def go(self): return ["D"] + super().go()

                print(D().go())
                print(B().go())
            '''),
            "The MRO of <code>D</code> is <code>D, B, C, A, object</code>. Each <code>super().go()</code> moves one step along <em>that</em> list, so <code>B</code>&rsquo;s super call reaches <code>C</code>, not <code>A</code>. On a plain <code>B</code> instance the MRO is <code>B, A, object</code>, so the same line in <code>B</code> reaches <code>A</code>. Every class runs exactly once, and the shared base <code>A</code> runs once, at the end.",
        ),
        question(
            "Compute the MRO of <code>Z</code> by hand.",
            "hard",
            code('''
                class O: pass
                class A(O): pass
                class B(O): pass
                class C(O): pass
                class D(O): pass
                class E(O): pass
                class K1(A, B, C): pass
                class K2(D, B, E): pass
                class K3(D, A): pass
                class Z(K1, K2, K3): pass

                print(" ".join(k.__name__ for k in Z.__mro__))
            ''', label="the classic example from the C3 paper"),
            "Start with <code>merge([K1 A B C O], [K2 D B E O], [K3 D A O], [K1 K2 K3])</code> and always scan heads from the first list:",
            "<code>K1</code> is in no tail &rarr; take it.<br><code>A</code> is in the tail of <code>[K3 D A O]</code> &rarr; blocked; <code>K2</code> is free &rarr; take it.<br><code>A</code> still blocked; <code>D</code> is in the tail of <code>[K3 D A O]</code> &rarr; blocked; <code>K3</code> is free &rarr; take it.<br><code>A</code> is in the tail of <code>[D A O]</code> &rarr; blocked; <code>D</code> is now free &rarr; take it.<br>Now <code>A</code> is free, then <code>B</code>, <code>C</code>, <code>E</code>, and finally <code>O</code>.",
            "Result: <code>Z K1 K2 K3 D A B C E O</code>. Notice <code>D</code> jumps ahead of <code>A</code> even though <code>K1</code> (listed first) inherits from <code>A</code>: <code>K3</code> said <code>D</code> before <code>A</code>, and C3 keeps every local order.",
        ),
        question(
            "Why does Python refuse to create this class?",
            "hard",
            code('''
                class Base: pass
                class Mixin(Base): pass

                class Widget(Base, Mixin): pass
            ''', raises=True),
            "<code>Widget(Base, Mixin)</code> asks for <code>Base</code> before <code>Mixin</code> (local order). But <code>Mixin</code> is a subclass of <code>Base</code>, so it must come before <code>Base</code> (children before parents). Both rules cannot hold, so there is no linearization. Swap the bases &mdash; <code>class Widget(Mixin, Base)</code> &mdash; or drop <code>Base</code> altogether since <code>Mixin</code> already brings it in.",
        ),
        question(
            "What is the difference between calling <code>Parent.__init__(self)</code> and <code>super().__init__()</code>?",
            "medium",
            "<code>Parent.__init__(self)</code> hard-codes one class; <code>super()</code> follows the MRO. In a diamond, explicit calls run the shared base once per path:",
            code('''
                class Root:
                    def __init__(self): print("Root.__init__")

                class Left(Root):
                    def __init__(self): print("Left"); Root.__init__(self)
                class Right(Root):
                    def __init__(self): print("Right"); Root.__init__(self)
                class Both(Left, Right):
                    def __init__(self):
                        Left.__init__(self)
                        Right.__init__(self)

                Both()
            ''', label="explicit calls: Root runs twice"),
            code('''
                class Root:
                    def __init__(self): print("Root.__init__")

                class Left(Root):
                    def __init__(self): print("Left"); super().__init__()
                class Right(Root):
                    def __init__(self): print("Right"); super().__init__()
                class Both(Left, Right):
                    def __init__(self): super().__init__()

                Both()
            ''', label="super(): each class once"),
            "Running <code>Root.__init__</code> twice can reset state, open two connections, or register a handler twice. Mixing the two styles is the worst case: one explicit call anywhere in the chain breaks it for every class after it.",
        ),
        question(
            "How does zero-argument <code>super()</code> know which class and instance to use?",
            "hard",
            "The compiler sees <code>super</code> (or <code>__class__</code>) used inside a function defined in a class body, and gives that function an implicit closure cell called <code>__class__</code>, filled in with the class once it is created. At run time, <code>super()</code> reads that cell for the class, and the first argument of the current frame for the instance. It is exactly <code>super(__class__, self)</code>.",
            code('''
                class A:
                    def f(self):
                        return super()
                    def g(self):
                        return __class__

                print(A.f.__code__.co_freevars)
                print(A().g())

                def outside(self):
                    return super().__repr__()

                class B:
                    method = outside

                try:
                    B().method()
                except RuntimeError as e:
                    print("RuntimeError:", e)
            '''),
            "So zero-argument <code>super()</code> fails in a function defined outside the class body and attached later, and it binds to the class where the method was <em>written</em> &mdash; which is exactly what makes the MRO walk correct in subclasses.",
        ),
        question(
            "Your mixin&rsquo;s method never runs. What is the most likely reason?",
            "medium",
            "Either the mixin is listed <em>after</em> the base class that defines the same method (so the base is found first and the mixin is never reached), or a class earlier in the MRO overrides the method without calling <code>super()</code>, which ends the chain. Print <code>Cls.__mro__</code> to check the order.",
            code('''
                class Base:
                    def run(self): return "base"

                class AuditMixin:
                    def run(self): return "audited " + super().run()

                class Wrong(Base, AuditMixin): pass
                class Right(AuditMixin, Base): pass

                print(Wrong().run(), "|", Right().run())
            '''),
            "Convention: mixins on the left, the concrete base class on the right, and every overriding method calls <code>super()</code>.",
        ),
    ],
    refs=[
        ("The Python 2.3 Method Resolution Order (C3)", "https://docs.python.org/3/howto/mro.html"),
        ("Python docs: super()", "https://docs.python.org/3/library/functions.html#super"),
        ("Raymond Hettinger — Python’s super() considered super!", "https://rhettinger.wordpress.com/2011/05/26/super-considered-super/"),
    ],
)
