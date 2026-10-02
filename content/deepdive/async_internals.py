from ._blocks import code, table, note, caveat, section, question

TOPIC = dict(
    id="async",
    title="Async Internals",
    intro=[
        "<code>asyncio</code> runs thousands of concurrent tasks on one thread, with no locks around your data and no thread switches. There is no magic in how: a coroutine is a function that can pause, <code>await</code> is the pause point, and the event loop is an ordinary loop that resumes whichever coroutine has something to do next.",
        "This page builds the machinery up from generators, writes a toy event loop, then maps it onto the real one: tasks, futures, <code>gather</code> and <code>TaskGroup</code>, cancellation and timeouts, why one blocking call freezes everything, and how to bridge sync and async code.",
    ],
    sections=[
        section(
            "Concurrency on one thread",
            "Threads get concurrency by letting the OS interrupt them at any instruction (<em>pre-emptive</em>). Async code gets it by having each task voluntarily give up control at an <code>await</code> (<em>cooperative</em>). Between two <code>await</code>s your code cannot be interrupted, which is why most async code needs no locks &mdash; and why one task that never awaits stalls every other.",
            table(
                ["", "Threads", "asyncio"],
                [
                    ["Switching", "Pre-emptive, anywhere", "Cooperative, only at <code>await</code>"],
                    ["Parallel CPU work", "No (GIL)", "No (one thread)"],
                    ["Cost per task", "An OS thread: ~MBs of stack reserved, kernel scheduling", "A Python object: a few KB"],
                    ["Practical scale", "Hundreds", "Tens of thousands"],
                    ["Shared-state races", "Anywhere", "Only across an <code>await</code>"],
                    ["Libraries", "Any blocking library", "Must be async-aware (or offloaded to a thread)"],
                ],
            ),
        ),
        section(
            "A coroutine is an object",
            "Calling an <code>async def</code> function runs none of its body. It returns a coroutine object: a paused computation. Something must drive it &mdash; normally the event loop, via <code>await</code> or a task.",
            code('''
                import asyncio, warnings
                warnings.simplefilter("ignore", RuntimeWarning)   # hide the 'never awaited' warning

                async def fetch():
                    print("  body runs")
                    return 42

                c = fetch()
                print(type(c).__name__, "- nothing printed yet")
                c.close()

                print(asyncio.run(fetch()))
            '''),
            "Forgetting an <code>await</code> is the classic async bug: <code>fetch()</code> on its own line creates a coroutine, throws it away, and Python emits <code>RuntimeWarning: coroutine 'fetch' was never awaited</code>.",
        ),
        section(
            "Under the hood: generators and send()",
            "Coroutines are built on the same machinery as generators. A generator pauses at <code>yield</code>; you resume it with <code>send()</code>; when it returns, it raises <code>StopIteration</code> carrying the return value. A coroutine is driven the same way:",
            code('''
                import types

                @types.coroutine
                def suspend(reason):
                    received = yield reason          # the one real yield in the chain
                    return received

                async def child():
                    got = await suspend("waiting for data")
                    return f"child got {got!r}"

                async def parent():
                    result = await child()           # await chains through child ...
                    return result.upper()

                coro = parent()
                print("yielded to driver:", coro.send(None))    # runs until the yield
                try:
                    coro.send("payload")                        # resume with a value
                except StopIteration as done:
                    print("returned:", done.value)
            '''),
            "This is the whole secret of <code>await</code>: it delegates down the chain (<code>parent</code> &rarr; <code>child</code> &rarr; <code>suspend</code>) until something at the bottom actually yields. That yielded value travels straight back up to whoever called <code>send</code> &mdash; the event loop. In asyncio, what is yielded at the bottom is a <code>Future</code>: &ldquo;wake me when this is done&rdquo;.",
        ),
        section(
            "A toy event loop",
            "With <code>send</code> you can write an event loop in twenty lines. Each task yields how long it wants to sleep; the loop keeps a heap of wake-up times and always resumes the earliest. It uses a fake clock so the output is deterministic.",
            code('''
                import heapq, types

                @types.coroutine
                def sleep(seconds):
                    yield seconds

                class Loop:
                    def __init__(self):
                        self.now, self.ready, self.seq = 0.0, [], 0
                    def spawn(self, coro, at=0.0):
                        heapq.heappush(self.ready, (at, self.seq, coro)); self.seq += 1
                    def run(self):
                        while self.ready:
                            self.now, _, coro = heapq.heappop(self.ready)
                            try:
                                delay = coro.send(None)
                                self.spawn(coro, self.now + delay)
                            except StopIteration:
                                pass

                loop = Loop()

                async def worker(name, delay, steps):
                    for i in range(steps):
                        print(f"t={loop.now:.1f}  {name} step {i}")
                        await sleep(delay)

                loop.spawn(worker("fast", 0.3, 3))
                loop.spawn(worker("slow", 0.5, 2))
                loop.run()
            '''),
            "asyncio&rsquo;s loop is the same idea with real parts: a ready queue of callbacks, a heap of timers, and &mdash; instead of a fake clock &mdash; a call to <code>select</code>/<code>epoll</code>/<code>kqueue</code> that sleeps until the next timer is due <em>or</em> a socket becomes readable. That one system call is how one thread waits on thousands of connections at once.",
        ),
        section(
            "Tasks and futures in asyncio",
            "<strong>Future</strong>: a placeholder for a result that will be set later. Awaiting an unfinished future suspends the awaiting coroutine until <code>set_result</code> or <code>set_exception</code> is called.<br><strong>Task</strong>: a Future subclass that drives a coroutine. <code>asyncio.create_task(coro)</code> schedules it on the loop immediately; it runs whenever the current task next yields.",
            code('''
                import asyncio

                async def main():
                    loop = asyncio.get_running_loop()
                    fut = loop.create_future()
                    loop.call_later(0.01, fut.set_result, "set by a timer callback")
                    print("awaiting future...")
                    print(await fut)

                    async def job(name):
                        print(f"  {name} started")
                        await asyncio.sleep(0)
                        print(f"  {name} finished")
                        return name

                    t = asyncio.create_task(job("task-1"))
                    print("task created, not started yet:", not t.done())
                    await asyncio.sleep(0)            # yield once: the task gets to start
                    print("back in main")
                    print("result:", await t)
                    print("is a Future:", isinstance(t, asyncio.Future))

                asyncio.run(main())
            '''),
            table(
                ["Object", "What it is", "You create it with"],
                [
                    ["Coroutine", "A paused function body; does nothing until driven", "Calling an <code>async def</code> function"],
                    ["Future", "A result slot plus a list of callbacks to run when it is filled", "<code>loop.create_future()</code> (rarely by hand)"],
                    ["Task", "A Future that runs a coroutine to completion on the loop", "<code>asyncio.create_task()</code>, <code>TaskGroup.create_task()</code>"],
                ],
            ),
        ),
        section(
            "Sequential await vs concurrent tasks",
            "<code>await</code> on a coroutine runs it to completion before moving on. For concurrency you must create tasks &mdash; directly, or through <code>gather</code> or a <code>TaskGroup</code>.",
            code('''
                import asyncio, time

                async def io(name, seconds):
                    await asyncio.sleep(seconds)
                    return name

                async def main():
                    start = time.perf_counter()
                    a = await io("a", 0.2)
                    b = await io("b", 0.2)
                    c = await io("c", 0.2)
                    print(f"sequential: {time.perf_counter() - start:.1f}s", [a, b, c])

                    start = time.perf_counter()
                    results = await asyncio.gather(io("a", 0.2), io("b", 0.2), io("c", 0.2))
                    print(f"gather:     {time.perf_counter() - start:.1f}s", results)

                    start = time.perf_counter()
                    async with asyncio.TaskGroup() as tg:
                        tasks = [tg.create_task(io(n, 0.2)) for n in "abc"]
                    print(f"TaskGroup:  {time.perf_counter() - start:.1f}s", [t.result() for t in tasks])

                asyncio.run(main())
            '''),
            "<code>TaskGroup</code> (3.11+) is <em>structured concurrency</em>: no task can outlive the <code>async with</code> block, and if one task fails, the others are cancelled and all errors are raised together as an <code>ExceptionGroup</code>. Prefer it to bare <code>create_task</code> and to <code>gather</code> in new code.",
        ),
        section(
            "Never block the event loop",
            "The loop can only switch tasks at an <code>await</code>. A blocking call &mdash; <code>time.sleep</code>, <code>requests.get</code>, a heavy computation, a sync database driver &mdash; holds the only thread, and every other task freezes until it returns.",
            code('''
                import asyncio, time

                async def heartbeat(log):
                    for _ in range(3):
                        log.append("beat")
                        await asyncio.sleep(0.05)

                async def bad_worker(log):
                    time.sleep(0.2)                         # blocks the whole loop
                    log.append("bad done")

                async def good_worker(log):
                    await asyncio.to_thread(time.sleep, 0.2)   # blocks a worker thread instead
                    log.append("good done")

                async def run(worker):
                    log = []
                    await asyncio.gather(worker(log), heartbeat(log))
                    return log

                print("blocking:  ", asyncio.run(run(bad_worker)))
                print("to_thread: ", asyncio.run(run(good_worker)))
            '''),
            "With the blocking call, the worker was scheduled first and held the only thread for the full 0.2&nbsp;s, so the heartbeat could not even start until it had finished. With <code>to_thread</code>, the wait happens on a thread pool, the heartbeat beats three times while the worker waits, and the worker finishes last. For CPU-heavy work use <code>loop.run_in_executor</code> with a <code>ProcessPoolExecutor</code>, since a thread would still hold the GIL.",
            note("Turn on debug mode (<code>asyncio.run(main(), debug=True)</code> or <code>PYTHONASYNCIODEBUG=1</code>) in development: it logs every callback that blocks the loop for more than 100&nbsp;ms, and names coroutines that were never awaited."),
        ),
        section(
            "Cancellation and timeouts",
            "Cancelling a task throws <code>CancelledError</code> into it at its current <code>await</code>. The task can run cleanup in <code>finally</code>, but should let the error propagate &mdash; swallowing it breaks timeouts and <code>TaskGroup</code>.",
            code('''
                import asyncio

                async def download():
                    try:
                        print("  downloading...")
                        await asyncio.sleep(10)
                    except asyncio.CancelledError:
                        print("  cancelled: cleaning up partial file")
                        raise                                   # always re-raise
                    finally:
                        print("  finally runs")

                async def main():
                    t = asyncio.create_task(download())
                    await asyncio.sleep(0.01)
                    t.cancel()
                    try:
                        await t
                    except asyncio.CancelledError:
                        print("task cancelled:", t.cancelled())

                    try:
                        async with asyncio.timeout(0.05):
                            await download()
                    except TimeoutError:
                        print("timed out -> TimeoutError")

                asyncio.run(main())
            '''),
            "<code>asyncio.timeout</code> (3.11+) cancels the work inside it and converts the <code>CancelledError</code> into a <code>TimeoutError</code> at the block boundary. <code>asyncio.wait_for(coro, t)</code> is the older, function-style equivalent.",
            caveat("A few operations are not cancellable at all: code running in <code>to_thread</code> keeps running in its thread after the awaiting task is cancelled. Use <code>asyncio.shield</code> to protect an inner operation from an outer cancellation when it must finish."),
        ),
        section(
            "Limiting concurrency and passing work between tasks",
            "Launching 10,000 requests at once will exhaust sockets or get you rate-limited. An <code>asyncio.Semaphore</code> caps how many are in flight; an <code>asyncio.Queue</code> connects producers and consumers with back-pressure.",
            code('''
                import asyncio

                async def main():
                    limit = asyncio.Semaphore(3)
                    active, peak = 0, 0

                    async def fetch(i):
                        nonlocal active, peak
                        async with limit:
                            active += 1
                            peak = max(peak, active)
                            await asyncio.sleep(0.01)
                            active -= 1
                            return i * i

                    results = await asyncio.gather(*(fetch(i) for i in range(20)))
                    print("results ok:", results == [i * i for i in range(20)])
                    print("never more than 3 at once:", peak)

                    queue = asyncio.Queue(maxsize=2)
                    async def producer():
                        for i in range(5):
                            await queue.put(i)          # waits while the queue is full
                        await queue.put(None)
                    async def consumer():
                        seen = []
                        while (item := await queue.get()) is not None:
                            seen.append(item)
                        return seen
                    _, seen = await asyncio.gather(producer(), consumer())
                    print("consumed:", seen)

                asyncio.run(main())
            '''),
            "No lock was needed around <code>active</code> and <code>peak</code>: each read-modify-write happens between two <code>await</code>s, so no other task can interleave. Add an <code>await</code> in the middle of such an update and you would need an <code>asyncio.Lock</code>.",
        ),
    ],
    questions=[
        question(
            "What is the difference between a coroutine, a Task and a Future?",
            "medium",
            "A <strong>coroutine</strong> is the paused function body produced by calling an <code>async def</code> function. Nothing runs until something drives it. A <strong>Future</strong> is a low-level result container with callbacks, awaitable, and completed by someone calling <code>set_result</code>. A <strong>Task</strong> is a Future that owns a coroutine and drives it on the event loop, completing with the coroutine&rsquo;s return value.",
            "Consequence: <code>await coro()</code> runs the coroutine inline, in the current task, one after another. <code>create_task(coro())</code> starts it running concurrently and gives you a handle to await, cancel or inspect later. Keep a reference to tasks you create &mdash; the loop only holds a weak reference, so a fire-and-forget task with no other reference can be garbage-collected mid-flight.",
        ),
        question(
            "What happens if you call <code>time.sleep(5)</code> or <code>requests.get()</code> inside an <code>async def</code>?",
            "medium",
            "The whole event loop stops for those five seconds. The loop runs on one thread and can only switch tasks at an <code>await</code>; a blocking call never yields, so every other task &mdash; every other client connection on a server &mdash; waits. Nothing crashes, which is why it is easy to ship: the symptom is latency spikes under load.",
            "Fixes, in order of preference: use the async equivalent (<code>await asyncio.sleep</code>, <code>httpx.AsyncClient</code>, an async DB driver); otherwise offload with <code>await asyncio.to_thread(blocking_fn, ...)</code>; for CPU-bound work, <code>loop.run_in_executor(process_pool, fn, ...)</code>.",
        ),
        question(
            "Fetch 1,000 URLs concurrently, but never more than 20 at a time, and collect failures without stopping the rest.",
            "hard",
            "A semaphore for the cap; <code>gather(..., return_exceptions=True)</code> so one failure does not cancel the others; then split results from errors. Here the network call is simulated so the answer is runnable.",
            code('''
                import asyncio

                async def fake_get(url):
                    await asyncio.sleep(0.001)
                    if url.endswith("7"):
                        raise ConnectionError(f"{url} unreachable")
                    return f"<html {url}>"

                async def fetch_all(urls, limit=20):
                    sem = asyncio.Semaphore(limit)
                    async def one(url):
                        async with sem:
                            return url, await fake_get(url)
                    results = await asyncio.gather(*(one(u) for u in urls), return_exceptions=True)
                    ok = dict(r for r in results if not isinstance(r, BaseException))
                    failed = [r for r in results if isinstance(r, BaseException)]
                    return ok, failed

                urls = [f"https://example.com/{i}" for i in range(1000)]
                ok, failed = asyncio.run(fetch_all(urls))
                print(len(ok), "succeeded,", len(failed), "failed")
                print(failed[0])
            '''),
            "Points interviewers look for: creating one client session and reusing it (connection pooling), a per-request timeout (<code>asyncio.timeout</code>) so one hung server cannot hold a semaphore slot forever, retries with back-off for transient errors, and &mdash; for truly huge lists &mdash; a fixed pool of worker tasks reading from a <code>Queue</code> instead of creating a million coroutine objects up front.",
        ),
        question(
            "How do <code>gather</code> and <code>TaskGroup</code> behave differently when one task fails?",
            "hard",
            code('''
                import asyncio

                async def ok(name, delay):
                    try:
                        await asyncio.sleep(delay)
                        return name
                    except asyncio.CancelledError:
                        print(f"  {name} was cancelled")
                        raise

                async def boom():
                    await asyncio.sleep(0.01)
                    raise ValueError("boom")

                async def main():
                    print("gather:")
                    slow = asyncio.create_task(ok("slow", 0.05))
                    try:
                        await asyncio.gather(slow, boom())
                    except ValueError as e:
                        print("  raised", repr(e), "| slow still running:", not slow.done())
                    print("  slow finished anyway:", await slow)

                    print("TaskGroup:")
                    try:
                        async with asyncio.TaskGroup() as tg:
                            tg.create_task(ok("slow", 0.05))
                            tg.create_task(boom())
                    except* ValueError as eg:
                        print("  raised", repr(eg.exceptions))

                asyncio.run(main())
            '''),
            "<code>gather</code> (without <code>return_exceptions</code>) propagates the first exception to the awaiting code immediately, but does <em>not</em> cancel the other tasks &mdash; they keep running unobserved, which is how leaked background work happens. <code>TaskGroup</code> cancels the siblings, waits for them to finish, and raises every failure together in an <code>ExceptionGroup</code>, which you handle with <code>except*</code>.",
        ),
        question(
            "How does <code>await</code> actually suspend a function and get it resumed later?",
            "hard",
            "A coroutine is a generator-like frame. <code>await x</code> calls <code>x.__await__()</code> to get an iterator and delegates to it, like <code>yield from</code>. The chain continues down until a <code>Future</code>&rsquo;s <code>__await__</code> hits a real <code>yield self</code>. That yield unwinds straight up to the Task, which called <code>coro.send(None)</code>.",
            "The Task sees it received a Future, registers its own <code>__step</code> method as a done-callback on that future, and returns to the event loop. The coroutine&rsquo;s frame is simply left suspended in memory. Later, when an I/O event or timer completes the future, its callbacks are scheduled; the Task&rsquo;s <code>__step</code> runs, calls <code>coro.send(None)</code> again, and execution resumes exactly after the <code>yield</code> &mdash; inside the <code>await</code> expression, which now returns the future&rsquo;s result.",
            code('''
                import asyncio

                class Ticket:
                    """A minimal awaitable: yields a Future to the Task, returns its result."""
                    def __init__(self, fut): self.fut = fut
                    def __await__(self):
                        print("  __await__: yielding the future to the Task")
                        result = yield from self.fut.__await__()
                        print("  __await__: resumed with", repr(result))
                        return result

                async def main():
                    loop = asyncio.get_running_loop()
                    fut = loop.create_future()
                    loop.call_soon(fut.set_result, "ready")
                    print("value:", await Ticket(fut))

                asyncio.run(main())
            '''),
        ),
        question(
            "How do you call async code from sync code, and sync code from async code?",
            "medium",
            table(
                ["From", "To", "Use"],
                [
                    ["Sync (top level)", "Async", "<code>asyncio.run(main())</code> &mdash; creates a loop, runs, closes it. Once per program, not in a loop"],
                    ["Sync code in another thread", "Async on a running loop", "<code>asyncio.run_coroutine_threadsafe(coro, loop).result()</code>"],
                    ["Async", "Blocking sync function", "<code>await asyncio.to_thread(fn, *args)</code>"],
                    ["Async", "CPU-heavy sync function", "<code>await loop.run_in_executor(process_pool, fn, *args)</code>"],
                    ["Async", "Quick, non-blocking sync function", "Just call it"],
                ],
            ),
            code('''
                import asyncio, threading

                async def double(x):
                    await asyncio.sleep(0)
                    return x * 2

                async def main():
                    loop = asyncio.get_running_loop()
                    out = []

                    def sync_worker():                       # runs in a plain thread
                        fut = asyncio.run_coroutine_threadsafe(double(21), loop)
                        out.append(fut.result())

                    t = threading.Thread(target=sync_worker)
                    t.start()
                    await asyncio.to_thread(t.join)          # do not block the loop while waiting
                    print("thread got:", out[0])

                print(asyncio.run(double(5)))
                asyncio.run(main())
            '''),
            "What does not work: calling <code>asyncio.run</code> from inside a running loop (it raises <code>RuntimeError</code>), or calling <code>fut.result()</code> on the loop&rsquo;s own thread, which deadlocks.",
        ),
    ],
    refs=[
        ("Python docs: asyncio", "https://docs.python.org/3/library/asyncio.html"),
        ("PEP 492 — Coroutines with async and await syntax", "https://peps.python.org/pep-0492/"),
        ("Python docs: Developing with asyncio", "https://docs.python.org/3/library/asyncio-dev.html"),
        ("Python docs: TaskGroup", "https://docs.python.org/3/library/asyncio-task.html#task-groups"),
    ],
)
