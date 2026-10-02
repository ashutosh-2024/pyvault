from ._blocks import code, table, note, caveat, section, question

# Timings are printed as comparisons or rounded to a coarse step, so the
# captured output does not change from run to run.

TOPIC = dict(
    id="asyncio-pitfalls",
    title="asyncio Pitfalls",
    intro=[
        "The async internals topic explains how the event loop and coroutines work. This one is about how async code goes wrong in practice. Almost every bug has the same root: <strong>an event loop is one thread running one task at a time, and a task only gives up control at an <code>await</code></strong>. Forget that, and you get code that blocks every other request, loses exceptions, races on shared state, or never runs at all.",
        "Each section shows the bug running, then the fix. The interview versions of these questions are &ldquo;why is my async server slow&rdquo; and &ldquo;where did my exception go&rdquo;.",
    ],
    sections=[
        section(
            "Forgetting await",
            "Calling a coroutine function does not run it. It creates a coroutine object, which does nothing until it is awaited or wrapped in a task. Forget the <code>await</code> and the work silently never happens; the only clue is a <code>RuntimeWarning</code> when the unused coroutine is garbage-collected.",
            code('''
                import asyncio, sys, warnings
                sys.stderr = sys.stdout                   # show the warning inline
                warnings.simplefilter("always")

                saved = []

                async def save(item):
                    await asyncio.sleep(0)
                    saved.append(item)

                async def main():
                    save("a")                             # BUG: creates a coroutine, never runs it
                    await save("b")
                    print("saved:", saved)

                asyncio.run(main())
            '''),
            "Turn on debug mode (<code>PYTHONASYNCIODEBUG=1</code> or <code>asyncio.run(main(), debug=True)</code>) in development, and use a linter: both catch this and several of the problems below. Type checkers flag an unused coroutine result too.",
        ),
        section(
            "Blocking the event loop",
            "While a coroutine runs code that does not <code>await</code> &mdash; <code>time.sleep</code>, <code>requests.get</code>, a big JSON parse, a CPU loop &mdash; nothing else on the loop can run. Ten concurrent requests become ten sequential ones.",
            code('''
                import asyncio, time

                async def handler_blocking(i):
                    time.sleep(0.2)                       # blocks the whole loop
                    return i

                async def handler_async(i):
                    await asyncio.sleep(0.2)              # yields to the loop while waiting
                    return i

                async def timed(handler):
                    start = time.perf_counter()
                    await asyncio.gather(*(handler(i) for i in range(5)))
                    return round(time.perf_counter() - start, 1)

                print("time.sleep    :", asyncio.run(timed(handler_blocking)), "s")
                print("asyncio.sleep :", asyncio.run(timed(handler_async)), "s")
            '''),
            "When you must call blocking code (a library with no async version, file I/O, a C extension), move it to a thread with <code>asyncio.to_thread</code>. The loop keeps running while the thread waits. For CPU-bound work, threads do not help under the GIL; use a <code>ProcessPoolExecutor</code> with <code>loop.run_in_executor</code>.",
            code('''
                import asyncio, time

                def legacy_fetch(i):                      # a blocking library call
                    time.sleep(0.2)
                    return f"result-{i}"

                async def main():
                    start = time.perf_counter()
                    results = await asyncio.gather(*(asyncio.to_thread(legacy_fetch, i) for i in range(5)))
                    print(results)
                    print("elapsed", round(time.perf_counter() - start, 1), "s")

                asyncio.run(main())
            '''),
            table(
                ["Work", "Inside async code, use"],
                [
                    ["Waiting on network or timers", "An async library (<code>aiohttp</code>, <code>httpx.AsyncClient</code>, <code>asyncpg</code>) and <code>await</code>"],
                    ["A blocking call you cannot replace", "<code>await asyncio.to_thread(fn, *args)</code>"],
                    ["CPU-heavy computation", "<code>await loop.run_in_executor(process_pool, fn, *args)</code>"],
                    ["A tight loop over many items", "<code>await asyncio.sleep(0)</code> every so often to let others run"],
                ],
            ),
        ),
        section(
            "Fire-and-forget tasks and lost exceptions",
            "<code>asyncio.create_task</code> schedules a coroutine and returns a <code>Task</code>. The event loop keeps only a <em>weak</em> reference to it, so a task nobody holds can be garbage-collected mid-flight. And if a task raises and nobody awaits it, the exception is not raised anywhere &mdash; it is logged as &ldquo;Task exception was never retrieved&rdquo;, if you are lucky, when the task is destroyed.",
            code('''
                import asyncio, sys
                sys.stderr = sys.stdout

                async def send_email(to):
                    await asyncio.sleep(0.01)
                    raise ConnectionError(f"SMTP down, could not mail {to}")

                async def main():
                    asyncio.create_task(send_email("ann"))   # nobody keeps it, nobody awaits it
                    await asyncio.sleep(0.05)
                    print("request handled, user told 'email sent'")

                asyncio.run(main())
                print("program finished without raising")
            '''),
            "The fix is to keep a strong reference and to observe the result. A set plus <code>add_done_callback</code> is the pattern the asyncio docs recommend for background tasks:",
            code('''
                import asyncio

                background = set()

                def spawn(coro):
                    task = asyncio.create_task(coro)
                    background.add(task)                      # strong reference
                    task.add_done_callback(on_done)
                    return task

                def on_done(task):
                    background.discard(task)
                    if not task.cancelled() and task.exception():
                        print(f"background task failed: {task.exception()!r}")

                async def send_email(to):
                    await asyncio.sleep(0.01)
                    raise ConnectionError(f"SMTP down, could not mail {to}")

                async def main():
                    spawn(send_email("ann"))
                    await asyncio.sleep(0.05)
                    print("pending tasks:", len(background))

                asyncio.run(main())
            '''),
        ),
        section(
            "gather vs TaskGroup",
            "<code>asyncio.gather(*aws)</code> runs awaitables concurrently and returns their results in order. If one raises, gather raises that exception to you immediately &mdash; but the <em>other</em> tasks keep running in the background, unsupervised. <code>asyncio.TaskGroup</code> (3.11+) is structured concurrency: if any task fails, the group cancels the rest, waits for them, and raises all failures together as an <code>ExceptionGroup</code>.",
            code('''
                import asyncio

                log = []

                async def job(name, delay, fail=False):
                    try:
                        await asyncio.sleep(delay)
                        if fail:
                            raise ValueError(f"{name} failed")
                        log.append(f"{name} done")
                    except asyncio.CancelledError:
                        log.append(f"{name} cancelled")
                        raise

                async def with_gather():
                    try:
                        await asyncio.gather(job("a", 0.01, fail=True), job("b", 0.05))
                    except ValueError as e:
                        log.append(f"caught {e}")
                    await asyncio.sleep(0.1)                  # b is still running...

                async def with_taskgroup():
                    try:
                        async with asyncio.TaskGroup() as tg:
                            tg.create_task(job("a", 0.01, fail=True))
                            tg.create_task(job("b", 0.05))
                    except* ValueError as eg:
                        log.append(f"caught {[str(e) for e in eg.exceptions]}")

                for scenario in (with_gather, with_taskgroup):
                    log.clear()
                    asyncio.run(scenario())
                    print(f"{scenario.__name__:15}", log)
            '''),
            "With gather, <code>b</code> finished after the error was already handled &mdash; in a real server, still holding a connection or writing to a closed resource. With the TaskGroup, <code>b</code> was cancelled before the <code>async with</code> exited. <code>gather(..., return_exceptions=True)</code> is the other option when you want every result, failures included, as values.",
            note("Prefer <code>TaskGroup</code> for &ldquo;run these together, and they all succeed or none do&rdquo;. Use <code>gather(return_exceptions=True)</code> for &ldquo;run all of these and tell me how each one went&rdquo;."),
        ),
        section(
            "Swallowing cancellation",
            "Cancelling a task throws <code>CancelledError</code> into it at its current <code>await</code>. Since 3.8 <code>CancelledError</code> derives from <code>BaseException</code>, so <code>except Exception</code> does not catch it &mdash; but a bare <code>except:</code> or <code>except BaseException</code> does, and if the handler does not re-raise, the task carries on as if nothing happened. Timeouts and TaskGroups stop working.",
            code('''
                import asyncio

                async def stubborn():
                    for i in range(3):
                        try:
                            await asyncio.sleep(0.05)
                        except BaseException:              # BUG: eats CancelledError
                            print(f"  swallowed cancellation on step {i}")
                    return "finished anyway"

                async def polite():
                    try:
                        await asyncio.sleep(0.05)
                    except asyncio.CancelledError:
                        print("  cleaning up, then re-raising")
                        raise
                    return "finished"

                async def main():
                    for fn in (stubborn, polite):
                        try:
                            async with asyncio.timeout(0.01):
                                print(fn.__name__, "->", await fn())
                        except TimeoutError:
                            print(fn.__name__, "-> TimeoutError (cancellation worked)")

                asyncio.run(main())
            '''),
            "<code>stubborn</code> blew through its 10 ms timeout and ran all three steps. Rule: if you catch <code>CancelledError</code> to clean up, re-raise it. Use <code>try/finally</code> when all you need is cleanup. If a piece of work must not be interrupted, wrap it in <code>asyncio.shield</code> and accept that the caller may stop waiting for it.",
        ),
        section(
            "Race conditions across await",
            "Async code has no preemption, so a block with no <code>await</code> in it is atomic. But every <code>await</code> is a point where other tasks run, and a check-then-act sequence that spans one is a race &mdash; exactly as with threads.",
            code('''
                import asyncio

                class Account:
                    def __init__(self, balance):
                        self.balance = balance
                        self.lock = asyncio.Lock()

                    async def withdraw_racy(self, amount):
                        if self.balance >= amount:          # check
                            await asyncio.sleep(0)          # e.g. an audit-log call
                            self.balance -= amount          # act: the check may be stale
                            return True
                        return False

                    async def withdraw_safe(self, amount):
                        async with self.lock:               # check and act under one lock
                            if self.balance >= amount:
                                await asyncio.sleep(0)
                                self.balance -= amount
                                return True
                            return False

                async def main():
                    for method in ("withdraw_racy", "withdraw_safe"):
                        acct = Account(100)
                        ok = await asyncio.gather(*(getattr(acct, method)(80) for _ in range(3)))
                        print(f"{method:14} approved={ok.count(True)} balance={acct.balance}")

                asyncio.run(main())
            '''),
            "All three racy withdrawals passed the check before any of them reached the subtraction. An <code>asyncio.Lock</code> is cheap; it does not block the thread, it only makes other tasks that want the same lock wait their turn.",
            caveat("<code>asyncio.Lock</code> protects against other <em>tasks</em> on the same loop. It is not thread-safe. State shared with threads (from <code>to_thread</code> or executors) needs <code>threading.Lock</code> or, better, no sharing."),
        ),
        section(
            "Unbounded concurrency",
            "<code>gather</code> over 10,000 URLs starts 10,000 requests at once: sockets run out, the remote server rate-limits you, memory spikes. Bound concurrency with a <code>Semaphore</code>, or use a fixed pool of worker tasks reading from a bounded <code>asyncio.Queue</code>, which also gives backpressure: producers wait when the queue is full.",
            code('''
                import asyncio

                in_flight = peak = 0

                async def fetch(i, limit):
                    global in_flight, peak
                    async with limit:
                        in_flight += 1
                        peak = max(peak, in_flight)
                        await asyncio.sleep(0.01)
                        in_flight -= 1
                        return i

                async def main():
                    global peak
                    for size in (1000, 20):
                        peak = 0
                        limit = asyncio.Semaphore(size)
                        results = await asyncio.gather(*(fetch(i, limit) for i in range(200)))
                        print(f"semaphore({size:4}): {len(results)} done, peak concurrency {peak}")

                asyncio.run(main())
            '''),
            code('''
                import asyncio

                async def producer(queue, n):
                    for i in range(n):
                        await queue.put(i)                 # waits while the queue is full
                    for _ in range(WORKERS):
                        await queue.put(None)              # one stop signal per worker

                async def worker(name, queue, done):
                    while (item := await queue.get()) is not None:
                        await asyncio.sleep(0.001)
                        done.append(item)

                WORKERS = 4

                async def main():
                    queue, done = asyncio.Queue(maxsize=10), []
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(producer(queue, 100))
                        for w in range(WORKERS):
                            tg.create_task(worker(w, queue, done))
                    print(len(done), sorted(done) == list(range(100)))

                asyncio.run(main())
            ''', label="worker pool with a bounded queue"),
        ),
        section(
            "Loops, threads and asyncio.run",
            "<code>asyncio.run</code> creates a new event loop, runs one coroutine, and closes the loop. It cannot be called from code that is already running inside a loop (a Jupyter cell, an async web handler). From async code, just <code>await</code>. From another <em>thread</em> that needs to submit work to a running loop, use <code>asyncio.run_coroutine_threadsafe</code>; nothing else on a loop is thread-safe.",
            code('''
                import asyncio, threading

                async def compute(x):
                    await asyncio.sleep(0.01)
                    return x * 2

                async def main():
                    coro = compute(1)
                    try:
                        asyncio.run(coro)
                    except RuntimeError as e:
                        coro.close()                      # never started: discard it quietly
                        print("RuntimeError:", e)

                    loop = asyncio.get_running_loop()
                    results = []

                    def from_thread():
                        fut = asyncio.run_coroutine_threadsafe(compute(21), loop)
                        results.append(fut.result(timeout=1))   # blocks this thread, not the loop

                    t = threading.Thread(target=from_thread)
                    t.start()
                    await asyncio.to_thread(t.join)
                    print("from thread:", results)

                asyncio.run(main())
            '''),
        ),
    ],
    questions=[
        question(
            "An async web service handles one request at a time even though every handler is <code>async def</code>. What do you look for?",
            "medium",
            "Something in the request path blocks the event loop. Usual suspects: a synchronous HTTP client (<code>requests</code>), a synchronous database driver, <code>time.sleep</code>, file I/O, heavy JSON or template rendering, password hashing, or any long CPU loop. <code>async def</code> only makes a function <em>able</em> to yield; it yields only at an <code>await</code> on something that actually waits asynchronously.",
            "To find it: run with <code>asyncio.run(..., debug=True)</code> (or <code>PYTHONASYNCIODEBUG=1</code>), which logs every callback that holds the loop for longer than <code>loop.slow_callback_duration</code> (100 ms by default). Fix with an async library, <code>asyncio.to_thread</code> for blocking I/O, or a process pool for CPU work.",
        ),
        question(
            "What is printed, and why is the second call so different?",
            "medium",
            code('''
                import asyncio, time

                async def work(n):
                    await asyncio.sleep(0.1)
                    return n

                async def sequential():
                    return [await work(i) for i in range(5)]

                async def concurrent():
                    return await asyncio.gather(*(work(i) for i in range(5)))

                for fn in (sequential, concurrent):
                    t = time.perf_counter()
                    result = asyncio.run(fn())
                    print(f"{fn.__name__:10} {result} {round(time.perf_counter() - t, 1)}s")
            '''),
            "Awaiting coroutines one after another runs them one after another: <code>await</code> means &ldquo;wait for this to finish before continuing&rdquo;. Concurrency only happens when several tasks exist at the same time &mdash; <code>gather</code> wraps each coroutine in a task, so all five sleeps overlap.",
        ),
        question(
            "Why can <code>asyncio.create_task(coro())</code> without keeping the result lose work?",
            "hard",
            "The event loop holds tasks only through weak references. A task that nothing else references can be garbage-collected before it finishes &mdash; the coroutine just stops. Even if it survives, an exception in it is never re-raised anywhere; it is only logged when the task object is destroyed. Keep tasks in a collection (or a <code>TaskGroup</code>), remove them in a done-callback, and check <code>task.exception()</code> there. In 3.12+ <code>asyncio.TaskGroup</code> or a framework-provided background-task API is the cleaner choice.",
        ),
        question(
            "Write a function that runs coroutines with at most N in flight and returns results in input order.",
            "medium",
            code('''
                import asyncio, random

                async def bounded_gather(coros, limit):
                    sem = asyncio.Semaphore(limit)
                    active = peak = 0

                    async def run(coro):
                        nonlocal active, peak
                        async with sem:
                            active += 1
                            peak = max(peak, active)
                            try:
                                return await coro
                            finally:
                                active -= 1

                    results = await asyncio.gather(*(run(c) for c in coros))
                    return results, peak

                async def fetch(i):
                    await asyncio.sleep(random.random() / 100)
                    return i * i

                results, peak = asyncio.run(bounded_gather([fetch(i) for i in range(30)], limit=5))
                print(results[:8], "... peak in flight:", peak)
            '''),
            "<code>gather</code> preserves input order regardless of completion order, and the semaphore caps how many bodies run at once. Note the coroutine objects are all created up front; that is cheap, since a coroutine does nothing until awaited. For very large or unbounded inputs, use a fixed set of workers pulling from a queue instead, so you never hold millions of pending coroutines.",
        ),
        question(
            "When should you not use asyncio at all?",
            "medium",
            "When the work is CPU-bound (asyncio adds overhead and no parallelism &mdash; use processes), when the important libraries have no async versions (you would wrap everything in <code>to_thread</code>, which is just a thread pool with extra steps), or when concurrency is low and a few threads would be simpler. asyncio shines with many concurrent, mostly-waiting I/O operations: thousands of sockets, websockets, proxies, crawlers, chat servers. It also &ldquo;colours&rdquo; functions: async functions can call sync ones but not the reverse without a loop, so adopting it is a whole-codebase decision.",
        ),
    ],
    refs=[
        ("Python docs: Developing with asyncio", "https://docs.python.org/3/library/asyncio-dev.html"),
        ("Python docs: Task groups and create_task", "https://docs.python.org/3/library/asyncio-task.html"),
        ("Python docs: asyncio synchronisation primitives", "https://docs.python.org/3/library/asyncio-sync.html"),
        ("PEP 654: Exception groups and except*", "https://peps.python.org/pep-0654/"),
    ],
)
