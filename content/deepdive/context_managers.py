from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="context-managers",
    title="Context Managers",
    intro=[
        "A <code>with</code> block guarantees that setup is paired with teardown, whether the block finishes normally, returns early, or raises. Files get closed, locks get released, transactions get committed or rolled back. The object that provides the setup and teardown is a <strong>context manager</strong>, and the protocol behind it is two methods: <code>__enter__</code> and <code>__exit__</code>.",
        "This page covers exactly what <code>with</code> expands to, how exceptions flow through <code>__exit__</code> and how to suppress them, writing managers as classes and as generators, managing a dynamic number of them with <code>ExitStack</code>, and the async version.",
    ],
    sections=[
        section(
            "The protocol, and what with expands to",
            "<code>with EXPR as VAR: BODY</code> is roughly this <code>try/finally</code>, written out by hand:",
            code('''
                import sys

                class Demo:
                    def __enter__(self):
                        print("enter")
                        return "the value bound by 'as'"
                    def __exit__(self, exc_type, exc, tb):
                        print(f"exit  exc_type={exc_type.__name__ if exc_type else None}")
                        return False                 # do not suppress

                # with Demo() as value: print(value)   is equivalent to:
                manager = Demo()
                value = type(manager).__enter__(manager)
                try:
                    print(value)
                except BaseException:
                    if not type(manager).__exit__(manager, *sys.exc_info()):
                        raise
                else:
                    type(manager).__exit__(manager, None, None, None)
            '''),
            "Four details fall out of the expansion:",
            table(
                ["Detail", "Consequence"],
                [
                    ["<code>as</code> binds what <code>__enter__</code> <em>returns</em>", "Not necessarily the manager. <code>open()</code> returns <code>self</code>; a lock returns <code>True</code>; <code>decimal.localcontext()</code> returns a new context"],
                    ["<code>__exit__</code> gets the exception triple", "<code>(None, None, None)</code> on success; type, instance and traceback on failure"],
                    ["A truthy return from <code>__exit__</code> swallows the exception", "Execution continues after the <code>with</code> block"],
                    ["<code>__enter__</code> runs <em>before</em> the <code>try</code>", "If <code>__enter__</code> raises, <code>__exit__</code> is never called"],
                ],
            ),
            "Like other special methods, <code>__enter__</code> and <code>__exit__</code> are looked up on the type, not the instance.",
        ),
        section(
            "A class-based context manager",
            "Class-based managers are the right choice when the manager has state you want to inspect afterwards, or is reusable. A timer is the classic example:",
            code('''
                import time

                class Timer:
                    def __enter__(self):
                        self.start = time.perf_counter()
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        self.elapsed = time.perf_counter() - self.start
                        return False

                with Timer() as t:
                    sum(range(100_000))

                print("measured something:", t.elapsed > 0)
                print("t is still usable after the block:", hasattr(t, "elapsed"))
            '''),
            "Names bound inside or by a <code>with</code> are ordinary local variables &mdash; the block does not create a scope, so <code>t</code> is still there afterwards.",
        ),
        section(
            "Exceptions and suppression",
            "<code>__exit__</code> sees every exception that leaves the block and decides whether it propagates. Returning <code>True</code> suppresses it. Be selective: swallowing everything hides bugs.",
            code('''
                class Ignore:
                    def __init__(self, *types):
                        self.types = types
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc, tb):
                        if exc_type is not None and issubclass(exc_type, self.types):
                            print(f"  suppressed {exc_type.__name__}: {exc}")
                            return True
                        return False

                with Ignore(KeyError):
                    {}["missing"]
                    print("never printed")
                print("carried on after KeyError")

                try:
                    with Ignore(KeyError):
                        1 / 0
                except ZeroDivisionError:
                    print("ZeroDivisionError still propagated")
            '''),
            "The standard library already has this as <code>contextlib.suppress</code>. Note that the rest of the block is skipped &mdash; suppression resumes <em>after</em> the <code>with</code>, not after the failing line.",
            code('''
                import contextlib, os

                with contextlib.suppress(FileNotFoundError):
                    os.remove("does-not-exist.tmp")
                print("no error, no if-exists race")
            '''),
            "That pattern is better than <code>if os.path.exists(p): os.remove(p)</code>, which has a race between the check and the remove.",
        ),
        section(
            "Generator-based: contextlib.contextmanager",
            "For simple setup/teardown pairs, write a generator that yields once. Code before the <code>yield</code> is <code>__enter__</code>, the yielded value is what <code>as</code> binds, and code after is <code>__exit__</code>. If the block raises, the exception is re-raised <em>at the yield</em>.",
            code('''
                from contextlib import contextmanager

                @contextmanager
                def tag(name):
                    print(f"<{name}>")
                    try:
                        yield name.upper()
                    finally:
                        print(f"</{name}>")

                with tag("div") as t:
                    print("  content", t)

                try:
                    with tag("p"):
                        raise ValueError("boom")
                except ValueError as e:
                    print("caught", e)
            '''),
            "The <code>try/finally</code> is not optional. Without it, an exception in the block is raised at the <code>yield</code> and the cleanup line after it never runs:",
            code('''
                from contextlib import contextmanager

                @contextmanager
                def lock_file():
                    print("acquire")
                    yield
                    print("release")          # skipped if the block raises

                try:
                    with lock_file():
                        raise RuntimeError("oops")
                except RuntimeError:
                    pass
                print("the lock was never released")
            ''', label="the bug"),
            table(
                ["", "Class with <code>__enter__</code>/<code>__exit__</code>", "<code>@contextmanager</code> generator"],
                [
                    ["Brevity", "More boilerplate", "Short; setup and teardown read top to bottom"],
                    ["State after the block", "Natural (attributes on <code>self</code>)", "Awkward (yield a mutable object)"],
                    ["Reusable / re-entrant", "Can be", "Single use: a generator can only run once"],
                    ["Suppressing exceptions", "Return <code>True</code>", "Catch it around the <code>yield</code> and do not re-raise"],
                    ["Also works as a decorator", "Subclass <code>ContextDecorator</code>", "Yes, automatically"],
                ],
            ),
        ),
        section(
            "Several managers, and a dynamic number: ExitStack",
            "One <code>with</code> can hold several managers; they are entered left to right and exited right to left. Since 3.10 you can wrap them in parentheses across lines.",
            code('''
                from contextlib import contextmanager

                @contextmanager
                def res(name):
                    print("open ", name)
                    try:
                        yield name
                    finally:
                        print("close", name)

                with (
                    res("db") as db,
                    res("cache") as cache,
                ):
                    print("using", db, cache)
            '''),
            "When the number of resources is only known at run time, use <code>ExitStack</code>. It is a context manager that holds other context managers, and unwinds all of them &mdash; even if opening the fourth one fails after three succeeded.",
            code('''
                from contextlib import ExitStack, contextmanager

                @contextmanager
                def res(name):
                    if name == "bad":
                        raise OSError(f"cannot open {name}")
                    print("open ", name)
                    try:
                        yield name
                    finally:
                        print("close", name)

                def open_all(names):
                    with ExitStack() as stack:
                        handles = [stack.enter_context(res(n)) for n in names]
                        stack.callback(print, "callback runs too")
                        print("all open:", handles)

                open_all(["a", "b", "c"])
                print("---")
                try:
                    open_all(["a", "b", "bad", "d"])
                except OSError as e:
                    print("OSError:", e)
            '''),
            "<code>stack.pop_all()</code> transfers everything to a new stack, which is the idiom for &ldquo;open several resources, and only if all succeed, hand them to the caller&rdquo;.",
        ),
        section(
            "Async context managers",
            "<code>async with</code> uses <code>__aenter__</code> and <code>__aexit__</code>, which are coroutines, so setup and teardown can await &mdash; opening a connection, starting a transaction, acquiring an <code>asyncio.Lock</code>.",
            code('''
                import asyncio
                from contextlib import asynccontextmanager

                class Connection:
                    async def __aenter__(self):
                        await asyncio.sleep(0)            # pretend network I/O
                        print("connected")
                        return self
                    async def __aexit__(self, exc_type, exc, tb):
                        await asyncio.sleep(0)
                        print("disconnected")
                        return False

                @asynccontextmanager
                async def transaction(conn):
                    print("  BEGIN")
                    try:
                        yield
                        print("  COMMIT")
                    except Exception:
                        print("  ROLLBACK")
                        raise

                async def main():
                    async with Connection() as conn:
                        async with transaction(conn):
                            print("  insert row")

                asyncio.run(main())
            '''),
        ),
        section(
            "Useful managers from the standard library",
            table(
                ["Manager", "Sets up", "Tears down"],
                [
                    ["<code>open(...)</code>", "Opens a file", "Closes it"],
                    ["<code>threading.Lock()</code>", "Acquires", "Releases"],
                    ["<code>contextlib.suppress(*exc)</code>", "&mdash;", "Swallows the listed exceptions"],
                    ["<code>contextlib.redirect_stdout(f)</code>", "Points <code>sys.stdout</code> at <code>f</code>", "Restores it"],
                    ["<code>contextlib.chdir(path)</code> (3.11+)", "Changes directory", "Changes back"],
                    ["<code>contextlib.nullcontext(x)</code>", "Nothing; <code>as</code> gets <code>x</code>", "Nothing &mdash; for optional managers"],
                    ["<code>contextlib.closing(obj)</code>", "&mdash;", "Calls <code>obj.close()</code>"],
                    ["<code>decimal.localcontext()</code>", "Copies the decimal context", "Restores precision and rounding"],
                    ["<code>tempfile.TemporaryDirectory()</code>", "Creates a directory", "Deletes it and its contents"],
                    ["<code>unittest.mock.patch(...)</code>", "Replaces an attribute", "Restores the original"],
                ],
            ),
            code('''
                import io, contextlib, decimal

                buffer = io.StringIO()
                with contextlib.redirect_stdout(buffer):
                    print("captured, not shown")
                print("captured:", repr(buffer.getvalue()))

                with decimal.localcontext() as ctx:
                    ctx.prec = 5
                    print(decimal.Decimal(1) / decimal.Decimal(7))
                print(decimal.Decimal(1) / decimal.Decimal(7))

                def process(path=None):
                    cm = open(path) if path else contextlib.nullcontext(io.StringIO("default"))
                    with cm as f:
                        return f.read()
                print(process())
            '''),
        ),
    ],
    questions=[
        question(
            "If <code>__enter__</code> raises, is <code>__exit__</code> called? What if the body raises and then <code>__exit__</code> raises too?",
            "medium",
            "No. <code>__enter__</code> runs before the implicit <code>try</code>, so a failing <code>__enter__</code> means the resource was never acquired and there is nothing to exit. Any partial setup must be cleaned up inside <code>__enter__</code> itself.",
            "If the body raises and <code>__exit__</code> also raises, the new exception replaces the original, with the original attached as <code>__context__</code> (&ldquo;During handling of the above exception, another exception occurred&rdquo;).",
            code('''
                class Fragile:
                    def __enter__(self):
                        return self
                    def __exit__(self, *exc):
                        raise RuntimeError("cleanup failed")

                try:
                    with Fragile():
                        raise ValueError("original problem")
                except Exception as e:
                    print(type(e).__name__, "-", e)
                    print("context:", repr(e.__context__))
            '''),
            "That is why teardown code should be as simple and failure-proof as possible, and why <code>ExitStack</code> goes to great lengths to keep running every remaining callback even when one fails.",
        ),
        question(
            "Write a transaction context manager that commits on success and rolls back on any exception.",
            "hard",
            "Decide on the path by whether an exception arrived, and do not suppress it: the caller needs to know the transaction failed.",
            code('''
                class FakeDB:
                    def __init__(self): self.data, self.pending = {}, None
                    def begin(self): self.pending = dict(self.data)
                    def commit(self): self.data, self.pending = self.pending, None
                    def rollback(self): self.pending = None

                class transaction:
                    def __init__(self, db): self.db = db
                    def __enter__(self):
                        self.db.begin()
                        return self.db.pending
                    def __exit__(self, exc_type, exc, tb):
                        if exc_type is None:
                            self.db.commit()
                        else:
                            self.db.rollback()
                        return False                       # let the error propagate

                db = FakeDB()
                with transaction(db) as t:
                    t["alice"] = 100
                print(db.data)

                try:
                    with transaction(db) as t:
                        t["alice"] = 0
                        raise ValueError("payment declined")
                except ValueError as e:
                    print("failed:", e, "| data unchanged:", db.data)
            '''),
            "Follow-ups: nested transactions (savepoints &mdash; keep a depth counter and only commit at depth zero), and what happens if <code>commit()</code> itself raises (the exception propagates from <code>__exit__</code>, which is correct: the caller must know).",
        ),
        question(
            "Why must a <code>@contextmanager</code> generator wrap its <code>yield</code> in <code>try/finally</code>?",
            "medium",
            "Because when the <code>with</code> body raises, <code>contextmanager</code> calls <code>generator.throw(exc)</code>, and the exception appears to come from the <code>yield</code> line. Anything after the <code>yield</code> that is not in a <code>finally</code> (or an <code>except</code>) is skipped, so the teardown never happens. A <code>finally</code> runs on success, on exceptions, and even when the block exits via <code>return</code> or <code>break</code>.",
            "If you want to <em>suppress</em> an exception in a generator-based manager, catch it around the <code>yield</code> and do not re-raise. If you catch it and forget to re-raise when you did not mean to suppress, you have silently swallowed errors &mdash; a surprisingly common bug.",
        ),
        question(
            "How do you open an unknown number of files safely, so that all are closed even if opening one of them fails?",
            "hard",
            "<code>contextlib.ExitStack</code>. Each <code>enter_context</code> call enters a manager and registers its exit. If a later <code>open</code> raises, the <code>with ExitStack()</code> block unwinds, closing every file opened so far in reverse order.",
            code('''
                import contextlib, pathlib, tempfile

                with tempfile.TemporaryDirectory() as d:
                    paths = [pathlib.Path(d, f"part{i}.txt") for i in range(3)]
                    for i, p in enumerate(paths):
                        p.write_text(f"chunk {i}\\n")

                    with contextlib.ExitStack() as stack:
                        files = [stack.enter_context(open(p)) for p in paths]
                        merged = "".join(f.read() for f in files)
                    print(merged, end="")
                    print("all closed:", all(f.closed for f in files))

                    missing = paths + [pathlib.Path(d, "nope.txt")]
                    try:
                        with contextlib.ExitStack() as stack:
                            files = []
                            for p in missing:
                                files.append(stack.enter_context(open(p)))
                    except FileNotFoundError:
                        print("failed on the 4th; first 3 closed:", all(f.closed for f in files))
            '''),
            "Writing this with nested <code>with</code> statements is impossible for an unknown count, and doing it with a manual list and <code>try/finally</code> is easy to get subtly wrong (a failing <code>close</code> can skip the rest).",
        ),
        question(
            "Can a context manager be reused or re-entered? Give examples of each.",
            "hard",
            "Three categories:",
            "<strong>Single-use</strong>: can be entered once. Generator-based managers (<code>@contextmanager</code>) &mdash; the generator has already run &mdash; and file objects returned by <code>open</code>, which are closed after the first block.<br><strong>Reusable</strong>: can be used in several <code>with</code> statements one after another, but not nested. <code>threading.Lock</code> is reusable; nesting it on the same thread deadlocks.<br><strong>Re-entrant</strong>: can be nested inside itself. <code>threading.RLock</code>, <code>contextlib.suppress</code>, <code>redirect_stdout</code>.",
            code('''
                from contextlib import contextmanager
                import threading

                @contextmanager
                def once():
                    yield

                cm = once()
                with cm: pass
                try:
                    with cm: pass
                except (RuntimeError, AttributeError) as e:
                    print("second use failed with", type(e).__name__)

                rlock = threading.RLock()
                with rlock:
                    with rlock:
                        print("RLock nested fine")

                lock = threading.Lock()
                with lock:
                    print("Lock acquired again while held?", lock.acquire(blocking=False))
            '''),
        ),
        question(
            "Implement a timing context manager that also works as a decorator.",
            "medium",
            "Subclass <code>contextlib.ContextDecorator</code>: it adds a <code>__call__</code> that wraps the function body in <code>with self:</code>. Generator managers from <code>@contextmanager</code> get this for free.",
            code('''
                import time
                from contextlib import ContextDecorator

                class timed(ContextDecorator):
                    def __init__(self, label):
                        self.label = label
                    def __enter__(self):
                        self.start = time.perf_counter()
                        return self
                    def __exit__(self, *exc):
                        ms = (time.perf_counter() - self.start) * 1000
                        print(f"{self.label}: finished, under 1000 ms: {ms < 1000}")
                        return False

                with timed("block"):
                    sum(range(10_000))

                @timed("function")
                def work():
                    return sum(range(10_000))

                print(work())
            '''),
            "One subtlety: when used as a decorator the same manager instance is entered on every call, so it must not keep per-call state that breaks under recursion or concurrent calls.",
        ),
    ],
    refs=[
        ("PEP 343 — The with statement", "https://peps.python.org/pep-0343/"),
        ("Python docs: contextlib", "https://docs.python.org/3/library/contextlib.html"),
        ("Python docs: With statement context managers", "https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers"),
    ],
)
