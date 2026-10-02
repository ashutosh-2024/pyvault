from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="gil",
    title="The Global Interpreter Lock",
    intro=[
        "The GIL is the single most-cited reason Python &ldquo;can&rsquo;t do threads&rdquo;, and most of what people say about it is half right. It does not stop you using threads, it does not make your code thread-safe, and it does not slow down I/O-bound programs. What it does is stop two threads from executing Python bytecode <em>at the same instant</em> inside one interpreter &mdash; which is exactly the thing a CPU-bound program needs.",
        "This page builds the model from the bottom up: what the lock protects, when it is released, why that makes I/O-bound threading fine and CPU-bound threading useless, why you still need your own locks, and what the alternatives are &mdash; including the free-threaded build that ships alongside CPython 3.14.",
    ],
    sections=[
        section(
            "What the GIL actually is",
            "The GIL is one mutex per interpreter. A thread must hold it to execute Python bytecode or touch Python objects. Every other thread that wants to run Python code waits for it. Threads are real OS threads &mdash; the kernel schedules them freely &mdash; but only the one holding the GIL makes progress in Python code.",
            code('''
                import sys, threading

                print("GIL enabled:", sys._is_gil_enabled())
                print("switch interval:", sys.getswitchinterval(), "seconds")
                print("threads right now:", threading.active_count())
            '''),
            "The switch interval is the heart of the scheduling policy. A thread waiting for the GIL waits for up to that long (5&nbsp;ms), then sets a &ldquo;drop request&rdquo; flag. The running thread checks that flag between bytecodes, releases the lock, and the OS decides who gets it next.",
            "Why a single lock? CPython manages memory with reference counts, and every <code>x = obj</code> or function call bumps a count. Making each of those increments atomic would slow down every single-threaded program. One coarse lock makes all of it safe for the price of one acquire per time slice, and it makes C extensions easy to write because they can assume nobody else is mutating Python objects underneath them.",
            note("The GIL protects the <em>interpreter&rsquo;s</em> internal state &mdash; refcounts, allocator, object internals. It was never designed to protect <em>your</em> data."),
        ),
        section(
            "When the GIL is released",
            "A thread gives up the GIL in three situations:",
            table(
                ["Trigger", "Who does it", "Example"],
                [
                    ["Switch interval expires", "The interpreter, between bytecodes", "A pure-Python loop that runs for more than 5&nbsp;ms while another thread is waiting"],
                    ["Blocking system call", "The C code around the call", "<code>socket.recv</code>, <code>file.read</code>, <code>time.sleep</code>, <code>select</code>, <code>subprocess.wait</code>"],
                    ["Long C computation", "Extension authors, explicitly", "<code>hashlib</code> on large buffers, <code>zlib</code>, most of NumPy, image codecs"],
                ],
            ),
            "The second row is why threads work well for I/O. While one thread is blocked in the kernel waiting for a socket, it does not hold the GIL, so every other thread keeps running Python code.",
            code('''
                import threading, time

                def fake_io():
                    time.sleep(0.2)          # releases the GIL while blocked

                start = time.perf_counter()
                for _ in range(5):
                    fake_io()
                sequential = time.perf_counter() - start

                start = time.perf_counter()
                threads = [threading.Thread(target=fake_io) for _ in range(5)]
                for t in threads: t.start()
                for t in threads: t.join()
                threaded = time.perf_counter() - start

                print(f"sequential ~ {sequential:.1f}s")
                print(f"threaded   ~ {threaded:.1f}s")
            ''', label="five 0.2 s waits, one after another vs. overlapped"),
            "Five waits overlap into one. The same is true for real network calls, disk reads and database queries: the time is spent in the kernel, not in bytecode.",
        ),
        section(
            "Why CPU-bound threads do not speed up",
            "Now make the work pure computation. There is no blocking call, so the only way the GIL changes hands is the switch interval, and only one thread is ever doing useful work. Two threads doing half the work each take as long as one thread doing all of it &mdash; often a little longer, because they now fight over the lock.",
            code('''
                import threading, time

                def count(n):
                    while n:
                        n -= 1

                N = 4_000_000

                start = time.perf_counter()
                count(N)
                one = time.perf_counter() - start

                start = time.perf_counter()
                a = threading.Thread(target=count, args=(N // 2,))
                b = threading.Thread(target=count, args=(N // 2,))
                a.start(); b.start(); a.join(); b.join()
                two = time.perf_counter() - start

                print("two threads at least 70% as slow as one:", two > one * 0.7)
                print("two threads at least 1.8x faster:       ", two < one / 1.8)
            ''', label="half the work each, on a multi-core machine"),
            "On a machine with plenty of cores the threaded version still cannot get close to 2x, because the two threads take turns rather than running side by side.",
            "The way around it is to stop sharing one interpreter. <code>multiprocessing</code> and <code>ProcessPoolExecutor</code> start separate Python processes, each with its own GIL, so they genuinely run on separate cores. The price is that arguments and results are pickled across a pipe, and every process pays interpreter start-up.",
            code('''
                from concurrent.futures import ProcessPoolExecutor

                def count(n):
                    total = 0
                    for i in range(n):
                        total += i * i
                    return total

                if __name__ == "__main__":          # required: workers re-import this file
                    with ProcessPoolExecutor(max_workers=4) as pool:
                        results = list(pool.map(count, [200_000] * 4))
                    print(results == [count(200_000)] * 4)
                    print(len(results), "chunks computed in separate processes")
            '''),
            note("Process pools pay off when each task does much more work than it costs to pickle its input and output. Sending a 50&nbsp;MB list to a worker so it can add one to each element is slower than doing it in the parent."),
        ),
        section(
            "The GIL does not make your code thread-safe",
            "This is the misconception that causes real bugs. The GIL guarantees that one <em>bytecode</em> runs at a time. It says nothing about a <em>statement</em>. <code>counter += 1</code> is several bytecodes: load, add, store. A switch can land between the load and the store.",
            code('''
                import dis

                counter = 0
                def bump():
                    global counter
                    counter += 1

                dis.dis(bump)
            ''', label="one line of Python, several steps"),
            "The window is small, so a naive demo often happens to get lucky. Widen it with <code>time.sleep(0)</code> &mdash; which releases the GIL on purpose &mdash; and the lost updates show up every time:",
            code('''
                import threading, time

                counter = 0

                def worker():
                    global counter
                    for _ in range(1000):
                        value = counter
                        time.sleep(0)            # another thread runs here
                        counter = value + 1

                threads = [threading.Thread(target=worker) for _ in range(4)]
                for t in threads: t.start()
                for t in threads: t.join()

                print("expected 4000, got 4000:", counter == 4000)
                print("updates were lost:", counter < 4000)
            ''', label="read, yield, write"),
            code('''
                import threading, time

                counter = 0
                lock = threading.Lock()

                def worker():
                    global counter
                    for _ in range(1000):
                        with lock:               # read-modify-write is now one unit
                            value = counter
                            time.sleep(0)
                            counter = value + 1

                threads = [threading.Thread(target=worker) for _ in range(4)]
                for t in threads: t.start()
                for t in threads: t.join()
                print(counter)
            ''', label="the fix"),
            "Single operations on built-in containers &mdash; <code>list.append</code>, <code>dict[key] = value</code>, <code>deque.popleft</code> &mdash; happen inside one C call and are atomic in practice. Anything that reads, decides, then writes (<code>d[k] += 1</code>, <code>if k not in d: d[k] = ...</code>) is not.",
            caveat("The atomicity of single built-in operations is a CPython behaviour, not a language guarantee. The free-threaded build keeps it by giving containers per-object locks, but code that relies on it is relying on the implementation. <code>queue.Queue</code> and <code>threading.Lock</code> are the documented tools."),
        ),
        section(
            "Threads, processes, asyncio &mdash; which one",
            "The right tool depends on where the time goes, not on how much work there is.",
            table(
                ["Workload", "Use", "Why not the others"],
                [
                    ["Many slow network calls, blocking library (<code>requests</code>, DB driver)", "<code>ThreadPoolExecutor</code>", "Processes waste memory waiting; asyncio needs an async library"],
                    ["Thousands of concurrent connections, async library available", "<code>asyncio</code>", "Thousands of OS threads cost memory and context switches"],
                    ["Pure-Python number crunching", "<code>ProcessPoolExecutor</code> (or free-threaded build)", "Threads serialize on the GIL; asyncio is one thread"],
                    ["NumPy / hashing / compression on big buffers", "Threads are fine", "The C code releases the GIL, so threads really do run in parallel"],
                    ["Mixed: async server that must do some CPU work", "asyncio + <code>run_in_executor</code> with a process pool", "Doing CPU work on the event loop stalls every connection"],
                ],
            ),
        ),
        section(
            "Getting rid of it: free-threading and subinterpreters",
            "Two efforts attack the problem from different sides.",
            "<strong>Free-threaded CPython</strong> (PEP 703) is a separate build &mdash; installed as <code>python3.14t</code> &mdash; with no GIL at all. It was experimental in 3.13 and is officially supported from 3.14 (PEP 779). Making it work took biased reference counting (cheap non-atomic increments for the owning thread), immortal objects, the <code>mimalloc</code> allocator and per-object locks on containers. Single-threaded code pays a few percent for all of that; C extensions must be rebuilt and declare they are safe, otherwise the interpreter turns the GIL back on.",
            "<strong>Subinterpreters</strong> keep the GIL but give each interpreter its own (PEP 684, 3.12). From 3.14 they are exposed as <code>concurrent.interpreters</code> and <code>InterpreterPoolExecutor</code>: isolated like processes, but inside one process and cheaper to start.",
            code('''
                import sys, sysconfig
                from concurrent.futures import InterpreterPoolExecutor

                def square(n):
                    return n * n

                print("free-threaded build:", bool(sysconfig.get_config_var("Py_GIL_DISABLED")))
                print("GIL currently enabled:", sys._is_gil_enabled())

                if __name__ == "__main__":
                    with InterpreterPoolExecutor(max_workers=2) as pool:
                        print(list(pool.map(square, range(6))))
            ''', label="checking the build, and a pool of isolated interpreters"),
            note("On a default CPython build, CPU parallelism means processes (or interpreters). Only reach for the free-threaded build when every C extension you import supports it."),
        ),
    ],
    questions=[
        question(
            "If Python has a GIL, why do I still need locks?",
            "medium",
            "Because the GIL makes each <em>bytecode</em> atomic, not each statement or each piece of your logic. A read-modify-write such as <code>balance -= amount</code> is a load, a subtract and a store; a thread switch between the load and the store loses the other thread&rsquo;s update. Check-then-act sequences are worse:",
            code('''
                import threading, time

                stock = {"widget": 1}
                sold = []

                def buy(who):
                    if stock["widget"] > 0:      # both threads see 1 ...
                        time.sleep(0.01)         # ... pretend to charge the card
                        stock["widget"] -= 1
                        sold.append(who)

                ts = [threading.Thread(target=buy, args=(n,)) for n in ("ann", "bob")]
                for t in ts: t.start()
                for t in ts: t.join()
                print(sold, stock)
            '''),
            "Both buyers got the last widget and the stock went negative. Wrapping the check and the decrement in one <code>with lock:</code> fixes it. The GIL also disappears entirely on the free-threaded build, so code that &ldquo;worked because of the GIL&rdquo; breaks there.",
        ),
        question(
            "You need to download 10,000 URLs and then resize 10,000 images. Which concurrency model do you use for each?",
            "medium",
            "Downloading is I/O-bound: nearly all the time is spent waiting on the network with the GIL released. Use <code>asyncio</code> with an async HTTP client and a semaphore to cap concurrency, or a <code>ThreadPoolExecutor</code> of a few dozen threads if the client library is blocking. Processes would work but waste memory on idle interpreters.",
            "Resizing is CPU-bound. If the resize happens in a C library that releases the GIL (Pillow does for most operations), threads can already use several cores. If it is pure Python, use a <code>ProcessPoolExecutor</code> sized to the core count and pass <em>file paths</em> to workers, not image bytes, so the pickling cost stays small.",
            "The follow-up interviewers like: in a pipeline doing both, run the downloads on the event loop and hand each finished file to a process pool via <code>loop.run_in_executor</code>, so neither stage blocks the other.",
        ),
        question(
            "Why hasn&rsquo;t the GIL simply been removed?",
            "hard",
            "It has been tried many times. Greg Stein&rsquo;s 1999 patch replaced it with fine-grained locks and made single-threaded code roughly twice as slow; Larry Hastings&rsquo; Gilectomy hit the same wall. The costs are:",
            "<strong>Reference counting</strong> &mdash; every incref/decref would have to be an atomic instruction, which is far slower than a plain increment and hammers shared cache lines.<br><strong>C API compatibility</strong> &mdash; thousands of extensions assume the GIL protects them.<br><strong>Single-thread speed</strong> &mdash; the core team&rsquo;s stated rule was that removing the GIL must not make ordinary programs meaningfully slower.",
            "PEP 703 got past these with <em>biased reference counting</em> (the owning thread uses non-atomic ops; others use atomic ones on a separate field), <em>immortal objects</em> whose counts never change (<code>None</code>, small ints), deferred refcounting for functions and modules, <code>mimalloc</code> for thread-safe allocation, and per-object critical sections for <code>list</code>/<code>dict</code>. It ships as a separate build so extensions can opt in gradually.",
        ),
        question(
            "What is the switch interval, and what is the &ldquo;convoy effect&rdquo;?",
            "hard",
            "Since Python 3.2 a waiting thread waits up to <code>sys.getswitchinterval()</code> (5&nbsp;ms by default) and then sets a flag asking the holder to drop the GIL. The holder checks the flag at safe points between bytecodes. The old scheme counted 100 &ldquo;ticks&rdquo; instead, which behaved terribly on multi-core machines.",
            "The convoy effect: an I/O thread that does a short read releases the GIL, gets its data almost instantly, and then has to wait up to a full interval behind a CPU-bound thread before it can process that data &mdash; for every single read. A thread doing thousands of small reads runs orders of magnitude slower than it would alone. Lowering the switch interval helps latency at the cost of more switching overhead:",
            code('''
                import sys
                print(sys.getswitchinterval())
                sys.setswitchinterval(0.001)
                print(sys.getswitchinterval())
            '''),
        ),
        question(
            "Is <code>d[key] += 1</code> thread-safe? What about <code>list.append</code>?",
            "medium",
            "<code>list.append(x)</code> is one C function call on a built-in type, and CPython will not switch threads in the middle of it, so in practice it is atomic. <code>d[key] += 1</code> is a lookup, an add and a store &mdash; three steps with switch points between them, so it is not.",
            code('''
                import dis
                def inc(d, key):
                    d[key] += 1
                dis.dis(inc)
            '''),
            "Use <code>collections.Counter</code> updates under a lock, <code>queue.Queue</code> for hand-offs, or give each thread its own counter and merge at the end. The last option is usually fastest because it needs no locking at all.",
        ),
        question(
            "Why does <code>multiprocessing</code> code need <code>if __name__ == &quot;__main__&quot;</code>?",
            "hard",
            "With the <em>spawn</em> start method a worker is a brand-new interpreter. To find the function you asked it to run, it imports your main module. Without the guard, that import runs the top-level code again &mdash; which starts another pool, which spawns more workers, which import the module&hellip; CPython detects this and raises a <code>RuntimeError</code> telling you to add the guard.",
            code('''
                import multiprocessing as mp
                print(mp.get_start_method())
            ''', label="the default on this build machine"),
            "<em>spawn</em> is the default on macOS and Windows. Linux used <em>fork</em> for years, which copies the parent&rsquo;s memory and so did not need the guard &mdash; but forking a process that has threads can deadlock, so 3.14 made <em>forkserver</em> the Linux default. Code without the guard that has only ever been run on Linux is now more likely to break.",
        ),
    ],
    refs=[
        ("Python docs: thread state and the GIL", "https://docs.python.org/3/c-api/init.html#thread-state-and-the-global-interpreter-lock"),
        ("PEP 703 — Making the GIL optional", "https://peps.python.org/pep-0703/"),
        ("PEP 734 — Multiple interpreters in the stdlib", "https://peps.python.org/pep-0734/"),
        ("Python docs: free-threading HOWTO", "https://docs.python.org/3/howto/free-threading-python.html"),
    ],
)
