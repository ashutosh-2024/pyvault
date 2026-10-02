from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="memory",
    title="Memory Management",
    intro=[
        "Python frees you from <code>malloc</code> and <code>free</code>, but not from memory. CPython uses two mechanisms together: <strong>reference counting</strong>, which frees almost everything the instant it becomes unreachable, and a <strong>cycle collector</strong>, which cleans up the objects reference counting cannot. Underneath both sits a specialised allocator for small objects.",
        "Knowing how these fit together explains why <code>__del__</code> runs when it does, why a program can hold on to memory after you delete a huge list, why <code>lru_cache</code> on a method leaks, and what <code>__slots__</code> actually saves.",
    ],
    sections=[
        section(
            "Names are references, objects carry a count",
            "A variable is a name bound to an object. Assignment never copies; it adds another reference. Every object stores how many references point at it, and <code>sys.getrefcount</code> reports that number &mdash; plus whatever temporary reference the call itself creates.",
            code('''
                import sys

                data = [1, 2, 3]
                print(sys.getrefcount(data))

                alias = data
                box = [data, data]
                print(sys.getrefcount(data))

                del alias
                box.clear()
                print(sys.getrefcount(data))
            '''),
            "Each name, container slot, attribute and stack frame that refers to an object counts. <code>del</code> removes a <em>name</em> and decrements the count; it does not destroy the object unless that was the last reference.",
            caveat("The absolute numbers depend on the interpreter version &mdash; newer CPythons avoid some temporary references altogether. Compare counts before and after an operation rather than reading meaning into the raw value."),
        ),
        section(
            "Deterministic destruction",
            "When a count hits zero, CPython deallocates the object immediately &mdash; inside the operation that dropped the last reference. That is why this prints in exactly this order:",
            code('''
                class Resource:
                    def __init__(self, name):
                        self.name = name
                        print("open ", name)
                    def __del__(self):
                        print("close", self.name)

                def work():
                    r = Resource("temp")
                    print("working")
                # r goes out of scope when work() returns

                work()
                print("after work()")

                a = Resource("a")
                a = Resource("b")        # rebinding drops the last reference to "a"
                print("end of script")
            '''),
            "Many Python programs quietly rely on this &mdash; files closing when the variable goes away, for instance. Do not. PyPy, GraalPy and the free-threaded build&rsquo;s deferred reference counting do not all free at the same moment, and an object caught in a reference cycle is not freed by counting at all. Use <code>with</code> for anything that must be released at a known point.",
        ),
        section(
            "Reference cycles and the garbage collector",
            "Reference counting has one blind spot: objects that refer to each other. When the outside world lets go, each member of the cycle still has a count of at least one, so nothing is freed.",
            code('''
                import gc, weakref

                class Node:
                    pass

                gc.collect()                   # start from a clean slate
                gc.disable()                   # so the collector cannot step in early

                a, b = Node(), Node()
                a.other, b.other = b, a        # a <-> b
                probe = weakref.ref(a)         # watches a without keeping it alive

                del a, b
                print("alive after del:       ", probe() is not None)

                found = gc.collect()
                print("alive after gc.collect:", probe() is not None)
                print("unreachable objects found:", found)
            '''),
            "The cycle collector finds garbage by elimination. For every container object it tracks (lists, dicts, class instances &mdash; not ints or strings), it subtracts the references that come from <em>other tracked objects</em>. Whatever still has a positive count is referenced from outside and is alive, along with everything reachable from it. The rest is an isolated cycle, and it is freed.",
            "Since Python 3.4 (PEP 442), cycles containing objects with <code>__del__</code> are collected too; before that they were parked in <code>gc.garbage</code> forever.",
        ),
        section(
            "Generations, thresholds and incremental collection",
            "Scanning every object on every allocation would be ruinous, so the collector uses the <em>generational hypothesis</em>: most objects die young. New containers start in the young generation, which is scanned often; survivors get promoted and scanned rarely.",
            code('''
                import gc
                print("thresholds:", gc.get_threshold())
                print("tracked int:", gc.is_tracked(42))
                print("tracked str:", gc.is_tracked("hello"))
                print("tracked []: ", gc.is_tracked([]))
                print("tracked obj:", gc.is_tracked(object.__new__(type("T", (), {}))))
            '''),
            "Atomic objects like ints and strings cannot hold references to other objects, so they can never be part of a cycle and the collector never looks at them. Only containers are tracked.",
            "The first threshold is how many net container allocations trigger a young collection. Python 3.14 replaced the classic three-generation collector with an <em>incremental</em> one: a young generation plus an old generation that is scanned a slice at a time, so a program with millions of long-lived objects no longer suffers one huge full-collection pause.",
            table(
                ["Tool", "What it does", "When to use it"],
                [
                    ["<code>gc.collect()</code>", "Run a full collection now, return objects found", "Tests, and after tearing down a big object graph"],
                    ["<code>gc.disable()</code>", "Stop automatic cycle collection (refcounting still works)", "Short batch jobs that create no cycles; latency-critical sections"],
                    ["<code>gc.freeze()</code>", "Move all current objects to a permanent generation that is never scanned", "Pre-fork servers: stops the GC touching pages the children share"],
                    ["<code>gc.set_threshold()</code>", "Collect less often", "Allocation-heavy programs where GC time shows up in profiles"],
                ],
            ),
        ),
        section(
            "How objects are allocated: pymalloc",
            "Python allocates huge numbers of small, short-lived objects. Calling the system <code>malloc</code> for each would be slow, so CPython routes every request of 512 bytes or less through <strong>pymalloc</strong>:",
            table(
                ["Layer", "Size", "Holds"],
                [
                    ["Arena", "1 MiB, from the OS via <code>mmap</code>", "Many pools"],
                    ["Pool", "16 KiB", "Blocks of one size class only"],
                    ["Block", "A multiple of 16 bytes, up to 512", "One object"],
                ],
            ),
            "Freed blocks go back on their pool&rsquo;s free list and are reused immediately by the next object of that size, which is very fast. Larger requests go straight to the system allocator.",
            "The catch: an arena is returned to the operating system only when <em>every</em> block in it is free. Build a million small objects, delete all but one in each arena, and the process keeps nearly all that memory. That is fragmentation, and it is why resident memory often does not drop after a big <code>del</code>.",
            "Containers also over-allocate so that appends are cheap on average. Watch a list&rsquo;s size step up only occasionally:",
            code('''
                import sys

                items, last = [], None
                for i in range(20):
                    size = sys.getsizeof(items)
                    if size != last:
                        print(f"len={len(items):2}  bytes={size}")
                        last = size
                    items.append(i)
            '''),
            "<code>sys.getsizeof</code> is <em>shallow</em>: it counts the list&rsquo;s pointer array, not the objects the pointers lead to. A list of a thousand 1&nbsp;KB strings is reported as about 8&nbsp;KB.",
        ),
        section(
            "Sharing, caching and immortal objects",
            "CPython avoids creating objects it can share. Integers from -5 to 256 are pre-built singletons, and short identifier-like strings are <em>interned</em> so equal ones are the same object.",
            code('''
                import sys

                a, b = int("256"), int("256")
                c, d = int("257"), int("257")
                print("256 is 256:", a is b)
                print("257 is 257:", c is d)

                s1 = "".join(["hello", "_", "world"])
                s2 = "hello_world"
                print("equal:", s1 == s2, " same object:", s1 is s2)
                print("after intern:", sys.intern(s1) is s2)
            '''),
            "Since 3.12 (PEP 683) objects like <code>None</code>, <code>True</code> and the small ints are <strong>immortal</strong>: their reference count is pinned to a huge sentinel and increments are skipped. That avoids writing to them from every thread and every forked child, which matters for both the free-threaded build and copy-on-write memory sharing.",
            code('''
                import sys
                print(sys.getrefcount(None))
                print(sys.getrefcount(7))
                print(sys._is_immortal(None), sys._is_immortal([]))
            '''),
            caveat("The small-int range, string interning and immortality are CPython implementation details. Never use <code>is</code> to compare numbers or strings in real code."),
        ),
        section(
            "Measuring and cutting memory: __slots__ and tracemalloc",
            "By default every instance carries a <code>__dict__</code> so you can add attributes at any time. When you create millions of small objects, that dict is most of the cost. <code>__slots__</code> replaces it with fixed storage.",
            code('''
                import tracemalloc

                class Plain:
                    def __init__(self, x, y):
                        self.x, self.y = x, y

                class Slotted:
                    __slots__ = ("x", "y")
                    def __init__(self, x, y):
                        self.x, self.y = x, y

                def measure(cls):
                    tracemalloc.start()
                    objs = [cls(i, i) for i in range(50_000)]
                    size, _ = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    return size

                plain, slotted = measure(Plain), measure(Slotted)
                print("slots use less memory:", slotted < plain)
                print("saving is over 30%:", slotted < plain * 0.7)

                s = Slotted(1, 2)
                try:
                    s.z = 3
                except AttributeError as e:
                    print("AttributeError:", e)
            '''),
            "<code>tracemalloc</code> records the Python stack for every allocation, so it can tell you <em>which line</em> is holding memory. Taking two snapshots and diffing them is the standard way to find a leak:",
            code('''
                import tracemalloc

                cache = []
                def leaky(n):
                    cache.append(bytearray(1000))   # a new 1 KB buffer every call

                tracemalloc.start()
                before = tracemalloc.take_snapshot()
                for i in range(2000):
                    leaky(i)
                after = tracemalloc.take_snapshot()

                top = after.compare_to(before, "lineno")[0]
                frame = top.traceback[0]
                print("biggest growth at line", frame.lineno)
                print(f"grew by about {top.size_diff / 1e6:.1f} MB")
            '''),
            note("Reach for <code>__slots__</code> when you have many instances of a class with a fixed set of attributes. It also blocks typos like <code>self.nmae = ...</code>, but you lose <code>__dict__</code>, and weak references unless you add <code>__weakref__</code> to the slots."),
        ),
        section(
            "Weak references",
            "A weak reference points at an object without adding to its count. When the last strong reference goes, the object is freed and the weak reference returns <code>None</code>. This is the tool for caches and observer lists that should not keep things alive.",
            code('''
                import weakref

                class Image:
                    def __init__(self, name):
                        self.name = name

                cache = weakref.WeakValueDictionary()

                img = Image("logo.png")
                cache["logo"] = img
                print("cached:", "logo" in cache)

                del img                          # last strong reference gone
                print("cached after del:", "logo" in cache)
            '''),
            table(
                ["Tool", "Holds keys", "Holds values", "Typical use"],
                [
                    ["<code>weakref.ref</code>", "&mdash;", "weakly", "Back-pointer from child to parent"],
                    ["<code>WeakValueDictionary</code>", "strongly", "weakly", "Cache of objects owned elsewhere"],
                    ["<code>WeakKeyDictionary</code>", "weakly", "strongly", "Attaching extra data to objects you do not own"],
                    ["<code>weakref.finalize</code>", "&mdash;", "&mdash;", "Reliable cleanup callback; safer than <code>__del__</code>"],
                ],
            ),
        ),
    ],
    questions=[
        question(
            "What is the difference between <code>del x</code> and freeing the object?",
            "medium",
            "<code>del x</code> unbinds the name <code>x</code> and decrements the object&rsquo;s reference count. The object is freed only if that was the last reference. If a list, a closure, a global or a cycle still refers to it, it lives on.",
            code('''
                class Big:
                    def __del__(self):
                        print("freed")

                b = Big()
                keep = [b]
                del b
                print("after del b")
                keep.clear()
                print("after clear")
            '''),
        ),
        question(
            "Why does <code>functools.lru_cache</code> on a method leak memory?",
            "hard",
            "The cache lives on the <em>function</em>, which lives on the class, which lives for the whole program. <code>self</code> is part of every cache key, so the cache holds a strong reference to every instance that ever called the method. Those instances are never freed.",
            code('''
                import functools, gc, weakref

                class Report:
                    @functools.lru_cache(maxsize=None)
                    def total(self):
                        return 42

                r = Report()
                r.total()
                probe = weakref.ref(r)
                del r
                gc.collect()
                print("instance still alive:", probe() is not None)
                print(Report.total.cache_info())
            ''', label="the leak"),
            "Fixes: use <code>functools.cached_property</code> (stores the result on the instance, so it dies with it), keep the cache per instance in <code>__init__</code>, or move the cached computation to a module-level function whose arguments are plain values rather than <code>self</code>.",
            code('''
                import functools, gc, weakref

                class Report:
                    @functools.cached_property
                    def total(self):
                        return 42

                r = Report()
                r.total
                probe = weakref.ref(r)
                del r
                gc.collect()
                print("instance still alive:", probe() is not None)
            ''', label="the fix"),
        ),
        question(
            "You delete a list of ten million objects but the process&rsquo;s memory barely drops. Why?",
            "hard",
            "Several reasons, usually together:",
            "<strong>Fragmentation in pymalloc</strong> &mdash; an arena goes back to the OS only when every block in it is free. A few survivors scattered across arenas pin them all.<br><strong>Free lists and caches</strong> &mdash; CPython keeps freed floats, tuples, frames and so on for reuse.<br><strong>The system allocator</strong> &mdash; large blocks freed with <code>free()</code> are often retained by libc for the next <code>malloc</code>.<br><strong>Something still references it</strong> &mdash; check with <code>gc.get_referrers</code> or a <code>weakref</code> probe.",
            "The memory is not lost &mdash; the next allocations reuse it. If peak memory is the problem, avoid materialising it: stream with generators, use <code>array</code> or NumPy for numbers (one buffer instead of millions of objects), or do the heavy work in a child process that exits and hands back only the result.",
        ),
        question(
            "How would you find a memory leak in a long-running Python service?",
            "medium",
            "Confirm it first: plot RSS over time under steady load. A leak climbs forever; fragmentation plateaus. Then:",
            "1. Take two <code>tracemalloc</code> snapshots some minutes apart and <code>compare_to</code> by line &mdash; the top entries show which code is allocating memory that is not freed.<br>2. Count live objects by type (<code>gc.get_objects()</code>, or <code>objgraph.show_growth()</code>) to see what kind of object is piling up.<br>3. Follow <code>gc.get_referrers</code> back from one of those objects to see who is holding it.",
            "The usual suspects are unbounded module-level caches and dicts, <code>lru_cache(maxsize=None)</code> on methods, listeners registered and never removed, exceptions stored with their tracebacks (which hold every frame and its locals), and threads that never exit.",
        ),
        question(
            "What does <code>sys.getsizeof</code> not tell you?",
            "medium",
            "It reports the size of the object itself &mdash; not what it refers to. A container&rsquo;s size is its header plus its pointer array.",
            code('''
                import sys

                small = ["a" for _ in range(1000)]
                large = ["a" * 10_000 for _ in range(1000)]
                print(sys.getsizeof(small) == sys.getsizeof(large))

                def deep_size(obj, seen=None):
                    seen = set() if seen is None else seen
                    if id(obj) in seen:
                        return 0
                    seen.add(id(obj))
                    size = sys.getsizeof(obj)
                    if isinstance(obj, (list, tuple, set)):
                        size += sum(deep_size(x, seen) for x in obj)
                    elif isinstance(obj, dict):
                        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
                    return size

                print(deep_size(large) > 100 * deep_size(small))
            '''),
            "The <code>seen</code> set matters: without it, shared objects are counted many times and cycles recurse forever.",
        ),
        question(
            "What are immortal objects, and why did CPython add them?",
            "hard",
            "PEP 683 (3.12) marks some objects &mdash; <code>None</code>, <code>True</code>, <code>False</code>, small ints, interned strings created at start-up &mdash; with a special reference count that is never incremented or decremented. They are never freed.",
            "Two problems went away. Every <code>return None</code> used to write to <code>None</code>&rsquo;s refcount; after a <code>fork</code>, that write copied the memory page into every child, defeating copy-on-write sharing (Instagram&rsquo;s servers were the motivating case). And in the free-threaded build, thousands of threads writing to the same hot counters would contend on one cache line. Immortal objects are read-only in practice, so both costs vanish.",
        ),
    ],
    refs=[
        ("Python docs: gc — Garbage Collector interface", "https://docs.python.org/3/library/gc.html"),
        ("Python docs: tracemalloc", "https://docs.python.org/3/library/tracemalloc.html"),
        ("CPython internals: garbage collector design", "https://github.com/python/cpython/blob/main/InternalDocs/garbage_collector.md"),
        ("PEP 683 — Immortal objects", "https://peps.python.org/pep-0683/"),
    ],
)
