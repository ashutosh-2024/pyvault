from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="generators",
    title="Generators and Iterators",
    intro=[
        "Every <code>for</code> loop in Python runs on two small methods: <code>__iter__</code> and <code>__next__</code>. Lists, dicts, files, ranges, database cursors and <code>zip</code> objects all speak this one protocol, and that is why they all work in the same loops, comprehensions and built-ins.",
        "A <strong>generator</strong> is the easiest way to implement the protocol: a function that can pause at <code>yield</code> and resume later with its local variables intact. That single feature gives you lazy pipelines that use constant memory, infinite sequences, two-way coroutines and, historically, the whole foundation <code>async</code>/<code>await</code> was built on.",
    ],
    sections=[
        section(
            "The iterator protocol",
            "An <strong>iterable</strong> is anything with <code>__iter__</code> that returns an iterator. An <strong>iterator</strong> has <code>__next__</code>, which returns the next value or raises <code>StopIteration</code> when there are none left. A <code>for</code> loop is just those two calls plus a <code>try</code>:",
            code('''
                nums = [10, 20, 30]

                # what `for x in nums: print(x)` actually does
                it = iter(nums)                 # nums.__iter__()
                while True:
                    try:
                        x = next(it)            # it.__next__()
                    except StopIteration:
                        break
                    print(x)

                print(type(nums).__name__, "->", type(it).__name__)
                print(iter(it) is it)           # an iterator is its own iterator
            '''),
            "The same protocol is behind unpacking, <code>in</code>, <code>sum</code>, <code>sorted</code>, <code>list()</code>, <code>dict()</code>, <code>zip</code>, <code>enumerate</code>, <code>str.join</code> and <code>yield from</code>. Implement it once and your object works with all of them.",
            table(
                ["", "Iterable", "Iterator"],
                [
                    ["Has", "<code>__iter__</code> returning a <em>new</em> iterator", "<code>__next__</code>, and <code>__iter__</code> returning <code>self</code>"],
                    ["Examples", "<code>list</code>, <code>dict</code>, <code>str</code>, <code>range</code>", "<code>iter([...])</code>, files, generators, <code>map</code>, <code>zip</code>"],
                    ["Loop twice?", "Yes, each loop gets a fresh iterator", "No, the second loop sees nothing"],
                    ["Supports <code>len()</code> / indexing?", "Often", "Almost never"],
                ],
            ),
        ),
        section(
            "Iterators are single use",
            "Because an iterator is its own iterator, a second loop over it continues where the first one stopped &mdash; usually at the end. This bites when a function receives a <code>map</code>, <code>zip</code>, file or generator and iterates it twice.",
            code('''
                squares = map(lambda x: x * x, [1, 2, 3, 4])
                print(sum(squares))      # consumes everything
                print(sum(squares))      # nothing left
                print(list(squares))

                def mean(values):
                    return sum(values) / len(list(values))

                try:
                    print(mean(x for x in [2, 4, 6]))
                except ZeroDivisionError as e:
                    print("ZeroDivisionError:", e)   # len saw an exhausted generator
            '''),
            "The second <code>list(values)</code> inside <code>mean</code> found nothing, so the length was 0. Two fixes: materialise once (<code>values = list(values)</code>), or write the function to make a single pass.",
            code('''
                def mean(values):
                    total = count = 0
                    for v in values:             # one pass, works for any iterable
                        total += v
                        count += 1
                    return total / count

                print(mean(x for x in [2, 4, 6]), mean([1, 2]), mean(range(101)))
            '''),
            note("If a function needs two passes, either accept a <code>Sequence</code> and say so, or call <code>list()</code> on the argument first. Never assume an iterable can be replayed."),
        ),
        section(
            "Generator functions: pause and resume",
            "Any function containing <code>yield</code> is a generator function. Calling it runs <em>none</em> of its body: it returns a generator object. Each <code>next()</code> runs the body until the next <code>yield</code>, hands that value out, and freezes the frame &mdash; locals, the instruction pointer, any open <code>try</code> blocks &mdash; until the next call.",
            code('''
                import inspect

                def countdown(n):
                    print("  started")
                    while n > 0:
                        print(f"  yielding {n}")
                        yield n
                        n -= 1
                    print("  finished")

                gen = countdown(2)
                print("created:", inspect.getgeneratorstate(gen))
                print("got", next(gen))
                print("state:", inspect.getgeneratorstate(gen))
                print("got", next(gen))
                try:
                    next(gen)
                except StopIteration:
                    print("StopIteration")
                print("state:", inspect.getgeneratorstate(gen))
            '''),
            "Nothing was printed until the first <code>next()</code>. That laziness is the point: work happens only when a value is asked for, and only as much as is asked for.",
            "A <code>return value</code> inside a generator ends it, and the value travels on the <code>StopIteration</code> exception as <code>.value</code>. Loops ignore it; <code>yield from</code> (below) picks it up.",
        ),
        section(
            "Laziness: constant memory and infinite sequences",
            "A list comprehension builds every element up front. A generator expression &mdash; same syntax in parentheses &mdash; produces them one at a time. The memory difference is the whole list versus one frame:",
            code('''
                import sys

                as_list = [x * x for x in range(1_000_000)]
                as_gen = (x * x for x in range(1_000_000))

                print(f"list: {sys.getsizeof(as_list):>10,} bytes (just the pointer array)")
                print(f"gen:  {sys.getsizeof(as_gen):>10,} bytes")
                print(sum(as_gen) == sum(as_list))
            '''),
            "Because nothing is computed ahead of time, a generator can be infinite. You take what you need with <code>itertools.islice</code> or stop on a condition:",
            code('''
                from itertools import islice, count, takewhile

                def fibonacci():
                    a, b = 0, 1
                    while True:                 # never ends: fine, it is lazy
                        yield a
                        a, b = b, a + b

                print(list(islice(fibonacci(), 10)))
                print(list(takewhile(lambda x: x < 100, fibonacci())))
                print(next(n for n in count(1) if n * n > 500))
            '''),
            "Chaining generators gives a <strong>pipeline</strong>: each stage pulls one item from the previous stage, so only one item is in flight at a time no matter how big the input is. This is how you process a 50 GB log file in a few kilobytes of memory.",
            code('''
                lines = [
                    "INFO start", "ERROR disk full", "INFO retry",
                    "ERROR disk full", "ERROR timeout", "INFO done",
                ]

                def read(source):
                    for line in source:
                        print(f"  read  {line!r}")
                        yield line

                errors = (l for l in read(lines) if l.startswith("ERROR"))
                messages = (l.split(" ", 1)[1] for l in errors)

                first_two = [next(messages), next(messages)]
                print(first_two)               # stopped reading after the 4th line
            '''),
            caveat("<code>sys.getsizeof</code> on a list counts only its array of pointers, not the int objects it points at. The real difference here is larger than the number shown."),
        ),
        section(
            "Two-way generators: send, throw, close",
            "<code>yield</code> is an expression. <code>gen.send(value)</code> resumes the generator and makes the paused <code>yield</code> evaluate to <code>value</code>. The first resume must be <code>next(gen)</code> (or <code>send(None)</code>) to run up to the first <code>yield</code> &mdash; this is called <em>priming</em>.",
            code('''
                def running_average():
                    total = count = 0
                    average = None
                    while True:
                        value = yield average      # hand out average, receive value
                        total += value
                        count += 1
                        average = total / count

                avg = running_average()
                next(avg)                          # prime: run to the first yield
                for v in (10, 20, 60):
                    print(f"sent {v:>2} -> average {avg.send(v)}")
            '''),
            "<code>gen.throw(exc)</code> raises an exception <em>at the paused yield</em>, so the generator can handle it. <code>gen.close()</code> throws <code>GeneratorExit</code>, which runs <code>finally</code> blocks &mdash; generators clean up after themselves.",
            code('''
                def worker():
                    try:
                        while True:
                            try:
                                job = yield
                                print(f"  processing {job}")
                            except ValueError as e:
                                print(f"  recovered from: {e}")
                    finally:
                        print("  cleanup ran")

                w = worker(); next(w)
                w.send("job-1")
                w.throw(ValueError("bad input"))   # handled inside, generator lives on
                w.send("job-2")
                w.close()                          # GeneratorExit -> finally
                print("closed:", w.gi_frame is None)
            '''),
            note("This is how coroutines worked before <code>async def</code>: a scheduler sent results into paused generators. <code>await</code> is built on the same machinery &mdash; see the async internals topic."),
        ),
        section(
            "yield from: delegating to a sub-generator",
            "<code>yield from sub</code> passes every value of <code>sub</code> straight through, forwards <code>send</code>/<code>throw</code> to it, and evaluates to the sub-generator's <code>return</code> value. It is what lets you split a generator into helper generators.",
            code('''
                def flatten(items):
                    for x in items:
                        if isinstance(x, list):
                            yield from flatten(x)     # recurse, values pass straight up
                        else:
                            yield x

                print(list(flatten([1, [2, [3, 4], 5], [[6]], 7])))

                def read_block(lines):
                    count = 0
                    for line in lines:
                        if line == "END":
                            return count              # becomes the value of yield from
                        count += 1
                        yield line.upper()

                def read_all(lines):
                    it = iter(lines)
                    n1 = yield from read_block(it)
                    n2 = yield from read_block(it)
                    yield f"blocks had {n1} and {n2} lines"

                print(list(read_all(["a", "b", "END", "c", "END"])))
            '''),
        ),
        section(
            "The itertools toolkit",
            "<code>itertools</code> is a library of lazy building blocks written in C. Knowing a dozen of them replaces most hand-written index loops:",
            code('''
                from itertools import (accumulate, batched, chain, groupby, islice,
                                       pairwise, product, starmap, tee, zip_longest)

                print(list(chain([1, 2], (3, 4), "ab")))
                print(list(accumulate([3, 1, 4, 1, 5])))            # running sums
                print(list(accumulate([3, 1, 4, 1, 5], max)))       # running max
                print(list(pairwise("abcd")))
                print(list(batched(range(7), 3)))                   # Python 3.12+
                print(list(zip_longest("ab", "wxyz", fillvalue="-")))
                print(list(starmap(pow, [(2, 3), (10, 2)])))
                print(list(islice(product("ab", repeat=2), 3)))

                a, b = tee(iter([1, 2, 3]))                        # two independent copies
                print(list(a), list(b))
            '''),
            "<code>groupby</code> deserves a warning of its own: it groups <em>consecutive</em> equal keys, like Unix <code>uniq</code>, not all equal keys. Sort by the same key first.",
            code('''
                from itertools import groupby

                words = ["apple", "bob", "avocado", "banana", "cherry", "blue"]
                first = lambda w: w[0]

                print([(k, list(g)) for k, g in groupby(words, key=first)])
                print([(k, list(g)) for k, g in groupby(sorted(words, key=first), key=first)])
            '''),
            table(
                ["Need", "Reach for"],
                [
                    ["First n items / a slice of an iterator", "<code>islice(it, n)</code>, <code>islice(it, start, stop, step)</code>"],
                    ["Concatenate iterables", "<code>chain(a, b)</code>, <code>chain.from_iterable(nested)</code>"],
                    ["Running total / max", "<code>accumulate</code>"],
                    ["Neighbouring pairs", "<code>pairwise</code>"],
                    ["Fixed-size chunks", "<code>batched</code> (3.12+)"],
                    ["Group runs of equal keys", "<code>groupby</code> (sort first)"],
                    ["Cartesian product, permutations, combinations", "<code>product</code>, <code>permutations</code>, <code>combinations</code>"],
                    ["Infinite counters and cycles", "<code>count</code>, <code>cycle</code>, <code>repeat</code>"],
                ],
            ),
        ),
        section(
            "Pitfalls",
            "<strong>A generator expression evaluates its first <code>for</code> immediately, and everything else lazily.</strong> The outermost iterable is captured when the expression is created; conditions and other names are looked up when items are pulled.",
            code('''
                data = [1, 2, 3]
                limit = 2
                gen = (x for x in data if x >= limit)

                data = [10, 20, 30]      # too late: the first `for` already took the old list
                limit = 3                # not too late: the condition reads `limit` lazily
                print(list(gen))
            '''),
            "<strong>A <code>StopIteration</code> escaping inside a generator is turned into <code>RuntimeError</code></strong> (PEP 479). Before Python 3.7 it silently ended the generator, hiding bugs. A bare <code>next()</code> on an empty iterator inside a generator is the usual culprit.",
            code('''
                def first_of_each(groups):
                    for g in groups:
                        yield next(iter(g))        # raises StopIteration on an empty group

                try:
                    print(list(first_of_each([[1, 2], [], [3]])))
                except RuntimeError as e:
                    print("RuntimeError:", e)

                def first_of_each_fixed(groups):
                    for g in groups:
                        first = next(iter(g), None)  # default instead of raising
                        if first is not None:
                            yield first

                print(list(first_of_each_fixed([[1, 2], [], [3]])))
            '''),
            "<strong>Generators do not run until iterated.</strong> A function with a <code>yield</code> anywhere in it is a generator, even if that <code>yield</code> is never reached. Calling it for its side effects does nothing.",
            code('''
                def save(records, debug=False):
                    for r in records:
                        print("saving", r)
                    if debug:
                        yield "debug info"           # this line makes save() a generator

                result = save(["a", "b"])            # nothing printed
                print(type(result).__name__)
                list(result)                         # now it runs
            '''),
        ),
    ],
    questions=[
        question(
            "What is the difference between an iterable and an iterator? Is a list an iterator?",
            "medium",
            "An iterable can produce an iterator (<code>__iter__</code>). An iterator produces values (<code>__next__</code>) and is its own iterable (<code>__iter__</code> returns <code>self</code>). A list is iterable but not an iterator: <code>next([1, 2])</code> is a <code>TypeError</code>, and every <code>for</code> loop over a list gets a fresh <code>list_iterator</code>, which is why lists can be looped over repeatedly while generators cannot.",
            code('''
                from collections.abc import Iterable, Iterator

                for obj in ([1, 2], iter([1, 2]), (x for x in "ab"), range(3), open(__file__)):
                    print(f"{type(obj).__name__:16} iterable={isinstance(obj, Iterable)!s:5} "
                          f"iterator={isinstance(obj, Iterator)}")
            '''),
        ),
        question(
            "Implement <code>range</code>-like iteration for a class two ways: as an iterator class and as a generator. Which would you choose?",
            "medium",
            code('''
                class CountUpIterator:
                    """Explicit iterator: state lives in attributes."""
                    def __init__(self, stop):
                        self.i, self.stop = 0, stop
                    def __iter__(self):
                        return self
                    def __next__(self):
                        if self.i >= self.stop:
                            raise StopIteration
                        self.i += 1
                        return self.i - 1

                class CountUp:
                    """Iterable whose __iter__ is a generator: state lives in the frame."""
                    def __init__(self, stop):
                        self.stop = stop
                    def __iter__(self):
                        i = 0
                        while i < self.stop:
                            yield i
                            i += 1

                it, c = CountUpIterator(3), CountUp(3)
                print(list(it), list(it))      # iterator: single use
                print(list(c), list(c))        # iterable: fresh generator each time
            '''),
            "Prefer the generator version: it is shorter, cannot forget to raise <code>StopIteration</code>, and making <code>__iter__</code> a generator automatically makes the object re-iterable. Write an explicit iterator class only when the iterator needs extra methods (e.g. <code>peek()</code>, <code>seek()</code>) or must be picklable.",
        ),
        question(
            "What does this print, and why?",
            "hard",
            code('''
                def gen():
                    try:
                        yield 1
                        yield 2
                    finally:
                        print("finally")

                for x in gen():
                    print(x)
                    break
                print("after loop")
            '''),
            "<code>1</code>, then <code>finally</code>, then <code>after loop</code>. Breaking out of the loop drops the last reference to the generator. CPython frees it immediately, and a generator's finaliser calls <code>close()</code>, which raises <code>GeneratorExit</code> at the paused <code>yield</code> and runs the <code>finally</code>.",
            "That timing is a CPython reference-counting detail. On PyPy, or if something else still references the generator, the cleanup happens later. If cleanup must happen at a known point, use <code>contextlib.closing(gen())</code> or call <code>gen.close()</code> yourself.",
        ),
        question(
            "Why can't you use a generator twice, and how do you share one stream between two consumers?",
            "medium",
            "A generator is an iterator; its frame advances and never rewinds. To give two consumers the same stream, either materialise it (<code>list</code>) or use <code>itertools.tee</code>, which buffers items that one copy has seen and the other has not.",
            code('''
                from itertools import tee

                def numbers():
                    for i in range(5):
                        print(f"  produce {i}")
                        yield i

                evens_src, odds_src = tee(numbers())
                evens = [x for x in evens_src if x % 2 == 0]   # pulls everything once
                odds = [x for x in odds_src if x % 2]          # served from tee's buffer
                print(evens, odds)
            '''),
            "Each value was produced once. The cost: <code>tee</code> keeps everything that one copy has consumed and the other has not. If one consumer runs all the way ahead, that is the whole stream in memory &mdash; in which case <code>list()</code> is simpler and no worse.",
        ),
        question(
            "What does <code>yield from</code> do that a <code>for</code> loop with <code>yield</code> doesn't?",
            "hard",
            "For plain iteration they are equivalent. The differences show up with two-way generators: <code>yield from</code> forwards <code>send()</code> and <code>throw()</code> into the sub-generator, calls its <code>close()</code> correctly, and evaluates to the sub-generator's <code>return</code> value. A <code>for</code> loop drops all of that.",
            code('''
                def inner():
                    received = yield "ready"
                    return f"inner got {received}"

                def with_yield_from():
                    result = yield from inner()
                    yield result

                def with_for_loop():
                    for v in inner():
                        yield v
                    yield "return value is lost"

                for outer in (with_yield_from, with_for_loop):
                    g = outer()
                    print(next(g), "->", g.send("hello"))
            '''),
            "In the <code>for</code> version, <code>send(\"hello\")</code> went to the <em>outer</em> generator's <code>yield</code>. The loop then called <code>next()</code> on <code>inner</code>, so <code>received</code> was <code>None</code>, and <code>inner</code>'s return value vanished inside the loop's <code>StopIteration</code>.",
        ),
        question(
            "You need to read a 20 GB CSV and write the rows that match a filter, transformed, to a new file. Sketch the design.",
            "medium",
            "A pipeline of generators: a reader that yields rows from the open file (files are already lazy iterators over lines), a filter stage, a transform stage, and a writer that consumes the pipeline. Memory stays at one row plus buffers, no matter how big the file is; each stage is separately testable with a list as input.",
            code('''
                import csv, io

                source = io.StringIO("id,amount\\n1,50\\n2,700\\n3,1200\\n4,30\\n")
                sink = io.StringIO()

                def read_rows(f):
                    yield from csv.DictReader(f)

                def large(rows, threshold):
                    return (r for r in rows if int(r["amount"]) >= threshold)

                def with_fee(rows):
                    for r in rows:
                        yield {**r, "fee": round(int(r["amount"]) * 0.02, 2)}

                def write(rows, f):
                    w = None
                    for n, r in enumerate(rows, 1):
                        if w is None:
                            w = csv.DictWriter(f, fieldnames=list(r))
                            w.writeheader()
                        w.writerow(r)
                    return n if w else 0

                print("rows written:", write(with_fee(large(read_rows(source), 500)), sink))
                print(sink.getvalue().strip())
            '''),
            "Things to mention: <code>csv</code> handles quoting so do not split on commas yourself; open files with <code>newline=\"\"</code> for <code>csv</code>; and the pipeline is single-pass, so counting rows has to happen inside a stage, as <code>write</code> does here.",
        ),
    ],
    refs=[
        ("Python docs: Iterator types", "https://docs.python.org/3/library/stdtypes.html#iterator-types"),
        ("Python docs: Generator expressions and yield", "https://docs.python.org/3/reference/expressions.html#yield-expressions"),
        ("Python docs: itertools", "https://docs.python.org/3/library/itertools.html"),
        ("PEP 479: Change StopIteration handling inside generators", "https://peps.python.org/pep-0479/"),
        ("PEP 380: Syntax for delegating to a subgenerator", "https://peps.python.org/pep-0380/"),
    ],
)
